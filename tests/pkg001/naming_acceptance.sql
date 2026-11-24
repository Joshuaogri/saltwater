-- SW-NAM-001 disposable PostgreSQL acceptance tests.
-- Run after foundation and proposals 0002-0009. Entire test is rolled back.
\set ON_ERROR_STOP on
BEGIN;
UPDATE sw_runtime.state SET state=1,player_present=false WHERE singleton=1 AND state=0;
UPDATE sw_runtime.state SET state=2,player_present=true WHERE singleton=1 AND state=1;
DO $test$
DECLARE
  v_sovereign bigint;
  v_city bigint;
  v_extra integer;
  v_person_event bigint;
  v_person_id integer;
  v_count integer;
  v_old_reservation bigint;
  v_new_reservation bigint;
  v_tick bigint;
  v_initial_tick bigint;
  v_repeat_id bigint;
BEGIN
  SELECT world_tick INTO v_initial_tick FROM sw_runtime.state WHERE singleton=1;
  SELECT spatial_id INTO STRICT v_sovereign FROM sw_geo.entity WHERE entity_code='saltwater-state';
  SELECT spatial_id INTO STRICT v_city FROM sw_geo.entity WHERE entity_code='saltwater-city';

  IF (SELECT count(*) FROM sw_names.registry
      WHERE normalized_key='saltwater' AND status='active'
        AND entity_type='GEOGRAPHY'
        AND (entity_id=v_sovereign OR entity_id=v_city)) <> 2 THEN
    RAISE EXCEPTION 'approved Saltwater root pair was not registered separately';
  END IF;
  IF (SELECT count(*) FROM sw_names.search_name('Saltwater')) <> 2 THEN
    RAISE EXCEPTION 'Saltwater search must return both roots, not silently select one';
  END IF;

  BEGIN
    PERFORM sw_names.add_alias('GEOGRAPHY',v_sovereign,'Saltwater',
      'sw-nam-test','test-runner','alias collision test',0);
    RAISE EXCEPTION 'Saltwater alias unexpectedly bypassed the root exception';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='Saltwater alias unexpectedly bypassed the root exception' THEN RAISE; END IF;
  END;

  SELECT sw_names.reserve_name('GEOGRAPHY',v_sovereign,'canonical','Saltwater',
    'sw-nam-repeat','test-runner','idempotent canon import check',0) INTO v_repeat_id;
  IF v_repeat_id <> (SELECT reservation_id FROM sw_names.name_reservation
      WHERE entity_type='GEOGRAPHY' AND entity_id=v_sovereign AND namespace_slot='SOVEREIGN_ROOT') THEN
    RAISE EXCEPTION 'repeat canon import was not idempotent';
  END IF;

  BEGIN
    PERFORM sw_names.reserve_name('BUSINESS',999,'canonical','Unsupported Entity',
      'sw-nam-test','test-runner','unknown adapter test',0);
    RAISE EXCEPTION 'unregistered entity type unexpectedly accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='unregistered entity type unexpectedly accepted' THEN RAISE; END IF;
  END;

  INSERT INTO sw_geo.entity(entity_code,kind) VALUES ('sw-nam-third-root-test',3)
    RETURNING spatial_id INTO v_extra;
  BEGIN
    INSERT INTO sw_geo.version(spatial_id,version_no,effective_from_tick,name,source_ref,reason_code)
    VALUES (v_extra,1,0,'Saltwater','sw-nam-third-root-test',1);
    RAISE EXCEPTION 'third entity unexpectedly claimed Saltwater';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='third entity unexpectedly claimed Saltwater' THEN RAISE; END IF;
  END;

  INSERT INTO sw_geo.entity(entity_code,kind) VALUES ('sw-nam-road-test',7)
    RETURNING spatial_id INTO v_extra;
  INSERT INTO sw_geo.version(spatial_id,version_no,effective_from_tick,name,source_ref,reason_code)
  VALUES (v_extra,1,0,'Registry Fixture Road','sw-nam-road-test',1);
  SELECT reservation_id INTO STRICT v_old_reservation FROM sw_names.name_reservation
    WHERE entity_type='GEOGRAPHY' AND entity_id=v_extra AND name_form='canonical';

  INSERT INTO sw_geo.version(spatial_id,version_no,effective_from_tick,name,source_ref,reason_code)
  VALUES (v_extra,2,1,'Harbour Registry Road','sw-nam-road-rename',2);
  SELECT reservation_id INTO STRICT v_new_reservation FROM sw_names.name_reservation
    WHERE entity_type='GEOGRAPHY' AND entity_id=v_extra
      AND normalized_key=sw_names.normalize_name('Harbour Registry Road');
  IF sw_names.latest_status(v_old_reservation) <> 'superseded'
     OR sw_names.latest_status(v_new_reservation) <> 'active' THEN
    RAISE EXCEPTION 'geography rename did not preserve append-only name lifecycle';
  END IF;

  SELECT world_tick INTO v_tick FROM sw_runtime.state WHERE singleton=1;
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,source_ref)
  SELECT event_type_id,clock_timestamp(),v_tick,'person','sw-nam-person-test'
  FROM sw_core.event_type WHERE event_code='PERSON_CREATED'
  RETURNING event_id INTO v_person_event;

  BEGIN
    INSERT INTO sw_people.person(given_name,family_name,created_tick,source_ref,last_event_id)
    VALUES ('Registry Fixture','Road',v_tick,'sw-nam-person-test',v_person_event);
    RAISE EXCEPTION 'cross-type duplicate person name unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='cross-type duplicate person name unexpectedly succeeded' THEN RAISE; END IF;
  END;

  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,source_ref)
  SELECT event_type_id,clock_timestamp(),v_tick,'person','sw-nam-person-success'
  FROM sw_core.event_type WHERE event_code='PERSON_CREATED'
  RETURNING event_id INTO v_person_event;
  INSERT INTO sw_people.person(given_name,middle_name,family_name,created_tick,source_ref,last_event_id)
  VALUES ('Aderonke','Mira','Bennett',v_tick,'sw-nam-person-success',v_person_event)
  RETURNING person_id INTO v_person_id;

  IF (SELECT count(*) FROM sw_names.registry
      WHERE entity_type='PERSON' AND entity_id=v_person_id
        AND name_form='canonical' AND status='active') <> 1 THEN
    RAISE EXCEPTION 'person full name did not register through the domain trigger';
  END IF;

  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref)
  SELECT event_type_id,clock_timestamp(),v_tick,'person',v_person_id,'sw-nam-person-rename'
  FROM sw_core.event_type WHERE event_code='PERSON_PROFILE_CHANGED'
  RETURNING event_id INTO v_person_event;
  UPDATE sw_people.person
    SET middle_name='Nneka',last_event_id=v_person_event
    WHERE person_id=v_person_id;
  IF NOT EXISTS (
    SELECT 1 FROM sw_names.registry
    WHERE entity_type='PERSON' AND entity_id=v_person_id
      AND normalized_key=sw_names.normalize_name('Aderonke Nneka Bennett')
      AND status='active'
  ) OR NOT EXISTS (
    SELECT 1 FROM sw_names.registry
    WHERE entity_type='PERSON' AND entity_id=v_person_id
      AND normalized_key=sw_names.normalize_name('Aderonke Mira Bennett')
      AND status='superseded'
  ) THEN
    RAISE EXCEPTION 'person rename failed to preserve stable identity and former name';
  END IF;

  BEGIN
    PERFORM sw_names.add_alias('PERSON',v_person_id,'Registry Fixture Road',
      'sw-nam-test','test-runner','cross-type alias collision',v_tick);
    RAISE EXCEPTION 'cross-type alias collision unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='cross-type alias collision unexpectedly succeeded' THEN RAISE; END IF;
  END;

  BEGIN
    INSERT INTO sw_people.person(given_name,created_tick,source_ref,last_event_id)
    VALUES ('Incomplete',v_tick,'sw-nam-incomplete',v_person_event);
    RAISE EXCEPTION 'incomplete person name unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='incomplete person name unexpectedly succeeded' THEN RAISE; END IF;
  END;

  BEGIN
    INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,source_ref)
    SELECT event_type_id,clock_timestamp(),v_tick,'person','sw-nam-duplicate-person'
    FROM sw_core.event_type WHERE event_code='PERSON_CREATED'
    RETURNING event_id INTO v_person_event;
    INSERT INTO sw_people.person(given_name,family_name,created_tick,source_ref,last_event_id)
    VALUES ('Aderonke','Mira Bennett',v_tick,'sw-nam-duplicate-person',v_person_event);
    RAISE EXCEPTION 'duplicate complete person name unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='duplicate complete person name unexpectedly succeeded' THEN RAISE; END IF;
  END;

  IF (SELECT count(*) FROM sw_names.name_event e
      JOIN sw_names.name_reservation r USING(reservation_id)
      WHERE r.entity_id=v_extra AND r.entity_type='GEOGRAPHY') < 3 THEN
    RAISE EXCEPTION 'name history did not preserve reservation and rename events';
  END IF;

  IF (SELECT world_tick FROM sw_runtime.state WHERE singleton=1) <> v_initial_tick THEN
    RAISE EXCEPTION 'naming acceptance advanced the fictional clock';
  END IF;

  RAISE NOTICE 'SW_NAM_001_ACCEPTANCE_PASS roots=2 geography_rename=pass person_adapter=pass collisions=blocked';
END
$test$;
ROLLBACK;
