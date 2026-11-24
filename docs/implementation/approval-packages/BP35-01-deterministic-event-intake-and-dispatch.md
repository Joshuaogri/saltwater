# BP35-01 — Deterministic Event Intake and Dispatch Core

**Division:** BP-35 — Simulation Engine  
**Package status:** APPROVED — implementation committed; automated verification in progress  
**Specification:** BP-35 v1.0, currently DESIGNED_DRAFT  
**Target branch:** `main` only  
**Dependencies:** PKG-001 runtime kernel and event ledger; BP-37-01 canonical world-tick/schedule eligibility; BP-38 existing event/record foundation; BP-42 existing permission enforcement interfaces  
**Production database:** No Neon production mutation is included or authorised.

## 1. Objective

Implement the first real BP-35 gameplay execution slice: accept a typed, attributable simulation event; validate it against a registered owner-domain handler contract; persist its execution work; select eligible work deterministically; dispatch it through the owning domain handler; and record a truthful, idempotent outcome.

This is an execution engine foundation, not a complete NPC/world simulator. It establishes the event lifecycle that later domain systems will use to make Saltwater active without duplicating domain authority or advancing while paused.

## 2. Existing foundation to reuse

- `runtime/kernel.py`: authoritative runtime lifecycle, player-presence gate, committed world tick and existing event ledger adapter.
- `runtime/scheduling.py`: BP-37 schedule eligibility and pause-safe claim semantics. Do not create a second clock or scheduler.
- Existing `sw_core.event_type` and `sw_core.simulation_event` event identity, causation, correlation and idempotency foundations.
- Existing permission/session gateway and disposable PostgreSQL workflow.
- Existing population/canon constraints and test harness.

No second runtime singleton, clock, event ledger, player identity, session system, permission system or database is to be created.

## 3. Bounded implementation

### 3.1 Typed event and handler contracts

Add a typed event execution module (proposed path: `runtime/event_engine.py`) with:

- Immutable event-work identity and validated metadata: event reference, owner division, handler key/version, schema version, due world tick, priority, idempotency key, correlation/causation references, visibility class and source provenance.
- Explicit distinction between command requests, committed events, observations, scheduled work and projections. Only an accepted event can enter dispatch.
- An explicit handler registry supplied by the application. Each handler declares owner division, accepted event/schema versions, permission requirements, idempotency strategy, time/pause semantics and retry/failure policy.
- Unknown event types, unsupported versions, missing owner handlers and malformed metadata are rejected or quarantined without domain mutation.
- Handler output is a proposal/receipt. The engine cannot manufacture domain success or write domain-owned records on a handler's behalf.

### 3.2 Durable work and attempt ledger

Add disposable-only SQL proposal `db/proposals/0007_bp35_event_dispatch.sql` with compact records for:

- Event execution work referencing the existing canonical event ID (no copied domain payload).
- Explicit lifecycle status, handler identity/version, due tick, deterministic priority, attempt count, retry eligibility, claim token and terminal outcome reference.
- Causal prerequisites referencing existing event IDs.
- Append-only dispatch-attempt/outcome records with timestamps in simulation ticks where applicable, error classification and source references.

The proposal must not introduce a new event identity source or permit mutation/deletion of accepted event history. Claim/finalize functions must lock and validate the existing runtime singleton and require RUNNING plus player-present state. All due-time comparisons use BP-37 world ticks; no host clock may make work eligible.

### 3.3 Deterministic dispatch

- Select only due, eligible, unclaimed work whose causal prerequisites have committed.
- Use explicit ordering: due tick ascending, priority descending, stable event ID ascending. No database natural order, thread completion order or wall-clock tie-break.
- Enforce claim tokens and idempotency keys. A stale or mismatched token cannot finalize work.
- Dispatch only through the declared owner-domain handler.
- A successful handler receipt is recorded as committed only after the handler reports its authoritative transaction outcome.
- A transient failure remains retryable under bounded attempt policy; a poison event is quarantined without blocking unrelated independent work.
- A retry retains the original event ID, payload reference and idempotency key. Changed intent requires a new command/event.
- An ambiguous handler result must not be marked successful. Recovery/reclaim of abandoned claims is deliberately deferred to a later BP35/BP39 increment until a safe owner-handler idempotency/reconciliation policy is specified.

### 3.4 Pause, absence and safety

- No event claim, handler invocation, retry progression or fictional event mutation while paused, stopped, recovering, safe-halted or player-absent.
- The database rejects a committed pause/stop/recovery transition while an event-work claim is active. The caller retries the lifecycle transition after the handler finalizes success/failure, so no in-flight domain transaction is cut in half.
- An abandoned claim deliberately blocks that lifecycle transition until explicit recovery; automatic claim reclaim is deferred to BP-39/follow-on BP-35 work.
- External ingress while paused may be held as non-simulation metadata only; it cannot enter world execution.
- Event payloads and error diagnostics must not disclose hidden crime truth, protected information or unauthorised NPC knowledge.
- No NPC behaviour, crime generation, business simulation, domain workflow, AI narrative execution, public endpoint or ChatGPT transport integration is included.

