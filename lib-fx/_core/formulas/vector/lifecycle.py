"""How the designer animated a reference: per-frame area, number of pieces, largest piece, extent, held frames (drawn
'on twos'), stroke width, area per layer, plus the phases found from the area curve, and, for a loop of several hits
(lightning: a new bolt every 6-10 drawings), the phases of each hit (`events`). Used to write generation rules (README section 8)."""
import json
import numpy as np
from scipy import ndimage as ndi
from . import measure


def frame_stats(prof, v, frames):
    from skimage.morphology import skeletonize
    k = prof.d["source"].get("scale", 1)
    ex = measure.exposure(prof, v)
    rows, prev = [], None
    for f in frames:
        rgb = measure.load_frame(prof, v, f)
        if rgb is None:
            continue
        held = prev is not None and float(np.abs(rgb - prev).mean()) < 0.5
        prev = rgb
        U = np.zeros(rgb.shape[:2], bool)
        M = measure.layer_masks(prof, v, rgb)
        for m in M.values():
            U |= m
        lab, n = ndi.label(U)
        sk = int(skeletonize(U).sum()) if U.any() else 0
        sz = np.sort(ndi.sum(U, lab, range(1, n + 1)))[::-1] if n else np.zeros(1)
        ys, xs = np.nonzero(U)
        rows.append(dict(frame=f, held=held, area=float(U.sum() / k / k), pieces=int(n),
                         big_pieces=int((sz >= 200 * k * k).sum()) if n else 0, largest=float(sz[0] / k / k),
                         extent_h=float((np.ptp(ys) if len(ys) else 0) / k), extent_w=float((np.ptp(xs) if len(xs) else 0) / k),
                         stroke_w=round(float(U.sum() / sk / k), 1) if sk else 0.0,   # mean stroke width = area / skeleton length
                         layers={l: int(m.sum() / k / k) for l, m in M.items() if m.any()}))
        if ex and f < len(ex["drawings"]):                                   # video source: frames this drawing is held
            rows[-1]["hold"] = ex["drawings"][f][1]
    return rows


def events(rows, jump=1.6):
    """Split a loop into hits: a hit starts at the first drawing after an empty one, or when the area jumps by `jump`x
    after it was falling (a new bolt drawn over the remains of the old one). Each hit gets the phases() of its rows."""
    out, cur = [], []
    for i, r in enumerate(rows):
        a = r["area"]
        rising = cur and a > jump * cur[-1]["area"] and len(cur) >= 2 and cur[-1]["area"] < cur[-2]["area"]
        if a == 0 or rising:
            if cur:
                out.append(cur)
            cur = [r] if a > 0 else []
        else:
            cur.append(r)
    if cur:
        out.append(cur)
    return [dict(frames=[r["frame"] for r in e], **phases(e)) for e in out]


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
        out[v] = dict(phases=phases(rows), events=events(rows), frames=rows)
    p = prof.out_dir() / "lifecycle.json"
    p.write_text(json.dumps(out, indent=1))
    return out, p
