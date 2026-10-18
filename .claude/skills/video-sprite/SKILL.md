---
name: video-sprite
description: Animate a game character's approved stills into consistent sprite animations (walk in 3 views for enemies, run/attack/death/skills from the side view for heroes) with image-to-video on fal.ai, then key, register, loop or retime, finish and export them into out/<class>/<id>/<category>/<sheet>/ (one final version; every source clip kept in raw/) with one fixed canvas and body size for every action. Use for any character or enemy animation; the stills come from the fal-image skill.
---

# Video sprites (image-to-video on fal.ai)

Port of `video2dsprite` from agent-sprite-forge 0.4.0 (MIT, see `LICENSE`, `VENDORED.md`), adapted to this
project: clips come from `scripts/fal_video.py` (fal.ai, `FAL_KEY` in `.env`), frames are exported into the
asset folder by `scripts/video_to_sheet.py`, and a top-down tower-defense game needs 1 view for heroes and allies, 3 for enemies and bosses (fal-image/format.md §3).

**Division of work.** The `fal-image` skill makes the stills: one approved master per character (the side
view) and, for enemies and bosses, front and back, plus a pose per skill, all in `A/design/`. Every
character's `A/brief.md` holds the **Asset manifest** (`fal-image/format.md` §8): the list of every still,
clip and effect it needs, from its class, role and skills. **This skill makes the manifest's `video-sprite`
rows marked ❌, and nothing else**: never invent a direction or a state the manifest does not list (no
diagonals, no hurt, no idle loop unless listed), and mark each row ✅ `tNN` in the same commit as its export. This skill animates them: one image-to-video
clip per action and view, then deterministic tools cut the frames. A video model moves ONE character
continuously from ONE still, so identity and motion stay consistent (an image model drawing a sheet repeated
poses, swapped legs and froze the upper body). A missing still: ask fal-image for it first.

`A = out/<class>/<id>` (enemies, bosses, heroes, allies). Run every tool from the project root (Python 3.10+, numpy, scipy, Pillow, ffmpeg 5.1+
on PATH; in Git Bash use the real Python, see `CLAUDE.md`).

## Tools
| Step | Command |
|---|---|
| Still -> master.json | `python scripts/make_master.py A/design/<still>.png --out-dir A/.work/masters/<view> --name <id> --facing <facing> --recap "<{design}>"` |
| Plan a set | `python .claude/skills/video-sprite/scripts/sprite_set.py plan --master A/.work/masters/<view>/master.json --views <side\|front\|back> --output-dir A/.work/<set> --actions <list> --duration 5 --resolution 480p --fps 12 --target-height <2x{H}> --formats png --max-takes 1` |
| Cost before paying | clips x takes x price (`python scripts/fal_video.py models`), or `fal_video.py video ... --dry-run` |
| Generate + process | `python .claude/skills/video-sprite/scripts/sprite_set.py run --plan A/.work/<set>/set_plan.json` |
| Review | `sprite_set.py review --plan ...`, then **Read** every `review/<action>/tNN-sheet.png` |
| Accept / retake | `sprite_set.py accept --plan ... --action walk --take 1 [--window 0:124]` / `retake ... --action attack --fix weapon-shape` |
| Export | `python scripts/video_to_sheet.py --set A/.work/<set> --action <action> --asset A --id <id> --sheet <sheet> [--flip-to <dir>] [--despill]` |
| Checks | `python scripts/motion_check.py A/<category>/<sheet>`, `python scripts/leg_check.py ...` (walks), Motion Lab |
| Prune (after export; always) | `python scripts/video_prune.py prune --set A/.work/<set>` |
| Rebuild a pruned action | `python scripts/video_prune.py rebuild --set A/.work/<set> --action <action>` (from the clip, no API call) |
`sprite_set.py` resumes where it stopped and never generates a clip twice; every verb prints one JSON line.
A paid clip that timed out is recovered with `python scripts/fal_video.py fetch --job <job.json>` (no new charge).
On Windows a stage can fail with `[WinError 5] Access is denied` while a scanner holds a new folder: run
the same command again (run sets one after another, not in parallel, when it happens).

