from dataclasses import dataclass
from functools import lru_cache

import av
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from media import FPS, HEIGHT, ROOT, WIDTH
from layers import paste_fractional, premultiplied_layer
from picture import load_photo, transition_picture
from prepare import INPUTS


FONTS = ROOT / "projects/wedding-opener/public/fonts"
PHOTO_SIZE = (WIDTH, HEIGHT)
NEUTRAL = (224, 203, 180)
WINE = (89, 31, 43)


@dataclass(frozen=True)
class Card:
    bounds: tuple
    focus: float = .18
    arch: bool = False
    lean: float = 0
    travel: tuple = (0, -10)


CARDS = {
    "memories": (
        Card((126, 102, 568, 846), .33, True, travel=(-17, -10)),
        Card((752, 40, 1088, 998), .015, travel=(13, 8)),
    ),
    "portraits": (
        Card((84, 152, 560, 786), .27, lean=3, travel=(-18, -9)),
        Card((647, 44, 652, 994), .26, travel=(0, 12)),
        Card((1308, 149, 526, 780), .27, lean=-3, travel=(18, -10)),
    ),
    "toast": (
        Card((32, 32, 1120, 1016), .02, travel=(12, -5)),
        Card((1175, 59, 715, 962), .24, travel=(-11, 7)),
    ),
    "dance": (
        Card((22, 31, 712, 1018), .30, travel=(-9, 12)),
        Card((752, 103, 514, 890), .14, travel=(5, -13)),
        Card((1285, 47, 609, 986), .36, travel=(11, 10)),
    ),
    "gestures": (
        Card((63, 50, 1026, 985), .18, travel=(16, 4)),
        Card((1137, 100, 691, 890), .34, travel=(-12, 12)),
    ),
    "botanical": (
        Card((109, 64, 667, 948), .33, True, travel=(-16, -9)),
        Card((796, 41, 1058, 998), .22, travel=(16, 8)),
    ),
    "ceremony": (
        Card((63, 66, 606, 954), .36, True, travel=(-12, -10)),
        Card((690, 45, 642, 998), .24, travel=(0, 9)),
        Card((1351, 112, 516, 845), .33, lean=-2, travel=(14, -10)),
    ),
    "closing": (
        Card((49, 90, 589, 910), .26, travel=(-16, -10)),
        Card((660, 43, 665, 992), .26, travel=(3, 8)),
        Card((1350, 92, 518, 902), .24, travel=(14, -9)),
    ),
}

# The coordinates place flowers and leaves on the frame edges or the paper between photos.
BOTANICALS = {
    "opening": (("leaf 05.png", 55, 787, 192, 26, .6),),
    "memories": (
        ("leaf 04.png", -50, 687, 360, -18, .85),
        ("leaf 01.png", 594, 772, 243, 30, .75),
        ("Flower 02.png", 75, 830, 206, 22, .87),
        ("Flower 03.png", 608, 912, 185, -20, .92),
    ),
    "botanical": (
        ("leaf 05.png", 658, 614, 277, 19, .75),
        ("leaf 04.png", -60, 752, 309, 10, .9),
        ("Flower 03.png", 73, 863, 219, -6, .89),
    ),
}


def smooth(value):
    value = min(1., max(0., value))
    return value * value * (3 - 2 * value)


