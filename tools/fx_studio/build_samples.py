"""Samples for Fx Studio's "+ Thêm hiệu ứng → Mẫu": the Python-drawn fx the user approved for holy_commander
(docs/python-fx-recipe.md §9 and out/heroes/holy_commander/brief.md), as transparent light layers that line up with the
hero's exported body frames.

  levelup v01, v03 (chosen for levelup), v05, v06, v07, v08, v09, v10   (v02 and v04 were rejected)
  radiant_slash beam (chosen for the skill)

Every sample has two layers: `back` (drawn behind the body) and `front` (over it), one drawing per body frame of its pose
(holy_commander plays 1 frame per game tick), anchored at the hero's feet. Light is stored as straight alpha = strength
(tools/frame_tuner/export_fx.py), meant to be blended with "screen" (the app's "Cộng sáng").

Usage:
  python tools/fx_studio/build_samples.py render [id ...]   # draw the variants once into tools/fx_studio/samples/ (slow, ~1 min each)
  python tools/fx_studio/build_samples.py [--out DIR]       # copy the cached sheets + samples.json (build_artifact.py calls main_out)

v03 and radiant_slash are taken from the hero's exported fx (fx/levelup, fx/radiant_slash): the very frames the user approved.
The aura variants follow holy_commander's levelup silhouette, so on another character or pose they are a starting point only."""
import argparse, copy, json, math, pathlib, shutil, sys, tempfile
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
HERO = ROOT / "out" / "heroes" / "holy_commander"
CACHE = HERE / "samples"

# id, title, the levelup_variants function (None = the hero's exported fx folder), the pose it was drawn on, note
SAMPLES = [
    ("hc_levelup_v03", "Hào quang xung nhịp (bản chốt levelup)", None, "levelup_side", "levelup",
     "3 đợt hào quang lan ra từ hình người, viền sáng trong thân, chớp ở nắm đấm"),
    ("hc_levelup_v01", "Cột sáng + sóng lan", "V01", "levelup_side", None, "cột viên nang, hào quang, 3 sóng lan dưới chân, dải sáng trên đầu"),
    ("hc_levelup_v05", "Sóng xung kích", "V05", "levelup_side", None, "3 sóng rộng dưới chân, chớp, tia lửa rơi (hợp skill đập đất)"),
    ("hc_levelup_v06", "Hai vòng xoắn sáng", "V06", "levelup_side", None, "hai xoắn hạt sáng quấn thân"),
    ("hc_levelup_v07", "Trụ sáng từ trời", "V07", "levelup_side", None, "trụ rất rộng đổ xuống, bắn tung, hạt nổi lên (hợp buff, triệu hồi)"),
    ("hc_levelup_v08", "Vòng sáng bay lên", "V08", "levelup_side", None, "4 vòng mềm bay từ chân quá đầu (hợp respawn)"),
    ("hc_levelup_v09", "Cột sáng có dải chạy", "V09", "levelup_side", None, "cột có dải sáng chạy lên, sóng đáy rộng"),
    ("hc_levelup_v10", "Tổng hợp", "V10", "levelup_side", None, "gộp mọi lớp: sóng, hào quang, cột, hạt, tia, chớp"),
    ("hc_radiant_slash", "Tia sáng từ mũi kiếm (bản chốt)", None, "skill_radiant_slash_side", "radiant_slash",
     "tia sáng bắn ra từ mũi kiếm khi chém"),
]


def frames_of(folder: pathlib.Path) -> list:
    return [Image.open(p).convert("RGBA") for p in sorted((folder / "frames" / "@2x").glob("*.png"))]


