"""Workspaces of the sprite prep tool: where the clips are, which heroes they hold, where edits and sequences are saved.

A workspace is either
  * a lineup folder (out/<class>/_lineups/<name>/) with a `sprite_prep.json` (grid, heroes, clips, actions), or
  * a single asset folder (out/<class>/<id>/) whose source/video/ holds clips of that one character (grid 1x1); its
    config is built from the clip names when it has no `sprite_prep.json` yet.

Files (all paths inside the workspace folder):
  sprite_prep.json                      config (tracked)
  prep/<hero>/<clip>.edits.json         non-destructive clean-up of one hero in one clip (tracked): denoise + ops per source frame
  prep/<hero>/<action>.seq.json         the chosen frames of one action (tracked): segments of (clip, source frames, ms), hit
  .work/prep/<clip>/<hero>/raw/fNNN.png every source frame of the clip, cut, keyed and anchored (cache, git-ignored, rebuilt by split)
  .work/prep/<clip>/<hero>/edited/      rendered frames after the edits (cache)
Source frame indices are the clip's native frames (0-based), so a change of sampling never orphans an edit.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out"
TIER_CELL = {"S": ([104, 92], 80), "M": ([176, 140], 120), "L": ([220, 196], 168), "XL": ([300, 280], 240), "XXL": ([400, 380], 340)}
SPLIT_KEYS = ("cols", "rows", "x_margin", "pad", "gap")


def read_json(p: Path, default=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(p: Path, data) -> None:
    """Atomic write (temp file + replace) so a crash never leaves half a file."""
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    os.close(fd)
    Path(tmp).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)


def rel(p: Path) -> str:
    try:
        return Path(p).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def _clip_action(stem: str) -> str:
    """attack_side_attack_t04 -> attack_side_attack ; run_side_t01 -> run_side"""
    return re.sub(r"_t\d+$", "", stem)


def _single_asset_config(asset: Path) -> dict | None:
    vids = sorted((asset / "source" / "video").glob("*.mp4")) + sorted((asset / "source" / "video").glob("*/clip.mp4"))
    if not vids:
        return None
    meta = read_json(asset / "meta.json", {}) or {}
    cell = meta.get("cell") or TIER_CELL["M"][0]
    hero = asset.name
    clips, actions = {}, {}
    for v in vids:
        cid = v.parent.name if v.name == "clip.mp4" else v.stem
        clips[cid] = {"path": v.relative_to(asset).as_posix()}
        act = _clip_action(cid)
        m = re.match(r"(.*?_side)(?:_|$)", act)      # attack_side_attack -> attack_side ; skill_side_skill_x -> skill_x_side
        sheet = m.group(1) if m and not act.startswith("skill_side_") else (re.sub(r"^skill_side_", "", act) + "_side" if act.startswith("skill_side_") else act + "_side")
        a = actions.setdefault(act, {"sheet": sheet, "takes": [], "pick": cid})
        a["takes"].append(cid)
        if "run" in act or "walk" in act or "idle" in act:
            a["loop"] = True
    return {"version": 1, "title": f"{asset.parent.name}/{hero} (one asset)", "kind": "asset",
            "grid": {"cols": 1, "rows": 1, "x_margin": 0.0, "pad": 64, "gap": 14}, "fps": 24,
            "heroes": {hero: {"asset": rel(asset), "kind": meta.get("kind", asset.parent.name.rstrip("s")), "cell": cell,
                              "body_2x": meta.get("body_height_2x") or 2 * {104: 40, 176: 60, 156: 60, 220: 84}.get(cell[0], 60),
                              "shadow": True}},
            "clips": clips, "actions": {hero: actions}, "auto": True}


class Workspace:
    def __init__(self, folder: Path, cfg: dict):
        self.dir = Path(folder)
        self.cfg = cfg
        self.id = rel(self.dir)

    # ---- discovery -------------------------------------------------------------------------------------------
    @staticmethod
    def discover() -> list["Workspace"]:
        found = []
        for f in sorted(OUT.glob("*/_lineups/*/sprite_prep.json")):
            cfg = read_json(f)
            if cfg:
                found.append(Workspace(f.parent, cfg))
        for asset in sorted(p for p in OUT.glob("*/*") if p.is_dir() and not p.name.startswith(("_", "."))):
            cfg = read_json(asset / "sprite_prep.json") or _single_asset_config(asset)
            if cfg:
                found.append(Workspace(asset, cfg))
        return found

    @staticmethod
    def load(ws_id: str) -> "Workspace":
        folder = (ROOT / ws_id).resolve()
        if ROOT not in folder.parents:
            raise ValueError("workspace outside the repo")
        cfg = read_json(folder / "sprite_prep.json") or _single_asset_config(folder)
        if not cfg:
            raise ValueError(f"no workspace at {ws_id}")
        return Workspace(folder, cfg)

    def save_config(self) -> None:
        self.cfg.pop("auto", None)
        write_json(self.dir / "sprite_prep.json", self.cfg)

    # ---- names and paths -------------------------------------------------------------------------------------
    @property
    def grid(self) -> dict:
        return self.cfg["grid"]

    @property
    def heroes(self) -> list[str]:
        return list(self.cfg["heroes"])

    def clip_path(self, clip: str) -> Path:
        return self.dir / self.cfg["clips"][clip]["path"]

    def clip_heroes(self, clip: str) -> list[str]:
        return self.cfg["clips"][clip].get("heroes") or self.heroes

    def cell_index(self, hero: str) -> int:
        return self.heroes.index(hero)

    def cache(self, clip: str, hero: str) -> Path:
        return self.dir / ".work" / "prep" / clip / hero

    def edits_path(self, hero: str, clip: str) -> Path:
        return self.dir / "prep" / hero / f"{clip}.edits.json"

    def seq_path(self, hero: str, action: str) -> Path:
        return self.dir / "prep" / hero / f"{action}.seq.json"

    def action(self, hero: str, action: str) -> dict:
        return self.cfg["actions"][hero][action]

    # ---- state -----------------------------------------------------------------------------------------------
    def split_info(self, clip: str, hero: str) -> dict | None:
        info = read_json(self.cache(clip, hero) / "info.json")
        if info and any(info.get("grid", {}).get(k) != self.grid.get(k) for k in SPLIT_KEYS):
            info["stale"] = True       # split with other grid settings: edits would point at other pixels
        return info

    def edits(self, hero: str, clip: str) -> dict:
        return read_json(self.edits_path(hero, clip), None) or {"version": 1, "denoise": {}, "ops": {}}

    def save_edits(self, hero: str, clip: str, data: dict) -> None:
        data["version"] = 1
        data["grid"] = {k: self.grid.get(k) for k in SPLIT_KEYS}
        write_json(self.edits_path(hero, clip), data)

    def seq(self, hero: str, action: str) -> dict | None:
        return read_json(self.seq_path(hero, action), None)

    def save_seq(self, hero: str, action: str, data: dict) -> None:
        data["version"] = 1
        write_json(self.seq_path(hero, action), data)

    def status(self, hero: str, action: str) -> dict:
        """One cell of the status board."""
        a = self.action(hero, action)
        takes = a.get("takes", [])
        split = [c for c in takes if self.split_info(c, hero)]
        seq = self.seq(hero, action)
        edited = [c for c in takes if self.edits(hero, c).get("ops") or self.edits(hero, c).get("denoise")]
        asset = ROOT / self.cfg["heroes"][hero]["asset"]
        meta = read_json(asset / "meta.json", {}) or {}
        exported = a["sheet"] in (meta.get("states") or {}) and (meta["states"][a["sheet"]].get("prep") or {}).get("ws") == self.id
        stage = "exported" if exported else "sequenced" if seq else "edited" if edited else "split" if split else "new"
        return {"stage": stage, "takes": takes, "split": split, "edited": edited, "pick": a.get("pick"),
                "frames": sum(len(s["keep"]) for s in seq["segments"]) if seq else 0, "sheet": a["sheet"], "loop": bool(a.get("loop"))}

    def summary(self) -> dict:
        return {"id": self.id, "title": self.cfg.get("title", self.id), "kind": self.cfg.get("kind"), "grid": self.grid,
                "heroes": self.cfg["heroes"], "clips": self.cfg["clips"], "actions": self.cfg["actions"],
                "board": {h: {a: self.status(h, a) for a in self.cfg["actions"][h]} for h in self.heroes}}
