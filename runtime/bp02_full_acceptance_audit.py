"""Read-only consolidated BP-02 parcel, address and access-point acceptance audit."""
from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

from runtime.geography_geometry_audit import audit_geometry
from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.parcel_dossier_geometry_audit import audit_parcel_dossiers
from runtime.physical_asset_inventory_generator import build_asset_inventory
from runtime.building_access_candidate_audit import audit_building_access_candidates
from runtime.building_access_connector_topology_audit import audit_connector_topology
from runtime.building_access_connector_audit import audit_direct_access_connectors
from runtime.building_access_route_corridor_audit import build_route_corridor_candidates
from runtime.bp04_geography_reconciliation import (
    GEO_PATH, IDENTITY_MAP_PATH, PROPERTY_WORLD_PATH,
    _read_columnar_gzip, build_reconciliation,
)
from runtime.bp02_address_frontage_exception_resolution import (
    resolve_address_frontage_exceptions,
)
from runtime.bp02_fictional_geography_release import (
    build_fictional_bridge_assessments,
    build_canonical_geography_register,
)
from runtime.bp02_no_building_site_reconciliation import (
    reconcile_no_building_sites_and_frontage_exceptions,
)

ROOT = Path(__file__).resolve().parents[1]


def _timed_stage(name: str, function, *args):
    started = perf_counter()
    print(f"BP02_STAGE_START name={name}", flush=True)
    try:
        result = function(*args)
    except Exception:
        print(f"BP02_STAGE_FAILED name={name} elapsed_seconds={perf_counter() - started:.3f}", flush=True)
        raise
    print(f"BP02_STAGE_DONE name={name} elapsed_seconds={perf_counter() - started:.3f}", flush=True)
    return result


