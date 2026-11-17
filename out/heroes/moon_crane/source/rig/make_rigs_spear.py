# Writes the three cut-out rigs of the spear sweep (rebuild: python out/heroes/moon_crane/source/rig/make_rigs_spear.py).
#   rig_spear_a.json  pose_sweep_guard_v02.png   A: guard, spear upright beside the face
#   rig_spear_b.json  pose_sweep_windup_v01.png  B: wind-up, spear drawn back to the left at shoulder height
#   rig_spear_c.json  pose_sweep_hit_v01.png     C: hit, spear level to the right
# Split (docs/pipeline/pose-pair-fx-method.md step 4): torso (rest: head, chest, crane wing, both shoulder plates, legs, skirt),
# spear (haft, spearhead, crescent guard, tassel) and two arm layers (each forearm with its bracer and fist), all three on bone
# "arms" (pivot at the chest centre). Muscle link "shoulder_chest" (mode stretch): when the arms slide (tx/ty) the torso picture
# around the shoulders and chest follows, so the chest rises with a lift and sinks with the impact. The crane wing and the
# shoulder plates stay on the torso (they must not swing with the arms). The arm polygons stay below the beard.
# Placement: ground = the planted REAR boot (the left boot in all three stills), so the cut keeps the rear foot still;
# unit = master body height x (head height of the still / head height of the master), so the body keeps one size across cuts.
# Every coordinate is in pixels of the 1024 stills, read on grid overlays (.work/rig/grid_*.png).
import json, pathlib, sys
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from puppet_kit.core import key_magenta  # noqa: E402

DES = HERE.parent / "design"


def bbox(name):
    a = key_magenta(Image.open(DES / name))
    ys, xs = np.nonzero(a[..., 3] > 128)
    return xs.min(), xs.max(), ys.min(), ys.max()


_, _, my0, my1 = bbox("master_v08.png")
MASTER_H = float(my1 - my0 + 1)
MASTER_HEAD = 390 - 155            # topknot top to beard bottom on master_v08

SPEC = {
    "a": dict(still="pose_sweep_guard_v02.png", head=478 - 295, rear_boot=[340, 932],
              spear=[[262, 70], [300, 62], [345, 140], [385, 210], [395, 265], [372, 305], [362, 318], [532, 850], [500, 862],
                     [328, 325], [318, 300], [290, 275], [270, 200]],
              arm_l=[[258, 560], [280, 520], [330, 500], [350, 470], [410, 468], [440, 495], [452, 560], [450, 600], [420, 650],
                     [330, 652], [290, 640], [262, 610]],
              arm_r=[[400, 600], [440, 585], [500, 560], [560, 555], [610, 560], [645, 590], [652, 640], [630, 690], [560, 702],
                     [500, 706], [440, 708], [408, 690], [398, 650]],
              pivot=[470, 560], anchors=[{"pt": [480, 540], "radius": 120, "gain": 1.0}, {"pt": [330, 470], "radius": 100, "gain": 0.7}],
              tip=[295, 68], root=[345, 300]),
    "b": dict(still="pose_sweep_windup_v01.png", head=395 - 172, rear_boot=[400, 900],
              spear=[[28, 236], [120, 228], [200, 240], [250, 275], [285, 298], [300, 345], [895, 612], [905, 640], [885, 670],
                     [830, 660], [305, 400], [302, 495], [265, 500], [262, 410], [240, 400], [200, 390], [150, 360], [70, 280]],
              arm_l=[[320, 470], [345, 440], [400, 412], [440, 392], [488, 394], [520, 410], [540, 450], [530, 490], [500, 520],
                     [450, 555], [400, 580], [350, 580], [320, 550]],
              arm_r=[[595, 470], [650, 455], [700, 460], [760, 470], [790, 500], [782, 560], [740, 585], [690, 592], [640, 578],
                     [598, 560], [585, 520]],
              pivot=[550, 480], anchors=[{"pt": [560, 450], "radius": 120, "gain": 1.0}, {"pt": [380, 420], "radius": 100, "gain": 0.7}],
              tip=[30, 238], root=[270, 352]),
    "c": dict(still="pose_sweep_hit_v01.png", head=435 - 243, rear_boot=[130, 815],
              spear=[[15, 528], [800, 528], [810, 485], [860, 480], [900, 495], [1022, 540], [900, 590], [860, 605], [820, 605],
                     [808, 565], [806, 650], [758, 652], [760, 568], [15, 568]],
              arm_l=[[200, 500], [230, 465], [285, 468], [330, 490], [400, 498], [420, 530], [415, 580], [395, 598], [300, 598],
                     [255, 602], [210, 580]],
              arm_r=[[520, 500], [560, 480], [610, 478], [650, 490], [680, 520], [675, 575], [645, 600], [590, 598], [540, 592],
                     [522, 560]],
              pivot=[460, 540], anchors=[{"pt": [460, 500], "radius": 120, "gain": 1.0}, {"pt": [300, 440], "radius": 100, "gain": 0.7}],
              tip=[1020, 545], root=[820, 545]),
}
GROW = {"arm_l": 12, "arm_r": 12, "spear": 6}   # px: the hand-read polygons sit inside the thick outline; push them out so the
                                                 # outline travels with the arm (otherwise a stray dark line stays on the torso)


