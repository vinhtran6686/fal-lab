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

## Lưới 10 nhân vật nữ, ba lần (2026-11-27, `out/heroes/_lineups/heroic_female_test/`)
So từng điểm với 10 ảnh tham chiếu cho thấy ba lần có ba kiểu lệch khác nhau:
| Lần | Việc mình làm | Hậu quả (người dùng nhận xét) |
|---|---|---|
| 1 | tả "người ngoài đời mặc đồ nghề nghiệp", 4,5-5 đầu, 10 con trong 2560×1440 | chung chung, không có tính unit, hình mờ, giống tranh minh họa |
| 2 | **bỏ khối style đã duyệt**, tự viết "game unit, NOT a film cartoon, no folds, no patterns, no soft shading", nữ 3,5-3,8 đầu mảnh | **tệ hơn**: nhạt, phẳng 2-3 tông, mảnh, trắng lợt, thiếu vùng tối, tĩnh |
| 3 | quay lại khối style đã duyệt + **thêm đúng những gì tham chiếu có** (bên dưới) | gần tham chiếu hơn rõ rệt |

**Những gì tham chiếu có mà bản 2 thiếu, và công thức lần 3:**
1. **Thân đặc, nén:** nữ 2,8-3,3 đầu, **đầu to lút giữa đôi vai rộng, gần như không cổ**, thân dày, tay chân dày, tay to, chân ngắn, giày to; nữ tính bằng tóc, lông mi, thắt lưng, váy xòe, không bằng tay chân mảnh.
2. **Tô theo khối 4-5 bậc tông cạnh cứng** ("RICH FORM-FOLLOWING SHADING"), bóng rất sâu ngả tím hoặc xanh, viền sáng, điểm sáng kem bóng loáng trên kim loại, tóc, ngọc.
3. **Nét viền rất dày, dày mỏng thay đổi**, dày nhất ở hình bóng.
4. **Màu rực, tối sâu,** ấm bên sáng, lạnh bên bóng; cấm "pastel" và "washed-out whites"; mỗi bảng màu ghi màu bóng thật sâu (`deep shadow #...`).
5. **Mặt đặc điểm to, nặng:** lông mày dày, miệng to, hàm hoặc má, một biểu cảm mạnh.
6. **Chi tiết vừa phải:** mép tấm giáp, dây đai, vài đinh tán tròn, tua, gấu váy rách bằng mảng lớn (đừng cấm hết chi tiết).
7. Giữ **một vật khổng lồ** và **hệ nằm trong cơ thể và vật đó**; ảnh 3840×2160.
**Bài học:** khi một khối style đã được duyệt thì chỉ thêm vào, không viết lại. "Sạch, đơn giản" không có nghĩa là bỏ tô khối, nét dày và tương phản.
