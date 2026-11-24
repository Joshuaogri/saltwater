-- BP04-03 Stage D detailed parcel dossier and spatial relationship candidate records.
-- Disposable PostgreSQL 16 implementation candidate; no Neon/production operation.
BEGIN;

CREATE TABLE sw_geo.parcel_dossier (
  parcel_spatial_id integer NOT NULL,
  version_no smallint NOT NULL,
  geometry_sha256 bytea NOT NULL CHECK (octet_length(geometry_sha256)=32),
  source_manifest_sha256 bytea NOT NULL CHECK (octet_length(source_manifest_sha256)=32),
  perimeter_m numeric(14,3) NOT NULL CHECK (perimeter_m > 0),
  compactness_index numeric(10,8) NOT NULL CHECK (compactness_index > 0 AND compactness_index <= 1.000001),
  centroid_x_m numeric(14,6) NOT NULL,
  centroid_y_m numeric(14,6) NOT NULL,
  label_point_x_m numeric(14,6) NOT NULL,
  label_point_y_m numeric(14,6) NOT NULL,
  bounds_min_x_m numeric(14,6) NOT NULL,
  bounds_min_y_m numeric(14,6) NOT NULL,
  bounds_max_x_m numeric(14,6) NOT NULL,
  bounds_max_y_m numeric(14,6) NOT NULL,
  exterior_vertex_count integer NOT NULL CHECK (exterior_vertex_count >= 3),
  interior_ring_count integer NOT NULL CHECK (interior_ring_count >= 0),
  road_frontage_length_m numeric(14,3) NOT NULL CHECK (road_frontage_length_m >= 0),
  frontage_segment_count integer NOT NULL CHECK (frontage_segment_count >= 0),
  frontage_candidate_count integer NOT NULL CHECK (frontage_candidate_count >= 0),
  water_boundary_contact_length_m numeric(14,3) NOT NULL CHECK (water_boundary_contact_length_m >= 0),
  adjacent_water_feature_count integer NOT NULL CHECK (adjacent_water_feature_count >= 0),
  frontage_review_status text NOT NULL CHECK (frontage_review_status IN
    ('REVIEW_REQUIRED','NO_ROAD_EDGE_CONTACT_REVIEW_REQUIRED')),
  geometry_review_status text NOT NULL CHECK (geometry_review_status='VALID_GENERATED_CANDIDATE'),
  measurement_basis text NOT NULL CHECK (measurement_basis='DERIVED_FROM_GENERATED_POLYGON_GEOMETRY'),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  PRIMARY KEY(parcel_spatial_id,version_no),
  FOREIGN KEY(parcel_spatial_id,version_no)
    REFERENCES sw_geo.parcel_profile(parcel_spatial_id,version_no),
  CHECK (bounds_max_x_m > bounds_min_x_m AND bounds_max_y_m > bounds_min_y_m)
);
CREATE INDEX parcel_dossier_frontage_idx
  ON sw_geo.parcel_dossier(frontage_review_status,road_frontage_length_m);
CREATE INDEX parcel_dossier_water_idx
  ON sw_geo.parcel_dossier(adjacent_water_feature_count,water_boundary_contact_length_m);

CREATE TABLE sw_geo.parcel_frontage_candidate (
  parcel_spatial_id integer NOT NULL,
  version_no smallint NOT NULL,
  frontage_candidate_id text NOT NULL CHECK (length(btrim(frontage_candidate_id)) BETWEEN 1 AND 180),
  road_segment_ids text[] NOT NULL CHECK (cardinality(road_segment_ids) > 0),
  road_id text NOT NULL CHECK (length(btrim(road_id)) BETWEEN 1 AND 80),
  road_name text NOT NULL CHECK (length(btrim(road_name)) BETWEEN 1 AND 160),
  road_class text NOT NULL CHECK (road_class IN ('local_street','district_connector','primary_arterial','bridge')),
  contact_length_m numeric(14,3) NOT NULL CHECK (contact_length_m > 0),
  candidate_point_x_m numeric(14,6) NOT NULL,
  candidate_point_y_m numeric(14,6) NOT NULL,
  review_status text NOT NULL CHECK (review_status='UNREVIEWED_GEOMETRIC_CONTACT'),
  source_manifest_sha256 bytea NOT NULL CHECK (octet_length(source_manifest_sha256)=32),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  PRIMARY KEY(parcel_spatial_id,version_no,frontage_candidate_id),
  FOREIGN KEY(parcel_spatial_id,version_no)
    REFERENCES sw_geo.parcel_dossier(parcel_spatial_id,version_no)
);
CREATE INDEX parcel_frontage_road_idx
  ON sw_geo.parcel_frontage_candidate(road_id,frontage_candidate_id);

