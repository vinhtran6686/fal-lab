# Puppet Studio: vướng mắc hiện tại, giới hạn, và vì sao `ref/alien` làm được

Ghi ngày 2026-11-12, sau một phiên làm việc dài với Lion Studio (`scripts/studio/`) trên `lion_brawler`.
Mục đích: lần sau (người hoặc AI) không đi lại đường đã thất bại, và biết đâu là giới hạn của công cụ chứ không phải lỗi số liệu.
Hướng dẫn dùng Studio: `docs/puppet-studio.md`, `docs/puppet-studio-concepts.md`; công thức cho AI: `docs/puppet-studio-ai-guide.md`.

## 1. Kết luận ngắn

- **Studio là công cụ quan trọng và được giữ.** Nó làm tốt việc dựng rig, sửa vùng cắt, tạo dáng, kiểm tra khớp.
- **Nhưng chưa tạo được chuyển động đẹp cho đòn đánh.** Mọi animation và GIF làm từ rig trong phiên này đều bị người dùng đánh giá là "xấu", "fail".
- **Nguyên nhân gốc không nằm ở số liệu chuyển động** mà ở: (a) master cũ không dựng để làm động tác, (b) rig cắt từ một ảnh 2D chỉ xoay và dãn được, không vẽ lại được góc nhìn mới, (c) cách làm nội suy mượt ngược với cách của game tham khảo (ít hình, giữ khung, hiệu ứng gánh chuyển động).
- **Các đường thay thế đã thử** (sheet tư thế bằng gpt-image-2, sheet bằng Gemini web, video `h3-max-turbo`) đều chưa đạt về tính đúng của động tác.

## 2. Studio đã làm được gì (giữ nguyên, đã có test)

| Tính năng | Ở đâu |
|---|---|
| Cẳng chân dãn theo bàn chân (IK `stretch: "lower"`, `max_bend`, skin `stretch`) | `core.py` `Rig.pose`, `_skin_inverse` |
| Mối nối tròn `parts[].discs` (bo tròn chỗ cắt ở khớp, không lộ mép thẳng) | `core.py` `_load_parts`, UI tab 4 |
| Vùng vẽ rộng (tay vung xa không bị cắt) | `app.js` `RENDER_REGION` |
| Xoay bằng phím T / Ctrl+T, chế độ Xoay kéo ở bất kỳ đâu, hàng "Xoay" nhập số | `app.js` `startRotModal`, `tabPose` |
| Kéo hai đầu cung giới hạn xoay để đặt `limit.rot` | `app.js` `pickLimitHandle`, `dragLimit` |
| Chỉ hiện nhóm khớp đang chọn (không bấm nhầm khớp khác) | `app.js` `focusSet` |
| Ctrl+Z trong ô số; nhóm "Chỉnh nhanh" giữ trạng thái mở | `app.js` |
| Test: `python scripts/studio/test_studio.py` 52/52; `puppet_test.py` 18/18 (animation cũ vẽ y hệt) | |

## 3. Vướng mắc chưa giải quyết

### 3.1 Rig 2D cắt từ một ảnh (giới hạn của phương pháp, không chỉnh số mà hết)
| Vấn đề | Thấy ở đâu | Vì sao |
|---|---|---|
| Đấm tay gần yếu, nắm đấm chỉ tới ngang mặt | animation đấm | Master v01 góc 3/4: vai gần nằm lùi sau thân 325 px so với vai xa. Xoay không đổi được chiều dài với tới; dây chằng (trượt vai) quá 80-90 px thì layer tay hở khỏi thân |
| Tay quét ngang đè lên ngực, bụng, mặt | đòn cào | Layer tay vẽ phía trước thân; rig không có góc nhìn khác để tay đi "vòng qua" thân |
| Nét V / khe ở cổ khi ngửa đầu | gầm, bị đánh | Phần thân dưới đầu đã bị xoá khi cắt layer; `fill_under` chỉ vá được trong vùng mask của đầu. Cần vẽ thêm lớp bị khuất (`docs/puppet-kit-next.md` §2) |
| Chạy không ra chạy | run_cycle | Không có pha lơ lửng, hai tay vung đè lên ngực, chân IK chỉ trượt trên đất |
| Hình cứng khi nội suy | mọi GIF | Nội suy xoay mượt giữa các dáng ở cỡ 1024 px làm lộ mọi mối nối; ở cỡ game (60 px) mới che được |
| Rig chưa có cho master mới | master v05 | Mọi layer, rig v2 và rig Studio vẫn cắt từ master v01; v05 chưa được tách lớp và dựng rig |

### 3.2 Master cũ không dựng để làm động tác
Người dùng chỉ ra (2026-11-12): hai chân không đều, tay to tay nhỏ, nên mọi đòn đấm xấu. Đã vẽ master v05 (chibi, gần nhìn thẳng ~20°, hai tay
và hai chân cân nhau; `brief.md` mục "Master v05"). Đây là gốc mới, nhưng các bước sau trên v05 (rig, tư thế) chưa đạt.

### 3.3 Sheet tư thế bằng model ảnh: giữ được nhân vật, không giữ được vật lý của động tác
| Thử | Kết quả |
|---|---|
| gpt-image-2 low, 1 ảnh 4 tư thế (master v05 + khung `ref/alien` làm mẫu) | Nhân vật đồng nhất; tư thế 1 và 3 giơ cùng một tay; người dùng: động tác không đúng |
| Gemini (web), 5 tư thế 1 hàng | Ra 7 hình 2 hàng; "giơ một tay" thành giơ hai tay; quét ngang thành đấm thẳng |
| Gemini, lưới 4x2 | Ra 10 hình 3-3-4; nhát 1 đúng, lấy đà 2 lại giơ hai tay |
| Gemini, 10 khung 1 hàng + mô tả võ thuật | Tốt hơn nhưng ra 12 khung 2 hàng, tự ghi nhãn tên khung, có vệt chém mỏng, có watermark; khung lặp; chỉ tay động, thân và chân gần như đứng yên |
| Gemini, mô tả toàn thân từng khung, cấm lặp | Người dùng: vẫn không ổn |

