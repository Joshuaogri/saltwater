# Saltwater implementation sequence and dependency plan

**Status:** IMPLEMENTATION PLAN DRAFT — planning only. It grants no division approval and no Neon write permission.  
**Authority:** Approved Saltwater master blueprint BP-01–BP-44 and completed 52→44 semantic audit.  
**Prepared:** 2026-11-23

## 1. Purpose

Move Saltwater from completed specification audit into staged implementation. Build on the existing GitHub/Neon foundation; do not restart the repository or treat documentation as software.

The fixed 44-division structure, Saltwater canon, player agency, exact `bingo` reveal gate, no-offline-time rule, text-first interface and storage/write gate remain binding.

## 2. Verified starting point

### Blueprint
- Master framework and binding canon approved.
- All 44 division specifications exist as `DESIGNED_DRAFT`; individual approval remains separate.
- Semantic audit complete: 52 source divisions, 168 requirements, 60 source acceptance tests and 228 source requirement/test IDs mapped.
- Integrated ownership/interface/canon audit complete. See `docs/blueprint/SALTWATER-WHOLE-BLUEPRINT-SEMANTIC-AUDIT.md`.

### Platform
- Neon project `misty-breeze-20463094`; production branch `br-bitter-rain-bdz9ddid`; database `neondb`.
- Foundation migration `db/migrations/0001_foundation.sql` is applied and recorded as version 1.
- A live connection probe verified a temporary transactional write/read and rolled it back.
- Read-only SQL verification on 2026-11-23 measured `pg_database_size` at **9,306,112 bytes (9.306 MB decimal; 8.875 MiB)** and user relations at **188,416 bytes**.
- Five user tables exist: `sw_core.world_config`, `sw_core.event_type`, `sw_core.simulation_event`, `sw_ops.schema_migration`, `sw_ops.storage_operation`.
- `world_config` contains one Saltwater row; `event_type` and `simulation_event` are empty.
- Benchmark 0005 temporarily created synthetic schema/data on Neon, measured it, then removed the schema; its storage-operation ledger row remains. No production simulation seed data remains.
- Benchmarks 0006–0008 ran on disposable PostgreSQL. Benchmark 0008 produced three repeatable runs at approximately **651.779 MB full disposable database** and **642.728 MB relations**.
- The 16-record narrative fixture passed automated structural/chronology checks. Its manual-review rows remain pending; AI-assisted editorial review is not human sign-off.
- Neon 1 GB production capacity is **NOT APPROVED**; production simulation seeding is **BLOCKED**.
- The repository has SQL migrations/benchmarks, GitHub Actions workflows and specifications, but no executable game runtime/application source code yet.

Provider-reported logical-size metadata around 33.6 MB is a different metric from direct SQL `pg_database_size`; retain method and metric with every baseline.

## 3. Mandatory controls

1. No Neon write by implication. A blueprint, plan, GitHub commit, disposable test or previous approval does not authorise a new migration, schema change, seed/import, bulk write, upload or credential change.
2. Before each proposed Neon-changing operation, measure the live baseline; estimate incremental bytes and MB/MiB with method, assumptions and uncertainty; show projected total; wait for explicit user approval.
3. After an approved operation, measure actual database/table/index/TOAST growth and compare with the estimate.
4. Build and test schema changes first on disposable PostgreSQL.
5. No production simulation data until narrative-quality and capacity gates are approved.
6. Population cap is 10,000 living people total, police included. Opening: 9,000 residents + 500 police = 9,500; 500 is unused headroom.
7. Maintain at least 10,000 distinct businesses without duplicate people/businesses.
8. Simulation time and world activity stop while the player is absent or paused.
9. Text is the complete primary interface; maps/graphics are optional projections.
10. Never reveal hidden culprit/accomplice/perpetrator truth unless the player types exactly `bingo`; never provide unsolicited investigative hints.
11. A designed acceptance criterion is not an executed test. A test passes only with reproducible evidence.
12. Domain divisions retain ownership of their authoritative records.

## 4. Readiness gates before production simulation data

### G1 — narrative-quality sign-off
- Human-review all 16 records in fixture 0001 against the published seven-part rubric.
- Keep manual-review rows pending until actually reviewed.
- Resolve or explicitly accept the disclosed limitations in R-006 (evidence continuity particulars), R-013 (arrest grounds/review record) and other borderline records.
- Do not invent missing source particulars. Automated success and AI-assisted scoring are not human sign-off.

### G2 — capacity and reserve decision
- Benchmark 0008 is repeatable, but its deterministic high-entropy prose does not prove realistic police narrative.
- Use human-reviewed, record-type-specific content and representative distributions to measure row, index, TOAST, query and lifecycle costs on disposable PostgreSQL.
- Retain the 200 MB nominal reserve. The 800 MB working ceiling is a gate, not an approval.
- Reconcile projected workload with direct Neon baseline and the provider's actual capacity/accounting metric.
- Record an explicit decision. Until then, production seeding remains blocked.

