---
name: fal-image
description: Generate still images with OpenAI GPT Image via fal.ai: a game character's approved master (side view) and, for enemies, its front and back views, icons, projectiles, towers, props, UI and level backgrounds. Use when the user asks to create, draw, render or design an image, a character or a game asset. Animation (walk, attack, death ...) is not drawn here: it is made from these stills by the video-sprite skill. With --manual it writes the prompts for the user to run in ChatGPT instead of calling fal, then reviews and files the images the user approves.
---

# Generate stills with fal.ai

You are the art director. The image model only draws; you plan, write prompts, review and iterate.
This skill makes **stills**: the raw source images, one fixed design per character. It never draws a
motion sheet. Animation comes from the `video-sprite` skill, which animates the approved stills.

## Arguments
- `--example [--hero | --ally | --enemy-small | --enemy | --enemy-large | --enemy-flying | --boss]`: only print the matching
  section of `examples.md` (no flag: the overview and one example per class). No API call, no size question,
  nothing written.
- Class flags (`--hero`, `--ally`, `--enemy-small`, `--enemy`, `--enemy-large`, `--enemy-flying`, `--boss`),
  `--tier XS|S|M|L|XL|XXL`, `--role melee|ranged|flying|summoned` and `skill: <name> - <what it does>` (one
  or more) may come with a real request; plain words work too ("hero size L", "quái bay", "đánh xa").
