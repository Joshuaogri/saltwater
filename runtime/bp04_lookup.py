"""Gameplay-facing, in-memory lookup layer for the compressed BP04 source archives.

The compressed Neon archives remain the sole static-world source of truth. This
module builds small process-local indexes for identity and navigation; it does
not create or persist typed property/business rows and does not claim BP-02
canonical parcel/address activation.
"""
from __future__ import annotations

import re
from typing import Any, Iterable

from runtime.bp04_archive_reader import load_dataset

WORLD = "SW-PROPERTY-WORLD-V1"
BUSINESSES = "SW-BUSINESS-REGISTRY-V1"

# Collection -> entity type -> stable identity field -> fields retained in the
# process-local lookup index. Full source archives remain untouched.
COLLECTIONS = {
    WORLD: {
        "properties": ("property", "property_id", (
            "property_id", "address_id", "source_candidate_parcel_id",
            "source_district_id", "source_neighbourhood_id", "primary_use",
            "site_state", "canonical_status", "building_ids",
        )),
        "addresses": ("address", "address_id", (
            "address_id", "property_id", "address_label", "street_number",
            "street_name", "road_id", "postcode", "district_id", "district_name",
            "neighbourhood_id", "neighbourhood_name", "building_ids",
            "address_type", "source_ref",
        )),
        "buildings": ("building", "building_id", (
            "building_id", "property_id", "address_id", "building_number",
            "building_form", "building_use", "building_configuration",
            "storeys_above", "construction_year", "building_condition",
            "premises_ids", "access_point_ids",
        )),
        "premises": ("premises", "premises_id", (
            "premises_id", "property_id", "building_id", "address_id",
            "floor_name", "primary_function", "unit_ids",
        )),
        "units": ("unit", "unit_id", (
            "unit_id", "property_id", "building_id", "premises_id", "address_id",
            "unit_locator", "unit_class", "primary_use", "occupancy_state",
            "operator_business_id",
        )),
        "access_points": ("access_point", "access_point_id", (
            "access_point_id", "property_id", "building_id", "premises_id",
            "unit_id", "access_type", "access_modes",
        )),
    },
    BUSINESSES: {
        "businesses": ("business", "business_id", (
            "business_id", "registered_name", "trading_name", "sector",
            "primary_activity", "legal_form", "business_size", "employee_band",
            "status", "parent_business_id", "primary_establishment_id",
            "registered_address_id",
        )),
        "establishments": ("establishment", "establishment_id", (
            "establishment_id", "business_id", "establishment_name",
            "establishment_type", "property_id", "building_id", "premises_id",
            "unit_id", "address_id", "district_id", "neighbourhood_id",
            "floor_level", "unit_locator", "operating_status", "customer_access",
            "delivery_access",
        )),
    },
}

ALIASES = {
    "property": "property", "property_id": "property",
    "address": "address", "address_id": "address",
    "building": "building", "building_id": "building",
    "premises": "premises", "premises_id": "premises",
    "unit": "unit", "unit_id": "unit",
    "access_point": "access_point", "access_point_id": "access_point",
    "business": "business", "business_id": "business",
    "establishment": "establishment", "establishment_id": "establishment",
}


