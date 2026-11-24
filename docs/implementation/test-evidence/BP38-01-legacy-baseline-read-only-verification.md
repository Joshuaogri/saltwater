# BP38-01 — Legacy Neon baseline read-only verification

**Date:** 2026-11-24  
**Target:** Neon project `misty-breeze-20463094`, branch `br-bitter-rain-bdz9ddid`, database `neondb`  
**Mode:** Read-only catalogue and data inspection; no DDL/DML or migration execution  
**Decision:** Baseline is structurally consistent with migration 0001 at the inspected catalogue level. Independent clean-replay equivalence is still required before checksum adoption.

## 1. Read-only controls

All production queries in this review were SELECT statements. No migration runner was connected to production. No production table, schema, ledger row, credential, setting or workflow was changed.

## 2. Migration ledger and canonical data

- Exactly one migration ledger row exists: version `1`, name `foundation`.
- `checksum_sha256` is NULL.
- `schema_fingerprint_sha256` does not exist.
- The canonical world row is `world_id=1`, country/city `Saltwater`, sovereign city-state true, population limit 10,000 and one playable city.
- `sw_core.event_type` and `sw_core.simulation_event` both contain zero rows.

## 3. Object inventory compared with migration 0001

The live `sw_*` inventory contains:

| Object | Live count | Expected from 0001 |
|---|---:|---:|
| Schemas | 2 | 2 |
| Tables | 5 | 5 |
| Identity sequences | 3 | 3 |
| Indexes | 10 | 10 |
| Constraints (including PostgreSQL NOT NULL constraints) | 42 | 42 |
| User-defined routines | 0 | 0 |
| Non-internal triggers | 0 | 0 |
| Row-security policies | 0 | 0 |

Schemas are `sw_core` and `sw_ops`.

Tables:
- `sw_core.world_config`
- `sw_core.event_type`
- `sw_core.simulation_event`
- `sw_ops.schema_migration`
- `sw_ops.storage_operation`

Identity sequences:
- `sw_core.event_type_event_type_id_seq`
- `sw_core.simulation_event_event_id_seq`
- `sw_ops.storage_operation_operation_id_seq`

All three sequences have start 1, minimum 1, increment 1, cache 1 and cycle disabled. The live columns, types, defaults, identity attributes, constraints and index definitions were inspected and correspond to the source migration. There are no additional `sw_*` tables, routines, triggers or policies in the returned catalogue inventory.

Both schemas and all five tables are owned by `neondb_owner`; schema/table ACLs are NULL (PostgreSQL default privileges). RLS and FORCE RLS are disabled. No `sw_*` default-privilege records were returned.

## 4. Existing storage-operation records

Two records exist:

1. Operation 1: successful `0001 foundation schema; no simulation data inserted`. Recorded database size before/after: 7,790,592 / 8,134,656 bytes; net 344,064 bytes.
2. Operation 2: successful synthetic lifecycle capacity benchmark 0005. Its notes identify a generated 54-table synthetic workload whose schema was removed after measurement. The record reports a 385,024-byte net database-size change during that operation.

These are operational provenance records, not people, police, business, case or evidence seed records. Their presence is not a schema mismatch; the storage-operation table is designed to retain history.

## 5. Source provenance

The current GitHub `main` file `db/migrations/0001_foundation.sql` was fetched successfully. Its Git blob SHA is `02d5f6bba150e8f277cd2aa9c34b4e9e9bb7856c`. A Git blob SHA is not the migration's SHA-256 checksum and must not be substituted for it. The exact source-byte SHA-256 still needs to be calculated by the repository's migration runner or an independent hashing command and retained in the replay evidence.

## 6. Current production measurement

- PostgreSQL: 18.7
- Database: `neondb`
- `pg_database_size`: 9,306,112 bytes
- Migration ledger: one row, version 1, checksum NULL
- No migration 0002 changes are present.

## 7. Outstanding verification before adoption

The inventory review is a strong structural consistency check, not a complete independent replay comparison. Before checksum adoption:

1. Replay the exact committed `0001_foundation.sql` bytes on a fresh disposable PostgreSQL instance.
2. Produce a normalized catalogue export from that clean replay.
3. Compare production and disposable exports across schemas, relation kinds, columns, types, defaults, identity/sequence definitions, constraints, indexes, ownership/ACLs, RLS, routines, triggers, policies, extensions and relevant database settings.
4. Compare canonical data separately, accounting for production-only operational history in `sw_ops.storage_operation` and the existing ledger row.
5. Calculate the exact source-byte SHA-256 independently and compare two implementations or tools.
6. Stop on any unexplained difference. Do not edit production to force a match.

Only after all comparisons pass should a one-row conditional checksum adoption statement be prepared for separate explicit approval. Migration 0002 remains a separate later operation, also requiring its own explicit approval and storage estimate.

**Conclusion:** Read-only structural inventory — PASS. Independent clean-replay equivalence — NOT YET RUN. Legacy checksum adoption — NOT AUTHORISED. Production changes — NONE.
