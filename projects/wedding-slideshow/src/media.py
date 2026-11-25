import argparse
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import wave

import numpy as np


SRC = Path(__file__).resolve().parent
PROJECT = SRC.parent
ROOT = PROJECT.parents[1]
SOURCE = ROOT / "Source/inbox/wedding-slideshow"
WORK = PROJECT / "working/v001"
PREVIEWS = PROJECT / "previews"
OUTPUT = ROOT / "output/wedding-slideshow"
DELIVERY = OUTPUT / "tu-hom-nay-slideshow-v001.mp4"
BINDINGS = ROOT / "projects/wedding-opener/node_modules/@remotion/compositor-win32-x64-msvc"
WIDTH, HEIGHT, FPS, RATE = 1920, 1080, 25, 48000
SAMPLES_PER_FRAME = RATE // FPS
CROSSFADE_FRAMES = 28
EDGE_THRESHOLD_DBFS = -49
SOUNDTRACK = WORK / "soundtrack.wav"
AUDIO_PLAN = WORK / "audio-plan.json"
TIMELINE = SRC / "timeline.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    pending = path.with_suffix(path.suffix + ".pending")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(path)


def digest(path):
    sha = sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def binary(program):
    override = os.environ.get("PIU_WEDDING_FFMPEG_DIR")
    directory = Path(override) if override else BINDINGS
    executable = directory / f"{program}.exe"
    if executable.is_file():
        return str(executable)
    found = shutil.which(program)
    if found:
        return found
    raise FileNotFoundError(executable)


