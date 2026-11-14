# Action planes: how the game's view turns a move into a picture

Read this before writing a `pose_<action>` / `pose_skill_<name>` prompt, a skill description, or a motion prompt for any class (fighters, mages,
supports, enemies). It answers one question: **seen from our camera, what does this move look like, and where does its effect go?**
The stills, the clips and the VFX (`lib-fx`, `fxkit`) must agree on it, or the effect will not sit on the pose.
Status: the frontal-plane wording is tested (overhead smash). The ground-plane pose pair is tested (2026-11-14, section 4b): pose A (back view) worked at the second try, pose B (open to the viewer) at the third, see the limits below;
the diagonal POSE wordings are still *untested*: the first pose made with each is the test; write what you learn back here.
The ground-plane pair needs a third still, pose C (the blade at the viewer), to read in its direction; in the tested sweep C is the LAST pose: order A (wound back) -> B (about two thirds of the way) -> C (the end, the hit) (2026-11-14, section 2 and `pose-pair-fx-method.md` 10.6). Effects `diag_down`, `diag_up` are built and measured on their own, not yet placed on a real pose pair.

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
| **Ground** (flat to the floor: ahead-behind x near-far) | horizontal sweep at waist or chest height, spin attack, a low leg sweep, a wide "push away" gesture, a ground ring cast around the feet | the arc **almost edge-on**: a flat ellipse, nearly a LINE. The part passing in front of the body is near (thick, bright, drawn OVER the body); the part passing behind is far (thin, dim, hidden BEHIND the body); the two ends are sharp points left and right | a flat lens (`melee/slash/sweep`, build with `--swing`): height about 0.3 of its width, split into a back half and a front half |
| **Diagonal** (tilted between the two) | a slash from high behind the shoulder to low in front (or the reverse, rising), a diagonal staff swipe | a tilted, half-flattened ellipse: it starts high and partly behind the body, ends low and in front of it | a tilted lens (`melee/slash/diag_down`, `diag_up`, build with `--swing`): height about 0.6 of its width, rotated 30-40 degrees |

And two straight lines:

| Line | Moves | What the viewer sees | The effect |
|---|---|---|---|
| **Ahead** | thrust, stab, dash, a bolt or a beam fired at a target | a straight streak to the right | `thrust`, `ranged/bolt` |
| **Up / down** | a pillar cast from the sky, a geyser, a jump smash landing | a vertical streak, then a flat ellipse on the ground where it lands | `element/*/aoe`, `impact/quake` |

A move **toward or away from the viewer** (near / far line: a thrust at the camera) cannot be read as a MOVE in this view: turn it into "ahead".
But a ground-plane arc (horizontal sweep, spin) always passes through the near / far line at its nearest point, and the blade then points AT the camera. A two-pose pair (A far left, B far right) hides that point and the
effect then reads backwards (right to left: tested 2026-11-14, `pose-pair-fx-method.md` section 10.6). **Rule: a horizontal sweep or spin whose arc passes through the near-far line needs a third still, pose C**
(section 4, "Ground, pose C"): the blade (or the hand) points at the viewer and is drawn FORESHORTENED, a short wedge about a third to 40 % of its real length, pointing DOWN in the image from the hands.
**Where C sits in the sequence depends on which way round the ellipse the tip goes** (the tip draws a very flat ellipse; angle 0 = ahead / right, 90 = nearest the viewer, 180 = behind / left, 270 = farthest):
- a 180 degree arc through the NEAR half (left -> near -> right, angles 180 -> 90 -> 0): C is the MIDDLE pose, order A -> C -> B;
- a 270 degree arc that starts through the FAR half (left -> far -> right -> back round the near side to the viewer, angles 180 -> 270 -> 360 -> 450): C is the END pose, order A -> B -> C, and the move finishes
  with the blade at the viewer, which is the hit pose.
The tested sweep uses the second: **A** = hips wound back, the blade behind the body pointing LEFT; **B** = the blade has travelled about two thirds of the way (fitted angle 368, A is 180), now pointing RIGHT
and slightly down; **C** = the end and the hit, the blade pointing at the viewer. It was chosen (2026-11-14) because the move then ends in the hit pose and the far half, drawn dim and thin behind the body, gives the
effect a long, thin start that grows into the bright, blunt head at the hit. The first attempt (C as the middle, A -> C -> B) was rejected: the move did not end on the hit.

## 3. Choosing the plane when a skill is designed
- Prefer the **frontal** plane for the hero's signature and heavy hits: it shows the most and gives the biggest effect.
- Use the **ground** plane for wide, area, "clear the space around me" moves (cleave, spin, sweep, repel). Its effect is a thin line by nature: make it read with
  length, brightness and a ground ring or dust, not with thickness.
