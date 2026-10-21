# Prompt: draw a character in our style from a concept image

For another AI (any image model that takes a reference image). Built from `.claude/skills/fal-image/format.md` §1-§3 and `classes/hero.md`.
Output: ONE image, 1024x1024, one character, side view facing right: the "master" still our pipeline animates later.

Two prompts: **A** converts the reference to our style and changes NOTHING else (use it alone when the reference already has what you want).
**B** is an optional add-on: paste it after A (same message) and keep only the lines you want to change; delete the others.

## Prompt A: convert style only (fill the 2 values in `[ ]`)
`[CLASS]`: hero / ally / enemy. `[HEIGHT_PX]`: body height in the game: 24, 40, 60 (hero default), 84, 120.

```
Use the attached reference image ONLY for the character's design. Redraw this exact character from scratch in the style described below. Keep EVERYTHING from the reference exactly as it is: the same body, the same number of arms, legs and every other part (count them in the reference and reproduce the same count, none merged or removed), the same face, hair, costume, accessories, colours and proportions. Add NOTHING that is not in the reference: no weapon, no shield, no prop, no extra accessory; if the hands are empty in the reference they stay empty. Ignore only the reference's rendering style, lighting, background and pose, and any signature or text in it.

Single game [CLASS] sprite.

VIEW: SIDE VIEW from a high top-down camera: facing RIGHT toward the right edge of the screen, the body turned only about 30 degrees toward the viewer so the face and the front of the chest are visible. Not a flat profile, not a front view, not a diagonal three-quarter view toward the bottom-right. Every limb of the character stays visible or clearly readable (extra arms must not be hidden or merged).

POSE: standing UPRIGHT in a calm neutral idle stance: the body vertical, not leaning and not walking diagonally, both feet side by side on ONE horizontal ground line, the arms relaxed and held close to the body (every arm visible), nothing raised. Full body, centered, filling about 70% of the frame, fully inside the frame with margin on every side.

SIMPLE: the face is only a brow line and a small eye slit; hands are simple mitten shapes, visible. No buckles, no pouches, no rope, no bandages, no spikes, no stitches, no patches, no fabric texture: clothing is a few big flat shapes. At most three colour families.

STYLE: Stylized 2D vector cartoon game art for a top-down fantasy tower defense game, designed to read at about [HEIGHT_PX] pixels tall. Simple design: big clear shapes and a strong silhouette; small details are left out or merged into larger shapes; faces, hands, armour and clothing are suggested with a few lines, never rendered in fine detail. Stylized, exaggerated cartoon proportions, not realistic anatomy (about 2.5 to 3.5 heads tall; models draw taller, so aim half a head lower): the parts that express the character's role are enlarged and the rest is shrunk. Colour: flat solid fills only, no gradients, no airbrush, no painterly texture, no noise. Volume and shadow come from 2-3 hard-edged tones of the same colour (shadow, base, light), plus a few small highlight shapes. Thick clean outlines in a dark shade of the neighbouring colour. No glow, no aura, no rim light, no ornate trim, not pixel art. Light comes from the top-left.

BACKGROUND: one flat solid pure magenta color (#FF00FF) everywhere, no gradient, no ground, no shadow, no scenery, no text, no border. Do not use magenta or pink anywhere on the subject.

OUTPUT: one image, 1024x1024, one character only.
```

## Prompt B: add or change details (keep only the lines you need, delete the rest)
Paste under A. Write after the colon; a line left empty or deleted is ignored. Describe sizes against the body and say where each hand is.

```
CHANGES to the design above (apply ONLY the lines below; everything else stays as in the reference):
weapon: [what it is, its size against the body (dagger-short / to the waist / to the chest / as tall as the body), which hand(s) hold it, where it rests in the idle pose; hilt and tip fully inside the frame]
hands: [where each hand is in the calm idle pose, e.g. lower pair hang relaxed with closed fists, upper pair bent with open palms at shoulder height]
pose: [a different stance instead of the neutral one]
costume: [what to add, remove or recolour]
colours: [main colour + one accent, if different from the reference]
other: [anything else]
```

## Check the result (our review list, score 1-10, redo below 8)
1. Flat fills, 2-3 hard tones, thick dark outline, no gradient or glow; face = brow line + eye slit; hands = mittens.
2. Side view facing right, turned slightly toward the camera; upright, feet on one line.
3. Same character as the reference: limb count, hair, costume, colours, proportions; nothing added (no weapon unless B asked for it).
4. Whole body inside the frame with margin; every arm visible.
5. At most three colour families; no magenta on the character; background one flat magenta.

Fix one thing per retry: a wrong weapon or a lost limb is the costly mistake (7 versions on the first hero); name the part and say "must be visible".
