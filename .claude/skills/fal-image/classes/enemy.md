# Class: Enemy

Inherits everything in `../format.md` (style, generation rules, output, pipeline, checklist).
Hierarchy: **format → class (enemy) → level → archetype (melee / ranged)**.
Only **Level 1** is defined for now (test set). Kind tag for files: `enemy`.

## Content slots (flexible, filled from the user's request)
| Slot | Meaning | Example (bandit request) |
|---|---|---|
| `{id}` | short snake_case id | `bandit` |
| `{design}` | one dense sentence that locks the look: body type, proportions, colors, gear, distinctive marks. Reused verbatim in every prompt | `a stocky bald bandit with a big round belly ..., drawn with chibi-like squat proportions: an oversized head about one third of the total height, ...` |
| `{body}` | motion profile for walks (animation.md §3): biped / quadruped / multi-legged / blob / flyer | `biped` |
| `{leg_anchor}` | how the model can tell the left leg from the right (biped); used by the walk blueprint | `He holds the sword in his RIGHT hand, so his RIGHT leg is the leg on the sword side and his LEFT leg is the leg on the side without the sword` |
| `{attack}` | the attack motion (user's words if given) | `a diagonal slash from high behind the shoulder down across the body` |
| `{death}` | how it dies (user's words if given) | `knocked backward off his feet, the sword flung away` |
| `{projectile}` | ranged only | `a glob of green venom` |

## Level 1: regular enemies (fodder of the first maps)
| Item | Value |
|---|---|
| Canvas @1x | **128 x 128** for every animation (@2x 256). One size for all states, so the engine needs a single offset |
| Body size | larger side of the body = 0.54 of the canvas (about 69 px in game), fixed by `walk_side`; the spare room is for weapon swings and flung props |
| Look | simple, few details, one accent color; must read at 48 px |
| Archetypes | `melee` (fights soldiers that block the road), `ranged` (shoots from a distance) |
| Move speed | `move_speed` in `meta.json`, px/s at 1x. The packer writes a default from the stride (2 steps per cycle, step = 0.4 x body height); tune it in the playtest (feet must not slide) and store it with `--move-speed` |

### Directions: 8-way movement from 5 generated sheets
| Moving toward | Sheet | How |
|---|---|---|
| right | `walk_side` | generated: true side profile facing right |
| left | `walk_left` | mirror of `walk_side` |
| down-right | `walk_down_side` | generated: 3/4 FRONT view facing down-right |
| down-left | `walk_down_left` | mirror of `walk_down_side` |
| up-right | `walk_up_side` | generated: 3/4 BACK view facing up-right |
| up-left | `walk_up_left` | mirror of `walk_up_side` |
| down | `walk_down` | generated: straight front view |
| up | `walk_up` | generated: straight back view |
The engine picks the sheet from the movement angle in 45° sectors (with a little hysteresis so a curve
does not flicker). Attack and death are side only (+ mirror): fights happen on the road, facing the target.

### State matrix, Level 1
| Sheet | Frames | Grid / `--size` | fps | Loop | Hit frame | Melee | Ranged |
|---|---|---|---|---|---|---|---|
| `walk_side`, `walk_down_side`, `walk_up_side`, `walk_down`, `walk_up` | **8** | 4x2 / `2048x1024` | 10 | yes | - | yes | yes |
| `attack_side` | **9** | 3x3 / `1536x1536` | 12 | yes | 5 | strike | shoot |
| `death_side` | **9** | 3x3 / `1536x1536` | 12 | no (holds last frame) | - | yes | yes |
| `projectile` | 1 | `1024x1024` | - | - | - | - | yes |
| `icon` | 1 | `1024x1024` | - | - | - | yes | yes |

Melee = master + 2 view references + 7 key-pose stages (5 walks, attack, death) + 5 walks + attack + death
+ icon = **18 calls** (~$0.24 at `low`). Ranged adds the projectile = 19.
(Why 8 for walks: a walk is 2 steps x 4 key poses, an even loop. 9 for attack/death: more in-betweens, smoother.)

## Animation design (motion first)
Every animated sheet of this class follows `../animation.md`: motion card -> motion phases from the
profile -> frame-by-frame blueprint in `A/<sheet>/blueprint.md` -> staged generation (key poses first)
-> review loop. The prompts below are written FROM the blueprint; a list of alternating poses is not a spec.
Class defaults for the motion card:

| Sheet | Profile (animation.md §3) | Type | Frames / fps | Stage 1 (key + breakdown, 2x2 `1024x1024`) |
|---|---|---|---|---|
| walks (5 views) | biped walk (or the `{body}` profile) | cyclic, translates at `move_speed` | 8 / 10 | F1 contact L, F3 passing, F5 contact R, F7 passing |
| `attack_side` | attack (melee) or ranged/cast | transition-into ready (loops while fighting) | 9 / 12, hit F5 | ready, wind-up peak, impact, recovery |
| `death_side` | death | one-shot, holds F9 | 9 / 12 | hit reaction, collapse, ground impact, final pose |

### Biped walk blueprint (default for all five walk views)
Use the 8-frame table in `animation.md` §4 (contact, down, passing, up, then the mirrored step).
Expected lead foot for the leg check: `LL-RRR-L`. View-specific notes:
- `walk_side`: true profile; legs read as near/far, the far leg a slightly darker shade.
- `walk_down_side` / `walk_up_side`: 3/4 views; the step goes diagonally down-right / up-right.
- `walk_down`: the leading foot is drawn lower and bigger (closer to the viewer).
- `walk_up`: the trailing boot shows its sole to the viewer.
- L/R are the character's own legs, tied to something visible in `{leg_anchor}` (e.g. the weapon side).
- Mirrored directions swap L and R; the motion is unchanged, which is correct.

**`{walk_poses}`** = one sentence per frame, written from the blueprint rows, e.g. for frames 1-4:
`{leg_anchor}. Frame 1 (contact): LEFT heel lands ahead, RIGHT leg stretched back pushing off its toes, body at mid height, the sword arm swung forward. Frame 2 (down): weight drops onto the bent LEFT leg, RIGHT toe lifting, body at its lowest, belly bouncing down. Frame 3 (passing): RIGHT leg swings under the body with the knee raised, LEFT leg supporting, body rising. Frame 4 (up): pushing off the LEFT toes, RIGHT leg reaching forward, body at its highest, the sword arm swung back.`
then frames 5-8 as the mirrored step ending "flowing into frame 1". If steps come out tiny, add:
`Exaggerated cartoon march: big wide steps, knees lifted high, the body bobbing clearly up and down.`

Other bodies use their profile in `animation.md` §3 (quadruped, multi-legged, blob, flyer); write
their blueprint the same way and agree the expected contact pattern with the user the first time.

### Walk-specific checks (part of the review loop in animation.md §8)
1. `python scripts/leg_check.py A/<sheet>/vNN` -> read `legcheck.png`; write the lead foot per frame in
   `history.md` (`legs LL?RRR?L`, `?` = unreadable).
2. Compare with the blueprint: `python scripts/leg_check.py --observed <...> [--expected LL-RRR-L] [--bad n]`.
   It prints the `--order` that fixes wrong frames from correct ones (copy the raw to the next version,
   re-pack with it); if no correct frame exists, regenerate (counts as a round).
3. `python scripts/motion_check.py A/<sheet>/vNN`: a walk needs a visible bob (lowest on the "down"
   rows, highest on the "up" rows), no FROZEN or SPIKE transitions, no DRIFT, and a smooth `8->1`.
4. `?` frames, timing and foot slide are unverified until seen moving: the user checks them in Motion
   Lab; **the user's reading wins** and becomes `--observed`.

Note: `bandit` walk_down_side v02 was fixed to `LRLRLRLR` under the earlier "alternate every frame"
rule (approved 2026-10-13). That rule is retired; regenerate that sheet from the blueprint when it is next edited.

## View references (before the walk sheets; tested on `bandit`)
The master is a 3/4 view, and the model pulls every sheet back toward it: "true side profile" and
"straight front view" in the prompt alone were ignored twice. So first make two single-sprite view
references from the master, review them, and pass each as the FIRST `--ref` (master second):
- `view_side` (for `walk_side`, attack, death): "FLAT SIDE PROFILE like a paper cutout, facing exactly
  right: chest and belly pointing to the right edge, the back of the head pointing left, only one eye visible".
- `view_front` (for `walk_down`): "Straight FRONT view, perfectly facing the viewer, mirror-symmetric".
```
python scripts/gen_image.py "<view prompt>" --size 1024x1024 --png --ref M --name view_side --versioned --out A/master/raw
python scripts/gen_image.py "<sheet prompt>" --size 2048x1024 --png --ref A/master/raw/view_side_vNN.png --ref M --name walk_side --versioned --out A/walk_side/raw
```
Sheet prompts using them start with: "Use the FIRST reference image for the exact viewing angle and both
reference images for the character design."

Front and back walks: near/far legs mean nothing there; always use `{leg_anchor}` (e.g. the weapon side).
Stage 1 (key poses) of a walk uses the same view reference as its full sheet.

## Prompt blocks (fixed wording; only the slots change)
Every prompt ends with `{STYLE}`; sheets add `{GRID}` (with the sheet's columns, rows and frame count) then `{BG}`;
single sprites add `{BG}`. Every sheet also gets `{SIZE_LOCK}`:
> Draw the character at the same size as in the reference image in every cell; if a prop flies away,
> leave room for it inside the cell instead of shrinking the character.

**master** (`--size 1024x1024 --png`)
> Single game enemy sprite: {design}. Three-quarter view facing down-right, as if walking toward the
> bottom-right of the screen. Neutral ready pose, full body, centered, filling about 70% of the frame.
> {BG} {STYLE}

**walk_side** (`--size 2048x1024 --png --ref <stage-1 key poses> --ref <view_side> --ref <master>`)
> Use the FIRST reference image for the key poses (frames 1, 3, 5 and 7 must match its four poses in
> order), the others for the viewing angle and the character design; redraw in the style described.
> Sprite sheet of {design}. An 8-frame walk cycle in a TRUE SIDE PROFILE, facing and moving right:
> exactly 90 degrees from the camera, only one eye visible, both legs visible side by side.
> {walk_poses} {SIZE_LOCK} {GRID 4x2, 8} {BG} {STYLE}

**walk_down_side**: same flags
> ... An 8-frame walk cycle in a three-quarter FRONT view, walking diagonally toward the bottom-right
> of the screen: the face and the front of the body visible, turned 45 degrees to the right. {walk_poses} ...

**walk_up_side**: same flags
> ... An 8-frame walk cycle in a three-quarter BACK view, walking diagonally toward the top-right of the
> screen: the back of the body visible, the face hidden, turned 45 degrees to the right. {walk_poses} ...

**walk_down**: same flags
> ... An 8-frame walk cycle in a symmetrical FRONT view: walking straight down the screen toward the
> viewer, face visible, mirror-symmetric. Not a side view, not a three-quarter view. The stepping foot is
> drawn lower and bigger (closer to the viewer). {walk_poses, with left/right legs instead of near/far} ...

**walk_up**: same flags
> ... An 8-frame walk cycle seen straight from BEHIND, walking up the screen away from the viewer: the
> back is visible and the face is hidden. {walk_poses, with left/right legs instead of near/far} ...

**attack_side** (`--size 1536x1536 --png --ref <stage-1 key poses> --ref <view_side> --ref <master>`)
Per-frame sentences come from the attack blueprint (phases: ready, anticipation, wind-up, action, impact,
follow-through, recovery); the default wording below matches the default blueprint:
> Use the reference image only for the character design; redraw it in the style described.
> Sprite sheet of {design} performing {attack}, true side profile facing right. Frame 1: ready stance.
> Frame 2: anticipation, crouching slightly. Frame 3: wind-up at its peak. Frame 4: the swing starts.
> Frame 5: the moment of impact with a short motion smear (the hit). Frame 6: follow-through.
> Frame 7: follow-through held. Frame 8: recovering. Frame 9: back to the ready stance of frame 1.
> {SIZE_LOCK} {GRID 3x3, 9} {BG} {STYLE}
(Ranged: frame 5 is the release; no projectile in flight.)

**death_side**: same flags as attack (blueprint phases: hit reaction, loss of balance, collapse,
ground impact, settle, final hold)
> Use the reference image only for the character design; redraw it in the style described.
> Sprite sheet of {design} dying, true side profile facing right. Frame 1: struck by a hit, body
> jolted backward. Frame 2: staggering. Frame 3: losing balance. Frame 4: falling. Frame 5: hitting the
> ground. Frame 6: a small bounce. Frame 7: settling. Frame 8: {death}, final pose. Frame 9 (held):
> exactly like frame 8 but completely still, eyes closed. No debris, no motion lines.
> {SIZE_LOCK} {GRID 3x3, 9} {BG} {STYLE}
A custom death (e.g. knocked back, weapon flung away): rewrite frames 1-8 to tell that story, keep
frame 9 = frame 8 still, and add "Keep the body AND the <weapon> fully inside each frame's own cell".

**projectile** (ranged only; `--size 1024x1024 --png --ref <master>`)
> Single projectile sprite fired by the enemy in the reference image: {projectile}. Pointing right,
> centered, small and simple, filling about 40% of the frame. {BG} {STYLE}

**icon** (`--size 1024x1024 --png --ref <master>`)
> Round enemy portrait icon: ONLY the head and shoulders of {design}, cropped at the chest, facing
> slightly right, inside a circular badge with a thick dark outline and a muted stone-grey rim, plain
> muted khaki background inside the circle. {BG} {STYLE}

## Commands (Level 1, run from the project root)
Let `A=out/enemies/{id}` and `M=A/master/raw/master_vNN.png` (the approved master).
```
# master candidates
python scripts/gen_image.py "<master prompt>" --size 1024x1024 --png --name master --versioned --out A/master/raw
# stage 1 per animated sheet: key + breakdown poses, 2x2 (review before stage 2)
python scripts/gen_image.py "<key-pose prompt>" --size 1024x1024 --png --ref A/master/raw/view_side_vNN.png --ref M --name walk_side_keys --versioned --out A/walk_side/raw
# stage 2: full sheets (independent sheets run in parallel), first --ref = the approved key-pose sheet
python scripts/gen_image.py "<walk prompt>"   --size 2048x1024 --png --ref A/walk_side/raw/walk_side_keys_vNN.png --ref A/master/raw/view_side_vNN.png --ref M --name walk_side --versioned --out A/walk_side/raw
python scripts/gen_image.py "<attack prompt>" --size 1536x1536 --png --ref M --name attack_side --versioned --out A/attack_side/raw
python scripts/gen_image.py "<icon prompt>"   --size 1024x1024 --png --ref M --name icon        --versioned --out A/icon/raw

# pack: walk_side FIRST (sets the asset's scale, reference body size and default move_speed)
python scripts/sprite_pack.py A/walk_side/raw/walk_side_vNN.png           --asset A --id {id} --state walk --dir side      --grid 4x2 --frames 8 --cell 128 --fill 0.54 --fps 10 --flip-to left --align torso
python scripts/sprite_pack.py A/walk_down_side/raw/walk_down_side_vNN.png --asset A --id {id} --state walk --dir down_side --grid 4x2 --frames 8 --cell 128 --fps 10 --flip-to down_left --align torso
python scripts/sprite_pack.py A/walk_up_side/raw/walk_up_side_vNN.png     --asset A --id {id} --state walk --dir up_side   --grid 4x2 --frames 8 --cell 128 --fps 10 --flip-to up_left --align torso
python scripts/sprite_pack.py A/walk_down/raw/walk_down_vNN.png           --asset A --id {id} --state walk --dir down      --grid 4x2 --frames 8 --cell 128 --fps 10 --align torso
python scripts/sprite_pack.py A/walk_up/raw/walk_up_vNN.png               --asset A --id {id} --state walk --dir up        --grid 4x2 --frames 8 --cell 128 --fps 10 --align torso
python scripts/sprite_pack.py A/attack_side/raw/attack_side_vNN.png       --asset A --id {id} --state attack --dir side   --grid 3x3 --frames 9 --cell 128 --fps 12 --hit-frame 5 --flip-to left
python scripts/sprite_pack.py A/death_side/raw/death_side_vNN.png         --asset A --id {id} --state death  --dir side   --grid 3x3 --frames 9 --cell 128 --fps 12 --no-loop --flip-to left
python scripts/sprite_pack.py A/icon/raw/icon_vNN.png                     --asset A --id {id} --state icon   --dir none   --grid 1x1 --frames 1 --cell 128 --center --own-scale --fill 0.95
```
- Every sheet after `walk_side` is matched to its body size automatically (the packer prints
  `body matched xK`). K far from 1 means the model drew that sheet bigger/smaller; the packer fixes it.
  If it then warns about overflow, regenerate with a stronger `{SIZE_LOCK}`.
- Walks are packed with `--align torso` (registers the head+torso, so the body does not slide sideways
  when the stride changes width). Then run the walk-specific checks above.
- Set a tuned speed: re-pack `walk_side` (same version is allowed) with `--move-speed <px/s>`.
- Projectile (ranged): like the icon with `--state projectile --dir side --cell 32 --fill 0.9`.

## Enemy-specific review points (in addition to format.md)
- Every animated sheet: classified Pass / Needs Revision / Fail per `animation.md` §7, defects named by
  transition (`3->4`, `8->1`), unverified items listed.
- Walk: lead foot matches the blueprint (`LL-RRR-L`), visible bob, no drift, smooth `8->1`.
- `walk_side` is a true profile; `*_side` diagonals are clearly 3/4; `up` shows the back, `down` the face.
- Attack frame 5 is clearly the moment of impact or release; anticipation and follow-through are visible.
- Death ends in a still pose on the ground line, at the same character size as the walk.
