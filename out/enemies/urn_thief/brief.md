# urn_thief (Hũ Tặc)

style: chunky, body type brawny (`.claude/skills/fal-image/style-chunky.md`)

## Request
User (2026-11-15): thử style chunky với một class khác, "cho bạn sáng tạo". Claude chọn lớp enemy (đi bộ), tier S, vai trò cận chiến.

## Class / size
- Class: enemy (`classes/enemy.md`), tier S, `{H}` 40 px, canvas 92x80 @1x
- Role: melee

## Slots
- `{id}`: urn_thief; `{body}`: biped; style: chunky brawny (~3 đầu)
- `{design}` (master v01, **người dùng chốt 2026-11-15 "chốt nhân vật này luôn"**): xem `source/design/prompts/master_p01.txt` (nguyên văn).
  Tóm tắt: goblin trộm bụng phệ, đầu to tai nhọn khổng lồ, mặt tối giản (mày dày, hai mắt xanh chanh phát sáng, mũi to, miệng một mảng có vài răng), đầu trọc;
  áo choàng tím mận rách mũi, áo vest vá, thắt lưng da nâu khoá gỉ; **hũ đất nung khổng lồ nứt đeo sau lưng, mủ độc xanh chanh rỉ qua vết nứt** (nét riêng của hình bóng);
  cầm một con dao phay sắt quá cỡ có mẻ ở tay bên trái ảnh, tay kia nắm đấm có vuốt.
- **COLOUR PLAN (hex)**: tím mận 285° `#3A2742 #5C3F68 #8B6BA0 #C2A8D0` (áo choàng, vest); họ ấm: da ô-liu `#7C8A4A #55612F #A9B66B`, da thuộc `#6A4430 #4A2E22`, hũ đất `#B5643A #7E3F22 #D98A58`;
  sắt trung tính `#8A8C8E #5B5E62 #C9CBCC`; điểm nhấn xanh chanh `#C9E04A / #86A01F` chỉ ở mắt và mủ; viền `#2B1E22`.
- `{idle}`: đứng cân bằng, đầu cúi ~8 độ, dao cầm thấp.

## Điểm chưa đạt đã biết (người dùng chấp nhận)
- Tư thế trông hơi bước chéo về góc dưới bên phải (thân gần đối diện người xem), thay vì nhìn nghiêng ~30 độ; chỉ thấy một chân.
- Lưỡi dao chạm gần mép dưới (~5%, yêu cầu 8%); miếng vá còn đường khâu nhỏ; hũ đất bão hoà hơn bảng màu.
- Cần xử lý khi làm `view_front` / `view_back`: nhắc "nhìn thẳng / từ phía sau", hũ ở lưng hiện trọn ở view_back.

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v01 | user chốt 2026-11-15, style chunky |
| view_front | fal-image | ảnh tĩnh | ⏭ | chưa làm |
| view_back | fal-image | ảnh tĩnh | ⏭ | chưa làm |
| icon | fal-image | ảnh tĩnh | ⏭ | chưa làm |
| walk_side, walk_down, walk_up, attack_side, death_side, package | video-sprite | - | ⏭ | ngoài phạm vi thử phong cách |
