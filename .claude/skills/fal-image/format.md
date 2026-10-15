# Game asset format (shared by every class)

Every class file in `classes/` (enemy, tower, hero, ...) inherits everything here. A class may add
rules but must not change this frame. This skill makes **stills**: the approved master of a character
and its standard views, plus icons and other single images. **Animation is never drawn here**: the
`video-sprite` skill animates the approved stills (image-to-video) and exports the frames into the same
asset folder. Style was derived from the reference pack in `ref/assets/` (read-only, for looking only:
never send it to the API, never copy its designs, never name the game it comes from).

## 1. Style block `{STYLE}` (fixed, append to every prompt)

> Flat vector-style 2D cartoon game art for a top-down fantasy tower defense game.
> Thick, uniform near-black outlines around every shape and major inner detail.
> Flat color fills with only 2-3 tone hard-edged cel shading: no gradients, no airbrush,
> no glow, no painterly texture, no realistic detail, no fur, no noise.
> Muted earthy palette: stone grey, olive green, khaki, rust brown, dull leather and bone,
> with at most one small saturated accent color per asset.
> Simple, chunky, readable shapes that still read clearly when shrunk to 64 pixels.
> Characters are squat and stocky with an oversized head, hands and weapon.
> High top-down camera tilted about 60 degrees: the top of the head and shoulders are visible.
> Light comes from the top-left.

If `style.md` exists at the project root it replaces this block.

## 2. Generation rules (fixed; tested 2026-10-13/14)
| Rule | Value | Why |
|---|---|---|
| Model | `gpt-image-2` (default) | follows the style; gpt-image-1.5 drew a furry 3D look |
| Size | `--size 1024x1024` for every still | master, views, icon, projectile |
| Background | flat magenta `#FF00FF` + `--png`, **no `--transparent`**; the tools key it out | gpt-image-2 has no transparency on fal |
| Consistency | every image after the master uses `--ref <approved master>` and repeats `{design}` verbatim | keeps design, colors, gear and proportions identical in every view |
| Pose | every view: the same neutral standing ready pose, full body and weapon inside the frame, filling about 70% | video-sprite starts every clip from this still; a cut-off weapon or an odd pose shows in every frame |
| Quality | `low` while testing; `medium/high` only after the user asks | cost |

