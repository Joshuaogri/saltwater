import unittest

from runtime.bp02_no_building_site_reconciliation import (
    reconcile_no_building_sites_and_frontage_exceptions,
)


class BP02NoBuildingSiteCrossRegisterTests(unittest.TestCase):
    def setUp(self):
        self.review = {
            "address_count": 3,
            "records": [
                {
                    "source_address_id": "ADDR-1", "source_property_id": "PROP-1",
                    "source_candidate_parcel_id": "PARCEL-1", "source_road_id": "ROAD-1",
                    "building_access_status": "NO_BUILDING_ON_PROPERTY_SITE",
                    "review_class": "ROAD_REFERENCE_CONFLICT", "review_priority": "P1",
                },
                {
                    "source_address_id": "ADDR-2", "source_property_id": "PROP-2",
                    "source_candidate_parcel_id": "PARCEL-2", "source_road_id": "ROAD-2",
                    "building_access_status": "NO_BUILDING_ON_PROPERTY_SITE",
                    "review_class": "NO_BUILDING_ON_PROPERTY_SITE", "review_priority": "P2",
                },
                {
                    "source_address_id": "ADDR-3", "source_property_id": "PROP-3",
                    "source_candidate_parcel_id": "PARCEL-3", "source_road_id": "BRIDGE-1",
                    "building_access_status": "SOURCE_ROAD_MATCHES_BUILDING_ACCESS_SET",
                    "review_class": "NO_PARCEL_FRONTAGE_EVIDENCE", "review_priority": "P1",
                },
            ],
        }
        self.exceptions = {
            "exception_count": 2,
            "records": [
                {
                    "source_address_id": "ADDR-1", "property_id": "PROP-1",
                    "source_candidate_parcel_id": "PARCEL-1", "source_road_id": "ROAD-1",
                    "geometry_disposition": "UNIQUE_PARCEL_FRONTAGE_ROAD_ASSOCIATION_RESOLVED",
                },
                {
                    "source_address_id": "ADDR-3", "property_id": "PROP-3",
                    "source_candidate_parcel_id": "PARCEL-3", "source_road_id": "BRIDGE-1",
                    "geometry_disposition": "BRIDGE_ACCESS_CONNECTOR_CANDIDATE_TO_CONNECTED_PUBLIC_ROAD_NETWORK",
                },
            ],
        }

    def build(self):
        return reconcile_no_building_sites_and_frontage_exceptions(
            self.review, self.exceptions
        )

    def test_counts_no_building_population_independently_of_primary_review_class(self):
        result = self.build()
        self.assertEqual(result["no_building_site_count"], 2)
        self.assertEqual(result["no_building_property_count"], 2)
        self.assertEqual(result["no_building_review_class_counts"], {
            "NO_BUILDING_ON_PROPERTY_SITE": 1,
            "ROAD_REFERENCE_CONFLICT": 1,
        })
        self.assertEqual(result["frontage_exceptions_on_no_building_sites"], 1)
        self.assertEqual(result["frontage_exceptions_on_sites_with_building_candidates"], 1)

    def test_preserves_explicit_property_identity_in_exception_crosswalk(self):
        result = self.build()
        bridge = result["frontage_exception_crosswalk"][1]
        self.assertEqual(bridge["property_id"], "PROP-3")
        self.assertFalse(bridge["no_building_site"])

    def test_mismatched_property_or_parcel_identity_fails_closed(self):
        broken = {
            "exception_count": 2,
            "records": [dict(self.exceptions["records"][0], property_id="WRONG")] +
                       self.exceptions["records"][1:],
        }
        with self.assertRaisesRegex(ValueError, "identity/provenance differs"):
            reconcile_no_building_sites_and_frontage_exceptions(self.review, broken)

    def test_duplicate_property_in_no_building_population_fails_closed(self):
        broken = dict(self.review)
        broken["records"] = self.review["records"] + [
            dict(self.review["records"][1], source_address_id="ADDR-4")
        ]
        broken["address_count"] = 4
        with self.assertRaisesRegex(ValueError, "Duplicate review property identity"):
            reconcile_no_building_sites_and_frontage_exceptions(broken, self.exceptions)

    def test_missing_exception_review_link_fails_closed(self):
        broken = {
            "exception_count": 1,
            "records": [dict(self.exceptions["records"][0], source_address_id="UNKNOWN")],
        }
        with self.assertRaisesRegex(ValueError, "no address review row"):
            reconcile_no_building_sites_and_frontage_exceptions(self.review, broken)

    def test_repeat_build_is_deterministic_and_read_only(self):
        first, second = self.build(), self.build()
        self.assertEqual(first, second)
        self.assertFalse(first["database_write_performed"])
        self.assertFalse(first["operational_approval"])


if __name__ == "__main__":
    unittest.main()
