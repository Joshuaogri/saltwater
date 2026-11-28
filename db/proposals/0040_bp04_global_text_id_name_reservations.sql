-- SW-NAM-003: shared persistent naming adapters for BP04 property entities.
-- Depends on SW-NAM-001 (0009), BP04 canonical property stack (0012), and
-- SW-NAM-002 business text-ID naming (0030).
-- Disposable PostgreSQL acceptance only. Never apply to production Neon without
-- separate explicit production-write approval.
BEGIN;

ALTER TABLE sw_names.generation_batch
  DROP CONSTRAINT generation_batch_domain_check;
ALTER TABLE sw_names.generation_batch
  ADD CONSTRAINT generation_batch_domain_check
  CHECK (domain IN (
    'PERSON','GEOGRAPHY','ROAD','PROPERTY','BUILDING','PREMISES',
    'BUSINESS','ORGANISATION','OPERATIONAL'
  ));

ALTER TABLE sw_names.name_reservation
  DROP CONSTRAINT name_reservation_entity_type_check;
ALTER TABLE sw_names.name_reservation
  ADD CONSTRAINT name_reservation_entity_type_check
  CHECK (entity_type IN (
    'GEOGRAPHY','PERSON','BUSINESS','PROPERTY','BUILDING','PREMISES','ORGANISATION'
  ));

ALTER TABLE sw_names.name_reservation
  DROP CONSTRAINT name_reservation_owner_identity_check;
ALTER TABLE sw_names.name_reservation
  ADD CONSTRAINT name_reservation_owner_identity_check
  CHECK (
    (entity_type IN ('BUSINESS','PROPERTY','BUILDING','PREMISES','ORGANISATION')
      AND entity_id IS NULL
      AND entity_ref IS NOT NULL
      AND length(btrim(entity_ref)) BETWEEN 1 AND 120)
    OR
    (entity_type IN ('GEOGRAPHY','PERSON')
      AND entity_id IS NOT NULL AND entity_id > 0 AND entity_ref IS NULL)
  );

CREATE INDEX name_reservation_text_owner_idx
  ON sw_names.name_reservation(entity_type,entity_ref,reservation_id)
  WHERE entity_ref IS NOT NULL;

CREATE OR REPLACE FUNCTION sw_names.guard_reservation()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_property,sw_core AS $$
DECLARE
  v_code text;
  v_kind smallint;
