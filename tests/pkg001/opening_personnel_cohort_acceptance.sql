-- Disposable-only acceptance for BP06 opening personnel cohort provisioning.
-- The test creates fixture BP03 people inside a transaction and rolls everything back.
\set ON_ERROR_STOP on
BEGIN;
DO $accept$
DECLARE
  v_person_created smallint;
  v_population_changed smallint;
  v_personnel_count integer;
  v_before_population integer;
  v_after_population integer;
  v_members jsonb;
  v_short jsonb;
  v_duplicate jsonb;
  v_missing jsonb;
  v_person_id integer;
  v_event_id bigint;
  i integer;
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM sw_runtime.state
    WHERE singleton=1 AND state=1 AND player_present=false
      AND bootstrap_open=true AND world_tick=0
  ) THEN
    RAISE EXCEPTION 'opening personnel cohort acceptance requires untouched tick-zero bootstrap';
  END IF;

  SELECT event_type_id INTO STRICT v_person_created
  FROM sw_core.event_type WHERE event_code='PERSON_CREATED';
  SELECT event_type_id INTO STRICT v_population_changed
  FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED';

  CREATE TEMP TABLE opening_police_fixture_person(
    person_id integer PRIMARY KEY,
    personnel_category text NOT NULL
  ) ON COMMIT DROP;

  FOR i IN 1..500 LOOP
    INSERT INTO sw_core.simulation_event(
      event_type_id,occurred_at,world_tick,subject_kind,source_ref,attributes,idempotency_key
    ) VALUES (
      v_person_created,clock_timestamp(),0,'person',
      'BP06-OPENING-TEST:person:'||i,
      jsonb_build_object('fixture',true),
      'BP06-OPENING-TEST:person:'||i
    ) RETURNING event_id INTO v_event_id;

    INSERT INTO sw_people.person(
      given_name,family_name,created_tick,source_ref,last_event_id
    ) VALUES (
      'Fixture','Police-'||lpad(i::text,4,'0'),0,
      'BP06-OPENING-TEST:person:'||i,v_event_id
    ) RETURNING person_id INTO v_person_id;

    INSERT INTO sw_core.simulation_event(
      event_type_id,occurred_at,world_tick,subject_kind,subject_id,
      source_ref,attributes,idempotency_key
    ) VALUES (
      v_population_changed,clock_timestamp(),0,'person',v_person_id::text,
      'BP06-OPENING-TEST:population:'||i,
      jsonb_build_object('life_status',1,'scope_status',1),
      'BP06-OPENING-TEST:population:'||i
    ) RETURNING event_id INTO v_event_id;

    INSERT INTO sw_people.population_state(
      person_id,life_status,scope_status,effective_tick,last_event_id
    ) VALUES (v_person_id,1,1,0,v_event_id);

    INSERT INTO opening_police_fixture_person(person_id,personnel_category)
    VALUES (
      v_person_id,
      CASE WHEN i<=400 THEN 'sworn_officer'
           WHEN i<=475 THEN 'civilian_employee'
           ELSE 'technical_professional' END
    );
  END LOOP;

  SELECT jsonb_agg(jsonb_build_object(
    'person_id',person_id,'personnel_category',personnel_category
  ) ORDER BY person_id) INTO v_members
  FROM opening_police_fixture_person;

  SELECT living_included INTO v_before_population
  FROM sw_people.population_counter WHERE singleton=1;
  IF v_before_population<>500 THEN
    RAISE EXCEPTION 'fixture must contain exactly 500 living included people before personnel provisioning';
  END IF;

  SELECT jsonb_agg(value ORDER BY ord) INTO v_short
  FROM jsonb_array_elements(v_members) WITH ORDINALITY AS a(value,ord)
  WHERE ord<=499;

  SELECT jsonb_agg(value ORDER BY ord) INTO v_duplicate
  FROM (
    SELECT value,ord
    FROM jsonb_array_elements(v_members) WITH ORDINALITY AS a(value,ord)
    WHERE ord<=499
    UNION ALL
    SELECT v_members->0,500
  ) duplicate_rows;

  v_missing := jsonb_set(v_members,'{0,person_id}','99999999'::jsonb);

  BEGIN
    PERFORM sw_police.provision_opening_personnel_cohort(v_short,'BP06-OPENING-TEST');
    RAISE EXCEPTION '499-member cohort unexpectedly accepted';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='499-member cohort unexpectedly accepted' THEN RAISE; END IF;
  END;
  BEGIN
    PERFORM sw_police.provision_opening_personnel_cohort(v_duplicate,'BP06-OPENING-TEST');
    RAISE EXCEPTION 'duplicate identity cohort unexpectedly accepted';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='duplicate identity cohort unexpectedly accepted' THEN RAISE; END IF;
  END;
  BEGIN
    PERFORM sw_police.provision_opening_personnel_cohort(v_missing,'BP06-OPENING-TEST');
    RAISE EXCEPTION 'missing canonical person unexpectedly accepted';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='missing canonical person unexpectedly accepted' THEN RAISE; END IF;
  END;

  SELECT sw_police.provision_opening_personnel_cohort(v_members,'BP06-OPENING-TEST')
  INTO v_personnel_count;
  IF v_personnel_count<>500 THEN
    RAISE EXCEPTION 'provisioner returned %, expected 500',v_personnel_count;
  END IF;

  IF sw_police.provision_opening_personnel_cohort(v_members,'BP06-OPENING-TEST')<>500 THEN
    RAISE EXCEPTION 'identical cohort replay was not idempotent';
  END IF;

  IF (SELECT count(*) FROM sw_police.personnel p
      JOIN opening_police_fixture_person f USING(person_id))<>500 THEN
    RAISE EXCEPTION 'exactly 500 canonical people must receive personnel dossiers';
  END IF;
  IF (SELECT count(DISTINCT person_id) FROM sw_police.personnel p
      JOIN opening_police_fixture_person f USING(person_id))<>500 THEN
    RAISE EXCEPTION 'personnel dossier identity linkage is not one-to-one';
  END IF;
  IF (SELECT count(*) FROM sw_police.personnel_service_engagement e
      JOIN sw_police.personnel p USING(personnel_id)
      JOIN opening_police_fixture_person f USING(person_id)
      WHERE e.service_state='active' AND e.is_primary)<>500 THEN
    RAISE EXCEPTION 'each personnel identity requires one active primary service engagement';
  END IF;
  IF (SELECT count(*) FROM sw_police.personnel_service_event e
      JOIN sw_police.personnel p USING(personnel_id)
      JOIN opening_police_fixture_person f USING(person_id)
      WHERE e.event_kind='appointed')<>500 THEN
    RAISE EXCEPTION 'each personnel identity requires one appointment history event';
  END IF;
  IF (SELECT count(*) FROM sw_police.service_number_history h
      JOIN sw_police.personnel p USING(personnel_id)
      JOIN opening_police_fixture_person f USING(person_id)
      WHERE h.event_kind='issued')<>500 THEN
    RAISE EXCEPTION 'each personnel identity requires one issued service number';
  END IF;
  IF (SELECT count(*) FROM sw_police.personnel_service_engagement e
      JOIN sw_police.personnel p USING(personnel_id)
      JOIN opening_police_fixture_person f USING(person_id)
      WHERE (f.personnel_category='sworn_officer' AND e.appointment_type<>'direct_entry')
         OR (f.personnel_category<>'sworn_officer' AND e.appointment_type<>'civilian_appointment')
         OR e.personnel_category<>f.personnel_category)<>0 THEN
    RAISE EXCEPTION 'personnel category and appointment type must be preserved in BP06 service records';
  END IF;

  SELECT living_included INTO v_after_population
  FROM sw_people.population_counter WHERE singleton=1;
  IF v_after_population<>v_before_population THEN
    RAISE EXCEPTION 'personnel provisioning must not create duplicate population count contributions';
  END IF;

  IF (SELECT count(*) FROM sw_police.opening_personnel_cohort_member)<>500 THEN
    RAISE EXCEPTION 'opening cohort member register must contain 500 rows';
  END IF;
  IF (SELECT count(*) FROM sw_police.authorised_post WHERE post_status='vacant')<>500 THEN
    RAISE EXCEPTION 'personnel provisioning must not silently fill any authorised post';
  END IF;
  IF (SELECT count(*) FROM sw_police.career_post_appointment)<>0
     OR (SELECT count(*) FROM sw_police.unit_membership)<>0 THEN
    RAISE EXCEPTION 'personnel provisioning must not silently create BP07 appointments or BP08 memberships';
  END IF;

  RAISE NOTICE 'BP06_OPENING_COHORT_PASS people=500 personnel=500 service_engagements=500 population_delta=0 posts_filled=0';
END
$accept$;
ROLLBACK;
