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

## 3. Standard views of a character (the "forms" video-sprite animates)
A top-down game moves in 8 directions; 5 views are generated, the 3 left-facing ones are mirrors.
| Still (`design/`) | View | Animated by video-sprite as | Required |
|---|---|---|---|
| `master_vNN` | three-quarter FRONT, facing down-right (the design reference) | `*_down_side` (+ mirror down-left) | yes |
| `view_side_vNN` | true side profile, facing right | `*_side` (+ mirror left) | yes |
| `view_front_vNN` | straight front, facing the viewer | `walk_down` | yes |
| `view_back_vNN` | straight back, facing away | `walk_up` | yes |
| `view_up_side_vNN` | three-quarter BACK, facing up-right | `walk_up_side` (+ mirror up-left) | yes |
| `icon_vNN` | portrait badge | `ui/icon` (packed with `sprite_pack.py`) | yes |
| `pose_<action>_vNN` | the character in the start pose of one action (ready, run, attack, death ...), same view as the sheet it starts | optional start still when the neutral pose reads wrong for that action | optional |
| `turnaround_vNN` | the 5 views side by side (`templates.md` "turn") | review only, never animated | optional |
Which views and sheets a character needs is set by its class file. Make and approve them in this order:
master, then side, front, back, up_side (each with `--ref <master>`), then the icon.

### View prompts (every class)
`{kind}` is the class word ("enemy", "hero", "friendly soldier"). Every view prompt is:
`Use the reference image only for the character design; redraw it in the style described. Single game
{kind} sprite: {design}. <VIEW> Neutral standing pose, full body, centered, filling about 70% of the frame.
{BG} {STYLE}`. The master has no `--ref` and starts directly with "Single game {kind} sprite: {design}.".
`<VIEW>` comes from the table of the character's `{body}`. The model pulls every view back toward the 3/4
master: name the angle in capitals, say what must and must not be visible (eyes, face, which side the
weapon or the asymmetric mark is on), and end with "Not a three-quarter view". A `pose_<action>` still uses
the same skeleton with its view, the pose instead of "Neutral standing pose", and `--ref <master>`.

