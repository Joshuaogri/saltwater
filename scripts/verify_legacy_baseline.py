#!/usr/bin/env python3
"""Read-only comparison of a clean 0001 replay with a legacy Saltwater database.

Both database URLs are inspected with pg_dump (which performs read-only catalog
and table reads). The script never runs SQL writes or migrations. The reference
database must already have been created by replaying the exact 0001 source.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

SCHEMAS = ("sw_core", "sw_ops")
CANONICAL_TABLES = ("sw_core.world_config",)


def dump(url: str, args: list[str]) -> bytes:
    command = ["pg_dump", "--dbname", url, "--no-owner", "--no-privileges", *args]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout


def normalized_schema(url: str) -> bytes:
    args = ["--schema-only", "--schema=sw_core", "--schema=sw_ops",
            "--no-comments", "--no-security-labels"]
    raw = dump(url, args)
    # pg_dump includes a generated timestamp/version preamble; compare the DDL
    # body only. Object ordering is deterministic for a fixed PostgreSQL major.
    lines = raw.decode("utf-8").splitlines()
    body = [line for line in lines if not line.startswith("--")
            and not line.startswith("SET ")
            and not line.startswith("\\restrict ")
            and not line.startswith("\\unrestrict")
            and line.strip()]
    return ("\n".join(body) + "\n").encode("utf-8")


def canonical_data(url: str) -> bytes:
    # created_at is an installation timestamp and legitimately differs between
    # a historical production install and a fresh replay. Compare canonical
    # invariants, not that incidental timestamp.
    query = (
        "SELECT COALESCE(jsonb_agg(jsonb_build_object("
        "'world_id',world_id,'country_name',country_name,'city_name',city_name,"
        "'sovereign_city_state',sovereign_city_state,"
        "'living_population_limit',living_population_limit,"
        "'playable_city_count',playable_city_count) ORDER BY world_id),'[]'::jsonb) "
        "FROM sw_core.world_config"
    )
    result = subprocess.run(
        ["psql", "--dbname", url, "--no-psqlrc", "--tuples-only",
         "--no-align", "--set=ON_ERROR_STOP=1", "--command", query],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-url", default=os.getenv("BASELINE_REFERENCE_DATABASE_URL"))
    parser.add_argument("--target-url", default=os.getenv("BASELINE_TARGET_DATABASE_URL"))
    parser.add_argument("--migration", default="db/migrations/0001_foundation.sql")
    args = parser.parse_args()
    if not args.reference_url or not args.target_url:
        parser.error("Set BASELINE_REFERENCE_DATABASE_URL and BASELINE_TARGET_DATABASE_URL")
    migration = Path(args.migration).read_bytes()
    print(f"0001 source SHA-256: {sha256(migration)}")
    print(f"0001 source bytes: {len(migration)}")

    ref_schema = normalized_schema(args.reference_url)
    target_schema = normalized_schema(args.target_url)
    ref_data = canonical_data(args.reference_url)
    target_data = canonical_data(args.target_url)

    checks = {
        "schema_ddl_equal": ref_schema == target_schema,
        "canonical_world_config_equal": ref_data == target_data,
    }
    print(f"reference schema SHA-256: {sha256(ref_schema)}")
    print(f"target schema SHA-256:    {sha256(target_schema)}")
    print(f"reference canonical data SHA-256: {sha256(ref_data)}")
    print(f"target canonical data SHA-256:    {sha256(target_data)}")
    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    print("NOTE: pg_dump comparison covers schema DDL and world_config only. "
          "Migration/storage ledgers and storage-operation history are excluded. "
          "Sequence current values, role memberships, database settings, "
          "extension state and external grants require separate review.")
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
