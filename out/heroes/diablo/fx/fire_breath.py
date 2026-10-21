"""diablo fire breath fx v03: stream of flat vector flame licks with hooked curling tips, from the mouth, facing right.
Layers back to front: soft glow, deep red, orange (with deep-red pockets), yellow, pale core; thin embers. Free, no model.
Usage: python out/heroes/diablo/fx/fire_breath.py <out_dir>
Canvas 380x340 @2x, mouth pivot (40,170); 30 frames @15 fps: grow 0-5, sustain 6-24, shrink 25-29."""
import sys, os, math
from PIL import Image, ImageDraw, ImageFilter
W, H, MX, MY, N, SS = 380, 340, 40, 170, 30, 4
RED, ORANGE, YELLOW, PALE, EDGE = (205, 40, 8), (255, 105, 8), (255, 185, 25), (255, 234, 150), (130, 20, 0)
def ease(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)
def grow(i): return ease(i / 5) if i < 25 else 1 - ease((i - 24) / 5)
def P(x, y): return ((MX + x) * SS, (MY + y) * SS)

def lick(x0, y0, th0, length, w0, curl, cs, ph, k, steps=26):
    pts = [(x0, y0, th0)]; x, y = x0, y0
    L, R = [], []
    for j in range(steps + 1):
        t = j / steps
        th = th0 + curl * max(0, (t - cs) / (1 - cs)) ** 2 + .16 * math.sin(ph * 1.5 + t * 5 + k * 1.7)
        if j: x += math.cos(th) * length / steps; y += math.sin(th) * length / steps
        w = w0 * (1 - t) ** .8 * (1 + .3 * math.sin(math.pi * t)) * min(1, .12 + t * 5)
        nx, ny = -math.sin(th), math.cos(th)
        L.append((x + nx * w, y + ny * w)); R.append((x - nx * w, y - ny * w))
    return L + R[::-1]

import random
NSLOT = 18
def params(k, c):
    r = random.Random(k * 7919 + c * 104729 + 17)
    x = r.uniform(0, 210); y = r.uniform(-34, 34) * (.4 + x / 210)
    th = max(-1.35, min(1.25, r.gauss(-.05, .6) - .25 * (y / 34)))
    ln = r.uniform(60, 210) * (1 - .3 * x / 210); w = r.uniform(13, 30)
    cu = r.choice((-1, 1, -1)) * r.uniform(.8, 2.6) ; cs = r.uniform(.25, .6)
    return x, y, th, ln, w, cu, cs

def licks_at(i, nslots):
    out = []
    for k in range(nslots):
        T = 6 + (k * 5) % 7; off = (k * 3) % T
        c, u = divmod(i + off, T); u = u / T
        x, y, th, ln, w, cu, cs = params(k, c)
        e = math.sin(math.pi * u) ** .7
        out.append((x, y, th + .25 * math.sin(u * 3 + k), ln * (.35 + .65 * e), w * (.4 + .6 * e), cu * (.5 + .5 * e), cs, k))
    return out

def layer(d, i, s, ph, col, nslots, pocket=None):
    g = grow(i)
    if g * s < .05: return
    for (x, y, th, ln, w, cu, cs, k) in licks_at(i, nslots):
        sh = lick(x * s * g, y * s * g, th, ln * s * g, w * s * (.45 + .55 * g), cu, cs, ph + s * 2, k)
        d.polygon([P(a, b) for a, b in sh], fill=col)
    r = 34 * s * (.45 + .55 * g)
    x1, y1 = P(40 * s * g - 1.7 * r, -r); x2, y2 = P(40 * s * g + 1.7 * r, r); d.ellipse([x1, y1, x2, y2], fill=col)
    if pocket:
        for k in range(5):
            u = (ph * .07 + k * .21) % 1.0; cx = (50 + 190 * u) * s * g; cy = 24 * math.sin(k * 2.1 + ph * .6) * s * u
            rr = (8 - 5 * u) * s * g * (1 + .5 * math.sin(k + ph))
            if rr > .8:
                x1, y1 = P(cx - rr * 1.4, cy - rr); x2, y2 = P(cx + rr * 1.4, cy + rr); d.ellipse([x1, y1, x2, y2], fill=pocket)

def frame(i):
    ph = i * .9; g = grow(i)
    glow = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    layer(gd, i, 1.05, ph, (255, 120, 20, 255), 10)
    glow = glow.filter(ImageFilter.GaussianBlur(9 * SS)); a = glow.getchannel('A').point(lambda v: int(v * .35)); glow.putalpha(a)
    im = glow; d = ImageDraw.Draw(im)
    layer(d, i, 1.0, ph, RED, 18)
    layer(d, i, .86, ph + 1.0, ORANGE, 14, RED)
    layer(d, i, .6, ph + 2.0, YELLOW, 9)
    layer(d, i, .3, ph + 3.0, PALE, 5)
    for k in range(7):
        u = (i * .05 + k * .14) % 1.0; x = (120 + 260 * u) * g; y = -30 * u - 18 * math.sin(k * 2.7 + i * .2) * u
        r = (3.2 * (1 - u) + 1.2) * SS; cx, cy = P(x, y)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=YELLOW if k % 2 else ORANGE)
    return im.resize((W, H), Image.LANCZOS)

out = sys.argv[1]; os.makedirs(out + '/frames', exist_ok=True)
fr = [frame(i) for i in range(N)]
for k, f in enumerate(fr): f.save(f'{out}/frames/{k:03d}.png')
bg = []
for f in fr:
    b = Image.new('RGBA', f.size, (30, 30, 36, 255)); b.alpha_composite(f); bg.append(b.convert('P', palette=Image.ADAPTIVE))
bg[0].save(out + '/preview.gif', save_all=True, append_images=bg[1:], duration=67, loop=0)
sheet = Image.new('RGB', (W // 2 * 6, H // 2 * 2))
for k, i in enumerate((0, 2, 4, 6, 10, 15, 20, 24, 26, 28, 29, 12)):
    t = Image.new('RGBA', (W, H), (30, 30, 36, 255)); t.alpha_composite(fr[i]); sheet.paste(t.convert('RGB').resize((W // 2, H // 2)), ((k % 6) * W // 2, (k // 6) * H // 2))
sheet.save(out + '/sheet.png'); print(N, 'frames ->', out)
