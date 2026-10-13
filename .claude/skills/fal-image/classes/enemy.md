# Class: Enemy

Inherits everything in `../format.md` (style, generation rules, output, pipeline, checklist).
Hierarchy: **format → class (enemy) → level → archetype (melee / ranged)**.
Only **Level 1** is defined for now (test set). Kind tag for files: `enemy`.

## Content slots (flexible, filled from the user's request)
| Slot | Meaning | Example (spider request) |
|---|---|---|
| `{id}` | short snake_case id | `spider` |
| `{design}` | one dense sentence that locks the look: body type, colors, gear, distinctive marks. Reused verbatim in every prompt | `a squat monster spider with a round olive-brown abdomen marked by a pale bone-colored skull pattern, eight thick jointed dark-brown legs, a small olive head with three glowing yellow eyes and two curved bone-white fangs` |
| `{walk_poses}` | 6 per-frame poses of the walk cycle (see presets) | multi-leg preset |
| `{attack}` + `{attack_poses}` | the attack and its 6 poses | `a lunging bite with its fangs` |
| `{death}` | how it ends up | `flips onto its back and curls its legs` |
| `{projectile}` | ranged only | `a glob of green venom` |

### Walk pose presets (pick by body type, adapt the wording)
- **Biped**: `Frame 1: left foot forward touching the ground, right foot back. Frame 2: body lowest, weight on the left foot. Frame 3: right leg passing the left, body highest. Frame 4: right foot forward touching the ground. Frame 5: body lowest, weight on the right foot. Frame 6: left leg passing, flowing back into frame 1.`
- **Quadruped**: `Frame 1: front-left and back-right legs forward. Frame 2: legs gathering under the body. Frame 3: legs passing, body highest. Frame 4: front-right and back-left legs forward. Frame 5: gathering. Frame 6: passing, flowing back into frame 1.`
- **Multi-legged**: `Frame 1: the first and third legs on the near side lifted high, the others planted. Frame 2: those legs reach forward, body slightly raised. Frame 3: they plant on the ground, body at its lowest. Frame 4: the second and fourth near-side legs lifted high. Frame 5: those legs reach forward, body slightly raised. Frame 6: they plant, flowing back into frame 1.`
- **Blob / slime**: `Frame 1: round at rest. Frame 2: squashed flat. Frame 3: stretched tall leaning forward. Frame 4: airborne a little. Frame 5: landing squash. Frame 6: back to round.`
Always end with: `The leg (or body) positions must be clearly different in every frame.`

## Level 1: regular enemies (fodder of the first maps)
| Item | Value |
|---|---|
| Cell @1x | **96 x 96** (@2x 192) |
| Body fill | larger side = 0.72 of the cell, fixed by `walk_side` |
| Look | simple, few details, one accent color; must read at 48 px |
| Archetypes | `melee` (fights soldiers that block the road), `ranged` (shoots from a distance) |

### State matrix, Level 1 (every sheet = 6 frames, 3x2 grid)
| State | Melee | Ranged | Dirs | fps | Loop | Hit frame |
|---|---|---|---|---|---|---|
| `walk` | yes | yes | side, up, down | 12 | yes | - |
| `attack` | yes (strike) | yes (shoot) | side | 12 | yes | 4 |
| `death` | yes | yes | side | 10 | no (holds last frame) | - |
| `projectile` | - | yes | side (pointing right) | - | - | - |
| `icon` | yes | yes | - | - | - | - |

Melee = master + 3 walk + attack + death + icon = **7 calls** (~$0.09 at `low`). Ranged adds the projectile = 8.

## Prompt blocks (fixed wording; only the slots change)
Every prompt ends with `{STYLE}`; sheets add `{GRID}` then `{BG}`; single sprites add `{BG}`.
Flags: master `--size 1024x1024 --png`; everything else adds `--ref <master.png>`.

**master** (`--size 1024x1024 --png`)
> Single game enemy sprite: {design}. Side profile view: the head is on the RIGHT side of the image
> facing right, as if walking to the right. Neutral ready pose, full body, centered, filling about
> 70% of the frame. {BG} {STYLE}

**walk_side** (`--size 1536x1024 --png --ref <master>`)
> Use the reference image only for the character design; redraw it in the style described.
> Sprite sheet of {design}. A 6-frame walk cycle, side view facing and moving right (head on the right).
> {walk_poses} {GRID} {BG} {STYLE}

**walk_up**: same flags
> Use the reference image only for the character design; redraw it in the style described.
> Sprite sheet of {design}. A 6-frame walk cycle seen from BEHIND, moving up and away from the camera:
> the back of the body is visible and the face is hidden. {walk_poses} {GRID} {BG} {STYLE}

