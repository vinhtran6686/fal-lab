# Bàn giao: hệ thống hiệu ứng lib-fx / fxkit (tới 2026-11-14)

Đọc file này trước khi làm tiếp. Nhánh làm việc: `ccr-38411bc5-l13uki` (repo `vinhtran6686/fal-lab`). Mọi thứ đã push; cây git sạch ở commit bàn giao.
Thư mục `lib-fx/_plans/` là kế hoạch đang chạy; xoá từng thư mục con khi kế hoạch đó xong và được duyệt.

## 1. Cách làm việc đã thống nhất với người dùng
- **Vai trò**: Claude ở session chính là **người lập kế hoạch và người chấm**. Không tự thi công. Người dùng giao từng task cho AI khác làm trên chính nhánh này, rồi báo "xong" để chấm.
- **Vòng lặp**: (1) người dùng góp ý → (2) phân tích nguyên nhân trong code, nói rõ đồng ý hay không → (3) viết task vào `lib-fx/_plans/<kế hoạch>/` + cập nhật checklist trong `PLAN.md`, push,
  báo người dùng **mã task** → (4) AI khác thi công, điền mục "Kết quả" → (5) pull, **tự dựng lại và nhìn ảnh** (không tin số trong báo cáo), ghi nhận xét vào `PLAN.md`, gửi ảnh so sánh và đánh giá → (6) người dùng duyệt.
- **Viết task** để người thi công "chỉ làm, không phải nghĩ": vấn đề + nguyên nhân có tên file / dòng, file được sửa, công thức và giá trị cụ thể, tiêu chí nghiệm thu đo được, lệnh chạy, mục "Kết quả".
  Luôn kèm ràng buộc: không sửa `out/` (asset đã duyệt chỉ là mốc so sánh), không hồi quy (so hash khung của hiệu ứng cũ), `build.py --check` và `fxkit_test.py` phải qua.
- **Chấm**: dựng ở 15 fps với `--split`, ghép `back/` dưới thân và `front/` trên thân nhân vật, đặt `hit_frame` của fx trùng khung trúng đòn; xem cả cỡ game. Gửi ảnh bằng công cụ gửi file.
- Người dùng muốn câu trả lời ngắn, tiếng Việt, tiết kiệm context; code, tên file, lệnh giữ nguyên tiếng Anh. Tài liệu trong skill viết tiếng Anh; tài liệu `lib-fx` và kế hoạch viết tiếng Việt.
- Việc tốn tiền (sinh ảnh, video) phải hỏi trước. Không đọc `.env`.

## 2. Đã có gì trong repo
| Thứ | Ở đâu | Trạng thái |
|---|---|---|
| `fxkit`: hệ thống dựng hiệu ứng theo lớp (không gian a → b, vòng đời từng lớp tính từ khung trúng đòn, biến thiên theo seed, tông phẳng xếp chồng, quầng = bản nhoè của hình, mòn tại chỗ, làm mịn nét) | `lib-fx/_core/formulas/draw/fxkit/`, hướng dẫn `lib-fx/_core/formulas/draw/FXKIT.md` | dùng được; **đọc FXKIT.md trước khi viết task về hiệu ứng** |
| 11 loại lớp: `flames`, `crystals`, `slash`, `bolt`, `star`, `streaks`, `ring`, `smoke`, `dust`, `scraps`, `embers` | `fxkit/layers/*.py` | xong |
| 26 hiệu ứng fxkit trong 7 họ: `impact/spark`, `impact/quake`, `melee/slash`, `ranged/bolt`, `element/fire/aoe`, `magic/arcane/aoe`, `explosion/blast` | `lib-fx/<nhóm>/<họ>/` | tất cả `draft`; người dùng: "khá ok, một số chưa được nhưng tạm chấp nhận, dùng tới đâu sửa tới đó" |
| Cổng chất lượng, biến thể cho nhân vật, bảng duyệt một lớp, test hồi quy | `lib-fx/_tools/fxcheck.py`, `lib-fx/build.py` (`--from --to --pal --s --seed --fps --speed --split --set --track --swing --out`), `_tools/fxkit_sheet.py`, `_tools/fxkit_test.py` | xong |
| Vệt chém: theo vũ khí (`weapon=sword|axe|saw`), bám quỹ đạo vũ khí thật (`--track`, hiệu ứng `swing`), theo mặt phẳng vung (`--swing`, hiệu ứng `sweep`, `diag_down`, `diag_up`) | `fxkit/layers/slash.py`, `lib-fx/melee/slash/slash.py` | S1 đạt; S2 đạt mô hình, `sweep` còn yếu (xem mục 4) |
| Góc nhìn của game và mặt phẳng của động tác (chém dọc / ngang / xéo, đâm, phép; cách tả pose A / B; thứ cần ghi cho vfx) | `.claude/skills/fal-image/action-planes.md` (chính), `.claude/skills/video-sprite/references/action-planes.md` | viết xong; phần chữ cho pose chém ngang và xéo **chưa thử sinh ảnh** |
| Dựng lại hai mẫu mới bằng bộ vector | `lib-fx/_core/formulas/vector/profiles/flame-burst.json`, `lightning.json`, `lib-fx/_core/results/vector-showcase/` | R1, R2 thi công xong, **chưa chấm** |
| Trang duyệt (GIF từng hiệu ứng, before / after) | https://claude.ai/artifact/6NN5cynqUge1CqM7tfUfoR | dựng từ bản cũ hơn vòng góp ý; có thể lệch so với repo |
Họ hiệu ứng cũ (khai báo `VARIANTS`: `force/shock`, `impact/hit`, `impact/ground`, `impact/dash`, `melee/blade`, `melee/blade_aura`, `magic/spirit`) vẫn chạy như trước; `magic/spirit/soulstrike` (nhãn `rework`) là hiệu ứng duy nhất FAIL cổng, ngoài phạm vi.

