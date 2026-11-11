# T4 (Sonnet): lệnh `prep` và `align` cho bước chuẩn bị tài nguyên

Trạng thái: TODO

## Mục tiêu
Hai lệnh hỗ trợ bước chuẩn bị tài nguyên của một nhân vật (`docs/puppet-kit-next.md` §2): biết còn thiếu ảnh gì kèm prompt điền sẵn, và kiểm một ảnh mới có khớp master không.

## Đọc trước
- `docs/tasks/README.md` mục "Quy tắc chung".
- `docs/puppet-kit-next.md` §2 (bảng 2.1 gói tài nguyên, 2.2 quy tắc prompt).
- `.claude/skills/fal-image/format.md` §1-§3 (khối `{STYLE}`, `{BG}`, `{SIMPLE}`, câu VIEW của master).
- `out/heroes/lion_brawler/brief.md` (dòng `{design}`), `out/heroes/lion_brawler/source/rig/plate_v01.json` (prompt plate đã chạy tốt).
- `scripts/puppet.py`: `colour_mask`, và `key_magenta` trong `scripts/puppet_kit/core.py` (chỉ để import, **không sửa**).

## Được sửa
- Tạo mới `scripts/puppet_prep.py` (file riêng để không đụng `puppet.py`)
- `docs/puppet-kit.md`: thêm một mục ngắn "Chuẩn bị tài nguyên" mô tả hai lệnh
- File task này và dòng T4 trong `docs/tasks/README.md`

## Đặc tả

### `python scripts/puppet_prep.py list <asset>`
- Đọc `<asset>/brief.md` lấy `{design}` (dòng bắt đầu bằng ``- `{design}`:``) và `{H}` (từ dòng Class / size), `<asset>/meta.json`, liệt kê file trong `source/design/` và `source/rig/`.
- In bảng (Markdown) các tài nguyên của bảng 2.1: tên chuẩn, có/thiếu (kèm tên file tìm thấy, bản `_vNN` mới nhất), và dùng cho gì.
  Quy ước tên để nhận ra: `master_v*`, `plate_v*` (trong `source/rig/`), `plate_legs_v*`, `layer_<tên>_v*`, `parts_v*`, `profile_v*`, `profile_plate_v*`, `profile_parts_v*`, `pose_turn_*_v*`.
- `--write-prompts`: với mỗi tài nguyên **thiếu**, ghi một file prompt `source/design/prompts/<tên>_p01.txt` (không ghi đè file đã có). Prompt phải **điền đủ**, không còn `{...}` hay `[...]`:
  `{design}` thật, khối STYLE với `{H}` thật, BG; và theo đúng quy tắc 2.2 (mỗi loại một mẫu câu: plate chân, lớp khuất, tờ part A-pose, profile, plate profile).
  Lớp khuất cần tên bộ phận: tham số `--layers cape,far_arm,far_leg,tail` (mặc định rỗng: không sinh prompt lớp khuất).
- In ra lệnh `gen_image.py` tương ứng cho từng prompt (chỉ in, **không chạy**), đúng mẫu:
  `python scripts/gen_image.py --prompt-file <file> --ref <master> --size 1024x1024 --png --name <tên> --versioned --out <asset>/source/design`

### `python scripts/puppet_prep.py align <asset> <ảnh> [--colour r,g,b] [--kind plate|pose|profile]`
So ảnh mới với master (ảnh `sources.master` của `source/rig/rig.json`, hoặc `master_v*` mới nhất nếu chưa có rig):
- `bbox`: lệch 4 cạnh của hình bóng (px), và lệch hàng chân (hàng thấp nhất có pixel thân).
- `scale`: nếu có `--colour`: căn bậc hai tỉ lệ diện tích vùng màu đó (`colour_mask`) giữa ảnh và master.
- Ngưỡng theo `--kind`:
  - `plate` (mặc định): hàng chân lệch ≤ 8 px, bbox trên ≤ 12 px, scale trong 0,97-1,03 (nếu có màu). Cạnh trái/phải không xét (plate bỏ tay nên hẹp hơn).
  - `pose`, `profile`: chỉ xét scale trong 0,95-1,05; in thêm gợi ý lệnh `puppet.py pose ...` với đúng `--colour`.
- In từng số đo, một dòng `PASS` hoặc `FAIL: <lý do>`; mã thoát 0/1.
- `--overlay <png>`: ghi ảnh chồng (master đỏ, ảnh mới xanh lục, 50% mỗi lớp) để người xem.

## Nghiệm thu
```bash
python scripts/puppet_prep.py list out/heroes/lion_brawler
python scripts/puppet_prep.py list out/heroes/lion_brawler --write-prompts --layers far_arm,far_leg,tail   # rồi xoá các file prompt vừa sinh trước khi commit, trừ khi Fable đã tạo ảnh tương ứng
python scripts/puppet_prep.py align out/heroes/lion_brawler out/heroes/lion_brawler/source/rig/plate_v01.png --colour 118,49,21
python scripts/puppet_prep.py align out/heroes/lion_brawler out/heroes/lion_brawler/source/design/pose_run_4_v01.png --colour 118,49,21 --kind pose
```
- Lệnh 1: master và plate "có"; plate_legs, parts, profile... đúng với thực tế thư mục lúc chạy.
- Lệnh 3: PASS (plate của lion khớp master). Lệnh 4: FAIL vì scale khoảng 0,80-0,87 (pose này vẽ nhỏ hơn).
- Đọc một prompt đã sinh: không còn ký tự `{` hay `[`, có `{design}` của lion nguyên văn.
- Không gọi mạng, không sửa file Python khác.

## Kết quả
(model điền)
