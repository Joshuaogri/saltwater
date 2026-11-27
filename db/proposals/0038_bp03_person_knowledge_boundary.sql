-- BP03 NPC/person knowledge provenance and chronology boundary.
BEGIN;

CREATE TABLE sw_people.person_knowledge_item (
 knowledge_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 person_id integer NOT NULL REFERENCES sw_people.person(person_id),
 knowledge_kind text NOT NULL CHECK (knowledge_kind IN ('observed','received','inferred')),
 information_ref text NOT NULL CHECK (length(btrim(information_ref)) BETWEEN 1 AND 240),
 source_event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
 source_person_id integer REFERENCES sw_people.person(person_id),
 acquired_tick bigint NOT NULL CHECK (acquired_tick>=0),
 recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
 confidence numeric(4,3) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
 source_ref text NOT NULL UNIQUE CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
 actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
 reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
 event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
 recorded_at timestamptz NOT NULL DEFAULT now(),
 CHECK (acquired_tick<=recorded_tick)
);
CREATE INDEX person_knowledge_person_time_idx
 ON sw_people.person_knowledge_item(person_id,acquired_tick,knowledge_id);

CREATE FUNCTION sw_people.reject_person_knowledge_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 RAISE EXCEPTION 'person knowledge is append-only; record a sourced correction or later acquisition';
END $$;
CREATE TRIGGER person_knowledge_immutable
BEFORE UPDATE OR DELETE ON sw_people.person_knowledge_item
FOR EACH ROW EXECUTE FUNCTION sw_people.reject_person_knowledge_mutation();

INSERT INTO sw_core.event_type(event_code,description) VALUES
 ('PERSON_KNOWLEDGE_ACQUIRED','A person acquired sourced information within their knowledge boundary')
ON CONFLICT(event_code) DO NOTHING;

CREATE FUNCTION sw_people.record_person_knowledge(
 p_person_id integer,p_knowledge_kind text,p_information_ref text,p_source_event_id bigint,
 p_source_person_id integer,p_acquired_tick bigint,p_confidence numeric,p_source_ref text,
 p_actor_ref text,p_reason text
) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_runtime,sw_core
AS $$
DECLARE v_tick bigint; v_source_tick bigint; v_life_status smallint;
 v_event bigint; v_id bigint; v_existing sw_people.person_knowledge_item%ROWTYPE;
BEGIN
 IF p_person_id IS NULL OR p_knowledge_kind IS NULL
  OR p_knowledge_kind NOT IN ('observed','received','inferred')
  OR p_information_ref IS NULL OR length(btrim(p_information_ref)) NOT BETWEEN 1 AND 240
  OR p_source_event_id IS NULL OR p_acquired_tick IS NULL OR p_acquired_tick<0
  OR p_confidence IS NULL OR p_confidence NOT BETWEEN 0 AND 1
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'knowledge, source event, acquisition time, confidence and provenance are required';
 END IF;
 SELECT ps.life_status INTO v_life_status
 FROM sw_people.population_state ps WHERE ps.person_id=p_person_id FOR UPDATE;
 IF NOT FOUND OR v_life_status<>1 THEN
  RAISE EXCEPTION 'knowledge recipient must be a living canonical person';
 END IF;
 IF p_source_person_id IS NOT NULL AND NOT EXISTS(
  SELECT 1 FROM sw_people.person WHERE person_id=p_source_person_id
 ) THEN RAISE EXCEPTION 'knowledge source person does not exist'; END IF;
 SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
 SELECT world_tick INTO v_source_tick FROM sw_core.simulation_event WHERE event_id=p_source_event_id;
 IF NOT FOUND THEN RAISE EXCEPTION 'knowledge source event does not exist'; END IF;
 IF v_source_tick>p_acquired_tick THEN
  RAISE EXCEPTION 'a person cannot acquire knowledge before its source event occurs';
 END IF;
 IF p_acquired_tick>v_tick THEN
  RAISE EXCEPTION 'knowledge acquisition cannot be recorded in the future';
 END IF;
 SELECT * INTO v_existing FROM sw_people.person_knowledge_item WHERE source_ref=p_source_ref;
 IF FOUND THEN
  IF ROW(v_existing.person_id,v_existing.knowledge_kind,v_existing.information_ref,
    v_existing.source_event_id,v_existing.source_person_id,v_existing.acquired_tick,v_existing.confidence)
   IS DISTINCT FROM ROW(p_person_id,p_knowledge_kind,p_information_ref,
    p_source_event_id,p_source_person_id,p_acquired_tick,p_confidence) THEN
   RAISE EXCEPTION 'knowledge source reference replay conflicts with original record';
  END IF;
  RETURN v_existing.knowledge_id;
 END IF;
 INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,
  source_ref,attributes,idempotency_key)
 SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('knowledge_kind',p_knowledge_kind,'information_ref',p_information_ref,
   'source_event_id',p_source_event_id,'source_person_id',p_source_person_id,
   'acquired_tick',p_acquired_tick,'confidence',p_confidence,'actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:KNOWLEDGE:'||p_person_id||':'||p_source_ref
 FROM sw_core.event_type WHERE event_code='PERSON_KNOWLEDGE_ACQUIRED'
 RETURNING event_id INTO v_event;
 IF v_event IS NULL THEN RAISE EXCEPTION 'PERSON_KNOWLEDGE_ACQUIRED event type is missing'; END IF;
 INSERT INTO sw_people.person_knowledge_item(person_id,knowledge_kind,information_ref,
  source_event_id,source_person_id,acquired_tick,recorded_tick,confidence,source_ref,
  actor_ref,reason,event_id)
 VALUES(p_person_id,p_knowledge_kind,p_information_ref,p_source_event_id,p_source_person_id,
  p_acquired_tick,v_tick,p_confidence,p_source_ref,p_actor_ref,p_reason,v_event)
 RETURNING knowledge_id INTO v_id;
 RETURN v_id;
END $$;

CREATE VIEW sw_people.person_knowledge_summary AS
SELECT person_id,count(*)::bigint AS knowledge_item_count,
 max(acquired_tick) AS latest_acquisition_tick
FROM sw_people.person_knowledge_item GROUP BY person_id;

REVOKE ALL ON sw_people.person_knowledge_item FROM PUBLIC;
GRANT SELECT ON sw_people.person_knowledge_item,sw_people.person_knowledge_summary TO sw_game_readonly;
REVOKE ALL ON FUNCTION sw_people.reject_person_knowledge_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.record_person_knowledge(integer,text,text,bigint,integer,bigint,numeric,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sw_people.record_person_knowledge(integer,text,text,bigint,integer,bigint,numeric,text,text,text) TO sw_game_command;
COMMIT;
