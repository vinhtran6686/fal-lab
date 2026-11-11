# Roadmap: VFX theo nhân vật (trạng thái)

Cập nhật 2026-11-10. Quyết định: `docs/decision-log.md`; thử nghiệm: `docs/experiment-log.md`.

## Milestones

| # | Tên | Trạng thái | Ghi chú |
|---|---|---|---|
| M01 | Character-Synchronized Slash (chém xéo xuống, Holy Commander) | ✅ đạt, Proof of Concept | caveat ở decision log; không làm lại |
| M02 | Single Rising Diagonal Slash (chém vuốt lên, Holy Commander) | 📝 kế hoạch nháp, chờ user duyệt chi phí | `docs/milestone-02-plan-DRAFT.md`; trajectory thứ hai cho SweepFrame |
| P01 | Puppet Kit: rig cắt lớp + pose-to-pose (Holy Commander) | 🧪 chạy được, chờ user duyệt | `docs/puppet-kit.md`; nhánh `claude/puppet-kit`; gốc/mũi kiếm lấy từ socket của rig |
| P02-P07 | Puppet Kit v2: chuẩn bị tài nguyên (lớp khuất, tờ part, profile), rig chân/háng/khuỷu, Rig Tuner v2, xoay thân | 📝 kế hoạch, chờ user báo bắt đầu | `docs/puppet-kit-next.md`, `docs/puppet-kit-motion-recipes.md` |
| — | Cross / Double Slash, skill nhiều động tác | ⏸ dừng | `docs/milestone-01-research-rising-cuts.md` |

## North Star (năng lực, theo chuyên gia)

| # | Năng lực | Trạng thái sau M01 |
|---|---|---|
| 1 | Reference Reconstruction | đã có nền tảng |
| 2 | Parametric Shape Generator | đã có nền tảng |
| 3 | Motion-driven VFX | **có PoC** (M01: VFX từ quỹ đạo kiếm thật, SweepFrame) |
| 4 | Lifecycle & Impact | cần mở rộng (M01 chỉ có bung, tan; chưa có va chạm) |
| 5 | VFX Composition | prototype |
| 6 | Character Integration | **có pipeline cho skill đơn** (body + lớp fx riêng, `fx.json`, một lệnh dựng lại) |
| 7 | Reusable Skill Assets | mục tiêu dài hạn; chờ hai trajectory trước khi promote |

## Điều kiện promote vào `lib-fx/_core/vector/`

- [ ] Có **hai** trajectory khác nhau dùng chung SweepFrame / `slash_from_track` (M01 ✅, M02 ⏳)
- [ ] Độ chính xác đo bằng dữ liệu trajectory **độc lập**
- [ ] Sửa technical debt `hash()` + regression các slash cũ trong showcase

## Technical debt

| Mục | Ảnh hưởng | Khi nào xử lý |
|---|---|---|
| `gen_slash_loop.drawing` đặt vệt đứt bằng `hash(l)`: thay đổi theo mỗi lần chạy | build không tất định nếu không cố định `PYTHONHASHSEED` | trước khi promote generator (không làm ở M02) |
| Sợi vệt cung mảnh còn ở body frame 11 của `attack_diag_side` | chỉ thấy khi phóng to | khi làm lại body, nếu có |
| `apply_recipe.py`: tuỳ chọn `anchor: feet` mới, chỉ state `diag` dùng | tool frame tuner có thêm một nhánh | xem lại khi có state thứ hai cần |
