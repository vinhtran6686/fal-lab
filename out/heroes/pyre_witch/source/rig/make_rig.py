# Writes rig.json and plate_v01.png for pyre_witch (master v12): head, both arms (raised and hanging) cut from the master, and a plate (the master with
# those three parts painted out) as the torso, so behind a moving arm or head there is real hair, not a smeared edge. Hair and hem sway through a band deform.
# Head and arms are hand-read polygons (the sleeves have dark facet lines inside, so a colour or flood cut leaks into the dress).
# Rebuild: python out/heroes/pyre_witch/source/rig/make_rig.py  (also writes .work/rig_masks.png, the review picture the polygons are read on)
import json, pathlib, sys
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage as ndi

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from puppet_kit.core import key_magenta  # noqa: E402

DES = HERE.parent / "design"
img = key_magenta(Image.open(DES / "master_v12.png"))
fg = img[..., 3] > 128
ys, xs = np.nonzero(fg)
UNIT = float(ys.max() - ys.min() + 1)               # one scale for every still of this character: the master's height
GROUND = [545.0, float(ys.max())]                    # between the two shoes, on the lowest row
H, W = fg.shape

# head: face and the hair around it (source px)
HEAD = [[418, 245], [425, 200], [445, 165], [480, 135], [520, 122], [545, 125], [585, 150], [608, 180], [640, 205], [642, 270], [600, 290], [566, 297],
        [548, 322], [500, 326], [470, 300], [440, 272]]
# arms: read on .work/rig_masks.png, a 2x crop of the keyed master whose top-left is (250, 100): view (vx, vy) -> source px (250 + vx / 2, 100 + vy / 2)
V2S = lambda pts: [[250 + vx // 2, 100 + vy // 2] for vx, vy in pts]
ARM_DOWN = V2S([(295, 460), (348, 468), (340, 545), (335, 628), (312, 690), (300, 720), (285, 760), (262, 790), (250, 825), (250, 860), (242, 890), (238, 935),
                (236, 1010), (215, 1060), (190, 1100), (168, 1130), (138, 1132), (112, 1090), (100, 1030), (104, 985), (125, 935), (145, 890), (150, 855),
                (190, 800), (225, 745), (250, 680), (272, 610), (285, 540)])
ARM_UP = V2S([(590, 462), (690, 462), (698, 540), (708, 600), (722, 640), (765, 664), (805, 678), (880, 660), (950, 645), (1010, 625), (1050, 605),
              (1072, 598), (1055, 632), (1010, 660), (1000, 680), (1050, 695), (1085, 718), (1112, 730), (1080, 752), (1030, 760), (1000, 775), (975, 795),
              (930, 815), (885, 795), (845, 790), (820, 790), (790, 775), (770, 750), (735, 742), (690, 742), (662, 722), (645, 690), (628, 640), (608, 590),
              (592, 545)])
polys = {"head": HEAD, "arm_up": ARM_UP, "arm_down": ARM_DOWN}
masks = {}
for n, pl in polys.items():
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.array(pl, np.int32)], 1)
    masks[n] = m > 0

# plate: every hole is filled with the colour of the nearest hair/outline pixel (dark, not red) outside the three parts, smoothed: behind a sleeve or a head there is hair.
# The raised hand's fingers stick out of the hair on the right, so that hole stops at x = HAIR_EDGE_X and leaves nothing behind the fingers.
HAIR_EDGE_X = 718
dil = lambda m: ndi.binary_dilation(m, iterations=3) & fg
xx = np.arange(W)[None, :] * np.ones((H, 1))
head_h, down_h = dil(masks["head"]), dil(masks["arm_down"])
up_h = dil(masks["arm_up"])
holes = head_h | down_h | up_h
zone = head_h | down_h | (up_h & (xx < HAIR_EDGE_X))
known = fg & ~holes
luma = 0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]
src_ok = known & (luma < 95) & (img[..., 0] < 70)
idx = ndi.distance_transform_edt(~src_ok, return_distances=False, return_indices=True)
near = img[idx[0], idx[1], :3].astype(np.float32)
wsum = np.maximum(ndi.gaussian_filter(zone.astype(np.float32), 3), 1e-3)[..., None]
soft = np.dstack([ndi.gaussian_filter(near[..., c] * zone, 3) for c in range(3)]) / wsum
plate = img.copy()
plate[zone, :3] = soft[zone]
keep = (fg & ~holes) | zone
AI = DES / "plate_noarms_v01.png"                    # the master with both arms ERASED by fal-image on the same canvas (puppet_prep.py align: PASS): real hair behind the arms
if "--code-plate" not in sys.argv and AI.exists():
    ai = key_magenta(Image.open(AI))
    ai_fg = ai[..., 3] > 128
    use_ai = ai_fg & ~head_h                          # everywhere except the head, which moves: behind the head the code fill stays
    plate[use_ai, :3] = ai[..., :3][use_ai]
    keep = (keep & ~(up_h | down_h)) | use_ai | (zone & head_h) | (keep & ~holes)
plate[~keep, :3] = (255, 0, 255)                     # the loader keys magenta, so empty means magenta (not an alpha channel)
Image.fromarray(plate[..., :3].clip(0, 255).astype(np.uint8), "RGB").save(HERE / ("plate_v01_code.png" if "--code-plate" in sys.argv else "plate_v01.png"))

rig = {"id": "pyre_witch", "note": "Master v12 split for the idle: head, raised arm (open palm), hanging arm cut from the master over a plate (the master without them).",
       "sources": {"pose": "../design/master_v12.png", "plate": ("plate_v01_code.png" if "--code-plate" in sys.argv else "plate_v01.png")}, "ground": GROUND, "unit": UNIT,
       "bones": [{"name": "root", "parent": None, "pivot": GROUND}, {"name": "body", "parent": "root", "pivot": GROUND},
                 {"name": "head", "parent": "body", "pivot": [520, 322]},
                 {"name": "arm_up", "parent": "body", "pivot": [575, 350]},
                 {"name": "arm_down", "parent": "body", "pivot": [418, 350]}],
       "parts": [{"name": "torso", "source": "plate", "bone": "body", "select": {"rest": True},
                  "deform": {"band": [380, 830], "range": 120, "range_end": 70, "amp": [5, 2], "wavelength": 130, "phase": -0.9}},
                 {"name": "arm_down", "source": "pose", "bone": "arm_down", "select": {"poly": ARM_DOWN}},
                 {"name": "head", "source": "pose", "bone": "head", "select": {"poly": HEAD}},
                 {"name": "arm_up", "source": "pose", "bone": "arm_up", "select": {"poly": ARM_UP}}]}
(HERE / "rig.json").write_text(json.dumps(rig, indent=1) + "\n")

# review picture: the three cut parts over the keyed master
work = HERE.parents[1] / ".work"
work.mkdir(exist_ok=True)
vis = np.full((H, W, 3), (70, 74, 84), np.uint8)
vis[fg] = img[..., :3][fg].astype(np.uint8)
for name, col in (("head", (0, 255, 0)), ("arm_up", (255, 160, 0)), ("arm_down", (255, 255, 0))):
    vis[masks[name] & ~ndi.binary_erosion(masks[name], iterations=2)] = col
Image.fromarray(vis).save(work / "rig_masks.png")
print("ground", GROUND, "unit", UNIT)
