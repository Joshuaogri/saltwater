-- BP04 phase 9: property title, ownership index and asset lifecycle.
-- Ownership-event facts remain authoritative in SW-PROPERTY-TENURE-V1.
-- Original source collections remain losslessly retained in the gzip archive.
-- Production migration candidate; validate on disposable PostgreSQL before production application.
BEGIN;
CREATE TABLE sw_property.property_title_register (
 title_register_id text PRIMARY KEY, property_id text NOT NULL UNIQUE REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 current_ownership_interest_id text NOT NULL REFERENCES sw_property.ownership_interest(ownership_interest_id) DEFERRABLE INITIALLY DEFERRED,
 registered_proprietor_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 title_status text NOT NULL, tenure_type text NOT NULL, registration_tick bigint NOT NULL, source_basis text NOT NULL,
 boundary_record_id text NOT NULL, active_dispute_count integer NOT NULL, unresolved_title_issue_count integer NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.property_interest_record (
 property_interest_record_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 ownership_interest_id text NOT NULL REFERENCES sw_property.ownership_interest(ownership_interest_id) DEFERRABLE INITIALLY DEFERRED,
 interest_holder_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 interest_type text NOT NULL, interest_status text NOT NULL, priority_order integer NOT NULL, source_basis text NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.property_title_instrument (
 title_instrument_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 title_register_id text NOT NULL REFERENCES sw_property.property_title_register(title_register_id) DEFERRABLE INITIALLY DEFERRED,
 ownership_event_id text NOT NULL UNIQUE, instrument_type text NOT NULL,
 transferor_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 transferee_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 effective_year integer, recorded_year integer, instrument_status text NOT NULL, source_basis text,
 consideration_recorded_as_band_only boolean NOT NULL, payment_or_settlement_record_created boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.property_transaction_index (
 property_transaction_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 title_register_id text NOT NULL REFERENCES sw_property.property_title_register(title_register_id) DEFERRABLE INITIALLY DEFERRED,
 transaction_type text NOT NULL, ownership_event_id text NOT NULL UNIQUE,
 title_instrument_id text NOT NULL REFERENCES sw_property.property_title_instrument(title_instrument_id) DEFERRABLE INITIALLY DEFERRED,
 from_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 to_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 effective_year integer, recorded_year integer, transaction_status text NOT NULL, consideration_band text,
 financial_settlement_status text NOT NULL, source_of_truth text NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.property_lifecycle_event (
 lifecycle_event_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 event_type text NOT NULL, effective_year integer, effective_tick bigint NOT NULL, event_status text NOT NULL,
 title_register_id text REFERENCES sw_property.property_title_register(title_register_id) DEFERRABLE INITIALLY DEFERRED,
 source_record_id text, historical_date_known boolean NOT NULL, financial_transaction_created boolean NOT NULL,
 narrative text NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.building_lifecycle_event (
 lifecycle_event_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text NOT NULL REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 event_type text NOT NULL, effective_year integer, effective_tick bigint NOT NULL, event_status text NOT NULL,
 planning_permission_id text REFERENCES sw_property.planning_permission(planning_permission_id) DEFERRABLE INITIALLY DEFERRED,
 completion_certificate_id text REFERENCES sw_property.completion_certificate(completion_certificate_id) DEFERRABLE INITIALLY DEFERRED,
 historical_construction_contract_created boolean NOT NULL, financial_transaction_created boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.premises_lifecycle_event (
 lifecycle_event_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 premises_id text NOT NULL REFERENCES sw_property.premises(premises_id) DEFERRABLE INITIALLY DEFERRED,
 event_type text NOT NULL, effective_tick bigint NOT NULL, event_status text NOT NULL,
 lawful_use_certificate_id text REFERENCES sw_property.lawful_use_certificate(lawful_use_certificate_id) DEFERRABLE INITIALLY DEFERRED, source_dataset text NOT NULL
);
CREATE TABLE sw_property.property_encumbrance_register (
 encumbrance_register_id text PRIMARY KEY, property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 title_register_id text NOT NULL REFERENCES sw_property.property_title_register(title_register_id) DEFERRABLE INITIALLY DEFERRED,
 recorded_encumbrance_count integer NOT NULL, register_state text NOT NULL, mortgage_or_charge_status text NOT NULL,
 caveat_or_lien_status text NOT NULL, search_required_before_transaction boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.property_lifecycle_action_rule (
 lifecycle_action_type text PRIMARY KEY, action_domain text NOT NULL, mandatory_linkage text NOT NULL,
 runtime_creation_policy text NOT NULL, mutates_canonical_baseline boolean NOT NULL, source_dataset text NOT NULL
);
CREATE INDEX property_title_proprietor_idx ON sw_property.property_title_register(registered_proprietor_organisation_id);
CREATE INDEX property_transaction_history_idx ON sw_property.property_transaction_index(property_id,effective_year,recorded_year);
CREATE INDEX building_lifecycle_history_idx ON sw_property.building_lifecycle_event(building_id,effective_tick);
CREATE INDEX premises_lifecycle_history_idx ON sw_property.premises_lifecycle_event(premises_id,effective_tick);
COMMIT;
