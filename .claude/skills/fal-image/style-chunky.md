# Style preset: chunky vector (default for new characters since 2026-11-15)

Read `preflight.md` first (think and verify before any paid image), then this file with `format.md` §1. The preset changes HOW a character is drawn (proportions, shapes, colour, face, detail); it changes nothing of the FORMAT
(one upright idle, near-front view, magenta background, margins, files, manifest). The older flat block of `format.md` §1 stays for assets made before
this date (`azure_blade`, `holy_commander`, `pyre_witch`, `surya`) and whenever the user asks for it. A character records its preset in `brief.md`
(`style: chunky`), and every later still of that character (views, poses, icon) reuses the same `{STYLE}` and colour plan.

Why it exists: the first block says "simple design, small details left out". It produced boxy, one-colour, symmetrical characters that the user called
monotone and crude. The user's references (a chunky cartoon tower-defense roster and several painterly concepts) were analysed and tested over eight
versions of one hero (`out/heroes/moon_crane`); the criteria below are what made it match. Never name the game the references come from in a prompt.

## 1. Proportions: role parts big, the rest small
- **About 3 heads tall**: the head is about one third of the figure. Massive barrel chest, huge round shoulders, **enormous fists (each almost as big as the face)**, thick forearms, **short thick legs and big boots**, wide planted stance.
- The weapon is oversized: a spear a little taller than the figure, a blade or a spearhead about as big as the head. The weapon head is the part that must read at 60 px.
- Size varies with the role: see "Body types" below. The 3-head brawny chunk is for melee and tank roles only.
- This overrides "3.5-4.5 heads" of `format.md` §1 for this preset only. The character is still **grim, serious, mature: never cute, never a mascot** (`format.md` "No chibi, no cute" keeps its other bans).

### Body types (choose one per character; never copy the body paragraph of the previous character)
The preset fixes how shapes are drawn, not one body. The first test (a brawny male spearman) wrote "massive barrel chest, enormous fists, short thick legs" and the same words, copied into a female mage, gave a beefy, androgynous figure (`tide_caller` v01). Pick the type from the role and the sex and write its own paragraph:
| Type | Use for | Heads | Body words that worked |
|---|---|---|---|
| **Brawny** | melee, tank, brute, male warriors | about 3 | BIG head one third of the height, massive barrel chest, huge round shoulders, ENORMOUS fists (as big as the face), short thick legs, big boots |
| **Slender** | casters, archers, supports, most female heroes | about 3.5-4 | big head (about 28 % of the height), narrow rounded shoulders, a clearly CINCHED waist, a bell-shaped robe or skirt that flares, slim arms, hands only a little bigger than life, slim legs in sturdy boots, weight on one leg |
| **Agile athletic** | young fast fighters, duelists, monks, scouts (male or female) | about 4.5-5 as DRAWN | ATHLETIC balanced build with defined but not bulky muscles, broad shoulders narrowing to a lean waist, strong forearms, hands a little bigger than life, lean legs (about 45 % of the height), a light springy stance with the weight on one leg, one arm bare or bracered |
Feminine cues are told by BIG shapes, never by detail: a small soft chin and rounded jaw, lips as ONE small colour shape, thin brows, a cinched waist (belt and fitted bodice), a flared hem, a long braid or bun as a few solid clumps. A "stout", "massive" or "enormous" word anywhere in a female prompt returns the brawny body.
Tested limit (`tide_caller` v02): the slender body gets a more illustrative look (soft skin shading, thinner outline, more face detail) than the brawny one; repeat "thick outline, bold flat shapes, face of the fewest marks" in the prompt and check against §8 at 60 px.

### Proportion calibration (the model overshoots; measured 2026-11-15)
| Body | Asked in the prompt | Drawn | Verdict |
|---|---|---|---|
| brawny | "about 3 heads, head one third of the height" | about 3 | follows the number |
| slender | "about 3.5 heads, head about 28 %" | about 4-4.5 | good |
| agile | "about 3.5 heads, head about 28 %, big head" | about 4 but chibi-looking (hair volume, "big head") | too childish |
| agile | "about 5 heads, head about 20 %" | about 7 | far too tall, outline thin, style lost |
| agile | "about 4.3 heads, head about 24 %, VERY thick outline, no soft shading" | about 6 | accepted |
Rule: for slender and agile bodies the drawn figure is 1 to 2 heads taller than asked, and a "chunky" word pushes it back toward chibi. Ask about 3.8-4.3 heads (head 24-27 %) and keep "bold flat shapes, VERY thick outline". Words that make a body childish: "big head", "bean-like volumes", "squash and stretch", "round", "cute"; use them only for the brawny body.
Frame fit: the model draws the figure about 1.33 times bigger than the fill you ask for (asked 62-68 %, drawn 90-94 % with a long weapon). Ask 58-60 % for a weapon taller than the figure (`preflight.md` item 5).

