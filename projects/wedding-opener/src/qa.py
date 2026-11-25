import json
import math
from pathlib import Path
import re
from statistics import correlation
import subprocess
import sys
import wave
from array import array

from PIL import Image, ImageDraw, ImageFont


PROJECT = Path(__file__).resolve().parents[1]
WORK = PROJECT / "working/v001"
PREVIEWS = PROJECT / "previews/v001"
CONFIG = json.loads((PROJECT / "src/timeline.json").read_text(encoding="utf-8"))
VIDEO = PROJECT.parents[1] / "output/wedding-opener/tu-hom-nay-v001.mp4"
BIN = PROJECT / "node_modules/@remotion/compositor-win32-x64-msvc"
FPS = CONFIG["fps"]
FRAMES = CONFIG["shots"][-1]["endFrame"]


def run(program, *args):
    return subprocess.run([str(BIN / program), *map(str, args)], check=True, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def caption(frame):
    shot = next(shot for shot in CONFIG["shots"] if frame < shot["endFrame"])
    return f"{frame / FPS:06.2f}s  ·  {shot['id']}"


def contact_sheet(paths, output):
    width, height, columns = 345, 194, 4
    cell_width, cell_height = width + 16, height + 34
    sheet = Image.new("RGB", (columns * cell_width + 16, math.ceil(len(paths) / columns) * cell_height + 14), "#151311")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    for index, path in enumerate(paths):
        with Image.open(path) as image:
            tile = image.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
        x, y = 16 + index % columns * cell_width, 12 + index // columns * cell_height
        sheet.paste(tile, (x, y))
        label = caption(int(path.stem.rsplit("-", 1)[1]))
        draw.text((x, y + height + 6), label, font=font, fill="#f2eade")
    sheet.save(output, quality=92)


def probe_picture():
    data = json.loads(run("ffprobe.exe", "-v", "error", "-show_format", "-show_streams", "-of", "json", VIDEO).stdout)
    require(len(data["streams"]) == 2, "Expected exactly video and audio tracks")
    video, audio = data["streams"]
    require((video["width"], video["height"]) == (CONFIG["width"], CONFIG["height"]), "Unexpected video size")
    require(video["codec_name"] == "h264" and video["pix_fmt"] == "yuv420p" and video["color_space"] == "bt709",
            "Unexpected picture codec, pixel format or color space")
    require(video["avg_frame_rate"] == f"{FPS}/1" and int(video["nb_frames"]) == FRAMES, "Unexpected frame rate/count")
    require(audio["codec_name"] == "aac" and (int(audio["sample_rate"]), audio["channels"]) == (48000, 2), "Unexpected audio format")
    require(abs(float(data["format"]["duration"]) - FRAMES / FPS) < 1 / FPS, "Unexpected container duration")
    require(abs(float(audio["duration"]) - FRAMES / FPS) < 1 / FPS, "Picture and audio durations differ")
    packets = run("ffprobe.exe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time",
                  "-of", "json", VIDEO)
    pts = sorted(float(packet["pts_time"]) for packet in json.loads(packets.stdout)["packets"])
    require(len(pts) == FRAMES and all(abs(stamp - frame / FPS) < .00004 for frame, stamp in enumerate(pts)),
            "Picture timestamps are uneven")
    head = VIDEO.open("rb")
    with head:
        header = head.read(128 * 1024)
    require(0 < header.find(b"moov") < header.find(b"mdat"), "MP4 metadata is not at the start")
    run("ffmpeg.exe", "-v", "error", "-xerror", "-i", VIDEO, "-map", "0:v:0", "-map", "0:a:0",
        "-c:v", "rawvideo", "-c:a", "pcm_s16le", "-f", "null", "-")
    return data


def wav_window(path, start, duration):
    with wave.open(str(path), "rb") as source:
        source.setpos(round(start * source.getframerate()))
        return array("h", source.readframes(round(duration * source.getframerate())))


def probe_audio():
    decoded = WORK / "decoded-delivery.wav"
    run("ffmpeg.exe", "-v", "error", "-y", "-i", VIDEO, "-map", "0:a:0", "-c:a", "pcm_s16le", decoded)
    result = run("ffmpeg.exe", "-hide_banner", "-nostats", "-i", decoded, "-af", "loudnorm=print_format=json",
                 "-c:a", "pcm_s16le", "-f", "null", "-")
    measured = json.loads(re.search(r'\{\s*"input_i".*?\}', result.stderr, re.S)[0])
    loudness, peak = float(measured["input_i"]), float(measured["input_tp"])
    require(-19 <= loudness <= -13 and peak <= -1.0, "Audio level is outside the target range")
    master = PROJECT / "public/soundtrack.wav"
    matches = {str(start): correlation(wav_window(master, start, 1), wav_window(decoded, start, 1))
               for start in (3, 28, 52, 84.35)}
    require(min(matches.values()) >= .985, "Encoded audio differs from the soundtrack")
    end = wav_window(decoded, CONFIG["audio"]["fadeOutEndSeconds"] + .1, .15)
    require(bool(end) and max(abs(sample) for sample in end) < 16, "Audio remains audible at the exit cue")
    return {"integratedLufs": loudness, "maxTruePeakDbtp": peak, "mixCorrelation": matches, "quietTail": True}


def extract_delivery_frames():
    final = PREVIEWS / "encoded"
    final.mkdir(exist_ok=True)
    start = 0
    frames = {24, 73, FRAMES - 2}
    for shot in CONFIG["shots"]:
        frames.add((start + shot["endFrame"]) // 2)
        if shot["id"] in ("song-hy", "thanks"):
            for after in (-2, 0, 5, 13, 28, 52):
                frames.add(start + after)
        start = shot["endFrame"]
    paths = []
    for frame in sorted(frames):
        path = final / f"frame-{frame:04d}.jpg"
        stamp = f"{(frame + .05) / FPS:.6f}" if frame == 0 else f"{frame / FPS - .00001:.6f}"
        run("ffmpeg.exe", "-v", "error", "-y", "-ss", stamp, "-i", VIDEO, "-frames:v", "1", "-an", "-c:v", "mjpeg",
            "-pix_fmt", "yuvj420p", "-update", "1", path)
        paths.append(path)
    return paths


def main():
    if sys.argv[1:] == ["stills"]:
        paths = sorted(PREVIEWS.glob("frame-*.png"))
        require(bool(paths), "Run npm run stills first")
        contact_sheet(paths, PREVIEWS / "still-contact.jpg")
        print(f"Contact sheet contains {len(paths)} preflight frames")
        return

    streams = probe_picture()
    audio = probe_audio()
    pictures = extract_delivery_frames()
    contact_sheet(pictures, PREVIEWS / "encoded-contact.jpg")
    report = {"file": str(VIDEO), "fullDecode": True, "pictureFrameCount": FRAMES, "fps": FPS,
              "duration": float(streams["format"]["duration"]), "audio": audio, "frameSamples": len(pictures)}
    (WORK / "qa-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
