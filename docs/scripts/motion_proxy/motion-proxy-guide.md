# Motion proxy: bộ xương 3D làm nguồn chuyển động đúng vật lý cho skill

`scripts/motion_proxy/` dựng chuyển động của một skill cận chiến trên một bộ xương 3D đơn giản. Bộ xương này trở thành **nguồn sự thật về chuyển động**: hướng thân, cung vũ khí, trọng tâm, chân bám đất, phần nào bị thân che. Mô hình ảnh và rig 2D chỉ "khoác hình" lên kết quả, không tự quyết tư thế.

Chạy bằng Python, numpy, Pillow, matplotlib. Không cần GPU, không gọi API, chi phí 0 USD.

## Vì sao

Mô hình ảnh và video sinh ra chuyển động "trông giống" một động tác chứ không đúng cơ học: thứ tự hông → vai → vũ khí sai, chân trượt, vũ khí lộ khi đáng lẽ bị thân che. Nội suy tuyến tính trên rig 2D cũng không giữ được cung chuyển động. Ở đây vật lý được **ép bằng cấu trúc** nên không thể sai:

| Luật | Cách ép |
|---|---|
| Hông dẫn, rồi vai, rồi vũ khí | Chỉ có một đường cong xoay (`pelvis_yaw`). Vai đọc đường đó trễ `chain.lag_chest` khung, vũ khí trễ `chain.lag_weapon`. Xoắn ngực–hông bị chặn ở `chain.max_twist` |
| Chân không trượt | Mũi chân khoá, chân giải IK hai đoạn. Khi chân cần với xa, gót tự nhấc (kiễng trên mũi chân, tối đa `body.max_heel_lift`) |
| Tay bám vũ khí | Tâm hai tay (`body.grip_center`) đặt trước ngực, hai tay chia đều dọc cán, giải IK. Không với tới thì cả vũ khí dời về phía vai (độ dời được đo, xem tiêu chí). Khi đâm, cán trượt qua tay trước |
| Hitstop | Khung giữ chèn ở ánh xạ thời gian, mọi bộ phận dừng cùng lúc |
| Mắt nhìn mục tiêu | Đầu luôn cố quay về `chain.head_spot_target`, lệch tối đa `head_spot_limit` so với ngực |
| Nội suy | Hermite đơn điệu theo góc khớp, không vượt khoá nên không rung ảo; vị trí tay và vũ khí tự đi theo cung |

## Lệnh

```bash
python scripts/motion_proxy/build.py out/heroes/<id>/source/rig/proxy_<skill>.json
```

Kết quả ghi vào `out/heroes/<id>/.work/motion_proxy/proxy_<skill>/` (git bỏ qua):

| File | Dùng để |
|---|---|
| `clean.gif`, `clean_slow.gif` | **hình để xem**: nhân vật vẽ kiểu chunky (`paint.py`: chi thuôn hai tông, viền dày, vẽ gấp 3 rồi thu nhỏ), vạt áo xoè theo tốc độ xoay, vệt chém theo quỹ đạo mũi vũ khí (nửa gần trước thân, nửa xa sau thân), nền xám như ref |
| `anim.gif`, `anim_slow.gif` | **hình đo đạc**: hình đẹp cộng thêm trọng tâm, mũi chân khoá, mốc mục tiêu, góc nhìn từ trên (tia hông/vai/vũ khí), thanh nhịp |
| `compare.gif` | tham chiếu (`reference`) ghép theo pha, đặt cạnh proxy, để so khung theo khung |
| `sheet.png` | bảng khung |
| `metrics.md` | tiêu chí vật lý ĐẠT / KHÔNG ĐẠT (loại 'đo' hoặc 'cấu trúc', xem dưới), cùng bảng từng khung |
| `curves.png` | góc, vận tốc góc (chuỗi động học), dồn trọng tâm, tốc độ mũi vũ khí |
| `blocks/fNN.png` | khung khối màu nền trong, làm khung mẫu cho `gen_image.py --ref` |
| `frames.json` | toạ độ 2D (px camera proxy) các khớp, độ sâu, hướng thân (`view`), thứ tự lớp (tên phần của proxy, chưa phải tên phần của rig), vệt mũi vũ khí gần/xa |
| `weapon_track.json` | gốc lưỡi và mũi vũ khí từng khung, cùng định dạng `scripts/puppet.py track`: đơn vị H, gốc ở chân, `side` front/back, khung đếm từ 1, `hit_frame` |

