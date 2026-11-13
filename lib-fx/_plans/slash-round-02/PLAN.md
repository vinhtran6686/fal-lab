# Vệt chém, vòng 02: kế hoạch

Nguồn: đánh giá của người lập kế hoạch và người dùng ngày 2026-11-13 sau khi áp `melee/slash/crescent --track` lên `out/heroes/azure_blade`.
Người lập kế hoạch không thi công; người thi công làm đúng từng bước trong file task, đánh dấu ô, điền "Kết quả". Xoá thư mục này khi mọi task xong và được duyệt.

## Checklist
- [x] **S1** Vệt chém bám vũ khí mượt như bản đã duyệt của `azure_blade` (khung đầu, nhịp tan ở 15 fps, đuôi rút, mũi đậm chuôi nhạt, mép sáng dọc lưỡi): [S1-tracked-slash-smooth.md](S1-tracked-slash-smooth.md)
- [ ] **S2** Mặt phẳng vung: chém ngang, chém xéo theo góc nhìn của game (kèm 3 việc nhỏ từ lần chấm S1): [S2-swing-planes.md](S2-swing-planes.md)
- [ ] **S3** Rìu dày hơn: ít dải, dải rộng (chưa viết task)
- [ ] **CHẤM** (người lập kế hoạch) sau mỗi task → **DUYỆT** (người dùng)

## Luật chung
1. Đọc `CLAUDE.md`, `lib-fx/_core/formulas/draw/FXKIT.md` (mục 4 và 6), `docs/pipeline/pose-pair-fx-method.md` (bước 7 và checklist "Vệt chém").
2. Chỉ sửa file ghi trong task. **Không sửa gì trong `out/`** (bản đã duyệt của `azure_blade` là mốc so sánh, không phải thứ để thay).
3. Không số RGB trong kind; ngẫu nhiên qua `c.rng`; hình qua `fxkit.shapes`; tô qua `Ink`.
4. Mỗi lần đổi phải mở ảnh ra xem; tối thiểu 3 vòng xem và sửa.
5. Xong: `python lib-fx/build.py melee/slash --check` không FAIL, `python lib-fx/_tools/fxkit_test.py` qua, commit + push lên `ccr-38411bc5-l13uki`.
6. Không công cụ tốn tiền, không đọc `.env`.

## Nhận xét khi chấm
**S1 (2026-11-13): ĐẠT.** Người lập kế hoạch dựng lại độc lập `melee/slash/swing --track` trên `azure_blade` ở 15 fps và ghép cạnh bản đã duyệt (khung thân 21-29).
- Khung trước đòn: lát trắng mảnh ôm lưỡi pose A, không che nhân vật. Khung đòn: vệt đầy, mép ngoài trùng đường mũi đao, mép trắng dọc lưỡi pose B, mũi đậm chuôi nhạt.
- Tổng alpha fx theo khung thân 23 → 27: 9204, 5841, 3313, 982, 122 (tỉ lệ 0,63 / 0,36 / 0,11 / 0,01): tan đều, không giữ rồi tắt; đuôi rút trước.
- Các lệch so với task (ghi trong file S1) đều hợp lý và được chấp nhận.
Việc nhỏ còn lại, đã gộp vào S2 (mục "Việc nhỏ gộp từ lần chấm S1"):
1. `scraps` ở mũi đao rơi xuống dưới mặt đất và còn lác đác tới khung 29 (cảnh báo `linger`): bật `floor=True`, rút ngắn đời.
2. Lint đòi một lớp primary / core / flash trên khung trúng đòn nên `swing` phải gắn `role="core"` cho `streaks`: sửa `Effect.lint` để lớp primary sinh **trước** đòn và còn sống ở t = 0 cũng được tính.
3. Khung trước đòn chỉ có màu trắng; bản đã duyệt có thêm sắc xanh của vệt. Thử thêm một viền `main` mỏng quanh lát trắng.
