"""Generator: SEQUENTIAL DOUBLE SLASH, X-shaped (user brief 2026-11-10, written by another AI; gold sword slash, 550 ms).

Screen coordinates: x grows to the right, y grows DOWN.
  Slash 01: starts top-RIGHT, ends bottom-LEFT (moves down-left).
  Slash 02: starts top-LEFT, ends bottom-RIGHT (moves down-right); starts only after slash 01 has done most of its motion and
            crosses slash 01 at its middle (the intersection is the effect's anchor / spawn point).
Order and direction come first (brief "FINAL REQUIREMENT"); light stays simple.

Timeline in BASE milliseconds (550 ms; any other duration rescales it, frames are sampled at `fps`):
    0-120   slash 01 grows head-first from top-right, brightness 0 -> 100 %, small sparks trail behind
  120-240   slash 01 stays where it was drawn, opacity 100 -> 40 % (never gone: the first direction stays readable)
  200-340   slash 02 grows from top-left (slash 01 still at 40 %); when its head passes the middle -> small bright impact + short rays
  340-390   X impact: both slashes a little wider, the crossing brightest
  390-550   dissolve: sparks / particles first, outer trail, main trail, the core last; nothing left at the end

Each slash = 3 flat layers (outer orange, main yellow, core white-yellow), tapered both ends, gently curved (an arc of a large circle),
the head sharp, the tail dragged behind; the outer trail is broken in its tail half. Glow is small (additive-style frames on black).
Reuses the vector kit: nét thon (`strokes`), several coordinate frames per effect, per-layer opacity, `render_sequence`."""
import numpy as np
from .frames import EllipseFrame
from .gen_render import render_sequence
from .strokes import peak_scale

COL = {"outer": [255, 138, 36], "main": [255, 214, 72], "core": [255, 250, 222]}
LAYERS = {f"s{i}_{l}": COL[l] for i in (1, 2) for l in ("outer", "main", "core")}
LAYERS.update({"x_main": COL["main"], "x_core": COL["core"]})                         # the crossing flash, on top
HALO = {"model": "blur", "sigma": [6.0, 22.0], "c": [[215, 115, 30], [170, 80, 15]]}  # soft orange glow, still smaller than the blade
BASE_MS = 550.0

# reference: ref/vfx/x-slash-gold/reference.webp (user 2026-11-10). Each slash is a CRESCENT: about a quarter circle (110 deg),
# radius ~0.5 of the canvas; slash 1 bulges toward the lower right (near vertical at the top-right start, near horizontal at the
# bottom-left end), slash 2 bulges toward the upper right (near horizontal at the top-left start, plunging to the bottom-right end).
# Thickest in the first third (the start end is blunt-ish and curls), a long needle toward the leading end.
WIDTH = {"outer": 58.0, "main": 38.0, "core": 16.0}
SPAN = {"outer": (0.00, 1.00), "main": (0.05, 0.97), "core": (0.12, 0.88)}
PROFILE = {1: (0.70, 1.50), 2: (0.90, 1.30)}            # (a = start end, b = leading end) of the width formula


def _clamp(x):
    return float(min(1.0, max(0.0, x)))


def _ease_out(x):
    x = _clamp(x)
    return 1 - (1 - x) ** 2.2


def _lerp_ms(b, keys):
    """piecewise-linear value over base ms: keys = [(ms, value), ...]."""
    ks = sorted(keys)
    if b <= ks[0][0]:
        return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if b <= t1:
            return v0 + (v1 - v0) * (b - t0) / (t1 - t0)
    return ks[-1][1]


