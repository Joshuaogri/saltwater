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

## BP04-03 — citywide terrain/obstacle survey coverage grid

SW-TERRAIN-SURVEY-GRID-001 divides the fictional 12 km × 9 km city planning extent into 432 500 m coverage cells. Each cell carries district/neighbourhood lineage, generated property/building candidate references, road/route candidate coverage, terrain/water intersections and explicit evidence gaps for elevation and physical obstacles. Cells are coverage-planning units, not parcels or physical assets. No terrain or obstacle facts, survey priority, passability or access are inferred. Workflow: .github/workflows/bp04-03-terrain-obstacle-survey-coverage-grid.yml.

## BP04-03 — detailed terrain and physical-obstacle register

The geometry-derived SW-TERRAIN-OBSTACLE-DETAIL-001 register (runtime/terrain_obstacle_detail_register.py) preserves source terrain polygons and adds planar area/perimeter, bounding boxes, centroids, boundary rings/edges, edge lengths/bearings, district/neighbourhood overlays and lineage-linked route-centreline intersections. Obstacle classes remain separately inventoried; classes without supplied source records are marked as coverage gaps, never asserted absent. No elevation, gradient, material, condition, passability, legal access or egress is inferred. Workflow: .github/workflows/bp04-03-terrain-obstacle-detail-register.yml. Generated artifact is read-only and is not an operational terrain/obstacle layer.

## BP04-03 — terrain, elevation and physical-obstacle source model

The read-only source model [SW-TERRAIN-OBSTACLE-001](runtime/terrain_obstacle_source_model.py) inventories terrain and physical-obstacle evidence without inventing missing facts. It recognises elevation surfaces, contours, spot elevations, terrain features, retaining structures, walls, fences, gates, drainage structures and natural/other barriers. Current SW-GEO-V1 supplies one terrain polygon (Central-Western Ridge) and no elevation surfaces, contours, spot elevations or mapped physical-obstacle records. This is a source-coverage statement, not proof that absent features do not exist. Elevation, vertical datum, gradient, obstacle dimensions/material/condition, traversal, accessibility, legal access and emergency egress remain null, unknown or not assessed. The 47 existing route-centreline/ridge intersections remain contextual only. No operational terrain/obstacle records, route approvals or Neon writes are created. Regression workflow: [BP04-03 Terrain and Physical Obstacle Source Inventory](.github/workflows/bp04-03-terrain-obstacle-source-inventory.yml).

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


## SW-DB-001 — canonical world provisioning (approved; disposable implementation verified)

