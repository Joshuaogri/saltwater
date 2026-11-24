#!/usr/bin/env python3
"""Deterministic Saltwater PostgreSQL migration runner.

Default mode is read-only verification. Applying migrations requires --apply.
The runner refuses legacy ledger rows without checksums; baseline adoption is a
separate, explicitly reviewed operation and is deliberately not automated here.
"""
from __future__ import annotations

import argparse
import hashlib
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


def ledger_rows(conn) -> list[tuple[int, str, str | None]]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT version, migration_name, checksum_sha256
            FROM sw_ops.schema_migration
            ORDER BY version
        """)
        return cur.fetchall()


def verify(conn, migrations: list[Migration]) -> None:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT to_regclass('sw_ops.schema_migration') IS NOT NULL
        """)
        if not cur.fetchone()[0]:
            raise RuntimeError("Migration ledger is absent; apply the foundation migration first")
    rows = ledger_rows(conn)
    by_version = {m.version: m for m in migrations}
    seen: set[int] = set()
    for version, name, checksum in rows:
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
    if pending:
        raise RuntimeError("Pending migrations: " + ", ".join(pending))
    print(f"OK: {len(rows)} applied migrations; identity and SHA-256 checksums match source")


def apply(conn, migrations: list[Migration]) -> None:
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_lock(%s)", (LOCK_KEY,))
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass('sw_ops.schema_migration') IS NOT NULL")
            ledger_exists = cur.fetchone()[0]
        applied = ledger_rows(conn) if ledger_exists else []
        by_version = {row[0]: row for row in applied}
        for migration in migrations:
            existing = by_version.get(migration.version)
            if existing:
                _, name, checksum = existing
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
                    cur.execute("""
                        SELECT migration_name, checksum_sha256
                        FROM sw_ops.schema_migration WHERE version = %s
                    """, (migration.version,))
                    recorded = cur.fetchone()
                    if not recorded or recorded[0] != migration.name or recorded[1].strip() != migration.checksum:
                        raise RuntimeError(f"Ledger write did not verify for {migration.filename}")
            by_version[migration.version] = (migration.version, migration.name, migration.checksum)
        verify(conn, migrations)
    finally:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_unlock(%s)", (LOCK_KEY,))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--migrations", default="db/migrations")
    parser.add_argument("--apply", action="store_true", help="apply pending migrations (never implied)")
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
                verify(conn, migrations)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
