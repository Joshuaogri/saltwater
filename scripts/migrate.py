#!/usr/bin/env python3
"""Deterministic Saltwater PostgreSQL migration runner.

Default mode is read-only verification. Applying migrations requires --apply.
The runner refuses legacy ledger rows without checksums; baseline adoption is a
separate, explicitly reviewed operation and is deliberately not automated here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import psycopg

MIGRATION_RE = re.compile(r"^(?P<version>\d{4})_(?P<name>[a-z0-9_]+)\.sql$")
LOCK_KEY = 0x5357414C54574152  # "SWALTWAR"


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    path: Path
    checksum: str

    @property
    def filename(self) -> str:
        return self.path.name


def discover(directory: Path) -> list[Migration]:
    found: list[Migration] = []
    for path in sorted(directory.glob("*.sql")):
        match = MIGRATION_RE.fullmatch(path.name)
        if not match:
            raise ValueError(f"Invalid migration filename: {path.name}")
        raw = path.read_bytes()
        found.append(Migration(
            int(match.group("version")),
            match.group("name"),
            path,
            hashlib.sha256(raw).hexdigest(),
        ))
    versions = [m.version for m in found]
    if versions != list(range(1, len(versions) + 1)):
        raise ValueError(f"Migration versions must be contiguous from 0001; found {versions}")
    if len({m.name for m in found}) != len(found):
        raise ValueError("Migration names must be unique")
    return found


def unwrap_transaction(sql: str) -> str:
    """Remove only a single outer BEGIN/COMMIT pair; runner owns atomicity."""
    begin = re.match(r"\A((?:\s*--[^\n]*\n)*)\s*BEGIN\s*;", sql, re.IGNORECASE)
    end = re.search(r"\bCOMMIT\s*;\s*\Z", sql, re.IGNORECASE)
    if not begin or not end or end.start() <= begin.end():
        raise ValueError("Each migration must have one outer BEGIN; ... COMMIT; wrapper")
    body = sql[begin.end():end.start()]
    if re.search(r"^\s*(BEGIN|COMMIT|ROLLBACK)\s*;", body, re.IGNORECASE | re.MULTILINE):
        raise ValueError("Nested transaction control is not permitted in migration body")
    return body


def ledger_rows(conn) -> list[tuple[int, str, str | None, str | None]]:
    has_fingerprint = has_fingerprint_column(conn)
    columns = "version, migration_name, checksum_sha256"
    if has_fingerprint:
        columns += ", schema_fingerprint_sha256"
    with conn.cursor() as cur:
        cur.execute(f"SELECT {columns} FROM sw_ops.schema_migration ORDER BY version")
        rows = cur.fetchall()
    if has_fingerprint:
        return rows
    return [(version, name, checksum, None) for version, name, checksum in rows]


def schema_fingerprint(conn) -> str:
    """Hash schemas owned by this runner, excluding BP02 sw_geo (which has its own migration ledger)."""
    catalogue = []
    queries = [
        ("schemas", """
            SELECT nspname,COALESCE(nspacl::text,'')
            FROM pg_namespace
            WHERE left(nspname,3)='sw_' AND nspname <> 'sw_geo'
            ORDER BY nspname
        """),
        ( "relations", """
            SELECT n.nspname, c.relname, c.relkind,
                   c.relrowsecurity,c.relforcerowsecurity,COALESCE(c.relacl::text,''),
                   COALESCE(pg_get_viewdef(c.oid, true), '')
            FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE left(n.nspname,3)='sw_' AND n.nspname <> 'sw_geo'
              AND c.relkind IN ('r','p','v','m','S')
            ORDER BY n.nspname,c.relname
        """),
        ( "columns", """
            SELECT n.nspname,c.relname,a.attnum,a.attname,
                   pg_catalog.format_type(a.atttypid,a.atttypmod),
                   a.attnotnull,COALESCE(pg_get_expr(d.adbin,d.adrelid),''),
                   a.attidentity,a.attgenerated
            FROM pg_attribute a
            JOIN pg_class c ON c.oid=a.attrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum
            WHERE left(n.nspname,3)='sw_' AND n.nspname <> 'sw_geo'
              AND a.attnum>0 AND NOT a.attisdropped
            ORDER BY n.nspname,c.relname,a.attnum
        """),
        ( "constraints", """
            SELECT n.nspname,c.relname,con.conname,con.contype,
                   pg_get_constraintdef(con.oid,true)
            FROM pg_constraint con
            JOIN pg_class c ON c.oid=con.conrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE left(n.nspname,3)='sw_' AND n.nspname <> 'sw_geo'
            ORDER BY n.nspname,c.relname,con.conname
        """),
        ( "indexes", """
            SELECT schemaname,tablename,indexname,indexdef
            FROM pg_indexes
            WHERE left(schemaname,3)='sw_' AND schemaname <> 'sw_geo'
            ORDER BY schemaname,tablename,indexname
        """),
        ( "routines", """
            SELECT n.nspname,p.proname,pg_get_function_identity_arguments(p.oid),
                   p.prokind,COALESCE(p.proacl::text,''),pg_get_functiondef(p.oid)
            FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
            WHERE left(n.nspname,3)='sw_' AND n.nspname <> 'sw_geo' AND p.prokind IN ('f','p')
            ORDER BY n.nspname,p.proname,pg_get_function_identity_arguments(p.oid)
        """),
        ( "triggers", """
            SELECT n.nspname,c.relname,t.tgname,t.tgenabled,pg_get_triggerdef(t.oid,true)
            FROM pg_trigger t
            JOIN pg_class c ON c.oid=t.tgrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE left(n.nspname,3)='sw_' AND n.nspname <> 'sw_geo' AND NOT t.tgisinternal
            ORDER BY n.nspname,c.relname,t.tgname
        """),
        ( "policies", """
            SELECT schemaname,tablename,policyname,permissive,roles,cmd,qual,with_check
            FROM pg_policies
            WHERE left(schemaname,3)='sw_' AND schemaname <> 'sw_geo'
            ORDER BY schemaname,tablename,policyname
        """),
    ]
    with conn.cursor() as cur:
        for label, query in queries:
            cur.execute(query)
            catalogue.append([label, cur.fetchall()])
    payload = json.dumps(catalogue, ensure_ascii=False, separators=(',', ':'), default=str)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def has_fingerprint_column(conn) -> bool:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema='sw_ops' AND table_name='schema_migration'
                  AND column_name='schema_fingerprint_sha256'
            )
        """)
        return cur.fetchone()[0]


