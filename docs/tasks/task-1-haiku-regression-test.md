# T1 (Haiku): test hồi quy bằng hash frame cho Puppet Kit

Trạng thái: DONE 2026-11-11 (Haiku)

## Mục tiêu
Một lệnh cho biết việc sửa engine có làm đổi frame của các animation đã có hay không.

## Đọc trước (chỉ cần hai thứ)
- `docs/tasks/README.md` mục "Quy tắc chung".
- Trong `scripts/puppet.py`: hàm `render_frames(asset, anim, meta, body_only=False)` trả về `(cells, socks, c2)`; `cells` là danh sách ảnh PIL RGBA. Lớp `Animation(path, asset_dir)` ở `scripts/puppet_kit/core.py`.

## Được sửa
- Tạo mới `scripts/puppet_test.py`
- Tạo mới `scripts/puppet_kit/golden.json`
- File task này và dòng T1 trong `docs/tasks/README.md`

## Việc cần làm
1. Viết `scripts/puppet_test.py` theo đúng khung sau (điền phần `...`):

```python
#!/usr/bin/env python3
"""Regression test of the Puppet Kit: every listed animation must render to the same frames as recorded.
  python scripts/puppet_test.py            # compare with scripts/puppet_kit/golden.json, exit 1 on any difference
  python scripts/puppet_test.py --update   # record the current frames as the new reference
"""
import argparse, hashlib, importlib.util, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("puppet_cli", ROOT / "scripts" / "puppet.py")
pp = importlib.util.module_from_spec(spec); spec.loader.exec_module(pp)
from puppet_kit.core import Animation  # noqa: E402

GOLDEN = ROOT / "scripts" / "puppet_kit" / "golden.json"

def cases():
    """Every anims/*.json of every asset that has source/rig/anims/."""
    for anim in sorted(ROOT.glob("out/*/*/source/rig/anims/*.json")):
        yield anim.parents[3], anim          # asset dir, anim path

def digest(asset, anim_path):
    meta = json.loads((asset / "meta.json").read_text(encoding="utf-8"))
    cells, _, _ = pp.render_frames(asset, Animation(anim_path, asset), meta)
    h = hashlib.sha256()
    for c in cells:
        h.update(c.tobytes())
    return h.hexdigest(), len(cells)
...
```

2. `main()`: với mỗi case tính `digest`; khoá trong JSON là đường dẫn anim tương đối so với `ROOT`, dạng posix; giá trị `{"sha256": ..., "frames": n}`.
   - `--update`: ghi `golden.json` (indent 1, khoá sắp xếp), in số case.
   - Không có cờ: so với `golden.json`; in một dòng `ok  <khoá>` hoặc `DIFF <khoá>` hoặc `NEW  <khoá>` (case chưa có trong golden); cuối cùng in tổng; `sys.exit(1)` nếu có DIFF hoặc NEW.
3. Chạy `python scripts/puppet_test.py --update`, rồi chạy lại không cờ: mọi dòng phải `ok`, mã thoát 0.
4. Chạy lần thứ hai không cờ để chắc kết quả lặp lại được (tất định).

## Nghiệm thu
- `python scripts/puppet_test.py` in toàn `ok`, mã thoát 0, hai lần liên tiếp.
- `golden.json` có đúng số khoá bằng số file `out/*/*/source/rig/anims/*.json` (hiện là 12; nếu khác thì ghi số thật vào Kết quả).
- Không file nào khác bị đổi (`git status --short` chỉ có các file ở mục "Được sửa").

## Lưu ý
- Cần `pip install numpy pillow scipy`. Không cần mạng, không cần `FAL_KEY`.
- Không sửa `puppet.py` hay `core.py`. Nếu import lỗi, ghi lỗi vào Kết quả và đặt BLOCKED.
- Khi Fable sửa engine (task F2), hash sẽ đổi có chủ ý; khi đó Fable tự chạy `--update`. Đây không phải việc của task này.

## Kết quả
- 15 animation cases (3 new: death, hurt, skill_roar của lion_brawler, không có trong tính toán ban đầu)
- `python scripts/puppet_test.py` in toàn `ok`, mã thoát 0, hai lần liên tiếp ✓
- `golden.json` có 15 khoá (tương ứng với 15 file animation)
- Chỉ `scripts/puppet_test.py` và `scripts/puppet_kit/golden.json` được tạo mới
- Import và chạy thành công, không lỗi
