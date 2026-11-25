from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
import json
from pathlib import Path
import re
import wave

import av
import numpy as np
from PIL import Image, ImageStat

from prepare import FPS, PLAN, PREVIEW, RATE, ROOT, SOUNDTRACK, SPF, VIDEO, WORK, digest, read_json, write_json
from media import HEIGHT, WIDTH, measure, run
from export import probe, sheet


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inspect_streams(video, plan):
    data = probe(video)
    streams = {s["codec_type"]: s for s in data["streams"]}
    picture, sound = (streams[key] for key in ("video", "audio"))
    expected = plan["totalFrames"] / FPS
    require((picture["width"], picture["height"], picture["avg_frame_rate"]) == (WIDTH, HEIGHT, f"{FPS}/1"),
            "Resolution or frame rate differs from the timeline")
    require((picture["codec_name"], picture["pix_fmt"], picture["color_space"]) == ("h264", "yuv420p", "bt709"),
            "Unexpected picture format")
    require(sound["codec_name"] == "aac" and int(sound["sample_rate"]) == RATE and sound["channels"] == 2,
            "Unexpected sound format")
    require(int(picture["nb_frames"]) == plan["totalFrames"], "Incorrect picture frame count")
    for stream in (picture, sound, data["format"]):
        require(abs(float(stream["duration"]) - expected) <= .002, "Video and audio lengths differ")
    require(len(data["chapters"]) == len(plan["chapters"]), "Incorrect MP4 chapter count")
    for actual, chapter in zip(data["chapters"], plan["chapters"], strict=True):
        require(abs(float(actual["start_time"]) - chapter["start"] / FPS) <= .001 and
                abs(float(actual["end_time"]) - chapter["end"] / FPS) <= .001 and
                actual["tags"]["title"] == chapter["title"] + " — " + chapter["chapter"], "Chapter metadata changed")
    with av.open(str(video)) as movie:
        v, a = movie.streams.video[0], movie.streams.audio[0]
        step = Fraction(1, FPS) / v.time_base
        video_pts, video_dts, audio_pts = [], [], []
        for packet in movie.demux(v, a):
            if packet.pts is None:
                continue
            if packet.stream.index == v.index:
                video_pts.append(packet.pts)
                video_dts.append(packet.dts)
            else:
                audio_pts.append((packet.pts, packet.duration))
        require(step.denominator == 1 and len(video_pts) == plan["totalFrames"], "Wrong timestamp grid")
        require(all(value == index * step for index, value in enumerate(sorted(video_pts))), "Gap or duplicate in PTS")
        require(all(after - before == step for before, after in zip(video_dts, video_dts[1:])), "Gap in DTS")
        require(a.time_base == Fraction(1, RATE), "Wrong audio clock")
        require(all(start + duration == end for (start, duration), (end, _) in zip(audio_pts, audio_pts[1:])),
                "Gap in AAC stream")
        require(sum(audio_pts[-1]) == plan["totalFrames"] * SPF, "AAC end does not align with picture")
    return len(audio_pts)


def decode(video):
    run("ffmpeg", "-v", "error", "-xerror", "-nostdin", "-threads", "7", "-i", video, "-map", "0:v:0", "-map", "0:a:0",
        "-c:v", "rawvideo", "-c:a", "pcm_s16le", "-f", "null", "-")
    print("Decoded the complete picture and sound.", flush=True)
    return True


def chunk(wav, frame, seconds=1):
    wav.setpos(frame * SPF)
    return np.frombuffer(wav.readframes(round(seconds * RATE)), dtype="<i2").astype(np.float32)


def check_audio(video, plan):
    require(digest(SOUNDTRACK) == plan["soundtrackSha256"], "Soundtrack hash changed")
    decoded = WORK / "decoded-delivery.wav"
    run("ffmpeg", "-v", "error", "-nostdin", "-y", "-i", video, "-map", "0:a:0", "-c:a", "pcm_s16le", decoded)
    levels = measure(decoded)
    require(-21 < levels[0] < -16 and levels[1] < -1.0, f"Unexpected output levels: {levels}")
    scores = []
    with wave.open(str(SOUNDTRACK), "rb") as master, wave.open(str(decoded), "rb") as final:
        require(abs(final.getnframes() - master.getnframes()) <= 1024, "Decoded music duration differs from WAV")
        for track in plan["chapters"]:
            positions = [track["start"] + round((track["end"] - track["start"]) * point) for point in (.15, .46, .79)]
            sampled = [float(np.corrcoef(chunk(master, frame), chunk(final, frame))[0, 1]) for frame in positions]
            score = min(sampled)
            require(score > .985, f"Track does not match the WAV: {track['title']}")
            scores.append({"song": track["title"], "minCorrelation": score})
        tail = chunk(final, plan["totalFrames"] - 10, .14)
        require(len(tail) and np.max(np.abs(tail)) < 20, "Expected a quiet ending")
    readout = run("ffmpeg", "-hide_banner", "-nostats", "-i", decoded, "-af", "silencedetect=noise=-48dB:d=0.7",
                  "-c:a", "pcm_s16le", "-f", "null", "-")
    pauses = [(float(start), float(end), float(dur)) for start, end, dur in re.findall(
        r"silence_start:\s*([\d.]+)[^\n]*\n[^\n]*silence_end:\s*([\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)", readout.stderr)]
    print(f"Checked all {len(scores)} songs in AAC · {levels[0]} LUFS · {levels[1]} dBTP.", flush=True)
    return {"lufs": levels[0], "truePeakDbtp": levels[1], "songs": scores, "quietTail": True, "silences": pauses}