def run_full_bp02_acceptance_audit() -> dict:
    source = _timed_stage("load_geography_source", lambda: json.loads(GEO_PATH.read_text(encoding="utf-8")))
    identity_map = _timed_stage("load_identity_map", lambda: json.loads(IDENTITY_MAP_PATH.read_text(encoding="utf-8")))
    property_document = _timed_stage("load_property_world", _read_columnar_gzip, PROPERTY_WORLD_PATH)

    geometry = _timed_stage("source_geometry_audit", audit_geometry, GEO_PATH)
    candidates = _timed_stage("parcel_candidate_generation", build_candidates, source)
    dossiers = _timed_stage("parcel_dossier_generation", build_parcel_dossiers, source, candidates)
    assets = _timed_stage("physical_asset_inventory_generation", build_asset_inventory, source, candidates, dossiers)

    parcel_geometry = _timed_stage("parcel_dossier_geometry_audit", audit_parcel_dossiers, source, candidates, dossiers)
    building_access = _timed_stage("building_access_candidate_audit", audit_building_access_candidates, candidates, dossiers, assets)
    connector_topology = _timed_stage("access_connector_topology_audit", audit_connector_topology, source, candidates, dossiers, assets)
    direct_connectors = _timed_stage("direct_access_connector_audit", audit_direct_access_connectors, source, candidates, dossiers, assets)
    route_corridors = _timed_stage("route_corridor_candidate_audit", build_route_corridor_candidates, source, candidates, dossiers, assets)
    reconciliation = _timed_stage(
        "bp04_geography_reconciliation", build_reconciliation,
        source, identity_map, property_document, candidates, dossiers, assets,
    )
    exception_resolution = _timed_stage("address_frontage_exception_resolution", resolve_address_frontage_exceptions, reconciliation, source, direct_connectors)
    if exception_resolution["unresolved_exception_count"]:
        unresolved_ids = {
            row["source_address_id"] for row in exception_resolution["records"]
            if not row["address_road_association_resolved"]
        }
        diagnostic = []
        for row in exception_resolution["records"]:
            if row["source_address_id"] not in unresolved_ids:
                continue
            property_connectors = [
                {
                    key: candidate.get(key)
                    for key in (
                        "candidate_access_point_id", "candidate_road_connection_id",
                        "road_connection_type", "road_connection_contact_type",
                        "geometry_status", "property_contains_connector",
                        "crosses_origin_building", "crosses_other_building", "crosses_water",
                    )
                }
                for candidate in direct_connectors.get("connector_candidates", [])
                if candidate.get("property_id") == row.get("property_id")
            ]
            diagnostic.append({
                "source_address_id": row["source_address_id"],
                "property_id": row.get("property_id"),
                "source_candidate_parcel_id": row["source_candidate_parcel_id"],
                "source_road_id": row["source_road_id"],
                "building_access_road_candidate_status": row["building_access_road_candidate_status"],
                "building_access_road_candidate_ids": row["building_access_road_candidate_ids"],
                "building_access_road_candidate_details": row["building_access_road_candidate_details"],
                "geometry_disposition": row["geometry_disposition"],
                "verified_geometric_connector_candidate_count": row["verified_geometric_connector_candidate_count"],
                "property_direct_connector_candidates": property_connectors,
            })
        print("BP02_UNRESOLVED_FRONTAGE_EXCEPTION_DIAGNOSTICS=" + json.dumps(diagnostic, sort_keys=True))
    bridge_engineering_register = _timed_stage(
        "fictional_bridge_engineering_register", build_fictional_bridge_assessments,
        route_corridors, exception_resolution,
    )
    canonical_geography = _timed_stage(
        "canonical_geography_register", build_canonical_geography_register,
        reconciliation["bp02_design_identity_register_data"], assets,
        bridge_engineering_register, exception_resolution,
    )
    no_building_cross_register = _timed_stage(
        "no_building_frontage_cross_register", reconcile_no_building_sites_and_frontage_exceptions,
        reconciliation["bp02_address_placement_review_register"], exception_resolution,
    )

    address_source_integrity = {
        "property_records": reconciliation["property_records"],
        "address_records": reconciliation["address_records"],
        "property_address_links": reconciliation["primary_property_address_links_resolved"],
        "district_entity_code_matches": reconciliation["district_entity_code_matches"],
        "neighbourhood_entity_code_matches": reconciliation["neighbourhood_entity_code_matches"],
        "road_entity_code_matches": reconciliation["road_entity_code_matches"],
        "design_parcel_identity_matches": reconciliation["bp02_design_parcel_identity_matches"],
        "design_address_identity_matches": reconciliation["bp02_design_address_identity_matches"],
        "canonical_parcel_identity_matches": reconciliation["canonical_parcel_identity_matches"],
        "canonical_address_identity_matches": reconciliation["canonical_address_identity_matches"],
    }

    structural_checks = {
        "source_geography_geometry": not geometry["failed_checks"],
        "parcel_polygon_dossiers": not parcel_geometry["failed_checks"],
        "building_boundary_access_candidates": not building_access["failed_checks"],
        "access_connector_topology": not connector_topology["failed_checks"],
        "direct_connector_geometry": not direct_connectors["failed_checks"],
        "route_corridor_candidate_geometry": not route_corridors["failed_checks"],
        "all_420_property_address_links_resolve": (
            address_source_integrity["property_records"] == 420
            and address_source_integrity["address_records"] == 420
            and address_source_integrity["property_address_links"] == 420
        ),
        "all_address_area_and_road_references_resolve": (
            address_source_integrity["district_entity_code_matches"] == 420
            and address_source_integrity["neighbourhood_entity_code_matches"] == 420
            and address_source_integrity["road_entity_code_matches"] == 420
        ),
        "all_five_frontage_exceptions_have_geometry_dispositions": (
            exception_resolution["exception_count"] == 5
            and exception_resolution["all_source_addresses_preserved"]
            and sum(exception_resolution["disposition_counts"].values()) == 5
        ),
        "all_three_unique_frontage_road_associations_resolved": (
            exception_resolution["disposition_counts"].get("UNIQUE_PARCEL_FRONTAGE_ROAD_ASSOCIATION_RESOLVED", 0) == 3
        ),
        "both_bridge_access_connector_candidates_resolved": (
            exception_resolution["resolved_bridge_access_connection_candidates"] == 2
            and sum(
                row["verified_geometric_connector_candidate_count"]
                for row in exception_resolution["records"]
            ) == 4
        ),
        "no_unresolved_address_road_access_exceptions": (
            exception_resolution["unresolved_exception_count"] == 0
        ),
        "no_building_and_frontage_exception_identities_reconcile": (
            no_building_cross_register["all_exception_identities_match_review_register"]
            and no_building_cross_register["no_building_site_count"] == 36
            and no_building_cross_register["frontage_exception_count"] == 5
            and no_building_cross_register["frontage_exceptions_on_no_building_sites"] == 3
            and no_building_cross_register["frontage_exceptions_on_sites_with_building_candidates"] == 2
        ),
    }

    operational_gates = {
        "approved_operational_geography_source": (
            source.get("status") == "APPROVED_FOR_OPERATIONAL_USE"
        ),
        "canonical_parcels_materialised": (
            canonical_geography["parcel_count"] == 420
            and len({row["parcel_id"] for row in canonical_geography["parcels"]}) == 420
        ),
        "canonical_addresses_materialised": (
            canonical_geography["address_count"] == 420
            and len({row["address_id"] for row in canonical_geography["addresses"]}) == 420
            and canonical_geography["property_primary_address_link_count"] == 420
            and canonical_geography["resolved_address_exception_count"] == 5
            and all(row["address_road_association_resolved"] for row in canonical_geography["addresses"])
        ),
        "identity_register_released_for_gameplay": (
            canonical_geography["identity_register_operational_approval"]
            and canonical_geography["identity_register_release_status"] == "RELEASED_FOR_GAMEPLAY"
        ),
        "operational_access_points_approved": canonical_geography["building_access_point_count"] > 0
            and canonical_geography["bridge_connector_count"] == 4,
        "all_four_bridge_approaches_match_engineering_assessments": (
            bridge_engineering_register["assessment_count"] == 4
            and bridge_engineering_register["approach_count"] == 4
            and bridge_engineering_register["all_approach_identities_unique"]
            and bridge_engineering_register["all_source_connector_identities_unique"]
            and len({row["candidate_route_corridor_id"] for row in bridge_engineering_register["records"]}) == 4
            and bridge_engineering_register["assessed_count"] == 4
            and bridge_engineering_register["operationally_approved_count"] == 4
        ),
        "all_address_road_access_exceptions_resolved": (
            exception_resolution["unresolved_exception_count"] == 0
        ),
    }

    all_structural = all(structural_checks.values())
    all_operational = all(operational_gates.values())
    return {
        "audit": "SW-BP02-FULL-PARCEL-ADDRESS-ACCESS-ACCEPTANCE",
        "audit_version": "1.1",
        "source_geography": source.get("dataset_id"),
        "source_geography_status": source.get("status"),
        "structural_status": "PASS" if all_structural else "FAIL",
        "operational_release_status": "PASS" if all_operational else "BLOCKED",
        "overall_status": "PASS" if all_structural and all_operational else "STRUCTURAL_PASS_OPERATIONAL_RELEASE_BLOCKED" if all_structural else "FAIL",
        "address_source_integrity": address_source_integrity,
        "frontage_exception_resolution": exception_resolution,
        "no_building_site_cross_register_reconciliation": no_building_cross_register,
        "bridge_connector_engineering_register": bridge_engineering_register,
        "canonical_geography_register": canonical_geography,
        "layer_reports": {
            "geography_geometry": geometry,
            "parcel_geometry": parcel_geometry,
            "building_access_candidates": building_access,
            "access_connector_topology": connector_topology,
            "direct_access_connectors": direct_connectors,
            "route_corridor_candidates": {
                "summary": route_corridors["summary"],
                "checks": route_corridors["checks"],
                "passed_checks": route_corridors["passed_checks"],
                "failed_checks": route_corridors["failed_checks"],
                "exceptions": route_corridors["exceptions"],
                "operational_approval": route_corridors["operational_approval"],
            },
        },
        "structural_checks": structural_checks,
        "operational_gates": operational_gates,
        "counts": {
            "candidate_parcels": len(candidates["parcels"]),
            "parcel_dossiers": len(dossiers["parcels"]),
            "parcel_frontage_candidates": parcel_geometry["counts"]["frontage_candidates"],
            "parcel_access_location_candidates": parcel_geometry["counts"]["access_location_candidates"],
            "property_sites": len(assets["properties"]),
            "building_candidates": len(assets["buildings"]),
            "building_boundary_access_candidates": len(assets["access_points"]),
            "access_connector_candidates": len(assets.get("access_connectors", [])),
            "address_records": reconciliation["address_records"],
            "frontage_exceptions": exception_resolution["exception_count"],
            "no_building_property_sites": no_building_cross_register["no_building_property_count"],
            "no_building_sites_with_frontage_exceptions": no_building_cross_register["frontage_exceptions_on_no_building_sites"],
            "frontage_exceptions_on_sites_with_building_candidates": no_building_cross_register["frontage_exceptions_on_sites_with_building_candidates"],
            "resolved_address_road_associations": exception_resolution["resolved_address_road_associations"],
            "resolved_bridge_access_connection_candidates": exception_resolution["resolved_bridge_access_connection_candidates"],
            "unresolved_address_road_access_exceptions": exception_resolution["unresolved_exception_count"],
            "operational_access_points": canonical_geography["building_access_point_count"],
            "canonical_parcels": canonical_geography["parcel_count"],
            "canonical_addresses": canonical_geography["address_count"],
            "canonical_bridge_connectors": canonical_geography["bridge_connector_count"],
            "bridge_connector_engineering_assessments": bridge_engineering_register["assessment_count"],
            "bridge_connector_engineering_assessed": bridge_engineering_register["assessed_count"],
        },
        "authority": {
            "operational_approval": all(operational_gates.values()),
            "canonical_address_promotion": canonical_geography["address_count"] == 420,
            "operational_access_point_promotion": canonical_geography["building_access_point_count"] > 0,
            "database_write_performed": False,
            "neon_write_performed": False,
        },
        "resolved_findings": [
            "All three source-road conflicts have one unique parcel frontage road association; original source values remain preserved as provenance.",
            "Both bridge properties have two feasible property-contained connector candidates to public bridges connected to public streets.",
        ],
        "blockers": [],
    }


