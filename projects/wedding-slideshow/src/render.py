import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import time

import av
from av.video.reformatter import VideoReformatter
import cv2
from PIL import Image, ImageDraw, ImageFont

from media import (AUDIO_PLAN, DELIVERY, FPS, HEIGHT, OUTPUT, PREVIEWS, PROJECT, ROOT, SOUNDTRACK,
                   TIMELINE, WIDTH, WORK, digest, read_json, run, write_json)
from picture import TITLE_FONT, camera_length, compose, moving_picture, transition_picture


def encode_video(destination, scenes, assets, encoder, previous=None, label=""):
    cv2.setNumThreads(2)
    started = time.perf_counter()
    reformatter = VideoReformatter()
    total = sum(scene["frames"] for scene in scenes)
    checkpoint = max(1, total // 4)
    frame_number = 0
    with av.open(str(destination), "w", options={"video_track_timescale": "25000"}) as container:
        stream = container.add_stream(encoder, rate=FPS)
        stream.width, stream.height = WIDTH, HEIGHT
        stream.pix_fmt = "yuv420p"
        stream.time_base = Fraction(1, 25000)
        codec = stream.codec_context
        codec.color_primaries = codec.color_trc = codec.colorspace = 1
        codec.color_range = 1
        codec.gop_size = 2 * FPS
        if encoder == "h264_nvenc":
            stream.options = {"preset": "p4", "rc": "vbr", "cq": "21", "b": "0", "profile": "high",
                              "rc-lookahead": "8"}
        else:
            codec.thread_count = 4
            stream.options = {"preset": "veryfast", "crf": "18", "profile": "high"}
        for scene in scenes:
            canvas = compose(scene, assets)
            advance = camera_length(scene)
            blend = 19 if scene["transition"] == "dissolve" else 23
            held = None
            for relative in range(scene["frames"]):
                if held is None:
                    picture = moving_picture(canvas, scene, relative)
                    if relative < blend and previous is not None:
                        picture = transition_picture(previous, picture, scene["transition"], relative / blend)
                    bgr = av.VideoFrame.from_ndarray(picture, format="bgr24")
                    yuv = reformatter.reformat(bgr, format="yuv420p", dst_colorspace="ITU709", dst_color_range="MPEG")
                    if relative >= max(advance, blend):
                        held = yuv
                else:
                    yuv = held
                yuv.pts, yuv.time_base = frame_number, Fraction(1, FPS)
                for packet in stream.encode(yuv):
                    container.mux(packet)
                frame_number += 1
                if label and (frame_number % checkpoint == 0 or frame_number == total):
                    print(f"{label} {frame_number}/{total} khung", flush=True)
            previous = moving_picture(canvas, scene, scene["frames"] - 1)
        for packet in stream.encode():
            container.mux(packet)
    elapsed = time.perf_counter() - started
    if label:
        print(f"{label} xong · {elapsed:.1f}s · {frame_number / elapsed:.1f} fps", flush=True)


def probe(path):
    result = run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path)
    return json.loads(result.stdout)


def render_part(index, chapter, preceding, assets, encoder, signature):
    chunk = WORK / f"track-{index:02d}.mp4"
    receipt = chunk.with_suffix(".json")
    count = chapter["end"] - chapter["start"]
    if receipt.is_file() and chunk.is_file():
        record = read_json(receipt)
        if record == {"signature": signature, "frames": count, "sha256": digest(chunk)}:
            print(f"{index:02d}/10 dùng lại đoạn đã xuất", flush=True)
            return chunk
    pending = chunk.with_suffix(".pending.mp4")
    previous = None
    if preceding:
        previous = moving_picture(compose(preceding, assets), preceding, preceding["frames"] - 1)
    encode_video(pending, chapter["scenes"], assets, encoder, previous, f"{index:02d}/10 {chapter['title']}")
    picture, = probe(pending)["streams"]
    if (int(picture["nb_frames"]) != count or picture["avg_frame_rate"] != f"{FPS}/1"
            or picture["codec_name"] != "h264" or picture["pix_fmt"] != "yuv420p"):
        raise ValueError(f"Invalid video part {index}")
    pending.replace(chunk)
    write_json(receipt, {"signature": signature, "frames": count, "sha256": digest(chunk)})
    return chunk


def render_signature(plan, encoder):
    selected = {row["path"]: row["sha256"] for row in read_json(PROJECT / "assets.json")["assets"] if row["selected"]}
    paths = [asset["path"] for asset in plan["photos"].values()]
    content = [digest(TIMELINE), encoder, av.__version__, cv2.__version__,
               digest(Path(__file__)), digest(Path(__file__).with_name("picture.py"))]
    font = TITLE_FONT if TITLE_FONT.is_file() else Path("C:/Windows/Fonts/georgiai.ttf")
    content.append(digest(font))
    for path in paths:
        actual = digest(ROOT / path)
        if actual != selected.get(path):
            raise ValueError(f"Selected photo changed after staging: {path}")
        content.append(actual)
    return sha256("\n".join(content).encode("utf-8")).hexdigest()


