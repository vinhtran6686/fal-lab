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
    # an arm held out level with the ground (a casting pose); arm = shoulder -> hand along +x, in body heights
    "arm": dict(H=240, canvas=(3.1, 2.1), feet=1.92, body_x=0.75, body_w=0.36, game_H=60, fps=30, loop=30,
                bg=(38, 37, 46), floor=(58, 58, 72), arc_box=(700, 640), arc_x=(55, 640), arc_y=(135, 590),
                strike=dict(ground=(340, 556), top=5, height=1.35),
                arm=dict(y=0.22, length=0.85, thick=0.11),
                instances=[dict(kind="wrap_h", v="arc", x=(-0.05, 1.12), R=0.17, twist=1.2, th0=0, dth=360, mirror=False, offset=0),
                           dict(kind="wrap_h", v="arc", x=(0.10, 1.20), R=0.21, twist=-0.9, th0=140, dth=360, mirror=True, offset=14),
                           dict(kind="shoot", v="bolt", anchor=(300, 5), length=0.95, rot=-90, mirror=False, depth=1, offset=7)]),
    # ---- poses (2026-11-28, after "arm" was approved): limbs are bars from a shoulder at an angle (deg, 0 = +x, 90 = up);
    # cylinders along any limb (wrap_axis), bolts between two physical points (bolt2: source -> end, the reference top -> source
    # and the reference ground point -> end, recomputed for every drawing; flash_flat keeps a ground flash lying on the ground)
    "raise": dict(H=240, body_w=0.36, game_H=60, fps=30, loop=30, bg=(38, 37, 46), floor=(58, 58, 72), arc_box=(700, 640), arc_x=(55, 640), arc_y=(135, 590), strike=dict(ground=(340, 556), top=5, height=1.35), canvas=(2.2, 2.75), feet=2.6, body_x=1.0,
                  arms=[dict(side=1, angle=88, length=0.75, thick=0.11, y=0.18)],
                  instances=[dict(kind="bolt2", v="bolt", src=("sky", 0.05), dst=("hand", 0), depth=1, offset=0),
                             dict(kind="wrap_axis", v="arc", arm=0, x=(-0.02, 1.15), R=0.17, twist=1.1, th0=0, dth=360, mirror=False, offset=9),
                             dict(kind="wrap", v="arc", th0=-70, dth=300, y=(0.10, 0.95), R=0.42, tilt=0.22, mirror=True, offset=20)]),
    "dual": dict(H=240, body_w=0.36, game_H=60, fps=30, loop=30, bg=(38, 37, 46), floor=(58, 58, 72), arc_box=(700, 640), arc_x=(55, 640), arc_y=(135, 590), strike=dict(ground=(340, 556), top=5, height=1.35), canvas=(4.2, 2.1), feet=1.92, body_x=2.1,
                 arms=[dict(side=1, angle=0, length=0.8, thick=0.11, y=0.22), dict(side=-1, angle=180, length=0.8, thick=0.11, y=0.22)],
                 instances=[dict(kind="wrap_axis", v="arc", arm=0, x=(-0.05, 1.12), R=0.17, twist=1.2, th0=0, dth=360, mirror=False, offset=0),
                            dict(kind="wrap_axis", v="arc", arm=1, x=(-0.05, 1.12), R=0.17, twist=-1.2, th0=180, dth=360, mirror=True, offset=15),
                            dict(kind="bolt2", v="bolt", src=("hand", 0), dst=("along", 0, 0.9), depth=1, offset=7),
                            dict(kind="bolt2", v="bolt", src=("hand", 1), dst=("along", 1, 0.9), depth=1, mirror=True, offset=22)]),
    "slam": dict(H=240, body_w=0.36, game_H=60, fps=30, loop=30, bg=(38, 37, 46), floor=(58, 58, 72), arc_box=(700, 640), arc_x=(55, 640), arc_y=(135, 590), strike=dict(ground=(340, 556), top=5, height=1.35), canvas=(3.4, 2.0), feet=1.85, body_x=1.1,
                 arms=[dict(side=1, angle=-50, length=0.78, thick=0.11, y=0.24)],
                 instances=[dict(kind="wrap_axis", v="arc", arm=0, x=(-0.05, 1.10), R=0.17, twist=1.0, th0=0, dth=360, mirror=False, offset=0),
                            dict(kind="bolt2", v="bolt", src=("hand", 0), dst=("ground", 1.3), depth=1, flash_flat=True, offset=7),
                            dict(kind="bolt2", v="bolt", src=("sky", -0.45), dst=("ground", -0.5), depth=-1, flash_flat=True, mirror=True, offset=19)]),
    "thrust": dict(H=240, body_w=0.36, game_H=60, fps=30, loop=30, bg=(38, 37, 46), floor=(58, 58, 72), arc_box=(700, 640), arc_x=(55, 640), arc_y=(135, 590), strike=dict(ground=(340, 556), top=5, height=1.35), canvas=(3.1, 2.6), feet=2.45, body_x=0.75,
                   arms=[dict(side=1, angle=35, length=0.85, thick=0.11, y=0.22)],
                   instances=[dict(kind="wrap_axis", v="arc", arm=0, x=(-0.05, 1.12), R=0.17, twist=1.2, th0=0, dth=360, mirror=False, offset=0),
                              dict(kind="wrap_axis", v="arc", arm=0, x=(0.10, 1.20), R=0.21, twist=-0.9, th0=140, dth=360, mirror=True, offset=14),
                              dict(kind="bolt2", v="bolt", src=("hand", 0), dst=("along", 0, 1.0), depth=1, offset=7)]),
}
# colour variants: rotate every colour of the remake around the grey axis (hue shift that keeps the light / dark structure);
# gold takes the measured colours of the lightning-2 `strike` (a real gold reference) where it has them.
PALETTES = {"blue": dict(rot=0), "purple": dict(rot=70), "red": dict(rot=155), "green": dict(rot=-80),
            "gold": dict(rot=-150, body=dict(colours=[[250, 254, 186]], edge=[249, 210, 129]), white_core=[255, 250, 225],
                         halo=[[101.8, 47.7, -20.6], [212.5, 87.2, -3.5]], flash=[255, 255, 58],
                         flash_halo=[[587.4, 366.7, 16.6], [1041.6, 689.1, 15.6]])}


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
    """Bolt drawings under one affine map: a reference anchor -> a target point, scale k, optional mirror and rotation.
    strike: anchor = the ground point (flash bottom) -> the floor beside the feet; shoot: anchor = the bolt's top (its source)
    -> the hand, rotated -90 deg so the bolt runs out along +x, its flash becoming the impact at the far end."""
    def __init__(self, spec, st, body, k, anchor=None, target=None):
        self.s, self.k = spec, k
        if anchor is None:
            anchor = st["strike"]["ground"]
            target = (body["cx"] + spec["x"] * body["H"], body["fy"])
        a = np.radians(spec.get("rot", 0))
        M = k * np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]]) @ np.diag([-1.0 if spec["mirror"] else 1.0, 1.0])
        self.A = np.c_[M, np.asarray(target, float) - M @ np.asarray(anchor, float)]

    def covers(self, layers, shape):
        out = {}
        A = self.A
        if self.s["kind"] == "shoot":                           # every drawing's own source point goes to the hand
            top = [p for loops in layers.values() for loop in loops for seg in loop for p in seg if p[1] < 40]
            if top:
                self.ax = float(np.mean([p[0] for p in top]))
            if getattr(self, "ax", None) is not None:
                A = self.A.copy()
                A[:, 2] += A[:, :2] @ np.array([self.s["anchor"][0] - self.ax, 0.0])
        for l, loops in layers.items():
            c = raster_evenodd(_affine(loops, A), shape)
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


