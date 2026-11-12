"""Scores: shape match (IoU) and smoothness of vector paths (what the eye calls clean vs kinked)."""
import numpy as np
from .bezier import bez_d, bez_dd


def iou(a, b):
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else 1.0


def path_fairness(paths, n=24):
    """kinks    : anchors whose two handles turn 5-35 deg (neither smooth nor a real corner) -> should be 0
    wobble   : curvature sign changes (inflections) per 100 px of outline
    curv_var : total curvature variation sum|dk| per 100 px (Moreton's fairness measure; lower = fairer)"""
    kinks, L, flips, var = 0, 0.0, 0, 0.0
    for segs in paths:
        for i, s in enumerate(segs):
            a, b = segs[i - 1][3] - segs[i - 1][2], s[1] - s[0]
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            if na > 1e-6 and nb > 1e-6:
                ang = np.degrees(np.arccos(np.clip(np.dot(a, b) / na / nb, -1, 1)))
                kinks += int(5 < ang < 35)
        for s in segs:
            t = np.linspace(0, 1, n)
            d1, d2 = bez_d(s, t), bez_dd(s, t)
            sp = np.linalg.norm(d1, axis=1) + 1e-9
            k = (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / sp**3
            L += float(np.sum(sp) / (n - 1))
            var += float(np.sum(np.abs(np.diff(k))))
            kk = k[np.abs(k) > 0.004]
            flips += int(np.sum(np.diff(np.sign(kk)) != 0))
    per = 100.0 / max(L, 1)
    return dict(anchors=int(sum(len(s) for s in paths)), kinks=kinks, wobble=round(flips * per, 2),
                curv_var=round(var * per, 2), length=round(L))
