"""Build the data the frame tuner shows. For every clip in sources.json it extracts ALL frames with ffmpeg at two rates:
the project rate (`fps`, 15) and, when `altFps` is set (24, the clip's own rate), the clip's native rate, keys the magenta background, crops to the union
box and packs each rate into one sprite sheet (data/<id>.png and data/<id>_<altFps>.png) plus data/states.json. States with a Python fx also get a
composite sheet per rate (the fx is drawn on every source frame; at 24 fps the fx time is mapped by 15/24 so it lands on the same beat).
Needs: python, numpy, Pillow, ffmpeg on PATH. Run from anywhere; paths resolve from this file. A sheet newer than its clip (and its fx script) is
reused; --force rebuilds everything. Optional arguments: state ids."""
import sys, os, json, glob, shutil, subprocess, tempfile, pathlib, importlib
sys.dont_write_bytecode = True   # the fx code lives in an asset's source/fx: no __pycache__ there
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from sprite_pack import key_out
from PIL import Image
import numpy as np

CELL_H = 220; COLS = 10
FX_COLS = 5; FX_CELL_H = 200; BGC = (58, 74, 64)
FXDIR = ROOT / 'out' / 'heroes' / 'holy_commander' / 'source' / 'fx'
BASE_FPS = 15                                # the fx scripts count their beats in frames at this rate

_frames = {}
def get_frames(clip, fps):
    """All keyed frames of a clip at a given rate (extracted once per run)."""
    k = (str(clip), fps)
    if k not in _frames:
        d = tempfile.mkdtemp(prefix='ft_')
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(clip), '-vf', f"fps={fps}", d + '/%03d.png'], check=True)
        _frames[k] = [key_out(Image.open(f).convert('RGBA')) for f in sorted(glob.glob(d + '/*.png'))]
        shutil.rmtree(d, ignore_errors=True)
    return _frames[k]

def union_box(frames):
    bb = None
    for im in frames:
        b = im.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
        if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    pad = 8; return (max(0, bb[0] - pad), max(0, bb[1] - pad), min(frames[0].width, bb[2] + pad), min(frames[0].height, bb[3] + pad))