## One canvas and one body size for every action (fixed)
The engine draws every action of a character in the same frame with the same pivot, so no action may be
bigger or smaller than another:
- **Canvas**: `meta.json` "cell", set by the first export and shared by every later one. Read class and tier
  from the asset's `brief.md` and pass that canvas from the size matrix (`fal-image/format.md` §7) as
  `--cell <W>x<H>` on the first export (e.g. hero M: `--cell 156x140`; enemy S: `--cell 92x80`). `video_to_sheet.py` never widens it for one action and
  never shrinks a body to fit; a state that does not fit is refused: delete `meta.json` and re-export every
  sheet with a larger `--cell` (all actions move to the new canvas together).
- **Body**: every set is finished at `--target-height <2 x {H}>` (the tier's body height at @2x, format.md §7:
  XS 48, S 80, M 120, L 168, XL 240, XXL 340); the first export
  records the measured body height (`body_height_2x`) and later exports are rescaled when they differ by
  more than 4% by silhouette area (a height-based check misread weapons and was replaced, 2026-10-16).
- **Pivot**: feet at x 0.5, y 0.88; one fixed transform per clip, so bob, lean, a fall or a spin are kept.

## Manifest rows -> sets and exports (fal-image/format.md §8; hero/ally 1 direction, enemy/boss 3)
Left is always the mirror of the side (`--flip-to left`); there are no diagonal sheets. The side still is the
`master` (a three-quarter view facing right). `make_master.py --class`: `flying` for flying enemies (hover
idle, no feet gate), `boss`, `hero` or `mob` otherwise.
| Manifest row | Set (`A/.work/`) | Master (`make_master.py`) | Plan `--actions` / `--views` | Export (`video_to_sheet.py --sheet ...`) |
|---|---|---|---|---|
| `master (= idle)` | `side` | `master`, `--facing right` | (no clip of its own) | `--action <any side action> --sheet idle_side --rest-frame`: frame 0 of a side take = the master pose, 1 frame |
| `walk_side` (enemy, boss) | `side` | `master`, `right` | `walk` / `side` | `--action walk --sheet walk_side --flip-to left` |
| `run_side` (hero, ally) | `side` | `master`, `right` | `run` / `side` | `--action run --sheet run_side --flip-to left` |
| `walk_down` | `down` | `view_front`, `--facing front` | `walk` / `front` (id `front-walk`) | `--action front-walk --sheet walk_down` |
| `walk_up` | `up` | `view_back`, `--facing back` | `walk` / `back` (id `back-walk`) | `--action back-walk --sheet walk_up` |
| `fly_side`, `fly_down`, `fly_up` (flying) | `side`, `down`, `up` | as walk, `--class flying` | `fly` / `side`, `front`, `back` (ids `fly`, `front-fly`, `back-fly`) | `--action fly --sheet fly_side --flip-to left` / `--action front-fly --sheet fly_down` / `--action back-fly --sheet fly_up` |
| `idle_fly` (flying) | `side` | `master`, `--class flying` | `idle` (hover template) | `--action idle --sheet idle_fly --flip-to left` |
| `attack_side` | `side_attack` | `master` (or `pose_attack`) | `attack` | `--sheet attack_side --flip-to left` |
| `shoot_side` | `side_attack` | `master` | `shoot` | `--sheet shoot_side --flip-to left` |
| `death_side` | `side_death` | `master` | `death` | `--sheet death_side --flip-to left` |
| `levelup_side` (hero) | `side_extra` | `master` | `levelup` | `--sheet levelup_side --flip-to left` |
| `respawn_side` (hero), `raise_side` (summoned) | `side_extra` | `master` | `despawn` (sinks into the ground) | `--action despawn --sheet respawn_side --reverse --flip-to left` (or `raise_side`) |
| `skill_<name>_side` | `side_skill_<name>` (one set per skill) | `master` | `skill` | `--action skill --sheet skill_<name>_side --flip-to left` |
| `fx_<name>`, `thorn_*`, rows marked ⏭ | - | - | not this skill (fx: fal-image vfx; ⏭: later) | - |
Front and back MUST be planned with `--views front` / `--views back` (their action ids become
`front-walk` / `back-walk`): that turns off the turn-around gate, which cannot work on a symmetric view.
Skills: put the skill's body move from `brief.md` in the entry's `motion` and set `"endStill":
"<path to A/design/pose_skill_<name>_vNN.png from the set folder>"`: the clip runs from the master to the
approved peak pose and the game switches back to idle after the last frame. The big effect is the vfx row.
The category folder comes from the sheet name (`scripts/asset_layout.py`: walk/run/fly -> move,
attack/attack2/shoot/cast -> attack, skill, respawn/raise -> spawn, levelup -> level, death, idle, icon -> ui).
Reference lengths (30 fps, `fal-image/classes/*.md`): one-shots are retimed to them (shoot 0.8 s, skill 1.2
s, level-up 0.7 s, respawn 0.6 s, attack 0.7 s, death 0.9 s); loops (walk, run, fly) take their length
from the stride, so a hero run of the reference's 0.2 s does not carry over: keep one clean stride.

