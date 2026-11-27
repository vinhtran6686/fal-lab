"""Compare a vector rebuild with its REFERENCE IMAGE (not with its own masks): IoU of layer masks misses a stroke traced
too thick (a thick stroke always covers a thin one: lightning R2 scored IoU 0.999 with strokes 3x too wide), so this
check measures both images directly. Interface as specified in lib-fx/_plans/vfx-rebuild-02/R1b-flame-burst-smoke.md.

    python lib-fx/_tools/rebuild_check.py PROFILE [--variant V | --variants a,b] [--mode bright|dark] [--frames A-B]
                                                  [--bright 170] [--dark-l 110] [--dark-d 14]

--mode bright (strokes): M = L > --bright on both images; per frame area_ref, area_reb, area_ratio = reb / ref,
    width_ref, width_reb, width_ratio, width = 2 * mean(distance to the edge on the skeleton). Frames with area_ref < 50
    are skipped. Pick --bright between the stroke's edge colour and the glow (lightning-2: 120). Pass: ratios 0.8-1.25.
--mode dark (smoke, inverse flash frames): M = (max channel |image - backdrop| > --dark-d) & (L < --dark-l); per frame
    area_ref, area_reb, area_ratio, IoU (the rebuild's backdrop is the profile's flat `background`). Frames with
    area_ref < 500 are skipped. Black shapes in a glow: --dark-l 40.
L = 0.299 R + 0.587 G + 0.114 B; backdrop = the profile's background_frame (measure.background).
Writes lib-fx/_study/<name>/check_<mode>.csv and rebuild_check_<mode>.json (with the thresholds used) next to the rebuild."""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "_core" / "formulas"))
from vector import Profile, measure  # noqa: E402


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def width(m):
    sk = skeletonize(m)
    return float(2 * ndi.distance_transform_edt(m)[sk].mean()) if sk.any() else 0.0


def rng(s):
    if not s:
        return None
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def summary(rows, keys):
    out = {}
    for k in keys:
        vals = [r[k] for r in rows if r.get(k) is not None]
        if vals:
            i = int(np.argmin(vals))
            out[k] = dict(mean=round(float(np.mean(vals)), 3), min=round(float(min(vals)), 3),
                          min_frame=[r for r in rows if r.get(k) is not None][i]["frame"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("profile")
    ap.add_argument("--variant")
    ap.add_argument("--variants")
    ap.add_argument("--mode", choices=["bright", "dark"], default="bright")
    ap.add_argument("--frames")
    ap.add_argument("--bright", type=float, default=170)
    ap.add_argument("--dark-l", type=float, default=110)
    ap.add_argument("--dark-d", type=float, default=14)
    a = ap.parse_args()
    p = pathlib.Path(a.profile)
    if not p.exists():
        p = HERE / "_core/formulas/vector/profiles" / f"{a.profile}.json"
    prof = Profile(p)
    frames = rng(a.frames) or prof.frames()
    variants = [a.variant] if a.variant else (a.variants.split(",") if a.variants else prof.variants)
    thresholds = dict(bright=a.bright) if a.mode == "bright" else dict(dark_l=a.dark_l, dark_d=a.dark_d)
    out, csv_rows = {"mode": a.mode, **thresholds}, []
    for v in variants:
        bg = measure.background(prof, v)
        rows = []
        for f in frames:
            ref = measure.load_frame(prof, v, f)
            if ref is None:
                continue
            fp = prof.out_dir() / "frames" / f"{v}_{f:02d}.png"
            reb = np.array(Image.open(fp).convert("RGB")).astype(float) if fp.exists() else bg.copy()
            ref = ref.astype(float)
            if a.mode == "bright":
                mr, mb = lum(ref) > a.bright, lum(reb) > a.bright
                if mr.sum() < 50:
                    continue
                wr, wb = width(mr), width(mb)
                r = dict(frame=f, area_ref=int(mr.sum()), area_reb=int(mb.sum()), area_ratio=round(mb.sum() / mr.sum(), 3),
                         width_ref=round(wr, 2), width_reb=round(wb, 2), width_ratio=round(wb / wr, 3) if wr else None)
            else:
                M = lambda im, b: (np.abs(im - b).max(-1) > a.dark_d) & (lum(im) < a.dark_l)
                # the rebuild is drawn on the profile's flat background, the reference on its own backdrop (grid, vignette)
                mr, mb = M(ref, bg), M(reb, np.array(prof.get("background"), float) if fp.exists() else bg)
                if mr.sum() < 500:
                    continue
                r = dict(frame=f, area_ref=int(mr.sum()), area_reb=int(mb.sum()), area_ratio=round(mb.sum() / mr.sum(), 3),
                         iou=round(float((mr & mb).sum() / (mr | mb).sum()), 3))
            rows.append(r)
            csv_rows.append(dict(variant=v, **r))
        keys = ["area_ratio", "width_ratio"] if a.mode == "bright" else ["area_ratio", "iou"]
        band = [r for r in rows if all(r.get(k) is not None and 0.8 <= r[k] <= 1.25 for k in keys if k != "iou")]
        out[v] = dict(summary=summary(rows, keys), in_band=f"{len(band)}/{len(rows)}", frames=rows)
        print(v, json.dumps(out[v]["summary"]), "in 0.8-1.25:", out[v]["in_band"])
        for r in rows:
            print("  ", json.dumps(r))
    study = prof.out_dir().parent
    if csv_rows:
        with open(study / f"check_{a.mode}.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(csv_rows[0]))
            w.writeheader()
            w.writerows(csv_rows)
    (prof.out_dir() / f"rebuild_check_{a.mode}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