class WrapH:
    """Arc drawings painted on a cylinder lying along the arm (axis along +x): reference x -> position along the arm,
    reference y -> angle around it (+ twist turns along the length, a helix). Screen y = axis_y - R sin(theta),
    depth = cos(theta): the back half is hidden by the arm, the front half crosses it."""
    def __init__(self, spec, st, body, shape):
        H, (Hc, W) = body["H"], shape
        xr, yr = st["arc_x"], st["arc_y"]
        self.s, self.ref_shape, self.floor = spec, (st["arc_box"][1], st["arc_box"][0]), body["fy"] - 1
        yy, xx = np.mgrid[0:Hc, 0:W].astype(np.float32)
        R, ay = spec["R"] * H, body["arm_y"]
        x0, x1 = body["shoulder"] + spec["x"][0] * H, body["shoulder"] + spec["x"][1] * H
        u = (xx - x0) / (x1 - x0)
        v = np.clip((ay - yy) / R, -1, 1)
        inside = (np.abs(ay - yy) <= R) & (u >= 0) & (u <= 1)
        self.k = (x1 - x0) / (xr[1] - xr[0])
        self.maps = {}
        for depth, th in ((1, np.arcsin(v)), (-1, np.pi - np.arcsin(v))):
            a = (np.degrees(th) - spec["th0"] - 360 * spec["twist"] * u) % 360
            valid = inside & (a <= spec["dth"])
            frac = a / spec["dth"]
            if spec["mirror"]:
                frac = 1 - frac
            mx = xr[0] + np.clip(u, 0, 1) * (xr[1] - xr[0])
            my = yr[0] + frac * (yr[1] - yr[0])
            mx[~valid] = -10
            self.maps[depth] = (mx.astype(np.float32), my.astype(np.float32))

    covers = Wrap.covers


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


