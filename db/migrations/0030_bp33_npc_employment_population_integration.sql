-- BP33 minimal NPC employment records with BP03 identity and BP04 employer links.
BEGIN;
CREATE SCHEMA IF NOT EXISTS sw_hr;

CREATE TABLE sw_hr.employment (
  employment_id text PRIMARY KEY,
  person_id integer NOT NULL,
  employer_business_id text REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  employer_organisation_id text REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  establishment_id text REFERENCES sw_property.establishment(establishment_id)
    DEFERRABLE INITIALLY DEFERRED,
  role_title text NOT NULL CHECK (length(trim(role_title)) BETWEEN 1 AND 200),
  employment_status text NOT NULL CHECK (employment_status IN ('future','active','suspended','ended')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  effective_to_tick bigint,
  recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  evidence_class text NOT NULL CHECK (evidence_class IN (
    'source_documented','generated_fictional_canon','gameplay_action'
  )),
  idempotency_key text NOT NULL UNIQUE,
  end_idempotency_key text UNIQUE,
  end_recorded_tick bigint,
  end_actor_ref text,
  end_source_ref text,
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (num_nonnulls(employer_business_id,employer_organisation_id)=1),
  CHECK (effective_to_tick IS NULL OR effective_to_tick>effective_from_tick),
  CHECK ((employment_status='ended')=(effective_to_tick IS NOT NULL)),
  CHECK ((employment_status='ended')=(end_idempotency_key IS NOT NULL))
);
CREATE INDEX employment_person_idx ON sw_hr.employment(person_id,effective_from_tick);
CREATE INDEX employment_employer_business_idx ON sw_hr.employment(employer_business_id,effective_from_tick);
CREATE INDEX employment_employer_org_idx ON sw_hr.employment(employer_organisation_id,effective_from_tick);

CREATE FUNCTION sw_hr.validate_employment_person_and_employer()
RETURNS trigger LANGUAGE plpgsql AS $hr$
DECLARE v_exists boolean; v_business_id text;
BEGIN
  IF to_regclass('sw_people.person') IS NULL THEN
    RAISE EXCEPTION 'BP03 person register is not installed; BP33 cannot create substitute person identities';
  END IF;
  EXECUTE 'SELECT EXISTS (SELECT 1 FROM sw_people.person WHERE person_id=$1)'
    INTO v_exists USING NEW.person_id;
  IF NOT v_exists THEN RAISE EXCEPTION 'BP33 employment person_id does not resolve to BP03'; END IF;
  IF NEW.employer_business_id IS NOT NULL AND NEW.establishment_id IS NOT NULL THEN
    SELECT e.business_id INTO v_business_id FROM sw_property.establishment AS e
    WHERE e.establishment_id=NEW.establishment_id;
    IF NOT FOUND OR v_business_id<>NEW.employer_business_id THEN
      RAISE EXCEPTION 'BP33 establishment must belong to the employing business';
    END IF;
  END IF;
  RETURN NEW;
END
$hr$;
CREATE TRIGGER employment_bp03_person_guard
BEFORE INSERT OR UPDATE OF person_id,employer_business_id,employer_organisation_id,establishment_id
ON sw_hr.employment FOR EACH ROW
EXECUTE FUNCTION sw_hr.validate_employment_person_and_employer();

CREATE TABLE sw_hr.employment_event (
  event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  employment_id text NOT NULL REFERENCES sw_hr.employment(employment_id)
    DEFERRABLE INITIALLY DEFERRED,
  event_type text NOT NULL CHECK (event_type IN ('employment_started','employment_ended')),
  effective_tick bigint NOT NULL CHECK (effective_tick>=0),
  recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
  actor_ref text NOT NULL,
  source_ref text NOT NULL,
  idempotency_key text NOT NULL,
  event_payload jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(event_payload)='object'),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE(employment_id,idempotency_key)
);
CREATE FUNCTION sw_hr.reject_employment_event_mutation()
RETURNS trigger LANGUAGE plpgsql AS $hr$
BEGIN RAISE EXCEPTION 'BP33 employment event history is append-only'; END
$hr$;
CREATE TRIGGER employment_event_immutable
BEFORE UPDATE OR DELETE ON sw_hr.employment_event
FOR EACH ROW EXECUTE FUNCTION sw_hr.reject_employment_event_mutation();

