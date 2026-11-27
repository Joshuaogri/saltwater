# BP-02 archive-only production release runbook

**Status: BP02 schema already present in production; SW-GEO-V1 archive insertion pending the guarded GitHub Actions run.** This procedure applies only the BP-02 source archive schema and one immutable source archive. It does not apply global migrations 0003–0012, promote operational geography, or change the global migration ledger.

## Current production state after explicit approval (2026-11-27)

A fresh read-only query after the user's explicit approval found that the independent BP02 schema migration had already been applied to production before this execution attempt. This assistant did not issue that schema write. The current state is:

- Database: `neondb`, PostgreSQL 18.7
- Production branch: `br-still-cloud-bdvaw8u4`
- Current database size: **9,879,552 bytes**
- BP02 migration ledger: one row, version 1, migration `0001_source_archive`, checksum `0801ca73441e3170df270d55747ca18ad3b2ede4937dec11c74b106b490c1850`
- BP02 archive rows: **0**
- Global migration versions: **1 and 2**, unchanged
- Recovery branch preserved: `br-gentle-moon-bdtc0y32`

The schema-only database increase relative to the earlier 9,781,248-byte baseline is **98,304 bytes**. The remaining disposable benchmark estimate for the archive insertion is **81,920 bytes**, projecting **9,961,472 bytes** after insertion. This is an estimate; the release workflow measures actual growth.

A manual-only workflow has been added on `main`: [BP02 archive-only production release](../../.github/workflows/bp02-production-archive-release.yml). It checks the migration checksum, archive digest, exact database baseline, recovery-point reference, PostgreSQL version and unchanged global migration ledger. It inserts only the immutable source archive, runs acceptance checks and verifies repeat-import idempotency. It requires the repository secret `DATABASE_URL` already used by the existing Neon production workflows. No production archive row has yet been inserted.

## Historical pre-release state (2026-11-27)

Read-only query against Neon project `misty-breeze-20463094`, production branch `br-still-cloud-bdvaw8u4`, database `neondb`:

- PostgreSQL: 18.7
- Database size: **9,781,248 bytes**
- Application tables: 5
- Global ledger `sw_ops.schema_migration`: versions 1 and 2 only
- BP-02 ledger `sw_geo.bp02_schema_migration`: absent
- BP-02 archive table `sw_geo.source_archive`: absent

## Recovery-point verification (2026-11-27)

A read-only Neon control-plane check found one manual snapshot:

- Snapshot: `snap-calm-credit-bdfp5tog`
- Name: `Saltwater BP04 pre-production release 2026-11-25`
- Created: `2026-11-25T17:37:13Z`
- Source branch: `br-bitter-rain-bdz9ddid`
- The current production branch metadata identifies this snapshot as its restore source.
- The snapshot's source branch is no longer present (Neon returned branch-not-found when inspected).
- The current production branch has no automatic snapshot schedule configured.

This confirms a historical pre-production snapshot exists and was used to establish the current production branch. A fresh manual snapshot attempt on 2026-11-27 was rejected by Neon with `snapshots limit exceeded`; the existing snapshot was not deleted or replaced.

As a non-destructive alternative, a no-compute copy-on-write recovery branch was created directly from the current production branch:

- Recovery branch: `br-gentle-moon-bdtc0y32`
- Name: `BP02 pre-release recovery 2026-11-27`
- Parent production branch: `br-still-cloud-bdvaw8u4`
- Parent LSN: `0/FFB0F510`
- Parent timestamp: `2026-11-26T23:30:47Z`
- Created: `2026-11-27T00:35:27Z`
- State: `ready`
- Compute: none; compute time and data transfer both zero at creation

This is a fresh branch-level recovery point at the recorded parent LSN, not a Neon manual snapshot. The branch is currently no-compute, so SQL verification against it was unavailable without adding compute. Do not add compute or modify this recovery branch as part of the release. Preserve it until the release has been verified and the user authorises any cleanup.
- BP04 global migrations 0003–0012: still pending; do not apply as part of this release

## Tested storage envelope

PostgreSQL 18.7 disposable benchmark:

| Component | Measured growth |
|---|---:|
| BP-02 schema and independent ledger | 147,456 bytes |
| First 25,689-byte compressed archive insertion | 81,920 bytes |
| Total measured BP-02 delta | **229,376 bytes** |
| Identical migration and archive replay | **0 bytes** |

