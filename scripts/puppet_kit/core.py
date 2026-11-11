"""Puppet Kit core: cut-out rig for one character still, 0 USD per animation, deterministic.

A rig (rig.json) = sources (stills) + bones (pivot, parent) + parts (a cut of one source, attached to a bone)
+ optional two-bone IK chains, sway deformers and sockets (named points that ride a bone, e.g. weapon root/tip).
An animation (anim.json) = one or more shots; a shot names a rig and drives bone channels with keyframes
and oscillators. Everything is in the pixel space of the rig's source still; export.py maps it to the game cell.

Guide: docs/puppet-kit.md
"""
from __future__ import annotations

import json
import math
import pathlib

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

# ---------------------------------------------------------------- image helpers


def key_magenta(img: Image.Image) -> np.ndarray:
    """RGB still on the flat magenta key -> float RGBA (0..255) with clean edges (colour pulled from inside)."""
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = (r > 150) & (b > 130) & (g < 0.55 * np.minimum(r, b))
    fg = ~bg
    fg = ndi.binary_opening(fg, iterations=1)
    alpha = ndi.gaussian_filter(fg.astype(np.float32), 0.7)
    inner = ndi.binary_erosion(fg, iterations=2)
    idx = ndi.distance_transform_edt(~inner, return_distances=False, return_indices=True)
    rgb = a[idx[0], idx[1]]
    return np.dstack([rgb, alpha * 255.0])


def reddish(rgba: np.ndarray) -> np.ndarray:
    r, g, b, al = rgba[..., 0], rgba[..., 1], rgba[..., 2], rgba[..., 3]
    return (al > 128) & (r > 3.0 * g) & (b < 90) & (r > 80)


def poly_mask(shape, poly) -> np.ndarray:
    m = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in poly], fill=255)
    return np.asarray(m) > 0


def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- matrices (3x3, column vectors, y down)


def T(x, y):
    return np.array([[1, 0, x], [0, 1, y], [0, 0, 1]], dtype=np.float64)


def R(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float64)


def S(sx, sy):
    return np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]], dtype=np.float64)


