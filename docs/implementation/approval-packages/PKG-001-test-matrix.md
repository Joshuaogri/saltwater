# PKG-001 — Disposable acceptance test matrix

**Status:** Partially executed. **Target:** disposable PostgreSQL only. The matrix below remains authoritative; execution states are recorded separately so no untested requirement is silently treated as passed.  
**Source package:** PKG-001. **No Neon execution permitted.**

## Runtime kernel
- K-001 singleton runtime row and valid lifecycle state.
- K-002 legal/illegal lifecycle transitions.
- K-003 attempt world-tick increment while stopped, paused, recovering and player-absent; each must fail and leave state unchanged.
- K-004 normal event insertion while paused/absent; reject.
- K-005 lifecycle events through explicit transition path; verify state and event commit atomically.
- K-006 monotonic world tick, exact current-tick event stamping, causal parent resolution.
- K-007 duplicate idempotency key; reject duplicate effect.
- K-008 simulate failure between event and domain commit; transaction rollback/retry must not duplicate effects.
- K-009 reject invalid lifecycle transitions and prohibit deleting the runtime singleton.
- K-010 bootstrap records are allowed only in ready/tick-zero/bootstrap-open state; bootstrap cannot reopen and runtime cannot start until it is closed.

## Geography
- G-001 exactly one sovereign root and one playable city.
- G-002 reject second active city/root and invalid parent relationships.
- G-003 geometry-null root identities accepted; no coordinates or CRS invented.
- G-004 geometry payload requires known format and 32-byte SHA-256; malformed metadata rejected.
- G-005 append new spatial version and confirm old version remains queryable.
- G-006 verify no external/off-map reference becomes playable geometry.
- G-007 reject spatial parent cycles, non-sequential versions and backwards effective ticks.
- G-008 reject update/delete of spatial identities and historical versions.

## Population
- P-001 person IDs unique and stable across name changes.
- P-002 roles/memberships do not create additional person identities or population count.
- P-003 count exactly 10,000 living+included persons.
- P-004 attempt 10,001st admission; transaction rejected.
- P-005 concurrent race: two sessions attempt final available slot; exactly one succeeds.
- P-006 unresolved and excluded scope statuses do not count as included.
- P-007 deceased persons cease counting but identity/history remain.
- P-008 every population-state change creates an append-only history row linked to the committed event.
- P-009 update/delete of population history is rejected.
- P-010 residence changes retain previous effective-dated residence and prohibit overlapping current residences.
- P-011 failed person admission leaves no orphan person, event, history or residence.
- P-012 reconcile transactional population counter exactly to count of living+included state rows.
- P-013 reject deletion of canonical person/population state; every state change requires a new event.
- P-014 profile/name corrections append immutable profile history and retain the stable person ID.

## Security, recovery and compactness
- A-001 player/service without permission cannot mutate runtime, person or geography records.
- A-002 protected hidden-truth payload is unavailable through normal event/query/log/search/export routes; only exact standalone `bingo` flow reaches the reveal service.
- R-001 backup/restore retains IDs, history, event order, runtime tick and population count.
- S-001 measure schema-only overhead and table/index/TOAST sizes.
- S-002 measure bytes per person+population state, event, history row and residence row.
- S-003 test low/median/high text and source-reference payloads; report bytes, MB and MiB.
- S-004 query plans and index sizes justify every index; remove unjustified indexes before approval.
- S-005 compare actual disposable DB growth with projected 9,500-person opening baseline.

All tests must run on disposable PostgreSQL with synthetic fixtures and automatic rollback/cleanup. No test connects to Neon production. Record exact commit, PostgreSQL version, fixture version, command, result, evidence and storage measurement.


## Execution status — run 0001

Evidence: [PKG-001 disposable validation and storage report](../test-evidence/PKG-001-run-0001.md).  
Successful CI commit: `13a78e4cb48d10e310f07fd04cb365f01dad436f`; PostgreSQL 16.16; Python 3.12; psycopg 3.3.9.

| Test ID | Status | Scope actually exercised |
|---|---|---|
| K-001 | PASS | Runtime singleton and initial stopped state |
| K-002 | PASS | Valid lifecycle transitions and invalid transition rejection |
| K-003 | PARTIAL | No tick advancement while stopped or paused; recovering/player-absent variants remain |
| K-004 | PENDING | Event insertion while paused/absent not separately exercised |
| K-005 | PASS | Lifecycle state/event transitions commit through PostgreSQL adapter |
| K-006 | PASS | Monotonic tick, current-tick events and causal event linkage |
| K-007 | PASS | Idempotent event and tick retries do not duplicate effects |
| K-008 | PENDING | Injected failure between event and domain commit |
| K-009 | PARTIAL | Invalid transition rejected; singleton deletion protection not separately tested |
| K-010 | PARTIAL | Bootstrap closure and start gate pass; invalid closure/reopen tests remain |
| G-001 | PASS | Exactly two canonical roots seeded |
| G-002 | PENDING | Duplicate roots, parent validity and cycles |
| G-003 | PASS | Geometry-null roots; no coordinates/CRS invented |
| G-004 | PENDING | Geometry metadata/hash validation |
| G-005 | PENDING | Spatial version append/history retention |
| G-006 | PENDING | Off-map references cannot become playable geometry |
| G-007 | PENDING | Spatial version chronology and cycle rejection |
| G-008 | PENDING | Spatial identity/version immutability |
| P-001 | PARTIAL | Stable canonical person IDs created; rename/correction path remains |
| P-002 | PENDING | Roles/memberships do not affect population identity/count |
| P-003 | PASS | Exactly 10,000 living+included people reached |
| P-004 | PASS | 10,001st admission rejected |
| P-005 | PASS | Two concurrent admissions at 9,999: exactly one accepted |
| P-006 | PENDING | Unresolved/excluded scope semantics |
| P-007 | PENDING | Death transition and retained history |
| P-008 | PASS | Population-state change produces linked append-only history |
| P-009 | PENDING | Direct history update/delete rejection |
| P-010 | PENDING | Residence chronology and overlap rules |
| P-011 | PASS | Rejected concurrent admission rolled back person/event/history; final counts reconcile |
| P-012 | PASS | Counter, person and population-state totals reconcile at 10,000 |
| P-013 | PENDING | Canonical person/state deletion protection and event-required transitions |
| P-014 | PENDING | Profile correction history and stable ID across correction |
| A-001 | PENDING | Permission boundary and unauthorised mutation tests |
| A-002 | PENDING | Hidden-truth firewall and exact `bingo` reveal route |
| R-001 | PENDING | Backup/restore verification |
| S-001 | PARTIAL | Whole-database baseline and relation totals measured; isolated schema-only overhead remains |
| S-002 | PARTIAL | Full-cap compact person/state/history/two-event fixture measured; residence/event/text sub-costs remain |
| S-003 | PENDING | Text/source-reference payload bands |
| S-004 | PENDING | Query-plan/index justification |
| S-005 | PARTIAL | 10,000-person compact fixture measured; full 9,500-person opening-world baseline not yet modelled |

Only PASS rows are complete for their stated test scope. PARTIAL rows must not be represented as full acceptance.
