# Saltwater player runtime host contract

**Version:** 1.0  
**Package:** PKG-006  
**Status:** Implemented as a provider-neutral in-process contract; no transport is deployed.

## Trust boundary

The host authenticates its own user/session and constructs a TrustedHostContext in server-side code. It passes that context separately from the model-controlled request. Never accept a serialized TrustedHostContext, host-session reference, Saltwater credential, principal ID, player ID, person ID, role, permission, career or profile from model/tool arguments.

A trusted HostCredentialProvider resolves the host context to the opaque Saltwater game-session credential. The credential remains inside the server process and is passed only to PostgresPlayerCommandRuntime.execute(credential, command_text) through TrustedPlayerHostAdapter. Do not log it, return it, place it in tool output, or include it in exception text.

## Model-visible request

The request has exactly these fields:

| Field | Type | Rule |
|---|---|---|
| command_text | string | One allowlisted command, or `workspace` plus one exact workspace ID; no other arguments or scripts |
| request_reference | string or null | Optional opaque correlation value, 1–128 nonblank characters |

Allowed commands: help, status, profile, recruit, career, start, pause, resume, quit, home, workspaces, back and where. The only argument-bearing form is `workspace <id>`, where `<id>` is one exact stable ID: home, operations, cases, people, evidence-scenes, department, legal-custody, resources-finance, reports-notifications or system-status.

No identity, credential, database, role, permission, session or profile fields are accepted. bingo is not a command and this adapter does not expose a hidden-truth operation.

## Trusted host-side inputs

- TrustedHostContext: constructed by trusted host middleware, contains an opaque host-session reference and an aware expiry time. It is never model-visible.
- HostCredentialProvider.resolve(context): resolves the trusted context to the opaque game-session credential or returns no credential.
- PostgresPlayerCommandRuntime: the only execution capability. It re-verifies the session, resolves the immutable player/person binding, enforces explicit grants and records durable authorization audit through PKG-005.

The adapter cannot issue/revoke sessions, activate players, create identities, grant permissions, access PostgreSQL directly or invoke domain services.

## Response

The response contains only:
- ok: boolean command outcome
- message: command result or a safe generic error

Generic failures:
- Access denied. for missing/expired/unresolved trusted context or credential
- Invalid command. for malformed, multi-command, argument-bearing or unsupported input
- Command unavailable. for provider/runtime failure or unsafe result

No provider exception, SQL detail, session/principal identifier or raw credential is returned. If a result unexpectedly contains the credential, the adapter replaces it with a generic failure.

## Execution sequence

1. Trusted host middleware authenticates the host session and creates TrustedHostContext.
2. The model submits only command_text and optional request_reference.
3. The host invokes TrustedPlayerHostAdapter.execute(context, request); it does not serialize context into model input.
4. The adapter validates context expiry and the single-command allowlist.
5. The injected credential provider resolves the game-session credential.
6. The adapter invokes only PostgresPlayerCommandRuntime.execute(credential, command_text).
7. PKG-005 re-verifies the credential and re-evaluates explicit grants. Revocation is therefore effective on the next command.
8. The host returns the safe command response to the player.

## Failure and operational rules

- Fail closed: absent, expired, invalid or unresolved host context never dispatches a command.
- Fail closed: provider errors and runtime exceptions produce generic responses.
- Do not retry a command automatically after an ambiguous runtime failure; commands may be state-changing.
- Do not treat request_reference as an idempotency key unless a future transport package explicitly defines durable deduplication.
- Do not bypass the PKG-005 runtime for reads or writes.
- Simulation time and pause/player-presence rules remain owned by the runtime kernel.
- No public endpoint, MCP server, ChatGPT app/plugin, OAuth integration, provider-specific identity mapping or production secret store is part of this contract.

## Machine-readable tool contract

The companion player-command-tool.schema.json describes only model-controlled request and model-visible response fields. Trusted context and credentials are deliberately absent.
