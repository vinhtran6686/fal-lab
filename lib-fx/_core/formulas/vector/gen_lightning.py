"""gen_lightning: NEW lightning effects built from the lightning formula (lib-fx/_core/formulas/rules/vfx/lightning/README.md
§5), with the colours, widths and glows measured on the lightning-2 remake. Created, not rebuilt: no reference frame is copied.

Style "aura" (user 2026-11-28: a character charging a skill, lightning shown around and wrapping the body, character at the
centre): a loop of 24 drawings at 24 fps, staggered bolts so 1-2 are always alive.
  wrap bolts  (look of `arc`: white core -> blue edge, thin)  run along a tilted ring / helix around the body's vertical axis;
              depth = sin(theta) at every vertex, so each bolt is split into a BACK part (drawn before the body) and a FRONT part.
  rise bolts  (look of `bolt`: cyan core, thicker)             rise from the ground beside the feet, with the elliptical ground flash.
Every bolt runs the measured hit table: wedge (x2.6 wide, first 55 % of the path) -> contact -> thin x0.55 -> [ink frame, black
inside a strong glow] or thin x0.5 -> break into 3, 5, 7, 8 claw pieces in place (area x0.5-0.65 per drawing) -> gone. Each
drawing redraws the bolt on its own path with the fold points jittered (no interpolation). Glow is per bolt and grows as it
breaks (gain 1.0 -> 2.0, measured). All measured px (on a 540 px bolt) are scaled by k = aura height / 540.

Invented here (not in the reference): the helix paths around a body, the depth split, the 24-drawing schedule.

Outputs (lib-fx/_core/results/vector-showcase/generated/<name>/): frames/NN.png (@2x, with the stand-in body, preview only),
back/NN.png and front/NN.png (@2x RGBA, effect only: draw back, then the character, then front), svg/NN.svg (flat fills, back and
front groups), preview.gif (@1x, body H = 120 px), preview_game.gif (body H = 60 px), preview_slow.gif, design.json (params,
schedule, per-bolt stats checked against the formula)."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from . import compose
from .dummy import BODY
from .profile import REPO

REF_LEN = 540.0   # length of the measured bolts (lightning-2, 640 px frame)
LOOKS = {         # measured in lightning-2.json: flat core, edge tint + s, contact width (p50), shared glow tiers (sigma, rgb)
    "arc": dict(core=(255, 255, 255), edge=(101, 197, 248), s=8.45, w=15.0,
                halo=([2.42, 28.21], [[-2.6, 71.9, 309.4], [-28.3, 74.1, 260.0]])),
    "bolt": dict(core=(126, 230, 252), edge=(24, 147, 238), s=3.06, w=26.0,
                 halo=([2.67, 67.15], [[-94.0, 73.0, 290.3], [-3.2, 48.6, 200.0]])),
}
INK_HALO = ([22.5], [[12.1, 277.0, 445.6]])                     # bolt ink: own glow, wide tier (the narrow tier is mask-edge compensation)
FLASH = dict(core=(60, 255, 255), size=(80.0, 20.0), feather=2.5,
             halo=([[8.6, 36.0], [19.6, 74.9]], [[38.5, 270.8, 279.6], [-39.9, 275.2, 781.4]]))
# hit table (formula §3 / §5): span of the path drawn, width x, glow gain, ground flash
HIT = [dict(ph="wedge", span=(0.0, 0.55), w=2.6, gain=1.0, flash=True),
       dict(ph="contact", span=(0.0, 1.0), w=1.0, gain=1.0, flash=True),
       dict(ph="thin", span=(0.0, 1.0), w=0.55, gain=1.1, flash=False),
       dict(ph="thin2", span=(0.0, 1.0), w=0.5, gain=1.2, flash=False),       # becomes the ink frame when the bolt has ink=True
       dict(ph="break", keep=0.75, w=0.50, pieces=3, gain=1.3),
       dict(ph="break", keep=0.55, w=0.42, pieces=4, gain=1.5),
       dict(ph="break", keep=0.38, w=0.36, pieces=6, gain=1.8),
       dict(ph="break", keep=0.22, w=0.30, pieces=7, gain=2.0)]
STYLES = {
    # glow: x on the measured glow (a charging aura is brighter than the reference reel; invented). arc_w: wrap contact width
    # on the 540 px scale (measured arc p50 15; 18 keeps the broken claws >= 1.5 px at game size)
    "aura": dict(loop=24, fps=24, H=240, canvas=(2.6, 1.95), feet=1.72, body_w=0.36, aura_h=1.3, min_w_game=1.5, game_H=60,
                 glow=1.5, arc_w=18.0, ring=(0.50, 0.60), tilt=0.24,
                 bolts=[dict(kind="rise", start=0, side=-1, ink=True, depth=-1),
                        dict(kind="wrap", start=1, y=0.20, th0=200, dth=330, rise=0.40),
                        dict(kind="wrap", start=5, y=0.55, th0=-20, dth=300, rise=0.35),
                        dict(kind="wrap", start=8, y=0.35, th0=100, dth=320, rise=0.45),
                        dict(kind="rise", start=12, side=1, ink=False, depth=1),
                        dict(kind="wrap", start=13, y=0.62, th0=250, dth=300, rise=0.35),
                        dict(kind="wrap", start=17, y=0.25, th0=20, dth=330, rise=0.45),
                        dict(kind="wrap", start=20, y=0.50, th0=160, dth=310, rise=0.40)]),
}
BG = (24, 25, 33)
FLOOR = (52, 54, 68)


def _widths(t, W, rng):
    """Width along the path (t in 0..1): pointed ends, one or two bulges (p90 / p50 ~ 1.5-3, formula §4.2)."""
    taper = np.clip(np.minimum(t / 0.12, (1 - t) / 0.16), 0, 1) ** 0.7
    b = 1 + sum(a * np.exp(-((t - c) / 0.10) ** 2) for a, c in zip(rng.uniform(0.6, 1.4, 2), rng.uniform(0.2, 0.8, 2)))
    return W * taper * b / 1.3


def _densify(P, step=3.0):
    out, src = [P[0]], [0.0]
    for i in range(len(P) - 1):
        n = max(1, int(np.linalg.norm(P[i + 1] - P[i]) / step))
        for j in range(1, n + 1):
            out.append(P[i] + (P[i + 1] - P[i]) * j / n)
            src.append(i + j / n)
    return np.array(out), np.array(src)


class Bolt:
    def __init__(self, spec, geo, seed):
        self.s, self.g, self.seed = spec, geo, seed
        rng = np.random.default_rng(seed)
        H, cx, fy, k = geo["H"], geo["cx"], geo["fy"], geo["k"]
        self.look = LOOKS["bolt" if spec["kind"] == "rise" else "arc"]
        if spec["kind"] == "rise":       # from the ground beside the feet, up past the head; 3-4 big folds
            gx = cx + spec["side"] * rng.uniform(0.42, 0.55) * H
            L = geo["aura_h"] * H * rng.uniform(0.85, 1.0)
            n = int(rng.integers(3, 5))
            ts = np.linspace(0, 1, n + 1)
            lat = np.array([0] + [(-1) ** i * rng.uniform(0.07, 0.15) * L for i in range(1, n)] + [rng.uniform(-0.1, 0.1) * L])
            self.base = np.stack([gx + lat + spec["side"] * ts * 0.12 * H, fy - ts * L], 1)
            self.theta = None
            self.ground = (gx, fy)
        else:                            # tilted ring / helix around the body axis, depth = sin(theta)
            R, Ry = rng.uniform(*geo["ring"]) * H, geo["tilt"] * H
            n = int(rng.integers(6, 9))
            th = np.radians(spec["th0"] + np.linspace(0, spec["dth"], n + 1))
            u = np.linspace(0, 1, n + 1)
            rad = R * (1 + np.array([0] + [(-1) ** i * rng.uniform(0.08, 0.18) for i in range(1, n)] + [0]))
            yc = fy - spec["y"] * H
            self.base = np.stack([cx + rad * np.cos(th), yc - spec["rise"] * H * u + Ry * np.sin(th)
                                  + rng.normal(0, 0.02 * H, n + 1)], 1)
            self.theta = th
            self.ground = None
        self.W = (self.look["w"] if spec["kind"] == "rise" else geo["arc_w"]) * k
        self.wrng_seed = seed + 1000
        self.centres = np.random.default_rng(seed + 7).permutation(np.linspace(0.08, 0.92, 8))

    def path(self, d):
        """Redraw: fold points jittered 5-20 px (scaled), anchors fixed."""
        rng = np.random.default_rng(self.seed * 100 + d)
        P = self.base.copy()
        P[1:-1] += rng.normal(0, 12 * self.g["k"], P[1:-1].shape)
        return P

    def drawing(self, d, min_w):
        """Elements of hit drawing d (0..7): list of dict(pts, w, depth, ink, gain) + flash or None."""
        hp = HIT[d]
        P = self.path(d)
        D, src = _densify(P)
        t = np.r_[0, np.cumsum(np.linalg.norm(np.diff(D, axis=0), axis=1))]
        t /= t[-1]
        Wd = _widths(t, self.W, np.random.default_rng(self.wrng_seed))
        if self.theta is not None:
            depth = np.sin(np.interp(src, np.arange(len(self.theta)), self.theta))
        else:
            depth = np.full(len(D), float(self.s.get("depth", -1)))
        ink = hp["ph"] == "thin2" and self.s.get("ink")
        out = []
        if hp["ph"] != "break":
            a, b = hp["span"]
            m = (t >= a) & (t <= b)
            tt = (t[m] - a) / (b - a)
            w = Wd[m] * hp["w"]
            if b < 1:   # wedge: a broad smear from the source, ending in its own point
                w = hp["w"] * self.W * np.clip(tt / 0.1, 0, 1) ** 0.7 * np.clip(1 - tt, 0, 1) ** 0.6
            out += self._split(D[m], np.maximum(w, 0), depth[m], ink, hp["gain"])
        else:
            n, half = hp["pieces"], hp["keep"] / hp["pieces"] / 2
            for c in self.centres[:n]:
                m = (t >= c - half) & (t <= c + half)
                if m.sum() < 3:
                    continue
                tt = (t[m] - (c - half)) / (2 * half)
                claw = np.clip(np.minimum(tt / 0.3, (1 - tt) / 0.3), 0, 1) ** 0.8      # piece pointed at both ends
                w = np.maximum(np.interp(c, t, Wd) * hp["w"], min_w) * claw
                out += self._split(D[m], w, depth[m], False, hp["gain"])
        flash = None
        if self.ground is not None and hp.get("flash"):
            flash = dict(c=self.ground, depth=float(self.s.get("depth", -1)))
        return out, flash

    @staticmethod
    def _split(pts, w, depth, ink, gain):
        """Cut where depth changes sign (one vertex overlap) -> back / front parts."""
        out, i0 = [], 0
        sgn = np.where(depth >= 0, 1, -1)
        for i in range(1, len(pts) + 1):
            if i == len(pts) or sgn[i] != sgn[i0]:
                j = min(i + 1, len(pts))
                if j - i0 >= 2:
                    out.append(dict(pts=pts[i0:j], w=w[i0:j], depth=int(sgn[i0]), ink=ink, gain=gain))
                i0 = i
        return out


def _raster(elems, shape, ss=4):
    """Coverage of a union of tapered polylines: per-segment quads + a disc at every vertex (no self-intersection at folds)."""
    H, W = shape
    im = Image.new("L", (W * ss, H * ss), 0)
    dr = ImageDraw.Draw(im)
    for e in elems:
        P, w = e["pts"] * ss, e["w"] * ss / 2
        for i in range(len(P) - 1):
            d = P[i + 1] - P[i]
            nrm = np.array([-d[1], d[0]]) / max(np.linalg.norm(d), 1e-6)
            q = [P[i] + nrm * w[i], P[i + 1] + nrm * w[i + 1], P[i + 1] - nrm * w[i + 1], P[i] - nrm * w[i]]
            dr.polygon([tuple(x) for x in q], fill=255)
        for p, r in zip(P, w):
            if r > ss * 0.3:
                dr.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=255)
    return np.asarray(im.resize((W, H), Image.BOX), float) / 255


def _glow(sil, sig, cols):
    return sum(ndi.gaussian_filter(sil, s)[..., None] * np.array(c, float) for s, c in zip(sig, cols))


def _ellipse(shape, c, size, feather):
    H, W = shape
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - c[0]) / (size[0] / 2)) ** 2 + ((yy - c[1]) / (size[1] / 2)) ** 2)
    return ndi.gaussian_filter((r <= 1).astype(float), feather)


def _layer(elems, flashes, shape, geo):
    """One depth layer -> (glow rgb, fill rgb, fill alpha)."""
    H, W = shape
    k = geo["k"]
    glow = np.zeros((H, W, 3))
    fill = np.zeros((H, W, 3))
    alpha = np.zeros((H, W))
    for look_name, look in LOOKS.items():
        es = [e for e in elems if e["look"] == look_name]
        if not es:
            continue
        sil = np.zeros((H, W))
        for e in es:
            cov = _raster([e], shape)
            e["cov"] = cov
            sil = np.maximum(sil, cov * e["gain"] * (0.0 if e["ink"] else 1.0))
        glow += _glow(sil, [s * k for s in look["halo"][0]], look["halo"][1]) * geo["glow"]
    ink = np.zeros((H, W))
    for e in elems:
        if e["ink"]:
            ink = np.maximum(ink, e["cov"])
    if ink.any():
        glow += _glow(ink * 2.0, [s * k for s in INK_HALO[0]], INK_HALO[1])
    for f in flashes:
        m = _ellipse(shape, f["c"], [x * k * 1.4 for x in FLASH["size"]], FLASH["feather"])
        glow += sum(ndi.gaussian_filter(m, tuple(x * k for x in s))[..., None] * np.array(c, float)
                    for s, c in zip(*FLASH["halo"]))
        fill = fill * (1 - m[..., None]) + np.array(FLASH["core"], float) * m[..., None]
        alpha = np.maximum(alpha, m)
    for e in elems:
        cov = e["cov"]
        look = LOOKS[e["look"]]
        col = np.zeros((H, W, 3)) if e["ink"] else compose.layer_colour(cov >= 0.5, look["core"], dict(edge=look["edge"], s=look["s"] * k))
        fill = fill * (1 - cov[..., None]) + col * cov[..., None]
        alpha = np.maximum(alpha, cov)
    return np.clip(glow, 0, None), fill, alpha


def _svg(elems, shape):
    H, W = shape
    g = {-1: [], 1: []}
    for e in elems:
        L = LOOKS[e["look"]]
        col = "#000000" if e["ink"] else "#%02x%02x%02x" % L["core"]
        P, w = e["pts"], e["w"] / 2
        nrm = np.gradient(P, axis=0)[:, ::-1] * [-1, 1]
        nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-6)
        ring = np.r_[P + nrm * w[:, None], (P - nrm * w[:, None])[::-1]]
        g[e["depth"]].append(f'<path fill="{col}" d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in ring) + ' Z"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<g id="back">{"".join(g[-1])}</g><g id="front">{"".join(g[1])}</g></svg>')


def _rgba(glow, fill, alpha):
    """Effect alone on transparency: glow as light (alpha = its brightness), fills over it."""
    ag = np.clip(glow.max(-1) / 255.0, 0, 1)
    A = alpha + ag * (1 - alpha)
    P = np.clip(glow, 0, 255) * (1 - alpha[..., None]) + fill * alpha[..., None]
    rgb = np.where(A[..., None] > 1e-4, P / np.maximum(A[..., None], 1e-4), 0)
    return np.dstack([np.clip(rgb, 0, 255), A * 255]).astype(np.uint8)


def build(name, style="aura", seed=3, out_root=None):
    st = STYLES[style]
    H = st["H"]
    W, Hc = int(st["canvas"][0] * H), int(st["canvas"][1] * H)
    geo = dict(H=H, cx=W / 2, fy=st["feet"] * H, aura_h=st["aura_h"], k=st["aura_h"] * H / REF_LEN, glow=st["glow"],
               arc_w=st["arc_w"], ring=st["ring"], tilt=st["tilt"])
    min_w = st["min_w_game"] * H / st["game_H"]               # thinnest piece still >= 1.5 px at game size
    bolts = [Bolt(b, geo, seed * 37 + i) for i, b in enumerate(st["bolts"])]
    out = Path(out_root) if out_root else REPO / "lib-fx/_core/results/vector-showcase/generated" / name
    for sub in ("frames", "back", "front", "svg"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    bw, bh = st["body_w"] * H, H
    body = (int(geo["cx"] - bw / 2), int(geo["fy"] - bh), int(geo["cx"] + bw / 2), int(geo["fy"]))
    stats = {i: [] for i in range(len(bolts))}
    frames = []
    for f in range(st["loop"]):
        elems, flashes = [], []
        for i, b in enumerate(bolts):
            d = (f - b.s["start"]) % st["loop"]
            if d >= len(HIT):
                continue
            es, fl = b.drawing(d, min_w)
            for e in es:
                e["look"] = "bolt" if b.s["kind"] == "rise" else "arc"
                e["bolt"] = i
            elems += es
            if fl:
                flashes.append(fl)
            cov = _raster(es, (Hc, W)) if es else np.zeros((Hc, W))
            lab, n = ndi.label(cov >= 0.5)
            stats[i].append(dict(frame=f, phase=HIT[d]["ph"] + ("/ink" if HIT[d]["ph"] == "thin2" and b.s.get("ink") else ""),
                                 area=int((cov >= 0.5).sum()), pieces=int(n)))
        img = np.zeros((Hc, W, 3)) + np.array(BG, float)
        img[int(geo["fy"]):int(geo["fy"]) + 2] = FLOOR
        layers = {}
        for dep in (-1, 1):
            g, fi, a = _layer([e for e in elems if e["depth"] == dep], [x for x in flashes if x["depth"] == dep], (Hc, W), geo)
            layers[dep] = (g, fi, a)
            img = img + g
            img = img * (1 - a[..., None]) + fi * a[..., None]
            if dep == -1:
                img[body[1]:body[3], body[0]:body[2]] = BODY
        img = np.clip(img, 0, 255).astype(np.uint8)
        Image.fromarray(img).save(out / "frames" / f"{f:02d}.png")
        Image.fromarray(_rgba(*layers[-1])).save(out / "back" / f"{f:02d}.png")
        Image.fromarray(_rgba(*layers[1])).save(out / "front" / f"{f:02d}.png")
        (out / "svg" / f"{f:02d}.svg").write_text(_svg(elems, (Hc, W)))
        vis = sum(int((l[2] >= 0.5).sum()) for l in layers.values())
        frames.append((Image.fromarray(img), vis))
    ms = round(1000 / st["fps"])
    big = [im.resize((W // 2, Hc // 2), Image.LANCZOS) for im, _ in frames]
    big[0].save(out / "preview.gif", save_all=True, append_images=big[1:], duration=ms, loop=0)
    big[0].save(out / "preview_slow.gif", save_all=True, append_images=big[1:], duration=ms * 3, loop=0)
    g = st["game_H"] / H
    game = [im.resize((round(W * g), round(Hc * g)), Image.LANCZOS) for im, _ in frames]
    game[0].save(out / "preview_game.gif", save_all=True, append_images=game[1:], duration=ms, loop=0)
    check = _check(stats, [v for _, v in frames])
    (out / "design.json").write_text(json.dumps(dict(style=style, seed=seed, params=st, k=round(geo["k"], 3), min_w_px=min_w,
                                                     hit_table=HIT, bolts=stats, check=check), indent=1, default=float))
    return out, check


def _check(stats, visible):
    """Formula §5: pieces 3-12 when broken, area kept per drawing 0.4-0.8 while breaking, every frame shows something."""
    rows = []
    for i, s in stats.items():
        br = [r for r in s if r["phase"] == "break"]
        ratios = [round(b["area"] / a["area"], 2) for a, b in zip(br, br[1:]) if a["area"]]
        rows.append(dict(bolt=i, max_pieces=max((r["pieces"] for r in br), default=0), break_area_ratios=ratios))
    return dict(bolts=rows, min_visible_px=int(min(visible)), empty_frames=[f for f, v in enumerate(visible) if v < 200])