## File thông số (`proxy_<skill>.json`, đặt trong `source/rig/` của nhân vật)

Code không chứa số của nhân vật nào. Mọi thứ nằm trong JSON (ví dụ `out/heroes/moon_crane/source/rig/proxy_spin_thrust.json`):

- `body`: tỉ lệ, **đo từ master** quy về chiều cao `height`. Kèm theo: `real_height_m` (để tính điểm bắt), `grip_center` (tâm hai tay so với ngực), `max_heel_lift`, khối lượng từng phần để tính trọng tâm.
- `weapon`: chiều dài, điểm nắm, kích thước mũi.
- `chain`: độ trễ pha, giới hạn xoắn, mục tiêu của mắt.
- `timing`: số khung, khung trúng, số khung hitstop, các pha (tên hiện trên khung), cửa sổ để đo.
- `channels`: các kênh `{τ: giá trị}`. τ tính bằng khung, chưa tính hitstop.
  - `pelvis_yaw`: kênh dẫn. Gồng thì giảm, quét thì tăng.
  - `chest_off`, `weapon_off`: lệch thêm so với hông.
  - `weapon_pitch`, `hand_drop`: độ cao vũ khí.
  - `weapon_slide`: rút về rồi đẩy khi đâm.
  - `root_x`, `root_y`: dồn trọng tâm và độ hạ người.
- `feet`: mũi chân sau/trước và các bước (`from`, `to`, `dx`, `lift`).
- `reference`: gif, vùng cắt, bảng `align` `[[τ proxy, khung ref], ...]` ghép theo pha.
- `body.skirt`: vạt áo (`drop` độ dài, `flare_base`, `flare_spin` độ xoè theo tốc độ xoay, `lift_spin`).
- `timing.slash_windows`: các khoảng τ có vệt chém (chỉ quét và đâm, không vẽ khi gồng).
- `palette`, `camera` (tuỳ chọn), `target_x`: màu, góc camera, mốc mục tiêu.

Chiều quay: yaw 0 = nhìn camera, 90 = nhìn mục tiêu (phải màn hình), 180 = lưng về camera, 270 = nhìn trái. Tăng yaw là xoay ngược chiều kim đồng hồ nhìn từ trên, cùng chiều cú quét của `ref/king`.

## Tiêu chí: "đo" và "cấu trúc"

`metrics.md` ghi loại của mỗi tiêu chí. Chỉ tiêu chí **đo** mới có thể hỏng và mới chứng minh được điều gì:

| Tiêu chí | Loại | Đo gì |
|---|---|---|
| Thứ tự nhả gồng, thứ tự đỉnh vận tốc | cấu trúc | Đúng vì vai và vũ khí đọc `pelvis_yaw` trễ pha. Chỉ hỏng khi `chest_off` / `weapon_off` chống lại |
| Xoắn ngực–hông | đo | Xoắn **thô**, trước khi bị chặn. Hỏng khi bộ chặn phải can thiệp (gây giật) |
| Chân bắt chéo được che | đo | Khi xoay trên mũi chân, hai chân được phép bắt chéo (như ref/king). Chỉ hỏng nếu chỗ hai chân cắt nhau trên ảnh nằm ngoài vạt áo |
| Tầm tay, chân | đo | Độ vượt tầm sau khi gót đã kiễng tối đa |
| Tay với tới đường tay | đo | Độ dời vũ khí của bộ giải tay ≤ `metrics.max_weapon_shift_pct` % chiều cao |
| Trọng tâm trong vùng đỡ | đo | Hai chân chạm đất: trọng tâm nằm giữa hai mũi chân. Một chân nhấc: điểm bắt (trọng tâm + vận tốc × √(h/g)) nằm giữa chân trụ và điểm chân sắp đặt |
| Dồn trọng tâm, gồng ra xa mục tiêu | đo | % về chân trước lúc gồng và lúc trúng; vị trí mũi lúc gồng |
| Cú đâm | đo | Từ khung nạp (thương rút về nhiều nhất) tới khung trúng, mũi tiến về mục tiêu và tăng tốc |
| Khung trúng quét | đo | Hướng vũ khí ở khung gần mục tiêu nhất lệch ≤ `metrics.sweep_hit_tol_deg` |
| Nửa xa / nửa gần | đo | Vũ khí 135–225° phải vẽ sau thân, 315–45° phải vẽ trước thân (theo thứ tự vẽ thật) |
| Mũi chân khoá, hitstop đứng yên | cấu trúc | Chỉ để nhắc |

