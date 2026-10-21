"""Compare how a tremor reads at GAME scale: the model's own tremble, the exaggerated prompt, and the post-process shake (apply_recipe.shake_offsets).
Uses the experiment clips; places each frame exactly like the export (finish scale 120/body px, feet on the pivot, baked shadow), at 15 fps like the shipped
assets. Writes experiments/shake_demo.mp4 (4 panels) and prints the peak-to-peak motion of the body in final @2x px.
Usage: python tools/frame_tuner/shake_demo.py"""
import sys, pathlib, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import apply_recipe as ar
EXP = ar.ROOT / 'out' / 'heroes' / 'holy_commander' / 'experiments'
CELL = (352, 280); PIV = (176, 246)

def place(ims, offs):
    b = ims[0].getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox(); fx, fy = (b[0] + b[2]) / 2, b[3]; S = 120 / (b[3] - b[1])
    sh = Image.new('RGBA', CELL, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((PIV[0] - 45, PIV[1] - 7, PIV[0] + 45, PIV[1] + 7), fill=(0, 0, 0, 89))
    out = []
    for k, im in enumerate(ims):
        sm = im.resize((round(im.width * S * 1.094), round(im.height * S * 1.094)), Image.LANCZOS)   # 1.094: the usual body_rescale of this hero
        c = Image.new('RGBA', CELL, (0, 0, 0, 0)); c.paste(sm, (round(PIV[0] - fx * S * 1.094) + offs[k][0], round(PIV[1] - fy * S * 1.094) + offs[k][1]))
        bg = Image.new('RGBA', CELL, (58, 74, 64, 255)); bg.alpha_composite(sh); bg.alpha_composite(c); out.append(bg)
    return out

def ptp(frames_rgba_mask):
    cy = []
    for im in frames_rgba_mask:
        a = np.array(im.convert('RGB')).astype(int); m = (np.abs(a - np.array([58, 74, 64])).sum(axis=2) > 60); ys, xs = np.nonzero(m[:240]); cy.append((xs.mean(), ys.mean()))
    c = np.array(cy); k = np.ones(5) / 5; h = c - np.stack([np.convolve(c[:, 0], k, 'same'), np.convolve(c[:, 1], k, 'same')], 1)
    return np.ptp(h[5:-5, 0]), np.ptp(h[5:-5, 1])

if __name__ == '__main__':
    panels = []
    for title, clip, shake in (('1 prompt: tremble', 'test_strain.mp4', None), ('2 prompt: violent shake', None, None),
                               ('3 tremble + post shake', 'test_strain.mp4', {'from': 6, 'to': 40, 'amp': 2.5, 'seed': 3}), ('4 violent + post shake', None, {'from': 6, 'to': 40, 'amp': 2.5, 'seed': 3})):
        clip = clip or 'test_strain_violent.mp4'
        p = EXP / clip
        if not p.exists(): print('missing', p); continue
        ims = ar.frames_of(p); n = len(ims)
        fr = place(ims, ar.shake_offsets(n, shake)); panels.append((title, fr)); print(f'{title:28s} body motion in final @2x px (peak-to-peak)  x {ptp(fr)[0]:.1f}  y {ptp(fr)[1]:.1f}')
    n = min(len(f) for _, f in panels); W = CELL[0] * len(panels)
    d = pathlib.Path(tempfile.mkdtemp())
    for i in range(n):
        row = Image.new('RGB', (W, CELL[1] + 24), (20, 24, 22)); dr = ImageDraw.Draw(row)
        for k, (t, fr) in enumerate(panels): row.paste(fr[i].convert('RGB'), (k * CELL[0], 24)); dr.text((k * CELL[0] + 8, 6), t, fill=(230, 230, 230))
        row.save(d / f'{i:03d}.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '15', '-stream_loop', '2', '-i', str(d / '%03d.png'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', str(EXP / 'shake_demo.mp4')], check=True)
    print('wrote', (EXP / 'shake_demo.mp4').relative_to(ar.ROOT))
