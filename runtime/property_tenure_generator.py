"""Generate ownership, landlord, lease and occupancy histories for Saltwater.

All generated records are fictional canon. The generator references canonical
property/business IDs and creates no person records or population changes.
"""
from __future__ import annotations

import hashlib
import json
from runtime.dataset_io import load_json
from pathlib import Path

from runtime.property_world_generator import build_property_world, to_columnar_document

GENERATOR = "SW-PROPERTY-TENURE-GENERATOR-001"


def _number(key: str, low: int, high: int) -> int:
    digest = hashlib.sha256(key.encode()).digest()
    return low + int.from_bytes(digest[:4], "big") % (high - low + 1)


def _pick(values, key: str):
    return values[_number(key, 0, len(values) - 1)]


def _slug(value: str) -> str:
    return "".join(c for c in value.upper() if c.isalnum())[:24]


def _manager_model(model: str, property_id: str):
    if model == "direct_owner_management":
        return None
    return {
        "organisation_id": f"SWORG-MGR-{_slug(property_id)}",
        "display_name": f"{_pick(['Meridian','Harbour','Civic','Northbank','Quayside','Crown'], property_id+'-mgr-name')} Property Management {_number(property_id+'-mgr-suffix', 1, 99):02d}",
        "organisation_type": "property_management_company",
        "registered_city": "Saltwater",
        "status": "active",
        "fictional_entity": True,
    }


def _expand_columnar(document: dict) -> dict:
    expanded = dict(document.get('metadata', {}))
    for name, table in document.get('tables', {}).items():
        columns = table['columns']
        expanded[name] = [dict(zip(columns, row)) for row in table['rows']]
    return expanded


