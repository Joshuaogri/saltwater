-- Disposable-only fixture: move from 1,000 to 9,999 living/included people.
-- Follow with test_population_concurrency.py, which races two admissions at the cap.
DO $$
DECLARE
  i integer;
  ev bigint;
  pid integer;
BEGIN
  UPDATE sw_runtime.state SET state=1 WHERE singleton=1;
  FOR i IN 1001..9999 LOOP
    INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick)
      SELECT event_type_id,now(),0 FROM sw_core.event_type WHERE event_code='PERSON_CREATED'
      RETURNING event_id INTO ev;
    INSERT INTO sw_people.person(given_name,family_name,created_tick,last_event_id)
      VALUES ('Synthetic','Person-'||i,0,ev) RETURNING person_id INTO pid;
    INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick)
      SELECT event_type_id,now(),0 FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED'
      RETURNING event_id INTO ev;
    INSERT INTO sw_people.population_state(person_id,life_status,scope_status,effective_tick,last_event_id)
      VALUES (pid,1,1,0,ev);
  END LOOP;
  IF (SELECT living_included FROM sw_people.population_counter WHERE singleton=1) <> 9999 THEN
    RAISE EXCEPTION 'fixture did not reach 9,999 living included persons';
  END IF;
END
$$;
