from dataclasses import dataclass
from functools import lru_cache

import av
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from prepare import FPS, ROOT, SOURCE, WORK, read_json
from media import HEIGHT, WIDTH
from layers import paste_fractional, premultiplied_layer
from picture import load_photo


SIZE = WIDTH, HEIGHT
PALETTES = {"ivory": (237, 220, 199), "rose": (225, 195, 186), "wheat": (229, 204, 182),
            "olive": (219, 214, 189), "wine": (99, 34, 46)}
CAMERAS = {
    "push": ((1.011, 0, 0), (1.054, -5, 4)),
    "recede": ((1.062, -8, 3), (1.012, 0, 0)),
    "driftLeft": ((1.033, 14, 3), (1.04, -15, -3)),
    "driftRight": ((1.04, -15, -3), (1.033, 14, 3)),
    "lift": ((1.035, 3, 10), (1.044, -5, -9)),
    "floatLeft": ((1.019, 7, -2), (1.044, -10, 4)),
    "floatRight": ((1.021, -7, 2), (1.047, 10, -4)),
}


@dataclass(frozen=True)
class Card:
    x: int
    y: int
    width: int
    height: int
    focus: float = .21
    tilt: float = 0
    arch: bool = False


CARDS = {
    "memory": (Card(222, 65, 638, 957, .5, -2),),
    "letter": (Card(686, 72, 505, 931, .28, -1.7), Card(1207, 81, 645, 924, .15, 1)),
    "memoryPair": (Card(710, 169, 457, 721, .5, -2, True), Card(1196, 66, 634, 943, .06, 1.7)),
    "duet": (Card(49, 59, 900, 964, .17, -.8), Card(988, 85, 884, 910, .20, 1.3)),
    "triptych": (Card(68, 141, 541, 820, .26, -3.9), Card(619, 43, 683, 994, .24),
                 Card(1324, 135, 534, 811, .22, 3.7)),
    "arch": (Card(125, 62, 646, 951, .29, 0, True), Card(804, 54, 1021, 966, .12, 1.1)),
    "gallery": (Card(78, 68, 721, 946, .24, -2.4), Card(814, 36, 1037, 1005, .15, 1)),
    "folio": (Card(66, 49, 1119, 966, .12, -1), Card(1211, 112, 631, 864, .25, 3.5)),
}

CLOSE_FOCUS = {"B10": .048, "B12": .024, "B13": .013, "B21": .08, "B46": .068, "B52": .015}
WIDE_FOCUS = {"B10": .17, "B12": .09, "B13": .114, "B21": .098, "B46": .12, "B52": .035}
DISPLAY_FULL = {"memory", "signature"}
TRANSITION_LENGTHS = {"dissolve": 43, "iris": 51, "page": 46, "lens": 49, "flare": 54}
OVERLAYS = SOURCE / "v002/overlays"


def to_bgr(image):
    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGBA2BGR)


@lru_cache(maxsize=48)
def outline(width, height, arch):
    w, h = width * 2, height * 2
    image = Image.new("L", (w, h))
    draw = ImageDraw.Draw(image)
    if arch:
        draw.ellipse((0, 0, w - 1, w - 1), fill=255)
        draw.rectangle((0, w // 2, w - 1, h - 1), fill=255)
    else:
        draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=6, fill=255)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def photo_card(photo, key, card, wine, mirror):
    w, h = card.width, card.height
    band, pad = (5 if wine else 7), 29
    x = WIDTH - card.x - w if mirror else card.x
    y = card.y
    silhouette = outline(w, h, card.arch)
    shadow = Image.new("L", (w + 2 * pad, h + 2 * pad))
    shadow.paste(silhouette, (pad, pad + 10))
    shadow = shadow.filter(ImageFilter.GaussianBlur(13)).point(lambda v: int(v * .33))
    result = Image.new("RGBA", shadow.size, (57, 27, 22, 0))
    result.putalpha(shadow)
    sheet = Image.new("RGBA", (w, h), "#e6bc84" if wine else "#fff1de")
    inner = (w - band * 2, h - band * 2)
    focus = min(card.focus, CLOSE_FOCUS.get(key, 1.0)) if w / h >= .84 else card.focus
    fitted = ImageOps.fit(photo, inner, Image.Resampling.LANCZOS, centering=(.5, focus))
    sheet.paste(fitted, (band, band), outline(*inner, card.arch))
    sheet.putalpha(silhouette)
    result.alpha_composite(sheet, (pad, pad))
    tilt = -card.tilt if mirror else card.tilt
    if tilt:
        spun = result.rotate(tilt, expand=True, resample=Image.Resampling.BICUBIC)
        x -= (spun.width - result.width) // 2
        y -= (spun.height - result.height) // 2
        result = spun
    return result, x - pad, y - pad


def paper(photo, palette):
    miniature = ImageOps.fit(photo, (384, 216), Image.Resampling.LANCZOS, centering=(.5, .35))
    blurred = miniature.filter(ImageFilter.GaussianBlur(17))
    wash = Image.blend(blurred, Image.new("RGB", blurred.size, PALETTES[palette]), .66)
    return wash.resize(SIZE, Image.Resampling.BICUBIC).convert("RGBA")


def shade(base, left, color):
    opacity = (np.linspace(1, 0, 864, dtype=np.float32) ** 1.55) * left
    mask = Image.fromarray(np.broadcast_to(np.round(opacity).astype(np.uint8), (HEIGHT, 864)).copy())
    base.paste(color, (0, 0, 864, HEIGHT), mask)


@lru_cache(maxsize=8)
def flower(name, size, angle):
    with Image.open(OVERLAYS / name) as original:
        sprig = original.convert("RGBA")
    sprig.thumbnail((size, size), Image.Resampling.LANCZOS)
    return sprig.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)


