#!/usr/bin/env python3
"""Static safety and numbering audit for the SW-DB-001 disposable package."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/fixtures/sw-db-001-opening-manifest.json"
DIGEST = ROOT / "data/fixtures/sw-db-001-opening-manifest.sha256"
PROPOSAL = ROOT / "db/proposals/0010_canonical_world_provisioning.sql"
FIXTURE = ROOT / "tests/pkg001/sw_db_001_world_fixture.sql"


def verify() -> None:
    proposals = sorted((ROOT / "db/proposals").glob("*.sql"))
    names = [path.name for path in proposals]
    if names.count("0010_canonical_world_provisioning.sql") != 1:
        raise SystemExit("expected exactly one disposable proposal 0010")
    if "0009_universal_name_registry.sql" not in names:
        raise SystemExit("proposal 0009 naming registry must precede SW-DB-001")
    migrations = sorted((ROOT / "db/migrations").glob("*.sql"))
    if any(path.name == PROPOSAL.name for path in migrations):
        raise SystemExit("SW-DB-001 must remain a disposable proposal, not a source migration")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    expected = DIGEST.read_text(encoding="utf-8").split()[0]
    if digest != expected:
        raise SystemExit("fixture manifest SHA-256 does not match canonical JSON")
    if digest not in FIXTURE.read_text(encoding="utf-8"):
        raise SystemExit("fixture SQL manifest digest differs from checked-in manifest")
    if manifest.get("residents") != 9000 or manifest.get("police_subset") != 500:
        raise SystemExit("opening cohort manifest must remain 9,000 + 500")
    if manifest.get("living_people") != 9500 or manifest.get("businesses", 0) < 10000:
        raise SystemExit("opening fixture must be 9,500 people and at least 10,000 businesses")
    if manifest.get("generator_version") != 2 or manifest.get("name_algorithm") != "md5-derived-twelve-syllable-pseudowords":
        raise SystemExit("fixture generator version/name algorithm is not the adopted deterministic version")

    sql = PROPOSAL.read_text(encoding="utf-8")
    fixture = FIXTURE.read_text(encoding="utf-8")
    if "CREATE SCHEMA sw_business" not in sql or "CREATE TABLE sw_business.business" not in sql:
        raise SystemExit("business-owned identity schema is missing")
    if "CREATE OR REPLACE FUNCTION sw_names.guard_reservation" not in sql:
        raise SystemExit("business universal-naming adapter is missing")
    if "provisioning_content_checksum" not in sql or "DISPOSABLE_TEST_ONLY" not in sql:
        raise SystemExit("immutable test-only manifest/content checksums are missing")
    if "DATABASE_URL" in sql or "SUPABASE" in sql or "NEON_CONNECTION" in sql:
        raise SystemExit("production connection material is forbidden in disposable proposal")
    if "current_database() <> 'saltwater_test'" not in fixture:
        raise SystemExit("fixture is not database-name guarded")
    if "server_version_num" not in fixture:
        raise SystemExit("fixture must enforce disposable PostgreSQL version")
    if re.search(r"INSERT\s+INTO\s+sw_police\.personnel", fixture, re.I):
        raise SystemExit("fixture must not fabricate police appointments")
    if re.search(r"INSERT\s+INTO\s+sw_geo\.entity", fixture, re.I):
        raise SystemExit("fixture must not fabricate detailed geography")
    if "NON_GEOGRAPHIC_TEST_FIXTURE" not in fixture or "TEST_MARITIME" not in fixture:
        raise SystemExit("test-only non-geographic business variety is not explicitly labelled")

    print("SW_DB_001_CONTRACT_PASS")
    print(f"proposal=0010_canonical_world_provisioning.sql")
    print(f"manifest_sha256={digest}")


if __name__ == "__main__":
    verify()
