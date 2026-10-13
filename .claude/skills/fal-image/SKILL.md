---
name: fal-image
description: Generate or iterate on images with OpenAI GPT Image via fal.ai, including 2D game assets (enemy sprites with walk/attack/death animations, towers, icons, VFX, UI, level backgrounds). Use when the user asks to create, draw, render or design an image, sprite or game asset.
---

# Generate images with fal.ai

You are the art director. The image model only draws; you plan, write prompts, review and iterate.

## Pick the route
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
    which image to review.
- **Other game asset** (tower, prop, icon, VFX, UI, map): use `templates.md`, with the style block from `format.md`.
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
checklist in `format.md` (or `templates.md`), and score it 1-10. Below 8: revise the prompt with a
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
