"""Compose azure_blade `skill_sweep_side` (3-pose sweep, S4b): body (Puppet Kit) + the lib-fx `melee/slash/sweep` streak.

Run (after the two rebuild commands below), from the repo root:
    python out/heroes/azure_blade/source/vfx/sweep/build_sweep.py

Sources (all numbers come from S4, lib-fx/_plans/slash-round-02/S4-sweep-body-timing.md "Kết quả"):
  body  : python scripts/puppet.py render out/heroes/azure_blade out/heroes/azure_blade/source/rig/anims/sweep.json --sheet skill_sweep_puppet_side
  streak: python lib-fx/build.py melee/slash/sweep --pal frost --fps 15 --split --s 0.707 --swing "tip_a=110.1,185.0;root_a=148.6,187.6;pivot=178.0,185.0;tip_b=251.5,174.8;root_b=205.7,173.7;pivot_b=177.5,172.8;tip_c=177.3,196.9;root_c=177.5,181.1;pivot_c=177.4,181.1" --out out/heroes/azure_blade/frames/fx/sweep
Layering per body frame k (1..21), n = k - FX_OFFSET: transparent cell; if 1 <= n <= streak frames: back/ at `origin`
(read from fx/sweep/meta.json), then the body, then front/ at the same place. The streak's hit frame (3) lands on body frame 8.
"""
import json, pathlib, shutil
from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).resolve().parent
ASSET = HERE.parents[2]
SHEET = "skill_sweep_side"
BODY_DIR = ASSET / "frames" / "skill_sweep_puppet_side" / "frames" / "@2x"
FX_DIR = ASSET / "frames" / "fx" / "sweep"
ANIM = json.loads((ASSET / "source" / "rig" / "anims" / "sweep.json").read_text())
FXM = json.loads((FX_DIR / "meta.json").read_text())
W2, H2 = 352, 280
FX_OFFSET = ANIM["hit_frame"] - FXM["hit_frame"]        # 8 - 3 = 5: streak frame n sits on body frame n + 5
ORIGIN = tuple(FXM["origin"])
NFX = FXM["frames"]
BODY = sorted(BODY_DIR.glob("*.png"))
BACK = sorted((FX_DIR / "back" / "@2x").glob("*.png"))
FRONT = sorted((FX_DIR / "front" / "@2x").glob("*.png"))
assert len(BODY) == 21 and len(BACK) == len(FRONT) == NFX

frames = []
for k, bp in enumerate(BODY, 1):
    n = k - FX_OFFSET
    cell = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    if 1 <= n <= NFX:
        cell.alpha_composite(Image.open(BACK[n - 1]).convert("RGBA"), ORIGIN)
    cell.alpha_composite(Image.open(bp).convert("RGBA"))
    if 1 <= n <= NFX:
        cell.alpha_composite(Image.open(FRONT[n - 1]).convert("RGBA"), ORIGIN)
    frames.append(cell)

out = ASSET / "frames" / SHEET
if out.exists():
    shutil.rmtree(out)
for sub in ("@2x", "@1x"):
    (out / "frames" / sub).mkdir(parents=True, exist_ok=True)
for k, im in enumerate(frames, 1):
    im.save(out / "frames" / "@2x" / f"hero_azure_blade_{SHEET}_{k:02d}.png")
    im.resize((W2 // 2, H2 // 2), Image.LANCZOS).save(out / "frames" / "@1x" / f"hero_azure_blade_{SHEET}_{k:02d}.png")


def gif(cells, path, fps, scale, bg=(40, 44, 54, 255)):
    fr = []
    for c in cells:
        base = Image.alpha_composite(Image.new("RGBA", c.size, bg), c)
        base = base.resize((round(c.width * scale), round(c.height * scale)), Image.LANCZOS if scale < 1 else Image.NEAREST)
        fr.append(base.convert("P", palette=Image.ADAPTIVE))
    fr[0].save(path, save_all=True, append_images=fr[1:], duration=round(1000 / fps), loop=0)


fps = ANIM["fps"]
gif(frames, out / "preview_2x.gif", fps, 1.0)
gif([c.resize((W2 // 2, H2 // 2), Image.LANCZOS) for c in frames], out / "preview_game_1x_x3.gif", fps, 3)
CR = (20, 60, 300, 270)
cols = 10; cw, ch = (CR[2] - CR[0]) // 2, (CR[3] - CR[1]) // 2
sheet = Image.new("RGB", (cw * cols, ch * ((len(frames) + cols - 1) // cols)), (40, 44, 54))
for k, c in enumerate(frames):
    t = Image.alpha_composite(Image.new("RGBA", c.size, (40, 44, 54, 255)), c).crop(CR).resize((cw, ch), Image.LANCZOS)
    ImageDraw.Draw(t).text((2, 2), str(k + 1), fill=(255, 255, 0))
    sheet.paste(t.convert("RGB"), ((k % cols) * cw, (k // cols) * ch))
sheet.save(out / "contact.png")
json.dump({
    "fps": fps, "frames": len(frames), "hit_frame": ANIM["hit_frame"], "fx_offset": FX_OFFSET, "fx_origin_2x": list(ORIGIN),
    "rebuild": {
        "body": "python scripts/puppet.py render out/heroes/azure_blade out/heroes/azure_blade/source/rig/anims/sweep.json --sheet skill_sweep_puppet_side",
        "fx": FXM.get("rebuild", "").replace("--swing ", "--swing \"", 1).replace(" --out", "\" --out", 1),
        "compose": "python out/heroes/azure_blade/source/vfx/sweep/build_sweep.py",
    },
}, open(out / "export_meta.json", "w"), indent=1, ensure_ascii=False)
print("frames", len(frames), "streak on body frames", FX_OFFSET + 1, "-", FX_OFFSET + NFX, "->", out)
