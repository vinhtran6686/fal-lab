# Bàn giao: Fx Studio (cập nhật 2026-10-24)

Tài liệu cho người làm tiếp Fx Studio (người hoặc một phiên Claude mới): tool làm ra những gì, file nằm đâu, đã kiểm
những gì, còn dở gì. Hướng dẫn dùng chi tiết nằm ở [tools/fx_studio/README.md](../tools/fx_studio/README.md).

## 1. Mục tiêu

Xuất được **bộ asset hiệu ứng mà game dùng được** cho Kingdom Rush 1 (bản dựng lại trên LÖVE 0.10.2 ở
`E:\work\reverse\games\kr1`, repo `kr-remake`), không chỉ là ghép hiệu ứng để xem:

- chọn nhân vật + pose, xếp nhiều tầng hiệu ứng trên timeline đúng frame của skill;
- xuất từng tầng thành frame game (@2x, @1x = fullhd, ipad) + thời điểm, một sheet gộp, và code Lua gọi chúng;
- cài vào game và phát thử ngay trong level.

## 2. Thành phần

| Phần | Đường dẫn | Vai trò |
|---|---|---|
| App (cách dùng chính) | https://claude.ai/artifact/JUVk6cDVriDXhLXLTTQzVi, nguồn `tools/fx_studio/app.html` | Studio chạy trên trình duyệt: timeline, frame tuner, chỉnh tầng, Lưu, Tải gói .zip |
| Đóng gói app | `tools/fx_studio/build_artifact.py` | Dựng `out/fx_studio_artifact/` (app + danh mục nhân vật + mẫu) để publish |
| Thư viện mẫu | `tools/fx_studio/build_samples.py` | 10 hiệu ứng mẫu vẽ bằng `scripts/fx_layers.py` (nổ, sét, cột sáng, hồi máu, băng, độc, chém, sóng, lên cấp, tia trúng) |
| Engine | `scripts/fx_studio.py` | Import/render sheet (bản cũ), `install-pack` (cài gói từ app), `install`/`uninstall`, ghi vào game |
| Bản chạy trên máy | `tools/fx_studio/fx_studio.bat`, `index.html`, `serve.py` | Bản cũ có server Python: vector (vtracer), cài thẳng; không có timeline |
| Phía game | `kr-remake/games/kr1/src/`: `kr1/fx_lab.lua`, `kr1/fx_lab_skills.lua`, các khối `-- fx_lab` trong `kr1/game_templates.lua`, `kr1/data/game_animations.lua`, `all/game.lua`; atlas `go_fx_lab` | Sinh tự động bởi `install`; không sửa tay |

## 3. Luồng làm việc

1. **App:** chọn Nhân vật → Pose (hoặc "Không có" để làm hiệu ứng tự do).
2. **+ Thêm hiệu ứng:** nhập sprite sheet, lửa mẫu, một trong 10 mẫu Python, hoặc lấy từ thư viện.
3. **Chỉnh:**
   - kéo hiệu ứng trên khung xem so với chân nhân vật; kéo tầng trên timeline (hít vào frame hit), kéo mép để co giãn;
   - màu, tốc độ (Nhanh/Chuẩn/Chậm hoặc nhập số), chuyển động (mờ, đổi cỡ, trôi, ghim vị trí theo frame), vị trí đặt
     (ở nhân vật / ở mục tiêu / bay tới mục tiêu);
   - **Frame tuner** (chuột phải / ⋯ trên tầng nhân vật): giữ/bỏ frame của pose, số giữ, frame hit;
   - Ctrl+Z / Ctrl+Y hoàn tác; chip ✓/⚠/⛔ trên thanh trên kiểm tra trước khi xuất.
4. **Lưu:** app lưu skill vào db của artifact (`skills/<nhân vật>__<pose>`) cùng ảnh và gói frame (assets).
5. **Cài:** nhắn Claude "cài skill `<key>` từ Fx Studio", hoặc Tải gói .zip rồi
   `python scripts/fx_studio.py install-pack <key>.fxskill.zip`. Đường Claude dùng:
   - ArtifactData `get` `skills/<key>` (`out_dir`);
   - Artifact `read` từng asset id trong `layers[].pack` và `combo.pack` (mỗi lần một `path`);
   - `python scripts/fx_studio.py install-pack <thư mục asset> --skill <skills/<key>.json>`.
