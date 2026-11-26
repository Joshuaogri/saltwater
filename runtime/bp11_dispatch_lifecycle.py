"""BP11 dispatch lifecycle orchestration over the canonical BP08 deployment port.

The service deliberately does not create a second assignment store. A trusted
BP08 gateway owns persistence, event creation, idempotency and transactionality.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from runtime.security import AuthorizationService, PrincipalKind


class DispatchLifecycleError(RuntimeError):
    """A dispatch lifecycle command could not be completed."""


_TRANSITIONS = {
    "authorised": {"issue": ("issued", "issued")},
    "issued": {
        "acknowledge": ("acknowledged", "acknowledged"),
        "refuse": ("rejected", "rejected"),
        "cancel": ("cancelled", "cancelled"),
        "reassign": ("reassigned", "reassigned"),
    },
    "acknowledged": {
        "mobilise": ("mobilising", "mobilising"),
        "refuse": ("rejected", "rejected"),
        "cancel": ("cancelled", "cancelled"),
        "reassign": ("reassigned", "reassigned"),
    },
    "mobilising": {
        "start": ("active", "started"),
        "cancel": ("cancelled", "cancelled"),
        "reassign": ("reassigned", "reassigned"),
    },
    "active": {
        "complete": ("completed", "completed"),
        "cancel": ("cancelled", "cancelled"),
        "reassign": ("reassigned", "reassigned"),
        "stand_down": ("stood_down", "stood_down"),
    },
}


class PostgresDispatchLifecycle:
    """Authorised command boundary for BP08 deployment lifecycle transitions.

    The injected BP08 port implements get_deployment(deployment_id) and
    transition_deployment(**command). It owns atomic compare-and-transition,
    BP35 event creation, BP08 append-only history, idempotency and transactions.
    """

    def __init__(
        self,
        authorization: AuthorizationService,
        principal_id: UUID,
        deployment_port: Any,
        *,
        purpose: str = "police_workflow",
    ):
        if not isinstance(authorization, AuthorizationService):
            raise TypeError("authorization must be an AuthorizationService")
        if not isinstance(principal_id, UUID):
            raise TypeError("principal_id must be a UUID")
        if not all(callable(getattr(deployment_port, name, None)) for name in (
            "get_deployment", "transition_deployment"
        )):
            raise TypeError("deployment_port must implement the BP08 deployment contract")
        if purpose != "police_workflow":
            raise ValueError("dispatch lifecycle purpose must be police_workflow")
        self._authorization = authorization
        self._principal_id = principal_id
        self._port = deployment_port
        self._purpose = purpose

    @staticmethod
    def _deployment_id(value: UUID) -> UUID:
        if not isinstance(value, UUID):
            raise ValueError("A deployment UUID is required.")
        return value

    @staticmethod
    def _required_text(value: str, name: str, maximum: int = 500) -> str:
        if not isinstance(value, str) or not value.strip() or len(value) > maximum:
            raise ValueError(f"{name} is required.")
        return value.strip()

    def _require(self, credential: str, action: str, deployment_id: UUID) -> None:
        decision = self._authorization.decide(
            credential,
            action=action,
            resource=f"dispatch-deployment:{deployment_id}",
            purpose=self._purpose,
            expected_principal_id=self._principal_id,
            expected_principal_kind=PrincipalKind.OFFICER,
        )
        if not decision.allowed:
            raise PermissionError("Access denied.")

    def transition(
        self,
        credential: str,
        deployment_id: UUID,
        *,
        command: str,
        expected_status: str,
        reason: str,
        source_ref: str,
        idempotency_key: str,
        effective_tick: int,
    ) -> dict:
        """Apply one allowed dispatch command against the expected BP08 state."""
        deployment_id = self._deployment_id(deployment_id)
        if command not in {
            "issue", "acknowledge", "refuse", "cancel", "reassign",
            "mobilise", "start", "complete", "stand_down",
        }:
            raise ValueError("Unsupported dispatch lifecycle command.")
        reason = self._required_text(reason, "reason")
        source_ref = self._required_text(source_ref, "source_ref", 200)
        idempotency_key = self._required_text(idempotency_key, "idempotency_key", 200)
        if type(effective_tick) is not int or effective_tick < 0:
            raise ValueError("effective_tick must be a non-negative integer.")
        if not isinstance(expected_status, str) or not expected_status:
            raise ValueError("expected_status is required.")

        self._require(credential, f"bp11.dispatch.{command}", deployment_id)
        try:
            current = self._port.get_deployment(deployment_id)
            if current is None:
                raise LookupError("Deployment was not found.")
            actual_status = current.get("status")
            if actual_status != expected_status:
                raise DispatchLifecycleError("Deployment status has changed; refresh the dispatch record.")
            allowed = _TRANSITIONS.get(actual_status, {})
            if command not in allowed:
                raise DispatchLifecycleError(
                    f"Command {command!r} is not valid from status {actual_status!r}."
                )
            resulting_status, event_kind = allowed[command]
            result = self._port.transition_deployment(
                deployment_id=deployment_id,
                expected_status=actual_status,
                resulting_status=resulting_status,
                event_kind=event_kind,
                actor_person_id=self._principal_id,
                reason=reason,
                source_ref=source_ref,
                idempotency_key=idempotency_key,
                effective_tick=effective_tick,
            )
            if not isinstance(result, dict):
                raise DispatchLifecycleError("BP08 deployment port returned an invalid result.")
            return result
        except (PermissionError, LookupError, ValueError, DispatchLifecycleError):
            raise
        except Exception as exc:
            raise DispatchLifecycleError("Dispatch lifecycle command failed.") from exc
