# Reference data (measured on the reference game, 2026-10-17/18)

Data, not rules: where the numbers in `format.md` and `classes/*.md` come from, kept so a new class or a
change can be checked against the same source. Sources: the asset atlas of the reference game (112
characters with frames: heroes, allies, enemies, bosses; `data.json` of the user's atlas artifact) and the
user's document read from the game's decompiled code (animation picking, anchors, state meanings). Never
name the game or its characters in a prompt or in the skill files.

## Directions (atlas, animation names)
| Class | Characters | Movement sheets | Other states |
|---|---|---|---|
| hero | 22 | 1: `running`, side | side only |
| ally | 9 | 1: `running`, side | side only |
| enemy | 60 of 68 | 3: `walkingRightLeft`, `walkingDown`, `walkingUp` | side only |
| boss | 7 of 16 | 3 (a few: side only, or side + up) | side only |
Exceptions: one ranged hero aims in 3 directions (`shootAim*`); one flyer has walk and fly sets with take-off
and landing per direction; one flyer has a fast walk variant.

Code (the user's document): the walk sheet is picked by quadrant: 315-45° side, 45-135° up, 135-225° side
flipped, 225-315° down, with 10° of stickiness around the current quadrant. With one movement sheet it is
used for every direction and flipped when moving left. 30 fps, mostly "on twos".

## Body height by group (idle silhouette, px at the game's 1x)
| Group | Range | Examples (kind) |
|---|---|---|
| tiny enemies | 17-30 | spiderling, small wolf, rat |
| regular enemies | 34-46 | bandit, skeleton, orc, troll |
| allies | 28-45 | archer, footman, paladin |
| heroes | 43-77 (most 50-70) | mage 43, archer 44, knight 52, fire elemental 64, saw robot 77 |
| large enemies | 60-95 | ogre 72, yeti 79, forest troll 94 |
| bosses | 110-200 | |
These ranges set the tiers of `format.md` §7 (XS 24, S 40, M 60, L 84, XL 120, XXL 170).

## Frame profiles (reach from the feet, in units of the body height, 85th percentile)
| Class | Up | Sideways | Below | Canvas (W x H) |
|---|---|---|---|---|
| enemy (61) | 1.56 | 1.12 | 0.24 | 2.25 x 2.0 |
| hero (22) | 2.00 | 1.29 | 0.16 | 2.6 x 2.3 |
| boss (15) | 1.48 | 1.27 | 0.17 | 2.55 x 1.7 |
| ally (9) | 1.57 | 1.25 | 0.43 | uses the enemy profile |
Back-test with the feet at 0.88: 78 of 107 characters (73%) fit their profile's canvas (bosses 11/15,
enemies 46/61, heroes 16/22, allies 5/9). Anchors in the game: 0.10-0.25 of the canvas above the bottom,
median 0.18, set per character; this project fixes 0.88 from the top for every asset.

## States (count of characters that have it; median frames at 30 fps)
| State | Hero (15) | Ally (8) | Enemy (68) | Boss (16) |
|---|---|---|---|---|
| idle | 15, 1 frame | 8, 1 | 65, 1 | 13, 1 |
| run / walk | 15, 6 | 8, 8 | 63, 22 (x3 directions) | 12, 24 (x3) |
| attack | 14, 22 | 8, 20 | 56, 19 | 12, 32 |
| attack2 | 4, 27 | 2, 15 | - | - |
| shoot | 4, 22 | 3, 16 | 8, 24 | 2, 40 |
| death | 13, 9 | 8, 15 | 63, 16 | 11, 35 (up to 151) |
| respawn | 13, 18 | - | - | - |
| levelup | 13, 18-23 | - | - | - |
| raise (summoned) | - | 3, 20 | 15, 34 | 1 |
| thorn + thornFree | - | - | 43, 19 + 5 | - |
| hurt | 0 | 0 | 0 | 0 |
Flying enemies (the user's document): fly ~14, death ~12, animated idle.

## Skills per character (states beyond the core set)
- Heroes: 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 7, 9. Kinds: area rain or storm, ground smash or shockwave, summon,
  transformation, buff or support, special weapon strike, teleport. Big effects are separate objects.
- Allies: 0-1 mostly; elite units 2-3 (heal, holy strike, twister); summoned units have raise.
- Bosses: 0, 0, 1 (x7), 2, 2, 5. Kinds: smash, breath, freeze, heal, spores, eat, cast, transformation.
- Enemies: 22 of 41 none, most others 1 (shoot, summon, heal, special).
