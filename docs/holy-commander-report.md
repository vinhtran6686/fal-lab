# holy_commander: status report (2026-10-20)

Chốt lại toàn bộ asset của `holy_commander` tới thời điểm này: phần nào đã duyệt, phần nào còn treo, và giải
thích kỹ thuật vì sao `run_side` (t01) và `attack_side` (t04) được chọn để tiếp tục convert sang frame. Các
bài học rút ra từ 2 asset này được tổng hợp ở mục 5 thành **đề xuất** sửa `.claude/skills/video-sprite/SKILL.md`
— **chưa áp dụng vào skill**, chờ duyệt.

## 1. Đã chốt (ổn, có thể dùng hoặc đã dùng trong `tools/kr_compare`)

| Asset | Trạng thái | Ghi chú |
|---|---|---|
| `master` (=idle, v07) | ✅ duyệt | trường kiếm cắm đất, hai chân giang rộng, báng đại bàng |
| `icon` v01 | ✅ duyệt | |
| `pose_skill_holy_banner` v01 | ✅ duyệt | |
| `pose_skill_radiant_slash` v01 | ✅ duyệt | |
| `pose_skill_charge` v01 | ✅ duyệt | |
| `fx_holy_banner`, `fx_radiant_slash` v01 | ✅ duyệt | còn là still/part, chưa lắp thành recipe `fx_layers.py` đầy đủ |
| **`run_side` t01** | ✅ **export chính thức** | 8 hình thật, 15fps, canvas 156×140, body 111px@2x, `--despill --kind hero`; mọi gate pass trừ `colour` (sửa bằng despill) |
| **`idle_side` t01** | ✅ **export chính thức** | miễn phí, frame 0 của `run_side` (`--rest-frame`), cùng canvas/tỉ lệ với `run_side` |
| **`attack_side` — t04 bớt frame (chốt)** | ⏳ **chốt, chưa export** | combo 2 chém; `sprite_set.py accept --window 0:73` trên t04 gốc; user chốt dùng bản đã bớt 1/2 frame (46→23 hình, 1.53s@15fps) làm animation nhanh hơn — xem mục 6-7; còn thiếu bước `video_to_sheet.py` trên đúng tập frame đã bớt |

## 2. Chưa xong / chưa chốt

| Asset | Trạng thái | Việc còn lại |
|---|---|---|
| `death_side` | raw đạt (score 8, review cũ) | chưa export |
| `respawn_side` (despawn `--reverse`) | raw đạt (score 8) | chưa export |
| `levelup_side` | raw dính vệt chém xanh + bụi | cần quay lại |
| `skill_holy_banner_side` | raw dính vòng sáng hồng/vàng | cần quay lại |
| `skill_radiant_slash_side` | raw dính vệt chém hồng lớn | cần quay lại |
| `skill_charge_side` | raw đạt (score 8) | chưa export |
| `fx_respawn`, `fx_levelup`, `fx_charge` | chưa làm | cần dựng recipe `fx_layers.py` |
| `attack_side` export chính thức | accepted nhưng chưa export | chạy `video_to_sheet.py` khi user chốt convert |

## 3. Vì sao `run_side` t01 được chốt

**Kỹ thuật**: đây là lần export đầu tiên pass toàn bộ gate tự động trừ `colour` — và `colour` chỉ là màu key
(magenta) lem nhẹ ở chân (foreignMax 0.0417, 28/124 frame), sửa dứt điểm bằng `--despill` (steel-grey hoá
vùng lem, không đổi hình dạng). Mọi gate còn lại — `area` (kích thước không đổi), `feet` (chân không trượt),
`identity` (đúng nhân vật suốt clip), `zoom`, `turn`, `edge`, `background`, `extra` (không vật thể lạ),
`motion` — đều pass sạch. `motion_check.py` xác nhận loop khép kín, không flag, độ nhún 6.8% thân.

**So với hero_malik (KR1)**: `running` của malik chỉ là giậm chân tại chỗ biên độ rất nhỏ (5 hình thật, thân
gần như đứng yên) vì hero trong KR chỉ di chuyển quãng ngắn tới điểm chặn. Bản của holy_commander biên độ
lớn hơn hẳn — sải chân thật, người đổ về trước, cape bay mạnh — đây là **khác biệt phong cách có chủ ý**, không
phải lỗi: luật KR chỉ quy định "hero có 1 hình chạy, chỉ lật trái/phải" (`fal-image/classes/hero.md` §4),
không quy định biên độ chuyển động. Tiêu chí chốt là gate kỹ thuật (không đổi size, không trượt chân, không
vật thể lạ, loop khép kín), không phải sao chép đúng biên độ của KR.

