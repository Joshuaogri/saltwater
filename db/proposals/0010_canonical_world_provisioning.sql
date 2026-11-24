-- SW-DB-001 / disposable proposal 0010.
-- Canonical world provisioning candidate; NEVER apply to Neon under this approval.
-- Depends on disposable proposals 0002-0009. No domain rows are seeded here.
BEGIN;

CREATE SCHEMA sw_business;

-- Cross-domain provisioning metadata only. Person and business truth remains in
-- their owning schemas; this table stores immutable batch provenance/counts.
CREATE TABLE sw_ops.world_provisioning_batch (
  batch_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  manifest_sha256 bytea NOT NULL UNIQUE CHECK (octet_length(manifest_sha256)=32),
  generator_version smallint NOT NULL CHECK (generator_version > 0),
  normalizer_version smallint NOT NULL CHECK (normalizer_version=1),
  config_version text NOT NULL CHECK (length(btrim(config_version)) BETWEEN 1 AND 80),
  seed bigint NOT NULL,
  source_revision text NOT NULL CHECK (length(btrim(source_revision)) BETWEEN 7 AND 64),
  expected_residents integer NOT NULL CHECK (expected_residents=9000),
  expected_police_subset integer NOT NULL CHECK (expected_police_subset=500),
  expected_living_people integer NOT NULL CHECK (expected_living_people=9500),
  expected_businesses integer NOT NULL CHECK (expected_businesses>=10000),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (expected_residents + expected_police_subset = expected_living_people),
  CHECK (expected_living_people <= 10000)
);

CREATE FUNCTION sw_ops.reject_provisioning_manifest_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'world provisioning manifests are immutable';
END
$$;
CREATE TRIGGER world_provisioning_manifest_immutable
BEFORE UPDATE OR DELETE ON sw_ops.world_provisioning_batch
FOR EACH ROW EXECUTE FUNCTION sw_ops.reject_provisioning_manifest_mutation();

-- BP-04 distribution/site canon remains open. The business identity deliberately
-- contains no invented category or spatial assignment. Test-only variety lives
-- in the disposable sw_test fixture overlay, never in canonical business fields.
CREATE TABLE sw_business.business (
  business_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  business_code text NOT NULL UNIQUE
    CHECK (business_code ~ '^SWB-[A-Z0-9-]{6,40}$'),
  created_batch_id bigint NOT NULL
    REFERENCES sw_ops.world_provisioning_batch(batch_id),
  operating_status text NOT NULL DEFAULT 'active'
    CHECK (operating_status IN ('active','suspended','closed')),
  site_assignment_status text NOT NULL DEFAULT 'unassigned'
    CHECK (site_assignment_status IN ('unassigned','assigned')),
  primary_spatial_id integer REFERENCES sw_geo.entity(spatial_id),
  created_tick bigint NOT NULL CHECK (created_tick >= 0),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (
    (site_assignment_status='unassigned' AND primary_spatial_id IS NULL)
    OR (site_assignment_status='assigned' AND primary_spatial_id IS NOT NULL)
  )
);
CREATE INDEX business_batch_idx ON sw_business.business(created_batch_id);

