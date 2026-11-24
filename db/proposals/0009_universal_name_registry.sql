-- SW-NAM-001: shared naming registry, atomic reservation and domain enforcement.
-- Disposable PostgreSQL proposal only. Never apply to Neon without separate approval.
-- Apply after proposals 0002-0008. BP-04 entities remain NOT CONNECTED until their
-- authoritative schema and stable IDs exist.
BEGIN;

CREATE SCHEMA sw_names;
CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA sw_names;

CREATE TABLE sw_names.generation_batch (
  batch_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  domain text NOT NULL CHECK (domain IN
    ('PERSON','GEOGRAPHY','ROAD','BUILDING','BUSINESS','ORGANISATION','OPERATIONAL')),
  generator_version smallint NOT NULL CHECK (generator_version > 0),
  normalizer_version smallint NOT NULL CHECK (normalizer_version > 0),
  config_version text NOT NULL CHECK (length(btrim(config_version)) BETWEEN 1 AND 80),
  seed bigint NOT NULL,
  manifest_sha256 bytea NOT NULL UNIQUE CHECK (octet_length(manifest_sha256)=32),
  candidate_count integer NOT NULL CHECK (candidate_count > 0),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);

CREATE TABLE sw_names.name_reservation (
  reservation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_type text NOT NULL CHECK (entity_type IN ('GEOGRAPHY','PERSON')),
  entity_id bigint NOT NULL CHECK (entity_id > 0),
  name_form text NOT NULL CHECK (name_form IN
    ('canonical','preferred','alias','legal','trading','call_sign')),
  display_name text NOT NULL CHECK (length(btrim(display_name)) BETWEEN 1 AND 200),
  normalized_key text NOT NULL CHECK (length(normalized_key) BETWEEN 1 AND 200),
  namespace_slot text NOT NULL DEFAULT 'GLOBAL'
    CHECK (namespace_slot IN ('GLOBAL','SOVEREIGN_ROOT','PLAYABLE_CITY')),
  normalizer_version smallint NOT NULL DEFAULT 1 CHECK (normalizer_version=1),
  source_ref text NOT NULL CHECK (length(source_ref) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(actor_ref) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(reason) BETWEEN 1 AND 240),
  generation_batch_id bigint REFERENCES sw_names.generation_batch(batch_id),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE (normalized_key, namespace_slot),
  UNIQUE (entity_type, entity_id, normalized_key, name_form),
  CHECK (
    (namespace_slot='GLOBAL' AND normalized_key <> 'saltwater')
    OR (namespace_slot='SOVEREIGN_ROOT' AND normalized_key='saltwater'
        AND entity_type='GEOGRAPHY' AND name_form='canonical')
    OR (namespace_slot='PLAYABLE_CITY' AND normalized_key='saltwater'
        AND entity_type='GEOGRAPHY' AND name_form='canonical')
  )
);

CREATE INDEX name_reservation_owner_idx
  ON sw_names.name_reservation(entity_type,entity_id);
CREATE INDEX name_reservation_key_idx
  ON sw_names.name_reservation(normalized_key);
CREATE INDEX name_reservation_trgm_idx
  ON sw_names.name_reservation USING gin(normalized_key sw_names.gin_trgm_ops);

