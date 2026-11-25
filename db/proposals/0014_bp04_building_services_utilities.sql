-- BP04 phase 2: typed building systems and utility operations.
-- Apply only after 0013 in the disposable PostgreSQL 16 benchmark.
-- Source gzip remains archived once; operational records are stored in typed columns.
BEGIN;
CREATE TABLE sw_property.building_system (
 building_system_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED, system_type text NOT NULL,
 system_status text, condition text, capacity_band text, redundancy_profile text, control_mode text, inspection_cycle_days integer,
 last_inspection_year integer, next_inspection_due_tick bigint,
 provider_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 effective_from_tick bigint, source_dataset text NOT NULL
);
CREATE INDEX building_system_property_idx ON sw_property.building_system(property_id);
CREATE INDEX building_system_building_idx ON sw_property.building_system(building_id);
CREATE TABLE sw_property.utility_connection (
 utility_connection_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 primary_building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED, utility_type text NOT NULL,
 provider_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 connection_point_type text, connection_capacity_band text, supply_redundancy text, connection_state text,
 is_live_game_connection boolean NOT NULL, effective_from_tick bigint, source_dataset text NOT NULL
);
CREATE INDEX utility_connection_property_idx ON sw_property.utility_connection(property_id);
CREATE TABLE sw_property.utility_provider_profile (
 organisation_id text PRIMARY KEY REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 display_name text NOT NULL, organisation_type text NOT NULL, registered_city text, status text,
 fictional_entity boolean NOT NULL, service_area text, source_dataset text NOT NULL
);
CREATE TABLE sw_property.utility_account (
 utility_account_id text PRIMARY KEY,
 utility_connection_id text NOT NULL REFERENCES sw_property.utility_connection(utility_connection_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 utility_type text NOT NULL,
 provider_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 account_holder_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 property_manager_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 account_scope text, billing_responsibility_profile text, metering_basis text, account_status text,
 financial_postings_created boolean NOT NULL, source_dataset text NOT NULL
);
CREATE INDEX utility_account_connection_idx ON sw_property.utility_account(utility_connection_id);
CREATE TABLE sw_property.meter (
 meter_id text PRIMARY KEY,
 utility_account_id text NOT NULL REFERENCES sw_property.utility_account(utility_account_id) DEFERRABLE INITIALLY DEFERRED,
 utility_connection_id text NOT NULL REFERENCES sw_property.utility_connection(utility_connection_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 unit_id text REFERENCES sw_property.unit_space(unit_id) DEFERRABLE INITIALLY DEFERRED,
 utility_type text NOT NULL, meter_role text, meter_type text, serial_reference text, read_frequency text, meter_state text,
 reading_value numeric, effective_from_tick bigint, source_dataset text NOT NULL
);
CREATE INDEX meter_account_idx ON sw_property.meter(utility_account_id);
CREATE INDEX meter_unit_idx ON sw_property.meter(unit_id);
CREATE TABLE sw_property.equipment_asset (
 equipment_id text PRIMARY KEY,
 building_system_id text NOT NULL REFERENCES sw_property.building_system(building_system_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 equipment_type text NOT NULL, equipment_reference text, manufacturer_profile text, installation_year integer,
 condition text, operational_state text, maintenance_class text, replacement_priority text, source_dataset text NOT NULL
);
CREATE INDEX equipment_system_idx ON sw_property.equipment_asset(building_system_id);
CREATE TABLE sw_property.system_inspection (
 inspection_id text PRIMARY KEY,
 building_system_id text NOT NULL REFERENCES sw_property.building_system(building_system_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 inspection_type text NOT NULL, inspection_interval_days integer, last_completed_year integer, next_due_tick bigint,
 inspection_status text, result_profile text, source_dataset text NOT NULL
);
CREATE INDEX system_inspection_system_idx ON sw_property.system_inspection(building_system_id);
CREATE TABLE sw_property.business_utility_responsibility (
 service_responsibility_id text PRIMARY KEY,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 premises_id text REFERENCES sw_property.premises(premises_id) DEFERRABLE INITIALLY DEFERRED,
 unit_id text REFERENCES sw_property.unit_space(unit_id) DEFERRABLE INITIALLY DEFERRED,
 occupancy_id text REFERENCES sw_property.occupancy(occupancy_id) DEFERRABLE INITIALLY DEFERRED,
 occupant_business_id text REFERENCES sw_property.business(business_id) DEFERRABLE INITIALLY DEFERRED,
 utility_scope text NOT NULL, responsibility_profile text, metering_basis text,
 financial_postings_created boolean NOT NULL, source_dataset text NOT NULL
);
CREATE INDEX utility_responsibility_property_idx ON sw_property.business_utility_responsibility(property_id);
CREATE INDEX utility_responsibility_occupancy_idx ON sw_property.business_utility_responsibility(occupancy_id);
COMMIT;
