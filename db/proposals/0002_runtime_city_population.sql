-- PROPOSAL ONLY — PKG-001 / migration 0002.
-- DO NOT APPLY TO NEON OR ANY AUTHORITATIVE DATABASE.
-- Requires 0001 foundation; execute only after separate explicit approval.
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
  world_tick bigint NOT NULL DEFAULT 0 CHECK (world_tick >= 0),
  calendar_day integer NOT NULL DEFAULT 0 CHECK (calendar_day >= 0),
  minute_of_day smallint NOT NULL DEFAULT 0 CHECK (minute_of_day BETWEEN 0 AND 1439),
  last_event_id bigint,
  updated_at timestamptz NOT NULL DEFAULT now(),
  CHECK (state <> 2 OR player_present),
  CHECK (state <> 0 OR NOT player_present)
);

-- World tick can advance only from an actively running, player-present state.
CREATE FUNCTION sw_runtime.guard_state_update() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
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

CREATE UNIQUE INDEX simulation_event_idempotency_uq
  ON sw_core.simulation_event(idempotency_key)
  WHERE idempotency_key IS NOT NULL;
CREATE INDEX simulation_event_tick_idx
  ON sw_core.simulation_event(world_tick, event_id);

INSERT INTO sw_core.event_type(event_code, description) VALUES
 ('RUNTIME_START', 'Simulation runtime started'),
 ('RUNTIME_PAUSE', 'Simulation paused'),
 ('RUNTIME_RESUME', 'Simulation resumed'),
 ('RUNTIME_STOP', 'Simulation stopped'),
 ('RUNTIME_RECOVERY', 'Simulation recovery transition'),
 ('CLOCK_ADVANCE', 'One committed in-world clock tick'),
 ('GEO_CREATED', 'Canonical geographic identity created'),
 ('GEO_VERSIONED', 'Geographic version recorded'),
 ('PERSON_CREATED', 'Canonical person identity created'),
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

  IF event_code NOT IN
     ('RUNTIME_START','RUNTIME_PAUSE','RUNTIME_RESUME','RUNTIME_STOP','RUNTIME_RECOVERY')
     AND NOT (runtime_state = 2 AND present) THEN
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
  parent_id integer REFERENCES sw_geo.entity(spatial_id),
  name text NOT NULL,
  active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (parent_id IS NULL OR parent_id <> spatial_id)
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
  geometry_format smallint,
  geometry_payload bytea,
  geometry_sha256 bytea,
  source_ref text,
  reason_code smallint,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (spatial_id, version_no),
  CHECK (
    (geometry_payload IS NULL AND geometry_format IS NULL AND geometry_sha256 IS NULL)
    OR
    (geometry_payload IS NOT NULL AND geometry_format IS NOT NULL
      AND geometry_sha256 IS NOT NULL AND octet_length(geometry_sha256) = 32)
  )
);

INSERT INTO sw_geo.entity(entity_code, kind, parent_id, name)
VALUES ('saltwater-state', 1, NULL, 'Saltwater')
ON CONFLICT (entity_code) DO NOTHING;

INSERT INTO sw_geo.entity(entity_code, kind, parent_id, name)
SELECT 'saltwater-city', 2, spatial_id, 'Saltwater'
FROM sw_geo.entity
WHERE entity_code = 'saltwater-state'
ON CONFLICT (entity_code) DO NOTHING;

INSERT INTO sw_geo.version(spatial_id, version_no, effective_from_tick, source_ref, reason_code)
SELECT spatial_id, 1, 0, 'approved-project-canon', 1
FROM sw_geo.entity
WHERE entity_code IN ('saltwater-state','saltwater-city')
ON CONFLICT (spatial_id, version_no) DO NOTHING;

-- Canonical person identity. No fabricated residents are inserted.
CREATE TABLE sw_people.person (
  person_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  given_name text,
  middle_name text,
  family_name text,
  created_tick bigint NOT NULL CHECK (created_tick >= 0),
  source_ref text,
  created_at timestamptz NOT NULL DEFAULT now()
);

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

CREATE FUNCTION sw_people.enforce_population_cap() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  current_count integer;
BEGIN
  -- Serialises competing admissions so concurrent transactions cannot exceed 10,000.
  PERFORM pg_advisory_xact_lock(57001, 1);

  IF NEW.life_status = 1 AND NEW.scope_status = 1 THEN
    SELECT count(*) INTO current_count
      FROM sw_people.population_state
      WHERE life_status = 1
        AND scope_status = 1
        AND person_id <> NEW.person_id;

    IF current_count >= 10000 THEN
      RAISE EXCEPTION 'Saltwater living population cap of 10000 would be exceeded';
    END IF;
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER population_cap_guard
BEFORE INSERT OR UPDATE OF life_status, scope_status
ON sw_people.population_state
FOR EACH ROW EXECUTE FUNCTION sw_people.enforce_population_cap();

-- Append-only history of population/life-state transitions.
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
INSERT INTO sw_runtime.state(singleton, state, player_present)
VALUES (1, 0, false);

INSERT INTO sw_ops.schema_migration(version, migration_name)
VALUES (2, 'runtime_city_population_proposal')
ON CONFLICT (version) DO NOTHING;

COMMIT;
