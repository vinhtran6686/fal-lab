"""Clean per-colour masks for the swirl-slash reference (exact palette colour, not the halo-polluted <30 masks)."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[3]
REF = ROOT / "ref/vfx/swirl-slash"
IDX = json.loads((REF / "layers/index.json").read_text())
LAYERS = {"fire": ["yellow", "amber", "pink", "crimson"], "frost": ["ice", "cyan", "mid", "deep"]}
BIG = {"yellow", "pink", "ice", "mid"}


def frame_rgb(variant, f):
    return np.array(Image.open(REF / f"frames/{variant}_{f:02d}.png").convert("RGB")).astype(int)


def clean_mask(variant, f, layer, tol=12, min_area=12):
    """Pixel is in the layer when its colour is within `tol` of the flat fill.
    Then: median 3x3 (drops dither speckle), holes < min_area filled, parts < min_area dropped."""
    a = frame_rgb(variant, f)
    c = np.array(IDX[variant + "_palette"][layer])
    m = np.sqrt(((a - c) ** 2).sum(-1)) < tol
    if layer == "ice":  # the white blade is tinted cyan by the additive halo near its edges: keep every near-white pixel
        m = (a[..., 0] > 200) & (a[..., 1] > 235) & (a[..., 2] > 235)
    m = ndi.median_filter(m.astype(np.uint8), 3).astype(bool)
    lab, n = ndi.label(~m)
    sizes = ndi.sum(~m, lab, range(1, n + 1))
    for i, s in enumerate(sizes, 1):
        if s < min_area:
            m[lab == i] = True
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1))
    for i, s in enumerate(sizes, 1):
        if s < min_area:
            m[lab == i] = False
    return m


def raw_mask(variant, f, layer):
    p = REF / f"layers/{variant}_{f:02d}_{layer}.png"
    return np.array(Image.open(p)) > 127 if p.exists() else None


def iou(a, b):
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else 1.0


# ---- v2 (after review 2026-11-08): a layer = its flat colour PLUS its own edge gradient --------------------------
# The flat fills are shaded toward a second colour near their edges (inner glow). Exact-colour masks missed that band,
# so the yellow lost ~30 % of its area and the pink tongues stabbing into it vanished. Each layer is now a colour
# polyline (flat -> edge tint); a pixel belongs to the closest polyline. Amber is the edge tint of yellow, not a layer.
FAMILY = {
    "fire": {"yellow": [(255, 214, 112), (252, 186, 88), (254, 172, 76), (250, 150, 60)],
             "pink": [(255, 98, 140), (252, 70, 122)],
             "crimson": [(209, 47, 87)]},
    "frost": {"ice": [(239, 255, 255), (215, 255, 255), (168, 252, 240)],
              "cyan": [(105, 231, 254), (84, 204, 252)],
              "mid": [(59, 169, 226)],
              "deep": [(30, 109, 157)]},
}
FAMILY_TOL = {"yellow": 26, "pink": 22, "crimson": 12, "ice": 22, "cyan": 18, "mid": 14, "deep": 12}

def _dist_poly(a, pts):
    pts = [np.array(p, float) for p in pts]
    if len(pts) == 1:
        return np.linalg.norm(a - pts[0], axis=-1)
    d = np.full(a.shape[:-1], 1e9)
    for p, q in zip(pts, pts[1:]):
        e = q - p
        t = np.clip(((a - p) @ e) / (e @ e), 0, 1)
        d = np.minimum(d, np.linalg.norm(a - (p + t[..., None] * e), axis=-1))
    return d

def family_masks(variant, f, min_area=12):
    a = frame_rgb(variant, f).astype(float)
    fam = FAMILY[variant]
    names = list(fam)
    D = np.stack([_dist_poly(a, fam[l]) / FAMILY_TOL[l] for l in names])
    best = np.argmin(D, 0)
    ok = np.min(D, 0) < 1
    out = {}
    for i, l in enumerate(names):
        m = ok & (best == i)
        m = ndi.median_filter(m.astype(np.uint8), 3).astype(bool)
        for inv in (True, False):
            tgt = ~m if inv else m
            lab, n = ndi.label(tgt)
            if n:
                sizes = ndi.sum(tgt, lab, range(1, n + 1))
                m[np.isin(lab, 1 + np.flatnonzero(sizes < min_area))] = inv
        out[l] = m
    return out
