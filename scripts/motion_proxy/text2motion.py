"""Chữ -> chuyển động 3D người bằng HY-Motion trên fal.ai (fal-ai/hunyuan-motion[/fast]).

    python scripts/motion_proxy/text2motion.py --asset out/heroes/<id> --name <skill> \
        --prompt "<tiếng Anh>" [--prompt-vi "<câu gốc>"] --seeds 1 2 3 [--model fast|full]

Mỗi seed ghi vào <asset>/.work/motion_proxy/t2m/<skill>/seed<N>/: result.json (nguyên văn fal trả về),
các file đầu ra (FBX, JSON chuyển động) và job.json (prompt, model, seed, chi phí).
Mỗi lần gọi ghi một dòng vào out/costs.csv (cột quality = 'motion').
Doc: docs/scripts/motion_proxy/motion-proxy-guide.md
"""
import argparse
import csv
import json
import os
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODELS = {
    "fast": {"endpoint": "fal-ai/hunyuan-motion/fast", "usd": 0.06},
    "full": {"endpoint": "fal-ai/hunyuan-motion", "usd": None},   # giá chưa xác minh: hỏi trước khi chạy
}


def log_cost(artifact, key, usd, elapsed, approx):
    log_path = ROOT / "out" / "costs.csv"
    new_log = not log_path.exists()
    shown = pathlib.Path(artifact).resolve()
    shown = shown.relative_to(ROOT).as_posix() if shown.is_relative_to(ROOT) else shown.name
    with log_path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new_log:
            w.writerow(["time", "file", "model", "quality", "size", "transparent", "seconds", "cost_usd", "approx"])
        w.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), shown, key, "motion", "", False, round(elapsed, 1),
                    f"{usd:.4f}" if usd is not None else "", approx])


def file_urls(obj, path=""):
    """Mọi {url: ...} hoặc chuỗi http trong kết quả, kèm đường dẫn khoá."""
    out = []
    if isinstance(obj, dict):
        if isinstance(obj.get("url"), str) and obj["url"].startswith("http"):
            out.append((path or "file", obj["url"], obj.get("file_name") or obj.get("content_type")))
        for k, v in obj.items():
            if k != "url":
                out += file_urls(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += file_urls(v, f"{path}[{i}]")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--asset", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--prompt-vi", default="")
    ap.add_argument("--seeds", type=int, nargs="+", default=[1])
    ap.add_argument("--model", choices=sorted(MODELS), default="fast")
    ap.add_argument("--extra", default="{}", help="tham số thêm cho fal, dạng JSON")
    a = ap.parse_args()
    if not os.environ.get("FAL_KEY"):
        raise SystemExit("FAL_KEY chưa có trong môi trường")
    spec = MODELS[a.model]
    import fal_client
    import requests
    base = pathlib.Path(a.asset) / ".work" / "motion_proxy" / "t2m" / a.name
    for seed in a.seeds:
        out = base / f"seed{seed}"
        out.mkdir(parents=True, exist_ok=True)
        args = {"prompt": a.prompt, "seed": seed, **json.loads(a.extra)}
        t0 = time.time()
        result = fal_client.subscribe(spec["endpoint"], arguments=args, with_logs=False)
        dt = time.time() - t0
        (out / "result.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
        saved = []
        for key, url, hint in file_urls(result):
            name = url.split("?")[0].rsplit("/", 1)[-1] or key
            r = requests.get(url, timeout=300)
            r.raise_for_status()
            (out / name).write_bytes(r.content)
            saved.append({"key": key, "file": name, "bytes": len(r.content)})
        job = {"endpoint": spec["endpoint"], "seed": seed, "arguments": args, "prompt_vi": a.prompt_vi,
               "estimate_usd": spec["usd"], "seconds": round(dt, 1), "files": saved}
        (out / "job.json").write_text(json.dumps(job, indent=1, ensure_ascii=False), encoding="utf-8")
        log_cost(out / "result.json", spec["endpoint"], spec["usd"], dt, True)
        print(f"seed {seed}: {dt:.1f}s, {len(saved)} file -> {out}")
        for s in saved:
            print("   ", s)


if __name__ == "__main__":
    main()
