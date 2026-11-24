# PKG-006 — trusted host session context and ChatGPT command contract

**Status:** Approved, implemented and verified 2026-11-24  
**Prepared:** 2026-11-24  
**Target branch:** `main` only  
**Dependencies:** PKG-001 through PKG-005  
**Production state:** No Neon migration, write, seed, upload or credential change is included.

## Purpose

Define the smallest safe boundary through which a future ChatGPT tool or other trusted host can submit player commands to the verified PKG-005 runtime. The model should provide only the command the player chose. It must not supply or control the player identity, canonical person, session credential, role, permission, profile or database connection.

PKG-005 already provides the authenticated command runtime. This package adds a provider-neutral host adapter and an explicit integration contract, without selecting or deploying a particular ChatGPT app, MCP host, HTTP service or identity provider.

## Decisions proposed

### D1 — trusted host context is separate from model input

1. The model-controlled command payload contains only the command text and, where needed, a bounded client request reference.
2. A trusted host creates the host-session context. The model cannot construct, edit or impersonate it.
3. A server-side credential provider resolves the current host context to the opaque Saltwater game-session credential.
4. The credential provider is an injected interface. No provider-specific user ID, OAuth issuer, ChatGPT conversation ID or browser identity is assumed.
5. The raw credential is never returned to the model, included in tool output, written to application logs or exposed in exception text.

### D2 — all commands use the existing security path

1. The host adapter calls only `PostgresPlayerCommandRuntime.execute(credential, command_text)`.
2. It does not call `PlayerCommandInterface`, PostgreSQL adapters or domain services directly.
3. PKG-005 remains responsible for session verification, immutable player/person binding, profile/career resolution, command parsing, explicit grants and durable audit.
4. Missing host context, missing credential, invalid context or adapter failure fails closed without command dispatch.
5. Session and grant revocation remain effective on the next command.
6. The host adapter cannot issue sessions, activate players, create identities or create grants.

### D3 — narrow text command contract

1. One request represents one existing command: `help`, `status`, `profile`, `recruit`, `career`, `start`, `pause`, `resume` or `quit`.
2. Arguments, multi-command scripts, arbitrary SQL, shell commands and generic database queries are not accepted.
3. The response contains only the command result and a safe status/error representation.
4. Authentication failures use a generic response. Internal SQL, credential, principal, session and authorization implementation details are not exposed.
5. Hidden-truth behavior remains unchanged. The host cannot add a reveal path or transform an arbitrary phrase into the exact `bingo` trigger.

### D4 — provider-neutral and non-production scope

1. Add a trusted host-context protocol, credential-provider protocol and small adapter that composes with PKG-005.
2. Add a concise machine-readable tool contract and human-readable integration specification.
3. Add unit tests for absent/invalid host context, credential secrecy, command forwarding, fail-closed behavior and proof that the adapter cannot bypass the PKG-005 runtime.
4. Keep the host adapter independent of any specific ChatGPT app, MCP transport, web framework or identity provider.
5. No public endpoint, deployed ChatGPT plugin, OAuth integration, production secret store or live credential delivery is included.

## Implementation scope if approved

- Add `runtime/player_host_adapter.py` with typed trusted-context and credential-provider interfaces.
- Add `docs/integration/CHATGPT-PLAYER-RUNTIME-CONTRACT.md` defining request/response shape, trust boundaries, command allowlist, error handling and credential custody.
- Add a machine-readable command-tool contract under `docs/integration/`.
- Add unit tests with fake trusted host contexts and credential providers.
- Add host-adapter tests proving the only execution route is PKG-005 and that raw credentials never appear in responses.
- Add the new test suite to the Python CI workflow.
- Update this package and implementation plan with commit and CI evidence.
- Commit directly to `main`.

## Explicit exclusions

- No Neon production migration, seed, data write, upload, credential change or live session creation.
- No deployed HTTP/API endpoint, MCP server, ChatGPT app/plugin or external transport.
- No external identity provider, OAuth flow, user-account system or provider-specific host identity.
- No new persistent database schema or credential-vault table.
- No session issuance, player activation, identity creation or permission grant creation.
- No direct database or domain-service access from the host adapter.
- No changes to the fixed BP-01–BP-44 structure or division names.
- No changes to hidden-truth policy, command allowlist or player career rules.

## Acceptance criteria

| ID | Acceptance criterion |
|---|---|
| P6-01 | Host context is constructed only by trusted server code and is not accepted as model-controlled identity data |
| P6-02 | The adapter obtains credentials only from its injected trusted credential provider |
| P6-03 | Missing, invalid or unresolved host context fails closed without command dispatch |
| P6-04 | The adapter invokes only the PKG-005 authenticated command runtime |
| P6-05 | The model cannot supply principal, player, person, profile, career, role, permission or credential overrides |
| P6-06 | Raw session credentials never appear in adapter responses, logs or surfaced exceptions |
| P6-07 | Existing command allowlist, one-command parsing, explicit grants and durable audit remain authoritative |
| P6-08 | Revoked sessions and grants are denied on the next command |
| P6-09 | Hidden-truth gate and exact `bingo` behavior remain unchanged |
| P6-10 | Python tests and CI pass |
| P6-11 | No new persistent schema or Neon production operation is introduced |

## Approval boundary

The user approved PKG-006 on 2026-11-24. This authorises the bounded repository implementation, contract documentation and Python tests described above. It will not authorise a deployed transport, ChatGPT plugin installation, external identity provider or any Neon production operation. Those require a separate, explicit proposal.

## Approval requested

**Approval recorded:** repository implementation and Python testing only. No deployed endpoint/plugin and Neon production remains untouched.


## Implementation record

The implementation is committed directly to main:
- `runtime/player_host_adapter.py`: typed trusted host context, injected credential-provider protocol, narrow request/response types and the only adapter path into PKG-005.
- `docs/integration/CHATGPT-PLAYER-RUNTIME-CONTRACT.md`: trust boundary, execution sequence, failure behavior and credential custody.
- `docs/integration/player-command-tool.schema.json`: model-visible request/response contract; no identity or credential fields.
- `tests/pkg001/test_player_host_adapter.py`: host-context, expiry, credential, allowlist, forwarding and secret-redaction tests.
- Disposable PostgreSQL CI workflow now runs the new Python unit suite. The adapter itself performs no database operations and introduces no schema.

**Verification:** Python and full disposable PostgreSQL workflow passed on CI run [45294966792](https://github.com/Joshuaogri/saltwater/actions/runs/45294966792), including the new trusted host adapter test suite and existing population, security, backup/restore and authenticated command acceptance tests. Database migration validation also passed on [45294932282](https://github.com/Joshuaogri/saltwater/actions/runs/45294932282). No endpoint, plugin, external identity provider, Neon production operation or live session was created. **PKG-006 is verified complete.**
