# BP38-01 — Migration 0002 production application plan

**Status:** READY FOR EXPLICIT PRODUCTION APPROVAL — NOT EXECUTED  
**Target:** Neon project `misty-breeze-20463094`, production branch `br-bitter-rain-bdz9ddid`, database `neondb`  
**Server:** PostgreSQL 18.7  
**Repository:** `Joshuaogri/saltwater`, branch `main`  
**Scope:** Apply only committed `db/migrations/0002_migration_integrity.sql` through `scripts/migrate.py --apply`.

## 1. Current verified production baseline

Read-only Neon inspection on 2026-11-24 returned:

| Measure | Current value |
|---|---:|
| Database size | 9,306,112 bytes |
| Ledger heap | 8,192 bytes |
| Ledger indexes | 32,768 bytes |
| Ledger total relation | 49,152 bytes |
| Ledger rows | 1 |
| Existing migration | version 1, `foundation` |
| Version-1 SHA-256 | `d4f874f71eb53a961fd3abe87a9342d0354a006ef04575158d2c72937dbe6aa8` |
| Fingerprint column | absent |
| Migration-0002 constraints | absent |

The one existing checksum matches the exact committed bytes of `0001_foundation.sql`. The live Neon schema and canonical world configuration were independently compared with a clean PostgreSQL 18 replay and matched. The database contains no migration-0002 changes at this baseline.

## 2. Exact source change

Committed source: [`0002_migration_integrity.sql`](../../../db/migrations/0002_migration_integrity.sql)  
Committed runner: [`migrate.py`](../../../scripts/migrate.py)

The migration source is 726 bytes and contains these four DDL operations against the existing `sw_ops.schema_migration` table:

1. Set `checksum_sha256` to NOT NULL. The only existing row already contains the valid 64-character checksum.
2. Add `schema_migration_checksum_sha256_check`, requiring 64 lowercase hexadecimal characters.
3. Add nullable `schema_fingerprint_sha256 char(64)`.
4. Add `schema_migration_schema_fingerprint_check`, allowing NULL or 64 lowercase hexadecimal characters.

No table, index, sequence, schema, seed record, person, business, property, event or game-world record is created. The SQL source file remains in GitHub; it is not uploaded as a database blob.

The migration runner strips the source's outer BEGIN/COMMIT wrapper and owns the transaction. It obtains the existing PostgreSQL advisory lock, applies each migration in its own transaction, records version 2 and its exact source SHA-256, computes the live schema fingerprint after the DDL, records that fingerprint for version 2, and runs final verification.

## 3. Preconditions — all must pass immediately before execution

Run only read-only checks against the exact target above:

- PostgreSQL major version is 18.
- `sw_ops.schema_migration` exists and has exactly one row.
- The row is exactly version 1 / `foundation`.
- Its checksum is exactly `d4f874f71eb53a961fd3abe87a9342d0354a006ef04575158d2c72937dbe6aa8`.
- No version 2 row exists.
- `schema_fingerprint_sha256` does not exist yet.
- Neither migration-0002 constraint exists.
- No other migration runner is active.
- The repository checkout is the approved `main` commit containing the exact migration and runner reviewed here.
- A fresh `pg_database_size` and ledger heap/index/total measurement is captured as the immediate pre-write baseline.

Any failed or unexpected condition stops execution. Do not repair, adopt, delete, rename or otherwise modify production data as part of this package.

## 4. Locking, transaction and rollback assessment

The two ALTER TABLE constraint operations and the column addition require an ACCESS EXCLUSIVE table lock on `sw_ops.schema_migration`. PostgreSQL validates the CHECK constraints against the existing ledger rows. There is currently one row, so the validation workload is trivial; the lock still blocks concurrent access to that ledger table while held.

The runner already serializes migration runners using its fixed PostgreSQL advisory lock. For the production invocation, set session limits through `PGOPTIONS`:

