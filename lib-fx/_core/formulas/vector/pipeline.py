"""rebuild(): reference frame -> layer masks -> strokes (cached) -> smooth & simplify -> stacked render, per frame.

Outputs in profile.out_dir():
  strokes/<v>_<NN>.json   fitted strokes per layer + frame geometry (the slow step, reused unless --refit)
  frames/<v>_<NN>.png     final image (gradient + halo)      flat/<v>_<NN>.png   flat colours only
  svg/<v>_<NN>.svg        one <path> per layer (the clean vector result)
  report.json             per layer: iou (visible part vs target), anchors, corners, kinks, wobble, curv_var"""
import json
import numpy as np
import cv2
from PIL import Image
from . import measure, compose
from .frames import make_frame, PolarFrame, LinearFrame
from .fit import fit_layer
from .strokes import to_path
from .bezier import raster_union, raster_evenodd
from .smooth import smooth_simplify
from .metrics import iou, path_fairness


def frame_from_dict(d):
    if d["type"] == "polar":
        return PolarFrame(tuple(d["centre"]), d["seam"], rmax=d.get("rmax", 430.0))
    return LinearFrame(tuple(d["origin"]), d["angle"], d["length"], d["half_width"])


def frame_to_dict(fr):
    d = fr.to_dict()
    if fr.kind == "polar":
        d["rmax"] = fr.nv * fr.dv
    else:
        d["length"], d["half_width"] = fr.nu * fr.du, fr.nv * fr.dv / 2
    return d


def strokes_cover_2x(strokes, frame, shape):
    """Coverage of a layer's strokes at 2x (the smoothing step works at 2x)."""
    sc = lambda segs: [tuple(np.asarray(q) * 2 for q in s) for s in segs]
    H, W = shape
    add = raster_union([sc(to_path(p, frame)) for p in strokes if p["op"] == "add"], (H * 2, W * 2), 4)
    cut = raster_union([sc(to_path(p, frame)) for p in strokes if p["op"] == "cut"], (H * 2, W * 2), 4)
    return np.clip(add - cut, 0, 1)


def fit_frame(prof, v, f):
    rgb = measure.load_frame(prof, v, f)
    if rgb is None:
        return None
    masks = measure.layer_masks(prof, v, rgb)
    U = np.zeros(rgb.shape[:2], bool)
    for m in masks.values():
        U |= m
    if U.sum() < 30:
        return {"empty": True}
    fr = make_frame(prof.var(v).get("frame") or prof.get("frame"), U)
    groups = prof.groups(v)
    T = measure.full_targets(masks, groups)
    fp = prof.get("fit")
    layers = {}
    for l in prof.order(v):
        tgt = compose.underlay_target(T, prof.order(v), groups, l, fp["underlay_px"])
        if tgt.sum() < 12:
            continue
        layers[l] = fit_layer(tgt, fr, fp["passes"], fp["min_area"], fp["min_gain"], tuple(fp["axes"]), tuple(fp.get("edge_bias", (0, 0))))
    return {"frame": frame_to_dict(fr), "shape": list(rgb.shape[:2]), "layers": layers}


def rebuild(prof, frames=None, variants=None, refit=False, log=print):
    out = prof.out_dir()
    for sub in ("strokes", "frames", "flat", "svg"):
        (out / sub).mkdir(exist_ok=True)
    rp = out / "report.json"
    report = json.loads(rp.read_text()) if rp.exists() else {}
    for v in variants or prof.variants:
        for f in frames or prof.frames():
            sp = out / "strokes" / f"{v}_{f:02d}.json"
            if refit or not sp.exists():
                data = fit_frame(prof, v, f)
                if data is None:
                    continue
                sp.write_text(json.dumps(data))
            data = json.loads(sp.read_text())
            if data.get("empty"):
                continue
            fr, shape = frame_from_dict(data["frame"]), tuple(data["shape"])
            covers, paths = {}, {}
            for l in prof.order(v):
                if l not in data["layers"] or not data["layers"][l]:
                    continue
                pl, _ = smooth_simplify(strokes_cover_2x(data["layers"][l], fr, shape), ss=2, **prof.smooth(v))
                paths[l], covers[l] = pl, raster_evenodd(pl, shape)
            if not covers:
                continue
            img, flat, vis = compose.composite(covers, prof.order(v), prof, v, f)
            Image.fromarray(img).save(out / "frames" / f"{v}_{f:02d}.png")
            Image.fromarray(flat).save(out / "flat" / f"{v}_{f:02d}.png")
            (out / "svg" / f"{v}_{f:02d}.svg").write_text(compose.svg(paths, prof.order(v), prof, v, shape))
            rgb = measure.load_frame(prof, v, f)
            T = measure.full_targets(measure.layer_masks(prof, v, rgb), prof.groups(v))
            for l in paths:
                r = dict(iou=round(iou(vis[l], T[l]), 3), **path_fairness(paths[l]))
                report[f"{v}_{f:02d}_{l}"] = r
                log(f"{v}_{f:02d}_{l} {r}")
    fresh = json.loads(rp.read_text()) if rp.exists() else {}  # merge: several rebuilds (variants) may run in parallel
    fresh.update(report)
    rp.write_text(json.dumps(dict(sorted(fresh.items())), indent=1))
    return report
