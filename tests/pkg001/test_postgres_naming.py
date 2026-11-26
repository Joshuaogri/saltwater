import hashlib
import unittest

from runtime.naming import GeneratedNameBatch, NameCollision, normalize_name
from runtime.postgres_naming import PostgresNameRegistry, PersistentNameRecord


class FakeCursor:
    def __init__(self):
        self.query = None
        self.params = None
        self.one = (71,)
        self.rows = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query, params=None):
        self.query = query
        self.params = params

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self):
        self.value = FakeCursor()
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.value

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class PostgresNamingAdapterTests(unittest.TestCase):
    def setUp(self):
        self.connection = FakeConnection()
        self.registry = PostgresNameRegistry(self.connection)

    def test_reservation_is_parameterized_and_uses_database_function(self):
        reservation_id = self.registry.reserve(
            "geography", 23, "Bellview Crescent", name_form="canonical",
            source_ref="fixture", actor_ref="test", reason="unit test",
            effective_tick=0, generation_batch_id=8,
        )
        self.assertEqual(reservation_id, 71)
        self.assertIn("sw_names.reserve_name", self.connection.value.query)
        self.assertIn("%s::bigint", self.connection.value.query)
        self.assertEqual(self.connection.value.params[0], "GEOGRAPHY")
        self.assertEqual(self.connection.value.params[-1], 8)
        self.assertEqual(self.connection.commits, 0)

    def test_business_reservation_uses_stable_text_id_and_controlled_function(self):
        reservation_id = self.registry.reserve_business(
            "SWBIZ-000001", "Amber Meridian Trading", name_form="trading",
            source_ref="business-registry-v1", actor_ref="ci-test",
            reason="business naming integration", effective_tick=0,
            generation_batch_id=8,
        )
        self.assertEqual(reservation_id, 71)
        self.assertIn("sw_names.reserve_business_name", self.connection.value.query)
        self.assertIn("%s::text", self.connection.value.query)
        self.assertEqual(self.connection.value.params[0], "SWBIZ-000001")
        self.assertEqual(self.connection.value.params[1], "trading")
        self.assertEqual(self.connection.value.params[-1], 8)
        self.assertEqual(self.connection.commits, 0)

    def test_business_search_preserves_text_identity(self):
        self.connection.value.rows = [
            (72, "BUSINESS", "SWBIZ-000001", "trading",
             "Amber Meridian Trading", "active", False),
        ]
        results = self.registry.search_business("Amber Meridian Trading")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].entity_id, None)
        self.assertEqual(results[0].entity_ref, "SWBIZ-000001")
        self.assertEqual(results[0].entity_type, "BUSINESS")
        self.assertIn("sw_names.search_business_name", self.connection.value.query)

    def test_business_reservation_rejects_missing_or_numeric_business_identity(self):
        with self.assertRaises(ValueError):
            self.registry.reserve_business(
                "", "Amber Meridian Trading", name_form="trading",
                source_ref="fixture", actor_ref="test", reason="invalid",
                effective_tick=0,
            )
        self.assertIsNone(self.connection.value.query)

    def test_generation_batch_manifest_is_persisted_with_binary_digest(self):
        digest = hashlib.sha256(b"fixture").hexdigest()
        batch = GeneratedNameBatch(
            domain="person", generator_version=1, normalizer_version=1, config_version="1",
            seed=14, candidates=("Amara Nneka Okafor",), manifest_sha256=digest,
        )
        batch_id = self.registry.record_generation_batch(
            batch, source_ref="fixture", actor_ref="test", reason="unit test",
        )
        self.assertEqual(batch_id, 71)
        self.assertIn("record_generation_batch", self.connection.value.query)
        self.assertEqual(self.connection.value.params[5], bytes.fromhex(digest))
        self.assertEqual(self.connection.value.params[2], 1)

    def test_alias_and_retirement_use_controlled_database_functions(self):
        alias_id = self.registry.add_alias(
            "PERSON", 12, "Nneka", source_ref="fixture", actor_ref="test",
            reason="preferred short name", effective_tick=3,
        )
        self.assertEqual(alias_id, 71)
        self.assertIn("sw_names.add_alias", self.connection.value.query)
        self.registry.retire(
            71, effective_tick=4, source_ref="fixture", actor_ref="test",
            reason="retirement test",
        )
        self.assertIn("sw_names.change_status", self.connection.value.query)
        self.assertEqual(self.connection.value.params[1], "retired")

    def test_search_returns_explicit_ambiguity_for_saltwater_roots(self):
        self.connection.value.rows = [
            (1, "GEOGRAPHY", 1, "canonical", "Saltwater", "active", True),
            (2, "GEOGRAPHY", 2, "canonical", "Saltwater", "active", True),
        ]
        results = self.registry.search("Saltwater")
        self.assertEqual(len(results), 2)
        self.assertTrue(all(isinstance(x, PersistentNameRecord) for x in results))
        self.assertTrue(all(x.ambiguous for x in results))
        self.assertIn("sw_names.search_name", self.connection.value.query)

    def test_invalid_name_fails_before_database_call(self):
        with self.assertRaises(ValueError):
            self.registry.reserve(
                "GEOGRAPHY", 2, "  ", source_ref="fixture",
                actor_ref="test", reason="invalid", effective_tick=0,
            )
        self.assertIsNone(self.connection.value.query)

    def test_adapter_does_not_commit_or_rollback_callers_transaction(self):
        self.registry.reserve(
            "GEOGRAPHY", 23, "Bellview Crescent", source_ref="fixture",
            actor_ref="test", reason="unit test", effective_tick=0,
        )
        self.assertEqual(self.connection.commits, 0)
        self.assertEqual(self.connection.rollbacks, 0)


if __name__ == "__main__":
    unittest.main()
