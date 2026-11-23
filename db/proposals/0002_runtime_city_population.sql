-- PKG-001 / migration 0002.
-- Disposable PostgreSQL acceptance-test migration only.
-- NEVER apply to Neon or another authoritative database under PKG-001 approval.
-- No resident/person/business/case/evidence seed data is inserted.
-- The two geographic root records identify Saltwater; geometry remains unset.

BEGIN;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM sw_core.simulation_event) THEN
    RAISE EXCEPTION 'PKG-001 precondition failed: simulation_event is not empty';
  END IF;
  IF EXISTS (SELECT 1 FROM sw_core.event_type) THEN
    RAISE EXCEPTION 'PKG-001 precondition failed: event_type is not empty';
  END IF;
END
$$;

CREATE SCHEMA IF NOT EXISTS sw_runtime;
CREATE SCHEMA IF NOT EXISTS sw_geo;
CREATE SCHEMA IF NOT EXISTS sw_people;

-- Stable runtime singleton. State codes:
-- 0 stopped, 1 ready, 2 running, 3 paused, 4 recovering, 5 safe-halt.
CREATE TABLE sw_runtime.state (
  singleton smallint PRIMARY KEY CHECK (singleton = 1),
  state smallint NOT NULL CHECK (state BETWEEN 0 AND 5),
  player_present boolean NOT NULL DEFAULT false,
  bootstrap_open boolean NOT NULL DEFAULT true,
  world_tick bigint NOT NULL DEFAULT 0 CHECK (world_tick >= 0),
  calendar_day integer NOT NULL DEFAULT 0 CHECK (calendar_day >= 0),
  minute_of_day smallint NOT NULL DEFAULT 0 CHECK (minute_of_day BETWEEN 0 AND 1439),
  last_event_id bigint,
  updated_at timestamptz NOT NULL DEFAULT now(),
  CHECK (state <> 2 OR (player_present AND NOT bootstrap_open)),
  CHECK (state <> 0 OR NOT player_present)
);

-- World tick can advance only from an actively running, player-present state.
CREATE FUNCTION sw_runtime.reject_state_delete() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'runtime singleton cannot be deleted';
END
$$;
CREATE TRIGGER runtime_state_no_delete
BEFORE DELETE ON sw_runtime.state
FOR EACH ROW EXECUTE FUNCTION sw_runtime.reject_state_delete();

CREATE FUNCTION sw_runtime.guard_state_update() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF OLD.bootstrap_open = false AND NEW.bootstrap_open = true THEN
    RAISE EXCEPTION 'bootstrap cannot be reopened after closure';
  END IF;
  IF OLD.bootstrap_open = true AND NEW.bootstrap_open = false
     AND NOT (OLD.state = 1 AND OLD.world_tick = 0) THEN
    RAISE EXCEPTION 'bootstrap can close only in ready state at world tick zero';
  END IF;
  IF (NEW.calendar_day, NEW.minute_of_day) IS DISTINCT FROM (OLD.calendar_day, OLD.minute_of_day) THEN
    RAISE EXCEPTION 'fictional calendar semantics are not yet approved';
  END IF;
  IF NEW.state = 2 AND NEW.bootstrap_open THEN
    RAISE EXCEPTION 'bootstrap must be closed before runtime start';
  END IF;
  IF NEW.state <> OLD.state AND NOT (
       (OLD.state = 0 AND NEW.state = 1)
    OR (OLD.state = 1 AND NEW.state IN (0,2,4))
    OR (OLD.state = 2 AND NEW.state IN (0,3,4))
    OR (OLD.state = 3 AND NEW.state IN (0,2,4))
    OR (OLD.state = 4 AND NEW.state IN (1,5))
    OR (OLD.state = 5 AND NEW.state = 4)
  ) THEN
    RAISE EXCEPTION 'invalid runtime state transition';
  END IF;
  IF NEW.world_tick < OLD.world_tick THEN
    RAISE EXCEPTION 'world_tick cannot move backwards';
  END IF;
  IF NEW.world_tick > OLD.world_tick
     AND NOT (OLD.state = 2 AND OLD.player_present) THEN
    RAISE EXCEPTION 'world time cannot advance unless simulation is running and player is present';
  END IF;
  IF NEW.world_tick > OLD.world_tick + 1 THEN
    RAISE EXCEPTION 'world_tick must advance one tick at a time';
  END IF;
  NEW.updated_at := now();
  RETURN NEW;
