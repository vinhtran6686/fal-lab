# Class: Enemy (flying)

Everything a flying enemy needs, in one file. Shared rules are in `../format.md`, cited by section. Kind tag
and `{kind}`: `enemy`. Folder: `out/enemies/{id}/`. video-sprite `make_master.py --class flying` (hover idle,
no feet gate). Flag `--enemy-flying`.

## 1. Role in the game
Flies over the path: the same route as walking enemies, but out of reach of ground traps; usually no melee
attack (it passes over the soldiers), sometimes shoots. **Three fly sheets** (side, down, up) and an
**animated idle** (it hovers; the only class whose idle is not a still).

## 2. Roles (ask when missing)
| Role | Adds |
|---|---|
| `flying` (default) | nothing more |
| `ranged` | `shoot_side` and a `projectile` still |

## 3. Size (`../format.md` §7, profile `unit` one tier up: the body floats about a third of the canvas above the ground line)
| Tier | `{H}` @1x | Canvas @1x | Typical |
|---|---|---|---|
| S | 40 | 136x120 | bat, imp, small gargoyle |
| **M (default)** | 60 | 192x168 | gargoyle, witch on a broom, wyvern |

## 4. Directions and master
**3 directions: side, down, up** (left = mirror; no diagonals). Master = side view (`../format.md` §3)
**hovering**: wings spread level, the near wing in front, no feet on the ground (`{body}` flyer wording).
Front and back hover too.
The master is upright and calm (`../format.md` §3 `{UPRIGHT}` flyer variant): the body vertical, hovering level, the weapon at rest; never a diagonal stride toward a corner.

## 5. Stills (fal-image), in order
1. `master` (side, hovering)
2. `view_front`, `view_back` (hovering, `--ref` the master)
3. `icon` (`{rim}` muted stone-grey, `{badge}` muted khaki)
4. `projectile` (ranged)

## 6. Asset manifest rows (`../format.md` §8 table format)
| Asset | Từ | Loại | Role | Reference (30 fps) |
|---|---|---|---|---|
| master | fal-image | ảnh tĩnh | all | - |
| view_front | fal-image | ảnh tĩnh | all | - |
| view_back | fal-image | ảnh tĩnh | all | - |
| icon | fal-image | ảnh tĩnh | all | - |
| projectile | fal-image | ảnh tĩnh | ranged | - |
| projectile_fly, projectile_hit | fx-layers | hiệu ứng | ranged | flying 2-4 drawings (the still turned or flickered, a `sprite` layer), hit 4-8 drawings (`burst`); reference `bolt_*_flying` / `bolt_*_hit` |
| idle_fly | video-sprite | loop | all | animated hover (the reference flyers' idle moves) |
| fly_side | video-sprite | loop | all | ~14 frames, 0.45 s |
| fly_down | video-sprite | loop | all | same length as side |
| fly_up | video-sprite | loop | all | same length as side |
| shoot_side | video-sprite | one-shot | ranged | ~24 frames, 0.8 s |
| death_side | video-sprite | one-shot | all | ~12 frames, 0.4 s: falls to the ground |
No attack, no thorn (vines do not reach it). Optional (`../format.md` §9): walk and fly (take-off and landing
per direction), a speed variant `fly_<dir>_fast`.
Cost: 4 stills (~USD 0.06) + 5 clips (~USD 0.40) + retakes.

## 7. Skills
Rare; made like a hero skill when the user asks.

## 8. Slots (`brief.md`)
| Slot | Meaning |
|---|---|
| `{id}` | short snake_case id |
| `{design}` | one dense sentence (`../format.md` §1), enemy palette (muted main colour + one warning accent); wings and the hovering body described; width-to-height ratio instead of a head count |
| `{body}` | `flyer` |
| `{death}` | how it falls out of the air |
| `{projectile}` | ranged only |

## 9. Review points (in addition to `../format.md` §6)
- Hovering in every view, the same height above the ground line; no feet planted, no shadow drawn.
- Wings the same shape and colour in every view; the near wing in front on the master.