def state(b):
    """Everything the timeline says at base time b (ms)."""
    h1 = _ease_out(b / 120.0)
    t1 = 0.10 * _clamp((b - 50) / 70.0) + 0.30 * _clamp((b - 390) / 160.0)
    h2 = _ease_out((b - 200) / 140.0) if b >= 200 else None
    t2 = 0.10 * _clamp((b - 250) / 90.0) + 0.30 * _clamp((b - 390) / 160.0) if h2 is not None else None
    widen = _lerp_ms(b, [(340, 1.0), (360, 1.16), (390, 1.10), (550, 0.35)])
    op1 = _lerp_ms(b, [(0, 0.35), (120, 1.0), (240, 0.40), (390, 0.40), (550, 0.0)])
    op2 = _lerp_ms(b, [(200, 0.40), (340, 1.0), (390, 1.0), (550, 0.0)]) if h2 is not None else 0.0
    fade = {  # dissolve order: outer first, then main, the core last (multiplies the slash opacity)
        "outer": _lerp_ms(b, [(390, 1.0), (500, 0.0)]),
        "main": _lerp_ms(b, [(390, 1.0), (530, 0.0)]),
        "core": 1.0}
    # the crossing: slash 02's head passes the middle of its path (s = 0.5)
    hit = None
    if h2 is not None and h2 >= 0.5:
        x = (1 - (0.5) ** (1 / 2.2))  # inverse ease: share of the 140 ms when the head reaches the middle
        hit = 200 + 140 * x
    return dict(h1=h1, t1=t1, h2=h2, t2=t2, widen=widen, op1=op1, op2=op2, fade=fade, hit=hit)


def _geometry(size, scale, rotation, R=350.0, arc_deg=116.0, k=0.62):
    """Two crescent arcs crossing at the canvas centre C, each centred on its own circle (u runs clockwise on screen, y down).
    Slash 1: circle centre up-left of C, u from -10 to +100 deg (top-right -> bottom-left, bulge lower-right).
    Slash 2: circle centre down-left of C, u from -100 to +10 deg (top-left -> bottom-right, bulge upper-right).
    `rotation` (deg, clockwise on screen) turns the whole X around C."""
    # both crescents reach much farther left of the crossing than right of it (see the reference): put the crossing right of centre
    C = np.array([size[0] * (0.60 if rotation == 0 else 0.5), size[1] / 2.0])
    rot = np.radians(rotation)
    Rm = np.array([[np.cos(rot), -np.sin(rot)], [np.sin(rot), np.cos(rot)]])
    Rs = R * scale
    half = np.radians(arc_deg) / 2
    out = []
    for mid in (np.radians(45.0), np.radians(-45.0)):        # angle of C seen from the circle centre
        O = C - Rm @ (Rs * np.array([np.cos(mid), k * np.sin(mid)]))   # k < 1: the crescents are wider than tall (reference)
        m = mid
        u0, u1 = m - half, m + half
        tan_mid = Rm @ np.array([-np.sin(m), k * np.cos(m)])
        tan_mid = tan_mid / np.linalg.norm(tan_mid)          # motion direction at the crossing
        # radius along the path (share s): slash 1 curls tight at its start and straightens out (reference: hooked top-right start,
        # long gentle sweep); slash 2 starts gentle and plunges at its end. r(0.5) = R keeps the crossing at C.
        a_, b_ = (0.70, 0.60) if mid > 0 else (1.30, -0.60)
        out.append(dict(frame=EllipseFrame(tuple(O), k, rot), O=O, R=Rs, u_start=u0, u_end=u1, d=tan_mid,
                        rf=(lambda s, a_=a_, b_=b_, Rs=Rs: Rs * (a_ + b_ * s))))
    for g in out:                                            # true motion direction at the crossing (r varies along the path)
        P = lambda q: np.array(g["frame"].to_xy(_pos(g, q), g["rf"](q)), float)
        d = P(0.505) - P(0.495)
        g["d"] = d / np.linalg.norm(d)
    return C, out


def _sp(g, s0, s1, off=0.0):
    """spine (4 Bernstein values) for a stroke covering path shares s0..s1: follows the path's own radius r(s), so the curve does
    not move while the stroke grows (r is linear in s: equally spaced control values reproduce it exactly)."""
    return [float(g["rf"](s0 + (s1 - s0) * j / 3.0) + off) for j in range(4)]


