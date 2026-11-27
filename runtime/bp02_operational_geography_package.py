"""Build a deterministic, source-pinned BP02 operational geography package.

This creates a local release artifact only. It does not connect to or write to Neon.
The complete BP02 gameplay acceptance audit is rerun before packaging.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

from runtime.bp02_full_acceptance_audit import run_full_bp02_acceptance_audit

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data/geography/saltwater-geography-v1.json"
IDENTITY = ROOT / "data/geography/saltwater-geography-v1-identity-map.json"
PROPERTY = ROOT / "data/property/saltwater-property-world-v1.json.gz"
OUTPUT = ROOT / "build/bp02-operational-geography-v1.json.gz"
MANIFEST = ROOT / "build/bp02-operational-geography-v1.manifest.json"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def build_release() -> tuple[bytes, dict]:
    geo_raw, identity_raw, property_raw = GEO.read_bytes(), IDENTITY.read_bytes(), PROPERTY.read_bytes()
    geography = json.loads(geo_raw)
    identity = json.loads(identity_raw)
    audit = run_full_bp02_acceptance_audit()
    if audit.get("overall_status") != "PASS" or audit.get("operational_release_status") != "PASS":
        raise ValueError("BP02 full acceptance must pass before operational package creation")
    if not audit.get("authority", {}).get("operational_approval"):
        raise ValueError("BP02 fictional gameplay release authority is not satisfied")
    production_seed_approved = identity.get("operational_seed_approved") is True
    canonical = audit["canonical_geography_register"]
    if canonical.get("operational_release_status") != "RELEASED_FOR_GAMEPLAY":
        raise ValueError("Canonical geography register is not released for gameplay")
    if canonical.get("database_write_performed") or canonical.get("neon_write_performed"):
        raise ValueError("Package builder must remain a no-database-write operation")

    expected = {
        "districts": 8, "neighbourhoods": 24, "roads": 42,
        "network_nodes": 367, "road_segments": 685, "routes": 5,
        "parcels": 420, "addresses": 420, "access_points": 2948,
        "bridge_connectors": 4,
    }
    actual = {
        "districts": len(geography["districts"]),
        "neighbourhoods": len(geography["neighbourhoods"]),
        "roads": len(geography["roads"]),
        "network_nodes": len(geography["network"]["nodes"]),
        "road_segments": len(geography["network"]["segments"]),
        "routes": len(geography["network"]["routes"]),
        "parcels": len(canonical["parcels"]),
        "addresses": len(canonical["addresses"]),
        "access_points": len(canonical["access_points"]),
        "bridge_connectors": len(canonical["bridge_connectors"]),
    }
    if actual != expected:
        raise ValueError(f"Operational geography count mismatch: {actual!r}")
    if identity.get("counts", {}).get("unresolved_source_to_entity_code_mappings") != 0:
        raise ValueError("Source identity map contains unresolved mappings")
    if len(identity.get("entries", [])) != 100:
        raise ValueError("Expected 100 portable geography identity mappings")
    if any(row.get("operational_status") != "ACTIVE_IN_GAME" for row in canonical["access_points"]):
        raise ValueError("Access-point gameplay status is not consistently ACTIVE_IN_GAME")
    if any(row.get("operational_status") != "ACTIVE_IN_GAME" for row in canonical["parcels"] + canonical["addresses"]):
        raise ValueError("Parcel/address gameplay status is not consistently ACTIVE_IN_GAME")
    if any(row.get("operational_status") != "ACTIVE_IN_GAME" for row in canonical["bridge_connectors"]):
        raise ValueError("Bridge connector gameplay status is not consistently ACTIVE_IN_GAME")

    payload = {
        "schema": "saltwater-bp02-operational-geography/1.0",
        "release_id": "SW-BP02-OPERATIONAL-GEOGRAPHY-V1",
        "release_status": "ACCEPTED_FOR_GAMEPLAY_DEPLOYMENT",
        "gameplay_release_accepted": True,
        "production_seed_approved": production_seed_approved,
        "source_dataset": geography["dataset_id"],
        "coordinate_reference": geography["coordinate_reference"],
        "source_hashes": {
            "geography_sha256": sha256(geo_raw),
            "identity_map_sha256": sha256(identity_raw),
            "property_world_sha256": sha256(property_raw),
        },
        "identity_map": identity,
        "geography": geography,
        "canonical_geography": canonical,
        "acceptance": {
            "audit": audit["audit"],
            "audit_version": audit["audit_version"],
            "overall_status": audit["overall_status"],
            "operational_release_status": audit["operational_release_status"],
            "authority": audit["authority"],
            "counts": actual,
        },
        "database_write_performed": False,
        "neon_write_performed": False,
    }
    raw = canonical_json(payload)
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    manifest = {
        "release_id": payload["release_id"],
        "schema": payload["schema"],
        "gameplay_release_accepted": True,
        "production_seed_approved": production_seed_approved,
        "source_hashes": payload["source_hashes"],
        "record_counts": actual,
        "uncompressed_bytes": len(raw),
        "compressed_bytes": len(compressed),
        "package_sha256": sha256(compressed),
        "release_scope": [
            "districts", "neighbourhoods", "geographic_features", "roads",
            "network_nodes", "road_segments", "routes", "parcels", "addresses",
            "building_access_points", "bridge_connectors",
        ],
        "semantic_guards": {
            "candidate_access_statuses_preserved": True,
            "bridge_connectors_are_accepted_gameplay_records": True,
            "database_surrogate_ids_embedded": False,
            "production_database_written": False,
            "production_seed_authority_granted": production_seed_approved,
        },
    }
    return compressed, manifest


def main() -> None:
    compressed, manifest = build_release()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(compressed)
    MANIFEST.write_bytes(canonical_json(manifest) + b"\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
