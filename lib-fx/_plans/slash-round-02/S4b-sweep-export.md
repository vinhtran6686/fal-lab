# S4b: xuất chính thức skill chém ngang (`skill_sweep_side`) cho `azure_blade`

Nguồn: S4 đạt, người dùng cho phép xuất (2026-11-14). Hiện thân và vệt chỉ nằm trong `.work/`. Việc này đưa chúng vào `frames/` đúng bố cục của skill đã có (`skill_crescent_side`)
và cập nhật manifest. **Không đổi số nào của S4** (anim, rig, lệnh vệt giữ nguyên).

## Đọc trước
`CLAUDE.md` (mục asset folder, lib-fx "For a character"), `docs/pipeline/asset-manifest.md`, kết quả S4: [S4-sweep-body-timing.md](S4-sweep-body-timing.md) mục "Kết quả",
mẫu ghép đã duyệt: `out/heroes/azure_blade/source/vfx/crescent/build_crescent.py` (dòng 32-40: đọc thân; 158-200: ghi `@2x`, `@1x`, GIF, `contact.png`).

## File được tạo / sửa
- Tạo (mới hết): `out/heroes/azure_blade/frames/skill_sweep_puppet_side/` (thân), `out/heroes/azure_blade/frames/fx/sweep/` (vệt),
  `out/heroes/azure_blade/source/vfx/sweep/build_sweep.py` (script ghép), `out/heroes/azure_blade/frames/skill_sweep_side/` (thân + vệt). Thêm vào git bằng `git add -f`.
- Sửa: `out/heroes/azure_blade/brief.md` (mục 2 và dòng manifest), `out/heroes/azure_blade/history.md` (một dòng), `out/heroes/azure_blade/meta.json` (chỉ những gì `puppet.py render` tự thêm cho sheet mới).
- **Không sửa** bất cứ thứ gì của `skill_crescent_*`, `fx/blade_charge*`, rig / anim của S4, ảnh trong `source/design/`. Không sửa `lib-fx/`, `scripts/`.

## Bước
1. **Thân**: `python scripts/puppet.py render out/heroes/azure_blade out/heroes/azure_blade/source/rig/anims/sweep.json --sheet skill_sweep_puppet_side` (không `--no-export`).
   **Kiểm**: `frames/skill_sweep_puppet_side/frames/@2x/` có 21 ảnh 352x280; `git diff out/heroes/azure_blade/meta.json` chỉ thêm khối của sheet mới.
2. **Vệt** (đúng lệnh của S4, chỉ đổi `--out`):
   `python lib-fx/build.py melee/slash/sweep --pal frost --fps 15 --split --s 0.707 --swing "tip_a=110.1,185.0;root_a=148.6,187.6;pivot=178.0,185.0;tip_b=251.5,174.8;root_b=205.7,173.7;pivot_b=177.5,172.8;tip_c=177.3,196.9;root_c=177.5,181.1;pivot_c=177.4,181.1" --out out/heroes/azure_blade/frames/fx/sweep`
   **Kiểm**: `meta.json` của vệt: 9 khung, `hit_frame` 3, `qa.fail` rỗng; có `back/`, `front/`.
3. **Ghép** bằng `source/vfx/sweep/build_sweep.py` (đầu file ghi lệnh chạy và nguồn như `build_crescent.py`): với mỗi khung thân k = 1..21, n = k - 5:
   nền trong suốt; nếu 1 <= n <= 9 dán `fx/sweep/back/@2x/sweep_NN.png` tại `origin` (đọc từ `fx/sweep/meta.json`, không ghi cứng); dán thân; dán `front/` cùng chỗ.
   Ghi `frames/skill_sweep_side/frames/@2x/hero_azure_blade_skill_sweep_side_KK.png` và bản `@1x` (thu nửa, LANCZOS), `preview_2x.gif`, `preview_game_1x_x3.gif`, `contact.png`
   (cùng cách như `build_crescent.py` dòng 170-196, 15 fps). Ghi `frames/skill_sweep_side/export_meta.json`: `fps` 15, `frames` 21, `hit_frame` 8, `fx_offset` 5, lệnh dựng lại thân, vệt, ghép.
4. **Manifest** `brief.md`:
   - mục "### 2. Quét ngang": tên đổi thành ba pose (`pose_skill_sweep_p1`, `p2`, `p3` + `melee/slash/sweep`); thay đoạn mô tả cũ (hai pose, "chưa đo điểm bám, chưa dựng rig") bằng 3 dòng:
     thứ tự A -> B -> C (cung 270 độ qua nửa xa), rig một mảnh x3 + `anims/sweep.json` 21 khung (lấy đà 6, chém 1, trúng đòn 6, nghỉ 8, hit 8), vệt `melee/slash/sweep --swing` ba điểm từ sockets của rig.
   - dòng `skill_sweep_side`: trạng thái ✅ (người dùng duyệt 2026-11-14), ghi chú: 21 khung @15 fps, hit 8, `frames/skill_sweep_side/`, dựng lại: `python out/heroes/azure_blade/source/vfx/sweep/build_sweep.py` (sau bước 1, 2).
   - thêm dòng `skill_sweep_puppet_side` (Puppet Kit, one-shot, ✅, thân không vệt) và `fx_sweep` (`lib-fx melee/slash/sweep`, hiệu ứng, ✅, `frames/fx/sweep/`).
   `python scripts/asset_status.py azure_blade` phải đọc được các dòng mới (không lỗi).