def run(program, *args):
    process = subprocess.run([binary(program), *map(str, args)], capture_output=True, encoding="utf-8", errors="replace",
                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    if process.returncode:
        raise RuntimeError(f"{program} exited {process.returncode}\n{process.stderr.strip()}")
    return process


def staged_copy(source, target):
    if not source.is_file() or source.is_symlink():
        raise FileNotFoundError(source)
    original_hash = digest(source)
    if target.is_file():
        if digest(target) != original_hash:
            raise ValueError(f"Local copy differs from original: {target}")
        return original_hash
    target.parent.mkdir(parents=True, exist_ok=True)
    pending = target.with_suffix(target.suffix + ".pending")
    shutil.copy2(source, pending)
    if digest(pending) != original_hash:
        raise ValueError(f"Copy failed checksum verification: {source}")
    pending.replace(target)
    return original_hash


def measure(path):
    result = run("ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "loudnorm=I=-18:TP=-3:LRA=11:print_format=json",
                 "-c:a", "pcm_s16le", "-f", "null", "-")
    block = re.search(r'\{\s*"input_i"[^}]*\}', result.stderr)
    if not block:
        raise ValueError(f"No loudness measurement for {path}")
    data = json.loads(block[0])
    return float(data["input_i"]), float(data["input_tp"])


def normalized_track(path, work=WORK):
    decoded = work / "decoded-track.wav"
    run("ffmpeg", "-v", "error", "-nostdin", "-y", "-i", path, "-map", "0:a:0", "-ar", RATE, "-ac", "2", "-c:a",
        "pcm_s16le", decoded)
    loudness, peak = measure(decoded)
    if not math.isfinite(loudness) or not math.isfinite(peak):
        raise ValueError(f"Music file is silent: {path}")
    gain = min(-18.0 - loudness, -4.0 - peak)
    with wave.open(str(decoded), "rb") as wav:
        pcm = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").reshape(-1, 2).astype(np.float32)
    frames = round(len(pcm) / SAMPLES_PER_FRAME)
    length = frames * SAMPLES_PER_FRAME
    if len(pcm) < length:
        pcm = np.pad(pcm, ((0, length - len(pcm)), (0, 0)))
    pcm = pcm[:length] * (10 ** (gain / 20))
    peak_per_frame = np.max(np.abs(pcm).reshape(frames, SAMPLES_PER_FRAME, 2), axis=(1, 2))
    threshold = 32768 * (10 ** (EDGE_THRESHOLD_DBFS / 20))
    sounding = np.flatnonzero(peak_per_frame >= threshold)
    if not len(sounding):
        raise ValueError(f"No audible samples in {path}")
    keep = round(FPS * .24)
    trim_in = max(0, int(sounding[0]) - keep)
    trim_out = max(0, frames - int(sounding[-1]) - 1 - keep)
    first, last = trim_in * SAMPLES_PER_FRAME, (frames - trim_out) * SAMPLES_PER_FRAME
    return pcm[first:last], frames, trim_in, trim_out, loudness, peak, gain


def write_pcm(wav, pcm):
    np.clip(pcm, -32768, 32767, out=pcm)
    wav.writeframesraw(np.rint(pcm).astype("<i2").tobytes())


def prepare_audio(original_root):
    WORK.mkdir(parents=True, exist_ok=True)
    tracks = read_json(SRC / "tracks.json")
    music = original_root / "nhạc cưới"
    paths = [SOURCE / "music" / track["file"] for track in tracks]
    hashes = [staged_copy(music / track["file"], path) for track, path in zip(tracks, paths)]
    staged_copy(music / "list nhạc và thứ tự.jpg", SOURCE / "playlist/list nhạc và thứ tự.jpg")
    overlap = CROSSFADE_FRAMES * SAMPLES_PER_FRAME
    phase = np.linspace(0, np.pi / 2, overlap, dtype=np.float32)[:, None]
    fade_out, fade_in = np.cos(phase), np.sin(phase)
    frames_written = 0
    last_tail = None
    timeline = []
    pending = WORK / "soundtrack.pending.wav"
    with wave.open(str(pending), "wb") as wav:
        wav.setparams((2, 2, RATE, 0, "NONE", "PCM"))
        for index, (track, path, source_hash) in enumerate(zip(tracks, paths, hashes)):
            pcm, source_frames, trim_in, trim_out, loudness, peak, gain = normalized_track(path)
            frames = source_frames - trim_in - trim_out
            if frames <= 2 * CROSSFADE_FRAMES:
                raise ValueError(f"Music file is too short to join: {path}")
            start = frames_written
            if last_tail is None:
                intro = round(.35 * RATE)
                pcm[:intro] *= np.linspace(0, 1, intro, dtype=np.float32)[:, None]
                first = 0
            else:
                write_pcm(wav, last_tail * fade_out + pcm[:overlap] * fade_in)
                first = overlap
                frames_written += CROSSFADE_FRAMES
            stop = len(pcm)
            if index + 1 < len(tracks):
                last_tail = pcm[-overlap:].copy()
                stop -= overlap
            else:
                ramp = round(1.85 * RATE)
                quiet = round(.28 * RATE)
                pcm[-ramp:-quiet] *= np.linspace(1, 0, ramp - quiet, dtype=np.float32)[:, None]
                pcm[-quiet:] = 0
            write_pcm(wav, pcm[first:stop])
            frames_written += (stop - first) // SAMPLES_PER_FRAME
            timeline.append({**track, "startFrame": start, "sourceFrames": source_frames, "nextFrame": frames_written,
                             "silenceTrimInFrames": trim_in, "silenceTrimOutFrames": trim_out,
                             "sourceSha256": source_hash, "sourceLufs": loudness, "sourcePeakDbtp": peak,
                             "gainDb": round(gain, 3)})
            trimmed = (trim_in + trim_out) / FPS
            print(f"{index + 1:02d}/{len(tracks)} {track['title']} · {frames / FPS:.2f}s · {gain:+.2f} dB · rút biên im {trimmed:.2f}s",
                  flush=True)
    with wave.open(str(pending), "rb") as wav:
        if wav.getnframes() != frames_written * SAMPLES_PER_FRAME:
            raise ValueError("Soundtrack sample count differs from the music timeline")
    pending.replace(SOUNDTRACK)
    write_json(AUDIO_PLAN, {"fps": FPS, "sampleRate": RATE, "crossfadeFrames": CROSSFADE_FRAMES,
                            "edgeThresholdDbfs": EDGE_THRESHOLD_DBFS,
                            "totalFrames": frames_written, "soundtrackSha256": digest(SOUNDTRACK), "tracks": timeline})
    print(f"Mixed {len(tracks)} tracks, {frames_written / FPS:.2f} seconds", flush=True)


def stage_photos(original_root):
    arrangement = read_json(TIMELINE)
    roles = {}
    for key, asset in arrangement["photos"].items():
        source = original_root / asset["original"]
        if not source.resolve().is_relative_to(original_root):
            raise ValueError(f"Source path escapes the chosen folder: {key}")
        target = ROOT / asset["path"]
        if not target.resolve().is_relative_to(SOURCE.resolve()):
            raise ValueError(f"Photo path escapes the project source: {key}")
        staged_copy(source, target)
        roles[target.relative_to(ROOT).as_posix()] = "Ảnh trên timeline"
    for track in read_json(SRC / "tracks.json"):
        roles[(SOURCE / "music" / track["file"]).relative_to(ROOT).as_posix()] = "Nhạc trong playlist"
    roles[(SOURCE / "playlist/list nhạc và thứ tự.jpg").relative_to(ROOT).as_posix()] = "Danh sách thứ tự phát"
    subprocess.run([sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts/studio.py"), "inventory", "--project",
                    PROJECT.name, "--hash"], check=True)
    manifest = PROJECT / "assets.json"
    data = read_json(manifest)
    input_prefixes = tuple(f"{(SOURCE / folder).relative_to(ROOT).as_posix()}/"
                           for folder in ("images", "music", "playlist"))
    for item in data["assets"]:
        if not item["path"].startswith(input_prefixes):
            continue
        role = roles.pop(item["path"], None)
        item["selected"] = role is not None
        if role:
            if not item["exists"] or item["changedSinceSelection"]:
                raise ValueError(f"Review the selected source: {item['path']}")
            item["role"] = role
    if roles:
        raise ValueError(f"Selected files are missing from inventory: {', '.join(roles)}")
    write_json(manifest, data)
    print(f"Verified and staged {len(arrangement['photos'])} photos", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["audio", "photos"])
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    original = args.source.resolve(strict=True)
    if args.mode == "audio":
        prepare_audio(original)
    else:
        stage_photos(original)


if __name__ == "__main__":
    main()
