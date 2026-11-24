-- Run as disposable database owner. Verifies that the application read role
-- can inspect canonical data but cannot mutate it, and the command role has
-- no direct table DML until authenticated command functions are designed.
\set ON_ERROR_STOP on

SET ROLE sw_game_readonly;
SELECT world_tick FROM sw_runtime.state WHERE singleton=1;
SELECT count(*) FROM sw_geo.entity;
SELECT count(*) FROM sw_people.person;
SELECT count(*) FROM sw_names.registry;
SELECT count(*) FROM sw_names.generation_batch;
DO $$
BEGIN
  IF has_table_privilege(current_user,'sw_people.person','INSERT') THEN
    RAISE EXCEPTION 'readonly role unexpectedly has person INSERT';
  END IF;
  IF has_table_privilege(current_user,'sw_people.person','UPDATE') THEN
    RAISE EXCEPTION 'readonly role unexpectedly has person UPDATE';
  END IF;
  IF has_table_privilege(current_user,'sw_people.person','DELETE') THEN
    RAISE EXCEPTION 'readonly role unexpectedly has person DELETE';
  END IF;
  IF has_table_privilege(current_user,'sw_runtime.state','UPDATE') THEN
    RAISE EXCEPTION 'readonly role unexpectedly has runtime UPDATE';
  END IF;
  IF NOT has_table_privilege(current_user,'sw_names.registry','SELECT') THEN
    RAISE EXCEPTION 'readonly role cannot read the naming registry view';
  END IF;
END
$$;
DO $$
BEGIN
  BEGIN
    UPDATE sw_runtime.state SET world_tick=world_tick+1 WHERE singleton=1;
    RAISE EXCEPTION 'readonly UPDATE unexpectedly succeeded';
  EXCEPTION WHEN insufficient_privilege THEN
    NULL;
  END;
END
$$;
RESET ROLE;

SET ROLE sw_game_command;
DO $$
BEGIN
  IF has_table_privilege(current_user,'sw_people.person','INSERT')
     OR has_table_privilege(current_user,'sw_people.person','UPDATE')
     OR has_table_privilege(current_user,'sw_people.person','DELETE')
     OR has_table_privilege(current_user,'sw_runtime.state','UPDATE')
     OR has_table_privilege(current_user,'sw_core.simulation_event','INSERT')
     OR has_table_privilege(current_user,'sw_names.name_reservation','INSERT')
     OR has_table_privilege(current_user,'sw_names.name_event','INSERT')
     OR has_table_privilege(current_user,'sw_names.generation_batch','INSERT') THEN
    RAISE EXCEPTION 'command role unexpectedly has direct table mutation privileges';
  END IF;
  IF NOT has_function_privilege(current_user,
       'sw_names.reserve_name(text,bigint,text,text,text,text,text,bigint,bigint)','EXECUTE')
     OR NOT has_function_privilege(current_user,
       'sw_names.record_generation_batch(text,smallint,smallint,text,bigint,bytea,integer,text,text,text)','EXECUTE') THEN
    RAISE EXCEPTION 'command role lacks controlled naming functions';
  END IF;
END
$;
RESET ROLE;

-- Owner-level append-only guards must also reject direct history mutation.
DO $$
BEGIN
  BEGIN
    UPDATE sw_people.population_history SET effective_tick=effective_tick
      WHERE event_id=(SELECT min(event_id) FROM sw_people.population_history);
    RAISE EXCEPTION 'population history UPDATE unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM = 'population history UPDATE unexpectedly succeeded' THEN RAISE; END IF;
  END;
END
$$;