CREATE TABLE sw_names.name_event (
  name_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  reservation_id bigint NOT NULL REFERENCES sw_names.name_reservation(reservation_id),
  event_code text NOT NULL CHECK (event_code IN
    ('reserved','activated','superseded','retired','reactivated','corrected')),
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  source_ref text NOT NULL CHECK (length(source_ref) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(actor_ref) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(reason) BETWEEN 1 AND 240),
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX name_event_reservation_idx
  ON sw_names.name_event(reservation_id,name_event_id DESC);

CREATE FUNCTION sw_names.normalize_name(p_value text)
RETURNS text LANGUAGE plpgsql IMMUTABLE STRICT PARALLEL SAFE AS $$
DECLARE
  v text;
BEGIN
  IF p_value ~ '[[:cntrl:]]' THEN
    RAISE EXCEPTION 'control characters are not permitted in names';
  END IF;
  v := normalize(btrim(p_value), NFKC);
  v := lower(v);
  v := replace(v, 'ß', 'ss');
  v := replace(v, 'ς', 'σ');
  v := replace(v, '’', '');
  v := replace(v, '‘', '');
  v := replace(v, 'ʼ', '');
  v := replace(v, '＇', '');
  v := regexp_replace(v, '[[:punct:]]+', ' ', 'g');
  v := regexp_replace(v, '[[:space:]]+', ' ', 'g');
  v := btrim(v);
  v := regexp_replace(v, '\mrd$', 'road');
  v := regexp_replace(v, '\mst$', 'street');
  v := regexp_replace(v, '\mave$', 'avenue');
  v := regexp_replace(v, '\mav$', 'avenue');
  v := regexp_replace(v, '\mcres$', 'crescent');
  v := regexp_replace(v, '\mcl$', 'close');
  v := regexp_replace(v, '\mln$', 'lane');
  v := regexp_replace(v, '\mdr$', 'drive');
  v := regexp_replace(v, '\msq$', 'square');
  v := regexp_replace(v, '\mpl$', 'place');
  v := regexp_replace(v, '\mct$', 'court');
  IF v = '' THEN RAISE EXCEPTION 'name cannot be empty'; END IF;
  IF length(v) > 200 THEN RAISE EXCEPTION 'normalized name exceeds 200 characters'; END IF;
  RETURN v;
END
$$;

CREATE FUNCTION sw_names.record_generation_batch(
  p_domain text,p_generator_version smallint,p_normalizer_version smallint,
  p_config_version text,p_seed bigint,p_manifest_sha256 bytea,
  p_candidate_count integer,p_source_ref text,p_actor_ref text,p_reason text
) RETURNS bigint LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_core AS $$
DECLARE v_id bigint; v_existing sw_names.generation_batch%ROWTYPE;
BEGIN
  IF p_manifest_sha256 IS NULL OR octet_length(p_manifest_sha256)<>32
     OR p_candidate_count IS NULL OR p_candidate_count<1
     OR p_source_ref IS NULL OR btrim(p_source_ref)=''
     OR p_actor_ref IS NULL OR btrim(p_actor_ref)=''
     OR p_reason IS NULL OR btrim(p_reason)='' THEN
    RAISE EXCEPTION 'generation manifest and provenance are required';
  END IF;
  p_domain := upper(p_domain);
  SELECT * INTO v_existing FROM sw_names.generation_batch
    WHERE manifest_sha256=p_manifest_sha256;
  IF FOUND THEN
    IF v_existing.domain=p_domain
       AND v_existing.generator_version=p_generator_version
       AND v_existing.normalizer_version=p_normalizer_version
       AND v_existing.config_version=p_config_version
       AND v_existing.seed=p_seed
       AND v_existing.candidate_count=p_candidate_count THEN
      RETURN v_existing.batch_id;
    END IF;
    RAISE EXCEPTION 'generation manifest hash is already bound to different metadata';
  END IF;
  INSERT INTO sw_names.generation_batch
    (domain,generator_version,normalizer_version,config_version,seed,
     manifest_sha256,candidate_count,source_ref,actor_ref,reason)
  VALUES
    (p_domain,p_generator_version,p_normalizer_version,p_config_version,p_seed,
     p_manifest_sha256,p_candidate_count,p_source_ref,p_actor_ref,p_reason)
  RETURNING batch_id INTO v_id;
  RETURN v_id;
END
$$;

CREATE FUNCTION sw_names.reject_generation_batch_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'generation batch manifests are immutable';
END
$$;
CREATE TRIGGER generation_batch_immutable
BEFORE UPDATE OR DELETE ON sw_names.generation_batch
FOR EACH ROW EXECUTE FUNCTION sw_names.reject_generation_batch_mutation();

CREATE FUNCTION sw_names.guard_reservation()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_core AS $$
DECLARE
  v_code text;
  v_kind smallint;
BEGIN
  IF NEW.normalized_key <> sw_names.normalize_name(NEW.display_name) THEN
    RAISE EXCEPTION 'normalized key does not match the authoritative normalizer';
  END IF;
  IF NEW.generation_batch_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM sw_names.generation_batch b
    WHERE b.batch_id=NEW.generation_batch_id
      AND b.normalizer_version=NEW.normalizer_version
      AND ((NEW.entity_type='PERSON' AND b.domain='PERSON')
        OR (NEW.entity_type='GEOGRAPHY' AND b.domain IN ('GEOGRAPHY','ROAD')))
  ) THEN
    RAISE EXCEPTION 'generator manifest domain does not match the owning entity type';
  END IF;

  -- High-similarity candidates are held for review before any domain row can
  -- claim them. The GIN trigram index keeps the check bounded as the registry grows.
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
  ELSIF NEW.entity_type='PERSON' THEN
    IF NOT EXISTS (SELECT 1 FROM sw_people.person WHERE person_id=NEW.entity_id) THEN
      RAISE EXCEPTION 'person identity does not exist';
    END IF;
    IF NEW.normalized_key='saltwater' THEN
      RAISE EXCEPTION 'Saltwater name is reserved only for the two geographic roots';
    END IF;
    NEW.namespace_slot := 'GLOBAL';
  ELSE
    RAISE EXCEPTION 'entity type has no registered naming adapter';
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER name_reservation_guard
BEFORE INSERT ON sw_names.name_reservation
FOR EACH ROW EXECUTE FUNCTION sw_names.guard_reservation();

