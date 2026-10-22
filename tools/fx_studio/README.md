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
