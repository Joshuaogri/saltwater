"""Low-friction, text-first player command interface for Saltwater.

This is an application layer over the shared runtime kernel. It deliberately
accepts injected durable adapters; it does not pretend an in-memory test store
is a persistent game save.
"""
from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Callable
from uuid import UUID

from runtime.kernel import KernelError, Lifecycle, RuntimeKernel
from runtime.recruitment import PostgresRecruitmentService, RecruitmentError


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


HELP = """Saltwater commands
  help       Show available commands
  status     Show runtime and simulation clock
  profile    Show the active player profile
  recruit    Request entry as a recruit (pending until authorised)
  career     Inspect recruit intake and career status
  start      Enter active play
  pause      Pause the simulation
  resume     Resume active play
  quit       Leave the game (world time stops)
"""


class PlayerCommandInterface:
    """Small command router; domain mutations remain with their owning systems."""

    def __init__(self, kernel: RuntimeKernel, profile: PlayerProfile,
                 recruitment: PostgresRecruitmentService | None = None):
        self.kernel = kernel
        self.profile = profile
        self.recruitment = recruitment
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
        }

    def execute(self, line: str) -> CommandResult:
        try:
            parts = shlex.split(line)
        except ValueError as exc:
            return CommandResult(False, f"Could not parse command: {exc}")
        if not parts:
            return CommandResult(True, "Enter a command. Type help for the list.")
        if len(parts) != 1:
            return CommandResult(False, "This command takes no arguments. Type help.")
        command = parts[0].casefold()
        handler = self._commands.get(command)
        if handler is None:
            return CommandResult(False, f"Unknown command: {parts[0]}. Type help.")
        try:
            return handler()
        except KernelError as exc:
            return CommandResult(False, str(exc))

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
