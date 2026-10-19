"""Build manifest.json for the hero_malik <-> holy_commander comparison viewer (tools/kr_compare/).

One-off compare tool, NOT part of the regular fal-lab pipeline: pulls hero_malik's real shipped
frames from the reverse-engineered KR1 repo (read-only reference, never sent to any API) and
holy_commander's real assets from out/heroes/holy_commander/. States fal-lab has not exported yet
are left with frames: [] (the viewer shows "chua co" for those).

Usage: python tools/kr_compare/build_manifest.py
"""
import glob
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FAL_LAB = os.path.abspath(os.path.join(HERE, '..', '..'))
REVERSE_KR1 = r"E:\work\reverse\games\kr1"  # read-only reference repo; look only, per CLAUDE.md
HOLY_COMMANDER = os.path.join(FAL_LAB, 'out', 'heroes', 'holy_commander')

SPRITES_OUT = os.path.join(HERE, 'sprites')

sys.path.insert(0, os.path.join(FAL_LAB, 'scripts'))


def extract_raw_clip(state, rel_mp4, fps=15):  # matches holy_commander's displayed fps below
    """A raw video-sprite clip (never exported: a rejected take, for review only), turned into
    real keyed frames the same way the finished sheets are: ffmpeg cuts the frames, sprite_pack's
    own key_out() removes the flat magenta background (format.md SS1). Not registered, not
    retimed, not cropped to the asset's canvas/body scale: this is the model's raw output, exactly
    as `sprite_set.py review` already showed it, just played instead of a single contact sheet."""
    import static_ffmpeg
    from PIL import Image
    from sprite_pack import key_out

    ffmpeg, _ = static_ffmpeg.run.get_or_fetch_platform_executables_else_raise()
    dst_dir = os.path.join(SPRITES_OUT, 'holy_commander', state)
    if os.path.isdir(dst_dir):
        shutil.rmtree(dst_dir)
    os.makedirs(dst_dir)
    subprocess.run([ffmpeg, '-y', '-i', os.path.join(HOLY_COMMANDER, rel_mp4), '-vf', f'fps={fps}',
                    os.path.join(dst_dir, f'{state}_%03d.png')],
                   check=True, capture_output=True)
    frames = []
    for path in sorted(glob.glob(os.path.join(dst_dir, '*.png'))):
        im = key_out(Image.open(path).convert('RGBA'))
        im.save(path)
        frames.append({'name': f'{state}/{os.path.splitext(os.path.basename(path))[0]}', 'w': im.width, 'h': im.height})
    return frames


def span(a, b):
    return list(range(a, b + 1))


def load_malik():
    """hero_malik's own animations from the KR1 data tables, real frame sizes from the sprite index."""
    index = json.load(open(os.path.join(REVERSE_KR1, 'sprites', 'fullhd', '_index.json'), encoding='utf-8'))
    anims = json.load(open(os.path.join(REVERSE_KR1, 'data', 'kr1', 'data', 'game_animations.json'),
                            encoding='utf-8'))['animations']

    group = 'go_hero_malik'
    src_dir = os.path.join(REVERSE_KR1, 'sprites', 'fullhd', group)
    dst_dir = os.path.join(SPRITES_OUT, 'hero_malik')
    os.makedirs(dst_dir, exist_ok=True)

    def frame_info(name):
        fr = index[f'{group}/{name}']
        return {'name': name, 'w': fr['size'][0], 'h': fr['size'][1]}

    states = {}
    # category matches tools/viewer/characters.py's category(): core/movement/role/skill
    category = {
        'idle': 'core', 'running': 'movement', 'attack': 'core', 'attack2': 'core', 'death': 'core',
        'levelup': 'role', 'levelUp': 'role', 'respawn': 'role', 'smash': 'skill', 'fissure': 'skill',
    }
    copied = set()
    for name, a in anims.items():
        if not name.startswith('hero_malik_'):
            continue
        state = name[len('hero_malik_'):]
        idx = span(a['from'], a['to'])
        frames = [frame_info(f'{a["prefix"]}_{i:04d}') for i in idx]
        for f in frames:
            if f['name'] not in copied:
                shutil.copyfile(os.path.join(src_dir, f['name'] + '.png'), os.path.join(dst_dir, f['name'] + '.png'))
                copied.add(f['name'])
        states[state] = {'category': category.get(state, 'skill'), 'frames': frames}

    return {
        'id': 'hero_malik',
        'label': 'hero_malik (KR1, mộc nhân giáp dày, cận chiến + sấm đất)',
        'sprite_root': 'sprites/hero_malik/',
        'fps': 30,
        'states': states,
        # games/kr1/src/kr1/game_templates.lua: tt.render.sprites[1].anchor = v(0.5, 0.1);
        # tt.motion.max_speed = 2 * FPS (world units/s) * 1.40625 px/unit (fullhd) = ~84 px/s
        'anchor': [0.5, 0.1],
        'speed': 84,
    }


