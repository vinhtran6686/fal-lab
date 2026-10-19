# Class: Enemy (walking)

Everything a walking enemy needs, in one file. Shared rules are in `../format.md`, cited by section. Kind tag
and `{kind}`: `enemy`. Folder: `out/enemies/{id}/`. video-sprite `--class mob`. Flying enemies:
`enemy-flying.md`; bosses: `boss.md`.

## 1. Role in the game
The waves: walk the path from the entrance to the exit, fight the soldiers that block them, die to towers.
The path runs right, left, up and down the screen, so it has **three walk sheets** (side, down, up); every
other state is side only and flipped to face its target.

## 2. Roles (ask when missing)
| Role | Adds |
|---|---|
| `melee` (default) | `attack_side` |
| `ranged` | `shoot_side` and a `projectile` still |
| `summoned` | `raise_side` (rises from the ground when a caster summons it) |

## 3. Size (`../format.md` §7, profile `unit`: canvas 2.25 x 2.0 `{H}`, feet at y 0.88)
| Tier | `{H}` @1x | Canvas @1x | Typical | Flag |
|---|---|---|---|---|
| XS | 24 | 56x48 | spiderling, rat, imp | `--enemy-small` |
| **S (default)** | 40 | 92x80 | goblin, bandit, skeleton | `--enemy` |
| M | 60 | 136x120 | werewolf, dark knight, raider | `--enemy` |
| L | 84 | 192x168 | ogre, yeti, troll brute | `--enemy-large` |

## 4. Directions and master
**3 directions: side, down, up** (left = mirror; no diagonals; the game picks by quadrant with 10° of
stickiness, `../format.md` §8). Master = side view (`../format.md` §3), neutral ready pose; front and back are
redrawn from it and must still look right when the enemy walks up to 45° off vertical. Idle is the master.
The master is upright and calm (`../format.md` §3 `{UPRIGHT}`): the body vertical, the feet on one horizontal ground line, the weapon at rest; never a diagonal stride toward a corner.

## 5. Stills (fal-image), in order
1. `master` (side)
2. `view_front`, `view_back` (`--ref` the master)
3. `icon` (`{rim}` muted stone-grey, `{badge}` muted khaki)
4. `projectile` (ranged)

## 6. Asset manifest rows (`../format.md` §8 table format)
| Asset | Từ | Loại | Role | Reference (30 fps, 68 enemies) |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | all | 65/68: idle is 1 frame |
| view_front | fal-image | ảnh tĩnh | all | - |
| view_back | fal-image | ảnh tĩnh | all | - |
| icon | fal-image | ảnh tĩnh | all | - |
| projectile | fal-image | ảnh tĩnh | ranged | - |
| projectile_fly, projectile_hit | fx-layers | hiệu ứng | ranged | flying 2-4 drawings (the still turned or flickered, a `sprite` layer), hit 4-8 drawings (`burst`); reference `bolt_*_flying` / `bolt_*_hit` |
| walk_side | video-sprite | loop | all | 63/68, ~22 frames, 0.7 s |
| walk_down | video-sprite | loop | all | 62/68, same length as side |
| walk_up | video-sprite | loop | all | 63/68, same length as side |
| attack_side | video-sprite | one-shot | melee | 56/68, ~19 frames, 0.65 s |
| shoot_side | video-sprite | one-shot | ranged | 8/68, ~24 frames, 0.8 s |
| death_side | video-sprite | one-shot | all | 63/68, ~16 frames, 0.55 s |
| raise_side | video-sprite | one-shot | summoned | 15/68, ~34 frames, 1.1 s (despawn clip played in reverse) |
| thorn_side, thorn_free_side | video-sprite | loop + one-shot | all | 43/68 (bound by a tower's vines); **⏭ later**, until the game has such a tower |
No reference enemy has a hurt state. Cost, melee enemy: 4 stills (~USD 0.06) + 5 clips (~USD 0.40) + retakes.

## 7. Skills
Rare (22 of 41 reference enemies have none; most others one: shoot, summon, heal or a special). A special is
made like a hero skill (pose + body clip + vfx when big), only when the user asks.

## 8. Slots (`brief.md`)
| Slot | Meaning |
|---|---|
| `{id}` | short snake_case id |
| `{design}` | one dense sentence (`../format.md` §1): body and what it exaggerates, gear, the weapon and the hand that holds it, palette **slightly darker, muted main colour + one warning accent**, effects as flat layers |
| `{body}` | biped / quadruped / blob / flyer (`../format.md` §3 view wording) |
| `{attack}` | the attack motion; an in-place strike, not a lunge across the canvas |
| `{death}` | how it dies |
| `{projectile}` | ranged only |

## 9. Review points (in addition to `../format.md` §6)
- The weapon (or a blob's asymmetric mark) is on the same side, same shape and size, in every view.
- Master faces right turned toward the viewer, front shows the face, back hides it.
- Every view stands in the same neutral pose, so the walk clips start alike.
- Reads as an enemy next to the heroes: muted main colour, one warning accent.
