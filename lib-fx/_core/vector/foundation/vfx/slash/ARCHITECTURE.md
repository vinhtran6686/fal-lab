# Slash: kiến trúc bộ sinh và hướng "FX đi theo vũ khí"

Viết 2026-11-10 theo yêu cầu user: ghi lại kiến trúc của bộ sinh slash và cách làm **hiệu ứng chém đi theo chuyển động của vũ khí**
(chưa làm, mới thống nhất hướng), để một session / AI sau đọc là làm được. Bối cảnh: [generators.md](generators.md) (các bộ sinh, luật,
điểm chấm), [../../../STATUS.md](../../../STATUS.md) (trạng thái), tư duy chung [lib-fx/MINDSET.md](../../../../../MINDSET.md) (Phase 2-3).

## 1. Kiến trúc hiện tại (v1.10)

```
 THÂN NHÂN VẬT             KHUNG TOẠ ĐỘ              NGÔN NGỮ NÉT                 THỜI GIAN               DỰNG
 H, FEET (điểm chân)  ─►   mỗi nhát một khung   ─►   nét thon nhiều sợi      ─►   bảng TIMELINE      ─►   render_sequence
 SHOULDER, IMPACT          EllipseFrame(tâm, k,      (dải chính, dải giữa,        mỗi hình vẽ: head,      nhiều khung, phản chiếu,
 (gen_slash_combo)         tilt), ReflectFrame,      sợi tối, vệt tốc độ,         tail, w, spread, brk,   backdrop (hình nộm),
                           khung tròn cho toé        đầu chổi khô, răng khía,     frames (giữ = 2 frame)  làm mịn, glow → PNG/SVG/GIF
                                                     vụn, toé, tím đuôi)
```

| Tầng | Vai trò | Ở đâu |
|---|---|---|
| Thân | mọi vị trí tính theo chiều cao thân `H` và điểm chân `FEET` (điểm neo lib-fx / `scripts/fx_layers.py`), quay về +x | `gen_slash_combo.py`: `H`, `FEET`, `SWEEP`, `SHOULDER`, `IMPACT` |
| Khung toạ độ | u = vị trí dọc đường chém (rad), v = lệch ngang (px). Nét chỉ cần `to_xy(u, v)`, `u_px`, `u_scale` | `frames.py`: `EllipseFrame`, `ReflectFrame` (+ `PolarFrame`, `LinearFrame` của bộ dựng lại) |
| Kiểu (phong cách) | độ rộng, phối cảnh (`back`, `front`), số sợi, đầu nét, răng, vệt, vụn, nét tóc tối thiểu | `gen_slash_loop.STYLES` (`light`, `heavy`, `front-heavy`, `combo-sweep`, `combo-smash`) |
| Một hình vẽ | từ (kiểu, dòng thời gian) → nét cho mỗi lớp màu | `gen_slash_loop.drawing(D, k, timeline)`, `design(seed, style)` |
| Thời gian | mỗi nhát một bảng; frame là frame **chung** của cả hiệu ứng | `TIMELINE*`, `T_SWEEP`, `T_SMASH`, `SPLASH` |
| Thành phần phụ | toé lúc chạm đất, vệt loang, tím ở đuôi | `gen_slash_combo._splash`, `_violet_tail` |
| Dựng | nhiều khung (nét chọn khung bằng `"frame": i`, vết cắt chỉ cắt cùng khung), phản chiếu sàn, ảnh nền xem thử | `gen_render.render_sequence(..., frame=[...], reflection=..., backdrop=...)` |
| Xem thử | hình nộm cầm vũ khí dài cố định, tay trượt dọc cán | `dummy.Dummy(feet, H, size, weapon=1.35).frame(tip)`, cờ `--dummy` |

**Chiều phụ thuộc hiện tại: FX → vũ khí.** Đường chém được đặt trước (tâm, bán kính, góc, nhịp); hình nộm chỉ **đọc** vị trí đầu nét
ở mỗi frame (`gen_slash_combo._tips`) để đặt mũi vũ khí. Vì hai bên dùng chung hình học nên khớp (user 2026-11-10: "đòn chém khớp vũ khí rồi").

