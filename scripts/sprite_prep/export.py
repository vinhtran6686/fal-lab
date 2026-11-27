"""From a sequence (chosen frames, edited) to the asset's sheet, through scripts/video_to_sheet.py.

sequence (prep/<hero>/<action>.seq.json):
  {"version": 1, "loop": false,
   "segments": [{"clip": "attack_t01", "keep": [0, 2, 4], "ms": [83, 83, 83], "dx": 0, "dy": 0}, ...],
   "hit": {"seg": 0, "k": 5} | null}
Segments may come from different clips (takes) of the same hero: they are played in order. dx, dy nudge a segment
(window pixels) so two takes join without a jump.

Scale: video_to_sheet does not resize to a target height, so every frame is scaled here by ONE factor per hero:
body_2x / body_px (the hero's standing height in the clips, measured on frame 0 of its takes, which all start from the
same lineup image), so every action of a hero has the same body size. The canvas (`cell`) is set by the first export of an
asset and shared by every action: `fit()` measures what all prepared actions of the hero need BEFORE the first export.
"""
from __future__ import annotations

import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from .edits import render
from .workspace import ROOT, Workspace, read_json, write_json

ALPHA = 24
BASELINE = 0.12


def items(seq: dict) -> list[dict]:
    out = []
    for si, s in enumerate(seq.get("segments", [])):
        ms = s.get("ms") or [83] * len(s["keep"])
        for k, f in enumerate(s["keep"]):
            out.append({"clip": s["clip"], "f": int(f), "ms": int(ms[k]), "dx": int(s.get("dx", 0)), "dy": int(s.get("dy", 0)), "seg": si, "k": k})
    return out


def hit_position(seq: dict) -> int | None:
    h = seq.get("hit")
    if not h:
        return None
    for i, it in enumerate(items(seq)):
        if it["seg"] == h.get("seg") and it["k"] == h.get("k"):
            return i
    return None


def hero_body_px(ws: Workspace, hero: str) -> float:
    cfg = ws.cfg["heroes"][hero]
    if cfg.get("body_px"):
        return float(cfg["body_px"])
    vals = [ws.split_info(c, hero)["body_px"] for c in ws.cfg["clips"] if hero in ws.clip_heroes(c) and ws.split_info(c, hero)]
    if not vals:
        raise RuntimeError(f"{hero}: no split clip yet, the body size is unknown")
    return float(np.median(vals))


def hero_scale(ws: Workspace, hero: str) -> float:
    return ws.cfg["heroes"][hero].get("body_2x", 168) / hero_body_px(ws, hero)


def finished_frame(ws: Workspace, hero: str, it: dict, scale: float) -> tuple[Image.Image, tuple[float, float]]:
    info = ws.split_info(it["clip"], hero)
    img = render(ws, it["clip"], hero, it["f"])
    if it["dx"] or it["dy"]:
        sh = np.zeros_like(img)
        dx, dy = it["dx"], it["dy"]
        h, w = img.shape[:2]
        sh[max(0, dy):min(h, h + dy), max(0, dx):min(w, w + dx)] = img[max(0, -dy):min(h, h - dy), max(0, -dx):min(w, w - dx)]
        img = sh
    im = Image.fromarray(img, "RGBA")
    if abs(scale - 1) > 1e-4:
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
    ax, ay = info["anchor"]
    return im, (ax * scale, ay * scale)


def _extent(im: Image.Image, anchor) -> tuple[float, float, float, float]:
    box = im.getchannel("A").point(lambda v: 255 if v > ALPHA else 0).getbbox()
    if not box:
        return 0, 0, 0, 0
    ax, ay = anchor
    return ax - box[0], box[2] - ax, ay - box[1], box[3] - ay


def fit(ws: Workspace, hero: str, actions: list[str] | None = None) -> dict:
    """What canvas every prepared action of `hero` needs (1x), against the configured cell."""
    scale = hero_scale(ws, hero)
    cell = ws.cfg["heroes"][hero]["cell"]
    need_l = need_r = need_u = need_d = 0.0
    per = {}
    for a in actions or list(ws.cfg["actions"][hero]):
        seq = ws.seq(hero, a)
        if not seq:
            continue
        l = r = u = d = 0.0
        for it in items(seq):
            im, anc = finished_frame(ws, hero, it, scale)
            e = _extent(im, anc)
            l, r, u, d = max(l, e[0]), max(r, e[1]), max(u, e[2]), max(d, e[3])
        need_w = math.ceil(2 * max(l, r) / 2 / 4) * 4        # @1x, symmetric about the pivot
        need_h = math.ceil(max(u / (1 - BASELINE), d / BASELINE) / 2 / 4) * 4
        per[a] = {"w": need_w, "h": need_h, "fits": need_w <= cell[0] and need_h <= cell[1]}
        need_l, need_r, need_u, need_d = max(need_l, l), max(need_r, r), max(need_u, u), max(need_d, d)
    w = max([cell[0]] + [p["w"] for p in per.values()])
    h = max([cell[1]] + [p["h"] for p in per.values()])
    return {"cell": cell, "suggest": [w, h], "per_action": per, "scale": round(scale, 4)}


