#!/usr/bin/env python3
"""Review sheet for ONE fxkit layer kind (or one effect of a family module), drawn alone in several seeds, directions, sizes
and palettes: the way to judge a kind before it goes into effects. 0 USD.

  python lib-fx/_tools/fxkit_sheet.py spikes                         a kind with its default parameters
  python lib-fx/_tools/fxkit_sheet.py spikes n=11 length=90 arc=-70,70   parameters: key=value (numbers, a,b tuples, true/false, text)
  python lib-fx/_tools/fxkit_sheet.py puffs --life 0,0.1,0.1,0.6 --step 2 --pal fire
  python lib-fx/_tools/fxkit_sheet.py impact/burst/heavy             an effect of the library instead of a kind
Rows: seed 0 aimed right; seed 1 aimed right; seed 2 aimed up-left at s = 0.7 in another palette; seed 3 aimed left.
Columns: the frames (every other one when there are more than 12). A yellow dot marks a, a cyan dot marks b.
Writes lib-fx/_gallery/kinds/<name>.png and .gif (git-ignored), prints the path and the fxcheck line of row 1.
"""
import argparse, importlib.util, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "_core" / "formulas" / "draw")); sys.path.insert(0, str(HERE / "_tools"))
from PIL import Image, ImageDraw
import fxcore, fxcheck
from fxkit import Effect, Layer, Life, render, KINDS

BG = (34, 38, 36)


def val(v):
    if v.lower() in ("true", "false"): return v.lower() == "true"
    if "," in v: return tuple(val(x) for x in v.split(","))
    try: return int(v)
    except ValueError:
        try: return float(v)
        except ValueError: return v


def load_effect(path):
    fam, _, name = path.rpartition("/")
    py = HERE / fam / (fam.rsplit("/", 1)[-1] + ".py")
    spec = importlib.util.spec_from_file_location("fx_" + fam.replace("/", "_"), py); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.EFFECTS[name]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name"); ap.add_argument("params", nargs="*")
    ap.add_argument("--life", default="0,0.066,0.034,0.3"); ap.add_argument("--step", type=int, default=1)
    ap.add_argument("--pal", default="sun"); ap.add_argument("--pal2", default="ice"); ap.add_argument("--z", default="front")
    ap.add_argument("--at", default="a"); ap.add_argument("--reach", type=float, default=140); ap.add_argument("--extent", type=float, default=240)
    a = ap.parse_args()
    if a.name in KINDS:
        st, at, ho, re = (float(x) for x in a.life.split(","))
        eff = Effect(a.name, [Layer(a.name, "primary", Life(st, at, ho, re, a.step), z=a.z, at=a.at, **dict(p.split("=", 1) and (p.split("=", 1)[0], val(p.split("=", 1)[1])) for p in a.params))],
                     reach=a.reach, extent=a.extent, pal=a.pal)
    else:
        eff = load_effect(a.name)
        for p in eff.lint(): print("lint:", p)
    R = eff.reach
    rows = [dict(seed=0), dict(seed=1), dict(seed=2, b=(-0.6 * R * 0.7, -0.8 * R * 0.7), s=0.7, pal=a.pal2), dict(seed=3, b=(-R, 0))]
    outs = [render(eff, a=(0, 0), b=r.get("b"), pal=r.get("pal"), s=r.get("s", 1.0), seed=r["seed"]) for r in rows]
    n = max(len(o["frames"]) for o in outs); cols = list(range(0, n, 2 if n > 12 else 1))
    cw, ch = max(o["size"][0] for o in outs), [o["size"][1] for o in outs]

    def cell(o, i):
        c = Image.new("RGBA", (cw, o["size"][1]), BG + (255,))
        if i < len(o["frames"]): c.alpha_composite(o["frames"][i], ((cw - o["size"][0]) // 2, 0))
        d = ImageDraw.Draw(c); ox = (cw - o["size"][0]) // 2
        for (x, y), col in ((o["anchor"], (255, 220, 60)), (o["target"], (80, 220, 255))):
            d.ellipse([ox + x - 2, y - 2, ox + x + 2, y + 2], outline=col)
        return c.convert("RGB")

    sheet = Image.new("RGB", (cw * len(cols), sum(ch) + 18), BG); d = ImageDraw.Draw(sheet); f = fxcore.font(13)
    for c, i in enumerate(cols): d.text((c * cw + 4, 2), f"{i + 1:02d}" + (" HIT" if i + 1 == outs[0]["hit_frame"] else ""), fill=(150, 160, 152), font=f)
    y = 18
    for o in outs:
        for c, i in enumerate(cols): sheet.paste(cell(o, i), (c * cw, y))
        y += o["size"][1]
    out = HERE / "_gallery" / "kinds"; out.mkdir(parents=True, exist_ok=True)
    stem = a.name.replace("/", "-")
    k = min(1.0, 2400 / sheet.width)
    (sheet if k == 1 else sheet.resize((round(sheet.width * k), round(sheet.height * k)), Image.LANCZOS)).save(out / f"{stem}.png")
    anim = []
    for i in range(n):
        g = Image.new("RGB", (cw * 2, max(ch[0], ch[1]) + max(ch[2], ch[3])), BG)
        for j, o in enumerate(outs): g.paste(cell(o, i), ((j % 2) * cw, (j // 2) * max(ch[0], ch[1])))
        anim.append(g)
    fxcore.save_gif(anim, out / f"{stem}.gif", 30, 600)
    print((out / f"{stem}.png").relative_to(HERE.parent).as_posix(), f"({len(cols)} of {n} frames per row)")
    print(fxcheck.line(a.name, fxcheck.check(outs[0]["frames"], eff.tags, outs[0]["anchor"])))


if __name__ == "__main__":
    main()