CREATE FUNCTION sw_hr.guard_employment_transition()
RETURNS trigger LANGUAGE plpgsql AS $hr$
BEGIN
  IF TG_OP='DELETE' THEN RAISE EXCEPTION 'BP33 employment history cannot be deleted'; END IF;
  IF ROW(NEW.employment_id,NEW.person_id,NEW.employer_business_id,NEW.employer_organisation_id,
         NEW.establishment_id,NEW.role_title,NEW.effective_from_tick,NEW.recorded_tick,
         NEW.source_ref,NEW.actor_ref,NEW.evidence_class,NEW.idempotency_key,NEW.created_at)
     IS DISTINCT FROM
     ROW(OLD.employment_id,OLD.person_id,OLD.employer_business_id,OLD.employer_organisation_id,
         OLD.establishment_id,OLD.role_title,OLD.effective_from_tick,OLD.recorded_tick,
         OLD.source_ref,OLD.actor_ref,OLD.evidence_class,OLD.idempotency_key,OLD.created_at)
     OR OLD.employment_status='ended' OR NEW.employment_status<>'ended'
     OR NEW.effective_to_tick IS NULL OR NEW.end_idempotency_key IS NULL
     OR NEW.end_recorded_tick IS NULL OR NEW.end_actor_ref IS NULL OR NEW.end_source_ref IS NULL
     OR NEW.effective_to_tick<=OLD.effective_from_tick
     OR NEW.end_recorded_tick<OLD.recorded_tick THEN
    RAISE EXCEPTION 'BP33 employment permits only a controlled end transition';
  END IF;
  RETURN NEW;
END
$hr$;
CREATE TRIGGER employment_transition_guard
BEFORE UPDATE OR DELETE ON sw_hr.employment
FOR EACH ROW EXECUTE FUNCTION sw_hr.guard_employment_transition();

CREATE FUNCTION sw_hr.record_employment_event()
RETURNS trigger LANGUAGE plpgsql AS $hr$
BEGIN
  INSERT INTO sw_hr.employment_event(
    employment_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,idempotency_key,event_payload
  ) VALUES (
    NEW.employment_id,
    CASE WHEN TG_OP='INSERT' THEN 'employment_started' ELSE 'employment_ended' END,
    CASE WHEN TG_OP='INSERT' THEN NEW.effective_from_tick ELSE NEW.effective_to_tick END,
    CASE WHEN TG_OP='INSERT' THEN NEW.recorded_tick ELSE NEW.end_recorded_tick END,
    CASE WHEN TG_OP='INSERT' THEN NEW.actor_ref ELSE NEW.end_actor_ref END,
    CASE WHEN TG_OP='INSERT' THEN NEW.source_ref ELSE NEW.end_source_ref END,
    CASE WHEN TG_OP='INSERT' THEN NEW.idempotency_key ELSE NEW.end_idempotency_key END,
    jsonb_build_object('person_id',NEW.person_id,'employment_status',NEW.employment_status)
  );
  RETURN NEW;
END
$hr$;
CREATE TRIGGER employment_event_writer
AFTER INSERT OR UPDATE OF employment_status ON sw_hr.employment
FOR EACH ROW EXECUTE FUNCTION sw_hr.record_employment_event();

