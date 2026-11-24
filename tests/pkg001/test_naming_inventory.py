import json
import unittest
from pathlib import Path

from runtime.naming_inventory import inventory_geography_names


class GeographyNameInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload = json.loads(
            Path("data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8")
        )
        cls.report = inventory_geography_names(payload)

    def test_inventory_covers_adopted_map_name_groups(self):
        self.assertEqual(self.report.dataset_id, "SW-GEO-V1")
        self.assertEqual(len(self.report.candidates), 102)
        kinds = {}
        for candidate in self.report.candidates:
            kinds[candidate.source_ref.rsplit(":", 1)[-1]] = (
                kinds.get(candidate.source_ref.rsplit(":", 1)[-1], 0) + 1
            )
        self.assertEqual(kinds["district"], 8)
        self.assertEqual(kinds["neighbourhood"], 24)
        self.assertEqual(kinds["road"], 42)
        self.assertEqual(kinds["route"], 5)

    def test_approved_saltwater_root_pair_is_not_reported_as_a_collision(self):
        self.assertNotIn("saltwater", {item.normalized_key for item in self.report.conflicts})
        roots = [x for x in self.report.candidates if x.display_name == "Saltwater"]
        self.assertEqual({x.source_id for x in roots}, {"saltwater-state", "saltwater-city"})

    def test_existing_map_name_collisions_are_reported_not_silently_renamed(self):
        conflicts = {item.normalized_key: item for item in self.report.conflicts}
        self.assertIn("westgate", conflicts)
        self.assertEqual(len(conflicts["westgate"].candidates), 2)

    def test_import_is_blocked_until_map_baseline_and_spatial_ids_are_resolved(self):
        self.assertFalse(self.report.can_import)
        self.assertEqual(self.report.source_status, "DESIGN_BASELINE_NOT_YET_USER_APPROVED_FOR_OPERATIONAL_SEED")
        self.assertEqual(len(self.report.unresolved_spatial_ids), 100)


if __name__ == "__main__":
    unittest.main()
