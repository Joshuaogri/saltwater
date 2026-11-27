-- BP03 individual simulation tiers and permanent police-relevance promotion.
-- Disposable acceptance first; this proposal is not applied to production Neon.
BEGIN;

CREATE TABLE sw_people.person_simulation_state (
  person_id integer PRIMARY KEY REFERENCES sw_people.person(person_id),
  detail_tier smallint NOT NULL DEFAULT 0 CHECK (detail_tier BETWEEN 0 AND 3),
  tier_reason text NOT NULL,
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  last_event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE sw_people.person_simulation_history (
  event_id bigint PRIMARY KEY REFERENCES sw_core.simulation_event(event_id),
  person_id integer NOT NULL REFERENCES sw_people.person(person_id),
  prior_tier smallint,
  new_tier smallint NOT NULL CHECK (new_tier BETWEEN 0 AND 3),
  trigger_kind text NOT NULL,
  trigger_ref text NOT NULL,
  reason text NOT NULL,
  actor_ref text NOT NULL,
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  recorded_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE sw_people.person_relevance_promotion (
  person_id integer PRIMARY KEY REFERENCES sw_people.person(person_id),
  promoted_tick bigint NOT NULL CHECK (promoted_tick >= 0),
  trigger_kind text NOT NULL,
  trigger_ref text NOT NULL,
  reason text NOT NULL,
  actor_ref text NOT NULL,
  event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  permanent boolean NOT NULL DEFAULT true CHECK (permanent),
  recorded_at timestamptz NOT NULL DEFAULT now()
);

CREATE FUNCTION sw_people.initialise_person_simulation_state()
RETURNS trigger LANGUAGE plpgsql AS $
DECLARE v_tick bigint;
BEGIN
 SELECT world_tick INTO STRICT v_tick FROM sw_core.simulation_event WHERE event_id=NEW.last_event_id;
 INSERT INTO sw_people.person_simulation_state(person_id,detail_tier,tier_reason,effective_tick,last_event_id)
 VALUES(NEW.person_id,0,'Registry identity created',v_tick,NEW.last_event_id);
 INSERT INTO sw_people.person_simulation_history(event_id,person_id,prior_tier,new_tier,
  trigger_kind,trigger_ref,reason,actor_ref,effective_tick)
 VALUES(NEW.last_event_id,NEW.person_id,NULL,0,'person_created',
  COALESCE(NEW.source_ref,'person:'||NEW.person_id::text),
  'Initial registry processing tier','system:bp03',v_tick);
 RETURN NEW;
END $;
CREATE TRIGGER person_simulation_state_initialise
AFTER INSERT ON sw_people.person
FOR EACH ROW EXECUTE FUNCTION sw_people.initialise_person_simulation_state();

CREATE FUNCTION sw_people.reject_person_simulation_history_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 RAISE EXCEPTION 'person simulation history is append-only';
END $$;
CREATE TRIGGER person_simulation_history_immutable
BEFORE UPDATE OR DELETE ON sw_people.person_simulation_history
FOR EACH ROW EXECUTE FUNCTION sw_people.reject_person_simulation_history_mutation();
CREATE TRIGGER person_relevance_promotion_immutable
BEFORE UPDATE OR DELETE ON sw_people.person_relevance_promotion
FOR EACH ROW EXECUTE FUNCTION sw_people.reject_person_simulation_history_mutation();

CREATE FUNCTION sw_people.set_person_detail_tier(
 p_person_id integer,p_detail_tier smallint,p_trigger_kind text,p_trigger_ref text,
 p_reason text,p_actor_ref text,p_source_ref text
) RETURNS smallint
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_runtime,sw_core
AS $$
DECLARE v_state sw_people.person_simulation_state%ROWTYPE;
 v_tick bigint; v_event bigint; v_kind text; v_target smallint;
BEGIN
 IF p_person_id IS NULL OR p_detail_tier NOT BETWEEN 0 AND 3
  OR p_trigger_kind IS NULL OR length(btrim(p_trigger_kind)) NOT BETWEEN 1 AND 80
  OR p_trigger_ref IS NULL OR length(btrim(p_trigger_ref)) NOT BETWEEN 1 AND 200
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200 THEN
  RAISE EXCEPTION 'person, valid tier and bounded provenance are required';
 END IF;
 PERFORM 1 FROM sw_people.person WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'canonical person does not exist'; END IF;
 SELECT * INTO v_state FROM sw_people.person_simulation_state
 WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN
  SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,
   source_ref,attributes,idempotency_key)
  SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
   jsonb_build_object('new_tier',p_detail_tier,'trigger_kind',p_trigger_kind,
    'trigger_ref',p_trigger_ref,'reason',p_reason,'actor_ref',p_actor_ref),
   'SW-BP03:DETAIL-TIER:'||p_person_id||':'||p_source_ref
  FROM sw_core.event_type WHERE event_code='PERSON_DETAIL_TIER_CHANGED'
  RETURNING event_id INTO v_event;
  IF v_event IS NULL THEN RAISE EXCEPTION 'PERSON_DETAIL_TIER_CHANGED event type is missing'; END IF;
  INSERT INTO sw_people.person_simulation_state(person_id,detail_tier,tier_reason,effective_tick,last_event_id)
  VALUES(p_person_id,p_detail_tier,p_reason,v_tick,v_event);
  INSERT INTO sw_people.person_simulation_history(event_id,person_id,prior_tier,new_tier,
   trigger_kind,trigger_ref,reason,actor_ref,effective_tick)
  VALUES(v_event,p_person_id,NULL,p_detail_tier,p_trigger_kind,p_trigger_ref,p_reason,p_actor_ref,v_tick);
  v_state.detail_tier:=p_detail_tier;
 ELSE
  IF v_state.detail_tier=3 AND p_detail_tier<3 THEN
   RAISE EXCEPTION 'tier 3 is permanent and cannot be downgraded';
  END IF;
  IF v_state.detail_tier=p_detail_tier THEN RETURN v_state.detail_tier; END IF;
  SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,
   source_ref,attributes,idempotency_key)
  SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
   jsonb_build_object('prior_tier',v_state.detail_tier,'new_tier',p_detail_tier,
    'trigger_kind',p_trigger_kind,'trigger_ref',p_trigger_ref,'reason',p_reason,'actor_ref',p_actor_ref),
   'SW-BP03:DETAIL-TIER:'||p_person_id||':'||p_source_ref
  FROM sw_core.event_type WHERE event_code='PERSON_DETAIL_TIER_CHANGED'
  RETURNING event_id INTO v_event;
  IF v_event IS NULL THEN RAISE EXCEPTION 'PERSON_DETAIL_TIER_CHANGED event type is missing'; END IF;
  UPDATE sw_people.person_simulation_state SET detail_tier=p_detail_tier,tier_reason=p_reason,
   effective_tick=v_tick,last_event_id=v_event,updated_at=now() WHERE person_id=p_person_id;
  INSERT INTO sw_people.person_simulation_history(event_id,person_id,prior_tier,new_tier,
   trigger_kind,trigger_ref,reason,actor_ref,effective_tick)
  VALUES(v_event,p_person_id,v_state.detail_tier,p_detail_tier,p_trigger_kind,p_trigger_ref,
   p_reason,p_actor_ref,v_tick);
 END IF;
 RETURN p_detail_tier;
