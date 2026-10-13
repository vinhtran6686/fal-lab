#!/usr/bin/env python3
"""Measure a packed animation as a motion, not as separate drawings (see .claude/skills/fal-image/animation.md §8).

Usage: python scripts/motion_check.py out/enemies/bandit/walk_side/v05 [--loop | --once]

Reads <version dir>/frames/@2x/*.png in order and reports, per frame:
  height  body height (px @2x): the bob curve; a walk should dip on loading and peak on push-off
  ground  lowest opaque row: should stay on the baseline for grounded motions
  torso_x horizontal centre of the upper body vs the pivot: drift = accidental whole-sprite sliding
  change  how much the frame differs from the previous one (0 = identical)
and flags frozen frames (no change), spikes (a transition much bigger than the others) and,
for cyclic animations (--loop, the default unless meta says loop=false), the last->first jump.
Writes motioncheck.txt and transitions.png (every transition as an onion pair: previous frame
in cyan under the current one, the N->1 pair included). Static numbers cannot judge timing or
foot slide at the real speed: watch it moving in Motion Lab for that.
"""
import argparse, json, pathlib, statistics, sys
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

ALPHA = 24


def pixels(img: Image.Image):
    return img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata()


def measure(im: Image.Image):
    a = im.getchannel("A").point(lambda v: 255 if v > ALPHA else 0)
    box = a.getbbox()
    if not box:
        return None
    x0, y0, x1, y1 = box
    upper = a.crop((0, y0, im.width, y0 + (y1 - y0) // 2))   # head + torso: limbs swing, this should not
    hist_x = [sum(1 for v in pixels(upper.crop((x, 0, x + 1, upper.height))) if v) for x in range(im.width)]
    mass = sum(hist_x) or 1
    cx = sum(x * n for x, n in enumerate(hist_x)) / mass
    return {"height": y1 - y0, "ground": y1, "torso_x": cx - im.width / 2}


def change(a: Image.Image, b: Image.Image) -> float:
    small = (a.width // 4, a.height // 4)
    ga = Image.alpha_composite(Image.new("RGBA", a.size, (128, 128, 128, 255)), a).convert("L").resize(small)
    gb = Image.alpha_composite(Image.new("RGBA", b.size, (128, 128, 128, 255)), b).convert("L").resize(small)
    diff = ImageChops.difference(ga, gb)
    return sum(pixels(diff)) / (small[0] * small[1])


def onion(prev: Image.Image, cur: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", cur.size, (232, 224, 205, 255))
    tint = Image.new("RGBA", prev.size, (40, 170, 230, 255))
    ghost = Image.composite(tint, Image.new("RGBA", prev.size, (0, 0, 0, 0)), prev.getchannel("A"))
    ghost.putalpha(prev.getchannel("A").point(lambda v: v * 110 // 255))
    out = Image.alpha_composite(bg, ghost)
    out = Image.alpha_composite(out, cur)
    d = ImageDraw.Draw(out)
    d.line([(0, int(cur.height * 0.88)), (cur.width, int(cur.height * 0.88))], fill=(200, 60, 50, 255), width=1)
    d.line([(cur.width // 2, 0), (cur.width // 2, cur.height)], fill=(200, 60, 50, 120), width=1)
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("version_dir")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--loop", action="store_true", help="cyclic animation: check the last->first transition")
    g.add_argument("--once", action="store_true", help="one-shot animation: no last->first check")
    a = p.parse_args()
    vdir = pathlib.Path(a.version_dir)
    files = sorted((vdir / "frames" / "@2x").glob("*.png"))
    if len(files) < 2:
        sys.exit(f"need at least 2 frames in {vdir / 'frames' / '@2x'}")
    loop = a.loop
    if not a.loop and not a.once:   # read it from the asset's meta.json when possible
        loop = True
        meta = vdir.parent.parent / "meta.json"
        if meta.exists():
            st = json.loads(meta.read_text(encoding="utf-8"))["states"].get(vdir.parent.name)
            if st is not None:
                loop = st.get("loop", True)

    frames = [Image.open(f).convert("RGBA") for f in files]
    m = [measure(f) for f in frames]
    if any(x is None for x in m):
        sys.exit("an empty frame was found")
    n = len(frames)
    pairs = [(i, i + 1) for i in range(n - 1)] + ([(n - 1, 0)] if loop else [])
    ch = {pair: change(frames[pair[0]], frames[pair[1]]) for pair in pairs}
    med = statistics.median(ch.values())
    heights = [x["height"] for x in m]

    lines = [f"{vdir}  frames={n}  {'cyclic' if loop else 'one-shot'}",
             f"{'F':>3} {'height':>7} {'ground':>7} {'torso_x':>8} {'change_in':>10}"]
    for i, x in enumerate(m):
        into = ch.get((i - 1, i)) if i else ch.get((n - 1, 0))
        lines.append(f"{i + 1:>3} {x['height']:>7} {x['ground']:>7} {x['torso_x']:>8.1f} "
                     f"{'' if into is None else f'{into:10.1f}'}")
    flags = []
    for (i, j), v in ch.items():
        tag = f"{i + 1}->{j + 1}"
        if v < max(0.6, med * 0.15):
            if not loop and j == n - 1:
                lines_note = f"HOLD    {tag}: final pose held (intended for a one-shot)"
                flags.append(lines_note)
                continue
            flags.append(f"FROZEN  {tag}: almost no change ({v:.1f}); a held pose reads as a stutter")
        elif v > med * 2.2 and v > 4:
            flags.append(f"SPIKE   {tag}: change {v:.1f} vs median {med:.1f}; check pose continuity")
    tx = [x["torso_x"] for x in m]
    if loop and max(tx) - min(tx) > frames[0].width * 0.06:
        flags.append(f"DRIFT   torso x moves {max(tx) - min(tx):.0f}px across the cycle; pack with --align torso "
                     f"or check for whole-sprite sliding")
    gr = [x["ground"] for x in m]
    if loop and max(gr) - min(gr) > 3:
        flags.append(f"GROUND  lowest pixel varies {max(gr) - min(gr)}px; fine for jumps/deaths, not for planted feet")
    bob = max(heights) - min(heights)
    lines.append(f"bob (height range): {bob}px = {100 * bob / max(heights):.1f}% of the body; "
                 f"lowest F{heights.index(min(heights)) + 1}, highest F{heights.index(max(heights)) + 1}")
    if loop:
        lines.append(f"loop 8->1 style check: {n}->1 change {ch[(n - 1, 0)]:.1f} vs median {med:.1f}")
    lines += ["flags:"] + (flags or ["  none (static checks only: timing and foot slide are unverified until seen moving)"])
    report = "\n".join(lines)
    (vdir / "motioncheck.txt").write_text(report + "\n", encoding="utf-8")
    print(report)

    cells = [onion(frames[i], frames[j]) for i, j in pairs]
    w, h, pad, label, per = cells[0].width, cells[0].height, 8, 28, 4
    rows = (len(cells) + per - 1) // per
    sheet = Image.new("RGB", (per * (w + pad) + pad, rows * (h + label + pad) + pad), (40, 44, 52))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    for k, (cell, (i, j)) in enumerate(zip(cells, pairs)):
        x, y = pad + (k % per) * (w + pad), pad + (k // per) * (h + label + pad)
        sheet.paste(cell.convert("RGB"), (x, y + label))
        d.text((x + 4, y + 2), f"{i + 1} -> {j + 1}", fill=(255, 255, 255), font=font)
    sheet.save(vdir / "transitions.png")
    print(vdir / "transitions.png")


if __name__ == "__main__":
    main()
