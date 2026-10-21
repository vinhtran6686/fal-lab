"""Make the separate fx layers VISIBLE: previews built only from the exported files under out/heroes/holy_commander/.
For every fx (fx/<name>/fx.json) it writes
  fx/<name>/preview_fx_only.gif    the two layers alone (back + front, screen blend) on a dark ground, hero cell outline and pivot marked
  fx/<name>/preview_with_body.gif  back fx + body + front fx on the same ground
  fx/<name>/sheet.png              8 key frames of the fx alone (@2x)
  <state folder>/preview_with_fx.gif  the same composite, next to the body-only preview.gif of the state
Usage: python tools/frame_tuner/preview_fx.py [--mp4-dir DIR]   (--mp4-dir also writes .mp4 copies for the artifact)"""
import json, glob, pathlib, argparse, subprocess
import numpy as np
from PIL import Image, ImageDraw
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parent.parent; A = ROOT / 'out' / 'heroes' / 'holy_commander'
BG = np.array([46, 58, 52], np.float32) / 255
CELL = (352, 280); PIV = (176, 246)

def over(c, im, xy):
    h, w = c.shape[:2]; x0, y0 = xy; a = np.asarray(im, np.float32) / 255
    sx0, sy0, sx1, sy1 = max(0, x0), max(0, y0), min(w, x0 + a.shape[1]), min(h, y0 + a.shape[0])
    if sx1 <= sx0 or sy1 <= sy0: return c
    p = a[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0]; reg = c[sy0:sy1, sx0:sx1]
    c[sy0:sy1, sx0:sx1] = reg * (1 - p[..., 3:4]) + p[..., :3] * p[..., 3:4]; return c

def screen(c, im, xy):
    h, w = c.shape[:2]; x0, y0 = xy; a = np.asarray(im, np.float32) / 255
    sx0, sy0, sx1, sy1 = max(0, x0), max(0, y0), min(w, x0 + a.shape[1]), min(h, y0 + a.shape[0])
    if sx1 <= sx0 or sy1 <= sy0: return c
    p = a[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0]; col = p[..., :3] * p[..., 3:4]; reg = c[sy0:sy1, sx0:sx1]
    c[sy0:sy1, sx0:sx1] = 1 - (1 - reg) * (1 - col); return c

def build(name):
    fx = json.loads((A / 'fx' / name / 'fx.json').read_text()); state = fx['state']
    meta = json.loads((A / 'meta.json').read_text())['states'][state]; sdir = A / meta['dir']
    body = sorted((sdir / 'frames' / '@2x').glob('*.png'))
    fb = sorted((A / 'fx' / name / 'back' / 'frames' / '@2x').glob('*.png')); ff = sorted((A / 'fx' / name / 'front' / 'frames' / '@2x').glob('*.png'))
    assert len(body) == len(fb) == len(ff), (len(body), len(fb), len(ff))
    fw, fh = fx['size_2x']; px, py = fx['pivot_2x']
    fxo = (PIV[0] - px, PIV[1] - py)                                   # where the fx image sits relative to the hero cell
    x0, y0 = min(0, fxo[0]) - 8, min(0, fxo[1]) - 8; x1, y1 = max(CELL[0], fxo[0] + fw) + 8, max(CELL[1], fxo[1] + fh) + 8
    W, H = x1 - x0, y1 - y0; ox, oy = -x0, -y0
    def ground():
        c = np.tile(BG, (H, W, 1)).astype(np.float32); im = Image.fromarray((c * 255).astype(np.uint8)); d = ImageDraw.Draw(im)
        d.rectangle((ox, oy, ox + CELL[0] - 1, oy + CELL[1] - 1), outline=(80, 96, 88)); cx, cy = ox + PIV[0], oy + PIV[1]
        d.line((cx - 8, cy, cx + 8, cy), fill=(120, 140, 130)); d.line((cx, cy - 8, cx, cy + 8), fill=(120, 140, 130))
        return np.asarray(im, np.float32) / 255
    base = ground(); only, withb = [], []
    for i in range(len(body)):
        a = Image.open(fb[i]).convert('RGBA'); b = Image.open(ff[i]).convert('RGBA')
        c = screen(screen(base.copy(), a, (ox + fxo[0], oy + fxo[1])), b, (ox + fxo[0], oy + fxo[1])); only.append(c)
        c = screen(base.copy(), a, (ox + fxo[0], oy + fxo[1])); c = over(c, Image.open(body[i]).convert('RGBA'), (ox, oy)); c = screen(c, b, (ox + fxo[0], oy + fxo[1])); withb.append(c)
    toimg = lambda c: Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8))
    ms = round(1000 / fx['fps']); out = A / 'fx' / name
    def gif(frames, path):
        ims = [toimg(c) for c in frames]; pal = [im.convert('P', palette=Image.ADAPTIVE, colors=128) for im in ims]
        pal[0].save(path, save_all=True, append_images=pal[1:], duration=ms, loop=0, optimize=False, disposal=2)
    gif(only, out / 'preview_fx_only.gif'); gif(withb, out / 'preview_with_body.gif'); gif(withb, sdir / 'preview_with_fx.gif')
    idx = [round(i * (len(only) - 1) / 7) for i in range(8)]; cw = 260; chh = round(cw * H / W)
    sh = Image.new('RGB', (cw * 4, chh * 2))
    for k, i in enumerate(idx): sh.paste(toimg(only[i]).resize((cw, chh), Image.LANCZOS), ((k % 4) * cw, (k // 4) * chh))
    sh.save(out / 'sheet.png', optimize=True)
    fx['previews'] = {'fx_only_gif': f'fx/{name}/preview_fx_only.gif', 'with_body_gif': f'fx/{name}/preview_with_body.gif', 'sheet': f'fx/{name}/sheet.png',
                      'state_folder_gif': meta['dir'] + '/preview_with_fx.gif', 'note': 'previews only (dark ground, screen blend); the game uses the PNG layers'}
    (out / 'fx.json').write_text(json.dumps(fx, indent=1, ensure_ascii=False))
    return withb, only, ms

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--mp4-dir'); a = ap.parse_args()
    for name in sorted(p.name for p in (A / 'fx').iterdir() if (p / 'fx.json').exists()):
        withb, only, ms = build(name); print(name, len(only), 'frames: previews written')
        if a.mp4_dir:
            d = pathlib.Path(a.mp4_dir); d.mkdir(parents=True, exist_ok=True)
            for tag, fr in (('with_body', withb), ('fx_only', only)):
                tmp = d / f'_{name}_{tag}'; tmp.mkdir(exist_ok=True)
                for n, c in enumerate(fr): Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)).save(tmp / f'{n:03d}.png')
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(round(1000 / ms)), '-stream_loop', '2', '-i', str(tmp / '%03d.png'), '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
                                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', str(d / f'fx_{name}_{tag}.mp4')], check=True)