def body_report(ws: Workspace, hero: str) -> dict:
    """Body size of the first frame of every prepared action (@2x after the hero scale): they should agree within 4%."""
    scale = hero_scale(ws, hero)
    rows = {}
    for a in ws.cfg["actions"][hero]:
        seq = ws.seq(hero, a)
        if not seq or not seq.get("segments"):
            continue
        it = items(seq)[0]
        im, _ = finished_frame(ws, hero, it, scale)
        al = np.asarray(im)[..., 3] > 127
        ys = np.nonzero(al.any(axis=1))[0]
        rows[a] = {"area": int(al.sum()), "height": int(ys.max() - ys.min() + 1) if len(ys) else 0}
    if rows:
        ref = float(np.median([r["area"] for r in rows.values()]))
        for r in rows.values():
            r["vs_median"] = round(math.sqrt(r["area"] / ref), 3) if ref else 0
            r["ok"] = abs(r["vs_median"] - 1) <= 0.04
    return {"scale": round(scale, 4), "actions": rows}


def export(ws: Workspace, hero: str, action: str, asset_out: Path | None = None) -> dict:
    seq = ws.seq(hero, action)
    if not seq or not items(seq):
        raise RuntimeError(f"{hero}/{action}: no frames chosen yet")
    hcfg = ws.cfg["heroes"][hero]
    a = ws.action(hero, action)
    asset = Path(asset_out) if asset_out else ROOT / hcfg["asset"]
    scale = hero_scale(ws, hero)
    its = items(seq)
    work = Path(tempfile.mkdtemp(prefix="sprite_prep_"))
    try:
        d = work / "fin" / "act"
        d.mkdir(parents=True)
        frames = [finished_frame(ws, hero, it, scale) for it in its]
        W = max(im.width for im, _ in frames)
        H = max(im.height for im, _ in frames)
        anchor = frames[0][1]
        for k, (im, anc) in enumerate(frames):
            c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            c.paste(im, (round(anchor[0] - anc[0]), round(anchor[1] - anc[1])))
            c.save(d / f"f_{k:03d}.png")
        dur = [it["ms"] for it in its]
        loop = bool(seq.get("loop", a.get("loop", False)))
        sel = {"start": 0, "endExclusive": len(its), "durationsMs": dur, "loopPolicy": "loop" if loop else "oneshot", "fps": 24}
        hp = hit_position(seq)
        if hp is not None:
            sel["impactMs"] = int(sum(dur[:hp]))
        write_json(work / "sel.json", sel)
        write_json(work / "fin.json", {"anchor": [anchor[0], anchor[1]]})
        state = {"actions": {"act": {"status": "done", "output": {"take": 1}, "takes": [{"take": 1, "clip": {"path": str(ws.clip_path(its[0]["clip"]))},
                 "route": "supplied", "stages": {"finished": {"framesDir": "fin/act", "metadata": "fin.json"}, "selection": {"selection": "sel.json"}}}]}}}
        write_json(work / "set_state.json", state)
        cmd = [sys.executable, str(ROOT / "scripts" / "video_to_sheet.py"), "--set", str(work), "--action", "act", "--asset", str(asset),
               "--id", hero, "--kind", hcfg.get("kind", "hero"), "--sheet", a["sheet"], "--cell", f"{hcfg['cell'][0]}x{hcfg['cell'][1]}"]
        if not hcfg.get("shadow", True):
            cmd.append("--no-shadow")
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            raise RuntimeError((r.stderr or r.stdout).strip()[-1200:])
        meta_p = asset / "meta.json"
        meta = read_json(meta_p, {}) or {}
        st = (meta.get("states") or {}).get(a["sheet"])
        if st is not None:
            st["prep"] = {"ws": ws.id, "action": action, "sequence": f"prep/{hero}/{action}.seq.json",
                          "clips": sorted({it["clip"] for it in its}), "scale": round(scale, 4)}
            st["source"] = Path(ws.clip_path(its[0]["clip"])).resolve().relative_to(ROOT).as_posix()
            st["video"] = {"route": "sprite_prep", "ws": ws.id}
            write_json(meta_p, meta)
        return {"ok": True, "out": (r.stdout or "").strip()[-600:], "warn": (r.stderr or "").strip()[-600:], "asset": str(asset)}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def export_order(ws: Workspace, hero: str, actions: list[str]) -> list[str]:
    """First export of an asset fixes its body area: start with a one-shot whose first frame is the standing pose
    (attack), never a loop (a loop's body area is measured over all its frames)."""
    def key(a):
        loop = ws.action(hero, a).get("loop")
        return (1 if loop else 0, 0 if a == "attack" else 1)
    return sorted(actions, key=key)
