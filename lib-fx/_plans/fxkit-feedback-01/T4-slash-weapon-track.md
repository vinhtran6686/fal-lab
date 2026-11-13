# T4. Vệt chém theo quỹ đạo vũ khí thật

Phụ thuộc: T3 (cùng file `slash.py`).

## Vấn đề
Trên `azure_blade`, vệt fxkit nối mũi đao pose A với mũi đao pose B bằng **một parabol** (`c.sp.path(f, bend)`), bề rộng là hằng số. Cú chém thật:
chuôi đao đi một đường cong qua trên đầu, lưỡi **xoay quanh chuôi** thuận kim đồng hồ, nên mũi đao vẽ một cung **không đối xứng** và vệt phải là
**bề mặt lưỡi quét qua** (rộng đúng bằng chiều dài lưỡi, mép dẫn song song lưỡi). Bản đã duyệt làm đúng điều này:
`out/heroes/azure_blade/source/vfx/crescent/build_crescent.py`, hàm `sweep_samples` (chuôi đi Bezier bậc hai, góc lưỡi nội suy có `ease`, chiều dài nội suy)
và dữ liệu `weapon_marks.json` (`A.root`, `A.tip`, `B.root`, `B.tip`, `root_ctrl_dx`, `root_ctrl_up`, `ease`).

## File được sửa
- `lib-fx/_core/formulas/draw/fxkit/space.py` (đổi toạ độ người gọi → canvas), `effect.py` (truyền gốc toạ độ vào `Space`)
- `lib-fx/_core/formulas/draw/fxkit/layers/slash.py` (chế độ theo vũ khí)
- `lib-fx/build.py` (cờ mới), `FXKIT.md` mục 6, `docs/pipeline/pose-pair-fx-method.md` bước 7 (cách gọi mới; ghi rõ bản cũ vẫn là bản đã duyệt)
- **Không** sửa gì trong `out/heroes/azure_blade/`.

## Cách làm
1. **Toạ độ người gọi**: `render()` dời gốc toạ độ (`x0, y0`). Thêm vào `Space` hai trường `ox, oy` và hàm `sp.world((x, y)) -> (x - ox, y - oy)` để một
   lớp nhận điểm trong toạ độ của người gọi (px @2x trong ô nhân vật) và đổi sang canvas. `render` truyền `x0, y0` vào.
2. **Quỹ đạo vũ khí** trong `slash`: thêm tham số `track=None`. Khi `track` là dict
   `{"root_a": (x, y), "root_b": (x, y), "root_up": px, "root_dx": px, "turn": "cw" | "ccw", "ease": 1.3}`:
   - mũi lúc đầu = `c.sp.a`, mũi lúc cuối = `c.sp.b` (vẫn là `--from` / `--to`);
   - với `f` trong 0..1: chuôi `r(f)` = Bezier bậc hai từ `root_a` tới `root_b`, điểm điều khiển = trung điểm + (`root_dx`, −`root_up`) (trục màn hình);
     góc lưỡi `ang(f)` nội suy từ góc(root_a → a) tới góc(root_b → b) theo chiều `turn`, với `f ** ease`; chiều dài lưỡi nội suy tuyến tính;
     mũi `p(f) = r(f) + L(f) * (cos ang, sin ang)`.
   - Vệt = **bề mặt quét**: thay `at(f)` bằng cặp (mép ngoài = `p(f)`, mép trong = `r(f) + (1 - blade) * (p(f) - r(f))`), với tham số
     `blade=1.0` (phần lưỡi tính từ mũi vào: 1.0 = cả lưỡi tới chuôi, 0.6 = 60 % phía mũi). Toạ độ nét `c` (ngang) chạy từ mép trong tới mép ngoài
     dọc theo **chính đường lưỡi**, nên mép dẫn của vệt song song với lưỡi ở pose B.
   - Bề rộng theo `v` (đuôi → đầu) vẫn thuôn như hiện tại nhưng bằng cách **kéo mép trong về phía mép ngoài** ở đuôi (đuôi nhọn bám theo cung mũi đao).
   - Mũi đậm, chuôi nhạt: sợi phía mũi (T3) rộng và sáng (`hot`), sợi phía chuôi mảnh và tàn trước.
   Mọi thứ của T3 (sợi dọc, loại vũ khí, pha tàn) dùng lại nguyên, chỉ đổi hàm toạ độ nét.
3. `build.py`: cờ `--track root_a=X,Y;root_b=X,Y;up=35;dx=0;turn=cw;ease=1.3` (hoặc `--track-file weapon_marks.json` đọc đúng định dạng file đang có của
   `azure_blade`, kèm hai hàm đăng ký rig A / B: xem `tf_of` trong `build_crescent.py` cho phép đổi px ảnh gốc → px ô @2x; nếu quá phức tạp thì chỉ làm cờ
   `--track` nhận sẵn toạ độ ô @2x và ghi rõ trong doc cách tính). Cờ này đặt tham số `track` cho lớp có kind `slash`.