def decorate(base, layout, scene):
    if layout == "memory":
        base.alpha_composite(flower("leaf 04.png", 365, 26), (36, 774))
        base.alpha_composite(flower("Flower 02.png", 232, -18), (190, 876))
        base.alpha_composite(flower("leaf 05.png", 270, 57), (1655, -57))
    elif layout == "signature":
        base.alpha_composite(flower("leaf 05.png", 230, 26), (39, 817))
    elif (layout in {"letter", "arch", "memoryPair"} and scene["palette"] != "wine" and scene["id"] % 3 != 0):
        base.alpha_composite(flower("leaf 04.png", 258, -22), (-32, 889))
        base.alpha_composite(flower("Flower 03.png", 153, 0), (102, 944))


def curve(samples, progress):
    return samples[min(512, max(0, round(512 * progress)))]


def frame_layers(scene, assets):
    keys = scene["photos"]
    photos = [load_photo(ROOT / assets[key]["path"]) for key in keys]
    layout = scene["layout"]
    if layout == "signature":
        image = ImageOps.fit(photos[0], SIZE, Image.Resampling.LANCZOS, centering=(.5, .48)).convert("RGBA")
        shade(image, 197, "#f5e4d2")
        decorate(image, layout, scene)
        return to_bgr(image), None, None
    if layout == "silk":
        focus = WIDE_FOCUS[keys[0]]
        image = ImageOps.fit(photos[0], SIZE, Image.Resampling.LANCZOS, centering=(.5, focus)).convert("RGBA")
        return to_bgr(image), None, None
    wine = scene["palette"] == "wine"
    base = paper(photos[-1], scene["palette"])
    if layout == "letter" and wine:
        shade(base, 178, "#39131e")
    layout_cards = CARDS[layout]
    if (layout == "letter" and (wine or scene["id"] % 3 == 1)):
        left, right = layout_cards
        layout_cards = (Card(left.x, left.y, left.width, left.height, left.focus, 0, True), right)
    cards = [photo_card(photo, key, card, wine, scene["mirror"])
             for key, photo, card in zip(keys, photos, layout_cards, strict=True)]
    for frame, x, y in cards[:-1]:
        base.alpha_composite(frame, (x, y))
    decorate(base, layout, scene)
    lead, x, y = cards[-1]
    behind = to_bgr(base)
    base.alpha_composite(lead, (x, y))
    return to_bgr(base), behind, (premultiplied_layer(lead), x, y)


@lru_cache(maxsize=12)
def lettering(cue):
    path = WORK / "lettering" / (cue + ".png")
    boxes = ((0, 0, 752, 86), (0, 86, 752, 254), (0, 254, 752, 431), (0, 432, 752, 464))
    with Image.open(path) as source:
        image = source.convert("RGBA")
    if image.getpixel((0, 0))[3] != 0:
        raise ValueError(f"Lettering surface has no transparency: {path}")
    layers = []
    for box in boxes:
        section = image.crop(box)
        bounds = section.getchannel("A").getbbox()
        layers.append(premultiplied_layer(section.crop(bounds)) if bounds else None)
    if any(layer is None for layer in layers[1:]):
        raise ValueError(f"Missing line in {path}")
    return layers


@lru_cache(maxsize=1)
def date_art():
    with Image.open(WORK / "lettering/date.png") as source:
        image = source.convert("RGBA")
    return premultiplied_layer(image.crop(image.getchannel("A").getbbox()))


def paint_text(picture, scene, frame, motion):
    text = scene["text"]
    if not text:
        return
    delta = frame - text["in"]
    if delta < 0:
        return
    if frame >= text["out"] and not text["hold"]:
        state = motion["titleOut"]
        offset = frame - text["out"]
    else:
        state = motion["titleIn"]
        offset = delta
    if offset < len(state) or state is motion["titleIn"]:
        parts = lettering(text["id"])
        x, y = {"memory": (1017, 372), "signature": (99, 261)}.get(scene["layout"], (109, 331))
        for index, (part, (alpha, lift, rule)) in enumerate(zip(parts, state[min(offset, len(state) - 1)], strict=True)):
            if part is None:
                continue
            if index == 3 and rule < .999:
                width = max(1, int(part.shape[1] * rule))
                part = cv2.resize(part, (width, part.shape[0]), interpolation=cv2.INTER_AREA)
            paste_fractional(picture, part, x, y + lift, alpha)
            y += part.shape[0] + (29 if index == 0 else 21)
    if text["date"]:
        end_fade = 1 if text["hold"] else 1 - curve(motion["reveal"], (frame - text["out"] - 17) / 41)
        date_progress = curve(motion["layers"], (delta - 28) / 49) * end_fade
        if date_progress > 0:
            plate = date_art()
            paste_fractional(picture, plate, WIDTH - 100 - plate.shape[1],
                             HEIGHT - 88 - plate.shape[0] + 11 * (1 - date_progress), date_progress)


