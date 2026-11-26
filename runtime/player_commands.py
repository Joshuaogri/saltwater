"""Canonical Saltwater player command catalogue and typed parser.

This is the sole grammar/metadata authority used by the interface, gateway,
trusted host and ChatGPT tool boundary. Parsing is pure and never dispatches.
"""
from __future__ import annotations

import shlex
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Final


class CommandClass(str, Enum):
    READ_ONLY = "read_only"
    PRESENTATION_STATE = "presentation_state"
    DOMAIN_MUTATION = "domain_runtime_mutation"


class ParseErrorCode(str, Enum):
    EMPTY_INPUT = "empty_input"
    MALFORMED_SYNTAX = "malformed_syntax"
    UNKNOWN_COMMAND = "unknown_command"
    MISSING_ARGUMENT = "missing_argument"
    INVALID_ARGUMENT_COUNT = "invalid_argument_count"
    INVALID_VALUE = "invalid_value"


@dataclass(frozen=True, slots=True)
class PlayerCommandDefinition:
    command_id: str
    token: str
    purpose: str
    owner: str
    argument_grammar: str
    classification: CommandClass
    permission_action: str
    confirmation_required: bool = False
    may_advance_time: bool = False


@dataclass(frozen=True, slots=True)
class ParsedPlayerCommand:
    definition: PlayerCommandDefinition
    arguments: tuple[str, ...]
    original_text: str

    @property
    def token(self) -> str:
        return self.definition.token

    @property
    def permission_action(self) -> str:
        return self.definition.permission_action


@dataclass(frozen=True, slots=True)
class CommandParseError:
    code: ParseErrorCode
    message: str
    supplied_token: str | None = None


@dataclass(frozen=True, slots=True)
class CommandParseResult:
    """Immutable typed result; exactly one of command/error is populated."""
    command: ParsedPlayerCommand | None = None
    error: CommandParseError | None = None

    def __post_init__(self) -> None:
        if (self.command is None) == (self.error is None):
            raise ValueError("exactly one of command or error is required")

    @property
    def ok(self) -> bool:
        return self.command is not None


def _definition(
    token: str,
    purpose: str,
    owner: str,
    classification: CommandClass,
    grammar: str = "no arguments",
) -> PlayerCommandDefinition:
    return PlayerCommandDefinition(
        command_id=f"player.{token}.v1",
        token=token,
        purpose=purpose,
        owner=owner,
        argument_grammar=grammar,
        classification=classification,
        permission_action=f"player.command.{token}",
    )


_DEFINITIONS: Final[tuple[PlayerCommandDefinition, ...]] = (
    _definition("help", "Show available commands", "BP-40 Interface", CommandClass.READ_ONLY),
    _definition("status", "Show runtime and simulation clock", "BP-40 Interface", CommandClass.READ_ONLY),
    _definition("profile", "Show the active player profile", "BP-40 Interface", CommandClass.READ_ONLY),
    _definition("recruit", "Request entry as a recruit", "BP-04 Recruitment", CommandClass.DOMAIN_MUTATION),
    _definition("career", "Inspect recruit intake and career status", "BP-04 Personnel", CommandClass.READ_ONLY),
    _definition("start", "Enter active play", "BP-40 Runtime Lifecycle", CommandClass.DOMAIN_MUTATION),
    _definition("pause", "Pause the simulation", "BP-40 Runtime Lifecycle", CommandClass.DOMAIN_MUTATION),
    _definition("resume", "Resume active play", "BP-40 Runtime Lifecycle", CommandClass.DOMAIN_MUTATION),
    _definition("quit", "Leave the game; world time stops", "BP-40 Runtime Lifecycle", CommandClass.DOMAIN_MUTATION),
    _definition("home", "Show the player home / shift desk", "BP-40 Interface", CommandClass.PRESENTATION_STATE),
    _definition("workspaces", "List all workspaces", "BP-40 Interface", CommandClass.READ_ONLY),
    _definition("workspace", "Select an exact workspace ID", "BP-40 Interface", CommandClass.PRESENTATION_STATE, "one exact workspace ID"),
    _definition("back", "Return to the previous workspace", "BP-40 Interface", CommandClass.PRESENTATION_STATE),
    _definition("where", "Show current workspace and selected-record state", "BP-40 Interface", CommandClass.READ_ONLY),
    _definition("find", "Search public property, address or business records", "BP-04 Property Lookup", CommandClass.READ_ONLY, "address|property|business plus search text"),
    _definition("inspect", "Inspect one property, address, building, premises, unit, access point, business or establishment", "BP-04 Property Lookup", CommandClass.READ_ONLY, "one entity type and one stable ID"),
    _definition("dispatch", "View NPC dispatch or issue a unit assignment", "BP-11 Dispatch", CommandClass.DOMAIN_MUTATION, "optional assign <incident-id> or deployment action <deployment-id>"),
)

COMMAND_CATALOGUE: Final[tuple[PlayerCommandDefinition, ...]] = _DEFINITIONS
COMMAND_BY_TOKEN: Final = MappingProxyType({
    item.token: item for item in COMMAND_CATALOGUE
})
if len(COMMAND_BY_TOKEN) != len(COMMAND_CATALOGUE):
    raise RuntimeError("duplicate player command token in canonical catalogue")
