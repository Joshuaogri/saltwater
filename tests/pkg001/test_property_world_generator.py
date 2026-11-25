import json
import unittest
from pathlib import Path

from runtime.property_world_generator import build_property_world, to_columnar_document

ROOT = Path(__file__).resolve().parents[2]


class CanonicalPropertyWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())
        cls.world = build_property_world(source)

    def test_dataset_is_canonical_fictional_game_world(self):
        self.assertEqual(self.world["dataset_id"], "SW-PROPERTY-WORLD-V1")
        self.assertEqual(self.world["canon_status"], "CANONICAL_FICTIONAL_GAME_WORLD")
        self.assertTrue(self.world["lineage"]["fictional_world_facts"])

    def test_property_building_premises_unit_hierarchy_is_resolvable(self):
        w = self.world
        properties = {x["property_id"]: x for x in w["properties"]}
        buildings = {x["building_id"]: x for x in w["buildings"]}
        premises = {x["premises_id"]: x for x in w["premises"]}
        units = {x["unit_id"]: x for x in w["units"]}
        self.assertEqual(len(properties), len(w["properties"]))
        self.assertEqual(len(buildings), len(w["buildings"]))
        self.assertEqual(len(premises), len(w["premises"]))
        self.assertEqual(len(units), len(w["units"]))
        for b in buildings.values():
            self.assertIn(b["property_id"], properties)
            self.assertGreaterEqual(len(b["premises_ids"]), 1)
            for prem_id in b["premises_ids"]:
                self.assertIn(prem_id, premises)
                self.assertEqual(premises[prem_id]["building_id"], b["building_id"])
        for p in premises.values():
            self.assertIn(p["building_id"], buildings)
            self.assertGreaterEqual(len(p["unit_ids"]), 1)
            for unit_id in p["unit_ids"]:
                self.assertIn(unit_id, units)
                self.assertEqual(units[unit_id]["premises_id"], p["premises_id"])

    def test_every_property_has_address_and_ownership(self):
        w = self.world
        addresses = {x["address_id"]: x for x in w["addresses"]}
        owners = {x["organisation_id"] for x in w["owner_organisations"]}
        interests = {x["property_id"]: x for x in w["ownership_interests"]}
        self.assertEqual(len(addresses), len(w["properties"]))
        self.assertEqual(len(interests), len(w["properties"]))
        for p in w["properties"]:
            self.assertIn(p["address_id"], addresses)
            self.assertIn(p["property_id"], interests)
            self.assertIn(interests[p["property_id"]]["owner_organisation_id"], owners)
            self.assertTrue(addresses[p["address_id"]]["address_label"])

    def test_every_access_point_has_constructed_route_to_named_road(self):
        w = self.world
        routes = {x["access_point_id"]: x for x in w["access_routes"]}
        access_ids = {x["access_point_id"] for x in w["access_points"]}
        self.assertEqual(len(routes), len(w["access_routes"]))
        self.assertEqual(access_ids, set(routes))
        for a in w["access_points"]:
            route = routes[a["access_point_id"]]
            self.assertEqual(route["route_state"], "open")
            self.assertTrue(route["road_id"])
            self.assertTrue(route["road_segment_ids"])
            self.assertTrue(route["pedestrian_access"])
            self.assertTrue(route["emergency_access"])
            self.assertGreaterEqual(route["width_m"], 1.8)

    def test_access_points_are_linked_to_building_or_site(self):
        buildings = {x["building_id"] for x in self.world["buildings"]}
        properties = {x["property_id"] for x in self.world["properties"]}
        for a in self.world["access_points"]:
            self.assertIn(a["property_id"], properties)
            if a["building_id"] is not None:
                self.assertIn(a["building_id"], buildings)
            else:
                self.assertEqual(a["access_type"], "site_entrance_gate")

    def test_four_proximity_sites_receive_shared_access_spurs(self):
        spurs = [r for r in self.world["access_routes"] if r["route_type"] == "shared_access_spur"]
        self.assertGreaterEqual(len(spurs), 4)
        self.assertTrue(all(r["fictional_access_basis"] == "constructed_in_game_route" for r in spurs))

    def test_unit_occupancy_does_not_create_people(self):
        self.assertEqual(self.world["summary"]["population_created"], 0)
        self.assertEqual(self.world["summary"]["unassigned_resident_count"], 0)
        self.assertLessEqual(self.world["city_population_hard_cap"], 10000)
        self.assertTrue(all(not u["occupant_person_ids"] for u in self.world["units"]))

    def test_all_identifiers_are_unique_within_entity_type(self):
        groups = [
            self.world["properties"], self.world["addresses"], self.world["buildings"],
            self.world["premises"], self.world["units"], self.world["access_points"],
            self.world["access_routes"], self.world["site_features"],
            self.world["building_components"], self.world["premises_rooms"],
            self.world["ownership_interests"], self.world["owner_organisations"],
        ]
        fields = [
            "property_id","address_id","building_id","premises_id","unit_id",
            "access_point_id","route_id","site_feature_id","component_id",
            "room_id","ownership_interest_id","organisation_id",
        ]
        for rows, field in zip(groups, fields):
            values = [x[field] for x in rows]
            self.assertEqual(len(values), len(set(values)), field)

    def test_persisted_textual_dataset_is_valid_json_and_count_consistent(self):
        path = ROOT / "data/property/saltwater-property-world-v1.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(document["schema"], "saltwater-canonical-property-world-columnar/1.0")
        self.assertEqual(document["metadata"]["summary"]["property_count"], 420)
        self.assertEqual(len(document["tables"]["units"]["rows"]), self.world["summary"]["unit_count"])
        self.assertEqual(len(document["tables"]["access_routes"]["rows"]), 804)
        self.assertGreater(path.stat().st_size, 0)

    def test_textual_storage_format_is_columnar_and_lossless_for_counts(self):
        document = to_columnar_document(self.world)
        self.assertEqual(document["storage_format"], "textual_json_columnar_v1")
        self.assertEqual(document["record_schema"], "saltwater-canonical-property-world/1.0")
        self.assertEqual(len(document["tables"]["properties"]["rows"]), self.world["summary"]["property_count"])
        self.assertEqual(len(document["tables"]["units"]["rows"]), self.world["summary"]["unit_count"])
        self.assertIn("unit_id", document["tables"]["units"]["columns"])
        self.assertIn("occupant_person_ids", document["tables"]["units"]["columns"])

    def test_summary_counts_match_records(self):
        w = self.world
        self.assertEqual(w["summary"]["property_count"], len(w["properties"]))
        self.assertEqual(w["summary"]["building_count"], len(w["buildings"]))
        self.assertEqual(w["summary"]["premises_count"], len(w["premises"]))
        self.assertEqual(w["summary"]["unit_count"], len(w["units"]))
        self.assertEqual(w["summary"]["address_count"], len(w["addresses"]))
        self.assertEqual(w["summary"]["access_point_count"], len(w["access_points"]))
        self.assertEqual(w["summary"]["constructed_access_route_count"], len(w["access_routes"]))


if __name__ == "__main__":
    unittest.main()
