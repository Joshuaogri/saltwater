# BP38-02 — live Neon verification run 0001

**Date:** 2026-11-24  
**Branch:** `main`  
**Workflow run:** [45437263676](https://github.com/Joshuaogri/saltwater/actions/runs/45437263676)  
**Result:** PASS — live comparison and supplementary read-only review completed

## Comparator result

The workflow replayed the exact committed `db/migrations/0001_foundation.sql` into disposable PostgreSQL 18 and compared it with the Neon production target.

- Migration source SHA-256: `d4f874f71eb53a961fd3abe87a9342d0354a006ef04575158d2c72937dbe6aa8`
- Migration source bytes: 3,775
- Reference schema SHA-256: `d7b439322b9a19ba09f45853a721dbebb84c3528e57af1010723c6c558160720`
- Neon target schema SHA-256: `d7b439322b9a19ba09f45853a721dbebb84c3528e57af1010723c6c558160720`
- Reference canonical world-config SHA-256: `a2440d507b53d31b4018be386592b5348f935527fb8d1830545cead056d1b53b`
- Neon target canonical world-config SHA-256: `a2440d507b53d31b4018be386592b5348f935527fb8d1830545cead056d1b53b`
- Schema DDL equality: **PASS**
- Canonical `sw_core.world_config` equality: **PASS**
- Neon target `default_transaction_read_only`: **on**

The comparison covers schema DDL in `sw_core` and `sw_ops`, plus canonical `world_config` data. Migration-ledger and storage-operation row values are intentionally excluded because they are installation-specific operational history.

## Supplementary catalogue review

The uploaded artifact `bp38-02-neon-read-only-verification` (1,492 bytes; artifact ID 14940194997) records:

- PostgreSQL 18.7; database `neondb`; measured `pg_database_size`: **9,306,112 bytes**.
- Five user tables and three identity sequences, all owned by `neondb_owner`; reported table ACLs are NULL and RLS is disabled/not forced on the listed relations.
- Sequence definitions are consistent with the foundation: smallint event-type sequence and bigint simulation-event/storage-operation sequences; the storage-operation sequence last value is 2, while the other two have no last value.
- Provider role memberships and the single `plpgsql` extension were enumerated.
- Selected settings were recorded, including TimeZone `GMT`, `row_security=on`, and the session-level read-only setting.
- At the time of this read-only workflow, the migration ledger contained exactly version 1, `foundation`, with `checksum_sha256=NULL`. The subsequently approved checksum-adoption operation is recorded below.
- Storage history contains the original foundation migration and the synthetic benchmark operation record; no simulation seed data is present.

These supplementary values describe the live installation and are not required to equal a clean disposable replay. No unexplained schema or canonical-data difference was reported. Provider-managed role memberships and settings are documented as baseline context, not modified.

## Interpretation and limits

The live comparison and supplementary inspection succeeded. The workflow itself was read-only against Neon; it performed no DDL/DML, migration, checksum adoption, seed, or configuration change. The later, separately approved checksum-adoption operation is recorded below.

## Subsequent production checksum adoption

The user explicitly approved the exact guarded update for version 1 / `foundation`. It executed successfully and a follow-up read-only query verified the exact committed migration-0001 SHA-256:

`d4f874f71eb53a961fd3abe87a9342d0354a006ef04575158d2c72937dbe6aa8`

Database size before and after: **9,306,112 bytes** (0-byte delta). Ledger heap: **8,192 bytes** before and after. Ledger total relation: **49,152 bytes** before and after.

Migration 0002 remains unapplied and requires its own separate explicit approval. Its production application plan is [BP38-01 migration 0002 plan](../approval-packages/BP38-01-migration-0002-production-application-plan.md).
