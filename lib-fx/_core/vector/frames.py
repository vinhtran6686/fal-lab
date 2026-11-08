"""Coordinate frames of an effect. Shapes are described in the effect's own coordinates:
  u = position along the motion (sweep angle for a swirl, distance along the axis for a thrust),
  v = position across it (radius for a swirl, offset from the axis for a thrust).

PolarFrame  : swirls, rings, shockwaves (centre fitted on the silhouette, seam put where the effect is thinnest).
LinearFrame : thrusts, beams, straight slashes (axis = principal direction of the silhouette, or given).

Every frame offers: sample(mask) -> boolean grid P[iu, iv]; to_xy(u, v); u_px(u-span, v) = length in px of a u-span;
and bands(P, axis) = decomposition of a mask into bands (one run per column), the input of stroke fitting."""
import numpy as np
from scipy import ndimage as ndi


class Frame:
    kind = "base"
    nu = nv = 0
    u0 = v0 = 0.0
    du = dv = 1.0

    def sample(self, mask):
        U, V = np.meshgrid(self.u0 + np.arange(self.nu) * self.du, self.v0 + np.arange(self.nv) * self.dv, indexing="ij")
        x, y = self.to_xy(U, V)
        return ndi.map_coordinates(mask.astype(float), [y, x], order=1, cval=0) > 0.5

    def u_px(self, du_span, v):  # px length of a u-span at across-position v
        return du_span

    def u_scale(self):  # px per u unit, used to express u widths of 'v'-axis strokes in px
        return 1.0

    def to_dict(self):
        return {"type": self.kind}


class PolarFrame(Frame):
    kind = "polar"

    def __init__(self, centre, seam=0.0, rmax=430.0, nu=1440, dv=0.5, r_typ=200.0):
        self.cx, self.cy = centre
        self.u0, self.du, self.nu = seam, 2 * np.pi / nu, nu
        self.v0, self.dv, self.nv = 0.0, dv, int(rmax / dv)
        self.r_typ = r_typ

    @classmethod
    def fit(cls, union, **kw):
        """Centre = Kasa circle fit on the outer outline; seam = angle where the effect is thinnest."""
        edge = union & ~ndi.binary_erosion(union)
        ys, xs = np.nonzero(edge)
        A = np.c_[2 * xs, 2 * ys, np.ones(len(xs))]
        cx, cy, k = np.linalg.lstsq(A, xs**2.0 + ys**2.0, rcond=None)[0]
        R = float(np.sqrt(max(k + cx * cx + cy * cy, 1.0)))
        H, W = union.shape
        rmax = float(np.hypot(max(cx, W - cx), max(cy, H - cy)))
        f = cls((float(cx), float(cy)), 0.0, rmax=min(rmax, 1.5 * max(H, W)), **kw)
        cov = ndi.uniform_filter1d(f.sample(union).sum(1).astype(float), 9, mode="wrap")
        f.u0 = float(np.argmin(cov) * f.du)
        return f

    def to_xy(self, u, v):
        return self.cx + v * np.cos(u), self.cy + v * np.sin(u)

    def u_px(self, du_span, v):
        return du_span * v

    def u_scale(self):
        return self.r_typ

    def to_dict(self):
        return {"type": self.kind, "centre": [self.cx, self.cy], "seam": self.u0}


class LinearFrame(Frame):
    kind = "linear"

    def __init__(self, origin, angle, length, half_width, du=1.0, dv=0.5):
        self.ox, self.oy = origin
        self.angle = angle
        self.u0, self.du, self.nu = -length / 2, du, int(length / du)
        self.v0, self.dv, self.nv = -half_width, dv, int(2 * half_width / dv)

    @classmethod
    def fit(cls, union, angle=None, **kw):
        """Axis = principal direction of the silhouette (or `angle` in degrees, 0 = +x, clockwise on screen)."""
        ys, xs = np.nonzero(union)
        cx, cy = xs.mean(), ys.mean()
        if angle is None:
            cov = np.cov(np.c_[xs - cx, ys - cy].T)
            w, V = np.linalg.eigh(cov)
            a = float(np.arctan2(V[1, -1], V[0, -1]))
        else:
            a = np.radians(angle)
        H, W = union.shape
        L = float(np.hypot(H, W))
        return cls((float(cx), float(cy)), a, L, L / 2, **kw)

    def to_xy(self, u, v):
        c, s = np.cos(self.angle), np.sin(self.angle)
        return self.ox + u * c - v * s, self.oy + u * s + v * c

    def to_dict(self):
        return {"type": self.kind, "origin": [self.ox, self.oy], "angle": self.angle}


