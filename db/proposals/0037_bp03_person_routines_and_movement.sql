-- BP03 person routines and sourced movement history.
BEGIN;

CREATE TABLE sw_people.person_routine (
 routine_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 person_id integer NOT NULL REFERENCES sw_people.person(person_id),
 routine_code text NOT NULL CHECK (length(btrim(routine_code)) BETWEEN 1 AND 80),
 location_ref text NOT NULL CHECK (length(btrim(location_ref)) BETWEEN 1 AND 200),
 schedule_spec jsonb NOT NULL CHECK (jsonb_typeof(schedule_spec)='object'),
 valid_from_tick bigint NOT NULL CHECK (valid_from_tick>=0),
 valid_to_tick bigint,
 supersedes_routine_id bigint REFERENCES sw_people.person_routine(routine_id),
 source_ref text NOT NULL UNIQUE CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
 actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
 reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
 event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
 recorded_at timestamptz NOT NULL DEFAULT now(),
 CHECK (valid_to_tick IS NULL OR valid_to_tick>valid_from_tick)
);
CREATE INDEX person_routine_person_validity_idx
 ON sw_people.person_routine(person_id,valid_from_tick DESC);

CREATE TABLE sw_people.person_movement_event (
 movement_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 person_id integer NOT NULL REFERENCES sw_people.person(person_id),
 from_location_ref text NOT NULL CHECK (length(btrim(from_location_ref)) BETWEEN 1 AND 200),
 to_location_ref text NOT NULL CHECK (length(btrim(to_location_ref)) BETWEEN 1 AND 200),
 movement_kind text NOT NULL CHECK (movement_kind IN ('observed','estimated','verified')),
 travel_mode text NOT NULL CHECK (travel_mode IN ('walking','cycling','driving','public_transport','other','unknown')),
 confidence numeric(4,3) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
 occurred_tick bigint NOT NULL CHECK (occurred_tick>=0),
 recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
 source_ref text NOT NULL UNIQUE CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
 actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
 reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
 event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
 recorded_at timestamptz NOT NULL DEFAULT now(),
 CHECK (from_location_ref<>to_location_ref),
 CHECK (occurred_tick<=recorded_tick)
);
CREATE INDEX person_movement_person_time_idx
 ON sw_people.person_movement_event(person_id,occurred_tick DESC,movement_id DESC);

CREATE FUNCTION sw_people.reject_person_routine_movement_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 RAISE EXCEPTION '% is append-only; record a new sourced event',TG_TABLE_NAME;
END $$;
CREATE TRIGGER person_routine_immutable
BEFORE UPDATE OR DELETE ON sw_people.person_routine
FOR EACH ROW EXECUTE FUNCTION sw_people.reject_person_routine_movement_mutation();
CREATE TRIGGER person_movement_event_immutable
BEFORE UPDATE OR DELETE ON sw_people.person_movement_event
FOR EACH ROW EXECUTE FUNCTION sw_people.reject_person_routine_movement_mutation();

INSERT INTO sw_core.event_type(event_code,description) VALUES
 ('PERSON_ROUTINE_RECORDED','A sourced person routine or schedule was recorded'),
 ('PERSON_MOVEMENT_RECORDED','A sourced person movement observation or estimate was recorded')
ON CONFLICT(event_code) DO NOTHING;

