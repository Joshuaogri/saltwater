-- BP02 operational gameplay geography, independent of the global/BP04 ledger.
-- Stable source identifiers are primary keys; geometry is local fictional JSON,
-- avoiding PostGIS overhead and any real-world coordinate interpretation.
BEGIN;
CREATE TABLE sw_geo.bp02_release (
  release_id text PRIMARY KEY,
  source_dataset text NOT NULL,
  package_sha256 char(64) NOT NULL CHECK (rtrim(package_sha256) ~ '^[0-9a-f]{64}$'),
  source_hashes jsonb NOT NULL CHECK (jsonb_typeof(source_hashes)='object'),
  gameplay_release_accepted boolean NOT NULL CHECK (gameplay_release_accepted),
  production_seed_approved boolean NOT NULL DEFAULT false,
  record_counts jsonb NOT NULL CHECK (jsonb_typeof(record_counts)='object'),
  imported_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE TABLE sw_geo.bp02_district (
  source_id text PRIMARY KEY,
  name text NOT NULL,
  bounds jsonb NOT NULL,
  record jsonb NOT NULL
);
CREATE TABLE sw_geo.bp02_neighbourhood (
  source_id text PRIMARY KEY,
  district_source_id text NOT NULL REFERENCES sw_geo.bp02_district(source_id),
  name text NOT NULL,
  geometry jsonb NOT NULL,
  record jsonb NOT NULL
);
CREATE TABLE sw_geo.bp02_feature (
  source_id text PRIMARY KEY,
  entity_type text NOT NULL,
  name text NOT NULL,
  geometry jsonb NOT NULL,
  properties jsonb NOT NULL
);
CREATE TABLE sw_geo.bp02_road (
  source_id text PRIMARY KEY,
  name text NOT NULL,
  road_class text NOT NULL,
  record jsonb NOT NULL
);
CREATE TABLE sw_geo.bp02_node (
  source_id text PRIMARY KEY,
  x numeric NOT NULL,
  y numeric NOT NULL,
  degree smallint NOT NULL CHECK (degree >= 0),
  node_kind text NOT NULL,
  record jsonb NOT NULL
);
CREATE TABLE sw_geo.bp02_segment (
  source_id text PRIMARY KEY,
  road_source_id text NOT NULL REFERENCES sw_geo.bp02_road(source_id),
  from_node_source_id text NOT NULL REFERENCES sw_geo.bp02_node(source_id),
  to_node_source_id text NOT NULL REFERENCES sw_geo.bp02_node(source_id),
  length_m numeric NOT NULL CHECK (length_m > 0),
  geometry jsonb NOT NULL,
  road_class text NOT NULL,
  segment_kind text NOT NULL,
  direction text NOT NULL,
  modes jsonb NOT NULL,
  access text NOT NULL,
  surface text NOT NULL,
  water_crossing boolean NOT NULL DEFAULT false,
  record jsonb NOT NULL,
  CHECK (from_node_source_id <> to_node_source_id)
);
CREATE TABLE sw_geo.bp02_route (
  source_id text PRIMARY KEY,
  name text NOT NULL,
  route_type text NOT NULL,
  record jsonb NOT NULL
);
CREATE TABLE sw_geo.bp02_route_node (
  route_source_id text NOT NULL REFERENCES sw_geo.bp02_route(source_id) ON DELETE CASCADE,
  sequence_no integer NOT NULL CHECK (sequence_no > 0),
  node_source_id text NOT NULL REFERENCES sw_geo.bp02_node(source_id),
  PRIMARY KEY (route_source_id, sequence_no)
);
CREATE TABLE sw_geo.bp02_route_segment (
  route_source_id text NOT NULL REFERENCES sw_geo.bp02_route(source_id) ON DELETE CASCADE,
  sequence_no integer NOT NULL CHECK (sequence_no > 0),
  segment_source_id text NOT NULL REFERENCES sw_geo.bp02_segment(source_id),
  PRIMARY KEY (route_source_id, sequence_no)
);
-- Property/address/access records remain explicitly in-game and retain full
-- source payloads. Their presence does not grant any production seed authority.
CREATE TABLE sw_geo.bp02_parcel (
  source_id text PRIMARY KEY,
  operational_status text NOT NULL CHECK (operational_status='ACTIVE_IN_GAME'),
  record jsonb NOT NULL
);
CREATE TABLE sw_geo.bp02_address (
  source_id text PRIMARY KEY,
  parcel_source_id text NOT NULL,
  operational_status text NOT NULL CHECK (operational_status='ACTIVE_IN_GAME'),
  record jsonb NOT NULL
);
CREATE TABLE sw_geo.bp02_access_point (
  source_id text PRIMARY KEY,
  operational_status text NOT NULL CHECK (operational_status='ACTIVE_IN_GAME'),
  record jsonb NOT NULL
);
CREATE TABLE sw_geo.bp02_bridge_connector (
  source_id text PRIMARY KEY,
  operational_status text NOT NULL CHECK (operational_status='ACTIVE_IN_GAME'),
  engineering_assessment_id text NOT NULL,
  record jsonb NOT NULL
);
CREATE INDEX bp02_neighbourhood_district_idx ON sw_geo.bp02_neighbourhood(district_source_id);
CREATE INDEX bp02_segment_road_idx ON sw_geo.bp02_segment(road_source_id);
CREATE INDEX bp02_segment_from_node_idx ON sw_geo.bp02_segment(from_node_source_id);
CREATE INDEX bp02_segment_to_node_idx ON sw_geo.bp02_segment(to_node_source_id);
CREATE INDEX bp02_route_node_node_idx ON sw_geo.bp02_route_node(node_source_id);
CREATE INDEX bp02_route_segment_segment_idx ON sw_geo.bp02_route_segment(segment_source_id);
CREATE INDEX bp02_address_parcel_idx ON sw_geo.bp02_address(parcel_source_id);
COMMIT;
