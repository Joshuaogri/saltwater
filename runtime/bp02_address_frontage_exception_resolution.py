"""Evidence-based disposition of BP04/BP02 address-road exceptions.

The register separates address-road association from operational access approval.
Source records are preserved; candidate geometry never silently promotes a
canonical address or an operational entrance.
"""
from __future__ import annotations


def _bridge_has_public_street_connections(road_id: str, geography: dict) -> bool:
    roads = {row["id"]: row for row in geography.get("roads", [])}
    segments = geography.get("network", {}).get("segments", [])
    bridge_segments = [row for row in segments if row.get("road_id") == road_id]
    if not bridge_segments:
        return False
    for bridge in bridge_segments:
        for endpoint in (bridge.get("from_node_id"), bridge.get("to_node_id")):
            connected = [
                row for row in segments
                if row.get("road_id") != road_id
                and endpoint in (row.get("from_node_id"), row.get("to_node_id"))
                and row.get("access") == "public"
                and {"motor_vehicle", "emergency"}.issubset(set(row.get("modes", [])))
                and roads.get(row.get("road_id"), {}).get("class") != "bridge"
            ]
            if not connected:
                return False
    return True


def _valid_bridge_connector_rows(
    property_id: str | None,
    road_id: str,
    candidate_details: dict,
    geography: dict,
    direct_connector_audit: dict | None,
) -> list[dict]:
    if direct_connector_audit is None:
        return []
    bridge_segment_ids = {
        row["id"] for row in geography.get("network", {}).get("segments", [])
        if row.get("road_id") == road_id
    }
    if not bridge_segment_ids or not _bridge_has_public_street_connections(road_id, geography):
        return []
    detail = candidate_details.get(road_id, {})
    if (detail.get("candidate_type") != "road_reserve_proximity_connection"
            or detail.get("contact_type") != "POINT_CONTACT_ONLY"):
        return []
    if not isinstance(property_id, str) or not property_id:
        return []
    rows = [
        row for row in direct_connector_audit.get("connector_candidates", [])
        if row.get("property_id") == property_id
        and any(
            str(row.get("candidate_road_connection_id", "")).endswith(segment_id)
            for segment_id in bridge_segment_ids
        )
    ]
    if not rows:
        return []
    connector_pairs = [
        (row.get("candidate_access_point_id"), row.get("candidate_road_connection_id"))
        for row in rows
    ]
    if any(
        not isinstance(access_id, str) or not access_id
        or not isinstance(road_connection_id, str) or not road_connection_id
        for access_id, road_connection_id in connector_pairs
    ):
        return []
    # A road-reserve candidate may legitimately serve two distinct building
    # access-point approaches. Identity belongs to the access-point/road-
    # connection pair, not to the road-connection ID in isolation.
    access_point_ids = [access_id for access_id, _ in connector_pairs]
    if (len(connector_pairs) != len(set(connector_pairs))
            or len(access_point_ids) != len(set(access_point_ids))):
        return []
    valid = all(
        row.get("road_connection_type") == "road_reserve_proximity_connection"
        and row.get("road_connection_contact_type") == "POINT_CONTACT_ONLY"
        and row.get("geometry_status") == "DIRECT_GEOMETRY_FEASIBLE_UNREVIEWED"
        and row.get("property_contains_connector") is True
        and row.get("crosses_origin_building") is False
        and row.get("crosses_other_building") is False
        and row.get("crosses_water") is False
        for row in rows
    )
    return rows if valid else []


