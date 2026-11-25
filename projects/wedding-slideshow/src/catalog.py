import argparse
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


PROJECT = Path(__file__).resolve().parents[1]
WORK = PROJECT / "working"
FONT = Path("C:/Windows/Fonts/segoeui.ttf")


def scan_photo(entry):
    photo, key, group = entry
    with Image.open(photo) as source:
        rotated = source.getexif().get(274, 1) in {5, 6, 7, 8}
        width, height = source.size[::-1] if rotated else source.size
        source.draft("RGB", (440, 440))
        thumb = ImageOps.exif_transpose(source).convert("RGB")
        thumb.thumbnail((440, 440), Image.Resampling.LANCZOS)
    gray = cv2.cvtColor(np.asarray(thumb), cv2.COLOR_RGB2GRAY)
    coeff = cv2.dct(cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA).astype(np.float32))[:8, :8].ravel()[1:]
    median = np.median(coeff)
    phash = int("".join("1" if value > median else "0" for value in coeff), 2)
    with BytesIO() as buffer:
        thumb.thumbnail((176, 126), Image.Resampling.LANCZOS)
        thumb.save(buffer, format="JPEG", quality=86)
        tile = buffer.getvalue()
    return {
        "id": key, "group": group, "file": photo.name, "width": width, "height": height,
        "phash": f"{phash:016x}", "bytes": photo.stat().st_size,
    }, tile


def photo_entries(source_root):
    folder = source_root / "Image"
    album = sorted(p for p in folder.iterdir() if p.is_file() and not p.is_symlink() and p.suffix.lower() in {".jpg", ".jpeg"})
    session = sorted(p for d in folder.iterdir() if d.is_dir() and not d.is_symlink() and d.resolve().is_relative_to(folder.resolve())
                     for p in d.iterdir() if p.is_file() and not p.is_symlink() and p.suffix.lower() in {".jpg", ".jpeg"})
    entries = [(p, f"A{index:03d}", "album") for index, p in enumerate(album, 1)]
    entries.extend((p, p.stem, "session") for p in session)
    if len({key for _, key, _ in entries}) != len(entries):
        raise ValueError("Photo IDs must be unique")
    return entries


def boards(rows):
    columns, cell_w, cell_h, page_size = 8, 182, 150, 48
    font = ImageFont.truetype(str(FONT), 15)
    for page, begin in enumerate(range(0, len(rows), page_size), 1):
        batch = rows[begin:begin + page_size]
        board = Image.new("RGB", (columns * cell_w, ((len(batch) + columns - 1) // columns) * cell_h), "#23201e")
        draw = ImageDraw.Draw(board)
        for index, (record, image_bytes) in enumerate(batch):
            x = (index % columns) * cell_w
            y = (index // columns) * cell_h
            with Image.open(BytesIO(image_bytes)) as tile:
                board.paste(tile, (x + (cell_w - tile.width) // 2, y + 2 + (126 - tile.height) // 2))
            draw.text((x + 8, y + 128), record["id"], font=font, fill="#fff8ef")
        board.save(WORK / f"source-atlas-{page:02d}.jpg", quality=92)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    cv2.setNumThreads(1)
    entries = photo_entries(args.source.resolve())
    WORK.mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=5) as pool:
        scanned = list(pool.map(scan_photo, entries))
    catalog = [{**record, "source": path.relative_to(args.source.resolve()).as_posix()}
               for (record, _), (path, _, _) in zip(scanned, entries)]
    (WORK / "photo-catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    album = [row for row in scanned if row[0]["group"] == "album"]
    session = [row for row in scanned if row[0]["group"] == "session"]
    sampled = [row for i, row in enumerate(session) if i % 3 == 0 or i == len(session) - 1]
    boards(album + sampled)
    print(f"Scanned {len(album)} album photos and {len(session)} session photos. Atlas samples {len(album) + len(sampled)}.")


if __name__ == "__main__":
    main()
