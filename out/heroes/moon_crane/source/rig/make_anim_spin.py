# Writes anims/spin.json: the spin attack as six one-piece poses with the five-phase timing of docs/scripts/puppet_kit/puppet-kit-motion-recipes.md
# (anticipation 'out', load, release 1 frame 'in3', hit squash + rebound, settle), 15 fps. hit_frame = the first frame of the hit pose.
# Rebuild: python out/heroes/moon_crane/source/rig/make_anim_spin.py
import json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
def shot(name, k, frames, tr): return {"name": name, "rig": f"source/rig/rig_spin_{k}.json", "frames": frames, "tracks": tr}
shots = [
    shot("ready", "k0", 3, {"body.sy": [[0, 1.0], [2, 0.955, "out"]], "body.sx": [[0, 1.0], [2, 1.022, "out"]], "root.shx": [[0, 0.0], [2, -0.05, "out"]]}),
    shot("coil", "k1", 4, {"body.sy": [[0, 1.05], [1, 1.0, "out"], [3, 0.97]], "body.sx": [[0, 0.97], [1, 1.0, "out"], [3, 1.02]], "root.shx": [[0, -0.09], [1, -0.04, "out"], [3, -0.06]]}),
    shot("load", "k2", 3, {"body.sy": [[0, 0.92], [1, 1.0, "out"], [2, 0.985]], "body.sx": [[0, 1.06], [1, 1.0, "out"], [2, 1.01]], "root.shx": [[0, -0.05], [2, -0.07]]}),
    shot("release", "k3", 1, {"body.sy": [[0, 1.03]], "body.sx": [[0, 0.985]], "root.shx": [[0, 0.11]]}),
    shot("hit", "k4", 5, {"body.sy": [[0, 0.90], [2, 1.03, "out"], [4, 1.0, "inout"]], "body.sx": [[0, 1.08], [2, 0.985, "out"], [4, 1.0, "inout"]],
                          "root.shx": [[0, 0.04], [2, -0.02, "out"], [4, 0.0, "inout"]], "root.tx": [[0, 10.0], [1, -7.0], [2, 4.0], [3, -2.0], [4, 0.0]]}),
    shot("follow", "k5", 7, {"body.sy": [[0, 0.94], [2, 1.02, "out"], [5, 1.0, "inout"], [6, 0.995]], "body.sx": [[0, 1.05], [2, 0.99, "out"], [5, 1.0, "inout"]],
                              "root.shx": [[0, 0.03], [3, -0.01, "out"], [6, 0.0]]}),
]
anim = {"note": "moon_crane spin attack: six one-piece poses cut from the approved clip, five-phase body timing; the vfx is built from the rig sockets.",
        "version": "p01", "fps": 15, "loop": False, "hit_frame": 12, "shots": shots}
(HERE / "anims" / "spin.json").write_text(json.dumps(anim, indent=1) + "\n")
print(sum(s["frames"] for s in shots), "frames")