CREATE FUNCTION sw_names.reject_reservation_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'name reservations are immutable; append a lifecycle event';
END
$$;
CREATE TRIGGER name_reservation_immutable
BEFORE UPDATE OR DELETE ON sw_names.name_reservation
FOR EACH ROW EXECUTE FUNCTION sw_names.reject_reservation_mutation();

CREATE FUNCTION sw_names.reject_event_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'name history is append-only';
END
$$;
CREATE TRIGGER name_event_immutable
BEFORE UPDATE OR DELETE ON sw_names.name_event
FOR EACH ROW EXECUTE FUNCTION sw_names.reject_event_mutation();

CREATE FUNCTION sw_names.latest_status(p_reservation_id bigint)
RETURNS text LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_core AS $$
  SELECT CASE e.event_code
    WHEN 'reserved' THEN 'reserved'
    WHEN 'activated' THEN 'active'
    WHEN 'reactivated' THEN 'active'
    WHEN 'corrected' THEN 'active'
    WHEN 'superseded' THEN 'superseded'
    WHEN 'retired' THEN 'retired'
  END
  FROM sw_names.name_event e
  WHERE e.reservation_id=p_reservation_id
  ORDER BY e.name_event_id DESC LIMIT 1
$$;

CREATE VIEW sw_names.registry AS
SELECT r.reservation_id,r.entity_type,r.entity_id,r.name_form,r.display_name,
       r.normalized_key,r.namespace_slot,r.normalizer_version,
       sw_names.latest_status(r.reservation_id) AS status,
       r.source_ref,r.actor_ref,r.reason,r.created_at
FROM sw_names.name_reservation r;

CREATE FUNCTION sw_names.reserve_name(
  p_entity_type text,p_entity_id bigint,p_name_form text,p_display_name text,
  p_source_ref text,p_actor_ref text,p_reason text,p_effective_tick bigint,
  p_generation_batch_id bigint DEFAULT NULL
) RETURNS bigint LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_core AS $$
DECLARE
  v_key text;
  v_slot text := 'GLOBAL';
  v_id bigint;
  v_existing sw_names.name_reservation%ROWTYPE;
  v_entity_code text;
