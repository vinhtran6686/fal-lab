# Brief: hero `centaur`

| Field | Value |
|---|---|
| Request | Thiết kế 1 nhân vật Hero, người ngựa, vũ khí liềm, màu chủ đạo xám, viền tím, liềm hợp tông xám nhưng nổi bật khỏi màu da; đứng yên dựng đứng liềm; di chuyển cầm cán liềm 1 tay; (chạy/tấn công) liềm xéo giữa người cầm 2 tay; vibe metal, giáp cơ bản không quá nhiều, đặc biệt có găng tay |
| Mode | default (master checkpoint) |
| Class / level | hero; no hero class yet: enemy Level 1 conventions (canvas 256x128 at 1x, body 138 px @2x, standard views, style of format.md §1 from 2026-10-16) |
| Approved master | `design/master_v03.png` = idle pose (user 2026-10-16: "master_v03 ổn") |

## Slots
- `{design}`: a heavy-metal centaur warrior: the upper body of a broad-shouldered man rising from the body of a strong four-legged horse, top-heavy with huge shoulders and arms, a small head and a compact horse body on sturdy short legs with big hooves; ash-grey skin and a darker charcoal-grey horse coat and tail; a few pieces of dark gunmetal armour only: one big spiked shoulder plate, a simple chest strap and plates on the horse's chest; large heavy steel gauntlets on both hands (a key feature); a long war scythe with a dark iron haft and a bright polished steel curved blade with a cold blue-white edge, clearly brighter than the grey skin; the outlines are dark purple and a small violet accent glows in the eyes and on the blade's edge
- `{poses}`: idle: the scythe planted upright beside him, held by the haft; walk: haft held in one hand; run: scythe held diagonally across the body with both hands (user confirmed)
- `{attack}`: a two-handed horizontal scythe sweep from behind to the front, the upper body twisting with the swing, the horse front legs rearing slightly (user approved 2026-10-16)
- `{death}`: the horse buckles on its front legs and topples onto its side, the scythe falls to the ground beside him, the violet eye glow goes out (user approved 2026-10-16)
- Approved poses: idle `design/master_v03.png`, run `design/pose_run_v01.png` (blade turned inward), attack `design/pose_attack_v01.png`, death `design/pose_death_v04.png`
- Outline: the user asked for purple outlines: this overrides the default "dark shade of the neighbouring colour"