def SH(shx):
    """Horizontal shear: x += shx * (pivot_y - y); positive leans the top to the right."""
    return np.array([[1, -shx, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float64)


def apply(M, pt):
    v = M @ np.array([pt[0], pt[1], 1.0])
    return np.array([v[0], v[1]])


# ---------------------------------------------------------------- easing and tracks

EASE = {
    "linear": lambda u: u,
    "in": lambda u: u * u,
    "out": lambda u: 1 - (1 - u) ** 2,
    "inout": lambda u: u * u * (3 - 2 * u),
    "in3": lambda u: u ** 3,
    "out3": lambda u: 1 - (1 - u) ** 3,
    "step": lambda u: 0.0 if u < 1 else 1.0,
    "back": lambda u: 1 + 2.2 * (u - 1) ** 3 + 1.2 * (u - 1) ** 2,  # overshoots, then settles
}

DEFAULTS = {"rot": 0.0, "tx": 0.0, "ty": 0.0, "sx": 1.0, "sy": 1.0, "shx": 0.0, "sway": 1.0, "alpha": 1.0, "grey": 0.0, "fk": 0.0, "z": 0.0}


def track_value(track, f: float, default: float) -> float:
    """track = [[frame, value, ease?], ...] or {"keys": [...], "osc": [{"amp","period","phase"}], "base": v}."""
    if track is None:
        return default
    keys, osc, base = track, [], None
    if isinstance(track, dict):
        keys, osc, base = track.get("keys", []), track.get("osc", []), track.get("base")
        if isinstance(osc, dict):
            osc = [osc]
    v = default if base is None else base
    if keys:
        if f <= keys[0][0]:
            v = keys[0][1]
        elif f >= keys[-1][0]:
            v = keys[-1][1]
        else:
            for k0, k1 in zip(keys, keys[1:]):
                if k0[0] <= f <= k1[0]:
                    u = (f - k0[0]) / max(1e-9, k1[0] - k0[0])
                    e = EASE[k1[2] if len(k1) > 2 else "inout"](u)
                    v = k0[1] + (k1[1] - k0[1]) * e
                    break
    for o in osc:
        v += o["amp"] * math.sin(2 * math.pi * (f / o["period"] + o.get("phase", 0.0)))
    return v


# ---------------------------------------------------------------- rig


class Rig:
    def __init__(self, path, spec=None):
        self.path = pathlib.Path(path)
        self.dir = self.path.parent
        self.spec = spec if spec is not None else json.loads(self.path.read_text(encoding="utf-8"))
        self.ground = np.array(self.spec["ground"], dtype=np.float64)
        self.unit = float(self.spec["unit"])  # source pixels of the body height H (the tier height in the game)
        self.bones = {b["name"]: b for b in self.spec["bones"]}
        self.order = self._bone_order()
        self.parts = []
        self._load_parts()

    # --- building parts from the sources -------------------------------------------------
    def _bone_order(self):
        out, done = [], set()
        for n, b in self.bones.items():
            if b.get("parent") is not None and b["parent"] not in self.bones:
                raise ValueError(f"bone {n}: unknown parent {b['parent']}")
        while len(out) < len(self.bones):
            before = len(out)
            for n, b in self.bones.items():
                if n not in done and (b.get("parent") is None or b["parent"] in done):
                    out.append(n)
                    done.add(n)
            if len(out) == before:
                raise ValueError("bones form a cycle")
        return out

    def _src(self, name, cache):
        if name not in cache:
            cache[name] = key_magenta(Image.open(self.dir / self.spec["sources"][name]))
        return cache[name]

    def _load_parts(self):
        cache, masks = {}, {}
        specs = self.spec["parts"]
        # pass 1: explicit selections (polygon / colour)
        for p in specs:
            src = self._src(p["source"], cache)
            sel = p["select"]
            if "poly" in sel:
                m = poly_mask(src.shape, sel["poly"]) & (src[..., 3] > 8)
            elif sel.get("colour") == "red":
                red = ndi.binary_closing(reddish(src), iterations=4)
                m = ndi.binary_dilation(red, iterations=sel.get("outline", 9)) & (src[..., 3] > 8)
                yy = np.arange(src.shape[0])[:, None]
                m &= (yy >= sel.get("ymin", 0)) & (yy <= sel.get("ymax", 10 ** 6))
            elif sel.get("rest"):
                m = None
            else:
                raise ValueError(f"part {p['name']}: unknown select {sel}")
            masks[p["name"]] = m
        for p in specs:
            m = masks[p["name"]]
            if m is not None:
                for other in p.get("subtract", []):
                    m &= ~masks[other]
        # pass 2: the "rest" parts take what is left of their source, holes filled under the parts cut from them
        for p in specs:
            src = self._src(p["source"], cache)
            if masks[p["name"]] is None:
                taken = np.zeros(src.shape[:2], bool)
                for q in specs:
                    if q is not p and q["source"] == p["source"] and masks[q["name"]] is not None:
                        taken |= masks[q["name"]]
                m = ndi.binary_opening((src[..., 3] > 8) & ~taken, iterations=3)   # drop thin leftovers of the cut parts
                lab, n = ndi.label(m)
                if n > 1:
                    sizes = ndi.sum(m, lab, range(1, n + 1))
                    m = np.isin(lab, [i + 1 for i, sz in enumerate(sizes) if sz >= 0.02 * sizes.max()])
                masks[p["name"]] = m
        for p in specs:
            src = self._src(p["source"], cache)
            m = masks[p["name"]]
            img = src.copy()
            soft = ndi.gaussian_filter(m.astype(np.float32), 0.6)
            img[..., 3] = src[..., 3] * soft
            fill = np.zeros(m.shape, bool)
            for h in p.get("fill_under", []):  # {"part": name, "erode": px}: keep a filled patch hidden under that part
                fill |= (ndi.binary_erosion(masks[h["part"]], iterations=h.get("erode", 12)) & ~m
                         & ndi.binary_dilation(m, iterations=h.get("reach", 30)))
            if p.get("grow"):  # extend this part under its neighbours (a cape behind the body)
                fill |= ndi.binary_dilation(m, iterations=int(p["grow"])) & ~m & (src[..., 3] > 128)
            if fill.any():
                core = ndi.binary_erosion(m, iterations=3)
                idx = ndi.distance_transform_edt(~core, return_distances=False, return_indices=True)
                img[fill, :3] = src[idx[0][fill], idx[1][fill], :3]
                img[..., 3] = np.maximum(img[..., 3], ndi.gaussian_filter(fill.astype(np.float32), 0.6) * 255)
            ys, xs = np.where(img[..., 3] > 4)
            if len(xs) == 0:
                raise ValueError(f"part {p['name']} is empty")
            x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
            part = {"name": p["name"], "bone": p["bone"], "img": img[y0:y1, x0:x1].copy(), "off": (x0, y0), "spec": p,
                    "mask": m}
            self.parts.append(part)
        self.masks = masks
        for part in self.parts:
            d = part["spec"].get("deform")
            if d:
                part["weight"] = self._sway_weight(part, d)

    def _sway_weight(self, part, d):
        """Weight 0 on the rigid core, rising with the distance from it: the free end of a cape or plume moves most."""
        x0, y0 = part["off"]
        h, w = part["img"].shape[:2]
        shape = self.masks[part["name"]].shape
        core = np.zeros(shape, bool)
        for n in d.get("core_parts", []):
            core |= ndi.binary_opening(self.masks[n], iterations=6)
        if d.get("core_self_hard"):
            full = np.zeros(shape + (4,), np.float32)
            full[y0:y0 + h, x0:x0 + w] = part["img"]
            hard = (full[..., 3] > 128) & ~reddish(full)
            core |= ndi.binary_opening(hard, iterations=d.get("core_open", 8))
        if d.get("band"):                            # rigid above y0 and at y1, free in between (a robe hem above planted feet)
            y0b, y1b = d["band"]
            yy = np.arange(shape[0], dtype=np.float32)[:, None] * np.ones((1, shape[1]), np.float32)
            wgt = smoothstep((yy - y0b) / d.get("range", 60)) * smoothstep((y1b - yy) / d.get("range_end", 40))
        elif not core.any():
            return np.ones((h, w), np.float32)
        else:
            dist = ndi.distance_transform_edt(~core)
            wgt = smoothstep((dist - d.get("start", 6)) / d.get("range", 60))
        pad = int(d.get("pad", 40))
        part["wpad"] = pad
        wfull = np.pad(wgt, pad, mode="edge")
        return wfull[y0:y0 + h + 2 * pad, x0:x0 + w + 2 * pad].astype(np.float32)

    # --- posing ---------------------------------------------------------------------------
    def channels(self, tracks, f):
        vals = {}
        for key in tracks:
            if key.startswith("_"):
                continue
            name, ch = key.rsplit(".", 1)
            vals.setdefault(name, {})[ch] = track_value(tracks[key], f, DEFAULTS[ch])
        return vals

    def pose(self, tracks, f):
        """World matrix of every bone at frame f (float), IK chains solved."""
        vals = self.channels(tracks, f)
        world, locals_ = {}, {}
        for n in self.order:
            b = self.bones[n]
            v = vals.get(n, {})
            px, py = b["pivot"]
            local = (T(px + v.get("tx", 0), py + v.get("ty", 0)) @ R(v.get("rot", 0)) @ SH(v.get("shx", 0))
                     @ S(v.get("sx", 1), v.get("sy", 1)) @ T(-px, -py))
            locals_[n] = local
            world[n] = local if b.get("parent") is None else world[b["parent"]] @ local
        for ik in self.spec.get("ik", []):
            if vals.get(ik["upper"], {}).get("fk"):
                continue
            up, lo = self.bones[ik["upper"]], self.bones[ik["lower"]]
            s0, e0, w0 = np.array(up["pivot"], float), np.array(lo["pivot"], float), np.array(ik["end"], float)
            l1, l2 = np.linalg.norm(e0 - s0), np.linalg.norm(w0 - e0)
            s1 = apply(world[up["parent"]], s0)
            t1 = apply(world[ik["target"]["bone"]], ik["target"]["pt"])
            d = np.linalg.norm(t1 - s1)
            stretch = max(1.0, d / (l1 + l2 - 1e-6))
            L1, L2 = l1 * stretch, l2 * stretch
            dd = min(max(d, abs(L1 - L2) + 1e-6), L1 + L2 - 1e-6)
            base = math.atan2(t1[1] - s1[1], t1[0] - s1[0])
            bend = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
            if ik.get("hint"):                       # which way the joint bends, as a screen direction (a knee: forward)
                hx, hy = ik["hint"]
                c0 = (t1 - s1)[0] * hy - (t1 - s1)[1] * hx
            else:                                    # the side it is on in the rest pose
                c0 = (w0 - s0)[0] * (e0 - s0)[1] - (w0 - s0)[1] * (e0 - s0)[0]
            side0 = 1.0 if c0 >= 0 else -1.0
            a1 = base + side0 * bend
            e1 = s1 + L1 * np.array([math.cos(a1), math.sin(a1)])
            a1r = math.atan2(e0[1] - s0[1], e0[0] - s0[0])
            a2r = math.atan2(w0[1] - e0[1], w0[0] - e0[0])
            a2 = math.atan2(t1[1] - e1[1], t1[0] - e1[0])
            world[ik["upper"]] = T(*s1) @ R(math.degrees(a1)) @ S(stretch, 1) @ R(-math.degrees(a1r)) @ T(-s0[0], -s0[1])
            world[ik["lower"]] = T(*e1) @ R(math.degrees(a2)) @ S(stretch, 1) @ R(-math.degrees(a2r)) @ T(-e0[0], -e0[1])
            fixed = {ik["upper"], ik["lower"]}
            if ik.get("end_bone"):                   # a planted foot: it sits on the target and keeps its own angle
                eb = self.bones[ik["end_bone"]]
                ev = vals.get(ik["end_bone"], {})
                world[ik["end_bone"]] = T(*t1) @ R(ev.get("rot", 0)) @ T(-eb["pivot"][0], -eb["pivot"][1])
                fixed.add(ik["end_bone"])
            for n in self.order:                     # bones below the chain follow it
                par = self.bones[n].get("parent")
                if n not in fixed and par is not None and self._under(n, ik["upper"]):
                    world[n] = world[par] @ locals_[n]
        for st in self.spec.get("stretch", []):      # one bone aimed at a target and stretched to reach it (a sleeve)
            b = self.bones[st["bone"]]
            s0, e0 = np.array(b["pivot"], float), np.array(st["end"], float)
            s1 = apply(world[b["parent"]], s0)
            t1 = apply(world[st["target"]["bone"]], st["target"]["pt"])
            a0 = math.atan2(e0[1] - s0[1], e0[0] - s0[0])
            a1 = math.atan2(t1[1] - s1[1], t1[0] - s1[0])
            k = np.linalg.norm(t1 - s1) / max(1e-6, np.linalg.norm(e0 - s0))
            world[st["bone"]] = T(*s1) @ R(math.degrees(a1)) @ S(k, 1) @ R(-math.degrees(a0)) @ T(-s0[0], -s0[1])
        return world, vals

    def _skin_inverse(self, skin, world, px, py):
        """Smooth joints instead of cuts ("skin": {"bones": [b0, b1, ...], "blend": px, "tip": [x, y]}).
        The part is ONE picture bound to b0. Each further bone bi turns about its own pivot by an angle a_i relative to
        its parent; a pixel is turned by w_i * a_i, where w_i rises smoothly from 0 to 1 across a band of 2 * blend
        pixels centred on the joint, measured along the limb. So the picture bends like a hose around the joint and
        nothing is cut. Here: the inverse (canvas -> rest pixel), solved by a few fixed-point rounds."""
        names = skin["bones"]
        joints = []
        for i in range(1, len(names)):
            b = self.bones[names[i]]
            piv = np.array(b["pivot"], float)
            nxt = np.array(self.bones[names[i + 1]]["pivot"] if i + 1 < len(names) else skin["tip"], float)
            axis = (nxt - piv) / max(1e-6, np.linalg.norm(nxt - piv))
            rel = np.linalg.inv(world[names[i - 1]]) @ world[names[i]]
            ang = math.atan2(rel[1, 0], rel[0, 0])
            blend = skin.get("blend", 40)
            blend = blend[i - 1] if isinstance(blend, list) else blend
            joints.append((piv, axis, ang, float(blend)))
        def weights(qx, qy):
            return [smoothstep(((qx - piv[0]) * axis[0] + (qy - piv[1]) * axis[1] + blend) / (2 * blend)) for piv, axis, _, blend in joints]

        def turn(rx, ry, ws, sign):                       # sign +1: rest -> bent (outer joints first); -1: bent -> rest
            seq = list(zip(joints, ws))
            for (piv, _, ang, _), w in (reversed(seq) if sign > 0 else seq):
                c, sn = np.cos(sign * w * ang), np.sin(sign * w * ang)
                dx, dy = rx - piv[0], ry - piv[1]
                rx, ry = piv[0] + c * dx - sn * dy, piv[1] + sn * dx + c * dy
            return rx, ry

        def residual(qx, qy):
            fx, fy = turn(qx, qy, weights(qx, qy), +1)
            return np.hypot(fx - px, fy - py)

        # start from the best rigid guess: the pixel taken as belonging wholly to bone 0, 1, 2 ...
        best_x, best_y, best_r = px.copy(), py.copy(), residual(px, py)
        for j in range(1, len(names)):
            ws = [np.ones_like(px) if i < j else np.zeros_like(px) for i in range(len(joints))]
            cx, cy = turn(px, py, ws, -1)
            r = residual(cx, cy)
            take = r < best_r
            best_x, best_y, best_r = np.where(take, cx, best_x), np.where(take, cy, best_y), np.where(take, r, best_r)
        qx, qy = best_x, best_y
        for _ in range(skin.get("iterations", 12)):       # refine near the joints (damped fixed point)
            rx, ry = turn(px, py, weights(qx, qy), -1)
            qx, qy = 0.5 * qx + 0.5 * rx, 0.5 * qy + 0.5 * ry
            r = residual(qx, qy)
            take = r < best_r
            best_x, best_y, best_r = np.where(take, qx, best_x), np.where(take, qy, best_y), np.where(take, r, best_r)
        bad = best_r > skin.get("tolerance", 2.5)          # no rest pixel lands here (the inside of a sharp fold): leave it empty
        return np.where(bad, -1e6, best_x), np.where(bad, -1e6, best_y)

    def _under(self, name, ancestor):
        par = self.bones[name].get("parent")
        while par is not None:
            if par == ancestor:
                return True
            par = self.bones[par].get("parent")
        return False

    def sockets(self, world):
        return {n: apply(world[s["bone"]], s["pt"]).tolist() for n, s in self.spec.get("sockets", {}).items()}

    # --- muscle links ---------------------------------------------------------------------
    @property
    def links(self):
        return self.spec.get("links", [])

    def _pulls(self, part, world, vals):
        """Muscle links (rig["links"], mode "stretch") pulling this part: [(shift in the part's rest space, anchor)].
        The shift is the shoulder bone's own tx/ty seen from the part, so the picture near each anchor follows the shoulder."""
        out = []
        for lk in self.links:
            if lk.get("mode", "stretch") != "stretch" or lk["arm"] not in self.bones:
                continue
            anchors = [a for a in lk.get("anchors", []) if a["part"] == part["name"]]
            if not anchors:
                continue
            v = vals.get(lk["arm"], {})
            t = np.array([v.get("tx", 0.0), v.get("ty", 0.0)])
            if not t.any():
                continue
            par = self.bones[lk["arm"]].get("parent")
            Lm = np.linalg.inv(world[part["bone"]])[:2, :2] @ (world[par][:2, :2] if par else np.eye(2))
            out += [(Lm @ t, a) for a in anchors]
        return out

    # --- rendering ------------------------------------------------------------------------
    def render(self, tracks, f, view, size, phase=None):
        """Render frame f through `view` (3x3: rig pixels -> canvas pixels) on an RGBA float canvas (h, w)."""
        world, vals = self.pose(tracks, f)
        H, W = size
        out = np.zeros((H, W, 4), np.float32)
        period = tracks.get("_sway_period", 24)
        t = 2 * math.pi * (f / period if phase is None else phase)
        order = sorted(range(len(self.parts)), key=lambda i: i + 100 * vals.get(self.parts[i]["name"], {}).get("z", 0.0))
        for part in (self.parts[i] for i in order):      # channel "<part>.z": +1 moves it in front of everything, -1 behind
            pv = vals.get(part["name"], {})
            alpha_mul = pv.get("alpha", 1.0)
            if alpha_mul <= 0.003:
                continue
            M = view @ world[part["bone"]]
            img = part["img"]
            h, w = img.shape[:2]
            x0, y0 = part["off"]
            d = part["spec"].get("deform")
            pad = part.get("wpad", 0) if d else 0
            pulls = self._pulls(part, world, vals)
            cpad = pad + (int(max(np.hypot(*sh) * a.get("gain", 1.0) for sh, a in pulls)) + 3 if pulls else 0)   # pulled pixels can leave the picture box
            corners = np.array([[x0 - cpad, y0 - cpad], [x0 + w + cpad, y0 - cpad], [x0 + w + cpad, y0 + h + cpad],
                                [x0 - cpad, y0 + h + cpad]], float)
            skin = part["spec"].get("skin")
            mats = [M] + ([view @ world[b] for b in skin["bones"][1:]] if skin else [])
            cc = np.array([apply(m_, c) for m_ in mats for c in corners])
            bx0, by0 = np.floor(cc.min(0)).astype(int) - 2
            bx1, by1 = np.ceil(cc.max(0)).astype(int) + 2
            bx0, by0, bx1, by1 = max(bx0, 0), max(by0, 0), min(bx1, W), min(by1, H)
            if bx1 <= bx0 or by1 <= by0:
                continue
            yy, xx = np.mgrid[by0:by1, bx0:bx1].astype(np.float64)
            Mi = np.linalg.inv(M)
            sx = Mi[0, 0] * xx + Mi[0, 1] * yy + Mi[0, 2]
            sy = Mi[1, 0] * xx + Mi[1, 1] * yy + Mi[1, 2]
            if skin:
                sx, sy = self._skin_inverse(skin, world, sx, sy)
            sx0, sy0 = sx, sy
            for sh, a in pulls:
                wgt_p = a.get("gain", 1.0) * smoothstep(1.0 - np.hypot(sx - a["pt"][0], sy - a["pt"][1]) / float(a["radius"]))
                sx = sx - wgt_p * sh[0]
                sy = sy - wgt_p * sh[1]
            if d:
                amp = pv.get("sway", 1.0)
                wgt = ndi.map_coordinates(part["weight"], [sy - y0 + pad, sx - x0 + pad], order=1, mode="nearest")
                ax, ay = d.get("amp", [12, 4])
                wl = d.get("wavelength", 130)
                along = sy if d.get("axis", "y") == "y" else sx
                ph = t * d.get("speed", 1) + d.get("phase", 0.0) - d.get("dir", 1) * along / wl
                sx = sx - amp * ax * wgt * np.sin(ph)
                sy = sy - amp * ay * wgt * np.sin(ph - 0.5)
            samp = np.dstack([ndi.map_coordinates(img[..., c], [sy - y0, sx - x0], order=1, mode="constant", cval=0.0)
                              for c in range(4)]).astype(np.float32)
            if pulls and not d:             # skin stretches but never tears: keep the unpulled pixel wherever the pulled one is more transparent
                orig = np.dstack([ndi.map_coordinates(img[..., c], [sy0 - y0, sx0 - x0], order=1, mode="constant", cval=0.0)
                                  for c in range(4)]).astype(np.float32)
                samp = np.where(orig[..., 3:4] > samp[..., 3:4], orig, samp)
            grey = pv.get("grey", 0.0)
            if grey > 0:
                lum = (0.3 * samp[..., 0] + 0.59 * samp[..., 1] + 0.11 * samp[..., 2])[..., None]
                samp[..., :3] = samp[..., :3] * (1 - grey) + lum * grey
            a = samp[..., 3:4] / 255.0 * alpha_mul
            dst = out[by0:by1, bx0:bx1]
            oa = dst[..., 3:4] / 255.0
            na = a + oa * (1 - a)
            dst[..., :3] = np.where(na > 1e-6, (samp[..., :3] * a + dst[..., :3] * oa * (1 - a)) / np.maximum(na, 1e-6), 0)
            dst[..., 3:4] = na * 255.0
        return out, world

    # --- review ---------------------------------------------------------------------------
    def overlay(self, world=None):
        """The rest pose with part outlines, bones and sockets drawn on it (for review and the tuner)."""
        shape = next(iter(self.masks.values())).shape
        view = np.eye(3)
        img, world = self.render({}, 0, view, shape)
        base = Image.new("RGBA", (shape[1], shape[0]), (70, 80, 90, 255))
        base.alpha_composite(Image.fromarray(img.clip(0, 255).astype(np.uint8), "RGBA"))
        dr = ImageDraw.Draw(base)
        cols = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 128, 0), (255, 0, 255), (120, 160, 255), (255, 255, 255)]
        for i, p in enumerate(self.spec["parts"]):
            if "poly" in p["select"]:
                pts = [tuple(q) for q in p["select"]["poly"]]
                dr.line(pts + [pts[0]], fill=cols[i % len(cols)] + (255,), width=2)
        for n, b in self.bones.items():
            x, y = b["pivot"]
            if b.get("parent"):
                px, py = self.bones[b["parent"]]["pivot"]
                dr.line([(px, py), (x, y)], fill=(255, 255, 255, 255), width=2)
            dr.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 40, 40, 255), outline=(255, 255, 255, 255))
            dr.text((x + 8, y - 6), n, fill=(255, 255, 255, 255))
        for n, s in self.spec.get("sockets", {}).items():
            x, y = s["pt"]
            dr.rectangle([x - 5, y - 5, x + 5, y + 5], outline=(0, 255, 0, 255), width=2)
            dr.text((x + 8, y - 6), n, fill=(0, 255, 0, 255))
        gx, gy = self.ground
        dr.line([(gx - 200, gy), (gx + 200, gy)], fill=(0, 255, 0, 255), width=1)
        return base


