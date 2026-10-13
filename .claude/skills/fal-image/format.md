# Game asset format (shared by every class)

Every class file in `classes/` (enemy, tower, hero, ...) inherits everything here.
A class may add rules but must not change this frame. **Animated sheets are also designed with
`animation.md`** (motion card, blueprint, staged key poses, motion checks); this file keeps the style,
generation rules, files and packing those animations must respect. Style was derived from the
reference pack in `ref/assets/` (read-only, for looking only: never send it to the API,
never copy its designs, never name the game it comes from).

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

## 2. Generation rules (fixed; tested 2026-10-13)
| Rule | Value | Why |
|---|---|---|
| Model | `gpt-image-2` (default) for everything | follows style and per-frame poses; gpt-image-1.5 drew furry 3D look and copied one frame 6x |
| Background | flat magenta `#FF00FF` + `--png`, **no `--transparent`**; `sprite_pack.py` keys it out and un-mixes translucent smears/glows (no pink tint) | gpt-image-2 has no transparency on fal |
| Consistency | every image after the master uses `--ref <master.png>` | keeps design, colors, eye count |
| Sheet layout | a grid of 512 px cells, row-major: **8 frames = 4x2 at `2048x1024`**, **9 frames = 3x3 at `1536x1536`**, **4 key poses = 2x2 at `1024x1024`** (stage 1 of an animation) (the class says which) | one long row is too short; the model makes a grid anyway. 6 frames looked choppy in the playtest |
| Single sprite | `--size 1024x1024` | master, icon, projectile |
| Poses | write every frame's pose **from the motion blueprint** (`animation.md` §4), key poses first (§5) | a bare pose list gave identical frames, repeated legs and no weight transfer |
| Directions | 8-way movement from 5 generated views: `side` (true profile, right), `down_side` (3/4 front, down-right), `up_side` (3/4 back, up-right), `down` (front), `up` (back). Left, down-left, up-left = mirrors (never generated) | 4 directions made the character snap at every bend of the road |
| Size lock | every sheet prompt says the character keeps the reference size; `sprite_pack.py` also matches each sheet's body size to `walk_side` | the model drew a death sheet ~27% smaller to fit a flung sword |
| Quality | `low` while testing; `medium/high` only after the user approves | cost |

