# Lion Rig & Pose Studio

Local editor around the Puppet Kit: pose the Lion, configure joints, joint limits and muscle links, edit pivots / cut polygons / joint blend, keep poses in an independent library.
Every picture is rendered by `scripts/puppet_kit/core.py` (`Rig.render`); the browser only draws overlays and edits data. 0 USD, no image/video API.

AI recipes: [docs/puppet-studio-ai-guide.md](../../docs/puppet-studio-ai-guide.md). Concepts for the user: [docs/puppet-studio-concepts.md](../../docs/puppet-studio-concepts.md).
Full guide (Vietnamese, schema for `limit` and `links`, rules for AI): [docs/puppet-studio.md](../../docs/puppet-studio.md).

```
python scripts/studio/server.py              # http://127.0.0.1:8765/  (opens rig_studio_v01.json when present)
python scripts/studio/server.py --rig rig.json --port 8765 --no-browser
python scripts/studio/test_studio.py         # 52 tests on a temp copy of the asset
```
Needs numpy, Pillow, scipy (already required by the Puppet Kit). Stdlib server on 127.0.0.1; POSTs need an `X-Studio` header.

## Interaction
- **Click** a joint dot or the picture itself = select (never changes the pose). **Press and drag** = move (hand reaches, body follows; legs move their IK target; hips slide the body). **Click outside** = deselect.
- Tools: V pose, E rotate, W slide, P edit rig (pivots, IK targets, sockets), A place muscle anchors. Esc leaves a mode / deselects. Tab next joint, arrows nudge, F fit, H guide, Ctrl+Z / Ctrl+Shift+Z, Ctrl+S save rig.
- Left: Layer tab (thumbnails, type, bound bone, polygon edit, solo) and Bone tab (tree, IK/FK, sockets). Right tabs: 1 Pose, 2 Joints & limits, 3 Muscles, 4 Edit rig, 5 Test. Bottom: pose library + compare.

## Data
- Poses: `out/<class>/<id>/poses/<id>.json` + `.png`; only non-default channels; never touches `rig.json` or `anims/*.json`.
- `bone.limit.rot = [min, max]`: enforced on edits (drag, sliders, keys, presets, solver), never on load/import/undo.
- `rig.links`: muscle links (shoulder slides out, chest near the anchors follows; or `carry`: the whole body follows). Rendered by the Puppet Kit; see the doc.
- Rig saves: Ctrl+S overwrites after confirmation with a backup in `source/rig/backup/`; "Lưu bản mới" writes `rig_studio_vNN.json`.
- Working state autosave: `.work/studio_autosave.json` (git-ignored), offered for restore on start.
