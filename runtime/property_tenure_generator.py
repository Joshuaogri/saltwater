"""Generate ownership, landlord, lease and occupancy histories for Saltwater.

All generated records are fictional canon. The generator references canonical
property/business IDs and creates no person records or population changes.
"""
from __future__ import annotations

import hashlib
import json
import uuid
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
    letting_authorities, letting_authority_events = [], []
    head_lessee_organisations, head_lessee_by_property = [], {}
    agreement_by_business = {}
    business_ids = sorted(businesses)
    business_position = {business_id: index for index, business_id in enumerate(business_ids)}
    # Ensure every generated property/unit class has at least one independent
    # tenant/operator arrangement; add a deterministic wider mix as well.
    first_tenant_by_unit_class = {}
    for candidate_id in business_ids:
        candidate_establishment = establishments[businesses[candidate_id]["primary_establishment_id"]]
        candidate_unit_class = units[candidate_establishment["unit_id"]]["unit_class"]
        first_tenant_by_unit_class.setdefault(candidate_unit_class, candidate_id)
    independent_operator_tenants = set(first_tenant_by_unit_class.values())
    # Guarantee an independent head-lessee landlord in every generated unit
    # class wherever the title chronology permits a current head lease.
    eligible_landlord_by_unit_class = {}
    for candidate_id in business_ids:
        candidate_establishment = establishments[businesses[candidate_id]["primary_establishment_id"]]
        candidate_unit = units[candidate_establishment["unit_id"]]
        candidate_property_id = candidate_unit["property_id"]
        candidate_start = _number(candidate_id+"-lease-start", 2016, 2026)
        candidate_owner_year = _number(candidate_property_id + "-owner-current-year", 2012, 2026)
        if candidate_start >= candidate_owner_year:
            eligible_landlord_by_unit_class.setdefault(candidate_unit["unit_class"], candidate_id)
    independent_landlord_tenants = set(eligible_landlord_by_unit_class.values())
    for sequence, business_id in enumerate(business_ids, 1):
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
        operator_business_id = business_id
        if business_id in independent_operator_tenants or _number(business_id + "-independent-operator", 1, 4) == 1:
            operator_offset = 1 + _number(business_id + "-operator-partner", 0, len(business_ids) - 2)
            operator_business_id = business_ids[(business_position[business_id] + operator_offset) % len(business_ids)]
        agreement_type = {
            "transport_logistics": "logistics_operating_lease",
            "maritime_trade": "port_or_maritime_concession",
            "finance_insurance": "commercial_office_lease",
            "manufacturing": "industrial_lease",
            "food_hospitality": "commercial_trading_lease",
            "creative_entertainment": "venue_or_studio_lease",
        }.get(sector, "commercial_occupancy_lease")
        current_owner_year = _number(property_id + "-owner-current-year", 2012, 2026)
        use_head_lease = (
            start_year >= current_owner_year
            and (
                business_id in independent_landlord_tenants
                or _number(property_id + "-independent-landlord", 1, 5) == 1
            )
        )
        if use_head_lease:
            head_lessee_id = head_lessee_by_property.get(property_id)
            if head_lessee_id is None:
                head_lessee_id = f"SWORG-HL-{_slug(property_id)}"
                head_lessee_by_property[property_id] = head_lessee_id
                head_lessee_organisations.append({
                    "organisation_id": head_lessee_id,
                    "display_name": f"{_pick(['Atlantic','Meridian','Crown','Harbour','Westgate','Northbank'], property_id+'-head-lessee-name')} Head Lease Holdings {_number(property_id+'-head-lessee-suffix', 1, 99):02d}",
                    "organisation_type": "head_lessee_property_operator",
                    "registered_city": "Saltwater",
                    "status": "active",
                    "fictional_entity": True,
                })
            landlord_id = head_lessee_id
        else:
            landlord_id = interest["owner_organisation_id"]
        agreements.append({
            "agreement_id": agreement_id,
            "agreement_type": agreement_type,
            "property_id": property_id,
            "building_id": unit["building_id"],
            "premises_id": unit["premises_id"],
            "unit_id": unit_id,
            "landlord_organisation_id": landlord_id,
            "letting_authority_id": f"SWLA-{_slug(property_id)}" if use_head_lease else None,
            "tenant_business_id": business_id,
            "operator_business_id": operator_business_id,
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
                "letting_authority_id": None,
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


    # Append-only generated agreement history. Execution dates remain unknown:
    # commencement years are canon fields, not evidence of signing.
    agreement_event_history = []
    for agreement in agreements:
        aid = agreement["agreement_id"]
        agreement_event_history.append({
            "agreement_event_id": f"SWA-EVT-{_slug(aid)}-BASE",
            "agreement_id": aid,
            "event_type": "agreement_baseline_registered",
            "effective_year": None,
            "recorded_tick": 0,
            "event_status": "baseline_state_registration",
            "execution_date": None,
            "execution_date_status": "not_recorded",
            "date_precision": "unknown",
            "source_basis": "generated_fictional_canonical_world_history",
            "historical_date_known": False,
            "financial_transaction_created": False,
        })
        agreement_event_history.append({
            "agreement_event_id": f"SWA-EVT-{_slug(aid)}-COMMENCE",
            "agreement_id": aid,
            "event_type": "agreement_commenced",
            "effective_year": agreement["commencement_year"],
            "recorded_tick": 0,
            "event_status": "generated_canonical_history",
            "execution_date": None,
            "execution_date_status": "not_recorded",
            "date_precision": "year",
            "source_basis": "generated_fictional_canonical_world_history",
            "historical_date_known": True,
            "financial_transaction_created": False,
        })
        if agreement["expiry_year"] is not None:
            agreement_event_history.append({
                "agreement_event_id": f"SWA-EVT-{_slug(aid)}-EXPIRE",
                "agreement_id": aid,
                "event_type": "agreement_expired",
                "effective_year": agreement["expiry_year"],
                "recorded_tick": 0,
                "event_status": "generated_canonical_history",
                "execution_date": None,
                "execution_date_status": "not_recorded",
                "date_precision": "year",
                "source_basis": "generated_fictional_canonical_world_history",
                "historical_date_known": True,
                "financial_transaction_created": False,
            })

    for property_id, head_lessee_id in sorted(head_lessee_by_property.items()):
        owner_id = current_interests[property_id]["owner_organisation_id"]
        authority_id = f"SWLA-{_slug(property_id)}"
        authority_year = _number(property_id + "-owner-current-year", 2012, 2026)
        instrument_ref = f"SW-INSTR-{_slug(property_id)}-HEADLEASE"
        letting_authorities.append({
            "letting_authority_id": authority_id,
            "property_id": property_id,
            "unit_id": None,
            "grantor_organisation_id": owner_id,
            "grantee_organisation_id": head_lessee_id,
            "authority_type": "head_lease",
            "authority_status": "current",
            "effective_from_year": authority_year,
            "effective_to_year": None,
            "source_instrument_ref": instrument_ref,
            "source_basis": "generated_fictional_canon",
        })
        letting_authority_events.append({
            "letting_authority_event_id": str(uuid.UUID(
                hashlib.sha256(("SWLAE-" + property_id + "-GRANT").encode()).hexdigest()[:32]
            )),
            "letting_authority_id": authority_id,
            "event_type": "authority_granted",
            "effective_year": authority_year,
            "recorded_tick": 0,
            "actor_ref": owner_id,
            "source_ref": instrument_ref,
            "idempotency_key": f"SWLAE-{_slug(property_id)}-GRANT",
            "evidence_class": "generated_fictional_canon",
            "event_payload": {"authority_type": "head_lease", "fictional_canon": True},
        })

    all_organisations = list(owners.values()) + managers + head_lessee_organisations
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
            "independent_head_lessee_property_count": len(head_lessee_by_property),
            "letting_authority_count": len(letting_authorities),
            "letting_authority_event_count": len(letting_authority_events),
            "current_non_owner_landlord_agreement_count": sum(
                agreement["letting_authority_id"] is not None
                for agreement in agreements if agreement["expiry_year"] is None
            ),
            "current_lease_or_concession_count": len(businesses),
            "historical_expired_agreement_count": len(agreements) - len(businesses),
            "agreement_event_count": len(agreement_event_history),
            "agreement_execution_date_recorded_count": 0,
            "agreement_execution_date_unknown_count": len(agreements),
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
        "letting_authorities": letting_authorities,
        "letting_authority_events": letting_authority_events,
        "agreements": agreements,
        "agreement_event_history": agreement_event_history,
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
            "tenancy": "Each registered business establishment has a current lease, licence or operating concession linked to its unit and landlord. A non-owner landlord resolves through a property-scoped authority granted by the current title holder. Agreement history is append-only; execution dates remain explicitly unrecorded unless evidenced.",
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


def audit_property_tenure_role_separation(
    tenure: dict, property_world: dict, registry: dict
) -> dict:
    """Validate typed role references across ownership, management, contracts and possession.

    Role equality is permitted where the same organisation/business genuinely holds
    multiple roles (for example, direct owner-management or a tenant that operates
    its own establishment). The audit instead proves that each role is resolved
    through its owning identity register and that role relationships agree.
    """
    required_lists = {
        "current_ownership_interests": tenure.get("current_ownership_interests"),
        "management_appointments": tenure.get("management_appointments"),
        "agreements": tenure.get("agreements"),
        "occupancies": tenure.get("occupancies"),
        "organisations": tenure.get("organisations"),
        "letting_authorities": tenure.get("letting_authorities"),
        "letting_authority_events": tenure.get("letting_authority_events"),
        "properties": property_world.get("properties"),
        "businesses": registry.get("businesses"),
        "establishments": registry.get("establishments"),
    }
    for name, rows in required_lists.items():
        if not isinstance(rows, list):
            raise ValueError(f"{name} must be a list")

    organisation_ids = {row.get("organisation_id") for row in tenure["organisations"]}
    property_ids = {row.get("property_id") for row in property_world["properties"]}
    unit_by_id = {row["unit_id"]: row for row in property_world["units"]}
    business_by_id = {row.get("business_id"): row for row in registry["businesses"]}
    establishment_by_id = {
        row.get("establishment_id"): row for row in registry["establishments"]
    }
    if None in organisation_ids or None in business_by_id or None in establishment_by_id:
        raise ValueError("role identity registers contain missing stable IDs")

    owner_by_property = {}
    for interest in tenure["current_ownership_interests"]:
        property_id = interest.get("property_id")
        owner_id = interest.get("owner_organisation_id")
        if property_id not in property_ids or owner_id not in organisation_ids:
            raise ValueError("ownership role does not resolve to canonical property and organisation")
        if property_id in owner_by_property:
            raise ValueError(f"multiple current owner projections for property {property_id}")
        owner_by_property[property_id] = owner_id
    if set(owner_by_property) != property_ids:
        raise ValueError("current ownership register does not cover every canonical property")

    managers_by_property = {}
    direct_owner_management = 0
    third_party_management = 0
    for appointment in tenure["management_appointments"]:
        property_id = appointment.get("property_id")
        manager_id = appointment.get("manager_organisation_id")
        appointing_owner_id = appointment.get("appointing_organisation_id")
        if appointment.get("appointment_status") != "current":
            continue
        if property_id not in property_ids or manager_id not in organisation_ids:
            raise ValueError("manager role does not resolve to canonical property and organisation")
        if appointing_owner_id != owner_by_property.get(property_id):
            raise ValueError(f"management appointment for {property_id} was not made by its current owner")
        if property_id in managers_by_property:
            raise ValueError(f"multiple current management appointments for property {property_id}")
        managers_by_property[property_id] = manager_id
        if manager_id == appointing_owner_id:
            direct_owner_management += 1
            if appointment.get("management_model") != "direct_owner_management":
                raise ValueError("non-direct management model incorrectly assigns owner as manager")
        else:
            third_party_management += 1
            if appointment.get("management_model") == "direct_owner_management":
                raise ValueError("direct owner-management incorrectly assigns a separate manager")
    if set(managers_by_property) != property_ids:
        raise ValueError("current management appointments do not cover every canonical property")

    property_unit_classes = {}
    for unit in property_world.get("units", []):
        property_unit_classes.setdefault(unit.get("property_id"), set()).add(unit.get("unit_class"))
    manager_role_coverage = {}
    for unit_class in sorted({value for values in property_unit_classes.values() for value in values}):
        class_properties = {
            property_id for property_id, classes in property_unit_classes.items()
            if unit_class in classes
        }
        manager_role_coverage[unit_class] = {
            "property_count": len(class_properties),
            "direct_owner_management_count": sum(
                managers_by_property[property_id] == owner_by_property[property_id]
                for property_id in class_properties
            ),
            "third_party_management_count": sum(
                managers_by_property[property_id] != owner_by_property[property_id]
                for property_id in class_properties
            ),
        }

    authority_by_id = {
        row.get("letting_authority_id"): row for row in tenure["letting_authorities"]
    }
    if len(authority_by_id) != len(tenure["letting_authorities"]) or None in authority_by_id:
        raise ValueError("letting authority identities must be present and unique")
    organisation_by_id = {row["organisation_id"]: row for row in tenure["organisations"]}
    grant_events_by_authority = {}
    event_ids, idempotency_keys = set(), set()
    for event in tenure["letting_authority_events"]:
        event_id = event.get("letting_authority_event_id")
        key = event.get("idempotency_key")
        authority_id = event.get("letting_authority_id")
        if not event_id or event_id in event_ids or not key or key in idempotency_keys:
            raise ValueError("letting authority event identities and idempotency keys must be unique")
        event_ids.add(event_id)
        idempotency_keys.add(key)
        if authority_id not in authority_by_id:
            raise ValueError("letting authority event does not resolve to an authority")
        if event.get("event_type") == "authority_granted":
            grant_events_by_authority.setdefault(authority_id, []).append(event)
    for authority_id, authority in authority_by_id.items():
        if (
            authority.get("property_id") not in property_ids
            or authority.get("grantor_organisation_id") not in organisation_by_id
            or authority.get("grantee_organisation_id") not in organisation_by_id
            or authority.get("grantor_organisation_id") == authority.get("grantee_organisation_id")
            or authority.get("grantor_organisation_id") != owner_by_property[authority["property_id"]]
            or len(grant_events_by_authority.get(authority_id, [])) != 1
        ):
            raise ValueError(f"letting authority {authority_id} does not have a unique valid title-holder grant")
        grant = grant_events_by_authority[authority_id][0]
        if grant.get("effective_year") != authority.get("effective_from_year"):
            raise ValueError(f"letting authority {authority_id} grant event does not match its effective date")
    agreement_by_id = {}
    for agreement in tenure["agreements"]:
        agreement_id = agreement.get("agreement_id")
        property_id = agreement.get("property_id")
        landlord_id = agreement.get("landlord_organisation_id")
        manager_id = agreement.get("managing_organisation_id")
        tenant_id = agreement.get("tenant_business_id")
        operator_id = agreement.get("operator_business_id")
        establishment_id = agreement.get("establishment_id")
        establishment = establishment_by_id.get(establishment_id)
        if not agreement_id or agreement_id in agreement_by_id:
            raise ValueError("agreement identities must be present and unique")
        if property_id not in property_ids or landlord_id not in organisation_ids:
            raise ValueError(f"landlord role for {agreement_id} does not resolve to an organisation/property")
        authority_id = agreement.get("letting_authority_id")
        if landlord_id != owner_by_property[property_id]:
            authority = authority_by_id.get(authority_id)
            if (
                authority is None
                or authority.get("property_id") != property_id
                or authority.get("grantor_organisation_id") != owner_by_property[property_id]
                or authority.get("grantee_organisation_id") != landlord_id
                or authority.get("grantor_organisation_id") == authority.get("grantee_organisation_id")
                or (authority.get("unit_id") is not None and authority.get("unit_id") != agreement.get("unit_id"))
                or agreement.get("commencement_year", 0) < authority.get("effective_from_year", 99999)
                or (authority.get("effective_to_year") is not None and agreement.get("commencement_year", 99999) > authority["effective_to_year"])
                or len(grant_events_by_authority.get(authority_id, [])) != 1
            ):
                raise ValueError(f"non-owner landlord role for {agreement_id} lacks matching title-holder letting authority")
        elif authority_id is not None:
            raise ValueError(f"owner landlord role for {agreement_id} must not claim a non-owner letting authority")
        if manager_id not in organisation_ids or manager_id != managers_by_property[property_id]:
            raise ValueError(f"manager role for {agreement_id} does not match the current appointment")
        if tenant_id not in business_by_id or operator_id not in business_by_id:
            raise ValueError(f"tenant/operator role for {agreement_id} does not resolve to a business")
        if establishment is None or establishment.get("business_id") != tenant_id:
            raise ValueError(f"tenant role for {agreement_id} does not own its establishment")
        if establishment.get("property_id") != property_id or establishment.get("unit_id") != agreement.get("unit_id"):
            raise ValueError(f"agreement {agreement_id} does not match its establishment location")
        agreement_by_id[agreement_id] = agreement

    occupancy_by_agreement = {}
    for occupancy in tenure["occupancies"]:
        agreement_id = occupancy.get("agreement_id")
        agreement = agreement_by_id.get(agreement_id)
        occupant_id = occupancy.get("occupant_business_id")
        if agreement is None or occupant_id not in business_by_id:
            raise ValueError("occupant/agreement role does not resolve to canonical business records")
        if agreement_id in occupancy_by_agreement:
            raise ValueError(f"multiple current occupancy projections for agreement {agreement_id}")
        if occupant_id != agreement.get("tenant_business_id"):
            raise ValueError(f"occupant role for {agreement_id} differs from the contracted tenant")
        if occupancy.get("unit_id") != agreement.get("unit_id"):
            raise ValueError(f"occupancy for {agreement_id} differs from the contracted unit")
        if occupancy.get("establishment_id") != agreement.get("establishment_id"):
            raise ValueError(f"occupancy for {agreement_id} differs from the contracted establishment")
        if occupancy.get("occupant_type") != "business":
            raise ValueError("this canonical opening occupancy projection must identify business occupants")
        if occupancy.get("population_person_ids") != []:
            raise ValueError("property occupancy must not create or embed population person identities")
        occupancy_by_agreement[agreement_id] = occupancy

    if set(occupancy_by_agreement) != {
        agreement["agreement_id"] for agreement in tenure["agreements"]
        if agreement.get("expiry_year") is None
    }:
        raise ValueError("current occupancy projections do not match current agreements")

    return {
        "valid": True,
        "properties_checked": len(property_ids),
        "ownership_interests_checked": len(owner_by_property),
        "management_appointments_checked": len(managers_by_property),
        "direct_owner_management_count": direct_owner_management,
        "third_party_management_count": third_party_management,
        "management_role_coverage_by_unit_class": manager_role_coverage,
        "agreements_checked": len(agreement_by_id),
        "letting_authorities_checked": len(authority_by_id),
        "letting_authority_events_checked": len(tenure["letting_authority_events"]),
        "independent_landlord_agreement_count": sum(
            agreement.get("letting_authority_id") is not None
            for agreement in agreement_by_id.values()
        ),
        "independent_landlord_role_coverage_by_unit_class": {
            unit_class: {
                "agreement_count": sum(
                    agreement.get("letting_authority_id") is not None
                    and unit_by_id[agreement["unit_id"]]["unit_class"] == unit_class
                    for agreement in agreement_by_id.values()
                    if agreement.get("expiry_year") is None
                )
            }
            for unit_class in sorted({
                unit_by_id[agreement["unit_id"]]["unit_class"]
                for agreement in agreement_by_id.values()
                if agreement.get("expiry_year") is None
            })
        },
        "occupancies_checked": len(occupancy_by_agreement),
        "business_identities_checked": len(business_by_id),
        "organisation_identities_checked": len(organisation_ids),
        "person_records_created": tenure.get("summary", {}).get("person_records_created", 0),
        "independent_operator_agreement_count": sum(
            agreement.get("tenant_business_id") != agreement.get("operator_business_id")
            for agreement in agreement_by_id.values()
        ),
        "same_tenant_operator_agreement_count": sum(
            agreement.get("tenant_business_id") == agreement.get("operator_business_id")
            for agreement in agreement_by_id.values()
        ),
    }
