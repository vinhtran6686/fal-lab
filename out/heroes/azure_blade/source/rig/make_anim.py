# Writes anims/crescent.json (pose-to-pose, Puppet Kit tier 2), only pose A and pose B, no idle:
#   P1  pose A edited: the arms lift the blade a little higher, a breath in; shoulder plate and chest rise with the arms (muscle link)
#   P2  back to pose A (the blade lowers), a breath out, hold
#   cut the slash fx covers it
#   P3  pose B (the chop lands): the body sinks, the arms bounce and the chest follows them
#   P4  inertia: a small dip and the return to pose B, settling, then a slow breath
# Units: tx/ty in source px of the 1024 stills (1 px @2x of the cell = 7.1 source px), rot in degrees, sx/sy scales, <part>.sway a multiplier.
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
K = lambda *pts: [list(p) for p in pts]

up_n, imp_n, hold_n = 22, 12, 10
shots = [
    {"name": "lift_and_return", "rig": "source/rig/rig_a.json", "frames": up_n, "tracks": {
        "_sway_period": 14,
        "arms.ty": K((0, 0), (6, -28, "inout"), (9, -28), (16, 0, "inout")),
        "arms.rot": K((0, 0), (6, -2.5, "inout"), (9, -2.5), (16, 0, "inout")),
        "body.sy": K((0, 1.0), (6, 1.022, "inout"), (9, 1.022), (16, 0.992, "inout"), (21, 1.0, "inout")),
        "body.sx": K((0, 1.0), (6, 0.992, "inout"), (9, 0.992), (16, 1.004, "inout"), (21, 1.0, "inout")),
        "torso.sway": K((0, 1.0), (21, 1.4, "in"))}},
    {"name": "impact", "rig": "source/rig/rig_b.json", "frames": imp_n, "tracks": {
        "_sway_period": 14,
        "body.sy": K((0, 0.93), (2, 1.015, "out"), (4, 0.985, "inout"), (6, 1.004, "inout"), (imp_n - 1, 1.0, "inout")),
        "body.sx": K((0, 1.04), (2, 0.992, "out"), (4, 1.006, "inout"), (imp_n - 1, 1.0, "inout")),
        "arms.ty": K((0, 20), (1, -9, "out"), (3, 6, "inout"), (5, -2, "inout"), (7, 0, "inout")),
        "arms.rot": K((0, -2.0), (2, 1.6, "out"), (4, -0.9, "inout"), (6, 0.3, "inout"), (8, 0, "inout")),
        "torso.sway": K((0, 2.4), (imp_n - 1, 1.0, "out"))}},
    {"name": "settle", "rig": "source/rig/rig_b.json", "frames": hold_n, "tracks": {
        "_sway_period": hold_n,
        "body.sy": {"base": 1.0, "osc": {"amp": -0.007, "period": hold_n}},
        "arms.ty": {"base": 0, "osc": {"amp": 1.5, "period": hold_n, "phase": -0.1}},
        "torso.sway": {"base": 1.0, "osc": {"amp": 0.15, "period": hold_n}}}},
]
anim = {"note": "azure_blade Trảm Trăng Khuyết: pose A lift/return -> cut (slash) -> pose B impact + settle. Only the two approved poses, split into torso/arms/blade with a shoulder-chest muscle link.",
        "version": "p02", "fps": 15, "loop": False, "hit_frame": up_n + 1, "shots": shots}
(HERE / "anims").mkdir(exist_ok=True)
(HERE / "anims" / "crescent.json").write_text(json.dumps(anim, indent=1) + "\n")
print("frames", sum(s["frames"] for s in shots), "hit", anim["hit_frame"])
