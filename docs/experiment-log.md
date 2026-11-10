# Experiment log (VFX theo nhân vật)

Một mục cho mỗi thử nghiệm: mục tiêu, cách làm, kết quả, chi phí, bài học. Chi tiết từng take ở `out/heroes/<id>/history.md`.

## M01 Character-Synchronized Slash, Holy Commander (2026-11-10): ĐẠT, Proof of Concept

- **Mục tiêu:** một nhát chém xéo từ trên xuống; VFX sinh từ quỹ đạo kiếm đánh dấu tay; tách lớp; ghép đúng frame.
- **Sản phẩm:** body `frames/attack_diag_side` (16 hình, 1,07 s, hit 13) + fx `frames/fx/slash_diag` (front, RGBA @2x/@1x, `fx.json`).
  Một lệnh dựng lại: `python scripts/experiments/milestone_01/build_slash_diag.py`.
- **Dữ liệu:** `source/vfx/slash_diag/` (`track_marks_raw.json`, `weapon_track.json`, `slash_params.json`, `review/`).
- **Kết quả số:** khớp đường tròn hình 8-13: sai số TB 0,037 H, lớn nhất 0,078 H. Đầu vệt cách mũi kiếm 0,03-0,06 H. Nét @1x dày nhất 24-28 px.
  Hai lần build ra PNG giống hệt nhau (khi cố định seed).
- **Chi phí API:** body ~0,07 USD (P1 hai lần, P2, 1 clip 3 s); cả ngày ~1 USD, phần lớn cho nhánh chém đôi bên dưới.
- **Caveat (chuyên gia):** hướng của SweepFrame chưa kiểm chứng độc lập; biến thể độ dày khác chưa rõ; sợi vệt nhỏ ở body frame 11; tất định nhờ
  `PYTHONHASHSEED=0`.
- **Bài học dùng lại:**
  1. Ghim ảnh đầu và ảnh cuối, cùng cỡ, cùng chỗ đặt chân (đo trên lưới).
  2. Prompt tả từng bộ phận theo chuỗi lực; ghi rõ tay nào nối vai nào.
  3. Model vẫn vẽ vệt cung khi chém nhanh: xoá bằng `dearc.py` / `destrand.py`.
  4. Quy tắc bắt đầu VFX: lấy đoạn nhanh liên tục chứa đỉnh tốc độ, không lấy lần đầu vượt ngưỡng.
  5. Phủ Root→Tip phải theo đường gốc/mũi thật (SweepFrame), không theo bán kính quanh tâm cung, vì tay cầm không nằm ở tâm cung.
  6. Đo hướng bằng sai phân trung tâm. Nếu đường vệt được dựng từ chính các điểm đó thì phép đo không còn độc lập.

## M01-b Chém đôi vuốt lên chữ X (2026-11-10): KHÔNG ĐẠT, dừng

- Chi tiết, các lần thử và bài học: `docs/milestone-01-research-rising-cuts.md`.
- Tóm tắt: hai động tác và xoay hông/thân trong một clip thì model không giữ được hướng xoay và không làm đủ động tác. Ảnh phác trắng không cho biết
  đâu là ngực, đâu là lưng. Vệt cung dính vào lưỡi kiếm. Khoảng 0,8 USD.

## M01-c Đâm kiếm do AI tự sáng tạo (2026-11-10): chỉ xem thử

- Một clip 4 s, khung đầu là master, không ghim khung cuối. Không đánh giá tiếp; file làm việc đã xoá.