def build_property_tenure(source: dict, property_world: dict | None = None, registry: dict | None = None) -> dict:
    world = property_world or build_property_world(source)
    if registry is None:
        from runtime.business_registry_generator import build_business_registry
        registry = build_business_registry(source, property_world=world)
    properties = {x["property_id"]: x for x in world["properties"]}
    owners = {x["organisation_id"]: x for x in world["owner_organisations"]}
    current_interests = {x["property_id"]: x for x in world["ownership_interests"]}
    buildings = {x["building_id"]: x for x in world["buildings"]}
    premises = {x["premises_id"]: x for x in world["premises"]}
    units = {x["unit_id"]: x for x in world["units"]}
    businesses = {x["business_id"]: x for x in registry["businesses"]}
    establishments = {x["establishment_id"]: x for x in registry["establishments"]}

    ownership_events, historical_owners = [], []
    management_appointments, managers = [], []
    manager_by_property = {}
    for property_id in sorted(properties):
        interest = current_interests[property_id]
        current_owner_id = interest["owner_organisation_id"]
        current_year = _number(property_id + "-owner-current-year", 2012, 2026)
        has_prior_transfer = _number(property_id + "-prior-transfer", 1, 100) <= 28
        if has_prior_transfer:
            prior_id = f"SWORG-HOWN-{_slug(property_id)}"
            prior = {
                "organisation_id": prior_id,
                "display_name": f"{_pick(['Atlantic','Crown','Meridian','Harbour','Civic','Westgate'], property_id+'-prior-name')} Estates {_number(property_id+'-prior-number', 1, 999):03d}",
                "organisation_type": "historical_property_holding_organisation",
                "registered_city": "Saltwater",
                "status": "historical",
                "fictional_entity": True,
            }
            historical_owners.append(prior)
            owners[prior_id] = prior
            first_year = max(1980, current_year - _number(property_id + "-prior-duration", 4, 22))
            ownership_events.append({
                "ownership_event_id": f"SWOEV-{_slug(property_id)}-01",
                "property_id": property_id,
                "ownership_interest_id": interest["ownership_interest_id"],
                "event_type": "initial_acquisition",
                "from_organisation_id": None,
                "to_organisation_id": prior_id,
                "effective_year": first_year,
                "recorded_year": first_year,
                "consideration_band": _pick(["nominal","standard","premium","institutional"], property_id+"-consideration-1"),
                "source_basis": "fictional_canonical_world_history",
                "is_historical": True,
            })
            ownership_events.append({
                "ownership_event_id": f"SWOEV-{_slug(property_id)}-02",
                "property_id": property_id,
                "ownership_interest_id": interest["ownership_interest_id"],
                "event_type": _pick(["sale_transfer","group_reorganisation","estate_transfer","institutional_acquisition"], property_id+"-transfer-type"),
                "from_organisation_id": prior_id,
                "to_organisation_id": current_owner_id,
                "effective_year": current_year,
                "recorded_year": current_year,
                "consideration_band": _pick(["standard","premium","strategic","intra_group"], property_id+"-consideration-2"),
                "source_basis": "fictional_canonical_world_history",
                "is_historical": False,
            })
        else:
            ownership_events.append({
                "ownership_event_id": f"SWOEV-{_slug(property_id)}-01",
                "property_id": property_id,
                "ownership_interest_id": interest["ownership_interest_id"],
                "event_type": "initial_acquisition",
                "from_organisation_id": None,
                "to_organisation_id": current_owner_id,
                "effective_year": current_year,
                "recorded_year": current_year,
                "consideration_band": _pick(["nominal","standard","premium","institutional"], property_id+"-consideration"),
                "source_basis": "fictional_canonical_world_history",
                "is_historical": False,
            })

        manager = _manager_model(interest["management_model"], property_id)
        if manager:
            managers.append(manager)
            manager_by_property[property_id] = manager["organisation_id"]
        else:
            manager_by_property[property_id] = current_owner_id
        management_appointments.append({
            "management_appointment_id": f"SWMGT-{_slug(property_id)}",
            "property_id": property_id,
            "manager_organisation_id": manager_by_property[property_id],
            "appointing_organisation_id": current_owner_id,
            "management_model": interest["management_model"],
            "effective_from_year": _number(property_id+"-management-year", 2015, 2026),
            "effective_to_year": None,
            "appointment_status": "current",
            "responsibility_profile": _pick(["full_estate_management","facilities_and_repairs","tenant_and_common_area_management","site_operations"], property_id+"-responsibility"),
        })

    business_by_unit = {}
    for link in registry["business_unit_links"]:
        if link["unit_id"] in business_by_unit:
            raise ValueError(f"Multiple primary business occupancies for unit {link['unit_id']}")
        business_by_unit[link["unit_id"]] = link

    agreements, occupancies, unit_states = [], [], []
    agreement_by_business = {}
    for sequence, business_id in enumerate(sorted(businesses), 1):
        business = businesses[business_id]
        establishment = establishments[business["primary_establishment_id"]]
        unit_id = establishment["unit_id"]
        unit = units[unit_id]
        property_id = unit["property_id"]
        interest = current_interests[property_id]
        start_year = _number(business_id+"-lease-start", 2016, 2026)
        agreement_id = f"SWAGR-{sequence:06d}"
        agreement_by_business[business_id] = agreement_id
        sector = business["sector"]
        agreement_type = {
            "transport_logistics": "logistics_operating_lease",
            "maritime_trade": "port_or_maritime_concession",
            "finance_insurance": "commercial_office_lease",
            "manufacturing": "industrial_lease",
            "food_hospitality": "commercial_trading_lease",
            "creative_entertainment": "venue_or_studio_lease",
        }.get(sector, "commercial_occupancy_lease")
        agreements.append({
            "agreement_id": agreement_id,
            "agreement_type": agreement_type,
            "property_id": property_id,
            "building_id": unit["building_id"],
            "premises_id": unit["premises_id"],
            "unit_id": unit_id,
            "landlord_organisation_id": interest["owner_organisation_id"],
            "tenant_business_id": business_id,
            "operator_business_id": business_id,
            "establishment_id": establishment["establishment_id"],
            "managing_organisation_id": manager_by_property[property_id],
            "commencement_year": start_year,
            "expiry_year": None,
            "renewal_option": _pick(["none","one_option","rolling_renewal","multiple_options"], business_id+"-renewal"),
            "rent_band": _pick(["B1","B2","B3","B4","B5","B6"], business_id+"-rent"),
            "payment_frequency": _pick(["monthly","quarterly"], business_id+"-frequency"),
            "deposit_profile": _pick(["none","one_period","two_periods","institutional_guarantee"], business_id+"-deposit"),
            "repair_responsibility": _pick(["landlord_structure_tenant_internal","tenant_full_internal","shared_schedule","landlord_full_service"], business_id+"-repair"),
            "permitted_use": business["primary_activity"],
            "agreement_status": "active" if business["status"] == "active" else business["status"],
            "source_basis": "fictional_canonical_world_history",
            "population_records_created": 0,
        })
        if sequence % 4 == 0:
            prior_start = max(1990, start_year - _number(business_id+"-prior-term", 2, 8))
            agreements.append({
                "agreement_id": f"SWAGR-H{sequence:05d}",
                "agreement_type": agreement_type,
                "property_id": property_id,
                "building_id": unit["building_id"],
                "premises_id": unit["premises_id"],
                "unit_id": unit_id,
                "landlord_organisation_id": interest["owner_organisation_id"],
                "tenant_business_id": business_id,
                "operator_business_id": business_id,
                "establishment_id": establishment["establishment_id"],
                "managing_organisation_id": manager_by_property[property_id],
                "commencement_year": prior_start,
                "expiry_year": start_year - 1,
                "renewal_option": "expired",
                "rent_band": _pick(["B1","B2","B3","B4"], business_id+"-prior-rent"),
                "payment_frequency": "monthly",
                "deposit_profile": "one_period",
                "repair_responsibility": "shared_schedule",
                "permitted_use": business["primary_activity"],
                "agreement_status": "expired_historical",
                "source_basis": "fictional_canonical_world_history",
                "population_records_created": 0,
            })
        occupancy_status = {
            "active": "occupied",
            "seasonal": "seasonal_occupation",
            "temporarily_inactive": "temporarily_suspended_occupation",
        }[business["status"]]
        occupancies.append({
            "occupancy_id": f"SWOCC-{sequence:06d}",
            "property_id": property_id,
            "building_id": unit["building_id"],
            "premises_id": unit["premises_id"],
            "unit_id": unit_id,
            "occupant_type": "business",
            "occupant_business_id": business_id,
            "establishment_id": establishment["establishment_id"],
            "agreement_id": agreement_id,
            "occupancy_status": occupancy_status,
            "effective_from_year": start_year,
            "effective_to_year": None,
            "population_person_ids": [],
            "source_basis": "business_registry_and_fictional_tenure_generator",
        })

    for unit_id, unit in units.items():
        link = business_by_unit.get(unit_id)
        if link:
            business = businesses[link["business_id"]]
            state = {
                "active": "business_occupied",
                "seasonal": "seasonal_business_occupied",
                "temporarily_inactive": "business_occupied_temporarily_inactive",
            }[business["status"]]
            business_id = link["business_id"]
        elif unit["unit_class"] == "dwelling":
            state, business_id = "residential_allocation_unassigned", None
        else:
            state = _pick(["available_to_let","owner_or_manager_use","vacant_commercial_space"], unit_id+"-vacancy")
            business_id = None
        unit_states.append({
            "unit_occupancy_state_id": f"SWUOS-{_slug(unit_id)}",
            "property_id": unit["property_id"],
            "building_id": unit["building_id"],
            "premises_id": unit["premises_id"],
            "unit_id": unit_id,
            "occupancy_state": state,
            "occupant_business_id": business_id,
            "effective_from_tick": 0,
            "effective_to_tick": None,
            "person_ids": [],
        })

    all_organisations = list(owners.values()) + managers
    body = {
        "schema": "saltwater-property-tenure/1.0",
        "dataset_id": "SW-PROPERTY-TENURE-V1",
        "canon_status": "CANONICAL_FICTIONAL_GAME_WORLD",
        "generator": GENERATOR,
        "effective_tick": 0,
        "city": "Saltwater",
        "city_population_hard_cap": 10000,
        "summary": {
            "property_count": len(properties),
            "current_ownership_interest_count": len(current_interests),
            "ownership_event_count": len(ownership_events),
            "historical_owner_organisation_count": len(historical_owners),
            "property_management_appointment_count": len(management_appointments),
            "property_manager_organisation_count": len(managers),
            "current_lease_or_concession_count": len(businesses),
            "historical_expired_agreement_count": len(agreements) - len(businesses),
            "current_business_occupancy_count": len(occupancies),
            "unit_occupancy_state_count": len(unit_states),
            "business_occupancy_count": len(business_by_unit),
            "person_records_created": 0,
            "population_records_created": 0,
        },
        "organisations": all_organisations,
        "current_ownership_interests": list(current_interests.values()),
        "ownership_events": ownership_events,
        "management_appointments": management_appointments,
        "agreements": agreements,
        "occupancies": occupancies,
        "unit_occupancy_states": unit_states,
        "lineage": {
            "property_world_dataset": "SW-PROPERTY-WORLD-V1",
            "business_registry_dataset": "SW-BUSINESS-REGISTRY-V1",
            "ownership_interests_source": "canonical_property_world.ownership_interests",
            "fictional_world_facts": True,
        },
        "gameplay": {
            "ownership": "Chronological acquisition and transfer events resolve to the current property ownership interest.",
            "tenancy": "Each registered business establishment has a current lease, licence or operating concession linked to its unit and landlord.",
            "occupancy": "Business occupancy is explicit; residential units remain unallocated until the separate population-allocation process.",
            "population": "No person records, residents, tenants-as-persons, employees or police personnel are created.",
            "finance_boundary": "Rent bands and contract terms are references only; rent postings, balances and accounting remain BP-34.",
            "time": "Historical years describe fictional backstory; current agreement and occupancy states begin at simulation tick zero.",
        },
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body


def main():
    root = Path(__file__).resolve().parents[1]
    world_doc = load_json(root / "data/property/saltwater-property-world-v1.json")
    registry_doc = json.loads((root / "data/business/saltwater-business-registry-v1.json").read_text(encoding="utf-8"))
    result = build_property_tenure({}, property_world=_expand_columnar(world_doc), registry=_expand_columnar(registry_doc))
    output = root / "data/property/saltwater-property-tenure-v1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    document = to_columnar_document(result)
    document["schema"] = "saltwater-property-tenure-columnar/1.0"
    output.write_text(json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"] | {
        "manifest_sha256": result["manifest_sha256"],
        "storage_format": document["storage_format"],
        "output_bytes": output.stat().st_size,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
