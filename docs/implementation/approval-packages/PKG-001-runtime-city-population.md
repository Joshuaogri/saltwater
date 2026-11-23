# PKG-001 — Shared runtime kernel and canonical city/population foundations

**Status:** APPROVED FOR IMPLEMENTATION — IN PROGRESS; NOT APPROVED FOR PRODUCTION DEPLOYMENT  
**Package version:** 1.0  
**Target repository:** `Joshuaogri/saltwater`, branch `main`  
**Blueprint:** fixed BP-01–BP-44; no division is renamed, split, merged or reordered.  
**Database:** Neon PostgreSQL production; no database action is authorised by this package.

## 1. Approval sought

Approve the bounded implementation scope below so that code, isolated disposable-PostgreSQL migrations and tests can be implemented. This approval, if given, will **not** authorise any Neon migration, seed, import, upload, credential change or production activation. Those require a separate, operation-specific approval after a fresh live baseline and measured storage estimate.

The package is divided into two deliverables:

- **PKG-001A — Shared runtime kernel:** runtime lifecycle, pause/presence gate, fictional clock, event envelope, idempotency and causal links, transaction contract, persistence/recovery interfaces and permission enforcement points.
- **PKG-001B — Canonical city and population substrate:** one Saltwater sovereign/city identity, versioned spatial entities, canonical person identity, population/life-state ledger, residence history and hard cap enforcement.

## 2. Existing verified foundation

As of the latest repository audit:

- Migration `0001_foundation.sql` is applied and recorded as schema version 1.
- Existing tables: `sw_core.world_config`, `sw_core.event_type`, `sw_core.simulation_event`, `sw_ops.schema_migration`, `sw_ops.storage_operation`.
- World configuration identifies one Saltwater city-state/city and fixes the population ceiling at 10,000.
- `event_type` and `simulation_event` are empty; there are no resident/person, geography-domain, business, case or evidence records.
- Direct SQL baseline: `pg_database_size = 9,306,112 bytes` (9.306 MB decimal; 8.875 MiB); user relations = 188,416 bytes.
- Provider logical-size metadata of 33,611,776 bytes is a different metric and must not be compared with `pg_database_size`.
- No executable game runtime/application source code exists yet. This package therefore begins with the persistence and service contracts, not a claim that the game is already playable.
- The 1 GB production capacity decision remains NOT APPROVED; production simulation seeding remains BLOCKED.

## 3. Exact scope and ownership

| Work item | Owner | Included in this package |
|---|---|---|
| Runtime lifecycle/event orchestration | BP-35 | Kernel contracts, state machine, event ordering, idempotency, causal links and failure states |
| Fictional clock/scheduling foundation | BP-37 | One persisted clock, monotonic world tick, calendar fields, freeze/resume semantics |
| Record/schema integrity | BP-38 | Typed IDs/references, constraints, transactions, migration proposal and storage measurements |
| Persistence/recovery interface | BP-39 | Checkpoint, backup/restore, replay and recovery contracts/tests |
| Security boundary | BP-42 | Authoritative actor/permission checks and hidden-truth access firewall contracts |
| Test evidence | BP-43 | Disposable DB test suite, invariant/concurrency/storage/recovery tests |
| Change approval | BP-44 | Versioned package, decision record, implementation-vs-deployment approval separation |
| Canonical geography | BP-02 | City-state/city identity, versioned spatial hierarchy and future geometry interface |
| Population | BP-03 | Person identity, life/population state, residence, history, cap enforcement |

**Interfaces only; not implemented here:** BP-04 business/property records; BP-36 relationship semantics; BP-40 player interface; BP-41 notifications. Their contracts must be respected and their implementation follows in dependency order.

## 4. Binding invariants

1. One sovereign city-state, one playable city, one jurisdiction. No external playable geography.
2. The exact city boundary, map dimensions, districts, neighbourhood counts, roads and geometry are not yet approved. Do not invent or seed them.
3. Living population hard cap: **10,000 total**, including police and every other role.
4. Opening population target: **9,000 residents + 500 police = 9,500**. The remaining 500 is unused headroom, not an automatic generation target.
5. A person has one canonical identity. Roles, employment, memberships and relationships never create duplicate people or extra population counts.
6. A failed population admission must leave no partial person, state, residence, job, relationship or event.
7. Every case-relevant person is permanently promoted to full persistent detail; no detail already established may be discarded.
8. Simulation time and all world activity stop when the player is absent or the simulation is paused. No offline catch-up.
9. Hidden offender/accomplice truth remains protected unless the player types exactly `bingo`. No runtime, logs, search, event payload, diagnostics or derived view may leak it.
10. Store the smallest practical lossless representation. Canonical facts are stored once and referenced; no duplicated profiles or full snapshots per event. Preserve meaning, history, provenance and evidential integrity.

