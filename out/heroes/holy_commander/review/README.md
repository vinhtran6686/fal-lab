# holy_commander: animation review package (2026-10-19, take t01 of every clip, nothing exported yet)

For an independent reviewer. Character: hero, tier M, side view facing right, two-handed very long longsword with a gold eagle-head pommel, silver armour with gold swirl pattern, red cape. Approved stills: `design/master_v07.png` (idle), `design/pose_skill_*_v01.png` (the end pose of each skill clip). Style: flat vector cartoon, no glow or soft effects in the character (big effects are separate vfx assets: `out/vfx/`).

Model: fal `minimax/h3-max-turbo` image-to-video, 480p, 5 s. Clips: `../raw/<action>_<set>_t01.mp4` (+ `.json` with prompt and cost).
Contact sheets (first cell = input master, red = frame a gate flagged): `sheets/`. Automatic gate results: `qc/`. Plans with the motion prompts sent to the model: `plans/` (field `actions[].motion`, `endStill` for skills).

## Our own verdicts (please challenge them)
| Clip | Our score | Verdict | Why |
|---|---|---|---|
| skill_charge | 8 | pass | draws the sword, leans into a dash, holds the approved pose; no gate failed |
| despawn (-> respawn, played reversed) | 8 | pass | sinks into the ground cleanly |
| death | 8 | pass | kneels, falls forward, sword beside him, lies still; the `feet` and `turn` gates misread the fall |
| run | 6 | needs revision | motion and sword rigidity good; pink/violet colour bleed on the legs in 28 of 124 frames (fix by `--despill` on export) |
| attack | 6 | retake | good chop, but the model added a huge pink-white slash arc (extra object) |
| levelup | 6 | retake | good salute, but a horizontal sword swing with a green slash effect and dust puffs at the end |
| skill_holy_banner | 3 | retake | pink/gold rings and sparks around the body (area 2.9x master); end pose (raised fist) is right |
| skill_radiant_slash | 4 | retake | huge pink slash arc, identity drop mid-clip; end pose is right |

## Questions for the reviewer
1. Do you agree with each verdict and score? Which clips would you accept as they are?
2. Is the sword rigid and the same character in every frame (identity, weapon length, hands on the grip)?
3. Are the retake fixes right ("no effects, trails, sparks or dust in the character clips")? Anything else to put in the prompt?
4. Do the gates misread correct motion (death `feet`/`turn`) or miss real defects?
5. Does each skill end on the pose of its approved still?
