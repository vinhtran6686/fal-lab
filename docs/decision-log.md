# Decision log (hướng VFX theo nhân vật)

Mỗi dòng là một quyết định đã chốt: ai quyết, căn cứ, nơi ghi chi tiết. Mới nhất ở trên. Experiment log: `docs/experiment-log.md`;
roadmap: `docs/roadmap.md`.

| Ngày | Quyết định | Ai | Chi tiết |
|---|---|---|---|
| 2026-11-10 | **Milestone 02 = Single Rising Diagonal Slash, Holy Commander**: một nhát chém từ dưới lên, không xoay thân phức tạp, không nhát thứ hai; lấy Root/Tip, dùng lại SweepFrame, VFX custom được và ghép vào nhân vật. Không tiếp tục Cross / Double Slash | chuyên gia | `milestone-01-advisor-closeout.md` §4 |
| 2026-11-10 | Nghiệm thu bổ sung cho M02: dữ liệu trajectory **độc lập** để đo độ chính xác; biến thể độ dày phải **thấy được ở cỡ thật**; dữ liệu và output reproducible; **không promote core trước khi có hai trajectory khác nhau**; không xây Editor / hệ thống tổng quát | chuyên gia | §5 |
| 2026-11-10 | Lỗi `hash()` trong `gen_slash_loop.drawing` vào technical debt; **không sửa core ở M02**; trước khi promote generator phải thay bằng cơ chế có seed và chạy regression các slash cũ | chuyên gia | §3; `roadmap.md` mục technical debt |
| 2026-11-10 | `SweepFrame` + `slash_from_track.py` **giữ ở experiment**, chưa promote. SweepFrame = **Blade Sweep Geometry** (vùng toàn bộ lưỡi quét từ Root tới Tip), **không** mặc định là công thức chung cho mọi slash | chuyên gia | §2 |
| 2026-11-10 | **Milestone 01 nghiệm thu: Successful Proof of Concept**, không làm lại. Caveat: hướng của SweepFrame chưa kiểm chứng độc lập (tạo và đo cùng dùng Catmull-Rom); biến thể độ dày khác chưa đủ rõ; sợi vệt nhỏ còn ở body frame 11; build tất định phụ thuộc `PYTHONHASHSEED=0` | chuyên gia | §1; `milestone-01-result-for-advisor.md` |
| 2026-11-10 | Quy trình M01 chỉ áp dụng cho **skill đơn** (một động tác); skill phức tạp (nhiều động tác, xoay hông/thân trong một clip) chưa đạt | user | `milestone-01-research-rising-cuts.md` |
| 2026-11-10 | VFX M01 đổi sang bản **nhiều tầng, phủ Root→Tip** (showcase `gen_slash_loop` heavy trong SweepFrame), chọn bản gốc | user | `out/heroes/holy_commander/history.md` |
| 2026-11-10 | Bỏ nhánh chém đôi chữ X; đòn M01 = một nhát chém xéo từ trên xuống | user | `milestone-01-research-rising-cuts.md` |
| 2026-11-10 | Kế hoạch M01: 6 gate, H = 55,5 px @1x, hệ toạ độ chân / y lên / ms, đánh dấu tay mọi frame, khớp elip trước (ngưỡng 0,08 / 0,15 H), VFX phương án C, code ở `scripts/experiments/milestone_01/` | chuyên gia | `milestone-01-advisor-review.md`, `milestone-01-plan.md` |
| 2026-11-10 | Chọn Milestone 01 Character-Synchronized Slash, hướng Character-first | chuyên gia | `milestone-01-character-synced-slash.md` |
