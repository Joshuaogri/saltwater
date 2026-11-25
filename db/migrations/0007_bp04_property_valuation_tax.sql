-- BP04 phase 5: condition, valuation, insurance exposure and property tax assessment.
-- Production migration candidate; validate on disposable PostgreSQL before production application.
BEGIN;
CREATE TABLE sw_property.property_condition_assessment (
 condition_assessment_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 assessment_scope text, condition_grade text NOT NULL, observed_risk_profiles text[],
 gross_floor_area_sqm numeric, system_count integer, open_defect_count integer, critical_defect_count integer,
 assessment_tick bigint, evidence_basis text, follow_up_required boolean NOT NULL, source_dataset text NOT NULL
);
CREATE INDEX property_condition_property_idx ON sw_property.property_condition_assessment(property_id);
CREATE TABLE sw_property.land_valuation (
 land_valuation_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 valuation_basis text, land_use_profile text, site_area_sqm numeric, rate_per_sqm_swc bigint,
 assessed_land_value_swc bigint NOT NULL, valuation_tick bigint, valuation_status text, source_dataset text NOT NULL
);
CREATE TABLE sw_property.improvement_valuation (
 improvement_valuation_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 building_use text, gross_floor_area_sqm numeric, construction_quality_profile text,
 replacement_value_swc bigint NOT NULL, depreciation_profile text, valuation_tick bigint, source_dataset text NOT NULL
);
CREATE TABLE sw_property.asset_valuation (
 asset_valuation_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 land_valuation_id text NOT NULL REFERENCES sw_property.land_valuation(land_valuation_id) DEFERRABLE INITIALLY DEFERRED,
 improvement_valuation_id text REFERENCES sw_property.improvement_valuation(improvement_valuation_id) DEFERRABLE INITIALLY DEFERRED,
 valuation_purpose text, currency text NOT NULL, assessed_value_swc bigint NOT NULL, value_band text, valuation_method text,
 valuation_tick bigint, valuation_status text, source_dataset text NOT NULL
);
CREATE INDEX asset_valuation_property_idx ON sw_property.asset_valuation(property_id);
CREATE TABLE sw_property.premises_valuation (
 premises_valuation_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 premises_id text NOT NULL REFERENCES sw_property.premises(premises_id) DEFERRABLE INITIALLY DEFERRED,
 valuation_basis text, assessed_value_swc bigint NOT NULL, value_band text, valuation_tick bigint, source_dataset text NOT NULL
);
CREATE TABLE sw_property.insurer_profile (
 organisation_id text PRIMARY KEY REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 display_name text NOT NULL, organisation_type text NOT NULL, status text, fictional_entity boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.insurance_policy (
 insurance_policy_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 policyholder_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 insured_property_manager_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 insurer_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 policy_type text, policy_status text, effective_tick bigint, renewal_interval_days integer, currency text,
 sum_insured_swc bigint NOT NULL, deductible_band text, premium_calculation text, claim_history text, source_dataset text NOT NULL
);
CREATE INDEX insurance_policy_property_idx ON sw_property.insurance_policy(property_id);
CREATE TABLE sw_property.insurance_coverage (
 coverage_id text PRIMARY KEY, insurance_policy_id text NOT NULL REFERENCES sw_property.insurance_policy(insurance_policy_id) DEFERRABLE INITIALLY DEFERRED,
 coverage_type text, limit_swc bigint NOT NULL, coverage_state text, source_dataset text NOT NULL
);
CREATE TABLE sw_property.property_risk (
 property_risk_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 insurance_policy_id text NOT NULL REFERENCES sw_property.insurance_policy(insurance_policy_id) DEFERRABLE INITIALLY DEFERRED,
 risk_profile text, risk_factors text[], mitigation_links text[], risk_review_interval_days integer, review_status text, source_dataset text NOT NULL
);
CREATE TABLE sw_property.property_tax_assessment (
 property_tax_assessment_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 liable_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 tax_year integer NOT NULL, tax_base_swc bigint NOT NULL, tax_rate_basis_points integer NOT NULL,
 assessed_annual_tax_swc bigint NOT NULL, assessment_status text NOT NULL, appeal_status text,
 assessment_tick bigint, currency text NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.tax_exemption_review (
 tax_exemption_review_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 review_state text, exemption_reason text, effective_tax_year integer, source_dataset text NOT NULL
);
CREATE TABLE sw_property.property_tax_rule (
 tax_rule_id text PRIMARY KEY, tax_year integer NOT NULL, rule_type text, currency text NOT NULL,
 collection_cycle text, billing_and_payment_authority text, effective_tick bigint, fictional_rule boolean NOT NULL,
 source_dataset text NOT NULL
);
COMMIT;