5. `history.md`: một dòng ngày 2026-11-14: xuất `skill_sweep_side` (ba pose, rig + vệt ba điểm), nguồn S4.

## Tiêu chí nghiệm thu
- `frames/skill_sweep_side/frames/@2x/` 21 ảnh; ảnh khung k so với ảnh ghép tự dựng của người lập kế hoạch giống hệt từng điểm ảnh hoặc chênh tối đa 1 mức màu (cùng thân, cùng vệt, cùng `origin`).
- Khung 6 có lát mỏng trên lưỡi A, khung 7 đầu vệt ở mũi B, khung 8 đầu vệt ở nêm C (mở `contact.png` ra xem); khung 1-5 và 15-21 không có vệt.
- `git diff --stat` trong `out/` chỉ gồm file của mục "File được tạo / sửa"; không đổi file nào của `skill_crescent_*`.
- `python lib-fx/build.py melee/slash --check` không FAIL. Không chạy công cụ tốn tiền, không đọc `.env`. Commit + push lên `ccr-38411bc5-l13uki`, đánh dấu ô S4b trong `PLAN.md`.

## Báo cáo (điền dưới đây)
Danh sách file tạo / sửa (`git diff --stat`), đường dẫn `contact.png` và GIF, kết quả `asset_status.py`, lệch so với task và lý do.

## Kết quả
**Trạng thái: xong. Ghép chính xác, không đổi số nào của S4. 1 lệch nhỏ ở `meta.json` (xem cuối).**

### File
`git diff --stat` (file đã có): `out/heroes/azure_blade/brief.md` (+7 -3), `history.md` (+1), `meta.json` (+41 -1). File mới (`git add -f`): `out/heroes/azure_blade/frames/skill_sweep_puppet_side/`, `frames/fx/sweep/`, `frames/skill_sweep_side/`, `source/vfx/sweep/build_sweep.py` (152 file). `skill_crescent_*`, `fx/blade_charge*`, rig / anim S4, `source/design/`, `lib-fx/`, `scripts/` không đổi.

### Ảnh
- contact: `/home/user/fal-lab/out/heroes/azure_blade/frames/skill_sweep_side/contact.png`
- GIF: `/home/user/fal-lab/out/heroes/azure_blade/frames/skill_sweep_side/preview_2x.gif`, `/home/user/fal-lab/out/heroes/azure_blade/frames/skill_sweep_side/preview_game_1x_x3.gif`

### Số đo (script tạm ở scratchpad, không vào repo)
- Thân: 21 ảnh 352x280 @2x. Vệt: 9 khung, `hit_frame` 3, `qa.fail` rỗng (`warn` rỗng), có `back/`, `front/`, `origin` (80, 106).
- `skill_sweep_side`: 21 ảnh @2x và @1x. So từng khung với ghép độc lập (cùng thân, vệt, origin, composite "over" bằng numpy): chênh tối đa 1,16 / 255 (làm tròn 8 bit, tức <= 1 mức màu).
- Vệt có mặt chỉ ở khung 6-11 (tổng alpha khác thân: 111, 776, 1870, 1295, 589, 114); khung 1-5 và 12-21 không có vệt (0). Khung 6 lát mỏng xanh trên lưỡi A, khung 7 đầu vệt ở mũi B, khung 8 đầu vệt ở nêm C (mở `contact.png` và ảnh phóng khung 6-8).
- `python lib-fx/build.py melee/slash --check`: không FAIL (còn cảnh báo `linger` có sẵn của `melee/slash/sweep`).
- `asset_status.py azure_blade` đọc được ba dòng mới (`skill_sweep_side` ✅, `skill_sweep_puppet_side` ✅, `fx_sweep` ✅), tổng "Xong 12/18", không lỗi.

### Lệch
1. `puppet.py render` ghi vào `meta.json` ngoài khối sheet mới còn thêm ba tên pose `pose_skill_sweep_p1/p2/p3` vào `sources.design` (danh sách ảnh gốc của các rig của sheet). Giữ lại vì do chính lệnh render tự thêm cho sheet này và đúng chuỗi nguồn; không đụng phần nào khác của `meta.json`.
2. `export_meta.json` có thêm `fx_origin_2x` và lệnh vệt có dấu nháy quanh `--swing` (lệnh `rebuild` trong `meta.json` của vệt không có nháy, không chạy lại được trực tiếp).
