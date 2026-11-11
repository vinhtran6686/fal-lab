# Puppet Kit: công thức chuyển động (motion recipes)

Cập nhật 2026-11-11. Mục đích: để **mọi model, kể cả model nhỏ, viết được `anims/*.json` đúng mà không phải tự nghĩ lại cơ học**. Chép bảng, thay số theo nhân vật, chạy `render --no-export`, xem `contact.png`.
Nguồn: 12 nguyên tắc hoạt hình cổ điển (squash & stretch, anticipation, follow-through, slow in/out, arcs, timing), vòng chạy/đi 4 pose khoá (contact, down, passing, up),
và các số đã chạy thật trong repo (Holy Commander, Frost Oracle, Lion Brawler). Số trong bảng là điểm bắt đầu; mục 9 nói cách chỉnh.
Mục đánh dấu **(cần rig v2)** dùng bộ xương ở `docs/puppet-kit-next.md` §3. Từ 2026-11-11 lion_brawler đã có rig v2 góc 3/4 (chân IK: gập gối bằng `hips.ty`, không đặt `rot` cho đùi và ống chân; mẫu: `out/heroes/lion_brawler/source/rig/anims/v2_test.json`); bảng góc chân của run/walk ở §6.2 vẫn cần rig profile (chưa có).

## 1. Quy ước (đọc một lần, không suy lại)

| Thứ | Quy ước |
|---|---|
| Nhân vật | quay mặt sang **phải**. "Trước" = phải màn hình, "sau" = trái |
| fps | 15. Một frame = 67 ms. Frame trong shot đếm từ 0; `hit_frame` đếm từ 1 trên cả animation |
| `rot` (độ) | **dương = xoay theo chiều kim đồng hồ trên màn hình** |
| Chi buông xuống (tay, chân, đuôi) | `rot` **âm** = đầu chi đi ra **trước**; dương = ra sau |
| Vật dựng lên (trượng, kiếm, đầu) | `rot` **dương** = ngọn ngả ra **trước**; âm = ngả ra sau |
| Khuỷu gập tự nhiên | cẳng tay `rot` **âm** (bàn tay lên trước) |
| Gối gập tự nhiên | ống chân `rot` **dương** (bàn chân ra sau) |
| `tx`, `ty` (px ảnh nguồn) | `tx` dương = sang phải; **`ty` dương = xuống** |
| `sx`, `sy` | 1 = nguyên; `sy` < 1 = nén (lùn); giữ thể tích: `sx ≈ 1 + (1 − sy) × 0,5` |
| `shx` | dương = ngọn ngả ra trước (phải) |
| Đơn vị độ dài | viết theo **H** (chiều cao thân) rồi đổi: `px = H_units × rig.unit` |
| Ease | `out` = giảm tốc (đến nơi), `in` = tăng tốc (rời đi), `in3`/`out3` = mạnh hơn, `inout` = cả hai, `back` = vượt quá rồi về, `step` = giữ rồi nhảy |
| Vòng lặp | dùng `osc` với `period` = số frame của vòng (hoặc ước của nó) để frame cuối nối frame đầu |

Quy tắc ease theo lực: **tay/vũ khí rời đi thì `in`, đến nơi thì `out`; đòn đánh: lấy đà `out`, ra đòn `in3`, hồi `out`**.

## 2. Năm pha của mọi động tác một lần (attack, skill, cast, levelup)

| Pha | Việc | Thời lượng (frame) | Thân | Ease |
|---|---|---|---|---|
| 1 Anticipation | đi **ngược hướng** đòn | 3-5 | nén `sy` 0,95-0,96, ngả ra sau `shx` −0,05..−0,10 | `out` |
| 2 Load | giữ đỉnh lấy đà, rung nhẹ | 1-3 | giữ | `linear` |
| 3 Release | ra đòn, **nhanh nhất** | 1-2 | giãn `sy` 1,03, ngả trước `shx` +0,08..+0,13 | `in3` |
| 4 Impact / hold | `hit_frame` là frame đầu của pha này | 3-5 | nén mạnh `sy` 0,90-0,93 rồi nảy 1,02-1,03 | `out` |
| 5 Settle | về tư thế nghỉ | 3-5 | về 1,0 | `inout` |

