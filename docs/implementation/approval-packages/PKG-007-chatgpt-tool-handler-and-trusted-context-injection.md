# PKG-007 — ChatGPT Tool Handler and Trusted Context Injection

**Package:** PKG-007  
**Status:** Approved; implemented and verified  
**Target branch:** `main` only  
**Depends on:** PKG-005 verified; PKG-006 verified  
**Approval boundary:** Repository implementation and Python/contract tests only. No deployed endpoint, ChatGPT app/plugin, external identity provider, production secret store, Neon production change or live player session.

## 1. Objective

Implement the narrow server-side handler that turns the PKG-006 model-visible command schema into one callable host operation. The handler receives model-controlled tool arguments separately from trusted host-injected session context, validates the exact request shape, invokes `TrustedPlayerHostAdapter`, and returns only the documented response shape.

This package closes the in-repository tool-handler gap. It does not claim that ChatGPT has been connected to a deployed Saltwater service.

## 2. Existing authoritative components

Reuse without duplicating authority:
- `runtime/player_host_adapter.py` — validates trusted context, command allowlist and expiry; resolves the opaque game credential; calls PKG-005 only.
- `runtime/player_command_runtime.py` — authoritative game-session, identity, permission and audit enforcement.
- `docs/integration/CHATGPT-PLAYER-RUNTIME-CONTRACT.md` — trust and execution contract.
- `docs/integration/player-command-tool.schema.json` — model-visible request and response shape.

The handler must not access PostgreSQL, issue credentials, construct trusted context from tool arguments, infer player identity, grant permissions, or call command/domain services directly.

## 3. Proposed implementation

1. Add `runtime/chatgpt_tool_handler.py` with a small typed handler, e.g. `handle_player_command(tool_arguments, trusted_context)`.
2. Parse only a JSON object with `command_text` and optional `request_reference`. Reject unknown keys, missing command, wrong types, invalid length, multi-command strings and unsupported commands.
3. Receive `TrustedHostContext` only as a separate host-injected argument. Never read it from `tool_arguments`, serialized model content, request metadata controlled by the model, or a fallback.
4. Delegate accepted requests to `TrustedPlayerHostAdapter.execute(context, request)`.
5. Serialize only `{"ok": boolean, "message": string}`. Do not expose credentials, host references, player/principal/person IDs, database details, permission internals, exception text or stack traces.
6. Make malformed tool arguments fail closed before calling the credential provider or runtime.
7. Add contract tests for exact schema conformance, unknown-field rejection, missing/expired/forged context, valid command forwarding, denied command response, secret redaction and provider/runtime failures.
8. Add the suite to the existing disposable PostgreSQL/Python CI workflow. The handler tests should use fakes and must not require a live database.

## 4. Model-visible tool definition

The tool has one operation: `saltwater_player_command`.

Input:
- `command_text`: one of `help`, `status`, `profile`, `recruit`, `career`, `start`, `pause`, `resume`, `quit`.
- `request_reference`: optional opaque correlation reference, 1–128 characters.

No additional properties are accepted. In particular, no host context, host session ID, credential, player/principal/person ID, role, permission, career, profile, SQL or arbitrary command arguments.

Output:
- `ok`: boolean.
- `message`: safe string.

Trusted context is injected by host-side code through a separate non-model argument and is not part of the tool schema.

## 5. Acceptance criteria

- **P7-01:** A valid tool request reaches the existing PKG-006 adapter exactly once.
- **P7-02:** Trusted context is a separate required host argument and cannot be populated by model arguments.
- **P7-03:** Missing, expired or wrong-type context fails closed before credential resolution.
- **P7-04:** Unknown input keys and malformed JSON/object shapes are rejected before adapter invocation.
- **P7-05:** Only the exact PKG-006 command allowlist is accepted; arguments and multi-command payloads are rejected.
- **P7-06:** The response contains exactly `ok` and `message`.
- **P7-07:** No credential, host reference, identity identifier, exception or SQL detail leaks through response serialization.
- **P7-08:** Adapter/runtime denials are represented without weakening PKG-005 authorization or audit.
- **P7-09:** Unit/contract tests pass in CI.
- **P7-10:** Existing disposable PostgreSQL workflow remains green, including prior acceptance suites.
- **P7-11:** No persistent schema, migration, seed, Neon operation, deployed endpoint or plugin is introduced.

## 6. Explicit exclusions

- No public HTTP route, web server, API gateway or network listener.
- No actual ChatGPT app/plugin deployment or claim of live ChatGPT connectivity.
- No OAuth, account linking or provider-specific authentication.
- No production credential vault or persistent host-session mapping.
- No Neon production migrations, writes, credentials or connection changes.
- No new player identity, session issuance, permissions or automatic grants.
- No new game commands or hidden-truth access.
- No change to BP-01–BP-44 or other approved blueprint structure.

## 7. Test plan

Use deterministic fakes for trusted host context, credential provider and PKG-006 adapter. Test exact input/output schemas, allowlist, unknown keys, request-reference boundaries, context separation, expiry, fail-closed behavior, safe generic failures and non-leakage. Run the full existing Python and disposable PostgreSQL CI workflow to detect regressions.

## 8. Completion record

The user authorised completion of PKG-007. Implemented directly on `main`:
- `runtime/chatgpt_tool_handler.py` strictly parses JSON/object arguments, rejects unknown fields and malformed shapes, validates the exact command allowlist and optional request reference, requires separately injected unexpired `TrustedHostContext`, delegates once to PKG-006, and returns exactly `ok` and `message`.
- `tests/pkg001/test_chatgpt_tool_handler.py` covers valid JSON/object calls, schema boundary, malformed/multi-command/unknown input, request-reference bounds, absent/forged/expired context, context separation, denial, host-reference non-disclosure, malformed adapter responses and generic exception handling.
- `.github/workflows/pkg001-disposable-postgres.yml` runs the new contract suite.

**Verification:** Python and contract test job passed; full disposable PostgreSQL acceptance job passed, including the existing population-cap, database security, backup/restore and authenticated-command regression tests. Workflow: https://github.com/Joshuaogri/saltwater/actions/runs/45308750086. Migration validation: https://github.com/Joshuaogri/saltwater/actions/runs/45308723918. No Neon production operation, persistent schema change, endpoint, deployed ChatGPT integration, plugin, identity, session or permission grant was created.

PKG-007 is complete within its repository-only approval boundary. A deployed ChatGPT connection remains a separate future integration task.
