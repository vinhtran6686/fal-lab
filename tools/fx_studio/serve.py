"""Local server for Fx Studio: serves the page and runs scripts/fx_studio.py (import, save, render, install, play in game).
Usage: python serve.py [port]   (fx_studio.bat opens the browser, then runs this). Binds to 127.0.0.1 only.
API (JSON): GET /api/list, GET /api/fx/<id>, POST /api/import {id, name, data (base64), grid, bg, force},
POST /api/save/<id> {recipe}, POST /api/render/<id> {recipe}, POST /api/install/<id>, POST /api/uninstall/<id>,
POST /api/play {level}. Files: /vfx/<id>/... (out/vfx), /bg.png (a KR1 map crop at @1x), /hero.png (a KR1 hero at @1x)."""
import base64, io, json, os, pathlib, subprocess, sys, tempfile, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import fx_studio as fx   # noqa: E402

LOCK = threading.Lock()   # one pipeline job at a time (render and install write the same folders)


def fx_info(fx_id: str) -> dict:
    r = fx.load(fx_id)
    a = fx.asset(fx_id)
    cells_dir = a / ".work" / "cells"
    if not cells_dir.exists() or len(list(cells_dir.glob("cell_*.png"))) != len(r["cells"]):
        fx.write_cells(r)
    man = a / "game" / "manifest.json"
    manifest = json.loads(man.read_text(encoding="utf-8")) if man.exists() else None
    stamp = int(man.stat().st_mtime) if man.exists() else 0
    return {"recipe": r, "cell_size": fx.cell_canvas(r),
            "cells": [f"/vfx/{fx_id}/.work/cells/cell_{i + 1:02d}.png" for i in range(len(r["cells"]))],
            "source": f"/vfx/{fx_id}/{r['source']}",
            "manifest": manifest, "stale": bool(manifest) and manifest.get("recipe_hash") != fx.recipe_hash(r),
            "rendered": [f"/vfx/{fx_id}/game/frames/@1x/{n}.png?t={stamp}" for n in manifest["frames"]] if manifest else [],
            "preview": f"/vfx/{fx_id}/game/preview.gif?t={stamp}" if manifest else None}


def list_fx() -> list:
    out = []
    for p in sorted(fx.VFX.glob("*/fx.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        out.append({"id": r["id"], "mode": r["mode"], "drawings": len(r["frames"]), "installed": r["game"].get("installed", False),
                    "rendered": (p.parent / "game" / "manifest.json").exists()})
    return out


def clean(recipe: dict, fx_id: str) -> dict:
    """Take what the page may change; keep id, source, cells and the install flag from disk."""
    r = fx.load(fx_id)
    for k in ("bg", "black_floor", "frames", "scale", "anchor", "mode", "color", "vector"):
        if k in recipe:
            r[k] = recipe[k]
    if "game" in recipe:
        for k in ("name", "z", "loop", "runs"):
            if k in recipe["game"]:
                r["game"][k] = recipe["game"][k]
    if not r["frames"] or any(not (0 <= int(f["cell"]) < len(r["cells"])) or not (1 <= int(f.get("hold", 2)) <= 60) for f in r["frames"]):
        raise ValueError("frames: each needs a cell of this sheet and a hold of 1-60 game frames")
    fx.check_game(r)
    if not (0.05 <= float(r["scale"]) <= 8):
        raise ValueError("scale must be 0.05-8")
    return r


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(HERE), **kw)

    def log_message(self, fmt, *a):
        pass

    def _send(self, body: bytes, ctype: str, code: int = 200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", code)

    def _png(self, im):
        b = io.BytesIO(); im.save(b, "PNG"); self._send(b.getvalue(), "image/png")

    def do_GET(self):
        path = unquote(self.path.split("?")[0])
        try:
            if path == "/api/list":
                return self._json({"ok": True, "fx": list_fx(), "game": str(fx.GAME_DIR), "game_found": fx.GAME_DIR.exists()})
            if path.startswith("/api/fx/"):
                return self._json({"ok": True, **fx_info(path.split("/")[3])})
            if path == "/bg.png":
                return self._png(fx.backdrop((960, 540)))
            if path == "/hero.png":
                h = fx.hero_for_scale()
                return self._png(h) if h else self._json({"ok": False}, 404)
            if path.startswith("/vfx/"):
                f = (fx.VFX / path[5:]).resolve()
                if fx.VFX.resolve() not in f.parents or not f.is_file():
                    return self._json({"ok": False, "error": "not found"}, 404)
                ctype = {".png": "image/png", ".gif": "image/gif", ".svg": "image/svg+xml", ".json": "application/json"}.get(f.suffix, "application/octet-stream")
                return self._send(f.read_bytes(), ctype)
        except SystemExit as e:
            return self._json({"ok": False, "error": str(e)}, 400)
        return super().do_GET()

    def do_POST(self):
        path = unquote(self.path.split("?")[0])
        logs = []
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
            parts = path.strip("/").split("/")
            with LOCK:
                if path == "/api/import":
                    data = base64.b64decode(body["data"].split(",")[-1])
                    tmp = pathlib.Path(tempfile.mkdtemp()) / (pathlib.Path(body.get("name") or "sheet.png").stem + ".png")
                    tmp.write_bytes(data)
                    grid = tuple(int(v) for v in body["grid"].lower().split("x")) if body.get("grid") else None
                    r = fx.do_import(tmp, body["id"], grid, body.get("bg") or "auto", bool(body.get("force")), log=logs.append)
                    return self._json({"ok": True, "id": r["id"], "log": logs})
                fx_id = parts[2] if len(parts) > 2 else None
                if parts[:2] == ["api", "save"]:
                    old = fx.load(fx_id)
                    r = clean(body["recipe"], fx_id)
                    fx.save(r)
                    if (old["bg"], old["black_floor"]) != (r["bg"], r["black_floor"]):
                        fx.write_cells(r)
                    return self._json({"ok": True, **fx_info(fx_id)})
                if parts[:2] == ["api", "render"]:
                    if body.get("recipe"):
                        fx.save(clean(body["recipe"], fx_id))
                    fx.render(fx.load(fx_id), log=logs.append)
                    return self._json({"ok": True, "log": logs, **fx_info(fx_id)})
                if parts[:2] in (["api", "install"], ["api", "uninstall"]):
                    fx.do_install([fx_id], fx.GAME_DIR, parts[1] == "install", log=logs.append)
                    return self._json({"ok": True, "log": logs, **fx_info(fx_id)})
                if path == "/api/play":
                    return self._json(play(int(body.get("level") or 3)))
            return self._json({"ok": False, "error": "not found"}, 404)
        except SystemExit as e:
            return self._json({"ok": False, "error": str(e), "log": logs}, 400)
        except Exception as e:
            return self._json({"ok": False, "error": f"{type(e).__name__}: {e}", "log": logs}, 400)


def play(level: int) -> dict:
    """Start the game on a level with the fx_lab demo on (every installed effect plays at the centre every 2 s)."""
    love = fx.GAME_DIR.parent.parent / "tools" / "love" / "0.10.2" / "love.exe"
    if not love.exists():
        return {"ok": False, "error": f"LOVE not found: {love}"}
    env = dict(os.environ, KR_FX_LAB_DEMO="1")
    subprocess.Popen([str(love), "src", "-level", str(level)], cwd=str(fx.GAME_DIR), env=env,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {"ok": True, "log": [f"game started on level {level}: F6 next effect, F7 play at the mouse, Shift+F7 mirrored"]}


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8768
    print(f"Fx Studio: http://127.0.0.1:{port}/   (out/vfx, game {fx.GAME_DIR}; Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
