"""fxkit / effect: an effect is a STACK OF LAYERS, each with one role, its own life and its own place.

  Effect("heavy", space="aim", layers=[
      Layer("ring",   role="secondary", z="back",  life=Life(0.033, 0.1, 0.0, 0.23), r=(24, 118)),
      Layer("star",   role="primary",              life=Life(0.0, 0.066, 0.033, 0.33), n=5, length=124),
      Layer("scraps", role="particles",            life=Life(0.033, 0.033, 0.0, 0.5), n=10)])

A layer KIND is a drawing function registered with @kind("name"): fn(c: Ctx, ph: Phase, **params). It draws on c.cv with
positions from c.sp (Space), colours from c.pal (Ramp), variation from c.rng(...) and sizes times c.s. Layer kinds live in
fxkit/layers/*.py. Roles (what a layer is FOR; lint counts them): ground, glow, smoke, secondary, primary, core, particles,
flash, accent. Layers are drawn in list order; z = "back" puts a layer behind the character, "front" in front of it.
"""
import math
from dataclasses import dataclass, field, replace
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import fxcore
from . import ink
from .ramp import Ramp
from .space import Space
from .timing import Life
from .vary import Rand

KINDS = {}
ROLES = ("ground", "glow", "smoke", "secondary", "primary", "core", "particles", "flash", "accent")
SPACES = ("point", "aim", "span", "travel", "ground")


def kind(name):
    """Register a layer kind: @kind("star") def star(c, ph, n=5, length=120, ...)."""
    def deco(fn):
        KINDS[name] = fn; return fn
    return deco


class Layer:
    def __init__(self, kind, role, life, id=None, z="front", at="a", plane=None, **p):
        """plane: None, or ("ground", k): every shape of this layer is squashed to y/x = k about the layer's anchor, so it lies on the
        floor (a ground blast seen from above-and-aside reads as a flat ellipse, its glow too). Applied once in Ink.add / Ink.cut."""
        assert role in ROLES, f"unknown role {role}"; assert z in ("front", "back")
        assert plane is None or (plane[0] == "ground" and 0 < plane[1] <= 1), f"bad plane {plane}"
        self.kind, self.role, self.life, self.id, self.z, self.at, self.plane, self.p = kind, role, life, id or kind, z, at, plane, p

    def but(self, **changes):
        """A copy with some fields or parameters changed (life=, z=, at= or any parameter of the kind)."""
        new = Layer(self.kind, self.role, self.life, self.id, self.z, self.at, self.plane, **self.p)
        for k, v in changes.items():
            if k in ("life", "z", "at", "role", "plane", "id"): setattr(new, k, v)
            else: new.p[k] = v
        return new


class Ctx:
    """What a layer function gets: sp (Space), pal (Ramp), s (size factor), cv (the canvas of this layer), front / back (both
    canvases), o (the layer's own anchor point on the canvas), fps, and rng(*keys): a named random stream of this layer."""
    def __init__(self, effect, layer, sp, pal, seed, front, back, fps):
        self.effect, self.layer, self.sp, self.pal, self.s, self.seed, self.fps = effect, layer, sp, pal, sp.s, seed, fps
        self.front, self.back = front, back
        self.cv = back if layer.z == "back" else front
        self.o = sp.at(layer.at)
        self._glow = None

    def add_glow(self, mask, weight=1.0):
        """Feed the effect's glow with a silhouette (bool, supersampled) of this layer; weight 0..1 = how strongly it glows now."""
        if self._glow is None or weight <= 0: return
        g = self._glow[self.layer.z]
        np.maximum(g, mask * np.float32(min(1.0, weight)), out=g)

    def rng(self, *keys):
        return Rand(self.seed, self.effect.name, self.layer.id, *keys)