- Use the **diagonal** plane for quick ordinary attacks: it reads as a slash without hiding the body.
- One skill, one plane. A move that changes plane halfway (a sweep that ends in a smash) is two effects and two pose pairs.
- How far three key stills can carry a move: a sweep up to about 270 degrees of arc fits three stills (A, B, C) when no leg between two stills is more than about 190 degrees (the tested sweep: A -> B 188, B -> C 82); beyond that the direction of a leg is a guess. A full turn of the body, a spin of 360 degrees or more, or a run needs a clip (`video-sprite`).

## 4. Writing the two poses (pose A = prepare, pose B = end) for each plane
For a THREE-still ground sweep (section 2) the order of travel is A (prepare) -> B (the middle, about two thirds of the way) -> C (the end and the hit); the Ground row below describes A and B, the pose C row the third still.
Keep everything of `docs/pipeline/pose-pair-fx-method.md` §4-§5 (design verbatim, both hands, no effects in the still, margins, pose A as a reference for pose B).
What changes with the plane is WHERE the weapon (or the casting hand, the staff, the focus) is in each pose. Describe it by its place in the IMAGE.

| Plane | Pose A (prepare) | Pose B (end) | Body |
|---|---|---|---|
| **Frontal, downward** (tested) | weapon raised high above and slightly behind the head, the blade pointing up and to the upper-left of the image | weapon low in front, the blade lying level near the ground and pointing right | A: upright, leaning back a little. B: crouched forward, front knee bent, rear leg stretched |
| **Frontal, upward** | weapon low and behind, the blade pointing to the lower-left, close to the ground | weapon high in front, the blade pointing to the upper-right | A: crouched, weight on the rear leg. B: stretched up, on the toes |
| **Ground (horizontal sweep)** | weapon held LEVEL at chest height, drawn back on the FAR side: the blade points LEFT and is partly HIDDEN BEHIND the body, both hands at the far hip or far shoulder; body TURNED AWAY (section 4b): viewed from behind, back and cape in the middle, chest NOT visible, head in profile looking right | weapon held LEVEL at the same height, swung across to the opposite side: the blade points RIGHT and slightly toward the BOTTOM of the image, fully visible IN FRONT of the body, arms extended (in a two-still pair this is the END pose reached through the near half; in the three-still far-half sweep it is the MIDDLE pose, reached through the FAR half behind the body, and the end is pose C); body OPEN TO THE VIEWER (section 4b): breastplate and both shoulder plates visible | feet stay planted in both poses; the torso twists, the hips follow a little; the blade stays level (never tilted up or down), at the SAME height in both poses |
| **Ground, pose C** (the blade points at the viewer: the END of a 270 degree sweep through the far half, or the MIDDLE of a 180 degree arc through the near half) | not used | not used; pose C is the third still (last, after B, for a far-half sweep; between A and B for a near-half arc): the weapon, held with both hands at the SAME chest height, points straight at the viewer; the BLADE is a short wedge (about one third to 40 % of its length) that starts at the fists and points DOWN in the image, its tip about 12 % of the image height lower than the fists | body SQUARE TO THE VIEWER (chest, both shoulder plates and both boots visible and symmetric, the back NOT visible), only the head in profile looking RIGHT; arms stretched toward the viewer and foreshortened (short and wide); the feet in the same place as in A and B |
| **Diagonal, downward** | weapon high behind the FAR shoulder, the blade pointing to the upper-left, partly hidden behind the head and shoulder | weapon low in front of the NEAR hip, the blade pointing to the lower-right, fully visible in front of the body | A: torso twisted away. B: torso twisted open, leaning into the cut |
| **Diagonal, upward** | weapon low behind the far hip, the blade pointing to the lower-left, partly hidden | weapon high in front, the blade pointing to the upper-right, in front of the body | mirror of the row above |
| **Ahead (thrust)** | weapon pulled back level at the near hip, the tip pointing right | weapon fully extended level to the right, the arm straight | A: weight back. B: lunge, front knee bent |

