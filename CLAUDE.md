# fal-image-lab

**Before creating any file, tool, skill, fx or doc, follow `docs/repo-structure-rules.md` (where things go, naming, docs rules).** Docs map: `docs/README.md` (a tree that mirrors the repo: `pipeline/`, `skills/`, `scripts/`, `tools/`, `lib-fx/`; one doc per tool, the file name says the subject). Docs that live next to their code (`lib-fx/README.md`, `tools/studio/README.md`) are listed there too. Add a new doc under the folder of the object it describes and add it to that tree.

Experiment: Claude Code is the "brain" (plans, writes prompts, reviews output, iterates);
fal.ai + OpenAI GPT Image (quality `low` by default) is the "hand" that draws.

- Generator: `scripts/gen_image.py` (run `python scripts/gen_image.py --help`)
- Two skills, one job each:
  - `fal-image` (`.claude/skills/fal-image/`): stills only: a character's approved master (side view) plus,
    for enemies and bosses, front and back views (`format.md` §3: no diagonals), icon, projectile; towers, props, UI, maps. Format, style
    and views in `format.md`, one file per class in `classes/` (`hero`, `ally`, `enemy`,
    `enemy-flying`, `boss`: roles, size, directions, stills, manifest rows, skills; asked with AskUserQuestion
    when missing), reference measurements in `reference.md`, other assets in `templates.md`, example
    requests in `examples.md` (`/fal-image --example --hero`); `--creative` proposes designs from a short idea. A `style.md` at the project root, if present, overrides the default style block.
    `--manual`: no fal call: you write fully expanded prompts for the user to run in ChatGPT, review what they bring back and file only the approved
    images with `scripts/ingest_image.py` (checks + next `_vNN`, cost 0, `costs.csv` untouched).
  - `video-sprite` (`.claude/skills/video-sprite/`): every character animation (move, attack, death ...) from
    the approved stills: image-to-video on fal.ai (`scripts/fal_video.py`) -> keyed, registered, looped or
    retimed frames -> `scripts/video_to_sheet.py` exports them into `out/<class>/<id>/frames/<sheet>/`
    with ONE canvas and ONE body size for every action (`meta.json`). After export, always
    `python scripts/video_prune.py prune --set <set>`; intermediate frames are rebuilt from the clip with
    `rebuild`. Checks: `scripts/motion_check.py`, `scripts/leg_check.py`.
- Asset folder `out/<class>/<id>/` has two groups (`format.md` §4, `scripts/asset_layout.py`): `source/` (approved
  originals: `design/` stills, `video/` clips, `fx/` Python fx code, `vfx/`) and `frames/` (cut from them: one folder per
  sheet with `preview.gif`, `frames/`, `check/`; `icon/`, `fx/<name>/`, `skills/<pose>/`, `export_recipe.json`), plus
  `brief.md`, `history.md`, `meta.json` and `.work/` (tools only, not in git). One session, one finished step: originals
  are cut in the same session; at its end `python scripts/source_prune.py <asset> [--keep ...] --apply` drops every still
  and take that was not approved (no "pick again later": run the flow again).
- Icon packing: `scripts/sprite_pack.py` (single stills into `ui/icon/`).
- Effects (skills, attack smears, respawn, level-up): `scripts/fx_layers.py A/source/fx/<skill>.json`, a recipe of small flat
  layers (slash, ring, burst, bolt, pillar, particles, tweened fx part stills) on one canvas anchored at the
  feet, the reference game's method; no video model. Character clips are body only (`video-sprite` SKILL.md).