class Effect:
    def __init__(self, name, layers, title="", desc="", space="point", reach=140, extent=220, pal="sun", tags=(), status="draft", weight="medium",
                 glow=(9, 0.8, 34, 0.5), glow_key="body"):
        """space: how the effect uses its two points: point (a only), aim (a + the direction to b), span (stretched from a to b),
        travel (moves from a to b, then hits at b), ground (a on the floor line, level). reach: the default distance a -> b in
        px at s = 1 (library build). extent: how far in px the effect may reach around a and b (work canvas; the result is
        cropped to what was drawn). pal: default palette name. weight: light | medium | heavy (lint wants more roles for heavy)."""
        assert space in SPACES
        ids = [l.id for l in layers]; assert len(ids) == len(set(ids)), f"{name}: layer ids must be unique: {ids}"
        self.name, self.layers, self.title, self.desc, self.space = name, list(layers), title or name, desc, space
        self.reach, self.extent, self.pal, self.tags, self.status, self.weight = reach, extent, pal, list(tags), status, weight
        self.glow, self.glow_key = glow, glow_key      # glow = (near blur px, near alpha, far blur px, far alpha) at s = 1; None = no glow

    t0 = property(lambda self: min(0.0, min(l.life.start for l in self.layers)))      # s before the hit when the effect starts
    end = property(lambda self: max(l.life.end for l in self.layers))

    def variant(self, name=None, layers=None, **attrs):
        """A sibling effect: layers = {layer id: False (drop it) | {param or life/z/at changes}}; attrs replace effect fields."""
        layers = layers or {}
        unknown = set(layers) - {l.id for l in self.layers}; assert not unknown, f"{self.name}: no layer {unknown}"
        ls = [l.but(**layers[l.id]) if isinstance(layers.get(l.id), dict) else l for l in self.layers if layers.get(l.id, True) is not False]
        e = Effect(name or self.name, ls, self.title, self.desc, self.space, self.reach, self.extent, self.pal, self.tags, self.status, self.weight,
                   self.glow, self.glow_key)
        for k, v in attrs.items(): setattr(e, k, v)
        return e

    def draw(self, t, sp, pal, seed, front, back, fps=30.0, only=None):
        """Draw every live layer at effect time t (seconds from the hit) onto the two canvases."""
        shape = front.img.size[::-1]
        glow = {"front": np.zeros(shape, np.float32), "back": np.zeros(shape, np.float32)}
        done = {"front": False, "back": False}
        for l in self.layers:
            if only is not None and l.id not in only: continue
            ph = l.life.at(t, fps)
            if ph is None: continue
            c = Ctx(self, l, sp, pal, seed, front, back, fps); c._glow = glow
            KINDS[l.kind](c, ph, **l.p)
        if self.glow:
            for z, cv in (("back", back), ("front", front)):
                g = glow[z]
                if not g.any(): continue
                self._put_glow(cv, g, pal[self.glow_key], sp.s)

    def _put_glow(self, cv, g, rgb, s):
        """The glow of one canvas: the silhouettes fed by its layers, blurred at two scales in the main colour, put UNDER what
        the canvas already holds (rules/01: glow = the shape itself, blurred; not a fixed outline)."""
        ss = cv.ss; nb, na, fb, fa = self.glow
        small = np.asarray(Image.fromarray((g * 255).astype(np.uint8), "L").resize((cv.w, cv.h), Image.BOX), np.float32) / 255
        a = np.clip(ndimage.gaussian_filter(small, nb * s) * na * 1.6, 0, na) + np.clip(ndimage.gaussian_filter(small, fb * s) * fa * 2.2, 0, fa)
        a = np.clip(a, 0, 0.92)
        lay = Image.fromarray(np.dstack([np.broadcast_to(np.asarray(rgb, np.uint8), a.shape + (3,)), (a * 255).astype(np.uint8)]), "RGBA")
        lay = lay.resize(cv.img.size, Image.BILINEAR)
        lay.alpha_composite(cv.img); cv.img = lay; cv.d = ImageDraw.Draw(cv.img)

    def lint(self):
        """Design rules every effect must pass (empty list = fine)."""
        out, L = [], self.layers
        for l in L:
            if l.kind not in KINDS: out.append(f"layer {l.id}: unknown kind '{l.kind}'")
            if l.life.release < 2 / 30 - 1e-9: out.append(f"layer {l.id}: release under 2 frames (it would pop off)")
        roles = {l.role for l in L}
        need = {"light": 2, "medium": 3, "heavy": 4}[self.weight]
        if len(roles) < need: out.append(f"{len(roles)} roles ({', '.join(sorted(roles))}); a {self.weight} effect needs {need}+ for depth")
        if "sustained" not in self.tags:
            if not any(l.role in ("flash", "core", "primary") and abs(l.life.start) <= 1 / 30 + 1e-9 for l in L): out.append("no primary / core / flash layer on the hit frame (the hit does not read)")
            if len({round(l.life.start, 3) for l in L if l.role != "flash"}) < 2 and len(L) > 2: out.append("every layer starts on the same frame (stagger them)")
            ends = sorted(l.life.end for l in L)
            if len(L) > 2 and ends[-1] < ends[0] * 1.5 + 1e-9: out.append("every layer ends at about the same time (fast layers must die early, slow ones linger)")
            prim = [l.life.end for l in L if l.role in ("primary", "core", "flash")]
            slow = [l.life.end for l in L if l.role in ("particles", "smoke", "glow")]
            if prim and slow and max(slow) <= max(prim): out.append("nothing outlives the primary shape (add lingering particles / smoke / glow)")
        return out