def _hue(c, deg):
    """Rotate an RGB vector around the grey axis by deg (keeps R+G+B)."""
    a = np.radians(deg)
    k = np.ones(3) / np.sqrt(3)
    v = np.asarray(c, float)
    return v * np.cos(a) + np.cross(k, v) * np.sin(a) + k * (k @ v) * (1 - np.cos(a))


def recolour(prof, name):
    """Profile colours of `arc` and `bolt` turned into palette `name` (in memory; the remake profile on disk is not touched)."""
    pal = PALETTES[name]
    if pal["rot"] == 0:
        return prof
    rot = lambda c, clip=True: [float(x) for x in (np.clip(_hue(c, pal["rot"]), 0, 255) if clip else _hue(c, pal["rot"]))]
    for v in ("arc", "bolt"):
        var = prof.var(v)
        var["halo"]["c"] = [rot(c, False) for c in var["halo"]["c"]]
        for l, L in var["layers"].items():
            if l == "ink":
                if L.get("halo"):
                    L["halo"]["c"] = [rot(c, False) for c in L["halo"]["c"]]
                continue
            L["colours"] = [rot(c) for c in L["colours"]]
            if L.get("gradient"):
                L["gradient"]["edge"] = rot(L["gradient"]["edge"])
            if L.get("halo"):
                L["halo"]["c"] = [rot(c, False) for c in L["halo"]["c"]]
    if "body" in pal:                                            # measured gold (lightning-2 strike)
        b = prof.layers("bolt")["body"]
        b["colours"], b["gradient"]["edge"] = pal["body"]["colours"], pal["body"]["edge"]
        prof.var("bolt")["halo"]["c"] = pal["halo"]
        prof.var("arc")["halo"]["c"] = pal["halo"]
        a = prof.layers("arc")["body"]
        a["colours"], a["gradient"]["edge"] = [pal["white_core"]], pal["body"]["edge"]
        f = prof.layers("bolt")["flash"]
        f["colours"], f["halo"]["c"] = [pal["flash"]], pal["flash_halo"]
    return prof


def _limbs(st, body, rect):
    """Arms of a pose: bars from a shoulder at an angle -> (polygons to draw, list of dict(p0, dir, hand))."""
    H, polys, arms = body["H"], [], []
    for am in st.get("arms", []):
        p0 = np.array([rect[2] if am["side"] > 0 else rect[0], rect[1] + am["y"] * H], float)
        a = np.radians(am["angle"])
        d = np.array([np.cos(a), -np.sin(a)])
        n = np.array([-d[1], d[0]]) * am["thick"] * H / 2
        p1 = p0 + d * am["length"] * H
        polys.append(np.array([p0 + n, p1 + n, p1 - n, p0 - n]))
        arms.append(dict(p0=p0, dir=d, hand=p1, length=am["length"] * H))
    return polys, arms


