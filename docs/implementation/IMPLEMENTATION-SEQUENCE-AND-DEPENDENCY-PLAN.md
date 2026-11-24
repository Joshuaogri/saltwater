# Saltwater implementation sequence and dependency plan

**Status:** IMPLEMENTATION PLAN — active delivery plan. It grants no division approval and no Neon write permission. All repository development is performed directly on `main`.  
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
- The repository now includes the shared runtime kernel and a first text command-interface application layer (`runtime/player_interface.py`). Persistent player saves, canonical officer/career creation and the full game application are not yet implemented.

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

PKG-001 was explicitly approved by the user on 2026-11-23 for bounded GitHub implementation and disposable PostgreSQL testing. Implementation was merged directly into `main` on 2026-11-23 (merge commit `0fb5eac232a8c414a1488f01f7a638b4b6554a7a`; historical PR [#1](https://github.com/Joshuaogri/saltwater/pull/1) is closed and merged). Future development takes place only on `main`; do not create or use development branches or PR-based workflows. Disposable PostgreSQL and Python test evidence is recorded in the PKG-001 run reports. No Neon migration, seed, or production activation is authorised. Its scope covers the runtime kernel and canonical city/population substrate; BP-04/BP-36 and user-facing interfaces remain downstream dependencies.


## 4B. PKG-002 — player command interface foundation

The first PKG-002 application-layer increment is committed directly to `main`. It adds a game-native player profile value object and a compact command router for `help`, `status`, `profile`, `start`, `pause`, `resume` and `quit`. Lifecycle commands delegate to the shared runtime kernel; pause and quit preserve the frozen-world-time invariant. The interface does not invent an officer/personnel identity or career, create local side-database saves, expose hidden truth, or bypass the bootstrap gate. GitHub Actions now targets `main` and runs its unit tests.

This increment is not yet a complete playable/persistent game. Durable player sessions, BP-03 person linkage, BP-06 personnel, BP-07 recruit career creation, the Neon runtime adapter integration and explicit turn/tick scheduling remain to be implemented and tested against disposable PostgreSQL. Neon production remains untouched. See `docs/implementation/approval-packages/PKG-002-player-command-interface.md`.

## 4C. PKG-003 — recruit-entry vertical slice

PKG-003 was approved on 2026-11-23 and implemented directly on `main`. The disposable-only proposal `db/proposals/0004_recruit_entry.sql` defines pending intake, canonical person admission, personnel appointment, explicitly authorised recruit supervision and career episode creation. The PostgreSQL adapter is in `runtime/recruitment.py`; the text interface exposes `recruit` and `career` commands when a trusted adapter is injected. The recruit-specific SQL acceptance script and Python adapter tests are included in the main-branch disposable PostgreSQL workflow. The full workflow passed on 2026-11-23: [run 115](https://github.com/Joshuaogri/saltwater/actions/runs/45275219362), commit `9235b36642e5c287d8e0fd1ec33398308ceb6ff2`.

A pending request creates no canonical person or serving career. Appointment requires an active recruitment approver and a separately authorised active established supervisor; `established` is a service-standing label, not a substantive rank. Successful appointment creates one person, one population membership, one personnel dossier and one recruit career episode atomically. The proposal preserves event provenance and uses the existing population counter lock.

**Current limitation:** the text commands honestly report unavailable until the trusted recruitment adapter is connected to the durable player/runtime path. End-to-end ChatGPT/runtime/Neon integration is not claimed. Proposal 0004 has not been applied to Neon; no production data or configuration was changed. See `docs/implementation/approval-packages/PKG-003-recruit-entry-vertical-slice.md` for scope and evidence state.

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

1. **Gameplay implementation takes priority over further ChatGPT transport work.** PKG-001 through PKG-006 provide a verified platform/player-command foundation. PKG-007 remains proposed and is deferred; it is not the next implementation task.
2. **BP37-01 — Canonical Clock Core and Schedule Eligibility** is implemented and verified as a bounded slice (see section 9). BP-37 remains partially implemented; calendar/civil-time, richer recurrence, cancellation/versioning, occurrence history and abandoned-claim recovery remain outstanding.
3. **BP35-01 — Deterministic Event Intake and Dispatch Core** was approved, implemented and verified on `main`. Python/disposable PostgreSQL regression [45369237153](https://github.com/Joshuaogri/saltwater/actions/runs/45369237153) and database migration validation [45369237232](https://github.com/Joshuaogri/saltwater/actions/runs/45369237232) passed. It reuses the BP-37 tick, runtime lifecycle and event ledger. The full BP-35 division remains incomplete; NPC/world simulation, replay, fairness/back-pressure and abandoned-claim recovery remain outstanding. See `docs/implementation/approval-packages/BP35-01-deterministic-event-intake-and-dispatch.md` and `docs/implementation/test-evidence/BP35-01-run-0001.md`.
4. **Next:** prepare BP39-01 checkpoint, restore-validation and explicit abandoned-claim recovery. This directly addresses the safe-pause boundary: an abandoned BP35 claim currently blocks pause/stop/recovery until a controlled recovery action resolves it. BP-39 must reconcile checkpoint watermarks with BP-35 event work and BP-37 world tick without inventing RPO/RTO, provider capabilities or Neon production changes.
5. Then continue BP-40 text gameplay controls, BP-41 reporting/notifications, and BP-43/BP-44 verification/configuration coverage, reconciling existing BP-38/BP-42 foundations rather than duplicating them.
4. Then begin Stage 2: BP-02 geography, BP-03 population/person simulation, BP-04 built world/businesses and BP-36 relationships. Respect unresolved canon decisions; do not invent exact map geography or population-counting policy.
5. Human sign-off of narrative fixture 0001 and the final text-quality/capacity decision remain separate gates. Production simulation seeding remains blocked until explicitly approved.
6. Present every proposed production Neon operation separately with measured baseline, incremental estimate and projected total. No production seed or domain migration is authorised by this plan.

## 8. Completion-state discipline

Track separate states for every division/item:

- **Design:** draft / reviewed / approved.
- **Implementation:** not started / in progress / implemented.
- **Test:** not started / passed / failed / blocked, with execution evidence.
- **Verification:** not started / verified, with reproducible evidence.
- **Production activation:** not proposed / awaiting approval / approved for exact operation / deployed / measured.

A GitHub commit, SQL file, successful benchmark, migration workflow no-op or AI review does not automatically advance every state.

## 4C. Durable player-application composition increment

A trusted server-side composition root is now implemented at `runtime/application.py`. `create_postgres_player_application(connect, profile)` wires one shared trusted PostgreSQL connection factory into the durable `PostgresRuntimeStore`, `PostgresRecruitmentService`, `RuntimeKernel` and `PlayerCommandInterface`. It is lazy and performs no connection, migration, seed, or write during construction. The composition contract is covered by `tests/pkg001/test_player_application.py` and the `main` CI workflow.

This is an application assembly increment, not a deployed ChatGPT/API transport or an authenticated public endpoint. The host must authenticate the player and enforce authorization before exposing commands; database credentials remain server-side. The next runtime work is to bind verified player sessions and authorization decisions to command execution, then exercise the composed commands against disposable PostgreSQL. Neon production remains unchanged and the production-write gate remains in force.


## 4D. Session-bound player command gateway increment

`runtime/application.py` now provides `bind_authorized_player_commands(...)`, which binds one application instance to an expected authenticated principal and the corresponding game-player resource. Every recognised one-word command is mapped to a command-specific `player.command.<name>` action and must receive an explicit allow decision for purpose `gameplay`. The gateway rejects denied decisions and principal mismatches before dispatch; unknown commands are denied. The existing authorization service verifies session state and records the decision through its configured audit sink, failing closed if audit persistence fails.

`tests/pkg001/test_player_application.py` covers successful dispatch only after authorization, wrong-principal denial, unknown-command denial, and invalid gateway construction. The existing Python CI step runs this suite. This remains a trusted in-process boundary: the host must supply the correct principal-to-player binding, a PostgreSQL-backed session verifier, durable audit sink and explicit grants. The command gateway does not issue credentials, create grants, expose an HTTP endpoint, or apply migrations. Direct access to the underlying command router must remain inside the trusted host. Neon production remains unchanged.

**Next:** connect the accepted player/recruit identity outcome to session issuance, then expose one trusted host entry point. Do not add broad default grants or enable production access as part of this increment.


## 4G. Game-native PostgreSQL session lifecycle

`runtime/postgres_sessions.py` provides `PostgresSessionLifecycle` for trusted server-side session issuance and revocation. Issuance requires an active principal and an active policy version, creates a high-entropy opaque credential, and persists only its SHA-256 digest. Session identity and expiry are immutable; revocation uses the existing one-way session lifecycle trigger. The composed player application exposes this service as `sessions`; it does not add a public endpoint, identity provider, automatic permission grant, or default access policy.

Disposable PostgreSQL tests verify issuance, digest-only persistence, successful verification, one-time revocation, repeated-revocation rejection, inactive-principal rejection and invalid lifetime rejection. The earlier grant-provider test failure was a test-harness mistake: it attempted to fetch a result from an INSERT without `RETURNING`; the test has been corrected. The replacement CI run must pass before this increment is marked verified. Neon production remains untouched.

**Next:** bind player creation/intake to a principal and session only after the recruit/player identity workflow has an explicit accepted outcome; then add a single trusted host entry point and full command coverage. No public transport is implied.


## 4F. Database-backed permission grant resolution

`runtime/postgres_security.py` now provides `PostgresGrantProvider`, which loads only unrevoked, currently valid grants belonging to the active policy version. `AuthorizationService` accepts this provider and reloads grants for each decision, so grant revocation and policy activation changes take effect without restarting or rebuilding the player application. The adapter is read-only; it does not issue grants or change policy.

The disposable PostgreSQL test executes the same authorised player `profile` command using the database-backed grant provider, revokes the grant, then repeats the command and confirms immediate default-deny behaviour and both durable audit outcomes. This is not a production grant policy or a blanket player role. No Neon schema or data has been changed.

**Next:** complete a security review of the command boundary and add a narrow game-native session lifecycle service (issue/revoke) with opaque credentials, hashed persistence and no public transport until the host integration is ready.


## 4E. PostgreSQL-backed player command integration tests

`tests/pkg001/test_postgres_security.py` now exercises the composed application through the real PostgreSQL session verifier and audit sink. One test grants only the exact player's `profile` command, executes it through the gateway, and checks the persisted allow audit. A companion test supplies no grant, confirms command dispatch is denied, and checks the persisted default-deny audit. These tests run in the disposable PostgreSQL workflow after the security proposal is applied; they create no Neon production data.

This proves the trusted in-process composition path for one read-only player command and its default-deny case. It does not yet implement persistent grant loading from `sw_auth.permission_grant`, session issuance/revocation APIs, external transport, or a player-facing client. The current integration test supplies explicit grants to the authorization service, so no broad role grants are implied.


## 4H. Fail-closed player command parsing and principal-bound audit

The player command gateway now rejects empty input, malformed shell quoting and multi-token input before authorization or command dispatch. Only a single recognised command token reaches the authorization service. The gateway supplies its bound principal ID to `AuthorizationService.decide`; a credential for a different principal produces a `principal_mismatch` denial that is itself appended to the configured audit sink. No command is dispatched for that decision.

Tests cover malformed/empty/multi-token input, wrong-principal denial and the corresponding audit record. This is still a trusted in-process command boundary; no public transport or production policy is enabled. The next increment is to bind accepted player intake to a principal and session, then compose a single trusted host entry point. Neon production remains unchanged.


## 4I. PKG-004 proposal — accepted-player identity and session activation

PKG-004 is drafted at docs/implementation/approval-packages/PKG-004-player-identity-session-activation.md and awaits explicit user approval. It defines the narrow transition from a resolved provider-neutral player principal to an immutable player/person binding and a durable session, gated on an accepted recruit career. The proposed transaction must bind the canonical person from the accepted personnel/career records and issue a digest-only session credential without granting permissions. It excludes public login transport, identity-provider selection, automatic grants and all Neon production writes. No PKG-004 implementation has started; its schema proposal, Python adapter and disposable PostgreSQL tests are contingent on approval.

**Verification update:** the command-gateway hardening in section 4H passed the Python workflow and disposable PostgreSQL workflow on commit 50cd205b9d9971370b812d172822a7164317a7f0. The implementation-plan and PKG-004 proposal documents are committed separately on main; documentation commits do not substitute for implementation or test evidence.


## 4J. PKG-004 accepted-player identity and session activation

PKG-004 was explicitly approved on 2026-11-24 for repository implementation and disposable PostgreSQL testing only. Proposal `0005_player_identity_activation.sql` adds an immutable one-to-one principal/player/canonical-person binding. The database resolves the person only through an accepted active recruit career, active personnel record and living in-scope person record. It rejects pending or inconsistent identity state, and prevents reassignment of an established principal/person link.

`runtime/player_activation.py` exposes one trusted in-process operation. It invokes the binding function and the existing `PostgresSessionLifecycle.issue_in_transaction` on the same connection and transaction, so a failed session insert rolls back the binding. Session credentials remain high-entropy, one-time returned values; only SHA-256 digests are persisted. The canonical person ID is attached to the session. Activation does not grant permissions, expose a public route, or bypass the existing command gateway.

The application composition root now exposes the activation service. Python adapter tests cover the shared transaction, canonical-person linkage, digest-only persistence and rollback. The recruit-entry disposable acceptance script now exercises accepted and pending-player binding, same-identity replay and competing-principal denial. CI must pass before this increment is marked verified. No Neon production migration or data change has been made.

**Next:** verify the complete PKG-004 Python and disposable PostgreSQL CI runs, correct any failures, record measured schema/record storage overhead, and then prepare the next bounded player-facing runtime increment. Neon remains the permanent production database; production activation remains separately gated.


**PKG-004 verification result:** Passed on implementation commit `e505c159dd8e11d368c043c1f83af2e140899186`. Python and application composition tests passed; disposable PostgreSQL workflow [45288422056](https://github.com/Joshuaogri/saltwater/actions/runs/45288422056) and database migration validation [45288422078](https://github.com/Joshuaogri/saltwater/actions/runs/45288422078) passed. The acceptance run denied pending/rejected intake, inactive/non-player principals and activation replay; it confirmed one-to-one immutable binding, accepted-person session linkage, digest-only storage and no automatic grants. Disposable storage: schema growth 90,112 bytes; binding/session tuple payloads 104/161 bytes (265 combined); identity-binding relation plus indexes 49,152 bytes. Neon production remained unchanged.

**PKG-004 state:** Design approved; implementation complete; Python and disposable PostgreSQL tests passed; implementation verified. Production activation: not proposed and not approved.


## 4K. PKG-005 — authenticated player command execution (proposed)

PKG-005 was explicitly approved by the user on 2026-11-24 for repository implementation and disposable PostgreSQL testing only. Its implementation is committed to `main`; automated verification is pending. The bounded objective is to connect the PKG-004 activated session to the existing command gateway without duplicating security services. A trusted in-process entry point will derive principal identity from `PostgresSessionVerifier`, resolve the immutable principal/player/person binding and player profile/career from PostgreSQL, verify that the session's active-person ID matches that binding, and dispatch through the existing `AuthorizationService` gateway. Every command remains default-deny and individually grant-controlled; the durable audit sink and immediate session/grant revocation checks remain authoritative.

The package proposes application code and tests only, with no new persistent schema. It excludes public API/ChatGPT transport and external identity-provider work. Implementation adds `runtime/player_command_runtime.py`, unit tests, a disposable PostgreSQL integration test and CI steps. It adds no persistent schema. Neon production remains untouched.



## 4L. PKG-005 authenticated player command execution

PKG-005 approval was received on 2026-11-24. The new `PostgresPlayerCommandRuntime.execute(credential, command_text)` is the single trusted in-process command entry point. It derives the principal only from `PostgresSessionVerifier`, resolves exactly one immutable `sw_player.identity_binding`, requires the session active-person and principal canonical-person links to match, and constructs `PlayerProfile` from PostgreSQL profile/career/personnel records. Caller-supplied identity, profile, career, role and permission values are not accepted.

The runtime then dispatches through the existing `AuthorizedPlayerCommandGateway`. That gateway re-verifies the credential and re-evaluates the explicit command grant on every command, preserving immediate session/grant revocation, default-deny behavior and durable authorization audit. Invalid/revoked sessions with an otherwise resolvable player binding reach the gateway for audited denial; inconsistent or missing identity context fails closed before dispatch. No command read advances world time, and no grants or identity records are created by context resolution. `start` now supports explicit re-entry after `quit` by transitioning through STOPPED → READY → RUNNING; it does not silently resume a paused simulation or bypass bootstrap closure.

Added `tests/pkg001/test_player_command_runtime.py` for context, mismatch, fail-closed and gateway behavior, and `tests/pkg001/test_player_command_runtime_postgres.py` for accepted-recruit activation, authoritative profile output, explicit grant, durable allow audit, session revocation and durable denial audit. The disposable PostgreSQL workflow runs both suites. Verification passed on implementation commit `95c27d45c96854c565a280b0b00048a977056208`: Python tests passed; [full disposable PostgreSQL workflow](https://github.com/Joshuaogri/saltwater/actions/runs/45292530120) passed, including the PKG-005 end-to-end command test, explicit quit/re-entry without world-time advance, 10,000-person population/concurrency checks, database access boundary and backup/restore; [database migration validation](https://github.com/Joshuaogri/saltwater/actions/runs/45292528450) passed. The integration exposed and corrected a pre-existing seven-placeholder/eight-argument recruitment adapter mismatch. Disposable fixture sequencing now preserves bootstrap immutability and uses the committed runtime tick. No new persistent schema was added and Neon production remains untouched. **PKG-005 is verified complete.**


## 4M. PKG-006 — trusted host session context and ChatGPT command contract (proposed)

PKG-006 was approved on 2026-11-24, implemented and verified. It defines a provider-neutral adapter between trusted host context and the PKG-005 authenticated player command runtime. Model-controlled input is limited to one allowlisted command and an optional request reference; host identity and session credentials are resolved server-side and never returned to the model. The typed adapter, integration contract, machine-readable tool schema and Python tests are committed on main. Full disposable PostgreSQL/Python CI passed in run [45294966792](https://github.com/Joshuaogri/saltwater/actions/runs/45294966792). A deployed endpoint/plugin, external identity provider, persistent schema and all Neon production operations remain excluded.**


## 4N. PKG-006 trusted host session context and ChatGPT command contract

PKG-006 was approved on 2026-11-24 for repository implementation and Python testing only. The provider-neutral `runtime/player_host_adapter.py` keeps trusted host context separate from model-controlled command input. The host credential provider resolves the opaque Saltwater game-session credential server-side; the adapter passes it only to `PostgresPlayerCommandRuntime.execute`. It does not expose identity overrides, database access, session issuance, player activation or grant creation.

The model-visible request is limited to one allowlisted command and an optional bounded request reference. Unsupported, argument-bearing and multi-command input is rejected before credential resolution. Missing/expired context, missing credentials and adapter failures fail closed. Provider/runtime exception details and any accidental credential echo are replaced with generic responses.

Added `docs/integration/CHATGPT-PLAYER-RUNTIME-CONTRACT.md`, machine-readable `docs/integration/player-command-tool.schema.json`, and `tests/pkg001/test_player_host_adapter.py`. The disposable PostgreSQL workflow now runs the PKG-006 Python unit suite. Implementation commits: adapter `9223c50bc1e34e7fc4c0aa592630342c402ab28d`; tests `b0e69763458f55d2ad91942018fd7fd4f08c60ac`; contract `1c9b4940d55ce9591fbf4f31607b156dc687a5fd`; schema `890feb3eef59744bfec6b0dda82de84f24e4e1ee`; CI `25c22dfebd0e7361bc9af0e3c7d6f829ac5ece9b`. Package and plan documentation updates follow. **Verification passed:** Python and full disposable PostgreSQL workflow [45294966792](https://github.com/Joshuaogri/saltwater/actions/runs/45294966792) passed, including the PKG-006 host-adapter unit suite and the existing database-backed runtime, 10,000-person population, security-boundary and backup/restore checks. Database migration validation [45294932282](https://github.com/Joshuaogri/saltwater/actions/runs/45294932282) passed. **PKG-006 is verified complete.** No Neon production operation or transport deployment occurred.


## 4O. PKG-007 — ChatGPT tool handler and trusted context injection (proposed)

PKG-007 is proposed in `docs/implementation/approval-packages/PKG-007-chatgpt-tool-handler-and-trusted-context-injection.md`. It depends on verified PKG-005 authenticated command execution and PKG-006 trusted host adapter. The package adds a narrow server-side tool handler that accepts only the PKG-006 model-visible request object and receives `TrustedHostContext` separately as a host-injected argument. It delegates to the existing adapter and returns only the documented `ok`/`message` response. Unknown fields, malformed inputs, unsupported commands and missing/expired context fail closed.

This is a repository-only callable handler and contract-test increment. It does not deploy an HTTP route, public endpoint, ChatGPT app/plugin, external identity provider, production secret store or persistent host-session mapping. No schema or Neon production operation is included. **PKG-007 complete:** `runtime/chatgpt_tool_handler.py` and contract tests are implemented and verified; see section 8.


## 8. PKG-007 implementation record

PKG-007 was authorised by the user's instruction to finish the package. The strict model-argument handler is implemented at `runtime/chatgpt_tool_handler.py`; contract tests are at `tests/pkg001/test_chatgpt_tool_handler.py`; the existing Python CI workflow now runs that suite. The handler accepts only the exact command allowlist and optional bounded request reference, receives trusted host context separately, rejects malformed/unknown fields before adapter invocation, delegates to PKG-006, and emits only the documented response keys. Python contract tests and the full disposable PostgreSQL workflow passed (run 45308750086); migration validation passed (run 45308723918). PKG-007 is complete within its repository-only boundary. No endpoint, deployed ChatGPT integration, plugin, Neon production change, schema migration, session or permission grant was created.


## 9. BP37-01 — canonical clock core and schedule eligibility (complete)

The user approved BP37-01 on 2026-11-24. The bounded implementation is committed directly to `main`:
- `runtime/scheduling.py`: canonical persisted-tick-based scheduler interface, deterministic due ordering, idempotent registration, one-off/interval schedules, expiry, retryable failure, owner-domain handler dispatch and lifecycle gates.
- `db/proposals/0006_bp37_tick_scheduling.sql`: disposable-only schedule registry and guarded transactional create/claim/finalize functions. No production migration was applied.
- `tests/pkg001/test_scheduling.py` and `tests/pkg001/scheduling_acceptance.sql`: unit, concurrency/idempotency, lifecycle, failure/retry, recurrence/expiry and PostgreSQL acceptance/storage tests.
- Existing CI workflow applies proposal 0006 only to disposable PostgreSQL, executes the new suites, and reports schema/row/index measurements.

**Verification:** [full Python + disposable PostgreSQL regression workflow 45310150181](https://github.com/Joshuaogri/saltwater/actions/runs/45310150181) passed, including all prior PKG-001–PKG-007 regressions, 10,000-person concurrency/cap checks, database security and backup/restore. [Database migration validation 45310150194](https://github.com/Joshuaogri/saltwater/actions/runs/45310150194) passed. Disposable storage: 131,072 bytes schema growth; 49,152 bytes empty schedule relation plus indexes; 1,001 rows measured 466,944 bytes total, approximately 466.48 bytes per schedule including indexes. Fixture rolled back. Neon production unchanged.

**BP-37 remains partially implemented:** calendar/epoch/timezone, civil-time, richer recurrence and exception/versioning, cancellation/suspension, occurrence history, abandoned-claim recovery and domain-specific schedules remain outstanding. Abandoned claims are not auto-reclaimed in this increment; stable handler idempotency keys preserve safe retry boundaries.

**Next implementation priority:** proceed with BP-40 text-first player interface and gameplay controls. BP39-01 is now verified; do not repeat its checkpoint/recovery package. Continue the actual gameplay blueprint rather than ChatGPT transport.


## 10. BP39-01 — consistent checkpoint and controlled event-claim recovery (verified bounded slice)

The user approved BP39-01 on 2026-11-24. The implementation is committed directly to `main` and verified at `d0175b2933acd14dc4abb3d6a89838e83e516f2e`.

- Proposal `db/proposals/0008_bp39_checkpoint_recovery.sql` is disposable-only. It adds a repeatable-read checkpoint manifest, separate restore-validation gates, controlled BP35 claim reconciliation, append-only recovery evidence, and conclusive owner resolution for quarantined work.
- `runtime/recovery.py` exposes the checkpoint/recovery functions through an injected PostgreSQL connection. It does not create schema or select a database target.
- Python and PostgreSQL acceptance suites cover committed, absent and indeterminate effects; later quarantine resolution; idempotency, owner matching, stale claim protection, lifecycle freeze and checkpoint mismatch.
- CI validates a separately restored disposable target. Schema/runtime/tick/event/event-work/schedule/population/manifest/structural/history/evidence gates passed. Business minimum, restore permission/hidden-truth and player-absence-freeze gates remain explicitly `not_executed`, so aggregate restore validity is false and the target is not promotable.
- [Full regression run 45376633160](https://github.com/Joshuaogri/saltwater/actions/runs/45376633160) and [database migration validation run 45376633013](https://github.com/Joshuaogri/saltwater/actions/runs/45376633013) passed.
- Disposable proposal schema growth: 155,648 bytes. Representative tuple sizes: checkpoint manifest 296 bytes; recovery audit 248 bytes. Empty and fixture relation/index sizes are recorded in [BP39-01 run 0001 evidence](test-evidence/BP39-01-run-0001.md).

**Boundary:** BP-39 remains `DESIGNED_DRAFT`; only BP39-01 is implemented/tested/verified. No physical backup, Neon PITR capability, production backup setting, RPO/RTO, retention policy, authoritative restore or promotion is claimed or authorised. No Neon production operation occurred.


## 11. BP40-01 — text-first workspace navigation and home shell (approved implementation)

Prepared package: [BP40-01 — Text-First Workspace Navigation and Home Shell](approval-packages/BP40-01-text-first-workspace-navigation-and-home-shell.md).

This is the next bounded gameplay-facing increment. It builds on the existing player command router and durable application gateway to deliver a plain-text laptop-style home/shift desk, stable navigation across the ten defined workspaces, current-workspace context and truthful domain-availability labels. Navigation remains read-only and must not create records, call unfinished domain systems, expose protected content or advance simulation time.

The package targets a narrow subset of BP-40 acceptance criteria and requires Python tests plus the existing disposable PostgreSQL regression workflow. It does not authorise a browser frontend, public deployment, new permission grants, domain mutations, database schema changes or Neon production operations.

**Status: APPROVED for bounded repository implementation on main.** Approval received 2026-11-24. Implementation and verification are recorded below; BP-40 remains DESIGNED_DRAFT.


### BP40-01 implementation record

The user approved BP40-01 on 2026-11-24. The bounded implementation adds `runtime/player_workspace.py` with the fixed ten-ID catalogue, immutable bounded navigation history, exact-ID selection and plain-text home/catalogue rendering. `PlayerCommandInterface` exposes `home`, `workspaces`, `workspace <id>`, `back` and `where`; the trusted gateway, host adapter and strict tool handler accept only these read-only forms and reject all other argument shapes. The host contract/schema documents the exact workspace command grammar. Non-home operational workspaces are explicitly marked navigation-only / not connected; no domain service, record, database credential, mutation or simulation tick is accessed by navigation.

Tests are added for catalogue stability, exact-ID rejection, bounded/back navigation, text output, lifecycle-independent read-only rendering, no tick advance, gateway permission checks and host/tool input validation. BP-40 remains DESIGNED_DRAFT; only BP40-01 is in scope. Neon production is unchanged.


**BP40-01 verification:** Implementation is committed on `main` at `4d271fc6fe01b79348e85c82089b0f9f1f81e036`. The dedicated six-test workspace suite and all existing Python regression suites passed. Full disposable PostgreSQL regression [45389064114](https://github.com/Joshuaogri/saltwater/actions/runs/45389064114) passed, including population-cap/concurrency, database access boundary and backup/restore. Database migration validation [45389064115](https://github.com/Joshuaogri/saltwater/actions/runs/45389064115) passed. No database proposal, migration or production Neon operation was part of this increment.


## 12. BP40-02 — stable player command catalogue and typed input parser (approved; implementation committed)

Prepared package: [BP40-02 — Stable Player Command Catalogue and Typed Input Parser](approval-packages/BP40-02-stable-command-catalogue-and-typed-parser.md).

The user explicitly approved BP40-02 on 2026-11-24. The bounded implementation adds `runtime/player_commands.py` as the sole immutable registry and pure typed parser. It records stable command IDs, owners, exact argument grammar, read-only/presentation-state/domain-runtime-mutation classification, existing `player.command.<token>` permission actions, confirmation metadata and the no-time-advance property. The current fourteen command forms are preserved, including the single-argument exact-ID `workspace <id>` command. Help text and the machine-readable tool schema are derived from the same catalogue contract.

`PlayerCommandInterface`, `AuthorizedPlayerCommandGateway`, `TrustedPlayerHostAdapter` and `runtime/chatgpt_tool_handler.py` now consume the shared parser. The gateway authorizes the canonical action before dispatch; host/tool syntax validation happens before credential resolution. Typed errors distinguish empty input, malformed syntax, unknown command, missing argument, invalid argument count and invalid workspace value. The exact ten workspace IDs, permission grants, recruit/lifecycle rules, hidden-truth gate and player-absence time freeze are unchanged. No new police-domain command, permission, schema, migration, seed or Neon operation is included.

**Status: IMPLEMENTED AND VERIFIED — bounded package complete.** The full Python regression, dedicated parser acceptance, full disposable PostgreSQL regression and database migration validation passed. Evidence: [BP40-02 run 0001](../test-evidence/BP40-02-run-0001.md). The later immutable-registry refinement was covered by the latest dedicated parser test. BP-40 remains `DESIGNED_DRAFT`; only BP40-01 and BP40-02 bounded slices are in scope. No Neon production operation occurred.


## 13. SW-DB-001 — canonical Saltwater world provisioning and capacity proof (proposed)

Prepared package: [SW-DB-001 — Canonical Saltwater World Provisioning and Capacity Proof](approval-packages/SW-DB-001-canonical-world-provisioning-and-capacity-proof.md).

This is the first database-first world implementation increment. It audits the existing disposable schema proposals, prepares a versioned canonical-world schema candidate, and builds a deterministic **disposable-only** full-scale fixture: 9,000 residents + 500 police-subset persons (9,500 total), 500 unused headroom and at least 10,000 distinct test businesses. It proves the 10,000-person cap, atomic admission, idempotency, referential integrity, reconciliation, restore and measured PostgreSQL storage/performance.

The fixture is explicitly synthetic and does not decide unresolved BP-02 geography, BP-03 population-scope semantics or BP-04 business distribution. BP-02/BP-03/BP-04/BP-38 specification approval and existing G1 narrative-quality/G2 capacity gates remain prerequisites for real production seeding. A separate exact-operation approval is required before any Neon production migration or data write.

**Status: PROPOSED — awaiting explicit user approval.** No SW-DB-001 implementation, test result or Neon production write is claimed.


## 14. SW-NAM-001 — universal naming registry, generator and enforcement (approved; implementation in progress)

Prepared package: [SW-NAM-001 — Universal Naming Registry, Generator and Enforcement](approval-packages/SW-NAM-001-universal-naming-registry-generator-and-enforcement.md).

This is the implementation package for the adopted core [SW-UNS-001](../blueprint/decisions/SW-UNS-001-universal-naming-standard.md). It adds one shared persistent naming registry and transactional reservation service, deterministic normalization and near-duplicate review, domain adapters, reproducible name generation, canon-name registration, automated Python/SQL/concurrency/bypass/restore tests, disposable PostgreSQL CI and measured storage/performance evidence. It preserves BP-02 geography IDs, BP-03 person IDs and BP-04 ownership of built-world entities; BP-38 owns registry integrity and BP-43 verifies it.

The repository audit found existing geography version names and person name fields in proposal 0002, with domain-specific IDs and profile history. The implementation must integrate these rather than create parallel identity authorities. BP-04 business/property schema integration is limited to the authoritative schema available at implementation time; no unresolved business distribution or property canon may be invented.

**User-approved naming exception (2026-11-24):** the sovereign territory and playable city retain the exact canonical name `Saltwater` as two distinct entities with separate IDs. The registry must permit this exact pair only; name-only search returns both as ambiguous, and no third entity or alias may claim the name. This exception is documented in SW-UNS-001 and tested in SW-NAM-001.

**Status: APPROVED — implementation in progress (2026-11-24).** Disposable proposal `0009_universal_name_registry.sql`, Python naming/generation service, immutable persisted generator manifests linked to reservations, geography/person adapters, SQL/Python/concurrency/rollback/restore tests and CI integration are committed on `main`. Core disposable PostgreSQL acceptance passed in run `45409845359`, including the 10,000-person fixture, same-entity concurrency, access control and backup/restore. Evidence: [SW-NAM-001 run 0001](../test-evidence/SW-NAM-001-run-0001.md). Follow-up run `45410340222` also passed the final manifest-version metadata. Final storage-detail workflow [45411243093](https://github.com/Joshuaogri/saltwater/actions/runs/45411243093) passed; the populated registry measured 4,546,560 heap bytes, 7,643,136 index bytes and 90,112 TOAST/auxiliary bytes across 12,279,808 total relation bytes (10,011 reservations). BP-04 and operational entity types remain NOT CONNECTED. SW-DB-001 uses proposal `0010` after the reserved 0009 sequence. The two SW-GEO-V1 name collisions have been resolved in source JSON/SVG with user approval and stable IDs preserved: `SW-D01-N1` is **Westgate Gardens** (district `SW-D01` remains **Westgate**), and `SW-D03-N2` is **Civic Terrace** (landmark `SW-POI-002` remains **Government Square**). The 100 map source IDs still lack materialised spatial-ID mappings; the dataset is not approved for operational seeding, so canon import remains blocked. No Neon production write or canon seed has occurred. A deterministic [SW-GEO-V1 identity-map candidate](../../data/geography/saltwater-geography-v1-identity-map.json) maps all 100 non-root source IDs to stable `entity_code` values and parent references. The disposable acceptance fixture now materialises all 100 entities and first versions, captures PostgreSQL-generated `spatial_id` values via `INSERT ... RETURNING`, validates parent links and confirms all 100 naming-trigger reservations. Its dedicated step passed in [run 45441551968](https://github.com/Joshuaogri/saltwater/actions/runs/45441551968), including the PostgreSQL 16/disposable-database guard; the full regression workflow subsequently completed successfully in both Python and disposable PostgreSQL jobs in [run 45441551968](https://github.com/Joshuaogri/saltwater/actions/runs/45441551968). The 10,000-person fixture grew its disposable database by 2,334,720 bytes (2.226562 MiB; 2,334.72 incremental bytes per person); the full fixture database measured 32,250,903 bytes. At the full fixture stage, 10,111 reservations occupied 8,642,560 bytes total (854.77 bytes/reservation), with heap/index/TOAST details recorded in [SW-NAM-001 run 0001 evidence](../test-evidence/SW-NAM-001-run-0001.md). Backup/restore reproduced all fixture counts and manifest values. The checkpoint validator correctly remained partial because business-minimum, player-absence-freeze and hidden-truth gates were not executed; no fully valid production checkpoint is claimed. No operational geography canon import or Neon write has occurred. SW-NAM-001 core naming, geography/person adapters, disposable identity mapping and full regression are verified; BP-04 and other operational naming adapters remain NOT CONNECTED until their authoritative schemas exist. Keep operational canon import blocked pending separate map approval.

## 15. BP38-01 — database integrity and migration foundation (implemented; production migration 0002 applied)

Package: [BP38-01 — Database Integrity and Migration Foundation](approval-packages/BP38-01-database-integrity-and-migration-foundation.md).

The user approved BP38-01 on 2026-11-24. The bounded slice reuses `sw_ops.schema_migration`, adds checksum enforcement and a schema-fingerprint field through migration 0002, and introduces `scripts/migrate.py`. The runner defaults to read-only verification; `--apply` is explicit. It validates ordered migration identity and SHA-256 source checksums, serializes concurrent runners with a PostgreSQL advisory lock, and compares a deterministic catalogue fingerprint to detect live schema drift. Unit tests and a disposable PostgreSQL CI workflow cover migration ordering, transaction wrappers, idempotency, checksum drift and schema drift.

**Production boundary:** BP38-02's live PostgreSQL 18 replay comparison and supplementary catalogue review passed. The user separately approved the guarded version-1 checksum adoption; the exact 0001 SHA-256 is now recorded in Neon. Database size remains 9,306,112 bytes (0-byte measured delta). Migration 0002 was separately approved and applied on 2026-11-24. The exact source checksum and live schema fingerprint are recorded in the authoritative ledger; the committed Python runner’s read-only verification passed in [run 45444735686](https://github.com/Joshuaogri/saltwater/actions/runs/45444735686). The push-triggered Neon deployment workflow remains disabled. The dedicated Neon migration-ledger workflow is read-only and cannot apply migrations. Disposable proposals do not write to the authoritative migration ledger.

**Status: IMPLEMENTED ON MAIN — disposable PostgreSQL tests PASS (run [45428332686](https://github.com/Joshuaogri/saltwater/actions/runs/45428332686)); final code review PASSED.** Evidence: [BP38-01 run 0001](../test-evidence/BP38-01-run-0001.md). BP38-02's live PostgreSQL 18 replay comparison and supplementary catalogue review passed in [run 45437263676](https://github.com/Joshuaogri/saltwater/actions/runs/45437263676). The guarded one-row version-1 checksum adoption was explicitly approved, executed and verified; Neon remains 9,306,112 bytes with a measured 0-byte database-size delta. The exact version-1 checksum matches committed migration 0001. **Migration 0002 is applied and verified.** Its execution record, including preflight, temporary-branch acceptance, production DDL, ledger registration, actual storage measurement and the two-transaction execution note, is [BP38-01 migration 0002 production application plan](approval-packages/BP38-01-migration-0002-production-application-plan.md). Final production verification evidence: [BP38-01 run 0002](../test-evidence/BP38-01-run-0002.md). BP-38 remains DESIGNED_DRAFT; BP38-01 and BP38-02 are the bounded implementation slices in scope.



## 16. SW-DB-001 — canonical world provisioning and capacity proof (approved; disposable implementation verified)

Package: [SW-DB-001 — Canonical World Provisioning and Capacity Proof](approval-packages/SW-DB-001-canonical-world-provisioning-and-capacity-proof.md). The user explicitly approved this bounded package on 2026-11-24 for GitHub main development and disposable PostgreSQL testing only.

The migration-number audit confirmed that 0009 is the universal naming proposal and 0010 is the next available proposal number. The candidate is committed as [0010 canonical world provisioning](../../db/proposals/0010_canonical_world_provisioning.sql); it is a disposable proposal, not a source migration. It adds BP-04-owned business identity/lifecycle history, immutable cross-domain provisioning metadata and a BUSINESS adapter in the existing SW-UNS registry. It does not decide BP-04 business category/site distribution.

The deterministic fixture and manifest are committed: [opening fixture](../../tests/pkg001/sw_db_001_world_fixture.sql), [manifest](../../data/fixtures/sw-db-001-opening-manifest.json), [acceptance](../../tests/pkg001/sw_db_001_acceptance.sql), [restore checks](../../tests/pkg001/sw_db_001_backup_restore_assert.sql), and [candidate model](../../docs/architecture/SW-DB-001-canonical-world-data-model.md). The fixture targets 9,000 resident-cohort identities + 500 police-subset-cohort identities = 9,500 distinct living people, leaving 500 headroom, plus 10,000 uniquely named business identities. Police cohort labels and varied business sector/legal-form/staff-band values are test-only. No police appointments or personnel histories are created. Business sites remain unassigned; no map, parcel, road, address or coordinate records are fabricated.

The dedicated [SW-DB-001 disposable workflow](../../.github/workflows/sw-db-001-disposable.yml) passed both Python and disposable PostgreSQL 16 jobs in [run 45456851773](https://github.com/Joshuaogri/saltwater/actions/runs/45456851773), tested at commit `db71703dfcdabb958913969ff07dfa310ad8d495`. The 9,500-person/10,000-business opening fixture passed acceptance with 9,000 resident labels, 500 police-subset test labels, 500 headroom and 10,000 unique business names. Proposal 0010 schema-only growth was 278,528 bytes. The fixture added 39,632,896 bytes (37.796875 MiB) in 169,295 ms, averaging 115.18 rows/second. Person-domain relations totalled 5,259,264 bytes (553.61 bytes/person); business-domain relations totalled 4,399,104 bytes (439.91 bytes/business). Same-manifest repeat produced a 0-byte database-size delta and unchanged row manifest. Both PERSON and BUSINESS SHA-256 content checksums matched after PostgreSQL custom-format backup/restore. Indexed population, person and business lookups measured 0.071 ms, 0.117 ms and 0.057 ms; cohort reconciliation measured 4.532 ms. The concurrent final-slot test from 9,999 admitted exactly one of two contenders; final cap assertions were all true, tick remained 0 and a further admission was rejected. Full figures and caveats are in [SW-DB-001 run 0001 evidence](../test-evidence/SW-DB-001-run-0001.md). **Bounded GitHub/disposable implementation: VERIFIED.** Production Neon remains untouched; no production seed or operational world activation is authorised.

**Production boundary:** this approval grants no Neon production write authority. No Neon connection, migration, schema change, seed, import, upload or configuration change is part of SW-DB-001. BP-04 distribution canon, detailed geography, G1 narrative sign-off, G2 Neon capacity and later production release gates remain open.


## 17. BP04-01 — property, building, premises, unit and access-point identity foundation

Package: [BP04-01 — Property, Building, Premises, Unit and Access-Point Identity Foundation](approval-packages/BP04-01-property-premises-identity-foundation.md).

BP04-01 is approved, implemented and verified on `main`. Corrected disposable PostgreSQL 16 workflow [run 45477359265](https://github.com/Joshuaogri/saltwater/actions/runs/45477359265) passed both Python regression and full PostgreSQL acceptance. The acceptance verifies property/building/premises/unit/access-point identities, typed geography references, global naming collision rejection, immutable identity, lifecycle/relationship history, parent integrity and all three access-point creation-history entries including the intentionally unnamed access point.

BP04-01 does not populate the actual Saltwater property inventory or determine city-wide property distribution. It establishes canonical identities only.

**Status: APPROVED — implementation and disposable acceptance passed.** Neon production remains untouched.

## 18. BP04-02 — deep physical asset and space profiles (approved; disposable verification underway)

Package: [BP04-02 — Deep Physical Asset and Space Profiles](approval-packages/BP04-02-deep-physical-asset-and-space-profiles.md).

User explicitly approved BP04-02 for implementation on `main` and disposable PostgreSQL 16 testing. Candidate migration `db/proposals/0012_bp04_physical_asset_detail_profiles.sql` creates effective-dated, append-only typed profiles for property, building, premises, unit and access point. Profile snapshots have distinct version identities, effective ticks and recorded timestamps; corrections are added as new records rather than overwriting earlier facts.

Structured child records include:
- Physical measurements with units, basis, method, precision, source, confidence and effective chronology.
- Building floor/level schedules and component/material/condition records.
- Premises room/zone records.
- Utility/service systems and physical service availability.
- Physical features/facilities.
- Element-specific condition assessments.
- Defect and remedial-action records.
- Attribute assertions with distinct known, unknown, not-assessed, not-applicable and not-present states.

All material detail is source/actor attributed and confidence-coded. No fabricated values or false precision are allowed. SW-UNS-001 remains the single naming registry; profile records do not introduce duplicate naming systems. The package excludes ownership, tenancy, occupancy, business operators, police facilities, new geometry, city-wide inventory seeding and Neon production changes.

Disposable acceptance: `tests/pkg001/bp04_02_profile_acceptance.sql`; static contract regression: `tests/pkg001/test_bp04_02_contract.py`; workflow: `.github/workflows/sw-db-001-disposable.yml`. The workflow measures migration-only schema growth separately from any future fixture growth and executes BP04-02 acceptance against disposable PostgreSQL 16.

**Status: APPROVED — implementation committed; first full disposable PostgreSQL verification pending.** Do not mark BP04-02 verified until the full workflow passes and its evidence is recorded.

## 19. BP04-03 — actual city physical inventory and geography-linked population (future package)

After BP04-02 passes acceptance, design a separate, bounded data-production package for the actual Saltwater city inventory. It must build from the approved BP-02 parcel/address/road/junction/route canon and populate property, building, premises, unit and access-point records with the full BP04-02 detail model. It must include neighbourhood coverage, spatial/access relationships, realistic use mix and provenance/quality states, unique names under SW-UNS-001, cross-record reconciliation and explicit unknowns where no reliable detail exists. It must not fabricate survey-grade dimensions or pretend synthetic estimates are verified.

The actual property inventory is not present yet. Do not seed it until the geography and inventory design are reconciled and a separate population package is approved. No Neon production write authority is granted by BP04-02.