def _normalise(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").casefold()).strip()


def _rows(document: dict, collection_name: str) -> Iterable[dict]:
    collection = document.get("tables", {}).get(collection_name)
    if collection is None:
        raise KeyError(f"BP04 collection not found: {collection_name}")
    columns = collection.get("columns")
    values = collection.get("rows")
    if not isinstance(columns, list) or not isinstance(values, list):
        raise ValueError(f"Malformed BP04 collection: {collection_name}")
    for number, values_row in enumerate(values):
        if not isinstance(values_row, list) or len(values_row) != len(columns):
            raise ValueError(f"Malformed BP04 row {collection_name}[{number}]")
        yield dict(zip(columns, values_row))


class BP04Lookup:
    """Build a read-only process-local index from the three core BP04 datasets.

    Construction reads each archive once, verifies its SHA-256 through the
    archive reader, and retains only identity/navigation fields. Recreate the
    instance after a new release is activated; do not use it as a write model.
    """

    def __init__(self, conn):
        self._by_id: dict[str, dict[str, dict]] = {
            kind: {} for kind in set(ALIASES.values())
        }
        self._search_rows: dict[str, list[dict]] = {
            "address": [], "business": [], "property": []
        }
        self._businesses_by_property: dict[str, list[str]] = {}
        self._establishments_by_business: dict[str, list[dict]] = {}
        self._buildings_by_property: dict[str, list[dict]] = {}
        self._addresses_by_property: dict[str, dict] = {}
        self._source_counts: dict[str, int] = {}

        for dataset_id, collections in COLLECTIONS.items():
            document = load_dataset(conn, dataset_id)
            for collection_name, (kind, id_field, retained_fields) in collections.items():
                count = 0
                for source_row in _rows(document, collection_name):
                    identity = source_row.get(id_field)
                    if not identity:
                        raise ValueError(
                            f"Missing {id_field} in {dataset_id}.{collection_name}"
                        )
                    key = str(identity)
                    if key in self._by_id[kind]:
                        raise ValueError(f"Duplicate {kind} identity: {key}")
                    record = {field: source_row.get(field) for field in retained_fields}
                    record["record_type"] = kind
                    self._by_id[kind][key] = record
                    count += 1
                self._source_counts[f"{dataset_id}.{collection_name}"] = count

        self._search_rows["address"] = list(self._by_id["address"].values())
        self._search_rows["property"] = list(self._by_id["property"].values())
        self._search_rows["business"] = list(self._by_id["business"].values())

        for address in self._by_id["address"].values():
            property_id = address.get("property_id")
            if property_id:
                if property_id in self._addresses_by_property:
                    raise ValueError(f"Multiple primary address records for property {property_id}")
                self._addresses_by_property[property_id] = address

        for building in self._by_id["building"].values():
            self._buildings_by_property.setdefault(building.get("property_id"), []).append(building)

        for establishment in self._by_id["establishment"].values():
            business_id = establishment.get("business_id")
            property_id = establishment.get("property_id")
            if business_id:
                self._establishments_by_business.setdefault(business_id, []).append(establishment)
            if property_id and business_id:
                self._businesses_by_property.setdefault(property_id, []).append(business_id)

        # Fail closed on dangling core identity links instead of returning
        # misleading partial details to gameplay callers.
        for property_id, prop in self._by_id["property"].items():
            address_id = prop.get("address_id")
            if address_id and address_id not in self._by_id["address"]:
                raise ValueError(f"Property {property_id} references missing address {address_id}")
        for address in self._by_id["address"].values():
            if address.get("property_id") not in self._by_id["property"]:
                raise ValueError(f"Address {address['address_id']} references missing property")
        for building in self._by_id["building"].values():
            if building.get("property_id") not in self._by_id["property"]:
                raise ValueError(f"Building {building['building_id']} references missing property")
        for establishment in self._by_id["establishment"].values():
            for field, kind in (
                ("business_id", "business"), ("property_id", "property"),
                ("building_id", "building"), ("premises_id", "premises"),
                ("unit_id", "unit"), ("address_id", "address"),
            ):
                value = establishment.get(field)
                if value and value not in self._by_id[kind]:
                    raise ValueError(
                        f"Establishment {establishment['establishment_id']} "
                        f"references missing {kind} {value}"
                    )

    @property
    def counts(self) -> dict[str, int]:
        """Number of indexed source identities, by dataset collection."""
        return dict(self._source_counts)

    def get(self, entity_type: str, identifier: str) -> dict | None:
        """Return one indexed identity record, or None when it does not exist."""
        kind = ALIASES.get(entity_type)
        if kind is None:
            raise ValueError(f"Unsupported BP04 entity type: {entity_type}")
        record = self._by_id[kind].get(str(identifier))
        return dict(record) if record is not None else None

    def search(self, entity_type: str, query: str, limit: int = 20) -> list[dict]:
        """Case-insensitive partial search; deterministic and strictly bounded."""
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
            raise ValueError("limit must be an integer from 1 to 100")
        kind = ALIASES.get(entity_type)
        if kind not in {"address", "business", "property"}:
            raise ValueError("search supports address, business or property")
        needle = _normalise(query)
        if len(needle) < 2:
            raise ValueError("search query must contain at least two characters")
        fields = {
            "address": ("address_id", "address_label", "street_name", "postcode",
                        "district_name", "neighbourhood_name"),
            "business": ("business_id", "registered_name", "trading_name",
                         "sector", "primary_activity"),
            "property": ("property_id", "source_candidate_parcel_id",
                        "primary_use", "source_district_id", "source_neighbourhood_id"),
        }[kind]
        matches = []
        for record in self._search_rows[kind]:
            haystack = " ".join(_normalise(record.get(field)) for field in fields)
            if needle in haystack:
                matches.append(record)
        matches.sort(key=lambda row: str(row.get({
            "address": "address_id", "business": "business_id",
            "property": "property_id"
        }[kind])))
        return [dict(row) for row in matches[:limit]]

    def property_detail(self, property_id: str) -> dict | None:
        """Resolve a property, its primary address, buildings and operators."""
        prop = self.get("property", property_id)
        if prop is None:
            return None
        address_id = prop.get("address_id")
        address = self.get("address", address_id) if address_id else None
        buildings = sorted(
            (dict(row) for row in self._buildings_by_property.get(property_id, [])),
            key=lambda row: str(row.get("building_id")),
        )
        businesses = []
        for business_id in sorted(set(self._businesses_by_property.get(property_id, []))):
            business = self.get("business", business_id)
            if business:
                businesses.append(business)
        return {
            "property": prop,
            "address": address,
            "buildings": buildings,
            "businesses": businesses,
            "geography_binding": "source_geography_reference_only",
        }

    def business_detail(self, business_id: str) -> dict | None:
        """Resolve a business and all establishments to their property addresses."""
        business = self.get("business", business_id)
        if business is None:
            return None
        establishments = []
        for source in sorted(
            self._establishments_by_business.get(business_id, []),
            key=lambda row: str(row.get("establishment_id")),
        ):
            row = dict(source)
            row["address"] = self.get("address", row.get("address_id")) if row.get("address_id") else None
            row["property"] = self.get("property", row.get("property_id")) if row.get("property_id") else None
            establishments.append(row)
        return {"business": business, "establishments": establishments}

    def address_detail(self, address_id: str) -> dict | None:
        """Resolve an address to its property and physical buildings."""
        address = self.get("address", address_id)
        if address is None:
            return None
        detail = self.property_detail(address["property_id"])
        if detail is None:
            return None
        detail["address"] = address
        return detail