## 2. Outline, tones, texture
- Thick clean **dark mauve-brown outline (never pure black)**, clearly thicker on the outer silhouette and thinner for inner lines, rounded joins.
- Flat fills in **3-4 stacked hard-edged tones**: shadow, base, light and one bright highlight shape on top. No gradients, no airbrush, no painterly texture, no realistic rendering.
- Material is told by a **few flat speckle spots** of a lighter or darker tone on large surfaces (armour, skin, wing, stone), never by lines.
- Chunky rounded bean-like volumes with slight squash and stretch; big simple shapes first.

## 3. Colour harmony (measured on ten reference characters)
1. **One dominant hue used in four values** (shadow, base, light, top highlight). Example: a blue family `#25526f #3786bc #8dc3e4`; a yellow-olive family from `#322e08` to `#e1c741`; a brown family only.
2. **Other hues are neighbours**, or ONE complementary accent (teal against orange, blue against gold).
3. **One warm family shared by skin, leather, belt, boots and wood** (hue about 15-40 degrees) ties every figure together.
4. **Gold or warm yellow (hue 40-52) is the universal accent**, used as chunky bands and big shapes, never as thin lines.
5. **Shadows are tinted, never black** (mauve `#26151a`, deep teal `#132126`); **lights are warmer and paler tints of the same colour**, never pure white.
6. **At most three families plus neutrals**: dominant + warm + accent, with one tiny saturated accent (a gem, a tassel, glowing eyes).
Saturation does NOT separate good from bad: the references are saturated (0.7-0.85) in their dominant hue. The harmony comes from the number of families and the value ladder. Large areas stay in mid values so the figure reads when shrunk (a navy or near-black body turns into one dark mass at 60 px).
**Method**: quantise each reference (median cut, 7 colours, background removed), list hue / saturation / value per colour, then write the palette of the new character with hex values (see §7).

## 4. Face: the fewest marks
The character is shown at about 60 px; the face is a few pixels. Write: a thick angular brow shape, **two bold glowing eye shapes with no pupils (the brightest points of the face)**, a small nose shape, a square jaw, a beard or mouth as ONE solid shape with a lighter patch. Forbid in the prompt: pupils, eye highlights, eyelashes, ear detail, wrinkles, skin texture, realistic face shading. Skin in two flat tones.

## 5. Detail level: medium
Details are bold simple shapes: one big emblem on the chest, layered plates, chunky gold bands, a tassel, a gem. **No filigree, no engraving, no tiny patterns, no thin gold lines, no ornate trim**; the words "ornate", "intricate", "highly detailed" stay banned. A pattern is allowed only as a big shape (a bird, a crescent) that is still visible at 60 px.
Silhouette: **one signature feature** (an oversized wing-shaped shoulder guard, a horn, a cape) plus an oversized weapon, an asymmetric costume, and a silhouette that is recognisable when filled black.

## 6. Pose of the master: upright but alive
The master stays an upright idle (`format.md` §3 `{UPRIGHT}`), with life written as numbers, not adjectives: head tilted about 8 degrees, one shoulder about 5 % of the figure height lower, the weapon tilted about 8 degrees, one fist raised a little. Words such as "slightly" or "dynamic" return the default pose (`action-planes.md` §4b).

## 7. Prompt template (master of a hero)
`Single game hero sprite: {design}.` + `{VIEW + UPRIGHT}` + `{BG}` + `{STYLE chunky}`; for the other stills, the usual `--ref` wording of `format.md` §3.
`{design}` carries, in this order: role and body in heads ("about 3 heads tall, a BIG head about one third of the height, enormous fists ..."), the face (§4), `TWO ARMS ... TWO LEGS ...`, the signature feature, the armour (one emblem, chunky bands), the weapon with its size and the hand that holds it, then a **COLOUR PLAN**:
> COLOUR PLAN with strict harmony: ONE dominant hue, a muted {hue name} (hue about {deg} degrees), used in four values only: shadow #…, base #…, light #…, top highlight #…. ONE warm family for the skin, the leather, the belt, the boots and the haft: … ONE accent family, gold, only chunky bands and big shapes: … {special material} ONLY for {part}. ONE tiny {accent} accent (…) and ONE small gem; glowing eyes in warm pale gold. Rules: large areas are mid values; only the eyes, the gem and the small accents are strongly saturated; every shadow is a darker tint of its own colour, never black; every light is a warmer, paler tint, never pure white; the outline is a dark mauve-brown #….

