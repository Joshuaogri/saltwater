"""Low-friction, text-first player command interface for Saltwater.

This is an application layer over the shared runtime kernel. It deliberately
accepts injected durable adapters; it does not pretend an in-memory test store
is a persistent game save.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from uuid import UUID

from runtime.kernel import KernelError, Lifecycle, RuntimeKernel
from runtime.recruitment import PostgresRecruitmentService, RecruitmentError
from runtime.player_workspace import (WorkspaceNavigation, WORKSPACE_BY_ID, render_home, render_workspace_catalogue)
from runtime.player_commands import parse_player_command, render_command_help


@dataclass(frozen=True, slots=True)
class PlayerProfile:
    """Game-native player identity; not a real-world account or credential."""

    player_id: str
    display_name: str
    officer_person_id: int | None = None
    career_id: str | None = None
    career_stage: str = "not_started"

    def __post_init__(self) -> None:
        if not self.player_id.strip() or not self.display_name.strip():
            raise ValueError("player_id and display_name are required")
        if self.career_stage not in {"not_started", "recruit", "serving", "former"}:
            raise ValueError("unsupported career stage")


@dataclass(frozen=True, slots=True)
class CommandResult:
    ok: bool
    message: str
    quit_requested: bool = False


HELP = render_command_help()


class PlayerCommandInterface:
    """Small command router; domain mutations remain with their owning systems."""

    def __init__(self, kernel: RuntimeKernel, profile: PlayerProfile,
                 recruitment: PostgresRecruitmentService | None = None,
                 bp04_lookup: Any | None = None,
                 dispatch_console: Any | None = None,
                 npc_dispatch_console: Any | None = None,
                 hidden_truth_revealer: Callable[[str], str] | None = None):
        self.kernel = kernel
        self.profile = profile
        self.recruitment = recruitment
        self.bp04_lookup = bp04_lookup
        self.dispatch_console = dispatch_console
        self.npc_dispatch_console = npc_dispatch_console
        self.hidden_truth_revealer = hidden_truth_revealer
        self.workspace_navigation = WorkspaceNavigation()
        self._commands: dict[str, Callable[[], CommandResult]] = {
            "help": self._help,
            "status": self._status,
            "profile": self._profile,
            "recruit": self._recruit,
            "career": self._career,
            "start": self._start,
            "pause": self._pause,
            "resume": self._resume,
            "quit": self._quit,
            "home": self._home,
            "workspaces": self._workspaces,
            "back": self._back,
            "where": self._where,
            "dispatch": self._dispatch,
            "bingo": self._bingo,
        }

    def execute(self, line: str) -> CommandResult:
        parsed = parse_player_command(line)
        if not parsed.ok:
            error = parsed.error
            if error.code.value == "empty_input":
                return CommandResult(True, error.message)
            return CommandResult(False, error.message)
        command = parsed.command
        if command.token in {"find", "inspect"}:
            return self._property_lookup(command.token, command.arguments)
        if command.token == "dispatch":
            return self._dispatch(command.arguments)
        if command.token == "workspace":
            self.workspace_navigation = self.workspace_navigation.select(command.arguments[0])
            return CommandResult(True, f"Current workspace: {WORKSPACE_BY_ID[self.workspace_navigation.current].label}")
        handler = self._commands.get(command.token)
        if handler is None:
            return CommandResult(False, "Command unavailable.")
        try:
            return handler()
        except KernelError as exc:
            return CommandResult(False, str(exc))


    def _property_lookup(self, operation: str, arguments: tuple[str, ...]) -> CommandResult:
        if self.bp04_lookup is None:
            return CommandResult(False, "Property lookup service is not connected.")
        try:
            lookup = self.bp04_lookup
            if callable(lookup) and not callable(getattr(lookup, "search", None)):
                lookup = lookup()
                if lookup is None:
                    return CommandResult(False, "Property lookup service is not connected.")
                self.bp04_lookup = lookup
            entity_type = arguments[0]
            if operation == "find":
                matches = lookup.search(entity_type, " ".join(arguments[1:]), limit=10)
                if not matches:
                    return CommandResult(True, f"No {entity_type} records matched that search.")
                lines = [f"Matches: {len(matches)} (maximum 10)"]
                for row in matches:
                    if entity_type == "address":
                        label = row.get("address_label") or row.get("address_id")
                        lines.append(f"{row['address_id']} | {label} | property {row.get('property_id')}")
                    elif entity_type == "business":
                        label = row.get("trading_name") or row.get("registered_name") or row.get("business_id")
                        lines.append(f"{row['business_id']} | {label} | {row.get('sector')}")
                    else:
                        lines.append(
                            f"{row['property_id']} | {row.get('primary_use')} | "
                            f"{row.get('source_district_id')} / {row.get('source_neighbourhood_id')}"
                        )
                return CommandResult(True, "\\n".join(lines))

            identifier = arguments[1]
            if entity_type == "property":
                detail = lookup.property_detail(identifier)
                if detail is None:
                    return CommandResult(True, "Property not found.")
                prop, address = detail["property"], detail["address"]
                lines = [
                    f"Property: {prop['property_id']}",
                    f"Address: {(address or {}).get('address_label', 'not recorded')}",
                    f"Use: {prop.get('primary_use')}",
                    f"District / neighbourhood: {prop.get('source_district_id')} / {prop.get('source_neighbourhood_id')}",
                    f"Buildings: {len(detail['buildings'])}",
                    "Businesses: " + (", ".join(
                        row.get("trading_name") or row.get("registered_name") or row["business_id"]
                        for row in detail["businesses"]
                    ) or "none linked"),
                    f"Geography: {detail['geography_binding']}",
                ]
                return CommandResult(True, "\\n".join(lines))
            if entity_type == "address":
                detail = lookup.address_detail(identifier)
                if detail is None:
                    return CommandResult(True, "Address not found.")
                address = detail["address"]
                return CommandResult(True, "\\n".join((
                    f"Address: {address['address_id']}",
                    f"Label: {address.get('address_label')}",
                    f"Property: {address.get('property_id')}",
                    f"Road / district / neighbourhood: {address.get('road_id')} / {address.get('district_id')} / {address.get('neighbourhood_id')}",
                    f"Geography: {detail['geography_binding']}",
                )))
            if entity_type == "business":
                detail = lookup.business_detail(identifier)
                if detail is None:
                    return CommandResult(True, "Business not found.")
                business = detail["business"]
                lines = [
                    f"Business: {business['business_id']}",
                    f"Name: {business.get('trading_name') or business.get('registered_name')}",
                    f"Sector: {business.get('sector')}",
                    f"Status: {business.get('status')}",
                    f"Establishments: {len(detail['establishments'])}",
                ]
                for row in detail["establishments"][:20]:
                    address = row.get("address") or {}
                    lines.append(
                        f"{row['establishment_id']} | {row.get('establishment_name')} | "
                        f"{address.get('address_label', 'address unavailable')} | "
                        f"property {row.get('property_id')}"
                    )
                return CommandResult(True, "\\n".join(lines))

            record = lookup.get(entity_type, identifier)
            if record is None:
                return CommandResult(True, f"{entity_type.replace('_', ' ').title()} not found.")
            fields = (
                "property_id", "building_id", "premises_id", "unit_id",
                "access_point_id", "business_id", "establishment_id", "address_id",
                "building_use", "primary_function", "unit_locator", "access_type",
                "access_modes", "floor_name", "primary_use",
            )
            lines = [f"{entity_type.replace('_', ' ').title()}: {identifier}"]
            for field in fields:
                if field in record and record[field] is not None:
                    lines.append(f"{field.replace('_', ' ').title()}: {record[field]}")
            return CommandResult(True, "\\n".join(lines))
        except (KeyError, ValueError) as exc:
            return CommandResult(False, f"Property lookup unavailable: {exc}")
        except Exception:
            return CommandResult(False, "Property lookup unavailable.")

    def _bingo(self) -> CommandResult:
        """Reveal case truth only through the trusted, gateway-authorised service."""
        if self.hidden_truth_revealer is None:
            return CommandResult(False, "Hidden-truth reveal service is not connected.")
        try:
            result = self.hidden_truth_revealer(self.profile.player_id)
            if not isinstance(result, str) or not result.strip():
                return CommandResult(False, "No revealable hidden truth is available.")
            return CommandResult(True, result)
        except Exception:
            return CommandResult(False, "Hidden-truth reveal is unavailable.")

    def _dispatch(self, arguments: tuple[str, ...] = ()):
        if self.npc_dispatch_console is not None:
            try:
                return CommandResult(True, self.npc_dispatch_console.execute(arguments))
            except Exception as exc:
                return CommandResult(False, str(exc))
        if arguments:
            return CommandResult(False, "NPC dispatch commands are not connected. Use dispatch to view the board.")
        if self.dispatch_console is None:
            return CommandResult(False, "Dispatcher console is not connected.")
        try:
            snapshot = self.dispatch_console.snapshot(incident_limit=25)
            return CommandResult(True, self.dispatch_console.render(snapshot))
        except Exception:
            return CommandResult(False, "Dispatcher console is unavailable.")

    def _home(self) -> CommandResult:
        return CommandResult(True, render_home(self.profile, self.kernel.status(), self.workspace_navigation))

    def _workspaces(self) -> CommandResult:
        return CommandResult(True, render_workspace_catalogue(self.workspace_navigation.current))

    def _back(self) -> CommandResult:
        self.workspace_navigation = self.workspace_navigation.back()
        return CommandResult(True, f"Current workspace: {WORKSPACE_BY_ID[self.workspace_navigation.current].label}")

    def _where(self) -> CommandResult:
        current = WORKSPACE_BY_ID[self.workspace_navigation.current]
        return CommandResult(True, f"Workspace: {current.label} ({current.id})\nSelected record: none\nCapability: {current.availability}")

    def _help(self) -> CommandResult:
        return CommandResult(True, HELP.rstrip())

    def _status(self) -> CommandResult:
        state = self.kernel.status()
        return CommandResult(
            True,
            "\n".join((
                f"Runtime: {state.lifecycle.value}",
                f"Player present: {'yes' if state.player_present else 'no'}",
                f"World tick: {state.world_tick}",
                f"Calendar: day {state.calendar_day}, minute {state.minute_of_day}",
            )),
        )

    def _profile(self) -> CommandResult:
        p = self.profile
        return CommandResult(
            True,
            "\n".join((
                f"Player: {p.display_name}",
                f"Player ID: {p.player_id}",
                f"Career: {p.career_stage}",
                f"Officer person ID: {p.officer_person_id if p.officer_person_id is not None else 'not assigned'}",
                f"Career ID: {p.career_id or 'not started'}",
            )),
        )


    def _recruit(self) -> CommandResult:
        if self.recruitment is None:
            return CommandResult(False, "Recruitment service is not connected.")
        try:
            player_id = UUID(self.profile.player_id)
            intake_id = self.recruitment.request_intake(
                player_id, self.profile.display_name,
                f"recruit-request:{player_id}",
            )
        except (ValueError, RecruitmentError) as exc:
            return CommandResult(False, f"Recruit request unavailable: {exc}")
        return CommandResult(
            True,
            f"Recruit intake {intake_id} is pending. No police appointment or career is active yet.",
        )

    def _career(self) -> CommandResult:
        if self.recruitment is None:
            return CommandResult(False, "Recruitment service is not connected.")
        try:
            player_id = UUID(self.profile.player_id)
            records = self.recruitment.status(player_id)
        except (ValueError, RecruitmentError) as exc:
            return CommandResult(False, f"Career status unavailable: {exc}")
        if not records:
            return CommandResult(True, "No recruit intake or police career has been recorded.")
        lines = []
        for item in records:
            lines.append(
                f"Intake: {item.intake_status} (requested tick {item.requested_tick})"
            )
            if item.career_id is None:
                lines.append("Career: not active; appointment outcome is pending")
            else:
                lines.append(
                    f"Career: {item.career_stage}/{item.career_status}; "
                    f"service {item.service_number}; standing {item.service_standing}"
                )
        return CommandResult(True, "\n".join(lines))

    def _start(self) -> CommandResult:
        state = self.kernel.status()
        if state.lifecycle == Lifecycle.PAUSED:
            return CommandResult(False, "Simulation is paused. Use resume to continue.")
        if state.lifecycle == Lifecycle.STOPPED:
            # Re-entry is explicit: move through READY first. This does not
            # restore player presence or advance time; the RUNNING transition
            # below is the only operation that makes the player present.
            self.kernel.transition(Lifecycle.READY, player_present=False)
            state = self.kernel.status()
        state = self.kernel.transition(Lifecycle.RUNNING, player_present=True)
        return CommandResult(True, f"Active play started at world tick {state.world_tick}.")

    def _pause(self) -> CommandResult:
        self.kernel.transition(Lifecycle.PAUSED, player_present=True)
        return CommandResult(True, "Simulation paused. World time is frozen.")

    def _resume(self) -> CommandResult:
        state = self.kernel.transition(Lifecycle.RUNNING, player_present=True)
        return CommandResult(True, f"Simulation resumed at world tick {state.world_tick}.")

    def _quit(self) -> CommandResult:
        state = self.kernel.status()
        if state.lifecycle == Lifecycle.STOPPED:
            return CommandResult(True, "Game is already stopped.", quit_requested=True)
        self.kernel.transition(Lifecycle.STOPPED, player_present=False)
        return CommandResult(True, "Game closed. Player absent; world time is frozen.", quit_requested=True)
