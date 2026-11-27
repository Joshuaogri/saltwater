-- BP03 population qualification union and canonical person service.
-- Disposable PostgreSQL proposal only. Never apply to Neon without separate approval.
-- Apply after 0002_runtime_city_population.sql and 0009_universal_name_registry.sql.
BEGIN;
DO $$
BEGIN
 IF EXISTS(SELECT 1 FROM sw_people.population_state) THEN
  RAISE EXCEPTION 'BP03 migration requires empty population_state; categories cannot be inferred';
 END IF;
 IF (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>0 THEN
  RAISE EXCEPTION 'BP03 migration requires empty population counter';
 END IF;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS person_source_ref_uq
 ON sw_people.person(source_ref) WHERE source_ref IS NOT NULL;

ALTER TABLE sw_people.population_state
 ADD COLUMN usual_resident boolean NOT NULL DEFAULT false,
 ADD COLUMN physically_present boolean NOT NULL DEFAULT false,
 ADD COLUMN active_police_service boolean NOT NULL DEFAULT false,
 ADD CONSTRAINT population_qualification_scope_consistency
 CHECK ((scope_status=1)=(usual_resident OR physically_present OR active_police_service));

CREATE TABLE sw_people.population_qualification_history(
 event_id bigint PRIMARY KEY REFERENCES sw_core.simulation_event(event_id),
 person_id integer NOT NULL REFERENCES sw_people.person(person_id),
 old_usual_resident boolean NOT NULL,new_usual_resident boolean NOT NULL,
 old_physically_present boolean NOT NULL,new_physically_present boolean NOT NULL,
 old_active_police_service boolean NOT NULL,new_active_police_service boolean NOT NULL,
 effective_tick bigint NOT NULL CHECK(effective_tick>=0),
 recorded_at timestamptz NOT NULL DEFAULT now()
);

CREATE FUNCTION sw_people.reject_qualification_history_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'population qualification history is append-only'; END $$;
CREATE TRIGGER population_qualification_history_immutable
BEFORE UPDATE OR DELETE ON sw_people.population_qualification_history
FOR EACH ROW EXECUTE FUNCTION sw_people.reject_qualification_history_mutation();

CREATE OR REPLACE FUNCTION sw_people.record_qualification_history()
RETURNS trigger LANGUAGE plpgsql AS $
BEGIN
 IF TG_OP='INSERT' THEN
  IF NEW.usual_resident OR NEW.physically_present OR NEW.active_police_service THEN
   INSERT INTO sw_people.population_qualification_history(
    event_id,person_id,old_usual_resident,new_usual_resident,
    old_physically_present,new_physically_present,
    old_active_police_service,new_active_police_service,effective_tick
   ) VALUES (
    NEW.last_event_id,NEW.person_id,false,NEW.usual_resident,
    false,NEW.physically_present,false,NEW.active_police_service,NEW.effective_tick
   );
  END IF;
 ELSIF ROW(NEW.usual_resident,NEW.physically_present,NEW.active_police_service)
    IS DISTINCT FROM ROW(OLD.usual_resident,OLD.physically_present,OLD.active_police_service) THEN
  IF NEW.last_event_id=OLD.last_event_id THEN
   RAISE EXCEPTION 'every qualification change requires a new committed event';
  END IF;
  INSERT INTO sw_people.population_qualification_history(
   event_id,person_id,old_usual_resident,new_usual_resident,
   old_physically_present,new_physically_present,
   old_active_police_service,new_active_police_service,effective_tick
  ) VALUES (
   NEW.last_event_id,NEW.person_id,OLD.usual_resident,NEW.usual_resident,
   OLD.physically_present,NEW.physically_present,
   OLD.active_police_service,NEW.active_police_service,NEW.effective_tick
  );
 END IF;
 RETURN NEW;
END $;
CREATE TRIGGER population_qualification_history_append
AFTER INSERT OR UPDATE OF usual_resident,physically_present,active_police_service
ON sw_people.population_state
FOR EACH ROW EXECUTE FUNCTION sw_people.record_qualification_history();

DROP TRIGGER population_cap_guard ON sw_people.population_state;
CREATE OR REPLACE FUNCTION sw_people.enforce_population_cap()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE current_count integer; old_count integer:=0; new_count integer:=0; adjusted_count integer;
BEGIN
 SELECT living_included INTO current_count
 FROM sw_people.population_counter WHERE singleton=1 FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'population counter singleton is missing'; END IF;
 IF TG_OP='UPDATE' AND OLD.life_status=1
  AND (OLD.usual_resident OR OLD.physically_present OR OLD.active_police_service) THEN old_count:=1; END IF;
 IF NEW.life_status=1
  AND (NEW.usual_resident OR NEW.physically_present OR NEW.active_police_service) THEN new_count:=1; END IF;
 adjusted_count:=current_count-old_count+new_count;
 IF adjusted_count>10000 THEN
  RAISE EXCEPTION 'Saltwater distinct living population union cap of 10000 would be exceeded';
 END IF;
 IF adjusted_count<0 THEN RAISE EXCEPTION 'population counter would become negative'; END IF;
 UPDATE sw_people.population_counter SET living_included=adjusted_count WHERE singleton=1;
 RETURN NEW;
END $$;
CREATE TRIGGER population_cap_guard
BEFORE INSERT OR UPDATE OF life_status,scope_status,usual_resident,physically_present,active_police_service
ON sw_people.population_state
FOR EACH ROW EXECUTE FUNCTION sw_people.enforce_population_cap();

CREATE OR REPLACE VIEW sw_people.population_summary AS
SELECT
 count(*) FILTER(WHERE life_status=1 AND
  (usual_resident OR physically_present OR active_police_service))::integer AS total_living_countable,
 count(*) FILTER(WHERE life_status=1 AND usual_resident)::integer AS usual_residents,
 count(*) FILTER(WHERE life_status=1 AND physically_present)::integer AS physically_present,
 count(*) FILTER(WHERE life_status=1 AND active_police_service)::integer AS active_police_service_members,
 count(*) FILTER(WHERE life_status=1 AND physically_present AND
  NOT usual_resident AND NOT active_police_service)::integer AS nonresident_present_only
FROM sw_people.population_state;

CREATE FUNCTION sw_people.create_person(
 p_given_name text,p_family_name text,p_source_ref text,p_actor_ref text,p_reason text,
 p_middle_name text DEFAULT NULL
) RETURNS integer LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_runtime,sw_core,sw_names AS $$
DECLARE v_person_id integer; v_existing sw_people.person%ROWTYPE;
 v_tick bigint; v_event_id bigint; v_population_event_id bigint; v_display_name text;
BEGIN
 IF p_given_name IS NULL OR btrim(p_given_name)='' OR p_family_name IS NULL OR btrim(p_family_name)=''
  OR (p_middle_name IS NOT NULL AND btrim(p_middle_name)='')
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'given/family names and bounded source, actor and reason are required';
 END IF;
 v_display_name:=concat_ws(' ',btrim(p_given_name),NULLIF(btrim(p_middle_name),''),btrim(p_family_name));
 IF length(v_display_name)>200 THEN RAISE EXCEPTION 'canonical person name exceeds 200 characters'; END IF;
 SELECT * INTO v_existing FROM sw_people.person WHERE source_ref=p_source_ref FOR UPDATE;
 IF FOUND THEN
  IF ROW(v_existing.given_name,v_existing.middle_name,v_existing.family_name)
   IS DISTINCT FROM ROW(btrim(p_given_name),NULLIF(btrim(p_middle_name),''),btrim(p_family_name)) THEN
   RAISE EXCEPTION 'person source_ref already belongs to a different canonical name';
  END IF;
  RETURN v_existing.person_id;
 END IF;
 SELECT world_tick INTO v_tick FROM sw_runtime.state WHERE singleton=1;
 IF NOT FOUND THEN RAISE EXCEPTION 'runtime state singleton is missing'; END IF;
 INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,source_ref,attributes,idempotency_key)
 SELECT event_type_id,clock_timestamp(),v_tick,'person',p_source_ref,
  jsonb_build_object('operation','canonical_person_created','actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:PERSON_CREATE:'||p_source_ref
 FROM sw_core.event_type WHERE event_code='PERSON_CREATED'
 RETURNING event_id INTO v_event_id;
 IF v_event_id IS NULL THEN RAISE EXCEPTION 'PERSON_CREATED event type is missing'; END IF;
 INSERT INTO sw_people.person(given_name,middle_name,family_name,created_tick,source_ref,last_event_id)
 VALUES(btrim(p_given_name),NULLIF(btrim(p_middle_name),''),btrim(p_family_name),v_tick,p_source_ref,v_event_id)
 RETURNING person_id INTO v_person_id;
 PERFORM sw_names.reserve_name('PERSON',v_person_id,'canonical',v_display_name,
  p_source_ref,p_actor_ref,p_reason,v_tick,NULL);
 INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key)
 SELECT event_type_id,clock_timestamp(),v_tick,'person',v_person_id,p_source_ref||':population-initial',
  jsonb_build_object('life_status',1,'usual_resident',false,'physically_present',false,'active_police_service',false),
  'SW-BP03:PERSON_POPULATION_INIT:'||v_person_id
 FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED'
 RETURNING event_id INTO v_population_event_id;
 IF v_population_event_id IS NULL THEN RAISE EXCEPTION 'POPULATION_STATE_CHANGED event type is missing'; END IF;
 INSERT INTO sw_people.population_state(person_id,life_status,scope_status,effective_tick,last_event_id,
  usual_resident,physically_present,active_police_service)
 VALUES(v_person_id,1,0,v_tick,v_population_event_id,false,false,false);
 RETURN v_person_id;
