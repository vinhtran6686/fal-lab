#!/usr/bin/env python3
"""Keep a video-sprite set small: the source and the decisions stay, the intermediate frames go.
(see .claude/skills/video-sprite/SKILL.md, "Disk: prune and rebuild")

Usage:
  python scripts/video_prune.py prune   --set out/enemies/bandit/.work/side [--dry-run] [--force]
                                        [--drop-rejected-clips]
  python scripts/video_prune.py rebuild --set out/enemies/bandit/.work/side --action walk

prune keeps, per set:
  set_plan.json, set_state.json, takes.jsonl, exports.json, master/, reports/, actions/<id>/job/ (the input
  image, keyed master and transform sent to the model); review/ only until every action is exported (the
  chosen take's review sheet is copied to <sheet>/vNN/check/take_review.png)
and per take:
  prompt.txt, qc.json, route.json, media/ (the clip + job.json: the paid source, never re-bought)
  record/<stage>/... every JSON of every stage: matte report, registration, loop/retime selection and
  reports, finish (anchor, scale), animation.json. The decisions, not the pixels.
It deletes every stage folder (keyed, registered*, motion*, timed*, finished*, selection*, package*,
orphans): hundreds of PNG frames per take that the tools rebuild from the clip in seconds.
The chosen take of an action is pruned only after scripts/video_to_sheet.py exported it (exports.json),
unless --force. --drop-rejected-clips also deletes the clips of takes that were never chosen.

rebuild re-creates the deleted stages of an action's chosen take from its clip (no API call): it clears
the action's output and runs sprite_set.py, which re-runs every stage whose folder is gone. Then export
again with video_to_sheet.py (a new vNN) if the frames should change.
Prints one summary line; --dry-run lists what would go.
"""
import argparse, json, os, pathlib, shutil, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPRITE_SET = ROOT / ".claude" / "skills" / "video-sprite" / "scripts" / "sprite_set.py"
TAKE_KEEP = {"prompt.txt", "qc.json", "route.json"}
TAKE_KEEP_DIRS = {"media", "record"}


def read_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def tree_size(path: pathlib.Path) -> tuple[int, int]:
    files = [p for p in path.rglob("*") if p.is_file()]
    return len(files), sum(p.stat().st_size for p in files)


def mb(n: int) -> str:
    return f"{n / 1e6:.1f} MB"


