"""Local server for the frame tuner: serves this folder and saves recipes straight into the repo.
Usage: python serve.py [port]   (frame_tuner.bat does build_states.py, opens the browser, then runs this)
API: GET /api/ping, GET /api/recipes, POST /api/recipe {state, recipe}. Recipes live in <asset>/export_recipe.json
(see docs/issue-frame-recipe-sync.md). Binds to 127.0.0.1 only."""
import sys, json, os, pathlib, tempfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parent.parent
CFG = json.loads((HERE / 'sources.json').read_text())
RECIPE = ROOT / CFG['asset'] / 'export_recipe.json'
IDS = {s['id'] for s in CFG['states']}

def read_recipes():
    if RECIPE.exists():
        try: return json.loads(RECIPE.read_text(encoding='utf-8'))
        except Exception: pass
    return {'version': 1, 'hero': CFG['hero'], 'states': {}}

def valid(r):
    k, d = r.get('keep'), r.get('durationsMs')
    return (isinstance(k, list) and k and all(isinstance(i, int) and i >= 0 for i in k) and k == sorted(set(k))
            and isinstance(d, list) and len(d) == len(k) and all(isinstance(x, int) and 10 <= x <= 5000 for x in d)
            and (r.get('hit') is None or (isinstance(r['hit'], int) and 0 <= r['hit'] < len(k))))

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw): super().__init__(*a, directory=str(HERE), **kw)
    def log_message(self, fmt, *a): pass
    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode('utf-8'); self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8'); self.send_header('Content-Length', str(len(b))); self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path.startswith('/api/ping'): return self._json({'ok': True, 'recipe': str(RECIPE.relative_to(ROOT))})
        if self.path.startswith('/api/recipes'): return self._json(read_recipes())
        return super().do_GET()
    def do_POST(self):
        if not self.path.startswith('/api/recipe'): return self._json({'ok': False, 'error': 'not found'}, 404)
        try:
            n = int(self.headers.get('Content-Length', 0)); body = json.loads(self.rfile.read(n).decode('utf-8'))
            sid, rec = body['state'], body['recipe']
            if sid not in IDS: return self._json({'ok': False, 'error': 'state lạ: ' + str(sid)}, 400)
            if not valid(rec): return self._json({'ok': False, 'error': 'công thức không hợp lệ'}, 400)
            data = read_recipes(); data.setdefault('states', {})[sid] = rec; data['hero'] = CFG['hero']; data['version'] = 1
            RECIPE.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=str(RECIPE.parent), suffix='.tmp'); os.close(fd)
            pathlib.Path(tmp).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8'); os.replace(tmp, RECIPE)
            return self._json({'ok': True, 'file': str(RECIPE.relative_to(ROOT))})
        except Exception as e:
            return self._json({'ok': False, 'error': str(e)}, 400)

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8767
    print(f'Frame Tuner: http://127.0.0.1:{port}/   (lưu vào {RECIPE.relative_to(ROOT)}; Ctrl+C để dừng)')
    ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
