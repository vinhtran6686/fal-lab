# Milestone 01: kế hoạch thực hiện (BẢN NHÁP v0, chờ chuyên gia góp ý)

> **Trạng thái: NHÁP.** Viết 2026-11-10 bởi Claude theo quyết định trong `docs/milestone-01-character-synced-slash.md`. **Chưa thực hiện bước nào,
> chưa gọi API.** Theo yêu cầu của user: Claude và chuyên gia thống nhất kế hoạch + checklist đầy đủ trong repo trước, rồi mới bắt đầu test. Câu hỏi
> gửi chuyên gia: `docs/milestone-01-advisor-questions.md`. Mỗi chỗ ghi **[HỎI Qn]** là điểm chờ chuyên gia quyết.

## 0. Phạm vi

Một nhát **chém xéo từ trên xuống** của `holy_commander` (anh hùng cỡ M, master v07), VFX slash sinh bằng Vector Kit **khớp theo quỹ đạo kiếm thật**,
ghép tách lớp với thân, xem ở cỡ game. Không làm: tự dò vũ khí, chia nhát tự động, Timeline Editor, Composition Editor, nhân vật khác, combo.

## 1. Quy ước chung của thử nghiệm (đề xuất)

| Thứ | Quy ước | Căn cứ hiện có |
|---|---|---|
| Gốc toạ độ | điểm neo chân của nhân vật = (0, 0) | pivot (0,5; 0,88) của cell 176×140 @1x, `out/heroes/holy_commander/meta.json` |
| Trục | x về phía trước (phải), **y lên trên** | giống `scripts/fx_layers.py` |
| Đơn vị dài | **H** = chiều cao thân. **[HỎI Q4]** dùng H của bậc cỡ (60 px @1x) hay H đo thật (`body_height_2x` 111 → 55,5 px @1x)? | `meta.json` |
| Thời gian | **ms** tính từ frame đầu của state (sau retime); dựng ra frame ở 15 fps (66,7 ms / frame) | `meta.json` fps 15 |
| Khung VFX | khung riêng của hiệu ứng, có pivot trùng pivot thân (như `radiant_slash`), không nới cell thân | `out/heroes/holy_commander/frames/fx/radiant_slash/fx.json` |

## 2. Các bước

### B1. Hai pose (fal-image, tốn tiền)

- `pose_slash_diag_p1` (chuẩn bị): kiếm giơ cao ra sau vai, mũi chĩa lên / ra sau; thân xoay nhẹ về sau, chân trước bước tới. **[HỎI Q1]**
- `pose_slash_diag_p3` (kết thúc): kiếm ở thấp phía trước, chéo xuống đất, thân đổ về trước. **[HỎI Q1]**
- Cách làm: `scripts/gen_image.py` + `--ref master_v07`, view prompt side, quality low (`.claude/skills/fal-image/format.md` §3, §11). Chấm ≥ 8/10, kiểm tra độ
  dài kiếm khớp master (giới hạn đã biết: độ dài vũ khí trôi giữa các pose).
- Ước tính: 2-6 ảnh × ~0,0135 USD.

### B2. Một clip chém xéo (video-sprite, tốn tiền)

- Model `h3-max-turbo` image-to-video, frame đầu = p1, frame cuối = p3, prompt chỉ cơ thể (không vệt, không hiệu ứng), thời lượng ≥ 3 s (dưới ~3 s model
  mất nhịp). **[HỎI Q2]** thời lượng sau retime (đề xuất 0,7 s như attack, hit ở 40%)?
- Xuất bằng `scripts/video_to_sheet.py` vào state mới `attack_diag_side` (không thay `attack_side`), cùng cell 176×140, cùng cỡ thân.
- Đạt khi: thấy rõ một đòn chém xéo, kiếm luôn thấy, **không có vệt / ánh sáng do model vẽ**, thân không zoom / không đổi cỡ. Tối đa **[HỎI Q2]** lần quay.
- Ước tính: 1-6 clip × ~0,062 USD.

### B3. Đánh dấu quỹ đạo kiếm (thủ công, 0 USD)

- Trên các frame của đoạn vung (từ frame bắt đầu vung tới frame chạm và 1-2 frame sau), ghi **Blade Root** (chỗ tay cầm / chân lưỡi) và **Blade Tip**
  (mũi kiếm) theo quy ước §1, kèm ms. **[HỎI Q3]** đánh dấu mọi frame hay chỉ 3-5 frame khoá? ai đánh dấu (user bằng công cụ click, hay Claude đọc
  ảnh phóng to có lưới)? sai số chấp nhận?
- Dữ liệu (đề xuất), lưu `out/heroes/holy_commander/source/vfx/slash_diag/weapon_track.json`:

```jsonc
{"state": "attack_diag_side", "cell": [176, 140], "pivot": [0.5, 0.88], "H_px_1x": 60, "fps": 15, "units": "H, origin feet, y up; time ms",
 "hit_frame": 6,
 "samples": [ {"frame": 2, "ms": 133, "root": [-0.10, 0.95], "tip": [-0.55, 1.75], "visible": true, "note": "start of swing"}, ... ]}
```

- Ghi cả frame mà kiếm bị che / mờ (`visible: false`), không đoán.

### B4. Sinh VFX từ quỹ đạo (Vector Kit, 0 USD)

