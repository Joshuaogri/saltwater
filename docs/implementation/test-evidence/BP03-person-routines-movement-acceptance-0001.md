# BP03 person routines and movement acceptance

**Date:** 2026-11-27  
**Blueprint:** BP03 — Population and Individual Simulation  
**Workflow:** [BP03 Individual Simulation Acceptance](https://github.com/Joshuaogri/saltwater/actions/runs/46039460668)  
**Result:** PASS  
**PostgreSQL:** Disposable PostgreSQL 16.16  
**Main commit under test:** `bdb8de8a000b10f74b4c7a1959961de1ffeb8727`

## Implemented

- Effective-dated person routines are stored against one canonical person identity.
- Routine schedules are structured JSON and remain explicitly separate from proof of attendance.
- A replacement routine links to the routine it supersedes; a prior routine cannot have multiple successors.
- The current-routine view respects the simulation tick and supersession chain.
- Movement records preserve origin/destination references, travel mode, certainty kind (observed, estimated or verified), confidence, occurrence tick, recorded tick, source, actor and reason.
- Routine and movement records are append-only.
- Movement records cannot be placed in the future or inserted behind a later movement already recorded for that person.
- Source-reference retries are idempotent and conflicting reuse is rejected.

## Acceptance exercised

- Create a canonical person.
- Record a structured workday routine and verify the current-routine projection.
- Replay the same routine source and verify no duplicate.
- Record a replacement routine and verify it supersedes the prior current routine.
- Record an estimated commute with confidence and verify certainty is preserved.
- Verify movement summary counts and latest tick.
- Attempt a future movement and verify rejection.
- Attempt to mutate a routine record and verify append-only protection.
- Entire fixture transaction rolled back; no persistent game population was created.

## Scope boundary

This acceptance covers routine and movement storage contracts. It does not claim that BP37 scheduling, BP02 route calculation, physical attendance verification or full NPC knowledge modelling are implemented by BP03. Location references remain stable opaque identifiers resolved by the owning geography system. No Neon production migration or population seed was performed.
