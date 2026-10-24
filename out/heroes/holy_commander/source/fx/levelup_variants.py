"""FINAL for holy_commander levelup: v03 (user choice 2026-10-20). Recipe: docs/python-fx-recipe.md.
Ten Python-drawn fx variants for levelup (free, no model). Every variant is drawn over the same clean body clip.
Usage: python levelup_variants.py <body_clip.mp4> <out_dir> [variant ...]
Colour + opacity layers only (soft, wide); no outlines, no small busy particles unless the variant is about them."""
import sys, os, subprocess, glob, math, random, tempfile
sys.path.insert(0, 'scripts')
from sprite_pack import key_out
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

W, H = 700, 720
FEET = (350, 630)
BODY = 425                     # body height in clip px
BODY_AT = (370, 453)           # feet position inside the 832x480 clip frame
BG = np.array([58, 74, 64], np.float32) / 255
CREAM, GOLD, WHITE, AMBER = (1, .957, .784), (1, .788, .235), (1, 1, .94), (1, .62, .15)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def ramp(i, a, b): return min(1.0, max(0.0, (i - a) / float(b - a)))
def env(i, a, full, hold, end): return ramp(i, a, full) * (1 - ramp(i, hold, end))

def paintL(fn, blur=0):
    im = Image.new('L', (W, H), 0); fn(ImageDraw.Draw(im))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, np.float32) / 255

def radial(cx, cy, rx, ry=None, p=1.5):
    ry = ry or rx
    return np.clip(1 - np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2), 0, 1) ** p

def capsule(w, h, cx=None, soft=9):
    cx = FEET[0] if cx is None else cx
    m = paintL(lambda d: d.rounded_rectangle((cx - w / 2, FEET[1] - h, cx + w / 2, FEET[1] + 8), radius=w / 2, fill=255), soft)
    return m

def ring(cx, cy, rx, ry, width, blur=4):
    return paintL(lambda d: d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=255, width=max(1, int(width))), blur)

def star(cx, cy, r, ang=0, spikes=4):
    def f(d):
        pts = []
        for k in range(spikes * 2):
            a = ang + k * math.pi / spikes; rr = r if k % 2 == 0 else r * 0.14
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=255)
    return np.maximum(paintL(f, 1.5), radial(cx, cy, r * .55, p=2.0) * .8)

def motes(i, n, seed, x_half, t0, speed, size, rise=1.0, top=None, jitter=0.6):
    rnd = random.Random(seed); pts = []
    for k in range(n):
        x = FEET[0] + rnd.uniform(-x_half, x_half); y0 = FEET[1] - rnd.uniform(0, .25 * BODY)
        delay = rnd.uniform(0, 14); sp = speed * rnd.uniform(.7, 1.3); sz = size * rnd.uniform(.6, 1.5)
        life = rnd.uniform(14, 26); ph = rnd.uniform(0, 6.28)
        age = i - t0 - delay
        if age < 0 or age > life: continue
        y = y0 - sp * age * rise; x += math.sin(ph + age * .3) * 10 * jitter
        a = math.sin(math.pi * age / life) * (0.6 + 0.4 * math.sin(age * 1.3 + ph))
        pts.append((x, y, sz, a))
    def f(d):
        for x, y, sz, a in pts: d.ellipse((x - sz, y - sz, x + sz, y + sz), fill=int(255 * max(0, min(1, a))))
    return paintL(f, 2.0)

class Canvas:
    def __init__(self): self.c = np.tile(BG, (H, W, 1)).astype(np.float32)
    def normal(self, col, a, k=1.0):
        a = np.clip(a * k, 0, 1)[..., None]; self.c = self.c * (1 - a) + np.array(col, np.float32) * a
    def screen(self, col, a, k=1.0):
        a = np.clip(a * k, 0, 1)[..., None]; self.c = 1 - (1 - self.c) * (1 - np.array(col, np.float32) * a)
    def img(self): return Image.fromarray((np.clip(self.c, 0, 1) * 255).astype(np.uint8))

def sil_of(body):                    # body silhouette (0..1) on the canvas
    a = Image.new('L', (W, H), 0); a.paste(body.getchannel('A'), (FEET[0] - BODY_AT[0], FEET[1] - BODY_AT[1]))
    return a

