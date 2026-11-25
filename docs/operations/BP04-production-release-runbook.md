# BP04 production release runbook

**Status:** archive-only release validated on disposable PostgreSQL 16 and 18; production remains restored to its pre-release baseline.
**Target:** Neon project `misty-breeze-20463094`, current production branch `br-still-cloud-bdvaw8u4`, database `neondb`.
**Source of truth:** this repository's `main` branch only.

## Release contents

The BP04 production schema is now represented by ordered migrations `0003`–`0012` under `db/migrations/`. The original `db/proposals/0013`–`0022` files remain as design/benchmark provenance. The disposable benchmark workflow applies the production migration files, not the proposals.

The importer `runtime/bp04_property_stack_importer.py` defaults to compressed archive-only mode. Targeting `neondb` requires the explicit `--allow-production` flag and `--expected-database neondb`; production typed-row expansion is explicitly rejected. The importer stores each original compressed source once and records its release and collection provenance. Its release ID is tied to the GitHub commit and package digest.

## Current verified source package benchmark

- 14 compressed datasets; 105 source collections; 1,950,923 source records.
- 1,422,202 typed-mapped rows; 19 archive-only collections; 3 partially mapped collections.
- 92 relational tables; zero cross-reference violations.
- Compressed source package: 29,434,820 bytes (29.43 MB / 28.07 MiB).
- Ten production migration files: 65,681 bytes; importer source: 68,115 bytes.
- Combined static release files: 29,568,616 bytes (29.57 MB / 28.20 MiB). Typed insert traffic and protocol overhead are additional.
- Disposable PostgreSQL 16 size: 627,792,919 bytes (627.79 MB / 598.71 MiB).
- Repeat import: zero inserts, updates or deletes; database size unchanged.
- Benchmark source package SHA-256: `54090f74332c1d0fedb09b48ad1fd669b9d62c593c9a5c253e979cbafaf4a3be`.

