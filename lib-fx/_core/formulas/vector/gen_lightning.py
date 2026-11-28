"""gen_lightning: NEW lightning effects built from the lightning formula (lib-fx/_core/formulas/rules/vfx/lightning/README.md
§5, §7), with colours and glow measured on the lightning-2 remake. Created, not rebuilt: no reference frame is copied.

Style "charge" (user 2026-11-28: a character gathering power at the centre; the lightning wraps the whole body as ONE shape,
thin fine strokes, grows to a maximum size, then shrinks and fades out). Design, in the order it was decided (silhouette and
rhythm first, colour and glow last):
  shell     every bolt lies on one ellipsoid around the body (radii 0.56 H x 0.80 H at peak, seen slightly from above); no
            standalone vertical bolt. Depth = cos(phi) sin(theta) per vertex: back parts are drawn before the body, front after.
  roles     rim primaries run along the projected outline of the shell (they ARE the silhouette, long, with one fork);
            swirls are helix arcs on the shell, all flowing the same way (around and upward, 30-50 deg), 80 % behind the body,
            front crossings few and thinner (x0.6); sparks are short bolts on the rim. Hierarchy 1 / 0.4-0.7 / < 0.25 (rules/01).
  envelope  one global curve: grow (ease-out, shell 0.3 -> 1) -> hold (breathing +-3 %) -> shrink (1 -> 0.55) with fade; it drives
            shell size, spawn rate, glow and opacity. Paths scale with the shell; WIDTHS stay in absolute px (thin at every size)
            and the fold count follows the path length (fixed fold spacing), so a small shell has short bolts with few folds.
  stroke    ~1.1 px at game size (body H = 60), swell <= 1.6x at 1-2 folds, pointed tips; neighbouring segments differ 2-5x in
            length, each slightly bowed, 2-4 real kinks + fine jitter (straight equal segments read stiff).
  hit       each bolt keeps the measured table: grow in from one end (2 drawings) -> full, redrawn with jittered folds (2) ->
            thin -> break into claws in place (3 drawings) -> gone; its glow rises as it breaks (1.0 -> 1.9, measured).
Invented (not in the reference): the shell and its roles, the envelope, the forks, glow x1.6, the soft charging glow behind the
body. The black ink frame and the ground flash of the lightning-2 bolts are left out.

Outputs (lib-fx/_core/results/vector-showcase/generated/<name>/): frames/NN.png (@2x, stand-in body, preview only), back/NN.png and
front/NN.png (@2x RGBA, effect only: back, then the character, then front), svg/NN.svg, sketch.png (flat lines at start / peak /
end + the envelope curve), preview.gif (@1x, body H = 120 px; 10 empty frames before it restarts), preview_game.gif (body
H = 60 px), preview_slow.gif, design.json (params, envelope, per-frame stats, checks)."""
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
STYLES = {
    "charge": dict(D=44, tail=10, fps=24, H=240, canvas=(2.4, 2.1), feet=1.86, body_w=0.36,
                   shell=(0.56, 0.80), centre=0.52, tilt=0.18, game_H=60, w_game=1.1, glow=1.6, centre_glow=0.3,
                   grow=0.33, hold=0.62, shrink_to=0.55, fold_px=0.16, amp=0.028, swirl_rate=0.9, spark_rate=0.6,
                   back_share=0.8, front_w=0.6, min_piece=0.05),
}
BG = (24, 25, 33)
FLOOR = (52, 54, 68)
LIFE = [dict(ph="in", span=0.5, w=1.0, gain=1.0), dict(ph="in", span=1.0, w=1.0, gain=1.0),
        dict(ph="full", w=1.0, gain=1.0), dict(ph="full", w=1.0, gain=1.0), dict(ph="thin", w=0.7, gain=1.1),
        dict(ph="break", keep=0.7, pieces=3, gain=1.3), dict(ph="break", keep=0.45, pieces=4, gain=1.6),
        dict(ph="break", keep=0.22, pieces=5, gain=1.9)]


