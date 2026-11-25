-- BP06 canonical personnel dossier, service engagement and supervision history.
-- Depends on PKG-003 recruit entry and BP05 organisation/establishment.
BEGIN;

CREATE TABLE sw_police.personnel_service_engagement (
  appointment_id uuid PRIMARY KEY,
  personnel_id uuid NOT NULL REFERENCES sw_police.personnel(personnel_id),
  personnel_category text NOT NULL CHECK(personnel_category IN
    ('sworn_officer','civilian_employee','technical_professional','auxiliary','contractor')),
  appointment_type text NOT NULL CHECK(appointment_type IN
    ('recruit_entry','direct_entry','civilian_appointment','secondment_in','rehire')),
  service_state text NOT NULL CHECK(service_state IN
    ('pending_start','probationary','active','leave','suspended','secondment_out',
     'secondment_in','notice','separated','retired','deceased','rescinded')),
  is_primary boolean NOT NULL DEFAULT true,
  effective_from_tick bigint NOT NULL CHECK(effective_from_tick>=0),
  effective_to_tick bigint,
  appointment_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  appointment_source text NOT NULL,
  source_ref text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK(effective_to_tick IS NULL OR effective_to_tick>=effective_from_tick)
);
CREATE UNIQUE INDEX personnel_one_active_primary_appointment
  ON sw_police.personnel_service_engagement(personnel_id)
  WHERE is_primary AND service_state IN
    ('pending_start','probationary','active','leave','suspended','secondment_out','secondment_in','notice');

CREATE TABLE sw_police.personnel_service_event (
  service_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  personnel_id uuid NOT NULL REFERENCES sw_police.personnel(personnel_id),
  appointment_id uuid NOT NULL REFERENCES sw_police.personnel_service_engagement(appointment_id),
  event_kind text NOT NULL CHECK(event_kind IN
    ('appointed','service_state_changed','category_changed','service_number_issued',
     'service_number_changed','supervision_assigned','supervision_ended','appointment_rescinded',
     'record_corrected')),
  prior_state text,
  new_state text,
  effective_tick bigint NOT NULL CHECK(effective_tick>=0),
  actor_ref text NOT NULL,
  authority_ref text,
  source_ref text NOT NULL,
  reason text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(event_id,event_kind)
);
CREATE INDEX personnel_service_event_history_idx
  ON sw_police.personnel_service_event(personnel_id,service_event_id);

