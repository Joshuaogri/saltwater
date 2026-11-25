# BP04 production release runbook

**Status:** production migration package prepared; production import not yet executed.
**Target:** Neon project `misty-breeze-20463094`, branch `br-bitter-rain-bdz9ddid`, database `neondb`.
**Source of truth:** this repository's `main` branch only.

## Release contents

The BP04 production schema is now represented by ordered migrations `0003`–`0012` under `db/migrations/`. The original `db/proposals/0013`–`0022` files remain as design/benchmark provenance. The disposable benchmark workflow applies the production migration files, not the proposals.

The importer `runtime/bp04_property_stack_importer.py` defaults to the disposable `saltwater_test` database. Targeting `neondb` requires the explicit `--allow-production` flag and `--expected-database neondb`. The importer stores each original compressed source once and inserts typed relational rows in one transaction. Its release ID is tied to the GitHub commit and package digest.

## Current verified source package benchmark

- 14 compressed datasets; 105 source collections; 1,950,923 source records.
- 1,422,202 typed-mapped rows; 19 archive-only collections; 3 partially mapped collections.
- 92 relational tables; zero cross-reference violations.
- Compressed source package: 29,434,820 bytes (29.43 MB / 28.07 MiB).
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