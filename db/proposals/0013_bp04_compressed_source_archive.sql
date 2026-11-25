-- BP04 canonical property-stack relational model, phase 1.
-- DISPOSABLE PostgreSQL 16 benchmark only. Never apply to production Neon.
-- Stable Saltwater source IDs are primary keys; no surrogate-ID translation is needed.
BEGIN;
CREATE SCHEMA IF NOT EXISTS sw_property;

CREATE TABLE sw_property.organisation (
  organisation_id text PRIMARY KEY,
  display_name text NOT NULL,
  organisation_type text NOT NULL,
  registered_city text,
  status text,
  source_dataset text NOT NULL
);

CREATE TABLE sw_property.property_site (
  property_id text PRIMARY KEY,
  display_name text NOT NULL,
  district_id text,
  neighbourhood_id text,
  address_id text,
  site_area_m2 numeric,
  use_class text,
  lifecycle_status text,
  source_dataset text NOT NULL
);
CREATE TABLE sw_property.street_address (
  address_id text PRIMARY KEY,
  property_id text NOT NULL UNIQUE REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  display_name text,
  road_id text,
  house_number text,
  postcode text,
  source_dataset text NOT NULL
);
ALTER TABLE sw_property.property_site ADD CONSTRAINT property_site_address_fk
  FOREIGN KEY(address_id) REFERENCES sw_property.street_address(address_id)
  DEFERRABLE INITIALLY DEFERRED;

CREATE TABLE sw_property.building (
  building_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  display_name text NOT NULL,
  building_use text,
  storeys integer CHECK (storeys IS NULL OR storeys >= 0),
  gross_floor_area_m2 numeric CHECK (gross_floor_area_m2 IS NULL OR gross_floor_area_m2 >= 0),
  construction_year integer,
  lifecycle_status text,
  source_dataset text NOT NULL
);
CREATE INDEX building_property_idx ON sw_property.building(property_id);

CREATE TABLE sw_property.premises (
  premises_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  building_id text REFERENCES sw_property.building(building_id)
    DEFERRABLE INITIALLY DEFERRED,
  display_name text NOT NULL,
  premises_use text,
  floor_name text,
  lifecycle_status text,
  source_dataset text NOT NULL,
  CHECK (building_id IS NOT NULL OR property_id IS NOT NULL)
);
CREATE INDEX premises_building_idx ON sw_property.premises(building_id);
CREATE INDEX premises_property_idx ON sw_property.premises(property_id);

CREATE TABLE sw_property.unit_space (
  unit_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  building_id text REFERENCES sw_property.building(building_id)
    DEFERRABLE INITIALLY DEFERRED,
  premises_id text NOT NULL REFERENCES sw_property.premises(premises_id)
    DEFERRABLE INITIALLY DEFERRED,
  display_name text NOT NULL,
  unit_class text,
  use_class text,
  floor_order integer,
  floor_area_m2 numeric CHECK (floor_area_m2 IS NULL OR floor_area_m2 >= 0),
  lifecycle_status text,
  source_dataset text NOT NULL
);
CREATE INDEX unit_property_idx ON sw_property.unit_space(property_id);
CREATE INDEX unit_building_idx ON sw_property.unit_space(building_id);
CREATE INDEX unit_premises_idx ON sw_property.unit_space(premises_id);

CREATE TABLE sw_property.access_point (
  access_point_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  building_id text REFERENCES sw_property.building(building_id)
    DEFERRABLE INITIALLY DEFERRED,
  premises_id text REFERENCES sw_property.premises(premises_id)
    DEFERRABLE INITIALLY DEFERRED,
  unit_id text REFERENCES sw_property.unit_space(unit_id)
    DEFERRABLE INITIALLY DEFERRED,
  display_name text,
  access_type text,
  access_modes text[],
  road_link_road_id text,
  source_dataset text NOT NULL,
  CHECK (num_nonnulls(building_id,premises_id,unit_id) <= 1)
);
CREATE INDEX access_point_property_idx ON sw_property.access_point(property_id);
CREATE INDEX access_point_building_idx ON sw_property.access_point(building_id);

