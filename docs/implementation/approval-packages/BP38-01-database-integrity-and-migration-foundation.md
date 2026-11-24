# BP38-01 — Database Integrity and Migration Foundation

**Status:** IMPLEMENTATION IN PROGRESS — GitHub `main` only; disposable PostgreSQL validation pending  
**Approval:** User approved BP38-01 implementation on 2026-11-24.  
**Blueprint:** BP-38, fixed BP-01–BP-44 structure.  
**Database authority:** Neon PostgreSQL.  
**Production write authority:** NOT GRANTED by this package.

## 1. Objective

Implement the smallest reliable database-integrity foundation around the existing Saltwater schema. Reuse the current migration ledger and event/audit structures; do not create duplicate registries or a second database.

## 2. Approved implementation boundary

1. Deterministic, ordered migration discovery using four-digit versioned filenames.
2. SHA-256 checksums over the exact migration source bytes.
3. Explicit apply mode; default command is read-only verification.
4. PostgreSQL advisory lock to serialize concurrent migration runners.
5. One transaction per migration, including its ledger record.
6. Refuse unknown, missing, reordered, modified or checksum-less applied migrations.
7. Record a deterministic schema-catalogue fingerprint and detect live drift.
8. Validate the canonical schema with disposable PostgreSQL integration tests.
9. Keep migration credentials outside GitHub source and test workflows.
10. Preserve compact storage; add no duplicate migration/audit tables.

## 3. Existing structures reused

- `sw_ops.schema_migration`: existing ordered migration ledger.
- `sw_ops.storage_operation`: existing storage-operation ledger.
- `sw_core.simulation_event`: existing event history structure.

Migration 0002 strengthens `sw_ops.schema_migration` by requiring a valid SHA-256 checksum and adding an optional schema-fingerprint field. It adds no new table.

## 4. Legacy production baseline

The live production ledger contains migration 0001 with a NULL checksum. The new runner deliberately refuses to silently bless this row. A future production adoption step must independently verify the existing schema against the approved 0001 baseline, measure the exact database effect, and receive its own explicit production-operation approval.

No Neon production migration, data write, upload, credential change or schema mutation is authorised here.

## 5. Files delivered

- `scripts/migrate.py` — ordered migration runner; default read-only, explicit `--apply`.
- `db/migrations/0002_migration_integrity.sql` — checksum and schema-fingerprint ledger extension.
- `tests/database/test_migrate.py` — deterministic discovery and transaction-wrapper unit tests.
- `.github/workflows/database-validation.yml` — disposable PostgreSQL execution, idempotency, checksum-drift and schema-drift checks.

## 6. Acceptance tests

| ID | Acceptance condition | Evidence |
|---|---|---|
| BP38-01-AT-01 | Migration filenames are strictly ordered and contiguous | Unit test |
| BP38-01-AT-02 | SHA-256 uses exact source bytes | Unit test |
| BP38-01-AT-03 | Invalid filenames and version gaps are rejected | Unit tests |
| BP38-01-AT-04 | Only one outer transaction wrapper is accepted | Unit tests |
| BP38-01-AT-05 | Migration runner defaults to read-only verification | CLI contract and CI |
| BP38-01-AT-06 | Concurrent runners are serialized by advisory lock | Code review / integration |
| BP38-01-AT-07 | Migration and ledger update commit atomically | Disposable PostgreSQL |
| BP38-01-AT-08 | Re-running applied migrations is idempotent | Disposable PostgreSQL |
| BP38-01-AT-09 | Source checksum mismatch is rejected | Disposable PostgreSQL |
| BP38-01-AT-10 | Live schema drift is rejected | Disposable PostgreSQL |
| BP38-01-AT-11 | Legacy NULL checksums are not silently adopted | Explicit runner refusal |
| BP38-01-AT-12 | No production Neon write occurs | Production audit / no write action |

## 7. Execution and status

Implementation files are committed directly to `main`. GitHub Actions must complete the disposable PostgreSQL workflow before the slice is marked tested. A successful workflow proves only the disposable environment; it does not approve or apply anything to Neon production.

## 8. Exit criteria

BP38-01 can be marked verified only after:
- the complete workflow passes;
- checksum and live schema drift negative tests fail for the expected reasons;
- migration replay is idempotent;
- the final schema and migration ledger are inspected;
- the implementation register and README report the actual evidence;
- production remains unchanged.
