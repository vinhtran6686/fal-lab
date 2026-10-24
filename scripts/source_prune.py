"""Keep only what was approved in an asset's source/ (fal-image format.md section 4, "one session, one finished step").

Every paid still or take is saved into <asset>/source/ the moment it exists (cost guard). At the end of a session the
asset's source/ holds only what was chosen, the rest is dropped (it stays in git history if it was ever committed):

  kept = meta.json states[*].source          (every exported sheet's clip or still; video_to_sheet / sprite_pack write it)
       + meta.json sources.{design,video,fx,vfx}   (approved or pending items without a sheet yet: master, poses, a ⏳ clip)
       + the sidecars of a kept file (same stem: .json, .prompt.txt) and design/prompts/<still>_pNN.txt of a kept still

Usage:
  python scripts/source_prune.py out/heroes/<id>                                   # dry run: what would go
  python scripts/source_prune.py out/heroes/<id> --keep source/design/master_v08.png  # mark approved (meta.json sources)
  python scripts/source_prune.py out/heroes/<id> --apply                           # delete everything not kept
"""
import argparse, json, pathlib, re, shutil

KINDS = ("design", "video", "fx", "vfx")


def load(asset: pathlib.Path) -> dict:
    return json.loads((asset / "meta.json").read_text(encoding="utf-8"))


def keep_set(asset: pathlib.Path, meta: dict) -> dict:
    keep = {k: set(meta.get("sources", {}).get(k, [])) for k in KINDS}
    for st in meta.get("states", {}).values():
        src = str(st.get("source") or "")
        m = re.match(r"source/(\w+)/([^/]+)", src)
        if m and m.group(1) in keep:
            keep[m.group(1)].add(m.group(2))
    for k in ("design", "video"):   # sidecars: same stem
        stems = {pathlib.Path(n).name.split(".")[0] for n in keep[k]}
        d = asset / "source" / k
        if d.exists():
            keep[k] |= {p.name for p in d.iterdir() if p.is_file() and p.name.split(".")[0] in stems}
    return keep


def plan(asset: pathlib.Path) -> list:
    meta = load(asset)
    keep, out = keep_set(asset, meta), []
    for k in KINDS:
        d = asset / "source" / k
        if not d.exists():
            continue
        for p in sorted(d.iterdir()):
            if k == "design" and p.is_dir() and p.name == "prompts":   # prompts/<still>_pNN.txt
                stills = {re.sub(r"_v\d+$", "", pathlib.Path(n).stem) for n in keep[k]}
                out += [q for q in sorted(p.iterdir()) if re.sub(r"_p\d+$", "", q.stem) not in stills]
            elif p.name not in keep[k] and p.name != "__pycache__":
                out.append(p)
    return out


def main() -> None:
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("asset"); a.add_argument("--keep", action="append", default=[], metavar="source/<kind>/<file>")
    a.add_argument("--apply", action="store_true")
    args = a.parse_args()
    asset = pathlib.Path(args.asset)
    if args.keep:
        meta = load(asset)
        for rel in args.keep:
            m = re.match(r"(?:source/)?(\w+)/([^/]+)$", rel.replace("\\", "/"))
            if not m or m.group(1) not in KINDS or not (asset / "source" / m.group(1) / m.group(2)).exists():
                raise SystemExit(f"--keep {rel}: not a file under {asset}/source/{{{','.join(KINDS)}}}")
            lst = meta.setdefault("sources", {}).setdefault(m.group(1), [])
            if m.group(2) not in lst:
                lst.append(m.group(2)); lst.sort()
        (asset / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("kept:", ", ".join(args.keep))
    drop = plan(asset)
    for p in drop:
        print(("DELETE " if args.apply else "would delete ") + p.relative_to(asset).as_posix())
    if args.apply:
        for p in drop:
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    print(f"{len(drop)} item(s) {'deleted' if args.apply else 'not kept (dry run; --apply deletes)'}")


if __name__ == "__main__":
    main()
