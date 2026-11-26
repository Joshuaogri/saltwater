-- BP06 opening police cohort provisioning.
-- Consumes existing canonical BP03 person identities only; it never creates people.
-- Disposable PostgreSQL proposal. Do not apply to production Neon without separate
-- explicit approval and a reviewed 500-person identity/category manifest.
BEGIN;

ALTER TABLE sw_police.personnel
  ADD COLUMN personnel_category text NOT NULL DEFAULT 'sworn_officer'
  CHECK (personnel_category IN
    ('sworn_officer','civilian_employee','technical_professional','auxiliary','contractor'));

ALTER TABLE sw_police.personnel
  ALTER COLUMN supervisor_person_id DROP NOT NULL;

CREATE OR REPLACE FUNCTION sw_runtime.guard_event_insert() RETURNS trigger
LANGUAGE plpgsql AS $function$
DECLARE
  runtime_state smallint;
  present boolean;
  current_tick bigint;
  event_code text;
BEGIN
  SELECT state, player_present, world_tick
    INTO runtime_state, present, current_tick
    FROM sw_runtime.state
    WHERE singleton = 1
    FOR SHARE;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'runtime state singleton is missing';
  END IF;

  SELECT et.event_code INTO event_code
    FROM sw_core.event_type et
    WHERE et.event_type_id = NEW.event_type_id;
  IF event_code IS NULL THEN
    RAISE EXCEPTION 'unknown event type';
  END IF;
  IF NEW.world_tick <> current_tick THEN
    RAISE EXCEPTION 'event world_tick must equal the committed runtime tick';
  END IF;
  IF event_code IN ('RUNTIME_READY','RUNTIME_START','RUNTIME_PAUSE','RUNTIME_RESUME','RUNTIME_STOP','RUNTIME_RECOVERY') THEN
    RETURN NEW;
  END IF;
  IF runtime_state = 1 AND current_tick = 0
     AND (SELECT bootstrap_open FROM sw_runtime.state WHERE singleton = 1)
     AND event_code IN ('GEO_CREATED','GEO_VERSIONED','PERSON_CREATED',
                        'POPULATION_STATE_CHANGED','RESIDENCE_CHANGED',
                        'PERSONNEL_APPOINTED') THEN
    RETURN NEW;
  END IF;
  IF NOT (runtime_state = 2 AND present) THEN
    RAISE EXCEPTION 'simulation events are blocked while stopped, paused, recovering or player-absent';
  END IF;
  RETURN NEW;
END
$function$;

CREATE OR REPLACE FUNCTION sw_police.create_personnel_service_dossier()
RETURNS trigger LANGUAGE plpgsql AS $bp06$
DECLARE
  v_appointment_id uuid := gen_random_uuid();
  v_supervisor_personnel_id uuid;
  v_authorised_by uuid;
  v_authority_source text;
  v_appointment_type text;
