-- BP03 sourced, effective-dated person attribute claims.
BEGIN;

CREATE TABLE sw_people.person_attribute_claim (
 claim_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 person_id integer NOT NULL REFERENCES sw_people.person(person_id),
 attribute_code text NOT NULL CHECK (attribute_code IN (
  'preferred_name','language','nationality_descriptor','birth_date','birth_place_ref',
  'age_range','occupation_ref','education_ref','skill_ref','routine_preference',
  'residency_descriptor'
 )),
 attribute_value jsonb NOT NULL CHECK (attribute_value<>'null'::jsonb),
 claim_status text NOT NULL CHECK (claim_status IN ('confirmed','estimated','reported','disputed')),
 confidence numeric(4,3) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
 effective_tick bigint NOT NULL CHECK (effective_tick>=0),
 recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
 source_event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
 supersedes_claim_id bigint REFERENCES sw_people.person_attribute_claim(claim_id),
 source_ref text NOT NULL UNIQUE CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
 actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
 reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
 event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
 recorded_at timestamptz NOT NULL DEFAULT now(),
 CHECK (effective_tick<=recorded_tick)
);
CREATE INDEX person_attribute_claim_person_code_idx
 ON sw_people.person_attribute_claim(person_id,attribute_code,effective_tick DESC,claim_id DESC);
CREATE UNIQUE INDEX person_attribute_claim_one_successor_idx
 ON sw_people.person_attribute_claim(supersedes_claim_id) WHERE supersedes_claim_id IS NOT NULL;

CREATE FUNCTION sw_people.reject_person_attribute_claim_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 RAISE EXCEPTION 'person attribute claims are append-only; record a sourced correction';
END $$;
CREATE TRIGGER person_attribute_claim_immutable
BEFORE UPDATE OR DELETE ON sw_people.person_attribute_claim
FOR EACH ROW EXECUTE FUNCTION sw_people.reject_person_attribute_claim_mutation();

INSERT INTO sw_core.event_type(event_code,description) VALUES
 ('PERSON_ATTRIBUTE_CLAIM_RECORDED','A sourced person attribute claim was recorded')
ON CONFLICT(event_code) DO NOTHING;

CREATE FUNCTION sw_people.record_person_attribute_claim(
 p_person_id integer,p_attribute_code text,p_attribute_value jsonb,p_claim_status text,
 p_confidence numeric,p_effective_tick bigint,p_source_event_id bigint,
 p_supersedes_claim_id bigint,p_source_ref text,p_actor_ref text,p_reason text
) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_runtime,sw_core
AS $$
DECLARE v_tick bigint; v_source_tick bigint; v_event bigint; v_id bigint;
 v_existing sw_people.person_attribute_claim%ROWTYPE;
BEGIN
 IF p_person_id IS NULL OR p_attribute_code IS NULL OR p_attribute_code NOT IN (
  'preferred_name','language','nationality_descriptor','birth_date','birth_place_ref',
  'age_range','occupation_ref','education_ref','skill_ref','routine_preference','residency_descriptor')
  OR p_attribute_value IS NULL OR p_attribute_value='null'::jsonb
  OR p_claim_status IS NULL OR p_claim_status NOT IN ('confirmed','estimated','reported','disputed')
  OR p_confidence IS NULL OR p_confidence NOT BETWEEN 0 AND 1
  OR p_effective_tick IS NULL OR p_effective_tick<0 OR p_source_event_id IS NULL
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'attribute claim, effective time and bounded provenance are required';
 END IF;
 PERFORM 1 FROM sw_people.person WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'canonical person does not exist'; END IF;
 SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
 SELECT world_tick INTO v_source_tick FROM sw_core.simulation_event WHERE event_id=p_source_event_id;
 IF NOT FOUND OR v_source_tick>v_tick THEN RAISE EXCEPTION 'attribute source event is missing or from the future'; END IF;
 IF p_effective_tick>v_tick THEN RAISE EXCEPTION 'attribute effective time cannot be in the future'; END IF;
 IF p_supersedes_claim_id IS NOT NULL AND NOT EXISTS(
  SELECT 1 FROM sw_people.person_attribute_claim
  WHERE claim_id=p_supersedes_claim_id AND person_id=p_person_id AND attribute_code=p_attribute_code
 ) THEN RAISE EXCEPTION 'superseded claim must be for the same person and attribute'; END IF;
 SELECT * INTO v_existing FROM sw_people.person_attribute_claim WHERE source_ref=p_source_ref;
 IF FOUND THEN
  IF ROW(v_existing.person_id,v_existing.attribute_code,v_existing.attribute_value,
    v_existing.claim_status,v_existing.confidence,v_existing.effective_tick,
    v_existing.source_event_id,v_existing.supersedes_claim_id)
   IS DISTINCT FROM ROW(p_person_id,p_attribute_code,p_attribute_value,p_claim_status,
    p_confidence,p_effective_tick,p_source_event_id,p_supersedes_claim_id) THEN
   RAISE EXCEPTION 'attribute claim source reference replay conflicts with original record';
  END IF;
  RETURN v_existing.claim_id;
 END IF;
 INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,
  source_ref,attributes,idempotency_key)
 SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('attribute_code',p_attribute_code,'attribute_value',p_attribute_value,
   'claim_status',p_claim_status,'confidence',p_confidence,'effective_tick',p_effective_tick,
   'source_event_id',p_source_event_id,'supersedes_claim_id',p_supersedes_claim_id,
   'actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:ATTRIBUTE:'||p_person_id||':'||p_source_ref
 FROM sw_core.event_type WHERE event_code='PERSON_ATTRIBUTE_CLAIM_RECORDED'
 RETURNING event_id INTO v_event;
 IF v_event IS NULL THEN RAISE EXCEPTION 'PERSON_ATTRIBUTE_CLAIM_RECORDED event type is missing'; END IF;
 INSERT INTO sw_people.person_attribute_claim(person_id,attribute_code,attribute_value,
  claim_status,confidence,effective_tick,recorded_tick,source_event_id,supersedes_claim_id,
  source_ref,actor_ref,reason,event_id)
 VALUES(p_person_id,p_attribute_code,p_attribute_value,p_claim_status,p_confidence,p_effective_tick,
  v_tick,p_source_event_id,p_supersedes_claim_id,p_source_ref,p_actor_ref,p_reason,v_event)
 RETURNING claim_id INTO v_id;
 RETURN v_id;
END $$;

CREATE VIEW sw_people.person_attribute_claim_summary AS
SELECT person_id,attribute_code,count(*)::bigint AS claim_count,
 count(*) FILTER(WHERE claim_status='disputed')::bigint AS disputed_claim_count,
 max(effective_tick) AS latest_effective_tick
FROM sw_people.person_attribute_claim GROUP BY person_id,attribute_code;

REVOKE ALL ON sw_people.person_attribute_claim FROM PUBLIC;
GRANT SELECT ON sw_people.person_attribute_claim,sw_people.person_attribute_claim_summary TO sw_game_readonly;
REVOKE ALL ON FUNCTION sw_people.reject_person_attribute_claim_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.record_person_attribute_claim(integer,text,jsonb,text,numeric,bigint,bigint,bigint,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sw_people.record_person_attribute_claim(integer,text,jsonb,text,numeric,bigint,bigint,bigint,text,text,text) TO sw_game_command;
COMMIT;
