import hashlib
import io
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import wave
from array import array

from PIL import Image, ImageCms, ImageFilter, ImageOps


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
SOURCE = ROOT / "Source/inbox/wedding-opener"
ORIGINAL = Path("D:/Edit Video Cuoi")
PUBLIC = PROJECT / "public"
WORK = PROJECT / "working/v001"
CONFIG = json.loads((PROJECT / "src/timeline.json").read_text(encoding="utf-8"))
FFMPEG = PROJECT / "node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"
FONTS = ["CormorantGaramond.ttf", "CormorantGaramond-Italic.ttf", "BeVietnamPro-Medium.ttf"]
SRGB = ImageCms.createProfile("sRGB")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_photo(folder, photo):
    exact = folder / f"{photo}.jpg"
    if exact.is_file():
        return exact
    candidates = sorted(folder.glob(f"{photo}_*.jpg")) if photo.isdecimal() else []
    if len(candidates) > 1:
        raise ValueError(f"Ambiguous photo ID {photo} in {folder}")
    return candidates[0] if candidates else None


def stage(original, target):
    if target.is_file():
        if original and original.is_file() and sha256(original) != sha256(target):
            raise ValueError(f"Source differs from the local copy: {target.name}")
        return target
    if original is None or not original.is_file():
        raise FileNotFoundError(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".tmp")
    shutil.copy2(original, temp)
    if sha256(original) != sha256(temp):
        raise ValueError(f"Copy differs from the source: {target.name}")
    temp.replace(target)
    return target


def prepare_photo(source, target, wash):
    with Image.open(source) as original:
        photo = ImageOps.exif_transpose(original)
        profile = photo.info.get("icc_profile")
        if profile:
            photo = ImageCms.profileToProfile(photo, io.BytesIO(profile), SRGB, outputMode="RGB")
        else:
            photo = photo.convert("RGB")
        photo.thumbnail((2304, 2304), Image.Resampling.LANCZOS)
        target.parent.mkdir(parents=True, exist_ok=True)
        photo.save(target, format="JPEG", quality=94, subsampling=0, optimize=True)
        if wash:
            wash.parent.mkdir(exist_ok=True)
            backdrop = ImageOps.fit(photo, (144, 81), method=Image.Resampling.LANCZOS, centering=(.5, .4))
            backdrop.filter(ImageFilter.GaussianBlur(13)).save(wash, format="JPEG", quality=90)


