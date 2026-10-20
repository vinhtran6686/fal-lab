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
| **`death_side` — t01 bớt frame (duyệt)** | ⏳ **duyệt, chưa export** | quỳ → ngã → nằm im, rõ ràng, không vật thể lạ; clip raw 5.18s đọc chậm như attack t01 — áp dụng đúng kỹ thuật bớt frame (78→39 hình, 2.60s@15fps), xem mục 8; còn thiếu bước `video_to_sheet.py` |

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

## 8. `death_side` — áp dụng kỹ thuật bớt frame, DUYỆT (2026-10-20)

Clip raw của `death_side` t01 (5.18s, 124 frame gốc @24fps) có đúng vấn đề như `attack` t01/t04: đọc rất chậm
khi xem thẳng clip raw, dù nội dung chuyển động (quỳ → ngã → nằm im) đã đúng và sạch từ lần quay đầu (history.md
2026-10-19: score 8, gate `feet`/`turn` từng đọc sai do tư thế ngã, không phải lỗi thật — chưa từng cần quay lại).

**Không quay video mới** — áp dụng thẳng kỹ thuật đã dùng cho `attack_fast_frames`:
1. Tách + key nền toàn bộ clip raw bằng `ffmpeg` + `sprite_pack.key_out()` (giống `attack`, không qua
   `sprite_set.py`/`video_to_sheet.py` — chỉ là xem trước trong `tools/kr_compare`): 78 hình @15fps (5.20s).
2. `decimate()` giữ 1 trong 2 hình (xen kẽ), không quay lại video: 78 → 39 hình (2.60s@15fps), nhanh gấp đôi.
3. Đọc lại từng hình quan trọng (frame 5/10/15/20/25/35) để chắc chắn không mất pha nào của cú ngã — vẫn thấy
   rõ: đứng → quỳ, đầu cúi, kiếm cắm đất → nằm sấp hẳn, không bị giật/thiếu khung hình chuyển tiếp.

**Kết quả**: user duyệt vì animation rõ ràng. `death_side` giờ ở cùng trạng thái với `attack_side` — đã chọn
xong tập frame cuối (`death_fast_frames`, 39 hình), còn thiếu bước `video_to_sheet.py` để đưa vào canvas
156×140 chuẩn game (retime còn lại ~0.3s theo `classes/hero.md`, tương tự attack).

**Vì sao kỹ thuật này dùng lại được cho cả 2 state**: khác với `attack` (phải quay 2-3 lần vì nội dung
chuyển động - đủ bao nhiêu nhát chém - phụ thuộc đúng `--duration` lúc sinh video), `death` chỉ có 1 động tác
liên tục (ngã), không có nguy cơ bị "gộp mất 1 pha" như combo nhiều nhát của attack. Nên bớt frame sau khi
quay xong là an toàn và đủ cho state này ngay từ lần quay đầu, không cần thử lại `--duration` ngắn hơn ở bước
sinh video.

## 9. Cả 3 skill cũ đều bị zoom nặng + nhân vật không ổn định — số liệu thật

User xem lại 3 clip `holy_banner`, `radiant_slash`, `charge` (bản gốc t01) và nhận ra 2 vấn đề chung: (1)
animation bị **zoom** vào nhân vật, (2) so với `hero_malik`, nhân vật **không ổn định** (tỉ lệ/dáng trôi theo
thời gian). Đọc lại đúng số trong `qc.json` của cả 3 (không chỉ nhìn sheet) xác nhận cả hai, nặng hơn cả ấn
tượng ban đầu:

| Clip (t01 gốc) | `area` median (ngưỡng pass: 0.72–1.32) | `area` max | `identity` min (ngưỡng warn <0.5) |
|---|---|---|---|
| `charge` | **2.535x** | 3.067x | 0.470 |
| `holy_banner` | **2.927x** | 4.008x | 0.554 |
| `radiant_slash` | **2.411x** | 3.260x | 0.452 |

Cả 3 đều zoom **sustained** (median đã ~2.4-2.9x, không phải 1 đỉnh nhọn thoáng qua) — tức phần lớn clip
nhân vật to hơn hẳn master, không phải lỗi đo ở 1-2 frame. `charge` từng được review cũ chấm "8 điểm, no gate
failed" — **verdict đó sai**, vì người review hồi đó chỉ nhìn sheet bằng mắt chứ không đọc `qc.json`; con số
thật cho thấy nó fail nặng ngang 2 clip kia.

