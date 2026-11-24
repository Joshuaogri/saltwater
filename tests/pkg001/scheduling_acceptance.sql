-- BP37-01 acceptance: disposable PostgreSQL only; transaction rolls back.
BEGIN;

DO $$
DECLARE
  first_id bigint;
  repeated_id bigint;
  second_id bigint;
  claimed record;
  completed boolean;
  denied boolean := false;
  current_tick bigint;
BEGIN
  UPDATE sw_runtime.state
    SET state=1, player_present=false
    WHERE singleton=1 AND state=0;
  UPDATE sw_runtime.state SET bootstrap_open=false WHERE singleton=1 AND bootstrap_open=true;
  UPDATE sw_runtime.state SET state=2, player_present=true WHERE singleton=1;

  SELECT world_tick INTO current_tick FROM sw_runtime.state WHERE singleton=1;
  first_id := sw_runtime.create_schedule(
    'police', 'shift:alpha', current_tick, NULL, 10, NULL, 'bp37-first'
  );
  repeated_id := sw_runtime.create_schedule(
    'police', 'shift:alpha', current_tick, NULL, 10, NULL, 'bp37-first'
  );
  IF first_id <> repeated_id THEN
    RAISE EXCEPTION 'schedule idempotent registration returned a new identity';
  END IF;

  second_id := sw_runtime.create_schedule(
    'world', 'world:second', current_tick, 2, 10, current_tick+10, 'bp37-second'
  );
  IF first_id >= second_id THEN RAISE EXCEPTION 'schedule identities are not stable'; END IF;

  SELECT * INTO claimed FROM sw_runtime.claim_due_schedule();
  IF claimed.schedule_id <> first_id THEN
    RAISE EXCEPTION 'due schedule ordering did not select earliest stable identity';
  END IF;
  SELECT sw_runtime.finish_schedule(
    claimed.schedule_id, claimed.claim_token, true, NULL, NULL
  ) INTO completed;
  IF NOT completed THEN RAISE EXCEPTION 'valid schedule claim did not complete'; END IF;

  SELECT * INTO claimed FROM sw_runtime.claim_due_schedule();
  IF claimed.schedule_id <> second_id THEN
    RAISE EXCEPTION 'next due schedule was not selected';
  END IF;
  SELECT sw_runtime.finish_schedule(
    claimed.schedule_id, claimed.claim_token, false, current_tick+1, 'temporary_failure'
  ) INTO completed;
  IF NOT completed THEN RAISE EXCEPTION 'valid failed dispatch was not recorded'; END IF;
  IF (SELECT status FROM sw_runtime.schedule WHERE schedule_id=second_id) <> 'failed' THEN
    RAISE EXCEPTION 'failed handler state was not retained';
  END IF;

  -- Representative 1,000-row schedule fixture for storage measurement.
  INSERT INTO sw_runtime.schedule(
    owner_domain, subject_ref, due_tick, interval_ticks, priority,
    expires_at_tick, retry_after_tick, status, attempt_count,
    idempotency_key, created_tick, last_event_id
  )
  SELECT 'benchmark', 'fixture:' || g::text, current_tick + 100,
    NULL, 0, NULL, 0, 'pending', 0,
    'bp37-storage-' || g::text, current_tick,
    (SELECT last_event_id FROM sw_runtime.schedule WHERE schedule_id=second_id)
  FROM generate_series(1,1000) AS g;

  UPDATE sw_runtime.state SET state=3, player_present=false WHERE singleton=1;
  SELECT * INTO claimed FROM sw_runtime.claim_due_schedule();
  IF claimed.schedule_id IS NOT NULL THEN
    RAISE EXCEPTION 'paused runtime claimed scheduled work';
  END IF;
  BEGIN
    PERFORM sw_runtime.finish_schedule(second_id, gen_random_uuid(), true, NULL, NULL);
    RAISE EXCEPTION 'paused runtime dispatched scheduled work';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='paused runtime dispatched scheduled work' THEN RAISE; END IF;
    denied := true;
  END;
  IF NOT denied THEN RAISE EXCEPTION 'paused dispatch was not rejected'; END IF;
END $;

SELECT pg_relation_size('sw_runtime.schedule') AS schedule_heap_bytes,
       pg_indexes_size('sw_runtime.schedule') AS schedule_index_bytes,
       pg_total_relation_size('sw_runtime.schedule') AS schedule_total_bytes,
       (pg_total_relation_size('sw_runtime.schedule')::numeric / 1001) AS approx_bytes_per_schedule_including_indexes;

ROLLBACK;
