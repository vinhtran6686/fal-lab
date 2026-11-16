"""Bộ xương 3D proxy: giải tư thế một skill cận chiến từ file thông số JSON.

Hệ toạ độ thế giới: x = phải màn hình (về mục tiêu), y = lên, z = về phía camera.
Yaw (độ): 0 = nhìn camera, 90 = nhìn phải (mục tiêu), 180 = quay lưng, 270 = nhìn trái.
Tăng yaw = xoay ngược chiều kim đồng hồ nhìn từ trên.

Vật lý được ép bằng cấu trúc:
  * hông -> vai -> vũ khí: vai và vũ khí đọc CÙNG đường cong yaw của hông, trễ pha
    (chain.lag_chest, chain.lag_weapon); xoắn ngực-hông bị chặn ở chain.max_twist.
  * chân bám đất: mũi chân khoá, chân giải IK hai đoạn, gót xoay quanh mũi chân.
  * tay bám vũ khí: tay giải IK tới điểm nắm; nếu không với tới, cả cây vũ khí dời về phía vai.
  * hitstop: khung giữ chèn ở ánh xạ thời gian, mọi bộ phận dừng cùng lúc.
"""
import json
import math

import numpy as np

UP = np.array([0.0, 1.0, 0.0])


# ------------------------------------------------------------------ nội suy
def pchip(keys):
    """Hermite đơn điệu (Fritsch-Carlson). keys: {τ: giá trị} (khoá chuỗi hoặc số)."""
    ks = sorted((float(k), float(v)) for k, v in keys.items())
    xs = np.array([k for k, _ in ks])
    ys = np.array([v for _, v in ks])
    if len(xs) == 1:
        return lambda t: float(ys[0])
    h = np.diff(xs)
    d = np.diff(ys) / h
    m = np.zeros_like(ys)
    for i in range(1, len(ys) - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

    def f(t):
        t = float(np.clip(t, xs[0], xs[-1]))
        i = int(np.clip(np.searchsorted(xs, t) - 1, 0, len(h) - 1))
        s = (t - xs[i]) / h[i]
        return float((2 * s**3 - 3 * s**2 + 1) * ys[i] + (s**3 - 2 * s**2 + s) * h[i] * m[i]
                     + (-2 * s**3 + 3 * s**2) * ys[i + 1] + (s**3 - s**2) * h[i] * m[i + 1])
    return f


# ------------------------------------------------------------------ hình học
def fwd(yaw):
    a = math.radians(yaw)
    return np.array([math.sin(a), 0.0, math.cos(a)])


def right(yaw):
    """Bên phải của nhân vật (nhìn camera thì bên phải nhân vật = trái màn hình)."""
    a = math.radians(yaw)
    return np.array([-math.cos(a), 0.0, math.sin(a)])


def wrap(a):
    return (a + 180) % 360 - 180


def ik2(root, target, l1, l2, pole):
    """IK hai đoạn. Trả (khớp giữa, đầu mút, độ vượt tầm)."""
    d = target - root
    dist = float(np.linalg.norm(d))
    over = max(0.0, dist - (l1 + l2) * 0.999)
    dc = min(dist, (l1 + l2) * 0.999)
    dn = d / max(dist, 1e-9)
    end = root + dn * dc
    a = (l1 * l1 - l2 * l2 + dc * dc) / (2 * dc)
    hgt = math.sqrt(max(l1 * l1 - a * a, 0.0))
    p = pole - dn * np.dot(pole, dn)
    if np.linalg.norm(p) < 1e-6:
        p = UP - dn * np.dot(UP, dn)
    p = p / np.linalg.norm(p)
    return root + dn * a + p * hgt, end, over


def smoothstep(s):
    s = min(max(s, 0.0), 1.0)
    return s * s * (3 - 2 * s)


# ------------------------------------------------------------------ mô hình
class Proxy:
    def __init__(self, params):
        if isinstance(params, str):
            with open(params, encoding="utf-8") as fh:
                params = json.load(fh)
        self.p = params
        self.b = params["body"]
        self.w = params["weapon"]
        self.c = params["chain"]
        self.tm = params["timing"]
        self.fps = params.get("fps", 15)
        self.ch = {k: pchip(v) for k, v in params["channels"].items()}
        ft = params["feet"]
        self.tracks = ft.get("tracks")          # vết chân từ chuyển động nguồn (retarget.py)
        if not self.tracks:
            self.back_toe = np.array(ft["back_toe"], float)
            self.front_toe0 = np.array(ft["front_toe"], float)
        self.steps = ft.get("steps", [])
        self.mass = self.b["mass"]

    # -------------------------------------------------------------- thời gian
    def frame_times(self):
        """τ của từng khung xuất ra, có chèn khung giữ hitstop."""
        ts, t = [], 0.0
        while t <= self.tm["t_end"] + 1e-9:
            ts.append(t)
            if abs(t - self.tm["t_hit"]) < 1e-9:
                ts += [t] * self.tm.get("hitstop_frames", 0)
            t += 1.0
        return ts

    def phase_of(self, t):
        name = self.tm["phases"][0][1]
        for t0, n in self.tm["phases"]:
            if t >= t0:
                name = n
        return name

    # -------------------------------------------------------------- chân trước
    def front_toe(self, t):
        """Mũi chân trước: (vị trí, đang nhấc?, điểm sẽ đặt xuống)."""
        pos = self.front_toe0.copy()
        for st in self.steps:
            a = pos.copy()
            b = a + np.array([st["dx"], 0, st.get("dz", 0.0)])
            if t < st["from"]:
                return pos, False, pos.copy()
            if t <= st["to"]:
                s = (t - st["from"]) / (st["to"] - st["from"])
                p = a + (b - a) * smoothstep(s)
                p[1] = st.get("lift", 0.15) * math.sin(math.pi * s)
                return p, 0 < s < 1, b
            pos = b
        return pos, False, pos.copy()

    def track_toe(self, side, t):
        """Mũi chân theo vết: [{t0, t1, pos}] là các đoạn chạm đất (mũi khoá ở pos);
        giữa hai đoạn là một bước (nội suy smoothstep, nhấc theo 'lift')."""
        segs = self.tracks[side]
        lift = self.tracks.get("lift", 0.14)
        for k, sg in enumerate(segs):
            if t < sg["t0"]:
                if k == 0:
                    return np.array(sg["pos"], float), False, np.array(sg["pos"], float)
                a, b = segs[k - 1], sg
                s = (t - a["t1"]) / max(b["t0"] - a["t1"], 1e-6)
                pa, pb = np.array(a["pos"], float), np.array(b["pos"], float)
                p = pa + (pb - pa) * smoothstep(s)
                p[1] = lift * math.sin(math.pi * min(max(s, 0), 1)) * min(1.0, np.linalg.norm(pb - pa) / 0.15)
                return p, True, pb
            if t <= sg["t1"]:
                return np.array(sg["pos"], float), False, np.array(sg["pos"], float)
        last = np.array(segs[-1]["pos"], float)
        return last, False, last

    # -------------------------------------------------------------- tư thế
    def pose(self, t):
        b, w, c, ch = self.b, self.w, self.c, self.ch
        P = ch["pelvis_yaw"](t)
        C_raw = ch["pelvis_yaw"](t - c["lag_chest"]) + ch["chest_off"](t)
        twist = float(np.clip(C_raw - P, -c["max_twist"], c["max_twist"]))
        C = P + twist
        S = ch["pelvis_yaw"](t - c["lag_weapon"]) + ch["weapon_off"](t)
        pitch = ch["weapon_pitch"](t)

        pelvis = np.array([ch["root_x"](t), ch["root_y"](t), 0.0])
        chest = pelvis + UP * b["spine"] + fwd(C) * 0.04
        neck = chest + UP * b["neck"]
        H = C + float(np.clip(wrap(c["head_spot_target"] - C), -c["head_spot_limit"],
                              c["head_spot_limit"]))
        head = neck + UP * b["head_above_neck"]

        hipR = pelvis + right(P) * b["hip_half"]
        hipL = pelvis - right(P) * b["hip_half"]
        shR = chest + right(C) * b["shoulder_half"]
        shL = chest - right(C) * b["shoulder_half"]

        # vũ khí
        a = math.radians(pitch)
        sd = fwd(S) * math.cos(a) + UP * math.sin(a)
        # tâm hai tay đặt trước ngực (grip_center), hai tay chia đều quanh tâm dọc theo cán
        go = b["grip_center"]
        slide = ch["weapon_slide"](t)
        gap = w["grip_gap"] - w.get("slide_gap_factor", 0.6) * max(0.0, slide)
        center = (chest + right(C) * go["right"] + fwd(C) * go["forward"]
                  - UP * ch["hand_drop"](t) + sd * slide)
        rear = center - sd * gap / 2
        front = center + sd * gap / 2
        reach = (b["upper_arm"] + b["forearm"]) * 0.97
        shift = np.zeros(3)
        for _ in range(60):
            oR = np.linalg.norm(rear - shR) - reach
            oL = np.linalg.norm(front - shL) - reach
            if oR <= 1e-4 and oL <= 1e-4:
                break
            mv = np.zeros(3)
            if oR > 0:
                mv += (shR - rear) / np.linalg.norm(shR - rear) * oR
            if oL > 0:
                mv += (shL - front) / np.linalg.norm(shL - front) * oL
            mv *= 0.6
            rear, front, shift = rear + mv, front + mv, shift + mv
        butt = rear - sd * w["grip_rear"]
        tip = rear + sd * (w["length"] - w["grip_rear"])
        elR, handR, overR = ik2(shR, rear, b["upper_arm"], b["forearm"], -UP + right(C) * 0.7)
        elL, handL, overL = ik2(shL, front, b["upper_arm"], b["forearm"], -UP - right(C) * 0.7)

        # chân
        fy = ch["pelvis_yaw"](t - c["foot_lag"])
        if self.tracks:
            toeR, swingR, landR = self.track_toe("R", t)
            toeL, swingL, landL = self.track_toe("L", t)
        else:
            toeR, swingR, landR = self.back_toe.copy(), False, self.back_toe.copy()
            toeL, swingL, landL = self.front_toe(t)
        sw = self.tm["spin_heel_window"]
        spin = sw[0] < t < sw[1]
        hl = self.tm["spin_heel_lift"] if spin else 0.0
        lg = self.tm["lunge_heel"]
        lunge = min((t - lg["start"]) / lg["rise"], (lg["end"] - t) / lg["fall"])
        hlR = max(hl, lg["lift"] * float(np.clip(lunge, 0, 1)))
        fl = b["foot_len"]
        max_lift = b.get("max_heel_lift", 0.24)

        def leg(hip, toe, yaw_f, lift):
            # Gót nhấc thêm vừa đủ để chân với tới (kiễng trên mũi chân); mũi chân vẫn khoá.
            while True:
                heel = toe - fwd(yaw_f) * fl + UP * lift
                ank = heel + fwd(yaw_f) * 0.08 + UP * b["ankle_h"]
                kn, ank2, over = ik2(hip, ank, b["thigh"], b["shin"], fwd(yaw_f) + UP * 0.2)
                if over <= 1e-4 or lift >= max_lift:
                    return heel, kn, ank2, over, lift
                lift = min(max_lift, lift + 0.01)

        fyR = fy - 15 if not self.tracks else self.foot_yaw("R", t, fy)
        fyL = fy + 15 if not self.tracks else self.foot_yaw("L", t, fy)
        heelR, knR, ankR2, oLR, hlR = leg(hipR, toeR, fyR, hlR)
        heelL, knL, ankL2, oLL, hlL = leg(hipL, toeL, fyL, hl)

        J = dict(pelvis=pelvis, chest=chest, neck=neck, head=head,
                 hipR=hipR, hipL=hipL, kneeR=knR, kneeL=knL, ankleR=ankR2, ankleL=ankL2,
                 heelR=heelR, heelL=heelL, toeR=toeR, toeL=toeL,
                 shR=shR, shL=shL, elbowR=elR, elbowL=elL, handR=handR, handL=handL,
                 butt=butt, tip=tip, blade_root=tip - sd * w["blade_len"])
        info = dict(yaw_pelvis=P, yaw_chest=C, yaw_weapon=S, yaw_head=H, weapon_pitch=pitch,
                    twist=twist, twist_raw=C_raw - P, weapon_shift=float(np.linalg.norm(shift)),
                    spin_rate=(ch["pelvis_yaw"](t + 0.1) - ch["pelvis_yaw"](t - 0.1)) / 0.2,
                    reach_over=dict(armR=overR, armL=overL, legR=oLR, legL=oLL),
                    foot_swing=swingL or swingR, swing=dict(R=swingR, L=swingL),
                    swing_land=landL if swingL else landR, heel_lift=dict(R=hlR, L=hlL))
        return J, info

    def foot_yaw(self, side, t, fallback):
        fy = self.tracks.get("yaw_" + side)
        return pchip(fy)(t) if fy else fallback

    def com(self, J):
        tot = sum(self.mass.values())
        return sum(J[k] * m for k, m in self.mass.items()) / tot
