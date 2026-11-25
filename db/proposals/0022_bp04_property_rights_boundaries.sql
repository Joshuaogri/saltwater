-- BP04 phase 10: property rights, boundary evidence and legal access indexes.
BEGIN;
CREATE TABLE sw_property.property_rights_schedule (
 property_rights_schedule_id text PRIMARY KEY,
 property_id text NOT NULL UNIQUE REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 title_register_id text NOT NULL REFERENCES sw_property.property_title_register(title_register_id) DEFERRABLE INITIALLY DEFERRED,
 registered_ownership_interest_id text NOT NULL REFERENCES sw_property.ownership_interest(ownership_interest_id) DEFERRABLE INITIALLY DEFERRED,
 registered_owner_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 current_contractual_right_count integer NOT NULL,
 historical_contractual_right_count integer NOT NULL,
 right_class_coverage text[] NOT NULL,
 unverified_right_classes text[] NOT NULL,
 schedule_status text NOT NULL,
 legal_search_required_before_disposition_or_works boolean NOT NULL,
 source_dataset text NOT NULL
);
CREATE TABLE sw_property.contractual_rights_index (
 property_right_id text PRIMARY KEY,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 premises_id text REFERENCES sw_property.premises(premises_id) DEFERRABLE INITIALLY DEFERRED,
 unit_id text REFERENCES sw_property.unit_space(unit_id) DEFERRABLE INITIALLY DEFERRED,
 right_type text NOT NULL,
 holder_business_id text REFERENCES sw_property.business(business_id) DEFERRABLE INITIALLY DEFERRED,
 grantor_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 managing_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 source_agreement_id text NOT NULL REFERENCES sw_property.occupancy_agreement(agreement_id) DEFERRABLE INITIALLY DEFERRED,
 commencement_year integer, expiry_year integer, right_status text NOT NULL,
 permitted_use text NOT NULL, source_of_truth text NOT NULL,
 new_legal_instrument_created boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.boundary_evidence_register (
 boundary_evidence_id text PRIMARY KEY,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 title_register_id text NOT NULL REFERENCES sw_property.property_title_register(title_register_id) DEFERRABLE INITIALLY DEFERRED,
 source_parcel_id text, source_geometry_ref text NOT NULL,
 geometry_present boolean NOT NULL, evidence_class text NOT NULL,
 survey_status text NOT NULL, legal_boundary_status text NOT NULL,
 coordinates_reproduced boolean NOT NULL, boundary_dispute_status text NOT NULL,
 adjoining_owner_consent_status text NOT NULL, boundary_change_event_count integer NOT NULL,
 source_dataset text NOT NULL
);
CREATE TABLE sw_property.physical_access_evidence_register (
 physical_access_evidence_id text PRIMARY KEY,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 building_id text REFERENCES sw_property.building(building_id) DEFERRABLE INITIALLY DEFERRED,
 access_point_id text NOT NULL REFERENCES sw_property.access_point(access_point_id) DEFERRABLE INITIALLY DEFERRED,
 constructed_route_id text REFERENCES sw_property.access_route(route_id) DEFERRABLE INITIALLY DEFERRED,
 road_id text, physical_connection_status text NOT NULL, access_type text NOT NULL,
 access_modes text[] NOT NULL, legal_right_of_way_status text NOT NULL,
 easement_or_wayleave_instrument_id text,
 frontage_or_proximity_is_not_legal_access boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.utility_wayleave_requirement (
 utility_wayleave_requirement_id text PRIMARY KEY,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 utility_connection_id text NOT NULL REFERENCES sw_property.utility_connection(utility_connection_id) DEFERRABLE INITIALLY DEFERRED,
 utility_type text NOT NULL,
 provider_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 connection_status text NOT NULL, wayleave_or_easement_instrument_id text,
 legal_route_right_status text NOT NULL,
 operational_connection_is_not_proof_of_property_right boolean NOT NULL, source_dataset text NOT NULL
);
CREATE TABLE sw_property.registered_property_instrument (
 instrument_id text PRIMARY KEY,
 property_id text NOT NULL REFERENCES sw_property.property_site(property_id) DEFERRABLE INITIALLY DEFERRED,
 instrument_type text NOT NULL, grantor_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 grantee_organisation_id text REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
 instrument_status text NOT NULL, source_reference text, evidence_summary text,
 source_dataset text NOT NULL
);
CREATE TABLE sw_property.future_instrument_template (
 instrument_type text PRIMARY KEY, minimum_evidence text NOT NULL,
 creation_policy text NOT NULL, default_status text NOT NULL, source_dataset text NOT NULL
);
CREATE INDEX contractual_rights_property_idx ON sw_property.contractual_rights_index(property_id,right_status);
CREATE INDEX physical_access_property_idx ON sw_property.physical_access_evidence_register(property_id,access_point_id);
CREATE INDEX utility_wayleave_property_idx ON sw_property.utility_wayleave_requirement(property_id,utility_type);
COMMIT;