## 3. Bài học đã rút ra (đừng lặp lại)
1. **Phong cách người dùng duyệt** = các mẫu trong `ref/vfx/` và `lib-fx/_core/results/vector-showcase/` (đã chấm 9-10/10), luật có số đo ở `lib-fx/_core/formulas/rules/01`, `02`, `05`:
   hình ít và lớn, nét cong liền có mũi nhọn; 2-3 tông phẳng xếp chồng; quầng là bản nhoè của hình; tàn bằng mòn và vỡ tại chỗ. Kiểu tô viền đồng tâm ("sticker") và hàng khối tròn bằng nhau đã bị chê hai lần.
2. **Chất liệu thể hiện qua cách chuyển động và cách tan, không qua hoa văn**: kiếm = các nét mịn cùng hướng; rìu = dải song song; mòn bằng nhiễu để lại "hoa văn" là sai với vệt chém.
3. **Vệt chém phải là bề mặt lưỡi quét**: mép ngoài = đường mũi vũ khí, mép dẫn nằm dọc lưỡi ở pose cuối, mũi đậm chuôi nhạt, khung trước đòn chỉ là lát mỏng trên lưỡi pose đầu, vệt đầy ngay khung trúng đòn, đuôi rút trước.
4. **Góc nhìn quyết định hình vệt**: một cú chém là đường tròn quanh vai; hình thấy được là hình chiếu của nó. Song song màn hình = lưỡi liềm; nằm ngang = ellipse rất dẹt (độ dẹt 0,3, bằng các vòng trên đất), nửa xa sau thân, nửa gần trước thân; xéo = ở giữa.
5. **15 fps khác 30 fps**: mọi nhịp phải kiểm ở 15 fps (tốc độ của thân nhân vật); "on twos" không được áp thêm khi fps < 20; khung trúng đòn phải ghim vào lưới khung.
6. **Hiệu ứng trên đất** phải nằm trên mặt phẳng đất (tham số `plane=("ground", k)`), chỉ phần bốc lên mới đứng.
7. **Trúng đòn nhẹ / nặng / chí mạng** phải khác nhau ở hình bóng, số lớp, nhịp, kể cả khi xem ảnh xám, không chỉ khác cỡ.
8. Tìm trên web không ra luật VFX có số; nguồn đáng tin là **đo mẫu của hoạ sĩ**. Bản nháp phương pháp chung (quy trình 9 bước của hoạ sĩ FX, 6 yếu tố chất lượng, đề xuất "bảng thiết kế trước khi code" và "duyệt theo tầng"): `lib-fx/_plans/vfx-rebuild-02/METHOD.md`, chưa thành luật.
9. Người thi công hay lệch task có lý do chính đáng (công thức trong task có thể sai: ví dụ vector `P` phải nhân `face`). Khi chấm: đọc mục "Lệch so với task", chấp nhận nếu ảnh đúng.

