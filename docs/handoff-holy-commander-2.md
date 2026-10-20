# Handoff 2: holy_commander, các trạng thái còn lại (2026-10-20)

Dành cho session mới (máy khác) để làm tiếp video cho các trạng thái còn thiếu của `out/heroes/holy_commander`.
Đọc kèm, theo thứ tự:
1. `docs/holy-commander-report.md`: lý do chọn từng version, bài học từ attack và death.
2. `out/heroes/holy_commander/history.md`: từng take, prompt, gate, quyết định của user.
3. `out/heroes/holy_commander/brief.md`: design, slots, manifest.
4. `docs/kr-reference-handover.md`: một hero trong game tham chiếu gồm những gì.

Artifact so sánh với hero tham chiếu (malik): https://claude.ai/artifact/MxiAuzsxrmnLt7EgZm1JCj
- Nguồn trong repo: `tools/kr_compare/` (`build_manifest.py`, `index.html`, `manifest.json`).
- Artifact có khoảng 468/511 file; mỗi version tối đa 511. Trước khi thêm state mới, bỏ các state không
  còn dùng: `attack` (bản đủ frame), `death` (bản đủ frame), `charge_v2`.

## 0. Skill 1 (`charge_v4`): đã có trong git (commit c897f40, kiểm 2026-10-20)

- Clip gốc: `raw/skill_side_skill_charge_v2_t01`, `_v3_t01`, `_v4_t01` (`.mp4` + `.json`; prompt đầy đủ
  nằm trong `.json`). Bản chốt: **v4** (4 s).
- `history.md`: có đủ dòng v2, v3, v4 (t01 cũ đánh dấu superseded). `brief.md`: dòng charge = "v4 chốt, chưa export".
- `docs/holy-commander-report.md`: từ §9-§10 phân tích charge (vì sao v2 sạch, vì sao v3/v4 có vòng lửa).
  Bảng ở mục 1-2 của report là bản cũ hơn; khi lệch nhau, tin `history.md` và các mục cuối của report.
- `tools/kr_compare/build_manifest.py` đã dựng state `charge_v2`, `charge_v4`.
- Thư mục set (`.work/side_skill_charge_v4/`) không lên git. Muốn export, dựng lại set từ clip trong `raw/`
  (route "supplied"), không quay lại clip.
- Câu chống zoom "locked tripod" nằm trong prompt v2 (`raw/skill_side_skill_charge_v2_t01.json`) và trong report.
- Lưu ý: đuôi style trong prompt v2-v4 vẫn là style cũ ("muted earthy palette", "near-black outlines").
  Style hiện tại ở `fal-image/format.md` §1. Clip mới nên dùng style hiện tại; kiểm tra xem đuôi này do
  plan local sinh ra hay do `sprite_set.py`.

## 1. Trạng thái hiện tại

| Asset | Trạng thái | Bản chốt | Còn thiếu |
|---|---|---|---|
| master (= idle), icon, 3 pose skill | ✅ | v07, v01 | - |
| `idle_side` | ✅ đã export | frame 0 của run t01 | - |
| `run_side` | ✅ đã export | t01, 8 hình, `--despill --kind hero` | - |
| `attack_side` | ⏳ chốt, chưa export | `attack_fast_frames` = t04 (accept `--window 0:73`) bỏ 1/2 frame: 23 hình, 1.53 s @15 fps | export lên canvas game |
| `death_side` | ⏳ duyệt, chưa export | `death_fast_frames` = t01 bỏ 1/2 frame: 39 hình, 2.60 s @15 fps | export |
| `skill_charge_side` (skill 1) | ⏳ chốt, chưa export | `charge_v4` (`raw/skill_side_skill_charge_v4_t01`): 67 hình, có lửa + blade-flash vẽ thẳng vào thân | export, quyết định về vòng lửa (mục 3) |
| `respawn_side` | ❌ | `raw/despawn_side_extra_t01` đạt (score 8) | export `--reverse` (miễn phí) + `fx_respawn` |
| `levelup_side` | ❌ | t01 có vệt chém xanh và bụi | quay lại + `fx_levelup` |
| `skill_holy_banner_side` (skill 2) | ❌ | t01 có vòng sáng hồng/vàng, area 2.9x | quay lại + fx |
| `skill_radiant_slash_side` (skill 3) | ❌ | t01 có vệt chém hồng lớn, identity 0.45 | quay lại + fx |

