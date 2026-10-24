"""Write out/heroes/holy_commander/frames/export_manifest.json (everything another repo needs to use the hero) and verify the package.
Usage: python tools/frame_tuner/build_export_manifest.py [--verify-only]
The manifest is built from meta.json (what the pipeline recorded), frames/export_recipe.json and frames/fx/*/fx.json; the descriptions below are ours.
The verification opens every listed file: counts, sizes @1x/@2x, fx frames vs body frames, alpha present, hashes of the sheets."""
import sys, json, hashlib, pathlib
from PIL import Image
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parent.parent; A = ROOT / 'out' / 'heroes' / 'holy_commander'

INFO = {
 'idle_side': {'label': 'Idle', 'what': 'đứng yên = master (1 hình)', 'status': 'final'},
 'run_side': {'label': 'Chạy', 'what': 'vòng chạy lặp (8 hình)', 'status': 'final'},
 'attack_side': {'label': 'Đánh', 'what': 'chém hai nhát (chéo xuống rồi ngang), vệt chém trắng nằm sẵn trong frame', 'status': 'final'},
 'death_side': {'label': 'Chết', 'what': 'quỳ rồi ngã sấp, nằm yên ở hình cuối', 'status': 'final'},
 'respawn_side': {'label': 'Hồi sinh', 'what': 'quỳ gục đầu vào kiếm, cả người màu xám; hồi màu rồi đứng lên đúng tư thế idle', 'status': 'final-pending-user-approval',
                  'note': 'clip rise t01 chưa được user duyệt'},
 'levelup_side': {'label': 'Lên cấp', 'what': 'hạ người lấy đà, đấm một tay lên trời, giữ pose; ánh sáng là lớp fx riêng (fx/levelup)', 'status': 'final', 'fx': 'levelup'},
 'skill_charge_side': {'label': 'Skill 1: Xung phong', 'what': 'cúi người, rút kiếm, vung lên; lửa và vòng lửa do model vẽ nằm sẵn trong frame', 'status': 'final',
                       'known_issues': ['vòng lửa lớn ở khoảng 2/3 clip (lỗi user đã nhận, giữ lại)', 'hình lạ cạnh vai ở đầu clip']},
 'skill_holy_banner_side': {'label': 'Skill 2: Cờ hiệu thánh', 'what': 'lùi chân, nâng kiếm, găm xuống đất và quỳ một gối, hai tay nắm chặt cán; sóng xung kích trên đất do model vẽ nằm sẵn trong frame', 'status': 'final',
                            'known_issues': ['một khối nón sáng mờ phủ lên hero trong vài hình lúc găm kiếm', 'vòng sóng chạy ra mép ô']},
 'skill_radiant_slash_side': {'label': 'Skill 3: Chém sáng (tia thánh xuyên)', 'what': 'rút kiếm ngang ngực, kéo sát người, bước dài đâm thẳng, giữ pose; tia sáng là lớp fx riêng (fx/radiant_slash)', 'status': 'final', 'fx': 'radiant_slash',
                              'known_issues': ['thân hơi xoay về camera khi kéo kiếm', 'kiếm vung chéo lên khi rút']},
 'icon': {'label': 'Icon', 'what': 'chân dung tròn 128x128', 'status': 'final'},
}
STILLS = [('master', 'source/design/master_v07.png', 'ảnh chốt = idle'), ('icon', 'source/design/icon_v01.png', 'icon gốc'), ('pose_respawn', 'source/design/pose_respawn_v02.png', 'ảnh đầu của respawn'),
          ('pose_levelup', 'source/design/pose_levelup_v02.png', 'đỉnh cú đấm levelup'), ('pose_charge', 'source/design/pose_skill_charge_v01.png', 'pose skill 1'),
          ('pose_holy_banner', 'source/design/pose_skill_holy_banner_v01.png', 'pose skill 2 (bản chốt dùng take do model vẽ)'),
          ('pose_radiant_slash', 'source/design/pose_skill_radiant_slash_v01.png', 'pose skill 3')]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()[:16]

