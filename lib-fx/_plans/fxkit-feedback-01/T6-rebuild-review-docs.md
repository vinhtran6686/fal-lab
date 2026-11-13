# T6. Dựng lại, trang duyệt, tài liệu, dọn kế hoạch

Phụ thuộc: T1-T5 đã đánh dấu xong.

## Việc
1. `python lib-fx/build.py` (toàn thư viện) rồi `python lib-fx/_tools/fxcheck.py` và `python lib-fx/_tools/fxkit_test.py`. Chỉ được còn FAIL ở
   `magic/spirit/soulstrike` (họ cũ, đang `rework`, ngoài phạm vi).
2. Cập nhật trang duyệt **cùng địa chỉ** https://claude.ai/artifact/6NN5cynqUge1CqM7tfUfoR (publish lại với `url` này, đọc trang trước khi ghi đè):
   - mục "Before / after" mới cho từng góp ý: lửa phun trước / sau làm mịn (phóng 300 % một khung đỉnh), `slam` trước / sau mặt phẳng đất,
     kiếm cạnh rìu, `azure_blade` ba cột (đã duyệt | fxkit cũ | fxkit theo quỹ đạo vũ khí), `light` / `heavy` / `crit` cạnh nhau cả màu lẫn xám;
   - giữ mục thư viện, biến thể, tách lớp, dựng lại GIF từ khung mới.
3. Tài liệu (sửa cùng thay đổi, `docs/repo-structure-rules.md` §4.6): `FXKIT.md` (bước làm mịn, `plane`, `weapon`, `track`, bảng kind),
   `lib-fx/README.md` (lệnh mới), `lib-fx/GUIDE.md` (hiệu ứng mới của `melee/slash`), `CLAUDE.md` (một dòng nếu lệnh cho nhân vật đổi).
4. Ghi vào `lib-fx/_core/formulas/rules/vfx/slash/README.md` các luật vừa được người dùng xác nhận: kiếm = nét mịn cùng hướng; rìu = dải song song;
   vệt phải theo bề mặt lưỡi quét. Kèm ngày và nguồn (góp ý 2026-11-13).
5. Xoá thư mục `lib-fx/_plans/` trong cùng commit cuối (kế hoạch đã xong không giữ trong repo). Nội dung "Kết quả" của các task chuyển thành thông điệp commit.
6. Báo người dùng: danh sách đã sửa, các số đo trước / sau, những gì còn mở.

## Tiêu chí nghiệm thu
- [ ] Toàn thư viện dựng sạch (trừ `soulstrike`), test qua, cây git sạch, đã push.
- [ ] Trang duyệt cập nhật đúng địa chỉ cũ, có đủ 5 cặp before / after.
- [ ] Không còn tham chiếu tới `lib-fx/_plans/` trong repo (`grep -rn "_plans" .`).

## Kết quả (người làm điền)