## 2. Hướng tiếp theo: vũ khí → FX (đảo chiều)

User hỏi (2026-11-10): đổi vị trí / biên độ chuyển động của vũ khí thì có build được FX slash combo theo đúng đường vũ khí đi không?
**Có.** Đầu vào là **đường đi của mũi vũ khí theo frame**, đầu ra là các nhát chém. Toàn bộ ngôn ngữ nét và bộ dựng dùng lại nguyên;
chỉ thêm tầng "đọc vũ khí" ở đầu.

```
 đường đi mũi vũ khí ─► chia nhát ─► khớp hình mỗi nhát ─► nhịp từ đường đi ─► (kiểu từ STYLES) ─► drawing() ─► render_sequence
 (JSON / hình nộm /     (theo tốc     (cung elip, hoặc      (head = mũi ở frame f,
  clip nhân vật)         độ, hoặc      khung theo đường      tail đuổi theo, va chạm
                         user đánh     cong bất kỳ)          = mũi dừng → giữ 2 frame)
                         dấu)
```

### 2.1 Dữ liệu vào (đề xuất định dạng)

Một file JSON, sửa được bằng tay hoặc bằng một trang kéo thả sau này:

```jsonc
{
  "body":   {"H": 170, "feet": [340, 480], "facing": 1},
  "weapon": {"length_H": 1.35, "kind": "spear"},
  "fps": 25,
  "keys": [                                   // vị trí MŨI vũ khí, đơn vị H, gốc = điểm chân, x về phía trước, y lên trên
    {"f": 0,  "tip": [-0.9, 0.75]},
    {"f": 3,  "tip": [ 1.2, 0.55], "ease": "out"},
    {"f": 7,  "tip": [-0.6, 1.9]},            // lấy đà: giơ ra sau, trên đầu
    {"f": 11, "tip": [ 1.75, 0.0], "impact": true}
  ],
  "slashes": [                                 // tuỳ chọn: user tự chia nhát; bỏ trống thì tool tự chia (§2.2)
    {"from": 0, "to": 3, "style": "combo-sweep", "depth": "ellipse"},
    {"from": 8, "to": 11, "style": "combo-smash", "depth": "plane", "splash": true}
  ]
}
```

Nguồn của `keys`: (a) user chỉnh frame khoá của hình nộm; (b) đánh dấu mũi vũ khí trên 3-5 frame khoá của clip attack nhân vật thật
(`out/heroes/<id>/frames/<sheet>/`, cùng khung và điểm neo vì `video-sprite` xuất một khung, một cỡ thân cho mọi động tác); (c) sau này: tự dò
mũi vũ khí trên clip. Giữa các frame khoá: nội suy theo góc quanh vai (như `_tips` đang làm cho pha lấy đà), không nội suy thẳng (mũi sẽ
cắt qua thân).

### 2.2 Chia nhát

- Tốc độ mũi `|tip(f+1) - tip(f)|`: **nhanh** = đang chém, **chậm / đứng** = lấy đà hoặc va chạm. Một nhát = một đoạn tốc độ cao liên tục.
- Đổi hướng gắt (góc rẽ > ~90° trong 1-2 frame) = **tách nhát** (nhát hồng gãy góc của slash-trio là 2 đoạn nối nhau).
- `impact: true` hoặc mũi chạm sàn (`y = 0`) rồi dừng = điểm va chạm: đầu nét dừng ở đó, giữ 2 frame (nhát nặng), sinh toé (`_splash`).
- Nhát sau **sinh khi nhát trước còn đang tàn** (gối lên nhau), như combo hiện tại (nhát 2 sinh ở frame 8, nhát 1 tàn tới 11).

### 2.3 Khớp hình mỗi nhát

