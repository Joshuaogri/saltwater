# PKG-001 — Disposable acceptance test matrix

**Status:** Proposed; not executed. **Target:** disposable PostgreSQL only.  
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
