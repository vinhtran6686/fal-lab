# dragon_sabre (Thanh Long Đao Khách)

style: chunky, body type agile athletic (`.claude/skills/fal-image/style-chunky.md`)

## Request
User (2026-11-15): nhân vật nam trẻ, dùng đại đao, màu chính xanh dương đậm, form nhanh nhẹn và cơ bắp cân đối; còn lại Claude sáng tạo.
Người dùng nhận xét v01 "hơi chibi quá"; chốt v03.

## Class / size
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 176x140 @1x
- Role: melee

## Slots
- `{id}`: dragon_sabre; `{body}`: biped; style: chunky, body type **agile athletic** (~5-6 đầu thực tế, xem bài học tỉ lệ trong `style-chunky.md`)
- `{design}` (master v03, **người dùng chốt 2026-11-15**): xem `source/design/prompts/master_p03.txt` (nguyên văn).
  Tóm tắt: nam trẻ nhanh nhẹn, cơ bắp cân đối, mặt gọn (mày góc cạnh, hai mắt vàng nhạt phát sáng, nụ cười một nét, không râu), tóc đuôi ngựa cao buộc dây đỏ, băng đô kem hai đuôi dài;
  một tay trần có băng cổ tay kem, tay kia tay áo xanh với giáp vai hình vảy xếp lớp; khăn quàng lót kem bay thành một mảng lớn sau lưng (nét riêng); áo khoác cổ cao, dải thắt lưng kem với hai đuôi đỏ, quần rộng bó cổ chân, giày nâu quấn dây;
  đại đao cán gỗ dài hơn người, lưỡi cong bản rộng bằng thép sáng, đầu rồng phẳng cobalt và kem ngậm gốc lưỡi, tua đỏ; cầm bằng tay bên trái ảnh.
- **COLOUR PLAN (hex)**: cobalt 228° `#162052 #2E45A0 #6482D6 #B5C8F5`; họ ấm: da `#D69A63 #9A5F3C #F0C08A`, giày `#A8764A`, gỗ `#7A4E31 #4B2F20`; kem `#EFE2BE / #BFAE8A`; thép `#C9D3E0 #8A97AB #EAF1F8` chỉ cho lưỡi;
  đỏ thẫm `#D8353A / #8F1F25` chỉ ở dây tóc, tua, đuôi dải thắt lưng; mắt `#FFE9A6`; viền `#241B2B`.
- `{idle}`: đứng nhẹ, trọng lượng dồn chân trái, đầu nghiêng ~8 độ, đao nghiêng ~8 độ, đuôi cán chạm đất.
- `{skills}`: chưa chọn. Hướng thử: chém ngang bằng đại đao (3 pose A/B/C), bổ từ trên xuống.

## Lưu ý thiết kế
- v01 (xin 3,5 đầu, "đầu lớn 28%", "khối hạt đậu") ra dáng chibi; v02 (xin 5 đầu, đầu 20%) ra ~7 đầu và mất chunky; v03 (xin 4,3 đầu, đầu 24%, viền "rất dày") ra ~6 đầu và được chốt.
  Bài học chung đã vào `style-chunky.md` (mô hình vẽ cao hơn số đầu xin 1-2 đầu với thân mảnh/cân đối).
- Lưỡi đao và khăn còn chuyển sắc nhẹ; mũi đao chỉ cách mép trên ~4%; đao + người chiếm ~94% chiều cao ảnh nên phải thu nhỏ khi ghép vào ô.

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v03 | user chốt 2026-11-15, style chunky agile athletic |
| icon | fal-image | ảnh tĩnh | ⏭ | chưa làm |
| pose_skill_* | fal-image | ảnh tĩnh | ⏭ | chưa chọn kỹ năng |
| run_side, attack_side, death_side, pose_respawn, respawn_side, levelup_side, package | - | - | ⏭ | ngoài phạm vi thử phong cách |