END $$;

CREATE FUNCTION sw_people.promote_person_persistently(
 p_person_id integer,p_trigger_kind text,p_trigger_ref text,p_reason text,
 p_actor_ref text,p_source_ref text
) RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_runtime,sw_core
AS $$
DECLARE v_tick bigint; v_event bigint; v_existing sw_people.person_relevance_promotion%ROWTYPE;
BEGIN
 IF p_person_id IS NULL OR p_trigger_kind IS NULL OR length(btrim(p_trigger_kind)) NOT BETWEEN 1 AND 80
  OR p_trigger_ref IS NULL OR length(btrim(p_trigger_ref)) NOT BETWEEN 1 AND 200
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200 THEN
  RAISE EXCEPTION 'person and bounded promotion provenance are required';
 END IF;
 PERFORM 1 FROM sw_people.person WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'canonical person does not exist'; END IF;
 SELECT * INTO v_existing FROM sw_people.person_relevance_promotion WHERE person_id=p_person_id;
 IF FOUND THEN
  IF v_existing.trigger_kind=p_trigger_kind AND v_existing.trigger_ref=p_trigger_ref THEN RETURN false; END IF;
  RETURN false;
 END IF;
 SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
 INSERT INTO sw_core.event_type(event_code,description)
 VALUES('PERSON_PERSISTENTLY_PROMOTED','A person was permanently promoted to full simulation detail')
 ON CONFLICT(event_code) DO NOTHING;
 INSERT INTO sw_core.event_type(event_code,description)
 VALUES('PERSON_DETAIL_TIER_CHANGED','A person simulation detail tier changed')
 ON CONFLICT(event_code) DO NOTHING;
 INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,
  source_ref,attributes,idempotency_key)
 SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('trigger_kind',p_trigger_kind,'trigger_ref',p_trigger_ref,
   'reason',p_reason,'actor_ref',p_actor_ref,'permanent',true),
  'SW-BP03:PROMOTION:'||p_person_id
 FROM sw_core.event_type WHERE event_code='PERSON_PERSISTENTLY_PROMOTED'
 RETURNING event_id INTO v_event;
 IF v_event IS NULL THEN RAISE EXCEPTION 'PERSON_PERSISTENTLY_PROMOTED event type is missing'; END IF;
 INSERT INTO sw_people.person_relevance_promotion(person_id,promoted_tick,trigger_kind,trigger_ref,
  reason,actor_ref,event_id)
 VALUES(p_person_id,v_tick,p_trigger_kind,p_trigger_ref,p_reason,p_actor_ref,v_event);
 PERFORM sw_people.set_person_detail_tier(p_person_id,3::smallint,p_trigger_kind,p_trigger_ref,
  'Permanent police-relevance promotion: '||p_reason,p_actor_ref,p_source_ref||':tier3');
 RETURN true;
