# Milestone 01 (Gate 5): ONE command rebuilds the exported slash_diag fx of holy_commander from weapon_track.json + slash_params.json.
#   python scripts/experiments/milestone_01/build_slash_diag.py
# Writes out/heroes/holy_commander/frames/fx/slash_diag/ (front layer @2x/@1x, fx.json, sheet.png, preview_fx_only.gif,
# preview_with_body.gif, preview_with_body_3x.gif, criteria.json) and registers it in meta.json "fx".
import os, sys, json, subprocess, hashlib, pathlib
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[3]
A = ROOT / 'out/heroes/holy_commander'; OUT = A / 'frames/fx/slash_diag'; SRC = A / 'source/vfx/slash_diag'
r = subprocess.run([sys.executable, str(ROOT / 'scripts/experiments/milestone_01/slash_from_track.py'), '--out', str(OUT)], capture_output=True, text=True,
                   env=dict(os.environ, PYTHONHASHSEED='0'))   # gen_slash_loop places breaks with hash(): fixed seed = same frames every run
if r.returncode: print(r.stderr); sys.exit(1)
crit3 = json.loads(r.stdout.strip().splitlines()[-1])
(OUT / 'report.json').rename(OUT / 'build_report.json')
meta = json.loads((A / 'meta.json').read_text()); st = meta['states']['attack_diag_side']; n = st['frames']
f2 = sorted((OUT / 'front/frames/@2x').glob('*.png')); f1 = sorted((OUT / 'front/frames/@1x').glob('*.png'))
b1 = sorted((A / 'frames/attack_diag_side/frames/@1x').glob('*.png'))
assert len(f2) == len(f1) == len(b1) == n, (len(f2), len(f1), len(b1), n)
BG = (36, 38, 46)
def on(im, bg=BG):
    b = Image.new('RGBA', im.size, bg + (255,)); b.alpha_composite(im); return b.convert('RGB')
sheet = Image.new('RGBA', (352 * n, 280)); [sheet.paste(Image.open(f), (i * 352, 0)) for i, f in enumerate(f2)]; sheet.save(OUT / 'sheet.png')
fx = [on(Image.open(f).convert('RGBA')) for f in f1]
fx[0].save(OUT / 'preview_fx_only.gif', save_all=True, append_images=fx[1:], duration=67, loop=0)
wb = []
for a, b in zip(b1, f1):
    c = Image.new('RGBA', (176, 140), BG + (255,)); c.alpha_composite(Image.open(a).convert('RGBA')); c.alpha_composite(Image.open(b).convert('RGBA')); wb.append(c.convert('RGB'))
wb[0].save(OUT / 'preview_with_body.gif', save_all=True, append_images=wb[1:], duration=67, loop=0)
w3 = [i.resize((528, 420), Image.NEAREST) for i in wb]; w3[0].save(OUT / 'preview_with_body_3x.gif', save_all=True, append_images=w3[1:], duration=67, loop=0)
P = json.loads((SRC / 'slash_params.json').read_text()); T = json.loads((SRC / 'weapon_track.json').read_text())
fxj = {
    'state': 'attack_diag_side', 'fx': 'slash_diag', 'source': 'Vector Kit strokes (showcase gen_slash_loop, heavy) in the blade sweep from the marked weapon track',
    'frames': n, 'fps': st['fps'], 'loop': False,
    'blend': 'screen (light on the body; the PNGs are straight-alpha, alpha-over is a little dimmer)', 'size_2x': [352, 280], 'size_1x': [176, 140],
    'pivot_2x': [176, 246.4], 'pivot_1x': [88, 123.2],
    'note': 'same cell and pivot as the body (feet, x 0.5, y 0.88 of 176x140): place the fx image exactly over the body frame; frame n goes with body frame n',
    'layers': [{'id': 'front', 'z': 'in front of the body', 'files': 'frames/fx/slash_diag/front/frames/@2x/hero_holy_commander_fx_slash_diag_front_NN.png (also @1x)'}],
    'timing': {'vfx_start_frame': T['speed']['vfx_start_frame'], 'hit_frame': T['hit_frame'], 'fade_frames': [14, 15, 16]},
    'rebuild': 'python scripts/experiments/milestone_01/build_slash_diag.py (inputs: source/vfx/slash_diag/weapon_track.json + slash_params.json)',
    'previews': {'fx_only_gif': 'frames/fx/slash_diag/preview_fx_only.gif', 'with_body_gif': 'frames/fx/slash_diag/preview_with_body.gif',
                 'with_body_3x_gif': 'frames/fx/slash_diag/preview_with_body_3x.gif', 'sheet': 'frames/fx/slash_diag/sheet.png'}}
(OUT / 'fx.json').write_text(json.dumps(fxj, indent=1, ensure_ascii=False))
meta.setdefault('fx', {})['slash_diag'] = 'frames/fx/slash_diag/fx.json'
(A / 'meta.json').write_text(json.dumps(meta, indent=2, ensure_ascii=False))
h = hashlib.sha256(b''.join(p.read_bytes() for p in f2 + f1)).hexdigest()
print(json.dumps({'frames': n, 'criterion3': crit3, 'png_sha256': h}, ensure_ascii=False))
