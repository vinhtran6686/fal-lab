# Class: Hero

Everything a hero needs, in one file. Shared rules (style, view prompt wording, files, manifest format) are
in `../format.md`, cited by section. Kind tag and `{kind}`: `hero`. Folder: `out/heroes/{id}/`.
video-sprite `make_master.py --class hero`.

## 1. Role in the game
The player's named character: one of each, sent to a point on the road where it blocks enemies, fights in
melee or shoots, uses 2-3 skills, levels up and respawns after death. Short moves to a blocking point, so
it has **one movement sheet** (run), drawn from the side.

## 2. Roles (ask when missing)
| Role | Adds |
|---|---|
| `melee` (default) | `attack_side` |
| `ranged` | `shoot_side` and a `projectile` still |

## 3. Size (`../format.md` §7, profile `hero`: canvas 2.6 x 2.3 `{H}` (M is 2.93 wide, see below), feet at y 0.88)
| Tier | `{H}` @1x | Canvas @1x | Typical |
|---|---|---|---|
| S | 40 | 104x92 | small mage, archer, child |
| **M (default)** | 60 | 176x140 | most heroes: knight, monk, warrior |
| L | 84 | 220x196 | robot, golem, beast rider |
The canvas leaves about 2 x `{H}` above the feet for casts, level-up and respawn.
M is 176 wide, not 156 (measured on a hero with a body-high weapon, 2026-10-21): the long strikes and thrusts of a big weapon did not fit 156x140 and every sheet had to be padded. S and L keep their canvas until a hero of that tier shows the same; a beam or arc longer than the cell is a separate fx layer (`../format.md` §10), never a reason to enlarge the body canvas.

## 4. Directions and master
**1 direction: side** (left = mirror). The master is the hero in its idle stance, side view (`../format.md`
§3: three-quarter facing right, turned about 30° toward the camera). **No front or back view.** Idle is the
master still itself.
The master is upright and calm (`../format.md` §3 `{UPRIGHT}`): the body vertical, the feet on one horizontal ground line, the weapon at rest; never a diagonal stride toward a corner.

