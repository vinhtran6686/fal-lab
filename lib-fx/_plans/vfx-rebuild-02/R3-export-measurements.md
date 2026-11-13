# R3. Xuất số đo cho luật (sau khi R1, R2 được chấm đạt)

File được tạo: `lib-fx/_core/formulas/rules/data/*_flame-burst.json`, `*_lightning.json` (cùng tên gọi với các file `*_element-trio.json` đang có trong thư mục đó).

## Các bước
1. Với mỗi profile (`flame-burst`, `lightning`): `python lib-fx/_tools/vectorfx.py lifecycle P`, `track P`, `study P`. Chép các file JSON kết quả vào
   `lib-fx/_core/formulas/rules/data/` theo đúng cách đặt tên của bộ `element-trio` (mở thư mục xem tên).
2. Lập bảng số cho 8 giả thuyết H1-H8 trong `PLAN.md` mục 3: mỗi dòng ghi **số đo**, **đúng / sai / một phần**, và khung dẫn chứng. Viết bảng vào mục "Kết quả" bên dưới
   (không viết vào `rules/`: phần luật do người lập kế hoạch viết sau khi người dùng duyệt).
   - H1: diện tích lớn nhất của pha báo trước / diện tích đỉnh; số khung lặng giữa hai pha.
   - H2: khung đầu và khung cuối có diện tích > 2 % đỉnh của từng lớp (`smoke`, `orange`, `yellow`).
   - H3: toạ độ tâm (cx theo hướng phụt, cy) của `orange ∪ yellow` và của `smoke` ở mỗi 5 khung, tính từ miệng hộp.
   - H4: với 3 đầu mút khói ở khung 51 và 58: tổng góc quay của path ở đoạn 40 px cuối (độ).
   - H5: với 10 tia sét lớn nhất: số nhánh, bề rộng trung vị thân và nhánh (px gốc), độ dài các đoạn thẳng giữa hai góc (danh sách).
   - H6: số khung sống của từng tia; khung sáng nhất là khung thứ mấy của tia.
   - H7: `halo.sigma` đo được / bề rộng nét trung vị.
   - H8: IoU lớn nhất giữa mặt nạ (đã nở 6 px) của hai tia bất kỳ.
3. Commit + push; đánh dấu ô R3 trong `PLAN.md`.

## Kết quả
