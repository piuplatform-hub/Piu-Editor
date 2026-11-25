from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
import json
import re
import wave

import av
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageStat

from media import (AUDIO_PLAN, DELIVERY, FPS, HEIGHT, PREVIEWS, RATE, SAMPLES_PER_FRAME, SOUNDTRACK, TIMELINE,
                   WIDTH, WORK, digest, measure, read_json, run, write_json)
from render import probe


def require(condition, message):
    if not condition:
        raise ValueError(message)


def video_streams(total_frames):
    info = probe(DELIVERY)
    streams = {item["codec_type"]: item for item in info["streams"]}
    require(len(info["streams"]) == 2 and set(streams) == {"video", "audio"}, "Expected one picture and one sound track")
    video, audio = streams["video"], streams["audio"]
    require((video["width"], video["height"]) == (WIDTH, HEIGHT), "Unexpected picture size")
    require(video["codec_name"] == "h264" and video["pix_fmt"] == "yuv420p" and video["color_space"] == "bt709",
            "Unexpected picture format")
    require(video["avg_frame_rate"] == f"{FPS}/1" and int(video["nb_frames"]) == total_frames, "Unexpected picture length")
    require(audio["codec_name"] == "aac" and int(audio["sample_rate"]) == RATE and audio["channels"] == 2,
            "Unexpected audio format")
    expected = total_frames / FPS
    for item in (info["format"], video, audio):
        require(abs(float(item["duration"]) - expected) <= .002, "Track duration differs from the timeline")
    return video, audio


def timestamps(stream, index):
    result = run("ffprobe", "-v", "error", "-select_streams", f"{stream}:0", "-show_entries",
                 f"packet={index}", "-of", "json", DELIVERY)
    return json.loads(result.stdout)["packets"]


def check_timestamps(total_frames, video, audio):
    video_packets = timestamps("v", "pts,dts")
    step = Fraction(1, FPS) / Fraction(video["time_base"])
    require(step.denominator == 1 and len(video_packets) == total_frames, "Unexpected video timestamp grid")
    pts = sorted(int(packet["pts"]) for packet in video_packets)
    dts = [int(packet["dts"]) for packet in video_packets]
    require(all(stamp == i * step for i, stamp in enumerate(pts)), "Gap or duplicate in video timestamps")
    require(all(second - first == step for first, second in zip(dts, dts[1:])), "Uneven video decode timestamps")
    a = [(int(packet["pts"]), int(packet["duration"])) for packet in timestamps("a", "pts,duration")]
    require(Fraction(audio["time_base"]) == Fraction(1, RATE), "Unexpected audio timestamp grid")
    require(all(first + length == second for (first, length), (second, _) in zip(a, a[1:])), "Gap in AAC packets")
    require(sum(a[-1]) == total_frames * SAMPLES_PER_FRAME, "AAC tail doesn't meet the end of picture")
    return len(a)


def decode_all():
    run("ffmpeg", "-v", "error", "-xerror", "-nostdin", "-threads", "8", "-i", DELIVERY, "-map", "0:v:0", "-map",
        "0:a:0", "-c:v", "rawvideo", "-c:a", "pcm_s16le", "-f", "null", "-")
    print("Decoded every frame of picture and sound", flush=True)
    return True


def samples(wav, offset, length):
    wav.setpos(offset)
    return np.frombuffer(wav.readframes(length), dtype="<i2").astype(np.float32)


def check_audio(audio_plan):
    decoded = WORK / "decoded-delivery.wav"
    run("ffmpeg", "-v", "error", "-nostdin", "-y", "-i", DELIVERY, "-map", "0:a:0", "-c:a", "pcm_s16le", decoded)
    loudness, true_peak = measure(decoded)
    require(-20 <= loudness <= -16 and true_peak < -1, "Encoded mix is outside the listening-level target")
    comparison = []
    with wave.open(str(SOUNDTRACK), "rb") as original, wave.open(str(decoded), "rb") as final:
        require(abs(final.getnframes() - original.getnframes()) <= 1024, "Decoded audio length differs from the mix")
        for track in audio_plan["tracks"]:
            width = track["nextFrame"] - track["startFrame"]
            offsets = [(track["startFrame"] + round(width * point)) * SAMPLES_PER_FRAME for point in (.27, .68)]
            score = min(float(np.corrcoef(samples(original, offset, 2 * RATE), samples(final, offset, 2 * RATE))[0, 1])
                        for offset in offsets)
            require(score >= .985, f"AAC samples do not match the prepared track: {track['title']}")
            comparison.append({"title": track["title"], "minSampleCorrelation": score})
        tail = samples(final, original.getnframes() - round(.18 * RATE), round(.15 * RATE))
        require(len(tail) and np.max(np.abs(tail)) < 20, "Expected quiet tail for playback")
    silence = run("ffmpeg", "-hide_banner", "-nostats", "-i", decoded, "-vn", "-af", "silencedetect=noise=-48dB:d=0.7",
                  "-c:a", "pcm_s16le", "-f", "null", "-")
    pauses = [float(value) for value in re.findall(r"silence_duration:\s*([0-9.]+)", silence.stderr)]
    print(f"Audio {loudness:.2f} LUFS · peak {true_peak:.2f} dBTP · matched all {len(comparison)} songs", flush=True)
    return {"integratedLufs": loudness, "truePeakDbtp": true_peak, "songChecks": comparison,
            "quietTail": True, "silencesOverPointSevenSecondsAtMinus48Dbfs": pauses}


