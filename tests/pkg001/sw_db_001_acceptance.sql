-- SW-DB-001 disposable acceptance. Requires the opening fixture at exactly 9,500 people.
\set ON_ERROR_STOP on
DO $$
DECLARE
  v_batch bigint;
  v_person integer;
  v_event bigint;
  v_business bigint;
  v_temp_business bigint;
  v_name text;
  v_before bigint;
BEGIN
  SELECT batch_id INTO v_batch FROM sw_ops.world_provisioning_batch
  WHERE config_version='saltwater-opening-fixture-v2';
  IF v_batch IS NULL THEN RAISE EXCEPTION 'opening provisioning manifest missing'; END IF;
  IF NOT EXISTS (SELECT 1 FROM sw_ops.world_provisioning_batch WHERE batch_id=v_batch AND environment_scope='DISPOSABLE_TEST_ONLY') THEN
    RAISE EXCEPTION 'fixture manifest is not explicitly marked disposable-only';
  END IF;
  IF (SELECT count(*) FROM sw_ops.provisioning_content_checksum WHERE batch_id=v_batch)<>2 THEN
    RAISE EXCEPTION 'person and business content checksums are not both recorded';
  END IF;

  IF (SELECT count(*) FROM sw_people.person)<>9500
     OR (SELECT count(*) FROM sw_people.population_state WHERE life_status=1 AND scope_status=1)<>9500
     OR (SELECT count(*) FROM sw_people.population_state WHERE usual_resident)<>9000
     OR (SELECT count(*) FROM sw_people.population_state WHERE physically_present)<>500
     OR (SELECT count(*) FROM sw_people.population_state WHERE active_police_service)<>0
     OR (SELECT total_living_countable FROM sw_people.population_summary)<>9500
     OR (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>9500 THEN
    RAISE EXCEPTION 'opening population does not reconcile to 9,500';
  END IF;
  IF (SELECT count(*) FROM sw_test.person_cohort WHERE batch_id=v_batch AND cohort='RESIDENT')<>9000
     OR (SELECT count(*) FROM sw_test.person_cohort WHERE batch_id=v_batch AND cohort='POLICE_SUBSET')<>500 THEN
    RAISE EXCEPTION 'opening resident and police-subset cohorts do not reconcile';
  END IF;
  IF (SELECT count(DISTINCT person_id) FROM sw_test.person_cohort WHERE batch_id=v_batch)<>9500 THEN
    RAISE EXCEPTION 'opening fixture duplicates canonical person identities';
  END IF;
  IF (SELECT world_tick FROM sw_runtime.state WHERE singleton=1)<>0
     OR (SELECT player_present FROM sw_runtime.state WHERE singleton=1)<>false THEN
    RAISE EXCEPTION 'controlled provisioning must not advance world time or mark the player present';
  END IF;
  IF (SELECT 10000-living_included FROM sw_people.population_counter WHERE singleton=1)<>500 THEN
    RAISE EXCEPTION 'opening shared population headroom is not exactly 500';
  END IF;
  IF (SELECT count(*) FROM sw_business.business WHERE created_batch_id=v_batch)<>10000
     OR (SELECT count(DISTINCT business_id) FROM sw_business.business WHERE created_batch_id=v_batch)<>10000
     OR (SELECT count(*) FROM sw_test.business_profile p JOIN sw_business.business b USING(business_id) WHERE b.created_batch_id=v_batch)<>10000 THEN
    RAISE EXCEPTION '10,000 distinct business records and test profiles do not reconcile';
  END IF;
  IF (SELECT count(DISTINCT r.normalized_key) FROM sw_names.name_reservation r
      JOIN sw_business.business b ON b.business_id=r.entity_id
      WHERE r.entity_type='BUSINESS' AND b.created_batch_id=v_batch)<>10000 THEN
    RAISE EXCEPTION 'business names are not globally unique';
  END IF;
  IF EXISTS (SELECT 1 FROM sw_business.business b
             WHERE b.created_batch_id=v_batch
               AND (b.site_assignment_status<>'unassigned' OR b.primary_spatial_id IS NOT NULL)) THEN
    RAISE EXCEPTION 'business fixture invented unsupported geography';
  END IF;
  IF (SELECT count(*) FROM sw_geo.entity)<>2 THEN
    RAISE EXCEPTION 'fixture may include only the two canonical geographic roots';
  END IF;
  IF EXISTS (SELECT 1 FROM sw_police.personnel) THEN
    RAISE EXCEPTION 'structural population fixture must not fabricate police appointments';
  END IF;

  -- A permanent-exit transition releases exactly one slot and retains identity/history.
  SELECT person_id INTO v_person FROM sw_test.person_cohort
  WHERE batch_id=v_batch ORDER BY fixture_person_key LIMIT 1;
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,source_ref)
  SELECT event_type_id,now(),0,'SW-DB-001:test-exit' FROM sw_core.event_type
  WHERE event_code='POPULATION_STATE_CHANGED' RETURNING event_id INTO v_event;
  UPDATE sw_people.population_state
  SET scope_status=2,usual_resident=false,physically_present=false,active_police_service=false,
      effective_tick=0,last_event_id=v_event
  WHERE person_id=v_person;
  IF (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>9499
     OR NOT EXISTS (SELECT 1 FROM sw_people.person WHERE person_id=v_person)
     OR (SELECT count(*) FROM sw_people.population_history WHERE person_id=v_person)<2 THEN
    RAISE EXCEPTION 'permanent exit did not release one slot while retaining identity/history';
  END IF;
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,source_ref)
  SELECT event_type_id,now(),0,'SW-DB-001:test-reentry' FROM sw_core.event_type
  WHERE event_code='POPULATION_STATE_CHANGED' RETURNING event_id INTO v_event;
  UPDATE sw_people.population_state
  SET scope_status=1,usual_resident=true,physically_present=false,active_police_service=false,
      effective_tick=0,last_event_id=v_event
  WHERE person_id=v_person;
  IF (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>9500 THEN
    RAISE EXCEPTION 're-entry did not restore exactly one population slot';
  END IF;

  -- Valid lifecycle transition records history; terminal close cannot reopen.
  SELECT business_id INTO v_business FROM sw_business.business
  WHERE created_batch_id=v_batch ORDER BY business_code LIMIT 1;
  UPDATE sw_business.business SET operating_status='suspended'
  WHERE business_id=v_business;
  UPDATE sw_business.business SET operating_status='active'
  WHERE business_id=v_business;
  IF (SELECT count(*) FROM sw_business.business_history
      WHERE business_id=v_business AND event_code='status_changed')<>2 THEN
    RAISE EXCEPTION 'business lifecycle history did not record both valid transitions';
  END IF;

  -- Duplicate identity is rejected.
  BEGIN
    INSERT INTO sw_business.business
      (business_code,created_batch_id,created_tick,source_ref)
    SELECT business_code,created_batch_id,0,'SW-DB-001:duplicate-test'
    FROM sw_business.business WHERE business_id=v_business;
    RAISE EXCEPTION 'duplicate business code unexpectedly accepted';
  EXCEPTION WHEN unique_violation THEN NULL;
  END;

  -- Unknown business reference is rejected by the naming adapter.
  BEGIN
    PERFORM sw_names.reserve_name('BUSINESS',9223372036854770000,'canonical',
      'Unregistered Test Enterprise','SW-DB-001:invalid-reference',
      'acceptance-test','must reject missing business identity',0,NULL);
    RAISE EXCEPTION 'unknown business identity unexpectedly named';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='unknown business identity unexpectedly named' THEN RAISE; END IF;
  END;

  -- Duplicate global name is rejected and its partially inserted business rolls back.
  SELECT display_name INTO v_name FROM sw_names.name_reservation
  WHERE entity_type='BUSINESS' ORDER BY reservation_id LIMIT 1;
  SELECT count(*) INTO v_before FROM sw_business.business;
  BEGIN
    INSERT INTO sw_business.business
      (business_code,created_batch_id,created_tick,source_ref)
    VALUES ('SWB-FX-ROLLBACK-01',v_batch,0,'SW-DB-001:partial-batch-test')
    RETURNING business_id INTO v_temp_business;
    PERFORM sw_names.reserve_name('BUSINESS',v_temp_business,'canonical',v_name,
      'SW-DB-001:duplicate-name','acceptance-test',
      'must reject duplicate global business name',0,NULL);
    RAISE EXCEPTION 'duplicate business name unexpectedly accepted';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='duplicate business name unexpectedly accepted' THEN RAISE; END IF;
  END;
  IF (SELECT count(*) FROM sw_business.business)<>v_before THEN
    RAISE EXCEPTION 'failed partial business batch left a domain row behind';
  END IF;

  -- Invalid lifecycle transition and invalid spatial reference both roll back.
  BEGIN
    UPDATE sw_business.business SET operating_status='closed' WHERE business_id=v_business;
    UPDATE sw_business.business SET operating_status='active' WHERE business_id=v_business;
    RAISE EXCEPTION 'closed business unexpectedly reopened';
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM='closed business unexpectedly reopened' THEN RAISE; END IF;
  END;
  IF (SELECT operating_status FROM sw_business.business WHERE business_id=v_business)<>'active' THEN
    RAISE EXCEPTION 'invalid lifecycle transition was not rolled back';
  END IF;
  BEGIN
    UPDATE sw_business.business
    SET site_assignment_status='assigned',primary_spatial_id=2147483647
    WHERE business_id=v_business;
    RAISE EXCEPTION 'invalid geography reference unexpectedly accepted';
  EXCEPTION WHEN foreign_key_violation THEN NULL;
  END;
  IF (SELECT site_assignment_status FROM sw_business.business WHERE business_id=v_business)<>'unassigned' THEN
    RAISE EXCEPTION 'invalid geography reference changed business site status';
  END IF;
END
$$;

SELECT 'SW_DB_001_ACCEPTANCE_PASS' AS result;