# ---------------------------------------------------------------- animation (shots)


class Animation:
    """anim.json: {"fps": 15, "loop": bool, "hit_frame": n?, "shots": [{"rig": path, "frames": n, "tracks": {...}}]}.
    A file with "rig"/"frames"/"tracks" at the top level is one shot. Frames are 0-based inside a shot."""

    def __init__(self, path, asset_dir):
        self.path = pathlib.Path(path)
        self.spec = json.loads(self.path.read_text(encoding="utf-8"))
        self.asset = pathlib.Path(asset_dir)
        shots = self.spec.get("shots") or [{k: self.spec[k] for k in ("rig", "frames", "tracks") if k in self.spec}]
        self.shots, self.rigs = [], {}
        for s in shots:
            if "reel" in s:                      # frames of a pose reel (docs/puppet-kit-pose-reel.md): one picture per frame
                rdir = self.asset / s["reel"]
                reel = json.loads((rdir / "reel.json").read_text(encoding="utf-8"))
                for i, n in enumerate(s["pick"]):
                    key = f"{s['reel']}/{int(n):03d}"
                    if key not in self.rigs:
                        spec = {"sources": {"pose": f"{int(n):03d}.png"}, "ground": reel["ground"], "unit": reel["unit"],
                                "bones": [{"name": "root", "parent": None, "pivot": reel["ground"]}],
                                "parts": [{"name": "pose", "source": "pose", "bone": "root", "select": {"rest": True}}]}
                        self.rigs[key] = Rig(rdir / "reel.json", spec)
                    baked = {k: [[0, track_value(v, i, DEFAULTS[k.rsplit(".", 1)[1]])]] for k, v in s.get("tracks", {}).items()
                             if not k.startswith("_")}
                    self.shots.append({"rig": self.rigs[key], "frames": 1, "tracks": baked, "name": f"{s.get('name', 'reel')}:{int(n)}"})
                continue
            rp = str(s["rig"])
            if rp not in self.rigs:
                self.rigs[rp] = Rig(self.asset / rp)
            self.shots.append({"rig": self.rigs[rp], "frames": int(s["frames"]), "tracks": s.get("tracks", {}),
                               "name": s.get("name", pathlib.Path(rp).stem)})
        self.fps = self.spec.get("fps", 15)
        self.loop = bool(self.spec.get("loop", False))
        self.total = sum(s["frames"] for s in self.shots)

    def locate(self, f: float):
        """Global frame (float) -> (shot, local frame)."""
        acc = 0
        for s in self.shots:
            if f < acc + s["frames"] or s is self.shots[-1]:
                return s, f - acc
            acc += s["frames"]

    def view(self, rig: Rig, cell2x, pivot, body2x):
        """Rig pixels -> @2x cell pixels: the rig's ground point lands on the pivot, its unit becomes body2x."""
        k = body2x / rig.unit
        return T(cell2x[0] * pivot[0], cell2x[1] * pivot[1]) @ S(k, k) @ T(-rig.ground[0], -rig.ground[1])