def verify(conn, migrations: list[Migration], allow_pending: bool = False) -> None:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT to_regclass('sw_ops.schema_migration') IS NOT NULL
        """)
        if not cur.fetchone()[0]:
            raise RuntimeError("Migration ledger is absent; apply the foundation migration first")
    rows = ledger_rows(conn)
    by_version = {m.version: m for m in migrations}
    seen: set[int] = set()
    for version, name, checksum, fingerprint in rows:
        migration = by_version.get(version)
        if migration is None:
            raise RuntimeError(f"Database has unknown migration version {version}")
        if name != migration.name:
            raise RuntimeError(f"Migration identity mismatch at {version}: database={name}, source={migration.name}")
        if checksum is None:
            raise RuntimeError(
                f"Legacy migration {version:04d}_{name} has no checksum; "
                "verification stops pending an explicit baseline-adoption review"
            )
        if checksum.strip().lower() != migration.checksum:
            raise RuntimeError(f"Checksum drift for {migration.filename}")
        seen.add(version)
    if seen != set(range(1, max(seen, default=0) + 1)):
        raise RuntimeError("Database migration history contains a version gap")
    pending = [m.filename for m in migrations if m.version not in seen]
    if pending and not allow_pending:
        raise RuntimeError("Pending migrations: " + ", ".join(pending))
    if rows and has_fingerprint_column(conn):
        latest_fingerprint = rows[-1][3]
        actual_fingerprint = schema_fingerprint(conn)
        if not latest_fingerprint:
            raise RuntimeError("Latest migration has no schema fingerprint")
        if latest_fingerprint.strip().lower() != actual_fingerprint:
            raise RuntimeError("Live schema drift detected: catalogue fingerprint differs from latest migration")
    print(f"OK: {len(rows)} applied migrations; checksums match" +
          ("; live schema fingerprint matches" if rows and has_fingerprint_column(conn) else "") +
          (("; pending migrations: " + ", ".join(pending)) if pending else ""))


def apply(conn, migrations: list[Migration]) -> None:
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_lock(%s)", (LOCK_KEY,))
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass('sw_ops.schema_migration') IS NOT NULL")
            ledger_exists = cur.fetchone()[0]
        applied = ledger_rows(conn) if ledger_exists else []
        by_version = {row[0]: row for row in applied}
        if applied and has_fingerprint_column(conn):
            latest = applied[-1]
            if not latest[3] or latest[3].strip().lower() != schema_fingerprint(conn):
                raise RuntimeError('Live schema drift detected before migration')
        for migration in migrations:
            existing = by_version.get(migration.version)
            if existing:
                _, name, checksum, fingerprint = existing
                if name != migration.name:
                    raise RuntimeError(f"Migration identity mismatch at {migration.version}")
                if checksum is None:
                    raise RuntimeError(
                        f"Legacy migration {migration.version:04d}_{name} has no checksum; "
                        "explicit baseline adoption is required before applying later migrations"
                    )
                if checksum.strip().lower() != migration.checksum:
                    raise RuntimeError(f"Checksum drift for {migration.filename}")
                continue

            expected = len(by_version) + 1
            if migration.version != expected:
                raise RuntimeError(f"Refusing out-of-order migration {migration.version}; expected {expected}")
            sql = unwrap_transaction(migration.path.read_text(encoding="utf-8"))
            print(f"Applying {migration.filename} ({len(migration.path.read_bytes())} source bytes)")
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(sql)
                    cur.execute("""
                        INSERT INTO sw_ops.schema_migration
                            (version, migration_name, checksum_sha256)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (version) DO UPDATE
                        SET migration_name = EXCLUDED.migration_name,
                            checksum_sha256 = EXCLUDED.checksum_sha256
                        WHERE sw_ops.schema_migration.migration_name = EXCLUDED.migration_name
                    """, (migration.version, migration.name, migration.checksum))
                    if has_fingerprint_column(conn):
                        fingerprint = schema_fingerprint(conn)
                        cur.execute("""
                            UPDATE sw_ops.schema_migration
                            SET schema_fingerprint_sha256 = %s
                            WHERE version = %s
                        """, (fingerprint, migration.version))
                    cur.execute("""
                        SELECT migration_name, checksum_sha256
                        FROM sw_ops.schema_migration WHERE version = %s
                    """, (migration.version,))
                    recorded = cur.fetchone()
                    if not recorded or recorded[0] != migration.name or recorded[1].strip() != migration.checksum:
                        raise RuntimeError(f"Ledger write did not verify for {migration.filename}")
            by_version[migration.version] = (migration.version, migration.name, migration.checksum, None)
        verify(conn, migrations)
    finally:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_unlock(%s)", (LOCK_KEY,))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--migrations", default="db/migrations")
    parser.add_argument("--apply", action="store_true", help="apply pending migrations (never implied)")
    parser.add_argument("--allow-pending", action="store_true", help="read-only verification may report unapplied migrations without failing")
    args = parser.parse_args()
    if not args.database_url:
        parser.error("DATABASE_URL or --database-url is required")
    migrations = discover(Path(args.migrations))
    if not migrations:
        parser.error("No migrations found")
    try:
        with psycopg.connect(args.database_url, autocommit=True) as conn:
            if args.apply:
                apply(conn, migrations)
            else:
                verify(conn, migrations, allow_pending=args.allow_pending)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
