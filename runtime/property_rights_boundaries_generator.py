"""Build property rights, easements, wayleaves and boundary evidence registers."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_world_generator import to_columnar_document

GENERATOR = "SW-PROPERTY-RIGHTS-AND-BOUNDARIES-001"

def _key(value):
    return hashlib.sha256(str(value).encode()).hexdigest()[:14].upper()

def build_property_rights(world, tenure, lifecycle, services, security):
    props={x["property_id"]:x for x in world["properties"]}
    buildings={x["building_id"]:x for x in world["buildings"]}
    premises={x["premises_id"]:x for x in world["premises"]}
    units={x["unit_id"]:x for x in world["units"]}
    title={x["property_id"]:x for x in lifecycle["title_register"]}
    owners={x["property_id"]:x for x in tenure["current_ownership_interests"]}
    agreements=tenure["agreements"]
    access={x["access_point_id"]:x for x in world["access_points"]}
    routes={x["access_point_id"]:x for x in world["access_routes"]}
    connections={pid:[] for pid in props}
    for row in services["property_utility_connections"]:
        connections.setdefault(row["property_id"],[]).append(row)
    # Contractual occupancy rights are indexes to existing agreements, not new grants.
    agreement_rights=[]
    for a in sorted(agreements,key=lambda x:x["agreement_id"]):
        agreement_rights.append({
            "property_right_id":f"SWCR-{_key(a['agreement_id'])}",
            "property_id":a["property_id"],"building_id":a["building_id"],
            "premises_id":a["premises_id"],"unit_id":a["unit_id"],
            "right_type":"contractual_lease_licence_or_concession",
            "holder_business_id":a["tenant_business_id"],
            "grantor_organisation_id":a["landlord_organisation_id"],
            "managing_organisation_id":a["managing_organisation_id"],
            "source_agreement_id":a["agreement_id"],
            "commencement_year":a["commencement_year"],"expiry_year":a["expiry_year"],
            "right_status":"current" if a["agreement_status"] in ("active","seasonal","temporarily_inactive") else "historical_expired",
            "permitted_use":a["permitted_use"],"source_of_truth":"SW-PROPERTY-TENURE-V1",
            "new_legal_instrument_created":False
        })
    property_schedules=[]; boundary_evidence=[]; access_evidence=[]; utility_wayleave_requirements=[]
    right_classes=["ownership","leasehold_or_occupancy","easement","right_of_way","wayleave","restrictive_covenant","positive_covenant","mortgage_or_charge","lien_or_caveat","development_restriction","heritage_or_environmental_restriction","boundary_agreement"]
    for pid,p in sorted(props.items()):
        title_row=title[pid]; owner=owners[pid]
        property_schedules.append({
            "property_rights_schedule_id":f"SWPRS-{_key(pid)}","property_id":pid,
            "title_register_id":title_row["title_register_id"],
            "registered_ownership_interest_id":owner["ownership_interest_id"],
            "registered_owner_organisation_id":owner["owner_organisation_id"],
            "current_contractual_right_count":sum(1 for x in agreement_rights if x["property_id"]==pid and x["right_status"]=="current"),
            "historical_contractual_right_count":sum(1 for x in agreement_rights if x["property_id"]==pid and x["right_status"]=="historical_expired"),
            "right_class_coverage":right_classes,
            "unverified_right_classes":right_classes[2:],
            "schedule_status":"ownership_and_agreement_indexes_present_other_rights_unverified",
            "legal_search_required_before_disposition_or_works":True
        })
        # The polygon is evidence of the fictional planning parcel only, not a surveyed or registered boundary.
        boundary_evidence.append({
            "boundary_evidence_id":f"SWBND-EV-{_key(pid)}","property_id":pid,
            "title_register_id":title_row["title_register_id"],
            "source_parcel_id":p.get("source_candidate_parcel_id"),
            "source_geometry_ref":p.get("source_ref") or f"SW-PROPERTY-WORLD-V1:{pid}",
            "geometry_present":bool(p.get("geometry")),
            "evidence_class":"canonical_planning_parcel_geometry",
            "survey_status":"not_survey_grade","legal_boundary_status":"not_independently_verified",
            "coordinates_reproduced":False,"boundary_dispute_status":"not_assessed",
            "adjoining_owner_consent_status":"not_recorded",
            "boundary_change_event_count":0
        })
        for aid,a in sorted(access.items()):
            if a["property_id"]!=pid: continue
            route=routes.get(aid)
            access_evidence.append({
                "physical_access_evidence_id":f"SWPAE-{_key(aid)}","property_id":pid,
                "building_id":a["building_id"],"access_point_id":aid,
                "constructed_route_id":route.get("route_id") if route else None,
                "road_id":a.get("road_link_road_id"),
                "physical_connection_status":"constructed_route_recorded" if route else "route_record_not_found",
                "access_type":a["access_type"],"access_modes":a["access_modes"],
                "legal_right_of_way_status":"not_asserted",
                "easement_or_wayleave_instrument_id":None,
                "frontage_or_proximity_is_not_legal_access":True
            })
        for c in connections.get(pid,[]):
            utility_wayleave_requirements.append({
                "utility_wayleave_requirement_id":f"SWWLR-{_key(c['utility_connection_id'])}",
                "property_id":pid,"utility_connection_id":c["utility_connection_id"],
                "utility_type":c["utility_type"],"provider_organisation_id":c["provider_organisation_id"],
                "connection_status":c.get("connection_status","recorded_connection"),
                "wayleave_or_easement_instrument_id":None,
                "legal_route_right_status":"not_evidenced",
                "operational_connection_is_not_proof_of_property_right":True
            })
    # Register is intentionally empty until supported source evidence or gameplay creates an instrument.
    instrument_register=[]
    instrument_types=[
        ("easement","dominant_and_servient_property_ids_required"),
        ("right_of_way","route_geometry_and_benefited_property_required"),
        ("utility_wayleave","provider_asset_route_and_affected_property_required"),
        ("restrictive_covenant","burdened_property_and_benefit_description_required"),
        ("positive_covenant","obligation_holder_and_enforcement_mechanism_required"),
        ("mortgage_or_charge","lender_and_secured_obligation_reference_required"),
        ("lien_or_caveat","claim_basis_and_registration_status_required"),
        ("boundary_agreement","adjoining_parcels_and_signed_boundary_plan_required"),
        ("access_licence","grantor_grantee_route_scope_and_term_required")
    ]
    templates=[{"instrument_type":t,"minimum_evidence":e,"creation_policy":"only_from_explicit_canonical_source_or_gameplay_event","default_status":"not_recorded"} for t,e in instrument_types]
    summary={
        "property_count":len(props),"property_rights_schedule_count":len(property_schedules),
        "contractual_right_index_count":len(agreement_rights),
        "current_contractual_right_count":sum(x["right_status"]=="current" for x in agreement_rights),
        "historical_contractual_right_count":sum(x["right_status"]=="historical_expired" for x in agreement_rights),
        "boundary_evidence_record_count":len(boundary_evidence),
        "physical_access_evidence_record_count":len(access_evidence),
        "utility_wayleave_requirement_count":len(utility_wayleave_requirements),
        "registered_easement_count":0,"registered_wayleave_count":0,
        "registered_mortgage_or_charge_count":0,"registered_covenant_count":0,
        "registered_lien_or_caveat_count":0,"boundary_dispute_count":0,
        "new_legal_instruments_created":0,"legal_access_inferences_created":0,
        "person_records_created":0,"financial_postings_created":0,
        "future_instrument_type_count":len(templates)
    }
    body={
        "schema":"saltwater-property-rights-boundaries/1.0",
        "dataset_id":"SW-PROPERTY-RIGHTS-AND-BOUNDARIES-V1",
        "canon_status":"CANONICAL_FICTIONAL_GAME_WORLD","generator":GENERATOR,
        "effective_tick":0,"city":"Saltwater","summary":summary,
        "property_rights_schedules":property_schedules,
        "contractual_rights_index":agreement_rights,
        "boundary_evidence_register":boundary_evidence,
        "physical_access_evidence_register":access_evidence,
        "utility_wayleave_requirements":utility_wayleave_requirements,
        "registered_instrument_register":instrument_register,
        "future_instrument_templates":templates,
        "lineage":{"property_world":"SW-PROPERTY-WORLD-V1","property_tenure":"SW-PROPERTY-TENURE-V1","property_lifecycle":"SW-PROPERTY-LIFECYCLE-TRANSACTIONS-V1","building_services":"SW-BUILDING-SERVICES-V1","physical_access":"SW-PROPERTY-WORLD-V1.access_points_and_access_routes"},
        "governance":{
            "boundary":"Planning parcel geometry is retained as source evidence only. It is not a legal survey, registered title plan or proof of exact legal boundary.",
            "access":"A constructed entrance, driveway, route, road frontage or proximity link is not proof of a legal right of way, easement, emergency access right or ownership.",
            "utilities":"A recorded utility connection does not establish a wayleave, easement, landowner consent or asset ownership right.",
            "unknowns":"No missing easement, covenant, charge, lien or boundary agreement is represented as absent. Such rights remain unverified until evidence is recorded.",
            "contractual":"Lease, licence and concession rows are references to existing tenure agreements. No duplicate contract or new legal grant is created.",
            "population_and_finance":"No person, population, invoice, payment, loan balance or financial posting is created."
        }
    }
    canonical=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    body["manifest_sha256"]=hashlib.sha256(canonical).hexdigest()
    return body

def main():
    root=Path(__file__).resolve().parents[1]
    def load(path): return _expand_columnar(json.loads((root/path).read_text(encoding="utf-8")))
    data=build_property_rights(
        load("data/property/saltwater-property-world-v1.json"),
        load("data/property/saltwater-property-tenure-v1.json"),
        load("data/property/saltwater-property-lifecycle-transactions-v1.json"),
        load("data/property/saltwater-building-services-v1.json"),
        load("data/property/saltwater-property-security-access-v1.json"))
    out=root/"data/property/saltwater-property-rights-boundaries-v1.json"
    doc=to_columnar_document(data); doc["schema"]="saltwater-property-rights-boundaries-columnar/1.0"
    out.write_text(json.dumps(doc,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(data["summary"]|{"manifest_sha256":data["manifest_sha256"],"output_bytes":out.stat().st_size},indent=2,sort_keys=True))
if __name__=="__main__": main()