def seek_image(container, stream, frame_number, fps=FPS):
    target = int(Fraction(frame_number, fps) / stream.time_base)
    container.seek(target, stream=stream, backward=True)
    for picture in container.decode(stream):
        if picture.pts == target:
            return picture.to_image()
        if picture.pts > target:
            break
    raise ValueError(f"Frame {frame_number} missing after seeking")


def board(items, path, columns=6, width=245):
    height = round(width * HEIGHT / WIDTH)
    gap = 8
    cell_w, cell_h = width + gap, height + 27
    output = Image.new("RGB", (columns * cell_w + gap, ((len(items) + columns - 1) // columns) * cell_h + gap), "#231f1b")
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    draw = ImageDraw.Draw(output)
    for index, (image, label) in enumerate(items):
        x, y = gap + index % columns * cell_w, gap + index // columns * cell_h
        output.paste(image, (x, y))
        draw.text((x, y + height + 4), label, font=font, fill="#fff6ea")
    output.save(path, quality=92)


def timecode(frame):
    seconds = frame / FPS
    return f"{int(seconds) // 60:02d}:{seconds % 60:05.2f}"


def check_pictures(plan):
    scenes = [scene for chapter in plan["chapters"] for scene in chapter["scenes"]]
    sample_size = (245, 138)
    with av.open(str(DELIVERY)) as container:
        stream = container.streams.video[0]
        stream.codec_context.thread_count = 4

        def picture(frame):
            large = seek_image(container, stream, frame)
            small = large.resize(sample_size, Image.Resampling.LANCZOS)
            require(ImageStat.Stat(small.convert("L")).stddev[0] > 9, f"Blank-looking image at frame {frame}")
            return small

        for page, begin in enumerate(range(0, len(scenes), 42), 1):
            samples = []
            for scene in scenes[begin:begin + 42]:
                center = scene["start"] + scene["frames"] // 2
                samples.append((picture(center), f"{scene['id']:03d} · {timecode(center)}"))
            board(samples, PREVIEWS / f"slideshow-final-{page}.jpg")
        cuts = []
        for scene in scenes[1:]:
            center = scene["start"] + (9 if scene["transition"] == "dissolve" else 11)
            cuts.append((picture(center), f"{scene['id']:03d} · {timecode(center)}"))
        for page, begin in enumerate(range(0, len(cuts), 42), 1):
            board(cuts[begin:begin + 42], PREVIEWS / f"slideshow-cuts-{page}.jpg")
        key_frames = [0, FPS * 3, plan["totalFrames"] - 1]
        for chapter in plan["chapters"][1:]:
            start = chapter["start"]
            key_frames.extend((start - 1, start + 10, start + FPS))
        chapter_samples = [(picture(frame), timecode(frame)) for frame in key_frames]
        board(chapter_samples, PREVIEWS / "slideshow-song-boundaries.jpg")
        for frame, label in ((FPS * 3, "opening"), (plan["totalFrames"] - 1, "closing")):
            seek_image(container, stream, frame).save(PREVIEWS / f"slideshow-{label}.jpg", quality=95)
    print(f"Sampled {len(scenes)} slides and {len(cuts)} picture transitions from the encoded MP4", flush=True)
    return {"sceneSamples": len(scenes), "transitionSamples": len(cuts), "chapterBoundarySamples": len(key_frames)}


def main():
    plan, audio_plan = read_json(TIMELINE), read_json(AUDIO_PLAN)
    count = plan["totalFrames"]
    video, audio = video_streams(count)
    packets = check_timestamps(count, video, audio)
    with ThreadPoolExecutor(max_workers=2) as pool:
        decoded = pool.submit(decode_all)
        audio_checks = pool.submit(check_audio, audio_plan)
        visual_samples = check_pictures(plan)
        complete = decoded.result()
        audio_values = audio_checks.result()
    report = {"file": DELIVERY.name, "bytes": DELIVERY.stat().st_size, "sha256": digest(DELIVERY), "fps": FPS,
              "width": WIDTH, "height": HEIGHT, "durationSeconds": count / FPS, "videoFrames": count,
              "fullDecode": complete, "audioPackets": packets, "timestampsContinuous": True,
              "audio": audio_values, **visual_samples}
    write_json(WORK / "qa-report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
