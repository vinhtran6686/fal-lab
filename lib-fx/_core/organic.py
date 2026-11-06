"""lib-fx organic shapes: hand-drawn looking silhouettes instead of circles and triangles (DESIGN.md §8).

The method:
  1. build ONE mask from many parts (curved tapered thorns, wobbly blobs, crescents), unioned; holes are cut separately;
  2. round the concave corners (morphological closing via two distance transforms) so thorns grow out of the body with soft
     fillets while their tips stay sharp;
  3. colour by distance to the edge (distance transform): thin parts stay in the outer bands (orange-red tips), thick parts reach
     the inner ones (white core): the bands follow the silhouette like a hand-painted inner glow, no outline;
  4. dissolve by noisy erosion (keep only pixels deeper than e(t) + noise): thin parts go first, thorns break into droplets;
  5. a dark, see-through backing a few px wider sits behind the bright shape for contrast on any background.
Animation moves the parts and the thresholds (cooling = the white band shrinks; erosion = the shape breaks up).
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

SPARK = dict(tip=(206, 70, 18), rim=(236, 122, 18), body=(250, 168, 30), light=(255, 210, 70), core=(255, 240, 170),
             white=(255, 254, 242), back=(150, 52, 10))
DUST = dict(shadow=(112, 116, 104), base=(166, 170, 150), light=(208, 212, 188), high=(234, 236, 218), curl=(132, 136, 122),
            back=(92, 96, 86))

_NOISE = {}


def spark_bands(pal=SPARK, s=1.0, heat=1.0):
    """Edge -> centre colour bands (distance from the edge in canvas px). heat 1 = fresh (wide white core), 0 = cooled."""
    k = s * (0.6 + 0.4 * heat)
    return [(1.3 * s, pal["tip"]), (3.6 * k, pal["rim"]), (6.4 * k, pal["body"]), (9.5 * k, pal["light"]),
            (13.5 * s / max(0.2, heat), pal["core"]), (None, pal["white"])]


def noise_field(shape, seed, scale):
    """Smooth value noise in -1..1, cached per (size, seed, scale)."""
    key = (shape, seed, round(scale, 1))
    if key not in _NOISE:
        rng = np.random.default_rng(seed)
        n = ndimage.gaussian_filter(rng.standard_normal(shape).astype(np.float32), scale)
        _NOISE[key] = n / (np.abs(n).max() + 1e-6)
    return _NOISE[key]


class Shape:
    """A mask drawn at the canvas's supersampled size, then painted into the canvas."""

    def __init__(self, canvas):
        self.c, self.ss = canvas, canvas.ss
        self.m = Image.new("L", canvas.img.size, 0)
        self.d = ImageDraw.Draw(self.m)
        self.h = None

    def poly(self, pts, on=True):
        if len(pts) >= 3:
            self.d.polygon([(x * self.ss, y * self.ss) for x, y in pts], fill=255 if on else 0)

    def ellipse(self, x, y, rx, ry, on=True):
        if rx > 0 and ry > 0:
            self.d.ellipse([(x - rx) * self.ss, (y - ry) * self.ss, (x + rx) * self.ss, (y + ry) * self.ss], fill=255 if on else 0)

    def line(self, pts, w):
        self.d.line([(x * self.ss, y * self.ss) for x, y in pts], fill=255, width=max(1, int(w * self.ss)), joint="curve")

    def hole(self, x, y, rx, ry):
        """A hole that does NOT count as an edge for the bands: the rim around it stays hot, like a punched ring."""
        if rx <= 0 or ry <= 0: return
        if self.h is None:
            self.h = Image.new("L", self.m.size, 0); self.hd = ImageDraw.Draw(self.h)
        self.hd.ellipse([(x - rx) * self.ss, (y - ry) * self.ss, (x + rx) * self.ss, (y + ry) * self.ss], fill=255)

    def mask(self, fillet=3.0, box=None):
        m0 = np.asarray(self.m) > 127
        if box is not None: m0 = m0[box]
        if not m0.any() or fillet <= 0: return m0
        r = fillet * self.ss                                              # closing: dilate then erode by the same radius
        dil = ndimage.distance_transform_edt(~m0) <= r
        return (ndimage.distance_transform_edt(dil) > r) | m0             # never lose a thin tip

    def paint(self, bands, a=1.0, fillet=3.0, erode=0.0, noise=0.0, seed=1, backing=None):
        """bands = [(max distance from the edge in px, colour), ..., (None, colour)]. erode (px) + noise (px) dissolve the shape;
        backing = (px, colour, alpha) draws a darker halo of the silhouette behind it."""
        if a <= 0.003: return
        bb = self.m.getbbox()                                             # work on the shape's box only (same pixels, much faster)
        if bb is None: return
        ss = self.ss
        pad = int(math.ceil((max(fillet, backing[0] if backing else 0.0) + 2) * ss))
        W, H = self.m.size
        x0, y0, x1, y1 = max(0, bb[0] - pad), max(0, bb[1] - pad), min(W, bb[2] + pad), min(H, bb[3] + pad)
        box = (slice(y0, y1), slice(x0, x1))
        m = self.mask(fillet, box)
        if not m.any(): return
        dist = ndimage.distance_transform_edt(m) / ss
        if erode > 0 or noise > 0:
            thr = erode + noise * noise_field((H, W), seed, 5 * ss)[box]
            m = m & (dist > thr)
            dist = dist - np.maximum(thr, 0)
            if not m.any(): return
        if self.h is not None:
            m = m & ~(np.asarray(self.h)[box] > 127)
        if backing:
            px, col, al = backing
            bk = ndimage.distance_transform_edt(~m) <= px * ss
            bimg = np.zeros(m.shape + (4,), np.uint8); bimg[bk] = tuple(col) + (int(255 * al * a),)
            self.c.img.alpha_composite(Image.fromarray(bimg, "RGBA"), (x0, y0))
        rgb = np.zeros(m.shape + (3,), np.uint8)
        left = m.copy()
        for lim, col in bands:
            sel = left if lim is None else (left & (dist <= lim))
            rgb[sel] = col
            left &= ~sel
        alpha = (m * (255 * min(1.0, a))).astype(np.uint8)
        self.c.img.alpha_composite(Image.fromarray(np.dstack([rgb, alpha]), "RGBA"), (x0, y0))


