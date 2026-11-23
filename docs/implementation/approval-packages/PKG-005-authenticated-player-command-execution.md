# PKG-005 — authenticated player command execution

**Status:** Approved by user 2026-11-24; implementation in progress; verification pending  
**Prepared:** 2026-11-24  
**Target branch:** `main` only  
**Dependencies:** PKG-001, PKG-002, PKG-003 and PKG-004  
**Production state:** No Neon migration, write, seed or credential change is included.

## Purpose

Complete the trusted in-process path from an activated player session to the existing text command gateway. The current repository already has durable session verification, explicit-grant authorization, fail-closed command dispatch, durable audit, the PostgreSQL player application, and PKG-004's accepted-recruit identity binding. What remains is to resolve the authenticated player's actual game profile from those authoritative records and expose one coherent server-side command execution entry point.

This package connects existing components; it does not replace them or create a second authentication/authorization system.

## Decisions proposed

### D1 — session is the source of actor identity

1. The opaque session credential is the only player-supplied authentication value accepted by this entry point.
2. Resolve the principal ID, principal kind/status, session status, validity window and active canonical person from the existing `PostgresSessionVerifier`.
3. Require an active `player` principal, active session and non-null active person.
4. Never accept a caller-supplied principal ID, player ID, person ID, role, permission, profile or career as an authority input.
5. The expected principal passed to the existing authorization gateway is derived from the verified session, not from the request.
6. The authorization gateway continues to verify the credential and enforce the current grants on every command. Revocation and grant changes therefore take effect immediately.

### D2 — authoritative player context resolution

1. Resolve the player through `sw_player.identity_binding` using the verified principal ID.
2. Require the binding's canonical person ID to equal the session's `active_person_id`.
3. Join the binding to `sw_player.profile`, and to the active/most recent career and personnel records where present.
4. Construct the existing `PlayerProfile` from database values only. The caller cannot override display name, player ID, canonical person, career ID or career stage.
5. Reject missing, conflicting or inconsistent binding/context state. Do not create or repair identities during command execution.
6. No accepted career means a valid player may still inspect their profile and request recruitment; career fields remain honestly unassigned.

### D3 — one trusted command entry point

1. Add a server-side `PostgresPlayerCommandRuntime` (or equivalently named service) exposing a narrow `execute(credential, command_text)` operation.
2. Resolve and validate the session and player context, compose the existing PostgreSQL application, bind the existing `AuthorizationService` gateway and dispatch through that gateway.
3. Preserve the existing command allowlist, strict single-token parsing, default-deny grant evaluation, principal-mismatch protection and durable audit.
4. Do not add an unauthenticated command route or a second command router.
5. Keep connection factories, verifier, authorization service and audit sink inside the trusted host. Do not expose database credentials or session digests to the player interface.
6. The command entry point does not itself issue, renew or reveal credentials. PKG-004 remains the activation/session lifecycle owner.

### D4 — player access and simulation continuity

1. Preserve the existing commands: `help`, `status`, `profile`, `recruit`, `career`, `start`, `pause`, `resume`, `quit`.
2. Every command requires its own explicit effective grant; no default player permissions are introduced by this package.
3. Keep the runtime's player-presence and pause gates authoritative. Authentication or a profile read does not advance world time.
4. `quit` must leave the player absent and freeze world time; a later valid session command must not silently resume the simulation.
5. Hidden-truth protections remain unchanged. This package does not add a hidden-truth command or weaken the exact `bingo` reveal gate.

## Implementation scope if approved