Provisional projection from the live baseline: 9,781,248 + 229,376 = **10,010,624 bytes**. This is a planning estimate, not a guarantee; confirm the actual database size after deployment.

## Mandatory release gate

Do not execute the following steps until the user explicitly approves the BP-02 production archive-only release. Immediately before approval/execution:

1. Re-run the read-only preflight queries below and confirm the baseline and absence of both BP-02 objects.
2. Confirm the Neon recovery/restore point and record its identifier/time. Do not assume a backup exists merely because the project is hosted by Neon.
3. Confirm the GitHub `main` commit and workflow evidence listed below.
4. Confirm the expected storage delta and projected total with the user.
5. Ensure the connection string targets the intended production project, branch and database.

## Read-only preflight SQL

```sql
SELECT current_database() AS database_name,
       current_setting('server_version') AS server_version,
       pg_database_size(current_database())::bigint AS database_bytes,
       to_regclass('sw_ops.schema_migration') AS global_ledger,
       to_regclass('sw_geo.bp02_schema_migration') AS bp02_ledger,
       to_regclass('sw_geo.source_archive') AS bp02_archive;

SELECT version, migration_name, checksum_sha256
FROM sw_ops.schema_migration
ORDER BY version;
```

Expected before deployment: database `neondb`, PostgreSQL 18.7, baseline near 9,781,248 bytes, global versions 1 and 2, and both BP-02 relations absent.

## Production execution (only after explicit approval)

Run both commands from the exact, clean GitHub `main` checkout being released. The importer command records `git rev-parse HEAD` as the source commit, avoiding the misleading `local-build` default. Set `DATABASE_URL` in the protected execution environment; never paste credentials into chat or commit them.

First apply the independent BP-02 schema migration:

```bash
python scripts/migrate_bp02.py \
  --apply \
  --expected-database neondb \
  --allow-production
```

Then insert the archive-only source package:

```bash
python -m runtime.bp02_geography_archive_importer \
  --apply \
  --expected-database neondb \
  --allow-production \
  --source-commit "$(git rev-parse HEAD)"
```

The independent migration runner verifies its own checksum ledger and never updates `sw_ops.schema_migration`. The importer is idempotent for the same release and checksum. A checksum mismatch for an existing release must stop the process for investigation; do not overwrite immutable archive data.

## Post-release verification

Run the BP-02 acceptance SQL and these read-only checks:

```sql
SELECT version, migration_name, checksum_sha256
FROM sw_geo.bp02_schema_migration
ORDER BY version;

SELECT release_code, archive_format, compressed_bytes,
       uncompressed_bytes, source_file_count, archive_sha256,
       release_scope
FROM sw_geo.source_archive;

SELECT version, migration_name
FROM sw_ops.schema_migration
ORDER BY version;

SELECT pg_database_size(current_database())::bigint AS database_bytes;
```

Confirm one BP-02 migration ledger row, one `SW-GEO-V1` archive row, source scope `SOURCE_ARCHIVE_ONLY`, the expected archive checksum, global migration history unchanged, and the final measured database size. Re-running the exact migration and importer should add zero bytes.

## Recovery and failure handling

- Both schema DDL and its BP-02 ledger insert are transactionally applied.
- Archive insertion is transactional and immutable. If it fails, fix the cause and retry the same release/checksum; do not edit or delete an existing archive row.
- If the schema migration succeeds but archive insertion fails, leave the empty archive table in place and retry the importer after investigation. Do not manually edit migration ledgers.
- If any unexpected schema, ledger, checksum or size result appears, stop and use the recorded Neon recovery point under the database owner's direction. Do not run ad hoc destructive SQL.
- This release does not deploy operational road, parcel, address, access-point or route records.

## Verified CI evidence

- [PostgreSQL 18.7 isolated BP-02 migration and storage benchmark](https://github.com/Joshuaogri/saltwater/actions/runs/45910227589) — passed.
- [Global migration validation after restoring the contiguous atomicity fixture](https://github.com/Joshuaogri/saltwater/actions/runs/45910255603) — passed.
- [PostgreSQL 16 archive regression](https://github.com/Joshuaogri/saltwater/actions/runs/45910168053) — passed.

**Production state note:** the BP02 schema is present as recorded above; the archive remains pending. The schema application was observed, not performed by this assistant. The new guarded workflow is the approved execution path for the remaining archive-only insert.