def grow_poly(poly, d):
    """Move every vertex d px outward along the mean outward normal of its two edges."""
    p = np.asarray(poly, float)
    area = 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])
    sgn = 1.0 if area > 0 else -1.0                      # image y points down: positive area = clockwise on screen
    out = []
    for i in range(len(p)):
        a, b, c = p[i - 1], p[i], p[(i + 1) % len(p)]
        n1 = np.array([(b - a)[1], -(b - a)[0]]) * sgn
        n2 = np.array([(c - b)[1], -(c - b)[0]]) * sgn
        n = n1 / (np.linalg.norm(n1) + 1e-9) + n2 / (np.linalg.norm(n2) + 1e-9)
        n = n / (np.linalg.norm(n) + 1e-9)
        out.append([round(float(b[0] + n[0] * d), 1), round(float(b[1] + n[1] * d), 1)])
    return out


NOTE = {"a": "A: guard, spear upright beside the face", "b": "B: wind-up, spear drawn back to the left at shoulder height",
        "c": "C: the hit, spear level to the right"}

if __name__ == "__main__":
    for key, s in SPEC.items():
        unit = round(MASTER_H * s["head"] / MASTER_HEAD, 1)
        g = s["rear_boot"]
        rig = {"id": "moon_crane",
               "note": f"Spear sweep {NOTE[key]}. Cut-out: torso (rest), spear, two arm layers on bone arms; muscle link shoulder_chest. "
                       "Ground = planted rear boot; unit from the head height so the body keeps one size across the cuts.",
               "sources": {"pose": f"../design/{s['still']}"}, "ground": g, "unit": unit,
               "bones": [{"name": "root", "parent": None, "pivot": g}, {"name": "body", "parent": "root", "pivot": g},
                         {"name": "arms", "parent": "body", "pivot": s["pivot"]}],
               "links": [{"name": "shoulder_chest", "arm": "arms", "mode": "stretch", "max_pull": 50,
                          "anchors": [dict(a, part="torso") for a in s["anchors"]]}],
               "sockets": {"spear_tip": {"bone": "arms", "pt": s["tip"]}, "spear_root": {"bone": "arms", "pt": s["root"]}},
               "parts": [{"name": "torso", "source": "pose", "bone": "body", "select": {"rest": True},
                          "fill_under": [{"part": "arm_l", "erode": 10, "reach": 30}, {"part": "arm_r", "erode": 10, "reach": 30},
                                         {"part": "spear", "erode": 4, "reach": 14}]},
                         {"name": "spear", "source": "pose", "bone": "arms", "select": {"poly": grow_poly(s["spear"], GROW["spear"])}},
                         {"name": "arm_l", "source": "pose", "bone": "arms", "select": {"poly": grow_poly(s["arm_l"], GROW["arm_l"])}},
                         {"name": "arm_r", "source": "pose", "bone": "arms", "select": {"poly": grow_poly(s["arm_r"], GROW["arm_r"])}}]}
        (HERE / f"rig_spear_{key}.json").write_text(json.dumps(rig, indent=1) + "\n")
        print(key, "ground", g, "unit", unit)
