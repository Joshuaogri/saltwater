# BP-01 Foundational Contract Test Run 0002

**Run:** [GitHub Actions 45863188374](https://github.com/Joshuaogri/saltwater/actions/runs/45863188374)  
**Workflow:** BP-01 foundational contract tests  
**Result:** SUCCESS  
**Source commit:** `6de73f27d81fd94ac85cba45b81380ba2bb16b0b`  
**Branch:** `main`  
**Executed:** 2026-11-26  
**Production Neon:** no connection or write

## Result

All 16 test steps passed: **155 tests, zero failures**.

The run covers:
- immutable Saltwater canon and exact reveal-trigger contract;
- player-only hidden-truth authorization;
- exact `bingo` command parsing and omission from ordinary help;
- player interface read-only state invariance;
- one-player application and authenticated gateway;
- ChatGPT tool and trusted host command boundaries;
- authoritative runtime absence freeze;
- causal event processing and idempotency;
- canonical tick scheduling;
- NPC workforce generation, four-shift rotation and dispatch lifecycle;
- canonical PostgreSQL NPC dispatch source adapter contracts;
- checkpoint and recovery contracts.

## Population-canon correction

The NPC workforce now creates exactly one distinct NPC per authorised post. The 500-post opening police establishment therefore produces 500 police NPCs, distributed across Alpha, Bravo, Charlie and Delta. Per-unit round-robin allocation balances shift coverage without multiplying the population or breaching the BP01/BP03 opening population baseline of 9,500 people.

This supersedes the earlier 2,000-occupant-per-shift design. Shift rotation changes which of the existing 500 NPCs are on duty; it does not create additional people.

## Superseding production-source correction

Run 0002's four-shift generator tests remain valid as synthetic roster coverage, but its former production interpretation (creating NPCs from authorised posts) is superseded. The subsequent source audit found that the disposable establishment has 500 vacant posts, zero active career post appointments and zero unit memberships. Production dispatch now loads canonical active personnel and active primary memberships, excludes the player-bound person, and respects BP08's unavailable status. It does not create people from vacancies. The adopted 500-person police subset is not yet fully linked to BP06 personnel service records; this is a recorded cross-division gap, not a reason to fabricate staff.

## Scope limits

This is focused Python contract evidence, not full BP-01 release verification. It does not prove:
- a live BP15/BP16 case-owned hidden-truth provider is connected;
- hidden identities cannot leak through every report, search, notification, dialogue, metadata or tool-output channel;
- NPC knowledge is restricted to facts each NPC could plausibly perceive, receive or access;
- the actual game-session host registers every recurring NPC schedule;
- NPC deployments and crew state persist and resume across restart;
- full disposable PostgreSQL and canonical 500-post NPC dispatch integration pass on this exact source commit.

BP-01 remains implementation-in-progress and verification-blocked until these remaining cross-division obligations are closed. No production Neon write, migration, seed, grant or permission change was made.
