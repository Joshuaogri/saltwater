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

## Current database-integrity implementation

BP38-01 is implemented on `main`; disposable PostgreSQL validation passed in [run 45428332686](https://github.com/Joshuaogri/saltwater/actions/runs/45428332686). BP38-02's independent PostgreSQL 18 replay and live baseline comparison passed in [run 45437263676](https://github.com/Joshuaogri/saltwater/actions/runs/45437263676). The guarded version-1 checksum adoption was separately approved, executed and verified. Migration 0002 was then separately approved and applied to Neon production on 2026-11-24. Both constraints and the fingerprint column are present; the authoritative ledger now contains versions 1 and 2 with exact source checksums, and version 2 has a recorded live schema fingerprint. The new [read-only Neon migration-ledger workflow](.github/workflows/neon-migration-ledger-readonly.yml) ran the committed Python migration runner against production with server-enforced read-only mode; checksum and live fingerprint verification passed in [run 45444735686](https://github.com/Joshuaogri/saltwater/actions/runs/45444735686). The migration source is 726 bytes; database size remained 9,306,112 bytes (0-byte measured delta). See [BP38-01 migration 0002 execution evidence](docs/implementation/test-evidence/BP38-01-run-0002.md). The push-triggered Neon production deployment workflow remains disabled; the new workflow is read-only and never applies migrations.

Package: [BP38-01 — Database Integrity and Migration Foundation](docs/implementation/approval-packages/BP38-01-database-integrity-and-migration-foundation.md). [Read-only Neon legacy-baseline verification](docs/implementation/test-evidence/BP38-01-legacy-baseline-read-only-verification.md).


## Repository layout

- `db/migrations/`: ordered PostgreSQL migrations.
- `docs/architecture/`: architecture decisions and storage design.
- `docs/operations/`: operational procedures and measurement records.
- `docs/implementation/`: dependency-led implementation sequence and delivery gates.
- `.github/workflows/`: automated checks.

## Current status

The **platform foundation is deployed; the simulation runtime and domain systems are not yet implemented**.

- Neon project: Saltwater (`misty-breeze-20463094`), production branch `br-bitter-rain-bdz9ddid`, database `neondb`.
- Foundation migration `0001_foundation.sql` and migration `0002_migration_integrity.sql` are applied and recorded as versions 1 and 2.
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
- The approved BP38-01 migration writes are complete; no operational geography import or simulation seed data has been authorised or performed.

## Detailed map and road network — SW-GEO-V1

- [Open the master Saltwater map (SVG)](docs/maps/saltwater-master-map-v1.svg)
- [Machine-readable geography and routable road graph](data/geography/saltwater-geography-v1.json)
- [Map register, network specification and limitations](docs/maps/README.md)

The initial map baseline contains 8 districts, 24 neighbourhoods, 42 named roads, 367 junction nodes, 685 connected road/bridge segments and 5 named route definitions. It uses the fictional `SW-LOCAL-01` metre grid. Structural graph checks passed at generation time; parcel/address/building coverage and full BP-02 operational acceptance remain outstanding. This is planning-grade fictional geometry, not survey-grade, and no Neon production data was changed.


## Core universal naming standard — SW-UNS-001

**Adopted 2026-11-24 as a core, mandatory Saltwater foundation.** The standard applies to all 44 blueprint divisions and every named entity: people, roads, places, properties, buildings, businesses, organisations, police units, vehicles, equipment and operational records. One shared registry must enforce permanent entity IDs, globally unique canonical names, normalization, exact/near-duplicate checks, reservations, concurrency safety, aliases and immutable historical name records. The sole user-approved exception allows the sovereign territory and playable city to both retain the exact name Saltwater, with separate IDs; no other entity may use that name. Domain-specific naming vocabularies are allowed; domain-specific bypasses or competing registries are not.

- [Read SW-UNS-001 — Universal Naming Standard](docs/blueprint/decisions/SW-UNS-001-universal-naming-standard.md)
- Existing adopted names must be preserved and registered before new names are generated, including the eight districts, 24 neighbourhoods and 42 named SW-GEO-V1 roads.
- Policy adoption is complete. SW-NAM-001 is approved; core disposable SQL/Python/PostgreSQL acceptance passed in runs `45409845359` and `45410340222`. Final storage-detail run `45411243093` passed. Populated registry relations total 12,279,808 bytes (4,546,560 heap; 7,643,136 indexes; 90,112 TOAST/auxiliary). No Neon production changes were made or authorised.

### Universal naming implementation

The adopted core naming policy is being implemented through [SW-NAM-001 — Universal Naming Registry, Generator and Enforcement](docs/implementation/approval-packages/SW-NAM-001-universal-naming-registry-generator-and-enforcement.md). Committed slices include disposable proposal `0009`, Python normalization/registry and transactional PostgreSQL adapter, deterministic candidate generation, geography/person adapters, dry-run canon inventory, immutable generator manifests, SQL/Python/concurrency/rollback/restore tests and disposable PostgreSQL CI. **Core regression and disposable identity mapping are verified**: full Python and PostgreSQL jobs passed in [run 45441551968](https://github.com/Joshuaogri/saltwater/actions/runs/45441551968), including all 100 geography identity-map entries and naming reservations, 10,000-person cap boundary, access controls, checkpoint-manifest capture and backup/restore. The full 10,000-person fixture grew its disposable database by 2,334,720 bytes (2.226562 MiB); full database size was 32,250,903 bytes. At the full fixture stage, 10,111 name reservations occupied 8,642,560 bytes total (854.77 bytes/reservation). Detailed heap/index/TOAST figures and the restore manifest are in [SW-NAM-001 run evidence](docs/implementation/test-evidence/SW-NAM-001-run-0001.md). The checkpoint validator intentionally remains partial: business-minimum, player-absence-freeze and permission/hidden-truth gates were not executed. BP-04 and other operational entity adapters remain NOT CONNECTED until their authoritative schemas exist. The 100-entry identity map is validated only in disposable PostgreSQL; no operational canon import, production spatial-ID allocation or Neon seed/write occurred. See [SW-NAM-001 integration coverage audit 0001](docs/implementation/test-evidence/SW-NAM-001-integration-coverage-audit-0001.md) for connected/NOT CONNECTED domain coverage.


## BP40-02 — stable player command catalogue and typed parser

The user approved BP40-02 on 2026-11-24. The implementation is committed directly to `main`: [canonical catalogue/parser](runtime/player_commands.py), [player command interface](runtime/player_interface.py), authorization gateway, trusted host adapter and ChatGPT tool handler all use the same parser and command metadata. The registry contains the existing fourteen command forms only; no new police-domain capability or permission was added. Typed parse failures distinguish empty, malformed, unknown, missing-argument, invalid-argument-count and invalid-value input. Help and [machine-readable tool schema](docs/integration/player-command-tool.schema.json) expose the same contract. The full Python regression, dedicated parser acceptance, full disposable PostgreSQL regression and database migration validation passed; see [BP40-02 run 0001 evidence](docs/implementation/test-evidence/BP40-02-run-0001.md). The registry and parse-result structures are immutable. No Neon production change occurred.


## SW-DB-001 — canonical world provisioning (approved; disposable implementation in progress)

The user approved SW-DB-001 on 2026-11-24 for GitHub main development and disposable PostgreSQL testing only. [Proposal 0010](db/proposals/0010_canonical_world_provisioning.sql) extends the existing universal naming registry with a business adapter and adds business-owned identity/lifecycle history plus immutable provisioning-batch metadata. The deterministic [opening fixture](tests/pkg001/sw_db_001_world_fixture.sql) targets 9,000 resident-cohort people + 500 police-subset-cohort people = 9,500 distinct living identities, leaving 500 headroom, and 10,000 distinct named businesses. The police subset and business category/legal-form/staff-band variety are test-only labels; no police appointments or detailed geography are fabricated, and business sites remain unassigned. [Manifest](data/fixtures/sw-db-001-opening-manifest.json) and [candidate model](docs/architecture/SW-DB-001-canonical-world-data-model.md) document the boundaries. The [dedicated disposable workflow](.github/workflows/sw-db-001-disposable.yml) will run regression, capacity, idempotency, performance and backup/restore tests. Results are pending in [SW-DB-001 run 0001 evidence](docs/implementation/test-evidence/SW-DB-001-run-0001.md). **No Neon production connection or write is authorised or performed by this approval.**
