-- BP04-20 serialize subletting creation with physical occupancy handover.
-- Use the same unit-before-agreement lock order as the handover writer.
BEGIN;

CREATE OR REPLACE FUNCTION sw_property.record_subletting_relationship(
  p_relationship_id text,
  p_superior_agreement_id text,
  p_sub_agreement_id text,
  p_superior_occupancy_id text,
  p_sub_occupancy_id text,
  p_subletting_right_id text,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text
) RETURNS TABLE(relationship_id text,relationship_status text)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_superior sw_property.occupancy_agreement%ROWTYPE;
  v_sub sw_property.occupancy_agreement%ROWTYPE;
  v_right sw_property.contractual_rights_index%ROWTYPE;
  v_superior_occupancy sw_property.occupancy%ROWTYPE;
  v_sub_occupancy sw_property.occupancy%ROWTYPE;
  v_prior sw_property.occupancy_relationship%ROWTYPE;
  v_property_id text;
  v_unit_id text;
BEGIN
  IF p_relationship_id IS NULL OR length(trim(p_relationship_id)) NOT BETWEEN 1 AND 128
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$' THEN
    RAISE EXCEPTION 'invalid subletting relationship request';
  END IF;

  SELECT * INTO v_prior FROM sw_property.occupancy_relationship
  WHERE idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.relationship_id<>p_relationship_id
       OR v_prior.superior_agreement_id<>p_superior_agreement_id
       OR v_prior.sub_agreement_id<>p_sub_agreement_id
       OR v_prior.superior_occupancy_id<>p_superior_occupancy_id
       OR v_prior.sub_occupancy_id<>p_sub_occupancy_id
       OR v_prior.subletting_right_id<>p_subletting_right_id
       OR v_prior.effective_from_tick<>p_effective_tick
       OR v_prior.recorded_tick<>p_recorded_tick
       OR v_prior.actor_ref<>p_actor_ref OR v_prior.source_ref<>p_source_ref THEN
      RAISE EXCEPTION 'subletting relationship idempotency key conflicts with prior definition';
    END IF;
    RETURN QUERY SELECT v_prior.relationship_id,v_prior.relationship_status;
    RETURN;
  END IF;

  -- Match the physical handover writer's lock order: unit first, then
  -- agreements. This serializes subletting creation against exclusive handover.
  SELECT a.property_id,a.unit_id INTO v_property_id,v_unit_id
  FROM sw_property.occupancy_agreement AS a
  WHERE a.agreement_id=p_superior_agreement_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'superior agreement must exist'; END IF;

  PERFORM 1 FROM sw_property.unit_space AS u
  WHERE u.unit_id=v_unit_id AND u.property_id=v_property_id
  FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'subletting property unit not found'; END IF;

  -- Lock both agreements in a stable order to avoid reversed-pair deadlocks.
  PERFORM 1 FROM sw_property.occupancy_agreement
  WHERE agreement_id IN (p_superior_agreement_id,p_sub_agreement_id)
  ORDER BY agreement_id FOR UPDATE;

  -- Recheck after acquiring both agreement locks. A concurrent exact request
  -- may have committed while this transaction waited.
  SELECT * INTO v_prior FROM sw_property.occupancy_relationship
  WHERE idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.relationship_id<>p_relationship_id
       OR v_prior.superior_agreement_id<>p_superior_agreement_id
       OR v_prior.sub_agreement_id<>p_sub_agreement_id
       OR v_prior.superior_occupancy_id<>p_superior_occupancy_id
       OR v_prior.sub_occupancy_id<>p_sub_occupancy_id
       OR v_prior.subletting_right_id<>p_subletting_right_id
       OR v_prior.effective_from_tick<>p_effective_tick
       OR v_prior.recorded_tick<>p_recorded_tick
       OR v_prior.actor_ref<>p_actor_ref OR v_prior.source_ref<>p_source_ref THEN
      RAISE EXCEPTION 'subletting relationship idempotency key conflicts with prior definition';
    END IF;
    RETURN QUERY SELECT v_prior.relationship_id,v_prior.relationship_status;
    RETURN;
  END IF;
  SELECT * INTO v_superior FROM sw_property.occupancy_agreement
  WHERE agreement_id=p_superior_agreement_id;
  SELECT * INTO v_sub FROM sw_property.occupancy_agreement
  WHERE agreement_id=p_sub_agreement_id;
  IF v_superior.agreement_id IS NULL OR v_sub.agreement_id IS NULL THEN
    RAISE EXCEPTION 'superior and sub-agreements must both exist';
  END IF;
  IF v_superior.agreement_status NOT IN ('active','seasonal','temporarily_inactive')
     OR v_sub.agreement_status NOT IN ('active','seasonal','temporarily_inactive')
     OR v_sub.agreement_type NOT IN ('sublease','underlease') THEN
    RAISE EXCEPTION 'superior agreement must be current and secondary agreement must be an active sublease';
  END IF;
  IF v_superior.property_id<>v_sub.property_id OR v_superior.unit_id<>v_sub.unit_id
     OR v_superior.tenant_business_id IS NULL
     OR v_superior.tenant_business_id=v_sub.tenant_business_id THEN
    RAISE EXCEPTION 'sublease must preserve property/unit and identify a distinct subtenant';
  END IF;

  SELECT * INTO v_right FROM sw_property.contractual_rights_index
  WHERE property_right_id=p_subletting_right_id;
  IF NOT FOUND OR v_right.right_type<>'subletting'
     OR v_right.right_status<>'current'
     OR v_right.source_agreement_id<>p_superior_agreement_id
     OR v_right.property_id<>v_superior.property_id
     OR v_right.unit_id<>v_superior.unit_id
     OR v_right.holder_business_id IS DISTINCT FROM v_superior.tenant_business_id THEN
    RAISE EXCEPTION 'explicit current subletting right for this superior agreement, tenant and unit is required';
  END IF;

  SELECT * INTO v_superior_occupancy FROM sw_property.occupancy
  WHERE occupancy_id=p_superior_occupancy_id;
  SELECT * INTO v_sub_occupancy FROM sw_property.occupancy
  WHERE occupancy_id=p_sub_occupancy_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'subtenant occupancy record not found'; END IF;
  IF v_superior_occupancy.occupancy_id IS NULL
     OR v_superior_occupancy.agreement_id<>p_superior_agreement_id
     OR v_superior_occupancy.unit_id<>v_superior.unit_id
     OR v_superior_occupancy.occupant_business_id<>v_superior.tenant_business_id
     OR v_superior_occupancy.effective_to_year IS NOT NULL THEN
    RAISE EXCEPTION 'superior occupancy must be current and match the superior tenant';
  END IF;
  IF v_sub_occupancy.occupancy_id IS NULL
     OR v_sub_occupancy.agreement_id<>p_sub_agreement_id
     OR v_sub_occupancy.unit_id<>v_sub.unit_id
     OR v_sub_occupancy.occupant_business_id<>v_sub.tenant_business_id
     OR v_sub_occupancy.occupant_type<>'business_subtenant'
     OR v_sub_occupancy.effective_to_year IS NOT NULL THEN
    RAISE EXCEPTION 'secondary occupancy must explicitly identify the subtenant and sublease';
  END IF;
  IF EXISTS (
    SELECT 1 FROM sw_property.business_unit_link
    WHERE business_id=v_sub.tenant_business_id
      AND unit_id=v_sub.unit_id AND valid_to_tick IS NULL
  ) THEN
    RAISE EXCEPTION 'subtenant cannot acquire a second primary business-unit link';
  END IF;

  INSERT INTO sw_property.occupancy_relationship(
    relationship_id,property_id,unit_id,superior_agreement_id,sub_agreement_id,
    superior_occupancy_id,sub_occupancy_id,subletting_right_id,
    granting_business_id,subtenant_business_id,effective_from_tick,recorded_tick,
    actor_ref,source_ref,idempotency_key
  ) VALUES (
    p_relationship_id,v_superior.property_id,v_superior.unit_id,
    p_superior_agreement_id,p_sub_agreement_id,p_superior_occupancy_id,
    p_sub_occupancy_id,p_subletting_right_id,v_superior.tenant_business_id,
    v_sub.tenant_business_id,p_effective_tick,p_recorded_tick,p_actor_ref,p_source_ref,p_idempotency_key
  );

  PERFORM sw_property.append_occupancy_agreement_event(
    p_superior_agreement_id,'subletting_authorised',p_effective_tick,p_recorded_tick,
    p_actor_ref,p_source_ref,p_idempotency_key,'gameplay_action',NULL,p_sub_agreement_id,
    jsonb_build_object('relationship_id',p_relationship_id,
      'subletting_right_id',p_subletting_right_id,
      'granting_business_id',v_superior.tenant_business_id,
      'subtenant_business_id',v_sub.tenant_business_id)
  );
  RETURN QUERY SELECT p_relationship_id,'active'::text;
END
$bp04$;

REVOKE ALL ON FUNCTION sw_property.record_subletting_relationship(
  text,text,text,text,text,text,bigint,bigint,text,text,text
) FROM PUBLIC;
COMMIT;
