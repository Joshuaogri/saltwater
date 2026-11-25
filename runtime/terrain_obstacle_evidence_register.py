"""Append-only evidence intake and assessment history for BP04-03.

This module validates submitted evidence; it does not manufacture observations,
approve physical features, or promote planning geometry into operational facts.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GENERATOR = "BP04-03-TERRAIN-OBSTACLE-EVIDENCE-REGISTER-V1"
REGISTER_ID = "SW-TERRAIN-EVIDENCE-REGISTER-001"
EVIDENCE_TYPES = {
    "field_observation", "instrument_measurement", "survey_plan", "survey_result",
    "photograph", "video", "document", "third_party_dataset", "inspection_record",
    "maintenance_record", "simulation_observation",
}
SUBJECT_TYPES = {
    "terrain_feature", "elevation_surface", "contour_line", "spot_elevation",
    "retaining_structure", "wall", "fence", "gate", "drainage_structure",
    "natural_barrier", "other_physical_obstacle", "route_corridor_candidate",
    "building_access_connector_candidate", "survey_cell",
}
REVIEW_ACTIONS = {"SUBMITTED", "NEEDS_CLARIFICATION", "ACCEPTED", "REJECTED", "SUPERSEDED"}
MEASUREMENT_KEYS = {
    "elevation_m", "gradient_degrees", "slope_direction_degrees", "height_m",
    "width_m", "depth_m", "surface_material", "condition", "continuity",
    "permeability", "traversal_restriction", "pedestrian_passability",
    "vehicle_passability", "accessibility", "legal_access", "emergency_egress",
}
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


def _iso(value: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _nonblank(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def build_evidence_register(
    source_inventory: dict,
    submissions: list[dict] | None = None,
    review_events: list[dict] | None = None,
    source_bytes: bytes | None = None,
) -> dict:
    """Validate evidence submissions and append-only review events."""
    submissions = submissions or []
    review_events = review_events or []
    source_id = _nonblank(source_inventory.get("source_dataset_id"), "source_dataset_id")
    known_subjects = {
        row["source_feature_id"]: row["source_entity_type"]
        for row in source_inventory.get("records", [])
    }
    evidence_ids: set[str] = set()
    records: list[dict] = []

    for item in submissions:
        evidence_id = _nonblank(item.get("evidence_id"), "evidence_id")
        if evidence_id in evidence_ids:
            raise ValueError(f"Duplicate evidence_id: {evidence_id}")
        evidence_ids.add(evidence_id)
        subject_id = _nonblank(item.get("subject_id"), "subject_id")
        subject_type = _nonblank(item.get("subject_type"), "subject_type")
        if subject_type not in SUBJECT_TYPES:
            raise ValueError(f"Unsupported subject_type: {subject_type}")
        if subject_type in {"terrain_feature", "elevation_surface", "contour_line", "spot_elevation",
                            "retaining_structure", "wall", "fence", "gate", "drainage_structure",
                            "natural_barrier", "other_physical_obstacle"}:
            if subject_id not in known_subjects:
                raise ValueError(f"Unknown source subject: {subject_id}")
            if known_subjects[subject_id] != subject_type:
                raise ValueError(f"Subject type does not match source feature: {subject_id}")
        evidence_type = _nonblank(item.get("evidence_type"), "evidence_type")
        if evidence_type not in EVIDENCE_TYPES:
            raise ValueError(f"Unsupported evidence_type: {evidence_type}")
        captured_at = _iso(item.get("captured_at"), "captured_at")
        submitted_at = _iso(item.get("submitted_at"), "submitted_at")
        actor_ref = _nonblank(item.get("actor_ref"), "actor_ref")
        source_ref = _nonblank(item.get("source_ref"), "source_ref")
        source_sha256 = _nonblank(item.get("source_sha256"), "source_sha256").lower()
        if not HASH_RE.fullmatch(source_sha256):
            raise ValueError("source_sha256 must be a 64-character SHA-256 digest")
        method = _nonblank(item.get("collection_method"), "collection_method")
        measurements = item.get("measurements") or {}
        if not isinstance(measurements, dict):
            raise ValueError("measurements must be an object")
        unknown = set(measurements) - MEASUREMENT_KEYS
        if unknown:
            raise ValueError("Unsupported measurement keys: " + ", ".join(sorted(unknown)))
        uncertainty = item.get("uncertainty") or {}
        if not isinstance(uncertainty, dict):
            raise ValueError("uncertainty must be an object")
        attachment_hashes = item.get("attachment_sha256") or []
        if not isinstance(attachment_hashes, list) or any(
            not isinstance(x, str) or not HASH_RE.fullmatch(x.lower()) for x in attachment_hashes
        ):
            raise ValueError("Every attachment_sha256 must be a SHA-256 digest")
        valid_from = _iso(item["valid_from"], "valid_from") if item.get("valid_from") else None
        valid_to = _iso(item["valid_to"], "valid_to") if item.get("valid_to") else None
        if valid_from and valid_to and valid_to < valid_from:
            raise ValueError("valid_to cannot precede valid_from")
        records.append({
            "evidence_id": evidence_id,
            "subject_id": subject_id,
            "subject_type": subject_type,
            "evidence_type": evidence_type,
            "captured_at": captured_at,
            "submitted_at": submitted_at,
            "actor_ref": actor_ref,
            "source_ref": source_ref,
            "source_sha256": source_sha256,
            "collection_method": method,
            "instrument_ref": item.get("instrument_ref"),
            "instrument_calibration_ref": item.get("instrument_calibration_ref"),
            "coordinate_reference": item.get("coordinate_reference"),
            "observation_geometry": item.get("observation_geometry"),
            "measurements": measurements,
            "uncertainty": uncertainty,
            "attachment_sha256": sorted(x.lower() for x in attachment_hashes),
            "chain_of_custody_ref": item.get("chain_of_custody_ref"),
            "valid_from": valid_from,
            "valid_to": valid_to,
            "supersedes_evidence_id": item.get("supersedes_evidence_id"),
            "initial_review_state": "SUBMITTED",
            "operational_effect": "NONE_PENDING_REVIEW",
        })

    event_ids: set[str] = set()
    events: list[dict] = []
    by_evidence: dict[str, list[dict]] = {key: [] for key in evidence_ids}
    for event in review_events:
        event_id = _nonblank(event.get("review_event_id"), "review_event_id")
        if event_id in event_ids:
            raise ValueError(f"Duplicate review_event_id: {event_id}")
        event_ids.add(event_id)
        evidence_id = _nonblank(event.get("evidence_id"), "evidence_id")
        if evidence_id not in by_evidence:
            raise ValueError(f"Review event references unknown evidence: {evidence_id}")
        action = _nonblank(event.get("action"), "action")
        if action not in REVIEW_ACTIONS:
            raise ValueError(f"Unsupported review action: {action}")
        actor = _nonblank(event.get("reviewer_ref"), "reviewer_ref")
        occurred_at = _iso(event.get("occurred_at"), "occurred_at")
        rationale = _nonblank(event.get("rationale"), "rationale")
        if action in {"ACCEPTED", "REJECTED", "SUPERSEDED"} and not event.get("review_basis_ref"):
            raise ValueError(f"{action} requires review_basis_ref")
        normalized = {
            "review_event_id": event_id, "evidence_id": evidence_id, "action": action,
            "occurred_at": occurred_at, "reviewer_ref": actor, "rationale": rationale,
            "review_basis_ref": event.get("review_basis_ref"),
            "superseding_evidence_id": event.get("superseding_evidence_id"),
        }
        events.append(normalized)
        by_evidence[evidence_id].append(normalized)

    state_by_id = {}
    for evidence in records:
        history = sorted(by_evidence[evidence["evidence_id"]], key=lambda e: (e["occurred_at"], e["review_event_id"]))
        state = "SUBMITTED"
        for event in history:
            if state in {"ACCEPTED", "REJECTED", "SUPERSEDED"}:
                raise ValueError("Terminal review state cannot be changed; submit a new evidence record")
            state = event["action"]
        state_by_id[evidence["evidence_id"]] = state
        evidence["review_history"] = history
        evidence["review_state"] = state
        evidence["operational_effect"] = "EVIDENCE_ACCEPTED_NOT_AUTOMATICALLY_ACTIVATED" if state == "ACCEPTED" else "NONE_PENDING_REVIEW"

    raw = source_bytes if source_bytes is not None else json.dumps(source_inventory, sort_keys=True, separators=(",", ":")).encode()
    checks = {
        "evidence_ids_unique": len(evidence_ids) == len(records),
        "all_evidence_has_source_and_actor_lineage": all(r["source_ref"] and r["actor_ref"] for r in records),
        "all_evidence_has_valid_hashes": all(HASH_RE.fullmatch(r["source_sha256"]) for r in records),
        "all_review_events_reference_submissions": all(e["evidence_id"] in evidence_ids for e in events),
        "review_history_is_append_only_and_terminal_states_are_final": True,
        "accepted_evidence_is_not_auto_activated": all(r["operational_effect"] == "EVIDENCE_ACCEPTED_NOT_AUTOMATICALLY_ACTIVATED" for r in records if r["review_state"] == "ACCEPTED"),
        "no_operational_state_or_database_write": True,
    }
    counts = {state: sum(r["review_state"] == state for r in records) for state in ("SUBMITTED", "NEEDS_CLARIFICATION", "ACCEPTED", "REJECTED", "SUPERSEDED")}
    return {
        "schema": "saltwater-bp04-03-terrain-obstacle-evidence-register/1.0",
        "register_id": REGISTER_ID, "generator": GENERATOR,
        "source_dataset_id": source_id, "source_inventory_sha256": hashlib.sha256(raw).hexdigest(),
        "evidence_records": sorted(records, key=lambda r: r["evidence_id"]),
        "review_events": sorted(events, key=lambda e: (e["occurred_at"], e["review_event_id"])),
        "summary": {
            "evidence_record_count": len(records), "review_event_count": len(events),
            "review_state_counts": counts,
            "measurement_assertion_count": sum(len(r["measurements"]) for r in records),
            "records_with_instrument_reference": sum(bool(r["instrument_ref"]) for r in records),
            "records_with_calibration_reference": sum(bool(r["instrument_calibration_ref"]) for r in records),
            "records_with_attachment_hashes": sum(bool(r["attachment_sha256"]) for r in records),
            "accepted_evidence_count": counts["ACCEPTED"],
            "operational_facts_activated": 0,
        },
        "checks": checks, "passed_checks": sum(checks.values()),
        "failed_checks": [key for key, value in checks.items() if not value],
        "operational_seed_eligible": False, "database_write_performed": False,
        "limitations": [
            "Submission records preserve claims and provenance; they are not proof that a measurement is correct.",
            "Acceptance validates evidence for review purposes only and never activates an operational fact.",
            "No source record is not proof that a physical feature is absent.",
            "Survey-cell and route-corridor references are planning geometry, not confirmed physical access.",
            "Every change is represented by a new evidence or review event; prior records are not overwritten.",
        ],
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source_path = root / "data/geography/saltwater-geography-v1.json"
    source_raw = source_path.read_bytes()
    from runtime.terrain_obstacle_source_model import build_source_inventory
    inventory = build_source_inventory(json.loads(source_raw), source_raw)
    report = build_evidence_register(inventory, source_bytes=source_raw)
    output = root / "bp04-03-terrain-obstacle-evidence-register.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "summary": report["summary"], "checks": report["checks"],
        "failed_checks": report["failed_checks"], "output": output.name,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
