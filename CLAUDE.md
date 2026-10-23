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
    retimed frames -> `scripts/video_to_sheet.py` exports them into `out/<class>/<id>/<category>/<sheet>/`
    with ONE canvas and ONE body size for every action (`meta.json`). After export, always
    `python scripts/video_prune.py prune --set <set>`; intermediate frames are rebuilt from the clip with
    `rebuild`. Checks: `scripts/motion_check.py`, `scripts/leg_check.py`.
- Asset folder `out/<class>/<id>/`: `design/` (the original design: source images, every version), `raw/` (source videos, every
  take, saved as soon as they are generated), state folders `idle/`, `move/`, `attack/`, `death/` ... (ONE final
  version per sheet: `preview.gif`, `frames/`, `check/`), `.work/` (tools only, not in git). `format.md` §4.
- Icon packing: `scripts/sprite_pack.py` (single stills into `ui/icon/`).
- Effects (skills, attack smears, respawn, level-up): `scripts/fx_layers.py A/fx/<skill>.json`, a recipe of small flat
  layers (slash, ring, burst, bolt, pillar, particles, tweened fx part stills) on one canvas anchored at the
  feet, the reference game's method; no video model. Character clips are body only (`video-sprite` SKILL.md).
- Fx Studio (`tools/fx_studio/fx_studio.bat`, engine `scripts/fx_studio.py`): a sprite sheet of a 2D effect -> `out/vfx/<id>/`
  (recipe `fx.json`; `game/`: frames @2x, @1x = fullhd, ipad, manifest in the `ref/hero` format) -> `install` packs atlas
  `go_fx_lab` into the Kingdom Rush 1 game (`KR1_GAME_DIR`, default `E:\work\reverse\games\kr1`, LOVE 0.10.2) and registers
  animation + template; F6/F7 play it in a level. Raster (as drawn) by default; `mode: vector` traces the flat core with
  vtracer and redraws the glow. Guide: `tools/fx_studio/README.md`.
  The main tool is the browser app (`tools/fx_studio/app.html`, Artifact https://claude.ai/artifact/JUVk6cDVriDXhLXLTTQzVi):
  pick character + pose, layer effects on a timeline at game frames (snap to the hit frame), drag to place, recolour, save.
  "cài skill <char>__<pose> từ Fx Studio" = ArtifactData `get` skills/<key> -> Artifact `read` each asset id in
  `layers[].pack` -> `python scripts/fx_studio.py install-pack <assets dir> --skill <doc.json>` (no re-render; F5 in a level).
  State, open work and repo notes: `docs/fx-studio-handover.md`.
- Python: in Git Bash `python` may be the Microsoft Store stub; the real interpreter is
  `C:\Users\vinhtv13\AppData\Local\Programs\Python\Python312\python.exe` (on the `Admin` machine plain `python`, 3.13,
  works). Video tools need ffmpeg on PATH.
- Playtest: `python scripts/build_playtest.py` builds `out/playtest/` from `tools/playtest/index.html`;
  publish `index.html` (Sprite Playtest: https://claude.ai/artifact/75DbnF3Fne9dnYVuu9XaSV) and
  `motion.html` (Motion Lab: https://claude.ai/artifact/C4umJEeQjjmx6FAjpcyT1J) with the same files.
- `ref/` holds style reference assets: look only, never send to the API.
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