CREATE FUNCTION sw_hr.end_employment(
  p_employment_id text,p_effective_tick bigint,p_recorded_tick bigint,
  p_actor_ref text,p_source_ref text,p_idempotency_key text
) RETURNS TABLE(employment_id text,employment_status text)
LANGUAGE plpgsql AS $hr$
DECLARE v_employment sw_hr.employment%ROWTYPE;
BEGIN
  IF p_employment_id IS NULL OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR length(trim(p_idempotency_key)) NOT BETWEEN 1 AND 128 THEN
    RAISE EXCEPTION 'invalid BP33 employment end request';
  END IF;
  SELECT e.* INTO v_employment FROM sw_hr.employment AS e
  WHERE e.employment_id=p_employment_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'BP33 employment record not found'; END IF;
  IF v_employment.employment_status='ended' THEN
    IF v_employment.end_idempotency_key<>p_idempotency_key
       OR v_employment.effective_to_tick<>p_effective_tick
       OR v_employment.end_recorded_tick<>p_recorded_tick
       OR v_employment.end_actor_ref<>p_actor_ref
       OR v_employment.end_source_ref<>p_source_ref THEN
      RAISE EXCEPTION 'BP33 employment end conflicts with prior terminal event';
    END IF;
    RETURN QUERY SELECT v_employment.employment_id,'ended'::text;
    RETURN;
  END IF;
  IF p_effective_tick<=v_employment.effective_from_tick OR p_recorded_tick<v_employment.recorded_tick THEN
    RAISE EXCEPTION 'BP33 employment end ticks must follow its start';
  END IF;
  UPDATE sw_hr.employment AS e SET employment_status='ended',
    effective_to_tick=p_effective_tick,end_idempotency_key=p_idempotency_key,
    end_recorded_tick=p_recorded_tick,end_actor_ref=p_actor_ref,end_source_ref=p_source_ref
  WHERE e.employment_id=p_employment_id;
  RETURN QUERY SELECT p_employment_id,'ended'::text;
END
$hr$;

ALTER TABLE sw_property.staff_role_link
  DROP COLUMN role_title,
  ADD CONSTRAINT staff_role_link_bp33_employment_fk
    FOREIGN KEY(bp33_employment_ref) REFERENCES sw_hr.employment(employment_id)
    DEFERRABLE INITIALLY DEFERRED;

CREATE OR REPLACE FUNCTION sw_property.validate_staff_role_bp03_person()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
DECLARE v_exists boolean; v_employment sw_hr.employment%ROWTYPE;
BEGIN
  IF to_regclass('sw_people.person') IS NULL THEN
    RAISE EXCEPTION 'BP03 person register is not installed; BP04 staff links cannot create substitute people';
  END IF;
  EXECUTE 'SELECT EXISTS (SELECT 1 FROM sw_people.person WHERE person_id=$1)'
    INTO v_exists USING NEW.person_id;
  IF NOT v_exists THEN RAISE EXCEPTION 'staff role person_id does not resolve to BP03'; END IF;
  SELECT e.* INTO v_employment FROM sw_hr.employment AS e
  WHERE e.employment_id=NEW.bp33_employment_ref;
  IF NOT FOUND OR v_employment.person_id<>NEW.person_id
     OR v_employment.employer_business_id IS DISTINCT FROM NEW.employer_business_id
     OR v_employment.employer_organisation_id IS DISTINCT FROM NEW.employer_organisation_id
     OR v_employment.establishment_id IS DISTINCT FROM NEW.establishment_id
     OR v_employment.effective_from_tick<>NEW.effective_from_tick THEN
    RAISE EXCEPTION 'BP04 staff role link must match the authoritative BP33 employment record';
  END IF;
  RETURN NEW;
END
$bp04$;
DROP TRIGGER staff_role_bp03_person_guard ON sw_property.staff_role_link;
CREATE TRIGGER staff_role_bp33_employment_guard
BEFORE INSERT OR UPDATE ON sw_property.staff_role_link
FOR EACH ROW EXECUTE FUNCTION sw_property.validate_staff_role_bp03_person();

CREATE FUNCTION sw_property.reject_staff_role_link_mutation()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN RAISE EXCEPTION 'BP04 staff role links are append-only references to BP33 employment'; END
$bp04$;
CREATE TRIGGER staff_role_link_immutable
BEFORE UPDATE OR DELETE ON sw_property.staff_role_link
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_staff_role_link_mutation();

REVOKE ALL ON FUNCTION sw_hr.validate_employment_person_and_employer() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_hr.reject_employment_event_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_hr.guard_employment_transition() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_hr.record_employment_event() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_hr.end_employment(text,bigint,bigint,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.validate_staff_role_bp03_person() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.reject_staff_role_link_mutation() FROM PUBLIC;
COMMIT;