class Picture:
    def __init__(self, scene, assets, motion):
        self.scene = scene
        self.motion = motion
        self.front, self.back, self.lead = frame_layers(scene, assets)
        self.drift = min(scene["frames"] - FPS, round(FPS * (8.2 if scene["layout"] in DISPLAY_FULL else 7.4)))
        self.camera_in, self.camera_out = CAMERAS[scene["motion"]]
        self.arrival = 78 if scene["layout"] in {"letter", "memoryPair", "arch", "triptych", "folio"} else 0
        self.repeat = max(self.drift, self.arrival)
        cue = scene["text"]
        if cue and not cue["hold"]:
            self.repeat = max(self.repeat, cue["out"] + len(motion["titleOut"]), cue["out"] + 59 if cue["date"] else 0)

    def at(self, frame):
        frame = min(frame, self.scene["frames"] - 1)
        moved = self.front
        if self.lead is not None and frame < self.arrival:
            lead, x, y = self.lead
            ease = 1 - curve(self.motion["layers"], frame / self.arrival)
            moved = self.back.copy()
            paste_fractional(moved, lead, x + (-17 if self.scene["mirror"] else 17) * ease, y + 9 * ease)
        t = curve(self.motion["drift"], frame / self.drift)
        scale, x, y = [a + (b - a) * t for a, b in zip(self.camera_in, self.camera_out, strict=True)]
        matrix = np.array(((scale, 0, WIDTH / 2 * (1 - scale) + x),
                           (0, scale, HEIGHT / 2 * (1 - scale) + y)), dtype=np.float32)
        result = cv2.warpAffine(moved, matrix, SIZE, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        paint_text(result, self.scene, frame, self.motion)
        return result


@lru_cache(maxsize=3)
def transition_map(style):
    x = np.linspace(0, 1, WIDTH, dtype=np.float32)[None, :]
    y = np.linspace(0, 1, HEIGHT, dtype=np.float32)[:, None]
    if style == "iris":
        return np.hypot((x - .46) * .93, (y - .46) * .71)
    direction = x if style == "page" else 1 - x
    return (direction + y * .20) / 1.2


@lru_cache(maxsize=2)
def flare_frames(amber):
    asset = "TR_03_2.mov" if amber else "TR_02_2.mov"
    with av.open(str(OVERLAYS / asset), metadata_errors="replace") as clip:
        return [frame.reformat(width=480, height=270, format="bgr24").to_ndarray() for frame in clip.decode(video=0)]


def change(previous, incoming, scene, frame, motion):
    style = scene["transition"]
    duration = TRANSITION_LENGTHS[style]
    blend = curve(motion["reveal"], frame / duration)
    if blend <= 0:
        return previous
    if blend >= 1:
        return incoming
    if style in ("iris", "page"):
        mask = transition_map("pageLeft" if style == "page" and scene["mirror"] else style)
        edge = (1.24 * blend - .12 - mask) * 8.333333
        alpha = cv2.cvtColor((np.clip(edge, 0, 1) * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
        return cv2.add(cv2.multiply(incoming, alpha, scale=1/255),
                       cv2.multiply(previous, cv2.bitwise_not(alpha), scale=1/255))
    mixed = cv2.addWeighted(previous, 1 - blend, incoming, blend, 0)
    peak = 4 * blend * (1 - blend)
    if style == "lens":
        small = cv2.resize(mixed, (480, 270), interpolation=cv2.INTER_AREA)
        soft = cv2.resize(cv2.GaussianBlur(small, (9, 9), 1.8), SIZE, interpolation=cv2.INTER_LINEAR)
        mixed = cv2.addWeighted(mixed, 1 - .49 * peak, soft, .49 * peak, 0)
    if style == "flare":
        clip = flare_frames(scene["chapter"] > 4)
        phase = frame / duration * (len(clip) - 1)
        index = int(phase)
        speed = phase - index
        light = cv2.addWeighted(clip[index], 1 - speed, clip[min(index + 1, len(clip) - 1)], speed, 0)
        light = cv2.convertScaleAbs(cv2.resize(light, SIZE, interpolation=cv2.INTER_LINEAR), alpha=peak * .37)
        mixed = cv2.bitwise_not(cv2.multiply(cv2.bitwise_not(mixed), cv2.bitwise_not(light), scale=1/255))
    return mixed
