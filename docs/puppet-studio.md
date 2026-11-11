# Lion Rig & Pose Studio (cập nhật 2026-11-11)

Công cụ cục bộ để xem rig, tạo dáng, cấu hình khớp, giới hạn góc và cơ (dãn theo), rồi lưu pose vào thư viện riêng. Mọi hình đều do `Rig.render` của Puppet Kit vẽ (`scripts/puppet_kit/core.py`); trình duyệt chỉ vẽ lớp phủ và sửa dữ liệu. 0 USD, không gọi API ảnh hay video.

```
python scripts/studio/server.py                 # mở http://127.0.0.1:8765/ (mặc định nạp rig_studio_v01.json nếu có)
python scripts/studio/server.py --rig rig.json  # rig gốc, không có bone đích chân, limit, links
python scripts/studio/test_studio.py            # 46 test trên bản sao tạm (không đụng rig, pose, anims thật)
```

Mã nằm ở `scripts/studio/` (`server.py` stdlib, `static/index.html|app.js|style.css`, `test_studio.py`, `README.md` bản ngắn). Server chỉ nghe 127.0.0.1, mọi POST cần header `X-Studio`.

## 1. Mô hình thao tác

| Thao tác | Ý nghĩa |
|---|---|
| **Bấm** vào khớp (chấm tròn) hoặc thẳng lên hình (cánh tay, thân, đầu…) | chọn. Bấm không bao giờ ghi kênh nào vào pose |
| **Giữ và kéo** (di quá 4 px) | di chuyển. Kiểu di chuyển theo thứ được bấm (xem dưới) |
| **Bấm ra ngoài** | bỏ chọn (dáng giữ nguyên) |
| Space/Alt/chuột giữa + kéo | dời khung nhìn. Cuộn = zoom |

Kéo trong công cụ **Tạo dáng** (V) hiểu theo loại khớp: bàn tay/cẳng tay/cánh tay duỗi theo chuột (CCD), thân đi theo; chân (IK) dời bone đích bàn chân và hạ hông vừa đủ (chân đứng đã duỗi thẳng nên không dạng ra được nếu không hạ hông); hông/gốc trượt cả thân; đầu, đuôi xoay hướng về con trỏ. **Xoay** (E) và **Trượt** (W) chỉnh đúng khớp đang chọn (kéo bắt đầu ở khớp hoặc trong vòng 64 px quanh nó). **Sửa rig** (P) và **Điểm bám** (A) là chế độ sửa rig: có biểu ngữ màu hồng, Esc để thoát.

Các nút phụ: Tab / Shift+Tab chọn khớp kế, mũi tên xoay hoặc trượt nhẹ (Shift = 5), Del đưa khớp về gốc, Ctrl+Z / Ctrl+Shift+Z, Ctrl+S lưu rig, F vừa khung, H hướng dẫn. Studio tự vẽ con trỏ riêng và đánh dấu điểm kéo được (đầu các chi nhấp nháy).

## 2. Bố cục

- **Trái**: tab **Layer (hình)**: mỗi layer có ảnh thu nhỏ, loại (uốn được/cứng), khớp gắn vào, khớp uốn và độ mềm, nút ẩn/hiện, "Chỉ xem lớp này", "Sửa vùng cắt". Tab **Bone (khớp)**: cây khớp có đánh dấu IK và giới hạn, công tắc IK/FK từng chân, socket.
- **Giữa**: viewport (bộ xương, tên khớp, tâm khớp, khung layer, vùng cắt, vùng uốn, socket, đích IK, cơ/điểm bám, cung giới hạn, vùng ảnh hưởng) và khung xem cỡ game H = 60 px @1x.
- **Phải** (mỗi tab mở đầu bằng một câu nói nó để làm gì): **1 Tạo dáng** (thanh trượt theo khớp đang chọn, dáng mẫu, mức thân đi theo) · **2 Khớp & giới hạn** (khớp cha, tâm xoay, giới hạn góc, bảng giới hạn mọi khớp) · **3 Cơ & dây chằng** · **4 Sửa rig** (vùng cắt, độ mềm khớp uốn, đích IK, socket, Lưu rig) · **5 Kiểm tra** (bend tester, lỗi đã biết).
- **Dưới**: thư viện pose (độc lập với `anims/*.json`) và so sánh A ⇄ B, bóng mờ.

