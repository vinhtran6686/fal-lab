# History: enemy `bandit`

One row per generated raw or video take. `final` = exported into `<sheet>/vNN/` (highest version is the one in use).
The exact prompt of each image raw is in its `.json` sidecar; of each video take in `<sheet>/clip_tNN.json`.
Reset 2026-10-14: every older sheet (image-sheet route) and the Luma/Kling tests were deleted; only the approved stills and the h3-max-turbo walk were kept.

| Date | Sheet | Ver | Model | Score | Verdict | Issue | Change for next version | Requested by |
|---|---|---|---|---|---|---|---|---|
| 2026-10-13 | master | v02 | gpt-image-2 | 8 | approved | 3/4 view turned right rather than a pure profile; belly a bit smaller than v01 | - | user: "chốt v02" |
| 2026-10-13 | master | view_side v01 | gpt-image-2 | 8 | approved | near-profile view reference (one eye, mask knot at the back) | - | pipeline |
| 2026-10-13 | master | view_front v01 | gpt-image-2 | 8 | approved | straight front view reference | - | pipeline |
| 2026-10-14 | walk_side (video test) | h3-max-turbo t01 | minimax/h3-max-turbo i2v 480P 5s | 7 | Needs Revision (best usable) | passed every gate; clean 10-frame loop @12fps, bob 4.8%; sword lowered and swung with the arm (master holds it upright); ~$0.08 | add "the sword stays upright in the right hand" fix clause; test in Motion Lab | user: "test walk_side 3 model" |
| 2026-10-14 | walk_side | v01 | h3-max-turbo t01 (.work/side) | 7 | **final** | exported from the take above: 10 frames @12 fps, loop, bob 4.8%, motion_check clean | sword should stay upright (next test) | user: "giữ assets h3-max-turbo" |
| 2026-10-14 | stills | view_back v01 | gpt-image-2 | 8 | approved | straight back view, mask knot + tails centered, no face, sword upright in the right hand (image right); blade a little straighter than the master's | - | user: "ok đồng ý" |
| 2026-10-14 | stills | view_up_side v01 | gpt-image-2 | 8 | approved | 3/4 back facing top-right, knot and ear edge visible, no face, sword upright on the right | - | user: "ok đồng ý" |
| 2026-10-14 | walk_down_side, walk_down, walk_up_side, walk_up | v01 | h3-max-turbo t01 (.work/<view>) | 7-8 | **final** | 4 clips ~USD 0.30; down passed every gate; the others failed only "feet" (the lifted foot of each step, 5.2-6.7% vs 5%) and were accepted after review; down_side lowers the sword sideways like walk_side | gait_loop could not tell one step from a stride ("ambiguous") and cut 2 strides (24-25 frames); stride=period rebuilt for down_side/down/up, not exported yet | user: "sinh video đi sau đó convert to frame" |
| 2026-10-14 | attack_side | v01 | h3-max-turbo t01 (.work/side_attack) | 7 | **final** | whirlwind spin: one 360° turn in place, blade held out, back to the ready stance; 11 frames @12 fps, 0.9 s, hit F7, cell 218x128; the model drew pink-tinted motion smears on the blade (colour/extra/key-spill gates): exported with --despill (smear turned steel grey) | if the grey smear reads badly in the playtest: retake with the no-blur clause | user: "giữ tâm nhân vật tại chỗ, giữ cây đao xoay vòng tròn tại chỗ" |
| 2026-10-14 | all sheets | v01 | (re-export, no API call) | - | **final** | reorganised into move/ and attack/; every action re-exported on ONE canvas 256x128 (was 128x128, attack widened to 218x128) with one body height 141 px @2x (attack_side was 134 px: rescaled x1.048); walks keep the approved 24-25 frame loops; .work pruned to 8.4 MB | - | user: "cố định 1 kích thước chuẩn cho move, attack, death" |
