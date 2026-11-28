-- BP04-16 explicit physical business-occupancy handover.
-- Legal agreement and title ownership remain separate projections.
BEGIN;

CREATE TABLE sw_property.occupancy_handover_event (
  handover_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  unit_id text NOT NULL REFERENCES sw_property.unit_space(unit_id)
    DEFERRABLE INITIALLY DEFERRED,
  prior_occupancy_id text NOT NULL REFERENCES sw_property.occupancy(occupancy_id)
    DEFERRABLE INITIALLY DEFERRED,
  new_occupancy_id text NOT NULL UNIQUE REFERENCES sw_property.occupancy(occupancy_id)
    DEFERRABLE INITIALLY DEFERRED,
  prior_agreement_id text NOT NULL REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  new_agreement_id text NOT NULL REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  prior_occupant_business_id text NOT NULL REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  new_occupant_business_id text NOT NULL REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  prior_business_unit_link_id text NOT NULL REFERENCES sw_property.business_unit_link(business_unit_link_id)
    DEFERRABLE INITIALLY DEFERRED,
  new_business_unit_link_id text NOT NULL UNIQUE REFERENCES sw_property.business_unit_link(business_unit_link_id)
    DEFERRABLE INITIALLY DEFERRED,
  effective_year integer NOT NULL CHECK (effective_year>=1),
  effective_tick bigint NOT NULL CHECK (effective_tick>=0),
  recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL
    CHECK (idempotency_key ~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'),
  evidence_class text NOT NULL CHECK (evidence_class IN (
    'source_documented','generated_fictional_canon','gameplay_action'
  )),
  event_payload jsonb NOT NULL CHECK (jsonb_typeof(event_payload)='object'),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE (property_id,idempotency_key),
  CHECK (prior_occupancy_id<>new_occupancy_id),
  CHECK (prior_agreement_id<>new_agreement_id),
  CHECK (prior_occupant_business_id<>new_occupant_business_id)
);
CREATE INDEX occupancy_handover_unit_history_idx
  ON sw_property.occupancy_handover_event(unit_id,effective_tick);

CREATE FUNCTION sw_property.reject_occupancy_handover_event_mutation()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  RAISE EXCEPTION 'occupancy handover event history is append-only';
END
$bp04$;

CREATE TRIGGER occupancy_handover_event_immutable
BEFORE UPDATE OR DELETE ON sw_property.occupancy_handover_event
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_occupancy_handover_event_mutation();

CREATE FUNCTION sw_property.handover_business_occupancy(
  p_property_id text,
  p_unit_id text,
  p_prior_occupancy_id text,
  p_new_agreement_id text,
  p_new_occupant_business_id text,
  p_effective_year integer,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text,
  p_evidence_class text
) RETURNS TABLE(
  handover_event_id uuid,
  prior_occupancy_id text,
  new_occupancy_id text,
  new_business_unit_link_id text
)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_old_occupancy sw_property.occupancy%ROWTYPE;
  v_old_agreement sw_property.occupancy_agreement%ROWTYPE;
  v_new_agreement sw_property.occupancy_agreement%ROWTYPE;
  v_old_link sw_property.business_unit_link%ROWTYPE;
  v_prior sw_property.occupancy_handover_event%ROWTYPE;
  v_event_id uuid;
  v_new_occupancy_id text;
  v_new_link_id text;
  v_latest_effective bigint;
  v_latest_recorded bigint;
  v_payload jsonb;
BEGIN
  IF p_property_id IS NULL OR p_unit_id IS NULL OR p_prior_occupancy_id IS NULL
     OR p_new_agreement_id IS NULL OR p_new_occupant_business_id IS NULL
     OR p_effective_year IS NULL OR p_effective_year<1
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_evidence_class IS NULL OR p_evidence_class NOT IN (
       'source_documented','generated_fictional_canon','gameplay_action'
     ) THEN
    RAISE EXCEPTION 'invalid business occupancy handover request';
  END IF;

  PERFORM 1 FROM sw_property.unit_space AS u
  WHERE u.unit_id=p_unit_id AND u.property_id=p_property_id
  FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'property unit not found'; END IF;

  SELECT ev.* INTO v_prior
  FROM sw_property.occupancy_handover_event AS ev
  WHERE ev.property_id=p_property_id AND ev.idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.unit_id<>p_unit_id
       OR v_prior.prior_occupancy_id<>p_prior_occupancy_id
       OR v_prior.new_agreement_id<>p_new_agreement_id
       OR v_prior.new_occupant_business_id<>p_new_occupant_business_id
       OR v_prior.effective_year<>p_effective_year
       OR v_prior.effective_tick<>p_effective_tick
       OR v_prior.recorded_tick<>p_recorded_tick
       OR v_prior.actor_ref<>p_actor_ref
       OR v_prior.source_ref<>p_source_ref
       OR v_prior.evidence_class<>p_evidence_class THEN
      RAISE EXCEPTION 'occupancy handover idempotency key conflicts with prior event';
    END IF;
    RETURN QUERY SELECT v_prior.handover_event_id,v_prior.prior_occupancy_id,
      v_prior.new_occupancy_id,v_prior.new_business_unit_link_id;
    RETURN;
  END IF;

  SELECT o.* INTO v_old_occupancy
  FROM sw_property.occupancy AS o
  WHERE o.occupancy_id=p_prior_occupancy_id
  FOR UPDATE;
  IF NOT FOUND OR v_old_occupancy.property_id<>p_property_id
     OR v_old_occupancy.unit_id<>p_unit_id
     OR v_old_occupancy.effective_to_year IS NOT NULL
     OR v_old_occupancy.occupancy_status NOT IN (
       'occupied','seasonal_occupation','temporarily_suspended_occupation'
     )
     OR v_old_occupancy.occupant_business_id IS NULL THEN
    RAISE EXCEPTION 'prior occupancy must be current and match the requested property/unit';
  END IF;

  SELECT a.* INTO v_old_agreement
  FROM sw_property.occupancy_agreement AS a
  WHERE a.agreement_id=v_old_occupancy.agreement_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'prior occupancy agreement not found'; END IF;

  SELECT a.* INTO v_new_agreement
  FROM sw_property.occupancy_agreement AS a
  WHERE a.agreement_id=p_new_agreement_id
  FOR UPDATE;
  IF NOT FOUND OR v_new_agreement.property_id<>p_property_id
     OR v_new_agreement.unit_id<>p_unit_id
     OR v_new_agreement.agreement_status NOT IN ('active','seasonal','temporarily_inactive')
     OR (v_new_agreement.tenant_business_id IS DISTINCT FROM p_new_occupant_business_id
         AND v_new_agreement.operator_business_id IS DISTINCT FROM p_new_occupant_business_id) THEN
    RAISE EXCEPTION 'new agreement must be current and authorise the incoming tenant/operator at this unit';
  END IF;
  IF p_new_occupant_business_id=v_old_occupancy.occupant_business_id THEN
    RAISE EXCEPTION 'occupancy handover must identify a different incoming business';
  END IF;
  IF v_old_occupancy.effective_from_year IS NOT NULL
     AND p_effective_year<=v_old_occupancy.effective_from_year THEN
    RAISE EXCEPTION 'occupancy handover year must follow prior occupancy start';
  END IF;

  SELECT l.* INTO v_old_link
  FROM sw_property.business_unit_link AS l
  WHERE l.unit_id=p_unit_id AND l.valid_to_tick IS NULL
  FOR UPDATE;
  IF NOT FOUND OR v_old_link.business_id<>v_old_occupancy.occupant_business_id
     OR v_old_link.establishment_id IS DISTINCT FROM v_old_occupancy.establishment_id
     OR v_old_link.premises_id IS DISTINCT FROM v_old_occupancy.premises_id THEN
    RAISE EXCEPTION 'current primary business-unit link must match the prior occupant';
  END IF;
  IF p_effective_tick<=v_old_link.valid_from_tick THEN
    RAISE EXCEPTION 'handover tick must follow prior primary unit-link start';
  END IF;

  IF EXISTS (
    SELECT 1 FROM sw_property.occupancy AS o
    WHERE o.unit_id=p_unit_id AND o.effective_to_year IS NULL
      AND o.occupancy_id<>p_prior_occupancy_id
  ) THEN
    RAISE EXCEPTION 'other current occupants must be explicitly ended before exclusive primary handover';
  END IF;
  IF EXISTS (
    SELECT 1 FROM sw_property.business_unit_link AS l
    WHERE l.unit_id=p_unit_id AND l.valid_to_tick IS NULL
      AND l.business_id=p_new_occupant_business_id
  ) THEN
    RAISE EXCEPTION 'incoming business already holds the current primary unit link';
  END IF;

  SELECT max(ev.effective_tick),max(ev.recorded_tick)
  INTO v_latest_effective,v_latest_recorded
  FROM sw_property.occupancy_handover_event AS ev
  WHERE ev.unit_id=p_unit_id;
  IF v_latest_effective IS NOT NULL AND p_effective_tick<v_latest_effective THEN
    RAISE EXCEPTION 'occupancy handover effective tick cannot move backwards';
  END IF;
  IF v_latest_recorded IS NOT NULL AND p_recorded_tick<v_latest_recorded THEN
    RAISE EXCEPTION 'occupancy handover recorded tick cannot move backwards';
  END IF;

  v_event_id := gen_random_uuid();
  v_new_occupancy_id := 'SWOCC-GAME-' || replace(gen_random_uuid()::text,'-','');
  v_new_link_id := 'SWBUL-GAME-' || replace(gen_random_uuid()::text,'-','');
  v_payload := jsonb_build_object(
    'prior_occupant_business_id',v_old_occupancy.occupant_business_id,
    'new_occupant_business_id',p_new_occupant_business_id,
    'prior_agreement_id',v_old_occupancy.agreement_id,
    'new_agreement_id',p_new_agreement_id,
    'new_occupancy_id',v_new_occupancy_id,
    'new_business_unit_link_id',v_new_link_id,
    'population_mutated',false
  );

  UPDATE sw_property.occupancy
  SET effective_to_year=p_effective_year,occupancy_status='vacated'
  WHERE occupancy_id=p_prior_occupancy_id;
  UPDATE sw_property.business_unit_link
  SET valid_to_tick=p_effective_tick,occupancy_status='ended'
  WHERE business_unit_link_id=v_old_link.business_unit_link_id;

  INSERT INTO sw_property.occupancy(
    occupancy_id,property_id,building_id,premises_id,unit_id,
    occupant_business_id,establishment_id,agreement_id,occupant_type,
    occupancy_status,effective_from_year,effective_to_year,source_dataset
  ) VALUES (
    v_new_occupancy_id,p_property_id,v_new_agreement.building_id,
    v_new_agreement.premises_id,p_unit_id,p_new_occupant_business_id,
    v_new_agreement.establishment_id,p_new_agreement_id,'business',
    'occupied',p_effective_year,NULL,'BP04-GAMEPLAY-OCCUPANCY-HANDOVER'
  );

  INSERT INTO sw_property.business_unit_link(
    business_unit_link_id,business_id,establishment_id,unit_id,premises_id,
    valid_from_tick,valid_to_tick,occupancy_relationship,occupancy_status,source_dataset
  ) VALUES (
    v_new_link_id,p_new_occupant_business_id,v_new_agreement.establishment_id,
    p_unit_id,v_new_agreement.premises_id,p_effective_tick,NULL,
    'primary_tenant','occupied','BP04-GAMEPLAY-OCCUPANCY-HANDOVER'
  );

  INSERT INTO sw_property.occupancy_handover_event(
    handover_event_id,property_id,unit_id,prior_occupancy_id,new_occupancy_id,
    prior_agreement_id,new_agreement_id,prior_occupant_business_id,new_occupant_business_id,
    prior_business_unit_link_id,new_business_unit_link_id,effective_year,
    effective_tick,recorded_tick,actor_ref,source_ref,idempotency_key,evidence_class,event_payload
  ) VALUES (
    v_event_id,p_property_id,p_unit_id,p_prior_occupancy_id,v_new_occupancy_id,
    v_old_occupancy.agreement_id,p_new_agreement_id,v_old_occupancy.occupant_business_id,
    p_new_occupant_business_id,v_old_link.business_unit_link_id,v_new_link_id,
    p_effective_year,p_effective_tick,p_recorded_tick,p_actor_ref,p_source_ref,
    p_idempotency_key,p_evidence_class,v_payload
  );

  RETURN QUERY SELECT v_event_id,p_prior_occupancy_id,v_new_occupancy_id,v_new_link_id;
END
$bp04$;

REVOKE ALL ON sw_property.occupancy_handover_event FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.handover_business_occupancy(
  text,text,text,text,text,integer,bigint,bigint,text,text,text,text
) FROM PUBLIC;
COMMIT;