- Tổng 12-20 frame cho đòn thường, 20-40 cho skill. Pha 3 không bao giờ dài hơn 2 frame.
- **Follow-through**: phần mềm (áo choàng, đuôi, mào) trễ 1-2 frame sau thân và đạt đỉnh `sway` 2,0-2,5 ở frame hit, về 1,0 sau 8-10 frame. Không vượt 2,5 (lộ miếng vá).
- **Overlap**: các khớp không đổi hướng cùng frame. Thứ tự dẫn: hông → thân → vai → khuỷu → cổ tay → vũ khí, mỗi khớp trễ 1 frame.
- **Arc**: đầu chi đi theo cung. Dùng `rot` ở khớp gốc, không dùng `tx/ty` để đưa tay.

## 3. Idle thở (đã chạy trên cả 3 nhân vật)

24 frame, lặp. Mọi kênh là `osc` cùng `period` 24; pha lệch để không cứng.

| Kênh | amp | phase | Ghi chú |
|---|---|---|---|
| `body.sy` (rig v2: `spine.sy`) | −0,014..−0,016 | 0 | base 1,0 |
| `body.sx` | +0,006..+0,008 | 0 | giữ thể tích |
| `head.ty` | 2,5-3,5 px | −0,08 | đầu trễ thân |
| `head.rot` | 1,2-1,5° | −0,12 | |
| `shoulder.ty` / vai | 3 px | −0,06 | nhún vai |
| `*_upper_arm.rot` | 2-2,6° (tay xa lấy dấu ngược) | −0,10 | |
| `*_forearm.rot` | 2,2-2,5° | −0,25 | cẳng tay trễ cánh tay |
| `tail.rot` | 6° + 2° (period 12) | +0,2 | hai dao động chồng nhau |
| vũ khí cắm đất | 0-0,5° | −0,3 | gần như đứng yên; tay bám bằng IK/stretch |
| `cape.sway`, `head.sway` | 1,0 (mặc định) | - | `_sway_period`: 24 |

Nhân vật nặng: amp ×0,8, period 30. Nhân vật nhẹ, nhanh: amp ×1,2, period 18.

## 4. Đòn cận chiến pose-to-pose (đã chạy: `attack_diag_puppet`, lion `attack`)

16 frame, `hit_frame` 8, `transitions: [{"after_shot": 1, "dir": "cw"}]` (vung từ trên-sau xuống dưới-trước; ngược lại thì `ccw`).

| Shot | Rig | Frame | Track |
|---|---|---|---|
| ready | rig chính | 2 | `body.sy` 1→0,955 `out`; tay cầm vũ khí nhích ngược hướng đòn |
| p1 (lấy đà) | pose p1 | 5 | `root.shx` −0,09 → −0,03 (f2, `out`) → −0,05 (f3) → +0,06 (f4, `in`); `root.sy` 1,06 → 1,0 (f2) → 0,96 (f4, `in`); `root.sx` 0,96 → 1,0 → 1,03 |
| p2 (trúng) | pose p2 | 6 | `root.shx` +0,12 → −0,02 (f2, `out`) → 0 (f4); `root.sy` 0,90 → 1,03 (f2, `out`) → 1,0 (f4); `root.sx` 1,08 → 0,985 → 1,0 |
| recover | rig chính | 3 | `body.sy` 0,94 → 1,0 `out`; các khớp về 0 |

Sau đó: `puppet.py track` rồi `puppet.py slash --lag 4.2` (vệt phủ ~70% cung).

## 5. Đòn bằng rig thuần (đã chạy: Frost Oracle `shoot`, Holy Commander `levelup`)

Đẩy vũ khí ra trước (16 frame, hit 8). `K` = frame: 0 nghỉ, 5 đỉnh lấy đà, 7 ra đòn, 10 giữ, 15 về.

| Kênh | 0 | 5 (`out`) | 7 (`in3`) | 10 (`out`) | 15 (`inout`) |
|---|---|---|---|---|---|
| `body.shx` | 0 | −0,07 | +0,10 | +0,06 | 0 |
| `body.sy` | 1 | 0,965 | 1,03 | 1,0 | 1,0 |
| `head.rot` | 0 | −5 | +7 | +3 | 0 |
| vũ khí `ty` (H) | 0 | −0,075 | −0,043 | −0,039 | 0 |
| vũ khí `tx` (H) | 0 | −0,037 | +0,05 | +0,04 | 0 |
| vũ khí `rot` | 0 | −16 | +34 | +28 | 0 |
| tay tự do `rot` | 0 | +24 (ra sau) | −72 (đấm ra trước) | −60 | 0 |
| phần mềm `sway` | 1 | 1,5 | 2,6 | - | 1 |