`meta.json` đã cố định canvas **156x140**, pivot (0.5, 0.88), **`body_height_2x` 111** (đo từ run).
- Mọi export sau phải khớp 111, đừng "sửa" về 120 của tier M; nếu không, các trạng thái sẽ lệch cỡ nhau.
- Bóng: 83x25 @2x, alpha 0.35.

## 2. Bài học đã kiểm chứng (CHƯA có trong SKILL.md; dùng khi viết prompt)

Đề xuất sửa skill nằm ở `docs/holy-commander-report.md` mục 5, đang chờ duyệt. Session này **không sửa
`SKILL.md`**: chỉ ghi kết quả vào `history.md` và report.

1. **Chỉ dồn người về phía trước.** Không viết "dồn trọng tâm ra chân sau" hay "ngả người ra sau": model
   (h3-max-turbo) đọc thành lệnh xoay cả người lại (attack t03: 4 đoạn quay lưng, pose cuối trôi khỏi master).
2. **Thời lượng có ngưỡng dưới theo số nhát chém.**
   - Combo 2 nhát cần 3 s. Ở 2 s model gộp thành 1 nhát (t05), kể cả khi prompt ép "EXACTLY TWO" (t06).
   - Đừng quay ngắn hơn để "tăng tốc".
3. **Tăng tốc = bớt frame của take đã đạt, không quay video mới.**
   - Giữ 1 trong 2 frame (`decimate`, stride 2) trong `tools/kr_compare/build_manifest.py`.
   - Clip raw luôn trông chậm; đánh giá tốc độ trên frame đã bớt, không trên clip raw.
4. **Vệt lưỡi liềm mờ cạnh lưỡi kiếm.**
   - Model gần như luôn tự vẽ nó khi chém, dù prompt cấm.
   - Nó làm gate `area`, `feet`, `turn` báo lỗi sai.
   - Trước khi loại một take vì gate: tách và key frame thật, xem trong kr_compare. Nếu thân không quay lưng
     và chân không trượt, user duyệt bằng mắt thì `accept --window`.
5. **Combo 2 nhát khác dáng** (chéo xuống + ngang) đọc nhanh và bớt cứng hơn 1 nhát đứng yên; ổn định hơn combo 3 nhát.
6. **Chống zoom:** câu "locked tripod" của charge_v2 đưa area từ median 2.54x xuống 1.21x. Lấy nguyên văn
   từ `raw/skill_side_skill_charge_v2_t01.json` và dùng cho mọi skill còn lại. Câu này chỉ hiệu quả khi prompt
   KHÔNG mời hiệu ứng; v3/v4 có mô tả lửa nên vẫn sinh vòng lửa lớn (report §10).
7. **Death và các động tác liền một mạch** (ngã, chìm) không bị mất pha khi bớt frame, nên quay 1 lần là đủ.

## 3. Hai quyết định phải hỏi user TRƯỚC khi chạy clip trả phí

**A. Quy ước hiệu ứng cho skill 2 và skill 3.**
`charge_v4` vẽ lửa và blade-flash thẳng vào clip thân. Điều này khác quy ước của skill: clip thân chỉ có
thân, hiệu ứng làm bằng `fx_layers.py`. Ba skill phải theo cùng một hướng:
- (1) **Thân sạch + `fx_layers`** cho holy_banner và radiant_slash; charge_v4 giữ như ngoại lệ đã chốt.
  - Đúng cách game tham chiếu làm: hiệu ứng là object riêng.
  - Đã có sẵn: recipe mẫu `fx/radiant_slash.json`, mảnh fx `fx_holy_banner`.
