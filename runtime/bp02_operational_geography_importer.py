"""Import a previously built BP02 operational geography package.

The package builder performs acceptance once; this importer only reads its
compressed output and never reruns the expensive acceptance audit. Production
writes remain separately guarded by --allow-production and the package's
production_seed_approved authority flag.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "build/bp02-operational-geography-v1.json.gz"
MANIFEST = ROOT / "build/bp02-operational-geography-v1.manifest.json"
RELEASE_ID = "SW-BP02-OPERATIONAL-GEOGRAPHY-V1"


def _source_id(row: dict, *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value:
            return str(value)
    raise ValueError(f"Missing stable source identity; expected one of {keys!r}: {row!r}")


def load_package(package_path: Path = PACKAGE, manifest_path: Path = MANIFEST) -> tuple[dict, dict, bytes]:
    compressed = package_path.read_bytes()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    digest = hashlib.sha256(compressed).hexdigest()
    if digest != manifest.get("package_sha256"):
        raise ValueError("Operational geography package checksum does not match its manifest")
    payload = json.loads(gzip.decompress(compressed))
    if payload.get("release_id") != RELEASE_ID:
        raise ValueError("Unexpected BP02 operational geography release ID")
    if payload.get("gameplay_release_accepted") is not True:
        raise ValueError("BP02 gameplay release acceptance is not satisfied")
    if payload.get("production_seed_approved") is not manifest.get("production_seed_approved"):
        raise ValueError("Package and manifest production-seed authority disagree")
    if payload.get("database_write_performed") or payload.get("neon_write_performed"):
        raise ValueError("A package that already performed a database write cannot be imported")
    return payload, manifest, compressed


def validate_package(payload: dict, manifest: dict, compressed: bytes) -> dict:
    geography = payload["geography"]
    canonical = payload["canonical_geography"]
    expected = {
        "districts": 8, "neighbourhoods": 24, "features": 54, "roads": 42,
        "network_nodes": 367, "road_segments": 685, "routes": 5,
        "parcels": 420, "addresses": 420, "access_points": 2948,
        "bridge_connectors": 4,
    }
    actual = {
        "districts": len(geography["districts"]),
        "neighbourhoods": len(geography["neighbourhoods"]),
        "features": len(geography["features"]),
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
        raise ValueError(f"BP02 operational record count mismatch: {actual!r}")
    if manifest.get("record_counts", {}).get("districts") != 8:
        raise ValueError("Manifest does not contain the expected BP02 record counts")
    if any(row.get("operational_status") != "ACTIVE_IN_GAME"
           for layer in ("parcels", "addresses", "access_points", "bridge_connectors")
           for row in canonical[layer]):
        raise ValueError("Canonical gameplay status is not preserved across property geography")
    node_ids = {row["id"] for row in geography["network"]["nodes"]}
    road_ids = {row["id"] for row in geography["roads"]}
    segment_ids = {row["id"] for row in geography["network"]["segments"]}
    for segment in geography["network"]["segments"]:
        if segment["road_id"] not in road_ids:
            raise ValueError(f"Segment {segment['id']} has an unresolved road reference")
        if segment["from_node_id"] not in node_ids or segment["to_node_id"] not in node_ids:
            raise ValueError(f"Segment {segment['id']} has an unresolved node reference")
    for route in geography["network"]["routes"]:
        if any(node_id not in node_ids for node_id in route["node_ids"]):
            raise ValueError(f"Route {route['id']} has an unresolved node reference")
        if any(segment_id not in segment_ids for segment_id in route["segment_ids"]):
            raise ValueError(f"Route {route['id']} has an unresolved segment reference")
    return actual


def _body(sql: str) -> str:
    upper = sql.upper()
    begin, commit = upper.find("BEGIN;"), upper.rfind("COMMIT;")
    if begin < 0 or commit <= begin:
        raise ValueError("BP02 operational migration wrapper is malformed")
    return sql[begin + len("BEGIN;"):commit]


def import_package(conn, payload: dict, manifest: dict, compressed: bytes,
                   expected_database: str, allow_production: bool = False) -> dict:
    actual_database = conn.execute("SELECT current_database()").fetchone()[0]
    if actual_database != expected_database:
        raise ValueError(f"Database mismatch: expected {expected_database!r}, connected to {actual_database!r}")
    if actual_database == "neondb":
        if not allow_production:
            raise PermissionError("Production requires explicit --allow-production")
        if payload.get("production_seed_approved") is not True:
            raise PermissionError("Package identity map does not approve production seeding")
    elif allow_production:
        raise ValueError("--allow-production is valid only for neondb")

    counts = validate_package(payload, manifest, compressed)
    package_sha = hashlib.sha256(compressed).hexdigest()
    existing = conn.execute(
        "SELECT package_sha256 FROM sw_geo.bp02_release WHERE release_id=%s FOR UPDATE",
        (RELEASE_ID,),
    ).fetchone()
    if existing:
        if existing[0].strip() != package_sha:
            raise ValueError("BP02 release ID already exists with a different package checksum")
        return {"status": "already_present", "release_id": RELEASE_ID,
                "package_sha256": package_sha, "record_counts": counts}

    geo, canonical = payload["geography"], payload["canonical_geography"]
    network = geo["network"]
    with conn.transaction():
        conn.execute(
            """INSERT INTO sw_geo.bp02_release
               (release_id,source_dataset,package_sha256,source_hashes,
                gameplay_release_accepted,production_seed_approved,record_counts)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (RELEASE_ID, payload["source_dataset"], package_sha,
             Jsonb(payload["source_hashes"]), True,
             payload["production_seed_approved"], Jsonb(counts)),
        )
        conn.cursor().executemany(
            "INSERT INTO sw_geo.bp02_district(source_id,name,bounds,record) VALUES (%s,%s,%s,%s)",
            [(r["id"], r["name"], Jsonb({k:r[k] for k in ("x0","x1","y0","y1")}), Jsonb(r))
             for r in geo["districts"]],
        )
        conn.cursor().executemany(
            "INSERT INTO sw_geo.bp02_neighbourhood(source_id,district_source_id,name,geometry,record) VALUES (%s,%s,%s,%s,%s)",
            [(r["id"], r["district_id"], r["name"], Jsonb(r["geometry"]), Jsonb(r))
             for r in geo["neighbourhoods"]],
        )
        conn.cursor().executemany(
            "INSERT INTO sw_geo.bp02_feature(source_id,entity_type,name,geometry,properties) VALUES (%s,%s,%s,%s,%s)",
            [(r["id"], r["properties"]["entity_type"], r["properties"]["name"],
              Jsonb(r["geometry"]), Jsonb(r["properties"])) for r in geo["features"]],
        )
        conn.cursor().executemany(
            "INSERT INTO sw_geo.bp02_road(source_id,name,road_class,record) VALUES (%s,%s,%s,%s)",
            [(r["id"], r["name"], r["class"], Jsonb(r)) for r in geo["roads"]],
        )
        conn.cursor().executemany(
            "INSERT INTO sw_geo.bp02_node(source_id,x,y,degree,node_kind,record) VALUES (%s,%s,%s,%s,%s,%s)",
            [(r["id"], r["x"], r["y"], r["degree"], r["kind"], Jsonb(r))
             for r in network["nodes"]],
        )
        conn.cursor().executemany(
            """INSERT INTO sw_geo.bp02_segment
               (source_id,road_source_id,from_node_source_id,to_node_source_id,length_m,
                geometry,road_class,segment_kind,direction,modes,access,surface,water_crossing,record)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            [(r["id"], r["road_id"], r["from_node_id"], r["to_node_id"], r["length_m"],
              Jsonb(r["geometry"]), r["class"], r["kind"], r["direction"], Jsonb(r["modes"]),
              r["access"], r["surface"], r.get("water_crossing", False), Jsonb(r))
             for r in network["segments"]],
        )
        conn.cursor().executemany(
            "INSERT INTO sw_geo.bp02_route(source_id,name,route_type,record) VALUES (%s,%s,%s,%s)",
            [(r["id"], r["name"], r["type"], Jsonb(r)) for r in network["routes"]],
        )
        route_nodes, route_segments = [], []
        for route in network["routes"]:
            route_nodes.extend((route["id"], i, node_id)
                               for i, node_id in enumerate(route["node_ids"], start=1))
            route_segments.extend((route["id"], i, segment_id)
                                  for i, segment_id in enumerate(route["segment_ids"], start=1))
        conn.cursor().executemany(
            "INSERT INTO sw_geo.bp02_route_node(route_source_id,sequence_no,node_source_id) VALUES (%s,%s,%s)",
            route_nodes,
        )
        conn.cursor().executemany(
            "INSERT INTO sw_geo.bp02_route_segment(route_source_id,sequence_no,segment_source_id) VALUES (%s,%s,%s)",
            route_segments,
        )
        conn.cursor().executemany(
            "INSERT INTO sw_geo.bp02_parcel(source_id,operational_status,record) VALUES (%s,%s,%s)",
            [(_source_id(r,"parcel_id"), r["operational_status"], Jsonb(r))
             for r in canonical["parcels"]],
        )
        conn.cursor().executemany(
            "INSERT INTO sw_geo.bp02_address(source_id,parcel_source_id,operational_status,record) VALUES (%s,%s,%s,%s)",
            [(_source_id(r,"address_id"), r["parcel_id"], r["operational_status"], Jsonb(r))
             for r in canonical["addresses"]],
        )
        conn.cursor().executemany(
            "INSERT INTO sw_geo.bp02_access_point(source_id,operational_status,record) VALUES (%s,%s,%s)",
            [(_source_id(r,"candidate_access_point_id","access_point_id","id"),
              r["operational_status"], Jsonb(r)) for r in canonical["access_points"]],
        )
        conn.cursor().executemany(
            "INSERT INTO sw_geo.bp02_bridge_connector(source_id,operational_status,engineering_assessment_id,record) VALUES (%s,%s,%s,%s)",
            [(_source_id(r,"candidate_connector_id","connector_id","source_connector_candidate_id"),
              r["operational_status"], r["engineering_assessment_id"], Jsonb(r))
             for r in canonical["bridge_connectors"]],
        )
    return {"status": "inserted", "release_id": RELEASE_ID,
            "package_sha256": package_sha, "record_counts": counts}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-database")
    parser.add_argument("--allow-production", action="store_true")
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    args = parser.parse_args()
    payload, manifest, compressed = load_package()
    counts = validate_package(payload, manifest, compressed)
    result = {"release_id": RELEASE_ID, "package_sha256": hashlib.sha256(compressed).hexdigest(),
              "record_counts": counts, "production_seed_approved": payload["production_seed_approved"]}
    if args.apply:
        if not args.database_url or not args.expected_database:
            parser.error("--apply requires DATABASE_URL and --expected-database")
        with psycopg.connect(args.database_url, autocommit=True) as conn:
            result["import"] = import_package(conn, payload, manifest, compressed,
                                              args.expected_database, args.allow_production)
    else:
        result["status"] = "dry_run_no_database_write"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