BEGIN
  IF p_entity_id IS NULL OR p_entity_id <= 0 OR p_effective_tick IS NULL OR p_effective_tick < 0
     OR p_source_ref IS NULL OR btrim(p_source_ref)=''
     OR p_actor_ref IS NULL OR btrim(p_actor_ref)=''
     OR p_reason IS NULL OR btrim(p_reason)='' THEN
    RAISE EXCEPTION 'entity, provenance, actor, reason and effective tick are required';
  END IF;
  IF p_generation_batch_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM sw_names.generation_batch WHERE batch_id=p_generation_batch_id
  ) THEN
    RAISE EXCEPTION 'generation manifest reference does not exist';
  END IF;
  v_key := sw_names.normalize_name(p_display_name);
  p_entity_type := upper(p_entity_type);
  p_name_form := lower(p_name_form);

  IF v_key='saltwater' THEN
    IF p_entity_type <> 'GEOGRAPHY' OR p_name_form <> 'canonical' OR p_display_name <> 'Saltwater' THEN
      RAISE EXCEPTION 'Saltwater exception is limited to the exact canonical geographic roots';
    END IF;
    SELECT entity_code INTO v_entity_code FROM sw_geo.entity WHERE spatial_id=p_entity_id;
    IF v_entity_code='saltwater-state' THEN v_slot := 'SOVEREIGN_ROOT';
    ELSIF v_entity_code='saltwater-city' THEN v_slot := 'PLAYABLE_CITY';
    ELSE RAISE EXCEPTION 'Saltwater exception is limited to the approved root pair'; END IF;
  END IF;

  SELECT * INTO v_existing FROM sw_names.name_reservation
    WHERE normalized_key=v_key AND namespace_slot=v_slot;
  IF FOUND THEN
    IF v_existing.entity_type=p_entity_type AND v_existing.entity_id=p_entity_id
       AND v_existing.name_form=p_name_form THEN
      IF sw_names.latest_status(v_existing.reservation_id) <> 'active' THEN
        IF p_name_form='canonical' THEN
          INSERT INTO sw_names.name_event
            (reservation_id,event_code,effective_tick,source_ref,actor_ref,reason)
          SELECT r.reservation_id,'superseded',p_effective_tick,p_source_ref,p_actor_ref,
                 'another canonical name for this entity was restored'
          FROM sw_names.name_reservation r
          WHERE r.entity_type=p_entity_type AND r.entity_id=p_entity_id
            AND r.name_form='canonical' AND r.reservation_id<>v_existing.reservation_id
            AND sw_names.latest_status(r.reservation_id)='active';
        END IF;
        INSERT INTO sw_names.name_event
          (reservation_id,event_code,effective_tick,source_ref,actor_ref,reason)
        VALUES (v_existing.reservation_id,'reactivated',p_effective_tick,
          p_source_ref,p_actor_ref,'same entity restored its previously reserved name');
      END IF;
      RETURN v_existing.reservation_id;
    END IF;
    RAISE EXCEPTION 'name is already permanently reserved: %',p_display_name;
  END IF;

  IF p_name_form='canonical' THEN
    INSERT INTO sw_names.name_event
      (reservation_id,event_code,effective_tick,source_ref,actor_ref,reason)
    SELECT r.reservation_id,'superseded',p_effective_tick,p_source_ref,p_actor_ref,
           'entity received a new canonical name'
    FROM sw_names.name_reservation r
    WHERE r.entity_type=p_entity_type AND r.entity_id=p_entity_id
      AND r.name_form='canonical'
      AND sw_names.latest_status(r.reservation_id)='active';
  END IF;

  INSERT INTO sw_names.name_reservation
    (entity_type,entity_id,name_form,display_name,normalized_key,namespace_slot,
     source_ref,actor_ref,reason,generation_batch_id)
  VALUES
    (p_entity_type,p_entity_id,p_name_form,p_display_name,v_key,v_slot,
     p_source_ref,p_actor_ref,p_reason,p_generation_batch_id)
  RETURNING reservation_id INTO v_id;

  INSERT INTO sw_names.name_event
    (reservation_id,event_code,effective_tick,source_ref,actor_ref,reason)
  VALUES
    (v_id,'reserved',p_effective_tick,p_source_ref,p_actor_ref,p_reason),
    (v_id,'activated',p_effective_tick,p_source_ref,p_actor_ref,p_reason);
  RETURN v_id;
END
$$;

CREATE FUNCTION sw_names.change_status(
  p_reservation_id bigint,p_event_code text,p_effective_tick bigint,
  p_source_ref text,p_actor_ref text,p_reason text
) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_core AS $$
DECLARE v_status text; v_reservation sw_names.name_reservation%ROWTYPE;
BEGIN
  IF p_event_code NOT IN ('superseded','retired','reactivated','corrected') THEN
    RAISE EXCEPTION 'unsupported name lifecycle event';
  END IF;
  SELECT * INTO v_reservation FROM sw_names.name_reservation WHERE reservation_id=p_reservation_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'name reservation not found'; END IF;
  v_status := sw_names.latest_status(p_reservation_id);
  IF p_event_code='reactivated' AND v_status NOT IN ('retired','superseded') THEN
    RAISE EXCEPTION 'only a retired or superseded reservation can be reactivated';
  END IF;
  IF p_event_code IN ('superseded','retired') AND v_status <> 'active' THEN
    RAISE EXCEPTION 'only an active name can be superseded or retired';
  END IF;
  IF p_event_code='corrected' AND v_status <> 'active' THEN
    RAISE EXCEPTION 'only an active name can receive a correction event';
  END IF;
  IF p_event_code='reactivated' AND v_reservation.name_form='canonical' THEN
    INSERT INTO sw_names.name_event
      (reservation_id,event_code,effective_tick,source_ref,actor_ref,reason)
    SELECT r.reservation_id,'superseded',p_effective_tick,p_source_ref,p_actor_ref,
           'another canonical name for this entity was reactivated'
    FROM sw_names.name_reservation r
    WHERE r.entity_type=v_reservation.entity_type
      AND r.entity_id=v_reservation.entity_id
      AND r.name_form='canonical'
      AND r.reservation_id<>p_reservation_id
      AND sw_names.latest_status(r.reservation_id)='active';
  END IF;
  INSERT INTO sw_names.name_event
    (reservation_id,event_code,effective_tick,source_ref,actor_ref,reason)
  VALUES (p_reservation_id,p_event_code,p_effective_tick,p_source_ref,p_actor_ref,p_reason);
