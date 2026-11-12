# Writes anims/idle.json: 24-frame breathing loop. Every channel is an osc of period 24 (a loop), phases offset so nothing moves in lockstep.
# tx/ty are source px of the 1024 still (1 px @2x of the cell = 7.1 source px), rot in degrees, sx/sy scales, torso.sway multiplies the hair and hem band.
import json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
P = 24
osc = lambda amp, phase=0.0, base=0.0: {"base": base, "osc": {"amp": amp, "period": P, "phase": phase}}
tracks = {"_sway_period": P,
          "body.sy": osc(-0.014, 0.0, 1.0), "body.sx": osc(0.007, 0.0, 1.0),
          "head.ty": osc(5, -0.08), "head.rot": osc(1.0, -0.12),
          "arm_up.rot": osc(2.2, -0.10), "arm_up.ty": osc(6, -0.20),
          "arm_down.rot": osc(-1.5, -0.10),
          "torso.sway": {"base": 1.0, "osc": {"amp": 0.25, "period": P, "phase": -0.3}}}
anim = {"note": "pyre_witch idle: breath, head, floating raised palm, hanging arm, hair and hem sway", "version": "p01", "fps": 15, "loop": True,
        "shots": [{"name": "idle", "rig": "source/rig/rig.json", "frames": P, "tracks": tracks}]}
(HERE / "anims").mkdir(exist_ok=True)
(HERE / "anims" / "idle.json").write_text(json.dumps(anim, indent=1) + "\n")
print("frames", P)
