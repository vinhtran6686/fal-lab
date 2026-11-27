# heroic-vector-style: đặc tả phong cách

Phong cách chọn thêm của `fal-image`, nghiên cứu từ 10 ảnh tham khảo của người dùng (`style-board.md`) và đã được người dùng duyệt trên bản thử v02 (2026-11-27, `out/enemies/_lineups/style_test_heroic_vector/`). **Không thay `style-chunky.md`**: chunky vẫn là mặc định; skill chỉ dùng phong cách này khi người dùng yêu cầu "style heroic" (xem `.claude/skills/fal-image/SKILL.md`). Cách viết prompt: `prompt-recipe.md`. Bài học: `lessons.md`.

## 1. Nguyên tắc số 1: đơn giản và sạch
Mỗi phần cơ thể và trang phục là **MỘT mảng lớn mịn**, viền gọn sắc, mảng màu phẳng lớn. Tối đa 6 mảng trong một bộ trang phục. Tóc, râu, lông, lửa, áo choàng là **3-5 cụm lớn mịn** có đầu nhọn. Chi tiết bề mặt chỉ là vài mảng điểm sáng lớn và vài đinh tán tròn. **Không** texture, nét gạch, vết xước, đốm, viền tua, chi tiết nhỏ, nét mảnh. Nhân vật được vẽ **to** (khoảng 80% chiều cao ô) để model giữ nét sắc.

## 2. Thân hình theo giới tính, class, loại (viết riêng cho từng nhân vật, không chép đoạn của con khác)
| Nhóm | Số đầu | Hình dáng |
|---|---|---|
| Nam chiến binh, đấu sĩ, tank, thủ lĩnh thấp bè | 2,5-3 | đầu to, ngực và vai khổng lồ, nắm đấm bằng hoặc lớn hơn mặt, chân rất ngắn, râu hoặc ria lớn, mặt gầm hoặc cười nhe răng |
| Nam già, pháp sư hoạt họa | ~3 | mặt caricature (miệng há, râu dài), lưng gù |
| Nữ anh hùng, pháp sư, cung thủ, sát thủ | 4-5 | mảnh, eo thắt, chân dài, tóc dài bay thành cụm lớn, áo choàng tung, mặt tự tin có lông mi; không chibi |
| Sát thủ (nam hoặc nữ) | 4-4,5 | gọn cơ bắp, người nghiêng về trước, khăn bịt mặt |
| Thủ lĩnh cao | ~4,2 | đầu nhỏ ~22% chiều cao, chân ~45%, vai nhọn, eo hẹp, đứng thẳng ưỡn ngực, không bụng |
| Quái, nguyên tố, công trình | 2,5-3 | thân làm từ vật chất của hệ (khối đá, ogre, nhớt), tay hoặc nắm đấm lớn nhất |
| Thú | tự nhiên | một đặc điểm lớn (bờm, sừng, tinh thể), giải phẫu đúng loài |
Mỗi nhân vật có **một thứ khổng lồ** (khiên, rìu, cung, mũ, vai giáp, nắm đấm). Hình bóng phải đọc được khi tô đen và ở 60 px.

## 3. Thẻ mô tả bắt buộc
Mỗi nhân vật mở đầu bằng bốn thẻ theo thứ tự: **GIỚI TÍNH** (nam, nữ, không giới tính cho công trình), **CLASS** (cận chiến, tank, sát thủ, cung thủ, ném lao, pháp sư, hỗ trợ, thủ lĩnh, thú), **HỆ** (lửa, băng, sét, độc, cây, đất, nước, gió, ánh sáng), **LOẠI** (người, thú, quái, công trình, linh hồn). Ví dụ: "SIR BRANT, male, tank paladin, light, human: ...". Cùng bốn thẻ này vào `brief.md` hoặc `meta.json`.

## 4. Nét viền và tô
- Nét viền dày, đều tay, góc bo tròn, **đậm nhưng ngả theo màu chủ đạo của chính nhân vật** (xanh tím đậm cho nhân vật xanh, nâu tím cho cam, lục tối cho lục), dày hơn ở ngoài, mỏng hơn bên trong.
- Tô theo ô **3 tông cạnh cứng, tương phản mạnh**: bóng đậm ngả màu, nền, sáng; cộng một mảng điểm sáng **kem trắng** và một mảng viền sáng (rim) ở cạnh nhận sáng. Không gradient, không airbrush, không quầng sáng mềm, không mờ.

## 5. Màu
**Mỗi nhân vật một bảng màu riêng:** một màu chủ đạo **bão hòa** (ba giá trị hex: bóng, nền, sáng) + một màu nhấn **gần bù** + kem trắng cho điểm sáng. Cặp thường gặp: xanh dương + vàng, đỏ cam + xanh ngọc, nâu đất + turquoise, xanh ngọc + san hô, xanh lá + cam, xanh trời + cam, tím + vàng chanh, xanh băng + cam, nâu xám + cyan, xanh biển + cam san hô. Không dùng magenta hoặc hồng trên chủ thể (nền là #FF00FF bị khóa bỏ); tím phải là tím rõ.

## 6. Mặt và tính cách
Mọi mặt có biểu cảm bằng vài hình đậm: lông mày góc nặng, **một** biểu cảm (gầm nhe răng, cười toe, cười nhếch, râu ria lớn), mắt sáng; nữ có vài nét lông mi. Dữ pha hài hoặc tự tin; không phải mascot dễ thương, không mặt trống.

## 7. Hiệu ứng
Không vẽ hiệu ứng lớn trong ảnh nhân vật: tối đa một hình phẳng gắn vào thân hoặc vũ khí (một ngọn lửa trên trượng, một bông hoa). vfx vẽ riêng (`lib-fx`).

## 8. Kiểm duyệt (đạt khi nhìn thấy đúng)
- [ ] Tỉ lệ đúng nhóm ở §2; một thứ khổng lồ; nắm đấm lớn ở nam vạm vỡ.
- [ ] Mảng lớn mịn, không texture, không viền tua, không nét mảnh.
- [ ] Nét viền dày, đều, ngả màu chủ đạo; tô 3 tông cạnh cứng, điểm sáng kem trắng.
- [ ] Mỗi con một cặp màu chủ đạo và nhấn bù, bóng không đen thuần.
- [ ] Mặt có biểu cảm.
- [ ] Phép thử thu nhỏ 60 px và 120 px: hình bóng, vật khổng lồ và màu còn đọc.
- [ ] Không hồng trên chủ thể (khóa nền sạch).

## 9. Giới hạn đã biết
Model bỏ qua phần trăm kích thước và vị trí; kiểu nhìn nghiêng dễ xoay chính diện; nhân vật nhiều mảng nhỏ (vương miện, vai nhiều vây) vẫn rối nhất ở 60 px; áo giáp nữ dễ bị vẽ hở (viết "plain fitted" nếu cần kín hơn); các giới hạn của `style-chunky.md` §9 vẫn áp dụng.
