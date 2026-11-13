# Vệt chém, vòng 02: kế hoạch

Nguồn: đánh giá của người lập kế hoạch và người dùng ngày 2026-11-13 sau khi áp `melee/slash/crescent --track` lên `out/heroes/azure_blade`.
Người lập kế hoạch không thi công; người thi công làm đúng từng bước trong file task, đánh dấu ô, điền "Kết quả". Xoá thư mục này khi mọi task xong và được duyệt.

## Checklist
- [ ] **S1** Vệt chém bám vũ khí mượt như bản đã duyệt của `azure_blade` (khung đầu, nhịp tan ở 15 fps, đuôi rút, mũi đậm chuôi nhạt, mép sáng dọc lưỡi): [S1-tracked-slash-smooth.md](S1-tracked-slash-smooth.md)
- [ ] **S2** Mặt phẳng vung: chém ngang, chém xéo theo góc nhìn của game (chưa viết task; chờ người dùng yêu cầu)
- [ ] **S3** Rìu dày hơn: ít dải, dải rộng (chưa viết task)
- [ ] **CHẤM** (người lập kế hoạch) sau mỗi task → **DUYỆT** (người dùng)

## Luật chung
1. Đọc `CLAUDE.md`, `lib-fx/_core/formulas/draw/FXKIT.md` (mục 4 và 6), `docs/pipeline/pose-pair-fx-method.md` (bước 7 và checklist "Vệt chém").
2. Chỉ sửa file ghi trong task. **Không sửa gì trong `out/`** (bản đã duyệt của `azure_blade` là mốc so sánh, không phải thứ để thay).
3. Không số RGB trong kind; ngẫu nhiên qua `c.rng`; hình qua `fxkit.shapes`; tô qua `Ink`.
4. Mỗi lần đổi phải mở ảnh ra xem; tối thiểu 3 vòng xem và sửa.
5. Xong: `python lib-fx/build.py melee/slash --check` không FAIL, `python lib-fx/_tools/fxkit_test.py` qua, commit + push lên `ccr-38411bc5-l13uki`.
6. Không công cụ tốn tiền, không đọc `.env`.
