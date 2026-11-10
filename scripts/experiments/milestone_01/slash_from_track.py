# Milestone 01 experiment (not a core generator). One command rebuilds the slash VFX from the weapon track + parameters:
#   python scripts/experiments/milestone_01/slash_from_track.py [--params P.json] [--out DIR] [--set key=value ...]
# Geometry: Vector Kit tapered strokes (strokes.py) in an EllipseFrame with k = 1 (the circle fitted in Gate 3), rasterised by
# pipeline.strokes_cover_2x (anti-aliased coverage). Output: straight-alpha RGBA frames (no background baked in) @2x and @1x on the
# body's own cell (352x280 @2x, pivot = feet), one per body frame, plus a check report for criterion 3 (head vs blade tip).
import sys, json, math, argparse, pathlib, numpy as np
from PIL import Image
from scipy import ndimage as ndi
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'lib-fx'))
from _core.vector.frames import EllipseFrame          # noqa: E402
from _core.vector.strokes import peak_scale            # noqa: E402
from _core.vector.pipeline import strokes_cover_2x     # noqa: E402

A = ROOT / 'out/heroes/holy_commander'; D = A / 'source/vfx/slash_diag'
W2, H2, PX, PY, HPX = 352, 280, 176.0, 246.4, 111.0
to_px = lambda h: (PX + h[0] * HPX, PY - h[1] * HPX)


def load(params_path, sets):
    track = json.loads((D / 'weapon_track.json').read_text())
    P = json.loads(pathlib.Path(params_path).read_text())
    for s in sets:                                       # --set width_px2x=20 / taper.tail=1.2
        k, v = s.split('=', 1); node = P; ks = k.split('.')
        for kk in ks[:-1]: node = node[kk]
        node[ks[-1]] = json.loads(v)
    return track, P


def plan(track, P):
    """Per body frame: the stroke (u_tail, u_head, r_tail, r_head, width scale, alpha) or None."""
    fit = track['fit']; cx, cy = to_px(fit['centre_H']); R = fit['radius_H'] * HPX
    frame = EllipseFrame((cx, cy), k=1.0, tilt=0.0)
    S = {s['frame']: s for s in track['samples']}
    sw = fit['frames']; start = track['speed']['vfx_start_frame']; hit = track['hit_frame']
    def polar(f):
        x, y = to_px(S[f]['tip']); return math.atan2(y - cy, x - cx), math.hypot(x - cx, y - cy)
    us = {}; prev = None
    for f in sw:                                         # unwrap the angle along the swing
        u, r = polar(f)
        if prev is not None:
            while u - prev > math.pi: u -= 2 * math.pi
            while u - prev < -math.pi: u += 2 * math.pi
        us[f] = (u, r); prev = u
    u_first = us[sw[0]][0]; sign = 1 if us[sw[-1]][0] > u_first else -1
    L = P['length_rad']; out = {}
    grow = P['timeline']['grow']
    for i, f in enumerate(range(start, hit + 1)):
        uh, rh = us[f]; ut = uh - sign * L
        if sign * (ut - u_first) < 0: ut = u_first       # the band never starts before the cut's first point
        out[f] = dict(u_tail=ut, u_head=uh, r_tail=R, r_head=rh * (1 - P['tip_offset_ratio']), w=grow[min(i, len(grow) - 1)], alpha=1.0, attached=True)
    uh, rh = us[hit]; base = out[hit]; f = hit
    for st in P['timeline']['after_hit']:
        for _ in range(st['frames']):
            f += 1
            if f > track['frames']: break
            span = abs(base['u_head'] - base['u_tail']) * st['tail_keep']; h = uh + sign * st['drift']
            out[f] = dict(u_tail=h - sign * span, u_head=h, r_tail=R, r_head=rh, w=st['w'], alpha=st['alpha'], attached=False)
    return frame, (cx, cy, R, sign), out


