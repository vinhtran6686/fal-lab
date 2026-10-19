# Game asset format (shared by every class)

Every class file in `classes/` (enemy, hero, ...) inherits everything here. A class adds its slots, its
sheet list and its frame size; it must not change the style, the view prompts, the files or the checklist.
This skill makes **stills**: the approved master of a character and its standard views, plus icons and
other single images. **Animation is never drawn here**: the `video-sprite` skill animates the approved
stills (image-to-video) and exports the frames into the same asset folder. Style references live in `ref/`
(`ref/assets/`, `ref/hero/`; read-only, for looking only: never send them to the API, never copy their
designs, never name the game they come from).

## 1. Style block `{STYLE}` (fixed, append to every prompt)
The block fixes the **design principles** (how things are drawn), not a look: body type, costume, armour,
weapon, colours and which parts are exaggerated belong to each character's `{design}`, so a robed mage, an
armoured knight and a fire elemental can all share it.

> Stylized 2D vector cartoon game art for a top-down fantasy tower defense game, designed to read at about
> {H} pixels tall.
> Simple design: big clear shapes and a strong silhouette; small details are left out or merged into larger
> shapes; faces, hands, armour and clothing are suggested with a few lines, never rendered in fine detail.
> Stylized, exaggerated cartoon proportions, not realistic anatomy (about 2.5 to 4 heads tall): the parts
> that express the character's role are enlarged and the rest is shrunk, so the silhouette reads at {H} pixels.
> Colour: flat solid fills only, no gradients, no airbrush, no painterly texture, no noise, no realistic
> rendering. Volume and shadow come from 2-3 hard-edged tones of the same colour (shadow, base, light), plus a
> few small highlight shapes.
> Thick clean outlines in a dark shade of the neighbouring colour.
> Effects (fire, ice, magic, poison, glow, energy) are drawn as stacked layers of flat single-colour vector
> shapes with an outline that follows the effect's form (flame tongues, ice shards, drips, sparks), never as
> soft blur or gradient glow.
> High top-down camera tilted about 60 degrees; light comes from the top-left.

Why each line (from `ref/hero`, a 64 px fire elemental, studied 2026-10-16): the face is a brow line and an
eye slit; hands are mitten shapes; muscles are 1-2 lines; the body is 3 tones of one orange with a few light
specks; the outline is dark brown, not black; the fire around it is flat yellow layers with flame-tongue
edges; it is about 3.8 heads tall and top-heavy (huge shoulders and arms, small head, short legs), its
exaggeration chosen for its role. It is vector art drawn large and scaled down (hundreds of colours,
anti-aliased edges), **not pixel art**: never write "pixel art" in a prompt (the model then draws fake
pixels that blur when the tools scale them).

`{H}` is the character's body height at 1x from its size tier (§7: 24, 40, 60, 84, 120 or 170); for an
asset without a tier (tower, prop, UI) write 64. Detail scales with it: a 24 px critter is one or two
shapes, a 170 px boss may show a few more.

