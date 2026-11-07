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
