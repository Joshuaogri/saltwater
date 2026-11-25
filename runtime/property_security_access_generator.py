"""Generate Saltwater's property doors, locks, keys, zones and organisation access control."""
from __future__ import annotations
import hashlib,json
from runtime.dataset_io import load_json
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_world_generator import to_columnar_document

GENERATOR="SW-PROPERTY-SECURITY-ACCESS-001"
def _n(k,lo,hi):
 d=hashlib.sha256(k.encode()).digest(); return lo+int.from_bytes(d[:4],"big")%(hi-lo+1)
def _pick(v,k): return v[_n(k,0,len(v)-1)]
def _slug(v): return "".join(c for c in str(v).upper() if c.isalnum())[:24]

def build_property_security(world,tenure,services):
 props={x["property_id"]:x for x in world["properties"]}
 buildings={x["building_id"]:x for x in world["buildings"]}
 premises={x["premises_id"]:x for x in world["premises"]}
 units={x["unit_id"]:x for x in world["units"]}
 access=world["access_points"]; routes={x["access_point_id"]:x for x in world["access_routes"]}
 managers={x["property_id"]:x["manager_organisation_id"] for x in tenure["management_appointments"]}
 owners={x["property_id"]:x["owner_organisation_id"] for x in tenure["current_ownership_interests"]}
 occ_by_unit={x["unit_id"]:x for x in tenure["occupancies"]}
 biz={x["business_id"]:x for x in _expand_columnar(__import__("json").loads((Path(__file__).resolve().parents[1]/"data/business/saltwater-business-registry-v1.json").read_text()))["businesses"]} if False else {}
 doors=[]; locks=[]; cylinders=[]; keys=[]; credentials=[]; devices=[]; zones=[]; groups=[]; permissions=[]; assignments=[]; cabinets=[]; policies=[]; events=[]
 access_groups={}
 for a in sorted(access,key=lambda x:x["access_point_id"]):
  aid=a["access_point_id"]; pid=a["property_id"]; bid=a.get("building_id"); route=routes.get(aid,{})
  door_id=f"SWDOOR-{_slug(aid)}"; lock_id=f"SWLOCK-{_slug(aid)}"
  doors.append({"door_id":door_id,"access_point_id":aid,"property_id":pid,"building_id":bid,"door_role":a.get("access_type"),"door_type":a.get("door_type","gate_or_door"),"clear_width_m":a.get("clear_width_m"),"opening_direction_profile":_pick(["outward_egress","inward_entry","sliding","overhead"],aid+"dir"),"fire_or_smoke_rating_profile":"rated_where_required_by_building_design" if bid else "not_applicable_or_unrated_site_gate","egress_hardware": "panic_release" if a.get("emergency_egress_state")=="designated_egress" else "standard_hardware","door_state":"operational","route_id":route.get("route_id"),"maintenance_dataset":"SW-PROPERTY-MAINTENANCE-V1"})
  lock_type={"keyed_lock":"mechanical_cylinder","keyed_maintenance_lock":"restricted_mechanical_cylinder","electronic_card":"electronic_access_controller","staff_controlled":"staffed_release_control","panic_hardware":"mechanical_lock_with_free_egress"}.get(a.get("control_type"),"mechanical_cylinder")
  locks.append({"lock_id":lock_id,"door_id":door_id,"access_point_id":aid,"property_id":pid,"building_id":bid,"lock_type":lock_type,"security_grade":_pick(["standard_commercial","high_security","restricted_keyway","electronic_supervised"],aid+"grade"),"outside_entry_control":"credential_required" if lock_type in ("electronic_access_controller","mechanical_cylinder","restricted_mechanical_cylinder") else "controlled_release","inside_egress":"free_mechanical_egress","fail_state":_pick(["fail_secure_with_free_egress","fail_safe_on_fire_signal","mechanical_override"],aid+"fail"),"monitoring_state":"supervised" if lock_type=="electronic_access_controller" else "not_electronically_monitored","lock_state":"in_service"})
  if lock_type in ("mechanical_cylinder","restricted_mechanical_cylinder","mechanical_lock_with_free_egress"):
   cylinders.append({"cylinder_id":f"SWCYL-{_slug(aid)}","lock_id":lock_id,"keyway_profile":_pick(["SW-KW-A","SW-KW-B","SW-KW-R"],aid+"kw"),"key_control_class":"restricted" if lock_type=="restricted_mechanical_cylinder" else "managed","master_keyed":True,"key_copy_control":"authorised_organisation_issue_only"})
   for kind in ("operational","maintenance","emergency_master"):
    keys.append({"key_id":f"SWKEY-{_slug(aid)}-{kind[:3].upper()}","cylinder_id":f"SWCYL-{_slug(aid)}","property_id":pid,"key_class":kind,"key_status":"in_controlled_stock","issue_to_person_id":None,"issue_to_organisation_id":None,"duplicate_control":"logged_authorisation_required"})
  if lock_type=="electronic_access_controller":
   devices.append({"security_device_id":f"SWSECDEV-{_slug(aid)}","device_type":"door_access_controller_and_reader","access_point_id":aid,"door_id":door_id,"lock_id":lock_id,"property_id":pid,"building_id":bid,"device_state":"online","power_backup_profile":"local_ups_or_building_backup_where_fitted","network_path":"building_security_network","tamper_monitoring":True})
  zone_id=f"SWZ-{_slug(bid or pid)}-ENTRY"
  access_groups.setdefault((pid,bid),set()).add(zone_id)
  policies.append({"access_policy_id":f"SWAPOL-{_slug(aid)}","access_point_id":aid,"door_id":door_id,"property_id":pid,"building_id":bid,"schedule_profile":"site_opening_schedule" if a.get("opening_schedule") else "continuous_controlled","emergency_override":"fire_and_life_safety_override","anti_passback":"enabled_for_electronic_access" if lock_type=="electronic_access_controller" else "not_applicable","tailgating_control":"procedural_or_sensor_control"})
 # zones for building, premises and unit boundaries
 for bid,b in sorted(buildings.items()):
  pid=b["property_id"]
  zones.append({"access_zone_id":f"SWZ-{_slug(bid)}-ENTRY","property_id":pid,"building_id":bid,"premises_id":None,"unit_id":None,"zone_type":"building_entry_control","security_level":"controlled","zone_state":"active","parent_zone_id":None})
  for ztype in ("public_reception","staff_only","plant_and_utilities","restricted_security","emergency_egress"):
   zid=f"SWZ-{_slug(bid)}-{ztype.upper()}"
   zones.append({"access_zone_id":zid,"property_id":pid,"building_id":bid,"premises_id":None,"unit_id":None,"zone_type":ztype,"security_level":_pick(["open","controlled","restricted","critical"],zid),"zone_state":"active","parent_zone_id":f"SWZ-{_slug(bid)}-ENTRY"})
 for prid,p in sorted(premises.items()):
  bid=p["building_id"]; pid=p["property_id"]
  zid=f"SWZ-{_slug(prid)}"
  zones.append({"access_zone_id":zid,"property_id":pid,"building_id":bid,"premises_id":prid,"unit_id":None,"zone_type":"premises_occupancy","security_level":"tenant_or_operator_controlled","zone_state":"active","parent_zone_id":f"SWZ-{_slug(bid)}-STAFF_ONLY"})
  for uid in p.get("unit_ids",[]):
   zones.append({"access_zone_id":f"SWZ-{_slug(uid)}","property_id":pid,"building_id":bid,"premises_id":prid,"unit_id":uid,"zone_type":"individual_unit","security_level":"unit_occupier_controlled","zone_state":"active","parent_zone_id":zid})
 # Organisation access groups and grants; never individual-person credentials.
 for unit_id,occ in sorted(occ_by_unit.items()):
  unit=units[unit_id]; pid=unit["property_id"]; bid=unit["building_id"]; prid=unit["premises_id"]; business_id=occ["occupant_business_id"]
  gid=f"SWAG-{_slug(unit_id)}"
  groups.append({"access_group_id":gid,"group_type":"business_occupancy_access_group","property_id":pid,"building_id":bid,"premises_id":prid,"unit_id":unit_id,"business_id":business_id,"occupancy_id":occ["occupancy_id"],"group_status":"active" if occ["occupancy_status"]=="occupied" else "conditional_or_seasonal","member_person_ids":[],"credential_issue_mode":"future_named_person_assignment_by_runtime"})
  permissions.append({"permission_set_id":f"SWPER-{_slug(unit_id)}","access_group_id":gid,"permitted_zone_ids":[f"SWZ-{_slug(prid)}",f"SWZ-{_slug(unit_id)}"],"permission_scope":"leased_unit_and_premises_only","schedule_profile":"lease_operating_hours","privileges":["unlock_occupied_unit","use_shared_occupancy_route"],"prohibited_privileges":["master_key_access","plant_room_access","other_tenant_units","security_control_room"],"effective_from_tick":0,"revocable":True})
  assignments.append({"access_assignment_id":f"SWASG-{_slug(unit_id)}","access_group_id":gid,"business_id":business_id,"occupancy_id":occ["occupancy_id"],"permission_set_id":f"SWPER-{_slug(unit_id)}","assignment_basis":"current_lease_or_concession","assignment_status":"active" if occ["occupancy_status"]=="occupied" else "conditional","person_credentials_created":0})
 # Controlled key cabinets per property; inventories reference keys without assigning to people.
 for pid in sorted(props):
  cabinet_id=f"SWKCAB-{_slug(pid)}"
  cabinets.append({"key_cabinet_id":cabinet_id,"property_id":pid,"managing_organisation_id":managers[pid],"cabinet_type":"tamper_evident_key_control_cabinet","access_control":"manager_authorised_organisation_control","key_inventory_count":sum(1 for k in keys if k["property_id"]==pid),"issue_register_required":True,"audit_interval_days":30,"person_records_created":0})
 for bid,b in sorted(buildings.items()):
  policies.append({"access_policy_id":f"SWAPOL-BLDG-{_slug(bid)}","property_id":b["property_id"],"building_id":bid,"policy_scope":"building_security_governance","visitor_management":"host_authorisation_and_time_limited_pass","contractor_access":"work_order_or_service_authorisation_linked","lost_credential_response":"revoke_and_rekey_or_reissue","emergency_services":"emergency_access_override_with_audit"})
 body={"schema":"saltwater-property-security-access/1.0","dataset_id":"SW-PROPERTY-SECURITY-ACCESS-V1","canon_status":"CANONICAL_FICTIONAL_GAME_WORLD","generator":GENERATOR,"effective_tick":0,"city":"Saltwater","summary":{"property_count":len(props),"building_count":len(buildings),"access_point_count":len(access),"door_count":len(doors),"lock_count":len(locks),"mechanical_cylinder_count":len(cylinders),"physical_key_count":len(keys),"electronic_security_device_count":len(devices),"access_zone_count":len(zones),"access_group_count":len(groups),"permission_set_count":len(permissions),"organisation_access_assignment_count":len(assignments),"key_cabinet_count":len(cabinets),"access_policy_count":len(policies),"person_credentials_created":0,"person_records_created":0,"population_records_created":0,"financial_postings_created":0},"doors":doors,"locks":locks,"key_cylinders":cylinders,"physical_keys":keys,"security_devices":devices,"access_zones":zones,"access_groups":groups,"permission_sets":permissions,"organisation_access_assignments":assignments,"key_cabinets":cabinets,"access_policies":policies,"lineage":{"property_world_dataset":"SW-PROPERTY-WORLD-V1","property_tenure_dataset":"SW-PROPERTY-TENURE-V1","building_services_dataset":"SW-BUILDING-SERVICES-V1","property_maintenance_dataset":"SW-PROPERTY-MAINTENANCE-V1"},"gameplay":{"physical_security":"Every canonical access point has a door/gate and lock record, with mechanical key control or an electronic controller as appropriate.","access_control":"Zones cover buildings, premises and individual units; business permissions are bounded by the current occupancy and leased unit.","credential_boundary":"Credentials are assigned to organisations/groups only. No named person credentials, employees, residents or population records are created.","audit":"Key issue registers, visitor controls, contractor authorisation, lost credential revocation and emergency override audit policies are defined; runtime events are created during play.","life_safety":"Emergency egress remains mechanically available; security controls do not obstruct designated egress.","finance_boundary":"No invoices, payments, asset purchases or financial postings are created."}}
 canonical=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode(); body["manifest_sha256"]=hashlib.sha256(canonical).hexdigest()
 return body

def main():
 root=Path(__file__).resolve().parents[1]
 def load(path): return _expand_columnar(load_json(root/path))
 result=build_property_security(load("data/property/saltwater-property-world-v1.json"),load("data/property/saltwater-property-tenure-v1.json"),load("data/property/saltwater-building-services-v1.json"))
 out=root/"data/property/saltwater-property-security-access-v1.json"; doc=to_columnar_document(result); doc["schema"]="saltwater-property-security-access-columnar/1.0"
 out.write_text(json.dumps(doc,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps(result["summary"]|{"manifest_sha256":result["manifest_sha256"],"output_bytes":out.stat().st_size},indent=2,sort_keys=True))
if __name__=="__main__": main()
