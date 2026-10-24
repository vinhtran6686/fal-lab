"""One-off (2026-10-24): move every character folder under out/ to the two-group layout and drop what was not approved.

  out/<class>/<id>/
    brief.md  history.md  meta.json
    source/   design/  video/  fx/  vfx/        group 1: the approved originals (stills, clips, Python fx code, fal-image vfx)
    frames/   <sheet>/  icon/  fx/<name>/  skills/<pose>/  export_*.json  README.md     group 2: cut from group 1
    .work/    tools only, not in git (left as is)

Usage: python scripts/restructure_out.py            # dry run: prints every delete / move / path rewrite
       python scripts/restructure_out.py --delete   # phase 1: delete what is not kept (rejected takes, drafts, two characters)
       python scripts/restructure_out.py --move     # phase 2: move into source/ and frames/, rewrite paths in text files
The keep lists below were read from each brief's Asset manifest (✅ and ⏳ rows) and meta.json states (user decision
2026-10-24: drop rejected and draft data; keep ⏳ items as pending; delete thunder_sage and goblin_miner)."""
import argparse, json, pathlib, re, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
CATS = {"move", "attack", "death", "idle", "level", "skill", "spawn", "hurt", "react", "other", "projectile"}

KEEP = {
    "heroes/holy_commander": {
        "design": ["master_v07", "icon_v01", "pose_skill_holy_banner_v01", "pose_skill_radiant_slash_v01", "pose_skill_charge_v01",
                   "pose_respawn_v02", "pose_levelup_v02"],
        "fx_code": ["levelup_variants.py", "radiant_slash_beam.py"],       # holy_banner_ripple.py: the model take was chosen
        "fx_frames": ["levelup", "radiant_slash"],
        "vfx": ["holy_banner", "radiant_slash"],                           # out/vfx/<name>: approved fal-image vfx of this hero
        "extra_video": [],
    },
    "heroes/diablo": {
        "design": ["master_v04", "icon_v01", "pose_respawn_v01", "pose_skill_horn_charge_v01", "pose_skill_ember_armor_v01",
                   "pose_skill_flame_slam_start_v01", "pose_skill_flame_slam_v04", "pose_skill_horn_charge_windup_v01",
                   "pose_skill_horn_charge_load_v01", "pose_skill_horn_charge_lunge_v01", "pose_skill_fire_breath_crouch_v01",
                   "pose_skill_fire_breath_v02", "concept_ref"],
        "fx_code": ["fire_breath.py", "levelup_glow.py"],
        "fx_frames": ["fire_breath_v04", "levelup_v01"],
        "vfx": [],
        "extra_video": ["skill_ember_armor_side_t01"],                     # ⏳ clip, not cut yet
    },
}
DROP_ASSETS = ["heroes/thunder_sage", "enemies/goblin_miner"]
DROP_IN_ASSET = ["experiments", "review"]
SAMPLE_SRC, SAMPLE_DST = OUT / "vfx" / "fire_breath_test" / "design" / "sheet_v01.png", ROOT / "tools" / "fx_studio" / "samples" / "fire_breath.png"


def kept_video(a: pathlib.Path, keep: dict) -> set:
    meta = json.loads((a / "meta.json").read_text(encoding="utf-8"))
    stems = {pathlib.Path(s["source"]).stem for s in meta["states"].values() if str(s.get("source", "")).startswith("raw/")}
    return stems | set(keep["extra_video"])


def plan_delete() -> list:
    out = [OUT / d for d in DROP_ASSETS if (OUT / d).exists()]
    for rel, keep in KEEP.items():
        a = OUT / rel
        out += [a / d for d in DROP_IN_ASSET if (a / d).exists()]
        vs = kept_video(a, keep)
        out += [p for p in (a / "raw").iterdir() if p.name.split(".")[0] not in vs]
        des = set(keep["design"])
        for p in (a / "design").iterdir():
            if p.is_dir():   # prompts/<still>_pNN.txt: kept when its still is kept
                out += [q for q in p.iterdir() if re.sub(r"_p\d+$", "", q.stem) not in {re.sub(r"_v\d+$", "", d) for d in des}]
            elif p.stem not in des:
                out.append(p)
        for p in (a / "fx").iterdir():
            if p.name not in keep["fx_code"] and p.name not in keep["fx_frames"]:
                out.append(p)
    vfx_keep = {v for k in KEEP.values() for v in k["vfx"]}
    out += [p for p in (OUT / "vfx").iterdir() if p.name not in vfx_keep and p.name != ".gitkeep"]
    return out


