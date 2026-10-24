"""The asset folder layout (fal-image format.md section 4), shared by every tool that reads or writes an asset.

  out/<class>/<id>/
    brief.md  history.md  meta.json
    source/                       group 1: the APPROVED originals (+ pending ones while a session is open)
      design/                     stills (gen_image.py --out <asset>/source/design): master_vNN.png, pose_*_vNN.png, icon_vNN.png
      video/                      clips (sprite_set saves every paid take here at once; source_prune.py drops the rest)
      fx/                         Python fx code (levelup_variants.py ...)
      vfx/<name>/                 fal-image vfx stills that belong to this character
    frames/                       group 2: cut from group 1, what the game uses
      <sheet>/                    e.g. frames/walk_side/: frames/@2x|@1x, sheet.png, preview.gif, check/
      icon/                       the packed icon
      fx/<name>/                  fx layers (back/front frames, fx.json) that go with a sheet
      skills/<pose>/              Fx Studio skill sets (layers, combo, skill.json, skill.lua)
      export_recipe.json          the frame tuner's recipes; export_manifest.json, README.md when exported for another repo
    .work/                        tools only, not in git
The category of a sheet (move, attack, ...) is metadata (meta.json), not a folder.
"""
import pathlib

CATEGORIES = {"walk": "move", "run": "move", "fly": "move", "idle": "idle", "attack": "attack", "attack2": "attack",
              "cast": "attack", "shoot": "attack", "skill": "skill", "respawn": "spawn", "raise": "spawn",
              "levelup": "level", "thorn": "react", "hurt": "hurt", "death": "death", "icon": "ui",
              "projectile": "projectile"}   # sheet names of the asset manifest (fal-image/format.md §8)


def category(sheet: str) -> str:
    return CATEGORIES.get(sheet.split("_")[0], "other")


SOURCE_DESIGN, SOURCE_VIDEO, SOURCE_FX, SOURCE_VFX = "source/design", "source/video", "source/fx", "source/vfx"
FRAMES, FRAMES_FX, FRAMES_SKILLS, RECIPE = "frames", "frames/fx", "frames/skills", "frames/export_recipe.json"


def sheet_rel(sheet: str) -> str:
    """Path of a sheet folder relative to its asset: frames/walk_side (the icon: frames/icon)."""
    return f"{FRAMES}/{sheet}"


def sheet_dir(asset: pathlib.Path, sheet: str) -> pathlib.Path:
    return pathlib.Path(asset) / sheet_rel(sheet)