def sheet(frames: list) -> tuple:
    n, (cw, ch) = len(frames), frames[0].size
    cols = min(n, max(1, round(math.sqrt(n * ch / cw))))
    rows = -(-n // cols)
    im = Image.new("RGBA", (cw * cols, ch * rows), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        im.paste(f, ((i % cols) * cw, (i // cols) * ch))
    return im, [cols, rows]


def cache_one(sid: str, fx_dir: pathlib.Path) -> None:
    """fx_dir = an export_fx output folder (back/, front/, fx.json) -> CACHE/<sid>/{back,front}.png + fx.json"""
    fxj = json.loads((fx_dir / "fx.json").read_text(encoding="utf-8"))
    out = CACHE / sid
    out.mkdir(parents=True, exist_ok=True)
    info = {"frames": fxj["frames"], "size_2x": fxj["size_2x"], "pivot_2x": fxj["pivot_2x"], "grid": None}
    for z in ("back", "front"):
        fr = frames_of(fx_dir / z)
        assert len(fr) == fxj["frames"], f"{sid}/{z}: {len(fr)} frames, fx.json says {fxj['frames']}"
        im, info["grid"] = sheet(fr)
        im.save(out / f"{z}.png", optimize=True)
    (out / "fx.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(f"{sid}: {info['frames']} frames, cell {info['size_2x']} @2x, grid {info['grid']}")


def render(ids: list) -> None:
    sys.path.insert(0, str(ROOT / "tools" / "frame_tuner"))
    import os
    os.chdir(ROOT)                       # levelup_variants adds 'scripts' to sys.path relative to the cwd
    import apply_recipe as ar
    import export_fx as ef
    saved = json.loads((ROOT / ar.CFG["asset"] / "export_recipe.json").read_text()).get("states", {})
    lv = next(s for s in ar.CFG["states"] if s["id"] == "levelup")
    for sid, title, fn, pose, exported, note in SAMPLES:
        if ids and sid not in ids:
            continue
        if fn is None:                   # the approved export itself
            cache_one(sid, HERO / "fx" / exported)
            continue
        with tempfile.TemporaryDirectory(prefix="fxs_") as tmp:   # export_fx writes fx/<name>/ and meta.json here, never in the hero folder
            t = pathlib.Path(tmp)
            shutil.copyfile(HERO / "meta.json", t / "meta.json")
            st = copy.deepcopy(lv)
            st["fx"] = {**st["fx"], "fn": fn, "name": sid, "label": f"fx Python {fn.lower()} ({title})"}
            ef.run(st, saved, t)
            cache_one(sid, t / "fx" / sid)


def main_out(out: pathlib.Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for sid, title, fn, pose, exported, note in SAMPLES:
        src = CACHE / sid
        if not (src / "fx.json").exists():
            print(f"{sid}: not rendered yet (python tools/fx_studio/build_samples.py render {sid})")
            continue
        info = json.loads((src / "fx.json").read_text(encoding="utf-8"))
        (w, h), (px, py) = info["size_2x"], info["pivot_2x"]
        parts = []
        for z, zl in (("back", "Z_DECALS"), ("front", "Z_EFFECTS")):
            shutil.copyfile(src / f"{z}.png", out / f"{sid}_{z}.png")
            parts.append({"part": z, "title": "sau thân" if z == "back" else "trước thân", "file": f"samples/{sid}_{z}.png", "z": zl})
        index.append({"id": sid, "title": title, "note": note, "character": "holy_commander", "pose": pose, "frames": info["frames"],
                      "grid": info["grid"], "cell": [w, h], "scale": 0.5, "anchor": [round(px / w, 4), round(py / h, 4)], "hold": 1,
                      "blend": "screen", "parts": parts})
    (out / "samples.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(index)} samples -> {out}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", nargs="?", default="out", choices=["out", "render"])
    p.add_argument("ids", nargs="*")
    p.add_argument("--out", default=str(ROOT / "out" / "fx_studio_artifact" / "samples"))
    a = p.parse_args()
    if a.cmd == "render":
        render(a.ids)
    else:
        main_out(pathlib.Path(a.out))


if __name__ == "__main__":
    main()