def resolve_address_frontage_exceptions(
    reconciliation: dict,
    geography: dict,
    direct_connector_audit: dict | None = None,
) -> dict:
    exceptions = reconciliation.get("address_frontage_exceptions_building_access_crosscheck", [])
    roads = {row["id"]: row for row in geography.get("roads", [])}
    records = []
    seen = set()
    for row in sorted(exceptions, key=lambda item: item["source_address_id"]):
        source_id = row["source_address_id"]
        if source_id in seen:
            raise ValueError(f"Duplicate frontage exception: {source_id}")
        seen.add(source_id)
        source_road = roads.get(row["source_road_id"])
        if source_road is None:
            raise ValueError(f"{source_id}: source road is missing from BP-02")
        candidates = row.get("candidate_frontage_road_ids", [])
        candidate_details = row.get("building_access_road_candidate_details", {})
        access_status = row.get("building_access_road_candidate_status")
        proposed = None
        resolved_access_road = None
        connector_count = 0
        connector_rows = []
        association_resolved = False

        if row["status"] == "ADDRESS_ROAD_DIFFERS_FROM_PARCEL_FRONTAGE_CANDIDATE":
            if len(candidates) != 1:
                disposition = "MULTIPLE_FRONTAGE_CANDIDATES_REMAIN_UNRESOLVED"
                outstanding = "Resolve the competing parcel frontage candidates before assigning an address road."
                basis = "BP04 parcel polygon boundary contact against SW-RDS-V1 road reserve geometry"
            else:
                candidate = roads.get(candidates[0])
                if candidate is None:
                    raise ValueError(f"{source_id}: frontage candidate road is missing from BP-02")
                proposed = candidate["id"]
                resolved_access_road = candidate["id"]
                association_resolved = True
                disposition = "UNIQUE_PARCEL_FRONTAGE_ROAD_ASSOCIATION_RESOLVED"
                outstanding = "Retain the original source-road value as provenance; canonical address promotion remains a separate release action."
                basis = "One unique parcel boundary frontage-road candidate; no competing frontage road is present."
        elif row["status"] == "NO_PARCEL_FRONTAGE_CANDIDATE":
            bridge_ids = [
                road_id for road_id, detail in candidate_details.items()
                if road_id in roads and roads[road_id].get("class") == "bridge"
                and detail.get("candidate_type") == "road_reserve_proximity_connection"
                and detail.get("contact_type") == "POINT_CONTACT_ONLY"
            ]
            if len(bridge_ids) == 1 and access_status == "SOURCE_ROAD_MATCHES_BUILDING_ACCESS_SET":
                bridge_id = bridge_ids[0]
                connector_rows = _valid_bridge_connector_rows(
                    row.get("property_id"), bridge_id, candidate_details, geography, direct_connector_audit
                )
                if connector_rows:
                    connector_count = len(connector_rows)
                    resolved_access_road = bridge_id
                    association_resolved = True
                    disposition = "BRIDGE_ACCESS_CONNECTOR_CANDIDATE_TO_CONNECTED_PUBLIC_ROAD_NETWORK"
                    basis = (
                        "Building-boundary connector candidates are geometrically feasible within the property, "
                        "terminate at the matching public bridge road reserve, and the bridge endpoints connect "
                        "to public motor-vehicle/emergency streets."
                    )
                    outstanding = (
                        "Verify the entrance and assess connector width, gradient, surface, drainage, clearance "
                        "and access controls before operational approval."
                    )
                else:
                    disposition = "BRIDGE_POINT_CONTACT_ONLY_NOT_STREET_FRONTAGE"
                    basis = "Parcel/building proximity to bridge road reserve is point contact only"
                    outstanding = (
                        "Validate a feasible property-to-bridge connector and confirm the bridge's public-street "
                        "network connection; bridge contact alone is insufficient."
                    )
            else:
                disposition = "NO_FRONTAGE_EVIDENCE_REMAINS_UNRESOLVED"
                basis = "No parcel boundary frontage candidate"
                outstanding = "Identify a valid street frontage or access connection from additional geometry evidence."
        else:
            raise ValueError(f"{source_id}: unexpected exception status {row['status']}")

        records.append({
            "source_address_id": source_id,
            "property_id": row.get("property_id"),
            "source_candidate_parcel_id": row["source_candidate_parcel_id"],
            "source_road_id": source_road["id"],
            "source_road_name": source_road["name"],
            "source_road_class": source_road["class"],
            "candidate_frontage_road_ids": candidates,
            "candidate_frontage_road_names": [roads[item]["name"] for item in candidates],
            "building_access_road_candidate_ids": row.get("building_access_road_candidate_ids", []),
            "building_access_road_candidate_details": candidate_details,
            "geometry_disposition": disposition,
            "proposed_frontage_road_id": proposed,
            "resolved_access_road_id": resolved_access_road,
            "address_road_association_resolved": association_resolved,
            "verified_geometric_connector_candidate_count": connector_count,
            "verified_geometric_connector_candidates": [
                {
                    "candidate_access_point_id": connector.get("candidate_access_point_id"),
                    "road_access_candidate_id": connector.get("candidate_road_connection_id"),
                }
                for connector in connector_rows
            ],
            "evidence_basis": basis,
            "outstanding_action": outstanding,
            "source_address_preserved": True,
            "canonical_address_corrected": False,
            "operational_frontage_approved": False,
            "operational_access_approved": False,
        })

    disposition_counts = {}
    for record in records:
        key = record["geometry_disposition"]
        disposition_counts[key] = disposition_counts.get(key, 0) + 1
    resolved_count = sum(1 for record in records if record["address_road_association_resolved"])
    bridge_count = sum(
        1 for record in records
        if record["geometry_disposition"] == "BRIDGE_ACCESS_CONNECTOR_CANDIDATE_TO_CONNECTED_PUBLIC_ROAD_NETWORK"
    )
    unresolved_count = len(records) - resolved_count
    return {
        "register_id": "SW-BP02-ADDRESS-FRONTAGE-EXCEPTION-DISPOSITION-V2",
        "exception_count": len(records),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "resolved_address_road_associations": resolved_count,
        "resolved_bridge_access_connection_candidates": bridge_count,
        "unresolved_exception_count": unresolved_count,
        "all_source_addresses_preserved": all(record["source_address_preserved"] for record in records),
        "canonical_address_corrections": 0,
        "operational_frontages_approved": 0,
        "operational_access_approved": 0,
        "records": records,
        "interpretation": (
            "The register resolves source-road association where one unique parcel frontage road exists, "
            "and recognises bridge access only when property-contained connector candidates are geometrically "
            "feasible and the public bridge is connected to public motor-vehicle/emergency streets. These are "
            "design-geometry dispositions only: no canonical address or operational access point is promoted."
        ),
    }
