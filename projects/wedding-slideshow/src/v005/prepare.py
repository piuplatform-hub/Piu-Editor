import argparse
from pathlib import Path
import subprocess
import sys
import wave

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from media import (OUTPUT, PREVIEWS, PROJECT, RATE, ROOT, SOURCE, digest, normalized_track,
                   read_json, staged_copy, write_json, write_pcm)


WORK = PROJECT / "working/v005"
PUBLIC = PROJECT / "public/v005"
PREVIEW = PREVIEWS / "v005"
VIDEO = OUTPUT / "van-cong-thuong-huyen-tu-hom-nay-v005.mp4"
STORY = HERE / "story.json"
PLAN = HERE / "timeline.json"
AUDIO_PLAN = WORK / "audio-plan.json"
SOUNDTRACK = WORK / "soundtrack.wav"
CURATED = PROJECT / "src/v002/curated.json"
SOURCE_MUSIC = SOURCE / "v005/music"
FPS = 50
SPF = RATE // FPS
CROSSFADE = 56
OVERLAYS = ("Flower 02.png", "Flower 03.png", "leaf 04.png", "leaf 05.png", "TR_02_2.mov", "TR_03_2.mov")


def source_file(root, relative, destination, authority=None):
    original = root / relative
    if not original.resolve().is_relative_to(root):
        raise ValueError(f"Source escapes the wedding folder: {relative}")
    if authority and digest(original) != authority:
        raise ValueError(f"Curated photo changed: {relative}")
    return staged_copy(original, destination)


def rhythm_marks(pcm, frames):
    mono = pcm[:frames * SPF:8].mean(axis=1)
    win, hop = 384, 120
    audio_windows = np.lib.stride_tricks.sliding_window_view(mono, win)[::hop]
    spectrum = np.abs(np.fft.rfft(audio_windows * np.hanning(win).astype(np.float32), axis=1))
    bands = np.log1p(spectrum[:, 4:160] * .0002)
    flux = np.maximum(0, np.diff(bands, axis=0, prepend=bands[:1])).mean(axis=1)
    flux = np.convolve(flux, [.22, .56, .22], mode="same")
    threshold = float(np.quantile(flux, .53))
    candidates = np.nonzero((flux[1:-1] >= flux[:-2]) & (flux[1:-1] > flux[2:]) & (flux[1:-1] > threshold))[0] + 1
    return [[int(index + round(win / (2 * hop))), round(float(flux[index]), 5)]
            for index in candidates if index + 2 < frames]


