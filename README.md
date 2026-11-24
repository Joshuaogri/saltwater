# Saltwater

Saltwater is a fictional sovereign city-state and a single-city police simulation.

## Canonical constraints

- Country and city: **Saltwater**.
- One sovereign city-state; no external playable cities or territory.
- Maximum population: **10,000 living people total**, police included; opening baseline 9,000 residents + 500 police = 9,500, leaving 500 unused headroom.
- Primary experience: exceptionally detailed, permanently text-first simulation; maps and selected graphics are optional.
- Primary simulation: the police service and its operations, supported by a credible, interconnected society.
- Persistent database: Neon PostgreSQL.
- Source, migrations and documentation: this GitHub repository.
- Player interface and AI partner: ChatGPT.

## Development principles

- Preserve meaningful detail and exact recoverability while minimising storage use; the simulation is text-first and narrative may be extensive.
- Prefer the smallest lossless representation (compact JSON, short keys/IDs/enums, normalisation, references and event/delta records); compress structure, never meaning.
- Avoid every unnecessary byte: duplicate payloads, repeated boilerplate, derivable fields, needless indexes/snapshots and oversized database blobs.
- HARD GATE: before every Neon migration, schema change, seed/import, bulk write or upload, calculate and show expected incremental bytes/MB, assumptions/range, current baseline and projected total; wait for explicit user approval. If the estimate is not credible, do not deploy—benchmark first.
- After approval, measure actual database/table/index/TOAST growth and compare it with the estimate.
- Normalise shared facts and reference them rather than duplicating them.
- Use compact identifiers where useful; never sacrifice human-readable records or provenance.
- Record meaningful state changes and chronology without indiscriminate full snapshots.
- Measure actual database growth after each approved deployment; report actual delta against the pre-deployment estimate.
- Do not upload simulation seed data until the schema, validation and storage baseline are ready.
- Never commit credentials. The Neon connection string belongs in a protected secret named `DATABASE_URL`.

## Repository layout

- `db/migrations/`: ordered PostgreSQL migrations.
- `docs/architecture/`: architecture decisions and storage design.
- `docs/operations/`: operational procedures and measurement records.
- `docs/implementation/`: dependency-led implementation sequence and delivery gates.
- `.github/workflows/`: automated checks.

## Current status

The **platform foundation is deployed; the simulation runtime and domain systems are not yet implemented**.

- Neon project: Saltwater (`misty-breeze-20463094`), production branch `br-bitter-rain-bdz9ddid`, database `neondb`.
- Foundation migration `0001_foundation.sql` is applied and recorded as version 1.
- A successful live connection probe verified a transactional read/write in a temporary table and rolled it back.
- Read-only SQL verification on 2026-11-23 measured `pg_database_size` at **9,306,112 bytes (9.306 MB / 8.875 MiB)** and user relations at **188,416 bytes**.
- The database currently has five user tables: three in `sw_core` and two in `sw_ops`. The single `world_config` row records Saltwater, one playable city and the 10,000-person cap; `event_type` and `simulation_event` contain zero rows.
- No resident, police-personnel, business, case or evidence domain schemas or production seed records are present. A first text command-interface layer now exists in `runtime/player_interface.py`; persistent player saves, canonical officer/career creation and the full game application are not yet implemented.
- GitHub Actions migration, database-validation, live-connection and storage-benchmark workflows are present. Benchmark 0005 briefly created a synthetic Neon benchmark schema and removed it after measurement; its operation-ledger record remains. No production simulation seed data remains.
- Three disposable PostgreSQL runs of benchmark 0008 measured approximately **651.779 MB** full-database and **642.728 MB** relations. This is repeatability evidence for the synthetic workload, not final capacity approval.
- **Neon 1 GB production capacity remains NOT APPROVED; production seeding remains BLOCKED.** The 16-record narrative fixture has passed automated structural checks, but its human-review rows remain pending and the fixture is not approved.
- The storage/write gate remains mandatory: before any proposed Neon migration, schema change, seed/import, bulk write or upload, measure the current baseline, estimate incremental bytes and MB/MiB with assumptions/range, show the projected total and wait for explicit user approval.

Provider-reported logical-size metadata (approximately 33.6 MB in the 2026-11-22 project metadata) is a different measurement from PostgreSQL `pg_database_size`; do not compare or substitute the two without an explicit metric definition.

## Latest canon decisions — 2026-11-24

- Adopted [SW-CANON-001 — Population Scope and Foundational Geography](docs/blueprint/decisions/SW-CANON-001-population-scope-and-foundational-geography.md).
- Population cap now has a closed distinct-person counting formula: usual residents ∪ persons physically present ∪ active Saltwater Police Service members; one person ID counts once. Opening target: 9,000 civilian residents + 500 police personnel = 9,500 unique people, 500 shared headroom.
- Foundational geography is fixed: one contiguous coastal island city-state, 12 km × 9 km fictional local grid, eastern harbour, eight districts and 24 neighbourhoods. Detailed map construction and routing validation remain implementation work.
- BP-02 and BP-03 updated; SW-DB-001 now references the adopted canon. BP-04 business distribution remains a separate open design item.
- No Neon production write or seed has been authorised or performed.