def stroke(p, W, a, b, curv, R, inset=0.0, sign=1):
    """Band = Vector Kit tapered stroke on the fitted circle: centre line at the circle radius at the tail, easing to the radius of the
    frame's marked tip at the head (so the head sits on the tip); `curvature` bows the middle outward (+) or inward (-), in units of R."""
    lo, hi = sorted((p['u_tail'], p['u_head']))
    rt, rh = p['r_tail'], p['r_head']
    if sign < 0: rt, rh = rh, rt
    bulge = curv * R; off = inset * W
    sp = [rt - off, (2 * rt + rh) / 3 + bulge - off, (rt + 2 * rh) / 3 + bulge - off, rh - off]
    ta, tb = (a, b) if sign > 0 else (b, a)
    return dict(axis='u', pos0=float(lo), pos1=float(hi), spine=sp, W=peak_scale(W, ta, tb), a=ta, b=tb, e0=0.0, e1=0.0, op='add')


def render(track, P):
    frame, (cx, cy, R, sign), pl = plan(track, P)
    n = track['frames']; frames2 = []
    for f in range(1, n + 1):
        rgba = np.zeros((H2, W2, 4), float)
        p = pl.get(f)
        if p and abs(p['u_head'] - p['u_tail']) > 0.02:
            covs = []
            for L in P['layers']:
                st = stroke(p, P['width_px2x'] * L['width'] * p['w'], P['taper']['tail'], P['taper']['head'], P['curvature'], R, L.get('inset', 0.0), sign)
                c = strokes_cover_2x([st], frame, (H2, W2))                         # coverage at 2x of the @2x canvas
                c = c.reshape(H2, 2, W2, 2).mean(axis=(1, 3))                     # -> @2x, anti-aliased
                covs.append((L, c))
            g = P['glow']; gl = ndi.gaussian_filter(covs[1][1], g['sigma_px2x']) * g['alpha']
            col = np.zeros((H2, W2, 3)); al = np.zeros((H2, W2))
            def over(c_rgb, a):                                                     # straight-alpha "over"
                nonlocal col, al
                na = a + al * (1 - a); w = np.where(na > 0, a / np.maximum(na, 1e-6), 0)
                col = col * (1 - w[..., None]) + np.array(c_rgb, float) * w[..., None]; al = na
            over(g['color'], gl)
            for L, c in covs: over(L['color'], c * L['alpha'])
            al *= p['alpha']; rgba[..., :3] = col; rgba[..., 3] = al
        frames2.append(rgba)
    return frame, (cx, cy, R, sign), pl, frames2


def to_img(rgba):
    a = np.clip(rgba[..., 3], 0, 1); c = np.clip(rgba[..., :3], 0, 255)
    return Image.fromarray(np.dstack([c, a * 255]).round().astype(np.uint8), 'RGBA')


