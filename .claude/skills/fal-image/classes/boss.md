# Class: Boss

Everything a boss needs, in one file. Shared rules are in `../format.md`, cited by section. Kind tag and
`{kind}`: `boss`. Folder: `out/bosses/{id}/`. video-sprite `make_master.py --class boss`.

## 1. Role in the game
The end of a level or a big wave: walks the path like an enemy, much bigger and slower, with 0-3 special
moves and a longer death. **Three walk sheets** (side, down, up; a few references only have side), every
other state side only.

## 2. Roles (ask when missing)
| Role | Adds |
|---|---|
| `melee` (default) | `attack_side` |
| `ranged` | `shoot_side` and a `projectile` still |

## 3. Size (`../format.md` §7, profile `boss`: canvas 2.55 x 1.7 `{H}`: wide and low, feet at y 0.88)
| Tier | `{H}` @1x | Canvas @1x | Typical |
|---|---|---|---|
| XL | 120 | 308x204 | mini-boss, giant, warlord |
| **XXL (default)** | 170 | 436x292 | final boss, demon lord, dragon on foot |

## 4. Directions and master
**3 directions: side, down, up** (left = mirror; no diagonals). Master = side view (`../format.md` §3),
neutral ready pose; front and back redrawn from it. Idle is the master still.
The master is upright and calm (`../format.md` §3 `{UPRIGHT}`): the body vertical, the feet on one horizontal ground line, the weapon at rest; never a diagonal stride toward a corner.

## 5. Stills (fal-image), in order
1. `master` (side)
2. `view_front`, `view_back` (`--ref` the master)
3. `icon` (`{rim}` dark iron with one warning-colour band, `{badge}` muted dark red)
4. `projectile` (ranged)
5. per special: `pose_skill_<name>`; its effect is an `fx_<name>` recipe (`scripts/fx_layers.py`) with fx part stills only for shaped elements

## 6. Asset manifest rows (`../format.md` §8 table format)
| Asset | Từ | Loại | Role | Reference (30 fps, 16 bosses) |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | all | 13/16: idle is 1 frame |
| view_front | fal-image | ảnh tĩnh | all | - |
| view_back | fal-image | ảnh tĩnh | all | - |
| icon | fal-image | ảnh tĩnh | all | - |
| projectile | fal-image | ảnh tĩnh | ranged | - |
| walk_side | video-sprite | loop | all | 12/16, ~24 frames, 0.8 s |
| walk_down | video-sprite | loop | all | 10/16 |
| walk_up | video-sprite | loop | all | 9/16 |
| attack_side | video-sprite | one-shot | melee | 12/16, ~32 frames, 1.05 s |
| shoot_side | video-sprite | one-shot | ranged | 2/16, ~40 frames, 1.3 s |
| death_side | video-sprite | one-shot | all | 11/16, ~35 frames, 1.2 s (up to 5 s) |
| pose_skill_`<name>` | fal-image | ảnh tĩnh | per special | - |
| skill_`<name>`_side | video-sprite | one-shot | per special | 30-48 frames, 1-1.6 s |
| fx_`<name>` | fx-layers | hiệu ứng | per special | separate small objects in the reference |
Optional (`../format.md` §9): `death_end_side` (two-phase death: lying, or fading out), a transformation
(a second form with its own rows). Cost, melee boss with 1 special: 5 stills (master, front, back, icon, pose) + 1 vfx (~USD 0.08) + 6 clips
(~USD 0.48) + retakes.

## 7. Skills
**0-3 specials** (references: most have 1, a few 2, one 5). Asked with the tier (`multiSelect`). Kinds seen:
smash, breath, freeze, heal, spores, eat, summon, cast, transformation. Each: pose + body clip + vfx when big.

## 8. Slots (`brief.md`)
| Slot | Meaning |
|---|---|
| `{id}` | short snake_case id |
| `{design}` | one dense sentence (`../format.md` §1), enemy palette (muted main colour + one warning accent), a few more big shapes than an enemy is allowed at this size |
| `{body}` | biped / quadruped / blob / flyer |
| `{attack}` | the attack motion; heavy and slow, inside the wide canvas |
| `{death}` | how it falls (long: ~1.2 s) |
| `{skills}` | per special: `<name>: <the body's move>; <the effect>` |

## 9. Review points (in addition to `../format.md` §6)
- Reads as the biggest threat on the screen: a heavy silhouette, enemy palette.
- Every `pose_*` still is the same character as the master; only the stance changes.
