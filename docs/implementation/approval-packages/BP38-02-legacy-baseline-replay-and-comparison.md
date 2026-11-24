# BP38-02 — Independent Legacy Baseline Replay and Comparison

**Status:** Comparator implemented on `main`; independent disposable replay and drift-detection CI PASS (run [45434212975](https://github.com/Joshuaogri/saltwater/actions/runs/45434212975)); live reference-vs-Neon comparison NOT RUN.  
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

## Adoption gate

No checksum adoption is included. After the full comparison and supplementary review pass, prepare a separate exact, conditional one-row update for `version=1`, `migration_name='foundation'`, and `checksum_sha256 IS NULL`. Present the exact SHA-256, statement, row-count guard, expected storage effect and rollback considerations for explicit user approval. Migration 0002 remains a distinct subsequent operation requiring separate approval.


## CI evidence — 2026-11-24

Workflow run [45434212975](https://github.com/Joshuaogri/saltwater/actions/runs/45434212975) passed all steps. It created independent PostgreSQL 18 reference and target databases, replayed exact migration 0001, confirmed the comparator accepts matching schema/canonical world data, deliberately introduced a target-only schema change and confirmed that the comparator rejects the drift, then ran the migration-runner and runtime-kernel tests. The CI comparison is disposable-only; it does not connect to Neon and is not evidence that the live Neon baseline matches the replay. See [BP38-02 run 0001](../test-evidence/BP38-02-run-0001.md).
