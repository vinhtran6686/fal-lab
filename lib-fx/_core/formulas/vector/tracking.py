"""Follow every PIECE of an effect through the frames (G1 of the roadmap): which piece comes from which, when pieces
split, how each one grows / shrinks, how it moves, how it dies. Works on the union of the layer masks.

Matching: piece B in frame f+1 is a child of piece A in frame f when they overlap (A dilated by `reach` px); a piece with
several children SPLIT, several parents MERGED, no parent was BORN, no child DIED. Held frames (identical drawings,
'on twos') are skipped so a hold is not read as a still piece."""
import json
import numpy as np
from scipy import ndimage as ndi
from . import measure


def pieces(prof, v, f, min_area=6):
    rgb = measure.load_frame(prof, v, f)
    if rgb is None:
        return None, None
    k = prof.d["source"].get("scale", 1)
    U = np.zeros(rgb.shape[:2], bool)
    for m in measure.layer_masks(prof, v, rgb).values():
        U |= m
    lab, n = ndi.label(U)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        a = len(ys) / k / k
        if a >= min_area:
            out.append(dict(id=i, area=a, cx=xs.mean() / k, cy=ys.mean() / k))
    return lab, out


def track(prof, v, frames, reach=3):
    k = prof.d["source"].get("scale", 1)
    seq, prev_rgb = [], None
    for f in frames:
        rgb = measure.load_frame(prof, v, f)
        if rgb is None:
            continue
        if prev_rgb is not None and float(np.abs(rgb - prev_rgb).mean()) < 0.5:
            continue  # held drawing
        prev_rgb = rgb
        lab, ps = pieces(prof, v, f)
        if ps:
            seq.append((f, lab, ps))
    events = []
    for (f0, lab0, p0), (f1, lab1, p1) in zip(seq, seq[1:]):
        ids1 = {p["id"]: p for p in p1}
        # overlap of every (dilated) parent with every child; each child goes to ONE parent: the one it overlaps most
        best = {}
        for a in p0:
            grown = ndi.binary_dilation(lab0 == a["id"], iterations=int(reach * k))
            ids, cnt = np.unique(lab1[grown], return_counts=True)
            for i, c in zip(ids, cnt):
                if i in ids1 and c > best.get(i, (None, 0))[1]:
                    best[i] = (a["id"], c)
        for a in p0:
            kids = [i for i, (pa, _) in best.items() if pa == a["id"]]
            kid_area = sum(ids1[i]["area"] for i in kids)
            events.append(dict(frame=f0, next=f1, area=a["area"], n_children=len(kids), child_area=kid_area,
                               ratio=kid_area / a["area"] if kids else 0.0,
                               dy=(float(np.average([ids1[i]["cy"] for i in kids], weights=[ids1[i]["area"] for i in kids])) - a["cy"]) if kids else None,
                               largest_child_share=(max(ids1[i]["area"] for i in kids) / kid_area) if kids else None))
        for i in ids1:
            if i not in best:
                events.append(dict(frame=f1, born=True, area=ids1[i]["area"]))
    return seq, events


def summarise(seq, events):
    if not seq:
        return {}
    areas = [sum(p["area"] for p in ps) for _, _, ps in seq]
    peak_f = seq[int(np.argmax(areas))][0]
    after = [e for e in events if not e.get("born") and e["frame"] >= peak_f]
    before = [e for e in events if not e.get("born") and e["frame"] < peak_f]
    alive = [e for e in after if e["n_children"] > 0]
    big = [e for e in alive if e["area"] >= 100]
    small = [e for e in alive if e["area"] < 100]
    deaths = [e for e in after if e["n_children"] == 0]
    splits = [e for e in after if e["n_children"] >= 2]
    q = lambda xs: dict(n=len(xs), p25=round(float(np.percentile(xs, 25)), 2), med=round(float(np.median(xs)), 2),
                        p75=round(float(np.percentile(xs, 75)), 2)) if len(xs) else {}
    return dict(
        peak_frame=peak_f,
        growth_ratio_before_peak=q([e["ratio"] for e in before if e["n_children"]]),
        shrink_ratio_after_peak_big=q([e["ratio"] for e in big]),
        shrink_ratio_after_peak_small=q([e["ratio"] for e in small]),
        split_share_after_peak=round(len(splits) / max(len(alive), 1), 2),
        children_when_split=q([e["n_children"] for e in splits]),
        largest_child_share_when_split=q([e["largest_child_share"] for e in splits]),
        area_at_death=q([e["area"] for e in deaths]),
        drift_dy_px=q([e["dy"] for e in alive if e["dy"] is not None]),
        births_after_peak=sum(1 for e in events if e.get("born") and e["frame"] > peak_f),
    )


def report(prof, frames=None):
    frames = frames or prof.frames()
    out = {}
    for v in prof.variants:
        seq, ev = track(prof, v, frames)
        out[v] = dict(summary=summarise(seq, ev), events=ev)
    p = prof.out_dir() / "tracking.json"
    p.write_text(json.dumps(out, indent=1, default=float))
    return out, p
