"""Integration check: resolve the real archive-only BP04 release from disposable PostgreSQL."""
import os
import unittest

import psycopg

from runtime.bp04_lookup import BP04Lookup


class BP04ArchiveLookupIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dsn = os.environ["DATABASE_URL"]
        cls.connection = psycopg.connect(dsn)
        cls.lookup = BP04Lookup(cls.connection)

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def test_real_archive_collection_counts_are_indexed(self):
        expected = {
            "SW-PROPERTY-WORLD-V1.properties": 420,
            "SW-PROPERTY-WORLD-V1.addresses": 420,
            "SW-PROPERTY-WORLD-V1.buildings": 1474,
            "SW-PROPERTY-WORLD-V1.premises": 27730,
            "SW-PROPERTY-WORLD-V1.units": 180733,
            "SW-PROPERTY-WORLD-V1.access_points": 2984,
            "SW-BUSINESS-REGISTRY-V1.businesses": 10000,
            "SW-BUSINESS-REGISTRY-V1.establishments": 10000,
        }
        for collection, count in expected.items():
            with self.subTest(collection=collection):
                self.assertEqual(self.lookup.counts[collection], count)

    def test_real_address_search_resolves_property_and_building_register(self):
        matches = self.lookup.search("address", "Saltwater", limit=5)
        self.assertEqual(len(matches), 5)
        detail = self.lookup.address_detail(matches[0]["address_id"])
        self.assertIsNotNone(detail)
        self.assertEqual(detail["property"]["property_id"], matches[0]["property_id"])
        self.assertIsNotNone(detail["address"])

    def test_real_business_search_resolves_establishment_and_location(self):
        matches = self.lookup.search("business", "SWBIZ", limit=5)
        self.assertEqual(len(matches), 5)
        detail = self.lookup.business_detail(matches[0]["business_id"])
        self.assertIsNotNone(detail)
        self.assertGreaterEqual(len(detail["establishments"]), 1)
        establishment = detail["establishments"][0]
        self.assertIsNotNone(establishment["property"])
        self.assertIsNotNone(establishment["address"])


if __name__ == "__main__":
    unittest.main()
