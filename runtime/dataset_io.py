"""Transparent JSON dataset reader supporting compact gzip snapshots."""
from __future__ import annotations
import gzip
import json
from pathlib import Path

def load_json(path: str | Path):
    path = Path(path)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    compressed = Path(str(path) + ".gz")
    if compressed.exists():
        with gzip.open(compressed, "rt", encoding="utf-8") as stream:
            return json.load(stream)
    raise FileNotFoundError(path)
