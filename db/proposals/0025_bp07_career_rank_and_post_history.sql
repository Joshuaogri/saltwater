-- BP07 career history, substantive rank and post appointment records.
-- No rank, promotion or post is automatically assigned to a recruit.
BEGIN;

CREATE TABLE sw_police.career_event (
  career_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  career_id uuid NOT NULL REFERENCES sw_police.career_episode(career_id),
  personnel_id uuid NOT NULL REFERENCES sw_police.personnel(personnel_id),
  event_kind text NOT NULL CHECK(event_kind IN
    ('career_opened','probation_reviewed','probation_extended','probation_confirmed',
     'rank_assigned','rank_changed','rank_removed','post_appointed','post_vacated',
     'promotion_case_opened','promotion_decided','acting_appointed','acting_ended',
     'secondment_started','secondment_ended','career_suspended','career_reinstated',
     'career_ended','service_credit_adjusted','record_corrected')),
  prior_stage text,
  resulting_stage text,
  prior_status text,
  resulting_status text,
  effective_tick bigint NOT NULL CHECK(effective_tick>=0),
  actor_ref text NOT NULL,
  authority_ref text,
  source_ref text NOT NULL,
  reason text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(event_id,event_kind)
);
CREATE INDEX career_event_history_idx ON sw_police.career_event(career_id,career_event_id);

CREATE TABLE sw_police.career_rank_assignment (
  rank_assignment_id uuid PRIMARY KEY,
  career_id uuid NOT NULL REFERENCES sw_police.career_episode(career_id),
  personnel_id uuid NOT NULL REFERENCES sw_police.personnel(personnel_id),
  rank_code text NOT NULL REFERENCES sw_police.rank_definition(rank_code),
  assignment_type text NOT NULL CHECK(assignment_type IN ('substantive','acting')),
  effective_from_tick bigint NOT NULL CHECK(effective_from_tick>=0),
  effective_to_tick bigint,
  source_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  decision_ref text NOT NULL,
  authorised_by_principal_id uuid REFERENCES sw_auth.principal(principal_id),
  idempotency_key text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK(effective_to_tick IS NULL OR effective_to_tick>=effective_from_tick)
);
CREATE UNIQUE INDEX career_one_active_substantive_rank
  ON sw_police.career_rank_assignment(personnel_id)
  WHERE assignment_type='substantive' AND effective_to_tick IS NULL;

CREATE TABLE sw_police.career_post_appointment (
  position_appointment_id uuid PRIMARY KEY,
  career_id uuid NOT NULL REFERENCES sw_police.career_episode(career_id),
  personnel_id uuid NOT NULL REFERENCES sw_police.personnel(personnel_id),
  post_id text NOT NULL REFERENCES sw_police.authorised_post(post_id),
  position_id text NOT NULL REFERENCES sw_police.position_definition(position_id),
  appointment_type text NOT NULL CHECK(appointment_type IN ('substantive','acting','temporary')),
  effective_from_tick bigint NOT NULL CHECK(effective_from_tick>=0),
  effective_to_tick bigint,
  source_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  authority_ref text NOT NULL,
  idempotency_key text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK(effective_to_tick IS NULL OR effective_to_tick>=effective_from_tick)
);
CREATE UNIQUE INDEX career_one_active_occupant_per_post
  ON sw_police.career_post_appointment(post_id)
  WHERE effective_to_tick IS NULL;
CREATE INDEX career_post_person_history_idx
  ON sw_police.career_post_appointment(personnel_id,effective_from_tick DESC);

CREATE FUNCTION sw_police.reject_career_history_mutation() RETURNS trigger
LANGUAGE plpgsql AS $bp07$
BEGIN
  RAISE EXCEPTION '% is append-only; record a new career event',TG_TABLE_NAME;
END
$bp07$;
CREATE TRIGGER career_event_immutable
BEFORE UPDATE OR DELETE ON sw_police.career_event
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_career_history_mutation();
CREATE TRIGGER career_rank_assignment_immutable
BEFORE UPDATE OR DELETE ON sw_police.career_rank_assignment
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_career_history_mutation();
CREATE TRIGGER career_post_appointment_immutable
BEFORE UPDATE OR DELETE ON sw_police.career_post_appointment
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_career_history_mutation();

CREATE FUNCTION sw_police.record_career_episode_opening()
RETURNS trigger LANGUAGE plpgsql AS $bp07$
BEGIN
  INSERT INTO sw_police.career_event(
    event_id,career_id,personnel_id,event_kind,resulting_stage,resulting_status,
    effective_tick,actor_ref,authority_ref,source_ref,reason
  ) VALUES (
    NEW.start_event_id,NEW.career_id,NEW.personnel_id,'career_opened',
    NEW.career_stage,NEW.career_status,NEW.started_tick,'domain:recruitment',
    'accepted-recruit-intake','BP07:career-open:'||NEW.career_id::text,
    'Initial career episode opened after accepted appointment'
  );
  RETURN NEW;
END
$bp07$;
CREATE TRIGGER career_episode_opening_event
AFTER INSERT ON sw_police.career_episode
FOR EACH ROW EXECUTE FUNCTION sw_police.record_career_episode_opening();

CREATE VIEW sw_police.career_current_rank AS
SELECT DISTINCT ON (career_id) career_id,personnel_id,rank_code,assignment_type,
       effective_from_tick,source_event_id,decision_ref
FROM sw_police.career_rank_assignment
WHERE effective_to_tick IS NULL
ORDER BY career_id,effective_from_tick DESC,rank_assignment_id;

CREATE VIEW sw_police.career_current_post AS
SELECT DISTINCT ON (career_id) career_id,personnel_id,post_id,position_id,
       appointment_type,effective_from_tick,source_event_id,authority_ref
FROM sw_police.career_post_appointment
WHERE effective_to_tick IS NULL
ORDER BY career_id,effective_from_tick DESC,position_appointment_id;

COMMIT;
