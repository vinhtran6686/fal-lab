# Class: Enemy

Inherits everything in `../format.md` (style, generation rules, view prompts, commands, folders, checklist).
Hierarchy: **format → class (enemy) → level → archetype (melee / ranged)**.
Only **Level 1** is defined for now. Kind tag for files and `{kind}`: `enemy`. Folder: `out/enemies/{id}/`.
This skill makes the enemy's design stills (master, standard views, icon, projectile). Its animations are
made by the `video-sprite` skill from those stills, with the Level 1 values below.

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
| Canvas | 256 x 128 at 1x (512 x 256 at @2x) for every action: move, attack, death, hurt, idle (**interim**, format.md §4) |
| Body height | 69 px at 1x (138 px at @2x) in every action (video-sprite `--target-height 138`; **interim**) |
| Pivot | feet, x 0.5, y 0.88 of the canvas (**interim**) |
| Look | the style principles of format.md §1; must read at 48-64 px |
| Archetypes | `melee` (fights soldiers that block the road), `ranged` (shoots from a distance) |
| Move speed | `move_speed` in `meta.json`, px/s at 1x: a default from the stride, tuned in the playtest (feet must not slide) |

### What a Level 1 enemy needs
| Category | Sheet | From still | Loop | Melee | Ranged |
|---|---|---|---|---|---|
| move | `walk_side` (+ mirror `walk_left`) | `view_side` | yes | yes | yes |
| move | `walk_down_side` (+ mirror `walk_down_left`) | `master` | yes | yes | yes |
| move | `walk_up_side` (+ mirror `walk_up_left`) | `view_up_side` | yes | yes | yes |
| move | `walk_down` | `view_front` | yes | yes | yes |
| move | `walk_up` | `view_back` | yes | yes | yes |
| attack | `attack_side` (+ mirror `attack_left`), hit frame exported | `view_side` | no | strike | shoot (release = hit, no projectile in the clip) |
| death | `death_side` (+ mirror), holds the last frame | `view_side` | no | yes | yes |
| ui | `icon` | `icon` still, packed with `sprite_pack.py` | - | yes | yes |
| projectile | `projectile` | `projectile` still | - | - | yes |
The engine picks the walk sheet from the movement angle in 45° sectors (a little hysteresis so a curve
does not flicker). Attack and death are side only (+ mirror): fights happen on the road, facing the target.
Optional: `hurt_side`, `idle_side` (category hurt, idle).

Cost of a melee enemy at `low`: 7 stills (master, 4 views, icon, maybe 1 retry) ~USD 0.10 + 7 clips
(5 walks, attack, death) with `h3-max-turbo` ~USD 0.55, more with retakes.

## Enemy-specific review points (in addition to format.md §6)
- The weapon (or the asymmetric mark of a blob) is on the same side, with the same shape and size, in every view.
- The 5 views together cover the 8 directions: side faces right, 3/4 front faces down-right, 3/4 back faces
  up-right, front shows the face, back hides it.
- Every view stands on the same kind of neutral pose, so the walk clips start alike.
- Reads as an enemy next to the heroes: muted main colour, one warning accent.
