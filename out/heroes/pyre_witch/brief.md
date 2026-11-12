# pyre_witch (Phù Thủy Lửa)

## Request
User (2026-11-12): nhân vật mới, phù thủy không dùng vũ khí, dùng năng lượng trong cơ thể. Trạng thái thay đổi: **đôi mắt** (hoá đỏ khi cast) và **đôi tay** (gồng skill); áp fx lên các pose đó. Phù thủy lửa, trang phục kiểu váy ôm cao cổ tay dài xẻ tà (tả đặc điểm, không gọi tên nhân vật), tóc dài, da trắng, bảng màu đỏ đen tím, ác và ma quái, hoang dã hơn, hợp style `ref/asra`.
Chạy `/fal-image --creative`.

## Concepts offered (2026-11-12)
- A. Huyết Nhãn (cao gầy, cổ tay quấn vải), B. Phù Thủy Tro (vai rộng, bao tay rune), C. Phù Thủy Rừng Sâu (sừng hươu). Người dùng không chọn, tự đặt: phù thủy lửa váy đỏ, tóc dài, da trắng, đỏ đen tím.

## Class / size
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 176x140 @1x
- Role: ranged (chưa làm `shoot_side`, `projectile`)

## Slots
- `{id}`: pyre_witch
- `{body}`: biped
- `{design}` (**master v12 được duyệt 2026-11-12**): feral sinister fire witch, adult woman; wild long dark blue-violet-black hair in many thin jagged locks; pale white skin; simple face with heavy brow, two light-grey eye slits (kept light so a red fx on the eyes reads) and a cruel sneer with one small fang; dark crimson ragged dress, high jagged collar, long sleeves with torn cuffs, skirt down to the shoes with a deep side slit showing one bare pale leg, black high-heeled shoes, wide black belt with one violet sigil; slender hands with long pointed black nails and two thin violet vein lines each; no weapon. Thick outlines, flat tones.
- Lịch sử: v01-v03 (kiểu vẽ thật, cao 5 đầu) bỏ; v04-v06 (ác, ma quái) bỏ; v07-v10 (chuyển sang style repo: chắc, viền dày, hoang dã); v11 thanh mảnh hơn 30% từ v09; **v12** tay thanh mảnh móng đen, chân trần + giày, váy dài tới giày xẻ lộ một chân, lọn tóc mỏng hơn.
- Điểm yếu v12: tỉ lệ cao hơn style (~4,5-5 đầu); giày cao gót nhỏ ở cỡ 60 px. Chấp nhận theo lựa chọn của user.
- `{idle}`: đứng thẳng, hai chân sát nhau, tay gần camera nâng ngang eo lòng bàn tay mở, tay kia buông (gần nhìn thẳng, xoay ~20° sang phải).
- `{skills}`: **Hoả Ấn** (hai tay gồng, lửa chạy từ cổ tay ra đầu ngón, rồi đẩy quả cầu/sóng lửa; dùng ngôn ngữ `charge_fire` của lib-fx). Skill mắt (Nhãn Hoả) để sau.

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v12 | chốt 2026-11-12 |
| idle_side | Puppet Kit | loop | ⏳ p01 | plate AI (ERASE) + đa giác đầu/tay; thở, đầu, tay nâng nổi, tóc và gấu váy đung đưa; `source/rig/`, `frames/idle_side/`; 0 USD |
| icon | fal-image | ảnh tĩnh | ❌ | |
| projectile | fal-image | ảnh tĩnh | ❌ | quả cầu lửa (ranged) |
| shoot_side | Puppet Kit / pose A-B | one-shot | ❌ | |
| pose_skill_hoa_an_p1, p2 | fal-image | ảnh tĩnh | ❌ | gồng và tung, phương pháp pose A/B |
| skill_hoa_an_side | ghép khung ($0) | one-shot | ❌ | + fx lửa trên hai tay |
| run_side, death_side, respawn_side, levelup_side, package | - | - | ⏭ | chưa làm |
