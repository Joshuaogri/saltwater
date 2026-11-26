"""NPC-led dispatch and crew allocation for the Saltwater single-player game.

The player selects an incident or gives a dispatch instruction. NPC dispatch
logic selects a suitable available unit and crew; the player never supplies
individual personnel or membership identifiers.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

from runtime.npc_workforce import NPCOfficer


class NPCDispatchError(RuntimeError):
    """A dispatch instruction cannot be completed in the current game state."""


@dataclass(frozen=True, slots=True)
class DispatchIncident:
    incident_id: str
    incident_type: str
    required_domain: str = "general_patrol"
    priority: int = 3
    location_ref: str = "unknown"

    def __post_init__(self) -> None:
        if not self.incident_id.strip() or not self.incident_type.strip():
            raise ValueError("incident identity and type are required")
        if not 1 <= self.priority <= 5:
            raise ValueError("priority must be between 1 and 5")


@dataclass(frozen=True, slots=True)
class NPCDeployment:
    deployment_id: str
    incident_id: str
    unit_id: str
    crew_ids: tuple[str, ...]
    crew_names: tuple[str, ...]
    supervisor_id: str | None
    status: str
    priority: int
    location_ref: str


class NPCDispatchSimulator:
    """Select available NPC units and manage their simple operational lifecycle."""

    _ACTIVE_STATES = frozenset({"responding", "on_scene", "busy", "returning"})

    def __init__(self, officers: Iterable[NPCOfficer], unit_profiles: Iterable[dict], *, current_shift: str = "Alpha"):
        officer_rows = tuple(officers)
        self._officers = {officer.npc_id: officer for officer in officer_rows}
        self._units: dict[str, dict] = {}
        self._officer_state = {
            officer.npc_id: ("available" if officer.shift_group == current_shift else "off_duty")
            for officer in officer_rows
        }
        self._unit_state: dict[str, str] = {}
        self._deployments: dict[str, NPCDeployment] = {}
        self._incident_assignments: dict[str, str] = {}
        self.current_shift = current_shift
        if current_shift not in {"Alpha", "Bravo", "Charlie", "Delta"}:
            raise ValueError("current_shift must be Alpha, Bravo, Charlie or Delta")
        for profile in unit_profiles:
            unit_id = profile.get("unit_id")
            if not isinstance(unit_id, str) or not unit_id.strip() or unit_id in self._units:
                raise ValueError("unit profiles require unique non-empty unit_id values")
            minimum = profile.get("minimum_crew_size", 2)
            if type(minimum) is not int or minimum < 1:
                raise ValueError("minimum_crew_size must be a positive integer")
            target = profile.get("target_crew_size", minimum)
            if type(target) is not int or target < minimum:
                raise ValueError("target_crew_size must be an integer at least minimum_crew_size")
            self._units[unit_id] = {
                "unit_id": unit_id,
                "domain": str(profile.get("functional_domain") or "general_patrol"),
                "capabilities": frozenset(profile.get("capability_codes") or ()),
                "dispatchable": profile.get("dispatchable", True) is True,
                "minimum_crew_size": minimum,
                "target_crew_size": target,
            }
            self._unit_state[unit_id] = str(profile.get("operational_status") or "available")

    def rotate_shift(self) -> str:
        """Move to the next NPC shift group without disturbing deployed crews."""
        shifts = ("Alpha", "Bravo", "Charlie", "Delta")
        self.current_shift = shifts[(shifts.index(self.current_shift) + 1) % len(shifts)]
        for officer in self._officers.values():
            state = self._officer_state[officer.npc_id]
            if state in {"available", "off_duty"}:
                self._officer_state[officer.npc_id] = (
                    "available" if officer.shift_group == self.current_shift else "off_duty"
                )
        return self.current_shift

    def available_units(self) -> list[dict]:
        result = []
        for unit_id, profile in sorted(self._units.items()):
            crew = self._available_crew(unit_id, self.current_shift)
            result.append({
                **profile,
                "operational_status": self._unit_state[unit_id],
                "available_crew": len(crew),
                "minimum_crew_available": len(crew) >= profile["minimum_crew_size"],
            })
        return result

    def assign_best_unit(self, incident: DispatchIncident) -> NPCDeployment:
        if not isinstance(incident, DispatchIncident):
            raise TypeError("incident must be a DispatchIncident")
        if incident.incident_id in self._incident_assignments:
            return self._deployments[self._incident_assignments[incident.incident_id]]
        candidates = []
        for unit_id, profile in self._units.items():
            if not profile["dispatchable"] or self._unit_state[unit_id] != "available":
                continue
            domain = profile["domain"]
            capabilities = profile["capabilities"]
            if domain not in {incident.required_domain, "general_patrol"} and incident.required_domain not in capabilities:
                continue
            crew = self._available_crew(unit_id, self.current_shift)
            if len(crew) < profile["minimum_crew_size"]:
                continue
            match_score = (
                0 if incident.required_domain in capabilities
                else 1 if domain == incident.required_domain
                else 2
            )
            candidates.append((match_score, -len(crew), unit_id, crew))
        if not candidates:
            raise NPCDispatchError(f"No available NPC unit has a crew for {incident.incident_type}.")
        _, _, unit_id, crew = sorted(candidates, key=lambda item: item[:3])[0]
        selected = crew[: self._units[unit_id]["target_crew_size"]]
        supervisor = next(
            (person for person in selected if any(
                word in person.position_title.casefold()
                for word in ("sergeant", "supervisor", "inspector")
            )),
            None,
        )
        deployment_id = f"SWNPC-DEP-{len(self._deployments) + 1:06d}"
        deployment = NPCDeployment(
            deployment_id=deployment_id,
            incident_id=incident.incident_id,
            unit_id=unit_id,
            crew_ids=tuple(person.npc_id for person in selected),
            crew_names=tuple(person.display_name for person in selected),
            supervisor_id=supervisor.npc_id if supervisor else selected[0].npc_id,
            status="responding",
            priority=incident.priority,
            location_ref=incident.location_ref,
        )
        self._deployments[deployment_id] = deployment
        self._incident_assignments[incident.incident_id] = deployment_id
        self._unit_state[unit_id] = "responding"
        for person in selected:
            self._officer_state[person.npc_id] = "responding"
        return deployment

    def transition(self, deployment_id: str, action: str) -> NPCDeployment:
        current = self._deployments.get(deployment_id)
        if current is None:
            raise NPCDispatchError("Unknown NPC deployment.")
        transitions = {
            "responding": {"arrive": "on_scene", "stand_down": "returning"},
            "on_scene": {"begin_work": "busy", "clear_scene": "returning", "stand_down": "returning"},
            "busy": {"finish_work": "on_scene", "stand_down": "returning"},
            "returning": {"available": "available"},
        }
        next_state = transitions.get(current.status, {}).get(action)
        if next_state is None:
            raise NPCDispatchError(f"Cannot {action} a deployment in state {current.status}.")
        updated = NPCDeployment(
            deployment_id=current.deployment_id,
            incident_id=current.incident_id,
            unit_id=current.unit_id,
            crew_ids=current.crew_ids,
            crew_names=current.crew_names,
            supervisor_id=current.supervisor_id,
            status=next_state,
            priority=current.priority,
            location_ref=current.location_ref,
        )
        self._deployments[deployment_id] = updated
        self._unit_state[current.unit_id] = next_state
        for npc_id in current.crew_ids:
            self._officer_state[npc_id] = next_state
        if next_state == "available":
            self._unit_state[current.unit_id] = "available"
            for npc_id in current.crew_ids:
                officer = self._officers[npc_id]
                self._officer_state[npc_id] = (
                    "available" if officer.shift_group == self.current_shift else "off_duty"
                )
        return updated

    def deployment(self, deployment_id: str) -> NPCDeployment | None:
        return self._deployments.get(deployment_id)

    def snapshot(self) -> dict:
        return {
            "current_shift": self.current_shift,
            "units": self.available_units(),
            "deployments": [asdict(item) for item in self._deployments.values()],
            "available_npc_count": sum(state == "available" for state in self._officer_state.values()),
            "assigned_npc_count": sum(state in self._ACTIVE_STATES for state in self._officer_state.values()),
            "off_duty_npc_count": sum(state == "off_duty" for state in self._officer_state.values()),
        }

    def _available_crew(self, unit_id: str, shift: str) -> list[NPCOfficer]:
        crew = [
            officer for officer in self._officers.values()
            if officer.unit_id == unit_id
            and officer.shift_group == shift
            and officer.service_state == "active"
            and self._officer_state[officer.npc_id] == "available"
        ]
        return sorted(
            crew,
            key=lambda person: (
                0 if any(word in person.position_title.casefold()
                         for word in ("sergeant", "supervisor", "inspector")) else 1,
                person.service_number,
            ),
        )
