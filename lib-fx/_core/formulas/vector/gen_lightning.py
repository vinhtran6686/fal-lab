"""gen_lightning: lightning AROUND a character, made from the remake itself (user 2026-11-28, fourth round: "the style exactly
like the remake, soft colours, not dark or heavy; only make the bolts wrap around the body well and keep it physical").
Nothing is redrawn: the clean vector drawings of the lightning-2 remake (lib-fx/_core/results/vector-showcase/lightning-2/<v>/svg)
are placed around a stand-in body with their measured colours, edge gradients, glows (per-drawing gain), ground flash, ink frame
and timing (exposure.json); only the geometry is changed:
  strike instances  (`bolt` drawings) fall from above and land on the floor beside the feet: the reference ground point
                    (its flash) is pinned to the floor line, so nothing goes below the ground; one behind the body, one in front
                    (mirrored), half a loop apart.
  wrap instances    (`arc` drawings) are wrapped around the body as if painted on a cylinder around its vertical axis: reference
                    x -> angle (300 deg), reference y -> height; for every pixel the front (sin > 0) and back surfaces are looked up
                    separately (inverse map), so the back half is hidden by the body and the front half crosses it, and the shapes
                    narrow toward the sides the way a wrapped band does. One instance (two made the loop too busy).
All measured px scale with the instance (glow sigma, gradient s, flash feather, own glows). Output loop = the reference loop
(30 frames at 30 fps), each instance offset so they never fire together.

Outputs (lib-fx/_core/results/vector-showcase/generated/<name>/): frames/NN.png (@2x, stand-in body, reference backdrop colour),
back/NN.png and front/NN.png (@2x RGBA, effect only: back, then the character, then front), preview.gif (@1x, body H = 120 px),
preview_game.gif (body H = 60 px), preview_slow.gif, design.json (instances, checks)."""
import json
import re
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage as ndi
from . import compose
from .bezier import parse_path_d, raster_evenodd
from .dummy import BODY
from .profile import Profile, REPO

SRC = REPO / "lib-fx/_core/results/vector-showcase/lightning-2"
PROFILE = REPO / "lib-fx/_core/formulas/vector/profiles/lightning-2.json"
EXPOSURE = SRC / "recipe/exposure.json"
STYLES = {
    # H: body height @2x. strike: ground point of the reference bolt (its flash bottom) and the height it spans.
    "wrap": dict(H=240, canvas=(2.8, 2.3), feet=2.1, body_w=0.36, game_H=60, fps=30, loop=30,
                 bg=(38, 37, 46), floor=(58, 58, 72), arc_box=(700, 640), arc_x=(55, 640), arc_y=(135, 590),
                 strike=dict(ground=(340, 556), top=5, height=1.35),
                 instances=[dict(kind="strike", v="bolt", x=0.44, mirror=False, depth=-1, offset=0),
                            dict(kind="strike", v="bolt", x=-0.48, mirror=True, depth=1, offset=15),
                            dict(kind="wrap", v="arc", th0=-70, dth=300, y=(0.18, 1.18), R=0.48, tilt=0.22, mirror=False, offset=8)]),
}


def load_drawing(v, f):
    """{layer: [loops]} of one remake drawing (None for a blank drawing)."""
    p = SRC / v / "svg" / f"{f:02d}.svg"
    if not p.exists():
        return None
    return {m.group(1): parse_path_d(m.group(2)) for m in re.finditer(r'<path id="([^"]+)"[^>]*? d="([^"]+)"', p.read_text())}


def drawing_at(expo, t):
    """Reference drawing shown at video frame t of its loop."""
    for i, (first, hold) in enumerate(expo["drawings"]):
        if first - expo["start"] <= t < first - expo["start"] + hold:
            return i
    return len(expo["drawings"]) - 1


def _affine(loops, A):
    return [[tuple(A[:, :2] @ np.asarray(p) + A[:, 2] for p in seg) for seg in loop] for loop in loops]


class Strike:
    def __init__(self, spec, st, body, k):
        self.s, self.k = spec, k
        gx, gy = st["strike"]["ground"]
        sx = -k if spec["mirror"] else k
        tx = body["cx"] + spec["x"] * body["H"]
        self.A = np.array([[sx, 0, tx - sx * gx], [0, k, body["fy"] - k * gy]])

    def covers(self, layers, shape):
        out = {}
        for l, loops in layers.items():
            c = raster_evenodd(_affine(loops, self.A), shape)
            if c.any():
                out[l] = {self.s["depth"]: c}
        return out


