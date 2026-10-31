# Reference-video route: a character performs a move taken from a sprite sheet

Tested 2026-10-29 on two heroes. Status: **works, not yet a skill**. This file is the full method so it can become one
(`video-sprite` route "ref") without re-deriving anything. The normal route (pose stills -> `h3-max-turbo` first/last frame ->
body-only clip + separate fx) is unchanged; this is a second route for when the user has a **motion + effect reference**.

## 1. What it does
Input: the approved master of a character (`Image 1`) and an mp4 made from a sprite sheet of ANOTHER character performing a
move (`Video 1`). Output: one clip of our character doing the same move, in the same timing, with the same kind of effect.
No pose stills are needed (hero.md §5 item 5 is optional). Endpoint: fal `minimax/h3-max/reference-to-video`.

| Test | Result |
|---|---|
| Dragonkin hero, slash combo, prompt "pose and timing only, no effects" | identity 8/10, pose match ~4/10: the model drew its own arcs and sometimes turned away |
| Surya, rising uppercut (reference: a fire fist skill, 43 frames), prompt "copy motion AND effects" | user: "quá tốt". Identity 8, fx 8, motion 7 (starts upright instead of crouched; the body shrinks while crouching) |
Two lessons: (1) a **short, single-beat, side-view move with a clear fx** matches best; a long multi-hit combo matches worst;
(2) asking for the effect too (not "no effects") gave the better result, because the fx timing tells the model where the beats are.

## 2. Sources of references (what the user may bring)
- A sprite sheet or a folder of frames the user collected or rendered with another AI: `ref/sprite/<move>/`.
- Frames of an existing game in the reverse repo (`E:\work\reverse\games\<game>\sprites\...`, the frame range comes from the
  animation table, e.g. `hero_robot.lua`: `{prefix, from, to}`).