The user approved SW-DB-001 on 2026-11-24 for GitHub main development and disposable PostgreSQL testing only. [Proposal 0010](db/proposals/0010_canonical_world_provisioning.sql) extends the existing universal naming registry with a business adapter and adds business-owned identity/lifecycle history plus immutable provisioning-batch metadata. The deterministic [opening fixture](tests/pkg001/sw_db_001_world_fixture.sql) targets 9,000 resident-cohort people + 500 police-subset-cohort people = 9,500 distinct living identities, leaving 500 headroom, and 10,000 distinct named businesses. The police subset and business category/legal-form/staff-band variety are test-only labels; no police appointments or detailed geography are fabricated, and business sites remain unassigned. Generator v2 creates deterministic pronounceable pseudowords, while the immutable batch manifest records source revision and separate person/business SHA-256 content checksums. [Manifest](data/fixtures/sw-db-001-opening-manifest.json) and [candidate model](docs/architecture/SW-DB-001-canonical-world-data-model.md) document the boundaries. The [dedicated disposable workflow](.github/workflows/sw-db-001-disposable.yml) passed both Python and PostgreSQL 16 jobs in [run 45456851773](https://github.com/Joshuaogri/saltwater/actions/runs/45456851773). It verified the 9,500-person/10,000-business fixture, 10,000 unique business names, 0-byte same-manifest repeat delta, both restored content checksums, backup/restore, 9,999-person concurrent final-slot admission, exact 10,000 cap and world tick 0. Proposal 0010 schema growth was 278,528 bytes; the opening fixture added 39,632,896 bytes (37.796875 MiB) in 169.295 seconds (115.18 fixture rows/second). Person-domain relations totalled 5,259,264 bytes (553.61 bytes/person); business-domain relations 4,399,104 bytes (439.91 bytes/business). Full measurements and limitations are recorded in [SW-DB-001 run 0001 evidence](docs/implementation/test-evidence/SW-DB-001-run-0001.md). This is disposable test evidence only: no Neon production connection, migration, seed, import, upload or configuration change occurred; production write authority remains NONE.


## BP04 — physical built-world records

[BP04-01 — Property, Building, Premises, Unit and Access-Point Identity Foundation](docs/implementation/approval-packages/BP04-01-property-premises-identity-foundation.md) is approved, implemented and verified on `main`. The corrected disposable PostgreSQL 16 workflow [run 45477359265](https://github.com/Joshuaogri/saltwater/actions/runs/45477359265) passed both Python regression and full disposable PostgreSQL acceptance. The corrected acceptance checks all three access-point creation-history rows, including the deliberately unnamed access point.

**BP04-02 — Deep Physical Asset and Space Profiles** is approved and implemented as a disposable-only candidate migration `0012_bp04_physical_asset_detail_profiles.sql`. It adds versioned typed profiles for all five physical identity types; provenance-rich measurements; building levels/components; premises rooms; utility systems; physical features; element-level condition assessments; defects; and knowledge-state assertions. Profiles and child records are append-only; revisions are additional effective-dated records. Its acceptance tests and workflow integration are committed on `main`; full Python regression and disposable PostgreSQL 16 acceptance passed in [run 45478587738](https://github.com/Joshuaogri/saltwater/actions/runs/45478587738). The completed run applied proposals 0002–0012, measured migration-only schema growth, provisioned and measured the deterministic fixture, passed BP04-01 and BP04-02 SQL acceptance, verified idempotency, query latency and backup/restore, passed the concurrent final-slot population-cap test, and completed final SW-DB-001 reconciliation. Detailed byte-level step output was not exposed by the available workflow API response, so no new exact BP04-02 storage figure is asserted here. See [BP04-02 run 0001 evidence](docs/implementation/test-evidence/BP04-02-run-0001.md).

**Mandatory physical-record depth:** property, building, premises, unit and access point records must be extensive, structured and individually meaningful. Do not stop at IDs and names. Capture applicable classification/use, physical form, dimensions and measurement basis, floor/space structure, materials/components, utilities/services, facilities, condition by element, defects/hazards, accessibility, security/physical controls, access modes/restrictions, capacity/suitability, lifecycle and inspection/maintenance history. Every material fact must retain source/provenance, confidence/quality and recorded/effective chronology. Unknown, not assessed, not applicable, not present and measured zero must remain distinct. Use typed, normalised child records; do not collapse detail into unstructured notes or one oversized JSON field. Do not invent missing facts or false precision.

The detailed profile model does **not** populate the actual Saltwater property inventory, ownership/tenancy/occupancy, or business operators. No actual Saltwater property/building/premises/unit/access-point population has been seeded. BP04-02 passed full Python and disposable PostgreSQL 16 acceptance in [run 45478587738](https://github.com/Joshuaogri/saltwater/actions/runs/45478587738); see [BP04-02 run evidence](docs/implementation/test-evidence/BP04-02-run-0001.md). [BP04-03 — City Physical Inventory and Geography-Linked Population](docs/implementation/approval-packages/BP04-03-city-physical-inventory-and-geography-linked-population.md) was approved on 2026-11-24 for GitHub `main` implementation and disposable PostgreSQL testing only. Stage A's read-only geography audit is committed in [runtime/geography_readiness.py](runtime/geography_readiness.py), with regression tests in [test_geography_readiness.py](tests/pkg001/test_geography_readiness.py) and a dedicated [GitHub Actions workflow](.github/workflows/bp04-03-geography-readiness.yml). The audit checks the committed district/neighbourhood/road/network structure and keeps the 100 resolved stable source-to-entity_code mappings, absent parcel/address fabric and absent footprints/entrances explicit. It cannot approve BP-02 geography. The audit passed in [run 45480493889](https://github.com/Joshuaogri/saltwater/actions/runs/45480493889): 28/28 checks passed; all 100 source identities are mapped one-to-one to stable entity_code values; no spatial IDs were fabricated or assigned. See [BP04-03 Stage A run evidence](docs/implementation/test-evidence/BP04-03-stage-a-run-0001.md) and the [100-record reconciliation register](data/geography/bp04-03-stage-a-source-spatial-reconciliation-v1.json). Stage A structural audit is verified; all 100 source identity mappings are resolved to stable entity_code values. Database-specific spatial_id surrogates are resolved by entity_code at materialisation. Stage B now has a BP-02-owned candidate schema in [proposal 0013](db/proposals/0013_bp02_parcel_address_candidate.sql), with parcel profiles, structured address locators/frontage, parcel lineage, address aliases, kind guards, checksum verification and append-only controls. Its Python and disposable PostgreSQL acceptance passed in [run 45481959712](https://github.com/Joshuaogri/saltwater/actions/runs/45481959712); schema-only growth was 294,912 bytes and the proposal source is 10,668 bytes. See [Stage B run evidence](docs/implementation/test-evidence/BP04-03-stage-b-schema-run-0001.md). The schema foundation is verified. Stage B now also has a deterministic [parcel/block candidate generator](runtime/parcel_candidate_generator.py), five regression tests and a dedicated [candidate workflow](.github/workflows/bp04-03-parcel-candidates.yml). Run [45482818681](https://github.com/Joshuaogri/saltwater/actions/runs/45482818681) passed: 396 block-scale candidates across all 24 neighbourhoods; 36 water-conflict cells excluded; 392 road-edge matches and 4 frontage-unresolved candidates. The generated artifact is 11,656 bytes compressed and has manifest SHA-256 `6afc12c8e27717523bb581057da8c936481b1950faa5703f52bb5e7560e8cba4`; see [Stage B candidate evidence](docs/implementation/test-evidence/BP04-03-stage-b-parcel-candidates-run-0001.md). These are 500m planning block candidates, not final cadastral parcels. The generator was refined to calculate exact water polygon-to-cell intersection area for the current single-ring SW-GEO-V1 water polygons (Sutherland–Hodgman clipping); unsupported holes/geometry fail closed. Refined [run 45483557867](https://github.com/Joshuaogri/saltwater/actions/runs/45483557867) passed all 7 tests, retained 396 candidates / 36 excluded water cells / 392 road-edge matches / 4 frontage-unresolved, and emitted manifest SHA-256 `4da7999ef7b5f98b3b1214096f11fbce633317ae38585ca231f6f8131c3c39bf`. Its artifact is 11,815 bytes compressed: [candidate artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45483557867/artifacts/14962966036). Evidence: [Stage B candidate run 0001](docs/implementation/test-evidence/BP04-03-stage-b-parcel-candidates-run-0001.md). The generator now also validates candidate containment and pairwise interior overlap: 432 source grid cells reconcile to 396 candidates plus 36 water-excluded cells; zero candidate overlaps and zero out-of-neighbourhood candidates. Eight Python tests passed in [run 45483804394](https://github.com/Joshuaogri/saltwater/actions/runs/45483804394). Latest manifest SHA-256 `83ec53dc09f51483110e1e564b82919d2da63a0f5c5adcd92b42e04bf508f85f`; artifact size 12,033 bytes compressed: [artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45483804394/artifacts/14962257890). This validates generated candidate rectangles only, not cadastral topology. The 15m road-reserve inset remains provisional; the unallocated area is not classified as road, public space or developable land. Road access, land-use capacity and full parcel topology remain. No spatial IDs or canonical addresses were assigned; all 100 source identities are resolved to stable entity_code values; database-specific spatial_id surrogates are looked up during materialisation. No database or Neon production write occurred.


BP04-03 Stage B now imports the 396 generated candidate parcels into disposable PostgreSQL 16 through [the guarded importer](runtime/parcel_candidate_importer.py). [Run 45484639045](https://github.com/Joshuaogri/saltwater/actions/runs/45484639045) passed: 396 candidate identities, 396 checksummed geometry versions and 396 parcel profiles; zero address identities; repeat import inserted zero rows and had 0-byte database growth. First import added 1,187,840 database bytes in the disposable CI database (739.125 ms); proposal 0013 schema growth was 294,912 bytes and its SQL source was 10,668 bytes. Full [ingestion evidence](docs/implementation/test-evidence/BP04-03-stage-b-disposable-ingestion-run-0001.md). These are candidate records only; no operational geography approval, canonical addresses, or Neon writes occurred.


BP04-03 Stage C road-centreline and road-reserve design is now resolved and verified in [run 45487528624](https://github.com/Joshuaogri/saltwater/actions/runs/45487528624). Both bridge lengths now reconcile to 2,019.804m from their stored geometry. Fictional canonical standard SW-RDS-V1 defines 18m local streets, 24m district connectors, 30m primary arterials and 24m bridges. Deterministic geometry generated all 685 segment corridor polygons; zero width or bridge-length exceptions remain. The 42-road, 685-segment, 367-node network remains connected with zero degree/membership/endpoint mismatches. Segment polygons intentionally overlap at junctions and must be dissolved before unique reserve-area calculations. The preserved road register is 23,915 compressed bytes ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45487528624/artifacts/14962764058)); [full evidence](docs/implementation/test-evidence/BP04-03-stage-c-road-centreline-audit-run-0001.md).


BP04-03 Stage C parcel coverage area reconciliation passed in [run 45486168411](https://github.com/Joshuaogri/saltwater/actions/runs/45486168411). The 24 neighbourhoods total 108,000,000 m² (432 grid cells); 396 candidate parcel interiors total 87,476,400 m²; exact water intersections in 36 excluded cells total 5,740,000 m². The 14,783,600 m² unallocated balance is decomposed into 11,523,600 m² of provisional 15m inset residual and 3,260,000 m² non-water area inside water-hit cell envelopes. Area balance delta: 0 m². These residuals remain unclassified, not assumed to be roads or developable land. The per-neighbourhood audit is retained as a 1,713-byte compressed [workflow artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45486168411/artifacts/14964432302). [Full evidence](docs/implementation/test-evidence/BP04-03-stage-c-parcel-coverage-area-run-0001.md).


BP04-03 Stage C road-reserve dissolve and neighbourhood-boundary reconciliation passed in [run 45488230508](https://github.com/Joshuaogri/saltwater/actions/runs/45488230508). The 685 segment corridor polygons dissolve into one connected road-reserve geometry of 7,057,146.032 m²; 140,804.555 m² of duplicate junction overlap is removed. The dissolved reserve lies entirely inside the city boundary. All 24 neighbourhood polygons exactly partition the 108,000,000 m² city: zero overlap, zero gap, zero outside area. Neighbourhood road-reserve allocations sum to 7,057,146.032 m² with a 0 m² difference. The topology artifact is 9,850 compressed bytes ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45488230508/artifacts/14964976654)). [Full evidence](docs/implementation/test-evidence/BP04-03-stage-c-road-centreline-audit-run-0001.md). Next: regenerate parcel candidates against the dissolved fictional road-reserve and water geometry, replacing the provisional 15m inset.


**BP04-03 Stage D geometry-derived parcel candidates — supersedes the earlier 396-cell / provisional 15m-inset candidate layer:** [Disposable PostgreSQL run 45490203072](https://github.com/Joshuaogri/saltwater/actions/runs/45490203072) and [candidate regression run 45490210942](https://github.com/Joshuaogri/saltwater/actions/runs/45490210942) passed. The generator now subtracts the actual dissolved SW-RDS-V1 road reserve and mapped water geometry from each 500m source lineage cell, then splits the remaining land into deterministic valid polygon components. It creates **420** parcel candidates; **418** have a geometric road-reserve edge-contact candidate. The 36 water-intersected cells are no longer excluded wholesale. Area reconciles exactly: 108,000,000.000 m² = 7,057,146.032 m² road reserve + 5,605,030.589 m² water outside road reserve + 95,337,823.379 m² candidate land; delta 0 m² across all 24 neighbourhoods. Candidate manifest: 28,513 compressed bytes ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45490203072/artifacts/14965647916)). Disposable PostgreSQL inserted 420 candidate identities, 420 geometry versions and 420 parcel profiles; first-import growth 1,081,344 bytes. Repeat import inserted zero rows and produced 0-byte growth. Zero canonical addresses were created. The first generic labels tripped SW-UNS-001 near-duplicate checks; deterministic unique fictional names now pass through the existing registry without bypassing it. [Full Stage D evidence](docs/implementation/test-evidence/BP04-03-stage-d-geometry-derived-parcel-candidates-run-0001.md). Next: detailed parcel dossier and boundary/frontage review before detailed property/building/premises/unit/access-point inventory. No Neon writes or operational geography activation occurred.


**BP04-03 Stage D detailed parcel dossiers and relationship layer completed:** [Run 45494991970](https://github.com/Joshuaogri/saltwater/actions/runs/45494991970) passed all eight Python suites (41 tests), disposable SQL acceptance, candidate import, dossier import and repeat-import idempotency. All 420 parcel candidates have measured dossiers (area, perimeter, compactness, centroid, representative point, bounds, ring counts, road frontage and water contact). Results: 418 parcels require frontage review; 2 have no road-edge contact; 1,374 parcel-to-road frontage relationships and unreviewed access-location candidates; 100 shared-boundary relationships; 32 water-adjacent parcels and 32 water relationships. These are candidate geometric relationships, not legal frontage, entrances, addresses or operational access points. The five-table append-only dossier schema is proposal 0014; source 10,311 bytes, disposable schema growth 368,640 bytes. First dossier import growth 1,859,584 bytes; repeat import 0 bytes. The 68,438-byte compressed dossier artifact is [preserved here](https://github.com/Joshuaogri/saltwater/actions/runs/45494991970/artifacts/14968720668). [Full evidence](docs/implementation/test-evidence/BP04-03-stage-d-parcel-dossiers-run-0001.md). Next: full-depth property, building, premises, unit and access-point inventory, with BP04-02 physical profiles and provenance. No Neon writes or operational addresses/access points were created.


**BP04-03 Stage E physical-asset candidate generation — first successful slice:** [Run 45502416189](https://github.com/Joshuaogri/saltwater/actions/runs/45502416189) passed seven regression tests and generated 420 property-site candidates, 384 contained building-footprint candidates, 1,327 floor-level premises, 15,199 units and 768 unreviewed building-boundary access-location candidates. 36 candidate properties have no building footprint and remain sites without fabricated structures. The 10,981,615-byte manifest is preserved as a 356,640-byte compressed [artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45502416189/artifacts/14970964187); SHA-256 `b710fcc3f5d08d24154ede08ebf99ec6a2f099a08c7f9c5d310c93ddb8aa30fe`. All five record classes have deterministic identities/names and provenance; geometry tests confirm each building footprint lies within its property candidate. This is candidate generation only: no asset records have yet been imported into PostgreSQL, and generated access points are not operational entrances. No addresses, operational spatial IDs, ownership, tenancy, occupancy or business assignments were created; all 100 source records resolve to stable entity_code values (100 resolved, 0 unresolved). Production spatial_id surrogates remain unassigned until activation and are looked up by entity_code. Full [Stage E evidence](docs/implementation/test-evidence/BP04-03-stage-e-physical-asset-candidates-run-0001.md). Next: complete BP04-02 profile and typed child-record depth, then disposable PostgreSQL schema/import/idempotency/storage/restore acceptance. No Neon production writes occurred.


**BP04-03 Stage E full physical-asset inventory — verified:** [Disposable PostgreSQL 16 run 45504985010](https://github.com/Joshuaogri/saltwater/actions/runs/45504985010) passed 15 Python tests, proposal 0015 migration, full import/SQL acceptance, repeat-import idempotency, query measurements and PostgreSQL 16 backup/restore. The hierarchy contains **420 property-site candidates, 384 building candidates, 1,327 premises, 15,199 units and 768 unreviewed access-location candidates**. All five identity classes have **18,098 typed BP04-02 profiles** and the inventory includes **181,915 detailed child records**: 34,624 measurements, 1,327 building levels, 4,608 components, 3,981 room allocations, 37,979 utility records, 21,417 features, 22,533 condition assessments and 55,446 knowledge-state assertions. There are no fabricated defect records. Proposal 0015 source SQL is 9,238 bytes and disposable schema growth 303,104 bytes. First asset import growth was 130,441,216 bytes; repeat import inserted zero records and grew 0 bytes. Full compressed inventory artifact: 1,523,057 bytes ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45504985010/artifacts/14971474446)). [Full Stage E evidence](docs/implementation/test-evidence/BP04-03-stage-e-physical-asset-inventory-run-0001.md).

All records remain generated, non-operational candidates. No canonical addresses, operational spatial IDs, confirmed entrances, ownership, tenancy, occupancy or business assignments were created. All 100 source records now map to stable entity_code values; database spatial_id is generated per database and looked up by entity_code. No Neon production connection, migration, seed, upload or activation occurred. Next dependency is BP-02 geography approval/versioning and source-to-spatial reconciliation before operational parcel/address/entrance identity creation.


## Geography source-identity reconciliation correction (2026-11-24)

The earlier statement that 100 source-to-spatial mappings remained unresolved is superseded. All **100 source records now map one-to-one to stable `sw_geo.entity.entity_code` values**: 8 districts, 24 neighbourhoods, 18 landmarks, 5 routes, 3 geography zones and 42 roads. The exact source record, entity type/kind, canonical name and parent are checked against SW-GEO-V1 by `runtime/geography_identity_reconciliation.py`; the readiness workflow runs regression tests for full coverage, duplicate IDs, incorrect parents and missing records. The reconciliation register now reports 100 resolved and 0 unresolved source-identity mappings.

PostgreSQL `spatial_id` is a GENERATED ALWAYS AS IDENTITY surrogate, so its integer is database-specific and must be looked up using the stable `entity_code` in each database. The portable source manifest intentionally does not freeze a disposable integer as a production ID. This correction resolves source-to-identity mapping; it does **not** approve SW-GEO-V1 for operational seeding, create parcel/address/entrance geometry, or authorize Neon writes. Those separate geography quality and activation gates remain.


**Disposable database materialisation proof:** the existing PKG-001 geography identity SQL fixture has now materialised all 100 `sw_geo.entity` rows and their database-generated `spatial_id` values, with all 100 version/parent/name relationships and naming-registry activations accepted. The materialisation step passed in [workflow run 45508321133](https://github.com/Joshuaogri/saltwater/actions/runs/45508321133). These integers belong to that disposable database only; production IDs remain unassigned and will be generated/looked up by `entity_code` when the operational geography version is activated.


### SW-GEO-V1 geometric QA extension (read-only)

A dedicated standard-library geometry and routing audit is added at `runtime/geography_geometry_audit.py`, with regression coverage in `tests/pkg001/test_geography_geometry_audit.py`. It checks polygon ring validity/self-intersection, point containment, neighbourhood-to-district containment, neighbourhood interior overlap and area balance, segment geometry against node coordinates and declared lengths, city-boundary containment, graph degree/connectivity, and route segment sequencing. The existing BP04-03 geography-readiness workflow runs this audit on relevant `main` changes. The audit is deliberately read-only and always reports operational seed eligibility as false; it does not approve SW-GEO-V1, validate cadastral parcels, establish legal frontage/access, or authorize Neon writes. Acceptance passed in [run 45510749489](https://github.com/Joshuaogri/saltwater/actions/runs/45510749489): 18 Python tests (4 structural, 9 geometric/routing, 5 identity) passed; the structural audit passed 28/28 checks with 100 resolved/0 unresolved source identities; the geometric/routing audit passed 10/10 checks with zero failed checks. City and neighbourhood areas both measure 108,000,000 m²; all 24 neighbourhoods are contained by their assigned districts with no interior overlaps; 367 road nodes form one connected component across 685 segments, with zero endpoint/length, degree or route-sequence exceptions. Full [SW-GEO-V1 geometric QA run 0001 evidence](docs/implementation/test-evidence/SW-GEO-V1-geometric-qa-run-0001.md). This remains read-only planning-geometry QA; no operational geography approval, cadastral/address/entrance acceptance or Neon write occurred.


### BP04-03 independent parcel-dossier geometry QA (read-only)

A second, independent geometry audit now verifies the 420 geometry-derived parcel candidates and their dossiers against the source road-reserve and water layers. It checks parcel containment/non-overlap, road-reserve/water exclusion, complete frontage-to-road-segment geometry, frontage candidate points, unreviewed access-location candidates, water adjacency and the complete measured parcel adjacency register. Successful [workflow run 45511739957](https://github.com/Joshuaogri/saltwater/actions/runs/45511739957) passed 8 regression tests and all 10 audit checks: 420 valid parcel dossiers, 95,337,823.379 m² candidate land, zero interior overlap, 1,374 frontage candidates, 1,374 unreviewed access-location candidates, 100 parcel adjacency relationships and 32 water adjacency relationships, with zero geometry exceptions. The audit is read-only; it creates no canonical addresses or operational access points and does not approve cadastral or operational geography. Full [BP04-03 parcel-dossier geometry QA evidence](docs/implementation/test-evidence/BP04-03-parcel-dossier-geometry-qa-run-0001.md). Next: reconcile parcel frontage/access candidates with the 768 building-boundary access-location candidates, retaining candidate-only status.


### BP04-03 building access and point-contact road-connection reconciliation

The four building-boundary candidates previously left without frontage links are now resolved through two separately classified road-reserve proximity candidates. The affected parcels are `BPC-SWD04N1-004-02` and `BPC-SWD08N1-018-02`, with point-only contact to bridge roads `SWR-B2`/`SWS-0685` and `SWR-B1`/`SWS-0684`. These are not conventional linear frontages: the dossier preserves them as `POINT_CONTACT_ONLY` proximity candidates, and all four building access candidates link to the corresponding same-parcel candidate. No building candidate remains without a road-connection candidate.

The latest independent audits passed: [parcel dossier QA run 45516792963](https://github.com/Joshuaogri/saltwater/actions/runs/45516792963) passed 9 tests and 10/10 checks (420 parcels, 1,374 true frontage candidates and 1,376 access-location candidates); [building access reconciliation run 45516972156](https://github.com/Joshuaogri/saltwater/actions/runs/45516972156) passed 7 tests and 8/8 checks (768 building-boundary candidates, four point-contact links, zero unlinked); [direct connector feasibility run 45516793015](https://github.com/Joshuaogri/saltwater/actions/runs/45516793015) passed 6 tests and 7/7 checks (768 geometric lines feasible under property/building/water checks, zero blocked and zero unlinked). A geometric line is not a driveway, entrance, legal access or traversable/emergency route.

Disposable PostgreSQL validation also passed: [Stage B/Stage D run 45517627917](https://github.com/Joshuaogri/saltwater/actions/runs/45517627917) and [Stage E run 45516793086](https://github.com/Joshuaogri/saltwater/actions/runs/45516793086). Proposal 0016 adds the separate point-contact/nearest-edge candidate classification; its measured disposable schema growth was 24,576 bytes (2,586-byte SQL source). Dossier import growth was 1,933,312 bytes with zero repeat-import growth. Stage E physical asset import growth was 130,744,320 bytes with zero repeat-import growth; 18,098 identities/profiles, 181,915 details, 1,572 geometry candidates, 420 site links and 16,910 relationships were accepted. All 100 stable source entity-code mappings resolved; zero remained unresolved. No production Neon writes or operational access/address records were created. The read-only Neon size remains 9,306,112 bytes.

Full [four-candidate resolution evidence](docs/implementation/test-evidence/BP04-03-four-unlinked-building-access-candidates-resolution-run-0001.md). Continue to keep frontage and point-contact proximity distinct; never promote either candidate to an actual entrance, driveway, legal access or emergency route without separate evidence and review.


### BP04-03 persistent access connector candidates

Stage E now extends beyond boundary-point proposals to a separate, provenance-bearing connector candidate for every building boundary access-location candidate. Each record carries stable candidate IDs, building access-point lineage, road/frontage or road-reserve relationship IDs, road and segment references, a two-endpoint LineString, measured straight-line length, coordinate reference, source manifest checksum and explicit review status. Construction, surface, gradient, barriers, pedestrian/vehicle suitability, accessibility, legal/public access and emergency-egress states remain unknown or not assessed. The four point-contact-only road-reserve cases remain distinct from frontage. The new append-only table is `sw_property.access_connector_candidate` (proposal 0017); disposable PostgreSQL acceptance requires 768 records, including four point-contact-only proximity records. No operational access or Neon production write is involved.


### BP04-03 persistent access connector candidates — validated

[Stage E disposable PostgreSQL run 45519143869](https://github.com/Joshuaogri/saltwater/actions/runs/45519143869) passed. The physical-asset inventory now persists 768 distinct connector candidates in the append-only `sw_property.access_connector_candidate` table, including four explicitly typed point-contact-only road-reserve connections. All 768 connector records retain road-segment lineage, two-endpoint LineString geometry, length, source manifest checksum and unknown/not-assessed physical and legal attributes. The corrected parcel dossier generator now supplies road segment IDs to every frontage access candidate; missing lineage is rejected before import.

The disposable PostgreSQL import added 130,973,696 bytes (130.97 MB decimal), including 768 connector records, 18,098 profiles and 181,915 typed detail records. The connector table occupies 1,007,616 bytes. Re-import of the same manifest grew the database by 0 bytes; backup/restore preserved the connector rows and manifest checksum. No operational access, canonical addresses, or production Neon writes were created. Neon remains 9,306,112 bytes on read-only measurement. See [complete connector candidate evidence](docs/implementation/test-evidence/BP04-03-persistent-access-connector-candidates-stage-e-run-0002.md).


### BP04-03 independent access connector road topology

The new independent topology audit [45519989730](https://github.com/Joshuaogri/saltwater/actions/runs/45519989730) passed all 9 checks and 6 regression tests. It verifies all 768 connector candidates against their building/property/parcel lineage, source road and segment identity, endpoint coordinates, measured length, parent-property containment and road-reserve geometry. It confirms 764 frontage connectors, four distinct point-contact-only road-reserve connectors, and zero unlinked connectors or topology exceptions. This remains geometric QA only; no built or legally usable access route is inferred and no Neon writes occur. See [independent topology audit evidence](docs/implementation/test-evidence/BP04-03-independent-access-connector-road-topology-run-0001.md).


### BP04-03 route-corridor centreline candidates — validated

[Route-corridor audit 45520905232](https://github.com/Joshuaogri/saltwater/actions/runs/45520905232) passed all 7 checks and 6 regression tests. The generated CI artifact contains 768 traceable two-dimensional centreline candidates: 764 frontage-linked and four point-contact/proximity-linked. There are zero unresolved connectors, mapped building intersections, mapped water intersections, originating-building interior crossings or road-reserve overlaps. Forty-seven centrelines intersect the mapped Central-Western Ridge terrain feature; this is recorded as context, not as an impassable obstacle. Other-building separation ranges from 31.894 m to 480.755 m, which is not available route width or a safety clearance.

No corridor width, available width, gradient, surface, barriers, accessibility, legal/public access or emergency-egress state is inferred: these remain null, unknown or not assessed. The artifact is CI-only; no production database write or operational access activation occurred. See [route-corridor candidate evidence](docs/implementation/test-evidence/BP04-03-route-corridor-centreline-candidates-run-0001.md).

### BP04-03 terrain evidence intake and append-only review register — validated

[Evidence intake and review workflow 45568025845](https://github.com/Joshuaogri/saltwater/actions/runs/45568025845) passed all **12 regression tests** and generated the source-linked [read-only evidence register artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45568025845/artifacts/15001455213) (1,061 bytes; SHA-256 `4142a88b349ae143b9e82a9f1c3c0d47df2d72b7ee79519bc2709bfbef80c446`). The register preserves stable evidence/subject IDs, evidence type, capture and submission times, actor/source references and hashes, collection method, instrument/calibration references, observation geometry, typed measurements, uncertainty, attachment hashes, chain-of-custody, validity intervals, supersession and append-only reviewer decisions. Accepted evidence remains non-operational and cannot automatically activate a physical fact. Terminal review decisions cannot be overwritten; changes require new records. The baseline contains 0 submitted observations, 0 review events, 0 accepted evidence records and 0 operational facts activated; 7/7 model checks passed. No survey facts were fabricated and no production database writes occurred. Full [run 0001 evidence](docs/implementation/test-evidence/BP04-03-terrain-evidence-intake-review-register-run-0001.md). Next: field-survey work orders and inspection protocols tied to survey cells and source subjects, including measurement requirements and instrument/calibration controls.

## BP04-03 — canonical fictional physical world (SW-PHYS-V1)

Saltwater now has a populated, playable physical geography layer in `data/geography/saltwater-physical-world-v1.json`. This is authored fictional game canon, not an empty survey-candidate register. It defines **9 terrain zones** with elevation ranges on the fictional SW-VERT-01 datum, landform, substrate, ground condition and gameplay context. It also defines **32 physical assets** with individual IDs, names, neighbourhood placement, geometry, height, width, construction material, condition and continuity: retaining walls, masonry walls, fences, gates, reservoir embankment, culvert, open/covered drainage, quay walls, flood wall, seawall and acoustic barrier. The dataset includes movement rules for barriers, gates, drainage and road-based vehicle travel. Gates have game operating states and access schedules; the existence of a gate does not imply it is open. All coordinates are fictional SW-LOCAL-01 coordinates. Automated validation checks geometry, parent-neighbourhood containment, unique IDs, dimensions, materials, terrain datum and required feature categories. Workflow: [Saltwater Canonical Physical World Validation](.github/workflows/saltwater-physical-world-validation.yml).

## BP04 — canonical playable property world (SW-PROPERTY-WORLD-V1)

The property-world generator now converts Saltwater's deterministic fictional parcel/building design into persistent in-game records. It creates one canonical property identity and street address per generated property site; links buildings, floor-level premises, units and ownership interests; creates the referenced property-holding organisations; and supplies named rooms, building components, site boundary/yard/parking/drainage/waste features, utility connections, construction profiles and condition states. Building access locations become actual fictional entrances, service entrances and emergency exits, each linked to a constructed in-game route and a named road. The four proximity-only building connections are represented as shared access spurs rather than being left unserved. Sites without buildings receive a site gate and pedestrian/maintenance path. Units remain unassigned: this dataset creates no residents or businesses and cannot exceed the 10,000-person population cap. Output is stored as normalized, columnar textual JSON at `data/property/saltwater-property-world-v1.json` so repeated field names are stored once rather than repeated across thousands of unit/component rows. It is generated and committed to `main` by [Saltwater Canonical Property World Build](.github/workflows/saltwater-property-world-build.yml). Regression tests verify identity uniqueness, property/building/premises/unit lineage, addresses, ownership references, access-route continuity and population isolation.

### Current generated baseline

The committed property-world baseline contains **420 properties, 384 buildings, 1,327 premises, 15,199 units, 420 addresses, 804 access points and 804 constructed access routes**. It also contains 420 ownership interests and property-holding organisations, 4,992 building-component records, 5,308 named room records and 2,100 site-feature records. The 36 sites without a building have a site-level entrance and maintenance path. The four proximity-only cases are represented by shared access spurs. The unit register creates no residents and leaves all units unassigned. The columnar JSON file is **12,788,522 bytes** (about 12.19 MiB), down from the first expanded-object encoding of 23,833,730 bytes. The property-world workflow passed all **11 regression tests**, including parsing the persisted JSON file and checking the record totals.

## BP04 — 10,000-business registry foundation (SW-BUSINESS-REGISTRY-V1)

The next built-world layer is a deterministic registry of **10,000 distinct Saltwater businesses**, distributed across 15 fictional sectors. Every business receives its own immutable business ID, registered name, trading name, activity, legal form, size, employee band, operating status and establishment. Each establishment links to a canonical property, building, premises, unit and street address. Business-to-unit occupancy is stored as a separate time-valid relationship. Home-based businesses are used where needed to represent the full range of local economic activity without inventing extra properties or buildings. Employee bands do not create people: the registry creates zero residents, staff-person records or additional population. Textual columnar JSON is persisted at `data/business/saltwater-business-registry-v1.json` by [Saltwater 10,000 Business Registry Build](.github/workflows/saltwater-business-registry-build.yml).

### Current business registry baseline

The generated registry now contains **10,000 distinct businesses**, **10,000 establishments** and **10,000 business-to-unit links** across **15 sectors**. The baseline comprises 9,400 active, 286 seasonal and 314 temporarily inactive businesses. All 10,000 establishments resolve through the property/building/premises/unit/address hierarchy. No staff or resident person records are created. The compact columnar textual JSON file is **8,025,670 bytes** (about 7.65 MiB). The build and its regression tests passed; the registry is committed on `main`.

### Business operations and opening-hours records

The next textual world layer adds a weekly operating schedule for every registered establishment. Each business has seven explicit weekday rows (70,000 daily records across 10,000 businesses), local customer opening and closing times, service windows, staff shift patterns, delivery windows, operational status and an access reference for dispatch. Seasonal and temporarily inactive businesses receive appropriate closure states. These schedules do not create employee, customer or resident person records and do not change the 10,000-person city cap. Source: `runtime/business_operations_generator.py`; output: `data/business/saltwater-business-operations-v1.json`; regression tests: `tests/pkg001/test_business_operations_generator.py`.


## SW-CANON-002 — primate city and global international hub

**Adopted 2026-11-25 as binding canon across all 44 blueprint divisions.** Saltwater is the country's single primate city and dominant national and international metropolis: the highest national and international levels of government, diplomacy, corporate headquarters, banking and finance, entertainment, media, technology, healthcare, education, hospitality, professional services, trade and culture are concentrated here. Saltwater is also a world-leading maritime transit, export, transshipment and logistics exchange hub, comparable in strategic role to the Suez Canal and the world's major port, financial and commercial centres. It must never be modelled as an ordinary small city.

The 10,000-person permanent population cap remains in force, but it does not limit corporate scale, subsidiaries, establishments, institutional capacity, cargo throughput, vessel movements, passenger flows, international reach or economic activity. Transient people must continue to be counted under the existing population rules; this canon does not authorise bypassing the person cap. The existing 10,000-business registry is an initial baseline, not a ceiling on global corporate presence or a claim that all businesses are small. Future property, business, transport, port, airport, institutional, economic and police systems must reflect this global primate-city role.

- [Read SW-CANON-002 — Primate City and Global International Hub](docs/blueprint/decisions/SW-CANON-002-primate-city-global-hub.md)


## BP-04 — property ownership, tenancy and occupancy (SW-PROPERTY-TENURE-V1)

The first property tenure layer is generated and committed on `main`. The deterministic generator consumes the existing compact property-world and business-registry datasets rather than rebuilding geometry, and writes a compact columnar JSON dataset at [`data/property/saltwater-property-tenure-v1.json`](data/property/saltwater-property-tenure-v1.json) (10,833,623 bytes; approximately 10.33 MiB).

The dataset contains:
- 420 current property ownership interests, with chronological fictional acquisition and transfer events and resolvable historical owner organisations.
- 420 current property-management appointments, with separate property-management organisations where appointed.
- 10,000 current commercial leases, licences or operating concessions, each linked to its landlord, business, establishment, property, building, premises and unit.
- 2,500 expired historical agreement records, retained alongside current agreements.
- 10,000 current business occupancy records.
- 15,199 unit occupancy-state records. Residential units remain unallocated for the separate population-allocation process; no resident or other person records are created.
- Contractual rent bands and repair/renewal terms are references only. Rent postings, balances and accounting remain BP-34.

The output uses the same lossless textual columnar representation as the property-world baseline. The build reuses persisted canonical property and business datasets, avoiding duplicate geometry generation. Regression workflow [45577532056](https://github.com/Joshuaogri/saltwater/actions/runs/45577532056) completed successfully, including generation, six tenure regression tests and persistence to `main`.

## BP-04 — weekly business operating schedules (SW-BUSINESS-OPERATIONS-V1)

The weekly schedule layer is generated and committed at [`data/business/saltwater-business-operations-v1.json`](data/business/saltwater-business-operations-v1.json) (15,319,899 bytes; approximately 14.61 MiB). It contains 70,000 daily opening/service/shift/delivery schedule records (seven per establishment) and 10,000 weekly profiles. Build and regression workflow [45574250446](https://github.com/Joshuaogri/saltwater/actions/runs/45574250446) completed successfully. Schedules do not create staff, customers or resident person records.

These datasets remain in GitHub only. No Neon upload or production seed write has occurred. Neon upload remains scheduled after the property-management layers are completed, with compact import packaging, a fresh live storage measurement, an incremental/projected storage estimate and explicit approval before any production write.


## BP-04 — building systems, utilities and metering (SW-BUILDING-SERVICES-V1)

The first building-services layer is generated, regression-tested and persisted on `main`. It consumes the existing compact property-world and tenure datasets and is stored as compact textual columnar JSON at [`data/property/saltwater-building-services-v1.json`](data/property/saltwater-building-services-v1.json) (16,961,533 bytes; approximately 16.18 MiB).

The dataset contains:
- Four citywide utility operators: electricity, potable water, wastewater and telecommunications.
- 1,680 property utility connections and 1,680 linked master utility accounts across 420 property sites.
- 32,078 meters: property master meters plus dedicated electricity and water submeters for all 15,199 units.
- 2,862 building systems across 384 buildings, including electrical distribution, water distribution, wastewater/sanitary, HVAC, fire protection, security/access control, building controls and vertical transport where installed.
- 6,431 equipment assets with installation year, condition, operational state, maintenance class and replacement priority.
- 2,862 system inspection schedules with intervals, last inspection years and next-due simulation ticks.
- 10,000 business utility-responsibility assignments linked to current occupancy records and dedicated unit submeters.

The layer records service availability, capacity bands, redundancy, account responsibility, equipment condition and inspection schedules. It does not create bills, meter readings, balances, financial postings, residents, employees or other person records. BP-34 retains authority over financial transactions; the population ledger remains unchanged.

Build and seven regression tests passed in workflow [45578689850](https://github.com/Joshuaogri/saltwater/actions/runs/45578689850). The final regression-test optimisation also passed the regenerated workflow [45578778424](https://github.com/Joshuaogri/saltwater/actions/runs/45578778424).

This dataset remains in GitHub only. No Neon upload or production seed write has occurred. Neon preparation remains after the remaining property-management layers, with compact import packaging, a fresh live database storage measurement, projected incremental storage and explicit approval before production writes.


## BP-04 — property maintenance, defects and repairs (SW-PROPERTY-MAINTENANCE-V1)

The maintenance and repair layer is generated from the persisted property-world, tenure and building-services datasets. It establishes:
- 384 integrated building maintenance plans and 1,920 linked maintenance cycles.
- 3,282 inspection schedules covering all 2,862 building systems and all 420 property sites.
- 3,169 equipment-linked defect records with severity, discovery basis, operational and safety implications, urgency, root-cause profile and temporary controls.
- 3,169 linked work requests; 2,119 open corrective work orders with trade requirements, responsible maintenance contractors, managing organisations, duration bands, line items, materials and lifecycle events.
- 2,119 material issue records, 384 building emergency-maintenance procedures, equipment warranties and capital replacement forecasts.
- 11 specialist fictional maintenance contractor organisations; contractor organisations are not individual people.

The generated dataset is compact columnar JSON (9,261,100 bytes). Seven regression tests passed in [workflow 45579288100](https://github.com/Joshuaogri/saltwater/actions/runs/45579288100). The generator and tests verify property/building/system/equipment/work-order linkages, full inspection coverage, deterministic manifests and zero person, population or financial postings.

No invoices, payments, cost ledger, capital commitments, residents, employees or contractor-person records are created. BP-34 retains financial authority. The dataset is committed to GitHub `main` only; no Neon upload or production seed write has occurred.

- [Maintenance dataset](data/property/saltwater-property-maintenance-v1.json)
- [Generator](runtime/property_maintenance_generator.py)
- [Regression tests](tests/pkg001/test_property_maintenance_generator.py)
- [Build workflow](.github/workflows/saltwater-property-maintenance-build.yml)


## BP-04 — property security and access control (SW-PROPERTY-SECURITY-ACCESS-V1)

The property security layer is generated from the canonical property, tenure and building-services records:
- 804 door/gate records and 804 linked lock records, covering every canonical property/building access point.
- 1,233 controlled physical key records across 1,233 mechanical key cylinders, with restricted keyway profiles, duplicate controls and organisation-managed key cabinets.
- Electronic door-controller/reader devices for electronically controlled entrances.
- 18,830 access zones across building entry, building security areas, premises and individual units.
- 10,000 business-occupancy access groups, permission sets and organisation-level assignments linked to current leases/concessions and unit occupancy.
- Door policies cover schedules, contractor/work-order authorisation, visitor passes, lost-credential revocation and emergency override audit.

The model preserves free emergency egress and does not issue credentials to named people. Individual credential assignment, access logs and key issue events are runtime gameplay records, not fabricated baseline history. No residents, employees, person credentials, population records, invoices or financial postings are created.

Generation and seven regression tests passed in [workflow 45579877325](https://github.com/Joshuaogri/saltwater/actions/runs/45579877325). The compact columnar dataset is 13,065,912 bytes.

- [Security and access dataset](data/property/saltwater-property-security-access-v1.json)
- [Generator](runtime/property_security_access_generator.py)
- [Regression tests](tests/pkg001/test_property_security_access_generator.py)
- [Build workflow](.github/workflows/saltwater-property-security-access-build.yml)

No Neon upload or production seed write has occurred.

## BP-04 — property condition, valuation, insurance and taxation (SW-PROPERTY-VALUE-RISK-TAX-V1)

Implemented on `main` and generated from the persisted property, tenure, building-services, maintenance and security datasets. The deterministic compact columnar dataset contains 804 site/building condition assessments; 420 land valuations; 384 building-improvement valuations; 804 whole-property/building asset valuations; 1,327 premises valuations; 420 property insurance policies with 1,260 coverage records; 420 property risk profiles; 420 annual 2026 property-tax assessments; 420 exemption-screening records; five fictional insurer organisations; and one annual property-tax rule. Valuations use fictional SWC simulation units and replacement-cost/land-assessment profiles, not real market quotes. Condition records reference the existing defect and building-system baseline. Tax assessments remain assessed-not-billed; exemption is not presumed. No insurance claims, premiums, tax bills, invoices, payments, financial postings, residents or other person records were created. BP-34 retains transaction authority. Seven regression tests passed and the dataset was persisted in [run 45601885026](https://github.com/Joshuaogri/saltwater/actions/runs/45601885026). Output size: 1,309,420 bytes (~1.25 MiB); manifest SHA-256: `921a3dd9274d74a53e8113c78099224a9a4a5b103532edcb672a21a7c8eb165e`.

- [Property valuation, insurance and tax dataset](data/property/saltwater-property-value-risk-tax-v1.json)
- [Deterministic generator](runtime/property_value_risk_tax_generator.py)
- [Regression tests](tests/pkg001/test_property_value_risk_tax_generator.py)
- [Build workflow](.github/workflows/saltwater-property-value-risk-tax-build.yml)

## BP-04 — property development control, building control and lawful use (SW-PROPERTY-DEVELOPMENT-CONTROL-V1)

Implemented on `main`; the deterministic generator consumes the persisted property, tenure, building-services, maintenance and valuation/condition datasets. It records 420 site development plans; 384 existing-building planning permissions; 384 building-control cases; 384 completion/safe-use certificates; 384 periodic inspection schedules; 1,327 premises lawful-use certificates; 15,199 unique unit-level use-compliance records; 72 approved pre-construction development projects; and four development-control rule profiles covering port/maritime, logistics, residential and critical digital infrastructure. The 384 permissions and completion certificates establish the existing fictional built-world baseline; they are not represented as newly submitted applications or fabricated historical inspection visits. All inspection schedules remain scheduled, not completed. The planning application register is empty until gameplay creates applications. The 72 development projects are approved but have not started construction. No people, population records, invoices, fees, payments or financial commitments were created. Seven regression tests passed in [run 45603224586](https://github.com/Joshuaogri/saltwater/actions/runs/45603224586). Output size: 15,029,136 bytes (~14.33 MiB); manifest SHA-256: `9699f165769898af8bc71a7911a2608f0ec8b464a94e6f950f92deccac7c9f60`.

- [Property development-control dataset](data/property/saltwater-property-development-control-v1.json)
- [Deterministic generator](runtime/property_development_control_generator.py)
- [Regression tests](tests/pkg001/test_property_development_control_generator.py)
- [Build workflow](.github/workflows/saltwater-property-development-control-build.yml)



## BP-04 — property title, transactions and lifecycle register (SW-PROPERTY-LIFECYCLE-TRANSACTIONS-V1)

The deterministic property lifecycle generator is `runtime/property_lifecycle_transactions_generator.py`; its compact columnar output is `data/property/saltwater-property-lifecycle-transactions-v1.json`. It creates a unified title register for all 420 canonical property sites, 420 current property-interest records, 531 title instruments and 531 property-transaction index rows. Each transaction row references the authoritative ownership event ID in `SW-PROPERTY-TENURE-V1`; ownership history is not duplicated or re-authored. It also records baseline lifecycle lineage for all 384 buildings and 1,327 premises, linked to their existing development permissions, completion certificates and lawful-use certificates.

Every property has an encumbrance register, but the absence of supplied mortgage, lien, easement or charge data is explicitly recorded as **not asserted**, not as proof that no such interests exist. Ten future gameplay action types are defined: acquisition, sale/transfer, subdivision, consolidation, redevelopment, demolition, change of use, easement/wayleave, mortgage/charge and lease/concession change. These action definitions do not fabricate completed events or mutate the current physical hierarchy. Subdivision and consolidation require new parcel geometry and parent/child lineage before execution. No financial postings, settlement, payments, people or population records are created.

Eight regression tests passed in [workflow 45604525551](https://github.com/Joshuaogri/saltwater/actions/runs/45604525551). The generated dataset is approximately 1.00 MiB (1,044,637 bytes); manifest SHA-256: `c3d35be72d8175d4c9e096ba0aa4e93a1353bb92902c6f19f54acbf7e82fe1ea`. This is GitHub artifact size, not a PostgreSQL storage estimate. No Neon writes were made.


## BP-04 — property rights, easements, wayleaves and boundary evidence (SW-PROPERTY-RIGHTS-AND-BOUNDARIES-V1)

The deterministic generator `runtime/property_rights_boundaries_generator.py` produces `data/property/saltwater-property-rights-boundaries-v1.json`. It creates 420 property-rights schedules, 12,500 contractual-right indexes (10,000 current and 2,500 expired), 420 parcel-boundary evidence records, 804 physical-access evidence records and 1,680 utility-wayleave requirement records. Contractual-right indexes reference existing lease/licence/concession agreement IDs from `SW-PROPERTY-TENURE-V1`; they do not create duplicate agreements.

The boundary register references the existing planning parcel geometry but explicitly marks it as non-survey-grade and not independently verified as a legal boundary. Physical entrances and constructed routes are recorded as physical access evidence only; no legal right of way is inferred. Utility connections are indexed separately from legal wayleaves: the existence of a connected service does not prove an easement, landowner consent or utility corridor right. Nine instrument templates define evidence required for easements, rights of way, utility wayleaves, covenants, mortgages/charges, liens/caveats, boundary agreements and access licences. The registered-instrument register remains empty because no supporting source instruments were present; missing rights are marked unverified, not presumed absent.

Eight regression tests passed in [workflow 45605593292](https://github.com/Joshuaogri/saltwater/actions/runs/45605593292). The generated compact dataset is 5,011,509 bytes (about 4.78 MiB); manifest SHA-256: `8b3f864c0f524c0482271ae4989ceddafe19ce1124169e7a149008ae9a621e69`. This is a GitHub artifact size, not a PostgreSQL storage estimate. No Neon writes were made.


## BP-04 — property insurance exposure, loss events and claims controls (SW-PROPERTY-INSURANCE-CLAIMS-V1)

The deterministic generator `runtime/property_insurance_claims_generator.py` produces `data/property/saltwater-property-insurance-claims-v1.json`. It indexes all 420 existing property insurance policies and their insurers, coverage references, sums insured, deductibles and property valuations. It creates 384 building insurance schedules, 6,431 equipment insurance schedules, 3,169 defect exposure links and 4,200 peril assessments (10 peril categories for each property). Equipment remains covered within its parent property/building schedule; no separate equipment sum insured or duplicate insurance is invented.

The claims process defines ten stages from first notification and coverage triage through loss mitigation, evidence preservation, adjuster review, quantum assessment, coverage decision, settlement authorisation and closure. Sixteen loss-event types are available for future simulation, including coastal flood, storm surge, extreme rainfall, fire, machinery breakdown, utility outage, port-adjacent property damage and business interruption. The operational claims and loss-event registers remain empty: no historical loss, claim, reserve, settlement, premium posting or payment was fabricated. Known maintenance defects are linked as exposures only; causation and insurable loss remain unassessed. Full policy wording, exclusions, endorsements and site-specific hazard surveys remain unverified inputs for future adjudication.

Eight regression tests passed in [workflow 45606397673](https://github.com/Joshuaogri/saltwater/actions/runs/45606397673). The compact dataset is 4,966,651 bytes (about 4.74 MiB); manifest SHA-256: `54e7b58825b843acc146f57fe604fd47f70f122fd5182dd6787950fc1041f12b`. This is a GitHub artifact size, not a PostgreSQL storage estimate. No Neon writes were made.

## BP-04 — property facilities management and operational services (SW-PROPERTY-FACILITIES-OPERATIONS-V1)

The deterministic generator `runtime/property_facilities_operations_generator.py` produces `data/property/saltwater-property-facilities-operations-v1.json`. The opening operating model covers all 420 property sites, 384 buildings and 1,327 premises. It defines 6,720 property-level facilities framework contracts, 6,720 service zones and target service-level agreements, and 13,243 planned service schedules. Service domains include cleaning, general/recycling/organic and specialist waste, pest management, grounds, water hygiene, fire systems, lifts and vertical transport, HVAC/air quality, security systems, energy management, drainage/flood readiness, roofs/facades and port/cargo specialist operations. Premises and building schedules are linked to canonical property IDs; specialist providers are framework-calloff arrangements where applicable.

The service-failure rules cover missed routine work, critical plant/life-safety failures, waste overflow or misclassification, flood/drainage obstruction and repeated supplier failure. Schedules and SLA values are opening targets, not measured performance. Service requests, completed visits and supplier-performance actuals remain empty until gameplay creates them. No staff/person records, waste tonnage, invoices, payments or financial postings are fabricated; BP-34 remains the sole financial posting authority.

Six regression tests passed in [workflow 45607314182](https://github.com/Joshuaogri/saltwater/actions/runs/45607314182). The compact dataset is 7,150,576 bytes (about 6.82 MiB); manifest SHA-256: `f324312f2764c5dac491ef47235b5e1acc976f9ed0ed5cf35452461f2fe95ba3`. This is a GitHub artifact size, not a PostgreSQL storage estimate. No Neon writes were made.

**Unit-count reconciliation completed:** the 62,585 figure was caused by a duplicate nested premises loop in the development-control generator, which emitted each unit's compliance row repeatedly for every premises in its building. The generator now emits one row per actual unit identity. The corrected property-world, tenure occupancy, utility submeter and development-control registers each resolve to the same 15,199 unit IDs; the facilities-operations dataset now verifies identity-set equality and reports `reconciled`. No units were added or removed to force a count match.


## BP-04 — unit identity reconciliation correction (SW-PROPERTY-UNIT-RECONCILIATION-001)

An integrity review traced the apparent 47,386-unit excess to a duplicate nested premises loop in `runtime/property_development_control_generator.py`. Unit compliance had been emitted repeatedly for every premises in the same building. The generator was corrected to emit one record for each unit under its actual premises, and regression tests now assert both one-to-one count equality and uniqueness of unit IDs. The corrected development-control dataset contains **15,199 unit-use compliance records for 15,199 canonical unit identities**. Seven regression tests passed in [workflow 45608515021](https://github.com/Joshuaogri/saltwater/actions/runs/45608515021). Corrected output size: 4,688,872 bytes; manifest SHA-256: `3c83da9b66389a451fb1997ee0801876305cc25c046bc621cd2eb0b5cb6814fe`. Dataset commit: `a722aa7eae9abd5ee3fbda5f886d738fda8f566a`.

The facilities-operations generator now reads the corrected development-control dataset and compares the actual unit-ID sets across property world, tenure, utility submeters and development control. All four contain the same **15,199** unit IDs and the result is **reconciled**. Six regression tests passed in [workflow 45608676475](https://github.com/Joshuaogri/saltwater/actions/runs/45608676475). Updated facilities dataset size: 7,150,790 bytes (~6.82 MiB); manifest SHA-256: `dd66d415612d66be74662b00d6ecfd2fcd5533b4061c8a18b63f9a520e43d2ca`. Dataset commit: `9a1e949808345fe856a581f968dfa2e985bcceda`. Neither dataset update involved a Neon production write.

## SW-GLOBAL-ESTATE-CAPACITY-AUDIT-001 — global-city estate scale review

The first vertical-intensification phase is now fully regenerated, regression-tested and persisted as one consistent property/business snapshot on `main`. Sequential rebuild workflow: [45611785956](https://github.com/Joshuaogri/saltwater/actions/runs/45611785956), completed successfully. Snapshot commit: `ed0b77e`.

The deterministic district-specific `GLOBAL-ESTATE-VERTICAL-V1` profiles create commercial towers up to 58 storeys, with distinct financial, civic, university and harbour skylines. Industrial, freight, port-yard and utility assets retain appropriately lower-rise forms.

**Verified regenerated estate totals**
- 420 property sites; 384 buildings; 6,954 premises; 80,965 canonical units.
- 12,430,234.506 m² gross floor area; maximum height 58 storeys; mean building height 18.109 storeys.
- 265 buildings have at least 10 storeys; 146 have at least 20 storeys.
- 10,000 businesses and 10,000 establishments.
- 163,610 utility meters; 6,815 equipment assets; 3,054 building systems.
- 90,223 access-control zones; 804 canonical access points and 804 constructed access routes.
- Facilities schedules and service zones have been regenerated against the same canonical unit set.

Unit identity reconciliation is exact across the property world, tenure occupancy, utility submeters, development-control use records and facilities operations: **80,965 unique unit IDs in each register, with no missing or extra IDs**. All sequential rebuild test groups passed, including the final insurance, facilities and estate-capacity audit regression suites.

The 10,000-person population hard cap is unchanged. No residents, workers, employees, police personnel or other person records were created. No Neon production writes were made.

**Next physical-estate phase:** replace the single-building-per-property limitation with multi-building campuses and specialist megasites. This includes international port and bonded-logistics terminals, intermodal freight/passenger complexes, export-manufacturing estates, financial/corporate headquarters campuses and major international institutions. Every additional building must receive unique building, premises, unit and access identifiers, site-contained geometry, a connected constructed entrance/route and fully regenerated downstream property records. Existing site-only entrances and no-frontage access solutions must be preserved. The one-contiguous-city-state canon and 10,000-person cap remain binding.

## SW-PROPERTY-ESTATE-V2 — expanded campus estate and regenerated property stack

**Verified and persisted on `main` on 2026-11-25.** This section supersedes all earlier property-estate counts and dataset-size statements above where they describe the pre-campus or single-building estate. The sequential full-stack rebuild and all 13 validation stages passed in [workflow run 45623907617](https://github.com/Joshuaogri/saltwater/actions/runs/45623907617). All dependent registers were regenerated in dependency order, compressed, and persisted together in one consistent snapshot.

### Canonical expanded physical estate

- 420 property sites.
- 1,474 buildings across multi-building campuses and specialist sites.
- 27,730 premises.
- 180,733 canonical units.
- 110,920 named rooms.
- 2,984 building/site access points and constructed access routes.
- 36 sites without buildings retain site-level entrances and maintenance paths.
- Existing shared access spurs continue to resolve the four original frontage-deficient cases.
- No resident, worker, employee, police-personnel or other person records were generated. The distinct-person population cap remains 10,000.

### Regenerated dependent registers

The same expanded estate was used to regenerate business registry and weekly operations, ownership and occupancy, utility connections/meters/building systems/equipment, maintenance and defects, security and access control, condition/valuation/insurance/tax, development and lawful use, title/lifecycle/transactions, rights/boundary evidence, insurance exposure/claims controls, facilities operations, and the global estate-capacity audit. All 13 workflow validation stages passed, including exact canonical unit-identity reconciliation across the property world, tenure, utility submeters, development-control and facilities records.

### Compressed source inventory

All 14 property/business datasets are stored as deterministic gzip snapshots under `data/property/` and `data/business/`. Their combined GitHub blob size is **23,023,562 bytes (21.96 MiB)**. No uncompressed `.json` dataset files remain in those two folders. The canonical property-world snapshot is 8,924,278 bytes compressed; the building-services snapshot is 4,284,913 bytes compressed. These are source-repository compressed sizes, **not** PostgreSQL storage estimates.

The full-stack workflow restores compressed inputs, rebuilds and validates the complete dependency stack, compresses every output and commits the consistent snapshot to `main`. No Neon production seed/import/upload or population write occurred. Before any proposed Neon import, the compact package must be prepared and benchmarked, the live PostgreSQL baseline remeasured, and projected database growth reported for explicit approval.

## Canonical property-stack import preparation

The expanded 14-dataset property/business stack is persisted and validated on `main`. The next database phase is governed by [BP04 canonical property-stack import and disposable benchmark plan](docs/implementation/BP04-canonical-property-stack-import-plan.md). Existing BP04-01/BP04-02 schema proposals and the BP04-03 Stage E importer are disposable-only candidate assets, not the canonical property-world importer. The production property schema and lossless relational import pipeline must be built and benchmarked in isolated PostgreSQL 16 first. The live Neon database remains unchanged; no property seed rows or production property tables have been written.

### BP04 canonical property relational schema — phase 1

The first typed relational import model is now committed on `main` for isolated PostgreSQL 16 validation. Candidate SQL: `db/proposals/0012_bp04_canonical_property_stack.sql`. The mapping and integrity contract is documented in [BP04 canonical property relational mapping](docs/implementation/BP04-canonical-property-relational-mapping.md). It establishes stable source-ID primary keys and typed property, building, premises, unit, access, room/component, ownership, business, establishment and occupancy tables, with explicit foreign keys, provenance and a deterministic import-release ledger. Original source objects are retained per typed row for lossless round-trip verification; this is not a single opaque JSONB store.

This is a disposable-only schema proposal. It has not been applied to Neon. The deterministic importer, full phase-2 register coverage and PostgreSQL 16 benchmark are the next implementation tasks. No production schema or data writes have occurred.

The phase-1 schema now has a dedicated disposable PostgreSQL 16 acceptance workflow (`.github/workflows/bp04-property-schema-disposable.yml`) and SQL contract checks (`tests/pkg001/bp04_property_schema_acceptance.sql`). The workflow applies only the candidate proposal to an ephemeral CI database, verifies the 19-table inventory, deferred cyclic reference, current-unit uniqueness and release ledger, and records disposable schema size. It has not been run against Neon.

### BP04 phase-1 importer implemented

A deterministic, compressed-columnar importer is now available at `runtime/bp04_property_stack_importer.py`. It reads the canonical property-world, business-registry and tenure snapshots directly from their gzip files, verifies dataset identities and package digests, preserves each complete source row in JSONB alongside typed columns, uses stable source IDs, records an import-release manifest, and imports within one transaction with deferred FK checks. It refuses to connect to any database other than the disposable `saltwater_test` database. The dedicated PostgreSQL 16 workflow now applies the candidate schema, imports the package, repeats the import for row-count/idempotency checks, and reports database/table storage. CI run: [BP04 schema and import](https://github.com/Joshuaogri/saltwater/actions/runs/45628722456). This has no connection to production Neon.

### BP04 compressed-archive import benchmark — passed

The phase-1 schema was optimized after the first disposable benchmark showed that duplicating every complete source row as per-row JSONB inflated the database to 453.5 MiB. The storage-efficient proposal is now `db/proposals/0013_bp04_compressed_source_archive.sql`: complete original datasets are retained once as their original gzip byte streams in `source_dataset_archive`, while the typed relational tables retain stable source IDs and mapped operational columns. The importer is `runtime/bp04_property_stack_importer.py`.

The PostgreSQL 16 disposable workflow passed using this design: [BP04 compressed archive benchmark](https://github.com/Joshuaogri/saltwater/actions/runs/45630476765). It imported and reconciled **402,658 records across 17 typed tables**, covering 420 property sites, 1,474 buildings, 27,730 premises, 180,733 units, 110,920 rooms, 2,984 access points/routes, 10,000 businesses, 10,000 establishments, 10,000 business-unit links, 12,500 occupancy agreements and 10,000 occupancies. Cross-reference violations: **0**.

The three compressed source archives total **10,934,275 bytes (10.43 MiB)**; their uncompressed JSON totals **196,604,988 bytes (187.45 MiB)**. The measured disposable PostgreSQL database is **135,257,111 bytes (128.99 MiB)**, including typed rows, indexes and the compressed source archives. Re-importing the same release left database size unchanged (**135,257,111 bytes before and after**) and all row-count checks passed. This is a **71.6% reduction** against the initial row-level-JSONB design.

This remains a partial import benchmark: only property world, business registry and property tenure are included. The other dependent property registers still need typed mappings and a complete combined benchmark. The 128.99 MiB figure is not a final Neon projection. **No production Neon schema or data writes have occurred.**


## BP04 — complete compressed property-source inventory

The read-only source inventory is implemented in `runtime/bp04_source_inventory.py`, with regression tests in `tests/pkg001/test_bp04_source_inventory.py` and CI workflow `.github/workflows/bp04-source-inventory.yml`. Successful inventory run: [45633081533](https://github.com/Joshuaogri/saltwater/actions/runs/45633081533).

- 14 compressed property/business source datasets.
- 105 columnar collections.
- 1,950,947 source records.
- 23,023,562 compressed bytes (21.96 MiB).
- 559,420,873 uncompressed bytes (533.5 MiB).
- Every collection was checked for valid columnar structure and row-width consistency; inventory records column names, row counts, candidate identity columns, compressed/uncompressed sizes and SHA-256 source digests.
- Canonical dataset IDs are read from source metadata rather than inferred from filenames.
- This is source-package inventory only. It is not a relational import, Neon storage estimate or production upload. The phase-one PostgreSQL benchmark remains limited to the three mapped datasets; typed mapping and full disposable benchmarking of the remaining registers are next.


## BP04 — building services and utilities relational phase 2

The candidate schema `db/proposals/0014_bp04_building_services_utilities.sql` and importer mappings now cover all eight collections in the compressed building-services source: **426,399 records** across building systems, utility connections, utility provider profiles, utility accounts, meters, equipment assets, system inspections and business utility responsibilities. The importer preserves the original gzip dataset once in the source archive and writes typed operational columns with stable source IDs and explicit links to canonical property, building, unit, organisation, business and occupancy records.

The disposable PostgreSQL workflow applies proposals 0013 and 0014 in order and checks the 28-table schema before import. It then verifies source/table counts, cross-register constraints, repeat-import idempotency and database storage stability. A first import attempt exposed source boolean flags encoded as 0/1 integers; the importer now normalizes those values explicitly. The latest benchmark run is [45635002711](https://github.com/Joshuaogri/saltwater/actions/runs/45635002711); its final import, reconciliation and storage result must be checked before treating phase 2 as accepted.

This remains disposable-only. No Neon production schema or data writes have occurred.
