# Game asset templates (2D fantasy tower defense)

Still images only: this skill draws stills. **Characters** (enemies, heroes, units, bosses) are not made
here: they use `format.md` and their class file (`classes/<class>.md`), which hold the view prompts and the
frame size. This file covers every other asset. Fill the `{placeholders}` from the user's request (use the
defaults when they give nothing), then append `{BG}` and `{STYLE}` from `format.md` (`style.md` at the
project root replaces `{STYLE}` if it exists). Keep every technical requirement (camera, cells, baseline,
footprint) exactly as written. Never name a commercial game or studio in a prompt.

## Rules shared by every template
- `--png` on a flat magenta background (`{BG}`, `format.md` §2), never `--transparent` (gpt-image-2 has no
  transparency on fal). Opaque maps are the only exception: no `{BG}`.
- `{STYLE}` on every prompt, effects included: simple big shapes, flat fills with 2-3 hard tones, thick dark
  outlines, effects as flat layered shapes. Never ask for "ornate", "intricate", "detailed", "glow",
  "rim light" or "pixel art" (`format.md` §1): complex effects are where the model drifts from the style.
- Same camera as the characters: high top-down, tilted about 60 degrees, light from the top-left.
- Folder: `out/<kind>s/<id>/design/` with `brief.md` and `history.md` (`format.md` §4), e.g.
  `--name tower_archer --versioned --out out/towers/archer/design`.
- Cutting a sheet into single images and keying the magenta: `scripts/sprite_pack.py` (splits a COLSxROWS
  grid by gaps, keys the magenta background, writes frames). Single stills (an ability icon) use the icon
  command in `format.md` §3.

## Quick table
| id | Asset | Size | `--name` example |
|---|---|---|---|
| turn | 3-view turnaround of an enemy (review sheet) | 1536x1024 | goblin_turn |
| tower | Tower, 3 upgrade levels | 1536x1024 | tower_archer |
| prop | Map props, 3x2 grid | 1024x1024 | props_forest |
| vfx | VFX key frame (one still) | 1024x1024 | fx_explosion |
| icon | Ability icon | 1024x1024 | icon_fire_arrows |
| ui | UI panel / button | 1024x1024 | ui_panel |
| map | Level background (opaque) | 1536x1024 | map_valley |

## Turnaround (review only)
Make the character's master and standard views first (`format.md` §3); this sheet only helps compare them
side by side and is never animated. `--ref <approved master>`.

### turn — 3-view turnaround (enemies and bosses)
> Character turnaround sheet of {design}: 3 views in ONE horizontal row of three equal-width cells, left to right: side view facing right with the body turned toward the viewer, straight front, straight back. Identical design, colors, proportions and scale in every view, feet on one shared baseline, neutral standing pose, no grid lines, no labels, no text. {BG} {STYLE}

## Buildings and props

### tower — Tower, 3 upgrade levels
`{kind}` default: an archer tower: wooden lookout platform on a round stone base

> Game asset sheet of {kind} in three upgrade levels, side by side left to right in ONE row of three equal cells. Level 1 small and simple, level 2 taller with more stone and red banners, level 3 bigger with gold trim and a few flat crystal shapes. Same camera angle, same footprint size and same base position in every cell so they can swap in place. No grid lines, no labels, no text. {BG} {STYLE}

### prop — Map props
`{what}` default: a set of 6 props: two pine trees, a boulder, a wooden fence piece, a haystack, a broken cart

> Game prop sheet: {what}. Arranged in a neat 3x2 grid with generous spacing, each prop separate and complete, consistent scale as if placed on the same battlefield. No grid lines, no labels, no text. {BG} {STYLE}

## Effects and UI

### fx part — ONE element of a layered effect (a `sprite` layer of `scripts/fx_layers.py`)
Rings, smears, bursts, bolts, light columns and particles are drawn by `fx_layers.py` itself: never make
a still for them. Make a still only for a shaped element the tool cannot draw, ONE element per still, nothing
else in it: `{part}` = "a dark storm cloud" (no lightning), "a holy banner on a pole" (no rays, no sparkles),
"an ice crystal", "a flaming meteor rock". Name: `fx_<skill>_<part>_vNN`, folder `out/vfx/<skill>/design/`.

> Single game effect element: {part}, alone, centered, filling about 70% of the frame, seen from the same high top-down camera as the characters: big flat shapes, 2-3 hard-edged tones of its colour, a thick dark outline of the same hue, no other effect around it: no glow, no rays, no sparkles, no lightning, no smoke unless the element IS smoke. {BG} {STYLE}

### icon — Ability icon
`{skill}` default: rain of fire arrows

> Round ability icon for a game HUD showing {skill}: a circular badge with a thick dark outline and a plain gold-yellow rim, the symbol large and centered and drawn with a few big shapes, readable at 64 pixels, strong contrast, no text. {BG} {STYLE}

### ui — UI panel / button
`{item}` default: an empty rectangular wooden panel with stone corners and iron rivets, for a level-select popup

> Game UI element: {item}. Front-facing, flat orthographic view, symmetrical, empty center area for text added later, clean edges suitable for 9-slice scaling, no text, no icons. {BG} {STYLE}

## Backgrounds

### map — Level background (opaque: no `{BG}`, no `--png` needed)
`{scene}` default: a grassy valley with a winding dirt road, pine forest edges and a river crossed by a wooden bridge
`{pads}` default: 6

> Tower defense level background, seen from a high top-down camera tilted about 60 degrees: {scene}. The road enters from the left edge and exits at the right edge. {pads} empty round stone build pads placed beside the road at strategic bends. No characters, no towers, no UI, no text. {STYLE}

## Review checklist (use when critiquing)
- Subject matches the description; silhouette readable at small size.
- Camera is high top-down (about 60 degrees), light from the top-left, as on the characters.
- Flat magenta background only (maps: opaque scene), no magenta or pink on the subject, no ground plate.
- Sheets (turnaround, towers, props): correct cell count, equal spacing, same scale in every cell, shared baseline.
- Style matches `format.md` §1 and a style anchor: big flat shapes, 2-3 tones, thick dark outlines, effects as flat layers.
