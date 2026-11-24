-- BP04-01: property, building, premises, unit and access-point identity.
-- Candidate proposal for disposable PostgreSQL 16 acceptance only.
-- Never apply to Neon or another authoritative database under BP04-01 approval.
BEGIN;

CREATE SCHEMA IF NOT EXISTS sw_property;

ALTER TABLE sw_names.name_reservation
  DROP CONSTRAINT name_reservation_entity_type_check;
ALTER TABLE sw_names.name_reservation
  ADD CONSTRAINT name_reservation_entity_type_check
  CHECK (entity_type IN ('GEOGRAPHY','PERSON','BUSINESS',
    'PROPERTY','BUILDING','PREMISES','UNIT','ACCESS_POINT'));

CREATE TABLE sw_property.property_asset (
  property_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_code text NOT NULL UNIQUE CHECK (entity_code ~ '^SWP-[A-Z0-9-]{4,40}$'),
  display_name text NOT NULL CHECK (length(btrim(display_name)) BETWEEN 1 AND 200),
  location_status text NOT NULL CHECK (location_status IN ('resolved','unresolved')),
  parcel_spatial_id integer REFERENCES sw_geo.entity(spatial_id),
  address_spatial_id integer REFERENCES sw_geo.entity(spatial_id),
  lifecycle_status text NOT NULL DEFAULT 'active'
    CHECK (lifecycle_status IN ('active','inactive','retired')),
  created_tick bigint NOT NULL CHECK (created_tick >= 0),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (
    (location_status='unresolved' AND parcel_spatial_id IS NULL AND address_spatial_id IS NULL)
    OR (location_status='resolved' AND
        (parcel_spatial_id IS NOT NULL OR address_spatial_id IS NOT NULL))
  )
);
CREATE INDEX property_parcel_idx ON sw_property.property_asset(parcel_spatial_id)
  WHERE parcel_spatial_id IS NOT NULL;
CREATE INDEX property_address_idx ON sw_property.property_asset(address_spatial_id)
  WHERE address_spatial_id IS NOT NULL;

CREATE TABLE sw_property.building (
  building_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_code text NOT NULL UNIQUE CHECK (entity_code ~ '^SWB-STR-[A-Z0-9-]{3,32}$'),
  display_name text NOT NULL CHECK (length(btrim(display_name)) BETWEEN 1 AND 200),
  lifecycle_status text NOT NULL DEFAULT 'active'
    CHECK (lifecycle_status IN ('active','inactive','retired')),
  created_tick bigint NOT NULL CHECK (created_tick >= 0),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);

CREATE TABLE sw_property.premises (
  premises_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_code text NOT NULL UNIQUE CHECK (entity_code ~ '^SWPR-[A-Z0-9-]{4,36}$'),
  display_name text NOT NULL CHECK (length(btrim(display_name)) BETWEEN 1 AND 200),
  building_id bigint REFERENCES sw_property.building(building_id),
  property_id bigint REFERENCES sw_property.property_asset(property_id),
  lifecycle_status text NOT NULL DEFAULT 'active'
    CHECK (lifecycle_status IN ('active','inactive','retired')),
  created_tick bigint NOT NULL CHECK (created_tick >= 0),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK ((building_id IS NOT NULL)::integer + (property_id IS NOT NULL)::integer = 1)
);
CREATE INDEX premises_building_idx ON sw_property.premises(building_id)
  WHERE building_id IS NOT NULL;
CREATE INDEX premises_property_idx ON sw_property.premises(property_id)
  WHERE property_id IS NOT NULL;

