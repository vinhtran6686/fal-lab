# Hướng dẫn thư viện lib-fx

Thư viện hiệu ứng (fx) chuẩn của dự án, dùng chung cho mọi nhân vật. Mỗi hiệu ứng vẽ bằng code (0 USD) và lưu **riêng lẻ, không kèm nhân vật**.
Tư duy chung (lib-fx để làm gì, tái tạo và sáng tạo, các bước tới nhân vật): `MINDSET.md`. File này mô tả từng thư mục chứa gì. Luật nhìn, lệnh dựng và cách thêm hiệu ứng nằm trong `README.md`; phương pháp thiết kế trong `lib-fx/_core/formulas/draw/DESIGN.md`; cách sinh hình tự do (gai, toé, khói) trong `lib-fx/_core/formulas/draw/RESEARCH-organic-impact.md`; công thức hiệu ứng nhiều lớp: `lib-fx/_core/formulas/draw/recipes/RECIPE-inferno.md` (đã duyệt), `lib-fx/_core/formulas/draw/recipes/RECIPE-soul-spirits.md` (linh hồn nhỏ, đạt); dựng lại từ GIF tham khảo: `lib-fx/_core/formulas/rules/REFERENCE-GIF.md` + `_tools/study_ref.py`.

## Cách chia

- **Thư mục = nhóm chủ đề → họ hiệu ứng** (cách designer tìm đồ: "cần một đòn kiếm", "cần một phép lửa").
- **Nguyên tố và trường phái phép chia tiếp theo chức năng chuẩn**: `cast`, `projectile`, `impact`, `aoe`, `aura`, `status`.
- **Các trục khác là tag** trong `meta.json` / `catalog.json` (nguyên tố, chức năng, nặng/nhẹ, lặp hay một lần, kiểu neo), để tìm chéo.
- **Màu không tạo thư mục mới**: cùng một hiệu ứng đổi bảng màu (`_core/palettes.py`) thành bản lửa, băng, thánh...
- **Id = đường dẫn**: `force/shock/tiers`. Tên thư mục tiếng Anh, tên tiếng Việt trong catalog.
- **Trạng thái mỗi hiệu ứng**: `draft` (mới làm), `approved` (đã duyệt), `rework` (cần làm lại). Gallery hiện trạng thái này.

Liên hệ với game thủ thành: tháp cung → `ranged/bow`, tháp phép → `element` / `magic`, lính → `melee`, tháp pháo → `ranged/siege` + `explosion`, hero → mọi nhóm.

## Thư mục hệ thống

| Thư mục | Chứa gì |
|---|---|
| `_core/` | Bộ vẽ dùng chung, không chứa hiệu ứng. `fxcore.py`: canvas siêu mẫu, hình cơ bản (lưỡi liềm, dải, thấu kính, ribbon, lấp lánh), easing, quầng sáng. `palettes.py`: 16 bảng màu chuẩn (sun, fire, ice, water, lightning, earth, wind, nature, poison, holy, shadow, arcane, blood, spirit, blaze, frost). `fxcore.glow_under`: quầng sáng nhiều cỡ chỉ từ một lớp. `fieldfx.py`: trường nhiệt cắt tầng màu phẳng, quầng bậc thang (luật: `lib-fx/_core/formulas/draw/SHAPE-RULES.md`). `organic.py`: hình tự do (gai, giọt, khối méo, lưỡi lửa chữ S `flame`, viền spline), tô theo khoảng cách tới mép, khói toon (`cloud`, `shade`). |
| `_gallery/` | Ảnh xem trước sinh tự động, mỗi họ một cặp: `<nhóm>-<họ>.png` (mọi hiệu ứng, frame cách 1) và `.gif` (chạy cùng lúc, đúng tốc độ). |
| `catalog.json` | Danh mục toàn bộ hiệu ứng: tên, trạng thái, tag, mô tả, fps, số frame, cỡ, điểm neo, thư mục. |
| `build.py` | Dựng lại asset và gallery: `python lib-fx/build.py [nhóm[/họ[/id]]]`. |

## Bên trong một họ

```
force/shock/
  shock.py        code mọi hiệu ứng của họ này (CATALOG: tên, mô tả, trạng thái, tag)
  tiers/          một hiệu ứng: sheet.png (1 hàng, nền trong suốt), frames/, preview.gif, meta.json
  drill/  ...
```

## `melee/`: Đòn cận chiến

Đòn vật lý đánh gần, gắn với vũ khí hoặc cơ thể: vệt vung, vệt đâm, va chạm của vũ khí.

