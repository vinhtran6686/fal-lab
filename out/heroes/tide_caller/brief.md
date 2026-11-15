# tide_caller (Triều Pháp Sư)

style: chunky, body type slender (`.claude/skills/fal-image/style-chunky.md`)

## Request
User (2026-11-15): thử nhân vật nữ với style chunky. Chọn pháp sư dùng trượng, bảng màu xanh ngọc biển + cát gỗ + san hô, size M.
Concept do Claude soạn từ lựa chọn đó (ba concept ban đầu: A Thiết Chùy Nữ Tướng, B Hải Cung Thủ, C Đăng Y Sư; người dùng chọn "pháp sư" + "trượng" + palette B).

## Class / size
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 176x140 @1x
- Role: ranged (pháp sư; cần `shoot_side` và ảnh `projectile` khi làm tiếp; chưa chọn kỹ năng)

## Slots
- `{id}`: tide_caller; `{body}`: biped; style: chunky, body type **slender** (~3,5 đầu)
- `{design}` (master v02, **người dùng chốt 2026-11-15**): xem `source/design/prompts/master_p02.txt` (nguyên văn).
  Tóm tắt: pháp sư nữ nghiêm nghị, thân mảnh, eo thắt, áo choàng xanh ngọc dáng chuông xoè, tay áo rộng, viền gấu sóng lượn bằng các mảng lớn kem, đai da nâu với dải san hô;
  mặt tối giản (mày mảnh, hai mắt vàng nhạt phát sáng, môi san hô một mảng), bím tóc dày nâu buộc dây san hô; giáp vai vỏ ốc anh vũ xoắn màu kem ở vai bên phải ảnh;
  trượng gỗ trôi sông cao hơn đầu, đầu trượng là vỏ ốc xoắn ôm ngọc trai phát sáng và cành san hô, cầm bằng tay bên trái ảnh; tay kia thả lỏng.
- **COLOUR PLAN (hex)**: xanh ngọc biển 185° `#1B4650 #2C7C84 #6DB8B4 #C4E6DC`; họ ấm (da, da thuộc, gỗ, bracer, cán) `#C98A55 #8E5A3A #E8B684 #7A4E31 #4B2F20`; kem `#EFE2BE / #BFAE8A` chỉ cho vỏ ốc và viền gấu;
  san hô `#E2674B / #A8432F` chỉ cho dải áo, dây buộc tóc, cành san hô; ngọc trai và mắt `#FFF1C9`; viền `#2B1E22`.
- `{idle}`: đứng cân bằng, trọng lượng dồn một chân, đầu nghiêng ~8 độ, vai trái hạ ~5%, trượng nghiêng ~8 độ.
- `{skills}`: chưa chọn. Hướng thử: gọi sóng (vùng nước), tia nước, hồi phục bằng ngọc trai.

## Lưu ý thiết kế (bài học riêng của nhân vật này; bài học chung đã vào `style-chunky.md` mục "Body types")
- v01 dùng nguyên đoạn thân "vạm vỡ, nắm đấm khổng lồ" của nhân vật nam nên ra thân trung tính; v02 viết riêng thân mảnh nữ tính.
- Thân mảnh có xu hướng trông minh hoạ hơn là chunky (viền mỏng hơn, da có đổ bóng mềm); khi làm các ảnh kế tiếp nhắc "viền dày, mảng phẳng, mặt vài nét".
- Trượng cao chiếm ~90% chiều cao ảnh, phải thu nhỏ khi ghép vào ô.

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v02 | user chốt 2026-11-15, style chunky slender |
| icon | fal-image | ảnh tĩnh | ⏭ | chưa làm |
| projectile | fal-image | ảnh tĩnh | ⏭ | pháp sư tầm xa |
| pose_skill_* | fal-image | ảnh tĩnh | ⏭ | chưa chọn kỹ năng |
| run_side, shoot_side, death_side, pose_respawn, respawn_side, levelup_side, package | - | - | ⏭ | ngoài phạm vi thử phong cách |
