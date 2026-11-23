-- Assertions executed after restoring the disposable custom-format backup.
\set ON_ERROR_STOP on
DO $$
DECLARE
  n_people bigint;
  n_population bigint;
  n_events bigint;
  max_event bigint;
  population_count integer;
  tick bigint;
  roots bigint;
BEGIN
  SELECT count(*) INTO n_people FROM sw_people.person;
  SELECT count(*) INTO n_population FROM sw_people.population_state;
  SELECT count(*), max(event_id) INTO n_events, max_event FROM sw_core.simulation_event;
  SELECT living_included INTO population_count FROM sw_people.population_counter WHERE singleton=1;
  SELECT world_tick INTO tick FROM sw_runtime.state WHERE singleton=1;
  SELECT count(*) INTO roots FROM sw_geo.entity WHERE kind IN (1,2);
  IF n_people <> 10000 OR n_population <> 10000 OR population_count <> 10000 THEN
    RAISE EXCEPTION 'restored population mismatch: people %, states %, counter %', n_people,n_population,population_count;
  END IF;
  IF n_events < 20000 OR max_event IS NULL THEN
    RAISE EXCEPTION 'restored event history is incomplete: events %, max %',n_events,max_event;
  END IF;
  IF tick <> 1 THEN
    RAISE EXCEPTION 'restored runtime tick mismatch: %',tick;
  END IF;
  IF roots <> 2 THEN
    RAISE EXCEPTION 'restored canonical geography roots mismatch: %',roots;
  END IF;
  IF (SELECT count(*) FROM sw_people.population_history) <> 10000 THEN
    RAISE EXCEPTION 'restored population history row count mismatch';
  END IF;
  IF (SELECT count(*) FROM sw_people.profile_history) <> 10000 THEN
    RAISE EXCEPTION 'restored profile history row count mismatch';
  END IF;
  RAISE NOTICE 'RESTORE_PASS people=% states=% population=% events=% max_event=% tick=% roots=%',
    n_people,n_population,population_count,n_events,max_event,tick,roots;
END
$$;