- **Khớp cung elip** (tâm, bán kính, độ dẹt, nghiêng) vào các điểm **tip** bằng bình phương nhỏ nhất; báo sai số theo H. **[HỎI Q5]** sai số bao nhiêu
  thì coi là "không đủ" và chuyển sang đường cong tự do?
- **[HỎI Q5]** VFX tượng trưng cho gì: (a) vệt theo **mũi kiếm** (dải mảnh quanh tip), hay (b) **vùng lưỡi quét** từ root tới tip (dải rộng = độ dài lưỡi),
  hay (c) dải lệch về phía mũi, độ rộng chỉnh độc lập?
- Thời gian: đầu nét = vị trí mũi kiếm ở từng frame; đuôi đuổi theo. **[HỎI Q6]** đầu nét trùng, đi trước hay đi sau mũi kiếm? VFX bắt đầu khi nào (frame
  bắt đầu vung, hay khi tốc độ mũi vượt ngưỡng)? sống bao lâu sau frame chạm?
- Tham số chỉnh độc lập (tiêu chí 4): length (độ trễ đuôi / phần cung phủ), width, curvature (bù vào cung đã khớp), taper (a, b), opacity theo thời gian,
  lifetime, glow. Kiểu nét: lấy từ `STYLES` hiện có. **[HỎI Q8]** màu (holy_commander: vàng / trắng như radiant_slash?).
- Cách làm trong code: một bộ sinh nhỏ mới dùng lại `gen_slash_loop.drawing`, `gen_render.render_sequence`, `frames.EllipseFrame` (không đổi code cũ;
  kiểm tra các slash cũ vẫn ra giống hệt).

### B5. Ghép với thân và xuất (0 USD)

- **[HỎI Q7]** chia lớp **back / front**: phần nào của nhát chém nằm sau thân, phần nào trước (theo phía vai xa / gần? theo nửa trên / dưới cung?);
  hoà màu **screen / additive** (như radiant_slash) hay alpha-over?
- Xuất RGBA @1x và @2x, mỗi lớp một thư mục, `fx.json` cùng định dạng `radiant_slash` (cỡ, pivot, blend, lớp, frame n khớp frame n của thân).
  **[HỎI Q9]** để ở `out/heroes/holy_commander/frames/fx/slash_diag/` (asset của nhân vật) hay đồng thời vào `lib-fx/` (thư viện)?
- Preview: GIF thân + VFX ở **@1x thật (H ≈ 60 px)**, 15 fps; thêm bản phóng 3× (nearest) để soi; bản VFX riêng.

### B6. Đánh giá theo 6 tiêu chí

| # | Tiêu chí | Cách đo đề xuất | **[HỎI Q10]** |
|---|---|---|---|
| 1 | đòn chém xéo rõ | user nhìn GIF @1x | |
| 2 | VFX không dính thân | VFX ở lớp riêng; bật / tắt được; thân sạch không có vệt model | |
| 3 | đúng hướng và quỹ đạo | khoảng cách đầu nét ↔ mũi kiếm đã đánh dấu ở mỗi frame ≤ ? H; hướng tiếp tuyến lệch ≤ ?° | ngưỡng? |
| 4 | chỉnh độc lập độ dày, dài, cong | đổi từng tham số, các tham số khác không đổi (3 biến thể đặt cạnh nhau) | |
| 5 | đọc được ở H = 60 px | GIF @1x; nét mảnh nhất ≥ ? px @1x; user chấm | ngưỡng px? |
| 6 | xuất và tái sử dụng | dựng lại từ `weapon_track.json` + tham số, không sửa tay; `fx.json` dùng được cho state khác | |

Không đạt: ghi rõ bước nào hỏng (pose / clip / đánh dấu / khớp / ghép / đọc ở 60 px) và đổi cách tiếp cận ở bước đó, không xây tầng trên.

## 3. Checklist thực hiện (nháp; chốt sau khi chuyên gia trả lời)

- [ ] Chuyên gia trả lời Q1-Q12; cập nhật file này thành bản chốt (bỏ "DRAFT"), user duyệt
- [ ] Ghi quy ước §1 vào `out/heroes/holy_commander/brief.md` (manifest: dòng mới cho pose, state, fx)
- [ ] User đồng ý chi phí B1 + B2
- [ ] B1: tạo pose p1, p3; chấm; ghi `history.md`; user duyệt
- [ ] B2: quay clip, chọn take, retime, xuất `attack_diag_side`; kiểm tra không vệt model, cỡ thân; ghi `history.md`; user duyệt
- [ ] B3: đánh dấu root / tip / ms; lưu `weapon_track.json`; contact sheet có điểm đánh dấu để kiểm tra
- [ ] B4: khớp cung, báo sai số; sinh VFX; 3 biến thể (dày, dài, cong) để kiểm tra tiêu chí 4; kiểm tra slash cũ không đổi
- [ ] B5: chia lớp back / front, xuất RGBA @1x / @2x + `fx.json`; preview @1x và 3×
- [ ] B6: chấm 6 tiêu chí; ghi kết quả + bài học vào `docs/milestone-01-character-synced-slash.md`, `lib-fx/_core/vector/STATUS.md`, `CHANGELOG.md`
- [ ] Dọn: `source_prune.py` (chú ý lỗi đã biết với tên file `_p<N>`), commit, push