def aura(sil, grow, blur):
    """Round halo around the silhouette: blur wide then lift, so the edge stays round (a square MaxFilter gave boxy halos)."""
    wide = np.asarray(sil.filter(ImageFilter.GaussianBlur(max(1.0, grow * .75))), np.float32) / 255
    d = Image.fromarray((np.clip(wide * 2.6, 0, 1) * 255).astype(np.uint8), 'L')
    return np.asarray(d.filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255

def rimlight(sil, k=1.0):
    s = np.asarray(sil, np.float32) / 255
    inner = np.asarray(sil.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(5)), np.float32) / 255
    return np.clip(s - inner, 0, 1) * k

def ground(cv, e, k=1.0, wide=.5):
    cv.screen(GOLD, radial(FEET[0], FEET[1], wide * BODY, .1 * BODY, 1.2), .85 * e * k)

def beam(cv, e, w=.30, k=.5):
    wpx = w * BODY; bot = FEET[1] - .78 * BODY
    m = paintL(lambda d: d.rectangle((FEET[0] - wpx / 2, 0, FEET[0] + wpx / 2, bot), fill=255), 14)
    g = np.clip((yy) / bot, 0, 1) ** 1.2
    cv.screen(CREAM, m * g, k * e)

def flash_fist(cv, i, t, k=.9, r=.42):
    e = max(0, 1 - abs(i - t) / 4.0)
    if e > 0: cv.screen(WHITE, radial(FEET[0] - .08 * BODY, FEET[1] - .93 * BODY, r * BODY, p=1.6), e * k)

# ---------- variants: each returns (back_fn, front_fn) taking (cv, i, body, sil) ----------
def V01(cv, i, body, sil, front):          # column + wide ripples + body aura + rim light
    e = env(i, 18, 24, 31, 40)
    if not front:
        ground(cv, e, 1.0, .58)
        for s in (19, 23, 27):
            t = ramp(i, s, s + 11)
            if 0 < t < 1: cv.screen(GOLD, ring(FEET[0], FEET[1], (.2 + .7 * t) * BODY, (.2 + .7 * t) * .17 * BODY, 10, 6), .9 * (1 - t))
        cv.screen(GOLD, aura(sil, 14, 16), .55 * e)
    else:
        h = .98 * BODY * (.35 + .65 * ramp(i, 18, 24)); c = capsule(.9 * BODY, h, soft=12)
        t = np.clip((yy - (FEET[1] - h)) / h, 0, 1)
        cv.screen(CREAM, c * (.16 + .34 * t), e)
        cv.screen(GOLD, np.clip(c - capsule(.9 * BODY - 30, h - 30, soft=14), 0, 1), .8 * e)
        cv.screen(CREAM, rimlight(sil, 1.0), .7 * e); beam(cv, e)

def V02(cv, i, body, sil, front):          # rising light streaks inside a faint column
    e = env(i, 18, 24, 31, 40); rnd = random.Random(5)
    if not front:
        ground(cv, e, 1.0, .6)
    else:
        h = .98 * BODY; c = capsule(.85 * BODY, h, soft=12)
        cv.screen(CREAM, c * .18, e)
        for k in range(16):
            x = FEET[0] + rnd.uniform(-.38, .38) * BODY; w = rnd.uniform(9, 20); L = rnd.uniform(.3, .7) * BODY
            sp = rnd.uniform(9, 18); ph = rnd.uniform(0, 60)
            y = FEET[1] - ((i * sp + ph) % (h + L)) + L * 0 
            m = paintL(lambda d: d.rounded_rectangle((x - w / 2, y - L, x + w / 2, y), radius=w / 2, fill=255), 3)
            tt = np.clip((yy - (y - L)) / L, 0, 1)
            cv.screen(CREAM if k % 3 else GOLD, m * c * tt, 1.6 * e)
        cv.screen(CREAM, rimlight(sil), .6 * e); beam(cv, e, .34, .45)

