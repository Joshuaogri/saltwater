-- BP04-14 agreement assignment with separate legal and physical occupancy.
-- Assignment changes the contractual tenant only; operator/occupant records are
-- retained. Current subletting relationships must be ended before assignment.
BEGIN;

CREATE FUNCTION sw_property.assign_occupancy_agreement_tenant(
  p_agreement_id text,
  p_expected_tenant_business_id text,
  p_new_tenant_business_id text,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text,
  p_evidence_class text
) RETURNS TABLE(agreement_id text,tenant_business_id text,agreement_event_id uuid)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_agreement sw_property.occupancy_agreement%ROWTYPE;
  v_prior sw_property.occupancy_agreement_event%ROWTYPE;
  v_payload jsonb;
  v_event_id uuid;
  v_rows integer;
BEGIN
  IF p_agreement_id IS NULL OR p_expected_tenant_business_id IS NULL
     OR p_new_tenant_business_id IS NULL
     OR p_expected_tenant_business_id=p_new_tenant_business_id
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_evidence_class NOT IN ('source_documented','generated_fictional_canon','gameplay_action') THEN
    RAISE EXCEPTION 'invalid agreement assignment request';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.business
    WHERE business_id=p_new_tenant_business_id
  ) THEN RAISE EXCEPTION 'assignee business does not exist'; END IF;

  SELECT * INTO v_agreement
  FROM sw_property.occupancy_agreement
  WHERE occupancy_agreement.agreement_id=p_agreement_id
  FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'occupancy agreement not found'; END IF;

  v_payload := jsonb_build_object(
    'prior_tenant_business_id',p_expected_tenant_business_id,
    'new_tenant_business_id',p_new_tenant_business_id,
    'operator_business_id',v_agreement.operator_business_id,
    'physical_occupancy_mutated',false
  );

  SELECT * INTO v_prior
  FROM sw_property.occupancy_agreement_event
  WHERE agreement_id=p_agreement_id AND idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.event_type<>'agreement_assigned'
       OR v_prior.effective_tick<>p_effective_tick
       OR v_prior.recorded_tick<>p_recorded_tick
       OR v_prior.actor_ref<>p_actor_ref
       OR v_prior.source_ref<>p_source_ref
       OR v_prior.evidence_class<>p_evidence_class
       OR v_prior.event_payload<>v_payload THEN
      RAISE EXCEPTION 'agreement assignment idempotency key conflicts with prior event';
    END IF;
    RETURN QUERY SELECT p_agreement_id,p_new_tenant_business_id,v_prior.agreement_event_id;
    RETURN;
  END IF;

  IF v_agreement.tenant_business_id IS DISTINCT FROM p_expected_tenant_business_id
     OR v_agreement.agreement_status NOT IN ('active','seasonal','temporarily_inactive') THEN
    RAISE EXCEPTION 'agreement tenant or lifecycle state conflicts with assignment request';
  END IF;
  IF EXISTS (
    SELECT 1 FROM sw_property.occupancy_relationship
    WHERE superior_agreement_id=p_agreement_id AND relationship_status='active'
  ) THEN
    RAISE EXCEPTION 'active subletting relationships must end before agreement assignment';
  END IF;

  v_event_id := sw_property.append_occupancy_agreement_event(
    p_agreement_id,'agreement_assigned',p_effective_tick,p_recorded_tick,
    p_actor_ref,p_source_ref,p_idempotency_key,p_evidence_class,
    NULL,NULL,v_payload
  );

  UPDATE sw_property.occupancy_agreement
  SET tenant_business_id=p_new_tenant_business_id
  WHERE occupancy_agreement.agreement_id=p_agreement_id;

  UPDATE sw_property.contractual_rights_index
  SET holder_business_id=p_new_tenant_business_id
  WHERE source_agreement_id=p_agreement_id
    AND right_type='contractual_lease_licence_or_concession'
    AND holder_business_id=p_expected_tenant_business_id
    AND right_status='current';
  GET DIAGNOSTICS v_rows = ROW_COUNT;
  IF v_rows<>1 THEN
    RAISE EXCEPTION 'assignment requires exactly one current contractual occupancy-right index';
  END IF;

  -- A subletting permission held by the former tenant does not silently pass
  -- to the assignee. New permission must be recorded explicitly.
  UPDATE sw_property.contractual_rights_index
  SET right_status='historical_expired'
  WHERE source_agreement_id=p_agreement_id
    AND right_type='subletting'
    AND holder_business_id=p_expected_tenant_business_id
    AND right_status='current';

  -- Operator, physical occupancy, and primary unit link are deliberately not
  -- rewritten by a legal assignment. A separate occupancy action owns handover.
  RETURN QUERY SELECT p_agreement_id,p_new_tenant_business_id,v_event_id;
END
$bp04$;

REVOKE ALL ON FUNCTION sw_property.assign_occupancy_agreement_tenant(
  text,text,text,bigint,bigint,text,text,text,text
) FROM PUBLIC;
COMMIT;
