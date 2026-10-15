---
name: video-sprite
description: Animate a game character's approved stills into consistent sprite animations (move/walk in 5 views, attack, death, hurt, idle, run) with image-to-video on fal.ai, then key, register, loop or retime, finish and export them into out/enemies/<id>/<category>/<sheet>/vNN with one fixed canvas and body size for every action. Use for any character or enemy animation; the stills come from the fal-image skill.
---

# Video sprites (image-to-video on fal.ai)

Port of `video2dsprite` from agent-sprite-forge 0.4.0 (MIT, see `LICENSE`, `VENDORED.md`), adapted to this
project: clips come from `scripts/fal_video.py` (fal.ai, `FAL_KEY` in `.env`), frames are exported into the
asset folder by `scripts/video_to_sheet.py`, and a top-down tower-defense game needs 5 views.

**Division of work.** The `fal-image` skill makes the stills: one approved master per character and its
standard views (`fal-image/format.md` §3), all in `A/stills/`. This skill animates them: one image-to-video
clip per action and view, then deterministic tools cut the frames. A video model moves ONE character
continuously from ONE still, so identity and motion stay consistent (an image model drawing a sheet repeated
poses, swapped legs and froze the upper body). A missing still: ask fal-image for it first.

`A = out/enemies/<id>`. Run every tool from the project root (Python 3.10+, numpy, scipy, Pillow, ffmpeg 5.1+
on PATH; in Git Bash use the real Python, see `CLAUDE.md`).

## Tools
| Step | Command |
|---|---|
| Still -> master.json | `python scripts/make_master.py A/stills/<still>.png --out-dir A/.work/masters/<view> --name <id> --facing <facing> --recap "<{design}>"` |
| Plan a set | `python .claude/skills/video-sprite/scripts/sprite_set.py plan --master A/.work/masters/<view>/master.json --views <side\|front\|back> --output-dir A/.work/<set> --actions <list> --duration 5 --resolution 480p --fps 12 --target-height 138 --formats png --max-takes 1` |
| Cost before paying | clips x takes x price (`python scripts/fal_video.py models`), or `fal_video.py video ... --dry-run` |
| Generate + process | `python .claude/skills/video-sprite/scripts/sprite_set.py run --plan A/.work/<set>/set_plan.json` |
| Review | `sprite_set.py review --plan ...`, then **Read** every `review/<action>/tNN-sheet.png` |
| Accept / retake | `sprite_set.py accept --plan ... --action walk --take 1 [--window 0:124]` / `retake ... --action attack --fix weapon-shape` |
| Export | `python scripts/video_to_sheet.py --set A/.work/<set> --action <action> --asset A --id <id> --sheet <sheet> [--flip-to <dir>] [--despill]` |
| Checks | `python scripts/motion_check.py A/<category>/<sheet>/vNN`, `python scripts/leg_check.py ...` (walks), Motion Lab |
| Prune (after export; always) | `python scripts/video_prune.py prune --set A/.work/<set>` |
| Rebuild a pruned action | `python scripts/video_prune.py rebuild --set A/.work/<set> --action <action>` (from the clip, no API call) |
`sprite_set.py` resumes where it stopped and never generates a clip twice; every verb prints one JSON line.
A paid clip that timed out is recovered with `python scripts/fal_video.py fetch --job <job.json>` (no new charge).
On Windows a stage can fail with `[WinError 5] Access is denied` while a scanner holds a new folder: run
the same command again (run sets one after another, not in parallel, when it happens).

## One canvas and one body size for every action (fixed)
The engine draws every action of a character in the same frame with the same pivot, so no action may be
bigger or smaller than another:
- **Canvas**: `meta.json` "cell", set by the first export and shared by every later one (Level 1 enemy:
  **256x128 at 1x**, `fal-image/classes/enemy.md`). `video_to_sheet.py` never widens it for one action and
  never shrinks a body to fit; a state that does not fit is refused: delete `meta.json` and re-export every
  sheet with a larger `--cell` (all actions move to the new canvas together).
- **Body**: every set is finished at `--target-height 138` (Level 1 body height at @2x); the first export
  records the measured body height (`body_height_2x`) and later exports are rescaled when they differ by
  more than 4% (bandit: the attack clip drew him 5% smaller, rescaled x1.048).
- **Pivot**: feet at x 0.5, y 0.88; one fixed transform per clip, so bob, lean, a fall or a spin are kept.

## Views and sets (top-down game, 8 directions from 5 views)
One set per view (or per view and action group); left, down-left and up-left are mirrors (`--flip-to`).
| Set (`A/.work/`) | Still | `--facing` | `--views` | Actions -> sheets (category/sheet, `--flip-to`) |
|---|---|---|---|---|
| `side` | `view_side` | `right` | `side` | walk -> `move/walk_side` left |
| `side_attack`, `side_death` | `view_side` (or `pose_ready_side`) | `right` | `side` | attack -> `attack/attack_side` left; death -> `death/death_side` left |
| `down_side` | `master` | `down-right` | `side` | walk -> `move/walk_down_side` down_left |
| `up_side` | `view_up_side` | `up-right` | `side` | walk -> `move/walk_up_side` up_left |
| `down` | `view_front` | `front` | `front` | front-walk -> `move/walk_down` |
| `up` | `view_back` | `back` | `back` | back-walk -> `move/walk_up` |
Front and back MUST be planned with `--views front` / `--views back` (their action ids become
`front-walk` / `back-walk`): that turns off the turn-around gate, which cannot work on a symmetric view.
The category folder comes from the sheet name (`scripts/asset_layout.py`: walk/run -> move, attack/cast ->
attack, death, hurt, idle, icon -> ui).

