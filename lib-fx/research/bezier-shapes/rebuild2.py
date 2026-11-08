"""v2 rebuild after review (2026-11-08): stacked layers + pen-tool pass + measured halo.

Review said: (1) shapes look like stroke pieces glued together, kinks where a curve should run smooth;
(2) the original sits on a soft halo in the effect's colour. Changes vs rebuild.py:
  - STACKING: layers are painted bottom -> top; each lower layer is fitted to its own region PLUS the part of the layers
    above it that lies within R px, so it runs underneath them as one big smooth shape (no seams, no dark cracks).
    Frost keeps the white blade separate (the thin dark line between blade and blue flame is part of the design).
  - PEN PASS (pen.py): each layer's union of formula strokes is redrawn as few smooth Bezier curves, corner to corner.
  - HALO: halo(d) = c_near*exp(-d/s_near) + c_far*exp(-d/s_far), d = distance to the silhouette (out/halo_fit.json).
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from masks import LAYERS, iou, family_masks, FAMILY
from polar import fit_centre, seam_angle
from rebuild import build_layer, render as render_strokes
from shapes import stroke_path
from bezier import sample_path, path_d, svg_doc
from pen import pen_paths, kinks_per_100px
import cv2

OUT = Path(__file__).parent / "out2"
ORDER = {"fire": ["yellow", "pink", "crimson"], "frost": ["deep", "mid", "cyan", "ice"]}
GROUP = {"fire": {"yellow": 0, "pink": 0, "crimson": 0}, "frost": {"deep": 0, "mid": 0, "cyan": 0, "ice": 1}}
BGCOL = np.array([24, 25, 28], float)
R_UNDER = 10

def full_targets(v, masks):
    """Exact-colour masks leave 2-4 px transition gaps between layers; give each gap pixel to the nearest layer of the
    same group. Gaps between groups (frost blade | blue flame) stay empty: that is the dark line."""
    U = np.zeros((700, 700), bool)
    for m in masks.values():
        U |= m
    S = ndi.binary_fill_holes(ndi.binary_closing(U, iterations=6)) & ndi.binary_dilation(U, iterations=7)
    names = list(masks)
    dist = np.stack([ndi.distance_transform_edt(~masks[l]) if masks[l].any() else np.full((700, 700), 1e9) for l in names])
    near = np.argmin(dist, 0)
    T = {l: masks[l].copy() for l in names}
    gap = S & ~U
    for gi in set(GROUP[v].values()):
        mine = [i for i, l in enumerate(names) if GROUP[v][l] == gi]
        other = [i for i, l in enumerate(names) if GROUP[v][l] != gi]
        dmine = dist[mine].min(0)
        dother = dist[other].min(0) if other else np.full((700, 700), 1e9)
        ok = gap & (dmine <= dother) & (dother > 3.5)
        for i in mine:
            T[names[i]] |= ok & (near == i)
    return T

def raster_paths(paths, ss=4):
    acc = np.zeros((700 * ss, 700 * ss), np.uint8)
    for segs in paths:
        if segs:
            p = sample_path(segs, 16) * ss
            m = np.zeros_like(acc)
            cv2.fillPoly(m, [np.round(p * 16).astype(np.int32)], 1, shift=4)
            acc ^= m
    return acc.reshape(700, ss, 700, ss).mean((1, 3))

def halo(covers, hf):
    """Halo behind the shapes: c_near*exp(-d/s_near) + c_far*exp(-d/s_far), d = px to the silhouette (out/halo_fit.json)."""
    sil = np.zeros((700, 700))
    for c in covers.values():
        sil = np.maximum(sil, c)
    d = ndi.distance_transform_edt(sil < 0.5)
    h = np.exp(-d / hf["s_near"])[..., None] * np.array(hf["c_near"]) + np.exp(-d / hf["s_far"])[..., None] * np.array(hf["c_far"])
    return np.clip(h, 0, None)

def layer_colour(vis2, flat, g):
    """Inner gradient: flat colour shaded toward the edge tint near the edges of the VISIBLE part (out/edge_gradient_fit.json).
    vis2 = visible mask at 2x."""
    d = ndi.distance_transform_edt(vis2) / 2.0
    d = d.reshape(700, 2, 700, 2).mean((1, 3))
    w = np.exp(-np.clip(d - 0.5, 0, None) / g["s"])[..., None]
    return np.array(flat, float) * (1 - w) + np.array(g["edge"], float) * w

def main(frames):
    OUT.mkdir(exist_ok=True)
    hfit = json.loads((Path(__file__).parent / "out/halo_fit.json").read_text())
    gfit = json.loads((Path(__file__).parent / "out/edge_gradient_fit.json").read_text())
    rp = OUT / "report.json"
    report = json.loads(rp.read_text()) if rp.exists() else {}
    for v in LAYERS:
        pal = {l: FAMILY[v][l][0] for l in FAMILY[v]}
        for f in frames:
            masks = family_masks(v, f)
            U = np.zeros((700, 700), bool)
            for m in masks.values():
                U |= m
            if U.sum() < 30:
                continue
            T = full_targets(v, masks)
            cx, cy, _ = fit_centre(U)
            seam = seam_angle(U, (cx, cy))
            order = ORDER[v]
            covers, svg, params = {}, [], {"centre": [cx, cy], "seam": seam, "layers": {}}
            for i, l in enumerate(order):
                above = np.zeros((700, 700), bool)
                for l2 in order[i + 1:]:
                    if GROUP[v][l2] == GROUP[v][l]:
                        above |= T[l2]
                tgt = T[l] | (above & ndi.binary_dilation(T[l], iterations=R_UNDER)) if T[l].any() else T[l]
                if tgt.sum() < 12:
                    continue
                shapes = build_layer(tgt, (cx, cy), seam, passes=4, min_area=6, min_gain=0.0008)
                rough = render_strokes(shapes, (cx, cy)) if shapes else np.zeros((700, 700), bool)
                # pen pass on a 2x raster of the strokes
                up = cv2.resize(rough.astype(np.uint8), (1400, 1400), interpolation=cv2.INTER_NEAREST).astype(bool)
                paths = pen_paths(up, ss=2, min_area=8, sigma=2.5, k=4, corner_deg=150)
                covers[l] = raster_paths(paths)
                params["layers"][l] = dict(strokes=shapes, anchors=sum(len(p) for p in paths))
                col = "#%02x%02x%02x" % tuple(pal[l])
                svg.append(f'<path fill="{col}" fill-rule="evenodd" d="{" ".join(path_d(p) for p in paths)}"/>')
            # composite: background + halo, then layers bottom -> top with their inner edge gradient
            img = BGCOL + halo(covers, hfit[v])
            vis, claimed = {}, np.zeros((700, 700))
            for l in reversed(order):  # visible part = own cover minus what is painted above
                if l in covers:
                    vis[l] = (covers[l] >= 0.5) & (claimed < 0.5)
                    claimed = np.maximum(claimed, covers[l])
            for l in order:
                if l in covers:
                    a = covers[l][..., None]
                    v2 = cv2.resize(vis[l].astype(np.uint8), (1400, 1400), interpolation=cv2.INTER_LINEAR).astype(bool)
                    img = img * (1 - a) + layer_colour(v2, pal[l], gfit[f"{v}/{l}"]) * a
            img = np.clip(img, 0, 255).astype(np.uint8)
            Image.fromarray(img).save(OUT / f"{v}_{f:02d}.png")
            # flat (no halo) version for shape-only review
            flat = np.zeros((700, 700, 3)) + 20
            for l in order:
                if l in covers:
                    a = covers[l][..., None]
                    flat = flat * (1 - a) + np.array(pal[l], float) * a
            Image.fromarray(flat.astype(np.uint8)).save(OUT / f"{v}_{f:02d}_flat.png")
            (OUT / f"{v}_{f:02d}.svg").write_text(svg_doc(700, 700, "".join(svg), "#141414"))
            (OUT / f"params_{v}_{f:02d}.json").write_text(json.dumps(params))
            for l in FAMILY[v]:
                if l not in vis:
                    continue
                report[f"{v}_{f:02d}_{l}"] = dict(iou_full=round(iou(vis[l], T[l]), 3), iou_exact=round(iou(vis[l], masks[l]), 3),
                    anchors=params["layers"][l]["anchors"], strokes=len(params["layers"][l]["strokes"]),
                    kinks_v2=round(kinks_per_100px(vis[l]), 2), kinks_target=round(kinks_per_100px(T[l]), 2))
                print(f"{v}_{f:02d}_{l}", report[f"{v}_{f:02d}_{l}"], flush=True)
    rp.write_text(json.dumps(dict(sorted(report.items())), indent=1))

if __name__ == "__main__":
    main(tuple(int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "4").split(",")))
