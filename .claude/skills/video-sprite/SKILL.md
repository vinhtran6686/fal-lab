---
name: video-sprite
description: Animate a game character's approved stills into consistent sprite animations (walk in 3 views for enemies, run/attack/death/skills from the side view for heroes) with image-to-video on fal.ai, then key, register, loop or retime, finish and export them into out/<class>/<id>/frames/<sheet>/ (one final version; the approved clips kept in source/video/, the rest pruned at the end of the session) with one fixed canvas and body size for every action. Use for any character or enemy animation; the stills come from the fal-image skill.
---

# Video sprites (image-to-video on fal.ai)

Port of `video2dsprite` from agent-sprite-forge 0.4.0 (MIT, see `LICENSE`, `VENDORED.md`), adapted to this
project: clips come from `scripts/fal_video.py` (fal.ai, `FAL_KEY` in `.env`), frames are exported into the
asset folder by `scripts/video_to_sheet.py`, and a top-down tower-defense game needs 1 view for heroes and allies, 3 for enemies and bosses (fal-image/format.md §3).

**Division of work.** The `fal-image` skill makes the stills: one approved master per character (the side
view) and, for enemies and bosses, front and back, plus a pose per skill, all in `A/source/design/`. Every
character's `A/brief.md` holds the **Asset manifest** (rows from `fal-image/classes/<class>.md` §6): the list of every still,
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
| Still -> master.json | `python scripts/make_master.py A/source/design/<still>.png --out-dir A/.work/masters/<view> --name <id> --facing <facing> --recap "<{design}>"` |
| Plan a set | `python .claude/skills/video-sprite/scripts/sprite_set.py plan --master A/.work/masters/<view>/master.json --views <side\|front\|back> --output-dir A/.work/<set> --actions <list> --duration 4 --resolution 480p --fps 15 --target-height <2x{H}> --formats png --max-takes 1` |
| Cost before paying | clips x takes x price (`python scripts/fal_video.py models`), or `fal_video.py video ... --dry-run` |
| Generate + process | `python .claude/skills/video-sprite/scripts/sprite_set.py run --plan A/.work/<set>/set_plan.json` |
| Review | `sprite_set.py review --plan ...`, then **Read** every `review/<action>/tNN-sheet.png` |
| Accept / retake | `sprite_set.py accept --plan ... --action walk --take 1 [--window 0:124]` / `retake ... --action attack --fix weapon-shape` |
| Export | `python scripts/video_to_sheet.py --set A/.work/<set> --action <action> --asset A --id <id> --sheet <sheet> [--flip-to <dir>] [--despill]` |
| Effect layers (free) | `python scripts/fx_layers.py A/fx/<skill>.json` (`--check` validates only) |
| Checks | `python scripts/motion_check.py A/frames/<sheet>`, `python scripts/leg_check.py ...` (walks), Motion Lab |
| Prune (after export; always) | `python scripts/video_prune.py prune --set A/.work/<set>` |
| Rebuild a pruned action | `python scripts/video_prune.py rebuild --set A/.work/<set> --action <action>` (from the clip, no API call) |
`sprite_set.py` resumes where it stopped and never generates a clip twice; every verb prints one JSON line.
A paid clip that timed out is recovered with `python scripts/fal_video.py fetch --job <job.json>` (no new charge).
On Windows a stage can fail with `[WinError 5] Access is denied` while a scanner holds a new folder: run
the same command again (run sets one after another, not in parallel, when it happens).