END
$$;

CREATE FUNCTION sw_names.add_alias(
  p_entity_type text,p_entity_id bigint,p_alias text,p_source_ref text,
  p_actor_ref text,p_reason text,p_effective_tick bigint
) RETURNS bigint LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_core AS $$
  SELECT sw_names.reserve_name(p_entity_type,p_entity_id,'alias',p_alias,
    p_source_ref,p_actor_ref,p_reason,p_effective_tick)
$$;

CREATE FUNCTION sw_names.search_name(p_value text)
RETURNS TABLE(reservation_id bigint,entity_type text,entity_id bigint,name_form text,
              display_name text,status text,ambiguous boolean)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_core AS $$
  SELECT r.reservation_id,r.entity_type,r.entity_id,r.name_form,r.display_name,
         sw_names.latest_status(r.reservation_id),count(*) OVER () > 1
  FROM sw_names.name_reservation r
  WHERE r.normalized_key=sw_names.normalize_name(p_value)
  ORDER BY r.entity_type,r.entity_id,r.reservation_id
$$;

CREATE FUNCTION sw_names.sync_geography_name()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_core AS $$
DECLARE
  v_prior sw_geo.version%ROWTYPE;
  v_new_id bigint;
  v_old_id bigint;
BEGIN
  SELECT * INTO v_prior FROM sw_geo.version
    WHERE spatial_id=NEW.spatial_id AND version_no<NEW.version_no
    ORDER BY version_no DESC LIMIT 1;

  v_new_id := sw_names.reserve_name(
    'GEOGRAPHY',NEW.spatial_id,'canonical',NEW.name,
    COALESCE(NEW.source_ref,'geography-version:'||NEW.spatial_id::text),
    'domain-trigger','geography version canonical name',NEW.effective_from_tick
  );
  IF v_prior.spatial_id IS NOT NULL
     AND sw_names.normalize_name(v_prior.name) <> sw_names.normalize_name(NEW.name) THEN
    SELECT reservation_id INTO v_old_id FROM sw_names.name_reservation
      WHERE entity_type='GEOGRAPHY' AND entity_id=NEW.spatial_id
        AND normalized_key=sw_names.normalize_name(v_prior.name)
        AND name_form='canonical';
    IF v_old_id IS NOT NULL AND sw_names.latest_status(v_old_id)='active' THEN
      PERFORM sw_names.change_status(v_old_id,'superseded',NEW.effective_from_tick,
        COALESCE(NEW.source_ref,'geography-version:'||NEW.spatial_id::text),
        'domain-trigger','geography entity renamed');
    END IF;
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER geography_name_registry_sync
AFTER INSERT ON sw_geo.version
FOR EACH ROW EXECUTE FUNCTION sw_names.sync_geography_name();

CREATE FUNCTION sw_names.sync_person_name()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_core AS $$
DECLARE
  v_full_name text;
  v_tick bigint;
  v_prior text;
  v_new_id bigint;
  v_old_id bigint;
