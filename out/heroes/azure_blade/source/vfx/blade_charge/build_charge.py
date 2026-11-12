# azure_blade "tu luc": blue energy that rises along the blade (hilt -> tip) before the skill and stays lit after it.
# Writes the effect as its own layer (one RGBA cell per body frame, same canvas as the body) into frames/fx/blade_charge/.
# Run (after `puppet.py render ... --sheet skill_crescent_puppet_side`; the rig sockets blade_root/blade_tip ride the blade, see make_rigs.py):
#   python out/heroes/azure_blade/source/vfx/blade_charge/build_charge.py
# The light is drawn on the blade's OWN pixels (the blade part rendered alone, minus the arms part in front of it), so it follows the lift and
# the cut to pose B and never covers the hands. Timeline constants live in aura_params.json, the drawing in lib-fx/melee/blade_aura/blade_aura.py.
import sys, json, pathlib, importlib.util
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "lib-fx" / "_core" / "formulas" / "draw"))
spec = importlib.util.spec_from_file_location("puppet_cli", ROOT / "scripts" / "puppet.py"); pp = importlib.util.module_from_spec(spec); spec.loader.exec_module(pp)
spec = importlib.util.spec_from_file_location("blade_aura", ROOT / "lib-fx" / "melee" / "blade_aura" / "blade_aura.py"); BA = importlib.util.module_from_spec(spec); spec.loader.exec_module(BA)
from puppet_kit.core import Animation, S  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
ASSET = HERE.parents[2]
P = json.loads((HERE / "aura_params.json").read_text())
SS = 4
FPS = P["fps"]
sec = lambda k: (k - 1) / FPS                                   # frame number (1-based) -> seconds

meta = json.loads((ASSET / "meta.json").read_text())
anim = Animation(ASSET / "source" / "rig" / "anims" / "crescent.json", ASSET)
c2 = (meta["cell"][0] * meta["scale_2x"], meta["cell"][1] * meta["scale_2x"])
body2x = meta["body_height_2x"]

tl = dict(start=sec(P["ignite_frame"]), rise=(P["front_full_frame"] - P["ignite_frame"]) / FPS,
          pulses=[(sec(f), d / FPS, s) for f, d, s in P["pulses"]],
          energy=[(sec(f), e) for f, e in P["energy"]],
          flares=[(sec(f), s, d / FPS) for f, s, d in P["flares"]],
          shimmer=dict(frm=sec(P["shimmer"]["from"]), amp=P["shimmer"]["amp"], period=P["shimmer"]["period"] / FPS),
          spark_every=P["spark_every"], fps=FPS, full_at=sec(P["hit_frame"]), cut=sec(P["hit_frame"]))

n = anim.total
masks, socks = [], []
for g in range(n):
    shot, f = anim.locate(g)
    rig = shot["rig"]
    view = S(SS, SS) @ anim.view(rig, c2, meta["pivot"], body2x)
    size = (c2[1] * SS, c2[0] * SS)
    solo = lambda keep: {**shot["tracks"], **{f"{p['name']}.alpha": {"base": 0.0} for p in rig.parts if p["name"] != keep}}
    img_b, world = rig.render(solo("blade"), f, view, size)
    img_a, _ = rig.render(solo("arms"), f, view, size)
    sk = rig.sockets(world)
    v2 = anim.view(rig, c2, meta["pivot"], body2x)
    from puppet_kit.core import apply
    socks.append((apply(v2, sk["blade_root"]), apply(v2, sk["blade_tip"])))
    masks.append((img_b[..., 3] / 255.0, img_a[..., 3] / 255.0))

hw = P["blade_half_width"]
pose_at = lambda t0: (*socks[min(n - 1, max(0, round(t0 * FPS)))], hw)
sparks = BA.make_sparks(tl, P["seed"], n / FPS)
cells = []
for g in range(n):
    t = g / FPS
    st = BA.params_at(t, tl)
    sp = BA.sparks_at(sparks, t, tl, pose_at)
    rgba = BA.render(masks[g][0], masks[g][1], socks[g][0], socks[g][1], st, SS, sp, grow=True, strength=P["strength"])
    cells.append(Image.fromarray(BA.to_cell(rgba, SS), "RGBA"))

out = ASSET / "frames" / "fx" / "blade_charge"
import shutil
if out.exists():
    shutil.rmtree(out)
for sub in ("@2x", "@1x"):
    (out / "frames" / sub).mkdir(parents=True)
for k, im in enumerate(cells, 1):
    im.save(out / "frames" / "@2x" / f"hero_azure_blade_fx_blade_charge_{k:02d}.png")
    im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(out / "frames" / "@1x" / f"hero_azure_blade_fx_blade_charge_{k:02d}.png")
json.dump({"id": "melee/blade_aura/charge_blue", "frames": n, "fps": FPS, "cell_2x": list(c2), "note": "full-cell RGBA layer per body frame of skill_crescent; compose under the slash",
           "timeline": P}, open(out / "fx.json", "w"), indent=1)
bg = (40, 44, 54, 255)
body_dir = ASSET / "frames" / "skill_crescent_puppet_side" / "frames" / "@2x"
body = [Image.open(p).convert("RGBA") for p in sorted(body_dir.glob("*.png"))]
prev = []
for b, c in zip(body, cells):
    im = Image.alpha_composite(Image.new("RGBA", b.size, bg), b); im.alpha_composite(c); prev.append(im.convert("P", palette=Image.ADAPTIVE))
prev[0].save(out / "preview_with_body.gif", save_all=True, append_images=prev[1:], duration=round(1000 / FPS), loop=0)
print("frames", n, "->", out)