- Add a PostgreSQL player-context resolver that maps verified principal + session active-person to exactly one immutable player binding and loads the profile/career projection.
- Add one trusted authenticated command runtime that composes the existing application and gateway for each request.
- Keep all security decisions in the existing `AuthorizationService`, `PostgresSessionVerifier`, `PostgresGrantProvider` and `PostgresAuditSink`.
- Add Python unit tests for context resolution, identity mismatch, absent binding, unsupported principal/session state, invalid command handling and gateway denial.
- Add disposable PostgreSQL end-to-end tests that activate an accepted recruit, execute a granted command, confirm database-derived profile content, confirm durable allow/deny audit, revoke a session and prove immediate denial, and verify no permission is silently created.
- Add storage measurement for any new persistent schema. Prefer no new persistent tables; this increment should be application code and tests only.
- Update this package and the implementation plan with commit and CI evidence. Commit directly to `main`.

## Explicit exclusions

- No Neon production migration, seed, data write, upload, credential change or live session creation.
- No external identity provider, OAuth flow, email/password login, password storage or real-world account system.
- No public HTTP/API endpoint, ChatGPT transport, web socket or external token-delivery workflow; this is the trusted in-process execution boundary only.
- No new permission grants, default roles, role escalation or implicit access.
- No new player/person/personnel/career records during context lookup.
- No changes to the fixed BP-01–BP-44 structure or division names.
- No full career ladder, training, roster, dispatch or investigation-domain implementation.
- No change to the hidden-truth rule or any disclosure of fictional culprit truth.

## Acceptance criteria

| ID | Acceptance criterion |
|---|---|
| P5-01 | A valid activated player session resolves exactly one player binding and canonical person |
| P5-02 | The session active-person ID must match the immutable player binding |
| P5-03 | Caller-supplied principal/player/person/profile/role values cannot influence identity resolution |
| P5-04 | Missing, duplicate, mismatched, inactive or non-player context fails closed without command dispatch |
| P5-05 | A valid explicit grant allows only its matching command/resource/purpose |
| P5-06 | Missing/revoked/expired grants deny and create durable denial audit |
| P5-07 | Revoked/expired/restricted sessions and disabled principals cannot execute commands |
| P5-08 | Profile and career output is sourced from PostgreSQL authoritative records |
| P5-09 | Session revocation and grant revocation take effect on the next command |
| P5-10 | Command execution does not create grants, identities or personnel/career records |
| P5-11 | Pause, quit and player-absence behavior remains frozen-world-time safe |
| P5-12 | Python and full disposable PostgreSQL integration workflows pass |
| P5-13 | Neon production remains unchanged |

## Approval boundary

Approval of PKG-005 will authorise the bounded repository implementation, Python tests and disposable PostgreSQL tests described above. It will not authorise any Neon production operation or external authentication/transport integration. No production operation is proposed in this package.

## Approval record

The user explicitly approved PKG-005 on 2026-11-24 for the bounded repository implementation, Python tests and disposable PostgreSQL tests described above. Neon production remains untouched and is not authorised by this approval.

## Implementation record

- Added `runtime/player_command_runtime.py` with session-derived identity, immutable binding/person consistency checks, PostgreSQL profile/career projection and one trusted command execution entry point.
- Added unit tests in `tests/pkg001/test_player_command_runtime.py`.
- Added disposable PostgreSQL end-to-end test in `tests/pkg001/test_player_command_runtime_postgres.py` covering accepted-recruit activation, database-derived profile, explicit command grant, durable allow audit, session revocation and durable denial audit.
- Extended `.github/workflows/pkg001-disposable-postgres.yml` to run the new unit and integration suites.
- Implementation commits: `b53c6d1f4e5ad5eab98bffd7ad1df7b70cf72b72`, `53d7e9f56cdd07d0183af23843f7a9180e04232f`, `33829f5de6dd8984e95a8e6f913110b316d51c87`, `1d25909fe07fd4cc5abb19aa96ee70196b8510fb`, `8b86fe3fbadf3d387c793449ca565bc0656f12bf`, `2b8cc4456ff3732f5af4e55b882f42bf87bd7b3b`.

**Current state:** implementation committed directly to `main`; automated verification is pending. No schema changes are proposed or added. No Neon production operation has been performed.
