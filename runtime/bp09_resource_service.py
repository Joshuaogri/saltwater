"""BP09 officer-facing police resource readiness and inventory reads."""
from __future__ import annotations

from typing import Any, Callable
from uuid import UUID

from runtime.security import AuthorizationService, PrincipalKind


class ResourceServiceError(RuntimeError):
    """Police resource data could not be read."""


class PostgresResourceReadinessService:
    """Read-only unit resource view; never allocates or changes asset state."""

    def __init__(
        self,
        connect: Callable[[], Any],
        authorization: AuthorizationService,
        principal_id: UUID,
        *,
        purpose: str = "police_workflow",
    ):
        if not callable(connect):
            raise TypeError("connect must be a trusted connection factory")
        if not isinstance(authorization, AuthorizationService):
            raise TypeError("authorization must be an AuthorizationService")
        if not isinstance(principal_id, UUID):
            raise TypeError("principal_id must be a UUID")
        if purpose != "police_workflow":
            raise ValueError("resource service purpose must be police_workflow")
        self._connect = connect
        self._authorization = authorization
        self._principal_id = principal_id
        self._purpose = purpose

    @staticmethod
    def _unit_id(unit_id: str) -> str:
        if not isinstance(unit_id, str) or not unit_id or len(unit_id) > 120:
            raise ValueError("A valid unit ID is required.")
        return unit_id

    def _require(self, credential: str, unit_id: str) -> None:
        decision = self._authorization.decide(
            credential,
            action="bp09.resources.unit.read",
            resource=f"police-resources:unit:{unit_id}",
            purpose=self._purpose,
            expected_principal_id=self._principal_id,
            expected_principal_kind=PrincipalKind.OFFICER,
        )
        if not decision.allowed:
            raise PermissionError("Access denied.")

    def unit_readiness(self, credential: str, unit_id: str) -> dict:
        """Return requirement counts and whether mandatory resources are ready."""
        unit_id = self._unit_id(unit_id)
        self._require(credential, unit_id)
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT unit_id, resources_ready, requirement_count,
                               satisfied_requirements
                        FROM sw_police.unit_resource_readiness
                        WHERE unit_id=%s
                        """,
                        (unit_id,),
                    )
                    row = cur.fetchone()
            if row is None:
                raise LookupError("Unit resource readiness was not found.")
            keys = ("unit_id", "resources_ready", "requirement_count",
                    "satisfied_requirements")
            return dict(zip(keys, row))
        except (PermissionError, LookupError):
            raise
        except Exception as exc:
            raise ResourceServiceError("Unit resource readiness is unavailable.") from exc

    def unit_inventory(self, credential: str, unit_id: str) -> list[dict]:
        """Return per-model required, allocated and serviceable quantities."""
        unit_id = self._unit_id(unit_id)
        self._require(credential, unit_id)
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT req.resource_model_id, model.model_name,
                               req.minimum_quantity,
                               count(asset.asset_id) FILTER (
                                 WHERE allocation.status='active'
                                   AND allocation.effective_to_tick IS NULL
                                   AND asset.lifecycle_state='allocated'
                               )::integer AS allocated_quantity,
                               count(asset.asset_id) FILTER (
                                 WHERE allocation.status='active'
                                   AND allocation.effective_to_tick IS NULL
                                   AND asset.lifecycle_state='allocated'
                                   AND asset.serviceability_state='serviceable'
                               )::integer AS serviceable_quantity
                        FROM sw_police.unit_resource_requirement req
                        JOIN sw_police.resource_model model
                          USING(resource_model_id)
                        LEFT JOIN sw_police.resource_allocation allocation
                          ON allocation.unit_id=req.unit_id
                         AND allocation.status='active'
                         AND allocation.effective_to_tick IS NULL
                        LEFT JOIN sw_police.resource_asset asset
                          ON asset.asset_id=allocation.asset_id
                         AND asset.resource_model_id=req.resource_model_id
                        WHERE req.unit_id=%s
                        GROUP BY req.resource_model_id, model.model_name,
                                 req.minimum_quantity
                        ORDER BY model.model_name, req.resource_model_id
                        """,
                        (unit_id,),
                    )
                    rows = cur.fetchall()
            keys = ("resource_model_id", "model_name", "minimum_quantity",
                    "allocated_quantity", "serviceable_quantity")
            return [dict(zip(keys, row)) for row in rows]
        except PermissionError:
            raise
        except Exception as exc:
            raise ResourceServiceError("Unit resource inventory is unavailable.") from exc
