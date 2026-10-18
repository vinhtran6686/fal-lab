#!/usr/bin/env python3
"""Collect the final frames of every asset into out/playtest/ for the browser playtest.

Usage: python scripts/build_playtest.py [--out out/playtest]

Reads out/{enemies,bosses,allies,heroes}/*/meta.json (the final version of each sheet), copies the @2x frames,
icons, the valley map and the footman soldier when present in out/ (both optional), writes manifest.json and copies
tools/playtest/index.html next to them. Publish out/playtest/index.html with all files
in that folder as an Artifact to watch the animations in a game-like scene, and
out/playtest/motion.html (same files) as a second Artifact: the Motion Lab for tuning
fps and move speed frame by frame.
"""
import argparse, json, pathlib, re, shutil, sys
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent


def first(pattern: str) -> pathlib.Path | None:
    hits = sorted((ROOT / "out").glob(pattern))
    return hits[0] if hits else None


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default=str(ROOT / "out" / "playtest"))
    a = p.parse_args()
    out = pathlib.Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    (out / "assets").mkdir(parents=True)

    man = {"enemies": {}}
    # every character class (fal-image/format.md §7); the page walks them all along the road
    metas = [m for folder in ("enemies", "bosses", "allies", "heroes") for m in sorted((ROOT / "out" / folder).glob("*/meta.json"))]
    for meta_path in metas:
        asset = meta_path.parent
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        eid = meta["id"]
        brief = asset / "brief.md"
        title = re.search(r"^# Brief: \w+ `(.+?)`", brief.read_text(encoding="utf-8"), re.M) if brief.exists() else None
        anims, icon = {}, False
        for key, st in meta["states"].items():
            src = asset / (st.get("dir") or pathlib.Path(st["files"]).parents[2].as_posix()) / "frames" / "@2x"
            dst = out / "assets" / eid / key
            dst.mkdir(parents=True)
            names = sorted(src.glob("*.png"))
            for i, f in enumerate(names, 1):
                shutil.copy(f, dst / f"{i:02d}.png")
            if key == "icon":
                icon = True
                continue
            anims[key] = {"frames": st["frames"], "fps": st["fps"], "loop": st["loop"],
                          "hit": st.get("hit_frame"), "version": st["version"],
                          "cell": [c * 2 for c in st.get("cell", meta["cell"])]}
        man["enemies"][eid] = {"name": title.group(1) if title else eid, "cell": meta["cell"][0] * 2,
                               "pivot": meta["pivot"], "move_speed": meta.get("move_speed"),
                               "mirrored": meta.get("mirrored", {}), "icon": icon, "anims": anims}
    if not man["enemies"]:
        sys.exit("no packed characters found in out/enemies, bosses, allies or heroes")

    # optional scenery: without them the page draws a plain field with the road and a placeholder soldier
    map_img, foot_img = first("map_valley-*.jpg"), first("footman-*.png")
    if map_img:
        Image.open(map_img).convert("RGB").save(out / "assets" / "map.jpg", quality=88)
    if foot_img:
        foot = Image.open(foot_img).convert("RGBA")
        foot = foot.crop(foot.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox())
        foot.thumbnail((160, 160))
        foot.save(out / "assets" / "footman.png")
    man["map"], man["footman"] = bool(map_img), bool(foot_img)
    (out / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy(ROOT / "tools" / "playtest" / "index.html", out / "index.html")
    shutil.copy(ROOT / "tools" / "playtest" / "motion.html", out / "motion.html")   # Motion Lab, same assets
    files = sorted(f.relative_to(out).as_posix() for f in out.rglob("*") if f.is_file() and f.suffix != ".html")
    print(f"playtest ready: {out / 'index.html'} ({len(man['enemies'])} enemies, {len(files)} files)")


if __name__ == "__main__":
    main()
