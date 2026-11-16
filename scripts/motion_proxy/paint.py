"""Vẽ proxy theo phong cách chunky: chi thuôn, hai tông sáng tối, viền dày, vẽ siêu mẫu rồi thu nhỏ.

Hợp đồng: Painter(proxy, cam).parts(J, inf) -> [(tên, độ sâu, hàm vẽ(dr))]; vẽ từ xa tới gần.
Tên 'torso', 'skirt', 'blade' được build.py dùng để đo, đừng đổi.
Màu lấy từ 'palette' trong file thông số của nhân vật.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

from skeleton import fwd, right, UP


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mul(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def chaikin(pts, it=2, closed=True):
    p = [np.asarray(q, float) for q in pts]
    for _ in range(it):
        out = []
        n = len(p)
        rng = range(n) if closed else range(n - 1)
        for i in rng:
            a, b = p[i], p[(i + 1) % n]
            out += [a * 0.75 + b * 0.25, a * 0.25 + b * 0.75]
        if not closed:
            out = [p[0]] + out + [p[-1]]
        p = out
    return p


class Painter:
    LIGHT = np.array([-0.45, -0.6])          # ánh sáng từ trên-trái (toạ độ ảnh, y xuống)

    def __init__(self, proxy, cam):
        self.px, self.cam = proxy, cam
        self.pal = {k: hexc(v) for k, v in proxy.p["palette"].items()}
        self.ink = self.pal["ink"]
        self.ow = max(2.0, 0.04 * cam.s)

    # ------------------------------------------------------------ nguyên tố
    def _taper(self, dr, a, b, ra, rb, col, caps=(True, True), ext=0.0):
        d = b - a
        L = np.linalg.norm(d)
        if L > 1e-6:
            u = d / L
            n = np.array([-u[1], u[0]])
            a2, b2 = a - u * ext, b + u * ext
            dr.polygon([tuple(a2 + n * ra), tuple(b2 + n * rb), tuple(b2 - n * rb), tuple(a2 - n * ra)], fill=col)
        for q, r, c in ((a, ra, caps[0]), (b, rb, caps[1])):
            if c:
                dr.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=col)

    def limb(self, dr, a, b, ra, rb, col, shade=0.72, caps=(True, True)):
        """Chi thuôn: viền mực, nền tối, khối sáng lệch về phía ánh sáng.
        caps=False ở một đầu: đoạn nối tiếp (cán thương chia đoạn) không có vạch ngang ở chỗ nối."""
        o = self.ow
        ext = 0.0 if all(caps) else 0.6
        self._taper(dr, a, b, ra + o, rb + o, self.ink, caps, ext)
        self._taper(dr, a, b, ra, rb, mul(col, shade), caps, ext + o * 0.0)
        off = self.LIGHT * min(ra, rb) * 0.28
        self._taper(dr, a + off, b + off, ra * 0.74, rb * 0.74, col, caps, ext)

    def ball(self, dr, q, r, col, shade=0.72, rx=None):
        rx = rx or r
        o = self.ow
        dr.ellipse([q[0] - rx - o, q[1] - r - o, q[0] + rx + o, q[1] + r + o], fill=self.ink)
        dr.ellipse([q[0] - rx, q[1] - r, q[0] + rx, q[1] + r], fill=mul(col, shade))
        c = q + self.LIGHT * r * 0.22
        dr.ellipse([c[0] - rx * 0.76, c[1] - r * 0.76, c[0] + rx * 0.76, c[1] + r * 0.76], fill=col)

    def shape(self, dr, pts, col, shade=0.72, it=2, inner=0.84):
        """Khối đa giác bo tròn: viền, nền tối, lõi sáng co về tâm và lệch về phía sáng."""
        p = chaikin(pts, it)
        dr.polygon([tuple(q) for q in p], fill=mul(col, shade), outline=self.ink, width=int(self.ow))
        c = np.mean(p, axis=0)
        span = np.max(np.linalg.norm(np.array(p) - c, axis=1))
        off = self.LIGHT * span * 0.07
        dr.polygon([tuple(c + (q - c) * inner + off) for q in p], fill=col)

    def flat(self, dr, pts, col, it=1, outline=True):
        p = chaikin(pts, it) if it else [np.asarray(q, float) for q in pts]
        dr.polygon([tuple(q) for q in p], fill=col, outline=self.ink if outline else None,
                   width=int(self.ow * 0.8) if outline else 0)

    # ------------------------------------------------------------ phần thân
    def parts(self, J, inf, trail=None):
        P, cam, b, pal = self.px, self.cam, self.px.b, self.pal
        pr, s = cam.proj, cam.s
        out = []

        def add(name, pts3d, fn, bias=0.0):
            out.append((name, float(np.mean([cam.depth(q) for q in pts3d])) + bias, fn))

        C, Pv, H = inf["yaw_chest"], inf["yaw_pelvis"], inf["yaw_head"]
        rC, rP, fC, fP = right(C), right(Pv), fwd(C), fwd(Pv)
        ch, pe = J["chest"], J["pelvis"]

        # ---- chân: quần da, ủng, ốp gối vàng có trăng khuyết, mũi ủng vàng
        for sd, sh in (("R", 1.0), ("L", 0.86)):
            hip, kn, an, he, to = (J["hip" + sd], J["knee" + sd], J["ankle" + sd], J["heel" + sd], J["toe" + sd])
            pants, boot = mul(pal["leather"], sh * 1.25), mul(pal["shaft"], sh)
            add("thigh" + sd, (hip, kn), lambda dr, hip=hip, kn=kn, c=pants:
                self.limb(dr, pr(hip), pr(kn), 0.19 * s, 0.15 * s, c))
            add("shin" + sd, (kn, an), lambda dr, kn=kn, an=an, c=boot:
                self.limb(dr, pr(kn), pr(an), 0.16 * s, 0.15 * s, c))

            def foot(dr, he=he, to=to, c=boot):
                self.limb(dr, pr(he), pr(to), 0.12 * s, 0.13 * s, c)
                self.ball(dr, pr(to), 0.085 * s, pal["gold"])
            add("foot" + sd, (he, to), foot)

            def knee(dr, kn=kn):
                q = pr(kn)
                self.ball(dr, q, 0.12 * s, pal["gold"])
                c2 = q + np.array([0.035, -0.02]) * s
                dr.ellipse([c2[0] - 0.065 * s, c2[1] - 0.065 * s, c2[0] + 0.065 * s, c2[1] + 0.065 * s],
                           fill=pal["armor_dark"])
            add("knee" + sd, (kn,), knee, bias=0.05)

        # ---- vạt áo: nón vải quanh hông, xoè theo tốc độ xoay (che chân khi quay)
        flare = min(1.0, abs(inf.get("spin_rate", 0.0)) / 90.0)
        waist = pe + UP * 0.46

        top3, hem3 = skirt_points(b, J, inf)

        def skirt(dr):
            pts = [pr(q) for q in top3 + hem3]
            hull = convex_hull(pts)
            self.shape(dr, hull, pal["armor"], it=1, inner=0.8)
            # viền ngà rách ở mép
            hem2 = [pr(q) for q in hem3]
            lowest = sorted(range(len(hem2)), key=lambda i: -hem2[i][1])[:13]
            lowest.sort(key=lambda i: hem2[i][0])
            for i in lowest:
                q = hem2[i]
                w = 0.07 * s
                if i % 2:
                    dr.polygon([(q[0] - w, q[1] - 0.12 * s), (q[0] + w, q[1] - 0.12 * s), (q[0], q[1])],
                               fill=pal["ivory"], outline=self.ink)
            if fP[2] > -0.2:   # dải đỏ trước bụng
                a3 = waist + fP * b["waist_half"]
                q0, q1 = pr(a3 + rP * 0.08), pr(a3 - rP * 0.08)
                q2 = pr(pe + fP * (b["waist_half"] + 0.1 + 0.2 * flare) - UP * 0.42 - fP * 0.0)
                self.flat(dr, [q0, q1, q2 + np.array([-0.05 * s, 0]), q2 + np.array([0.05 * s, 0])], pal["red"], it=0)
        # ---- giáp ngực
        sp = b["shoulder_pad_half"]

        def torso(dr):
            pts = [ch + UP * 0.12 + rC * sp * 0.78, ch + UP * 0.16, ch + UP * 0.12 - rC * sp * 0.78,
                   ch - UP * 0.30 - rC * sp * 0.90, waist - rP * b["waist_half"] * 1.02,
                   waist + rP * b["waist_half"] * 1.02, ch - UP * 0.30 + rC * sp * 0.90]
            pts = [q + fC * 0.05 for q in pts]
            face_cam = fC[2]
            col = pal["armor"] if face_cam > -0.2 else mul(pal["armor"], 0.85)
            self.shape(dr, [pr(q) for q in pts], col, it=2)
            # thắt lưng + khoá vàng
            bl = [waist + rP * b["waist_half"] * 1.05 + UP * 0.07, waist - rP * b["waist_half"] * 1.05 + UP * 0.07,
                  waist - rP * b["waist_half"] * 1.05 - UP * 0.07, waist + rP * b["waist_half"] * 1.05 - UP * 0.07]
            bl = [q + fP * 0.08 for q in bl]
            self.flat(dr, [pr(q) for q in bl], pal["leather"], it=0)
            if fP[2] > -0.1:
                bq = pr(waist + fP * (b["waist_half"] * 0.9))
                w = 0.11 * s * max(0.3, fP[2])
                dr.rectangle([bq[0] - w, bq[1] - 0.075 * s, bq[0] + w, bq[1] + 0.075 * s],
                             fill=pal["gold"], outline=self.ink, width=int(self.ow * 0.7))
            if face_cam > 0.1:                      # chim vàng trước ngực (toạ độ cục bộ rC, UP)
                bird = [(-0.36, 0.14), (-0.12, -0.02), (-0.05, -0.22), (0.05, -0.22), (0.12, -0.02), (0.36, 0.14),
                        (0.14, 0.06), (0.05, 0.16), (0.0, 0.26), (-0.05, 0.16), (-0.14, 0.06)]
                c0 = ch - UP * 0.30 + fC * 0.38
                q = [pr(c0 - rC * x + UP * y) for x, y in bird]
                self.flat(dr, q, pal["gold"], it=1)
                hq = pr(c0 + UP * 0.30)
                r = 0.05 * s
                dr.ellipse([hq[0] - r, hq[1] - r, hq[0] + r, hq[1] + r], fill=pal["gold"], outline=self.ink)
            # cổ áo vàng
            nq = [pr(ch + UP * 0.14 + rC * 0.2 + fC * 0.1), pr(ch + UP * 0.2 + fC * 0.18),
                  pr(ch + UP * 0.14 - rC * 0.2 + fC * 0.1), pr(ch + UP * 0.06 + fC * 0.2)]
            self.flat(dr, nq, pal["gold"], it=1)
        tdepth = cam.depth(ch - UP * 0.5)
        out.append(("skirt", tdepth - 0.004, skirt))
        out.append(("torso", tdepth, torso))

        # ---- giáp vai vòm + cánh hạc (vai trái nhân vật)
        for sd, k in (("R", "shR"), ("L", "shL")):
            q3 = J[k] + UP * 0.05

            def pad(dr, q3=q3, k=k):
                q = pr(q3)
                r = 0.27 * s
                self.ball(dr, q + np.array([0, 0.05 * s]), r * 0.82, pal["gold"], rx=r)
                self.ball(dr, q - np.array([0, 0.03 * s]), r * 0.66, pal["armor"], rx=r * 0.84)
            add("pad" + sd, (q3,), pad, bias=0.06)
        wing_root = J["shL"] + UP * 0.08

        def wing(dr):
            out_dir = -rC
            for k, (ang, ln, wd) in enumerate(((84, 1.00, 0.17), (64, 0.92, 0.17), (45, 0.82, 0.16), (27, 0.70, 0.15))):
                a = math.radians(ang)
                axis = UP * math.sin(a) + out_dir * math.cos(a)
                side = UP * math.cos(a) - out_dir * math.sin(a)
                root = wing_root + out_dir * (0.05 * k) - fC * 0.06
                q = [root + side * wd * 0.5, root + axis * ln * 0.55 + side * wd, root + axis * ln,
                     root + axis * ln * 0.5 - side * wd * 0.8, root - side * wd * 0.4]
                self.shape(dr, [pr(p) for p in q], pal["ivory"], shade=0.82, it=2)
                g = [root + side * wd * 0.5, root + axis * 0.18 + side * wd * 0.6,
                     root + axis * 0.18 - side * wd * 0.4, root - side * wd * 0.4]
                self.flat(dr, [pr(p) for p in g], pal["gold"], it=0)
        add("wing", (wing_root - fC * 0.15,), wing, bias=-0.02)

        # ---- tay: bắp tay trần, giáp cẳng tay có đai vàng, nắm đấm to
        for sd, sh in (("R", 1.0), ("L", 0.88)):
            S_, E_, Hd = J["sh" + sd], J["elbow" + sd], J["hand" + sd]
            skin, arm = mul(pal["skin"], sh), mul(pal["armor"], sh)
            add("upperArm" + sd, (S_, E_), lambda dr, S_=S_, E_=E_, c=skin:
                self.limb(dr, pr(S_), pr(E_), 0.18 * s, 0.15 * s, c))

            def forearm(dr, E_=E_, Hd=Hd, c=arm):
                a, h = pr(E_), pr(Hd)
                self.limb(dr, a, h, 0.17 * s, 0.17 * s, c)
                for t, w in ((0.15, 0.19), (0.8, 0.2)):
                    m = a + (h - a) * t
                    d = (h - a) / max(np.linalg.norm(h - a), 1e-6)
                    self.limb(dr, m - d * 0.035 * s, m + d * 0.035 * s, w * s, w * s, pal["gold"])
            add("forearm" + sd, (E_, Hd), forearm)

            def fist(dr, Hd=Hd, c=skin):
                q = pr(Hd)
                self.ball(dr, q, b["fist_r"] * s, c)
                dr.arc([q[0] - 0.12 * s, q[1] - 0.05 * s, q[0] + 0.12 * s, q[1] + 0.12 * s], 200, 340,
                       fill=self.ink, width=int(self.ow * 0.6))
            add("fist" + sd, (Hd,), fist, bias=0.03)

        # ---- đầu: da, búi tóc dây đỏ, mày, mắt phát sáng, râu một mảng
        hd = J["head"]
        R = b["head_r"]

        def head(dr):
            fH, rH = fwd(H), right(H)
            bun = pr(hd + UP * (R + 0.09) - fH * 0.10)
            self.ball(dr, bun, 0.14 * s, pal["hair"], shade=0.8)
            band = pr(hd + UP * (R - 0.02) - fH * 0.08)
            dr.ellipse([band[0] - 0.09 * s, band[1] - 0.045 * s, band[0] + 0.09 * s, band[1] + 0.045 * s],
                       fill=pal["red"], outline=self.ink)
            q = pr(hd)
            self.ball(dr, q, R * s, pal["skin"], rx=R * s * 0.94)

            def sph(az, el, rr=1.0):
                d = (fH * math.cos(az) + rH * math.sin(az)) * math.cos(el) + UP * math.sin(el)
                return hd + d * R * rr

            def vis(az, el):
                d = (fH * math.cos(az) + rH * math.sin(az)) * math.cos(el) + UP * math.sin(el)
                return d[2] * math.cos(cam.pitch) + d[1] * math.sin(cam.pitch) > -0.05
            # tóc phủ đỉnh và gáy
            cap = [sph(math.radians(a), math.radians(25)) for a in range(-180, 181, 20)]
            cap_pts = [pr(p) for p in cap]
            top = pr(hd + UP * R * 1.02)
            hair = convex_hull(cap_pts + [top, pr(hd + UP * R * 0.7 - fH * R * 0.6)])
            self.flat(dr, hair, pal["hair"], it=1)
            if fH[2] > -0.35:
                # râu: mảng hàm từ má này sang má kia
                upper = [sph(math.radians(a), math.radians(-30 + 0.12 * abs(a))) for a in range(-80, 81, 16)]
                lower = [sph(math.radians(a), math.radians(-78), 1.04) for a in range(80, -81, -16)]
                bp = [pr(p) for p in upper + lower]
                self.flat(dr, convex_hull(bp), pal["hair"], it=1)
                # mày và mắt
                for sg in (1, -1):
                    az = math.radians(24 * sg)
                    if vis(az, 0.15):
                        b0, b1 = pr(sph(math.radians(8 * sg), math.radians(22))), pr(sph(math.radians(42 * sg), math.radians(14)))
                        dr.line([tuple(b0), tuple(b1)], fill=pal["hair"], width=int(0.075 * s))
                        e = pr(sph(az, math.radians(6)))
                        w, h = 0.07 * s, 0.035 * s
                        dr.ellipse([e[0] - w, e[1] - h, e[0] + w, e[1] + h], fill=pal["eye"], outline=self.ink,
                                   width=max(1, int(self.ow * 0.5)))
                # mũi
                if vis(0, 0):
                    n0 = pr(sph(0, math.radians(-2), 1.08))
                    dr.ellipse([n0[0] - 0.04 * s, n0[1] - 0.03 * s, n0[0] + 0.04 * s, n0[1] + 0.03 * s],
                               fill=mul(pal["skin"], 0.75))
            else:
                self.ball(dr, q, R * s * 0.98, pal["hair"], shade=0.8, rx=R * s * 0.92)
        add("head", (hd,), head)

        # ---- thương: cán thuôn, mũi lá có gân, chắn trăng khuyết vàng, đá đỏ, tua đỏ rủ xuống
        w = self.px.w
        bt, tp = J["butt"], J["tip"]
        d3 = (tp - bt) / np.linalg.norm(tp - bt)
        base = tp - d3 * w["blade_len"]
        n = 10
        for i in range(n):
            a3 = bt + (base - bt) * (i / n)
            b3 = bt + (base - bt) * ((i + 1) / n)
            add(f"shaft{i}", (a3, b3), lambda dr, a3=a3, b3=b3, i=i:
                self.limb(dr, pr(a3), pr(b3), 0.05 * s, 0.05 * s, pal["shaft"], shade=0.7,
                          caps=(i == 0, i == n - 1)))

        def blade(dr):
            A, Bq = pr(base), pr(tp)
            dv = Bq - A
            L = np.linalg.norm(dv)
            u = dv / max(L, 1e-6)
            nrm = np.array([-u[1], u[0]])
            hw = w["blade_half_w"] * s
            fs = max(0.35, L / (w["blade_len"] * s))      # thu ngắn khi chĩa về camera
            leaf = [A + nrm * hw * 0.35, A + u * L * 0.32 + nrm * hw, Bq, A + u * L * 0.32 - nrm * hw * 0.9,
                    A - nrm * hw * 0.35]
            self.shape(dr, leaf, pal["blade"], shade=0.78, it=1)
            dr.line([tuple(A + u * L * 0.08), tuple(A + u * L * 0.85)], fill=pal["armor_light"],
                    width=max(1, int(0.03 * s)))
            # tua đỏ rủ theo trọng lực
            t0 = A - u * 0.08 * s
            tass = [t0 + np.array([-0.05 * s, 0]), t0 + np.array([0.05 * s, 0]),
                    t0 + np.array([0.08 * s, 0.32 * s]), t0 + np.array([-0.06 * s, 0.34 * s])]
            self.flat(dr, tass, pal["red"], it=1)
            # chắn trăng khuyết
            Rr = 0.19 * s * min(1.0, 0.6 + 0.4 * fs)
            crest = [A + (nrm * math.cos(a) - u * math.sin(a) * 0.55) * Rr for a in np.linspace(-1.9, 1.9, 9)]
            inner = [A + u * 0.07 * s + (nrm * math.cos(a) - u * math.sin(a) * 0.4) * Rr * 0.62
                     for a in np.linspace(1.6, -1.6, 7)]
            self.flat(dr, crest + inner, pal["gold"], it=1)
            r = 0.05 * s
            dr.ellipse([A[0] - r, A[1] - r, A[0] + r, A[1] + r], fill=pal["red"], outline=self.ink)
        add("blade", (base, tp), blade)

        # ---- vệt chém: dải thuôn theo quỹ đạo mũi thương; nửa gần trước thân, nửa xa sau thân
        if trail:
            dP = cam.depth(pe)
            near, far = [], []
            n = len(trail)
            for k in range(n - 1):
                (t0, i0), (t1, i1) = trail[k], trail[k + 1]
                age0, age1 = 1 - k / (n - 1), 1 - (k + 1) / (n - 1)
                w0, w1 = (1 - age0) ** 1.3, (1 - age1) ** 1.3
                quad = [pr(t0), pr(t1), pr(t1 + (i1 - t1) * w1), pr(t0 + (i0 - t0) * w0)]
                ((near if cam.depth((t0 + t1) / 2) > dP else far)).append((quad, age1))

            def strip(dr, quads, col, edge):
                for quad, age in quads:
                    c = mix(col, (80, 80, 80), age * 0.35)
                    dr.polygon([tuple(q) for q in quad], fill=c)
                for quad, age in quads:
                    dr.line([tuple(quad[0]), tuple(quad[1])], fill=edge, width=int(self.ow * 0.9))
            if far:
                out.append(("trail_far", -1e3, lambda dr: strip(dr, far, (150, 156, 162), (175, 180, 186))))
            if near:
                out.append(("trail_near", 1e3, lambda dr: strip(dr, near, (236, 240, 242), (255, 255, 255))))
        return out

    def draw(self, img, J, inf, trail=None, ss=1):
        dr = ImageDraw.Draw(img)
        ps = sorted(self.parts(J, inf, trail), key=lambda p: p[1])
        for _, _, fn in ps:
            fn(dr)
        return [p[0] for p in ps]


def skirt_points(b, J, inf):
    """Vạt áo: nón vải quanh hông; mép xoè rộng và hơi nâng theo tốc độ xoay của hông."""
    flare = min(1.0, abs(inf.get("spin_rate", 0.0)) / 90.0)
    pe = J["pelvis"]
    waist = pe + UP * 0.46
    rP, fP = right(inf["yaw_pelvis"]), fwd(inf["yaw_pelvis"])
    top, hem = [], []
    n = 24
    for k in range(n):
        a = 2 * math.pi * k / n
        dirv = rP * math.cos(a) + fP * math.sin(a)
        top.append(waist + dirv * b["waist_half"] * 0.95)
        sk = b.get("skirt", {})
        rr = b["waist_half"] + sk.get("flare_base", 0.04) + sk.get("flare_spin", 0.28) * flare
        drop = sk.get("drop", 0.14) - sk.get("lift_spin", 0.06) * flare + (0.04 if k % 2 else 0.0)  # mép rách
        hem.append(pe - UP * drop + dirv * rr * (1.0 if k % 2 else 0.93))
    return top, hem


def convex_hull(pts):
    P = sorted({(float(p[0]), float(p[1])) for p in pts})
    if len(P) < 3:
        return [np.array(p) for p in P]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return [np.array(p) for p in lo[:-1] + up[:-1]]


def render_clean(proxy, cam, J, inf, trail=None, ss=3, bg=(78, 80, 84), shadow=(58, 60, 63)):
    """Khung đẹp: nền xám như ref, bóng đất mềm, nhân vật + vệt chém. Vẽ ở ss lần rồi thu nhỏ (khử răng cưa)."""
    from build import Cam  # noqa: tránh vòng import ở mức module
    big = Cam(pitch_deg=math.degrees(cam.pitch), scale=cam.s * ss, size=(cam.size[0] * ss, cam.size[1] * ss),
              origin=(cam.o[0] * ss, cam.o[1] * ss))
    img = Image.new("RGB", big.size, bg)
    dr = ImageDraw.Draw(img)
    cp = proxy.com(J)
    g = big.proj(np.array([cp[0], 0, 0]))
    rw, rh = 1.15 * big.s, 0.2 * big.s
    dr.ellipse([g[0] - rw, g[1] - rh, g[0] + rw, g[1] + rh], fill=shadow)
    Painter(proxy, big).draw(img, J, inf, trail)
    return img.resize(cam.size, Image.LANCZOS)