def load_exported_sheet(state, category, sheet_dir, fps):
    """A sheet already exported by video_to_sheet.py: real frames from <sheet_dir>/frames/@1x."""
    from PIL import Image
    src = os.path.join(HOLY_COMMANDER, sheet_dir, 'frames', '@1x')
    dst_dir = os.path.join(SPRITES_OUT, 'holy_commander', state)
    os.makedirs(dst_dir, exist_ok=True)
    frames = []
    for name in sorted(os.listdir(src)):
        if not name.endswith('.png'):
            continue
        stem = os.path.splitext(name)[0]
        shutil.copyfile(os.path.join(src, name), os.path.join(dst_dir, name))
        w, h = Image.open(os.path.join(src, name)).size
        frames.append({'name': f'{state}/{stem}', 'w': w, 'h': h})
    return {'category': category, 'frames': frames}


def load_holy_commander():
    """holy_commander's own assets: idle, run and every other row already exported by
    video_to_sheet.py (meta.json "states") use their real frames, all on the same 156x140
    canvas/body scale (idle_side is frame 0 of run_side, format.md SS6 row 1: free, no model);
    everything else from brief.md's manifest that is not exported yet is left with frames: []
    so the viewer shows it as missing, same convention as classes/hero.md SS6."""
    dst_dir = os.path.join(SPRITES_OUT, 'holy_commander')
    os.makedirs(dst_dir, exist_ok=True)

    meta_path = os.path.join(HOLY_COMMANDER, 'meta.json')
    exported = json.load(open(meta_path, encoding='utf-8'))['states'] if os.path.exists(meta_path) else {}

    def row(sheet, category, fallback_note, fps_override=None):
        if sheet in exported:
            st = exported[sheet]
            return load_exported_sheet(sheet, category, st['dir'], fps_override or st['fps'])
        return {'category': category, 'frames': [], 'note': fallback_note}

    states = {
        'idle': row('idle_side', 'core', 'idle_side chua export'),
        'running': row('run_side', 'movement',
                       'raw/run_side_t01.mp4 da quay (124 frame, 24fps); qc pass tru mau lem o chan '
                       '(28/124 frame) - chua export sheet that (can ffmpeg + sprite_set.py run, dang cho duyet)'),
        'attack': {'category': 'core', 'frames': [],
                   'note': 'QC FAIL that (khong phai export chinh thuc), nhung user danh gia dang nhin dep: '
                           't04 la combo 2 chem (cheo xuong + ngang), 3s; gate area/feet/turn deu fail dung luc '
                           'co vet trang mo hinh luoi liem xuat hien (frame ~13-39) - rat co the gate doc sai '
                           'vi vet do lam meo silhouette, khong han la nhan vat quay lung that. Chua accept/export, '
                           'dang cho quyet dinh co quay lai sua vet luoi liem hay giu ban nay.',
                   'raw_clip': 'raw/attack_side_attack_t04.mp4'},
        'death': {'category': 'core', 'frames': [],
                  'note': 'raw/death_side_death_t01.mp4 dat (score 8) - chua export'},
        'respawn': {'category': 'role', 'frames': [],
                    'note': 'raw/despawn_side_extra_t01.mp4 dat (score 8), export --reverse - chua export'},
        'levelup': {'category': 'role', 'frames': [],
                    'note': 'raw/levelup_side_extra_t01.mp4 dinh vet chem xanh + bui - can quay lai'},
        'holy_banner': {'category': 'skill', 'frames': [],
                        'note': 'raw/skill_side_skill_holy_banner_t01.mp4 dinh vong sang hong/vang - can quay lai'},
        'radiant_slash': {'category': 'skill', 'frames': [],
                          'note': 'raw/skill_side_skill_radiant_slash_t01.mp4 dinh vet chem hong lon - can quay lai'},
        'charge': {'category': 'skill', 'frames': [],
                   'note': 'raw/skill_side_skill_charge_t01.mp4 dat (score 8) - chua export'},
    }
    for name, s in states.items():
        rel = s.pop('raw_clip', None)
        if rel:
            s['frames'] = extract_raw_clip(name, rel)
            s['qc_fail'] = True

    return {
        'id': 'holy_commander',
        'label': 'holy_commander (fal-lab, dang lam)',
        'sprite_root': 'sprites/holy_commander/',
        'fps': 15,
        'states': states,
        # video-sprite pivot is feet at y=0.88 from the top (fal-image/format.md SS7); the viewer's
        # draw formula wants the KR convention oy=(1-anchor.y)*h, so anchor.y = 1 - 0.88 = 0.12.
        # No real game speed stat yet (hero not wired into a game loop): demo speed only.
        'anchor': [0.5, 0.12],
        'speed': 84,
    }


if __name__ == '__main__':
    manifest = {'characters': [load_malik(), load_holy_commander()]}
    out = os.path.join(HERE, 'manifest.json')
    json.dump(manifest, open(out, 'w', encoding='utf-8'), indent=1)
    for c in manifest['characters']:
        n = sum(len(s['frames']) for s in c['states'].values())
        print(f"{c['id']}: {len(c['states'])} states, {n} frames -> {out}")
