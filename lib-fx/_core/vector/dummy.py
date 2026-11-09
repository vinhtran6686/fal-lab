"""A training dummy for PREVIEWS: a flat mannequin holding a weapon whose tip follows the slash head, drawn under the effect so the
user can judge scale and distance to the body (user 2026-11-09: "add a dummy fighter quickly to preview the strike").
It is never part of the effect itself: the clean frames are rendered without it (lib-fx rule: an effect is stored on its own).

Units: H = body height in px, feet = (x, y) of the feet pivot on the canvas (the lib-fx / fx_layers.py anchor), facing +x."""
import numpy as np
from PIL import Image, ImageDraw

BODY = (74, 79, 100)      # flat slate, readable on the dark preview background, darker than every fx layer
WEAPON = (120, 112, 104)
FLOOR = (52, 54, 68)


class Dummy:
    def __init__(self, feet, H, size, background=(18, 17, 24), weapon=1.35):
        self.fx, self.fy = feet
        self.H, self.size, self.bg = float(H), size, background
        self.Lw = weapon * self.H            # weapon length is FIXED: the hands slide along the shaft (choke up / reach out)

    def joints(self, tip):
        """Simple pose toward the weapon tip: hips over the feet, shoulders lean toward the tip, hands at arm's reach on the line
        shoulder -> tip, the weapon runs from behind the hands to the tip."""
        H = self.H
        tip = np.array(tip, float)
        hip = np.array([self.fx, self.fy - 0.47 * H])
        lean = np.clip((tip[0] - hip[0]) / H, -1, 1) * 0.12 * H
        crouch = np.clip((tip[1] - (self.fy - 0.6 * H)) / H, 0, 1) * 0.10 * H     # bends down when the tip goes low
        hip = hip + [0, crouch]
        sh = hip + [lean, -0.33 * H]
        d = tip - sh
        d = d / max(np.linalg.norm(d), 1e-6)
        dist = np.linalg.norm(tip - sh)
        hands = sh + d * np.clip(dist - 0.75 * self.Lw, 0.14 * H, 0.60 * H)   # close slash: hold the shaft mid-way; far: reach out
        butt = tip - d * self.Lw
        head = sh + [lean * 0.4, -0.15 * H]
        feet = [np.array([self.fx - 0.20 * H, self.fy]), np.array([self.fx + 0.22 * H, self.fy])]
        knees = [hip + (f - hip) * 0.5 + [-0.04 * H, 0] for f in feet]
        return dict(hip=hip, sh=sh, hands=hands, butt=butt, tip=tip, head=head, feet=feet, knees=knees)

    def frame(self, tip, ss=2):
        """RGB uint8 image: background, floor line, mannequin + weapon (supersampled)."""
        W, Hc = self.size
        im = Image.new("RGB", (W * ss, Hc * ss), tuple(self.bg))
        dr = ImageDraw.Draw(im)
        j = self.joints(tip)
        S = lambda p: (float(p[0]) * ss, float(p[1]) * ss)
        line = lambda a, b, w, c: dr.line([S(a), S(b)], fill=c, width=max(1, int(w * ss)))
        dot = lambda p, r, c: dr.ellipse([S(np.array(p) - r), S(np.array(p) + r)], fill=c)
        H = self.H
        dr.line([(0, self.fy * ss), (W * ss, self.fy * ss)], fill=FLOOR, width=2 * ss)
        line(j["butt"], j["tip"], 0.03 * H, WEAPON)
        for f, k in zip(j["feet"], j["knees"]):
            line(j["hip"], k, 0.09 * H, BODY); line(k, f, 0.08 * H, BODY); dot(k, 0.045 * H, BODY)
        line(j["hip"], j["sh"], 0.17 * H, BODY)
        dot(j["sh"], 0.085 * H, BODY); dot(j["hip"], 0.085 * H, BODY)
        line(j["sh"], j["hands"], 0.06 * H, BODY)
        dot(j["hands"], 0.04 * H, BODY)
        dot(j["head"], 0.10 * H, BODY)
        return np.asarray(im.resize((W, Hc), Image.LANCZOS))
