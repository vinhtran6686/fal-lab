"""Build the Fx Studio app (the published Artifact) into one folder.

Usage: python tools/fx_studio/build_artifact.py [--out out/fx_studio_artifact]

Writes <out>/index.html (tools/fx_studio/app.html), bg.png and hero.png (a KR1 map crop and a KR1 hero at the game's
fullhd size), samples/fire_breath.png (the sample sheet) and the character catalog the timeline plays:
chars/<id>/<pose>.png (every frame of a pose side by side, @1x = fullhd), chars/<id>/<pose>@2x.png (the @2x frames in a
grid of cols2x columns, when the character has them) and characters.json:
  [{id, name, pivot: [x, y from the TOP], cell: [w, h], poses: [{id, name, strip, strip2x, cols2x, frames, ticks: [game ticks per frame],
    hit (0-based or null), timing: "game" | "meta", anim (the game's animation name or null)}]}]
Timing comes from the game's animation table when the character is in the game (one atlas frame per tick at 30 fps,
the way the game plays it), else from meta.json fps. Publish index.html with every other file of <out> under its
relative path, capabilities {db: {}, assets: {}, downloads: true}. No server, no paid call."""
import argparse, json, pathlib, re, shutil, sys
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
import fx_studio as fx   # noqa: E402

SAMPLE = ROOT / "out" / "vfx" / "fire_breath_test" / "design" / "sheet_v01.png"
FPS = 30
# meta.json state -> the game's animation suffix (hero_<id>_<suffix>), when the names differ
STATE_ANIM = {"run_side": "running", "idle_side": "idle", "attack_side": "attack", "death_side": "death",
              "respawn_side": "respawn", "levelup_side": "levelup"}
POSE_NAMES = {"idle": "Đứng yên", "running": "Chạy", "attack": "Đánh thường", "death": "Chết", "respawn": "Hồi sinh",
              "levelup": "Lên cấp"}


def game_anims() -> dict:
    p = fx.GAME_DIR / "src" / "kr1" / "data" / "game_animations.lua"
    if not p.exists():
        return {}
    s, out = p.read_text(encoding="utf-8"), {}
    for m in re.finditer(r"^\t(?:a\.)?(\w+) = \{(.*?)\n\t?\}", s, re.M | re.S):
        g = {k: re.search(k + r'\s*=\s*"?(\w+)"?', m.group(2)) for k in ("prefix", "from", "to")}
        if all(g.values()):
            out[m.group(1)] = (g["prefix"].group(1), int(g["from"].group(1)), int(g["to"].group(1)))
    return out


def strip(frames: list, dst: pathlib.Path) -> list:
    ims = [Image.open(f).convert("RGBA") for f in frames]
    w, h = ims[0].size
    sheet = Image.new("RGBA", (w * len(ims), h), (0, 0, 0, 0))
    for i, im in enumerate(ims):
        sheet.paste(im, (i * w, 0))
    dst.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dst, optimize=True)
    return [w, h]


def grid_strip(frames: list, dst: pathlib.Path, max_side: int = 8000) -> int:
    """@2x frames in a grid (rows of `cols`), so no side passes ~8000 px; -> cols."""
    ims = [Image.open(f).convert("RGBA") for f in frames]
    w, h = ims[0].size
    cols = max(1, min(len(ims), max_side // w))
    rows = -(-len(ims) // cols)
    sheet = Image.new("RGBA", (w * cols, h * rows), (0, 0, 0, 0))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    dst.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dst, optimize=True)
    return cols


def catalog(out: pathlib.Path) -> list:
    anims, chars = game_anims(), []
    for meta_p in sorted((ROOT / "out").glob("*/*/meta.json")):
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        cid, poses, cell = meta["id"], [], meta["cell"]
        for state, st in meta.get("states", {}).items():
            if st.get("dir", "").startswith("ui/"):
                continue
            files = sorted((meta_p.parent / st["dir"] / "frames" / "@1x").glob("*.png"))
            if not files:
                continue
            suffix = STATE_ANIM.get(state, re.sub(r"^skill_|_side$", "", state))
            anim = f"hero_{cid}_{suffix}"
            in_game = anim in anims and anims[anim][2] - anims[anim][1] + 1 == len(files)
            ticks = [1] * len(files) if in_game else [max(1, round(FPS / st.get("fps", 15)))] * len(files)
            rel = f"chars/{cid}/{state}.png"
            strip(files, out / rel)
            hit = st.get("hit_frame")
            files2 = sorted((meta_p.parent / st["dir"] / "frames" / "@2x").glob("*.png"))
            extra = {}
            if len(files2) == len(files):   # real @2x frames: the combo bake draws its @2x from these
                rel2 = f"chars/{cid}/{state}@2x.png"
                extra = {"strip2x": rel2, "cols2x": grid_strip(files2, out / rel2)}
            poses.append({**extra, "id": state, "name": POSE_NAMES.get(suffix, suffix.replace("_", " ").capitalize()), "strip": rel,
                          "frames": len(files), "ticks": ticks, "hit": hit - 1 if hit else None,
                          "timing": "game" if in_game else "meta", "anim": anim if in_game else None})
        if poses:
            chars.append({"id": cid, "name": cid.replace("_", " ").title(), "pivot": meta.get("pivot", [0.5, 0.88]),
                          "cell": cell, "poses": poses})
    # Ignus, a KR1 hero, from ref/hero (its frames as the game stores them, held frames listed with alias_of)
    man_p = ROOT / "ref" / "hero" / "manifest.json"
    if man_p.exists():
        man = json.loads(man_p.read_text(encoding="utf-8"))
        names = list(man["frames"])
        files = [ROOT / "ref" / "hero" / "frames" / f"{n}.png" for n in names]
        if all(f.exists() for f in files):
            rel = "chars/ignus/attack.png"
            cell = strip(files, out / rel)
            anim = "hero_ignus_attack"
            chars.append({"id": "ignus", "name": "Ignus (KR1)", "pivot": [0.5, 0.9], "cell": cell,
                          "poses": [{"id": "attack", "name": "Đánh thường", "strip": rel, "frames": len(files),
                                     "ticks": [1] * len(files), "hit": None, "timing": "game",
                                     "anim": anim if anim in anims else None}]})
    return chars


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default=str(ROOT / "out" / "fx_studio_artifact"))
    a = p.parse_args()
    out = pathlib.Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    (out / "samples").mkdir(parents=True)
    shutil.copyfile(HERE / "app.html", out / "index.html")
    fx.backdrop((960, 540)).convert("RGB").save(out / "bg.png", optimize=True)
    hero = fx.hero_for_scale()
    if hero:
        hero.save(out / "hero.png")
    if SAMPLE.exists():
        shutil.copyfile(SAMPLE, out / "samples" / "fire_breath.png")
    import build_samples   # the sample effects behind "+ Thêm hiệu ứng → Mẫu" (samples/<id>.png + samples.json)
    build_samples.main_out(out / "samples")
    chars = catalog(out)
    (out / "characters.json").write_text(json.dumps(chars, ensure_ascii=False, indent=1), encoding="utf-8")
    for c in chars:
        print(f"{c['id']}: " + ", ".join(f"{p['id']} {p['frames']}f {sum(p['ticks'])}t {p['timing']}" for p in c["poses"]))
    files = sorted(f.relative_to(out).as_posix() for f in out.rglob("*") if f.is_file())
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"{out}: {len(files)} files, {size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
