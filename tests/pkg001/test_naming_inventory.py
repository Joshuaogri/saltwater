import json
import unittest
from pathlib import Path

from runtime.naming_inventory import build_spatial_identity_map, inventory_geography_names


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

    def test_user_approved_neighbourhood_renames_resolve_global_name_collisions(self):
        conflicts = {item.normalized_key: item for item in self.report.conflicts}
        self.assertNotIn("westgate", conflicts)
        self.assertNotIn("government square", conflicts)
        names_by_id = {item.source_id: item.display_name for item in self.report.candidates}
        self.assertEqual(names_by_id["SW-D01"], "Westgate")
        self.assertEqual(names_by_id["SW-D01-N1"], "Westgate Gardens")
        self.assertEqual(names_by_id["SW-D03-N2"], "Civic Terrace")
        self.assertEqual(names_by_id["SW-POI-002"], "Government Square")

    def test_import_is_blocked_until_map_baseline_and_spatial_ids_are_resolved(self):
        self.assertFalse(self.report.can_import)
        self.assertEqual(self.report.source_status, "DESIGN_BASELINE_NOT_YET_USER_APPROVED_FOR_OPERATIONAL_SEED")
        self.assertEqual(len(self.report.unresolved_spatial_ids), 100)


    def test_stable_spatial_identity_map_covers_all_unresolved_source_ids(self):
        payload = json.loads(
            Path("data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8")
        )
        identity_map = build_spatial_identity_map(payload)
        self.assertEqual(len(identity_map.entries), 100)
        self.assertFalse(identity_map.operational_seed_approved)
        self.assertEqual(
            {row.source_id for row in identity_map.entries},
            set(self.report.unresolved_spatial_ids),
        )
        self.assertEqual(
            {row.entity_code for row in identity_map.entries},
            {row.source_id for row in identity_map.entries},
        )
        self.assertTrue(all(row.spatial_id is None for row in identity_map.entries))
        parent_codes = {row.entity_code for row in identity_map.entries} | {
            "saltwater-state", "saltwater-city"
        }
        self.assertTrue(all(row.parent_entity_code in parent_codes for row in identity_map.entries))

    def test_stable_spatial_identity_map_has_expected_domain_kinds(self):
        payload = json.loads(
            Path("data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8")
        )
        identity_map = build_spatial_identity_map(payload)
        counts = {}
        for row in identity_map.entries:
            counts[row.entity_type] = counts.get(row.entity_type, 0) + 1
        self.assertEqual(counts, {
            "DISTRICT": 8,
            "NEIGHBOURHOOD": 24,
            "ROAD": 42,
            "ROUTE": 5,
            "GEO_ZONE": 3,
            "LANDMARK": 18,
        })

    def test_committed_identity_map_manifest_matches_builder_output(self):
        source = json.loads(
            Path("data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8")
        )
        manifest = json.loads(
            Path("data/geography/saltwater-geography-v1-identity-map.json").read_text(encoding="utf-8")
        )
        built = build_spatial_identity_map(source)
        self.assertEqual(manifest["schema"], "saltwater-spatial-identity-map/1.0")
        self.assertEqual(manifest["dataset_id"], built.dataset_id)
        self.assertEqual(manifest["source_dataset_status"], built.source_status)
        self.assertEqual(manifest["source_dataset_git_blob_sha"], "27b3f7848af10f2d61dee04a4dada1eff1f9871b")
        self.assertNotIn("source_dataset_sha", manifest)
        self.assertEqual(manifest["mapping_status"], "DISPOSABLE_MAPPING_CANDIDATE_ONLY")
        self.assertFalse(manifest["operational_seed_approved"])
        expected = [
            {
                "source_id": row.source_id,
                "entity_code": row.entity_code,
                "entity_type": row.entity_type,
                "entity_kind": row.entity_kind,
                "display_name": row.display_name,
                "parent_entity_code": row.parent_entity_code,
                "source_ref": row.source_ref,
                "spatial_id": None,
            }
            for row in built.entries
        ]
        self.assertEqual(manifest["entries"], expected)

    def test_stable_spatial_identity_map_is_deterministic_and_preserves_neighbourhood_parent(self):
        payload = json.loads(
            Path("data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8")
        )
        first = build_spatial_identity_map(payload)
        second = build_spatial_identity_map(payload)
        self.assertEqual(first, second)
        by_id = {row.source_id: row for row in first.entries}
        self.assertEqual(by_id["SW-D01-N1"].parent_entity_code, "SW-D01")
        self.assertEqual(by_id["SW-D03-N2"].parent_entity_code, "SW-D03")


if __name__ == "__main__":
    unittest.main()
