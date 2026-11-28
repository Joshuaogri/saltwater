-- BP04-11 append-only occupancy-agreement event history.
-- Applies to the existing canonical occupancy_agreement projection.
-- Validate on disposable PostgreSQL; no production Neon write is performed here.
BEGIN;

CREATE TABLE sw_property.occupancy_agreement_event (
  agreement_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agreement_id text NOT NULL REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  event_type text NOT NULL CHECK (event_type IN (
    'agreement_baseline_registered','agreement_executed','agreement_commenced',
    'agreement_varied','agreement_renewed','agreement_expired',
    'agreement_terminated','agreement_assigned','agreement_surrendered',
    'subletting_authorised','subletting_ended'
  )),
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  recorded_tick bigint NOT NULL CHECK (recorded_tick >= 0),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL CHECK (idempotency_key ~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'),
  evidence_class text NOT NULL CHECK (evidence_class IN (
    'source_documented','generated_fictional_canon','gameplay_action'
  )),
  predecessor_agreement_id text REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  successor_agreement_id text REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  event_payload jsonb NOT NULL DEFAULT '{}'::jsonb
    CHECK (jsonb_typeof(event_payload)='object'),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE (agreement_id,idempotency_key),
  CHECK (predecessor_agreement_id IS NULL OR predecessor_agreement_id<>agreement_id),
  CHECK (successor_agreement_id IS NULL OR successor_agreement_id<>agreement_id),
  CHECK (event_type<>'agreement_renewed' OR successor_agreement_id IS NOT NULL)
);
CREATE INDEX occupancy_agreement_event_history_idx
  ON sw_property.occupancy_agreement_event(agreement_id,effective_tick,agreement_event_id);
CREATE INDEX occupancy_agreement_event_type_idx
  ON sw_property.occupancy_agreement_event(event_type,effective_tick);

CREATE FUNCTION sw_property.reject_agreement_event_mutation()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  RAISE EXCEPTION 'occupancy agreement event history is append-only';
END
$bp04$;

CREATE TRIGGER occupancy_agreement_event_immutable
BEFORE UPDATE OR DELETE ON sw_property.occupancy_agreement_event
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_agreement_event_mutation();

CREATE FUNCTION sw_property.append_occupancy_agreement_event(
  p_agreement_id text,
  p_event_type text,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text,
  p_evidence_class text,
  p_predecessor_agreement_id text,
  p_successor_agreement_id text,
  p_event_payload jsonb
) RETURNS uuid
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_agreement sw_property.occupancy_agreement%ROWTYPE;
  v_related sw_property.occupancy_agreement%ROWTYPE;
  v_prior sw_property.occupancy_agreement_event%ROWTYPE;
  v_latest_effective bigint;
  v_latest_recorded bigint;
  v_event_id uuid;
BEGIN
  IF p_agreement_id IS NULL OR p_event_type IS NULL
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_evidence_class NOT IN ('source_documented','generated_fictional_canon','gameplay_action')
     OR p_event_payload IS NULL OR jsonb_typeof(p_event_payload)<>'object' THEN
    RAISE EXCEPTION 'invalid occupancy agreement event request';
  END IF;

  SELECT * INTO v_agreement
  FROM sw_property.occupancy_agreement
  WHERE agreement_id=p_agreement_id
  FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'occupancy agreement not found'; END IF;

  SELECT * INTO v_prior
  FROM sw_property.occupancy_agreement_event
  WHERE agreement_id=p_agreement_id AND idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.event_type<>p_event_type
       OR v_prior.effective_tick<>p_effective_tick
       OR v_prior.recorded_tick<>p_recorded_tick
       OR v_prior.actor_ref<>p_actor_ref
       OR v_prior.source_ref<>p_source_ref
       OR v_prior.evidence_class<>p_evidence_class
       OR v_prior.predecessor_agreement_id IS DISTINCT FROM p_predecessor_agreement_id
       OR v_prior.successor_agreement_id IS DISTINCT FROM p_successor_agreement_id
       OR v_prior.event_payload<>p_event_payload THEN
      RAISE EXCEPTION 'agreement event idempotency key conflicts with prior definition';
    END IF;
    RETURN v_prior.agreement_event_id;
  END IF;

  IF p_predecessor_agreement_id IS NOT NULL THEN
    SELECT * INTO v_related FROM sw_property.occupancy_agreement
    WHERE agreement_id=p_predecessor_agreement_id;
    IF NOT FOUND OR v_related.property_id<>v_agreement.property_id
       OR v_related.unit_id<>v_agreement.unit_id THEN
      RAISE EXCEPTION 'predecessor agreement must reference the same property and unit';
    END IF;
  END IF;
  IF p_successor_agreement_id IS NOT NULL THEN
    SELECT * INTO v_related FROM sw_property.occupancy_agreement
    WHERE agreement_id=p_successor_agreement_id;
    IF NOT FOUND OR v_related.property_id<>v_agreement.property_id
       OR v_related.unit_id<>v_agreement.unit_id THEN
      RAISE EXCEPTION 'successor agreement must reference the same property and unit';
    END IF;
  END IF;
  IF p_event_type='agreement_renewed' THEN
    SELECT * INTO v_related FROM sw_property.occupancy_agreement
    WHERE agreement_id=p_successor_agreement_id;
    IF v_related.tenant_business_id IS DISTINCT FROM v_agreement.tenant_business_id THEN
      RAISE EXCEPTION 'renewal successor must preserve the tenant business';
    END IF;
  END IF;

  SELECT max(effective_tick),max(recorded_tick)
  INTO v_latest_effective,v_latest_recorded
  FROM sw_property.occupancy_agreement_event
  WHERE agreement_id=p_agreement_id;
  IF v_latest_effective IS NOT NULL AND p_effective_tick<v_latest_effective THEN
    RAISE EXCEPTION 'agreement event effective tick cannot move backwards';
  END IF;
  IF v_latest_recorded IS NOT NULL AND p_recorded_tick<v_latest_recorded THEN
    RAISE EXCEPTION 'agreement event recorded tick cannot move backwards';
  END IF;

  INSERT INTO sw_property.occupancy_agreement_event(
    agreement_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,
    idempotency_key,evidence_class,predecessor_agreement_id,
    successor_agreement_id,event_payload
  ) VALUES (
    p_agreement_id,p_event_type,p_effective_tick,p_recorded_tick,p_actor_ref,p_source_ref,
    p_idempotency_key,p_evidence_class,p_predecessor_agreement_id,
    p_successor_agreement_id,coalesce(p_event_payload,'{}'::jsonb)
  ) RETURNING agreement_event_id INTO v_event_id;

  RETURN v_event_id;
END
$bp04$;

REVOKE ALL ON sw_property.occupancy_agreement_event FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.append_occupancy_agreement_event(
  text,text,bigint,bigint,text,text,text,text,text,text,jsonb
) FROM PUBLIC;
COMMIT;
