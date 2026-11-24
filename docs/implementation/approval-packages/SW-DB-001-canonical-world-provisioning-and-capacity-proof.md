# SW-DB-001 — Canonical Saltwater World Provisioning and Capacity Proof

**Project:** Saltwater  
**Package:** SW-DB-001  
**Target:** Neon PostgreSQL production is the final intended destination; implementation/testing in this package is disposable PostgreSQL only  
**Git branch:** `main` only  
**Status:** APPROVED — implementation in progress (2026-11-24)  
**Prepared:** 2026-11-24  
**Neon production write authority:** NONE

## 1. Purpose

Prepare the first full-scale canonical-world data foundation for Saltwater and prove its structural integrity, idempotency and measured storage footprint before any production provisioning. This is the first database-first world implementation package after the existing runtime/platform foundation.

It deliberately separates:
1. schema and provisioning implementation;
2. disposable full-scale data generation and validation;
3. Neon production rollout, which requires a later explicit approval after all release gates pass.

Neon remains the authoritative persistent game database. GitHub `main` remains the only development branch and source of schema/migration history. No second authoritative database is introduced.

## 2. Binding canon used by this package

- One fictional sovereign city-state, one playable city and one jurisdiction: Saltwater.
- Maximum 10,000 living people in total, including police.
- Opening population: 9,000 residents + 500 police = 9,500 total.
- Opening headroom: 500; do not silently fill it.
- At least 10,000 distinct, coherent businesses.
- One canonical person identity per person; police are a subset of the same population, not additional people.
- Geography canon is resolved by [SW-CANON-001](../../blueprint/decisions/SW-CANON-001-population-scope-and-foundational-geography.md): one contiguous coastal island city-state, 12 km × 9 km local-grid extent, eastern harbour, eight districts and 24 named neighbourhoods. This package must not fabricate the detailed polygons, roads, parcels or addresses; those require a coherent versioned map dataset.
- Population counting is resolved by SW-CANON-001: count the distinct living-person union of usual residents, everyone physically present and active police-service members; each person counts once.
- No duplicate/placeholder businesses merely to meet the minimum.
- No simulation-time advance while player absent or paused.
- Preserve full meaning, provenance, chronology, uncertainty and history; compress structure, never meaning.
- No hidden offender/accomplice reveal except the exact `bingo` trigger.

Population-scope and foundational-geography canon are now resolved by SW-CANON-001 and the corresponding BP-02/BP-03 updates. BP-04 business category/site distribution remains a separate open design item and must not be silently invented by this package. The disposable fixture must use the adopted count formula and must label any business-category distribution as test-only.

## 3. Existing platform and blockers

- Neon foundation migration 0001 is already applied; it contains the Saltwater world configuration and platform event/storage tables.
- PKG-001's `db/proposals/0002_runtime_city_population.sql` is a disposable-only proposal. It must not be applied to Neon or treated as production-approved.
- BP-02, BP-03, BP-04 and BP-38 specifications remain `DESIGNED_DRAFT`.
- BP-02/BP-03 population and foundational-geography canon decisions are closed in SW-CANON-001; the actual detailed map and individual person records remain to be implemented and tested.
- BP-04 business baseline/category/site distribution decisions remain open and are not resolved by SW-DB-001.
- Production simulation seeding remains blocked by the existing G1 narrative-quality and G2 capacity/reserve gates. The 16-record narrative fixture's manual review rows remain pending; AI-assisted review is not human sign-off.
- The 1 GB Neon production capacity decision remains NOT APPROVED.

## 4. Bounded deliverables

### 4.1 Schema audit and candidate canonical-world model

Audit the existing disposable proposals and define a versioned, domain-owned schema candidate for:
- canonical person identity and effective-dated life/population state;
- one authoritative population count ledger/projection with transactionally enforced 10,000 ceiling;
- canonical business identity and business lifecycle;
- canonical geography references that do not invent geography;
- typed person/business/spatial relationships and provenance;
- deterministic provisioning batch manifest, generator version, source revision, record counts and content checksums;
- storage-operation measurements linked to a unique provisioning operation.