def attach_soundtrack(plan, audio, parts):
    if audio["totalFrames"] != plan["totalFrames"] or digest(SOUNDTRACK) != audio["soundtrackSha256"]:
        raise ValueError("The soundtrack changed after the picture timeline was prepared")
    concat = WORK / "picture-parts.txt"
    concat.write_text("".join(f"file '{path.name}'\nduration {(chapter['end'] - chapter['start']) / FPS:.6f}\n"
                              for chapter, path in zip(plan["chapters"], parts)), encoding="utf-8")
    pending = WORK / "assembled.mp4"
    run("ffmpeg", "-v", "error", "-nostdin", "-y", "-f", "concat", "-safe", "1", "-i", concat, "-i", SOUNDTRACK,
        "-map", "0:v:0", "-map", "1:a:0", "-map_metadata", "-1", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
        "-video_track_timescale", "25000", "-movflags", "+faststart",
        "-metadata", "title=Từ hôm nay — Slideshow tiệc cưới", pending)
    info = probe(pending)
    streams = {stream["codec_type"]: stream for stream in info["streams"]}
    if (int(streams["video"]["nb_frames"]) != plan["totalFrames"] or streams["audio"]["codec_name"] != "aac"
            or abs(float(info["format"]["duration"]) - plan["totalFrames"] / FPS) > .002):
        raise ValueError("The assembled MP4 differs from the picture and audio timelines")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if DELIVERY.exists():
        raise FileExistsError(DELIVERY)
    pending.rename(DELIVERY)
    print(f"Đã xuất {DELIVERY}", flush=True)


def render_final(plan, encoder, workers):
    if DELIVERY.exists():
        raise FileExistsError(DELIVERY)
    WORK.mkdir(parents=True, exist_ok=True)
    signature = render_signature(plan, encoder)
    parts = {}
    chapters = plan["chapters"]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        jobs = {}
        for index, chapter in enumerate(chapters):
            preceding = chapters[index - 1]["scenes"][-1] if index else None
            future = pool.submit(render_part, index + 1, chapter, preceding, plan["photos"], encoder, signature)
            jobs[future] = index
        for future in as_completed(jobs):
            parts[jobs[future]] = future.result()
    attach_soundtrack(plan, read_json(AUDIO_PLAN), [parts[index] for index in range(len(chapters))])


def contact_sheet(samples, output):
    columns, cell_w, cell_h = 3, 402, 248
    sheet = Image.new("RGB", (columns * cell_w, ((len(samples) + columns - 1) // columns) * cell_h), "#211c1a")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 17)
    for index, (rgb, label) in enumerate(samples):
        x, y = index % columns * cell_w + 6, index // columns * cell_h + 4
        cell = rgb.resize((390, 219), Image.Resampling.LANCZOS)
        sheet.paste(cell, (x, y))
        draw.text((x, y + 221), label, font=font, fill="#fff4e9")
    sheet.save(output, quality=94)


def preview(plan, encoder):
    cv2.setNumThreads(2)
    PREVIEWS.mkdir(exist_ok=True)
    for page, chapters in enumerate((plan["chapters"][:5], plan["chapters"][5:]), 1):
        samples = []
        for chapter in chapters:
            scenes = chapter["scenes"]
            for scene in (scenes[0], scenes[len(scenes) // 2], scenes[-1]):
                frame = moving_picture(compose(scene, plan["photos"]), scene, camera_length(scene))
                rgb = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                samples.append((rgb, f"{scene['id']:03d} · {chapter['title']}"))
        contact_sheet(samples, PREVIEWS / f"slideshow-design-{page}.jpg")
    first = plan["chapters"][0]["scenes"]
    red = plan["chapters"][3]["scenes"]
    selected = [first[0], first[1], red[0], red[len(red) // 2], plan["chapters"][-1]["scenes"][-1]]
    shortened = [{**scene, "frames": 3 * FPS} for scene in selected]
    encode_video(PREVIEWS / "slideshow-motion-preview.mp4", shortened, plan["photos"], encoder)
    print("Rendered 30 design samples and a 15-second motion preview", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["preview", "final"])
    parser.add_argument("--encoder", choices=["h264_nvenc", "libx264"], default="h264_nvenc")
    parser.add_argument("--workers", type=int, choices=(1, 2), default=2)
    args = parser.parse_args()
    plan = read_json(TIMELINE)
    if plan["fps"] != FPS:
        raise ValueError("Picture timeline FPS differs from the renderer")
    if args.mode == "preview":
        preview(plan, args.encoder)
    else:
        render_final(plan, args.encoder, args.workers)


if __name__ == "__main__":
    main()