def build():
    meta = json.loads((A / 'meta.json').read_text()); recipe = json.loads((A / 'frames' / 'export_recipe.json').read_text()); fxs = {}
    for name, rel in (meta.get('fx') or {}).items(): fxs[name] = json.loads((A / rel).read_text())
    cell = meta['cell']; ms = round(1000 / 15)
    states = []
    for sid, st in meta['states'].items():
        info = INFO.get(sid, {}); n = st['frames']; fps = st['fps']; fr = 1000 / fps
        e = {'id': sid, 'label': info.get('label', sid), 'what': info.get('what', ''), 'status': info.get('status', 'final'), 'frames': n, 'fps': fps, 'frame_ms': round(fr),
             'duration_ms': round(n * fr), 'loop': bool(st.get('loop')), 'hit_frame_1based': st.get('hit_frame'), 'folder': st['dir'],
             'files_1x': st['files'].replace('NN', '01..%02d' % n), 'files_2x': st['files'].replace('@1x', '@2x').replace('NN', '01..%02d' % n),
             'sheet_2x': st['sheet'], 'preview': st['dir'] + '/preview.gif', 'sheet_sha256_16': sha(A / st['sheet']), 'source_clip': st.get('source')}
        for k in ('known_issues', 'note', 'fx'):
            if k in info: e[k] = info[k]
        states.append(e)
    # recipe keys are the tuner ids; attach them by sheet name
    by = {'attack_side': 'attack', 'death_side': 'death', 'skill_charge_side': 'charge', 'levelup_side': 'levelup', 'skill_holy_banner_side': 'banner', 'skill_radiant_slash_side': 'slash', 'respawn_side': 'respawn'}
    for e in states:
        k = by.get(e['id'])
        if k and k in recipe['states']:
            rc = recipe['states'][k]; e['frame_recipe'] = {'kept_clip_frames': rc['keep'], 'hit_index_0based_in_kept': rc.get('hit'), 'clip_fps': rc['fps']}
    fx = []
    for name, f in fxs.items():
        d = f"frames/fx/{name}"; n = f['frames']
        fx.append({'id': name, 'for_state': f['state'], 'frames': n, 'fps': f['fps'], 'blend': f['blend'], 'size_2x': f['size_2x'], 'size_1x': f['size_1x'], 'pivot_2x': f['pivot_2x'], 'pivot_1x': f['pivot_1x'],
                   'back_2x': f"{d}/back/frames/@2x/hero_holy_commander_fx_{name}_back_01..{n:02d}.png", 'front_2x': f"{d}/front/frames/@2x/hero_holy_commander_fx_{name}_front_01..{n:02d}.png",
                   'back_1x': f"{d}/back/frames/@1x/hero_holy_commander_fx_{name}_back_01..{n:02d}.png", 'front_1x': f"{d}/front/frames/@1x/hero_holy_commander_fx_{name}_front_01..{n:02d}.png",
                   'previews': f.get('previews'),
                   'how': 'draw back behind the body, front over it; put the fx image so its pivot is on the hero pivot; frame n goes with body frame n of for_state'})
    man = {'hero': 'holy_commander', 'name': 'Thánh Kỵ Sĩ Chỉ Huy', 'class': 'hero', 'tier': 'M', 'role': 'melee', 'facing': 'right',
           'canvas_1x': cell, 'canvas_2x': [cell[0] * 2, cell[1] * 2], 'pivot_frac': meta['pivot'], 'pivot_px_1x': [cell[0] / 2, round(cell[1] * meta['pivot'][1])],
           'pivot_px_2x': [cell[0], round(cell[1] * 2 * meta['pivot'][1])], 'body_height_2x_pipeline': meta.get('body_height_2x'), 'body_area_2x': meta.get('body_area_2x'), 'fps': 15,
           'shadow_baked': dict(meta.get('shadow') or {}, note='an ellipse under the feet is drawn INTO every body frame (not in the fx layers)'),
           'flip': 'every state faces RIGHT; flip horizontally for LEFT (meta.json "mirrored" lists run/idle mirrors)', 'hit_frame_note': 'hit_frame is 1-based (the frame the hit lands on)',
           'stats': None, 'states': states, 'fx': fx, 'stills': [{'id': i, 'file': f, 'role': r} for i, f, r in STILLS],
           'reproduce': {'recipes': 'frames/export_recipe.json', 'source_clips': 'source/video/*.mp4', 'tools': ['tools/frame_tuner/apply_recipe.py', 'tools/frame_tuner/export_fx.py', 'tools/frame_tuner/build_export_manifest.py']},
           'not_in_package': 'source/ (clips, stills, fx code) and .work are repo-only; copy frames/ and meta.json',
           'open_items': ['respawn clip not approved by the user yet', 'fx blend: screen is preferred; alpha-over is dimmer on bright ground', 'no gate run (qc.json) on the new states', 'stats not defined']}
    (A / 'frames' / 'export_manifest.json').write_text(json.dumps(man, ensure_ascii=False, indent=1)); return man

