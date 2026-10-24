# Fx Studio: sprite sheet hiệu ứng 2D → frame cho Kingdom Rush 1

Đầu vào là **một sprite sheet** của hiệu ứng (lửa, nổ, phép...). Tool cắt từng frame, bỏ nền, chỉnh màu, cỡ, điểm neo và nhịp,
rồi xuất frame đúng định dạng game (giống `ref/hero`). Bước cài sẽ đóng gói vào game KR1 (LÖVE 0.10.2) để xem ngay trong level.
Không gọi model, không tốn phí.

## App (cách dùng chính): studio với timeline
**https://claude.ai/artifact/JUVk6cDVriDXhLXLTTQzVi**: chạy trong trình duyệt, không cần server hay Python.

1. **Thanh trên: Nhân vật → Pose** (Holy Commander 9 pose, Diablo, Ignus của KR1). "Không có" = chỉnh hiệu ứng tự do.
   Pose có ✓ là skill đã lưu.
2. **Timeline (dưới)**: thước tính bằng frame game (30 / giây); tầng đầu là pose của nhân vật (vạch đỏ **hit** = frame trúng
   đòn), mỗi hiệu ứng là một tầng riêng. Bấm hoặc kéo trên thước để tua; **kéo một tầng sang ngang** để đổi lúc nó bắt đầu
   (tự hít vào frame hit); ● ẩn/hiện, ✕ xóa.
3. **+ Thêm hiệu ứng**: nhập sprite sheet, lửa mẫu, hoặc lấy từ thư viện (mỗi skill giữ một bản sao riêng, chỉnh không ảnh
   hưởng skill khác). Hiệu ứng mới bắt đầu tại đầu phát: dừng ở frame muốn gắn rồi thêm.
4. **Panel phải** chỉnh tầng đang chọn: *Bắt đầu ở frame* (nút **Gắn vào hit**, **Tại đầu phát**), vị trí (kéo trên khung
   xem; số là px trong game từ chân nhân vật tới tâm hiệu ứng), kích thước, màu, các hình và tốc độ; mỗi mục có ↺.
5. **Frame tuner** (chuột phải hoặc ⋯ trên tầng nhân vật): bấm hình để giữ/bỏ, số giữ (frame game) cho từng hình, ◎ đặt
   frame hit; nút Giữ tất cả, Bỏ 1 trong 2, mọi hình giữ N frame, Về gốc; **Áp dụng**. Tầng hiệu ứng đang gắn vào hit tự dời
   theo hit mới. Pose đã chỉnh lưu trong skill (`poseEdit`), tầng nhân vật ghi "đã chỉnh".
6. Tốc độ hiệu ứng: Nhanh/Chuẩn/Chậm, ô **giữ N frame/hình** (số tùy ý 1-60), hoặc **kéo mép trái/phải** của tầng trên
   timeline để co giãn (số giữ chia lại theo độ dài mới). Chuột phải trên tầng hiệu ứng: nhân đôi, đổi thứ tự, xóa.
   Phím `,` `.` dời tầng đang chọn 1 frame.
7. **Lưu**: lưu skill (mọi tầng, sheet, gói frame) vào app, cùng **một sheet gộp** = nhân vật + mọi tầng đang hiện, từng frame
   game (frame giống nhau liên tiếp thành alias, điểm neo ở chân). Sheet mới cũng vào thư viện. **Bỏ thay đổi** về bản đã lưu.
   @2x của sheet gộp phóng từ @1x (danh mục chỉ có frame nhân vật @1x).
8. Đưa vào game: nhắn Claude **“cài skill <nhân vật>__<pose> từ Fx Studio”**, hoặc **Tải gói .zip** rồi
   `python scripts/fx_studio.py install-pack <key>.fxskill.zip`.

Nhịp của pose lấy từ bảng animation của game khi nhân vật đã có trong game (mỗi frame atlas = 1 frame game, đúng như game
chạy; holy_commander chạy nhanh gấp đôi con số 15 fps trong meta.json), còn không thì từ meta.json (tầng nhân vật ghi
"game" hay "meta"). Khung xem hiện **đúng các frame sẽ vào game**: app render một lần, gói chứa chính các frame đó.

