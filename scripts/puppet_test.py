#!/usr/bin/env python3
"""Regression test of the Puppet Kit: every listed animation must render to the same frames as recorded.
  python scripts/puppet_test.py            # compare with scripts/puppet_kit/golden.json, exit 1 on any difference
  python scripts/puppet_test.py --update   # record the current frames as the new reference
"""
import argparse, hashlib, importlib.util, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("puppet_cli", ROOT / "scripts" / "puppet.py")
pp = importlib.util.module_from_spec(spec); spec.loader.exec_module(pp)
from puppet_kit.core import Animation  # noqa: E402

GOLDEN = ROOT / "scripts" / "puppet_kit" / "golden.json"

def cases():
    """Every anims/*.json of every asset that has source/rig/anims/."""
    for anim in sorted(ROOT.glob("out/*/*/source/rig/anims/*.json")):
        yield anim.parents[3], anim          # asset dir, anim path

def digest(asset, anim_path):
    meta = json.loads((asset / "meta.json").read_text(encoding="utf-8"))
    cells, _, _ = pp.render_frames(asset, Animation(anim_path, asset), meta)
    h = hashlib.sha256()
    for c in cells:
        h.update(c.tobytes())
    return h.hexdigest(), len(cells)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true", help="Record current frames as the new reference")
    args = parser.parse_args()

    results = {}
    for asset, anim_path in cases():
        try:
            sha256_hash, frame_count = digest(asset, anim_path)
            # Store key as relative posix path from ROOT
            key = anim_path.relative_to(ROOT).as_posix()
            results[key] = {"sha256": sha256_hash, "frames": frame_count}
        except Exception as e:
            print(f"ERROR {anim_path}: {e}", file=sys.stderr)
            sys.exit(1)

    if args.update:
        # Write golden.json with sorted keys, indent 1
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        golden_data = dict(sorted(results.items()))
        GOLDEN.write_text(json.dumps(golden_data, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"{len(results)} case(s) recorded")
        sys.exit(0)
    else:
        # Compare with golden.json
        if not GOLDEN.exists():
            print("ERROR: golden.json not found. Run with --update first.", file=sys.stderr)
            sys.exit(1)

        golden = json.loads(GOLDEN.read_text(encoding="utf-8"))

        ok_count = 0
        diff_count = 0
        new_count = 0
        all_keys = set(results.keys()) | set(golden.keys())

        for key in sorted(all_keys):
            if key not in golden:
                print(f"NEW  {key}")
                new_count += 1
            elif results[key] != golden[key]:
                print(f"DIFF {key}")
                diff_count += 1
            else:
                print(f"ok  {key}")
                ok_count += 1

        print(f"\nTotal: {ok_count} ok, {diff_count} diff, {new_count} new")

        if diff_count > 0 or new_count > 0:
            sys.exit(1)
        sys.exit(0)

if __name__ == "__main__":
    main()
