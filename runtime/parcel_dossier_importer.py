"""Disposable-only importer for detailed BP04-03 parcel dossier records."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import psycopg
from shapely.geometry import Polygon


def validate_manifest(data, candidates):
    if data.get("operational_approval") is not False:
        raise ValueError("Operational dossier manifests are not accepted")
    if data.get("summary", {}).get("canonical_addresses_created") != 0:
        raise ValueError("Dossier manifest must not create canonical addresses")
    if data.get("summary", {}).get("operational_access_points_created") != 0:
        raise ValueError("Dossier manifest must not create operational access points")
    if data.get("candidate_manifest_sha256") != candidates.get("manifest_sha256"):
        raise ValueError("Dossier candidate manifest reference mismatch")
    canonical = dict(data)
    claimed = canonical.pop("manifest_sha256", None)
    expected = hashlib.sha256(json.dumps(
        canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()).hexdigest()
    if claimed != expected:
        raise ValueError("Parcel dossier manifest SHA-256 mismatch")
    dossier_ids = [row["dossier"]["candidate_parcel_id"] for row in data.get("parcels", [])]
    candidate_ids = [row["candidate_parcel_id"] for row in candidates.get("parcels", [])]
    if len(dossier_ids) != len(set(dossier_ids)):
        raise ValueError("Duplicate parcel dossier IDs")
    if set(dossier_ids) != set(candidate_ids):
        raise ValueError("Parcel dossier identities do not match candidate parcel manifest")
    candidate_by_id = {row["candidate_parcel_id"]: row for row in candidates.get("parcels", [])}
    for row in data["parcels"]:
        dossier = row["dossier"]
        candidate = candidate_by_id[dossier["candidate_parcel_id"]]
        polygon = Polygon(candidate["geometry"][0], candidate["geometry"][1:])
        if not polygon.is_valid or polygon.is_empty or polygon.area <= 0:
            raise ValueError("Candidate geometry is invalid while validating dossier measurements")
        if dossier["area_m2"] <= 0 or dossier["perimeter_m"] <= 0:
            raise ValueError("Parcel dossier contains invalid geometry measurements")
        if abs(dossier["area_m2"] - candidate["area_m2"]) > 0.001:
            raise ValueError("Parcel dossier area does not match candidate geometry")
        if abs(dossier["perimeter_m"] - round(polygon.length, 3)) > 0.001:
            raise ValueError("Parcel dossier perimeter does not match candidate geometry")
        compactness = 4.0 * 3.141592653589793 * polygon.area / (polygon.length * polygon.length)
        if abs(dossier["compactness_index"] - round(compactness, 8)) > 0.00000001:
            raise ValueError("Parcel dossier compactness does not match candidate geometry")
        centroid = polygon.centroid
        representative = polygon.representative_point()
        if abs(dossier["centroid_x_m"] - round(centroid.x, 6)) > 0.000001 or abs(dossier["centroid_y_m"] - round(centroid.y, 6)) > 0.000001:
            raise ValueError("Parcel dossier centroid does not match candidate geometry")
        if abs(dossier["label_point_x_m"] - round(representative.x, 6)) > 0.000001 or abs(dossier["label_point_y_m"] - round(representative.y, 6)) > 0.000001:
            raise ValueError("Parcel dossier label point does not match candidate geometry")
        bounds = [round(value, 6) for value in polygon.bounds]
        if dossier["bounds_m"] != bounds:
            raise ValueError("Parcel dossier bounds do not match candidate geometry")
        if dossier["exterior_vertex_count"] != len(polygon.exterior.coords) - 1 or dossier["interior_ring_count"] != len(polygon.interiors):
            raise ValueError("Parcel dossier ring counts do not match candidate geometry")
        if dossier["frontage_candidate_count"] != len(row["frontages"]):
            raise ValueError("Parcel frontage candidate count does not match frontage rows")
        if dossier["frontage_segment_count"] != sum(len(item["road_segment_ids"]) for item in row["frontages"]):
            raise ValueError("Parcel frontage segment count does not match frontage rows")
        if dossier["adjacent_water_feature_ids"] != sorted(item["water_feature_id"] for item in row["water_adjacencies"]):
            raise ValueError("Parcel water adjacency IDs do not match water adjacency rows")
        frontage_ids = {item["frontage_candidate_id"] for item in row["frontages"]}
        if any(item["frontage_candidate_id"] not in frontage_ids for item in row["access_candidates"]):
            raise ValueError("Access location candidate has no matching frontage candidate")
    for row in data.get("adjacency", []):
        if row["left_candidate_parcel_id"] >= row["right_candidate_parcel_id"]:
            raise ValueError("Parcel adjacency pairs must be canonically ordered")
    return expected


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


def import_dossiers(conn, data, manifest_sha, candidates):
    if conn.info.dbname != "saltwater_test":
        raise RuntimeError("Refusing parcel dossier import outside database saltwater_test")
    started = time.perf_counter()
    digest = bytes.fromhex(manifest_sha)
    inserted = {name: 0 for name in ("dossiers", "frontages", "access_candidates", "adjacencies", "water_adjacencies")}
    with conn.transaction():
        with conn.cursor() as cur:
            version = cur.execute("SELECT current_setting('server_version_num')::int").fetchone()[0]
            if not 160000 <= version < 170000:
                raise RuntimeError("Parcel dossier importer requires PostgreSQL 16")
            before = cur.execute("SELECT pg_database_size(current_database())").fetchone()[0]
            spatial_ids = {}
            candidate_manifest_records = {item["candidate_parcel_id"]: item for item in candidates["parcels"]}
            for row in data["parcels"]:
                dossier = row["dossier"]
                candidate_id = dossier["candidate_parcel_id"]
                code = "SWP-CAND-" + candidate_id.removeprefix("BPC-")
                identity = cur.execute(
                    "SELECT spatial_id FROM sw_geo.entity WHERE entity_code=%s AND kind=6", (code,)
                ).fetchone()
                if identity is None:
                    raise ValueError(f"Candidate parcel identity is missing: {candidate_id}")
                parcel_id = identity[0]
                spatial_ids[candidate_id] = parcel_id
                profile = cur.execute(
                    "SELECT 1 FROM sw_geo.parcel_profile WHERE parcel_spatial_id=%s AND version_no=1",
                    (parcel_id,),
                ).fetchone()
                if profile is None:
                    raise ValueError(f"Candidate parcel profile is missing: {candidate_id}")
                geometry_hash = cur.execute(
                    "SELECT geometry_sha256 FROM sw_geo.version WHERE spatial_id=%s AND version_no=1",
                    (parcel_id,),
                ).fetchone()[0]
                candidate_record = candidate_manifest_records[candidate_id]
                candidate_geometry = {"type": "Polygon", "coordinates": candidate_record["geometry"]}
                candidate_bytes = json.dumps(candidate_geometry, sort_keys=True, separators=(",", ":")).encode("utf-8")
                if bytes(geometry_hash) != hashlib.sha256(candidate_bytes).digest():
                    raise ValueError(f"Candidate geometry checksum differs from disposable geography version: {candidate_id}")
                bounds = dossier["bounds_m"]
                cur.execute(
                    """INSERT INTO sw_geo.parcel_dossier
                    (parcel_spatial_id,version_no,geometry_sha256,source_manifest_sha256,
                     perimeter_m,compactness_index,centroid_x_m,centroid_y_m,label_point_x_m,label_point_y_m,
                     bounds_min_x_m,bounds_min_y_m,bounds_max_x_m,bounds_max_y_m,
                     exterior_vertex_count,interior_ring_count,road_frontage_length_m,frontage_segment_count,
                     frontage_candidate_count,water_boundary_contact_length_m,adjacent_water_feature_count,frontage_review_status,
                     geometry_review_status,measurement_basis,source_ref,actor_ref,confidence_code,reason)
                    VALUES (%s,1,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING""",
                    (parcel_id, bytes(geometry_hash), digest, dossier["perimeter_m"], dossier["compactness_index"],
                     dossier["centroid_x_m"], dossier["centroid_y_m"], dossier["label_point_x_m"], dossier["label_point_y_m"],
                     *bounds, dossier["exterior_vertex_count"], dossier["interior_ring_count"],
                     dossier["road_frontage_length_m"], dossier["frontage_segment_count"], dossier["frontage_candidate_count"],
                     dossier["water_boundary_contact_length_m"], len(dossier["adjacent_water_feature_ids"]),
                     dossier["frontage_review_status"], dossier["geometry_review_status"], dossier["measurement_basis"],
                     dossier["source_ref"], dossier["actor_ref"], dossier["confidence_code"], dossier["reason"]),
                )
                inserted["dossiers"] += cur.rowcount
                existing = cur.execute(
                    "SELECT source_manifest_sha256 FROM sw_geo.parcel_dossier WHERE parcel_spatial_id=%s AND version_no=1",
                    (parcel_id,),
                ).fetchone()
                if existing is None or bytes(existing[0]) != digest:
                    raise ValueError(f"Conflicting or missing parcel dossier: {candidate_id}")

                for frontage in row["frontages"]:
                    cur.execute(
                        """INSERT INTO sw_geo.parcel_frontage_candidate
                        (parcel_spatial_id,version_no,frontage_candidate_id,road_segment_ids,road_id,road_name,road_class,
                         contact_length_m,candidate_point_x_m,candidate_point_y_m,review_status,
                         source_manifest_sha256,source_ref,actor_ref,confidence_code,reason)
                        VALUES (%s,1,%s,%s,%s,%s,%s,%s,%s,%s,'UNREVIEWED_GEOMETRIC_CONTACT',%s,%s,
                                'BP04-03-PARCEL-DOSSIER-IMPORTER','estimated',
                                'Derived continuous road-reserve boundary contact; not approved legal frontage.')
                        ON CONFLICT DO NOTHING""",
                        (parcel_id, frontage["frontage_candidate_id"], frontage["road_segment_ids"],
                         frontage["road_id"], frontage["road_name"], frontage["road_class"],
                         frontage["contact_length_m"], frontage["candidate_point_x_m"], frontage["candidate_point_y_m"],
                         digest, frontage["source_ref"]),
                    )
                    inserted["frontages"] += cur.rowcount

                for access in row["access_candidates"]:
                    cur.execute(
                        """INSERT INTO sw_geo.parcel_access_location_candidate
                        (access_candidate_id,parcel_spatial_id,version_no,frontage_candidate_id,candidate_x_m,candidate_y_m,
                         candidate_type,review_status,source_manifest_sha256,source_ref,actor_ref,confidence_code,reason)
                        VALUES (%s,%s,1,%s,%s,%s,%s,%s,%s,%s,'BP04-03-PARCEL-DOSSIER-IMPORTER','estimated',
                                'Unreviewed geometric point on a road-reserve contact; not an entrance or access-point identity.')
                        ON CONFLICT DO NOTHING""",
                        (access["access_candidate_id"], parcel_id, access["frontage_candidate_id"],
                         access["candidate_x_m"], access["candidate_y_m"], access["candidate_type"],
                         access["review_status"], digest, access["source_ref"]),
                    )
                    inserted["access_candidates"] += cur.rowcount

                for water in row["water_adjacencies"]:
                    cur.execute(
                        """INSERT INTO sw_geo.parcel_water_adjacency_candidate
                        (parcel_spatial_id,version_no,water_feature_id,contact_length_m,source_manifest_sha256,
                         source_ref,actor_ref,confidence_code,reason)
                        VALUES (%s,1,%s,%s,%s,%s,'BP04-03-PARCEL-DOSSIER-IMPORTER','estimated',
                                'Derived geometric contact with a mapped fictional water feature.')
                        ON CONFLICT DO NOTHING""",
                        (parcel_id, water["water_feature_id"], water["contact_length_m"], digest, water["source_ref"]),
                    )
                    inserted["water_adjacencies"] += cur.rowcount

            for adjacency in data["adjacency"]:
                left_id = spatial_ids[adjacency["left_candidate_parcel_id"]]
                right_id = spatial_ids[adjacency["right_candidate_parcel_id"]]
                left_hood = cur.execute(
                    "SELECT spatial_id FROM sw_geo.entity WHERE entity_code=%s AND kind=4",
                    (adjacency["left_neighbourhood_id"],),
                ).fetchone()
                right_hood = cur.execute(
                    "SELECT spatial_id FROM sw_geo.entity WHERE entity_code=%s AND kind=4",
                    (adjacency["right_neighbourhood_id"],),
                ).fetchone()
                if left_hood is None or right_hood is None:
                    raise ValueError("Parcel adjacency neighbourhood identity is unresolved")
                if left_id > right_id:
                    left_id, right_id = right_id, left_id
                    left_hood, right_hood = right_hood, left_hood
                cur.execute(
                    """INSERT INTO sw_geo.parcel_adjacency_candidate
                    (left_parcel_spatial_id,left_version_no,right_parcel_spatial_id,right_version_no,
                     left_neighbourhood_spatial_id,right_neighbourhood_spatial_id,relationship_code,
                     shared_boundary_length_m,source_manifest_sha256,source_ref,actor_ref,confidence_code,reason)
                    VALUES (%s,1,%s,1,%s,%s,%s,%s,%s,%s,'BP04-03-PARCEL-DOSSIER-IMPORTER','estimated',
                            'Geometric adjacency candidate; no ownership or legal boundary conclusion.')
                    ON CONFLICT DO NOTHING""",
                    (left_id, right_id, left_hood[0], right_hood[0], adjacency["relationship_code"],
                     adjacency["shared_boundary_length_m"], digest, adjacency["source_ref"]),
                )
                inserted["adjacencies"] += cur.rowcount

            expected = {
                "dossiers": len(data["parcels"]),
                "frontages": sum(len(row["frontages"]) for row in data["parcels"]),
                "access_candidates": sum(len(row["access_candidates"]) for row in data["parcels"]),
                "adjacencies": len(data["adjacency"]),
                "water_adjacencies": sum(len(row["water_adjacencies"]) for row in data["parcels"]),
            }
            tables = {
                "dossiers": "parcel_dossier",
                "frontages": "parcel_frontage_candidate",
                "access_candidates": "parcel_access_location_candidate",
                "adjacencies": "parcel_adjacency_candidate",
                "water_adjacencies": "parcel_water_adjacency_candidate",
            }
            present = {}
            for key, table in tables.items():
                if key == "adjacencies":
                    count = cur.execute(
                        f"SELECT count(*) FROM sw_geo.{table} WHERE source_manifest_sha256=%s", (digest,)
                    ).fetchone()[0]
                else:
                    count = cur.execute(
                        f"SELECT count(*) FROM sw_geo.{table} WHERE source_manifest_sha256=%s", (digest,)
                    ).fetchone()[0]
                present[key] = count
                if count != expected[key]:
                    raise RuntimeError(f"{key} count mismatch: expected {expected[key]}, got {count}")
            addresses = cur.execute(
                "SELECT count(*) FROM sw_geo.address_profile a JOIN sw_geo.entity e ON e.spatial_id=a.address_spatial_id "
                "WHERE e.entity_code LIKE 'SWA-CAND-%'"
            ).fetchone()[0]
            if addresses != 0:
                raise RuntimeError("Parcel dossier import unexpectedly created canonical addresses")
            after = cur.execute("SELECT pg_database_size(current_database())").fetchone()[0]
    return {
        "manifest_sha256": manifest_sha,
        "expected_records": expected,
        "records_present": present,
        "records_inserted_this_run": inserted,
        "canonical_addresses_created": addresses,
        "database_bytes_before": before,
        "database_bytes_after": after,
        "database_growth_bytes": after - before,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="bp04-03-parcel-dossiers.json")
    parser.add_argument("--candidate-manifest", default="bp04-03-stage-b-parcel-candidates.json")
    parser.add_argument("--dsn", default=None)
    args = parser.parse_args()
    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    candidates = json.loads(Path(args.candidate_manifest).read_text(encoding="utf-8"))
    manifest_sha = validate_manifest(data, candidates)
    params = _connection_parameters(args)
    with (psycopg.connect(**params) if isinstance(params, dict) else psycopg.connect(params)) as conn:
        report = import_dossiers(conn, data, manifest_sha, candidates)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
