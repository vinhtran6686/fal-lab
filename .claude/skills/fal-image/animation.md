# Animation spec (motion-first, shared by every animated asset)

Read this before making ANY animated sheet: walks, attacks, deaths, idles, tower attacks, VFX.
It decides **what moves and how**; `format.md` still decides style, files, grids and packing, and the
class file (`classes/<class>.md`) adds class defaults (frame counts, prompt wording, commands).

An animation is a motion, not a list of different drawings. "Left foot forward, right foot forward"
describes poses, not the movement between them, and is never a sufficient spec on its own.

## 1. Workflow (every animation request)

| Phase | Output | Where it is written |
|---|---|---|
| A. Analyze the motion | motion card (§2) | top of `A/<sheet>/blueprint.md` |
| B. Define the mechanics | motion phases from the profile (§3), adapted | `blueprint.md` |
| C. Frame-by-frame blueprint | table (§4), one row per frame + loop row | `blueprint.md` |
| D. Key poses before in-betweens | staged generation (§5), reviewed per stage | `history.md` rows per stage |
| Validate | review loop (§8), Pass / Needs Revision / Fail (§7) | `history.md` |

Short requests ("Create a walk animation for this bandit", "idle animation for this magical tower")
are enough: infer the object type, pick its motion profile (§3) and the class defaults, fill the motion
card with documented defaults, and ask the user only when a missing fact changes the result materially
(e.g. "does the tower rotate to aim?"). Write every assumption in the motion card.

If `blueprint.md` already exists for a sheet (an edit), update it first, then regenerate.

## 2. Phase A: motion card

```
Animation:        walk_side (enemy bandit, melee)        Gameplay: travels along the road
Type:             cyclic | one-shot | transition-into <state>
Translation:      translates through the world (move_speed) | in place | stationary object
Direction/camera: moving right; true side profile; top-down camera ~60°
Ground contact:   feet (2) | 4 paws | none (flying/hovering) | base fixed to the ground (tower)
Weight/COM:       COM rides over the support foot, lowest on loading, highest on push-off
Major motion:     legs (stride), pelvis (bob + small rotation), torso (counter-rotation)
Secondary motion: belly bounce 1 frame late, sash tails trail, sword hand swings opposite the lead leg
Poses:            start = contact L ; end = up R→ flows into contact L (loop)
Frames / fps:     8 @ 10 fps = 0.80 s per cycle (2 steps)   Hit/key event frame: -
Must stay fixed:  design, proportions, palette, line weight, light from top-left, camera, facing,
                  pivot at the feet, ground line for planted feet
```

## 3. Phase B: motion profiles (pick by object + action; never force an irrelevant one)

Phases are motion stages, not "one frame each". Distribute them over the class's frame count.

| Object / action | Phases | Contact & weight notes |
|---|---|---|
| Biped walk | contact → down (loading) → passing → up (push-off) → opposite contact → … mirrored | one foot always planted; COM lowest at down, highest at up; arms counter-swing |
| Biped run | contact → down → push-off → **flight** → opposite contact → … | longer stride, both feet off the ground in flight, stronger lean and arm pump |
| Quadruped walk | diagonal pairs alternate: near-front + far-hind, then far-front + near-hind | spine undulates; head bobs on the front-foot contact |
| Multi-legged (spider) | two alternating leg groups (tetrapod-like): lift → reach → plant → push | body stays level with a small bob; legs never all lift together |
| Blob / slime | squash (load) → stretch (launch) → airborne → land squash → recover | volume stays constant: wider when squashed, taller when stretched |
| Flyer / hover | rise → peak → sink → trough | no ground contact; shadow stays on the ground; wings/fins lead the bob |
| Attack (melee) | ready → anticipation → wind-up → action → **impact** → follow-through → recovery | weight moves back on anticipation, forward through impact; impact = the hit frame |
| Attack (ranged / cast) | ready → draw/charge → aim hold → release (hit) → recoil → recovery | the release frame is the hit frame; no projectile in flight on the sheet |
| Jump | anticipation (crouch) → take-off → ascent → apex → descent → landing (squash) → recovery | one-shot or transition-into idle/walk |
| Death | hit reaction → loss of balance → collapse → ground impact → settle → final hold | one-shot; final pose held; same body size as the walk |
| Idle | breathe in → hold → breathe out, small weight shift | in place; motion 1-3% of body height; must not look frozen or jittery |
| Tower attack | target acquisition → aim → fire (hit) → recoil → recover | the base never moves; only the turret/unit/arm moves; idle may be a subtle loop (flag flutter, glow pulse) |
| Projectile | 1 frame, or a short spin/flicker loop | no walk, no character physics; points along travel direction |
| VFX | anticipation flash → expansion → peak → dissipation | one-shot; anchored to one point; may change size freely |

