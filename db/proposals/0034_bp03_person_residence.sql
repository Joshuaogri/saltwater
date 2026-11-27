-- BP03 canonical residence-to-BP02 address linkage.
-- Disposable PostgreSQL acceptance only until separately reviewed and approved.
BEGIN;
CREATE TABLE sw_people.person_residence (
 residence_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 person_id integer NOT NULL REFERENCES sw_people.person(person_id),
 address_source_id text NOT NULL REFERENCES sw_geo.bp02_address(source_id),
 residence_kind text NOT NULL CHECK(residence_kind IN ('permanent','temporary','institutional')),
 residence_status text NOT NULL DEFAULT 'current' CHECK(residence_status IN ('current','ended')),
 effective_from_tick bigint NOT NULL CHECK(effective_from_tick>=0),
 effective_to_tick bigint,
 source_ref text NOT NULL UNIQUE CHECK(length(btrim(source_ref)) BETWEEN 1 AND 200),
 last_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK((residence_status='current' AND effective_to_tick IS NULL)
    OR (residence_status='ended' AND effective_to_tick IS NOT NULL
        AND effective_to_tick>=effective_from_tick))
);
CREATE UNIQUE INDEX person_one_current_residence
 ON sw_people.person_residence(person_id) WHERE residence_status='current';
CREATE INDEX person_residence_address_history
 ON sw_people.person_residence(address_source_id,person_id);
CREATE TABLE sw_people.person_residence_history (
 event_id bigint PRIMARY KEY REFERENCES sw_core.simulation_event(event_id),
 person_id integer NOT NULL REFERENCES sw_people.person(person_id),
 event_kind text NOT NULL CHECK(event_kind IN ('residence_assigned','residence_changed','residence_ended')),
 prior_address_source_id text REFERENCES sw_geo.bp02_address(source_id),
 new_address_source_id text REFERENCES sw_geo.bp02_address(source_id),
 prior_residence_kind text,new_residence_kind text,
 effective_tick bigint NOT NULL CHECK(effective_tick>=0),
 actor_ref text NOT NULL,reason text NOT NULL,
 recorded_at timestamptz NOT NULL DEFAULT now()
);
CREATE FUNCTION sw_people.reject_residence_history_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'person residence history is append-only'; END $$;
CREATE TRIGGER person_residence_history_immutable
BEFORE UPDATE OR DELETE ON sw_people.person_residence_history
FOR EACH ROW EXECUTE FUNCTION sw_people.reject_residence_history_mutation();

CREATE FUNCTION sw_people.set_person_residence(
 p_person_id integer,p_address_source_id text,p_residence_kind text,
 p_source_ref text,p_actor_ref text,p_reason text
) RETURNS bigint LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_geo,sw_runtime,sw_core AS $$
DECLARE
 v_state sw_people.population_state%ROWTYPE; v_old sw_people.person_residence%ROWTYPE;
 v_existing sw_people.person_residence%ROWTYPE; v_tick bigint; v_event_id bigint; v_residence_id bigint;
 v_event_kind text;
