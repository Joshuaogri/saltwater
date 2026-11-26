"""SW-DB-001 manifest, scope and production-boundary contract tests."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class SWDB001ContractTests(unittest.TestCase):
    def test_manifest_digest_and_exact_opening_counts(self):
        manifest = json.loads((ROOT / "data/fixtures/sw-db-001-opening-manifest.json").read_text())
        canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(canonical).hexdigest()
        expected = (ROOT / "data/fixtures/sw-db-001-opening-manifest.sha256").read_text().split()[0]
        fixture = (ROOT / "tests/pkg001/sw_db_001_world_fixture.sql").read_text()
        self.assertEqual(digest, expected)
        self.assertIn(digest, fixture)
        self.assertEqual((manifest["residents"], manifest["police_subset"], manifest["living_people"]), (9000, 500, 9500))
        self.assertGreaterEqual(manifest["businesses"], 10000)
        self.assertEqual(manifest["generator_version"], 2)
        self.assertEqual(manifest["name_algorithm"], "md5-derived-twelve-syllable-pseudowords")

    def test_generator_v2_is_deterministic_and_collision_free_at_opening_scale(self):
        syllables = ["ba", "be", "bi", "bo", "bu", "da", "de", "di",
                     "do", "du", "ka", "ke", "ki", "ko", "ku", "ra"]

        def word(seed):
            digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
            return "".join(syllables[int(char, 16)] for char in digest[:12])

        people = [word(f"given:{i}") + " " + word(f"family:{i}") for i in range(1, 9501)]
        businesses = [word(f"business-name:SWB-FX-{i:05d}") + " Trading" for i in range(1, 10001)]
        self.assertEqual(len(set(people)), 9500)
        self.assertEqual(len(set(businesses)), 10000)
        self.assertEqual(len(set(people + businesses)), 19500)
        self.assertNotEqual(word("given:1"), word("given:2"))

    def test_proposal_numbering_keeps_0010_disposable_only(self):
        proposals = {p.name for p in (ROOT / "db/proposals").glob("*.sql")}
        migrations = {p.name for p in (ROOT / "db/migrations").glob("*.sql")}
        self.assertIn("0009_universal_name_registry.sql", proposals)
        self.assertIn("0010_canonical_world_provisioning.sql", proposals)
        # A legitimate source migration may also use the 0010 prefix.
        # Only the exact disposable proposal must remain out of db/migrations.
        self.assertNotIn("0010_canonical_world_provisioning.sql", migrations)

    def test_business_schema_uses_universal_naming_and_preserves_bp04_open_items(self):
        sql = (ROOT / "db/proposals/0010_canonical_world_provisioning.sql").read_text()
        self.assertIn("CREATE TABLE sw_business.business", sql)
        self.assertIn("CREATE TABLE sw_business.business_history", sql)
        self.assertIn("CREATE OR REPLACE FUNCTION sw_names.guard_reservation", sql)
        self.assertIn("entity_type IN ('GEOGRAPHY','PERSON','BUSINESS')", sql)
        self.assertNotIn("business_category", sql)
        self.assertIn("primary_spatial_id integer REFERENCES sw_geo.entity", sql)
        self.assertIn("site_assignment_status='unassigned' AND primary_spatial_id IS NULL", sql)
        self.assertIn("provisioning_content_checksum", sql)
        self.assertIn("DISPOSABLE_TEST_ONLY", sql)

    def test_fixture_is_guarded_and_does_not_seed_police_employment_or_geography(self):
        fixture = (ROOT / "tests/pkg001/sw_db_001_world_fixture.sql").read_text()
        self.assertIn("current_database() <> 'saltwater_test'", fixture)
        self.assertIn("server_version_num", fixture)
        self.assertNotRegex(fixture, re.compile(r"INSERT\\s+INTO\\s+sw_police\\.personnel", re.I))
        self.assertNotRegex(fixture, re.compile(r"INSERT\\s+INTO\\s+sw_geo\\.entity", re.I))
        self.assertIn("'RESIDENT'", fixture)
        self.assertIn("'POLICE_SUBSET'", fixture)
        self.assertIn("NON_GEOGRAPHIC_TEST_FIXTURE", fixture)

    def test_fixture_and_proposal_contain_no_production_connection_or_seed_route(self):
        proposal = (ROOT / "db/proposals/0010_canonical_world_provisioning.sql").read_text()
        fixture = (ROOT / "tests/pkg001/sw_db_001_world_fixture.sql").read_text()
        self.assertNotIn("DATABASE_URL", proposal)
        self.assertNotIn("NEON_CONNECTION", proposal)
        self.assertNotIn("DATABASE_URL", fixture)
        self.assertNotIn("NEON_CONNECTION", fixture)


if __name__ == "__main__":
    unittest.main()