Respect domain ownership: BP-02 owns geography; BP-03 owns person identity/population; BP-04 owns businesses/property/organisations; BP-38 owns shared schema integrity; BP-39 owns recovery. Do not make BP-38 or a generic registry the owner of domain truth.

Any unresolved semantic field must be explicitly marked as unresolved in the design and must not be used to silently decide canon. No production schema migration is created by assumption.

### 4.2 Disposable PostgreSQL migration proposal

Prepare the next numbered candidate SQL proposal (expected `db/proposals/0010_canonical_world_provisioning.sql`, because SW-NAM-001 reserves proposal 0009 for the universal naming registry; perform a fresh migration-number audit before implementation) and apply it only to a fresh disposable PostgreSQL database.

The proposal must:
- be repeatable only where safe and fail clearly on incompatible prior state;
- use stable primary/foreign keys, explicit unique/check constraints and measured indexes;
- enforce population-cap changes atomically under concurrent admission attempts;
- preserve append-only source/lifecycle history and typed ownership;
- reject duplicate canonical person/business identities;
- support idempotent provisioning batches without duplicate inserts;
- retain a clean separation between authoritative records and rebuildable projections;
- avoid generic unbounded JSON payloads and unnecessary indexes;
- contain no production credentials or Neon connection path.

### 4.3 Deterministic full-scale disposable fixture

Create a versioned deterministic generator/fixture for:
- 9,000 test-only resident person records;
- 500 test-only police-subset person records, counted within the same 9,500;
- 500 unused population headroom;
- at least 10,000 distinct test-only businesses with non-duplicate identities and coherent varied attributes;
- only the canonical Saltwater sovereign/city roots where needed; no fabricated detailed geography;
- provenance and a fixture manifest that unambiguously labels every generated row as synthetic test data.

The fixture is for structural and capacity measurement, not production canon. It must not invent real-world persons or use personal data. Business categories/distributions used for load testing must be labelled test assumptions, not approved Saltwater business-distribution canon. Do not fabricate police personnel appointments, ranks, command structures or employee histories owned by BP-05–BP-08.

### 4.4 Acceptance and reconciliation

Prove on disposable PostgreSQL:
1. Exactly 9,500 distinct living test people are counted at opening.
2. Resident and police-subset counts reconcile to 9,000 + 500 without double counting.
3. Headroom is exactly 500.
4. The 10,001st living-person admission is rejected atomically.
5. Concurrent attempts for the final available slot cannot both succeed.
6. Death/permanent-exit test transitions release exactly one capacity slot without deleting identity or history.
7. Repeat provisioning with the same manifest is idempotent; it creates no duplicate people or businesses.
8. Business count is at least 10,000 distinct canonical business IDs; no duplicate placeholder identities.
9. Every business has a valid test-only operational basis and typed references; no unsupported geography is fabricated.
10. Invalid references, duplicate IDs, invalid lifecycle states and partial batch failures roll back cleanly.
11. The fixture and reports do not reveal hidden simulation truth or create any case/offender content.
12. Player-absence/pause invariants and canonical runtime time are unchanged; provisioning is a controlled setup operation, not a simulation tick.
13. Backup/restore of the disposable provisioned state preserves counts, identities, manifest and checksums.
14. All rows are labelled test-only and cannot be mistaken for production data.

### 4.5 Storage and performance report

Measure and report:
- fresh disposable database baseline;
- schema-only incremental bytes;
- data-stage incremental bytes;
- table heap, index, TOAST/auxiliary bytes;
- full database size before/after each stage;
- submitted fixture bytes separately from PostgreSQL storage growth;
- bytes per person and per business, with measurement method;
- insert throughput and query latency for population count/headroom, person lookup, business lookup and reconciliation;
- repeat-run idempotency/storage delta;
- uncertainty and excluded lifecycle costs.

Use raw bytes as authoritative and decimal MB (1 MB = 1,000,000 bytes); report MiB separately. Do not infer production capacity from a compact structural fixture. Do not claim the 1 GB plan is sufficient. Compare results with the 200 MB nominal reserve and 800 MB working ceiling only as existing planning gates, not approved capacity.

