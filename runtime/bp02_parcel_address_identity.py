"""Stable, versioned BP-02 parcel/address identities for the fictional design baseline.

These IDs establish portable source identity and lineage only. Candidate geometry
and source-derived address attributes remain unapproved for operational use until
the geography release gate is separately satisfied. No DB IDs or writes occur.
"""
from __future__ import annotations

import hashlib
from typing import Iterable


REGISTER_ID = "SW-PARCEL-ADDRESS-IDENTITY-V1"


def _stable_id(prefix: str, source_id: str) -> str:
    digest = hashlib.sha256(source_id.encode("utf-8")).hexdigest()[:16].upper()
    return f"{prefix}-{digest}"


def build_identity_register(
    candidate_manifest: dict,
    properties: Iterable[dict],
    addresses: Iterable[dict],
    geography_entity_codes: set[str],
) -> dict:
    properties = list(properties)
    addresses = list(addresses)
    candidates = candidate_manifest.get("parcels", [])
    candidate_by_id = {}
    for candidate in candidates:
        source_id = candidate.get("candidate_parcel_id")
        if not source_id or source_id in candidate_by_id:
            raise ValueError(f"Missing or duplicate parcel candidate ID: {source_id}")
        candidate_by_id[source_id] = candidate

    property_by_id = {}
    for row in properties:
        source_id = row.get("property_id")
        if not source_id or source_id in property_by_id:
            raise ValueError(f"Missing or duplicate property ID: {source_id}")
        property_by_id[source_id] = row

    address_by_id = {}
    for row in addresses:
        source_id = row.get("address_id")
        if not source_id or source_id in address_by_id:
            raise ValueError(f"Missing or duplicate source address ID: {source_id}")
        address_by_id[source_id] = row

    parcel_rows = []
    for candidate_id, candidate in sorted(candidate_by_id.items()):
        parcel_rows.append({
            "parcel_id": _stable_id("SWP", candidate_id),
            "source_candidate_parcel_id": candidate_id,
            "source_dataset": candidate.get("source_dataset"),
            "district_id": candidate.get("source_district_id"),
            "neighbourhood_id": candidate.get("source_neighbourhood_id"),
            "geometry": candidate.get("geometry"),
            "area_m2": candidate.get("area_m2"),
            "geometry_quality": candidate.get("geometry_quality", "unknown"),
            "frontage_segment_ids": list(candidate.get("road_frontage_segment_ids", [])),
            "identity_status": "STABLE_DESIGN_IDENTITY",
            "operational_status": "NOT_APPROVED_FOR_OPERATIONAL_SEED",
            "source_ref": candidate.get("source_ref"),
        })

    candidate_to_parcel = {
        row["source_candidate_parcel_id"]: row["parcel_id"] for row in parcel_rows
    }
    address_rows = []
    linked_properties = set()
    for source_address_id, source_address in sorted(address_by_id.items()):
        property_id = source_address.get("property_id")
        prop = property_by_id.get(property_id)
        if prop is None:
            raise ValueError(f"{source_address_id}: address property reference is unresolved")
        if prop.get("address_id") != source_address_id:
            raise ValueError(f"{source_address_id}: not the property's primary address")
        candidate_id = prop.get("source_candidate_parcel_id")
        parcel_id = candidate_to_parcel.get(candidate_id)
        if parcel_id is None:
            raise ValueError(f"{source_address_id}: linked parcel candidate is unresolved")
        road_id = source_address.get("road_id")
        district_id = source_address.get("district_id")
        neighbourhood_id = source_address.get("neighbourhood_id")
        for label, value in (("road", road_id), ("district", district_id), ("neighbourhood", neighbourhood_id)):
            if value not in geography_entity_codes:
                raise ValueError(f"{source_address_id}: {label} reference is not a BP-02 entity_code")
        if district_id != prop.get("source_district_id") or neighbourhood_id != prop.get("source_neighbourhood_id"):
            raise ValueError(f"{source_address_id}: address administrative context conflicts with property")
        linked_properties.add(property_id)
        address_rows.append({
            "address_id": _stable_id("SWA", source_address_id),
            "source_address_id": source_address_id,
            "property_id": property_id,
            "parcel_id": parcel_id,
            "road_id": road_id,
            "district_id": district_id,
            "neighbourhood_id": neighbourhood_id,
            "source_address_attributes": {
                key: value for key, value in source_address.items()
                if key not in {"address_id", "property_id", "road_id", "district_id", "neighbourhood_id"}
            },
            "identity_status": "STABLE_DESIGN_IDENTITY",
            "address_status": "SOURCE_DERIVED_NOT_OPERATIONALLY_VERIFIED",
            "frontage_status": "NOT_PROVEN_BY_IDENTITY_MAPPING",
            "operational_status": "NOT_APPROVED_FOR_OPERATIONAL_SEED",
        })

    if linked_properties != set(property_by_id):
        missing = sorted(set(property_by_id) - linked_properties)
        raise ValueError(f"Properties without exactly one mapped primary address: {missing[:10]}")
    if len(parcel_rows) != len(properties):
        raise ValueError(
            f"Parcel/property cardinality mismatch: parcels={len(parcel_rows)} properties={len(properties)}"
        )
    if len(address_rows) != len(properties):
        raise ValueError(
            f"Address/property cardinality mismatch: addresses={len(address_rows)} properties={len(properties)}"
        )
    parcel_ids = [row["parcel_id"] for row in parcel_rows]
    address_ids = [row["address_id"] for row in address_rows]
    if len(parcel_ids) != len(set(parcel_ids)) or len(address_ids) != len(set(address_ids)):
        raise ValueError("Stable parcel or address identity collision")

    return {
        "schema": "saltwater-bp02-parcel-address-identity/1.0",
        "register_id": REGISTER_ID,
        "source_geography": "SW-GEO-V1",
        "candidate_set_id": candidate_manifest.get("candidate_set_id"),
        "operational_approval": False,
        "parcel_identity_count": len(parcel_rows),
        "address_identity_count": len(address_rows),
        "property_primary_address_links": len(linked_properties),
        "spatial_id_policy": "PORTABLE_STRING_ID; database surrogate IDs are never embedded",
        "parcel_id_policy": "SWP- plus first 16 uppercase SHA-256 hex characters of immutable source candidate ID",
        "address_id_policy": "SWA- plus first 16 uppercase SHA-256 hex characters of immutable BP04 source address ID",
        "parcels": parcel_rows,
        "addresses": address_rows,
        "limitations": [
            "Parcel polygons remain generated design candidates, not approved cadastral boundaries.",
            "Road-reserve boundary contact is not legal or usable frontage.",
            "Source street labels and numbers are preserved but not independently verified by this identity register.",
            "No missing street number, entrance, postal attribute or frontage is invented.",
            "No operational approval, Neon write or database-specific spatial_id is created.",
        ],
    }
