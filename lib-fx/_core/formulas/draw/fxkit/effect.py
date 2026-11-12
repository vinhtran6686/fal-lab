"""fxkit / effect: an effect is a STACK OF LAYERS, each with one role, its own life and its own place.

  Effect("heavy", space="aim", layers=[
      Layer("glow",   role="glow",      z="back",  life=Life(0.0, 0.05, 0.05, 0.25), r=90),
      Layer("spikes", role="primary",              life=Life(0.0, 0.07, 0.03, 0.22), n=9, length=110),
      Layer("sparks", role="particles",            life=Life(0.03, 0.05, 0.0, 0.45), n=12),
      Layer("flash",  role="flash",                life=Life(0.0, 0.03, 0.0, 0.07), r=34)])

A layer KIND is a drawing function registered with @kind("name"): fn(c: Ctx, ph: Phase, **params). It draws on c.cv with
positions from c.sp (Space), colours from c.pal (Ramp), variation from c.rng(...) and sizes times c.s. Layer kinds live in
fxkit/layers/*.py. Roles (what a layer is FOR; lint counts them): ground, glow, smoke, secondary, primary, core, particles,
flash, accent. Layers are drawn in list order; z = "back" puts a layer behind the character, "front" in front of it.
"""
import math
from dataclasses import dataclass, field, replace
import numpy as np
from PIL import Image
import fxcore
from .ramp import Ramp
from .space import Space
from .timing import Life
from .vary import Rand

KINDS = {}
ROLES = ("ground", "glow", "smoke", "secondary", "primary", "core", "particles", "flash", "accent")
SPACES = ("point", "aim", "span", "travel", "ground")


def kind(name):
    """Register a layer kind: @kind("spikes") def spikes(c, ph, n=8, length=100, ...)."""
    def deco(fn):
        KINDS[name] = fn; return fn
    return deco


class Layer:
    def __init__(self, kind, role, life, id=None, z="front", at="a", **p):
        assert role in ROLES, f"unknown role {role}"; assert z in ("front", "back")
        self.kind, self.role, self.life, self.id, self.z, self.at, self.p = kind, role, life, id or kind, z, at, p

    def but(self, **changes):
        """A copy with some fields or parameters changed (life=, z=, at= or any parameter of the kind)."""
        new = Layer(self.kind, self.role, self.life, self.id, self.z, self.at, **self.p)
        for k, v in changes.items():
            if k in ("life", "z", "at", "role"): setattr(new, k, v)
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

    def rng(self, *keys):
        return Rand(self.seed, self.effect.name, self.layer.id, *keys)