def render(effect, a=None, b=None, pal=None, s=1.0, seed=0, fps=30.0, speed=1.0, only=None, ss=3, pad=6):
    """Every frame of an effect between two points. a, b: canvas px of the caller (any origin); None = the library default
    (a at the origin, b `reach` px to the right). Returns dict:
      frames (RGBA, back under front), back, front (the two halves, for drawing a character between them), size, anchor (a in
      the frame), target (b in the frame), hit_frame (1-based frame of the hit), fps, origin (frame's top-left in caller px).
    The frame is cropped to what was drawn (+pad), so no frame size has to be chosen; only a shape reaching beyond the work
    canvas (`extent` px around a and b) is cut, and the quality gate reports that as `clip`: raise the effect's `extent`."""
    a = (0.0, 0.0) if a is None else a
    b = (a[0] + effect.reach * s, a[1]) if b is None else b
    if effect.space in ("ground", "point"):                                 # these stay level: b only says which side is "ahead"
        b = (a[0] + math.copysign(effect.reach * s, b[0] - a[0] if b[0] != a[0] else 1.0), a[1])
    ink._NOISE.clear()                                                      # the noise cache is per work canvas: start clean
    E = effect.extent * s
    x0, y0 = math.floor(min(a[0], b[0]) - E), math.floor(min(a[1], b[1]) - E)
    W, H = math.ceil(max(a[0], b[0]) + E) - x0, math.ceil(max(a[1], b[1]) + E) - y0
    sp = Space((a[0] - x0, a[1] - y0), (b[0] - x0, b[1] - y0), s)
    ramp = Ramp.of(pal or effect.pal)
    dt = speed / fps                                                        # the frame grid is pinned to the hit: frame n_pre is t = 0
    n_pre = int(math.ceil(-effect.t0 / dt - 1e-6))
    n = n_pre + int(math.ceil(effect.end / dt - 1e-6)) + 1
    backs, fronts = [], []
    for i in range(n):
        fc, bc = fxcore.Canvas(W, H, ss), fxcore.Canvas(W, H, ss)
        effect.draw((i - n_pre) * dt, sp, ramp, seed, fc, bc, fps, only)
        backs.append(bc.done()); fronts.append(fc.done())
    al = np.zeros((H, W), bool)
    for im in backs + fronts: al |= np.asarray(im)[..., 3] > 0
    if al.any():
        ys, xs = np.nonzero(al)
        bx0, by0, bx1, by1 = max(0, xs.min() - pad), max(0, ys.min() - pad), min(W, xs.max() + 1 + pad), min(H, ys.max() + 1 + pad)
    else: bx0, by0, bx1, by1 = 0, 0, 2, 2
    bx0 -= (x0 + bx0) % 2; by0 -= (y0 + by0) % 2                            # even origin and even size: the @1x frame is exactly
    bx1 += (bx1 - bx0) % 2; by1 += (by1 - by0) % 2                          # half and lands on whole pixels
    box = (int(bx0), int(by0), int(bx1), int(by1))
    backs = [im.crop(box) for im in backs]; fronts = [im.crop(box) for im in fronts]
    frames = []
    for bk, fr in zip(backs, fronts):
        im = bk.copy(); im.alpha_composite(fr); frames.append(im)
    return dict(frames=frames, back=backs, front=fronts, size=(box[2] - box[0], box[3] - box[1]), fps=fps,
                anchor=(sp.a[0] - box[0], sp.a[1] - box[1]), target=(sp.b[0] - box[0], sp.b[1] - box[1]),
                hit_frame=n_pre + 1, origin=(x0 + box[0], y0 + box[1]))
