# Issue: `.work/` không có trong git, mỗi nơi làm việc cắt ra frame khác nhau

Ngày: 2026-10-20 · Phát hiện khi export holy_commander (attack, death, charge_v4, respawn) trong cloud session.

## Vấn đề

- `out/**/.work/` nằm trong `.gitignore`. Set đã finish (`set_state.json`, frame đã key/đăng ký/retime, `fin_*.json`, `sel_*.json`) chỉ tồn tại trên máy đã sinh nó.
- `scripts/video_to_sheet.py` chỉ đọc từ set đó. Máy khác chỉ có clip trong `raw/` và các frame xem trước của `tools/kr_compare/sprites/`, nên phải tự dựng lại set. Cách dựng lại không được ghi ở đâu, nên mỗi phiên làm một kiểu và ra frame khác nhau.
- Ví dụ lần này: dựng lại bằng `sprite_set.py` thì `retime --auto-oneshot` nén attack về ~0.7 s và death về ~0.9 s, khác bản user đã duyệt (23 và 39 frame trong kr_compare). Phải đi đường vòng, dùng thẳng frame của kr_compare.
- Tham số "cắt frame" (bớt 1/2, cửa sổ, thang tỉ lệ, điểm neo chân, thời lượng mỗi frame, hit) nằm rải rác ở `build_manifest.py` (`decimate`, `fast_version`), `history.md`, report và lệnh chạy tay. Không có một nơi duy nhất.

## Công thức đã dùng lần này (làm chuẩn tạm)

Mã: `tools/kr_compare/export_frames.py` (đọc frame từ `tools/kr_compare/sprites/holy_commander/<state>/`, ghi set tạm `out/.../.work/side_export`, rồi `video_to_sheet.py`).

| Bước | Giá trị |
|---|---|
| Nguồn | clip trong `raw/` → `ffmpeg fps=15` → `sprite_pack.key_out()` (đúng như `extract_raw_clip`) |
| Bớt frame | `decimate` stride 2 (giữ frame 0, 2, 4...): attack t04 46→23, death t01 78→39. charge_v4 giữ 67, không bớt |
| Thang tỉ lệ | `120 / 268` (thân master cao 268 px trong clip 480 px; 120 = body tier M @2x). Cùng hệ số cho mọi clip của hero này |
| Neo chân | tâm ngang và đáy bbox (alpha > 24) của frame 0 mỗi clip, đặt tại (256, 400) trên canvas finish 512x512; không căn lại từng frame |
| Thời gian | 67 ms mỗi frame (15 fps), không retime, không bỏ đoạn đứng yên |
| Hit (attack) | 40% thời lượng = frame 10 |
| Despill | không (frame đúng như bản user đã duyệt) |
| Respawn | `--reverse` từ `despawn_side_extra_t01`, 78 frame, chưa bớt |
| Chuẩn thân | `video_to_sheet.py` tự rescale theo diện tích frame nghỉ so với run (`body_area_2x` 6083): x1.09; hệ quả canvas phải là 176x140 |

## Việc cần làm (đề xuất, chưa làm)

1. Đưa công thức vào một file có phiên bản trong git, ví dụ `out/<class>/<id>/export_recipe.json`: mỗi sheet có `source` (clip raw), `fps`, `stride`, `window`, `scale`, `anchor`, `duration_ms`, `hit`, `reverse`, `despill`.
2. Một script đọc recipe và dựng set + export (thay `export_frames.py`), để mọi máy chạy một lệnh ra cùng frame; kèm hash của frame đầu ra trong recipe để kiểm.
3. `build_manifest.py` đọc cùng recipe, không còn `decimate` riêng.
4. Quyết định có ghi vào `video-sprite/SKILL.md` không (phiên này không sửa SKILL.md).
5. Trước đó: kiểm khớp byte với bản đã export hôm nay (chạy lại recipe, so hash).

## Liên quan

- `docs/handoff-holy-commander-2.md` mục 0 ("dựng lại set từ clip trong raw/, route supplied") và 3B.
- `out/heroes/holy_commander/history.md` (các dòng export ngày 2026-10-20).

## Cập nhật 2026-10-20: đã có công cụ (tools/frame_tuner)

- Đã có `export_recipe.json` (`out/heroes/holy_commander/`) do **Frame Tuner** ghi (`tools/frame_tuner/`), và `tools/frame_tuner/apply_recipe.py` đọc recipe,
  dựng set tạm từ clip trong `raw/` rồi export bằng `video_to_sheet.py`. Mục 1 và 2 ở trên (recipe + script một lệnh) đã làm cho holy_commander.
- Đã kiểm mục 5: chạy lại recipe mặc định (đã chốt) cho attack, death, charge ra frame **trùng từng pixel** với bản đã export (23/23, 39/39, 67/67), cùng `hit_frame` và `body_rescale`.
- Còn mở: (3) `build_manifest.py` chưa đọc recipe (còn `decimate` riêng); (4) chưa quyết ghi vào `SKILL.md`; hash đầu ra chưa ghi trong recipe; chưa áp dụng cho run/idle.
- Thang tỉ lệ: attack/death/charge dùng cố định `120/268` (khớp bản đã duyệt); clip mới đo theo chiều cao thân hình 0.