def V03(cv, i, body, sil, front):          # silhouette aura pulses (3 waves) + ripple + flash
    e = env(i, 18, 24, 32, 41)
    if not front:
        ground(cv, e, .9, .55)
        for s, col in ((19, GOLD), (23, CREAM), (27, AMBER)):
            t = ramp(i, s, s + 13)
            if 0 < t < 1: cv.screen(col, aura(sil, 4 + 56 * t ** .7, 8 + 12 * t), .85 * (1 - t) ** 1.2)
        cv.screen(GOLD, aura(sil, 8, 12), .45 * e)
    else:
        cv.screen(CREAM, rimlight(sil, 1.0), .8 * e); flash_fist(cv, i, 22, .7)

def V04(cv, i, body, sil, front):          # holy rays + halo behind the head + cross sparkle at the fist
    e = env(i, 18, 24, 32, 41); cx, cy = FEET[0], FEET[1] - .55 * BODY
    if not front:
        ground(cv, e, .9, .55)
        ang0 = i * .035
        def rays(d):
            for k in range(14):
                a = ang0 + k * 2 * math.pi / 14; R = 1.15 * BODY; wd = .09
                d.polygon([(cx, cy), (cx + R * math.cos(a - wd), cy + R * math.sin(a - wd)), (cx + R * math.cos(a + wd), cy + R * math.sin(a + wd))], fill=255)
        r = paintL(rays, 5) * radial(cx, cy, 1.15 * BODY, p=.8)
        cv.screen(CREAM, r, .42 * e)
        cv.screen(GOLD, ring(FEET[0] + 10, FEET[1] - .72 * BODY, .3 * BODY, .3 * BODY, 14, 5), .75 * e)
        cv.screen(GOLD, aura(sil, 10, 14), .4 * e)
    else:
        cv.screen(CREAM, rimlight(sil), .6 * e)
        s = ramp(i, 20, 25) * (1 - ramp(i, 33, 40))
        if s > 0: cv.screen(WHITE, star(FEET[0] - .08 * BODY, FEET[1] - .95 * BODY, .3 * BODY * (.7 + .3 * math.sin(i * .5)), math.pi / 4 * 0), s)
        flash_fist(cv, i, 22, .5)

def V05(cv, i, body, sil, front):          # shockwave: three wide ground waves + flash + falling sparks
    e = env(i, 18, 22, 32, 41)
    if not front:
        ground(cv, e, 1.0, .7)
        for s in (20, 23, 26):
            t = ramp(i, s, s + 12)
            if 0 < t < 1:
                R = (.15 + 1.0 * t) * BODY
                cv.screen(CREAM if s != 23 else GOLD, ring(FEET[0], FEET[1], R, R * .2, 18 * (1 - t) + 4, 8), .95 * (1 - t))
        cv.screen(GOLD, aura(sil, 9, 14), .4 * e)
    else:
        flash_fist(cv, i, 22, .95, .55); cv.screen(CREAM, rimlight(sil), .75 * e)
        cv.screen(GOLD, motes(i, 22, 11, .6 * BODY, 21, -7, 6, jitter=.2) * 0 + motes(i, 22, 11, .55 * BODY, 21, 5, 6.5, jitter=.3), .9)

def V06(cv, i, body, sil, front):          # two spirals of light motes + faint column
    e = env(i, 17, 24, 32, 41)
    def helix(fr):
        def f(d):
            for strand in range(2):
                for k in range(26):
                    t = (i * .045 + k * .035) % 1.0; y = FEET[1] - t * 1.05 * BODY
                    a = i * .22 + k * .5 + strand * math.pi; depth = math.cos(a)
                    if (depth >= 0) != fr: continue
                    x = FEET[0] + math.sin(a) * .42 * BODY * (.75 + .25 * t); r = (13 - 6 * t) * (.8 + .3 * depth)
                    al = math.sin(math.pi * t) ** .7 * (.55 + .45 * abs(depth))
                    d.ellipse((x - r, y - r, x + r, y + r), fill=int(255 * al))
        return paintL(f, 2.2)
    if not front:
        ground(cv, e, 1.0, .6); cv.screen(CREAM, capsule(.9 * BODY, .98 * BODY, soft=14), .12 * e); cv.screen(GOLD, helix(False), e)
    else:
        cv.screen(GOLD, helix(True), e); cv.screen(CREAM, rimlight(sil), .6 * e); beam(cv, e, .24, .35)