@lru_cache(maxsize=40)
def mask(size, arch, antialias=False):
    multiplier = 2 if antialias else 1
    width, height = (value * multiplier for value in size)
    silhouette = Image.new("L", (width, height))
    draw = ImageDraw.Draw(silhouette)
    if arch:
        draw.ellipse((0, 0, width - 1, width - 1), fill=255)
        draw.rectangle((0, width // 2, width - 1, height - 1), fill=255)
    else:
        draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=4 * multiplier, fill=255)
    return silhouette.resize(size, Image.Resampling.LANCZOS) if antialias else silhouette


def make_card(photo, card, ceremony, antialias=False):
    x, y, width, height = card.bounds
    border, margin = (5 if ceremony else 7), 20
    image_size = width - border * 2, height - border * 2
    fitted = ImageOps.fit(photo, image_size, Image.Resampling.LANCZOS, centering=(.5, card.focus))
    layer = Image.new("RGBA", (width + 2 * margin, height + 2 * margin))
    shadow = Image.new("L", layer.size)
    outer = mask((width, height), card.arch, antialias)
    shadow.paste(outer, (margin, margin + 3))
    shadow = shadow.filter(ImageFilter.GaussianBlur(11)).point(lambda value: value * .38)
    layer.paste((30, 18, 15, 255), (0, 0, *layer.size), shadow)
    frame = Image.new("RGBA", (width, height), "#f6eadb" if not ceremony else "#e5bc83")
    frame.paste(fitted, (border, border), mask(image_size, card.arch, antialias))
    frame.putalpha(outer)
    layer.alpha_composite(frame, (margin, margin))
    if card.lean:
        angled = layer.rotate(card.lean, expand=True, resample=Image.Resampling.BICUBIC)
        x -= (angled.width - layer.width) // 2
        y -= (angled.height - layer.height) // 2
        layer = angled
    return layer, x - margin, y - margin


def textured_background(photo, ceremony):
    mini = ImageOps.fit(photo, (480, 270), Image.Resampling.LANCZOS, centering=(.5, .38))
    mini = mini.filter(ImageFilter.GaussianBlur(18))
    paper = Image.new("RGB", mini.size, WINE if ceremony else NEUTRAL)
    wash = Image.blend(mini, paper, .56 if ceremony else .48)
    return wash.resize(PHOTO_SIZE, Image.Resampling.BICUBIC).convert("RGBA")


def make_title(label):
    layer = Image.new("RGBA", (680, 405))
    if not label:
        return layer
    text = ImageDraw.Draw(layer)
    roman = ImageFont.truetype(str(FONTS / "CormorantGaramond.ttf"), 139)
    italic = ImageFont.truetype(str(FONTS / "CormorantGaramond-Italic.ttf"), 132)
    text.text((9, 136), "Từ", font=roman, fill="#382820", anchor="ls")
    text.text((5, 267), "hôm nay", font=italic, fill="#382820", anchor="ls")
    text.line((15, 306, 157, 306), fill="#997353", width=2)
    return layer


@lru_cache(maxsize=10)
def botanical(spec):
    name, _, _, size, turn, opacity = spec
    with Image.open(INPUTS / "overlays" / name) as source:
        layer = source.convert("RGBA")
    layer.thumbnail((size, size), Image.Resampling.LANCZOS)
    layer = layer.rotate(turn, expand=True, resample=Image.Resampling.BICUBIC)
    layer.putalpha(layer.getchannel("A").point(lambda value: value * opacity))
    return layer


@lru_cache(maxsize=3)
def footage(name):
    with av.open(str(INPUTS / "overlays" / name), metadata_errors="replace") as clip:
        return tuple(frame.reformat(width=480, height=270, format="bgr24").to_ndarray() for frame in clip.decode(video=0))


def screen(base, overlay, gain):
    small = cv2.convertScaleAbs(overlay, alpha=gain)
    light = cv2.resize(small, PHOTO_SIZE, interpolation=cv2.INTER_LINEAR)
    return cv2.bitwise_not(cv2.multiply(cv2.bitwise_not(base), cv2.bitwise_not(light), scale=1 / 255))


def interpolate_footage(clip, position):
    first = min(len(clip) - 1, int(position))
    if first + 1 == len(clip):
        return clip[first]
    fraction = position - first
    if fraction == 0:
        return clip[first]
    return cv2.addWeighted(clip[first], 1 - fraction, clip[first + 1], fraction, 0)


def paste_rounded(canvas, layer, x, y, opacity=1.):
    if opacity < 1:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda value: value * opacity))
    canvas.alpha_composite(layer, (round(x), round(y)))


