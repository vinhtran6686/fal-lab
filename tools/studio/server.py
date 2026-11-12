"""Rig & Pose Studio: local server (stdlib only) around the Puppet Kit renderer.

Every picture the Studio shows comes from `puppet_kit.core.Rig.render`; the browser only draws overlays and handles.
Run: python tools/studio/server.py [--asset out/heroes/azure_blade] [--port 8765]
Guide: tools/studio/README.md
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import io
import json
import math
import pathlib
import re
import shutil
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "scripts"))
from puppet_kit.core import DEFAULTS, Rig, S, T, key_magenta  # noqa: E402

POSE_CHANNELS = ("rot", "tx", "ty", "sx", "sy", "shx")
RIG_FILE_RE = re.compile(r"^rig[\w\-]*\.json$")
THUMB_REGION = (60, 60, 900, 900)
THUMB_PX = 240
DRAFT_SKIN_ITERATIONS = 5


# ---------------------------------------------------------------- rig wrapper


class StudioRig(Rig):
    """Rig with a shared cache of the keyed source stills, so a polygon edit does not re-key the images."""

    _keyed: dict = {}

    def _src(self, name, cache):
        path = (self.dir / self.spec["sources"][name]).resolve()
        key = (str(path), path.stat().st_mtime_ns)
        if key not in StudioRig._keyed:
            StudioRig._keyed[key] = key_magenta(Image.open(path))
        return StudioRig._keyed[key]

    @staticmethod
    def structure_key(spec) -> str:
        """Everything that needs the parts rebuilt (cuts, sources); bones, IK, sockets and skin params do not."""
        parts = [{k: v for k, v in p.items() if k not in ("skin", "bone")} for p in spec["parts"]]
        return json.dumps({"sources": spec["sources"], "parts": parts}, sort_keys=True)

    def update_spec(self, spec) -> bool:
        """Swap in an edited spec. Returns True when the parts had to be rebuilt (a cut changed)."""
        rebuild = self.structure_key(spec) != self.structure_key(self.spec)
        self.spec = spec
        self.ground = np.array(spec["ground"], dtype=np.float64)
        self.unit = float(spec["unit"])
        self.bones = {b["name"]: b for b in spec["bones"]}
        self.order = self._bone_order()
        if rebuild:
            self.parts = []
            self._load_parts()
        else:
            by_name = {p["name"]: p for p in spec["parts"]}
            for part in self.parts:
                part["spec"] = by_name[part["name"]]
                part["bone"] = part["spec"]["bone"]
        return rebuild


def segments_cross(a, b, c, d) -> bool:
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0


def poly_is_simple(poly) -> bool:
    n = len(poly)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(i - j) in (1, n - 1):
                continue
            if segments_cross(poly[i], poly[(i + 1) % n], poly[j], poly[(j + 1) % n]):
                return False
    return True


def validate_spec(spec) -> list[str]:
    """Rules the Puppet Kit needs; the Studio refuses an edit that breaks them rather than rendering garbage."""
    errs = []
    names = [b["name"] for b in spec["bones"]]
    if len(set(names)) != len(names):
        errs.append("duplicate bone names")
    by_name = {b["name"]: b for b in spec["bones"]}
    cycle_reported = False
    for b in spec["bones"]:
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in b["pivot"]):
            errs.append(f"bone {b['name']}: pivot is not a finite number")
        if b.get("parent") is not None and b["parent"] not in by_name:
            errs.append(f"bone {b['name']}: unknown parent {b['parent']}")
        seen, cur = set(), b["name"]
        while cur is not None and cur in by_name and cur not in seen:       # a parent chain that loops back is a cycle
            seen.add(cur)
            cur = by_name[cur].get("parent")
        if cur is not None and cur in seen and not cycle_reported:
            errs.append(f"bone {b['name']}: parent chain forms a cycle")
            cycle_reported = True
        lim = (b.get("limit") or {}).get("rot")
        if lim is not None and not (len(lim) == 2 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in lim) and lim[0] < lim[1]):
            errs.append(f"bone {b['name']}: limit.rot must be [min, max] with min < max")
    part_names = {p["name"] for p in spec["parts"]}
    for lk in spec.get("links", []):
        nm = lk.get("name", "?")
        if lk.get("arm") not in by_name:
            errs.append(f"link {nm}: arm bone {lk.get('arm')} does not exist")
        if lk.get("mode", "stretch") not in ("stretch", "carry"):
            errs.append(f"link {nm}: mode must be stretch or carry")
        if not (isinstance(lk.get("max_pull", 80), (int, float)) and lk.get("max_pull", 80) >= 0):
            errs.append(f"link {nm}: max_pull must be >= 0")
        for a in lk.get("anchors", []):
            if a.get("part") not in part_names:
                errs.append(f"link {nm}: anchor part {a.get('part')} does not exist")
            if not (len(a.get("pt", [])) == 2 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in a["pt"])):
                errs.append(f"link {nm}: anchor pt must be [x, y]")
            if not (isinstance(a.get("radius"), (int, float)) and a["radius"] > 0):
                errs.append(f"link {nm}: anchor radius must be > 0")
            if not (isinstance(a.get("gain", 1.0), (int, float)) and 0 <= a.get("gain", 1.0) <= 3):
                errs.append(f"link {nm}: anchor gain must be in 0..3")
    for p in spec["parts"]:
        poly = p.get("select", {}).get("poly")
        if poly is not None:
            if len(poly) < 3:
                errs.append(f"part {p['name']}: polygon needs at least 3 vertices")
            elif not all(len(q) == 2 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in q) for q in poly):
                errs.append(f"part {p['name']}: polygon has a non-numeric vertex")
            elif not poly_is_simple(poly):
                errs.append(f"part {p['name']}: polygon edges cross each other")
        for d_ in p.get("discs", []):
            if not (len(d_.get("at", [])) == 2 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in d_["at"]) and isinstance(d_.get("r"), (int, float)) and 1 <= d_["r"] <= 400):
                errs.append(f"part {p['name']}: disc needs at=[x, y] and 1 <= r <= 400")
        sk = p.get("skin")
        if sk:
            bl = sk.get("blend", 40)
            for v in (bl if isinstance(bl, list) else [bl]):
                if not (isinstance(v, (int, float)) and v >= 1):
                    errs.append(f"part {p['name']}: blend must be >= 1")
    return errs


def parts_meta(rig):
    return [{"name": p["name"], "off": [int(v) for v in p["off"]], "size": [int(p["img"].shape[1]), int(p["img"].shape[0])]} for p in rig.parts]


def topology_hash(spec) -> str:
    topo = {"bones": [(b["name"], b.get("parent")) for b in spec["bones"]],
            "ik": [(i["upper"], i["lower"]) for i in spec.get("ik", [])],
            "parts": [p["name"] for p in spec["parts"]]}
    return hashlib.sha1(json.dumps(topo, sort_keys=True).encode()).hexdigest()[:12]


# ---------------------------------------------------------------- pose <-> tracks


def pose_to_tracks(pose, hide=()) -> dict:
    """{"bones": {name: {channel: value}}, "ik": {upper: false = FK}} -> the tracks a Rig.pose call takes."""
    tracks = {}
    for bone, chans in (pose.get("bones") or {}).items():
        for ch, v in chans.items():
            if ch in POSE_CHANNELS:
                tracks[f"{bone}.{ch}"] = [[0, float(v)]]
    for upper, on in (pose.get("ik") or {}).items():
        if on is False:
            tracks[f"{upper}.fk"] = [[0, 1.0]]
    for part in hide:
        tracks[f"{part}.alpha"] = [[0, 0.0]]
    return tracks


def clean_pose(pose, bones) -> dict:
    """Keep only supported channels that differ from the default; drop unknown bones."""
    out = {"bones": {}, "ik": {}}
    for bone, chans in (pose.get("bones") or {}).items():
        if bone not in bones:
            continue
        keep = {ch: float(v) for ch, v in chans.items()
                if ch in POSE_CHANNELS and isinstance(v, (int, float)) and math.isfinite(v) and abs(v - DEFAULTS[ch]) > 1e-9}
        if keep:
            out["bones"][bone] = keep
    for upper, on in (pose.get("ik") or {}).items():
        if upper in bones and on is False:
            out["ik"][upper] = False
    return out


# ---------------------------------------------------------------- studio state


def sha(path: pathlib.Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()[:12]


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return s or "pose"


class Studio:
    def __init__(self, asset: pathlib.Path, rig_file: str = "rig.json"):
        self.asset = asset.resolve()
        self.rig_dir = self.asset / "source" / "rig"
        self.pose_dir = self.asset / "poses"
        self.work_dir = self.asset / ".work"
        self.lock = threading.RLock()
        self.rig_file = rig_file
        self.working: StudioRig | None = None
        self.saved: StudioRig | None = None
        self.open_rig(rig_file)

    # --- rig files
    def rig_files(self):
        return sorted(p.name for p in self.rig_dir.glob("rig*.json") if RIG_FILE_RE.match(p.name))

    def open_rig(self, name: str):
        if not RIG_FILE_RE.match(name) or not (self.rig_dir / name).exists():
            raise ValueError(f"unknown rig file {name}")
        with self.lock:
            self.rig_file = name
            self.saved = StudioRig(self.rig_dir / name)
            self.working = StudioRig(self.rig_dir / name, spec=copy.deepcopy(self.saved.spec))
        return self.saved.spec

    def set_rig(self, spec) -> dict:
        errs = validate_spec(spec)
        if errs:
            raise ValueError("; ".join(errs))
        with self.lock:
            t = time.time()
            rebuilt = self.working.update_spec(spec)
            return {"rebuilt": rebuilt, "ms": round((time.time() - t) * 1000)}

    def save_rig(self, spec, mode: str, name: str | None) -> dict:
        errs = validate_spec(spec)
        if errs:
            raise ValueError("; ".join(errs))
        with self.lock:
            target = self.rig_file
            if mode == "new":
                nums = [int(m.group(1)) for f in self.rig_files() if (m := re.match(r"^rig_studio_v(\d+)\.json$", f))]
                target = f"rig_studio_v{(max(nums) + 1 if nums else 1):02d}.json"
            src = self.rig_dir / self.rig_file
            backup = None
            if mode == "overwrite" and src.exists():
                bdir = self.rig_dir / "backup"
                bdir.mkdir(exist_ok=True)
                backup = bdir / f"{src.stem}_{time.strftime('%Y%m%d-%H%M%S')}.json"
                shutil.copy2(src, backup)
            (self.rig_dir / target).write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            self.open_rig(target)
            return {"file": target, "backup": backup.name if backup else None}

    # --- rendering
    def render(self, req) -> dict:
        t0 = time.time()
        scale = float(req.get("scale", 0.5))
        x0, y0, w, h = req.get("region", [-160, -160, 1344, 1344])
        W, H = max(1, math.ceil(w * scale)), max(1, math.ceil(h * scale))
        if W * H > 4_000_000:
            raise ValueError("region too large")
        view = S(scale, scale) @ T(-x0, -y0)
        canvas = np.zeros((H, W, 4), np.float32)
        primary = None
        game_png = None
        with self.lock:
            lowered = []
            if req.get("draft"):                       # fewer skin solver rounds while dragging; the final render uses the rig's own value
                for rg in (self.working, self.saved):
                    for p in rg.spec["parts"]:
                        if p.get("skin"):
                            lowered.append((p["skin"], p["skin"].get("iterations")))
                            p["skin"]["iterations"] = DRAFT_SKIN_ITERATIONS
            try:
                for layer in req["layers"]:
                    rig = self.saved if layer.get("src") == "saved" else self.working
                    tracks = pose_to_tracks(layer.get("pose") or {}, layer.get("hide") or [])
                    out, world = rig.render(tracks, 0, view, (H, W))
                    out[..., 3] *= float(layer.get("alpha", 1.0))
                    canvas = over(canvas, out)
                    if layer.get("primary"):
                        primary = (rig, world, tracks)
                if req.get("game") and primary:
                    g = req["game"]
                    gs = float(g["scale"])
                    gx, gy, gw, gh = g["region"]
                    gout, _ = primary[0].render(primary[2], 0, S(gs, gs) @ T(-gx, -gy), (math.ceil(gh * gs), math.ceil(gw * gs)))
                    gb = io.BytesIO()
                    Image.fromarray(gout.clip(0, 255).astype(np.uint8), "RGBA").save(gb, "PNG", compress_level=1)
                    game_png = base64.b64encode(gb.getvalue()).decode()
            finally:
                for sk, old in lowered:
                    if old is None:
                        sk.pop("iterations", None)
                    else:
                        sk["iterations"] = old
            rig, world = (primary[0], primary[1]) if primary else (self.working, self.working.pose({}, 0)[0])
            info = {
                "world": {n: [m[0, 0], m[1, 0], m[0, 1], m[1, 1], m[0, 2], m[1, 2]] for n, m in world.items()},
                "sockets": rig.sockets(world),
                "game_png": game_png,
            }
        buf = io.BytesIO()
        Image.fromarray(canvas.clip(0, 255).astype(np.uint8), "RGBA").save(buf, "PNG", compress_level=1)
        info.update(png=base64.b64encode(buf.getvalue()).decode(), size=[W, H], scale=scale, region=[x0, y0, w, h],
                    ms=round((time.time() - t0) * 1000))
        return info

    def thumbnail(self, pose) -> bytes:
        x0, y0, w, h = THUMB_REGION
        s = THUMB_PX / w
        view = S(s, s) @ T(-x0, -y0)
        with self.lock:
            out, _ = self.working.render(pose_to_tracks(pose), 0, view, (round(h * s), round(w * s)))
        img = Image.new("RGBA", (out.shape[1], out.shape[0]), (46, 52, 62, 255))
        img.alpha_composite(Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA"))
        buf = io.BytesIO()
        img.convert("RGB").save(buf, "PNG")
        return buf.getvalue()

    # --- pose library (independent of anims/*.json and rig.json)
    def pose_path(self, pid: str) -> pathlib.Path:
        if not re.match(r"^[a-z0-9_]+$", pid):
            raise ValueError("bad pose id")
        return self.pose_dir / f"{pid}.json"

    def list_poses(self):
        out = []
        for p in sorted(self.pose_dir.glob("*.json")) if self.pose_dir.exists() else []:
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                d["has_thumb"] = p.with_suffix(".png").exists()
                out.append(d)
            except Exception:
                continue
        return sorted(out, key=lambda d: d.get("created", ""))

    def _write_pose(self, d, thumb=True):
        self.pose_dir.mkdir(parents=True, exist_ok=True)
        d["rig"] = {"file": self.rig_file, "topology": topology_hash(self.working.spec), "hash": sha(self.rig_dir / self.rig_file),
                    "bones": len(self.working.spec["bones"])}
        d["schema"] = "pose/1"
        self.pose_path(d["id"]).write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        if thumb:
            self.pose_path(d["id"]).with_suffix(".png").write_bytes(self.thumbnail(d))

    def pose_op(self, req) -> dict:
        op = req["op"]
        with self.lock:
            bones = self.working.bones
            if op in ("save", "import"):
                src = req["pose"]
                name = (req.get("name") or src.get("name") or "pose").strip()[:80] or "pose"
                base, pid, n = slug(req.get("id") or name), None, 1
                pid = base
                while self.pose_path(pid).exists():
                    n += 1
                    pid = f"{base}_{n}"
                d = {"id": pid, "name": name, "description": (req.get("description") or src.get("description") or "")[:500],
                     "created": now(), "updated": now(), **clean_pose(src, bones)}
                self._write_pose(d)
                return d
            path = self.pose_path(req["id"])
            if not path.exists():
                raise ValueError("pose not found")
            d = json.loads(path.read_text(encoding="utf-8"))
            if op == "update":
                d.update(clean_pose(req["pose"], bones))
                d["updated"] = now()
                if "description" in req:
                    d["description"] = req["description"][:500]
                self._write_pose(d)
            elif op == "rename":
                d["name"] = req["name"].strip()[:80] or d["name"]
                if "description" in req:
                    d["description"] = req["description"][:500]
                d["updated"] = now()
                self._write_pose(d, thumb=False)
            elif op == "duplicate":
                base, n = d["id"] + "_copy", 1
                pid = base
                while self.pose_path(pid).exists():
                    n += 1
                    pid = f"{base}{n}"
                d = {**d, "id": pid, "name": d["name"] + " copy", "created": now(), "updated": now()}
                self._write_pose(d)
            elif op == "delete":
                trash = self.pose_dir / ".trash"
                trash.mkdir(exist_ok=True)
                stamp = time.strftime("%Y%m%d-%H%M%S")
                for ext in (".json", ".png"):
                    f = path.with_suffix(ext)
                    if f.exists():
                        shutil.move(str(f), trash / f"{f.stem}_{stamp}{ext}")
                return {"deleted": d["id"]}
            else:
                raise ValueError(f"unknown pose op {op}")
            return d

    # --- working-state autosave (not in git: .work/)
    def autosave_path(self):
        return self.work_dir / "studio_autosave.json"


# ---------------------------------------------------------------- compositing


def over(dst, src):
    a = src[..., 3:4] / 255.0
    oa = dst[..., 3:4] / 255.0
    na = a + oa * (1 - a)
    rgb = np.where(na > 1e-6, (src[..., :3] * a + dst[..., :3] * oa * (1 - a)) / np.maximum(na, 1e-6), 0)
    return np.concatenate([rgb, na * 255.0], axis=-1).astype(np.float32)


# ---------------------------------------------------------------- http

STUDIO: Studio | None = None
STATIC = HERE / "static"
MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".png": "image/png", ".json": "application/json; charset=utf-8"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body: bytes, ctype="application/json; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj).encode())

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        st = STUDIO
        try:
            if path == "/api/state":
                with st.lock:
                    return self._json({
                        "asset": st.asset.name, "rig_file": st.rig_file, "rig_files": st.rig_files(), "rig": st.saved.spec,
                        "parts": parts_meta(st.saved),
                        "poses": st.list_poses(), "topology": topology_hash(st.saved.spec),
                        "autosave": st.autosave_path().exists() and json.loads(st.autosave_path().read_text(encoding="utf-8")) or None,
                        "rig_mtime": (st.rig_dir / st.rig_file).stat().st_mtime,
                    })
            if path.startswith("/api/open"):
                name = urlparse(self.path).query.split("=", 1)[1]
                spec = st.open_rig(name)
                return self._json({"rig": spec, "rig_file": name, "topology": topology_hash(spec),
                                   "parts": parts_meta(st.saved)})
            if path.startswith("/api/part/"):
                name = path[len("/api/part/"):].removesuffix(".png")
                part = next((q for q in st.saved.parts if q["name"] == name), None)
                if part is None:
                    return self._send(404, b"not found", "text/plain")
                im = Image.fromarray(part["img"].clip(0, 255).astype(np.uint8), "RGBA")
                im.thumbnail((96, 96))
                buf = io.BytesIO()
                im.save(buf, "PNG")
                return self._send(200, buf.getvalue(), "image/png", {"Cache-Control": "max-age=60"})
            if path.startswith("/poses/"):
                f = (st.pose_dir / path[len("/poses/"):]).resolve()
                if f.parent == st.pose_dir.resolve() and f.exists():
                    return self._send(200, f.read_bytes(), MIME.get(f.suffix, "application/octet-stream"),
                                      {"Content-Disposition": f'inline; filename="{f.name}"'})
                return self._send(404, b"not found", "text/plain")
            rel = "index.html" if path in ("/", "") else path.lstrip("/")
            f = (STATIC / rel).resolve()
            if STATIC.resolve() in f.parents and f.exists():
                return self._send(200, f.read_bytes(), MIME.get(f.suffix, "application/octet-stream"))
            self._send(404, b"not found", "text/plain")
        except Exception as e:  # noqa: BLE001
            self._json({"error": str(e)}, 400)

    def do_POST(self):
        if self.headers.get("X-Studio") != "1":           # blocks cross-site POSTs to this local server
            return self._send(403, b"forbidden", "text/plain")
        st = STUDIO
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            path = urlparse(self.path).path
            if path == "/api/render":
                return self._json(st.render(req))
            if path == "/api/rig/set":
                return self._json(st.set_rig(req["rig"]))
            if path == "/api/rig/save":
                return self._json(st.save_rig(req["rig"], req.get("mode", "overwrite"), req.get("name")))
            if path == "/api/pose":
                return self._json(st.pose_op(req))
            if path == "/api/autosave":
                p = st.autosave_path()
                p.parent.mkdir(exist_ok=True)
                p.write_text(json.dumps(req), encoding="utf-8")
                return self._json({"ok": True})
            if path == "/api/autosave/clear":
                st.autosave_path().unlink(missing_ok=True)
                return self._json({"ok": True})
            self._send(404, b"not found", "text/plain")
        except Exception as e:  # noqa: BLE001
            self._json({"error": f"{type(e).__name__}: {e}"}, 400)


def make_server(asset, port=8765, rig_file="rig.json"):
    global STUDIO
    STUDIO = Studio(pathlib.Path(asset), rig_file)
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main():
    ap = argparse.ArgumentParser(description="Rig & Pose Studio")
    ap.add_argument("--asset", default=str(HERE.parent.parent / "out" / "heroes" / "azure_blade"))
    ap.add_argument("--rig", default=None, help="rig file in source/rig (default: rig_studio_v01.json if present, else rig.json)")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    rig = a.rig or ("rig_studio_v01.json" if (pathlib.Path(a.asset) / "source" / "rig" / "rig_studio_v01.json").exists() else ("rig.json" if (pathlib.Path(a.asset) / "source" / "rig" / "rig.json").exists() else "rig_a.json"))
    srv = make_server(a.asset, a.port, rig)
    url = f"http://127.0.0.1:{a.port}/"
    print(f"[Studio] {STUDIO.asset.name} rig {STUDIO.rig_file}: {len(STUDIO.working.bones)} bones, {len(STUDIO.working.parts)} layers -> {url}")
    if not a.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
