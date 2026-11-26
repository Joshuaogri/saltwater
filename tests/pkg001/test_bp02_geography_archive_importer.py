from __future__ import annotations

import gzip
import io
import tarfile
import unittest

from runtime.bp02_geography_archive_importer import (
    RELEASE_CODE,
    SOURCE_PATHS,
    build_package,
)


class BP02GeographyArchiveImporterTests(unittest.TestCase):
    def test_package_is_deterministic_and_validated(self):
        first = build_package("test-commit-123")
        second = build_package("test-commit-123")
        self.assertEqual(first["payload"], second["payload"])
        self.assertEqual(first["archive_sha256"], second["archive_sha256"])
        self.assertEqual(first["manifest"]["release_code"], RELEASE_CODE)
        self.assertEqual(first["manifest"]["release_scope"], "SOURCE_ARCHIVE_ONLY")
        self.assertFalse(first["manifest"]["operational_geography_promoted"])
        self.assertEqual(first["manifest"]["identity_validation"]["source_records"], 100)
        self.assertEqual(first["manifest"]["identity_validation"]["resolved"], 100)
        self.assertEqual(first["manifest"]["identity_validation"]["unresolved"], 0)
        self.assertEqual(len(first["manifest"]["source_files"]), 2)
        self.assertEqual(
            [row["path"] for row in first["manifest"]["source_files"]],
            list(SOURCE_PATHS),
        )
        self.assertGreater(first["compressed_bytes"], 0)
        self.assertGreater(first["source_bytes_total"], first["compressed_bytes"])

    def test_archive_contains_exact_source_files(self):
        package = build_package("test-commit-123")
        tar_bytes = gzip.decompress(package["payload"])
        with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:") as archive:
            members = archive.getmembers()
            self.assertEqual([member.name for member in members], sorted(SOURCE_PATHS))
            self.assertEqual(
                sum(member.size for member in members),
                package["source_bytes_total"],
            )
            self.assertTrue(all(member.uid == 0 and member.gid == 0 for member in members))
            self.assertTrue(all(member.mtime == 0 for member in members))


if __name__ == "__main__":
    unittest.main()
