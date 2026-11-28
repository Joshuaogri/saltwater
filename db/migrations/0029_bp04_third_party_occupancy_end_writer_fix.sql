-- BP04-29: qualify third-party termination target to avoid OUT-parameter ambiguity.
BEGIN;
CREATE OR REPLACE FUNCTION sw_property.end_third_party_occupancy_relationship(
  p_relationship_id text,p_effective_tick bigint,p_recorded_tick bigint,
  p_actor_ref text,p_source_ref text,p_idempotency_key text
) RETURNS TABLE(relationship_id text,relationship_status text)
LANGUAGE plpgsql AS $bp04$
DECLARE v_relationship sw_property.third_party_occupancy_relationship%ROWTYPE;
BEGIN
  IF p_relationship_id IS NULL OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$' THEN
    RAISE EXCEPTION 'invalid third-party occupancy end request';
  END IF;
  SELECT r.* INTO v_relationship FROM sw_property.third_party_occupancy_relationship AS r
  WHERE r.relationship_id=p_relationship_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'third-party occupancy relationship not found'; END IF;
  PERFORM 1 FROM sw_property.unit_space AS u
  WHERE u.unit_id=v_relationship.unit_id AND u.property_id=v_relationship.property_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'third-party occupancy unit not found'; END IF;
  SELECT r.* INTO v_relationship FROM sw_property.third_party_occupancy_relationship AS r
  WHERE r.relationship_id=p_relationship_id FOR UPDATE;
  IF v_relationship.relationship_status='ended' THEN
    IF v_relationship.end_idempotency_key<>p_idempotency_key
       OR v_relationship.effective_to_tick<>p_effective_tick
       OR v_relationship.end_recorded_tick<>p_recorded_tick
       OR v_relationship.end_actor_ref<>p_actor_ref
       OR v_relationship.end_source_ref<>p_source_ref THEN
      RAISE EXCEPTION 'third-party occupancy end conflicts with prior terminal event';
    END IF;
    RETURN QUERY SELECT v_relationship.relationship_id,'ended'::text;
    RETURN;
  END IF;
  IF p_effective_tick<=v_relationship.effective_from_tick
     OR p_recorded_tick<v_relationship.recorded_tick THEN
    RAISE EXCEPTION 'third-party occupancy end ticks must follow the recorded relationship';
  END IF;
  UPDATE sw_property.third_party_occupancy_relationship AS target
  SET relationship_status='ended',effective_to_tick=p_effective_tick,
      end_idempotency_key=p_idempotency_key,end_actor_ref=p_actor_ref,
      end_source_ref=p_source_ref,end_recorded_tick=p_recorded_tick
  WHERE target.relationship_id=p_relationship_id;
  RETURN QUERY SELECT p_relationship_id,'ended'::text;
END
$bp04$;
REVOKE ALL ON FUNCTION sw_property.end_third_party_occupancy_relationship(text,bigint,bigint,text,text,text) FROM PUBLIC;
COMMIT;