# ---------------------------------------------------------------- parts (all in canvas px)
def thorn(x, y, ang, L, W, bend=0.0, p=1.5, sy=1.0, n=18):
    """A curved, tapered thorn from its base (x, y) along angle ang, L long, W wide at the base. bend curls the tip (radians at
    the tip); p > 1 makes the flanks concave (a sharp, hand-drawn spike); sy squashes it vertically (ground perspective)."""
    left, right = [], []
    px, py = x, y
    for i in range(n + 1):
        s = i / n
        a = ang + bend * s * s
        if i:
            px += math.cos(a) * L / n; py += math.sin(a) * L / n * sy
        w = W / 2 * (1 - s) ** p
        nx, ny = -math.sin(a), math.cos(a) * sy
        left.append((px + nx * w, py + ny * w)); right.append((px - nx * w, py - ny * w))
    return left + right[::-1]


def shard(x, y, ang, L, W, bend=0.0, sy=1.0, n=12):
    """A flying droplet / sliver: round head at (x, y), tail tapering back against `ang` (the direction it flies)."""
    pl, pr = [], []
    px, py = x, y
    for i in range(n + 1):
        s = i / n
        a = ang + math.pi + bend * s
        if i:
            px += math.cos(a) * L / n; py += math.sin(a) * L / n * sy
        w = W / 2 * (1 - s) ** 1.2
        nx, ny = -math.sin(a), math.cos(a) * sy
        pl.append((px + nx * w, py + ny * w)); pr.append((px - nx * w, py - ny * w))
    head = [(x + math.cos(ang + t) * W / 2, y + math.sin(ang + t) * W / 2 * sy) for t in np.linspace(math.pi / 2, -math.pi / 2, 9)]
    return pl[::-1] + head + pr