def _pos(g, s):
    """angle on the arc for path share s (0 = start corner, 1 = end corner)."""
    return g["u_start"] + (g["u_end"] - g["u_start"]) * s


def _blade(g, fi, tail, head, w, scale, prefix, out, which):
    """The three layers of one slash between path shares tail..head. The core sits toward the inner (concave) side, as in the
    reference, where the white core runs along the inside of the crescent."""
    L = head - tail
    if L < 0.02:
        return
    a, b = PROFILE[which]
    for l in ("outer", "main", "core"):
        s0, s1 = tail + SPAN[l][0] * L, tail + SPAN[l][1] * L
        Wl = WIDTH[l] * scale * w
        off = -(0.18 * WIDTH["outer"] * scale * w if l == "core" else 0.0)
        out[f"{prefix}_{l}"].append(dict(axis="u", pos0=_pos(g, s0), pos1=_pos(g, s1), spine=_sp(g, s0, s1, off), a=a, b=b, e0=0.0, e1=0.0,
                                         W=peak_scale(Wl, a, b), op="add", frame=fi))


def _trails(g, fi, tail, head, w, scale, prefix, out, which, seed):
    """Thin parallel trail arcs (outer trail): one outside near the start (the doubled arc of the reference), two inside lagging
    behind the head; broken in the tail half."""
    L = head - tail
    if L < 0.15:
        return
    rng = np.random.default_rng(seed)
    specs = [(+0.62, 0.00, 0.38, 5.0), (-0.75, 0.35, 0.78, 3.4)]   # (offset in blade widths, s0, s1, px)
    for off, a0, a1, px in specs:
        s0, s1 = tail + a0 * L, tail + a1 * L
        out[f"{prefix}_main"].append(dict(axis="u", pos0=_pos(g, s0), pos1=_pos(g, s1), spine=_sp(g, s0, s1, off * WIDTH["outer"] * scale * w), a=1.0, b=1.2, e0=0.0, e1=0.0,
                                          W=peak_scale(px * scale * max(w, 0.4), 1.0, 1.2), op="add", frame=fi))
    for k in range(2):                                                 # broken outer trail in the tail half
        u = tail + rng.uniform(0.15, 0.45) * L
        gap = 0.012 + 0.01 * k
        out[f"{prefix}_outer"].append(dict(axis="u", pos0=_pos(g, u - gap), pos1=_pos(g, u + gap),
                                           spine=[g["rf"](u) + 30 * scale] * 2 + [g["rf"](u) - 30 * scale] * 2, a=0.6, b=0.6, e0=0.0, e1=0.0,
                                           W=70 * scale, op="cut", frame=fi))


def _sparks(g, fi, b, b0, grow_ms, scale, layer, seed, out, n=5, life=170.0):
    """Small lens-shaped sparks (glints) left beside the path as the head passes, drifting on along the swing; short-lived."""
    rng = np.random.default_rng(seed)
    for s, off, ln, drift, dly in zip(rng.uniform(0.15, 0.95, n), rng.choice([-1, 1], n) * rng.uniform(30, 95, n),
                                      rng.uniform(26, 48, n), rng.uniform(0.04, 0.10, n), rng.uniform(0, 30, n)):
        born = b0 + grow_ms * (1 - (1 - s) ** (1 / 2.2)) * 0.9 + dly    # when the eased head passes s
        age = b - born
        if 0 <= age <= life:
            k = 1 - age / life
            sc = s + drift * age / life
            span = ln * scale * (0.5 + 0.5 * k) / g["R"]
            out[layer].append(dict(axis="u", pos0=_pos(g, sc) - span / 2 * np.sign(g["u_end"] - g["u_start"]),
                                   pos1=_pos(g, sc) + span / 2 * np.sign(g["u_end"] - g["u_start"]),
                                   spine=[g["rf"](sc) + off * scale] * 4, a=1.0, b=1.0, e0=0.0, e1=0.0,
                                   W=peak_scale(8.0 * scale * k, 1.0, 1.0), op="add", frame=fi))


