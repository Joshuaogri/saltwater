import unittest

from runtime.bp04_property_stack_importer import rows, source_collection_key


class PropertyImporterSourceIdentityTests(unittest.TestCase):
    def test_rows_preserves_original_collection_name(self):
        document = {"tables": {"properties": {"columns": ["property_id"], "rows": [["SWP-001"]]}}}
        source_rows = rows(document, "properties")
        self.assertEqual(source_rows.collection_name, "properties")
        self.assertEqual(source_collection_key("SW-PROPERTY-WORLD-V1", source_rows, "property_site"),
                         "SW-PROPERTY-WORLD-V1.properties")

    def test_empty_source_collection_retains_identity(self):
        source_rows = rows({"tables": {}}, "capacity_findings")
        self.assertEqual(source_rows.collection_name, "capacity_findings")
        self.assertEqual(source_collection_key("SW-GLOBAL-ESTATE-CAPACITY-AUDIT-V1", source_rows, "audit"),
                         "SW-GLOBAL-ESTATE-CAPACITY-AUDIT-V1.capacity_findings")


if __name__ == "__main__":
    unittest.main()