def build_fx(state, cfg, frames, out, fps, tag):
    """Composite the Python fx over every frame (the fx follows the source frame) and pack it as data/<id>_fx<tag>.jpg."""
    fx = state['fx']; scale = BASE_FPS / fps          # fx time in 15 fps frames = source index * 15 / fps
    sys.path.insert(0, str(FXDIR)); m = importlib.import_module(fx['module'])
    if fx['module'] == 'levelup_variants':
        fn = getattr(m, fx['fn']); ims = m.render(lambda cv, i, body, sil, front: fn(cv, i * scale, body, sil, front), frames)
    else:
        ims = m.render(frames, scale)
    bb = None
    for im in ims:
        a = np.abs(np.asarray(im.convert('RGB'), np.int16) - np.array(BGC, np.int16)).max(axis=2) > 6
        ys, xs = np.nonzero(a)
        if len(ys): b = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1); bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    pad = 8; bb = tuple(int(v) for v in (max(0, bb[0] - pad), max(0, bb[1] - pad), min(ims[0].width, bb[2] + pad), min(ims[0].height, bb[3] + pad)))
    s2 = FX_CELL_H / (bb[3] - bb[1]); cw, ch = round((bb[2] - bb[0]) * s2), FX_CELL_H
    n = len(ims); rows = (n + FX_COLS - 1) // FX_COLS
    sh = Image.new('RGB', (cw * FX_COLS, ch * rows), BGC)
    for i, im in enumerate(ims): sh.paste(im.convert('RGB').crop(bb).resize((cw, ch), Image.LANCZOS), ((i % FX_COLS) * cw, (i // FX_COLS) * ch))
    sheet = out / f"{state['id']}_fx{tag}.jpg"; sh.save(sheet, quality=88)
    print(state['id'], 'fx', fps, 'fps', n, 'frames', sheet.stat().st_size // 1024, 'KB')
    return {'sheet': f"data/{sheet.name}", 'cols': FX_COLS, 'cellW': cw, 'cellH': ch, 'label': fx['label']}

def variant(state, cfg, fps, tag, force, base_n=None):
    """One source rate of a state: the body sheet (+ fx sheet) and the approved default expressed at that rate."""
    clip = ROOT / cfg['asset'] / state['clip']; out = HERE / 'data'; out.mkdir(exist_ok=True)
    sheet = out / f"{state['id']}{tag}.png"; meta = out / f"{state['id']}{tag}.json"
    fxmod = (FXDIR / (state['fx']['module'] + '.py')) if state.get('fx') else None
    newest = max([clip.stat().st_mtime] + ([fxmod.stat().st_mtime] if fxmod else []))
    fresh = not force and sheet.exists() and meta.exists() and sheet.stat().st_mtime > clip.stat().st_mtime
    m = json.loads(meta.read_text()) if fresh else None
    if m is None:
        frames = get_frames(clip, fps); bb = union_box(frames)
        s = CELL_H / (bb[3] - bb[1]); cw, ch = round((bb[2] - bb[0]) * s), CELL_H
        n = len(frames); rows = (n + COLS - 1) // COLS
        sh = Image.new('RGBA', (cw * COLS, ch * rows), (0, 0, 0, 0))
        for i, im in enumerate(frames): sh.paste(im.crop(bb).resize((cw, ch), Image.LANCZOS), ((i % COLS) * cw, (i // COLS) * ch))
        sh.save(sheet, optimize=True)
        m = {'sheet': f"data/{sheet.name}", 'cols': COLS, 'cellW': cw, 'cellH': ch, 'n': n, 'fps': fps, 'srcBox': [int(v) for v in bb]}
        print(state['id'], fps, 'fps', n, 'frames', sheet.stat().st_size // 1024, 'KB')
    ap = state['approved']; stride = ap.get('stride', 1)
    n15 = base_n or m['n']; keep15 = list(range(0, n15, stride)); ratio = fps / BASE_FPS
    keep = sorted({min(m['n'] - 1, round(i * ratio)) for i in keep15}); ms = round(1000 / BASE_FPS)
    hit = None
    if 'hit' in ap:
        h = ap['hit'] // stride; hit = keep.index(min(m['n'] - 1, round(keep15[h] * ratio)))
    m['default'] = {'keep': keep, 'durationsMs': [ms] * len(keep), 'hit': hit}
    if state.get('fx'):
        fxs = out / f"{state['id']}_fx{tag}.jpg"; fxm = out / f"{state['id']}_fx{tag}.json"
        if not force and fxs.exists() and fxm.exists() and fxs.stat().st_mtime > newest: m['fx'] = json.loads(fxm.read_text())
        else:
            m['fx'] = build_fx(state, cfg, get_frames(clip, fps), out, fps, tag); fxm.write_text(json.dumps(m['fx']))
    meta.write_text(json.dumps({k: v for k, v in m.items() if k != 'fx'}, ensure_ascii=False))
    return m

def build(state, cfg, force):
    clip = ROOT / cfg['asset'] / state['clip']
    if not clip.exists(): print('missing clip', clip); return None
    m = variant(state, cfg, cfg['fps'], '', force)
    m.update({'id': state['id'], 'label': state['label'], 'sheetName': state['sheet'], 'clip': state['clip'], 'loop': state['loop'], 'hasHit': state['hasHit'], 'note': state['note']})
    alt = cfg.get('altFps')
    if alt and alt != cfg['fps']:
        a = variant(state, cfg, alt, f'_{alt}', force, base_n=m['n']); m['alt'] = a
    return m

if __name__ == '__main__':
    cfg = json.loads((HERE / 'sources.json').read_text()); force = '--force' in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    states = [m for st in cfg['states'] if (not only or st['id'] in only) for m in [build(st, cfg, force)] if m]
    (HERE / 'data' / 'states.json').write_text(json.dumps({'hero': cfg['hero'], 'fps': cfg['fps'], 'altFps': cfg.get('altFps'), 'states': states}, ensure_ascii=False))
    print('wrote data/states.json with', len(states), 'states')
