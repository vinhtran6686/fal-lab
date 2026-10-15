"""Where a sheet lives inside an asset folder (shared by video_to_sheet, sprite_pack, build_playtest).

  out/enemies/<id>/<category>/<sheet>/      e.g. out/enemies/bandit/move/walk_side/
The category comes from the sheet's state (the part before the first "_"): walk_side -> move,
attack_side -> attack, death_side -> death, icon -> ui.
"""
import pathlib

CATEGORIES = {"walk": "move", "run": "move", "idle": "idle", "attack": "attack", "cast": "attack",
              "hurt": "hurt", "death": "death", "icon": "ui", "projectile": "projectile"}


def category(sheet: str) -> str:
    return CATEGORIES.get(sheet.split("_")[0], "other")


def sheet_rel(sheet: str) -> str:
    """Path of a sheet folder relative to its asset: move/walk_side."""
    return f"{category(sheet)}/{sheet}"


def sheet_dir(asset: pathlib.Path, sheet: str) -> pathlib.Path:
    return pathlib.Path(asset) / category(sheet) / sheet
