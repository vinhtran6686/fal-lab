"""Export the Python-drawn fx of a state as separate transparent layers that line up with the exported body frames.

Usage: python tools/frame_tuner/export_fx.py [levelup|slash ...] [--asset DIR]    (default: every state with an "fx" in sources.json)

For every kept frame of the state's recipe the fx is drawn on the clip's canvas (same code as the preview: out/heroes/holy_commander/fx/*.py),
then mapped into the SAME @2x space as the exported body: clip px -> (px - feet of the reference frame) * k + pivot, with
k = finish scale (120 / body px) * the sheet's body_rescale (meta.json). So the fx layer and the body frame share one pivot.

Output (per fx, e.g. fx/levelup/): back/ and front/ frame folders (RGBA PNG, @2x and @1x, 01-based) + fx.json. `back` is drawn BEHIND the body, `front`
over it. Light is stored the way it was drawn, "screen" (additive) light on black: colour = light colour, alpha = its strength (max channel), straight alpha.
Blend with `screen`/additive where the engine has it; plain alpha-over also works (a little dimmer on bright backgrounds).
Frames are repeated like the body (video_to_sheet's even_fps) when the recipe holds a frame longer."""
import sys, os, json, pathlib, argparse, shutil
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / 'scripts')); sys.path.insert(0, str(ROOT / 'out' / 'heroes' / 'holy_commander' / 'fx'))
import numpy as np
from PIL import Image
import apply_recipe as ar

PW, PH = 1700, 1100; PPIV = (850, 800)      # provisional @2x canvas and the pivot inside it (cropped to the content afterwards)
BASELINE = 0.12

def screen_acc(layers, shape):
    acc = np.zeros(shape + (3,), np.float32)
    for col, a in layers: acc = 1 - (1 - acc) * (1 - np.array(col, np.float32) * np.clip(a, 0, 1)[..., None])
    return acc

def draw_layers(fx, i, body):
    """-> (back, front) additive RGB float images on the fx canvas (canvas coords) and the offset of the clip frame on that canvas."""
    if fx['module'] == 'levelup_variants':
        import levelup_variants as m
        fn = getattr(m, fx['fn']); sil = m.sil_of(body); out = []
        for front in (False, True):
            cv = m.Canvas(); cv.c = np.zeros_like(cv.c); fn(cv, i, body, sil, front); out.append(cv.c.copy())
        return out[0], out[1], (m.FEET[0] - m.BODY_AT[0], m.FEET[1] - m.BODY_AT[1]), (m.H, m.W)
    if fx['module'] == 'radiant_slash_beam':
        import radiant_slash_beam as m
        sil = m.silhouette(body); back, front = m.fx(i, body, sil)
        return screen_acc(back, (m.H, m.W)), screen_acc(front, (m.H, m.W)), (m.OX, m.OY), (m.H, m.W)
    raise SystemExit('unknown fx module ' + fx['module'])

def placement(ref_bbox, S, scale, size0, cell2):
    """The exact chain the body goes through (apply_recipe: finish at S and put the feet at (AX, AY) on a 512 canvas, then video_to_sheet:
    resize by `scale` and paste so the feet land on the pivot), including its roundings. Returns (sx, sy, ox1, oy1, se, ox2, oy2)."""
    fx0, fy0 = (ref_bbox[0] + ref_bbox[2]) / 2, ref_bbox[3]; W0, H0 = size0
    sx, sy = round(W0 * S) / W0, round(H0 * S) / H0
    ox1, oy1 = round(ar.AX - fx0 * S), round(ar.AY - fy0 * S)
    se = round(ar.CW * scale) / ar.CW if scale != 1.0 else 1.0
    px, py = cell2[0] / 2, round(cell2[1] * (1 - BASELINE))
    ox2, oy2 = round(px - ar.AX * scale), round(py - ar.AY * scale)
    return sx, sy, ox1, oy1, se, ox2, oy2, (px, py)

def to_export(rgb, offset, pl, size_out):
    """warp an additive RGB image from fx-canvas coords into the provisional @2x canvas (the cell pivot sits at PPIV)."""
    im = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), 'RGB')
    sx, sy, ox1, oy1, se, ox2, oy2, (px, py) = pl; ox, oy = offset
    # cell X = (clip x * sx + ox1) * se + ox2 ; provisional X' = X + PPIV - pivot ; canvas = clip + offset
    ax, ay = 1 / (se * sx), 1 / (se * sy)
    data = (ax, 0, ((PPIV[0] - px) * -1 - ox2) / se / sx - ox1 / sx + ox, 0, ay, ((PPIV[1] - py) * -1 - oy2) / se / sy - oy1 / sy + oy)
    return im.transform(size_out, Image.AFFINE, data, resample=Image.BICUBIC)

def to_rgba(rgb_img):
    c = np.asarray(rgb_img, np.float32) / 255; a = c.max(axis=2)
    rgb = np.where(a[..., None] > 1e-4, c / np.maximum(a, 1e-4)[..., None], 0)
    return Image.fromarray(np.dstack([(np.clip(rgb, 0, 1) * 255).astype(np.uint8), (a * 255).astype(np.uint8)]), 'RGBA')