class Wrap:
    """Arc drawings painted on a cylinder around the body axis; inverse maps for the front and back surfaces."""
    def __init__(self, spec, st, body, shape):
        H, (Hc, W) = body["H"], shape
        xr, yr = st["arc_x"], st["arc_y"]
        self.s, self.ref_shape, self.floor = spec, (st["arc_box"][1], st["arc_box"][0]), body["fy"] - 1
        yy, xx = np.mgrid[0:Hc, 0:W].astype(np.float32)
        R = spec["R"] * H
        u = np.clip((xx - body["cx"]) / R, -1, 1)
        inside = np.abs(xx - body["cx"]) <= R
        top, bot = body["fy"] - spec["y"][1] * H, body["fy"] - spec["y"][0] * H
        self.k = (bot - top) / (yr[1] - yr[0])
        self.maps = {}
        for depth, th in ((1, np.arccos(u)), (-1, -np.arccos(u))):
            a = (np.degrees(th) - spec["th0"]) % 360
            valid = inside & (a <= spec["dth"])
            frac = a / spec["dth"]
            if spec["mirror"]:
                frac = 1 - frac
            mx = xr[0] + frac * (xr[1] - xr[0])
            ys = yy - spec["tilt"] * R * np.sin(th)                      # tilted ring: the front half sits lower
            my = yr[0] + (ys - top) / (bot - top) * (yr[1] - yr[0])
            mx[~valid] = -10
            self.maps[depth] = (mx.astype(np.float32), my.astype(np.float32))

    def covers(self, layers, shape):
        out = {}
        for l, loops in layers.items():
            src = raster_evenodd(loops, self.ref_shape).astype(np.float32)
            d = {dep: cv2.remap(src, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
                 for dep, (mx, my) in self.maps.items()}
            for c in d.values():
                c[int(self.floor):] = 0                                  # the floor hides anything under it
            d = {dep: c.astype(float) for dep, c in d.items() if c.max() > 0.05}
            if d:
                out[l] = d
        return out


def _gain(cfg, f):
    g = cfg["halo"].get("gain", {})
    if not g:
        return 1.0
    return float(g[str(f)] if str(f) in g else g[str(min((int(x) for x in g), key=lambda x: abs(x - f)))])


def _paint(img, glow_parts, fill_parts):
    for g in glow_parts:
        img = img + g
    for col, a in fill_parts:
        img = img * (1 - a[..., None]) + col * a[..., None]
    return img


def _rgba(glow_parts, fill_parts, shape):
    Hc, W = shape
    g = np.clip(sum(glow_parts) if glow_parts else np.zeros((Hc, W, 3)), 0, None)
    fi, al = np.zeros((Hc, W, 3)), np.zeros((Hc, W))
    for col, a in fill_parts:
        fi = fi * (1 - a[..., None]) + col * a[..., None]
        al = np.maximum(al, a)
    ag = np.clip(g.max(-1) / 255.0, 0, 1)
    A = al + ag * (1 - al)
    P = np.clip(g, 0, 255) * (1 - al[..., None]) + fi * al[..., None]
    rgb = np.where(A[..., None] > 1e-4, P / np.maximum(A[..., None], 1e-4), 0)
    return np.dstack([np.clip(rgb, 0, 255), A * 255]).astype(np.uint8)


def build(name, style="wrap", seed=0, out_root=None):
    st = STYLES[style]
    prof = Profile(PROFILE)
    expo = json.loads(EXPOSURE.read_text())
    H = st["H"]
    W, Hc = int(st["canvas"][0] * H), int(st["canvas"][1] * H)
    body = dict(H=H, cx=W / 2, fy=st["feet"] * H)
    rect = (int(body["cx"] - st["body_w"] * H / 2), int(body["fy"] - H), int(body["cx"] + st["body_w"] * H / 2), int(body["fy"]))
    ks = st["strike"]["height"] * H / (st["strike"]["ground"][1] - st["strike"]["top"])
    inst = []
    for sp in st["instances"]:
        if sp["kind"] == "strike":
            inst.append((sp, Strike(sp, st, body, ks), ks))
        else:
            w = Wrap(sp, st, body, (Hc, W))
            inst.append((sp, w, w.k))
    out = Path(out_root) if out_root else REPO / "lib-fx/_core/results/vector-showcase/generated" / name
    for sub in ("frames", "back", "front"):
        (out / sub).mkdir(parents=True, exist_ok=True)
        for p in (out / sub).glob("*"):
            p.unlink()
    frames, log, below = [], [], 0
    for t in range(st["loop"]):
        glow, fill, row = {-1: [], 1: []}, {-1: [], 1: []}, []
        for sp, geo, k in inst:
            v = sp["v"]
            f = drawing_at(expo[v], (t + sp["offset"]) % st["loop"])
            layers = load_drawing(v, f)
            row.append(f"{v}:{f}")
            if not layers:
                continue
            var, L = prof.var(v), prof.layers(v)
            cov = geo.covers(layers, (Hc, W))
            gain = _gain(var, f)
            for dep in (-1, 1):
                shared = [c[dep] for l, c in cov.items() if dep in c and "own_halo" not in L[l]]
                if shared:
                    sil = np.max(shared, axis=0)
                    glow[dep].append(sum(ndi.gaussian_filter(sil, s * k)[..., None] * np.array(c, float)
                                         for s, c in zip(var["halo"]["sigma"], var["halo"]["c"])) * gain)
                for l, c in cov.items():
                    if dep in c and "own_halo" in L[l] and L[l].get("halo"):
                        glow[dep].append(sum(ndi.gaussian_filter(c[dep], (sy * k, sx * k))[..., None] * np.array(cc, float)
                                             for (sy, sx), cc in zip(L[l]["halo"]["sigma"], L[l]["halo"]["c"])))
                for l in prof.order(v):                                  # fills bottom -> top, as in the remake
                    if l not in cov or dep not in cov[l]:
                        continue
                    a = cov[l][dep]
                    if l != "flash":
                        below += int((a[rect[3] + 2:] > 0.5).sum())
                    if L[l].get("feather"):
                        a = ndi.gaussian_filter(a, L[l]["feather"] * k)
                    grad = L[l].get("gradient")
                    col = compose.layer_colour(a >= 0.5, L[l]["colours"][0], dict(edge=grad["edge"], s=grad["s"] * k) if grad else None)
                    fill[dep].append((col, a))
        img = np.zeros((Hc, W, 3)) + np.array(st["bg"], float)
        img[rect[3]:rect[3] + 2] = st["floor"]
        img = _paint(img, glow[-1], fill[-1])
        img[rect[1]:rect[3], rect[0]:rect[2]] = BODY
        img = np.clip(_paint(img, glow[1], fill[1]), 0, 255).astype(np.uint8)
        Image.fromarray(img).save(out / "frames" / f"{t:02d}.png")
        Image.fromarray(_rgba(glow[-1], fill[-1], (Hc, W))).save(out / "back" / f"{t:02d}.png")
        Image.fromarray(_rgba(glow[1], fill[1], (Hc, W))).save(out / "front" / f"{t:02d}.png")
        frames.append(Image.fromarray(img))
        log.append(dict(frame=t, drawings=row))
    ms = round(1000 / st["fps"])
    half = [im.resize((W // 2, Hc // 2), Image.LANCZOS) for im in frames]
    half[0].save(out / "preview.gif", save_all=True, append_images=half[1:], duration=ms, loop=0)
    half[0].save(out / "preview_slow.gif", save_all=True, append_images=half[1:], duration=ms * 3, loop=0)
    gk = st["game_H"] / H
    game = [im.resize((round(W * gk), round(Hc * gk)), Image.LANCZOS) for im in frames]
    game[0].save(out / "preview_game.gif", save_all=True, append_images=game[1:], duration=ms, loop=0)
    check = dict(scale_strike=round(ks, 3), scale_wrap=[round(k, 3) for sp, _, k in inst if sp["kind"] == "wrap"],
                 stroke_px_below_floor=below)
    (out / "design.json").write_text(json.dumps(dict(style=style, params=st, frames=log, check=check), indent=1, default=float))
    return out, check
