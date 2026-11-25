import json,unittest
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_rights_boundaries_generator import build_property_rights
ROOT=Path(__file__).resolve().parents[2]
def load(p): return _expand_columnar(json.loads((ROOT/p).read_text()))
class PropertyRightsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.world=load("data/property/saltwater-property-world-v1.json")
  cls.tenure=load("data/property/saltwater-property-tenure-v1.json")
  cls.lifecycle=load("data/property/saltwater-property-lifecycle-transactions-v1.json")
  cls.services=load("data/property/saltwater-building-services-v1.json")
  cls.security=load("data/property/saltwater-property-security-access-v1.json")
  cls.data=build_property_rights(cls.world,cls.tenure,cls.lifecycle,cls.services,cls.security)
 def test_every_property_has_rights_and_boundary_schedule(self):
  d=self.data; ids={x["property_id"] for x in self.world["properties"]}
  self.assertEqual(ids,{x["property_id"] for x in d["property_rights_schedules"]})
  self.assertEqual(ids,{x["property_id"] for x in d["boundary_evidence_register"]})
 def test_contractual_rights_exactly_index_existing_agreements(self):
  d=self.data; src={x["agreement_id"]:x for x in self.tenure["agreements"]}
  idx={x["source_agreement_id"]:x for x in d["contractual_rights_index"]}
  self.assertEqual(set(src),set(idx)); self.assertEqual(len(idx),len(d["contractual_rights_index"]))
  for aid,row in idx.items():
   self.assertEqual(row["unit_id"],src[aid]["unit_id"])
   self.assertEqual(row["property_id"],src[aid]["property_id"])
   self.assertFalse(row["new_legal_instrument_created"])
 def test_boundary_evidence_is_not_misrepresented_as_survey(self):
  self.assertTrue(all(x["survey_status"]=="not_survey_grade" for x in self.data["boundary_evidence_register"]))
  self.assertTrue(all(x["legal_boundary_status"]=="not_independently_verified" for x in self.data["boundary_evidence_register"]))
 def test_physical_access_never_implies_legal_right(self):
  rows=self.data["physical_access_evidence_register"]
  self.assertTrue(rows)
  self.assertTrue(all(x["legal_right_of_way_status"]=="not_asserted" for x in rows))
  self.assertTrue(all(x["frontage_or_proximity_is_not_legal_access"] for x in rows))
 def test_utility_connection_never_implies_wayleave(self):
  rows=self.data["utility_wayleave_requirements"]
  self.assertTrue(rows)
  self.assertTrue(all(x["legal_route_right_status"]=="not_evidenced" for x in rows))
  self.assertTrue(all(x["operational_connection_is_not_proof_of_property_right"] for x in rows))
 def test_no_unsubstantiated_instruments_are_created(self):
  s=self.data["summary"]
  self.assertEqual(len(self.data["registered_instrument_register"]),0)
  for k in ("registered_easement_count","registered_wayleave_count","registered_mortgage_or_charge_count","registered_covenant_count","registered_lien_or_caveat_count","boundary_dispute_count","new_legal_instruments_created","legal_access_inferences_created","person_records_created","financial_postings_created"): self.assertEqual(s[k],0)
 def test_instrument_templates_have_evidence_requirements(self):
  self.assertEqual(len(self.data["future_instrument_templates"]),9)
  self.assertTrue(all(x["minimum_evidence"] for x in self.data["future_instrument_templates"]))
 def test_deterministic(self):
  other=build_property_rights(self.world,self.tenure,self.lifecycle,self.services,self.security)
  self.assertEqual(self.data["manifest_sha256"],other["manifest_sha256"])
if __name__=="__main__":unittest.main()
