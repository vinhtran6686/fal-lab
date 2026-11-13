"""fxkit / ink: how a layer is painted in the house style (rules/01, 02, 05).

  FLAT TONES, STACKED   a layer draws its shapes into a few tone masks (e.g. "body", "deep", "hot"); each tone is one flat colour;
                        tones are painted in order, the hot one deepest inside the mass or at the root. No outline, no contour bands.
  IN-PLACE EROSION      a shape does not shrink towards its centre and does not fade: it is eaten where it stands. `erode` keeps a
                        chosen SHARE of the area (so the area follows the measured decay curve), taking the edges first (thin parts
                        and tips go, thick parts stay) and opening holes where a fixed noise is low, so pieces chip off and die as
                        specks. The noise is fixed in space: pieces stay put from drawing to drawing.
  SMOOTH OUTLINES       before painting, every tone mask goes through `smooth_mask` (the Smooth Tool of a vector editor): concave corners
                        where two shapes meet are filleted, small burrs left by the erosion are shaved, the edge is evened out, and
                        real tips stay sharp. A kind may ask for less (`Ink(c, smooth=dict(fillet=1.0))`) or none (`smooth=False`).
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


def _disc(m, r, grow):
    """Morphological dilation (grow) or erosion of a bool mask by a disc of radius r px, from the distance transform."""
    if r <= 0: return m
    return ndimage.distance_transform_edt(~m) <= r if grow else ndimage.distance_transform_edt(m) > r


def smooth_mask(mask, ss, fillet=2.0, burr=1.0, tip_keep=6.0, sigma=0.8):
    """The outline of a tone mask (bool, supersampled by ss), smoothed like the Smooth Tool of a vector editor. Three steps:
    1. fillet: closing by a disc of `fillet` canvas px rounds the concave corners where two shapes meet (tips are convex: untouched);
    2. burr: opening by `burr` px shaves the small bumps and chips an erosion leaves on the edge; what the opening cuts off but that is
       a real tip (a connected piece longer than `tip_keep` px that hangs on the opened shape) is put back;
    3. even out: a Gaussian blur of `sigma` canvas px of the mask, cut at 0.5, makes the edge one even curve; the tips are put back
       again so they stay sharp. Pieces thinner than the burr (a ring line, a streak, a bolt tail) survive as tips.
    Works on the bounding box only. fillet = burr = 0 and sigma = 0 returns the mask unchanged."""
    if not mask.any() or (fillet <= 0 and burr <= 0 and sigma <= 0): return mask
    ys, xs = np.nonzero(mask)
    pad = int(round((fillet + burr + 3 * sigma + 2) * ss)) + 2
    y0, y1 = max(0, ys.min() - pad), min(mask.shape[0], ys.max() + 1 + pad)
    x0, x1 = max(0, xs.min() - pad), min(mask.shape[1], xs.max() + 1 + pad)
    m = mask[y0:y1, x0:x1]
    if fillet > 0:
        r = fillet * ss
        m = m | _disc(_disc(m, r, True), r, False)
    base, tips = m, np.zeros_like(m)
    if burr > 0:
        r = burr * ss
        opened = _disc(_disc(m, r, False), r, True) & m
        rest = m & ~opened
        if rest.any():
            lab, n = ndimage.label(rest, structure=np.ones((3, 3)))
            touch = np.unique(lab[ndimage.binary_dilation(opened, iterations=2) & rest])
            sl = ndimage.find_objects(lab)
            keep = [i + 1 for i in range(n) if (i + 1) in touch and np.hypot(sl[i][0].stop - sl[i][0].start, sl[i][1].stop - sl[i][1].start) > tip_keep * ss]
            if keep: tips = np.isin(lab, keep)
        base = opened | tips
    if sigma > 0:
        f = ndimage.gaussian_filter(base.astype(np.float32), sigma * ss) > 0.5
        base = f | tips
    out = np.zeros_like(mask); out[y0:y1, x0:x1] = base
    return out


THIN = dict(fillet=1.0, burr=0.5, sigma=0.6)       # for thin kinds (ring, streaks, scraps, embers, bolt): a light touch, nothing thin may vanish


class Ink:
    """The drawing of one layer: named tone masks at the canvas's supersampled size."""
    def __init__(self, c, smooth=True):
        """smooth: True = the house defaults of `smooth_mask`; a dict of its keywords (fillet, burr, tip_keep, sigma) = tuned
        (thin kinds: ring, streaks, scraps, bolt ask for less); False = paint the masks as they are."""
        self.c, self.cv, self.ss = c, c.cv, c.cv.ss
        self.t = {}
        self.smooth = smooth

    def _d(self, tone):
        if tone not in self.t:
            im = Image.new("L", self.cv.img.size, 0); self.t[tone] = (im, ImageDraw.Draw(im))
        return self.t[tone][1]

    def _px(self, pts):
        """Polygon points in supersampled px; a layer with plane=("ground", k) is squashed to y/x = k about the layer's anchor."""
        ss, pl = self.ss, getattr(self.c.layer, "plane", None)
        if pl: k, oy = pl[1], self.c.o[1]; return [(x * ss, (oy + (y - oy) * k) * ss) for x, y in pts]
        return [(x * ss, y * ss) for x, y in pts]

    def add(self, tone, pts):
        if len(pts) >= 3: self._d(tone).polygon(self._px(pts), fill=255)

    def cut(self, tone, pts):
        if len(pts) >= 3 and tone in self.t: self._d(tone).polygon(self._px(pts), fill=0)

    def mask(self, tone):
        return np.asarray(self.t[tone][0]) > 127 if tone in self.t else np.zeros(self.cv.img.size[::-1], bool)

    def set(self, tone, m):
        im = Image.fromarray((m * 255).astype(np.uint8), "L"); self.t[tone] = (im, ImageDraw.Draw(im))

    def smoothed(self, tone, smooth=None):
        """The mask of `tone` through `smooth_mask`; smooth None = this Ink's setting. Fillet and burr are in px of a size-1 effect: they scale with c.s."""
        m = self.mask(tone)
        smooth = self.smooth if smooth is None else smooth
        if smooth is False or not m.any(): return m
        kw = dict(smooth) if isinstance(smooth, dict) else {}
        k = max(0.5, min(2.0, float(self.c.s)))
        for key, v in (("fillet", 2.0), ("burr", 1.0), ("sigma", 0.8)): kw[key] = kw.get(key, v) * k
        return smooth_mask(m, self.ss, **kw)

    def paint(self, order, glow=1.0, opacity=None, smooth=None):
        """Composite the tones onto the layer's canvas in `order` = [(tone, rgb), ...] bottom to top, each one flat colour.
        opacity = {tone: 0..1} for see-through tones (smoke, veils). glow = how strongly this layer feeds the effect's glow
        (0 = none: smoke, dust, debris). smooth: None = this Ink's setting (see __init__); the tones are smoothed first and an inner tone
        that lay inside the first tone stays inside it."""
        H, W = self.cv.img.size[1], self.cv.img.size[0]
        rgb_ = np.zeros((H, W, 3), np.float32); al = np.zeros((H, W), np.float32); union = np.zeros((H, W), bool)
        first = None
        for tone, rgb in order:
            m = self.smoothed(tone, smooth)
            if first is None: first = (self.mask(tone), m)
            elif m.any() and not (self.mask(tone) & ~first[0]).any(): m = m & first[1]
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
