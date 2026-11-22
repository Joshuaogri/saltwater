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

- Preserve meaningful detail and exact recoverability while minimising storage use.
- Normalise shared facts and reference them rather than duplicating them.
- Use compact identifiers where useful; never sacrifice human-readable records or provenance.
- Record meaningful state changes and chronology without indiscriminate full snapshots.
- Measure actual database growth; never substitute estimates for measurements.
- Do not upload simulation seed data until the schema, validation and storage baseline are ready.
- Never commit credentials. The Neon connection string belongs in a protected secret named `DATABASE_URL`.

## Repository layout

- `db/migrations/`: ordered PostgreSQL migrations.
- `docs/architecture/`: architecture decisions and storage design.
- `docs/operations/`: operational procedures and measurement records.
- `.github/workflows/`: automated checks.

## Current status

Repository bootstrap is underway. Neon project creation and the GitHub `DATABASE_URL` secret were reported by the project owner; this repository has not yet independently verified a live database connection. No simulation data has been uploaded, and the initial database storage baseline remains **not measured**.
