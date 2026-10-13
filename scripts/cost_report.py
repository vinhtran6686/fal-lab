#!/usr/bin/env python3
"""Summarise estimated fal.ai spend from out/costs.csv.

Usage: python scripts/cost_report.py [--today] [--csv out/costs.csv]
"""
import argparse, csv, pathlib, sys, time
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    p = argparse.ArgumentParser()
    p.add_argument("--today", action="store_true", help="only count images made today")
    p.add_argument("--csv", default=str(ROOT / "out" / "costs.csv"))
    a = p.parse_args()
    path = pathlib.Path(a.csv)
    if not path.exists():
        sys.exit("No images generated yet (out/costs.csv not found).")

    today = time.strftime("%Y-%m-%d")
    by_key, total, count, approx = defaultdict(lambda: [0, 0.0]), 0.0, 0, False
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if a.today and not row["time"].startswith(today):
                continue
            cost = float(row["cost_usd"])
            k = f"{row['model']} · {row['quality']} · {row['size']}"
            by_key[k][0] += 1; by_key[k][1] += cost
            total += cost; count += 1
            approx |= row.get("approx") == "True"

    scope = "today" if a.today else "all time"
    print(f"Estimated fal.ai spend ({scope}): {'~' if approx else ''}${total:.4f} for {count} image(s)")
    for k, (n, c) in sorted(by_key.items(), key=lambda kv: -kv[1][1]):
        print(f"  {k:<40} {n:>4} img  ${c:.4f}")
    print("Estimates from public fal.ai prices. Real charges: fal.ai dashboard → Billing.")


if __name__ == "__main__":
    main()