END
$$;
CREATE TRIGGER state_update_guard
BEFORE UPDATE ON sw_runtime.state
FOR EACH ROW EXECUTE FUNCTION sw_runtime.guard_state_update();

-- Extend the existing event envelope without duplicating domain payloads.
ALTER TABLE sw_core.simulation_event
  ADD COLUMN world_tick bigint NOT NULL CHECK (world_tick >= 0),
  ADD COLUMN causation_event_id bigint REFERENCES sw_core.simulation_event(event_id),
  ADD COLUMN correlation_id uuid,
  ADD COLUMN idempotency_key text;

ALTER TABLE sw_runtime.state
  ADD CONSTRAINT runtime_last_event_fk
  FOREIGN KEY (last_event_id) REFERENCES sw_core.simulation_event(event_id);

CREATE UNIQUE INDEX simulation_event_idempotency_uq
  ON sw_core.simulation_event(idempotency_key)
  WHERE idempotency_key IS NOT NULL;
CREATE INDEX simulation_event_tick_idx
  ON sw_core.simulation_event(world_tick, event_id);

INSERT INTO sw_core.event_type(event_code, description) VALUES
 ('RUNTIME_READY', 'Simulation runtime ready for initialisation'),
 ('RUNTIME_START', 'Simulation runtime started'),
 ('RUNTIME_PAUSE', 'Simulation paused'),
 ('RUNTIME_RESUME', 'Simulation resumed'),
 ('RUNTIME_STOP', 'Simulation stopped'),
 ('RUNTIME_RECOVERY', 'Simulation recovery transition'),
 ('CLOCK_ADVANCE', 'One committed in-world clock tick'),
 ('GEO_CREATED', 'Canonical geographic identity created'),
 ('GEO_VERSIONED', 'Geographic version recorded'),
 ('PERSON_CREATED', 'Canonical person identity created'),
 ('PERSON_PROFILE_CHANGED', 'Canonical person profile corrected or changed'),
 ('POPULATION_STATE_CHANGED', 'Person population/life state changed'),
 ('RESIDENCE_CHANGED', 'Person residence link changed')
ON CONFLICT (event_code) DO NOTHING;

CREATE FUNCTION sw_runtime.guard_event_insert() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  runtime_state smallint;
  present boolean;
  current_tick bigint;
  event_code text;
BEGIN
  SELECT state, player_present, world_tick
    INTO runtime_state, present, current_tick
    FROM sw_runtime.state
    WHERE singleton = 1
    FOR SHARE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'runtime state singleton is missing';
  END IF;

  SELECT et.event_code INTO event_code
    FROM sw_core.event_type et
    WHERE et.event_type_id = NEW.event_type_id;

  IF event_code IS NULL THEN
    RAISE EXCEPTION 'unknown event type';
  END IF;

  IF NEW.world_tick <> current_tick THEN
    RAISE EXCEPTION 'event world_tick must equal the committed runtime tick';
  END IF;

  IF event_code IN ('RUNTIME_READY','RUNTIME_START','RUNTIME_PAUSE','RUNTIME_RESUME','RUNTIME_STOP','RUNTIME_RECOVERY') THEN
    RETURN NEW;
  END IF;

  IF runtime_state = 1 AND current_tick = 0
     AND (SELECT bootstrap_open FROM sw_runtime.state WHERE singleton = 1)
     AND event_code IN ('GEO_CREATED','GEO_VERSIONED','PERSON_CREATED',
                        'POPULATION_STATE_CHANGED','RESIDENCE_CHANGED') THEN
    RETURN NEW;
  END IF;

  IF NOT (runtime_state = 2 AND present) THEN
    RAISE EXCEPTION 'simulation events are blocked while stopped, paused, recovering or player-absent';
  END IF;

  RETURN NEW;
