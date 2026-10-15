# Game asset templates (2D fantasy tower defense)

Still images only: this skill draws stills (characters, their standard views, towers, props, icons, UI,
maps). Character and enemy animation is made by the `video-sprite` skill from approved stills; never draw
a multi-frame motion sheet here. Fill the `{placeholders}` from the user's request (use the defaults when
they give nothing), then append the **style guide** wherever `{STYLE}` appears. Keep every technical
requirement (camera, facing, cells, baseline, transparency) exactly as written.
Never name a commercial game or studio in a prompt.

## Style guide (`{STYLE}`)

Use the style block in `format.md` section 1 (or `style.md` at the project root if it exists)
so every asset matches the enemy sprites. Raw sizes here are model sizes; characters of a defined class
use their class file (`classes/<class>.md`) instead.

Shared endings:
- `{CLEAN}` = Isolated on a fully transparent background: no ground, no cast-shadow plate, no scenery, no text, no border.
- `{SHEET}` = Transparent background, no grid lines, no frame numbers, no labels, no text.

## Quick table

| id | Asset | Size | Flags | `--name` example |
|---|---|---|---|---|
| unit | Friendly soldier | 1024x1024 | --transparent | footman |
| hero | Hero | 1024x1024 | --transparent | hero_ranger |
| enemy | Regular enemy | 1024x1024 | --transparent | goblin |
| boss | Boss | 1024x1024 | --transparent | boss_ogre |
| turn | 5-view turnaround (review sheet) | 2048x1024 | --transparent | dwarf_turn |
| tower | Tower, 3 upgrade levels | 1536x1024 | --transparent | tower_archer |
| prop | Map props, 3x2 grid | 1024x1024 | --transparent | props_forest |
| vfx | VFX key frame (one still) | 1024x1024 | --transparent | fx_explosion |
| icon | Ability icon | 1024x1024 | --transparent | icon_fire_arrows |
| ui | UI panel / button | 1024x1024 | --transparent | ui_panel |
| map | Level background | 1536x1024 | (opaque) | map_valley |

## Characters

### unit — Friendly soldier
`{who}` default: a human footman with a round wooden shield, short sword and blue tabard
`{pose}` default: idle battle stance, weight on the back foot

> Single game character sprite: {who}, {pose}. Full body, centered, facing down-right, filling about 70% of the frame. {STYLE} {CLEAN}

### hero — Hero
`{who}` default: an elven ranger heroine with a green hooded cloak and a glowing longbow
`{pose}` default: confident heroic pose, bow lowered

> Single hero character sprite, more detailed and ornate than a regular soldier: {who}, {pose}. Full body, centered, facing down-right, filling about 75% of the frame, a faint rim light to make the hero stand out. {STYLE} {CLEAN}

### enemy — Regular enemy
`{who}` default: a green goblin raider with a rusty dagger and patched leather armor

> Single enemy creature sprite: {who}. Menacing but cute, mid-stride as if marching along a road, full body, centered, facing down-left, filling about 65% of the frame. {STYLE} {CLEAN}

### boss — Boss
`{who}` default: a giant two-headed ogre chieftain with a spiked club and a bone crown

> Single boss enemy sprite: {who}. Huge and heavy, intimidating silhouette, glowing eyes, full body, centered, facing down-left, filling about 85% of the frame. {STYLE} {CLEAN}

## Turnaround (review only)

Make the single-character sprite first and get it approved, then describe that exact design in `{who}`.
For a character of a defined class, generate its standard views one by one (`classes/<class>.md`,
"Standard views"); this sheet only helps compare them side by side and is never animated.

### turn — 5-view turnaround
> Character turnaround sheet of {who}: 5 views in ONE horizontal row of five equal-width cells, left to right: three-quarter front facing down-right, side profile facing right, straight front, three-quarter back facing up-right, straight back. Identical design, colors, proportions and scale in every view, feet on one shared baseline, neutral standing pose. {STYLE} {SHEET}

## Buildings and props

### tower — Tower, 3 upgrade levels
`{kind}` default: an archer tower: wooden lookout platform on a round stone base

> Game asset sheet of {kind} in three upgrade levels, side by side left to right in ONE row of three equal cells. Level 1 small and simple, level 2 taller with more stone and red banners, level 3 grand with gold trim and a faint magical glow. Same camera angle, same footprint size and same base position in every cell so they can swap in place. {STYLE} {SHEET}

### prop — Map props
`{what}` default: a set of 6 props: two pine trees, a boulder, a wooden fence piece, a haystack, a broken cart

> Game prop sheet: {what}. Arranged in a neat 3x2 grid with generous spacing, each prop separate and complete, consistent scale as if placed on the same battlefield. {STYLE} {SHEET}

## Effects and UI

### vfx — Effect key frame (one still)
`{fx}` default: a fiery cannonball explosion at its peak, with smoke and sparks

> Single VFX sprite of {fx}, centered, stylized cartoon effect, bold shapes, limited palette. {CLEAN}

### icon — Ability icon
`{skill}` default: rain of fire arrows

> Round ability icon for a game HUD showing {skill}. A circular badge with an ornate gold rim, the symbol large and centered, readable at 64 pixels, strong contrast. {STYLE} Transparent outside the circle, no text.

### ui — UI panel / button
`{item}` default: an empty rectangular wooden panel with carved stone corners and iron rivets, for a level-select popup

> Game UI element: {item}. Front-facing, flat orthographic view, symmetrical, empty center area for text added later, clean edges suitable for 9-slice scaling. {STYLE} Transparent background, no text, no icons.

## Backgrounds

### map — Level background (opaque, no --transparent)
`{scene}` default: a grassy valley with a winding dirt road, pine forest edges and a river crossed by a wooden bridge
`{pads}` default: 6

> Tower defense level background, seen from a slightly overhead 3/4 view: {scene}. The road enters from the left edge and exits at the right edge. {pads} empty round stone build pads placed beside the road at strategic bends. No characters, no towers, no UI, no text. {STYLE}

## Review checklist (use when critiquing)
- Subject and gear match the description; silhouette readable at small size.
- Camera is slightly overhead 3/4; facing direction is as requested.
- Transparent assets: no painted background, ground plate or scenery
  (transparent pixels may show as black, white or a checkerboard; that is fine).
- Sheets (turnaround, towers, props): correct cell count, equal spacing, same scale in every cell, shared baseline.
- Style matches the style guide and earlier approved assets.