CREATE FUNCTION sw_people.record_person_routine(
 p_person_id integer,p_routine_code text,p_location_ref text,p_schedule_spec jsonb,
 p_valid_from_tick bigint,p_valid_to_tick bigint,p_supersedes_routine_id bigint,
 p_source_ref text,p_actor_ref text,p_reason text
) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_runtime,sw_core
AS $$
DECLARE v_tick bigint; v_event bigint; v_id bigint; v_existing sw_people.person_routine%ROWTYPE;
BEGIN
 IF p_person_id IS NULL OR p_routine_code IS NULL OR length(btrim(p_routine_code)) NOT BETWEEN 1 AND 80
  OR p_location_ref IS NULL OR length(btrim(p_location_ref)) NOT BETWEEN 1 AND 200
  OR p_schedule_spec IS NULL OR jsonb_typeof(p_schedule_spec)<>'object'
  OR p_valid_from_tick IS NULL OR p_valid_from_tick<0
  OR (p_valid_to_tick IS NOT NULL AND p_valid_to_tick<=p_valid_from_tick)
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'person, routine, location, schedule, validity and provenance are required';
 END IF;
 PERFORM 1 FROM sw_people.person WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'canonical person does not exist'; END IF;
 SELECT * INTO v_existing FROM sw_people.person_routine WHERE source_ref=p_source_ref;
 IF FOUND THEN
  IF ROW(v_existing.person_id,v_existing.routine_code,v_existing.location_ref,v_existing.schedule_spec,
    v_existing.valid_from_tick,v_existing.valid_to_tick,v_existing.supersedes_routine_id)
   IS DISTINCT FROM ROW(p_person_id,p_routine_code,p_location_ref,p_schedule_spec,
    p_valid_from_tick,p_valid_to_tick,p_supersedes_routine_id) THEN
   RAISE EXCEPTION 'routine source reference replay conflicts with original record';
  END IF;
  RETURN v_existing.routine_id;
 END IF;
 IF p_supersedes_routine_id IS NOT NULL AND NOT EXISTS(
  SELECT 1 FROM sw_people.person_routine WHERE routine_id=p_supersedes_routine_id AND person_id=p_person_id
 ) THEN RAISE EXCEPTION 'superseded routine must belong to the same canonical person'; END IF;
 SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
 INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,
  source_ref,attributes,idempotency_key)
 SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('routine_code',p_routine_code,'location_ref',p_location_ref,
   'schedule_spec',p_schedule_spec,'valid_from_tick',p_valid_from_tick,
   'valid_to_tick',p_valid_to_tick,'supersedes_routine_id',p_supersedes_routine_id,
   'actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:ROUTINE:'||p_person_id||':'||p_source_ref
 FROM sw_core.event_type WHERE event_code='PERSON_ROUTINE_RECORDED'
 RETURNING event_id INTO v_event;
 IF v_event IS NULL THEN RAISE EXCEPTION 'PERSON_ROUTINE_RECORDED event type is missing'; END IF;
 INSERT INTO sw_people.person_routine(person_id,routine_code,location_ref,schedule_spec,
  valid_from_tick,valid_to_tick,supersedes_routine_id,source_ref,actor_ref,reason,event_id)
 VALUES(p_person_id,p_routine_code,p_location_ref,p_schedule_spec,p_valid_from_tick,p_valid_to_tick,
  p_supersedes_routine_id,p_source_ref,p_actor_ref,p_reason,v_event)
 RETURNING routine_id INTO v_id;
 RETURN v_id;
END $$;

CREATE FUNCTION sw_people.record_person_movement(
 p_person_id integer,p_from_location_ref text,p_to_location_ref text,p_movement_kind text,
 p_travel_mode text,p_confidence numeric,p_occurred_tick bigint,p_source_ref text,
 p_actor_ref text,p_reason text
) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_runtime,sw_core
AS $$
DECLARE v_tick bigint; v_event bigint; v_id bigint; v_existing sw_people.person_movement_event%ROWTYPE;
BEGIN
 IF p_person_id IS NULL OR p_from_location_ref IS NULL OR length(btrim(p_from_location_ref)) NOT BETWEEN 1 AND 200
  OR p_to_location_ref IS NULL OR length(btrim(p_to_location_ref)) NOT BETWEEN 1 AND 200
  OR p_from_location_ref=p_to_location_ref
  OR p_movement_kind IS NULL OR p_movement_kind NOT IN ('observed','estimated','verified')
  OR p_travel_mode IS NULL OR p_travel_mode NOT IN ('walking','cycling','driving','public_transport','other','unknown')
  OR p_confidence IS NULL OR p_confidence NOT BETWEEN 0 AND 1
  OR p_occurred_tick IS NULL OR p_occurred_tick<0
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'movement, time, confidence and bounded provenance are required';
 END IF;
 PERFORM 1 FROM sw_people.person WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'canonical person does not exist'; END IF;
 SELECT * INTO v_existing FROM sw_people.person_movement_event WHERE source_ref=p_source_ref;
 IF FOUND THEN
  IF ROW(v_existing.person_id,v_existing.from_location_ref,v_existing.to_location_ref,
    v_existing.movement_kind,v_existing.travel_mode,v_existing.confidence,v_existing.occurred_tick)
   IS DISTINCT FROM ROW(p_person_id,p_from_location_ref,p_to_location_ref,
    p_movement_kind,p_travel_mode,p_confidence,p_occurred_tick) THEN
   RAISE EXCEPTION 'movement source reference replay conflicts with original record';
  END IF;
  RETURN v_existing.movement_id;
 END IF;
 SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
 IF p_occurred_tick>v_tick THEN RAISE EXCEPTION 'actual/estimated movement cannot be recorded in the future'; END IF;
 IF EXISTS(SELECT 1 FROM sw_people.person_movement_event
  WHERE person_id=p_person_id AND occurred_tick>p_occurred_tick) THEN
  RAISE EXCEPTION 'movement chronology cannot move behind an already recorded later movement';
 END IF;
 INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,
  source_ref,attributes,idempotency_key)
 SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('from_location_ref',p_from_location_ref,'to_location_ref',p_to_location_ref,
   'movement_kind',p_movement_kind,'travel_mode',p_travel_mode,'confidence',p_confidence,
   'occurred_tick',p_occurred_tick,'actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:MOVEMENT:'||p_person_id||':'||p_source_ref
 FROM sw_core.event_type WHERE event_code='PERSON_MOVEMENT_RECORDED'
 RETURNING event_id INTO v_event;
 IF v_event IS NULL THEN RAISE EXCEPTION 'PERSON_MOVEMENT_RECORDED event type is missing'; END IF;
 INSERT INTO sw_people.person_movement_event(person_id,from_location_ref,to_location_ref,movement_kind,
  travel_mode,confidence,occurred_tick,recorded_tick,source_ref,actor_ref,reason,event_id)
 VALUES(p_person_id,p_from_location_ref,p_to_location_ref,p_movement_kind,p_travel_mode,p_confidence,
  p_occurred_tick,v_tick,p_source_ref,p_actor_ref,p_reason,v_event)
 RETURNING movement_id INTO v_id;
 RETURN v_id;
END $$;

CREATE VIEW sw_people.person_routine_current AS
SELECT r.* FROM sw_people.person_routine r
WHERE NOT EXISTS(SELECT 1 FROM sw_people.person_routine n
 WHERE n.supersedes_routine_id=r.routine_id);

CREATE VIEW sw_people.person_movement_summary AS
SELECT person_id,count(*)::bigint AS movement_event_count,
 max(occurred_tick) AS latest_movement_tick
FROM sw_people.person_movement_event GROUP BY person_id;

REVOKE ALL ON sw_people.person_routine,sw_people.person_movement_event FROM PUBLIC;
GRANT SELECT ON sw_people.person_routine,sw_people.person_movement_event,
 sw_people.person_routine_current,sw_people.person_movement_summary TO sw_game_readonly;
REVOKE ALL ON FUNCTION sw_people.reject_person_routine_movement_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.record_person_routine(integer,text,text,jsonb,bigint,bigint,bigint,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.record_person_movement(integer,text,text,text,text,numeric,bigint,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sw_people.record_person_routine(integer,text,text,jsonb,bigint,bigint,bigint,text,text,text) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_people.record_person_movement(integer,text,text,text,text,numeric,bigint,text,text,text) TO sw_game_command;
COMMIT;