| Thư mục | Tên | Chứa gì | Ví dụ | Hiện có |
|---|---|---|---|---|
| `melee/unarmed/` | Tay không | đấm, đá, chưởng tay (phần vệt và va chạm của đòn thân thể), húc vai, vật | vệt đấm thẳng, vệt đá quét, tia trúng nắm đấm | - |
| `melee/blade/` | Kiếm, dao | vệt chém, đâm, chém xoay, chuỗi combo của vũ khí có lưỡi | vệt chém lưỡi liềm, chém chữ X, đâm nhanh, chém xoáy | Xoáy chém lửa (draft), Xoáy chém băng (draft) (công thức: lib-fx/_core/formulas/draw/recipes/RECIPE-swirl.md) |
| `melee/blade_aura/` | Ánh sáng trên lưỡi | năng lượng phủ lên chính lưỡi vũ khí (không phải vệt chém rời lưỡi): tụ lực trước đòn, giữ sáng suốt và sau đòn | tụ lực lưỡi đao (xanh, lửa) | Tụ lực lưỡi đao xanh (approved), Tụ lực lưỡi đao lửa (approved) |
| `melee/blunt/` | Búa, chùy | đòn nặng: đập, nện xuống đất, vụt ngang | vệt búa nặng, đập đất nứt | - |
| `melee/polearm/` | Thương, giáo | đâm xuyên dài, quét rộng hình quạt | đâm thương xuyên, quét giáo | - |
| `melee/beast/` | Quái thú | vuốt, cắn, húc, quật đuôi của quái | ba vệt vuốt, vết cắn | - |

## `ranged/`: Đòn tầm xa vật lý

Vũ khí bắn hoặc ném không dùng phép: đầu nòng, vật bay, vệt bay.

| Thư mục | Tên | Chứa gì | Ví dụ | Hiện có |
|---|---|---|---|---|
| `ranged/bow/` | Cung, nỏ | vệt tên bay, kéo cung tụ lực, mưa tên, tên xuyên | vệt tên, tia lúc buông dây, mưa tên | - |
| `ranged/thrown/` | Vật ném | dao, rìu, đá, bom ném tay: vệt xoay khi bay | vệt dao xoay, vòng rìu bay | - |
| `ranged/siege/` | Công thành | pháo, máy bắn đá, bom (tháp pháo): lửa đầu nòng, quỹ đạo, khói bắn | lửa đầu nòng pháo, vệt đạn cong | - |

## `force/`: Chưởng lực

Năng lượng thuần không thuộc nguyên tố nào: khí công, chưởng, sóng lực. Màu do bảng màu quyết định.

| Thư mục | Tên | Chứa gì | Ví dụ | Hiện có |
|---|---|---|---|---|
| `force/shock/` | Sóng xung kích | luồng lực bùng ra dọc một trục tại điểm chạm của đòn thẳng (đá, đấm, chưởng) | tầng vòng, khoan xoắn, vòng vỡ | Hoa nổ (draft), Khoan xoắn (draft), Vòng vỡ (draft), Tầng vòng (draft), Nón hơi (draft), Hỏa xung tầng (approved, công thức: lib-fx/_core/formulas/draw/recipes/RECIPE-inferno.md) |
| `force/wave/` | Sóng lan | sóng lực lan trên mặt đất hoặc bay đi như một bức tường | sóng chưởng bay, sóng lan đất | - |
| `force/beam/` | Tia năng lượng | tia bắn thẳng liên tục (kame-style), có đầu, thân, điểm chạm | tia chưởng, tia khí | - |
| `force/charge/` | Tụ khí | gom lực trước đòn: hạt bay vào, quầng sáng lớn dần, bùng khí | tụ khí tay, bùng khí toàn thân | - |

## `element/`: Nguyên tố

Phép và đòn mang nguyên tố vật lý. Mỗi nguyên tố chia theo chức năng chuẩn (bên dưới).

Mỗi thư mục con chia tiếp theo chức năng:

- `cast/`: tụ phép ở người dùng: vòng phép dưới chân, ánh sáng gom vào tay, trước khi phóng
- `projectile/`: vật bay: quả cầu, mũi tên phép, tia; gồm đầu đạn + vệt đuôi
- `impact/`: lúc trúng mục tiêu: nổ nhỏ, tóe, chớp
- `aoe/`: vùng ảnh hưởng trên mặt đất: vòng, cột, mưa, bãi
- `aura/`: hào quang lặp quanh người hoặc vật: cháy âm ỉ, khí bao quanh
- `status/`: dấu hiệu trạng thái gắn trên mục tiêu: bị đốt, đóng băng, nhiễm độc...

