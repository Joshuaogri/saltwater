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

Neon project metadata reports a production-branch logical size of **33,611,776 bytes (33.61 MB / 32.05 MiB), measured 2026-11-22**. This is a provider-reported logical-size baseline, not a live SQL database-size query; live SQL connectivity has not yet been independently verified. Keep these measurements distinct. A blank or unknown measurement must never be reported as zero.

## Security

- Never commit database URLs, passwords, API keys or tokens.
- Use GitHub Actions repository secret `DATABASE_URL` for CI jobs that require database access.
- Do not print secrets in logs or expose them in job output.
- Public source code must contain no credentials or private player data.

## Current implementation boundary

This initial bootstrap does not create resident, police, crime, case or evidence seed data. Those domain schemas will be introduced in reviewed, ordered migrations after the foundational model and requirements are developed.
