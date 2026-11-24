"""Provider-neutral trusted host adapter for PKG-006.

The host context and credential provider are supplied by trusted server code.
Model-controlled requests contain only one existing command and an optional
bounded request reference. This module never creates sessions or grants.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

from runtime.player_command_runtime import PostgresPlayerCommandRuntime
from runtime.player_commands import parse_player_command

_MAX_REQUEST_REFERENCE = 128


@dataclass(frozen=True, slots=True)
class TrustedHostContext:
    """Opaque host-session reference created by trusted host-side code only.

    Never deserialize this object from model/tool arguments or expose its
    reference in a model-visible response.
    """
    host_session_ref: str
    expires_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.host_session_ref, str) or not self.host_session_ref.strip():
            raise ValueError("trusted host context reference is required")
        if len(self.host_session_ref) > 512:
            raise ValueError("trusted host context reference is too long")
        if not isinstance(self.expires_at, datetime) or self.expires_at.tzinfo is None:
            raise ValueError("trusted host context requires an aware expiry")


@runtime_checkable
class HostCredentialProvider(Protocol):
    """Resolve a trusted host context to its opaque game-session credential."""
    def resolve(self, context: TrustedHostContext) -> str | None: ...


@runtime_checkable
class PlayerCommandRuntime(Protocol):
    """The sole command execution capability exposed to this adapter."""
    def execute(self, credential: str, command_text: str): ...


@dataclass(frozen=True, slots=True)
class HostCommandRequest:
    """Model-controlled fields: command text and optional opaque request ref."""
    command_text: str
    request_reference: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.command_text, str):
            raise TypeError("command_text must be text")
        if self.request_reference is not None:
            if (not isinstance(self.request_reference, str)
                    or len(self.request_reference) > _MAX_REQUEST_REFERENCE
                    or not self.request_reference.strip()):
                raise ValueError("request reference must be 1-128 nonblank characters")


@dataclass(frozen=True, slots=True)
class HostCommandResponse:
    ok: bool
    message: str


class TrustedPlayerHostAdapter:
    """Resolve trusted context, then invoke only the PKG-005 runtime."""

    def __init__(
        self,
        credential_provider: HostCredentialProvider,
        command_runtime: PlayerCommandRuntime,
    ) -> None:
        if not callable(getattr(credential_provider, "resolve", None)):
            raise TypeError("credential_provider must provide resolve(context)")
        if not callable(getattr(command_runtime, "execute", None)):
            raise TypeError("command_runtime must provide execute(credential, command)")
        self._credential_provider = credential_provider
        self._command_runtime = command_runtime

    def execute(
        self,
        context: TrustedHostContext | None,
        request: HostCommandRequest,
    ) -> HostCommandResponse:
        """Execute one allowed command without surfacing credentials or internals."""
        if not isinstance(request, HostCommandRequest):
            return HostCommandResponse(False, "Invalid command request.")
        if not isinstance(context, TrustedHostContext):
            return HostCommandResponse(False, "Access denied.")
        if context.expires_at <= datetime.now(timezone.utc):
            return HostCommandResponse(False, "Access denied.")

        parsed = parse_player_command(request.command_text)
        if not parsed.ok:
            return HostCommandResponse(False, "Invalid command.")


        try:
            credential = self._credential_provider.resolve(context)
            if not isinstance(credential, str) or not credential:
                return HostCommandResponse(False, "Access denied.")
            result = self._command_runtime.execute(credential, request.command_text)
            if not hasattr(result, "ok") or not hasattr(result, "message"):
                return HostCommandResponse(False, "Command unavailable.")
            message = str(result.message)
            if credential in message:
                return HostCommandResponse(False, "Command unavailable.")
            return HostCommandResponse(bool(result.ok), message)
        except Exception:
            return HostCommandResponse(False, "Command unavailable.")
