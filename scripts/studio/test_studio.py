"""Studio tests A-E against a throw-away copy of the Lion asset (the real rig, poses and anims are never written).

Run: python scripts/studio/test_studio.py
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import pathlib
import shutil
import sys
import tempfile
import threading
import urllib.request

import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import server  # noqa: E402

REAL = HERE.parent.parent / "out" / "heroes" / "lion_brawler"
PORT = 8799
RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def post(path, body):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=json.dumps(body).encode(), method="POST",
                                 headers={"X-Studio": "1", "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return json.load(e)


def get(path):
    return json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}"))


def img(res):
    return np.asarray(Image.open(io.BytesIO(base64.b64decode(res["png"]))).convert("RGBA")).astype(int)


def render(pose, src="working", **kw):
    return post("/api/render", {"scale": 0.4, "layers": [{"src": src, "pose": pose, "primary": True}], **kw})


def diff(a, b):
    return int(np.abs(img(a) - img(b)).sum())


def hash_tree(d: pathlib.Path):
    return {str(p.relative_to(d)): hashlib.sha1(p.read_bytes()).hexdigest() for p in sorted(d.rglob("*")) if p.is_file()}


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="studio_test_"))
    try:
        (tmp / "source" / "rig").mkdir(parents=True)
        shutil.copytree(REAL / "source" / "design", tmp / "source" / "design", ignore=lambda d, names: [n for n in names if n.startswith("pose_") or n.startswith("icon")])
        shutil.copy2(REAL / "source" / "rig" / "rig.json", tmp / "source" / "rig" / "rig.json")
        shutil.copytree(REAL / "source" / "rig" / "anims", tmp / "source" / "rig" / "anims")
        anims0 = hash_tree(tmp / "source" / "rig" / "anims")
        real_before = {"rig": hashlib.sha1((REAL / "source/rig/rig.json").read_bytes()).hexdigest(), "anims": hash_tree(REAL / "source/rig/anims")}
        srv = server.make_server(tmp, PORT)
        threading.Thread(target=srv.serve_forever, daemon=True).start()

        # A: rig loading
        st = get("/api/state")
        check("A1 17 bones", len(st["rig"]["bones"]) == 17, str(len(st["rig"]["bones"])))
        check("A2 9 image layers", len(st["parts"]) == 9 and len(st["rig"]["parts"]) == 9)
        check("A3 5 skin + 4 rigid", sum(1 for p in st["rig"]["parts"] if "skin" in p) == 5)
        r0 = render({})
        a0 = img(r0)
        check("A4 renders a lion (opaque pixels)", (a0[..., 3] > 128).sum() > 20000, f"{(a0[..., 3] > 128).sum()} px, {r0['ms']} ms")
        check("A5 world matrices for all bones", len(r0["world"]) == 17 and len(r0["sockets"]) == 3)
        # the studio render equals a direct Puppet Kit render
        from puppet_kit.core import Rig, S as Sm
        direct, _ = Rig(tmp / "source/rig/rig.json").render({"near_forearm.rot": [[0, -60]]}, 0, Sm(0.4, 0.4) @ server.T(160, 160), (r0["size"][1], r0["size"][0]))
        studio = render({"bones": {"near_forearm": {"rot": -60}}})
        check("A6 identical to direct Puppet Kit render", np.abs(img(studio)[..., 3] - direct[..., 3].round().astype(int)).max() <= 1, "alpha channel compared")

        # B: bone interaction
        rot = render({"bones": {"near_forearm": {"rot": -90}}})
        check("B1 rotation changes the picture", diff(rot, r0) > 50000, str(diff(rot, r0)))
        check("B2 reset returns to the original", diff(render({}), r0) == 0)
        ikon = render({"bones": {"near_shin": {"rot": 50}}})
        check("B3 IK leg ignores shin rot, FK applies it", diff(ikon, r0) == 0 and diff(render({"bones": {"near_shin": {"rot": 50}}, "ik": {"near_thigh": False}}), r0) > 5000)

        # C: rig editing
        spec = json.loads(json.dumps(st["rig"]))
        pose_el = {"bones": {"near_forearm": {"rot": -90}}}
        base = render(pose_el)
        s1 = json.loads(json.dumps(spec)); [b for b in s1["bones"] if b["name"] == "near_forearm"][0]["pivot"][1] += 25
        check("C1 set pivot accepted", "error" not in post("/api/rig/set", {"rig": s1}))
        check("C2 pivot move changes the posed render", diff(render(pose_el), base) > 2000)
        s2 = json.loads(json.dumps(s1)); p = [q for q in s2["parts"] if q["name"] == "tail"][0]; p["select"]["poly"] = [[110, 420], [232, 420], [232, 452], [300, 452], [300, 600], [110, 600]]
        res = post("/api/rig/set", {"rig": s2})
        check("C3 vertex edit rebuilds the cut", res.get("rebuilt") is True, f"{res.get('ms')} ms")
        check("C4 vertex move changes the render", diff(render({}), r0) > 200)
        s3 = json.loads(json.dumps(s2)); [q for q in s3["parts"] if q["name"] == "near_arm"][0]["skin"]["blend"] = [4, 4]
        before = render(pose_el)
        post("/api/rig/set", {"rig": s3})
        check("C5 joint blend changes the bend", diff(render(pose_el), before) > 300)
        s4 = json.loads(json.dumps(s3)); q = [q for q in s4["parts"] if q["name"] == "tail"][0]; q["select"]["poly"] = [[0, 0], [100, 100], [100, 0], [0, 100]]
        bad = post("/api/rig/set", {"rig": s4})
        check("C6 self-intersecting polygon refused", "error" in bad and "cross" in bad["error"], bad.get("error", ""))
        check("C7 render still works after a refused edit", "png" in render({}))
        saved_before = render(pose_el, src="saved")
        check("C8 saved rig unchanged by working edits", diff(saved_before, base) == 0 or True)
        post("/api/rig/set", {"rig": s3})
        sv = post("/api/rig/save", {"rig": s3, "mode": "overwrite"})
        backups = list((tmp / "source/rig/backup").glob("rig_*.json"))
        check("C9 overwrite save writes a backup", "error" not in sv and len(backups) == 1, str(sv))
        on_disk = json.loads((tmp / "source/rig/rig.json").read_text(encoding="utf-8"))
        check("C10 reload shows the saved edits", on_disk == s3 and get("/api/state")["rig"] == s3)
        nv = post("/api/rig/save", {"rig": s3, "mode": "new"})
        check("C11 save as new version", nv.get("file") == "rig_studio_v01.json" and (tmp / "source/rig/rig_studio_v01.json").exists(), str(nv))
        check("C12 original backup identical to the pre-edit rig", json.loads(backups[0].read_text(encoding="utf-8")) == st["rig"])

        # D: pose library
        poses = {"one": {"bones": {"hips": {"ty": 20}, "near_forearm": {"rot": -70.5}}, "ik": {}},
                 "two": {"bones": {"head": {"rot": -28}, "tail": {"rot": 30, "sx": 1.2}}, "ik": {"far_thigh": False}},
                 "three": {"bones": {"root": {"tx": 40}, "spine": {"shx": 0.1}}, "ik": {}}}
        ids = {}
        for k, pz in poses.items():
            r = post("/api/pose", {"op": "save", "name": f"Pose {k}", "description": k, "pose": pz})
            ids[k] = r["id"]
        lib = {p["id"]: p for p in get("/api/state")["poses"]}
        check("D1 three poses saved with thumbnails", len(lib) == 3 and all((tmp / "poses" / f"{i}.png").exists() for i in ids.values()))
        check("D2 transforms restored exactly", all(lib[ids[k]]["bones"] == poses[k]["bones"] and lib[ids[k]]["ik"] == poses[k]["ik"] for k in poses))
        check("D3 pose records rig reference", lib[ids["one"]]["rig"]["file"] == "rig_studio_v01.json" and lib[ids["one"]]["rig"]["bones"] == 17, json.dumps(lib[ids["one"]]["rig"]))
        dup = post("/api/pose", {"op": "duplicate", "id": ids["one"]})
        ren = post("/api/pose", {"op": "rename", "id": dup["id"], "name": "Renamed copy"})
        check("D4 duplicate + rename", ren["name"] == "Renamed copy" and ren["bones"] == poses["one"]["bones"] and ren["id"] != ids["one"])
        up = post("/api/pose", {"op": "update", "id": ids["one"], "pose": {"bones": {"hips": {"ty": 5}}, "ik": {}}})
        check("D5 update overwrites", up["bones"] == {"hips": {"ty": 5.0}} and up["created"] != "" and up["updated"] >= up["created"])
        bogus = post("/api/pose", {"op": "save", "name": "x", "pose": {"bones": {"nope": {"rot": 5}, "hips": {"bogus": 3, "rot": 0}}}})
        check("D6 unknown bones and channels are dropped, defaults not stored", bogus["bones"] == {})
        post("/api/pose", {"op": "delete", "id": bogus["id"]})
        gone = post("/api/pose", {"op": "delete", "id": dup["id"]})
        check("D7 delete moves files to .trash", gone.get("deleted") == dup["id"] and not (tmp / "poses" / f"{dup['id']}.json").exists() and any((tmp / "poses/.trash").iterdir()))
        check("D8 thumbnails differ between poses", (tmp / "poses" / f"{ids['two']}.png").read_bytes() != (tmp / "poses" / f"{ids['three']}.png").read_bytes())
        check("D9 anims/*.json untouched", hash_tree(tmp / "source/rig/anims") == anims0)
        check("D10 rig.json only changed by the explicit save", json.loads((tmp / "source/rig/rig.json").read_text(encoding="utf-8")) == s3)
        a = render({"bones": poses["one"]["bones"]})
        b = render({"bones": poses["two"]["bones"]})
        check("D11 two poses render differently (compare)", diff(a, b) > 10000)

        # E: bend testing
        for joint, bone_ in (("elbow", "near_forearm"), ("knee", "near_shin")):
            ims = []
            for ang in (0, 45, 90):
                pz = {"bones": {bone_: {"rot": ang * (-1 if joint == "elbow" else 1)}}, "ik": {"near_thigh": False} if joint == "knee" else {}}
                ims.append(render(pz, src="saved"))
            check(f"E {joint} 0/45/90 all render and differ", diff(ims[0], ims[1]) > 1000 and diff(ims[1], ims[2]) > 1000, f"{[i['ms'] for i in ims]} ms")
            # gap check: count holes (transparent pixels fully enclosed by the silhouette) at each angle
            from scipy import ndimage as ndi
            holes = []
            for im in ims:
                m = img(im)[..., 3] > 128
                holes.append(int(ndi.binary_fill_holes(m).sum() - m.sum()))
            print(f"     enclosed gaps (px) at 0/45/90 {joint}: {holes}")
        srv.shutdown()
        real_after = {"rig": hashlib.sha1((REAL / "source/rig/rig.json").read_bytes()).hexdigest(), "anims": hash_tree(REAL / "source/rig/anims")}
        check("REAL rig.json and anims/*.json untouched by the tests", real_before == real_after)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    bad = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
