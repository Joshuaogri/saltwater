"""BP37 tick-scheduler integration for autonomous NPC police dispatch."""
from __future__ import annotations

from runtime.npc_dispatch_console import NPCDispatchConsole
from runtime.scheduling import (
    ScheduleDefinition,
    ScheduleExecutionResult,
    TickScheduler,
)


class NPCDispatchScheduleHandler:
    """Runs NPC dispatch as an owner-domain action on an authoritative game tick."""

    def __init__(self, console: NPCDispatchConsole, *, max_assignments_per_tick: int | None = None):
        if not isinstance(console, NPCDispatchConsole):
            raise TypeError("console must be an NPCDispatchConsole")
        if max_assignments_per_tick is not None and (
            type(max_assignments_per_tick) is not int or max_assignments_per_tick < 1
        ):
            raise ValueError("max_assignments_per_tick must be a positive integer or None")
        self.console = console
        self.max_assignments_per_tick = max_assignments_per_tick
        self.last_assigned_count = 0
        self.last_run_tick: int | None = None

    def __call__(self, schedule, *, world_tick: int) -> ScheduleExecutionResult:
        if schedule.owner_domain != "police" or schedule.subject_ref != "npc-dispatch":
            return ScheduleExecutionResult(
                False, error_code="npc_dispatch_schedule_mismatch",
                retry_after_tick=world_tick + 1,
            )
        assigned = self.console.process_dispatch_tick(
            max_assignments=self.max_assignments_per_tick
        )
        self.last_assigned_count = len(assigned)
        self.last_run_tick = world_tick
        return ScheduleExecutionResult(True)


def register_npc_dispatch_schedule(
    scheduler: TickScheduler,
    *,
    interval_ticks: int = 1,
    max_assignments_per_tick: int | None = None,
) -> tuple[int, NPCDispatchScheduleHandler]:
    """Register a recurring police dispatch decision on the game clock."""
    if type(interval_ticks) is not int or interval_ticks < 1:
        raise ValueError("interval_ticks must be a positive integer")
    handler = NPCDispatchScheduleHandler(
        scheduler.handlers.get("police_console")  # deliberately rejected below
    )
    return 0, handler