END
$$;
CREATE TRIGGER simulation_event_runtime_guard
BEFORE INSERT ON sw_core.simulation_event
FOR EACH ROW EXECUTE FUNCTION sw_runtime.guard_event_insert();

-- Geographic identity. No real-world coordinates, dimensions, district count,
-- CRS or geometry codec is assumed by this proposal.
CREATE TABLE sw_geo.entity (
  spatial_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_code text NOT NULL UNIQUE,
  kind smallint NOT NULL CHECK (kind BETWEEN 1 AND 12),
  created_at timestamptz NOT NULL DEFAULT now()
);
-- kind: 1 sovereign territory, 2 playable city, 3 admin area,
-- 4 locality, 5 zone, 6 parcel, 7 road, 8 junction, 9 path,
-- 10 landmark, 11 address, 12 off-map reference.
CREATE UNIQUE INDEX geo_one_sovereign_root_uq ON sw_geo.entity(kind) WHERE kind = 1;
CREATE UNIQUE INDEX geo_one_playable_city_uq ON sw_geo.entity(kind) WHERE kind = 2;

CREATE TABLE sw_geo.version (
  spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  version_no smallint NOT NULL CHECK (version_no > 0),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick >= 0),
  parent_id integer REFERENCES sw_geo.entity(spatial_id),
  name text NOT NULL,
  active boolean NOT NULL DEFAULT true,
  geometry_format smallint,
  geometry_payload bytea,
  geometry_sha256 bytea,
  source_ref text,
  reason_code smallint,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (spatial_id, version_no),
  CHECK (parent_id IS NULL OR parent_id <> spatial_id),
  CHECK (
    (geometry_payload IS NULL AND geometry_format IS NULL AND geometry_sha256 IS NULL)
    OR
    (geometry_payload IS NOT NULL AND geometry_format IS NOT NULL
      AND geometry_sha256 IS NOT NULL AND octet_length(geometry_sha256) = 32)
  )
);

INSERT INTO sw_geo.entity(entity_code, kind)
VALUES ('saltwater-state', 1)
ON CONFLICT (entity_code) DO NOTHING;

INSERT INTO sw_geo.entity(entity_code, kind)
SELECT 'saltwater-city', 2
WHERE EXISTS (SELECT 1 FROM sw_geo.entity WHERE entity_code = 'saltwater-state')
ON CONFLICT (entity_code) DO NOTHING;

INSERT INTO sw_geo.version
  (spatial_id, version_no, effective_from_tick, parent_id, name, active, source_ref, reason_code)
SELECT e.spatial_id, 1, 0, NULL::integer, 'Saltwater', true, 'approved-project-canon', 1
FROM sw_geo.entity e
WHERE e.entity_code = 'saltwater-state'
ON CONFLICT (spatial_id, version_no) DO NOTHING;

INSERT INTO sw_geo.version
  (spatial_id, version_no, effective_from_tick, parent_id, name, active, source_ref, reason_code)
SELECT e.spatial_id, 1, 0, p.spatial_id, 'Saltwater', true, 'approved-project-canon', 1
FROM sw_geo.entity e
JOIN sw_geo.entity p ON p.entity_code = 'saltwater-state'
WHERE e.entity_code = 'saltwater-city'
ON CONFLICT (spatial_id, version_no) DO NOTHING;

CREATE FUNCTION sw_geo.guard_version_insert() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  prior_version smallint;
  prior_tick bigint;
  has_cycle boolean;
