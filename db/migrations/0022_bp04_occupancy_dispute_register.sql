-- BP04-22 auditable occupancy entitlement and consent disputes.
-- Disputes are a separate claim register: opening/resolving a claim never
-- silently changes legal rights, contractual permissions or physical occupancy.
BEGIN;

CREATE TABLE sw_property.occupancy_dispute (
  dispute_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  unit_id text NOT NULL REFERENCES sw_property.unit_space(unit_id)
    DEFERRABLE INITIALLY DEFERRED,
  occupancy_id text NOT NULL REFERENCES sw_property.occupancy(occupancy_id)
    DEFERRABLE INITIALLY DEFERRED,
  agreement_id text REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  property_right_id text REFERENCES sw_property.contractual_rights_index(property_right_id)
    DEFERRABLE INITIALLY DEFERRED,
  occupancy_relationship_id text REFERENCES sw_property.occupancy_relationship(relationship_id)
    DEFERRABLE INITIALLY DEFERRED,
  claimant_organisation_id text REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  claimant_business_id text REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  respondent_organisation_id text REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  respondent_business_id text REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  claim_type text NOT NULL CHECK (claim_type IN (
    'unauthorised_occupancy','occupancy_entitlement','lease_term',
    'subletting_authority','consent_required','consent_revoked',
    'overlapping_occupancy','possession_claim','other'
  )),
  claim_summary text NOT NULL CHECK (length(trim(claim_summary)) BETWEEN 1 AND 2000),
  dispute_status text NOT NULL DEFAULT 'open'
    CHECK (dispute_status IN ('open','upheld','rejected','withdrawn','settled')),
  opened_effective_tick bigint NOT NULL CHECK (opened_effective_tick>=0),
  opened_recorded_tick bigint NOT NULL CHECK (opened_recorded_tick>=0),
  resolved_effective_tick bigint,
  resolved_recorded_tick bigint,
  resolution_outcome text,
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL UNIQUE
    CHECK (idempotency_key ~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'),
  evidence_class text NOT NULL CHECK (evidence_class IN (
    'source_documented','generated_fictional_canon','gameplay_action'
  )),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (num_nonnulls(claimant_organisation_id,claimant_business_id)=1),
  CHECK (num_nonnulls(respondent_organisation_id,respondent_business_id)<=1),
  CHECK (
    claimant_organisation_id IS DISTINCT FROM respondent_organisation_id
    OR claimant_business_id IS DISTINCT FROM respondent_business_id
  ),
  CHECK (
    (dispute_status='open' AND resolved_effective_tick IS NULL
      AND resolved_recorded_tick IS NULL AND resolution_outcome IS NULL)
    OR
    (dispute_status<>'open' AND resolved_effective_tick IS NOT NULL
      AND resolved_recorded_tick IS NOT NULL
      AND resolution_outcome=dispute_status)
  ),
  CHECK (
    claim_type NOT IN ('subletting_authority','consent_required','consent_revoked')
    OR property_right_id IS NOT NULL OR occupancy_relationship_id IS NOT NULL
  )
);
CREATE INDEX occupancy_dispute_unit_status_idx
  ON sw_property.occupancy_dispute(unit_id,dispute_status,opened_effective_tick);
CREATE INDEX occupancy_dispute_occupancy_idx
  ON sw_property.occupancy_dispute(occupancy_id,opened_effective_tick);
CREATE INDEX occupancy_dispute_claimant_idx
  ON sw_property.occupancy_dispute(claimant_organisation_id,claimant_business_id);

CREATE TABLE sw_property.occupancy_dispute_event (
  dispute_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dispute_id text NOT NULL REFERENCES sw_property.occupancy_dispute(dispute_id)
    DEFERRABLE INITIALLY DEFERRED,
  event_type text NOT NULL CHECK (event_type IN (
    'dispute_opened','dispute_upheld','dispute_rejected',
    'dispute_withdrawn','dispute_settled'
  )),
  effective_tick bigint NOT NULL CHECK (effective_tick>=0),
  recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL
    CHECK (idempotency_key ~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'),
  evidence_class text NOT NULL CHECK (evidence_class IN (
    'source_documented','generated_fictional_canon','gameplay_action'
  )),
  event_payload jsonb NOT NULL DEFAULT '{}'::jsonb
    CHECK (jsonb_typeof(event_payload)='object'),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE(dispute_id,idempotency_key)
);
CREATE INDEX occupancy_dispute_event_history_idx
  ON sw_property.occupancy_dispute_event(dispute_id,effective_tick,dispute_event_id);

CREATE FUNCTION sw_property.reject_occupancy_dispute_event_mutation()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  RAISE EXCEPTION 'occupancy dispute event history is append-only';
END
$bp04$;
CREATE TRIGGER occupancy_dispute_event_immutable
BEFORE UPDATE OR DELETE ON sw_property.occupancy_dispute_event
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_occupancy_dispute_event_mutation();

CREATE FUNCTION sw_property.guard_occupancy_dispute_transition()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  IF TG_OP='DELETE'
     OR ROW(NEW.dispute_id,NEW.property_id,NEW.unit_id,NEW.occupancy_id,
       NEW.agreement_id,NEW.property_right_id,NEW.occupancy_relationship_id,
       NEW.claimant_organisation_id,NEW.claimant_business_id,
       NEW.respondent_organisation_id,NEW.respondent_business_id,
       NEW.claim_type,NEW.claim_summary,NEW.opened_effective_tick,
       NEW.opened_recorded_tick,NEW.actor_ref,NEW.source_ref,
       NEW.idempotency_key,NEW.evidence_class,NEW.created_at)
       IS DISTINCT FROM
       ROW(OLD.dispute_id,OLD.property_id,OLD.unit_id,OLD.occupancy_id,
       OLD.agreement_id,OLD.property_right_id,OLD.occupancy_relationship_id,
       OLD.claimant_organisation_id,OLD.claimant_business_id,
       OLD.respondent_organisation_id,OLD.respondent_business_id,
       OLD.claim_type,OLD.claim_summary,OLD.opened_effective_tick,
       OLD.opened_recorded_tick,OLD.actor_ref,OLD.source_ref,
       OLD.idempotency_key,OLD.evidence_class,OLD.created_at)
     OR OLD.dispute_status<>'open'
     OR NEW.dispute_status NOT IN ('upheld','rejected','withdrawn','settled')
     OR NEW.resolved_effective_tick IS NULL
     OR NEW.resolved_recorded_tick IS NULL
     OR NEW.resolved_effective_tick<OLD.opened_effective_tick
     OR NEW.resolved_recorded_tick<OLD.opened_recorded_tick
     OR NEW.resolution_outcome<>NEW.dispute_status THEN
    RAISE EXCEPTION 'occupancy dispute permits one controlled terminal transition only';
  END IF;
  RETURN NEW;
END
$bp04$;
CREATE TRIGGER occupancy_dispute_transition_guard
BEFORE UPDATE OR DELETE ON sw_property.occupancy_dispute
FOR EACH ROW EXECUTE FUNCTION sw_property.guard_occupancy_dispute_transition();

CREATE FUNCTION sw_property.record_occupancy_dispute(
  p_dispute_id text,
  p_occupancy_id text,
  p_claimant_organisation_id text,
  p_claimant_business_id text,
  p_respondent_organisation_id text,
  p_respondent_business_id text,
  p_claim_type text,
  p_claim_summary text,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text,
  p_evidence_class text,
  p_agreement_id text DEFAULT NULL,
  p_property_right_id text DEFAULT NULL,
  p_occupancy_relationship_id text DEFAULT NULL
) RETURNS TABLE(dispute_id text,dispute_status text)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_occupancy sw_property.occupancy%ROWTYPE;
  v_agreement sw_property.occupancy_agreement%ROWTYPE;
  v_right sw_property.contractual_rights_index%ROWTYPE;
  v_relationship sw_property.occupancy_relationship%ROWTYPE;
  v_prior sw_property.occupancy_dispute%ROWTYPE;
BEGIN
  IF p_dispute_id IS NULL OR length(trim(p_dispute_id)) NOT BETWEEN 1 AND 128
     OR p_occupancy_id IS NULL
     OR p_claim_type NOT IN ('unauthorised_occupancy','occupancy_entitlement','lease_term',
       'subletting_authority','consent_required','consent_revoked',
       'overlapping_occupancy','possession_claim','other')
     OR p_claim_summary IS NULL OR length(trim(p_claim_summary)) NOT BETWEEN 1 AND 2000
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_evidence_class NOT IN ('source_documented','generated_fictional_canon','gameplay_action')
     OR num_nonnulls(p_claimant_organisation_id,p_claimant_business_id)<>1
     OR num_nonnulls(p_respondent_organisation_id,p_respondent_business_id)>1 THEN
    RAISE EXCEPTION 'invalid occupancy dispute request';
  END IF;

  SELECT * INTO v_prior FROM sw_property.occupancy_dispute
  WHERE idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.dispute_id<>p_dispute_id OR v_prior.occupancy_id<>p_occupancy_id
       OR v_prior.claimant_organisation_id IS DISTINCT FROM p_claimant_organisation_id
       OR v_prior.claimant_business_id IS DISTINCT FROM p_claimant_business_id
       OR v_prior.respondent_organisation_id IS DISTINCT FROM p_respondent_organisation_id
       OR v_prior.respondent_business_id IS DISTINCT FROM p_respondent_business_id
       OR v_prior.claim_type<>p_claim_type OR v_prior.claim_summary<>p_claim_summary
       OR v_prior.opened_effective_tick<>p_effective_tick
       OR v_prior.opened_recorded_tick<>p_recorded_tick
       OR v_prior.actor_ref<>p_actor_ref OR v_prior.source_ref<>p_source_ref
       OR v_prior.evidence_class<>p_evidence_class
       OR v_prior.agreement_id IS DISTINCT FROM p_agreement_id
       OR v_prior.property_right_id IS DISTINCT FROM p_property_right_id
       OR v_prior.occupancy_relationship_id IS DISTINCT FROM p_occupancy_relationship_id THEN
      RAISE EXCEPTION 'occupancy dispute idempotency key conflicts with prior definition';
    END IF;
    RETURN QUERY SELECT v_prior.dispute_id,v_prior.dispute_status;
    RETURN;
  END IF;

  SELECT o.* INTO v_occupancy FROM sw_property.occupancy AS o
  WHERE o.occupancy_id=p_occupancy_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'disputed occupancy does not exist'; END IF;

  -- Match the occupancy handover/subletting writer lock order: unit first.
  PERFORM 1 FROM sw_property.unit_space AS u
  WHERE u.unit_id=v_occupancy.unit_id AND u.property_id=v_occupancy.property_id
  FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'disputed occupancy unit does not exist'; END IF;
  SELECT o.* INTO v_occupancy FROM sw_property.occupancy AS o
  WHERE o.occupancy_id=p_occupancy_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'disputed occupancy does not exist'; END IF;

  IF p_agreement_id IS NOT NULL THEN
    SELECT a.* INTO v_agreement FROM sw_property.occupancy_agreement AS a
    WHERE a.agreement_id=p_agreement_id;
    IF NOT FOUND OR v_agreement.property_id<>v_occupancy.property_id
       OR v_agreement.unit_id<>v_occupancy.unit_id
       OR (v_occupancy.agreement_id IS NOT NULL AND v_occupancy.agreement_id<>p_agreement_id) THEN
      RAISE EXCEPTION 'dispute agreement must match the target occupancy property and unit';
    END IF;
  END IF;
  IF p_property_right_id IS NOT NULL THEN
    SELECT r.* INTO v_right FROM sw_property.contractual_rights_index AS r
    WHERE r.property_right_id=p_property_right_id;
    IF NOT FOUND OR v_right.property_id<>v_occupancy.property_id
       OR (v_right.unit_id IS NOT NULL AND v_right.unit_id<>v_occupancy.unit_id)
       OR (p_agreement_id IS NOT NULL AND v_right.source_agreement_id<>p_agreement_id) THEN
      RAISE EXCEPTION 'disputed contractual right must match the target occupancy property, unit and agreement';
    END IF;
  END IF;
  IF p_occupancy_relationship_id IS NOT NULL THEN
    SELECT rel.* INTO v_relationship FROM sw_property.occupancy_relationship AS rel
    WHERE rel.relationship_id=p_occupancy_relationship_id;
    IF NOT FOUND OR v_relationship.property_id<>v_occupancy.property_id
       OR v_relationship.unit_id<>v_occupancy.unit_id
       OR (v_relationship.superior_occupancy_id<>p_occupancy_id
           AND v_relationship.sub_occupancy_id<>p_occupancy_id) THEN
      RAISE EXCEPTION 'disputed subletting relationship must include the target occupancy';
    END IF;
  END IF;

  INSERT INTO sw_property.occupancy_dispute(
    dispute_id,property_id,unit_id,occupancy_id,agreement_id,
    property_right_id,occupancy_relationship_id,
    claimant_organisation_id,claimant_business_id,
    respondent_organisation_id,respondent_business_id,
    claim_type,claim_summary,opened_effective_tick,opened_recorded_tick,
    actor_ref,source_ref,idempotency_key,evidence_class
  ) VALUES (
    p_dispute_id,v_occupancy.property_id,v_occupancy.unit_id,p_occupancy_id,
    p_agreement_id,p_property_right_id,p_occupancy_relationship_id,
    p_claimant_organisation_id,p_claimant_business_id,
    p_respondent_organisation_id,p_respondent_business_id,
    p_claim_type,p_claim_summary,p_effective_tick,p_recorded_tick,
    p_actor_ref,p_source_ref,p_idempotency_key,p_evidence_class
  );

  INSERT INTO sw_property.occupancy_dispute_event(
    dispute_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,
    idempotency_key,evidence_class,event_payload
  ) VALUES (
    p_dispute_id,'dispute_opened',p_effective_tick,p_recorded_tick,
    p_actor_ref,p_source_ref,p_idempotency_key,p_evidence_class,
    jsonb_build_object('occupancy_id',p_occupancy_id,'claim_type',p_claim_type,
      'claimant_organisation_id',p_claimant_organisation_id,
      'claimant_business_id',p_claimant_business_id,
      'respondent_organisation_id',p_respondent_organisation_id,
      'respondent_business_id',p_respondent_business_id)
  );

  RETURN QUERY SELECT p_dispute_id,'open'::text;
END
$bp04$;

CREATE FUNCTION sw_property.transition_occupancy_dispute(
  p_dispute_id text,
  p_expected_status text,
  p_resulting_status text,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text,
  p_evidence_class text,
  p_resolution_note text
) RETURNS TABLE(dispute_id text,dispute_status text,dispute_event_id uuid)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_dispute sw_property.occupancy_dispute%ROWTYPE;
  v_prior sw_property.occupancy_dispute_event%ROWTYPE;
  v_event_id uuid;
  v_event_type text;
  v_payload jsonb;
BEGIN
  IF p_dispute_id IS NULL
     OR p_expected_status<>'open'
     OR p_resulting_status NOT IN ('upheld','rejected','withdrawn','settled')
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_evidence_class NOT IN ('source_documented','generated_fictional_canon','gameplay_action')
     OR p_resolution_note IS NULL OR length(trim(p_resolution_note)) NOT BETWEEN 1 AND 2000 THEN
    RAISE EXCEPTION 'invalid occupancy dispute transition request';
  END IF;

  -- Discover the unit, then take the shared unit lock before locking the dispute.
  SELECT d.* INTO v_dispute FROM sw_property.occupancy_dispute AS d
  WHERE d.dispute_id=p_dispute_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'occupancy dispute not found'; END IF;
  PERFORM 1 FROM sw_property.unit_space AS u
  WHERE u.unit_id=v_dispute.unit_id AND u.property_id=v_dispute.property_id
  FOR UPDATE;
  SELECT d.* INTO v_dispute FROM sw_property.occupancy_dispute AS d
  WHERE d.dispute_id=p_dispute_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'occupancy dispute not found'; END IF;

  SELECT e.* INTO v_prior FROM sw_property.occupancy_dispute_event AS e
  WHERE e.dispute_id=p_dispute_id AND e.idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.event_type<>'dispute_'||p_resulting_status
       OR v_prior.effective_tick<>p_effective_tick
       OR v_prior.recorded_tick<>p_recorded_tick
       OR v_prior.actor_ref<>p_actor_ref OR v_prior.source_ref<>p_source_ref
       OR v_prior.evidence_class<>p_evidence_class
       OR v_prior.event_payload->>'resolution_note' IS DISTINCT FROM p_resolution_note THEN
      RAISE EXCEPTION 'occupancy dispute transition idempotency key conflicts with prior event';
    END IF;
    RETURN QUERY SELECT p_dispute_id,p_resulting_status,v_prior.dispute_event_id;
    RETURN;
  END IF;

  IF v_dispute.dispute_status<>p_expected_status THEN
    RAISE EXCEPTION 'occupancy dispute status conflict: expected %, found %',
      p_expected_status,v_dispute.dispute_status;
  END IF;
  IF p_effective_tick<v_dispute.opened_effective_tick
     OR p_recorded_tick<v_dispute.opened_recorded_tick THEN
    RAISE EXCEPTION 'dispute resolution ticks cannot precede dispute opening';
  END IF;

  v_event_type:='dispute_'||p_resulting_status;
  v_payload:=jsonb_build_object('resolution_note',p_resolution_note,
    'prior_status',p_expected_status,'resulting_status',p_resulting_status);
  INSERT INTO sw_property.occupancy_dispute_event(
    dispute_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,
    idempotency_key,evidence_class,event_payload
  ) VALUES (
    p_dispute_id,v_event_type,p_effective_tick,p_recorded_tick,
    p_actor_ref,p_source_ref,p_idempotency_key,p_evidence_class,v_payload
  ) RETURNING dispute_event_id INTO v_event_id;

  UPDATE sw_property.occupancy_dispute
  SET dispute_status=p_resulting_status,
      resolved_effective_tick=p_effective_tick,
      resolved_recorded_tick=p_recorded_tick,
      resolution_outcome=p_resulting_status
  WHERE dispute_id=p_dispute_id;

  -- Resolution records the outcome only. It does not vacate the occupant,
  -- terminate the agreement, revoke a right or transfer title.
  RETURN QUERY SELECT p_dispute_id,p_resulting_status,v_event_id;
END
$bp04$;

REVOKE ALL ON sw_property.occupancy_dispute FROM PUBLIC;
REVOKE ALL ON sw_property.occupancy_dispute_event FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.record_occupancy_dispute(
  text,text,text,text,text,text,text,text,bigint,bigint,text,text,text,text,text,text,text
) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.transition_occupancy_dispute(
  text,text,text,bigint,bigint,text,text,text,text,text
) FROM PUBLIC;
COMMIT;
