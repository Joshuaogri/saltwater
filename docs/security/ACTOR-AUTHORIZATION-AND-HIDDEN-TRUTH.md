# PKG-001 — actor authorization and hidden-truth boundary

**Status:** foundational contract implemented; integration incomplete  
**Owners:** BP-42 security policy; BP-35 runtime enforcement; BP-38 data permissions; BP-39 recovery; BP-43 test evidence  
**Authority:** PKG-001 approved scope. No Neon write or production activation.

## 1. Enforced design

The implementation in `runtime/security.py` establishes a provider-neutral authorization boundary:

- Human/player, officer, administrator, operator, developer, service, system and test principals are distinct.
- A trusted `SessionVerifier` adapter must validate the opaque credential and return a verified session. The authorization layer never treats a caller-supplied role string or officer rank as proof of identity.
- Sessions and principals must be active, the session must be within its real security-time validity window, and the policy version is carried into the decision.
- Authorization is default-deny. Grants match action, exact/prefix resource, purpose and every specified subject constraint. An explicit deny overrides any allow.
- Each decision is written to an `AuditSink`. If audit persistence fails, the protected action is denied.
- The audit record contains actor/session IDs, action, resource, purpose, outcome, reason, policy version and decision time; it never contains credentials or hidden truth payloads.
- The hidden-truth reveal decision is centrally constrained to a player principal and the exact case-sensitive trigger `bingo`. Whitespace, case, punctuation, paraphrase and other input variants are rejected.

The PostgreSQL proposal creates NOLOGIN templates `sw_game_readonly` and `sw_game_command`. The read role can select canonical data but cannot directly mutate it. The command role has schema visibility but no direct table DML. Neither role is connected to a login, provider, player or service identity.

## 2. Persistent identity proposal (0003)

`db/proposals/0003_actor_session_authorization.sql` adds a provider-neutral `sw_auth` schema for disposable validation. It stores external issuer/subject identifiers (not passwords), principal kind/status and optional canonical-person linkage; opaque session credential digests only (SHA-256-sized binary digest, never raw token); session expiry/revocation and active persona; role assignments; permission grants with action/resource/purpose/effect and subject constraints; immutable policy versions; and append-only authorization audit decisions. Session issuance facts and grant definitions are immutable; sessions can be revoked and grants can be revoked once. Policy versions and audit rows cannot be updated or deleted.

The proposal deliberately grants no direct `sw_auth` table access to ordinary read/command roles. A future narrow trusted authentication service/API must own these writes and reads. The identity provider and credential issuance format remain unselected. The schema is a persistence contract, not yet a working login system or connected `SessionVerifier`/`AuditSink` adapter. The SQL acceptance fixture is transactionally rolled back in disposable PostgreSQL only.

## 3. Tests

The authorization unit suite covers:
- explicit allow and audit;
- default deny;
- explicit deny precedence;
- invalid, expired and revoked sessions;
- exact `bingo` only;
- non-player reveal rejection;
- audit failure fails closed.

The disposable database suite separately tests the read-only and command role grants and append-only history enforcement. These tests do not use Neon.

## 4. Integration still required

This module is a policy contract, not yet a complete production security system. Before A-001/A-002 can be fully accepted:

1. Implement a real trusted session verifier adapter after selecting/configuring the identity provider. No provider is assumed here.
2. Persist principal, session, grant, revocation and policy-version records with auditable lifecycle.
3. Implement a durable append-only security audit sink; the in-memory sink is test-only.
4. Bind every player command, NPC/service command, query, search, aggregation, map, notification, report, export, cache and administrative route to the same authorization decision service.
5. Ensure domain writes cannot bypass the command boundary; add row/field/purpose constraints where needed.
6. Store hidden occurrence truth separately from ordinary case facts and projections. Only a narrow reveal service may retrieve it after the exact player trigger and a successful central decision.
7. Prove that ordinary event payloads, logs, errors, AI context, metrics, search indexes, exports and caches never contain the protected payload.
8. Test session revocation, policy changes, stale cache invalidation, cross-principal isolation, unauthorised direct SQL and audit failure under the actual deployed adapters.
9. Verify that security operations use real security time but never advance fictional time or NPC activity.

## 5. Deliberate non-assumptions

- No external identity provider or credential format selected.
- No player account, authenticated session, active officer persona or live login seeded.
- No hidden case truth or offender identity inserted.
- No case-domain table ownership or schema guessed.
- No secret, session token or credential committed to GitHub.
- No Neon role, grant, schema, migration or data write performed.

**Acceptance status:** A-001 database role boundary is passed for its tested scope. A-002 exact-trigger policy gate is unit-tested, but the complete hidden-truth storage/query/log/search/export firewall remains pending. BP-42 itself remains DESIGNED_DRAFT and is not marked implemented or approved by this contract.
