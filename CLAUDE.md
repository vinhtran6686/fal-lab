# fal-image-lab

Experiment: Claude Code is the "brain" (plans, writes prompts, reviews output, iterates);
fal.ai + OpenAI GPT Image (quality `low` by default) is the "hand" that draws.

- Generator: `scripts/gen_image.py` (run `python scripts/gen_image.py --help`)
- Two skills, one job each:
  - `fal-image` (`.claude/skills/fal-image/`): stills only: a character's approved master and its standard
    views (side, front, back, 3/4 front and back), icon, projectile; towers, props, UI, maps. Format, style
    and views in `format.md`, per-class specs in `classes/` (`enemy.md` Level 1, `hero.md`), other assets in
    `templates.md`. A `style.md` at the project root, if present, overrides the default style block.
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
- Python: in Git Bash `python` may be the Microsoft Store stub; the real interpreter is
  `C:\Users\vinhtv13\AppData\Local\Programs\Python\Python312\python.exe`. Video tools need ffmpeg on PATH.
- Playtest: `python scripts/build_playtest.py` builds `out/playtest/` from `tools/playtest/index.html`;
  publish `index.html` (Sprite Playtest: https://claude.ai/artifact/75DbnF3Fne9dnYVuu9XaSV) and
  `motion.html` (Motion Lab: https://claude.ai/artifact/C4umJEeQjjmx6FAjpcyT1J) with the same files.
- `ref/` holds style reference assets: look only, never send to the API.
- Output: images, `.json` sidecars (prompt, settings, estimated cost) and `costs.csv` go to `out/`.
- Spend summary: `python scripts/cost_report.py [--today]`.
- Secrets: `FAL_KEY` is in `.env` (git-ignored). Never read it, print it, log it, or commit it.
- Cost guard: stay on `--quality low` unless the user explicitly asks for medium/high.
  Video clips cost ~10x an image: show the clip count and estimate and get a yes before a paid
  `sprite_set.py run`; `FAL_VIDEO_MAX_USD` (default 0.60) caps each clip.
- Advisor rule: consult the advisor (Opus 5.5) before locking a plan, after hitting the same error
  twice, and before calling a task done. Use the built-in advisor tool; when it is unavailable, or when
  the user wants proof that Opus answered, call the `advisor` subagent (`.claude/agents/advisor.md`,
  Opus 5.5) with a self-contained brief (task, plan or result, file paths). Its transcript messages record
  the model, so the session can be checked with `list_events`.