BEGIN
  IF NEW.given_name IS NULL OR btrim(NEW.given_name)=''
     OR NEW.family_name IS NULL OR btrim(NEW.family_name)='' THEN
    RAISE EXCEPTION 'every canonical person requires given and family names';
  END IF;
  v_full_name := concat_ws(' ',NULLIF(btrim(NEW.given_name),''),NULLIF(btrim(NEW.middle_name),''),NULLIF(btrim(NEW.family_name),''));
  SELECT world_tick INTO v_tick FROM sw_core.simulation_event WHERE event_id=NEW.last_event_id;
  IF v_tick IS NULL THEN RAISE EXCEPTION 'person naming requires its committed event'; END IF;

  IF TG_OP='UPDATE' THEN
    v_prior := concat_ws(' ',NULLIF(btrim(OLD.given_name),''),NULLIF(btrim(OLD.middle_name),''),NULLIF(btrim(OLD.family_name),''));
  END IF;

  v_new_id := sw_names.reserve_name(
    'PERSON',NEW.person_id,'canonical',v_full_name,
    COALESCE(NEW.source_ref,'person:'||NEW.person_id::text),
    'domain-trigger',CASE WHEN TG_OP='INSERT' THEN 'person creation' ELSE 'person profile change' END,
    v_tick
  );

  IF TG_OP='UPDATE' AND sw_names.normalize_name(v_prior) <> sw_names.normalize_name(v_full_name) THEN
    SELECT reservation_id INTO v_old_id FROM sw_names.name_reservation
      WHERE entity_type='PERSON' AND entity_id=NEW.person_id
        AND normalized_key=sw_names.normalize_name(v_prior) AND name_form='canonical';
    IF v_old_id IS NOT NULL AND sw_names.latest_status(v_old_id)='active' THEN
      PERFORM sw_names.change_status(v_old_id,'superseded',v_tick,
        COALESCE(NEW.source_ref,'person:'||NEW.person_id::text),
        'domain-trigger','person canonical name changed');
    END IF;
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER person_name_registry_sync
AFTER INSERT OR UPDATE OF given_name,middle_name,family_name ON sw_people.person
FOR EACH ROW EXECUTE FUNCTION sw_names.sync_person_name();

-- Canonical roots and existing V1 map names are registered automatically by
-- the geography trigger on the next fresh application of proposal 0002.
-- Existing already-created disposable rows are backfilled idempotently here.
DO $$
DECLARE r record;
BEGIN
  FOR r IN SELECT v.spatial_id,v.name,v.effective_from_tick,v.source_ref
           FROM sw_geo.version v
           WHERE v.version_no=(SELECT min(v2.version_no) FROM sw_geo.version v2
                               WHERE v2.spatial_id=v.spatial_id)
           ORDER BY v.spatial_id
  LOOP
    PERFORM sw_names.reserve_name('GEOGRAPHY',r.spatial_id,'canonical',r.name,
      COALESCE(r.source_ref,'canon-import:proposal-0002'),'canon-import',
      'existing canonical geography name',r.effective_from_tick);
  END LOOP;
END
$$;

INSERT INTO sw_core.event_type(event_code,description)
VALUES ('NAME_RESERVED','Canonical or alternate name reserved'),
       ('NAME_CHANGED','Canonical name changed'),
       ('NAME_RETIRED','Name retired but permanently reserved')
ON CONFLICT (event_code) DO NOTHING;

INSERT INTO sw_ops.schema_migration(version,migration_name)
VALUES (9,'universal_name_registry')
ON CONFLICT (version) DO NOTHING;

INSERT INTO sw_ops.storage_operation(operation_kind,description,status,measurement_notes)
VALUES ('migration','0009 universal naming registry','succeeded',
  'Measure disposable database and relation/index bytes before and after. No Neon production operation.');

-- Only the controlled functions are callable by the command role; no direct
-- table DML is granted. Read-only access is through the registry view/search.
REVOKE ALL ON SCHEMA sw_names FROM PUBLIC;
GRANT USAGE ON SCHEMA sw_names TO sw_game_readonly,sw_game_command;
REVOKE ALL ON ALL TABLES IN SCHEMA sw_names FROM PUBLIC,sw_game_command,sw_game_readonly;
GRANT SELECT ON sw_names.registry,sw_names.generation_batch TO sw_game_readonly;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA sw_names FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sw_names.search_name(text) TO sw_game_readonly;
GRANT EXECUTE ON FUNCTION sw_names.latest_status(bigint) TO sw_game_readonly;
GRANT EXECUTE ON FUNCTION sw_names.reserve_name(text,bigint,text,text,text,text,text,bigint,bigint) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_names.record_generation_batch(text,smallint,smallint,text,bigint,bytea,integer,text,text,text) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_names.add_alias(text,bigint,text,text,text,text,bigint) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_names.change_status(bigint,text,bigint,text,text,text) TO sw_game_command;

COMMIT;
