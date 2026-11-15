# moon_crane (Hạc Nguyệt Phủ Sĩ)

style: chunky (`.claude/skills/fal-image/style-chunky.md`)

## Request
User (2026-11-15): nhân vật nam, cầm vũ khí, có giáp, phong cách mới lạ và có tính thẩm mỹ, để thử phong cách và thử vệt chém của vũ khí hạng nặng.
Chạy `/fal-image --creative` (ý tưởng ngắn của người dùng). Mẫu tham khảo của người dùng: các nhân vật hoạt hình chắc khối kiểu tower defense (tỉ lệ khoảng 3 đầu, nét viền nâu đậm, màu phẳng 3-4 tông) và một số concept painterly.

## Concepts offered (2026-11-15)
- A. Hạc Nguyệt Phủ Sĩ: thanh lịch, giáp vai cánh hạc khổng lồ, vũ khí vành trăng khuyết. **Chọn.**
- B. Thanh Đồng Cự Phủ: nặng, mũ mặt nạ có mào, giáp đồng gỉ, hoạ tiết nghi lễ.
- C. Sa Phủ Vệ: giáp vảy phân đoạn, lapis và cát, vũ khí cong lai loan đao.
Người dùng chọn A, sau đó đổi vũ khí rìu -> cây thương (nhìn hợp phong cách hơn).

## Class / size
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 176x140 @1x
- Role: melee
- **Ngoại lệ so với skill, theo yêu cầu người dùng**: tỉ lệ khoảng 3 đầu (skill mặc định 3,5-4,5), nắm đấm to bằng mặt; vẫn nghiêm, không dễ thương.

## Slots
- `{id}`: moon_crane; `{body}`: biped; style: chunky
- `{design}` (master v08, **người dùng chốt 2026-11-15, "style này ổn nhất và khớp với mong đợi"**): xem `source/design/prompts/master_p08.txt` (nguyên văn).
  Tóm tắt: chiến binh nam ~3 đầu, mặt tối giản (mày dày, hai mắt vàng phát sáng, râu một mảng), búi tóc cao dây đỏ gạch; giáp vai cánh hạc ngà ở vai bên phải ảnh, vai trái tròn nhỏ;
  giáp ngực xanh slate với một chim vàng lớn, thắt lưng nâu khoá vàng, dải đỏ gạch, vạt áo rách mũi; găng có dải vàng dày và trăng khuyết vàng;
  một cây thương quá cỡ (cán nâu cao hơn người, mũi thương lá bạc xanh nhạt, chắn trăng khuyết vàng, tua đỏ gạch, một đá đỏ cam) cầm bằng tay bên trái ảnh, tay kia nắm đấm.
- **COLOUR PLAN (hex)**: xanh slate 210° `#26394F #3F5F80 #7FA0C0 #BBD3E6`; họ ấm (da, da thuộc, cán) `#C98A55 #8E5A3A #E8B684 #6A4430 #4A2E22`; vàng `#D6A03A #8A5E1A #F2D678` (chỉ dải dày);
  ngà `#EFE2BE / #BFAE8A` chỉ cho cánh hạc; mũi thương `#DDE9F2 / #7FA0C0`; đỏ gạch `#B5472F` nhỏ; mắt `#FFE9A6`; viền `#2B1E22`.
- `{idle}`: đứng thẳng chân rộng, đầu nghiêng ~8 độ, vai trái hạ ~5%, thương nghiêng ~8 độ, đuôi cán chạm đất.
- `{skills}`: chưa chọn. Hướng thử: đâm thẳng (thương), quét ngang bằng cán, bổ từ trên xuống.

## Lưu ý thiết kế (bài học riêng của nhân vật này, bài học chung đã vào `style-chunky.md`)
- Mô hình ảnh bỏ qua yêu cầu "màu trầm"; hài hoà đến từ số họ màu và bảng hex, không từ giảm bão hoà.
- Cánh hạc đọc rõ nhất ở 60 px; mũi thương và mắt phát sáng là điểm nhìn. Thương dài chiếm ~90% chiều cao ảnh nên phải thu nhỏ khi ghép vào ô.

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v08 | user chốt 2026-11-15, style chunky |
| icon | fal-image | ảnh tĩnh | ⏭ | chưa làm |
| pose_skill_* | fal-image | ảnh tĩnh | ⏭ | chưa chọn kỹ năng |
| run_side, attack_side, death_side, pose_respawn, respawn_side, levelup_side, package | - | - | ⏭ | ngoài phạm vi thử phong cách |