CREATE TABLE sw_property.access_route (
  route_id text PRIMARY KEY,
  access_point_id text NOT NULL REFERENCES sw_property.access_point(access_point_id)
    DEFERRABLE INITIALLY DEFERRED,
  road_id text,
  route_type text,
  access_modes text[],
  route_status text,
  source_dataset text NOT NULL
);
CREATE INDEX access_route_access_point_idx ON sw_property.access_route(access_point_id);

CREATE TABLE sw_property.site_feature (
  site_feature_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  feature_type text,
  display_name text,
  source_dataset text NOT NULL
);
CREATE INDEX site_feature_property_idx ON sw_property.site_feature(property_id);

CREATE TABLE sw_property.building_component (
  component_id text PRIMARY KEY,
  building_id text NOT NULL REFERENCES sw_property.building(building_id)
    DEFERRABLE INITIALLY DEFERRED,
  component_type text,
  display_name text,
  source_dataset text NOT NULL
);
CREATE INDEX building_component_building_idx ON sw_property.building_component(building_id);

CREATE TABLE sw_property.premises_room (
  room_id text PRIMARY KEY,
  premises_id text NOT NULL REFERENCES sw_property.premises(premises_id)
    DEFERRABLE INITIALLY DEFERRED,
  display_name text NOT NULL,
  room_type text,
  floor_name text,
  source_dataset text NOT NULL
);
CREATE INDEX premises_room_parent_idx ON sw_property.premises_room(premises_id);

CREATE TABLE sw_property.ownership_interest (
  ownership_interest_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  owner_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  management_model text,
  interest_type text,
  source_dataset text NOT NULL
);
CREATE INDEX ownership_interest_owner_idx ON sw_property.ownership_interest(owner_organisation_id);

CREATE TABLE sw_property.business (
  business_id text PRIMARY KEY,
  display_name text NOT NULL,
  sector text NOT NULL,
  primary_activity text,
  status text NOT NULL,
  parent_business_id text REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  primary_establishment_id text,
  source_dataset text NOT NULL
);
CREATE INDEX business_sector_status_idx ON sw_property.business(sector,status);

CREATE TABLE sw_property.establishment (
  establishment_id text PRIMARY KEY,
  business_id text NOT NULL REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  property_id text REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  building_id text REFERENCES sw_property.building(building_id)
    DEFERRABLE INITIALLY DEFERRED,
  premises_id text REFERENCES sw_property.premises(premises_id)
    DEFERRABLE INITIALLY DEFERRED,
  unit_id text REFERENCES sw_property.unit_space(unit_id)
    DEFERRABLE INITIALLY DEFERRED,
  display_name text NOT NULL,
  establishment_type text,
  status text,
  source_dataset text NOT NULL
);
CREATE INDEX establishment_business_idx ON sw_property.establishment(business_id);
CREATE INDEX establishment_unit_idx ON sw_property.establishment(unit_id);

ALTER TABLE sw_property.business ADD CONSTRAINT business_primary_establishment_fk
  FOREIGN KEY(primary_establishment_id) REFERENCES sw_property.establishment(establishment_id)
  DEFERRABLE INITIALLY DEFERRED;

CREATE TABLE sw_property.business_unit_link (
  business_unit_link_id text PRIMARY KEY,
  business_id text NOT NULL REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  establishment_id text NOT NULL REFERENCES sw_property.establishment(establishment_id)
    DEFERRABLE INITIALLY DEFERRED,
  unit_id text NOT NULL REFERENCES sw_property.unit_space(unit_id)
    DEFERRABLE INITIALLY DEFERRED,
  premises_id text NOT NULL REFERENCES sw_property.premises(premises_id)
    DEFERRABLE INITIALLY DEFERRED,
  valid_from_tick bigint NOT NULL,
  valid_to_tick bigint,
  occupancy_relationship text,
  occupancy_status text,
  source_dataset text NOT NULL,
  CHECK (valid_to_tick IS NULL OR valid_to_tick > valid_from_tick)
);
CREATE INDEX business_unit_link_business_idx ON sw_property.business_unit_link(business_id);
CREATE INDEX business_unit_link_unit_idx ON sw_property.business_unit_link(unit_id);
CREATE UNIQUE INDEX business_unit_link_current_unit_uq
  ON sw_property.business_unit_link(unit_id) WHERE valid_to_tick IS NULL;