### Mẫu hiệu ứng đã duyệt
"+ Thêm hiệu ứng → Mẫu hiệu ứng đã duyệt…" mở bảng thẻ có hình động (thân Holy Commander + hiệu ứng). Đó là 9 fx Python user đã duyệt
(`docs/python-fx-recipe.md` §9): levelup v03 (bản chốt), v01, v05-v10 và tia radiant_slash. Mỗi mẫu thêm **2 tầng** (sau thân `Z_DECALS`,
trước thân `Z_EFFECTS`) trong một bước hoàn tác, mỗi hình = 1 frame thân, hòa trộn **Cộng sáng**. Trên Holy Commander · Lên cấp / Radiant
slash, mẫu bắt đầu ở frame 0, khớp từng frame. Trên pose khác, mẫu được dời để đỉnh hiệu ứng trùng frame hit, và app nhắc rằng hào quang vẽ
theo dáng Holy Commander. Vẽ lại: `PYTHONUTF8=1 python tools/fx_studio/build_samples.py render [id]` (ghi `tools/fx_studio/samples/`).

**Vẽ theo dáng này** (nút trên thẻ của 8 mẫu levelup): vẽ lại hào quang quanh dáng của nhân vật + pose đang mở, ngay trong trình duyệt.
Mã là bản chép của `levelup_variants.py` (cùng canvas 700x720, BODY 425, cùng số, mặt nạ số thực; canvas chỉ để vẽ hình). Thân lấy từ frame
@2x đúng như sheet gộp vẽ (cả khi đã chỉnh Frame tuner), bỏ bóng dưới chân; chiều cao thân = khung idle x 0,897 (hiệu chỉnh theo bản export
đã duyệt của Holy Commander); chớp sáng đặt ở điểm cao nhất của thân tại frame đỉnh. Đỉnh hiệu ứng (python frame 22) = frame hit, sửa được
trong ô "đỉnh ở frame". Trên Holy Commander · Lên cấp dùng đúng bảng frame đã duyệt (`keep`): so với bản export, lớp sau thân lệch trung bình
3,7/255, lớp trước thân (viền sáng mảnh) IoU 0,72. Mất khoảng 7-8 giây cho 27 frame. Nguồn gốc ghi trong `recipe.gen`.

**Xuất GIF** (thanh trên): toàn bộ skill đúng như khung xem (nền, hướng nhìn, phóng to, cả tầng ở mục tiêu và tầng bay), mỗi frame game một hình,
30 frame/giây (trễ 3-3-4 phần trăm giây), lặp mãi, cắt sát phần có hình. Bộ mã hóa GIF89a tự viết (bảng màu median cut 256 màu).

**Cộng sáng** (Màu → Hòa trộn) có trong khung xem và trong sheet gộp. Tầng cài riêng vào game vẽ thường (sprite KR1 không có chế độ cộng).
**Nền khung xem** (bản đồ / tối / sáng, cạnh ô phóng to): hiệu ứng sáng nhìn rõ hơn trên nền tối. **?**: bảng phím tắt.

### Nhập sheet ngoài: trình cắt sheet
"+ Thêm hiệu ứng → Nhập sprite sheet" mở **trình cắt sheet** (mở lại cho tầng đang chọn ở Nâng cao → "Mở trình cắt sheet…"):
- **Nền:** tự nhận (trong suốt, magenta, đen kiểu ánh sáng, hoặc **một màu bất kỳ** = trung vị viền ảnh, ví dụ xanh navy);
  "Hút màu" bấm lên nền; "Độ lệch" nới ngưỡng. Màu nền được gỡ khỏi viền mềm (không còn viền navy).
- **Theo hàng (tự tìm):** vạch vàng chia hàng, vạch hồng chia hình trong hàng; kéo được cả hai, bấm đúp lên vạch để xóa,
  bấm đúp chỗ trống để thêm vạch hồng (Shift: vạch vàng); ✕ cạnh mỗi hàng gộp nó với hàng kế. Số hình mỗi hàng nhập tay (cập nhật ngay).
  Số trên ô hình ở panel phải = số khung trong trình cắt. Panel phải kéo rộng / hẹp ở vạch giữa khung xem và panel.
  Mỗi mảng màu thuộc về hình **chứa tâm của nó**, nên đuôi sóng lấn sang cột bên cạnh vẫn đi đúng hình; mảng nằm trong khung
  của mảng lớn (bọt, giọt) tính chung với mảng lớn khi tự chia.