def prune(a) -> None:
    set_dir = pathlib.Path(a.set)
    state_path = set_dir / "set_state.json"
    if not state_path.exists():
        sys.exit(f"{set_dir} is not a sprite set (no set_state.json)")
    state = read_json(state_path)
    exports = read_json(set_dir / "exports.json") if (set_dir / "exports.json").exists() else []
    exported = {(e["action"], e["take"]) for e in exports}
    before = tree_size(set_dir)
    plan, skipped = [], []   # plan: (take dir, stage dir or clip file, record)
    for ident, st in (state.get("actions") or {}).items():
        chosen = (st.get("chosen") or {}).get("take")
        exported_chosen = (ident, chosen) in exported and st.get("accepted")
        busy = st.get("status") not in ("done", "done-warn", "failed") and not exported_chosen
        for record in st.get("takes", []):
            take = set_dir / record["dir"]
            if not take.is_dir():
                continue
            is_chosen = record["take"] == chosen
            if busy and not a.force:
                skipped.append(f"{ident} t{record['take']:02d}: action is {st.get('status')!r}")
                continue
            if is_chosen and (ident, record["take"]) not in exported and not a.force:
                skipped.append(f"{ident} t{record['take']:02d}: chosen but not exported (video_to_sheet.py first)")
                continue
            for child in sorted(take.iterdir()):
                if child.is_dir() and child.name not in TAKE_KEEP_DIRS:
                    plan.append((take, child, record))
                elif child.is_file() and child.name not in TAKE_KEEP:
                    plan.append((take, child, record))
            if a.drop_rejected_clips and not is_chosen and (ident, record["take"]) not in exported:
                for clip in (take / "media").glob("*"):
                    if clip.suffix.lower() in (".mp4", ".webm", ".mov"):
                        plan.append((take, clip, record))
    for orphan in set_dir.rglob("*.orphan-*"):
        plan.append((orphan.parent, orphan, None))
    if not skipped:   # every action exported: the chosen take's review sheet now lives in <sheet>/vNN/check/
        plan += [(set_dir, path, None) for path in [set_dir / "review", *set_dir.glob("actions/*/job/review-guide.png")]
                 if path.exists()]

    gone_files = sum(tree_size(p)[0] if p.is_dir() else 1 for _, p, _ in plan)
    gone_bytes = sum(tree_size(p)[1] if p.is_dir() else p.stat().st_size for _, p, _ in plan)
    if a.dry_run:
        for _, p, _ in plan:
            n, b = tree_size(p) if p.is_dir() else (1, p.stat().st_size)
            print(f"  would delete {p.relative_to(set_dir).as_posix()}: {n} files, {mb(b)}")
        for line in skipped:
            print(f"  kept (skipped) {line}")
        print(f"dry run: {set_dir}: {before[0]} files, {mb(before[1])} -> {before[0] - gone_files} files, "
              f"{mb(before[1] - gone_bytes)}")
        return

    stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    for take, path, record in plan:
        if path.is_dir() and record is not None:
            for js in path.rglob("*.json"):   # the stage's decisions survive in record/<stage>/
                dest = take / "record" / path.name / js.relative_to(path)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(js, dest)
            shutil.rmtree(path)
            record.setdefault("pruned", {"stages": []})
            record["pruned"]["at"] = stamp
            if path.name not in record["pruned"]["stages"]:
                record["pruned"]["stages"].append(path.name)
        elif path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
            if record is not None and path.parent.name == "media":
                record.setdefault("pruned", {"stages": []})["clipDeleted"] = True
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    after = tree_size(set_dir)
    note = f"; skipped {len(skipped)}: " + " | ".join(skipped) if skipped else ""
    print(f"pruned {set_dir}: {before[0]} files, {mb(before[1])} -> {after[0]} files, {mb(after[1])}{note}")


def rebuild(a) -> None:
    set_dir = pathlib.Path(a.set)
    state_path = set_dir / "set_state.json"
    state = read_json(state_path)
    st = (state.get("actions") or {}).get(a.action)
    if not st or not st.get("chosen"):
        sys.exit(f"{a.action} has no chosen take in {set_dir}")
    record = next(t for t in st["takes"] if t["take"] == st["chosen"]["take"])
    if not (set_dir / record["clip"]["path"]).is_file():
        sys.exit(f"the clip of {a.action} take {record['take']} was deleted; it cannot be rebuilt")
    st["output"] = None   # sprite_set post-processes it again; stages whose folder is gone are re-run
    record.pop("pruned", None)
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    done = subprocess.run([sys.executable, str(SPRITE_SET), "run", "--plan", str(set_dir / "set_plan.json"),
                           "--actions", a.action], capture_output=True, text=True,
                          env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    line = (done.stdout.strip().splitlines() or [""])[-1]
    try:
        status = json.loads(line)["actions"][a.action]
    except (ValueError, KeyError):
        sys.exit(f"sprite_set.py run failed: {(done.stderr or line).strip()[-400:]}")
    if status.get("status") not in ("done", "done-warn"):
        sys.exit(f"rebuild of {a.action} ended {status.get('status')!r}: {status.get('message')}")
    print(f"rebuilt {a.action} take {record['take']} in {set_dir} from its clip (no API call); export it again "
          f"with video_to_sheet.py if the frames should change")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("prune", help="delete intermediate frames, keep the source and the decisions")
    pr.add_argument("--set", required=True)
    pr.add_argument("--dry-run", action="store_true")
    pr.add_argument("--force", action="store_true", help="also prune unexported chosen takes and busy actions")
    pr.add_argument("--drop-rejected-clips", action="store_true", help="delete clips of takes never chosen")
    rb = sub.add_parser("rebuild", help="re-create the pruned stages of an action from its clip")
    rb.add_argument("--set", required=True)
    rb.add_argument("--action", required=True)
    a = p.parse_args()
    {"prune": prune, "rebuild": rebuild}[a.cmd](a)


if __name__ == "__main__":
    main()
