# Puppet Studio: sổ tay cho AI (thêm khớp, dây chằng, IK, mối nối tròn...)

Đọc file này TRƯỚC khi sửa rig theo yêu cầu của người dùng ("thêm khớp", "thêm dây chằng", "cho chân dãn", "bo tròn chỗ cắt"...).
Bản cho người dùng (khái niệm, cách yêu cầu): `docs/tools/studio/puppet-studio-concepts.md`. Chi tiết sâu về `limit` / `links`: `docs/tools/studio/puppet-studio-guide.md`.

## 0. Quy tắc cứng

1. Chỉ sửa **rig của Studio** `out/<class>/<id>/source/rig/rig_studio_v01.json` (hoặc bản `rig_studio_vNN.json` người dùng đang mở). **Không** đặt `limit`, `links`, `discs`, `ik.stretch` vào `rig.json` (animation đã duyệt dùng nó).
2. Mọi sửa tay JSON phải đi qua `validate_spec` ([server.py](../../../tools/studio/server.py)); sau khi sửa chạy `python scripts/puppet_test.py` (0 diff). Core mới phải **opt-in** bằng khóa trong rig để rig/animation cũ vẽ y hệt (test F11).
3. Toạ độ trong rig = **pixel của still 1024×1024** (không phải toạ độ màn hình). `pivot`, `pt`, `at`, polygon đều ở không gian này, ở dáng gốc.
4. Không đoán khớp cha, tâm xoay, điểm bám: nếu người dùng chưa chỉ, hỏi hoặc đề nghị họ đặt trong Studio rồi Lưu rig, dùng file đã lưu làm nguồn.
5. Sau khi sửa, **vẽ thử** (Rig.render trong script, xem ảnh) ở dáng gốc và 2–3 dáng cực đoan; xem bằng mắt. Test pixel không thấy được "nứt" nhỏ.
6. Lưu rig của Studio luôn tạo backup ở `source/rig/backup/`; sửa tay file thì tự `git diff` để chắc chỉ đổi đúng chỗ (ghi lại bằng `json.dumps(indent=1, ensure_ascii=False)`, giữ xuống dòng cuối).

## 1. Cấu trúc rig (khóa cấp cao)

`id, note, sources, ground, unit, bones, ik, sockets, parts, links` (+ `stretch` tuỳ chọn, xem §3.4).

| Khóa | Nội dung |
|---|---|
| `sources` | `{tên: đường dẫn ảnh still}` (tương đối so với thư mục rig). Layer lấy ảnh từ đây |
| `ground`, `unit` | điểm đất `[x,y]` và chiều cao đứng (px) |
| `bones` | danh sách `{name, parent, pivot:[x,y], limit?:{rot:[min,max]}}`. `parent: null` chỉ có `root`. Thứ tự: cha trước con không bắt buộc (core tự sắp) |
| `parts` | layer vẽ: `{name, source, bone, select, skin?, discs?, subtract?, fill_under?, grow?}` |
| `ik` | chân IK hai xương |
| `sockets` | `{tên: {bone, pt}}` điểm gắn vũ khí/hiệu ứng |
| `links` | dây chằng/cơ (dãn ngực theo vai) |

Kênh của mỗi bone (pose/anim): `rot` (độ, dương = cùng chiều kim đồng hồ), `tx`, `ty` (trượt, px, theo hệ của bone cha), `sx`, `sy` (dãn), `shx`; kênh của layer: `alpha`, `z`, `grey`, `sway`; `fk` bật FK cho chân IK. Mặc định: core.py `DEFAULTS`.

## 2. Công thức: thêm từng loại thứ

### 2.1 Thêm một khớp (bone)
```json
{"name": "near_ear", "parent": "head", "pivot": [300, 150], "limit": {"rot": [-30, 30]}}
```
- `parent` phải tồn tại, không tạo vòng. Đổi cha không đổi hình ở dáng gốc, nhưng đổi cách khớp kéo theo nhau khi xoay; pose cũ ghi `rig.topology` nên thư viện sẽ hiện ⚠.
- Khớp mới chưa vẽ gì cho tới khi có layer gắn vào nó (§2.2) hoặc nằm trong `skin.bones` (§2.3).
- Tên bone phải duy nhất. Studio gọi tên tiếng Việt qua `SEG`/`viName` trong app.js (phần cuối tên: `upper_arm, forearm, hand, thigh, shin, foot, head, spine, hips, tail, root`); tên lạ vẫn chạy, hiện nguyên tên.
- Cần giới hạn xoay thì thêm `limit.rot` (min < max). Không có `limit` thì Studio dùng mặc định theo tên (`DEFAULT_LIMITS` app.js) hoặc tự do.

