"""Build and store the immutable BP-02 SW-GEO-V1 source archive.

The default invocation is a local dry run. Applying requires --apply and an
explicit expected database name. Production additionally requires
--allow-production and is archive-only: no spatial identities or geometry rows
are promoted into operational gameplay tables.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import tarfile
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

from runtime.geography_identity_reconciliation import validate_identity_map

ROOT = Path(__file__).resolve().parents[1]
RELEASE_CODE = "SW-GEO-V1"
SOURCE_PATHS = (
    "data/geography/saltwater-geography-v1.json",
    "data/geography/saltwater-geography-v1-identity-map.json",
)


def build_package(source_commit: str = "local-build") -> dict:
    source_files = []
    raw_files = []
    for relative in SOURCE_PATHS:
        path = ROOT / relative
        raw = path.read_bytes()
        raw_files.append((relative, raw))
        source_files.append({
            "path": relative,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })

    geography = json.loads(raw_files[0][1])
    identity_map = json.loads(raw_files[1][1])
    identity_validation = validate_identity_map(geography, identity_map)

    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for relative, raw in sorted(raw_files):
            info = tarfile.TarInfo(relative)
            info.size = len(raw)
            info.mode = 0o644
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mtime = 0
            archive.addfile(info, io.BytesIO(raw))

    tar_bytes = tar_buffer.getvalue()
    compressed_buffer = io.BytesIO()
    with gzip.GzipFile(
        filename="", mode="wb", fileobj=compressed_buffer, compresslevel=9, mtime=0
    ) as compressed:
        compressed.write(tar_bytes)
    payload = compressed_buffer.getvalue()

    manifest = {
        "release_code": RELEASE_CODE,
        "archive_format": "tar.gz",
        "source_commit": source_commit,
        "source_files": source_files,
        "source_bytes_total": sum(row["bytes"] for row in source_files),
        "tar_uncompressed_bytes": len(tar_bytes),
        "compressed_archive_bytes": len(payload),
        "archive_sha256": hashlib.sha256(payload).hexdigest(),
        "identity_validation": identity_validation,
        "release_scope": "SOURCE_ARCHIVE_ONLY",
        "operational_geography_promoted": False,
    }
    return {
        "payload": payload,
        "manifest": manifest,
        "source_bytes_total": manifest["source_bytes_total"],
        "compressed_bytes": len(payload),
        "uncompressed_bytes": manifest["source_bytes_total"],
        "archive_sha256": manifest["archive_sha256"],
    }


def import_package(dsn: str, package: dict, expected_database: str,
                   allow_production: bool = False) -> dict:
    if not dsn:
        raise ValueError("DATABASE_URL is required for --apply")
    if not expected_database:
        raise ValueError("--expected-database is required for --apply")

    with psycopg.connect(dsn) as conn:
        actual_database = conn.execute("SELECT current_database()").fetchone()[0]
        if actual_database != expected_database:
            raise ValueError(
                f"Database mismatch: expected {expected_database!r}, connected to {actual_database!r}"
            )
        if actual_database == "neondb" and not allow_production:
            raise PermissionError("Production requires explicit --allow-production")
        if actual_database != "neondb" and allow_production:
            raise ValueError("--allow-production is valid only for the neondb database")

        with conn.transaction():
            existing = conn.execute(
                """
                SELECT archive_sha256, compressed_bytes
                FROM sw_geo.source_archive
                WHERE release_code = %s
                FOR UPDATE
                """,
                (RELEASE_CODE,),
            ).fetchone()
            if existing:
                if existing[0].strip() != package["archive_sha256"]:
                    raise ValueError(
                        "SW-GEO-V1 already exists with a different checksum; publish a new release code"
                    )
                return {
                    "status": "already_present",
                    "release_code": RELEASE_CODE,
                    "archive_sha256": package["archive_sha256"],
                    "compressed_bytes": existing[1],
                    "database": actual_database,
                }

            conn.execute(
                """
                INSERT INTO sw_geo.source_archive
                    (release_code, archive_format, compressed_payload,
                     compressed_bytes, uncompressed_bytes, source_file_count,
                     source_manifest, archive_sha256, source_commit, release_scope)
                VALUES (%s, 'tar.gz', %s, %s, %s, 2, %s, %s, %s,
                        'SOURCE_ARCHIVE_ONLY')
                """,
                (
                    RELEASE_CODE,
                    package["payload"],
                    package["compressed_bytes"],
                    package["uncompressed_bytes"],
                    Jsonb(package["manifest"]),
                    package["archive_sha256"],
                    package["manifest"]["source_commit"],
                ),
            )

        return {
            "status": "inserted",
            "release_code": RELEASE_CODE,
            "archive_sha256": package["archive_sha256"],
            "compressed_bytes": package["compressed_bytes"],
            "database": actual_database,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="store the archive; default is a no-write package measurement")
    parser.add_argument("--expected-database", default=None)
    parser.add_argument("--allow-production", action="store_true",
                        help="explicitly permit the neondb production database")
    parser.add_argument("--source-commit", default=os.environ.get("GITHUB_SHA", "local-build"))
    args = parser.parse_args()

    package = build_package(args.source_commit)
    result = {
        "release_code": RELEASE_CODE,
        "source_bytes_total": package["source_bytes_total"],
        "compressed_archive_bytes": package["compressed_bytes"],
        "archive_sha256": package["archive_sha256"],
        "identity_validation": package["manifest"]["identity_validation"],
        "release_scope": "SOURCE_ARCHIVE_ONLY",
        "operational_geography_promoted": False,
    }
    if args.apply:
        result["import"] = import_package(
            os.environ.get("DATABASE_URL", ""),
            package,
            args.expected_database or "",
            allow_production=args.allow_production,
        )
    else:
        result["status"] = "dry_run_no_database_write"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
