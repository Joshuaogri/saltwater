-- BP04-24 explicit consent request, decision, revocation and subletting enforcement.
-- Consent is a separate time-bounded NPC decision; revocation never silently
-- ends an existing occupancy relationship or removes the physical occupant.
BEGIN;

ALTER TABLE sw_property.contractual_rights_index
  ADD COLUMN consent_requirement text NOT NULL DEFAULT 'not_required'
    CHECK (consent_requirement IN ('not_required','required','prohibited','unknown')),
  ADD COLUMN consent_authority_organisation_id text
    REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT contractual_rights_consent_authority_ck CHECK (
    consent_requirement<>'required' OR consent_authority_organisation_id IS NOT NULL
  );

CREATE TABLE sw_property.contractual_right_consent (
  consent_id text PRIMARY KEY,
  property_right_id text NOT NULL REFERENCES sw_property.contractual_rights_index(property_right_id)
    DEFERRABLE INITIALLY DEFERRED,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  unit_id text REFERENCES sw_property.unit_space(unit_id)
    DEFERRABLE INITIALLY DEFERRED,
  source_agreement_id text NOT NULL REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  consent_type text NOT NULL CHECK (consent_type IN (
    'subletting','assignment','alteration','works','other'
  )),
  requester_business_id text NOT NULL REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  authorised_business_id text REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  decision_authority_organisation_id text NOT NULL
    REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  consent_status text NOT NULL DEFAULT 'pending'
    CHECK (consent_status IN ('pending','granted','refused','revoked','expired','withdrawn')),
  requested_effective_tick bigint NOT NULL CHECK (requested_effective_tick>=0),
  requested_recorded_tick bigint NOT NULL CHECK (requested_recorded_tick>=0),
  valid_from_tick bigint,
  valid_to_tick bigint,
  decision_effective_tick bigint,
  decision_recorded_tick bigint,
  decision_note text,
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL UNIQUE
    CHECK (idempotency_key ~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'),
  evidence_class text NOT NULL CHECK (evidence_class IN (
    'source_documented','generated_fictional_canon','gameplay_action'
  )),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (authorised_business_id IS NULL OR authorised_business_id<>requester_business_id),
  CHECK (valid_to_tick IS NULL OR (valid_from_tick IS NOT NULL AND valid_to_tick>valid_from_tick)),
  CHECK (
    (consent_status='pending' AND valid_from_tick IS NULL AND valid_to_tick IS NULL
      AND decision_effective_tick IS NULL AND decision_recorded_tick IS NULL)
    OR
    (consent_status='granted' AND valid_from_tick IS NOT NULL AND valid_to_tick IS NULL
      AND decision_effective_tick IS NOT NULL AND decision_recorded_tick IS NOT NULL)
    OR
    (consent_status IN ('refused','withdrawn') AND valid_from_tick IS NULL
      AND valid_to_tick IS NULL AND decision_effective_tick IS NOT NULL
      AND decision_recorded_tick IS NOT NULL)
    OR
    (consent_status IN ('revoked','expired') AND valid_from_tick IS NOT NULL
      AND valid_to_tick IS NOT NULL AND decision_effective_tick=valid_to_tick
      AND decision_recorded_tick IS NOT NULL)
  )
);
CREATE UNIQUE INDEX contractual_right_consent_one_open_request_uq
  ON sw_property.contractual_right_consent(
    property_right_id,consent_type,COALESCE(authorised_business_id,'')
  ) WHERE consent_status IN ('pending','granted');
CREATE INDEX contractual_right_consent_current_lookup_idx
  ON sw_property.contractual_right_consent(
    property_right_id,consent_type,consent_status,valid_from_tick,valid_to_tick
  );

CREATE TABLE sw_property.contractual_right_consent_event (
  consent_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  consent_id text NOT NULL REFERENCES sw_property.contractual_right_consent(consent_id)
    DEFERRABLE INITIALLY DEFERRED,
  event_type text NOT NULL CHECK (event_type IN (
    'consent_requested','consent_granted','consent_refused',
    'consent_revoked','consent_expired','consent_withdrawn'
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
  UNIQUE(consent_id,idempotency_key)
);
CREATE INDEX contractual_right_consent_event_history_idx
  ON sw_property.contractual_right_consent_event(consent_id,effective_tick,consent_event_id);

CREATE FUNCTION sw_property.reject_contractual_right_consent_event_mutation()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  RAISE EXCEPTION 'contractual right consent event history is append-only';
END
$bp04$;
CREATE TRIGGER contractual_right_consent_event_immutable
BEFORE UPDATE OR DELETE ON sw_property.contractual_right_consent_event
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_contractual_right_consent_event_mutation();

CREATE FUNCTION sw_property.guard_contractual_right_consent_transition()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  IF TG_OP='DELETE' THEN
    RAISE EXCEPTION 'contractual right consent records cannot be deleted';
  END IF;
  IF ROW(NEW.consent_id,NEW.property_right_id,NEW.property_id,NEW.unit_id,
       NEW.source_agreement_id,NEW.consent_type,NEW.requester_business_id,
       NEW.authorised_business_id,NEW.decision_authority_organisation_id,
       NEW.requested_effective_tick,NEW.requested_recorded_tick,
       NEW.actor_ref,NEW.source_ref,NEW.idempotency_key,NEW.evidence_class,NEW.created_at)
     IS DISTINCT FROM
     ROW(OLD.consent_id,OLD.property_right_id,OLD.property_id,OLD.unit_id,
       OLD.source_agreement_id,OLD.consent_type,OLD.requester_business_id,
       OLD.authorised_business_id,OLD.decision_authority_organisation_id,
       OLD.requested_effective_tick,OLD.requested_recorded_tick,
       OLD.actor_ref,OLD.source_ref,OLD.idempotency_key,OLD.evidence_class,OLD.created_at)
     OR NOT (
       (OLD.consent_status='pending' AND NEW.consent_status IN ('granted','refused','withdrawn'))
       OR (OLD.consent_status='granted' AND NEW.consent_status IN ('revoked','expired'))
     )
     OR NEW.decision_effective_tick IS NULL
     OR NEW.decision_recorded_tick IS NULL
     OR NEW.decision_effective_tick<OLD.requested_effective_tick
     OR NEW.decision_recorded_tick<OLD.requested_recorded_tick
     OR NEW.decision_note IS NULL
     OR length(trim(NEW.decision_note)) NOT BETWEEN 1 AND 2000 THEN
    RAISE EXCEPTION 'contractual right consent permits only a controlled, append-backed decision transition';
  END IF;
  RETURN NEW;
END
$bp04$;
CREATE TRIGGER contractual_right_consent_transition_guard
BEFORE UPDATE OR DELETE ON sw_property.contractual_right_consent
FOR EACH ROW EXECUTE FUNCTION sw_property.guard_contractual_right_consent_transition();

CREATE FUNCTION sw_property.request_contractual_right_consent(
  p_consent_id text,
  p_property_right_id text,
  p_consent_type text,
  p_requester_business_id text,
  p_authorised_business_id text,
  p_decision_authority_organisation_id text,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text,
  p_evidence_class text
) RETURNS TABLE(consent_id text,consent_status text)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_right sw_property.contractual_rights_index%ROWTYPE;
  v_prior sw_property.contractual_right_consent%ROWTYPE;
BEGIN
  IF p_consent_id IS NULL OR length(trim(p_consent_id)) NOT BETWEEN 1 AND 128
     OR p_property_right_id IS NULL
     OR p_consent_type NOT IN ('subletting','assignment','alteration','works','other')
     OR p_requester_business_id IS NULL
     OR p_decision_authority_organisation_id IS NULL
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_evidence_class NOT IN ('source_documented','generated_fictional_canon','gameplay_action') THEN
    RAISE EXCEPTION 'invalid contractual right consent request';
  END IF;

  SELECT r.* INTO v_right FROM sw_property.contractual_rights_index AS r
  WHERE r.property_right_id=p_property_right_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'contractual right not found'; END IF;
  IF v_right.unit_id IS NULL THEN RAISE EXCEPTION 'consent request requires a unit-scoped contractual right'; END IF;

  PERFORM 1 FROM sw_property.unit_space AS u
  WHERE u.unit_id=v_right.unit_id AND u.property_id=v_right.property_id
  FOR UPDATE;
  SELECT r.* INTO v_right FROM sw_property.contractual_rights_index AS r
  WHERE r.property_right_id=p_property_right_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'contractual right not found'; END IF;

  SELECT c.* INTO v_prior FROM sw_property.contractual_right_consent AS c
  WHERE c.idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.consent_id<>p_consent_id OR v_prior.property_right_id<>p_property_right_id
       OR v_prior.consent_type<>p_consent_type
       OR v_prior.requester_business_id<>p_requester_business_id
       OR v_prior.authorised_business_id IS DISTINCT FROM p_authorised_business_id
       OR v_prior.decision_authority_organisation_id<>p_decision_authority_organisation_id
       OR v_prior.requested_effective_tick<>p_effective_tick
       OR v_prior.requested_recorded_tick<>p_recorded_tick
       OR v_prior.actor_ref<>p_actor_ref OR v_prior.source_ref<>p_source_ref
       OR v_prior.evidence_class<>p_evidence_class THEN
      RAISE EXCEPTION 'contractual right consent idempotency key conflicts with prior request';
    END IF;
    RETURN QUERY SELECT v_prior.consent_id,v_prior.consent_status;
    RETURN;
  END IF;

  IF v_right.right_status<>'current'
     OR v_right.consent_requirement<>'required'
     OR v_right.consent_authority_organisation_id IS DISTINCT FROM p_decision_authority_organisation_id
     OR v_right.source_agreement_id IS NULL
     OR v_right.holder_business_id IS DISTINCT FROM p_requester_business_id
     OR (p_consent_type='subletting' AND v_right.right_type<>'subletting') THEN
    RAISE EXCEPTION 'consent request must match a current consent-required right, its holder and named decision authority';
  END IF;

  INSERT INTO sw_property.contractual_right_consent(
    consent_id,property_right_id,property_id,unit_id,source_agreement_id,
    consent_type,requester_business_id,authorised_business_id,
    decision_authority_organisation_id,consent_status,requested_effective_tick,
    requested_recorded_tick,actor_ref,source_ref,idempotency_key,evidence_class
  ) VALUES (
    p_consent_id,p_property_right_id,v_right.property_id,v_right.unit_id,
    v_right.source_agreement_id,p_consent_type,p_requester_business_id,
    p_authorised_business_id,p_decision_authority_organisation_id,'pending',
    p_effective_tick,p_recorded_tick,p_actor_ref,p_source_ref,p_idempotency_key,p_evidence_class
  );

  INSERT INTO sw_property.contractual_right_consent_event(
    consent_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,
    idempotency_key,evidence_class,event_payload
  ) VALUES (
    p_consent_id,'consent_requested',p_effective_tick,p_recorded_tick,
    p_actor_ref,p_source_ref,p_idempotency_key,p_evidence_class,
    jsonb_build_object('property_right_id',p_property_right_id,
      'consent_type',p_consent_type,'requester_business_id',p_requester_business_id,
      'authorised_business_id',p_authorised_business_id,
      'decision_authority_organisation_id',p_decision_authority_organisation_id)
  );

  RETURN QUERY SELECT p_consent_id,'pending'::text;
END
$bp04$;

CREATE FUNCTION sw_property.decide_contractual_right_consent(
  p_consent_id text,
  p_expected_status text,
  p_resulting_status text,
  p_decision_authority_organisation_id text,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text,
  p_evidence_class text,
  p_decision_note text
) RETURNS TABLE(consent_id text,consent_status text,consent_event_id uuid)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_consent sw_property.contractual_right_consent%ROWTYPE;
  v_prior sw_property.contractual_right_consent_event%ROWTYPE;
  v_event_id uuid;
  v_event_type text;
  v_payload jsonb;
BEGIN
  IF p_consent_id IS NULL
     OR p_decision_authority_organisation_id IS NULL
     OR p_expected_status NOT IN ('pending','granted')
     OR p_resulting_status NOT IN ('granted','refused','withdrawn','revoked','expired')
     OR NOT (
       (p_expected_status='pending' AND p_resulting_status IN ('granted','refused','withdrawn'))
       OR (p_expected_status='granted' AND p_resulting_status IN ('revoked','expired'))
     )
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_evidence_class NOT IN ('source_documented','generated_fictional_canon','gameplay_action')
     OR p_decision_note IS NULL OR length(trim(p_decision_note)) NOT BETWEEN 1 AND 2000 THEN
    RAISE EXCEPTION 'invalid contractual right consent decision';
  END IF;

  SELECT c.* INTO v_consent FROM sw_property.contractual_right_consent AS c
  WHERE c.consent_id=p_consent_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'contractual right consent request not found'; END IF;

  PERFORM 1 FROM sw_property.unit_space AS u
  WHERE u.unit_id=v_consent.unit_id AND u.property_id=v_consent.property_id
  FOR UPDATE;
  SELECT c.* INTO v_consent FROM sw_property.contractual_right_consent AS c
  WHERE c.consent_id=p_consent_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'contractual right consent request not found'; END IF;

  SELECT e.* INTO v_prior FROM sw_property.contractual_right_consent_event AS e
  WHERE e.consent_id=p_consent_id AND e.idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.event_type<>'consent_'||p_resulting_status
       OR v_prior.effective_tick<>p_effective_tick
       OR v_prior.recorded_tick<>p_recorded_tick
       OR v_prior.actor_ref<>p_actor_ref OR v_prior.source_ref<>p_source_ref
       OR v_prior.evidence_class<>p_evidence_class
       OR v_prior.event_payload->>'decision_note' IS DISTINCT FROM p_decision_note
       OR v_prior.event_payload->>'decision_authority_organisation_id' IS DISTINCT FROM p_decision_authority_organisation_id THEN
      RAISE EXCEPTION 'contractual right consent decision idempotency key conflicts with prior event';
    END IF;
    RETURN QUERY SELECT p_consent_id,p_resulting_status,v_prior.consent_event_id;
    RETURN;
  END IF;

  IF v_consent.consent_status<>p_expected_status THEN
    RAISE EXCEPTION 'contractual right consent status conflict: expected %, found %',
      p_expected_status,v_consent.consent_status;
  END IF;
  IF v_consent.decision_authority_organisation_id<>p_decision_authority_organisation_id THEN
    RAISE EXCEPTION 'consent decision must be made by the explicitly named authority organisation';
  END IF;
  IF p_effective_tick<v_consent.requested_effective_tick
     OR p_recorded_tick<v_consent.requested_recorded_tick THEN
    RAISE EXCEPTION 'consent decision ticks cannot precede the request';
  END IF;
  IF p_expected_status='granted' AND (p_effective_tick<=v_consent.valid_from_tick
       OR p_recorded_tick<v_consent.decision_recorded_tick) THEN
    RAISE EXCEPTION 'consent revocation/expiry tick must follow its effective grant tick';
  END IF;

  v_event_type:='consent_'||p_resulting_status;
  v_payload:=jsonb_build_object('decision_note',p_decision_note,
    'decision_authority_organisation_id',p_decision_authority_organisation_id,
    'prior_status',p_expected_status,'resulting_status',p_resulting_status);
  INSERT INTO sw_property.contractual_right_consent_event(
    consent_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,
    idempotency_key,evidence_class,event_payload
  ) VALUES (
    p_consent_id,v_event_type,p_effective_tick,p_recorded_tick,
    p_actor_ref,p_source_ref,p_idempotency_key,p_evidence_class,v_payload
  ) RETURNING contractual_right_consent_event.consent_event_id INTO v_event_id;

  UPDATE sw_property.contractual_right_consent AS c
  SET consent_status=p_resulting_status,
      valid_from_tick=CASE WHEN p_resulting_status='granted' THEN p_effective_tick ELSE c.valid_from_tick END,
      valid_to_tick=CASE WHEN p_resulting_status IN ('revoked','expired') THEN p_effective_tick ELSE NULL END,
      decision_effective_tick=p_effective_tick,
      decision_recorded_tick=p_recorded_tick,
      decision_note=p_decision_note
  WHERE c.consent_id=p_consent_id;

  RETURN QUERY SELECT p_consent_id,p_resulting_status,v_event_id;
END
$bp04$;

CREATE FUNCTION sw_property.enforce_subletting_consent()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
DECLARE
  v_right sw_property.contractual_rights_index%ROWTYPE;
BEGIN
  SELECT r.* INTO v_right
  FROM sw_property.contractual_rights_index AS r
  WHERE r.property_right_id=NEW.subletting_right_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'subletting right not found for consent enforcement'; END IF;

  IF v_right.consent_requirement='prohibited' THEN
    RAISE EXCEPTION 'subletting is prohibited by the contractual right';
  ELSIF v_right.consent_requirement='unknown' THEN
    RAISE EXCEPTION 'subletting consent requirement is unknown; fail closed';
  ELSIF v_right.consent_requirement='required' THEN
    IF v_right.consent_authority_organisation_id IS NULL
       OR NOT EXISTS (
         SELECT 1
         FROM sw_property.contractual_right_consent AS c
         WHERE c.property_right_id=NEW.subletting_right_id
           AND c.property_id=v_right.property_id
           AND c.unit_id=v_right.unit_id
           AND c.source_agreement_id=v_right.source_agreement_id
           AND c.consent_type='subletting'
           AND c.requester_business_id=NEW.granting_business_id
           AND c.decision_authority_organisation_id=v_right.consent_authority_organisation_id
           AND c.consent_status='granted'
           AND c.valid_from_tick<=NEW.effective_from_tick
           AND (c.valid_to_tick IS NULL OR c.valid_to_tick>NEW.effective_from_tick)
           AND (c.authorised_business_id IS NULL
                OR c.authorised_business_id=NEW.subtenant_business_id)
       ) THEN
      RAISE EXCEPTION 'explicit current consent for this subtenant from the named decision authority is required';
    END IF;
  END IF;
  RETURN NEW;
END
$bp04$;

CREATE TRIGGER occupancy_relationship_consent_guard
BEFORE INSERT ON sw_property.occupancy_relationship
FOR EACH ROW EXECUTE FUNCTION sw_property.enforce_subletting_consent();

REVOKE ALL ON sw_property.contractual_right_consent FROM PUBLIC;
REVOKE ALL ON sw_property.contractual_right_consent_event FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.reject_contractual_right_consent_event_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.guard_contractual_right_consent_transition() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.request_contractual_right_consent(
  text,text,text,text,text,text,bigint,bigint,text,text,text,text
) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.decide_contractual_right_consent(
  text,text,text,text,bigint,bigint,text,text,text,text,text
) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.enforce_subletting_consent() FROM PUBLIC;
COMMIT;
