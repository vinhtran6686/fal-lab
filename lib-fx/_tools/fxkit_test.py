#!/usr/bin/env python3
"""Regression test of fxkit (lib-fx/_core/formulas/draw/FXKIT.md). Plain asserts, one line per check, exit 1 on a failure. 0 USD.

Usage (repo root):
  python lib-fx/_tools/fxkit_test.py [kind ...]     every registered layer kind (or the named ones), then the palettes and every kit family

Per kind (one layer, role primary, Life(0, 0.066, 0.034, 0.3), default parameters, reach 140, extent 240):
  a deterministic (same seed twice = same frames)   b seeded (seed 0 vs 1 differ; WARNING when identical)
  c first frame drawn, last frame empty             d follows the points (centroids printed, never a failure)
  e scales (s = 0.5 gives under 45 % of the box area)
Then every palette must pass Ramp.of(p).problems() (WARNING only), and every effect of every fxkit family under lib-fx must have an
empty lint() and render with the default --from / --to.
"""
import pathlib, sys
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))               # lib-fx/build.py
import build                                        # also puts the draw folder and _tools on sys.path
import fxkit, palettes
from fxkit import Effect, Layer, Life, Ramp

fails = 0
def say(ok, msg, level=None):
    global fails
    tag = level or ("ok  " if ok else "FAIL")
    print(f"{tag} {msg}")
    if not ok and level is None: fails += 1


def stack(r):
    return np.stack([np.asarray(f) for f in r["frames"]])


def box_area(r):
    al = (stack(r)[..., 3] > 0).any(axis=0); ys, xs = np.nonzero(al)
    return (xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1) if len(xs) else 0


def centroid(r):
    """Alpha-weighted centroid of all frames relative to the anchor (px)."""
    w = stack(r)[..., 3].astype(float).sum(axis=0); tot = w.sum()
    if not tot: return (0.0, 0.0)
    ys, xs = np.indices(w.shape)
    return (float((xs * w).sum() / tot - r["anchor"][0]), float((ys * w).sum() / tot - r["anchor"][1]))


def test_kind(k):
    e = Effect("t_" + k, layers=[Layer(k, role="primary", life=Life(0, 0.066, 0.034, 0.3))], reach=140, extent=240)
    try:
        r0 = fxkit.render(e, seed=0); r0b = fxkit.render(e, seed=0); r1 = fxkit.render(e, seed=1)
    except Exception as ex:
        say(False, f"{k}: renders ({type(ex).__name__}: {ex})"); return
    same = lambda p, q: len(p["frames"]) == len(q["frames"]) and all(np.array_equal(np.asarray(x), np.asarray(y)) for x, y in zip(p["frames"], q["frames"]))
    say(same(r0, r0b), f"{k}: deterministic")
    say(not same(r0, r1), f"{k}: seed 0 and seed 1 differ" if not same(r0, r1) else f"{k}: seeds 0 and 1 give identical frames (nothing random?)",
        None if not same(r0, r1) else "WARNING")
    A = [np.asarray(f)[..., 3].any() for f in r0["frames"]]
    say(A[0] and not A[-1], f"{k}: first frame drawn, last frame empty ({sum(A)} of {len(A)} frames drawn)")
    try:
        rx = fxkit.render(e, (0, 0), (140, 0)); ry = fxkit.render(e, (0, 0), (0, -140))
        ok = box_area(rx) > 0 and box_area(ry) > 0
        cx, cy = centroid(rx), centroid(ry)
        say(ok, f"{k}: follows the points: centroid to the right ({cx[0]:.0f}, {cx[1]:.0f}), upward ({cy[0]:.0f}, {cy[1]:.0f})")
    except Exception as ex:
        say(False, f"{k}: renders with a, b ({type(ex).__name__}: {ex})")
    try:
        ra, rb = fxkit.render(e, s=1.0), fxkit.render(e, s=0.5)
        ratio = box_area(rb) / max(1, box_area(ra))
        say(ratio < 0.45, f"{k}: scales: s 0.5 covers {ratio * 100:.0f} % of the area of s 1")
    except Exception as ex:
        say(False, f"{k}: renders at s 0.5 ({type(ex).__name__}: {ex})")


def main():
    want = sys.argv[1:]
    kinds = list(fxkit.KINDS)
    for w in want:
        if w not in fxkit.KINDS: sys.exit(f"no kind '{w}'. Kinds: {', '.join(kinds)}")
    for k in (want or kinds): test_kind(k)
    if want: sys.exit(1 if fails else 0)
    for name in palettes.PALETTES:
        probs = Ramp.of(name).problems()
        say(not probs, f"palette {name}: Ramp problems: {'; '.join(probs) if probs else 'none'}", "ok  " if not probs else "WARNING")
    for fam, mod in build.families().items():
        if not build.is_kit(mod): continue
        for name, e in mod.EFFECTS.items():
            lint = e.lint()
            say(not lint, f"{fam}/{name}: lint {'clean' if not lint else '; '.join(lint)}")
            try:
                r = fxkit.render(e); ok = len(r["frames"]) > 0
            except Exception as ex:
                ok = False; print(f"     {type(ex).__name__}: {ex}")
            say(ok, f"{fam}/{name}: renders with the default --from / --to")
    print("FAILED" if fails else "all checks passed")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
