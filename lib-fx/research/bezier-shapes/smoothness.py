"""Objective smoothness of a vector path (what the eye calls 'clean' vs 'kinked'):
  - kinks        : anchors that are neither smooth (handles collinear within 5 deg) nor real corners (> 35 deg turn)
  - wobble       : curvature sign changes (inflections) per 100 px of outline, on smooth stretches
  - curv_var     : total curvature variation  sum|dk/ds| ds  per 100 px (Moreton's fairness measure; lower = fairer)"""
import numpy as np
from bezier import bez, bez_d, bez_dd

def path_fairness(paths, n=24):
    kinks, L, flips, var = 0, 0.0, 0, 0.0
    for segs in paths:
        for i, s in enumerate(segs):
            prev = segs[i - 1]
            a, b = prev[3] - prev[2], s[1] - s[0]
            if np.linalg.norm(a) > 1e-6 and np.linalg.norm(b) > 1e-6:
                ang = np.degrees(np.arccos(np.clip(np.dot(a, b) / np.linalg.norm(a) / np.linalg.norm(b), -1, 1)))
                if 5 < ang < 35:
                    kinks += 1
        ks, ds = [], []
        for s in segs:
            t = np.linspace(0, 1, n)
            d1, d2 = bez_d(s, t), bez_dd(s, t)
            sp = np.linalg.norm(d1, axis=1) + 1e-9
            k = (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / sp**3
            ks.append(k); ds.append(sp / (n - 1))
            seglen = float(np.sum(sp) / (n - 1)); L += seglen
            var += float(np.sum(np.abs(np.diff(k))))
            kk = k[np.abs(k) > 0.004]
            flips += int(np.sum(np.diff(np.sign(kk)) != 0))
    per = 100.0 / max(L, 1)
    return dict(kinks=kinks, wobble=round(flips * per, 2), curv_var=round(var * per, 2), length=round(L))
