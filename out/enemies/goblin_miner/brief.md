# goblin_miner

Request (2026-10-19): `--enemy --tier S --role melee` "goblin thợ mỏ, mũ bảo hộ có đèn, cuốc chim cầm tay phải, túi đá trên lưng"

- Class: enemy (walking), tier S, `{H}` 40, canvas 92x80 (profile unit), role melee, skills: none
- `{body}`: biped; weapon hand: right
- `{design}`: A small hunched goblin miner about 3 heads tall and top-heavy (big head with long pointed ears, huge hands and shoulders, short bowed legs), muted olive-green skin, a dull grey-brown work tunic and a round yellow-brown safety helmet with one small lamp on the front of it (a flat orange-yellow lamp shape, no glow), a short pickaxe held upright in its RIGHT hand, and a lumpy sack of grey rocks carried on its back; muted olive and brown palette with one warning accent of orange on the helmet lamp.
- `{attack}`: an in-place downward pick swing; `{death}`: collapses forward in place, the rock sack spilling
- `{rim}` muted stone-grey, `{badge}` muted khaki

## Asset manifest
| Asset | Từ | Loại | Trạng thái | Ghi chú |
|---|---|---|---|---|
| master (= idle) | fal-image | ảnh tĩnh | ✅ v01 | chốt 2026-10-19 |
| view_front | fal-image | ảnh tĩnh | ⏳ | v01 |
| view_back | fal-image | ảnh tĩnh | ⏳ | v01 |
| icon | fal-image | ảnh tĩnh | ⏳ | v01, đã pack vào ui/icon |
| walk_side | video-sprite | loop | ❌ | |
| walk_down | video-sprite | loop | ❌ | |
| walk_up | video-sprite | loop | ❌ | |
| attack_side | video-sprite | one-shot | ❌ | |
| death_side | video-sprite | one-shot | ❌ | |
| thorn_side, thorn_free_side | video-sprite | loop + one-shot | ⏭ | later, until the game has a vine tower |

Estimate: 4 stills x ~USD 0.014 = ~USD 0.06 + 5 clips x ~USD 0.08 = ~USD 0.40 + retakes.