class Effect:
    def __init__(self, name, layers, title="", desc="", space="point", reach=140, extent=220, pal="sun", tags=(), status="draft", weight="medium"):
        """space: how the effect uses its two points: point (a only), aim (a + the direction to b), span (stretched from a to b),
        travel (moves from a to b, then hits at b), ground (a on the floor line, level). reach: the default distance a -> b in
        px at s = 1 (library build). extent: how far in px the effect may reach around a and b (work canvas; the result is
        cropped to what was drawn). pal: default palette name. weight: light | medium | heavy (lint wants more roles for heavy)."""
        assert space in SPACES
        ids = [l.id for l in layers]; assert len(ids) == len(set(ids)), f"{name}: layer ids must be unique: {ids}"
        self.name, self.layers, self.title, self.desc, self.space = name, list(layers), title or name, desc, space
        self.reach, self.extent, self.pal, self.tags, self.status, self.weight = reach, extent, pal, list(tags), status, weight

    t0 = property(lambda self: min(0.0, min(l.life.start for l in self.layers)))      # s before the hit when the effect starts
    end = property(lambda self: max(l.life.end for l in self.layers))

    def variant(self, name=None, layers=None, **attrs):
        """A sibling effect: layers = {layer id: False (drop it) | {param or life/z/at changes}}; attrs replace effect fields."""
        layers = layers or {}
        unknown = set(layers) - {l.id for l in self.layers}; assert not unknown, f"{self.name}: no layer {unknown}"
        ls = [l.but(**layers[l.id]) if isinstance(layers.get(l.id), dict) else l for l in self.layers if layers.get(l.id, True) is not False]
        e = Effect(name or self.name, ls, self.title, self.desc, self.space, self.reach, self.extent, self.pal, self.tags, self.status, self.weight)
        for k, v in attrs.items(): setattr(e, k, v)
        return e

    def draw(self, t, sp, pal, seed, front, back, fps=30.0, only=None):
        """Draw every live layer at effect time t (seconds from the hit) onto the two canvases."""
        for l in self.layers:
            if only is not None and l.id not in only: continue
            ph = l.life.at(t, fps)
            if ph is None: continue
            KINDS[l.kind](Ctx(self, l, sp, pal, seed, front, back, fps), ph, **l.p)

    def lint(self):
        """Design rules every effect must pass (empty list = fine)."""
        out, L = [], self.layers
        for l in L:
            if l.kind not in KINDS: out.append(f"layer {l.id}: unknown kind '{l.kind}'")
            if l.life.release < 2 / 30 - 1e-9: out.append(f"layer {l.id}: release under 2 frames (it would pop off)")
        roles = {l.role for l in L}
        need = {"light": 3, "medium": 4, "heavy": 5}[self.weight]
        if len(roles) < need: out.append(f"{len(roles)} roles ({', '.join(sorted(roles))}); a {self.weight} effect needs {need}+ for depth")
        if "sustained" not in self.tags:
            if not any(l.role in ("flash", "core") and abs(l.life.start) <= 1 / 30 + 1e-9 for l in L): out.append("no flash / core layer on the hit frame (the hit does not read)")
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
    The frame is cropped to what was drawn (+pad), so nothing is ever clipped and no frame size has to be chosen."""
    a = (0.0, 0.0) if a is None else a
    b = (a[0] + effect.reach * s, a[1]) if b is None else b
    E = effect.extent * s
    x0, y0 = math.floor(min(a[0], b[0]) - E), math.floor(min(a[1], b[1]) - E)
    W, H = math.ceil(max(a[0], b[0]) + E) - x0, math.ceil(max(a[1], b[1]) + E) - y0
    sp = Space((a[0] - x0, a[1] - y0), (b[0] - x0, b[1] - y0), s)
    ramp = Ramp.of(pal or effect.pal)
    n = int(math.ceil((effect.end - effect.t0) * fps / speed - 1e-6)) + 1
    backs, fronts = [], []
    for i in range(n):
        fc, bc = fxcore.Canvas(W, H, ss), fxcore.Canvas(W, H, ss)
        effect.draw(effect.t0 + i * speed / fps, sp, ramp, seed, fc, bc, fps, only)
        backs.append(bc.done()); fronts.append(fc.done())
    al = np.zeros((H, W), bool)
    for im in backs + fronts: al |= np.asarray(im)[..., 3] > 0
    if al.any():
        ys, xs = np.nonzero(al)
        bx0, by0, bx1, by1 = max(0, xs.min() - pad), max(0, ys.min() - pad), min(W, xs.max() + 1 + pad), min(H, ys.max() + 1 + pad)
    else: bx0, by0, bx1, by1 = 0, 0, 2, 2
    bx1 += (bx1 - bx0) % 2; by1 += (by1 - by0) % 2                          # even size: the @1x frame is exactly half
    box = (int(bx0), int(by0), int(bx1), int(by1))
    backs = [im.crop(box) for im in backs]; fronts = [im.crop(box) for im in fronts]
    frames = []
    for bk, fr in zip(backs, fronts):
        im = bk.copy(); im.alpha_composite(fr); frames.append(im)
    return dict(frames=frames, back=backs, front=fronts, size=(box[2] - box[0], box[3] - box[1]), fps=fps,
                anchor=(sp.a[0] - box[0], sp.a[1] - box[1]), target=(sp.b[0] - box[0], sp.b[1] - box[1]),
                hit_frame=int(round(-effect.t0 * fps / speed)) + 1, origin=(x0 + box[0], y0 + box[1]))
