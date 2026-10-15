#!/usr/bin/env python3
"""Image-to-video clips via fal.ai, for the video-sprite skill (.claude/skills/video-sprite).

Usage:
  python scripts/fal_video.py video --prompt-file P --reference start.png --out-dir D
                                    [--last-frame end.png] [--duration 5] [--resolution 480p]
                                    [--model luma-ray-3.2] [--max-usd 0.60] [--dry-run]
  python scripts/fal_video.py fetch --job D/job.json       # recover a paid clip after a timeout
  python scripts/fal_video.py models                       # curated models, prices, the default

Same argv and output as agent-sprite-forge's route_media.py video, so sprite_set.py calls it as its
media CLI: stdout is ONE JSON line {status, route, artifact, sha256, estimateUsd, lastFrameUsed, ...};
errors go to stderr as "error: ..." and exit 1; exit 3 = no route (FAL_KEY missing).

Model: --model, else FAL_VIDEO_MODEL (env or .env), else the default in fal_video_models.json.
Duration and resolution snap to what the model renders (a note says so). The clip's estimated cost
must stay under --max-usd (env FAL_VIDEO_MAX_USD, default 0.60) or nothing is sent.
Every clip is logged to out/costs.csv and gets a job.json (prompt, model, request id, cost).
Needs FAL_KEY in the environment or in .env at the project root (never printed).
"""
import argparse, csv, hashlib, json, os, pathlib, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELS_FILE = pathlib.Path(__file__).resolve().parent / "fal_video_models.json"
EXIT_NO_ROUTE = 3
DEFAULT_MAX_USD = 0.60


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


def fail(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def load_models() -> dict:
    return json.loads(MODELS_FILE.read_text(encoding="utf-8"))


def pick_model(name: str | None, table: dict) -> tuple[str, dict]:
    name = name or os.environ.get("FAL_VIDEO_MODEL") or table["default"]
    models = table["models"]
    if name in models:
        return name, models[name]
    for key, spec in models.items():   # an endpoint id works too
        if spec["endpoint"] == name:
            return key, spec
    fail(f"unknown model {name!r}; choose one of {', '.join(models)} (python scripts/fal_video.py models)")


def snap_duration(seconds: float, spec: dict) -> tuple[int, str | None]:
    d = spec["duration"]
    want = max(1, round(seconds))
    if "values" in d:
        got = min(d["values"], key=lambda v: (abs(v - want), v))
    else:
        got = min(max(want, d["min"]), d["max"])
    return got, (None if got == want else f"duration {want}s snapped to {got}s for this model")


def duration_value(seconds: int, spec: dict):
    fmt = spec["duration"]["format"]
    return seconds if fmt == "int" else str(seconds) if fmt == "str" else fmt.format(seconds)


def price_key(spec: dict, resolution: str | None) -> str:
    prices = spec["usd_per_s"]
    return "any" if "any" in prices else resolution


def nearest_aspect(size: tuple[int, int], values: list[str]) -> str:
    ratio = size[0] / size[1]
    def gap(v: str) -> float:
        w, h = (int(x) for x in v.split(":"))
        return abs(ratio - w / h)
    return min(values, key=gap)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def build_request(a, key: str, spec: dict, prompt: str) -> tuple[dict, dict]:
    """(arguments with local paths in the image fields, plan facts: seconds, resolution, cost, notes)."""
    from PIL import Image  # late import keeps --help fast
    notes = []
    seconds, note = snap_duration(a.duration, spec)
    if note:
        notes.append(note)
    args = {"prompt": prompt, spec["duration"]["field"]: duration_value(seconds, spec), **spec.get("fixed", {})}
    resolution = None
    if "resolution" in spec:
        mapping = spec["resolution"]["map"]
        if a.resolution not in mapping:
            fail(f"--resolution {a.resolution} is not one of {', '.join(mapping)} for {key}")
        resolution = mapping[a.resolution]
        args[spec["resolution"]["field"]] = resolution
    with Image.open(a.reference) as im:
        size = im.size
    if "aspect" in spec:
        args[spec["aspect"]["field"]] = nearest_aspect(size, spec["aspect"]["values"])
    args[spec["first"]] = a.reference
    last_used = False
    if not a.last_frame and spec.get("last_required"):
        a.last_frame = a.reference
        notes.append("this model needs an end frame: the start frame was sent, so the clip loops")
    if a.last_frame:
        same = sha256_file(pathlib.Path(a.last_frame)) == sha256_file(pathlib.Path(a.reference))
        if same and spec.get("loop_field"):
            args[spec["loop_field"]] = True
            notes.append("last frame = first frame: sent as the model's loop flag")
            last_used = True
        elif spec.get("last"):
            args[spec["last"]] = a.last_frame
            last_used = True
    rate = spec["usd_per_s"][price_key(spec, resolution)]
    facts = {"seconds": seconds, "resolution": resolution or "model default", "size": list(size),
             "estimateUsd": round(rate * seconds, 4), "lastFrameUsed": last_used, "notes": notes}
    return args, facts


def log_cost(artifact: pathlib.Path, key: str, facts: dict, elapsed: float) -> None:
    """One row in out/costs.csv, same columns as gen_image.py (quality column = 'video')."""
    log_path = ROOT / "out" / "costs.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    new_log = not log_path.exists()
    shown = artifact.resolve()
    shown = shown.relative_to(ROOT).as_posix() if shown.is_relative_to(ROOT) else artifact.name
    with log_path.open("a", newline="", encoding="utf-8") as fh:
        log = csv.writer(fh)
        if new_log:
            log.writerow(["time", "file", "model", "quality", "size", "transparent", "seconds", "cost_usd", "approx"])
        log.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), shown, key, "video",
                      f"{facts['resolution']} {facts['seconds']}s", False, elapsed, f"{facts['estimateUsd']:.4f}", True])


