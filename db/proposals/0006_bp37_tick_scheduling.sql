-- BP37-01: canonical tick schedules. Disposable PostgreSQL proposal only.
-- Apply after proposals 0002-0005 in disposable test databases.
-- Do not apply to Neon or another authoritative database without separate approval.

BEGIN;

INSERT INTO sw_core.event_type(event_code, description) VALUES
  ('SCHEDULE_CREATED', 'A domain-owned tick schedule was registered'),
  ('SCHEDULE_COMPLETED', 'A due schedule action completed through its owner handler'),
  ('SCHEDULE_FAILED', 'A due schedule action failed through its owner handler')
ON CONFLICT (event_code) DO NOTHING;

CREATE TABLE sw_runtime.schedule (
  schedule_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  owner_domain text NOT NULL CHECK (owner_domain ~ '^[a-z][a-z0-9_]{1,47}$'),
  subject_ref text NOT NULL CHECK (length(subject_ref) BETWEEN 1 AND 128),
  due_tick bigint NOT NULL CHECK (due_tick >= 0),
  interval_ticks bigint CHECK (interval_ticks IS NULL OR interval_ticks > 0),
  priority integer NOT NULL DEFAULT 0 CHECK (priority BETWEEN -1000 AND 1000),
  expires_at_tick bigint CHECK (expires_at_tick IS NULL OR expires_at_tick >= due_tick),
  retry_after_tick bigint NOT NULL DEFAULT 0 CHECK (retry_after_tick >= 0),
  status text NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending','claimed','completed','failed','cancelled','expired')),
  attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
  claim_token uuid,
  claimed_at_tick bigint,
  completed_at_tick bigint,
  last_error_code text CHECK (last_error_code IS NULL OR length(last_error_code) <= 64),
  idempotency_key text NOT NULL UNIQUE CHECK (length(idempotency_key) BETWEEN 1 AND 128),
  created_tick bigint NOT NULL CHECK (created_tick >= 0),
  last_event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK ((status = 'claimed') = (claim_token IS NOT NULL)),
  CHECK ((status = 'claimed') = (claimed_at_tick IS NOT NULL)),
  CHECK ((status = 'completed') = (completed_at_tick IS NOT NULL))
);

CREATE INDEX schedule_due_order_idx
  ON sw_runtime.schedule(due_tick, priority DESC, schedule_id)
  WHERE status IN ('pending','failed');
CREATE INDEX schedule_owner_subject_idx
  ON sw_runtime.schedule(owner_domain, subject_ref, schedule_id);
CREATE UNIQUE INDEX schedule_claim_token_uq
  ON sw_runtime.schedule(claim_token) WHERE claim_token IS NOT NULL;

CREATE FUNCTION sw_runtime.create_schedule(
  p_owner_domain text,
  p_subject_ref text,
  p_due_tick bigint,
  p_interval_ticks bigint,
  p_priority integer,
  p_expires_at_tick bigint,
  p_idempotency_key text
) RETURNS bigint
LANGUAGE plpgsql AS $$
DECLARE
  runtime_row sw_runtime.state%ROWTYPE;
  prior sw_runtime.schedule%ROWTYPE;
  event_id bigint;
  new_id bigint;
BEGIN
  SELECT * INTO runtime_row FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR runtime_row.state <> 2 OR NOT runtime_row.player_present THEN
    RAISE EXCEPTION 'schedule registration requires running player-present runtime';
  END IF;
  IF p_owner_domain IS NULL OR p_owner_domain !~ '^[a-z][a-z0-9_]{1,47}$'
     OR p_subject_ref IS NULL OR length(p_subject_ref) NOT BETWEEN 1 AND 128
     OR p_due_tick < runtime_row.world_tick
     OR (p_interval_ticks IS NOT NULL AND p_interval_ticks <= 0)
     OR p_priority NOT BETWEEN -1000 AND 1000
     OR (p_expires_at_tick IS NOT NULL AND p_expires_at_tick < p_due_tick)
     OR p_idempotency_key IS NULL OR length(p_idempotency_key) NOT BETWEEN 1 AND 128 THEN
    RAISE EXCEPTION 'invalid schedule definition';
  END IF;

  SELECT * INTO prior FROM sw_runtime.schedule
    WHERE idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF (prior.owner_domain, prior.subject_ref, prior.due_tick,
        prior.interval_ticks, prior.priority, prior.expires_at_tick)
       IS DISTINCT FROM
       (p_owner_domain, p_subject_ref, p_due_tick,
        p_interval_ticks, p_priority, p_expires_at_tick) THEN
      RAISE EXCEPTION 'schedule idempotency key conflicts with prior definition';
    END IF;
    RETURN prior.schedule_id;
  END IF;

  event_id := sw_runtime.insert_schedule_event(
    'SCHEDULE_CREATED', runtime_row.world_tick, 'schedule:create:' || p_idempotency_key
  );
  INSERT INTO sw_runtime.schedule(
    owner_domain, subject_ref, due_tick, interval_ticks, priority,
    expires_at_tick, idempotency_key, created_tick, last_event_id
  ) VALUES (
    p_owner_domain, p_subject_ref, p_due_tick, p_interval_ticks, p_priority,
    p_expires_at_tick, p_idempotency_key, runtime_row.world_tick, event_id
  ) RETURNING schedule_id INTO new_id;
  RETURN new_id;
END
$$;

CREATE FUNCTION sw_runtime.insert_schedule_event(
  p_event_code text, p_tick bigint, p_idempotency_key text
) RETURNS bigint
LANGUAGE plpgsql AS $$
DECLARE
  type_id smallint;
  new_event_id bigint;