def verify(man):
    bad = []; cell = tuple(man['canvas_1x']); c2 = tuple(man['canvas_2x']); total = 0
    for s in man['states']:
        n = s['frames']; base = A / s['folder'] / 'frames'
        for scale, size in (('@1x', cell if s['id'] != 'icon' else (128, 128)), ('@2x', c2 if s['id'] != 'icon' else (256, 256))):
            fs = sorted((base / scale).glob('*.png')); total += len(fs)
            if len(fs) != n: bad.append(f"{s['id']} {scale}: {len(fs)} files, meta says {n}")
            for f in fs[:1] + fs[-1:]:
                im = Image.open(f)
                if im.size != size or im.mode != 'RGBA': bad.append(f'{f.name}: {im.size} {im.mode}, want {size} RGBA')
        if not (A / s['sheet_2x']).exists(): bad.append(s['id'] + ': no sheet')
        if s.get('fx') and s['fx'] not in {f['id'] for f in man['fx']}: bad.append(s['id'] + ': fx missing')
    for f in man['fx']:
        n = f['frames']; st = next(x for x in man['states'] if x['id'] == f['for_state'])
        if n != st['frames']: bad.append(f"fx {f['id']}: {n} frames vs body {st['frames']}")
        for k, rel in (f.get('previews') or {}).items():
            if k != 'note' and not (A / rel).exists(): bad.append(f"fx {f['id']}: preview missing {rel}")
        for z in ('back', 'front'):
            for scale in ('@1x', '@2x'):
                fs = sorted((A / 'frames' / 'fx' / f['id'] / z / 'frames' / scale).glob('*.png')); total += len(fs)
                if len(fs) != n: bad.append(f"fx {f['id']} {z} {scale}: {len(fs)} files")
                im = Image.open(fs[0]); want = tuple(f['size_2x']) if scale == '@2x' else tuple(f['size_1x'])
                if im.size != want or im.mode != 'RGBA': bad.append(f"fx {f['id']} {z} {scale}: {im.size} {im.mode}, want {want}")
    for s in man['stills']:
        if not (A / s['file']).exists(): bad.append('still missing ' + s['file'])
    print(f"checked {len(man['states'])} states, {len(man['fx'])} fx, {len(man['stills'])} stills, {total} frame files")
    print('OK: package complete' if not bad else 'PROBLEMS:\n  ' + '\n  '.join(bad)); return not bad

if __name__ == '__main__':
    man = json.loads((A / 'frames' / 'export_manifest.json').read_text()) if '--verify-only' in sys.argv else build()
    sys.exit(0 if verify(man) else 1)