Kết luận: model ảnh vẽ **từng hình** đẹp và giữ nhân vật tốt (Gemini > gpt-image-2), nhưng không bảo đảm **chuỗi hình** liền nhau về vật lý,
không đếm đúng số khung, nhầm tay trái/phải, tự thêm hiệu ứng và chữ. Viết prompt chi tiết hơn chỉ cải thiện từng phần.

### 3.4 Video `h3-max-turbo` (image-to-video, 4 s, 0,06 USD)
Clip `attack_claw2_t01` (đã xoá): hai nhát cào đúng thứ tự mô tả, nhân vật giữ nguyên, nhưng model tự vẽ vệt hồng, nhiều khung nhoè, giữ quá lâu sau nhát 1.
Người dùng đánh giá **Fail**; lý do cụ thể chưa ghi lại. Lần sau hỏi rõ trước khi chạy lại.

## 4. Vì sao `ref/alien` làm được (đo trực tiếp trên khung)

| Đặc điểm | Số đo / quan sát |
|---|---|
| Cỡ | Nhân vật cao 32-41 px trong ô 168x112. Ở cỡ này mắt đọc bóng dáng và hiệu ứng, không đọc chi tiết khớp |
| Số hình | Chạy (0002-0006): **5 hình**. Đòn đánh đôi (0007-0032): 26 khung nhưng **~15 hình**; hầu hết mỗi hình giữ đúng **2 khung** (khung 0008, 0010, 0012... trùng 100% khung trước) |
| Lấy đà | Một tư thế giữ 6 khung (0007-0012), chỉ ánh sáng nhấp nháy (~600 px đổi) |
| Ra đòn | Đổi thẳng sang **tư thế mới**, không có khung chuyển tiếp, không nội suy |
| Hiệu ứng | Vệt chém hình lưỡi liềm **rất to** trong 2-3 khung, **che gần hết thân** đúng lúc đổi tư thế. Vệt chém gánh cảm giác chuyển động và che chỗ nhảy hình |
| Thiết kế | Cân đối, mập, chi ngắn, hai tay bằng nhau, chân bằng nhau, tay không đè lên thân; góc gần nhìn thẳng |
| Thân | Gần như không di chuyển; chạy chỉ nhún 1-2 px |

Cách họ làm (suy luận, chưa xác nhận): vẽ tay các **tư thế khoá** (rất có thể vector, tái dùng mảnh, đổi mảnh khi đổi tư thế), xuất ra cỡ nhỏ, giữ
khung on twos, và vẽ riêng vài hình vệt chém. Họ không mô phỏng vật lý từng khung: **người vẽ quyết định tư thế đúng**, hiệu ứng che phần còn lại.
Điều mình chưa làm được là có một "người vẽ tư thế đúng": rig thì không vẽ được góc mới, model ảnh thì không giữ được chuỗi vật lý.

## 5. Giới hạn của Studio (ghi rõ để khỏi kỳ vọng sai)
- Chỉ **biến đổi ảnh đã có** (xoay, dãn, trượt, uốn quanh khớp). Không vẽ được phần bị khuất, mặt sau, tay vòng qua thân, hay góc nhìn mới.
- Hợp cho: thở, nhún, gầm, rung, nghiêng nhẹ, dáng chuyển tiếp nhỏ, kiểm tra khớp, phác dáng.
- Không hợp cho: đấm hay cào cần xoay thân, chạy, quay người, mọi động tác mà tư thế cuối khác hẳn về hình chiếu.
- Chất lượng phụ thuộc master: master lệch (tay to tay nhỏ, vai lùi) thì mọi dáng đều lệch.

## 6. Hướng còn mở (chưa thử hoặc chưa xong)
1. **Rig cho master v05**: tách lớp và dựng lại rig để Studio dùng thiết kế cân đối mới.
2. **Studio làm bản phác, model ảnh vẽ sạch từng khung**: dùng dáng từ Studio làm ảnh phác (tư thế đúng) + master làm thiết kế, gọi model ảnh vẽ lại **từng khung một** (không phải cả sheet). Chưa thử.
3. **Video tham chiếu** (`docs/reference-video-motion.md`): đưa đúng khung `ref/alien` làm video mẫu chuyển động. Đã chạy tốt với đòn một nhịp; combo nhiều nhát bám kém. Chưa thử với alien.
4. **Vệt chém lớn kiểu ref** trong `lib-fx/melee/beast` (thư viện chưa có hiệu ứng vuốt), đặt đúng lúc đổi tư thế để che chỗ nhảy hình.
5. Người vẽ tay các tư thế khoá (ngoài phạm vi công cụ hiện có).

## 7. Chi phí phiên 2026-11-12
~0,15 USD: 4 master gpt-image-2 low (0,058), 1 sheet tư thế 2 ảnh (0,031), 1 clip h3-max-turbo 4 s (0,06). Các lần Gemini chạy trên web của người dùng (0 USD qua fal).

## 8. Dọn dẹp đã làm
Đã xoá các thử nghiệm hỏng: `source/rig/anims_studio/`, thư viện `poses/` (13 dáng), `pose_claw2_sheet_v01/v02`, các prompt `pose_claw2_*`, clip `attack_claw2_t01`, và `.work/` thử nghiệm.
Giữ: toàn bộ thay đổi Studio, master v05 (`brief.md`, `history.md`), `rig_studio_v01..v03`, `ref/alien`, `ref/asra`.
