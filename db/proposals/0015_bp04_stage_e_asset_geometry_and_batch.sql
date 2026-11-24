-- BP04-03 Stage E: candidate site lineage, asset geometry and generation provenance.
-- Disposable PostgreSQL 16 acceptance only. Never apply to Neon or production.
BEGIN;

-- BP04-02 used NOT NULL booleans for two access-point facts. That representation
-- cannot distinguish false from unknown/not assessed. Preserve any existing
-- known boolean facts, then introduce an explicit epistemic state.
ALTER TABLE sw_property.access_point_profile
  ADD COLUMN emergency_egress_state text,
  ADD COLUMN loading_capability_state text;
ALTER TABLE sw_property.access_point_profile
  ALTER COLUMN emergency_egress DROP NOT NULL,
  ALTER COLUMN loading_capable DROP NOT NULL;

ALTER TABLE sw_property.access_point_profile
  DISABLE TRIGGER access_point_profile_append_only;
UPDATE sw_property.access_point_profile
SET emergency_egress_state = CASE WHEN emergency_egress IS TRUE THEN 'known_true' ELSE 'known_false' END,
    loading_capability_state = CASE WHEN loading_capable IS TRUE THEN 'known_true' ELSE 'known_false' END;
ALTER TABLE sw_property.access_point_profile
  ENABLE TRIGGER access_point_profile_append_only;

ALTER TABLE sw_property.access_point_profile
  ALTER COLUMN emergency_egress_state SET DEFAULT 'not_assessed',
  ALTER COLUMN emergency_egress_state SET NOT NULL,
  ALTER COLUMN loading_capability_state SET DEFAULT 'not_assessed',
  ALTER COLUMN loading_capability_state SET NOT NULL,
  ADD CONSTRAINT access_point_emergency_egress_state_check
    CHECK (emergency_egress_state IN ('known_true','known_false','unknown','not_assessed','not_applicable')),
  ADD CONSTRAINT access_point_loading_capability_state_check
    CHECK (loading_capability_state IN ('known_true','known_false','unknown','not_assessed','not_applicable')),
  ADD CONSTRAINT access_point_emergency_egress_value_check
    CHECK (
      (emergency_egress_state='known_true' AND emergency_egress IS TRUE) OR
      (emergency_egress_state='known_false' AND emergency_egress IS FALSE) OR
      (emergency_egress_state IN ('unknown','not_assessed','not_applicable') AND emergency_egress IS NULL)
    ),
  ADD CONSTRAINT access_point_loading_capability_value_check
    CHECK (
      (loading_capability_state='known_true' AND loading_capable IS TRUE) OR
      (loading_capability_state='known_false' AND loading_capable IS FALSE) OR
      (loading_capability_state IN ('unknown','not_assessed','not_applicable') AND loading_capable IS NULL)
    );