| Thư mục | Tên | Chứa gì | Ví dụ | Hiện có |
|---|---|---|---|---|
| `element/fire/` | Lửa | lửa, than hồng, khói nóng | quả cầu lửa, cột lửa, bị đốt | - |
| `element/water/` | Nước | sóng, tóe nước, bong bóng, xoáy nước | tóe nước, cột nước, xoáy | - |
| `element/ice/` | Băng | tinh thể, sương lạnh, mảnh băng | gai băng, đóng băng, mưa đá | - |
| `element/lightning/` | Sét | tia sét gấp khúc, điện nhảy, chớp | sét đánh, sét chuyền, giật điện | - |
| `element/earth/` | Đất, đá | đá trồi, nứt đất, bụi đá | gai đá, động đất, tảng đá | - |
| `element/wind/` | Gió | lốc, lưỡi gió, luồng khí | lốc xoáy, lưỡi gió, đẩy lùi | - |
| `element/nature/` | Thực vật | lá, dây leo, hoa, rễ | dây trói, mưa lá, hoa hồi máu | - |
| `element/poison/` | Độc, axit | khói độc, bọt axit, giọt độc | mây độc, tóe axit, nhiễm độc | - |

## `magic/`: Trường phái phép

Phép không phải nguyên tố vật lý: thần thánh, bóng tối, ma thuật. Chia theo chức năng chuẩn như nguyên tố.
Một chiêu trọn bộ (tụ phép → bay → trúng → bám mục tiêu) có thể nằm ngay ở cấp họ (vd. `magic/spirit/soulstrike`); các phần lẻ
làm sau thì vào thư mục chức năng (`cast/`, `projectile/`...).

Mỗi thư mục con chia tiếp theo chức năng:

- `cast/`: tụ phép ở người dùng: vòng phép dưới chân, ánh sáng gom vào tay, trước khi phóng
- `projectile/`: vật bay: quả cầu, mũi tên phép, tia; gồm đầu đạn + vệt đuôi
- `impact/`: lúc trúng mục tiêu: nổ nhỏ, tóe, chớp
- `aoe/`: vùng ảnh hưởng trên mặt đất: vòng, cột, mưa, bãi
- `aura/`: hào quang lặp quanh người hoặc vật: cháy âm ỉ, khí bao quanh
- `status/`: dấu hiệu trạng thái gắn trên mục tiêu: bị đốt, đóng băng, nhiễm độc...

| Thư mục | Tên | Chứa gì | Ví dụ | Hiện có |
|---|---|---|---|---|
| `magic/holy/` | Thánh, ánh sáng | ánh sáng trời, hào quang, lông vũ, chữ thập | cột sáng phán xét, hồi máu, khiên thánh | - |
| `magic/shadow/` | Bóng tối | khói đen, tay bóng tối, mắt, hư không | lỗ đen, trói bóng, nguyền | - |
| `magic/arcane/` | Ma thuật | rune, vòng phép, tinh thể tím, dịch chuyển | vòng phép, tên ma thuật, cổng | - |
| `magic/blood/` | Huyết thuật | máu, hút máu, gai máu | hút máu, gai máu | - |
| `magic/spirit/` | Linh hồn | hồn lửa (ma trơi) rời khỏi thân, bay, nhập và đốt mục tiêu; lửa hồn dưới đất; bóng ma bám mục tiêu | xuất hồn kích | Xuất hồn kích (rework; phần linh hồn nhỏ đạt: lib-fx/_core/formulas/draw/recipes/RECIPE-soul-spirits.md) |

## `explosion/`: Vụ nổ

Nổ dùng chung cho mọi nhóm (bom, pháo, phép, quái chết). Thêm màu bằng bảng màu.

| Thư mục | Tên | Chứa gì | Ví dụ | Hiện có |
|---|---|---|---|---|
| `explosion/blast/` | Nổ | quả cầu nổ, vòng sóng nổ, chớp nổ; to nhỏ theo cấp | nổ nhỏ, nổ lớn, nổ năng lượng | - |
| `explosion/smoke/` | Khói, bụi | khói bốc sau nổ, bụi cuộn, khói tan | cột khói, bụi cuộn | - |
| `explosion/debris/` | Mảnh văng | đá vụn, mảnh gỗ, mảnh kim loại văng ra | đá văng, mảnh vỡ | - |

## `impact/`: Va chạm chung

Hiệu ứng trúng đòn nhỏ, dùng nhiều nhất, không thuộc vũ khí hay nguyên tố nào.