4. Nhịp ở 15 fps: cú quét (`attack`) dài 0.1 s = 1.5 khung. Kiểm tra khung đầu của vệt **bắt đầu đúng trên lưỡi pose A** và khung vệt đầy có mũi
   **trùng mũi đao pose B** (checklist "Vệt chém" trong `docs/pipeline/pose-pair-fx-method.md` §5).
5. Bản thử so sánh (không ghi vào `out/`): dựng ra thư mục tạm, ghép lên thân `frames/skill_crescent_puppet_side` ở khung `hit - 1`, đặt cạnh
   `frames/skill_crescent_side` đã duyệt. Số liệu của `azure_blade` (ô @2x): mũi A (107.3, 191.1), chuôi A (118.5, 144.1), mũi B (238.6, 241.0),
   chuôi B (202.9, 241.5), `hit_frame` 23, 15 fps, `root_ctrl_up` 35, `ease` 1.3, quay thuận kim đồng hồ.

## Tiêu chí nghiệm thu
- [ ] Chồng đường mũi đao của bản đã duyệt (`frames/skill_crescent_side/track.json`, mảng `samples[].tip_px2x`) lên vệt mới: mép ngoài của vệt lệch
      không quá 4 px @2x ở mọi mẫu.
- [ ] Ở khung vệt đầy, mép dẫn của vệt trùng lưỡi đao pose B (lệch ≤ 3 px); khung đầu bắt đầu trên lưỡi pose A.
- [ ] Bề rộng vệt ở phần đầu = chiều dài lưỡi × `blade` (±10 %).
- [ ] Không có `track` thì kind chạy y như sau T3 (so khung: giống hệt).
- [ ] `fxkit_test.py` qua; `melee/slash --check` không FAIL.

## Kết quả (người làm điền)

Làm xong 2026-11-13. Đã sửa: `space.py` (`origin`, `Space.world`), `effect.py` (truyền `x0, y0`), `layers/slash.py` (tham số `track`, `blade`: mũi `swing(f)`, `at/lat/strand` giữ nguyên, chỉ đổi nguồn đường và độ lệch `OFS`), `build.py` (cờ `--track`), `FXKIT.md` mục 6, `docs/pipeline/pose-pair-fx-method.md` (cách gọi mới sau bước 7, bản cũ vẫn là bản đã duyệt).
- Lệnh thử (azure_blade, ô @2x): `python lib-fx/build.py melee/slash/crescent --from 107.3,191.1 --to 238.6,241.0 --pal frost --fps 15 --split --out <tmp> --track "root_a=118.5,144.1;root_b=202.9,241.5;up=35;turn=cw;ease=1.3"`.
- Quỹ đạo: mép ngoài lệch so với `track.json` (khoảng cách mẫu mũi tới hợp các khung): 2.0, 0, 0, 0, 0, 1.4 px (bản parabol cũ: 1.4, 11.2, 24.1, 19.6, 0, 2.2). Đạt (<= 4).
- Mép dẫn ở khung vệt đầy (khung 2 ở 15 fps) nằm trên lưỡi pose B: lệch 1.1 px, trải 34.2 / 35.8 px chiều dài lưỡi (96 %, blade = 1.0). Đạt. Khung đầu: đuôi nhọn bắt đầu ở mũi pose A (2 px).
- Không `--track`: toàn bộ khung PNG giống hệt (md5) trước và sau. `fxkit_test.py`: all checks passed. `build.py melee/slash --check`: không FAIL (chỉ cảnh báo `pop` / `cut` đã có từ trước, bản cũ cũng báo).
- Thay đổi so với đặc tả: (1) điểm điều khiển của chuôi dùng `min(y chuôi A, y chuôi B) - up` như `sweep_samples` đã duyệt (đặc tả ghi "trung điểm", sai lệch 12-40 px nếu theo đúng chữ); (2) khi có `track`, đầu vệt mọc tới 1.0 bằng `0.45 + 0.55 * out_quint(g)` (công thức cũ dừng ở 0.95 nên khung đầy chưa tới mũi B); (3) chỉ làm cờ `--track` nhận sẵn toạ độ ô @2x, không làm `--track-file` (đã ghi trong doc); (4) cờ áp cho mọi lớp kind `slash`, gồm cả `echo` của `heavy`.
- Chưa làm / hạn chế: thử `heavy`, `axe`, `thrust` với `--track` chỉ để chắc không lỗi (không xem kỹ hình); răng cưa `teeth` và sợi tóc `streaks` ở chế độ track chỉ dò mắt (không có ca chạy với `saw`). Ảnh trước / sau xem ở contact sheet 3x3 (ngoài repo): bản trước là cánh bướm lệch, bản sau là dải bám cung mũi đao; xem `preview_game.gif` thấy dải rõ, không bị mất hình ở cỡ game. Các hiệu ứng được khen (spark, quake, bolt) không bị đụng (chỉ sửa kind slash, Space thêm trường mặc định).
