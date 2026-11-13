# Action planes: how the game's view turns a move into a picture

Read this before writing a `pose_<action>` / `pose_skill_<name>` prompt, a skill description, or a motion prompt for any class (fighters, mages,
supports, enemies). It answers one question: **seen from our camera, what does this move look like, and where does its effect go?**
The stills, the clips and the VFX (`lib-fx`, `fxkit`) must agree on it, or the effect will not sit on the pose.
Status: the frontal-plane wording is tested (`out/heroes/azure_blade`, overhead smash). The ground-plane and diagonal wordings are *untested*: the first
pose made with each is the test; write what you learn back here.

## 1. The view (from `format.md` §1 and §3)
- The camera is high and looks down at the battlefield; the ground is a plane that runs away from the viewer.
- A character's working view is the **side view**: facing RIGHT, the body turned about 30 degrees toward the viewer. Left is its mirror.
- Three directions of space, named by what they are on the SCREEN (use these words in prompts, never the character's own left / right):

| Direction in the world | On the screen | Example |
|---|---|---|
| **ahead / behind** (the way the character faces) | right / left | a thrust goes right; a wind-up pulls the weapon left |
| **up / down** (height) | up / down | an overhead smash comes down; an uppercut rises |
| **near / far** (depth: toward the viewer / away) | slightly DOWN and in front of the body / slightly UP and hidden behind the body | the near arm is in front of the torso; the far arm is partly hidden |

Depth is compressed: a circle lying on the ground is drawn as an ellipse about **0.3 as tall as it is wide** (the value every ground ring in `lib-fx` uses).

## 2. The three planes a move can live in
A swing is an arc around the shoulder. What the viewer sees depends on the plane of that arc.

| Plane | Moves | What the viewer sees | The effect (fxkit `melee/slash`) |
|---|---|---|---|
| **Frontal** (flat to the screen: ahead-behind x up-down) | overhead smash, downward chop, uppercut, upward scoop, a staff raised and brought down | the WHOLE arc, as a big crescent; the full length of the blade sweeps a wide surface | a full crescent (`crescent`, `heavy`, `swing` with `--track`): the widest, most readable smear |
| **Ground** (flat to the floor: ahead-behind x near-far) | horizontal sweep at waist or chest height, spin attack, a low leg sweep, a wide "push away" gesture, a ground ring cast around the feet | the arc **almost edge-on**: a flat ellipse, nearly a LINE. The part passing in front of the body is near (thick, bright, drawn OVER the body); the part passing behind is far (thin, dim, hidden BEHIND the body); the two ends are sharp points left and right | a flat lens (`sweep`, plan S2): height about 0.3 of its width, split into a back half and a front half |
| **Diagonal** (tilted between the two) | a slash from high behind the shoulder to low in front (or the reverse, rising), a diagonal staff swipe | a tilted, half-flattened ellipse: it starts high and partly behind the body, ends low and in front of it | a tilted lens (`diag_down`, `diag_up`, plan S2): height about 0.6 of its width, rotated 30-40 degrees |

And two straight lines:

| Line | Moves | What the viewer sees | The effect |
|---|---|---|---|
| **Ahead** | thrust, stab, dash, a bolt or a beam fired at a target | a straight streak to the right | `thrust`, `ranged/bolt` |
| **Up / down** | a pillar cast from the sky, a geyser, a jump smash landing | a vertical streak, then a flat ellipse on the ground where it lands | `element/*/aoe`, `impact/quake` |

A move **toward or away from the viewer** (near / far line: a thrust at the camera) cannot be read in this view and is never used: turn it into "ahead".

## 3. Choosing the plane when a skill is designed
- Prefer the **frontal** plane for the hero's signature and heavy hits: it shows the most and gives the biggest effect.
- Use the **ground** plane for wide, area, "clear the space around me" moves (cleave, spin, sweep, repel). Its effect is a thin line by nature: make it read with
  length, brightness and a ground ring or dust, not with thickness.
- Use the **diagonal** plane for quick ordinary attacks: it reads as a slash without hiding the body.
- One skill, one plane. A move that changes plane halfway (a sweep that ends in a smash) is two effects and two pose pairs.
- A turn of the whole body, a run or a spin of more than about 200 degrees is not a pose pair: it needs a clip (`video-sprite`).

## 4. Writing the two poses (pose A = prepare, pose B = end) for each plane
Keep everything of `docs/pipeline/pose-pair-fx-method.md` §4-§5 (design verbatim, both hands, no effects in the still, margins, pose A as a reference for pose B).
What changes with the plane is WHERE the weapon (or the casting hand, the staff, the focus) is in each pose. Describe it by its place in the IMAGE.

| Plane | Pose A (prepare) | Pose B (end) | Body |
|---|---|---|---|
| **Frontal, downward** (tested) | weapon raised high above and slightly behind the head, the blade pointing up and to the upper-left of the image | weapon low in front, the blade lying level near the ground and pointing right | A: upright, leaning back a little. B: crouched forward, front knee bent, rear leg stretched |
| **Frontal, upward** | weapon low and behind, the blade pointing to the lower-left, close to the ground | weapon high in front, the blade pointing to the upper-right | A: crouched, weight on the rear leg. B: stretched up, on the toes |
| **Ground (horizontal sweep)** | weapon held LEVEL at chest height, drawn back on the FAR side: the blade points LEFT and is partly HIDDEN BEHIND the body, both hands at the far hip or far shoulder; the chest turned AWAY from the viewer so part of the back shows | weapon held LEVEL at the same height, swung across to the NEAR side: the blade points RIGHT and slightly toward the BOTTOM of the image, fully visible IN FRONT of the body, arms extended; the chest turned OPEN to the viewer | feet stay planted in both poses; the torso twists, the hips follow a little; the blade stays level (never tilted up or down), at the SAME height in both poses |
| **Diagonal, downward** | weapon high behind the FAR shoulder, the blade pointing to the upper-left, partly hidden behind the head and shoulder | weapon low in front of the NEAR hip, the blade pointing to the lower-right, fully visible in front of the body | A: torso twisted away. B: torso twisted open, leaning into the cut |
| **Diagonal, upward** | weapon low behind the far hip, the blade pointing to the lower-left, partly hidden | weapon high in front, the blade pointing to the upper-right, in front of the body | mirror of the row above |
| **Ahead (thrust)** | weapon pulled back level at the near hip, the tip pointing right | weapon fully extended level to the right, the arm straight | A: weight back. B: lunge, front knee bent |

Sentences that keep the model on the plane (add them to the pose text):
- frontal: "the whole swing stays flat to the picture, like a clock hand seen from the front";
- ground: "the weapon stays LEVEL with the ground from start to end, like a helicopter blade seen slightly from above; it never rises above the shoulders and never points up";
- diagonal: "the weapon travels along a slanted line from the upper-left of the image to the lower-right" (or the reverse).

## 5. Casters and supports use the same planes
A mage or a support has no blade, but the staff, the hand or the focus draws the same arcs, and the effect follows the same plane.

| Gesture | Plane | Pose A | Pose B | Effect placement |
|---|---|---|---|---|
| Staff raised, then brought down / planted | frontal, then the ground under it | staff high above the head, top pointing up | staff planted in front, top at chest height | a vertical streak, then a flat ring / eruption at the foot of the staff (`aoe`, `quake`) |
| Arm sweep "scatter", wave of the hand, cone of frost | ground | casting hand drawn back on the far side at chest height | casting hand swung across to the near side, palm open toward the right | a flat fan / lens in front of the body, back half behind it |
| Throw, point, fire | ahead | hand or staff pulled back near the shoulder | hand or staff tip extended to the right at the target's height | muzzle flash at the tip, then `ranged/bolt` to the target |
| Circle around oneself: buff, aura, heal, shield | ground | arms low and open | arms raised, chest open | a flat ring on the floor around the feet: back half behind the body, front half in front (`squash` 0.3) |
| Lift, summon from the ground | up / down | hands low, palms down | hands raised, palms up | a rising column over a flat ring |
| Blessing sent to an ally | ahead (arched) | hand at the chest | hand extended, palm up | `bolt` with `bend` > 0 (a lobbed arc) |

## 6. What to record for the VFX after a pose pair is approved
Measured on the stills (source px), next to the foot mark (`pose-pair-fx-method.md` step 3):
1. the **plane** of the move (frontal / ground / diagonal up / diagonal down / ahead) and the hit frame;
2. weapon **root** (hilt, hand) and **tip** in pose A and pose B;
3. for ground and diagonal planes also the **pivot** (the shoulder the arc turns around) and whether the weapon passes **behind** or **in front** of the body on its way;
4. the height of the hands above the ground line in both poses (they must match for a ground-plane move).
`weapon_marks.json` keeps these; the effect is then built with `python lib-fx/build.py melee/slash/<effect> --from ... --to ... --track ...` (frontal) or the plane options of plan S2 (ground, diagonal).

## 7. Checklist for a pose of a move
- [ ] The plane is named in the skill description and in `brief.md`.
- [ ] Both poses keep the weapon in that plane (ground: level and at one height; frontal: flat to the picture).
- [ ] Positions are given by place in the image (left / right / top / bottom, in front of / hidden behind the body), never by the character's left / right.
- [ ] For ground and diagonal planes: pose A shows the weapon partly hidden behind the body, pose B shows it fully in front.
- [ ] The whole weapon is inside the frame with at least 8 % margin in both poses.
- [ ] No effect, no motion lines, no dust in the still.
- [ ] Root, tip, pivot and plane are recorded for the VFX.
