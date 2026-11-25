import json
import unittest
from pathlib import Path

from runtime.business_registry_generator import build_business_registry

ROOT = Path(__file__).resolve().parents[2]


class BusinessRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())
        cls.registry = build_business_registry(source)

    def test_registry_meets_ten_thousand_distinct_business_invariant(self):
        rows = self.registry["businesses"]
        ids = [x["business_id"] for x in rows]
        names = [x["registered_name"] for x in rows]
        self.assertEqual(len(rows), 10000)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(self.registry["summary"]["distinct_business_count"], 10000)

    def test_every_business_has_one_establishment_and_unit_link(self):
        r = self.registry
        businesses = {x["business_id"] for x in r["businesses"]}
        establishments = {x["establishment_id"]: x for x in r["establishments"]}
        links = {x["business_id"]: x for x in r["business_unit_links"]}
        self.assertEqual(len(establishments), 10000)
        self.assertEqual(len(links), 10000)
        for b in r["businesses"]:
            self.assertIn(b["primary_establishment_id"], establishments)
            self.assertIn(b["business_id"], links)
            self.assertEqual(establishments[b["primary_establishment_id"]]["business_id"], b["business_id"])

    def test_establishments_resolve_full_property_hierarchy(self):
        property_world = __import__("runtime.property_world_generator", fromlist=["build_property_world"]).build_property_world(
            json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())
        )
        props = {x["property_id"] for x in property_world["properties"]}
        buildings = {x["building_id"] for x in property_world["buildings"]}
        premises = {x["premises_id"] for x in property_world["premises"]}
        units = {x["unit_id"] for x in property_world["units"]}
        addresses = {x["address_id"] for x in property_world["addresses"]}
        for e in self.registry["establishments"]:
            self.assertIn(e["property_id"], props)
            self.assertIn(e["building_id"], buildings)
            self.assertIn(e["premises_id"], premises)
            self.assertIn(e["unit_id"], units)
            self.assertIn(e["address_id"], addresses)

    def test_sector_allocation_is_complete_and_balanced(self):
        expected = {sector: count for sector, count, _ in __import__("runtime.business_registry_generator", fromlist=["SECTORS"]).SECTORS}
        self.assertEqual(self.registry["summary"]["businesses_by_sector"], expected)
        self.assertEqual(sum(expected.values()), 10000)

    def test_no_people_or_population_are_created(self):
        summary = self.registry["summary"]
        self.assertEqual(summary["population_records_created"], 0)
        self.assertEqual(summary["staff_person_records_created"], 0)
        self.assertEqual(self.registry["city_population_hard_cap"], 10000)
        self.assertTrue(all(x["person_records_created"] == 0 for x in self.registry["businesses"]))

    def test_persisted_business_registry_is_valid_columnar_json(self):
        path = ROOT / "data/business/saltwater-business-registry-v1.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(document["schema"], "saltwater-canonical-property-world-columnar/1.0")
        self.assertEqual(document["metadata"]["summary"]["distinct_business_count"], 10000)
        self.assertEqual(len(document["tables"]["businesses"]["rows"]), 10000)
        self.assertEqual(len(document["tables"]["establishments"]["rows"]), 10000)


if __name__ == "__main__":
    unittest.main()
