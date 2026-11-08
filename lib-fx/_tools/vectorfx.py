#!/usr/bin/env python3
"""CLI for the lib-fx vector kit (lib-fx/_core/vector). 0 USD, no model.

  python lib-fx/_tools/vectorfx.py palette  PROFILE [--variant V] [--frame N]   flat-colour candidates + colour clusters (to write a profile)
  python lib-fx/_tools/vectorfx.py ingest   PROFILE                             cut source.gif into frames (source.crops)
  python lib-fx/_tools/vectorfx.py measure  PROFILE [--frames 3-5]              fit layer gradients + halo, write them into PROFILE
  python lib-fx/_tools/vectorfx.py rebuild  PROFILE [--frames 2-12] [--variants a,b] [--refit]
  python lib-fx/_tools/vectorfx.py review   PROFILE                             panels, GIFs, review/index.html
  python lib-fx/_tools/vectorfx.py all      PROFILE                             rebuild + review
  python lib-fx/_tools/vectorfx.py lifecycle PROFILE                            how the reference was animated (phases, area, pieces, holds)

PROFILE: path, or a name in lib-fx/_core/vector/profiles/ (e.g. swirl-slash). Outputs: lib-fx/_study/<name>/vector/ (not in git)."""
import argparse, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "_core"))
from vector import Profile, measure, pipeline, review  # noqa: E402


def rng(s):
    if not s:
        return None
    a, _, b = s.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["palette", "ingest", "measure", "rebuild", "review", "all", "lifecycle"])
    ap.add_argument("profile")
    ap.add_argument("--frames"); ap.add_argument("--variants"); ap.add_argument("--variant"); ap.add_argument("--frame", type=int)
    ap.add_argument("--refit", action="store_true")
    a = ap.parse_args()
    p = pathlib.Path(a.profile)
    if not p.exists():
        p = HERE / "_core/vector/profiles" / f"{a.profile}.json"
    prof = Profile(p)
    fr, vs = rng(a.frames), (a.variants.split(",") if a.variants else None)
    if a.cmd == "palette":
        v = a.variant or prof.variants[0]
        f = a.frame or prof.frames()[len(prof.frames()) // 3]
        rgb = measure.load_frame(prof, v, f)
        cands = measure.palette_candidates(rgb, measure.background(prof, v))
        for c in cands:
            print(c)
        out = prof.out_dir() / f"palette_{v}_{f:02d}.png"
        measure.palette_sheet(rgb, cands, out)
        print("candidate masks:", out)
        print("colour clusters (brightest first; dark ones are usually glow):")
        for c, share in measure.colour_clusters(rgb, measure.background(prof, v)):
            print(" ", c, share)
    elif a.cmd == "ingest":
        print(measure.ingest(prof), "frames")
    elif a.cmd == "measure":
        import json
        print(json.dumps(measure.measure_profile(prof, fr), indent=1))
    elif a.cmd in ("rebuild", "all"):
        pipeline.rebuild(prof, fr, vs, a.refit)
    elif a.cmd == "lifecycle":
        import json
        from vector import lifecycle
        out, path = lifecycle.report(prof, fr)
        for v, d in out.items():
            print(v, json.dumps(d["phases"]))
        print("frames:", path)
    if a.cmd in ("review", "all"):
        print(review.build(prof, fr))


if __name__ == "__main__":
    main()
