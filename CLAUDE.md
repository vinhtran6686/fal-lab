# fal-image-lab

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
  ...), map in `lib-fx/GUIDE.md` (Vietnamese), rules and commands in `lib-fx/README.md`. Code sits in its family (`force/shock/shock.py`),
  shared kit in `lib-fx/_core/` (`fxcore.py`, `palettes.py`). `python lib-fx/build.py [group[/family[/id]]]` renders each effect
  (`sheet.png`, `frames/`, `preview.gif`, `meta.json` with status draft|approved|rework) plus `lib-fx/_gallery/<group>-<family>.png|gif`
  and `lib-fx/catalog.json`. New effects go into the library first; characters use them from there. Show fx alone for review.
  Design method: `lib-fx/DESIGN.md`; hand-drawn organic shapes (thorns, splats, toon dust via `_core/organic.py`): `lib-fx/RESEARCH-organic-impact.md`.
- **lib-fx/_core/vector/** (since 2026-11-08): the vector kit: rebuild or draw hand-drawn flat-colour VFX as clean Bezier paths (measure
  layer colours + edge gradients + halo, fit tapered strokes, Illustrator-style smooth & simplify, stacked render, review page).
  One JSON profile per effect in `lib-fx/_core/vector/profiles/`; CLI `python lib-fx/_tools/vectorfx.py palette|ingest|measure|rebuild|review|all PROFILE`;
  outputs in `lib-fx/_study/<name>/vector/` (git-ignored). Guide `lib-fx/_core/vector/README.md`; history `lib-fx/research/bezier-shapes/RETROSPECTIVE.md`.
- Python: in Git Bash `python` may be the Microsoft Store stub; the real interpreter is
  `C:\Users\vinhtv13\AppData\Local\Programs\Python\Python312\python.exe` (on the `Admin` machine plain `python`, 3.13,
  works). Video tools need ffmpeg on PATH.
- Reference-video route (experimental, tested 2026-10-29): a character performs a move taken from a sprite sheet of another character,
  fx included: `scripts/make_ref_video.py` (frames -> mp4 >= 24 fps) then fal `minimax/h3-max/reference-to-video` (0.05 USD/s, 5 s = 0.25;
  called directly, log the cost in `costs.csv` by hand). Full method, prompt template, limits: `docs/reference-video-motion.md`.
- Playtest (part of the `video-sprite` skill): `python .claude/skills/video-sprite/playtest/build_playtest.py` builds `out/playtest/`;
  publish `index.html` (Sprite Playtest: https://claude.ai/artifact/75DbnF3Fne9dnYVuu9XaSV) and
  `motion.html` (Motion Lab: https://claude.ai/artifact/C4umJEeQjjmx6FAjpcyT1J) with the same files.
- `ref/` holds reference assets (style anchors, collected or AI-rendered sprites for poses and motion). Since 2026-10-29 they MAY be sent to the API as `--ref` when the user asks or for a test; the prompt says what to take from them (pose, motion, layout, never the character's design) and never names a commercial game.
- Output: images, `.json` sidecars (prompt, settings, estimated cost) and `costs.csv` go to `out/`.
- Spend summary: `python scripts/cost_report.py [--today]`.
- Progress: every character's `brief.md` holds an Asset manifest (rows from `fal-image/classes/<class>.md` §6, format in `format.md` §8: class + role +
  skills -> every still, clip and vfx it needs, with ✅/⏳/❌/⏭). `python scripts/asset_status.py [<id>]`
  answers "trạng thái tới đâu rồi"; guide in `docs/asset-manifest.md`.
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
