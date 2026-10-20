"""Build the data the frame tuner shows: for every clip in sources.json, extract ALL frames (ffmpeg, 15 fps), key the
magenta background, crop to the union box and pack them into one sprite sheet (data/<id>.png) + data/states.json.
Needs: python, numpy, Pillow, ffmpeg on PATH. Run from anywhere; paths resolve from this file. Skips a state whose sheet is
newer than its clip (use --force to rebuild)."""
import sys, os, json, glob, shutil, subprocess, tempfile, pathlib
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from sprite_pack import key_out
from PIL import Image

CELL_H = 220; COLS = 10

def build(state, cfg, force):
    clip = ROOT / cfg['asset'] / state['clip']; out = HERE / 'data'; out.mkdir(exist_ok=True)
    sheet = out / f"{state['id']}.png"; meta = out / f"{state['id']}.json"
    if not clip.exists(): print('missing clip', clip); return None
    if not force and sheet.exists() and meta.exists() and sheet.stat().st_mtime > clip.stat().st_mtime:
        m = json.loads(meta.read_text()); ap = state['approved']; stride = ap.get('stride', 1)      # sheet is cached; the defaults always follow sources.json
        keep = list(range(0, m['n'], stride))
        m.update({'label': state['label'], 'note': state['note'], 'hasHit': state['hasHit'], 'loop': state['loop'],
                  'default': {'keep': keep, 'durationsMs': [round(1000 / cfg['fps'])] * len(keep), 'hit': (ap['hit'] // stride if 'hit' in ap else None)}})
        meta.write_text(json.dumps(m, ensure_ascii=False)); return m
    d = tempfile.mkdtemp(prefix='ft_')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(clip), '-vf', f"fps={cfg['fps']}", d + '/%03d.png'], check=True)
    frames = [key_out(Image.open(f).convert('RGBA')) for f in sorted(glob.glob(d + '/*.png'))]
    shutil.rmtree(d, ignore_errors=True)
    bb = None
    for im in frames:
        b = im.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
        if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    pad = 8; bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(frames[0].width, bb[2] + pad), min(frames[0].height, bb[3] + pad))
    s = CELL_H / (bb[3] - bb[1]); cw, ch = round((bb[2] - bb[0]) * s), CELL_H
    n = len(frames); rows = (n + COLS - 1) // COLS
    sh = Image.new('RGBA', (cw * COLS, ch * rows), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        sh.paste(im.crop(bb).resize((cw, ch), Image.LANCZOS), ((i % COLS) * cw, (i // COLS) * ch))
    sh.save(sheet, optimize=True)
    ap = state['approved']; stride = ap.get('stride', 1)
    keep = list(range(0, n, stride))
    m = {'id': state['id'], 'label': state['label'], 'sheetName': state['sheet'], 'clip': state['clip'], 'sheet': f"data/{state['id']}.png",
         'cols': COLS, 'cellW': cw, 'cellH': ch, 'n': n, 'fps': cfg['fps'], 'loop': state['loop'], 'hasHit': state['hasHit'], 'note': state['note'],
         'srcBox': list(bb), 'default': {'keep': keep, 'durationsMs': [round(1000 / cfg['fps'])] * len(keep),
                                         'hit': (ap['hit'] // stride if 'hit' in ap else None)}}
    meta.write_text(json.dumps(m, ensure_ascii=False))
    print(state['id'], n, 'frames', sheet.stat().st_size // 1024, 'KB')
    return m

if __name__ == '__main__':
    cfg = json.loads((HERE / 'sources.json').read_text()); force = '--force' in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    states = [m for st in cfg['states'] if (not only or st['id'] in only) for m in [build(st, cfg, force)] if m]
    (HERE / 'data' / 'states.json').write_text(json.dumps({'hero': cfg['hero'], 'fps': cfg['fps'], 'states': states}, ensure_ascii=False))
    print('wrote data/states.json with', len(states), 'states')
