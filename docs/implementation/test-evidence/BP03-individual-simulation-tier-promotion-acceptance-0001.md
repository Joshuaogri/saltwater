# BP03 individual simulation tier and promotion acceptance

**Date:** 2026-11-27  
**Blueprint:** BP03 — Population and Individual Simulation  
**Workflow:** [BP03 Individual Simulation Acceptance](https://github.com/Joshuaogri/saltwater/actions/runs/46040104903)  
**Result:** PASS  
**PostgreSQL:** Disposable PostgreSQL 16.16  
**Main commit under test:** `05696a91bd7892903a8e9812305c432d3fce60f8`

## Implemented

- Every canonical person is automatically assigned a persisted registry-level tier (0) and an initial tier-history record at identity creation.
- Event-backed tier transitions support tiers 0–3.
- Tier history is append-only and records prior/new tier, trigger, source, reason, actor and effective simulation tick.
- Material police relevance can permanently promote a person to tier 3.
- Promotion preserves the triggering case/incident reference and reason.
- Repeated promotion is idempotent.
- Tier 3 cannot be downgraded, including after a case closes.
- Read-only simulation summary exposes current tier and permanent promotion status.

## Acceptance exercised

- Create a canonical person using the SW-UNS name reservation path.
- Verify persisted default tier 0 and its initial creation-history event.
- Advance tier 0 → 1.
- Promote a material witness to tier 3.
- Verify promotion trigger provenance and permanent flag.
- Retry promotion without creating a second promotion.
- Attempt tier 3 → 2 and verify rejection.
- Verify the initial tier-zero record, tier 0 → 1 and tier 1 → 3 history, and exactly one promotion record.
- Test ran in a transaction and rolled back; no persistent game population was created.

## Storage measurement

The isolated schema-only database growth for proposal `0036_bp03_individual_simulation_promotion.sql` was **139,264 bytes** on disposable PostgreSQL 16.16. This is not a Neon production measurement.

## Scope boundary

This acceptance proves the tier and permanent-promotion slice only. It does not claim that the full BP03 individual simulation is complete: routines, movement, NPC knowledge boundaries, full opening-cohort materialisation and broader lifecycle/reconciliation acceptance remain separate implementation work. No Neon production migration or population seed was performed.
