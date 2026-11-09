# Tư duy xây dựng lib-fx

File gốc về **tại sao và theo thứ tự nào** lib-fx được xây. Các file khác trả lời "cái gì" và "làm thế nào":

| File | Trả lời |
|---|---|
| **MINDSET.md** (file này) | lib-fx để làm gì, một hiệu ứng đi qua những bước nào, tái tạo và sáng tạo khác nhau ra sao, nó nối với việc thiết kế nhân vật thế nào |
| [GUIDE.md](GUIDE.md) | bản đồ thư mục thư viện (nhóm → họ → hiệu ứng) |
| [README.md](README.md) | luật nhìn, lệnh dựng, cách thêm một hiệu ứng |
| [_core/vector/STATUS.md](_core/vector/STATUS.md) | trạng thái hiện tại của bộ tool vector, việc để dành, câu hỏi mở (đọc đầu tiên khi mở session mới) |

Viết 2026-11-09 theo lời user. Khi tư duy thay đổi, sửa file này trước rồi mới sửa các file khác.

---

## 1. Mục tiêu

**lib-fx là một bộ bách khoa toàn thư về hiệu ứng VFX 2D**, chia theo nhóm. Nó vừa là **kho lưu trữ** (hiệu ứng dùng được cho nhân vật),
vừa là **phòng nghiên cứu** (tái tạo hiệu ứng của người khác để hiểu cách họ vẽ, ghi lại thành luật có số đo).

Ba việc user muốn làm với nó:

1. **Tái tạo và kiểm thử đầy đủ cho từng loại** hiệu ứng: slash, impact, nổ, ... Mỗi loại có vài mẫu gốc được dựng lại tới 9-10/10, và từ đó
   có bộ luật của loại đó.
2. **Phân biệt rõ** phần nào **tái tạo** (dựng lại từ GIF gốc của người khác) và phần nào **sáng tạo** (chúng ta tự làm ra).
3. **Bách khoa toàn thư theo nhóm**: tìm hiệu ứng theo cách dùng trong game ("cần một nhát kiếm nặng", "cần một vụ nổ lửa"), mỗi hiệu ứng
   kèm luật và cách làm của nó.

Mỗi hiệu ứng trong lib phải trả lời được ba câu:

| Câu hỏi | Ghi ở đâu |
|---|---|
| Nó là **loại** gì? (slash, impact, nổ ...: ngôn ngữ hình) | `foundation/vfx/<loại>/`, tag trong `meta.json` |
| Nó **từ đâu ra**? (tái tạo từ GIF nào, hay sáng tạo) | `origin`, `source` trong `meta.json` (xem §4) |
| Nó **dùng ở đâu** trong game? (đòn cận chiến, phép, tháp ...) | thư mục nhóm / họ (`melee/blade` ...), xem [GUIDE.md](GUIDE.md) |

---

## 2. Vòng làm việc: một hiệu ứng đi từ mẫu tới nhân vật

```
                     ┌──────────────────────────── KIẾN THỨC ─────────────────────────────┐
                     │  luật chung (foundation 01-05, DESIGN.md)                          │
                     │  luật theo loại (foundation/vfx/<loại>/)   công thức (RECIPE-*.md) │
                     └──────▲──────────────────────────────▲──────────────────────────────┘
                            │ ghi lại                      │ đọc
 GIF gốc (ref/vfx/) ──► [BƯỚC 0] TÁI TẠO / TẠO MẪU ──► [PHASE 1] MÔ TẢ ──► [PHASE 2] BIÊN ĐỘ ──► [PHASE 3] GẮN VÀO NHÂN VẬT
                        dựng lại 9-10/10            user tả bằng lời     xuất dữ liệu chuyển      khớp pose, nhịp, điểm neo
                        hoặc sinh mẫu từ luật       → tool sinh lại      động → user chỉnh        của một nhân vật cụ thể
                                                                         → tool sinh lại          → asset của nhân vật
```

