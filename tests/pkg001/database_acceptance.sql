-- Runs only against the disposable PostgreSQL service in pkg001 workflow.
BEGIN;

DO $$
DECLARE
  n integer;
  ev bigint;
  pid integer;
BEGIN
  SELECT count(*) INTO n FROM sw_geo.entity;
  IF n <> 2 THEN RAISE EXCEPTION 'expected exactly two canonical geographic roots, got %', n; END IF;
  IF (SELECT count(*) FROM sw_geo.version WHERE geometry_payload IS NOT NULL) <> 0 THEN
    RAISE EXCEPTION 'unapproved geometry must remain absent';
  END IF;
  IF (SELECT count(*) FROM sw_people.person) <> 0 THEN
    RAISE EXCEPTION 'PKG-001 must not seed people';
  END IF;
  IF (SELECT count(*) FROM sw_runtime.state) <> 1 THEN
    RAISE EXCEPTION 'runtime singleton missing';
  END IF;

  UPDATE sw_runtime.state SET state=1 WHERE singleton=1;
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick)
    SELECT event_type_id,now(),0 FROM sw_core.event_type WHERE event_code='PERSON_CREATED'
    RETURNING event_id INTO ev;
  INSERT INTO sw_people.person(given_name,family_name,created_tick,last_event_id)
    VALUES ('Test','Resident',0,ev) RETURNING person_id INTO pid;
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick)
    SELECT event_type_id,now(),0 FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED'
    RETURNING event_id INTO ev;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='sw_people' AND table_name='population_state'
      AND column_name='usual_resident'
  ) THEN
    EXECUTE 'INSERT INTO sw_people.population_state(person_id,life_status,scope_status,effective_tick,last_event_id,usual_resident) VALUES ($1,1,1,0,$2,true)'
      USING pid,ev;
  ELSE
    INSERT INTO sw_people.population_state(person_id,life_status,scope_status,effective_tick,last_event_id)
      VALUES (pid,1,1,0,ev);
  END IF;
  IF (SELECT living_included FROM sw_people.population_counter WHERE singleton=1) <> 1 THEN
    RAISE EXCEPTION 'population counter failed to count included living person';
  END IF;
  IF (SELECT count(*) FROM sw_people.population_history WHERE person_id=pid) <> 1 THEN
    RAISE EXCEPTION 'population history missing';
  END IF;
  IF (SELECT count(*) FROM sw_people.profile_history WHERE person_id=pid) <> 1 THEN
    RAISE EXCEPTION 'profile history missing';
  END IF;

  -- Exercise the hard-cap rejection in a subtransaction without retaining fixtures.
  UPDATE sw_people.population_counter SET living_included=10000 WHERE singleton=1;
  BEGIN
    INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick)
      SELECT event_type_id,now(),0 FROM sw_core.event_type WHERE event_code='PERSON_CREATED'
      RETURNING event_id INTO ev;
    INSERT INTO sw_people.person(given_name,family_name,created_tick,last_event_id)
      VALUES ('Over-cap','Resident',0,ev) RETURNING person_id INTO pid;
    INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick)
      SELECT event_type_id,now(),0 FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED'
      RETURNING event_id INTO ev;
    IF EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_schema='sw_people' AND table_name='population_state'
        AND column_name='usual_resident'
    ) THEN
      EXECUTE 'INSERT INTO sw_people.population_state(person_id,life_status,scope_status,effective_tick,last_event_id,usual_resident) VALUES ($1,1,1,0,$2,true)'
        USING pid,ev;
    ELSE
      INSERT INTO sw_people.population_state(person_id,life_status,scope_status,effective_tick,last_event_id)
        VALUES (pid,1,1,0,ev);
    END IF;
    RAISE EXCEPTION '10,001st living included person was incorrectly accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM = '10,001st living included person was incorrectly accepted' THEN RAISE; END IF;
  END;
  -- Start runtime only after the one-time bootstrap is closed.
  UPDATE sw_runtime.state
    SET bootstrap_open=false, player_present=true, state=2
    WHERE singleton=1;
  UPDATE sw_runtime.state SET world_tick=1 WHERE singleton=1;
  UPDATE sw_runtime.state SET state=3, player_present=false WHERE singleton=1;
  BEGIN
    UPDATE sw_runtime.state SET world_tick=2 WHERE singleton=1;
    RAISE EXCEPTION 'world tick advanced while paused';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM = 'world tick advanced while paused' THEN RAISE; END IF;
  END;
  IF (SELECT world_tick FROM sw_runtime.state WHERE singleton=1) <> 1 THEN
    RAISE EXCEPTION 'paused runtime tick changed';
  END IF;
END
$$;

ROLLBACK;
