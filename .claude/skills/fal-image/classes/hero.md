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

## 3. Size (`../format.md` §7, profile `hero`: canvas 2.6 x 2.3 `{H}`, feet at y 0.88)
| Tier | `{H}` @1x | Canvas @1x | Typical |
|---|---|---|---|
| S | 40 | 104x92 | small mage, archer, child |
| **M (default)** | 60 | 156x140 | most heroes: knight, monk, warrior |
| L | 84 | 220x196 | robot, golem, beast rider |
The canvas leaves about 2 x `{H}` above the feet for casts, level-up and respawn.

## 4. Directions and master
**1 direction: side** (left = mirror). The master is the hero in its idle stance, side view (`../format.md`
§3: three-quarter facing right, turned 30-45° toward the camera). **No front or back view.** Idle is the
master still itself.
The master is upright and calm (`../format.md` §3 `{UPRIGHT}`): the body vertical, the feet on one horizontal ground line, the weapon at rest; never a diagonal stride toward a corner.

## 5. Stills (fal-image), in order
1. `master` (side, idle stance; `{idle}` when not the neutral pose)
2. `icon` (`../format.md` §3 icon; `{rim}` bright gold-yellow, `{badge}` the hero's main colour, lighter)
3. `projectile` (ranged)
4. `pose_skill_<name>`: one per skill, the skill's peak pose, side view, `--ref` the master
5. `fx_<name>` (vfx, `../templates.md` vfx): one per skill whose effect is big
6. `pose_attack` / `pose_run` only when the master's stance reads wrong for that action

## 6. Asset manifest rows (`../format.md` §8 table format)
| Asset | Từ | Loại | Role | Reference (30 fps) |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | all | 15/15 heroes: idle is 1 frame |
| icon | fal-image | ảnh tĩnh | all | - |
| projectile | fal-image | ảnh tĩnh | ranged | - |
| run_side | video-sprite | loop | all | 15/15, ~6 frames, 0.2 s: short, fast loop |
| attack_side | video-sprite | one-shot | melee | 14/15, ~22 frames, 0.75 s |
| shoot_side | video-sprite | one-shot | ranged | 4/15, ~22 frames, 0.75 s |
| death_side | video-sprite | one-shot | all | 13/15, ~9 frames, 0.3 s: short |
| respawn_side | video-sprite | one-shot | all | 13/15, ~18 frames, 0.6 s |
| levelup_side | video-sprite | one-shot | all | 13/15, ~18-23 frames, 0.7 s |
| pose_skill_`<name>` | fal-image | ảnh tĩnh | per skill | - |
| skill_`<name>`_side | video-sprite | one-shot | per skill | 28-68 frames, 1-2 s |
| fx_`<name>` | fal-image vfx | hiệu ứng | per big skill effect | separate object in the reference |
Optional (`../format.md` §9): `attack2_side` (4/15 heroes have a second melee move), a transformation.
Cost, melee hero with 2 skills: 4 stills (master, icon, 2 poses) + 2 vfx (~USD 0.10) + 7 clips (~USD 0.56) + retakes.

## 7. Skills
**2-3 per hero** (the references: 2-9, median 2-3). Asked with the tier (`multiSelect`). Each skill has three
parts: the **pose** (peak, one still), the **body clip** (master → pose, video-sprite) and a **vfx** when the
effect is big. Kinds seen in the references: area rain or storm, ground smash or shockwave, summon,
transformation, buff or support, special weapon strike (sawblade, multishot, counter, chain), teleport.

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