def prepare_mix(original, story):
    tracks = story["tracks"]
    paths = [SOURCE_MUSIC / track["file"] for track in tracks]
    recorded = [source_file(original, Path("nhạc cưới") / track["file"], path)
                for track, path in zip(tracks, paths, strict=True)]
    overlap = CROSSFADE * SPF
    phase = np.linspace(0, np.pi / 2, overlap, dtype=np.float32)[:, None]
    fade_out, fade_in = np.cos(phase), np.sin(phase)
    pending = WORK / "soundtrack.pending.wav"
    chapters, marks = [], []
    cursor, tail = 0, None
    with wave.open(str(pending), "wb") as wav:
        wav.setparams((2, 2, RATE, 0, "NONE", "PCM"))
        for index, (track, path, sha) in enumerate(zip(tracks, paths, recorded, strict=True)):
            pcm, full, trim_in, trim_out, lufs, peak, gain = normalized_track(path, WORK)
            frames = (full - trim_in - trim_out) * 2
            if frames <= 2 * CROSSFADE or len(pcm) != frames * SPF:
                raise ValueError(f"Invalid music length: {path}")
            start = cursor
            if tail is None:
                attack = round(.33 * RATE)
                pcm[:attack] *= np.linspace(0, 1, attack, dtype=np.float32)[:, None]
                first = 0
            else:
                write_pcm(wav, tail * fade_out + pcm[:overlap] * fade_in)
                first = overlap
                cursor += CROSSFADE
            last = len(pcm)
            if index + 1 < len(tracks):
                tail = pcm[-overlap:].copy()
                last -= overlap
            else:
                release, quiet = round(2.2 * RATE), round(.32 * RATE)
                pcm[-release:-quiet] *= np.linspace(1, 0, release - quiet, dtype=np.float32)[:, None]
                pcm[-quiet:] = 0
            marks.append(rhythm_marks(pcm, last // SPF))
            write_pcm(wav, pcm[first:last])
            cursor += (last - first) // SPF
            chapters.append({"index": index + 1, "title": track["title"], "artist": track["artist"],
                             "start": start, "end": cursor, "sourceFrames": full * 2,
                             "trimIn": trim_in * 2, "trimOut": trim_out * 2, "sourceSha256": sha,
                             "path": path.relative_to(ROOT).as_posix(), "sourceLufs": lufs,
                             "sourceTruePeakDbtp": peak, "gainDb": round(gain, 3)})
            print(f"{index+1:02d}/{len(tracks)} {track['title']} · {(cursor-start)/FPS:.2f}s · {gain:+.1f} dB", flush=True)
    with wave.open(str(pending), "rb") as wav:
        if wav.getnframes() != cursor * SPF:
            raise ValueError("WAV samples and picture frames differ")
    pending.replace(SOUNDTRACK)
    write_json(AUDIO_PLAN, {"fps": FPS, "totalFrames": cursor, "crossfadeFrames": CROSSFADE,
                            "soundtrackSha256": digest(SOUNDTRACK), "tracks": chapters})
    write_json(WORK / "rhythm-marks.json", marks)
    print(f"Music mixed: {len(tracks)} tracks, {cursor/FPS:.2f}s", flush=True)


def prepare_picture(original):
    curated = read_json(CURATED)
    seen = set()
    picks = {}
    for key, entry in curated.items():
        sha = entry["sha256"]
        if sha in seen:
            continue
        seen.add(sha)
        path = SOURCE / "v002/photos" / (key + ".jpg")
        actual = source_file(original, Path("Image") / entry["file"], path, sha)
        picks[key] = {"path": path.relative_to(ROOT).as_posix(), "sha256": actual}
    font_dir = ROOT / "projects/wedding-opener/public/fonts"
    for name in ("CormorantGaramond.ttf", "CormorantGaramond-Italic.ttf", "BeVietnamPro-Medium.ttf"):
        staged_copy(font_dir / name, PUBLIC / "fonts" / name)
    write_json(WORK / "picture-inputs.json", picks)
    print(f"Photo sources verified: {len(picks)} distinct photos from {len(curated)} files.", flush=True)


def inventory():
    audio = read_json(AUDIO_PLAN)
    picks = read_json(WORK / "picture-inputs.json")
    chosen = {track["path"]: "Nhạc chiếu tiệc V005" for track in audio["tracks"]}
    chosen.update({asset["path"]: "Ảnh đã lọc dùng trong V005" for asset in picks.values()})
    for name in OVERLAYS:
        name_path = SOURCE / "v002/overlays" / name
        chosen[name_path.relative_to(ROOT).as_posix()] = "Hiệu ứng dùng trong V005"
    subprocess.run([sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts/studio.py"),
                    "inventory", "--project", PROJECT.name, "--hash"], check=True)
    target = PROJECT / "assets.json"
    data = read_json(target)
    known = {row["path"]: row for row in data["assets"]}
    for path, role in chosen.items():
        row = known[path]
        if not row["exists"] or row["changedSinceSelection"]:
            raise ValueError(f"Media missing or changed: {path}")
        row["selected"] = True
        uses = row.setdefault("usedBy", [])
        if "v005" not in uses:
            uses.append("v005")
        if not row.get("role"):
            row["role"] = role
    write_json(target, data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("original", type=Path)
    args = parser.parse_args()
    root = args.original.resolve(strict=True)
    WORK.mkdir(parents=True, exist_ok=True)
    prepare_picture(root)
    prepare_mix(root, read_json(STORY))
    inventory()
