"""Shared renderer for generators: drawings (layer -> strokes) -> smooth_simplify -> stacked layers + glow -> frames,
SVGs, GIFs. Every generator goes through the same clean-vector path as the rebuilt references."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from .profile import Profile, REPO
from .pipeline import strokes_cover_2x
from .smooth import smooth_simplify
from .bezier import raster_evenodd
from . import compose


def render_sequence(name, drawings, frame, size, layers, halo, gain, background=(18, 17, 24),
                    smooth=dict(sigma=3.0, corner_deg=145, merge_tol=0.8, min_area=4, close_px=0.8), out_root=None, meta=None):
    """drawings: list of dict(strokes={layer: [stroke, ...]}, frames=[frame indices shown], label=str)
    layers: {layer: rgb} bottom -> top. Returns (out dir, per-drawing stats)."""
    W, H = size
    out = Path(out_root) if out_root else REPO / f"lib-fx/_study/{name}"
    for sub in ("frames", "flat", "svg"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    h = dict(halo); h["gain"] = {str(f): g for f, g in gain.items()}
    pd = {"name": name, "source": {"frames": [0, 0]}, "background": list(background),
          "variants": {"fx": {"order": list(layers), "halo_model": "blur", "near_halo": False, "halo": h,
                              "layers": {l: {"colours": [c]} for l, c in layers.items()}}}}
    pp = out / "profile.json"
    pp.write_text(json.dumps(pd, indent=1))
    prof = Profile(pp)
    stats, last = [], -1
    for k, d in enumerate(drawings):
        covers, paths = {}, {}
        for l in layers:
            st = d["strokes"].get(l, [])
            if not any(p["op"] == "add" for p in st):
                continue
            pl, _ = smooth_simplify(strokes_cover_2x(st, frame, (H, W)), ss=2, **smooth)
            if pl:
                paths[l], covers[l] = pl, raster_evenodd(pl, (H, W))
        for f in d["frames"]:
            if covers:
                img, flat, _ = compose.composite(covers, list(layers), prof, "fx", f)
                (out / "svg" / f"{f:02d}.svg").write_text(compose.svg(paths, list(layers), prof, "fx", (H, W)))
            else:
                img = np.zeros((H, W, 3), np.uint8) + np.array(background, np.uint8)
                flat = np.zeros((H, W, 3), np.uint8) + 20
            Image.fromarray(img).save(out / "frames" / f"{f:02d}.png")
            Image.fromarray(flat).save(out / "flat" / f"{f:02d}.png")
            last = max(last, f)
        sil = np.zeros((H, W), bool)
        for c in covers.values():
            sil |= c >= 0.5
        stats.append(dict(drawing=k, label=d.get("label", ""), frames=d["frames"], area=int(sil.sum()), pieces=int(ndi.label(sil)[1])))
    Image.fromarray(np.zeros((H, W, 3), np.uint8) + np.array(background, np.uint8)).save(out / "frames" / f"{last + 1:02d}.png")
    seq = [Image.open(out / "frames" / f"{f:02d}.png") for f in range(last + 2)]
    seq[0].save(out / "preview.gif", save_all=True, append_images=seq[1:], duration=40, loop=0)
    seq[0].save(out / "preview_slow.gif", save_all=True, append_images=seq[1:], duration=125, loop=0)
    (out / "design.json").write_text(json.dumps(dict(meta or {}, stats=stats), indent=1, default=float))
    return out, stats
