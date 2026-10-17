---
name: fal-image
description: Generate still images with OpenAI GPT Image via fal.ai: a game character's approved master and its standard views (side, front, back, three-quarter front and back), icons, projectiles, towers, props, UI and level backgrounds. Use when the user asks to create, draw, render or design an image, a character or a game asset. Animation (walk, attack, death ...) is not drawn here: it is made from these stills by the video-sprite skill.
---

# Generate stills with fal.ai

You are the art director. The image model only draws; you plan, write prompts, review and iterate.
This skill makes **stills**: the raw source images, one fixed design per character. It never draws a
motion sheet. Animation comes from the `video-sprite` skill, which animates the approved stills.

## Arguments
- `--example [--hero | --ally | --enemy-small | --enemy | --enemy-large | --boss]`: only print the matching
  section of `examples.md` (no flag: the overview and one example per class). No API call, no size question,
  nothing written.
- Class flags (`--hero`, `--ally`, `--enemy-small`, `--enemy`, `--enemy-large`, `--boss`) and `--tier
  XS|S|M|L|XL|XXL` may also come with a real request; plain words work too ("hero size L", "boss cỡ XXL").
- `--auto`: format.md §5.
- `--creative`: design-suggestion mode (next section). The user gives only the idea; you propose, they pick.

## Creative mode (`--creative`)
The user gives a short idea ("hero nữ có biệt tài sử dụng gió --creative"). You are the concept artist: you
turn it into a few designs and the user only chooses. No API call until the choices are made.
1. **Class**: from the idea or a class flag; missing → ask it first (as below, one call).
2. **Propose** in chat, in Vietnamese, **3 concepts** that differ in silhouette and role, not only in colour.
   Each concept, 3-4 short lines: name and body (`{body}`, build, what is exaggerated for its role), weapon
   or focus and the hand that holds it, palette (one main colour family + one accent, by side: format.md §1),
   one signature feature, the attack in one phrase, and the tier it fits.
   Restraint (the style forbids the rest): one signature feature per concept, effects only as one or two flat
   layered shapes touching the body or the weapon, no ornate trim, no glow, no aura, no extra accessories.
3. **Ask** in ONE AskUserQuestion call, up to 4 questions, every option labelled with its concept letter:
   - "Hình dáng / vai trò" (header `Concept`): the 3 concepts (A, B, C), the best fit first "(Recommended)".
   - "Vũ khí / tâm điểm" (header `Weapon`): 3 options mixing the concepts' weapons.
   - "Bảng màu" (header `Palette`): 3 palettes (main + accent), all within format.md §1.
   - "Size" (header `Size`): the class's tiers with `{H}`, canvas and an example (as below), the tier the
     concept fits first "(Recommended)".
   The user may mix (concept A with weapon from B) or type their own with "Other".
4. **Compose** `{design}` (one dense sentence, format.md §1) and the other slots from the choices; write
   `brief.md` with the idea in the user's words, the 3 concepts offered, the choices made, class and tier.
5. Continue in the normal mode (default: master, then stop for approval; with `--auto` too, if given).
   Show the composed `{design}` sentence in the master report so the user sees what was drawn from.

## Ask for class and size (every character, before anything else; `--creative` asks the size together with its design questions)
A character needs a **class** and a **size tier** from the matrix (`format.md` §7) before `brief.md` or any
paid call, in `--auto` mode too. Take them from the flags or the words of the request; never guess a missing one.
1. Class missing: AskUserQuestion "Nhân vật thuộc class nào?" with the options Hero, Quân phe ta (ally),
   Quái (enemy), Boss; the one the description suggests first, marked "(Recommended)".
2. Tier missing: AskUserQuestion "Chọn size cho <class>" with that class's tiers only (hero: S, M, L; ally:
   S, M, L; enemy: XS, S, M, L; boss: XL, XXL). Each option: tier, `{H}` and canvas, with a typical example
   ("L: 84 px, canvas 220x196 — robot, golem"). The tier that fits the description first, "(Recommended)".
   Both missing: ask the class first, then the tier, in two calls (the tier options depend on the class).
3. Record class, tier, `{H}` and canvas in `brief.md`; `{H}` goes into `{STYLE}`.

## Pick the route
- **Character** (hero, ally, enemy, boss; `format.md` §7 says which class file holds its slots and sheets:
  `classes/hero.md` or `classes/enemy.md`): read `format.md` and the class file next to this file and follow
  them exactly. The user gives content ("đạo tặc đầu trọc, dùng đao"); the class file sets the slots and
  sheets, the matrix the frame size; `format.md` sets the style, the view prompts (by `{body}`: biped,
  quadruped, blob, flyer), files and checklist. If the level or archetype is not given, use Level 1 and the
  archetype that fits.
  1. `brief.md` with class, tier and the filled slots, then the **master** (3/4 front) into `<asset>/design/`. Mode (`format.md` §5): no `--auto`
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
