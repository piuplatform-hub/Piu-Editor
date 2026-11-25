import argparse
from fractions import Fraction
from pathlib import Path
import sys
import wave

import av
from av.video.reformatter import VideoReformatter
import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from media import (AUDIO_PLAN, FPS, HEIGHT, PREVIEWS, PROJECT, RATE, ROOT, SAMPLES_PER_FRAME, SOUNDTRACK,
                   WIDTH, digest, measure, read_json, run, write_json)
from qa import seek_image
from render import contact_sheet, probe
from design import Scene, change
from prepare import CATALOG, INPUTS, OVERLAYS, PLAN, WORK


DEST = PREVIEWS / "v002"
FADES = {"iris": 29, "dissolve": 17, "lens": 23, "wipe_right": 25, "wipe_left": 25, "flare": 28}
SCENE_LABELS = {
    "opening": "Từ hôm nay", "memories": "Khung ảnh kỷ niệm", "portraits": "Chân dung",
    "veil": "Khăn voan", "toast": "Nâng ly", "dance": "Dáng váy", "gestures": "Khoảnh khắc bên nhau",
    "botanical": "Vòm hoa", "ceremony": "Song Hỷ", "closing": "Khép lại",
}
TRANSITIONS = {
    "iris": "Mở bằng khung tròn", "dissolve": "Tan hình", "lens": "Mờ rồi lấy nét",
    "wipe_right": "Vệt sáng ấm", "wipe_left": "Lau mép mềm", "flare": "Vệt sáng đỏ",
}


def layout_frames(plan, fps):
    starts = [round(fps * scene["start"]) for scene in plan["scenes"]]
    end = round(fps * plan["duration"])
    lengths = [last - start for start, last in zip(starts, starts[1:] + [end])]
    if starts[0] != 0 or min(lengths) < fps:
        raise ValueError("The scene plan must start at frame 0 and contain at least one second per scene")
    return starts, lengths, end


def preflight(plan):
    manifest = read_json(PROJECT / "assets.json")
    selected = {row["path"]: row["sha256"] for row in manifest["assets"] if row["selected"] and row["exists"]}
    catalog = read_json(CATALOG)
    keys = {key for scene in plan["scenes"] for key in scene["photos"]}
    paths = [INPUTS / "photos" / f"{key}.jpg" for key in sorted(keys)]
    paths += [INPUTS / "overlays" / name for name in OVERLAYS]
    for path in paths:
        actual = digest(path)
        if actual != selected.get(path.relative_to(ROOT).as_posix()):
            raise ValueError(f"Preview input differs from its manifest: {path}")
        if path.parent.name == "photos" and actual != catalog[path.stem]["sha256"]:
            raise ValueError(f"Preview input differs from the curated set: {path}")


