# moon_crane: history

| date | sheet/still | vNN | model | score | verdict | issue | change for next version | requested by |
|---|---|---|---|---|---|---|---|---|
| 2026-11-15 | master | v01 | gpt-image-2 low | 6 | rejected (deleted) | khối vector mảnh, 7 đầu, nét viền mảnh, lộ cơ bắp, giáp vai lệch bên | prompt có số đầu, nét dày | user: chọn concept A |
| 2026-11-15 | master | v02 | gpt-image-2 low | 7 | rejected (deleted) | painterly giàu chi tiết, hơn 6 đầu | user: bớt chi tiết, theo vector | user |
| 2026-11-15 | master | v03 | gpt-image-2 low | 7.5 | rejected (deleted) | vector, ~4 đầu, mặt còn nhiều chi tiết | mặt tối giản | user |
| 2026-11-15 | master | v04 | gpt-image-2 low | 7.5 | rejected (deleted) | mặt tối giản, cánh hạc đổi sang sai bên | theo ảnh mẫu: 3 đầu, nắm đấm lớn | user |
| 2026-11-15 | master | v05 | gpt-image-2 low | 8 | rejected (deleted) | tỉ lệ 3 đầu, vector chắc khối; vũ khí rìu | đổi sang cây thương | user: "hợp lý hơn, đổi vũ khí là cây thương" |
| 2026-11-15 | master | v06 | gpt-image-2 low | 8 | rejected (deleted) | thương; thân chàm gần đen, vàng mảnh, mắt nhỏ, mũi thương tối (thử thu nhỏ 60 px) | sáng hơn, mắt phát sáng, vàng dày, nét viền dày, dáng có sức sống | user: "đồng ý, tạo v07" |
| 2026-11-15 | master | v07 | gpt-image-2 low | 8.5 | rejected (deleted) | màu: bốn họ bão hoà cạnh tranh, giống màu pháp sư mẫu | bảng màu hex: một sắc chủ đạo bốn độ sáng, họ ấm, vàng | user: "màu chưa matching ảnh mẫu" |
| 2026-11-15 | master | v08 | gpt-image-2 low | 9 | approved by user | màu hài hoà; mũi thương to, chắn trăng nhỏ; da hơi sẫm; dáng còn cứng | - | user: "style này ổn nhất và khớp với mong đợi" |
| 2026-11-15 | skill_sweep_spear (video) | take a | h3-max-turbo | 7 | dùng một phần | A đúng, mid và B đúng, C đúng; có 4 khung nhoè và thương bay khỏi khung (khung 47-50) | bỏ khung nhoè, ghép với clip B->C | user: "v01 tốt hơn nhiều" |
| 2026-11-15 | skill_sweep_spear (video) | take b (B->C ghim) | h3-max-turbo | 7.5 | dùng | ghim đầu cuối đúng; 2 khung nhoè; thương hạ chúi | - | user |
| 2026-11-15 | skill_sweep_spear (video) | join | ghép 0 USD | 7.5 | approved by user | một cú nhảy 0,04 s từ quay lưng sang nghiêng | - | user: "Chốt phiên bản đó" |

## 2026-11-15 — pose_horse_stance_v01 (low horse stance, spear across the shoulders)
Pose copied from a user reference frame (single pixel-art frame as `--ref`, design not copied). 2 images (0.0188 + 0.0189 USD); v2 kept, cropped and rescaled to a 10% margin (the model ignored the margin and the 50-degree turn). Body still near-front.

## 2026-11-15 — spin test discarded
A spear spin over the head (A -> mirrored A -> A, 2 clips, 0.06 USD, logged in `out/costs.csv`) was made from ONE reference frame and did not match the user's reference (a gif with several skills, of which only one frame reached us). Files removed; redo from the full reference frames when they are added to `ref/`.

## 2026-11-15 — skill_spin_back (body spin, back to the viewer, from the king reference gif)
Reference: `ref/king/leon-leon-yase2.gif`, character 1 (ready, wind-up, drop and turn, back to the viewer with the weapon hidden, recover, low guard). Two 4 s clips, h3-max-turbo 768P, first frame `master_v08`, prompts in `source/video/prompts/skill_spin_back_t0N.txt`. t01: last frame pinned to `pose_horse_stance_v01`; t02: no last frame. 0.12 USD (`out/costs.csv`). Not accepted yet (user reviews). Known: the body is larger in the first frames than later (the two pinned stills have different fill), one smeared frame at the release, spear visible during the back view.

### skill_spin_back, round 2 (description rewritten with the view and facing of each step)
The first two clips (t01, t02) were removed: the description lacked the viewer's view and facing per step and misplaced the sweep. Re-read of the reference: the weapon travels ONE full circle at waist height (left -> across the front -> right -> behind the body, hidden -> left), the body turns once counter-clockwise on the spot. Two 5 s clips (v2A free ending with the spear down-right, v2B last frame pinned to `pose_horse_stance_v01`), start frame scaled to the same body size as the end frame. 0.15 USD. One smeared frame near the end of v2B. Not accepted yet.

### skill_spin_back, round 3 (two hits with a stop each, no return to rest, turn from the hips)
From the user's review of round 2 (clip A closest): no return to the start pose, every strike has a target, no slash, each hit has a held beat, turns come from the hips and waist. Two 6 s clips from one prompt (`prompts/skill_spin_back_v3.txt`), 0.18 USD. Result: both clips follow the plan (coil, hit on the right with a stop, wind on with the back to the viewer, hit on the left, held end), BUT the model drew a white arc / flash at each strike (frames about 29-35 and 100-104, against the "no slash" line) and held each stop for 1.6-2 s (too long). The gifs sent to the user drop the flash frames and cut the holds (free, the clips are untouched). Not accepted yet.

### skill_spin_back, round 4 (ONE continuous sweep, one target on the right, the head always toward the target)
Round 3 (two hits with a stop) was read by the model as two opposite thrusts and was removed. Round 4: one sweep from the left across the front to the target on the right, the turn continues the same way until the back faces the viewer, the spear comes out on the left and is held. Two 5 s clips (`prompts/skill_spin_back_v4.txt`), 0.15 USD. Result: coil, spin and back view as planned, the head turned right over the shoulder; the model again draws pink/white arcs and blur on the fast frames (about 45-65) and holds the last pose too long (the gifs sent end at frame 100). Not accepted yet.

### skill_spin_back, round 5 (spear level at waist height, no slash)
The user approved round 4 clip 1 as the direction (one continuous sweep) and asked for a level, waist-height sweep and no slash. Round 5 prompt = round 4 + "the spear stays LEVEL, parallel to the ground at waist height" + a longer no-streak sentence. Two 5 s clips (`prompts/skill_spin_back_v5.txt`), 0.15 USD; round 4 clips removed. t01: the spear is level at waist height in front of the crouched body, then the body turns and the back faces the viewer with the spear level; t02: the spear swings down to point at the ground (not level). The model still paints pink/white arcs on the fast frames; a tighter key (alpha ramp from min(R,B)-G = 8 to 53) removes them completely, so the preview gif is clean. Preview: `skill_spin_back_v5_t01_preview.gif` (static frames 51-62 cut). Not accepted yet.