## 5. Proposed architecture

### 5.1 Runtime kernel

One persisted singleton runtime state owns:

- lifecycle state: stopped, ready, running, paused, recovering, safe-halt;
- player-presence gate;
- monotonic committed world tick;
- fictional calendar day and minute-of-day;
- last committed event/watermark.

The runtime service is the only authorised coordinator of state transitions and due work. A domain handler validates and mutates its own records. The runtime does not decide domain truth.

Every event has a stable ID, event type/version, world tick, optional causation/correlation references and optional idempotency key. Domain participants and locations are typed references, not copied profiles. A retry with the same idempotency key cannot repeat the domain effect. A one-time bootstrap window permits reviewed initial geography/person records at tick zero; it must be closed before the runtime can start and cannot be reopened.

**Pause rule:** world tick may advance only from a committed running state while player-present is true. No scheduler, NPC, event queue, narrative generation or recovery routine may advance fictional time while stopped, paused or absent. Technical audit timestamps may continue; they are not fictional time.

### 5.2 Canonical city/geography

Create one sovereign-territory identity and one child playable-city identity. Their first versions may exist without geometry. No boundary coordinates, CRS, district, neighbourhood, parcel, road or landmark is fabricated.

Spatial entities use stable IDs, controlled type codes, optional parent links and immutable version rows. Geometry bytes remain absent until the user approves the fictional coordinate system, geometry format and boundary design. External places remain non-playable references.

### 5.3 Canonical population

Separate immutable person identity from current population/life state and append-only state history. Residence is an effective-dated link to a canonical spatial ID.

Proposed countability model has three scope states:
- 0 unresolved — not eligible for authoritative population activation;
- 1 included — counts if living;
- 2 excluded — does not count.

A transactional singleton counter serialises concurrent admissions and is reconciled against the canonical person-state rows. The 10,001st living included person is rejected atomically. Person identities, spatial identities and their histories cannot be deleted or silently rewritten. Roles and memberships are separate future domain links and do not alter the count.

No person seed is included. The 9,500 opening population requires a separate, fully reviewed seed package with unique identities and a measured storage estimate. The bootstrap window is a one-time initialisation facility, not a general bypass of runtime controls.

## 6. Files prepared

- SQL proposal: [`db/proposals/0002_runtime_city_population.sql`](../../../db/proposals/0002_runtime_city_population.sql)
- Disposable acceptance matrix: [`PKG-001-test-matrix.md`](PKG-001-test-matrix.md)
- Compact storage standard: [`docs/storage/COMPACT-STORAGE-DESIGN.md`](../../storage/COMPACT-STORAGE-DESIGN.md)
- Implementation sequence: [`docs/implementation/IMPLEMENTATION-SEQUENCE-AND-DEPENDENCY-PLAN.md`](../IMPLEMENTATION-SEQUENCE-AND-DEPENDENCY-PLAN.md)

The SQL file is a proposal only. It extends the existing foundation with a validated runtime state machine, world-tick/presence guard, one-time bootstrap gate, event causality/idempotency, immutable geographic identity/versioning, canonical person identity/profile history, a race-safe population counter, population state/history, residence and typed event references. It seeds only the two canonical geographic root identities and a stopped runtime singleton. It inserts **zero people, businesses, cases, evidence or invented geography**.

## 7. Unresolved decisions — must remain open

| ID | Decision | Why it matters | Safe treatment until decided |
|---|---|---|---|
| D-001 | Exact population-scope rules for residents, temporary residents, visitors, transient persons and off-map case participants | Prevents count loopholes and incorrect admission/departure | Scope status remains unresolved until classified; no production person seed |
| D-002 | Fictional calendar, day length, epoch and calendar display | Defines the meaning of calendar day/minute and deadlines | Persist monotonic tick; do not invent calendar semantics |
| D-003 | Fictional local coordinate reference system and geometry encoding | Prevents false precision and extension lock-in | Geometry remains null; no PostGIS dependency assumed |
| D-004 | Sovereign/city boundary geometry and district/locality inventory | Canonical geography is not yet specified | Create root identities only; no invented map |
| D-005 | Authenticated player/session identity source and actor context | Runtime presence and permission checks must be authoritative | Define an adapter contract; no secrets or provider changes |
| D-006 | Runtime application/API execution host | No executable runtime exists in repository | Implement a small service boundary without introducing a second database |
| D-007 | Final event taxonomy/version policy | Domain events have multiple owners | Start with a minimal controlled kernel catalogue; domain owners extend through versioned contracts |

D-001 and D-005 are required before authoritative population admission and player-controlled runtime activation. D-002 is required before calendar-facing simulation play. D-003/D-004 are required before any detailed map geometry is seeded. D-006 is required before the game can be launched as an executable playable application.

