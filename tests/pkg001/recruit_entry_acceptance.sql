-- PKG-003 disposable PostgreSQL end-to-end acceptance.
-- Run after 0001, 0002, 0003 and 0004 in a fresh disposable database.
\set ON_ERROR_STOP on
DO $$
DECLARE
  v_admin uuid := gen_random_uuid();
  v_unapproved uuid := gen_random_uuid();
  v_player uuid := gen_random_uuid();
  v_second_player uuid := gen_random_uuid();
  v_intake uuid;
  v_replayed_intake uuid;
  v_career uuid;
  v_replayed_career uuid;
  v_person_a integer;
  v_person_b integer;
  v_event_type smallint;
  v_event bigint;
  v_count integer;
  v_tick bigint;
BEGIN
  INSERT INTO sw_auth.policy_version(policy_version,description,active)
  VALUES ('pkg003-test','Disposable PKG-003 acceptance policy',true);

  INSERT INTO sw_auth.principal(principal_id,issuer,subject,principal_kind,status)
  VALUES (v_admin,'saltwater-test','recruitment-approver','administrator','active'),
         (v_unapproved,'saltwater-test','unapproved-user','officer','active');
  INSERT INTO sw_auth.principal_role(principal_id,role_code,assigned_by)
  VALUES (v_admin,'recruitment_approver',v_admin);

  UPDATE sw_runtime.state SET state=1 WHERE singleton=1;

  SELECT event_type_id INTO STRICT v_event_type FROM sw_core.event_type WHERE event_code='PERSON_CREATED';
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,source_ref,attributes,idempotency_key)
  VALUES (v_event_type,clock_timestamp(),0,'person','pkg003-supervisor-a','{}','pkg003-supervisor-a')
  RETURNING event_id INTO v_event;
  INSERT INTO sw_people.person(created_tick,source_ref,last_event_id)
  VALUES (0,'pkg003-supervisor-a',v_event) RETURNING person_id INTO v_person_a;

  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,source_ref,attributes,idempotency_key)
  VALUES (v_event_type,clock_timestamp(),0,'person','pkg003-supervisor-b','{}','pkg003-supervisor-b')
  RETURNING event_id INTO v_event;
  INSERT INTO sw_people.person(created_tick,source_ref,last_event_id)
  VALUES (0,'pkg003-supervisor-b',v_event) RETURNING person_id INTO v_person_b;

  SELECT event_type_id INTO STRICT v_event_type FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED';
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key)
  VALUES (v_event_type,clock_timestamp(),0,'person',v_person_a,'pkg003-supervisor-a','{"life_status":1,"scope_status":1}','pkg003-supervisor-a-pop')
  RETURNING event_id INTO v_event;
  INSERT INTO sw_people.population_state VALUES (v_person_a,1,1,0,v_event);

  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key)
  VALUES (v_event_type,clock_timestamp(),0,'person',v_person_b,'pkg003-supervisor-b','{"life_status":1,"scope_status":1}','pkg003-supervisor-b-pop')
  RETURNING event_id INTO v_event;
  INSERT INTO sw_people.population_state VALUES (v_person_b,1,1,0,v_event);

  UPDATE sw_runtime.state SET bootstrap_open=false WHERE singleton=1;
  UPDATE sw_runtime.state SET state=2,player_present=true WHERE singleton=1;

  SELECT event_type_id INTO STRICT v_event_type FROM sw_core.event_type WHERE event_code='PERSONNEL_APPOINTED';
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key)
  VALUES (v_event_type,clock_timestamp(),0,'person',v_person_a,'pkg003-fixture-supervisor',
          '{"standing":"established"}','pkg003-fixture-supervisor-appointment')
  RETURNING event_id INTO v_event;
  INSERT INTO sw_police.personnel(personnel_id,person_id,service_number,service_standing,service_status,
    supervisor_person_id,appointment_tick,appointment_source,appointment_event_id)
  VALUES (gen_random_uuid(),v_person_a,'SWP-00000001','established','active',
    v_person_b,0,'PKG-003 disposable test fixture',v_event);
  INSERT INTO sw_police.recruit_supervisor_authorisation(person_id,authorised_by_principal_id,authority_source,effective_tick)
  VALUES (v_person_a,v_admin,'PKG-003 disposable test fixture',0);

  v_intake := sw_police.request_recruit_intake(v_player,'Test Player','pkg003-request-0001');
  v_replayed_intake := sw_police.request_recruit_intake(v_player,'Test Player','pkg003-request-0001');
  IF v_intake <> v_replayed_intake THEN RAISE EXCEPTION 'request idempotency failed'; END IF;

  SELECT count(*) INTO v_count FROM sw_people.person;
  IF v_count <> 2 THEN RAISE EXCEPTION 'pending intake created a person prematurely'; END IF;

  BEGIN
    PERFORM sw_police.accept_recruit_intake(v_intake,v_person_a,'Test appointment','pkg003-bad-approver',v_unapproved,'Player');
    RAISE EXCEPTION 'unauthorised appointment unexpectedly succeeded';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM = 'unauthorised appointment unexpectedly succeeded' THEN RAISE; END IF;
  END;
  SELECT count(*) INTO v_count FROM sw_people.person;
  IF v_count <> 2 THEN RAISE EXCEPTION 'unauthorised appointment left a partial person'; END IF;

  BEGIN
    PERFORM sw_police.accept_recruit_intake(v_intake,2147483000,'Test appointment','pkg003-bad-supervisor',v_admin,'Player');
    RAISE EXCEPTION 'missing supervisor unexpectedly succeeded';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM = 'missing supervisor unexpectedly succeeded' THEN RAISE; END IF;
  END;
  SELECT count(*) INTO v_count FROM sw_people.person;
  IF v_count <> 2 THEN RAISE EXCEPTION 'failed supervisor check left a partial person'; END IF;

  v_career := sw_police.accept_recruit_intake(v_intake,v_person_a,'Authorised recruitment decision',
    'pkg003-accept-0001',v_admin,'Player');
  v_replayed_career := sw_police.accept_recruit_intake(v_intake,v_person_a,'Authorised recruitment decision',
    'pkg003-accept-replay',v_admin,'Player');
  IF v_career <> v_replayed_career THEN RAISE EXCEPTION 'appointment replay created a different career'; END IF;

  SELECT count(*) INTO v_count FROM sw_people.person;
  IF v_count <> 3 THEN RAISE EXCEPTION 'accepted recruit did not create exactly one canonical person'; END IF;
  IF (SELECT living_included FROM sw_people.population_counter WHERE singleton=1) <> 3 THEN
    RAISE EXCEPTION 'population counter did not include recruit exactly once';
  END IF;
  IF (SELECT count(*) FROM sw_police.personnel WHERE service_standing='recruit') <> 1 THEN
    RAISE EXCEPTION 'recruit personnel record missing or duplicated';
  END IF;
  IF (SELECT count(*) FROM sw_police.career_episode WHERE career_id=v_career AND career_stage='recruit' AND career_status='active') <> 1 THEN
    RAISE EXCEPTION 'active recruit career missing';
  END IF;
  IF (SELECT count(*) FROM sw_police.lifecycle_event WHERE career_id=v_career AND event_kind='career_opened') <> 1 THEN
    RAISE EXCEPTION 'career lifecycle history missing';
  END IF;
  IF (SELECT count(*) FROM sw_police.player_career_status WHERE player_id=v_player AND intake_status='accepted') <> 1 THEN
    RAISE EXCEPTION 'player career status projection incorrect';
  END IF;

  v_intake := sw_police.request_recruit_intake(v_second_player,'Second Player','pkg003-request-0002');
  UPDATE sw_runtime.state SET state=3 WHERE singleton=1;
  SELECT world_tick INTO v_tick FROM sw_runtime.state WHERE singleton=1;
  BEGIN
    PERFORM sw_police.accept_recruit_intake(v_intake,v_person_a,'Paused appointment','pkg003-paused-accept',v_admin,'Second');
    RAISE EXCEPTION 'appointment unexpectedly succeeded while paused';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM = 'appointment unexpectedly succeeded while paused' THEN RAISE; END IF;
  END;
  IF (SELECT world_tick FROM sw_runtime.state WHERE singleton=1) <> v_tick THEN
    RAISE EXCEPTION 'world tick changed while paused';
  END IF;

  RAISE NOTICE 'PKG003_ACCEPTANCE_PASS people=3 population=3 career=%',v_career;
END
$$;
