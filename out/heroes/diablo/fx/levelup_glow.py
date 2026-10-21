"""diablo levelup fx: soft ember glow pulsing around the still master pose (free, no model).
Based on holy_commander levelup v03 (docs/python-fx-recipe.md). Usage: python out/heroes/diablo/fx/levelup_glow.py <out_dir>"""
import sys, os, subprocess, math
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'out/heroes/holy_commander/fx')
import levelup_variants as L
from sprite_pack import key_out
from PIL import Image
import numpy as np

N = 30                                   # 2 s at 15 fps
EMBER, YELLOW, PALE, HOT = (1, .5, .1), (1, .82, .2), (1, .93, .62), (1, .66, .12)

body = key_out(Image.open('out/heroes/diablo/design/master_v04.png').convert('RGBA'))
bb = body.getchannel('A').point(lambda v: 255 if v > 128 else 0).getbbox()
body = body.crop(bb)
s = L.BODY / body.height
body = body.resize((round(body.width * s), L.BODY), Image.LANCZOS)
at = (L.FEET[0] - body.width // 2, L.FEET[1] - body.height)
sil = Image.new('L', (L.W, L.H), 0); sil.paste(body.getchannel('A'), at)
full = Image.new('RGBA', (L.W, L.H), (0, 0, 0, 0)); full.alpha_composite(body, at)
fa = np.asarray(full, np.float32) / 255

def draw(i):
    cv = L.Canvas(); e = L.env(i, 2, 8, 20, 29)
    L.ground(cv, e, .9, .55) if False else cv.screen(YELLOW, L.radial(L.FEET[0], L.FEET[1], .55 * L.BODY, .1 * L.BODY, 1.2), .8 * e)
    for st, col in ((2, YELLOW), (7, PALE), (12, HOT)):
        t = L.ramp(i, st, st + 12)
        if 0 < t < 1: cv.screen(col, L.aura(sil, 4 + 56 * t ** .7, 8 + 12 * t), .85 * (1 - t) ** 1.2)
    cv.screen(EMBER, L.aura(sil, 8, 12), .45 * e)
    cv.screen(YELLOW, L.motes(i, 14, 3, .3 * L.BODY, 4, 6, 4, jitter=.8), .8 * e)
    cv.c = cv.c * (1 - fa[..., 3:4]) + fa[..., :3] * fa[..., 3:4]
    cv.screen(PALE, L.rimlight(sil, 1.0), .8 * e)
    return cv.img()

out = sys.argv[1]; os.makedirs(out + '/frames', exist_ok=True)
fr = [draw(i) for i in range(N)]
for k, im in enumerate(fr): im.save(f'{out}/frames/{k:03d}.png')
fr[0].save(f'{out}/preview.gif', save_all=True, append_images=fr[1:], duration=67, loop=0)
W2, H2 = L.W // 3, L.H // 3
sheet = Image.new('RGB', (W2 * 6, H2 * 2))
for k, i in enumerate(range(0, N, 3)): sheet.paste(fr[i].resize((W2, H2)), ((k % 6) * W2, (k // 6) * H2))
sheet.save(out + '/sheet.png'); print(N, 'frames ->', out)
