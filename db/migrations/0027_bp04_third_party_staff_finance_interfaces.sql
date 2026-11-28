-- BP04-27: NPC third-party occupancy, BP03/BP33 staff references and BP34 financial boundaries.
BEGIN;

ALTER TABLE sw_property.occupancy
  ADD COLUMN occupant_organisation_id text
    REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
  ADD COLUMN occupant_person_id integer;
ALTER TABLE sw_property.occupancy
  ADD CONSTRAINT occupancy_party_identity_count_ck
  CHECK (num_nonnulls(occupant_business_id,occupant_organisation_id,occupant_person_id)<=1);

CREATE FUNCTION sw_property.validate_bp03_person_reference()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
DECLARE v_exists boolean;
BEGIN
  IF NEW.occupant_person_id IS NOT NULL THEN
    IF to_regclass('sw_people.person') IS NULL THEN
      RAISE EXCEPTION 'BP03 person register is not installed; BP04 cannot create or substitute a person identity';
    END IF;
    EXECUTE 'SELECT EXISTS (SELECT 1 FROM sw_people.person WHERE person_id=$1)'
      INTO v_exists USING NEW.occupant_person_id;
    IF NOT v_exists THEN RAISE EXCEPTION 'occupancy person reference does not resolve to BP03'; END IF;
  END IF;
  IF NEW.occupant_type IN ('person','resident_person','employee_person')
     AND NEW.occupant_person_id IS NULL THEN
    RAISE EXCEPTION 'person occupancy must reference the canonical BP03 person_id';
  ELSIF NEW.occupant_type IN ('organisation','institution','public_body')
     AND NEW.occupant_organisation_id IS NULL THEN
    RAISE EXCEPTION 'organisation occupancy must reference the canonical BP04 organisation_id';
  ELSIF NEW.occupant_type IN ('business','business_subtenant')
     AND NEW.occupant_business_id IS NULL THEN
    RAISE EXCEPTION 'business occupancy must reference the canonical BP04 business_id';
  END IF;
  RETURN NEW;
END
$bp04$;
CREATE TRIGGER occupancy_bp03_person_reference_guard
BEFORE INSERT OR UPDATE OF occupant_business_id,occupant_organisation_id,occupant_person_id,occupant_type
ON sw_property.occupancy
FOR EACH ROW EXECUTE FUNCTION sw_property.validate_bp03_person_reference();

