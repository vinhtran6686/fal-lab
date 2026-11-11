#!/usr/bin/env python3
"""Copy the sprite sheets the review page plays (Puppet Review artifact) from out/ into this folder, so index.html works locally.
   python docs/puppet-review/build.py      then open docs/puppet-review/index.html
The figure images (*.jpg) are committed here; the sheets are not (they already live under out/ and would double the repo size)."""
import pathlib, shutil
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
H = ROOT / "out" / "heroes"
SHEETS = {
    "idle.png": "holy_commander/frames/idle_side/sheet.png",
    "lv_p.png": "holy_commander/frames/levelup_puppet_side/sheet.png",
    "lv_v.png": "holy_commander/frames/levelup_side/sheet.png",
    "at_p.png": "holy_commander/frames/attack_diag_puppet_side/sheet.png",
    "at_v.png": "holy_commander/frames/attack_diag_side/sheet.png",
    "fx_p.png": "holy_commander/frames/fx/slash_diag_puppet/sheet.png",
    "fx_v.png": "holy_commander/frames/fx/slash_diag/sheet.png",
    "fo_idle.png": "frost_oracle/frames/idle_side/sheet.png",
    "fo_shoot.png": "frost_oracle/frames/shoot_side/sheet.png",
    "fo_lv.png": "frost_oracle/frames/levelup_side/sheet.png",
    "lb_fx_claw.png": "lion_brawler/frames/fx/claw_swipe/sheet.png",
    "lb_fx_slam.png": "lion_brawler/frames/fx/slam/sheet.png",
}
for n in ["idle", "levelup", "attack", "skill_slam", "v2_test", "hurt", "death", "skill_roar", "run", "turn_left", "reel_test", "death_back"]:
    SHEETS[f"lb_{n}.png"] = f"lion_brawler/frames/{n}_side/sheet.png"
for dst, src in SHEETS.items():
    shutil.copyfile(H / src, HERE / dst)
print(f"copied {len(SHEETS)} sheets into {HERE}")