`{BG}` (append to every prompt):
> Background: one flat solid pure magenta color (#FF00FF) everywhere, no gradient, no ground,
> no shadow, no scenery, no text, no border. Do not use magenta or pink anywhere on the subject.

`{GRID}` (append to every sheet prompt, before `{BG}`; fill in the sheet's columns, rows and frames):
> Layout: a {COLS}x{ROWS} grid, {COLS} columns and {ROWS} rows of {N} equal cells, read left to right, top row first.
> One figure per cell, centered, with clear empty space between figures. The exact same character,
> same colors, same proportions and the same size in every frame, standing on the same ground line
> in each row. No grid lines, no frame numbers, no labels.

## 3. Files, folders and versions (fixed)
One folder per asset, one subfolder per sheet. Every generation is a new version; nothing is overwritten.
```
out/<kind>s/<id>/                     e.g. out/enemies/spider/
  brief.md                            request, class/level/archetype, filled slots, approved master
  history.md                          one row per generated raw: version, score, verdict, issue, change
  meta.json                           engine metadata; per sheet: final version + its source raw
  master/raw/master_v01.png (+.json)  master candidates (never packed)
  walk_side/                          one folder per sheet: walk_side, walk_up, walk_down, attack_side, death_side, icon ...
    blueprint.md                      motion card + frame-by-frame blueprint (animation.md), written before generating
    raw/walk_side_keys_v01.png        stage 1: key + breakdown poses (2x2), reviewed before the full sheet
    raw/walk_side_v01.png (+.json)    every raw the model returned (.json = exact prompt, model, refs, cost)
    raw/walk_side_v02.png
    v02/                              packed from raw v02 (only approved raws get packed)
      enemy_spider_walk_side.png        horizontal sheet @2x
      enemy_spider_walk_side_preview.gif
      frames/@2x/enemy_spider_walk_side_01.png ...
      frames/@1x/enemy_spider_walk_side_01.png ...
      legcheck.png, transitions.png, motioncheck.txt   review outputs (leg_check.py, motion_check.py)
```
- **The highest `vNN/` folder of a sheet is its final version.** A packed folder has the number of the raw it came from.
- Raw names: `<sheet>_vNN.png`, made by `gen_image.py --name <sheet> --versioned --out <asset>/<sheet>/raw`.
- Frame names keep kind and id (`enemy_spider_walk_side_03.png`) so they are unique inside a game project.
- A few wrong frames in an otherwise good sheet (e.g. the same leg steps twice): fix them for free by
  re-ordering frames instead of regenerating: copy the raw to the next version and pack it with
  `--order 1,2,3,4,5,4,3,8` (reuse frames that show the right pose). Log it in `history.md`.
- To go back to an older version (e.g. v02 after v03): copy `raw/<sheet>_v02.*` to the next free number,
  pack it, and log it in `history.md` ("restore of v02"). `sprite_pack.py` refuses to pack below the final.

Game-ready frames (`sprite_pack.py`):
| Item | Value |
|---|---|
| File type | PNG-32 RGBA, transparent |
| Resolutions | `@2x` master and `@1x` in-game; cell size comes from the class/level |
| Pivot | feet, bottom-center: x 0.5, y 0.88 of the cell (12% above the bottom); icons are centered. Horizontal registration: bbox centre, or `--align torso` (head+torso centre) for cyclic in-place motion such as walks, so the body does not slide when the stride changes |
| Canvas | one canvas size for every animation of an asset (class/level decides, e.g. 128x128) so the engine needs one offset |
| Scale | `walk_side` sets the base scale; every later sheet is matched to the same body size (packer prints `body matched xK`) |
| Motion | `move_speed` (px/s at 1x) in `meta.json`: default from the stride, tuned in the playtest so the feet do not slide |

`history.md` row format (append one row after reviewing every raw, including rejected ones):
`| date | sheet | vNN | model | score | approved/rejected/final/awaiting user | issue | change for next version | requested by (pipeline/user: "...") |`

## 4. Run modes (fixed for every class)
Read the mode from the user's request:

**Default (no `--auto`): master checkpoint**
1. Write `brief.md` (fill the class's content slots from the request; invent sensible details).
2. Generate the master into `master/raw/`; self-review it and regenerate while it fails the checklist
   (max 3 versions).
3. **Stop.** Show the user the master candidates (paths + scores + issues), recommend one, and wait.
4. When the user approves one ("chốt v02"), record it in `brief.md` and `history.md`, then run the
   sheets exactly as in auto mode steps 3-6 (no further stops).

**`--auto`: full run**
1-2. As above, but approve the master yourself (score >= 8).
3. Motion design, then sheets: for every animated sheet write `A/<sheet>/blueprint.md` (motion card +
   frame-by-frame blueprint, `animation.md` §1-4), generate and review stage 1 (key + breakdown poses),
   then the full sheet with the approved key poses as the first `--ref` (§5). All images use
   `--ref <approved master> --png`; independent sheets run in parallel. Non-animated images (icon) skip this.
4. Pack each approved raw with `sprite_pack.py`, `walk_side` first (it fixes the asset's scale).
   Every walk sheet then goes through the class's **leg check** (`scripts/leg_check.py`); a broken leg
   order is fixed with `--order` (a new version, no API call) before the sheet can be final.
   The packer must report `split=gaps`; `split=equal` means figures touch: regenerate that sheet.
5. Review each packed sheet with the review loop in `animation.md` §8 (`motion_check.py`, onion
   transitions, leg check for walks) and classify it Pass / Needs Revision / Fail (§7), naming defective
   transitions (`3->4`, `8->1`). Not Pass -> fix (re-order, regenerate the stage at fault, adjust fps or
   move_speed), max 3 regeneration rounds per sheet. Log every raw and every verdict in `history.md`.
6. Playtest: `python scripts/build_playtest.py` collects the final frames of every asset into
   `out/playtest/`; publish `out/playtest/index.html` with the Artifact tool (all files in that folder,
   same artifact URL each time if one exists) so the user can watch the animations moving on a map.
7. Report: the final version of every sheet (path to its `vNN/` folder), scores, rounds, total cost,
   the playtest link. Remind the user that frames may need hand-alignment: image models are not pixel-precise.

**Edit an existing asset** (e.g. "make the spider's attack bite more powerful")
1. Read the asset's `brief.md`, `history.md` and `meta.json`; reuse the approved master and `{design}` verbatim.
2. Change only the slot(s) the request is about (e.g. `{attack}`/attack poses); keep every other fixed block.
   Record the new slot value in `brief.md`. For a change of motion, update the sheet's `blueprint.md`
   first (create it if the sheet predates it), then regenerate from the stage that the change affects.
3. Generate the next raw version of that sheet only (`--versioned` picks the number), review, iterate
   (max 3), pack the approved one into its `vNN/`, log every raw in `history.md` with
   requested by = the user's words.
4. Report old final vs new final side by side (paths). The previous version stays untouched.
- Changing the master or `{design}` affects every sheet: confirm with the user first, then regenerate all sheets.

## 5. Review checklist (score 1-10, redo below 8)
Animated sheets: the structural and motion checks and the Pass / Needs Revision / Fail classification
in `animation.md` §7 come first; a sheet never passes on frame count alone. Then:
- Same character as the master in every frame: colors, gear, proportions.
- The right number of separate figures (`split=gaps`).
- Walks match their blueprint (lead-foot pattern via the leg check, e.g. `LL-RRR-L`); same character size across all sheets.
- Direction correct (side faces right; up shows the back; down shows the face).
- Style: thick dark outlines, flat 2-3 tone shading, muted palette, no gradients, glow or fur.
- Poses follow the blueprint and read as the requested action; cyclic sheets flow from the last frame to the first.
- No leftover magenta fringe, background, ground, shadow or text; silhouette readable at @1x.