def run(st, saved, asset_out):
    fx = st['fx']; meta_p = asset_out / 'meta.json'; meta = json.loads(meta_p.read_text())
    sheet = st['sheet']; sm = meta['states'][sheet]; rescale = sm.get('body_rescale', 1.0)
    rec = saved[st['id']]; keep, dur = rec['keep'], rec['durationsMs']
    clip = ROOT / ar.CFG['asset'] / st['clip']; ims = ar.frames_of(clip)
    ref = ims[keep[-1]] if st.get('restFrame') == 'last' else ims[0]
    b = ref.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
    S = ar.TARGET_H / (st.get('bodyPx') or (b[3] - b[1])); cell2 = (meta['cell'][0] * 2, meta['cell'][1] * 2)
    pl = placement(b, S, rescale, ims[0].size, cell2); k = S * rescale
    tick = max(1, min(dur)); repeats = [max(1, round(d / tick)) for d in dur]
    order = [i for i, n in zip(keep, repeats) for _ in range(n)]          # same expansion as video_to_sheet's even_fps
    print(f"{st['id']}: {len(keep)} kept frames -> {len(order)} drawn (k={k:.4f})")
    raw = {'back': [], 'front': []}; cache = {}
    for i in keep:
        back, front, off, shp = draw_layers(fx, i, ims[i]); cache[i] = (back, front, off, shp)
    for i in order:
        back, front, off, shp = cache[i]
        for z, rgb in (('back', back), ('front', front)): raw[z].append(to_export(rgb, off, pl, (PW, PH)))
    # crop to the union of what is drawn, snapped to even numbers so @1x is exactly half
    bb = None
    for z in raw:
        for im in raw[z]:
            a = np.asarray(im).max(axis=2) > 3; ys, xs = np.nonzero(a)
            if len(ys): bx = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1); bb = bx if bb is None else (min(bb[0], bx[0]), min(bb[1], bx[1]), max(bb[2], bx[2]), max(bb[3], bx[3]))
    bb = tuple(int(v) for v in bb)
    x0, y0 = (bb[0] - 4) // 2 * 2, (bb[1] - 4) // 2 * 2; x1, y1 = (bb[2] + 5) // 2 * 2, (bb[3] + 5) // 2 * 2
    box = (max(0, x0), max(0, y0), min(PW, x1), min(PH, y1)); w2, h2 = box[2] - box[0], box[3] - box[1]
    pivot2 = (PPIV[0] - box[0], PPIV[1] - box[1])
    name = fx.get('name', st['id']); out = asset_out / 'fx' / name; nm = 'hero_' + ar.CFG['hero'] + '_fx_' + name
    for z in ('back', 'front'):
        d = out / z / 'frames'
        if d.exists(): shutil.rmtree(d)
        (d / '@2x').mkdir(parents=True); (d / '@1x').mkdir(parents=True)
        for n, im in enumerate(raw[z], 1):
            c = im.crop(box); to_rgba(c).save(d / '@2x' / f'{nm}_{z}_{n:02d}.png', optimize=True)
            to_rgba(c.resize((w2 // 2, h2 // 2), Image.LANCZOS)).save(d / '@1x' / f'{nm}_{z}_{n:02d}.png', optimize=True)
    fxj = {'state': sheet, 'fx': name, 'source': fx.get('label'), 'frames': len(order), 'fps': ar.CFG['fps'] if len(set(repeats)) == 1 else round(1000 / tick),
           'loop': False, 'blend': 'screen (additive light on black; straight alpha = strength, alpha-over is a little dimmer)',
           'size_2x': [w2, h2], 'size_1x': [w2 // 2, h2 // 2], 'pivot_2x': list(pivot2), 'pivot_1x': [pivot2[0] // 2, pivot2[1] // 2],
           'note': 'place the fx image so its pivot sits on the hero pivot (feet, x 0.5, y 0.88 of the 176x140 cell); frame n goes with body frame n of the same state',
           'layers': [{'id': 'back', 'z': 'behind the body', 'files': f'fx/{name}/back/frames/@2x/{nm}_back_NN.png (also @1x)'},
                      {'id': 'front', 'z': 'in front of the body', 'files': f'fx/{name}/front/frames/@2x/{nm}_front_NN.png (also @1x)'}]}
    (out / 'fx.json').write_text(json.dumps(fxj, indent=1, ensure_ascii=False))
    meta.setdefault('fx', {})[name] = f'fx/{name}/fx.json'; meta_p.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"  wrote {out.relative_to(asset_out)}: {len(order)} frames each for back/front, {w2}x{h2} @2x, pivot {pivot2}")

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('states', nargs='*'); p.add_argument('--asset'); a = p.parse_args()
    rf = ROOT / ar.CFG['asset'] / 'export_recipe.json'; saved = json.loads(rf.read_text()).get('states', {})
    out = pathlib.Path(a.asset) if a.asset else ROOT / ar.CFG['asset']
    todo = [s for s in ar.CFG['states'] if s.get('fx') and (not a.states or s['id'] in a.states) and s['id'] in saved]
    for st in todo: run(st, saved, out)
    if a.asset is None:                                  # previews of the real asset only
        import preview_fx
        for st in todo: preview_fx.build(st['fx'].get('name', st['id']))
