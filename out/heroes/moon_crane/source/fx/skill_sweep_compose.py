"""moon_crane skill_sweep: pose A -> pose B (cut from the clip by skill_sweep_cut.py) + lib-fx crescent + a two-layer rig
(legs fixed; the upper body breathes: a small squash/stretch about the waist and a tiny sway). 15 fps, one drawing per frame."""
import json, math, pathlib
from PIL import Image
R = pathlib.Path('out/heroes/moon_crane/frames'); B = R/'skill_sweep'; FX = R/'fx/skill_sweep'
m = json.load(open(FX/'meta.json', encoding='utf8')); ox, oy = m['origin']; fw, fh = m['frame_size_2x']
CW, CH = json.load(open(B/'cut.json', encoding='utf8'))['cell']
X0, Y0, X1, Y1 = min(0, ox), 0, max(CW, ox+fw), max(CH, oy+fh); W, H = X1-X0, Y1-Y0
WAIST = {'A': 222, 'B': 224}; PIVX = 176          # waist cut line (cell px) and the sway pivot
body = {k: Image.open(B/f'pose_{k}.png').convert('RGBA') for k in 'AB'}
SPLIT = {'A': ('left', 118), 'B': ('right', 232)}          # x of the cut across the haft: the spear beyond it is its own layer
def rig(k, lean, prev, sy=1.0):
    """three layers: legs (feet fixed, the legs lean a little: a shear that is 0 at the soles), upper body (leans `lean` degrees about the waist,
    + = toward the swing, squash/stretch `sy`), and the spear beyond the hands (follows the body, then lags: turns against the change of lean)."""
    img = body[k]; cy = WAIST[k]; yb = 246
    low = img.crop((0, cy, CW, CH)); kk = 0.3*lean/(yb-cy)
    low = low.transform(low.size, Image.AFFINE, (1, kk, -kk*(yb-cy), 0, 1, 0), resample=Image.BICUBIC)   # x_src = x + kk*(y-(yb-cy)): shift 0 at the soles
    up = img.crop((0, 0, CW, cy)); side, xs = SPLIT[k]
    sp = up.copy(); import numpy as np
    m = np.zeros((cy, CW), bool); m[:, :xs] = side == 'left'; m[:, xs:] = side == 'right'
    a = np.array(sp); a[..., 3] = np.where(m, a[..., 3], 0); sp = Image.fromarray(a)
    b2 = np.array(up); b2[..., 3] = np.where(m, 0, b2[..., 3]); up = Image.fromarray(b2)
    def sway(im, deg, pv):
        im = im.resize((CW, max(1, round(cy*sy))), Image.BICUBIC); lay = Image.new('RGBA', (CW, CH), (0,0,0,0)); lay.alpha_composite(im, (0, cy-im.height))
        return lay.rotate(-deg, resample=Image.BICUBIC, center=pv, translate=(0.6*lean, 0))
    out = Image.new('RGBA', (CW, CH), (0,0,0,0)); out.alpha_composite(sway(up, lean, (PIVX, cy)))
    out.alpha_composite(sway(sp, lean + 0.45*(prev-lean), (PIVX, cy)))
    out.alpha_composite(low, (0, cy)); return out
# the motion: A stands still, ONE nudge back (the wind-up), the cut to B with the fx, ONE damped overshoot forward (inertia) and B settles
WIND = [-1.6, -3.5, -4.8, -4.8]                      # lean back, away from the swing
INERTIA = [4.8, 6.0, 4.8, 2.6, 0.3, -1.4, -1.9, -1.3, -0.3, 0.5, 0.6, 0.3, 0.0, 0.0, 0.0]   # overshoot, one rebound, settle
fxl = lambda kind, i: Image.open(FX/kind/'@2x'/f'crescent_{i:02d}.png').convert('RGBA')
seq = [('A', 0.0, 0) for _ in range(4)] + [('A', l, 0) for l in WIND] + [('A', -4.8, 1)] + [('B', l, i) for l, i in zip(INERTIA, [*range(2, 10), *[0]*7])]
outs = []
prev = 0.0
for p, lean, i in seq:
    c = Image.new('RGBA', (W, H), (0,0,0,0)); b = rig(p, lean, prev, 1 + 0.012*lean/6.0); prev = lean
    if i: c.alpha_composite(fxl('back', i), (ox-X0, oy-Y0))
    c.alpha_composite(b, (-X0, -Y0))
    if i: c.alpha_composite(fxl('front', i), (ox-X0, oy-Y0))
    outs.append(c)
(B/'frames').mkdir(exist_ok=True)
for k, c in enumerate(outs): c.save(B/'frames'/f'{k+1:02d}.png')
g = []
for c in outs:
    bg = Image.new('RGBA', c.size, (90,90,100,255)); bg.alpha_composite(c); g.append(bg.convert('P', palette=Image.ADAPTIVE))
g[0].save(B/'preview.gif', save_all=True, append_images=g[1:], duration=66, loop=0, disposal=2)
cols = 7; rows = -(-len(outs)//cols); sh = Image.new('RGBA', (W*cols, H*rows), (90,90,100,255))
for k, c in enumerate(outs): sh.alpha_composite(c, ((k%cols)*W, (k//cols)*H))
sh.save(B/'sheet.png'); print(W, H, len(outs))