Nhấc lên rồi dộng xuống (26 frame, hit 15): nén f3 (`sy` 0,955) → nhấc f9 (`ty` −0,14 H, `sy` 1,04, `out3`) → giữ f12 → dộng f14 (`ty` +0,01 H, `sy` 0,925, `in3`) → nảy f18 (`sy` 1,025) → nghỉ f22.

## 6. Vòng chạy (run) và đi (walk)

### 6.1 Bằng pose khoá (đã chạy: lion `run_side`, 8 frame)

4 ảnh: contact A, passing A, contact B, passing B. Mỗi pose 2 frame, track `step`:

| Pose | frame 0 | frame 1 |
|---|---|---|
| contact | `ty` 0, `sy` 1,0, `sx` 1,0 | `ty` +5, `sy` 0,975, `sx` 1,015 (lún) |
| passing | `ty` +7, `sy` 0,965, `sx` 1,02 (thấp nhất) | `ty` −9, `sy` 1,03, `sx` 0,985 (đạp lên) |

Yêu cầu ảnh: thân ngả trước ~20°, **tay ngược chân, khuỷu gập ~90° ở cả hai tay và ghi số trong prompt**, đầu cùng cỡ. Căn cỡ: `puppet.py pose --colour ... --ref-source plate`.

### 6.2 Bằng rig chân, góc profile **(cần rig v2)**

Run 8 frame (0,53 s), mỗi chân lệch nhau 4 frame. Góc là `rot` của khớp so với cha, theo quy ước mục 1. Bảng cho **một chân**; chân kia dùng cùng bảng lệch 4 frame.

| Frame | Pha | `thigh.rot` | `shin.rot` | `foot.rot` | `hips.ty` (H) |
|---|---|---|---|---|---|
| 0 | contact (gót chạm, chân trước) | −35 | +10 | −15 | 0 |
| 1 | down (chịu lực) | −20 | +40 | 0 | +0,04 |
| 2 | passing (dưới thân) | 0 | +20 | 0 | +0,02 |
| 3 | up (đạp đất) | +25 | +5 | +30 | −0,04 |
| 4 | rời đất, chân sau | +35 | +60 | +40 | 0 |
| 5 | gót đá lên | +15 | +100 | +30 | +0,04 |
| 6 | gối vung trước | −30 | +95 | 0 | +0,02 |
| 7 | vươn ra | −50 | +45 | −10 | −0,04 |

| Kênh khác | Giá trị |
|---|---|
| `spine.rot` | +12..+18 cố định (ngả trước), cộng `osc` ±2, period 4 |
| `hips.rot` | `osc` ±4, period 8 |
| `head.rot` | −8 (bù ngả thân), `osc` ±1,5 period 4 |
| `*_upper_arm.rot` | `osc` ±40, period 8, **ngược pha với chân cùng bên** |
| `*_forearm.rot` | −90 cố định ±10 (khuỷu luôn gập khi chạy) |
| đuôi, áo choàng | `rot` −25 (bay ra sau) + `osc` ±6 period 4; `sway` 1,6 |
| `z` | chân và tay bên xa vẽ sau thân; bên gần vẽ trước |

Walk 12 frame (0,8 s): cùng cấu trúc, biên độ nhỏ hơn: `thigh` −25..+25, `shin` 0..+60, `hips.ty` ±0,02 H, tay ±20, khuỷu −20, `spine.rot` +3. Trong walk luôn có một chân chạm đất; trong run có 2 frame cả hai chân rời đất (frame 3-4).

Kiểm: `python scripts/motion_check.py <asset>/frames/run_side --loop` không có cờ; `ground` không đổi; `torso_x` lệch dưới 6 px.

## 7. Các động tác khác (khung thời gian)

| Động tác | Frame | Khoá | Ghi chú |
|---|---|---|---|
| Hit / hurt | 6 | f0 `shx` −0,12, `sy` 0,94, `tx` −0,03 H → f2 `back` → f5 nghỉ | chớp trắng là fx |
| Death (sụp tại chỗ) | 9-14 | f0-2 giật ra sau; f3-8 `hips.ty` +0,35 H `in`, `spine.rot` +60; f9+ nằm yên | rig hiện tại: dùng 1-2 pose still |
| Respawn | 18-30 | từ pose quỳ; `grey` 1 → 0 trong 10 frame; đứng lên `out3` | kênh `grey` đã có |
| Level up / gầm | 20-26 | nén 3 frame → pose đỉnh ở f3-4 (hit) → giữ 10-14 frame với `osc` `sy` ±0,012 period 4 → về | |
| Cast giơ cao | 24 | nén f3 → giơ f9 (`out3`) → giữ tới f15 (rung `rot` ±3) → hạ f19 (`in3`) → nghỉ f23 | |
| Nhảy tại chỗ | 14 | nén f0-3 (`sy` 0,88) → bật f4-6 (`ty` −0,5 H, `sy` 1,10, `out`) → rơi f7-9 (`in`) → tiếp đất f10 (`sy` 0,90) → nảy | bóng co 60% ở đỉnh (chưa có) |
| Dộng đất | 20 | như mục 4 nhưng p1 vươn cao (`ty` −0,03 H, `sy` 1,07) và p2 rung `ty` +6, −3, +3, −1 px | |
| Xoay thân **(cần rig v2 + profile)** | 6-8 | 3/4 (2 f) → `pose_turn` (1-2 f, `sx` 0,92) → profile | không nội suy hình; che bằng fx nếu cần |

