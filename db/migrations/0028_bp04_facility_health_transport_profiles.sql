-- BP04-28: complete third-party end provenance and add facility/service interfaces.
BEGIN;

ALTER TABLE sw_property.third_party_occupancy_relationship
  ADD COLUMN end_actor_ref text,
  ADD COLUMN end_source_ref text,
  ADD COLUMN end_recorded_tick bigint;

CREATE OR REPLACE FUNCTION sw_property.guard_third_party_occupancy_relationship()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
DECLARE
  v_occupancy sw_property.occupancy%ROWTYPE;
  v_agreement sw_property.occupancy_agreement%ROWTYPE;
  v_right sw_property.contractual_rights_index%ROWTYPE;
  v_exists boolean;
BEGIN
  IF TG_OP='DELETE' THEN RAISE EXCEPTION 'third-party occupancy history cannot be deleted'; END IF;
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
       OR NEW.effective_to_tick<=OLD.effective_from_tick
       OR OLD.end_actor_ref IS NOT NULL OR OLD.end_source_ref IS NOT NULL
       OR OLD.end_recorded_tick IS NOT NULL
       OR NEW.end_actor_ref IS NULL OR length(trim(NEW.end_actor_ref)) NOT BETWEEN 1 AND 200
       OR NEW.end_source_ref IS NULL OR length(trim(NEW.end_source_ref)) NOT BETWEEN 1 AND 200
       OR NEW.end_recorded_tick IS NULL OR NEW.end_recorded_tick<OLD.recorded_tick THEN
      RAISE EXCEPTION 'third-party occupancy permits only a controlled, fully attributed end transition';
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

CREATE OR REPLACE FUNCTION sw_property.record_third_party_occupancy_event()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  INSERT INTO sw_property.third_party_occupancy_event(
    relationship_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,idempotency_key,event_payload
  ) VALUES (
    NEW.relationship_id,
    CASE WHEN TG_OP='INSERT' THEN 'relationship_recorded' ELSE 'relationship_ended' END,
    CASE WHEN TG_OP='INSERT' THEN NEW.effective_from_tick ELSE NEW.effective_to_tick END,
    CASE WHEN TG_OP='INSERT' THEN NEW.recorded_tick ELSE NEW.end_recorded_tick END,
    CASE WHEN TG_OP='INSERT' THEN NEW.actor_ref ELSE NEW.end_actor_ref END,
    CASE WHEN TG_OP='INSERT' THEN NEW.source_ref ELSE NEW.end_source_ref END,
    CASE WHEN TG_OP='INSERT' THEN NEW.idempotency_key ELSE NEW.end_idempotency_key END,
    jsonb_build_object('occupancy_id',NEW.occupancy_id,'use_type',NEW.use_type,
      'relationship_status',NEW.relationship_status,'permission_status',NEW.permission_status)
  );
  RETURN NEW;
END
$bp04$;

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
  UPDATE sw_property.third_party_occupancy_relationship
  SET relationship_status='ended',effective_to_tick=p_effective_tick,
      end_idempotency_key=p_idempotency_key,end_actor_ref=p_actor_ref,
      end_source_ref=p_source_ref,end_recorded_tick=p_recorded_tick
  WHERE relationship_id=p_relationship_id;
  RETURN QUERY SELECT p_relationship_id,'ended'::text;
END
$bp04$;

CREATE TABLE sw_property.facility (
  facility_id text PRIMARY KEY,
  owner_organisation_id text REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  operator_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  building_id text REFERENCES sw_property.building(building_id)
    DEFERRABLE INITIALLY DEFERRED,
  premises_id text REFERENCES sw_property.premises(premises_id)
    DEFERRABLE INITIALLY DEFERRED,
  facility_type text NOT NULL CHECK (facility_type IN (
    'healthcare','transport_terminal','transport_station','education','shelter',
    'utility','emergency_service','public_office','logistics','cultural','commercial','other'
  )),
  facility_status text NOT NULL CHECK (facility_status IN ('planned','active','temporarily_closed','closed','under_construction')),
  availability_status text NOT NULL CHECK (availability_status IN ('available','limited','unavailable','unknown')),
  capacity_value numeric CHECK (capacity_value IS NULL OR capacity_value>=0),
  capacity_unit text,
  bp37_schedule_ref text,
  source_dataset text NOT NULL,
  CHECK (building_id IS NOT NULL OR premises_id IS NOT NULL OR property_id IS NOT NULL)
);
CREATE INDEX facility_property_idx ON sw_property.facility(property_id);
CREATE INDEX facility_operator_idx ON sw_property.facility(operator_organisation_id);

