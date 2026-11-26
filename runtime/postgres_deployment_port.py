"""PostgreSQL adapter for the BP08 unit deployment lifecycle ledger."""
from __future__ import annotations

from typing import Any, Callable
from uuid import UUID


class PostgresDeploymentPortError(RuntimeError):
    """The BP08 deployment writer could not complete a transition."""


class PostgresDeploymentPort:
    """Implements the port consumed by BP11DispatchLifecycle.

    Connection factory credentials and PostgreSQL grants are supplied by the
    trusted host. Each command executes one atomic database function call.
    """

    def __init__(self, connect: Callable[[], Any]):
        if not callable(connect):
            raise TypeError("connect must be a trusted connection factory")
        self._connect = connect

    def get_deployment(self, deployment_id: UUID) -> dict | None:
        if not isinstance(deployment_id, UUID):
            raise ValueError("deployment_id must be a UUID")
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT deployment_id, status, unit_id, task_ref, location_ref "
                        "FROM sw_police.unit_deployment WHERE deployment_id=%s",
                        (deployment_id,),
                    )
                    row = cur.fetchone()
            if row is None:
                return None
            return dict(zip(
                ("deployment_id", "status", "unit_id", "task_ref", "location_ref"),
                row,
            ))
        except Exception as exc:
            raise PostgresDeploymentPortError("Deployment lookup failed.") from exc

    def create_deployment(self, **command: Any) -> dict:
        required = {
            "unit_id", "incident_id", "membership_ids", "objective", "priority",
            "actor_ref", "authority_ref", "source_ref", "idempotency_key", "effective_tick",
        }
        if set(command) != required:
            raise ValueError("Invalid BP08 deployment creation command.")
        if not isinstance(command["membership_ids"], (list, tuple)) or not all(
            isinstance(value, UUID) for value in command["membership_ids"]
        ):
            raise ValueError("membership_ids must be UUID values.")
        if type(command["incident_id"]) is not int or command["incident_id"] < 1:
            raise ValueError("incident_id must be a positive integer.")
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT deployment_id,status,unit_id,assigned_members,event_id
                           FROM sw_police.create_authorised_unit_deployment(
                             %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (
                            command["unit_id"], command["incident_id"],
                            list(command["membership_ids"]), command["objective"],
                            command["priority"], command["actor_ref"],
                            command["authority_ref"], command["source_ref"],
                            command["idempotency_key"], command["effective_tick"],
                        ),
                    )
                    row = cur.fetchone()
            if row is None:
                raise PostgresDeploymentPortError("BP08 creation function returned no result.")
            return {"deployment_id": row[0], "status": row[1], "unit_id": row[2],
                    "assigned_members": row[3], "event_id": row[4]}
        except PostgresDeploymentPortError:
            raise
        except Exception as exc:
            raise PostgresDeploymentPortError("Deployment creation failed.") from exc

    def transition_deployment(self, **command: Any) -> dict:
        required = {
            "deployment_id", "expected_status", "resulting_status", "event_kind",
            "actor_ref", "reason", "source_ref", "idempotency_key", "effective_tick",
        }
        if set(command) != required:
            raise ValueError("Invalid BP08 deployment transition command.")
        if not isinstance(command["deployment_id"], UUID):
            raise ValueError("deployment_id must be a UUID")
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT deployment_id, status, event_id
                        FROM sw_police.transition_unit_deployment(
                          %s,%s,%s,%s,%s,%s,%s,%s,%s
                        )
                        """,
                        (
                            command["deployment_id"], command["expected_status"],
                            command["resulting_status"], command["event_kind"],
                            command["actor_ref"], command["reason"],
                            command["source_ref"], command["idempotency_key"],
                            command["effective_tick"],
                        ),
                    )
                    row = cur.fetchone()
            if row is None:
                raise PostgresDeploymentPortError("BP08 writer returned no result.")
            return {"deployment_id": row[0], "status": row[1], "event_id": row[2]}
        except PostgresDeploymentPortError:
            raise
        except Exception as exc:
            raise PostgresDeploymentPortError("Deployment transition failed.") from exc
