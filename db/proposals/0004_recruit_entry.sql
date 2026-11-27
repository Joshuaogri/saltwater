-- PKG-003 recruit-entry domain proposal.
-- Disposable PostgreSQL validation only. NEVER apply to Neon without a separate
-- measured operation proposal and explicit production-write approval.
-- Depends on 0001_foundation.sql, 0002_runtime_city_population.sql,
-- and 0003_actor_session_authorization.sql.
BEGIN;

CREATE SCHEMA sw_player;
CREATE SCHEMA sw_police;

CREATE TABLE sw_player.profile (
  player_id uuid PRIMARY KEY,
  display_name text NOT NULL CHECK (length(btrim(display_name)) BETWEEN 1 AND 100),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE sw_police.recruit_intake (
  intake_id uuid PRIMARY KEY,
  player_id uuid NOT NULL REFERENCES sw_player.profile(player_id),
  status text NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending','accepted','rejected')),
  requested_tick bigint NOT NULL CHECK (requested_tick >= 0),
  request_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  request_idempotency_key text NOT NULL UNIQUE,
  outcome_event_id bigint UNIQUE REFERENCES sw_core.simulation_event(event_id),
  outcome_source text,
  outcome_actor_principal_id uuid REFERENCES sw_auth.principal(principal_id),
  outcome_tick bigint,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK ((status='pending' AND outcome_event_id IS NULL AND outcome_source IS NULL AND outcome_actor_principal_id IS NULL AND outcome_tick IS NULL)
      OR (status IN ('accepted','rejected') AND outcome_event_id IS NOT NULL
          AND outcome_source IS NOT NULL AND outcome_actor_principal_id IS NOT NULL AND outcome_tick IS NOT NULL))
);

CREATE SEQUENCE sw_police.service_number_seq START 1;

CREATE TABLE sw_police.personnel (
  personnel_id uuid PRIMARY KEY,
  person_id integer NOT NULL UNIQUE REFERENCES sw_people.person(person_id),
  service_number text NOT NULL UNIQUE,
  service_standing text NOT NULL CHECK (service_standing IN ('recruit','established')),
  service_status text NOT NULL CHECK (service_status IN ('active','suspended','separated')),
  supervisor_person_id integer NOT NULL REFERENCES sw_people.person(person_id),
  appointment_tick bigint NOT NULL CHECK (appointment_tick >= 0),
  appointment_source text NOT NULL CHECK (length(btrim(appointment_source)) BETWEEN 1 AND 200),
  appointment_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (person_id <> supervisor_person_id)
);

CREATE FUNCTION sw_police.reject_history_mutation() RETURNS trigger
LANGUAGE plpgsql AS $function$
BEGIN
  RAISE EXCEPTION 'police lifecycle history is append-only';
END
$function$;

CREATE TABLE sw_police.recruit_supervisor_authorisation (
  person_id integer PRIMARY KEY REFERENCES sw_police.personnel(person_id),
  authorised_by_principal_id uuid NOT NULL REFERENCES sw_auth.principal(principal_id),
  authority_source text NOT NULL CHECK (length(btrim(authority_source)) BETWEEN 1 AND 200),
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER recruit_supervisor_authorisation_immutable
BEFORE UPDATE OR DELETE ON sw_police.recruit_supervisor_authorisation
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_history_mutation();

CREATE TABLE sw_police.career_episode (
  career_id uuid PRIMARY KEY,
  player_id uuid NOT NULL REFERENCES sw_player.profile(player_id),
  personnel_id uuid NOT NULL REFERENCES sw_police.personnel(personnel_id),
  episode_no smallint NOT NULL CHECK (episode_no > 0),
  career_stage text NOT NULL CHECK (career_stage='recruit'),
  career_status text NOT NULL CHECK (career_status IN ('active','suspended','ended')),
  started_tick bigint NOT NULL CHECK (started_tick >= 0),
  start_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  UNIQUE (player_id, episode_no),
  UNIQUE (personnel_id, episode_no)
);
CREATE UNIQUE INDEX career_one_active_player_idx
  ON sw_police.career_episode(player_id) WHERE career_status IN ('active','suspended');

CREATE TABLE sw_police.lifecycle_event (
  event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  event_kind text NOT NULL CHECK (event_kind IN
    ('intake_requested','intake_accepted','intake_rejected','personnel_appointed','career_opened')),
  player_id uuid REFERENCES sw_player.profile(player_id),
  intake_id uuid REFERENCES sw_police.recruit_intake(intake_id),
  personnel_id uuid REFERENCES sw_police.personnel(personnel_id),
  career_id uuid REFERENCES sw_police.career_episode(career_id),
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  source_ref text,
  PRIMARY KEY (event_id,event_kind)
);

CREATE TRIGGER police_lifecycle_history_immutable
BEFORE UPDATE OR DELETE ON sw_police.lifecycle_event
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_history_mutation();

CREATE FUNCTION sw_police.reject_identity_delete() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'player, personnel and career identities cannot be deleted';
END
$$;
CREATE TRIGGER player_profile_no_delete
BEFORE DELETE ON sw_player.profile
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_identity_delete();
CREATE TRIGGER personnel_no_delete
BEFORE DELETE ON sw_police.personnel
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_identity_delete();
CREATE TRIGGER career_episode_no_delete
BEFORE DELETE ON sw_police.career_episode
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_identity_delete();

INSERT INTO sw_core.event_type(event_code,description) VALUES
 ('RECRUIT_INTAKE_REQUESTED','Player requests recruit entry; pending until authorised outcome'),
 ('RECRUIT_INTAKE_ACCEPTED','Recruit intake accepted by authorised recruitment owner'),
 ('RECRUIT_INTAKE_REJECTED','Recruit intake rejected by authorised recruitment owner'),
 ('PERSONNEL_APPOINTED','Canonical person receives a police recruit service appointment'),
 ('CAREER_EPISODE_OPENED','Player career episode opens after accepted recruit appointment')
ON CONFLICT (event_code) DO NOTHING;

CREATE FUNCTION sw_police.request_recruit_intake(
  p_player_id uuid,
  p_display_name text,
  p_idempotency_key text
) RETURNS uuid
LANGUAGE plpgsql AS $$
DECLARE
  v_existing sw_police.recruit_intake%ROWTYPE;
  v_tick bigint;
  v_intake_id uuid := gen_random_uuid();
  v_event_id bigint;
BEGIN
  IF p_player_id IS NULL OR p_idempotency_key IS NULL OR length(btrim(p_idempotency_key)) < 8 THEN
    RAISE EXCEPTION 'player identity and idempotency key (minimum 8 characters) are required';
  END IF;
  IF p_display_name IS NULL OR length(btrim(p_display_name)) NOT BETWEEN 1 AND 100 THEN
    RAISE EXCEPTION 'display name must contain 1 to 100 characters';
  END IF;

  PERFORM pg_advisory_xact_lock(hashtextextended(p_idempotency_key,0));
  SELECT * INTO v_existing FROM sw_police.recruit_intake
    WHERE request_idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_existing.player_id <> p_player_id THEN
      RAISE EXCEPTION 'idempotency key belongs to a different player';
    END IF;
    RETURN v_existing.intake_id;
  END IF;

  SELECT world_tick INTO v_tick FROM sw_runtime.state
    WHERE singleton=1 AND state=2 AND player_present=true FOR SHARE;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'recruit intake requires active play and a present player';
  END IF;

  INSERT INTO sw_player.profile(player_id,display_name)
  VALUES (p_player_id,btrim(p_display_name))
  ON CONFLICT (player_id) DO NOTHING;

  SELECT event_type_id INTO STRICT v_event_id
    FROM sw_core.event_type WHERE event_code='RECRUIT_INTAKE_REQUESTED';
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,source_ref,attributes,idempotency_key)
  VALUES (v_event_id,clock_timestamp(),v_tick,'player',p_player_id::text,
          jsonb_build_object('intake_id',v_intake_id,'status','pending'),p_idempotency_key)
  RETURNING event_id INTO v_event_id;

  INSERT INTO sw_police.recruit_intake(intake_id,player_id,status,requested_tick,request_event_id,request_idempotency_key)
  VALUES (v_intake_id,p_player_id,'pending',v_tick,v_event_id,p_idempotency_key);
  INSERT INTO sw_police.lifecycle_event(event_id,player_id,intake_id,event_kind,effective_tick)
  VALUES (v_event_id,p_player_id,v_intake_id,'intake_requested',v_tick);
  RETURN v_intake_id;
END
$$;

CREATE FUNCTION sw_police.accept_recruit_intake(
  p_intake_id uuid,
  p_supervisor_person_id integer,
  p_appointment_source text,
  p_idempotency_key text,
  p_authorised_by_principal_id uuid,
  p_given_name text DEFAULT NULL,
  p_middle_name text DEFAULT NULL,
  p_family_name text DEFAULT NULL
) RETURNS uuid
LANGUAGE plpgsql AS $$
DECLARE
  v_intake sw_police.recruit_intake%ROWTYPE;
  v_tick bigint;
  v_count integer;
  v_person_id integer;
  v_personnel_id uuid := gen_random_uuid();
  v_career_id uuid := gen_random_uuid();
  v_person_event bigint;
  v_population_event bigint;
  v_appointment_event bigint;
  v_intake_event bigint;
  v_career_event bigint;
  v_personnel_number text;
  v_event_type smallint;
  v_episode smallint;
  v_actor_ok boolean;
BEGIN
  IF p_intake_id IS NULL OR p_supervisor_person_id IS NULL OR p_authorised_by_principal_id IS NULL
     OR p_appointment_source IS NULL OR length(btrim(p_appointment_source)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR length(btrim(p_idempotency_key)) < 8 THEN
    RAISE EXCEPTION 'intake, authorised supervisor, appointment source and idempotency key are required';
  END IF;

  SELECT * INTO v_intake FROM sw_police.recruit_intake
    WHERE intake_id=p_intake_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'recruit intake does not exist'; END IF;

  SELECT EXISTS (
    SELECT 1 FROM sw_auth.principal p
    JOIN sw_auth.principal_role r ON r.principal_id=p.principal_id
    WHERE p.principal_id=p_authorised_by_principal_id
      AND p.status='active' AND p.principal_kind IN ('administrator','officer')
      AND r.role_code='recruitment_approver' AND r.revoked_at IS NULL
  ) INTO v_actor_ok;
  IF NOT v_actor_ok THEN RAISE EXCEPTION 'appointment requires an active authorised recruitment approver'; END IF;

  IF v_intake.status='accepted' THEN
    SELECT career_id INTO STRICT v_career_id
      FROM sw_police.career_episode
      WHERE player_id=v_intake.player_id AND career_status IN ('active','suspended');
    RETURN v_career_id;
  END IF;
  IF v_intake.status <> 'pending' THEN RAISE EXCEPTION 'only pending intake can be accepted'; END IF;

  SELECT world_tick INTO v_tick FROM sw_runtime.state
    WHERE singleton=1 AND state=2 AND player_present=true FOR SHARE;
  IF NOT FOUND THEN RAISE EXCEPTION 'appointment requires active play and a present player'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM sw_police.personnel p
    JOIN sw_police.recruit_supervisor_authorisation a ON a.person_id=p.person_id
    WHERE p.person_id=p_supervisor_person_id AND p.service_status='active'
      AND p.service_standing='established'
  ) THEN
    RAISE EXCEPTION 'supervisor must be active established personnel with explicit recruit-supervision authorisation';
  END IF;

  -- Lock the shared population counter before checking or creating the person.
  SELECT living_included INTO v_count
    FROM sw_people.population_counter WHERE singleton=1 FOR UPDATE;
  IF v_count >= 10000 THEN
    RAISE EXCEPTION 'Saltwater living population cap of 10000 reached';
  END IF;

  SELECT event_type_id INTO STRICT v_event_type FROM sw_core.event_type WHERE event_code='PERSON_CREATED';
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,source_ref,attributes,idempotency_key)
  VALUES (v_event_type,clock_timestamp(),v_tick,'person','recruit-intake:'||p_intake_id::text,
          jsonb_build_object('intake_id',p_intake_id),p_idempotency_key||':person')
  RETURNING event_id INTO v_person_event;

  INSERT INTO sw_people.person(given_name,middle_name,family_name,created_tick,source_ref,last_event_id)
  VALUES (p_given_name,p_middle_name,p_family_name,v_tick,'recruit-intake:'||p_intake_id::text,v_person_event)
  RETURNING person_id INTO v_person_id;

  SELECT event_type_id INTO STRICT v_event_type FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED';
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key)
  VALUES (v_event_type,clock_timestamp(),v_tick,'person',v_person_id,'recruit-intake:'||p_intake_id::text,
          jsonb_build_object('life_status',1,'scope_status',1),p_idempotency_key||':population')
  RETURNING event_id INTO v_population_event;

  INSERT INTO sw_people.population_state(person_id,life_status,scope_status,effective_tick,last_event_id,active_police_service)
  VALUES (v_person_id,1,1,v_tick,v_population_event,true);

  SELECT event_type_id INTO STRICT v_event_type FROM sw_core.event_type WHERE event_code='PERSONNEL_APPOINTED';
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key)
  VALUES (v_event_type,clock_timestamp(),v_tick,'person',v_person_id,p_appointment_source,
          jsonb_build_object('standing','recruit','supervisor_person_id',p_supervisor_person_id,
            'authorised_by_principal_id',p_authorised_by_principal_id),p_idempotency_key||':appointment')
  RETURNING event_id INTO v_appointment_event;

  v_personnel_number := 'SWP-'||lpad(nextval('sw_police.service_number_seq')::text,8,'0');
  INSERT INTO sw_police.personnel(personnel_id,person_id,service_number,service_standing,service_status,
    supervisor_person_id,appointment_tick,appointment_source,appointment_event_id)
  VALUES (v_personnel_id,v_person_id,v_personnel_number,'recruit','active',
    p_supervisor_person_id,v_tick,p_appointment_source,v_appointment_event);

  SELECT COALESCE(max(episode_no),0)+1 INTO v_episode
    FROM sw_police.career_episode WHERE player_id=v_intake.player_id;
  IF v_episode > 32767 THEN RAISE EXCEPTION 'career episode limit reached'; END IF;

  SELECT event_type_id INTO STRICT v_event_type FROM sw_core.event_type WHERE event_code='CAREER_EPISODE_OPENED';
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,source_ref,attributes,idempotency_key)
  VALUES (v_event_type,clock_timestamp(),v_tick,'player',v_intake.player_id::text,
          jsonb_build_object('person_id',v_person_id,'personnel_id',v_personnel_id,'career_id',v_career_id,'stage','recruit'),
          p_idempotency_key||':career')
  RETURNING event_id INTO v_career_event;

  INSERT INTO sw_police.career_episode(career_id,player_id,personnel_id,episode_no,career_stage,career_status,started_tick,start_event_id)
  VALUES (v_career_id,v_intake.player_id,v_personnel_id,v_episode,'recruit','active',v_tick,v_career_event);

  SELECT event_type_id INTO STRICT v_event_type FROM sw_core.event_type WHERE event_code='RECRUIT_INTAKE_ACCEPTED';
  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,subject_kind,source_ref,attributes,idempotency_key)
  VALUES (v_event_type,clock_timestamp(),v_tick,'player',v_intake.player_id::text,
          jsonb_build_object('intake_id',p_intake_id,'career_id',v_career_id),p_idempotency_key||':intake')
  RETURNING event_id INTO v_intake_event;

  UPDATE sw_police.recruit_intake SET status='accepted',outcome_event_id=v_intake_event,
    outcome_source=p_appointment_source,outcome_actor_principal_id=p_authorised_by_principal_id,
    outcome_tick=v_tick WHERE intake_id=p_intake_id;
  INSERT INTO sw_police.lifecycle_event(event_id,player_id,intake_id,personnel_id,career_id,event_kind,effective_tick,source_ref)
  VALUES (v_intake_event,v_intake.player_id,p_intake_id,v_personnel_id,v_career_id,'intake_accepted',v_tick,p_appointment_source),
         (v_appointment_event,v_intake.player_id,p_intake_id,v_personnel_id,v_career_id,'personnel_appointed',v_tick,p_appointment_source);
  INSERT INTO sw_police.lifecycle_event(event_id,player_id,intake_id,personnel_id,career_id,event_kind,effective_tick,source_ref)
  VALUES (v_career_event,v_intake.player_id,p_intake_id,v_personnel_id,v_career_id,'career_opened',v_tick,p_appointment_source);

  RETURN v_career_id;
END
$$;

REVOKE ALL ON ALL TABLES IN SCHEMA sw_player FROM PUBLIC, sw_game_readonly, sw_game_command;
REVOKE ALL ON ALL TABLES IN SCHEMA sw_police FROM PUBLIC, sw_game_readonly, sw_game_command;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA sw_police FROM PUBLIC, sw_game_readonly, sw_game_command;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA sw_police FROM PUBLIC, sw_game_readonly, sw_game_command;
REVOKE ALL ON SCHEMA sw_player, sw_police FROM PUBLIC;

CREATE VIEW sw_police.player_career_status AS
SELECT i.player_id,i.intake_id,i.status AS intake_status,i.requested_tick,
       c.career_id,c.career_stage,c.career_status,c.started_tick,
       p.person_id,p.service_number,p.service_standing,p.service_status,
       p.supervisor_person_id
FROM sw_police.recruit_intake i
LEFT JOIN sw_police.career_episode c ON c.player_id=i.player_id
LEFT JOIN sw_police.personnel p ON p.personnel_id=c.personnel_id;

REVOKE ALL ON sw_police.player_career_status FROM PUBLIC, sw_game_readonly, sw_game_command;
COMMIT;