The production migration runner and importer were then tested together on both PostgreSQL 16 and 18 in successful workflow [45664193870](https://github.com/Joshuaogri/saltwater/actions/runs/45664193870), commit `9b4089fdd90e2eb996e166eb7ef667681a25c5ae`. Both versions applied migrations 0001–0012 through `scripts/migrate.py --apply`, passed schema acceptance, importer guard tests, all 14-source import and source-ledger acceptance, and repeat-import storage-stability checks. The package digest remained `54090f74332c1d0fedb09b48ad1fd669b9d62c593c9a5c253e979cbafaf4a3be`.

Measured full disposable database sizes including the foundation migrations:
- PostgreSQL 16: 628,120,599 bytes (628.12 MB / 599.02 MiB).
- PostgreSQL 18: 628,569,791 bytes (628.57 MB / 599.45 MiB).
- Repeat import on both versions: database size unchanged.
- PostgreSQL 18 is the closest benchmark for Neon, which runs PostgreSQL 18.7.

## Ordered migration sequence

1. `0003_bp04_compressed_source_archive.sql`
2. `0004_bp04_building_services_utilities.sql`
3. `0005_bp04_property_maintenance_repairs.sql`
4. `0006_bp04_property_security_access.sql`
5. `0007_bp04_property_valuation_tax.sql`
6. `0008_bp04_source_collection_mapping.sql`
7. `0009_bp04_business_operating_schedules.sql`
8. `0010_bp04_lawful_use_building_control.sql`
9. `0011_bp04_property_title_lifecycle.sql`
10. `0012_bp04_property_rights_boundaries.sql`

The migration runner `scripts/migrate.py` verifies contiguous versions, migration names, SHA-256 checksums and the live schema fingerprint. It takes a transaction-scoped advisory lock and applies each migration atomically. It refuses checksum drift, out-of-order application and legacy rows without checksums. Read-only verification now supports `--allow-pending`, so the production ledger workflow can report the prepared BP04 migrations without attempting to apply them.

## Production preflight and execution

Before production execution:

1. Confirm the current `main` commit and rerun the BP04 disposable benchmark. Confirm the package manifest and SHA-256 are the release values.
2. Take/verify a Neon restore point or backup and record the restore identifier.
3. Measure `pg_database_size`, user relation size, table/index/TOAST breakdown and free project storage on the production branch.
4. Verify migration ledger versions 1–2 and the live schema fingerprint with `python scripts/migrate.py --allow-pending`.
5. Confirm capacity for the measured disposable footprint plus operational headroom. The PostgreSQL 16 benchmark is an estimate, not a production guarantee.
6. Apply migrations from the repository root with `DATABASE_URL` bound to the intended Neon database: `python scripts/migrate.py --apply`.
7. Run the importer from the same pinned checkout: `python runtime/bp04_property_stack_importer.py --expected-database neondb --allow-production`.
8. Run `tests/pkg001/bp04_property_schema_acceptance.sql` and `tests/pkg001/bp04_property_import_acceptance.sql` against Neon, plus the source-ledger, row-count and cross-reference checks.
9. Repeat the importer once and verify zero row mutations and no material database growth.
10. Record before/after database bytes, relation bytes, table/index/TOAST sizes, elapsed time, release ID, source commit, source digest and migration checksums in the evidence log and README.

## Recovery behaviour

- A failed migration is rolled back atomically by the migration runner; the ledger row is written in the same transaction as the migration.
- A failed import rolls back its complete data transaction. The schema migrations remain applied and can be verified before retrying the same pinned import.
- Do not manually delete partially loaded rows or edit the migration ledger to force progress.
- If post-import acceptance fails, stop game use of BP04 and restore the verified pre-release Neon restore point; preserve logs and the failed release manifest for diagnosis.
- Re-importing the same package is designed to be idempotent, but this must be confirmed against production after deployment.

## Manual production release workflow

The manual-only workflow `.github/workflows/neon-production-migrations.yml` now performs the ordered migration, compressed dataset import, production acceptance and repeat-import storage check. It runs only from `main`, requires the exact confirmation `APPLY_BP04_TO_NEON`, requires a pre-release Neon restore-point reference, checks the exact package SHA-256 and targets only the database named `neondb`. It is not triggered by pushes and has not been run against production.

## Current production state

Read-only Neon measurement on 2026-11-25: database size 9,306,112 bytes (9.306 MB); five user tables; no `sw_property` tables. No BP04 production schema or data has been applied. Estimated post-import database size is approximately 628.57 MB (599.45 MiB) using the PostgreSQL 18 benchmark. Against the 9,306,112-byte live baseline, the estimated incremental database growth is approximately 619,263,679 bytes (619.26 MB / 590.58 MiB), subject to production measurement.

## Superseding compact-storage release procedure (2026-11-25)

The typed-row import procedure and 628 MB PostgreSQL 18 benchmark above are historical. They describe the previous representation and must not be used to estimate or execute the selected production release. The production upload was subsequently rolled back to the preserved Neon snapshot. The live production branch is now `br-still-cloud-bdvaw8u4` (`production`), and the database is back at 9,306,112 bytes with five user tables, migration versions 1–2, and no `sw_property` schema.

The selected BP04 release mode is now `--archive-only`. It stores the original 14 gzip datasets once and their provenance/count ledgers, without inserting any of the 1,422,202 mapped rows into the 92 domain tables. Runtime access uses `runtime/bp04_archive_reader.py`, which fetches one archived dataset, verifies its SHA-256, decompresses it in application memory, and expands the requested columnar collection. The original source archive remains lossless and authoritative. Domain tables stay empty for this static source import; dynamic gameplay state belongs in its own transactional records.

Both `.github/workflows/bp04-property-schema-disposable.yml` and the manual-only `.github/workflows/neon-production-migrations.yml` now invoke `--archive-only` and use `tests/pkg001/bp04_archive_only_acceptance.sql`. The production workflow still requires an explicit `APPLY_BP04_TO_NEON` dispatch and a fresh restore-point reference. This code change does not itself authorise or execute a Neon write.

The new storage target is the 29.43 MB compressed package plus PostgreSQL schema, TOAST, and provenance overhead. No projected final database size is to be stated as measured until the archive-only PG16/PG18 workflow completes. Production remains untouched at the 9.31 MB baseline.


## Verified archive-only storage benchmark — PostgreSQL 16 and 18 (2026-11-25)

The archive-only release workflow passed on both PostgreSQL 16 and PostgreSQL 18 in GitHub Actions run [45672135316](https://github.com/Joshuaogri/saltwater/actions/runs/45672135316), commit `a1836b83df980824a5291d7ed67b89cba5c624e9`.

| Measure | PostgreSQL 16 | PostgreSQL 18 (closest Neon benchmark) |
|---|---:|---:|
| Full disposable database size | 40,434,711 bytes (40.43 MB) | 40,875,711 bytes (40.88 MB) |
| Baseline before BP04 import | 9,306,112 bytes | 9,306,112 bytes |
| Incremental database growth | 31,128,599 bytes (31.13 MB) | 31,569,599 bytes (31.57 MB) |
| Compressed source package | 29,434,820 bytes (29.43 MB) | 29,434,820 bytes (29.43 MB) |
| `source_dataset_archive` relation | 28,368,896 bytes | 28,368,896 bytes |
| Typed rows permanently imported | 0 | 0 |
| Repeat-import size change | 0 bytes | 0 bytes |
| Repeat-import row mutations | 0 | 0 |

The import preserved all 14 archives, 105 source collections and 1,950,923 source records. The archive-only acceptance test passed on both PostgreSQL versions, and the second import left database size unchanged. Against the previous typed-row production growth of 616,505,344 bytes, the PostgreSQL 18 archive-only benchmark reduces incremental growth by approximately **94.88%** (about 19.5 times smaller).

The 31.57 MB figure is incremental database growth, not the final total size. Starting from the 9.31 MB production baseline, the closest PostgreSQL 18 benchmark indicates an approximately **40.88 MB total database** after an archive-only import. This remains a disposable benchmark, not a production measurement. Neon has not been written; production remains at 9.31 MB pending fresh explicit authorisation.


**Safe default:** the importer now defaults to `compressed_archive_only` even when no storage flag is supplied. The previous expanded representation is available only through the explicit `--typed-relational` option for disposable benchmarking; the importer itself rejects typed-relational mode when the target database is `neondb`. The production workflow also explicitly passes `--archive-only`.


## Actual Neon production deployment — 2026-11-25

The manual production workflow [45675735246](https://github.com/Joshuaogri/saltwater/actions/runs/45675735246) completed successfully on `main` at commit `625a75612dd760a8de7ef1362df1b23f61b23db1`. Both jobs and every deployment step passed, including ordered migrations, archive-only import, production acceptance and repeat-import idempotency/storage stability.

Read-only Neon verification after deployment:

- Production branch: `br-still-cloud-bdvaw8u4`.
- Migration ledger: versions 1–12; BP04 versions 3–12 all present.
- BP04 schema: 92 base tables.
- Archives: 14 datasets, 105 collections, 1,950,923 source records.
- Compressed archive bytes: 29,434,820; uncompressed source bytes: 558,602,287.
- Typed static source rows: 0; all 14 datasets and 105 collections have `archive_only` mapping status.
- Live `pg_database_size`: 41,525,248 bytes (41.53 MB / 39.60 MiB).
- Pre-release baseline: 9,306,112 bytes; measured increase: 32,219,136 bytes (32.22 MB).

This supersedes the earlier statements in this runbook that production remained at baseline or that no BP04 production writes had occurred. The archive-only production release is complete. It does **not** establish full BP04 division acceptance: canonical BP-02 address binding, gameplay-facing indexed lookups, complete cross-register acceptance and authorised police-facing access remain outstanding. See [BP04 full acceptance audit](../implementation/test-evidence/BP04-full-acceptance-audit-2026-11-25.md).

The archive-only release workflow is repeatable and storage-stable. Do not re-upload the package. No Neon writes were made during the audit or documentation update.
