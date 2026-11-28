-- Serialize subletting termination with starts on the same physical unit.
-- All non-player parties are NPCs; this is a simulation lifecycle consistency rule.
BEGIN;

CREATE OR REPLACE FUNCTION sw_property.end_subletting_relationship(
  p_relationship_id text,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text
) RETURNS TABLE(relationship_id text,relationship_status text)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_relationship sw_property.occupancy_relationship%ROWTYPE;
  v_prior_event sw_property.occupancy_agreement_event%ROWTYPE;
  v_unit_id text;
BEGIN
  IF p_relationship_id IS NULL OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$' THEN
    RAISE EXCEPTION 'invalid subletting end request';
  END IF;

  -- Discover the immutable unit key, then take the same unit-first lock used
  -- by the start writer before locking the relationship or appending events.
  SELECT rel.unit_id INTO v_unit_id
  FROM sw_property.occupancy_relationship AS rel
  WHERE rel.relationship_id=p_relationship_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'occupancy relationship not found'; END IF;

  PERFORM 1 FROM sw_property.unit_space AS u
  WHERE u.unit_id=v_unit_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'subletting unit not found'; END IF;

  SELECT rel.* INTO v_relationship
  FROM sw_property.occupancy_relationship AS rel
  WHERE rel.relationship_id=p_relationship_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'occupancy relationship not found'; END IF;
  IF v_relationship.unit_id<>v_unit_id THEN
    RAISE EXCEPTION 'subletting relationship unit changed during termination';
  END IF;

  IF v_relationship.relationship_status='ended' THEN
    SELECT * INTO v_prior_event
    FROM sw_property.occupancy_agreement_event
    WHERE agreement_id=v_relationship.superior_agreement_id
      AND idempotency_key=p_idempotency_key;
    IF v_relationship.end_idempotency_key<>p_idempotency_key
       OR v_relationship.effective_to_tick<>p_effective_tick
       OR NOT FOUND
       OR v_prior_event.event_type<>'subletting_ended'
       OR v_prior_event.recorded_tick<>p_recorded_tick
       OR v_prior_event.actor_ref<>p_actor_ref
       OR v_prior_event.source_ref<>p_source_ref
       OR v_prior_event.event_payload->>'relationship_id' IS DISTINCT FROM p_relationship_id
       OR v_prior_event.event_payload->>'subtenant_business_id' IS DISTINCT FROM v_relationship.subtenant_business_id THEN
      RAISE EXCEPTION 'subletting end conflicts with prior terminal event';
    END IF;
    RETURN QUERY SELECT v_relationship.relationship_id,'ended'::text;
    RETURN;
  END IF;
  IF p_effective_tick<=v_relationship.effective_from_tick THEN
    RAISE EXCEPTION 'subletting end tick must follow relationship start';
  END IF;

  PERFORM sw_property.append_occupancy_agreement_event(
    v_relationship.superior_agreement_id,'subletting_ended',
    p_effective_tick,p_recorded_tick,p_actor_ref,p_source_ref,p_idempotency_key,
    'gameplay_action',NULL,v_relationship.sub_agreement_id,
    jsonb_build_object('relationship_id',p_relationship_id,
      'subtenant_business_id',v_relationship.subtenant_business_id)
  );
  UPDATE sw_property.occupancy_relationship
  SET relationship_status='ended',effective_to_tick=p_effective_tick,
      end_idempotency_key=p_idempotency_key
  WHERE occupancy_relationship.relationship_id=p_relationship_id;
  -- Ending the legal subletting relationship does not evict or end physical occupancy.
  RETURN QUERY SELECT p_relationship_id,'ended'::text;
END
$bp04$;

REVOKE ALL ON FUNCTION sw_property.end_subletting_relationship(
  text,bigint,bigint,text,text,text
) FROM PUBLIC;
COMMIT;
