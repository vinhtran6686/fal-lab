#!/usr/bin/env python3
"""Quality gate for lib-fx effects: measures every frame of an effect and reports what the eye would catch late. 0 USD.

Usage (repo root):
  python lib-fx/_tools/fxcheck.py                      every effect in catalog.json (frames on disk)
  python lib-fx/_tools/fxcheck.py impact/ground        a group, a family or one effect
  python lib-fx/_tools/fxcheck.py DIR --frames         any folder of RGBA frames (e.g. a character's frames/fx/<skill>/<layer>/frames/@2x)
  ... --strict                                         exit 1 when any effect FAILS (for scripts)

`build.py` runs the same checks on what it has just rendered and stores the result in meta.json / catalog.json ("qa").

What is measured (weight of a frame = sum of its alpha, so a faint big shape and a small solid one count alike):
  FAIL clip     the effect touches the border of its frame: it is cut off. Enlarge "frame" or move "anchor".
  FAIL end      a one-shot effect is still visible on its last frame (> 0.4 % of its peak): it pops off instead of dissolving.
                Sustained / looping effects (tag sustained, loop or hold) are exempt.
  FAIL anchor   the anchor lies outside the frame.
  WARN pop      between two frames after the peak the effect loses more than 45 % of its peak weight: a visible jump.
  WARN cut      the last visible frame still holds more than 5 % of the peak, the next one is empty: it is switched off.
  WARN linger   the last quarter (or more) of the frames carries under 2 % of the peak: dead air, shorten "dur".
  WARN empty0   the first frame is empty: the effect starts one frame late against the hit frame.
  WARN flicker  the weight goes up and down by more than 12 % of the peak three times or more: it flashes.
  WARN tiny     at game size (@1x, body H = 60 px) the peak frame is under 10 px in both directions: unreadable.
  WARN speck    at game size, 30 % or more of the frames are visible but under 3 px of solid area in total: stray specks.
Numbers reported: frames, peak frame, size of the peak frame at @1x, weight left on the last frame (% of peak).
"""
import json, pathlib, sys
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent.parent
EXEMPT_END = {"sustained", "loop", "hold"}


def check(frames, tags=(), anchor=None):
    """frames: list of RGBA PIL images of one effect (@2x). Returns {"fail": [...], "warn": [...], numbers}."""
    A = [np.asarray(f.convert("RGBA"))[..., 3].astype(np.float32) / 255 for f in frames]
    n = len(A); H, W = A[0].shape
    wt = np.array([a.sum() for a in A]); peak = float(wt.max()) or 1.0; ip = int(wt.argmax())
    fail, warn = [], []
    edge = max(float(max(a[0].max(), a[-1].max(), a[:, 0].max(), a[:, -1].max())) for a in A)
    if edge > 0.05: fail.append(f"clip: touches the frame border (alpha {edge:.2f})")
    one_shot = not (EXEMPT_END & set(tags))
    last = float(wt[-1] / peak)
    if one_shot and last > 0.004: fail.append(f"end: {last * 100:.1f} % of the peak is still visible on the last frame")
    if anchor is not None and not (0 <= anchor[0] <= W and 0 <= anchor[1] <= H): fail.append(f"anchor {list(anchor)} outside {W}x{H}")
    if one_shot:
        drops = [(float(wt[i] - wt[i + 1]) / peak, i) for i in range(ip, n - 1)]
        if drops:
            d, i = max(drops)
            if d > 0.45: warn.append(f"pop: frame {i + 1} -> {i + 2} loses {d * 100:.0f} % of the peak")
        vis = [i for i in range(n) if wt[i] > 0.001 * peak]
        if vis and vis[-1] < n - 1 and wt[vis[-1]] > 0.05 * peak:
            warn.append(f"cut: frame {vis[-1] + 1} still holds {wt[vis[-1]] / peak * 100:.0f} % of the peak, frame {vis[-1] + 2} is empty")
        tail = 0
        for w in wt[::-1]:
            if w < 0.02 * peak: tail += 1
            else: break
        if tail >= max(4, n // 4): warn.append(f"linger: the last {tail} of {n} frames carry under 2 % of the peak")
        if wt[0] <= 0: warn.append("empty0: the first frame is empty")
        turns, last_ext, going = 0, float(wt[0]), 0
        for w in wt[1:]:
            w = float(w)
            if going >= 0 and w < last_ext - 0.12 * peak: turns += going > 0; going = -1; last_ext = w
            elif going <= 0 and w > last_ext + 0.12 * peak: turns += going < 0; going = 1; last_ext = w
            elif (going > 0 and w > last_ext) or (going < 0 and w < last_ext): last_ext = w
        if turns >= 3: warn.append(f"flicker: the weight reverses {turns} times by more than 12 % of the peak")
    def at1x(a): return a[:H // 2 * 2, :W // 2 * 2].reshape(H // 2, 2, W // 2, 2).mean(axis=(1, 3))
    pk = at1x(A[ip]) > 0.25
    ys, xs = np.nonzero(pk)
    size1x = [int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)] if len(xs) else [0, 0]
    if max(size1x) < 10: warn.append(f"tiny: the peak frame is {size1x[0]}x{size1x[1]} px at game size")
    speck = sum(1 for a in A if a.sum() > 0 and 0 < (at1x(a) > 0.25).sum() < 3)
    if speck >= max(3, round(0.3 * n)): warn.append(f"speck: {speck} of {n} frames show under 3 px at game size")
    return {"fail": fail, "warn": warn, "frames": n, "peak_frame": ip + 1, "peak_size_1x": size1x, "last_frame_pct": round(last * 100, 2)}


def line(name, r):
    st = "FAIL" if r["fail"] else "warn" if r["warn"] else "ok  "
    head = f"{st} {name:34s} {r['frames']:3d} fr  peak@{r['peak_frame']:<3d} {r['peak_size_1x'][0]:3d}x{r['peak_size_1x'][1]:<3d}@1x  end {r['last_frame_pct']:5.1f}%"
    return "\n".join([head] + [f"       FAIL {m}" for m in r["fail"]] + [f"       warn {m}" for m in r["warn"]])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict, raw = "--strict" in sys.argv, "--frames" in sys.argv
    bad = 0
    if raw:
        d = pathlib.Path(args[0]); fs = sorted(d.glob("*.png"))
        if not fs: sys.exit(f"no PNG frames in {d}")
        r = check([Image.open(f) for f in fs]); print(line(d.as_posix(), r)); bad += bool(r["fail"])
    else:
        want = args[0].strip("/") if args else ""
        cat = json.loads((HERE / "catalog.json").read_text(encoding="utf8"))
        hit = False
        for k, v in cat.items():
            if want and not (k == want or k.startswith(want + "/")): continue
            fs = sorted((HERE / v["dir"] / "frames").glob("*.png"))
            if not fs: print(f"FAIL {k}: no frames on disk (run lib-fx/build.py {k})"); bad += 1; continue
            hit = True
            r = check([Image.open(f) for f in fs], v.get("tags", ()), v.get("anchor_2x")); print(line(k, r)); bad += bool(r["fail"])
        if not hit and not bad: sys.exit(f"nothing in catalog.json matches '{want}'")
    if strict and bad: sys.exit(1)


if __name__ == "__main__":
    main()
