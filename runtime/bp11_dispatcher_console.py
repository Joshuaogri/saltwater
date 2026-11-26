"""Officer-facing BP11 dispatcher console composition."""
from __future__ import annotations

from typing import Any
from uuid import UUID


class DispatcherConsoleError(RuntimeError):
    """The dispatcher console could not produce a safe operational view."""


class PostgresDispatcherConsole:
    """Compose the authorised BP11 board and lifecycle command boundary.

    The credential is supplied by trusted host context, never by player text.
    """

    def __init__(self, board: Any, lifecycle: Any, credential: str):
        if not callable(getattr(board, "snapshot", None)):
            raise TypeError("board must provide snapshot")
        if not callable(getattr(lifecycle, "transition", None)):
            raise TypeError("lifecycle must provide transition")
        if not isinstance(credential, str) or not credential:
            raise ValueError("trusted dispatcher credential is required")
        self._board = board
        self._lifecycle = lifecycle
        self._credential = credential

    def snapshot(self, *, incident_limit: int = 25) -> dict:
        try:
            result = self._board.snapshot(
                self._credential, incident_limit=incident_limit
            )
            if not isinstance(result, dict):
                raise DispatcherConsoleError("Dispatch board returned an invalid snapshot.")
            return result
        except Exception as exc:
            if isinstance(exc, DispatcherConsoleError):
                raise
            raise DispatcherConsoleError("Dispatcher console is unavailable.") from exc

    def create_deployment(self, creation_service: Any, **command: Any) -> dict:
        """Create a deployment through the officer-authorised creation service."""
        if not callable(getattr(creation_service, "create", None)):
            raise TypeError("creation_service must provide create")
        try:
            return creation_service.create(self._credential, **command)
        except Exception as exc:
            raise DispatcherConsoleError("Deployment creation was not completed.") from exc

    def transition(
        self, deployment_id: UUID, *, command: str, expected_status: str,
        reason: str, source_ref: str, idempotency_key: str, effective_tick: int,
    ) -> dict:
        try:
            return self._lifecycle.transition(
                self._credential, deployment_id, command=command,
                expected_status=expected_status, reason=reason,
                source_ref=source_ref, idempotency_key=idempotency_key,
                effective_tick=effective_tick,
            )
        except Exception as exc:
            raise DispatcherConsoleError("Dispatch command was not completed.") from exc

    @staticmethod
    def render(snapshot: dict) -> str:
        incidents = snapshot.get("incidents")
        units = snapshot.get("dispatchable_unit_profiles")
        if not isinstance(incidents, list) or not isinstance(units, list):
            raise DispatcherConsoleError("Dispatch snapshot is incomplete.")
        lines = [
            "SALTWATER DISPATCH",
            f"Open incidents: {len(incidents)}",
            f"Dispatchable unit profiles: {len(units)}",
            f"Currently eligible units: {snapshot.get('eligible_unit_count', 0)}",
            "",
            "INCIDENT QUEUE",
        ]
        if not incidents:
            lines.append("No open incidents.")
        for row in incidents:
            lines.append(
                f"{row.get('incident_ref') or row.get('incident_id')} | "
                f"{row.get('priority') or 'unprioritised'} | "
                f"{row.get('severity_code') or 'unassessed'} | "
                f"{row.get('status')}"
            )
        lines.extend(("", "UNIT READINESS"))
        if not units:
            lines.append("No dispatchable unit profiles returned.")
        for row in units:
            eligible = row.get("dispatch_eligible") is True
            lines.append(
                f"{row.get('unit_id')} | {row.get('official_name')} | "
                f"{'ELIGIBLE' if eligible else 'NOT ELIGIBLE'} | "
                f"{row.get('readiness_reason') or 'No reason supplied'}"
            )
        lines.extend(("", "Board is read-only; deployments change only through authorised BP11 commands."))
        return "\n".join(lines)
