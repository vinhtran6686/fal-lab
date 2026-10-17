---
name: fal-image
description: Generate still images with OpenAI GPT Image via fal.ai: a game character's approved master and its standard views (side, front, back, three-quarter front and back), icons, projectiles, towers, props, UI and level backgrounds. Use when the user asks to create, draw, render or design an image, a character or a game asset. Animation (walk, attack, death ...) is not drawn here: it is made from these stills by the video-sprite skill.
---

# Generate stills with fal.ai

You are the art director. The image model only draws; you plan, write prompts, review and iterate.
This skill makes **stills**: the raw source images, one fixed design per character. It never draws a
motion sheet. Animation comes from the `video-sprite` skill, which animates the approved stills.

## Pick the route
- **Character of a defined class** (`classes/enemy.md`, `classes/hero.md`): read `format.md` and the class
  file next to this file and follow them exactly. The user gives content ("đạo tặc đầu trọc, dùng đao"); the
  class file sets the slots, sheets and frame size; `format.md` sets the style, the view prompts (by `{body}`:
  biped, quadruped, blob, flyer), files and checklist. If the level or archetype is not given, use Level 1
  and the archetype that fits. A character of a class with no file yet (friendly unit, boss ...): ask the
  user, then use the closest class file and note it in `brief.md`.
  1. `brief.md` with the filled slots, then the **master** (3/4 front) into `<asset>/design/`. Mode (`format.md` §5): no `--auto`
     → stop after the master and ask the user to approve a version; `--auto` → approve it yourself (>= 8).
  2. The **standard views** and stills the class needs, from the approved master (`format.md` §3): side,
     front, back, 3/4 back, icon (+ projectile; optional `pose_<action>`, `turnaround`). Show them; get approval.
  3. **Animation request** (move, attack, death, hurt, idle ...) or "làm tiếp phần chuyển động": hand over
     to the `video-sprite` skill with the approved stills. Missing views are made here first.
  - Keep `brief.md` and `history.md` of the asset up to date (one history row per still).
  - Restyle ("restyle bandit sang ..."), edit ("đổi vũ khí", "góc sau bị lộ mặt"): `format.md` §5.
- **Character animation** asked directly ("tạo attack cho bandit"): use the `video-sprite` skill; it uses
  this skill only for a missing still.
- **Other game asset** (tower, prop, ability icon, VFX key frame, UI, map): `templates.md`, with `{STYLE}` and
  `{BG}` from `format.md`, into `out/<kind>s/<id>/design/` (`format.md` §4). They are stills too.
- **Anything else**: write a concrete prompt (subject, composition, camera, lighting, style, palette).

## Running the generator (project root)
`python scripts/gen_image.py "<prompt>" --size <size> [--ref <image>] [--png] --name <name> [--versioned] [--out <dir>]`
- Defaults: `--model gpt-image-2 --quality low` (cheap drafts). Class stills: `--size 1024x1024 --png` on a
  flat magenta background (no `--transparent`; the tools key it out), `--versioned --out <asset>/design`.
  Every other asset uses the magenta background too, except opaque maps.
- `--ref` sends a local image as visual reference (edit endpoint): every view uses `--ref <approved master>`.
- Only use `--quality medium` or `high` after the user asks.
- stdout lists saved image paths; stderr has a `cost:` line. Independent stills can run in parallel.
- Put any in-image text in double quotes and say it must render exactly as written.

## Review loop
Open each image with the Read tool, check it against the goal and the checklist in `format.md` §6 (or
`templates.md`), and score it 1-10. Below 8: revise the prompt with a specific fix (name the angle in
capitals, say what must not be visible) and regenerate that image only. Max 3 rounds per image. Report:
output paths, scores, what changed each round, and the cost from the `cost:` lines.

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
