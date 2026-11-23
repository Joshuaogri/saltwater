# Neon + GitHub integration

This repository uses the Neon project Saltwater (misty-breeze-20463094) and its default production branch.

## Pull-request database branching

Workflow: .github/workflows/neon-pull-request-branches.yml

- Each pull request creates or reuses saltwater-pr-<number> from production.
- Only migrations absent from sw_ops.schema_migration are applied.
- The preview database is checked against Saltwater's canonical world invariants.
- Closing the pull request deletes only that pull request's preview branch.
- Preview changes do not modify production.

## Production migration deployment

Workflow: .github/workflows/neon-production-migrations.yml

- Runs when migration files change on main, or when manually dispatched.
- Uses the repository Actions secret DATABASE_URL for the production connection.
- Uses the migration ledger to skip versions already applied.
- Serialises production migration runs to prevent overlapping deployments.
- Uses the GitHub Environment named production. Configure required reviewers in GitHub repository Settings > Environments > production if manual approval is desired before production writes.

## Required GitHub Actions configuration

In GitHub repository Settings > Secrets and variables > Actions:

| Name | Type | Value |
|---|---|---|
| NEON_API_KEY | Secret | Neon API key with permission to create and delete branches in this project |
| DATABASE_URL | Secret | Connection string for the Neon production branch |
| NEON_PROJECT_ID | Variable (optional) | misty-breeze-20463094 |

The workflows include the known project ID as a fallback, so the variable is optional. Do not commit credentials or paste connection strings into source files.

The Neon GitHub App integration can create the NEON_API_KEY secret and NEON_PROJECT_ID variable automatically. If those are not present, connect the Neon GitHub integration for this repository in the Neon Console, or add the values manually.

## Migration contract

- Migration files live in db/migrations/ and use a zero-padded numeric prefix, e.g. 0002_add_person_records.sql.
- Every migration must record its own version in sw_ops.schema_migration within the same transaction as its schema changes.
- Migrations must be safe to run once and must not insert simulation seed data unless that data has been separately approved and measured.
- Never edit an already-applied migration; add a new numbered migration.
- PR preview databases are created from production and inherit its already-applied migration ledger.

## Current live baseline

Verified against Neon on 2026-11-22:

- Project: Saltwater
- Project ID: misty-breeze-20463094
- Branch: production (br-bitter-rain-bdz9ddid)
- Branch state: ready
- Database: neondb
- Foundation migration: version 1, foundation, recorded at 2026-11-22 17:11:30 UTC
- Logical database size reported by Neon: 33,595,392 bytes (approximately 33.6 MB)

No simulation seed data was added during this integration work.


## Direct live SQL verification — 2026-11-23

A read-only query against production branch `br-bitter-rain-bdz9ddid`, database `neondb`, confirmed:

- Foundation migration version 1 (`foundation`) is recorded in `sw_ops.schema_migration`, applied at 2026-11-22 17:11:30 UTC.
- `pg_database_size(current_database())`: **9,306,112 bytes** (9.306 MB decimal; 8.875 MiB).
- User relation footprint: **188,416 bytes**.
- Five user tables: `sw_core.world_config`, `sw_core.event_type`, `sw_core.simulation_event`, `sw_ops.schema_migration`, `sw_ops.storage_operation`.
- `world_config` contains one Saltwater row (one playable city; 10,000-person cap); `event_type` and `simulation_event` contain zero rows.
- No resident, police, business, case or evidence domain tables or production seed records are present.

The provider-reported logical-size metadata (approximately 33.6 MB in the 2026-11-22 project metadata) is a distinct metric from the SQL `pg_database_size` reading above. Do not treat the two as interchangeable.

The live connection probe workflow succeeded on 2026-11-22. It created a temporary table, inserted/read one test row, and rolled back; it left no persistent simulation data.

Benchmark 0005 did create a temporary synthetic benchmark schema/data set on Neon for measurement, then dropped that schema. Its successful operation record remains in `sw_ops.storage_operation`; the synthetic benchmark tables and rows do not remain. Later text-depth/high-entropy runs 0006–0008 were run on disposable PostgreSQL and did not load benchmark data into Neon. None of these runs loaded production population/business/police/case/evidence seed data.

**Current gate:** Neon 1 GB production capacity is NOT APPROVED; production seeding remains BLOCKED. Benchmark 0008's three repeatability runs are not a narrative-quality approval or a Neon capacity approval. The 16-record narrative fixture's manual-review rows remain pending.
