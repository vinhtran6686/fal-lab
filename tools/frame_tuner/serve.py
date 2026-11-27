"""Local server of the Frame Tuner (sprite prep): serves this folder and the API; every step is done by scripts/sprite_prep/.
Usage: python serve.py [port]        (frame_tuner.bat checks python, the packages and ffmpeg, starts this, then opens the browser)
Binds to 127.0.0.1 only.

Pages: /            Sprite prep (index.html): split clips, clean frames, choose frames, preview, export sheets
       /legacy.html  the first tuner (holy_commander recipes); its data is built on demand (POST /api/legacy/build)
Legacy API (unchanged): GET /api/ping, GET /api/recipes, POST /api/recipe {state, recipe}
Sprite prep API (/api/prep/...): workspaces, ws, info, frame, strip, flags, edits, seq, seam, fit, body, config, split, denoise, export, jobs
"""
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import threading
import traceback
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

from sprite_prep.workspace import Workspace  # noqa: E402
from sprite_prep import split as sp, edits as ed, analyze, export as ex  # noqa: E402

# ---- legacy (holy_commander recipes) -------------------------------------------------------------------------------
CFG = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
RECIPE = ROOT / CFG["asset"] / "frames" / "export_recipe.json"
IDS = {s["id"] for s in CFG["states"]}


def read_recipes():
    if RECIPE.exists():
        try:
            return json.loads(RECIPE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"version": 1, "hero": CFG["hero"], "states": {}}


def valid(r):
    k, d = r.get("keep"), r.get("durationsMs")
    return (isinstance(k, list) and k and all(isinstance(i, int) and i >= 0 for i in k) and k == sorted(set(k))
            and isinstance(d, list) and len(d) == len(k) and all(isinstance(x, int) and 10 <= x <= 5000 for x in d)
            and (r.get("hit") is None or (isinstance(r["hit"], int) and 0 <= r["hit"] < len(k))))


# ---- background jobs (split, export, legacy build): one worker, a queue -------------------------------------------
JOBS = {}
QUEUE = []
QLOCK = threading.Condition()


def submit(kind, title, fn):
    jid = uuid.uuid4().hex[:8]
    JOBS[jid] = {"id": jid, "kind": kind, "title": title, "status": "queued", "progress": 0.0, "text": "", "result": None, "error": None}
    with QLOCK:
        QUEUE.append((jid, fn))
        QLOCK.notify()
    return jid


def worker():
    while True:
        with QLOCK:
            while not QUEUE:
                QLOCK.wait()
            jid, fn = QUEUE.pop(0)
        job = JOBS[jid]
        job["status"] = "running"

        def say(f, t, job=job):
            job["progress"], job["text"] = round(float(f), 3), t
        try:
            job["result"] = fn(say)
            job["status"], job["progress"] = "done", 1.0
        except Exception as e:  # shown in the page
            job["status"], job["error"] = "error", f"{e}"
            traceback.print_exc()


threading.Thread(target=worker, daemon=True).start()