## 4. Việc đang mở (theo thứ tự ưu tiên)
| # | Việc | Ở đâu | Ai |
|---|---|---|---|
| 1 | **S2b**: `sweep` (chém ngang) còn yếu: kéo dài và làm dày phần gần; nhịp tan theo bán kính | `slash-round-02/S2b-sweep-strength.md` | AI thi công, rồi chấm |
| 2 | **Thử pose chém ngang thật** cho `azure_blade` (hai ảnh, ~0,03 USD): kiểm cả `action-planes.md` lẫn `sweep` | chưa có task; **chờ người dùng đồng ý chi** | người dùng quyết |
| 3 | **Chấm R1, R2** (flame-burst, lightning): xem `compare.gif` và mục "Kết quả" của hai task | `vfx-rebuild-02/PLAN.md` ô CHẤM | người lập kế hoạch |
| 4 | **R3**: xuất số đo cho 8 giả thuyết H1-H8 và cho từng dòng [suy luận] của `METHOD.md` (chỉ sau khi R1, R2 đạt) | `vfx-rebuild-02/R3-export-measurements.md` | AI thi công |
| 5 | Sau khi người dùng duyệt R1-R3: **viết docs phương pháp chung** vào `lib-fx/_core/formulas/rules/` (phương pháp trước, ghi chú từng chất liệu sau), rồi task dựng lớp fxkit cho lửa phụt và sét | - | người lập kế hoạch |
| 6 | **S3**: rìu dày hơn (ít dải, dải rộng); hiện dải mảnh như răng lược | chưa viết task | khi người dùng yêu cầu |
| 7 | Quyết định của người dùng còn treo: có thay vệt đã duyệt của `azure_blade` (`build_crescent.py`) bằng `melee/slash/swing --track` không; các họ cũ trùng việc giữ hay bỏ | - | người dùng |
| 8 | Việc nhỏ đã biết: `embers` quá nhỏ ở cỡ game; `charge_blue` / `charge_fire` chưa đổi được màu / cỡ qua dòng lệnh; `swing` ở 30 fps mặc định còn cảnh báo `pop` / `cut`; trang duyệt cần dựng lại | - | khi cần |

## 5. Số liệu hay dùng khi chấm (nhân vật `out/heroes/azure_blade`, px ô @2x, ô 352x280)
- Skill "Trảm Trăng Khuyết": thân `frames/skill_crescent_puppet_side/frames/@2x/` (44 khung, 15 fps, khung trúng đòn 23); bản đã duyệt có vệt `frames/skill_crescent_side/` (không sửa); đường mũi đao `frames/skill_crescent_side/track.json`.
- Mũi A (107.3, 191.1), chuôi A (118.5, 144.1), mũi B (238.6, 241.0), chuôi B (202.9, 241.5); vai của dáng đứng (khung 1) ước lượng (140, 160).
- Lệnh mẫu:
```
python lib-fx/build.py melee/slash/swing --from 107.3,191.1 --to 238.6,241.0 --pal frost --fps 15 --split \
    --track "root_a=118.5,144.1;root_b=202.9,241.5;up=35;turn=cw;ease=1.3" --out <tạm>
python lib-fx/build.py melee/slash/sweep --from 140,160 --to 225,160 --pal frost --fps 15 --split --out <tạm>
```
- Ghép: dán khung fx tại `meta.json → origin`; khung fx `hit_frame` vào khung thân trúng đòn; `back/` dưới thân, `front/` trên thân.
- Máy mới: `pip install scipy` (và `scikit-image opencv-python-headless` cho bộ vector) trước khi dựng.

## 6. Bản đồ tài liệu
`CLAUDE.md` (quy tắc dự án) → `docs/repo-structure-rules.md` (đặt file ở đâu) → `lib-fx/README.md`, `lib-fx/GUIDE.md` → `lib-fx/_core/formulas/draw/FXKIT.md` (hệ thống) →
`lib-fx/_core/formulas/rules/` (luật có số đo; `vfx/slash/README.md` cho vệt chém) → `.claude/skills/fal-image/action-planes.md` (góc nhìn) → `docs/pipeline/pose-pair-fx-method.md` (skill bằng hai pose + vfx).
