# History: hero `centaur`

One row per generated still or video take. Prompts are in each still's `.json` sidecar.

| Date | Sheet/still | Ver | Model | Score | Verdict | Issue | Change for next version | Requested by |
|---|---|---|---|---|---|---|---|---|
| 2026-10-16 | master | v01 | gpt-image-2 | 7 | rejected | face and six-pack too detailed; outlines dark, not purple; blade edge pinkish (close to the magenta key) | simplify face/muscles, purple outline, blue-white edge | user: brief |
| 2026-10-16 | master | v02 | gpt-image-2 | 7 | rejected | same as v01 | same | user: brief |
| 2026-10-16 | master | v03 | gpt-image-2 | 8.5 | approved (idle) | 3/4 down-right, simple face (brow + violet eye slits + block beard), purple outlines, blue-white steel blade, big gauntlets, scythe upright; a few abdominal lines remain | - | user: "master_v03 ổn" |
| 2026-10-16 | master | v04 | gpt-image-2 | 6 | rejected | faces down-LEFT, scythe in the left hand | - | user: "master_v03 ổn" |
| 2026-10-16 | pose_run | v01 | gpt-image-2 (--ref master_v03) | 8.5 | approved (run) | gallop 3/4 down-right, scythe diagonal across the body in both hands, blade behind the shoulder; same design as the master; clean torso | - | user: "running: liềm xéo 2 tay" |
| 2026-10-16 | pose_run | v02 | gpt-image-2 (--ref master_v03) | 8 | rejected (user prefers v01: blade turned inward) | same pose, wider blade arc; more abdominal detail; blade close to the left edge | - | user: "running: liềm xéo 2 tay" |
| 2026-10-16 | pose_attack | v01 | gpt-image-2 (--ref master_v03) | 8.5 | approved (attack) | strike moment: two-handed horizontal sweep, blade out front toward the bottom-right, torso twisted, one front leg rearing | - | user: approved attack prompt |
| 2026-10-16 | pose_attack | v02 | gpt-image-2 (--ref master_v03) | 8 | rejected | same pose, blade lower and more downward; front leg lifted | - | user: approved attack prompt |
| 2026-10-16 | pose_death | v01 | gpt-image-2 (--ref master_v03) | 8 | rejected | collapsed on its side but the body lies diagonally across the frame | lie fully on its side, flat and horizontal along the ground | user: approved death prompt |
| 2026-10-16 | pose_death | v02 | gpt-image-2 (--ref master_v03) | 8 | rejected | slumped forward on folded legs (reads more kneeling than lying on its side), eyes closed, scythe in front | - | user: approved death prompt |
| 2026-10-16 | pose_death | v03 | gpt-image-2 (--ref master_v03) | 8.5 | rejected | lies flat on its side along a horizontal ground line, hooves and tail at the left, head resting at the right, eyes closed; scythe flat and parallel below | - | user: "death nằm nghiêng, sát đất hơn" |
| 2026-10-16 | pose_death | v04 | gpt-image-2 (--ref master_v03) | 8.5 | approved (death) | same, even flatter and longer; scythe shorter and tucked under | - | user: "death nằm nghiêng, sát đất hơn" |
| 2026-10-16 | idle_down_side | v01 | h3-max-turbo t01 (.work/down_side) | 8 | **final** | breathing idle, scythe upright; 43-frame loop @12 fps; registration anchor misread the 4 hooves + scythe butt (framing checked identical): registerArgs --max-anchor-error 100 | - | user: approved idle motion |
| 2026-10-16 | run_down_side | v01 | h3-max-turbo t01 (.work/down_side_run) | 6 | **final (to redo)** | gallop in place from pose_run_v01; user: the scythe is warped during the run; small gallop amplitude, hooves tinted greenish in some frames | retake later: rigid-weapon sentence + weapon-shape + no-blur, bigger gallop | user: "lưỡi liềm hướng về trước mặt" |
| 2026-10-16 | attack_down_side | v01 | h3-max-turbo t01 (.work/down_side) | 8 | **final** | wind-up over the head, horizontal sweep, back to idle; 8 frames, hit F4; violet-white smear on the blade kept (no --despill: it would grey the purple outlines and eyes) | - | user: approved attack motion |
| 2026-10-16 | death_down_side | v01 | h3-max-turbo t01 (.work/down_side) | 8 | **final** | struck, falls, lies flat matching pose_death_v04 (end frame pinned to it: new endStill option); 11 frames, holds the last | - | user: approved death motion |