def _impact(fc, b, hit, scale, dirs, seed, out):
    """Bright flash at the crossing + a few short rays + small particles flying along the slash directions."""
    if hit is None or b < hit:
        return
    age = b - hit
    S = 200.0                                          # EllipseFrame.u_scale: angle -> stroke 'across' units
    grow = _clamp(age / 50.0)
    power = _lerp_ms(b, [(hit, 0.6), (hit + 40, 1.0), (390, 1.0), (470, 0.0)])
    if power > 0.02:
        # star: 4 rays on the two slash lines (8 directions would be a third slash) + 2 short ones across
        angs = [np.degrees(np.arctan2(v[1], v[0])) for v in dirs] + [np.degrees(np.arctan2(-v[1], -v[0])) for v in dirs]
        rng = np.random.default_rng(seed)
        angs += list(rng.uniform(-180, 180, 2))
        for i, a in enumerate(angs):
            Ln = (120 if i < 4 else 40) * scale * (0.5 + 0.5 * grow) * power
            if Ln < 4:
                continue
            r0 = 3 * scale
            Wpx = (9 if i < 4 else 5) * scale * power
            for lay, k in (("x_main", 1.0), ("x_core", 0.45)):
                out[lay].append(dict(axis="v", pos0=float(r0), pos1=float(r0 + Ln * (1.0 if lay == "x_main" else 0.8)),
                                     spine=[np.radians(a) * S] * 4, a=0.35, b=1.6, e0=0.0, e1=0.0,
                                     W=float(peak_scale(Wpx * k * S / (r0 + 0.25 * Ln), 0.35, 1.6)), op="add", frame=2))
        # bright centre: a small 4-point diamond
        for a in (0, 90, 180, 270):
            out["x_core"].append(dict(axis="v", pos0=0.0, pos1=float(22 * scale * power), spine=[np.radians(a + 45) * S] * 4, a=0.2, b=1.2,
                                      e0=0.0, e1=0.0, W=float(peak_scale(22 * scale * power * S / (10 * scale), 0.2, 1.2)), op="add", frame=2))
    # particles: small dashes flying out along the slash directions, short life, gone before the cores
    if age < 110:
        rng = np.random.default_rng(seed + 1)
        for v in list(dirs) + [-x for x in dirs]:
            for _ in range(2):
                a = np.degrees(np.arctan2(v[1], v[0])) + rng.uniform(-14, 14)
                r = (14 + rng.uniform(1.6, 2.6) * age) * scale
                ln = 9 * scale * (1 - age / 110)
                if ln > 2:
                    out["x_main"].append(dict(axis="v", pos0=float(r), pos1=float(r + ln), spine=[np.radians(a) * S] * 4, a=0.8, b=0.8,
                                              e0=0.0, e1=0.0, W=float(peak_scale(3.2 * scale * S / r, 0.8, 0.8)), op="add", frame=2))