`{design}` carries what the style leaves open: body type and the parts it exaggerates ("top-heavy: huge
shoulders and arms, small head, short legs"), costume and gear, the weapon and the hand that holds it, the
dominant colour family and one accent, any effect and its colours ("yellow flame layers around an orange body").

**What a character may and may not change** (every class, every asset):
| May set per character (in `{design}` or `brief.md`) | Never, whatever the request |
|---|---|
| dominant colour family and one accent | gradients, airbrush, soft glow, blur, painterly texture |
| outline hue (e.g. centaur: dark purple), still thick and dark | thin, sketchy or black-only outlines |
| which parts are exaggerated, body type, gear | realistic anatomy or rendering, fine detail |
| effects, drawn as flat layered shapes | "pixel art", "ornate", "intricate", "highly detailed", "rim light", glowing auras |
Complex effects are where the model drifts most: keep them to one or two flat layered shapes attached to
the body or the weapon; the big effects of a skill belong to the animation, not to the design still.

**Palette by side** (default; the user's request wins):
- Heroes and friendly units: saturated, clean main colour plus one bright accent, so they stand out on the map.
- Enemies: a slightly darker, muted main colour plus one warning accent (red, sickly green, violet ...).
- Never magenta or pink on any subject (`{BG}` is keyed out).

**Style anchors** (review only): before approving a new master, open it next to `ref/hero/frames/hero_elemental_0014.png`
(and, once one exists, the first approved master of the project) with the Read tool and check outline weight,
tone count, shape size and face simplicity match. Never send an anchor as `--ref`: `ref/` never goes to the
API, and an approved master's design would leak into the new character.

If `style.md` exists at the project root it replaces this block. Assets made before 2026-10-16 (bandit) used
the previous block (muted earthy palette, near-black outlines, oversized chibi head); restyle them only on request.

## 2. Generation rules (fixed; tested 2026-10-13/14)
| Rule | Value | Why |
|---|---|---|
| Model | `gpt-image-2` (default) | follows the style; gpt-image-1.5 drew a furry 3D look |
| Size | `--size 1024x1024` for every character still; other assets as in `templates.md` | master, views, icon, projectile |
| Background | flat magenta `#FF00FF` + `--png`, **no `--transparent`**, for every asset except opaque maps; the tools key it out | gpt-image-2 has no transparency on fal |
| Consistency | every image after the master uses `--ref <approved master>` and repeats `{design}` verbatim | keeps design, colors, gear and proportions identical in every view |
| Pose | every view: the same neutral standing ready pose, full body and weapon inside the frame, filling about 70% | video-sprite starts every clip from this still; a cut-off weapon or an odd pose shows in every frame |
| Quality | `low` while testing; `medium/high` only after the user asks | cost |

`{BG}` (append to every prompt):
> Background: one flat solid pure magenta color (#FF00FF) everywhere, no gradient, no ground,
> no shadow, no scenery, no text, no border. Do not use magenta or pink anywhere on the subject.

`{SIMPLE}` (append to every character prompt, right after `{design}` and the view; learned 2026-10-17: without
it the first masters came back with buckles, pouches, bandages and fabric texture, scored 7 and were redrawn):
> The face is only a brow line and a small eye slit; hands are simple mitten shapes, visible and holding the
> weapon (not hidden in sleeves). No buckles, no pouches, no straps beyond one, no rope, no bandages, no
> spikes, no stitches, no patches, no fabric texture: clothing is a few big flat shapes. At most three
> colour families. The weapon and every part of the body stay inside the frame with margin on every side.

Proportions drift taller: ask for half a head less than wanted ("about 3 heads tall" came back near 4), and
a long upright weapon (glaive, staff, spear) held diagonally so its tip does not reach the top edge.

## 3. Directions and views
**Only movement has several directions** (the reference game's code, `reference.md`): a class either has one
movement sheet seen from the side (heroes, allies) or three (side, down, up: enemies, flying enemies, bosses).
Every other state (idle, attack, death, skills) is drawn once from the side; left is always the mirror of
the side, and a diagonal view is never made. Each class file (§4 "Directions and master") says which.

**"Side" is not a flat profile**: the side sprite is a three-quarter view facing right, the body turned about
30-45 degrees toward the camera (high top-down view), the face and the front of the torso visible, the far
arm and leg partly hidden; four-legged beasts sit closer to a profile but still turn the head toward the
camera. "Down" is a straight front view, "up" a straight back view. *Master wording untested*: the first
master made with it is the test.

**The master IS the side view.** It is the direction the game shows most, so it gets the best drawing; every
other still (`view_front`, `view_back`, `pose_*`, icon) is redrawn from it with `--ref`. Idle is the master
still itself, except for flying enemies (an animated hover). Still names in `design/`: `master_vNN`,
`view_front_vNN`, `view_back_vNN`, `icon_vNN`, `projectile_vNN`, `pose_<action>_vNN`, `pose_skill_<name>_vNN`.

### View prompts (every class)
`{kind}` is the class word ("enemy", "hero", "friendly soldier"). Every view prompt is:
`Use the reference image only for the character design; redraw it in the style described. Single game
{kind} sprite: {design}. <VIEW> {UPRIGHT} Full body, centered, filling about 70% of the frame.
{SIMPLE} {BG} {STYLE}`. The master has no `--ref` and starts directly with "Single game {kind} sprite: {design}.".
`{UPRIGHT}` (in the master and every front/back view, all classes; learned 2026-10-19: without it the master came
back leaning along a diagonal, one foot higher than the other, the sword raised, reading as the old 3/4 view):
> Standing UPRIGHT in a calm neutral idle stance: the body vertical, not leaning and not walking diagonally,
> both feet side by side on ONE horizontal ground line, the weapon held at rest (lowered or upright in front of
> the body, not raised to strike), a shield or off-hand item held at the side.

Flyers replace it with: "Hovering UPRIGHT and level in place, not diving or climbing diagonally, wings spread
level, the body at one steady height". Blobs: "Resting upright and level, the flat base on ONE horizontal
ground line".

`<VIEW>` comes from the table of the character's `{body}`. The model pulls front and back views back toward
the turned master: name the angle in capitals, say what must and must not be visible (eyes, face, which side
the weapon or the asymmetric mark is on), and end with "Not a side view". A `pose_<action>` still uses the
same skeleton with the master's view, the pose instead of `{UPRIGHT}`, and `--ref <master>`.

**biped** (two legs; front and back tested on bandit 2026-10-13/14). `{weapon hand}` is the hand that holds
the weapon (or the staff, the book ...).
| Still | `<VIEW>` |
|---|---|
| `master` | SIDE VIEW from a high top-down camera: facing RIGHT toward the right edge of the screen, the body turned only about 30 degrees toward the viewer so the face and the front of the chest are visible, the far arm and leg partly hidden behind the body. Not a flat profile, not a front view, not a diagonal three-quarter view toward the bottom-right. |
| `view_front` | Straight FRONT view, perfectly facing the viewer, walking toward the bottom of the screen, mirror-symmetric body: both eyes visible, both shoulders the same size, feet side by side, the weapon held upright in its {weapon hand} (on the left side of the image for a right hand). Not a side view. |
| `view_back` | Straight BACK view, seen from directly behind, walking away toward the top of the screen: the back of the head, NO face and NO eyes visible, mirror-symmetric body, feet side by side with the heels toward the viewer, the weapon held upright in its {weapon hand} (on the RIGHT side of the image for a right hand). Everything worn on the FRONT (a helmet lamp, a visor, an emblem, a belt buckle) is hidden; everything worn on the BACK (a sack, a quiver, a cape, wings) is in full view and covers the back. Not a side view, not a front view. |
| `pose_ready_side` (example of `pose_<action>`) | The master's SIDE VIEW (facing right, turned toward the viewer) in a combat-ready stance: knees bent, weight forward, the weapon raised and ready to strike. |

**quadruped** (four legs, incl. centaurs and beasts; *untested*): as biped, with these changes.
- `master`: the long body level across the frame, head and chest to the right, tail to the left, turned toward the viewer so the near flank and both pairs of legs show, the face visible; all four feet on one horizontal ground line, the back level (not climbing or walking diagonally), the weapon at rest.
- `view_front` / `view_back`: the body foreshortened to a short block, front legs side by side (front) or hindquarters and tail (back); the long body is hidden behind the head or the rump.

**blob** (no legs: slimes, oozes; *untested*): no `{weapon hand}`, no feet; "standing" becomes "resting on
a wide flat base on the ground". `{design}` must name one asymmetric mark and its side ("a drip on its RIGHT
side"): that mark tells the views apart. Master: facing right, eyes and mouth shifted to the right, the flat base level on one horizontal ground line. Front:
eyes and mouth centred, the mark on the image left. Back: no face, only a highlight arc, the mark on the image
right. The top-left highlight never moves with the body.
Blob and flyer have no head count: `{design}` gives a width-to-height ratio instead of "2.5 to 4 heads tall"
("about 1.3 times as wide as it is tall").

**flyer** (wings, floats; *untested*): no feet on the ground; "standing" becomes "hovering in place, wings
spread level". Master: facing right, the body upright and level (not diving or climbing diagonally), wings spread, the near wing in front; front/back: wings spread
symmetrically, face visible / hidden. In the references a flyer floats with its body about a third of the
canvas above the ground line; video-sprite uses its `flying` profile.

### Icon and projectile (every class)
**icon** (`--ref <master>`):
> Round {kind} portrait icon: ONLY the head and shoulders of {design}, cropped at the chest, facing
> slightly right, inside a circular badge with a thick dark outline and a {rim} rim, plain {badge}
> background inside the circle. {BG} {STYLE}

`{rim}`/`{badge}` come from the class file (so heroes and enemies read apart on the HUD). For a blob or a
creature without shoulders: "ONLY the upper half of {design} with its face".

**projectile** (`--ref <master>`, when the class says the character shoots):
> Single projectile sprite fired by the {kind} in the reference image: {projectile}. Pointing right,
> centered, small and simple, filling about 40% of the frame. {BG} {STYLE}

### Commands (project root)
Let `A=out/<class>/{id}` (class folder from the class file) and `M=A/design/master_vNN.png` (approved master).
```
python scripts/gen_image.py "<master prompt>" --size 1024x1024 --png --name master --versioned --out A/design
python scripts/gen_image.py "<view prompt>"   --size 1024x1024 --png --ref M --name view_front --versioned --out A/design
# ... view_back (enemies, bosses), pose_*, icon (and projectile) the same way; independent stills run in parallel
python scripts/sprite_pack.py A/design/icon_vNN.png --asset A --kind <kind> --id {id} --state icon --dir none --grid 1x1 --frames 1 --cell 128 --center --own-scale --fill 0.95
```
Then the animations: `video-sprite` skill, with the frame size of the class file.

## 4. Files, folders and versions (fixed)
One folder per asset (`out/<class>/<id>/`: enemies, heroes, towers, props, vfx, ui, maps ...). Sources keep
every version; state folders keep only the one final version; `.work/` holds the tools' intermediate data
and is not in git.
```
out/<class>/<id>/                         e.g. out/heroes/centaur/
  brief.md                                request, class/level, filled slots, approved design stills and poses
  history.md                              one row per still or video take: version, score, verdict, issue, change
  meta.json                               engine metadata: one canvas, pivot and body size for every action
  design/                                 the ORIGINAL DESIGN (this skill), every version: master_v03.png, view_front_v01.png, pose_run_v01.png ... (+ .json)
  raw/                                    SOURCE videos (video-sprite), every take, saved as soon as the model returns
    run_side_run_t02.mp4 (+ .json)   <action>_<set>_tNN: the .json holds model, prompt, cost, request id
  idle/ move/ attack/ death/ ...          STATE folders (category, scripts/asset_layout.py): ONE final version each
    move/run_side/                        one folder per sheet
      preview.gif                         look here first
      sheet.png                           horizontal sheet @2x
      frames/@2x/hero_centaur_run_side_01.png ...   frames for the game (also @1x)
      check/                              motioncheck.txt, transitions.png, legcheck.png, take_review.png
  ui/icon/                                packed icon (sprite_pack.py from design/icon_vNN.png)
  .work/                                  tools only, not in git (video-sprite sets pruned to their decisions)
```
Assets without a class file (towers, props, vfx, ui, maps; `templates.md`) use the same folder:
`out/<kind>s/<id>/` with `brief.md`, `history.md` and `design/` (+ packed frames when the asset is cut up).
Re-exporting a sheet replaces its state folder; the take it came from is named in `meta.json` (`version`,
`source`), and every other take stays in `raw/` (any of them can be accepted and exported later).
Categories: `move` (walk, run), `attack` (attack, cast), `death`, `hurt`, `idle`, `ui` (icon), `projectile`.
- Design still names: `<name>_vNN.png`, made by `gen_image.py --name <name> --versioned --out <asset>/design`.
- Frame names keep kind and id (`enemy_bandit_walk_side_03.png`) so they are unique inside a game project.

Game-ready frames (the same for every action of an asset):
| Item | Value |
|---|---|
| File type | PNG-32 RGBA, transparent; `@2x` master and `@1x` in-game |
| Canvas | **one canvas for every action of an asset** (`meta.json` "cell"), from the class file's §3 (class and tier, §7). No action gets a bigger or smaller frame, so the engine never rescales one action against another |
| Body | **one body height for every action**: `2 x {H}` at @2x (video-sprite `--target-height`), recorded as `meta.json` "body_height_2x"; a sheet whose body differs by more than 4% is rescaled on export |
| Pivot | feet, x 0.5, y 0.88 of the canvas (`meta.json` "pivot"; fixed in `video_to_sheet.py`); icons are centered. The reference game sets the anchor per character (0.10-0.25 of the canvas above the bottom, median 0.18) and the engine reads it per character; this project fixes it at 0.88 for every asset and records it in `meta.json`, the size matrix (§7) already includes the room below the feet |
| Motion | `move_speed` (px/s at 1x) in `meta.json`, tuned in the playtest so the feet do not slide |
Frame size: §7.

`history.md` row format (append one row after reviewing every still or take, including rejected ones):
`| date | sheet/still | vNN | model | score | approved/rejected/final/awaiting user | issue | change for next version | requested by (pipeline/user: "...") |`

## 5. Run modes (fixed for every class)
**Default (no `--auto`): master checkpoint**
1. Write `brief.md` (fill the class's content slots from the request; invent sensible details).
2. Generate the master into `design/`; self-review it and regenerate while it fails the checklist (max 3).
3. **Stop.** Show the user the master candidates (paths + scores + issues), recommend one, and wait.
4. When the user approves one ("chốt v02"), record it in `brief.md` and `history.md`, then make the other
   standard views and the icon (§3) the same way (each reviewed, max 3 versions), show them, and wait for
   approval before any animation is paid for.
5. Animation: hand over to the `video-sprite` skill with the approved design stills.

**`--auto`**: as above, but approve the master and the views yourself (score >= 8), then continue with
`video-sprite` (it still asks before paying for video unless the request already approved the cost).

**Restyle a character** (same character, new look: "restyle bandit sang ...", a new `style.md`):
1. Write the new style block (into `style.md` if it should apply to every asset, else into `brief.md`
   as `{STYLE}` for this character) and record the request in `brief.md`.
2. New master: `--ref <current approved master>`, prompt starts "Use the reference image for the character
   design (shape, gear, colours, proportions, the hand that holds the weapon); redraw it ONLY in the new
   style described", then `{design}`, the master view, `{BG}`, the new `{STYLE}`. Next free `master_vNN`;
   old stills stay. Stop for approval (unless `--auto`).
3. Every standard view again from the NEW master (§3), next free versions; approve them.
4. Update `brief.md` (approved stills) and `history.md`; animations are then redone by `video-sprite`
   from the new stills (paid clips; old sheets stay as earlier versions).

**Edit an existing character** (e.g. "đổi đao thành rìu"): changing the master or `{design}` affects every
view and every animation: confirm with the user first, then regenerate the stills, then the animations.
Fixing one view only (e.g. the back view shows the face): generate the next version of that still, and
re-animate only the actions that start from it.

## 6. Review checklist for stills (score 1-10, redo below 8)
- Same character as the master: colors, gear, proportions, the weapon's shape and the hand that holds it.
- The view is exact (§3 table of its `{body}`): master = three-quarter view facing right, body turned about 30° toward the viewer,
  face visible (not a flat profile, not a front view); front = mirror-symmetric, face visible; back = no face.
- Neutral pose (or the requested `pose_*`), full body and weapon inside the frame with margin, nothing touching the edges.
- Back view: no front-worn item shows (a lamp, a visor, an emblem); back-worn items (a sack, a quiver, a cape)
  cover the back. A back view that shows the front of the gear is a front view with the face removed: redo it.
- Master and front/back views: the body upright (its vertical axis vertical, not leaning along a diagonal),
  the feet (or base, or all four feet) on ONE horizontal ground line, the weapon at rest, not raised to strike;
  a figure that reads as walking diagonally toward a corner is the old 3/4 master: redo it (learned 2026-10-19).
- Style (§1): simple big shapes and a clear silhouette at `{H}` px; no fine detail on face, hands or clothes;
  stylized proportions as `{design}` says; flat fills with 2-3 hard tones per colour, no gradient or blur;
  thick outlines in a dark shade (or the hue set in the brief); effects as flat layered shapes, not glow.
  A new master also matches a style anchor (§1) side by side.
- Flat magenta background only; no magenta or pink on the subject, no ground, shadow or text.
- Class-specific points in the class file.

## 7. Size: tiers and profiles (fixed; measured 2026-10-17)
Every character has a **class** and a **size tier** before anything is drawn (SKILL.md "Ask for class and
size"). The tier fixes the body height `{H}`; the class fixes the frame profile; together they give the canvas
that every action of the asset shares.

**Size tiers** (`{H}` = height of the whole standing idle silhouette at 1x, feet to the top of whatever the
idle pose shows, a weapon held upright included; the same box video-sprite measures for `--target-height`):
| Tier | `{H}` @1x | `--target-height` (@2x) | Range in the references | Typical |
|---|---|---|---|---|
| XS | 24 | 48 | 17-30 | spiderling, rat, imp, sheep |
| S | 40 | 80 | 31-48 | goblin, bandit, skeleton, footman, archer, small mage |
| M | 60 | 120 | 49-70 | most heroes, knight, raider, werewolf |
| L | 84 | 168 | 71-100 | robot, golem, ogre, yeti, troll brute |
| XL | 120 | 240 | 101-140 | mini-boss, giant |
| XXL | 170 | 340 | 141-200 | boss |

**Frame profiles** (canvas in units of `{H}`, feet at x 0.5, y 0.88):
| Profile | Canvas W x H | Used by | Why |
|---|---|---|---|
| `unit` | 2.25 x 2.0 | allies, enemies | room for strikes and a death falling toward the viewer |
| `hero` | 2.6 x 2.3 | heroes | room above the head for casts, level-up and respawn |
| `boss` | 2.55 x 1.7 | bosses | wide, low frames |
Measured on the references (`reference.md`): 73% of them fit their profile canvas; the rest are wide death
falls and skill moves, which our prompts keep inside the frame.

**Classes** (each file holds its tiers with the canvases, rounded up to 4 px; @2x doubles them):
| Class | File | Folder | Profile | Tiers (default *) |
|---|---|---|---|---|
| hero | `classes/hero.md` | `out/heroes/` | hero | S, M*, L |
| ally | `classes/ally.md` | `out/allies/` | unit | S*, M, L |
| enemy (walking) | `classes/enemy.md` | `out/enemies/` | unit | XS, S*, M, L |
| enemy (flying) | `classes/enemy-flying.md` | `out/enemies/` | unit, one tier up | S, M* |
| boss | `classes/boss.md` | `out/bosses/` | boss | XL, XXL* |
A new class is a new file in `classes/` with the same nine sections, and a row here.

Rules that come with the size:
- Pass the canvas to video-sprite as `--cell <W>x<H>` (1x) and `--target-height <2 x {H}>`; record class,
  tier, `{H}` and canvas in `brief.md`.
- `{attack}`, `{death}` and casts are written to stay inside the canvas (strike forward or upward, fall
  in place); the exporter refuses a frame that does not fit and never shrinks it.
- **Big skill effects are separate assets**, as in the references: a rain of fire, a lightning chain or a
  summoned storm is a vfx asset (`templates.md` vfx, `out/vfx/<id>/`) placed over the scene by the game. Only
  the body and effects touching it (a glowing fist, flames on the weapon) stay in the character's frame.
- **A frame that does not fit**: first re-prompt that action to stay inside the canvas (shorter reach, fall
  in place); if it still does not fit, use the next tier's canvas of the same profile, keep `{H}`, and record
  it in `brief.md`. Never shrink the body.
- Class-specific palettes, rims and review points are in each class file.
- Flyers (*to confirm*): the references float their body well above the canvas bottom (feet line about
  0.55-0.65); until a flyer is made, use the `unit` canvas one tier up and note it in `brief.md`.
- `{H}` replaces "64" in `{STYLE}` (§1).

## 8. Asset manifest: what a character needs (fixed; from the reference game's code and atlas, 2026-10-18)
Every character's `brief.md` holds an **Asset manifest**: the list of every still, clip and effect the
character needs, with its status. It is written with the brief (from class, role and skills), shown to the
user before the master, and kept up to date by both skills: fal-image fills the stills and effects,
video-sprite the clips. `python scripts/asset_status.py` reads every manifest ("trạng thái tới đâu rồi").

**Rules of the reference game (from its code):**
- Only **movement** has several directions: walking and flying enemies and bosses draw 3 (side, up, down);
  heroes and allies 1 (`run`). Every other state (idle, attack, death, skills) is drawn once, from the
  side, and flipped left/right to face the target.
- The game picks the walk sheet by quadrant: 315-45° side, 45-135° up (back), 135-225° side flipped,
  225-315° down (front), with 10° of stickiness so a diagonal near 45° does not flicker between two sheets.
  Up and down sheets must still look right when the character actually moves up to 45° off vertical.
- `idle` is a single still frame (the master) for walking enemies, bosses, heroes and allies; a flying
  enemy's idle is an animated hover.
- 30 fps, mostly drawn "on twos" (each drawing held 2 frames: about 15 drawings a second).

**Roles and rows**: each class file lists its roles (§2) and its manifest rows (§6), with the reference
lengths. Rows are named `<state>_<direction>` (`walk_side`, `walk_down`, `run_side`, `attack_side`,
`skill_<name>_side` ...), stills by their file stem (`master`, `view_front`, `pose_skill_<name>`, `icon`),
effects `fx_<name>`; mark a row the class has but the game does not need yet as `⏭` (e.g. `thorn_*`).

Skills follow three parts, as in the reference game: the **pose** (the skill's peak, one still, the end the
clip moves to), the **body clip** (video-sprite: the body ONLY, never a painted effect) and the **effect
layers** (`fx_<name>`: a recipe of small flat layers, `scripts/fx_layers.py`, no video model: smear, ground
ring, burst, bolt, pillar, particles, and tweened keyframe stills). A keyframe still is ONE flat element (a
cloud alone, a banner alone, a crystal alone; `templates.md` "fx part"), never a finished picture of the
whole effect: a cloud drawn with its lightning cannot be animated. A basic attack has no pose by default; its
smear is a `slash` layer. Respawn and raise are the body sinking into the ground played in reverse, plus a pillar
and ring recipe.

**Manifest table** (in `brief.md`, heading exactly `## Asset manifest`; one row per asset; the tool reads
the status column):
```
## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v03 | chốt 2026-10-18 |
| icon | fal-image | ảnh tĩnh | ❌ | |
| pose_skill_gale | fal-image | ảnh tĩnh | ❌ | đỉnh chiêu lốc xoáy |
| run_side | video-sprite | loop | ❌ | |
| attack_side | video-sprite | one-shot | ❌ | |
| death_side | video-sprite | one-shot | ❌ | |
| respawn_side | video-sprite | one-shot | ❌ | |
| levelup_side | video-sprite | one-shot | ❌ | |
| skill_gale_side | video-sprite | one-shot | ❌ | |
| fx_gale | fx-layers | hiệu ứng | ❌ | lốc xoáy: công thức lớp (scripts/fx_layers.py) |
```
Status: `✅ vNN` / `✅ tNN` done and approved; `⏳` made, waiting for the user's approval; `❌` not made yet;
`⏭` later or skipped (say why in Ghi chú). Update the row the moment its state changes, in the same commit
as the still or the clip. Under the table, one line of estimated cost: stills x ~USD 0.014 + clips x ~USD 0.08.

## 9. Extension patterns (from the reference game; add their rows to the manifest when asked)
| Pattern | Rows to add | Example request |
|---|---|---|
| Variant to avoid repetition | `attack2_side` (and `idle2`) | "thêm đòn đánh thứ 2" |
| Two-phase death (bosses) | `death_end_side` (lying, or fading out) | "boss chết 2 pha" |
| Transformation | a second `master_<form>` F and its own rows (idle, run or walk, attack ...), plus `to_<form>_side` and `to_<base>_side` V | "biến thành gấu" |
| Walk and fly | the walking set, the `fly_*` set, and `take_off_<dir>` + `land_<dir>` V for each of the 3 directions | "đi bộ rồi bay lên" |
| Speed variant | `walk_<dir>_fast` V | "chạy nhanh khi tăng tốc" |
| Aimed shot in 3 directions | `shoot_side`, `shoot_up`, `shoot_down` V (+ `view_front`/`view_back` F for a hero) | "bắn lên xuống" |
A new direction, state or skill is a new row: the size, style and pivot never change for it.