- **lib-fx/** is THE fx library for every character (since 2026-11-06): effects drawn in code (0 USD), each stored ON ITS OWN
  (no character), frames @2x. Folders = group -> family (`melee/blade`, `force/shock`, `element/fire/<cast|projectile|impact|aoe|aura|status>`
  ...), map in `lib-fx/GUIDE.md` (Vietnamese), rules and commands in `lib-fx/README.md`, the why and the workflow (rebuild vs original,
  describe -> motion envelope -> apply to a character, sibling folders) in `lib-fx/MINDSET.md`. Code sits in its family (`force/shock/shock.py`),
  shared kit in `lib-fx/_core/` (`fxcore.py`, `palettes.py`). `python lib-fx/build.py [group[/family[/id]]]` renders each effect
  (`sheet.png`, `frames/`, `preview.gif`, `meta.json` with status draft|approved|rework) plus `lib-fx/_gallery/<group>-<family>.png|gif`
  and `lib-fx/catalog.json`. New effects go into the library first; characters use them from there. Show fx alone for review.
  **fxkit** (since 2026-11-13) is how NEW effects are made: an effect = a stack of layers (role, life from the hit frame, back / front of the
  character) drawn between two points a -> b in a palette ramp, every shape varied by a seed, in the house style (few bold smooth shapes,
  2-3 flat stacked tones, glow = the shape blurred, eaten in place). Families declare `EFFECTS` (e.g. `impact/quake/quake.py`); kinds live in
  `lib-fx/_core/formulas/draw/fxkit/layers/`. **Read `lib-fx/_core/formulas/draw/FXKIT.md` before writing an effect or a layer kind.**
  For a character: `python lib-fx/build.py <effect> --from X,Y --to X,Y --pal NAME --seed N --fps 15 --split --out <asset>/frames/fx/<name>`.
  Quality gate: Slash that follows a real weapon swing: add `--track "root_a=X,Y;root_b=X,Y;up=35;turn=cw;ease=1.3"` (FXKIT.md §6); `--set slash.weapon=axe` for parallel axe bands. `build.py` stores `qa` per effect (`lib-fx/_tools/fxcheck.py`); a FAIL blocks `approved`. Review a kind alone with
  `lib-fx/_tools/fxkit_sheet.py`, regression `lib-fx/_tools/fxkit_test.py`. Review `preview_game.gif` (game size), not only @2x.
  Design method: `lib-fx/_core/formulas/draw/DESIGN.md`; hand-drawn organic shapes (thorns, splats, toon dust via `_core/organic.py`): `lib-fx/_core/formulas/draw/RESEARCH-organic-impact.md`.
- **lib-fx/_core/formulas/vector/** (since 2026-11-08): the vector kit: rebuild or draw hand-drawn flat-colour VFX as clean Bezier paths (measure
  layer colours + edge gradients + halo, fit tapered strokes, Illustrator-style smooth & simplify, stacked render, review page).
  One JSON profile per effect in `lib-fx/_core/formulas/vector/profiles/`; CLI `python lib-fx/_tools/vectorfx.py palette|ingest|measure|rebuild|review|all PROFILE`;
  outputs in `lib-fx/_study/<name>/vector/` (git-ignored). Guide `lib-fx/_core/formulas/vector/README.md`; measurements `lib-fx/_core/results/bezier-research/FINDINGS.md`.
  Design foundation (layers, smooth lines, colour hierarchy, lifecycle and per-piece decay, reading references, generator spec): `lib-fx/_core/formulas/rules/`;
  per VFX type (slash, explosion: references, rules, generators, open work): `lib-fx/_core/formulas/rules/vfx/`.
  **lib-fx formulas vs results**: `lib-fx/_core/formulas/` (draw/ code kit, vector/ rebuild kit, rules/ design rules with measurements) and `lib-fx/_core/results/` (vector-showcase/, bezier-research/); map in `lib-fx/_core/README.md`.
  Character-synced slash (M01, code `scripts/slash_fx/`): the current method is `docs/pipeline/pose-pair-fx-method.md`; review every VFX at game size (H = 60 px @1x).
- **Puppet Kit** (since 2026-11-11): character motion from the approved stills with a cut-out rig, no video model, deterministic, 0 USD per
  animation: `scripts/puppet.py check|render|track|slash`, engine `scripts/puppet_kit/core.py`, rig tuner page `scripts/puppet_kit/rig_tuner.html`,
  guide `docs/scripts/puppet_kit/puppet-kit-guide.md` (Vietnamese). A character's rig lives in `<asset>/source/rig/` (`rig.json`, `plate_vNN.png` = the master redrawn
  without weapon and forearms, `poses/*.json` one-part rigs of `pose_*` stills, `anims/*.json`). Use it first for idle, level-up, buffs and
  pose-to-pose attacks; keep `video-sprite` for turns, runs and anything a 2D rig cannot do. `track` writes the weapon root/tip from rig sockets
  in the milestone-01 `weapon_track.json` format; `slash` draws the M01 layered slash on the cut of a pose-to-pose attack.
  **Before writing any animation JSON read `docs/scripts/puppet_kit/puppet-kit-motion-recipes.md`** (sign conventions, timing tables, run cycle, checklist: copy the
  tables, do not re-derive the mechanics). Asset preparation pack, rig v2 (legs / hips / elbows), Rig Tuner v2 and the remaining tech debt: `docs/scripts/puppet_kit/puppet-kit-asset-prep-and-rig-v2.md` `pose` registers a pose still to the rig.
  Limbs and torso should be ONE picture with `"skin"` (smooth joints: the picture bends around elbow, knee, waist) rather than cut at the joint; see `docs/scripts/puppet_kit/puppet-kit-guide.md` "Khớp uốn liền".
  **Pose reel** (2026-11-11, template awaiting user approval): five short pinned clips per character (turn_a, turn_b, run, squat, press) cut into a pose library for what the rig
  cannot draw (large joint bends, runs, turns): `docs/scripts/puppet_kit/puppet-kit-pose-reel.md`, tools `scripts/puppet_reel.py input|cut`, animation shots `{"reel": dir, "pick": [...]}`. Paid clips: ask first.
- **Pose pair + fx method** (2026-11-12, tested on `out/heroes/azure_blade`): a skill = two approved stills (pose A prepare, pose B end, ~0.015 USD each, retry one pose only) + a big blade-swept slash from `lib-fx` + a Studio/Puppet rig with a shoulder-chest muscle link for breath, impact and cape sway; no video, no in-between poses (the `ref/alien` method). Full process, mandatory checklist, costs: `docs/pipeline/pose-pair-fx-method.md`. Heroes are never chibi or cute (`fal-image/format.md`).
- **Rig & Pose Studio** (since 2026-11-11): local editor around the Puppet Kit, `python tools/studio/server.py` (http://127.0.0.1:8765/), guide `docs/tools/studio/puppet-studio-guide.md` (Vietnamese), short README in `tools/studio/`.
  Click = select, press + drag = move, click outside = deselect; pose library in `<asset>/poses/` (independent of `anims/*.json`); edits the rig too (pivots, cut polygons, joint blend, parent, joint limits).
  Studio rig `<asset>/source/rig/rig_studio_v01.json` = `rig.json` + movable foot IK targets + `bone.limit.rot` + `links` (muscle links: when the hand overreaches, the shoulder slides out and the chest near the anchors follows; `carry` = whole body follows; schema and rules for connecting bones in the doc).
  `limit` / `links` only live in the Studio rig, never in `rig.json` (anims may move the shoulders). Core change: `Rig.render` honours `links` (`Rig._pulls`); regression test compares every anim frame with the pre-change core. Regression: `python scripts/puppet_test.py`. **Before adding a joint, muscle link, IK, round joint (`discs`) or limit to a rig, read `docs/tools/studio/puppet-studio-ai-guide.md`** (recipes + code map); the user-facing concepts are in `docs/tools/studio/puppet-studio-concepts.md` (Vietnamese).
- Python: in Git Bash `python` may be the Microsoft Store stub; the real interpreter is
  `C:\Users\vinhtv13\AppData\Local\Programs\Python\Python312\python.exe` (on the `Admin` machine plain `python`, 3.13,
  works). Video tools need ffmpeg on PATH.
- Reference-video route (experimental, tested 2026-10-29): a character performs a move taken from a sprite sheet of another character,
  fx included: `scripts/make_ref_video.py` (frames -> mp4 >= 24 fps) then fal `minimax/h3-max/reference-to-video` (0.05 USD/s, 5 s = 0.25;
  called directly, log the cost in `costs.csv` by hand). Full method, prompt template, limits: `docs/skills/video-sprite/video-sprite-reference-video-route.md`.
- Playtest (part of the `video-sprite` skill): `python .claude/skills/video-sprite/playtest/build_playtest.py` builds `out/playtest/`;
  publish `index.html` (Sprite Playtest: https://claude.ai/artifact/75DbnF3Fne9dnYVuu9XaSV) and
  `motion.html` (Motion Lab: https://claude.ai/artifact/C4umJEeQjjmx6FAjpcyT1J) with the same files.
- `ref/` holds reference assets (style anchors, collected or AI-rendered sprites for poses and motion). Since 2026-10-29 they MAY be sent to the API as `--ref` when the user asks or for a test; the prompt says what to take from them (pose, motion, layout, never the character's design) and never names a commercial game.
- Output: images, `.json` sidecars (prompt, settings, estimated cost) and `costs.csv` go to `out/`.
- Spend summary: `python scripts/cost_report.py [--today]`.
- Progress: every character's `brief.md` holds an Asset manifest (rows from `fal-image/classes/<class>.md` §6, format in `format.md` §8: class + role +
  skills -> every still, clip and vfx it needs, with ✅/⏳/❌/⏭). `python scripts/asset_status.py [<id>]`
  answers "trạng thái tới đâu rồi"; guide in `docs/pipeline/asset-manifest.md`.
- Secrets: `FAL_KEY` is in `.env` (git-ignored). Never read it, print it, log it, or commit it.
  Cloud sessions: `FAL_KEY` comes from the environment's settings (Network secrets or an environment
  variable), never pasted into chat. Network policy must allow the fal API hosts and `*.fal.media` (image
  downloads); `gen_image.py` keeps the paid image URL in the `.json` sidecar if a download fails.
- Cost guard: stay on `--quality low` unless the user explicitly asks for medium/high.
  Video clips cost ~10x an image: show the clip count and estimate and get a yes before a paid
  `sprite_set.py run`; `FAL_VIDEO_MAX_USD` (default 0.60) caps each clip.
- Advisor rule: consult the advisor (Opus 5.5) before locking a plan, after hitting the same error
  twice, and before calling a task done. Use the built-in advisor tool; when it is unavailable, or when
  the user wants proof that Opus answered, call the `advisor` subagent (`.claude/agents/advisor.md`,
  Opus 5.5) with a self-contained brief (task, plan or result, file paths). Its transcript messages record
  the model, so the session can be checked with `list_events`.
