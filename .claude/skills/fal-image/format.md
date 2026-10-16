# Game asset format (shared by every class)

Every class file in `classes/` (enemy, tower, hero, ...) inherits everything here. A class may add
rules but must not change this frame. This skill makes **stills**: the approved master of a character
and its standard views, plus icons and other single images. **Animation is never drawn here**: the
`video-sprite` skill animates the approved stills (image-to-video) and exports the frames into the same
asset folder. Style references live in `ref/` (`ref/assets/`, `ref/hero/`; read-only, for looking only:
never send them to the API, never copy their designs, never name the game they come from).

## 1. Style block `{STYLE}` (fixed, append to every prompt)
The block fixes the **design principles** (how things are drawn), not a look: body type, costume, armour,
weapon, colours and which parts are exaggerated belong to each character's `{design}`, so a robed mage, an
armoured knight and a fire elemental can all share it.

> Stylized 2D vector cartoon game art for a top-down fantasy tower defense game, designed to read at about
> 64 pixels tall.
> Simple design: big clear shapes and a strong silhouette; small details are left out or merged into larger
> shapes; faces, hands, armour and clothing are suggested with a few lines, never rendered in fine detail.
> Stylized, exaggerated cartoon proportions, not realistic anatomy (about 2.5 to 4 heads tall): the parts
> that express the character's role are enlarged and the rest is shrunk, so the silhouette reads at 64 pixels.
> Colour: flat solid fills only, no gradients, no airbrush, no painterly texture, no noise, no realistic
> rendering. Volume and shadow come from 2-3 hard-edged tones of the same colour (shadow, base, light), plus a
> few small highlight shapes.
> Thick clean outlines in a dark shade of the neighbouring colour.
> Effects (fire, ice, magic, poison, glow, energy) are drawn as stacked layers of flat single-colour vector
> shapes with an outline that follows the effect's form (flame tongues, ice shards, drips, sparks), never as
> soft blur or gradient glow.
> High top-down camera tilted about 60 degrees; light comes from the top-left.

Why each line (from `ref/hero`, a 64 px fire elemental, studied 2026-10-16): the face is a brow line and an
eye slit; hands are mitten shapes; muscles are 1-2 lines; the body is 3 tones of one orange with a few light
specks; the outline is dark brown, not black; the fire around it is flat yellow layers with flame-tongue
edges; it is about 3.8 heads tall and top-heavy (huge shoulders and arms, small head, short legs), its
exaggeration chosen for its role. It is vector art drawn large and scaled down (hundreds of colours,
anti-aliased edges), **not pixel art**: never write "pixel art" in a prompt (the model then draws fake
pixels that blur when the tools scale them).

`{design}` carries what the style leaves open: body type and the parts it exaggerates ("top-heavy: huge
shoulders and arms, small head, short legs"), costume and gear, the weapon and the hand that holds it, the
dominant colour family and one accent, any effect and its colours ("yellow flame layers around an orange body").

If `style.md` exists at the project root it replaces this block. Assets made before 2026-10-16 (bandit) used
the previous block (muted earthy palette, near-black outlines, oversized chibi head); restyle them only on request.

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
One folder per asset (`out/<class>/<id>/`: enemies, heroes, towers ...). Sources keep every version; state
folders keep only the one final version; `.work/` holds the tools' intermediate data and is not in git.
```
out/<class>/<id>/                         e.g. out/heroes/centaur/
  brief.md                                request, class/level, filled slots, approved stills and poses
  history.md                              one row per still or video take: version, score, verdict, issue, change
  meta.json                               engine metadata: one canvas, pivot and body size for every action
  stills/                                 SOURCE images (this skill), every version: master_v03.png, pose_run_v01.png ... (+ .json)
  raw/                                    SOURCE videos (video-sprite), every take, saved as soon as the model returns
    run_down_side_run_t02.mp4 (+ .json)   <action>_<set>_tNN: the .json holds model, prompt, cost, request id
  idle/ move/ attack/ death/ ...          STATE folders (category, scripts/asset_layout.py): ONE final version each
    move/run_down_side/                   one folder per sheet
      preview.gif                         look here first
      sheet.png                           horizontal sheet @2x
      frames/@2x/hero_centaur_run_down_side_01.png ...   frames for the game (also @1x)
      check/                              motioncheck.txt, transitions.png, legcheck.png, take_review.png
  ui/icon/                                packed icon (sprite_pack.py from stills/icon_vNN.png)
  .work/                                  tools only, not in git (video-sprite sets pruned to their decisions)
```
Re-exporting a sheet replaces its state folder; the take it came from is named in `meta.json` (`version`,
`source`), and every other take stays in `raw/` (any of them can be accepted and exported later).
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

**Restyle a character** (same character, new look: "restyle bandit sang pixel art", a new `style.md`):
1. Write the new style block (into `style.md` if it should apply to every asset, else into `brief.md`
   as `{STYLE}` for this character) and record the request in `brief.md`.
2. New master: `--ref <current approved master>`, prompt starts "Use the reference image for the character
   design (shape, gear, colours, proportions, the hand that holds the weapon); redraw it ONLY in the new
   style described", then `{design}`, the master view, `{BG}`, the new `{STYLE}`. Next free `master_vNN`;
   old stills stay. Stop for approval (unless `--auto`).
3. Every standard view again from the NEW master (§3), next free versions; approve them.
4. Update `brief.md` (approved stills) and `history.md`; animations are then redone by `video-sprite`
   from the new stills (paid clips; old sheets stay as earlier versions).

**Edit an existing character** (e.g. "đổi đao thành rìu"): changing the master or `{design}` affects every
view and every animation: confirm with the user first, then regenerate the stills, then the animations.
Fixing one view only (e.g. the back view shows the face): generate the next version of that still, and
re-animate only the actions that start from it.

## 6. Review checklist for stills (score 1-10, redo below 8)
- Same character as the master: colors, gear, proportions, the weapon's shape and the hand that holds it.
- The view is exact: side = true profile facing right (one eye); front = mirror-symmetric, face visible;
  back = no face; 3/4 front faces down-right; 3/4 back faces up-right, face hidden.
- Neutral standing ready pose, full body and weapon inside the frame with margin, nothing touching the edges.
- Style (§1): simple big shapes and a clear silhouette at 64 px; no fine detail on face, hands or clothes;
  stylized proportions as `{design}` says; flat fills with 2-3 hard tones per colour, no gradient or blur;
  thick outlines in a dark shade of the neighbouring colour; effects as flat layered shapes, not glow.
- Flat magenta background only; no magenta or pink on the subject, no ground, shadow or text.
