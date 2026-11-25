import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import time
import wave

import av
from av.video.reformatter import VideoReformatter
import cv2
from PIL import Image, ImageDraw, ImageFont

from prepare import (FPS, PLAN, PREVIEW, PUBLIC, RATE, ROOT, SOUNDTRACK, SPF, VIDEO, WORK,
                     digest, read_json, write_json)
from media import HEIGHT, WIDTH, run
from compose import Picture, TRANSITION_LENGTHS, change


def probe(path):
    result = run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-show_chapters", "-of", "json", path)
    return json.loads(result.stdout)


def emit(container, stream, frame, timestamp):
    frame.pts, frame.time_base = timestamp, Fraction(1, FPS)
    for packet in stream.encode(frame):
        container.mux(packet)


def write_picture(destination, scenes, assets, motion, encoder, previous_scene=None, label=""):
    cv2.setNumThreads(2)
    started = time.perf_counter()
    convert = VideoReformatter()
    frame_index = 0
    previous = None
    if previous_scene:
        previous = Picture(previous_scene, assets, motion).at(previous_scene["frames"] - 1)
    with av.open(str(destination), "w", options={"video_track_timescale": "50000"}) as container:
        stream = container.add_stream(encoder, rate=FPS)
        stream.width, stream.height, stream.pix_fmt = WIDTH, HEIGHT, "yuv420p"
        stream.time_base = Fraction(1, 50000)
        codec = stream.codec_context
        codec.color_primaries = codec.color_trc = codec.colorspace = codec.color_range = 1
        codec.gop_size = 2 * FPS
        if encoder == "h264_nvenc":
            stream.options = {"preset": "p4", "rc": "vbr", "cq": "20", "b": "0", "profile": "high", "rc-lookahead": "8"}
        else:
            codec.thread_count = 5
            stream.options = {"preset": "veryfast", "crf": "18", "profile": "high"}
        for index, scene in enumerate(scenes, 1):
            picture = Picture(scene, assets, motion)
            fade = TRANSITION_LENGTHS[scene["transition"]]
            encoded = None
            for frame in range(scene["frames"]):
                if frame <= max(picture.repeat, fade) or encoded is None:
                    output = picture.at(frame)
                    if previous is not None and frame < fade:
                        output = change(previous, output, scene, frame, motion)
                    base = av.VideoFrame.from_ndarray(output, format="bgr24")
                    encoded = convert.reformat(base, format="yuv420p", dst_colorspace="ITU709", dst_color_range="MPEG")
                emit(container, stream, encoded, frame_index)
                frame_index += 1
            previous = output
            if label and (index % 5 == 0 or index == len(scenes)):
                print(f"{label} · {index}/{len(scenes)} cảnh", flush=True)
        for packet in stream.encode():
            container.mux(packet)
    if label:
        elapsed = time.perf_counter() - started
        print(f"{label} xong · {elapsed:.1f}s · {frame_index / elapsed:.1f} fps", flush=True)


def fingerprint(plan, encoder):
    letter_cues = [scene["text"]["id"] for chapter in plan["chapters"] for scene in chapter["scenes"] if scene["text"]]
    paths = [PLAN, WORK / "motion.json", WORK / "lettering/date.png", Path(__file__), Path(__file__).with_name("compose.py"),
             Path(__file__).parents[1] / "layers.py"]
    paths += [WORK / f"lettering/{cue}.png" for cue in letter_cues]
    from compose import OVERLAYS
    paths += [OVERLAYS / overlay for overlay in ("Flower 02.png", "Flower 03.png", "leaf 04.png", "leaf 05.png",
                                                "TR_02_2.mov", "TR_03_2.mov")]
    sources = []
    for asset in plan["assets"].values():
        actual = digest(ROOT / asset["path"])
        if actual != asset["sha256"]:
            raise ValueError(f"Photo changed after preparation: {asset['path']}")
        sources.append(actual)
    content = [encoder, av.__version__, cv2.__version__, *sources, *(digest(path) for path in paths)]
    return sha256("\n".join(content).encode("utf-8")).hexdigest()