- `--status [<id>]` or "trạng thái tới đâu rồi", "xem manifest của <id>": run `python scripts/asset_status.py
  [<id>]` and show its table (every character, or one character's manifest). No API call, nothing written.
- `--auto`: format.md §5.
- `--manual`: no API call and no fal cost; the user carries the prompts to ChatGPT (or another image tool) and brings the images back ("Manual mode" below). Everything else works as without the flag.
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
   Each concept also names its role and, for a hero or boss, 2-3 skills; a second AskUserQuestion call asks
   "Chọn kỹ năng" (`multiSelect`) from the chosen concept's skills.
   The user may mix (concept A with weapon from B) or type their own with "Other".
4. **Compose** `{design}` (one dense sentence, format.md §1) and the other slots from the choices; write
   `brief.md` with the idea in the user's words, the 3 concepts offered, the choices made, class and tier.
   **Actions**: once the character is approved, each skill (and any action the user has not described) gets 2-3 proposed action
   descriptions written by the `video-sprite` formula (`references/motion-prompts.md` "Writing the action"): beats by body part, facing lock,
   end state, suggested clip length, risks, price; the user picks or edits one before any clip is paid. Use the model-habit table there
   to enrich, never to fix the design to one hero. **Physical motion** (same file, "Physical motion: five phases"): every proposed action is
   written as wind-up (joint angles named, longest beat), load, one explosive release, travel or impact, short hold; a move that goes
   somewhere says how far and which way. Design the `pose_skill_<name>` still to show that intent (a charge: horns forward, body low).
5. Continue in the normal mode (default: master, then stop for approval; with `--auto` too, if given).
   Show the composed `{design}` sentence in the master report so the user sees what was drawn from.

## Manual mode (`--manual`)
Same standards, different hand: you are the art director who writes the requests, the user is the courier who sends them to ChatGPT and
brings images back; no `gen_image.py` call, no fal cost. Used to test ideas for free and to save the stills' cost. Without the flag
nothing in this skill changes. Class, tier, role, skills and the design questions (below) are asked exactly as usual, with these differences:
1. **Nothing is written until something is approved.** No folder, `brief.md` or manifest is created for a candidate; they appear when
   the user says "chốt" for the first image (idea testing costs nothing and leaves nothing behind).
2. **The prompt pack** replaces the generator call. For each still show, in ONE code block the user can copy: (a) a line "Đính kèm: ..."
   naming exactly which image(s) to attach (the approved master `vNN`, or the concept image; none for a first master from words), (b) the
   message, **fully expanded**: the real `{design}`, `{STYLE}`, `{BG}`, `{UPRIGHT}`, `{SIMPLE}` and the view text from `format.md` (§1-§3,
   §10) with `{H}` filled in, no `[ ]` or `{ }` left (an unfilled slot is read by the model as text and it invents the design), ending
   "Output: one image, 1024x1024, one character only". Each message must stand alone (the chat has no memory we rely on): one still per
   message; a new chat per still is safest. Save the same text as `A/design/prompts/<still>_pNN.txt` once the asset exists.
   Patterns already written out: `docs/prompt-style-transfer.md` (from a concept image: A convert only, B optional changes) and
   `docs/prompt-assets-from-master.md` (front, back, icon, projectile, poses, fx part, ability icon). Use them, adapted, instead of inventing a new shape.
3. **From a concept image**: the prompt says what to KEEP (count limbs and features), what to CHANGE, and what must NOT be added (a weapon the
   concept does not have). The two failures seen: all extra arms dropped, and a staff added to empty hands.
4. **Review** what the user sends (a path in the chat, usually `.../images/N.webp`): open it with Read, score it 1-10 with `format.md` §6, and for
   a candidate run `python scripts/ingest_image.py <image> --check` (size, flat magenta border, margins, share of the frame, magenta tint).
   Report scores and warnings in Vietnamese, recommend one, write the next prompt as a one-fix retry. The user's words are the brief: translate
   their feedback into prompt lines yourself.
5. **File only what the user approves**: `python scripts/ingest_image.py <image> --out <asset>/design --name <still> --prompt-file <the pack text> --note "<why chosen>"`
   (PNG 1024x1024, next free `<still>_vNN`, sidecar `.json` with source `manual`, the prompt and cost 0; `costs.csv` is not touched).
   Rejected candidates are never saved. Then `brief.md` (approved stills, "why chosen"), `history.md` (model column: `chatgpt (manual)`, cost 0) and the manifest row as usual.
6. Never ask the user to attach anything from `ref/` (look-only style anchors), and no confidential material.
7. After this the asset is an ordinary asset: the same names, folders and numbering, so `video-sprite` and every tool work unchanged. A still may be
   made through the API later for the same character (the numbering continues); `--auto` does not apply (a human carries every prompt).

## Ask for class, size, role and skills (every character, before anything else; `--creative` asks them with its design questions)
A character needs a **class** (one file in `classes/`: hero, ally, enemy, enemy-flying, boss), a **size
tier**, a **role** and, for heroes and bosses, its **skills** (each from the class file: §3 Size, §2 Roles,
§7 Skills) before `brief.md` or any paid call, in `--auto` mode too. Take them from the
flags or the words of the request; never guess a missing one. Ask only what is missing.
1. Class missing: AskUserQuestion "Nhân vật thuộc class nào?" with the options Hero, Quân phe ta (ally),
   Quái (enemy), Boss; the one the description suggests first, marked "(Recommended)".
2. Tier missing: AskUserQuestion "Chọn size cho <class>" with the tiers of the class file's §3 only. Each option: tier, `{H}` and canvas, with a typical example
   ("L: 84 px, canvas 220x196 — robot, golem"). The tier that fits the description first, "(Recommended)".
   Both missing: ask the class first, then the tier, in two calls (the tier options depend on the class).
   "Quái" covers `enemy.md` (walking) and `enemy-flying.md`: a flying enemy ("quái bay", `--enemy-flying`) is
   offered the flying tiers (S, M); if the description does not say whether it flies, ask it as its role
   in the same call (walking roles, plus "bay") and re-ask the tier with S and M if "bay" is picked.
   Role and skills go in the SAME call as the tier (up to 4 questions):
   - Role missing: "Vai trò?" with the class file's §2 roles, the one the description suggests first.
   - Skills missing (hero; boss: specials): "Chọn kỹ năng" with `multiSelect: true`, 3-4 skills you propose
     from the description, each "<name>: <the body's move>; <the effect, marked vfx when big>". Hero: pick 2-3.
     Allies and enemies get no skill question (none by default; the user may add them).
   **Design details** the description leaves out (size of a held weapon against the body, hands, where it rests when idle, stance width, cape or
   hair): detect them from the description and ask them in the same call or a following one, as the class file's "Design details" table says
   (hero §7b). Never fill them with a guess; a wrong weapon size is the most expensive master loop seen.
3. Record class, tier, `{H}`, canvas, role and skills in `brief.md`; `{H}` goes into `{STYLE}`.
4. Write the **Asset manifest** (table format `format.md` §8; rows from the class file's §6) from role and skills, with the cost estimate, and show
   it to the user with the master report (they may add or drop rows).

## Pick the route
- **Character**: read its class file (`classes/<class>.md`: role in the game, roles, size, directions,
  stills, manifest rows, skills, slots, review points) and `format.md` (shared rules: style, view prompts by
  `{body}`, files, manifest format, checklist), and follow them exactly. The class file is the only place
  for class-specific facts; `reference.md` holds the measurements behind them. The user gives content
  ("đạo tặc đầu trọc, dùng đao"); the class file says what to make of it.
  1. `brief.md` with class, tier, role, skills, the filled slots and the **Asset manifest**, then the **master** (side view, format.md §3) into `<asset>/design/`. Mode (`format.md` §5): no `--auto`
     → stop after the master and ask the user to approve a version; `--auto` → approve it yourself (>= 8).
  2. Every `fal-image` row of the manifest, from the approved master (`--ref`): front and back (enemies,
     bosses), icon, projectile (ranged), `pose_skill_<name>` (one per skill, the skill's peak), then the
     `fx_<name>` vfx stills (`templates.md` vfx). Show them; get approval; mark each row ✅ or ⏳.
     Heroes and allies have no other view.
  3. **Animation request** or "làm tiếp phần chuyển động": hand over to the `video-sprite` skill, which makes
     the manifest's `video-sprite` rows marked ❌. Missing stills are made here first.
  - Keep `brief.md` (manifest status), and `history.md` (one row per still) up to date.
  - Extensions (a second attack, a two-phase death, a transformation, walk and fly ...): `format.md` §9; add
    their rows to the manifest first.
  - Restyle ("restyle bandit sang ..."), edit ("đổi vũ khí", "góc sau bị lộ mặt"): `format.md` §5.
- **Character animation** asked directly ("tạo attack cho bandit"): use the `video-sprite` skill; it uses
  this skill only for a missing still.
- **Other game asset** (tower, prop, ability icon, VFX key frame, UI, map): `templates.md`, with `{STYLE}` and
  `{BG}` from `format.md`, into `out/<kind>s/<id>/design/` (`format.md` §4). They are stills too.
- **Anything else**: write a concrete prompt (subject, composition, camera, lighting, style, palette).

## Running the generator (project root; not used in `--manual`)
`python scripts/gen_image.py "<prompt>" --size <size> [--ref <image>] [--png] --name <name> [--versioned] [--out <dir>]`
- Defaults: `--model gpt-image-2 --quality low` (cheap drafts). Class stills: `--size 1024x1024 --png` on a
  flat magenta background (no `--transparent`; the tools key it out), `--versioned --out <asset>/design`.
  Every other asset uses the magenta background too, except opaque maps.
- `--ref` sends a local image as visual reference (edit endpoint): every view uses `--ref <approved master>`.
- Only use `--quality medium` or `high` after the user asks.
- Long prompt: write it to a file and pass `--prompt-file <file>` (a shell-quoted `$(cat file)` once sent the literal text and wasted two images). After the first image of a command, open its `.json` sidecar and check the first 60 characters of `prompt`; the script also prints them on stderr.
- Style bans (`format.md` §1) are defaults: when the user asks for something they forbid, allow it for that asset and note it in `brief.md`.
- stdout lists saved image paths; stderr has a `cost:` line. Independent stills can run in parallel.
- Put any in-image text in double quotes and say it must render exactly as written.

## Review loop
Open each image with the Read tool, check it against the goal and the checklist in `format.md` §6 (or
`templates.md`), and score it 1-10. Below 8: revise the prompt with a specific fix (name the angle in
capitals, say what must not be visible) and regenerate that image only. Max 3 rounds per image. Report:
output paths, scores, what changed each round, and the cost from the `cost:` lines.

## Costs
- Each run logs to `out/costs.csv` (manual stills cost nothing and are not logged). Spend summary: `python scripts/cost_report.py` (add `--today`).
  Mention the session total when you finish a task.
- `~` means the cost is approximate (no exact fal price, or reference images were sent).

## Rules
- Never print, echo, read or write FAL_KEY. It lives only in `.env`.
- Do not send confidential company data or real people's photos to the API.
- Never send files from `ref/` to the API and never name a commercial game or studio in a prompt;
  describe the style instead.
- If a script exits with an error, read the message, fix the arguments, and retry once before reporting.
