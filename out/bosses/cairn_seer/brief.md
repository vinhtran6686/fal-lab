# cairn_seer (Thạch Tiên Tri)

style: chunky, body type brawny (`.claude/skills/fal-image/style-chunky.md`)

## Request
User (2026-11-15): thiết kế một nhân vật thuộc hệ pháp sư, dùng phép từ chính cơ thể, không dùng vũ khí. Claude chọn lớp boss, tier XL, vai trò ranged.
Người dùng "tạm chốt" v01, sẽ xử lý từng nhân vật sau.

## Class / size
- Class: boss (`classes/boss.md`), tier XL, `{H}` 120 px, canvas 308x204 @1x
- Role: ranged (phép từ lòng bàn tay; cần `shoot_side` và ảnh `projectile` khi làm tiếp)

## Slots
- `{id}`: cairn_seer; `{body}`: biped; style: chunky brawny
- `{design}` (master v01, **tạm chốt 2026-11-15**): xem `source/design/prompts/master_p01.txt` (nguyên văn).
  Tóm tắt: đại hiền giả khổng lồ bằng các khối đá khắc, vai tảng đá tròn, hai bàn tay mở khổng lồ có biểu tượng tròn và quả cầu lửa phẳng lơ lửng; lõi nứt phát sáng hình xoắn ốc ở ngực và vết nứt sáng chạy xuống tay (phép từ chính cơ thể);
  đầu nhỏ trọc, hai mắt cam phát sáng; thắt lưng dây thừng đồng thau có sash và vòng cổ tay; vài búi rêu trên vai. Không vũ khí.
- **COLOUR PLAN (hex)**: đá xám tím 265° `#2A2433 #4B4259 #7A6F8E #B7AEC6`; họ ấm đồng thau `#8A5A2B #5C3A1C #D1A25A`, rêu `#6E7A3A`; điểm nhấn cam lửa `#FF8A2E / #B8421A / #FFE08A` chỉ ở vết nứt, ký tự, biểu tượng bàn tay, quả cầu và mắt; viền `#2B1E22`.
- `{idle}`: đứng, hai tay gập khuỷu, lòng bàn tay mở hướng ra trước ở ngang hông.

## Điểm chưa đạt đã biết (xử lý sau)
- Tư thế: thân gần như đối diện người xem, hai tay đối xứng; master lớp boss cần nhìn nghiêng ~30 độ, tay xa che một phần.
- Tỉ lệ: đầu nhỏ (khoảng 1/4-1/5 thân) so với "3 đầu"; vài vết nứt trên tay hơi mảnh.

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ⏳ v01 (tạm chốt) | tạm chốt 2026-11-15; làm lại tư thế nhìn nghiêng khi xử lý nhân vật |
| view_front | fal-image | ảnh tĩnh | ⏭ | chưa làm |
| view_back | fal-image | ảnh tĩnh | ⏭ | chưa làm |
| icon, projectile | fal-image | ảnh tĩnh | ⏭ | chưa làm |
| walk_side, walk_down, walk_up, shoot_side, death_side, package | video-sprite | - | ⏭ | ngoài phạm vi thử phong cách |