## Workflow
0. **Manifest.** `python scripts/asset_status.py <id>`: the rows to make are the `video-sprite` rows marked
   ❌ (or the ones the user names). A row whose still is missing or not approved (a skill without its
   `pose_skill_*`, an enemy without `view_front`) goes back to `fal-image` first.
1. **Stills.** The approved master and the views the rows need, from `fal-image` (`A/design/`).
2. **Masters.** `make_master.py` per view, with `--recap` = the `{design}` slot of `brief.md` verbatim (the
   long recap is repeated in every motion prompt; short recaps let the model redesign the character).
3. **Plan** the sets the rows need (table above). Read every action's `prompt` in `set_plan.json` and edit
   `motion` there for this character: the attack from `{attack}`, the death from `{death}`, each skill from
   its line in `brief.md` (keep "then lies completely still" for deaths). One action per clip; no effects in
   character clips (the game adds FX; big ones are the manifest's vfx rows).
4. **Ask before paying.** Show the user the manifest rows you will make, the clip count and the estimate
   (default `h3-max-turbo` 480P 5 s = ~USD 0.08 per clip; a melee enemy: walk x3, attack, death = 5 clips
   ~USD 0.40, idle is free; a hero with 2 skills: run, attack, death, levelup, respawn, 2 skills = 7 clips
   ~USD 0.56; + retakes) and wait for a yes, unless they
   already approved this run. `FAL_VIDEO_MAX_USD` (default 0.60) caps every clip; `FAL_VIDEO_MODEL` picks
   another model (`kling-3-std` keeps a weapon's pose best but costs ~USD 0.70 a clip).
5. **Run**, then **review**: Read every take's sheet. The gates measure size, feet, zoom, turning, edges,
   background, extra objects, motion, colour and timing; they cannot see identity, a changed weapon, the
   wrong leg order or a covered face. Never accept an action you have not looked at. Classify each take:
   **Pass** (8-10, coherent motion, same character), **Needs Revision** (5-7, name the frames, e.g.
   `F5-F10 pink smear`), **Fail** (1-4). Fix: `accept --window` (a gate that misreads a correct motion),
   `retake --fix <clause id or sentence>` (clause ids in `references/motion-prompts.md`), or plan options.
   Default mode: stop here and show the user (see "Run modes"); `--auto` continues.
6. **Export** each accepted action with `video_to_sheet.py` (one canvas, one body size, see above), then
   `idle_side --rest-frame` from the first side take. Each export replaces the sheet's state folder
   `A/<category>/<sheet>/` (one final version). Log one row per take in `history.md` (`model` column = the
   fal model) and mark the manifest row ✅ `tNN` (⏳ while it waits for the user).
7. **Check**: `motion_check.py` on every sheet, `leg_check.py` on walks; anything only visible in motion is
   unverified until seen in Motion Lab (`python scripts/build_playtest.py`, republish, see `CLAUDE.md`).
8. **Prune** every set once its actions are exported (always; no need to ask).
Report: the manifest after the run (`python scripts/asset_status.py <id>`), the state folder of every sheet,
the model and takes, the cost (`python scripts/cost_report.py --today`).

## Run modes (like fal-image: preview by default)
Read the mode from the request. Every paid clip still needs the cost agreed first (Workflow step 4).
- **Default: preview checkpoint.** After `run` + `review`, do your own review (Pass / Needs Revision / Fail)
  but **do not export**. Stop and show the user, per action: the clip
  (`A/raw/<action>_<set>_tNN.mp4`), the review sheet
  (`review/<action>/tNN-sheet.png`), your verdict with the frames at fault, and the next options. Wait.
  - "ok" / "chốt" → accept (with `--window` if a gate misread it), export, check, prune, log.
  - Natural-language feedback ("liềm bị méo khi chạy", "đánh chậm quá", "ngựa không phi") → **Retake
    translation** below, show the user the new prompt lines and the cost of the retake, then run it and come
    back to this checkpoint with the new take next to the old one.
- **`--auto`**: no stop after review: accept takes that score >= 8 yourself, retake the others with your own
  translated fix up to `--max-takes`, then export, check and prune, and report. The cost must still be
  agreed (the request can carry it: "--auto, tối đa 0.5 USD").
- **Re-export only** (frames cut wrong, loop length, smear colour, size): free, no checkpoint needed
  (`rebuild` + export), see "Changing existing sprites".

### Retake translation (user's words -> a prompt h3-max-turbo follows)
Turn the feedback into short, concrete, physical sentences; keep the rest of the prompt unchanged.
1. Name the defect and where it is ("frames 20-40 of the run: the scythe blade bends and changes length").
2. Write what must STAY, in absolute terms, first: "The scythe keeps exactly the same rigid shape and length
   in every frame: a straight dark iron haft and one curved steel blade; it never bends, stretches or melts."
3. Then the corrected motion, body part by body part, with directions on screen and hand positions ("both
   gauntlets stay on the haft, the blade stays in front of his chest pointing toward the bottom-right").
4. Add the matching clause ids from `references/motion-prompts.md` (`weapon-shape`, `no-blur`,
   `fluid-motion`, `visible-motion`, `steady-cycle`, `never-turn`, `identity-lock` ...).
5. Speed/amplitude words that work: "fast", "powerful", "big clearly visible", "full", "one"; avoid weak
   ones ("slightly", "gently", "subtle") for actions, and never ask for slow motion. For a motion the model
   keeps too small, describe the extreme poses ("the front hooves reach far forward, then the hind hooves
   push far back").
6. h3-max-turbo habits seen so far: lowers or swings a weapon held upright (say "held upright the whole
   time"), warps long thin weapons in fast motion (rigid-weapon sentence + `no-blur`), adds pink/violet
   smears on fast blades (`no-blur`), plays one-shots slowly (the retime handles it), keeps idles very still
   (ask for "clearly visible breathing" and one named secondary motion).
Apply: `sprite_set.py retake --plan ... --action <a> --fix "<sentence>"` (repeatable; clause ids allowed),
and/or edit the action's `motion` in `set_plan.json` for a bigger change; then `run` (1 clip per take).
Log the user's words and the translated fix in `history.md`.

## Changing existing sprites
| Request | What to do | Cost |
|---|---|---|
| Frames cut wrong (loop length, timing, smear colour) | edit `set_plan.json` / export flags, `video_prune.py rebuild`, export again (replaces the state folder) | free |
| Motion wrong (pose, weapon, turned head) | `retake --fix ...`, `run`, review, export | 1 clip per take |
| New stills (restyle, new design, fixed view) from `fal-image` | `make_master.py` from the new still into a NEW folder (`A/.work/masters/<view>_v2`), plan a NEW set (`A/.work/<set>_v2`; plan refuses an existing folder), run, export (replaces the state folder) on the SAME canvas and body height (`meta.json` stays) | 1 clip per action |
Every clip stays in `A/raw/`; the state folder holds only the exported (final) take.

## Per-action options in `set_plan.json` (ours, see `VENDORED.md`)
- `"spins": true`: the body turns on purpose (a whirlwind spin attack); the prompt locks the facing only at
  the start and end. Also set `gates.turn.enabled` to false. Example: bandit `attack_side`.
- `"gaitStride": "period"`: a walk whose `loop-report.json` says `ambiguous` and whose leg check shows both
  steps inside T: loop T instead of 2T (half the frames). `"double"` forces 2T. Then `rebuild` and export.
- `"endStill": "<path from the set folder>"`: pin the clip's LAST frame to another approved still (a death
  ending in the approved lying pose): the still is placed on the start frame's canvas (`job/end.png`).
- `"registerArgs": [...]`: extra `register_clip.py apply` flags, e.g. `["--max-anchor-error", "100"]` when the
  stance anchor misreads a quadruped with a weapon touching the ground; check by hand that the clip's frame 0
  matches the input framing first (centaur, 2026-10-16).
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
| fly, idle (flying) | loop, end frame pinned | square | hover loop |
| idle (walking, hero, ally, boss) | no clip | - | `--rest-frame`: the master pose, 1 frame |
| attack | one-shot, end frame pinned | 16:9 | retimed to 0.7 s, hit at 40% (exported as `hit_frame`) |
| shoot | one-shot, end frame pinned | 16:9 | retimed to 0.8 s, release at 45% (`hit_frame`) |
| skill | one-shot, end pinned to `pose_skill_*` | 16:9 | retimed to 1.2 s, peak pose held at the end |
| levelup | one-shot, end frame pinned | 3:4 | retimed to 0.7 s |
| despawn (-> respawn, raise) | one-shot | square | retimed to 0.6 s, exported `--reverse` |
| death | one-shot, holds the last frame | 16:9 | retimed to 0.9 s, lying still at 80% |
| hurt, jump, cast, guard ... | one-shot | - | kept in the tool, never made for this game (not in any manifest) |
Video models play one-shots in slow motion; the retime cuts frozen holds and compresses to game length.
(The clip canvas only frames the video; every export lands on the asset's one canvas.)

## Where things are, and disk
Layout (`fal-image/format.md` §4): `A/raw/<action>_<set>_tNN.mp4` (+ `.json`: model, prompt, cost, request
id) = every clip the model returned, moved there by `sprite_set.py` **as soon as it is generated** (git keeps
it even before any export); `A/<category>/<sheet>/` = the ONE final version: `preview.gif`, `frames/`,
`check/` (checks and the take's review sheet); `meta.json` names the take. `A/.work/` is for tools only and
is not in git: on another machine, to cut a clip again, plan the set again (`make_master.py` + `plan`), copy
the clip from `raw/` into the new take's `actions/<action>/takes/t01/media/` and `run`: the clip is adopted
(no API call) and matched back to its `raw/` file. One take produces ~550 files / ~70 MB of intermediate frames;
`video_prune.py prune` keeps per set only what decides the frames (the master, the input image and transform
sent to the model, prompts, QC and every stage's JSON in `takes/tNN/record/`): ~1.4 MB per set; the review
folder goes once every action of the set is exported (the chosen take's sheet is in `<sheet>/check/`). Wrong
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