def check(track, P, frame, geo, pl, frames2=None, solids=None):
    """Criterion 3 on the observed swing frames. head_to_tip: leading point of the band vs the marked tip (H).
    tangent: the band's own direction at its head (drawn spine, radius change included) vs the tip's direction of travel at that frame,
    estimated by a central difference of the marked tips (tip f+1 - tip f-1; backward difference at the hit). The plain chord
    (tip f - tip f-1) is also reported: with ~50 deg of arc per frame it is the tangent half a frame earlier, so it lags by ~half the arc."""
    from _core.vector.strokes import bern
    cx, cy, R, sign = geo; S = {s['frame']: s for s in track['samples']}; rows = []; hit = track['hit_frame']
    def ang(u, v):
        return math.degrees(math.acos(max(-1, min(1, (u[0] * v[0] + u[1] * v[1]) / max(1e-9, math.hypot(*u) * math.hypot(*v))))))
    for f, p in sorted(pl.items()):
        if not p['attached'] or not S[f]['visible']: continue
        if cx == 'sweep':                               # tip side of the sweep frame: v = Lnom
            h1 = frame.to_xy(float(f), cy); h0 = frame.to_xy(float(f) - 0.02, cy)        # cy carries Lnom for the sweep frame
        else:
            st = stroke(p, 1.0, 1.0, 1.0, P['curvature'], R, 0.0, sign)
            t1, t0 = (1.0, 0.98) if sign > 0 else (0.0, 0.02)
            pos = lambda t: frame.to_xy(st['pos0'] + (st['pos1'] - st['pos0']) * t, float(bern(st['spine'], t)))
            h1, h0 = pos(t1), pos(t0)
        h1 = (float(h1[0]), float(h1[1])); h0 = (float(h0[0]), float(h0[1])); band = (h1[0] - h0[0], h1[1] - h0[1])
        tx, ty = to_px(S[f]['tip']); dist = math.hypot(h1[0] - tx, h1[1] - ty) / HPX
        nb = S.get(f + 1) if f < hit else None; pv = S.get(f - 1)
        a_ = to_px(pv['tip']) if pv and pv['tip'] else (tx, ty); b_ = to_px(nb['tip']) if nb and nb['tip'] else (tx, ty)
        central = ang(band, (b_[0] - a_[0], b_[1] - a_[1])); chord = ang(band, (tx - a_[0], ty - a_[1]))
        meas = None
        if frames2 is not None:                       # measured: farthest visible pixel of the rendered band along the direction of travel
            al = solids[f - 1] if solids is not None else frames2[f - 1][..., 3]; ys, xs = np.nonzero(al > 0.5)
            if len(xs):
                if cx == 'sweep':     # the ribbon's head must reach the tip: nearest drawn pixel to the marked tip
                    meas = round(float(np.min(np.hypot(xs - tx, ys - ty))) / HPX, 4)
                else:
                    d = np.array(band) / max(1e-9, math.hypot(*band)); k = int(np.argmax(xs * d[0] + ys * d[1]))
                    meas = round(math.hypot(xs[k] - tx, ys[k] - ty) / HPX, 4)
        rows.append(dict(frame=f, head_to_tip_H=round(dist, 4), head_to_tip_measured_H=meas, tangent_error_deg=round(central, 1), chord_error_deg=round(chord, 1)))
    ok_d = all((r['head_to_tip_measured_H'] if r['head_to_tip_measured_H'] is not None else r['head_to_tip_H']) <= 0.1 for r in rows); ok_a = all(r['tangent_error_deg'] <= 15 for r in rows)
    return dict(rows=rows, head_ok=ok_d, tangent_ok=ok_a, thresholds=dict(head_H=0.1, tangent_deg=15), tangent_method='central difference of marked tips (chosen after the chord numbers came back large; both reported)')


