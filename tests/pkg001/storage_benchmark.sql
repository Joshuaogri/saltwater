-- Disposable-only representative storage fixture; leaves 1,000 synthetic people in CI DB.
-- The GitHub Actions PostgreSQL service is destroyed after the workflow.
DO $$
DECLARE
  i integer;
  ev bigint;
  pid integer;
BEGIN
  UPDATE sw_runtime.state SET state=1 WHERE singleton=1;
  FOR i IN 1..1000 LOOP
    INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick)
      SELECT event_type_id,now(),0 FROM sw_core.event_type WHERE event_code='PERSON_CREATED'
      RETURNING event_id INTO ev;
    INSERT INTO sw_people.person(given_name,family_name,created_tick,last_event_id)
      VALUES ('Synthetic','Fixture-'||substr(md5(i::text),1,12),0,ev) RETURNING person_id INTO pid;
    INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick)
      SELECT event_type_id,now(),0 FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED'
      RETURNING event_id INTO ev;
    INSERT INTO sw_people.population_state(person_id,life_status,scope_status,effective_tick,last_event_id)
      VALUES (pid,1,1,0,ev);
  END LOOP;
  UPDATE sw_runtime.state SET state=0,player_present=false WHERE singleton=1;
END
$$;

SELECT 'people='||count(*) FROM sw_people.person;
SELECT 'population_count='||living_included FROM sw_people.population_counter WHERE singleton=1;
SELECT 'database_bytes='||pg_database_size(current_database());
SELECT schemaname,relname,
       pg_total_relation_size(format('%I.%I',schemaname,relname)) AS total_bytes
FROM pg_stat_user_tables
WHERE schemaname IN ('sw_people','sw_core')
ORDER BY total_bytes DESC;
