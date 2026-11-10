# Milestone 01 experiment. Builds weapon_track.json from the marker page's raw marks, measures tip speed, finds the VFX start
# and fits the tip path (circle first, as agreed), then writes the Gate 3 review images.
# Usage: python scripts/experiments/milestone_01/track_report.py
import json, math, pathlib, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.optimize import least_squares
ROOT = pathlib.Path(__file__).resolve().parents[3]
A = ROOT / 'out/heroes/holy_commander'; D = A / 'source/vfx/slash_diag'; R = D / 'review'; R.mkdir(parents=True, exist_ok=True)
try: FT = ImageFont.truetype('DejaVuSans.ttf', 14); FS = ImageFont.truetype('DejaVuSans.ttf', 17)
except OSError: FT = FS = ImageFont.load_default()
meta = json.loads((A / 'meta.json').read_text()); st = meta['states']['attack_diag_side']
raw = json.loads((D / 'track_marks_raw.json').read_text())['docs']
H2, PX, PY = 111.0, 176.0, 246.4                      # @2x: H px, pivot (0.5*352, 0.88*280)
S = []
for d in sorted(raw, key=lambda d: d['frame']):
    S.append({'frame': d['frame'], 'ms': d['ms'], 'visible': bool(d['visible']), 'used': bool(d['include']), 'estimated': False, 'side': d['side'],
              'root': d.get('rootH'), 'tip': d.get('tipH'), 'root_px2x': d.get('root'), 'tip_px2x': d.get('tip'), 'note': d.get('note', '')})
obs = [s for s in S if s['used'] and s['visible'] and s['tip']]
# speed of the tip between consecutive observed frames (H / frame), assigned to the later frame
for a, b in zip(obs, obs[1:]):
    b['tip_speed'] = round(math.dist(a['tip'], b['tip']) / (b['frame'] - a['frame']), 4)
obs[0]['tip_speed'] = 0.0
peak = max(obs, key=lambda s: s['tip_speed']); vpk = peak['tip_speed']; thr = max(0.2 * vpk, 0.1)
# VFX start: the contiguous run of frames at or above the threshold that contains the peak (a wind-up before it is not the cut)
i = obs.index(peak); j = i
while j - 1 >= 0 and obs[j - 1]['tip_speed'] >= thr: j -= 1
start = obs[j]; k = i
while k + 1 < len(obs) and obs[k + 1]['tip_speed'] >= thr: k += 1
end_fast = obs[k]
hit = st['hit_frame']
swing = [s for s in obs if obs[j - 1 if j else 0]['frame'] <= s['frame'] <= hit]   # from the frame before the start (the cut's first point) to the hit
P = np.array([s['tip'] for s in swing])
def fit_circle(P):
    x, y = P[:, 0], P[:, 1]; A_ = np.c_[2 * x, 2 * y, np.ones(len(x))]; c = np.linalg.lstsq(A_, x * x + y * y, rcond=None)[0]
    cx, cy = c[0], c[1]; r = math.sqrt(c[2] + cx * cx + cy * cy)
    res = least_squares(lambda p: np.hypot(x - p[0], y - p[1]) - p[2], [cx, cy, r]); return res.x
def fit_ellipse(P):          # centre, a, b(=k*a), tilt: 5 dof
    cx, cy, r = fit_circle(P)
    def f(p):
        c, s = math.cos(p[4]), math.sin(p[4]); dx, dy = P[:, 0] - p[0], P[:, 1] - p[1]; u = (dx * c + dy * s) / p[2]; v = (-dx * s + dy * c) / p[3]
        rr = np.hypot(u, v); return (rr - 1) * np.minimum(p[2], p[3])
    return least_squares(f, [cx, cy, r, r, 0.0]).x
cx, cy, r = fit_circle(P); res = np.abs(np.hypot(P[:, 0] - cx, P[:, 1] - cy) - r)
loo = []
for m in range(1, len(P) - 1):
    Q = np.delete(P, m, 0); c2 = fit_circle(Q); loo.append(abs(math.hypot(P[m, 0] - c2[0], P[m, 1] - c2[1]) - c2[2]))
gate = {'model': 'circle (EllipseFrame k=1)', 'n': len(P), 'dof': 3, 'frames': [s['frame'] for s in swing],
        'centre_H': [round(cx, 4), round(cy, 4)], 'radius_H': round(r, 4),
        'residual_mean_H': round(float(res.mean()), 4), 'residual_max_H': round(float(res.max()), 4),
        'loo_interior_mean_H': round(float(np.mean(loo)), 4), 'loo_interior_max_H': round(float(np.max(loo)), 4),
        'threshold': {'mean_H': 0.08, 'max_H': 0.15}}
gate['pass'] = gate['residual_mean_H'] <= 0.08 and gate['residual_max_H'] <= 0.15
# sweep angle and direction of each swing sample (tangent = direction of travel)
ang = [math.degrees(math.atan2(p[1] - cy, p[0] - cx)) for p in P]
for s, a in zip(swing, ang): s['arc_angle_deg'] = round(a, 2)
track = {'state': 'attack_diag_side', 'take': 'source/video/attack_diag_side_downcut_t01.mp4', 'recipe': 'frames/export_recipe.json#diag',
         'cell': meta['cell'], 'pivot': meta['pivot'], 'fps': st['fps'], 'frames': st['frames'], 'frame_ms': 67,
         'units': 'H, origin = feet pivot, x forward (right), y up; time ms from frame 1',
         'tier_H_px': 60, 'body_height_px': meta['body_height_2x'] / 2, 'coordinate_H_px': meta['body_height_2x'] / 2,
         'px_to_H_2x': {'x': '(px - 176) / 111', 'y': '(246.4 - py) / 111'},
         'hit_frame': hit, 'marked_by': 'user, Blade Track Marker page', 'samples': S,
         'speed': {'peak_frame': peak['frame'], 'peak_H_per_frame': vpk, 'threshold_H_per_frame': round(thr, 4),
                   'rule': 'max(20% of peak, 0.1 H/frame); start = first frame of the contiguous fast run that contains the peak',
                   'vfx_start_frame': start['frame'], 'vfx_start_ms': start['ms'], 'fast_until_frame': end_fast['frame']},
         'fit': gate}