- **Lưới đều:** cột × hàng.
- Bấm một hình để chọn: gộp với hình sau, xóa, đổi thứ tự ◀▶, dịch x/y (mũi tên, Shift = 10 px); kéo trên chỗ trống để vẽ khung.
  Khung đỏ = hình trống (không bị bỏ ngầm).
- **Căn:** đáy-trái / đáy-giữa / giữa / trên-trái; xem trước động với bóng mờ hình trước.
- Recipe: `slice = {boxes: [[x0,y0,x1,y1,dx,dy, sx0,sy0,sx1,sy1]...], align, cellScale}` (px của sheet gốc; ô dài nhất ≤ 512 px),
  `bg: "color"` + `key = {c: [r,g,b], tol}`. Sheet gốc được lưu nguyên, nên mở lại vẫn cắt lại được.

### Nhập nhân vật từ sprite sheet
Trong trình cắt sheet, mục **Dùng làm → Nhân vật (pose)**: chọn nhân vật (mới hoặc đã nhập), tên pose, chiều cao khung trong game
(px @1x = fullhd) và số frame giữ mỗi hình, rồi **Tạo pose nhân vật**. App ghép các hình đã căn thành strip @1x + lưới @2x (đúng
dạng catalog), lưu thành tài liệu `characters/<id>` + asset của artifact; nhân vật hiện trong danh sách với dấu ★, mỗi pose giữ
khung và điểm đặt riêng. Thêm hiệu ứng, Lưu (sheet gộp) và cài vào game như nhân vật có sẵn (game chưa có nhân vật này nên phát
sheet gộp).
- **Lật**: nút Lật ⇋ (phím F), Lật cả hàng, Lật tất cả (sheet vẽ ngược hướng). Lưu trong `slice.flips`.
- **Căn để không giật**: **Tâm thân** (trọng tâm phần thân sau khi bỏ cánh, đuôi mảnh; hợp nhân vật bay, xoay), **Tâm thân + đáy**
  (đi trên đất), **Điểm neo** (bấm "Đặt điểm neo" rồi bấm cùng một điểm, ví dụ ngực, trên từng hình; `slice.anchors`). Mọi cách căn
  dùng chung một bố cục cho xem trước và cắt thật: khung = hợp của các hình đã đặt, dấu + = điểm chung (= chân của nhân vật).
- Tự tìm hàng nhận cả khoảng trống hẹp (từ 1% chiều cao); dải mỏng vẫn được gộp lại.

### Trong game
- `install-pack` cài từng tầng như một hiệu ứng (`fx_<nhân vật>_<pose>_<n>`), thêm một template phát chính animation của
  nhân vật (`fx_lab_pose_<n>`), bảng `FX_LAB_SKILLS` (tầng nào, frame nào), và nạp atlas của nhân vật ở mọi level.
- Skill có sheet gộp (mọi skill có nhân vật, lưu từ bản này): game phát **chính sheet gộp** (`fx_<key>_combo`), nên pose đã chỉnh
  và nhân vật chưa có trong game (Diablo) đều chạy đúng; không cần template pose hay atlas của nhân vật. Sheet gộp nằm trong
  atlas `go_fx_lab` (nạp ở mọi level). Skill cũ không có sheet gộp vẫn phát pose của game + từng tầng.
- Đã kiểm (2026-10-23): Diablo fire breath, frame tuner bỏ 2 hình trước hit (hit 38 -> 34, tầng lửa dời theo), co giãn lửa
  18 -> 27 frame, save() thật (nơi lưu giả lập) -> `install-pack --skill` và cả bản zip -> trong game Diablo phun lửa (cả lật).
  Sheet gộp: khung 232x187, 62 frame (36 hình), 1,5 MB.
- Trong level: **F5** phát skill (pose + hiệu ứng đúng frame) tại chuột, **Ctrl+F5** đổi skill, **Shift** = nhìn sang
  trái; **F7 / F6** như trước cho từng hiệu ứng. `KR_FX_LAB_DEMO=1` phát mọi skill giữa màn hình.