END $$;

CREATE FUNCTION sw_people.set_population_qualifications(
 p_person_id integer,p_usual_resident boolean,p_physically_present boolean,
 p_active_police_service boolean,p_source_ref text,p_actor_ref text,p_reason text
) RETURNS integer LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_runtime,sw_core AS $$
DECLARE v_person integer; v_state sw_people.population_state%ROWTYPE;
 v_tick bigint; v_event_id bigint; v_idempotency_key text; v_scope_status smallint;
BEGIN
 IF p_person_id IS NULL OR p_usual_resident IS NULL OR p_physically_present IS NULL
  OR p_active_police_service IS NULL
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'person, qualification booleans and bounded provenance are required';
 END IF;
 SELECT person_id INTO v_person FROM sw_people.person WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'canonical person does not exist'; END IF;
 SELECT * INTO v_state FROM sw_people.population_state WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'canonical person has no population state'; END IF;
 IF v_state.life_status=2 AND (p_usual_resident OR p_physically_present OR p_active_police_service) THEN
  RAISE EXCEPTION 'a deceased person cannot receive a live population qualification';
 END IF;
 v_idempotency_key:='SW-BP03:POPQUAL:'||p_person_id||':'||p_source_ref;
 IF EXISTS(SELECT 1 FROM sw_core.simulation_event WHERE idempotency_key=v_idempotency_key) THEN
  IF ROW(v_state.usual_resident,v_state.physically_present,v_state.active_police_service)
   IS DISTINCT FROM ROW(p_usual_resident,p_physically_present,p_active_police_service) THEN
   RAISE EXCEPTION 'population qualification idempotency key reused with different values';
  END IF;
  RETURN (SELECT living_included FROM sw_people.population_counter WHERE singleton=1);
 END IF;
 IF ROW(v_state.usual_resident,v_state.physically_present,v_state.active_police_service)
  IS NOT DISTINCT FROM ROW(p_usual_resident,p_physically_present,p_active_police_service) THEN
  RETURN (SELECT living_included FROM sw_people.population_counter WHERE singleton=1);
 END IF;
 SELECT world_tick INTO v_tick FROM sw_runtime.state WHERE singleton=1;
 v_scope_status:=CASE
  WHEN p_usual_resident OR p_physically_present OR p_active_police_service THEN 1
  WHEN v_state.scope_status=2 THEN 2 ELSE 0 END;
 INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key)
 SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('operation','population_qualification_changed','usual_resident',p_usual_resident,
   'physically_present',p_physically_present,'active_police_service',p_active_police_service,
   'actor_ref',p_actor_ref,'reason',p_reason),v_idempotency_key
 FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED'
 RETURNING event_id INTO v_event_id;
 IF v_event_id IS NULL THEN RAISE EXCEPTION 'POPULATION_STATE_CHANGED event type is missing'; END IF;
 UPDATE sw_people.population_state SET scope_status=v_scope_status,
  usual_resident=p_usual_resident,physically_present=p_physically_present,
  active_police_service=p_active_police_service,effective_tick=v_tick,last_event_id=v_event_id
 WHERE person_id=p_person_id;
 RETURN (SELECT living_included FROM sw_people.population_counter WHERE singleton=1);
