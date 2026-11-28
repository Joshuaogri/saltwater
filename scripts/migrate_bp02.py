"""Independent, checksum-controlled BP02 domain migration runner.

Applies only db/domain-migrations/bp02/*.sql in version order. It never reads
or changes sw_ops.schema_migration and never applies BP04 migrations.
Default mode is a no-write plan. Production requires --apply and --allow-production.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
import psycopg

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = sorted((ROOT / "db/domain-migrations/bp02").glob("[0-9][0-9][0-9][0-9]_*.sql"))
MIGRATION = MIGRATIONS[0]  # compatibility alias for the original migration contract
LOCK_KEY = 0x4250303247454F31  # BP02GEO1


def migration_checksum(path: Path = MIGRATION) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def migration_plan() -> list[dict]:
    if not MIGRATIONS:
        raise RuntimeError("No BP02 domain migrations were found")
    plan = []
    for index, path in enumerate(MIGRATIONS, start=1):
        prefix, _, name = path.name.partition("_")
        if not prefix.isdigit() or int(prefix) != index:
            raise RuntimeError(f"BP02 migration sequence must be contiguous; found {path.name}")
        plan.append({
            "version": index,
            "migration_name": path.stem,
            "checksum_sha256": migration_checksum(path),
            "path": path,
        })
    return plan


def _migration_body(path: Path) -> str:
    sql = path.read_text(encoding="utf-8")
    upper = sql.upper()
    begin = upper.find("BEGIN;")
    commit = upper.rfind("COMMIT;")
    prefix = sql[:begin] if begin >= 0 else sql
    if begin < 0 or commit <= begin or any(
        line.strip() and not line.lstrip().startswith("--") for line in prefix.splitlines()
    ):
        raise ValueError(f"{path.name} must have one outer BEGIN/COMMIT wrapper")
    return sql[begin + len("BEGIN;"):commit]


def apply_bp02(conn, expected_database: str, allow_production: bool = False) -> dict:
    actual = conn.execute("SELECT current_database()").fetchone()[0]
    if actual != expected_database:
        raise ValueError(f"Database mismatch: expected {expected_database!r}, connected to {actual!r}")
    if actual == "neondb" and not allow_production:
        raise PermissionError("Production requires --allow-production")
    if actual != "neondb" and allow_production:
        raise ValueError("--allow-production is valid only for neondb")

    plan = migration_plan()
    conn.execute("SELECT pg_advisory_lock(%s)", (LOCK_KEY,))
    try:
        exists = conn.execute(
            "SELECT to_regclass('sw_geo.bp02_schema_migration') IS NOT NULL"
        ).fetchone()[0]
        rows = []
        if exists:
            rows = conn.execute(
                "SELECT version,migration_name,rtrim(checksum_sha256) FROM sw_geo.bp02_schema_migration ORDER BY version"
            ).fetchall()
        if len(rows) > len(plan):
            raise RuntimeError(f"BP02 migration ledger is ahead of source: {rows!r}")
        for expected, recorded in zip(plan, rows):
            wanted = (expected["version"], expected["migration_name"], expected["checksum_sha256"])
            if recorded != wanted:
                raise RuntimeError(f"BP02 migration ledger mismatch: expected {wanted!r}, found {recorded!r}")

        applied = []
        for migration in plan[len(rows):]:
            with conn.transaction():
                conn.execute(_migration_body(migration["path"]))
                conn.execute(
                    "INSERT INTO sw_geo.bp02_schema_migration(version,migration_name,checksum_sha256) VALUES (%s,%s,%s)",
                    (migration["version"], migration["migration_name"], migration["checksum_sha256"]),
                )
                recorded = conn.execute(
                    "SELECT version,migration_name,rtrim(checksum_sha256) FROM sw_geo.bp02_schema_migration WHERE version=%s",
                    (migration["version"],),
                ).fetchone()
                wanted = (migration["version"], migration["migration_name"], migration["checksum_sha256"])
                if recorded != wanted:
                    raise RuntimeError(f"BP02 migration ledger verification failed: {recorded!r}")
            applied.append(migration["migration_name"])
        return {
            "status": "applied" if applied else "already_applied",
            "applied_migrations": applied,
            "current_version": len(plan),
            "migration_checksums": [
                {key: value for key, value in row.items() if key != "path"} for row in plan
            ],
            "independent_ledger": "sw_geo.bp02_schema_migration",
            "global_migration_ledger_touched": False,
        }
    finally:
        conn.execute("SELECT pg_advisory_unlock(%s)", (LOCK_KEY,))



def verify_bp02(conn, expected_database: str) -> dict:
    """Read-only verification of the independent BP02 ledger and source checksums."""
    actual = conn.execute("SELECT current_database()").fetchone()[0]
    if actual != expected_database:
        raise ValueError(f"Database mismatch: expected {expected_database!r}, connected to {actual!r}")
    exists = conn.execute(
        "SELECT to_regclass('sw_geo.bp02_schema_migration') IS NOT NULL"
    ).fetchone()[0]
    if not exists:
        raise RuntimeError("BP02 migration ledger is absent")
    rows = conn.execute(
        "SELECT version,migration_name,rtrim(checksum_sha256) FROM sw_geo.bp02_schema_migration ORDER BY version"
    ).fetchall()
    plan = migration_plan()
    if len(rows) > len(plan):
        raise RuntimeError(f"BP02 migration ledger is ahead of source: {rows!r}")
    for expected, recorded in zip(plan, rows):
        wanted = (expected["version"], expected["migration_name"], expected["checksum_sha256"])
        if recorded != wanted:
            raise RuntimeError(f"BP02 migration ledger mismatch: expected {wanted!r}, found {recorded!r}")
    pending = [item["migration_name"] for item in plan[len(rows):]]
    return {
        "status": "verified",
        "current_version": len(rows),
        "pending_migrations": pending,
        "independent_ledger": "sw_geo.bp02_schema_migration",
        "global_migration_ledger_touched": False,
        "database_write_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--expected-database")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--verify", action="store_true", help="verify the existing BP02 ledger without writing")
    parser.add_argument("--allow-production", action="store_true")
    args = parser.parse_args()
    if not args.database_url:
        parser.error("DATABASE_URL or --database-url is required")
    if args.apply and args.verify:
        parser.error("--apply and --verify cannot be used together")
    if not args.apply and not args.verify:
        print(json.dumps({
            "status": "dry_run_no_database_write",
            "migrations": [{key: value for key, value in row.items() if key != "path"} for row in migration_plan()],
            "independent_ledger": "sw_geo.bp02_schema_migration",
            "global_migration_ledger_touched": False,
        }, indent=2))
        return 0
    if not args.expected_database:
        parser.error("--expected-database is required with --apply or --verify")
    try:
        with psycopg.connect(args.database_url, autocommit=True) as conn:
            if args.verify:
                result = verify_bp02(conn, args.expected_database)
            else:
                result = apply_bp02(conn, args.expected_database, args.allow_production)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
