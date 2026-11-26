import gzip
import hashlib
import json
import unittest

from runtime.bp04_lookup import BP04Lookup


def archive(dataset_id, tables):
    document = {
        "storage_format": "textual_json_columnar_v1",
        "metadata": {"dataset_id": dataset_id},
        "tables": {
            name: {
                "columns": list(rows[0]) if rows else [],
                "rows": [[row.get(column) for column in (list(rows[0]) if rows else [])] for row in rows],
            }
            for name, rows in tables.items()
        },
    }
    payload = gzip.compress(json.dumps(document, separators=(",", ":")).encode())
    return payload, hashlib.sha256(payload).hexdigest()


class FakeConnection:
    def __init__(self, archives):
        self.archives = archives

    def execute(self, _sql, params):
        payload, digest = self.archives[params[0]]

        class Result:
            def fetchone(inner_self):
                return payload, digest

        return Result()


def tables_from_archive(payload):
    document = json.loads(gzip.decompress(payload).decode())
    return {
        name: [dict(zip(table["columns"], row)) for row in table["rows"]]
        for name, table in document["tables"].items()
    }


class BP04LookupTests(unittest.TestCase):
    def setUp(self):
        world = {
            "properties": [{
                "property_id": "SWPROP-0001", "address_id": "SWADDR-0001",
                "source_candidate_parcel_id": "SWPAR-0001",
                "source_district_id": "DISTRICT-01",
                "source_neighbourhood_id": "NEIGHBOURHOOD-01",
                "primary_use": "commercial", "site_state": "developed",
                "canonical_status": "active", "building_ids": ["SWBLD-0001"],
            }],
            "addresses": [{
                "address_id": "SWADDR-0001", "property_id": "SWPROP-0001",
                "address_label": "10 Harbour Avenue, Central, Saltwater",
                "street_number": 10, "street_name": "Harbour Avenue",
                "road_id": "SWROAD-01", "postcode": "SW-01 1AB",
                "district_id": "DISTRICT-01", "district_name": "Central",
                "neighbourhood_id": "NEIGHBOURHOOD-01",
                "neighbourhood_name": "Harbour Quarter",
                "building_ids": ["SWBLD-0001"], "address_type": "primary_site_address",
                "source_ref": "SW-GEO-V1:SWPAR-0001",
            }],
            "buildings": [{
                "building_id": "SWBLD-0001", "property_id": "SWPROP-0001",
                "address_id": "SWADDR-0001", "building_number": "A",
                "building_form": "tower", "building_use": "office",
                "building_configuration": "podium_and_tower", "storeys_above": 12,
                "construction_year": 2022, "building_condition": "good",
                "premises_ids": ["SWPRE-0001"], "access_point_ids": ["SWACC-0001"],
            }],
            "premises": [{
                "premises_id": "SWPRE-0001", "property_id": "SWPROP-0001",
                "building_id": "SWBLD-0001", "address_id": "SWADDR-0001",
                "floor_name": "Ground Floor", "primary_function": "office",
                "unit_ids": ["SWUNIT-0001"],
            }],
            "units": [{
                "unit_id": "SWUNIT-0001", "property_id": "SWPROP-0001",
                "building_id": "SWBLD-0001", "premises_id": "SWPRE-0001",
                "address_id": "SWADDR-0001", "unit_locator": "G-01",
                "unit_class": "commercial", "primary_use": "office",
                "occupancy_state": "unassigned", "operator_business_id": "SWBIZ-000001",
            }],
            "access_points": [{
                "access_point_id": "SWACC-0001", "property_id": "SWPROP-0001",
                "building_id": "SWBLD-0001", "premises_id": "SWPRE-0001",
                "unit_id": "SWUNIT-0001", "access_type": "public_entrance",
                "access_modes": ["pedestrian"],
            }],
        }
        businesses = {
            "businesses": [{
                "business_id": "SWBIZ-000001", "registered_name": "Harbour Bank Limited",
                "trading_name": "Harbour Bank", "sector": "finance_insurance",
                "primary_activity": "banking_services", "legal_form": "public_company",
                "business_size": "large", "employee_band": "100-499",
                "status": "active", "parent_business_id": None,
                "primary_establishment_id": "SWEST-000001",
                "registered_address_id": "SWADDR-0001",
            }],
            "establishments": [{
                "establishment_id": "SWEST-000001", "business_id": "SWBIZ-000001",
                "establishment_name": "Harbour Bank", "establishment_type": "operating_business_site",
                "property_id": "SWPROP-0001", "building_id": "SWBLD-0001",
                "premises_id": "SWPRE-0001", "unit_id": "SWUNIT-0001",
                "address_id": "SWADDR-0001", "district_id": "DISTRICT-01",
                "neighbourhood_id": "NEIGHBOURHOOD-01", "floor_level": "G",
                "unit_locator": "G-01", "operating_status": "active",
                "customer_access": "public_front_door", "delivery_access": "rear_service_access",
            }],
        }
        self.archives = {
            "SW-PROPERTY-WORLD-V1": archive("SW-PROPERTY-WORLD-V1", world),
            "SW-BUSINESS-REGISTRY-V1": archive("SW-BUSINESS-REGISTRY-V1", businesses),
        }
        self.lookup = BP04Lookup(FakeConnection(self.archives))

    def test_identity_lookups_resolve_core_entity_types(self):
        self.assertEqual(self.lookup.get("property_id", "SWPROP-0001")["address_id"], "SWADDR-0001")
        self.assertEqual(self.lookup.get("address", "SWADDR-0001")["property_id"], "SWPROP-0001")
        self.assertEqual(self.lookup.get("building", "SWBLD-0001")["property_id"], "SWPROP-0001")
        self.assertEqual(self.lookup.get("premises", "SWPRE-0001")["building_id"], "SWBLD-0001")
        self.assertEqual(self.lookup.get("unit", "SWUNIT-0001")["premises_id"], "SWPRE-0001")
        self.assertEqual(self.lookup.get("business", "SWBIZ-000001")["sector"], "finance_insurance")
        self.assertEqual(self.lookup.get("establishment", "SWEST-000001")["unit_id"], "SWUNIT-0001")
        self.assertEqual(self.lookup.get("access_point", "SWACC-0001")["property_id"], "SWPROP-0001")

    def test_address_search_is_case_insensitive_and_partial(self):
        rows = self.lookup.search("address", "harbour avenue")
        self.assertEqual([row["address_id"] for row in rows], ["SWADDR-0001"])
        self.assertEqual(self.lookup.search("address", "SW-01 1AB")[0]["property_id"], "SWPROP-0001")

    def test_business_search_and_detail_resolve_address_and_property(self):
        rows = self.lookup.search("business", "HARBOUR BANK")
        self.assertEqual([row["business_id"] for row in rows], ["SWBIZ-000001"])
        detail = self.lookup.business_detail("SWBIZ-000001")
        self.assertEqual(detail["establishments"][0]["address"]["address_label"],
                         "10 Harbour Avenue, Central, Saltwater")
        self.assertEqual(detail["establishments"][0]["property"]["property_id"], "SWPROP-0001")

    def test_property_detail_resolves_address_building_and_operator(self):
        detail = self.lookup.property_detail("SWPROP-0001")
        self.assertEqual(detail["address"]["address_id"], "SWADDR-0001")
        self.assertEqual(detail["buildings"][0]["building_id"], "SWBLD-0001")
        self.assertEqual(detail["businesses"][0]["business_id"], "SWBIZ-000001")
        self.assertEqual(detail["geography_binding"], "bp02_design_identity_bound_operational_release_blocked")
        self.assertFalse(detail["operational_geography_approved"])
        self.assertTrue(detail["property"]["parcel_design_id"].startswith("SWP-"))

    def test_address_detail_returns_property_dossier(self):
        self.assertEqual(
            self.lookup.address_detail("SWADDR-0001")["property"]["property_id"],
            "SWPROP-0001",
        )

    def test_parcel_and_address_design_ids_resolve_without_operational_promotion(self):
        prop = self.lookup.get("property", "SWPROP-0001")
        address = self.lookup.get("address", "SWADDR-0001")
        parcel_id = prop["parcel_design_id"]
        address_id = address["address_design_id"]
        self.assertEqual(self.lookup.get("parcel", parcel_id)["property_id"], "SWPROP-0001")
        self.assertEqual(self.lookup.get("parcel_id", parcel_id)["parcel_identity_status"],
                         "STABLE_DESIGN_IDENTITY")
        self.assertEqual(self.lookup.get("address_design_id", address_id)["address_id"],
                         "SWADDR-0001")
        self.assertEqual(self.lookup.property_detail(parcel_id)["property"]["property_id"],
                         "SWPROP-0001")
        self.assertEqual(self.lookup.address_detail(address_id)["property"]["property_id"],
                         "SWPROP-0001")
        self.assertEqual(self.lookup.get("parcel", parcel_id)["parcel_operational_status"],
                         "NOT_APPROVED_FOR_OPERATIONAL_SEED")
        self.assertEqual(self.lookup.get("address", address_id)["address_operational_status"],
                         "NOT_APPROVED_FOR_OPERATIONAL_SEED")

    def test_search_matches_stable_parcel_and_address_design_ids(self):
        prop = self.lookup.get("property", "SWPROP-0001")
        address = self.lookup.get("address", "SWADDR-0001")
        self.assertEqual(self.lookup.search("property", prop["parcel_design_id"])[0]["property_id"],
                         "SWPROP-0001")
        self.assertEqual(self.lookup.search("address", address["address_design_id"])[0]["address_id"],
                         "SWADDR-0001")

    def test_missing_identity_returns_none(self):
        self.assertIsNone(self.lookup.get("property", "missing"))
        self.assertIsNone(self.lookup.property_detail("missing"))
        self.assertIsNone(self.lookup.business_detail("missing"))

    def test_search_rejects_unbounded_or_ambiguous_requests(self):
        with self.assertRaises(ValueError):
            self.lookup.search("address", "x")
        with self.assertRaises(ValueError):
            self.lookup.search("address", "harbour", 101)
        with self.assertRaises(ValueError):
            self.lookup.search("unit", "SWUNIT")

    def test_source_counts_are_reported(self):
        self.assertEqual(self.lookup.counts["SW-PROPERTY-WORLD-V1.properties"], 1)
        self.assertEqual(self.lookup.counts["SW-BUSINESS-REGISTRY-V1.businesses"], 1)

    def test_dangling_premises_building_link_fails_closed(self):
        world = tables_from_archive(self.archives["SW-PROPERTY-WORLD-V1"])
        world["premises"][0]["building_id"] = "SWBLD-MISSING"
        broken = dict(self.archives)
        broken["SW-PROPERTY-WORLD-V1"] = archive("SW-PROPERTY-WORLD-V1", world)
        with self.assertRaisesRegex(ValueError, "Premises .* references missing building"):
            BP04Lookup(FakeConnection(broken))

    def test_unit_parent_hierarchy_conflict_fails_closed(self):
        world = tables_from_archive(self.archives["SW-PROPERTY-WORLD-V1"])
        world["units"][0]["building_id"] = "SWBLD-OTHER"
        world["buildings"].append({
            **world["buildings"][0], "building_id": "SWBLD-OTHER",
            "property_id": "SWPROP-0001",
        })
        broken = dict(self.archives)
        broken["SW-PROPERTY-WORLD-V1"] = archive("SW-PROPERTY-WORLD-V1", world)
        with self.assertRaisesRegex(ValueError, "Unit .* premises hierarchy conflicts"):
            BP04Lookup(FakeConnection(broken))

    def test_access_point_unit_hierarchy_conflict_fails_closed(self):
        world = tables_from_archive(self.archives["SW-PROPERTY-WORLD-V1"])
        world["access_points"][0]["premises_id"] = "SWPRE-OTHER"
        world["premises"].append({
            **world["premises"][0], "premises_id": "SWPRE-OTHER",
        })
        broken = dict(self.archives)
        broken["SW-PROPERTY-WORLD-V1"] = archive("SW-PROPERTY-WORLD-V1", world)
        with self.assertRaisesRegex(ValueError, "Access point .* unit hierarchy conflicts"):
            BP04Lookup(FakeConnection(broken))

    def test_dangling_establishment_links_fail_closed(self):
        businesses = {
            "businesses": [{
                "business_id": "SWBIZ-000002", "registered_name": "Broken",
                "trading_name": "Broken", "sector": "other", "primary_activity": "other",
                "legal_form": "company", "business_size": "small", "employee_band": "5-19",
                "status": "active", "parent_business_id": None,
                "primary_establishment_id": "SWEST-000002", "registered_address_id": "SWADDR-0001",
            }],
            "establishments": [{
                "establishment_id": "SWEST-000002", "business_id": "SWBIZ-000002",
                "property_id": "SWPROP-MISSING", "building_id": None, "premises_id": None,
                "unit_id": None, "address_id": None,
            }],
        }
        broken = dict(self.archives)
        broken["SW-BUSINESS-REGISTRY-V1"] = archive("SW-BUSINESS-REGISTRY-V1", businesses)
        with self.assertRaisesRegex(ValueError, "references missing property"):
            BP04Lookup(FakeConnection(broken))


if __name__ == "__main__":
    unittest.main()