COMMAND_IDS: Final[frozenset[str]] = frozenset(item.command_id for item in COMMAND_CATALOGUE)


def render_command_help() -> str:
    """Render the human help text from the canonical command definitions."""
    lines = ["Saltwater commands"]
    for item in COMMAND_CATALOGUE:
        suffix = " <id>" if item.token == "workspace" else " <type> <query>" if item.token == "find" else " <type> <id>" if item.token == "inspect" else ""
        lines.append(f"  {item.token}{suffix}  {item.purpose}")
    return "\n".join(lines)


def parse_player_command(
    text: str,
    *,
    require_canonical_token: bool = False,
    require_canonical_spacing: bool = False,
) -> CommandParseResult:
    """Parse one command without fuzzy matching, rewriting or target guessing."""
    if not isinstance(text, str) or not text.strip():
        return CommandParseResult(error=CommandParseError(
            ParseErrorCode.EMPTY_INPUT, "Enter a command. Type help for the list."
        ))
    try:
        parts = shlex.split(text, posix=True)
    except ValueError:
        return CommandParseResult(error=CommandParseError(
            ParseErrorCode.MALFORMED_SYNTAX, "Malformed command syntax."
        ))
    if not parts:
        return CommandParseResult(error=CommandParseError(
            ParseErrorCode.EMPTY_INPUT, "Enter a command. Type help for the list."
        ))

    supplied = parts[0]
    token = supplied if require_canonical_token else supplied.casefold()
    definition = COMMAND_BY_TOKEN.get(token)
    if definition is None:
        return CommandParseResult(error=CommandParseError(
            ParseErrorCode.UNKNOWN_COMMAND, f"Unknown command: {supplied}. Type help.",
            supplied_token=supplied,
        ))
    if require_canonical_spacing:
        canonical = text == text.strip() and text == " ".join(parts)
        if not canonical or supplied != definition.token:
            return CommandParseResult(error=CommandParseError(
                ParseErrorCode.MALFORMED_SYNTAX, "Command must use its exact canonical form.",
                supplied_token=supplied,
            ))

    args = tuple(parts[1:])
    if definition.token == "workspace":
        if not args:
            return CommandParseResult(error=CommandParseError(
                ParseErrorCode.MISSING_ARGUMENT, "Use workspace <exact-id>. Type workspaces.",
                supplied_token=supplied,
            ))
        if len(args) != 1:
            return CommandParseResult(error=CommandParseError(
                ParseErrorCode.INVALID_ARGUMENT_COUNT, "workspace accepts exactly one workspace ID.",
                supplied_token=supplied,
            ))
        from runtime.player_workspace import WORKSPACE_BY_ID
        if args[0] not in WORKSPACE_BY_ID:
            return CommandParseResult(error=CommandParseError(
                ParseErrorCode.INVALID_VALUE, f"Unknown workspace ID: {args[0]}",
                supplied_token=supplied,
            ))
    elif definition.token == "find":
        if not args:
            return CommandParseResult(error=CommandParseError(
                ParseErrorCode.MISSING_ARGUMENT,
                "Use find address|property|business <search text>.",
                supplied_token=supplied,
            ))
        if args[0] not in {"address", "property", "business"}:
            return CommandParseResult(error=CommandParseError(
                ParseErrorCode.INVALID_VALUE,
                "find supports address, property or business.",
                supplied_token=supplied,
            ))
        if len(args) < 2:
            return CommandParseResult(error=CommandParseError(
                ParseErrorCode.MISSING_ARGUMENT,
                "Use find <type> <search text>.",
                supplied_token=supplied,
            ))
        if len(" ".join(args[1:]).strip()) < 2:
            return CommandParseResult(error=CommandParseError(
                ParseErrorCode.INVALID_VALUE, "Search text must contain at least two characters.",
                supplied_token=supplied,
            ))
    elif definition.token == "inspect":
        if len(args) != 2:
            return CommandParseResult(error=CommandParseError(
                ParseErrorCode.INVALID_ARGUMENT_COUNT,
                "Use inspect <entity-type> <stable-id>.",
                supplied_token=supplied,
            ))
        if args[0] not in {
            "property", "address", "building", "premises", "unit",
            "access_point", "business", "establishment",
        }:
            return CommandParseResult(error=CommandParseError(
                ParseErrorCode.INVALID_VALUE, "Unsupported BP04 entity type.",
                supplied_token=supplied,
            ))
    elif definition.token == "dispatch":
        valid_actions = {"assign", "arrive", "begin", "finish", "clear", "stand_down", "available"}
        if args and (len(args) != 2 or args[0] not in valid_actions or not args[1].strip()):
            return CommandParseResult(error=CommandParseError(
                ParseErrorCode.INVALID_ARGUMENT_COUNT,
                "Use dispatch, dispatch assign <incident-id>, or a deployment action and deployment ID.",
                supplied_token=supplied,
            ))
    elif args:
        return CommandParseResult(error=CommandParseError(
            ParseErrorCode.INVALID_ARGUMENT_COUNT,
            f"{definition.token} takes no arguments.",
            supplied_token=supplied,
        ))

    return CommandParseResult(command=ParsedPlayerCommand(
        definition=definition, arguments=args, original_text=text
    ))