(D / 'weapon_track.json').write_text(json.dumps(track, indent=1, ensure_ascii=False))
# ---------- review images ----------
fdir = A / 'frames/attack_diag_side/frames/@2x'; files = sorted(fdir.glob('*.png'))
Z = 2; cw, ch = 352 * Z // 2 * 1, 280 * Z // 2 * 1
cols = 8; sheet = Image.new('RGB', (cols * 352, 2 * (280 + 24)), (52, 55, 64)); dr = ImageDraw.Draw(sheet)
for s in S:
    n = s['frame'] - 1; im = Image.open(files[n]).convert('RGBA'); bg = Image.new('RGBA', im.size, (52, 55, 64, 255)); bg.alpha_composite(im)
    d = ImageDraw.Draw(bg)
    if s['root_px2x'] and s['tip_px2x']:
        d.line([tuple(s['root_px2x']), tuple(s['tip_px2x'])], fill=(255, 255, 255), width=2)
        for p, c in ((s['root_px2x'], (66, 153, 225)), (s['tip_px2x'], (229, 62, 62))):
            d.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], fill=c, outline=(255, 255, 255))
    x, y = (n % cols) * 352, (n // cols) * (280 + 24); sheet.paste(bg.convert('RGB'), (x, y + 24))
    tag = f"#{s['frame']}  {s['ms']} ms" + ('  HIT' if s['frame'] == hit else '') + ('  VFX start' if s['frame'] == start['frame'] else '')
    dr.text((x + 6, y + 5), tag, fill=(255, 220, 120) if s['frame'] in (hit, start['frame']) else (230, 230, 235), font=FS)
sheet.save(R / 'gate3_contact_sheet.png')
# trajectory plot in H
W, Hh, sc, ox, oy = 1000, 720, 260, 380, 520
pl = Image.new('RGB', (W, Hh), (250, 250, 252)); d = ImageDraw.Draw(pl)
P2 = lambda x, y: (ox + x * sc, oy - y * sc)
for g in np.arange(-1.5, 2.01, 0.5):
    d.line([P2(g, -0.5), P2(g, 2)], fill=(225, 228, 235)); d.line([P2(-1.5, g), P2(1.5, g)], fill=(225, 228, 235))
    d.text((P2(g, -0.5)[0] - 8, P2(g, -0.5)[1] + 4), f"{g:g}", fill=(120, 125, 135)); d.text((P2(-1.5, g)[0] - 30, P2(-1.5, g)[1] - 6), f"{g:g}", fill=(120, 125, 135))
d.line([P2(-1.5, 0), P2(1.5, 0)], fill=(150, 155, 165), width=2); d.text(P2(0.02, -0.04), 'chân (gốc)', fill=(90, 95, 105), font=FT)
t = np.linspace(min(ang) - 15, max(ang) + 15, 200); t = np.radians(t)
d.line([P2(cx + r * math.cos(a), cy + r * math.sin(a)) for a in t], fill=(160, 160, 220), width=2)
d.ellipse([P2(cx, cy)[0] - 4, P2(cx, cy)[1] - 4, P2(cx, cy)[0] + 4, P2(cx, cy)[1] + 4], fill=(120, 120, 200))
pts = [s for s in S if s['tip']]
d.line([P2(*s['tip']) for s in pts], fill=(229, 62, 62), width=1)
for s in pts:
    q = P2(*s['tip']); rr = 6 if s in swing else 3; d.ellipse([q[0] - rr, q[1] - rr, q[0] + rr, q[1] + rr], fill=(229, 62, 62) if s in swing else (240, 160, 160))
    if s in swing or s['frame'] in (1, 5, 16): d.text((q[0] + 8, q[1] - 14), f"{s['frame']} ({s.get('tip_speed', 0):.2f})", fill=(40, 40, 50), font=FT)
    if s['root']: rq = P2(*s['root']); d.line([rq, q], fill=(200, 205, 215))
d.text((16, 12), f"Quỹ đạo mũi kiếm (H). Đỏ đậm = đoạn khớp cung (hình {gate['frames'][0]}-{gate['frames'][-1]}), số trong ngoặc = tốc độ H/hình", fill=(30, 30, 40), font=FT)
d.text((16, 32), f"Cung tròn: tâm ({cx:.2f}; {cy:.2f}) H, bán kính {r:.2f} H; sai số TB {gate['residual_mean_H']:.3f} H, lớn nhất {gate['residual_max_H']:.3f} H -> {'ĐẠT' if gate['pass'] else 'KHÔNG ĐẠT'} (ngưỡng 0,08 / 0,15)", fill=(30, 30, 40), font=FT)
d.text((16, 52), f"Đỉnh tốc độ hình {peak['frame']} = {vpk:.2f} H/hình; ngưỡng {thr:.2f}; VFX bắt đầu hình {start['frame']} ({start['ms']} ms); hit hình {hit}", fill=(30, 30, 40), font=FT)
pl.save(R / 'gate3_tip_trajectory.png')
print(json.dumps({'speed': track['speed'], 'fit': gate}, indent=1, ensure_ascii=False))
