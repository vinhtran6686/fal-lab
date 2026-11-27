# Lưới hero từ master đã chốt: quy trình và bài học

Cách làm hoạt ảnh thân cho một nhóm hero (mỗi con một thiết kế riêng, không cùng tộc) bằng MỘT clip cho mỗi động tác. Đã chạy thật với 5 hero vẽ lại từ ảnh tham khảo (`out/heroes/_lineups/heroic_ref_five/`, tier L, style heroic). Các bước chung (cắt ô, giá, tách khung) ở `lineup-workflow.md`; doc này ghi phần khác của hero và các bài học rút từ những lần người dùng chốt hoặc trả lại.

## 1. Master: vẽ lại từ ảnh tham khảo (mỗi con một ảnh)
1. Hỏi một lần: class, tier, role, skills, tư thế idle; với ảnh tham khảo thêm: style (heroic), mức bám (bám sát thiết kế), tỷ lệ, màu, mặt (khi mũ che mặt).
2. Ảnh tham khảo: bản gốc vào `ref/style_board/hero_ref/` (giữ nguyên, ghi nguồn trong README); bản gửi model nằm trong `<asset>/.work/`: xóa chữ ký, logo, tên in trên ảnh, và **lật ngang nếu nhân vật quay trái** (master luôn quay phải).
3. Prompt: `docs/styles/heroic-vector-style/prompt-template-hero-faithful-redraw.txt` (mẫu đã chạy). Câu mở đầu "FAITHFUL REDRAW ... take ONLY its design, never its sketchy lines or dull colours"; đoạn nhân vật đếm mảng; câu idle viết theo **phía màn hình** ("the hand on the RIGHT side of the image"), không viết near/far vì ảnh lật làm đổi tay; danh sách Visible / NOT visible; COLOUR PLAN hex "màu gốc làm sáng hơn".
4. `prompt_lint.py`, một ảnh, `--ref` bản sạch, 1024×1024 low (~0,016 USD). 5/5 con đạt ở lần đầu.
5. Đã đo: model vẽ to hơn số xin khoảng 1,4-1,7 lần (xin 52-66% → được 82-95%); model theo tỷ lệ của ảnh tham khảo hơn số đầu trong prompt (xin 5 đầu cho ảnh gốc 7 đầu → ~6,5 đầu); nét viền mảnh dần nếu ảnh gốc nét mảnh. Kiểm bằng cách đặt các con cạnh nhau ở 84 px và 60 px.

## 2. Lưới: ghép bằng code, không vẽ lại
- Không vẽ ảnh lưới mới (thiết kế sẽ trôi). Lấy các master đã chốt, khóa nền, dán vào ô 512 px trên 2560×1440, rồi `lineup_regrid.py --cols 5 --rows 1 --heights 0.22,0.22,0.23,0.24,0.22 --feet 0.70 --x-margin 0.03`.
- 0,22 chiều cao ô = ~169 px trong clip 768P = L @2x, không cần phóng. Cao 0,30 thì mỗi con rộng 64-78% ô và đòn đánh chạm hàng xóm; 0,22 → 44-57%.
- Một hàng, khoảng trống lớn phía trên đủ cho nhảy (skill 1, skill 3).
- **Sửa riêng vài con**: tạo bản đầu vào chỉ giữ ô của các con đó (các ô khác tô magenta, cùng vị trí) rồi chạy một clip. Khung tách ra vẫn khớp lưới.

## 3. Viết prompt chuyển động (đã đạt)
Mẫu trong `prompts/hero-lineup-*.txt`. Khung cố định:
1. Câu mở: "Five separate fantasy heroes stand in five separate cells ... Each one performs its OWN ... the five are independent: never copy one hero's movement, pose or prop onto another."
2. Hệ quy chiếu (trái phải của màn hình, mục tiêu ngoài ô bên phải), "IN PLACE ... ends where it started, never leaves its cell ... its weapon never reaches into another hero's cell", giữ thiết kế và góc nhìn.
3. **Một đoạn đánh số cho mỗi hero**, gọi bằng hình dáng ("the armoured knight with the red crest (far left)"), từng nhịp theo bảng pha đã chốt với người dùng (`fal-image/format.md` §11 level 2).
4. Câu cuối cấm hiệu ứng **liệt kê đầy đủ** (no arrow, no fire, no light, no glow, no aura, no beam, no explosion, no ring, no projectile, no dust, no debris, no crack, no slash arc, no motion trail, no afterimage) + "only the bodies move" + nền magenta cố định.
5. Run: chạy tại chỗ "like on a treadmill" + `--last-frame` = ảnh đầu để lặp vòng; mỗi con cách di chuyển riêng (kéo búa, chạy, bay nhấp nhô, đi bộ).
6. Hiệu ứng (vệt chém, vòng phép, mưa tên, buff) KHÔNG nằm trong clip: làm sau bằng `lib-fx`, bám vào khung va chạm.

