"""Preview of the EXPORTED package only (reads files under out/heroes/holy_commander/, never the clips or the fx scripts):
body @2x frames + fx back/front layers (placed by their pivots, screen blend) on a dark ground -> data/export_preview/<state>.mp4 + a key-frame strip.
Usage: python tools/frame_tuner/preview_export.py [--out DIR]"""
import sys, json, glob, pathlib, subprocess, argparse
import numpy as np
from PIL import Image
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parent.parent; A = ROOT / 'out' / 'heroes' / 'holy_commander'
BG = np.array([58, 74, 64], np.float32) / 255
CELL = (352, 280); PIV = (176, 246)

def over(c, rgba):
    a = np.asarray(rgba, np.float32) / 255; return c * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
def screen_layer(c, im, pivot):
    full = Image.new('RGBA', CELL, (0, 0, 0, 0)); full.paste(im, (PIV[0] - pivot[0], PIV[1] - pivot[1]))
    a = np.asarray(full, np.float32) / 255; col = a[..., :3] * a[..., 3:4]            # straight alpha -> additive colour
    return 1 - (1 - c) * (1 - col)

def render_state(sheet, folder, fxname):
    body = sorted(glob.glob(str(A / folder / sheet / 'frames' / '@2x' / '*.png')))
    fx = json.loads((A / 'fx' / fxname / 'fx.json').read_text()) if fxname else None
    fb = sorted(glob.glob(str(A / 'fx' / fxname / 'back' / 'frames' / '@2x' / '*.png'))) if fxname else []
    ff = sorted(glob.glob(str(A / 'fx' / fxname / 'front' / 'frames' / '@2x' / '*.png'))) if fxname else []
    out = []
    for i, f in enumerate(body):
        c = np.tile(BG, (CELL[1], CELL[0], 1)).astype(np.float32)
        if fb: c = screen_layer(c, Image.open(fb[i]).convert('RGBA'), fx['pivot_2x'])
        c = over(c, Image.open(f).convert('RGBA'))
        if ff: c = screen_layer(c, Image.open(ff[i]).convert('RGBA'), fx['pivot_2x'])
        out.append(Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)))
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default=str(HERE / 'data' / 'export_preview')); a = ap.parse_args()
    od = pathlib.Path(a.out); od.mkdir(parents=True, exist_ok=True)
    meta = json.loads((A / 'meta.json').read_text()); fxmap = {'levelup_side': 'levelup', 'skill_radiant_slash_side': 'radiant_slash'}
    for sheet, st in meta['states'].items():
        frames = render_state(sheet, st['dir'].rsplit('/', 1)[0], fxmap.get(sheet))
        d = od / sheet; d.mkdir(exist_ok=True)
        for f in d.glob('*.png'): f.unlink()
        for n, im in enumerate(frames): im.save(d / f'{n:03d}.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(st['fps']), '-stream_loop', '2', '-i', str(d / '%03d.png'), '-vf', 'scale=352:280', '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p', '-crf', '20', str(od / f'{sheet}.mp4')], check=True)
        idx = [round(i * (len(frames) - 1) / 7) for i in range(8)] if len(frames) > 8 else list(range(len(frames)))
        strip = Image.new('RGB', (len(idx) * 220, 175)); [strip.paste(frames[i].resize((220, 175)), (k * 220, 0)) for k, i in enumerate(idx)]
        strip.save(od / f'{sheet}_strip.png'); print(sheet, len(frames), 'frames')
