"""Dựng proxy 3D của một skill cận chiến: hình, chỉ số vật lý, so với tham chiếu, dữ liệu cho rig.

    python scripts/motion_proxy/build.py out/heroes/<id>/source/rig/proxy_<skill>.json [--out DIR]

Mặc định ghi vào <asset>/.work/motion_proxy/<tên file>/ (git bỏ qua):
  clean.gif, clean_slow.gif hình đẹp: nhân vật + vệt chém, nền xám như ref (để xem); clean/fNN.png từng khung
  anim.gif, anim_slow.gif   hình đo đạc: + trọng tâm, mũi chân, nhìn từ trên, thanh nhịp
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
from paint import Painter, render_clean, skirt_points, convex_hull  # noqa: E402

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
    def __init__(self, pitch_deg=15, scale=100, size=(780, 480), origin=(300, 440)):
        self.pitch = math.radians(pitch_deg)
        self.s = scale
        self.size = size
        self.o = origin

    def proj(self, p):
        return np.array([self.o[0] + p[0] * self.s,
                         self.o[1] - (p[1] * math.cos(self.pitch) - p[2] * math.sin(self.pitch)) * self.s])

    def depth(self, p):
        return p[2] * math.cos(self.pitch) + p[1] * math.sin(self.pitch)


# ================================================================== chỉ số
def support(P, J, com_p, inf, com_v=None):
    """Trọng tâm so với vùng đỡ. 0 = chân sau, 1 = chân trước.
    Hai chân chạm đất: trọng tâm chiếu xuống phải nằm giữa hai mũi chân.
    Một chân đang nhấc: dùng điểm bắt (capture point = trọng tâm + vận tốc * sqrt(h/g)); điểm này phải nằm
    giữa chân trụ và điểm chân sắp đặt xuống, tức bước chân kịp đỡ cú ngã có kiểm soát."""
    b = J["toeR"]
    f = J["toeL"]
    c = com_p.copy()
    sw = inf.get("swing", {"L": inf["foot_swing"], "R": False})
    if P.tracks:
        # vết chân từ nguồn: chân sau / chân trước xác định theo hướng mục tiêu (+x), không theo trái/phải
        if sw["R"] != sw["L"]:
            b = J["toeL"] if sw["R"] else J["toeR"]
            f = inf["swing_land"].copy()
        else:
            b, f = (J["toeR"], J["toeL"]) if J["toeR"][0] <= J["toeL"][0] else (J["toeL"], J["toeR"])
        if sw["R"] and sw["L"]:
            return 0.5, 0.0, True
        seg = f - b
        seg[1] = 0
        if np.dot(seg, seg) < 1e-6:
            return 0.5, 0.0, True
        cc = c - b
        if inf["foot_swing"] and com_v is not None:
            m_per_u = P.b.get("real_height_m", 1.8) / P.b["height"]
            cc = cc + com_v * math.sqrt(max(com_p[1], 1e-3) / (9.81 / m_per_u))
        cc[1] = 0
        u = float(np.dot(cc, seg) / np.dot(seg, seg))
        perp = float(np.linalg.norm(cc - seg * u))
        return u, perp, (-0.05 <= u <= 1.05) and perp < 0.30
    if sw["R"] and sw["L"]:
        return 0.5, 0.0, True            # nhảy: cả hai chân trên không, không xét vùng đỡ
    if sw["R"]:
        b, f = J["toeL"], inf["swing_land"].copy()   # chân trụ là chân trái
    if inf["foot_swing"]:
        f = inf["swing_land"].copy() if not sw["R"] else f
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


def slash_trail(P, t, span=0.8, step=0.08, inward=1.1, min_path=0.9):
    """Mẫu (mũi, điểm trong) cho vệt chém, chỉ trong timing.slash_windows; rỗng khi mũi đi chậm."""
    wins = P.tm.get("slash_windows")
    if wins and not any(a <= t <= b for a, b in wins):
        return None
    lo = max([a for a, b in wins if a <= t <= b] + [0]) if wins else 0
    ts = np.arange(max(lo, t - span), t + 1e-9, step)
    if len(ts) < 2:
        return None
    out = []
    for x in ts:
        J = P.pose(x)[0]
        d = (J["tip"] - J["butt"]) / np.linalg.norm(J["tip"] - J["butt"])
        out.append((J["tip"], J["tip"] - d * inward))
    path = sum(np.linalg.norm(out[k + 1][0] - out[k][0]) for k in range(len(out) - 1))
    return out if path >= min_path else None


def tip_trail(P, t, span=1.0, step=0.125):
    return [P.pose(x)[0]["tip"] for x in np.arange(max(0, t - span), t + 1e-9, step)]


PAINTER = None


def seg_cross(a0, a1, b0, b1):
    d1, d2 = a1 - a0, b1 - b0
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-9:
        return None
    t = ((b0[0] - a0[0]) * d2[1] - (b0[1] - a0[1]) * d2[0]) / den
    u = ((b0[0] - a0[0]) * d1[1] - (b0[1] - a0[1]) * d1[0]) / den
    return a0 + d1 * t if 0 <= t <= 1 and 0 <= u <= 1 else None


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
        crossed = float(np.dot(J["ankleR"] - J["ankleL"], rP)) < 0
        exposed = False
        if crossed:
            # chỗ hai chân cắt nhau trên ảnh có nằm ngoài vạt áo và thân không
            legR = [cam.proj(J[k]) for k in ("hipR", "kneeR", "ankleR")]
            legL = [cam.proj(J[k]) for k in ("hipL", "kneeL", "ankleL")]
            top3, hem3 = skirt_points(P.b, J, inf)
            cover = MplPath(convex_hull([cam.proj(q) for q in top3 + hem3]))
            for a0, a1 in zip(legR, legR[1:]):
                for b0, b1 in zip(legL, legL[1:]):
                    x = seg_cross(a0, a1, b0, b1)
                    if x is not None and not cover.contains_point(x):
                        exposed = True
        cross.append((crossed, exposed))
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


def render_game(P, cam, M, i):
    """Khung đo đạc: khung đẹp + trọng tâm, mũi chân khoá, mốc mục tiêu."""
    J, inf = M["F"][i]
    img = M["clean"][i].copy()
    dr = ImageDraw.Draw(img)
    cp = P.com(J)
    g = cam.proj(np.array([cp[0], 0, cp[2]]))
    tx = cam.proj(np.array([P.p.get("target_x", 4.2), 0, 0]))
    dr.line([(tx[0], tx[1] - 160), (tx[0], tx[1])], fill=(200, 120, 110), width=3)
    dr.text((tx[0] - 28, tx[1] + 6), "mục tiêu", font=F_SM, fill=(220, 160, 150))
    ok = M["support"][i][2]
    col = (90, 210, 120) if ok else (240, 80, 70)
    dr.line([(g[0] - 10, g[1]), (g[0] + 10, g[1])], fill=col, width=3)
    dr.line([(g[0], g[1] - 10), (g[0], g[1] + 10)], fill=col, width=3)
    for k, sw in (("toeR", False), ("toeL", inf["foot_swing"])):
        q = cam.proj(J[k])
        dr.rectangle([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=(240, 150, 40) if sw else (90, 210, 120))
    return img


def render_block(P, cam, J, inf, ss=3):
    """Khung khối nền trong, không vệt chém, không bóng: khung mẫu cho mô hình ảnh."""
    big = Cam(pitch_deg=math.degrees(cam.pitch), scale=cam.s * ss, size=(cam.size[0] * ss, cam.size[1] * ss),
              origin=(cam.o[0] * ss, cam.o[1] * ss))
    im = Image.new("RGBA", big.size, (0, 0, 0, 0))
    Painter(P, big).draw(im, J, inf)
    return im.resize(cam.size, Image.LANCZOS)


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
    M["clean"] = [render_clean(P, cam, J, inf, slash_trail(P, TS[i])) for i, (J, inf) in enumerate(F)]
    dur = int(1000 / P.fps)
    clean = M["clean"]
    os.makedirs(os.path.join(out, "clean"), exist_ok=True)
    for i, im in enumerate(clean):
        im.save(os.path.join(out, "clean", f"f{i:02d}.png"))
    clean[0].save(os.path.join(out, "clean.gif"), save_all=True, append_images=clean[1:], duration=dur, loop=0)
    clean[0].save(os.path.join(out, "clean_slow.gif"), save_all=True, append_images=clean[1:], duration=250, loop=0)
    TW = 300

    frames = []
    for i in range(N):
        J, inf = F[i]
        u, perp, ok = M["support"][i]
        game = render_game(P, cam, M, i)
        ImageDraw.Draw(game).text((10, 8), f"proxy {P.p.get('name', '')}", font=F_BD, fill=(235, 235, 235))
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
    frames[0].save(os.path.join(out, "anim.gif"), save_all=True, append_images=frames[1:], duration=dur, loop=0)
    frames[0].save(os.path.join(out, "anim_slow.gif"), save_all=True, append_images=frames[1:], duration=300, loop=0)

    # so với tham chiếu (ghép theo pha)
    refs = ref_frames(P)
    if refs:
        RS = 400
        cmp = []
        for i in range(N):
            ri = ref_index(P, TS[i])
            cv = Image.new("RGB", (RS + GW, max(RS, GH) + 30), (40, 41, 44))
            cv.paste(refs[ri].resize((RS, RS), Image.NEAREST), (0, 30))
            cv.paste(clean[i], (RS, 30 + (RS - GH) // 2 if RS > GH else 30))
            d = ImageDraw.Draw(cv)
            d.text((8, 6), f"tham chiếu khung {ri}", font=F_BD, fill=(230, 230, 230))
            d.text((RS + 8, 6), f"proxy khung {i:02d} · {P.phase_of(TS[i])}", font=F_BD,
                   fill=(255, 120, 100) if (i in M["hit_frames"] or i == M["sweep_hit"]) else (230, 230, 230))
            cmp.append(cv)
        cmp[0].save(os.path.join(out, "compare.gif"), save_all=True, append_images=cmp[1:], duration=200, loop=0)

    # bảng khung
    cols, tw, th = 5, 350, 235
    rows = math.ceil(N / cols)
    sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), (255, 255, 255))
    ds = ImageDraw.Draw(sheet)
    for i in range(N):
        g = clean[i].resize((tw, th), Image.LANCZOS)
        x, y = (i % cols) * tw, (i // cols) * (th + 22)
        sheet.paste(g, (x, y + 22))
        hit = i in M["hit_frames"] or i == M["sweep_hit"]
        ds.text((x + 6, y + 3), f"{i:02d} {P.phase_of(TS[i])}", font=F_MD,
                fill=(170, 30, 20) if hit else (26, 31, 38))
    sheet.save(os.path.join(out, "sheet.png"))
    for i in range(N):
        im = render_block(P, cam, *F[i])
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
    chamber = min(cand, key=lambda i: P.ch["weapon_slide"](TS[i])) if cand else hit0
    # vận tốc mũi thương VỀ PHÍA MỤC TIÊU (+x) từ khung nạp tới khung trúng: dương và tăng dần
    pre = [tipx[i] - tipx[i - 1] for i in range(chamber + 1, hit0 + 1)]
    hit_ok = all(x > 0 for x in pre) and all(b > a for a, b in zip(pre, pre[1:]))
    tw_lim = P.c["max_twist"]
    tw_ok = M["twist_raw_max"] <= tw_lim
    crossed = [i for i, c in enumerate(M["cross"]) if c[0]]
    cross = [i for i, c in enumerate(M["cross"]) if c[1]]
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
        ("Chân bắt chéo khi xoay trên mũi chân phải được vạt áo / thân che", "đo",
         f"khung bắt chéo: {crossed or 'không'}; lộ ra: {cross or 'không'}", not cross),
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
    keys = ["order", "order", "twist", "cross", "reach", "shift", "support", "weight", "antic", "thrust",
            "sweep_hit", "far_half", "struct"]
    enabled = P.p.get("checks")
    if enabled:
        rows = [r for r, k in zip(rows, keys) if k in enabled or (k in ("order", "struct") and P.c.get("lag_chest", 0) > 0)]
    n_ok = sum(1 for r in rows if r[3] and r[1] == "đo")
    n_meas = sum(1 for r in rows if r[1] == "đo")
    L = [f"# Proxy {P.p.get('name', '')}", "",
         f"{N} khung ở {P.fps} fps ({N / P.fps:.2f} s). Khung trúng quét: {M['sweep_hit']}. "
         f"Khung trúng (giữ hitstop): {M['hit_frames']}.", "",
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
                 f"{'trước' if M['side'][i] == 'front' else 'sau'} | {('lộ' if M['cross'][i][1] else 'che') if M['cross'][i][0] else ''} |")
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