Mindset của user: **làm ra (hoặc dựng lại) hiệu ứng trước**, rồi **từ kiến thức đó tuỳ biến** theo hướng mình muốn: trước bằng lời,
sau bằng số liệu chuyển động, cuối cùng gắn vào nhân vật.

### Bước 0: tái tạo hoặc tạo mẫu (nền móng)

- **Mục tiêu**: có một hiệu ứng đẹp **và hiểu vì sao nó đẹp**. Tái tạo một GIF gốc tới 9-10/10, hoặc sinh một mẫu mới từ luật đã có.
- **Đầu vào**: GIF gốc trong `ref/vfx/<tên>/` (tái tạo), hoặc luật trong `foundation/` (sáng tạo).
- **Đầu ra**: hiệu ứng dựng lại (frame, SVG, GIF so sánh với gốc), **số đo** (lớp, màu, vòng đời, từng mảnh), **luật** ghi vào
  `foundation/vfx/<loại>/`.
- **Công cụ đã có**:
  - bộ vector `_core/vector/`: `vectorfx.py init | check | all | lifecycle | track | study | showcase` (đọc GIF → path Bézier → số đo);
  - bộ code cũ `_core/fxcore.py`, `fieldfx.py`, `organic.py` + `_tools/study_ref.py` (dựng bằng hình cơ bản, xem `REFERENCE-GIF.md`).
- **Xong khi**: user chấm 9-10/10 **và** luật của loại đó được ghi lại có số đo. Một loại cần 2-3 mẫu gốc thì luật mới đủ tin.
- **Đã làm**: slash (5 mẫu tái tạo + 4 mẫu sáng tạo 9-10/10), nổ / phun (3 mẫu tái tạo 10/10).

### Phase 1: mô tả (user tả bằng lời)

- **Mục tiêu**: một hiệu ứng mới **theo ý user**, dựa trên mẫu đã có, chỉ bằng mô tả.
- **Đầu vào**: lời user ("chém ngang màu xanh", "nét dày hơn", "vòng quanh thân", "chữ C hở trước mặt", "nặng như đại đao"), có khi kèm ảnh
  ý tưởng (chỉ lấy ý, không đồ: `ref/vfx/axe-swing-idea/`).
- **Đầu ra**: hiệu ứng sinh mới + các thông số đã chọn (`design.json`).
- **Công cụ đã có**: bộ sinh slash `vectorfx.py gen-slash NAME --style crescent | loop | loop-heavy | front-heavy`; mỗi kiểu là một dòng
  trong `STYLES` (`_core/vector/gen_slash_loop.py`). Mô tả của user được dịch thành tham số: độ rộng lưỡi, elip (tâm, bán kính, độ dẹt),
  điểm bắt đầu, độ dày theo phối cảnh, số sợi, đầu nét, nhịp (`TIMELINE`), phản chiếu.