def save(frames2, out, name='slash_diag'):
    for res, sub in ((1, '@2x'), (2, '@1x')):
        d = out / 'front' / 'frames' / sub; d.mkdir(parents=True, exist_ok=True)
        for i, fr in enumerate(frames2, 1):
            im = to_img(fr)
            if res == 2: im = im.resize((W2 // 2, H2 // 2), Image.LANCZOS)
            im.save(d / f'hero_holy_commander_fx_{name}_front_{i:02d}.png')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--params', default=str(D / 'slash_params.json'))
    ap.add_argument('--out', default=str(D / 'review' / 'gate4' / 'base')); ap.add_argument('--set', action='append', default=[])
    a = ap.parse_args(); track, P = load(a.params, a.set)
    extra = {}
    if P.get('style') == 'layered':
        frame, geo, pl, fr, extra = render_layered(track, P)
    else:
        frame, geo, pl, fr = render(track, P)
    out = pathlib.Path(a.out); save(fr, out)
    rep = dict(params=P, geometry=extra, plan={str(k): v for k, v in pl.items()}, criterion3=check(track, P, frame, geo, pl, fr, extra.pop('solids', None)))
    (out / 'report.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    print(json.dumps(rep['criterion3'], ensure_ascii=False))



# ---------------------------------------------------------------- layered style (user, 2026-11-10: thicker, root-to-tip, more layers)
class SweepFrame:
    """The area the blade sweeps, as an effect frame for Vector Kit strokes (experiment, not core):
    u = time in body frames (8.0 = frame 8 ...), v = position along the blade in px of a nominal blade (0 = marked ROOT, Lnom = marked TIP).
    The root and tip paths are Catmull-Rom curves through the marked samples, so a stroke drawn at v = Lnom rides exactly on the tip."""
    kind = 'sweep'
    def __init__(self, us, roots, tips, Lnom):
        self.us = np.asarray(us, float); self.R = np.asarray(roots, float); self.T = np.asarray(tips, float); self.L = float(Lnom)
        d = lambda P: np.linalg.norm(np.diff(P, axis=0), axis=1).mean()
        self.sr, self.st = d(self.R), d(self.T)
    def _cr(self, P, u):
        u = np.clip(np.asarray(u, float), self.us[0], self.us[-1] + 0.6); i = np.clip(np.floor(u - self.us[0]).astype(int), 0, len(self.us) - 2)
        t = (u - self.us[0]) - i; Pp = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2], 3 * P[-1] - 2 * P[-2]])
        p0, p1, p2, p3 = Pp[i], Pp[i + 1], Pp[i + 2], Pp[i + 3]; t = t[..., None]
        return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
    def to_xy(self, u, v):
        u = np.asarray(u, float); v = np.asarray(v, float); u, v = np.broadcast_arrays(u, v)
        r, t = self._cr(self.R, u), self._cr(self.T, u); f = (v / self.L)[..., None]; p = r + (t - r) * f
        return p[..., 0], p[..., 1]
    def u_px(self, du, v):
        return du * (self.sr + (self.st - self.sr) * float(np.clip(v / self.L, 0, 1.5)))
    def u_scale(self):
        return 0.5 * (self.sr + self.st)
    def to_dict(self):
        return {'type': self.kind}