def V07(cv, i, body, sil, front):          # wide pillar of light from the sky + splash + rising motes
    e = env(i, 17, 22, 33, 42)
    if not front:
        ground(cv, e, 1.1, .7)
        for s in (20, 25):
            t = ramp(i, s, s + 12)
            if 0 < t < 1: cv.screen(CREAM, ring(FEET[0], FEET[1], (.2 + .8 * t) * BODY, (.2 + .8 * t) * .2 * BODY, 12, 7), .7 * (1 - t))
    else:
        w = (.95 + .08 * math.sin(i * .6)) * BODY
        m = paintL(lambda d: d.rectangle((FEET[0] - w / 2, 0, FEET[0] + w / 2, FEET[1]), fill=255), 22)
        g = np.clip(1 - np.abs(xx - FEET[0]) / (w / 2), 0, 1) ** .6
        top = ramp(i, 17, 21) * 1.0
        cv.screen(CREAM, m * g * (.18 + .5 * np.clip((yy / FEET[1]), 0, 1) ** 1.5), e * top)
        cv.screen(WHITE, motes(i, 26, 21, .4 * BODY, 20, 7, 5.5) , e); cv.screen(CREAM, rimlight(sil), .7 * e)

def V08(cv, i, body, sil, front):          # four soft halo rings rising from the feet over the head
    e = env(i, 17, 23, 33, 42)
    if not front:
        ground(cv, e, 1.0, .6); cv.screen(CREAM, capsule(.9 * BODY, .98 * BODY, soft=16), .12 * e)
    else:
        for k in range(4):
            t = ramp(i, 18 + k * 3.5, 18 + k * 3.5 + 14)
            if 0 < t < 1:
                y = FEET[1] - t * 1.05 * BODY; rx = (.46 - .1 * t) * BODY
                cv.screen(GOLD if k % 2 == 0 else CREAM, ring(FEET[0], y, rx, rx * .25, 14 * (1 - .4 * t), 5), .9 * math.sin(math.pi * t) ** .8)
        cv.screen(CREAM, rimlight(sil), .6 * e); beam(cv, e, .28, .4)

def V09(cv, i, body, sil, front):          # banded column: light bands travel upward + wide base disk
    e = env(i, 18, 24, 32, 41)
    if not front:
        ground(cv, e, 1.1, .75)
        for s in (19, 24):
            t = ramp(i, s, s + 12)
            if 0 < t < 1: cv.screen(GOLD, ring(FEET[0], FEET[1], (.2 + .85 * t) * BODY, (.2 + .85 * t) * .2 * BODY, 14, 7), .8 * (1 - t))
        cv.screen(GOLD, aura(sil, 16, 22), .5 * e)
    else:
        h = .98 * BODY * (.4 + .6 * ramp(i, 18, 24)); c = capsule(.82 * BODY, h, soft=14)
        band = .5 + .5 * np.sin((FEET[1] - yy) / 26.0 - i * .9)
        t = np.clip((yy - (FEET[1] - h)) / h, 0, 1)
        cv.screen(CREAM, c * (.10 + .30 * t) * (.55 + .6 * band), e)
        cv.screen(GOLD, np.clip(c - capsule(.82 * BODY - 26, h - 26, soft=14), 0, 1), .7 * e)
        cv.screen(CREAM, rimlight(sil), .6 * e); beam(cv, e)