def envelope(st):
    """Per drawing: shell scale s and intensity I (grow ease-out -> hold -> shrink ease-in with fade)."""
    D, g, h = st["D"], st["grow"], st["hold"]
    out = []
    for f in range(D):
        u = f / (D - 1)
        if u < g:
            x = u / g
            s, I = 0.3 + 0.7 * (1 - (1 - x) ** 2.2), 0.35 + 0.65 * (1 - (1 - x) ** 2)
        elif u < h:
            s, I = 1 + 0.03 * np.sin((u - g) / (h - g) * 2 * np.pi * 2), 1.0
        else:
            x = (u - h) / (1 - h)
            s, I = 1 - (1 - st["shrink_to"]) * x ** 1.6, max(0.0, 1 - x ** 1.3)
        out.append((round(float(s), 3), round(float(I), 3)))
    return out


class Shell:
    def __init__(self, st, H, W):
        self.cx, self.cy = W / 2, st["feet"] * H - st["centre"] * H
        self.rx, self.ry, self.tilt = st["shell"][0] * H, st["shell"][1] * H, st["tilt"]

    def sphere(self, th, ph, s):
        x = self.cx + s * self.rx * np.cos(ph) * np.cos(th)
        y = self.cy - s * self.ry * np.sin(ph) + s * self.tilt * self.rx * np.cos(ph) * np.sin(th)
        return np.stack([x, y], -1), np.cos(ph) * np.sin(th)

    def rim(self, a, s):
        """Projected outline (depth 0): ellipse through the widest points."""
        return np.stack([self.cx + s * self.rx * np.cos(a), self.cy - s * self.ry * np.sin(a)], -1), np.zeros_like(a)