## 5. Tests and evidence

Add focused Python/SQL tests and a dedicated disposable PostgreSQL CI workflow. Run:
- all new provisioning and population-cap tests;
- all existing runtime, identity, security, hidden-truth, scheduling, event-dispatch and recovery regression tests;
- database migration validation;
- disposable backup/restore validation.

Record exact commit, workflow run IDs, row counts, measured byte values, SQL/script versions and limitations in `docs/implementation/test-evidence/SW-DB-001-run-0001.md`.

A green CI run means only that the disposable schema/fixture and listed tests passed. It does not approve the domain specifications, narrative quality, Neon capacity, production data or production migration.

## 6. Explicit exclusions

- No Neon production migration, schema change, seed, import, bulk write, upload, credential change or production connection test.
- No change to existing Neon branch/database configuration.
- No production simulation data or live game activation.
- No change to the adopted BP-02/BP-03 canon; the package must implement against SW-CANON-001. No resolution of BP-04 business distribution.
- No fabricated city map, roads, districts, parcels, addresses or coordinates.
- No full 9,500-person biographies, social graphs, employment histories or NPC schedules; this is a structural/capacity fixture, not a completed world population.
- No police employee, rank, unit, recruitment or career provisioning.
- No crime, case, evidence, hidden offender or investigative content.
- No production backup/PITR configuration changes.
- No public deployment or new application/API surface.
- No change to the fixed BP-01–BP-44 division structure or existing canon.

## 7. Production Neon release gate — separate future approval

A later production rollout cannot begin until all of the following are satisfied:

1. BP-02, BP-03, BP-04 and BP-38 domain/schema specifications are reviewed, semantically complete and individually approved at the versions used.
2. Population-scope/countability rules in SW-CANON-001 are implemented and the 9,500 opening population is reconciled to individual identities without double counting.
3. The actual map dataset is built and validated against SW-CANON-001; BP-04 business baseline/category/site distribution decisions needed by the seed are separately approved, with no invented geography or placeholder businesses.
4. G1 narrative-quality gate has independent human sign-off and the pending manual-review rows are resolved.
5. G2 representative capacity/performance assessment is complete, reconciled against Neon provider accounting and reserve, and capacity is explicitly approved.
6. G3 runtime integration and G4 relevant division approvals are satisfied for the operations being enabled.
7. A fresh read-only Neon baseline is measured immediately before the proposed production operation. Incremental bytes, MB/MiB, projected total, method, assumptions and uncertainty are shown.
8. The exact migration/seed batch, rollback/recovery plan, expected duration, record counts and storage-operation ledger entry are presented.
9. The user explicitly approves that exact Neon production operation. Approval of this GitHub/disposable package is not Neon write approval.

After a separately approved Neon operation, measure actual database/table/index/TOAST growth, reconcile counts and record the result. Do not claim success before verification.

## 8. Approval requested

Approve **SW-DB-001 — Canonical Saltwater World Provisioning and Capacity Proof** for:
- GitHub implementation directly on `main`;
- candidate schema/proposal and deterministic fixture development;
- disposable PostgreSQL full-scale provisioning, regression, storage/performance measurement and restore tests;
- documentation and reproducible evidence.

This approval grants **zero Neon production write authority**. No Neon mutation is included or implied.

## 9. Status

**APPROVED — bounded implementation and disposable verification complete (2026-11-24).** Proposal 0010, deterministic 9,500-person/10,000-business fixture, test-only distribution overlay, acceptance/restore SQL and dedicated CI workflow are committed on `main`. Both Python and disposable PostgreSQL 16 jobs passed in [run 45456851773](https://github.com/Joshuaogri/saltwater/actions/runs/45456851773). The full opening fixture, unique-name reservation, storage/performance measurements, exact-manifest idempotency, person/business content checksums, backup/restore, concurrent 9,999-person final-slot admission, exact 10,000 cap and no-clock-advance checks passed. See [SW-DB-001 run 0001 evidence](../test-evidence/SW-DB-001-run-0001.md). This completion is limited to the approved GitHub/disposable test scope. Neon production write authority remains NONE; no Neon operation has been performed.