def build(name="gen-slash-x-gold", seed=5, scale=1.0, rotation=0.0, duration_ms=550.0, fps=30, background=(0, 0, 0)):
    """Renders the effect into lib-fx/_study/<name>/ (+ sheet.png and fx_meta.json for an engine). Frames are on black: with additive
    blending (brief: 'additive if the engine supports it') black adds nothing, so no background is drawn into the game."""
    size = (int(round(640 * scale)), int(round(640 * scale)))
    C, (g1, g2) = _geometry(size, scale, rotation)
    fc = EllipseFrame(tuple(C), 1.0, 0.0)
    n = int(round(duration_ms * fps / 1000.0))
    drawings, opac, hits = [], {l: {} for l in LAYERS}, []
    for f in range(n):
        b = ((f + 1) * 1000.0 / fps) * BASE_MS / duration_ms  # this frame's time on the base 550 ms timeline (end of its slot)
        st = state(b)
        out = {l: [] for l in LAYERS}
        w1 = st["widen"] * (0.6 + 0.4 * st["h1"])
        _blade(g1, 0, st["t1"], st["h1"], w1, scale, "s1", out, 1)
        _trails(g1, 0, st["t1"], st["h1"], w1, scale, "s1", out, 1, seed)
        _sparks(g1, 0, b, 0, 120, scale, "s1_core", seed + 11, out)
        if st["h2"] is not None:
            w2 = st["widen"] * (0.6 + 0.4 * st["h2"])
            _blade(g2, 1, st["t2"], st["h2"], w2, scale, "s2", out, 2)
            _trails(g2, 1, st["t2"], st["h2"], w2, scale, "s2", out, 2, seed + 3)
            _sparks(g2, 1, b, 200, 140, scale, "s2_core", seed + 13, out)
        _impact(fc, b, st["hit"], scale, (g1["d"], g2["d"]), seed + 9, out)
        for i, op in ((1, st["op1"]), (2, st["op2"])):
            for l in ("outer", "main", "core"):
                opac[f"s{i}_{l}"][f] = op * st["fade"][l]
        flash = _lerp_ms(b, [(390, 1.0), (470, 0.0)])
        opac["x_main"][f], opac["x_core"][f] = flash, flash
        hits.append(dict(frame=f, ms=round((f + 1) * 1000.0 / fps, 1), base_ms=round(b, 1), **{k: (None if v is None else round(v, 3))
                    for k, v in st.items() if k in ("h1", "h2", "op1", "op2", "widen")}))
        drawings.append(dict(strokes=out, frames=[f], label=f"{b:.0f} ms"))
    gain = {f: _lerp_ms((f + 1) * 1000.0 / fps * BASE_MS / duration_ms, [(0, 0.8), (120, 1.0), (340, 1.0), (390, 1.15), (550, 0.0)])
            for f in range(n)}
    meta = dict(style="x-double-slash", seed=seed, scale=scale, rotation=rotation, duration_ms=duration_ms, fps=fps, frames=n,
                anchor=[float(C[0]), float(C[1])], blend="additive", directions=dict(slash1="top-right -> bottom-left, bulges lower-right",
                slash2="top-left -> bottom-right, bulges upper-right"), reference="ref/vfx/x-slash-gold/reference.webp", timeline=hits)
    res = render_sequence(name, drawings, [g1["frame"], g2["frame"], fc], size, LAYERS, HALO, gain, background=background, fps=fps,
                          layer_opacity=opac, halo_weight={l: 0.6 for l in LAYERS if l.startswith("s1")}, meta=meta)
    _export(res[0], n, size, C, fps, duration_ms, meta)
    return res


def _export(out, n, size, C, fps, duration_ms, meta):
    """sheet.png (one row, the lib-fx convention) + fx_meta.json: what an engine needs to spawn it (anchor = the crossing)."""
    import json
    from PIL import Image
    W, H = size
    sheet = Image.new("RGB", (W * n, H))
    for f in range(n):
        sheet.paste(Image.open(out / "frames" / f"{f:02d}.png").convert("RGB"), (f * W, 0))
    sheet.save(out / "sheet.png")
    (out / "fx_meta.json").write_text(json.dumps(dict(
        id=out.name, frames=n, fps=fps, duration_ms=duration_ms, frame_size=[W, H], anchor=[float(C[0]), float(C[1])],
        blend="additive", background="black (adds nothing with additive blending)", loop=False,
        spawn="draw the sheet centred on the anchor at the target position; scale / rotate / opacity at draw time",
        directions=meta["directions"]), indent=1))
