"""fxkit: the effect system of lib-fx. An effect = a stack of layers (role, life, place) drawn between two points a -> b in a
palette ramp, every shape varied by a seed. Guide: lib-fx/_core/formulas/draw/FXKIT.md.

  from fxkit import Effect, Layer, Life, render          # authoring and rendering
  from fxkit import kind, Ctx, Rand, sizes, angles, delays, Ramp, Space   # writing a layer kind
"""
from .vary import Rand, sizes, angles, delays, varied
from .timing import Life, Phase, clamp, smooth, out_cubic, out_quint, out_expo, out_back, in_quad, in_cubic
from .space import Space
from .ramp import Ramp, mix, lum
from .effect import Effect, Layer, Ctx, kind, render, KINDS, ROLES, SPACES
from . import shapes
from .ink import Ink, THIN, erode, noise, drop_specks, smooth_mask
from . import layers  # noqa: F401  (registers every layer kind)
