# Dựng động tác từ clip video tham chiếu: cắt pose, vệt chém, rig nhún

Phương pháp cho một động tác mà ảnh tĩnh sinh từng pose không nhất quán được (xoay người, quét vũ khí lớn). Thay vì sinh nhiều ảnh rời, ta **cho mô hình video làm một clip, chỉ cắt vài khung đúng pose từ clip**, thêm vệt chém từ `lib-fx` và nhún thân bằng rig lớp. Làm thử trên `out/heroes/moon_crane` (kỹ năng `skill_sweep`, tham chiếu là một hero KR5). Cùng họ với `docs/pipeline/pose-pair-fx-method.md` (hai pose + vệt + rig), khác ở chỗ hai pose lấy từ một clip nên cùng thân, cùng chân, cùng tỉ lệ.

## 1. Vì sao không dùng ảnh rời
Sinh từng pose bằng `fal-image` (có `--ref` pose) đúng hướng nhưng mỗi ảnh vẽ lại cả chân, kích cỡ và dòng đất khác nhau: ghép lại thì nhân vật giật, cắt thân trên ghép lên một bộ chân chung thì lộ vết cắt. Một clip video giữ nguyên nhân vật, cỡ và chân trong cả đoạn, nên các pose cắt từ nó khớp nhau.

## 2. Các bước
1. **Đọc động tác tham chiếu cho đúng** (bước quyết định, sai ở đây là fail cả quy trình).
   - Tách atlas và bảng animation: `docs/scripts/ref_atlas/ref-atlas-split-and-animations.md`.
   - Xem cả đoạn xung quanh (start, loop, end, idle), không chỉ một khoảng khung. Tìm **chuyển động chính duy nhất** và pose cuối thật sự (ở ví dụ, cú quét kết thúc là về tư thế idle chứ không phải một pose giơ cao).
   - Đo: chân và bóng có đứng yên không, hình nào lặp (on twos), hình nào chỉ nhích. Gộp thành **nhịp**, không phải mỗi hình một pose. Cho người dùng duyệt nhịp chính trước khi viết prompt (lần đầu chia sai thành 4 pose nên fail).
2. **Video tham chiếu**: `scripts/make_ref_video.py` trên đúng khoảng khung của chuyển động chính, không kèm khung thừa, `--seconds 3`. Đặt ở `ref/sprite/<tên>/`.
3. **Mô tả và prompt** (duyệt trước khi trả phí, theo `video-sprite` Phase A):
   - Chỉ mô tả **hướng và đường đi của động tác**, không viết mốc giây: để mô hình tự quyết nhịp.
   - Nói rõ **vị trí đường quét** (từ trái sang phải, tầm nào). Không nói thì mô hình tự bịa đường quét qua đầu.
   - Cấm thẳng những gì không muốn ("thương không bao giờ ngang qua đầu"). Chỉ một động tác, không có tư thế cuối thừa.
   - Chân: "giày đứng yên một chỗ, không trượt". Khung hình: nhân vật nhỏ khoảng nửa chiều cao khung, lề rộng, cả vũ khí nằm trong khung, nền magenta, không hiệu ứng.
   - `aspect_ratio` 16:9 cho vũ khí dài (1:1 bị cắt mép), `duration` 3 s.
