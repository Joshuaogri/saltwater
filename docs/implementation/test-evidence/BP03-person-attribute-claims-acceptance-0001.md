# BP03 person attribute claims acceptance

**Date:** 2026-11-27  
**Blueprint:** BP03 — Population and Individual Simulation  
**Workflow:** [BP03 Individual Simulation Acceptance](https://github.com/Joshuaogri/saltwater/actions/runs/46040104903)  
**Result:** PASS  
**PostgreSQL:** Disposable PostgreSQL 16.16  
**Main commit under test:** `0b3214c864b3993c9e3fd57feaa0b4362951f358`

## Implemented

- Canonical people receive a persisted registry processing tier 0 and an initial tier-history event when created.
- Sourced person attribute claims support a bounded non-sensitive attribute catalogue: preferred name, language, nationality descriptor, birth date/place reference, age range, occupation, education, skill, routine preference and residency descriptor.
- Each claim retains structured value, status (confirmed, estimated, reported or disputed), confidence, effective tick, source event, actor, reason and recorded tick.
- Multiple conflicting claims remain separate; the system does not silently overwrite or resolve them.
- An explicit supersession link can connect a later claim to an earlier claim for the same person and attribute.
- Claims are append-only and command writes are restricted to the game command role.

## Acceptance exercised

- Create canonical recipient and source identities.
- Record two distinct, conflicting age-range claims with different statuses and confidence.
- Verify both claims remain present and the summary reports two claims, including one disputed claim.
- Replay the same source reference and verify idempotency.
- Attempt to mutate a claim and verify rejection.
- Verify all preceding BP03 acceptance slices in the same workflow: persisted tier zero, tier progression, permanent promotion, routine succession, movement certainty/chronology and sourced knowledge boundary.
- All test fixtures ran inside disposable transactions and were rolled back.

## Scope boundary

This acceptance verifies the person-attribute claim contract, not a complete demographic seed or civil registry. It does not invent unknown personal facts. Health, financial, protected and other sensitive details are excluded from this attribute catalogue and remain with their owning domains and access controls. No Neon production migration or population seed was performed.
