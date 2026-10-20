"""Python-drawn ground ripple (shockwave from the buried sword) over the body-only holy banner clip. Free, no model.
Usage: python holy_banner_ripple.py <body_clip.mp4> <out_dir>
Measured on raw/skill_side_skill_holy_banner_v4_t01: sword point at (475, 455) in the 832x480 frame, impact at frame 32 (15 fps),
body height ~425 px. Rings are drawn on the ground plane (ellipse, ry = 0.2 rx); the half behind the sword is drawn behind the
body, the front half in front, so the rings wrap the legs. Colour + opacity only, screen blend. Recipe: docs/python-fx-recipe.md."""
import sys, os, subprocess, glob, tempfile
sys.path.insert(0, 'scripts')
from sprite_pack import key_out
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

W, H = 1240, 680
OX, OY = 200, 80                       # where the 832x480 clip frame sits on the canvas
POINT = (475 + OX, 455 + OY)           # sword point on the ground, canvas coordinates
IMPACT = 32
BODY = 425
BG = np.array([58, 74, 64], np.float32) / 255
CREAM, GOLD, WHITE, AMBER = (1, .957, .784), (1, .788, .235), (1, 1, .94), (1, .62, .15)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def ramp(t, a, b): return min(1.0, max(0.0, (t - a) / float(b - a)))
def paintL(fn, blur=0):
    im = Image.new('L', (W, H), 0); fn(ImageDraw.Draw(im))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, np.float32) / 255
def radial(cx, cy, rx, ry, p=1.4):
    return np.clip(1 - np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2), 0, 1) ** p
def ring(cx, cy, rx, width, blur):
    ry = rx * .2
    return paintL(lambda d: d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=255, width=max(1, int(width))), blur)
def screen(c, col, a):
    a = np.clip(a, 0, 1)[..., None]; return 1 - (1 - c) * (1 - np.array(col, np.float32) * a)

RINGS = ((0, CREAM, 1.00, 15), (3, GOLD, .95, 16), (6, AMBER, .85, 17), (9, CREAM, .5, 18))   # (delay, colour, strength, length)

def layers(i):
    """returns (back, front): lists of (colour, alpha) with the ground-plane layers split at the sword point."""
    t = i - IMPACT; back, front = [], []
    if t < 0: return back, front
    split = (yy < POINT[1]).astype(np.float32)               # upper half of each ellipse is behind the sword
    for delay, col, k, ln in RINGS:
        u = ramp(t - delay, 0, ln)
        if not (0 < u < 1): continue
        rx = (.10 + 1.0 * u ** .85) * BODY
        a = ring(POINT[0], POINT[1], rx, 34 * (1 - u) + 6, 8) * k * 1.35 * (1 - u) ** .9
        back.append((col, a * split)); front.append((col, a * (1 - split)))
        disc = radial(POINT[0], POINT[1], rx * .95, rx * .19, 1.2) * .42 * (1 - u) * (1 if delay == 0 else .6)
        back.append((GOLD, disc * split)); front.append((GOLD, disc * (1 - split)))
    f = max(0.0, 1 - t / 5.0)                                   # impact flash on the point, 5 frames
    if f > 0:
        front.append((WHITE, radial(POINT[0], POINT[1] - 14, 90, 46, 1.5) * .95 * f))
        front.append((GOLD, radial(POINT[0], POINT[1], 170, 60, 1.2) * .55 * f))
    return back, front

def clean(body, i):
    """the model drew a pink-white splash right of the sword from frame 31; the body never goes past x 540 or below y 459 once kneeling."""
    if i >= 31:
        a = np.array(body); a[:, 540:, 3] = 0; a[459:, :, 3] = 0
        if i >= 32: a[:98, :, 3] = 0           # a thin streak of the lifted blade stays above the head for a frame
        return Image.fromarray(a, 'RGBA')
    return body

def render(frames):
    out = []
    for i, body in enumerate(frames):
        body = clean(body, i); c = np.tile(BG, (H, W, 1)).astype(np.float32)
        back, front = layers(i)
        for col, a in back: c = screen(c, col, a)
        full = Image.new('RGBA', (W, H), (0, 0, 0, 0)); full.alpha_composite(body, (OX, OY))
        a = np.asarray(full, np.float32) / 255
        c = c * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
        for col, al in front: c = screen(c, col, al)
        out.append(Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)))
    return out

if __name__ == '__main__':
    mp4, outd = sys.argv[1], sys.argv[2]; os.makedirs(outd, exist_ok=True)
    d = tempfile.mkdtemp(prefix='hbfr_'); subprocess.run(['ffmpeg', '-v', 'error', '-i', mp4, '-vf', 'fps=15', d + '/%03d.png'], check=True)
    frames = [key_out(Image.open(f).convert('RGBA')) for f in sorted(glob.glob(d + '/*.png'))]; print(len(frames), 'frames')
    fr = render(frames); fd = outd + '/frames'; os.makedirs(fd, exist_ok=True)
    for k, im in enumerate(fr): im.save(f'{fd}/{k:03d}.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '15', '-i', fd + '/%03d.png', '-vf', 'scale=720:-2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', outd + '/py_ripple.mp4'], check=True)
    s = Image.new('RGB', (310 * 6, 170 * 2))
    for c, i in enumerate([30, 32, 34, 37, 41, 46, 33, 36, 39, 43, 50, 60]):
        s.paste(fr[i].resize((310, 170)), ((c % 6) * 310, (c // 6) * 170))
    s.save(outd + '/sheet_py.png')
