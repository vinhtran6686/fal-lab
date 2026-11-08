"""v3 (2026-11-08): same formula strokes as v2 (out2/params_*.json), new outline clean-up `fair.smooth_simplify`
(Illustrator Simplify / potrace curve optimisation / curvature fairing) instead of `pen.pen_paths`.
Writes out3/: final frames (gradient + halo), flat frames, SVG, report with smoothness metrics."""
import json, sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from masks import family_masks, FAMILY, iou
from rebuild2 import full_targets, ORDER, BGCOL, halo, layer_colour, raster_paths
from shapes import stroke_path
from bezier import sample_path, path_d, svg_doc
from fair import smooth_simplify
from smoothness import path_fairness

HERE = Path(__file__).parent
OUT = HERE / "out3"
# Clean-up strength per variant. Frost "max smooth" (user review 2026-11-08: fire 9/10, frost 8/10 "still cracked"):
# stronger fairing, only clearly sharp corners kept, longer merged curves, bigger gaps joined, crumbs < 40 px dropped.
SMOOTH = {"fire": dict(sigma=4.5, corner_deg=145, merge_tol=0.9, min_area=8, close_px=1.5),
          "frost": dict(sigma=7.0, corner_deg=142, merge_tol=1.5, min_area=40, close_px=2.5)}
# The near halo term fitted on frost (s_near 0.5 px) is the GIF's anti-aliasing, not a glow: drawn, it outlines every
# edge with bright dots. Only the wide glow is kept for frost.
NEAR_HALO = {"fire": True, "frost": False}

def stroke_cover(shapes, centre, ss=2, sub=4):
    """Coverage of add-strokes minus cut-strokes at ss x resolution (supersampled sub x)."""
    S = 700 * ss * sub
    def ras(op):
        acc = np.zeros((S, S), np.uint8)
        for p in shapes:
            if p["op"] == op:
                pts = sample_path(stroke_path(p, centre), 16) * ss * sub
                cv2.fillPoly(acc, [np.round(pts * 16).astype(np.int32)], 1, shift=4)
        return acc
    m = ras("add") & (1 - ras("cut"))
    return m.reshape(700 * ss, sub, 700 * ss, sub).mean((1, 3))

def main(frames):
    OUT.mkdir(exist_ok=True)
    hfit = json.loads((HERE / "out/halo_fit.json").read_text())
    gfit = json.loads((HERE / "out/edge_gradient_fit.json").read_text())
    rp = OUT / "report.json"
    report = json.loads(rp.read_text()) if rp.exists() else {}
    for v in VARIANTS:
        pal = {l: FAMILY[v][l][0] for l in FAMILY[v]}
        for f in frames:
            pj = HERE / f"out2/params_{v}_{f:02d}.json"
            if not pj.exists():
                continue
            P = json.loads(pj.read_text())
            if not P.get("layers"):
                continue
            c = tuple(P["centre"])
            masks = family_masks(v, f)
            T = full_targets(v, masks)
            covers, svg, allpaths = {}, [], {}
            for l in ORDER[v]:
                if l not in P["layers"] or not P["layers"][l]["strokes"]:
                    continue
                cov = stroke_cover(P["layers"][l]["strokes"], c)
                paths, st = smooth_simplify(cov, ss=2, **SMOOTH[v])
                covers[l] = raster_paths(paths)
                allpaths[l] = (paths, st)
                svg.append(f'<path fill="#%02x%02x%02x" fill-rule="evenodd" d="{" ".join(path_d(p) for p in paths)}"/>' % tuple(pal[l]))
            hf = dict(hfit[v]) if NEAR_HALO[v] else dict(hfit[v], c_near=[0, 0, 0])
            img = BGCOL + halo(covers, hf)
            vis, claimed = {}, np.zeros((700, 700))
            for l in reversed(ORDER[v]):
                if l in covers:
                    vis[l] = (covers[l] >= 0.5) & (claimed < 0.5)
                    claimed = np.maximum(claimed, covers[l])
            flat = np.zeros((700, 700, 3)) + 20
            for l in ORDER[v]:
                if l in covers:
                    a = covers[l][..., None]
                    v2 = cv2.resize(vis[l].astype(np.uint8), (1400, 1400), interpolation=cv2.INTER_LINEAR).astype(bool)
                    img = img * (1 - a) + layer_colour(v2, pal[l], gfit[f"{v}/{l}"]) * a
                    flat = flat * (1 - a) + np.array(pal[l], float) * a
            Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(OUT / f"{v}_{f:02d}.png")
            Image.fromarray(flat.astype(np.uint8)).save(OUT / f"{v}_{f:02d}_flat.png")
            (OUT / f"{v}_{f:02d}.svg").write_text(svg_doc(700, 700, "".join(svg), "#141414"))
            for l, (paths, st) in allpaths.items():
                fa = path_fairness(paths)
                report[f"{v}_{f:02d}_{l}"] = dict(iou=round(iou(vis[l], T[l]), 3), anchors=st["anchors"], corners=st["corners"], **fa)
                print(f"{v}_{f:02d}_{l}", report[f"{v}_{f:02d}_{l}"], flush=True)
    rp.write_text(json.dumps(dict(sorted(report.items())), indent=1))

VARIANTS = list(FAMILY)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        VARIANTS = sys.argv[2].split(",")
    main(tuple(int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "4").split(",")))