CREATE TABLE sw_business.business_history (
  history_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  business_id bigint NOT NULL REFERENCES sw_business.business(business_id),
  event_code text NOT NULL CHECK (event_code IN
    ('registered','status_changed','site_assigned','site_unassigned')),
  old_operating_status text,
  new_operating_status text NOT NULL
    CHECK (new_operating_status IN ('active','suspended','closed')),
  old_site_assignment_status text,
  new_site_assignment_status text NOT NULL
    CHECK (new_site_assignment_status IN ('unassigned','assigned')),
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX business_history_owner_idx
  ON sw_business.business_history(business_id,history_id DESC);

CREATE FUNCTION sw_business.guard_business_update()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.business_id <> OLD.business_id
     OR NEW.business_code <> OLD.business_code
     OR NEW.created_batch_id <> OLD.created_batch_id
     OR NEW.created_tick <> OLD.created_tick
     OR NEW.source_ref <> OLD.source_ref
     OR NEW.created_at <> OLD.created_at THEN
    RAISE EXCEPTION 'business identity, provenance and creation facts are immutable';
  END IF;
  IF NEW.operating_status <> OLD.operating_status THEN
    IF NOT (
      (OLD.operating_status='active' AND NEW.operating_status IN ('suspended','closed'))
      OR (OLD.operating_status='suspended' AND NEW.operating_status IN ('active','closed'))
    ) THEN
      RAISE EXCEPTION 'invalid business operating-status transition';
    END IF;
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER business_update_guard
BEFORE UPDATE ON sw_business.business
FOR EACH ROW EXECUTE FUNCTION sw_business.guard_business_update();

CREATE FUNCTION sw_business.record_business_history()
RETURNS trigger LANGUAGE plpgsql AS $business_history$
BEGIN
  IF TG_OP='INSERT' THEN
    INSERT INTO sw_business.business_history
      (business_id,event_code,old_operating_status,new_operating_status,
       old_site_assignment_status,new_site_assignment_status,effective_tick,
       source_ref,actor_ref,reason)
    VALUES
      (NEW.business_id,'registered',NULL,NEW.operating_status,NULL,
       NEW.site_assignment_status,NEW.created_tick,NEW.source_ref,
       'domain-trigger','business identity registered');
    RETURN NEW;
  END IF;

  IF NEW.operating_status IS DISTINCT FROM OLD.operating_status THEN
    INSERT INTO sw_business.business_history
      (business_id,event_code,old_operating_status,new_operating_status,
       old_site_assignment_status,new_site_assignment_status,effective_tick,
       source_ref,actor_ref,reason)
    VALUES
      (NEW.business_id,'status_changed',OLD.operating_status,NEW.operating_status,
       OLD.site_assignment_status,NEW.site_assignment_status,NEW.created_tick,
       NEW.source_ref,'domain-trigger','business operating status changed');
  END IF;

  IF NEW.site_assignment_status IS DISTINCT FROM OLD.site_assignment_status
     OR NEW.primary_spatial_id IS DISTINCT FROM OLD.primary_spatial_id THEN
    INSERT INTO sw_business.business_history
      (business_id,event_code,old_operating_status,new_operating_status,
       old_site_assignment_status,new_site_assignment_status,effective_tick,
       source_ref,actor_ref,reason)
    VALUES
      (NEW.business_id,
       CASE WHEN NEW.site_assignment_status='assigned'
            THEN 'site_assigned' ELSE 'site_unassigned' END,
       OLD.operating_status,NEW.operating_status,OLD.site_assignment_status,
       NEW.site_assignment_status,NEW.created_tick,NEW.source_ref,
       'domain-trigger','business site assignment changed');
  END IF;
  RETURN NEW;
END
$business_history$;
CREATE TRIGGER business_history_append
AFTER INSERT OR UPDATE OF operating_status,site_assignment_status,primary_spatial_id
ON sw_business.business
FOR EACH ROW EXECUTE FUNCTION sw_business.record_business_history();

CREATE FUNCTION sw_business.reject_business_history_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'business lifecycle history is append-only';
END
$$;
CREATE TRIGGER business_history_immutable
BEFORE UPDATE OR DELETE ON sw_business.business_history
FOR EACH ROW EXECUTE FUNCTION sw_business.reject_business_history_mutation();

CREATE FUNCTION sw_business.reject_business_delete()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'business identities cannot be deleted; use lifecycle transitions';
END
$$;
CREATE TRIGGER business_no_delete
BEFORE DELETE ON sw_business.business
FOR EACH ROW EXECUTE FUNCTION sw_business.reject_business_delete();

CREATE FUNCTION sw_business.require_canonical_name()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_business,sw_names AS $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM sw_names.name_reservation r
    WHERE r.entity_type='BUSINESS'
      AND r.entity_id=NEW.business_id
      AND r.name_form='canonical'
      AND sw_names.latest_status(r.reservation_id)='active'
  ) THEN
    RAISE EXCEPTION 'every business requires one active canonical registry name';
  END IF;
  RETURN NEW;
END
$$;
CREATE CONSTRAINT TRIGGER business_canonical_name_required
AFTER INSERT ON sw_business.business
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION sw_business.require_canonical_name();

-- Extend the universal naming adapter. The existing reserve_name() function
-- remains the only public reservation entry point; this trigger locks and
-- validates the owning business row and enforces the same global namespace.
ALTER TABLE sw_names.name_reservation
  DROP CONSTRAINT name_reservation_entity_type_check;
ALTER TABLE sw_names.name_reservation
  ADD CONSTRAINT name_reservation_entity_type_check
  CHECK (entity_type IN ('GEOGRAPHY','PERSON','BUSINESS'));

CREATE OR REPLACE FUNCTION sw_names.guard_reservation()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_business,sw_core AS $$
DECLARE
  v_code text;
  v_kind smallint;
