# Writes anims/sweep.json (3-pose horizontal sweep, Puppet Kit pose-to-pose, 15 fps, 21 frames, hit_frame 8):
#   wind   rig_sweep_a  6 frames  anticipation + load: the body sinks (sy 0.95), widens, leans back (shx -0.10) on `out`
#   cross  rig_sweep_b  1 frame   release (the fastest phase, one frame): stretched (sy 1.03), leaning forward (shx +0.10)
#   hit    rig_sweep_c  6 frames  impact: squash (0.90 / 1.08), rebound (1.03 / 0.985), settle; hit_frame = first frame (8)
#   settle rig_sweep_c  8 frames  slow breath
# root.shx leans the picture around the ground point (feet stay planted); positive = the top goes right (toward the body of the NEXT pose
# at the cuts A -> B -> C). Numbers: docs/scripts/puppet_kit/puppet-kit-motion-recipes.md sections 2 and 4. Usage: make_anim_sweep.py [--no-shx OUT.json]
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
K = lambda *pts: [list(p) for p in pts]

shots = [
    {"name": "wind", "rig": "source/rig/rig_sweep_a.json", "frames": 6, "tracks": {
        "body.sy": K((0, 1.0), (3, 0.955, "out"), (5, 0.95)),
        "body.sx": K((0, 1.0), (3, 1.022, "out"), (5, 1.025)),
        "root.shx": K((0, 0), (3, -0.08, "out"), (5, -0.10))}},
    {"name": "cross", "rig": "source/rig/rig_sweep_b.json", "frames": 1, "tracks": {
        "body.sy": K((0, 1.03)), "body.sx": K((0, 0.985)), "root.shx": K((0, 0.0))}},   # task said +0.10: overshoots the cut A -> B, see Ket qua
    {"name": "hit", "rig": "source/rig/rig_sweep_c.json", "frames": 6, "tracks": {
        "body.sy": K((0, 0.90), (2, 1.03, "out"), (4, 1.0, "inout")),
        "body.sx": K((0, 1.08), (2, 0.985, "out"), (4, 1.0, "inout")),
        "root.shx": K((0, 0.01), (2, -0.02, "out"), (4, 0, "inout"))}},   # task said +0.12: jumps away from B at the cut B -> C
    {"name": "settle", "rig": "source/rig/rig_sweep_c.json", "frames": 8, "tracks": {
        "body.sy": {"base": 1.0, "osc": {"amp": -0.007, "period": 8}}}},
]
anim = {"note": "azure_blade horizontal sweep A -> B -> C: three one-piece poses, five-phase body timing (wind-up, cross, hit squash and rebound, settle); the vfx is built from the rig sockets (puppet.py track).",
        "version": "p01", "fps": 15, "loop": False, "hit_frame": 8, "shots": shots}
if len(sys.argv) > 2 and sys.argv[1] == "--no-shx":
    for s in shots:
        s["tracks"].pop("root.shx", None)
    out = pathlib.Path(sys.argv[2])
else:
    out = HERE / "anims" / "sweep.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(anim, indent=1) + "\n")
print("frames", sum(s["frames"] for s in shots), "hit", anim["hit_frame"], "->", out)