| Đường đi của mũi | Cách khớp | Lý do |
|---|---|---|
| gần tròn, vung **quanh thân** (có chiều sâu) | **khớp elip** (tâm, bán kính, dẹt `k`, nghiêng) bằng bình phương nhỏ nhất trên các điểm mũi → `EllipseFrame` | giữ phía xa mảnh, phía gần dày (`_persp`); đây là cách các kiểu loop đang vẽ |
| gần tròn, **trong mặt phẳng** (bổ dọc, quét phẳng trước mặt) | khớp elip với `back = front = 1` (không phối cảnh) | như `combo-smash` |
| cong tự do (chữ S, xoắn) | **khung theo đường cong** `PathFrame` (chưa có: u = độ dài cung dọc đường cong, v = lệch theo pháp tuyến; ~40-60 dòng trong `frames.py`) | đi đúng nét user vẽ |
| gãy góc | tách thành 2 nhát nối nhau | mép trong của nét tự cắt nhau nếu độ dày > bán kính cong |

Ràng buộc: độ dày nét ≤ bán kính cong ở mọi chỗ (giới hạn `W` theo độ cong, hoặc làm trơn đường trước khi khớp).

### 2.4 Nhịp lấy từ đường đi

- `head(f)` = vị trí (u) của mũi ở frame f trên khung đã khớp; `tail(f)` = đuổi theo, bám theo các luật đã có: đuôi đứng gần chỗ sinh tới đỉnh,
  sau đỉnh đuổi nhanh (xem các bảng `TIMELINE*`); sau va chạm `head` giữ nguyên ở điểm chạm.
- `w` (độ dày theo thời gian) và `spread` / `brk` (giãn rồi đứt) giữ theo luật vòng đời: đỉnh ở frame mũi đi nhanh nhất hoặc frame va chạm,
  sau đó giãn 1 hình rồi mới đứt, mỗi sợi đứt chỗ riêng.
- Tốc độ mũi → độ dày / độ dài nét: vung nhanh thì nét dày và dài hơn (đề xuất: `w ∝ (tốc độ / tốc độ lớn nhất)^0.5`, kẹp 0,4-1).
- Phong cách (số sợi, đầu nét, màu, toé, nặng / nhẹ) **không** lấy từ vũ khí: chọn kiểu trong `STYLES` (hoặc theo `weapon.kind`).

### 2.5 File sẽ đụng tới khi làm

| File | Việc |
|---|---|
| `dummy.py` | nhận `keys` (frame khoá) thay vì chỉ một hàm `tip(f)`; nội suy theo góc quanh vai |
| `gen_slash_weapon.py` (mới) | đọc JSON → chia nhát → khớp elip / `PathFrame` → sinh bảng thời gian → gọi `gen_slash_loop.drawing` + `render_sequence` (như `gen_slash_combo.build`) |
| `frames.py` | `PathFrame` (khi cần nhát cong tự do) |
| `_tools/vectorfx.py` | lệnh `gen-slash NAME --weapon path.json [--dummy]` |
| `gen_slash_combo.py` | trở thành một trường hợp của bộ trên: combo hiện tại = một file JSON vũ khí |

### 2.6 Kiểm thử đề xuất

1. Xuất đường đi mũi vũ khí của combo hiện tại (`_tips`) ra JSON → dựng lại bằng hướng mới → so từng frame với `gen-slash-combo-blue`
   (phải gần như trùng: cùng hình học).
2. Đổi biên độ (chạm đất xa 2 H; quét thấp ngang hông; thêm nhát thứ 3 hất lên) → xem tool tự dựng lại, xem kèm hình nộm, user chấm.
3. Lấy `keys` từ clip attack một nhân vật thật trong `out/heroes/` → ghép thử (Phase 3).

## 3. Giới hạn và quyết định của user

- Đường đi vũ khí quyết định **ở đâu và khi nào**; **phong cách** vẫn từ `STYLES`.
- Vung quanh thân nên khớp elip (giữ chiều sâu); nhát phẳng trước mặt đi đúng nét.
- Trạng thái: **chưa làm** (user 2026-11-10: "chưa cần làm, note lại"). Khi làm: theo §2.5-2.6, cập nhật file này, `generators.md`, `STATUS.md`.