BEGIN
  IF NEW.normalized_key <> sw_names.normalize_name(NEW.display_name) THEN
    RAISE EXCEPTION 'normalized key does not match the authoritative normalizer';
  END IF;
  IF NEW.entity_type='GEOGRAPHY' THEN
    PERFORM 1 FROM sw_geo.entity WHERE spatial_id=NEW.entity_id FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'geography identity does not exist'; END IF;
  ELSIF NEW.entity_type='PERSON' THEN
    PERFORM 1 FROM sw_people.person WHERE person_id=NEW.entity_id FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'person identity does not exist'; END IF;
  ELSIF NEW.entity_type='BUSINESS' THEN
    PERFORM 1 FROM sw_business.business WHERE business_id=NEW.entity_id FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'business identity does not exist'; END IF;
  ELSE
    RAISE EXCEPTION 'entity type has no registered naming adapter';
  END IF;

  IF NEW.generation_batch_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM sw_names.generation_batch b
    WHERE b.batch_id=NEW.generation_batch_id
      AND b.normalizer_version=NEW.normalizer_version
      AND ((NEW.entity_type='PERSON' AND b.domain='PERSON')
        OR (NEW.entity_type='GEOGRAPHY' AND b.domain IN ('GEOGRAPHY','ROAD'))
        OR (NEW.entity_type='BUSINESS' AND b.domain='BUSINESS'))
  ) THEN
    RAISE EXCEPTION 'generator manifest domain does not match the owning entity type';
  END IF;

  PERFORM set_config('pg_trgm.similarity_threshold','0.90',true);
  IF EXISTS (
    SELECT 1 FROM sw_names.name_reservation r
    WHERE r.normalized_key <> NEW.normalized_key
      AND r.normalized_key % NEW.normalized_key
  ) THEN
    RAISE EXCEPTION 'near-duplicate name requires review before reservation';
  END IF;

  IF NEW.name_form='canonical' AND EXISTS (
    SELECT 1 FROM sw_names.name_reservation r
    WHERE r.entity_type=NEW.entity_type AND r.entity_id=NEW.entity_id
      AND r.name_form='canonical'
      AND sw_names.latest_status(r.reservation_id)='active'
  ) THEN
    RAISE EXCEPTION 'a second active canonical name is forbidden; use the transactional reservation function';
  END IF;

  IF NEW.entity_type='GEOGRAPHY' THEN
    SELECT entity_code,kind INTO v_code,v_kind
      FROM sw_geo.entity WHERE spatial_id=NEW.entity_id;
    IF NOT FOUND THEN RAISE EXCEPTION 'geography identity does not exist'; END IF;
    IF NEW.normalized_key='saltwater' THEN
      IF NEW.name_form <> 'canonical' OR NEW.display_name <> 'Saltwater' THEN
        RAISE EXCEPTION 'Saltwater root exception permits only exact canonical display spelling';
      END IF;
      IF v_code='saltwater-state' AND v_kind=1 THEN
        NEW.namespace_slot := 'SOVEREIGN_ROOT';
      ELSIF v_code='saltwater-city' AND v_kind=2 THEN
        NEW.namespace_slot := 'PLAYABLE_CITY';
      ELSE
        RAISE EXCEPTION 'Saltwater name is reserved only for the sovereign root and playable city';
      END IF;
    ELSE
      NEW.namespace_slot := 'GLOBAL';
    END IF;
  ELSE
    IF NEW.normalized_key='saltwater' THEN
      RAISE EXCEPTION 'Saltwater name is reserved only for the two geographic roots';
    END IF;
    NEW.namespace_slot := 'GLOBAL';
  END IF;
  RETURN NEW;
END
$$;

GRANT USAGE ON SCHEMA sw_business TO sw_game_readonly,sw_game_command;
REVOKE ALL ON ALL TABLES IN SCHEMA sw_business FROM PUBLIC,sw_game_command,sw_game_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA sw_business TO sw_game_readonly;
GRANT SELECT ON sw_ops.world_provisioning_batch TO sw_game_readonly;
REVOKE ALL ON sw_ops.world_provisioning_batch FROM PUBLIC,sw_game_command;

INSERT INTO sw_ops.storage_operation
  (operation_kind,description,status,measurement_notes)
VALUES
  ('migration','0010 canonical world provisioning candidate','succeeded',
   'Disposable PostgreSQL only. Measure database/table/index/TOAST bytes and fixture deltas; no Neon production operation.');

COMMIT;
