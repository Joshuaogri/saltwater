"""Deterministic BP-02 address-placement review queue from BP04 source evidence.

This register organizes review work; it does not correct source addresses,
create canonical operational addresses, or prove frontage/access.
"""
from __future__ import annotations

from typing import Iterable


def build_address_review_register(
    identity_register: dict,
    building_access_reconciliation: dict,
) -> dict:
    parcels = {
        row["source_candidate_parcel_id"]: row
        for row in identity_register.get("parcels", [])
    }
    addresses = identity_register.get("addresses", [])
    access_rows = {
        row["source_address_id"]: row
        for row in building_access_reconciliation.get("address_access_road_results", [])
    }
    if len(parcels) != identity_register.get("parcel_identity_count"):
        raise ValueError("Parcel identity register is incomplete or duplicated")
    if len(addresses) != identity_register.get("address_identity_count"):
        raise ValueError("Address identity register is incomplete or duplicated")
    if len(access_rows) != building_access_reconciliation.get("address_count"):
        raise ValueError("Building-access reconciliation is incomplete or duplicated")

    rows = []
    seen_source_ids = set()
    for address in sorted(addresses, key=lambda row: row["source_address_id"]):
        source_id = address["source_address_id"]
        if source_id in seen_source_ids:
            raise ValueError(f"Duplicate source address in review register: {source_id}")
        seen_source_ids.add(source_id)
        parcel_id = address["source_candidate_parcel_id"]
        if parcel_id not in parcels:
            raise ValueError(f"{source_id}: parcel identity is unresolved")
        access = access_rows.get(source_id)
        if access is None:
            raise ValueError(f"{source_id}: building-access evidence is unresolved")

        frontage_status = address["road_frontage_match_status"]
        access_status = access["status"]
        if frontage_status == "ADDRESS_ROAD_DIFFERS_FROM_PARCEL_FRONTAGE_CANDIDATE":
            review_class = "ROAD_REFERENCE_CONFLICT"
            priority = "P1"
        elif frontage_status == "NO_PARCEL_FRONTAGE_CANDIDATE":
            review_class = "NO_PARCEL_FRONTAGE_EVIDENCE"
            priority = "P1"
        elif access_status == "NO_BUILDING_ON_PROPERTY_SITE":
            review_class = "NO_BUILDING_ON_PROPERTY_SITE"
            priority = "P2"
        elif access_status != "SOURCE_ROAD_MATCHES_BUILDING_ACCESS_SET":
            review_class = "BUILDING_ACCESS_ROAD_REVIEW"
            priority = "P2"
        else:
            review_class = "SOURCE_CONTEXT_COHERENT_CANDIDATE"
            priority = "P3"

        rows.append({
            "source_address_id": source_id,
            "design_address_id": address["address_id"],
            "source_property_id": address["property_id"],
            "design_parcel_id": address["parcel_id"],
            "source_candidate_parcel_id": parcel_id,
            "source_road_id": address["road_id"],
            "frontage_candidate_road_ids": address["candidate_frontage_road_ids"],
            "proposed_frontage_road_id": address["address_road_candidate_id"],
            "frontage_status": frontage_status,
            "building_access_candidate_road_ids": access["candidate_access_road_ids"],
            "building_access_candidate_road_id": access["address_access_road_candidate_id"],
            "building_access_status": access_status,
            "review_class": review_class,
            "review_priority": priority,
            "source_road_preserved": True,
            "operational_address_approved": False,
            "operational_access_confirmed": False,
        })

    counts = {}
    priority_counts = {}
    for row in rows:
        counts[row["review_class"]] = counts.get(row["review_class"], 0) + 1
        priority_counts[row["review_priority"]] = priority_counts.get(row["review_priority"], 0) + 1

    return {
        "schema": "saltwater-bp02-address-placement-review/1.0",
        "register_id": "SW-BP02-ADDRESS-PLACEMENT-REVIEW-V1",
        "source_identity_register": identity_register.get("register_id"),
        "address_count": len(rows),
        "review_class_counts": dict(sorted(counts.items())),
        "review_priority_counts": dict(sorted(priority_counts.items())),
        "priority_1_review_count": priority_counts.get("P1", 0),
        "all_source_roads_preserved": all(row["source_road_preserved"] for row in rows),
        "operational_addresses_approved": 0,
        "operational_access_points_confirmed": 0,
        "database_write_performed": False,
        "records": rows,
        "interpretation": (
            "This is a deterministic review queue, not an address correction or "
            "approval. P1 identifies frontage/address evidence conflicts or absent "
            "frontage candidates. P2 identifies sites without a building or other "
            "building-access evidence requiring review. P3 means source context is "
            "coherent across the available geometric candidates only. All records "
            "remain non-operational until BP-02 geography release."
        ),
    }