def legacy_build(say):
    say(0.05, "building the legacy sheets (first time ~80 s)")
    r = subprocess.run([sys.executable, str(HERE / "build_states.py")], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError((r.stderr or r.stdout)[-800:])
    return {"ok": True}


# ---- helpers -------------------------------------------------------------------------------------------------------
def png_bytes(arr_or_img) -> bytes:
    im = arr_or_img if isinstance(arr_or_img, Image.Image) else Image.fromarray(arr_or_img, "RGBA")
    b = io.BytesIO()
    im.save(b, "PNG", compress_level=1)
    return b.getvalue()


def strip(ws, clip, hero, h, raw=False):
    """All frames of a hero in a clip, cropped to the union box and scaled to height h, side by side (one PNG)."""
    info = ws.split_info(clip, hero)
    x0, y0, x1, y1 = info["crop"]
    s = h / (y1 - y0)
    w = max(1, round((x1 - x0) * s))
    n = info["frames"]
    e = ws.edits(hero, clip)
    sheet = Image.new("RGBA", (w * n, h), (0, 0, 0, 0))
    for f in range(n):
        img = ed.load_raw(ws, clip, hero, f) if raw else ed.render(ws, clip, hero, f, e)
        im = Image.fromarray(img[y0:y1, x0:x1], "RGBA").resize((w, h), Image.BILINEAR)
        sheet.paste(im, (f * w, 0))
    return sheet, {"w": w, "h": h, "n": n, "crop": info["crop"]}


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(HERE), **kw)

    def log_message(self, fmt, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _send(self, body: bytes, ctype: str, code=200, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", code)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    # ---- GET ------------------------------------------------------------------------------------------------------
    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        p = u.path
        try:
            if p == "/api/ping":
                return self._json({"ok": True, "recipe": str(RECIPE.relative_to(ROOT)), "legacy_built": (HERE / "data" / "states.json").exists()})
            if p == "/api/recipes":
                return self._json(read_recipes())
            if not p.startswith("/api/prep/"):
                return super().do_GET()
            cmd = p[len("/api/prep/"):]
            if cmd == "workspaces":
                return self._json([{"id": w.id, "title": w.cfg.get("title", w.id), "kind": w.cfg.get("kind")} for w in Workspace.discover()])
            if cmd == "jobs":
                return self._json(list(JOBS.values())[-30:])
            ws = Workspace.load(q["ws"])
            if cmd == "ws":
                return self._json(ws.summary())
            if cmd == "info":
                return self._json(ws.split_info(q["clip"], q["hero"]))
            if cmd == "frame":
                clip, hero, f = q["clip"], q["hero"], int(q["f"])
                img = ed.load_raw(ws, clip, hero, f) if q.get("raw") == "1" else ed.render(ws, clip, hero, f)
                if q.get("crop", "1") == "1":
                    x0, y0, x1, y1 = ws.split_info(clip, hero)["crop"]
                    img = img[y0:y1, x0:x1]
                return self._send(png_bytes(img), "image/png")
            if cmd == "strip":
                sheet, meta = strip(ws, q["clip"], q["hero"], int(q.get("h", 120)), q.get("raw") == "1")
                return self._send(png_bytes(sheet), "image/png", extra={"X-Strip": json.dumps(meta)})
            if cmd == "stripmeta":
                info = ws.split_info(q["clip"], q["hero"])
                x0, y0, x1, y1 = info["crop"]
                h = int(q.get("h", 120))
                return self._json({"w": max(1, round((x1 - x0) * h / (y1 - y0))), "h": h, "n": info["frames"], "crop": info["crop"]})
            if cmd == "flags":
                return self._json(analyze.clip_flags(ws, q["clip"], q["hero"]))
            if cmd == "edits":
                return self._json(ws.edits(q["hero"], q["clip"]))
            if cmd == "seq":
                return self._json(ws.seq(q["hero"], q["action"]))
            if cmd == "fit":
                return self._json(ex.fit(ws, q["hero"]))
            if cmd == "body":
                return self._json(ex.body_report(ws, q["hero"]))
            return self._json({"error": "unknown"}, 404)
        except Exception as e:
            traceback.print_exc()
            return self._json({"error": str(e)}, 400)

    # ---- POST -----------------------------------------------------------------------------------------------------
    def do_POST(self):
        u = urlparse(self.path)
        p = u.path
        try:
            body = self._body()
            if p == "/api/recipe":
                sid, rec = body["state"], body["recipe"]
                if sid not in IDS:
                    return self._json({"ok": False, "error": "state lạ: " + str(sid)}, 400)
                if not valid(rec):
                    return self._json({"ok": False, "error": "công thức không hợp lệ"}, 400)
                data = read_recipes()
                data.setdefault("states", {})[sid] = rec
                data["hero"], data["version"] = CFG["hero"], 1
                RECIPE.parent.mkdir(parents=True, exist_ok=True)
                fd, tmp = tempfile.mkstemp(dir=str(RECIPE.parent), suffix=".tmp")
                os.close(fd)
                pathlib.Path(tmp).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
                os.replace(tmp, RECIPE)
                return self._json({"ok": True, "file": str(RECIPE.relative_to(ROOT))})
            if p == "/api/legacy/build":
                return self._json({"ok": True, "job": submit("legacy", "legacy sheets", legacy_build)})
            if not p.startswith("/api/prep/"):
                return self._json({"error": "not found"}, 404)
            cmd = p[len("/api/prep/"):]
            ws = Workspace.load(body["ws"])
            if cmd == "split":
                clips = body.get("clips") or list(ws.cfg["clips"])
                heroes = body.get("heroes")
                jobs = []
                for c in clips:
                    jobs.append(submit("split", f"tách {c}", lambda say, c=c: {h: i["frames"] for h, i in sp.split_clip(Workspace.load(ws.id), c, heroes, say).items()}))
                return self._json({"ok": True, "jobs": jobs})
            if cmd == "edits":
                ws.save_edits(body["hero"], body["clip"], body["data"])
                return self._json({"ok": True})
            if cmd == "denoise":       # batch: the same denoise settings for many (hero, clip) pairs
                n = 0
                for hero in body.get("heroes") or ws.heroes:
                    for clip in body.get("clips") or list(ws.cfg["clips"]):
                        if hero in ws.clip_heroes(clip) and ws.split_info(clip, hero):
                            e = ws.edits(hero, clip)
                            e["denoise"] = body["denoise"]
                            ws.save_edits(hero, clip, e)
                            n += 1
                return self._json({"ok": True, "count": n})
            if cmd == "seq":
                ws.save_seq(body["hero"], body["action"], body["data"])
                return self._json({"ok": True})
            if cmd == "seam":
                return self._json(analyze.seam(ws, body["hero"], [tuple(x) for x in body["items"]]))
            if cmd == "config":       # hero settings (cell, shadow, body_2x) or an action's chosen take
                h = body["hero"]
                if "heroPatch" in body:
                    ws.cfg["heroes"][h].update({k: v for k, v in body["heroPatch"].items() if k in ("cell", "shadow", "body_2x", "body_px")})
                if "action" in body and "pick" in body:
                    ws.action(h, body["action"])["pick"] = body["pick"]
                ws.save_config()
                return self._json({"ok": True})
            if cmd == "export":
                hero = body["hero"]
                acts = body.get("actions") or [a for a in ws.cfg["actions"][hero] if ws.seq(hero, a)]
                asset = body.get("asset") or None

                def run(say, acts=acts, hero=hero, asset=asset):
                    w2 = Workspace.load(ws.id)
                    order = ex.export_order(w2, hero, acts)
                    res = {}
                    for i, a in enumerate(order):
                        say(i / len(order), f"xuất {hero} {a}")
                        res[a] = ex.export(w2, hero, a, pathlib.Path(asset) if asset else None)["out"]
                    return res
                return self._json({"ok": True, "job": submit("export", f"xuất {hero}", run)})
            return self._json({"error": "unknown"}, 404)
        except Exception as e:
            traceback.print_exc()
            return self._json({"ok": False, "error": str(e)}, 400)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8767
    print(f"Frame Tuner: http://127.0.0.1:{port}/   (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