def ffmpeg(*args):
    executable = FFMPEG if FFMPEG.is_file() else shutil.which("ffmpeg")
    if not executable:
        raise FileNotFoundError("FFmpeg binary not found. Install the project dependencies first.")
    return subprocess.run(
        [str(executable), *map(str, args)], check=True, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def prepare_audio(source):
    audio = CONFIG["audio"]
    seconds = CONFIG["shots"][-1]["endFrame"] / CONFIG["fps"]
    raw = WORK / "music-excerpt.wav"
    ffmpeg("-v", "error", "-y", "-i", source, "-map", "0:a:0", "-t", seconds,
           "-ar", 48000, "-ac", 2, "-c:a", "pcm_s16le", raw)
    analysis = ffmpeg("-hide_banner", "-nostats", "-i", raw, "-af",
                      "loudnorm=I=-15.5:TP=-1.8:LRA=11:print_format=json",
                      "-c:a", "pcm_s16le", "-f", "null", "-")
    stats = json.loads(re.search(r'\{\s*"input_i".*?\}', analysis.stderr, re.S)[0])
    gain_db = min(audio["targetLufs"] - float(stats["input_i"]),
                  audio["peakCeilingDbtp"] - float(stats["input_tp"]))
    gain = 10 ** (gain_db / 20)
    with wave.open(str(raw), "rb") as read:
        params = read.getparams()
        samples = array("h", read.readframes(params.nframes))
    expected_frames = round(seconds * params.framerate)
    if params.nframes != expected_frames or params.nchannels != 2 or params.sampwidth != 2:
        raise ValueError(f"Unexpected music excerpt format: {params}")

    fade_in = round(audio["fadeInSeconds"] * params.framerate)
    fade_out_start = round(audio["fadeOutStartSeconds"] * params.framerate)
    fade_out_end = round(audio["fadeOutEndSeconds"] * params.framerate)
    if not 0 < fade_in < fade_out_start < fade_out_end <= params.nframes:
        raise ValueError("Audio fades must fit the timeline")
    for frame in range(params.nframes):
        if frame < fade_in:
            level = gain * (0.5 - 0.5 * math.cos(math.pi * frame / fade_in))
        elif frame < fade_out_start:
            level = gain
        elif frame < fade_out_end:
            progress = (frame - fade_out_start) / (fade_out_end - fade_out_start)
            level = gain * (0.5 + 0.5 * math.cos(math.pi * progress))
        else:
            level = 0
        for channel in range(params.nchannels):
            index = frame * params.nchannels + channel
            samples[index] = max(-32768, min(32767, round(samples[index] * level)))

    with wave.open(str(PUBLIC / "soundtrack.wav"), "wb") as write:
        write.setparams(params)
        write.writeframes(samples.tobytes())
    mix = {"source": source.name, "sourceSha256": sha256(source), "seconds": seconds,
           "sourceLufs": float(stats["input_i"]), "sourcePeakDbtp": float(stats["input_tp"]),
           "gainDb": gain_db, "fadeInSeconds": audio["fadeInSeconds"],
           "fadeOutStartSeconds": audio["fadeOutStartSeconds"],
           "fadeOutEndSeconds": audio["fadeOutEndSeconds"]}
    (WORK / "audio-mix.json").write_text(json.dumps(mix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {seconds:.2f}s stereo WAV, gain {gain_db:+.2f} dB", flush=True)


def update_inventory(picks):
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/studio.py"),
                    "inventory", "--project", PROJECT.name, "--hash"], check=True)
    manifest = PROJECT / "assets.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    chosen = {path.relative_to(ROOT).as_posix(): role for path, role in picks.items()}
    for row in data["assets"]:
        role = chosen.pop(row["path"], None)
        row["selected"] = role is not None
        if role is not None:
            if not row["exists"] or row["changedSinceSelection"]:
                raise ValueError(f"Review the changed selection: {row['path']}")
            row["role"] = role
            row["notes"] = "Dùng trong phim theo timeline V001."
    if chosen:
        raise ValueError(f"Missing from inventory: {', '.join(chosen)}")
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    PUBLIC.mkdir(exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    picks = {}
    seen = set()
    previous_end = 0
    for shot in CONFIG["shots"]:
        if shot["endFrame"] <= previous_end:
            raise ValueError(f"Shot frames overlap or are empty: {shot['id']}")
        previous_end = shot["endFrame"]
        for photo in shot["photos"]:
            if photo in seen:
                raise ValueError(f"Photo is repeated: {photo}")
            seen.add(photo)
            original = find_photo(ORIGINAL / "Image", photo)
            known = find_photo(SOURCE / "images", photo)
            selected = known or (SOURCE / "images" / original.name if original else None)
            if selected is None:
                raise FileNotFoundError(f"Photo {photo}")
            selected = stage(original, selected)
            wash = PUBLIC / f"washes/{photo}.jpg" if shot["layout"] == "portrait" else None
            prepare_photo(selected, PUBLIC / f"photos/{photo}.jpg", wash)
            picks[selected] = shot["id"]

    name = CONFIG["audio"]["file"]
    original = next(ORIGINAL.glob(f"*/{name}"), None)
    selected = stage(original, SOURCE / "music" / name)
    for font in FONTS:
        installed = PROJECT / "working" / font
        target = PUBLIC / "fonts" / font
        target.parent.mkdir(exist_ok=True)
        if installed.is_file():
            shutil.copy2(installed, target)
        elif not target.is_file():
            raise FileNotFoundError(f"Local font is required: {installed}")
    prepare_audio(selected)
    picks[selected] = "Nhạc mở màn"
    update_inventory(picks)
    print(f"Prepared {len(seen)} photos and {len(FONTS)} font files", flush=True)


if __name__ == "__main__":
    main()
