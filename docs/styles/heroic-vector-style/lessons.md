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

## Lưới 10 nhân vật nữ (2026-11-27, `out/heroes/_lineups/heroic_female_test/`)
Prompt: `prompt-template-female-lineup.txt` (một ảnh, ~$0,022). Cách làm: câu mở đầu liệt kê **mười dáng người khác nhau** (cao mảnh, thấp mập, thể thao, đầy đặn, gầy dẻo, vạm vỡ, nhỏ nhắn, mẹ hiền mập, thanh thoát chân dài, giáp nặng), "every woman has HER OWN face shape and hairstyle, so no two faces look alike", và mỗi đoạn nhân vật nêu hình mặt riêng (mặt góc cạnh cằm nhọn, trái tim, tròn có tàn nhang, hàm vuông...) cùng kiểu tóc bằng số cụm. Thêm "all costumes cover the body fully, no bare midriffs". Kết quả: mặt và dáng khác nhau rõ (khác với lần trộn nam nữ, nơi ba nữ giống mặt), ở 60 px vẫn đọc được phù thủy, pháp sư, sát thủ, cung thủ, người hồi máu, cuồng chiến, trộm, hiệp sĩ, kiếm sĩ, nữ hoàng. Còn yếu: Queen Seraphine (tóc dài và áo choàng nhiều mảng) hơi rối ở 60 px.
