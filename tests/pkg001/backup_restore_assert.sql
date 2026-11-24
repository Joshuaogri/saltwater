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
  name_count bigint;
  name_event_count bigint;
  generation_batch_count bigint;
BEGIN
  SELECT count(*) INTO n_people FROM sw_people.person;
  SELECT count(*) INTO n_population FROM sw_people.population_state;
  SELECT count(*), max(event_id) INTO n_events, max_event FROM sw_core.simulation_event;
  SELECT living_included INTO population_count FROM sw_people.population_counter WHERE singleton=1;
  SELECT world_tick INTO tick FROM sw_runtime.state WHERE singleton=1;
  SELECT count(*) INTO roots FROM sw_geo.entity WHERE kind IN (1,2);
  SELECT count(*) INTO name_count FROM sw_names.name_reservation;
  SELECT count(*) INTO name_event_count FROM sw_names.name_event;
  SELECT count(*) INTO generation_batch_count FROM sw_names.generation_batch;
  IF n_people <> 10000 OR n_population <> 10000 OR population_count <> 10000 THEN
    RAISE EXCEPTION 'restored population mismatch: people %, states %, counter %', n_people,n_population,population_count;
  END IF;
  IF n_events < 20000 OR max_event IS NULL THEN
    RAISE EXCEPTION 'restored event history is incomplete: events %, max %',n_events,max_event;
  END IF;
  IF tick <> 2 THEN
    RAISE EXCEPTION 'restored runtime tick mismatch: %',tick;
  END IF;
  IF roots <> 2 THEN
    RAISE EXCEPTION 'restored canonical geography roots mismatch: %',roots;
  END IF;
  IF name_count < 10009 OR name_event_count < 20019 OR generation_batch_count < 1 THEN
    RAISE EXCEPTION 'restored naming registry/history/manifests incomplete: reservations %, events %, batches %',name_count,name_event_count,generation_batch_count;
  END IF;
  IF (SELECT count(*) FROM sw_names.registry WHERE normalized_key='saltwater' AND status='active') <> 2 THEN
    RAISE EXCEPTION 'restored Saltwater root-name exception is missing or ambiguous';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM sw_names.registry old_name
    JOIN sw_names.registry new_name
      ON new_name.entity_type=old_name.entity_type
     AND new_name.entity_id=old_name.entity_id
    WHERE old_name.entity_type='GEOGRAPHY'
      AND old_name.display_name='Historic Registry Road'
      AND old_name.status='superseded'
      AND new_name.display_name='Current Registry Road'
      AND new_name.status='active'
  ) THEN
    RAISE EXCEPTION 'restored geographic name history did not preserve rename identity';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM sw_names.name_reservation r
    JOIN sw_names.generation_batch b ON b.batch_id=r.generation_batch_id
  ) THEN
    RAISE EXCEPTION 'restored generator manifest is not linked to a reserved name';
  END IF;
  IF (SELECT count(*) FROM sw_people.population_history) <> 10000 THEN
    RAISE EXCEPTION 'restored population history row count mismatch';
  END IF;
  IF (SELECT count(*) FROM sw_people.profile_history) <> 10000 THEN
    RAISE EXCEPTION 'restored profile history row count mismatch';
  END IF;
  RAISE NOTICE 'RESTORE_PASS people=% states=% population=% events=% max_event=% tick=% roots=% names=% name_events=% generator_batches=%',
    n_people,n_population,population_count,n_events,max_event,tick,roots,name_count,name_event_count,generation_batch_count;
END
$$;