## 4. Vì sao `attack_side` t04 được chọn, qua 3 lần quay

| Take | Mô tả chuyển động | Kết quả |
|---|---|---|
| t01 (gốc) | 1 chém duy nhất, 5s clip | Model tự vẽ thêm 1 vệt chém trắng/hồng lớn (vật thể lạ, bị cấm); gate `turn` fail 1 đoạn (frame 28-51, nhân vật quay lưng). Cảm giác rất chậm khi xem raw (1 chém trải trong 5s). |
| t03 | Sửa thành 3 chém (chéo xuống, chéo lên **có dồn trọng tâm ra sau + ngả người ra sau**, ngang) | **Tệ hơn hẳn**: gate `turn` fail ở **4 đoạn riêng biệt** (13-15, 21-23, 40-42, 50-69), gate `area` fail (vung kiếm quá rộng), và tư thế cuối **trôi hẳn sang 1 dáng khác** không về lại pose gốc (identity chỉ còn 0.32 so với master). Tốn $0.06. |
| **t04 (chốt)** | Sửa còn **2 chém**, **bỏ hẳn mọi câu lệnh về "ra sau"/"ngả lưng"**, cả 2 chém đều dồn người **về phía trước** (bước chân trước, nghiêng người tới); rút ngắn clip còn 3s; thêm câu "one continuous, fast, fluid... no slow motion, no pause between strikes" | Gate `area`/`feet`/`turn` vẫn báo fail (frame ~12-41) nhưng **đúng vào vùng có vệt chém trắng mờ** (artifact cũ vẫn còn, không phải lỗi mới) — đọc trực tiếp frame thật (đã tách + key nền, xem trong `tools/kr_compare`) xác nhận nhân vật **không thực sự quay lưng**, chân không trượt thật, chuyển động mượt. User xem frame thật và duyệt bằng mắt ("khá đẹp... giữ nhé") — chấp nhận dựa trên đánh giá trực quan, ghi đè gate (giống cách `run_side` ghi đè gate `colour`, nhưng lần này có xác nhận trực tiếp bằng mắt trên frame thật thay vì chỉ đọc contact sheet). |

**Nguyên nhân gốc rễ đã xác định** (đề xuất đưa vào `SKILL.md`, xem mục 5):
1. **Không bao giờ mô tả "dồn trọng tâm ra sau"/"ngả người ra sau"** — model h3-max-turbo đọc câu này thành
   lệnh **xoay cả người ra sau**, không phải nghiêng tại chỗ. Đây là nguyên nhân chính khiến t03 tệ hơn t01.
2. **Động tác "chém kiếm" luôn có xu hướng tự vẽ thêm 1 vệt mờ trắng/hồng hình lưỡi liềm cạnh lưỡi kiếm**, dù
   câu cấm đã rất tường minh ("no glowing arc", "no white crescent shape") — model vẫn làm. Vệt này còn làm
   gate `area`/`feet`/`turn` đọc sai theo (silhouette bị méo). Thói quen này coi như rủi ro thẩm mỹ cố hữu của
   model với hành động chém, cần xem frame thật trước khi loại bỏ một take chỉ vì gate báo fail.
3. **Combo 2 chém, khác hẳn hình dáng nhau** (1 chém chéo dốc + 1 chém ngang rộng) đọc nhanh và bớt cứng hơn
   hẳn so với đứng yên vung 1 chém — và ổn định hơn combo 3 chém (3 chém làm model dễ lạc hướng/trôi dáng hơn
   combo 2). Rút ngắn thời lượng clip (3s thay vì 4-5s mặc định) cũng giúp raw clip tự đọc nhanh hơn ngay cả
   trước khi qua bước `retime`.

**So với hero_malik**: `attack` của malik là 1 chém sạch tuyệt đối, không hiệu ứng gì vẽ vào clip thân, vì đó
là frame vẽ tay thật. Pipeline video-generation của chúng ta đổi lại: đánh đổi sự sạch sẽ tuyệt đối đó để lấy
chuyển động đa dạng/sinh động hơn, chấp nhận rủi ro còn sót 1 vệt chém mờ (cosmetic, có thể sửa sau bằng fx
layer riêng hoặc quay lại khi cần) — một lựa chọn có chủ ý, không phải hạ chuẩn.