## 3. Dữ liệu

### 3.1 Pose (`out/<class>/<id>/poses/<id>.json` + `.png`)
`{schema, id, name, description, created, updated, rig {file, topology, hash, bones}, bones {tên: {rot,tx,ty,sx,sy,shx}}, ik {upper: false}}`. Chỉ lưu kênh khác mặc định; `ik.<upper>: false` = chân đó ở FK. Không bao giờ ghi vào `rig.json` hay `anims/*.json`. Mở pose giữ nguyên giá trị đã lưu (không bị kẹp giới hạn khớp).

### 3.2 Giới hạn khớp: `bone.limit.rot = [min, max]` (độ, min < max)
Một khóa mở rộng trong `rig` (Puppet Kit bỏ qua khóa lạ). Dùng để **chặn lúc chỉnh**: kéo, thanh trượt, phím, dáng mẫu và solver đều kẹp vào khoảng này (cung cam trên màn hình). `limit: {"rot": null}` = tự do. Bone không có `limit` dùng mặc định theo tên (`DEFAULT_LIMITS` trong `app.js`: bàn chân ±30°, bàn tay ±70°, đầu ±40°, cẳng tay −160…20°, cánh tay −170…80°…). Nạp pose, nhập pose, hoàn tác và khôi phục bản tự lưu **không** kẹp. Chỉ Studio áp dụng; một `anims/*.json` vẫn có thể đặt giá trị ngoài khoảng. Tab Kiểm tra bỏ qua giới hạn có chủ đích để thử góc cực đoan.

### 3.3 Cơ dãn theo: `rig.links` (Puppet Kit hỗ trợ trong `Rig.render`, từ 2026-11-11)
```json
"links": [{"name": "near_chest", "arm": "near_upper_arm", "mode": "stretch", "max_pull": 90,
           "anchors": [{"part": "torso", "pt": [500, 430], "radius": 140, "gain": 1.0}]}]
```
| Khóa | Ý nghĩa |
|---|---|
| `arm` | bone gốc của cánh tay (vai). Phải tồn tại. **Kênh `tx`/`ty` của bone này là độ trượt vai ra khỏi thân** |
| `mode: "stretch"` | vai trượt ra theo tay khi tay quá tầm; chỉ phần ảnh quanh mỗi điểm bám của layer `part` dãn theo, phần còn lại của thân đứng yên. Dành cho nhân vật có cơ |
| `mode: "carry"` | không dãn gì cả; solver của Studio dịch và nghiêng cả thân theo tay. Dành cho nhân vật không có cơ (người đá). Core bỏ qua link này khi vẽ |
| `max_pull` | vai được trượt tối đa bao nhiêu px (Studio dùng khi giải; core không kẹp) |
| `anchors[].part` | layer bị dãn (thường `torso`) |
| `anchors[].pt` | điểm bám trong **không gian ảnh gốc của layer đó** (pixel của still, không phải toạ độ màn hình) |
| `anchors[].radius`, `gain` | bán kính vùng bị kéo (px, > 0) và độ mạnh (0…3). Trọng số = `gain × smoothstep(1 − d/radius)` |

Công thức trong core (`Rig._pulls` và `Rig.render`): độ dịch `d` = phần tuyến tính của `inv(world[part.bone]) · world[cha của arm]` nhân `(tx, ty)` của `arm`; điểm ảnh được lấy mẫu tại `s − w·d`, nên nội dung quanh điểm bám đi theo vai (cùng hướng `tx, ty`), mờ dần về 0 ở mép bán kính. Khung vẽ của layer được nới thêm đúng mức dãn để không bị cắt. Chỉ vẽ lại khi `tx/ty` của `arm` ≠ 0, nên mọi animation cũ (không dịch vai) cho kết quả y hệt.

