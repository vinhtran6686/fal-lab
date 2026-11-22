"""Cut named animations from an animation table (json: name -> {prefix, from, to}, layered ones: layer_prefix / layer_from / layer_to)
out of the split atlas -> <dir>/anim/<name>/{frames, preview.gif} + <dir>/preview.html.
usage: python scripts/ref_atlas/build_anims.py <dir> <animations.json>   (run split_atlas.py first)"""
import json, os, sys
os.chdir(sys.argv[1])
from PIL import Image
A = json.load(open(sys.argv[2], encoding='utf8'))
FPS = 30
def load(group, i):
    p = f'out/{group}/frames/{i:04d}.png'
    return Image.open(p).convert('RGBA') if os.path.exists(p) else None
def canvas(group):
    return json.load(open(f'out/{group}/frames.json'))['canvas']
cards = []
for name, a in sorted(A.items()):
    layers = [a['layer_prefix'] % k for k in range(a['layer_from'], a['layer_to'] + 1)] if 'layer_prefix' in a else [a['prefix']]
    if not os.path.exists(f'out/{layers[0]}/frames.json'):
        print('SKIP (no sprites in atlas):', name); continue
    W, H = canvas(layers[0]); fr = []
    for i in range(a['from'], a['to'] + 1):
        c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for g in layers:
            im = load(g, i)
            if im: c.alpha_composite(im, ((W - im.width) // 2, (H - im.height) // 2))
        fr.append(c)
    d = f'anim/{name}'; os.makedirs(d + '/frames', exist_ok=True)
    gif = []
    for k, c in enumerate(fr):
        c.save(f"{d}/frames/{a['from'] + k:04d}.png")
        bg = Image.new('RGBA', c.size, (90, 90, 100, 255)); bg.alpha_composite(c); gif.append(bg.convert('P', palette=Image.ADAPTIVE))
    gif[0].save(f'{d}/preview.gif', save_all=True, append_images=gif[1:], duration=1000 // FPS, loop=0, disposal=2)
    cards.append(f'<figure><img src="{d}/preview.gif"><figcaption>{name}<br>{a["from"]}-{a["to"]} ({len(fr)}f)</figcaption></figure>')
open('preview.html', 'w', encoding='utf8').write(f'''<!doctype html><meta charset="utf-8"><title>atlas animations</title>
<style>body{{background:#2a2a32;color:#ddd;font:13px sans-serif;margin:16px}}main{{display:flex;flex-wrap:wrap;gap:12px}}
figure{{margin:0;background:#5a5a64;padding:8px;text-align:center}}img{{display:block;margin:auto;image-rendering:pixelated;max-width:420px}}</style><main>{''.join(cards)}</main>''')
print(len(cards), 'animations')
