# Puppet Studio: tính năng đã có và giới hạn

Mục đích: biết đâu là giới hạn của công cụ (không phải lỗi số liệu) để khỏi đi lại đường đã thất bại. Cách dùng: `puppet-studio-guide.md`, `docs/tools/studio/puppet-studio-concepts.md`; công thức cho AI: `docs/tools/studio/puppet-studio-ai-guide.md`.

## 1. Kết luận ngắn

- Studio dựng rig, sửa vùng cắt, tạo dáng, kiểm tra khớp rất tốt và được giữ.
- Studio **không tạo được cả đòn đánh từ một ảnh**: rig chỉ biến đổi ảnh có sẵn. Muốn đòn đánh đẹp, dùng cặp pose A/B đã duyệt + vệt chém, rồi Studio chỉ làm phần sống động (thở, nhún, dây chằng, áo choàng): `docs/pipeline/pose-pair-fx-method.md`.
- Việc thử sheet tư thế bằng model ảnh và video cho đòn đánh liền mạch không đạt (model giữ được nhân vật nhưng không giữ được vật lý của chuỗi hình).

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
| Test hồi quy: `scripts/puppet_test.py` (Studio chưa có bộ test riêng sau khi gỡ nhân vật lion) | |

## 3. Vướng mắc còn lại của rig cắt từ một ảnh

(giới hạn của phương pháp, không chỉnh số mà hết)
| Vấn đề | Thấy ở đâu | Vì sao |
|---|---|---|
| Đấm tay gần yếu, nắm đấm chỉ tới ngang mặt | animation đấm | Master v01 góc 3/4: vai gần nằm lùi sau thân 325 px so với vai xa. Xoay không đổi được chiều dài với tới; dây chằng (trượt vai) quá 80-90 px thì layer tay hở khỏi thân |
| Tay quét ngang đè lên ngực, bụng, mặt | đòn cào | Layer tay vẽ phía trước thân; rig không có góc nhìn khác để tay đi "vòng qua" thân |
| Nét V / khe ở cổ khi ngửa đầu | gầm, bị đánh | Phần thân dưới đầu đã bị xoá khi cắt layer; `fill_under` chỉ vá được trong vùng mask của đầu. Cần vẽ thêm lớp bị khuất (`docs/scripts/puppet_kit/puppet-kit-asset-prep-and-rig-v2.md` §2) |
| Chạy không ra chạy | run_cycle | Không có pha lơ lửng, hai tay vung đè lên ngực, chân IK chỉ trượt trên đất |
| Hình cứng khi nội suy | mọi GIF | Nội suy xoay mượt giữa các dáng ở cỡ 1024 px làm lộ mọi mối nối; ở cỡ game (60 px) mới che được |
| Rig chưa có cho master mới | master v05 | Mọi layer, rig v2 và rig Studio vẫn cắt từ master v01; v05 chưa được tách lớp và dựng rig |

## 4. Giới hạn của Studio (ghi rõ để khỏi kỳ vọng sai)
- Chỉ **biến đổi ảnh đã có** (xoay, dãn, trượt, uốn quanh khớp). Không vẽ được phần bị khuất, mặt sau, tay vòng qua thân, hay góc nhìn mới.
- Hợp cho: thở, nhún, gầm, rung, nghiêng nhẹ, dáng chuyển tiếp nhỏ, kiểm tra khớp, phác dáng.
- Không hợp cho: đấm hay cào cần xoay thân, chạy, quay người, mọi động tác mà tư thế cuối khác hẳn về hình chiếu.
- Chất lượng phụ thuộc master: master lệch (tay to tay nhỏ, vai lùi) thì mọi dáng đều lệch.

