import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.migrate import discover, unwrap_transaction


class MigrationDiscoveryTests(unittest.TestCase):
    def test_discovers_ordered_files_and_hashes_exact_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = b"-- one\nBEGIN;\nSELECT 1;\nCOMMIT;\n"
            second = b"-- two\nBEGIN;\nSELECT 2;\nCOMMIT;\n"
            (root / "0001_first.sql").write_bytes(first)
            (root / "0002_second.sql").write_bytes(second)
            result = discover(root)
            self.assertEqual([m.version for m in result], [1, 2])
            self.assertEqual(result[0].checksum, hashlib.sha256(first).hexdigest())

    def test_rejects_version_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "0001_first.sql").write_text("BEGIN; SELECT 1; COMMIT;")
            (root / "0003_third.sql").write_text("BEGIN; SELECT 3; COMMIT;")
            with self.assertRaisesRegex(ValueError, "contiguous"):
                discover(root)

    def test_rejects_unrecognised_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "first.sql").write_text("BEGIN; SELECT 1; COMMIT;")
            with self.assertRaisesRegex(ValueError, "Invalid migration filename"):
                discover(root)

    def test_unwraps_outer_transaction_only(self):
        source = "-- header\nBEGIN;\nSELECT 1;\nCOMMIT;\n"
        self.assertEqual(unwrap_transaction(source), "\nSELECT 1;\n")

    def test_rejects_missing_transaction_wrapper(self):
        with self.assertRaisesRegex(ValueError, "outer BEGIN"):
            unwrap_transaction("SELECT 1;")

    def test_rejects_nested_transaction_control(self):
        source = "BEGIN;\nSELECT 1;\nCOMMIT;\n"
        # An inner boundary must not be mistaken for the outer wrapper.
        source = "BEGIN;\nSELECT 1;\nBEGIN;\nSELECT 2;\nCOMMIT;\nCOMMIT;\n"
        with self.assertRaisesRegex(ValueError, "Nested"):
            unwrap_transaction(source)


if __name__ == "__main__":
    unittest.main()