class Bolt:
    def __init__(self, kind, birth, rng, st, H):
        self.kind, self.birth, self.H, self.st = kind, birth, H, st
        self.seed = int(rng.integers(1 << 30))
        r = np.random.default_rng(self.seed)
        wg = st["w_game"] * H / st["game_H"]
        if kind == "rim":
            self.a0, self.da = r.uniform(0, 2 * np.pi), r.uniform(1.6, 2.6)   # 90-150 deg of the outline, counter-clockwise (one flow)
            self.w = wg
        elif kind == "swirl":
            self.dth = r.uniform(1.4, 2.4)                                     # around ...
            self.ph0, self.dph = r.uniform(-1.0, 0.3), r.uniform(0.5, 0.9)     # ... and upward (diagonal wrap, not horizontal bands)
            back = r.random() < st["back_share"]                               # mostly behind the body
            self.th0 = np.pi + r.uniform(0.0, max(0.05, np.pi - self.dth)) if back else r.uniform(0, 2 * np.pi)
            self.w = 0.85 * wg
        else:                                                                  # spark: short bolt on the rim
            self.a0, self.da = r.uniform(0, 2 * np.pi), r.uniform(0.35, 0.6)
            self.w = 0.75 * wg
        self.fork = kind == "rim"
        self.centres = r.permutation(np.linspace(0.1, 0.9, 6))

    def base(self, shell, s, n=80):
        u = np.linspace(0, 1, n)
        if self.kind in ("rim", "spark"):
            return shell.rim(self.a0 + self.da * u, s)
        return shell.sphere(self.th0 + self.dth * u, self.ph0 + self.dph * u, s)

    def path(self, shell, s, d):
        """Base curve -> zigzag: folds at irregular spacing (fixed in px), alternating offsets, bowed segments, jitter per drawing."""
        B, dep = self.base(shell, s)
        seg = np.linalg.norm(np.diff(B, axis=0), axis=1)
        L = seg.sum()
        t = np.r_[0, np.cumsum(seg)] / L
        r = np.random.default_rng(self.seed)
        n = max(2, int(round(L / (self.st["fold_px"] * self.H))))
        tf = np.r_[0, np.cumsum(r.dirichlet(np.full(n, 1.2)))]                 # neighbours differ 2-5x
        sign = np.where(np.arange(n + 1) % 2, 1.0, -1.0) * r.uniform(0.4, 1.0, n + 1)
        sign[0] = sign[-1] = 0
        jr = np.random.default_rng(self.seed * 31 + d)
        amp = self.st["amp"] * self.H * min(1.0, L / (0.6 * self.H)) ** 0.5
        off = sign * amp + jr.normal(0, 0.3 * amp, n + 1) * (sign != 0)
        tan = np.gradient(B, axis=0)
        nrm = np.stack([-tan[:, 1], tan[:, 0]], 1) / np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-6)
        o = np.interp(t, tf, off)
        k = np.clip(np.searchsorted(tf, t, side="right") - 1, 0, n - 1)
        loc = (t - tf[k]) / np.maximum(tf[k + 1] - tf[k], 1e-6)
        bow = np.sin(np.pi * loc) * 0.25 * amp * np.where(k % 2, 1, -1)
        return B + nrm * (o + bow)[:, None], dep, t, tf[1:-1]

    def elements(self, shell, s, I, f):
        d = f - self.birth
        if d < 0 or d >= len(LIFE):
            return []
        lp = LIFE[d]
        P, dep, t, folds = self.path(shell, s, d)
        r = np.random.default_rng(self.seed + 5)
        cs = r.choice(folds, 2) if len(folds) else np.array([0.5, 0.5])
        sw = 1 + sum(a * np.exp(-((t - c) / 0.08) ** 2) for a, c in zip(r.uniform(0.3, 0.6, 2), cs))   # swell <= 1.6x at folds
        taper = np.clip(np.minimum(t / 0.15, (1 - t) / 0.18), 0, 1) ** 0.7
        w = self.w * sw * taper
        gain = lp["gain"] * I
        out = []
        if lp["ph"] != "break":
            m = t <= lp.get("span", 1.0)
            ww = w[m] * lp["w"]
            if lp.get("span", 1.0) < 1:
                ww = ww * np.clip((1 - t[m] / lp["span"]) / 0.3, 0, 1) ** 0.7
            out += _split(P[m], ww, dep[m], gain, self.st["front_w"])
            if self.fork and lp["ph"] == "full" and len(folds):
                i = int(np.argmin(abs(t - folds[len(folds) // 2])))
                tan = P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]
                tan /= max(np.linalg.norm(tan), 1e-6)
                od = P[i] - [shell.cx, shell.cy]
                od /= max(np.linalg.norm(od), 1e-6)
                q = P[i] + np.outer(np.linspace(0, 1, 12), (0.6 * tan + 0.8 * od) * 0.12 * self.H * s)
                q[:, 1] += np.sin(np.linspace(0, np.pi, 12)) * 0.02 * self.H
                out += _split(q, w[i] * 0.8 * np.linspace(1, 0, 12) ** 0.8, np.full(12, dep[i]), gain, self.st["front_w"])
        else:
            n, half = lp["pieces"], lp["keep"] / lp["pieces"] / 2
            for c in self.centres[:n]:
                m = (t >= c - half) & (t <= c + half)
                if m.sum() < 3 or np.linalg.norm(np.diff(P[m], axis=0), axis=1).sum() < self.st["min_piece"] * self.H:
                    continue                                       # a claw shorter than ~0.05 H reads as a dot
                tt = (t[m] - (c - half)) / (2 * half)
                claw = np.clip(np.minimum(tt / 0.3, (1 - tt) / 0.3), 0, 1) ** 0.8
                out += _split(P[m], max(float(w[m].max()), 0.8 * self.w) * claw, dep[m], gain, self.st["front_w"])
        return out


def _split(pts, w, depth, gain, front_w=0.75):
    """Cut where depth changes sign (one vertex overlap); front parts thinner (the body stays the focus)."""
    out, i0 = [], 0
    sgn = np.where(depth > 0.02, 1, -1)
    w = np.broadcast_to(np.asarray(w, float), (len(pts),))
    for i in range(1, len(pts) + 1):
        if i == len(pts) or sgn[i] != sgn[i0]:
            j = min(i + 1, len(pts))
            if j - i0 >= 2:
                out.append(dict(pts=pts[i0:j], w=w[i0:j] * (front_w if sgn[i0] > 0 else 1.0), depth=int(sgn[i0]), gain=gain))
            i0 = i
    return out


def _raster(elems, shape, ss=4):
    """Union of tapered polylines: per-segment quads + a disc at every vertex (no self-intersection at folds)."""
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


def _layer(elems, shape, k, glow_x, extra_glow=None):
    """-> (glow rgb, fill rgb, fill alpha) of one depth layer; glow = per-bolt blurred copy x gain (measured arc tiers)."""
    H, W = shape
    glow = np.zeros((H, W, 3)) if extra_glow is None else extra_glow.copy()
    fill, alpha, sil = np.zeros((H, W, 3)), np.zeros((H, W)), np.zeros((H, W))
    for e in elems:
        e["cov"] = _raster([e], shape)
        sil = np.maximum(sil, e["cov"] * e["gain"])
    if sil.any():
        glow += sum(ndi.gaussian_filter(sil, s * k)[..., None] * np.array(c, float) for s, c in zip(*ARC["halo"])) * glow_x
    for e in elems:
        cov, op = e["cov"], min(1.0, e["gain"] / 0.35)       # bolts fade with the global intensity at the end
        col = compose.layer_colour(cov >= 0.5, ARC["core"], dict(edge=ARC["edge"], s=max(0.3 * float(np.max(e["w"])), 0.8)))
        a = cov[..., None] * op
        fill = fill * (1 - a) + col * a
        alpha = np.maximum(alpha, cov * op)
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
        g[e["depth"]].append('<path fill="#ffffff" d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in ring) + ' Z"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<g id="back">{"".join(g[-1])}</g><g id="front">{"".join(g[1])}</g></svg>')


def schedule(st, env, seed, H):
    """Bolts born per drawing, driven by the intensity curve: a rim primary every 3 drawings, swirls and sparks x I. No bolt is
    born after D - len(LIFE): every bolt has broken and gone by the last drawing."""
    r = np.random.default_rng(seed)
    bolts, acc_s, acc_k = [], 0.0, 0.0
    for f, (s, I) in enumerate(env):
        if I < 0.25 or f > st["D"] - len(LIFE) - 1:
            continue
        if f % 3 == 0:
            bolts.append(Bolt("rim", f, r, st, H))
        acc_s += st["swirl_rate"] * I
        acc_k += st["spark_rate"] * I
        while acc_s >= 1:
            bolts.append(Bolt("swirl", f, r, st, H)); acc_s -= 1
        while acc_k >= 1:
            bolts.append(Bolt("spark", f, r, st, H)); acc_k -= 1
    return bolts


def build(name, style="charge", seed=3, out_root=None):
    st = STYLES[style]
    H = st["H"]
    W, Hc = int(st["canvas"][0] * H), int(st["canvas"][1] * H)
    shell = Shell(st, H, W)
    k = 2 * st["shell"][1] * H / REF_LEN                    # measured px (540 px bolt) -> this shell
    env = envelope(st)
    bolts = schedule(st, env, seed, H)
    out = Path(out_root) if out_root else REPO / "lib-fx/_core/results/vector-showcase/generated" / name
    for sub in ("frames", "back", "front", "svg"):
        (out / sub).mkdir(parents=True, exist_ok=True)
        for p in (out / sub).glob("*"):
            p.unlink()
    fy = st["feet"] * H
    body = (int(W / 2 - st["body_w"] * H / 2), int(fy - H), int(W / 2 + st["body_w"] * H / 2), int(fy))
    yy, xx = np.mgrid[0:Hc, 0:W]
    rr = np.sqrt(((xx - shell.cx) / (0.5 * shell.rx)) ** 2 + ((yy - shell.cy) / (0.5 * shell.ry)) ** 2)
    frames, lines, stats = [], [], []
    for f, (s, I) in enumerate(env):
        elems = [e for b in bolts for e in b.elements(shell, s, I, f)]
        cglow = np.exp(-(rr / s) ** 2)[..., None] * np.array(ARC["halo"][1][1], float) * st["centre_glow"] * I   # invented: charging glow
        img = np.zeros((Hc, W, 3)) + np.array(BG, float)
        img[int(fy):int(fy) + 2] = FLOOR
        layers = {}
        for dep in (-1, 1):
            g, fi, a = _layer([e for e in elems if e["depth"] == dep], (Hc, W), k, st["glow"], cglow if dep == -1 else None)
            layers[dep] = (g, fi, a)
            img = img * (1 - a[..., None]) + fi * a[..., None] + g * (1 - a[..., None])
            if dep == -1:
                img[body[1]:body[3], body[0]:body[2]] = BODY
        img = np.clip(img, 0, 255).astype(np.uint8)
        Image.fromarray(img).save(out / "frames" / f"{f:02d}.png")
        Image.fromarray(_rgba(*layers[-1])).save(out / "back" / f"{f:02d}.png")
        Image.fromarray(_rgba(*layers[1])).save(out / "front" / f"{f:02d}.png")
        (out / "svg" / f"{f:02d}.svg").write_text(_svg(elems, (Hc, W)))
        line = (_raster(elems, (Hc, W)) >= 0.5) if elems else np.zeros((Hc, W), bool)
        lines.append(line)
        frames.append(Image.fromarray(img))
        stats.append(dict(frame=f, scale=s, intensity=I, parts=len(elems), line_px=int(line.sum())))
    rest = np.zeros((Hc, W, 3)) + np.array(BG, float)              # previews: the body alone before the effect restarts
    rest[int(fy):int(fy) + 2] = FLOOR
    rest[body[1]:body[3], body[0]:body[2]] = BODY
    seq = frames + [Image.fromarray(rest.astype(np.uint8))] * st["tail"]
    ms = round(1000 / st["fps"])
    half = [im.resize((W // 2, Hc // 2), Image.LANCZOS) for im in seq]
    half[0].save(out / "preview.gif", save_all=True, append_images=half[1:], duration=ms, loop=0)
    half[0].save(out / "preview_slow.gif", save_all=True, append_images=half[1:], duration=ms * 3, loop=0)
    gk = st["game_H"] / H
    game = [im.resize((round(W * gk), round(Hc * gk)), Image.LANCZOS) for im in seq]
    game[0].save(out / "preview_game.gif", save_all=True, append_images=game[1:], duration=ms, loop=0)
    _sketch(out / "sketch.png", lines, env, body, (Hc, W))
    check = _check(lines, env, shell, st, game[:st["D"]])
    (out / "design.json").write_text(json.dumps(dict(style=style, seed=seed, params=st, k=round(k, 3), life=LIFE, envelope=env,
                                                     bolts=len(bolts), frames=stats, check=check), indent=1, default=float))
    return out, check


def _sketch(path, lines, env, body, shape):
    """Flat single-colour lines at start / peak / end + the envelope curve (silhouette and rhythm before colour)."""
    H, W = shape
    D = len(env)
    picks = [3, int(np.argmax([l.sum() for l in lines])), D - 6]
    sh = Image.new("RGB", (W * 3, H + 160), (245, 245, 240))
    dr = ImageDraw.Draw(sh)
    for j, f in enumerate(picks):
        im = np.zeros((H, W, 3), np.uint8) + 245
        im[body[1]:body[3], body[0]:body[2]] = (190, 192, 200)
        im[lines[f]] = (20, 40, 90)
        sh.paste(Image.fromarray(im), (j * W, 0))
        dr.text((j * W + 8, 8), f"drawing {f}  shell x{env[f][0]:.2f}  I {env[f][1]:.2f}", fill=(20, 20, 20))
    x0, y0, cw, ch = 40, H + 20, W * 3 - 80, 120
    dr.rectangle([x0, y0, x0 + cw, y0 + ch], outline=(150, 150, 150))
    for idx, col in ((0, (20, 40, 90)), (1, (220, 120, 40))):
        dr.line([(x0 + cw * f / (D - 1), y0 + ch - ch * env[f][idx]) for f in range(D)], fill=col, width=3)
    dr.text((x0 + 6, y0 + 4), "blue: shell size   orange: intensity (spawn, glow, opacity)", fill=(20, 20, 20))
    sh.save(path)


def _check(lines, env, shell, st, game):
    """Sector coverage on the shell during the hold (12 sectors, every 3-drawing window), empty last frame, stroke width at game size."""
    D, g, h = st["D"], st["grow"], st["hold"]
    H, W = lines[0].shape
    yy, xx = np.mgrid[0:H, 0:W]
    hold = [f for f in range(D) if g <= f / (D - 1) < h]
    hits = []
    for f in hold:
        s = env[f][0]
        nx, ny = (xx - shell.cx) / (s * shell.rx), (yy - shell.cy) / (s * shell.ry)
        rad, ang = np.hypot(nx, ny), (np.degrees(np.arctan2(-ny, nx)) + 360) % 360
        m = lines[f] & (rad > 0.7) & (rad < 1.25)
        hits.append(set((ang[m] // 30).astype(int).tolist()))
    win = [len(set().union(*hits[i:i + 3])) for i in range(len(hits) - 2)]
    widths = []
    for im in game:
        a = np.asarray(im, float)
        L = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
        m = L > 150
        sk = skeletonize(m)
        if sk.sum() > 20:
            widths.append(float(2 * ndi.distance_transform_edt(m)[sk].mean()))
    return dict(hold_frames=[hold[0], hold[-1]], sectors_per_3_drawings_min=min(win) if win else 0,
                sectors_per_3_drawings=win, last_frame_line_px=int(lines[-1].sum()),
                stroke_width_game_px=round(float(np.median(widths)), 2) if widths else None)