def main() -> None:
    report = run_full_bp02_acceptance_audit()
    target = Path("bp02-full-parcel-address-access-acceptance.json")
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "audit": report["audit"],
        "overall_status": report["overall_status"],
        "structural_status": report["structural_status"],
        "operational_release_status": report["operational_release_status"],
        "counts": report["counts"],
        "structural_checks": report["structural_checks"],
        "operational_gates": report["operational_gates"],
        "frontage_exception_dispositions": report["frontage_exception_resolution"]["disposition_counts"],
        "layer_failure_details": {
            "building_access": {
                "failed_checks": report["layer_reports"]["building_access_candidates"]["failed_checks"],
                "exception_counts": {
                    key: len(value) for key, value
                    in report["layer_reports"]["building_access_candidates"]["exceptions"].items()
                },
            },
            "route_corridors": {
                "failed_checks": report["layer_reports"]["route_corridor_candidates"]["failed_checks"],
                "exception_counts": {
                    key: len(value) for key, value
                    in report["layer_reports"]["route_corridor_candidates"]["exceptions"].items()
                },
                "exception_samples": {
                    key: value[:5] for key, value
                    in report["layer_reports"]["route_corridor_candidates"]["exceptions"].items()
                    if value
                },
            },
        },
        "authority": report["authority"],
    }, indent=2, sort_keys=True))
    if report["overall_status"] != "PASS":
        raise SystemExit("BP-02 full gameplay acceptance failed; see generated report")


if __name__ == "__main__":
    main()
