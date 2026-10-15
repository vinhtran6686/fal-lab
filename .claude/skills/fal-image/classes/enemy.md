# Class: Enemy

Inherits everything in `../format.md` (style, generation rules, standard views, folders, checklist).
Hierarchy: **format → class (enemy) → level → archetype (melee / ranged)**.
Only **Level 1** is defined for now. Kind tag for files: `enemy`.
This skill makes the enemy's **stills** (master, standard views, icon, projectile). Its animations are made
by the `video-sprite` skill from those stills, with the Level 1 values below.

## Content slots (flexible, filled from the user's request)
| Slot | Meaning | Example (bandit request) |
|---|---|---|
| `{id}` | short snake_case id | `bandit` |
| `{design}` | one dense sentence that locks the look: body type, proportions, colors, gear, the hand that holds the weapon, distinctive marks. Reused verbatim in every prompt (stills and video) | `a stocky bald bandit with a big round belly ..., holding a large curved single-edged broadsword (dao) ... in the right hand, drawn with chibi-like squat proportions ...` |
| `{body}` | how it moves: biped / quadruped / multi-legged / blob / flyer (flyers: video-sprite class `flying`) | `biped` |
| `{attack}` | the attack motion (user's words if given), written into the video prompt | `a whirlwind spin in place with the broadsword held out` |
| `{death}` | how it dies (user's words if given), written into the video prompt | `knocked backward off his feet, the sword flung away` |
| `{projectile}` | ranged only | `a glob of green venom` |

## Level 1: regular enemies (fodder of the first maps)
| Item | Value |
|---|---|
| Canvas | **256 x 128 at 1x (512 x 256 at @2x) for every action**: move, attack, death, hurt, idle. One frame size and one pivot for the whole enemy, wide enough for weapon swings and a body lying flat |
| Body height | **69 px at 1x (138 px at @2x)** in every action (video-sprite `--target-height 138`; the first export records it in `meta.json`, later exports are matched to it) |
| Pivot | feet, x 0.5, y 0.88 of the canvas |
| Look | simple, few details, one accent color; must read at 48 px |
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

## Standard views (prompts; every view after the master: `--ref <approved master> --png --size 1024x1024`)
Every view prompt is: `Use the reference image only for the character design; redraw it in the style
described. Single game enemy sprite: {design}. <VIEW> Neutral standing pose, full body, centered, filling
about 70% of the frame. {BG} {STYLE}`, with `<VIEW>` from this table (tested on bandit, 2026-10-13/14):

| Still | `<VIEW>` |
|---|---|
| `master` (no `--ref`) | Three-quarter view facing down-right, as if walking toward the bottom-right of the screen. Neutral ready pose. (prompt starts directly with "Single game enemy sprite: {design}.") |
| `view_side` | FLAT SIDE PROFILE like a paper cutout, facing exactly right: chest and belly pointing to the right edge, the back of the head pointing left, only one eye visible, the weapon held out in front to the right, legs one in front of the other along the ground. Not a three-quarter view. |
| `view_front` | Straight FRONT view, perfectly facing the viewer, mirror-symmetric body: both eyes visible, both shoulders the same size, feet side by side, the weapon held upright in its {weapon hand} (on the left side of the image for a right hand). Not a three-quarter view. |
| `view_back` | Straight BACK view, seen from directly behind, walking away from the viewer: the back of the head, NO face and NO eyes visible, mirror-symmetric body, feet side by side with the heels toward the viewer, the weapon held upright in its {weapon hand} (on the RIGHT side of the image for a right hand). Not a three-quarter view, not a front view. |
| `view_up_side` | Three-quarter BACK view, turned 45 degrees to face the TOP-RIGHT of the screen, walking away from the viewer toward the upper right: the back and the left side visible, only the edge of one ear, NO eyes and no face visible, the weapon held upright in its {weapon hand}. Not a side profile, not a front view. |
| `pose_ready_side` (optional) | FLAT SIDE PROFILE facing exactly right in a combat-ready stance: knees bent, weight forward, the weapon raised and ready to strike. Not a three-quarter view. |
The model pulls every view back toward the 3/4 master: name the angle in capitals, say what must and must
not be visible (eyes, face, which side the weapon is on), and end with "Not a three-quarter view".

**icon** (`--ref <master>`)
> Round enemy portrait icon: ONLY the head and shoulders of {design}, cropped at the chest, facing
> slightly right, inside a circular badge with a thick dark outline and a muted stone-grey rim, plain
> muted khaki background inside the circle. {BG} {STYLE}

**projectile** (ranged only; `--ref <master>`)
> Single projectile sprite fired by the enemy in the reference image: {projectile}. Pointing right,
> centered, small and simple, filling about 40% of the frame. {BG} {STYLE}

## Commands (run from the project root)
Let `A=out/enemies/{id}` and `M=A/stills/master_vNN.png` (the approved master).
```
python scripts/gen_image.py "<master prompt>" --size 1024x1024 --png --name master --versioned --out A/stills
python scripts/gen_image.py "<view prompt>"   --size 1024x1024 --png --ref M --name view_side --versioned --out A/stills
# ... view_front, view_back, view_up_side, icon (and projectile) the same way; independent stills run in parallel
python scripts/gen_image.py "<icon prompt>"   --size 1024x1024 --png --ref M --name icon --versioned --out A/stills
python scripts/sprite_pack.py A/stills/icon_vNN.png --asset A --id {id} --state icon --dir none --grid 1x1 --frames 1 --cell 128 --center --own-scale --fill 0.95
```
Then the animations: `video-sprite` skill (one set per view, `--target-height 138`, sheets as in the table above).

## Enemy-specific review points (in addition to format.md §6)
- The weapon is in the same hand, with the same shape and size, in every view.
- The 5 views together cover the 8 directions: side faces right, 3/4 front faces down-right, 3/4 back faces
  up-right, front shows the face, back hides it.
- Every view stands on the same kind of neutral pose, so the walk clips start alike.
