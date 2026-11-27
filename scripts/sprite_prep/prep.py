#!/usr/bin/env python3
"""Sprite prep from the command line: the same steps as the Frame Tuner page (tools/frame_tuner/), same files.

  python scripts/sprite_prep/prep.py list                                   workspaces and their status board
  python scripts/sprite_prep/prep.py split <ws> [clip ...] [--hero H]       cut every frame of the clips (cache)
  python scripts/sprite_prep/prep.py flags <ws> <clip> <hero>               suspicious frames
  python scripts/sprite_prep/prep.py fit <ws> <hero>                        canvas every prepared action needs
  python scripts/sprite_prep/prep.py export <ws> <hero> [action ...] [--asset DIR]   write the sheets
<ws> is the workspace folder (e.g. out/heroes/_lineups/heroic_ref_five). Costs nothing (no model is called).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sprite_prep.workspace import Workspace  # noqa: E402
from sprite_prep import split as sp, analyze, export as ex  # noqa: E402


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["list", "split", "flags", "fit", "export"])
    p.add_argument("args", nargs="*")
    p.add_argument("--hero")
    p.add_argument("--asset", help="export into this folder instead of the hero's asset (testing)")
    a = p.parse_args()
    if a.cmd == "list":
        for ws in Workspace.discover():
            s = ws.summary()
            print(f"{s['id']}  ({s['title']})")
            for h, acts in s["board"].items():
                print("   ", h.ljust(16), "  ".join(f"{k}:{v['stage']}" for k, v in acts.items()))
        return
    ws = Workspace.load(a.args[0])
    if a.cmd == "split":
        clips = a.args[1:] or list(ws.cfg["clips"])
        for c in clips:
            sp.split_clip(ws, c, [a.hero] if a.hero else None, progress=lambda f, t: print(f"\r{t:60s}", end="", flush=True))
            print()
    elif a.cmd == "flags":
        for r in analyze.clip_flags(ws, a.args[1], a.args[2]):
            if r["flags"]:
                print(r["f"], ",".join(r["flags"]), r["ratio"])
    elif a.cmd == "fit":
        print(json.dumps(ex.fit(ws, a.args[1]), indent=1))
    elif a.cmd == "export":
        hero = a.args[1]
        acts = a.args[2:] or [x for x in ws.cfg["actions"][hero] if ws.seq(hero, x)]
        for act in ex.export_order(ws, hero, acts):
            r = ex.export(ws, hero, act, Path(a.asset) if a.asset else None)
            print(act, "->", r["out"])
            if r["warn"]:
                print("  ", r["warn"])


if __name__ == "__main__":
    main()
