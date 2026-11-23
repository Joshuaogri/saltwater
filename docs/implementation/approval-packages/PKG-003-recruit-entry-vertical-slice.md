# PKG-003 — recruit-entry vertical slice approval

**Status:** Approved 2026-11-23; implementation committed to main; CI verification pending  
**Branch:** `main` only; no feature branches or pull requests  
**Project:** Entirely fictional Saltwater police simulation  
**Production database:** No Neon migration, seed, write, upload, or configuration change is included or authorised.

## Purpose

Complete the next playable milestone: allow a player to begin a recruit career without inventing identities, bypassing population accounting, or creating competing personnel/career records.

The existing PKG-001 runtime kernel and PKG-002 command interface are foundations only. The relevant BP-03, BP-05, BP-06 and BP-07 specifications remain `DESIGNED_DRAFT`. Their own text expressly leaves population countability and several recruit/rank/appointment decisions open. This package asks for one bounded approval of the minimum rules needed for a recruit-entry vertical slice; it does not approve or rewrite all four divisions.

## Decisions proposed for this package

### D1 — one canonical person and population admission (BP-03)

1. A recruit is one living person and consumes exactly one place within Saltwater's hard 10,000-person cap.
2. Police personnel are a subset of the population, never an additional count.
3. The opening planning totals remain 9,000 other residents + 500 police = 9,500 total; the player recruit is included within the 500-person police allocation, not added on top.
4. One immutable `person_id` is used by all domains. Player identity, person identity, personnel identity and career identity remain separate identifiers linked to that one person.
5. Unknown biographical details remain unknown. Creating a recruit does not fabricate a date of birth, home address, family, or life history.
6. Failed admission or appointment creates no partial person, personnel record, career, or population count.

This package does not settle every visitor, commuter, temporary-presence or off-map counting edge case in BP-03. Those remain for the full BP-03 approval.

### D2 — minimum recruit establishment (BP-05)

1. Provide one controlled entry establishment type: **Recruit**.
2. Recruit is a career/service standing, not a substantive constable rank.
3. A recruit has no independent police powers, command authority, unsupervised operational deployment, or unrestricted system access.
4. Each recruit must have an identified supervisor reference before active career play.
5. Rank, position, grade, authority, qualification, clearance and assignment remain separate. No implied rank or powers are created by the word Recruit.
6. This is a minimum entry post/establishment contract only; it does not approve the full department hierarchy, rank ladder, titles, staffing establishment or command structure.

### D3 — personnel record (BP-06)

1. A personnel dossier references exactly one canonical BP-03 person.
2. Personnel and service identifiers are stable, unique and never recycled.
3. The recruit service engagement is recorded with effective simulation time, appointment source, service standing, supervisor reference and provenance.
4. The current personnel profile is a projection of append-preserving events; corrections supersede rather than erase history.
5. Player profile does not itself constitute a personnel record. A player may have a profile before joining the department.

### D4 — recruit career episode (BP-07)

1. The player may choose the Recruit entry route at new career start, subject to an available approved recruit place and successful D1–D3 transactions.
2. One career episode links to exactly one personnel identity. Re-entry creates a separately recorded episode or authorised reactivation, never a duplicate person.
3. Recruit status remains distinct from substantive rank and position.
4. Probation, training, supervision, assessments and confirmation are future governed stages; elapsed time alone never confirms a recruit.
5. Career progression advances only with the fictional simulation clock. Paused, stopped or player-absent time does not count.
6. Player and NPC recruits use the same underlying rules.
7. No promotion, rank title, specialist qualification or operational authority is granted by career creation.

### D5 — recruitment/appointment boundary (BP-33 interface only)

1. The player-facing new-career flow may record the player's choice and create a pending intake request.
2. A personnel appointment and active career may be committed only after an explicit accepted/authorised intake outcome is supplied by the recruitment/HR owner.
3. Until that outcome exists, the interface shows the request as pending and does not claim that the player is a serving recruit.
4. This package defines only the minimum interface contract; it does not approve or implement the full recruitment campaign, HR, payroll or workforce administration system.

### D6 — time and persistence boundaries (BP-37–BP-39)

1. Use the existing committed simulation tick as the authoritative effective-time reference for the first vertical slice.
2. Do not infer calendar dates, probation duration or service-year calculations until the BP-37 time/calendar policy is approved.
3. Persist authoritative records only through the approved Neon-backed architecture when separately authorised. Disposable PostgreSQL is used for integration tests.
4. Measure storage impact before any proposed production write. No production write is part of this package.

## Implementation scope if approved

