#!/usr/bin/env python3
"""Layered skill effects, the way the reference game builds them: no video model, a few small flat layers
(ground ring, slash smear, burst, bolt, pillar, particles, tweened keyframe stills) drawn on ONE effect canvas
anchored at the character's feet, each layer exported on its own and composited over the body sheet.

Usage:
  python scripts/fx_layers.py out/heroes/holy_commander/fx/radiant_slash.json        render + preview
  python scripts/fx_layers.py <recipe> --check                                       validate only

Recipe (JSON, one per skill; units of the character's body height H, origin = the feet pivot, x right,
y up; times in seconds from the start of the body sheet):
  {"asset": "out/heroes/holy_commander", "skill": "radiant_slash",
   "body": "skill_radiant_slash_side",           # exported sheet under the asset (meta.json state), optional
   "canvas": [4.0, 4.0], "pivot": [0.5, 0.85],   # effect canvas in H and the feet pivot inside it (fractions)
   "fps": 15,                                    # drawings per second ("on twos" of the game's 30 fps)
   "duration": 1.2,                              # optional, default: the body sheet's length
   "layers": [{"id": "smear", "type": "slash", "z": "front", "start": 0.35, "length": 0.3,
               "color": "#ffe27a", "at": [0.6, 0.6], "radius": 0.9, "from": 120, "to": -40, "width": 0.22}, ...]}

Layer types (all flat: 2-3 tones of one colour and a dark outline of the same hue, never a gradient or blur):
  ring      ground decal: a perspective ellipse that grows and fades   radius [r0, r1], width, squash (0.35)
  slash     crescent smear sweeping along an arc                       at, radius, from, to (degrees), width
  burst     spiky flash that pops and shrinks                          at, radius, spikes
  bolt      zigzag lightning from the sky (or between two points)      at (target), top (height), width, kinks
  pillar    vertical light column that rises and thins                 at, width, height
  particles shards or sparks thrown out and falling                    at, count, speed, size, spread, gravity
  sprite    a keyframe still (fal-image, magenta key) tweened          image, height, keys [{t, scale, alpha, dx, dy, rot}]
Common: id, type, z (back|front of the body), start, length, color, alpha (peak), ease (out|in|inout|linear).

Writes <asset>/fx/<skill>/: <layer>/frames/@2x and @1x/<layer>_NN.png (each layer on the shared effect canvas),
preview.gif and sheet.png (body + every layer), fx.json (canvas, pivot @2x, fps, layer list and timing for
the engine), and records the skill under "fx" in <asset>/meta.json when that file exists.
"""
import argparse, colorsys, json, math, pathlib, random, sys
import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
SS = 4   # supersampling for clean anti-aliased edges
TYPES = ("ring", "slash", "burst", "bolt", "pillar", "particles", "sprite")


# ---------------------------------------------------------------- colour and easing
def rgb(hexcode: str) -> tuple:
    h = hexcode.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def tone(c: tuple, light: float) -> tuple:
    """Same hue, lightness scaled (light < 1 darker, > 1 lighter): the 2-3 flat tones and the outline."""
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
    l = max(0.0, min(1.0, l * light if light < 1 else l + (1 - l) * (light - 1)))
    return tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s))


def ease(t: float, kind: str = "out") -> float:
    t = max(0.0, min(1.0, t))
    return {"linear": t, "in": t * t, "out": 1 - (1 - t) ** 2, "inout": 3 * t * t - 2 * t ** 3}.get(kind, t)


def fade(t: float, tail: float = 0.4) -> float:
    """Full until the last `tail` of the layer, then down to 0: effects dissipate, they never pop off."""
    return 1.0 if t < 1 - tail else max(0.0, (1 - t) / tail)