class EllipseFrame(Frame):
    """A circle seen in perspective (a swing around a body, a ground ring): u = angle, v = radius, y squashed by `k`.
    Widths across the path are squashed too, so the far / near sides read thinner than the turns, as drawn by hand."""
    kind = "ellipse"

    def __init__(self, centre, k=0.3, tilt=0.0, rmax=1200.0):
        self.cx, self.cy = centre
        self.k, self.tilt = k, tilt
        self.u0, self.du, self.nu = 0.0, 2 * np.pi / 1440, 1440
        self.v0, self.dv, self.nv = 0.0, 0.5, int(rmax / 0.5)

    def to_xy(self, u, v):
        x, y = v * np.cos(u), self.k * v * np.sin(u)
        c, s = np.cos(self.tilt), np.sin(self.tilt)
        return self.cx + x * c - y * s, self.cy + x * s + y * c

    def u_px(self, du_span, v):
        return du_span * v * (1 + self.k) / 2

    def u_scale(self):
        return 200.0

    def to_dict(self):
        return {"type": self.kind, "centre": [self.cx, self.cy], "k": self.k, "tilt": self.tilt}


def make_frame(spec, union):
    """spec: profile['frame'] -> fitted Frame for this image."""
    t = (spec or {}).get("type", "polar")
    if t == "polar":
        return PolarFrame.fit(union)
    if t == "linear":
        return LinearFrame.fit(union, spec.get("angle"))
    raise ValueError(f"unknown frame type {t}")


def _runs(col):
    d = np.diff(np.r_[0, col.astype(np.int8), 0])
    return list(zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]))


def bands(frame, P, axis="u", min_cols=2, ext=4, edge_bias=(0.0, 0.0)):
    """Decompose a sampled mask into bands.
    axis 'u': columns along u, runs across v  -> strokes that follow the motion (most shapes);
    axis 'v': columns along v, runs across u  -> strokes pointing across the motion (hooks, radial tips).
    Linking: each band continues with the run it overlaps most; a branch born at / dying into a fork is extended `ext`
    columns into its parent (drawn INTO the parent, never cut flush). Returned positions are in frame units:
      pos (column centre), lo/hi (edges): v units for axis 'u'; px (u * u_scale) for axis 'v'.
    A run [s, e) of point samples spans (s - 0.5) .. (e - 0.5) samples; `edge_bias` = (lo, hi) extra shift in samples
    (0, 0 = geometric edge; best on clean shapes. swirl-slash uses (0.5, 1.5), which matched its anti-aliased,
    halo-tinted reference better: IoU +0.01-0.02 on thin layers)."""
    G = P if axis == "u" else P.T
    open_b, out, fork0, fork1, nid = [], {}, {}, {}, 0
    for j in range(G.shape[0]):
        rs = _runs(G[j])
        pairs = sorted(((min(e0, e1) - max(s0, s1), bi, ri) for bi, (_, (s0, e0)) in enumerate(open_b)
                        for ri, (s1, e1) in enumerate(rs) if min(e0, e1) - max(s0, s1) > 0), reverse=True)
        claimed, used_b, used_r = {}, set(), set()
        for _, bi, ri in pairs:
            if bi in used_b or ri in used_r:
                continue
            used_b.add(bi); used_r.add(ri); claimed[ri] = open_b[bi][0]
        for bi, (bid, (s0, e0)) in enumerate(open_b):
            if bi not in used_b:
                fork1[bid] = any(min(e0, e1) - max(s0, s1) > 0 for s1, e1 in rs)
        new_open = []
        for ri, (s, e) in enumerate(rs):
            if ri in claimed:
                bid = claimed[ri]
            else:
                bid, nid = nid, nid + 1
                out[bid] = []
                fork0[bid] = any(min(se[1], e) - max(se[0], s) > 0 for _, se in open_b)
            out[bid].append((j, s, e))
            new_open.append((bid, (s, e)))
        open_b = new_open
    if axis == "u":
        p0, dp, q0, dq = frame.u0, frame.du, frame.v0, frame.dv
    else:
        p0, dp, q0, dq = frame.v0, frame.dv, frame.u0 * frame.u_scale(), frame.du * frame.u_scale()
    res = []
    for bid, cols in out.items():
        if len(cols) < min_cols:
            continue
        if fork0.get(bid):
            j0, s0, e0 = cols[0]
            cols = [(j0 - k, s0, e0) for k in range(ext, 0, -1)] + cols
        if fork1.get(bid):
            j1, s1, e1 = cols[-1]
            cols = cols + [(j1 + k, s1, e1) for k in range(1, ext + 1)]
        a = np.array(cols, float)
        res.append(dict(axis=axis, pos=p0 + (a[:, 0] + 0.5) * dp, step=dp, lo=q0 + (a[:, 1] - 0.5 + edge_bias[0]) * dq,
                        hi=q0 + (a[:, 2] - 0.5 + edge_bias[1]) * dq,
                        fork0=bool(fork0.get(bid)), fork1=bool(fork1.get(bid))))
    return res


def band_area(frame, b):
    """Area of a band in px^2."""
    w = b["hi"] - b["lo"]
    if b["axis"] == "u":
        return float(np.sum(w * frame.u_px(b["step"], (b["hi"] + b["lo"]) / 2)))
    return float(np.sum(w * b["step"]))
