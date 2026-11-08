"""Effect profile: everything that is specific to one effect lives in a JSON file, never in code.

{
  "name": "swirl-slash",
  "source": {"frames_dir": "...", "pattern": "{variant}_{frame:02d}.png", "frames": [2, 12],        # inclusive range
             "gif": "...", "crops": {"fire": [x0, y0, x1, y1]}, "background_frame": 13},
  "frame": {"type": "polar"} | {"type": "linear", "angle": null},
  "fit":    {"underlay_px": 10, "passes": 4, "min_area": 6, "min_gain": 0.0008, "axes": ["u", "v"],
             "edge_bias": [0, 0]},                                  # band edge shift in samples (frames.bands)
  "masks":  {"min_area": 12},
  "smooth": {"sigma": 4.5, "corner_deg": 145, "merge_tol": 0.9, "min_area": 8, "close_px": 1.5},   # defaults
  "variants": {
    "fire": {
      "order": ["yellow", "pink", "crimson"],                      # painted bottom -> top
      "groups": {"yellow": 0, ...},                                 # optional; layers of one group run under each other
      "layers": {"yellow": {"colours": [[255,214,112], ...],       # colour polyline: flat fill first, then its edge tint
                            "tol": 26,
                            "gradient": {"edge": [255,163,69], "s": 8.08}}},   # inner edge gradient (optional)
      "halo": {"s_near": .., "c_near": [..], "s_far": .., "c_far": [..]},     # glow behind the shapes (optional)
      "near_halo": true,
      "smooth": {...}                                               # per-variant override
    }
  }
}"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DEFAULTS = {
    "frame": {"type": "polar"},
    "fit": {"underlay_px": 10, "passes": 4, "min_area": 6, "min_gain": 0.0008, "axes": ["u", "v"], "edge_bias": [0, 0]},
    "masks": {"min_area": 12},
    "smooth": {"sigma": 4.5, "corner_deg": 145, "merge_tol": 0.9, "min_area": 8, "close_px": 1.5},
    "background": [24, 25, 28],
}


class Profile:
    def __init__(self, path):
        self.path = Path(path)
        self.d = json.loads(self.path.read_text())

    # --- generic access ---
    def get(self, key):
        v = dict(DEFAULTS.get(key, {})) if isinstance(DEFAULTS.get(key), dict) else DEFAULTS.get(key)
        if isinstance(v, dict):
            v.update(self.d.get(key, {}))
            return v
        return self.d.get(key, v)

    @property
    def name(self):
        return self.d["name"]

    @property
    def variants(self):
        return list(self.d["variants"])

    def var(self, v):
        return self.d["variants"][v]

    def order(self, v):
        return self.var(v)["order"]

    def layers(self, v):
        return self.var(v)["layers"]

    def flat(self, v, l):
        return tuple(self.layers(v)[l]["colours"][0])

    def groups(self, v):
        g = self.var(v).get("groups") or {}
        return {l: g.get(l, 0) for l in self.order(v)}

    def smooth(self, v):
        s = self.get("smooth")
        s.update(self.var(v).get("smooth", {}))
        return s

    def frames(self):
        a, b = self.d["source"]["frames"]
        return list(range(a, b + 1))

    def out_dir(self):
        o = self.d.get("output") or f"lib-fx/_study/{self.name}/vector"
        p = REPO / o
        p.mkdir(parents=True, exist_ok=True)
        return p

    def resolve(self, rel):
        return REPO / rel

    def save(self):
        self.path.write_text(json.dumps(self.d, indent=1, ensure_ascii=False))
