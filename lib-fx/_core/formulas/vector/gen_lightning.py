"""gen_lightning: NEW lightning effects built from the lightning formula (lib-fx/_core/formulas/rules/vfx/lightning/README.md
§5, §7), with colours and glow measured on the lightning-2 remake. Created, not rebuilt: no reference frame is copied.

Style "crackle" (user 2026-11-28, third round: a character gathering power, lightning around it; earlier versions were too
regular, "lightning is a random element", it went below the ground, and the remake's black strokes behind the bolts were
missing). How it is built:
  anchors   every bolt starts ON the body outline (sides and top, never under the feet) and either jumps back to it (crawl, wrap)
            or out into the air (jump); nothing goes below the floor line (y is clamped). Electricity hugs the body instead of
            forming a regular shell.
  kinds     crawl: both ends on one side, bulging outward 0.10-0.35 H; wrap: side to side across the body, in front (70 %) or
            behind; jump: from the body outward 0.3-0.7 H with 1-2 short fingers (branches); spark: short crawl near the feet.
  chance    every drawing is decided by a seeded random process, not a schedule: new bolts ~ Poisson(1.7 x I + 0.25) with bursts of
            3-5 (22 %), each bolt lives 2-5 drawings (random), some drawings are blank strobes, some are held 2 frames, glow
            flickers 0.75-1.3 per drawing. I = charge intensity (rises, stays, falls, all with noise); reach of the bolts grows with I.
  dark      every bolt has a dark copy behind it (navy-black, wider, offset down-right): the shadow line that makes the bright
            stroke pop; about 1 in 8 bolts of 3+ drawings shows one INK drawing (the bolt drawn black inside a strong glow),
            the inverse frame measured on lightning-2 (strike 12, bolt 0).
  stroke    ~1.1 px at game size (body H = 60), pointed tips, folds every ~0.07 H with 2-5x length variation, bowed segments,
            fold points re-jittered every drawing; a bolt ends by breaking into claws in place (formula §5.4).
Invented: anchors on the body, the kinds, the random process, the shadow offset, the faint charging glow behind the body.

Outputs (lib-fx/_core/results/vector-showcase/generated/<name>/): frames/NN.png (@2x, stand-in body, preview only), back/NN.png and
front/NN.png (@2x RGBA, effect only), svg/NN.svg, sketch.png, preview.gif (@1x, body H = 120 px, real holds, 10 empty frames
before it restarts), preview_game.gif (body H = 60 px), preview_slow.gif, design.json (params, per-drawing log, checks)."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
from . import compose
from .dummy import BODY
from .profile import REPO

REF_LEN = 540.0
ARC = dict(core=(255, 255, 255), edge=(101, 197, 248), halo=([2.42, 28.21], [[-2.6, 71.9, 309.4], [-28.3, 74.1, 260.0]]))  # lightning-2 arc
INK_HALO = ([22.5], [[12.1, 277.0, 445.6]])                                                                       # lightning-2 bolt ink
SHADOW = (6, 8, 22)
STYLES = {
    "crackle": dict(D=48, tail=10, fps=24, H=240, canvas=(2.4, 1.9), feet=1.75, body_w=0.36, game_H=60, w_game=1.1,
                    glow=1.8, centre_glow=0.22, fold_px=0.085, amp=0.032, spawn=1.7, burst=0.22, strobe=0.07, hold=0.18,
                    ink=0.12, shadow=dict(offset=(0.006, 0.010), widen=1.7, add=0.010, alpha=0.9),
                    kinds=dict(crawl=0.40, wrap=0.22, jump=0.28, spark=0.10)),
}
BG = (24, 25, 33)
FLOOR = (52, 54, 68)


def intensity(st, rng):
    """Charge curve with noise: rises over 35 %, stays, falls from 70 % to 96 % (the end thins out, it does not cut)."""
    D = st["D"]
    out = []
    for f in range(D):
        u = f / (D - 1)
        base = min(1.0, (u / 0.35) ** 0.8) if u < 0.70 else max(0.0, 1 - (u - 0.70) / 0.26) ** 1.2
        out.append(float(np.clip(base * rng.uniform(0.75, 1.15), 0, 1)))
    return out


class Body:
    def __init__(self, st, W):
        H = st["H"]
        self.H, self.fy = H, st["feet"] * H
        self.x0, self.x1 = W / 2 - st["body_w"] * H / 2, W / 2 + st["body_w"] * H / 2
        self.y0 = self.fy - H
        self.c = np.array([W / 2, self.fy - 0.5 * H])

    def side(self, r, side=None, lo=0.0, hi=1.0):
        """A point on the body outline: side -1 left, 1 right, 0 top; v along the side (0 = top, 1 = feet)."""
        side = r.choice([-1, 1, -1, 1, 0]) if side is None else side
        if side == 0:
            return np.array([r.uniform(self.x0, self.x1), self.y0]), np.array([0.0, -1.0]), side
        v = r.uniform(lo, hi)
        return np.array([self.x1 if side > 0 else self.x0, self.y0 + v * self.H]), np.array([float(side), 0.0]), side


def _bezier(a, c, b, n=60):
    u = np.linspace(0, 1, n)[:, None]
    return (1 - u) ** 2 * a + 2 * (1 - u) * u * c + u ** 2 * b


class Bolt:
    def __init__(self, kind, birth, life, reach, body, st, rng):
        self.kind, self.birth, self.life, self.st, self.body = kind, birth, life, st, body
        self.seed = int(rng.integers(1 << 30))
        r = np.random.default_rng(self.seed)
        H = body.H
        self.depth, self.fingers = 1, []
        if kind == "crawl":
            a, n, sd = body.side(r)
            b = a + (np.array([r.uniform(-0.5, 0.5), 0]) * H if sd == 0 else np.array([0, r.choice([-1, 1]) * r.uniform(0.2, 0.5) * H]))
            b[0] = np.clip(b[0], body.x0, body.x1) if sd == 0 else b[0]
            c = (a + b) / 2 + n * r.uniform(0.10, 0.35) * H * reach
        elif kind == "wrap":
            a, _, _ = body.side(r, -1, 0.05, 0.85)
            b, _, _ = body.side(r, 1, 0.05, 0.85)
            if r.random() < 0.5:
                a, b = b, a
            c = (a + b) / 2 + [0, r.uniform(-0.15, 0.15) * H]
            self.depth = 1 if r.random() < 0.7 else -1
        elif kind == "jump":
            a, n, sd = body.side(r, None, 0.0, 0.8)
            ang = np.arctan2(n[1], n[0]) + r.uniform(-0.9, 0.9)
            d = np.array([np.cos(ang), np.sin(ang)])
            b = a + d * r.uniform(0.3, 0.7) * H * reach
            c = (a + b) / 2 + np.array([-d[1], d[0]]) * r.uniform(-0.12, 0.12) * H
            self.fingers = [dict(t=r.uniform(0.35, 0.8), turn=r.choice([-1, 1]) * r.uniform(0.4, 0.8), L=r.uniform(0.25, 0.45))
                            for _ in range(int(r.integers(1, 3)))]
        else:                                                    # spark near the feet, along the floor
            sd = r.choice([-1, 1])
            a = np.array([body.x1 if sd > 0 else body.x0, body.fy - r.uniform(0.0, 0.12) * H])
            b = a + [sd * r.uniform(0.15, 0.35) * H, 0]
            b[1] = body.fy
            c = (a + b) / 2 + [0, -r.uniform(0.03, 0.10) * H]
        self.ctrl = (a, c, b)
        self.w = st["w_game"] * H / st["game_H"] * (0.75 if kind == "spark" else r.uniform(0.85, 1.25))
        self.ink_at = life - 2 if life >= 3 and r.random() < st["ink"] else None
        self.centres = r.permutation(np.linspace(0.12, 0.88, 5))

    def _zig(self, B, d, seed_add=0, amp_k=1.0):
        H, st = self.body.H, self.st
        seg = np.linalg.norm(np.diff(B, axis=0), axis=1)
        L = max(seg.sum(), 1.0)
        t = np.r_[0, np.cumsum(seg)] / L
        r = np.random.default_rng(self.seed + seed_add)
        n = max(2, int(round(L / (st["fold_px"] * H))))
        tf = np.r_[0, np.cumsum(r.dirichlet(np.full(n, 1.2)))]
        sign = np.where(np.arange(n + 1) % 2, 1.0, -1.0) * r.uniform(0.4, 1.0, n + 1)
        sign[0] = sign[-1] = 0
        jr = np.random.default_rng(self.seed * 31 + d + seed_add)
        amp = st["amp"] * H * amp_k * min(1.0, L / (0.4 * H)) ** 0.5
        off = sign * amp * jr.uniform(0.6, 1.4, n + 1)                       # every drawing redrawn: folds move
        tan = np.gradient(B, axis=0)
        nrm = np.stack([-tan[:, 1], tan[:, 0]], 1) / np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-6)
        k = np.clip(np.searchsorted(tf, t, side="right") - 1, 0, n - 1)
        loc = (t - tf[k]) / np.maximum(tf[k + 1] - tf[k], 1e-6)
        bow = np.sin(np.pi * loc) * 0.25 * amp * np.where(k % 2, 1, -1)
        P = B + nrm * (np.interp(t, tf, off) + bow)[:, None]
        P[:, 1] = np.minimum(P[:, 1], self.body.fy - 0.014 * H)               # never below the floor (half a stroke above it)
        return P, t

    def elements(self, f):
        d = f - self.birth
        if d < 0 or d >= self.life:
            return []
        P, t = self._zig(_bezier(*self.ctrl), d)
        taper = np.clip(np.minimum(t / 0.15, (1 - t) / 0.2), 0, 1) ** 0.7
        r = np.random.default_rng(self.seed + 5)
        w = self.w * taper * (1 + 0.5 * np.exp(-((t - r.uniform(0.3, 0.7)) / 0.1) ** 2))
        last, ink = d == self.life - 1, d == self.ink_at
        if d == 0 and self.life >= 4:                            # big bolts grow in from the anchor (wedge drawing, thin)
            m = t <= 0.6
            ww = w[m] * np.clip((1 - t[m] / 0.6) / 0.3, 0, 1) ** 0.7
            return [dict(pts=P[m], w=ww, depth=self.depth, ink=False)]
        if last:                                                 # break into claws in place
            out = []
            n = int(np.random.default_rng(self.seed + 9).integers(2, 5))
            for c in self.centres[:n]:
                m = (t >= c - 0.09) & (t <= c + 0.09)
                if m.sum() >= 3:
                    tt = (t[m] - (c - 0.09)) / 0.18
                    out.append(dict(pts=P[m], w=0.9 * self.w * np.clip(np.minimum(tt, 1 - tt) / 0.3, 0, 1) ** 0.8, depth=self.depth, ink=False))
            return out
        out = [dict(pts=P, w=w * (0.75 if d >= 2 else 1.0), depth=self.depth, ink=ink)]
        for i, fg in enumerate(self.fingers):                    # short branches ("fingers") off the main bolt
            j = int(np.argmin(abs(t - fg["t"])))
            tan = P[min(j + 1, len(P) - 1)] - P[max(j - 1, 0)]
            tan /= max(np.linalg.norm(tan), 1e-6)
            rot = np.array([[np.cos(fg["turn"]), -np.sin(fg["turn"])], [np.sin(fg["turn"]), np.cos(fg["turn"])]])
            L = fg["L"] * np.linalg.norm(self.ctrl[2] - self.ctrl[0])
            B = P[j] + np.outer(np.linspace(0, 1, 16), rot @ tan * L)
            Q, tq = self._zig(B, d, 100 + i, 0.6)
            out.append(dict(pts=Q, w=0.7 * self.w * np.clip((1 - tq) / 0.8, 0, 1) ** 0.8, depth=self.depth, ink=ink))
        return out


def _raster(elems, shape, ss=4, key="w", shift=(0, 0)):
    """Union of tapered polylines: per-segment quads + a disc at every vertex (no self-intersection at folds)."""
    H, W = shape
    im = Image.new("L", (W * ss, H * ss), 0)
    dr = ImageDraw.Draw(im)
    for e in elems:
        P, w = (e["pts"] + shift) * ss, e[key] * ss / 2
        for i in range(len(P) - 1):
            d = P[i + 1] - P[i]
            nrm = np.array([-d[1], d[0]]) / max(np.linalg.norm(d), 1e-6)
            q = [P[i] + nrm * w[i], P[i + 1] + nrm * w[i + 1], P[i + 1] - nrm * w[i + 1], P[i] - nrm * w[i]]
            dr.polygon([tuple(x) for x in q], fill=255)
        for p, r in zip(P, w):
            if r > ss * 0.3:
                dr.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=255)
    return np.asarray(im.resize((W, H), Image.BOX), float) / 255


def _layer(elems, shape, st, k, glow_x, extra_glow=None):
    """One depth layer -> (glow, fill, alpha). Order inside: glow, dark shadow lines, bright fills (ink fills black)."""
    H, W = shape
    glow = np.zeros((H, W, 3)) if extra_glow is None else extra_glow.copy()
    fill, alpha = np.zeros((H, W, 3)), np.zeros((H, W))
    if not elems:
        return glow, fill, alpha
    bright = [e for e in elems if not e["ink"]]
    ink = [e for e in elems if e["ink"]]
    if bright:
        sil = _raster(bright, shape)
        glow += sum(ndi.gaussian_filter(sil, s * k)[..., None] * np.array(c, float) for s, c in zip(*ARC["halo"])) * glow_x
    if ink:
        sil = _raster(ink, shape)
        glow += sum(ndi.gaussian_filter(sil * 2.2, s * k)[..., None] * np.array(c, float) for s, c in zip(*INK_HALO)) * glow_x
    sh, H0 = st["shadow"], st["H"]
    for e in elems:
        e["ws"] = e["w"] * sh["widen"] + sh["add"] * H0
    sc = _raster(elems, shape, key="ws", shift=(sh["offset"][0] * H0, sh["offset"][1] * H0)) * sh["alpha"]
    fill = fill * (1 - sc[..., None]) + np.array(SHADOW, float) * sc[..., None]
    alpha = np.maximum(alpha, sc)
    for group, colour in ((bright, None), (ink, (0, 0, 0))):
        if not group:
            continue
        cov = _raster(group, shape)
        col = (np.zeros((H, W, 3)) + colour) if colour else compose.layer_colour(cov >= 0.5, ARC["core"], dict(edge=ARC["edge"], s=1.6))
        fill = fill * (1 - cov[..., None]) + col * cov[..., None]
        alpha = np.maximum(alpha, cov)
    return np.clip(glow, 0, None), fill, alpha


def _rgba(glow, fill, alpha):
    ag = np.clip(glow.max(-1) / 255.0, 0, 1)
    A = alpha + ag * (1 - alpha)
    P = np.clip(glow, 0, 255) * (1 - alpha[..., None]) + fill * alpha[..., None]
    rgb = np.where(A[..., None] > 1e-4, P / np.maximum(A[..., None], 1e-4), 0)
    return np.dstack([np.clip(rgb, 0, 255), A * 255]).astype(np.uint8)


def _svg(elems, shape):
    H, W = shape
    g = {-1: [], 1: []}
    for e in elems:
        P, w = e["pts"], e["w"] / 2
        nrm = np.gradient(P, axis=0)[:, ::-1] * [-1, 1]
        nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-6)
        ring = np.r_[P + nrm * w[:, None], (P - nrm * w[:, None])[::-1]]
        g[e["depth"]].append(f'<path fill="{"#000000" if e["ink"] else "#ffffff"}" d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in ring) + ' Z"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<g id="back">{"".join(g[-1])}</g><g id="front">{"".join(g[1])}</g></svg>')


def plan(st, body, seed):
    """The random process: per drawing, new bolts (Poisson or a burst), strobe blanks, holds, glow flicker."""
    r = np.random.default_rng(seed)
    I = intensity(st, r)
    kinds, probs = list(st["kinds"]), np.array(list(st["kinds"].values()))
    bolts, log, quiet = [], [], 0
    D = st["D"]
    for f in range(D):
        n = 0
        if I[f] > 0.05 and f < D - 3:
            n = int(r.integers(3, 6)) if r.random() < st["burst"] * I[f] else int(r.poisson(st["spawn"] * I[f] + 0.25))
            if n == 0 and quiet >= 2 and I[f] > 0.4:
                n = 1                                            # no more than two quiet drawings while charged
        for _ in range(n):
            life = int(min(r.choice([2, 3, 3, 4, 5]) if I[f] > 0.3 else r.choice([2, 2, 3]), D - 1 - f))
            if life >= 1:
                bolts.append(Bolt(r.choice(kinds, p=probs / probs.sum()), f, life, 0.5 + 0.5 * I[f], body, st, r))
        quiet = quiet + 1 if n == 0 else 0
        log.append(dict(drawing=f, I=round(I[f], 2), new=n, strobe=bool(0.2 < I[f] and r.random() < st["strobe"]),
                        hold=2 if r.random() < st["hold"] else 1, glow=round(float(r.uniform(0.75, 1.3)), 2)))
    return bolts, log


def build(name, style="crackle", seed=3, out_root=None):
    st = STYLES[style]
    H = st["H"]
    W, Hc = int(st["canvas"][0] * H), int(st["canvas"][1] * H)
    body = Body(st, W)
    k = 1.4 * H / REF_LEN
    bolts, log = plan(st, body, seed)
    out = Path(out_root) if out_root else REPO / "lib-fx/_core/results/vector-showcase/generated" / name
    for sub in ("frames", "back", "front", "svg"):
        (out / sub).mkdir(parents=True, exist_ok=True)
        for p in (out / sub).glob("*"):
            p.unlink()
    fy = int(body.fy)
    rect = (int(body.x0), int(body.y0), int(body.x1), fy)
    yy, xx = np.mgrid[0:Hc, 0:W]
    rr = np.sqrt(((xx - body.c[0]) / (0.45 * H)) ** 2 + ((yy - body.c[1]) / (0.6 * H)) ** 2)
    frames, lines = [], []
    for f, lg in enumerate(log):
        elems = [] if lg["strobe"] else [e for b in bolts for e in b.elements(f)]
        cg = np.exp(-rr ** 2)[..., None] * np.array(ARC["halo"][1][1], float) * st["centre_glow"] * lg["I"] * lg["glow"]
        img = np.zeros((Hc, W, 3)) + np.array(BG, float)
        img[fy:fy + 2] = FLOOR
        layers = {}
        for dep in (-1, 1):
            g, fi, a = _layer([e for e in elems if e["depth"] == dep], (Hc, W), st, k, st["glow"] * lg["glow"], cg if dep == -1 else None)
            layers[dep] = (g, fi, a)
            img = img * (1 - a[..., None]) + fi * a[..., None] + g * (1 - a[..., None])
            if dep == -1:
                img[rect[1]:rect[3], rect[0]:rect[2]] = BODY
        img = np.clip(img, 0, 255).astype(np.uint8)
        Image.fromarray(img).save(out / "frames" / f"{f:02d}.png")
        Image.fromarray(_rgba(*layers[-1])).save(out / "back" / f"{f:02d}.png")
        Image.fromarray(_rgba(*layers[1])).save(out / "front" / f"{f:02d}.png")
        (out / "svg" / f"{f:02d}.svg").write_text(_svg(elems, (Hc, W)))
        lines.append((_raster(elems, (Hc, W)) >= 0.5) if elems else np.zeros((Hc, W), bool))
        lg["parts"], lg["ink"] = len(elems), sum(e["ink"] for e in elems)
        frames.append(Image.fromarray(img))
    rest = np.zeros((Hc, W, 3)) + np.array(BG, float)
    rest[fy:fy + 2] = FLOOR
    rest[rect[1]:rect[3], rect[0]:rect[2]] = BODY
    rest = Image.fromarray(rest.astype(np.uint8))
    ms = round(1000 / st["fps"])
    seq, dur = frames + [rest], [ms * lg["hold"] for lg in log] + [ms * st["tail"]]
    half = [im.resize((W // 2, Hc // 2), Image.LANCZOS) for im in seq]
    half[0].save(out / "preview.gif", save_all=True, append_images=half[1:], duration=dur, loop=0)
    half[0].save(out / "preview_slow.gif", save_all=True, append_images=half[1:], duration=[3 * d for d in dur], loop=0)
    gk = st["game_H"] / H
    game = [im.resize((round(W * gk), round(Hc * gk)), Image.LANCZOS) for im in seq]
    game[0].save(out / "preview_game.gif", save_all=True, append_images=game[1:], duration=dur, loop=0)
    _sketch(out / "sketch.png", lines, log, rect, (Hc, W))
    check = _check(lines, log, fy, game[:-1])
    (out / "design.json").write_text(json.dumps(dict(style=style, seed=seed, params=st, bolts=len(bolts), drawings=log, check=check),
                                                indent=1, default=float))
    return out, check


def _sketch(path, lines, log, rect, shape):
    """Flat lines of three drawings (early, busiest, late) + the random charge curve with the bolts born per drawing."""
    H, W = shape
    D = len(log)
    picks = [max(2, D // 6), int(np.argmax([l.sum() for l in lines])), int(D * 0.8)]
    sh = Image.new("RGB", (W * 3, H + 170), (245, 245, 240))
    dr = ImageDraw.Draw(sh)
    for j, f in enumerate(picks):
        im = np.zeros((H, W, 3), np.uint8) + 245
        im[rect[1]:rect[3], rect[0]:rect[2]] = (190, 192, 200)
        im[rect[3]:rect[3] + 2] = (150, 150, 150)
        im[lines[f]] = (20, 40, 90)
        sh.paste(Image.fromarray(im), (j * W, 0))
        dr.text((j * W + 8, 8), f"drawing {f}  I {log[f]['I']}", fill=(20, 20, 20))
    x0, y0, cw, ch = 40, H + 25, W * 3 - 80, 120
    dr.rectangle([x0, y0, x0 + cw, y0 + ch], outline=(150, 150, 150))
    for f, lg in enumerate(log):
        x = x0 + cw * f / (D - 1)
        dr.rectangle([x - 3, y0 + ch - 12 * lg["new"], x + 3, y0 + ch], fill=(120, 160, 220))
        if lg["strobe"]:
            dr.text((x - 3, y0 + 2), "s", fill=(200, 60, 60))
    dr.line([(x0 + cw * f / (D - 1), y0 + ch - ch * lg["I"]) for f, lg in enumerate(log)], fill=(220, 120, 40), width=3)
    dr.text((x0 + 6, y0 - 16), "orange: charge intensity (with noise)   bars: bolts born   s: blank strobe drawing", fill=(20, 20, 20))
    sh.save(path)


def _check(lines, log, fy, game):
    below = int(sum(l[fy + 2:].sum() for l in lines))
    widths = []
    for im in game:
        a = np.asarray(im, float)
        m = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114 > 150
        sk = skeletonize(m)
        if sk.sum() > 20:
            widths.append(float(2 * ndi.distance_transform_edt(m)[sk].mean()))
    new = [lg["new"] for lg in log]
    return dict(line_px_below_floor=below, last_drawing_line_px=int(lines[-1].sum()),
                stroke_width_game_px=round(float(np.median(widths)), 2) if widths else None,
                bolts_born_per_drawing=new, strobes=[lg["drawing"] for lg in log if lg["strobe"]],
                held=[lg["drawing"] for lg in log if lg["hold"] == 2], ink_drawings=[lg["drawing"] for lg in log if lg.get("ink")])