BEGIN
  PERFORM pg_advisory_xact_lock(725101001::bigint);
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
    IF NEW.entity_id IS NOT NULL OR NEW.entity_ref IS NULL THEN
      RAISE EXCEPTION 'business reservation requires a stable text business ID';
    END IF;
    PERFORM 1 FROM sw_property.business WHERE business_id=NEW.entity_ref FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'business identity does not exist'; END IF;
    IF NEW.name_form NOT IN ('trading','legal') THEN
      RAISE EXCEPTION 'business names must use trading or legal name form';
    END IF;
  ELSIF NEW.entity_type='PROPERTY' THEN
    PERFORM 1 FROM sw_property.property_site WHERE property_id=NEW.entity_ref FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'property identity does not exist'; END IF;
    IF NEW.name_form <> 'canonical' THEN
      RAISE EXCEPTION 'property names must use canonical name form';
    END IF;
  ELSIF NEW.entity_type='BUILDING' THEN
    PERFORM 1 FROM sw_property.building WHERE building_id=NEW.entity_ref FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'building identity does not exist'; END IF;
    IF NEW.name_form <> 'canonical' THEN
      RAISE EXCEPTION 'building names must use canonical name form';
    END IF;
  ELSIF NEW.entity_type='PREMISES' THEN
    PERFORM 1 FROM sw_property.premises WHERE premises_id=NEW.entity_ref FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'premises identity does not exist'; END IF;
    IF NEW.name_form <> 'canonical' THEN
      RAISE EXCEPTION 'premises names must use canonical name form';
    END IF;
  ELSIF NEW.entity_type='ORGANISATION' THEN
    PERFORM 1 FROM sw_property.organisation WHERE organisation_id=NEW.entity_ref FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'organisation identity does not exist'; END IF;
    IF NEW.name_form <> 'canonical' THEN
      RAISE EXCEPTION 'organisation names must use canonical name form';
    END IF;
  ELSE
    RAISE EXCEPTION 'entity type has no registered naming adapter';
  END IF;

  IF NEW.generation_batch_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM sw_names.generation_batch b
    WHERE b.batch_id=NEW.generation_batch_id
      AND b.normalizer_version=NEW.normalizer_version
      AND (
        (NEW.entity_type='PERSON' AND b.domain='PERSON')
        OR (NEW.entity_type='GEOGRAPHY' AND b.domain IN ('GEOGRAPHY','ROAD'))
        OR (NEW.entity_type='BUSINESS' AND b.domain='BUSINESS')
        OR (NEW.entity_type='PROPERTY' AND b.domain='PROPERTY')
        OR (NEW.entity_type='BUILDING' AND b.domain='BUILDING')
        OR (NEW.entity_type='PREMISES' AND b.domain='PREMISES')
        OR (NEW.entity_type='ORGANISATION' AND b.domain='ORGANISATION')
      )
  ) THEN
    RAISE EXCEPTION 'generator manifest domain does not match the owning entity type';
  END IF;

  PERFORM set_config('pg_trgm.similarity_threshold','0.90',true);
  IF EXISTS (
    SELECT 1 FROM sw_names.name_reservation r
    WHERE r.normalized_key <> NEW.normalized_key
      AND r.normalized_key % NEW.normalized_key
      AND NOT (
        NEW.entity_type IN ('BUSINESS','PROPERTY','BUILDING','PREMISES','ORGANISATION')
        AND r.entity_type=NEW.entity_type
        AND r.entity_ref=NEW.entity_ref
      )
  ) THEN
    RAISE EXCEPTION 'near-duplicate name requires review before reservation';
  END IF;

  IF NEW.name_form='canonical' AND EXISTS (
    SELECT 1 FROM sw_names.name_reservation r
    WHERE r.entity_type=NEW.entity_type
      AND r.entity_id IS NOT DISTINCT FROM NEW.entity_id
      AND r.entity_ref IS NOT DISTINCT FROM NEW.entity_ref
      AND r.name_form='canonical'
      AND sw_names.latest_status(r.reservation_id)='active'
  ) THEN
    RAISE EXCEPTION 'a second active canonical name is forbidden; use the transactional reservation function';
  END IF;

  IF NEW.entity_type='GEOGRAPHY' THEN
    SELECT entity_code,kind INTO v_code,v_kind
      FROM sw_geo.entity WHERE spatial_id=NEW.entity_id;
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

CREATE FUNCTION sw_names.reserve_text_entity_name(
  p_entity_type text,p_entity_ref text,p_name_form text,p_display_name text,
  p_source_ref text,p_actor_ref text,p_reason text,p_effective_tick bigint,
  p_generation_batch_id bigint DEFAULT NULL
) RETURNS bigint LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_names,sw_property,sw_core AS $$
DECLARE
  v_type text;
  v_form text;
  v_key text;
  v_id bigint;
  v_existing sw_names.name_reservation%ROWTYPE;
