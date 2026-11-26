-- BP11 dispatch lifecycle writer over the canonical BP08 deployment ledger.
-- Apply only through the approved migration process; this proposal is not
-- applied to production Neon by repository CI.
BEGIN;

CREATE OR REPLACE FUNCTION sw_police.transition_unit_deployment(
  p_deployment_id uuid,
  p_expected_status text,
  p_resulting_status text,
  p_event_kind text,
  p_actor_ref text,
  p_reason text,
  p_source_ref text,
  p_idempotency_key text,
  p_effective_tick bigint
) RETURNS TABLE(deployment_id uuid, status text, event_id bigint)
LANGUAGE plpgsql AS $bp11$
DECLARE
  deployment_row sw_police.unit_deployment%ROWTYPE;
  prior_event_id bigint;
  new_event_id bigint;
  event_code text;
  current_tick bigint;
BEGIN
  IF p_deployment_id IS NULL
     OR p_expected_status IS NULL OR p_resulting_status IS NULL
     OR p_event_kind NOT IN ('issued','acknowledged','mobilising','started',
          'reassigned','stood_down','completed','cancelled','rejected')
     OR p_actor_ref IS NULL OR length(p_actor_ref) NOT BETWEEN 1 AND 200
     OR p_reason IS NULL OR length(trim(p_reason))=0 OR length(p_reason)>500
     OR p_source_ref IS NULL OR length(p_source_ref) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_effective_tick IS NULL OR p_effective_tick<0 THEN
    RAISE EXCEPTION 'invalid dispatch transition request';
  END IF;

  SELECT * INTO deployment_row
  FROM sw_police.unit_deployment
  WHERE unit_deployment.deployment_id=p_deployment_id
  FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'deployment not found'; END IF;

  -- Safe replay: only return an earlier event when it belongs to this exact
  -- deployment and records the same resulting state.
  SELECT e.source_event_id INTO prior_event_id
  FROM sw_police.unit_deployment_event e
  JOIN sw_runtime.event_work w ON w.event_id=e.source_event_id
  WHERE w.idempotency_key=p_idempotency_key
    AND e.deployment_id=p_deployment_id
    AND e.resulting_status=p_resulting_status
    AND e.event_kind=p_event_kind
    AND e.reason=p_reason
    AND e.source_ref=p_source_ref
    AND e.actor_ref=p_actor_ref;
  IF prior_event_id IS NOT NULL THEN
    RETURN QUERY SELECT p_deployment_id,p_resulting_status,prior_event_id;
    RETURN;
  END IF;

  IF deployment_row.status<>p_expected_status THEN
    RAISE EXCEPTION 'deployment status conflict: expected %, found %',
      p_expected_status,deployment_row.status;
  END IF;
  IF NOT (
    (p_expected_status='authorised' AND p_resulting_status='issued' AND p_event_kind='issued')
    OR (p_expected_status='issued' AND p_resulting_status='acknowledged' AND p_event_kind='acknowledged')
    OR (p_expected_status='issued' AND p_resulting_status='rejected' AND p_event_kind='rejected')
    OR (p_expected_status='acknowledged' AND p_resulting_status='mobilising' AND p_event_kind='mobilising')
    OR (p_expected_status='acknowledged' AND p_resulting_status='rejected' AND p_event_kind='rejected')
    OR (p_expected_status IN ('issued','acknowledged','mobilising','active')
        AND p_resulting_status='cancelled' AND p_event_kind='cancelled')
    OR (p_expected_status IN ('issued','acknowledged','mobilising','active')
        AND p_resulting_status='reassigned' AND p_event_kind='reassigned')
    OR (p_expected_status='mobilising' AND p_resulting_status='active' AND p_event_kind='started')
    OR (p_expected_status='active' AND p_resulting_status='completed' AND p_event_kind='completed')
    OR (p_expected_status='active' AND p_resulting_status='stood_down' AND p_event_kind='stood_down')
  ) THEN RAISE EXCEPTION 'invalid dispatch status transition'; END IF;

  SELECT world_tick INTO current_tick
  FROM sw_runtime.state WHERE singleton=1;
  IF current_tick IS NULL OR p_effective_tick<current_tick THEN
    RAISE EXCEPTION 'dispatch effective tick is behind the world clock';
  END IF;

  event_code := CASE p_event_kind
    WHEN 'issued' THEN 'UNIT_DEPLOYMENT_ISSUED'
    WHEN 'acknowledged' THEN 'UNIT_DEPLOYMENT_ACKNOWLEDGED'
    WHEN 'rejected' THEN 'UNIT_DEPLOYMENT_CHANGED'
    WHEN 'mobilising' THEN 'UNIT_DEPLOYMENT_CHANGED'
    WHEN 'started' THEN 'UNIT_DEPLOYMENT_STARTED'
    WHEN 'reassigned' THEN 'UNIT_DEPLOYMENT_CHANGED'
    WHEN 'stood_down' THEN 'UNIT_DEPLOYMENT_CHANGED'
    WHEN 'completed' THEN 'UNIT_DEPLOYMENT_COMPLETED'
    WHEN 'cancelled' THEN 'UNIT_DEPLOYMENT_CANCELLED'
  END;

  new_event_id := sw_runtime.submit_event_work(
    event_code, 'police', 'bp08:deployment:transition', 1, 1,
    p_effective_tick, 0, p_idempotency_key, p_actor_ref, 'bp08',
    p_source_ref, NULL, p_deployment_id, 'police_operational', 5
  );

  UPDATE sw_police.unit_deployment
  SET status=p_resulting_status,
      actual_end_tick=CASE WHEN p_resulting_status IN ('completed','cancelled','stood_down','rejected')
                           THEN p_effective_tick ELSE actual_end_tick END
  WHERE unit_deployment.deployment_id=p_deployment_id;

  INSERT INTO sw_police.unit_deployment_event(
    deployment_id,source_event_id,event_kind,prior_status,resulting_status,
    effective_tick,actor_ref,authority_ref,reason,source_ref
  ) VALUES (
    p_deployment_id,new_event_id,p_event_kind,p_expected_status,p_resulting_status,
    p_effective_tick,p_actor_ref,deployment_row.authority_ref,p_reason,p_source_ref
  );

  RETURN QUERY SELECT p_deployment_id,p_resulting_status,new_event_id;
END
$bp11$;

COMMIT;
