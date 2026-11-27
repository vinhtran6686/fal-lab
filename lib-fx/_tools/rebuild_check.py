"""Compare a vector rebuild with its reference on what the eye reads: area and stroke width of the BRIGHT part, and of the
DARK part (inverse flash frames). IoU of the layer masks misses a stroke traced too thick (a thick stroke always covers a
thin one: lightning R2 scored IoU 0.999 with strokes 3x too wide), so this check measures the two images directly.

    python lib-fx/_tools/rebuild_check.py PROFILE [--frames 0-19] [--variants a,b] [--bright 170] [--dark 40]

Per frame and variant: area_ratio = rebuilt / reference pixel count with luminance > --bright (strokes and cores, not
glow); width_ratio = the same for mean stroke width (area / skeleton length); dark_ratio = area with luminance < --dark
where the reference background is not that dark (black inverse shapes). Pass: area and width ratios in 0.8-1.25.
Writes rebuild_check.json next to the rebuild (lib-fx/_study/<name>/vector/)."""
import argparse
import json
import pathlib
import sys

import numpy as np
from PIL import Image
from skimage.morphology import skeletonize

HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "_core" / "formulas"))
from vector import Profile, measure  # noqa: E402


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def width(m):
    sk = skeletonize(m).sum()
    return float(m.sum() / sk) if sk else 0.0


def rng(s):
    if not s:
        return None
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("profile")
    ap.add_argument("--frames")
    ap.add_argument("--variants")
    ap.add_argument("--bright", type=float, default=170)
    ap.add_argument("--dark", type=float, default=40)
    a = ap.parse_args()
    p = pathlib.Path(a.profile)
    if not p.exists():
        p = HERE / "_core/formulas/vector/profiles" / f"{a.profile}.json"
    prof = Profile(p)
    frames = rng(a.frames) or prof.frames()
    out = {}
    for v in (a.variants.split(",") if a.variants else prof.variants):
        bgL = lum(measure.background(prof, v))
        rows = []
        for f in frames:
            ref = measure.load_frame(prof, v, f)
            fp = prof.out_dir() / "frames" / f"{v}_{f:02d}.png"
            if ref is None:
                continue
            reb = np.array(Image.open(fp).convert("RGB")).astype(int) if fp.exists() else np.zeros_like(ref) + 40
            Lr, Lb = lum(ref), lum(reb)
            mr, mb = Lr > a.bright, Lb > a.bright
            dr, db = (Lr < a.dark) & (bgL > a.dark + 10), (Lb < a.dark) & (bgL > a.dark + 10)
            r = dict(frame=f, ref_area=int(mr.sum()), area_ratio=round(mb.sum() / mr.sum(), 3) if mr.sum() > 50 else None,
                     width_ratio=round(width(mb) / width(mr), 3) if mr.sum() > 50 and mb.sum() > 50 else None,
                     dark_ratio=round(db.sum() / dr.sum(), 3) if dr.sum() > 200 else None)
            rows.append(r)
        ok = [r for r in rows if r["area_ratio"] is not None and r["width_ratio"] is not None]
        mean = dict(area_ratio=round(float(np.mean([r["area_ratio"] for r in ok])), 3) if ok else None,
                    width_ratio=round(float(np.mean([r["width_ratio"] for r in ok])), 3) if ok else None,
                    in_band=f"{sum(0.8 <= r['area_ratio'] <= 1.25 and 0.8 <= r['width_ratio'] <= 1.25 for r in ok)}/{len(ok)}")
        out[v] = {"mean": mean, "frames": rows}
        print(v, json.dumps(mean))
        for r in rows:
            flag = "" if r["area_ratio"] is None or (0.8 <= r["area_ratio"] <= 1.25 and 0.8 <= (r["width_ratio"] or 0) <= 1.25) else "  <-- off"
            print("  ", json.dumps(r), flag)
    (prof.out_dir() / "rebuild_check.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