END $$;

CREATE FUNCTION sw_people.record_person_death(
 p_person_id integer,p_source_ref text,p_actor_ref text,p_reason text
) RETURNS integer LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_runtime,sw_core AS $$
DECLARE v_person integer; v_state sw_people.population_state%ROWTYPE;
 v_tick bigint; v_event_id bigint; v_idempotency_key text;
BEGIN
 IF p_person_id IS NULL OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'person and bounded provenance are required';
 END IF;
 SELECT person_id INTO v_person FROM sw_people.person WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'canonical person does not exist'; END IF;
 SELECT * INTO v_state FROM sw_people.population_state WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'canonical person has no population state'; END IF;
 IF v_state.life_status=2 THEN
  RETURN (SELECT living_included FROM sw_people.population_counter WHERE singleton=1);
 END IF;
 v_idempotency_key:='SW-BP03:PERSON_DEATH:'||p_person_id||':'||p_source_ref;
 IF EXISTS(SELECT 1 FROM sw_core.simulation_event WHERE idempotency_key=v_idempotency_key) THEN
  RAISE EXCEPTION 'death idempotency key exists while person remains living';
 END IF;
 SELECT world_tick INTO v_tick FROM sw_runtime.state WHERE singleton=1;
 INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key)
 SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('operation','person_deceased','actor_ref',p_actor_ref,'reason',p_reason),v_idempotency_key
 FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED'
 RETURNING event_id INTO v_event_id;
 IF v_event_id IS NULL THEN RAISE EXCEPTION 'POPULATION_STATE_CHANGED event type is missing'; END IF;
 UPDATE sw_people.population_state SET life_status=2,scope_status=0,
  usual_resident=false,physically_present=false,active_police_service=false,
  effective_tick=v_tick,last_event_id=v_event_id WHERE person_id=p_person_id;
 RETURN (SELECT living_included FROM sw_people.population_counter WHERE singleton=1);
END $$;

REVOKE ALL ON sw_people.population_qualification_history,sw_people.population_summary FROM PUBLIC;
GRANT SELECT ON sw_people.population_qualification_history,sw_people.population_summary TO sw_game_readonly;
REVOKE ALL ON FUNCTION sw_people.reject_qualification_history_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.record_qualification_history() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.enforce_population_cap() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.create_person(text,text,text,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.set_population_qualifications(integer,boolean,boolean,boolean,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.record_person_death(integer,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sw_people.create_person(text,text,text,text,text,text) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_people.set_population_qualifications(integer,boolean,boolean,boolean,text,text,text) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_people.record_person_death(integer,text,text,text) TO sw_game_command;
COMMIT;
