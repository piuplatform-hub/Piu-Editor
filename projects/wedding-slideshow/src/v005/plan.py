from bisect import bisect_left, bisect_right
from collections import Counter
from random import Random

from PIL import ImageFont

from prepare import AUDIO_PLAN, FPS, PLAN, PUBLIC, STORY, WORK, read_json, write_json


def ids(numbers):
    return [f"B{number:02d}" for number in numbers]


GROUPS = {
    "studio": ids([23, 24, 28, 30, 32, 34, 35, 39, 41, 44, 45, 49, 51, 52, 53, 54, 55]),
    "flowers": ids([1, 2, 25, 26, 27, 29, 31, 33, 36, 42, 46, 50]),
    "veil": ids([21, 23, 28, 30, 44, 50, 51, 52, 53, 54, 55]),
    "table": ids([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 38, 48]),
    "red": ids([16, 17, 18, 19, 20, 22, 40, 43]),
    "close": ids([12, 13, 21, 10, 52, 46]),
}
POSES = [ids(group) for group in ([1, 2, 33, 36], [5, 38], [6, 7], [8, 9, 10], [12, 13],
                                 [14, 48], [17, 18, 43], [19, 40], [20, 22], [32, 39],
                                 [41, 49], [23, 28], [54, 55])]
FAMILY = {key: i for i, group in enumerate(POSES) for key in group}
PHOTO_COUNTS = {"triptych": 3, "duet": 2, "arch": 2, "silk": 1, "gallery": 2, "folio": 2}
LAYOUTS = ("duet", "triptych", "arch", "duet", "gallery", "folio", "silk", "triptych", "duet")
MOTIONS = ("driftRight", "push", "driftLeft", "recede", "lift", "floatRight", "floatLeft")
TRANSITIONS = {"triptych": "page", "arch": "iris", "silk": "lens", "folio": "page",
               "memoryPair": "iris", "signature": "lens"}


def cut_grid(length, pace, marks, opening):
    count = max(3, round(length / FPS / pace))
    weights = [1.04, .86, 1.12, .9, 1.08, .98, 1.10, .91]
    spans = [weights[index % len(weights)] for index in range(count)]
    if opening:
        spans[0] = 1.08
    total = sum(spans)
    starts, targets = [0], [0]
    onsets = [mark[0] for mark in marks]
    for index in range(1, count):
        target = round(length * sum(spans[:index]) / total)
        low, high = bisect_left(onsets, target - 23), bisect_right(onsets, target + 23)
        candidates = marks[low:high]
        strength = max((value for _, value in candidates), default=1.0)
        frame = min(candidates, key=lambda pair: .62 * abs(pair[0] - target) / 23 - .38 * pair[1] / strength)[0] if candidates else target
        starts.append(frame)
        targets.append(target)
    return [(start, stop - start, target) for start, stop, target in zip(starts, starts[1:] + [length], targets, strict=True)]


def pick(choices, count, layout, used, history, prior, upcoming, index, rng):
    placed = []
    for _ in range(count):
        allowed = [key for key in choices if key not in placed and key not in prior and key not in upcoming]
        if not allowed:
            allowed = [key for key in choices if key not in placed and key not in prior]
        if not allowed:
            raise ValueError(f"Too few photos for {layout}: {choices}")
        families = [FAMILY[key] for key in placed + prior if key in FAMILY]

        def score(key):
            last, old_layout = history.get(key, (-200, ""))
            return (FAMILY.get(key, -1) in families, index - last < 5, old_layout == layout,
                    used[key], max(0, last - index + 11), rng.random())

        placed.append(min(allowed, key=score))
    return placed


def font_size(text, proposed, italic, width):
    suffix = "-Italic.ttf" if italic else ".ttf"
    face = ImageFont.truetype(str(PUBLIC / "fonts" / ("CormorantGaramond" + suffix)), proposed)
    return min(proposed, int(proposed * width / face.getlength(text)))


