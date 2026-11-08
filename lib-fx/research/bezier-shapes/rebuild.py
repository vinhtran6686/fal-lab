"""Steps 3-4: rebuild every layer of frames 3-5 from fitted stroke parameters, rasterise, IoU, side-by-side images."""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
from masks import LAYERS, BIG, clean_mask, raw_mask, iou, frame_rgb, IDX
from polar import fit_centre, seam_angle, to_polar, bands, bands_any
from fit import fit_band
from shapes import stroke_path
from bezier import sample_path, path_d, svg_doc
import cv2

OUT = Path(__file__).parent / "out"

def raster_union(paths, shape=(700, 700), ss=4):
    H, W = shape
    acc = np.zeros((H * ss, W * ss), np.uint8)
    for segs in paths:
        if segs:
            p = sample_path(segs, 16) * ss
            cv2.fillPoly(acc, [np.round(p * 16).astype(np.int32)], 1, shift=4)
    return acc.reshape(H, ss, W, ss).mean((1, 3)) >= 0.5

def _fit_all(mask, centre, seam, robust, min_area, op, axis="theta"):
    out = []
    P = to_polar(mask, centre, seam)
    for bd in bands_any(P, seam, axis):
        if axis == "theta":
            area = float(np.sum((bd["hi"] + 0.5 - bd["lo"]) * (bd["hi"] + bd["lo"]) / 2) * 2 * np.pi / 1440)
        else:
            area = float(np.sum(bd["hi"] - bd["lo"]) / 200.0 * np.mean(bd["j"]) * 0.5 * 0.5)
        if area < min_area:
            continue
        p = fit_band(bd, seam, robust=robust, axis=axis)
        p["area"], p["op"] = area, op
        out.append(p)
    return out

def render(shapes, centre):
    add = raster_union([stroke_path(p, centre) for p in shapes if p["op"] == "add"])
    cut = raster_union([stroke_path(p, centre) for p in shapes if p["op"] == "cut"])
    return add & ~cut

def build_layer(mask, centre, seam, passes=3, min_area=12, min_gain=0.003):
    """Body first (robust fit: fused tongue bases are outliers), then tongues added / notches cut from the residual.
    Mirrors the drawing order assumed for the designer: smooth stroke, then flame tongues and bites on top."""
    from scipy import ndimage as ndi
    shapes = _fit_all(mask, centre, seam, True, min_area, "add")
    cur = render(shapes, centre)
    for _ in range(passes):
        st = ndi.generate_binary_structure(2, 1)
        add = ndi.binary_opening(mask & ~cur, st)
        cut = ndi.binary_opening(cur & ~mask, st)
        new = [p for ax in ("theta", "r") for p in
               _fit_all(add, centre, seam, False, min_area, "add", ax) + _fit_all(cut, centre, seam, False, min_area, "cut", ax)]
        new.sort(key=lambda p: -p["area"])
        base = iou(cur, mask)
        took = False
        for p in new:  # keep a tongue / notch only if it pays for itself
            trial = render(shapes + [p], centre)
            g = iou(trial, mask)
            if g - base >= min_gain:
                shapes, cur, base, took = shapes + [p], trial, g, True
        if not took:
            break
    return shapes

def main(frames=(3, 4, 5)):
    OUT.mkdir(exist_ok=True)
    report = {}
    for v, layers in LAYERS.items():
        pal = IDX[v + "_palette"]
        for f in frames:
            masks = {l: clean_mask(v, f, l) for l in layers}
            U = np.zeros((700, 700), bool)
            for m in masks.values():
                U |= m
            if U.sum() < 30:  # effect finished: empty frame
                (OUT / f"rebuild_{v}_{f:02d}.svg").write_text(svg_doc(700, 700, "", "#141414"))
                (OUT / f"params_{v}_{f:02d}.json").write_text(json.dumps({"layers": {}}))
                continue
            cx, cy, R = fit_centre(U)
            seam = seam_angle(U, (cx, cy))
            canvas = np.zeros((700, 700, 3), np.uint8) + 20
            svg = []
            params = {"centre": [cx, cy], "seam": seam, "layers": {}}
            for l in layers:
                shapes = build_layer(masks[l], (cx, cy), seam)
                paths = [stroke_path(p, (cx, cy)) for p in shapes]
                rm = render(shapes, (cx, cy))
                canvas[rm] = pal[l]
                col = "#%02x%02x%02x" % tuple(pal[l])
                adds = " ".join(path_d(s) for s, p in zip(paths, shapes) if p["op"] == "add")
                cuts = " ".join(path_d(s) for s, p in zip(paths, shapes) if p["op"] == "cut")
                mid = f"{v}{f}{l}"
                if cuts:
                    svg.append(f'<mask id="m{mid}"><rect width="700" height="700" fill="#fff"/><path fill="#000" d="{cuts}"/></mask>')
                svg.append(f'<path fill="{col}" d="{adds}"' + (f' mask="url(#m{mid})"' if cuts else "") + "/>")
                raw = raw_mask(v, f, l)
                raw = raw if raw is not None else np.zeros_like(rm)
                key = f"{v}_{f:02d}_{l}"
                report[key] = dict(iou_clean=round(iou(rm, masks[l]), 3), iou_raw=round(iou(rm, raw), 3),
                                   shapes=len(shapes), cuts=sum(p['op']=='cut' for p in shapes), params=int(sum(p["npar"] for p in shapes)),
                                   anchors=int(sum(len(s) for s in paths)), big=l in BIG)
                params["layers"][l] = shapes
            (OUT / f"rebuild_{v}_{f:02d}.svg").write_text(svg_doc(700, 700, "".join(svg), "#141414"))
            (OUT / f"params_{v}_{f:02d}.json").write_text(json.dumps(params, indent=0))
            orig = frame_rgb(v, f).astype(np.uint8)
            Image.fromarray(np.hstack([orig, canvas])).save(OUT / f"compare_{v}_{f:02d}.png")
    rp = OUT / "rebuild_report.json"
    old = json.loads(rp.read_text()) if rp.exists() else {}
    old.update(report)
    rp.write_text(json.dumps(dict(sorted(old.items())), indent=1))
    for k, r in report.items():
        print(k, r)

if __name__ == "__main__":
    fr = tuple(int(x) for x in sys.argv[1].split(",")) if len(sys.argv) > 1 else (3, 4, 5)
    main(fr)
