# Class: Hero

Inherits everything in `../format.md` (style, generation rules, view prompts, commands, folders, checklist).
Kind tag for files and `{kind}`: `hero`. Folder: `out/heroes/{id}/`.
Heroes are the player's named characters: one each, controlled on the map, with idle, move, attack, death
and later skills. Built from the two heroes made so far (`centaur`, `inferno_monk`, 2026-10-16); rows
marked *to confirm* have no tested asset yet.

## Content slots (flexible, filled from the user's request)
| Slot | Meaning | Example |
|---|---|---|
| `{id}` | short snake_case id | `centaur`, `inferno_monk` |
| `{design}` | one dense sentence that locks the look, as for enemies; palette (format.md §1): saturated main colour and one bright accent. Reused verbatim in every prompt | centaur: `a heavy-metal centaur warrior: the upper body of a broad-shouldered man rising from ... the outlines are dark purple ...` |
| `{body}` | biped / quadruped / blob / flyer (format.md §3) | centaur `quadruped`, inferno_monk `biped` |
| `{idle}` | the idle stance, if it is not the neutral pose (the master is then drawn in it) | inferno_monk: `stands on ONE leg like an old tree, ... both hands pressed lightly together in front of the chest` |
| `{idle_motion}` | the looping micro-motion of idle, for video-sprite | inferno_monk: `chest rising and falling with the breath, ... the standing leg and the balance pose never change` |
| `{poses}` | how the weapon is held per action (idle / walk / run / attack), when it changes | centaur: `idle: the scythe planted upright ...; run: scythe held diagonally across the body with both hands` |
| `{attack}` | the attack motion; stays inside the frame (strike forward or upward, not a wide sweep across the canvas) | centaur: `a two-handed horizontal scythe sweep from behind to the front ...` |
| `{death}` | how the hero falls | centaur: `the horse buckles on its front legs and topples onto its side ...` |
| `{skills}` | *to confirm*: each skill's cast motion and its effect, drawn as flat layered shapes inside the frame | - |
Icon: `{rim}` = bright gold-yellow, `{badge}` = the hero's main colour, lighter.
Record in `brief.md`: the approved master and every approved `pose_*` still (centaur: idle `master_v03`, run
`pose_run_v01`, attack `pose_attack_v01`, death `pose_death_v04`), and any per-hero style choice (centaur:
purple outlines, format.md §1).

## Master and poses
- The master is the hero in its idle stance, in the side view (facing right, turned ~30° toward the camera;
  format.md §3). Heroes have no front or back view: the references draw every hero action from the side only.
- When an action needs a different hold or stance (`{poses}`), make a `pose_<action>` still from the master
  (`--ref M`, same view as the sheet). video-sprite starts that action from it.

## Frame size
Profile `hero` of the size matrix (`../format.md` §7): tier S 104x92, **M 156x140 (default)**, L 220x196 at
1x, feet at y 0.88. The canvas leaves about 2 x `{H}` above the feet for casts, level-up and respawn; big skill
effects (storms, rains, beams) are separate vfx assets. A small mage is S, most heroes M, a robot or golem L.

## What a hero needs (states measured on 22 reference heroes and 9 allies, 2026-10-17)
Every sheet is side only (+ mirror left). Durations are the reference's (30 fps).
| Category | Sheet | From still | Loop | Reference |
|---|---|---|---|---|
| idle | `idle_side` = the master still, 1 frame (a breathing loop only on request) | `master` | hold | 15/15 heroes, 1 frame |
| move | `run_side` | `master` or `pose_run` | yes | 15/15, ~6 frames, 0.2 s: a short, fast loop |
| attack | `attack_side`, hit frame exported | `master` or `pose_attack` | no | 14/15, ~22 frames, 0.75 s |
| attack | `attack2_side` (a second melee move) or `shoot_side` (ranged) | `master` | no | 4/15 each, ~22-27 frames |
| death | `death_side`, holds the last frame | `master` or `pose_death` | no | 13/15, ~9 frames, 0.3 s: short |
| spawn | `respawn_side` (appears on the map again) | `master` | no | 13/15, ~18 frames, 0.6 s |
| level | `levelup_side` (a short flourish) | `master` | no | 13/15, ~18-23 frames, 0.7 s |
| skill | `skill_<name>_side`, one per skill | `master` or `pose_<skill>` | no | **2-4 skills per hero**, 28-68 frames, 1-2 s |
| ui | `icon` | `icon` still | - | - |
Skills: the body's motion only; a big effect (rain, storm, beam, summon) is a separate vfx asset (format.md §7).
Allies (`out/allies/`, `classes/enemy.md` slots) use this list without respawn, level-up and skills: idle
(still), `run_side` (~8 frames), `attack_side` (~20), `death_side` (~15); a summoned ally adds `spawn_side`,
an elite ally 1-2 specials (heal, holy strike: ~30 frames).

## Hero-specific review points (in addition to format.md §6)
- Reads as a hero next to the enemies: brighter main colour, one bright accent, a clear role silhouette.
- Every `pose_*` still is the same character as the master (gear, colours, proportions); only the stance changes.
- No "heroic" extras the style forbids: no rim light, no aura, no ornate trim.