def part(chapter, preceding, assets, motion, encoder, signature):
    index = chapter["index"]
    output = WORK / f"part-{index:02d}.mp4"
    receipt = output.with_suffix(".json")
    frames = chapter["end"] - chapter["start"]
    if output.is_file() and receipt.is_file():
        if read_json(receipt) == {"signature": signature, "frames": frames, "sha256": digest(output)}:
            print(f"{index:02d}/13 {chapter['title']} · dùng bản xuất đã kiểm tra", flush=True)
            return output
    pending = output.with_suffix(".pending.mp4")
    write_picture(pending, chapter["scenes"], assets, motion, encoder, preceding, f"{index:02d}/13 {chapter['title']}")
    data, = probe(pending)["streams"]
    if (int(data["nb_frames"]) != frames or data["avg_frame_rate"] != f"{FPS}/1" or data["codec_name"] != "h264"
            or data["color_space"] != "bt709" or data["pix_fmt"] != "yuv420p" or abs(float(data["duration"]) - frames/FPS) > .002):
        raise ValueError(f"Invalid picture part: {index}")
    pending.replace(output)
    write_json(receipt, {"signature": signature, "frames": frames, "sha256": digest(output)})
    return output


def mix_picture(concat, audio, pending):
    run("ffmpeg", "-v", "error", "-nostdin", "-y", "-f", "concat", "-safe", "1", "-i", concat,
        "-i", audio, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
        "-video_track_timescale", "50000", "-movflags", "+faststart", pending)


def write_chapters(source, destination, chapters, story):
    metadata = [{"id": c["index"], "start": c["start"], "end": c["end"], "time_base": Fraction(1, FPS),
                 "metadata": {"title": c["title"] + " — " + c["chapter"]}} for c in chapters]
    with av.open(str(source)) as original, av.open(str(destination), "w",
                                                  options={"movflags": "+faststart", "video_track_timescale": "50000"}) as final:
        final.metadata["title"] = f"{story['groom']} & {story['bride']} — Từ hôm nay"
        final.set_chapters(metadata)
        streams = {item.index: final.add_stream_from_template(item) for item in original.streams}
        for packet in original.demux():
            if packet.dts is not None:
                packet.stream = streams[packet.stream.index]
                final.mux(packet)


def concatenate(plan, parts, story):
    concat = WORK / "picture-parts.txt"
    concat.write_text("".join(f"file '{path.name}'\nduration {(chapter['end'] - chapter['start']) / FPS:.6f}\n"
                              for chapter, path in zip(plan["chapters"], parts, strict=True)), encoding="utf-8")
    pending = WORK / "master-mux.mp4"
    mix_picture(concat, SOUNDTRACK, pending)
    titled = WORK / "master-chapters.mp4"
    write_chapters(pending, titled, plan["chapters"], story)
    output = probe(titled)
    video, audio = (next(stream for stream in output["streams"] if stream["codec_type"] == typ) for typ in ("video", "audio"))
    expected = plan["totalFrames"] / FPS
    if (int(video["nb_frames"]) != plan["totalFrames"] or int(audio["sample_rate"]) != RATE
            or abs(float(output["format"]["duration"]) - expected) > .003
            or len(output["chapters"]) != len(plan["chapters"])):
        raise ValueError("Final picture, chapter or audio ranges do not match the master timeline")
    if VIDEO.exists():
        raise FileExistsError(VIDEO)
    titled.rename(VIDEO)
    print(f"Saved {VIDEO}", flush=True)


