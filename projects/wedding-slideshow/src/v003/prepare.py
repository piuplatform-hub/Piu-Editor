import argparse
from pathlib import Path
import sys
import wave

import numpy as np
from PIL import Image, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from media import (AUDIO_PLAN, PROJECT, RATE, ROOT, SOURCE, SOUNDTRACK, digest, read_json, run, staged_copy)
from picture import load_photo


STAGED = SOURCE / "v002"
DEFAULT_BACKDROPS = {"B21": (222, 202, 182), "B41": (225, 210, 194), "B40": (105, 27, 38)}
SERIF_FONTS = ("CormorantGaramond.ttf", "CormorantGaramond-Italic.ttf")


def selected_copy(path, destination, manifest):
    selected_hash = manifest.get(path.relative_to(ROOT).as_posix())
    if not selected_hash or digest(path) != selected_hash:
        raise ValueError(f"Missing or changed V002 asset: {path}")
    staged_copy(path, destination)


def photos(plan, public):
    registry = read_json(PROJECT / "assets.json")
    selected = {row["path"]: row["sha256"] for row in registry["assets"] if row["exists"] and row["selected"]}
    for key in {key for scene in plan["scenes"] for key in scene["photos"]}:
        selected_copy(STAGED / "photos" / f"{key}.jpg", public / "photos" / f"{key}.jpg", selected)
    for name in ("Flower 03.png", "leaf 04.png", "leaf 05.png", "TR_02_2.mov"):
        selected_copy(STAGED / "overlays" / name, public / "effects" / name, selected)
    font_root = ROOT / "projects/wedding-opener/public/fonts"
    for name in (*SERIF_FONTS, *plan.get("additionalFonts", [])):
        staged_copy(font_root / name, public / "fonts" / name)
    for key, tint in plan.get("backdrops", DEFAULT_BACKDROPS).items():
        image = load_photo(public / "photos" / f"{key}.jpg")
        paper = ImageOps.fit(image, (480, 270), Image.Resampling.LANCZOS, centering=(.5, .33))
        paper = paper.filter(ImageFilter.GaussianBlur(21))
        wash = Image.blend(paper, Image.new("RGB", paper.size, tuple(tint)), .62)
        wash.save(public / "photos" / f"{key}-background.jpg", quality=93)
    # Browser-friendly, audio-free version of the actual V002 template flare for OffthreadVideo.
    run("ffmpeg", "-v", "error", "-nostdin", "-y", "-i", public / "effects/TR_02_2.mov",
        "-map", "0:v:0", "-vf", "scale=960:540", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", public / "effects/ceremony-flare.mp4")


def music(plan, work):
    if digest(SOUNDTRACK) != read_json(AUDIO_PLAN)["soundtrackSha256"]:
        raise ValueError("Source music mix differs from its recorded hash")
    start = plan["musicStartFrame"] * RATE // plan["fps"]
    duration = plan["durationInFrames"] * RATE // plan["fps"]
    with wave.open(str(SOUNDTRACK), "rb") as original:
        if (original.getnchannels(), original.getsampwidth(), original.getframerate()) != (2, 2, RATE):
            raise ValueError("Expected the frozen stereo 48 kHz WAV")
        original.setpos(start)
        audio = np.frombuffer(original.readframes(duration), dtype="<i2").reshape(-1, 2).copy()
    if len(audio) != duration:
        raise ValueError("Not enough song samples for the preview")
    attack, release = RATE // 4, round(RATE * 1.4)
    audio[:attack] = (audio[:attack] * np.linspace(0, 1, attack)[:, None]).round().astype("<i2")
    audio[-release:] = (audio[-release:] * np.linspace(1, 0, release)[:, None]).round().astype("<i2")
    with wave.open(str(work / "music.wav"), "wb") as output:
        output.setparams((2, 2, RATE, 0, "NONE", "PCM"))
        output.writeframes(audio.tobytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("version", nargs="?", choices=("v003", "v004"), default="v003")
    version = parser.parse_args().version
    plan = read_json(PROJECT / "src" / version / "timeline.json")
    work = PROJECT / "working" / version
    work.mkdir(parents=True, exist_ok=True)
    photos(plan, PROJECT / "public" / version)
    music(plan, work)
    print(f"{version}: prepared the reviewed photos, fonts, flare and {plan['durationInFrames'] / plan['fps']:.2f}s of music.")
