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
- The master is the hero in its idle stance, three-quarter front facing down-right (format.md §3).
- When an action needs a different hold or stance (`{poses}`), make a `pose_<action>` still from the master
  (`--ref M`, same view as the sheet). video-sprite starts that action from it.

## Frame size
**Pending** (format.md §4): heroes will get a frame with room for skills and casts above and around the
body. Until it is set, the two existing heroes use the enemy Level 1 values (256 x 128 at 1x, body 69 px,
pivot y 0.88); a new hero uses them too and is marked interim in `brief.md`.

## What a hero needs
| Category | Sheet | From still | Loop | Status |
|---|---|---|---|---|
| idle | `idle_down_side` (+ mirror) | `master` (idle stance) | yes | tested (centaur) |
| move | `run_down_side` or `walk_down_side` (+ mirror) | `master` or `pose_run` | yes | tested (centaur) |
| attack | `attack_down_side` (+ mirror), hit frame exported | `master` or `pose_attack` | no | tested (centaur) |
| death | `death_down_side` (+ mirror), holds the last frame | `master` or `pose_death` | no | tested (centaur) |
| move | `*_side`, `*_up_side`, `*_down`, `*_up` | the other standard views | yes | *to confirm*: whether heroes need all 8 directions |
| attack | `cast_down_side` per skill | `master` or `pose_cast` | no | *to confirm* |
| ui | `icon` | `icon` still | - | *to confirm* (none made yet) |
Centaur's sheets face down-side only (the 3/4 master), not the enemy's side profile.

## Hero-specific review points (in addition to format.md §6)
- Reads as a hero next to the enemies: brighter main colour, one bright accent, a clear role silhouette.
- Every `pose_*` still is the same character as the master (gear, colours, proportions); only the stance changes.
- No "heroic" extras the style forbids: no rim light, no aura, no ornate trim.
