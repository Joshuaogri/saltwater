# BP-01 Foundational Contract Test Run 0003

**Run:** [GitHub Actions 45864752181](https://github.com/Joshuaogri/saltwater/actions/runs/45864752181)  
**Workflow:** BP-01 foundational contract tests  
**Result:** SUCCESS  
**Source commit:** `6a7ccc6408ce1aa60a43d6e6a362d3d1d6ff7b67`  
**Branch:** `main`  
**Executed:** 2026-11-26  
**Production Neon:** no connection or write

## Result

All 16 test steps passed: **156 tests, zero failures**.

The suite covers:
- immutable Saltwater canon and exact reveal-trigger contract;
- player-only hidden-truth authorization;
- exact `bingo` parsing, help suppression and authenticated command routing;
- read-only player interface state invariance;
- single-player application and player-bound identity checks;
- ChatGPT tool and trusted host boundaries;
- authoritative runtime absence freeze;
- causal event processing and idempotency;
- tick scheduling and recovery;
- NPC workforce, four-shift rotation and dispatch lifecycle;
- PostgreSQL NPC source-adapter contract, including real personnel identity mapping, player exclusion, unassigned/recruit handling and BP08 unavailable status.

## Production NPC source correction

The production PostgreSQL adapter no longer creates NPCs from authorised posts. It reads existing personnel identities and active primary unit memberships, excludes the person bound to the human player, and honours BP08's current unit status. Vacant posts do not create people or dispatch-ready crews. The synthetic post-based workforce generator is restricted to in-memory tests and sandbox scenarios.

## Additional disposable PostgreSQL evidence

The dedicated NPC integration step in [PKG-001 run 45865031957](https://github.com/Joshuaogri/saltwater/actions/runs/45865031957) passed. It verifies that the current fixture's 500 vacant posts, zero personnel service rows, zero appointments and zero memberships produce no fabricated NPC workforce and no dispatch assignment. The full PKG-001 workflow remains in progress, so this is a step-level result, not a full workflow pass.

## Scope limits

This is focused Python contract evidence. The disposable PostgreSQL end-to-end NPC source integration is being validated separately in PKG-001; it is not part of this run. The current opening fixture has 500 vacant posts, zero active appointments and memberships, and zero active personnel service rows. The 500-person POLICE_SUBSET population cohort has not yet been provisioned as BP06 personnel service records. No dispatch crew should be fabricated until the owning BP03/BP06–BP08 records exist.

Other BP-01 verification gaps remain:
- live BP15/BP16 case-owned hidden-truth provider and cross-channel non-leakage;
- NPC knowledge boundaries;
- actual game-session host registration of recurring NPC schedules;
- persistent NPC deployment/crew state and restart recovery;
- complete cross-division acceptance traceability.

BP-01 remains implementation-in-progress and verification-blocked. No production Neon write, migration, seed, grant or permission change was made.