def download(url: str, out_dir: pathlib.Path) -> pathlib.Path:
    import requests
    path = out_dir / "clip.mp4"
    r = requests.get(url, timeout=300); r.raise_for_status()
    path.write_bytes(r.content)
    return path


def video_url(result: dict) -> str:
    video = result.get("video")
    url = video.get("url") if isinstance(video, dict) else None
    if not url:
        fail(f"no video in the fal.ai result: {json.dumps(result)[:400]}")
    return url


def summary(artifact: pathlib.Path, key: str, spec: dict, facts: dict, **extra) -> None:
    print(json.dumps({"status": "ok", "route": f"fal:{spec['endpoint']}", "model": key,
                      "artifact": str(artifact.resolve()), "sha256": sha256_file(artifact),
                      "estimateUsd": facts["estimateUsd"], "lastFrameUsed": facts["lastFrameUsed"],
                      "seconds": facts["seconds"], "resolution": facts["resolution"], "notes": facts["notes"],
                      **extra}, ensure_ascii=True))


def cmd_video(a) -> None:
    table = load_models()
    key, spec = pick_model(a.model, table)
    prompt = pathlib.Path(a.prompt_file).read_text(encoding="utf-8").strip()
    for p in [a.reference] + ([a.last_frame] if a.last_frame else []):
        if not pathlib.Path(p).is_file():
            fail(f"input image not found: {p}")
    args, facts = build_request(a, key, spec, prompt)
    cap = a.max_usd if a.max_usd is not None else float(os.environ.get("FAL_VIDEO_MAX_USD", DEFAULT_MAX_USD))
    if facts["estimateUsd"] > cap:
        fail(f"{key} {facts['seconds']}s at {facts['resolution']} is ~${facts['estimateUsd']:.2f}, over the "
             f"${cap:.2f} cap per clip (--max-usd or FAL_VIDEO_MAX_USD); nothing was sent")
    out_dir = pathlib.Path(a.out_dir)
    if a.dry_run:
        shown = {k: (pathlib.Path(v).name if k in (spec["first"], spec.get("last")) else v) for k, v in args.items()}
        print(json.dumps({"status": "dry-run", "model": key, "endpoint": spec["endpoint"], "arguments": shown,
                          **facts}, ensure_ascii=True))
        return
    if not os.environ.get("FAL_KEY"):
        fail("FAL_KEY is not set. Copy .env.example to .env and paste your key.", EXIT_NO_ROUTE)
    if out_dir.exists() and any(out_dir.iterdir()):
        fail(f"--out-dir {out_dir} is not empty")
    out_dir.mkdir(parents=True, exist_ok=True)

    import fal_client  # imported late so --help and --dry-run work without it
    for field in (spec["first"], spec.get("last")):   # free CDN uploads before the paid request
        if field and field in args:
            args[field] = fal_client.upload_file(args[field])
    job = {"prompt": prompt, "model": key, "endpoint": spec["endpoint"],
           "arguments": {k: v for k, v in args.items() if k != "prompt"}, **facts,
           "reference": str(pathlib.Path(a.reference).resolve()),
           "lastFrame": str(pathlib.Path(a.last_frame).resolve()) if a.last_frame else None}
    job_path = out_dir / "job.json"
    t0 = time.time()
    try:
        handle = fal_client.submit(spec["endpoint"], arguments=args)
        job["requestId"] = handle.request_id   # kept before waiting: a timeout never loses a paid clip
        job_path.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
        result = handle.get()
    except Exception as e:  # surface API errors clearly for the agent
        if "requestId" in job:
            fail(f"fal.ai request {job['requestId']} failed or timed out: {e}. If it was charged, recover it with "
                 f"python scripts/fal_video.py fetch --job {job_path}")
        fail(f"fal.ai request failed: {e}")
    elapsed = round(time.time() - t0, 1)
    artifact = download(video_url(result), out_dir)
    job.update(seconds_elapsed=elapsed, source_url=video_url(result), cost_is_estimate=True)
    job_path.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
    log_cost(artifact, key, facts, elapsed)
    print(f"cost: ~${facts['estimateUsd']:.4f} for 1 clip [{key}, {facts['resolution']}, {facts['seconds']}s] "
          f"in {elapsed}s", file=sys.stderr)
    summary(artifact, key, spec, facts, requestId=job["requestId"])


