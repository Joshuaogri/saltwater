-- BP39-01 checkpoint and controlled abandoned-claim recovery acceptance.
-- Disposable PostgreSQL only. All state and fixtures roll back.
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

DO $bp39$
DECLARE
  tick bigint;
  v_event_id bigint;
  claimed record;
  result_status text;
  v_checkpoint_id uuid;
  report jsonb;
  unresolved_id bigint;
  unresolved_claim record;
  blocked boolean:=false;
  checkpoint_row_bytes integer;
  recovery_row_bytes integer;
BEGIN
  UPDATE sw_runtime.state SET state=1,player_present=false
    WHERE singleton=1 AND state=0;
  UPDATE sw_runtime.state SET bootstrap_open=false
    WHERE singleton=1 AND bootstrap_open=true;
  UPDATE sw_runtime.state SET state=2,player_present=true WHERE singleton=1;
  SELECT world_tick INTO tick FROM sw_runtime.state WHERE singleton=1;

  v_event_id:=sw_runtime.submit_event_work(
    'GEO_CREATED','geography','geo.create',1,1,tick,0,'bp39-recovery-fixture',
    'test:actor','geography','fixture:recovery',NULL,NULL,'internal',3
  );
  SELECT * INTO claimed FROM sw_runtime.claim_due_event_work();
  IF claimed.event_id<>v_event_id THEN RAISE EXCEPTION 'recovery fixture was not claimed'; END IF;

  PERFORM sw_runtime.begin_event_claim_recovery('test:operator','approval:BP39-01');
  IF (SELECT state FROM sw_runtime.state WHERE singleton=1)<>4
     OR (SELECT player_present FROM sw_runtime.state WHERE singleton=1) THEN
    RAISE EXCEPTION 'recovery did not freeze the runtime';
  END IF;
  result_status:=sw_runtime.reconcile_event_claim(
    v_event_id,claimed.claim_token,'effect_committed','geography',
    'owner:geography:reconciliation:fixture','domain:geography:outcome:fixture',
    'test:operator','approval:BP39-01','owner_confirmed_committed',
    'bp39-recovery-decision-1',NULL
  );
  IF result_status<>'completed' THEN RAISE EXCEPTION 'committed owner effect was not finalised'; END IF;
  IF (SELECT status FROM sw_runtime.event_work WHERE event_id=v_event_id)<>'completed'
     OR (SELECT outcome_ref FROM sw_runtime.event_work WHERE event_id=v_event_id)
       <>'domain:geography:outcome:fixture' THEN
    RAISE EXCEPTION 'recovery did not preserve the owner outcome reference';
  END IF;
  IF NOT sw_runtime.finish_event_claim_recovery() THEN
    RAISE EXCEPTION 'valid recovery did not return runtime to ready';
  END IF;
  IF (SELECT state FROM sw_runtime.state WHERE singleton=1)<>1
     OR (SELECT player_present FROM sw_runtime.state WHERE singleton=1) THEN
    RAISE EXCEPTION 'recovery completion did not leave runtime safely ready and absent';
  END IF;
  IF (SELECT count(*) FROM sw_runtime.event_work_attempt
      WHERE event_id=v_event_id AND attempt_status='completed')<>1 THEN
    RAISE EXCEPTION 'recovery completion attempt history missing';
  END IF;

  UPDATE sw_runtime.state SET state=2,player_present=true WHERE singleton=1;
  unresolved_id:=sw_runtime.submit_event_work(
    'GEO_CREATED','geography','geo.create',1,1,tick,0,'bp39-indeterminate-fixture',
    'test:actor','geography','fixture:indeterminate',NULL,NULL,'internal',3
  );
  SELECT * INTO unresolved_claim FROM sw_runtime.claim_due_event_work();
  IF unresolved_claim.event_id<>unresolved_id THEN
    RAISE EXCEPTION 'indeterminate fixture was not claimed';
  END IF;
  PERFORM sw_runtime.begin_event_claim_recovery('test:operator','approval:BP39-01');
  result_status:=sw_runtime.reconcile_event_claim(
    unresolved_id,unresolved_claim.claim_token,'indeterminate','geography',
    'owner:geography:reconciliation:indeterminate',NULL,
    'test:operator','approval:BP39-01','owner_cannot_determine',
    'bp39-indeterminate-decision',NULL
  );
  IF result_status<>'quarantined' THEN
    RAISE EXCEPTION 'indeterminate effect was not quarantined';
  END IF;
  BEGIN
    PERFORM sw_runtime.finish_event_claim_recovery();
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='unresolved or quarantined event claims block recovery completion' THEN
      blocked:=true;
    ELSE RAISE; END IF;
  END;
  IF NOT blocked THEN RAISE EXCEPTION 'quarantined work did not block recovery completion'; END IF;
  result_status:=sw_runtime.resolve_quarantined_event_claim(
    unresolved_id,unresolved_claim.claim_token,'effect_absent','geography',
    'owner:geography:reconciliation:resolved-absent',NULL,
    'test:operator','approval:BP39-01','owner_confirmed_absent',
    'bp39-indeterminate-resolution',NULL
  );
  IF result_status<>'failed' THEN
    RAISE EXCEPTION 'conclusive absence did not safely release work for retry';
  END IF;
  IF NOT sw_runtime.finish_event_claim_recovery() THEN
    RAISE EXCEPTION 'resolved recovery did not finish';
  END IF;

  v_checkpoint_id:=sw_runtime.capture_checkpoint_manifest(
    'disposable-ci','saltwater','main','saltwater_test',
    'test:operator','approval:BP39-01'
  );
  SELECT pg_column_size(m) INTO checkpoint_row_bytes
    FROM sw_runtime.checkpoint_manifest m WHERE m.checkpoint_id=v_checkpoint_id;
  SELECT pg_column_size(r) INTO recovery_row_bytes
    FROM sw_runtime.event_claim_recovery r
    WHERE r.event_id=unresolved_id ORDER BY r.recovery_id DESC LIMIT 1;
  RAISE NOTICE 'BP39_CHECKPOINT_ROW_BYTES=%',checkpoint_row_bytes;
  RAISE NOTICE 'BP39_RECOVERY_ROW_BYTES=%',recovery_row_bytes;
  report:=sw_runtime.validate_checkpoint_manifest(v_checkpoint_id);
  IF report->'gates'->'schema_watermark'->>'status'<>'pass'
     OR report->'gates'->'runtime_and_tick'->>'status'<>'pass'
     OR report->'gates'->'event_work'->>'status'<>'pass'
     OR report->'gates'->'append_only_history'->>'status'<>'pass' THEN
    RAISE EXCEPTION 'matching checkpoint failed a required measured gate: %',report;
  END IF;
  IF report->'gates'->'business_minimum'->>'status' NOT IN ('not_executed','pass')
     OR report->'gates'->'permission_hidden_truth'->>'status'<>'not_executed' THEN
    RAISE EXCEPTION 'unavailable gates were not honestly reported: %',report;
  END IF;

  UPDATE sw_runtime.state SET state=2,player_present=true WHERE singleton=1;
  UPDATE sw_runtime.state SET world_tick=world_tick+1 WHERE singleton=1;
  report:=sw_runtime.validate_checkpoint_manifest(checkpoint_id);
  IF report->'gates'->'runtime_and_tick'->>'status'<>'fail'
     OR COALESCE((report->>'valid')::boolean,true) THEN
    RAISE EXCEPTION 'mismatched restored tick was not rejected: %',report;
  END IF;
END
$bp39$;

SELECT relname,pg_relation_size(c.oid) AS heap_bytes,
       pg_indexes_size(c.oid) AS index_bytes,
       pg_total_relation_size(c.oid) AS total_bytes
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='sw_runtime'
  AND c.relname IN ('checkpoint_manifest','event_claim_recovery')
ORDER BY c.relname;

ROLLBACK;