def render_stills(plan, lengths, fps, dest):
    pictures = []
    previous = None
    for info, length in zip(plan["scenes"], lengths):
        scene = Scene(info, fps)
        main = scene.picture(length // 2, length)
        pictures.append((Image.fromarray(cv2.cvtColor(main, cv2.COLOR_BGR2RGB)),
                         f"{info['start']:05.2f}s · {SCENE_LABELS[info['layout']]}"))
        if previous is not None and info["layout"] in {"memories", "portraits", "veil", "ceremony"}:
            motion = scene.picture(12 * fps // FPS, length)
            sample = change(previous, motion, info["transition"], .5, info["layout"] == "portraits", fps > FPS)
            pictures.append((Image.fromarray(cv2.cvtColor(sample, cv2.COLOR_BGR2RGB)), TRANSITIONS[info["transition"]]))
        previous = scene.picture(length - 1, length)
    contact_sheet(pictures, dest / "layout-check.jpg")


def encode_picture(plan, lengths, path, encoder, fps):
    converter = VideoReformatter()
    through = 0
    previous = None
    with av.open(str(path), "w", options={"video_track_timescale": "25000"}) as container:
        stream = container.add_stream(encoder, rate=fps)
        stream.width, stream.height, stream.pix_fmt = WIDTH, HEIGHT, "yuv420p"
        stream.time_base = Fraction(1, 25000)
        codec = stream.codec_context
        codec.color_primaries = codec.color_trc = codec.colorspace = codec.color_range = 1
        codec.gop_size = 2 * fps
        if encoder == "h264_nvenc":
            stream.options = {"preset": "p4", "rc": "vbr", "cq": "20", "b": "0", "profile": "high", "rc-lookahead": "8"}
        else:
            codec.thread_count = 6
            stream.options = {"preset": "veryfast", "crf": "17", "profile": "high"}
        previous_scene = None
        previous_length = 0
        for config, length in zip(plan["scenes"], lengths):
            scene = Scene(config, fps)
            mode = config["transition"]
            fade = FADES[mode] * fps // FPS
            for relative in range(length):
                picture = scene.picture(relative, length)
                if previous is not None and relative < fade:
                    outgoing = previous
                    if fps > FPS and previous_scene.layout in {"opening", "veil", "botanical", "ceremony"}:
                        outgoing = previous_scene.picture(previous_length - 1 + relative, previous_length)
                    picture = change(outgoing, picture, mode, relative / fade, config["layout"] == "portraits", fps > FPS)
                rgb = av.VideoFrame.from_ndarray(picture, format="bgr24")
                frame = converter.reformat(rgb, format="yuv420p", dst_colorspace="ITU709", dst_color_range="MPEG")
                frame.pts, frame.time_base = through, Fraction(1, fps)
                for packet in stream.encode(frame):
                    container.mux(packet)
                through += 1
            previous = picture
            previous_scene, previous_length = scene, length
            print(f"{through / fps:06.2f}s · {config['layout']}", flush=True)
        for packet in stream.encode():
            container.mux(packet)


def soundtrack(plan, frames, fps, work):
    audio = read_json(AUDIO_PLAN)
    if digest(SOUNDTRACK) != audio["soundtrackSha256"]:
        raise ValueError("The prepared V001 soundtrack does not match its receipt")
    track = next(song for song in audio["tracks"] if song["title"] == plan["song"])
    length = frames * (RATE // fps)
    if length > (track["nextFrame"] - track["startFrame"]) * SAMPLES_PER_FRAME:
        raise ValueError("Preview would extend past the selected song")
    with wave.open(str(SOUNDTRACK), "rb") as source:
        source.setpos(track["startFrame"] * SAMPLES_PER_FRAME)
        if source.getnchannels() != 2 or source.getframerate() != RATE or source.getsampwidth() != 2:
            raise ValueError("Expected stereo PCM at 48 kHz")
        raw = np.frombuffer(source.readframes(length), dtype="<i2").reshape(-1, 2).copy()
    if len(raw) != length:
        raise ValueError("Soundtrack did not cover the preview")
    tail = round(1.9 * RATE)
    raw[-tail:] = (raw[-tail:] * np.linspace(1, 0, tail, dtype=np.float32)[:, None]).round().astype("<i2")
    path = work / "preview-mix.wav"
    with wave.open(str(path), "wb") as output:
        output.setparams((2, 2, RATE, 0, "NONE", "PCM"))
        output.writeframes(raw.tobytes())
    return path


def verify_and_sample(path, plan, starts, lengths, end, encoder, fps, movie, work):
    info = probe(path)
    video, audio = info["streams"]
    if ((video["codec_name"], audio["codec_name"]) != ("h264", "aac") or
            (video["width"], video["height"], video["avg_frame_rate"]) != (WIDTH, HEIGHT, f"{fps}/1") or
            int(video["nb_frames"]) != end or (int(audio["sample_rate"]), audio["channels"]) != (RATE, 2)):
        raise ValueError("Unexpected preview format")
    for stream in (video, audio, info["format"]):
        if abs(float(stream["duration"]) - end / fps) >= .003:
            raise ValueError("Preview picture and sound durations differ")
    run("ffmpeg", "-v", "error", "-xerror", "-nostdin", "-i", path, "-map", "0:v:0", "-map", "0:a:0",
        "-c:v", "rawvideo", "-c:a", "pcm_s16le", "-f", "null", "-")
    loudness, true_peak = measure(path)
    if not -24 < loudness < -14 or true_peak >= -1:
        raise ValueError(f"Preview audio is outside the expected range: {loudness} LUFS / {true_peak} dBTP")
    with av.open(str(path)) as content:
        stream = content.streams.video[0]
        tick = Fraction(1, fps) / stream.time_base
        stamps = sorted(packet.pts for packet in content.demux(stream) if packet.pts is not None)
        if tick.denominator != 1 or len(stamps) != end or any(stamp != n * tick for n, stamp in enumerate(stamps)):
            raise ValueError("Uneven video presentation timestamps")
        shots, cuts = [], []
        for config, start, length in zip(plan["scenes"], starts, lengths):
            center = start + length // 2
            main = seek_image(content, stream, center, fps)
            shots.append((main, f"{center / fps:06.2f}s · {SCENE_LABELS[config['layout']]}"))
            if config["layout"] in ("opening", "ceremony"):
                main.save(movie.parent / f"preview-{config['layout']}.jpg", quality=96)
            if start:
                fade = FADES[config["transition"]] * fps // FPS
                for mark in (start - 1, start + fade // 2, start + fade + 6 * fps // FPS):
                    cuts.append((seek_image(content, stream, mark, fps), f"{mark / fps:06.2f}s · {TRANSITIONS[config['transition']]}"))
        shots.append((seek_image(content, stream, end - 1, fps), f"{(end - 1) / fps:06.2f}s · cuối"))
        contact_sheet(shots, movie.parent / "preview-board.jpg")
        contact_sheet(cuts, movie.parent / "preview-transitions.jpg")
    write_json(work / "preview-qa.json",
               {"file": movie.relative_to(ROOT).as_posix(), "sha256": digest(path), "bytes": path.stat().st_size,
                "width": WIDTH, "height": HEIGHT, "fps": fps, "frames": end, "durationSeconds": end / fps,
                "videoTimestampGaps": 0,
                "encoder": encoder, "fullDecode": True, "photoCount": len({key for scene in plan["scenes"] for key in scene["photos"]}),
                "sceneSamples": len(shots), "transitionSamples": len(cuts), "audioLufs": loudness, "truePeakDbtp": true_peak})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["stills", "render"])
    parser.add_argument("--encoder", choices=["h264_nvenc", "libx264"], default="h264_nvenc")
    parser.add_argument("--smooth", action="store_true", help="Render the review version at 50 fps with fractional-pixel motion.")
    args = parser.parse_args()
    cv2.setNumThreads(4 if args.smooth else 2)
    fps = 2 * FPS if args.smooth else FPS
    work = WORK / "smooth" if args.smooth else WORK
    dest = DEST / "muot" if args.smooth else DEST
    movie = dest / ("tu-hom-nay-v002-muot.mp4" if args.smooth else "tu-hom-nay-v002-preview.mp4")
    dest.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    plan = read_json(PLAN)
    preflight(plan)
    starts, lengths, end = layout_frames(plan, fps)
    if args.mode == "stills":
        render_stills(plan, lengths, fps, dest)
        return
    picture = work / "preview-picture.mp4"
    pending = work / "preview.pending.mp4"
    audio = soundtrack(plan, end, fps, work)
    encode_picture(plan, lengths, picture, args.encoder, fps)
    run("ffmpeg", "-v", "error", "-nostdin", "-y", "-i", picture, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", pending)
    verify_and_sample(pending, plan, starts, lengths, end, args.encoder, fps, movie, work)
    pending.replace(movie)
    print(movie, flush=True)


if __name__ == "__main__":
    main()
