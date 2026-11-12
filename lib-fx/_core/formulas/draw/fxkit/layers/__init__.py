"""fxkit / layers: every layer kind, one file per family. Importing this package registers them in fxkit.KINDS."""
import importlib, pathlib

for _f in sorted(pathlib.Path(__file__).parent.glob("*.py")):
    if not _f.name.startswith("_"): importlib.import_module(f"{__name__}.{_f.stem}")
