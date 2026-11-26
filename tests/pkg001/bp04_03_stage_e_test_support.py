"""Shared, process-local fixtures for the BP04-03 Stage E regression suite."""
from functools import lru_cache
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def stage_e_parcel_inputs():
    """Build the source, parcel candidates and dossiers once per test process."""
    source = json.loads(
        (ROOT / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8")
    )
    from runtime.parcel_candidate_generator import build_candidates
    from runtime.parcel_dossier_generator import build_parcel_dossiers

    candidates = build_candidates(source)
    dossiers = build_parcel_dossiers(source, candidates)
    return source, candidates, dossiers


@lru_cache(maxsize=1)
def stage_e_asset_inventory():
    """Build the large detailed asset inventory once for all Stage E tests."""
    from runtime.physical_asset_inventory_generator import build_asset_inventory

    source, candidates, dossiers = stage_e_parcel_inputs()
    return build_asset_inventory(source, candidates, dossiers)
