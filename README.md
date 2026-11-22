# Saltwater

Saltwater is a fictional sovereign city-state and a single-city police simulation.

## Canonical constraints

- Country and city: **Saltwater**.
- One sovereign city-state; no external playable cities or territory.
- Maximum population: **10,000 living residents**.
- Primary experience: exceptionally detailed text simulation, supported by maps and selected graphics.
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
- `.github/workflows/`: automated checks.

## Current status

Repository bootstrap is underway. Neon project creation and the GitHub `DATABASE_URL` secret were reported by the project owner. Neon project metadata reports a production-branch logical size of **33,611,776 bytes (33.61 MB / 32.05 MiB), measured 2026-11-22**. This is a provider-reported logical-size baseline, not a measurement from a live SQL query; live SQL connectivity has not yet been independently verified. No simulation data has been uploaded.