def cmd_fetch(a) -> None:
    job_path = pathlib.Path(a.job)
    job = json.loads(job_path.read_text(encoding="utf-8"))
    if not job.get("requestId"):
        fail(f"{job_path} has no requestId")
    if not os.environ.get("FAL_KEY"):
        fail("FAL_KEY is not set.", EXIT_NO_ROUTE)
    import fal_client
    result = fal_client.result(job["endpoint"], job["requestId"])
    artifact = download(video_url(result), job_path.parent)
    log_cost(artifact, job["model"], job, 0)
    key, spec = pick_model(job["model"], load_models())
    summary(artifact, key, spec, job, requestId=job["requestId"], recovered=True)


def cmd_models(_a) -> None:
    table = load_models()
    for key, spec in table["models"].items():
        prices = ", ".join(f"{r} ${v}/s" for r, v in spec["usd_per_s"].items())
        mark = " (default)" if key == table["default"] else ""
        print(f"{key}{mark}: {spec['endpoint']} | {prices} | {spec.get('note', '')}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("video", help="one image-to-video clip")
    v.add_argument("--prompt-file", required=True)
    v.add_argument("--reference", required=True, help="start frame (the master placed on the action canvas)")
    v.add_argument("--last-frame", help="end frame; equal to the start = a loop where the model has a loop flag")
    v.add_argument("--duration", type=float, default=5)
    v.add_argument("--resolution", default="480p")
    v.add_argument("--out-dir", required=True)
    v.add_argument("--model")
    v.add_argument("--max-usd", type=float)
    v.add_argument("--dry-run", action="store_true", help="print the request and its cost, send nothing")
    f = sub.add_parser("fetch", help="download the result of a job.json whose request id is known")
    f.add_argument("--job", required=True)
    sub.add_parser("models", help="list the curated models")
    a = p.parse_args()
    load_dotenv(ROOT / ".env")
    {"video": cmd_video, "fetch": cmd_fetch, "models": cmd_models}[a.cmd](a)


if __name__ == "__main__":
    main()
