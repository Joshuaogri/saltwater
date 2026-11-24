# BP38-02 — Independent Legacy Baseline Replay and Comparison

**Status:** Comparator implemented on `main`; independent disposable replay, drift detection and guarded checksum-adoption CI PASS; live Neon schema and canonical-data comparison PASS in [run 45437263676](https://github.com/Joshuaogri/saltwater/actions/runs/45437263676), with supplementary catalogue review recorded in [live run 0001 evidence](../test-evidence/BP38-02-live-neon-run-0001.md). Checksum adoption is prepared but NOT applied.  
**Production authority:** No Neon write or adoption approval is granted by this package.

## Purpose

Compare a fresh disposable PostgreSQL replay of the exact committed `0001_foundation.sql` with the existing legacy Neon baseline. The comparison must be read-only against both databases.

## Tool

`scripts/verify_legacy_baseline.py` uses `pg_dump` to create deterministic, owner/privilege-neutral schema DDL snapshots for `sw_core` and `sw_ops`, and a separate canonical-data snapshot for `sw_core.world_config` that excludes the installation-specific `created_at` timestamp. It prints the exact migration source SHA-256 and byte count, snapshot hashes and pass/fail results.

Environment variables:
- `BASELINE_REFERENCE_DATABASE_URL`: disposable database where exact 0001 has been replayed.
- `BASELINE_TARGET_DATABASE_URL`: existing legacy Neon database, supplied only through a protected environment variable.

The script does not invoke the migration runner against the target, issue DDL/DML, alter the migration ledger or adopt a checksum. `pg_dump` is used only for read operations.

## Comparison boundary

Compared:
- DDL for all objects included in `sw_core` and `sw_ops`, including table/sequence definitions, constraints, indexes, defaults, identity declarations, routines, triggers and policies where present.
- Canonical `sw_core.world_config` data.

Intentionally excluded:
- `sw_ops.schema_migration` row values (legacy checksum is NULL by design).
- `sw_ops.storage_operation` row values (production operational history is legitimate and not present in a clean replay).
- Sequence current values, role memberships, database settings, extension state, external grants and provider configuration. These require separate review and must not be inferred from a matching DDL hash.

## Run procedure

1. Create a disposable PostgreSQL database using the same major version as Neon (currently PostgreSQL 18); use a matching `pg_dump`/`psql` client major version.
2. Replay exact `db/migrations/0001_foundation.sql` into that disposable database.
3. Set the reference URL to that disposable database.
4. Set the target URL to Neon production using a protected secret; never print or commit either URL.
5. Run `python scripts/verify_legacy_baseline.py`.
6. Require both comparisons to PASS. Any failure stops adoption.
7. Separately inspect sequence state, ownership/ACLs, role memberships, extensions, settings and the two storage-operation records. Record differences and explain them; do not change production to force a match.

A passing result is evidence for the compared categories only. It is not blanket certification of every PostgreSQL object or permission.

## Manual production verification workflow

A manual-only workflow is provided at [BP38-02 read-only Neon baseline verification](../../../.github/workflows/bp38-02-neon-read-only-verification.yml). It requires the protected repository secret `DATABASE_URL`, starts a disposable PostgreSQL 18 reference service, replays the exact committed 0001 migration there, and compares that reference with Neon. For target connections it sets PostgreSQL `default_transaction_read_only=on`; it runs no migration or production DDL/DML. It also emits a supplementary SELECT-only catalogue report covering database size/version, schema relation ownership/ACL/RLS, sequence configuration/current values, role memberships, extensions, selected database settings, migration ledger and storage-operation history. The report is uploaded as a 14-day workflow artifact. The workflow is `workflow_dispatch` only and has no push trigger.

The workflow completed successfully in [run 45437263676](https://github.com/Joshuaogri/saltwater/actions/runs/45437263676). Schema DDL and canonical world-config hashes matched exactly; the target session confirmed `default_transaction_read_only=on`. The supplementary report was reviewed and is recorded in [live run 0001 evidence](../test-evidence/BP38-02-live-neon-run-0001.md). Do not put the connection URL in logs, artifacts, command output or repository files.

## Guarded checksum-adoption proposal

A proposal-only SQL file is committed at [`db/proposals/0003_legacy_checksum_adoption.sql`](../../../db/proposals/0003_legacy_checksum_adoption.sql). It targets exactly one row: `version=1`, `migration_name='foundation'`, and `checksum_sha256 IS NULL`. It writes the committed migration 0001 SHA-256 `d4f874f71eb53a961fd3abe87a9342d0354a006ef04575158d2c72937dbe6aa8`, aborts unless exactly one row changes, verifies the resulting value, and rolls back on any failed guard. A second execution is intentionally rejected. CI tests it only against a disposable database. This SQL is not in `db/migrations/` and must not be run against Neon until the live comparison and supplementary review pass and the exact production operation receives separate explicit approval.

Expected production effect if separately approved: one existing ledger row metadata field updated; no game-world records, schema objects, sequence values or simulation data are intentionally changed. Measure database size before/after if executed; do not assume a zero-byte physical storage delta.

## Adoption gate

No checksum adoption is included. After the full comparison and supplementary review pass, prepare a separate exact, conditional one-row update for `version=1`, `migration_name='foundation'`, and `checksum_sha256 IS NULL`. Present the exact SHA-256, statement, row-count guard, expected storage effect and rollback considerations for explicit user approval. Migration 0002 remains a distinct subsequent operation requiring separate approval.


## CI evidence — 2026-11-24

Workflow run [45434212975](https://github.com/Joshuaogri/saltwater/actions/runs/45434212975) passed all steps. It created independent PostgreSQL 18 reference and target databases, replayed exact migration 0001, confirmed the comparator accepts matching schema/canonical world data, deliberately introduced a target-only schema change and confirmed that the comparator rejects the drift, then ran the migration-runner and runtime-kernel tests. The CI comparison is disposable-only; it does not connect to Neon and is not evidence that the live Neon baseline matches the replay. See [BP38-02 run 0001](../test-evidence/BP38-02-run-0001.md).


## CI evidence — run 0002

Workflow run [45435673095](https://github.com/Joshuaogri/saltwater/actions/runs/45435673095) completed successfully. In addition to the independent PostgreSQL 18 replay/comparison and migration/runtime regression checks, it exercised the guarded legacy checksum-adoption proposal in disposable PostgreSQL only, including the one-row precondition and fail-closed repeat execution. All job steps, including container cleanup, completed. This is not live Neon comparison evidence and did not modify Neon. See [BP38-02 run 0002](../test-evidence/BP38-02-run-0002.md).


## Live Neon evidence — run 0001

The live workflow passed on 2026-11-24. Exact schema DDL hashes and canonical world-config hashes matched the independent PostgreSQL 18 replay. The supplementary SELECT-only report was reviewed: Neon is PostgreSQL 18.7 at 9,306,112 bytes; the ledger remains at version 1 with a NULL checksum; the two storage-operation history rows and provider catalogue context were enumerated. No mismatch affecting the comparison was found. The workflow enforced read-only mode and made no production changes. See [live Neon run 0001](../test-evidence/BP38-02-live-neon-run-0001.md).

**Next gate:** present the exact guarded one-row checksum adoption, expected storage delta/range and projected total for separate explicit production approval. Do not apply migration 0002 as part of that operation.


## Production checksum-adoption operation — prepared, not executed

**Target:** Neon project `misty-breeze-20463094`, production branch `br-bitter-rain-bdz9ddid`, database `neondb`.  
**Baseline measured read-only after successful comparison:** `pg_database_size=9,306,112` bytes; `sw_ops.schema_migration` heap = 8,192 bytes; total ledger relation including indexes = 49,152 bytes. Exactly one eligible row exists: version 1, name `foundation`, checksum NULL. Its composite row size is 48 bytes; the proposed checksum is 64 ASCII hex characters. No index is defined on `checksum_sha256`.

**Exact intended logical change:** set only `sw_ops.schema_migration.checksum_sha256` for that one eligible row to `d4f874f71eb53a961fd3abe87a9342d0354a006ef04575158d2c72937dbe6aa8`. Use the guarded transaction in `db/proposals/0003_legacy_checksum_adoption.sql`; it aborts unless exactly one row is updated and verifies the resulting value.

**Storage estimate (estimate, not a measured write):**
- Additional field payload: 64 bytes.
- Expected allocated database-size increase: **0 bytes**, because the table already occupies one 8 KiB heap page, the update does not add an index entry, and the new tuple is expected to fit in existing page space.
- Conservative allowance: **0–8,192 bytes** (one additional 8 KiB heap page if page space is unexpectedly insufficient).
- Projected database size: **9,306,112 bytes expected; no more than 9,314,304 bytes under the one-page allowance** (9.306–9.314 MB decimal; approximately 8.875–8.883 MiB).
- This estimate excludes WAL/provider billing metrics and cannot guarantee physical storage accounting. Re-measure `pg_database_size`, ledger relation sizes and provider logical-size metric after any approved operation; compare actual values with this range.

**Transaction/rollback:** the guarded proposal is one transaction. Before COMMIT, any guard or verification failure rolls back the entire update. After a successful commit, a compensating change to NULL would require a separately reviewed and explicitly approved operation; do not automatically reverse it. The proposal is idempotency-safe by failing closed on a second run.

**Approval boundary:** this operation is prepared only. No production write has been made. The user must explicitly approve this exact one-row Neon checksum update before execution. Migration 0002, schema fingerprinting, seeds and all other changes are excluded and require their own separate approval.