Sentences that keep the model on the plane (add them to the pose text):
- frontal: "the whole swing stays flat to the picture, like a clock hand seen from the front";
- ground: "the weapon stays LEVEL with the ground from start to end, like a helicopter blade seen slightly from above; it never rises above the shoulders and never points up";
- diagonal: "the weapon travels along a slanted line from the upper-left of the image to the lower-right" (or the reverse).
- ground, pose C (the approved prompt of `azure_blade` pose C, 2026-11-14; key sentences, copy them with the character's own design block): "POSE C of a three-part horizontal sweep, the END of the sweep (the hit pose; for a near-half arc write "the MIDDLE of the sweep"), the moment the blade points straight at the viewer, SQUARE TO THE VIEWER: the chest faces the viewer, the breastplate and BOTH shoulder plates are visible and level, the shoulders are symmetrical, the back is NOT visible; only the head is turned in PROFILE to look to the RIGHT of the image." "BOTH ARMS are stretched straight out toward the viewer and hold the sword together, both fists gripping the hilt, one fist right above the other, at the SAME chest height as in the other poses; seen from the front the two forearms are FORESHORTENED, short and wide." "The sword points straight at the viewer, level with the ground in space, so in the picture the BLADE is FORESHORTENED: it appears as a SHORT wedge about one third of its real length, starting at the fists and pointing DOWN in the image, the tip about 12% of the image height LOWER than the fists, the flat of the blade facing the viewer; NOT a full-length blade, NOT pointing left, NOT pointing right." Also attach pose B as a reference and say "the same size of the figure and the same feet position as in the second image; do NOT copy the pose". Result: the wedge came out at about 38-40 % of the visible blade of pose B; approved at the first try.

## 4b. Say the body's orientation in words a model cannot misread (mandatory for every pose)
**Why this section exists (learned 2026-11-14, ground-plane pose A).** The prompt said "the body is turned a little more than the usual three-quarter view so that part of his back shows".
The model drew the usual standing front view: chest, both shoulder plates and symmetric legs facing the viewer, only the face turned right. Nothing in the sentence was
checkable, so nothing forced the model to change. The same prompt rewritten as a list of what the viewer SEES and what the viewer must NOT see gave the intended pose at once.
A wording like "slightly", "a little", "more than", "partly turned", "twisted", "dynamic" is a request for the model's default. The default is the master's pose.

**Rules**
1. **Name one orientation from the table below**, and give its visible / not visible list in the prompt. Never describe a turn by degrees alone, by "three-quarter" alone
   (front three-quarter or back three-quarter?) or by a comparison to another view.
2. **Write what is NOT visible**, not only what is. A model keeps whatever you do not forbid: if the chest must be hidden, say "the breastplate, the belly and the chest are NOT visible at all".
3. **Say what hides what** (depth order): "the hands and the hilt are hidden behind the torso", "only the tip half of the blade sticks out past the back on the LEFT of the image".
   A thing that must be partly hidden is described as hidden, with the part that stays visible named.
4. **Name the head separately** from the body: the head turns independently ("only the head is turned in profile to look to the RIGHT of the image, over the shoulder").
5. **Every part gets a place in the image** (left / right / top / bottom, in front of / behind the body, at chest height), never "the far side", "the near side" or the character's own left / right alone.
   Add the screen words next to them when you use them.
6. **No vague quantity words** in a pose: slightly, a bit, a little, somewhat, more or less, about (for positions), partly (without saying which part), dynamic, natural, powerful stance.
   Replace each with a position, a visible / not visible fact or a number measured on the picture (for example "the blade at chest height, the same height in both poses").
7. **Look at the result yourself before showing it**: tick every visible / not visible line against the image. A failed line is a failed pose, whatever the overall impression.

**Orientation vocabulary** (for a character that faces RIGHT; mirror for LEFT). Copy the lines into the prompt.

| Name | Say in the prompt | Visible | NOT visible |
|---|---|---|---|
| **Master view** (default) | "side view, facing RIGHT, the body turned only about 30 degrees toward the viewer" | face (one eye and a bit of the second), the front of the chest at a slant, the near arm and leg in full | the far arm and leg are partly hidden |
| **Pure profile** | "a pure profile facing RIGHT, only one eye visible, the near shoulder toward the viewer, the chest edge-on" | one eye, the near shoulder, the near arm and leg | the chest face, the far shoulder |
| **Open to the viewer** | "the chest turned OPEN toward the viewer: the breastplate and both shoulder plates visible, the face looking RIGHT of the image" | chest, both shoulders, both legs side by side | the back |
| **Turned away (back three-quarter)** | "VIEWED FROM BEHIND: his back and the cape fill the middle of the picture; the breastplate, the belly and the chest are NOT visible at all; only his head is turned in PROFILE to look to the RIGHT of the image, over his shoulder" | back, cape, both shoulder plates from behind, the head in profile | chest, belly, the face looking at the viewer |

**Template for a ground-plane (horizontal) pose A**, tested 2026-11-14:
"POSE A of a two-part horizontal sweep, VIEWED FROM BEHIND: he is turned AWAY from the viewer, so the viewer sees mostly his BACK. His back and the cape fill the middle of the picture;
the front breastplate, the belly and the chest are NOT visible at all, and the face is NOT looking at the viewer: only his head is turned in PROFILE to look to the RIGHT of the image, over his shoulder.
Both feet planted on ONE horizontal ground line, a wide stable stance, the knees bent, the thighs not horizontal. BOTH ARMS hold the weapon together, the two forearms and the two fists of the SAME size, wound back to the far hip,
HIDDEN BEHIND his body, so the hands and the hilt are NOT visible. The weapon is held LEVEL at chest height and points to the LEFT of the image, parallel to the ground: only the tip half of the blade
sticks out past his back and the cape on the LEFT of the image, the rest is hidden behind his body and cape."
Known limit of that take: one arm may still show on the near side holding the weapon; accept it if the hands stay hidden, or add "the near arm is also behind the body".

**Known limits of the ground-plane pair (2026-11-14).** Three tries for pose B showed what a prompt cannot pin:
- *Feet and size*: percentages of the image ("left boot at 28 % from the left edge") did NOT hold; the figure came out 70-100 px (of 1024) to the left of pose A and 4 % bigger, and the third try was worse than the second. Do not spend retries on it: measure the feet, then align and scale when compositing (`pose-pair-fx-method.md` step 3).
- *Blade slant*: "the tip is lower than the hilt" gave about a quarter to a third of the slant asked for, even with image coordinates and an angle. Ask for a larger slant than needed, or accept a nearly level blade and let the effect carry the depth.
- What did work: orientation names with visible / NOT visible lists, the level-at-chest-height sentence, hiding the hands and hilt in pose A, naming the blade's place in the image.

**Pose B must return to a named orientation too.** Name the orientation (table above) and the feet: "the feet are in the SAME place on the ground line as in pose A".
A model that is told to "open the chest" without a name may keep the back view: write "OPEN TO THE VIEWER: the breastplate and both shoulder plates visible".

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
2. weapon **root** (hilt, hand) and **tip** in pose A and pose B, and in pose C when there is one (in the ORDER OF TRAVEL: `tip_a` start, `tip_b` middle, `tip_c` end; for the 270 degree far-half sweep `tip_c`: the end of the foreshortened wedge, `root_c`: where it leaves the fists, the torso centre and the feet of C too);
3. for ground and diagonal planes also the **pivot** (the shoulder the arc turns around) and whether the weapon passes **behind** or **in front** of the body on its way;
4. the height of the hands above the ground line in both poses (they must match for a ground-plane move).
`weapon_marks.json` keeps these (for a ground pair that does not line up, `out/heroes/azure_blade/source/design/weapon_marks_sweep.json` is the model: measure BOTH stills, align B to A by the feet, and fit the effect to the measured tips with `--swing "tip_a=..;tip_b=..;pivot=.."` (with a pose C add `tip_c=..;root_c=..;pivot_c=..`, the tips in the order of travel: the ellipse is then fitted through THREE tips, k included, swept A -> B -> C through the far half by default, `via=near` for the other way round, and the smear reads in its direction) instead of a fixed shape; `docs/pipeline/pose-pair-fx-method.md` section 10); the effect is then built with `python lib-fx/build.py melee/slash/<effect> --from ... --to ... --track ...` (frontal) or `--swing` (ground, diagonal: `FXKIT.md` section 6).

## 7. Checklist for a pose of a move
- [ ] The plane is named in the skill description and in `brief.md`.
- [ ] Both poses keep the weapon in that plane (ground: level and at one height; frontal: flat to the picture).
- [ ] Positions are given by place in the image (left / right / top / bottom, in front of / hidden behind the body), never by the character's left / right.
- [ ] For ground and diagonal planes: pose A shows the weapon partly hidden behind the body, pose B shows it fully in front.
- [ ] The whole weapon is inside the frame with at least 8 % margin in both poses.
- [ ] The body orientation is a NAME from section 4b with its visible / NOT visible list; no vague quantity word (slightly, a little, more than, partly, twisted) is left in the pose text.
- [ ] Hidden parts are said to be hidden, with the visible part named (what hides what).
- [ ] The result was looked at and each visible / NOT visible line ticked against the image before it was shown to anyone.
- [ ] No effect, no motion lines, no dust in the still.
- [ ] Root, tip, pivot and plane are recorded for the VFX.
- [ ] A ground-plane arc that passes through the near-far line (horizontal sweep, spin) has a pose C (the blade at the viewer, foreshortened, pointing down in the image), the three stills are in the ORDER OF TRAVEL (far-half sweep: A wound back, B about two thirds, C the end and the hit; near-half arc: A, C, B) and the VFX is fitted to three tips in that order.
