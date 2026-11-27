# heroic-vector-style: bài học (từ hai lần thử, 2026-11-27)

| | Bản v01 (bị từ chối, chỉ 1 trong 10 khớp) | Bản v02 (người dùng: "hoàn toàn khớp") |
|---|---|---|
| Khối style | "material told by flat speckle spots, scratches, rivets, plate edges", "a few small flat speckle spots" | "SIMPLE AND CLEAN ... ONE big smooth bold shape ... NO texture, NO scratches, NO speckles, NO fringe, NO thin lines" |
| Mô tả từng con | chi tiết nhỏ: lông vũ, rêu, cuộn dây, "nhiều gai", "fringe" | đếm mảng lớn: bốn cụm lửa, sáu mảng cơ, tám khối đá, sáu gai, ba mũi đinh ba |
| Cỡ nhân vật trong ô | "VERY SMALL inside its cell" (ít điểm ảnh, nét nhòe) | "drawn LARGE, about 80% of the cell height, feet at 92%" |
| Kết quả | rối, nhòe, viền tua, texture lan khắp thân | mảng lớn mịn, viền sắc đều, màu rực |
| Thành công chung | bốn thẻ giới tính, class, hệ, loại; bảng màu riêng từng con; nét viền ngả màu: đều giữ ở cả hai bản | |

## Rút ra
1. **Model làm đúng những gì ta liệt kê.** Nhắc "đốm, vết xước" là nhận về đốm và vết xước khắp thân. Phong cách tham khảo thực chất sạch; muốn sạch thì **cấm** texture và **đếm** số mảng.
2. **Vẽ to thì nét sắc.** Lưới 10 con trên một ảnh: để mỗi con chiếm ~80% chiều cao ô, đừng nhờ vẽ nhỏ rồi thu nhỏ sau.
3. **Bốn thẻ (giới tính, class, hệ, loại) cho phân biệt rõ** nam vạm vỡ, nữ mảnh, thú, quái, công trình mà không cần mô tả dài.
4. **Bảng màu riêng mỗi con** (chủ đạo + nhấn bù + kem trắng) giúp mười con khác nhau rõ mà vẫn cùng phong cách.
5. **Không đổi màu hồng bừa bãi** (`lineup_fix_pink.py --target`) trên lưới có da tím; chỉ làm phẳng nền.
6. **Còn yếu:** Tide Lord (vương miện và vai nhiều mảng nhỏ) vẫn rối nhất ở 60 px; mặt của ba nhân vật nữ khá giống nhau (mặt trái xoan, tai nhọn): nên cho mỗi nữ một kiểu mặt riêng (cằm vuông, tàn nhang, sẹo, mắt to…).

## Lưới 10 nhân vật nữ, hai lần (2026-11-27, `out/heroes/_lineups/heroic_female_test/`)
**Lần 1 (bị từ chối: "chưa có tính unit, chung chung, hình mờ, giống hoạt hình"):** prompt tả "người ngoài đời mặc đồ nghề nghiệp" (4,5-5 đầu, mặt và vải minh họa, hệ chỉ ở màu), vẽ 10 con trong 2560×1440 (~570 px cao mỗi con). Kết quả: như tranh minh họa RPG, mềm nét, class đọc được nhưng không có bản sắc unit.

**Lần 2 (game unit), công thức:**
1. Mở đầu "TEN WOMAN UNITS for a tower defense game ... you must tell her CLASS and her ELEMENT from the silhouette and the colour alone, even as a tiny icon"; mỗi unit **MỘT vật khổng lồ bằng hoặc lớn hơn thân** làm hình bóng, **hệ nằm trong cơ thể và vật đó** (bình thuốc đầy nhớt xanh, đĩa mặt trời, cung là cành cây sống, khiên và vai pha lê băng, rapier có ngọn lửa, đinh ba ngọc trai), tư thế thể hiện class.
2. **Tỉ lệ game 3-3,8 đầu**, đầu to, tay to.
3. **Mặt game đơn giản:** mắt to là mảng sáng, lông mày dày, MỘT biểu cảm, không nét da thật, "no skin texture".
4. **Khối style mới** ("NOT a book illustration and NOT a film cartoon", "razor sharp clean vector edges", "no fabric texture, no folds drawn as thin lines, no soft shading").
5. **Ảnh to hơn 3840×2160** (cùng giá ~$0,021 ở low): mỗi con ~860 px cao thay vì ~570, nét sắc hơn rõ.
Kết quả: mười unit khác nhau rõ về vật định nghĩa và hệ, đọc được ở 60 px. Còn yếu: Shade Nyx có vòng xoáy và tàn lửa nhỏ quanh chân (hơi rối), vài mảnh vụn nhỏ lọt từ ô bên cạnh khi cắt; Queen Seraphine vẫn nhiều mảng ở tóc.
