"""fxkit / ink: how a layer is painted in the house style (rules/01, 02, 05).

  FLAT TONES, STACKED   a layer draws its shapes into a few tone masks (e.g. "body", "deep", "hot"); each tone is one flat colour;
                        tones are painted in order, the hot one deepest inside the mass or at the root. No outline, no contour bands.
  IN-PLACE EROSION      a shape does not shrink towards its centre and does not fade: it is eaten where it stands. `erode` keeps a
                        chosen SHARE of the area (so the area follows the measured decay curve), taking the edges first (thin parts
                        and tips go, thick parts stay) and opening holes where a fixed noise is low, so pieces chip off and die as
                        specks. The noise is fixed in space: pieces stay put from drawing to drawing.
  GLOW = THE SHAPE, BLURRED   every glowing layer adds its silhouette to the effect's glow, which is blurred at two scales in the
                        effect's main colour and put under the shapes.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

_NOISE = {}


def noise(shape, seed, scale, stretch=1.0):
    """Smooth noise 0..1, fixed in canvas space, cached. scale = feature size in supersampled px; stretch > 1 makes the features
    taller than wide (vertical slivers), < 1 wider than tall."""
    key = (shape, seed, round(scale, 1), round(stretch, 2))
    if key not in _NOISE:
        if len(_NOISE) > 64: _NOISE.clear()
        rng = np.random.default_rng(seed)
        n = ndimage.gaussian_filter(rng.standard_normal(shape).astype(np.float32), (scale * stretch, scale / max(stretch, 1e-3)))
        lo, hi = np.percentile(n, 1), np.percentile(n, 99)
        _NOISE[key] = np.clip((n - lo) / (hi - lo + 1e-9), 0, 1)
    return _NOISE[key]


def erode(mask, keep, seed, ss, holes=0.25, grain=14.0, stretch=1.0, root=None, root_bias=0.0, hollow=False, shift=(0.0, 0.0)):
    """The part of `mask` (bool, supersampled) that is still there when only the share `keep` (0..1) of its area is left.
    holes 0..1: 0 = eaten evenly from the edge (fire, crystal: 85 % edge), 0.5 = edges and holes alike (smoke, slashes).
    grain: size of the holes / chips in px. root (x, y canvas px) + root_bias: the part near the root is eaten last (a fire's
    foot outlives its tips). hollow: eaten from the inside out, the outline goes last (a veil, a membrane). shift (dx, dy) px:
    the noise has moved this far (pass a growing value: the holes travel, so the pieces seem to rise or to be blown along)."""
    if keep >= 0.999 or not mask.any(): return mask
    if keep <= 0.001: return np.zeros_like(mask)
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    m = mask[y0:y1, x0:x1]
    d = ndimage.distance_transform_edt(m)
    d = d / (d.max() + 1e-6)
    if hollow: d = np.where(m, 1 - d, 0)
    nz = noise(mask.shape, seed, grain * ss, stretch)
    if shift[0] or shift[1]: nz = np.roll(nz, (int(round(shift[1] * ss)), int(round(shift[0] * ss))), axis=(0, 1))
    f = (1 - holes) * d + holes * nz[y0:y1, x0:x1]
    if root is not None and root_bias > 0:
        yy, xx = np.mgrid[y0:y1, x0:x1]
        r = np.hypot(xx - root[0] * ss, yy - root[1] * ss)
        f = f + root_bias * (1 - r / (r[m].max() + 1e-6))
    thr = np.quantile(f[m], 1 - keep)
    out = np.zeros_like(mask); out[y0:y1, x0:x1] = m & (f > thr)
    return out


def drop_specks(mask, ss, min_px=5.0):
    """Remove pieces smaller than min_px (canvas px^2): a piece dies as a speck, it is never drawn as dust."""
    lab, n = ndimage.label(mask)
    if n == 0: return mask
    area = ndimage.sum(mask, lab, range(1, n + 1))
    small = 1 + np.flatnonzero(area < min_px * ss * ss)
    return mask & ~np.isin(lab, small) if len(small) else mask


class Ink:
    """The drawing of one layer: named tone masks at the canvas's supersampled size."""
    def __init__(self, c):
        self.c, self.cv, self.ss = c, c.cv, c.cv.ss
        self.t = {}

    def _d(self, tone):
        if tone not in self.t:
            im = Image.new("L", self.cv.img.size, 0); self.t[tone] = (im, ImageDraw.Draw(im))
        return self.t[tone][1]

    def add(self, tone, pts):
        if len(pts) >= 3: self._d(tone).polygon([(x * self.ss, y * self.ss) for x, y in pts], fill=255)

    def cut(self, tone, pts):
        if len(pts) >= 3 and tone in self.t: self._d(tone).polygon([(x * self.ss, y * self.ss) for x, y in pts], fill=0)

    def mask(self, tone):
        return np.asarray(self.t[tone][0]) > 127 if tone in self.t else np.zeros(self.cv.img.size[::-1], bool)

    def set(self, tone, m):
        im = Image.fromarray((m * 255).astype(np.uint8), "L"); self.t[tone] = (im, ImageDraw.Draw(im))

    def paint(self, order, glow=1.0, opacity=None):
        """Composite the tones onto the layer's canvas in `order` = [(tone, rgb), ...] bottom to top, each one flat colour.
        opacity = {tone: 0..1} for see-through tones (smoke, veils). glow = how strongly this layer feeds the effect's glow
        (0 = none: smoke, dust, debris)."""
        H, W = self.cv.img.size[1], self.cv.img.size[0]
        rgb_ = np.zeros((H, W, 3), np.float32); al = np.zeros((H, W), np.float32); union = np.zeros((H, W), bool)
        for tone, rgb in order:
            m = self.mask(tone)
            if not m.any(): continue
            a = float((opacity or {}).get(tone, 1.0))
            na = a + al[m] * (1 - a)                                          # "over": this tone on top of what is there
            rgb_[m] = (np.asarray(rgb, np.float32) * a + rgb_[m] * (al[m] * (1 - a))[:, None]) / np.maximum(na, 1e-6)[:, None]
            al[m] = na
            union |= m
        if not union.any(): return
        img = Image.fromarray(np.dstack([rgb_, al[..., None] * 255]).round().astype(np.uint8), "RGBA")
        self.cv.img.alpha_composite(img)
        if glow > 0: self.c.add_glow(union, glow)
