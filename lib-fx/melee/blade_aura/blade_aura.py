"""lib-fx / melee / blade_aura: light that lives ON a weapon blade (not a slash that leaves it).

charge_blue ("tu luc"): a source at the hilt ignites, a front of blue energy rises along the blade to the tip, then bright pulses keep running
hilt -> tip while the blade stays lit. It is meant to start BEFORE a skill and to carry on after it.

Two ways to use it:
  - standalone (lib-fx/build.py): VARIANTS["charge_blue"] draws it on a straight blade of 70 px, hilt at the anchor, tip towards +x;
  - on a character: `render()` takes the blade's own pixels (a mask) plus its root/tip per frame, so the light follows the real blade and
    never draws over the hands; `params_at()` and `make_sparks()` build the timeline. See docs/pipeline/pose-pair-fx-method.md §8.

Layers, back to front (rules: lib-fx/_core/formulas/rules/01-design-style.md, 02-animation.md):
  1. glow    air layer: the blurred lit blade in the main blue at two scales (the glow carries the main colour, it is not an outline);
  2. aura    two flat see-through bands hugging the lit blade (blue, then deep blue);
  3. body    the lit blade in 4 flat tiers (deep, blue, ice, white), the hottest tier deepest inside the blade and under the moving heads;
  4. tip     a small source at the hilt while it ignites (a four-point twinkle on the tip exists but is off by default);
  5. sparks  a few specks born on the lit blade, rising and shrinking, drawn on twos, never at regular spacing.
No gradients: every tier is flat, the soft parts are blurs of the shape itself.
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from fxcore import clamp, smooth

FPS = 30
FRAME, ANCHOR = (150, 90), (34, 45)
DUR = 2.0
TAGS = ["melee", "blade", "aura", "charge", "sustained", "blue", "anchor:hilt"]
PAL = dict(rim=(30, 90, 200), body=(70, 165, 255), light=(170, 225, 255), core=(235, 248, 255), white=(255, 255, 255),
           deep=(30, 90, 200), blue=(70, 165, 255), ice=(170, 225, 255))
PAL_SUN = PAL
TIERS = np.array([PAL["deep"], PAL["blue"], PAL["ice"], PAL["white"]], float)
CATALOG = {
    "charge_blue": dict(name="Tụ lực lưỡi đao (xanh)", status="approved", tags=["charge", "buff", "energy"], halo=(0.0, 8), palette=PAL,
                        desc="blue energy that gathers in a weapon: a source ignites at the hilt, a front rises along the blade to the tip, "
                             "then bright pulses keep running hilt to tip; discreet (it is a status); flat tiers (deep, blue, "
                             "ice, white), two see-through bands and a two-scale glow around the blade, a few rising specks drawn on twos; "
                             "it does not fade out, so it can run through a skill"),
}
BLADE_LEN = 70.0
BLADE_HW = 4.0

# the standalone timeline (seconds); a character passes its own (frames / fps)
DEFAULT_TL = dict(start=0.15, rise=0.65, pulses=[(1.0, 0.45, 0.9), (1.55, 0.4, 1.0)],
                  energy=[(0.15, 0.3), (0.8, 0.62), (1.6, 1.0), (2.0, 0.85)], flares=[], shimmer=dict(frm=1.6, amp=0.05, period=0.667),
                  spark_every=0.13, fps=FPS)


# ------------------------------------------------------------------ timeline
def params_at(t, tl):
    """State of the effect at time t: front (0..1 along the blade), heads [(position, strength)], energy E, tip and source strengths."""
    start, rise = tl["start"], tl["rise"]
    front = 0.0 if t < start else smooth(0.0, 1.0, (t - start) / rise)
    if tl.get("full_at") is not None and t >= tl["full_at"]:
        front = 1.0
    heads = [(front, 1.0)] if 0.0 < front < 1.0 else []
    for t0, dur, s in tl["pulses"]:
        u = (t - t0) / dur
        if 0.0 <= u <= 1.0:
            heads.append((u, s))
    keys = tl["energy"]
    E = keys[0][1] if t <= keys[0][0] else keys[-1][1] if t >= keys[-1][0] else next(
        a[1] + (b[1] - a[1]) * (t - a[0]) / (b[0] - a[0]) for a, b in zip(keys, keys[1:]) if a[0] <= t <= b[0])
    if t < start:
        E = 0.0
    for t0, s, dec in tl.get("flares", []):
        if t >= t0:
            E += s * math.exp(-(t - t0) / dec)
    sh = tl.get("shimmer")
    if sh and t >= sh["frm"]:
        E += sh["amp"] * math.sin(2 * math.pi * (t - sh["frm"]) / sh["period"])
    return dict(front=front, heads=heads, E=E, tip=clamp((front - 0.985) / 0.015) * clamp(E * 1.15), source=smooth(start - 0.05, start + 0.2, t) * (0.5 + 0.5 * clamp(E)))


def make_sparks(tl, seed, t_end):
    """Specks, each with its own birth time, life, place on the blade, speed and size (uneven on purpose: repeated spacing reads as a strip)."""
    rng = np.random.default_rng(seed)
    out, t = [], tl["start"] + 0.12
    while t < t_end:
        out.append(dict(t0=t, life=rng.uniform(0.35, 0.75), u=rng.uniform(0.06, 1.0), c=rng.uniform(-1.0, 1.0), sp=rng.uniform(14, 34),
                        r=rng.uniform(0.9, 1.9), side=rng.uniform(-0.6, 0.6)))
        t += rng.uniform(0.5, 1.5) * tl.get("spark_every", 0.13)
    return out


def sparks_at(sparks, t, tl, pose_at):
    """[(x, y, radius, alpha, tier)] in cell px at time t. pose_at(t0) -> (root, tip, half_width) of the blade when the speck was born.
    Time is held on twos (two frames per drawing); tl["cut"] kills every speck born before it (the blade is somewhere else after a cut)."""
    fps = tl.get("fps", FPS)
    tq = math.floor(t * fps / 2.0 + 1e-6) * 2.0 / fps
    out = []
    for s in sparks:
        f = (tq - s["t0"]) / s["life"]
        if not 0.0 <= f < 1.0:
            continue
        if tl.get("cut") is not None and s["t0"] < tl["cut"] <= tq:
            continue
        pre = params_at(s["t0"], tl)
        if s["u"] > pre["front"] or pre["E"] < 0.25:
            continue
        root, tip, hw = pose_at(s["t0"])
        root, tip = np.asarray(root, float), np.asarray(tip, float)
        L = float(np.hypot(*(tip - root))); d = (tip - root) / L; n = np.array([-d[1], d[0]])
        if n[1] > 0:
            n = -n
        up = np.array([0.0, -1.0])
        dd = n * (0.8 + s["side"]) + up * 0.6
        dd /= np.hypot(*dd)
        base = root + d * (s["u"] * L) + n * (s["c"] * hw)
        p = base + dd * s["sp"] * (tq - s["t0"])
        out.append((p[0], p[1], s["r"] * (1.0 - f) ** 0.7 + 0.35, 1.0 - f ** 2, 3 if f < 0.25 else 2 if f < 0.6 else 1))
    return out


# ------------------------------------------------------------------ drawing
def _over(base, top):
    a = top[..., 3:4]; b = base[..., 3:4]
    na = a + b * (1 - a)
    rgb = np.where(na > 1e-5, (top[..., :3] * a + base[..., :3] * b * (1 - a)) / np.maximum(na, 1e-5), 0)
    return np.dstack([rgb, na[..., 0]])


def _layer(col, alpha):
    return np.dstack([np.broadcast_to(np.asarray(col, float), alpha.shape + (3,)), np.clip(alpha, 0, 1)])


def _star(size, centre, along, across, rx, ry, ss, tw):
    """Four-point twinkle: two thin spikes (along the blade and across it), an ice halo and a white core."""
    im = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy = centre
    ax, ay = along; bx, by = across
    w = 0.9 * ss * (0.6 + 0.4 * tw)
    for k, col, al in ((1.0, PAL["blue"], 215), (0.62, PAL["ice"], 235)):          # outer blue spikes, shorter ice ones on top
        for (ux, uy), r in (((ax, ay), rx * k), ((bx, by), ry * k)):
            px, py = -uy, ux
            d.polygon([(cx + ux * r, cy + uy * r), (cx + px * w, cy + py * w), (cx - ux * r * 0.55, cy - uy * r * 0.55), (cx - px * w, cy - py * w)],
                      fill=tuple(col) + (round(al * tw),))
    rh = 2.6 * ss * (0.6 + 0.4 * tw); rc = 1.3 * ss * (0.6 + 0.4 * tw)
    d.ellipse([cx - rh, cy - rh, cx + rh, cy + rh], fill=tuple(PAL["blue"]) + (round(150 * tw),))
    d.ellipse([cx - rc, cy - rc, cx + rc, cy + rc], fill=(255, 255, 255, round(255 * tw)))
    return np.asarray(im, float) / np.array([1, 1, 1, 255.0])


def render(mask, arms, root, tip, st, ss, sparks=(), grow=False, strength=0.65, star=False):
    """RGBA float (H*ss, W*ss) of the effect on one blade. mask: blade coverage 0..1 at ss; arms: coverage of whatever is in front of the blade
    (hands, forearms: the light is not drawn over it); root/tip: hilt end and tip in cell px; st: params_at(); sparks: sparks_at(); strength: overall opacity of the effect (it is a status, so it stays discreet); star: the four-point twinkle on the tip (off by default); grow: widen the mask by about 1 px (a hand-drawn blade has an edge line outside its part polygon)."""
    Hs, Ws = mask.shape
    out = np.zeros((Hs, Ws, 4))
    if st["E"] <= 0.01 and not st["heads"] and st["front"] <= 0:
        return out
    r = np.asarray(root, float) * ss; tp = np.asarray(tip, float) * ss
    L = float(np.hypot(*(tp - r))); d = (tp - r) / L; n = np.array([-d[1], d[0]])
    pad = int(0.4 * L + 10 * ss)
    x0 = max(0, int(min(r[0], tp[0]) - pad)); x1 = min(Ws, int(max(r[0], tp[0]) + pad))
    y0 = max(0, int(min(r[1], tp[1]) - pad)); y1 = min(Hs, int(max(r[1], tp[1]) + pad))
    m = np.clip(mask[y0:y1, x0:x1], 0, 1); a = np.clip(arms[y0:y1, x0:x1], 0, 1)
    m = np.clip(ndi.gaussian_filter(m, 0.5 * ss) * 2.2, 0, 1) if grow else m
    yy, xx = np.mgrid[y0:y1, x0:x1]
    X = xx + 0.5 - r[0]; Y = yy + 0.5 - r[1]
    v = (X * d[0] + Y * d[1]) / L
    inside = m > 0.5
    if not inside.any():
        return out
    din = ndi.distance_transform_edt(inside)
    dn = np.clip(din / max(din.max(), 1.0), 0, 1)
    dout = ndi.distance_transform_edt(~inside) / ss                     # px outside the blade, in cell px
    E, front = st["E"], st["front"]
    vis = m * (1 - a)
    lead = 0.12 * (1 - dn)                                              # the edges trail the centre: the front is an arrow, not a ruler line
    lit = (v + lead <= front + 0.012).astype(float)

    # tiers: depth into the blade + energy + the heads that run along it (stepped, so each tier stays flat)
    val = 0.72 * dn + 0.34 * E
    for pos, s in st["heads"]:
        dq = pos - v - lead
        val = val + s * np.where(dq < 0, 0.0, np.where(dq < 0.07, 0.55, np.where(dq < 0.20, 0.30, np.where(dq < 0.38, 0.12, 0.0))))
    tier = np.digitize(val, [0.30, 0.60, 0.86])
    body_col = TIERS[tier]
    body_a = vis * lit * 0.93
    pre_a = vis * (v + lead > front + 0.012) * (v + lead <= front + 0.10) * (0.30 if 0.0 < front < 1.0 else 0.0)

    gE = clamp(E * 1.2)
    glow_src = vis * lit
    g1 = ndi.gaussian_filter(glow_src, 2.4 * ss) * 0.9
    g2 = ndi.gaussian_filter(glow_src, 7.5 * ss) * 0.6
    gk = (0.45 + 0.55 * clamp(E, 0, 1.3)) * (1 - 0.55 * a)
    gate = np.clip((front + 0.05 - v) / 0.12, 0, 1) * (v > -0.03) * (v < 1.07)
    ring1 = np.clip((1.5 - dout) / 0.7, 0, 1) * ~inside * gate * gE * 0.55 * (1 - a)
    ring2 = np.clip((3.4 - dout) / 0.7, 0, 1) * ~inside * (1 - np.clip((1.5 - dout) / 0.7, 0, 1)) * gate * gE * 0.30 * (1 - a)

    lay = np.zeros((y1 - y0, x1 - x0, 4))
    lay = _over(lay, _layer(PAL["deep"], g2 * gk))
    lay = _over(lay, _layer(PAL["blue"], g1 * gk))
    lay = _over(lay, _layer(PAL["deep"], ring2))
    lay = _over(lay, _layer(PAL["blue"], ring1))
    lay = _over(lay, _layer(PAL["deep"], pre_a))
    lay = _over(lay, np.dstack([body_col, np.clip(body_a, 0, 1)]))
    if st["source"] > 0.02:                                              # the source at the hilt, only on the visible blade
        sc = r + d * (0.035 * L)
        gem = np.hypot(xx + 0.5 - sc[0], yy + 0.5 - sc[1]) / ss
        hwp = max(din.max(), 1.0) / ss
        s = st["source"]
        lay = _over(lay, _layer(PAL["blue"], np.clip((2.2 * hwp - gem) / 1.0, 0, 1) * 0.5 * s * (1 - a)))
        lay = _over(lay, _layer(PAL["ice"], np.clip((1.5 * hwp - gem) / 1.0, 0, 1) * 0.85 * s * (1 - a)))
        lay = _over(lay, _layer(PAL["white"], np.clip((0.7 * hwp - gem) / 0.7, 0, 1) * s * (1 - a)))
    if star and st["tip"] > 0.02:
        tw = st["tip"]
        star = _star((x1 - x0, y1 - y0), (tp[0] - x0, tp[1] - y0), d, n, 0.2 * L * (0.6 + 0.4 * tw), 0.12 * L * (0.6 + 0.4 * tw), ss, tw)
        lay = _over(lay, np.dstack([star[..., :3] * 255.0, star[..., 3]]))
    if len(sparks):
        im = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
        for (sx, sy, rad, al, tr) in sparks:
            cx, cy, rr = sx * ss - x0, sy * ss - y0, rad * ss
            dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=tuple(int(c) for c in TIERS[tr]) + (round(255 * clamp(al)),))
        sp = np.asarray(im, float) / np.array([1, 1, 1, 255.0])
        lay = _over(lay, sp)
    lay[..., 3] *= strength
    out[y0:y1, x0:x1] = lay
    return out


def to_cell(rgba, ss):
    """Down-sample an ss-times RGBA float image with premultiplied colour (anti-aliased edge)."""
    H, W = rgba.shape[0] // ss, rgba.shape[1] // ss
    al = rgba[..., 3]
    pm = (rgba[..., :3] * al[..., None]).reshape(H, ss, W, ss, 3).mean(axis=(1, 3)); a = al.reshape(H, ss, W, ss).mean(axis=(1, 3))
    rgb = np.where(a[..., None] > 1e-4, pm / np.maximum(a[..., None], 1e-4), 0)
    return np.dstack([np.clip(rgb, 0, 255), np.clip(a, 0, 1) * 255]).round().astype(np.uint8)


# ------------------------------------------------------------------ standalone variant (library)
def _lens_mask(size, ss, root, tip, hw):
    """A straight lens-shaped blade (wide at the hilt, pointed at the tip) at ss times the cell size: the stand-in used by the library preview."""
    im = Image.new("L", (size[0] * ss, size[1] * ss), 0); dr = ImageDraw.Draw(im)
    r = np.asarray(root, float); tp = np.asarray(tip, float); L = float(np.hypot(*(tp - r))); d = (tp - r) / L; n = np.array([-d[1], d[0]])
    pts = []
    for sgn in (1, -1):
        for k in range(0, 21):
            u = k / 20 if sgn == 1 else 1 - k / 20
            w = hw * (1.0 - 0.35 * u) * min(1.0, (1.0 - u) / 0.15)
            pts.append(tuple((r + d * u * L + n * sgn * w) * ss))
    dr.polygon(pts, fill=255)
    return np.asarray(im, float) / 255.0


def charge_blue(t, P, front, back):
    tl = dict(DEFAULT_TL)
    ss = front.ss
    root = (P[0], P[1]); tip = (P[0] + BLADE_LEN, P[1])
    mask = _lens_mask(FRAME, ss, root, tip, BLADE_HW)
    st = params_at(t, tl)
    sp = sparks_at(make_sparks(tl, 7, DUR), t, tl, lambda t0: (root, tip, BLADE_HW))
    img = to_cell_ss(render(mask, np.zeros_like(mask), root, tip, st, ss, sp))
    front.img.alpha_composite(img)


def to_cell_ss(rgba):
    """Same array at supersampled size as a PIL RGBA image (the Canvas down-samples it itself)."""
    return Image.fromarray(np.dstack([np.clip(rgba[..., :3], 0, 255), np.clip(rgba[..., 3], 0, 1) * 255]).round().astype(np.uint8), "RGBA")


VARIANTS = {"charge_blue": charge_blue}
