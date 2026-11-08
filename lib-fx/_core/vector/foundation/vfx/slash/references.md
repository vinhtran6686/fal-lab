# Slash: đọc bản gốc (5 mẫu tham khảo)

(Trước đây là `foundation/06-slash.md`.)

Bản gốc: `ref/vfx/slash-trio/dmitry-sarkisov-twitch-fx-2.gif` (2255x1000, 22 frame, 25 fps): ba nhát chém cạnh nhau, cùng lúc: **xanh** (lưỡi liềm),
**hồng** (nhát gãy góc hình chữ L), **vàng** (lưỡi liềm), mỗi nhát có **bóng phản chiếu** dưới sàn. Profile `slash-trio` (6 biến thể: 3 nhát +
3 phản chiếu `*_refl`). Dựng lại: frame 3-5 các lớp chính 0,86-0,96, 0 điểm gãy; trang review Slash Trio
https://claude.ai/artifact/69ermXASZKmFccapxfCYis; showcase [`showcase/slash-trio/`](../../../showcase/slash-trio/). Số liệu: [`data/*_slash-trio.json`](../../data/).
Cùng dạng với `swirl-slash` (2 mẫu) → dạng chém nay có **5 mẫu**.

## 1. Lớp và màu

| Nhát | Thang màu (sáng → tối, luma) | Kiểu phối |
|---|---|---|
| xanh | trắng băng 244 → xanh 172 | thang một họ màu, 2 tông, bước 72 |
| hồng | hồng nhạt 239 → hồng đỏ 145 → đỏ sẫm 117 | thang một họ, 3 tông |
| vàng | kem 243 → cam 207 (mép ngả đỏ cam, dải 20 px) | thang một họ, 2 tông + gradient mép rộng |

Giống xoáy chém: lớp sáng nhất nằm ở **mặt ngoài / phía đầu nét** (phần "lưỡi dao"), lớp tối ở mép trong và đuôi. Viền tối mảnh quanh nét là mép
gradient của lớp, không phải nét riêng. Glow màu chính của từng nhát (xanh, hồng đỏ, đỏ cam).

**Phản chiếu**: cùng hình, **dẹt theo chiều đứng** (cao 87-119 px so với 361-487 px của nhát chính, ≈ 1/4), bảng màu **tối và nhạt đi** (luma
~0,7-0,85 của nhát chính), cùng nhịp thời gian (sinh, đỉnh cùng frame).

## 2. Vòng đời (hình vẽ, px bản gốc)

| | xanh | hồng | vàng | xoáy lửa | xoáy băng |
|---|---|---|---|---|---|
| Hình đầu / đỉnh (diện tích) | 6% | 5% | 6% | 44% | 46% |
| Bùng tới đỉnh | 2 frame | 3 | 2 | 2 | 1 |
| Mỗi mảnh lớn to lên mỗi hình (trước đỉnh) | ×8 | ×1,7-6 | ×7,4 | ×1,6 | ×2,2 |
| Diện tích còn lại mỗi frame sau đỉnh | 0,27 | 0,32 | 0,30 | 0,50 | 0,36 |
| Mảnh lớn còn lại mỗi hình (theo dõi) | 0,22 | 0,27 | 0,23 | 0,30 | 0,29 |
| Đời (tới < 2% đỉnh) | 6 | 8 | 7 | 7 | 6 |
| Số mảnh nhiều nhất | 6 | 6 | 6 | 10 | 5 |
| Mất do lỗ / vết cắt khi co | 64% | 44% | 59% | 50% | 56% |

Luật cho dạng chém (5 mẫu):
1. **Sinh từ một đầu nét và chạy theo đường quét**: hình đầu là một mẩu nhỏ ở điểm bắt đầu cú chém (xanh: cx 0,13 → 0,47 → 0,68; vàng và hồng:
   từ trên xuống, cy 0,08-0,11 → 0,39-0,41 → 0,6-0,72). Nhát chém **dài ra theo đường đi**, không phình từ tâm.
2. **Bùng cực nhanh** (2-3 frame, ×7-8 diện tích mỗi hình) rồi **tàn cực nhanh**: diện tích còn ~0,3 mỗi frame, cả đời chỉ 6-8 frame. Nhát chém là dạng
   ngắn và gắt nhất trong 4 dạng đã đo.
3. **Đầu nét có thể chạy tiếp sau đỉnh diện tích**: ở nhát xanh, khung còn dài ra 2 frame sau khi diện tích đã giảm (cao 361 → 421 → 442 px trong khi
   diện tích 50 000 → 29 000 → 11 000): đầu nét đi tiếp, thân mỏng đi, đuôi tan trước. Nhát hồng giữ khung (486 → 490), nhát vàng co nhẹ (487 → 478):
   không phải luật cứng, là một lựa chọn của designer cho nhát chém dài.
4. **Tàn bằng vết cắt và lỗ**, không chỉ mòn mép: 44-64% phần mất là lỗ / cắt sâu (giống xoáy, khác lửa và pha lê ~15%); thân tách thành 2-6 mảnh
   cong, mỗi mảnh co mạnh (còn ~25% mỗi hình), cuối cùng thành tia lửa nhỏ.
5. **Glow giữ sáng tới cuối**: độ mạnh glow (so với cỡ hình) đi từ ~1 ở đỉnh lên 1,2-2,0 ở các frame tàn: tia và mảnh vụn vẫn rực. Khác với lửa
   phun (glow tắt trước hình). Luật chung: **hiệu ứng ngắn, gắt (chém) giữ glow trên mảnh vụn; hiệu ứng cháy lâu (lửa) cho glow tắt dần**.
6. **Nhịp**: vẽ từng frame trong pha chém; chỉ các frame tia lửa cuối mới giữ 2 frame (từ frame 9-11).

## 3. Bố cục

- Lưỡi liềm (xanh, vàng): **một nét cong dài**, tỉ lệ dài / dày ~6-8, hai đầu nhọn (đầu chém tròn hơn, đuôi kim); các mảng màu sáng xếp thành dải
  chéo dọc thân (vàng: các dải kem cách nhau không đều).
- Nhát gãy góc (hồng): hai đoạn gần thẳng nối bằng một góc ~90°, mép trong có răng nhọn, đầu nét cong lại như móc.
- Mỗi cảnh có **một hình chính**; mảnh phụ chỉ xuất hiện ở pha tàn (tia, mảnh cắt).
