"""Reconcile BP04 source address roads with BP02 building-access road candidates.

All building/access/connector evidence is geometric design-candidate evidence.
It never confirms a door, driveway, legal frontage, usable route or operational
access. Original address road references are preserved unchanged.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable


def reconcile_building_access_roads(
    properties: Iterable[dict],
    addresses: Iterable[dict],
    dossiers: dict,
    assets: dict,
) -> dict:
    properties, addresses = list(properties), list(addresses)
    property_by_id = {}
    for row in properties:
        key = row.get("property_id")
        if not key or key in property_by_id:
            raise ValueError(f"Missing or duplicate property ID: {key}")
        property_by_id[key] = row

    buildings = {row["candidate_building_id"]: row for row in assets.get("buildings", [])}
    dossier_by_parcel = {
        row["dossier"]["candidate_parcel_id"]: row for row in dossiers.get("parcels", [])
    }
    access_roads = defaultdict(dict)
    unresolved_access_points = []

    for access in assets.get("access_points", []):
        access_id = access.get("candidate_access_point_id")
        building = buildings.get(access.get("building_id"))
        if building is None:
            raise ValueError(f"{access_id}: access point has no candidate building")
        parcel_id = building.get("source_candidate_parcel_id")
        dossier = dossier_by_parcel.get(parcel_id)
        if dossier is None:
            raise ValueError(f"{access_id}: building parcel has no BP02 dossier")
        candidate_id = access.get("road_link_candidate_id")
        if candidate_id is None:
            unresolved_access_points.append(access_id)
            continue
        candidates = {
            row["access_candidate_id"]: row
            for row in dossier.get("access_candidates", [])
        }
        candidate = candidates.get(candidate_id)
        if candidate is None:
            raise ValueError(f"{access_id}: road connection candidate is unresolved")
        road_id = candidate.get("road_id")
        if not road_id:
            unresolved_access_points.append(access_id)
            continue
        access_roads[parcel_id][road_id] = {
            "candidate_type": candidate.get("candidate_type"),
            "contact_type": candidate.get("contact_type"),
        }

    results = []
    status_counts = defaultdict(int)
    resolved = 0
    for address in addresses:
        address_id = address.get("address_id")
        prop = property_by_id.get(address.get("property_id"))
        if prop is None:
            raise ValueError(f"{address_id}: address property reference is unresolved")
        parcel_id = prop.get("source_candidate_parcel_id")
        candidates = access_roads.get(parcel_id, {})
        candidate_roads = sorted(candidates)
        source_road = address.get("road_id")
        if source_road in candidates:
            candidate_road, status = source_road, "SOURCE_ROAD_MATCHES_BUILDING_ACCESS_SET"
        elif len(candidate_roads) == 1:
            candidate_road, status = candidate_roads[0], "SINGLE_ALTERNATIVE_BUILDING_ACCESS_ROAD_REQUIRES_REVIEW"
        elif len(candidate_roads) > 1:
            candidate_road, status = None, "MULTIPLE_BUILDING_ACCESS_ROADS_REQUIRE_REVIEW"
        else:
            candidate_road, status = None, "NO_BUILDING_ACCESS_ROAD_CANDIDATE"
        if candidate_road:
            resolved += 1
        status_counts[status] += 1
        results.append({
            "source_address_id": address_id,
            "source_candidate_parcel_id": parcel_id,
            "source_road_id": source_road,
            "candidate_access_road_ids": candidate_roads,
            "candidate_access_road_details": candidates,
            "address_access_road_candidate_id": candidate_road,
            "status": status,
        })

    return {
        "address_count": len(addresses),
        "address_access_road_candidate_references_resolved": resolved,
        "address_access_road_candidate_status_counts": dict(sorted(status_counts.items())),
        "unresolved_building_access_point_count": len(unresolved_access_points),
        "unresolved_building_access_point_ids": sorted(unresolved_access_points),
        "address_access_road_results": results,
        "operational_access_confirmed": False,
        "database_write_performed": False,
        "interpretation": (
            "A matching road ID is a geometric building-access candidate only. "
            "A proximity or point-contact candidate does not prove a constructed "
            "entrance, driveway, traversable path, legal access or emergency egress."
        ),
    }