def lettering(cue, story, scene_id, duration, layout):
    if not cue:
        return None
    names = cue.get("names", False)
    lines = [story["groom"], "& " + story["bride"]] if names else cue["lines"]
    width = 560 if layout == "signature" else 660 if layout == "memory" else 520
    sizes = (115, 116) if names else (112, 104) if layout == "memory" else (94, 89)
    return {
        "id": f"{scene_id:03d}", "names": names, "eyebrow": cue.get("eyebrow"),
        "lines": [{"text": line, "size": font_size(line, sizes[i], i == 1, width), "italic": i == 1}
                  for i, line in enumerate(lines)],
        "in": 32 if scene_id == 1 else 48, "out": duration - 72,
        "hold": cue.get("hold", False), "date": cue.get("date", False),
    }


def plan():
    story, audio = read_json(STORY), read_json(AUDIO_PLAN)
    marks = read_json(WORK / "rhythm-marks.json")
    assets = read_json(WORK / "picture-inputs.json")
    rng = Random(280526)
    chapters, used, history = [], Counter(), {}
    prior = []
    number = 0
    for section, track, beats in zip(story["tracks"], audio["tracks"], marks, strict=True):
        index = track["index"]
        grid = cut_grid(track["end"] - track["start"], section["pace"], beats, index == 1)
        cues = {min(range(len(grid)), key=lambda i: abs(grid[i][0] - cue["at"] * (track["end"] - track["start"]))): cue
                for cue in section["cues"]}
        if len(cues) != len(section["cues"]):
            raise ValueError(f"Overlapping story cues in {track['title']}")
        scenes = []
        for local, (start, length, target) in enumerate(grid):
            number += 1
            theme = section["groups"][(local + local // 5) % len(section["groups"])]
            palette = "wine" if theme == "red" else section["palette"]
            if section["palette"] == "wine" and theme != "red":
                palette = "ivory"
            cue = cues.get(local)
            if cue:
                layout = cue.get("layout", "letter")
                pool = GROUPS["red" if section["palette"] == "wine" else theme]
                theme = "red" if section["palette"] == "wine" else theme
                palette = section["palette"]
                fixed = cue.get("photos")
            else:
                layout = LAYOUTS[(local + 3 * index) % len(LAYOUTS)]
                pool = GROUPS[theme]
                if layout == "silk":
                    pool = [key for key in GROUPS["close"] if key in pool]
                    if not set(pool) - set(prior):
                        layout, pool = "gallery", GROUPS[theme]
                fixed = None
            upcoming = [key for offset in (1, 2) for key in cues.get(local + offset, {}).get("photos", [])]
            chosen = fixed or pick(pool, 2 if cue else PHOTO_COUNTS[layout], layout, used, history, prior, upcoming, number, rng)
            if not set(chosen) <= assets.keys() or len(chosen) != len(set(chosen)):
                raise ValueError(f"Invalid photos in scene {number}")
            transition = (cue or {}).get("transition", TRANSITIONS.get(layout, "dissolve"))
            if local == 0 and transition != "flare":
                transition = "iris" if layout in ("memory", "memoryPair") else "dissolve"
            scenes.append({"id": number, "start": start + track["start"], "frames": length, "chapter": index,
                           "target": target + track["start"], "layout": layout, "palette": palette, "theme": theme,
                           "photos": chosen, "motion": MOTIONS[(number + index) % len(MOTIONS)],
                           "mirror": number % 2 == 0 and not cue, "transition": transition,
                           "text": lettering(cue, story, number, length, layout)})
            for key in chosen:
                used[key] += 1
                history[key] = (number, layout)
            prior = chosen
        chapters.append({**track, "chapter": section["chapter"], "scenes": scenes})
    if len(used) != len(assets):
        raise ValueError(f"Photos missing from timeline: {set(assets)-set(used)}")
    write_json(PLAN, {"fps": FPS, "totalFrames": audio["totalFrames"], "soundtrackSha256": audio["soundtrackSha256"],
                      "solarDate": story["solarDate"], "lunarDate": story["lunarDate"], "assets": assets, "chapters": chapters})
    print(f"{len(chapters)} chapters · {number} scenes · {sum(used.values())} photo placements · {len(used)} distinct photos", flush=True)


if __name__ == "__main__":
    plan()
