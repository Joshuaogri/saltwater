-- Disposable-only fixture: fill the current living/included population to 9,999.
-- Keep canonical event, person-name registry, population-cap, and append-only
-- history triggers enabled. Batch fixture DML to avoid per-person round trips.
DO $$
DECLARE
  current_count integer;
  current_tick bigint;
  phase_started timestamptz;
BEGIN
  UPDATE sw_runtime.state
    SET state=1,player_present=false,bootstrap_open=false
    WHERE singleton=1 AND state IN (0,1) AND bootstrap_open=true AND world_tick=0;
  -- Re-enter ready/running after prior adapter tests without reopening bootstrap.
  UPDATE sw_runtime.state SET state=1,player_present=false
    WHERE singleton=1 AND state=0 AND bootstrap_open=false;
  UPDATE sw_runtime.state SET state=2,player_present=true
    WHERE singleton=1 AND state=1 AND bootstrap_open=false;
  -- Resume only the explicit paused state; never bypass recovery/stopped states.
  UPDATE sw_runtime.state SET state=2,player_present=true
    WHERE singleton=1 AND state=3 AND bootstrap_open=false;

  SELECT living_included INTO current_count
    FROM sw_people.population_counter WHERE singleton=1;
  SELECT world_tick INTO current_tick
    FROM sw_runtime.state
    WHERE singleton=1 AND state=2 AND player_present=true;
  IF current_tick IS NULL THEN
    RAISE EXCEPTION 'population fixture requires active player-present runtime';
  END IF;
  IF current_count > 9999 THEN
    RAISE EXCEPTION 'fixture population already exceeds 9,999';
  END IF;

  CREATE TEMP TABLE cap_fixture_stage (
    fixture_no integer PRIMARY KEY,
    created_event_id bigint,
    person_id integer,
    population_event_id bigint
  ) ON COMMIT DROP;

  phase_started := clock_timestamp();
  WITH inserted AS (
    INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,source_ref)
    SELECT et.event_type_id,now(),current_tick,
           'SW-DB-001:cap-person-created:'||g.fixture_no
    FROM generate_series(current_count+1,9999) AS g(fixture_no)
    CROSS JOIN sw_core.event_type et
    WHERE et.event_code='PERSON_CREATED'
    RETURNING event_id,source_ref
  )
  INSERT INTO cap_fixture_stage(fixture_no,created_event_id)
  SELECT substring(source_ref from '([0-9]+)$')::integer,event_id
  FROM inserted;

  RAISE NOTICE 'CAP_FIXTURE_PHASE=person_created_events ELAPSED_MS=%',round((extract(epoch FROM clock_timestamp()-phase_started)*1000)::numeric,2);

  -- The canonical person-name AFTER trigger remains enabled for every row.
  phase_started := clock_timestamp();
  -- High-entropy family tokens avoid a shared-prefix synthetic naming workload.
  WITH inserted AS (
    INSERT INTO sw_people.person
      (given_name,family_name,created_tick,source_ref,last_event_id)
    SELECT 'Person',upper(substr(md5('saltwater-cap-person:'||fixture_no),1,24)),
           current_tick,'SW-DB-001:cap-person:'||fixture_no,created_event_id
    FROM cap_fixture_stage
    ORDER BY fixture_no
    RETURNING person_id,source_ref
  )
  UPDATE cap_fixture_stage s
    SET person_id=i.person_id
  FROM inserted i
  WHERE i.source_ref='SW-DB-001:cap-person:'||s.fixture_no;

  RAISE NOTICE 'CAP_FIXTURE_PHASE=people_and_name_registry ELAPSED_MS=%',round((extract(epoch FROM clock_timestamp()-phase_started)*1000)::numeric,2);
  phase_started := clock_timestamp();

  WITH inserted AS (
    INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,source_ref)
    SELECT et.event_type_id,now(),current_tick,
           'SW-DB-001:cap-population-state:'||s.fixture_no
    FROM cap_fixture_stage s
    CROSS JOIN sw_core.event_type et
    WHERE et.event_code='POPULATION_STATE_CHANGED'
    RETURNING event_id,source_ref
  )
  UPDATE cap_fixture_stage s
    SET population_event_id=i.event_id
  FROM inserted i
  WHERE i.source_ref='SW-DB-001:cap-population-state:'||s.fixture_no;

  RAISE NOTICE 'CAP_FIXTURE_PHASE=population_state_events ELAPSED_MS=%',round((extract(epoch FROM clock_timestamp()-phase_started)*1000)::numeric,2);

  -- Population-cap and immutable history triggers remain authoritative.
  phase_started := clock_timestamp();
  INSERT INTO sw_people.population_state
    (person_id,life_status,scope_status,effective_tick,last_event_id,usual_resident)
  SELECT person_id,1,1,current_tick,population_event_id,true
  FROM cap_fixture_stage
  ORDER BY fixture_no;

  RAISE NOTICE 'CAP_FIXTURE_PHASE=population_state_and_history ELAPSED_MS=%',round((extract(epoch FROM clock_timestamp()-phase_started)*1000)::numeric,2);
  phase_started := clock_timestamp();

  IF (SELECT count(*) FROM cap_fixture_stage) <> 9999-current_count
     OR EXISTS (SELECT 1 FROM cap_fixture_stage
                WHERE created_event_id IS NULL OR person_id IS NULL
                   OR population_event_id IS NULL) THEN
    RAISE EXCEPTION 'population fixture staging is incomplete';
  END IF;
  IF (SELECT living_included FROM sw_people.population_counter WHERE singleton=1) <> 9999 THEN
    RAISE EXCEPTION 'fixture did not reach 9,999 living included persons';
  END IF;
  RAISE NOTICE 'CAP_FIXTURE_PHASE=final_reconciliation ELAPSED_MS=%',round((extract(epoch FROM clock_timestamp()-phase_started)*1000)::numeric,2);
END
$;
