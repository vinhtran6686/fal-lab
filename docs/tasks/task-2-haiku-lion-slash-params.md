# T2 (Haiku): tham số vệt vuốt riêng cho lion + file requirements

Trạng thái: TODO

## Mục tiêu
1. Lion không còn mượn file tham số vệt chém của Holy Commander.
2. Có một file liệt kê thư viện Python mà Puppet Kit cần.

## Đọc trước
- `docs/tasks/README.md` mục "Quy tắc chung".
- `out/heroes/holy_commander/source/vfx/slash_diag/slash_params.json` (file gốc để chép).

## Được sửa
- Tạo mới `out/heroes/lion_brawler/source/vfx/claw_swipe/slash_params.json`
- Tạo mới `requirements-puppet.txt` (gốc repo)
- Sinh lại (bằng lệnh, không sửa tay): `out/heroes/lion_brawler/frames/fx/claw_swipe/`, `out/heroes/lion_brawler/frames/fx/slam/`, `out/heroes/lion_brawler/meta.json`
- `out/heroes/lion_brawler/brief.md`: chỉ hai dòng manifest `fx_claw_swipe` và `fx_slam` (cột Ghi chú)
- File task này và dòng T2 trong `docs/tasks/README.md`

## Việc cần làm
1. Chép `out/heroes/holy_commander/source/vfx/slash_diag/slash_params.json` thành `out/heroes/lion_brawler/source/vfx/claw_swipe/slash_params.json`.
2. Trong bản chép, sửa đúng các khoá sau (giữ nguyên mọi khoá khác):
   - `"note"`: `"Lion Brawler claw slash parameters (copied from holy_commander slash_diag, palette and width changed)."`
   - `layered.palette.deep`: `[150, 70, 10]`
   - `layered.palette.blue`: `[230, 140, 20]`
   - `layered.palette.ice`: `[255, 214, 60]`
   - `layered.palette.core`: `[255, 252, 235]`
   - `layered.width_scale`: `0.85`
   - `glow.color`: `[255, 190, 60]`
3. Chạy đúng 4 lệnh (từ gốc repo):
```bash
python scripts/puppet.py track out/heroes/lion_brawler out/heroes/lion_brawler/source/rig/anims/attack.json --name claw_swipe --sheet attack_side --sub 4
python scripts/puppet.py slash out/heroes/lion_brawler out/heroes/lion_brawler/source/rig/anims/attack.json --name claw_swipe --sheet attack_side --params out/heroes/lion_brawler/source/vfx/claw_swipe/slash_params.json
python scripts/puppet.py track out/heroes/lion_brawler out/heroes/lion_brawler/source/rig/anims/skill_slam.json --name slam --sheet skill_slam_side --sub 4
python scripts/puppet.py slash out/heroes/lion_brawler out/heroes/lion_brawler/source/rig/anims/skill_slam.json --name slam --sheet skill_slam_side --params out/heroes/lion_brawler/source/vfx/claw_swipe/slash_params.json
```
4. Mở `out/heroes/lion_brawler/frames/fx/claw_swipe/contact_with_body.png` bằng công cụ đọc ảnh: frame 8 phải có một dải vàng cong từ trên đầu xuống trước chân. Nếu không thấy dải nào, đặt BLOCKED.
5. Trong `brief.md` của lion, ở cột Ghi chú của hai dòng `fx_claw_swipe` và `fx_slam`, thay cụm "tham số màu mượn của holy_commander" (nếu có) bằng "tham số riêng: `source/vfx/claw_swipe/slash_params.json`"; dòng `fx_slam` thêm cùng cụm đó vào cuối ghi chú.
6. Tạo `requirements-puppet.txt` với đúng nội dung:
```
# Puppet Kit (scripts/puppet.py). The slash command also needs the last two.
numpy
pillow
scipy
opencv-python-headless
scikit-image
```

## Nghiệm thu
- 4 lệnh ở bước 3 chạy không lỗi; lệnh `slash` in dòng `slash fx ...`.
- `git status --short` chỉ có file thuộc mục "Được sửa" (các PNG trong hai thư mục fx sẽ đổi: đúng).
- `python scripts/source_prune.py out/heroes/lion_brawler` (chạy thử, không `--apply`) **không** liệt kê `source/vfx/claw_swipe`.

## Lưu ý
- Nếu `git pull --rebase` báo xung đột ở `meta.json` hoặc các PNG fx của lion: lấy bản remote (`git checkout --theirs` trong rebase là bản của mình; dùng `git checkout --ours <file>` để lấy bản remote), rồi chạy lại 4 lệnh ở bước 3.
- Lệnh `slash` cần `pip install opencv-python-headless scikit-image scipy numpy pillow`.
- Không đổi thuật toán, không sửa file Python nào.

## Kết quả
(model điền)