BEGIN
  SELECT max(version_no), max(effective_from_tick)
    INTO prior_version, prior_tick
    FROM sw_geo.version
    WHERE spatial_id = NEW.spatial_id;

  IF NEW.version_no <> COALESCE(prior_version, 0) + 1 THEN
    RAISE EXCEPTION 'spatial version numbers must be sequential';
  END IF;
  IF prior_tick IS NOT NULL AND NEW.effective_from_tick < prior_tick THEN
    RAISE EXCEPTION 'spatial effective time cannot move backwards';
  END IF;

  IF NEW.parent_id IS NOT NULL THEN
    WITH RECURSIVE ancestors(spatial_id) AS (
      SELECT NEW.parent_id
      UNION
      SELECT v.parent_id
      FROM sw_geo.version v
      JOIN ancestors a ON a.spatial_id = v.spatial_id
      WHERE v.version_no = (
        SELECT max(v2.version_no) FROM sw_geo.version v2
        WHERE v2.spatial_id = v.spatial_id
      ) AND v.parent_id IS NOT NULL
    )
    SELECT EXISTS(SELECT 1 FROM ancestors WHERE spatial_id = NEW.spatial_id)
      INTO has_cycle;
    IF has_cycle THEN
      RAISE EXCEPTION 'spatial parent relationship would create a cycle';
    END IF;
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER spatial_version_insert_guard
BEFORE INSERT ON sw_geo.version
FOR EACH ROW EXECUTE FUNCTION sw_geo.guard_version_insert();

CREATE FUNCTION sw_geo.reject_version_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'spatial versions are append-only';
END
$$;
CREATE TRIGGER spatial_version_immutable
BEFORE UPDATE OR DELETE ON sw_geo.version
FOR EACH ROW EXECUTE FUNCTION sw_geo.reject_version_mutation();

CREATE FUNCTION sw_geo.reject_entity_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'spatial identities are immutable; create a version instead';
END
$$;
CREATE TRIGGER spatial_entity_immutable
BEFORE UPDATE OR DELETE ON sw_geo.entity
FOR EACH ROW EXECUTE FUNCTION sw_geo.reject_entity_mutation();