## Cách chỉnh

1. Đo nhịp tham chiếu: cắt nhân vật ra, ghi khung của từng pha (sẵn sàng, gồng, nhả, trúng, quay lưng, ló ra, giữ). Chuyển sang 15 fps rồi ghi vào `reference.align` và `timing.phases`.
2. Đặt `pelvis_yaw` theo pha. Lúc trúng phải là lúc nhanh nhất: phía gần dồn khung lại, phía sau lưng thưa ra.
3. Chạy `build.py`, đọc `metrics.md`, sửa đúng kênh mà tiêu chí báo:

| Tiêu chí hỏng | Sửa |
|---|---|
| Xoắn chạm giới hạn | Giảm tốc `pelvis_yaw` hoặc giảm `lag_chest` (quay nhanh thì độ trễ phải ngắn) |
| Chân vượt tầm | Hạ `root_y`, thu hẹp `feet` |
| Tay phải dời vũ khí nhiều | Giảm `grip_center.forward`, `hand_drop` hoặc `weapon_slide`: phần vươn của cú đâm đến từ lunge (`root_x`), không phải từ tay |
| Trọng tâm ngoài vùng đỡ khi bước | Chân phải chạm đất trước rồi mới dồn người: dời `steps.to` sớm hơn, làm chậm `root_x` lúc chân trên không |
| Cú đâm chậm lại trước khung trúng | Dồn phần đẩy của `weapon_slide` và `root_x` vào khung ngay trước `t_hit` |
| Khung trúng quét lệch mục tiêu | Dời khoá `pelvis_yaw` quanh cú trúng để một khung nguyên rơi đúng hướng 90° |

4. So `compare.gif` với tham chiếu bằng mắt. Số đo chỉ thay việc soi chi tiết, không thay mắt.

## Bước sau proxy

- **Khung khoá**: chọn 5-6 khung trong `blocks/`, đưa làm `--ref` cho `gen_image.py` kèm master. Prompt nói lấy tư thế từ khung khối, lấy thiết kế từ master (luật `fal-image/action-planes.md` §9 vẫn áp dụng).
- **Phần quay người (xoay ra ngoài mặt phẳng)**: Puppet Kit không làm được. Hướng dẫn của Puppet Kit ghi rõ rig 2D không xoay ra ngoài mặt phẳng. Phần này cần một ảnh tĩnh cho mỗi `view` trong `frames.json` (chính diện, 3/4, nghiêng, lưng). Các khung trung gian lấy từ ảnh tĩnh gần nhất, đặt theo toạ độ khớp của proxy.
- **Phần trong mặt phẳng** (nạp, đâm, hitstop, hồi thế): Puppet Kit dựng được theo `frames.json`. `layer_back_to_front` dùng tên phần của proxy (`shaft0..9`, `wing`, ...), cần ánh xạ sang tên phần của rig khi nhân vật có `rig.json`.
- **Vệt chém**: `weapon_track.json` cho lib-fx. `--track` (FXKIT §6) chỉ nhận hai đầu mút kèm chiều quay. Cú quét 360° phải dùng `--swing ...;via=near|far` hoặc tách thành hai nửa theo `side`.

## Giới hạn

- Thân là khối cứng: không có áo choàng, tóc hay dải vải lay động. Phần đó để cho rig hoặc fx.
- Mỗi tay chỉ có một khớp khuỷu. Cổ tay không xoay riêng, vũ khí nắm cứng.
- Khi quay 360° tại chỗ với hai mũi chân khoá, chân bắt chéo ở các khung quay lưng. Cách đã chọn (2026-11-16): giữ chân xoay trên mũi như ref/king, vạt áo xoè theo tốc độ xoay che chỗ chéo; tiêu chí kiểm tra chỗ chéo không lộ. Nhân vật không có vạt áo thì thêm bước chân trong `feet.steps`.
- `paint.py` là hình khối gần giống master để đánh giá động tác, không phải asset game. Asset thật vẫn đi qua ảnh tĩnh và rig.
