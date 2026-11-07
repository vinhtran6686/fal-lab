"""Step 2: read the structure of the traced paths and of the fitted strokes, per shape type -> out/analysis.json."""
import json
from pathlib import Path
import numpy as np
from masks import LAYERS, clean_mask
from vectorize import trace

OUT = Path(__file__).parent / "out"

def classify(p, layer):
    span = p["span_px"]
    W = p["Wmax"]
    sharp0, sharp1 = p["e0"] < 1e-3, p["e1"] < 1e-3
    if p["op"] == "cut":
        return "notch"
    if layer in ("amber", "deep") and W <= 6 and span > 4 * W:
        return "rim"
    if span > 180 and W > 12:
        return "crescent"
    if sharp0 != sharp1 or p.get("fork", False):
        return "tongue"
    if sharp0 and sharp1:
        return "feather" if layer in ("cyan", "mid", "pink") else "sliver"
    return "chunk"

def q(a):
    a = np.asarray(a, float)
    return dict(n=int(len(a)), p10=round(float(np.percentile(a, 10)), 2), med=round(float(np.median(a)), 2),
                p90=round(float(np.percentile(a, 90)), 2)) if len(a) else {}

def main():
    res = {"trace": {}, "strokes": {}}
    # --- traced paths: anchors, corners, handle ratios
    hr, ang, apl = [], {"all": []}, []
    for v, layers in LAYERS.items():
        for f in (3, 4, 5):
            for l in layers:
                loops = trace(clean_mask(v, f, l))
                for lp in loops:
                    segs = lp["segs"]
                    per = sum(np.linalg.norm(s[3] - s[0]) for s in segs)
                    apl.append(per / max(len(segs), 1))
                    for s in segs:
                        ch = np.linalg.norm(s[3] - s[0])
                        if ch > 3:
                            hr += [np.linalg.norm(s[1] - s[0]) / ch, np.linalg.norm(s[2] - s[3]) / ch]
                    for _, a in lp["sharp"]:
                        ang.setdefault(l, []).append(a)
                        ang["all"].append(a)
    res["trace"]["handle_over_chord"] = q(hr)
    res["trace"]["px_per_anchor"] = q(apl)
    res["trace"]["corner_inner_angle_deg"] = {k: q(v) for k, v in ang.items()}
    # --- fitted strokes
    by = {}
    for v in LAYERS:
        for f in (3, 4, 5):
            P = json.loads((OUT / f"params_{v}_{f:02d}.json").read_text())
            for l, shapes in P["layers"].items():
                rows = []
                for p in shapes:
                    t = classify(p, l)
                    d = by.setdefault(t, {"a": [], "b": [], "len_over_w": [], "W": [], "span_deg": [], "tip_back": [], "layers": {}})
                    d["a"].append(p["a"]); d["b"].append(p["b"])
                    d["len_over_w"].append(p["span_px"] / max(p["Wmax"], 0.5)); d["W"].append(p["Wmax"])
                    d["span_deg"].append(np.degrees(p["theta1"] - p["theta0"]))
                    d["layers"][l] = d["layers"].get(l, 0) + 1
                    if t == "tongue":  # theta grows with the sweep: a sharp START means the tip trails behind
                        d["tip_back"].append(1.0 if p["e0"] < 1e-3 else 0.0)
                    if p["op"] == "add" and t in ("tongue", "feather"):
                        rows.append((p["theta0"], p["span_px"]))
                # rhythm: consecutive tongue/feather lengths along one layer
                rows.sort()
                if len(rows) >= 3:
                    L = np.array([r[1] for r in rows])
                    gaps = np.diff([r[0] for r in rows])
                    by.setdefault("_rhythm", []).append(dict(key=f"{v}_{f:02d}_{l}", lengths=[round(x) for x in L],
                        len_ratio_consecutive=round(float(np.median(np.maximum(L[1:], L[:-1]) / np.maximum(np.minimum(L[1:], L[:-1]), 1))), 2),
                        gap_cv=round(float(np.std(gaps) / max(np.mean(gaps), 1e-6)), 2)))
    for t, d in by.items():
        if t == "_rhythm":
            res["strokes"]["rhythm"] = d
            continue
        res["strokes"][t] = {k: (q(x) if k not in ("layers", "tip_back") else x) for k, x in d.items()}
        if d["tip_back"]:
            res["strokes"][t]["tip_back"] = round(float(np.mean(d["tip_back"])), 2)
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1)[:6000])

if __name__ == "__main__":
    main()
