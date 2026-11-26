"""Player-facing NPC dispatch console; no personnel credentials or IDs required."""
from __future__ import annotations
from typing import Iterable
from runtime.npc_dispatch import DispatchIncident, NPCDispatchSimulator

class NPCDispatchConsole:
    _ACTIONS = {"arrive":"arrive","begin":"begin_work","finish":"finish_work","clear":"clear_scene","stand_down":"stand_down","available":"available"}
    def __init__(self, simulator: NPCDispatchSimulator, incidents: Iterable[DispatchIncident]):
        if not callable(getattr(simulator, "assign_best_unit", None)):
            raise TypeError("simulator must support NPC dispatch")
        self._simulator = simulator
        self._incidents = {}
        for incident in incidents:
            if not isinstance(incident, DispatchIncident):
                raise TypeError("incidents must contain DispatchIncident records")
            if incident.incident_id in self._incidents:
                raise ValueError("incident IDs must be unique")
            self._incidents[incident.incident_id] = incident
    def execute(self, arguments: tuple[str, ...] = ()) -> str:
        if not arguments:
            return self.render()
        action = arguments[0]
        if action == "assign" and len(arguments) == 2:
            incident = self._incidents.get(arguments[1])
            if incident is None:
                raise ValueError(f"Incident {arguments[1]} was not found.")
            deployment = self._simulator.assign_best_unit(incident)
            lead = next((name for name, person_id in zip(deployment.crew_names, deployment.crew_ids) if person_id == deployment.supervisor_id), "NPC crew lead")
            return (f"NPC dispatch assigned {deployment.unit_id} to {deployment.incident_id}.\n"
                    f"Deployment: {deployment.deployment_id}\nCrew: {', '.join(deployment.crew_names)}\n"
                    f"Crew lead: {lead}\nStatus: {deployment.status}")
        if action in self._ACTIONS and len(arguments) == 2:
            deployment = self._simulator.transition(arguments[1], self._ACTIONS[action])
            return f"{deployment.deployment_id} | {deployment.unit_id} | {deployment.status}"
        raise ValueError("Use dispatch, dispatch assign <incident-id>, or dispatch arrive|begin|finish|clear|stand_down|available <deployment-id>.")
    def render(self) -> str:
        snapshot = self._simulator.snapshot()
        lines = ["SALTWATER NPC DISPATCH", f"Shift: {snapshot['current_shift']}",
                 f"NPCs available: {snapshot['available_npc_count']}", f"NPCs deployed: {snapshot['assigned_npc_count']}", "", "INCIDENTS"]
        if not self._incidents:
            lines.append("No incidents waiting for dispatch.")
        for incident in self._incidents.values():
            lines.append(f"{incident.incident_id} | {incident.incident_type} | priority {incident.priority} | {incident.location_ref}")
        lines.extend(("", "UNITS"))
        for unit in snapshot["units"]:
            lines.append(f"{unit['unit_id']} | {unit['operational_status']} | {unit['available_crew']} NPCs available")
        lines.extend(("", "DEPLOYMENTS"))
        if not snapshot["deployments"]:
            lines.append("No active deployments.")
        for deployment in snapshot["deployments"]:
            lines.append(f"{deployment['deployment_id']} | {deployment['unit_id']} | {deployment['incident_id']} | {deployment['status']}")
        lines.extend(("", "Commands: dispatch assign <incident-id>; dispatch arrive|begin|finish|clear|stand_down|available <deployment-id>"))
        return "\n".join(lines)