def final(plan, motion, encoder, workers, story):
    if VIDEO.exists():
        raise FileExistsError(VIDEO)
    if digest(SOUNDTRACK) != plan["soundtrackSha256"]:
        raise ValueError("Soundtrack differs from the planned mix")
    signature = fingerprint(plan, encoder)
    completed = {}
    chapters = plan["chapters"]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        jobs = {}
        for index, chapter in enumerate(chapters):
            preceding = chapters[index - 1]["scenes"][-1] if index else None
            future = pool.submit(part, chapter, preceding, plan["assets"], motion, encoder, signature)
            jobs[future] = index
        for future in as_completed(jobs):
            completed[jobs[future]] = future.result()
    concatenate(plan, [completed[index] for index in range(len(chapters))], story)


def sheet(items, path, columns=3, width=407):
    height = round(width * HEIGHT / WIDTH)
    cell_w, cell_h = width + 9, height + 28
    board = Image.new("RGB", (columns * cell_w + 7, ((len(items) + columns - 1) // columns) * cell_h + 7), "#24191b")
    draw = ImageDraw.Draw(board)
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    for i, (image, caption) in enumerate(items):
        x, y = 7 + (i % columns) * cell_w, 7 + (i // columns) * cell_h
        board.paste(image.resize((width, height), Image.Resampling.LANCZOS), (x, y))
        draw.text((x + 5, y + height + 3), caption, fill="#f9eddf", font=font)
    board.save(path, quality=94)


def stills(plan, motion):
    cv2.setNumThreads(2)
    scenes = [scene for chapter in plan["chapters"] for scene in chapter["scenes"]]
    picks = [scene for scene in scenes if scene["text"]]
    examples = []
    for layout in ("duet", "triptych", "arch", "gallery", "folio", "silk"):
        examples.append(next(scene for scene in scenes if scene["layout"] == layout))
    for name, selected in (("lettering", picks), ("layouts", examples)):
        items = []
        for scene in selected:
            frame = Picture(scene, plan["assets"], motion).at(round(.47 * scene["frames"]))
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            items.append((image, f"{scene['id']:03d} · {scene['start']/FPS:.2f}s"))
            if scene["id"] in (1, 2) or (scene["text"] and scene["text"]["date"]):
                image.save(PREVIEW / f"test-{scene['id']:03d}.jpg", quality=96)
        for page, n in enumerate(range(0, len(items), 15), 1):
            sheet(items[n:n + 15], PREVIEW / f"test-{name}-{page:02d}.jpg")
    print("Prepared 28 lettering checks and 6 layout checks.", flush=True)


def sample(plan, motion, encoder):
    scenes = plan["chapters"][0]["scenes"][:3]
    frames = sum(scene["frames"] for scene in scenes)
    raw = WORK / "sample-picture.mp4"
    write_picture(raw, scenes, plan["assets"], motion, encoder, label="Bản thử phần mở")
    with wave.open(str(SOUNDTRACK), "rb") as src, wave.open(str(WORK / "sample.wav"), "wb") as target:
        target.setparams((2, 2, RATE, 0, "NONE", "PCM"))
        target.writeframes(src.readframes(frames * SPF))
    movie = PREVIEW / "tu-hom-nay-phan-mo-v005.mp4"
    run("ffmpeg", "-v", "error", "-nostdin", "-y", "-i", raw, "-i", WORK / "sample.wav", "-map", "0:v:0",
        "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", movie)
    print(f"Opening sample: {frames/FPS:.2f}s · {movie}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("stills", "sample", "final"))
    parser.add_argument("--workers", type=int, default=3, choices=(1, 2, 3))
    parser.add_argument("--encoder", default="h264_nvenc", choices=("h264_nvenc", "libx264"))
    args = parser.parse_args()
    PREVIEW.mkdir(exist_ok=True)
    plan = read_json(PLAN)
    motion = read_json(WORK / "motion.json")
    if args.mode == "stills":
        stills(plan, motion)
    elif args.mode == "sample":
        sample(plan, motion, args.encoder)
    else:
        from prepare import STORY
        final(plan, motion, args.encoder, args.workers, read_json(STORY))