BEGIN
  v_appointment_type := CASE
    WHEN NEW.service_standing='recruit' THEN 'recruit_entry'
    WHEN NEW.personnel_category='sworn_officer' THEN 'direct_entry'
    ELSE 'civilian_appointment'
  END;

  INSERT INTO sw_police.personnel_service_engagement(
    appointment_id,personnel_id,personnel_category,appointment_type,service_state,
    is_primary,effective_from_tick,appointment_event_id,appointment_source,source_ref
  ) VALUES (
    v_appointment_id,NEW.personnel_id,NEW.personnel_category,v_appointment_type,'active',
    true,NEW.appointment_tick,NEW.appointment_event_id,NEW.appointment_source,
    'BP06:personnel-appointment:'||NEW.personnel_id::text
  );

  INSERT INTO sw_police.personnel_service_event(
    event_id,personnel_id,appointment_id,event_kind,new_state,effective_tick,
    actor_ref,authority_ref,source_ref,reason
  ) VALUES (
    NEW.appointment_event_id,NEW.personnel_id,v_appointment_id,'appointed','active',
    NEW.appointment_tick,'domain:personnel-provisioning',NEW.appointment_source,
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

CREATE TABLE sw_police.opening_personnel_cohort (
  cohort_code text PRIMARY KEY CHECK (cohort_code='OPENING-POLICE-500'),
  member_manifest jsonb NOT NULL,
  member_count smallint NOT NULL CHECK (member_count=500),
  effective_tick bigint NOT NULL CHECK (effective_tick=0),
  source_ref text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (jsonb_typeof(member_manifest)='array' AND jsonb_array_length(member_manifest)=500)
);

CREATE TABLE sw_police.opening_personnel_cohort_member (
  cohort_code text NOT NULL REFERENCES sw_police.opening_personnel_cohort(cohort_code),
  person_id integer NOT NULL UNIQUE REFERENCES sw_people.person(person_id),
  personnel_id uuid NOT NULL UNIQUE REFERENCES sw_police.personnel(personnel_id),
  personnel_category text NOT NULL CHECK (personnel_category IN
    ('sworn_officer','civilian_employee','technical_professional')),
  service_number text NOT NULL UNIQUE,
  source_ref text NOT NULL,
  PRIMARY KEY (cohort_code,person_id)
);

CREATE TRIGGER opening_personnel_cohort_immutable
BEFORE UPDATE OR DELETE ON sw_police.opening_personnel_cohort
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_personnel_history_mutation();

CREATE TRIGGER opening_personnel_cohort_member_immutable
BEFORE UPDATE OR DELETE ON sw_police.opening_personnel_cohort_member
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_personnel_history_mutation();

CREATE FUNCTION sw_police.provision_opening_personnel_cohort(
  p_members jsonb,
  p_source_ref text
) RETURNS integer
LANGUAGE plpgsql
AS $function$
DECLARE
  v_manifest jsonb;
  v_existing jsonb;
  v_existing_source_ref text;
  v_tick bigint;
  v_event_type smallint;
  v_member record;
  v_personnel_id uuid;
  v_event_id bigint;
  v_service_number text;
  v_existing_count integer;
BEGIN
  IF p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200 THEN
    RAISE EXCEPTION 'opening cohort source reference must contain 1 to 200 characters';
  END IF;
  IF p_members IS NULL OR jsonb_typeof(p_members)<>'array'
     OR jsonb_array_length(p_members)<>500 THEN
    RAISE EXCEPTION 'opening police cohort must contain exactly 500 person/category records';
  END IF;

  SELECT jsonb_agg(
           jsonb_build_object('person_id',x.person_id,'personnel_category',x.personnel_category)
           ORDER BY x.person_id
         )
    INTO v_manifest
  FROM jsonb_to_recordset(p_members)
       AS x(person_id integer,personnel_category text);

  IF jsonb_array_length(v_manifest)<>500
     OR (SELECT count(DISTINCT x.person_id) FROM jsonb_to_recordset(v_manifest)
          AS x(person_id integer,personnel_category text))<>500
     OR EXISTS (
       SELECT 1 FROM jsonb_to_recordset(v_manifest)
         AS x(person_id integer,personnel_category text)
       WHERE x.person_id IS NULL
          OR x.personnel_category IS NULL
          OR x.personnel_category NOT IN
             ('sworn_officer','civilian_employee','technical_professional')
     ) THEN
    RAISE EXCEPTION 'cohort requires 500 unique person IDs and supported employee categories';
  END IF;

  PERFORM pg_advisory_xact_lock(hashtextextended('saltwater:opening-police-cohort-v1',0));

  SELECT member_manifest,source_ref INTO v_existing,v_existing_source_ref
  FROM sw_police.opening_personnel_cohort
  WHERE cohort_code='OPENING-POLICE-500'
  FOR UPDATE;
  IF FOUND THEN
    IF v_existing IS DISTINCT FROM v_manifest OR v_existing_source_ref IS DISTINCT FROM p_source_ref THEN
      RAISE EXCEPTION 'opening police cohort already exists with a different identity manifest or source';
    END IF;
    SELECT count(*) INTO v_existing_count
    FROM sw_police.opening_personnel_cohort_member
    WHERE cohort_code='OPENING-POLICE-500';
    IF v_existing_count<>500 THEN
      RAISE EXCEPTION 'existing opening police cohort is incomplete';
    END IF;
    RETURN 500;
  END IF;

  SELECT world_tick INTO STRICT v_tick
  FROM sw_runtime.state
  WHERE singleton=1 AND state=1 AND player_present=false
    AND bootstrap_open=true AND world_tick=0
  FOR UPDATE;

  IF (SELECT count(*)
      FROM jsonb_to_recordset(v_manifest)
           AS x(person_id integer,personnel_category text)
      JOIN sw_people.person p ON p.person_id=x.person_id
      JOIN sw_people.population_state ps ON ps.person_id=p.person_id
      WHERE ps.life_status=1 AND ps.scope_status=1)<>500 THEN
    RAISE EXCEPTION 'all 500 cohort members must already exist as living, population-included BP03 people';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM jsonb_to_recordset(v_manifest)
         AS x(person_id integer,personnel_category text)
    JOIN sw_player.identity_binding b ON b.person_id=x.person_id
  ) THEN
    RAISE EXCEPTION 'the human player identity cannot be appointed as an NPC police employee';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM jsonb_to_recordset(v_manifest)
         AS x(person_id integer,personnel_category text)
    JOIN sw_police.personnel p ON p.person_id=x.person_id
  ) THEN
    RAISE EXCEPTION 'one or more cohort members already have a police personnel dossier';
  END IF;

  SELECT event_type_id INTO STRICT v_event_type
  FROM sw_core.event_type WHERE event_code='PERSONNEL_APPOINTED';

  INSERT INTO sw_police.opening_personnel_cohort(
    cohort_code,member_manifest,member_count,effective_tick,source_ref
  ) VALUES ('OPENING-POLICE-500',v_manifest,500,0,p_source_ref);

  FOR v_member IN
    SELECT x.person_id,x.personnel_category
    FROM jsonb_to_recordset(v_manifest)
         AS x(person_id integer,personnel_category text)
    ORDER BY x.person_id
  LOOP
    v_personnel_id := gen_random_uuid();
    v_service_number := 'SWP-'||lpad(nextval('sw_police.service_number_seq')::text,8,'0');

    INSERT INTO sw_core.simulation_event(
      event_type_id,occurred_at,world_tick,subject_kind,subject_id,
      source_ref,attributes,idempotency_key
    ) VALUES (
      v_event_type,clock_timestamp(),v_tick,'person',v_member.person_id,
      p_source_ref,
      jsonb_build_object('personnel_category',v_member.personnel_category,
                         'service_standing','established',
                         'cohort_code','OPENING-POLICE-500'),
      'SW-OPENING-POLICE-V1:'||v_member.person_id::text
    ) RETURNING event_id INTO v_event_id;

    INSERT INTO sw_police.personnel(
      personnel_id,person_id,service_number,service_standing,service_status,
      personnel_category,supervisor_person_id,appointment_tick,
      appointment_source,appointment_event_id
    ) VALUES (
      v_personnel_id,v_member.person_id,v_service_number,'established','active',
      v_member.personnel_category,NULL,v_tick,p_source_ref,v_event_id
    );

    INSERT INTO sw_police.opening_personnel_cohort_member(
      cohort_code,person_id,personnel_id,personnel_category,service_number,source_ref
    ) VALUES (
      'OPENING-POLICE-500',v_member.person_id,v_personnel_id,
      v_member.personnel_category,v_service_number,p_source_ref
    );
  END LOOP;

  SELECT count(*) INTO v_existing_count
  FROM sw_police.opening_personnel_cohort_member
  WHERE cohort_code='OPENING-POLICE-500';
  IF v_existing_count<>500 THEN
    RAISE EXCEPTION 'opening police cohort provisioning did not create 500 personnel links';
  END IF;
  RETURN v_existing_count;
END
$function$;

REVOKE ALL ON TABLE sw_police.opening_personnel_cohort,
  sw_police.opening_personnel_cohort_member
  FROM PUBLIC,sw_game_readonly,sw_game_command;
REVOKE ALL ON FUNCTION sw_police.provision_opening_personnel_cohort(jsonb,text)
  FROM PUBLIC,sw_game_readonly,sw_game_command;

COMMIT;