## 4. Phase C: frame-by-frame blueprint

Columns (drop the ones that do not apply to the object, e.g. a tower has no feet):

| F | Phase / purpose | Lead foot | Support / contact | Legs | Pelvis | Torso | Head | Arms / hands | Weapon / gear | COM | From prev → to next |
|---|---|---|---|---|---|---|---|---|---|---|---|

Add a final row `8→1` (cyclic) describing the loop transition, and mark each frame's role:
**K** key pose, **B** breakdown, **I** in-between. The blueprint is what the frames are reviewed against,
and the prompts are written from it (the per-frame pose sentences come from the table).

### Example: 8-frame biped walk, side view, moving right, 10 fps (0.8 s, two steps)

| F | Role | Phase | Lead foot | Contact | Legs | Pelvis / COM | Torso / head | Arms / weapon | Transition |
|---|---|---|---|---|---|---|---|---|---|
| 1 | K | Contact L | L | L heel lands, R toe pushing off | L straight ahead, R stretched back | mid height, level | upright, head level | R arm (sword) forward, L arm back | 8→1: R toe-off becomes this contact |
| 2 | I | Down / loading | L | L flat, R toe lifts | L knee bends, R knee bends lifting | **lowest**, shifts over L | slight forward lean, belly bounces down | arms near max swing | weight drops onto L |
| 3 | B | Passing | (even) | L planted, R airborne | R swings under the body, knee up | rising over L | upright | arms pass the body | R passes L |
| 4 | I | Up / push-off | R | L on toes, R reaching | L extends behind, R reaches forward | **highest** | head slightly up, belly lags | L arm forward, sword arm back | R about to land |
| 5 | K | Contact R | R | R heel lands, L toe pushing off | mirror of F1 | mid, level | upright | L arm forward, sword arm back | mirror of 1 |
| 6 | I | Down / loading | R | R flat, L toe lifts | mirror of F2 | **lowest**, over R | lean, belly down | max swing | weight onto R |
| 7 | B | Passing | (even) | R planted, L airborne | L swings under the body | rising over R | upright | arms pass | L passes R |
| 8 | I | Up / push-off | L | R on toes, L reaching | mirror of F4 | **highest** | head up | sword arm forward | → F1 contact L |

Expected lead-foot pattern for the leg check: `LL-RRR-L` (`-` = passing, legs together).
This replaces the earlier "lead foot alternates every frame" rule (`LRLRLRLR`): that rule only fixed a
limp, it put a contact pose in every frame and skipped loading, passing and push-off.

## 5. Phase D: key poses before in-betweens (staged generation)

