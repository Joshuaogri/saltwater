-- BP04 phase 4: physical security, keys, zones and organisation access control.
-- Disposable PostgreSQL benchmark only; never apply to production Neon.
BEGIN;
CREATE TABLE sw_property.security_door (
 door_id text PRIMARY KEY, access_point_id text NOT NULL REFERENCES sw_property.access_point(access_point_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 door_role text, door_type text, clear_width_m numeric, opening_direction_profile text, fire_or_smoke_rating_profile text,
 egress_hardware text, door_state text, route_id text REFERENCES sw_property.access_route(route_id) DEFERRABLE INITIALLY DEFERRED,
 maintenance_dataset text, source_dataset text NOT NULL
);
CREATE INDEX security_door_access_point_idx ON sw_property.security_door(access_point_id);
CREATE TABLE sw_property.security_lock (
 lock_id text PRIMARY KEY, door_id text NOT NULL REFERENCES sw_property.security_door(door_id) DEFERRABLE INITIALLY DEFERRED,
 access_point_id text NOT NULL REFERENCES sw_property.access_point(access_point_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 lock_type text, security_grade text, outside_entry_control text, inside_egress text, fail_state text,
 monitoring_state text, lock_state text, source_dataset text NOT NULL
);
CREATE TABLE sw_property.key_cylinder (
 cylinder_id text PRIMARY KEY, lock_id text NOT NULL REFERENCES sw_property.security_lock(lock_id) DEFERRABLE INITIALLY DEFERRED,
 keyway_profile text, key_control_class text, master_keyed boolean NOT NULL, key_copy_control text, source_dataset text NOT NULL
);
CREATE TABLE sw_property.physical_key (
 key_id text PRIMARY KEY, cylinder_id text NOT NULL REFERENCES sw_property.key_cylinder(cylinder_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 key_class text, key_status text, issue_to_person_id text, issue_to_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 duplicate_control text, source_dataset text NOT NULL,
 CONSTRAINT physical_key_no_person_credential CHECK (issue_to_person_id IS NULL)
);
CREATE TABLE sw_property.security_device (
 security_device_id text PRIMARY KEY, device_type text, access_point_id text NOT NULL REFERENCES sw_property.access_point(access_point_id) DEFERRABLE INITIALLY DEFERRED,
 door_id text NOT NULL REFERENCES sw_property.security_door(door_id) DEFERRABLE INITIALLY DEFERRED,
 lock_id text NOT NULL REFERENCES sw_property.security_lock(lock_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 device_state text, power_backup_profile text, network_path text, tamper_monitoring boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.access_zone (
 access_zone_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 premises_id text REFERENCES sw_property.premises(premises_id) DEFERRABLE INITIALLY DEFERRED,
 unit_id text REFERENCES sw_property.unit_space(unit_id) DEFERRABLE INITIALLY DEFERRED,
 zone_type text NOT NULL, security_level text, zone_state text,
 parent_zone_id text REFERENCES sw_property.access_zone(access_zone_id) DEFERRABLE INITIALLY DEFERRED,
 source_dataset text NOT NULL
);
CREATE INDEX access_zone_property_idx ON sw_property.access_zone(property_id);
CREATE INDEX access_zone_parent_idx ON sw_property.access_zone(parent_zone_id);
CREATE TABLE sw_property.access_group (
 access_group_id text PRIMARY KEY, group_type text NOT NULL,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 premises_id text REFERENCES sw_property.premises(premises_id) DEFERRABLE INITIALLY DEFERRED,
 unit_id text NOT NULL REFERENCES sw_property.unit_space(unit_id) DEFERRABLE INITIALLY DEFERRED,
 business_id text REFERENCES sw_property.business(business_id) DEFERRABLE INITIALLY DEFERRED,
 occupancy_id text REFERENCES sw_property.occupancy(occupancy_id) DEFERRABLE INITIALLY DEFERRED,
 group_status text, member_person_ids text[] NOT NULL, credential_issue_mode text, source_dataset text NOT NULL,
 CONSTRAINT access_group_no_person_members CHECK (cardinality(member_person_ids)=0)
);
CREATE TABLE sw_property.permission_set (
 permission_set_id text PRIMARY KEY, access_group_id text NOT NULL REFERENCES sw_property.access_group(access_group_id) DEFERRABLE INITIALLY DEFERRED,
 permission_scope text, schedule_profile text, privileges text[] NOT NULL, prohibited_privileges text[] NOT NULL,
 effective_from_tick bigint, revocable boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.permission_zone_grant (
 grant_id text PRIMARY KEY,
 permission_set_id text NOT NULL REFERENCES sw_property.permission_set(permission_set_id) DEFERRABLE INITIALLY DEFERRED,
 access_zone_id text NOT NULL REFERENCES sw_property.access_zone(access_zone_id) DEFERRABLE INITIALLY DEFERRED,
 grant_order integer NOT NULL, source_dataset text NOT NULL,
 UNIQUE(permission_set_id,access_zone_id)
);
CREATE TABLE sw_property.organisation_access_assignment (
 access_assignment_id text PRIMARY KEY, access_group_id text NOT NULL REFERENCES sw_property.access_group(access_group_id) DEFERRABLE INITIALLY DEFERRED,
 business_id text REFERENCES sw_property.business(business_id) DEFERRABLE INITIALLY DEFERRED,
 occupancy_id text REFERENCES sw_property.occupancy(occupancy_id) DEFERRABLE INITIALLY DEFERRED,
 permission_set_id text NOT NULL REFERENCES sw_property.permission_set(permission_set_id) DEFERRABLE INITIALLY DEFERRED,
 assignment_basis text, assignment_status text, person_credentials_created integer NOT NULL, source_dataset text NOT NULL,
 CHECK (person_credentials_created=0)
);
CREATE TABLE sw_property.key_cabinet (
 key_cabinet_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 managing_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 cabinet_type text, access_control text, key_inventory_count integer, issue_register_required boolean NOT NULL,
 audit_interval_days integer, person_records_created integer NOT NULL, source_dataset text NOT NULL,
 CHECK (person_records_created=0)
);
CREATE TABLE sw_property.access_policy (
 access_policy_id text PRIMARY KEY, access_point_id text REFERENCES sw_property.access_point(access_point_id) DEFERRABLE INITIALLY DEFERRED,
 door_id text REFERENCES sw_property.security_door(door_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 policy_scope text, schedule_profile text, emergency_override text, anti_passback text, tailgating_control text,
 visitor_management text, contractor_access text, lost_credential_response text, emergency_services text, source_dataset text NOT NULL
);
COMMIT;