CREATE TABLE sw_police.service_number_history (
  service_number_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  personnel_id uuid NOT NULL REFERENCES sw_police.personnel(personnel_id),
  service_number text NOT NULL UNIQUE,
  event_kind text NOT NULL CHECK(event_kind IN ('issued','changed','retired')),
  effective_tick bigint NOT NULL CHECK(effective_tick>=0),
  source_ref text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX service_number_history_person_idx
  ON sw_police.service_number_history(personnel_id,service_number_event_id);

CREATE TABLE sw_police.personnel_supervision_link (
  supervision_link_id text PRIMARY KEY,
  supervisor_personnel_id uuid NOT NULL REFERENCES sw_police.personnel(personnel_id),
  supervisee_personnel_id uuid NOT NULL REFERENCES sw_police.personnel(personnel_id),
  relationship_type text NOT NULL CHECK(relationship_type IN
    ('line_supervisor','acting_supervisor','recruit_supervisor','mentor','assessor')),
  effective_from_tick bigint NOT NULL CHECK(effective_from_tick>=0),
  effective_to_tick bigint,
  authority_source text NOT NULL,
  authorised_by_principal_id uuid REFERENCES sw_auth.principal(principal_id),
  source_ref text NOT NULL,
  CHECK(supervisor_personnel_id<>supervisee_personnel_id),
  CHECK(effective_to_tick IS NULL OR effective_to_tick>=effective_from_tick)
);
CREATE UNIQUE INDEX personnel_one_active_recruit_supervisor
  ON sw_police.personnel_supervision_link(supervisee_personnel_id)
  WHERE relationship_type='recruit_supervisor' AND effective_to_tick IS NULL;
CREATE INDEX personnel_supervision_supervisor_idx
  ON sw_police.personnel_supervision_link(supervisor_personnel_id,effective_from_tick DESC);

CREATE FUNCTION sw_police.reject_personnel_history_mutation() RETURNS trigger
LANGUAGE plpgsql AS $bp06$
BEGIN
  RAISE EXCEPTION '% is append-only; add a new service event',TG_TABLE_NAME;
END
$bp06$;
CREATE TRIGGER personnel_service_event_immutable
BEFORE UPDATE OR DELETE ON sw_police.personnel_service_event
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_personnel_history_mutation();
CREATE TRIGGER service_number_history_immutable
BEFORE UPDATE OR DELETE ON sw_police.service_number_history
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_personnel_history_mutation();

CREATE FUNCTION sw_police.create_personnel_service_dossier()
RETURNS trigger LANGUAGE plpgsql AS $bp06$
DECLARE
  v_appointment_id uuid := gen_random_uuid();
  v_supervisor_personnel_id uuid;
  v_authorised_by uuid;
  v_authority_source text;
BEGIN
  INSERT INTO sw_police.personnel_service_engagement(
    appointment_id,personnel_id,personnel_category,appointment_type,service_state,
    is_primary,effective_from_tick,appointment_event_id,appointment_source,source_ref
  ) VALUES (
    v_appointment_id,NEW.personnel_id,'sworn_officer','recruit_entry','active',
    true,NEW.appointment_tick,NEW.appointment_event_id,NEW.appointment_source,
    'BP06:personnel-appointment:'||NEW.personnel_id::text
  );

  INSERT INTO sw_police.personnel_service_event(
    event_id,personnel_id,appointment_id,event_kind,new_state,effective_tick,
    actor_ref,authority_ref,source_ref,reason
  ) VALUES (
    NEW.appointment_event_id,NEW.personnel_id,v_appointment_id,'appointed','active',
    NEW.appointment_tick,'domain:recruitment',NEW.appointment_source,
    'BP06:personnel-appointment:'||NEW.personnel_id::text,
    'Personnel dossier and primary service engagement created'
  );

  INSERT INTO sw_police.service_number_history(
    personnel_id,service_number,event_kind,effective_tick,source_ref
  ) VALUES (
    NEW.personnel_id,NEW.service_number,'issued',NEW.appointment_tick,
    'BP06:service-number:'||NEW.personnel_id::text
  );

  IF NEW.service_standing='recruit' THEN
    SELECT p.personnel_id INTO v_supervisor_personnel_id
    FROM sw_police.personnel p
    WHERE p.person_id=NEW.supervisor_person_id
      AND p.service_status='active'
      AND p.service_standing='established';
    IF v_supervisor_personnel_id IS NULL THEN
      RAISE EXCEPTION 'recruit appointment requires one active established personnel supervisor';
    END IF;

    SELECT a.authorised_by_principal_id,a.authority_source
      INTO v_authorised_by,v_authority_source
    FROM sw_police.recruit_supervisor_authorisation a
    WHERE a.person_id=NEW.supervisor_person_id;

    IF v_authorised_by IS NULL THEN
      RAISE EXCEPTION 'recruit supervisor authorisation is missing';
    END IF;

    INSERT INTO sw_police.personnel_supervision_link(
      supervision_link_id,supervisor_personnel_id,supervisee_personnel_id,
      relationship_type,effective_from_tick,authority_source,
      authorised_by_principal_id,source_ref
    ) VALUES (
      'SWPS-SUP-'||NEW.personnel_id::text,v_supervisor_personnel_id,NEW.personnel_id,
      'recruit_supervisor',NEW.appointment_tick,v_authority_source,
      v_authorised_by,'BP06:recruit-supervision:'||NEW.personnel_id::text
    );
  END IF;
  RETURN NEW;
END
$bp06$;
CREATE TRIGGER personnel_service_dossier_after_insert
AFTER INSERT ON sw_police.personnel
FOR EACH ROW EXECUTE FUNCTION sw_police.create_personnel_service_dossier();

CREATE VIEW sw_police.personnel_service_current AS
SELECT p.personnel_id,p.person_id,p.service_number,p.service_standing,p.service_status,
       e.appointment_id,e.personnel_category,e.appointment_type,e.service_state,
       e.effective_from_tick,e.effective_to_tick,e.is_primary,
       pop.life_status,pop.scope_status
FROM sw_police.personnel p
JOIN sw_police.personnel_service_engagement e
  ON e.personnel_id=p.personnel_id AND e.is_primary
JOIN sw_people.population_state pop ON pop.person_id=p.person_id
WHERE e.service_state IN
  ('pending_start','probationary','active','leave','suspended','secondment_out','secondment_in','notice');

CREATE VIEW sw_police.personnel_headcount_by_state AS
SELECT personnel_category,service_state,count(DISTINCT person_id)::bigint AS distinct_people
FROM sw_police.personnel_service_current
WHERE life_status=1 AND scope_status=1
GROUP BY personnel_category,service_state;

COMMIT;
