# Writes the azure_blade rigs for the two approved pose stills (rebuild: python out/heroes/azure_blade/source/rig/make_rigs.py).
#   rig_a.json  pose A: torso (body, head, legs, cape) + arms (both arms, fists, shoulder plate) + blade, bones root > body > arms
#   rig_b.json  pose B: the same split
# Muscle link "shoulder_chest": when the arms bone slides (tx/ty), the picture of the torso near the shoulder and chest follows it, so the shoulder
# plate and the chest rise with the raised arms and sink with the impact (Puppet Kit `links`, mode stretch; the torso never tears).
# Every polygon below is in pixels of the 1024 stills. One scale for every still: unit = the master's body height (keeps the size across the cut).
import json, pathlib, sys
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from puppet_kit.core import key_magenta  # noqa: E402

DES = HERE.parent / "design"
FOOT = json.loads((HERE / "foot_marks.json").read_text())


def bbox(name):
    a = key_magenta(Image.open(DES / name))
    ys, xs = np.nonzero(a[..., 3] > 128)
    return xs.min(), xs.max(), ys.min(), ys.max()


_, _, my0, my1 = bbox("master_v06.png")
UNIT = float(my1 - my0 + 1)


def shift(poly, dx, dy):
    return [[x + dx, y + dy] for x, y in poly]


# Pose A (grid view origin (200, 40)); arms: pommel -> far arm -> shoulder plate -> near fist -> guard
A_ARMS = [[350, 52], [390, 64], [398, 98], [450, 98], [500, 112], [528, 140], [535, 176], [520, 200], [480, 206], [462, 214], [458, 262], [452, 300],
          [448, 345], [446, 392], [424, 416], [380, 418], [330, 410], [318, 372], [318, 330], [326, 296], [300, 270], [286, 240], [284, 200],
          [280, 165], [286, 128], [300, 92], [318, 62]]   # source px read on the keyed still; the right edge stays left of the face (x < 462 below the hair)
A_BLADE = shift([(68, 172), (120, 184), (142, 202), (130, 216), (112, 262), (98, 340), (84, 420), (52, 500), (28, 524), (20, 500), (34, 420), (52, 330),
                 (68, 240), (70, 205)], 200, 40)
# Pose B (grid view origin (40, 360)); arms: upper arm -> forearm bracers -> fists; blade lying on the ground
B_ARMS = shift([(546, 195), (588, 208), (620, 240), (642, 270), (656, 305), (670, 330), (690, 345), (668, 372), (672, 398), (650, 420), (626, 410),
                (580, 395), (560, 360), (530, 330), (505, 290), (515, 262), (540, 235)], 40, 360)
B_BLADE = shift([(655, 350), (700, 350), (760, 372), (850, 378), (925, 382), (905, 392), (840, 396), (760, 398), (700, 402), (672, 402), (660, 380)], 40, 360)

SPEC = {
    "A": dict(still="pose_skill_crescent_p1_v01.png", arms=A_ARMS, blade=A_BLADE, shoulder=[390, 335],
              anchors=[{"pt": [410, 335], "radius": 120, "gain": 1.0}, {"pt": [470, 430], "radius": 130, "gain": 0.7}]),
    "B": dict(still="pose_skill_crescent_p2_v03.png", arms=B_ARMS, blade=B_BLADE, shoulder=[600, 560],
              anchors=[{"pt": [600, 540], "radius": 110, "gain": 1.0}, {"pt": [520, 560], "radius": 120, "gain": 0.6}]),
}
DEFORM = {"core_self_hard": True, "amp": [9, 3], "wavelength": 130, "range": 60, "start": 6, "phase": -0.9}

for key, s in SPEC.items():
    x0, x1, y0, y1 = bbox(s["still"])
    g = [FOOT[key], float(y1)]
    rig = {"id": "azure_blade",
           "note": f"Pose {key} split for the studio: torso, arms (both arms, fists, shoulder plate) and blade. Muscle link: the arms' slide pulls shoulder and chest of the torso.",
           "sources": {"pose": f"../design/{s['still']}"}, "ground": g, "unit": UNIT,
           "bones": [{"name": "root", "parent": None, "pivot": g}, {"name": "body", "parent": "root", "pivot": g},
                     {"name": "arms", "parent": "body", "pivot": s["shoulder"]}],
           "links": [{"name": "shoulder_chest", "arm": "arms", "mode": "stretch", "max_pull": 60,
                      "anchors": [dict(a, part="torso") for a in s["anchors"]]}],
           "parts": [{"name": "torso", "source": "pose", "bone": "body", "select": {"rest": True},
                      "fill_under": [{"part": "arms", "erode": 10, "reach": 30}], "deform": DEFORM},
                     {"name": "blade", "source": "pose", "bone": "arms", "select": {"poly": s["blade"]}},
                     {"name": "arms", "source": "pose", "bone": "arms", "select": {"poly": s["arms"]}}]}
    (HERE / f"rig_{key.lower()}.json").write_text(json.dumps(rig, indent=1) + "\n")
    print(key, "ground", g, "unit", UNIT)
