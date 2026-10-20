"""Soft light-column fx for levelup, modelled on how the reference hero's levelup wraps the body:
translucent column around the whole body (warm colour, alpha 0.4-0.55, strongest at the feet), thin
rim, short flickering light tongues at the bottom, a tall faded beam above the head, a soft ground
glow behind. Usage: python levelup_soft_glow.py <keyed_frames_dir> <out_dir>  (frames = clip frames, magenta)."""
import sys, glob, random
sys.path.insert(0, 'scripts')
from sprite_pack import key_out
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

W, H = 1020, 800
FEET = (510, 640)           # feet pivot on the canvas
BODY = 425                  # body height in clip px
BODY_AT = (370, 453)        # feet position inside the 832x480 clip frame
T0, T_FULL, T_HOLD, T_END = 18, 24, 31, 40   # frame indices: appears, full, starts fading, gone
CREAM, GOLD, CORE = (255, 244, 200), (255, 201, 60), (255, 246, 180)

def ramp(i, a, b):
    return min(1.0, max(0.0, (i - a) / (b - a)))

def envelope(i):
    return ramp(i, T0, T_FULL) * (1.0 - ramp(i, T_HOLD, T_END))

def layer_size(): return (W, H)

def soft(img, r): return img.filter(ImageFilter.GaussianBlur(r))

def ground_glow(env):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rx, ry = 0.42 * BODY, 0.09 * BODY
    d.ellipse((FEET[0] - rx, FEET[1] - ry, FEET[0] + rx, FEET[1] + ry), fill=GOLD + (int(150 * env),))
    return soft(im, 10)

def column(i, env):
    """Soft capsule of light around the body: feathered edge, a soft bright edge band, rounded flame tongues."""
    grow = ramp(i, T0, T_FULL)
    h = int(0.98 * BODY * (0.35 + 0.65 * grow)); w = int(0.70 * BODY)
    x0, x1, y1 = FEET[0] - w // 2, FEET[0] + w // 2, FEET[1] + 8
    y0 = y1 - h
    mask = Image.new('L', (W, H), 0); d = ImageDraw.Draw(mask)
    d.rounded_rectangle((x0, y0, x1, y1), radius=w // 2, fill=255)          # round top, soft sides
    m_soft = soft(mask, 9)
    inner = soft(mask.filter(ImageFilter.MinFilter(25)), 12)
    edge = np.clip(np.asarray(m_soft, np.float32) - np.asarray(inner, np.float32), 0, 255) / 255.0
    body_m = np.asarray(m_soft, np.float32) / 255.0
    ys = np.arange(H, dtype=np.float32)[:, None]
    t = np.clip((ys - y0) / max(1, h), 0, 1)                                # 0 top .. 1 feet
    fill_a = body_m * (0.20 + 0.42 * t) * env                               # clear at the top, strong at the feet
    edge_a = edge * 0.70 * env
    out = np.zeros((H, W, 4), np.float32)
    out[..., :3] = np.array(CREAM, np.float32)
    out[..., 3] = np.clip(fill_a + edge_a * 0.0, 0, 1)
    im = Image.fromarray((out * np.array([1, 1, 1, 255], np.float32)).astype(np.uint8), 'RGBA')
    ed = np.zeros((H, W, 4), np.float32); ed[..., :3] = np.array(GOLD, np.float32); ed[..., 3] = np.clip(edge_a, 0, 1) * 255
    im.alpha_composite(Image.fromarray(ed.astype(np.uint8), 'RGBA'))
    tg = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(tg)
    rnd = random.Random(i * 7 + 3); n = 6
    for k in range(n):
        cx = x0 + (k + 0.5) * w / n + rnd.uniform(-8, 8)
        th = rnd.uniform(0.16, 0.36) * BODY * (0.4 + 0.6 * grow)
        tw = w / n * 0.95
        d.ellipse((cx - tw / 2, y1 - th, cx + tw / 2, y1 + th * 0.25), fill=GOLD + (int(150 * env),))
        d.ellipse((cx - tw / 4, y1 - th * 0.6, cx + tw / 4, y1 + th * 0.2), fill=CORE + (int(170 * env),))
    tg = soft(tg, 6)
    clip = Image.fromarray((body_m * 255).astype(np.uint8), 'L')
    ta = np.minimum(np.asarray(tg.getchannel('A'), np.float32), np.asarray(clip, np.float32))
    tg.putalpha(Image.fromarray(ta.astype(np.uint8), 'L'))
    im.alpha_composite(tg)
    return im

def beam(i, env):
    w = int(0.26 * BODY); top = 0; bot = FEET[1] - int(0.80 * BODY)
    col = np.zeros((H, W, 4), np.float32)
    ys = np.arange(top, bot)
    a = 0.55 * (ys - top) / max(1, bot - top)         # fades out going up
    x0, x1 = FEET[0] - w // 2, FEET[0] + w // 2
    col[top:bot, x0:x1, :3] = CREAM
    col[top:bot, x0:x1, 3] = (a * 255 * env * ramp(i, T0 + 1, T_FULL))[:, None]
    return soft(Image.fromarray(col.astype(np.uint8), 'RGBA'), 6)

def frame(body_png, i):
    env = envelope(i)
    c = Image.new('RGBA', (W, H), (58, 74, 64, 255))
    body = key_out(Image.open(body_png).convert('RGBA'))
    if env > 0:
        c.alpha_composite(ground_glow(env))
    c.alpha_composite(body, (FEET[0] - BODY_AT[0], FEET[1] - BODY_AT[1]))
    if env > 0:
        c.alpha_composite(beam(i, env)); c.alpha_composite(column(i, env))
    return c

if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    fs = sorted(glob.glob(src + '/*.png'))[:45]
    fr = [frame(f, i) for i, f in enumerate(fs)]
    ps = [f.convert('RGB').resize((510, 400)).convert('P', palette=Image.ADAPTIVE) for f in fr]
    ps[0].save(out + '/levelup_a_soft.gif', save_all=True, append_images=ps[1:], duration=67, loop=0, disposal=2)
    idx = [16, 19, 21, 24, 28, 32, 36, 42]
    s = Image.new('RGB', (255 * 8, 200))
    for c, i in enumerate(idx): s.paste(fr[i].convert('RGB').resize((255, 200)), (c * 255, 0))
    s.save(out + '/soft_peak.png')