### G3 — runtime integration design
The repository has no executable runtime/API yet. Define the smallest supported execution path connecting the ChatGPT player interface to authorised Saltwater domain operations backed by Neon. Enforce permissions and domain rules server-side; distinguish read-only from mutating actions; provide idempotency and audit; never expose credentials. Do not silently add a second database or substitute the approved architecture.

### G4 — division-level design approval
Approve the relevant division specification versions before implementing their domain rules. Master framework approval does not approve all 44 drafts. Record approved versions and affected requirements in the register.

## 4A. First implementation approval package

PKG-001 was explicitly approved by the user on 2026-11-23 for bounded GitHub implementation and disposable PostgreSQL testing. Implementation is in progress on branch `implementation/pkg-001-runtime-city-population`, PR [#1](https://github.com/Joshuaogri/saltwater/pull/1). Run 0001 passed on disposable PostgreSQL 16.16 and Python 3.12.16; see [test evidence](test-evidence/PKG-001-run-0001.md). No Neon migration, seed, or production activation is authorised. Its scope covers the runtime kernel and canonical city/population substrate; BP-04/BP-36 and user-facing interfaces remain downstream dependencies.

## 5. Dependency-led implementation sequence

This is a dependency plan, not permission to write to production. Code, schema drafts, disposable migrations and tests may proceed while Neon production remains unchanged.

### Stage 0 — existing platform foundation (deployed)
**Owners:** BP-38, BP-39, BP-43, BP-44; supporting CI/operations.

Existing deliverables: migration 0001; world configuration and event envelope tables; migration/storage ledgers; database-validation and live-connection workflows; storage benchmark harnesses; disposable narrative fixture.

**Exit evidence:** migration version 1 in live ledger; verified table inventory and baseline; successful connection probe; no production simulation seed data.

### Stage 1 — runtime kernel and shared controls
**Primary divisions:** BP-35, BP-37, BP-38, BP-39, BP-42, BP-43, BP-44.  
**Interface foundation:** BP-40; notification/report contracts BP-41.

1. **BP-38:** stable IDs, schema registry, typed references, transaction boundaries, provenance, append-preserving corrections, constraints and compact storage. Apply the compact-storage standard to every schema/event; benchmark bytes per representative record before any production proposal.
2. **BP-42:** principals/personas, permissions, purpose-limited reads, service identities, secrets, audit and hidden-truth protection.
3. **BP-37:** canonical in-world clock, pause/resume, effective/recorded time, calendar, recurrence and schedule semantics.
4. **BP-35:** deterministic event acceptance/ordering, idempotency, causal dispatch, NPC activation, player-presence gate, replay and failure handling.
5. **BP-39:** save/checkpoint, backup, restore, recovery validation and continuity evidence.
6. **BP-43:** disposable fixtures, schema/invariant, integration, replay, concurrency, storage and evidence harnesses.
7. **BP-44:** versioned configuration, decisions, approvals, release/rollback and traceability.
8. **BP-40:** laptop-style text interface, commands, record views, permission-aware search, read/mutate distinction and honest operation status.
9. **BP-41:** attributable reports/notifications, delivery state, permission filtering, no hidden-truth leakage and no paused game-time progression.

**Exit criteria:** deterministic pause-safe kernel; authoritative permission checks; persistent/auditable event contracts; complete text-only control path; repeatable disposable tests; recoverable checkpoint.

### Stage 2 — canonical city and population substrate
**Primary divisions:** BP-02, BP-03, BP-04, BP-36.  
**Dependencies:** BP-35, BP-37–BP-39, BP-42, BP-43.

1. BP-02: one-city jurisdiction, districts, parcels, addresses, roads, access points and spatial references.
2. BP-03: one person identity/ledger, lifecycle, population membership, 10,000 cap, atomic arrivals/deaths/permanent exits and permanent full-detail promotion.
3. BP-04: buildings, premises, occupancy, property, organisations and at least 10,000 distinct businesses with valid ownership/operator/employment/schedule links.
4. BP-36: households, relationships, social groups, effective-dated links and individual knowledge boundaries.

**Exit criteria:** canonical spatial/person registries; exact population reconciliation; no duplicate people/businesses; 10,000 businesses with valid identity/status/operating basis; time-valid occupancy/relationship histories; no offline world activity.

### Stage 3 — institutional and police-service foundation
**Police structure/workforce:** BP-05–BP-09.  
**Supporting administration:** BP-30–BP-34.

Implement institutional chart and authority catalogue, individual personnel/service records, recruit/career progression, unit membership/deployment, police resources, governance/standards, training, HR and finance.

**Exit criteria:** each officer is one canonical person with one authoritative personnel dossier; rank/grade/position/authority/clearance/qualification/posting are distinct; vacancies, acting appointments, training gates, planned roster, actual attendance and resources reconcile.

### Stage 4 — first operational police loop
**Primary divisions:** BP-10, BP-11, BP-12.  
**Dependencies:** BP-02, BP-05–BP-09, BP-35, BP-37, BP-40–BP-43.

Implement patrol/field tasks, emergency and non-emergency intake, CAD, radio, unit availability, dispatch, incident creation, response, command, handover and closure.

**Exit criteria:** player officer can start shift, patrol, receive a call, be dispatched, attend a location, record actions and close/hand over an incident. Travel, staffing, time, resources and authority reconcile. All actions are inspectable in text.

### Stage 5 — crime, cases and investigation
**Primary divisions:** BP-13–BP-16; expand through BP-17–BP-24.

Implement crime/non-crime taxonomy, classification distinctions, causally grounded occurrence generation, stable case identity/lifecycle, investigative tasks, plans, hypotheses, decisions and reviews.

**Exit criteria:** occurrence truth is separate from report/allegation/intelligence; case chronology and source links persist; concurrent, cold, linked and reopened cases work; the player directs investigation without unsolicited lead ranking or solution hints.

### Stage 6 — participants, collection, scenes and evidence
**Primary divisions:** BP-17–BP-24.

Implement victim/witness and suspect/offender roles, interviews/statements, surveillance, intelligence, scene control, exhibit registration/custody and forensic examination.

**Exit criteria:** originals remain immutable; role/suspicion does not imply guilt; exhibits have identity/provenance/continuity; source ownership is preserved; forensic conclusions identify method, examiner, limitations and uncertainty; relevant people receive permanent full simulation.

### Stage 7 — arrest and justice continuity
**Primary divisions:** BP-25–BP-29.

Implement arrest/warrant/search/seizure decisions and execution, custody handover/welfare, legal processes, court adjudication and correctional execution.

**Exit criteria:** operational action, custody, legal filing, judicial decision and sentence execution remain separate linked records. No unconfigured fictional authority is invented. Acquittals, dismissals and unresolved outcomes remain possible.

### Stage 8 — full-world operation, scale and quality
**Owners:** BP-35, BP-37–BP-44 and every domain owner.

Expand event-driven world activity, business/service dependencies, environmental and civic schedules, reports, observability, population/business-scale tests, long-duration replay, storage, recovery, permissions and narrative-quality evaluation.

**Exit criteria:** approved requirements have reproducible tests; no impossible concurrent states or offline progression; provenance is complete; capacity/performance are measured; production growth stays within approved limits.

## 6. First playable vertical slice

Prove one connected officer workflow rather than isolated tables:

1. Create a recruit/player-officer persona linked to one canonical person and personnel record.
2. Assign valid training/career state, unit and duty roster; distinguish planned roster from actual attendance.
3. Start a shift and patrol using canonical geography, time and police resources.
4. Receive a call, triage an incident and dispatch a feasible unit.
5. Attend, record field observations/actions, link an occurrence and open a case when justified.
6. Access participants/source records and conduct a player-directed interview or other authorised investigative action.
7. Control a scene, register an exhibit, preserve custody/provenance and request a forensic examination.
8. Preserve decisions, chronology, reports and outcomes across pause/restart.
9. Confirm hidden offender truth remains unavailable until the exact `bingo` command.

This is the first end-to-end proof, not a substitute for the full 44-division simulation.

## 7. Immediate next work

1. PKG-001: runtime kernel, city/population foundation, and persistent provider-neutral actor/session/policy/grant/audit schema proposal. The 0003 schema is tested only on disposable PostgreSQL; no identity provider, credential issuer, durable application adapter, route integration or hidden-truth store is selected or deployed. Next: implement trusted provider adapter and durable verifier/audit adapters, then route all game reads/writes through the same low-friction authorization service. Preserve a simple player login/persona flow; avoid unnecessary approval prompts during ordinary play. Keep calendar and population-scope decisions open until resolved.
2. Human sign-off of narrative fixture 0001; keep manual-review state honest.
3. Final text-quality/capacity assessment and explicit decision on the 1 GB Neon allowance with 200 MB reserve.
4. Define the minimal ChatGPT ↔ authorised runtime ↔ Neon integration contract.
5. Prepare subsequent Stage 1 and Stage 2 implementation packages: entity/event contracts, schema drafts, disposable PostgreSQL migrations, acceptance tests and measured storage estimates.
6. Present every proposed production Neon operation separately for explicit approval. No production seed or domain migration is included in this plan.

## 8. Completion-state discipline

Track separate states for every division/item:

- **Design:** draft / reviewed / approved.
- **Implementation:** not started / in progress / implemented.
- **Test:** not started / passed / failed / blocked, with execution evidence.
- **Verification:** not started / verified, with reproducible evidence.
- **Production activation:** not proposed / awaiting approval / approved for exact operation / deployed / measured.

A GitHub commit, SQL file, successful benchmark, migration workflow no-op or AI review does not automatically advance every state.