CREATE TABLE sw_property.occupancy_agreement (
  agreement_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  building_id text REFERENCES sw_property.building(building_id)
    DEFERRABLE INITIALLY DEFERRED,
  premises_id text REFERENCES sw_property.premises(premises_id)
    DEFERRABLE INITIALLY DEFERRED,
  unit_id text NOT NULL REFERENCES sw_property.unit_space(unit_id)
    DEFERRABLE INITIALLY DEFERRED,
  landlord_organisation_id text REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  tenant_business_id text REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  operator_business_id text REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  establishment_id text REFERENCES sw_property.establishment(establishment_id)
    DEFERRABLE INITIALLY DEFERRED,
  agreement_type text NOT NULL,
  commencement_year integer,
  expiry_year integer,
  agreement_status text NOT NULL,
  source_dataset text NOT NULL
);
CREATE INDEX occupancy_agreement_unit_idx ON sw_property.occupancy_agreement(unit_id);
CREATE INDEX occupancy_agreement_tenant_idx ON sw_property.occupancy_agreement(tenant_business_id);

CREATE TABLE sw_property.occupancy (
  occupancy_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  building_id text REFERENCES sw_property.building(building_id)
    DEFERRABLE INITIALLY DEFERRED,
  premises_id text REFERENCES sw_property.premises(premises_id)
    DEFERRABLE INITIALLY DEFERRED,
  unit_id text NOT NULL REFERENCES sw_property.unit_space(unit_id)
    DEFERRABLE INITIALLY DEFERRED,
  occupant_business_id text REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  establishment_id text REFERENCES sw_property.establishment(establishment_id)
    DEFERRABLE INITIALLY DEFERRED,
  agreement_id text REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  occupant_type text NOT NULL,
  occupancy_status text NOT NULL,
  effective_from_year integer,
  effective_to_year integer,
  source_dataset text NOT NULL
);
CREATE INDEX occupancy_unit_idx ON sw_property.occupancy(unit_id);
CREATE INDEX occupancy_business_idx ON sw_property.occupancy(occupant_business_id);

CREATE TABLE sw_property.import_release (
  release_id text PRIMARY KEY,
  source_commit text NOT NULL,
  package_sha256 char(64) NOT NULL,
  manifest jsonb NOT NULL CHECK (jsonb_typeof(manifest)='object'),
  imported_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE TABLE sw_property.source_dataset_archive (
  source_sha256 char(64) PRIMARY KEY,
  dataset_id text NOT NULL,
  source_path text NOT NULL,
  compressed_bytes bigint NOT NULL CHECK (compressed_bytes >= 0),
  uncompressed_bytes bigint NOT NULL CHECK (uncompressed_bytes >= 0),
  compressed_payload bytea NOT NULL,
  archived_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (octet_length(compressed_payload)=compressed_bytes)
);

CREATE TABLE sw_property.import_dataset (
  release_id text NOT NULL REFERENCES sw_property.import_release(release_id),
  dataset_id text NOT NULL,
  source_path text NOT NULL,
  source_sha256 char(64) NOT NULL,
  FOREIGN KEY(source_sha256) REFERENCES sw_property.source_dataset_archive(source_sha256),
  compressed_bytes bigint NOT NULL CHECK (compressed_bytes >= 0),
  uncompressed_bytes bigint NOT NULL CHECK (uncompressed_bytes >= 0),
  source_record_count bigint NOT NULL CHECK (source_record_count >= 0),
  loaded_record_count bigint NOT NULL CHECK (loaded_record_count >= 0),
  PRIMARY KEY(release_id,dataset_id),
  FOREIGN KEY(source_sha256) REFERENCES sw_property.source_dataset_archive(source_sha256),
  CHECK (source_record_count=loaded_record_count)
);
COMMIT;
