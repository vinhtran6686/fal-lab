| date | sheet/still | vNN | model | score | approved/rejected/final/awaiting user | issue | change for next version | requested by (pipeline/user: "...") |
|---|---|---|---|---|---|---|---|---|
| 2026-11-27 | master | v01 | gpt-image-2 low (ref: ảnh tham khảo đã xóa chữ ký) | 7.5 | approved (user: "chốt ảnh trên nha") | rất khớp ảnh gốc (tóc, capelet vàng, ngọc xanh, áo choàng rách có lỗ, tư thế bay); nhưng ~6,5 đầu (hỏi 5, model theo ảnh gốc) và nét viền mảnh hơn hẳn cinder_maul / ash_ranger; mặt quay gần chính diện; chiếm 92% khung | nếu vẽ lại: tỷ lệ thấp hơn + nét viền dày như 2 con trước (gửi kèm cinder_maul làm ref style) | user: "tiếp tục với" |

## 2026-11-28: skill2 cape_storm tách khung, dọn, ghép Charge v2 (chờ duyệt)
- Tách `skill2_t01` (lưới heroic_ref_five) bằng `scripts/sprite_prep/prep.py split`: 107 khung 24 fps.
- Dọn (`out/heroes/_lineups/heroic_ref_five/prep/pale_seraph/skill2_t01.edits.json`): `despill` 12, `sharpen` 0,8, `specks` 40; khung 48-51 xoá mũi tên
  của ash_ranger lọt sang ô (`erase` ngoài người + `erase_tint` sát người).
- Pha: 0-11 lấy đà, 12-33 cuộn áo xoay, 34-47 bung áo (đòn chính), 48-80 áo hạ, 81-106 về đứng.
- Ghép Charge v2 (Prism Spark quấn quanh thân theo bóng dáng, 5 màu): lệnh trong `lib-fx/_core/formulas/rules/vfx/lightning/README.md` §8; kết quả
  trong `.work/fx/cape_storm_prism/` (chưa vào git); xem ở https://claude.ai/artifact/4cbfa2MD123GvG3iVK3ubb.
