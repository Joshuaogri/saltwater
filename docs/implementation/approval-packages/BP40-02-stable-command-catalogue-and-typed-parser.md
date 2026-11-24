# BP40-02 — Stable Player Command Catalogue and Typed Input Parser

**Project:** Saltwater  
**Division:** BP-40 — Interface (fixed BP-01–BP-44 structure)  
**Package:** BP40-02  
**Status:** IMPLEMENTED AND VERIFIED — bounded package complete  
**Prepared:** 2026-11-24  
**Target branch:** `main` only  
**Neon production authority:** NONE

## 1. Purpose

Turn the existing working command surface into a single, stable, inspectable command contract. Every accepted command must have a canonical identifier, owner, input grammar, classification and permission action. The same parser and catalogue must govern the player interface, trusted gateway and host/tool boundaries so they cannot drift apart.

This is the next bounded interface foundation after BP40-01. It does not add police-domain features or imply that unfinished workspaces are operational.

## 2. Existing foundation

BP40-01 is implemented and verified. The current command set includes help, status, profile, recruit, career, start, pause, resume, quit, home, workspaces, workspace <id>, back and where. The parser and command allowlists are currently repeated across the player router, permission gateway and trusted host/tool boundary. BP40-02 consolidates those rules while preserving current command behavior and the existing authorization model.

## 3. Deliverables

### 3.1 Canonical command catalogue

Add `runtime/player_commands.py` containing immutable command definitions and one ordered registry for all currently supported commands.

Each definition records:
- Stable command ID and canonical token.
- Purpose/help text.
- Owning division/service.
- Exact argument grammar and accepted values.
- Classification: read-only, presentation-state or domain/runtime mutation.
- Required permission action (retain `player.command.<token>`).
- Whether confirmation is required by this bounded implementation.
- Whether the command may advance simulation time (only the existing explicit runtime lifecycle/time owner may do so; interface-only commands never do).

The registry includes only commands already implemented. It must not invent commands for case search, patrol, dispatch, evidence, people or other unconnected workspaces.

### 3.2 Typed parser

Provide a pure parser returning a typed parsed-command value or a typed parse error. Distinguish at least:
- Unknown command.
- Malformed quoting/syntax.
- Missing argument.
- Extra/invalid argument count.
- Invalid workspace identifier/value.

The parser must preserve input text and international names where those are valid future argument values; it must not destructively truncate, silently substitute, fuzzy-match or guess a target. For this package, the only argument-bearing command remains `workspace <exact-id>`.

### 3.3 One parser across all boundaries

Refactor `PlayerCommandInterface`, `AuthorizedPlayerCommandGateway`, `TrustedPlayerHostAdapter` and `runtime/chatgpt_tool_handler.py` to consume the canonical registry/parser rather than maintaining independent allowlists.

- The gateway authorizes the canonical command action before dispatch.
- The host/tool layer rejects invalid command syntax before resolving credentials.
- Unknown or malformed commands never reach authorization or dispatch.
- No permission grants, role changes or bypasses are added.
- `bingo` remains absent from the command catalogue and cannot become a general command.

### 3.4 Help and contract documentation

Generate command help from the canonical registry. Update the host contract and machine-readable schema from the same exact command grammar. Document command ownership, classification and distinct parse failures.

## 4. Required tests

Add `tests/pkg001/test_player_commands.py` and extend existing interface, gateway, host adapter and tool-handler suites.

Tests must prove:
1. Every currently supported command appears exactly once in the registry with a stable ID and owner.
2. Command order and IDs are deterministic.
3. Every command has a valid classification, permission action and explicit argument grammar.
4. The read-only/presentation-state/mutating classification is correct and no command is misrepresented as read-only.
5. Exact valid forms parse; missing, extra, malformed, unknown and invalid workspace inputs return distinct typed errors.
6. No fuzzy matching, case guessing for workspace IDs, truncation or silent substitution occurs.
7. Help is generated from the same registry and cannot drift from accepted commands.
8. Gateway permission is checked before dispatch using the canonical permission action.
9. Host/tool validation rejects malformed requests before credential resolution.
10. Existing command outcomes, recruit idempotency, lifecycle gates, hidden-truth protection and player-absence time freeze remain unchanged.
11. Parser use, help, status and navigation never advance world time.
12. No credentials, protected domain records or hidden offender truth appear in errors or help.

Run the full Python suite, full disposable PostgreSQL regression and database migration validation. No new SQL proposal is expected.

## 5. Acceptance criteria targeted

- UI-AT-012: stable, discoverable labels and command names.
- UI-AT-013: stable command identifier, purpose, owner, arguments, permissions and output contract.
- UI-AT-014: distinguish read-only, presentation-state and mutating commands.
- UI-AT-015: distinguish unknown, malformed, missing, invalid and ambiguous input classes.
- UI-AT-016: do not guess a target.
- UI-AT-022: attribute actions through existing player identity/authority context.
- UI-AT-023/024: preserve honest error and outcome distinctions.
- UI-AT-091/092: parser/help/navigation do not advance simulation time.
- UI-AT-102/103: preserve international input and reject invalid input without destructive rewriting.
- UI-AT-133: presentation/parser does not own domain truth or lifecycle.

Only these bounded criteria are targeted. Full BP-40 remains incomplete.

## 6. Explicit exclusions

- No new command that searches, opens, exports, creates or mutates a domain record.
- No new police-domain service, case/patrol/dispatch workflow or NPC behavior.
- No change to the fixed ten workspace IDs or BP-01–BP-44 division structure.
- No role, permission grant, authentication provider, session, credential or policy change.
- No change to recruit, career, lifecycle or scheduler business rules.
- No database schema, migration, seed, import, bulk write or Neon production operation.
- No browser frontend, deployment, maps, imagery or graphical dependency.
- No hidden-truth reveal route; exact `bingo` rules remain unchanged.
- No claim that BP-40 is complete.

## 7. Approval requested

Approve **BP40-02 — Stable Player Command Catalogue and Typed Input Parser** for:
1. Repository implementation directly on `main`.
2. Python tests and the existing disposable PostgreSQL regression workflow.
3. Host/tool contract and schema documentation updates plus reproducible test evidence.

Approval does not authorise Neon production operations, new credentials or permission grants, public deployment or full BP-40 completion.

## 8. Status

**IMPLEMENTED AND VERIFIED — bounded package complete.** The canonical catalogue/parser, four boundary integrations, generated help/schema contract and tests are committed directly to `main`. Full Python regression, dedicated parser acceptance, full disposable PostgreSQL regression and database migration validation passed; see [BP40-02 run 0001 evidence](../test-evidence/BP40-02-run-0001.md). BP-40 remains `DESIGNED_DRAFT`; no Neon production operation occurred.
