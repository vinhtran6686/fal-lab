"""Python-drawn light thrust for radiant_slash (body clip + free fx, no model).
Usage: python radiant_slash_beam.py <body_clip.mp4> <out_dir>
Measured on raw/skill_side_skill_radiant_slash_v2_t01 (15 fps, 67 frames, 832x480): the sword is drawn at frames 6-18, held
level and pulled in at 21-38, thrust at 39-43, full extension at frame 43 with the point at (803, 202.5), held to the end.
Layers: a gold glow gathering at the blade point while the sword is pulled in, then at frame 43 a horizontal beam (white core,
gold body, faint outer glow) that shoots to the right edge and fades, two expanding rings and a flash at the point, and two
soft aura waves leaving the whole silhouette (sword included). Colour + opacity only, screen blend. Recipe: docs/python-fx-recipe.md."""
import sys, os, subprocess, glob, tempfile
sys.path.insert(0, 'scripts')
from sprite_pack import key_out
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

W, H = 1500, 600
OX, OY = 100, 60                       # where the 832x480 clip frame sits on the canvas
TIP = (803 + OX, 202.5 + OY)           # blade point at full extension, canvas coordinates
HIT = 43                               # frame of full extension
BODY = 425
BG = np.array([58, 74, 64], np.float32) / 255
CREAM, GOLD, WHITE, AMBER = (1, .957, .784), (1, .788, .235), (1, 1, .94), (1, .62, .15)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def ramp(t, a, b): return min(1.0, max(0.0, (t - a) / float(b - a)))
def radial(cx, cy, rx, ry, p=1.4): return np.clip(1 - np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2), 0, 1) ** p
def paintL(fn, blur=0):
    im = Image.new('L', (W, H), 0); fn(ImageDraw.Draw(im))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(blur)) if blur else im, np.float32) / 255
def ring(cx, cy, r, width, blur): return paintL(lambda d: d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=255, width=max(1, int(width))), blur)
def screen(c, col, a):
    a = np.clip(a, 0, 1)[..., None]; return 1 - (1 - c) * (1 - np.array(col, np.float32) * a)

def silhouette(body):
    a = Image.new('L', (W, H), 0); a.paste(body.getchannel('A'), (OX, OY)); return a
def aura(sil, grow, blur):
    wide = np.asarray(sil.filter(ImageFilter.GaussianBlur(max(1.0, grow * .75))), np.float32) / 255
    d = Image.fromarray((np.clip(wide * 2.6, 0, 1) * 255).astype(np.uint8), 'L')
    return np.asarray(d.filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255

def tip_of(body):
    a = np.array(body)[:, :, 3] > 128; ys, xs = np.nonzero(a); xm = xs.max()
    return xm + OX, ys[xs > xm - 5].mean() + OY

def fx(i, body, sil):
    """returns (back, front) layer lists of (colour, alpha)."""
    back, front = [], []
    t = i - HIT
    # 1. gold glow gathering at the blade point while the sword is pulled in (frames 21-38)
    g = ramp(i, 21, 38) * (1 - ramp(i, 38, 41))
    if g > 0:
        tx, ty = tip_of(body); front.append((GOLD, radial(tx, ty, 70 + 40 * g, 70 + 40 * g, 1.2) * .75 * g))
    if t < 0: return back, front
    # 2. the beam: white core, gold body, faint outer glow, shoots right and fades
    env = ramp(t, 0, 2) * (1 - ramp(t, 12, 22))
    if env > 0:
        reach = ramp(t, 0, 4) * (W - TIP[0]); dx = xx - TIP[0]; dy = yy - TIP[1]
        front_mask = np.clip((reach - dx) / 60.0, 0, 1) * (dx > -10)
        fall = np.clip(1 - np.clip(dx, 0, None) / (W - TIP[0]), 0, 1) ** .5
        wv = 1 + .12 * np.sin(t * 1.3)
        core = np.exp(-(dy / (7 * wv)) ** 2); body_ = np.exp(-(dy / (20 * wv)) ** 2); outer = np.exp(-(dy / (52 * wv)) ** 2)
        m = front_mask * fall * env
        front.append((AMBER, outer * m * .35)); front.append((GOLD, body_ * m * .85)); front.append((WHITE, core * m))
    # 3. rings and flash at the point
    for delay, col in ((0, CREAM), (3, GOLD)):
        u = ramp(t - delay, 0, 14)
        if 0 < u < 1: front.append((col, ring(TIP[0], TIP[1], (.10 + .60 * u ** .8) * BODY, 16 * (1 - u) + 3, 6) * .9 * (1 - u)))
    f = max(0.0, 1 - t / 6.0)
    if f > 0:
        front.append((WHITE, radial(TIP[0], TIP[1], 110, 110, 1.4) * f)); front.append((GOLD, radial(TIP[0], TIP[1], 220, 160, 1.2) * .6 * f))
    # 4. two aura waves leaving the silhouette (sword included), behind the body
    for s, col in ((0, GOLD), (4, CREAM)):
        u = ramp(t - s, 0, 14)
        if 0 < u < 1: back.append((col, aura(sil, 4 + 50 * u ** .7, 8 + 10 * u) * .8 * (1 - u) ** 1.2))
    return back, front

def render(frames, scale=1.0):
    """scale = 15 / source fps: the beats above are counted in 15 fps frames, so a 24 fps source passes 0.625."""
    out = []
    for i, body in enumerate(frames):
        sil = silhouette(body); c = np.tile(BG, (H, W, 1)).astype(np.float32)
        back, front = fx(i * scale, body, sil)
        for col, a in back: c = screen(c, col, a)
        full = Image.new('RGBA', (W, H), (0, 0, 0, 0)); full.alpha_composite(body, (OX, OY))
        a = np.asarray(full, np.float32) / 255
        c = c * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
        for col, al in front: c = screen(c, col, al)
        out.append(Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)))
    return out

if __name__ == '__main__':
    mp4, outd = sys.argv[1], sys.argv[2]; os.makedirs(outd, exist_ok=True)
    d = tempfile.mkdtemp(prefix='rsfr_'); subprocess.run(['ffmpeg', '-v', 'error', '-i', mp4, '-vf', 'fps=15', d + '/%03d.png'], check=True)
    frames = [key_out(Image.open(f).convert('RGBA')) for f in sorted(glob.glob(d + '/*.png'))]; print(len(frames), 'frames')
    fr = render(frames); fd = outd + '/frames'; os.makedirs(fd, exist_ok=True)
    for k, im in enumerate(fr): im.save(f'{fd}/{k:03d}.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '15', '-i', fd + '/%03d.png', '-vf', 'scale=900:-2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', outd + '/py_beam.mp4'], check=True)
    s = Image.new('RGB', (375 * 4, 150 * 3))
    for c, i in enumerate([30, 37, 41, 43, 44, 46, 48, 51, 54, 57, 60, 66]):
        s.paste(fr[i].resize((375, 150)), ((c % 4) * 375, (c // 4) * 150))
    s.save(outd + '/sheet_py.png')
