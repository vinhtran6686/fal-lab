# Brief: enemy `bandit`

| Field | Value |
|---|---|
| Request | Tạo enemy đạo tặc, có đeo khăn đen che nửa mặt, không cần thấy rõ khuôn mặt (chỉ mắt + khăn), đầu trọc, bụng to, mặc đồ đen, sử dụng đao |
| Mode | default (master checkpoint); user approved master v02 on 2026-10-13 |
| Class / level / archetype | enemy / 1 / melee |
| Canvas | 256 x 128 at 1x (512 x 256 @2x), the same for every action; body 138 px @2x; icon 128 px |
| Approved master | `design/master_v02.png` (user: "chốt v02") |
| View references | `design/view_side_v01.png` (side), `design/view_front_v01.png` (front), `design/view_up_side_v01.png` (3/4 back), `design/view_back_v01.png` (back): approved 2026-10-14 |
| Move speed | from the video walk_side v01 (meta.json); tune in the playtest |

## Slots (reuse verbatim in every prompt)
- `{design}`: a stocky bald bandit with a big round belly and a shiny shaved head, a black cloth mask covering the lower half of the face so only two narrow eyes show, wearing a black sleeveless tunic, baggy black trousers, a dark red cloth sash tied around the belly, brown leather wrist wraps and boots, holding a large curved single-edged broadsword (dao) with a wide steel blade in the right hand, drawn with chibi-like squat proportions: an oversized head about one third of the total height, a huge round belly, very short thick legs and big hands
- `{leg_anchor}`: He holds the sword in his RIGHT hand, so his RIGHT leg is the leg on the sword side and his LEFT leg is the leg on the side without the sword
- `{walk_poses}`: biped preset under the leg standard (leading leg L,R,L,R,L,R,L,R)
- `{attack}`: a whirlwind spin in place: keeps his center on the spot and spins one full 360° turn with the broadsword held out, the blade sweeping a full circle around him, then back to the ready stance (user 2026-10-14: "giữ tâm nhân vật tại chỗ, giữ cây đao xoay vòng tròn tại chỗ, thấy lưỡi đao được xoay"; replaces the diagonal slash)
- `{death}`: knocked backward off his feet by a hit, flies back and lands flat on his back, the broadsword flung out of his hand and landing away from him (user: "nảy về sau, ngã về sau, vung mất đao")
