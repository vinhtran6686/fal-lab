# Prompts: the remaining stills from an approved master (same set as the `fal-image` skill)

Use in the other tool, one message per asset. Attach the APPROVED master (the side view you chose) as the reference image every time.
Paste a prompt, fill or delete every `[ ]` (an unfilled `[ ]` is read as text), then paste the COMMON TAIL under it.
Which assets a character needs depends on its class (from `classes/*.md`):
| Class | Stills after the master |
|---|---|
| enemy, boss | `view_front`, `view_back`, `icon`, `projectile` (ranged only), `pose_skill_*` (boss specials) |
| hero | `icon`, `projectile` (ranged only), `pose_respawn`, `pose_levelup` (optional), `pose_skill_*` (optional: skip when you can describe the final pose in words) |
| ally | `icon` |
| any skill effect | `fx part` (only a shaped element: a banner, a crystal), `ability icon` |
Output of each: one image 1024x1024, flat magenta background. Review each against the master, redo below 8/10.

## COMMON TAIL (paste under every prompt below)
```
STYLE: Stylized 2D vector cartoon game art for a top-down fantasy tower defense game, designed to read at about [HEIGHT_PX] pixels tall (24, 40, 60, 84, 120 or 170). Simple design: big clear shapes and a strong silhouette; small details are left out or merged into larger shapes. Colour: flat solid fills only, no gradients, no airbrush, no painterly texture, no noise. Volume and shadow come from 2-3 hard-edged tones of the same colour, plus a few small highlight shapes. Thick clean outlines in a dark shade of the neighbouring colour. No soft glow, no aura, no rim light, no ornate trim, not pixel art. Light comes from the top-left. Fire or magic that is PART OF THE CHARACTER stays as in the reference: flat layered shapes with an outline, never soft blur.
BACKGROUND: one flat solid pure magenta color (#FF00FF) everywhere, no gradient, no ground, no shadow, no scenery, no text, no border. Do not use magenta or pink anywhere on the subject.
OUTPUT: one image, 1024x1024.
```

## 1. Front view (enemy, boss)
```
Use the attached reference image ONLY for the character's design; keep every part, colour, proportion and the same number of limbs exactly as in the reference, add nothing. Redraw this same character as a straight FRONT view, perfectly facing the viewer, walking toward the bottom of the screen: mirror-symmetric body, both eyes (or the face/visor) visible, both shoulders the same size, feet side by side on ONE horizontal ground line, standing UPRIGHT in a calm neutral stance, [items held, if any: which hand, upright; otherwise "hands empty"]. Full body, centered, filling about 70% of the frame, everything inside the frame with margin. Not a side view.
```

## 2. Back view (enemy, boss)
```
Use the attached reference image ONLY for the character's design; keep every part, colour, proportion and the same number of limbs exactly as in the reference, add nothing. Redraw this same character as a straight BACK view, seen from directly behind, walking away toward the top of the screen: the back of the head, NO face and NO eyes visible, mirror-symmetric body, feet side by side with the heels toward the viewer on ONE horizontal ground line, standing UPRIGHT in a calm neutral stance, [items held, if any: same hand as in the front view, upright]. Everything worn on the FRONT (visor, face, chest emblem) is hidden; everything on the BACK (cape, wings, spikes, a back plate) is in full view. Full body, centered, filling about 70% of the frame, everything inside the frame with margin. Not a side view, not a front view.
```

## 3. Icon (HUD portrait)
Pick the rim and badge by class: hero or ally = bright gold-yellow rim, badge = the character's main colour, lighter; enemy = muted stone-grey rim, muted khaki badge; boss = dark iron rim with one warning-colour band, muted dark red badge.
```
Use the attached reference image ONLY for the character's design. Round character portrait icon: ONLY the head and shoulders of this same character (same face, helmet or hair, colours), cropped at the chest, facing slightly right, inside a circular badge with a thick dark outline and a [RIM] rim, plain [BADGE] background inside the circle. Readable at 64 pixels.
```
(Icon exception to the tail: the circle badge replaces the plain magenta; keep magenta OUTSIDE the circle.)

## 4. Projectile (ranged only)
```
Single projectile sprite fired by the character in the reference image: [what it is, e.g. a small fireball, an arrow, a dark bolt]. Pointing right, centered, small and simple, filling about 40% of the frame, same palette as the character.
```

## 5. Pose for a skill (`pose_skill_<name>`, the PEAK of the move)
```
Use the attached reference image ONLY for the character's design; the same character, same SIDE VIEW (facing RIGHT, body turned about 30 degrees toward the viewer), same proportions, colours and gear, but in this pose: [the peak pose of the skill, described by body part: legs (knees, which foot forward, weight), torso, head, each arm and hand, the held item's direction and height]. Everything inside the frame with margin, nothing above the top edge. No effects around the body: the effect is made later.
```
Skip this still when the pose can be written in the animation prompt; it matched on the first try without a still.

## 6. Hero state poses (hero only)
```
Use the attached reference image ONLY for the character's design; the same character, same SIDE VIEW (facing RIGHT, turned about 30 degrees toward the viewer), same proportions, colours and gear, in this pose: [pose_respawn: KNEELING low on one knee, head bowed, the weapon planted upright in front, motionless | pose_levelup: your pose]. 
```
For a lifeless respawn start add: "THE WHOLE character IS DESATURATED GREY: every part (armour, cloth, skin, weapon) in flat shades of cool grey (light, mid and dark only), no colour anywhere; outlines stay near-black. The character has no colour at all, only grey." (the tail's magenta rule still applies to the background).

## 7. Effect part (a shaped element only; rings, bursts and light are drawn by the tools, never make a still for them)
```
Single game effect element: [ONE element, e.g. "a dark storm cloud" with no lightning, "a holy banner on a pole" with no rays, "an ice crystal"], alone, centered, filling about 70% of the frame, seen from a high top-down camera: big flat shapes, 2-3 hard-edged tones of its colour, a thick dark outline of the same hue, no other effect around it: no glow, no rays, no sparkles, no lightning, no smoke unless the element IS smoke.
```

## 8. Ability icon (skill button)
```
Round ability icon for a game HUD showing [the skill, e.g. a rain of fire arrows]: a circular badge with a thick dark outline and a plain gold-yellow rim, the symbol large and centered and drawn with a few big shapes, readable at 64 pixels, strong contrast, no text.
```

## Check each result
Same character as the master (limb count, colours, proportions, nothing added); flat fills and thick dark outline; whole body inside the frame; front has the face and symmetric, back has NO face; icon cropped at the chest inside a circle; one flat magenta background. Retry one fix at a time and name the part ("must show both arms").