class WrapAxis(WrapH):
    """WrapH along any limb: the cylinder axis runs from the shoulder along the arm direction."""
    def __init__(self, spec, st, body, shape, arm):
        H, (Hc, W) = body["H"], shape
        xr, yr = st["arc_x"], st["arc_y"]
        self.s, self.ref_shape, self.floor = spec, (st["arc_box"][1], st["arc_box"][0]), body["fy"] - 1
        yy, xx = np.mgrid[0:Hc, 0:W].astype(np.float32)
        R, d = spec["R"] * H, arm["dir"]
        nrm = np.array([d[1], -d[0]])                            # "up" side of the limb (for a level arm: screen up)
        if nrm[1] > 0:
            nrm = -nrm
        rx, ry = xx - arm["p0"][0], yy - arm["p0"][1]
        along = rx * d[0] + ry * d[1]
        side = rx * nrm[0] + ry * nrm[1]
        L0, L1 = spec["x"][0] * H, spec["x"][1] * H
        u = (along - L0) / (L1 - L0)
        v = np.clip(side / R, -1, 1)
        inside = (np.abs(side) <= R) & (u >= 0) & (u <= 1)
        self.k = (L1 - L0) / (xr[1] - xr[0])
        self.maps = {}
        for depth, th in ((1, np.arcsin(v)), (-1, np.pi - np.arcsin(v))):
            a = (np.degrees(th) - spec["th0"] - 360 * spec["twist"] * u) % 360
            valid = inside & (a <= spec["dth"])
            frac = a / spec["dth"]
            if spec["mirror"]:
                frac = 1 - frac
            mx = xr[0] + np.clip(u, 0, 1) * (xr[1] - xr[0])
            my = yr[0] + frac * (yr[1] - yr[0])
            mx[~valid] = -10
            self.maps[depth] = (mx.astype(np.float32), my.astype(np.float32))


class Bolt2:
    """A bolt between two physical points: for every drawing, its own top (mean of the points with y < 40) -> src and the
    reference ground point -> dst (similarity: scale + rotation, mirrored on request). flash_flat: the ground flash keeps its
    horizontal ellipse (it lies on the ground) instead of tilting with the bolt."""
    def __init__(self, spec, st, src, dst):
        self.s, self.st = spec, st
        self.src, self.dst = np.asarray(src, float), np.asarray(dst, float)
        self.g = np.array(st["strike"]["ground"], float)
        self.k = np.linalg.norm(self.dst - self.src) / (self.g[1] - st["strike"]["top"])
        self.ax = 300.0

    def _A(self, top):
        a, b = np.array([top, self.st["strike"]["top"]], float), self.g
        if self.s.get("mirror"):
            a, b = a * [-1, 1], b * [-1, 1]
        va, vb = b - a, self.dst - self.src
        ang = np.arctan2(vb[1], vb[0]) - np.arctan2(va[1], va[0])
        sc = np.linalg.norm(vb) / np.linalg.norm(va)
        M = sc * np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
        if self.s.get("mirror"):
            M = M @ np.diag([-1.0, 1.0])
            a = a * [-1, 1]
        M2 = M
        return np.c_[M2, self.src - M2 @ (np.array([top, self.st["strike"]["top"]], float))], sc

    def covers(self, layers, shape):
        top = [p for loops in layers.values() for loop in loops for seg in loop for p in seg if p[1] < 40]
        if top:
            self.ax = float(np.mean([p[0] for p in top]))
        A, sc = self._A(self.ax)
        out = {}
        for l, loops in layers.items():
            T = A
            if l == "flash" and self.s.get("flash_flat"):          # same place, no tilt
                T = np.c_[np.diag([sc, sc]), self.dst - sc * self.g]
            c = raster_evenodd(_affine(loops, T), shape)
            if self.s.get("flash_flat"):
                c[int(self.st["_floor"]) + 1:] = 0 if l != "flash" else c[int(self.st["_floor"]) + 1:]
            if c.any():
                out[l] = {self.s["depth"]: c}
        return out


