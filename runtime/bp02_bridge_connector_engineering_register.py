"""BP-02 engineering evidence register for the four bridge access candidates.

This register is deliberately fail-closed: geometric candidates are not
entrances, constructed paths, or operational access points.
"""
from __future__ import annotations

BRIDGE_ROAD_IDS = ("SWR-B1", "SWR-B2")
EXPECTED_CONNECTORS_PER_BRIDGE = 2

ENGINEERING_EVIDENCE_FIELDS = (
    "surveyed_entrance_reference",
    "surveyed_connector_alignment",
    "measured_clear_width_m",
    "measured_vertical_clearance_m",
    "elevation_profile_reference",
    "maximum_longitudinal_gradient_pct",
    "maximum_crossfall_pct",
    "verified_surface_and_condition",
    "drainage_inspection_reference",
    "physical_obstacle_inspection_reference",
    "access_control_and_gate_details",
    "public_or_authorised_access_basis",
    "emergency_vehicle_suitability_assessment",
    "emergency_egress_assessment",
)


def build_bridge_connector_engineering_register(route_corridor_report: dict) -> dict:
    """Create four site-specific evidence work items without inventing facts."""
    corridors = route_corridor_report.get("route_corridors", [])
    rows = []
    for road_id in BRIDGE_ROAD_IDS:
        matches = sorted(
            (row for row in corridors if row.get("road_id") == road_id),
            key=lambda row: row.get("source_connector_candidate_id", ""),
        )
        if len(matches) != EXPECTED_CONNECTORS_PER_BRIDGE:
            raise ValueError(
                f"{road_id}: expected {EXPECTED_CONNECTORS_PER_BRIDGE} connector candidates; "
                f"found {len(matches)}"
            )
        for candidate in matches:
            connector_id = candidate.get("source_connector_candidate_id")
            property_id = candidate.get("candidate_property_id")
            if not connector_id or not property_id:
                raise ValueError(f"{road_id}: connector candidate lacks identity lineage")
            rows.append({
                "engineering_work_item_id": f"SW-BP02-ENG-{connector_id}",
                "bridge_road_id": road_id,
                "source_connector_candidate_id": connector_id,
                "candidate_access_point_id": candidate.get("candidate_access_point_id"),
                "candidate_building_id": candidate.get("candidate_building_id"),
                "candidate_property_id": property_id,
                "source_candidate_parcel_id": candidate.get("source_candidate_parcel_id"),
                "candidate_route_corridor_id": candidate.get("candidate_route_corridor_id"),
                "centreline_length_m": candidate.get("centreline_length_m"),
                "geometry_status": candidate.get("centreline_status"),
                "engineering_status": "NOT_ASSESSED",
                "operational_access_status": "HOLD_NOT_APPROVED",
                "evidence": {field: None for field in ENGINEERING_EVIDENCE_FIELDS},
                "missing_evidence": list(ENGINEERING_EVIDENCE_FIELDS),
                "entrance_verified": False,
                "constructed_route_verified": False,
                "vehicle_suitability_confirmed": False,
                "emergency_egress_confirmed": False,
                "operational_access_approved": False,
            })
    rows.sort(key=lambda row: row["engineering_work_item_id"])
    return {
        "register_id": "SW-BP02-BRIDGE-CONNECTOR-ENGINEERING-REGISTER-V1",
        "source_connector_manifest_sha256": route_corridor_report.get("source_connector_manifest_sha256"),
        "candidate_manifest_sha256": route_corridor_report.get("manifest_sha256"),
        "expected_bridge_road_ids": list(BRIDGE_ROAD_IDS),
        "expected_connector_count": 4,
        "engineering_work_item_count": len(rows),
        "assessed_count": 0,
        "operationally_approved_count": 0,
        "all_candidate_identities_complete": True,
        "all_required_evidence_explicitly_unassessed": all(
            all(value is None for value in row["evidence"].values())
            and row["engineering_status"] == "NOT_ASSESSED"
            for row in rows
        ),
        "all_operational_access_holds_preserved": all(
            row["operational_access_status"] == "HOLD_NOT_APPROVED"
            and row["operational_access_approved"] is False
            for row in rows
        ),
        "records": rows,
        "release_rule": (
            "A connector remains on hold until every required evidence field is supplied "
            "from a traceable, site-specific in-world survey/engineering record, reviewed, "
            "and separately approved for its intended access modes. Geometric feasibility "
            "or public-road connectivity alone never grants operational access."
        ),
        "database_write_performed": False,
        "neon_write_performed": False,
    }
