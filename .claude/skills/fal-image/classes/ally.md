# Class: Ally (friendly soldier)

Everything an ally needs, in one file. Shared rules are in `../format.md`, cited by section. Kind tag and
`{kind}`: `ally` (prompts: "friendly soldier"). Folder: `out/allies/{id}/`. video-sprite `--class mob`.

## 1. Role in the game
The player's unnamed units: soldiers from a barracks tower, archers, units summoned by a hero. They run a
short way to block the road and fight there; no skills except elite units. **One movement sheet** (run),
side only.

## 2. Roles (ask when missing)
| Role | Adds |
|---|---|
| `melee` (default) | `attack_side` |
| `ranged` | `shoot_side` and a `projectile` still |
| `summoned` | `raise_side` (rises from the ground when summoned) |

## 3. Size (`../format.md` §7, profile `unit`: canvas 2.25 x 2.0 `{H}`, feet at y 0.88)
| Tier | `{H}` @1x | Canvas @1x | Typical |
|---|---|---|---|
| **S (default)** | 40 | 92x80 | footman, archer, militia |
| M | 60 | 136x120 | knight, paladin, elite |
| L | 84 | 192x168 | tamed beast, golem summon |

## 4. Directions and master
**1 direction: side** (left = mirror). Master = side view (`../format.md` §3), neutral ready pose. No front or
back view. Idle is the master still.
The master is upright and calm (`../format.md` §3 `{UPRIGHT}`): the body vertical, the feet on one horizontal ground line, the weapon at rest; never a diagonal stride toward a corner.

## 5. Stills (fal-image), in order
1. `master` (side)
2. `icon` (`{rim}` plain gold-yellow, `{badge}` the unit's main colour, lighter)
3. `projectile` (ranged)
4. elite units only: `pose_skill_<name>` + `fx_<name>` per special

## 6. Asset manifest rows (`../format.md` §8 table format)
| Asset | Từ | Loại | Role | Reference (30 fps) |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | all | 8/8: idle is 1 frame |
| icon | fal-image | ảnh tĩnh | all | - |
| projectile | fal-image | ảnh tĩnh | ranged | - |
| run_side | video-sprite | loop | all | 8/8, ~8 frames, 0.27 s |
| attack_side | video-sprite | one-shot | melee | 8/8, ~20 frames, 0.67 s |
| shoot_side | video-sprite | one-shot | ranged | 3/8, ~16 frames, 0.53 s |
| death_side | video-sprite | one-shot | all | 8/8, ~15 frames, 0.5 s |
| pose_respawn | fal-image | ảnh tĩnh | summoned | kneeling start pose |
| raise_side | video-sprite | one-shot | summoned | 3/8, ~20 frames, 0.67 s (rise from `pose_respawn`) |
Optional: `attack2_side` (2/8), 1-2 specials for an elite unit (heal, holy strike: ~30 frames, 1 s).
Cost, melee ally: 2 stills (~USD 0.03) + 3 clips (~USD 0.24) + retakes.

## 7. Skills
None by default. Elite units: 1-2 specials, made like a hero skill (pose + body clip + vfx when big).

## 8. Slots (`brief.md`)
| Slot | Meaning |
|---|---|
| `{id}` | short snake_case id |
| `{design}` | one dense sentence (`../format.md` §1); palette like heroes: **saturated main colour + one bright accent**, often the faction colour shared by all allies |
| `{body}` | biped / quadruped / blob / flyer |
| `{attack}` | the attack motion, inside the canvas |
| `{death}` | how it falls |
| `{projectile}` | ranged only |

## 9. Review points (in addition to `../format.md` §6)
- Reads as friendly next to the enemies: hero palette, the faction colour.
- Simpler than a hero of the same tier: fewer parts, no signature effect.
