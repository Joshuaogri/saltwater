"""Cross-register identity audit for no-building sites and frontage exceptions.

The no-building site population is counted independently from the single
primary review classification, because a site can also carry a higher-priority
frontage exception. This is read-only design evidence, not a property change.
"""
from __future__ import annotations


def reconcile_no_building_sites_and_frontage_exceptions(
    address_review_register: dict,
    frontage_exception_resolution: dict,
) -> dict:
    review_rows = address_review_register.get("records", [])
    exceptions = frontage_exception_resolution.get("records", [])

    by_address = {}
    by_property = {}
    for row in review_rows:
        address_id = row.get("source_address_id")
        property_id = row.get("source_property_id")
        parcel_id = row.get("source_candidate_parcel_id")
        if not address_id or not property_id or not parcel_id:
            raise ValueError("Review row is missing source address, property or parcel identity")
        if address_id in by_address:
            raise ValueError(f"Duplicate review source address: {address_id}")
        if property_id in by_property:
            raise ValueError(f"Duplicate review property identity: {property_id}")
        by_address[address_id] = row
        by_property[property_id] = row

    if len(review_rows) != address_review_register.get("address_count"):
        raise ValueError("Address review register count does not match its records")

    no_building_rows = [
        row for row in review_rows
        if row.get("building_access_status") == "NO_BUILDING_ON_PROPERTY_SITE"
    ]
    no_building_properties = {row["source_property_id"] for row in no_building_rows}
    if len(no_building_properties) != len(no_building_rows):
        raise ValueError("No-building site population contains duplicate property identities")

    exception_addresses = set()
    exception_properties = set()
    exception_rows = []
    no_building_exception_properties = set()
    for exception in exceptions:
        address_id = exception.get("source_address_id")
        property_id = exception.get("property_id")
        parcel_id = exception.get("source_candidate_parcel_id")
        if not address_id or not property_id or not parcel_id:
            raise ValueError("Frontage exception is missing source address, property or parcel identity")
        if address_id in exception_addresses:
            raise ValueError(f"Duplicate frontage exception address: {address_id}")
        if property_id in exception_properties:
            raise ValueError(f"Duplicate frontage exception property: {property_id}")
        exception_addresses.add(address_id)
        exception_properties.add(property_id)
        review = by_address.get(address_id)
        if review is None:
            raise ValueError(f"{address_id}: frontage exception has no address review row")
        if (
            review["source_property_id"] != property_id
            or review["source_candidate_parcel_id"] != parcel_id
            or review["source_road_id"] != exception.get("source_road_id")
        ):
            raise ValueError(f"{address_id}: frontage exception identity/provenance differs from review register")
        is_no_building = property_id in no_building_properties
        if is_no_building:
            no_building_exception_properties.add(property_id)
        exception_rows.append({
            "source_address_id": address_id,
            "property_id": property_id,
            "source_candidate_parcel_id": parcel_id,
            "source_road_id": exception["source_road_id"],
            "no_building_site": is_no_building,
            "review_class": review["review_class"],
            "review_priority": review["review_priority"],
            "geometry_disposition": exception.get("geometry_disposition"),
        })

    if len(exceptions) != frontage_exception_resolution.get("exception_count"):
        raise ValueError("Frontage exception count does not match its records")

    review_class_counts = {}
    for row in no_building_rows:
        key = row["review_class"]
        review_class_counts[key] = review_class_counts.get(key, 0) + 1

    no_building_site_records = [
        {
            "source_address_id": row["source_address_id"],
            "property_id": row["source_property_id"],
            "source_candidate_parcel_id": row["source_candidate_parcel_id"],
            "source_road_id": row["source_road_id"],
            "review_class": row["review_class"],
            "review_priority": row["review_priority"],
        }
        for row in sorted(no_building_rows, key=lambda item: item["source_property_id"])
    ]

    return {
        "audit": "SW-BP02-NO-BUILDING-FRONTAGE-CROSS-REGISTER-IDENTITY",
        "address_review_record_count": len(review_rows),
        "no_building_site_count": len(no_building_rows),
        "no_building_property_count": len(no_building_properties),
        "no_building_review_class_counts": dict(sorted(review_class_counts.items())),
        "frontage_exception_count": len(exceptions),
        "frontage_exceptions_on_no_building_sites": len(no_building_exception_properties),
        "frontage_exceptions_on_sites_with_building_candidates": (
            len(exceptions) - len(no_building_exception_properties)
        ),
        "no_building_sites": no_building_site_records,
        "frontage_exception_crosswalk": sorted(
            exception_rows, key=lambda item: item["source_address_id"]
        ),
        "all_exception_identities_match_review_register": True,
        "database_write_performed": False,
        "operational_approval": False,
    }
