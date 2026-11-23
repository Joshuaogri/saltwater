# PKG-004 — accepted-player identity and session activation

**Status:** Approved; implementation in progress  
**Branch:** main only; no feature branches or pull requests  
**Project:** Entirely fictional Saltwater police simulation  
**Production database:** No Neon migration, seed, write, upload, or configuration change is included or authorised.

## Purpose

Complete the missing link between an authenticated game principal, the game-native player profile, an accepted recruit career, and a durable player session. PKG-003 deliberately allows a pending player profile without creating a canonical person or personnel record. PKG-004 ensures that a player does not receive an active officer-linked game session until the recruit intake has an authorised accepted outcome.

This package is limited to the identity/session activation seam. It does not approve the full identity provider, public login transport, complete police career system, or any of the fixed BP-01–BP-44 divisions.

## Decisions proposed

### D1 — separate identity namespaces

1. Keep external/game authentication principal ID, player ID, canonical person ID, personnel ID, career ID and session ID as distinct identifiers.
2. A trusted host may register or resolve a provider-neutral sw_auth.principal using an issuer/subject pair. The application must never invent an issuer or subject, and no raw password, external access token or credential is persisted.
3. A player principal must be active and of principal kind player before it can be bound to a player profile.
4. One principal may bind to at most one player profile; one player profile may bind to at most one principal. Binding is immutable and append-preserving; corrections use a superseding lifecycle record rather than reassignment.
5. No principal-to-player binding is created merely by requesting recruit intake.

### D2 — accepted-career gate

1. Identity activation requires an existing sw_player.profile, exactly one explicit principal binding, and an accepted recruit intake with an active recruit career/personnel record.
2. Pending or rejected intake, missing career/personnel/person links, suspended/disabled principal, or inconsistent identity links must fail closed without creating a session.
3. The canonical person comes from the accepted career's personnel record; caller-supplied person IDs are not trusted.
4. The canonical person must be linked to the principal and to the session's active_person_id. No new person or personnel record is created by activation.
5. The same player/principal/person binding cannot be duplicated or silently changed.

### D3 — session issuance

1. Only after D2 succeeds may the trusted host issue a game session for that principal.
2. Session credential generation remains high-entropy and opaque; only a SHA-256 digest is persisted.
3. Session issuance uses the currently active policy version and the canonical active person ID.
4. Session issuance does not create, infer, or grant any permission. Existing explicit grants and default-deny authorization remain authoritative.
5. The raw credential is returned once to the trusted caller and is never included in logs, audit rows, simulation events, or player-visible records.
6. The default session lifetime remains 12 hours unless the trusted host explicitly supplies a shorter supported lifetime.

### D4 — atomicity and idempotency

1. The player binding and session activation operation must use one database transaction for all authoritative state changes.
2. A failed operation leaves no partial binding/session state.
3. Repeated activation for an already-bound player must not create a second binding or silently issue an untracked credential. The host must explicitly request a new session using the established session lifecycle.
4. Session revocation remains one-way and must be auditable. Revoking one session must not revoke unrelated sessions or delete the player/principal binding.
5. Lock ordering must prevent races between acceptance, binding, and session issuance; the accepted career/personnel/person links are rechecked under transaction locks.

### D5 — host boundary

1. Expose one trusted in-process application operation that accepts a resolved principal and player ID, checks the accepted career, binds identity if not already bound, and issues a session.
2. The operation must not be exposed as a public unauthenticated command, player-entered text command, or direct database grant.
3. The existing authorized command gateway remains the only command dispatch path. It must receive the exact principal ID that was bound and used for session issuance.
4. No broad player grants or automatic permissions are introduced.
5. No identity provider, browser login, email/phone verification, password reset, MFA vendor, public API, ChatGPT connector, or external transport is selected or implemented here.

### D6 — persistence, provenance and storage