CREATE TABLE sw_property.facility_service (
  service_id text PRIMARY KEY,
  facility_id text NOT NULL REFERENCES sw_property.facility(facility_id)
    DEFERRABLE INITIALLY DEFERRED,
  service_type text NOT NULL CHECK (service_type IN (
    'emergency_care','outpatient_care','diagnostics','primary_care','public_transport',
    'bus','rail','ferry','taxi','logistics','education','shelter','utility','other'
  )),
  service_status text NOT NULL CHECK (service_status IN ('planned','active','suspended','withdrawn')),
  availability_status text NOT NULL CHECK (availability_status IN ('available','limited','unavailable','unknown')),
  capacity_value numeric CHECK (capacity_value IS NULL OR capacity_value>=0),
  capacity_unit text,
  bp37_schedule_ref text,
  service_area_ref text,
  source_dataset text NOT NULL
);
CREATE INDEX facility_service_facility_idx ON sw_property.facility_service(facility_id);

CREATE TABLE sw_property.healthcare_service_profile (
  service_id text PRIMARY KEY REFERENCES sw_property.facility_service(service_id)
    DEFERRABLE INITIALLY DEFERRED,
  emergency_care_capability text NOT NULL CHECK (emergency_care_capability IN ('none','basic','urgent','full_emergency','specialist')),
  appointment_availability text NOT NULL CHECK (appointment_availability IN ('available','limited','unavailable','unknown')),
  referral_availability text NOT NULL CHECK (referral_availability IN ('available','limited','unavailable','unknown')),
  practitioner_role_profile jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(practitioner_role_profile)='object'),
  public_health_alert_ref text,
  treatment_event_metadata_only boolean NOT NULL DEFAULT true CHECK (treatment_event_metadata_only),
  source_dataset text NOT NULL
);

CREATE TABLE sw_property.transport_service_profile (
  service_id text PRIMARY KEY REFERENCES sw_property.facility_service(service_id)
    DEFERRABLE INITIALLY DEFERRED,
  bp02_route_ref text NOT NULL CHECK (length(trim(bp02_route_ref)) BETWEEN 1 AND 200),
  ordered_stop_refs text[] NOT NULL CHECK (cardinality(ordered_stop_refs)>=2),
  bp37_timetable_ref text NOT NULL CHECK (length(trim(bp37_timetable_ref)) BETWEEN 1 AND 200),
  fleet_profile jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(fleet_profile)='object'),
  accessibility_profile jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(accessibility_profile)='object'),
  service_restrictions text[] NOT NULL DEFAULT ARRAY[]::text[],
  disruption_status text NOT NULL CHECK (disruption_status IN ('normal','delayed','reduced','suspended','cancelled','restored')),
  source_dataset text NOT NULL
);

CREATE TABLE sw_property.facility_dependency (
  dependency_id text PRIMARY KEY,
  facility_id text NOT NULL REFERENCES sw_property.facility(facility_id)
    DEFERRABLE INITIALLY DEFERRED,
  provider_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  dependency_type text NOT NULL CHECK (dependency_type IN (
    'power','water','communications','waste','fuel','food','transport','emergency_support','other'
  )),
  provider_service_ref text,
  dependency_status text NOT NULL CHECK (dependency_status IN ('active','degraded','interrupted','unknown')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  effective_to_tick bigint,
  source_dataset text NOT NULL,
  CHECK (effective_to_tick IS NULL OR effective_to_tick>effective_from_tick)
);
CREATE INDEX facility_dependency_facility_idx ON sw_property.facility_dependency(facility_id);

CREATE TABLE sw_property.facility_service_event (
  event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  service_id text NOT NULL REFERENCES sw_property.facility_service(service_id)
    DEFERRABLE INITIALLY DEFERRED,
  event_type text NOT NULL CHECK (event_type IN (
    'service_activated','service_suspended','service_disrupted','service_restored',
    'service_withdrawn','capacity_changed','availability_changed'
  )),
  effective_tick bigint NOT NULL CHECK (effective_tick>=0),
  recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL CHECK (length(trim(idempotency_key)) BETWEEN 1 AND 128),
  event_payload jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(event_payload)='object'),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE(service_id,idempotency_key)
);
CREATE INDEX facility_service_event_history_idx
  ON sw_property.facility_service_event(service_id,effective_tick,event_id);
CREATE FUNCTION sw_property.reject_facility_service_event_mutation()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN RAISE EXCEPTION 'facility service event history is append-only'; END
$bp04$;
CREATE TRIGGER facility_service_event_immutable
BEFORE UPDATE OR DELETE ON sw_property.facility_service_event
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_facility_service_event_mutation();

REVOKE ALL ON FUNCTION sw_property.reject_facility_service_event_mutation() FROM PUBLIC;
COMMIT;
