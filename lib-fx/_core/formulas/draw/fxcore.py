"""lib-fx core: the drawing kit every effect in the library is built from (no effect lives here).
Look: smooth supersampled shapes, flat tones in 3-4 steps with a dark rim of the same hue, soft glow; never pixel art, never dither.
"""
import colorsys, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- basics
class Canvas:
    """Supersampled RGBA layer; shapes in cell px, flat fills."""
    def __init__(self, w, h, ss=3):
        self.w, self.h, self.ss = w, h, ss
        self.img = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def poly(self, pts, rgb, a=1.0):
        if len(pts) >= 3 and a > 0.003:
            self.d.polygon([(x * self.ss, y * self.ss) for x, y in pts], fill=tuple(rgb) + (round(255 * min(1, a)),))

    def ellipse(self, x, y, rx, ry, rgb, a=1.0):
        if a > 0.003 and rx > 0 and ry > 0:
            self.d.ellipse([(x - rx) * self.ss, (y - ry) * self.ss, (x + rx) * self.ss, (y + ry) * self.ss], fill=tuple(rgb) + (round(255 * min(1, a)),))

    def line(self, p, q, w, rgb, a=1.0):
        if a > 0.003:
            self.d.line([(p[0] * self.ss, p[1] * self.ss), (q[0] * self.ss, q[1] * self.ss)], fill=tuple(rgb) + (round(255 * min(1, a)),), width=max(1, round(w * self.ss)))

    def paste(self, other): self.img.alpha_composite(other.img)
    def done(self): return self.img.resize((self.w, self.h), Image.LANCZOS)


def tone(c, light):
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
    l = max(0.0, min(1.0, l * light if light < 1 else l + (1 - l) * (light - 1)))
    return tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s))


def mix(a, b, k): return tuple(round(x + (y - x) * k) for x, y in zip(a, b))
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def smooth(a, b, x): x = clamp((x - a) / (b - a)); return x * x * (3 - 2 * x)
def out_cubic(x): return 1 - (1 - clamp(x)) ** 3
def env(t, t0, up, hold, down):
    u = t - t0
    if u < 0: return 0.0
    return smooth(0, up, u) * (1 - smooth(up + hold, up + hold + down, u))
def lin(a, b, n): return [a + (b - a) * i / (n - 1) for i in range(n)]


def halo(img, rgb, a, blur=10):
    """Soft light under a layer: a blurred copy of its alpha tinted rgb, composited beneath it."""
    if a <= 0: return img
    al = img.getchannel("A").filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(min(255, v * a)))
    g = Image.new("RGBA", img.size, tuple(rgb) + (0,)); g.putalpha(al)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(img)
    return out


def glow_under(dst, src, passes):
    """Soft light from the alpha of canvas `src`, composited onto canvas `dst` (put it on the layer behind): passes =
    [(rgb, alpha, blur px), ...], widest first. Unlike the build-level halo it glows only what you pass it, at several scales."""
    al0 = src.img.getchannel("A")
    for rgb, a, blur in passes:
        if a <= 0: continue
        al = al0.filter(ImageFilter.GaussianBlur(blur * src.ss)).point(lambda v, a=a: int(min(255, v * a)))
        g = Image.new("RGBA", src.img.size, tuple(rgb) + (0,)); g.putalpha(al)
        dst.img.alpha_composite(g)


# ---------------------------------------------------------------- shapes
def lune(c, cx, cy, rxo, rxi, ry, col, a, d=1, ryi=None, n=36):
    """Crescent between two half-ellipses through (cx, cy +- ry): bulges rxo towards d, its inner edge rxi (rxi < rxo; may be negative)."""
    ryi = ry if ryi is None else ryi
    out = [(cx + d * rxo * math.cos(th), cy + ry * math.sin(th)) for th in lin(-math.pi / 2, math.pi / 2, n)]
    inn = [(cx + d * rxi * math.cos(th), cy + ryi * math.sin(th)) for th in lin(math.pi / 2, -math.pi / 2, n)]
    c.poly(out + inn, col, a)


def lune_shaded(c, cx, cy, rxo, rxi, ry, pal, a, d=1):
    """A crescent in four flat steps: dark rim, body, light, and a thin hot core hugging the leading edge."""
    th = rxo - rxi
    lune(c, cx, cy, rxo + 1.5, rxi - 1.0, ry + 1.8, pal["rim"], a, d, ry + 0.6)
    lune(c, cx, cy, rxo, rxi, ry, pal["body"], a, d)
    lune(c, cx, cy, rxo - th * 0.12, rxi + th * 0.38, ry * 0.96, pal["light"], a, d)
    lune(c, cx, cy, rxo - th * 0.16, rxo - th * 0.42, ry * 0.9, pal["core"], a, d)


