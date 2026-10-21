#!/usr/bin/env python3
"""Generate images via fal.ai (OpenAI GPT Image models).

Usage:
  python scripts/gen_image.py "prompt..." [--model gpt-image-2] [--quality low]
                              [--size 1024x1024|1024x1536|1536x1024] [--transparent]
                              [--name goblin_walk] [--n 1] [--out out]
                              [--ref master.png ...] [--png] [--versioned]
                              [--prompt-file prompt.txt]   (long prompt from a file instead of the argument)

--transparent needs gpt-image-1.5 (gpt-image-2 rejects it on fal), so the script
switches model automatically.  --ref sends local image(s) to the model's edit
endpoint as visual reference (used to keep a character consistent across sheets).

Needs FAL_KEY in the environment or in a .env file at the project root.
stdout: one saved image path per line (nothing else).
stderr: a cost line per run.  Every image is also logged to out/costs.csv,
and gets a .json sidecar with prompt, settings and estimated cost.
"""
import argparse, csv, json, math, os, pathlib, re, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent

MODELS = {
    "gpt-image-2":      "openai/gpt-image-2",
    "gpt-image-1.5":    "fal-ai/gpt-image-1.5",
    "gpt-image-1-mini": "fal-ai/gpt-image-1-mini",
}
EDIT_MODELS = {
    "gpt-image-2":   "openai/gpt-image-2/edit",
    "gpt-image-1.5": "fal-ai/gpt-image-1.5/edit",
}

# Estimated USD per image from fal.ai model pages (Oct 2026).
# "sq" = 1024x1024, "other" = any other size, or an exact size key.
PRICES = {
    "gpt-image-2": {"low": {"sq": 0.01, "other": 0.01}, "medium": {"sq": 0.06, "other": 0.05},
                    "high": {"sq": 0.22, "other": 0.17}, "text_per_tok": 5 / 1e6, "approx": True},
    "gpt-image-1.5": {"low": {"sq": 0.009, "other": 0.013},
                      "medium": {"sq": 0.034, "1024x1536": 0.051, "1536x1024": 0.050},
                      "high": {"sq": 0.133, "1024x1536": 0.200, "1536x1024": 0.199},
                      "text_per_tok": 0.005 / 1000},
    "gpt-image-1-mini": {"low": {"sq": 0.005, "other": 0.006}, "medium": {"sq": 0.011, "other": 0.015},
                         "high": {"sq": 0.036, "other": 0.052}, "text_per_tok": 0.002 / 1000,
                         "round_cent": True},
}
FIXED_SIZES = {"1024x1024", "1536x1024", "1024x1536"}


def estimate_cost(model: str, quality: str, size: str, prompt: str) -> float:
    t = PRICES[model]; q = t[quality]
    price = q["sq"] if size == "1024x1024" else q.get(size, q.get("other"))
    price += math.ceil(len(prompt) / 4) * t["text_per_tok"]
    if t.get("round_cent"):
        price = math.ceil(price * 100 - 1e-9) / 100
    return price


