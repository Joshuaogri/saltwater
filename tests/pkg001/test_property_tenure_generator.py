import json
import unittest
from pathlib import Path

from runtime.property_tenure_generator import build_property_tenure, _expand_columnar
from runtime.dataset_io import load_json
from runtime.property_world_generator import to_columnar_document

ROOT = Path(__file__).resolve().parents[2]


class PropertyTenureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        world = _expand_columnar(load_json(ROOT / "data/property/saltwater-property-world-v1.json"))
        registry = _expand_columnar(load_json(ROOT / "data/business/saltwater-business-registry-v1.json"))
        cls.world = world
        cls.registry = registry
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
        self.assertEqual(len([x for x in d["occupancies"] if x["occupant_type"] == "business"]), 10000)
        self.assertEqual(len(d["occupancies"]), 10032)
        agreements = {x["agreement_id"]: x for x in d["agreements"]}
        for occ in d["occupancies"]:
            if occ["occupant_type"] != "business":
                continue
            self.assertIn(occ["agreement_id"], agreements)
            agreement = agreements[occ["agreement_id"]]
            self.assertEqual(agreement["unit_id"], occ["unit_id"])
            self.assertEqual(agreement["tenant_business_id"], occ["occupant_business_id"])

    def test_business_occupancies_follow_current_registry_unit_links(self):
        registry_links = {x["business_id"]: x["unit_id"] for x in self.registry["business_unit_links"]}
        occupancy_links = {x["occupant_business_id"]: x["unit_id"] for x in self.data["occupancies"] if x["occupant_type"] == "business"}
        self.assertEqual(occupancy_links, registry_links)

    def test_third_party_organisation_occupancy_matrix_covers_every_property(self):
        occupancies = {row["occupancy_id"]: row for row in self.data["occupancies"]}
        relationships = self.data["third_party_occupancy_relationships"]
        self.assertEqual(len(relationships), 32)
        self.assertEqual(len({row["relationship_id"] for row in relationships}), 32)
        self.assertEqual(len({row["unit_id"] for row in relationships}), 32)
        active_property_ids = {
            next(unit["property_id"] for unit in self.world["units"] if unit["unit_id"] == link["unit_id"])
            for link in self.registry["business_unit_links"]
        }
        self.assertEqual({row["property_id"] for row in relationships}, active_property_ids)
        unit_by_id = {unit["unit_id"]: unit for unit in self.world["units"]}
        self.assertEqual(
            {unit_by_id[row["unit_id"]]["unit_class"] for row in relationships},
            {unit_by_id[link["unit_id"]]["unit_class"] for link in self.registry["business_unit_links"]},
        )
        for relationship in relationships:
            occupancy = occupancies[relationship["occupancy_id"]]
            self.assertEqual(occupancy["occupant_type"], "organisation")
            self.assertEqual(occupancy["occupant_organisation_id"], relationship["receiving_organisation_id"])
            self.assertIsNotNone(relationship["granting_business_id"])
            self.assertIn(relationship["use_type"], {"service_provider", "contractor_access", "concession", "storage"})
            self.assertEqual(relationship["relationship_status"], "active")
            self.assertEqual(relationship["permission_status"], "not_required")

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


    def test_agreement_history_is_append_only_and_execution_dates_remain_unknown(self):
        d = self.data
        agreements = {x["agreement_id"]: x for x in d["agreements"]}
        events = d["agreement_event_history"]
        self.assertEqual(len(events), d["summary"]["agreement_event_count"])
        self.assertEqual(len({x["agreement_event_id"] for x in events}), len(events))
        self.assertEqual({x["agreement_id"] for x in events}, set(agreements))
        self.assertEqual(d["summary"]["agreement_execution_date_recorded_count"], 0)
        self.assertEqual(d["summary"]["agreement_execution_date_unknown_count"], len(agreements))
        self.assertTrue(all(x["execution_date"] is None and x["execution_date_status"] == "not_recorded" for x in events))
        for agreement in agreements.values():
            rows = [x for x in events if x["agreement_id"] == agreement["agreement_id"]]
            self.assertEqual(sum(x["event_type"] == "agreement_baseline_registered" for x in rows), 1)
            self.assertEqual(sum(x["event_type"] == "agreement_commenced" for x in rows), 1)
            self.assertEqual(sum(x["event_type"] == "agreement_expired" for x in rows), int(agreement["expiry_year"] is not None))

    def test_expiry_does_not_automatically_evict_or_vacate_current_occupant(self):
        d = self.data
        current_by_unit = {x["unit_id"]: x for x in d["occupancies"] if x["occupant_type"] == "business"}
        expired = [x for x in d["agreements"] if x["expiry_year"] is not None]
        self.assertTrue(expired)
        for old in expired:
            current = current_by_unit[old["unit_id"]]
            self.assertNotEqual(current["agreement_id"], old["agreement_id"])
            self.assertEqual(current["occupant_business_id"], old["tenant_business_id"])
            self.assertIsNone(current["effective_to_year"])
            self.assertIn(current["occupancy_status"], {"occupied", "seasonal_occupation", "temporarily_suspended_occupation"})

    def test_columnar_output_preserves_counts_and_references(self):
        doc = to_columnar_document(self.data)
        doc["schema"] = "saltwater-property-tenure-columnar/1.0"
        self.assertEqual(doc["storage_format"], "textual_json_columnar_v1")
        self.assertEqual(len(doc["tables"]["occupancies"]["rows"]), 10032)
        self.assertEqual(len(doc["tables"]["unit_occupancy_states"]["rows"]), len(self.data["unit_occupancy_states"]))
        self.assertEqual(doc["metadata"]["summary"]["ownership_event_count"], len(self.data["ownership_events"]))
        self.assertIn("agreement_event_history", doc["tables"])
        self.assertEqual(len(doc["tables"]["agreement_event_history"]["rows"]), len(self.data["agreement_event_history"]))
        self.assertEqual(len(doc["tables"]["agreement_event_history"]["rows"]), doc["metadata"]["summary"]["agreement_event_count"])


    def test_owner_manager_landlord_tenant_operator_and_occupant_roles_resolve_separately(self):
        from runtime.property_tenure_generator import audit_property_tenure_role_separation

        report = audit_property_tenure_role_separation(
            self.data, self.world, self.registry
        )
        self.assertTrue(report["valid"])
        self.assertEqual(report["properties_checked"], 420)
        self.assertEqual(report["ownership_interests_checked"], 420)
        self.assertEqual(report["management_appointments_checked"], 420)
        self.assertEqual(report["agreements_checked"], len(self.data["agreements"]))
        self.assertEqual(report["occupancies_checked"], 10032)
        self.assertEqual(report["primary_business_occupancies_checked"], 10000)
        self.assertEqual(report["third_party_occupancy_relationships_checked"], 32)
        self.assertGreater(report["third_party_management_count"], 0)
        self.assertGreater(report["direct_owner_management_count"], 0)
        self.assertEqual(report["person_records_created"], 0)

    def test_owner_and_independent_manager_roles_are_audited_by_unit_class(self):
        from runtime.property_tenure_generator import audit_property_tenure_role_separation

        report = audit_property_tenure_role_separation(
            self.data, self.world, self.registry
        )
        self.assertGreater(report["direct_owner_management_count"], 0)
        self.assertGreater(report["third_party_management_count"], 0)
        self.assertEqual(
            set(report["management_role_coverage_by_unit_class"]),
            {unit["unit_class"] for unit in self.world["units"]},
        )
        for unit_class, coverage in report["management_role_coverage_by_unit_class"].items():
            self.assertGreater(coverage["property_count"], 0, unit_class)
            self.assertGreater(
                coverage["direct_owner_management_count"] + coverage["third_party_management_count"],
                0,
                unit_class,
            )
            self.assertEqual(
                coverage["direct_owner_management_count"] + coverage["third_party_management_count"],
                coverage["property_count"],
            )

    def test_independent_operator_roles_cover_every_generated_unit_class(self):
        report = __import__(
            "runtime.property_tenure_generator", fromlist=["audit_property_tenure_role_separation"]
        ).audit_property_tenure_role_separation(self.data, self.world, self.registry)
        agreements = [a for a in self.data["agreements"] if a["expiry_year"] is None]
        business_by_id = {b["business_id"]: b for b in self.registry["businesses"]}
        establishment_by_id = {e["establishment_id"]: e for e in self.registry["establishments"]}
        unit_by_id = {u["unit_id"]: u for u in self.world["units"]}
        independent_classes = {
            unit_by_id[establishment_by_id[business_by_id[a["tenant_business_id"]]["primary_establishment_id"]]["unit_id"]]["unit_class"]
            for a in agreements if a["tenant_business_id"] != a["operator_business_id"]
        }
        all_classes = {
            unit_by_id[establishment_by_id[b["primary_establishment_id"]]["unit_id"]]["unit_class"]
            for b in self.registry["businesses"]
        }
        self.assertEqual(independent_classes, all_classes)
        self.assertGreater(report["independent_operator_agreement_count"], 0)
        self.assertGreater(report["same_tenant_operator_agreement_count"], 0)
        self.assertTrue(all(a["operator_business_id"] in business_by_id for a in agreements))

    def test_independent_landlords_resolve_through_title_holder_authority(self):
        from runtime.property_tenure_generator import audit_property_tenure_role_separation

        report = audit_property_tenure_role_separation(
            self.data, self.world, self.registry
        )
        self.assertGreater(report["letting_authorities_checked"], 0)
        self.assertEqual(
            report["letting_authorities_checked"],
            report["letting_authority_events_checked"],
        )
        self.assertGreater(report["independent_landlord_agreement_count"], 0)
        unit_by_id = {unit["unit_id"]: unit for unit in self.world["units"]}
        unit_classes = {
            unit_by_id[row["unit_id"]]["unit_class"]
            for row in self.data["agreements"]
            if row["expiry_year"] is None
        }
        self.assertEqual(
            set(report["independent_landlord_role_coverage_by_unit_class"]),
            unit_classes,
        )
        for unit_class, coverage in report["independent_landlord_role_coverage_by_unit_class"].items():
            self.assertGreater(coverage["agreement_count"], 0, unit_class)
        owners = {
            row["property_id"]: row["owner_organisation_id"]
            for row in self.data["current_ownership_interests"]
        }
        authorities = {
            row["letting_authority_id"]: row
            for row in self.data["letting_authorities"]
        }
        grants = {
            row["letting_authority_id"]
            for row in self.data["letting_authority_events"]
            if row["event_type"] == "authority_granted"
        }
        independent = [
            row for row in self.data["agreements"]
            if row.get("letting_authority_id") is not None
        ]
        for agreement in independent:
            authority = authorities[agreement["letting_authority_id"]]
            self.assertEqual(authority["property_id"], agreement["property_id"])
            self.assertEqual(authority["grantor_organisation_id"], owners[agreement["property_id"]])
            self.assertEqual(authority["grantee_organisation_id"], agreement["landlord_organisation_id"])
            self.assertIn(authority["letting_authority_id"], grants)
            self.assertGreaterEqual(agreement["commencement_year"], authority["effective_from_year"])

    def test_letting_authority_event_ids_are_stable_uuids(self):
        import uuid

        event_ids = [
            row["letting_authority_event_id"]
            for row in self.data["letting_authority_events"]
        ]
        self.assertEqual(len(event_ids), len(set(event_ids)))
        self.assertTrue(all(str(uuid.UUID(value)) == value for value in event_ids))
        self.assertTrue(all("letting_authority_id" in row for row in self.data["agreements"]))

    def test_non_owner_landlord_without_authority_fails_role_audit(self):
        from runtime.property_tenure_generator import audit_property_tenure_role_separation

        tenure = json.loads(json.dumps(self.data))
        agreement = next(
            row for row in tenure["agreements"]
            if row.get("letting_authority_id") is not None
        )
        agreement["letting_authority_id"] = None
        with self.assertRaisesRegex(ValueError, "lacks matching title-holder letting authority"):
            audit_property_tenure_role_separation(tenure, self.world, self.registry)

    def test_head_lessee_authority_must_match_title_holder_grantor(self):
        from runtime.property_tenure_generator import audit_property_tenure_role_separation

        tenure = json.loads(json.dumps(self.data))
        tenure["letting_authorities"][0]["grantor_organisation_id"] = "not-the-title-holder"
        with self.assertRaisesRegex(ValueError, "letting authority"):
            audit_property_tenure_role_separation(tenure, self.world, self.registry)

    def test_head_lessee_authority_must_match_unit_scope(self):
        from runtime.property_tenure_generator import audit_property_tenure_role_separation

        tenure = json.loads(json.dumps(self.data))
        agreement = next(row for row in tenure["agreements"] if row.get("letting_authority_id"))
        authority = next(
            row for row in tenure["letting_authorities"]
            if row["letting_authority_id"] == agreement["letting_authority_id"]
        )
        authority["unit_id"] = "SWUNIT-NOT-IN-SCOPE"
        with self.assertRaisesRegex(ValueError, "lacks matching title-holder letting authority"):
            audit_property_tenure_role_separation(tenure, self.world, self.registry)

    def test_letting_authority_requires_one_matching_grant_event(self):
        from runtime.property_tenure_generator import audit_property_tenure_role_separation

        tenure = json.loads(json.dumps(self.data))
        tenure["letting_authority_events"][0]["effective_year"] -= 1
        with self.assertRaisesRegex(ValueError, "grant event does not match its effective date"):
            audit_property_tenure_role_separation(tenure, self.world, self.registry)

    def test_duplicate_letting_authority_event_idempotency_is_rejected(self):
        from runtime.property_tenure_generator import audit_property_tenure_role_separation

        tenure = json.loads(json.dumps(self.data))
        duplicate = json.loads(json.dumps(tenure["letting_authority_events"][0]))
        duplicate["letting_authority_event_id"] = "00000000-0000-0000-0000-000000000001"
        tenure["letting_authority_events"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "identities and idempotency keys must be unique"):
            audit_property_tenure_role_separation(tenure, self.world, self.registry)

    def test_tenant_cannot_be_resolved_through_organisation_register(self):
        from runtime.property_tenure_generator import audit_property_tenure_role_separation

        tenure = json.loads(json.dumps(self.data))
        tenure["agreements"][0]["tenant_business_id"] = tenure["organisations"][0]["organisation_id"]
        with self.assertRaisesRegex(ValueError, "tenant/operator role"):
            audit_property_tenure_role_separation(tenure, self.world, self.registry)

    def test_manager_cannot_be_resolved_through_business_register(self):
        from runtime.property_tenure_generator import audit_property_tenure_role_separation

        tenure = json.loads(json.dumps(self.data))
        tenure["management_appointments"][0]["manager_organisation_id"] = (
            self.registry["businesses"][0]["business_id"]
        )
        with self.assertRaisesRegex(ValueError, "manager role"):
            audit_property_tenure_role_separation(tenure, self.world, self.registry)

    def test_occupant_must_match_explicit_tenant_and_establishment(self):
        from runtime.property_tenure_generator import audit_property_tenure_role_separation

        tenure = json.loads(json.dumps(self.data))
        tenure["occupancies"][0]["occupant_business_id"] = self.registry["businesses"][1]["business_id"]
        with self.assertRaisesRegex(ValueError, "occupant role"):
            audit_property_tenure_role_separation(tenure, self.world, self.registry)


if __name__ == "__main__":
    unittest.main()
