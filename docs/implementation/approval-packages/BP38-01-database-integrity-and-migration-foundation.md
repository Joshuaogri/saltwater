# BP38-01 — Database Integrity and Migration Foundation

**Status:** IMPLEMENTED ON `main` — FINAL CODE REVIEW PASSED; BP38-02 baseline comparison and checksum adoption complete; migration 0002 production application plan prepared, awaiting separate approval  
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
7. Record a deterministic schema-catalogue fingerprint and detect drift within its explicitly defined catalogue coverage.
8. Fingerprint Saltwater (`sw_*`) schemas, including relations, columns, constraints, indexes, routines, triggers, row-security policies, schema/relation ACLs and routine ACLs.
9. Validate the canonical schema with disposable PostgreSQL integration tests.
10. Keep migration credentials outside GitHub source and test workflows.
11. Preserve compact storage; add no duplicate migration/audit tables.

## 3. Existing structures reused

- `sw_ops.schema_migration`: existing ordered migration ledger.
- `sw_ops.storage_operation`: existing storage-operation ledger.
- `sw_core.simulation_event`: existing event history structure.

Migration 0002 strengthens `sw_ops.schema_migration` by requiring a valid SHA-256 checksum and adding an optional schema-fingerprint field. It adds no new table.

## 4. Legacy production baseline

The live production ledger's version-1 `foundation` checksum was NULL during the initial BP38-01 rollout. BP38-02 subsequently completed an independent PostgreSQL 18 replay comparison and supplementary read-only catalogue review. The user explicitly approved the exact one-row checksum adoption; it was executed and verified. The production row now contains the exact committed 0001 SHA-256 `d4f874f71eb53a961fd3abe87a9342d0354a006ef04575158d2c72937dbe6aa8`. Database size remained 9,306,112 bytes (0-byte delta), and the ledger relation remained 49,152 bytes.

Migration 0002 remains unapplied. Its separate production application plan is [BP38-01 migration 0002 production application plan](BP38-01-migration-0002-production-application-plan.md). It specifies the exact DDL, live preconditions, advisory/table locking, transaction/rollback behavior, bounded session timeouts, storage estimate and postflight checks. No migration-0002 production write is authorised or performed by this package.

## 5. Files delivered

- `scripts/migrate.py` — ordered migration runner; default read-only, explicit `--apply`.
- `db/migrations/0002_migration_integrity.sql` — checksum and schema-fingerprint ledger extension.
- `tests/database/test_migrate.py` — deterministic discovery and transaction-wrapper unit tests.
- `.github/workflows/database-validation.yml` — disposable PostgreSQL execution, idempotency, legacy-checksum refusal, checksum-drift and schema-drift checks.
- `.github/workflows/neon-production-migrations.yml` — production push-triggered deployment disabled; no Neon connection is made by repository pushes.

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
| BP38-01-AT-11 | Legacy NULL checksums are not silently adopted | Disposable PostgreSQL negative test |
| BP38-01-AT-12 | Fingerprint detects drift in the catalogue categories it explicitly queries; it is not a universal PostgreSQL object/security fingerprint | Disposable PostgreSQL drift test |\n| BP38-01-AT-13 | No production Neon write occurs | Production audit / no write action |

The disposable proposals 0002 and 0009 no longer insert themselves into the authoritative migration ledger. A proposal fixture is not an applied source migration; only the ordered migration runner may write that ledger. This removes version-number collisions and keeps proposal execution separate from migration history.\n\n## 7. Fingerprint scope and exclusions

The current fingerprint is a deterministic hash of the catalogue query results in `scripts/migrate.py`. It covers the listed schema/relation/column/constraint/index/routine/trigger/policy categories and selected schema, relation and routine ACL fields. It does **not** claim to cover every PostgreSQL object or security property. In particular, it does not comprehensively encode enum labels, domain definitions, composite-type attributes, sequence parameters/state, column-level ACLs, default privileges, role memberships, ownership changes, extension configuration or all database-level settings. These are excluded from the current drift detector and must be included in a separate baseline comparison where relevant.

## 8. Execution and status

Implementation files are committed directly to `main`. Disposable PostgreSQL validation passed in [BP38-01 run 0001](../test-evidence/BP38-01-run-0001.md), GitHub Actions run [45428332686](https://github.com/Joshuaogri/saltwater/actions/runs/45428332686). All 17 workflow steps passed, including migration replay, checksum mismatch, schema drift, legacy NULL refusal, unit tests and existing runtime-kernel tests. A successful workflow proves only the disposable environment; it does not approve or apply anything to Neon production.

## 9. Exit criteria

BP38-01 can be marked verified only after:
- [x] the complete disposable workflow passes;
- [x] checksum, live schema drift and legacy NULL negative tests fail for the expected reasons;
- [x] migration replay is idempotent;
- [x] the final disposable schema and migration ledger are inspected by acceptance queries;
- [x] the implementation register and README report the actual evidence;
- [x] production remains unchanged;
- [x] final code review; scope limitations are documented.
- [x] independent PostgreSQL 18 clean-replay comparison and supplementary live Neon catalogue review completed under BP38-02.
- [x] separately approved version-1 checksum adoption executed and verified; measured database-size delta was 0 bytes.
- [x] exact migration-0002 production application plan prepared with live baseline and bounded storage estimate.
- [ ] separate explicit approval and execution of migration 0002 on Neon production.

Migration 0002 is not part of the completed checksum-adoption operation. BP38-01 repository implementation and disposable tests are complete; production migration execution remains a separate gate.