## 8. Mẫu JSON tối thiểu

```json
{
  "version": "p01", "fps": 15, "loop": false, "hit_frame": 8,
  "transitions": [{"after_shot": 1, "dir": "cw", "ease": "linear"}],
  "shots": [
    {"name": "ready",   "rig": "source/rig/rig.json",          "frames": 2, "tracks": {"body.sy": [[0, 1.0], [1, 0.955, "out"]]}},
    {"name": "p1",      "rig": "source/rig/poses/x_p1.json",   "frames": 5, "tracks": {"root.shx": [[0, -0.09], [2, -0.03, "out"], [4, 0.06, "in"]]}},
    {"name": "p2",      "rig": "source/rig/poses/x_p2.json",   "frames": 6, "tracks": {"root.sy": [[0, 0.90], [2, 1.03, "out"], [4, 1.0, "inout"]]}},
    {"name": "recover", "rig": "source/rig/rig.json",          "frames": 3, "tracks": {"body.sy": [[0, 0.94], [2, 1.0, "out"]]}}
  ]
}
```

Vòng lặp một rig: bỏ `shots`, đặt `"rig"`, `"frames"`, `"tracks"` ở gốc, `"loop": true`, mọi track là `{"base": v, "osc": {"amp", "period", "phase"}}`.

## 9. Checklist trước khi xuất (làm đúng thứ tự)

1. `python scripts/puppet.py render <asset> <anim> --sheet <tên> --no-export`, mở `.work/puppet/<tên>/contact.png`.
2. Không frame nào chạm mép ô (176x140 @1x). Chạm thì giảm `ty`/`rot`, **không** thu nhỏ nhân vật.
3. Chân: bàn chân không rời đường đất trừ khi là nhảy/chạy.
4. Cỡ đầu giữa các shot lệch không quá 5% (đo như `docs/puppet-kit.md`, mục vòng chạy). Lệch thì chạy lại `puppet.py pose`, không sửa bằng `sx/sy`.
5. Frame hit là frame nén mạnh nhất hoặc vươn xa nhất; `hit_frame` trỏ đúng frame đó (đếm từ 1).
6. Không có hai frame liền nhau giống hệt (trừ khi cố ý giữ); pha release ≤ 2 frame.
7. Vòng lặp: frame cuối và frame đầu khác nhau không hơn các cặp liền kề (`motion_check.py --loop`).
8. Phần mềm (`sway`) ≤ 2,5; lộ mảng màu lạ ở mép lớp thì giảm biên độ hoặc xin lớp khuất (`puppet-kit-next.md` §2).
9. Xuất thật, cập nhật dòng manifest trong `brief.md` (⏳), thêm dòng `history.md`.

## 10. Chỉnh theo cảm giác (bảng tra nhanh)

| Thấy | Sửa |
|---|---|
| Đòn yếu | kéo dài anticipation +2 frame; rút release còn 1 frame; tăng nén ở hit (`sy` −0,03) |
| Nhân vật nhẹ như giấy | tăng frame settle; giảm `back`; thêm trễ cho đầu và vai |
| Cứng như robot | lệch pha các khớp 1 frame; thêm `osc` nhỏ ở đầu; dùng `inout` thay `linear` |
| Giật ở chỗ cắt pose | frame cuối pose trước ngả theo hướng đòn (`shx` +0,06), frame đầu pose sau vượt quá (`shx` +0,12, `sy` 0,90) |
| Trượt chân | kiểm `ground` của pose; chân phải ghim (rig v2: IK chân) |
| Lộ khe giữa các lớp | giảm biên độ khớp đó; kiểm đa giác bằng `check`; xin lớp khuất |