- Add versioned, compact PostgreSQL proposal schema for canonical player/person linkage, recruit intake, personnel dossier, career episode and append-only lifecycle events.
- Add Python domain services with atomic transactions, idempotency, population-cap enforcement and no duplicate person creation.
- Add a new-career player flow and commands to inspect the intake/personnel/career state.
- Add disposable PostgreSQL integration tests for admission at 9,999/10,000, duplicate/replayed intake, rollback, missing supervisor, unauthorised appointment, no-rank recruit, paused-time behaviour, history correction and save/recovery.
- Add clear blocked/pending states for dependencies not yet implemented. Do not make command stubs appear functional.
- Update traceability and package evidence. Commit directly to `main`.

## Explicit exclusions

- No mass population/personnel generation or invented staffing roster.
- No Neon production migration, seed, or data write.
- No full rank ladder, command hierarchy, promotion engine, training catalogue, probation-duration policy, retirement calculator or payroll.
- No external identity provider or real-world authentication/compliance system.
- No second database or local side-database save format.
- No changes to the fixed BP-01–BP-44 division structure or names.
- No hidden offender/case truth exposure; the exact standalone player command `bingo` rule remains unchanged.

## Acceptance criteria

| ID | Acceptance criterion |
|---|---|
| P3-01 | A person can be counted only once, regardless of player/personnel/career links |
| P3-02 | Population can never exceed 10,000, including concurrent recruit admission |
| P3-03 | Failed recruit intake leaves no partial records |
| P3-04 | Duplicate/replayed intake is idempotent |
| P3-05 | Recruit has no implied substantive rank or independent powers |
| P3-06 | Personnel and career history is append-preserving |
| P3-07 | No active career is claimed before an authorised intake outcome |
| P3-08 | Simulation absence/pause freezes career time |
| P3-09 | Disposable PostgreSQL tests pass; Neon production remains unchanged |
| P3-10 | Player can inspect pending/active recruit state through text commands |

## Approval and implementation record

**User approval:** Explicitly approved on 2026-11-23. Approval covers D1–D6 and the bounded implementation scope above. It does not authorise any Neon production operation.

### Implemented on `main`

- `db/proposals/0004_recruit_entry.sql`: disposable-only schema proposal for game-native player profile, pending recruit intake, personnel, recruit-supervisor authorisation, career episode and append-only lifecycle events.
- `runtime/recruitment.py`: trusted PostgreSQL adapter for idempotent intake requests, explicitly authorised acceptance and career-status inspection.
- `runtime/player_interface.py`: `recruit` and `career` commands; without a connected recruitment adapter they return an honest unavailable state. The recruit request remains pending until the database accepts an authorised recruitment outcome.
- `tests/pkg001/test_recruitment.py`: adapter contract tests.
- `tests/pkg001/recruit_entry_acceptance.sql`: disposable PostgreSQL acceptance checks for pending intake, idempotent request, authorised approver, missing supervisor, atomic rollback, one-person admission, population accounting, active recruit career, replay and pause gate.
- `.github/workflows/pkg001-disposable-postgres.yml`: applies proposal 0004 only in the disposable CI database and runs the new tests.

### Bounded implementation choices

- `established` is a generic service-standing value used only to represent an existing supervisor; it is not a substantive rank or a rank ladder.
- Supervisors must be active established personnel with a separate, explicit recruit-supervision authorisation. Appointment approval requires an active administrator/officer principal holding the `recruitment_approver` role.
- An intake request creates no person, personnel dossier or career. Those records are created together only after the authorised acceptance function succeeds in one database transaction.
- Person, population, appointment and career events retain distinct event identities and effective simulation ticks.
- The player identity remains distinct from the canonical person and personnel/career identifiers. Unknown biographical details remain null.
- No probation duration, confirmation, rank, grade, command authority, specialist qualification or independent police power is inferred.

### Verification state

| Check | State |
|---|---|
| Schema proposal authored; not a live migration | Implemented |
| PostgreSQL atomic recruit-acceptance path | Implemented; disposable CI pending |
| Population counter/cap transaction boundary | Reuses PKG-001 locked counter; recruit-specific CI pending |
| Adapter unit tests | Implemented; CI pending |
| Player command hooks | Implemented; require injected durable adapter |
| End-to-end player/runtime/Neon connection | Not implemented; production Neon unchanged |
| Production migration or data write | Not authorised; not performed |

The new recruit commands are intentionally unavailable until a trusted PostgreSQL recruitment adapter is supplied to the player interface. This package does not pretend that the overall ChatGPT-to-Neon runtime connection is complete. The approval does not alter the production-write gate.

## Approval requested

The package was approved on 2026-11-23. The approval covers the bounded D1–D6 decisions and implementation scope above. It does not approve the complete BP-03/BP-05/BP-06/BP-07/BP-33 specifications, and it does not authorise production Neon writes.
