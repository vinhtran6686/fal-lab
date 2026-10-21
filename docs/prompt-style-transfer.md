# Prompt: draw a character in our style from a concept image

For another AI (any image model that takes a reference image). Attach the concept image, paste the prompt below, fill the 5 slots in `[ ]`.
Built from `.claude/skills/fal-image/format.md` §1-§3 (style block, SIMPLE, UPRIGHT, master view, BG) and `classes/hero.md` (hero tier M).
Output: ONE image, 1024x1024, one character, the "master" still that our pipeline animates later.

## Fill these first (the ones people forget are the weapon ones)
| Slot | What to write | Example |
|---|---|---|
| `[CLASS]` | hero / ally / enemy | hero |
| `[HEIGHT_PX]` | body height in the game: 24, 40, 60 (hero default), 84, 120 | 60 |
| `[DESIGN]` | ONE dense sentence: body type and what is exaggerated, costume, palette (one main colour + one accent), the weapon | see example |
| `[WEAPON_SIZE_AND_HAND]` | the item's size against the body, the hand(s) that hold it, and where it rests in the idle pose | a sword as tall as from the ground to the chest, both hands stacked on the pommel, point planted in the ground in front |
| `[CHANGES]` | what to take from the concept image and what to change (optional) | keep the helmet and cape, drop the shield |

Example `[DESIGN]`: "top-heavy holy knight about 2.5 heads tall (huge rounded silver shoulder plates, small head, short legs), sleek silver plate armour with a gold cross on the chest, tall silver helmet with an angular T-shaped visor and a swept-back red plume, a long plain red cape behind him; saturated silver main colour, bright gold accent, red cape".

## The prompt (copy from here)

```
Use the attached reference image ONLY for the character's design (shape, gear, colours, proportions, the hand that holds the weapon). Ignore its rendering style, lighting, background and pose: redraw the character from scratch in the style described below. Keep from the reference: [CHANGES].

Single game [CLASS] sprite: [DESIGN]. [WEAPON_SIZE_AND_HAND].

VIEW: SIDE VIEW from a high top-down camera: facing RIGHT toward the right edge of the screen, the body turned only about 30 degrees toward the viewer so the face and the front of the chest are visible, the far arm and leg partly hidden behind the body. Not a flat profile, not a front view, not a diagonal three-quarter view toward the bottom-right.

POSE: standing UPRIGHT in a calm neutral idle stance: the body vertical, not leaning and not walking diagonally, both feet side by side on ONE horizontal ground line, the weapon at rest (lowered or upright in front of the body, not raised to strike), a shield or off-hand item held at the side. Full body, centered, filling about 70% of the frame. The weapon and every part of the body stay fully inside the frame with margin on every side (a long upright weapon must not reach the top edge; a planted tip must stay above the bottom edge).

SIMPLE: the face is only a brow line and a small eye slit; hands are simple mitten shapes, visible and holding the weapon (not hidden in sleeves). No buckles, no pouches, no straps beyond one, no rope, no bandages, no spikes, no stitches, no patches, no fabric texture: clothing is a few big flat shapes. At most three colour families.

STYLE: Stylized 2D vector cartoon game art for a top-down fantasy tower defense game, designed to read at about [HEIGHT_PX] pixels tall. Simple design: big clear shapes and a strong silhouette; small details are left out or merged into larger shapes; faces, hands, armour and clothing are suggested with a few lines, never rendered in fine detail. Stylized, exaggerated cartoon proportions, not realistic anatomy (about 2.5 to 3.5 heads tall; ask for half a head less than you want, models draw taller): the parts that express the character's role are enlarged and the rest is shrunk, so the silhouette reads at [HEIGHT_PX] pixels. Colour: flat solid fills only, no gradients, no airbrush, no painterly texture, no noise, no realistic rendering. Volume and shadow come from 2-3 hard-edged tones of the same colour (shadow, base, light), plus a few small highlight shapes. Thick clean outlines in a dark shade of the neighbouring colour. No glow, no aura, no rim light, no ornate trim, no "intricate" or "highly detailed" rendering, not pixel art. Light comes from the top-left. Heroes: a saturated, clean main colour plus one bright accent.

BACKGROUND: one flat solid pure magenta color (#FF00FF) everywhere, no gradient, no ground, no shadow, no scenery, no text, no border. Do not use magenta or pink anywhere on the subject.

OUTPUT: one image, 1024x1024, one character only.
```

## Check the result (our review list, score 1-10, redo below 8)
1. Flat fills, 2-3 hard tones, thick dark outline, no gradient or glow; face = brow line + eye slit; hands = mittens.
2. Side view facing right, turned slightly toward the camera; upright, feet on one line; weapon at rest.
3. Whole body and weapon inside the frame with margin; hilt and tip both visible; the hands visible on the weapon.
4. Weapon size matches `[WEAPON_SIZE_AND_HAND]`; at most three colour families; no magenta on the character; background one flat magenta.
5. Same character as the concept (gear, colours, proportions), not its painting style.

If the weapon is wrong (too short, tip cut, hilt hidden, one hand), fix only that sentence and regenerate; it is the most expensive mistake in our experience (7 versions on the first hero).
