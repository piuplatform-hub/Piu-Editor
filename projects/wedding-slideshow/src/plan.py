import argparse
from collections import Counter
from random import Random

from media import AUDIO_PLAN, FPS, PROJECT, SRC, TIMELINE, read_json, write_json


PACE = (17, 16, 13, 17, 18, 14, 18, 17, 18, 13)
THEMES = (
    ("studio", "studio", "greenery", "veil", "studio", "greenery"),
    ("studio", "solo", "greenery", "veil", "greenery"),
    ("table", "greenery", "table", "table", "veil"),
    ("red_solo", "red", "red", "red", "red"),
    ("veil", "studio", "veil", "greenery", "studio"),
    ("table", "greenery", "table", "studio"),
    ("veil", "studio", "table", "greenery"),
    ("solo", "veil", "studio", "greenery", "table"),
    ("studio", "table", "red", "greenery", "veil", "red"),
    ("red", "table", "red", "greenery", "table", "red"),
)
LAYOUTS = ("trio", "pair", "feature", "pair", "trio", "spread", "trio")
MOTIONS = ("approach", "drift_left", "recede", "drift_right", "lift", "settle")
COUNTS = {"wide": 1, "pair": 2, "spread": 2, "trio": 3, "feature": 3}
BRIDE_SOLOS = ["A044", "A045", "PAD_4399", "PAD_4724", "PAD_4730"]
GROOM_SOLOS = ["A042", "A043", "A067", "PAD_4826", "PAD_4832", "PAD_4841"]
FIXED = {
    (0, 0): ("wide", ["A063"], "Từ hôm nay"),
    (0, 1): ("trio", ["A044", "A050", "A042"], ""),
    (5, 0): ("wide", ["PAD_4552"], ""),
    (9, -1): ("trio", ["A066", "A054", "A065"], "Cảm ơn"),
}


def select_photo(pool, photos, placed, scene, style, used, previous, recent, rng):
    phash = {key: int(photos[key]["phash"], 16) for key in pool + placed + recent}

    def distance(key, group):
        return min(((phash[key] ^ phash[other]).bit_count() for other in group), default=64)

    choices = [key for key in pool if key not in placed and key not in recent
               and photos[key]["height"] > photos[key]["width"]]
    if not choices:
        raise ValueError("Photo pool is too small for this part of the timeline")
    return min(choices, key=lambda key: (distance(key, placed) < 13,
                                        distance(key, recent[:6]) < 9,
                                        previous.get(key, (None, 0))[0] == style,
                                        used[key],
                                        previous.get(key, (None, -1000))[1] > scene - 9,
                                        rng.random()))


def chapter_parts(frames, count):
    weights = (1.04, .86, 1.07, 1.15, .94, 1.02, .92)
    pacing = [weights[index % len(weights)] for index in range(count)]
    balance = sum(pacing)
    edges = [round(frames * sum(pacing[:index]) / balance) for index in range(count)]
    return list(zip(edges, edges[1:] + [frames]))


def retime(audio):
    arrangement = read_json(TIMELINE)
    chapters = arrangement["chapters"]
    if [chapter["title"] for chapter in chapters] != [track["title"] for track in audio["tracks"]]:
        raise ValueError("Retiming requires the same playlist and order")
    for chapter, track in zip(chapters, audio["tracks"]):
        chapter["start"], chapter["end"] = track["startFrame"], track["nextFrame"]
        scenes = chapter["scenes"]
        parts = chapter_parts(chapter["end"] - chapter["start"], len(scenes))
        for scene, (first, end) in zip(scenes, parts):
            scene["start"], scene["frames"] = chapter["start"] + first, end - first
    arrangement["totalFrames"] = audio["totalFrames"]
    write_json(TIMELINE, arrangement)
    print(f"Retimed {sum(len(chapter['scenes']) for chapter in chapters)} slides to {audio['totalFrames'] / FPS:.2f}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--retime", action="store_true", help="Keep layouts and image choices when applying updated music timing.")
    args = parser.parse_args()
    audio = read_json(AUDIO_PLAN)
    if args.retime:
        retime(audio)
        return
    catalog = {row["id"]: row for row in read_json(PROJECT / "working/photo-catalog.json")}
    pools = read_json(SRC / "photo-pools.json")
    if len(audio["tracks"]) != len(PACE):
        raise ValueError("Playlist and picture chapter count differ")
    rng = Random(20261125)
    use_count = Counter()
    previous = {}
    recent = []
    chapters = []
    ordered_assets = {}
    scene_id = 0

    for chapter, (track, pace, themes) in enumerate(zip(audio["tracks"], PACE, THEMES)):
        chapter_in, chapter_out = track["startFrame"], track["nextFrame"]
        count = max(2, round((chapter_out - chapter_in) / FPS / pace))
        parts = chapter_parts(chapter_out - chapter_in, count)
        scenes = []
        for local, (first, end) in enumerate(parts):
            scene_id += 1
            theme = themes[local % len(themes)]
            motion = MOTIONS[(scene_id + chapter * 2) % len(MOTIONS)]
            fixed = FIXED.get((chapter, local))
            if local + 1 == len(parts):
                fixed = FIXED.get((chapter, -1), fixed)
            if fixed:
                layout, picked, title = fixed
            else:
                layout = LAYOUTS[(local + chapter * 3) % len(LAYOUTS)]
                style = (layout, motion)
                count = COUNTS[layout]
                if theme == "solo":
                    middle = [pools["studio"]] if count == 3 else []
                    pane_pools = [BRIDE_SOLOS, *middle, GROOM_SOLOS]
                elif theme == "red_solo":
                    pane_pools = [pools["red_solo"] + pools["red"]] * count
                else:
                    pane_pools = [pools[theme]] * count
                picked = []
                for pool in pane_pools:
                    picked.append(select_photo(pool, catalog, picked, scene_id, style, use_count, previous, recent, rng))
                title = ""
            palette = "wine" if theme.startswith("red") else "ivory"
            if title:
                palette = "ivory"
            if chapter == 3 and local == 0:
                transition = "wipe_right"
            elif local % 5 == 2:
                transition = "wipe_left" if scene_id % 2 else "wipe_right"
            else:
                transition = "dissolve"
            scenes.append({"id": scene_id, "start": chapter_in + first, "frames": end - first, "theme": theme,
                           "layout": layout, "photos": picked, "motion": motion, "transition": transition,
                           "palette": palette, "title": title})
            style = (layout, motion)
            for key in picked:
                use_count[key] += 1
                previous[key] = (style, scene_id)
                row = catalog[key]
                ordered_assets[key] = {
                    "path": f"Source/inbox/wedding-slideshow/images/{row['group']}/{row['file']}",
                    "original": row["source"],
                    "group": row["group"],
                }
            recent = (picked + recent)[:13]
        chapters.append({"index": chapter + 1, "title": track["title"], "artist": track["artist"],
                         "start": chapter_in, "end": chapter_out, "scenes": scenes})

    write_json(TIMELINE, {"fps": FPS, "totalFrames": audio["totalFrames"], "chapters": chapters, "photos": ordered_assets})
    print(f"{len(chapters)} chapters, {scene_id} scenes, {len(use_count)} distinct photo files, "
          f"{sum(use_count.values())} placements, {audio['totalFrames'] / FPS:.2f} seconds")
    print(dict(Counter(asset["group"] for asset in ordered_assets.values())))


if __name__ == "__main__":
    main()