BEGIN
  SELECT event_type_id INTO type_id FROM sw_core.event_type WHERE event_code=p_event_code;
  IF type_id IS NULL THEN RAISE EXCEPTION 'schedule event type is missing'; END IF;
  INSERT INTO sw_core.simulation_event(
    event_type_id, occurred_at, world_tick, idempotency_key
  ) VALUES (type_id, now(), p_tick, p_idempotency_key)
  RETURNING event_id INTO new_event_id;
  UPDATE sw_runtime.state SET last_event_id=new_event_id WHERE singleton=1;
  RETURN new_event_id;
END
$$;

CREATE FUNCTION sw_runtime.claim_due_schedule()
RETURNS TABLE(
  schedule_id bigint, owner_domain text, subject_ref text, due_tick bigint,
  interval_ticks bigint, priority integer, attempt_count integer,
  claim_token uuid, idempotency_key text
)
LANGUAGE plpgsql AS $$
DECLARE
  runtime_row sw_runtime.state%ROWTYPE;
  selected sw_runtime.schedule%ROWTYPE;
  token uuid;
BEGIN
  SELECT * INTO runtime_row FROM sw_runtime.state WHERE singleton=1 FOR SHARE;
  IF NOT FOUND OR runtime_row.state <> 2 OR NOT runtime_row.player_present THEN
    RETURN;
  END IF;

  SELECT * INTO selected
  FROM sw_runtime.schedule s
  WHERE s.status IN ('pending','failed')
    AND s.due_tick <= runtime_row.world_tick
    AND s.retry_after_tick <= runtime_row.world_tick
    AND (s.expires_at_tick IS NULL OR s.expires_at_tick >= runtime_row.world_tick)
  ORDER BY s.due_tick ASC, s.priority DESC, s.schedule_id ASC
  LIMIT 1
  FOR UPDATE SKIP LOCKED;

  IF NOT FOUND THEN
    UPDATE sw_runtime.schedule SET status='expired', claim_token=NULL,
      claimed_at_tick=NULL
    WHERE status IN ('pending','failed')
      AND expires_at_tick IS NOT NULL
      AND expires_at_tick < runtime_row.world_tick;
    RETURN;
  END IF;

  token := gen_random_uuid();
  UPDATE sw_runtime.schedule s SET status='claimed',
    claim_token=token, claimed_at_tick=runtime_row.world_tick,
    attempt_count=s.attempt_count+1
  WHERE s.schedule_id=selected.schedule_id;

  RETURN QUERY SELECT selected.schedule_id, selected.owner_domain,
    selected.subject_ref, selected.due_tick, selected.interval_ticks,
    selected.priority, selected.attempt_count+1, token, selected.idempotency_key;
END
$$;

CREATE FUNCTION sw_runtime.finish_schedule(
  p_schedule_id bigint,
  p_claim_token uuid,
  p_success boolean,
  p_retry_after_tick bigint DEFAULT NULL,
  p_error_code text DEFAULT NULL
) RETURNS boolean
LANGUAGE plpgsql AS $$
DECLARE
  runtime_row sw_runtime.state%ROWTYPE;
  selected sw_runtime.schedule%ROWTYPE;
  event_id bigint;
BEGIN
  SELECT * INTO runtime_row FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR runtime_row.state <> 2 OR NOT runtime_row.player_present THEN
    RAISE EXCEPTION 'schedule dispatch is frozen outside running player-present state';
  END IF;

  SELECT * INTO selected FROM sw_runtime.schedule
    WHERE schedule_id=p_schedule_id FOR UPDATE;
  IF NOT FOUND OR selected.status <> 'claimed'
     OR selected.claim_token IS DISTINCT FROM p_claim_token THEN
    RETURN false;
  END IF;

  IF p_success THEN
    IF selected.interval_ticks IS NULL THEN
      event_id := sw_runtime.insert_schedule_event(
        'SCHEDULE_COMPLETED', runtime_row.world_tick,
        'schedule:complete:' || selected.schedule_id::text || ':' || selected.attempt_count::text
      );
      UPDATE sw_runtime.schedule SET status='completed',
        completed_at_tick=runtime_row.world_tick, claim_token=NULL,
        claimed_at_tick=NULL, last_event_id=event_id,
        last_error_code=NULL
      WHERE schedule_id=p_schedule_id;
    ELSE
      event_id := sw_runtime.insert_schedule_event(
        'SCHEDULE_COMPLETED', runtime_row.world_tick,
        'schedule:complete:' || selected.schedule_id::text || ':' || selected.attempt_count::text
      );
      UPDATE sw_runtime.schedule SET status='pending',
        due_tick=runtime_row.world_tick + selected.interval_ticks,
        retry_after_tick=0, claim_token=NULL, claimed_at_tick=NULL,
        last_event_id=event_id, last_error_code=NULL,
        expires_at_tick=selected.expires_at_tick
      WHERE schedule_id=p_schedule_id;
    END IF;
  ELSE
    IF p_error_code IS NULL OR length(p_error_code) NOT BETWEEN 1 AND 64
       OR p_retry_after_tick IS NULL OR p_retry_after_tick < runtime_row.world_tick THEN
      RAISE EXCEPTION 'failed schedule requires bounded error code and retry tick';
    END IF;
    event_id := sw_runtime.insert_schedule_event(
      'SCHEDULE_FAILED', runtime_row.world_tick,
      'schedule:failed:' || selected.schedule_id::text || ':' || selected.attempt_count::text
    );
    UPDATE sw_runtime.schedule SET status='failed',
      retry_after_tick=p_retry_after_tick, claim_token=NULL,
      claimed_at_tick=NULL, last_event_id=event_id,
      last_error_code=p_error_code
    WHERE schedule_id=p_schedule_id;
  END IF;
  RETURN true;
END
$$;

COMMIT;