6. **Thử trong game:** `run.bat -level 3` rồi **F5** (phát skill tại chuột, Shift lật, Ctrl+F5 đổi skill), F7/F6 cho từng
   hiệu ứng; `KR_FX_LAB_DEMO=1` tự phát mọi skill.

## 4. Kết quả xuất ra

**Bộ asset của skill:** `out/<class>/<id>/skills/<pose>/` (khi skill có nhân vật trong `out/`):

| File | Nội dung |
|---|---|
| `layers/<fx_name>/` | mỗi tầng: `frames/@2x`, `frames/@1x`, `frames/ipad`, `manifest.json` (size, trim, alias, anchor) |
| `combo/` | sheet gộp: nhân vật + mọi tầng ở nhân vật, từng frame game, neo ở chân |
| `skill.json` | thời điểm từng tầng (frame), frame hit, độ dài, pose đã chỉnh hay chưa, cách dùng |
| `skill.lua` | hàm Lua cho script hero: gọi từng tầng đúng frame bằng `U.y_wait(store, fts(n))` |

Thêm `meta.json["skills"][<pose>]`, và dòng `fx_<skill>` trong Asset manifest của `brief.md`:
- dòng đang chờ (⏸ ⏳ ❌) được cập nhật;
- dòng đã ✅ từ pipeline khác không bị đụng, Fx Studio thêm dòng riêng `fx_<skill> (Fx Studio)`.

**Kho của engine:** `out/vfx/<id>/` cho từng hiệu ứng đã cài (fx.json, `game/`, `pack/`), `out/vfx/_skills/<key>.json`.

**Trong game:**
- skill có pose gốc của game (Holy Commander) phát animation của game + hàm trong `fx_lab_skills.lua`;
- skill có pose đã chỉnh hoặc nhân vật chưa có trong game (Diablo) phát sheet gộp.

## 5. Trạng thái theo giai đoạn

| Giai đoạn | Nội dung | Trạng thái |
|---|---|---|
| 1 | Bộ asset đúng chỗ + manifest, @2x thật, code skill chạy được, kiểm tra trước khi xuất, hoàn tác/làm lại | ✅ xong, đã kiểm (headless + trong game), đã publish |
| 2 | 10 hiệu ứng mẫu Python trong menu "+ Thêm hiệu ứng" | ✅ xong, đã kiểm (mọi mẫu cắt đủ hình), đã publish (bản 7) |
| 3a | Chuyển động: mờ vào/ra, cỡ đầu→cuối, trôi, ghim vị trí theo frame; vị trí đặt ở mục tiêu / bay tới mục tiêu (xem trước, kéo dấu mục tiêu) | ✅ xong, đã thử headless (gói "motion" 24 frame), đã publish (bản 8) |
| 3b | Phía game cho tầng "ở mục tiêu" và "bay tới mục tiêu" | ✅ xong (2026-10-24): `skill_lua` nhận `target` / `external_only`, tầng bay do `fly()` (runner) di chuyển; đã thấy trong game: vệt chém bay từ nhân vật tới mục tiêu, cả khi lật; tia trúng ở mục tiêu |

## 6. Đã kiểm / chưa kiểm

**Đã kiểm:**
- Chrome headless dùng hàm `save()` thật của app (nơi lưu giả lập): frame tuner, co giãn tầng, hoàn tác, mẫu, chuyển động, sheet gộp.
- `install-pack` theo cả đường `--skill` lẫn file zip.
- Trong game: Holy Commander chém + lửa đúng frame hit, qua đúng hàm `fx_lab_skills.lua`; Diablo phun lửa từ sheet gộp,
  cả khi lật; level 1 chạy được sau bản sửa timer.
- Renderer của app so với Python: lệch trung bình khoảng 1/255, khung cắt lệch tối đa 1 px.
- **Lưu thật trong artifact:** người dùng đã lưu `diablo__skill_fire_breath_side` (2026-10-22 23:55, bản app trước khi
  có sheet gộp), nên upload ảnh, gói và ghi db hoạt động thật.

**Chưa kiểm trong artifact thật:**
- Mở lại skill đã lưu sau khi tải lại trang.
- **Tải gói .zip** (capability downloads).
- Bản app có sheet gộp và chuyển động.

## 7. Việc còn dở (làm tiếp theo thứ tự)

1. `skill.lua` dùng độc lập được: `fly()` tự đăng ký entity `fx_lab_runner` nếu chưa có. Script hero muốn dùng mục tiêu
   thật thì gọi `FXS.<key>(this, store, nil, target_entity)`.
