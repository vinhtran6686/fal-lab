#!/usr/bin/env python3
"""Turn an approved still (a master or a view reference made with gen_image.py) into the
master.json that the video-sprite skill animates (.claude/skills/video-sprite/SKILL.md).

Usage:
  python scripts/make_master.py out/enemies/bandit/design/master_v01.png
                                --out-dir out/enemies/bandit/.work/masters/side
                                --name bandit --facing right --recap "<{design} from brief.md>"
                                [--class mob] [--height 0.56] [--canvas 1024]

What it does:
  1. keys out the flat magenta background (same un-mixing as sprite_pack.py)
  2. crops the figure and places it on a square transparent canvas: body height = --height of the
     canvas, feet on the pivot line (12% above the bottom, as in sprite_pack.py), centered, with room
     above the head for raised weapons
  3. writes master.png and master.json (schema generate2dsprite.master.v1: identity recap, facing,
     class, key colour, style, framing, sha256)
Facing: right (the side master: three-quarter view facing right), left, front (walk down), back (walk up), down-right (3/4 front),
up-right (3/4 back). One master per view; the left diagonals are mirrors and are never generated.
Prints the master.json path.
"""
import argparse, hashlib, json, pathlib, sys
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sprite_pack import key_out, has_alpha, bbox, BASELINE  # noqa: E402

STYLE = ("flat vector 2D cartoon game art: thick uniform near-black outlines, flat colour fills with 2-3 tone "
         "hard-edged cel shading, muted earthy palette, chunky readable shapes, high top-down camera, "
         "light from the top-left")
FACINGS = ("right", "left", "front", "back", "down-right", "up-right")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("image")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--facing", required=True, choices=FACINGS)
    p.add_argument("--recap", required=True, help="the long identity phrase ({design} of brief.md)")
    p.add_argument("--class", dest="klass", default="mob", help="mob (enemies), hero, boss, flying ...")
    p.add_argument("--style", default=STYLE)
    p.add_argument("--height", type=float, default=0.56, help="body height / canvas (default 0.56)")
    p.add_argument("--canvas", type=int, default=1024)
    a = p.parse_args()

    out = pathlib.Path(a.out_dir)
    if out.exists() and any(out.iterdir()):
        sys.exit(f"{out} is not empty; use a new folder (one master per view)")
    img = Image.open(a.image).convert("RGBA")
    if not has_alpha(img):
        img = key_out(img)
    box = bbox(img)
    if not box:
        sys.exit("no figure found after keying the background")
    fig = img.crop(box)
    s = a.canvas * a.height / fig.height
    fig = fig.resize((max(1, round(fig.width * s)), max(1, round(fig.height * s))), Image.LANCZOS)
    if fig.width > a.canvas * 0.9:
        sys.exit(f"the figure is {fig.width}px wide at this height; lower --height")
    feet = round(a.canvas * (1 - BASELINE))
    canvas = Image.new("RGBA", (a.canvas, a.canvas), (0, 0, 0, 0))
    canvas.paste(fig, ((a.canvas - fig.width) // 2, feet - fig.height))
    out.mkdir(parents=True, exist_ok=True)
    png = out / "master.png"
    canvas.save(png)
    digest = hashlib.sha256(png.read_bytes()).hexdigest()
    doc = {"schema": "generate2dsprite.master.v1", "name": a.name, "identity_recap": " ".join(a.recap.split()),
           "facing": a.facing, "finish": "hd", "class": a.klass, "key": "magenta", "style": a.style,
           "framing": {"canvas": [a.canvas, a.canvas], "subject_height_px": fig.height,
                       "top_margin_px": feet - fig.height},
           "files": {"master": {"path": "master.png", "sha256": digest}},
           "source": {"image": pathlib.Path(a.image).resolve().as_posix()}}
    (out / "master.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out / "master.json")


if __name__ == "__main__":
    main()