- **Xong khi**: user chấm 9-10/10. Mỗi lần chấm, nhận xét được đổi thành **luật** (ví dụ: "nét quá đơn giản" → luật "một nhát chém là
  nhiều sợi"; xem `foundation/vfx/slash/generators.md` §4).
- **Đã làm**: slash đơn (user: "sáng tạo slash đơn bằng tool đã khá ổn", 9-10/10). Chưa làm: loại khác; slash combo 2-3 nhát (đang định thử).

### Phase 2: biên độ (xuất dữ liệu chuyển động → chỉnh → sinh lại)

- **Mục tiêu**: user điều chỉnh hiệu ứng **bằng số liệu**, không chỉ bằng lời: tool xuất "biên độ" của hiệu ứng, user biến đổi nó, tool
  sinh lại ra một hiệu ứng có biên độ mới.
- **"Biên độ" gồm** (đề xuất định nghĩa, các phần đã đo được ở cột phải):

| Thành phần | Ý nghĩa | Đã có |
|---|---|---|
| quỹ đạo | đường đi của hiệu ứng (đường chém, trục phun) | khung toạ độ của bộ sinh (`EllipseFrame`, `PolarFrame`, `LinearFrame`) |
| nhịp | đầu / đuôi nét, độ dày, độ giãn, độ đứt theo từng hình vẽ; frame giữ (on ones / on twos) | `TIMELINE` của bộ sinh; `vectorfx.py lifecycle` (đọc từ GIF) |
| đường cong diện tích | to dần → đỉnh → co (A(t)), khung bao theo frame | `lifecycle` → `foundation/data/lifecycle_*.json` |
| từng mảnh | mảnh nào lớn, tách, co, trôi, chết khi nào | `vectorfx.py track` → `tracking_*.json` |
| hình | độ dày dọc nét, phối cảnh (`wknots`), đầu nét, răng khía | tham số nét trong `design.json` |
| ánh sáng | glow theo frame (`gain`), độ đục lớp | profile / `design.json` |

- **Phép biến đổi user muốn** (ví dụ): kéo dài / thu ngắn quỹ đạo, xoay, đổi độ cong; nhanh / chậm (đổi nhịp, thêm frame giữ ở va chạm);
  to / nhỏ hơn ở đỉnh; tàn lâu hơn; dày hơn ở phía trước ...
- **Còn thiếu**: (1) một **định dạng chung** cho biên độ (một file JSON đọc được, chỉnh được bằng tay hoặc bằng một trang kéo thả);
  (2) **bộ sinh đọc ngược** từ file biên độ (hiện mỗi bộ sinh giữ biên độ trong code: `TIMELINE`, `STYLES`); (3) chuyển một bản **tái tạo**
  (khớp từng frame độc lập) sang dạng tham số để chỉnh được như bản sinh; (4) khung theo đường cong bất kỳ (`PathFrame`, xem STATUS §3.1).
- **Xong khi**: user đổi một số trong file biên độ, chạy lại, được hiệu ứng mới đúng ý mà không cần mô tả lại bằng lời.

### Phase 3: gắn vào một nhân vật cụ thể

- **Mục tiêu**: hiệu ứng có biên độ user muốn được **khớp với nhân vật**: đúng pose, đúng quỹ đạo vũ khí, đúng nhịp clip attack, đúng
  điểm neo, rồi trở thành asset của nhân vật.
- **Đầu vào**: hiệu ứng (từ lib) + clip / frame của nhân vật (`out/heroes/<id>/frames/<sheet>/`) + quỹ đạo user vẽ hoặc đánh dấu mũi vũ khí.
- **Đầu ra**: lớp fx của nhân vật trong `out/heroes/<id>/source/vfx/` (gốc) và `frames/fx/<tên>/` (cắt), ghép lên sprite.
- **Công cụ đã có**: `scripts/fx_layers.py` (công thức nhiều lớp phẳng neo ở chân, đơn vị = chiều cao thân H, thời gian theo sheet thân);
  `tools/frame_tuner/` (chỉnh frame, xuất); quy ước asset trong `.claude/skills/fal-image/format.md` §4.
- **Còn thiếu**: lấy quỹ đạo và nhịp từ clip attack; xuất bản vector theo chuẩn lib-fx (nền trong suốt, @2x, `sheet.png`, `meta.json`)
  để `fx_layers.py` hoặc game dùng. Đánh giá khả thi: STATUS §3.1 (làm được, thiếu 3 mảnh nhỏ).
- **Xong khi**: user xem nhân vật đánh kèm hiệu ứng (playtest) và duyệt.

---

## 3. Ba tầng kiến thức

| Tầng | Chứa | Ở đâu |
|---|---|---|
| Luật chung (mọi loại) | ba nhịp báo trước → bùng → tan; nhiều lớp; nét mịn; cấp bậc màu; vòng đời và từng mảnh; ánh sáng theo thời gian; cách đọc bản gốc | `_core/vector/foundation/01-05`, [DESIGN.md](DESIGN.md), [SHAPE-RULES.md](SHAPE-RULES.md) |
| Luật theo loại | slash: sinh từ đầu nét, nhiều sợi, giãn rồi đứt, glow giữ tới cuối, phản chiếu ...; nổ: sinh ở chân, lưỡi xoè, tàn tại chỗ ... | `_core/vector/foundation/vfx/<loại>/` |
| Công thức từng hiệu ứng | cách làm một hiệu ứng cụ thể, lệnh, tham số | `RECIPE-*.md`, `foundation/vfx/slash/generators.md`, `profiles/*.json` |

Luật nào cũng phải có **số đo** hoặc **lần user chấm** đứng sau. Nhận xét của user là dữ liệu: mỗi lần chấm được ghi lại cùng luật rút ra.

---

## 4. Tái tạo và sáng tạo

| | **Tái tạo** (rebuild) | **Sáng tạo** (original) |
|---|---|---|
| Là gì | dựng lại một GIF của người khác càng giống càng tốt | hiệu ứng mới: từ luật, từ mô tả của user, hoặc vẽ bằng code từ đầu |
| Để làm gì | **học**: đo lớp, màu, vòng đời, cách vẽ; kiểm chứng bộ tool | **dùng**: asset cho nhân vật, game |
| Được đưa vào game? | **không** (art gốc thuộc người khác); chỉ dùng để học, ghi nguồn | **có** |
| Ảnh ý tưởng | GIF gốc là mục tiêu, so từng frame | ảnh ý tưởng chỉ để lấy ý; không đồ, không so từng frame |
| Đánh giá | so với gốc (IoU, điểm gãy) + user chấm | user chấm + kiểm tra trong khoảng luật đã đo |

Hai cách làm (dùng cho cả tái tạo lẫn sáng tạo):

- **`fxcore` (procedural)**: hình cơ bản, trường nhiệt cắt tầng, hình tự do (`_core/fxcore.py`, `fieldfx.py`, `organic.py`), dựng bằng
  `build.py`. Các hiệu ứng trong `force/`, `impact/`, `magic/`, `melee/blade/`.
- **`vector`**: path Bézier đo từ GIF hoặc sinh từ luật (`_core/vector/`), dựng bằng `_tools/vectorfx.py`.

**Phân loại các hiệu ứng hiện có:**

| Hiệu ứng | Nguồn gốc | Cách làm | Gốc / ý tưởng | Đang nằm ở | User |
|---|---|---|---|---|---|
| `melee/blade/swirl_fire`, `swirl_frost` | tái tạo | fxcore (trường nhiệt) | `ref/vfx/swirl-slash/` | thư viện | draft (bản vector đẹp hơn) |
| xoáy chém lửa, băng | tái tạo | vector | `ref/vfx/swirl-slash/` | `_core/vector/showcase/swirl-slash/` | 9, 9-10/10 |
| slash-trio xanh, hồng, vàng + phản chiếu | tái tạo | vector | `ref/vfx/slash-trio/` | `_core/vector/showcase/slash-trio/` | đạt |
| lửa phun, Arcane, Toxic | tái tạo | vector | `ref/vfx/element-trio/` | `_core/vector/showcase/element-trio/` | 10/10 |
| `gen-slash-blue` (lưỡi liềm) | sáng tạo | vector (bộ sinh) | luật slash | `_core/vector/showcase/generated/` | 7/10 |
| `gen-slash-loop-blue`, `-loop-heavy-blue`, `-front-heavy-blue` | sáng tạo | vector (bộ sinh) | luật slash + ý `ref/vfx/axe-swing-idea/` | `_core/vector/showcase/generated/` | 9-10/10 |
| `gen-slash-combo-blue` (quét ngang + bổ xuống) | sáng tạo | vector (bộ sinh, 2 khung) | luật slash + ý `ref/vfx/spear-combo-idea/` | `_core/vector/showcase/generated/` | chưa chấm |
| `force/shock/*` (inferno ...) | sáng tạo | fxcore | — | thư viện | inferno approved, còn lại draft |
| `impact/hit|dash|ground/*` | sáng tạo | fxcore (organic) | — | thư viện | draft |
| `magic/spirit/soulstrike` | sáng tạo | fxcore | — | thư viện | rework (linh hồn nhỏ đạt) |
| `life/dash/tiger` | sáng tạo | fxcore | — | **đã xoá 2026-11-09** | rework |

Vấn đề hiện tại (user hỏi 2026-11-09 "có dễ đọc phần nào tái tạo, phần nào sáng tạo không?"): **chưa**. Bản vector (cả tái tạo lẫn
sáng tạo) nằm trong `_core/` (thư mục code), không có trong thư viện, catalog hay gallery; `melee/blade/swirl_*` là tái tạo nhưng nằm
lẫn với hiệu ứng sáng tạo. Hướng sửa: §6.

---

## 5. Hai trục phân loại

- **Nhóm thư viện = cách dùng trong game** (thư mục): `melee`, `ranged`, `force`, `element`, `magic`, `explosion`, `impact`, `status`,
  `life`, `ui`, `environment` ([GUIDE.md](GUIDE.md)).
- **Loại hình = ngôn ngữ hình** (kiến thức): slash, impact (va chạm), explosion (nổ / phun), sau này: projectile, aura, beam, ...
  (`_core/vector/foundation/vfx/<loại>/`).

Hai trục không trùng nhau: một **loại** dùng ở nhiều **nhóm** (slash có ở `melee/blade`, `melee/polearm`, `magic/*` khi là chém phép;
nổ có ở `explosion/blast`, `element/fire/impact`, `ranged/siege`). Vì vậy: **kiến thức** xếp theo loại, **hiệu ứng dùng được** xếp theo nhóm,
`meta.json` của mỗi hiệu ứng ghi cả hai (`tags` có loại).

| Loại | Nhóm dùng nhiều | Kiến thức | Mẫu tái tạo | Mẫu sáng tạo |
|---|---|---|---|---|
| slash | `melee/blade`, `melee/polearm`, `melee/beast`, `magic/*` | [foundation/vfx/slash](_core/vector/foundation/vfx/slash/README.md) | 5 | 4 (vector) |
| explosion | `explosion/*`, `element/*/impact`, `ranged/siege` | [foundation/vfx/explosion](_core/vector/foundation/vfx/explosion/README.md) | 3 | 0 (vector); `force/shock/*` (fxcore) gần với loại này |
| impact | `impact/*`, mọi đòn đánh trúng | [RESEARCH-organic-impact.md](RESEARCH-organic-impact.md) (chưa có thư mục loại) | 0 | 10 (fxcore) |

---

## 6. Bản đồ thư mục

### 6.1 Bên trong `lib-fx/` (hiện tại)

| Thư mục / file | Vai trò | Thuộc bước |
|---|---|---|
| `<nhóm>/<họ>/<id>/` | thư viện: hiệu ứng fxcore (`sheet.png`, `frames/`, `preview.gif`, `meta.json`), code của họ cạnh đó | 0, 1 (đầu ra dùng được) |
| `_core/fxcore.py`, `fieldfx.py`, `organic.py`, `palettes.py` | bộ vẽ procedural | 0, 1 |
| `_core/vector/` | bộ vector: đọc GIF → path, đo, bộ sinh, phản chiếu | 0, 1, 2 |
| `_core/vector/profiles/` | mỗi bản tái tạo một profile JSON | 0 |
| `_core/vector/showcase/` | kết quả vector trong git (tái tạo + `generated/` sáng tạo) | 0, 1 |
| `_core/vector/foundation/` | luật chung (01-05) + `vfx/<loại>/` + `data/` số đo | kiến thức |
| `_core/vector/STATUS.md` | trạng thái, việc để dành, câu hỏi mở | điểm nối các session |
| `_tools/vectorfx.py`, `_tools/study_ref.py` | dòng lệnh | 0, 1 |
| `_gallery/`, `catalog.json`, `build.py` | xem nhanh, danh mục, dựng thư viện fxcore | thư viện |
| `_study/` | file trung gian (git bỏ qua) | mọi bước |
| `research/bezier-shapes/` | nghiên cứu path Bézier (đã lưu trữ, sinh ra `_core/vector`) | lịch sử |
| `DESIGN.md`, `SHAPE-RULES.md`, `REFERENCE-GIF.md`, `RESEARCH-organic-impact.md`, `RECIPE-*.md` | phương pháp, luật, công thức (bộ fxcore) | kiến thức |

### 6.2 Thư mục anh em trong repo (luồng thiết kế nhân vật)

```
Ý tưởng nhân vật
  └─► .claude/skills/fal-image/       ảnh tĩnh: master (side), front/back cho quái, icon; luật trong format.md, classes/<lớp>.md
        └─► out/heroes/<id>/source/design/        ảnh đã duyệt
  └─► .claude/skills/video-sprite/    mọi animation (run, attack, skill, death) từ ảnh tĩnh: clip → frame → sheet
        └─► out/heroes/<id>/source/video/         clip đã duyệt
        └─► out/heroes/<id>/frames/<sheet>/        sheet đã cắt (một khung, một cỡ thân cho mọi động tác; meta.json)
  └─► lib-fx/  (THƯ VIỆN FX, độc lập với nhân vật)  ◄── ref/vfx/ (GIF gốc, ảnh ý tưởng)
        └─► Phase 3: gắn vào nhân vật
              scripts/fx_layers.py            công thức lớp fx neo ở chân (đơn vị H, thời gian theo sheet thân)
              out/heroes/<id>/source/fx/      code / công thức fx của nhân vật (vd. diablo: fire_breath.py, levelup_glow.py)
              out/heroes/<id>/source/vfx/     fx gốc của nhân vật (vd. surya: whirlwind_kick/)
              out/heroes/<id>/frames/fx/<tên>/ fx đã cắt, ghép lên sprite
              tools/frame_tuner/              chỉnh frame, xem trước, xuất
              .claude/skills/video-sprite/playtest/   xem nhân vật đánh kèm fx (Sprite Playtest, Motion Lab)
```

| Thư mục | Chứa | Liên quan tới lib-fx |
|---|---|---|
| `ref/vfx/` | GIF gốc để tái tạo (`swirl-slash`, `slash-trio`, `element-trio`), ảnh ý tưởng (`axe-swing-idea`) | đầu vào Bước 0 |
| `ref/sprite/` | sprite tham khảo cho dáng và chuyển động (`slash`, `uppercut`) | quỹ đạo vũ khí để học (Phase 3) |
| `ref/hero/`, `ref/assets/` | asset tham khảo của game mẫu | khung, cỡ nhân vật |
| `.claude/skills/fal-image/` | thiết kế ảnh tĩnh nhân vật | nhân vật mà fx sẽ gắn vào |
| `.claude/skills/video-sprite/` | animation nhân vật, playtest | nhịp, pose, clip attack cho Phase 3 |
| `out/heroes/<id>/` | asset từng nhân vật (`brief.md` có bảng Asset manifest: mọi still, clip, vfx cần có) | nơi Phase 3 ghi ra |
| `scripts/fx_layers.py` | fx nhiều lớp phẳng neo ở chân nhân vật | công cụ Phase 3 hiện có |
| `docs/` | `python-fx-recipe.md` (fx vẽ bằng Python lên clip), `reference-video-motion.md` (lấy chuyển động từ sprite khác), `asset-manifest.md` | cách làm fx gắn nhân vật trước khi có lib-fx |
| `tools/frame_tuner/` | chỉnh và xuất frame | Phase 3 |

### 6.3 Cấu trúc đích (đề xuất 2026-11-09, **chờ user duyệt, chưa di chuyển gì**)

```
lib-fx/
  MINDSET.md, README.md, GUIDE.md      tư duy, luật + lệnh, bản đồ
  <nhóm>/<họ>/<id>/                    THƯ VIỆN: chỉ hiệu ứng dùng được (sáng tạo: fxcore + vector)
                                       meta.json: origin = original, method = fxcore | vector, tags có loại hình
                                       vd. melee/blade/spin-blue, spin-heavy-blue, front-heavy-blue
  _rebuild/<loại>/<tên>/               TÁI TẠO (học, không đưa vào game): so sánh với gốc, frame, SVG, link profile + ref
                                       vd. _rebuild/slash/swirl-slash, _rebuild/slash/slash-trio, _rebuild/explosion/element-trio
  _core/                               CHỈ code: fxcore ..., vector/ (cả profiles, bộ sinh)
  docs/                                KIẾN THỨC gom một chỗ: foundation/ (chung), vfx/<loại>/, recipes/, research/
  _gallery/  _tools/  _study/          giữ nguyên
```

Nhìn tên là biết: thư mục thường = **dùng được**; `_rebuild/` = **tái tạo**; `docs/` = **đọc để hiểu**. Gallery và catalog lọc được theo
`origin`. Việc phải làm khi duyệt: xuất bản vector sang chuẩn lib-fx (nền trong suốt, @2x, `sheet.png`, `meta.json`); chuyển
`showcase/` và `foundation/`; sửa đường dẫn trong code, `CLAUDE.md`, docs (kiểm tra link tự động); quyết số phận `melee/blade/swirl_*`
(chuyển sang `_rebuild/` hay xoá vì bản vector đẹp hơn).

---

## 7. Trạng thái theo loại (2026-11-09)

| Loại | Bước 0 tái tạo | Bước 0 / Phase 1 sáng tạo | Phase 2 biên độ | Phase 3 nhân vật |
|---|---|---|---|---|
| slash | ✅ 5 mẫu | ✅ 4 kiểu (9-10/10 cho 3 kiểu loop / front) | ⏳ dữ liệu có (`TIMELINE`, `lifecycle`), chưa có file biên độ chung | ❌ (khả thi, STATUS §3.1) |
| slash combo (2-3 nhát) | ❌ | ⏳ bản đầu 2 nhát (quét + bổ), chờ chấm | ❌ | ❌ |
| explosion (nổ / phun) | ✅ 3 mẫu | ❌ chưa có bộ sinh | ⏳ `lifecycle`, `track` có | ❌ |
| impact | ❌ chưa tái tạo mẫu nào | ✅ 10 bản fxcore (draft) | ❌ | ❌ |
| force / shock | ❌ | ✅ 6 bản fxcore (inferno approved) | ❌ | ❌ |

---

## 8. Quy ước khi làm tiếp

1. Hiệu ứng **loại mới**: gom 2-3 GIF gốc vào `ref/vfx/<tên>/` → tái tạo bằng vector (`vectorfx.py init` → `all`) tới 9-10/10 →
   `lifecycle`, `track`, `study` → viết `foundation/vfx/<loại>/README.md` → rồi mới viết bộ sinh.
2. Mỗi lần user chấm: ghi điểm + nhận xét + luật rút ra vào file của loại đó; cập nhật `STATUS.md` và `CHANGELOG.md`.
3. Bản **tái tạo** luôn ghi nguồn (file GIF, tác giả nếu biết) và không đưa vào thư viện dùng được.
4. Bản **sáng tạo** từ ảnh ý tưởng: chỉ lấy ý (vị trí, phong cách), không đồ lại.
5. Một hiệu ứng = một thư mục, không kèm nhân vật; màu là bảng màu, không nhân bản hiệu ứng để đổi màu.
6. Không đổi cấu trúc thư mục khi user chưa duyệt (§6.3).
