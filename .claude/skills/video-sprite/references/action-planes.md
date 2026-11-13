# Action planes in clips

The rules of the view (what a move looks like from the game's camera, the three planes a swing can live in, how casters use them, what to
record for the VFX) are in **`.claude/skills/fal-image/action-planes.md`**. Read it first; this file only adds what is specific to motion.

## What a clip must keep
- **The plane does not change during the move.** State it in the motion prompt in screen words:
  frontal: "the weapon swings like a clock hand seen from the front, flat to the picture";
  ground: "the weapon stays level with the ground the whole time, sweeping from behind the body on the far side, across the front at chest height, to the near side";
  diagonal: "the weapon travels along one slanted line from the upper-left to the lower-right of the frame".
- **Depth order is part of the motion.** In a ground or diagonal move the weapon is hidden behind the body at the start and passes in front of it
  at the end. Say so ("partly hidden behind the torso at first, then fully in front of it"); a clip where the weapon stays in front all the way
  reads as a frontal swing and the flat effect will not match it.
- **Feet and height.** In a ground-plane move the feet stay planted and the hands stay at one height; reject a take where the body rises, hops or the blade tips upward.
- **Body only.** As always, no smear, glow, dust or sparks in the clip (`SKILL.md`): the effect is added from `lib-fx` on the plane recorded for the move.
- **Camera locked**, the character facing right, same body size as the other sheets.

## When a clip is the right tool
| Move | Tool |
|---|---|
| a strike between two clear poses in one plane (smash, chop, uppercut, thrust, a single sweep under ~200 degrees) | pose pair + effect (`docs/pipeline/pose-pair-fx-method.md`), no clip |
| a spin of the whole body, a sweep longer than ~200 degrees, a turn to the other side, a combo that changes plane | clip (this skill) or pose reel |
| a caster's gesture with a readable start and end (raise and plant, sweep, throw) | pose pair or Puppet Kit rig; a clip only if the robe or the body must turn |

## After export
Record for the VFX, from the exported frames: the plane, the hit frame, weapon root and tip on the first and last frame of the strike and, for ground
and diagonal moves, the frames where the weapon is behind the body (the back half of the effect is shown on those frames, the front half on the others).
