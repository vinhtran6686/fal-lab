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
FX_COLS = 5; FX_CELL_H = 200; BGC = (58, 74, 64)
FXDIR = ROOT / 'out' / 'heroes' / 'holy_commander' / 'fx'

def build_fx(state, cfg, frames, force, out):
    """Composite the Python-drawn fx over every frame of the clip (the fx follows the source frame, so dropping a frame keeps the
    fx where it was) and pack the result as data/<id>_fx.jpg."""
    fx = state.get('fx')
    if not fx: return None
    mod = FXDIR / (fx['module'] + '.py'); sheet = out / f"{state['id']}_fx.jpg"; meta = out / f"{state['id']}_fx.json"
    if not force and sheet.exists() and meta.exists() and sheet.stat().st_mtime > max(mod.stat().st_mtime, (ROOT / cfg['asset'] / state['clip']).stat().st_mtime):
        return json.loads(meta.read_text())
    sys.path.insert(0, str(FXDIR)); import importlib; m = importlib.import_module(fx['module'])
    ims = m.render(getattr(m, fx['fn']) if 'fn' in fx else None, frames) if fx['module'] == 'levelup_variants' else m.render(frames)
    import numpy as np
    bb = None
    for im in ims:
        a = np.abs(np.asarray(im.convert('RGB'), np.int16) - np.array(BGC, np.int16)).max(axis=2) > 6
        ys, xs = np.nonzero(a)
        if len(ys): b = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1); bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    pad = 8; bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(ims[0].width, bb[2] + pad), min(ims[0].height, bb[3] + pad))
    s2 = FX_CELL_H / (bb[3] - bb[1]); cw, ch = round((bb[2] - bb[0]) * s2), FX_CELL_H
    n = len(ims); rows = (n + FX_COLS - 1) // FX_COLS
    sh = Image.new('RGB', (cw * FX_COLS, ch * rows), BGC)
    for i, im in enumerate(ims): sh.paste(im.convert('RGB').crop(bb).resize((cw, ch), Image.LANCZOS), ((i % FX_COLS) * cw, (i // FX_COLS) * ch))
    sh.save(sheet, quality=88)
    r = {'sheet': f"data/{state['id']}_fx.jpg", 'cols': FX_COLS, 'cellW': cw, 'cellH': ch, 'label': fx['label']}
    meta.write_text(json.dumps(r)); print(state['id'], 'fx', n, 'frames', sheet.stat().st_size // 1024, 'KB'); return r

_frames = {}
def get_frames(clip, fps):
    """All keyed frames of a clip (extracted once per run)."""
    if clip not in _frames:
        d = tempfile.mkdtemp(prefix='ft_')
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(clip), '-vf', f"fps={fps}", d + '/%03d.png'], check=True)
        _frames[clip] = [key_out(Image.open(f).convert('RGBA')) for f in sorted(glob.glob(d + '/*.png'))]
        shutil.rmtree(d, ignore_errors=True)
    return _frames[clip]

def build(state, cfg, force):
    clip = ROOT / cfg['asset'] / state['clip']; out = HERE / 'data'; out.mkdir(exist_ok=True)
    sheet = out / f"{state['id']}.png"; meta = out / f"{state['id']}.json"
    if not clip.exists(): print('missing clip', clip); return None
    ap = state['approved']; stride = ap.get('stride', 1)
    if not force and sheet.exists() and meta.exists() and sheet.stat().st_mtime > clip.stat().st_mtime:
        m = json.loads(meta.read_text())          # sheet is cached; the defaults and the fx always follow sources.json
    else:
        frames = get_frames(clip, cfg['fps'])
        bb = None
        for im in frames:
            b = im.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
            if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
        pad = 8; bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(frames[0].width, bb[2] + pad), min(frames[0].height, bb[3] + pad))
        s = CELL_H / (bb[3] - bb[1]); cw, ch = round((bb[2] - bb[0]) * s), CELL_H
        n = len(frames); rows = (n + COLS - 1) // COLS
        sh = Image.new('RGBA', (cw * COLS, ch * rows), (0, 0, 0, 0))
        for i, im in enumerate(frames): sh.paste(im.crop(bb).resize((cw, ch), Image.LANCZOS), ((i % COLS) * cw, (i // COLS) * ch))
        sh.save(sheet, optimize=True)
        m = {'id': state['id'], 'sheetName': state['sheet'], 'clip': state['clip'], 'sheet': f"data/{state['id']}.png",
             'cols': COLS, 'cellW': cw, 'cellH': ch, 'n': n, 'fps': cfg['fps'], 'srcBox': list(bb)}
        print(state['id'], n, 'frames', sheet.stat().st_size // 1024, 'KB')
    keep = list(range(0, m['n'], stride))
    m.update({'label': state['label'], 'note': state['note'], 'hasHit': state['hasHit'], 'loop': state['loop'],
              'default': {'keep': keep, 'durationsMs': [round(1000 / cfg['fps'])] * len(keep), 'hit': (ap['hit'] // stride if 'hit' in ap else None)}})
    fxm = None
    if state.get('fx'):
        fxdir = FXDIR / (state['fx']['module'] + '.py'); fxs = out / f"{state['id']}_fx.jpg"
        stale = force or not fxs.exists() or fxs.stat().st_mtime < max(fxdir.stat().st_mtime, clip.stat().st_mtime)
        fxm = build_fx(state, cfg, get_frames(clip, cfg['fps']) if stale else None, force, out)
    if fxm: m['fx'] = fxm
    else: m.pop('fx', None)
    meta.write_text(json.dumps(m, ensure_ascii=False)); return m

if __name__ == '__main__':
    cfg = json.loads((HERE / 'sources.json').read_text()); force = '--force' in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    states = [m for st in cfg['states'] if (not only or st['id'] in only) for m in [build(st, cfg, force)] if m]
    (HERE / 'data' / 'states.json').write_text(json.dumps({'hero': cfg['hero'], 'fps': cfg['fps'], 'states': states}, ensure_ascii=False))
    print('wrote data/states.json with', len(states), 'states')