`ref/` MAY be sent to the API (CLAUDE.md, since 2026-10-29). Rules that stay: say in the prompt what to take (pose, timing,
effect shape) and what NOT to take (the character's body, colours, costume); never name the source game or studio in a prompt.

## 3. Step 1 - build the reference mp4 (free)
```
python scripts/make_ref_video.py --src "<pattern with {i:04d}>" --first 162 --last 204 \
    --out ref/sprite/uppercut --name ref_uppercut --seconds 5
```
What the script does and why each choice matters:
| Choice | Why |
|---|---|
| ONE crop box = union of the alpha boxes of all frames (+12 px) | keeps the registration; a per-frame crop makes the body jump |
| ONE scale, frames centred on a flat WHITE 704x704 canvas | one fixed camera and one body size in the reference |
| encode with `-framerate N` then `-vf fps=30` | the API rejects < 24 fps (`video_frame_rate_error`: a 10 fps file failed) |
| `--seconds` = the length you will ask for (5) | the model follows the video in time; a 4.6 s reference for a 5 s clip drifts by 0.5 s |
| video length 2-15 s | API limit per reference video |
Frames with a transparent background are composited on white. Black or magenta backgrounds also work but white leaked into
the output less than magenta did in the still tests. Keep the move to one clean take (no cut, no second character).

## 4. Step 2 - the request
```
endpoint  minimax/h3-max/reference-to-video      price 0.05 USD per output second (fal pricing API): 5 s = USD 0.25
arguments prompt (names "Image 1" and "Video 1")        prompt_expansion_mode "disabled" (required field)
          reference_image_urls [master]                   reference_video_urls [ref mp4]
          duration 5   resolution "480P"   aspect_ratio "1:1"
          (no image_url / end_image_url: there is no first or last frame)
```
Upload with `fal_client.upload_file`, call `fal_client.subscribe`, download the `video.url` with **curl** (Python urllib failed with
`CERTIFICATE_VERIFY_FAILED` once, after the paid call). Reference code: `out/heroes/surya/source/video/skill_rising_uppercut_side_t01.run.py`.
Output: 480x480, 24 fps, ~5.18 s for 5 s asked. Up to 12 reference files in total (images, videos, audio).

### The prompt (template; the Surya one is `skill_rising_uppercut_side_t01.prompt.txt` beside the clip)
1. **Image 1 = who** : `{design}` verbatim from `brief.md` + "side view facing right, keep the design, proportions and colours exactly".
2. **Video 1 = what** : "motion and effect reference from a DIFFERENT character. Match it frame by frame in time." Then the beats
   written out in time order from the reference (e.g. low crouch guard -> rear fist charged -> pause -> fast rising uppercut to the
   upper right with a diagonal lunge -> settle -> back to guard). Name which beat is the longest.
3. **Effects** (when wanted) : describe the effect by shape and place, in flat 2D terms: "flat orange fireball around the rear fist,
   flame trail along the fist path, flash at the end of the punch, embers, fading glow". Colour them in the CHARACTER's accent colour.
4. **Do not copy** : the reference body, costume, colours, face.
5. **Camera and background** : fixed camera, no zoom, flat solid magenta #FF00FF background, the character stays the same size.
Never say the name of the game or character the reference comes from.

## 5. Step 3 - review (what to look at)
Compare the reference and the output at the **same proportional time** (t / duration of each, not the same second: 5.0 s vs 5.18 s),
12 frames side by side. Check, in this order: identity; start pose (does it start where the reference starts); the longest beat;
fx timing and place; **body size through the clip** (Surya shrank while crouching); background flat; turn-around (3/4-front drift).

## 6. What it does NOT do yet (known limits and the fixes to try)
| Limit | Fix to try |
|---|---|
| Body shrinks when crouching (user note) | add "the character's height and width stay the same size in every frame, only the pose changes"; export with `video_to_sheet.py` fixed scale per clip (`--target-height`, body-size gate by silhouette area) |
| Starts upright, not in the reference's start pose | say it in beat 0: "frame 0 is already in the low crouch"; or pass `image_url` = a still of the start pose (first-frame field exists) |
| Weak diagonal lunge / trail | exaggerate in words ("the whole body travels diagonally up and right") |
| Fx baked into the body; glow on magenta is hard to key | OK for a test. For the game: either export as one sheet (despill, accept the halo) or run the clip with "no effects" and build the fx as `fx_layers.py` / Python fx |
| Multi-hit combos, twists, behind-the-body moves | not followed (the dragonkin test): split into single-beat clips |
| No gates, no `sprite_set.py` | the call is direct. After approval run the standard export: `video_to_sheet.py --set ... --sheet skill_<name>_side` (needs a set/plan whose master and take point to the clip) then `video_prune.py prune` |
| Cost not logged by a script | add the row to `out/costs.csv` by hand (done for the two tests) |

## 7. Files and bookkeeping for one use
- Reference: `ref/sprite/<move>/` (`frames/`, `<name>.mp4`, optionally `preview.png`). Look-and-send only; never an asset of the game.
- Approved clip: `A/source/video/<sheet>_tNN.mp4` + `.json` (model, arguments, seed, price) + `.prompt.txt` + `.run.py`; reject takes are
  deleted (format.md §4, one session one step).
- `A/brief.md` manifest row: `skill_<name>_side` ⏳ tNN until the frames are cut; the vfx row `fx_<name>` ⏭ ("in the clip").
- `A/history.md`: one row with model, price, score and the next fix.
- `out/costs.csv`: one row per paid clip (`minimax/h3-max/reference-to-video,video,480P 5s,...,0.25`).

## 8. Cost of what was tried (2026-10-29)
| Item | USD |
|---|---|
| Surya uppercut clip (1 x 5 s) | 0.25 |
| Dragonkin combo test clip (1 x 5 s) | 0.25 |
| Pose-by-pose still tests with a sprite ref (2 rounds, gpt-image-2 low, edit endpoint) | ~0.27 |
| 12-frame sheet test + 3 poses | ~0.05 |
The first estimate (>= 0.16) was low; the endpoint costs 3.3x the `h3-max-turbo` clip (0.015/s).

## 9. If this becomes a skill
Proposed shape: `video-sprite` route `ref` = (a) ask for the source frames and the move description, (b) `make_ref_video.py`,
(c) write the beat-by-beat description and show it for approval (the same loop as Phase A step 4), (d) price + yes, (e) call,
(f) the 12-frame proportional comparison, (g) bookkeeping above. Open decisions: body-only + separate fx versus baked fx as the
default; a wrapper script `scripts/ref_to_video.py` that does (b)+(e) and logs the cost; whether to run the gates on the output.

## 10. Tests to run next (noted 2026-10-29, user's ideas)
### T1. Shorter reference video -> shorter, cheaper clip
The reference mp4 was slowed: 43 game frames played at 8.6 fps = 5 s, while the original runs 43/30 = 1.43 s (3.5x slower). The
clip then follows it for 5.2 s and looks slow. h3-max bills per output second only (the reference length is free), and accepts
`duration` from 0.92 to 15 s; the reference video must be 2-15 s.
| Variant | `make_ref_video.py --seconds` | clip `duration` | cost (0.05 USD/s) |
|---|---|---|---|
| now | 5 | 5 | 0.25 |
| a | 3 | 3 | 0.15 |
| b | 2 (the shortest the API accepts for a reference) | 2-3 | 0.10-0.15 |
Compare a/b against t01 with the 12-frame proportional board (section 5): does the model still land the crouch, the pause and the
uppercut, or does it merge beats (see video-sprite "Clip length decides the number of motions")? Keep the pause beat in the
reference; remember the output may run ~0.7 s longer than asked. Also fixes "starts upright": with less time the model has less room to idle.

### T2. Price per model, from the public price lists (checked 2026-10-29)
Seedance token formula (BytePlus): tokens = (reference-video seconds + output seconds) x width x height x fps / 1024, 24 fps.
A 5 s 480p 1:1 output = 640x640x24x5/1024 = 48,000 tokens; with a 5 s reference video 96,000 tokens (estimate: the reference is counted
at the output's size and fps, so the pixel size of the real 480p frame of 2.5 may differ; confirm with the first real bill).
| Where | Rate | 5 s out + 5 s ref (96k tokens) | 3 s out + 3 s ref (57.6k) | 5 s out, no ref (48k) |
|---|---|---|---|---|
| BytePlus ModelArk Seedance 2.5 (plans: Light 32 USD / 5M tokens = 6.4 USD per M, the with-video-input rate) | 6.40 / M with video input, 10.70 / M without | **0.61** | 0.37 | 0.51 |
| fal Seedance 2.0 mini reference-to-video | 0.0042 per 1k tokens with a video ref, 0.007 without | 0.40 | 0.24 | 0.34 |
| fal Seedance 2.0 fast | 0.0112 per 1k (no cheaper rate seen for video input) | 1.08 | 0.65 | 0.54 |
| fal minimax/h3-max/reference-to-video (what we use) | 0.05 per output second | **0.25** | **0.15** | 0.25 |
BytePlus Light plan: 5M tokens = ~52 clips of 5 s with a 5 s reference, ~87 of 3 s + 3 s (the plan page says 120-500 s of 480P output;
500 s = 5M / 9,600 tokens per second, no reference video). The plan is valid 3 months. Seedance outputs a minimum of 4 s there.
Verdict: at 480P with a reference video, h3-max is the cheapest per clip; Seedance 2.0 mini is the closest (and 4 s minimum makes the 2-3 s test
impossible there). Seedance's real edge is 12 references, audio and more control, not price.

### T3. Other models that take a reference VIDEO (fal, public prices, 2026-10-29)
| Endpoint | USD | Takes a video + an image? | Note |
|---|---|---|---|
| minimax/h3-max/reference-to-video | 0.05/s | yes (tested) | 480P minimum |
| bytedance/seedance-2.0/mini/reference-to-video | 0.0042-0.007 per 1k tokens | yes (`video_urls`, `@Video1`) | duration 4-15 s |
| fal-ai/wan/v2.2-14b/animate/move | 0.08/s | yes: a driving video moves the character of an image | pose transfer, not a prompt: **no fx, no style**; 480p-720p; worth one test for body-only clips |
| wan/v2.6/reference-to-video | 0.10/s | yes (`video_urls`, 1-3) | 720p and 1080p only, 5 or 10 s: 0.50 |
| fal-ai/ltx-2.3-22b/distilled/reference-video-to-video | 0.0012 per megapixel | yes (video-to-video, `video_strength`) | cheapest by far, but it re-styles the video itself: likely keeps the reference character; test with a low strength |
| kling o1 standard video-to-video/reference | 0.126/s | yes | meant for style/camera reference |
| pixverse c1, grok imagine, kling o1 r2v, bernini-r | 0.005-0.084/s | images only | not a motion reference |
Not yet tested: Wan animate/move (0.08/s, 5 s = 0.40, 3 s = 0.24) and LTX reference-video-to-video. Do T1 first: it halves the cost with no new model.
