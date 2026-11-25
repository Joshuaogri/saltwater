import unittest
from pathlib import Path
from runtime.dataset_io import load_json
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_development_control_generator import build_development_control
ROOT=Path(__file__).resolve().parents[2]
def load(p): return _expand_columnar(load_json(ROOT/p))
class PropertyDevelopmentControlTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  def get(p): return load(p)
  cls.world=get("data/property/saltwater-property-world-v1.json")
  cls.tenure=get("data/property/saltwater-property-tenure-v1.json")
  cls.services=get("data/property/saltwater-building-services-v1.json")
  cls.maintenance=get("data/property/saltwater-property-maintenance-v1.json")
  cls.valuation=get("data/property/saltwater-property-value-risk-tax-v1.json")
  cls.data=build_development_control(cls.world,cls.tenure,cls.services,cls.maintenance,cls.valuation)
 def test_every_site_and_building_has_development_control(self):
  d=self.data
  self.assertEqual({x["property_id"] for x in self.world["properties"]},{x["property_id"] for x in d["site_development_plans"]})
  self.assertEqual({x["building_id"] for x in self.world["buildings"]},{x["building_id"] for x in d["planning_permissions"]})
  self.assertEqual({x["building_id"] for x in self.world["buildings"]},{x["building_id"] for x in d["building_control_cases"]})
 def test_certificates_and_lawful_use_cover_all_assets(self):
  d=self.data
  self.assertEqual({x["building_id"] for x in self.world["buildings"]},{x["building_id"] for x in d["completion_certificates"]})
  self.assertEqual({x["premises_id"] for x in self.world["premises"]},{x["premises_id"] for x in d["lawful_use_certificates"]})
  self.assertEqual({x["unit_id"] for x in self.world["units"]},{x["unit_id"] for x in d["unit_use_compliance"]})
  self.assertEqual(len(d["unit_use_compliance"]),len(self.world["units"]))
  self.assertEqual(len({x["unit_id"] for x in d["unit_use_compliance"]}),len(d["unit_use_compliance"]))
  self.assertEqual(d["summary"]["unit_use_compliance_count"],len(self.world["units"]))
 def test_all_generated_identifiers_are_unique(self):
  for collection,field in (("site_development_plans","site_development_plan_id"),("planning_permissions","planning_permission_id"),("building_control_cases","building_control_case_id"),("building_inspection_schedules","building_inspection_schedule_id"),("completion_certificates","completion_certificate_id"),("lawful_use_certificates","lawful_use_certificate_id"),("unit_use_compliance","use_compliance_id"),("development_projects","development_project_id")):
   values=[x[field] for x in self.data[collection]]
   self.assertEqual(len(values),len(set(values)),f"{collection} contains colliding IDs")

 def test_all_references_resolve(self):
  d=self.data
  permissions={x["planning_permission_id"] for x in d["planning_permissions"]}
  cases={x["building_control_case_id"] for x in d["building_control_cases"]}
  certs={x["completion_certificate_id"] for x in d["completion_certificates"]}
  self.assertTrue(all(x["planning_permission_id"] in permissions for x in d["building_control_cases"]))
  self.assertTrue(all(x["building_control_case_id"] in cases for x in d["completion_certificates"]))
  self.assertTrue(all(x["completion_certificate_id"] in certs for x in d["lawful_use_certificates"]))
 def test_inspection_schedules_do_not_claim_visits(self):
  self.assertTrue(all(x["inspection_status"]=="scheduled_not_completed" and x["inspection_visit_created"] is False for x in self.data["building_inspection_schedules"]))
 def test_applications_and_started_projects_not_fabricated(self):
  s=self.data["summary"]
  self.assertEqual(s["planning_application_count"],0)
  self.assertEqual(s["construction_projects_started"],0)
  self.assertTrue(all(x["project_status"]=="approved_preconstruction" and not x["construction_activity_started"] for x in self.data["development_projects"]))
 def test_no_person_or_financial_records(self):
  s=self.data["summary"]
  for k in ("financial_commitments_created","invoices_created","person_records_created","population_records_created"): self.assertEqual(s[k],0)
 def test_deterministic(self):
  again=build_development_control(self.world,self.tenure,self.services,self.maintenance,self.valuation)
  self.assertEqual(self.data["manifest_sha256"],again["manifest_sha256"])
if __name__=="__main__": unittest.main()