CREATE TABLE sw_property.asset_generation_batch (
  batch_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  inventory_set_id text NOT NULL UNIQUE CHECK (length(btrim(inventory_set_id)) BETWEEN 1 AND 120),
  source_dataset text NOT NULL CHECK (length(btrim(source_dataset)) BETWEEN 1 AND 120),
  candidate_set_id text NOT NULL CHECK (length(btrim(candidate_set_id)) BETWEEN 1 AND 120),
  generator_version text NOT NULL CHECK (length(btrim(generator_version)) BETWEEN 1 AND 120),
  coordinate_reference text NOT NULL CHECK (length(btrim(coordinate_reference)) BETWEEN 1 AND 120),
  manifest_sha256 bytea NOT NULL UNIQUE CHECK (octet_length(manifest_sha256)=32),
  candidate_manifest_sha256 bytea NOT NULL CHECK (octet_length(candidate_manifest_sha256)=32),
  dossier_manifest_sha256 bytea NOT NULL CHECK (octet_length(dossier_manifest_sha256)=32),
  source_commit text NOT NULL CHECK (length(btrim(source_commit)) BETWEEN 7 AND 64),
  record_counts jsonb NOT NULL CHECK (jsonb_typeof(record_counts)='object'),
  unresolved_source_mapping_count integer NOT NULL CHECK (unresolved_source_mapping_count>=0),
  operational_approval boolean NOT NULL DEFAULT false CHECK (operational_approval=false),
  source_ref text NOT NULL, actor_ref text NOT NULL, reason text NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX asset_generation_batch_source_idx
  ON sw_property.asset_generation_batch(source_dataset,inventory_set_id);

CREATE TABLE sw_property.property_candidate_site (
  property_candidate_site_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  property_id bigint NOT NULL UNIQUE REFERENCES sw_property.property_asset(property_id),
  batch_id bigint NOT NULL REFERENCES sw_property.asset_generation_batch(batch_id),
  candidate_parcel_id text NOT NULL UNIQUE CHECK (length(btrim(candidate_parcel_id)) BETWEEN 1 AND 120),
  candidate_set_id text NOT NULL CHECK (length(btrim(candidate_set_id)) BETWEEN 1 AND 120),
  candidate_manifest_sha256 bytea NOT NULL CHECK (octet_length(candidate_manifest_sha256)=32),
  dossier_manifest_sha256 bytea NOT NULL CHECK (octet_length(dossier_manifest_sha256)=32),
  review_status text NOT NULL DEFAULT 'unreviewed_candidate'
    CHECK (review_status IN ('unreviewed_candidate','review_required','reviewed_candidate','rejected')),
  source_ref text NOT NULL, actor_ref text NOT NULL,
  confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  reason text NOT NULL, recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX property_candidate_site_batch_idx
  ON sw_property.property_candidate_site(batch_id,candidate_set_id);

CREATE TABLE sw_property.asset_geometry_candidate (
  geometry_candidate_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  batch_id bigint NOT NULL REFERENCES sw_property.asset_generation_batch(batch_id),
  entity_type text NOT NULL CHECK (entity_type IN ('PROPERTY','BUILDING','ACCESS_POINT')),
  entity_id bigint NOT NULL CHECK (entity_id>0),
  version_no integer NOT NULL CHECK (version_no>0),
  geometry_type text NOT NULL CHECK (geometry_type IN ('Polygon','Point')),
  coordinate_reference text NOT NULL CHECK (length(btrim(coordinate_reference)) BETWEEN 1 AND 120),
  geometry_payload jsonb NOT NULL CHECK (jsonb_typeof(geometry_payload)='object'),
  geometry_sha256 bytea NOT NULL CHECK (octet_length(geometry_sha256)=32),
  source_manifest_sha256 bytea NOT NULL CHECK (octet_length(source_manifest_sha256)=32),
  geometry_status text NOT NULL CHECK (geometry_status='generated_design_candidate'),
  source_ref text NOT NULL, actor_ref text NOT NULL,
  confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  reason text NOT NULL, recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE(entity_type,entity_id,version_no),
  CHECK (
    (geometry_type='Polygon' AND geometry_payload->>'type'='Polygon') OR
    (geometry_type='Point' AND geometry_payload->>'type'='Point')
  )
);
CREATE INDEX asset_geometry_candidate_entity_idx
  ON sw_property.asset_geometry_candidate(entity_type,entity_id,version_no DESC);
CREATE INDEX asset_geometry_candidate_batch_idx
  ON sw_property.asset_geometry_candidate(batch_id,entity_type);

CREATE FUNCTION sw_property.guard_asset_geometry_entity()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE ok boolean;
BEGIN
  CASE NEW.entity_type
    WHEN 'PROPERTY' THEN SELECT EXISTS(SELECT 1 FROM sw_property.property_asset WHERE property_id=NEW.entity_id) INTO ok;
    WHEN 'BUILDING' THEN SELECT EXISTS(SELECT 1 FROM sw_property.building WHERE building_id=NEW.entity_id) INTO ok;
    WHEN 'ACCESS_POINT' THEN SELECT EXISTS(SELECT 1 FROM sw_property.access_point WHERE access_point_id=NEW.entity_id) INTO ok;
    ELSE ok:=false;
  END CASE;
  IF NOT ok THEN RAISE EXCEPTION 'asset geometry candidate references a missing or mismatched BP04 identity'; END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER asset_geometry_candidate_entity_guard
BEFORE INSERT ON sw_property.asset_geometry_candidate
FOR EACH ROW EXECUTE FUNCTION sw_property.guard_asset_geometry_entity();

CREATE FUNCTION sw_property.reject_stage_e_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'BP04-03 Stage E candidate batches, links and geometry are append-only';
END
$$;
DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['asset_generation_batch','property_candidate_site','asset_geometry_candidate'] LOOP
    EXECUTE format('CREATE TRIGGER %I_append_only BEFORE UPDATE OR DELETE ON sw_property.%I FOR EACH ROW EXECUTE FUNCTION sw_property.reject_stage_e_mutation()',t,t);
  END LOOP;
END
$$;

GRANT SELECT ON ALL TABLES IN SCHEMA sw_property TO sw_game_readonly;
REVOKE ALL ON TABLE sw_property.asset_generation_batch,
  sw_property.property_candidate_site,sw_property.asset_geometry_candidate
  FROM PUBLIC,sw_game_command,sw_game_readonly;
GRANT SELECT ON TABLE sw_property.asset_generation_batch,
  sw_property.property_candidate_site,sw_property.asset_geometry_candidate
  TO sw_game_readonly;
REVOKE ALL ON SEQUENCE sw_property.asset_generation_batch_batch_id_seq,
  sw_property.property_candidate_site_property_candidate_site_id_seq,
  sw_property.asset_geometry_candidate_geometry_candidate_id_seq
  FROM PUBLIC,sw_game_command,sw_game_readonly;

INSERT INTO sw_ops.storage_operation(operation_kind,description,status,measurement_notes)
VALUES('migration','0015 BP04-03 Stage E asset candidate geometry and batch provenance','succeeded',
 'Disposable PostgreSQL 16 only. Adds property-to-candidate-site lineage, append-only generated asset geometry and batch checksums; corrects access-point boolean epistemic states. No Neon production write.');
COMMIT;