- (2) **Vẽ thẳng vào thân như charge_v4** cho cả 3 skill: nhanh, đồng bộ về nhìn, nhưng khó kiểm soát
  (vòng lửa lớn ở frame ~46-72 của charge_v4 xuất hiện 2 lần dù đã cấm).
- (3) Trộn: radiant_slash cho phép blade-flash phẳng (model đằng nào cũng vẽ vệt chém); holy_banner thân
  sạch + cờ và vòng đất bằng `fx_layers` (lá cờ là một object riêng, không thể vẽ ổn vào clip thân).

Gợi ý: (3). Nhưng user quyết; đừng tự chọn.
Kèm câu hỏi phụ: giữ vòng lửa lớn trong charge_v4 hay cắt các frame đó khi export?

**B. Tốc độ khi export.**
- User duyệt attack 1.53 s và death 2.60 s; game tham chiếu dùng attack ~0.6-0.75 s, death ~0.3 s.
- Export mặc định (`retime --auto-oneshot`) sẽ nén attack về ~0.7 s và death về ~0.9 s, tức NHANH HƠN bản đã duyệt.
- Mặc định của handoff này: **giữ đúng tốc độ đã duyệt**. Đặt `timing.durationMs` trong `set_plan.json`
  (hoặc `--oneshot-ms attack=1530,death=2600`), rồi `rebuild` và export.
- Retime còn cắt các đoạn đứng yên, nên kết quả sẽ không giống hệt bản bỏ 1/2 frame. Đặt bản export cạnh
  `attack_fast_frames` / `death_fast_frames` trong kr_compare; chỉ thay khi user thấy giống.
- Muốn theo đúng độ dài của game tham chiếu là một quyết định riêng của user.

## 4. Thứ tự làm đề xuất

| # | Việc | Chi phí |
|---|---|---|
| 1 | Đọc mục 0 (charge v4 đã có trong git) | 0 |
| 2 | Hỏi user 2 quyết định ở mục 3 | 0 |
| 3 | Export attack, death, charge_v4 lên canvas 156x140, body 111 (mục 3B); cập nhật manifest, kr_compare | 0 |
| 4 | `respawn_side` = despawn t01 `--reverse`; recipe `fx/respawn.json` (pillar + ring) | 0 |
| 5 | `levelup_side`: quay lại (giơ kiếm chào, KHÔNG vung ngang, không hiệu ứng, câu locked tripod); `fx/levelup.json` (pillar hoặc burst) | ~0.08 USD/take |
| 6 | Skill 2 `holy_banner`: endStill = `pose_skill_holy_banner_v01`, giữ pose; hiệu ứng theo quyết định 3A | ~0.08 USD/take |
| 7 | Skill 3 `radiant_slash`: endStill = `pose_skill_radiant_slash_v01`; nhát chém dồn về trước (bài học 1, 4); hiệu ứng theo 3A | ~0.08 USD/take |

- Thực tế attack mất 5 take, charge khoảng 4. Khi báo giá, tính vài take cho mỗi skill (khoảng 0.25-0.40 USD
  mỗi skill), không chỉ 1.
- Mỗi lần chạy trả phí: báo số clip và giá, chờ user "ok" (cost guard trong CLAUDE.md).
- Sau mỗi take:
  - tách + key frame, đưa lên kr_compare cạnh malik, user duyệt bằng mắt;
  - nếu chậm thì bớt frame (bài học 3);
  - ghi `history.md`, cập nhật manifest trong `brief.md`.
- Cuối mỗi bước: `python scripts/video_prune.py prune --set <set>`; publish lại artifact kr_compare (cùng URL).