def build(name, style="wrap", seed=0, out_root=None, colour="blue", preview_only=False):
    """style "wrap": around the body; "arm": around an arm held out level (casting) plus a bolt shot from the hand; poses
    "raise", "dual", "slam", "thrust" (see STYLES). colour: a PALETTES name. preview_only: write only colours/<colour>.gif and
    colours/<colour>_game.gif (colour variants of an output whose frames are already stored)."""
    st = dict(STYLES[style])
    prof = recolour(Profile(PROFILE), colour)
    expo = json.loads(EXPOSURE.read_text())
    H = st["H"]
    W, Hc = int(st["canvas"][0] * H), int(st["canvas"][1] * H)
    body = dict(H=H, cx=st.get("body_x", W / H / 2) * H, fy=st["feet"] * H)
    st["_floor"] = body["fy"]
    rect = (int(body["cx"] - st["body_w"] * H / 2), int(body["fy"] - H), int(body["cx"] + st["body_w"] * H / 2), int(body["fy"]))
    rects, polys = [rect], []
    if "arm" in st:                                               # stand-in arm: shoulder -> hand, level with the ground
        am = st["arm"]
        body["shoulder"], body["arm_y"] = rect[2], rect[1] + am["y"] * H
        body["hand"] = (body["shoulder"] + am["length"] * H, body["arm_y"])
        rects.append((rect[2], int(body["arm_y"] - am["thick"] * H / 2), int(body["hand"][0]), int(body["arm_y"] + am["thick"] * H / 2)))
    polys, arms = _limbs(st, body, rect)

    def point(ref):
        if ref[0] == "hand":
            return arms[ref[1]]["hand"]
        if ref[0] == "along":
            return arms[ref[1]]["hand"] + arms[ref[1]]["dir"] * ref[2] * H
        if ref[0] == "ground":
            return np.array([body["cx"] + ref[1] * H, body["fy"]])
        return np.array([body["cx"] + ref[1] * H, 0.04 * H])       # sky: top of the frame
    ks = st["strike"]["height"] * H / (st["strike"]["ground"][1] - st["strike"]["top"])
    inst = []
    for sp in st["instances"]:
        if sp["kind"] == "strike":
            inst.append((sp, Strike(sp, st, body, ks), ks))
        elif sp["kind"] == "shoot":
            k = sp["length"] * H / (st["strike"]["ground"][1] - sp["anchor"][1])
            inst.append((sp, Strike(sp, st, body, k, sp["anchor"], body["hand"]), k))
        elif sp["kind"] == "wrap_h":
            w = WrapH(sp, st, body, (Hc, W))
            inst.append((sp, w, w.k))
        elif sp["kind"] == "wrap_axis":
            w = WrapAxis(sp, st, body, (Hc, W), arms[sp["arm"]])
            inst.append((sp, w, w.k))
        elif sp["kind"] == "bolt2":
            b = Bolt2(sp, st, point(sp["src"]), point(sp["dst"]))
            inst.append((sp, b, b.k))
        else:
            w = Wrap(sp, st, body, (Hc, W))
            inst.append((sp, w, w.k))
    out = Path(out_root) if out_root else REPO / "lib-fx/_core/results/vector-showcase/generated" / name
    if not preview_only:
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
        for r in rects:
            img[r[1]:r[3], r[0]:r[2]] = BODY
        if polys:
            im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
            from PIL import ImageDraw
            dr = ImageDraw.Draw(im)
            for pg in polys:
                dr.polygon([tuple(x) for x in pg], fill=BODY)
            img = np.asarray(im, float)
        img = np.clip(_paint(img, glow[1], fill[1]), 0, 255).astype(np.uint8)
        if not preview_only:
            Image.fromarray(img).save(out / "frames" / f"{t:02d}.png")
            Image.fromarray(_rgba(glow[-1], fill[-1], (Hc, W))).save(out / "back" / f"{t:02d}.png")
            Image.fromarray(_rgba(glow[1], fill[1], (Hc, W))).save(out / "front" / f"{t:02d}.png")
        frames.append(Image.fromarray(img))
        log.append(dict(frame=t, drawings=row))
    ms = round(1000 / st["fps"])
    half = [im.resize((W // 2, Hc // 2), Image.LANCZOS) for im in frames]
    gk = st["game_H"] / H
    game = [im.resize((round(W * gk), round(Hc * gk)), Image.LANCZOS) for im in frames]
    if preview_only:
        (out / "colours").mkdir(parents=True, exist_ok=True)
        half[0].save(out / "colours" / f"{colour}.gif", save_all=True, append_images=half[1:], duration=ms, loop=0)
        game[0].save(out / "colours" / f"{colour}_game.gif", save_all=True, append_images=game[1:], duration=ms, loop=0)
        return out, dict(colour=colour, stroke_px_below_floor=below)
    half[0].save(out / "preview.gif", save_all=True, append_images=half[1:], duration=ms, loop=0)
    half[0].save(out / "preview_slow.gif", save_all=True, append_images=half[1:], duration=ms * 3, loop=0)
    game[0].save(out / "preview_game.gif", save_all=True, append_images=game[1:], duration=ms, loop=0)
    check = dict(scale_strike=round(ks, 3), scale_wrap=[round(k, 3) for sp, _, k in inst if sp["kind"] != "strike"],
                 stroke_px_below_floor=below)
    (out / "design.json").write_text(json.dumps(dict(style=style, colour=colour, params={k: v for k, v in st.items() if not k.startswith("_")},
                                                     frames=log, check=check), indent=1, default=float))
    return out, check
