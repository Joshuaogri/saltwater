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
