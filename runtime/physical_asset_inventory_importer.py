"""Disposable-only BP04-03 Stage E physical asset and profile importer."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb


ACTOR = "BP04-03-STAGE-E-DISPOSABLE-IMPORTER"
REASON = "Deterministic BP04-03 Stage E generated design candidate import; not operational canon."


def _sha(value: dict) -> str:
    body = dict(value)
    body.pop("manifest_sha256", None)
    return hashlib.sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()).hexdigest()


def validate_manifests(inventory: dict, candidates: dict, dossiers: dict) -> tuple[str, str]:
    if inventory.get("operational_approval") is not False:
        raise ValueError("Operational asset manifests are not accepted by the disposable importer")
    if candidates.get("operational_approval") is not False or dossiers.get("operational_approval") is not False:
        raise ValueError("Operational geography manifests are not accepted")
    expected = _sha(inventory)
    if inventory.get("manifest_sha256") != expected:
        raise ValueError("Physical asset inventory manifest SHA-256 mismatch")
    if candidates.get("manifest_sha256") != inventory.get("candidate_manifest_sha256"):
        raise ValueError("Physical asset inventory candidate-manifest reference mismatch")
    if dossiers.get("manifest_sha256") != inventory.get("parcel_dossier_manifest_sha256"):
        raise ValueError("Physical asset inventory dossier-manifest reference mismatch")
    if dossiers.get("candidate_manifest_sha256") != candidates.get("manifest_sha256"):
        raise ValueError("Parcel dossier/candidate manifest reference mismatch")
    generation = inventory.get("generation", {})
    groups = ("properties", "buildings", "premises", "units", "access_points")
    expected_counts = {
        "properties": "property_count", "buildings": "building_count",
        "premises": "premises_count", "units": "unit_count",
        "access_points": "access_point_candidate_count",
    }
    for group in groups:
        rows = inventory.get(group)
        if not isinstance(rows, list) or len(rows) != generation.get(expected_counts[group]):
            raise ValueError(f"{group} count does not match the inventory manifest")
        ids = [row.get({
            "properties": "candidate_property_id", "buildings": "candidate_building_id",
            "premises": "candidate_premises_id", "units": "candidate_unit_id",
            "access_points": "candidate_access_point_id",
        }[group]) for row in rows]
        if None in ids or len(ids) != len(set(ids)):
            raise ValueError(f"{group} contains missing or duplicate candidate identities")
    property_ids = {row["candidate_property_id"] for row in inventory["properties"]}
    building_ids = {row["candidate_building_id"] for row in inventory["buildings"]}
    premises_ids = {row["candidate_premises_id"] for row in inventory["premises"]}
    for row in inventory["buildings"]:
        if row["property_id"] not in property_ids:
            raise ValueError("Building references a missing property candidate")
    for row in inventory["premises"]:
        if row["building_id"] not in building_ids or "property_id" in row:
            raise ValueError("Premises parent does not match BP04-01 single-parent identity rules")
    for row in inventory["units"]:
        if row["premises_id"] not in premises_ids or "building_id" in row:
            raise ValueError("Unit parent does not match BP04-01 premises-only identity rules")
    for row in inventory["access_points"]:
        if row["building_id"] not in building_ids or "premises_id" in row or "property_id" in row:
            raise ValueError("Access point parent does not match BP04-01 single-parent identity rules")
    connectors = inventory.get("access_connectors")
    if not isinstance(connectors, list) or len(connectors) != generation.get("access_connector_candidate_count"):
        raise ValueError("Access connector candidate count does not match the inventory manifest")
    access_ids = {row["candidate_access_point_id"] for row in inventory["access_points"]}
    connector_ids = [row.get("candidate_connector_id") for row in connectors]
    if None in connector_ids or len(connector_ids) != len(set(connector_ids)):
        raise ValueError("Access connector candidates contain missing or duplicate identities")
    if len(connectors) != len(access_ids):
        raise ValueError("Every building-boundary access candidate must have one connector candidate")
    for row in connectors:
        if row.get("access_point_candidate_id") not in access_ids:
            raise ValueError("Access connector references a missing access-point candidate")
        coordinates = row.get("geometry_coordinates")
        if (row.get("geometry_type") != "LineString" or not isinstance(coordinates, list)
                or len(coordinates) < 2 or coordinates[0] == coordinates[-1]):
            raise ValueError("Access connector must contain a valid multi-segment LineString with distinct endpoints")
        if not row.get("road_id") or not row.get("road_segment_ids"):
            raise ValueError("Access connector must retain road and road-segment lineage")
        if not row.get("road_access_candidate_id"):
            raise ValueError("Access connector must reference a road access candidate")
        if row.get("connector_type") not in (
            "BUILDING_TO_FRONTAGE_CANDIDATE",
            "BUILDING_TO_ROAD_RESERVE_PROXIMITY_CANDIDATE",
        ):
            raise ValueError("Access connector type is not recognised")
        if row.get("review_status") != "unreviewed_candidate" or row.get("geometry_status") != "UNREVIEWED_GEOMETRIC_LINE_ONLY":
            raise ValueError("Access connectors must remain unreviewed geometric candidates")
        if row.get("constructed_state") != "unknown" or row.get("surface_code") != "unknown":
            raise ValueError("Unobserved connector construction and surface attributes must remain unknown")
        for field in ("slope_state", "barrier_state", "pedestrian_suitability",
                      "vehicle_suitability", "accessibility_state", "legal_access_state",
                      "public_access_state", "emergency_egress_state"):
            if row.get(field) != "not_assessed":
                raise ValueError(f"Unassessed connector attribute {field} cannot be promoted")
        if row.get("connector_type") == "BUILDING_TO_FRONTAGE_CANDIDATE":
            if not row.get("frontage_candidate_id") or row.get("road_connection_candidate_id") is not None:
                raise ValueError("Frontage connector must reference frontage, not proximity, lineage")
        else:
            if row.get("frontage_candidate_id") is not None or not row.get("road_connection_candidate_id"):
                raise ValueError("Road-reserve proximity connector must retain separate non-frontage lineage")
    profiles = inventory.get("profiles", {})
    for group in groups:
        if len(profiles.get(group, [])) != len(inventory[group]):
            raise ValueError(f"{group} profiles are incomplete")
    if generation.get("canonical_addresses_created") != 0 or generation.get("operational_spatial_ids_assigned") != 0:
        raise ValueError("Stage E candidate importer must not allocate operational geography")
    if generation.get("operational_access_points_created") != 0:
        raise ValueError("Stage E access-location candidates cannot be operational access points")
    if generation.get("ownership_records_created") != 0 or generation.get("tenancy_records_created") != 0:
        raise ValueError("Stage E cannot create ownership or tenancy")
    if generation.get("occupancy_records_created") != 0 or generation.get("business_assignments_created") != 0:
        raise ValueError("Stage E cannot create occupancy or business assignments")
    if (generation.get("resolved_source_entity_code_mappings") != 100
            or generation.get("unresolved_source_entity_code_mappings") != 0
            or generation.get("unresolved_source_spatial_mappings") != 0):
        raise ValueError("All 100 source entity_code mappings must be resolved; database-specific spatial_id values remain unassigned")
    return expected, candidates["candidate_set_id"]


def _geojson(kind: str, coordinates: list) -> dict:
    return {"type": kind, "coordinates": coordinates}


def _geometry_hash(payload: dict) -> bytes:
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()).digest()


def _execute_many(cur, sql: str, rows: list[tuple]) -> int:
    if not rows:
        return 0
    cur.executemany(sql, rows)
    return len(rows)


def import_inventory(conn, inventory: dict, candidates: dict, dossiers: dict,
                     source_commit: str = "unknown") -> dict:
    if conn.info.dbname != "saltwater_test":
        raise RuntimeError("Refusing BP04-03 Stage E import outside database saltwater_test")
    manifest_sha, candidate_set_id = validate_manifests(inventory, candidates, dossiers)
    started = time.perf_counter()
    source_ref = f"BP04-03:{inventory['inventory_set_id']}:{manifest_sha}"
    candidate_sha = bytes.fromhex(candidates["manifest_sha256"])
    dossier_sha = bytes.fromhex(dossiers["manifest_sha256"])
    inventory_sha = bytes.fromhex(manifest_sha)
    generation = inventory["generation"]
    expected = {
        "property": len(inventory["properties"]), "building": len(inventory["buildings"]),
        "premises": len(inventory["premises"]), "unit": len(inventory["units"]),
        "access_point": len(inventory["access_points"]),
    }
    detail_counts = {key: len(value) for key, value in inventory["details"].items()}
    profile_counts = {key: len(value) for key, value in inventory["profiles"].items()}
    before_bytes = 0
    after_bytes = 0
    inserted = {}
    existing = False

    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("SELECT current_setting('server_version_num')::int")
            version = cur.fetchone()[0]
            if not 160000 <= version < 170000:
                raise RuntimeError("BP04-03 Stage E importer requires PostgreSQL 16")
            cur.execute("SELECT pg_database_size(current_database())")
            before_bytes = cur.fetchone()[0]
            cur.execute(
                "SELECT batch_id FROM sw_property.asset_generation_batch WHERE manifest_sha256=%s",
                (inventory_sha,),
            )
            batch = cur.fetchone()
            if batch:
                existing = True
                batch_id = batch[0]
                inserted = {"identities": 0, "relationships": 0, "profiles": 0,
                            "details": 0, "geometry": 0, "candidate_site_links": 0, "access_connector_candidates": 0}
            else:
                counts = {
                    "identities": expected, "profiles": profile_counts,
                    "details": detail_counts,
                    "geometry": len(inventory["properties"]) + len(inventory["buildings"]) + len(inventory["access_points"]),
                    "candidate_site_links": len(inventory["properties"]),
                    "access_connector_candidates": len(inventory["access_connectors"]),
                }
                cur.execute("""
                    INSERT INTO sw_property.asset_generation_batch
                    (inventory_set_id,source_dataset,candidate_set_id,generator_version,
                     coordinate_reference,manifest_sha256,candidate_manifest_sha256,
                     dossier_manifest_sha256,source_commit,record_counts,
                     unresolved_source_mapping_count,operational_approval,
                     source_ref,actor_ref,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,false,%s,%s,%s)
                    RETURNING batch_id
                """, (
                    inventory["inventory_set_id"], inventory["source_dataset"], candidate_set_id,
                    inventory["generator"], inventory["coordinate_reference"],
                    inventory_sha, candidate_sha, dossier_sha, source_commit,
                    Jsonb(counts), generation["unresolved_source_spatial_mappings"],
                    source_ref, ACTOR, REASON,
                ))
                batch_id = cur.fetchone()[0]
                property_map, building_map, premises_map, unit_map, access_map = {}, {}, {}, {}, {}

                # Canonical BP04-01 identities remain unresolved against BP-02:
                # candidate parcel references are held in a separate lineage table.
                for row in inventory["properties"]:
                    cur.execute("""
                        INSERT INTO sw_property.property_asset
                        (entity_code,display_name,location_status,parcel_spatial_id,
                         address_spatial_id,lifecycle_status,created_tick,source_ref,actor_ref,reason)
                        VALUES (%s,%s,'unresolved',NULL,NULL,'active',0,%s,%s,%s)
                        RETURNING property_id
                    """, (row["candidate_property_id"],row["display_name"],row["source_ref"],ACTOR,REASON))
                    property_map[row["candidate_property_id"]] = cur.fetchone()[0]

                for row in inventory["buildings"]:
                    cur.execute("""
                        INSERT INTO sw_property.building
                        (entity_code,display_name,lifecycle_status,created_tick,source_ref,actor_ref,reason)
                        VALUES (%s,%s,'active',0,%s,%s,%s) RETURNING building_id
                    """, (row["candidate_building_id"],row["display_name"],row["source_ref"],ACTOR,REASON))
                    building_map[row["candidate_building_id"]] = cur.fetchone()[0]
                    cur.execute("""
                        INSERT INTO sw_property.property_building
                        (property_id,building_id,valid_from_tick,source_ref,actor_ref,reason)
                        VALUES (%s,%s,0,%s,%s,%s)
                    """, (property_map[row["property_id"]],building_map[row["candidate_building_id"]],row["source_ref"],ACTOR,REASON))

                for row in inventory["premises"]:
                    cur.execute("""
                        INSERT INTO sw_property.premises
                        (entity_code,display_name,building_id,property_id,lifecycle_status,
                         created_tick,source_ref,actor_ref,reason)
                        VALUES (%s,%s,%s,NULL,'active',0,%s,%s,%s) RETURNING premises_id
                    """, (row["candidate_premises_id"],row["display_name"],
                          building_map[row["building_id"]],row["source_ref"],ACTOR,REASON))
                    premises_map[row["candidate_premises_id"]] = cur.fetchone()[0]
                    cur.execute("""
                        INSERT INTO sw_property.building_premises
                        (building_id,premises_id,valid_from_tick,source_ref,actor_ref,reason)
                        VALUES (%s,%s,0,%s,%s,%s)
                    """, (building_map[row["building_id"]],premises_map[row["candidate_premises_id"]],row["source_ref"],ACTOR,REASON))

                for row in inventory["units"]:
                    cur.execute("""
                        INSERT INTO sw_property.unit_space
                        (entity_code,display_name,premises_id,lifecycle_status,created_tick,source_ref,actor_ref,reason)
                        VALUES (%s,%s,%s,'active',0,%s,%s,%s) RETURNING unit_id
                    """, (row["candidate_unit_id"],row["display_name"],premises_map[row["premises_id"]],
                          row["source_ref"],ACTOR,REASON))
                    unit_map[row["candidate_unit_id"]] = cur.fetchone()[0]
                    cur.execute("""
                        INSERT INTO sw_property.premises_unit
                        (premises_id,unit_id,valid_from_tick,source_ref,actor_ref,reason)
                        VALUES (%s,%s,0,%s,%s,%s)
                    """, (premises_map[row["premises_id"]],unit_map[row["candidate_unit_id"]],row["source_ref"],ACTOR,REASON))

                for row in inventory["access_points"]:
                    cur.execute("""
                        INSERT INTO sw_property.access_point
                        (entity_code,display_name,building_id,premises_id,unit_id,lifecycle_status,
                         created_tick,source_ref,actor_ref,reason)
                        VALUES (%s,%s,%s,NULL,NULL,'active',0,%s,%s,%s) RETURNING access_point_id
                    """, (row["candidate_access_point_id"],row["display_name"],
                          building_map[row["building_id"]],row["source_ref"],ACTOR,REASON))
                    access_map[row["candidate_access_point_id"]] = cur.fetchone()[0]

                _execute_many(cur, """
                    INSERT INTO sw_property.access_connector_candidate
                    (batch_id,access_point_id,candidate_connector_id,candidate_access_point_id,
                     road_access_candidate_id,frontage_candidate_id,road_connection_candidate_id,
                     road_id,road_segment_ids,connector_type,contact_type,length_m,
                     coordinate_reference,geometry_payload,geometry_sha256,source_manifest_sha256,
                     geometry_status,review_status,constructed_state,surface_code,slope_state,
                     barrier_state,pedestrian_suitability,vehicle_suitability,accessibility_state,
                     legal_access_state,public_access_state,emergency_egress_state,
                     source_ref,actor_ref,confidence_code,effective_from_tick,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                            'UNREVIEWED_GEOMETRIC_LINE_ONLY','unreviewed_candidate','unknown','unknown',
                            'not_assessed','not_assessed','not_assessed','not_assessed',
                            'not_assessed','not_assessed','not_assessed','not_assessed',
                            %s,%s,%s,%s,%s)
                """, [(
                    batch_id, access_map[row["access_point_candidate_id"]],
                    row["candidate_connector_id"], row["access_point_candidate_id"],
                    row["road_access_candidate_id"], row["frontage_candidate_id"],
                    row["road_connection_candidate_id"], row["road_id"],
                    row["road_segment_ids"], row["connector_type"], row["contact_type"],
                    row["length_m"], row["coordinate_reference"],
                    Jsonb(_geojson("LineString", row["geometry_coordinates"])),
                    _geometry_hash(_geojson("LineString", row["geometry_coordinates"])),
                    inventory_sha, row["source_ref"], ACTOR, row["confidence_code"],
                    row["effective_from_tick"], row["reason"],
                ) for row in inventory["access_connectors"]])

                # Profiles are inserted only after all stable numeric identities exist.
                p = inventory["profiles"]
                profile_rows = []
                for row in p["properties"]:
                    profile_rows.append((property_map[row["candidate_property_id"]],row))
                _execute_many(cur, """
                    INSERT INTO sw_property.property_profile
                    (property_id,property_class,primary_use,secondary_uses,development_form,
                     site_state,boundary_status,terrain_code,drainage_state,perimeter_type,
                     utility_availability,source_ref,actor_ref,confidence_code,effective_from_tick,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [(i,r["property_class"],r["primary_use"],r["secondary_uses"],r["development_form"],
                       r["site_state"],r["boundary_status"],r["terrain_code"],r["drainage_state"],
                       r["perimeter_type"],r["utility_availability"],r["source_ref"],ACTOR,
                       r["confidence_code"],r["effective_from_tick"],r["reason"]) for i,r in profile_rows])

                _execute_many(cur, """
                    INSERT INTO sw_property.building_profile
                    (building_id,building_use,building_form,structure_class,construction_system,
                     foundation_type,roof_form,roof_covering,facade_system,storeys_above,storeys_below,
                     height_m,height_datum,structural_capacity_persons,authorised_capacity_persons,
                     construction_year,completion_year,heritage_status,source_ref,actor_ref,
                     confidence_code,effective_from_tick,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [(building_map[r["candidate_building_id"]],r["building_use"],r["building_form"],
                       r["structure_class"],r["construction_system"],r["foundation_type"],r["roof_form"],
                       r["roof_covering"],r["facade_system"],r["storeys_above"],r["storeys_below"],
                       r["height_m"],r["height_datum"],r["structural_capacity_persons"],
                       r["authorised_capacity_persons"],r["construction_year"],r["completion_year"],
                       r["heritage_status"],r["source_ref"],ACTOR,r["confidence_code"],
                       r["effective_from_tick"],r["reason"]) for r in p["buildings"]])

                _execute_many(cur, """
                    INSERT INTO sw_property.premises_profile
                    (premises_id,premises_type,primary_function,floor_level,orientation,fitout_standard,
                     occupancy_suitability,security_boundary,accessibility_state,source_ref,actor_ref,
                     confidence_code,effective_from_tick,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [(premises_map[r["candidate_premises_id"]],r["premises_type"],r["primary_function"],
                       r["floor_level"],r["orientation"],r["fitout_standard"],r["occupancy_suitability"],
                       r["security_boundary"],r["accessibility_state"],r["source_ref"],ACTOR,
                       r["confidence_code"],r["effective_from_tick"],r["reason"]) for r in p["premises"]])

                _execute_many(cur, """
                    INSERT INTO sw_property.unit_profile
                    (unit_id,unit_class,local_locator,floor_level,room_count,physical_capacity,
                     suitability_state,fitout_state,accessibility_state,source_ref,actor_ref,
                     confidence_code,effective_from_tick,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [(unit_map[r["candidate_unit_id"]],r["unit_class"],r["local_locator"],
                       r["floor_level"],r["room_count"],r["physical_capacity"],r["suitability_state"],
                       r["fitout_state"],r["accessibility_state"],r["source_ref"],ACTOR,
                       r["confidence_code"],r["effective_from_tick"],r["reason"]) for r in p["units"]])

                _execute_many(cur, """
                    INSERT INTO sw_property.access_point_profile
                    (access_point_id,access_type,access_modes,directionality,control_type,
                     availability_state,accessibility_state,emergency_egress,loading_capable,
                     emergency_egress_state,loading_capability_state,source_ref,actor_ref,
                     confidence_code,effective_from_tick,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [(access_map[r["candidate_access_point_id"]],r["access_type"],r["access_modes"],
                       r["directionality"],r["control_type"],r["availability_state"],r["accessibility_state"],
                       r["emergency_egress"],r["loading_capable"],r["emergency_egress_state"],
                       r["loading_capability_state"],r["source_ref"],ACTOR,r["confidence_code"],
                       r["effective_from_tick"],r["reason"]) for r in p["access_points"]])

                d = inventory["details"]
                entity_maps = {"PROPERTY":property_map,"BUILDING":building_map,
                               "PREMISES":premises_map,"UNIT":unit_map,"ACCESS_POINT":access_map}
                def entity_id(kind, code):
                    return entity_maps[kind][code]

                _execute_many(cur, """
                    INSERT INTO sw_property.physical_measurement
                    (entity_type,entity_id,measure_code,numeric_value,unit_code,measurement_basis,
                     precision_code,method_code,effective_from_tick,source_ref,actor_ref,confidence_code,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [(r["entity_type"],entity_id(r["entity_type"],r["entity_id"]),r["measure_code"],
                       r["numeric_value"],r["unit_code"],r["measurement_basis"],r["precision_code"],
                       r["method_code"],r["effective_from_tick"],r["source_ref"],ACTOR,
                       r["confidence_code"],r["reason"]) for r in d["measurements"]])

                level_map = {}
                for row in d["building_levels"]:
                    cur.execute("""
                        INSERT INTO sw_property.building_level
                        (building_id,level_code,level_name,level_order,level_type,source_ref,actor_ref,effective_from_tick,reason)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING level_id
                    """, (building_map[row["candidate_building_id"]],row["level_code"],row["level_name"],
                          row["level_order"],row["level_type"],row["source_ref"],ACTOR,
                          row["effective_from_tick"],row["reason"]))
                    level_map[(row["candidate_building_id"],row["level_code"])] = cur.fetchone()[0]

                _execute_many(cur, """
                    INSERT INTO sw_property.building_component
                    (building_id,level_id,component_type,material_code,condition_code,source_ref,actor_ref,effective_from_tick,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [(building_map[r["candidate_building_id"]],
                       level_map.get((r["candidate_building_id"],r["level_code"])) if r["level_code"] else None,
                       r["component_type"],r["material_code"],r["condition_code"],r["source_ref"],
                       ACTOR,r["effective_from_tick"],r["reason"]) for r in d["building_components"]])

                _execute_many(cur, """
                    INSERT INTO sw_property.premises_room
                    (premises_id,room_code,room_type,floor_level,area_m2,accessibility_state,source_ref,actor_ref,effective_from_tick,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [(premises_map[r["candidate_premises_id"]],r["room_code"],r["room_type"],
                       r["floor_level"],r["area_m2"],r["accessibility_state"],r["source_ref"],
                       ACTOR,r["effective_from_tick"],r["reason"]) for r in d["premises_rooms"]])

                _execute_many(cur, """
                    INSERT INTO sw_property.utility_system
                    (entity_type,entity_id,utility_type,availability_state,capacity_value,capacity_unit,
                     service_point_ref,source_ref,actor_ref,effective_from_tick,confidence_code,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [(r["entity_type"],entity_id(r["entity_type"],r["entity_id"]),r["utility_type"],
                       r["availability_state"],r["capacity_value"],r["capacity_unit"],r["service_point_ref"],
                       r["source_ref"],ACTOR,r["effective_from_tick"],r["confidence_code"],r["reason"])
                      for r in d["utility_systems"]])

                _execute_many(cur, """
                    INSERT INTO sw_property.physical_feature
                    (entity_type,entity_id,feature_type,feature_label,feature_state,source_ref,actor_ref,
                     effective_from_tick,confidence_code,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [(r["entity_type"],entity_id(r["entity_type"],r["entity_id"]),r["feature_type"],
                       r["feature_label"],r["feature_state"],r["source_ref"],ACTOR,
                       r["effective_from_tick"],r["confidence_code"],r["reason"]) for r in d["physical_features"]])

                _execute_many(cur, """
                    INSERT INTO sw_property.condition_assessment
                    (entity_type,entity_id,element_code,condition_code,assessed_tick,assessor_ref,
                     source_ref,confidence_code,findings,recommended_action)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [(r["entity_type"],entity_id(r["entity_type"],r["entity_id"]),r["element_code"],
                       r["condition_code"],r["assessed_tick"],ACTOR,r["source_ref"],r["confidence_code"],
                       r["findings"],r["recommended_action"]) for r in d["condition_assessments"]])

                _execute_many(cur, """
                    INSERT INTO sw_property.asset_assertion
                    (entity_type,entity_id,attribute_code,value_text,knowledge_state,effective_from_tick,
                     source_ref,actor_ref,confidence_code,reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [(r["entity_type"],entity_id(r["entity_type"],r["entity_id"]),r["attribute_code"],
                       r["value_text"],r["knowledge_state"],r["effective_from_tick"],r["source_ref"],
                       ACTOR,r["confidence_code"],r["reason"]) for r in d["asset_assertions"]])

                # Store source parcel lineage and geometry payloads after identity creation.
                parcel_by_id = {r["source_candidate_parcel_id"]: r for r in inventory["properties"]}
                for row in inventory["properties"]:
                    cur.execute("""
                        INSERT INTO sw_property.property_candidate_site
                        (property_id,batch_id,candidate_parcel_id,candidate_set_id,
                         candidate_manifest_sha256,dossier_manifest_sha256,review_status,
                         source_ref,actor_ref,confidence_code,reason)
                        VALUES (%s,%s,%s,%s,%s,%s,'unreviewed_candidate',%s,%s,'estimated',%s)
                    """, (property_map[row["candidate_property_id"]],batch_id,
                          row["source_candidate_parcel_id"],candidate_set_id,candidate_sha,dossier_sha,
                          row["source_ref"],ACTOR,REASON))

                geometry_rows = []
                for row in inventory["properties"]:
                    payload = _geojson("Polygon",row["geometry"])
                    geometry_rows.append(("PROPERTY",property_map[row["candidate_property_id"]],payload,row["source_ref"]))
                for row in inventory["buildings"]:
                    payload = _geojson("Polygon",row["geometry"])
                    geometry_rows.append(("BUILDING",building_map[row["candidate_building_id"]],payload,row["source_ref"]))
                for row in inventory["access_points"]:
                    payload = _geojson("Point",row["point_m"])
                    geometry_rows.append(("ACCESS_POINT",access_map[row["candidate_access_point_id"]],payload,row["source_ref"]))
                _execute_many(cur, """
                    INSERT INTO sw_property.asset_geometry_candidate
                    (batch_id,entity_type,entity_id,version_no,geometry_type,coordinate_reference,
                     geometry_payload,geometry_sha256,source_manifest_sha256,geometry_status,
                     source_ref,actor_ref,confidence_code,effective_from_tick,reason)
                    VALUES (%s,%s,%s,1,%s,%s,%s,%s,%s,'generated_design_candidate',%s,%s,'estimated',0,%s)
                """, [(batch_id,kind,ident,payload["type"],inventory["coordinate_reference"],
                       Jsonb(payload),_geometry_hash(payload),inventory_sha,row_ref,ACTOR,REASON)
                      for kind,ident,payload,row_ref in geometry_rows])

                inserted = {
                    "identities": sum(expected.values()),
                    "relationships": len(inventory["buildings"])+len(inventory["premises"])+len(inventory["units"]),
                    "profiles": sum(profile_counts.values()),
                    "details": sum(detail_counts.values()),
                    "geometry": len(geometry_rows),
                    "candidate_site_links": len(inventory["properties"]),
                    "access_connector_candidates": len(inventory["access_connectors"]),
                }

            cur.execute("SELECT pg_database_size(current_database())")
            after_bytes = cur.fetchone()[0]

    elapsed_ms = round((time.perf_counter()-started)*1000,3)
    return {
        "manifest_sha256": manifest_sha, "batch_id": batch_id,
        "already_imported": existing, "expected_identities": expected,
        "expected_profile_counts": profile_counts, "expected_detail_counts": detail_counts,
        "records_inserted_this_run": inserted,
        "database_growth_bytes": after_bytes-before_bytes,
        "elapsed_ms": elapsed_ms,
        "canonical_addresses_created": 0, "operational_access_points_created": 0,
        "unresolved_source_spatial_mappings": 0,
        "resolved_source_entity_code_mappings": 100,
        "unresolved_source_entity_code_mappings": 0,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--candidate-manifest",required=True)
    parser.add_argument("--dossier-manifest",required=True)
    parser.add_argument("--dsn",default=None)
    parser.add_argument("--source-commit",default=os.getenv("GITHUB_SHA","unknown"))
    args=parser.parse_args()
    inventory=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    candidates=json.loads(Path(args.candidate_manifest).read_text(encoding="utf-8"))
    dossiers=json.loads(Path(args.dossier_manifest).read_text(encoding="utf-8"))
    if args.dsn:
        conn=psycopg.connect(args.dsn)
    else:
        conn=psycopg.connect(
            host=os.getenv("PGHOST","localhost"),port=int(os.getenv("PGPORT","5432")),
            dbname=os.getenv("PGDATABASE","saltwater_test"),user=os.getenv("PGUSER","saltwater_test"),
            password=os.getenv("PGPASSWORD","test-only"))
    try:
        result=import_inventory(conn,inventory,candidates,dossiers,args.source_commit)
        print(json.dumps(result,indent=2,sort_keys=True))
    finally:
        conn.close()

if __name__=="__main__":
    main()
