"""Load the phase-1 Saltwater property/business stack into disposable PostgreSQL.

Production use is deliberately blocked. The command accepts only the disposable
saltwater_test database unless an explicit future implementation changes this
guard through reviewed code. It imports compressed columnar JSON losslessly.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import psycopg
from psycopg.types.json import Jsonb

DATASETS = {
    "SW-PROPERTY-WORLD-V1": "data/property/saltwater-property-world-v1.json.gz",
    "SW-BUSINESS-REGISTRY-V1": "data/business/saltwater-business-registry-v1.json.gz",
    "SW-PROPERTY-TENURE-V1": "data/property/saltwater-property-tenure-v1.json.gz",
}

def read_document(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    payload = gzip.decompress(raw) if path.suffix == ".gz" else raw
    doc = json.loads(payload)
    if doc.get("storage_format") != "textual_json_columnar_v1":
        raise ValueError(f"Unsupported dataset storage format: {path}")
    if not isinstance(doc.get("metadata"), dict) or not isinstance(doc.get("tables"), dict):
        raise ValueError(f"Malformed columnar dataset: {path}")
    return doc, raw

def rows(doc: dict, name: str) -> list[dict]:
    table = doc["tables"].get(name)
    if table is None:
        return []
    columns, values = table.get("columns"), table.get("rows")
    if not isinstance(columns, list) or not isinstance(values, list):
        raise ValueError(f"Malformed columnar collection: {name}")
    result = []
    for index, values_row in enumerate(values):
        if len(values_row) != len(columns):
            raise ValueError(f"{name}[{index}] has {len(values_row)} values for {len(columns)} columns")
        result.append(dict(zip(columns, values_row)))
    return result

def pick(row: dict, *keys: str, default=None):
    for key in keys:
        value = row.get(key)
        if value is not None:
            return value
    return default

def text_value(value):
    if value is None:
        return None
    return str(value)

def numeric_value(value):
    if value is None or isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def record(table: str, source_dataset: str, row: dict, values: dict) -> tuple:
    values["source_dataset"] = source_dataset
    values["source_record"] = Jsonb(row)
    return table, values

def build_batches(documents: dict[str, dict]) -> tuple[dict[str, list[dict]], dict[str, int]]:
    batches: dict[str, list[dict]] = {}
    counts: dict[str, int] = {}

    def add(table: str, dataset: str, source_rows: list[dict], mapper):
        counts[f"{dataset}.{table}"] = len(source_rows)
        batches.setdefault(table, []).extend(mapper(dataset, row) for row in source_rows)

    world = documents["SW-PROPERTY-WORLD-V1"]
    registry = documents["SW-BUSINESS-REGISTRY-V1"]
    tenure = documents["SW-PROPERTY-TENURE-V1"]

    add("organisation", "SW-PROPERTY-WORLD-V1", rows(world, "owner_organisations"),
        lambda ds, r: {"organisation_id":r["organisation_id"],"display_name":r["display_name"],"organisation_type":r["organisation_type"],"registered_city":r.get("registered_city"),"status":r.get("status"),"source_dataset":ds,"source_record":r})
    add("organisation", "SW-PROPERTY-TENURE-V1", rows(tenure, "organisations"),
        lambda ds, r: {"organisation_id":r["organisation_id"],"display_name":r["display_name"],"organisation_type":r["organisation_type"],"registered_city":r.get("registered_city"),"status":r.get("status"),"source_dataset":ds,"source_record":r})

    add("property_site", "SW-PROPERTY-WORLD-V1", rows(world, "properties"),
        lambda ds,r: {"property_id":r["property_id"],"display_name":pick(r,"display_name","property_name","name",default=r["property_id"]),"district_id":pick(r,"district_id","source_district_id"),"neighbourhood_id":pick(r,"neighbourhood_id","source_neighbourhood_id"),"address_id":r.get("address_id"),"site_area_m2":numeric_value(pick(r,"site_area_m2","area_m2","area")),"use_class":pick(r,"primary_use","use_class","property_use"),"lifecycle_status":pick(r,"canonical_status","lifecycle_status","site_state"),"source_dataset":ds,"source_record":r})
    add("street_address", "SW-PROPERTY-WORLD-V1", rows(world, "addresses"),
        lambda ds,r: {"address_id":r["address_id"],"property_id":r["property_id"],"display_name":pick(r,"address_label","display_name"),"road_id":r.get("road_id"),"house_number":text_value(pick(r,"street_number","house_number")),"postcode":r.get("postcode"),"source_dataset":ds,"source_record":r})
    add("building", "SW-PROPERTY-WORLD-V1", rows(world, "buildings"),
        lambda ds,r: {"building_id":r["building_id"],"property_id":r["property_id"],"display_name":pick(r,"display_name","building_name","name",default=r["building_id"]),"building_use":pick(r,"building_use","primary_use","use_class"),"storeys":pick(r,"storeys_above","storeys","floors_above"),"gross_floor_area_m2":numeric_value(pick(r,"gross_floor_area_m2","floor_area_m2","gross_internal_area_m2")),"construction_year":r.get("construction_year"),"lifecycle_status":pick(r,"canonical_status","lifecycle_status"),"source_dataset":ds,"source_record":r})
    add("premises", "SW-PROPERTY-WORLD-V1", rows(world, "premises"),
        lambda ds,r: {"premises_id":r["premises_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"display_name":pick(r,"display_name","premises_name","name",default=r["premises_id"]),"premises_use":pick(r,"premises_use","premises_type","use_class","primary_use"),"floor_name":pick(r,"floor_name","floor_code"),"lifecycle_status":pick(r,"canonical_status","lifecycle_status"),"source_dataset":ds,"source_record":r})
    add("unit_space", "SW-PROPERTY-WORLD-V1", rows(world, "units"),
        lambda ds,r: {"unit_id":r["unit_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"premises_id":r["premises_id"],"display_name":pick(r,"display_name","unit_name","unit_locator","name",default=r["unit_id"]),"unit_class":r.get("unit_class"),"use_class":pick(r,"use_class","primary_use","unit_use"),"floor_order":r.get("floor_order"),"floor_area_m2":numeric_value(r.get("floor_area_m2")),"lifecycle_status":pick(r,"canonical_status","lifecycle_status"),"source_dataset":ds,"source_record":r})
    add("access_point", "SW-PROPERTY-WORLD-V1", rows(world, "access_points"),
        lambda ds,r: {"access_point_id":r["access_point_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"premises_id":r.get("premises_id"),"unit_id":r.get("unit_id"),"display_name":pick(r,"display_name","access_point_name",default=r["access_point_id"]),"access_type":r.get("access_type"),"access_modes":r.get("access_modes"),"road_link_road_id":r.get("road_link_road_id"),"source_dataset":ds,"source_record":r})
    add("access_route", "SW-PROPERTY-WORLD-V1", rows(world, "access_routes"),
        lambda ds,r: {"route_id":r["route_id"],"access_point_id":r["access_point_id"],"road_id":r.get("road_id"),"route_type":r.get("route_type"),"access_modes":[m for m,ok in (("vehicle",r.get("vehicle_access")),("pedestrian",r.get("pedestrian_access"))) if ok],"route_status":r.get("route_state"),"source_dataset":ds,"source_record":r})
    add("site_feature", "SW-PROPERTY-WORLD-V1", rows(world, "site_features"),
        lambda ds,r: {"site_feature_id":r["site_feature_id"],"property_id":r["property_id"],"feature_type":r.get("feature_type"),"display_name":pick(r,"display_name","design_type","subtype",default=r["site_feature_id"]),"source_dataset":ds,"source_record":r})
    add("building_component", "SW-PROPERTY-WORLD-V1", rows(world, "building_components"),
        lambda ds,r: {"component_id":r["component_id"],"building_id":r["building_id"],"component_type":r.get("component_type"),"display_name":pick(r,"display_name","material",default=r["component_id"]),"source_dataset":ds,"source_record":r})
    add("premises_room", "SW-PROPERTY-WORLD-V1", rows(world, "premises_rooms"),
        lambda ds,r: {"room_id":r["room_id"],"premises_id":r["premises_id"],"display_name":pick(r,"room_name","display_name","room_code",default=r["room_id"]),"room_type":r.get("room_type"),"floor_name":pick(r,"floor_name","floor_level"),"source_dataset":ds,"source_record":r})
    add("ownership_interest", "SW-PROPERTY-WORLD-V1", rows(world, "ownership_interests"),
        lambda ds,r: {"ownership_interest_id":r["ownership_interest_id"],"property_id":r["property_id"],"owner_organisation_id":r["owner_organisation_id"],"management_model":r.get("management_model"),"interest_type":r.get("interest_type"),"source_dataset":ds,"source_record":r})

    add("business", "SW-BUSINESS-REGISTRY-V1", rows(registry, "businesses"),
        lambda ds,r: {"business_id":r["business_id"],"display_name":pick(r,"registered_name","trading_name","display_name","business_name","name",default=r["business_id"]),"sector":pick(r,"sector","business_sector",default="unclassified"),"primary_activity":pick(r,"primary_activity","activity"),"status":r.get("status","active"),"parent_business_id":r.get("parent_business_id"),"primary_establishment_id":r.get("primary_establishment_id"),"source_dataset":ds,"source_record":r})
    add("establishment", "SW-BUSINESS-REGISTRY-V1", rows(registry, "establishments"),
        lambda ds,r: {"establishment_id":r["establishment_id"],"business_id":r["business_id"],"property_id":r.get("property_id"),"building_id":r.get("building_id"),"premises_id":r.get("premises_id"),"unit_id":r.get("unit_id"),"display_name":pick(r,"establishment_name","display_name","name",default=r["establishment_id"]),"establishment_type":r.get("establishment_type"),"status":pick(r,"operating_status","status"),"source_dataset":ds,"source_record":r})
    add("business_unit_link", "SW-BUSINESS-REGISTRY-V1", rows(registry, "business_unit_links"),
        lambda ds,r: {"business_unit_link_id":r["business_unit_link_id"],"business_id":r["business_id"],"establishment_id":r["establishment_id"],"unit_id":r["unit_id"],"premises_id":r["premises_id"],"valid_from_tick":r.get("valid_from_tick",0),"valid_to_tick":r.get("valid_to_tick"),"occupancy_relationship":r.get("occupancy_relationship"),"occupancy_status":r.get("occupancy_status"),"source_dataset":ds,"source_record":r})

    add("occupancy_agreement", "SW-PROPERTY-TENURE-V1", rows(tenure, "agreements"),
        lambda ds,r: {"agreement_id":r["agreement_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"premises_id":r.get("premises_id"),"unit_id":r["unit_id"],"landlord_organisation_id":r.get("landlord_organisation_id"),"tenant_business_id":r.get("tenant_business_id"),"operator_business_id":r.get("operator_business_id"),"establishment_id":r.get("establishment_id"),"agreement_type":r["agreement_type"],"commencement_year":r.get("commencement_year"),"expiry_year":r.get("expiry_year"),"agreement_status":r["agreement_status"],"source_dataset":ds,"source_record":r})
    add("occupancy", "SW-PROPERTY-TENURE-V1", rows(tenure, "occupancies"),
        lambda ds,r: {"occupancy_id":r["occupancy_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"premises_id":r.get("premises_id"),"unit_id":r["unit_id"],"occupant_business_id":r.get("occupant_business_id"),"establishment_id":r.get("establishment_id"),"agreement_id":r.get("agreement_id"),"occupant_type":r["occupant_type"],"occupancy_status":r["occupancy_status"],"effective_from_year":r.get("effective_from_year"),"effective_to_year":r.get("effective_to_year"),"source_dataset":ds,"source_record":r})
    return batches, counts

def import_package(root: Path, dsn: str, expected_database: str = "saltwater_test") -> dict:
    with psycopg.connect(dsn) as conn:
        dbname = conn.execute("select current_database()").fetchone()[0]
        if dbname != expected_database:
            raise RuntimeError(f"Refusing non-disposable database {dbname!r}; expected {expected_database!r}")
        documents, manifest_files = {}, {}
        for dataset_id, relative in DATASETS.items():
            path = root / relative
            doc, raw = read_document(path)
            if doc["metadata"].get("dataset_id") != dataset_id:
                raise ValueError(f"Dataset ID mismatch in {relative}")
            documents[dataset_id] = doc
            manifest_files[dataset_id] = {
                "source_path": relative, "source_sha256": hashlib.sha256(raw).hexdigest(),
                "compressed_bytes": len(raw), "uncompressed_bytes": len(gzip.decompress(raw)),
            }
        batches, source_counts = build_batches(documents)
        package_sha = hashlib.sha256(json.dumps(manifest_files,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        commit = os.environ.get("GITHUB_SHA", "local-unpinned")
        release_id = "SWREL-" + hashlib.sha256((commit + package_sha).encode()).hexdigest()[:20].upper()
        manifest = {"release_id":release_id,"source_commit":commit,"package_sha256":package_sha,"files":manifest_files,"source_collection_counts":source_counts}
        with conn.transaction():
            conn.execute("SET CONSTRAINTS ALL DEFERRED")
            conn.execute("""INSERT INTO sw_property.import_release AS current(release_id,source_commit,package_sha256,manifest)
                VALUES (%s,%s,%s,%s) ON CONFLICT(release_id) DO UPDATE SET
                source_commit=excluded.source_commit, package_sha256=excluded.package_sha256, manifest=excluded.manifest
                WHERE current.source_commit IS DISTINCT FROM excluded.source_commit
                   OR current.package_sha256 IS DISTINCT FROM excluded.package_sha256
                   OR current.manifest IS DISTINCT FROM excluded.manifest""",
                (release_id,commit,package_sha,Jsonb(manifest)))
            for dataset_id, info in manifest_files.items():
                collection_count = sum(v for k,v in source_counts.items() if k.startswith(dataset_id+"."))
                conn.execute("""INSERT INTO sw_property.import_dataset AS current
                    (release_id,dataset_id,source_path,source_sha256,compressed_bytes,uncompressed_bytes,source_record_count,loaded_record_count)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT(release_id,dataset_id) DO UPDATE SET source_path=excluded.source_path,
                    source_sha256=excluded.source_sha256,compressed_bytes=excluded.compressed_bytes,
                    uncompressed_bytes=excluded.uncompressed_bytes,source_record_count=excluded.source_record_count,
                    loaded_record_count=excluded.loaded_record_count
                    WHERE current.source_sha256 IS DISTINCT FROM excluded.source_sha256
                       OR current.source_path IS DISTINCT FROM excluded.source_path
                       OR current.compressed_bytes IS DISTINCT FROM excluded.compressed_bytes
                       OR current.uncompressed_bytes IS DISTINCT FROM excluded.uncompressed_bytes
                       OR current.source_record_count IS DISTINCT FROM excluded.source_record_count
                       OR current.loaded_record_count IS DISTINCT FROM excluded.loaded_record_count""",
                    (release_id,dataset_id,info["source_path"],info["source_sha256"],info["compressed_bytes"],info["uncompressed_bytes"],collection_count,collection_count))
            table_order = ["organisation","property_site","street_address","building","premises","unit_space","access_point","access_route","site_feature","building_component","premises_room","ownership_interest","business","establishment","business_unit_link","occupancy_agreement","occupancy"]
            for table in table_order:
                entries = batches.get(table, [])
                if not entries:
                    continue
                columns = list(entries[0].keys())
                if any(list(entry.keys()) != columns for entry in entries):
                    raise ValueError(f"Inconsistent mapped columns for {table}")
                placeholders = ",".join(["%s"] * len(columns))
                col_sql = ",".join(f'"{c}"' for c in columns)
                updates = ",".join(f'"{c}"=excluded."{c}"' for c in columns if c not in {"organisation_id","property_id","address_id","building_id","premises_id","unit_id","access_point_id","route_id","site_feature_id","component_id","room_id","ownership_interest_id","business_id","establishment_id","business_unit_link_id","agreement_id","occupancy_id"})
                pk = {
                    "organisation":"organisation_id","property_site":"property_id","street_address":"address_id","building":"building_id","premises":"premises_id","unit_space":"unit_id","access_point":"access_point_id","access_route":"route_id","site_feature":"site_feature_id","building_component":"component_id","premises_room":"room_id","ownership_interest":"ownership_interest_id","business":"business_id","establishment":"establishment_id","business_unit_link":"business_unit_link_id","occupancy_agreement":"agreement_id","occupancy":"occupancy_id"
                }[table]
                action = f"DO UPDATE SET {updates} WHERE current.source_record IS DISTINCT FROM excluded.source_record OR current.source_dataset IS DISTINCT FROM excluded.source_dataset" if updates else "DO NOTHING"
                sql = f'INSERT INTO sw_property."{table}" AS current ({col_sql}) VALUES ({placeholders}) ON CONFLICT ("{pk}") {action}'
                values = [tuple(Jsonb(entry[c]) if c == "source_record" else entry[c] for c in columns) for entry in entries]
                with conn.cursor() as cur:
                    cur.executemany(sql, values)

            expected = {table:len(entries) for table,entries in batches.items()}
            expected["organisation"] = len({entry["organisation_id"] for entry in batches.get("organisation", [])})
            actual = {}
            for table, count in expected.items():
                actual[table] = conn.execute(f'SELECT count(*) FROM sw_property."{table}"').fetchone()[0]
                if actual[table] != count:
                    raise RuntimeError(f"{table}: expected {count} imported rows, database contains {actual[table]}")
            # Verify all FK relationships now, before transaction commit.
            fk_violations = conn.execute("""
                SELECT count(*) FROM (
                  SELECT u.unit_id FROM sw_property.unit_space u
                  LEFT JOIN sw_property.premises p ON p.premises_id=u.premises_id
                  LEFT JOIN sw_property.building b ON b.building_id=u.building_id
                  LEFT JOIN sw_property.property_site s ON s.property_id=u.property_id
                  WHERE p.premises_id IS NULL OR s.property_id IS NULL OR (u.building_id IS NOT NULL AND b.building_id IS NULL)
                  UNION ALL
                  SELECT e.establishment_id FROM sw_property.establishment e
                  LEFT JOIN sw_property.business b USING(business_id)
                  WHERE b.business_id IS NULL
                ) v
            """).fetchone()[0]
            if fk_violations:
                raise RuntimeError(f"Cross-reference reconciliation failed: {fk_violations} violations")
            size_bytes = conn.execute("SELECT pg_database_size(current_database())").fetchone()[0]
        return {"database":dbname,"release_id":release_id,"package_sha256":package_sha,"file_manifest":manifest_files,"source_collection_counts":source_counts,"verified_table_counts":actual,"cross_reference_violations":fk_violations,"database_size_bytes":size_bytes}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dsn",default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--expected-database",default="saltwater_test")
    args=parser.parse_args()
    if not args.dsn:
        parser.error("Set DATABASE_URL to the disposable PostgreSQL connection.")
    print(json.dumps(import_package(args.root,args.dsn,args.expected_database),indent=2,sort_keys=True))

if __name__=="__main__":
    main()
