# fal-image-lab

Experiment: Claude Code is the "brain" (plans, writes prompts, reviews output, iterates);
fal.ai + OpenAI GPT Image (quality `low` by default) is the "hand" that draws.

- Generator: `scripts/gen_image.py` (run `python scripts/gen_image.py --help`)
- Workflow: follow the `fal-image` skill in `.claude/skills/fal-image/SKILL.md` for any image request.
- Game assets: shared format + style in `.claude/skills/fal-image/format.md`, per-class specs in
  `classes/` (currently `enemy.md`, Level 1), other assets in `templates.md`.
  A `style.md` at the project root, if present, overrides the default style block.
- Sprite post-processing: `scripts/sprite_pack.py` (slice, align, resize, meta.json).
- `ref/` holds style reference assets: look only, never send to the API.
- Output: images, `.json` sidecars (prompt, settings, estimated cost) and `costs.csv` go to `out/`.
- Spend summary: `python scripts/cost_report.py [--today]`.
- Secrets: `FAL_KEY` is in `.env` (git-ignored). Never read it, print it, log it, or commit it.
- Cost guard: stay on `--quality low` unless the user explicitly asks for medium/high.