## Workflow
1. **Stills.** The approved master and the views the actions need, from `fal-image` (`A/stills/`).
2. **Masters.** `make_master.py` per view, with `--recap` = the `{design}` slot of `brief.md` verbatim (the
   long recap is repeated in every motion prompt; short recaps let the model redesign the character).
3. **Plan** each set. Read every action's `prompt` in `set_plan.json` and edit `motion` there for this
   character: the attack from `{attack}`, the death from `{death}` of `brief.md` (keep "then lies completely
   still"). One action per clip; no effects in character clips (the game adds FX).
4. **Ask before paying.** Show the user the clip count and the estimate (default `h3-max-turbo` 480P 5 s
   = ~USD 0.08 per clip; a melee enemy of 7 clips ~USD 0.55 + retakes) and wait for a yes, unless they
   already approved this run. `FAL_VIDEO_MAX_USD` (default 0.60) caps every clip; `FAL_VIDEO_MODEL` picks
   another model (`kling-3-std` keeps a weapon's pose best but costs ~USD 0.70 a clip).
5. **Run**, then **review**: Read every take's sheet. The gates measure size, feet, zoom, turning, edges,
   background, extra objects, motion, colour and timing; they cannot see identity, a changed weapon, the
   wrong leg order or a covered face. Never accept an action you have not looked at. Classify each take:
   **Pass** (8-10, coherent motion, same character), **Needs Revision** (5-7, name the frames, e.g.
   `F5-F10 pink smear`), **Fail** (1-4). Fix: `accept --window` (a gate that misreads a correct motion),
   `retake --fix <clause id or sentence>` (clause ids in `references/motion-prompts.md`), or plan options.
6. **Export** each accepted action with `video_to_sheet.py` (one canvas, one body size, see above). Each
   export is a new `vNN`; the clip moves to `A/<category>/<sheet>/clip_tNN.mp4`. Log one row per take in
   `history.md` (`model` column = the fal model).
7. **Check**: `motion_check.py` on every sheet, `leg_check.py` on walks; anything only visible in motion is
   unverified until seen in Motion Lab (`python scripts/build_playtest.py`, republish, see `CLAUDE.md`).
8. **Prune** every set once its actions are exported (always; no need to ask).
Report: the final `vNN` of every sheet, the model and takes, the cost (`python scripts/cost_report.py --today`).

## Per-action options in `set_plan.json` (ours, see `VENDORED.md`)
- `"spins": true`: the body turns on purpose (a whirlwind spin attack); the prompt locks the facing only at
  the start and end. Also set `gates.turn.enabled` to false. Example: bandit `attack_side`.
- `"gaitStride": "period"`: a walk whose `loop-report.json` says `ambiguous` and whose leg check shows both
  steps inside T: loop T instead of 2T (half the frames). `"double"` forces 2T. Then `rebuild` and export.
- `timing` of one-shots: `{"mode": "auto", "durationMs": 700, "keys": {"hit": {"at": 0.4, "holdMs": 80}}}`.
Lessons from bandit (2026-10-14): on 3/4, front and back walks the `feet` gate flags the lifted foot of each
step (5-7% vs 5%): check the sheet and `accept --window 0:<frames>`; a spin fails `area` (the held-out blade);
fast blades get a pink motion smear (the backdrop blended in): export with `--despill` (turns it steel grey)
or retake with the `no-blur` clause. An accepted take whose engine package is refused for key spill still
exports from its finished frames.

## Timing defaults
| Action | Kind | Canvas of the clip | Cut |
|---|---|---|---|
| walk, run | loop | square | `gait_loop` picks the cleanest cycle by measurement (never ping-pong) |
| idle | loop, end frame pinned | square | idle loop |
| attack | one-shot, end frame pinned | 16:9 | retimed to 0.7 s, hit at 40% (exported as `hit_frame`) |
| death | one-shot, holds the last frame | 16:9 | retimed to 0.9 s, lying still at 80% |
| hurt | one-shot | square | 0.5 s |
Video models play one-shots in slow motion; the retime cuts frozen holds and compresses to game length.
(The clip canvas only frames the video; every export lands on the asset's one canvas.)

## Where things are, and disk
A person opens `A/<category>/<sheet>/`: `clip_tNN.mp4` (+ `.json`: model, prompt, cost) is the source,
`vNN/preview.gif` the result, `vNN/frames/` the game frames, `vNN/check/` the checks and the take's review
sheet. `A/.work/` is for tools only. One take produces ~550 files / ~70 MB of intermediate frames;
`video_prune.py prune` keeps per set only what decides the frames (the master, the input image and transform
sent to the model, prompts, QC and every stage's JSON in `takes/tNN/record/`): ~1.4 MB per set; the review
folder goes once every action of the set is exported (the chosen take's sheet is in `vNN/check/`). Wrong
frames after a conversion: fix the tool or the plan, `rebuild` (byte-identical, tested), export again; the
clip is never bought twice. `--drop-rejected-clips` also deletes clips of takes never chosen.

## Known limits (report them honestly)
- h3-max-turbo (default) lowers a weapon held upright into a horizontal swing on side and 3/4 front walks.
- Colours can shimmer on fast limbs; slow motion and an occasional turned head are common: expect 1-3
  takes per action. Walks are treadmill walks in place; the game moves the sprite.
- `gait_loop` can call a front/back/3/4 walk `ambiguous` and loop two strides (24 frames instead of 12):
  correct to watch, twice the frames; `gaitStride: period` halves it.

## References (upstream, kept for detail)
`references/sprite-set.md` (plan/run/gates), `references/motion-prompts.md` (templates, fix clauses; the
`death` template is ours), `references/matte.md`, `references/finishing.md`, `references/animation-review.md`.
Where they mention `route_media.py`, Grok or xAI, read `scripts/fal_video.py`: it takes the same arguments.