def load_dotenv(path: pathlib.Path) -> None:
    """Minimal .env loader (no extra dependency). Existing env vars win."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def parse_size(s: str, model: str) -> str:
    s = s.strip().lower()
    try:
        w, h = (int(x) for x in s.split("x"))
    except ValueError:
        sys.exit(f"Bad --size '{s}'. Use WxH, e.g. 1024x1024, 1024x1536, 1536x1024")
    if model != "gpt-image-2" and s not in FIXED_SIZES:
        sys.exit(f"{model} only supports {', '.join(sorted(FIXED_SIZES))}")
    problems = []
    if w % 16 or h % 16:
        problems.append("both sides must be multiples of 16")
    if max(w, h) > 3840:
        problems.append("longest side must be <= 3840")
    if max(w, h) / min(w, h) > 3:
        problems.append("aspect ratio must be <= 3:1")
    if not 655_360 <= w * h <= 8_294_400:
        problems.append("total pixels must be between 655,360 and 8,294,400")
    if problems:
        sys.exit(f"Bad --size {s}: " + "; ".join(problems))
    return s


def next_version(folder: pathlib.Path, stem: str) -> int:
    """1 + the highest NN among <stem>_vNN.* files in folder."""
    nums = [int(m.group(1)) for f in folder.glob(f"{stem}_v*.*")
            if (m := re.fullmatch(re.escape(stem) + r"_v(\d+)\.\w+", f.name))]
    return max(nums, default=0) + 1


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("prompt", nargs="?", default="")
    p.add_argument("--prompt-file", help="read the prompt from this UTF-8 file (long prompts; avoids shell quoting)")
    p.add_argument("--model", default="gpt-image-2", choices=MODELS.keys())
    p.add_argument("--quality", default="low", choices=["low", "medium", "high"])
    p.add_argument("--size", default="1024x1024")
    p.add_argument("--transparent", action="store_true", help="transparent background, saved as PNG (for sprites)")
    p.add_argument("--name", default="", help="filename prefix, e.g. goblin_walk")
    p.add_argument("--n", type=int, default=1, choices=range(1, 5), metavar="1-4")
    p.add_argument("--out", default=str(ROOT / "out"))
    p.add_argument("--ref", action="append", default=[], help="local reference image (repeatable)")
    p.add_argument("--png", action="store_true", help="save PNG instead of JPEG (lossless, for chroma-key sheets)")
    p.add_argument("--versioned", action="store_true",
                   help="name files <name>_vNN.<ext> with the next free NN in --out (asset pipeline)")
    a = p.parse_args()
    if a.prompt_file:
        if a.prompt:
            sys.exit("give the prompt either as the argument or with --prompt-file, not both")
        a.prompt = pathlib.Path(a.prompt_file).read_text(encoding="utf-8").strip()
    if not a.prompt:
        sys.exit("no prompt: pass it as the first argument or with --prompt-file")
    print(f"prompt: {a.prompt[:60]!r}... ({len(a.prompt)} chars)", file=sys.stderr)
    if a.versioned and not a.name:
        sys.exit("--versioned needs --name")

    if a.transparent and a.model == "gpt-image-2":
        a.model = "gpt-image-1.5"
        print("note: gpt-image-2 has no transparent background on fal; using gpt-image-1.5", file=sys.stderr)
    if a.ref and a.model not in EDIT_MODELS:
        sys.exit(f"--ref is not supported with {a.model}; use gpt-image-1.5 or gpt-image-2")
    for r in a.ref:
        if not pathlib.Path(r).is_file():
            sys.exit(f"--ref file not found: {r}")
    size = parse_size(a.size, a.model)
    load_dotenv(ROOT / ".env")
    if not os.environ.get("FAL_KEY"):
        sys.exit("FAL_KEY is not set. Copy .env.example to .env and paste your key.")

    import fal_client, requests  # imported late so --help works without them

    w, h = (int(x) for x in size.split("x"))
    args = {
        "prompt": a.prompt,
        "quality": a.quality,
        "image_size": {"width": w, "height": h} if a.model == "gpt-image-2" else size,
        "num_images": a.n,
        "background": "transparent" if a.transparent else "auto",
        "output_format": "png" if a.transparent or a.png else "jpeg",
    }
    endpoint = MODELS[a.model]
    t0 = time.time()
    try:
        if a.ref:
            endpoint = EDIT_MODELS[a.model]
            args["image_urls"] = [fal_client.upload_file(r) for r in a.ref]
            if a.model == "gpt-image-1.5":
                args["input_fidelity"] = "high"
        result = fal_client.subscribe(endpoint, arguments=args, with_logs=False)
    except Exception as e:  # surface API errors clearly for the agent
        sys.exit(f"fal.ai request failed: {e}")
    elapsed = round(time.time() - t0, 1)

    images = result.get("images") or []
    if not images:
        sys.exit(f"No images returned. Raw response: {json.dumps(result)[:500]}")

    unit = estimate_cost(a.model, a.quality, size, a.prompt)
    approx = PRICES[a.model].get("approx", False) or bool(a.ref)  # reference images add input-token cost
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    prefix = "".join(c if c.isalnum() or c in "-_" else "_" for c in a.name.strip())[:40]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    log_path = ROOT / "out" / "costs.csv"  # one spend log, whatever --out is
    log_path.parent.mkdir(parents=True, exist_ok=True)
    new_log = not log_path.exists()
    with log_path.open("a", newline="", encoding="utf-8") as fh:
        log = csv.writer(fh)
        if new_log:
            log.writerow(["time", "file", "model", "quality", "size", "transparent", "seconds", "cost_usd", "approx"])
        for i, img in enumerate(images):
            ext = "png" if a.transparent or a.png else "jpg"
            if a.versioned:
                path = out / f"{prefix}_v{next_version(out, prefix):02d}.{ext}"
            else:
                path = out / f"{prefix + '-' if prefix else ''}{stamp}-{i}.{ext}"
            meta = {"prompt": a.prompt, "model": endpoint, "quality": a.quality, "size": size,
                    "refs": [str(pathlib.Path(r).resolve()) for r in a.ref],
                    "transparent": a.transparent, "seconds": elapsed, "cost_usd": round(unit, 4),
                    "cost_is_estimate": True, "source_url": img["url"]}
            path.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            # the image is already paid for: the sidecar (with source_url) is written first, then the download is
            # retried; on failure the URL stays on disk and on stderr so it can be fetched later
            for attempt in range(3):
                try:
                    r = requests.get(img["url"], timeout=120); r.raise_for_status()
                    path.write_bytes(r.content)
                    break
                except Exception as e:
                    if attempt == 2:
                        print(f"download failed ({e}); paid image kept at {img['url']} (see {path.with_suffix('.json').name}); "
                              f"fetch it later, e.g. allow *.fal.media in the network policy", file=sys.stderr)
                    else:
                        time.sleep(2 * (attempt + 1))
            shown = path.resolve().relative_to(ROOT).as_posix() if path.resolve().is_relative_to(ROOT) else path.name
            log.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), shown, a.model, a.quality, size,
                          a.transparent, elapsed, f"{unit:.4f}", approx])
            if path.exists():
                print(path)
    total = unit * len(images)
    print(f"cost: {'~' if approx else ''}${total:.4f} for {len(images)} image(s) "
          f"[{a.model}, {a.quality}, {size}] in {elapsed}s", file=sys.stderr)


if __name__ == "__main__":
    main()