# ---------------------------------------------------------------- drawing on a supersampled layer
class Layer:
    def __init__(self, size, pivot, h_px):
        self.W, self.H = size
        self.img = Image.new("RGBA", (self.W * SS, self.H * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.px, self.py, self.hpx = pivot[0], pivot[1], h_px

    def pt(self, x, y):   # H units, origin feet, y up -> supersampled pixels
        return ((self.px + x * self.hpx) * SS, (self.py - y * self.hpx) * SS)

    def u(self, v):       # length in H -> supersampled pixels
        return v * self.hpx * SS

    def poly(self, pts, fill, outline=None, ow=0.0):
        if outline is not None and ow > 0:
            self.d.line(pts + [pts[0]], fill=outline, width=max(1, round(self.u(ow))), joint="curve")
        self.d.polygon(pts, fill=fill)

    def done(self, alpha: float) -> Image.Image:
        out = self.img.resize((self.W, self.H), Image.LANCZOS)
        if alpha < 1:
            a = np.asarray(out).copy()
            a[..., 3] = (a[..., 3] * max(0.0, alpha)).astype(np.uint8)
            out = Image.fromarray(a)
        return out


def draw_ring(L, t, p, c):
    r0, r1 = p.get("radius", [0.3, 1.4]); sq = p.get("squash", 0.35); w = p.get("width", 0.12)
    r = r0 + (r1 - r0) * ease(t, p.get("ease", "out")); th = w * (1 - 0.7 * t)
    cx, cy = L.pt(*p.get("at", [0, 0]))
    def ell(rad, fill):
        L.d.ellipse([cx - L.u(rad), cy - L.u(rad * sq), cx + L.u(rad), cy + L.u(rad * sq)], fill=fill)
    ell(r + th * 0.5, tone(c, 0.45) + (255,))
    ell(r + th * 0.5 - max(th * 0.18, 0.012), c + (255,))
    ell(r + th * 0.1, tone(c, 1.45) + (255,))
    ell(max(0.0, r - th * 0.5), (0, 0, 0, 0))
    return fade(t, 0.5)


def draw_slash(L, t, p, c):
    ax, ay = p.get("at", [0.5, 0.6]); R = p.get("radius", 0.9); w = p.get("width", 0.2)
    a0, a1 = math.radians(p.get("from", 120)), math.radians(p.get("to", -40))
    head = ease(min(1, t / 0.55), "out"); tail = ease(max(0, (t - 0.25) / 0.75), "in")
    if head - tail < 0.02:
        return 0.0
    n = 24; outer, inner = [], []
    for i in range(n + 1):
        k = tail + (head - tail) * i / n
        ang = a0 + (a1 - a0) * k
        thick = w * math.sin(math.pi * i / n) ** 0.7          # tapered both ends: a crescent
        outer.append(L.pt(ax + math.cos(ang) * R, ay + math.sin(ang) * R))
        inner.append(L.pt(ax + math.cos(ang) * (R - thick), ay + math.sin(ang) * (R - thick)))
    band = outer + inner[::-1]
    L.poly(band, c + (255,), tone(c, 0.45) + (255,), 0.035)
    core = [((o[0] * 2 + i[0]) / 3, (o[1] * 2 + i[1]) / 3) for o, i in zip(outer, inner)]
    L.d.line(core, fill=tone(c, 1.5) + (255,), width=max(1, round(L.u(w * 0.22))), joint="curve")
    return 1.0 if t < 0.7 else max(0.0, (1 - t) / 0.3)


def draw_burst(L, t, p, c):
    ax, ay = p.get("at", [0.6, 0.5]); R = p.get("radius", 0.45); n = p.get("spikes", 8)
    s = math.sin(math.pi * min(1, t * 1.6)) if t < 0.62 else max(0.0, 1 - (t - 0.62) / 0.38) * 0.6
    rot = p.get("seed", 1) * 0.37 + t * 0.6
    def star(scale, col):
        pts = []
        for i in range(n * 2):
            rr = R * scale * (1.0 if i % 2 == 0 else 0.42) * s
            a = rot + math.pi * i / n
            pts.append(L.pt(ax + math.cos(a) * rr, ay + math.sin(a) * rr))
        L.poly(pts, col + (255,))
    if s > 0.02:
        star(1.12, tone(c, 0.45)); star(1.0, c); star(0.55, tone(c, 1.55))
    return fade(t, 0.35)


def draw_bolt(L, t, p, c, drawing):
    tx, ty = p.get("at", [0.8, 0.0]); top = p.get("top", 4.0); w = p.get("width", 0.08); k = p.get("kinks", 6)
    sx, sy = p.get("from", [tx + 0.3, top])
    rnd = random.Random(p.get("seed", 7) * 1000 + drawing)     # a new zigzag every drawing: it flickers
    reach = ease(min(1, t / 0.25), "out")
    pts = []
    for i in range(k + 1):
        f = i / k
        if f > reach:
            break
        jx = 0 if i in (0, k) else rnd.uniform(-0.18, 0.18)
        pts.append(L.pt(sx + (tx - sx) * f + jx, sy + (ty - sy) * f))
    if len(pts) > 1:
        for width, col in ((w * 2.2, tone(c, 0.45)), (w * 1.5, c), (w * 0.6, tone(c, 1.6))):
            L.d.line(pts, fill=col + (255,), width=max(1, round(L.u(width))), joint="curve")
    return 1.0 if t < 0.55 else max(0.0, (1 - t) / 0.45)


def draw_pillar(L, t, p, c):
    ax, ay = p.get("at", [0, 0]); W = p.get("width", 0.7); Hh = p.get("height", 3.0)
    grow = ease(min(1, t / 0.3), "out"); thin = 1 - 0.75 * ease(max(0, (t - 0.3) / 0.7), "in")
    h = Hh * grow; w = W * thin
    for scale, col in ((1.0, tone(c, 0.5)), (0.82, c), (0.38, tone(c, 1.55))):
        x0, x1 = ax - w * scale / 2, ax + w * scale / 2
        a = L.pt(x0, ay + h); b = L.pt(x1, ay)
        L.d.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=L.u(w * scale / 2), fill=col + (255,))
    return fade(t, 0.4)


def draw_particles(L, t, p, c):
    ax, ay = p.get("at", [0, 0.3]); n = p.get("count", 10); sp = p.get("speed", 1.6); size = p.get("size", 0.07)
    spread = math.radians(p.get("spread", 140)); g = p.get("gravity", 2.5); up = math.radians(p.get("angle", 90))
    rnd = random.Random(p.get("seed", 3))
    for i in range(n):
        a = up + rnd.uniform(-spread / 2, spread / 2); v = sp * rnd.uniform(0.5, 1.0); life = rnd.uniform(0.55, 1.0)
        tt = t / life
        if tt >= 1:
            continue
        T = tt * life * p.get("time", 0.8)
        x = ax + math.cos(a) * v * T; y = ay + math.sin(a) * v * T - 0.5 * g * T * T
        s = size * (1 - tt * 0.6)
        diamond = [L.pt(x, y + s * 1.6), L.pt(x + s, y), L.pt(x, y - s * 1.6), L.pt(x - s, y)]
        L.poly(diamond, (tone(c, 1.45) if i % 3 == 0 else c) + (255,), tone(c, 0.45) + (255,), 0.02)
    return fade(t, 0.3)


_sprites = {}
def key_magenta(path: pathlib.Path) -> Image.Image:
    if path not in _sprites:
        a = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        k = np.clip((np.minimum(r, b) - g) / 255.0, 0, 1)                 # magenta share
        alpha = np.where(np.sqrt((r - 255) ** 2 + g ** 2 + (b - 255) ** 2) < 90, 0.0, 1 - k)
        keep = np.maximum(alpha, 1e-3)[..., None]
        a[..., :3] = np.clip((a[..., :3] - (1 - keep) * np.array([255, 0, 255])) / keep, 0, 255)
        a[..., 3] = alpha * 255
        img = Image.fromarray(a.astype(np.uint8)); _sprites[path] = img.crop(img.getbbox())
    return _sprites[path]


def draw_sprite(L, t, p, c):
    img = key_magenta(ROOT / p["image"])
    keys = sorted(p.get("keys") or [{"t": 0, "scale": 0.6, "alpha": 0}, {"t": 0.25, "scale": 1, "alpha": 1},
                                    {"t": 1, "scale": 1.05, "alpha": 0}], key=lambda k: k["t"])
    def at(name, default):
        prev = next((k for k in reversed(keys) if k["t"] <= t), keys[0])
        nxt = next((k for k in keys if k["t"] >= t), keys[-1])
        a, b = prev.get(name, default), nxt.get(name, default)
        f = 0 if nxt["t"] == prev["t"] else ease((t - prev["t"]) / (nxt["t"] - prev["t"]), p.get("ease", "inout"))
        return a + (b - a) * f
    h = L.u(p.get("height", 1.0) * at("scale", 1.0))
    s = img.resize((max(1, round(img.width * h / img.height)), max(1, round(h))), Image.LANCZOS)
    s = s.rotate(at("rot", 0.0), expand=True, resample=Image.BICUBIC)
    ax, ay = p.get("at", [0, 0]); cx, cy = L.pt(ax + at("dx", 0.0), ay + at("dy", 0.0))
    L.img.alpha_composite(s, (round(cx - s.width / 2), round(cy - s.height)))   # "at" = the sprite's bottom centre
    return at("alpha", 1.0)


DRAW = {"ring": draw_ring, "slash": draw_slash, "burst": draw_burst, "pillar": draw_pillar,
        "particles": draw_particles, "sprite": draw_sprite}


# ---------------------------------------------------------------- recipe, body, render
def load_body(asset: pathlib.Path, sheet: str | None, h2: float, still: str | None = None):
    """(frames @2x, fps, feet pivot px) of the exported body sheet; else the master still as one frame."""
    meta_path = asset / "meta.json"
    if sheet and meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        st = meta.get("states", {}).get(sheet)
        if st:
            src = asset / st["dir"] / "frames" / "@2x"
            frames = [Image.open(f).convert("RGBA") for f in sorted(src.glob("*.png"))]
            cw, ch = (c * 2 for c in meta["cell"])
            return frames, st["fps"], (cw * meta["pivot"][0], ch * meta["pivot"][1])
    if still:   # recipe "body_still": preview over one approved still (the skill's pose) until the clip exists
        img = key_magenta(ROOT / still); s = img.resize((round(img.width * h2 / img.height * 1.0), round(h2)), Image.LANCZOS)
        return [s], 15, (s.width / 2, s.height)
    masters = sorted((asset / "design").glob("master_v*.png"))
    if not masters:
        return [], 15, (0, 0)
    img = key_magenta(masters[-1]); s = img.resize((round(img.width * h2 / img.height), round(h2)), Image.LANCZOS)
    print(f"note: no exported '{sheet}' sheet; the preview uses the latest master still as the body", file=sys.stderr)
    return [s], 15, (s.width / 2, s.height)


def tier_height(asset: pathlib.Path) -> float:
    """{H} @1x from meta.json body_height_2x, else from brief.md ("{H}` 60 px")."""
    meta = asset / "meta.json"
    if meta.exists():
        bh = json.loads(meta.read_text(encoding="utf-8")).get("body_height_2x")
        if bh:
            return bh / 2
    import re
    m = re.search(r"\{H\}`?\s*(\d+)", (asset / "brief.md").read_text(encoding="utf-8")) if (asset / "brief.md").exists() else None
    if not m:
        sys.exit(f"{asset}: no body height (meta.json body_height_2x or '{{H}} <n> px' in brief.md)")
    return float(m.group(1))


def check(recipe: dict) -> list:
    errs = []
    for key in ("asset", "skill", "layers"):
        if key not in recipe:
            errs.append(f"missing '{key}'")
    for i, ly in enumerate(recipe.get("layers", [])):
        if ly.get("type") not in TYPES:
            errs.append(f"layer {i}: type must be one of {TYPES}")
        if ly.get("type") == "sprite" and not (ROOT / ly.get("image", "")).exists():
            errs.append(f"layer {ly.get('id', i)}: image {ly.get('image')} not found")
        if "start" not in ly or "length" not in ly:
            errs.append(f"layer {ly.get('id', i)}: needs start and length (seconds)")
    return errs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("recipe"); ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    rpath = pathlib.Path(a.recipe); recipe = json.loads(rpath.read_text(encoding="utf-8"))
    errs = check(recipe)
    if errs:
        sys.exit("recipe errors:\n  " + "\n  ".join(errs))
    if a.check:
        print(json.dumps({"recipe": str(rpath), "ok": True, "layers": len(recipe["layers"])})); return
    asset = ROOT / recipe["asset"] if not pathlib.Path(recipe["asset"]).is_absolute() else pathlib.Path(recipe["asset"])
    H = tier_height(asset); h2 = 2 * H                              # everything is drawn @2x
    cw, ch = (round(v * h2) for v in recipe.get("canvas", [4.0, 4.0]))
    pv = recipe.get("pivot", [0.5, 0.85]); pivot = (cw * pv[0], ch * pv[1])
    fps = recipe.get("fps", 15)
    body, bfps, bpivot = load_body(asset, recipe.get("body"), h2, recipe.get("body_still"))
    body_len = len(body) / bfps if len(body) > 1 else 0
    dur = recipe.get("duration") or max([body_len] + [ly["start"] + ly["length"] for ly in recipe["layers"]])
    n = max(1, math.ceil(dur * fps))
    out = asset / "fx" / recipe["skill"]
    layer_frames = {ly["id"]: [] for ly in recipe["layers"]}
    composite = []
    for f in range(n):
        time = f / fps
        frame_layers = {}
        for ly in recipe["layers"]:
            L = Layer((cw, ch), pivot, h2)
            t = (time - ly["start"]) / ly["length"]
            alpha = 0.0
            if 0 <= t <= 1:
                c = rgb(ly.get("color", "#ffd84a"))
                alpha = (draw_bolt(L, t, ly, c, f) if ly["type"] == "bolt" else DRAW[ly["type"]](L, t, ly, c))
                alpha *= ly.get("alpha", 1.0)
            frame_layers[ly["id"]] = L.done(alpha)
            layer_frames[ly["id"]].append(frame_layers[ly["id"]])
        comp = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        for z in ("back", "body", "front"):
            if z == "body" and body:
                b = body[min(len(body) - 1, int(time * bfps))]
                comp.alpha_composite(b, (round(pivot[0] - bpivot[0]), round(pivot[1] - bpivot[1])))
                continue
            for ly in recipe["layers"]:
                if ly.get("z", "front") == z:
                    comp.alpha_composite(frame_layers[ly["id"]])
        composite.append(comp)
    # write: one folder per layer on the shared canvas, the composite preview, fx.json for the engine
    for lid, frames in layer_frames.items():
        d = out / lid / "frames" / "@2x"; d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.png"):
            old.unlink()
        d1 = out / lid / "frames" / "@1x"; d1.mkdir(parents=True, exist_ok=True)
        for old in d1.glob("*.png"):
            old.unlink()
        for i, im in enumerate(frames, 1):
            im.save(d / f"{lid}_{i:02d}.png")
            im.resize((max(1, cw // 2), max(1, ch // 2)), Image.LANCZOS).save(d1 / f"{lid}_{i:02d}.png")
    bg = (58, 74, 46, 255)
    gif = [Image.alpha_composite(Image.new("RGBA", (cw, ch), bg), c).convert("P", palette=Image.ADAPTIVE) for c in composite]
    gif[0].save(out / "preview.gif", save_all=True, append_images=gif[1:], duration=round(1000 / fps), loop=0, disposal=2)
    sheet = Image.new("RGBA", (cw * n, ch), bg)
    for i, c in enumerate(composite):
        sheet.alpha_composite(c, (i * cw, 0))
    sheet.save(out / "sheet.png")
    info = {"skill": recipe["skill"], "canvas_2x": [cw, ch], "pivot_2x": [round(pivot[0]), round(pivot[1])],
            "fps": fps, "frames": n, "body": recipe.get("body"),
            "layers": [{"id": ly["id"], "type": ly["type"], "z": ly.get("z", "front"), "start": ly["start"],
                        "length": ly["length"], "files": f"fx/{recipe['skill']}/{ly['id']}/frames/@2x/{ly['id']}_NN.png (also @1x)"}
                       for ly in recipe["layers"]]}
    (out / "fx.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    meta_path = asset / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta.setdefault("fx", {})[recipe["skill"]] = f"fx/{recipe['skill']}/fx.json"
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps({"skill": recipe["skill"], "frames": n, "fps": fps, "canvas_2x": [cw, ch],
                      "layers": [ly["id"] for ly in recipe["layers"]], "preview": str((out / "preview.gif").relative_to(ROOT))}))


if __name__ == "__main__":
    main()