-- Canonical person identity. No fabricated residents are inserted.
CREATE TABLE sw_people.person (
  person_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  given_name text,
  middle_name text,
  family_name text,
  created_tick bigint NOT NULL CHECK (created_tick >= 0),
  source_ref text,
  last_event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE sw_people.profile_history (
  event_id bigint PRIMARY KEY REFERENCES sw_core.simulation_event(event_id),
  person_id integer NOT NULL REFERENCES sw_people.person(person_id),
  old_given_name text,
  new_given_name text,
  old_middle_name text,
  new_middle_name text,
  old_family_name text,
  new_family_name text,
  old_source_ref text,
  new_source_ref text,
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  recorded_at timestamptz NOT NULL DEFAULT now()
);

CREATE FUNCTION sw_people.record_profile_history() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  event_tick bigint;
BEGIN
  SELECT world_tick INTO event_tick
    FROM sw_core.simulation_event
    WHERE event_id = NEW.last_event_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'person profile event is missing';
  END IF;

  IF TG_OP = 'INSERT' THEN
    INSERT INTO sw_people.profile_history
      (event_id, person_id, new_given_name, new_middle_name,
       new_family_name, new_source_ref, effective_tick)
    VALUES
      (NEW.last_event_id, NEW.person_id, NEW.given_name, NEW.middle_name,
       NEW.family_name, NEW.source_ref, event_tick);
  ELSIF ROW(NEW.given_name, NEW.middle_name, NEW.family_name, NEW.source_ref)
        IS DISTINCT FROM
        ROW(OLD.given_name, OLD.middle_name, OLD.family_name, OLD.source_ref) THEN
    IF NEW.last_event_id = OLD.last_event_id THEN
      RAISE EXCEPTION 'every person profile change requires a new committed event';
    END IF;
    INSERT INTO sw_people.profile_history
      (event_id, person_id, old_given_name, new_given_name,
       old_middle_name, new_middle_name, old_family_name, new_family_name,
       old_source_ref, new_source_ref, effective_tick)
    VALUES
      (NEW.last_event_id, NEW.person_id, OLD.given_name, NEW.given_name,
       OLD.middle_name, NEW.middle_name, OLD.family_name, NEW.family_name,
       OLD.source_ref, NEW.source_ref, event_tick);
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER person_profile_history_append
AFTER INSERT OR UPDATE OF given_name, middle_name, family_name, source_ref
ON sw_people.person
FOR EACH ROW EXECUTE FUNCTION sw_people.record_profile_history();

CREATE FUNCTION sw_people.reject_profile_history_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'person profile history is append-only';
END
$$;
CREATE TRIGGER person_profile_history_immutable
BEFORE UPDATE OR DELETE ON sw_people.profile_history
FOR EACH ROW EXECUTE FUNCTION sw_people.reject_profile_history_mutation();

CREATE FUNCTION sw_people.guard_person_identity_update() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.person_id <> OLD.person_id OR NEW.created_tick <> OLD.created_tick
     OR NEW.created_at <> OLD.created_at THEN
    RAISE EXCEPTION 'canonical person identity and creation time are immutable';
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER person_identity_update_guard
BEFORE UPDATE ON sw_people.person
FOR EACH ROW EXECUTE FUNCTION sw_people.guard_person_identity_update();

-- life_status: 1 living, 2 deceased.
-- scope_status: 0 unresolved, 1 included in Saltwater population, 2 excluded.
-- Unresolved scope must be resolved before authoritative population activation.
CREATE TABLE sw_people.population_state (
  person_id integer PRIMARY KEY REFERENCES sw_people.person(person_id),
  life_status smallint NOT NULL CHECK (life_status IN (1,2)),
  scope_status smallint NOT NULL CHECK (scope_status IN (0,1,2)),
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  last_event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  CHECK (life_status = 1 OR scope_status <> 1)
);

CREATE TABLE sw_people.population_counter (
  singleton smallint PRIMARY KEY CHECK (singleton = 1),
  living_included integer NOT NULL DEFAULT 0 CHECK (living_included BETWEEN 0 AND 10000)
);
INSERT INTO sw_people.population_counter(singleton, living_included)
VALUES (1, 0);

CREATE FUNCTION sw_people.enforce_population_cap() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  current_count integer;
  old_count integer := 0;
  new_count integer := 0;
  adjusted_count integer;
BEGIN
  -- A single locked counter row serialises admissions across concurrent sessions.
  SELECT living_included INTO current_count
    FROM sw_people.population_counter
    WHERE singleton = 1
    FOR UPDATE;

  IF TG_OP = 'UPDATE'
     AND OLD.life_status = 1 AND OLD.scope_status = 1 THEN
    old_count := 1;
  END IF;
  IF NEW.life_status = 1 AND NEW.scope_status = 1 THEN
    new_count := 1;
  END IF;

  adjusted_count := current_count - old_count + new_count;
  IF adjusted_count > 10000 THEN
    RAISE EXCEPTION 'Saltwater living population cap of 10000 would be exceeded';
  END IF;
  UPDATE sw_people.population_counter
    SET living_included = adjusted_count
    WHERE singleton = 1;
  RETURN NEW;
END
$$;
CREATE TRIGGER population_cap_guard
BEFORE INSERT OR UPDATE OF life_status, scope_status
ON sw_people.population_state
FOR EACH ROW EXECUTE FUNCTION sw_people.enforce_population_cap();

CREATE FUNCTION sw_people.reject_person_delete() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'canonical person identities cannot be deleted';
END
$$;
CREATE TRIGGER person_identity_no_delete
BEFORE DELETE ON sw_people.person
FOR EACH ROW EXECUTE FUNCTION sw_people.reject_person_delete();

CREATE FUNCTION sw_people.reject_population_state_delete() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'population state cannot be deleted; use a lifecycle transition';
END
$$;
CREATE TRIGGER population_state_no_delete
BEFORE DELETE ON sw_people.population_state
FOR EACH ROW EXECUTE FUNCTION sw_people.reject_population_state_delete();

CREATE TABLE sw_people.population_history (
  event_id bigint PRIMARY KEY REFERENCES sw_core.simulation_event(event_id),
  person_id integer NOT NULL REFERENCES sw_people.person(person_id),
  old_life_status smallint,
  new_life_status smallint NOT NULL CHECK (new_life_status IN (1,2)),
  old_scope_status smallint,
  new_scope_status smallint NOT NULL CHECK (new_scope_status IN (0,1,2)),
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  recorded_at timestamptz NOT NULL DEFAULT now()
);

CREATE FUNCTION sw_people.record_population_history() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO sw_people.population_history
      (event_id, person_id, old_life_status, new_life_status,
       old_scope_status, new_scope_status, effective_tick)
    VALUES
      (NEW.last_event_id, NEW.person_id, NULL, NEW.life_status,
       NULL, NEW.scope_status, NEW.effective_tick);
  ELSIF (NEW.life_status, NEW.scope_status, NEW.effective_tick)
        IS DISTINCT FROM
        (OLD.life_status, OLD.scope_status, OLD.effective_tick) THEN
    IF NEW.last_event_id = OLD.last_event_id THEN
      RAISE EXCEPTION 'every population-state change requires a new committed event';
    END IF;
    INSERT INTO sw_people.population_history
      (event_id, person_id, old_life_status, new_life_status,
       old_scope_status, new_scope_status, effective_tick)
    VALUES
      (NEW.last_event_id, NEW.person_id, OLD.life_status, NEW.life_status,
       OLD.scope_status, NEW.scope_status, NEW.effective_tick);
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER population_history_append
AFTER INSERT OR UPDATE ON sw_people.population_state
FOR EACH ROW EXECUTE FUNCTION sw_people.record_population_history();

CREATE FUNCTION sw_people.reject_history_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'population history is append-only';
END
$$;
CREATE TRIGGER population_history_immutable
BEFORE UPDATE OR DELETE ON sw_people.population_history
FOR EACH ROW EXECUTE FUNCTION sw_people.reject_history_mutation();

CREATE TABLE sw_people.residence (
  person_id integer NOT NULL REFERENCES sw_people.person(person_id),
  spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  valid_from_tick bigint NOT NULL CHECK (valid_from_tick >= 0),
  valid_to_tick bigint,
  source_ref text,
  PRIMARY KEY (person_id, valid_from_tick),
  CHECK (valid_to_tick IS NULL OR valid_to_tick > valid_from_tick)
);
CREATE UNIQUE INDEX person_one_current_residence_uq
  ON sw_people.residence(person_id)
  WHERE valid_to_tick IS NULL;

CREATE TABLE sw_core.event_person_ref (
  event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  person_id integer NOT NULL REFERENCES sw_people.person(person_id),
  relation_code smallint NOT NULL,
  PRIMARY KEY (event_id, person_id, relation_code)
);
CREATE TABLE sw_core.event_spatial_ref (
  event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  relation_code smallint NOT NULL,
  PRIMARY KEY (event_id, spatial_id, relation_code)
);

-- Seed only the singleton stopped runtime. No people, cases or businesses.
INSERT INTO sw_runtime.state(singleton, state, player_present, bootstrap_open)
VALUES (1, 0, false, true);

INSERT INTO sw_ops.schema_migration(version, migration_name)
VALUES (2, 'runtime_city_population')
ON CONFLICT (version) DO NOTHING;

INSERT INTO sw_ops.storage_operation
  (operation_kind, description, status, measurement_notes)
VALUES
  ('migration', '0002 runtime, canonical geography and population schema', 'succeeded',
   'Record measured before/after database bytes after separately approved deployment.');

COMMIT;