## 8. Migration and data-safety approach

1. Review the SQL proposal and resolve its open decisions/technical comments.
2. Implement the same schema in disposable PostgreSQL first.
3. Test migration from an exact copy of the current version-1 schema; verify migration preconditions and rollback.
4. Run positive, negative, boundary and concurrent tests.
5. Benchmark empty-schema overhead and representative person/event/history rows; measure heap, index, TOAST and bytes per record.
6. Review backup/restore and replay evidence.
7. Prepare a separate Neon execution request with a fresh baseline, incremental estimate in bytes/MB/MiB, uncertainty and projected total.
8. Wait for explicit approval of that exact Neon operation before any production write.

No production seed is part of this package. No schema migration may be run against Neon as a test. Implementation branch and pull request are open. Run 0001 passed on disposable PostgreSQL 16.16: both migrations applied, the listed database acceptance checks passed, and all six Python kernel tests passed. Whole-database storage measured 8,756,247 bytes; this is not a migration delta or production estimate. See [run evidence](../test-evidence/PKG-001-run-0001.md). Further concurrency, recovery, permission and persistence-adapter tests remain outstanding.

## 9. Acceptance tests required before implementation can be marked tested

| ID | Test | Required result |
|---|---|---|
| K-001 | Singleton runtime state | Exactly one state/clock row |
| K-002 | Start/pause/resume/stop transitions | Only valid transitions accepted |
| K-003 | Tick while paused/stopped/player absent | Rejected; tick unchanged |
| K-004 | Normal event while not running/present | Rejected |
| K-005 | Runtime lifecycle events | Allowed only through lifecycle command path |
| K-006 | Tick ordering and causation | Monotonic tick; parent/correlation references resolve |
| K-007 | Duplicate idempotency key | No duplicate domain effect |
| K-008 | Retry after simulated failure | Recoverable, no double-commit |
| G-001 | Geographic root identities | Exactly one sovereign territory and one playable city |
| G-002 | Boundary containment | No playable geography outside sovereign territory |
| G-003 | Unapproved geometry | No geometry fabricated or activated |
| G-004 | Spatial version correction | Prior version and historical references remain resolvable |
| P-001 | Canonical person identity | One person row per individual; mutable name does not change ID |
| P-002 | Population count | Counts living included person identities exactly once |
| P-003 | 10,000 boundary | 10,000 accepted; 10,001st rejected |
| P-004 | Concurrent admission race | Two simultaneous admissions cannot exceed cap |
| P-005 | Failed admission atomicity | No partial identity/state/history/residence/event remains |
| P-006 | Unresolved/excluded scope | Not silently counted or silently promoted |
| P-007 | Population history | Every state transition appends immutable history |
| P-008 | Residence chronology | Effective-dated links retain prior residence |
| S-001 | Storage footprint | Bytes per person/event/history row measured on disposable PostgreSQL |
| S-002 | Compactness regression | Duplicate profile payloads and unjustified indexes rejected |
| R-001 | Backup/restore | Canonical IDs, event order, population count and clock watermark reconcile |
| A-001 | Permission bypass | Direct API/query path cannot bypass actor permissions |
| A-002 | Hidden-truth firewall | No leak through events, logs, search, summaries or exports; only exact `bingo` trigger reveals |

A test definition or GitHub commit is not a test pass. Each executed test must retain commit, schema, fixture, environment, inputs, result and evidence.

## 10. Storage estimate and limits

No defensible production migration estimate is claimed yet. The current database baseline is known, but the schema proposal has not been executed or measured in disposable PostgreSQL. Catalog growth, indexes, trigger functions and actual tuple overhead must be measured, not guessed.

The first benchmark will report:
- empty schema/migration delta;
- bytes per canonical person row plus population-state row and required indexes;
- bytes per lifecycle/event/history transition;
- 9,500-person projected opening baseline using representative names and state distribution;
- 10,000-person cap test;
- low/median/high narrative and source-reference overhead separately.

The 9,500-person seed estimate is not a seed authorisation. No production capacity approval is inferred.

## 11. Explicit approval boundary

If approved, PKG-001 authorises only implementation of the bounded contracts and disposable test work described above. It does not:
- approve every requirement in BP-02, BP-03 or BP-35–BP-44;
- settle D-001 through D-007;
- approve the exact map, boundary, districts or fictional calendar;
- approve the 9,500-person seed or 10,000-business seed;
- authorise Neon schema/data writes, migrations, uploads, credential changes or production activation;
- mark any division implemented, tested or verified before evidence exists.

**Requested decision:** approve or reject PKG-001 scope for GitHub implementation and disposable PostgreSQL testing. Neon deployment and all production seed data remain separate future decisions.