CREATE TABLE sw_property.unit_space (
  unit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_code text NOT NULL UNIQUE CHECK (entity_code ~ '^SWU-[A-Z0-9-]{4,36}$'),
  display_name text NOT NULL CHECK (length(btrim(display_name)) BETWEEN 1 AND 200),
  premises_id bigint NOT NULL REFERENCES sw_property.premises(premises_id),
  lifecycle_status text NOT NULL DEFAULT 'active'
    CHECK (lifecycle_status IN ('active','inactive','retired')),
  created_tick bigint NOT NULL CHECK (created_tick >= 0),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX unit_premises_idx ON sw_property.unit_space(premises_id);

CREATE TABLE sw_property.access_point (
  access_point_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_code text NOT NULL UNIQUE CHECK (entity_code ~ '^SWA-[A-Z0-9-]{4,36}$'),
  display_name text CHECK (display_name IS NULL OR length(btrim(display_name)) BETWEEN 1 AND 200),
  building_id bigint REFERENCES sw_property.building(building_id),
  premises_id bigint REFERENCES sw_property.premises(premises_id),
  unit_id bigint REFERENCES sw_property.unit_space(unit_id),
  lifecycle_status text NOT NULL DEFAULT 'active'
    CHECK (lifecycle_status IN ('active','inactive','retired')),
  created_tick bigint NOT NULL CHECK (created_tick >= 0),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK ((building_id IS NOT NULL)::integer +
         (premises_id IS NOT NULL)::integer +
         (unit_id IS NOT NULL)::integer = 1)
);

CREATE TABLE sw_property.property_building (
  property_id bigint NOT NULL REFERENCES sw_property.property_asset(property_id),
  building_id bigint NOT NULL REFERENCES sw_property.building(building_id),
  valid_from_tick bigint NOT NULL CHECK (valid_from_tick >= 0),
  valid_to_tick bigint CHECK (valid_to_tick IS NULL OR valid_to_tick > valid_from_tick),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  PRIMARY KEY(property_id,building_id,valid_from_tick)
);
CREATE UNIQUE INDEX property_building_current_uq
  ON sw_property.property_building(property_id,building_id) WHERE valid_to_tick IS NULL;
CREATE INDEX property_building_building_idx ON sw_property.property_building(building_id);

CREATE TABLE sw_property.building_premises (
  building_id bigint NOT NULL REFERENCES sw_property.building(building_id),
  premises_id bigint NOT NULL UNIQUE REFERENCES sw_property.premises(premises_id),
  valid_from_tick bigint NOT NULL CHECK (valid_from_tick >= 0),
  valid_to_tick bigint CHECK (valid_to_tick IS NULL OR valid_to_tick > valid_from_tick),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  PRIMARY KEY(building_id,premises_id,valid_from_tick)
);

CREATE TABLE sw_property.premises_unit (
  premises_id bigint NOT NULL REFERENCES sw_property.premises(premises_id),
  unit_id bigint NOT NULL UNIQUE REFERENCES sw_property.unit_space(unit_id),
  valid_from_tick bigint NOT NULL CHECK (valid_from_tick >= 0),
  valid_to_tick bigint CHECK (valid_to_tick IS NULL OR valid_to_tick > valid_from_tick),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  PRIMARY KEY(premises_id,unit_id,valid_from_tick)
);

CREATE TABLE sw_property.entity_history (
  history_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_type text NOT NULL CHECK (entity_type IN
    ('PROPERTY','BUILDING','PREMISES','UNIT','ACCESS_POINT')),
  entity_id bigint NOT NULL CHECK (entity_id > 0),
  event_code text NOT NULL CHECK (event_code IN ('created','status_changed')),
  old_status text,
  new_status text NOT NULL CHECK (new_status IN ('active','inactive','retired')),
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  source_ref text NOT NULL,
  actor_ref text NOT NULL,
  reason text NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX entity_history_owner_idx
  ON sw_property.entity_history(entity_type,entity_id,history_id DESC);

CREATE TABLE sw_property.relationship_history (
  relationship_history_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  relationship_type text NOT NULL CHECK (relationship_type IN
    ('property_building','building_premises','premises_unit')),
  from_id bigint NOT NULL CHECK (from_id > 0),
  to_id bigint NOT NULL CHECK (to_id > 0),
  event_code text NOT NULL CHECK (event_code IN ('linked','unlinked')),
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  source_ref text NOT NULL,
  actor_ref text NOT NULL,
  reason text NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX relationship_history_lookup_idx
  ON sw_property.relationship_history(relationship_type,from_id,to_id,relationship_history_id DESC);

CREATE FUNCTION sw_property.guard_geography_reference()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.location_status='resolved' THEN
    IF NEW.parcel_spatial_id IS NOT NULL AND NOT EXISTS (
      SELECT 1 FROM sw_geo.entity WHERE spatial_id=NEW.parcel_spatial_id AND kind=6
    ) THEN RAISE EXCEPTION 'property parcel reference must identify a BP-02 parcel (kind 6)'; END IF;
    IF NEW.address_spatial_id IS NOT NULL AND NOT EXISTS (
      SELECT 1 FROM sw_geo.entity WHERE spatial_id=NEW.address_spatial_id AND kind=11
    ) THEN RAISE EXCEPTION 'property address reference must identify a BP-02 address (kind 11)'; END IF;
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER property_geography_kind_guard
BEFORE INSERT OR UPDATE OF location_status,parcel_spatial_id,address_spatial_id
ON sw_property.property_asset
FOR EACH ROW EXECUTE FUNCTION sw_property.guard_geography_reference();

CREATE FUNCTION sw_property.guard_identity_update()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF (to_jsonb(NEW) - 'lifecycle_status') IS DISTINCT FROM
     (to_jsonb(OLD) - 'lifecycle_status') THEN
    RAISE EXCEPTION 'BP-04 identity, naming, parent and provenance facts are immutable';
  END IF;
  IF NEW.lifecycle_status IS DISTINCT FROM OLD.lifecycle_status AND NOT (
    (OLD.lifecycle_status='active' AND NEW.lifecycle_status IN ('inactive','retired'))
    OR (OLD.lifecycle_status='inactive' AND NEW.lifecycle_status IN ('active','retired'))
  ) THEN
    RAISE EXCEPTION 'invalid BP-04 lifecycle transition';
  END IF;
  RETURN NEW;
END
$$;

CREATE FUNCTION sw_property.record_entity_history()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_property,sw_names AS $$
DECLARE
  v_row jsonb := to_jsonb(NEW);
  v_type text := TG_ARGV[0];
  v_id bigint;
  v_tick bigint;
  v_source text;
  v_actor text;
  v_reason text;
  v_name text;
BEGIN
  v_id := (v_row->>TG_ARGV[1])::bigint;
  v_tick := (v_row->>'created_tick')::bigint;
  v_source := v_row->>'source_ref';
  v_actor := v_row->>'actor_ref';
  v_reason := v_row->>'reason';
  v_name := v_row->>'display_name';
  INSERT INTO sw_property.entity_history
    (entity_type,entity_id,event_code,old_status,new_status,effective_tick,source_ref,actor_ref,reason)
  VALUES (v_type,v_id,'created',NULL,NEW.lifecycle_status,v_tick,v_source,v_actor,v_reason);
  IF v_name IS NOT NULL THEN
    PERFORM sw_names.reserve_name(v_type,v_id,'canonical',v_name,
      v_source,v_actor,v_reason,v_tick);
  END IF;
  RETURN NEW;
END
$$;

CREATE FUNCTION sw_property.record_entity_status_history()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
DECLARE
  v_id bigint;
  v_tick bigint;
  v_source text;
  v_actor text;
  v_reason text;
BEGIN
  IF NEW.lifecycle_status IS DISTINCT FROM OLD.lifecycle_status THEN
    v_id := (to_jsonb(NEW)->>TG_ARGV[1])::bigint;
    v_tick := NULLIF(current_setting('sw_property.change_tick',true),'')::bigint;
    v_source := NULLIF(current_setting('sw_property.change_source',true),'');
    v_actor := NULLIF(current_setting('sw_property.change_actor',true),'');
    v_reason := NULLIF(current_setting('sw_property.change_reason',true),'');
    IF v_tick IS NULL OR v_source IS NULL OR v_actor IS NULL OR v_reason IS NULL THEN
      RAISE EXCEPTION 'lifecycle changes require effective tick and source, actor and reason provenance';
    END IF;
    INSERT INTO sw_property.entity_history
      (entity_type,entity_id,event_code,old_status,new_status,effective_tick,source_ref,actor_ref,reason)
    VALUES (TG_ARGV[0],v_id,'status_changed',OLD.lifecycle_status,NEW.lifecycle_status,
      v_tick,v_source,v_actor,v_reason);
  END IF;
  RETURN NEW;
END
$bp04$;

CREATE FUNCTION sw_property.change_lifecycle(
  p_entity_type text,p_entity_id bigint,p_new_status text,p_effective_tick bigint,
  p_source_ref text,p_actor_ref text,p_reason text
) RETURNS void LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_property AS $bp04$
DECLARE
  v_table text;
  v_id_column text;
  v_rows integer;
  v_old_tick text := current_setting('sw_property.change_tick',true);
  v_old_source text := current_setting('sw_property.change_source',true);
  v_old_actor text := current_setting('sw_property.change_actor',true);
  v_old_reason text := current_setting('sw_property.change_reason',true);
BEGIN
  IF p_entity_id IS NULL OR p_entity_id<=0 OR p_effective_tick IS NULL OR p_effective_tick<0
    OR p_source_ref IS NULL OR btrim(p_source_ref)=''
    OR p_actor_ref IS NULL OR btrim(p_actor_ref)=''
    OR p_reason IS NULL OR btrim(p_reason)='' THEN
    RAISE EXCEPTION 'lifecycle identity and provenance are required';
  END IF;
  CASE upper(p_entity_type)
    WHEN 'PROPERTY' THEN v_table:='property_asset'; v_id_column:='property_id';
    WHEN 'BUILDING' THEN v_table:='building'; v_id_column:='building_id';
    WHEN 'PREMISES' THEN v_table:='premises'; v_id_column:='premises_id';
    WHEN 'UNIT' THEN v_table:='unit_space'; v_id_column:='unit_id';
    WHEN 'ACCESS_POINT' THEN v_table:='access_point'; v_id_column:='access_point_id';
    ELSE RAISE EXCEPTION 'unsupported BP-04 lifecycle entity type';
  END CASE;
  PERFORM set_config('sw_property.change_tick',p_effective_tick::text,true);
  PERFORM set_config('sw_property.change_source',p_source_ref,true);
  PERFORM set_config('sw_property.change_actor',p_actor_ref,true);
  PERFORM set_config('sw_property.change_reason',p_reason,true);
  EXECUTE format('UPDATE sw_property.%I SET lifecycle_status=$1 WHERE %I=$2',v_table,v_id_column)
    USING p_new_status,p_entity_id;
  GET DIAGNOSTICS v_rows=ROW_COUNT;
  PERFORM set_config('sw_property.change_tick',COALESCE(v_old_tick,''),true);
  PERFORM set_config('sw_property.change_source',COALESCE(v_old_source,''),true);
  PERFORM set_config('sw_property.change_actor',COALESCE(v_old_actor,''),true);
  PERFORM set_config('sw_property.change_reason',COALESCE(v_old_reason,''),true);
  IF v_rows<>1 THEN RAISE EXCEPTION 'BP-04 lifecycle identity not found'; END IF;
END
$bp04$;

CREATE FUNCTION sw_property.reject_entity_delete()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'BP-04 identities cannot be deleted; use lifecycle transitions';
END
$$;

CREATE FUNCTION sw_property.guard_relationship()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE v_tick bigint;
BEGIN
  IF TG_TABLE_NAME='property_building' THEN
    SELECT created_tick INTO v_tick FROM sw_property.property_asset WHERE property_id=NEW.property_id;
    IF v_tick IS NULL OR NOT EXISTS (SELECT 1 FROM sw_property.building WHERE building_id=NEW.building_id) THEN
      RAISE EXCEPTION 'property-building link has an invalid endpoint';
    END IF;
  ELSIF TG_TABLE_NAME='building_premises' THEN
    IF NOT EXISTS (SELECT 1 FROM sw_property.premises WHERE premises_id=NEW.premises_id AND building_id=NEW.building_id) THEN
      RAISE EXCEPTION 'building-premises link must match the premises owning building';
    END IF;
  ELSIF TG_TABLE_NAME='premises_unit' THEN
    IF NOT EXISTS (SELECT 1 FROM sw_property.unit_space WHERE unit_id=NEW.unit_id AND premises_id=NEW.premises_id) THEN
      RAISE EXCEPTION 'premises-unit link must match the unit owning premises';
    END IF;
  END IF;
  RETURN NEW;
END
$$;

CREATE FUNCTION sw_property.record_relationship_history()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE v_type text := TG_TABLE_NAME;
DECLARE v_from bigint;
DECLARE v_to bigint;
BEGIN
  IF TG_OP='INSERT' THEN
    IF v_type='property_building' THEN v_from:=NEW.property_id; v_to:=NEW.building_id;
    ELSIF v_type='building_premises' THEN v_from:=NEW.building_id; v_to:=NEW.premises_id;
    ELSE v_from:=NEW.premises_id; v_to:=NEW.unit_id; END IF;
    INSERT INTO sw_property.relationship_history
      (relationship_type,from_id,to_id,event_code,effective_tick,source_ref,actor_ref,reason)
    VALUES(v_type,v_from,v_to,'linked',NEW.valid_from_tick,NEW.source_ref,NEW.actor_ref,NEW.reason);
  ELSIF OLD.valid_to_tick IS NULL AND NEW.valid_to_tick IS NOT NULL THEN
    IF v_type='property_building' THEN v_from:=NEW.property_id; v_to:=NEW.building_id;
    ELSIF v_type='building_premises' THEN v_from:=NEW.building_id; v_to:=NEW.premises_id;
    ELSE v_from:=NEW.premises_id; v_to:=NEW.unit_id; END IF;
    INSERT INTO sw_property.relationship_history
      (relationship_type,from_id,to_id,event_code,effective_tick,source_ref,actor_ref,reason)
    VALUES(v_type,v_from,v_to,'unlinked',NEW.valid_to_tick,NEW.source_ref,NEW.actor_ref,'relationship ended');
  END IF;
  RETURN NEW;
END
$$;

CREATE FUNCTION sw_property.guard_relationship_update()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF (to_jsonb(NEW) - 'valid_to_tick') IS DISTINCT FROM
     (to_jsonb(OLD) - 'valid_to_tick') THEN
    RAISE EXCEPTION 'relationship identity and provenance are immutable';
  END IF;
  IF OLD.valid_to_tick IS NOT NULL OR NEW.valid_to_tick IS NULL
     OR NEW.valid_to_tick <= OLD.valid_from_tick THEN
    RAISE EXCEPTION 'relationship can be ended exactly once at a later tick';
  END IF;
  RETURN NEW;
END
$$;

DO $$
DECLARE t record;
BEGIN
  FOR t IN SELECT * FROM (VALUES
    ('property_asset','PROPERTY','property_id'),
    ('building','BUILDING','building_id'),
    ('premises','PREMISES','premises_id'),
    ('unit_space','UNIT','unit_id'),
    ('access_point','ACCESS_POINT','access_point_id')
  ) AS x(table_name,entity_type,id_column)
  LOOP
    EXECUTE format('CREATE TRIGGER %I_identity_update BEFORE UPDATE ON sw_property.%I FOR EACH ROW EXECUTE FUNCTION sw_property.guard_identity_update()',t.table_name||'_identity_update',t.table_name);
    EXECUTE format('CREATE TRIGGER %I_history_insert AFTER INSERT ON sw_property.%I FOR EACH ROW EXECUTE FUNCTION sw_property.record_entity_history(%L,%L)',t.table_name||'_history_insert',t.table_name,t.entity_type,t.id_column);
    EXECUTE format('CREATE TRIGGER %I_history_status AFTER UPDATE OF lifecycle_status ON sw_property.%I FOR EACH ROW EXECUTE FUNCTION sw_property.record_entity_status_history(%L,%L)',t.table_name||'_history_status',t.table_name,t.entity_type,t.id_column);
    EXECUTE format('CREATE TRIGGER %I_no_delete BEFORE DELETE ON sw_property.%I FOR EACH ROW EXECUTE FUNCTION sw_property.reject_entity_delete()',t.table_name||'_no_delete',t.table_name);
  END LOOP;
END
$$;

CREATE TRIGGER property_building_guard BEFORE INSERT ON sw_property.property_building
FOR EACH ROW EXECUTE FUNCTION sw_property.guard_relationship();
CREATE TRIGGER building_premises_guard BEFORE INSERT ON sw_property.building_premises
FOR EACH ROW EXECUTE FUNCTION sw_property.guard_relationship();
CREATE TRIGGER premises_unit_guard BEFORE INSERT ON sw_property.premises_unit
FOR EACH ROW EXECUTE FUNCTION sw_property.guard_relationship();

DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['property_building','building_premises','premises_unit'] LOOP
    EXECUTE format('CREATE TRIGGER %I_history AFTER INSERT OR UPDATE OF valid_to_tick ON sw_property.%I FOR EACH ROW EXECUTE FUNCTION sw_property.record_relationship_history()',t||'_history',t);
    EXECUTE format('CREATE TRIGGER %I_update_guard BEFORE UPDATE ON sw_property.%I FOR EACH ROW EXECUTE FUNCTION sw_property.guard_relationship_update()',t||'_update_guard',t);
    EXECUTE format('CREATE TRIGGER %I_no_delete BEFORE DELETE ON sw_property.%I FOR EACH ROW EXECUTE FUNCTION sw_property.reject_entity_delete()',t||'_no_delete',t);
  END LOOP;
END
$$;

CREATE OR REPLACE FUNCTION sw_names.guard_reservation()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_business,sw_property,sw_core AS $$
DECLARE v_code text; v_kind smallint; v_enable_seqscan text;
BEGIN
  IF NEW.normalized_key <> sw_names.normalize_name(NEW.display_name) THEN
    RAISE EXCEPTION 'normalized key does not match the authoritative normalizer';
  END IF;
  IF NEW.entity_type='GEOGRAPHY' THEN
    PERFORM 1 FROM sw_geo.entity WHERE spatial_id=NEW.entity_id FOR UPDATE;
  ELSIF NEW.entity_type='PERSON' THEN
    PERFORM 1 FROM sw_people.person WHERE person_id=NEW.entity_id FOR UPDATE;
  ELSIF NEW.entity_type='BUSINESS' THEN
    PERFORM 1 FROM sw_business.business WHERE business_id=NEW.entity_id FOR UPDATE;
  ELSIF NEW.entity_type='PROPERTY' THEN
    PERFORM 1 FROM sw_property.property_asset WHERE property_id=NEW.entity_id FOR UPDATE;
  ELSIF NEW.entity_type='BUILDING' THEN
    PERFORM 1 FROM sw_property.building WHERE building_id=NEW.entity_id FOR UPDATE;
  ELSIF NEW.entity_type='PREMISES' THEN
    PERFORM 1 FROM sw_property.premises WHERE premises_id=NEW.entity_id FOR UPDATE;
  ELSIF NEW.entity_type='UNIT' THEN
    PERFORM 1 FROM sw_property.unit_space WHERE unit_id=NEW.entity_id FOR UPDATE;
  ELSIF NEW.entity_type='ACCESS_POINT' THEN
    PERFORM 1 FROM sw_property.access_point WHERE access_point_id=NEW.entity_id FOR UPDATE;
  ELSE RAISE EXCEPTION 'entity type has no registered naming adapter';
  END IF;
  IF NOT FOUND THEN RAISE EXCEPTION 'named entity identity does not exist'; END IF;

  IF NEW.generation_batch_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM sw_names.generation_batch b
    WHERE b.batch_id=NEW.generation_batch_id AND b.normalizer_version=NEW.normalizer_version
      AND ((NEW.entity_type='PERSON' AND b.domain='PERSON')
        OR (NEW.entity_type='GEOGRAPHY' AND b.domain IN ('GEOGRAPHY','ROAD'))
        OR (NEW.entity_type='BUSINESS' AND b.domain='BUSINESS'))
  ) THEN RAISE EXCEPTION 'generator manifest domain does not match the owning entity type'; END IF;

  v_enable_seqscan := current_setting('enable_seqscan');
  PERFORM set_config('enable_seqscan','off',true);
  PERFORM set_config('pg_trgm.similarity_threshold','0.90',true);
  IF EXISTS (SELECT 1 FROM sw_names.name_reservation r
    WHERE r.normalized_key <> NEW.normalized_key AND r.normalized_key % NEW.normalized_key) THEN
    PERFORM set_config('enable_seqscan',v_enable_seqscan,true);
    RAISE EXCEPTION 'near-duplicate name requires review before reservation';
  END IF;
  PERFORM set_config('enable_seqscan',v_enable_seqscan,true);

  IF NEW.name_form='canonical' AND EXISTS (
    SELECT 1 FROM sw_names.name_reservation r WHERE r.entity_type=NEW.entity_type
      AND r.entity_id=NEW.entity_id AND r.name_form='canonical'
      AND sw_names.latest_status(r.reservation_id)='active'
  ) THEN RAISE EXCEPTION 'a second active canonical name is forbidden; use the transactional reservation function'; END IF;

  IF NEW.entity_type='GEOGRAPHY' THEN
    SELECT entity_code,kind INTO v_code,v_kind FROM sw_geo.entity WHERE spatial_id=NEW.entity_id;
    IF NEW.normalized_key='saltwater' THEN
      IF NEW.name_form<>'canonical' OR NEW.display_name<>'Saltwater' THEN RAISE EXCEPTION 'Saltwater root exception permits only exact canonical display spelling'; END IF;
      IF v_code='saltwater-state' AND v_kind=1 THEN NEW.namespace_slot:='SOVEREIGN_ROOT';
      ELSIF v_code='saltwater-city' AND v_kind=2 THEN NEW.namespace_slot:='PLAYABLE_CITY';
      ELSE RAISE EXCEPTION 'Saltwater name is reserved only for the sovereign root and playable city'; END IF;
    ELSE NEW.namespace_slot:='GLOBAL'; END IF;
  ELSE
    IF NEW.normalized_key='saltwater' THEN RAISE EXCEPTION 'Saltwater name is reserved only for the two geographic roots'; END IF;
    NEW.namespace_slot:='GLOBAL';
  END IF;
  RETURN NEW;
END
$$;

CREATE OR REPLACE FUNCTION sw_names.reserve_name(
  p_entity_type text,p_entity_id bigint,p_name_form text,p_display_name text,
  p_source_ref text,p_actor_ref text,p_reason text,p_effective_tick bigint,
  p_generation_batch_id bigint DEFAULT NULL
) RETURNS bigint LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_names,sw_geo,sw_people,sw_business,sw_property,sw_core AS $$
DECLARE v_key text; v_slot text:='GLOBAL'; v_id bigint;
  v_existing sw_names.name_reservation%ROWTYPE; v_entity_code text;
BEGIN
  IF p_entity_id IS NULL OR p_entity_id<=0 OR p_effective_tick IS NULL OR p_effective_tick<0
    OR p_source_ref IS NULL OR btrim(p_source_ref)='' OR p_actor_ref IS NULL OR btrim(p_actor_ref)=''
    OR p_reason IS NULL OR btrim(p_reason)='' THEN
    RAISE EXCEPTION 'entity, provenance, actor, reason and effective tick are required';
  END IF;
  IF p_generation_batch_id IS NOT NULL AND NOT EXISTS
    (SELECT 1 FROM sw_names.generation_batch WHERE batch_id=p_generation_batch_id) THEN
    RAISE EXCEPTION 'generation manifest reference does not exist';
  END IF;
  v_key:=sw_names.normalize_name(p_display_name);
  p_entity_type:=upper(p_entity_type); p_name_form:=lower(p_name_form);
  IF p_entity_type='GEOGRAPHY' THEN
    PERFORM 1 FROM sw_geo.entity WHERE spatial_id=p_entity_id FOR UPDATE;
  ELSIF p_entity_type='PERSON' THEN
    PERFORM 1 FROM sw_people.person WHERE person_id=p_entity_id FOR UPDATE;
  ELSIF p_entity_type='BUSINESS' THEN
    PERFORM 1 FROM sw_business.business WHERE business_id=p_entity_id FOR UPDATE;
  ELSIF p_entity_type='PROPERTY' THEN
    PERFORM 1 FROM sw_property.property_asset WHERE property_id=p_entity_id FOR UPDATE;
  ELSIF p_entity_type='BUILDING' THEN
    PERFORM 1 FROM sw_property.building WHERE building_id=p_entity_id FOR UPDATE;
  ELSIF p_entity_type='PREMISES' THEN
    PERFORM 1 FROM sw_property.premises WHERE premises_id=p_entity_id FOR UPDATE;
  ELSIF p_entity_type='UNIT' THEN
    PERFORM 1 FROM sw_property.unit_space WHERE unit_id=p_entity_id FOR UPDATE;
  ELSIF p_entity_type='ACCESS_POINT' THEN
    PERFORM 1 FROM sw_property.access_point WHERE access_point_id=p_entity_id FOR UPDATE;
  ELSE RAISE EXCEPTION 'entity type has no registered naming adapter'; END IF;
  IF NOT FOUND THEN RAISE EXCEPTION 'named entity identity does not exist'; END IF;
  IF v_key='saltwater' THEN
    IF p_entity_type<>'GEOGRAPHY' OR p_name_form<>'canonical' OR p_display_name<>'Saltwater' THEN
      RAISE EXCEPTION 'Saltwater exception is limited to the exact canonical geographic roots';
    END IF;
    SELECT entity_code INTO v_entity_code FROM sw_geo.entity WHERE spatial_id=p_entity_id;
    IF v_entity_code='saltwater-state' THEN v_slot:='SOVEREIGN_ROOT';
    ELSIF v_entity_code='saltwater-city' THEN v_slot:='PLAYABLE_CITY';
    ELSE RAISE EXCEPTION 'Saltwater exception is limited to the approved root pair'; END IF;
  END IF;
  SELECT * INTO v_existing FROM sw_names.name_reservation
    WHERE normalized_key=v_key AND namespace_slot=v_slot;
  IF FOUND THEN
    IF v_existing.entity_type=p_entity_type AND v_existing.entity_id=p_entity_id
       AND v_existing.name_form=p_name_form THEN
      IF sw_names.latest_status(v_existing.reservation_id)<>'active' THEN
        IF p_name_form='canonical' THEN
          INSERT INTO sw_names.name_event(reservation_id,event_code,effective_tick,source_ref,actor_ref,reason)
          SELECT r.reservation_id,'superseded',p_effective_tick,p_source_ref,p_actor_ref,
            'another canonical name for this entity was restored'
          FROM sw_names.name_reservation r WHERE r.entity_type=p_entity_type AND r.entity_id=p_entity_id
            AND r.name_form='canonical' AND r.reservation_id<>v_existing.reservation_id
            AND sw_names.latest_status(r.reservation_id)='active';
        END IF;
        INSERT INTO sw_names.name_event(reservation_id,event_code,effective_tick,source_ref,actor_ref,reason)
        VALUES(v_existing.reservation_id,'reactivated',p_effective_tick,p_source_ref,p_actor_ref,
          'same entity restored its previously reserved name');
      END IF;
      RETURN v_existing.reservation_id;
    END IF;
    RAISE EXCEPTION 'name is already permanently reserved: %',p_display_name;
  END IF;
  IF p_name_form='canonical' THEN
    INSERT INTO sw_names.name_event(reservation_id,event_code,effective_tick,source_ref,actor_ref,reason)
    SELECT r.reservation_id,'superseded',p_effective_tick,p_source_ref,p_actor_ref,
      'entity received a new canonical name'
    FROM sw_names.name_reservation r WHERE r.entity_type=p_entity_type AND r.entity_id=p_entity_id
      AND r.name_form='canonical' AND sw_names.latest_status(r.reservation_id)='active';
  END IF;
  INSERT INTO sw_names.name_reservation
    (entity_type,entity_id,name_form,display_name,normalized_key,namespace_slot,
     source_ref,actor_ref,reason,generation_batch_id)
  VALUES(p_entity_type,p_entity_id,p_name_form,p_display_name,v_key,v_slot,
    p_source_ref,p_actor_ref,p_reason,p_generation_batch_id)
  RETURNING reservation_id INTO v_id;
  INSERT INTO sw_names.name_event(reservation_id,event_code,effective_tick,source_ref,actor_ref,reason)
  VALUES(v_id,'reserved',p_effective_tick,p_source_ref,p_actor_ref,p_reason),
        (v_id,'activated',p_effective_tick,p_source_ref,p_actor_ref,p_reason);
  RETURN v_id;
END
$$;

-- Trigger adapter is generic; all named BP-04 identities reserve through SW-UNS.
GRANT USAGE ON SCHEMA sw_property TO sw_game_readonly,sw_game_command;
REVOKE ALL ON ALL TABLES IN SCHEMA sw_property FROM PUBLIC,sw_game_command,sw_game_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA sw_property TO sw_game_readonly;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA sw_property FROM PUBLIC,sw_game_command,sw_game_readonly;
REVOKE ALL ON FUNCTION sw_property.change_lifecycle(text,bigint,text,bigint,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sw_property.change_lifecycle(text,bigint,text,bigint,text,text,text) TO sw_game_command;
INSERT INTO sw_ops.storage_operation(operation_kind,description,status,measurement_notes)
VALUES('migration','0011 BP04-01 property and premises identity foundation','succeeded',
  'Disposable PostgreSQL 16 only. No operational geography, property fixture, Neon production connection or production write.');

COMMIT;
