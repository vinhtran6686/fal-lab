"""Dựng proxy 3D của một skill cận chiến: hình, chỉ số vật lý, so với tham chiếu, dữ liệu cho rig.

    python scripts/motion_proxy/build.py out/heroes/<id>/source/rig/proxy_<skill>.json [--out DIR]

Mặc định ghi vào <asset>/.work/motion_proxy/<tên file>/ (git bỏ qua):
  anim.gif, anim_slow.gif   camera game + nhìn từ trên + thanh nhịp
  compare.gif               tham chiếu (ghép theo pha, 'reference.align') cạnh proxy
  sheet.png                 bảng khung
  blocks/fNN.png            khung khối màu nền trong (khung mẫu cho mô hình ảnh)
  curves.png                góc, vận tốc góc, trọng tâm, tốc độ mũi vũ khí
  metrics.md                tiêu chí vật lý ĐẠT / KHÔNG ĐẠT
  frames.json               toạ độ 2D, độ sâu, hướng thân, thứ tự lớp, vệt mũi vũ khí
  weapon_track.json         gốc lưỡi / mũi vũ khí theo định dạng scripts/puppet.py track (đơn vị H)
Doc: docs/scripts/motion_proxy/motion-proxy-guide.md
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from matplotlib.path import Path as MplPath

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skeleton import Proxy, fwd, right, UP  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def font(size, bold=False):
    for name in (("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
                 ("arialbd.ttf" if bold else "arial.ttf")):
        for d in ("/usr/share/fonts/truetype/dejavu", "C:/Windows/Fonts"):
            p = os.path.join(d, name)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_SM, F_MD, F_BD = font(13), font(15), font(17, True)


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ================================================================== camera
class Cam:
    def __init__(self, pitch_deg=15, scale=78, size=(700, 470), origin=(250, 420)):
        self.pitch = math.radians(pitch_deg)
        self.s = scale
        self.size = size
        self.o = origin

    def proj(self, p):
        return np.array([self.o[0] + p[0] * self.s,
                         self.o[1] - (p[1] * math.cos(self.pitch) - p[2] * math.sin(self.pitch)) * self.s])

    def depth(self, p):
        return p[2] * math.cos(self.pitch) + p[1] * math.sin(self.pitch)


# ================================================================== vẽ nhân vật
class Painter:
    def __init__(self, proxy, cam):
        self.px = proxy
        self.cam = cam
        pal = {k: hexc(v) for k, v in proxy.p["palette"].items()}
        self.pal = pal
        self.ink = pal["ink"]

    # --- nguyên tố
    def capsule(self, dr, a, b, w, col, ow=3):
        for c, ww in ((self.ink, w + 2 * ow), (col, w)):
            dr.line([tuple(a), tuple(b)], fill=c, width=int(ww))
            for q in (a, b):
                r = ww / 2
                dr.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=c)

    def disc(self, dr, q, r, col, ow=3):
        dr.ellipse([q[0] - r - ow, q[1] - r - ow, q[0] + r + ow, q[1] + r + ow], fill=self.ink)
        dr.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=col)

    def poly(self, dr, pts, col, ow=4):
        dr.polygon([tuple(p) for p in pts], fill=col, outline=self.ink, width=ow)

    # --- danh sách phần thân (tên, độ sâu, hàm vẽ)
    def parts(self, J, inf):
        P, cam, b, pal = self.px, self.cam, self.px.b, self.pal
        pr = cam.proj
        s = cam.s
        out = []

        def add(name, pts3d, fn, bias=0.0):
            d = float(np.mean([cam.depth(q) for q in pts3d])) + bias
            out.append((name, d, fn))

        # chân: đùi (quần da), ống (ủng) + ốp gối vàng
        for side, shade in (("R", 1.0), ("L", 0.78)):
            hip, kn, an, he, to = (J["hip" + side], J["knee" + side], J["ankle" + side],
                                   J["heel" + side], J["toe" + side])
            pants = tuple(int(c * shade) for c in pal["leather"])
            boot = tuple(int(c * shade) for c in pal["shaft"])
            add("thigh" + side, (hip, kn), lambda dr, hip=hip, kn=kn, c=pants:
                self.capsule(dr, pr(hip), pr(kn), 0.30 * s, c))
            add("shin" + side, (kn, an), lambda dr, kn=kn, an=an, c=boot:
                self.capsule(dr, pr(kn), pr(an), 0.26 * s, c))
            add("foot" + side, (he, to), lambda dr, he=he, to=to, c=boot:
                self.capsule(dr, pr(he), pr(to), 0.20 * s, c))
            add("knee" + side, (kn,), lambda dr, kn=kn:
                self.disc(dr, pr(kn), 0.10 * s, pal["gold"]), bias=0.05)

        # thân: giáp ngực hình thang + váy giáp + thắt lưng + huy hiệu
        C, Pv = inf["yaw_chest"], inf["yaw_pelvis"]
        ch, pe = J["chest"], J["pelvis"]
        rC, rP = right(C), right(Pv)
        waist = pe + UP * 0.48
        shoulder_top = ch + UP * 0.05

        def torso(dr):
            sp = b["shoulder_pad_half"] * 0.85
            wh = b["waist_half"]
            q = [pr(shoulder_top + rC * sp), pr(shoulder_top - rC * sp),
                 pr(waist - rP * wh), pr(waist + rP * wh)]
            self.poly(dr, q, pal["armor"])
            sk = [pr(waist + rP * wh), pr(waist - rP * wh),
                  pr(pe - UP * 0.16 - rP * (wh + 0.06)), pr(pe - UP * 0.16 + rP * (wh + 0.06))]
            self.poly(dr, sk, pal["armor_dark"])
            belt = [pr(waist + rP * wh + UP * 0.08), pr(waist - rP * wh + UP * 0.08),
                    pr(waist - rP * wh - UP * 0.06), pr(waist + rP * wh - UP * 0.06)]
            self.poly(dr, belt, pal["leather"], 3)
            fP = fwd(Pv)
            if fP[2] > 0.0:
                bq = pr(waist + fP * 0.40)
                self.disc(dr, bq, 0.08 * s, pal["gold"], 2)
                sash = [pr(waist + fP * 0.40 + rP * 0.07 - UP * 0.05),
                        pr(waist + fP * 0.40 - rP * 0.07 - UP * 0.05),
                        pr(pe + fP * 0.40 - UP * 0.30)]
                self.poly(dr, sash, pal["red"], 2)
            fC = fwd(C)
            if fC[2] > 0.1:                       # chim vàng trước ngực
                e = ch - UP * 0.42 + fC * 0.42
                q = pr(e)
                r = 0.22 * s * min(1.0, fC[2] + 0.25)
                dr.ellipse([q[0] - r, q[1] - r * 0.8, q[0] + r, q[1] + r * 0.8],
                           fill=pal["gold"], outline=self.ink, width=3)
                dr.ellipse([q[0] - r * 0.45, q[1] - r * 0.35, q[0] + r * 0.45, q[1] + r * 0.35],
                           fill=pal["armor"])
        add("torso", (ch - UP * 0.5,), torso)

        # giáp vai + cánh hạc (vai trái nhân vật, như master)
        for side, k in (("R", "shR"), ("L", "shL")):
            q3 = J[k] + UP * 0.04
            def pad(dr, q3=q3):
                q = pr(q3)
                r = 0.27 * s
                dr.ellipse([q[0] - r - 3, q[1] - r * 0.8 - 3, q[0] + r + 3, q[1] + r * 0.8 + 3], fill=self.ink)
                dr.ellipse([q[0] - r, q[1] - r * 0.8, q[0] + r, q[1] + r * 0.8], fill=pal["armor"],
                           outline=pal["gold"], width=max(3, int(0.06 * s)))
            add("pad" + side, (q3,), pad, bias=0.06)
        wing_root = J["shL"] + UP * 0.10

        def wing(dr):
            # quạt 4 lông ngà rộng bản, gốc ở vai trái, xoè lên và ra ngoài (như master)
            out_dir = -rC
            back = -fwd(C) * 0.08
            for k, (ang, ln) in enumerate(((80, 0.95), (62, 0.88), (44, 0.80), (26, 0.70))):
                a = math.radians(ang)
                axis = UP * math.sin(a) + out_dir * math.cos(a)
                side = UP * math.cos(a) - out_dir * math.sin(a)
                root = wing_root + out_dir * (0.04 * k) + back
                q = [root + side * 0.07, root + axis * ln * 0.55 + side * 0.13,
                     root + axis * ln, root + axis * ln * 0.55 - side * 0.11, root - side * 0.06]
                self.poly(dr, [pr(p) for p in q], pal["ivory"], 3)
                g0 = root + axis * ln * 0.55 - side * 0.11
                dr.line([tuple(pr(root + axis * 0.08)), tuple(pr(g0 + side * 0.05))],
                        fill=pal["gold"], width=3)
        add("wing", (wing_root - fwd(C) * 0.15,), wing, bias=-0.02)

        # tay: bắp tay da, cẳng tay giáp + đai vàng, nắm đấm to
        for side, shade in (("R", 1.0), ("L", 0.8)):
            sh, el, hd = J["sh" + side], J["elbow" + side], J["hand" + side]
            skin = tuple(int(c * shade) for c in pal["skin"])
            arm = tuple(int(c * shade) for c in pal["armor"])
            add("upperArm" + side, (sh, el), lambda dr, sh=sh, el=el, c=skin:
                self.capsule(dr, pr(sh), pr(el), 0.28 * s, c))
            add("forearm" + side, (el, hd), lambda dr, el=el, hd=hd, c=arm:
                (self.capsule(dr, pr(el), pr(hd), 0.32 * s, c),
                 self.capsule(dr, pr(el + (hd - el) * 0.75), pr(el + (hd - el) * 0.78),
                              0.34 * s, pal["gold"], 2)))
            add("fist" + side, (hd,), lambda dr, hd=hd, c=skin:
                self.disc(dr, pr(hd), b["fist_r"] * s, c), bias=0.03)

        # đầu: da, tóc, búi, râu, mắt phát sáng
        hd3 = J["head"]
        H = inf["yaw_head"]

        def head(dr):
            q = pr(hd3)
            r = b["head_r"] * s
            fH, rH = fwd(H), right(H)
            bun = pr(hd3 + UP * (b["head_r"] + 0.10) - fH * 0.06)
            self.disc(dr, bun, 0.13 * s, pal["hair"])
            self.disc(dr, q, r, pal["skin"], 4)
            dr.pieslice([q[0] - r, q[1] - r, q[0] + r, q[1] + r], 180, 360, fill=pal["hair"])
            if fH[2] > -0.3:
                beard = pr(hd3 - UP * 0.14 + fH * 0.14)
                rb = r * 0.62
                dr.pieslice([beard[0] - rb, beard[1] - rb, beard[0] + rb, beard[1] + rb], 0, 180,
                            fill=pal["hair"], outline=self.ink, width=2)
                for sgn in (1, -1):
                    e3 = hd3 + fH * b["head_r"] * 0.85 + rH * 0.12 * sgn + UP * 0.03
                    if np.dot(fH * 0.85 + rH * 0.36 * sgn, [0, 0, 1]) > -0.15:
                        e = pr(e3)
                        dr.ellipse([e[0] - 5, e[1] - 3, e[0] + 5, e[1] + 3], fill=pal["eye"],
                                   outline=self.ink, width=1)
            else:
                dr.pieslice([q[0] - r, q[1] - r, q[0] + r, q[1] + r], 0, 360, fill=pal["hair"])
                self.disc(dr, pr(hd3 + UP * 0.05 - fH * 0.25), 0.10 * s, pal["red"], 2)
        add("head", (hd3,), head)

        # thương: cán chia đoạn để thân che đúng phần, mũi lá + chắn trăng + tua
        w = self.px.w
        bt, tp = J["butt"], J["tip"]
        d = (tp - bt) / np.linalg.norm(tp - bt)
        base = tp - d * w["blade_len"]
        n = 10
        for i in range(n):
            a3 = bt + (base - bt) * (i / n)
            b3 = bt + (base - bt) * ((i + 1) / n)
            add(f"shaft{i}", (a3, b3), lambda dr, a3=a3, b3=b3:
                self.capsule(dr, pr(a3), pr(b3), 0.07 * s, pal["shaft"], 2))

        def blade(dr):
            side = np.cross(d, [0, 0, 1.0])
            if np.linalg.norm(side) < 1e-3:
                side = np.array([0, 1.0, 0])
            side = side / np.linalg.norm(side)
            hw = w["blade_half_w"]
            leaf = [pr(tp), pr(base + d * w["blade_len"] * 0.35 + side * hw), pr(base),
                    pr(base + d * w["blade_len"] * 0.35 - side * hw)]
            self.poly(dr, leaf, pal["blade"], 3)
            cq = pr(base)
            rr = 0.15 * s
            dr.arc([cq[0] - rr, cq[1] - rr, cq[0] + rr, cq[1] + rr], 200, 340, fill=self.ink, width=9)
            dr.arc([cq[0] - rr, cq[1] - rr, cq[0] + rr, cq[1] + rr], 200, 340, fill=pal["gold"], width=5)
            tq = pr(base - d * 0.12)
            self.capsule(dr, tq, tq + np.array([0, 0.30 * s]), 0.07 * s, pal["red"], 2)
        add("blade", (base, tp), blade)
        return out

    def draw(self, img, J, inf):
        dr = ImageDraw.Draw(img)
        ps = sorted(self.parts(J, inf), key=lambda p: p[1])
        for _, _, fn in ps:
            fn(dr)
        return [p[0] for p in ps]


# ================================================================== chỉ số
def support(P, J, com_p, inf, com_v=None):
    """Trọng tâm so với vùng đỡ. 0 = chân sau, 1 = chân trước.
    Hai chân chạm đất: trọng tâm chiếu xuống phải nằm giữa hai mũi chân.
    Một chân đang nhấc: dùng điểm bắt (capture point = trọng tâm + vận tốc * sqrt(h/g)); điểm này phải nằm
    giữa chân trụ và điểm chân sắp đặt xuống, tức bước chân kịp đỡ cú ngã có kiểm soát."""
    b = J["toeR"]
    f = J["toeL"]
    c = com_p.copy()
    if inf["foot_swing"]:
        f = inf["swing_land"].copy()
        if com_v is not None:
            m_per_u = P.b.get("real_height_m", 1.8) / P.b["height"]
            g = 9.81 / m_per_u
            c = c + com_v * math.sqrt(max(com_p[1], 1e-3) / g)
    seg = f - b
    seg[1] = 0
    c = c - b
    c[1] = 0
    u = float(np.dot(c, seg) / np.dot(seg, seg))
    perp = float(np.linalg.norm(c - seg * u))
    return u, perp, (-0.05 <= u <= 1.05) and perp < 0.30


def tip_trail(P, t, span=1.0, step=0.125):
    return [P.pose(x)[0]["tip"] for x in np.arange(max(0, t - span), t + 1e-9, step)]


PAINTER = None


def compute(P, cam):
    TS = P.frame_times()
    F = [P.pose(t) for t in TS]
    N = len(TS)
    dt = 0.02
    tt = np.arange(0, P.tm["t_end"] + dt, dt)
    infs = [P.pose(t)[1] for t in tt]
    yP = np.array([i["yaw_pelvis"] for i in infs])
    yC = np.array([i["yaw_chest"] for i in infs])
    yW = np.array([i["yaw_weapon"] for i in infs])
    vP, vC, vW = (np.gradient(a, dt) for a in (yP, yC, yW))
    M = dict(TS=TS, F=F, N=N, curves=dict(tt=tt, yP=yP, yC=yC, yW=yW, vP=vP, vC=vC, vW=vW))
    rw = P.tm["release_window"]

    def zc(v):
        w = (tt > rw[0]) & (tt < rw[1])
        idx = np.where(w[:-1] & (v[:-1] < 0) & (v[1:] >= 0))[0]
        return float(tt[idx[0]]) if len(idx) else None
    M["release"] = {"hông": zc(vP), "vai": zc(vC), "vũ khí": zc(vW)}
    sw = P.tm["sweep_window"]
    w = (tt > sw[0]) & (tt < sw[1])
    M["peak"] = {k: float(tt[w][np.argmax(v[w])]) for k, v in (("hông", vP), ("vai", vC), ("vũ khí", vW))}
    M["peak_v"] = {k: float(np.max(v[w])) for k, v in (("hông", vP), ("vai", vC), ("vũ khí", vW))}
    M["twist_max"] = float(np.max(np.abs(yC - yP)))
    M["twist_raw_max"] = float(max(abs(i["twist_raw"]) for i in infs))
    slip, reach, sup, tipx, tipv, occl = [], [], [], [], [], []
    cross, shift, side = [], [], []
    for i, (J, inf) in enumerate(F):
        t = TS[i]
        cv = (P.com(P.pose(t + 0.25)[0]) - P.com(P.pose(t - 0.25)[0])) / 0.5 * P.fps
        sup.append(support(P, J, P.com(J), inf, cv))
        # chân bắt chéo: thứ tự hai bàn chân theo trục ngang của hông bị đảo
        rP = right(inf["yaw_pelvis"])
        cross.append(float(np.dot(J["ankleR"] - J["ankleL"], rP)) < 0)
        shift.append(inf["weapon_shift"])
        # lưỡi thương trước hay sau thân (theo thứ tự vẽ thật của painter)
        parts = {p[0]: p[1] for p in PAINTER.parts(J, inf)}
        side.append("front" if parts["blade"] > parts["torso"] else "back")
        reach.append(max(inf["reach_over"].values()))
        tipx.append(float(J["tip"][0]))
        if i:
            Jp, ip = F[i - 1]
            s = 0.0
            if not inf["foot_swing"] and not ip["foot_swing"]:
                s = max(np.linalg.norm(J["toeR"] - Jp["toeR"]), np.linalg.norm(J["toeL"] - Jp["toeL"]))
            slip.append(float(s))
            tipv.append(float(np.linalg.norm(J["tip"] - Jp["tip"])))
        else:
            slip.append(0.0)
            tipv.append(0.0)
        # vũ khí bị che: điểm trên cán nằm SAU ngực và lọt vào trong đa giác thân trên ảnh
        hidden = 0
        torso_poly = MplPath([cam.proj(J[x]) for x in ("shR", "shL", "hipL", "hipR")])
        for k in range(1, 10):
            q = J["butt"] + (J["tip"] - J["butt"]) * (k / 10)
            if cam.depth(q) < cam.depth(J["chest"]) - 0.1 and torso_poly.contains_point(cam.proj(q)):
                hidden += 1
        occl.append(hidden)
    M.update(slip=slip, reach=reach, support=sup, tipx=tipx, tipv=tipv, occl=occl,
             cross=cross, shift=shift, side=side)
    M["hit_frames"] = [i for i, t in enumerate(TS) if abs(t - P.tm["t_hit"]) < 1e-9]
    M["sweep_hit"] = min((i for i in range(N) if sw[0] < TS[i] < sw[1]),
                         key=lambda i: abs(F[i][1]["yaw_weapon"] - 90))
    return M


# ================================================================== khung hình
def view_name(yaw):
    a = yaw % 360
    for lim, n in ((22.5, "chính diện"), (67.5, "3/4 phải"), (112.5, "nghiêng phải"),
                   (157.5, "3/4 lưng phải"), (202.5, "lưng"), (247.5, "3/4 lưng trái"),
                   (292.5, "nghiêng trái"), (337.5, "3/4 trái"), (360.1, "chính diện")):
        if a < lim:
            return n


def render_game(P, cam, painter, M, i, overlay=True, bg=(250, 250, 247)):
    J, inf = M["F"][i]
    W, H = cam.size
    img = Image.new("RGB", (W, H), bg)
    dr = ImageDraw.Draw(img)
    cp = P.com(J)
    g = cam.proj(np.array([cp[0], 0, cp[2]]))
    dr.line([(0, cam.o[1]), (W, cam.o[1])], fill=(205, 205, 200), width=1)
    dr.ellipse([g[0] - 75, g[1] - 13, g[0] + 75, g[1] + 13], fill=(222, 222, 216))
    tx = cam.proj(np.array([P.p.get("target_x", 4.2), 0, 0]))
    dr.rectangle([tx[0] - 4, tx[1] - 170, tx[0] + 4, tx[1]], fill=(200, 120, 110))
    dr.text((tx[0] - 30, tx[1] + 6), "mục tiêu", font=F_SM, fill=(160, 90, 80))
    painter.draw(img, J, inf)
    if overlay:
        trail = tip_trail(P, M["TS"][i])
        dP = cam.depth(J["pelvis"])
        for a, b in zip(trail[:-1], trail[1:]):
            near = (cam.depth(a) + cam.depth(b)) / 2 > dP
            dr.line([tuple(cam.proj(a)), tuple(cam.proj(b))],
                    fill=(70, 150, 230) if near else (170, 196, 222), width=4 if near else 2)
        ok = M["support"][i][2]
        col = (40, 160, 80) if ok else (220, 60, 50)
        dr.line([(g[0] - 10, g[1]), (g[0] + 10, g[1])], fill=col, width=3)
        dr.line([(g[0], g[1] - 10), (g[0], g[1] + 10)], fill=col, width=3)
        for k, sw in (("toeR", False), ("toeL", inf["foot_swing"])):
            q = cam.proj(J[k])
            dr.rectangle([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=(240, 150, 40) if sw else (40, 160, 80))
    return img


def render_top(P, J, inf, size=300):
    img = Image.new("RGB", (size, size), (248, 247, 243))
    dr = ImageDraw.Draw(img)
    c = np.array([size / 2, size / 2 - 10])
    s = 52

    def tp(p):
        return tuple(c + np.array([p[0] - J["pelvis"][0], p[2]]) * s)
    dr.ellipse([c[0] - 2.4 * s, c[1] - 2.4 * s, c[0] + 2.4 * s, c[1] + 2.4 * s], outline=(225, 225, 220))
    for key, col, L, w in (("yaw_pelvis", (200, 70, 60), 1.0, 5), ("yaw_chest", (60, 110, 190), 1.4, 5),
                           ("yaw_weapon", (139, 107, 71), 2.3, 3)):
        a = J["pelvis"]
        b = a + fwd(inf[key]) * L
        dr.line([tp(a), tp(b)], fill=col, width=w)
        q = tp(b)
        dr.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=col)
    for k in ("toeR", "toeL"):
        q = tp(J[k])
        dr.ellipse([q[0] - 5, q[1] - 5, q[0] + 5, q[1] + 5], fill=(40, 160, 80))
    dr.text((8, 6), "nhìn từ trên (camera ở dưới)", font=F_SM, fill=(90, 90, 90))
    y = size - 58
    for lab, col in (("hông", (200, 70, 60)), ("ngực/vai", (60, 110, 190)), ("vũ khí", (139, 107, 71))):
        dr.rectangle([8, y + 3, 20, y + 13], fill=col)
        dr.text((26, y), lab, font=F_SM, fill=(26, 31, 38))
        y += 17
    dr.polygon([(size / 2 - 9, size - 4), (size / 2 + 9, size - 4), (size / 2, size - 18)], fill=(120, 120, 120))
    return img


def timeline(P, M, i, width):
    N, TS = M["N"], M["TS"]
    img = Image.new("RGB", (width, 56), (255, 255, 255))
    dr = ImageDraw.Draw(img)
    x0, x1 = 12, width - 12
    wc = (x1 - x0) / N
    pal = [(225, 225, 220), (235, 225, 190), (250, 214, 165), (180, 210, 240), (215, 200, 240),
           (255, 190, 170), (240, 110, 90), (200, 230, 200), (225, 225, 220), (210, 210, 210)]
    names = [n for _, n in P.tm["phases"]]
    for k, t in enumerate(TS):
        ph = names.index(P.phase_of(t))
        dr.rectangle([x0 + k * wc + 1, 8, x0 + (k + 1) * wc - 1, 30], fill=pal[ph % len(pal)])
        if k in M["hit_frames"] or k == M["sweep_hit"]:
            dr.rectangle([x0 + k * wc + 1, 8, x0 + (k + 1) * wc - 1, 30], outline=(150, 30, 20), width=2)
    dr.rectangle([x0 + i * wc, 4, x0 + (i + 1) * wc, 34], outline=(26, 31, 38), width=3)
    dr.text((x0, 36), f"khung {i:02d}/{N - 1}  ·  {P.phase_of(TS[i])}", font=F_MD, fill=(26, 31, 38))
    dr.text((x1 - 300, 36), "viền đỏ = khung trúng (quét / đâm)", font=F_SM, fill=(150, 30, 20))
    return img


def ref_frames(P):
    r = P.p.get("reference")
    if not r:
        return None
    path = os.path.join(REPO, r["gif"])
    if not os.path.exists(path):
        return None
    im = Image.open(path)
    out = []
    for k in range(im.n_frames):
        im.seek(k)
        out.append(im.convert("RGB").crop(tuple(r["crop"])))
    return out


def ref_index(P, t):
    al = P.p["reference"]["align"]
    xs = [a for a, _ in al]
    ys = [b for _, b in al]
    return int(round(float(np.interp(t, xs, ys))))


# ================================================================== main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("params")
    ap.add_argument("--out")
    a = ap.parse_args()
    P = Proxy(a.params)
    name = os.path.splitext(os.path.basename(a.params))[0]
    asset = os.path.abspath(os.path.join(os.path.dirname(a.params), "..", ".."))
    out = a.out or os.path.join(asset, ".work", "motion_proxy", name)
    os.makedirs(os.path.join(out, "blocks"), exist_ok=True)

    cam = Cam(**P.p.get("camera", {}))
    painter = Painter(P, cam)
    global PAINTER
    PAINTER = painter
    M = compute(P, cam)
    N, TS, F = M["N"], M["TS"], M["F"]
    GW, GH = cam.size
    TW = 300

    frames = []
    for i in range(N):
        J, inf = F[i]
        u, perp, ok = M["support"][i]
        game = render_game(P, cam, painter, M, i)
        ImageDraw.Draw(game).text((10, 8), f"camera game — proxy {P.p.get('name', '')}", font=F_BD,
                                  fill=(26, 31, 38))
        info = Image.new("RGB", (TW, GH - TW), (255, 255, 255))
        di = ImageDraw.Draw(info)
        lines = [f"hông {inf['yaw_pelvis'] % 360:4.0f}°  ngực {inf['yaw_chest'] % 360:4.0f}°",
                 f"vũ khí {inf['yaw_weapon'] % 360:4.0f}°  đầu {inf['yaw_head'] % 360:4.0f}°",
                 f"xoắn ngực–hông {inf['twist']:+4.0f}°",
                 f"trọng tâm {u * 100:3.0f}% về chân trước",
                 "  (trong vùng đỡ)" if ok else "  NGOÀI vùng đỡ!",
                 f"gót kiễng R {inf['heel_lift']['R']:.2f}  L {inf['heel_lift']['L']:.2f}"]
        for k, s in enumerate(lines):
            di.text((10, 8 + k * 21), s, font=F_MD, fill=(200, 50, 40) if "NGOÀI" in s else (26, 31, 38))
        cv = Image.new("RGB", (GW + TW, GH + 56), (255, 255, 255))
        cv.paste(game, (0, 0))
        cv.paste(render_top(P, J, inf, TW), (GW, 0))
        cv.paste(info, (GW, TW))
        cv.paste(timeline(P, M, i, GW + TW), (0, GH))
        frames.append(cv)
    dur = int(1000 / P.fps)
    frames[0].save(os.path.join(out, "anim.gif"), save_all=True, append_images=frames[1:], duration=dur, loop=0)
    frames[0].save(os.path.join(out, "anim_slow.gif"), save_all=True, append_images=frames[1:], duration=300, loop=0)

    # so với tham chiếu (ghép theo pha)
    refs = ref_frames(P)
    if refs:
        RS = 400
        cmp = []
        for i in range(N):
            ri = ref_index(P, TS[i])
            cv = Image.new("RGB", (RS + GW, max(RS, GH) + 30), (255, 255, 255))
            cv.paste(refs[ri].resize((RS, RS), Image.NEAREST), (0, 30))
            cv.paste(render_game(P, cam, painter, M, i), (RS, 30))
            d = ImageDraw.Draw(cv)
            d.text((8, 6), f"tham chiếu khung {ri}", font=F_BD, fill=(26, 31, 38))
            d.text((RS + 8, 6), f"proxy khung {i:02d} · {P.phase_of(TS[i])}", font=F_BD,
                   fill=(170, 30, 20) if (i in M["hit_frames"] or i == M["sweep_hit"]) else (26, 31, 38))
            cmp.append(cv)
        cmp[0].save(os.path.join(out, "compare.gif"), save_all=True, append_images=cmp[1:], duration=200, loop=0)

    # bảng khung
    cols, tw, th = 5, 350, 235
    rows = math.ceil(N / cols)
    sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), (255, 255, 255))
    ds = ImageDraw.Draw(sheet)
    for i in range(N):
        g = render_game(P, cam, painter, M, i).resize((tw, th), Image.LANCZOS)
        x, y = (i % cols) * tw, (i // cols) * (th + 22)
        sheet.paste(g, (x, y + 22))
        hit = i in M["hit_frames"] or i == M["sweep_hit"]
        ds.text((x + 6, y + 3), f"{i:02d} {P.phase_of(TS[i])}", font=F_MD,
                fill=(170, 30, 20) if hit else (26, 31, 38))
    sheet.save(os.path.join(out, "sheet.png"))
    for i in range(N):
        im = Image.new("RGBA", (GW, GH), (255, 255, 255, 0))
        painter.draw(im, *F[i])
        im.save(os.path.join(out, "blocks", f"f{i:02d}.png"))

    write_curves(P, M, out)
    write_metrics(P, M, out)
    write_frames_json(P, cam, painter, M, out)
    print(open(os.path.join(out, "metrics.md"), encoding="utf-8").read().split("## Từng khung")[0])
    print("->", out)


def write_curves(P, M, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    c, N = M["curves"], M["N"]
    hit_set = set(M["hit_frames"]) | {M["sweep_hit"]}
    fig, ax = plt.subplots(4, 1, figsize=(10, 11))
    for k, col, lab in (("yP", "#c8463c", "hông"), ("yC", "#3c6ebe", "ngực/vai"), ("yW", "#8b6b47", "vũ khí")):
        ax[0].plot(c["tt"], c[k], color=col, label=lab)
    for y in (90, 450):
        ax[0].axhline(y, ls=":", color="gray")
    ax[0].set_ylabel("góc xoay (°)")
    ax[0].set_title("Góc xoay theo τ (chưa chèn hitstop); đường chấm = hướng mục tiêu")
    ax[0].legend()
    for k, col, lab in (("vP", "#c8463c", "hông"), ("vC", "#3c6ebe", "ngực/vai"), ("vW", "#8b6b47", "vũ khí")):
        ax[1].plot(c["tt"], c[k], color=col, label=lab)
    ax[1].axhline(0, color="k", lw=0.6)
    for k, col in (("hông", "#c8463c"), ("vai", "#3c6ebe"), ("vũ khí", "#8b6b47")):
        if M["release"][k]:
            ax[1].axvline(M["release"][k], color=col, ls="--", lw=1)
    ax[1].set_ylabel("°/khung")
    ax[1].set_title("Chuỗi động học: nhả gồng (nét đứt) và đỉnh quét theo thứ tự hông → vai → vũ khí")
    ax[1].legend()
    fr = np.arange(N)
    ax[2].plot(fr, [s[0] * 100 for s in M["support"]], "o-", color="#2e8b57", label="% trọng tâm về chân trước")
    ax[2].plot(fr, [M["F"][i][0]["pelvis"][1] * 100 for i in fr], "s-", color="#777", label="độ cao hông (x100)")
    ax[2].set_title("Dồn trọng tâm theo khung xuất (có hitstop)")
    ax[2].legend()
    ax[3].bar(fr, M["tipv"], color=["#d0402c" if i in hit_set else "#8b6b47" for i in fr])
    ax[3].set_ylabel("đv/khung")
    ax[3].set_xlabel(f"khung xuất ({P.fps} fps)")
    ax[3].set_title("Tốc độ mũi vũ khí (đỏ = khung trúng)")
    for a in ax[2:]:
        a.set_xticks(fr)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "curves.png"), dpi=110)


def write_metrics(P, M, out):
    """Mỗi tiêu chí ghi rõ 'đo' (có thể hỏng) hay 'cấu trúc' (đúng do cách dựng, chỉ hỏng khi kênh *_off chống lại)."""
    def chk(ok):
        return "ĐẠT" if ok else "**KHÔNG ĐẠT**"
    N, TS, F = M["N"], M["TS"], M["F"]
    mt = P.p.get("metrics", {})
    H = P.b["height"]
    rel, pk = M["release"], M["peak"]
    rel_ok = all(v is not None for v in rel.values()) and rel["hông"] < rel["vai"] < rel["vũ khí"]
    pk_ok = pk["hông"] < pk["vai"] < pk["vũ khí"]
    reach_max = max(M["reach"])
    sup_bad = [i for i, s in enumerate(M["support"]) if not s[2]]
    u = [s[0] for s in M["support"]]
    rw = P.tm["release_window"]
    coil_fr = [i for i in range(N) if 1 <= TS[i] <= rw[1]]
    coil_u = min(u[i] for i in coil_fr)
    hit0 = M["hit_frames"][0]
    hit_u = u[hit0]
    tipx = M["tipx"]
    rel_frame = min(coil_fr, key=lambda i: tipx[i])
    antic_ok = tipx[rel_frame] < tipx[0] - 0.5
    tv = M["tipv"]
    # khung nạp = khung có thương rút về nhiều nhất (kênh weapon_slide), không chọn theo tốc độ
    cs = mt.get("chamber_search", [P.tm["t_hit"] - 5, P.tm["t_hit"]])
    cand = [i for i in range(N) if cs[0] <= TS[i] < P.tm["t_hit"]]
    chamber = min(cand, key=lambda i: P.ch["weapon_slide"](TS[i]))
    # vận tốc mũi thương VỀ PHÍA MỤC TIÊU (+x) từ khung nạp tới khung trúng: dương và tăng dần
    pre = [tipx[i] - tipx[i - 1] for i in range(chamber + 1, hit0 + 1)]
    hit_ok = all(x > 0 for x in pre) and all(b > a for a, b in zip(pre, pre[1:]))
    tw_lim = P.c["max_twist"]
    tw_ok = M["twist_raw_max"] <= tw_lim
    cross = [i for i, c in enumerate(M["cross"]) if c]
    shift_lim = mt.get("max_weapon_shift_pct", 5) / 100 * H
    shift_max = max(M["shift"])
    shift_bad = [i for i, s in enumerate(M["shift"]) if s > shift_lim]
    wy = [F[i][1]["yaw_weapon"] % 360 for i in range(N)]
    far = [i for i in range(N) if 135 <= wy[i] <= 225]
    near = [i for i in range(N) if wy[i] >= 315 or wy[i] <= 45]
    far_bad = [i for i in far if M["side"][i] != "back"]
    near_bad = [i for i in near if M["side"][i] != "front"]
    occ_ok = bool(far) and not far_bad and not near_bad
    sweep_err = abs(((wy[M["sweep_hit"]] - 90) + 180) % 360 - 180)
    sweep_ok = sweep_err <= mt.get("sweep_hit_tol_deg", 20)
    rows = [
        ("Nhả gồng theo thứ tự hông → vai → vũ khí", "cấu trúc",
         "đổi chiều tại τ = " + " / ".join(f"{v:.2f}" if v is not None else "—" for v in rel.values()), rel_ok),
        ("Đỉnh vận tốc quét theo thứ tự", "cấu trúc",
         "τ = " + " / ".join(f"{v:.2f}" for v in pk.values()) + " (đỉnh "
         + "/".join(f"{v:.0f}" for v in M["peak_v"].values()) + " °/khung)", pk_ok),
        (f"Xoắn ngực–hông tự nhiên ≤ {tw_lim}° (bộ chặn không phải can thiệp)", "đo",
         f"xoắn thô tối đa {M['twist_raw_max']:.0f}°", tw_ok),
        ("Chân không bắt chéo (thứ tự hai chân theo trục hông)", "đo",
         f"khung bắt chéo: {cross or 'không'}", not cross),
        ("Tay, chân trong tầm (gót đã kiễng tối đa)", "đo",
         f"vượt tối đa {reach_max:.3f} đv ({reach_max / H * 100:.1f}% chiều cao)", reach_max / H < 0.01),
        (f"Tay với tới đường tay đã đặt (dời thương ≤ {shift_lim:.2f} đv)", "đo",
         f"dời tối đa {shift_max:.2f} đv; khung vượt: {shift_bad or 'không'}", not shift_bad),
        ("Trọng tâm trong vùng đỡ (một chân: điểm bắt nằm giữa chân trụ và điểm đặt)", "đo",
         f"khung ngoài vùng: {sup_bad or 'không'}", not sup_bad),
        ("Gồng dồn về chân sau, trúng dồn về chân trước", "đo",
         f"gồng {coil_u * 100:.0f}% → trúng {hit_u * 100:.0f}%",
         coil_u * 100 < mt.get("coil_frames_max_front_pct", 45) and hit_u * 100 > mt.get("hit_min_front_pct", 60)),
        ("Gồng ra xa mục tiêu trước khi nhả", "đo",
         f"mũi x: {tipx[0]:.2f} → {tipx[rel_frame]:.2f} (khung {rel_frame})", antic_ok),
        ("Đâm: từ khung nạp, mũi tiến về mục tiêu và tăng tốc tới khung trúng", "đo",
         f"nạp ở khung {chamber}; dịch về mục tiêu " + ", ".join(f"{x:+.2f}" for x in pre) + " đv/khung", hit_ok),
        ("Khung trúng quét gần hướng mục tiêu", "đo",
         f"khung {M['sweep_hit']}: vũ khí {wy[M['sweep_hit']]:.0f}° (lệch {sweep_err:.0f}°)", sweep_ok),
        ("Nửa xa (vũ khí 135–225°) vẽ sau thân, nửa gần vẽ trước thân", "đo",
         f"nửa xa {far or 'không có'}, sai {far_bad or 'không'}; nửa gần sai {near_bad or 'không'}", occ_ok),
        ("Mũi chân khoá khi chạm đất; hitstop giữ nguyên tư thế", "cấu trúc",
         f"hitstop {len(M['hit_frames'])} khung {M['hit_frames']}", True),
    ]
    n_ok = sum(1 for r in rows if r[3] and r[1] == "đo")
    n_meas = sum(1 for r in rows if r[1] == "đo")
    L = [f"# Proxy {P.p.get('name', '')}", "",
         f"{N} khung ở {P.fps} fps ({N / P.fps:.2f} s). Khung trúng quét: {M['sweep_hit']}. "
         f"Khung trúng đâm (giữ hitstop): {M['hit_frames']}.", "",
         f"**Tiêu chí đo: {n_ok}/{n_meas} đạt.** Tiêu chí 'cấu trúc' đúng do cách dựng bộ xương, chỉ để nhắc,"
         " không chứng minh gì thêm.", "",
         "| # | Tiêu chí | Loại | Số đo | Kết quả |", "|---|---|---|---|---|"]
    for k, (name, kind, meas, ok) in enumerate(rows, 1):
        L.append(f"| {k} | {name} | {kind} | {meas} | {chk(ok)} |")
    L += ["", "## Từng khung", "",
          "| khung | τ | pha | ref | hông | ngực | vũ khí | đầu | hướng thân | xoắn | % chân trước | gót R/L | lưỡi | chéo chân |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    has_ref = bool(P.p.get("reference"))
    for i, (J, inf) in enumerate(F):
        L.append(f"| {i:02d} | {TS[i]:.0f} | {P.phase_of(TS[i])} | {ref_index(P, TS[i]) if has_ref else ''} | "
                 f"{inf['yaw_pelvis'] % 360:.0f} | {inf['yaw_chest'] % 360:.0f} | {wy[i]:.0f} | "
                 f"{inf['yaw_head'] % 360:.0f} | {view_name(inf['yaw_chest'])} | {inf['twist']:+.0f} | "
                 f"{u[i] * 100:.0f} | {inf['heel_lift']['R']:.2f}/{inf['heel_lift']['L']:.2f} | "
                 f"{'trước' if M['side'][i] == 'front' else 'sau'} | {'có' if M['cross'][i] else ''} |")
    with open(os.path.join(out, "metrics.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def write_frames_json(P, cam, painter, M, out):
    data = dict(fps=P.fps, units_px=cam.s, origin_px=list(cam.o), camera_pitch_deg=math.degrees(cam.pitch),
                hit_frames=M["hit_frames"], sweep_hit_frame=M["sweep_hit"], frames=[])
    for i, (J, inf) in enumerate(M["F"]):
        tr = tip_trail(P, M["TS"][i])
        data["frames"].append(dict(
            i=i, tau=M["TS"][i], phase=P.phase_of(M["TS"][i]),
            yaw={k: inf["yaw_" + k] % 360 for k in ("pelvis", "chest", "weapon", "head")},
            view={"torso": view_name(inf["yaw_chest"]), "head": view_name(inf["yaw_head"]),
                  "hips": view_name(inf["yaw_pelvis"])},
            weapon_pitch=inf["weapon_pitch"],
            joints2d={k: [round(float(v), 1) for v in cam.proj(p)] for k, p in J.items()},
            depth={k: round(float(cam.depth(p)), 3) for k, p in J.items()},
            layer_back_to_front=[p[0] for p in sorted(painter.parts(J, inf), key=lambda p: p[1])],
            com_front_pct=round(M["support"][i][0] * 100, 1),
            heel_lift=inf["heel_lift"],
            tip_trail2d=[[round(float(v), 1) for v in cam.proj(q)] for q in tr],
            tip_trail_near=[bool(cam.depth(q) > cam.depth(J["pelvis"])) for q in tr]))
    with open(os.path.join(out, "frames.json"), "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)

    # weapon_track.json: cùng định dạng scripts/puppet.py track (milestone-01), đọc được bởi lib-fx --track
    Hpx = P.b["height"] * cam.s

    def Hc(p):
        q = cam.proj(p)
        return [round(float((q[0] - cam.o[0]) / Hpx), 4), round(float((cam.o[1] - q[1]) / Hpx), 4)]
    samples, prev = [], None
    for i, (J, inf) in enumerate(M["F"]):
        tip = np.array(Hc(J["tip"]))
        sp = 0.0 if prev is None else float(np.hypot(*(tip - prev)))
        prev = tip
        samples.append({"frame": i + 1, "ms": round(i * 1000 / P.fps), "visible": True, "used": True,
                        "estimated": False, "side": M["side"][i], "root": Hc(J["blade_root"]), "tip": tip.tolist(),
                        "root_px": [round(float(v), 1) for v in cam.proj(J["blade_root"])],
                        "tip_px": [round(float(v), 1) for v in cam.proj(J["tip"])],
                        "note": P.phase_of(M["TS"][i]), "tip_speed": round(sp, 4)})
    track = {"state": P.p.get("name", ""), "take": "motion_proxy", "fps": P.fps, "frames": M["N"],
             "frame_ms": round(1000 / P.fps),
             "units": "H, origin = feet pivot, x forward (right), y up; time ms from frame 1; tip_speed in H per frame",
             "body_height_px": Hpx, "coordinate_H_px": Hpx, "subframes": 1,
             "hit_frame": M["hit_frames"][0] + 1, "sweep_hit_frame": M["sweep_hit"] + 1,
             "marked_by": "motion_proxy skeleton (root = blade root, side = blade drawn in front of / behind the torso)",
             "samples": samples}
    with open(os.path.join(out, "weapon_track.json"), "w", encoding="utf-8") as fh:
        json.dump(track, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
