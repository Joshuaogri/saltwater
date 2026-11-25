import gzip
import json
import tempfile
import unittest
from pathlib import Path

from runtime.bp04_source_inventory import inspect_dataset


class SourceInventoryTests(unittest.TestCase):
    def write_dataset(self, root: Path, document: dict) -> Path:
        path = root / "fixture.json.gz"
        path.write_bytes(gzip.compress(json.dumps(document).encode("utf-8"), mtime=0))
        return path

    def test_reports_collection_shape_and_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            document = {
                "storage_format": "textual_json_columnar_v1",
                "metadata": {"dataset_id": "SW-TEST-V1"},
                "tables": {
                    "assets": {"columns": ["asset_id", "name"], "rows": [["A1", "One"], ["A2", "Two"]]},
                    "empty": {"columns": ["event_id"], "rows": []},
                },
            }
            self.write_dataset(root, document)
            result = inspect_dataset(root, "SW-TEST-V1", "fixture.json.gz")
            self.assertEqual(result["record_count"], 2)
            self.assertEqual(result["collection_count"], 2)
            self.assertEqual(result["collections"][0]["identity_columns"], ["asset_id"])

    def test_rejects_malformed_row_width(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            document = {
                "storage_format": "textual_json_columnar_v1",
                "metadata": {"dataset_id": "SW-TEST-V1"},
                "tables": {"assets": {"columns": ["asset_id", "name"], "rows": [["A1"]]}},
            }
            self.write_dataset(root, document)
            with self.assertRaisesRegex(ValueError, "width mismatch"):
                inspect_dataset(root, "SW-TEST-V1", "fixture.json.gz")

    def test_rejects_missing_canonical_dataset_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            document = {
                "storage_format": "textual_json_columnar_v1",
                "metadata": {},
                "tables": {},
            }
            self.write_dataset(root, document)
            with self.assertRaisesRegex(ValueError, "missing canonical metadata.dataset_id"):
                inspect_dataset(root, "SW-TEST-V1", "fixture.json.gz")


if __name__ == "__main__":
    unittest.main()
