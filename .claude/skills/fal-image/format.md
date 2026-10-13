# Game asset format (shared by every class)

Every class file in `classes/` (enemy, tower, hero, ...) inherits everything here.
A class may add rules but must not change this frame. Style was derived from the
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
| Sheet layout | **3x2 grid, 6 frames**, row-major, `--size 1536x1024` (512 px per cell) | a 1536 px row is too short for 6 frames; the model makes a grid anyway |
| Single sprite | `--size 1024x1024` | master, icon, projectile |
| Poses | describe **every frame's pose** explicitly | otherwise frames come out identical |
| Directions | `side` = facing and moving right; `up` = back view moving up the screen; `down` = front view moving toward the camera. **Left = mirror of side** (never generated) | |
| Quality | `low` while testing; `medium/high` only after the user approves | cost |

`{BG}` (append to every prompt):
> Background: one flat solid pure magenta color (#FF00FF) everywhere, no gradient, no ground,
> no shadow, no scenery, no text, no border. Do not use magenta or pink anywhere on the subject.

`{GRID}` (append to every sheet prompt, before `{BG}`):
> Layout: a 3x2 grid, 3 columns and 2 rows of 6 equal cells, read left to right, top row first.
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
    raw/walk_side_v01.png (+.json)    every raw the model returned (.json = exact prompt, model, refs, cost)
    raw/walk_side_v02.png
    v02/                              packed from raw v02 (only approved raws get packed)
      enemy_spider_walk_side.png        horizontal sheet @2x
      enemy_spider_walk_side_preview.gif
      frames/@2x/enemy_spider_walk_side_01.png ...
      frames/@1x/enemy_spider_walk_side_01.png ...
```
- **The highest `vNN/` folder of a sheet is its final version.** A packed folder has the number of the raw it came from.
- Raw names: `<sheet>_vNN.png`, made by `gen_image.py --name <sheet> --versioned --out <asset>/<sheet>/raw`.
- Frame names keep kind and id (`enemy_spider_walk_side_03.png`) so they are unique inside a game project.
- To go back to an older version (e.g. v02 after v03): copy `raw/<sheet>_v02.*` to the next free number,
  pack it, and log it in `history.md` ("restore of v02"). `sprite_pack.py` refuses to pack below the final.

Game-ready frames (`sprite_pack.py`):
| Item | Value |
|---|---|
| File type | PNG-32 RGBA, transparent |
| Resolutions | `@2x` master and `@1x` in-game; cell size comes from the class/level |
| Pivot | feet, bottom-center: x 0.5, y 0.88 of the cell (12% above the bottom); icons are centered |
| Scale | one shared scale per asset (body's larger side = 72% of the cell), fixed by the first packed sheet (`walk_side`) |

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
3. Sheets: one `gen_image.py --versioned` call per sheet, all with `--ref <approved master> --png`;
   independent sheets run in parallel.
4. Pack each approved raw with `sprite_pack.py`, `walk_side` first (it fixes the asset's scale).
   The packer must report `split=gaps`; `split=equal` means figures touch: regenerate that sheet.
5. Review each packed sheet; a sheet below 8 gets a new raw version (max 3 per sheet).
   Log every raw in `history.md`.
6. Report: the final version of every sheet (path to its `vNN/` folder), scores, rounds, total cost.
   Remind the user that frames may need hand-alignment: image models are not pixel-precise.

**Edit an existing asset** (e.g. "make the spider's attack bite more powerful")
1. Read the asset's `brief.md`, `history.md` and `meta.json`; reuse the approved master and `{design}` verbatim.
2. Change only the slot(s) the request is about (e.g. `{attack}`/attack poses); keep every other fixed block.
   Record the new slot value in `brief.md`.
3. Generate the next raw version of that sheet only (`--versioned` picks the number), review, iterate
   (max 3), pack the approved one into its `vNN/`, log every raw in `history.md` with
   requested by = the user's words.
4. Report old final vs new final side by side (paths). The previous version stays untouched.
- Changing the master or `{design}` affects every sheet: confirm with the user first, then regenerate all sheets.

## 5. Review checklist (score 1-10, redo below 8)
- Same character as the master in every frame: colors, gear, proportions.
- 6 separate figures (`split=gaps`).
- Direction correct (side faces right; up shows the back; down shows the face).
- Style: thick dark outlines, flat 2-3 tone shading, muted palette, no gradients, glow or fur.
- Poses visibly differ frame to frame and read as the requested action; loops flow back to frame 1.
- No leftover magenta fringe, background, ground, shadow or text; silhouette readable at @1x.
