from functools import lru_cache
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageFont, ImageOps

from media import FPS, HEIGHT, ROOT, WIDTH


PALETTES = {"ivory": (241, 230, 216), "wine": (70, 33, 43)}
TITLE_FONT = ROOT / "projects/wedding-opener/public/fonts/CormorantGaramond-Italic.ttf"
MOTIONS = {
    # Each pair is (scale, horizontal offset, vertical offset).
    "approach": ((1.007, 0, 0), (1.044, -7, 3)),
    "recede": ((1.046, 5, -5), (1.009, 0, 0)),
    "drift_left": ((1.028, 11, 1), (1.035, -11, -3)),
    "drift_right": ((1.034, -11, -3), (1.028, 11, 1)),
    "lift": ((1.024, -4, 7), (1.040, 4, -8)),
    "settle": ((1.037, 4, -7), (1.018, -3, 4)),
}


@lru_cache(maxsize=7)
def load_photo(path):
    with Image.open(path) as image:
        profile = image.info.get("icc_profile")
        image.draft("RGB", (1500, 1500))
        oriented = ImageOps.exif_transpose(image)
        if profile:
            return ImageCms.profileToProfile(oriented, BytesIO(profile), ImageCms.createProfile("sRGB"), outputMode="RGB")
        return oriented.convert("RGB")


def pane_widths(scene):
    layout = scene["layout"]
    if layout == "wide":
        return [WIDTH]
    if layout == "pair":
        return [942, 942]
    if layout == "spread":
        return [1040, 844] if scene["id"] % 2 else [844, 1040]
    if layout == "feature":
        return [548, 776, 548]
    if layout == "trio":
        return [624, 624, 624]
    raise ValueError(f"Unknown photo layout: {layout}")


def add_title(canvas, label):
    if not label:
        return
    font_path = TITLE_FONT if TITLE_FONT.is_file() else Path("C:/Windows/Fonts/georgiai.ttf")
    draw = ImageDraw.Draw(canvas)
    if label == "Từ hôm nay":
        font = ImageFont.truetype(str(font_path), 111)
        draw.text((83, 314), "Từ", font=font, fill="#382923", anchor="ls")
        draw.text((83, 418), "hôm nay", font=font, fill="#382923", anchor="ls")
        return
    reach, depth = 690, 300
    left = np.linspace(1, 0, reach, dtype=np.float32) ** .62
    bottom = np.linspace(0, 1, depth, dtype=np.float32) ** .8
    opacity = Image.fromarray(np.rint(224 * bottom[:, None] * left[None, :]).astype(np.uint8))
    canvas.paste((31, 16, 24), (0, HEIGHT - depth, reach, HEIGHT), opacity)
    font = ImageFont.truetype(str(font_path), 104)
    draw.text((76, HEIGHT - 80), label, font=font, fill="#fff9ed", anchor="ls", stroke_width=1, stroke_fill="#312026")


def compose(scene, assets):
    widths = pane_widths(scene)
    if len(widths) != len(scene["photos"]):
        raise ValueError(f"Layout and photo count differ for slide {scene['id']}")
    rail = 0 if scene["layout"] == "wide" else 12
    pane_height = HEIGHT - 2 * rail
    canvas = Image.new("RGB", (WIDTH, HEIGHT), PALETTES[scene["palette"]])
    x = rail
    for key, width in zip(scene["photos"], widths):
        photo = load_photo(ROOT / assets[key]["path"])
        # Anchor taller photos toward the upper portion in the wider panes.
        # The narrower panes retain the full vertical composition.
        anchor = (0.5, 0.14 if photo.height > photo.width else 0.45)
        tile = ImageOps.fit(photo, (width, pane_height), Image.Resampling.LANCZOS, centering=anchor)
        canvas.paste(tile, (x, rail))
        x += width + rail
    add_title(canvas, scene["title"])
    return cv2.cvtColor(np.asarray(canvas), cv2.COLOR_RGB2BGR)


def eased(value):
    return value * value * (3 - 2 * value)


def camera_length(scene):
    return min(round(scene["frames"] * .81), round(FPS * (7.4 if scene["layout"] == "wide" else 8.5)))


def moving_picture(canvas, scene, relative_frame):
    length = camera_length(scene)
    progress = eased(min(1, relative_frame / max(1, length)))
    first, last = MOTIONS[scene["motion"]]
    scale, dx, dy = (a + (b - a) * progress for a, b in zip(first, last))
    transform = np.array([[scale, 0, WIDTH / 2 * (1 - scale) + dx],
                          [0, scale, HEIGHT / 2 * (1 - scale) + dy]], dtype=np.float32)
    return cv2.warpAffine(canvas, transform, (WIDTH, HEIGHT), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def transition_picture(previous, picture, mode, amount):
    progress = eased(amount)
    if mode == "dissolve":
        return cv2.addWeighted(previous, 1 - progress, picture, progress, 0)
    reverse = mode == "wipe_left"
    before, after = (previous[:, ::-1], picture[:, ::-1]) if reverse else (previous, picture)
    feather = 112
    edge = (WIDTH + feather) * progress - feather / 2
    left, right = max(0, int(edge - feather / 2)), min(WIDTH, int(edge + feather / 2))
    result = before.copy()
    result[:, :left] = after[:, :left]
    alpha = np.clip((edge + feather / 2 - np.arange(left, right, dtype=np.float32)) / feather, 0, 1)[None, :, None]
    result[:, left:right] = np.rint(after[:, left:right] * alpha + before[:, left:right] * (1 - alpha)).astype(np.uint8)
    return np.ascontiguousarray(result[:, ::-1]) if reverse else result
