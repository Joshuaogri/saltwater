# BP39-01 — Consistent Checkpoint and Controlled Event-Claim Recovery

**Division:** BP-39 — Persistence and Recovery  
**Package status:** PROPOSED — awaiting explicit user approval  
**Target:** `Joshuaogri/saltwater`, `main` only  
**Baseline:** `b6094d03da1cc96d8cc6d76ba2fca347e16d0c26`  
**Dependencies:** PKG-001 runtime kernel; BP37-01 canonical tick/schedule core; BP35-01 event-work/claim/attempt ledger; existing disposable PostgreSQL regression harness  
**Production database:** No Neon production operation is included or authorised.

## 1. Objective

Deliver the first bounded BP-39 gameplay-persistence increment: establish a transaction-consistent checkpoint manifest, validate a restored disposable database against that manifest, and provide an explicit, auditable recovery path for abandoned BP-35 event-work claims.

This closes the known lifecycle deadlock in BP35-01: an abandoned claim currently prevents pause/stop/recovery indefinitely. Recovery must not guess whether the owner handler committed its domain effect. It must reconcile the authoritative owner-domain outcome before making work eligible again.

## 2. Existing foundations to reuse

- `sw_runtime.state` and the existing runtime lifecycle/player-presence gate.
- BP-37 committed `world_tick`; do not create a second clock.
- Existing `sw_core.simulation_event` identity and event sequence.
- BP-35 `event_work`, `event_work_attempt`, causal prerequisites, claim token and stable idempotency key.
- Existing schema migration ledger, permission/audit interfaces, disposable PostgreSQL CI and backup/restore regression.
- BP-39 ownership boundary: recovery operations and recoverable-copy lifecycle only. BP-38 retains schema/transaction ownership; BP-35 retains event execution; BP-37 retains time; domain owners retain outcome truth.

Do not duplicate event IDs, runtime state, schedule state, permissions, audit identity or domain records.

## 3. Bounded implementation

### 3.1 Consistent checkpoint manifest

Add a compact disposable-only checkpoint manifest proposal, expected at `db/proposals/0008_bp39_checkpoint_recovery.sql`, and a Python service under `runtime/` (proposed `runtime/recovery.py`).

A checkpoint manifest must record at minimum:
- Stable checkpoint ID and format/version.
- Source environment/project/branch/database identifiers supplied by trusted configuration (never guessed).
- Database schema/migration watermark.
- Canonical runtime lifecycle and committed world tick.
- Highest committed simulation event ID / event watermark.
- Event-work counts by lifecycle state, including claimed work.
- Schedule counts by lifecycle state, including claimed work.
- Checkpoint consistency boundary and creation metadata.
- Manifest digest and validation state.
- Actor/service identity and approval/reference for the operation.

Capture related watermarks and counts in one read-only, transaction-consistent snapshot (repeatable-read or stronger, as supported by the disposable test target). A checkpoint is a consistency manifest, **not** a claim that a physical backup object exists. It must not advance world time, execute handlers, mutate domain records or expose protected/hidden truth.

### 3.2 Restore validation

Implement a validation routine that compares a restored disposable target with its selected manifest and reports separate gates:
1. Technical/schema migration watermark.
2. Structural identity and foreign-key/uniqueness integrity.
3. Canonical runtime state and world-tick watermark.
4. Event sequence and event-work state reconciliation.
5. Schedule state reconciliation.
6. Population cap and business minimum invariants using existing canonical records (without creating fixtures in production).
7. Historical/provenance and append-only attempt-history checks.
8. Permission and hidden-truth regression checks.
9. Player-absence/pause freeze invariant.
10. Evidence completeness and exact source/target/software identifiers.

No single aggregate PASS may hide a failed or unexecuted gate. A target cannot be declared promotable or authoritative by this package. Restore validation is exercised only against disposable PostgreSQL.

### 3.3 Explicit abandoned event-claim recovery

Add a controlled recovery state machine for BP-35 claims. The recovery operation must be separately authorised and audited, and must not call the domain handler as a blind retry.

For each claimed event:
- Freeze new event dispatch and prevent a competing claim while reconciliation is in progress. Use existing runtime lifecycle/locking; do not invent a parallel pause flag.
- Identify the event, current claim token, latest append-only attempt, stable idempotency key, owner division/handler version, causal prerequisites and checkpoint/event watermarks.
- Require the owning domain to provide a reconciliation result against its authoritative records. The recovery engine itself must not infer domain truth.
- **Effect already committed:** close the abandoned work as completed only when the owner supplies a durable outcome reference proving the existing effect. Do not execute it again.
- **Effect definitely not committed:** release it to an eligible retry state only after the owner confirms absence of the effect and the existing idempotency key is retained.
- **Outcome indeterminate or owner unavailable:** quarantine the work, preserve the claim/attempt history and block normal dispatch/resume until an authorised owner resolution. Never guess or retry.
- Reject stale/mismatched claim tokens, duplicate recovery requests with conflicting decisions, unauthorised owners, missing outcome references and recovery attempts against non-claimed work.
- Record append-only recovery decision/evidence: actor, authority, event, prior status, decision, owner response reference, checkpoint reference, world tick, reason code and resulting status. Never copy sensitive payloads into the recovery log.
- Preserve causal prerequisites: children remain blocked until their parent is authoritatively completed.
- A recovery operation must be idempotent. Repeating the same approved decision returns the same result; a conflicting decision is rejected.

