"""Playable BP-02 fictional engineering and canonical geography release.

All dimensions and engineering outcomes here are invented game-world facts,
not real-world survey claims. IDs and geometry lineage are taken from the
versioned Saltwater source manifests.
"""
from __future__ import annotations

BRIDGE_PROFILES = {
    "SWR-B1": {
        "bridge_name": "Customs Bridge",
        "district": "East Harbour",
        "surface": "reinforced_concrete",
        "access_control": "public_access_with_port_security_cctv",
        "road_width_m": 4.5,
        "vertical_clearance_m": 4.8,
        "gradient_pct": 3.2,
        "crossfall_pct": 2.0,
        "load_limit_t": 32.0,
        "drainage": "kerb_channels_to_silt_traps",
        "vehicle_class": "all_standard_emergency_and_service_vehicles",
    },
    "SWR-B2": {
        "bridge_name": "Harbour Bridge",
        "district": "Old Quays",
        "surface": "heavy_duty_asphalt",
        "access_control": "public_access_with_harbour_patrol_cctv",
        "road_width_m": 4.2,
        "vertical_clearance_m": 4.6,
        "gradient_pct": 4.1,
        "crossfall_pct": 2.0,
        "load_limit_t": 30.0,
        "drainage": "slot_drains_to_oil_water_interceptor",
        "vehicle_class": "all_standard_emergency_and_service_vehicles",
    },
}


def build_fictional_bridge_assessments(route_corridor_report: dict) -> dict:
    """Assess the four generated game-world bridge connectors in-world."""
    corridors = route_corridor_report.get("route_corridors", [])
    records = []
    for road_id, profile in BRIDGE_PROFILES.items():
        candidates = sorted(
            (row for row in corridors if row.get("road_id") == road_id),
            key=lambda row: row.get("source_connector_candidate_id", ""),
        )
        if len(candidates) != 2:
            raise ValueError(f"{road_id}: expected two game connector candidates, got {len(candidates)}")
        for index, candidate in enumerate(candidates, start=1):
            cid = candidate.get("source_connector_candidate_id")
            if not cid or not candidate.get("candidate_property_id") or not candidate.get("candidate_access_point_id"):
                raise ValueError(f"{road_id}: incomplete connector lineage")
            width = profile["road_width_m"] - (0.1 if index == 2 else 0.0)
            records.append({
                "assessment_id": f"SW-BP02-FENG-{cid}",
                "bridge_road_id": road_id,
                "bridge_name": profile["bridge_name"],
                "district": profile["district"],
                "source_connector_candidate_id": cid,
                "candidate_route_corridor_id": candidate["candidate_route_corridor_id"],
                "candidate_access_point_id": candidate["candidate_access_point_id"],
                "candidate_building_id": candidate["candidate_building_id"],
                "candidate_property_id": candidate["candidate_property_id"],
                "source_candidate_parcel_id": candidate["source_candidate_parcel_id"],
                "candidate_centreline_length_m": candidate["centreline_length_m"],
                "fictional_assessment": True,
                "engineering_status": "ASSESSED_PASS",
                "entrance_configuration": "controlled_flush_threshold_with_mountable_kerb",
                "clear_width_m": width,
                "vertical_clearance_m": profile["vertical_clearance_m"],
                "maximum_gradient_pct": profile["gradient_pct"] + (0.3 if index == 2 else 0.0),
                "maximum_crossfall_pct": profile["crossfall_pct"],
                "surface": profile["surface"],
                "surface_condition": "good_no_material_defects",
                "design_load_limit_tonnes": profile["load_limit_t"],
                "drainage": profile["drainage"],
                "obstacles": "none_within_defined_clear_route_envelope",
                "access_control": profile["access_control"],
                "public_access": "open_24_hours",
                "pedestrian_access": "continuous_1_8m_clear_side_path",
                "step_free_access": True,
                "emergency_vehicle_suitability": profile["vehicle_class"],
                "emergency_egress": "two_directional_exit_to_connected_public_road_network",
                "lighting": "LED_FULL_COVERAGE_WITH_BACKUP_POWER",
                "inspection_interval_days": 90,
                "operational_access_status": "APPROVED_IN_GAME",
                "operational_access_approved": True,
                "approved_access_modes": ["pedestrian", "patrol_vehicle", "fire_appliance", "ambulance", "service_vehicle"],
                "fictional_record_note": "Invented Saltwater simulation specification; no real-world measurement is represented.",
            })
    records.sort(key=lambda row: row["assessment_id"])
    return {
        "register_id": "SW-BP02-FICTIONAL-BRIDGE-ENGINEERING-V1",
        "source_candidate_manifest_sha256": route_corridor_report.get("manifest_sha256"),
        "fictional_game_world_assessments": True,
        "assessment_count": len(records),
        "assessed_count": sum(row["engineering_status"] == "ASSESSED_PASS" for row in records),
        "operationally_approved_count": sum(row["operational_access_approved"] for row in records),
        "records": records,
    }


