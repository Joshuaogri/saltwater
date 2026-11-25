"""Build the canonical property title, transaction and lifecycle register."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_world_generator import to_columnar_document

GENERATOR = "SW-PROPERTY-LIFECYCLE-TRANSACTIONS-001"

def _slug(value):
    return "".join(c for c in str(value).upper() if c.isalnum())[:24]

def build_property_lifecycle(world, tenure, development):
    properties = {x["property_id"]: x for x in world["properties"]}
    buildings = {x["building_id"]: x for x in world["buildings"]}
    premises = {x["premises_id"]: x for x in world["premises"]}
    units = {x["unit_id"]: x for x in world["units"]}
    interests = {x["property_id"]: x for x in tenure["current_ownership_interests"]}
    ownership_events = tenure["ownership_events"]
    events_by_property = {}
    for event in ownership_events:
        events_by_property.setdefault(event["property_id"], []).append(event)
    permissions = {x["building_id"]: x["planning_permission_id"] for x in development["planning_permissions"]}
    completion = {x["building_id"]: x["completion_certificate_id"] for x in development["completion_certificates"]}
    lawful = {x["premises_id"]: x["lawful_use_certificate_id"] for x in development["lawful_use_certificates"]}
    title_register, title_instruments, transactions, lifecycle_events = [], [], [], []
    property_interests, encumbrance_register = [], []
    for pid, prop in sorted(properties.items()):
        interest = interests[pid]
        owner = interest["owner_organisation_id"]
        title_id = f"SWTITLE-{_slug(pid)}"
        title_register.append({
            "title_register_id": title_id, "property_id": pid,
            "current_ownership_interest_id": interest["ownership_interest_id"],
            "registered_proprietor_organisation_id": owner,
            "title_status": "registered_current", "tenure_type": interest.get("interest_type", "freehold_or_canonical_estate"),
            "registration_tick": 0, "source_basis": "canonical_property_world_and_tenure",
            "boundary_record_id": f"SWBOUNDARY-{_slug(pid)}",
            "active_dispute_count": 0, "unresolved_title_issue_count": 0
        })
        property_interests.append({
            "property_interest_record_id": f"SWINT-{_slug(pid)}",
            "property_id": pid, "ownership_interest_id": interest["ownership_interest_id"],
            "interest_holder_organisation_id": owner, "interest_type": interest.get("interest_type", "registered_ownership"),
            "interest_status": "current", "priority_order": 1, "source_basis": "current_ownership_interest"
        })
        lifecycle_events.append({
            "lifecycle_event_id": f"SWPLE-{_slug(pid)}-REG",
            "property_id": pid, "event_type": "canonical_property_registration",
            "effective_year": None, "effective_tick": 0, "event_status": "baseline_state_registration",
            "title_register_id": title_id, "source_record_id": pid,
            "historical_date_known": False, "financial_transaction_created": False,
            "narrative": "Existing canonical property site entered into the unified property register"
        })
        # Ownership changes remain authoritative in the tenure dataset. This table is
        # a transaction index referencing those source events, never a second event log.
        for event in sorted(events_by_property.get(pid, []), key=lambda x: (x.get("effective_year") or 0, x["ownership_event_id"])):
            event_key = hashlib.sha256(event["ownership_event_id"].encode()).hexdigest()[:12]
            instrument_id = f"SWTI-{event_key}"
            title_instruments.append({
                "title_instrument_id": instrument_id, "property_id": pid,
                "title_register_id": title_id, "ownership_event_id": event["ownership_event_id"],
                "instrument_type": event["event_type"], "transferor_organisation_id": event.get("from_organisation_id"),
                "transferee_organisation_id": event.get("to_organisation_id"),
                "effective_year": event.get("effective_year"), "recorded_year": event.get("recorded_year"),
                "instrument_status": "registered_historical" if event.get("is_historical") else "registered_current_chain",
                "source_dataset": "SW-PROPERTY-TENURE-V1", "source_basis": event.get("source_basis"),
                "consideration_recorded_as_band_only": bool(event.get("consideration_band")),
                "payment_or_settlement_record_created": False
            })
            transactions.append({
                "property_transaction_id": f"SWPTX-{event_key}",
                "property_id": pid, "title_register_id": title_id,
                "transaction_type": event["event_type"], "ownership_event_id": event["ownership_event_id"],
                "title_instrument_id": instrument_id,
                "from_organisation_id": event.get("from_organisation_id"),
                "to_organisation_id": event.get("to_organisation_id"),
                "effective_year": event.get("effective_year"), "recorded_year": event.get("recorded_year"),
                "transaction_status": "completed_in_canonical_history",
                "consideration_band": event.get("consideration_band"),
                "financial_settlement_status": "not_modelled_in_this_layer",
                "source_of_truth": "SW-PROPERTY-TENURE-V1"
            })
        encumbrance_register.append({
            "encumbrance_register_id": f"SWENC-{_slug(pid)}", "property_id": pid,
            "title_register_id": title_id, "recorded_encumbrance_count": 0,
            "register_state": "no_encumbrance_record_supplied",
            "mortgage_or_charge_status": "not_asserted", "caveat_or_lien_status": "not_asserted",
            "search_required_before_transaction": True
        })
    building_events = []
    for bid, building in sorted(buildings.items()):
        pid = building["property_id"]
        building_events.append({
            "lifecycle_event_id": f"SWBLE-{_slug(bid)}-BASE",
            "property_id": pid, "building_id": bid,
            "event_type": "existing_building_baseline_registration",
            "effective_year": building.get("construction_year"), "effective_tick": 0,
            "event_status": "existing_asset_baseline",
            "planning_permission_id": permissions.get(bid),
            "completion_certificate_id": completion.get(bid),
            "historical_construction_contract_created": False,
            "financial_transaction_created": False
        })
    premises_events = []
    for prid, item in sorted(premises.items()):
        premises_events.append({
            "lifecycle_event_id": f"SWPRE-LE-{_slug(prid)}",
            "property_id": item["property_id"], "building_id": item["building_id"],
            "premises_id": prid, "event_type": "existing_premises_baseline_registration",
            "effective_tick": 0, "event_status": "existing_asset_baseline",
            "lawful_use_certificate_id": lawful.get(prid)
        })
    # No parcel geometry or asset hierarchy is mutated by proposed future actions.
    action_catalog = [
        ("sale_or_transfer", "ownership_transaction", "title_transfer_registration"),
        ("acquisition", "ownership_transaction", "title_transfer_registration"),
        ("subdivision", "boundary_and_parcel_change", "new_parcel_and_parent_child_lineage_required"),
        ("consolidation", "boundary_and_parcel_change", "merged_parcel_and_predecessor_lineage_required"),
        ("redevelopment", "development_and_construction", "planning_and_building_control_required"),
        ("demolition", "asset_retirement", "demolition_permission_and_clearance_required"),
        ("change_of_use", "lawful_use_change", "planning_permission_and_use_certificate_required"),
        ("easement_or_wayleave", "property_interest_change", "registered_instrument_and_servient_dominant_links_required"),
        ("mortgage_or_charge", "secured_interest", "lender_instrument_and_discharge_lifecycle_required"),
        ("lease_or_concession_change", "occupancy_transaction", "agreement_and_unit_occupancy_lineage_required")
    ]
    action_rules = [{
        "lifecycle_action_type": a, "action_domain": d, "mandatory_linkage": r,
        "runtime_creation_policy": "create_only_when_player_or_npc_gameplay_event_occurs",
        "mutates_canonical_baseline": False
    } for a, d, r in action_catalog]
    summary = {
        "property_count": len(properties), "title_register_count": len(title_register),
        "property_interest_count": len(property_interests), "title_instrument_count": len(title_instruments),
        "property_transaction_count": len(transactions), "ownership_source_event_count": len(ownership_events),
        "property_registration_lifecycle_event_count": len(lifecycle_events),
        "building_baseline_lifecycle_event_count": len(building_events),
        "premises_baseline_lifecycle_event_count": len(premises_events),
        "encumbrance_register_count": len(encumbrance_register),
        "recorded_encumbrance_count": 0, "boundary_change_count": 0,
        "subdivision_count": 0, "consolidation_count": 0, "redevelopment_started_count": 0,
        "demolition_completed_count": 0, "change_of_use_completed_count": 0,
        "future_action_type_count": len(action_rules),
        "financial_postings_created": 0, "payments_created": 0,
        "person_records_created": 0, "population_records_created": 0
    }
    body = {
        "schema": "saltwater-property-lifecycle-transactions/1.0",
        "dataset_id": "SW-PROPERTY-LIFECYCLE-TRANSACTIONS-V1",
        "canon_status": "CANONICAL_FICTIONAL_GAME_WORLD",
        "generator": GENERATOR, "effective_tick": 0, "city": "Saltwater",
        "summary": summary, "title_register": title_register,
        "property_interests": property_interests, "title_instruments": title_instruments,
        "property_transactions": transactions, "property_lifecycle_events": lifecycle_events,
        "building_lifecycle_events": building_events, "premises_lifecycle_events": premises_events,
        "encumbrance_register": encumbrance_register, "future_lifecycle_action_rules": action_rules,
        "lineage": {
            "property_world": "SW-PROPERTY-WORLD-V1",
            "property_tenure": "SW-PROPERTY-TENURE-V1",
            "development_control": "SW-PROPERTY-DEVELOPMENT-CONTROL-V1"
        },
        "gameplay": {
            "ownership_history": "SW-PROPERTY-TENURE-V1 remains the sole source of ownership event facts; this dataset provides title instruments and transaction indexes keyed to source event IDs.",
            "unknowns": "No mortgage, lien, easement, boundary dispute or encumbrance is presumed absent; no source record was supplied, so status remains not asserted.",
            "physical_changes": "Subdivision, consolidation, redevelopment, demolition and change-of-use actions are available as runtime action types but do not alter the baseline until a gameplay event is executed and all dependent records are updated.",
            "finance": "Consideration bands are descriptive only. No prices, invoices, tax postings, receipts, payments, loans or settlement events are generated.",
            "population": "No person, resident, employee, tenant-as-person or population records are created."
        }
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body

def main():
    root = Path(__file__).resolve().parents[1]
    def load(path):
        return _expand_columnar(json.loads((root / path).read_text(encoding="utf-8")))
    data = build_property_lifecycle(
        load("data/property/saltwater-property-world-v1.json"),
        load("data/property/saltwater-property-tenure-v1.json"),
        load("data/property/saltwater-property-development-control-v1.json")
    )
    output = root / "data/property/saltwater-property-lifecycle-transactions-v1.json"
    doc = to_columnar_document(data)
    doc["schema"] = "saltwater-property-lifecycle-transactions-columnar/1.0"
    output.write_text(json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(data["summary"] | {"manifest_sha256": data["manifest_sha256"], "output_bytes": output.stat().st_size}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
