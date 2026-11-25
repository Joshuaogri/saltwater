-- BP04-03 Stage E: persistent, provenance-bearing access connector candidates.
-- Geometry-only candidates; never imply a constructed path or lawful/operational access.
BEGIN;

CREATE TABLE sw_property.access_connector_candidate (
  access_connector_candidate_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  batch_id bigint NOT NULL REFERENCES sw_property.asset_generation_batch(batch_id),
  access_point_id bigint NOT NULL REFERENCES sw_property.access_point(access_point_id),
  candidate_connector_id text NOT NULL UNIQUE
    CHECK (length(btrim(candidate_connector_id)) BETWEEN 1 AND 180),
  candidate_access_point_id text NOT NULL
    CHECK (length(btrim(candidate_access_point_id)) BETWEEN 1 AND 180),
  road_access_candidate_id text NOT NULL
    CHECK (length(btrim(road_access_candidate_id)) BETWEEN 1 AND 180),
  frontage_candidate_id text,
  road_connection_candidate_id text,
  road_id text NOT NULL CHECK (length(btrim(road_id)) BETWEEN 1 AND 120),
  road_segment_ids text[] NOT NULL CHECK (cardinality(road_segment_ids)>=1),
  connector_type text NOT NULL CHECK (connector_type IN (
    'BUILDING_TO_FRONTAGE_CANDIDATE',
    'BUILDING_TO_ROAD_RESERVE_PROXIMITY_CANDIDATE'
  )),
  contact_type text NOT NULL CHECK (contact_type IN (
    'FRONTAGE_CANDIDATE','POINT_CONTACT_ONLY','NEAREST_EDGE_PROXIMITY_NOT_FRONTAGE'
  )),
  length_m numeric(14,3) NOT NULL CHECK (length_m>=0),
  coordinate_reference text NOT NULL,
  geometry_payload jsonb NOT NULL CHECK (
    jsonb_typeof(geometry_payload)='object'
    AND geometry_payload->>'type'='LineString'
    AND jsonb_typeof(geometry_payload->'coordinates')='array'
    AND jsonb_array_length(geometry_payload->'coordinates')>=2
  ),
  geometry_sha256 bytea NOT NULL CHECK (octet_length(geometry_sha256)=32),
  source_manifest_sha256 bytea NOT NULL CHECK (octet_length(source_manifest_sha256)=32),
  geometry_status text NOT NULL CHECK (geometry_status='UNREVIEWED_GEOMETRIC_LINE_ONLY'),
  review_status text NOT NULL CHECK (review_status='unreviewed_candidate'),
  constructed_state text NOT NULL CHECK (constructed_state='unknown'),
  surface_code text NOT NULL CHECK (surface_code='unknown'),
  slope_state text NOT NULL CHECK (slope_state='not_assessed'),
  barrier_state text NOT NULL CHECK (barrier_state='not_assessed'),
  pedestrian_suitability text NOT NULL CHECK (pedestrian_suitability='not_assessed'),
  vehicle_suitability text NOT NULL CHECK (vehicle_suitability='not_assessed'),
  accessibility_state text NOT NULL CHECK (accessibility_state='not_assessed'),
  legal_access_state text NOT NULL CHECK (legal_access_state='not_assessed'),
  public_access_state text NOT NULL CHECK (public_access_state='not_assessed'),
  emergency_egress_state text NOT NULL CHECK (emergency_egress_state='not_assessed'),
  source_ref text NOT NULL, actor_ref text NOT NULL,
  confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  reason text NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE(batch_id,access_point_id),
  CHECK (
    (connector_type='BUILDING_TO_FRONTAGE_CANDIDATE'
      AND frontage_candidate_id IS NOT NULL
      AND road_connection_candidate_id IS NULL
      AND contact_type='FRONTAGE_CANDIDATE')
    OR
    (connector_type='BUILDING_TO_ROAD_RESERVE_PROXIMITY_CANDIDATE'
      AND frontage_candidate_id IS NULL
      AND road_connection_candidate_id IS NOT NULL
      AND contact_type IN ('POINT_CONTACT_ONLY','NEAREST_EDGE_PROXIMITY_NOT_FRONTAGE'))
  )
);
CREATE INDEX access_connector_candidate_batch_idx
  ON sw_property.access_connector_candidate(batch_id,connector_type);
CREATE INDEX access_connector_candidate_access_point_idx
  ON sw_property.access_connector_candidate(access_point_id);

CREATE FUNCTION sw_property.reject_access_connector_candidate_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'BP04-03 access connector candidates are append-only';
END
$$;
CREATE TRIGGER access_connector_candidate_append_only
BEFORE UPDATE OR DELETE ON sw_property.access_connector_candidate
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_access_connector_candidate_mutation();

REVOKE ALL ON TABLE sw_property.access_connector_candidate
  FROM PUBLIC,sw_game_command,sw_game_readonly;
GRANT SELECT ON TABLE sw_property.access_connector_candidate TO sw_game_readonly;
REVOKE ALL ON SEQUENCE sw_property.access_connector_candidate_access_connector_candidate_id_seq
  FROM PUBLIC,sw_game_command,sw_game_readonly;

INSERT INTO sw_ops.storage_operation(operation_kind,description,status,measurement_notes)
VALUES('migration','0017 BP04-03 access connector candidate records','succeeded',
 'Disposable PostgreSQL 16 validation only. Stores 768 provenance-bearing geometric connector candidates with explicit unknown/not-assessed physical and legal attributes. No Neon production write or operational access activation.');
COMMIT;
