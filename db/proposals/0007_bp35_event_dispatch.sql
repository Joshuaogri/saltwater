-- BP35-01 deterministic event intake and dispatch.
-- Disposable PostgreSQL proposal only. NEVER apply to Neon without separate approval.
-- Apply after proposals 0002-0006 in a disposable database.
BEGIN;

CREATE TABLE sw_runtime.event_work (
  event_id bigint PRIMARY KEY REFERENCES sw_core.simulation_event(event_id),
  owner_domain text NOT NULL CHECK (owner_domain ~ '^[a-z][a-z0-9_]{1,47}$'),
  handler_key text NOT NULL CHECK (handler_key ~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'),
  handler_version integer NOT NULL CHECK (handler_version > 0),
  schema_version integer NOT NULL CHECK (schema_version > 0),
  due_tick bigint NOT NULL CHECK (due_tick >= 0),
  priority integer NOT NULL DEFAULT 0 CHECK (priority BETWEEN -1000 AND 1000),
  idempotency_key text NOT NULL UNIQUE CHECK (length(idempotency_key) BETWEEN 1 AND 128),
  actor_ref text CHECK (actor_ref IS NULL OR length(actor_ref) BETWEEN 1 AND 200),
  source_division text NOT NULL CHECK (source_division ~ '^[a-z][a-z0-9_]{1,47}$'),
  source_ref text CHECK (source_ref IS NULL OR length(source_ref) BETWEEN 1 AND 200),
  visibility_class text NOT NULL CHECK (visibility_class ~ '^[a-z][a-z0-9_]{1,47}$'),
  max_attempts smallint NOT NULL DEFAULT 3 CHECK (max_attempts BETWEEN 1 AND 100),
  status text NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending','claimed','completed','failed','quarantined')),
  attempt_count smallint NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
  retry_after_tick bigint NOT NULL DEFAULT 0 CHECK (retry_after_tick >= 0),
  claim_token uuid,
  outcome_ref text CHECK (outcome_ref IS NULL OR length(outcome_ref) BETWEEN 1 AND 200),
  last_error_code text CHECK (last_error_code IS NULL OR last_error_code ~ '^[a-z][a-z0-9_]{0,63}$'),
  created_tick bigint NOT NULL CHECK (created_tick >= 0),
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK ((status='claimed') = (claim_token IS NOT NULL)),
  CHECK (attempt_count <= max_attempts),
  CHECK ((status='completed') = (outcome_ref IS NOT NULL))
);
CREATE INDEX event_work_due_order_idx
  ON sw_runtime.event_work(due_tick, priority DESC, event_id)
  WHERE status IN ('pending','failed');
CREATE UNIQUE INDEX event_work_claim_token_uq
  ON sw_runtime.event_work(claim_token) WHERE claim_token IS NOT NULL;

CREATE TABLE sw_runtime.event_work_prerequisite (
  event_id bigint NOT NULL REFERENCES sw_runtime.event_work(event_id),
  prerequisite_event_id bigint NOT NULL REFERENCES sw_runtime.event_work(event_id),
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(event_id, prerequisite_event_id),
  CHECK(event_id <> prerequisite_event_id)
);
CREATE INDEX event_work_prerequisite_parent_idx
  ON sw_runtime.event_work_prerequisite(prerequisite_event_id,event_id);

CREATE TABLE sw_runtime.event_work_attempt (
  attempt_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  event_id bigint NOT NULL REFERENCES sw_runtime.event_work(event_id),
  attempt_no smallint NOT NULL CHECK (attempt_no > 0),
  attempt_status text NOT NULL CHECK (attempt_status IN
    ('claimed','completed','failed','quarantined')),
  world_tick bigint NOT NULL CHECK (world_tick >= 0),
  error_code text CHECK (error_code IS NULL OR error_code ~ '^[a-z][a-z0-9_]{0,63}$'),
  outcome_ref text CHECK (outcome_ref IS NULL OR length(outcome_ref) BETWEEN 1 AND 200),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(event_id,attempt_no,attempt_status)
);
CREATE INDEX event_work_attempt_event_idx
  ON sw_runtime.event_work_attempt(event_id,attempt_no,attempt_id);

CREATE FUNCTION sw_runtime.guard_event_work_write() RETURNS trigger
LANGUAGE plpgsql AS $bp35$
DECLARE runtime_row sw_runtime.state%ROWTYPE;
BEGIN
  SELECT * INTO runtime_row FROM sw_runtime.state WHERE singleton=1 FOR SHARE;
  IF NOT FOUND OR runtime_row.state <> 2 OR NOT runtime_row.player_present THEN
    RAISE EXCEPTION 'event work writes require running player-present runtime';
  END IF;
  IF TG_OP='INSERT' THEN
    IF NEW.created_tick <> runtime_row.world_tick OR NEW.due_tick < runtime_row.world_tick THEN
      RAISE EXCEPTION 'event work must use current committed world tick';
    END IF;
    RETURN NEW;
  END IF;
  IF ROW(NEW.event_id,NEW.owner_domain,NEW.handler_key,NEW.handler_version,
         NEW.schema_version,NEW.due_tick,NEW.priority,NEW.idempotency_key,
         NEW.actor_ref,NEW.source_division,NEW.source_ref,NEW.visibility_class,
         NEW.max_attempts,NEW.created_tick,NEW.created_at)
     IS DISTINCT FROM
     ROW(OLD.event_id,OLD.owner_domain,OLD.handler_key,OLD.handler_version,
         OLD.schema_version,OLD.due_tick,OLD.priority,OLD.idempotency_key,
         OLD.actor_ref,OLD.source_division,OLD.source_ref,OLD.visibility_class,
         OLD.max_attempts,OLD.created_tick,OLD.created_at) THEN
    RAISE EXCEPTION 'accepted event work identity and contract are immutable';
  END IF;
  IF NOT ((OLD.status IN ('pending','failed') AND NEW.status='claimed')
       OR (OLD.status='claimed' AND NEW.status IN ('completed','failed','quarantined'))) THEN
    RAISE EXCEPTION 'invalid event work lifecycle transition';
  END IF;
  IF NEW.status='claimed' AND NEW.attempt_count <> OLD.attempt_count+1 THEN
    RAISE EXCEPTION 'event work claim must increment attempts exactly once';
  END IF;
  IF NEW.status<>'claimed' AND NEW.claim_token IS NOT NULL THEN
    RAISE EXCEPTION 'only claimed event work may hold a claim token';
  END IF;
  RETURN NEW;
END
$bp35$;
CREATE TRIGGER event_work_write_guard
BEFORE INSERT OR UPDATE ON sw_runtime.event_work
FOR EACH ROW EXECUTE FUNCTION sw_runtime.guard_event_work_write();

CREATE FUNCTION sw_runtime.reject_event_work_delete() RETURNS trigger
LANGUAGE plpgsql AS $bp35$
BEGIN RAISE EXCEPTION 'event work is retained; deletion is prohibited'; END
$bp35$;
CREATE TRIGGER event_work_no_delete
BEFORE DELETE ON sw_runtime.event_work
FOR EACH ROW EXECUTE FUNCTION sw_runtime.reject_event_work_delete();

CREATE FUNCTION sw_runtime.reject_event_work_history_mutation() RETURNS trigger
LANGUAGE plpgsql AS $bp35$
BEGIN RAISE EXCEPTION 'event work history is append-only'; END
$bp35$;
CREATE TRIGGER event_work_attempt_immutable
BEFORE UPDATE OR DELETE ON sw_runtime.event_work_attempt
FOR EACH ROW EXECUTE FUNCTION sw_runtime.reject_event_work_history_mutation();
CREATE TRIGGER event_work_prerequisite_immutable
BEFORE UPDATE OR DELETE ON sw_runtime.event_work_prerequisite
FOR EACH ROW EXECUTE FUNCTION sw_runtime.reject_event_work_history_mutation();

CREATE FUNCTION sw_runtime.submit_event_work(
  p_event_code text,
  p_owner_domain text,
  p_handler_key text,
  p_handler_version integer,
  p_schema_version integer,
  p_due_tick bigint,
  p_priority integer,
  p_idempotency_key text,
  p_actor_ref text,
  p_source_division text,
  p_source_ref text,
  p_causation_event_id bigint,
  p_correlation_id uuid,
  p_visibility_class text,
  p_max_attempts integer
) RETURNS bigint
LANGUAGE plpgsql AS $bp35$
DECLARE
  runtime_row sw_runtime.state%ROWTYPE;
  prior sw_runtime.event_work%ROWTYPE;
  event_type smallint;
  prior_code text;
  prior_causation bigint;
  prior_correlation uuid;
  new_event_id bigint;
BEGIN
  SELECT * INTO runtime_row FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR runtime_row.state<>2 OR NOT runtime_row.player_present THEN
    RAISE EXCEPTION 'event intake requires running player-present runtime';
  END IF;
  IF p_event_code IS NULL OR p_event_code !~ '^[A-Z][A-Z0-9_]{1,63}$'
     OR p_owner_domain IS NULL OR p_owner_domain !~ '^[a-z][a-z0-9_]{1,47}$'
     OR p_handler_key IS NULL OR p_handler_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_handler_version IS NULL OR p_handler_version<1
     OR p_schema_version IS NULL OR p_schema_version<1
     OR p_due_tick IS NULL OR p_due_tick<runtime_row.world_tick
     OR p_priority IS NULL OR p_priority NOT BETWEEN -1000 AND 1000
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_source_division IS NULL OR p_source_division !~ '^[a-z][a-z0-9_]{1,47}$'
     OR p_visibility_class IS NULL OR p_visibility_class !~ '^[a-z][a-z0-9_]{1,47}$'
     OR (p_actor_ref IS NOT NULL AND length(p_actor_ref) NOT BETWEEN 1 AND 200)
     OR (p_source_ref IS NOT NULL AND length(p_source_ref) NOT BETWEEN 1 AND 200)
     OR p_max_attempts IS NULL OR p_max_attempts NOT BETWEEN 1 AND 100 THEN
    RAISE EXCEPTION 'invalid event work definition';
  END IF;
  SELECT * INTO prior FROM sw_runtime.event_work WHERE idempotency_key=p_idempotency_key;
  IF FOUND THEN
    SELECT et.event_code,se.causation_event_id,se.correlation_id
      INTO prior_code,prior_causation,prior_correlation
      FROM sw_core.simulation_event se
      JOIN sw_core.event_type et USING(event_type_id)
      WHERE se.event_id=prior.event_id;
    IF (prior_code,prior.owner_domain,prior.handler_key,prior.handler_version,
        prior.schema_version,prior.due_tick,prior.priority,prior.actor_ref,
        prior.source_division,prior.source_ref,prior.visibility_class,
        prior.max_attempts,prior_causation,prior_correlation)
       IS DISTINCT FROM
       (p_event_code,p_owner_domain,p_handler_key,p_handler_version,
        p_schema_version,p_due_tick,p_priority,p_actor_ref,p_source_division,
        p_source_ref,p_visibility_class,p_max_attempts,p_causation_event_id,p_correlation_id) THEN
      RAISE EXCEPTION 'event idempotency key conflicts with prior definition';
    END IF;
    RETURN prior.event_id;
  END IF;
  SELECT event_type_id INTO event_type FROM sw_core.event_type WHERE event_code=p_event_code;
  IF event_type IS NULL THEN RAISE EXCEPTION 'unregistered event type'; END IF;
  INSERT INTO sw_core.simulation_event(
    event_type_id,occurred_at,world_tick,causation_event_id,correlation_id,idempotency_key
  ) VALUES (
    event_type,now(),runtime_row.world_tick,p_causation_event_id,p_correlation_id,p_idempotency_key
  ) RETURNING event_id INTO new_event_id;
  INSERT INTO sw_runtime.event_work(
    event_id,owner_domain,handler_key,handler_version,schema_version,due_tick,priority,
    idempotency_key,actor_ref,source_division,source_ref,visibility_class,max_attempts,created_tick
  ) VALUES (
    new_event_id,p_owner_domain,p_handler_key,p_handler_version,p_schema_version,p_due_tick,p_priority,
    p_idempotency_key,p_actor_ref,p_source_division,p_source_ref,p_visibility_class,p_max_attempts,
    runtime_row.world_tick
  );
  UPDATE sw_runtime.state SET last_event_id=new_event_id WHERE singleton=1;
  RETURN new_event_id;
END
$bp35$;

CREATE FUNCTION sw_runtime.add_event_prerequisite(
  p_event_id bigint, p_prerequisite_event_id bigint
) RETURNS boolean
LANGUAGE plpgsql AS $bp35$
DECLARE runtime_row sw_runtime.state%ROWTYPE;
BEGIN
  SELECT * INTO runtime_row FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR runtime_row.state<>2 OR NOT runtime_row.player_present THEN
    RAISE EXCEPTION 'causal dependency writes require running player-present runtime';
  END IF;
  IF p_event_id=p_prerequisite_event_id
     OR NOT EXISTS(SELECT 1 FROM sw_runtime.event_work WHERE event_id=p_event_id)
     OR NOT EXISTS(SELECT 1 FROM sw_runtime.event_work WHERE event_id=p_prerequisite_event_id) THEN
    RAISE EXCEPTION 'causal prerequisite must reference two distinct accepted event work items';
  END IF;
  IF EXISTS (
    WITH RECURSIVE ancestors(event_id) AS (
      SELECT p_prerequisite_event_id
      UNION
      SELECT d.prerequisite_event_id
      FROM sw_runtime.event_work_prerequisite d
      JOIN ancestors a ON d.event_id=a.event_id
    )
    SELECT 1 FROM ancestors WHERE event_id=p_event_id
  ) THEN RAISE EXCEPTION 'causal prerequisite would create a cycle'; END IF;
  INSERT INTO sw_runtime.event_work_prerequisite(event_id,prerequisite_event_id)
  VALUES(p_event_id,p_prerequisite_event_id)
  ON CONFLICT DO NOTHING;
  RETURN true;
END
$bp35$;

CREATE FUNCTION sw_runtime.claim_due_event_work()
RETURNS TABLE(
  event_id bigint,event_code text,owner_domain text,handler_key text,
  handler_version integer,schema_version integer,due_tick bigint,priority integer,
  attempt_count integer,claim_token uuid,idempotency_key text,actor_ref text,
  source_division text,source_ref text,causation_event_id bigint,correlation_id uuid,
  visibility_class text,prerequisite_event_ids bigint[],max_attempts integer
)
LANGUAGE plpgsql AS $bp35$
DECLARE
  runtime_row sw_runtime.state%ROWTYPE;
  selected sw_runtime.event_work%ROWTYPE;
  selected_code text;
  token uuid;
  prerequisites bigint[];
BEGIN
  SELECT * INTO runtime_row FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR runtime_row.state<>2 OR NOT runtime_row.player_present THEN RETURN; END IF;
  SELECT ew.* INTO selected
  FROM sw_runtime.event_work ew
  WHERE ew.status IN ('pending','failed')
    AND ew.due_tick<=runtime_row.world_tick
    AND ew.retry_after_tick<=runtime_row.world_tick
    AND NOT EXISTS (
      SELECT 1 FROM sw_runtime.event_work_prerequisite dep
      JOIN sw_runtime.event_work parent ON parent.event_id=dep.prerequisite_event_id
      WHERE dep.event_id=ew.event_id AND parent.status<>'completed'
    )
  ORDER BY ew.due_tick ASC,ew.priority DESC,ew.event_id ASC
  LIMIT 1 FOR UPDATE SKIP LOCKED;
  IF NOT FOUND THEN RETURN; END IF;
  SELECT et.event_code INTO selected_code
    FROM sw_core.simulation_event se JOIN sw_core.event_type et USING(event_type_id)
    WHERE se.event_id=selected.event_id;
  SELECT COALESCE(array_agg(dep.prerequisite_event_id ORDER BY dep.prerequisite_event_id),ARRAY[]::bigint[])
    INTO prerequisites FROM sw_runtime.event_work_prerequisite dep
    WHERE dep.event_id=selected.event_id;
  token:=gen_random_uuid();
  UPDATE sw_runtime.event_work SET status='claimed',claim_token=token,
    attempt_count=attempt_count+1 WHERE event_id=selected.event_id;
  INSERT INTO sw_runtime.event_work_attempt(event_id,attempt_no,attempt_status,world_tick)
    VALUES(selected.event_id,selected.attempt_count+1,'claimed',runtime_row.world_tick);
  RETURN QUERY SELECT selected.event_id,selected_code,selected.owner_domain,
    selected.handler_key,selected.handler_version,selected.schema_version,selected.due_tick,
    selected.priority,selected.attempt_count+1,token,selected.idempotency_key,
    selected.actor_ref,selected.source_division,selected.source_ref,
    se.causation_event_id,se.correlation_id,selected.visibility_class,prerequisites,
    selected.max_attempts
    FROM sw_core.simulation_event se WHERE se.event_id=selected.event_id;
END
$bp35$;

CREATE FUNCTION sw_runtime.finish_event_work(
  p_event_id bigint,p_claim_token uuid,p_success boolean,p_outcome_ref text,
  p_error_code text,p_retry_after_tick bigint,p_retryable boolean
) RETURNS text
LANGUAGE plpgsql AS $bp35$
DECLARE
  runtime_row sw_runtime.state%ROWTYPE;
  selected sw_runtime.event_work%ROWTYPE;
  final_status text;
BEGIN
  SELECT * INTO runtime_row FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR runtime_row.state<>2 OR NOT runtime_row.player_present THEN
    RAISE EXCEPTION 'event dispatch is frozen outside running player-present state';
  END IF;
  IF p_success IS NULL OR p_retryable IS NULL THEN
    RAISE EXCEPTION 'dispatch outcome flags are required';
  END IF;
  SELECT * INTO selected FROM sw_runtime.event_work WHERE event_id=p_event_id FOR UPDATE;
  IF NOT FOUND OR selected.status<>'claimed'
     OR selected.claim_token IS DISTINCT FROM p_claim_token THEN
    RAISE EXCEPTION 'event claim token is stale or invalid';
  END IF;
  IF p_success THEN
    IF p_outcome_ref IS NULL OR length(p_outcome_ref) NOT BETWEEN 1 AND 200
       OR p_error_code IS NOT NULL OR p_retry_after_tick IS NOT NULL THEN
      RAISE EXCEPTION 'successful dispatch requires outcome reference only';
    END IF;
    final_status:='completed';
  ELSE
    IF p_error_code IS NULL OR p_error_code !~ '^[a-z][a-z0-9_]{0,63}$'
       OR p_retry_after_tick IS NULL OR p_retry_after_tick<runtime_row.world_tick
       OR p_outcome_ref IS NOT NULL THEN
      RAISE EXCEPTION 'failed dispatch requires safe error code and valid retry tick';
    END IF;
    IF p_retryable AND selected.attempt_count<selected.max_attempts THEN
      final_status:='failed';
    ELSE
      final_status:='quarantined';
    END IF;
  END IF;
  UPDATE sw_runtime.event_work SET status=final_status,claim_token=NULL,
    outcome_ref=p_outcome_ref,last_error_code=p_error_code,
    retry_after_tick=CASE WHEN final_status='failed' THEN p_retry_after_tick ELSE retry_after_tick END
    WHERE event_id=p_event_id;
  INSERT INTO sw_runtime.event_work_attempt(
    event_id,attempt_no,attempt_status,world_tick,error_code,outcome_ref
  ) VALUES(p_event_id,selected.attempt_count,final_status,runtime_row.world_tick,
           p_error_code,p_outcome_ref);
  RETURN final_status;
END
$bp35$;

REVOKE ALL ON sw_runtime.event_work,sw_runtime.event_work_prerequisite,
  sw_runtime.event_work_attempt FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_runtime.submit_event_work(text,text,text,integer,integer,bigint,integer,text,text,text,text,bigint,uuid,text,integer) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_runtime.add_event_prerequisite(bigint,bigint) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_runtime.claim_due_event_work() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_runtime.finish_event_work(bigint,uuid,boolean,text,text,bigint,boolean) FROM PUBLIC;

COMMIT;