def seek(container, stream, frame):
    target = int(Fraction(frame, FPS) / stream.time_base)
    container.seek(target, stream=stream, backward=True)
    for picture in container.decode(stream):
        if picture.pts == target:
            return picture.to_image()
        if picture.pts > target:
            break
    raise ValueError(f"Couldn't decode frame {frame}")


def stamp(frame):
    seconds = frame / FPS
    return f"{int(seconds) // 60:02d}:{seconds % 60:05.2f}"


def check_pictures(video, plan):
    scenes = [s for c in plan["chapters"] for s in c["scenes"]]
    with av.open(str(video)) as movie:
        stream = movie.streams.video[0]
        stream.codec_context.thread_count = 4

        def small(frame):
            picture = seek(movie, stream, frame).resize((286, 161), Image.Resampling.LANCZOS)
            require(ImageStat.Stat(picture.convert("L")).stddev[0] > 7, f"Blank-looking frame {frame}")
            return picture

        for page, start in enumerate(range(0, len(scenes), 48), 1):
            items = []
            for scene in scenes[start:start + 48]:
                center = scene["start"] + scene["frames"] // 2
                items.append((small(center), f"{scene['id']:03d}   {stamp(center)}"))
                if scene["id"] in (1, 2) or (scene["text"] and scene["text"]["date"]):
                    seek(movie, stream, center).save(PREVIEW / f"encoded-{scene['id']:03d}.jpg", quality=96)
            sheet(items, PREVIEW / f"encoded-scenes-{page:02d}.jpg", 6, 286)
        texts = []
        phases = []
        for scene in scenes:
            cue = scene["text"]
            if not cue:
                continue
            center = scene["start"] + scene["frames"] // 2
            texts.append((small(center), f"{scene['id']:03d}   {stamp(center)}"))
            if scene["id"] in (1, 2, 21, 59, 138, 221, 255, 261):
                for frame in (scene["start"] + cue["in"] + 18, center,
                              scene["start"] + (scene["frames"] - 1 if cue["hold"] else cue["out"] + 29)):
                    phases.append((small(frame), f"{scene['id']:03d}   {stamp(frame)}"))
        for page, begin in enumerate(range(0, len(texts), 15), 1):
            sheet(texts[begin:begin + 15], PREVIEW / f"encoded-text-{page:02d}.jpg", 3, 407)
        sheet(phases, PREVIEW / "encoded-text-motion.jpg", 3, 407)
        cuts = []
        for chapter in plan["chapters"][1:]:
            for frame in (chapter["start"] - 1, chapter["start"] + 23, chapter["start"] + 60):
                cuts.append((small(frame), f"{chapter['index']:02d}   {stamp(frame)}"))
        sheet(cuts, PREVIEW / "encoded-chapter-cuts.jpg", 3, 407)
        last = seek(movie, stream, plan["totalFrames"] - 1)
        last.save(PREVIEW / "encoded-last-frame.jpg", quality=96)
    print(f"Extracted {len(scenes)} scene checks, {len(texts)} text cues and {len(cuts)} chapter join frames.", flush=True)
    return {"sceneSamples": len(scenes), "textSamples": len(texts), "textMotionSamples": len(phases),
            "chapterCutSamples": len(cuts)}


def main():
    plan = read_json(PLAN)
    packets = inspect_streams(VIDEO, plan)
    with ThreadPoolExecutor(max_workers=2) as pool:
        pictures = pool.submit(check_pictures, VIDEO, plan)
        decode_result = pool.submit(decode, VIDEO)
        sound = check_audio(VIDEO, plan)
        visual = pictures.result()
        decoded = decode_result.result()
    report = {"movie": VIDEO.relative_to(ROOT).as_posix(), "bytes": VIDEO.stat().st_size, "sha256": digest(VIDEO),
              "durationSeconds": plan["totalFrames"] / FPS, "width": WIDTH, "height": HEIGHT,
              "fps": FPS, "videoFrames": plan["totalFrames"], "tracks": len(plan["chapters"]),
              "audioPackets": packets, "fullDecode": decoded, "timestampsContinuous": True, "audio": sound, **visual}
    write_json(WORK / "qa-report.json", report)
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