CREATE TABLE sw_property.third_party_occupancy_relationship (
  relationship_id text PRIMARY KEY,
  occupancy_id text NOT NULL REFERENCES sw_property.occupancy(occupancy_id)
    DEFERRABLE INITIALLY DEFERRED,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  unit_id text NOT NULL REFERENCES sw_property.unit_space(unit_id)
    DEFERRABLE INITIALLY DEFERRED,
  underlying_agreement_id text REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  property_right_id text REFERENCES sw_property.contractual_rights_index(property_right_id)
    DEFERRABLE INITIALLY DEFERRED,
  use_type text NOT NULL CHECK (use_type IN (
    'licence','concession','desk_share','room_share','storage','contractor_access',
    'service_provider','temporary_use','event_vendor','residential_guest','other'
  )),
  granting_business_id text REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  granting_organisation_id text REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  granting_person_id integer,
  receiving_business_id text REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  receiving_organisation_id text REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  receiving_person_id integer,
  permitted_purpose text NOT NULL CHECK (length(trim(permitted_purpose)) BETWEEN 1 AND 500),
  access_scope text NOT NULL CHECK (length(trim(access_scope)) BETWEEN 1 AND 500),
  permission_status text NOT NULL CHECK (permission_status IN (
    'not_required','granted','pending','refused','revoked','unknown','disputed','unauthorised'
  )),
  relationship_status text NOT NULL CHECK (relationship_status IN (
    'active','pending','ended','disputed','unauthorised'
  )),
  decision_authority_organisation_id text REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  consent_decision_ref text,
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  effective_to_tick bigint,
  recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  evidence_class text NOT NULL CHECK (evidence_class IN (
    'source_documented','generated_fictional_canon','gameplay_action'
  )),
  idempotency_key text NOT NULL UNIQUE
    CHECK (idempotency_key ~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'),
  end_idempotency_key text UNIQUE,
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (num_nonnulls(granting_business_id,granting_organisation_id,granting_person_id)=1),
  CHECK (num_nonnulls(receiving_business_id,receiving_organisation_id,receiving_person_id)=1),
  CHECK (effective_to_tick IS NULL OR effective_to_tick>effective_from_tick),
  CHECK ((relationship_status IN ('active','pending','disputed','unauthorised'))=(effective_to_tick IS NULL)),
  CHECK ((relationship_status='ended')=(end_idempotency_key IS NOT NULL)),
  CHECK (
    (relationship_status='active' AND permission_status IN ('not_required','granted'))
    OR (relationship_status='pending' AND permission_status='pending')
    OR (relationship_status='disputed' AND permission_status='disputed')
    OR (relationship_status='unauthorised' AND permission_status IN ('refused','revoked','unknown','unauthorised'))
    OR (relationship_status='ended' AND permission_status IN ('not_required','granted','revoked','refused'))
  ),
  CHECK (permission_status<>'granted' OR
    (decision_authority_organisation_id IS NOT NULL
     AND consent_decision_ref IS NOT NULL AND length(trim(consent_decision_ref)) BETWEEN 1 AND 200))
);
CREATE INDEX third_party_occupancy_unit_idx
  ON sw_property.third_party_occupancy_relationship(unit_id,relationship_status);
CREATE INDEX third_party_occupancy_occupancy_idx
  ON sw_property.third_party_occupancy_relationship(occupancy_id,relationship_status);

CREATE FUNCTION sw_property.guard_third_party_occupancy_relationship()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
DECLARE
  v_occupancy sw_property.occupancy%ROWTYPE;
  v_agreement sw_property.occupancy_agreement%ROWTYPE;
  v_right sw_property.contractual_rights_index%ROWTYPE;
  v_exists boolean;
BEGIN
  IF TG_OP='DELETE' THEN
    RAISE EXCEPTION 'third-party occupancy history cannot be deleted';
  END IF;
  IF TG_OP='UPDATE' THEN
    IF ROW(NEW.relationship_id,NEW.occupancy_id,NEW.property_id,NEW.unit_id,
       NEW.underlying_agreement_id,NEW.property_right_id,NEW.use_type,
       NEW.granting_business_id,NEW.granting_organisation_id,NEW.granting_person_id,
       NEW.receiving_business_id,NEW.receiving_organisation_id,NEW.receiving_person_id,
       NEW.permitted_purpose,NEW.access_scope,NEW.permission_status,NEW.decision_authority_organisation_id,
       NEW.consent_decision_ref,NEW.effective_from_tick,NEW.recorded_tick,NEW.actor_ref,
       NEW.source_ref,NEW.evidence_class,NEW.idempotency_key,NEW.created_at)
       IS DISTINCT FROM
       ROW(OLD.relationship_id,OLD.occupancy_id,OLD.property_id,OLD.unit_id,
       OLD.underlying_agreement_id,OLD.property_right_id,OLD.use_type,
       OLD.granting_business_id,OLD.granting_organisation_id,OLD.granting_person_id,
       OLD.receiving_business_id,OLD.receiving_organisation_id,OLD.receiving_person_id,
       OLD.permitted_purpose,OLD.access_scope,OLD.permission_status,OLD.decision_authority_organisation_id,
       OLD.consent_decision_ref,OLD.effective_from_tick,OLD.recorded_tick,OLD.actor_ref,
       OLD.source_ref,OLD.evidence_class,OLD.idempotency_key,OLD.created_at)
       OR OLD.relationship_status NOT IN ('active','pending','disputed','unauthorised')
       OR NEW.relationship_status<>'ended'
       OR NEW.effective_to_tick IS NULL
       OR NEW.end_idempotency_key IS NULL
       OR NEW.effective_to_tick<=OLD.effective_from_tick THEN
      RAISE EXCEPTION 'third-party occupancy permits only a controlled end transition';
    END IF;
    RETURN NEW;
  END IF;

  PERFORM 1 FROM sw_property.unit_space AS u
  WHERE u.unit_id=NEW.unit_id AND u.property_id=NEW.property_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'third-party occupancy unit/property reference is invalid'; END IF;

  SELECT o.* INTO v_occupancy FROM sw_property.occupancy AS o
  WHERE o.occupancy_id=NEW.occupancy_id FOR UPDATE;
  IF NOT FOUND OR v_occupancy.property_id<>NEW.property_id OR v_occupancy.unit_id<>NEW.unit_id THEN
    RAISE EXCEPTION 'third-party relationship must match its physical occupancy record';
  END IF;
  IF v_occupancy.occupant_business_id IS DISTINCT FROM NEW.receiving_business_id
     OR v_occupancy.occupant_organisation_id IS DISTINCT FROM NEW.receiving_organisation_id
     OR v_occupancy.occupant_person_id IS DISTINCT FROM NEW.receiving_person_id THEN
    RAISE EXCEPTION 'third-party receiving party must match the canonical occupancy party';
  END IF;

  IF NEW.receiving_person_id IS NOT NULL OR NEW.granting_person_id IS NOT NULL THEN
    IF to_regclass('sw_people.person') IS NULL THEN
      RAISE EXCEPTION 'BP03 person register is not installed; third-party person references fail closed';
    END IF;
    IF NEW.receiving_person_id IS NOT NULL THEN
      EXECUTE 'SELECT EXISTS (SELECT 1 FROM sw_people.person WHERE person_id=$1)'
        INTO v_exists USING NEW.receiving_person_id;
      IF NOT v_exists THEN RAISE EXCEPTION 'receiving person does not resolve to BP03'; END IF;
    END IF;
    IF NEW.granting_person_id IS NOT NULL THEN
      EXECUTE 'SELECT EXISTS (SELECT 1 FROM sw_people.person WHERE person_id=$1)'
        INTO v_exists USING NEW.granting_person_id;
      IF NOT v_exists THEN RAISE EXCEPTION 'granting person does not resolve to BP03'; END IF;
    END IF;
  END IF;

  IF NEW.underlying_agreement_id IS NOT NULL THEN
    SELECT a.* INTO v_agreement FROM sw_property.occupancy_agreement AS a
    WHERE a.agreement_id=NEW.underlying_agreement_id FOR UPDATE;
    IF NOT FOUND OR v_agreement.property_id<>NEW.property_id OR v_agreement.unit_id<>NEW.unit_id THEN
      RAISE EXCEPTION 'third-party relationship does not match its underlying agreement';
    END IF;
    IF NEW.granting_business_id IS NOT NULL
       AND NEW.granting_business_id NOT IN (v_agreement.tenant_business_id,v_agreement.operator_business_id) THEN
      RAISE EXCEPTION 'granting business is not a party to the underlying agreement';
    END IF;
    IF NEW.granting_organisation_id IS NOT NULL
       AND NEW.granting_organisation_id IS DISTINCT FROM v_agreement.landlord_organisation_id THEN
      RAISE EXCEPTION 'granting organisation is not the recorded landlord';
    END IF;
  END IF;

  IF NEW.property_right_id IS NOT NULL THEN
    SELECT r.* INTO v_right FROM sw_property.contractual_rights_index AS r
    WHERE r.property_right_id=NEW.property_right_id FOR UPDATE;
    IF NOT FOUND OR v_right.property_id<>NEW.property_id OR v_right.unit_id<>NEW.unit_id
       OR v_right.right_status<>'current' THEN
      RAISE EXCEPTION 'third-party relationship requires a current right for the same property and unit';
    END IF;
    IF v_right.consent_requirement='prohibited' THEN
      RAISE EXCEPTION 'third-party use is prohibited by the contractual right';
    ELSIF v_right.consent_requirement='unknown' THEN
      RAISE EXCEPTION 'third-party permission is unknown; active use fails closed';
    ELSIF v_right.consent_requirement='required' THEN
      IF NEW.permission_status<>'granted'
         OR NEW.decision_authority_organisation_id IS DISTINCT FROM v_right.consent_authority_organisation_id THEN
        RAISE EXCEPTION 'third-party use requires a grant from the named authority';
      END IF;
    END IF;
    IF v_right.holder_business_id IS NOT NULL
       AND NEW.granting_business_id IS DISTINCT FROM v_right.holder_business_id THEN
      RAISE EXCEPTION 'third-party grantor does not hold the referenced contractual right';
    END IF;
  END IF;
  RETURN NEW;
END
$bp04$;
CREATE TRIGGER third_party_occupancy_guard
BEFORE INSERT OR UPDATE OR DELETE ON sw_property.third_party_occupancy_relationship
FOR EACH ROW EXECUTE FUNCTION sw_property.guard_third_party_occupancy_relationship();

CREATE TABLE sw_property.third_party_occupancy_event (
  event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  relationship_id text NOT NULL REFERENCES sw_property.third_party_occupancy_relationship(relationship_id)
    DEFERRABLE INITIALLY DEFERRED,
  event_type text NOT NULL CHECK (event_type IN ('relationship_recorded','relationship_ended')),
  effective_tick bigint NOT NULL CHECK (effective_tick>=0),
  recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
  actor_ref text NOT NULL,
  source_ref text NOT NULL,
  idempotency_key text NOT NULL,
  event_payload jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(event_payload)='object'),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE(relationship_id,idempotency_key)
);
CREATE FUNCTION sw_property.reject_third_party_occupancy_event_mutation()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN RAISE EXCEPTION 'third-party occupancy event history is append-only'; END
$bp04$;
CREATE TRIGGER third_party_occupancy_event_immutable
BEFORE UPDATE OR DELETE ON sw_property.third_party_occupancy_event
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_third_party_occupancy_event_mutation();

