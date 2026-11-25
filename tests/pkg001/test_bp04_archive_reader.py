import gzip
import hashlib
import json
import unittest

from runtime.bp04_archive_reader import decode_archive, load_collection


class ArchiveReaderTests(unittest.TestCase):
    def setUp(self):
        self.dataset_id = "SW-TEST-V1"
        self.document = {
            "storage_format": "textual_json_columnar_v1",
            "metadata": {"dataset_id": self.dataset_id},
            "tables": {"properties": {"columns": ["property_id", "name"], "rows": [["P-1", "Central"]]}},
        }
        self.payload = gzip.compress(json.dumps(self.document, separators=(",", ":")).encode())
        self.digest = hashlib.sha256(self.payload).hexdigest()

    def test_lossless_archive_decode(self):
        self.assertEqual(decode_archive(self.dataset_id, self.payload, self.digest), self.document)

    def test_digest_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            decode_archive(self.dataset_id, self.payload, "0" * 64)

    def test_dataset_identity_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            decode_archive("SW-OTHER-V1", self.payload, self.digest)

    def test_collection_expansion(self):
        class FakeConnection:
            def execute(self, _sql, _params):
                class Result:
                    def fetchone(inner_self):
                        return (self.payload, self.digest)
                return Result()
        self.assertEqual(
            load_collection(FakeConnection(), self.dataset_id, "properties"),
            [{"property_id": "P-1", "name": "Central"}],
        )

    def test_missing_collection_is_rejected(self):
        class FakeConnection:
            def execute(self, _sql, _params):
                class Result:
                    def fetchone(inner_self):
                        return (self.payload, self.digest)
                return Result()
        with self.assertRaisesRegex(KeyError, "Collection"):
            load_collection(FakeConnection(), self.dataset_id, "missing")


if __name__ == "__main__":
    unittest.main()