def plan_move() -> list:
    """(src, dst) pairs, inside each kept character (+ its out/vfx stills)."""
    mv = []
    for rel, keep in KEEP.items():
        a = OUT / rel
        mv += [(p, a / "source" / "video" / p.name) for p in sorted((a / "raw").iterdir())]
        mv += [(p, a / "source" / "design" / p.name) for p in sorted((a / "design").iterdir())]
        mv += [(a / "fx" / f, a / "source" / "fx" / f) for f in keep["fx_code"]]
        mv += [(a / "fx" / f, a / "frames" / "fx" / f) for f in keep["fx_frames"]]
        mv += [(OUT / "vfx" / v, a / "source" / "vfx" / v) for v in keep["vfx"]]
        for c in sorted(CATS):
            if (a / c).is_dir():
                mv += [(s, a / "frames" / s.name) for s in sorted((a / c).iterdir())]
        if (a / "ui" / "icon").exists():
            mv.append((a / "ui" / "icon", a / "frames" / "icon"))
        if (a / "skills").exists():
            mv.append((a / "skills", a / "frames" / "skills"))
        for f, to in (("EXPORT_README.md", "README.md"), ("export_manifest.json", "export_manifest.json"), ("export_recipe.json", "export_recipe.json")):
            if (a / f).exists():
                mv.append((a / f, a / "frames" / to))
    return mv


PATH_RE = re.compile(r"(?<![\w./@-])((?:raw|design|fx|ui|skills|" + "|".join(sorted(CATS)) + r")/[\w./@*{}-]*)")


def new_path(p: str, keep: dict) -> str | None:
    head, _, rest = p.partition("/")
    first = rest.split("/")[0]
    if head == "raw":
        return "source/video/" + rest
    if head == "design":
        return "source/design/" + rest
    if head == "fx":
        if first in keep["fx_code"]:
            return "source/fx/" + rest
        if first in keep["fx_frames"]:
            return "frames/fx/" + rest
        return None
    if head == "ui" and first == "icon":
        return "frames/icon" + rest[len("icon"):]
    if head == "skills":
        return "frames/skills/" + rest
    if head in CATS and first:
        return "frames/" + rest
    return None


def exists_like(a: pathlib.Path, p: str) -> bool:
    """the path exists in the new layout; for a pattern (…_NN.png, *.mp4, 01..08) its folder does"""
    segs = []
    for seg in p.rstrip("/.").split("/"):
        if re.search(r"[*{]|_NN|\d+\.\.\d+", seg):
            break
        segs.append(seg)
    return len(segs) >= 2 and (a / "/".join(segs)).exists()


def rewrite_text(a: pathlib.Path, keep: dict, text: str) -> tuple:
    n = 0
    def sub(m):
        nonlocal n
        p = m.group(1); np = new_path(p, keep)
        if np and exists_like(a, np):
            n += 1; return np
        return p
    return PATH_RE.sub(sub, text), n


TEXT_FILES = ["meta.json", "brief.md", "history.md", "frames/export_manifest.json", "frames/export_recipe.json", "frames/README.md"]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(); g.add_argument("--delete", action="store_true"); g.add_argument("--move", action="store_true")
    a = p.parse_args()
    if not a.move:
        dels = plan_delete()
        size = lambda q: sum(f.stat().st_size for f in q.rglob("*") if f.is_file()) if q.is_dir() else q.stat().st_size
        tot = 0
        for q in dels:
            s = size(q); tot += s
            print(f"DELETE {q.relative_to(ROOT)}  ({s / 1e6:.1f} MB)")
        print(f"= {len(dels)} items, {tot / 1e6:.1f} MB")
        print(f"COPY   {SAMPLE_SRC.relative_to(ROOT)} -> {SAMPLE_DST.relative_to(ROOT)}  (the 'Lửa mẫu' sample)")
        if a.delete:
            SAMPLE_DST.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(SAMPLE_SRC, SAMPLE_DST)
            for q in dels:
                shutil.rmtree(q) if q.is_dir() else q.unlink()
            print("deleted")
        if a.delete or not a.move:
            if a.delete:
                return
    mv = plan_move()
    for s, d in mv:
        print(f"MOVE   {s.relative_to(OUT)} -> {d.relative_to(OUT)}")
    if not a.move:
        return
    for s, d in mv:
        d.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(s), str(d))
    for rel, keep in KEEP.items():
        asset = OUT / rel
        for d in ["raw", "design", "fx", "ui", *CATS]:   # emptied folders (a leftover __pycache__ included)
            q = asset / d
            if q.exists() and all(f.name == "__pycache__" or f.is_dir() and not any(f.iterdir()) for f in q.iterdir()):
                shutil.rmtree(q)
        for f in TEXT_FILES:
            q = asset / f
            if q.exists():
                t, n = rewrite_text(asset, keep, q.read_text(encoding="utf-8"))
                q.write_text(t, encoding="utf-8"); print(f"paths  {q.relative_to(OUT)}: {n} rewritten")
        meta_p = asset / "meta.json"; meta = json.loads(meta_p.read_text(encoding="utf-8"))
        meta["sources"] = {k: sorted(x.name for x in (asset / "source" / k).iterdir()) for k in ("design", "video", "fx", "vfx") if (asset / "source" / k).exists()}
        meta_p.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("moved")


if __name__ == "__main__":
    main()