def blob(x, y, r, sy=1.0, wob=0.08, freq=3, phase=0.0, n=48):
    """A wobbly round body."""
    return [(x + r * (1 + wob * math.sin(freq * t + phase) + wob * 0.5 * math.sin((freq + 2) * t + phase * 1.7)) * math.cos(t),
             y + r * sy * (1 + wob * math.sin(freq * t + phase)) * math.sin(t)) for t in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def crescent(x, y, rxo, rxi, ry, d=1, n=40):
    """A crescent standing across the x axis, bulging towards d: outer half-ellipse rxo, inner rxi (may be negative), height 2*ry."""
    o = [(x + d * rxo * math.cos(t), y + ry * math.sin(t)) for t in np.linspace(-math.pi / 2, math.pi / 2, n)]
    i = [(x + d * rxi * math.cos(t), y + ry * math.sin(t)) for t in np.linspace(math.pi / 2, -math.pi / 2, n)]
    return o + i


def ring_halves(x, y, rx, ry, w, n=72, taper=0.0):
    """An elliptical ring as two half bands (no self-overlap). taper > 0 thins it towards the top and bottom (a ring seen edge-on)."""
    halves = []
    for t0, t1 in ((-math.pi / 2, math.pi / 2), (math.pi / 2, 3 * math.pi / 2)):
        ts = np.linspace(t0, t1, n // 2)
        ww = [w / 2 * (1 - taper * abs(math.sin(t)) ** 2) for t in ts]
        o = [(x + (rx + q) * math.cos(t), y + (ry + q) * math.sin(t)) for t, q in zip(ts, ww)]
        i = [(x + max(0.1, rx - q) * math.cos(t), y + max(0.1, ry - q) * math.sin(t)) for t, q in zip(ts[::-1], ww[::-1])]
        halves.append(o + i)
    return halves


# ---------------------------------------------------------------- animation drivers (shared by every burst-like effect)
def smooth(a, b, x):
    x = max(0.0, min(1.0, (x - a) / (b - a))); return x * x * (3 - 2 * x)


def out_back(x, k=1.70158):
    x = max(0.0, min(1.0, x)) - 1; return 1 + (k + 1) * x ** 3 + k * x ** 2


def out_cubic(x): return 1 - (1 - max(0.0, min(1.0, x))) ** 3


def thorns_at(sh, cx, cy, thorns, t, life, sy=1.0, t_grow=0.07, detach=0.5, keep=0.6, start=0.7, thin_by=0.8):
    """Thorns (ang, L, W, bend, r0[, delay]) of a burst: first drawing at `start` of full size, full size with an overshoot by
    t_grow, then they keep growing a little while they thin, shorten and slide off the body (becoming flying slivers)."""
    for th in thorns:
        ang, L, W, bend, r0 = th[:5]
        dl = th[5] if len(th) > 5 else 0.0
        tt = t - dl
        if tt < 0: continue
        u = tt / life
        g = start + (1 - start) * out_back(min(1.0, tt / t_grow)) + 0.15 * u
        off = smooth(0.4, 1.0, u)
        thin = 1 - thin_by * smooth(0.3, 1.0, u)
        r = r0 + L * detach * off
        Ll = L * g * (1 - (1 - keep) * off)
        if Ll < 1 or thin <= 0.02: continue
        sh.poly(thorn(cx + math.cos(ang) * r, cy + math.sin(ang) * r * sy, ang, Ll, W * thin, bend * (1 + 0.6 * off), sy=sy))


def shards_at(sh, cx, cy, shards, t, life, sy=1.0, g=0.0):
    """Flying droplets (ang, d0, speed, L, W, bend, delay): leave from d0 along ang with drag, shrink to nothing by `life`."""
    for ang, d0, sp, L, W, bend, dl in shards:
        tt = t - dl
        if tt <= 0 or tt >= life: continue
        k = 5.0
        dist = d0 + sp * (1 - math.exp(-k * tt)) / k
        x, y = cx + math.cos(ang) * dist, cy + math.sin(ang) * dist * sy + 0.5 * g * tt * tt
        sz = 1 - smooth(0.4, 1.0, tt / life)
        if sz > 0.05:
            sh.poly(shard(x, y, ang, L * (0.6 + 0.4 * sz), W * sz, bend, sy=sy))


def cloud(canvas, puffs, pal=DUST, a=1.0, light=(-0.55, -0.83), off=5.0, fillet=4.0, erode=0.0, noise=0.0, seed=3,
          tones=("shadow", "base", "light"), curls=True, holes=()):
    """A cartoon dust cloud: the union of wobbly puffs (x, y, r), shaded in flat tones by shifting the silhouette towards the light:
    the side away from the light gets the dark tone, the side facing it the light tone. Curl lines sit on the big puffs' shadow
    side. holes = [(x, y, rx, ry)] open the middle as it dissipates; erode + noise break it into wisps."""
    sh = Shape(canvas)
    for x, y, r in puffs:
        sh.poly(blob(x, y, r, wob=0.07, freq=4, phase=x * 0.37 + y * 0.11))
    for h in holes: sh.hole(*h)
    m = sh.mask(fillet)
    if not m.any() or a <= 0.003: return
    ss = canvas.ss
    dist = ndimage.distance_transform_edt(m) / ss
    if erode > 0 or noise > 0:
        thr = erode + noise * noise_field(m.shape, seed, 7 * ss)
        m = m & (dist > thr)
    if sh.h is not None:
        m = m & ~(np.asarray(sh.h) > 127)
    if not m.any(): return
    o = int(off * ss)
    lx, ly = light
    toward = np.roll(np.roll(m, int(round(-lx * o)), axis=1), int(round(-ly * o)), axis=0)      # silhouette moved away from the light
    away = np.roll(np.roll(m, int(round(lx * o * 1.6)), axis=1), int(round(ly * o * 1.6)), axis=0)
    shadow = m & ~toward                                                  # rim on the side away from the light
    lit = m & ~away                                                       # rim facing the light
    rgb = np.zeros(m.shape + (3,), np.uint8)
    rgb[m] = pal[tones[1]]
    rgb[lit] = pal[tones[2]]
    rgb[shadow] = pal[tones[0]]
    img = Image.fromarray(np.dstack([rgb, (m * 255 * min(1, a)).astype(np.uint8)]), "RGBA")
    if curls:
        cd = ImageDraw.Draw(img)
        for x, y, r in puffs:
            if r < 10: continue
            pts = [(x + r * 0.55 * math.cos(t) * (0.55 + 0.12 * t), y + r * 0.5 * math.sin(t) * (0.55 + 0.12 * t)) for t in np.linspace(0.3, 3.4, 16)]
            cd.line([(px * ss, py * ss) for px, py in pts], fill=tuple(pal["curl"]) + (int(200 * a),), width=max(1, int(1.6 * ss)), joint="curve")
        arr = np.asarray(img).copy(); arr[~m] = 0; img = Image.fromarray(arr, "RGBA")
    canvas.img.alpha_composite(img)


def shade(sh, pal, a=1.0, light=(-0.35, -0.94), off=4.0, fillet=4.0, erode=0.0, noise=0.0, seed=3, tones=("shadow", "base", "light")):
    """Paint any Shape (puffs, thorns, wisps) as flat toon smoke: base tone, the side facing the light in the light tone, the side away
    from it in the shadow tone (the silhouette shifted towards / away from the light, as in cloud()). Works on the shape's box only."""
    if a <= 0.003: return
    bb = sh.m.getbbox()
    if bb is None: return
    ss = sh.ss
    pad = int(math.ceil((fillet + off * 1.6 + 2) * ss))
    W, H = sh.m.size
    x0, y0, x1, y1 = max(0, bb[0] - pad), max(0, bb[1] - pad), min(W, bb[2] + pad), min(H, bb[3] + pad)
    box = (slice(y0, y1), slice(x0, x1))
    m = sh.mask(fillet, box)
    if not m.any(): return
    if erode > 0 or noise > 0:
        dist = ndimage.distance_transform_edt(m) / ss
        m = m & (dist > erode + noise * noise_field((H, W), seed, 6 * ss)[box])
    if sh.h is not None:
        m = m & ~(np.asarray(sh.h)[box] > 127)
    if not m.any(): return
    o = int(off * ss)
    lx, ly = light
    toward = np.roll(np.roll(m, int(round(-lx * o)), axis=1), int(round(-ly * o)), axis=0)
    away = np.roll(np.roll(m, int(round(lx * o * 1.6)), axis=1), int(round(ly * o * 1.6)), axis=0)
    rgb = np.zeros(m.shape + (3,), np.uint8)
    rgb[m] = pal[tones[1]]
    rgb[m & ~away] = pal[tones[2]]
    rgb[m & ~toward] = pal[tones[0]]
    sh.c.img.alpha_composite(Image.fromarray(np.dstack([rgb, (m * 255 * min(1.0, a)).astype(np.uint8)]), "RGBA"), (x0, y0))


def spline(pts, k=6):
    """A closed Catmull-Rom curve through pts: rounds a hand-placed silhouette."""
    out, n = [], len(pts)
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        for j in range(k):
            u = j / k; u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * (2 * b + (-a + c) * u + (2 * a - 5 * b + 4 * c - e) * u2 + (-a + 3 * b - 3 * c + e) * u3)
                             for a, b, c, e in zip(p0, p1, p2, p3)))
    return out


def flame(x, y, ang, L, W, bend=0.0, wave=0.0, p=1.15, n=22):
    """A flame tongue from its base (x, y): like organic.thorn but its spine can sway in an S (wave) as well as curl (bend)."""
    left, right = [], []
    px, py = x, y
    for i in range(n + 1):
        s = i / n
        a = ang + bend * s * s + wave * math.sin(1.6 * math.pi * s)
        if i:
            px += math.cos(a) * L / n; py += math.sin(a) * L / n
        w = W / 2 * (1 - s) ** p * (0.75 + 0.25 * math.sin(math.pi * min(1.0, s * 2.2)))
        nx, ny = -math.sin(a), math.cos(a)
        left.append((px + nx * w, py + ny * w)); right.append((px - nx * w, py - ny * w))
    return left + right[::-1]