BEGIN
 IF p_person_id IS NULL OR p_address_source_id IS NULL OR btrim(p_address_source_id)=''
  OR p_residence_kind IS NULL OR p_residence_kind NOT IN ('permanent','temporary','institutional')
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'person, active BP02 address, residence kind and bounded provenance are required';
 END IF;
 PERFORM 1 FROM sw_people.person WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'canonical person does not exist'; END IF;
 SELECT * INTO v_state FROM sw_people.population_state WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'canonical person has no population state'; END IF;
 IF v_state.life_status<>1 THEN RAISE EXCEPTION 'only a living canonical person can receive a residence'; END IF;
 PERFORM 1 FROM sw_geo.bp02_address WHERE source_id=p_address_source_id
  AND operational_status='ACTIVE_IN_GAME' FOR SHARE;
 IF NOT FOUND THEN RAISE EXCEPTION 'residence address is not an active BP02 gameplay address'; END IF;
 SELECT * INTO v_existing FROM sw_people.person_residence WHERE source_ref=p_source_ref;
 IF FOUND THEN
  IF v_existing.person_id<>p_person_id OR v_existing.address_source_id<>p_address_source_id
   OR v_existing.residence_kind<>p_residence_kind THEN
   RAISE EXCEPTION 'residence source_ref replay conflicts with its original assignment';
  END IF;
  RETURN v_existing.residence_id;
 END IF;
 SELECT * INTO v_old FROM sw_people.person_residence
  WHERE person_id=p_person_id AND residence_status='current' FOR UPDATE;
 IF FOUND AND v_old.address_source_id=p_address_source_id AND v_old.residence_kind=p_residence_kind
  THEN RETURN v_old.residence_id; END IF;
 SELECT world_tick INTO v_tick FROM sw_runtime.state WHERE singleton=1;
 IF NOT FOUND THEN RAISE EXCEPTION 'runtime state singleton is missing'; END IF;
 v_event_kind:=CASE WHEN v_old.residence_id IS NULL THEN 'residence_assigned' ELSE 'residence_changed' END;
 INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,
  source_ref,attributes,idempotency_key)
 SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('operation',v_event_kind,'address_source_id',p_address_source_id,
   'residence_kind',p_residence_kind,'actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:RESIDENCE:'||p_person_id||':'||p_source_ref
 FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED'
 RETURNING event_id INTO v_event_id;
 IF v_event_id IS NULL THEN RAISE EXCEPTION 'POPULATION_STATE_CHANGED event type is missing'; END IF;
 IF v_old.residence_id IS NOT NULL THEN
  UPDATE sw_people.person_residence SET residence_status='ended',
   effective_to_tick=GREATEST(v_tick,v_old.effective_from_tick) WHERE residence_id=v_old.residence_id;
 END IF;
 INSERT INTO sw_people.person_residence(person_id,address_source_id,residence_kind,
  effective_from_tick,source_ref,last_event_id)
 VALUES(p_person_id,p_address_source_id,p_residence_kind,v_tick,p_source_ref,v_event_id)
 RETURNING residence_id INTO v_residence_id;
 INSERT INTO sw_people.person_residence_history(event_id,person_id,event_kind,
  prior_address_source_id,new_address_source_id,prior_residence_kind,new_residence_kind,
  effective_tick,actor_ref,reason)
 VALUES(v_event_id,p_person_id,v_event_kind,v_old.address_source_id,p_address_source_id,
  v_old.residence_kind,p_residence_kind,v_tick,p_actor_ref,p_reason);
 PERFORM sw_people.set_population_qualifications(p_person_id,true,
  v_state.physically_present,v_state.active_police_service,
  'BP03:RESIDENCE-POPULATION:'||v_event_id,p_actor_ref,p_reason);
 RETURN v_residence_id;
END $$;

CREATE FUNCTION sw_people.end_person_residence(
 p_person_id integer,p_source_ref text,p_actor_ref text,p_reason text
) RETURNS integer LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_runtime,sw_core AS $$
DECLARE
 v_state sw_people.population_state%ROWTYPE; v_old sw_people.person_residence%ROWTYPE;
 v_tick bigint; v_event_id bigint;
BEGIN
 IF p_person_id IS NULL OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'person and bounded provenance are required';
 END IF;
 SELECT * INTO v_state FROM sw_people.population_state WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'canonical person has no population state'; END IF;
 SELECT * INTO v_old FROM sw_people.person_residence
  WHERE person_id=p_person_id AND residence_status='current' FOR UPDATE;
 IF NOT FOUND THEN RETURN (SELECT living_included FROM sw_people.population_counter WHERE singleton=1); END IF;
 SELECT world_tick INTO v_tick FROM sw_runtime.state WHERE singleton=1;
 INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,
  source_ref,attributes,idempotency_key)
 SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('operation','residence_ended','address_source_id',v_old.address_source_id,
   'actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:RESIDENCE-END:'||p_person_id||':'||p_source_ref
 FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED'
 RETURNING event_id INTO v_event_id;
 IF v_event_id IS NULL THEN RAISE EXCEPTION 'POPULATION_STATE_CHANGED event type is missing'; END IF;
 UPDATE sw_people.person_residence SET residence_status='ended',
  effective_to_tick=GREATEST(v_tick,v_old.effective_from_tick) WHERE residence_id=v_old.residence_id;
 INSERT INTO sw_people.person_residence_history(event_id,person_id,event_kind,
  prior_address_source_id,prior_residence_kind,effective_tick,actor_ref,reason)
 VALUES(v_event_id,p_person_id,'residence_ended',v_old.address_source_id,
  v_old.residence_kind,v_tick,p_actor_ref,p_reason);
 PERFORM sw_people.set_population_qualifications(p_person_id,false,
  v_state.physically_present,v_state.active_police_service,
  'BP03:RESIDENCE-END-POPULATION:'||v_event_id,p_actor_ref,p_reason);
 RETURN (SELECT living_included FROM sw_people.population_counter WHERE singleton=1);
END $$;
REVOKE ALL ON sw_people.person_residence,sw_people.person_residence_history FROM PUBLIC;
GRANT SELECT ON sw_people.person_residence,sw_people.person_residence_history TO sw_game_readonly;
REVOKE ALL ON FUNCTION sw_people.reject_residence_history_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.set_person_residence(integer,text,text,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.end_person_residence(integer,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sw_people.set_person_residence(integer,text,text,text,text,text) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_people.end_person_residence(integer,text,text,text) TO sw_game_command;
COMMIT;