**Nguyên nhân gốc (xác định qua thử nghiệm ở mục 10 bên dưới)**: cả 3 clip này đều có **hiệu ứng (ring,
sparks, slash arc) vẽ thẳng vào clip thân** — và chính hiệu ứng đó kéo theo zoom + mất ổn định, không phải 2
vấn đề tách rời. Logic: khi model vẽ thêm 1 vật thể lớn (vòng tròn sáng, vệt chém khổng lồ) đè lên nhân vật,
(a) diện tích pixel-không-trong-suốt tăng vọt → gate `area` đọc thành "zoom", và (b) silhouette bị hiệu ứng
che/biến dạng → gate `identity` so khớp với master kém đi → đọc thành "không ổn định". Thử nghiệm trực tiếp
(mục 10) tách riêng được: nhấc hiệu ứng ra khỏi prompt thì `area` trở lại bình thường ngay (xem `charge_v2`),
đưa hiệu ứng vào lại thì cả `area` lẫn `identity` cùng hỏng lại.

So với `hero_malik`: KR vẽ tay từng frame, không có khái niệm "camera" hay "hiệu ứng cháy nổ" trong frame thân
— nhân vật tuyệt đối không đổi kích thước giữa các trạng thái. Pipeline video-generation của chúng ta mô
phỏng một "cú quay phim" từ 1 ảnh tĩnh, và model có xu hướng tự thêm kịch tính (phóng to, hiệu ứng bùng nổ)
cho các hành động mang tính "quyền năng" (skill/charge) — đây là khác biệt về bản chất công cụ, không sửa
được 100% bằng cách viết prompt, chỉ giảm thiểu được.

## 10. Thiết kế lại `charge` — toàn bộ quá trình, từ v1 tới v4 (chốt)

### Tóm tắt kết quả

| Bản | Hiệu ứng trong prompt? | `area` median / max | Vấn đề | Trạng thái |
|---|---|---|---|---|
| v1 (gốc, "xung phong") | không (nhưng vẫn zoom) | 2.535x / 3.067x | thiết kế cũ (dash), zoom nặng, review cũ sai | thay thế hoàn toàn |
| v2 | **không** (body-only, đúng quy ước) | **1.212x / 2.381x** | sạch, chỉ còn 1 vệt mờ nhỏ + edge-touch 2 frame | giữ làm bằng chứng "bỏ hiệu ứng thì hết zoom" |
| v3 | **có** (lửa + blade-flash) | 1.317x / **6.135x** | vòng tròn lửa lớn tái xuất (~frame 46-72/107), giống hệt lỗi `holy_banner` cũ | user thích tổng thể, xin sửa thêm 1 điểm |
| v4 (**chốt**) | có (giữ nguyên v3) + nhân vật lao về trước | 1.421x / 6.732x | vòng tròn lửa **vẫn còn y hệt** (lần thứ 2 liên tiếp) | **user duyệt, chấp nhận giữ vòng tròn** |

### Diễn biến từng bước

1. **v1 → v2 (bỏ hiệu ứng khỏi prompt)**: đổi hẳn thiết kế theo mô tả tiếng Việt của user (cúi người vận sức
   → vung kiếm từ dưới lên), **cố tình không nhắc gì tới lửa/hiệu ứng** trong `motion`/`negatives` (đúng quy
   ước body-only của dự án: hiệu ứng là `fx_layers.py` riêng), thêm câu chống zoom rất mạnh ("camera như máy
   quay cố định trên chân máy, không bao giờ zoom"). Kết quả: gate `area` **pass** hẳn (1.212x so với 2.535x
   cũ) — xác nhận: bỏ hiệu ứng khỏi prompt là cách chắc chắn nhất để hết zoom.
