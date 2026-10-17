# Class: Enemy

Inherits everything in `../format.md` (style, generation rules, view prompts, commands, folders, checklist).
Hierarchy: **format → class (enemy) → size tier → level → archetype (melee / ranged)**.
Allies (`out/allies/`) and bosses (`out/bosses/`) use this file's slots and sheet list (format.md §7); allies
take the hero palette instead of the enemy one.
Only **Level 1** is defined for now. Kind tag for files and `{kind}`: `enemy`. Folder: `out/enemies/{id}/`.
This skill makes the enemy's design stills (master, standard views, icon, projectile). Its animations are
made by the `video-sprite` skill from those stills, with the size of format.md §7.

## Content slots (flexible, filled from the user's request)
| Slot | Meaning | Example (bandit request) |
|---|---|---|
| `{id}` | short snake_case id | `bandit` |
| `{design}` | one dense sentence that locks the look (format.md §1 leaves these open): body type and the parts it exaggerates, costume and gear, the weapon and the hand that holds it, the dominant colour family and one accent (format.md §1 palette: muted main colour, one warning accent), any effect drawn as flat layers. Reused verbatim in every prompt (stills and video) | `a stocky bald bandit with a big round belly ..., holding a large curved single-edged broadsword (dao) ... in the right hand, drawn with chibi-like squat proportions ...` |
| `{body}` | biped / quadruped / blob / flyer: picks the view wording in format.md §3 (flyers: video-sprite class `flying`) | `biped` |
| `{attack}` | the attack motion (user's words if given), written into the video prompt; it stays inside the frame (an in-place strike, not a lunge across the canvas) | `a whirlwind spin in place with the broadsword held out` |
| `{death}` | how it dies (user's words if given), written into the video prompt | `knocked backward off his feet, the sword flung away` |
| `{projectile}` | ranged only | `a glob of green venom` |
Icon: `{rim}` = muted stone-grey, `{badge}` = muted khaki.

## Level 1: regular enemies (fodder of the first maps)
| Item | Value |
|---|---|
| Size | tier and canvas from the size matrix (`../format.md` §7, profile `unit`): XS 56x48, S 92x80 (default), M 136x120, L 192x168 at 1x; bosses (XL, XXL) use profile `boss`. Body `{H}` per tier, video-sprite `--target-height 2x{H}` |
| Pivot | feet, x 0.5, y 0.88 of the canvas |
| Look | the style principles of format.md §1; must read at its tier height `{H}` |
| Archetypes | `melee` (fights soldiers that block the road), `ranged` (shoots from a distance) |
| Move speed | `move_speed` in `meta.json`, px/s at 1x: a default from the stride, tuned in the playtest (feet must not slide) |

### What an enemy needs (states measured on 68 reference enemies and 16 bosses, 2026-10-17)
Durations are the reference's (30 fps): one-shots (attack, death ...) aim at them; loops (walk, run) take
their length from the stride, so a reference length does not carry over directly.
| Category | Sheet | From still | Loop | Reference | Melee | Ranged |
|---|---|---|---|---|---|---|
| idle | `idle_side` = the master still, 1 frame | `master` | hold | 65/68 enemies, 1 frame | yes | yes |
| move | `walk_side` (+ mirror `walk_left`) | `master` | yes | 63/68, ~22 frames, 0.7 s | yes | yes |
| move | `walk_down` | `view_front` | yes | 62/68, same length as side | yes | yes |
| move | `walk_up` | `view_back` | yes | 63/68, same length as side | yes | yes |
| attack | `attack_side` (+ mirror), hit frame exported | `master` | no | 56/68, ~19 frames, 0.65 s (bosses ~32, 1.05 s) | strike | - |
| attack | `shoot_side` (+ mirror), release frame exported | `master` | no | 8/68, ~24 frames, 0.8 s | - | shoot (no projectile in the clip) |
| death | `death_side` (+ mirror), holds the last frame | `master` | no | 63/68, ~16 frames, 0.55 s (bosses ~35, 1.2 s) | yes | yes |
| ui | `icon` | `icon` still, packed with `sprite_pack.py` | - | - | yes | yes |
| projectile | `projectile` | `projectile` still | - | - | - | yes |
Optional, only when the game needs them (reference counts): `trapped_side` + `trapped_free_side` (43/68:
held by a tower's root or thorn trap, a short struggle loop and a ~5-frame release), `spawn_side` (15/68:
rises from the ground or a portal, ~34 frames, 1.1 s), `special_side` (heal, summon, ~1 s, rare). No
reference enemy has a hurt state. Bosses: the enemy list plus **1 to 3 special moves** (smash, breath,
freeze, heal, spores, summon, transform: 30-48 frames, 1-1.6 s each), side only.
The engine picks the walk sheet from the movement angle (right/left = side, down = front, up = back, a
diagonal uses the nearest; a little hysteresis so a curve does not flicker). Everything else is side only.

Cost of a melee enemy at `low`: 4 stills (master, front, back, icon) ~USD 0.06 + 5 clips (3 walks, attack,
death; idle is the master) with `h3-max-turbo` ~USD 0.40, more with retakes.

## Enemy-specific review points (in addition to format.md §6)
- The weapon (or the asymmetric mark of a blob) is on the same side, with the same shape and size, in every view.
- The 3 views cover every direction: master faces right (turned toward the viewer), front shows the face,
  back hides it.
- Every view stands on the same kind of neutral pose, so the walk clips start alike.
- Reads as an enemy next to the heroes: muted main colour, one warning accent.
