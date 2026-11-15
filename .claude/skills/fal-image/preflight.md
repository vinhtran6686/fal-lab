# Preflight: think and verify BEFORE any paid image (every character, every still)

Why this exists (2026-11-15): five characters were made by "draw, look, redraw". Most redraws had a cause that was visible in the prompt before the first draw: contradictory sentences (an axe haft "as tall as the chin" and "the head at knee height"), words that return the wrong body ("stout" in a female prompt), a copied body paragraph, a size the model always overshoots, a weapon too long for the frame. A redraw costs money AND context. **One decision, one image.**

## Rules
1. **No paid image until the design note below is written and the prompt lint has no ERROR.** Put the design note in `brief.md` (or in the answer to the user when the asset does not exist yet).
2. **At most one candidate per decision.** A second image is allowed only after you wrote the DIAGNOSIS of the first one: which sentence of the prompt caused the failure, and the one change that removes the cause. If you cannot name the sentence, read the prompt again; do not draw.
3. **Show the user the design note (and the pose table for poses) for an OK when the change is large** (a new character, a new move). For a small retry, state the one change in a line and go.
4. Look at the image yourself, tick the review checklist line by line, and only then show it. Never show an image you have not looked at.

## Design note (fill every line; 10-15 lines)
1. **Request**: the user's words mapped to slots: class, tier `{H}`, role, sex and age, weapon (or none), main colour, move. Ask only what is missing, in ONE AskUserQuestion call.
2. **Preset and body type** (`style-chunky.md`): brawny / slender / agile. The body paragraph is WRITTEN for this character; never pasted from another one (a female mage got "enormous fists" that way).
3. **Proportions as calibrated numbers**, not adjectives. The model overshoots the heads you ask for on slender and agile bodies (see the table in `style-chunky.md` §1). Write the number that gives the look you want, not the look itself.
4. **Weapon geometry**: length against the figure, size of the head of the weapon, which hand, how it rests, the direction of the edge or the head (a blade projects sideways from an axe haft; a spearhead lies on the axis of the haft). Read every sentence about the weapon once more: do two of them disagree?
5. **Frame fit**: a weapon that rises above the head by `w` (as a fraction of the figure height) needs the figure to fill at most `0.9 / (1.33 x (1 + w))` of the frame height in the PROMPT (the model draws about 1.33 times bigger than asked). Example: a spear 15 % taller than the figure: ask 58-60 %.
6. **One signature feature** (a shoulder guard shaped like a wing, a hat, a scarf, a backpack urn) that is still visible at 60 px, plus the oversized weapon head. List the bold shapes of the costume: at most six.
7. **Colour plan**: one dominant hue in four values, one warm family, one accent family, neutrals; hex for every value; the base value of the dominant hue at least 0.45; **a hue not used by the previous characters** (`grep -h "COLOUR PLAN" out/*/*/brief.md`). Written as hex in the prompt.
8. **Face**: the fewest marks (brow, glowing eyes, nose shape, jaw, one mouth or beard shape); skin in two flat tones.
9. **View and pose**: the master view wording of `format.md` §3 (hero: near-front 20 degrees; enemy, ally, boss: side 30 degrees with the far arm and leg partly hidden). A living pose written as numbers (head tilt about 8 degrees, one shoulder about 5 % lower, weapon tilt about 8 degrees). Side views come back frontal when a visible / NOT visible list is missing (`action-planes.md` §4b): write it.
10. **Words audit**: no vague word (slightly, a little, dynamic, elegant, natural), no word that returns the wrong body, no "ornate / intricate / detailed / pixel art", no name of a commercial game. The lint does this.
11. **Poses of a move**: the table of `action-planes.md` §8 item 1 (letter, role, share of the path, where the weapon points on the screen, body orientation by name, the arc in degrees) is written and agreed before the first pose; the weapon head's orientation per pose is written (`action-planes.md` §8).
12. **Cost**: number of images and the estimate in USD.

## Prompt lint (free)
```
python scripts/prompt_lint.py <prompt.txt> --body brawny|slender|agile
```
Checks required parts (background, upright, two arms and legs, named view, COLOUR PLAN), banned words, `cute / chibi / mascot` outside a negation, commercial game names, magenta or pink outside the background sentence, words that return the wrong body, vague words, frame fit and tip margin, number of hue families, near-black base colours. ERROR blocks the draw; read every WARN and either fix it or write why it stays.

## Verify against the files, not against memory
- Tier numbers and canvas: `classes/<class>.md` §3. View wording: `format.md` §3. Style and body type: `style-chunky.md`. Pose arcs: `action-planes.md`.
- A weapon or a view that was not drawn before in this project: read the lesson list of `action-planes.md` §8 and `style-chunky.md` §9 first.
- References from `ref/` or the user: say what is taken (proportions, colour organisation) and what is not (the design, the name of the game).

## After the image (review, not redraw)
Tick `style-chunky.md` §8 against the image. For each failed line write the sentence of the prompt that caused it. Several failures with one cause are one fix. Ask the user before a redraw when the failure is a matter of taste.
