# Puppet Kit: bảng phân việc theo model

Cập nhật 2026-11-11. Nhánh làm việc của mọi task: `claude/puppet-kit`. Kế hoạch gốc: `docs/puppet-kit-next.md`.

Cách dùng: mở một session mới với đúng model ghi ở tên file, nói "làm theo `docs/tasks/<file>`". Model đó chỉ cần đọc file task (và các file task chỉ ra), làm,
tự kiểm theo mục "Nghiệm thu", rồi **sửa dòng `Trạng thái` trong file task thành DONE** kèm ghi chú kết quả, commit và push. Không cần đọc lại lịch sử hội thoại.

## Quy tắc chung cho mọi task

1. `git pull --rebase origin claude/puppet-kit` trước khi bắt đầu và trước khi push.
2. **Chỉ sửa các file ghi ở mục "Được sửa"** của task. Không sửa `scripts/puppet.py`, `scripts/puppet_kit/core.py` trừ khi task ghi rõ (hai file này Fable đang sửa: tránh xung đột).
3. Không gọi API trả tiền (fal) trừ khi task ghi rõ số ảnh và trần tiền.
4. Kết thúc: điền mục "Kết quả" trong file task, đổi `Trạng thái: TODO` thành `Trạng thái: DONE (ngày, model)`; nếu kẹt thì `BLOCKED` và ghi lý do. Cập nhật dòng tương ứng trong bảng dưới.
5. Commit một lần, message bắt đầu bằng mã task (`T1: ...`), rồi `git push -u origin claude/puppet-kit`.
6. Không viết tên model vào commit hay code.

## Bảng việc

| Mã | File | Model | Việc | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|
| T1 | `task-1-haiku-regression-test.md` | Haiku | test hồi quy bằng hash frame | không | TODO |
| T2 | `task-2-haiku-lion-slash-params.md` | Haiku | bộ tham số vệt vuốt riêng cho lion + file requirements | không | TODO |
| T3 | `task-3-sonnet-rig-tuner-v2.md` | Sonnet | Rig Tuner v2: tạo/xoá xương, xem thử xoay khớp | không | TODO |
| T4 | `task-4-sonnet-prep-align.md` | Sonnet | lệnh `prep` và `align` cho bước chuẩn bị tài nguyên | không | TODO |
| T5 | `task-5-sonnet-lion-animations.md` | Sonnet | viết hurt, death, roar cho lion theo công thức | F2 (đã xong) | TODO |
| F1 | (Fable, trong session chính) | Fable | P02: gói tài nguyên lion (lớp thân, chân, tay, đuôi) | không | DONE 2026-11-11 (chờ user duyệt) |
| F2 | (Fable) | Fable | P03: engine rig v2 (IK chân ghim đất, khớp háng, thứ tự vẽ theo frame) + rig v2 cho lion | F1 | DONE 2026-11-11 (chờ user duyệt) |
| F3 | (Fable) | Fable | P05: bộ profile + run/walk bằng rig | F2 | chưa làm |
| F4 | (Fable) | Fable | P06: xoay thân (cào từ trước mặt sang trái) | F3 | chưa làm |

Vì sao chia như vậy: F1-F4 cần nhìn ảnh, phán đoán hình và sửa lõi engine; T1-T5 có đặc tả đóng, kiểm được bằng lệnh.
