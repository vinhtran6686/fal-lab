# Vendored from agent-sprite-forge

- Upstream: https://github.com/0x0funky/agent-sprite-forge, skill `skills/video2dsprite`
- Commit: `5324342fdfab72430f4e9604f3fe427009f8596d` (0.4.0, 2026-10-06), MIT (`LICENSE`)
- Copied 2026-10-14: `scripts/` and `references/` unchanged except the edits below.
  Not copied: `agents/openai.yaml`, the sibling skills (generate2dmedia, generate2dsprite, generate2dmap,
  codeart2d). Their roles are taken by this project's own tools:

| Upstream | Here |
|---|---|
| `generate2dmedia/scripts/route_media.py video` (OpenAI, Gemini, xAI, BytePlus, fal, Codex/Grok CLIs) | `scripts/fal_video.py video` (fal.ai only, same argv and JSON line, `.env`, `out/costs.csv`, per-clip cost cap, `fetch` to recover a paid clip) |
| `generate2dmedia/references/capabilities.json` (fal part) | `scripts/fal_video_models.json` (re-checked against the fal OpenAPI schemas on 2026-10-14) |
| `generate2dsprite/scripts/master_still.py` (master.json) | `scripts/gen_image.py` for the still + `scripts/make_master.py` for master.json |
| `engine_export.py` packages for Godot/web | kept (run by sprite_set); the game format comes from `scripts/video_to_sheet.py` |

## Edits to upstream files (search for "fal-image-lab")
- `scripts/sprite_set.py`
  - `ROUTE_MEDIA` points to `<project>/scripts/fal_video.py`.
  - Facings `down-right` and `up-right` (3/4 front and 3/4 back views of a top-down game) in
    `_parse_facing`, `prompt_words`, the attack lead and the reach measure (`FACINGS`, `RIGHTWARD`).
  - New action `death` (one-shot, 16:9, ends lying still, retimed to 0.9 s) in `ACTION_PRESETS`,
    `ONESHOT_TIMING` and the timing gate.
  - `post_process` re-runs the `keyed` stage when its folder is gone, so a set pruned by
    `scripts/video_prune.py` can be rebuilt from its clip (the later stages already re-run when missing).
  - `build_prompt`: an entry with `"spins": true` locks the facing only at the start and the end (spin attacks).
  - `run_motion` passes an entry's `"gaitStride"` (period|double) to `gait_loop.py select --stride`.
- `scripts/gait_loop.py`: `select --stride auto|period|double` (default auto = upstream): a human's reading of an
  `ambiguous` gait (verdicts `full-stride-confirmed` / `one-step-confirmed`).
- `references/motion-prompts.md`: `death` template and negatives.

To update from upstream: copy the new `scripts/` and `references/`, then re-apply the edits above.
