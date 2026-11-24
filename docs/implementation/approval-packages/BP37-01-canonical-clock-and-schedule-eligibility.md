# BP37-01 — Canonical Clock Core and Schedule Eligibility

**Division:** BP-37 — Time and Scheduling  
**Package status:** Proposed; awaiting explicit user approval  
**Specification:** BP-37 v1.0, currently DESIGNED_DRAFT  
**Target branch:** `main` only  
**Dependencies:** Existing PKG-001 runtime kernel and PostgreSQL runtime store; BP-35 runtime lifecycle; BP-38 record/event foundation  
**Approval boundary:** Approve BP-37 v1.0 for this bounded first implementation increment, repository code/schema proposal/docs, and disposable PostgreSQL/Python tests only. No Neon production mutation.

## 1. Objective

Begin implementing the actual Saltwater blueprint in its dependency order. This is the first BP-37 gameplay-runtime increment: make the existing abstract world tick a canonical, persisted clock sequence and add deterministic schedule eligibility/dispatch foundations. It replaces further ChatGPT transport work as the immediate development priority.

The world must advance only through explicit player-present runtime advancement. Pause, quit, absence, recovery and safe-halt freeze the clock and all due-work execution. No wall-clock catch-up is permitted.

## 2. Existing foundation to reuse

- `runtime/kernel.py`: lifecycle, player-presence gate, monotonic world tick, idempotent tick event and PostgreSQL store.
- `sw_runtime.state`: persisted lifecycle and world-tick singleton.
- `sw_core.simulation_event`: existing event envelope, causal/idempotency references.
- Existing PKG-001–PKG-006 tests and disposable PostgreSQL workflow.

Do not create a second clock, runtime singleton, event ledger, player identity, session, permission system or database.

## 3. Proposed implementation

1. Add a typed BP-37 clock/scheduling module that reads the authoritative runtime snapshot and never reads host/device/database wall time to advance the fictional world.
2. Define the current `world_tick` as a monotonic simulation sequence only. Do not silently assign it a real-time duration or invent a fictional calendar, epoch, timezone, month structure or weekday system; those remain versioned configuration decisions.
3. Add a compact, domain-owned schedule registry for one-off and interval-based tick schedules. Store stable schedule identity, owner domain, subject reference, due tick, optional interval in ticks, priority, lifecycle, expiry/retry metadata, idempotency reference and provenance.
4. Determine eligibility only from the committed world tick. Provide stable ordering by due tick, priority and schedule ID. A schedule being due is not authority to execute its domain action.
5. Dispatch only through an injected owner-domain handler. Require the handler to validate its own domain rules and return an attributable result. Never fabricate successful execution.
6. Make clock advancement and schedule-claim/dispatch bookkeeping transactional and idempotent. Concurrent advancement/claim attempts must serialize or reject; retries must not execute a schedule twice.
7. Ensure paused/stopped/player-absent/recovering/safe-halted states cannot advance time, claim due work or execute scheduled actions. No offline progression or catch-up queue flush.
8. Add a disposable-only SQL proposal, Python unit tests, PostgreSQL integration/acceptance tests, storage measurements and CI coverage.
9. Update BP-37 implementation status only for the scope actually delivered; retain remaining calendar, civil-time, recurrence, exception and domain-specific scheduling work as outstanding.

## 4. Acceptance criteria

- **T37-01:** World tick is monotonic and sourced only from the authoritative runtime store.
- **T37-02:** Advancement requires RUNNING state and player presence.
- **T37-03:** Pause, quit, absence, recovery and safe-halt freeze clock and scheduler activity.
- **T37-04:** No host wall-clock elapsed time is converted into world-time advancement.
- **T37-05:** Schedule eligibility is determined only by committed simulation tick.
- **T37-06:** Due work has deterministic ordering and stable identity.
- **T37-07:** Schedule ownership does not grant action authority; only the owning domain handler may validate and execute its action.
- **T37-08:** Idempotent retries and concurrent claims cannot execute one schedule twice.
- **T37-09:** Failed handler execution leaves a truthful failed/retryable state and no false completion.
- **T37-10:** Existing runtime, recruitment, identity, session, security and backup/restore tests remain green.
- **T37-11:** Disposable schema growth and representative schedule-row/index cost are measured and recorded.
- **T37-12:** No Neon production schema/data/configuration or credentials are changed.

## 5. Explicit exclusions

- No calendar epoch, named calendar, timezone, month/weekday/season rules or tick-to-minute conversion.
- No policy choices for police shifts, business hours, court listings, custody reviews, employment or other domain schedules.
- No NPC behaviour engine, crime generation, business simulation or police operational workflow.
- No public endpoint, ChatGPT app/plugin deployment or further model-tool transport work.
- No new identity/session/grant model and no broad permission grant.
- No Neon migration, seed, import, bulk write, upload or credential change.
- No change to the fixed BP-01–BP-44 structure or Saltwater canon.

## 6. Test and measurement plan

Use deterministic in-memory tests for lifecycle, ordering, idempotency, retry and failure behaviour. Use disposable PostgreSQL 16 for transactional clock advancement, concurrent claims, persisted schedule lifecycle, rollback, player-absence/pause gates and existing regression acceptance. Measure database bytes before/after schema creation and representative schedule fixtures, including relation/index totals and per-schedule cost. Do not use production Neon for tests.

## 7. Approval requested

Approval authorises the bounded BP-37 v1.0 design increment and repository implementation described above, committed directly to `main`, plus disposable PostgreSQL/Python testing and measured storage reporting. It does not approve a fictional calendar/timezone or any production Neon operation.

**Do you approve BP37-01 for implementation and disposable testing, with Neon production remaining untouched?**
