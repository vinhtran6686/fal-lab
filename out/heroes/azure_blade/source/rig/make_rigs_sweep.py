# Writes the three one-piece rigs of the 3-pose horizontal sweep (rebuild: python out/heroes/azure_blade/source/rig/make_rigs_sweep.py).
#   rig_sweep_a.json  pose_skill_sweep_p1_v02.png  A: hips wound back, blade behind the body, pointing left
#   rig_sweep_b.json  pose_skill_sweep_p2_v03.png  B: two thirds of the arc, blade pointing right
#   rig_sweep_c.json  pose_skill_sweep_p3_v01.png  C: the end and the hit, blade foreshortened at the viewer
# One part "whole" (the whole still) on bone body (root > body, both pivoted on the ground point between the feet). No cut-out: the body breathes,
# squashes and leans (root.shx = lean around the feet) as ONE picture. unit = 849 x (pose height / 812): the three poses come out the SAME size as A
# (and the same body size as the other animations, unit 849). Sockets sit on bone body, in source px of the pose's own still, measured in
# source/design/weapon_marks_sweep.json; "pivot" = the torso centre at blade / fist height (docs/pipeline/pose-pair-fx-method.md 10.6).
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
SPEC = {
    "a": dict(still="pose_skill_sweep_p1_v02.png", ground=[541.8, 921], unit=849.0,
              blade_tip=[129, 464], blade_root=[393, 483], pivot=[598, 464]),
    "b": dict(still="pose_skill_sweep_p2_v03.png", ground=[438, 940], unit=890.8,
              blade_tip=[1007, 424], blade_root=[662, 416], pivot=[449.0, 409.4]),
    "c": dict(still="pose_skill_sweep_p3_v01.png", ground=[496.25, 952.5], unit=906.0,
              blade_tip=[502, 537], blade_root=[502, 405], pivot=[501.5, 405]),
}
NOTE = {"a": "A: hips wound back, blade behind the body pointing left", "b": "B: about 2/3 of the arc, blade pointing right",
        "c": "C: the end and the hit, blade foreshortened toward the viewer"}
for key, s in SPEC.items():
    g = s["ground"]
    rig = {"id": "azure_blade", "note": f"Sweep pose {NOTE[key]}: one picture, no cut-out (breath, squash and lean around the feet only).",
           "sources": {"pose": f"../design/{s['still']}"}, "ground": g, "unit": s["unit"],
           "bones": [{"name": "root", "parent": None, "pivot": g}, {"name": "body", "parent": "root", "pivot": g}],
           "sockets": {n: {"bone": "body", "pt": s[n]} for n in ("blade_tip", "blade_root", "pivot")},
           "parts": [{"name": "whole", "source": "pose", "bone": "body", "select": {"rest": True}}]}
    (HERE / f"rig_sweep_{key}.json").write_text(json.dumps(rig, indent=1) + "\n")
    print(key, "ground", g, "unit", s["unit"])