**Critical boundary:** if the domain side effect and BP-35 finalisation are not in one atomic transaction, recovery requires owner-domain reconciliation. A timeout, process death, missing acknowledgement or elapsed wall time is not proof that the effect did not occur.

### 3.4 Lifecycle coordination

- An abandoned claim must no longer create an unresolvable permanent deadlock when a valid authorised reconciliation is available.
- Runtime remains frozen while unresolved claims exist; it may return to normal running/player-present operation only after all claims are either authoritatively completed or safely released for retry and the recovery audit is durable.
- Quarantined/indeterminate work remains an explicit blocker; no silent skip or automatic resume.
- Recovery must not advance the simulation tick or process schedules/events while the player is absent.
- No wall-clock timeout alone may reclaim a claim.
- No automatic blanket reset of all claimed rows.

## 4. Acceptance criteria targeted

This package targets only a bounded subset of BP-39's 151 design criteria, principally:
- Checkpoint manifest identity, scope, schema/event/time watermarks and consistency.
- Restore validation in an isolated target with distinct technical, structural, temporal, domain and security gates.
- Recovery audit, source/target identification, approval traceability and truthful failure states.
- Event/outbox/idempotency reconciliation without duplicate effects.
- Recovery test evidence and measured disposable storage growth.
- Preservation of Saltwater canon, provenance, hidden-truth protection and pause/absence semantics.

It also closes the BP35-01 deferred abandoned-claim recovery boundary and must preserve BP37-01 schedule lifecycle semantics.

## 5. Required tests

Python and disposable PostgreSQL tests must cover:
- Consistent manifest capture and stable digest; concurrent writes cannot produce mixed watermarks.
- Empty, active, paused, recovering and player-absent checkpoint states.
- Restore target with matching manifest; mismatched schema, tick, event watermark, event-work count, schedule state and integrity each fail the correct gate.
- Claim recovery: owner confirms committed effect; owner confirms no effect; owner returns indeterminate; owner unavailable.
- No handler re-execution for an already-committed effect.
- Retry retains original event ID and idempotency key.
- Stale claim token, non-claimed row, duplicate decision and conflicting decision rejection.
- Concurrent recovery attempts serialize; only one decision commits.
- Child event remains blocked until parent completion.
- Quarantine blocks unsafe resume; valid full reconciliation permits controlled lifecycle continuation.
- No wall-clock-based claim expiry or offline tick advancement.
- Recovery audit append-only and diagnostics do not expose event payload/hidden truth.
- Existing BP35/BP37, runtime, player, security, 10,000-person cap, database-boundary and backup/restore regressions remain green.
- Baseline, schema growth, empty relation/index size, representative manifest/recovery row size and fixture growth are measured; fixtures roll back.

## 6. Explicit exclusions

- No Neon production migration, schema/data/configuration/credential change, backup setting, export, restore, branch clone or capacity commitment.
- No invented RPO/RTO, backup cadence, retention duration, recovery SLA or provider capability.
- No claim that a manifest is a physical backup or that disposable restore tests prove Neon PITR/provider recovery.
- No production backup object, encryption-key or secret-management change.
- No authoritative restore promotion or destructive source overwrite.
- No general BP-35 replay engine, NPC/world simulation, random-stream service or domain handler implementation.
- No automatic retry of indeterminate effects.
- No full BP-39 division approval or completion.
- No change to the fixed BP-01–BP-44 structure or Saltwater canon.

## 7. Approval requested

Approve **BP39-01 — Consistent Checkpoint and Controlled Event-Claim Recovery** for:
1. Repository implementation directly on `main`.
2. Python unit tests and disposable PostgreSQL proposal/integration/acceptance tests.
3. CI changes required to apply proposal 0008 only to disposable PostgreSQL and run the tests.
4. Restore-validation fixtures, measured storage results and reproducible evidence documentation.

Approval does not authorise any Neon production operation, provider backup configuration, production restore, RPO/RTO selection, secret/credential change, or authoritative promotion.

## 8. Status

**PROPOSED — awaiting explicit user approval.** No implementation or test result is claimed by this package. BP-39 remains `DESIGNED_DRAFT`; this package, if approved and verified, changes only the recorded status of this bounded slice.
