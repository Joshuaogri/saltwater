# Saltwater technical architecture (initial)

**Status:** Initial implementation baseline; subject to revision as requirements are tested.

## System responsibilities

| Component | Responsibility |
|---|---|
| ChatGPT | Primary player interface, narration, command interpretation and AI-assisted development |
| Neon PostgreSQL | Authoritative persistent simulation state and structured history |
| GitHub | Source code, SQL migrations, tests, architecture decisions and operational documentation |
| Maps/graphics | Supporting presentation; never the source of truth for simulation facts |

## World constraints

- The country and city are both named Saltwater.
- Saltwater is an independent sovereign city-state.
- The playable world contains one city only.
- The hard ceiling is 10,000 living residents. A new resident may only be added when a place is available under the population rules.
- Text is the primary interface. Maps and a limited number of diagrams/illustrations support navigation and comprehension.
- The police service receives the deepest simulation. Other institutions and society are modelled sufficiently to support credible police work and interconnected cases.

## Data design

1. Use relational tables for stable, shared facts and high-value relationships.
2. Use integer surrogate keys for frequently referenced internal records where this is space-efficient.
3. Keep names, descriptions and other meaningful content intact; compact IDs must not obscure identity.
4. Store changes as timestamped events where event history is useful. Do not event-source every trivial field by default.
5. Use JSONB only for genuinely variable event attributes, not as a substitute for a relational model.
6. Avoid duplicate copies of the same document or payload; use references and content hashes where appropriate.
7. Add indexes in response to query needs and measured plans; indexes consume storage.
8. Consider partitioning, archival compression and binary encodings only after representative data and query patterns exist.
9. Maintain provenance, chronology and recoverability for cases, evidence and institutional decisions.

## Storage measurement policy

Every import, bulk insert, migration carrying data, file upload or other material data load must have a ledger entry. Record, when measurable:

- original input bytes and MB;
- compressed input bytes and MB;
- submitted payload bytes and MB;
- database size before and after;
- net database growth;
- compression ratio/savings;
- operation result and duplicate/recovery checks.

Use decimal MB (1 MB = 1,000,000 bytes) consistently in reports. Distinguish transfer size from PostgreSQL storage growth. If a measurement is unavailable, mark it **not measured**; never invent it. Schema-only migrations must also be logged as operations, with database size deltas measured where practical.

A successful live connection probe and a read-only SQL inspection verified the production branch on 2026-11-23. Direct PostgreSQL measurement returned `pg_database_size(current_database()) = 9,306,112 bytes` (9.306 MB decimal; 8.875 MiB) and 188,416 bytes of user relations. The database contains five user tables (three in `sw_core`, two in `sw_ops`); `world_config` contains the single Saltwater world row, while `event_type` and `simulation_event` are empty. Provider-reported logical-size metadata around 33.6 MB is a different metric and must not be conflated with `pg_database_size`. Keep timestamp, method and metric with every baseline; unknown is not zero.

## Security

- Never commit database URLs, passwords, API keys or tokens.
- Use GitHub Actions repository secret `DATABASE_URL` for CI jobs that require database access.
- Do not print secrets in logs or expose them in job output.
- Public source code must contain no credentials or private player data.

## Current implementation boundary

## Current implementation boundary

- Foundation migration 0001 is deployed. It created the `sw_core` and `sw_ops` schemas, world configuration, event type/event tables, migration ledger and storage-operation ledger.
- The foundation migration includes the one Saltwater world configuration row. It does not create residents, police personnel, businesses, crimes, cases, exhibits or evidence records.
- The current production database has five user tables; no domain simulation schemas or production seed data have been loaded.
- The repository contains SQL migrations, benchmark fixtures, GitHub Actions workflows and specifications, but no executable game runtime/application code yet.
- Storage benchmarks 0001–0008 and the narrative fixture are test assets, not production simulation data. Benchmark 0005 created a temporary synthetic schema in Neon and removed it after measurement; its operation-ledger entry remains.
- Benchmark 0008 passed three repeatability runs on disposable PostgreSQL. This does not approve the 1 GB Neon capacity; production seeding remains blocked pending narrative-quality sign-off and a final capacity/reserve assessment.
- All future Neon-changing operations remain subject to a fresh baseline, a measured/credible incremental estimate, explicit user approval and post-operation measurement.
