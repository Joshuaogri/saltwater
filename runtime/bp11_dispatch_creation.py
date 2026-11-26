"""Officer-authorised BP11 creation of incident-response deployments."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from runtime.security import AuthorizationService, PrincipalKind


class DispatchCreationError(RuntimeError):
    """An incident-response deployment could not be created."""


class PostgresDispatchCreationService:
    def __init__(self, authorization: AuthorizationService, principal_id: UUID, deployment_port: Any):
        if not callable(getattr(authorization, "decide", None)):
            raise TypeError("authorization must provide a decide method")
        if not isinstance(principal_id, UUID):
            raise TypeError("principal_id must be a UUID")
        if not callable(getattr(deployment_port, "create_deployment", None)):
            raise TypeError("deployment port must implement create_deployment")
        self._authorization = authorization
        self._principal_id = principal_id
        self._port = deployment_port

    def create(
        self, credential: str, *, unit_id: str, incident_id: int,
        membership_ids: list[UUID], objective: str, priority: int,
        authority_ref: str, source_ref: str, idempotency_key: str,
        effective_tick: int,
    ) -> dict:
        if not isinstance(unit_id, str) or not unit_id.strip():
            raise ValueError("unit_id is required")
        if type(incident_id) is not int or incident_id < 1:
            raise ValueError("incident_id must be positive")
        if not isinstance(membership_ids, list) or not membership_ids or not all(
            isinstance(value, UUID) for value in membership_ids
        ):
            raise ValueError("At least one valid crew membership ID is required")
        if not isinstance(objective, str) or not objective.strip() or len(objective)>1000:
            raise ValueError("objective is required")
        if type(priority) is not int or priority not in range(1,6):
            raise ValueError("priority must be between 1 and 5")
        for value, name in ((authority_ref,"authority_ref"),(source_ref,"source_ref"),
                            (idempotency_key,"idempotency_key")):
            if not isinstance(value,str) or not value.strip() or len(value)>200:
                raise ValueError(f"{name} is required")
        if type(effective_tick) is not int or effective_tick<0:
            raise ValueError("effective_tick must be non-negative")
        decision=self._authorization.decide(
            credential,action="bp11.dispatch.create",
            resource=f"dispatch-incident:{incident_id}",
            purpose="police_workflow",expected_principal_id=self._principal_id,
            expected_principal_kind=PrincipalKind.OFFICER,
        )
        if not decision.allowed or type(decision.active_person_id) is not int or decision.active_person_id<1:
            raise PermissionError("Access denied.")
        try:
            result=self._port.create_deployment(
                unit_id=unit_id.strip(),incident_id=incident_id,
                membership_ids=membership_ids,objective=objective.strip(),
                priority=priority,actor_ref=f"officer-person:{decision.active_person_id}",
                authority_ref=authority_ref.strip(),source_ref=source_ref.strip(),
                idempotency_key=idempotency_key.strip(),effective_tick=effective_tick,
            )
            if not isinstance(result,dict) or result.get("status")!="authorised":
                raise DispatchCreationError("Deployment writer returned an invalid result.")
            return result
        except (PermissionError,ValueError,DispatchCreationError):
            raise
        except Exception as exc:
            raise DispatchCreationError("Incident-response deployment was not created.") from exc
