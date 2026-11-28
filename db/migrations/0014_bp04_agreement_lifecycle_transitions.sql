-- BP04-12 controlled agreement lifecycle transitions.
-- The existing occupancy agreement and occupancy projections remain authoritative.
-- Expiry/termination/surrender never silently vacate premises or change population.
BEGIN;

CREATE FUNCTION sw_property.transition_occupancy_agreement(
  p_agreement_id text,
  p_event_type text,
  p_expected_status text,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text,
  p_evidence_class text,
  p_successor_agreement_id text,
  p_event_payload jsonb
) RETURNS TABLE(agreement_id text, agreement_status text, agreement_event_id uuid)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_agreement sw_property.occupancy_agreement%ROWTYPE;
  v_successor sw_property.occupancy_agreement%ROWTYPE;
  v_prior sw_property.occupancy_agreement_event%ROWTYPE;
  v_resulting_status text;
  v_payload jsonb;
  v_event_id uuid;
BEGIN
  IF p_agreement_id IS NULL OR p_event_type NOT IN (
       'agreement_executed','agreement_varied','agreement_renewed',
       'agreement_expired','agreement_terminated','agreement_surrendered'
     )
     OR p_expected_status IS NULL OR length(trim(p_expected_status))=0
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_evidence_class NOT IN ('source_documented','generated_fictional_canon','gameplay_action')
     OR p_event_payload IS NULL OR jsonb_typeof(p_event_payload)<>'object' THEN
    RAISE EXCEPTION 'invalid occupancy agreement transition request';
  END IF;

  v_resulting_status := CASE
    WHEN p_event_type='agreement_executed' AND p_expected_status IN ('draft','proposed') THEN 'active'
    WHEN p_event_type='agreement_varied' AND p_expected_status IN ('active','seasonal','temporarily_inactive') THEN p_expected_status
    WHEN p_event_type='agreement_renewed' AND p_expected_status IN ('active','seasonal','temporarily_inactive') THEN 'renewed'
    WHEN p_event_type='agreement_expired' AND p_expected_status IN ('active','seasonal','temporarily_inactive') THEN 'expired'
    WHEN p_event_type='agreement_terminated' AND p_expected_status IN ('active','seasonal','temporarily_inactive') THEN 'terminated'
    WHEN p_event_type='agreement_surrendered' AND p_expected_status IN ('active','seasonal','temporarily_inactive') THEN 'surrendered'
    ELSE NULL
  END;
  IF v_resulting_status IS NULL THEN
    RAISE EXCEPTION 'invalid agreement lifecycle state transition';
  END IF;
  IF (p_event_type='agreement_renewed')<>(p_successor_agreement_id IS NOT NULL) THEN
    RAISE EXCEPTION 'renewal requires exactly one successor agreement';
  END IF;

  v_payload := p_event_payload ||
    jsonb_build_object('prior_status',p_expected_status,'resulting_status',v_resulting_status);

  SELECT * INTO v_agreement
  FROM sw_property.occupancy_agreement
  WHERE occupancy_agreement.agreement_id=p_agreement_id
  FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'occupancy agreement not found'; END IF;

  -- Idempotent replay is resolved before checking current status: later valid
  -- transitions must not make an exact earlier retry fail.
  SELECT * INTO v_prior
  FROM sw_property.occupancy_agreement_event
  WHERE occupancy_agreement_event.agreement_id=p_agreement_id
    AND occupancy_agreement_event.idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.event_type<>p_event_type
       OR v_prior.effective_tick<>p_effective_tick
       OR v_prior.recorded_tick<>p_recorded_tick
       OR v_prior.actor_ref<>p_actor_ref
       OR v_prior.source_ref<>p_source_ref
       OR v_prior.evidence_class<>p_evidence_class
       OR v_prior.successor_agreement_id IS DISTINCT FROM p_successor_agreement_id
       OR v_prior.event_payload<>v_payload THEN
      RAISE EXCEPTION 'agreement transition idempotency key conflicts with prior event';
    END IF;
    RETURN QUERY SELECT p_agreement_id,
      v_prior.event_payload->>'resulting_status',v_prior.agreement_event_id;
    RETURN;
  END IF;

  IF v_agreement.agreement_status<>p_expected_status THEN
    RAISE EXCEPTION 'agreement status conflict: expected %, found %',
      p_expected_status,v_agreement.agreement_status;
  END IF;

  IF p_event_type='agreement_renewed' THEN
    SELECT * INTO v_successor
    FROM sw_property.occupancy_agreement
    WHERE occupancy_agreement.agreement_id=p_successor_agreement_id
    FOR UPDATE;
    IF NOT FOUND
       OR v_successor.property_id<>v_agreement.property_id
       OR v_successor.unit_id<>v_agreement.unit_id
       OR v_successor.tenant_business_id IS DISTINCT FROM v_agreement.tenant_business_id
       OR v_successor.agreement_status NOT IN ('draft','proposed') THEN
      RAISE EXCEPTION 'renewal successor must be a draft agreement for the same property, unit and tenant';
    END IF;
  END IF;

  v_event_id := sw_property.append_occupancy_agreement_event(
    p_agreement_id,p_event_type,p_effective_tick,p_recorded_tick,
    p_actor_ref,p_source_ref,p_idempotency_key,p_evidence_class,
    NULL,p_successor_agreement_id,v_payload
  );

  UPDATE sw_property.occupancy_agreement
  SET agreement_status=v_resulting_status
  WHERE occupancy_agreement.agreement_id=p_agreement_id;

  IF p_event_type='agreement_renewed' THEN
    UPDATE sw_property.occupancy_agreement
    SET agreement_status='active'
    WHERE occupancy_agreement.agreement_id=p_successor_agreement_id;
  END IF;

  -- Physical occupancy is intentionally untouched. A separate explicit
  -- occupancy action is required to end or replace an occupant.
  RETURN QUERY SELECT p_agreement_id,v_resulting_status,v_event_id;
END
$bp04$;

REVOKE ALL ON FUNCTION sw_property.transition_occupancy_agreement(
  text,text,text,bigint,bigint,text,text,text,text,text,jsonb
) FROM PUBLIC;
COMMIT;