### 2.2 Thêm một layer cứng (cắt từ ảnh, gắn một bone)
```json
{"name": "ear_near", "source": "torso", "bone": "near_ear",
 "select": {"poly": [[x,y], ...]}, "subtract": ["head"]}
```
- `select.poly`: đa giác đơn (không tự cắt nhau, ≥3 đỉnh). Layer lấy phần ảnh gốc trong đa giác (và alpha > 8).
- `subtract`: trừ vùng của layer khác khỏi layer này. `select: {"rest": true}`: lấy phần còn lại của ảnh sau khi các layer khác cùng `source` đã cắt.
- Thứ tự trong `parts` = thứ tự vẽ (sau đè trước); chỉnh nhanh bằng kênh `<layer>.z`.
- Sau khi thêm, layer đó cần lấy ảnh ra khỏi layer cũ: nếu layer cũ cùng `source` đang chứa phần ấy thì dùng `subtract` hoặc co đa giác cũ lại.

### 2.3 Khớp uốn liền (skin) cho tay/chân/thân
```json
"skin": {"bones": ["near_thigh", "near_shin"], "tip": [440, 868], "blend": 30}
```
- Một ảnh gắn `bone` = `skin.bones[0]`; ảnh uốn cong quanh mỗi khớp thay vì cắt. `tip` = đầu mút xương cuối. `blend` (số hoặc mảng từng khớp) = nửa bề rộng dải uốn, px.
- `skin.stretch: true` làm ảnh **dãn dọc xương** theo hệ số dãn bone dưới khớp (dùng với `ik.stretch`, §2.5). Không bật thì chỉ xoay.
- `skin.iterations`, `skin.tolerance`: độ chính xác giải ngược (mặc định 12, 2.5).

### 2.4 Dây chằng / cơ dãn theo vai (`links`)
```json
{"name": "near_chest", "arm": "near_upper_arm", "mode": "stretch", "max_pull": 90,
 "anchors": [{"part": "torso", "pt": [500, 430], "radius": 140, "gain": 1.0}]}
```
- `arm` = bone vai; `tx/ty` của bone này là độ trượt vai ra khỏi thân. `mode`: `stretch` (cơ dãn quanh điểm bám) hoặc `carry` (cả thân đi theo, chỉ Studio giải, core bỏ qua).
- `anchors[].pt` ở không gian ảnh của layer `part`; `radius > 0`; `gain` 0…3. 1–3 điểm bám trên ngực, bán kính 100–160, không phủ cả thân.
- Cách nhanh nhất: người dùng vào tab 3 của Studio, chọn link, bấm lên thân (phím A) để đặt điểm, rồi Lưu rig. AI chỉ nên viết tay khi biết chính xác toạ độ.
- Chi tiết công thức và giới hạn: `docs/tools/studio/puppet-studio-guide.md` §3.3.

### 2.5 Chân IK, cẳng chân dãn theo bàn chân
```json
{"upper": "near_thigh", "lower": "near_shin", "end": [440, 868], "end_bone": "near_foot",
 "hint": [1, 0], "target": {"bone": "near_foot_target", "pt": [440, 868]},
 "stretch": "lower", "max_bend": 55, "min_scale": 0.5}
```
- IK hai xương: đùi + cẳng chân tới `target` (điểm trong hệ bone đích; `near_foot_target` là con của `root`, kênh `tx/ty` của nó dời bàn chân). `end_bone` đứng yên trên đích, giữ góc `rot` của riêng nó. `hint` = hướng gối gập (màn hình), `[1,0]` = gối ra trước.
- Không có `stretch`: cả đùi và cẳng chân dãn đều khi quá tầm. `"stretch": "lower"`: đùi giữ nguyên, chỉ cẳng chân (lower) dài ra khi quá tầm và **co** (tối thiểu `min_scale`) thay vì gập gối quá `max_bend` độ. Layer chân phải có `skin.stretch: true` (§2.3).
- Muốn có IK chân mới: thêm hai bone đích `<x>_foot_target` (parent `root`, pivot = `end`), một mục `ik`, layer chân có `skin` hai xương. `topology_hash` tính cả `ik`, nên thư viện pose sẽ báo cấu trúc đổi.
- Tay không có IK (xương tay dãn bằng `sy` hoặc link). Một bone ngắm và dãn tới điểm (ống tay áo): khóa `stretch` cấp cao `[{"bone", "end", "target": {"bone","pt"}}]` (core đã hỗ trợ; Studio chưa có UI).

