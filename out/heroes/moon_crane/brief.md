# moon_crane (Hạc Nguyệt Phủ Sĩ)

style: chunky (`.claude/skills/fal-image/style-chunky.md`)

## Request
User (2026-11-15): nhân vật nam, cầm vũ khí, có giáp, phong cách mới lạ và có tính thẩm mỹ, để thử phong cách và thử vệt chém của vũ khí hạng nặng.
Chạy `/fal-image --creative` (ý tưởng ngắn của người dùng). Mẫu tham khảo của người dùng: các nhân vật hoạt hình chắc khối kiểu tower defense (tỉ lệ khoảng 3 đầu, nét viền nâu đậm, màu phẳng 3-4 tông) và một số concept painterly.

## Concepts offered (2026-11-15)
- A. Hạc Nguyệt Phủ Sĩ: thanh lịch, giáp vai cánh hạc khổng lồ, vũ khí vành trăng khuyết. **Chọn.**
- B. Thanh Đồng Cự Phủ: nặng, mũ mặt nạ có mào, giáp đồng gỉ, hoạ tiết nghi lễ.
- C. Sa Phủ Vệ: giáp vảy phân đoạn, lapis và cát, vũ khí cong lai loan đao.
Người dùng chọn A, sau đó đổi vũ khí rìu -> cây thương (nhìn hợp phong cách hơn).

## Class / size
- Class: hero (`classes/hero.md`), tier M, `{H}` 60 px, canvas 176x140 @1x
- Role: melee
- **Ngoại lệ so với skill, theo yêu cầu người dùng**: tỉ lệ khoảng 3 đầu (skill mặc định 3,5-4,5), nắm đấm to bằng mặt; vẫn nghiêm, không dễ thương.

## Slots
- `{id}`: moon_crane; `{body}`: biped; style: chunky
- `{design}` (master v08, **người dùng chốt 2026-11-15, "style này ổn nhất và khớp với mong đợi"**): xem `source/design/prompts/master_p08.txt` (nguyên văn).
  Tóm tắt: chiến binh nam ~3 đầu, mặt tối giản (mày dày, hai mắt vàng phát sáng, râu một mảng), búi tóc cao dây đỏ gạch; giáp vai cánh hạc ngà ở vai bên phải ảnh, vai trái tròn nhỏ;
  giáp ngực xanh slate với một chim vàng lớn, thắt lưng nâu khoá vàng, dải đỏ gạch, vạt áo rách mũi; găng có dải vàng dày và trăng khuyết vàng;
  một cây thương quá cỡ (cán nâu cao hơn người, mũi thương lá bạc xanh nhạt, chắn trăng khuyết vàng, tua đỏ gạch, một đá đỏ cam) cầm bằng tay bên trái ảnh, tay kia nắm đấm.
- **COLOUR PLAN (hex)**: xanh slate 210° `#26394F #3F5F80 #7FA0C0 #BBD3E6`; họ ấm (da, da thuộc, cán) `#C98A55 #8E5A3A #E8B684 #6A4430 #4A2E22`; vàng `#D6A03A #8A5E1A #F2D678` (chỉ dải dày);
  ngà `#EFE2BE / #BFAE8A` chỉ cho cánh hạc; mũi thương `#DDE9F2 / #7FA0C0`; đỏ gạch `#B5472F` nhỏ; mắt `#FFE9A6`; viền `#2B1E22`.
- `{idle}`: đứng thẳng chân rộng, đầu nghiêng ~8 độ, vai trái hạ ~5%, thương nghiêng ~8 độ, đuôi cán chạm đất.
- `{skills}`: đã làm thử **chém ngang quay người** (video thô đã chốt, xem manifest). Hướng khác: đâm thẳng, bổ từ trên xuống.

