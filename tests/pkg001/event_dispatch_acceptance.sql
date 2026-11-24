-- BP35-01 event intake/dispatch acceptance. Disposable PostgreSQL only.
-- All fixture rows and runtime changes are rolled back.
BEGIN;

DO $bp35$
DECLARE
  tick bigint;
  parent_id bigint;
  child_id bigint;
  retry_id bigint;
  duplicate_id bigint;
  claimed record;
  result_status text;
  cycle_denied boolean := false;
  stale_denied boolean := false;
  pause_denied boolean := false;
  active_pause_blocked boolean := false;
BEGIN
  UPDATE sw_runtime.state SET state=1,player_present=false
    WHERE singleton=1 AND state=0;
  UPDATE sw_runtime.state SET bootstrap_open=false
    WHERE singleton=1 AND bootstrap_open=true;
  UPDATE sw_runtime.state SET state=2,player_present=true WHERE singleton=1;
  SELECT world_tick INTO tick FROM sw_runtime.state WHERE singleton=1;

  parent_id:=sw_runtime.submit_event_work(
    'GEO_CREATED','geography','geo.create',1,1,tick,0,'bp35-parent',
    'test:actor','geography','fixture:parent',NULL,NULL,'internal',3
  );
  duplicate_id:=sw_runtime.submit_event_work(
    'GEO_CREATED','geography','geo.create',1,1,tick,0,'bp35-parent',
    'test:actor','geography','fixture:parent',NULL,NULL,'internal',3
  );
  IF parent_id<>duplicate_id THEN RAISE EXCEPTION 'event submission idempotency failed'; END IF;

  child_id:=sw_runtime.submit_event_work(
    'GEO_VERSIONED','geography','geo.create',1,1,tick,100,'bp35-child',
    'test:actor','geography','fixture:child',parent_id,NULL,'internal',3
  );
  PERFORM sw_runtime.add_event_prerequisite(child_id,parent_id);
  PERFORM sw_runtime.add_event_prerequisite(child_id,parent_id);

  BEGIN
    PERFORM sw_runtime.add_event_prerequisite(parent_id,child_id);
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='causal prerequisite would create a cycle' THEN cycle_denied:=true;
    ELSE RAISE; END IF;
  END;
  IF NOT cycle_denied THEN RAISE EXCEPTION 'causal cycle was not rejected'; END IF;

  SELECT * INTO claimed FROM sw_runtime.claim_due_event_work();
  IF claimed.event_id<>parent_id THEN
    RAISE EXCEPTION 'causal child ran before parent or deterministic ordering failed';
  END IF;
  BEGIN
    PERFORM sw_runtime.finish_event_work(
      parent_id,gen_random_uuid(),true,'fixture:wrong-token',NULL,NULL,true
    );
    RAISE EXCEPTION 'stale claim token unexpectedly finalized event work';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='event claim token is stale or invalid' THEN stale_denied:=true;
    ELSIF SQLERRM='stale claim token unexpectedly finalized event work' THEN RAISE;
    ELSE RAISE; END IF;
  END;
  IF NOT stale_denied THEN RAISE EXCEPTION 'stale claim token was not rejected'; END IF;

  BEGIN
    UPDATE sw_runtime.state SET state=3,player_present=false WHERE singleton=1;
    RAISE EXCEPTION 'pause unexpectedly committed during active event dispatch';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='pause waits for active event dispatch to finish' THEN active_pause_blocked:=true;
    ELSIF SQLERRM='pause unexpectedly committed during active event dispatch' THEN RAISE;
    ELSE RAISE; END IF;
  END;
  IF NOT active_pause_blocked THEN RAISE EXCEPTION 'active dispatch did not block pause'; END IF;

  SELECT sw_runtime.finish_event_work(
    parent_id,claimed.claim_token,true,'fixture:parent-committed',NULL,NULL,true
  ) INTO result_status;
  IF result_status<>'completed' THEN RAISE EXCEPTION 'parent did not complete'; END IF;

  SELECT * INTO claimed FROM sw_runtime.claim_due_event_work();
  IF claimed.event_id<>child_id THEN RAISE EXCEPTION 'child did not become eligible after parent commit'; END IF;
  SELECT sw_runtime.finish_event_work(
    child_id,claimed.claim_token,true,'fixture:child-committed',NULL,NULL,true
  ) INTO result_status;
  IF result_status<>'completed' THEN RAISE EXCEPTION 'child did not complete'; END IF;

  retry_id:=sw_runtime.submit_event_work(
    'GEO_CREATED','geography','geo.create',1,1,tick,0,'bp35-retry',
    NULL,'geography','fixture:retry',NULL,NULL,'internal',2
  );
  SELECT * INTO claimed FROM sw_runtime.claim_due_event_work();
  IF claimed.event_id<>retry_id THEN RAISE EXCEPTION 'retry fixture was not claimed'; END IF;
  SELECT sw_runtime.finish_event_work(
    retry_id,claimed.claim_token,false,NULL,'temporary_failure',tick,true
  ) INTO result_status;
  IF result_status<>'failed' THEN RAISE EXCEPTION 'transient failure was not retryable'; END IF;

  SELECT * INTO claimed FROM sw_runtime.claim_due_event_work();
  IF claimed.event_id<>retry_id OR claimed.attempt_count<>2 THEN
    RAISE EXCEPTION 'retry did not retain event identity and increment attempt count';
  END IF;
  SELECT sw_runtime.finish_event_work(
    retry_id,claimed.claim_token,false,NULL,'temporary_failure',tick,true
  ) INTO result_status;
  IF result_status<>'quarantined' THEN RAISE EXCEPTION 'attempt limit did not quarantine poison event'; END IF;

  UPDATE sw_runtime.state SET state=3,player_present=false WHERE singleton=1;
  SELECT * INTO claimed FROM sw_runtime.claim_due_event_work();
  IF claimed.event_id IS NOT NULL THEN RAISE EXCEPTION 'paused runtime claimed event work'; END IF;
  BEGIN
    PERFORM sw_runtime.submit_event_work(
      'GEO_CREATED','geography','geo.create',1,1,tick,0,'bp35-paused',
      NULL,'geography','fixture:paused',NULL,NULL,'internal',2
    );
    RAISE EXCEPTION 'paused event intake was not rejected';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='event intake requires running player-present runtime' THEN pause_denied:=true;
    ELSIF SQLERRM='paused event intake was not rejected' THEN RAISE;
    ELSE RAISE; END IF;
  END;
  IF NOT pause_denied THEN RAISE EXCEPTION 'paused event intake was not rejected'; END IF;
END
$bp35$;

SELECT c.relname,
       pg_relation_size(c.oid) AS heap_bytes,
       pg_indexes_size(c.oid) AS index_bytes,
       pg_total_relation_size(c.oid) AS total_bytes
FROM pg_class c
JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='sw_runtime'
  AND c.relname IN ('event_work','event_work_attempt','event_work_prerequisite')
ORDER BY c.relname;
SELECT (SELECT count(*) FROM sw_runtime.event_work) AS fixture_work_rows,
       (SELECT count(*) FROM sw_runtime.event_work_attempt) AS fixture_attempt_rows,
       (SELECT count(*) FROM sw_runtime.event_work_prerequisite) AS fixture_dependency_rows;

ROLLBACK;
