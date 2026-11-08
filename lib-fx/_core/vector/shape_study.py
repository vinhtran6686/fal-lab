"""Foundation measurements that a generator needs beyond lifecycle / tracking (foundation/05):
  birth       : where the first drawing sits inside the peak silhouette, how big it is, how width and height grow
  erosion     : when a piece shrinks between two drawings, WHERE it loses area: at its rim or by holes inside, evenly
                or from one side (direction bias, 0 = even, 1 = all from one side)
  composition : at the peak, the silhouette seen from the effect's origin: how many tongues (peaks of the outline
                distance), their spread angle and length hierarchy; piece size hierarchy."""
import json
import numpy as np
from scipy import ndimage as ndi
from scipy.signal import find_peaks
from . import measure


def _union(prof, v, f):
    rgb = measure.load_frame(prof, v, f)
    if rgb is None:
        return None
    U = np.zeros(rgb.shape[:2], bool)
    for m in measure.layer_masks(prof, v, rgb).values():
        U |= m
    return U


def _drawn(prof, v, frames):
    seq, prev = [], None
    for f in frames:
        rgb = measure.load_frame(prof, v, f)
        if rgb is None:
            continue
        if prev is not None and float(np.abs(rgb - prev).mean()) < 0.5:
            continue
        prev = rgb
        U = _union(prof, v, f)
        if U.sum() > 0:
            seq.append((f, U))
    return seq


def _bbox(U):
    ys, xs = np.nonzero(U)
    return xs.min(), xs.max(), ys.min(), ys.max()


def birth(seq, k):
    areas = [U.sum() for _, U in seq]
    ip = int(np.argmax(areas))
    x0, x1, y0, y1 = _bbox(seq[ip][1])
    W, H = max(x1 - x0, 1), max(y1 - y0, 1)
    rows = []
    for f, U in seq[:ip + 1]:
        a0, a1, b0, b1 = _bbox(U)
        ys, xs = np.nonzero(U)
        rows.append(dict(frame=f, area_share=round(U.sum() / areas[ip], 3), width_share=round((a1 - a0) / W, 2),
                         height_share=round((b1 - b0) / H, 2), cx=round((xs.mean() - x0) / W, 2), cy=round((ys.mean() - y0) / H, 2)))
    return dict(peak_frame=seq[ip][0], frames=rows)


def erosion(seq, k, min_area=100):
    """Pairs of consecutive drawings after the peak; each piece of frame A is matched to the piece of frame B it
    overlaps most (its main continuation)."""
    areas = [U.sum() for _, U in seq]
    ip = int(np.argmax(areas))
    rim_share, bias, hole_share, depth = [], [], [], []
    for (fa, A), (fb, B) in zip(seq[ip:], seq[ip + 1:]):
        la, na = ndi.label(A)
        lb, nb = ndi.label(B)
        for i in range(1, na + 1):
            P = la == i
            if P.sum() < min_area * k * k:
                continue
            ids, cnt = np.unique(lb[P], return_counts=True)
            cnt = cnt[ids > 0]; ids = ids[ids > 0]
            if not len(ids):
                continue
            C = lb == ids[np.argmax(cnt)]
            lost = P & ~C
            if lost.sum() < 4 * k * k:
                continue
            d_in = ndi.distance_transform_edt(P)          # depth inside the parent
            filled = ndi.binary_fill_holes(P)
            new_holes = lost & filled & (d_in > 2 * k)      # lost pixels deep inside = holes opening / cuts
            rim_share.append(float((lost & (d_in <= 2 * k)).sum() / lost.sum()))
            hole_share.append(float(new_holes.sum() / lost.sum()))
            depth.append(float(np.median(d_in[lost]) / k))
            ys, xs = np.nonzero(P)
            cy, cx = ys.mean(), xs.mean()
            ly, lx = np.nonzero(lost)
            vec = np.c_[lx - cx, ly - cy]
            r = np.linalg.norm(vec, axis=1) + 1e-6
            bias.append(float(np.linalg.norm((vec / r[:, None]).mean(0))))
    q = lambda xs: dict(n=len(xs), p25=round(float(np.percentile(xs, 25)), 2), med=round(float(np.median(xs)), 2),
                        p75=round(float(np.percentile(xs, 75)), 2)) if xs else {}
    return dict(rim_share=q(rim_share), hole_share=q(hole_share), lost_depth_px=q(depth), one_side_bias=q(bias))


def composition(seq, k, origin="bottom"):
    """Outline distance from the origin (bottom-centre for eruptions, centroid otherwise) as a function of angle;
    tongues = its peaks."""
    areas = [U.sum() for _, U in seq]
    f, U = seq[int(np.argmax(areas))]
    x0, x1, y0, y1 = _bbox(U)
    ys, xs = np.nonzero(U)
    ox, oy = ((x0 + x1) / 2, y1) if origin == "bottom" else (xs.mean(), ys.mean())
    ang = np.degrees(np.arctan2(-(ys - oy), xs - ox))      # 90 = straight up
    rad = np.hypot(xs - ox, ys - oy)
    bins = np.arange(-180, 181, 3)
    prof = np.zeros(len(bins) - 1)
    idx = np.digitize(ang, bins) - 1
    np.maximum.at(prof, np.clip(idx, 0, len(prof) - 1), rad)
    sm = ndi.uniform_filter1d(prof, 3, mode="wrap")
    pk, props = find_peaks(np.r_[sm, sm[:5]], prominence=0.12 * sm.max())
    pk = sorted(set(p % len(sm) for p in pk))
    centres = bins[:-1][pk] + 1.5
    lens = sorted((sm[pk] / sm.max()).round(2).tolist(), reverse=True)
    lab, n = ndi.label(U)
    sz = np.sort(ndi.sum(U, lab, range(1, n + 1)))[::-1] if n else np.zeros(1)
    return dict(frame=f, origin=origin, tongues=len(pk), tongue_angles_deg=[round(float(c)) for c in sorted(centres)],
                spread_deg=round(float(np.ptp(centres)), 0) if len(pk) > 1 else 0.0, tongue_length_ratio=lens,
                piece_size_ratio=[round(float(s / sz[0]), 3) for s in sz[:5]])


def study(prof, frames=None, origins=None):
    frames = frames or prof.frames()
    k = prof.d["source"].get("scale", 1)
    out = {}
    for v in prof.variants:
        seq = _drawn(prof, v, frames)
        if not seq:
            continue
        org = (origins or {}).get(v, "bottom" if (prof.var(v).get("frame") or prof.get("frame")).get("type") == "linear" else "centroid")
        out[v] = dict(birth=birth(seq, k), erosion=erosion(seq, k), composition=composition(seq, k, org))
    p = prof.out_dir() / "shape_study.json"
    p.write_text(json.dumps(out, indent=1))
    return out, p