- Đã kiểm (2026-10-22): holy_commander radiant slash + lửa mẫu ở frame hit 26 → trong game lửa phun từ mũi kiếm đúng lúc chém.
- Dùng trong code của hero: tạo entity `fx_..._1` tại `hero.pos` khi animation tới frame `start` (ghi trong
  `out/vfx/_skills/<key>.json`), `flip_x` theo hướng hero.

### Gói (pack) và cách Claude cài
- Gói = `pack.json` (tên, anchor, canvas, từng frame và `alias_of`, vị trí từng hình trong sheet, công thức) + `sheet@2x.png`,
  `sheet@1x.png` (= fullhd), `sheet_ipad.png`. Bản .zip chứa đúng 4 file đó.
- App lưu dự án ở db `projects/<id>`: `{id, title, sheet, recipe, pack: {json, @2x, @1x, ipad}, savedAt}` (các giá trị là asset id).
- Skill lưu ở db `skills/<nhân vật>__<pose>` (`free` khi không chọn nhân vật): `{key, character, pose, anim, pivot, length,
  layers: [{lid, title, sheet, recipe, start, muted, pack: {json, @2x, @1x, ipad}}], savedAt}`; thư viện ở `projects/<id>`.
- Claude cài skill: ArtifactData `get` `skills/<key>` (`out_dir`), Artifact `read` từng asset id trong `layers[].pack`
  (mỗi lần một `path`), rồi `python scripts/fx_studio.py install-pack <thư mục asset> --skill <skills/<key>.json>`.
  Một hiệu ứng lẻ từ `projects/<id>` (bản cũ): `install-pack <thư mục asset> --project <projects/<id>.json>`.
- `install-pack` ghi `out/vfx/<id>/` (`fx.json` có `"pack": true`, `pack/`, `game/` như render) rồi cài như mọi hiệu ứng.
  Hiệu ứng từ app không render lại bằng Python; muốn sửa thì sửa trong app và cài gói mới.
- Đổi app: sửa `tools/fx_studio/app.html`, chạy `python tools/fx_studio/build_artifact.py`, publish `out/fx_studio_artifact/index.html`
  (cùng `bg.png`, `hero.png`, `samples/fire_breath.png`) vào link trên với capabilities `{db: {}, assets: {}, downloads: true}`.

## Bản chạy trên máy (vector, cài thẳng)
| | |
|---|---|
| Trang chỉnh | double-click `tools/fx_studio/fx_studio.bat`, trình duyệt mở `http://127.0.0.1:8768/` (chỉ nghe 127.0.0.1) |
| Dòng lệnh | `python scripts/fx_studio.py --help` |
| Cần | python có numpy, Pillow, scipy, **vtracer**, **resvg-py** (`pip install -r requirements.txt`) |
| Game | `E:\work
everse\games\kr1`; máy khác đặt biến `KR1_GAME_DIR` |

Cùng cách thao tác như app (kéo để đặt vị trí, ↺, trạng thái), thêm: kiểu nét **Vector** (nút *Tạo xem trước vector*),
**Áp dụng vào game** (lưu + render + cài một lần), **Gỡ khỏi game**, **▶ Chơi thử** (mở level 3, mọi hiệu ứng đã cài tự phát
giữa màn hình mỗi 2 giây). Trong game: **F7** phát tại chuột, **Shift+F7** nhìn sang trái, **F6** đổi hiệu ứng.

## Raster hay vector
- **Raster (mặc định, như gốc)**: giữ nguyên nét vẽ và glow mềm của sheet; chỉ bỏ nền, đổi màu, đổi cỡ.
  Với nền đen, alpha = kênh sáng nhất, trừ đi "ngưỡng đen" để bụi JPEG không thành chấm màu trên cỏ.
  Các cụm điểm rời nhỏ hơn 12 px cũng bị bỏ.
- **Vector**:
  - Lõi phẳng (pixel có alpha ≥ "ngưỡng lõi") được gom về một bảng màu chung cho mọi frame, nên màu không nhấp nháy giữa các frame.
  - Lõi được trace bằng vtracer trên ảnh phóng mượt 4x. Glow được vẽ lại, màu lấy từ chính sheet.
  - Nét ra phẳng và sắc hơn gốc, phóng to vẫn nét. File SVG nằm ở `game/svg/`.
  - Render mất khoảng 1 giây mỗi hình.

