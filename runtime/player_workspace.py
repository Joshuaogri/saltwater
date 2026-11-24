"""Stable text-first player workspace catalogue and navigation state."""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Workspace:
    id: str
    label: str
    availability: str

WORKSPACES = (
    Workspace("home", "Home / Shift Desk", "available"),
    Workspace("operations", "Operations", "navigation_only"),
    Workspace("cases", "Cases", "navigation_only"),
    Workspace("people", "People", "navigation_only"),
    Workspace("evidence-scenes", "Evidence / Scenes", "navigation_only"),
    Workspace("department", "Department", "navigation_only"),
    Workspace("legal-custody", "Legal / Custody", "navigation_only"),
    Workspace("resources-finance", "Resources / Finance", "navigation_only"),
    Workspace("reports-notifications", "Reports / Notifications", "navigation_only"),
    Workspace("system-status", "System Status", "available"),
)
WORKSPACE_BY_ID = {item.id: item for item in WORKSPACES}
MAX_HISTORY = 16

@dataclass(frozen=True, slots=True)
class WorkspaceNavigation:
    current: str = "home"
    history: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.current not in WORKSPACE_BY_ID:
            raise ValueError("unknown workspace")
        if len(self.history) > MAX_HISTORY or any(x not in WORKSPACE_BY_ID for x in self.history):
            raise ValueError("invalid workspace history")

    def select(self, workspace_id: str) -> "WorkspaceNavigation":
        if not isinstance(workspace_id, str) or workspace_id not in WORKSPACE_BY_ID:
            raise ValueError("unknown workspace identifier")
        if workspace_id == self.current:
            return self
        history = (self.history + (self.current,))[-MAX_HISTORY:]
        return WorkspaceNavigation(workspace_id, history)

    def back(self) -> "WorkspaceNavigation":
        if not self.history:
            return self
        return WorkspaceNavigation(self.history[-1], self.history[:-1])

def render_workspace_catalogue(current: str) -> str:
    if current not in WORKSPACE_BY_ID:
        raise ValueError("unknown workspace")
    lines = ["WORKSPACES"]
    for item in WORKSPACES:
        marker = ">" if item.id == current else " "
        availability = "READY" if item.availability == "available" else "NOT CONNECTED"
        lines.append(f"{marker} {item.id:<24} {item.label} [{availability}]")
    return "\n".join(lines)

def render_home(profile, status, navigation: WorkspaceNavigation) -> str:
    current = WORKSPACE_BY_ID[navigation.current]
    return "\n".join((
        "SALTWATER — PLAYER WORKSPACE",
        f"Player: {profile.display_name}",
        f"Player ID: {profile.player_id}",
        f"Career: {profile.career_stage}",
        f"Runtime: {status.lifecycle.value.upper()}",
        f"Player present: {'yes' if status.player_present else 'no'}",
        f"World tick: {status.world_tick}",
        f"Current workspace: {current.label} ({current.id})",
        f"Workspace capability: {'available' if current.availability == 'available' else 'navigation only — domain service not connected'}",
        "",
        render_workspace_catalogue(navigation.current),
        "",
        "Commands: home | workspaces | workspace <id> | back | where",
        "Navigation is read-only. No simulation time advances from this screen.",
    ))