CREATE TABLE sw_geo.parcel_access_location_candidate (
  access_candidate_id text PRIMARY KEY CHECK (length(btrim(access_candidate_id)) BETWEEN 1 AND 160),
  parcel_spatial_id integer NOT NULL,
  version_no smallint NOT NULL,
  frontage_candidate_id text NOT NULL,
  candidate_x_m numeric(14,6) NOT NULL,
  candidate_y_m numeric(14,6) NOT NULL,
  candidate_type text NOT NULL CHECK (candidate_type='unclassified_access_location'),
  review_status text NOT NULL CHECK (review_status='UNREVIEWED_GEOMETRIC_CANDIDATE'),
  source_manifest_sha256 bytea NOT NULL CHECK (octet_length(source_manifest_sha256)=32),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE(parcel_spatial_id,version_no,frontage_candidate_id),
  FOREIGN KEY(parcel_spatial_id,version_no,frontage_candidate_id)
    REFERENCES sw_geo.parcel_frontage_candidate(parcel_spatial_id,version_no,frontage_candidate_id)
);
CREATE INDEX parcel_access_candidate_location_idx
  ON sw_geo.parcel_access_location_candidate(candidate_x_m,candidate_y_m);

CREATE TABLE sw_geo.parcel_adjacency_candidate (
  left_parcel_spatial_id integer NOT NULL,
  left_version_no smallint NOT NULL,
  right_parcel_spatial_id integer NOT NULL,
  right_version_no smallint NOT NULL,
  left_neighbourhood_spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  right_neighbourhood_spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  relationship_code text NOT NULL CHECK (relationship_code IN
    ('SHARED_BOUNDARY_CANDIDATE','CORNER_TOUCH_CANDIDATE')),
  shared_boundary_length_m numeric(14,3) NOT NULL CHECK (shared_boundary_length_m >= 0),
  source_manifest_sha256 bytea NOT NULL CHECK (octet_length(source_manifest_sha256)=32),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  PRIMARY KEY(left_parcel_spatial_id,left_version_no,right_parcel_spatial_id,right_version_no),
  FOREIGN KEY(left_parcel_spatial_id,left_version_no)
    REFERENCES sw_geo.parcel_dossier(parcel_spatial_id,version_no),
  FOREIGN KEY(right_parcel_spatial_id,right_version_no)
    REFERENCES sw_geo.parcel_dossier(parcel_spatial_id,version_no),
  CHECK (left_parcel_spatial_id < right_parcel_spatial_id),
  CHECK (
    (relationship_code='SHARED_BOUNDARY_CANDIDATE' AND shared_boundary_length_m > 0)
    OR (relationship_code='CORNER_TOUCH_CANDIDATE' AND shared_boundary_length_m=0)
  )
);
CREATE INDEX parcel_adjacency_right_idx
  ON sw_geo.parcel_adjacency_candidate(right_parcel_spatial_id,right_version_no);
CREATE INDEX parcel_adjacency_neighbourhood_idx
  ON sw_geo.parcel_adjacency_candidate(left_neighbourhood_spatial_id,right_neighbourhood_spatial_id);

CREATE TABLE sw_geo.parcel_water_adjacency_candidate (
  parcel_spatial_id integer NOT NULL,
  version_no smallint NOT NULL,
  water_feature_id text NOT NULL CHECK (length(btrim(water_feature_id)) BETWEEN 1 AND 100),
  contact_length_m numeric(14,3) NOT NULL CHECK (contact_length_m > 0),
  source_manifest_sha256 bytea NOT NULL CHECK (octet_length(source_manifest_sha256)=32),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  PRIMARY KEY(parcel_spatial_id,version_no,water_feature_id),
  FOREIGN KEY(parcel_spatial_id,version_no)
    REFERENCES sw_geo.parcel_dossier(parcel_spatial_id,version_no)
);
CREATE INDEX parcel_water_adjacency_feature_idx
  ON sw_geo.parcel_water_adjacency_candidate(water_feature_id);

CREATE TRIGGER parcel_dossier_immutable
BEFORE UPDATE OR DELETE ON sw_geo.parcel_dossier
FOR EACH ROW EXECUTE FUNCTION sw_geo.reject_candidate_record_mutation();
CREATE TRIGGER parcel_frontage_candidate_immutable
BEFORE UPDATE OR DELETE ON sw_geo.parcel_frontage_candidate
FOR EACH ROW EXECUTE FUNCTION sw_geo.reject_candidate_record_mutation();
CREATE TRIGGER parcel_access_candidate_immutable
BEFORE UPDATE OR DELETE ON sw_geo.parcel_access_location_candidate
FOR EACH ROW EXECUTE FUNCTION sw_geo.reject_candidate_record_mutation();
CREATE TRIGGER parcel_adjacency_candidate_immutable
BEFORE UPDATE OR DELETE ON sw_geo.parcel_adjacency_candidate
FOR EACH ROW EXECUTE FUNCTION sw_geo.reject_candidate_record_mutation();
CREATE TRIGGER parcel_water_adjacency_candidate_immutable
BEFORE UPDATE OR DELETE ON sw_geo.parcel_water_adjacency_candidate
FOR EACH ROW EXECUTE FUNCTION sw_geo.reject_candidate_record_mutation();

REVOKE INSERT,UPDATE,DELETE,TRUNCATE ON
  sw_geo.parcel_dossier,sw_geo.parcel_frontage_candidate,
  sw_geo.parcel_access_location_candidate,sw_geo.parcel_adjacency_candidate,
  sw_geo.parcel_water_adjacency_candidate
FROM PUBLIC;
GRANT SELECT ON
  sw_geo.parcel_dossier,sw_geo.parcel_frontage_candidate,
  sw_geo.parcel_access_location_candidate,sw_geo.parcel_adjacency_candidate,
  sw_geo.parcel_water_adjacency_candidate
TO PUBLIC;

COMMIT;