## 4. Bài học từ các lần chốt và trả lại
| Tình huống | Điều xảy ra | Cách làm đúng |
|---|---|---|
| Death: "its killing blow comes from an unseen attacker" | model vẽ một đòn lửa đánh vào cả 5 con | không mô tả gì từ bên ngoài đánh vào; nhân vật tự ngã; cấm lửa, nổ, đạn, va chạm |
| Câu chung cho cả nhóm | hành động lan sang con khác | mỗi con một đoạn riêng, câu "independent, never copy" (người dùng: "mỗi nhân vật phải độc lập") |
| Cung thủ: "the arrow simply vanishes" | 3 mũi tên bay sang ô bên cạnh | không có mũi tên nào: "pulls the bare string with two EMPTY fingers", cấm mũi tên hai lần; model vẫn vẽ một mũi tên lúc kéo dây → xóa khi tách khung |
| Cung thủ bắn trên không (nhảy rồi mới kéo) | kéo cung xảy ra trên đất | **giương cung sẵn trước khi nhảy**, chỉ nhả ở đỉnh cú nhảy, bàn tay bung ra rõ ("flies open behind his head") |
| Mưa tên | cần cung hướng trời, kéo thả liên tục | "aiming HIGH ... about 60 degrees", "THREE times in a row", mũi tên là vfx riêng |
| Xoay vòng với vũ khí dài (rìu) | đầu rìu chạm ô bên cạnh | tránh xoay với vũ khí dài trong lưới, hoặc chạy con đó riêng |
| Khổng lồ đá (vai to, đầu nhỏ) | khi đấm hoặc khom, đầu lún giữa vai, thân xoay đi, mất mặt | khóa "head, eyes, beard stay visible above his shoulders and face screen right in every frame", kết thúc đứng hoặc khom vừa; động tác to (giơ hai tay, dậm hai lần) cho ra hình sinh động hơn ("đơn điệu quá" khi chỉ dậm một lần) |
| Nhân vật bay | đẩy chưởng thành lao bay hoặc dang hai tay | chấp nhận được; ghi "never touches the ground" |

## 5. Nhân vật 1 (hiệp sĩ búa): động tác khó thì để model tự sáng tạo
Skill 3 của `cinder_maul` thử 5 lần. Bốn lần mô tả chi tiết đều hỏng: quét ngang (búa chĩa thẳng như giáo), "vòng tiếp về phía xa" (búa dừng ở sau lưng), combo 3 nhịp viết rõ (nhịp quét dừng sai phía), hất búa từ dưới lên (cuối nâng búa ngang như nâng tạ). Lần thứ năm chỉ viết chung: "unleashes a fierce combo of THREE different powerful strikes in a row ... choose the strikes freely and make them heavy, fast and varied ... hammer staying inside his own cell" → **người dùng chốt**.
Quy tắc: với cú vung ngang hoặc chuỗi đòn khó tả bằng hướng màn hình, sau **hai** lần mô tả chi tiết không đạt thì viết một câu mục đích (số đòn, tính chất, ràng buộc ô) và để model chọn đòn. Cú bổ và đập theo chiều dọc màn hình (attack, skill 1) model làm đúng ngay lần đầu.

## 6. Quy trình duyệt (người dùng, 2026-11-27)
- Sau mỗi clip: lưu clip, `job.json`, prompt vào `source/video/<động tác>_tNN/`, **chỉ gửi video** cho người dùng xem; không tách khung.
- Chốt theo từng con: một clip có thể lấy 2-3 con; bảng "clip nào cho con nào" trong `README.md` và `meta.json` (`pick`) của lưới. Mỗi lần làm lại vẫn chạy cả 5 con (người dùng: "lỡ các con kia có pose đẹp hơn"), trừ khi chỉ sửa riêng một con.
- Tách khung và chọn khung làm sau bằng `tools/frame_tuner/` (`docs/tools/frame_tuner/frame-tuner-guide.md`).
- Không làm clip: idle (rig từ master), levelup (idle + vfx), respawn (vfx sáng rồi hiện idle).

## 7. Chi phí đã đo
5 master × ~0,016 USD + 11 clip 768P 4 s × 0,12 USD ≈ 1,40 USD cho 5 hero × 6 động tác (attack, death, run, 3 skill), gồm 5 lần chạy lại.