- `lock_timeout=5s` for table-lock acquisition.
- `statement_timeout=60s` to bound each statement, including advisory-lock waiting.

Use a direct Neon database connection rather than a transaction-pooler URL for the migration session. Keep the connection URL in the protected `DATABASE_URL` secret; never print it.

The DDL, version-2 ledger insert and schema-fingerprint update are performed in one migration transaction. If a statement, constraint validation, ledger verification or fingerprint operation fails before commit, PostgreSQL rolls back the complete migration transaction. The runner's `finally` block releases the advisory lock; connection termination also releases session locks. Do not manually run individual ALTER statements or apply the SQL file outside the runner.

## 5. Storage estimate

The source migration is 726 bytes in GitHub and is not stored in Neon. It adds one nullable fixed-width ledger column and two check constraints, and changes the existing checksum column's nullability. It adds no user index and performs no intentional update to the existing version-1 row.

| Measure | Estimate |
|---|---:|
| Current database baseline | 9,306,112 bytes |
| Expected database-size delta | 0 bytes |
| Conservative allowance | 0–65,536 bytes |
| Projected database size | 9,306,112–9,371,648 bytes |
| Expected ledger heap delta | 0 bytes |
| Conservative ledger heap allowance | 0–8,192 bytes |
| Ledger index delta | 0 bytes expected |

The estimate allows up to 64 KiB for database catalogue/page allocation and one additional 8 KiB ledger heap page if required. These are planning allowances, not guaranteed physical accounting. WAL, provider logical-size/billing metrics and transient storage are separate measures. No upload or simulation-data import is part of this operation.

Immediately after execution, measure database size, ledger heap, index and total relation sizes. Record actual deltas against the immediate pre-write baseline. If actual database growth exceeds 65,536 bytes or the ledger relation grows by more than 8,192 bytes, stop further production changes and investigate before proceeding.

## 6. Exact execution procedure — only after separate approval

1. Confirm the approval explicitly names migration 0002, this Neon project, production branch and database.
2. Re-run every precondition and capture fresh sizes.
3. Check out the approved `main` commit; do not create a branch or PR.
4. Use the protected direct-connection `DATABASE_URL` and session limits:
   ```sh
   export PGOPTIONS="-c lock_timeout=5s -c statement_timeout=60s"
   python scripts/migrate.py --apply
   ```
5. Do not run any other migration, proposal, seed, upload or write.
6. Capture the runner output without exposing credentials.
7. Run the postflight read-only SQL checks below and the default read-only runner verification:
   ```sh
   python scripts/migrate.py
   ```
8. Measure and record actual database and ledger relation sizes.

## 7. Postflight acceptance

All conditions must pass:

- Ledger contains exactly versions 1 and 2 in order.
- Version 1 remains `foundation` with its adopted checksum unchanged.
- Version 2 is `migration_integrity` and its checksum matches the exact committed migration-0002 bytes.
- `schema_fingerprint_sha256` exists and version 2 contains a valid 64-character lowercase hexadecimal fingerprint.
- Both named migration-0002 constraints exist, are validated and enforce their intended expressions.
- `checksum_sha256` is NOT NULL.
- Default read-only `scripts/migrate.py` reports two applied migrations, matching source checksums and matching live schema fingerprint.
- No unexpected tables, indexes, sequences, seed rows or world-config changes appear.
- Actual storage is measured and compared with the estimate.
- No other migration or production write occurred.

If any postflight condition fails, freeze further changes. Preserve the exact error and measurements; do not attempt an unapproved compensating write.

## 8. Approval boundary

This is an execution plan, not an execution authorization. The previous approval applied only to the version-1 checksum adoption, which is complete. It did not approve migration 0002.

**No migration-0002 production write has been made.** The exact operation still requires a separate explicit approval. BP38-01 implementation in GitHub and disposable PostgreSQL tests do not themselves authorize Neon production changes.