## 5. Stills (fal-image), in order
1. `master` (side, idle stance; `{idle}` when not the neutral pose)
2. `icon` (`../format.md` §3 icon; `{rim}` bright gold-yellow, `{badge}` the hero's main colour, lighter)
3. `projectile` (ranged)
4. `pose_respawn` (kneeling or fallen, the start of the rise; grey when the respawn goes grey -> colour, `../format.md` §10) and, when the
   level-up has a stance of its own, `pose_levelup`
5. `pose_skill_<name>`: one per skill, the skill's peak pose, side view, `--ref` the master. **Optional** when the user describes the final pose
   in words: the clip then ends on the described pose (`../format.md` §10)
6. `fx_<name>` parts only when a skill's effect needs a shaped element (`../templates.md` fx part); the effect
   itself is a recipe of layers (`scripts/fx_layers.py`)
7. `pose_attack` / `pose_run` only when the master's stance reads wrong for that action

## 6. Asset manifest rows (`../format.md` §8 table format)
| Asset | Từ | Loại | Role | Reference (30 fps) |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | all | 15/15 heroes: idle is 1 frame |
| icon | fal-image | ảnh tĩnh | all | - |
| projectile | fal-image | ảnh tĩnh | ranged | - |
| projectile_fly, projectile_hit | fx-layers | hiệu ứng | ranged | flying 2-4 drawings (the still turned or flickered, a `sprite` layer), hit 4-8 drawings (`burst`); reference `bolt_*_flying` / `bolt_*_hit` |
| run_side | video-sprite | loop | all | 15/15, ~6 frames, 0.2 s: short, fast loop |
| attack_side | video-sprite | one-shot | melee | 14/15, ~22 frames, 0.75 s (smear: an `fx_attack` slash layer) |
| shoot_side | video-sprite | one-shot | ranged | 4/15, ~22 frames, 0.75 s |
| death_side | video-sprite | one-shot | all | 13/15, ~9 frames, 0.3 s: short |
| pose_respawn | fal-image | ảnh tĩnh | all | - |
| respawn_side | video-sprite | one-shot | all | 13/15, ~18 frames, 0.6 s: `rise` from `pose_respawn` (tested), or the despawn clip played in reverse |
| fx_respawn | fx-layers | hiệu ứng | all | pillar + ground ring, or a Python fx layer (`video-sprite` "Effect layers") |
| fx_levelup | fx-layers | hiệu ứng | all | pillar or burst |
| levelup_side | video-sprite | one-shot | all | 13/15, ~18-23 frames, 0.7 s |
| pose_skill_`<name>` | fal-image | ảnh tĩnh | per skill, optional (final pose described in words) | - |
| skill_`<name>`_side | video-sprite | one-shot | per skill | 28-68 frames, 1-2 s |
| fx_`<name>` | fx-layers | hiệu ứng | per skill (+ its fx part stills, if any) | separate small objects in the reference |
| package | export | gói | all | last row: `ui/icon`, `export_manifest.json`, `EXPORT_README.md` when the asset leaves the repo |
Optional (`../format.md` §9): `attack2_side` (4/15 heroes have a second melee move), a transformation.
Cost, melee hero with 2 skills: 4 stills (master, icon, 2 poses) + 2 vfx (~USD 0.10) + 7 clips (~USD 0.56) + retakes.

## 7. Skills
**2-3 per hero** (the references: 2-9, median 2-3). Asked with the tier (`multiSelect`). Each skill has three
parts: the **pose** (peak, one still), the **body clip** (master → pose, video-sprite) and a **vfx** when the
effect is big. Kinds seen in the references: area rain or storm, ground smash or shockwave, summon,
transformation, buff or support, special weapon strike (sawblade, multishot, counter, chain), teleport.

## 7b. Design details to ask when the description leaves them out
A weapon or held item that is not described with its size has cost a hero 7 master versions (a long sword: the tip fell under the ground line,
the hilt was hidden, one hand showed). Before the master, read the user's description; for every detail below it does not state, ask in ONE
AskUserQuestion call (up to 4 questions, 3-4 options, the likeliest first "(Recommended)"). The answers go straight into `{design}` and `{idle}`.
| Detail | Options (examples) |
|---|---|
| Held item **size against the body** | dagger-short / to the waist / to the chest / as tall as the body |
| **Hands**: which hand, or both | right / left / both hands on the hilt |
| **Where it rests** in the idle stance | planted in the ground / held in front / on the back / in a hand at the side; hilt and tip inside the frame? |
| Stance width, soft parts, exaggerated part | feet apart (narrow / wide), cape or hair (none / short / long), the part to enlarge |
Ask only what is missing. A character with no held item skips the first three.

## 8. Slots (`brief.md`)
| Slot | Meaning |
|---|---|
| `{id}` | short snake_case id |
| `{design}` | one dense sentence (`../format.md` §1): body and what it exaggerates, costume, the weapon and the hand that holds it, palette **saturated main colour + one bright accent**, effects as flat layers. Reused verbatim in every prompt |
| `{body}` | biped / quadruped / blob / flyer (`../format.md` §3 view wording) |
| `{idle}` | the idle stance, when not the neutral ready pose (the master is drawn in it) |
| `{idle_motion}` | optional: a looping breathing idle, only when the user asks for one (adds an `idle_loop_side` row; video-sprite `idle`) |
| `{poses}` | how the weapon is held per action, when it changes |
| `{attack}` | the attack motion; stays inside the canvas (strike forward or upward) |
| `{death}` | how the hero falls (short: ~0.3 s) |
| `{skills}` | per skill: `<name>: <the body's move>; <the effect>` |

## 9. Review points (in addition to `../format.md` §6)
- Reads as a hero next to the enemies: brighter main colour, one bright accent, a clear role silhouette.
- Every `pose_*` still is the same character as the master; only the stance changes.
- No "heroic" extras the style forbids: no rim light, no aura, no ornate trim.