| Thư mục | Tên | Chứa gì | Ví dụ | Hiện có |
|---|---|---|---|---|
| `impact/hit/` | Trúng đòn cận chiến | tia trúng của đấm, kiếm, búa: lõi trắng, gai cong, giọt văng (hình tự do, xem lib-fx/_core/formulas/draw/RESEARCH-organic-impact.md) | nổ sao, mũi chéo, vòng gai, chữ thập chí mạng | Mũi chéo (draft), Chữ thập chí mạng (draft), Vòng gai (draft), Nổ sao (draft) |
| `impact/dash/` | Lướt va chạm | cú va ở cuối một cú lướt / lao: mép sáng phía trước, gai chảy về sau dọc đường lao, giọt bay tới trước | vách lưỡi liềm, xuyên vòng, sao chổi | Sao chổi (draft), Xuyên vòng (draft), Vách lưỡi liềm (draft) |
| `impact/crit/` | Chí mạng | trúng mạnh nổi bật hơn hit thường | tia chí mạng, vỡ kính | - |
| `impact/ground/` | Mặt đất | nện, đập, tiếp đất: khói nhiều tầng là chính, gai sáng, đá văng, vòng dẹt trên mặt đất | nện bụi, vòng chấn đất, phun đất | Vòng chấn đất (draft), Phun đất (draft), Nện bụi (draft) |

## `status/`: Trạng thái

Hiệu ứng gắn trên người không thuộc nguyên tố (trạng thái theo nguyên tố nằm ở element/<x>/status).

| Thư mục | Tên | Chứa gì | Ví dụ | Hiện có |
|---|---|---|---|---|
| `status/buff/` | Có lợi | tăng sức, tăng tốc, khiên, hồi máu, bất tử | khiên, tăng sức, hồi máu | - |
| `status/debuff/` | Bất lợi | choáng, chậm, câm lặng, sợ hãi, giảm giáp | sao choáng, chậm, câm | - |

## `life/`: Vòng đời nhân vật

Những lúc nhân vật xuất hiện, biến mất, đổi trạng thái lớn.

| Thư mục | Tên | Chứa gì | Ví dụ | Hiện có |
|---|---|---|---|---|
| `life/spawn/` | Xuất hiện | nhân vật hoặc quái hiện ra trên map | vòng triệu hồi, khói xuất hiện | - |
| `life/death/` | Chết | tan biến, ngã, linh hồn bay lên | tan thành khói, hồn bay | - |
| `life/respawn/` | Hồi sinh | hero sống lại | cột sáng hồi sinh | - |
| `life/levelup/` | Lên cấp | hero lên cấp | hào quang lên cấp | - |
| `life/teleport/` | Dịch chuyển | biến mất ở chỗ này, hiện ra chỗ khác | chớp dịch chuyển, cổng | - |
| `life/dash/` | Lướt | lướt nhanh: bóng mờ, vệt tốc độ, bụi, một nguyên tố đi kèm (lửa, gió...) | bóng mờ lướt, vệt tốc độ, hổ lửa | (chưa có; `tiger` đã xoá 2026-11-09, bài học ở lib-fx/_core/formulas/draw/DESIGN.md §10) |

## `ui/`: Giao diện

Phản hồi trên giao diện và trên map cho người chơi.

| Thư mục | Tên | Chứa gì | Ví dụ | Hiện có |
|---|---|---|---|---|
| `ui/number/` | Chữ số | số sát thương, chữ chí mạng, số hồi máu | số bay lên, chữ CRIT | - |
| `ui/pickup/` | Nhặt đồ | vàng, vật phẩm, sao khi nhặt | xu bay vào túi | - |
| `ui/tower/` | Tháp | xây, nâng cấp, bán tháp (game thủ thành) | bụi xây tháp, sáng nâng cấp | - |

## `environment/`: Môi trường

Hiệu ứng nền của map, thường lặp: thời tiết, ánh sáng, nước, sinh vật nhỏ.

| Thư mục | Tên | Chứa gì | Ví dụ | Hiện có |
|---|---|---|---|---|
| `environment/` | Môi trường | mưa, tuyết, sương, đuốc, lửa trại, thác nước, đom đóm, lá rơi | mưa, đom đóm, đuốc | - |

## Thêm một hiệu ứng

1. Chọn họ theo bảng trên (chưa có họ phù hợp thì tạo thư mục mới trong nhóm đúng và ghi thêm vào file này).
2. Viết code trong `<họ>/<họ>.py` (khuôn: `force/shock/shock.py`), dùng hình trong `_core/fxcore.py` và màu trong `_core/palettes.py`.
3. `python lib-fx/build.py <nhóm>/<họ>`, xem `_gallery/<nhóm>-<họ>.png|gif`, duyệt rồi đổi trạng thái thành `approved`.
4. Xóa README "chưa có hiệu ứng" của họ đó khi họ đã có hiệu ứng đầu tiên.