## Thư mục `out/vfx/<id>/`
```
design/sheet_vNN.png     sheet đã nhập, mọi phiên bản (nhập lại: --force, giữ cài đặt)
fx.json                  công thức: mọi thứ render và install cần (xem đầu scripts/fx_studio.py)
.work/cells/             từng ô đã bỏ nền (cho trang; không vào git)
game/frames/@2x|@1x|ipad/fx_<id>_0001.png ...   @1x = fullhd của game, ipad = @1x x 768/1080
game/manifest.json       size, trim_offset, content, alias_of từng frame (như ref/hero), anchor của game, animation
game/preview.gif         xem nhanh trên map KR, sheet.png: các hình xếp ngang, svg/ (chế độ vector)
```

## Install ghi gì vào game
Mọi thứ đều có đánh dấu `fx_lab`. Repo `reverse` không bị commit, xem bằng `git diff`.
- `src/_assets/kr1-desktop/images/{fullhd,ipad}/go_fx_lab.lua` + `go_fx_lab-N.png`: atlas đúng định dạng KR (`size`, `trim`, `f_quad`,
  `alias`). Hình giữ nhiều frame được ghi một lần, các frame còn lại là alias. Thư mục `_assets` bị git ignore, nên uninstall tự xóa các file này.
- `kr1/data/game_animations.lua`: khối `a.fx_<id> = {prefix, from = 1, to = N}` trước `local o = {}`.
- `kr1/game_templates.lua`: khối cuối file, gồm `RT("fx_<id>", "fx")` với anchor (y tính từ **dưới** lên), z, loop, `timed.runs`, cùng `FX_LAB_LIST`.
- `all/game.lua`: 4 dòng kết thúc bằng `-- fx_lab`, gồm nhóm atlas trong `game.required_textures` và hook update/keypressed.
- `kr1/fx_lab.lua`: phím F6/F7 và chế độ demo (`KR_FX_LAB_DEMO=1`: giữa màn hình, cộng thêm một lần ở 1/4 màn hình, cứ một chu kỳ thì lật một lần).
- Các bản mirror mà viewer và `tools/verify_assets.py` đọc:
  - `data/kr1/data/game_animations.json`;
  - `data/_assets/kr1-desktop/images/{fullhd,ipad}/go_fx_lab.json`;
  - `sprites/fullhd/go_fx_lab/*.png` cùng các mục tương ứng trong `sprites/fullhd/_index.json`.
  Nhờ vậy verify ra đúng như khi chưa cài: `never referenced []`, không frame nào thiếu, không pixel nào lệch.

Dùng hiệu ứng trong code game như mọi fx khác:
```lua
local fx = E:create_entity("fx_fire_breath")
fx.pos.x, fx.pos.y = hero.pos.x, hero.pos.y
fx.render.sprites[1].ts = store.tick_ts
fx.render.sprites[1].flip_x = hero.render.sprites[1].flip_x
queue_insert(store, fx)
```

## Đã kiểm (2026-10-22)
- Sheet mẫu 3x3 lửa trên nền đen: lưới tự nhận 9 ô. Render raster thành 18 frame game (0,6 s); vector thành 4 màu.
- Đã cài vào game, rồi chạy `love.exe src -level 3` với `KR_FX_LAB_DEMO=1` (cả fullhd lẫn `-texture_size ipad`):
  - lửa và băng hiện giữa map; lần đặt ở 1/4 màn hình rơi đúng chỗ;
  - bản lật đối xứng quanh điểm neo;
  - log không có lỗi atlas.
- Cài rồi gỡ thì `git diff` trở về đúng như trước.
- Level 1 crash ở khung hình đầu (`invalid key to 'next'` trong `lib/hump/timer.lua`), kể cả khi chưa cài gì. Lỗi này có từ trước:
  LuaJIT desktop cũng báo lỗi, không chỉ love.js. Đã sửa bằng cách luôn duyệt bản sao (`_SNAPSHOT = true`).
