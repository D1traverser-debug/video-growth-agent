from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
DATA_ROOT = PACKAGE_ROOT / "data"


def data_path(name: str) -> Path:
    path = DATA_ROOT / name
    if not path.is_file():
        raise FileNotFoundError(f"Missing packaged runtime resource: {name}")
    return path
