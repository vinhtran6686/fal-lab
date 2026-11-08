"""How the designer animated a reference: per-frame area, number of pieces, largest piece, extent, held frames (drawn
'on twos'), plus the phases found from the area curve. Used to write generation rules (README section 8)."""
import json
import numpy as np
from scipy import ndimage as ndi
from . import measure


def frame_stats(prof, v, frames):
    k = prof.d["source"].get("scale", 1)
    rows, prev = [], None
    for f in frames:
        rgb = measure.load_frame(prof, v, f)
        if rgb is None:
            continue
        held = prev is not None and float(np.abs(rgb - prev).mean()) < 0.5
        prev = rgb
        U = np.zeros(rgb.shape[:2], bool)
        for m in measure.layer_masks(prof, v, rgb).values():
            U |= m
        lab, n = ndi.label(U)
        sz = np.sort(ndi.sum(U, lab, range(1, n + 1)))[::-1] if n else np.zeros(1)
        ys, xs = np.nonzero(U)
        rows.append(dict(frame=f, held=held, area=float(U.sum() / k / k), pieces=int(n),
                         big_pieces=int((sz >= 200 * k * k).sum()) if n else 0, largest=float(sz[0] / k / k),
                         extent_h=float((np.ptp(ys) if len(ys) else 0) / k), extent_w=float((np.ptp(xs) if len(xs) else 0) / k)))
    return rows


def phases(rows):
    """birth (first visible) -> peak (max area) -> break (pieces jump / largest < 60 % of area) -> end (area < 2 % peak)."""
    a = np.array([r["area"] for r in rows])
    if not len(a) or a.max() == 0:
        return {}
    alive = [r for r in rows if r["area"] > 0]
    peak = rows[int(np.argmax(a))]
    after = [r for r in rows if r["frame"] >= peak["frame"]]
    brk = next((r for r in after if r["largest"] < 0.6 * r["area"] or r["pieces"] >= 3 * max(peak["pieces"], 1)), after[-1])
    end = next((r for r in after if r["area"] < 0.02 * peak["area"]), after[-1])
    held = [r["frame"] for r in rows if r["held"] and r["area"] > 0]
    decay = [r["area"] for r in after if r["area"] > 0]
    per_frame = float(np.exp(np.mean(np.diff(np.log(decay))))) if len(decay) > 2 else None
    return dict(birth=alive[0]["frame"], peak=peak["frame"], break_up=brk["frame"], end=end["frame"],
                build_frames=peak["frame"] - alive[0]["frame"], life_frames=end["frame"] - alive[0]["frame"],
                first_held=held[0] if held else None, area_ratio_per_frame_after_peak=round(per_frame, 3) if per_frame else None,
                max_pieces=int(max(r["pieces"] for r in rows)))


def report(prof, frames=None):
    frames = frames or prof.frames()
    out = {}
    for v in prof.variants:
        rows = frame_stats(prof, v, frames)
        out[v] = dict(phases=phases(rows), frames=rows)
    p = prof.out_dir() / "lifecycle.json"
    p.write_text(json.dumps(out, indent=1))
    return out, p
