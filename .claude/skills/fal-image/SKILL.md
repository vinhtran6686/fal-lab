---
name: fal-image
description: Generate or iterate on images with OpenAI GPT Image via fal.ai, including 2D game assets (enemy sprites with walk/attack/death animations, towers, icons, VFX, UI, level backgrounds). Use when the user asks to create, draw, render or design an image, sprite or game asset.
---

# Generate images with fal.ai

You are the art director. The image model only draws; you plan, write prompts, review and iterate.

## Pick the route
- **Any animation request** (walk, run, attack, death, idle, tower attack, VFX ...), however short
  ("Create a walk animation for this bandit", "idle animation for this magical tower"): read
  `animation.md` first. Design the motion before drawing: motion card, phases from the object's
  profile, frame-by-frame blueprint in `A/<sheet>/blueprint.md`, key poses first, then the full sheet,
  then the review loop. Never treat a list of alternating poses as the spec. Ask only when a missing
  fact changes the result (e.g. does the tower turn to aim?); otherwise use documented defaults.
- **Game asset of a defined class** (currently: `enemy`): read `format.md` and `classes/<class>.md`
  next to this file and follow them exactly. The user only gives content ("monster spider, melee");
  the class file fixes states, frames, sizes, files and prompt wording.
  If the level or archetype is not given, use Level 1 and the archetype that fits.
  - **Mode** (`format.md` §4): request contains `--auto` → full run without stopping.
    No `--auto` → generate the master only, **stop and ask the user to approve a master version**,
    then make all sheets.
  - **Edit** of an existing asset ("sửa attack của spider…", "dùng lại walk_down v02"): follow
    "Edit an existing asset" in `format.md` §4: new version of that sheet only; old versions stay.
  - Always keep `brief.md` and `history.md` of the asset up to date (one history row per raw).
  - When reporting, name the final version of each sheet (highest `vNN/` folder) so the user knows
    which image to review, and refresh the playtest (`format.md` §4 step 6) so they can watch it move.
  - Leg feedback ("frame 6 bước cùng 1 chân"): turn the user's per-frame reading into
    `leg_check.py --observed ... --expected <blueprint pattern> [--bad ...]`, re-pack with the printed
    `--order` as a new version (no API call). Regenerate only if no frame shows the needed foot.
  - Movement feedback ("bước nhiều mà đi ít", feet sliding): change `move_speed` (re-pack `walk_side`
    with `--move-speed`), not the art. Limping or choppy walks: check the blueprint, then regenerate
    from stage 1 (key poses). A sheet drawn smaller/bigger: re-pack it (the packer matches body size).
- **Other game asset** (tower, prop, icon, VFX, UI, map): use `templates.md`, with the style block from `format.md`;
  if it moves (tower attack/idle, VFX), design it with `animation.md` and its object profile (§3): a tower,
  projectile or effect never inherits a walk cycle.
- **Anything else**: write a concrete prompt (subject, composition, camera, lighting, style, palette).

## Running the generator (project root)
`python scripts/gen_image.py "<prompt>" --size <size> [--transparent] [--ref <image>] --name <name> [--out <dir>]`
- Defaults: `--model gpt-image-2 --quality low` (cheap drafts).
- Class assets do NOT use `--transparent`: they use gpt-image-2 on a flat magenta background with
  `--png`, and `sprite_pack.py` removes it (see `format.md` §2). `--transparent` (other assets only)
  switches to `gpt-image-1.5` automatically, which is weaker at style and multi-frame sheets.
- `--ref` sends a local image as visual reference (edit endpoint); use the approved master for every sheet.
- Only use `--quality medium` or `high` after the user approves a draft.
- stdout lists saved image paths; stderr has a `cost:` line.
- Put any in-image text in double quotes and say it must render exactly as written.

## Review loop
Open each image (and each packed sheet) with the Read tool, check it against the goal and the
checklist in `format.md` (or `templates.md`), and score it 1-10. Animated sheets also go through the
review loop in `animation.md` §8 (`scripts/motion_check.py`, onion transitions, leg check) and get a
Pass / Needs Revision / Fail verdict with the defective transitions named; anything only visible in
motion is reported as unverified until seen in Motion Lab. Below 8: revise the prompt with a
specific fix and regenerate that image only. Max 3 rounds per image. Report: output paths, scores,
what changed each round, and total cost from the `cost:` lines.

## Costs
- Each run logs to `out/costs.csv`. Spend summary: `python scripts/cost_report.py` (add `--today`).
  Mention the session total when you finish a task.
- `~` means the cost is approximate (no exact fal price, or reference images were sent).

## Rules
- Never print, echo, read or write FAL_KEY. It lives only in `.env`.
- Do not send confidential company data or real people's photos to the API.
- Never send files from `ref/` to the API and never name a commercial game or studio in a prompt;
  describe the style instead.
- If a script exits with an error, read the message, fix the arguments, and retry once before reporting.
