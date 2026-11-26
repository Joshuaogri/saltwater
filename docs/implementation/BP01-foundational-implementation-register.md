# BP-01 — Foundational Implementation and Acceptance Register

**Project:** Saltwater  
**Division:** BP-01 — Game Identity, Foundations and Governing Rules  
**Initial audit base:** 73a0faf4abbc19fe38295648c51367e8cc58a6ae; implementation changes are committed on the current `main` branch.  
**Updated:** 2026-11-26  
**Branch:** main only  
**Production Neon:** unchanged

## 1. Design disposition

BP-01 version 1.0 is design-complete. It reconciles the approved master framework and fixed BP-01–BP-44 structure with:

- SW-CANON-001: exact population membership, 10,000-person ceiling, 9,000 civilian + 500 police opening cohorts, 9,500 opening total and 500 shared headroom; one contiguous island city-state and adopted geographic hierarchy.
- SW-CANON-002: Saltwater as the sole primate city and dominant national/international hub.
- SW-UNS-001: mandatory universal naming authority across all 44 divisions.
- The adopted single-human-player model: every other person is an NPC.
- Text-first complete gameplay, one canonical world clock, no offline progression, causal continuity, player agency and exact standalone lowercase `bingo` reveal trigger.
- Fictional-game boundary: real-world legal/compliance/approval requirements are not imported as gameplay gates. External production database writes and permission changes remain subject to the user's explicit approval.

The old BP-01 draft's references to unresolved population membership and foundational geography are now correctly treated as implementation ownership under BP-02/BP-03, not open canon questions.

## 2. Implemented BP-01 contracts and owner integrations

| BP-01 obligation | Existing implementation | Existing test coverage | Current assessment |
|---|---|---|---|
| Machine-readable core canon | `runtime/bp01_foundations.py` | `test_bp01_foundations.py` | Added in this change |
| Exact hidden-truth reveal command, parser and player-only authorization | `runtime/bp01_foundations.py`, `runtime/player_commands.py`, `runtime/application.py`, `runtime/security.py` | `test_bp01_foundations.py`, `test_player_commands.py`, `test_player_application.py`, `test_authorization.py` | Command is exact, omitted from help, gated before dispatch and routed to an injected trusted provider; case-owned provider and cross-channel leak coverage remain outstanding |
| One player application and authenticated command gateway | `runtime/application.py`, `runtime/player_command_runtime.py` | `test_player_application.py`, `test_player_command_runtime.py` | Existing |
| Player identity activation and recruit entry | `runtime/player_activation.py`, `runtime/recruitment.py` | `test_player_activation.py`, `test_recruitment.py` | Existing |
| Canonical command parsing and action classification | `runtime/player_commands.py`, `runtime/player_interface.py` | `test_player_commands.py`, `test_player_interface.py` | Existing |
| One authoritative runtime state and absence freeze | `runtime/kernel.py` | `test_runtime_kernel.py`, PostgreSQL runtime-store tests | Existing |
| Causal event intake, idempotency and dispatch | `runtime/event_engine.py` | `test_event_engine.py`, disposable PostgreSQL acceptance | Existing |
| Canonical clock and scheduled processing | `runtime/scheduling.py` | `test_scheduling.py`, disposable PostgreSQL acceptance | Existing; host composition and complete NPC scheduler integration remain open |
| NPC workforce and autonomous dispatch | `runtime/npc_workforce.py`, `runtime/npc_dispatch.py`, `runtime/npc_dispatch_scheduler.py`, `runtime/postgres_npc_dispatch.py` | `test_npc_workforce.py`, `test_npc_dispatch.py`, `test_npc_dispatch_console.py`, `test_postgres_npc_dispatch_integration.py` | Production loads canonical active personnel, excludes the player, and requires active primary post/unit membership plus BP08 availability. It does not create NPCs from vacancies. The opening 500-person police population cohort has not yet been provisioned in live Neon; the new BP06 opening-cohort provisioner consumes 500 existing BP03 person IDs and creates service dossiers only. The separate PKG-001 disposable fixture starts with zero active personnel service rows. Host registration and persistence remain open |
| Population identity/cap | BP-03 population schema and services | `test_population_concurrency.py`, population-cap SQL fixture and disposable acceptance | Owner implementation exists; current-head evidence must be refreshed |
| Business minimum and registry integrity | BP-04 business generator/audit | `test_business_registry_generator.py`, `test_bp04_business_registry_audit.py`, business PostgreSQL acceptance | Owner implementation exists; current-head evidence must be refreshed |
| Universal naming | SW-UNS-001 shared registry and adapters | naming Python/PostgreSQL suites | Owner implementation exists; business near-duplicate acceptance still requires current-head confirmation |
| Persistence/recovery | BP-39 recovery implementation | `test_recovery.py`, backup/restore SQL acceptance | Owner implementation exists; current-head evidence must be refreshed |
| Text-first player surface | BP-40 command/workspace/interface | player command, workspace and interface suites | Existing text surface; full gameplay breadth remains in later divisions |

