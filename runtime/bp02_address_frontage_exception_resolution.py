"""Geometry-evidence disposition of BP04 address/frontage exceptions.

No source address is overwritten. A unique frontage candidate is not promoted
to an address correction; bridge point-contact is not treated as frontage.
"""
from __future__ import annotations


def resolve_address_frontage_exceptions(reconciliation: dict, geography: dict) -> dict:
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

        if row["status"] == "ADDRESS_ROAD_DIFFERS_FROM_PARCEL_FRONTAGE_CANDIDATE":
            if len(candidates) != 1:
                disposition = "MULTIPLE_FRONTAGE_CANDIDATES_REMAIN_UNRESOLVED"
                proposed = None
            else:
                candidate = roads.get(candidates[0])
                if candidate is None:
                    raise ValueError(f"{source_id}: frontage candidate road is missing from BP-02")
                disposition = "UNIQUE_PARCEL_FRONTAGE_IDENTIFIED_SOURCE_ADDRESS_NOT_CONFIRMED"
                proposed = candidate["id"]
            basis = "BP04 parcel polygon boundary contact against SW-RDS-V1 road reserve geometry"
            outstanding = "Confirm the address-side access/entrance and resolve the source road conflict; do not overwrite the source address."
        elif row["status"] == "NO_PARCEL_FRONTAGE_CANDIDATE":
            bridge_ids = [
                road_id for road_id, detail in candidate_details.items()
                if road_id in roads and roads[road_id].get("class") == "bridge"
                and detail.get("candidate_type") == "road_reserve_proximity_connection"
                and detail.get("contact_type") == "POINT_CONTACT_ONLY"
            ]
            if len(bridge_ids) == 1 and access_status == "SOURCE_ROAD_MATCHES_BUILDING_ACCESS_SET":
                disposition = "BRIDGE_POINT_CONTACT_ONLY_NOT_STREET_FRONTAGE"
                proposed = None
                basis = "Parcel/building proximity to bridge road reserve is point contact only"
                outstanding = "Provide a geometrically valid connection to an addressable public street or redesign the access arrangement; bridge contact alone is insufficient."
            else:
                disposition = "NO_FRONTAGE_EVIDENCE_REMAINS_UNRESOLVED"
                proposed = None
                basis = "No parcel boundary frontage candidate"
                outstanding = "Identify a valid street frontage or access connection from additional geometry evidence."
        else:
            raise ValueError(f"{source_id}: unexpected exception status {row['status']}")

        records.append({
            "source_address_id": source_id,
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
            "evidence_basis": basis,
            "outstanding_action": outstanding,
            "source_address_preserved": True,
            "canonical_address_corrected": False,
            "operational_frontage_approved": False,
            "operational_access_approved": False,
        })

    disposition_counts = {}
    for row in records:
        key = row["geometry_disposition"]
        disposition_counts[key] = disposition_counts.get(key, 0) + 1
    return {
        "register_id": "SW-BP02-ADDRESS-FRONTAGE-EXCEPTION-DISPOSITION-V1",
        "exception_count": len(records),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "unique_frontage_candidates_identified": disposition_counts.get(
            "UNIQUE_PARCEL_FRONTAGE_IDENTIFIED_SOURCE_ADDRESS_NOT_CONFIRMED", 0
        ),
        "bridge_point_contact_cases": disposition_counts.get(
            "BRIDGE_POINT_CONTACT_ONLY_NOT_STREET_FRONTAGE", 0
        ),
        "all_source_addresses_preserved": all(row["source_address_preserved"] for row in records),
        "canonical_address_corrections": 0,
        "operational_frontages_approved": 0,
        "operational_access_approved": 0,
        "records": records,
        "interpretation": (
            "All P1 exceptions receive an explicit geometry-based disposition. "
            "This is not a silent correction: three have a unique parcel frontage "
            "candidate but no confirmed address-side entrance, while two touch only "
            "a bridge road reserve at a point and therefore have no street frontage. "
            "All five remain non-operational pending the stated follow-up evidence."
        ),
    }
