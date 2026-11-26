"""BP11 read-only dispatch board over canonical BP12 and BP08 records.

The board never creates assignments or treats staffing eligibility as full
operational readiness. BP08's dispatch_eligible projection remains authoritative.
"""
from __future__ import annotations

from typing import Any, Callable
from uuid import UUID

from runtime.security import AuthorizationService, PrincipalKind


class DispatchBoardError(RuntimeError):
    """Dispatch board could not be read."""


class PostgresDispatchBoard:
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
            raise ValueError("dispatch board purpose must be police_workflow")
        self._connect = connect
        self._authorization = authorization
        self._principal_id = principal_id
        self._purpose = purpose

    def _require(self, credential: str, action: str, resource: str) -> None:
        decision = self._authorization.decide(
            credential,
            action=action,
            resource=resource,
            purpose=self._purpose,
            expected_principal_id=self._principal_id,
            expected_principal_kind=PrincipalKind.OFFICER,
        )
        if not decision.allowed:
            raise PermissionError("Access denied.")

    @staticmethod
    def _limit(limit: int) -> int:
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("Dispatch board limit must be between 1 and 100.")
        return limit

    def incident_queue(self, credential: str, *, limit: int = 25) -> list[dict]:
        """List live, non-terminal incidents for dispatcher review."""
        limit = self._limit(limit)
        self._require(
            credential, "bp11.dispatch.board.read", "dispatch-board:incidents"
        )
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT incident_id, incident_ref, status, source_type,
                               category_code, priority, severity_code,
                               priority_rationale, received_tick, created_tick,
                               updated_tick, location_count, source_count,
                               lead_unit_id, owning_function
                        FROM sw_incident.incident_current
                        WHERE status NOT IN
                          ('CLOSED','CANCELLED','DUPLICATE_LINKED')
                        ORDER BY priority ASC NULLS LAST, received_tick,
                                 incident_id
                        LIMIT %s
                        """,
                        (limit,),
                    )
                    rows = cur.fetchall()
            keys = (
                "incident_id", "incident_ref", "status", "source_type",
                "category_code", "priority", "severity_code",
                "priority_rationale", "received_tick", "created_tick",
                "updated_tick", "location_count", "source_count",
                "lead_unit_id", "owning_function",
            )
            return [dict(zip(keys, row)) for row in rows]
        except PermissionError:
            raise
        except Exception as exc:
            raise DispatchBoardError("Dispatch incident queue is unavailable.") from exc

    def unit_readiness(self, credential: str) -> list[dict]:
        """Read BP08 unit readiness, preserving every reason for ineligibility."""
        self._require(
            credential, "bp11.dispatch.units.read", "dispatch-board:units"
        )
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT r.unit_id, r.official_name, r.unit_type_code,
                               r.functional_domain, r.dispatchable,
                               r.minimum_crew_size, r.target_crew_size,
                               r.maximum_crew_size, r.active_members,
                               r.operational_status, r.staffing_eligible,
                               r.dispatch_eligible, r.readiness_reason,
                               p.capability_codes
                        FROM sw_police.unit_readiness r
                        JOIN sw_police.unit_profile p USING(unit_id)
                        WHERE r.dispatchable=true
                        ORDER BY r.functional_domain, r.official_name, r.unit_id
                        """
                    )
                    rows = cur.fetchall()
            keys = (
                "unit_id", "official_name", "unit_type_code",
                "functional_domain", "dispatchable", "minimum_crew_size",
                "target_crew_size", "maximum_crew_size", "active_members",
                "operational_status", "staffing_eligible", "dispatch_eligible",
                "readiness_reason", "resources_ready", "capability_codes",
            )
            return [dict(zip(keys, row)) for row in rows]
        except PermissionError:
            raise
        except Exception as exc:
            raise DispatchBoardError("Dispatch unit readiness is unavailable.") from exc

    def snapshot(
        self, credential: str, *, incident_limit: int = 25
    ) -> dict:
        """Compose an incident queue and actual BP08 unit readiness snapshot."""
        incidents = self.incident_queue(credential, limit=incident_limit)
        units = self.unit_readiness(credential)
        return {
            "incidents": incidents,
            "dispatchable_unit_profiles": units,
            "incident_count": len(incidents),
            "unit_profile_count": len(units),
            "eligible_unit_count": sum(
                1 for unit in units if unit["dispatch_eligible"] is True
            ),
            "snapshot_is_read_only": True,
            "assignments_created": 0,
        }
