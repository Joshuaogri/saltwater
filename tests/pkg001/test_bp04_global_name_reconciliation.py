import unittest

from runtime.bp04_global_name_reconciliation import build_global_name_inventory


class BP04GlobalNameReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_global_name_inventory()

    def test_inventory_covers_all_required_bp04_name_domains(self):
        counts = self.report["domain_counts"]
        self.assertGreaterEqual(counts.get("geography", 0), 100)
        self.assertEqual(counts.get("business", 0), 20000)
        self.assertGreaterEqual(counts.get("property", 0), 1)
        self.assertGreaterEqual(counts.get("organisation", 0), 1)
        self.assertEqual(counts.get("npc_candidate", 0), 9500)
        self.assertGreater(self.report["candidate_count"], 30000)

    def test_report_is_reproducible_and_contains_reconciliation_results(self):
        second = build_global_name_inventory()
        self.assertEqual(self.report, second)
        self.assertIn("exact_conflicts", self.report)
        self.assertIn("cross_domain_near_duplicates", self.report)
        self.assertIn("placeholders", self.report)

    def test_no_placeholder_or_conflicting_owner_identity(self):
        self.assertEqual(self.report["placeholder_count"], 0)
        self.assertEqual(self.report["owner_name_conflicts"], [])

    def test_cross_domain_reconciliation_is_clear(self):
        # This is the acceptance gate for AC-A04: every included canonical
        # domain and unmaterialised opening NPC name candidate is screened
        # against the same normalizer and cross-domain namespace.
        self.assertEqual(self.report["exact_conflicts"], [])
        self.assertEqual(self.report["cross_domain_near_duplicate_count"], 0)
        self.assertTrue(self.report["pass"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
