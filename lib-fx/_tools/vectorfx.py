#!/usr/bin/env python3
"""CLI for the lib-fx vector kit (lib-fx/_core/vector). 0 USD, no model.

  python lib-fx/_tools/vectorfx.py gen-slash NAME [--variant blue|pink|gold] [--frame SEED]   generate a NEW slash from the foundation rules
  python lib-fx/_tools/vectorfx.py init     GIF NAME                            draft profile: auto crops (+ reflections), frames, suggested layers
  python lib-fx/_tools/vectorfx.py check    PROFILE                             bright pixels no layer claims, per frame (+ image of the worst frame)
  python lib-fx/_tools/vectorfx.py palette  PROFILE [--variant V] [--frame N]   flat-colour candidates + colour clusters (to write a profile)
  python lib-fx/_tools/vectorfx.py ingest   PROFILE                             cut source.gif into frames (source.crops)
  python lib-fx/_tools/vectorfx.py measure  PROFILE [--frames 3-5]              fit layer gradients + halo, write them into PROFILE
  python lib-fx/_tools/vectorfx.py rebuild  PROFILE [--frames 2-12] [--variants a,b] [--refit]
  python lib-fx/_tools/vectorfx.py review   PROFILE                             panels, GIFs, review/index.html
  python lib-fx/_tools/vectorfx.py all      PROFILE                             rebuild + review
  python lib-fx/_tools/vectorfx.py lifecycle PROFILE                            how the reference was animated (phases, area, pieces, holds)
  python lib-fx/_tools/vectorfx.py track     PROFILE                            follow every piece: growth, splits, shrink, drift, death
  python lib-fx/_tools/vectorfx.py study     PROFILE                            birth, erosion and peak composition (foundation/05)
  python lib-fx/_tools/vectorfx.py showcase  PROFILE                            export GIFs, frames and SVGs into lib-fx/_core/vector/showcase/ (tracked)

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
    ap.add_argument("cmd", choices=["gen-slash", "init", "check", "palette", "ingest", "measure", "rebuild", "review", "all", "lifecycle", "track", "showcase", "study"])
    ap.add_argument("profile")
    ap.add_argument("name", nargs="?", help="init only: profile name")
    ap.add_argument("--frames"); ap.add_argument("--variants"); ap.add_argument("--variant"); ap.add_argument("--frame", type=int)
    ap.add_argument("--refit", action="store_true")
    a = ap.parse_args()
    if a.cmd == "gen-slash":
        import shutil
        from vector import gen_slash
        out, stats = gen_slash.build(a.profile, a.variant or "blue", a.frame or 7)
        dst = HERE / "_core/vector/showcase/generated" / a.profile
        if dst.exists():
            shutil.rmtree(dst)
        dst.mkdir(parents=True)
        for f in ("preview.gif", "preview_slow.gif", "design.json"):
            shutil.copy(out / f, dst / f)
        shutil.copytree(out / "svg", dst / "svg")
        shutil.copytree(out / "frames", dst / "frames")
        pk = max(s["area"] for s in stats)
        for s in stats:
            print(f"drawing {s['drawing']} frames {s['frames']} area {s['area'] / pk:.3f} pieces {s['pieces']}")
        print("out:", out, "| showcase:", dst)
        return
    if a.cmd == "init":
        from vector import auto
        name = a.name or pathlib.Path(a.profile).parent.name
        out = HERE / "_core/vector/profiles" / f"{name}.json"
        prof = auto.init_profile(a.profile, name, out)
        print("draft profile:", out)
        for v in prof.variants:
            print(" ", v, prof.d["source"]["crops"][v], {l: x["colours"] for l, x in prof.layers(v).items()})
        print("next: check the layers by eye (palette / check), then measure, all")
        return
    p = pathlib.Path(a.profile)
    if not p.exists():
        p = HERE / "_core/vector/profiles" / f"{a.profile}.json"
    prof = Profile(p)
    fr, vs = rng(a.frames), (a.variants.split(",") if a.variants else None)
    if a.cmd == "check":
        from vector import auto
        for v in vs or prof.variants:
            img = prof.out_dir() / f"check_{v}.png"
            rows = auto.mask_check(prof, v, fr, image=img)
            tot = rows[-1] if rows else {"unclaimed_share": 0, "colours": []}
            dom = tot["colours"][0][1] / max(tot["unclaimed_px"], 1) if tot["colours"] else 0
            # a missing layer = ONE colour dominating the unclaimed pixels; spread colours are edge blends / bright glow
            flag = ("  <-- MISSING LAYER likely: add %s" % (tot["colours"][0][0],)) if tot["unclaimed_share"] > 0.05 and dom > 0.4 else "  ok"
            print(v, "unclaimed", tot["unclaimed_share"], "top colour share", round(dom, 2), "top colours", tot["colours"][:3], flag)
            print("   image:", img)
    elif a.cmd == "palette":
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
    elif a.cmd == "track":
        import json
        from vector import tracking
        out, path = tracking.report(prof, fr)
        for v, d in out.items():
            print(v, json.dumps(d["summary"]))
        print("events:", path)
    elif a.cmd == "study":
        import json
        from vector import shape_study
        out, path = shape_study.study(prof, fr)
        for v, d in out.items():
            print(v, json.dumps({kk: d[kk] for kk in ("erosion", "composition")}))
            print("   birth", json.dumps(d["birth"]["frames"]))
        print("data:", path)
    elif a.cmd == "showcase":
        from vector import showcase
        for d in showcase.export(prof, fr):
            print(d)
    if a.cmd in ("review", "all"):
        print(review.build(prof, fr))


if __name__ == "__main__":
    main()
