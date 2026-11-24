# BP40-01 — Text-First Workspace Navigation and Home Shell

**Project:** Saltwater  
**Division:** BP-40 — Interface (fixed BP-01–BP-44 structure)  
**Package:** BP40-01  
**Status:** PROPOSED — awaiting explicit user approval  
**Prepared:** 2026-11-24  
**Target branch:** `main` only  
**Neon production authority:** NONE

## 1. Purpose

Deliver the first visible, usable player-facing interface increment: a compact laptop-style, text-first home screen and stable workspace navigation over the existing player application. The player should be able to see their game identity and current simulation status, move between the defined operational workspaces, and always know which workspace is selected.

This is a real application-layer increment, not a mock screenshot or a claim that unfinished police-domain systems already exist. The shell must clearly distinguish navigation that is available now from domain functions that are not yet connected.

## 2. Existing foundation and boundary

The repository already contains:
- `runtime/player_interface.py`: command router for help, status, profile, recruit/career and runtime lifecycle.
- `runtime/application.py`: trusted PostgreSQL composition root and permission-checked command gateway.
- Durable player identity/session/activation adapters and shared runtime kernel.
- Python tests and disposable PostgreSQL CI.

BP40-01 builds on those components. It does not replace the runtime, create a second application, add another database, or make the player interface authoritative for domain records.

## 3. Deliverables

### 3.1 Text workspace model

Add `runtime/player_workspace.py` with:
- A fixed, ordered workspace catalogue using stable identifiers and human-readable labels.
- Workspaces: Home/Shift Desk; Operations; Cases; People; Evidence/Scenes; Department; Legal/Custody; Resources/Finance; Reports/Notifications; System Status.
- A small navigation-state value object holding only the current workspace and bounded navigation history.
- Strict validation of workspace identifiers; no fuzzy selection or guessed target.
- A text renderer for the shell header, player identity, runtime lifecycle, player-presence state, world tick, current workspace and workspace catalogue.
- A clear availability marker: navigation/catalogue is present, but a domain workspace is not operational until its owning service is connected.
- Plain text output with stable labels and no dependence on graphics, colour, hover, mouse or screen dimensions.

### 3.2 Player command integration

Extend `PlayerCommandInterface` with:
- `home` — render the home/shift desk.
- `workspaces` — list the stable workspace catalogue.
- `workspace <id>` — select a workspace by exact stable ID.
- `back` — return to the previous navigation location when one exists.
- `where` — show current workspace and selected-record state.

The current package does not introduce record-opening, record-search, case actions, patrol actions or domain mutations. No record is selected by navigation alone.

### 3.3 Authorised command boundary

Extend the existing trusted command gateway only as needed to authorise the new navigation commands before dispatch. Navigation commands are read-only. Unknown commands and malformed argument counts fail closed. Do not add grants, relax existing permissions, or infer that an authenticated player has unrestricted record access.

The workspace shell must not receive database credentials or open connections. It reads only the already-authorised player profile and runtime status supplied by the existing application components.

### 3.4 Documentation

Add command help and a concise interface contract describing:
- Stable workspace IDs and labels.
- Read-only navigation semantics.
- The distinction between workspace navigation and domain capability.
- Honest unavailable/not-connected status.
- No simulation-time advancement from navigation, rendering or status display.

## 4. Required tests

Add `tests/pkg001/test_player_workspace.py` and extend existing player-interface/application gateway tests.

Tests must prove:
1. All ten workspace IDs are unique, stable, ordered and resolve to exactly one label.
2. Home renders Saltwater, player identity, lifecycle, presence and world tick from supplied authoritative objects.
3. The one-city Saltwater context is not represented as multiple playable cities.
4. Navigation selects only exact known workspace IDs; unknown, partial, ambiguous and malformed identifiers are rejected without changing current selection.
5. Back navigation is deterministic and cannot escape the catalogue or create invalid state.
6. Workspace navigation never reads domain records, creates entities, mutates domain state or advances simulation time.
7. Workspace availability is not misrepresented as implemented domain capability.
8. Navigation, home, workspaces and where remain read-only in RUNNING, PAUSED, READY and STOPPED states.
9. The shell renders entirely as text and preserves international names, punctuation and long identifiers.
10. Existing start/pause/resume/quit, recruit/career, permission-denial, hidden-truth and 10,000-person cap regressions remain green.
11. The authorised gateway checks permission before executing each new command and rejects malformed or unauthorised navigation.
12. No credentials, connection strings, hidden offender truth or protected domain data appear in shell output.

No disposable SQL proposal is expected because this increment is presentation/navigation state only. Run the full existing Python suite and full disposable PostgreSQL regression workflow to prove no regressions.

## 5. Acceptance criteria targeted

This bounded package targets:
- UI-AT-001: laptop-style text-first shell and stable navigation.
- UI-AT-003: display only available player/persona facts without conflating identity dimensions.
- UI-AT-004: one-city Saltwater context.
- UI-AT-005: predictable workspace navigation.
- UI-AT-006: distinguish current workspace and selected-record context.
- UI-AT-010: essential navigation is text-only.
- UI-AT-012: stable, discoverable labels and command names.
- UI-AT-013/014: command identity and read-only classification.
- UI-AT-015/016: malformed and unknown navigation rejected without guessing.
- UI-AT-022/023/024: preserve attribution and truthful command outcomes.
- UI-AT-091/092: navigation and rendering never advance simulation time.
- UI-AT-098/099: plain-text accessible labels and status.
- UI-AT-102/103: preserve names and reject invalid input without destructive rewriting.
- UI-AT-133: presentation does not take ownership of domain truth.

These are the only criteria this package claims to target. The full BP-40 acceptance catalogue remains unimplemented unless separately delivered and verified.

## 6. Explicit exclusions

- No browser frontend, graphical dashboard, React/Next.js application, public API or deployed ChatGPT integration.
- No new authentication/session provider, role, grant, permission bypass or unrestricted admin view.
- No domain search, record inspection, record creation, mutation, export, clipboard, notification delivery or case/patrol workflow.
- No maps, scene diagrams, generated imagery or other visual dependency.
- No domain schema, migration, seed, import, bulk operation or Neon production write.
- No production connectivity claim or credential/configuration change.
- No new database, service, scheduler, timer or simulation clock.
- No simulation tick or NPC/world activity from interface navigation.
- No alteration to Saltwater canon, fixed division structure, hidden-truth/bingo gate or player-agency rules.
- No claim that BP-40 or any other division is fully implemented.

## 7. Approval requested

Approve **BP40-01 — Text-First Workspace Navigation and Home Shell** for:
1. Repository implementation directly on `main`.
2. Python unit/contract tests and existing disposable PostgreSQL regression CI.
3. Documentation and reproducible test evidence for this bounded slice.

Approval does not authorise any Neon production operation, new credential or permission grant, public deployment, production data access, or full BP-40 completion.

## 8. Status

**PROPOSED — awaiting explicit user approval.** No BP40-01 implementation or test result is claimed by this package. BP-40 remains `DESIGNED_DRAFT`.
