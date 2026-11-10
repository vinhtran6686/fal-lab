# Milestone 02: Single Rising Diagonal Slash, Holy Commander (KẾ HOẠCH NHÁP)

> Trạng thái: **nháp, chờ user duyệt kế hoạch + chi phí**. Chưa gọi API. Quyết định gốc: `docs/milestone-01-advisor-closeout.md` §4-5,
> `docs/decision-log.md`.

## 0. Mục tiêu và phạm vi

Một nhát **chém vuốt từ dưới lên** của Holy Commander (master v07). Nhìn ngang, hướng phải, **không xoay thân**, **không có nhát thứ hai**. Mục tiêu:
lấy Root/Tip, **dùng lại SweepFrame** cho trajectory thứ hai, tạo VFX chỉnh được và ghép vào nhân vật.

Không làm: Cross / Double Slash, xoay hông lớn, Editor hay hệ thống tổng quát mới, sửa core (kể cả lỗi `hash()`), promote vào core.

## 1. Đòn (đề xuất)

- Đường mũi kiếm trên màn hình: **trái-dưới → phải-trên**, tức từ thấp phía sau lên cao phía trước. Ngược hướng và khác vùng với M01 (trái-trên → phải-dưới),
  nên là một trajectory khác thật sự.
- **P1, chuẩn bị:** chân giang rộng, cắm chỗ, gối khuỵu. Hai tay cầm chuôi ở hông sau; lưỡi thấp phía sau, mũi gần đất sau chân sau; **lưỡi ở trước áo
  choàng, thấy rõ**; thấy mặt.
- **P2, kết thúc:** cùng chỗ đặt hai bàn chân, trọng tâm dồn chân trước, thân hơi đổ về trước. Hai tay ngang đầu phía trước, khuỷu hơi gập; lưỡi chĩa
  **lên phía phải-trên** (~50°), mũi trong khung.
- Clip 3 s, các beat như M01:
  1. giữ P1 ngắn, gồng;
  2. chém (0,4-0,9 s): chân sau đạp → hông → vai → tay kéo chuôi lên; lưỡi đi sau tay, quét một cung từ thấp phía sau, qua trước thân, lên phải-trên;
  3. theo đà rồi giữ P2.

  Không dùng các cụm "quay lại / phía xa / ra sau lưng" (bài học M01-b). Ghi rõ tay nào nối vai nào. Viết hướng theo màn hình.

## 2. Tái sử dụng

| Thứ | Dùng lại | Ghi chú |
|---|---|---|
| Nhân vật | `master_v07`, khối `{design}` trong brief, canvas 1820×1024, cell 176×140, H = 55,5 px | không tạo master mới |
| Ảnh tĩnh | prompt khung của `pose_downcut_p1/p2_v01` (thiết kế, style, magenta, "mỗi tay nối đúng vai") | chỉ đổi đoạn tư thế |
| Căn ảnh | đo bàn chân trên lưới, đặt theo trung điểm hai bàn chân (cách đã đạt ở M01) | script nhỏ, 0 USD |
| Video | `fal_video.py` route written-prompt, công thức chuỗi lực | 1 clip |
| Xoá vệt model | `dearc.py` (clip), `destrand.py` (frame xuất) | |
| Chọn frame | Frame Editor (artifact), `apply_recipe.py` (`anchor: feet`) | thêm một state `rise` |
| Đánh dấu | trang Blade Track Marker (chỉ đổi danh sách frame) | không xây editor mới |
| Quỹ đạo, khớp cung | `track_report.py` | đặt tên state/thư mục bằng tham số |
| VFX | `slash_from_track.py` kiểu `layered` + `SweepFrame`; `build_slash_diag.py` | tham số hoá tên state/fx, **không đổi thuật toán** |

Phương án rẻ hơn (không đề xuất): dùng lại chính P2 → P1 của M01 (0 USD ảnh). Đòn sẽ là vuốt ngược lên **cùng cung** với M01, nên không được tính là
trajectory khác. Chỉ dùng nếu user muốn tiết kiệm tối đa.