## Body clips and effect layers (fixed; the reference game's method, measured 2026-10-19)
Everything a character does is two separate things, as in the reference game:
1. **The body clip** (this skill's video): the character only. The prompt never names an effect;
   `sprite_set.py` strips any clause that does (glow, light, lightning, energy, magic, sparks ...) and adds
   "body motion only ... the camera never moves or zooms". Takes with painted glows, rings, starbursts or a
   changing body size are retaken unless the user prefers that take (a hero's banner skill kept the model's own ripple at the
   user's choice): a size change is caught by the `area` gate, a painted glow only by your review of the sheet. The size of
   the character never changes.
2. **The effect layers** (`scripts/fx_layers.py`, no video model, free): small flat objects on ONE effect
   canvas anchored at the character's feet, each 4-18 drawings, played over the body:
   | Layer | Use | Reference example |
   |---|---|---|
   | `slash` | the smear of a swing (a flat crescent, never a blurred trail) | the knight's sword arc |
   | `ring` | ground decal: a perspective ellipse that grows and fades | a smash, a respawn, a ground hit |
   | `burst` | impact flash where a hit lands | a hammer hit, a bolt's end |
   | `bolt` | lightning from the sky or between two points, a new zigzag every drawing | a thunderclap |
   | `pillar` | light column (respawn, level-up, a buff) | a respawn |
   | `particles` | small shards or sparks thrown out | embers, ice shards |
   | `sprite` | a keyframe still from fal-image (one flat element: a cloud, a banner, a crystal) tweened in scale, alpha and position | a summoned banner, a storm cloud |
   One recipe per skill (`A/fx/<skill>.json`: body sheet, canvas and pivot in units of `{H}`, layers with
   `start`/`length` in seconds, z back or front of the body). The tool writes each layer's frames on the shared
   canvas, `fx.json` for the engine and a composite `preview.gif`/`sheet.png`; Read the sheet to review it,
   tune the numbers, run again (free). Before the body clip exists, `"body_still"` previews over the pose.
   Example recipes: in git history (tag `pre-out-restructure`: `out/heroes/holy_commander/fx/radiant_slash.json`); the approved fx of that hero are Python (`source/fx/`).

   **Soft light around a body (level-up, buff, beam, ripple): Python first** (`docs/python-fx-recipe.md`, examples in
   `out/heroes/holy_commander/source/fx/*.py`; numpy + Pillow, no model, $0). Flat vector layers (`fx_layers.py`) read as coarse when laid over a
   body (rejected once); use them for small shaped objects (sprite, projectile). The soft recipe: a wide soft layer that wraps the
   silhouette (blur-and-lift of the body mask, not a max-filter: that gives square halos), additive "screen" light, a `back` and a
   `front` layer, no fine particles that clutter. Make 3-10 variants, let the user pick (a 10-variant round got one clear winner),
   then export the winner as RGBA layers (`tools/frame_tuner/export_fx.py`) placed through the exact chain the body goes through
   (finish scale, feet on the pivot, rescale): re-placed body vs exported body IoU 0.985-0.993. Ship a preview gif and sheet with
   the layers: without one the user cannot see the fx. Clean body clip + Python fx is the default; a model-drawn fx take is
   allowed as a second version when it is cheap and the user wants to compare (it adds stray cones/rings, see motion habits).
   An effect longer than the cell (a beam) is its own canvas, never a wider body canvas.

**Timing, "on twos"** (the reference: 30 fps, each drawing held 2 frames): plan at `--fps 15`. Drawings per
sheet: run 5-6, walk ~12, attack ~10, death 7-9, level-up ~16, respawn ~16. A skill is a short move into its
pose and a long HOLD (reference skills: 39 frames from 4-13 drawings) while the layers play: the `skill`
timing puts the pose at 40% and holds it. Fewer, cleaner drawings read smoother than many wobbling frames.
Clips are 4 s by default (`--duration 4`, up to 5 for many beats): longer takes drift and zoom.

**Ground shadow**: every export draws a flat 35% black ellipse under the feet, behind the body, in every frame
(the reference game bakes it into each walking character's frames); its size is set by the first export and kept
in `meta.json` "shadow". `--shadow-color` for a hero's own colour; `--no-shadow` for flying enemies, whose shadow
is a separate decal. Stills stay shadowless (the magenta key needs a clean background).

**Projectiles**: the `projectile` still flies as an fx recipe (`sprite` layer turning or flickering over 2-4
drawings, plus a `burst` hit of 4-8 drawings): manifest rows `projectile_fly`, `projectile_hit`.

**Respawn and raise**: `rise` (from a kneeling `pose_respawn` to the master) is tested and preferred for heroes: a grey, lifeless
pose that regains colour and stands, ~4 s clip, no post-process for the colour; export it with `--rest-last` (below). The
`despawn` clip (the body sinks into the ground) exported `--reverse` stays the fallback (a statue-like result was criticised),
plus a `pillar` + `ring` recipe or a Python fx.

## One canvas and one body size for every action (fixed)
The engine draws every action of a character in the same frame with the same pivot, so no action may be
bigger or smaller than another:
- **Canvas**: `meta.json` "cell", set by the first export and shared by every later one. Read class and tier
  from the asset's `brief.md` and pass that canvas from the class file's §3 (`fal-image/classes/<class>.md`) as
  `--cell <W>x<H>` on the first export (e.g. hero M: `--cell 176x140`; enemy S: `--cell 92x80`). `video_to_sheet.py` never widens it for one action and
  never shrinks a body to fit; a state that does not fit is refused: delete `meta.json` and re-export every
  sheet with a larger `--cell` (all actions move to the new canvas together).
- **Body**: every set is finished at `--target-height <2 x {H}>` (the tier's body height at @2x, format.md §7:
  XS 48, S 80, M 120, L 168, XL 240, XXL 340); the first export
  records the measured body height (`body_height_2x`) and later exports are rescaled when they differ by
  more than 4% by silhouette area (a height-based check misread weapons and was replaced, 2026-10-16).
- **Pivot**: feet at x 0.5, y 0.88; one fixed transform per clip, so bob, lean, a fall or a spin are kept.
- **`--rest-last`**: a clip that ENDS on the master pose (a rise from kneeling) takes its body size and feet from its last frame, not
  the first (the first frame is kneeling and made the standing end 4% too small). Use it for such a clip.

## Manifest rows -> sets and exports (fal-image/classes/<class>.md; hero/ally 1 direction, enemy/flying/boss 3)
Left is always the mirror of the side (`--flip-to left`); there are no diagonal sheets. The side still is the
`master` (a three-quarter view facing right). `make_master.py --class`: `flying` for flying enemies (hover
idle, no feet gate), `boss`, `hero` or `mob` otherwise.
| Manifest row | Set (`A/.work/`) | Master (`make_master.py`) | Plan `--actions` / `--views` | Export (`video_to_sheet.py --sheet ...`) |
|---|---|---|---|---|
| `master (= idle)` | `side` | `master`, `--facing right` | (no clip of its own) | `--action <any side action> --sheet idle_side --rest-frame --flip-to left`: frame 0 of a side take = the master pose, 1 frame |
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
| `respawn_side` (hero), `raise_side` (summoned) | `side_extra` | `master` | `despawn` (sinks into the ground) | `--action despawn --sheet respawn_side --reverse --flip-to left` (or `raise_side`); its light column + ground ring are an fx recipe |
| `skill_<name>_side` | `side_skill_<name>` (one set per skill) | `master` | `skill` | `--action skill --sheet skill_<name>_side --flip-to left` |
| `fx_<name>` | - | - | no video: `python scripts/fx_layers.py A/fx/<name>.json` (layers below) | `A/fx/<name>/` |
| `thorn_*`, rows marked ⏭ | - | - | later | - |
Front and back MUST be planned with `--views front` / `--views back` (their action ids become
`front-walk` / `back-walk`): that turns off the turn-around gate, which cannot work on a symmetric view.
Skills: put the skill's body move from `brief.md` in the entry's `motion` and set `"endStill":
"<path to A/source/design/pose_skill_<name>_vNN.png from the set folder>"`: the clip runs from the master to the
approved peak pose and the game switches back to idle after the last frame. The big effect is the vfx row.
The category folder comes from the sheet name (`scripts/asset_layout.py`: walk/run/fly -> move,
attack/attack2/shoot/cast -> attack, skill, respawn/raise -> spawn, levelup -> level, death, idle, icon -> ui).
Reference lengths (30 fps, `fal-image/classes/*.md`; the old `sprite_set` retime defaults; a state with a user-tuned frame recipe keeps the
length the user chose, e.g. one hero: attack 1.2 s, death 2.1 s, level-up 1.8 s, skills 2.3-2.9 s, respawn 2.0 s): one-shots are retimed to them (shoot 0.8 s, skill 1.2
s, level-up 0.7 s, respawn 0.6 s, attack 0.7 s, death 0.9 s); loops (walk, run, fly) take their length
from the stride, so a hero run of the reference's 0.2 s does not carry over: keep one clean stride.

## Workflow
Two phases, in this order, for the whole batch of rows this request covers: **Phase A generates and
confirms every pose first** (one row at a time, no exports); **Phase B exports everything once**, after
every row in the batch is accepted. Never export a row and then go back to generate the next one - that
interleaving is the mistake this structure exists to prevent.

### Phase A - describe, generate and accept every pose (repeat per row, export nothing yet)
0. **Manifest.** `python scripts/asset_status.py <id>`: the rows to make are the `video-sprite` rows marked
   ❌ (or the ones the user names) - this whole list is the batch for steps 1-6 below. A row whose still is
   missing or not approved (a skill without its `pose_skill_*`, an enemy without `view_front`) goes back to
   `fal-image` first.
1. **Stills.** The approved master and the views the rows need, from `fal-image` (`A/source/design/`).
2. **Masters.** `make_master.py` per view, with `--recap` = the `{design}` slot of `brief.md` verbatim (the
   long recap is repeated in every motion prompt; short recaps let the model redesign the character).
3. **Plan** the set for the row you are on now (table above). Read the action's `prompt` in `set_plan.json`;
   `motion` there is what step 4 writes and gets approved, not a generic default. One action per clip; no
   effects in character clips (the game adds FX; big ones are the manifest's vfx rows).
4. **Describe the action, get it approved in a loop, THEN price and run - before touching the next row.**
   This is the biggest lever on quality and on cost (`references/motion-prompts.md` "Writing the action").
   Skipped entirely in `--auto` mode (see "Run modes"): there, write the description yourself from the
   template below and the character's `brief.md`, with no stop, and go straight to step 5.
   a. Write the full action, beat by beat, body part by body part, each beat with its time range, e.g.
      "0-0.8 s, <beat name>: <what the body, weapon and any effect physically do>" ... down to the short
      hold at the end; for a move that travels, say where it ends up. This is the actual text you will send
      to the model (translated into the model's prompt language), not a summary of it - show it to the user
      in full and ask them to review it (in `--creative`/`--example`, 2-3 options with their risks).
   b. Wait for the user:
      - **Feedback** (a correction, a different idea, "làm theo kiểu X"): rewrite the WHOLE description
        from scratch around their feedback, at the same beat-by-beat, timed, physical level of detail as
        (a) - a full replacement, never a diff or a note appended to the old text. Show the new full
        description and go back to (a).
      - **Confirm** ("ok", "duyệt", "chốt"): this description becomes the action's `motion`; go to step 5.
      Repeat (a)-(b) until confirmed - do not price or run on an unconfirmed description.
   **Physical motion**: the five phases of `references/motion-prompts.md` "Physical motion" (wind-up, load,
   release, travel or impact, short hold) are the beats (a) breaks the action into.
   **Clip length decides the number of motions**: plan about 0.7-1 s per distinct beat plus about 1 s of
   final hold, 3-5 s in total. Two strikes in 2 s were merged into one by the model; the same two in 3 s
   were both made. A shorter clip drops beats, it does not speed them up; 5 s tends to drift. Say which beat
   should be longest (the model splits time unevenly).
   **Motion quality** that makes an action lively, to add when you complete the user's words (never against
   them): anticipation before the strike, follow-through after, knees giving on impact, cape or cloth thrown
   up and settling; **tremor** (gripping, straining) and **losing balance** (channeling a big move) when the
   move is heavy. A tremor asked in the prompt stays tiny (peak-to-peak ~2.4 px at 480P, below 1 px at game
   size; asking "violent shaking" tripled it and it was still under 1 px at game size): if it must be seen,
   add it in the export (`shake` in the frame recipe, below) and ask the model only for the braced pose.
5. **Ask before paying.** Show the user this one row's clip count and the estimate
   (default `h3-max-turbo` 480P ~USD 0.015 per second: 4 s = ~USD 0.06, 5 s = ~0.08; a melee enemy: walk x3, attack, death = 5 clips
   ~USD 0.40, idle is free; a hero with 2 skills: run, attack, death, levelup, respawn, 2 skills = 7 clips
   ~USD 0.56; + retakes) and wait for a yes, unless they
   already approved this run. `FAL_VIDEO_MAX_USD` (default 0.60) caps every clip; `FAL_VIDEO_MODEL` picks
   another model (`kling-3-std` keeps a weapon's pose best but costs ~USD 0.70 a clip).
   **Written-prompt route.** A hand-written action (formula) is NOT sent through `sprite_set.py plan/run`: its `build_prompt` strips every
   effect word, appends "starts AND ends in exactly the same pose" to any `returnsToRest` action and adds a "same size" tail, which
   contradicts an action that ends in another pose or is allowed one fx. Send it directly:
   `python scripts/fal_video.py video --prompt-file <P.txt> --reference <start.png> [--last-frame <end.png>] --duration 4 --resolution 480p --out-dir <dir>`,
   where `start.png` (and `end.png`) is the keyed still centred on one magenta canvas (the reference hero used 1820x1024, body 268 px;
   no helper script exists yet: place it by hand and keep the same canvas for every clip of the hero). Save the mp4, `.json` and the
   prompt as `A/source/video/<action>_<set>_tNN.*` at once. Frames then come from the recipe route ("Choosing the frames"). The `sprite_set`
   route stays for loops (walk, run, fly), which need its gait gates and loop cutting.
6. **Run**, then **review**: Read every take's sheet. The gates measure size, feet, zoom, turning, edges,
   background, extra objects, motion, colour and timing; they cannot see identity, a changed weapon, the
   wrong leg order or a covered face. Never accept an action you have not looked at. Classify each take:
   **Pass** (8-10, coherent motion, same character), **Needs Revision** (5-7, name the frames, e.g.
   `F5-F10 pink smear`), **Fail** (1-4). Fix: `accept --window` (a gate that misreads a correct motion),
   `retake --fix <clause id or sentence>` (clause ids in `references/motion-prompts.md`), or plan options.
   Default mode: stop here and show the user (see "Run modes"); `--auto` continues.
   **Once this row's take is accepted, do not export it yet.** Go back to step 3 for the next row in the
   batch. Only start Phase B once every row planned for this request has an accepted take.

### Phase B - export every accepted row, once
7. **Export** each accepted action with `video_to_sheet.py` (one canvas, one body size, see above; for a state with a frame recipe use
   `apply_recipe.py`, "Choosing the frames"), then
   `idle_side --rest-frame` from the first side take. Each export replaces the sheet's state folder
   `A/frames/<sheet>/` (one final version). Log one row per take in `history.md` (`model` column = the
   fal model) and mark the manifest row ✅ `tNN` (⏳ while it waits for the user).
8. **Check**: `motion_check.py` on every sheet, `leg_check.py` on walks; anything only visible in motion is
   unverified until seen in Motion Lab (`python scripts/build_playtest.py`, republish, see `CLAUDE.md`).
9. **Prune** every set once its actions are exported (always; no need to ask).
Report: the manifest after the run (`python scripts/asset_status.py <id>`), the state folder of every sheet,
the model and takes, the cost (`python scripts/cost_report.py --today`).

## Run modes (like fal-image: preview by default)
Read the mode from the request. Every paid clip still needs the cost agreed first (Workflow step 5). Both
modes still follow the two-phase structure (Workflow): every row in the batch gets accepted in Phase A
before Phase B exports any of them.
- **Default: two checkpoints per row, Phase A only; Phase B runs once at the end.**
  - **Checkpoint 1 (step 4, before any clip is paid for): the description.** Show the full beat-by-beat
    text, wait for "ok"/"chốt" (go to step 5, price, then run) or feedback (rewrite the whole description,
    show it again, same checkpoint). Never run a clip on an unconfirmed description.
  - **Checkpoint 2 (step 6, after `run` + `review`): the take.** Do your own review (Pass / Needs Revision /
    Fail) but **do not export**. Stop and show the user, per action: the clip
    (`A/source/video/<action>_<set>_tNN.mp4`), the review sheet (`review/<action>/tNN-sheet.png`), your verdict with
    the frames at fault, and the next options. Wait.
    - "ok" / "chốt" → accept (with `--window` if a gate misread it); this row is done - go back to step 3
      for the next row in the batch, or to Phase B if this was the last row. Do not export here.
    - Natural-language feedback ("liềm bị méo khi chạy", "đánh chậm quá", "ngựa không phi") → **Retake
      translation** below, show the user the new prompt lines and the cost of the retake, then run it and
      come back to this checkpoint with the new take next to the old one.
- **`--auto`**: no stop at either checkpoint. Write each row's description yourself (step 4a's template,
  from `brief.md`) with no approval loop, accept takes that score >= 8 yourself, retake the others with your
  own translated fix up to `--max-takes` - across every row in the batch - then run Phase B (export, check,
  prune) once at the end and report. The cost must still be agreed (the request can carry it: "--auto, tối
  đa 0.5 USD").
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

## Choosing the frames: Frame Tuner and frame recipes (`tools/frame_tuner/`, free)
The user picks the smoothest frames, per-frame durations and the hit frame of each clip by eye. The tool shows EVERY frame of the clip
(with the Python fx composited), saves a **recipe** (`A/frames/export_recipe.json`: per state `clip`, `fps`, `keep`, `durationsMs`, `hit`
= index in the kept list, optional `shake`), and `apply_recipe.py <state> --write` exports it through `video_to_sheet.py` (one canvas,
one body size, `--rest-last` where the state asks); `export_fx.py` exports the fx for the same kept frames. Run it as an artifact
(recipes saved in its db; the first Claude-side copy is `export_recipe.json`) or locally with `frame_tuner.bat` + `serve.py`. Offer it after a
one-shot is accepted; with no recipe, the old `retime` default applies.
- Recipes replace `retime --auto-oneshot` for a state that has one. `hit_frame` in `meta.json` counts from 1.
- **Source rate**: the tuner offers the project's 15 fps and the clip's native 24 fps (about 1.6x the frames to choose from); the recipe
  stores the rate it used and `apply_recipe`/`export_fx` read it; the fx counts its beats in 15 fps frames and is mapped by 15/fps.
- **The tuner only chooses among rendered frames**: it cannot repair a blurry, off-size or flickering frame. Check the clip BEFORE it
  goes in: sharp, constant body size (locked tripod), no flicker, facing held, no stray object covering the body. Retake the clip rather
  than tune around a defect. Optional: render at 1080P (same price per second in the model table, sharper visor/face lines, key-edge
  pixels halved, but ~2x slower, ~5x bigger files and a slower `key_out`): default stays 480P; use 1080P on request or for a final
  take of a state that is hard to key.
- **`shake`** `{"from": a, "to": b, "amp": 2.5, "seed": 1}` (indices in the kept list): a deterministic post-process tremor, an offset of
  a few @2x px per frame, eased in and out. About 2-3 px reads clearly at game size where a prompted tremor does not. Demo:
  `tools/frame_tuner/shake_demo.py`.
- The tools carry a hero's `sources.json` (clips, states, fx modules). For a new character copy and edit it; they stay in `tools/` until a
  second character has used them.

## Changing existing sprites
| Request | What to do | Cost |
|---|---|---|
| Frames cut wrong (loop length, timing, smear colour) | edit `set_plan.json` / export flags, `video_prune.py rebuild`, export again (replaces the state folder) | free |
| Motion wrong (pose, weapon, turned head) | `retake --fix ...`, `run`, review, export | 1 clip per take |
| New stills (restyle, new design, fixed view) from `fal-image` | `make_master.py` from the new still into a NEW folder (`A/.work/masters/<view>_v2`), plan a NEW set (`A/.work/<set>_v2`; plan refuses an existing folder), run, export (replaces the state folder) on the SAME canvas and body height (`meta.json` stays) | 1 clip per action |
Every take is saved in `A/source/video/` at once; the sheet folder `A/frames/<sheet>/` holds only the exported (final) take, and at the end of the session `python scripts/source_prune.py A --apply` drops the takes that were not exported or kept as pending (`format.md` §4, "One session, one finished step").

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
| skill | one-shot, end pinned to `pose_skill_*` | 16:9 | retimed to 1.2 s: the pose at 40%, then held while the fx layers play |
| levelup | one-shot, end frame pinned | 3:4 | retimed to 0.7 s |
| despawn (-> respawn, raise) | one-shot | square | retimed to 0.6 s, exported `--reverse` |
| death | one-shot, holds the last frame | 16:9 | retimed to 0.9 s, lying still at 80% |
| hurt, jump, cast, guard ... | one-shot | - | kept in the tool, never made for this game (not in any manifest) |
Video models play one-shots in slow motion; the retime cuts frozen holds and compresses to game length.
(The clip canvas only frames the video; every export lands on the asset's one canvas.)

## Where things are, and disk
Layout (`fal-image/format.md` §4): `A/source/video/<action>_<set>_tNN.mp4` (+ `.json`: model, prompt, cost, request
id) = every clip the model returned, moved there by `sprite_set.py` **as soon as it is generated** (git keeps
it even before any export); `A/frames/<sheet>/` = the ONE final version: `preview.gif`, `frames/`,
`check/` (checks and the take's review sheet); `meta.json` names the take. `A/.work/` is for tools only and
is not in git: on another machine, to cut a clip again, plan the set again (`make_master.py` + `plan`), copy
the clip from `source/video/` into the new take's `actions/<action>/takes/t01/media/` and `run`: the clip is adopted
(no API call) and matched back to its `source/video/` file. One take produces ~550 files / ~70 MB of intermediate frames;
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
