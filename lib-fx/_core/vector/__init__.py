"""lib-fx vector kit: rebuild / draw hand-drawn flat-colour VFX as clean Bezier paths.

Pipeline (one effect = one JSON profile in profiles/):
    measure  : read the reference right (layer colour polylines incl. edge gradients, inner gradients, halo)
    fit      : each layer -> tapered strokes in the effect's own frame (polar for swirls, linear for thrusts)
    smooth   : Smooth & Simplify (Illustrator Simplify / Potrace curve optimisation / minimum-variation fairing)
    compose  : stacked layers (lower layers run under upper ones), inner gradient, halo -> PNG + SVG
    review   : panels, motion GIFs, review page with OK / needs-work notes
CLI: python lib-fx/_tools/vectorfx.py --help.  Method and lessons: README.md here,
lib-fx/research/bezier-shapes/RETROSPECTIVE.md (archive of the research that produced this kit)."""
__version__ = "1.1"

from .profile import Profile
from .strokes import to_path, crescent, tongue, feather, notch, width_profile, peak_scale
from .frames import PolarFrame, LinearFrame, make_frame
from .smooth import smooth_simplify
from .metrics import iou, path_fairness
from . import measure, fit, compose, pipeline, review, lifecycle, tracking

__all__ = ["Profile", "to_path", "crescent", "tongue", "feather", "notch", "width_profile", "peak_scale", "PolarFrame",
           "LinearFrame", "make_frame", "smooth_simplify", "iou", "path_fairness", "measure", "fit", "compose", "pipeline",
           "review", "lifecycle", "tracking"]