2. Người dùng mở lại skill thật `diablo__skill_fire_breath_side` (lưu bằng app cũ, chưa có sheet gộp) và bấm **Lưu** lại;
   `install-pack --skill` chặn bản cũ này với lời nhắn rõ ràng. Bản app mới đã mở thử được bản ghi này (headless).
   Lửa trong bản đó bắt đầu ở frame 41, hit là 38 (chip kiểm tra báo). Sau đó: thử Tải gói .zip, nhắn "cài skill …".
   Hiện trong game và `out/vfx`, cả hai skill Holy Commander và Diablo là **dữ liệu test** của Claude, không phải bản người dùng lưu.
3. Dọn hiệu ứng thử trong game:
   - còn cài: `fire_breath_test`, `ice_breath_test`, `fire_breath`, `holy_commander_radiant_slash_1/_2/_3`, `diablo_fire_breath_1/_2`, các combo thử;
   - lệnh: `python scripts/fx_studio.py uninstall <id> …` hoặc `--all`;
   - cài lại skill thật của người dùng từ db.
4. Thư viện trong app: thêm cùng một sheet hai lần tạo hai mục (`lua_mau`, `lua_mau_2`); nên gộp theo nội dung ảnh.

## 8. Lưu ý về repo

- **fal-lab:** nhánh `main`.
- **kr-remake:**
  - `feature/hero-holy-commander` đã gộp vào `master` (`d56f747d`: hero Holy Commander, port web love.js, fx_lab), và hai
    nhánh giờ bằng nhau.
  - `E:\work\reverse` ở nhánh feature; `master` đang checkout ở worktree `E:\work\reverse-master-kr4` (có thay đổi chưa
    commit của phần kr4, `master` local ở đó còn chậm: stash rồi pull).
  - Stash "fx_lab wip before ff to master" ở `E:\work\reverse` không còn cần, có thể drop.
  - **Đừng `git stash -u`** trong repo game: nó cất luôn `_assets/.../go_fx_lab.lua` (file sinh ra).
  - Mất các file đó thì chạy lại `python -c "import sys; sys.path.insert(0,'scripts'); import fx_studio as fx; fx.do_install([], fx.GAME_DIR, True)"`.
- **Atlas game:**
  - `src/_assets` bị git ignore: atlas `go_fx_lab-*.png` / `.lua` không có trong git, clone mới phải chạy lại install.
  - `go_fx_lab` và atlas của nhân vật có skill dùng pose game (`go_hero_holy_commander`) được nạp ở **mọi level**.
  - Với texture ipad, `go_hero_holy_commander` báo "atlas file not found", vì hero này chỉ có bản fullhd.
- **Sửa ngoài phạm vi:** `lib/hump/timer.lua` luôn duyệt bản sao (snapshot), vì level 1 crash trên desktop. Uninstall không hoàn tác bản sửa này.
- **Diablo:**
  - 6 pose đã cắt từ clip có sẵn.
  - `respawn_side` lệch cỡ 10–18% ở frame 15–33, do video tự zoom.
  - `skill_fire_breath_side` chưa chốt chính thức; `ember_armor` chưa cắt.
- **Python:** máy này dùng `python` 3.13. Cần `vtracer`, `resvg-py` (chỉ cho bản vector chạy trên máy), `websockets`
  (để test headless qua Chrome DevTools).

## 9. Lệnh hay dùng

```
python tools/fx_studio/build_artifact.py                 # dựng bản app để publish (gồm mẫu + danh mục nhân vật)
python tools/fx_studio/build_samples.py                  # chỉ dựng lại 10 mẫu
python scripts/fx_studio.py install-pack <key>.fxskill.zip
python scripts/fx_studio.py install-pack <assets dir> --skill <skills/<key>.json>
python scripts/fx_studio.py list
python scripts/fx_studio.py uninstall <id> ... | --all
python scripts/asset_status.py <nhân vật>
cd E:\work\reverse\games\kr1 && run.bat -level 3            # F5 skill, F7 hiệu ứng
```

Test headless của app (ví dụ trong lịch sử phiên làm việc):
- dựng `out/fx_studio_artifact/`, chép ra thư mục tạm, chèn `<meta charset="utf-8">` vào đầu `index.html`;
- chạy `python -m http.server`, rồi điều khiển Chrome headless qua DevTools protocol (thư viện `websockets`);
- thay `db` / `assets` bằng bản giả ghi lại dữ liệu, rồi gọi `save()` thật.