### 2.5b Điểm gắn (socket)
`"sockets": {"hand_fx": {"bone": "near_hand", "pt": [330, 790]}}`. Xuất vị trí cho vũ khí/hiệu ứng (`puppet.py track`). Studio kéo được ở chế độ Sửa rig (P).

### 2.6 Mối nối tròn (bo tròn chỗ cắt)
```json
"discs": [{"at": [440, 868], "r": 62}]
```
- Đặt trên **layer** (`parts[]`), không phải bone. Thêm một hình tròn của ảnh gốc vào vùng cắt, nên layer xoay quanh tâm hình tròn thì mép cắt thẳng biến mất, không hở khe khi gập. `at` ở pixel still, tốt nhất đúng tâm khớp (`pivot` của bone). `r` 40–80 px, 1 ≤ r ≤ 400.
- Hình tròn chồng lên layer bên cạnh (cùng ảnh nguồn) nên dáng gốc không đổi (test H2). Core: `Rig._load_parts` (sau khi tính mask polygon). Chỉ layer có `select.poly`.
- Studio: tab 4 > "Mối nối tròn" (sau khi bấm "Sửa vùng cắt" của layer) thêm/xóa/đổi số; hình tròn hiện đường nét hồng.
- Khi nào dùng: layer cứng quay quanh một khớp mà chỗ nối lộ mép (cổ chân, cổ tay nếu không dùng skin, vai). Khớp uốn liền đã có `skin` thì thường không cần.

### 2.7 Giới hạn xoay
`bones[].limit.rot = [min, max]` (độ, so với dáng gốc). Studio áp khi kéo/thanh trượt/phím; không áp khi nạp pose hay undo. Người dùng kéo hai chấm cam trên cung giới hạn hoặc sửa số ở tab 2.

## 3. Bản đồ code (sửa ở đâu)

| Việc | Chỗ |
|---|---|
| Vẽ, IK, skin, link, discs | `scripts/puppet_kit/core.py` (`Rig.pose`, `_skin_inverse`, `_pulls`, `_load_parts`, `render`) |
| Kiểm tra rig, API, lưu/backup, pose | `tools/studio/server.py` (`validate_spec`, `StudioRig`, `Studio`) |
| Giao diện | `tools/studio/static/app.js` (+ `index.html`, `style.css`) |
| Test | `scripts/puppet_test.py` (bộ test riêng của Studio đã bị gỡ cùng nhân vật lion) |

Mẹo trong app.js: `limitOf`, `setCh` (kẹp giới hạn), `focusSet`/`inFocus` (nhóm khớp đang chọn), `mkPoseDrag`/`applyChain`/`applyFoot`/`applyRotate`, `startRotModal` (phím T), `pickLimitHandle`/`dragLimit`, `tabPose`/`tabRig` (panel phải), `RENDER_REGION` (vùng vẽ), `beginEdit`/`commitEdit` (undo). Mọi chỉnh sửa người dùng phải đi qua cặp `beginEdit()` … `commitEdit()` để Ctrl+Z hoạt động.

Khi thêm khóa mới vào rig: (1) core xử lý khóa, mặc định = hành vi cũ; (2) `validate_spec`; (3) `structure_key` (server.py) nếu khóa đổi cách cắt layer; (4) UI nếu cần; (5) test; (6) cập nhật hai doc.

## 4. Quy trình mẫu: "thêm dây chằng cho vai xa"
1. Mở rig Studio, đọc `links` hiện có (đang có `near_chest`, `far_chest`).
2. Nếu đã có thì bảo người dùng chỉnh điểm bám ở tab 3; nếu thiếu thì thêm mục `links` như §2.4 với điểm bám mặc định ở ngực, rồi mở Studio kéo tay xa quá tầm để xem.
3. Kiểm: `validate_spec` qua `/api/rig/set` hoặc test F; xem ảnh với `far_upper_arm.tx` = 30/60/90.
4. Ghi vào `docs/tools/studio/puppet-studio-guide.md` nếu có quy tắc mới.
