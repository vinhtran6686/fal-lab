# Writes the six one-piece rigs of the spin attack (rebuild: python out/heroes/moon_crane/source/rig/make_rigs_spin.py).
#   k0 ready (spear upright) | k1 coil (spear behind the head) | k2 loaded (crouched, spear low on the left) | k3 release (the spear sweeps
#   across the front) | k4 hit (spear out on the right, toward the target) | k5 follow-through (back to the viewer, spear out on the left)
# Stills: cut from the approved clip source/video/skill_spin_back_v5_t01.mp4 (frames 0, 24, 50, 70, 80, 90), keyed on exact magenta.
# One part "whole" on bone body (root > body, pivoted on the ground point between the boots): no cut-out; the body squashes, stretches and leans
# as ONE picture. unit = source px of the body height (head top to boots), the same for all six (they come from one clip at one scale).
# Sockets (source px of the still): blade_tip = the spearhead tip, blade_root = the blade end nearest the haft, pivot = the torso centre at spear height.
import json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
UNIT = 495.0
SPEC = {
    "k0": dict(ground=[390.5, 633], tip=[147, 82], root=[207, 251], pivot=[385, 420], note="ready, spear upright"),
    "k1": dict(ground=[386.5, 635], tip=[621, 126], root=[522, 200], pivot=[385, 330], note="coil, spear behind the head"),
    "k2": dict(ground=[388, 635], tip=[112, 618], root=[290, 534], pivot=[385, 560], note="loaded, crouched, spear low on the left"),
    "k3": dict(ground=[390, 635], tip=[364, 676], root=[405, 560], pivot=[385, 560], note="release, the spear across the front"),
    "k4": dict(ground=[396, 645], tip=[787, 418], root=[674, 435], pivot=[385, 430], note="hit, spear out on the right; the spearhead was cut by the clip frame and smeared, so it is the spearhead of k5 mirrored (the still is padded to 1010 px wide)"),
    "k5": dict(ground=[412.5, 637], tip=[84, 425], root=[197, 438], pivot=[400, 430], note="follow-through, back to the viewer, spear out on the left"),
}
for k, s in SPEC.items():
    g = s["ground"]
    rig = {"id": "moon_crane", "note": f"Spin attack {k}: {s['note']}; one picture, no cut-out.",
           "sources": {"pose": f"../design/pose_spin_{k}_v01.png"}, "ground": g, "unit": UNIT,
           "bones": [{"name": "root", "parent": None, "pivot": g}, {"name": "body", "parent": "root", "pivot": g}],
           "sockets": {"weapon_tip": {"bone": "body", "pt": s["tip"]}, "weapon_root": {"bone": "body", "pt": s["root"]}, "pivot": {"bone": "body", "pt": s["pivot"]}},
           "parts": [{"name": "whole", "source": "pose", "bone": "body", "select": {"rest": True}}]}
    (HERE / f"rig_spin_{k}.json").write_text(json.dumps(rig, indent=1) + "\n")
    print(k, g)
