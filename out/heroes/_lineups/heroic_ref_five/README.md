# heroic_ref_five: 5 hero vẽ lại từ ảnh tham khảo, video chung một lưới

Lưới: `source/design/lineup_v01_regrid.png` (5 cột x 1 hàng, ghép bằng code từ 5 master đã chốt, mỗi con cao ~169 px trong clip 768P = L @2x).
Thứ tự ô (trái sang phải): `cinder_maul`, `ash_ranger`, `pale_seraph`, `red_axe`, `magma_giant`.
Mọi clip: `minimax/h3-max-turbo` 768P (1344x768), 4 s, 24 fps, 107 khung; prompt trong `source/video/prompts/`; tham số và nhận xét trong `meta.json`.
**Tách, dọn, chọn khung và xuất**: Frame Tuner (`tools/frame_tuner/frame_tuner.bat`) đọc `sprite_prep.json` của lưới này (bảng sheet, take và take đang chọn dưới đây).

## Clip chọn cho từng nhân vật
| Động tác | cinder_maul | ash_ranger | pale_seraph | red_axe | magma_giant |
|---|---|---|---|---|---|
| attack | attack_t01 | attack_t01 (shoot) | attack_t01 | attack_t01 | attack_t01 |
| death | death_t01 ¹ | death_t01 ¹ | death_t01 ¹ | death_t01 ¹ | death_t01 ¹ |
| run (loop) | run_t01 (kéo búa) | run_t01 | run_t01 (bay lướt) | run_t01 | run_t01 (đi bộ) |
| skill 1 | skill1_t01 leap_slam | skill1_t01 pierce_shot | skill1_t01 soul_field | skill1_t01 axe_combo | skill1_t01 lava_fist |
| skill 2 | skill2_t01 quake | skill2_ash_t02 arrow_rain ² | skill2_t01 cape_storm | skill2_t01 axe_whirl ³ | skill2_t01 stone_skin |
| skill 3 | skill3_t05 combo 3 đòn | skill3_t04 leap_shot ² | skill3_t01 soul_beam | skill3_t01 war_cry | skill3_t02 stomp |

¹ bỏ các khung có đòn lửa do model tự vẽ. ² xóa mũi tên model vẽ lúc kéo dây (mũi tên là vfx riêng). ³ lúc xoay đầu rìu chạm sang ô pale_seraph.
Skill 3 có bản dự phòng cho seraph, red_axe, giant trong t02, t04, t05. `skill2_ash_t02` chỉ có ô ash_ranger (cùng vị trí). `skill3_knight_ash_t03` không dùng.
Không làm clip: idle (rig từ master), levelup (idle + vfx), respawn (vfx sáng rồi hiện idle).
