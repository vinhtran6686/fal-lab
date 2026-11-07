"""Step 1: trace every clean layer mask into closed cubic Bezier paths, measure the fit, write SVG overlays + stats."""
import json, base64, io
from pathlib import Path
import numpy as np
from PIL import Image
from masks import LAYERS, clean_mask, iou, REF
from bezier import contours, vectorize_loop, max_error, raster, path_d, svg_doc

OUT = Path(__file__).parent / "out"
COL = {"yellow": "#ffd670", "amber": "#feac4c", "pink": "#ff628c", "crimson": "#d12f57",
       "ice": "#efffff", "cyan": "#69e7fe", "mid": "#3ba9e2", "deep": "#1e6d9d"}

def trace(mask, tol=1.0):
    loops = []
    for c in contours(mask):
        segs, flags, sharp, cs = vectorize_loop(c, tol)
        emax, emean = max_error(segs, cs)
        loops.append(dict(segs=segs, flags=flags, sharp=sharp, emax=emax, emean=emean, n=len(cs)))
    return loops

def main(frames=(3, 4, 5)):
    OUT.mkdir(exist_ok=True)
    stats = {}
    for v, layers in LAYERS.items():
        for f in frames:
            body = []
            frame = Image.open(REF / f"frames/{v}_{f:02d}.png").convert("RGB")
            buf = io.BytesIO(); frame.save(buf, "PNG")
            body.append(f'<image width="700" height="700" opacity="0.55" xlink:href="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"/>')
            for l in layers:
                m = clean_mask(v, f, l)
                loops = trace(m)
                segs = [lp["segs"] for lp in loops]
                rm = raster(segs, m.shape)
                key = f"{v}_{f:02d}_{l}"
                stats[key] = dict(
                    loops=len(loops), anchors=sum(len(s) for s in segs),
                    sharp=sum(len(lp["sharp"]) for lp in loops),
                    err_max=round(max([lp["emax"] for lp in loops] or [0]), 2),
                    err_mean=round(float(np.mean([lp["emean"] for lp in loops] or [0])), 3),
                    iou_trace=round(iou(rm, m), 4),
                    sharp_angles=sorted(round(a) for lp in loops for _, a in lp["sharp"]))
                d = " ".join(path_d(s) for s in segs)
                body.append(f'<path d="{d}" fill="none" stroke="{COL[l]}" stroke-width="1.2" fill-rule="evenodd"/>')
                # mark sharp anchors
                for lp in loops:
                    for s, fl in zip(lp["segs"], lp["flags"]):
                        if fl:
                            body.append(f'<circle cx="{s[0][0]:.1f}" cy="{s[0][1]:.1f}" r="2.2" fill="#fff" stroke="#000" stroke-width="0.6"/>')
                # stash traced path (measurement only)
                (OUT / "trace").mkdir(exist_ok=True)
                (OUT / "trace" / f"{key}.svg").write_text(svg_doc(700, 700, f'<path d="{d}" fill="{COL[l]}" fill-rule="evenodd"/>', "#141414"))
            (OUT / f"overlay_{v}_{f:02d}.svg").write_text(svg_doc(700, 700, "".join(body), "#000"))
    (OUT / "trace_stats.json").write_text(json.dumps(stats, indent=1))
    for k, s in stats.items():
        print(k, {x: s[x] for x in ("loops", "anchors", "sharp", "err_max", "err_mean", "iou_trace")})

if __name__ == "__main__":
    main()