def band(c, cx, cy, rx, ry, w, col, a, th0=0.0, th1=2 * math.pi, n=48, taper=False):
    """A stroke along an ellipse from angle th0 to th1, w wide (optionally pointed at both ends)."""
    ts = lin(th0, th1, n)
    o, i = [], []
    for k, th in enumerate(ts):
        ww = w * (max(0.0, math.sin(math.pi * k / (n - 1))) ** 0.7 if taper else 1) / 2
        o.append((cx + (rx + ww) * math.cos(th), cy + (ry + ww) * math.sin(th)))
        i.append((cx + max(0, rx - ww) * math.cos(th), cy + max(0, ry - ww) * math.sin(th)))
    c.poly(o + i[::-1], col, a)


def lens(c, p0, p1, w, col, a, n=14):
    """A pointed lens (leaf) from p0 to p1, w at its widest."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
    side1, side2 = [], []
    for k in range(n + 1):
        v = k / n; hw = w / 2 * max(0.0, math.sin(math.pi * v)) ** 0.85
        x, y = p0[0] + dx * v, p0[1] + dy * v
        side1.append((x + nx * hw, y + ny * hw)); side2.append((x - nx * hw, y - ny * hw))
    c.poly(side1 + side2[::-1], col, a)


def ribbon(c, pts, widths, col, a):
    """A strip through pts with a width per point."""
    if len(pts) < 2: return
    L, R = [], []
    for k, (x, y) in enumerate(pts):
        p, q = pts[max(0, k - 1)], pts[min(len(pts) - 1, k + 1)]
        dx, dy = q[0] - p[0], q[1] - p[1]; l = math.hypot(dx, dy) or 1; nx, ny = -dy / l, dx / l
        L.append((x + nx * widths[k] / 2, y + ny * widths[k] / 2)); R.append((x - nx * widths[k] / 2, y - ny * widths[k] / 2))
    c.poly(L + R[::-1], col, a)


def twinkle(c, x, y, r, pal, a):
    """A small four-point glint."""
    if r <= 0.3 or a <= 0: return
    for (dx, dy) in ((1, 0), (0, 1)):
        lens(c, (x - dx * r * 1.6, y - dy * r * 1.6), (x + dx * r * 1.6, y + dy * r * 1.6), r * 0.7, pal["core"], a, 8)
    c.ellipse(x, y, r * 0.45, r * 0.45, pal["white"], a)


def font(size):
    for f in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf", "DejaVuSans.ttf"):
        try: return ImageFont.truetype(f, size)
        except OSError: pass
    return ImageFont.load_default()


# ---------------------------------------------------------------- motion
def out_back(x, k=1.70158):
    """Ease out with a small overshoot (goes past 1, settles back): punchy growth."""
    x = clamp(x) - 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


def out_expo(x): return 1.0 if x >= 1 else 1 - 2 ** (-10 * clamp(x))


def drag_pos(x0, y0, vx, vy, u, k=4.0, g=0.0):
    """Where a particle is u seconds after leaving (x0, y0) at (vx, vy), slowed by drag k, pulled down by g. Returns x, y, vx, vy."""
    f = (1 - math.exp(-k * u)) / k
    e = math.exp(-k * u)
    return x0 + vx * f, y0 + vy * f + 0.5 * g * u * u, vx * e, vy * e + g * u


# ---------------------------------------------------------------- layered shapes
def stepped_glow(c, x, y, r, pal, a, sy=1.0):
    """A glow in flat steps (our look has no gradients): three nested discs, wide and faint to small and hot."""
    if a <= 0.003 or r <= 0.5: return
    for k, col, al in ((1.0, pal["light"], 0.16), (0.68, pal["light"], 0.3), (0.42, pal["core"], 0.6), (0.2, pal["white"], 0.9)):
        c.ellipse(x, y, r * k, r * k * sy, col, a * al)


def starburst(c, x, y, r, n, pal, a, rot=0.0, seed=1, thin=1.0, sy=1.0):
    """A flash of pointed rays: long and short alternate, each ray in three passes (rim, light body, white core)."""
    if a <= 0.003 or r <= 1: return
    import random
    rng = random.Random(seed)
    rays = [(rot + (i + rng.uniform(-0.18, 0.18)) / n * 2 * math.pi, (1.0 if i % 2 == 0 else 0.55) * rng.uniform(0.85, 1.1)) for i in range(n)]
    for wk, lk, col in ((1.5, 1.06, pal["rim"]), (1.0, 1.0, pal["light"]), (0.45, 0.7, pal["white"])):
        for ang, ln in rays:
            L = r * ln * lk
            lens(c, (x, y), (x + math.cos(ang) * L, y + math.sin(ang) * L * sy), r * 0.2 * thin * wk * (0.6 + 0.4 * ln), col, a)


def spark(c, x, y, vx, vy, L, w, col, a, core=None):
    """A streak: round hot head at (x, y), tapering back along the velocity over L."""
    if a <= 0.003: return
    sp = math.hypot(vx, vy) or 1
    ux, uy = vx / sp, vy / sp
    nx, ny = -uy, ux
    tail = (x - ux * L, y - uy * L)
    c.poly([(x + nx * w / 2, y + ny * w / 2), (x + ux * w * 0.5, y + uy * w * 0.5), (x - nx * w / 2, y - ny * w / 2), tail], col, a)
    if core is not None and w > 1.2:
        c.poly([(x + nx * w / 4, y + ny * w / 4), (x + ux * w * 0.25, y + uy * w * 0.25), (x - nx * w / 4, y - ny * w / 4),
                (x - ux * L * 0.45, y - uy * L * 0.45)], core, a)


def arc3d(fc, bc, cx, cy, R, w, pal, a, sq=0.4, th0=0.0, th1=2 * math.pi, d=1, taper=False, hot=0.0, far=0.7, near_only=False):
    """A band along a ring standing across the x axis, seen three-quarters. Angle 0 points ahead (+x * d) and is NEAR the viewer.
    The near half is wider, brighter and goes on `fc`; the far half is thinner, darker and goes on `bc` (behind a character).
    Flat tones in steps: the ring is cut in short chunks, each with its own tone; drawn in passes (rim, body, highlight) per half so
    no outline ever crosses a neighbouring body."""
    if a <= 0.003 or R <= 0.5 or w <= 0.1: return
    span = th1 - th0
    n = max(8, int(abs(span) * R / 3.2))
    ths = [th0 + span * i / n for i in range(n + 1)]
    def pt(th, r): return (cx + d * r * math.cos(th) * sq, cy + r * math.sin(th))
    wl = []
    for i, th in enumerate(ths):
        near = (math.cos(th) + 1) / 2
        wl.append(w * (0.5 + 0.5 * near) * (max(0.0, math.sin(math.pi * i / n)) ** 0.6 if taper else 1))
    chunks, i = [], 0
    while i < n:
        j = min(n, i + 4)
        for k in range(i + 1, j + 1):
            if (math.cos(ths[k]) >= 0) != (math.cos(ths[i]) >= 0): j = k; break
        mid = ths[(i + j) // 2]
        chunks.append((i, j, math.cos(mid) >= 0, (math.cos(mid) + 1) / 2))
        i = j
    def band(i, j, r_out, r_in):
        e = 0.006                                                       # a hair of overlap: no seams between chunks
        idx = range(i, j + 1)
        o = [pt(ths[k] + (-e if k == i else e if k == j else 0), r_out(k)) for k in idx]
        n_ = [pt(ths[k] + (-e if k == i else e if k == j else 0), r_in(k)) for k in idx]
        return o + n_[::-1]
    for isnear in (False, True):
        if near_only and not isnear: continue
        c = fc if isnear else bc
        al = a if isnear else a * far
        mine = [ch for ch in chunks if ch[2] == isnear]
        for i, j, _, nr in mine:
            c.poly(band(i, j, lambda k: R + wl[k] / 2 + 1.2, lambda k: R - wl[k] / 2 - 1.2), pal["rim"], al)
        for i, j, _, nr in mine:
            col = mix(pal["body"], pal["light"], nr) if isnear else mix(pal["rim"], pal["body"], 0.45 + 0.4 * nr)
            c.poly(band(i, j, lambda k: R + wl[k] / 2, lambda k: R - wl[k] / 2), col, al)
        if isnear:
            for i, j, _, nr in mine:
                col = mix(mix(pal["light"], pal["core"], nr), pal["white"], hot)
                c.poly(band(i, j, lambda k: R + wl[k] * 0.42, lambda k: R + wl[k] * 0.04), col, al)
                if nr > 0.7:
                    c.poly(band(i, j, lambda k: R + wl[k] * 0.33, lambda k: R + wl[k] * 0.2), pal["white"], al * (nr - 0.7) / 0.3)


# ---------------------------------------------------------------- previews
def save_gif(frames, path, fps, hold=400):
    """Write RGB frames as a GIF with ONE palette for the whole animation and no dither: flat colours stay flat and a colour does
    not shimmer from frame to frame (a palette per frame gives every frame slightly different tones). hold = ms on the last frame."""
    frames = [f.convert("RGB") for f in frames]
    pick = sorted({round(i * (len(frames) - 1) / 23) for i in range(24)}) if len(frames) > 24 else range(len(frames))
    w, h = frames[0].size; k = min(1.0, 320 / max(w, h))
    tw, th = max(1, round(w * k)), max(1, round(h * k))
    mosaic = Image.new("RGB", (tw * len(pick), th))
    for j, i in enumerate(pick): mosaic.paste(frames[i].resize((tw, th), Image.BOX), (j * tw, 0))
    pal = mosaic.quantize(255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    out[0].save(path, save_all=True, append_images=out[1:], duration=[round(1000 / fps)] * (len(out) - 1) + [hold], loop=0)