## 3. Verified BP-01 contract test evidence

The dedicated [BP-01 foundational contract test run 0001](../test-evidence/BP01-foundational-contracts-run-0001.md) passed (128 tests). [Run 0002](../test-evidence/BP01-foundational-contracts-run-0002.md) passed 155 tests. The latest [run 0003](../test-evidence/BP01-foundational-contracts-run-0003.md) passed 16 test steps and 156 tests at source commit `6a7ccc6408ce1aa60a43d6e6a362d3d1d6ff7b67`. Run 0003 covers the production personnel-source adapter contract, player exclusion, vacancy boundary, BP08 status and unassigned/recruit handling. This is focused Python evidence. The canonical NPC source integration step also passed in [PKG-001 run 45865031957](https://github.com/Joshuaogri/saltwater/actions/runs/45865031957), proving the opening vacant establishment does not fabricate NPCs or dispatch readiness; that overall workflow remains in progress. Hidden-truth non-leakage, NPC knowledge and live host-composition acceptance remain outstanding.

## 4. Remaining BP-01 verification work

These are real outstanding items; they are not reasons to reopen settled canon:

1. Add end-to-end tests proving hidden culprit identity cannot leak through reports, summaries, search, notifications, generated dialogue, metadata or tool responses before the exact trigger.
2. Add NPC knowledge-history tests proving NPCs cannot know facts without a plausible perception, access or communication path.
3. Prove player questions and information-only commands do not mutate authoritative world state across the full command gateway. A focused player-interface regression now checks the read-only command set against runtime state and event history.
4. Prove player choices are never silently selected or auto-completed, including investigation direction and consequential decisions.
5. Complete the BP15/BP16 case-owned hidden-truth reveal provider and verify that all outward channels preserve the reveal gate.
6. Provision the opening 500 police-subset person identities as canonical BP06 personnel service records without creating duplicate people. The new BP06 opening-cohort provisioner is implemented and its first disposable PostgreSQL acceptance passed in PKG-001 run 45868150806; the 500-person BP03 opening identity candidate seed has now been generated from a versioned SW-UNS vocabulary; names remain unreserved and person IDs/categories unmaterialised pending authoritative registry checks and BP05/BP06 staffing allocation. BP07 career/post appointments and BP08 unit memberships remain to be connected.
7. Wire the recurring NPC dispatch schedule into the actual game-session host, persist and restore NPC deployment/crew state, and prove scheduled work runs while the player is present and freezes during absence.
8. Run the relevant Python and disposable PostgreSQL acceptance suites against the current main commit and retain reproducible evidence.
9. Reconcile every BP-01 acceptance ID to its owner implementation, test and evidence reference; no criterion is marked verified from documentation alone.

Items 1–5 depend partly on BP-15–BP-24, BP-35–BP-42 and their owning services. BP-01 defines the invariant; it must not duplicate those divisions' substantive data models or algorithms.

## 5. BP06 opening cohort provisioning increment

The first disposable acceptance passed in [run 45868150806](../test-evidence/BP06-opening-personnel-cohort-run-0001.md). This is a step-level result, not a full PKG-001 workflow pass.

`db/proposals/0033_bp06_opening_personnel_cohort.sql` adds a one-time, idempotent 500-person linkage from existing BP03 identities to BP06 personnel dossiers. It does not create people, alter population counts, fill authorised posts, or create BP07/BP08 assignments. The disposable acceptance fixture is `tests/pkg001/opening_personnel_cohort_acceptance.sql`; CI applies the proposal only to disposable PostgreSQL. The candidate identity dataset is generated by `runtime/opening_police_person_seed.py` from `data/naming/saltwater-person-naming-v1.json` and persisted as readable/compressed files under `data/people/`. It contains no person IDs, personnel categories or invented demographic facts. Name reservation and BP03 person-row materialisation remain separate.

## 5.1 BP03 opening police identity candidate seed

The versioned person vocabulary and deterministic candidate generator now produce 500 unique, three-part opening police identity candidates. Internal exact and pg_trgm-compatible near-duplicate screening is applied. Each row has a stable seed reference but no database `person_id`, personnel category, demographic facts or active service status. Names remain unreserved until checked/reserved through the authoritative SW-UNS registry; the candidate dataset is not a production import or a claim that the opening cohort is already provisioned. A dedicated GitHub build workflow persists readable and gzip forms on `main`; PKG-001 also runs its regression tests.

## 6. Acceptance and release boundary

- Design: **DESIGNED**.
- Implementation: **IN_PROGRESS**.
- Testing: **IN_PROGRESS** — focused BP-01 Python contract suite passed (156 tests across 16 steps in run 0003). The separate PKG-001 run 45865031957 has also passed the canonical NPC source integration step; the overall disposable workflow and remaining cross-division acceptance evidence are still being completed.
- Verification: **BLOCKED** pending the global evidence listed above.
- No production Neon writes, migrations, seeds, grants or permission changes were performed.
- No new BP division or branch was created.
