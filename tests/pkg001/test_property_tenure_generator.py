import json
import unittest
from pathlib import Path

from runtime.property_tenure_generator import build_property_tenure, _expand_columnar
from runtime.property_world_generator import to_columnar_document

ROOT = Path(__file__).resolve().parents[2]


class PropertyTenureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        world = _expand_columnar(json.loads((ROOT / "data/property/saltwater-property-world-v1.json").read_text()))
        registry = _expand_columnar(json.loads((ROOT / "data/business/saltwater-business-registry-v1.json").read_text()))
        cls.world = world
        cls.data = build_property_tenure({}, property_world=world, registry=registry)

    def test_every_property_has_current_owner_and_chronology(self):
        d = self.data
        current = {x["property_id"]: x["owner_organisation_id"] for x in d["current_ownership_interests"]}
        self.assertEqual(len(current), 420)
        self.assertEqual({x["property_id"] for x in d["ownership_events"]}, set(current))
        for pid in current:
            events = sorted((x for x in d["ownership_events"] if x["property_id"] == pid),
                            key=lambda x: x["effective_year"])
            self.assertEqual(events[-1]["to_organisation_id"], current[pid])
            self.assertEqual(len(events), len({x["ownership_event_id"] for x in events}))

    def test_all_businesses_have_current_agreement_and_occupancy(self):
        d = self.data
        self.assertEqual(d["summary"]["current_lease_or_concession_count"], 10000)
        self.assertEqual(len(d["occupancies"]), 10000)
        agreements = {x["agreement_id"]: x for x in d["agreements"]}
        for occ in d["occupancies"]:
            self.assertIn(occ["agreement_id"], agreements)
            agreement = agreements[occ["agreement_id"]]
            self.assertEqual(agreement["unit_id"], occ["unit_id"])
            self.assertEqual(agreement["tenant_business_id"], occ["occupant_business_id"])

    def test_all_occupancy_references_resolve(self):
        d = self.data
        unit_states = d["unit_occupancy_states"]
        self.assertEqual(len(unit_states), len(self.world["units"]))
        self.assertEqual(len({x["unit_id"] for x in unit_states}), len(unit_states))
        self.assertTrue(all(not x["person_ids"] for x in unit_states))
        self.assertEqual(d["summary"]["person_records_created"], 0)

    def test_management_appointments_have_resolvable_organisations(self):
        d = self.data
        orgs = {x["organisation_id"] for x in d["organisations"]}
        self.assertEqual(len(d["management_appointments"]), 420)
        self.assertTrue(all(x["manager_organisation_id"] in orgs for x in d["management_appointments"]))

    def test_historical_agreements_do_not_overlap_current_start(self):
        by_unit = {}
        for agreement in self.data["agreements"]:
            by_unit.setdefault(agreement["unit_id"], []).append(agreement)
        for rows in by_unit.values():
            current = [x for x in rows if x["expiry_year"] is None]
            history = [x for x in rows if x["expiry_year"] is not None]
            for old in history:
                self.assertLess(old["expiry_year"], current[0]["commencement_year"])

    def test_columnar_output_preserves_counts_and_references(self):
        doc = to_columnar_document(self.data)
        doc["schema"] = "saltwater-property-tenure-columnar/1.0"
        self.assertEqual(doc["storage_format"], "textual_json_columnar_v1")
        self.assertEqual(len(doc["tables"]["occupancies"]["rows"]), 10000)
        self.assertEqual(len(doc["tables"]["unit_occupancy_states"]["rows"]), len(self.data["unit_occupancy_states"]))
        self.assertEqual(doc["metadata"]["summary"]["ownership_event_count"], len(self.data["ownership_events"]))


if __name__ == "__main__":
    unittest.main()
