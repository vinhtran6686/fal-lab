# Fx Studio: sprite sheet hiệu ứng 2D → frame cho Kingdom Rush 1

Đầu vào là **một sprite sheet** của hiệu ứng (lửa, nổ, phép...). Tool cắt từng frame, bỏ nền, chỉnh màu, cỡ, điểm neo và nhịp,
rồi xuất frame đúng định dạng game (giống `ref/hero`). Bước cài sẽ đóng gói vào game KR1 (LÖVE 0.10.2) để xem ngay trong level.
Không gọi model, không tốn phí.

## Chạy

| | |
|---|---|
| Trang chỉnh | double-click `tools/fx_studio/fx_studio.bat`, trình duyệt mở `http://127.0.0.1:8768/` (chỉ nghe 127.0.0.1) |
| Dòng lệnh | `python scripts/fx_studio.py --help` |
| Cần | python có numpy, Pillow, scipy, **vtracer**, **resvg-py** (`pip install -r requirements.txt`) |
| Game | `E:\work\reverse\games\kr1`; máy khác đặt biến `KR1_GAME_DIR` |

## Các bước trên trang
1. **Nhập sheet mới…**: chọn ảnh, đặt mã (id, ví dụ `fire_breath`). Lưới và nền được tự nhận (nền đen, trong suốt hoặc magenta).
   Sheet lệch lưới thì ghi rõ, ví dụ `3x3`.
2. **Xem nhanh**: hiệu ứng chạy 30 fps trên map KR thật, cạnh một hero KR (Ignus) để so cỡ.
   - **Bấm vào hình** để đặt điểm neo: điểm phun của hơi thở, tâm của vụ nổ. Điểm đó nằm đúng vị trí entity trong game (dấu +).
   - **Scale**: px của sheet → px trong game (fullhd).
   - **Màu**: hue, bão hòa, độ sáng, độ đục, có sẵn mẫu Băng, Độc, Hư không, Thánh, Bóng tối.
3. **Frame**:
   - "giữ" = số frame game mỗi hình (2 = vẽ "on twos" như KR).
   - Dùng ◀ ▶ để đổi thứ tự, ✕ để bỏ một hình; có nút Đảo ngược và Ping-pong.
   - Dòng **Thứ tự** (`ô:giữ`, ví dụ `1:2 2:2 3:3 2:2`) cho phép dùng lại một ô.
4. **Render**: xuất `out/vfx/<id>/game/`. Chọn "Bản render" để xem đúng thứ sẽ vào game (kể cả chế độ vector).
5. **Cài vào game**, rồi **Chơi thử trong game**:
   - Nút Chơi thử mở level ở chế độ demo: mọi hiệu ứng đã cài phát giữa màn hình mỗi 2 giây.
   - Chạy bằng `run.bat` thì dùng **F6** để chọn hiệu ứng, **F7** để phát tại chuột, **Shift+F7** để phát bản lật.
   - **Gỡ** xóa hiệu ứng khỏi game. Gỡ cái cuối cùng sẽ xóa mọi dấu vết, các file game trở về đúng từng byte như trước.

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
