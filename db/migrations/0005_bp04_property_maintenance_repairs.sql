-- BP04 phase 3: maintenance, defects, repairs and asset lifecycle.
-- Production migration candidate; validate on disposable PostgreSQL before production application.
BEGIN;
CREATE TABLE sw_property.maintenance_contractor_profile (
 organisation_id text PRIMARY KEY REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 specialisms text[] NOT NULL, status text, fictional_entity boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.maintenance_plan (
 maintenance_plan_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 responsible_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 plan_type text NOT NULL, plan_status text NOT NULL, review_interval_days integer, risk_profile text, effective_tick bigint,
 source_dataset text NOT NULL
);
CREATE INDEX maintenance_plan_building_idx ON sw_property.maintenance_plan(building_id);
CREATE TABLE sw_property.maintenance_cycle (
 maintenance_cycle_id text PRIMARY KEY, maintenance_plan_id text NOT NULL REFERENCES sw_property.maintenance_plan(maintenance_plan_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 cycle_type text NOT NULL, interval_days integer, next_due_tick bigint, priority text, source_dataset text NOT NULL
);
CREATE TABLE sw_property.maintenance_inspection (
 inspection_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 building_system_id text REFERENCES sw_property.building_system(building_system_id) DEFERRABLE INITIALLY DEFERRED,
 inspection_type text NOT NULL, inspection_scope text, interval_days integer, last_completed_tick bigint, next_due_tick bigint,
 inspection_status text, responsible_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 result text, source_dataset text NOT NULL
);
CREATE INDEX maintenance_inspection_building_idx ON sw_property.maintenance_inspection(building_id);
CREATE TABLE sw_property.maintenance_defect (
 defect_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 building_system_id text NOT NULL REFERENCES sw_property.building_system(building_system_id) DEFERRABLE INITIALLY DEFERRED,
 equipment_id text NOT NULL REFERENCES sw_property.equipment_asset(equipment_id) DEFERRABLE INITIALLY DEFERRED,
 defect_location_type text, severity text NOT NULL, defect_category text, discovery_source text, discovered_tick bigint,
 defect_status text, operational_impact text, safety_implication text, root_cause_profile text, repair_urgency text,
 temporary_control text, raised_work_request_id text, source_dataset text NOT NULL
);
CREATE INDEX maintenance_defect_equipment_idx ON sw_property.maintenance_defect(equipment_id);
CREATE TABLE sw_property.maintenance_work_request (
 work_request_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 building_system_id text NOT NULL REFERENCES sw_property.building_system(building_system_id) DEFERRABLE INITIALLY DEFERRED,
 equipment_id text NOT NULL REFERENCES sw_property.equipment_asset(equipment_id) DEFERRABLE INITIALLY DEFERRED,
 defect_id text NOT NULL REFERENCES sw_property.maintenance_defect(defect_id) DEFERRABLE INITIALLY DEFERRED,
 request_type text, priority text, requested_tick bigint, request_status text,
 raised_by_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 responsible_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 description_code text, source_dataset text NOT NULL
);
CREATE TABLE sw_property.maintenance_work_order (
 work_order_id text PRIMARY KEY, work_request_id text NOT NULL REFERENCES sw_property.maintenance_work_request(work_request_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 building_system_id text NOT NULL REFERENCES sw_property.building_system(building_system_id) DEFERRABLE INITIALLY DEFERRED,
 equipment_id text NOT NULL REFERENCES sw_property.equipment_asset(equipment_id) DEFERRABLE INITIALLY DEFERRED,
 defect_id text NOT NULL REFERENCES sw_property.maintenance_defect(defect_id) DEFERRABLE INITIALLY DEFERRED,
 maintenance_plan_id text NOT NULL REFERENCES sw_property.maintenance_plan(maintenance_plan_id) DEFERRABLE INITIALLY DEFERRED,
 work_type text, priority text, work_order_status text,
 responsible_contractor_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 managing_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 required_trade text, estimated_duration_hours_band text, labour_costing text, scheduled_tick bigint, completion_tick bigint,
 verification_required boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.maintenance_work_order_line (
 work_order_line_id text PRIMARY KEY, work_order_id text NOT NULL REFERENCES sw_property.maintenance_work_order(work_order_id) DEFERRABLE INITIALLY DEFERRED,
 line_type text, asset_id text REFERENCES sw_property.equipment_asset(equipment_id) DEFERRABLE INITIALLY DEFERRED,
 description_code text, quantity_band text, trade text, source_dataset text NOT NULL
);
CREATE TABLE sw_property.maintenance_material_issue (
 material_issue_id text PRIMARY KEY, work_order_id text NOT NULL REFERENCES sw_property.maintenance_work_order(work_order_id) DEFERRABLE INITIALLY DEFERRED,
 equipment_id text NOT NULL REFERENCES sw_property.equipment_asset(equipment_id) DEFERRABLE INITIALLY DEFERRED,
 material_class text, quantity_band text, stock_source_profile text,
 financial_posting_created boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.maintenance_event (
 maintenance_event_id text PRIMARY KEY, work_order_id text NOT NULL REFERENCES sw_property.maintenance_work_order(work_order_id) DEFERRABLE INITIALLY DEFERRED,
 equipment_id text NOT NULL REFERENCES sw_property.equipment_asset(equipment_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 event_type text, event_tick bigint, event_status text, verification_state text, source_dataset text NOT NULL
);
CREATE TABLE sw_property.equipment_warranty (
 warranty_id text PRIMARY KEY, equipment_id text NOT NULL REFERENCES sw_property.equipment_asset(equipment_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 warranty_provider_profile text, start_year integer, end_year integer, warranty_state text, terms_profile text, source_dataset text NOT NULL
);
CREATE TABLE sw_property.equipment_replacement_forecast (
 replacement_plan_id text PRIMARY KEY, equipment_id text NOT NULL REFERENCES sw_property.equipment_asset(equipment_id) DEFERRABLE INITIALLY DEFERRED,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 building_system_id text NOT NULL REFERENCES sw_property.building_system(building_system_id) DEFERRABLE INITIALLY DEFERRED,
 replacement_reason text, target_year integer, priority text, capital_approval_state text,
 financial_commitment_created boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.building_emergency_procedure (
 procedure_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 procedure_scope text, scenarios text[] NOT NULL,
 first_response_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 continuity_arrangements text[] NOT NULL, person_records_created integer NOT NULL, source_dataset text NOT NULL
);
COMMIT;