`{BG}` (append to every prompt):
> Background: one flat solid pure magenta color (#FF00FF) everywhere, no gradient, no ground,
> no shadow, no scenery, no text, no border. Do not use magenta or pink anywhere on the subject.

## 3. Standard views of a character (the "forms" video-sprite animates)
A top-down game moves in 8 directions; 5 views are generated, the 3 left-facing ones are mirrors.
| Still (`stills/`) | View | Animated by video-sprite as | Required |
|---|---|---|---|
| `master_vNN` | three-quarter FRONT, facing down-right (the design reference) | `move/walk_down_side` (+ mirror down-left) | yes |
| `view_side_vNN` | true side profile, facing right | `move/walk_side`, `attack/attack_side`, `death/death_side`, `hurt`, `idle` (+ mirror left) | yes |
| `view_front_vNN` | straight front, facing the viewer | `move/walk_down` | yes |
| `view_back_vNN` | straight back, facing away | `move/walk_up` | yes |
| `view_up_side_vNN` | three-quarter BACK, facing up-right | `move/walk_up_side` (+ mirror up-left) | yes |
| `icon_vNN` | head-and-shoulders portrait badge | `ui/icon` (packed with `sprite_pack.py`) | yes |
| `pose_ready_side_vNN` | side profile in a combat-ready stance (weapon raised, knees bent) | optional start still for `attack`/`hurt` when the neutral stance reads too passive | optional |
| `turnaround_vNN` | the 5 views side by side (`templates.md` "turn") | review only, never animated | optional |
The view prompts are in the class file ("Standard views"). Make and approve them in this order: master,
then side, front, back, up_side (each with `--ref <master>`), then the icon.

## 4. Files, folders and versions (fixed)
One folder per asset. A person opens at most 4 levels: category, sheet, version. `.work/` is for tools only.
```
out/<kind>s/<id>/                         e.g. out/enemies/bandit/
  brief.md                                request, class/level/archetype, filled slots, approved stills
  history.md                              one row per still or video take: version, score, verdict, issue, change
  meta.json                               engine metadata: one canvas, pivot and body height for every action
  stills/                                 INPUT stills (this skill): master_v02.png, view_side_v01.png ... (+ .json prompt)
  move/                                   one folder per category (scripts/asset_layout.py)
    walk_side/                            one folder per sheet
      clip_t01.mp4 (+ .json)              SOURCE: the video the frames were cut from (.json = model, prompt, cost)
      v01/                                OUTPUT: one folder per export; the highest vNN is the final one
        preview.gif                       look here first
        sheet.png                         horizontal sheet @2x
        frames/@2x/enemy_bandit_walk_side_01.png ...   frames for the game (also @1x)
        check/                            motioncheck.txt, transitions.png, legcheck.png, take_review.png
    walk_down_side/ walk_down/ walk_up_side/ walk_up/
  attack/attack_side/                     same layout
  death/death_side/
  ui/icon/v01/                            packed icon (sprite_pack.py from stills/icon_vNN.png)
  .work/                                  tools only (video-sprite sets, pruned to their decisions)
```
Categories: `move` (walk, run), `attack` (attack, cast), `death`, `hurt`, `idle`, `ui` (icon), `projectile`.
- Still names: `<name>_vNN.png`, made by `gen_image.py --name <name> --versioned --out <asset>/stills`.
- Frame names keep kind and id (`enemy_bandit_walk_side_03.png`) so they are unique inside a game project.

Game-ready frames (the same for every action of an asset):
| Item | Value |
|---|---|
| File type | PNG-32 RGBA, transparent; `@2x` master and `@1x` in-game |
| Canvas | **one canvas for every action of an asset** (`meta.json` "cell"; class/level decides, Level 1 enemy 256x128 at 1x). No action gets a bigger or smaller frame, so the engine never rescales one action against another |
| Body | **one body height for every action** (`meta.json` "body_height_2x", set by the first export); a sheet whose body differs by more than 4% is rescaled on export |
| Pivot | feet, bottom-center: x 0.5, y 0.88 of the canvas; icons are centered |
| Motion | `move_speed` (px/s at 1x) in `meta.json`, tuned in the playtest so the feet do not slide |

`history.md` row format (append one row after reviewing every still or take, including rejected ones):
`| date | sheet/still | vNN | model | score | approved/rejected/final/awaiting user | issue | change for next version | requested by (pipeline/user: "...") |`

## 5. Run modes (fixed for every class)
**Default (no `--auto`): master checkpoint**
1. Write `brief.md` (fill the class's content slots from the request; invent sensible details).
2. Generate the master into `stills/`; self-review it and regenerate while it fails the checklist (max 3).
3. **Stop.** Show the user the master candidates (paths + scores + issues), recommend one, and wait.
4. When the user approves one ("chốt v02"), record it in `brief.md` and `history.md`, then make the other
   standard views and the icon (§3) the same way (each reviewed, max 3 versions), show them, and wait for
   approval before any animation is paid for.
5. Animation: hand over to the `video-sprite` skill with the approved stills.

**`--auto`**: as above, but approve the master and the views yourself (score >= 8), then continue with
`video-sprite` (it still asks before paying for video unless the request already approved the cost).

**Edit an existing character** (e.g. "đổi đao thành rìu"): changing the master or `{design}` affects every
view and every animation: confirm with the user first, then regenerate the stills, then the animations.
Fixing one view only (e.g. the back view shows the face): generate the next version of that still, and
re-animate only the actions that start from it.

## 6. Review checklist for stills (score 1-10, redo below 8)
- Same character as the master: colors, gear, proportions, the weapon's shape and the hand that holds it.
- The view is exact: side = true profile facing right (one eye); front = mirror-symmetric, face visible;
  back = no face; 3/4 front faces down-right; 3/4 back faces up-right, face hidden.
- Neutral standing ready pose, full body and weapon inside the frame with margin, nothing touching the edges.
- Style: thick dark outlines, flat 2-3 tone shading, muted palette, no gradients, glow or fur.
- Flat magenta background only; no magenta or pink on the subject, no ground, shadow or text.
