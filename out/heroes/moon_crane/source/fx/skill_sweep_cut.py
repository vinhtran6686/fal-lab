"""moon_crane skill_sweep: cut 3 drawings (A start, M mid, C end) from the approved clip skill_sweep_ref_t01.mp4
onto the hero cell (352x280 @2x, feet pivot x 0.5 y 0.88, one body size). Writes frames/skill_sweep/pose_{A,M,C}.png + cut.json."""
import json, subprocess, sys, pathlib, numpy as np
from PIL import Image
ROOT = pathlib.Path('out/heroes/moon_crane'); CLIP = ROOT/'source/video/skill_sweep_ref_t01.mp4'
OUT = ROOT/'frames/skill_sweep'; TMP = pathlib.Path(sys.argv[1]); TMP.mkdir(parents=True, exist_ok=True)
PICK = {'A': 9, 'B': 57}; CELL = (352, 280); PIV = (176, 246); BODY = 120
subprocess.run(['ffmpeg','-y','-v','error','-i',str(CLIP),str(TMP/'f%03d.png')],check=True)
def key(p):
    a = np.array(Image.open(p).convert('RGB')).astype(float)
    bg = np.median(np.concatenate([a[:6,:6].reshape(-1,3), a[:6,-6:].reshape(-1,3), a[-6:,:6].reshape(-1,3), a[-6:,-6:].reshape(-1,3)]), 0)
    d = np.sqrt(((a-bg)**2).sum(-1)); al = np.clip((d-55)/55, 0, 1)
    sp = (a[...,0] > a[...,1]+30) & (a[...,2] > a[...,1]+30) & (al < 1)
    a[sp,0] = np.minimum(a[sp,0], a[sp,1]+10); a[sp,2] = np.minimum(a[sp,2], a[sp,1]+10)
    im = Image.fromarray(np.dstack([a, al*255]).astype('uint8'), 'RGBA'); return im
def feet(im):
    m = np.array(im)[...,3] > 128; h, w = m.shape; ys, xs = np.where(m); bot = ys.max()
    c = m[max(bot-int(h*0.05),0):bot+1].any(0); runs=[]; s=None
    for x, v in enumerate(c):
        if v and s is None: s = x
        if not v and s is not None: runs.append((s,x-1)); s=None
    if s is not None: runs.append((s,w-1))
    runs = [r for r in runs if r[1]-r[0] > 8]; return (runs[0][0]+runs[-1][1])/2, bot
ims = {k: key(TMP/f'f{i:03d}.png') for k, i in PICK.items()}
mA = np.array(ims['A'])[...,3] > 128; ysA, xsA = np.where(mA); S = BODY/(ysA.max()-ysA.min())   # one scale for every drawing
info = {'scale': S, 'cell': CELL, 'pivot': PIV, 'pick': PICK}
for k, im in ims.items():
    fx, fy = feet(im); sc = im.resize((int(im.width*S), int(im.height*S)), Image.LANCZOS)
    cell = Image.new('RGBA', CELL, (0,0,0,0)); cell.alpha_composite(sc, (int(round(PIV[0]-fx*S)), int(round(PIV[1]-fy*S))))
    cell.save(OUT/f'pose_{k}.png'); m = np.array(cell)[...,3] > 128; ys, xs = np.where(m)
    info[k] = {'bbox': [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())], 'left_tip': [int(xs.min()), int(ys[xs==xs.min()].mean())], 'right_tip': [int(xs.max()), int(ys[xs==xs.max()].mean())]}
json.dump(info, open(OUT/'cut.json','w'), indent=1); print(json.dumps(info))