## 5. Đề xuất cập nhật SKILL.md (CHƯA áp dụng — chờ duyệt)

`.claude/skills/video-sprite/SKILL.md` hiện **chưa bị đổi gì** (bản sửa trước đó đã bị revert theo yêu cầu).
Dưới đây là nguyên văn đề xuất, để duyệt trước khi áp dụng.

**Thêm vào "Retake translation" điểm 6** (sau dòng "h3-max-turbo habits seen so far..."):
> - Never describe backward weight or a backward lean ("shift weight onto the back foot", "lean the torso
>   back"): the model reads it as a cue to spin the whole body around, not lean in place. Seen on
>   holy_commander `attack` t03 vs t01/t04 (2026-10-20): this one phrase turned a single `turn` failure into
>   four separate turned-around windows plus a final pose that drifted away from the master entirely.
>   Describe every weight shift and lean as driving FORWARD only.
> - A sword "chop"/"swing" reliably draws a pale, semi-opaque slash-arc near the blade even when the prompt
>   explicitly forbids it. Treat this as a standing cosmetic risk of attack clips with this model, not
>   something the wording reliably suppresses. It also drags the `area`/`feet`/`turn` gates into false
>   failures (the arc distorts the measured silhouette) — before rejecting on gate output alone, read the
>   real converted frames and judge the actual body motion; a human visual accept can override gates that are
>   reading the arc, not a real defect.
> - A multi-strike combo (2 distinct strikes, each a different silhouette) reads faster and less stiff than a
>   single standing chop, and is more forgiving than 3 strikes. Keep each strike's footwork forward-only.
> - `--duration` has a hard floor per the number of distinct strikes asked for, and a stricter prompt does
>   not move that floor: cutting duration below what a combo needs makes the model drop a strike, not speed
>   up (holy_commander `attack` t05 and t06, 2026-10-20 — t06 kept the same short duration with a much
>   stricter "exactly two strikes" prompt and got the identical single-strike result). If frames are missing
>   a strike, raise `--duration` back up instead of rewording.
> - The "raw clip reads slow" worry is often a preview artifact: `retime --auto-oneshot` compresses a
>   one-shot to its class's standard game length regardless of raw duration (attack: ~0.7 s). Judge final
>   speed after export + Motion Lab, not from the raw preview.

**Thêm vào "Known limits"**:
> - A motion phrase describing backward weight or lean reads as "spin the body around" to h3-max-turbo;
>   keep attack footwork and lean forward-only.
> - A sword chop/swing draws a pale slash-arc that negatives alone do not reliably suppress, and that arc
>   also fails `area`/`feet`/`turn` by distorting the measured silhouette: read the real frames before
>   rejecting on the gate alone.
> - A single strike in a one-shot's raw clip reads slow/stiff; a 2-strike combo with two different
>   silhouettes reads better, but a shorter `--duration` is not a reliable way to speed up a multi-strike
>   combo — below the duration it actually needs, the model drops a strike instead (confirmed with and
>   without a stricter prompt). The raw clip's speed mostly stops mattering once `retime` runs.

Khi bạn duyệt, mình sẽ áp dụng đúng nguyên văn trên (hoặc bản bạn sửa) vào `SKILL.md`.

## 6. Thử nghiệm tăng tốc (t05) — không đạt, nhưng ra bài học rõ

User muốn 1 bản `attack` giống hệt t04 nhưng vung kiếm nhanh hơn ~40%, theo hướng rút ngắn thời lượng clip
(2s thay vì 3s, giữ nguyên toàn bộ lời mô tả) thay vì chỉ đổi lời mô tả tốc độ.

**Kết quả: không đạt.** Cùng `motion`/`negatives` với t04 (accepted), chỉ đổi `--duration` 3s → 2s — nhưng khi
đọc frame thật (đã tách + key nền trong `tools/kr_compare`, state `attack_fast`) thì 2 nhát chém riêng biệt
của t04 đã **gộp lại thành 1 động tác chém-rồi-theo-đà duy nhất**, không phải "2 nhát nhưng nhanh hơn". Gate
tự động cũng fail nặng hơn t04 (`area` 1.19x, `feet` trôi 8.2%, `turn` 3 đoạn, thêm cả `colour`).

**Bài học**: `--duration` có một ngưỡng dưới phụ thuộc số nhát chém yêu cầu. 3s đủ cho combo 2 chém của t04;
giảm xuống 2s (còn ~67%) không "nén nhanh" được combo đó, mà làm model bỏ bớt 1 nhát. Đề xuất đưa vào
`SKILL.md` ở mục 5 (chờ duyệt): trước khi tin một `--duration` ngắn hơn sẽ "tăng tốc" một combo nhiều nhát,
phải đọc frame thật và đếm lại đủ số nhát; nếu thiếu, lùi thời lượng về gần mức đã chạy được thay vì sửa câu
mô tả tốc độ.

**Thử lần 2 (t06) — vẫn 2s, prompt chặt hơn hẳn**: giữ nguyên `--duration 2.0`, viết lại `motion`/`negatives`
ép rất rõ "EXACTLY TWO separate, complete strikes... never collapse them into one swing" (lặp lại cả trong
`motion` lẫn `negatives`). Kết quả: **vẫn y hệt t05** — tách và key toàn bộ 35 frame thật (không chỉ xem
contact sheet thưa) xác nhận chỉ có 1 động tác chém + theo đà + về lại tư thế đứng, không có nhát thứ hai nào
xuất hiện ở bất kỳ đâu trong clip.

**Kết luận (trả lời câu hỏi "được hay không")**: **Không được.** Ở model này, ngưỡng thời lượng cho 1 combo 2
chém là một giới hạn cứng của bước tạo video — **không phải do câu lệnh chưa đủ rõ**, viết chặt cỡ nào ở 2s
cũng cho kết quả giống hệt. Đừng tiếp tục đốt tiền thử lại 2s với prompt khác.

**Hướng khác (đã xác nhận, không tốn thêm tiền)**: nỗi lo "clip raw trông chậm" phần lớn là **ảo giác của
bước xem preview**, không phải tốc độ thật trong game. Khi export chính thức (`video_to_sheet.py`), one-shot
luôn đi qua `retime --auto-oneshot` để nén về đúng thời lượng chuẩn của class — `attack` nén về ~0.7s, đòn
trúng tại 40% (`classes/hero.md` / `SKILL.md` "Timing defaults") — **bất kể clip raw dài 3s, 4s hay 5s**. Vậy
nên: cứ dùng `t04` (3s, đủ 2 chém sạch, đã accept) để export; nhiều khả năng sau khi nén về 0.7s nó đã đủ
nhanh, không cần clip raw nhanh hơn nữa. Nếu sau khi export + xem trong Motion Lab vẫn thấy chậm, chỉnh ở
bước retime (`oneshotMs`/timing trong `set_plan.json`) chứ không cần quay lại video.

Cả 2 kết luận đã đưa vào đề xuất ở mục 5 (chờ duyệt), chưa áp dụng vào `SKILL.md`.

## 7. Quyết định cuối cùng (2026-10-20)

User xác nhận: t06 vẫn chỉ ra 1 đòn — đúng như phân tích, model không đủ thời gian trong 2s để vẽ 2 đòn tách
biệt nên tự gộp lại. **Hướng được chọn**: không quay thêm video nữa; xử lý ngay trên frame đã có của t04 (đã
accept, đủ 2 đòn sạch) — bớt bớt frame thừa để animation tự đọc nhanh hơn, tương đương "retime" thủ công
ngay trong `tools/kr_compare`, không tốn thêm phí sinh video.

Đã dựng 2 phiên bản để so trực tiếp trong `tools/kr_compare`:
- **Phiên bản 1** (`attack`): t04 gốc, đủ 46 frame (3.07s@15fps).
- **Phiên bản 2** (`attack_fast_frames`): cùng nguồn t04, giữ 1/2 số frame (xen kẽ) → 23 frame (1.53s@15fps),
  nhanh gấp đôi, vẫn đủ 2 nhát chém thật vì không quay lại — chỉ bớt khung hình có sẵn.

**User đã xem và chốt phiên bản 2** ("cực kỳ ổn và đẹp"). Đây là bản sẽ dùng để export chính thức
(`video_to_sheet.py`), không phải t04 chưa bớt frame. Việc còn lại: chạy export trên đúng tập 23 frame này,
đưa về canvas 156×140 chuẩn hero, retime về khoảng 0.7s theo `classes/hero.md`.

(Ghi chú UI: viền màu trong `tools/kr_compare` ban đầu dùng màu đỏ cho mọi state "chưa export sang canvas
game", khiến dễ hiểu nhầm là lỗi QC — đã đổi sang màu vàng hổ phách cho đúng nghĩa "đang chờ export", tách
biệt khỏi lỗi QC thật.)
