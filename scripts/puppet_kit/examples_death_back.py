"""Build anims/death_back.json: the lion is hit, recoils, falls flat on his back, bounces once and lies still. Rig v2 only.
The root turns about the feet; root.ty is solved per frame so the lowest pixel of the body never sinks under the ground line."""
import json, pathlib, sys
import numpy as np
sys.path.insert(0, 'scripts')
from puppet_kit.core import Rig, T, track_value
A = pathlib.Path('out/heroes/lion_brawler')
rig = Rig(A / 'source/rig/rig.json')
N = 24
tr = {
  "_sway_period": 12,
  # whole body turns backward about the feet: slow start, gravity, impact, one small bounce, rest
  "root.rot":  [[0, 0], [3, -7, "out"], [10, -90, "in"], [12, -82, "out"], [14, -90, "in"], [16, -88, "out"], [18, -90, "inout"]],
  # knees give on the hit, buckle during the fall, legs go slack (half bent) on the ground
  "hips.ty":   [[0, 0], [3, 30, "out"], [9, 55, "inout"], [11, 30, "out"], [16, 22, "inout"]],
  "hips.tx":   [[0, 0], [3, -10, "out"], [9, 10, "inout"], [16, 0]],
  # recoil: chest pushed back, then whiplash: the head lags the body, snaps on impact and rolls
  "spine.rot": [[0, 0], [2, -8, "out"], [9, -6], [11, 4, "out"], [14, 0, "inout"]],
  "head.rot":  [[0, 0], [2, -10, "out"], [8, 6, "inout"], [10, 10, "in"], [12, -6, "out"], [15, 4, "inout"], [18, 2]],
  # arms fling forward and up with the hit, trail during the fall, flop on the floor
  "near_upper_arm.rot": [[0, 0], [2, -45, "out"], [8, -70, "inout"], [10, -95, "in"], [12, -80, "out"], [15, -88, "inout"]],
  "near_forearm.rot":   [[0, 0], [2, -40, "out"], [8, -25], [10, -5, "in"], [12, -25, "out"], [15, -15]],
  "near_hand.rot":      [[0, 0], [2, 10, "out"], [10, -20], [13, 5, "out"]],
  "far_upper_arm.rot":  [[0, 0], [2, -30, "out"], [8, -35, "inout"], [10, 10, "in"], [12, 45, "out"], [15, 38, "inout"]],
  "far_forearm.rot":    [[0, 0], [2, -45, "out"], [10, -10, "in"], [12, -5, "out"], [15, -12]],
  "tail.rot":  [[0, 0], [3, 15, "out"], [8, -20, "inout"], [11, -110, "in"], [13, -90, "out"], [16, -100, "inout"]],
  "torso.sway": [[0, 1], [10, 2.0], [16, 1.0, "out"]],
}
def lowest(tracks, f):
    tracks = dict(tracks, **{"tail.alpha": [[0, 0.0]]})      # the tail may lie flat on the ground: the body decides the lift
    img, _ = rig.render(tracks, f, T(800, 0), (1700, 2000))
    ys = np.where(img[..., 3] > 128)[0]
    return float(ys.max())
rest = lowest({}, 0)
lift = []
for f in range(N):
    low = lowest(tr, f)
    lift.append([f, round(min(0.0, rest - low), 1)])
tr["root.ty"] = [[f, v, "linear"] for f, v in lift]
anim = {"note": "Death, falling flat on the back (rig v2 only, no video): hit and recoil (arms fling up, knees give), the whole body turns backward about the feet "
        "with gravity (ease in), hits the ground at frame 11, bounces once, slack limbs and a last head roll, then lies still. root.ty is solved per frame so the body never sinks under the ground.",
        "version": "p01", "fps": 15, "loop": False, "shadow": "follow", "hit_frame": 1, "rig": "source/rig/rig.json", "frames": N, "tracks": tr}
(A / 'source/rig/anims/death_back.json').write_text(json.dumps(anim, indent=1) + "\n", encoding='utf-8')
print('rest lowest', rest, 'lift', [v for _, v in lift])
