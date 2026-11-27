# Style preset: vivid (draft, from 10 user references; 2026-11-27)

Candidate default for new characters, to replace `style-chunky.md` once the Lightning clan test is approved. Same FORMAT as `format.md` (one character per still or a lineup grid on magenta, side view, upright). It changes HOW the character is drawn. Source of the traits: `docs/skills/fal-image/fal-image-style-board.md` and the images in `ref/style_board/`. Never name the game the references come from in a prompt.

## 0. Description header (required for every character)
Every character description starts with four tags, in this order, so the model draws gender, role, element and kind unmistakably: **GENDER** (male, female, or "no gender" for a construct), **CLASS** (melee fighter, assassin, archer, spear thrower, mage, priest or support, knight, brute or tank, chief or boss), **ELEMENT** (the clan's: fire, ice, lightning, poison, nature, earth, water, wind) and **KIND** (human, beast, monster, construct, spirit). Example: "COIL SOLDIER, male, melee fighter, lightning, human: ...". The body paragraph of §1 then follows the tags (male fighter: stocky with huge fists; female caster: slim with flowing hair; beast: its own anatomy). The element shows in the colour plan and in ONE signature motif of the element (coil and spark shapes for lightning, flame clumps for fire, crystal shards for ice, goo drips for poison), never as a glow. Same four tags go in `brief.md` and in the lineup `meta.json`.

## 1. Body by gender and role (write one body paragraph per character; never copy another's)
| Group | Heads | Words that give it |
|---|---|---|
| Male fighter, brute, tank | 2.5-3 | BIG head, huge shoulders and chest, enormous fists as big as the face or bigger, very short thick legs, wide stance, a big beard or moustache |
| Old or comic caster | about 3 | caricature face (wide open mouth or shut eyes), long white beard, small hands |
| Female hero, priestess, mage | 4-5 | slim with a clear waist and a gentle curve, long flowing hair, a cape that flies, a confident face with a few eyelash marks, bright eyes; never chibi |
| Agile (assassin, scout) | 4-4.5 | lean and muscular, forward lean, sharp angles |
| Monster, elemental | 2.5-3 | body made of its element (stone blocks, flame shapes, chitin), biggest part is a fist or a limb |
| Beast, mount | natural | one huge feature (horns, ruff), strong silhouette |
One OVERSIZED signature element per character (weapon, shield, hat, pauldron, fist, mount). The silhouette must read when filled black and at 60 px.

## 2. Outline, shading, material
**Simple and clean is the first rule (user feedback 2026-11-27, test 2).** The references are CLEAN: every part is one big smooth shape. A first test that asked for "speckle spots, scratches, rivets, plate edges" came out busy and smudged (only 1 of 10 matched). So: no texture, no hatching, no scratches, no speckles, no fringe, no thin lines; at most six bold shapes in a costume; hair, beards, fur, flames and capes as 3-5 big smooth clumps with pointed tips; surface detail only a few big highlight shapes and a few round rivets; draw the characters LARGE in the cell (about 80 % of its height), not tiny, so the model keeps edges crisp.

- Thick clean outline, **dark but tinted by the local colour** (deep navy, deep purple, deep brown, deep green), thicker on the outside, thinner inside, rounded joins.
- Flat cel shading in 3-4 hard-edged tones with **strong contrast**: a deep tinted shadow, the base, a light tone, and a cream-white highlight shape; one bright rim-light shape on the lit edge and a few glossy highlight shapes on metal. No gradients, no airbrush, no soft glow, no blur.
- Material is NOT told by texture: only big smooth shapes, a few big highlight shapes and round rivets; hair, fur and flames as 3-5 big flat clumps with pointed tips.

## 3. Colour
One **saturated** dominant hue + one **bright accent close to its complement** (purple + gold, green + gold, blue + gold or cyan, orange + blue-grey) + cream-white highlights. Shadows are a deeper tint of the same colour. Glows (eyes, crystals, gems) are flat layered shapes, never a halo. Never magenta or pink on the subject (the background is keyed): a violet or pink accent must be kept clearly violet (see `docs/scripts/lineup/lineup-workflow.md`, the pink fix).

## 4. Face: personality in a few bold shapes
Heavy angular brows, and ONE expression: a snarl with teeth, a toothy grin, a squint, a big moustache or beard, glowing eyes (no realistic eyes, no tiny pupils). Women: eyelash marks, small mouth shape, brow lines. Dark, grim-heroic or comic, never a cute mascot.

## 5. Prompt block `{STYLE vivid}` (fill `{H}`)
> Style: stylized 2D vector cartoon game art for a fantasy tower defense game, in the manner of a bold heroic cartoon character illustration with a lot of personality, designed to read at about {H} pixels tall. Exaggerated chunky proportions: stocky male characters about 2.5 to 3 heads tall with a big head, huge shoulders and chest, enormous fists and short legs; female and agile characters slimmer, about 4 to 5 heads tall; every character has ONE oversized signature element. Faces with strong expression: heavy angular brows, snarls or grins showing teeth, big moustaches and beards, glowing eyes. Colour: one saturated dominant hue with a bright accent close to its complement and cream-white highlights; flat solid fills in 3 to 4 hard-edged tones with strong contrast, a deep shadow tone tinted toward the colour, a bright rim-light shape and a few glossy highlight shapes on metal; no gradients, no airbrush, no soft glow, no blur, no painterly texture. Thick clean outlines in a dark shade of the local colour, thicker on the outside and thinner inside, with rounded joins. SIMPLE AND CLEAN: every part of the body and the costume is ONE big smooth bold shape with clean crisp outlines and large flat colour areas, at most six bold shapes in the costume; hair, beards, fur, flames and capes are three to five big smooth clumps with pointed tips, never many thin strands; the only surface detail is a few big highlight shapes and at most a few round rivets; NO texture, NO hatching, NO scratches, NO speckles, NO noise, NO fringe, NO tiny details, NO thin lines. High top-down camera tilted about 60 degrees; light comes from the top-left.

## 6. Review (a still passes only if every line is true when LOOKED AT)
- [ ] Proportions match the group of §1; one oversized signature element; fists as big as the face on males.
- [ ] Outline dark and tinted, thick outside; tones hard-edged with a cream-white highlight; no gradient, no halo.
- [ ] One dominant hue + a complementary accent; deep tinted shadows.
- [ ] The face has an expression (brow, teeth, moustache or lashes), not a blank face.
- [ ] Shrink test at 60 px: silhouette, signature element and eyes still read.
- [ ] No pink or magenta on the subject (`python scripts/lineup/lineup_fix_pink.py`).

## 7. Status and known limits
Draft. Tried twice. **Test 2 (ten brand-new characters of mixed gender, class, element and kind, `out/enemies/_lineups/vivid_test/`, prompt `docs/scripts/lineup/prompts/lineup-grid-vivid-style-test.txt`, 0.021 USD)** gave the best result so far: the four tags of §0 plus a colour plan PER CHARACTER (own dominant + complementary accent + cream) made every character different in silhouette, colour and mood; the key is clean without any pink recolour (only the background flattening of `lineup_fix_pink.py --flatten-bg` was used; do NOT run the pink recolour on a grid that has purple skin); the shrink test at 60 px and 120 px reads (shield, flame hair, axe, scarf, mushroom hat, bow, ogre, wolf, crystal golem); the Tide Lord (many small fins and spikes) is the busiest at 60 px. **Test 1** was the Lightning clan lineup (10 characters, `out/enemies/_lineups/lightning/source/design/grid_vivid_v01.png`, prompt `docs/scripts/lineup/prompts/lineup-grid-lightning-clan-vivid.txt`, one image about 0.021 USD):
- **Worked:** the four tags of §0 gave an unmistakable gender, class, element and kind per character; stocky males with enormous fists and big beards and moustaches, slim women with a clear waist, flowing hair and a confident smirk, a beast, an insect-like monster, a stone construct; every face has an expression; the dominant yellow with a violet accent (near-complementary) reads strongly; the outline is dark and tinted; the cel shading is hard-edged.
- **Watch:** more texture and trim than the references (scratchy fringes on cloaks and feathers, many small bits), which may not read at 60 px; the chief's jagged cloak and shoulder plates are very wide (about 67 % of the cell, 43 % tall after the regrid); women's armour is skimpy (keep it like the references or ask for more cover); the model again painted violet as magenta-pink (use `lineup_fix_pink.py --target 130,90,235 --flatten-bg`, then the key is clean).
- The pre-existing limits of `style-chunky.md` §9 still apply. Not approved yet: the user compares it with the chunky grid before it replaces the default.
