-- Disposable-only fixture: fill the current living/included population to 9,999.
-- Follow with test_population_concurrency.py, which races two admissions at the cap.
DO $$
DECLARE
  i integer;
  ev bigint;
  pid integer;
  current_count integer;
  current_tick bigint;
BEGIN
  UPDATE sw_runtime.state
    SET state=1,player_present=false,bootstrap_open=false
    WHERE singleton=1 AND state IN (0,1) AND bootstrap_open=true AND world_tick=0;
  UPDATE sw_runtime.state SET state=2,player_present=true
    WHERE singleton=1 AND state=1 AND bootstrap_open=false;
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
  FOR i IN current_count+1..9999 LOOP
    INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,source_ref)
      SELECT event_type_id,now(),current_tick,'SW-DB-001:cap-person-created:'||i FROM sw_core.event_type WHERE event_code='PERSON_CREATED'
      RETURNING event_id INTO ev;
    INSERT INTO sw_people.person(given_name,family_name,created_tick,source_ref,last_event_id)
      VALUES ('Synthetic','Fixture-'||substr(md5(i::text),1,12),current_tick,'SW-DB-001:cap-person:'||i,ev) RETURNING person_id INTO pid;
    INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,source_ref)
      SELECT event_type_id,now(),current_tick,'SW-DB-001:cap-population-state:'||i FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED'
      RETURNING event_id INTO ev;
    INSERT INTO sw_people.population_state(person_id,life_status,scope_status,effective_tick,last_event_id)
      VALUES (pid,1,1,current_tick,ev);
  END LOOP;
  IF (SELECT living_included FROM sw_people.population_counter WHERE singleton=1) <> 9999 THEN
    RAISE EXCEPTION 'fixture did not reach 9,999 living included persons';
  END IF;
END
$$;