2. **v2 → v3 (user muốn xem cả hiệu ứng để đánh giá tổng thể)**: user gửi 1 ảnh tham khảo kiểu vệt chém phẳng
   màu hồng-trắng (blade effect), yêu cầu thêm lửa trên kiếm lúc vận sức + vệt chém khi vung. Đưa hẳn mô tả
   hiệu ứng vào lại `motion`, kèm giới hạn kích thước rất cụ thể ("lửa chỉ bám theo cạnh lưỡi kiếm, không bao
   giờ to thành vòng tròn/quầng sáng quanh người"). Kết quả: đoạn vung kiếm (frame 6-46) và pose cuối (73-106)
   đẹp, đúng ý — nhưng đúng giữa clip (frame ~46-72) model tự vẽ **1 vòng tròn lửa lớn**, dù đã cấm rất rõ.
3. **v3 → v4 (thêm lao người về trước)**: giữ nguyên toàn bộ phần hiệu ứng của v3 (user duyệt phần này),
   chỉ sửa 1 điểm: nhân vật đứng yên 1 chỗ không giống đang tấn công. Thêm cụm "explodes upward AND FORWARD
   out of the crouch... as if closing the distance to strike a target just ahead of him" vào đúng đoạn vung
   kiếm. Kết quả: nhân vật dịch chuyển về phía trước rõ rệt — nhưng vòng tròn lửa **tái xuất hiện ở đúng vị
   trí tương đối trong clip** (~frame 46-72/107) lần thứ 2 liên tiếp, xác nhận đây là thói quen khó trị của
   model với mô-típ "chém + lửa", không liên quan gì tới câu lệnh lao người mới thêm.
4. **Quyết định**: user xem bản v4 trong `tools/kr_compare` (đã tách + key nền, animation thật) và duyệt
   ngay ("ok đẹp rồi → chốt v4"), **chấp nhận giữ vòng tròn** thay vì tiếp tục quay thử hoặc cắt frame loại
   bỏ đoạn đó (phương án mình đề xuất nhưng user không chọn).

### Cách mô tả hiệu ứng cho model để ra đúng ý — những gì có tác dụng và không

Rút từ 3 lần thử (v2 sạch hẳn, v3/v4 vẫn dính vòng tròn), đây là công thức đã dùng và mức độ hiệu quả của
từng phần:

1. **Tách DUY NHẤT 1 hành động thành các nhịp (beat) rõ ràng, có thứ tự** — hiệu quả tốt cho phần chuyển
   động thân, không ảnh hưởng tới hiệu ứng:
   > "...quickly pulls the sword up out of the ground, lowers his whole body into a low crouched coiled
   > stance... while he holds this low crouch in place for a beat, the blade catches fire... then he
   > explodes upward AND FORWARD out of the crouch... swinging the burning sword in ONE fast, powerful arc...
   > finishing with the blade held high... and HOLDS that final pose completely still."

   Viết đúng thứ tự "cúi → giữ → bật lên → giữ pose cuối" giúp model theo khá sát bố cục thời gian (dù đôi
   khi vẫn đảo thứ tự nhẹ, xem sheet v3: swing xuất hiện trước đoạn cúi người giữ lửa dọc).

2. **Mô tả hiệu ứng bằng từ ngữ "vector phẳng" đúng phong cách dự án, không dùng từ mơ hồ** — có tác dụng về
   màu sắc/hình dạng khi hiệu ứng CÓ xuất hiện đúng như mong muốn (đoạn vung kiếm ở v3/v4 nhìn khá giống ảnh
   tham khảo), nhưng KHÔNG ngăn được model tự thêm phần thừa (vòng tròn):
   > "the blade catches fire, small flat red-and-gold flames appearing along the blade's edge only" /
   > "a single flat bright pink-white blade-shaped flash releasing along the swing path... no wider than the
   > character's own height"

3. **Giới hạn kích thước + cấm rõ hình dạng cụ thể (ring/burst/halo/circle), lặp lại ở cả `motion` lẫn
   `negatives`** — đây là phần **không có tác dụng đáng kể**: dù lặp "never grows into a ring, a burst, a
   cloud or a halo around the character" ở cả 2 chỗ, vòng tròn vẫn xuất hiện y hệt ở cả v3 và v4. Rút ra:
   **với hành động kiểu "chém + lửa/quyền năng", mô tả phủ định (negative) về hình dạng hiệu ứng không đáng
   tin cậy với model này** — khác với các action khác (`run`, `attack`, `death`) nơi câu cấm "no effects, no
   trails" tỏ ra khá hiệu quả khi hiệu ứng không được MỜI vào prompt ngay từ đầu.

4. **Câu chống zoom rất mạnh, lặp lại, ví von cụ thể** — có tác dụng rõ rệt NHƯNG chỉ khi hiệu ứng không có
   trong prompt (v2); khi hiệu ứng có mặt (v3/v4), câu này không đủ sức giữ `area` trong ngưỡng vì chính
   hiệu ứng (vòng tròn) mới là nguồn gốc tăng diện tích, không phải "camera zoom" theo nghĩa đen:
   > "No camera zoom, no push-in, no pull-out, no dolly movement... the camera is fixed like a locked tripod
   > the entire time, exactly the same framing and the same character size from the first frame to the last."

**Kết luận thực dụng**: cách đáng tin cậy nhất để có 1 clip thân sạch, ổn định là **không nhắc tới hiệu ứng
trong prompt** (đúng quy ước body-only gốc của dự án — bằng chứng là `v2`, `run`, `attack`, `death` đều sạch
theo cách này). Khi cần hiệu ứng ngay trong clip để đánh giá ý tưởng tổng thể (như lần này), có thể đạt được
phần lớn ý muốn (lửa đúng chỗ, vệt chém đúng hình) nhưng phải **chấp nhận rủi ro model tự thêm 1 vật thể lớn
không mời** (ở đây là vòng tròn) — prompt viết chặt cỡ nào cũng chưa chặn được, đã thử 2 lần liên tiếp. Khi
chốt, có 2 lựa chọn còn mở: giữ nguyên (đã chọn, user chấp nhận) hoặc tách lại thành body-only (dùng `v2`) +
hiệu ứng lửa/blade-flash làm `fx_charge` riêng qua `fx_layers.py` sau này.

## 11. Phản hồi sau khi export (2026-10-20)

Đánh giá lại các trạng thái sau khi export attack, death, charge_v4, respawn lên canvas 176x140.

1. **charge_v4, vòng lửa**: user đồng ý đó là lỗi, vẫn giữ bản này. Lần sau tránh: hiệu ứng phải vừa khung hình
   (không vòng lớn quanh thân; bám lưỡi kiếm, nằm trong canvas). Khi làm lại, thử hiệu ứng nhỏ hơn hoặc fx_layers.
   Cũng thấy một hình lạ cạnh vai ở ~frame 5.
2. **attack, vệt chém trắng**: user thấy vệt này đọc như một đòn chém thật và thích. Ghi nhận ngược với mục 4/5 ở
   trên (đang coi là lỗi): với attack, vệt này chấp nhận được và không cần quay lại vì nó. Skill video-sprite sẽ do
   user sửa để cho phép; session này không sửa `SKILL.md`.
3. **respawn**: bản đảo despawn đúng về kỹ thuật nhưng đọc như một pho tượng cứng nhắc, không phải hero. Thiết kế
   lại hoàn toàn: quỳ, gục đầu vào thanh kiếm dựng đứng, cả hero màu xám; rồi hồi màu và đứng lên, như vừa được
   khôi phục. Cần clip mới (trả phí).
4. **levelup**: thiết kế mới, hero đứng và đấm một tay lên trời như chiến thắng/đạt thành tựu, ánh sáng chớp quanh
   người theo nhịp vung tay. Clip t01 cũ (giơ kiếm chào) không dùng.
5. **holy_banner, radiant_slash**: thiết kế lại hoàn toàn dựa trên bài học charge_v4 (mục 10): tách nhịp có thứ tự,
   chỉ dồn về trước, câu locked tripod, hiệu ứng nhỏ sát vũ khí hoặc nắm đấm. Ý tưởng chi tiết của từng skill
   chưa chốt, cần bàn với user trước khi quay.
6. Quy ước chung chưa đổi: `.work/` không có trong git, công thức cắt frame sẽ ghi ở
   `docs/issue-frame-recipe-sync.md` (user sẽ cập nhật); phiên này không cắt frame thêm.

## 12. Respawn: pose_respawn_v02 và clip rise t01 (2026-10-20)

Thiết kế respawn mới (mục 11.3) đã có ảnh đầu và take đầu. Chi tiết cách tạo, lý do chọn v02 và lý do ổn: `out/heroes/holy_commander/brief.md`, mục "Respawn pose".

1. Ảnh: 3 bản nháp (~0.042 USD), user chọn v02: "đẹp, ổn".
2. Clip: take `rise` t01 (h3-max-turbo, 4 s, 480P, ảnh đầu v02, ảnh cuối master_v07, ~0.06 USD). Xám giữ ~0.5 s, màu hồi xong ~1.2 s khi còn quỳ, đứng lên từ ~1.5 s, kết ở tư thế master. Không có vòng hay vật lạ, kích thước ổn định.
3. Cách viết prompt đã hiệu quả: nhịp đúng thứ tự (quỳ xám, hồi màu, ngẩng đầu, đứng lên, giữ), câu "locked tripod" của charge_v2, và chỉ nhắc một thay đổi ngoài chuyển động là chuyển màu. Model làm được chuyển xám sang màu, không cần hậu kỳ.
4. Còn lại: user duyệt t01, export `respawn_side` 176x140, `fx_respawn` nếu cần. Frame chưa cắt.

## 13. Fx bằng Python (2026-10-20)

Fx của levelup được làm bằng Python (0 USD) lên clip thân sạch; user duyệt 10 phiên bản và chọn v03. Quy trình đầy đủ: `docs/python-fx-recipe.md`;
tham số v03: `out/heroes/holy_commander/brief.md`. Chưa export, chưa cắt frame, chưa chạy gate `qc.json` cho levelup.
