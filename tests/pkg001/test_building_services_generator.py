import json
import unittest
from pathlib import Path

from runtime.property_tenure_generator import _expand_columnar
from runtime.building_services_generator import build_building_services
from runtime.property_world_generator import to_columnar_document

ROOT = Path(__file__).resolve().parents[2]


class BuildingServicesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        world = _expand_columnar(json.loads((ROOT / "data/property/saltwater-property-world-v1.json").read_text()))
        tenure = _expand_columnar(json.loads((ROOT / "data/property/saltwater-property-tenure-v1.json").read_text()))
        cls.data = build_building_services(world, tenure)
        cls.world = world
        cls.tenure = tenure

    def test_every_property_has_four_utility_connections_and_accounts(self):
        d = self.data
        self.assertEqual(d["summary"]["utility_connection_count"], 420 * 4)
        self.assertEqual(d["summary"]["utility_account_count"], 420 * 4)
        self.assertEqual(len({x["utility_connection_id"] for x in d["utility_connections"]}), 1680)
        accounts = {x["utility_connection_id"] for x in d["utility_accounts"]}
        self.assertEqual(accounts, {x["utility_connection_id"] for x in d["utility_connections"]})

    def test_every_unit_has_electricity_and_water_submeters(self):
        d = self.data
        sub = [x for x in d["meters"] if x["meter_role"] == "unit_submeter"]
        self.assertEqual(len(sub), 15199 * 2)
        self.assertEqual(len({x["meter_id"] for x in sub}), len(sub))
        unit_ids = {u["unit_id"] for u in self.world["units"]}
        self.assertTrue(all(x["unit_id"] in unit_ids for x in sub))

    def test_building_systems_and_equipment_resolve(self):
        d = self.data
        building_ids = {x["building_id"] for x in self.world["buildings"]}
        system_ids = {x["building_system_id"] for x in d["building_systems"]}
        self.assertEqual(len(d["building_systems"]), len(system_ids))
        self.assertTrue(all(x["building_id"] in building_ids for x in d["building_systems"]))
        self.assertTrue(all(x["building_system_id"] in system_ids for x in d["equipment_assets"]))
        self.assertTrue(all(x["building_system_id"] in system_ids for x in d["system_inspections"]))

    def test_current_business_utility_responsibilities_resolve(self):
        d = self.data
        occupancy_ids = {x["occupancy_id"] for x in self.tenure["occupancies"]}
        self.assertEqual(len(d["business_utility_responsibilities"]), 10000)
        self.assertTrue(all(x["occupancy_id"] in occupancy_ids for x in d["business_utility_responsibilities"]))

    def test_provider_and_owner_relationships_resolve(self):
        d = self.data
        provider_ids = {x["organisation_id"] for x in d["utility_providers"]}
        owner_ids = {x["organisation_id"] for x in self.tenure["organisations"]}
        self.assertTrue(all(x["provider_organisation_id"] in provider_ids for x in d["utility_connections"]))
        self.assertTrue(all(x["account_holder_organisation_id"] in owner_ids for x in d["utility_accounts"]))

    def test_no_people_or_financial_postings_are_created(self):
        self.assertEqual(self.data["summary"]["person_records_created"], 0)
        self.assertEqual(self.data["summary"]["financial_postings_created"], 0)
        self.assertEqual(self.data["summary"]["population_records_created"], 0)

    def test_columnar_output_preserves_entity_counts(self):
        doc = to_columnar_document(self.data)
        doc["schema"] = "saltwater-building-services-columnar/1.0"
        self.assertEqual(doc["storage_format"], "textual_json_columnar_v1")
        self.assertEqual(len(doc["tables"]["meters"]["rows"]), len(self.data["meters"]))
        self.assertEqual(doc["metadata"]["summary"]["property_count"], 420)


if __name__ == "__main__":
    unittest.main()