**Chỉ đặt `limit` và `links` trong rig của Studio** (`rig_studio_v01.json`), không đặt vào `rig.json`: animation nào đó có thể đang đặt `*_upper_arm.tx/ty` và sẽ bắt đầu vẽ khác.

### 3.4 `rig_studio_v01.json`
`rig.json` + hai bone đích IK `near_foot_target`, `far_foot_target` (con của `root`, tâm ở đích IK, `ik[].target.bone` trỏ tới chúng) để pose dời được từng bàn chân bằng `tx/ty`. Khi ở dáng gốc và mọi pose cũ, hình giống hệt `rig.json` (đã kiểm). Thêm `limit` cho 16 bone và hai link `near_chest`, `far_chest` (điểm bám ngực mặc định ở (500,430) và (650,430), bán kính 140). Lưu rig luôn tạo bản sao lưu ở `source/rig/backup/`.

## 4. Quy tắc cho AI khi nối bone hoặc sửa rig (đọc trước khi đụng `rig.json`)

1. **Đừng đoán khớp cha, giới hạn hay điểm bám.** Mở Studio, cấu hình ở tab 2 và 3 rồi Lưu rig; dùng file đã lưu làm nguồn. Mọi chỉnh sửa tay vào JSON phải qua `validate_spec` (`server.py`): cha tồn tại và không vòng lặp, `limit.rot` có min < max, link có `arm` tồn tại, `mode` ∈ {stretch, carry}, anchor có `part` tồn tại, `pt` hai số, `radius` > 0, `gain` ∈ [0,3].
2. Đổi khớp cha không đổi hình ở dáng gốc (mỗi khớp là biến đổi cục bộ quanh tâm của nó); nó đổi khớp nào kéo theo khớp nào khi xoay. Đổi xong phải xem lại các pose đã lưu (pose ghi `rig.topology`; cấu trúc đổi thì thư viện hiện ⚠).
3. Tâm xoay (`pivot`) là pixel của still. Kéo tâm ở dáng gốc cho chính xác.
4. Muốn tay kéo dãn cơ ngực: một `link` cho mỗi cánh tay với `arm` = bone vai, `mode: "stretch"`, 1–3 điểm bám trên ngực (không phủ cả thân, bán kính 100–160 px). Muốn cả thân đi theo: `mode: "carry"` hoặc không có link.
5. Không thêm khóa lạ vào `bones`/`parts` ngoài `limit`; không đặt `links` hay `limit` vào `rig.json` đang dùng bởi animation đã duyệt.

## 5. Kiểm thử và giới hạn

- `python scripts/studio/test_studio.py`: 46 test (A–E: nạp rig, tương tác, sửa rig, thư viện pose, bend; F: giới hạn, link, hướng kéo, ngoài bán kính không đổi, `carry` không méo, ảnh layer, **hồi quy**: mọi frame của `anims/*.json` trên `rig.json` giống hệt core trước thay đổi `links` (git `3276f20`)). `python scripts/puppet_test.py`: 18/18.
- Giới hạn: polygon, vùng uốn và điểm bám trên màn hình vẽ theo biến đổi cứng của bone (đúng ở dáng gốc, xấp xỉ chỗ da đang uốn). Giới hạn khớp chỉ do Studio áp dụng. `stretch` kéo vai qua `tx/ty`, nên layer cánh tay (dính vào bone vai) cũng trượt theo; chỗ nối vai–ngực dựa vào vùng dãn che lấp, cần xem bằng mắt ở dáng cực đoan. Phần dãn xương tay bằng `sy` (khi không có link) làm cả cẳng tay và bàn tay dãn theo.
- Hiệu năng: kéo dùng bản nháp 0,3× với ít vòng giải skin hơn (~110 ms); bản chuẩn 0,5× ~0,5 s chạy 0,45 s sau khi thả chuột.
- Chưa có: giới hạn cho `tx/ty/sx/sy`, nhiều layer bị dãn cho một link (hiện `part` đặt tay hoặc mặc định `torso`), IK cho tay, nối lại layer vào bone khác, timeline.
