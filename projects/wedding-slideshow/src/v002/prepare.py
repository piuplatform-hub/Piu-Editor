import argparse
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from media import PROJECT, ROOT, SOURCE, digest, read_json, staged_copy, write_json


HERE = Path(__file__).resolve().parent
WORK = PROJECT / "working/v002"
INPUTS = SOURCE / "v002"
PLAN = HERE / "preview-plan.json"
CATALOG = HERE / "curated.json"
FOOTAGE = Path("wedding folder/(Footage)/02 Others/Fotage")
FLARES = Path("wedding folder/(Footage)/02 Others/Transition/(do not edit)/Flares")
OVERLAYS = {
    "Flower 02.png": FOOTAGE, "Flower 03.png": FOOTAGE,
    "leaf 01.png": FOOTAGE, "leaf 04.png": FOOTAGE, "leaf 05.png": FOOTAGE,
    "Bokeh_02.mov": FOOTAGE, "TR_03_2.mov": FLARES, "TR_02_2.mov": FLARES,
}


def freeze_catalog(original):
    if CATALOG.exists():
        raise FileExistsError(f"Existing V002 photo selection: {CATALOG}")
    source_dir = (original / "Image").resolve(strict=True)
    files = sorted(path for path in source_dir.iterdir() if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg"}
                   and not path.is_symlink() and path.resolve().is_relative_to(source_dir))
    if len(files) != 55:
        raise ValueError(f"The reviewed collection has 55 photos, found {len(files)}")
    records = {f"B{index:02d}": {"file": path.name, "sha256": digest(path)} for index, path in enumerate(files, 1)}
    write_json(CATALOG, records)


def copied_input(original, source, local, expected_hash=None):
    path = original / source
    if not path.resolve().is_relative_to(original):
        raise ValueError(f"Input escapes the wedding folder: {path}")
    if expected_hash and digest(path) != expected_hash:
        raise ValueError(f"The curated photo changed after review: {path.name}")
    return staged_copy(path, local)


def prepare(original):
    plan = read_json(PLAN)
    catalog = read_json(CATALOG)
    photo_ids = {key for scene in plan["scenes"] for key in scene["photos"]}
    if not photo_ids <= catalog.keys():
        raise ValueError(f"Unknown curated photos: {photo_ids - catalog.keys()}")
    uses = {}
    copied = {}
    for key, asset in catalog.items():
        local = INPUTS / "photos" / f"{key}.jpg"
        root_path = local.relative_to(ROOT).as_posix()
        copied[root_path] = copied_input(original, Path("Image") / asset["file"], local, asset["sha256"])
        if key in photo_ids:
            uses[root_path] = "Ảnh đã lọc dùng trong preview V002"
    for name, parent in OVERLAYS.items():
        local = INPUTS / "overlays" / name
        root_path = local.relative_to(ROOT).as_posix()
        copied[root_path] = copied_input(original, parent / name, local)
        uses[root_path] = "Lớp hiệu ứng từ template người dùng gửi"

    subprocess.run([sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts/studio.py"), "inventory",
                    "--project", PROJECT.name, "--hash"], check=True)
    manifest_path = PROJECT / "assets.json"
    old = read_json(manifest_path)
    for row in old["assets"]:
        name = row["path"]
        if name not in copied:
            continue
        if not row["exists"] or row["changedSinceSelection"] or row["sha256"] != copied.pop(name):
            raise ValueError(f"Staged input does not match the original: {name}")
        row["selected"] = name in uses
        row["role"] = uses.get(name, "")
        row["notes"] = "Ảnh hoặc hiệu ứng từ nguồn V002."
    if copied:
        raise ValueError(f"Missing entries for V002: {list(copied)}")
    write_json(manifest_path, old)
    print(f"V002: staged {len(catalog)} curated photos, selected {len(photo_ids)} for the preview and {len(OVERLAYS)} overlays.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("original", type=Path)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    original = args.original.resolve(strict=True)
    if args.freeze:
        freeze_catalog(original)
    prepare(original)


if __name__ == "__main__":
    main()