def render_layered(track, P):
    """Reuses the showcase generator gen_slash_loop (style 'heavy': main ribbon, inner ribbon, dark strand, dry-brush fingers, teeth,
    speed lines, breaks, debris) inside the SweepFrame: the main ribbon spans the blade from root (v = 0) to tip (v = Lnom), so the head
    covers the whole blade and its outer edge rides on each frame's marked tip. u runs in body frames (one frame ~ 0.9 rad of this arc,
    close to the radian units the showcase timeline uses)."""
    from _core.vector import gen_slash_loop as GL
    L = P['layered']; S = {s['frame']: s for s in track['samples']}
    fs = track['fit']['frames']; start = track['speed']['vfx_start_frame']; hit = track['hit_frame']
    roots = [S[f]['root_px2x'] for f in fs]; tips = [S[f]['tip_px2x'] for f in fs]
    Lnom = float(np.mean([math.dist(r, t) for r, t in zip(roots, tips)]))
    frame = SweepFrame(fs, roots, tips, Lnom)
    W = Lnom * L['width_scale']; R = Lnom - W / 2
    D = GL.design(L['seed'], 'heavy'); sc = Lnom / D['width']          # showcase px -> this blade
    for f_ in D['fingers']: f_['ext'] = 0.0
    for ln in D['lines']: ln['dr'] *= sc; ln['w'] = max(ln['w'] * sc, 1.2)
    for fl in D['flecks']: fl['r'] *= sc; fl['L'] *= sc
    u0 = float(fs[0]); lag = L['lag_frames']
    D.update(centre=(0, 0), R=R, k=1.0, tilt=0.0, width=W, u_start=u0, back=1.0, front=1.0, min_w=L['min_w'] * sc)
    TL, pl = [], {}
    for f in range(start, hit + 1):
        TL.append(dict(head=f - u0, tail=max(0.0, f - lag - u0), w=L['grow'][min(f - start, len(L['grow']) - 1)], spread=0.0, brk=0.0, frames=[f]))
        pl[f] = dict(attached=True, alpha=1.0)
    for f in range(hit + 1, track['frames'] + 1):
        a_ = L['after'].get(str(f))
        if not a_: break
        TL.append(dict(head=hit - u0 + a_.get('drift', 0.0), tail=max(0.0, hit - u0 - lag * a_['tail_keep']), w=a_['w'], spread=a_['spread'], brk=a_['brk'], frames=[f]))
        pl[f] = dict(attached=False, alpha=a_.get('alpha', 1.0))
    first_brk = next((i for i, T in enumerate(TL) if T['brk'] > 0), len(TL))
    for i, d in enumerate(D['debris']):
        d['dr'] *= sc; d['L'] *= sc; d['born'] = first_brk + (0 if i < 3 else 1); d['drift'] *= 0.5
    n = track['frames']; frames2 = [np.zeros((H2, W2, 4)) for _ in range(n)]; solids = [np.zeros((H2, W2)) for _ in range(n)]
    pal = L['palette']; g = P['glow']
    for k, T in enumerate(TL):
        f = T['frames'][0]; out = GL.drawing(D, k, TL)
        cv = L.get('curvature', 0.0) * Lnom
        if cv:
            for lay in out.values():
                for s_ in lay:
                    if s_['op'] == 'add' and len(s_['spine']) == 4: s_['spine'] = [s_['spine'][0], s_['spine'][1] + cv, s_['spine'][2] + cv, s_['spine'][3]]
        cr = L.get('core')
        if cr and T['w'] > 0.3 and T['head'] - T['tail'] > 0.4:     # bright core streak along the tip side of the ribbon
            h_, t_ = u0 + T['head'], u0 + T['tail']; Wc = W * cr['width'] * T['w']
            out['core'] = [dict(axis='u', pos0=float(t_ + 0.2 * (h_ - t_)), pos1=float(h_ - 0.06 * (h_ - t_)), spine=[R + cr['offset'] * W] * 4,
                                W=peak_scale(Wc, 1.4, 0.6), a=1.4, b=0.6, e0=0.0, e1=0.0, op='add')]
        covs = []
        for lay in ('deep', 'blue', 'ice', 'core'):
            st = out.get(lay, [])
            if lay in pal:
                c = strokes_cover_2x(st, frame, (H2, W2)).reshape(H2, 2, W2, 2).mean(axis=(1, 3)) if any(s_['op'] == 'add' for s_ in st) else np.zeros((H2, W2))
                covs.append((pal[lay], c))
        sil = np.maximum.reduce([c for _, c in covs]); solids[f - 1] = sil
        col = np.zeros((H2, W2, 3)); al = np.zeros((H2, W2))
        def over(c_rgb, a_):
            nonlocal col, al
            na = a_ + al * (1 - a_); w = np.where(na > 0, a_ / np.maximum(na, 1e-6), 0)
            col = col * (1 - w[..., None]) + np.array(c_rgb, float) * w[..., None]; al = na
        over(g['color'], np.clip(ndi.gaussian_filter(sil, g['sigma_px2x']) * g['alpha'], 0, 1))
        for c_rgb, c in covs: over(c_rgb, c)
        frames2[f - 1] = np.dstack([col, al * pl[f]['alpha']])
    # for the criterion-3 check: head = the marked tip at each attached frame
    for f, p in pl.items():
        x, y = frame.to_xy(float(min(f, hit)), Lnom); p.update(u_head=float(f), u_tail=float(f - lag), r_head=None, head_xy=(float(x), float(y)))
    return frame, ('sweep', Lnom, None, 1), pl, frames2, dict(Lnom_px2x=Lnom, ribbon_R=R, ribbon_W=W, scale=sc, solids=solids)

if __name__ == '__main__':
    main()