One big sheet prompt does not reliably produce correct motion (tested: frames drifted toward the
master's angle, the same leg stepped twice, rows copied each other). So generate in stages, each
reviewed before the next, each image reusing the approved images as `--ref`:

1. **Key + breakdown poses** (walk: frames 1, 3, 5, 7 = contact L, passing, contact R, passing) as a
   2x2 sheet, `--size 1024x1024`, refs: view reference + master. Validate silhouette, foot placement,
   lead foot, body height, weight. Fix or regenerate before going on.
2. **Full sheet** (`--size` from the class), first `--ref` = the approved key-pose sheet:
   "frames 1, 3, 5 and 7 must match the poses of the first reference image; frames 2, 4, 6 and 8 are the
   in-betweens described below". Then validate the whole sequence (§8).
3. A sheet that is right except for a few frames: fix by re-ordering (`sprite_pack.py --order`) or
   regenerate only that sheet; record which frames and transitions were wrong.

For attacks: stage 1 = ready, wind-up peak, impact, recovery (2x2); for deaths: hit reaction, collapse,
ground impact, final pose. For tiny loops (idle 4 frames, projectile, VFX) one stage is enough.
Staged generation costs one extra call per sheet; it is the default for walks and attacks.

## 6. Continuity rules

**Identity (every frame):** same character, proportions, head shape, face/mask, silhouette, clothing,
weapon and accessories, palette, line weight, shading, light direction, camera and facing.

**Space:** one canvas and cell size per asset, one pivot (feet, `format.md` §3), stable scale (the
packer matches body size), planted feet on the ground line, no accidental cropping or padding changes,
no whole-sprite drift. Legitimate body motion is allowed and expected: the body rises, falls, leans,
stretches and compresses as the action requires. Never "fix" motion into identical poses.

**Motion:** every frame continues the previous one; limbs follow smooth arcs; weight transfer is
visible; a planted foot does not slide (unless sliding is the action); the support leg bends under
load; torso, pelvis, head, arms and gear move as one body; secondary motion lags the main motion by a
frame and settles, never jitters; any big jump in silhouette, limb position or height must be explained
by the blueprint.

## 7. Loop closure and acceptance

**Types:** *cyclic* (walk, run, idle, hover: the last frame flows into the first), *one-shot* (death,
jump-and-land, VFX: holds or ends, never forced to loop), *transition-into* (attack recovery ends in
the ready pose of the walk/idle it returns to). Never duplicate frame 1 at the end of a cycle to hide a
discontinuity; that makes a visible stutter. Review `N→1` as carefully as any internal transition:
pose, foot contact, COM, height, orientation, limb trajectories, secondary motion, silhouette.

**Structural checks:** frame count; grid; equal cells; transparency and PNG; no overlap, clipping or
grid artifacts (packer split = `gaps` or `blobs`, never `equal`); stable registration.

**Motion checks:** a clear cycle or action; contact / loading / passing / push-off (or the profile's
phases) distinguishable; logical progression, not unrelated poses; plausible foot contact and release
(leg check against the blueprint pattern); coherent weight shift; arms, torso, head and gear respond to
the main motion; readable silhouette at @1x; timing and spacing give the intended weight and speed;
smooth `N→1` for cyclic animations.

**Classification (write it in `history.md`):**
- **Pass**: structurally correct and the motion is coherent (score 8-10).
- **Needs Revision**: recognizable, but with visible mechanical or continuity issues (score 5-7):
  name the frames/transitions (e.g. `3→4 support foot slides`, `8→1 height pops`).
- **Fail**: structurally invalid, inconsistent or unusable in gameplay (score 1-4).

Frame count alone never makes a Pass. Anything a static image cannot prove (feel of timing, foot slide
at the real move speed) is written as **unverified** until it is seen moving (Motion Lab / playtest),
and stays unverified if no preview was possible. Never invent a validation result.

## 8. Review loop

1. Generate the stage (§5); open the raw sheet and each frame.
2. Pack it (`sprite_pack.py`): frames come out in order, plus a GIF preview at the class fps.
3. `python scripts/motion_check.py A/<sheet>/vNN [--loop|--once]`: measures per frame the body
   height (bob), ground line, horizontal drift, frame-to-frame change, frozen frames and the `N→1`
   jump, and writes `transitions.png` (each transition overlaid as an onion pair, `8→1` included).
   Read the report and the image.
4. Walks: `python scripts/leg_check.py A/<sheet>/vNN` and compare the lead foot per frame with the
   blueprint pattern (`--expected LL-RRR-L --observed ...`).
5. Watch it moving: Motion Lab (https://claude.ai/artifact/C4umJEeQjjmx6FAjpcyT1J) after
   `build_playtest.py` + republish; the user can step frames, pin feet and note bad frames.
6. List defects as transitions (`2→3`, `8→1`) and frames, classify (§7), fix (re-order, regenerate
   the stage that caused it, or adjust fps / move_speed), rebuild, review again.
7. Stop after 3 regeneration rounds per sheet; then document the remaining limitations in
   `history.md` and the report instead of claiming a Pass.

## 9. Known limits (keep in mind, report them honestly)

- The image model draws poses, not motion: it does not keep limb trajectories, exact foot positions or
  body height across frames, and often repeats a pose or copies a row. Staged generation and the checks
  reduce this; they do not remove it.
- Lead-foot reading on 3/4, front and back views is unreliable even zoomed; the user's reading wins.
- Static checks cannot judge timing or foot slide at the real move speed; only a moving preview can.
- `motion_check.py` measures silhouettes (height, ground line, drift, change), not individual limbs.
