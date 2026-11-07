"""Reuse demo: NEW swirl stills built only from the stroke formula + the rules measured in analysis.json.
No coordinate comes from the GIF. Three seeds -> three different drawings with the same design language."""
from pathlib import Path
import numpy as np
from PIL import Image
import io, cairosvg
from shapes import stroke_path, width_profile, bern
from bezier import path_d, svg_doc

OUT = Path(__file__).parent

def rhythm(rng, n, mean, ratio=(2.0, 4.0)):
    """Lengths alternating big/small: consecutive ratio drawn in `ratio` (measured median 2.3-4.7), never equal."""
    L, big = [], rng.random() < 0.5
    for _ in range(n):
        f = rng.uniform(*ratio)
        L.append(mean * (np.sqrt(f) if big else 1 / np.sqrt(f)) * rng.uniform(0.85, 1.15))
        big = not big if rng.random() < 0.8 else big
    return np.array(L)

def gaps(rng, n, total, cv=0.7):
    """Irregular spacing: gamma gaps with coefficient of variation ~cv (measured 0.54-1.2)."""
    g = rng.gamma(1 / cv**2, 1.0, n)
    return np.cumsum(g / g.sum() * total)

def peak(W, a, b, e0=0.0, e1=0.0):
    """W given as the PEAK width -> the formula's scale factor."""
    t = np.linspace(0, 1, 401)
    return W / width_profile(t, 1.0, a, b, e0, e1).max()

def swirl(seed, C=(350, 350)):
    rng = np.random.default_rng(seed)
    t0, t1 = np.radians(rng.uniform(160, 200)), np.radians(rng.uniform(370, 410))
    r_tail, r_head = rng.uniform(120, 150), rng.uniform(190, 230)
    bul = rng.uniform(5, 25)
    body = dict(theta0=t0, theta1=t1, spine=[r_tail, r_tail + bul, r_head + bul, r_head],
                a=rng.uniform(1.1, 1.6), b=rng.uniform(0.3, 0.5))  # needle tail (a>1), round head (b<1)
    body["W"] = peak(rng.uniform(60, 80), body["a"], body["b"])
    shapes = {"amber": [], "yellow": [], "pink": [], "crimson": []}
    # amber rim = same stroke, a few px fatter (outline drawn under the body)
    rim = dict(body); rim["W"] = body["W"] * 1.08; rim["spine"] = [s + 2.0 for s in body["spine"]]
    shapes["amber"].append(rim)
    shapes["yellow"].append(body)
    # pink: inner layer = same spine pushed inwards, thinner, longer tail
    inner = dict(body); inner["W"] = body["W"] * rng.uniform(0.5, 0.6)
    inner["spine"] = [s - 16 for s in body["spine"]]; inner["theta1"] = t1 - np.radians(rng.uniform(25, 45))
    shapes["pink"].append(inner)
    # pink tongues: grow from the pink layer outwards INTO yellow, tip pointing back against the sweep
    n = rng.integers(4, 7)
    pos = t0 + np.radians(25) + gaps(rng, n, (inner["theta1"] - t0) * 0.8)
    lens = rhythm(rng, n, mean=rng.uniform(60, 85))
    for th, L in zip(pos, lens):
        tt = (th - t0) / (t1 - t0)
        rc = float(bern(inner["spine"], np.array([tt]))[0])
        wi = float(width_profile(np.array([tt]), inner["W"], inner["a"], inner["b"])[0])
        dth = L / rc
        lean = rng.uniform(0.6, 1.1) * wi + 8
        tb = np.array([max((th - dth - t0) / (t1 - t0), 0.0)])  # keep the tip inside the yellow: flames lick inside
        hi_b = float(bern(body["spine"], tb)[0] + width_profile(tb, body["W"], body["a"], body["b"])[0] / 2)
        lean = max(min(lean, hi_b - 7 - rc), 0.0)  # how far outwards the tip leans (into the yellow)
        a = rng.uniform(0.6, 1.4)  # <1 convex flame, >1 concave needle-like tongue
        shapes["pink"].append(dict(theta0=th - dth, theta1=th + 0.25 * dth, spine=[rc + lean, rc + lean * 0.5, rc, rc - wi * 0.1],
                                   W=peak(min(L / rng.uniform(2.0, 3.0), wi * 1.1), a, 0.4, 0.0, 0.1), a=a, b=0.4, e0=0.0, e1=0.1))
    # crimson: deepest inner sliver + needle tail running past the body
    core = dict(theta0=t0 - np.radians(rng.uniform(10, 25)), theta1=inner["theta1"] - np.radians(rng.uniform(10, 30)),
                spine=[s - 26 for s in body["spine"]], a=rng.uniform(1.4, 2.2), b=0.6)
    core["W"] = peak(rng.uniform(14, 22), core["a"], core["b"])
    shapes["crimson"].append(core)
    return shapes

def render(shapes, C=(350, 350)):
    col = {"amber": "#feac4c", "yellow": "#ffd670", "pink": "#ff628c", "crimson": "#d12f57"}
    body = "".join(f'<path fill="{col[k]}" d="{" ".join(path_d(stroke_path(p, C)) for p in v)}"/>' for k, v in shapes.items())
    return svg_doc(700, 700, body, "#141414")

if __name__ == "__main__":
    tiles = []
    for seed in (1, 2, 3):
        svg = render(swirl(seed))
        (OUT / "out").mkdir(exist_ok=True)
        (OUT / "out" / f"generated_seed{seed}.svg").write_text(svg)
        tiles.append(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert("RGB"))
    sheet = Image.new("RGB", (2100, 700))
    for i, t in enumerate(tiles):
        sheet.paste(t, (700 * i, 0))
    sheet.resize((1050, 350), Image.LANCZOS).save(OUT / "generated_demo.png")
    print("wrote generated_demo.png")