## 3. Nghiệm thu bổ sung (theo chuyên gia)

1. **Trajectory độc lập để đo độ chính xác.** Clip gốc 24 fps; bản xuất dùng các frame 15 fps.
   - User đánh dấu Root/Tip trên các frame **đã giữ** (dùng để dựng vệt), và **thêm 4-6 frame xen giữa** trong đoạn vung, lấy từ nguồn 24 fps. Các frame
     này **không** dùng để dựng.
   - Đo vị trí mũi và hướng của vệt (nội suy SweepFrame tại thời điểm đó) so với tip quan sát ở các frame xen giữa này.
   - Ngưỡng giữ như M01: ≤ 0,1 H, ≤ 15°.
   - Thêm: user đánh dấu lại 3 frame lần thứ hai để đo sai số của chính việc đánh dấu (mục tiêu ±0,05 H).
2. **Biến thể độ dày thấy được ở cỡ thật.** Đổi tham số dày/mỏng sao cho **mọi tầng** cùng co giãn (không chỉ dải chính). Đo @1x: diện tích và độ dày
   lớn nhất khác ≥ 30%. User xác nhận trên GIF @1x đặt cạnh nhau.
3. **Reproducible.** Mọi dữ liệu (điểm đánh dấu, `weapon_track.json`, `slash_params.json`) vào git. Một lệnh dựng lại. Hai lần build ra PNG cùng hash.
   Vẫn cố định `PYTHONHASHSEED` trong build vì debt `hash()` chưa sửa.
4. 6 tiêu chí của M01 giữ nguyên; khớp cung là gate ghi nhận như M01.
5. Sau M02 mới bàn promote. Điều kiện: hai trajectory + đo độc lập + sửa debt `hash()`.

## 4. Gate

| Gate | Việc | Tốn tiền |
|---|---|---|
| 0 | Kiểm tra tái sử dụng (bảng §2) | 0 |
| 1 | P1, P2 (fal-image, từng ảnh một); chồng hai ảnh kiểm chân, cỡ, kiếm; **user duyệt** | có |
| 2 | Mô tả chuyển động theo skill video-sprite, **user duyệt mô tả** → 1 clip 3 s → xoá vệt → user chọn frame → xuất `attack_rise_side`; **user duyệt** | có |
| 3 | Đánh dấu (frame giữ + frame xen giữa + đánh dấu lại); `weapon_track.json`; khớp cung; **user duyệt** | 0 |
| 4 | VFX layered + 3 biến thể (dày có khác biệt đo được); độ chính xác trên dữ liệu độc lập; **user duyệt** | 0 |
| 5 | Xuất `frames/fx/slash_rise/` + `fx.json`; chấm tiêu chí; cập nhật decision log, experiment log, roadmap | 0 |

## 5. Chi phí API dự kiến

| Mục | Dự kiến | Trần |
|---|---|---|
| P1 + P2 (gpt-image-2 low ~0,015 USD/ảnh), từng ảnh một | 0,03 | 0,09 (tối đa 3 lần mỗi ảnh) |
| Clip h3-max-turbo 3 s (0,045 USD) | 0,045 | 0,09 (tối đa 2 take; take 2 chỉ khi có nguyên nhân rõ) |
| **Tổng** | **~0,075 USD** | **~0,18 USD** |

Gate 3-5 không tốn tiền.

## 6. Rủi ro đã biết

- Model vẽ vệt cung khi vung nhanh → xoá ở bước xử lý sau. Vệt dính vào lưỡi kiếm → bỏ frame.
- Fal-image cho cả hai tay mọc từ một vai → prompt ghi rõ.
- Lưỡi thấp phía sau bị áo choàng che → prompt "lưỡi ở trước áo choàng".
- Model hiểu cử động kéo ra sau thành xoay người → tả theo màn hình, không có từ "ra sau lưng".
- Mũi kiếm giơ cao vượt khoảng trống cell (≈ 2,2 H trên chân) → kiểm tra khi đặt; vượt thì dừng hỏi, không nới canvas.