CREATE FUNCTION sw_property.record_third_party_occupancy_event()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  INSERT INTO sw_property.third_party_occupancy_event(
    relationship_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,idempotency_key,event_payload
  ) VALUES (
    NEW.relationship_id,
    CASE WHEN TG_OP='INSERT' THEN 'relationship_recorded' ELSE 'relationship_ended' END,
    CASE WHEN TG_OP='INSERT' THEN NEW.effective_from_tick ELSE NEW.effective_to_tick END,
    NEW.recorded_tick,NEW.actor_ref,NEW.source_ref,
    CASE WHEN TG_OP='INSERT' THEN NEW.idempotency_key ELSE NEW.end_idempotency_key END,
    jsonb_build_object('occupancy_id',NEW.occupancy_id,'use_type',NEW.use_type,
      'relationship_status',NEW.relationship_status,'permission_status',NEW.permission_status)
  );
  RETURN NEW;
END
$bp04$;
CREATE TRIGGER third_party_occupancy_event_writer
AFTER INSERT OR UPDATE OF relationship_status ON sw_property.third_party_occupancy_relationship
FOR EACH ROW EXECUTE FUNCTION sw_property.record_third_party_occupancy_event();

CREATE FUNCTION sw_property.end_third_party_occupancy_relationship(
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
  SELECT r.* INTO v_relationship FROM sw_property.third_party_occupancy_relationship r
  WHERE r.relationship_id=p_relationship_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'third-party occupancy relationship not found'; END IF;
  PERFORM 1 FROM sw_property.unit_space u
  WHERE u.unit_id=v_relationship.unit_id AND u.property_id=v_relationship.property_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'third-party occupancy unit not found'; END IF;
  SELECT r.* INTO v_relationship FROM sw_property.third_party_occupancy_relationship r
  WHERE r.relationship_id=p_relationship_id FOR UPDATE;
  IF v_relationship.relationship_status='ended' THEN
    IF v_relationship.end_idempotency_key<>p_idempotency_key
       OR v_relationship.effective_to_tick<>p_effective_tick THEN
      RAISE EXCEPTION 'third-party occupancy end conflicts with prior terminal event';
    END IF;
    RETURN QUERY SELECT v_relationship.relationship_id,'ended'::text;
    RETURN;
  END IF;
  IF p_effective_tick<=v_relationship.effective_from_tick THEN
    RAISE EXCEPTION 'third-party occupancy end tick must follow its start';
  END IF;
  UPDATE sw_property.third_party_occupancy_relationship
  SET relationship_status='ended',effective_to_tick=p_effective_tick,
      end_idempotency_key=p_idempotency_key,actor_ref=p_actor_ref,source_ref=p_source_ref,
      recorded_tick=p_recorded_tick
  WHERE relationship_id=p_relationship_id;
  RETURN QUERY SELECT p_relationship_id,'ended'::text;
END
$bp04$;

CREATE TABLE sw_property.staff_role_link (
  staff_role_link_id text PRIMARY KEY,
  person_id integer NOT NULL,
  employer_business_id text REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  employer_organisation_id text REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  establishment_id text REFERENCES sw_property.establishment(establishment_id)
    DEFERRABLE INITIALLY DEFERRED,
  bp33_employment_ref text NOT NULL UNIQUE CHECK (length(trim(bp33_employment_ref)) BETWEEN 1 AND 200),
  role_title text NOT NULL CHECK (length(trim(role_title)) BETWEEN 1 AND 200),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  effective_to_tick bigint,
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  evidence_class text NOT NULL CHECK (evidence_class IN (
    'source_documented','generated_fictional_canon','gameplay_action'
  )),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (num_nonnulls(employer_business_id,employer_organisation_id)=1),
  CHECK (effective_to_tick IS NULL OR effective_to_tick>effective_from_tick)
);
CREATE INDEX staff_role_link_person_idx ON sw_property.staff_role_link(person_id,effective_from_tick);
CREATE FUNCTION sw_property.validate_staff_role_bp03_person()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
DECLARE v_exists boolean;
BEGIN
  IF to_regclass('sw_people.person') IS NULL THEN
    RAISE EXCEPTION 'BP03 person register is not installed; BP04 staff links cannot create substitute people';
  END IF;
  EXECUTE 'SELECT EXISTS (SELECT 1 FROM sw_people.person WHERE person_id=$1)'
    INTO v_exists USING NEW.person_id;
  IF NOT v_exists THEN RAISE EXCEPTION 'staff role person_id does not resolve to BP03'; END IF;
  RETURN NEW;
END
$bp04$;
CREATE TRIGGER staff_role_bp03_person_guard
BEFORE INSERT OR UPDATE OF person_id ON sw_property.staff_role_link
FOR EACH ROW EXECUTE FUNCTION sw_property.validate_staff_role_bp03_person();

CREATE TABLE sw_property.occupancy_financial_reference (
  reference_id text PRIMARY KEY,
  agreement_id text NOT NULL REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  bp34_financial_agreement_ref text,
  bp34_rent_schedule_ref text,
  bp34_deposit_reference text,
  bp34_receivable_reference text,
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  effective_to_tick bigint,
  recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL UNIQUE,
  supersedes_reference_id text REFERENCES sw_property.occupancy_financial_reference(reference_id)
    DEFERRABLE INITIALLY DEFERRED,
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (num_nonnulls(bp34_financial_agreement_ref,bp34_rent_schedule_ref,
        bp34_deposit_reference,bp34_receivable_reference)>0),
  CHECK (effective_to_tick IS NULL OR effective_to_tick>effective_from_tick)
);
CREATE INDEX occupancy_financial_reference_agreement_idx
  ON sw_property.occupancy_financial_reference(agreement_id,effective_from_tick);
CREATE FUNCTION sw_property.reject_occupancy_financial_reference_mutation()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN RAISE EXCEPTION 'BP34 financial references are append-only links; financial values and postings belong to BP34'; END
$bp04$;
CREATE TRIGGER occupancy_financial_reference_immutable
BEFORE UPDATE OR DELETE ON sw_property.occupancy_financial_reference
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_occupancy_financial_reference_mutation();

REVOKE ALL ON FUNCTION sw_property.validate_bp03_person_reference() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.guard_third_party_occupancy_relationship() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.reject_third_party_occupancy_event_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.record_third_party_occupancy_event() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.end_third_party_occupancy_relationship(text,bigint,bigint,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.validate_staff_role_bp03_person() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.reject_occupancy_financial_reference_mutation() FROM PUBLIC;
COMMIT;