**walk_down**: same flags
> Use the reference image only for the character design; redraw it in the style described.
> Sprite sheet of {design}. A 6-frame walk cycle in a symmetrical FRONT view: it walks straight down
> the screen toward the viewer, its face at the bottom-center of each figure looking at the viewer,
> the body behind and above the head, mirror-symmetric. Not a side view, not a three-quarter view.
> {walk_poses, rewritten as left/right pairs} {GRID} {BG} {STYLE}
(Without the "symmetrical / not three-quarter" wording the model drew a 3/4 side view.)

**attack_side**: same flags
> Use the reference image only for the character design; redraw it in the style described.
> Sprite sheet of {design} performing {attack}, side view facing right. Frame 1: ready stance.
> Frame 2: wind-up, pulling back. Frame 3: launching forward. Frame 4: full extension at the moment of
> impact with a short motion smear (the hit). Frame 5: follow-through. Frame 6: recovering to the ready
> stance. {GRID} {BG} {STYLE}
(Ranged: frame 4 is the release; no projectile in flight.)

**death_side**: same flags
> Use the reference image only for the character design; redraw it in the style described.
> Sprite sheet of {design} dying, side view facing right. Frame 1: recoils from a hit, body jolted
> backward. Frame 2: staggers. Frame 3: falling over. Frame 4: hits the ground. Frame 5: {death}.
> Frame 6 (final pose, held): exactly like frame 5 but completely still, eyes closed.
> No debris, no motion lines. {GRID} {BG} {STYLE}
(Spelling out "frame 6 = frame 5, still" fixed a final frame that stood back up.)
Custom death behavior (e.g. knocked back, weapon flung away): rewrite frames 1-5 to tell that story,
keep frame 6 = frame 5 still, and add "Keep the body AND the <weapon> fully inside each frame's own
cell" so the packer can split the frames (tested on `bandit`).
Walk cycles that come out as a shuffle (tiny steps): add "Exaggerated cartoon march: big wide steps,
knees lifted high, the free arm swinging, the body bobbing clearly up and down" (tested on `bandit`).

**projectile** (ranged only; `--size 1024x1024 --png --ref <master>`)
> Single projectile sprite fired by the enemy in the reference image: {projectile}. Pointing right,
> centered, small and simple, filling about 40% of the frame. {BG} {STYLE}

**icon** (`--size 1024x1024 --png --ref <master>`)
> Round enemy portrait icon: head and shoulders of {design}, facing slightly right, inside a circular
> badge with a thick dark outline and a muted stone-grey rim, plain muted khaki background inside the
> circle. {BG} {STYLE}

## Commands (Level 1, run from the project root)
Let `A=out/enemies/{id}` and `M=A/master/raw/master_vNN.png` (the approved master). Sheet names:
`walk_side`, `walk_up`, `walk_down`, `attack_side`, `death_side`, `icon` (ranged adds `projectile`).
```
# master candidates
python scripts/gen_image.py "<master prompt>" --size 1024x1024 --png --name master --versioned --out A/master/raw
# one sheet (same pattern for every sheet; independent sheets can run in parallel)
python scripts/gen_image.py "<sheet prompt>"  --size 1536x1024 --png --ref M --name walk_side --versioned --out A/walk_side/raw
python scripts/gen_image.py "<icon prompt>"   --size 1024x1024 --png --ref M --name icon --versioned --out A/icon/raw

# pack the approved raw of each sheet: walk_side FIRST (fixes the scale)
python scripts/sprite_pack.py A/walk_side/raw/walk_side_vNN.png     --asset A --id {id} --state walk   --dir side --frames 6 --cell 96 --fps 12 --flip-to left
python scripts/sprite_pack.py A/walk_up/raw/walk_up_vNN.png         --asset A --id {id} --state walk   --dir up   --frames 6 --cell 96 --fps 12
python scripts/sprite_pack.py A/walk_down/raw/walk_down_vNN.png     --asset A --id {id} --state walk   --dir down --frames 6 --cell 96 --fps 12
python scripts/sprite_pack.py A/attack_side/raw/attack_side_vNN.png --asset A --id {id} --state attack --dir side --frames 6 --cell 96 --fps 12 --hit-frame 4 --flip-to left
python scripts/sprite_pack.py A/death_side/raw/death_side_vNN.png   --asset A --id {id} --state death  --dir side --frames 6 --cell 96 --fps 10 --no-loop --flip-to left
python scripts/sprite_pack.py A/icon/raw/icon_vNN.png               --asset A --id {id} --state icon   --dir none --grid 1x1 --frames 1 --cell 128 --center --own-scale --fill 0.95
```
Projectile (ranged): like the icon with `--state projectile --dir side --cell 32 --fill 0.9`.
The packer writes `A/<sheet>/vNN/` (vNN = the raw's version) and updates `A/meta.json`.

## Enemy-specific review points (in addition to format.md)
- `up` really shows the back and `down` the face; legs/feet move in every walk frame.
- Attack frame 4 is clearly the moment of impact or release.
- Death ends in a still pose that stays on the ground line.