def V10(cv, i, body, sil, front):          # everything, layered: ground, ripples, aura waves, column, motes, rays, flash, beam
    e = env(i, 17, 24, 32, 41); cx, cy = FEET[0], FEET[1] - .55 * BODY
    if not front:
        ground(cv, e, 1.1, .7)
        ang0 = i * .03
        def rays(d):
            for k in range(12):
                a = ang0 + k * 2 * math.pi / 12
                d.polygon([(cx, cy), (cx + 1.1 * BODY * math.cos(a - .08), cy + 1.1 * BODY * math.sin(a - .08)), (cx + 1.1 * BODY * math.cos(a + .08), cy + 1.1 * BODY * math.sin(a + .08))], fill=255)
        cv.screen(CREAM, paintL(rays, 6) * radial(cx, cy, 1.1 * BODY, p=.9), .28 * e)
        for s in (19, 23):
            t = ramp(i, s, s + 13)
            if 0 < t < 1: cv.screen(GOLD, ring(FEET[0], FEET[1], (.2 + .9 * t) * BODY, (.2 + .9 * t) * .2 * BODY, 14, 7), .85 * (1 - t))
        for s, col in ((20, GOLD), (25, CREAM)):
            t = ramp(i, s, s + 13)
            if 0 < t < 1: cv.screen(col, aura(sil, 4 + 44 * t ** .7, 8 + 10 * t), .7 * (1 - t) ** 1.2)
        cv.screen(GOLD, aura(sil, 12, 16), .5 * e)
    else:
        h = .98 * BODY * (.35 + .65 * ramp(i, 18, 24)); c = capsule(.86 * BODY, h, soft=12); t = np.clip((yy - (FEET[1] - h)) / h, 0, 1)
        cv.screen(CREAM, c * (.14 + .34 * t), e)
        cv.screen(GOLD, np.clip(c - capsule(.86 * BODY - 28, h - 28, soft=14), 0, 1), .75 * e)
        cv.screen(WHITE, motes(i, 30, 33, .42 * BODY, 19, 6.5, 5), e)
        cv.screen(CREAM, rimlight(sil), .75 * e); beam(cv, e, .3, .5); flash_fist(cv, i, 22, .8)
        s = ramp(i, 21, 25) * (1 - ramp(i, 32, 40))
        if s > 0: cv.screen(WHITE, star(FEET[0] - .08 * BODY, FEET[1] - .95 * BODY, .24 * BODY), s)

VARIANTS = {'v01': (V01, 'Cột sáng + sóng lan'), 'v02': (V02, 'Vệt sáng bay lên'), 'v03': (V03, 'Hào quang xung nhịp'),
            'v04': (V04, 'Tia thánh + vầng sáng'), 'v05': (V05, 'Sóng xung kích'), 'v06': (V06, 'Hai vòng xoắn sáng'),
            'v07': (V07, 'Trụ sáng từ trời'), 'v08': (V08, 'Vòng sáng bay lên'), 'v09': (V09, 'Cột sáng có dải chạy'), 'v10': (V10, 'Tổng hợp')}

def load_frames(mp4):
    d = tempfile.mkdtemp(prefix='lvfr_')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', mp4, '-vf', 'fps=15', d + '/%03d.png'], check=True)
    return [key_out(Image.open(f).convert('RGBA')) for f in sorted(glob.glob(d + '/*.png'))]

def render(fn, frames):
    out = []
    for i, body in enumerate(frames):
        sil = sil_of(body); cv = Canvas()
        fn(cv, i, body, sil, False)
        cv.normal(np.zeros(3), np.zeros((H, W)))   # no-op, keeps the order explicit
        full = Image.new('RGBA', (W, H), (0, 0, 0, 0)); full.alpha_composite(body, (FEET[0] - BODY_AT[0], FEET[1] - BODY_AT[1]))
        a = np.asarray(full, np.float32) / 255
        cv.c = cv.c * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
        fn(cv, i, body, sil, True); out.append(cv.img())
    return out

if __name__ == '__main__':
    mp4, out = sys.argv[1], sys.argv[2]; names = sys.argv[3:] or list(VARIANTS)
    os.makedirs(out, exist_ok=True); frames = load_frames(mp4); print(len(frames), 'frames')
    for n in names:
        fr = render(VARIANTS[n][0], frames); d = f'{out}/{n}'; os.makedirs(d, exist_ok=True)
        for k, im in enumerate(fr): im.save(f'{d}/{k:03d}.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '15', '-i', d + '/%03d.png', '-vf', 'scale=420:-2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', f'{out}/{n}.mp4'], check=True)
        fr[27].save(f'{out}/{n}_peak.png'); print(n, VARIANTS[n][1])
