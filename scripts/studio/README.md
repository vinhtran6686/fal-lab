# Lion Rig & Pose Studio

Local editor around the Puppet Kit: look at the rig, edit pivots / cut polygons / joint blend, pose the Lion, keep poses in an independent library.
Every picture is rendered by `scripts/puppet_kit/core.py` (`Rig.render`); the browser only draws overlays and handles. 0 USD, no image/video API.

## Start

```
python scripts/studio/server.py            # opens http://127.0.0.1:8765/
python scripts/studio/server.py --asset out/heroes/lion_brawler --port 8765 --no-browser
python scripts/studio/test_studio.py       # tests A-E on a temp copy of the asset
```
Needs numpy, Pillow, scipy (already required by the Puppet Kit). Stdlib server, bound to 127.0.0.1, POSTs need an `X-Studio` header.

## Use

| Want | Do |
|---|---|
| Select bone | Select (Q): click a pivot/bone, the hierarchy, or right-click for the menu |
| Pose a bone | Rotate (E) / Move (W): drag, or type in Inspector > Bone. Shift = whole numbers. Legs under IK: switch the leg to FK (IK panel) to rotate thigh/shin |
| Easiest | Panel "Tạo dáng nhanh" (top of the right column): turn on **Tay gần** or **Tay xa**, then drag or click ANYWHERE in the viewport: that hand follows the pointer, the body follows the hand. No aiming needed. Also preset buttons (crouch, claw forward, both arms forward) and plain sliders (sit down, lean, raise arm, bend elbow, tail) |
| Feet | Studio opens `rig_studio_v01.json` (the original rig + two IK target bones, `near_foot_target` / `far_foot_target`). In the quick panel press **Chân gần** / **Chân xa**, then drag anywhere: the foot goes to the pointer and the hips lower just enough, because the standing legs are already fully straight. Or use the sliders (Sang ngang, Nhấc lên) and the preset "Đứng rộng chân". `rig.json` is untouched; pick it in the rig box to go back |
| Start here | Press H (or "? Guide") for a 6-step guide in Vietnamese; the bar at the bottom of the viewport explains the active tool. The Studio draws its own pointer and rings the grab points (limb tips) and the bone under the pointer |
| Chain drag (default tool, "Grab") | Grab (C): drag a bone end (e.g. the hand). The arm joints turn to reach it; hips shift and the spine leans by the **body** amount (0 = body fixed, 1 = full), the top limb bone stretches (`sy`, up to max ×) when out of reach. Writes only rot / tx / ty / sy, so poses stay compatible. Legs are IK: use the Pivot tool on their target |
| Edit pivot / IK target / socket | Pivot tool (P): drag, or type in Inspector > Rig. This edits the **rig** |
| Edit cut polygon | Click a layer in Layers. Drag vertices, double-click an edge to add, Del removes, Inspector > Polygon has numbers. Self-crossing or <3 vertices are refused and reverted |
| Joint blend | Inspector > Joint deformation: slider + number per joint, before/after shown, reset per joint or all |
| Bend test | Inspector > Joint bend tester: pick joint, angle buttons 0-120°, slider, "Preview" strip, and one-click known-issue poses |
| Game size | Actual 1x / 2x and the corner box (H = 60 px @1x, shown 3x) |
| Pose library | + Save, double-click or Load, Update, Duplicate, Rename, Delete (to `poses/.trash/`), Export / Import JSON |
| Compare | pick A and B (working, rest, any pose), A ⇄ B flips the view (edits locked while comparing), Onion ghosts the other. "Saved rig ghost" overlays the rig before your edits |
| Save rig | Ctrl+S overwrites after confirmation with a backup in `source/rig/backup/`; "Save as new version" writes `rig_studio_vNN.json`; Reload drops unsaved edits |

Keys: C Grab, Q Select, E Rotate, W Move, P Pivot; Tab / Shift+Tab next / previous bone; arrows nudge the selected bone (Shift = 5); H guide, F fit, Ctrl+Z / Ctrl+Shift+Z, Ctrl+S, Del (vertex > focused library pose > reset bone). Wheel zoom, Space/Alt/middle-drag pans. Panels resize by their splitters.

Render: drags use a 0.3x draft with fewer skin solver rounds (~110 ms); the sharp render (Quality, 0.5x default, ~0.5 s) runs only 0.45 s after you stop and never while a drag is on. The game-size box is rendered in the same request. The status bar shows size and ms.

## Data

- Poses: `out/heroes/lion_brawler/poses/<id>.json` + `<id>.png`. Fields: `id, name, description, created, updated, rig {file, topology, hash, bones}, bones {name: {rot,tx,ty,sx,sy,shx}}, ik {upper: false = FK}`. Only non-default channels are stored. Never touches `anims/*.json` or `rig.json`.
- Working state autosave: `.work/studio_autosave.json` (git-ignored), offered for restore on start.
- Overlay data: pivots and parent links are stored; bone length/direction is derived (child pivot, or skin tip) and labelled so. Polygons and skin bands are drawn with the owning bone's rigid transform: exact at rest, approximate where a skin bends.