## Lưu ý thiết kế (bài học riêng của nhân vật này, bài học chung đã vào `style-chunky.md`)
- Mô hình ảnh bỏ qua yêu cầu "màu trầm"; hài hoà đến từ số họ màu và bảng hex, không từ giảm bão hoà.
- Cánh hạc đọc rõ nhất ở 60 px; mũi thương và mắt phát sáng là điểm nhìn. Thương dài chiếm ~90% chiều cao ảnh nên phải thu nhỏ khi ghép vào ô.

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v08 | user chốt 2026-11-15, style chunky |
| icon | fal-image | ảnh tĩnh | ⏭ | chưa làm |
| skill_sweep_spear (nguồn video) | video-sprite (h3-max-turbo, 2 take ghép) | video thô | ✅ chốt 2026-11-15 | `source/video/sweep_spear_join.mp4`: 88 khung @24 fps 768x768, chém ngang quay người 3 pose A/B/C (thương sau lưng -> hai tay trước ngực -> một tay hất ra sau lưng); dựng lại `python out/heroes/moon_crane/source/video/build_sweep_join.py`; giới hạn trong `sweep_spear_join.json`; chưa tách key / đăng ký / xuất frames |
| pose_horse_stance | fal-image (ảnh mẫu 1 khung) | ảnh tĩnh | ✅ 2026-11-15 | `source/design/pose_horse_stance_v01.png`: tấn thấp, thương vắt ngang vai, tư thế chép từ một khung của user; cắt và thu lại để lề 10%; thân vẫn gần chính diện |
| skill_spin_back (nguồn video) | video-sprite (h3-max-turbo, 5 s) | video thô | ✅ chốt 2026-11-15 | `source/video/skill_spin_back_v5_t01.mp4`: một cú quét ngang hông liên tục (thương nằm ngang), thân xoay từ hông, quay lưng về người xem, mắt luôn nhìn mục tiêu bên phải, giữ thế cuối; prompt `prompts/skill_spin_back_v5.txt`; vệt thừa của mô hình bị loại ở bước tách nền (key chặt), xem history; chưa xuất frames, chưa ghép fx |
| skill_spin_thrust (proxy chuyển động) | motion_proxy | thông số + khối 3D | ⏳ chờ duyệt | `source/rig/proxy_spin_thrust.json`: quét 360 ngang eo rồi đâm, 27 khung @15 fps, tỉ lệ đo từ master_v08, nhịp ghép theo pha với `ref/king` nhân vật 1; 10/10 tiêu chí đo (chân chéo khi xoay được vạt áo che, theo lựa chọn của user); dựng lại `python scripts/motion_proxy/build.py out/heroes/moon_crane/source/rig/proxy_spin_thrust.json` (kết quả trong `.work/`); bước sau: khung khoá bằng gpt-image-2 từ `blocks/` |
| pose_sweep_guard / windup / hit / follow | fal-image (khung khoá từ motion proxy) | ảnh tĩnh | ✅ v01 user duyệt 2026-11-16 | 4 khung khoá của skill quét thương (bản lai HY-Motion seed1), master + khung khối proxy làm tham chiếu; 0,0756 USD; xem history 2026-11-16 |
| skill_spear_sweep (animation, đổi tranh v1) | motion_proxy compose | 23 khung @15 fps | ⏳ chờ duyệt | dựng lại: `python scripts/motion_proxy/build.py source/rig/proxy_spear_sweep_hy.json --layers source/rig/hybrid_spear_sweep.json --out .work/motion_proxy/spear_sweep/hybrid` rồi `compose.py source/rig/compose_spear_sweep.json --out .work/motion_proxy/spear_sweep/compose`; chưa xuất vào `frames/` (canvas hero 176x140) |
| pose_skill_* | fal-image | ảnh tĩnh | ⏭ | chưa chọn kỹ năng |
| run_side, attack_side, death_side, pose_respawn, respawn_side, levelup_side, package | - | - | ⏭ | ngoài phạm vi thử phong cách |

## Video thử chém ngang (2026-11-15)
- Ba pose ảnh tĩnh sinh bằng prompt không đạt (cứng, đối xứng); thay bằng các khung của video v01. Pose A, B, C lấy từ take a ở 1,5 s / 2,8 s / 4,3 s.
- Ghim khung đầu và cuối A và B trong một clip khiến mô hình vung thương qua đầu (thử hai lần). Cách dùng được: take không ghim cộng clip B->C ghim, bỏ các khung nhoè.

## Pose stills từ motion proxy (2026-11-16): design note (preflight)
1. Yêu cầu: user duyệt chuyển động lai (HY-Motion seed1 + lớp đặt tay), muốn "apply đúng nhân vật master" → hướng A: 4 khung khoá vẽ bằng gpt-image-2 low, sau đó rig cắt lớp cho khung giữa. Hero M, melee, nam, thương.
2. Preset chunky, thân brawny; đoạn mô tả thân và thương chép nguyên văn từ prompt `pose_horse_stance_v01` (đã giữ đúng thiết kế), không viết lại.
3. Tỉ lệ: như master (≈3 đầu, nắm đấm to bằng mặt, chân ngắn); không đổi.
4. Thương: dài hơn người ~13 %, mũi lá nằm trên trục cán, chắn trăng khuyết hai sừng ngang cán; hai tay cùng nắm.
5. Khung: hình chiếm 42 % chiều cao ảnh (như pose trước), mũi và đuôi thương cách mép ≥ 8 %.
6. Đặc trưng: cánh hạc ngà trên vai trái nhân vật, mũi thương bạc to.
7. Màu: bảng hex của master (không đổi).
8. Mặt: như master.
9. Tư thế: lấy từ `frames.json` của bản lai, ảnh mẫu = khung khối proxy (`.work/pose_refs/ref_*.png`); hướng thân theo `action-planes.md` §4b, mô tả theo §9 (trái/phải của ảnh, mục tiêu bên phải ở ngang eo):
   | Khung | Pha | Hướng thân | Đầu | Chân | Thương |
   |---|---|---|---|---|---|
   | 00 | thủ thế | OPEN TO THE VIEWER, hông quay phải | nghiêng nhìn phải | so le, sau trái, trước phải | chéo trước thân, mũi phải ngang hông |
   | 10 | gồng (thay 09: ở 09 thương chĩa thẳng vào camera, không đọc được) | OPEN TO THE VIEWER, ngực quay trái | ngoái nhìn phải | so le, trọng tâm chân sau | kéo về trái ngang vai, đuôi phải ngang hông |
   | 13 | trúng | side view facing RIGHT 30° | nghiêng nhìn phải | lunge, chân trước phải | thẳng ngang eo, mũi ở mục tiêu |
   | 16 | theo đà | VIEWED FROM BEHIND (back 3/4) | ngoái nhìn phải | hai chân sát dưới hông | sau thân, mũi trên vai phải |
10. Lint: `prompt_lint.py --kind pose --body brawny` sạch cả 4 (đã bỏ "slightly", thêm câu lề mũi thương).
11. Chi phí: 4 ảnh low có 2 ảnh tham chiếu ≈ 0,08 USD (user duyệt).