**biped** (two legs; tested on bandit 2026-10-13/14 and centaur's upper body 2026-10-16). `{weapon hand}` is
the hand that holds the weapon (or the staff, the book ...).
| Still | `<VIEW>` |
|---|---|
| `master` | Three-quarter view facing down-right, as if walking toward the bottom-right of the screen. Neutral ready pose. |
| `view_side` | FLAT SIDE PROFILE like a paper cutout, facing exactly right: chest and belly pointing to the right edge, the back of the head pointing left, only one eye visible, the weapon held out in front to the right, legs one in front of the other along the ground. Not a three-quarter view. |
| `view_front` | Straight FRONT view, perfectly facing the viewer, mirror-symmetric body: both eyes visible, both shoulders the same size, feet side by side, the weapon held upright in its {weapon hand} (on the left side of the image for a right hand). Not a three-quarter view. |
| `view_back` | Straight BACK view, seen from directly behind, walking away from the viewer: the back of the head, NO face and NO eyes visible, mirror-symmetric body, feet side by side with the heels toward the viewer, the weapon held upright in its {weapon hand} (on the RIGHT side of the image for a right hand). Not a three-quarter view, not a front view. |
| `view_up_side` | Three-quarter BACK view, turned 45 degrees to face the TOP-RIGHT of the screen, walking away from the viewer toward the upper right: the back and the left side visible, only the edge of one ear, NO eyes and no face visible, the weapon held upright in its {weapon hand}. Not a side profile, not a front view. |
| `pose_ready_side` (example of `pose_<action>`) | FLAT SIDE PROFILE facing exactly right in a combat-ready stance: knees bent, weight forward, the weapon raised and ready to strike. Not a three-quarter view. |

**quadruped** (four legs, incl. centaurs and beasts; *untested as a full set*): as biped, with these changes.
- `view_side`: the whole body long and flat across the frame, head and chest to the right, tail to the left, all four legs visible as two pairs, one eye visible.
- `view_front` / `view_back`: the body foreshortened to a short block, front legs side by side (front) or hindquarters and tail (back); the long body is hidden behind the head or the rump.
- `view_up_side`: rump and tail toward the viewer, the back and the left flank visible, the head turned away.

**blob** (no legs: slimes, oozes; *untested*): no `{weapon hand}`, no feet; "standing" becomes "resting on
a wide flat base on the ground". `{design}` must name one asymmetric mark and its side ("a drip on its RIGHT
side"): that mark tells the views apart. Front: eyes and mouth visible, the mark on the image left. Back:
no face, only a highlight arc, the mark on the image right. Side: one eye, the body bulging to the right.
up_side: the back and right flank, face hidden, mark visible. The top-left highlight never moves with the body.
Blob and flyer have no head count: `{design}` gives a width-to-height ratio instead of "2.5 to 4 heads tall"
("about 1.3 times as wide as it is tall").

**flyer** (wings, floats; *untested*): no feet on the ground; "standing" becomes "hovering in place, wings
spread level". Side: wings seen edge-on, one above the other; front/back: wings spread symmetrically, face
visible / hidden. The body is drawn with no shadow below; video-sprite uses its `flying` profile.

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
python scripts/gen_image.py "<view prompt>"   --size 1024x1024 --png --ref M --name view_side --versioned --out A/design
# ... view_front, view_back, view_up_side, pose_*, icon (and projectile) the same way; independent stills run in parallel
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
  design/                                 the ORIGINAL DESIGN (this skill), every version: master_v03.png, view_side_v01.png, pose_run_v01.png ... (+ .json)
  raw/                                    SOURCE videos (video-sprite), every take, saved as soon as the model returns
    run_down_side_run_t02.mp4 (+ .json)   <action>_<set>_tNN: the .json holds model, prompt, cost, request id
  idle/ move/ attack/ death/ ...          STATE folders (category, scripts/asset_layout.py): ONE final version each
    move/run_down_side/                   one folder per sheet
      preview.gif                         look here first
      sheet.png                           horizontal sheet @2x
      frames/@2x/hero_centaur_run_down_side_01.png ...   frames for the game (also @1x)
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
| Canvas | **one canvas for every action of an asset** (`meta.json` "cell"), from the size matrix (§7) by class and tier. No action gets a bigger or smaller frame, so the engine never rescales one action against another |
| Body | **one body height for every action**: `2 x {H}` at @2x (video-sprite `--target-height`), recorded as `meta.json` "body_height_2x"; a sheet whose body differs by more than 4% is rescaled on export |
| Pivot | feet, x 0.5, y 0.88 of the canvas (`meta.json` "pivot"; fixed in `video_to_sheet.py`); icons are centered |
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
- The view is exact (§3 table of its `{body}`): side = true profile facing right (one eye); front =
  mirror-symmetric, face visible; back = no face; 3/4 front faces down-right; 3/4 back faces up-right, face hidden.
- Neutral pose (or the requested `pose_*`), full body and weapon inside the frame with margin, nothing touching the edges.
- Style (§1): simple big shapes and a clear silhouette at `{H}` px; no fine detail on face, hands or clothes;
  stylized proportions as `{design}` says; flat fills with 2-3 hard tones per colour, no gradient or blur;
  thick outlines in a dark shade (or the hue set in the brief); effects as flat layered shapes, not glow.
  A new master also matches a style anchor (§1) side by side.
- Flat magenta background only; no magenta or pink on the subject, no ground, shadow or text.
- Class-specific points in the class file.

## 7. Size: class x tier matrix (fixed; measured 2026-10-17)
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
| `unit` | 2.25 x 2.0 | allies, enemies | references: reach from the feet (85th percentile) up 1.56H, sideways 1.12H, below 0.24H (deaths fall toward the viewer) |
| `hero` | 2.6 x 2.3 | heroes | up 2.0H (level-up, respawn, casts above the head), sideways 1.29H |
| `boss` | 2.55 x 1.7 | bosses | up 1.48H, sideways 1.27H: wide, low frames |
Back-test on 107 reference characters (heroes, allies, enemies, bosses; flyers excluded): 78 (73%) fit their
profile canvas; the rest are wide death falls and skill moves, which our prompts keep inside the frame.

**Matrix** (canvas at 1x, rounded to 4 px; @2x doubles it; default tier marked *):
| Class | Example flag | Folder, kind | Profile | Sheets | Tiers -> canvas @1x |
|---|---|---|---|---|---|
| hero | `--hero` | `out/heroes/`, `hero` | hero | `classes/hero.md` | S 104x92, **M* 156x136**, L 220x192 |
| ally (friendly soldier) | `--ally` | `out/allies/`, `ally` | unit | `classes/enemy.md` list (5 walks, attack, death), icon rim gold | **S* 88x80**, M 136x120, L 188x168 |
| enemy, small | `--enemy-small` | `out/enemies/`, `enemy` | unit | `classes/enemy.md` | **XS* 56x48** |
| enemy | `--enemy` | `out/enemies/`, `enemy` | unit | `classes/enemy.md` | **S* 88x80**, M 136x120 |
| enemy, large | `--enemy-large` | `out/enemies/`, `enemy` | unit | `classes/enemy.md` | **L* 188x168** |
| boss | `--boss` | `out/bosses/`, `boss` | boss | `classes/enemy.md` list + one sheet per special move | XL 304x204, **XXL* 432x288** |
When asking, enemies are one class with tiers XS, S, M, L; bosses XL, XXL.

Rules that come with the matrix:
- Pass the canvas to video-sprite as `--cell <W>x<H>` (1x) and `--target-height <2 x {H}>`; record class,
  tier, `{H}` and canvas in `brief.md`.
- `{attack}`, `{death}` and casts are written to stay inside the canvas (strike forward or upward, fall
  in place); the exporter refuses a frame that does not fit and never shrinks it.
- **Big skill effects are separate assets**, as in the references: a rain of fire, a lightning chain or a
  summoned storm is a vfx asset (`templates.md` vfx, `out/vfx/<id>/`) placed over the scene by the game. Only
  the body and effects touching it (a glowing fist, flames on the weapon) stay in the character's frame.
- Flyers (*to confirm*): the references float their body well above the canvas bottom (feet line about
  0.55-0.65); until a flyer is made, use the `unit` canvas one tier up and note it in `brief.md`.
- `{H}` replaces "64" in `{STYLE}` (§1).
