"""Read-only PostgreSQL source for the NPC workforce and dispatch game layer."""
from __future__ import annotations

from typing import Any, Callable, Iterable

from runtime.npc_dispatch import NPCDispatchSimulator
from runtime.npc_dispatch_console import NPCDispatchConsole
from runtime.npc_workforce import NPCOfficer, NPCWorkforceGenerator


class PostgresNPCDispatchFactory:
    """Build an NPC dispatch view from canonical personnel and BP08 units.

    Only existing active personnel and active primary memberships are loaded.
    The player-bound person is excluded. Vacant posts never create NPCs, and
    BP08's current unit status is authoritative. Only SELECT statements run.
    """

    STAFF_SQL = """
        SELECT p.personnel_id::text, p.service_number,
               person.given_name, person.family_name,
               p.service_standing, service.service_state, service.personnel_category,
               membership.unit_id, membership.post_id,
               position.position_title, position.position_type
        FROM sw_police.personnel p
        JOIN sw_police.personnel_service_current service
          ON service.personnel_id = p.personnel_id
        JOIN sw_people.person person ON person.person_id = p.person_id
        LEFT JOIN sw_police.unit_membership membership
          ON membership.personnel_id = p.personnel_id
         AND membership.membership_type = 'primary'
         AND membership.actual_end_tick IS NULL
        LEFT JOIN sw_police.career_post_appointment appointment
          ON appointment.position_appointment_id = membership.position_appointment_id
         AND appointment.effective_to_tick IS NULL
        LEFT JOIN sw_police.position_definition position
          ON position.position_id = appointment.position_id
        WHERE service.life_status = 1 AND service.scope_status = 1
          AND NOT EXISTS (
              SELECT 1 FROM sw_player.identity_binding player_binding
              WHERE player_binding.person_id = p.person_id
          )
        ORDER BY p.personnel_id
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
                    cursor.execute(self.STAFF_SQL)
                    staff_rows = cursor.fetchall()
                    officers = []
                    for row in staff_rows:
                        personnel_id, service_number, given, family, standing, service_state, category, unit_id, post_id, title, position_type = row
                        display_name = " ".join(part for part in (given, family) if isinstance(part, str) and part.strip())
                        if not display_name:
                            display_name = str(service_number)
                        if not title:
                            title = "Unassigned recruit" if standing == "recruit" else "Unassigned personnel"
                        if position_type not in {"sworn", "civilian", "mixed"}:
                            position_type = "sworn" if category == "sworn_officer" else "civilian"
                        officers.append(NPCOfficer(
                            npc_id=f"SWPERSONNEL:{personnel_id}",
                            service_number=str(service_number),
                            given_name=str(given or ""),
                            family_name=str(family or ""),
                            display_name=display_name,
                            unit_id=unit_id,
                            post_id=post_id,
                            position_title=str(title),
                            shift_group="Alpha",
                            service_state=str(service_state),
                            service_standing=str(standing),
                            position_type=position_type,
                        ))
                    officers = self._generator.assign_shift_groups(officers)
                    cursor.execute(self.UNITS_SQL)
                    units = [
                        {
                            "unit_id": row[0],
                            "functional_domain": row[1],
                            "dispatchable": row[2],
                            "minimum_crew_size": row[3],
                            "target_crew_size": row[4],
                            # BP08's current-status projection is authoritative.
                            # No status event means unavailable, not implicitly ready.
                            "operational_status": row[5],
                            "capability_codes": row[6],
                        }
                        for row in cursor.fetchall()
                    ]
            if not units:
                raise ValueError("The police establishment contains no active unit profiles.")
            simulator = NPCDispatchSimulator(
                officers, units, current_shift=current_shift
            )
            return NPCDispatchConsole(simulator, incidents)
        except Exception as exc:
            raise RuntimeError("NPC dispatch world could not be loaded from police source records.") from exc