END $$;

INSERT INTO sw_core.event_type(event_code,description) VALUES
 ('PERSON_DETAIL_TIER_CHANGED','A person simulation detail tier changed'),
 ('PERSON_PERSISTENTLY_PROMOTED','A person was permanently promoted to full simulation detail')
ON CONFLICT(event_code) DO NOTHING;

CREATE VIEW sw_people.person_simulation_summary AS
SELECT p.person_id,COALESCE(s.detail_tier,0)::smallint AS detail_tier,
       (r.person_id IS NOT NULL) AS permanently_promoted,
       r.trigger_kind,r.trigger_ref,r.promoted_tick
FROM sw_people.person p
LEFT JOIN sw_people.person_simulation_state s USING(person_id)
LEFT JOIN sw_people.person_relevance_promotion r USING(person_id);

REVOKE ALL ON sw_people.person_simulation_state,sw_people.person_simulation_history,
 sw_people.person_relevance_promotion FROM PUBLIC;
GRANT SELECT ON sw_people.person_simulation_state,sw_people.person_simulation_history,
 sw_people.person_relevance_promotion,sw_people.person_simulation_summary TO sw_game_readonly;
REVOKE ALL ON FUNCTION sw_people.reject_person_simulation_history_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.set_person_detail_tier(integer,smallint,text,text,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.promote_person_persistently(integer,text,text,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sw_people.set_person_detail_tier(integer,smallint,text,text,text,text,text) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_people.promote_person_persistently(integer,text,text,text,text,text) TO sw_game_command;
COMMIT;