`{STYLE chunky}` (fill `{H}` from the size tier):
> Style: stylized 2D vector cartoon game art for a fantasy tower defense game, in the manner of a chunky heroic cartoon hero illustration, designed to read at about {H} pixels tall. Chunky rounded bean-like volumes with slight squash and stretch, big simple shapes with a bold silhouette, exaggerated proportions with the hands, shoulders and the weapon enlarged and the legs shrunk. Colour: flat solid fills in 3 to 4 stacked hard-edged tones (a shadow tone shifted toward a cooler hue, the base, a lighter tone, and one bright highlight shape on top), with the large areas kept in MID values so the figure stays readable when shrunk; no gradients, no airbrush, no painterly texture, no noise, no realistic rendering. Thick clean dark mauve-brown outlines (never pure black), clearly thicker on the outer silhouette and thinner for inner lines, with rounded joins. A few small flat speckle spots of a lighter or darker tone are scattered on the armour and the skin. Medium detail only: details are bold simple shapes (one emblem, layered plates, a tassel, a gem), no fine engraving, no filigree, no tiny patterns, NO thin gold lines. High top-down camera tilted about 60 degrees; light comes from the top-left.

Words to use: "chunky", "bold shapes", "mid values", "thick gold bands", the hex values. Words not to use: "simple design", "small details are left out", "elegant", "realistic", "painterly", "ornate", "intricate", "detailed".

## 8. Review checklist (a master passes only if every line is true when LOOKED AT)
- [ ] Head about one third of the figure; fists as big as the face; short legs; the weapon head about as big as the head.
- [ ] Style: flat tones with hard edges, outline mauve-brown and thicker outside, no gradients, no filigree.
- [ ] **Shrink test**: the figure at 200, 120 and 60 px (next to a reference crop): the emblem, the weapon head, the signature feature and the eyes are still visible; no large area is near-black; gold bands are still visible.
- [ ] Colour: one dominant hue in four values, one warm family, one accent family; no more than three families plus neutrals; no pure black or pure white.
- [ ] Face: only brow, glowing eyes, nose shape, jaw, one beard / mouth shape.
- [ ] The prompt contains numbers and hex values, not adjectives. `python scripts/ingest_image.py <image> --check`: no magenta tint in the subject.
- [ ] Margins: the weapon tip at least 8 % inside the frame (a long weapon may fill 90 % of the height; scale it down when composing).

## 9. Known limits
- The model ignores percentages for size and position of whole figures between stills (`action-planes.md` §8); for later poses measure and align.
- "Muted" is ignored: the model draws saturated colour. Control harmony by the number of families and the hex values, not by asking for muted tones.
- A weapon with a thin blade (a long sword) reads badly at 60 px in this style; give it a wide bright blade or a bright highlight shape.
- Steel and cloth drift to a soft gradient (a blade, a scarf): write "steel in three flat hard-edged tones" and "no gradient on cloth".
- In `enemy` and `boss` masters the "SIDE VIEW turned 30 degrees" came back frontal (the body square to the viewer, both arms visible) three times out of three; the near-front 20-degree view of a hero is accepted. Write the visible / NOT visible list (`action-planes.md` §4b) and the far arm "partly hidden behind the body" for side masters.
- The model keeps a thin stitch or a thin line when a patch or a seam is named: do not name patches, seams, stitches.

## 10. Worked examples (prompts that passed; copy the structure, never the body paragraph)
| Asset | Class, body | What it tested | Prompt |
|---|---|---|---|
| `out/heroes/moon_crane` | hero M, brawny, spear | the preset; one dominant hue + gold; wing shoulder guard | `source/design/prompts/master_p08.txt` |
| `out/heroes/tide_caller` | hero M, slender, female mage with a staff | feminine cues by big shapes; coral accent | `master_p02.txt` |
| `out/enemies/urn_thief` | enemy S, brawny goblin | enemy palette (plum + olive + toxic lime), a backpack urn silhouette | `master_p01.txt` |
| `out/bosses/cairn_seer` | boss XL, brawny, body magic without weapon | glow drawn as flat layers; stone body | `master_p01.txt` |
| `out/heroes/dragon_sabre` | hero M, agile athletic, great dao | proportion calibration (chibi to tall); scarf silhouette | `master_p03.txt` |
Each asset's `brief.md` holds its colour plan and its own lessons; `python scripts/prompt_lint.py <prompt> --body <type>` on these files shows what the lint reports on prompts that were accepted (vague words and a base colour are warnings, not errors).