4. **Gọi** `minimax/h3-max/reference-to-video` (0,05 USD mỗi giây; 3 s = 0,15 USD). Mã chạy lưu cạnh clip (`<sheet>_ref_tNN.run.py`, `.prompt.txt`, `.json`); ghi chi phí vào `out/costs.csv`. Xem kết quả bằng 12 khung theo cùng tỉ lệ thời gian cạnh tham chiếu.
5. **Chọn pose, không dùng cả clip**: người dùng chỉ giây nào là pose 1, giây nào là pose 2. Nhịp nào đúng thì lấy, nhịp mô hình bịa thì bỏ; clip không cần đúng toàn bộ.
6. **Cắt pose** (`out/<hero>/source/fx/skill_sweep_cut.py` là mẫu): tách nền magenta (màu nền ước lượng từ bốn góc, alpha theo khoảng cách, khử viền hồng), đặt từng pose lên ô của nhân vật với **cùng một tỉ lệ** (lấy từ pose A) và **cùng điểm đặt chân** (giữa hai giày ở hàng đáy). Điểm đặt chân cố định là thứ chống giật; căn theo khung bao cả thương làm thân nhảy.
7. **Vệt chém**: `lib-fx` `melee/slash/crescent`, `--from` mũi vũ khí pose A, `--to` mũi pose B, `--set slash.bend=-0.2` (âm = bụng vệt võng xuống, đi ngang hông rồi vút lên), `slash.width=28`, `streaks.off=true`, `--split` (lớp sau nằm dưới thân, lớp trước đè lên thân). Dạng `sweep` (bầu dục lớn) che hết thân của nhân vật nhỏ, không dùng. Màu `frost` mới là tạm.
8. **Rig lớp nhún** (`skill_sweep_compose.py`, không dùng Puppet Kit): ba lớp từ chính hai pose, không cần plate.
   - chân: cắt ở thắt lưng, giày cố định, chân chỉ méo ngang rất nhẹ (0 ở đế);
   - thân trên: nghiêng quanh thắt lưng, trượt nhẹ, co dãn;
   - vũ khí ngoài bàn tay (cắt dọc theo cán): quay trễ, ngược chiều khi thân đổi hướng.
   Nhịp: **đứng yên, MỘT nhịp ngả ra sau (lấy đà), cắt sang pose B cùng vệt, MỘT nhịp quá đà về phía đòn rồi bật lại và tắt dần, dừng** (quán tính sau đòn). Không nhún liên tục: nhún đều bị chê là đơ. Ở ví dụ (15 fps, mỗi khung một hình): A đứng yên 4, ngả 4, cắt cùng vệt 1, B quá đà 15 khung (vệt phủ 9 khung đầu).
9. **Xuất và dọn**: giữ clip đã duyệt trong `source/video/`, xoá clip bị loại, ghi manifest và `history.md`.

## 3. Giới hạn và bài học
| Điều | Thực tế |
|---|---|
| Clip nhiều nhịp có xoay thân, quay lưng | mô hình không theo; chỉ lấy nhịp đúng hoặc chia nhỏ clip |
| Mô tả có mốc giây | mô hình ép nhịp sai; bỏ mốc, chỉ nêu thứ tự |
| Không nêu đường quét | mô hình quét qua đầu, thương bị méo |
| Hai pose, không có hình trung gian | cắt thẳng + vệt che chuyển (cách game gốc làm); cần hình trung gian thì chọn thêm khung từ clip |
| Cánh, nắm đấm | chỉ thương được tách lớp; cánh hạc và nắm đấm đi theo thân |
| Cổng chất lượng vệt (`lib-fx` `fxcheck`) | báo FAIL ở cảnh báo `cut` (đuôi vệt tắt đột ngột); chưa chỉnh |
| Mã cắt và ghép | hằng số của riêng `moon_crane` (khung chọn, đường cắt thắt lưng, điểm cắt cán) nằm đầu hai script; tách thành file JSON khi dùng cho nhân vật thứ hai |

## 4. File
- `out/<hero>/source/video/<sheet>_ref_tNN.{mp4,json,prompt.txt,run.py}`: clip đã duyệt và cách gọi lại.
- `out/<hero>/source/fx/skill_sweep_cut.py`, `skill_sweep_compose.py`: cắt pose, ghép vệt và rig.
- `out/<hero>/frames/skill_sweep/`: `pose_A.png`, `pose_B.png`, `cut.json`, `frames/`, `preview.gif`, `sheet.png`; `frames/fx/skill_sweep/` là vệt dựng bằng lệnh trong `meta.json` của nó.
