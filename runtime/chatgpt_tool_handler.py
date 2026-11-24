"""Strict model-argument boundary for the Saltwater player command tool (PKG-007).

Trusted host context is a separate host-side argument and is never parsed from
model-controlled tool arguments. This module delegates all authority to PKG-006.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from runtime.player_host_adapter import (
    HostCommandRequest,
    HostCommandResponse,
    TrustedHostContext,
    TrustedPlayerHostAdapter,
)

_ALLOWED_COMMANDS = frozenset({
    "help", "status", "profile", "recruit", "career",
    "start", "pause", "resume", "quit",
})
_ALLOWED_KEYS = frozenset({"command_text", "request_reference"})
_MAX_COMMAND_LENGTH = 32
_MAX_REQUEST_REFERENCE = 128


def _parse_arguments(tool_arguments: Any) -> dict[str, Any] | None:
    """Accept a JSON object or decoded object; reject all other shapes."""
    if isinstance(tool_arguments, str):
        try:
            tool_arguments = json.loads(tool_arguments)
        except (json.JSONDecodeError, TypeError):
            return None
    if not isinstance(tool_arguments, dict):
        return None
    if set(tool_arguments) - _ALLOWED_KEYS:
        return None
    if "command_text" not in tool_arguments:
        return None
    command = tool_arguments["command_text"]
    if (not isinstance(command, str) or not command
            or len(command) > _MAX_COMMAND_LENGTH
            or command not in _ALLOWED_COMMANDS):
        return None
    reference = tool_arguments.get("request_reference")
    if reference is not None and (
        not isinstance(reference, str)
        or not reference.strip()
        or len(reference) > _MAX_REQUEST_REFERENCE
    ):
        return None
    return {"command_text": command, "request_reference": reference}


def handle_player_command(
    tool_arguments: Any,
    trusted_context: TrustedHostContext | None,
    adapter: TrustedPlayerHostAdapter,
) -> dict[str, bool | str]:
    """Validate untrusted arguments, require separate trusted context, delegate once.

    The returned object always has exactly ok and message. Exceptions and
    malformed adapter responses become a generic safe failure.
    """
    parsed = _parse_arguments(tool_arguments)
    if parsed is None:
        return {"ok": False, "message": "Invalid command request."}

    if not isinstance(trusted_context, TrustedHostContext):
        return {"ok": False, "message": "Access denied."}
    if trusted_context.expires_at <= datetime.now(timezone.utc):
        return {"ok": False, "message": "Access denied."}

    try:
        request = HostCommandRequest(
            command_text=parsed["command_text"],
            request_reference=parsed["request_reference"],
        )
        response = adapter.execute(trusted_context, request)
        if not isinstance(response, HostCommandResponse):
            return {"ok": False, "message": "Command unavailable."}
        if type(response.ok) is not bool or not isinstance(response.message, str):
            return {"ok": False, "message": "Command unavailable."}
        message = response.message
        if trusted_context.host_session_ref in message:
            return {"ok": False, "message": "Command unavailable."}
        return {"ok": response.ok, "message": message}
    except Exception:
        return {"ok": False, "message": "Command unavailable."}
