# VFX loại "explosion" (nổ / phun từ đất)

Hiệu ứng bùng lên tại một điểm (thường ở chân, trên mặt đất) rồi cháy, tan tại chỗ. Mẫu đã dựng lại: `element-trio`
(`ref/vfx/element-trio/`): **lửa phun**, **Arcane** (pha lê tím), **Toxic** (khói độc), cả ba 10/10. Profile
`lib-fx/_core/vector/profiles/element-trio.json`; showcase [showcase/element-trio](../../../showcase/element-trio/); trang review Element Trio
https://claude.ai/artifact/6Vw3supbrvPSULNoNsxCzn. Số liệu: [`data/*_element-trio.json`](../../data/). Chưa có bộ sinh.

## 1. Lớp và màu

| | Lớp (dưới → trên) | Lớp đặc biệt | Thang màu |
|---|---|---|---|
| lửa phun | cam, vàng | glow cam (làm nhoè hình, tắt dần) | vàng 207 → cam 162 (luma); **vàng ở chân**, cam lên trên |
| Arcane | màn cánh trong mờ (độ đục ~0,45), tím nhạt, cánh xanh | glow tím | hai sắc cùng độ sáng + màn mờ |
| Toxic | bóng tối trong mờ, bạc hà | vòng sáng dưới đất | lõi sáng + bóng tối |

Tông sáng nhất = phần nóng / nhiều năng lượng nhất: sâu trong khối, ở **gốc phun**. Chi tiết: [../../01-design-style.md](../../01-design-style.md) §1, §3.

## 2. Vòng đời

| | lửa phun | Arcane | Toxic |
|---|---|---|---|
| Hình đầu tiên (so với đỉnh) | 4% (357 px) | 46% | 10% |
| Bùng tới đỉnh | 3 frame | 4 | 1 |
| Giữ đỉnh trước khi vỡ | 3 frame | 0 | 0 |
| Diện tích còn lại mỗi frame sau đỉnh | **0,81** (cháy lâu) | 0,55 | 0,55 |
| Đời (tới < 2% đỉnh) | 21 frame | 12 | 9 |
| Số mảnh nhiều nhất | 36 | 76 | 23 |
| Bắt đầu on twos | frame 14 | 8 | 10 |
| Mảnh mới sau đỉnh | 11 (tàn bay lên) | 1 | 3 |

Nguồn và phần theo dõi từng mảnh: [../../02-animation.md](../../02-animation.md).

## 3. Luật của loại nổ / phun

- **Sinh ở chân, giữa** (cy ≈ 0,8-0,86 khung đỉnh); hình đầu nhỏ. Bung **ngang trước, cao sau**; Arcane bung ngang quá tay (115%) rồi thu lại
  (nhịp "bật"); tâm khối đi lên dần.
- **Bố cục ở đỉnh**: 2-5 lưỡi chính, xoè 57-165°, cách nhau ~36°, lệch khỏi trục đứng; thứ bậc dài 1 / 0,7-0,9 / 0,3-0,6; thứ bậc mảnh to / vừa / nhỏ.
- **Tàn tại chỗ**: mỗi mảnh co mỗi hình vẽ (lửa còn ~83%, Arcane, Toxic ~50%), sứt ra 1-2 mảnh nhỏ, không bay (trừ tàn lửa bay lên);
  khung bao giữ nguyên tới 3-4 frame cuối mới sụp về chân.
- **Mòn mép**: lửa, pha lê mòn đều từ mép (~84-86%, ~1 px / hình); khói độc mòn mép và mở lỗ (63 / 37%). Chân mòn chậm hơn đỉnh (lõi nóng ở chân).
- **Ánh sáng**: glow **tắt trước hình** (lửa: 1 tới frame 12, 0 từ 19, hình còn tới 22); lớp sáng mờ dần ở 30% cuối; khác hẳn nhát chém (glow giữ
  tới cuối).

Nguồn: [../../05-birth-erosion-composition.md](../../05-birth-erosion-composition.md).

## 4. Bẫy khi đọc bản gốc (đã gặp)

- Glow cố định làm frame cuối sáng gấp 5-8 lần → dùng glow `blur` × độ mạnh từng frame.
- Mảnh Arcane mờ dần bị mất → lớp theo độ đục + độ đục từng frame, màn trong mờ.
- Viền xanh tối quanh Toxic là vệt phóng to 3x của GIF nhỏ bị đo thành gradient → luật 1,5 px ảnh gốc.

Chi tiết: [../../03-reading-references.md](../../03-reading-references.md).

## 5. Việc tiếp theo

Bộ sinh `eruption` (kế hoạch G2 trong [../../04-generation-spec.md](../../04-generation-spec.md)): sinh 2-3 hiệu ứng mới (vd. phun băng, phun
điện) từ luật trên, đặt cạnh bản gốc để user chấm. Các dạng nổ khác (nổ tròn, sóng xung kích) cần 2-3 GIF tham khảo mỗi dạng trước.
