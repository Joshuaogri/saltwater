import copy
import json
import unittest
from pathlib import Path

from runtime.terrain_obstacle_source_model import build_source_inventory
from runtime.terrain_obstacle_evidence_register import build_evidence_register


class TerrainObstacleEvidenceRegisterTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[2] / "data/geography/saltwater-geography-v1.json"
        raw = path.read_bytes()
        self.source = json.loads(raw)
        self.inventory = build_source_inventory(self.source, raw)
        self.now = "2026-11-25T08:00:00Z"
        self.evidence = {
            "evidence_id": "SWEV-TEST-001",
            "subject_id": self.inventory["records"][0]["source_feature_id"],
            "subject_type": self.inventory["records"][0]["source_entity_type"],
            "evidence_type": "field_observation",
            "captured_at": self.now,
            "submitted_at": self.now,
            "actor_ref": "NPC-SURVEYOR-001",
            "source_ref": "fictional-field-notebook:page-1",
            "source_sha256": "a" * 64,
            "collection_method": "documented synthetic test observation",
            "measurements": {"condition": "reported_not_independently_verified"},
            "uncertainty": {"statement": "test fixture only"},
            "attachment_sha256": ["b" * 64],
        }

    def test_empty_register_does_not_invent_observations(self):
        report = build_evidence_register(self.inventory)
        self.assertEqual(report["summary"]["evidence_record_count"], 0)
        self.assertEqual(report["summary"]["review_event_count"], 0)
        self.assertEqual(report["summary"]["operational_facts_activated"], 0)
        self.assertFalse(report["operational_seed_eligible"])
        self.assertFalse(report["database_write_performed"])
        self.assertEqual(report["passed_checks"], 7)

    def test_submission_preserves_claim_without_activation(self):
        report = build_evidence_register(self.inventory, [self.evidence])
        row = report["evidence_records"][0]
        self.assertEqual(row["review_state"], "SUBMITTED")
        self.assertEqual(row["measurements"]["condition"], "reported_not_independently_verified")
        self.assertEqual(row["operational_effect"], "NONE_PENDING_REVIEW")
        self.assertEqual(report["summary"]["measurement_assertion_count"], 1)

    def test_accepted_evidence_still_requires_separate_activation(self):
        event = {
            "review_event_id": "SWREV-001",
            "evidence_id": "SWEV-TEST-001",
            "action": "ACCEPTED",
            "occurred_at": self.now,
            "reviewer_ref": "NPC-REVIEWER-001",
            "rationale": "Evidence provenance and method reviewed",
            "review_basis_ref": "fictional-review-record:001",
        }
        report = build_evidence_register(self.inventory, [self.evidence], [event])
        row = report["evidence_records"][0]
        self.assertEqual(row["review_state"], "ACCEPTED")
        self.assertEqual(row["operational_effect"], "EVIDENCE_ACCEPTED_NOT_AUTOMATICALLY_ACTIVATED")
        self.assertEqual(report["summary"]["operational_facts_activated"], 0)

    def test_duplicate_evidence_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate evidence_id"):
            build_evidence_register(self.inventory, [self.evidence, copy.deepcopy(self.evidence)])

    def test_unknown_subject_rejected(self):
        item = copy.deepcopy(self.evidence)
        item["subject_id"] = "NOT-IN-SOURCE"
        with self.assertRaisesRegex(ValueError, "Unknown source subject"):
            build_evidence_register(self.inventory, [item])

    def test_subject_type_mismatch_rejected(self):
        item = copy.deepcopy(self.evidence)
        item["subject_type"] = "wall"
        with self.assertRaisesRegex(ValueError, "does not match"):
            build_evidence_register(self.inventory, [item])

    def test_timezone_required(self):
        item = copy.deepcopy(self.evidence)
        item["captured_at"] = "2026-11-25T08:00:00"
        with self.assertRaisesRegex(ValueError, "include a timezone"):
            build_evidence_register(self.inventory, [item])

    def test_invalid_source_hash_rejected(self):
        item = copy.deepcopy(self.evidence)
        item["source_sha256"] = "not-a-hash"
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            build_evidence_register(self.inventory, [item])

    def test_review_event_requires_existing_submission(self):
        event = {
            "review_event_id": "SWREV-002",
            "evidence_id": "MISSING",
            "action": "ACCEPTED",
            "occurred_at": self.now,
            "reviewer_ref": "NPC-REVIEWER-001",
            "rationale": "Test",
            "review_basis_ref": "review:002",
        }
        with self.assertRaisesRegex(ValueError, "unknown evidence"):
            build_evidence_register(self.inventory, [self.evidence], [event])

    def test_terminal_review_state_cannot_be_overwritten(self):
        events = [
            {"review_event_id": "SWREV-003", "evidence_id": "SWEV-TEST-001",
             "action": "ACCEPTED", "occurred_at": self.now,
             "reviewer_ref": "NPC-REVIEWER-001", "rationale": "Accepted",
             "review_basis_ref": "review:003"},
            {"review_event_id": "SWREV-004", "evidence_id": "SWEV-TEST-001",
             "action": "REJECTED", "occurred_at": "2026-11-25T08:01:00Z",
             "reviewer_ref": "NPC-REVIEWER-002", "rationale": "Attempted overwrite",
             "review_basis_ref": "review:004"},
        ]
        with self.assertRaisesRegex(ValueError, "Terminal review state"):
            build_evidence_register(self.inventory, [self.evidence], events)

    def test_measurements_are_whitelisted(self):
        item = copy.deepcopy(self.evidence)
        item["measurements"]["invented_property"] = "bad"
        with self.assertRaisesRegex(ValueError, "Unsupported measurement"):
            build_evidence_register(self.inventory, [item])

    def test_attachment_hashes_validated(self):
        item = copy.deepcopy(self.evidence)
        item["attachment_sha256"] = ["bad"]
        with self.assertRaisesRegex(ValueError, "attachment_sha256"):
            build_evidence_register(self.inventory, [item])


if __name__ == "__main__":
    unittest.main()
