"""Independent, checksum-controlled BP-02 domain migration runner.

It never reads or changes sw_ops.schema_migration and never applies BP04 migrations.
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
MIGRATION = ROOT / "db/domain-migrations/bp02/0001_source_archive.sql"
LOCK_KEY = 0x4250303247454F31  # BP02GEO1

def migration_checksum() -> str:
    return hashlib.sha256(MIGRATION.read_bytes()).hexdigest()

def apply_bp02(conn, expected_database: str, allow_production: bool = False) -> dict:
    actual = conn.execute("SELECT current_database()").fetchone()[0]
    if actual != expected_database:
        raise ValueError(f"Database mismatch: expected {expected_database!r}, connected to {actual!r}")
    if actual == "neondb" and not allow_production:
        raise PermissionError("Production requires --allow-production")
    if actual != "neondb" and allow_production:
        raise ValueError("--allow-production is valid only for neondb")
    checksum = migration_checksum()
    name = MIGRATION.stem
    conn.execute("SELECT pg_advisory_lock(%s)", (LOCK_KEY,))
    try:
        exists = conn.execute(
            "SELECT to_regclass('sw_geo.bp02_schema_migration') IS NOT NULL"
        ).fetchone()[0]
        if exists:
            rows = conn.execute(
                "SELECT version,migration_name,checksum_sha256 FROM sw_geo.bp02_schema_migration ORDER BY version"
            ).fetchall()
            if rows:
                if rows != [(1, name, checksum)]:
                    raise RuntimeError(f"BP02 migration ledger mismatch: {rows!r}")
                return {"status":"already_applied","version":1,"migration":name,"checksum_sha256":checksum}
        sql = MIGRATION.read_text(encoding="utf-8")
        if not sql.lstrip().upper().startswith("BEGIN;") or not sql.rstrip().upper().endswith("COMMIT;"):
            raise ValueError("BP02 migration must have one outer BEGIN/COMMIT wrapper")
        body = sql[sql.upper().find("BEGIN;")+len("BEGIN;"):sql.upper().rfind("COMMIT;")]
        with conn.transaction():
            conn.execute(body)
            conn.execute(
                "INSERT INTO sw_geo.bp02_schema_migration(version,migration_name,checksum_sha256) VALUES (1,%s,%s)",
                (name,checksum),
            )
            recorded=conn.execute(
                "SELECT version,migration_name,checksum_sha256 FROM sw_geo.bp02_schema_migration WHERE version=1"
            ).fetchone()
            if recorded != (1,name,checksum):
                raise RuntimeError("BP02 migration ledger verification failed")
        return {"status":"applied","version":1,"migration":name,"checksum_sha256":checksum}
    finally:
        conn.execute("SELECT pg_advisory_unlock(%s)", (LOCK_KEY,))

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url",default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--expected-database")
    parser.add_argument("--apply",action="store_true")
    parser.add_argument("--allow-production",action="store_true")
    args=parser.parse_args()
    if not args.database_url:
        parser.error("DATABASE_URL or --database-url is required")
    if not args.apply:
        print(json.dumps({"status":"dry_run_no_database_write","migration":MIGRATION.name,"checksum_sha256":migration_checksum(),"independent_ledger":"sw_geo.bp02_schema_migration","global_migration_ledger_touched":False},indent=2))
        return 0
    if not args.expected_database:
        parser.error("--expected-database is required with --apply")
    try:
        with psycopg.connect(args.database_url,autocommit=True) as conn:
            result=apply_bp02(conn,args.expected_database,args.allow_production)
        print(json.dumps(result,indent=2,sort_keys=True))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        return 1

if __name__=="__main__":
    raise SystemExit(main())
