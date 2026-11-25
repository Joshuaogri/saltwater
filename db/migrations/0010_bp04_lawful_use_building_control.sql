-- BP04 phase 8: police-gameplay-relevant lawful-use and building-control records.
-- The 180,733 unit-use-compliance rows remain losslessly archived, not duplicated as operational rows.
-- Disposable PostgreSQL benchmark only; never apply to production Neon.
BEGIN;
CREATE TABLE sw_property.site_development_plan (
  site_development_plan_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
  applicant_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
  land_use_designation text NOT NULL,
  development_intensity text NOT NULL,
  site_plan_status text NOT NULL,
  site_constraints text[] NOT NULL,
  planning_policy_version text NOT NULL,
  adoption_tick bigint NOT NULL,
  source_basis text NOT NULL,
  source_dataset text NOT NULL
);
CREATE TABLE sw_property.planning_permission (
  planning_permission_id text PRIMARY KEY,
  site_development_plan_id text NOT NULL REFERENCES sw_property.site_development_plan(site_development_plan_id) DEFERRABLE INITIALLY DEFERRED,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
  building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
  applicant_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
  permission_type text NOT NULL,
  development_description text NOT NULL,
  approved_use_class text NOT NULL,
  decision text NOT NULL,
  decision_tick bigint NOT NULL,
  decision_basis text NOT NULL,
  conditions text[] NOT NULL,
  permission_validity text NOT NULL,
  historic_application_fabricated boolean NOT NULL,
  source_dataset text NOT NULL
);
CREATE TABLE sw_property.building_control_case (
  building_control_case_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
  building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
  planning_permission_id text NOT NULL REFERENCES sw_property.planning_permission(planning_permission_id) DEFERRABLE INITIALLY DEFERRED,
  applicant_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
  principal_contractor_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
  control_route text NOT NULL,
  case_status text NOT NULL,
  design_standard_profile text NOT NULL,
  fire_safety_review text NOT NULL,
  structural_review text NOT NULL,
  accessibility_review text NOT NULL,
  utility_and_drainage_review text NOT NULL,
  construction_year integer,
  case_basis text NOT NULL,
  inspection_history text NOT NULL,
  source_dataset text NOT NULL
);
CREATE TABLE sw_property.building_inspection_schedule (
  building_inspection_schedule_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
  building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
  building_control_case_id text NOT NULL REFERENCES sw_property.building_control_case(building_control_case_id) DEFERRABLE INITIALLY DEFERRED,
  inspection_type text NOT NULL,
  inspection_interval_days integer NOT NULL,
  next_due_tick bigint NOT NULL,
  inspection_status text NOT NULL,
  priority text NOT NULL,
  linked_open_defects integer NOT NULL,
  inspection_visit_created boolean NOT NULL,
  source_dataset text NOT NULL
);
CREATE TABLE sw_property.completion_certificate (
  completion_certificate_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
  building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
  building_control_case_id text NOT NULL REFERENCES sw_property.building_control_case(building_control_case_id) DEFERRABLE INITIALLY DEFERRED,
  certificate_type text NOT NULL,
  certificate_status text NOT NULL,
  issue_tick bigint NOT NULL,
  issue_basis text NOT NULL,
  approved_use_class text NOT NULL,
  conditions text[] NOT NULL,
  certificate_number text NOT NULL,
  source_dataset text NOT NULL
);
CREATE TABLE sw_property.lawful_use_certificate (
  lawful_use_certificate_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
  building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
  premises_id text NOT NULL REFERENCES sw_property.premises(premises_id) DEFERRABLE INITIALLY DEFERRED,
  completion_certificate_id text NOT NULL REFERENCES sw_property.completion_certificate(completion_certificate_id) DEFERRABLE INITIALLY DEFERRED,
  lawful_use_class text NOT NULL,
  certificate_status text NOT NULL,
  effective_tick bigint NOT NULL,
  change_of_use_permission_required boolean NOT NULL,
  use_conditions text[] NOT NULL,
  evidence_basis text NOT NULL,
  source_dataset text NOT NULL
);
CREATE TABLE sw_property.development_project (
  development_project_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
  project_type text NOT NULL,
  project_status text NOT NULL,
  project_sponsor_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
  property_manager_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
  planning_permission_id text REFERENCES sw_property.planning_permission(planning_permission_id) DEFERRABLE INITIALLY DEFERRED,
  project_start_tick bigint,
  project_completion_tick bigint,
  construction_activity_started boolean NOT NULL,
  financial_commitments_created boolean NOT NULL,
  project_history_basis text NOT NULL,
  source_dataset text NOT NULL
);
CREATE TABLE sw_property.development_control_rule (
  development_control_rule_id text PRIMARY KEY,
  regulated_site_profile text NOT NULL,
  permitted_use_class text NOT NULL,
  mandatory_assessment_topics text[] NOT NULL,
  rule_status text NOT NULL,
  effective_tick bigint NOT NULL,
  fictional_code text NOT NULL,
  source_dataset text NOT NULL
);
CREATE INDEX lawful_use_property_premises_idx ON sw_property.lawful_use_certificate(property_id,premises_id);
CREATE INDEX building_control_building_idx ON sw_property.building_control_case(building_id);
CREATE INDEX building_inspection_due_idx ON sw_property.building_inspection_schedule(priority,next_due_tick);
CREATE INDEX development_project_property_status_idx ON sw_property.development_project(property_id,project_status);
COMMIT;