def build_canonical_geography_register(identity_register: dict, asset_inventory: dict,
                                        engineering_register: dict) -> dict:
    """Promote stable source identities into the playable canonical game register."""
    parcels = []
    for row in identity_register.get("parcels", []):
        parcels.append({
            **row,
            "identity_status": "CANONICAL",
            "operational_status": "ACTIVE_IN_GAME",
            "canonical": True,
        })
    addresses = []
    for row in identity_register.get("addresses", []):
        addresses.append({
            **row,
            "identity_status": "CANONICAL",
            "address_status": "ACTIVE_IN_GAME",
            "frontage_status": (
                "GEOMETRY_ASSOCIATION_RESOLVED" if row.get("address_road_candidate_id")
                else "NO_FRONTAGE_CANDIDATE_RECORDED"
            ),
            "operational_status": "ACTIVE_IN_GAME",
            "canonical": True,
        })
    access_points = []
    for row in asset_inventory.get("access_points", []):
        access_points.append({
            **row,
            "operational_status": "ACTIVE_IN_GAME",
            "access_point_status": "ACTIVE_IN_GAME",
            "canonical": True,
        })
    connectors = []
    approved_by_candidate = {
        row["source_connector_candidate_id"]: row
        for row in engineering_register["records"]
    }
    for row in asset_inventory.get("access_connectors", []):
        assessment = approved_by_candidate.get(row["candidate_connector_id"])
        if assessment:
            connectors.append({
                **row,
                "engineering_assessment_id": assessment["assessment_id"],
                "operational_status": "ACTIVE_IN_GAME",
                "access_modes": assessment["approved_access_modes"],
                "canonical": True,
            })
    if len(parcels) != 420 or len(addresses) != 420:
        raise ValueError(f"Expected 420 parcels and addresses, got {len(parcels)} / {len(addresses)}")
    if len({row["parcel_id"] for row in parcels}) != 420:
        raise ValueError("Canonical parcel IDs are not unique")
    if len({row["address_id"] for row in addresses}) != 420:
        raise ValueError("Canonical address IDs are not unique")
    if any(row["parcel_id"] not in {p["parcel_id"] for p in parcels} for row in addresses):
        raise ValueError("Canonical address references an absent parcel")
    if len(engineering_register["records"]) != 4 or len(connectors) != 4:
        raise ValueError("All four bridge connector assessments must bind to source connectors")
    return {
        "register_id": "SW-BP02-CANONICAL-GEOGRAPHY-V1",
        "source_identity_register": identity_register["register_id"],
        "parcel_count": len(parcels),
        "address_count": len(addresses),
        "property_primary_address_link_count": identity_register["property_primary_address_links"],
        "building_access_point_count": len(access_points),
        "bridge_connector_count": len(connectors),
        "fictional_game_world_canon": True,
        "operational_release_status": "RELEASED_FOR_GAMEPLAY",
        "parcels": parcels,
        "addresses": addresses,
        "access_points": access_points,
        "bridge_connectors": connectors,
        "database_write_performed": False,
        "neon_write_performed": False,
    }
