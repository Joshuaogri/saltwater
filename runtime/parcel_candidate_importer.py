"""Disposable-only BP04-03 Stage B parcel candidate PostgreSQL importer.

Consumes the deterministic generator artifact. It creates candidate spatial
identities and geometry/profile versions only in an explicitly disposable
PostgreSQL 16 database named saltwater_test. It never assigns addresses.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb


def _connection_parameters(args):
    if args.dsn:
        return args.dsn
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "dbname": os.getenv("PGDATABASE", "saltwater_test"),
        "user": os.getenv("PGUSER", "saltwater_test"),
        "password": os.getenv("PGPASSWORD", "test-only"),
    }


def validate_manifest(data):
    if data.get("operational_approval") is not False:
        raise ValueError("Operationally approved manifests are not accepted by this disposable importer")
    generation = data.get("generation", {})
    if generation.get("spatial_ids_assigned") != 0 or generation.get("canonical_addresses_created") != 0:
        raise ValueError("Input manifest must not contain allocated IDs or addresses")
    canonical = dict(data)
    claimed = canonical.pop("manifest_sha256", None)
    expected = hashlib.sha256(json.dumps(
        canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()).hexdigest()
    if claimed != expected:
        raise ValueError("Candidate manifest SHA-256 mismatch")
    parcels = data.get("parcels", [])
    ids = [p["candidate_parcel_id"] for p in parcels]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate candidate parcel IDs")
    if len(parcels) != generation.get("parcel_candidate_count"):
        raise ValueError("Candidate count does not match manifest")
    for parcel in parcels:
        ring = parcel["geometry"][0]
        if len(ring) < 4 or ring[0] != ring[-1]:
            raise ValueError(f"Invalid closed polygon ring: {parcel['candidate_parcel_id']}")
        if parcel["candidate_spatial_id"] is not None or parcel["canonical_address_id"] is not None:
            raise ValueError("Candidate artifact unexpectedly contains operational identifiers")
    return expected


def import_candidates(conn, data, manifest_sha):
    if conn.info.dbname != "saltwater_test":
        raise RuntimeError("Refusing BP04-03 candidate import outside database saltwater_test")
    started = time.perf_counter()
    inserted_entities = inserted_versions = inserted_profiles = 0
    source_ref = f"BP04-03:{data['candidate_set_id']}:{manifest_sha}"
    actor_ref = "BP04-03-DISPOSABLE-IMPORTER"
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("SELECT current_setting('server_version_num')::int")
            version = cur.fetchone()[0]
            if not 160000 <= version < 170000:
                raise RuntimeError("BP04-03 importer requires PostgreSQL 16")
            cur.execute("SELECT pg_database_size(current_database())")
            before_bytes = cur.fetchone()[0]

            for parcel in data["parcels"]:
                code = "SWP-CAND-" + parcel["candidate_parcel_id"].removeprefix("BPC-")
                display_name = "Candidate Parcel " + parcel["candidate_parcel_id"]
                cur.execute(
                    "INSERT INTO sw_geo.entity(entity_code,kind) VALUES(%s,6) "
                    "ON CONFLICT(entity_code) DO NOTHING",
                    (code,),
                )
                inserted_entities += cur.rowcount
                cur.execute(
                    "SELECT spatial_id,kind FROM sw_geo.entity WHERE entity_code=%s",
                    (code,),
                )
                row = cur.fetchone()
                if row is None or row[1] != 6:
                    raise ValueError(f"Candidate identity kind mismatch: {code}")
                spatial_id = row[0]
                neighbourhood_code = parcel["source_neighbourhood_id"]
                cur.execute(
                    "SELECT spatial_id FROM sw_geo.entity WHERE entity_code=%s AND kind=4",
                    (neighbourhood_code,),
                )
                hood = cur.fetchone()
                if hood is None:
                    raise ValueError(f"Unresolved neighbourhood identity: {neighbourhood_code}")
                neighbourhood_id = hood[0]
                geometry = {
                    "type": "Polygon",
                    "coordinates": parcel["geometry"],
                }
                geometry_bytes = json.dumps(
                    geometry, sort_keys=True, separators=(",", ":")
                ).encode("utf-8")
                geometry_hash = hashlib.sha256(geometry_bytes).digest()
                cur.execute(
                    "SELECT geometry_payload,geometry_sha256 FROM sw_geo.version "
                    "WHERE spatial_id=%s AND version_no=1",
                    (spatial_id,),
                )
                existing = cur.fetchone()
                if existing is None:
                    cur.execute(
                        "INSERT INTO sw_geo.version "
                        "(spatial_id,version_no,effective_from_tick,parent_id,name,active,"
                        "geometry_format,geometry_payload,geometry_sha256,source_ref,reason_code) "
                        "VALUES(%s,1,0,%s,%s,true,1,%s,%s,%s,1)",
                        (spatial_id, neighbourhood_id, display_name,
                         geometry_bytes, geometry_hash, source_ref),
                    )
                    inserted_versions += 1
                elif bytes(existing[0]) != geometry_bytes or bytes(existing[1]) != geometry_hash:
                    raise ValueError(f"Existing candidate version conflicts with manifest: {code}")
                cur.execute(
                    "SELECT 1 FROM sw_geo.parcel_profile WHERE parcel_spatial_id=%s AND version_no=1",
                    (spatial_id,),
                )
                if cur.fetchone() is None:
                    cur.execute(
                        "INSERT INTO sw_geo.parcel_profile "
                        "(parcel_spatial_id,version_no,neighbourhood_spatial_id,land_use_code,"
                        "development_state,area_m2,area_basis,geometry_quality,source_ref,"
                        "actor_ref,confidence_code,reason) "
                        "VALUES(%s,1,%s,%s,%s,%s,%s,'candidate_unreviewed',%s,%s,%s,%s)",
                        (spatial_id, neighbourhood_id, parcel["land_use_code"],
                         parcel["development_state"], parcel["area_m2"], parcel["area_basis"],
                         source_ref, actor_ref, parcel["confidence_code"], parcel["reason"]),
                    )
                    inserted_profiles += 1

            cur.execute(
                "SELECT count(*) FROM sw_geo.parcel_profile p "
                "JOIN sw_geo.entity e ON e.spatial_id=p.parcel_spatial_id "
                "WHERE e.entity_code LIKE 'SWP-CAND-%'"
            )
            candidate_profile_count = cur.fetchone()[0]
            expected = len(data["parcels"])
            if candidate_profile_count != expected:
                raise RuntimeError(
                    f"Candidate profile count mismatch: expected {expected}, got {candidate_profile_count}"
                )
            cur.execute(
                "SELECT count(*) FROM sw_geo.address_profile a "
                "JOIN sw_geo.entity e ON e.spatial_id=a.address_spatial_id "
                "WHERE e.entity_code LIKE 'SWA-CAND-%'"
            )
            address_count = cur.fetchone()[0]
            if address_count != 0:
                raise RuntimeError("This stage must not create canonical address identities")
            cur.execute("SELECT pg_database_size(current_database())")
            after_bytes = cur.fetchone()[0]
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    return {
        "manifest_sha256": manifest_sha,
        "candidate_count_expected": len(data["parcels"]),
        "candidate_profiles_present": candidate_profile_count,
        "candidate_entities_inserted_this_run": inserted_entities,
        "geometry_versions_inserted_this_run": inserted_versions,
        "parcel_profiles_inserted_this_run": inserted_profiles,
        "canonical_addresses_created": address_count,
        "database_bytes_before": before_bytes,
        "database_bytes_after": after_bytes,
        "database_growth_bytes": after_bytes - before_bytes,
        "elapsed_ms": elapsed_ms,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="bp04-03-stage-b-parcel-candidates.json")
    parser.add_argument("--dsn", default=None)
    args = parser.parse_args()
    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    manifest_sha = validate_manifest(data)
    with psycopg.connect(**_connection_parameters(args)) if isinstance(_connection_parameters(args), dict) else psycopg.connect(_connection_parameters(args)) as conn:
        report = import_candidates(conn, data, manifest_sha)
        with conn.cursor() as cur:
            cur.execute("ANALYZE sw_geo.parcel_profile")
            cur.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
                        "SELECT parcel_spatial_id FROM sw_geo.parcel_profile "
                        "WHERE neighbourhood_spatial_id=(SELECT spatial_id FROM sw_geo.entity "
                        "WHERE entity_code='SW-D01-N1') ORDER BY parcel_spatial_id")
            report["neighbourhood_lookup_plan"] = cur.fetchone()[0]
            cur.execute("SELECT pg_total_relation_size('sw_geo.parcel_profile'::regclass)")
            report["parcel_profile_relation_bytes"] = cur.fetchone()[0]
            cur.execute("SELECT pg_total_relation_size('sw_geo.version'::regclass)")
            report["geography_version_relation_bytes"] = cur.fetchone()[0]
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
