"""Read-only PostgreSQL source for the NPC workforce and dispatch game layer."""
from __future__ import annotations

from typing import Any, Callable, Iterable

from runtime.npc_dispatch import NPCDispatchSimulator
from runtime.npc_dispatch_console import NPCDispatchConsole
from runtime.npc_workforce import NPCWorkforceGenerator


class PostgresNPCDispatchFactory:
    """Build an in-memory NPC dispatch world from canonical BP05/BP08 records.

    Only SELECT statements are issued. No personnel, membership, deployment,
    event, or production data is written by this factory.
    """

    POSTS_SQL = """
        SELECT p.post_id, p.component_id AS unit_id, d.position_title, d.position_type
        FROM sw_police.authorised_post p
        JOIN sw_police.position_definition d USING (position_id)
        WHERE p.post_status <> 'abolished'
        ORDER BY p.post_id
    """
    UNITS_SQL = """
        SELECT u.unit_id, u.functional_domain, u.dispatchable,
               u.minimum_crew_size, u.target_crew_size,
               s.operational_status, u.capability_codes
        FROM sw_police.unit_profile u
        JOIN sw_police.unit_current_status s USING (unit_id)
        WHERE u.lifecycle_state = 'active'
        ORDER BY u.unit_id
    """

    def __init__(self, connection_factory: Callable[[], Any], *, seed: int = 20261126):
        if not callable(connection_factory):
            raise TypeError("connection_factory must be callable")
        self._connection_factory = connection_factory
        self._generator = NPCWorkforceGenerator(seed=seed)

    def build(self, incidents: Iterable, *, current_shift: str = "Alpha") -> NPCDispatchConsole:
        try:
            with self._connection_factory() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(self.POSTS_SQL)
                    posts = [
                        {"post_id": row[0], "unit_id": row[1], "position_title": row[2], "position_type": row[3]}
                        for row in cursor.fetchall()
                    ]
                    cursor.execute(self.UNITS_SQL)
                    units = [
                        {
                            "unit_id": row[0],
                            "functional_domain": row[1],
                            "dispatchable": row[2],
                            "minimum_crew_size": row[3],
                            "target_crew_size": row[4],
                            "operational_status": row[5],
                            "capability_codes": row[6],
                        }
                        for row in cursor.fetchall()
                    ]
            if not posts:
                raise ValueError("The police establishment contains no authorised NPC posts.")
            if not units:
                raise ValueError("The police establishment contains no active unit profiles.")
            officers = self._generator.generate_shift_roster(posts)
            simulator = NPCDispatchSimulator(
                officers, units, current_shift=current_shift
            )
            return NPCDispatchConsole(simulator, incidents)
        except Exception as exc:
            raise RuntimeError("NPC dispatch world could not be loaded from police source records.") from exc