BEGIN
  v_type := upper(btrim(p_entity_type));
  v_form := lower(btrim(p_name_form));
  IF v_type NOT IN ('PROPERTY','BUILDING','PREMISES','ORGANISATION') THEN
    RAISE EXCEPTION 'unsupported text-ID naming entity type';
  END IF;
  IF p_entity_ref IS NULL OR btrim(p_entity_ref)=''
     OR length(p_entity_ref)>120
     OR v_form<>'canonical'
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_source_ref IS NULL OR btrim(p_source_ref)=''
     OR p_actor_ref IS NULL OR btrim(p_actor_ref)=''
     OR p_reason IS NULL OR btrim(p_reason)='' THEN
    RAISE EXCEPTION 'stable entity ID, canonical name form, provenance and effective tick are required';
  END IF;

  PERFORM pg_advisory_xact_lock(725101001::bigint);
  IF v_type='PROPERTY' THEN
    PERFORM 1 FROM sw_property.property_site WHERE property_id=p_entity_ref FOR UPDATE;
  ELSIF v_type='BUILDING' THEN
    PERFORM 1 FROM sw_property.building WHERE building_id=p_entity_ref FOR UPDATE;
  ELSIF v_type='PREMISES' THEN
    PERFORM 1 FROM sw_property.premises WHERE premises_id=p_entity_ref FOR UPDATE;
  ELSE
    PERFORM 1 FROM sw_property.organisation WHERE organisation_id=p_entity_ref FOR UPDATE;
  END IF;
  IF NOT FOUND THEN RAISE EXCEPTION 'text-ID naming entity does not exist'; END IF;

  IF p_generation_batch_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM sw_names.generation_batch
    WHERE batch_id=p_generation_batch_id
      AND domain=v_type AND normalizer_version=1
  ) THEN
    RAISE EXCEPTION 'text-ID generator manifest is missing or incompatible';
  END IF;

  v_key := sw_names.normalize_name(p_display_name);
  IF v_key='saltwater' THEN
    RAISE EXCEPTION 'Saltwater name is reserved only for the two geographic roots';
  END IF;
  SELECT * INTO v_existing FROM sw_names.name_reservation
  WHERE normalized_key=v_key AND namespace_slot='GLOBAL';
  IF FOUND THEN
    IF v_existing.entity_type=v_type
       AND v_existing.entity_ref=p_entity_ref
       AND v_existing.name_form=v_form THEN
      RETURN v_existing.reservation_id;
    END IF;
    RAISE EXCEPTION 'name is already permanently reserved: %',p_display_name;
  END IF;

  INSERT INTO sw_names.name_reservation
    (entity_type,entity_id,entity_ref,name_form,display_name,normalized_key,
     namespace_slot,normalizer_version,source_ref,actor_ref,reason,generation_batch_id)
  VALUES
    (v_type,NULL,p_entity_ref,v_form,p_display_name,v_key,
     'GLOBAL',1,p_source_ref,p_actor_ref,p_reason,p_generation_batch_id)
  RETURNING reservation_id INTO v_id;

  INSERT INTO sw_names.name_event
    (reservation_id,event_code,effective_tick,source_ref,actor_ref,reason)
  VALUES
    (v_id,'reserved',p_effective_tick,p_source_ref,p_actor_ref,p_reason),
    (v_id,'activated',p_effective_tick,p_source_ref,p_actor_ref,p_reason);
  RETURN v_id;
END
$$;

CREATE FUNCTION sw_names.search_text_entity_name(p_entity_type text,p_value text)
RETURNS TABLE(reservation_id bigint,entity_type text,entity_ref text,
              name_form text,display_name text,status text,ambiguous boolean)
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path=pg_catalog,sw_names,sw_core AS $$
  SELECT r.reservation_id,r.entity_type,r.entity_ref,r.name_form,r.display_name,
         sw_names.latest_status(r.reservation_id),count(*) OVER () > 1
  FROM sw_names.name_reservation r
  WHERE r.entity_type=upper(btrim(p_entity_type))
    AND r.entity_ref IS NOT NULL
    AND r.normalized_key=sw_names.normalize_name(p_value)
  ORDER BY r.entity_ref,r.reservation_id
$$;

REVOKE ALL ON FUNCTION sw_names.reserve_text_entity_name(text,text,text,text,text,text,text,bigint,bigint) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_names.search_text_entity_name(text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sw_names.reserve_text_entity_name(text,text,text,text,text,text,text,bigint,bigint) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_names.search_text_entity_name(text,text) TO sw_game_readonly;

COMMIT;