class Scene:
    def __init__(self, config, fps=FPS):
        self.layout = config["layout"]
        self.sample_scale = FPS / fps
        self.subpixel = fps != FPS
        prepare_layer = premultiplied_layer if self.subpixel else lambda image: image
        self.paste = paste_fractional if self.subpixel else paste_rounded
        photos = [load_photo(INPUTS / "photos" / f"{key}.jpg") for key in config["photos"]]
        self.title = prepare_layer(make_title(config.get("title")))
        self.cards = []
        self.leaves = [(prepare_layer(botanical(spec)), spec[1], spec[2]) for spec in BOTANICALS.get(self.layout, ())]
        if self.layout in ("opening", "veil"):
            focus = (.5, .49 if self.layout == "opening" else .095)
            self.base = ImageOps.fit(photos[0], PHOTO_SIZE, Image.Resampling.LANCZOS, centering=focus).convert("RGBA")
        else:
            ceremony = self.layout == "ceremony"
            self.base = textured_background(photos[-1], ceremony)
            cards = CARDS[self.layout]
            for photo, card in zip(photos, cards, strict=True):
                layer, x, y = make_card(photo, card, ceremony, self.subpixel)
                self.cards.append(((prepare_layer(layer), x, y), card.travel))
        if self.subpixel:
            self.base = cv2.cvtColor(np.asarray(self.base), cv2.COLOR_RGBA2BGR)

    def picture(self, relative, frames):
        phase = smooth(relative / max(1, frames - 1))
        template_frame = relative * self.sample_scale
        if self.layout in ("opening", "veil"):
            scale = 1.016 + .043 * (phase if self.layout == "veil" else 1 - phase)
            x = (WIDTH / 2 * (1 - scale)) + (phase - .5) * 10
            y = (HEIGHT / 2 * (1 - scale)) - 5
            if self.subpixel:
                matrix = np.array(((scale, 0, x), (0, scale, y)), dtype=np.float32)
                scene = cv2.warpAffine(self.base, matrix, PHOTO_SIZE, flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            else:
                scene = self.base.transform(PHOTO_SIZE, Image.Transform.AFFINE, (1 / scale, 0, -x / scale, 0, 1 / scale, -y / scale),
                                            resample=Image.Resampling.BICUBIC)
        else:
            scene = self.base.copy()
        for index, ((card, x, y), (dx, dy)) in enumerate(self.cards):
            arrival = (1 - smooth((template_frame - index * 2) / 31)) * 19
            self.paste(scene, card, x + (phase - .5) * dx + arrival * (-1 if index % 2 else 1),
                       y + (phase - .5) * dy + arrival)
        for index, (leaf, x, y) in enumerate(self.leaves):
            self.paste(scene, leaf, x + (phase - .5) * (24 + 5 * index), y - 22 * phase)
        if self.layout == "opening":
            reveal = smooth((template_frame - 9) / 28)
            self.paste(scene, self.title, 96, 178 + 15 * (1 - reveal), reveal)
        picture = scene if self.subpixel else cv2.cvtColor(np.asarray(scene), cv2.COLOR_RGBA2BGR)
        if self.layout in ("opening", "veil", "botanical", "ceremony"):
            dust = footage("Bokeh_02.mov")
            offset = {"opening": 24, "veil": 63, "botanical": 91, "ceremony": 110}[self.layout]
            picture = screen(picture, interpolate_footage(dust, template_frame + offset),
                             .19 if self.layout != "ceremony" else .26)
        return picture


def blur(frame, amount):
    mini = cv2.resize(frame, (480, 270), interpolation=cv2.INTER_AREA)
    blurred = cv2.GaussianBlur(mini, (0, 0), max(.4, amount * 3.8))
    return cv2.resize(blurred, PHOTO_SIZE, interpolation=cv2.INTER_LINEAR)


@lru_cache(maxsize=1)
def iris_distance():
    x = (np.arange(WIDTH, dtype=np.float32)[None, :] - WIDTH * .42) / WIDTH
    y = (np.arange(HEIGHT, dtype=np.float32)[:, None] - HEIGHT * .54) / (HEIGHT * 1.23)
    return np.sqrt(x * x + y * y)


def change(previous, upcoming, style, amount, alternate=False, interpolate=False):
    if style == "iris":
        radius = smooth(amount) * .89 - .09 if interpolate else smooth(amount) * .88 - .08
        weight = np.clip((radius + .09 - iris_distance()) / .12, 0, 1)[:, :, None]
        new = cv2.multiply(upcoming, np.broadcast_to(weight, upcoming.shape), dtype=cv2.CV_8U)
        old = cv2.multiply(previous, np.broadcast_to(1 - weight, previous.shape), dtype=cv2.CV_8U)
        return cv2.add(old, new)
    if style == "lens":
        phase = smooth(amount)
        mixed = cv2.addWeighted(previous, 1 - phase, upcoming, phase, 0)
        strength = 4 * phase * (1 - phase)
        return cv2.addWeighted(mixed, 1 - strength * .61, blur(mixed, strength), strength * .61, 0)
    if style == "flare" or (style == "wipe_right" and alternate):
        progress = smooth(amount)
        mixed = cv2.addWeighted(previous, 1 - progress, upcoming, progress, 0)
        clip = footage("TR_02_2.mov" if style == "flare" else "TR_03_2.mov")
        position = amount * (len(clip) - 1)
        overlay = interpolate_footage(clip, position) if interpolate else clip[round(position)]
        return screen(mixed, overlay, 4 * progress * (1 - progress) * .42)
    return transition_picture(previous, upcoming, style, amount)
