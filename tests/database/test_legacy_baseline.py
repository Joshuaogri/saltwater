import hashlib
import unittest

from scripts.verify_legacy_baseline import sha256


class LegacyBaselineHelpersTest(unittest.TestCase):
    def test_sha256_uses_exact_bytes(self):
        self.assertEqual(
            sha256(b"BEGIN;\nSELECT 1;\nCOMMIT;\n"),
            hashlib.sha256(b"BEGIN;\nSELECT 1;\nCOMMIT;\n").hexdigest(),
        )

    def test_newline_difference_changes_hash(self):
        self.assertNotEqual(sha256(b"SELECT 1;\n"), sha256(b"SELECT 1;"))


if __name__ == "__main__":
    unittest.main()