1. Use a compact versioned SQL proposal and append-only binding/lifecycle provenance.
2. Preserve issuer/subject uniqueness and principal status semantics from PKG-001.
3. Persist only credential digests; do not store raw session credentials.
4. Test exclusively in disposable PostgreSQL. Record before/after database and relation bytes for the added schema and representative binding/session records.
5. Neon production remains untouched unless separately proposed with exact measured storage impact and explicitly approved.

## Implementation scope if approved

- Add the next versioned SQL proposal for immutable one-to-one player/principal/person binding and the minimum transactional activation function.
- Add a trusted Python PostgresPlayerActivationService that validates the accepted intake/career/personnel chain, invokes the atomic binding/session operation and returns the one-time credential only to its caller.
- Reuse PostgresSessionLifecycle verification/revocation semantics; avoid duplicating credential hashing or policy selection in a second independent implementation.
- Wire the activation service into the trusted application composition root without exposing a public route.
- Add disposable PostgreSQL acceptance tests for pending/rejected/accepted intake, principal kind/status, mismatched player/principal, duplicate binding, missing person/personnel/career, replay, rollback, policy absence, digest-only storage, session active-person linkage, revocation and audit.
- Test that no command dispatch is possible before session issuance and that an issued session still requires an explicit command grant.
- Update the implementation plan and package evidence; commit directly to main.

## Explicit exclusions

- No Neon production migration, seed, import, write, upload or configuration change.
- No new public HTTP/API endpoint, login page, browser flow or identity provider.
- No password storage, email/phone identity verification, MFA vendor or external credential-management system.
- No automatic permission grant, default player role grant or expansion of existing grants.
- No creation of a canonical person, personnel record or career during identity activation.
- No full probation/training/rank/promotion/career progression implementation.
- No change to the 10,000-person hard cap, one-city Saltwater canon, or fixed BP-01–BP-44 division structure.
- No hidden-truth bypass; exact standalone bingo remains the only player reveal trigger.

## Acceptance criteria

| ID | Acceptance criterion |
|---|---|
| P4-01 | Pending/rejected intake cannot be activated |
| P4-02 | Accepted intake resolves exactly one canonical person through personnel/career records |
| P4-03 | Principal and player binding is immutable and one-to-one |
| P4-04 | Inactive/non-player/mismatched principal is denied |
| P4-05 | Binding and initial session issuance are atomic |
| P4-06 | Credential is returned once; only its digest is persisted |
| P4-07 | Session contains the accepted recruit's canonical active person ID |
| P4-08 | No permission is granted by activation; command gateway remains default-deny |
| P4-09 | Replays cannot create duplicate binding or ambiguous sessions |
| P4-10 | Revocation is one-way and does not remove identity history |
| P4-11 | Disposable PostgreSQL and Python tests pass; Neon production remains unchanged |
| P4-12 | Storage overhead is measured and documented |

## Approval requested

Approve PKG-004 D1–D6 and the bounded implementation scope above. Approval will authorise repository implementation and disposable PostgreSQL testing only. It will not authorise any production Neon operation.


## Approval record

**Approved by user:** 2026-11-24. Approval covers D1–D6, repository implementation and disposable PostgreSQL testing only. It does not authorise Neon production changes.

## Implementation record

- Added `db/proposals/0005_player_identity_activation.sql`: immutable one-to-one principal/player/person binding, accepted-recruit validation, principal-to-person link protection and transactional identity-binding function.
- Added `runtime/player_activation.py`: trusted activation service that resolves the canonical person from accepted career/personnel records and issues the first session in the same PostgreSQL transaction.
- Extended `PostgresSessionLifecycle` with transaction-scoped issuance so binding and session insertion commit or roll back together; credential hashing and active-policy selection remain in the existing lifecycle service.
- Wired activation into the trusted application composition root; no public route or player-entered activation command was added.
- Added Python adapter tests and disposable SQL acceptance checks for accepted/pending intake, immutable binding, duplicate binding and session digest/active-person linkage.
- Neon production remains unchanged. CI evidence will be recorded after the current main-branch runs complete.
