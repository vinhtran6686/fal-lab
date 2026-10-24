"""Apply a saved frame recipe: rebuild the state's frames from the clip in source/video/ and export them with video_to_sheet.py.

Usage (from the repo root or anywhere):
  python tools/frame_tuner/apply_recipe.py                      dry run for every saved state (prints the plan, writes nothing)
  python tools/frame_tuner/apply_recipe.py attack --write       export the attack recipe into out/heroes/holy_commander/
  python tools/frame_tuner/apply_recipe.py --default attack     use the approved default instead of a saved recipe (no recipe file needed)
  python tools/frame_tuner/apply_recipe.py attack --write --asset /tmp/test_asset    export into another asset folder (testing)

The recipe (export_recipe.json, written by the frame tuner) has per state: keep (indices of the 15 fps frames of the clip),
durationsMs (one per kept frame), hit (index in the kept list or null). The route is the one used for the approved exports
(the route of the approved exports): ffmpeg fps=15 -> sprite_pack.key_out -> finish scale 120/<body height of frame 0> -> feet of frame 0
at (256, 400) on a 512x512 canvas -> synthetic set -> video_to_sheet.py (it matches the body size to the asset and keeps one canvas).
Needs python, numpy, Pillow, ffmpeg on PATH. Same-day recipes never touch SKILL.md; no model is called (free)."""
import sys, os, json, glob, shutil, subprocess, tempfile, pathlib, argparse
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from sprite_pack import key_out
from PIL import Image

CFG = json.loads((HERE / 'sources.json').read_text())
CW = CH = 512; AX, AY = 256, 400; TARGET_H = 120

def default_recipe(st):
    ap = st['approved']; stride = ap.get('stride', 1)
    return {'stride': stride, 'hit_frame': ap.get('hit')}

def frames_of(clip, fps=None):
    """All keyed frames of the clip at `fps` (default: the project rate; a saved recipe may name its own, e.g. 24, the clip's native rate)."""
    fps = fps or CFG['fps']; d = tempfile.mkdtemp(prefix='ar_')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(clip), '-vf', f"fps={fps}", d + '/%03d.png'], check=True)
    ims = [key_out(Image.open(f).convert('RGBA')) for f in sorted(glob.glob(d + '/*.png'))]
    shutil.rmtree(d, ignore_errors=True); return ims

def shake_offsets(n, cfg):
    """Post-process tremor: per kept frame (dx, dy) in finished-canvas px (about @2x px), zero outside cfg['from']..cfg['to'] (indices in the KEPT list),
    eased in and out, deterministic from cfg['seed']. cfg = {"from": 8, "to": 20, "amp": 2.5, "seed": 1}; amp 2-3 reads as a clear tremor at game size."""
    import random, math
    if not cfg: return [(0, 0)] * n
    rnd = random.Random(cfg.get('seed', 1)); a, b, amp = cfg['from'], cfg['to'], cfg.get('amp', 2.5); out = []
    for k in range(n):
        if a <= k <= b and b > a:
            env = math.sin(math.pi * (k - a) / (b - a)) ** 0.5
            out.append((round(rnd.uniform(-1, 1) * amp * env), round(rnd.uniform(-1, 1) * amp * 0.7 * env)))
        else: out.append((0, 0))
    return out

def plan_for(st, saved, use_default, n):
    if use_default or st['id'] not in saved:
        stride = st['approved'].get('stride', 1); keep = list(range(0, n, stride)); ms = round(1000 / CFG['fps'])
        hit = st['approved'].get('hit'); hit = None if hit is None else hit // stride
        return keep, [ms] * len(keep), hit, 'approved default'
    r = saved[st['id']]; return r['keep'], r['durationsMs'], r.get('hit'), 'saved recipe'