## 4. Acceptance criteria

This increment targets the following BP-35 v1.0 criteria:

- **AT-006–AT-016:** committed pause boundary, no post-pause claims, no offline progression, safe resume and held external ingress.
- **AT-017–AT-031:** stable event identity, registered type/version, provenance, distinct command/event/observation/schedule/projection semantics, immutable accepted event and declared domain ownership.
- **AT-032–AT-039:** deterministic ordering, causal prerequisites, causation/correlation traceability and safe blocking of cycles/invalid dependencies.
- **AT-026–AT-028, AT-135–AT-142:** append-only attempts, effectively-once handler effects through idempotency, truthful acknowledgements, bounded retry, quarantine and persistence-failure handling.
- **AT-151–AT-159:** permission checks before dispatch, no payload-granted authority, safe diagnostics and attributable recovery records.
- **AT-160–AT-169, AT-183–AT-190:** queue/attempt observability, deterministic degradation, back-pressure limits, pause-safe execution, replay/test support and invariant failure handling.

Acceptance tests will explicitly cover: equal-tick deterministic ordering; unknown handler/type rejection; schema-version mismatch; causal child blocked until parent commit; cycle/invalid prerequisite rejection; duplicate submission; repeated delivery; concurrent claims; stale claim token; pause/absence gate; retry and quarantine; unrelated work continuing after poison event; no false commit after handler/persistence failure; hidden-truth-safe diagnostics; and storage growth.

This package does **not** claim all listed BP-35 criteria are completed. Each acceptance test will be mapped to the precise implemented subset.

## 5. Storage and test controls

- Implement the schema proposal and integration tests only on disposable PostgreSQL.
- Measure baseline, schema growth, empty relation/index growth, representative work/attempt/dependency row cost and total fixture growth.
- Roll back all benchmark fixtures.
- Run existing Python, PostgreSQL, security, population-cap and backup/restore regression suites.
- No Neon production migration, seed, import, bulk write, upload, configuration or credential change.
- No new production capacity assumption or approval.

## 6. Explicit exclusions and deferred work

- Full NPC agent activation, relevance promotion, knowledge boundaries and action proposals.
- City/business/environment/transport/public-service causal simulation.
- Crime occurrence generation and any case-truth ownership.
- AI/narrative generation, visual projections and player-facing reporting.
- Deterministic random-stream service and full replay engine.
- Cross-domain saga orchestration, compensating actions and general fairness/anti-starvation policy.
- Automatic recovery/reclaim of abandoned claims, checkpoint/restore and recovery watermark reconciliation (BP-39 follow-on).
- Full schema/calendar/timezone/priority-policy configuration and handler-version governance.
- BP-35 division-wide approval or completion.

These remain future increments. BP-35 remains DESIGNED_DRAFT and this package changes only its recorded implementation status for the bounded delivered slice.

## 7. Approval requested

Approve **BP35-01 — Deterministic Event Intake and Dispatch Core** for:
1. repository implementation directly on `main`;
2. Python unit tests and disposable PostgreSQL proposal/integration/acceptance tests;
3. CI workflow changes required to run those disposable tests;
4. measured storage and test evidence documentation.

Approval does not authorise any Neon production change, production data, new fictional calendar/time semantics, full BP-35 division approval, NPC simulation, or additional ChatGPT transport work.

## 8. Approval and implementation record

**Approved:** 2026-11-24 — explicit user approval received.

Implemented directly on `main`:
- `runtime/event_engine.py`: typed handler contracts, registered event/schema validation, explicit authorizer, deterministic in-memory test store, PostgreSQL adapter, stable idempotency, causal prerequisites, claim-token dispatch, bounded retry and quarantine.
- `db/proposals/0007_bp35_event_dispatch.sql`: disposable-only event-work, prerequisite and append-only attempt ledgers; guarded submit/claim/finalize functions; deterministic due ordering; pause/player-presence gate.
- `tests/pkg001/test_event_engine.py` and `tests/pkg001/event_dispatch_acceptance.sql`: unit and PostgreSQL acceptance coverage.
- `.github/workflows/pkg001-disposable-postgres.yml`: disposable proposal application, storage measurement and Python/SQL test execution.

**Implementation state:** bounded code and test artefacts committed. **Test state:** automated CI is in progress; not yet marked passed. **Verification:** pending successful complete regression and storage evidence.

No Neon production schema/data/configuration/credential change was made. BP-35 remains `DESIGNED_DRAFT`; NPC activation, world simulation, full replay/recovery, fairness/back-pressure and division-wide completion remain out of scope.