def apply(st, saved, use_default, write, asset_out):
    asset = ROOT / CFG['asset']; clip = asset / st['clip']
    rec = None if use_default else saved.get(st['id']); rfps = (rec or {}).get('fps') or CFG['fps']
    ims = frames_of(clip, rfps); n = len(ims)
    keep, dur, hit, src = plan_for(st, saved, use_default, n)
    if max(keep) >= n: raise SystemExit(f"{st['id']}: recipe keeps frame {max(keep)} but the clip has {n} frames")
    total = sum(dur)
    print(f"{st['id']:8s} {src:16s} @{rfps} fps {len(keep):3d}/{n} frames  {total / 1000:.2f} s  hit={'-' if hit is None else keep[hit]}  -> {st['sheet']}")
    if not write: return
    ref = ims[keep[-1]] if st.get('restFrame') == 'last' else ims[0]     # respawn rises to the master pose: size and feet come from its last frame
    b = ref.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox(); fx, fy = (b[0] + b[2]) / 2, b[3]
    S = TARGET_H / (st.get('bodyPx') or (b[3] - b[1]))      # the approved clips of this hero used the master's 268 px in the clip
    work = pathlib.Path(tempfile.mkdtemp(prefix='ar_set_')); act = 'skill' if st['sheet'].startswith('skill_') else st['id']
    d = work / 'fin' / act; d.mkdir(parents=True)
    offs = shake_offsets(len(keep), (rec or {}).get('shake'))        # optional post-process tremor, recipe field "shake"
    for k, i in enumerate(keep):
        im = ims[i]; sm = im.resize((round(im.width * S), round(im.height * S)), Image.LANCZOS)
        c = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); c.paste(sm, (round(AX - fx * S) + offs[k][0], round(AY - fy * S) + offs[k][1])); c.save(d / f'f_{k:03d}.png')
    sel = {'start': 0, 'endExclusive': len(keep), 'durationsMs': dur, 'loopPolicy': 'loop' if st['loop'] else 'oneshot', 'fps': CFG['fps']}
    if hit is not None: sel['impactMs'] = int(sum(dur[:hit]))
    (work / f'sel_{act}.json').write_text(json.dumps(sel)); (work / f'fin_{act}.json').write_text(json.dumps({'anchor': [AX, AY]}))
    state = {'actions': {act: {'status': 'done', 'output': {'take': 1}, 'takes': [{'take': 1, 'clip': {'path': str(clip)}, 'route': 'supplied',
             'stages': {'finished': {'framesDir': f'fin/{act}', 'metadata': f'fin_{act}.json'}, 'selection': {'selection': f'sel_{act}.json'}}}]}}}
    (work / 'set_state.json').write_text(json.dumps(state, indent=1))
    cmd = [sys.executable, str(ROOT / 'scripts' / 'video_to_sheet.py'), '--set', str(work), '--action', act, '--asset', str(asset_out), '--id', CFG['hero'],
           '--kind', 'hero', '--sheet', st['sheet']] + (['--rest-last'] if st.get('restFrame') == 'last' else [])
    r = subprocess.run(cmd, capture_output=True, text=True); print(r.stdout.strip()[-400:]);
    if r.returncode: print(r.stderr[-800:]); raise SystemExit(f"{st['id']}: video_to_sheet failed")
    shutil.rmtree(work, ignore_errors=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('states', nargs='*'); ap.add_argument('--write', action='store_true')
    ap.add_argument('--default', action='store_true', help='use the approved default instead of the saved recipe')
    ap.add_argument('--asset', help='export into this asset folder instead of the real one (testing)')
    a = ap.parse_args()
    rf = ROOT / CFG['asset'] / 'frames' / 'export_recipe.json'
    saved = json.loads(rf.read_text()).get('states', {}) if rf.exists() else {}
    todo = [s for s in CFG['states'] if (a.states and s['id'] in a.states) or (not a.states and (a.default or s['id'] in saved))]
    if not todo: print('nothing to do: no saved recipe in', rf, '(save one in the frame tuner, or use --default <state>)'); sys.exit(0)
    out = pathlib.Path(a.asset) if a.asset else ROOT / CFG['asset']
    for st in todo: apply(st, saved, a.default, a.write, out)
    if not a.write: print('dry run: add --write to export')
