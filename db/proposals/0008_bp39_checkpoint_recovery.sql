-- BP39-01 consistent checkpoint manifest and controlled BP35 claim recovery.
-- Disposable PostgreSQL proposal only. Never apply to Neon without separate approval.
-- Apply after proposals 0002-0007.

BEGIN;

CREATE TABLE sw_runtime.checkpoint_manifest (
  checkpoint_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  format_version smallint NOT NULL DEFAULT 1 CHECK (format_version=1),
  source_environment text NOT NULL CHECK (length(source_environment) BETWEEN 1 AND 80),
  source_project text NOT NULL CHECK (length(source_project) BETWEEN 1 AND 120),
  source_branch text NOT NULL CHECK (length(source_branch) BETWEEN 1 AND 120),
  source_database text NOT NULL CHECK (length(source_database) BETWEEN 1 AND 120),
  schema_watermark integer NOT NULL CHECK (schema_watermark >= 0),
  runtime_state smallint NOT NULL CHECK (runtime_state BETWEEN 0 AND 5),
  player_present boolean NOT NULL,
  world_tick bigint NOT NULL CHECK (world_tick >= 0),
  last_event_id bigint,
  event_count bigint NOT NULL CHECK (event_count >= 0),
  event_work_counts jsonb NOT NULL,
  schedule_counts jsonb NOT NULL,
  population_count integer,
  business_count bigint,
  consistency_boundary text NOT NULL DEFAULT 'repeatable_read' CHECK (consistency_boundary='repeatable_read'),
  manifest_digest text NOT NULL CHECK (manifest_digest ~ '^[0-9a-f]{32}$'),
  validation_state text NOT NULL DEFAULT 'captured'
    CHECK (validation_state IN ('captured','validated','failed')),
  actor_ref text NOT NULL CHECK (length(actor_ref) BETWEEN 1 AND 200),
  approval_ref text NOT NULL CHECK (length(approval_ref) BETWEEN 1 AND 200),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX checkpoint_manifest_created_idx
  ON sw_runtime.checkpoint_manifest(created_at DESC,checkpoint_id);

CREATE TABLE sw_runtime.event_claim_recovery (
  recovery_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  recovery_key text NOT NULL UNIQUE CHECK (length(recovery_key) BETWEEN 1 AND 128),
  event_id bigint NOT NULL REFERENCES sw_runtime.event_work(event_id),
  prior_claim_token uuid NOT NULL,
  decision text NOT NULL CHECK (decision IN ('effect_committed','effect_absent','indeterminate')),
  owner_domain text NOT NULL CHECK (owner_domain ~ '^[a-z][a-z0-9_]{1,47}$'),
  owner_response_ref text NOT NULL CHECK (length(owner_response_ref) BETWEEN 1 AND 200),
  outcome_ref text CHECK (outcome_ref IS NULL OR length(outcome_ref) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(actor_ref) BETWEEN 1 AND 200),
  approval_ref text NOT NULL CHECK (length(approval_ref) BETWEEN 1 AND 200),
  reason_code text NOT NULL CHECK (reason_code ~ '^[a-z][a-z0-9_]{0,63}$'),
  checkpoint_id uuid REFERENCES sw_runtime.checkpoint_manifest(checkpoint_id),
  world_tick bigint NOT NULL CHECK (world_tick >= 0),
  resulting_status text NOT NULL CHECK (resulting_status IN ('completed','failed','quarantined')),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX event_claim_recovery_event_idx
  ON sw_runtime.event_claim_recovery(event_id,recovery_id);

CREATE OR REPLACE FUNCTION sw_runtime.guard_event_work_write() RETURNS trigger
LANGUAGE plpgsql AS $bp39$
DECLARE runtime_row sw_runtime.state%ROWTYPE;
  recovery_mode boolean := current_setting('sw_runtime.recovery_authorized',true)='on';
BEGIN
  SELECT * INTO runtime_row FROM sw_runtime.state WHERE singleton=1 FOR SHARE;
  IF NOT FOUND OR NOT (
    (runtime_row.state=2 AND runtime_row.player_present)
    OR (recovery_mode AND runtime_row.state=4 AND NOT runtime_row.player_present)
  ) THEN
    RAISE EXCEPTION 'event work writes require running runtime or authorised recovery';
  END IF;
  IF TG_OP='INSERT' THEN
    IF recovery_mode OR NEW.created_tick <> runtime_row.world_tick
       OR NEW.due_tick < runtime_row.world_tick THEN
      RAISE EXCEPTION 'event work intake requires current running world tick';
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
  IF recovery_mode AND runtime_row.state=4
     AND ((OLD.status='claimed' AND NEW.status IN ('completed','failed','quarantined'))
       OR (OLD.status='quarantined' AND NEW.status IN ('completed','failed'))) THEN
    IF NEW.claim_token IS NOT NULL OR NEW.attempt_count<>OLD.attempt_count THEN
      RAISE EXCEPTION 'recovery must clear claim token without changing attempt count';
    END IF;
    RETURN NEW;
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
$bp39$;

CREATE OR REPLACE FUNCTION sw_runtime.guard_event_work_pause() RETURNS trigger
LANGUAGE plpgsql AS $bp39$
BEGIN
  IF OLD.state=2 AND (NEW.state<>2 OR NOT NEW.player_present)
     AND EXISTS(SELECT 1 FROM sw_runtime.event_work WHERE status='claimed')
     AND NOT (NEW.state=4 AND NOT NEW.player_present
              AND current_setting('sw_runtime.recovery_authorized',true)='on') THEN
    RAISE EXCEPTION 'pause waits for active event dispatch to finish';
  END IF;
  RETURN NEW;
END
$bp39$;

CREATE FUNCTION sw_runtime.begin_event_claim_recovery(
  p_actor_ref text,p_approval_ref text
) RETURNS bigint
LANGUAGE plpgsql AS $bp39$
DECLARE state_row sw_runtime.state%ROWTYPE;
BEGIN
  IF p_actor_ref IS NULL OR length(p_actor_ref) NOT BETWEEN 1 AND 200
     OR p_approval_ref IS NULL OR length(p_approval_ref) NOT BETWEEN 1 AND 200 THEN
    RAISE EXCEPTION 'recovery actor and approval references are required';
  END IF;
  SELECT * INTO state_row FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR state_row.state NOT IN (2,3) THEN
    RAISE EXCEPTION 'recovery requires running or paused runtime';
  END IF;
  IF NOT EXISTS(SELECT 1 FROM sw_runtime.event_work WHERE status='claimed') THEN
    RAISE EXCEPTION 'no abandoned event claims require recovery';
  END IF;
  PERFORM set_config('sw_runtime.recovery_authorized','on',true);
  UPDATE sw_runtime.state SET state=4,player_present=false WHERE singleton=1;
  RETURN state_row.world_tick;
END
$bp39$;

CREATE FUNCTION sw_runtime.reconcile_event_claim(
  p_event_id bigint,p_claim_token uuid,p_decision text,p_owner_domain text,
  p_owner_response_ref text,p_outcome_ref text,p_actor_ref text,p_approval_ref text,
  p_reason_code text,p_recovery_key text,p_checkpoint_id uuid DEFAULT NULL
) RETURNS text
LANGUAGE plpgsql AS $bp39$
DECLARE
  state_row sw_runtime.state%ROWTYPE;
  work_row sw_runtime.event_work%ROWTYPE;
  prior sw_runtime.event_claim_recovery%ROWTYPE;
  final_status text;
BEGIN
  SELECT * INTO state_row FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR state_row.state<>4 OR state_row.player_present THEN
    RAISE EXCEPTION 'claim reconciliation requires frozen recovering runtime';
  END IF;
  IF p_recovery_key IS NULL OR length(p_recovery_key) NOT BETWEEN 1 AND 128
     OR p_decision IS NULL OR p_decision NOT IN ('effect_committed','effect_absent','indeterminate')
     OR p_owner_domain IS NULL OR p_owner_domain !~ '^[a-z][a-z0-9_]{1,47}$'
     OR p_owner_response_ref IS NULL OR length(p_owner_response_ref) NOT BETWEEN 1 AND 200
     OR p_actor_ref IS NULL OR length(p_actor_ref) NOT BETWEEN 1 AND 200
     OR p_approval_ref IS NULL OR length(p_approval_ref) NOT BETWEEN 1 AND 200
     OR p_reason_code IS NULL OR p_reason_code !~ '^[a-z][a-z0-9_]{0,63}$' THEN
    RAISE EXCEPTION 'invalid recovery decision or missing provenance';
  END IF;
  SELECT * INTO prior FROM sw_runtime.event_claim_recovery WHERE recovery_key=p_recovery_key;
  IF FOUND THEN
    IF (prior.event_id,prior.prior_claim_token,prior.decision,prior.owner_domain,
        prior.owner_response_ref,prior.outcome_ref,prior.actor_ref,prior.approval_ref,
        prior.reason_code,prior.checkpoint_id)
       IS DISTINCT FROM
       (p_event_id,p_claim_token,p_decision,p_owner_domain,p_owner_response_ref,
        p_outcome_ref,p_actor_ref,p_approval_ref,p_reason_code,p_checkpoint_id) THEN
      RAISE EXCEPTION 'recovery key conflicts with prior decision';
    END IF;
    RETURN prior.resulting_status;
  END IF;
  SELECT * INTO work_row FROM sw_runtime.event_work
    WHERE event_id=p_event_id FOR UPDATE;
  IF NOT FOUND OR work_row.status<>'claimed'
     OR work_row.claim_token IS DISTINCT FROM p_claim_token THEN
    RAISE EXCEPTION 'claimed event or claim token is stale';
  END IF;
  IF work_row.owner_domain<>p_owner_domain THEN
    RAISE EXCEPTION 'reconciliation owner does not match event owner domain';
  END IF;
  IF p_decision='effect_committed' THEN
    IF p_outcome_ref IS NULL OR length(p_outcome_ref) NOT BETWEEN 1 AND 200 THEN
      RAISE EXCEPTION 'committed effect requires durable owner outcome reference';
    END IF;
    final_status:='completed';
  ELSIF p_decision='effect_absent' THEN
    IF p_outcome_ref IS NOT NULL THEN
      RAISE EXCEPTION 'absent effect cannot carry an outcome reference';
    END IF;
    final_status:='failed';
  ELSE
    IF p_outcome_ref IS NOT NULL THEN
      RAISE EXCEPTION 'indeterminate effect cannot carry an outcome reference';
    END IF;
    final_status:='quarantined';
  END IF;
  PERFORM set_config('sw_runtime.recovery_authorized','on',true);
  UPDATE sw_runtime.event_work SET status=final_status,claim_token=NULL,
    outcome_ref=p_outcome_ref,
    last_error_code=CASE WHEN final_status='failed' THEN 'recovery_effect_absent'
                         WHEN final_status='quarantined' THEN 'recovery_indeterminate' ELSE NULL END,
    retry_after_tick=CASE WHEN final_status='failed' THEN state_row.world_tick ELSE retry_after_tick END
    WHERE event_id=p_event_id;
  INSERT INTO sw_runtime.event_work_attempt(
    event_id,attempt_no,attempt_status,world_tick,error_code,outcome_ref
  ) VALUES(p_event_id,work_row.attempt_count,final_status,state_row.world_tick,
    CASE WHEN final_status='failed' THEN 'recovery_effect_absent'
         WHEN final_status='quarantined' THEN 'recovery_indeterminate' ELSE NULL END,
    p_outcome_ref);
  INSERT INTO sw_runtime.event_claim_recovery(
    recovery_key,event_id,prior_claim_token,decision,owner_domain,owner_response_ref,
    outcome_ref,actor_ref,approval_ref,reason_code,checkpoint_id,world_tick,resulting_status
  ) VALUES(
    p_recovery_key,p_event_id,p_claim_token,p_decision,p_owner_domain,p_owner_response_ref,
    p_outcome_ref,p_actor_ref,p_approval_ref,p_reason_code,p_checkpoint_id,
    state_row.world_tick,final_status
  );
  RETURN final_status;
END
$bp39$;

CREATE FUNCTION sw_runtime.resolve_quarantined_event_claim(
  p_event_id bigint,p_original_claim_token uuid,p_decision text,p_owner_domain text,
  p_owner_response_ref text,p_outcome_ref text,p_actor_ref text,p_approval_ref text,
  p_reason_code text,p_recovery_key text,p_checkpoint_id uuid DEFAULT NULL
) RETURNS text
LANGUAGE plpgsql AS $bp39$
DECLARE
  state_row sw_runtime.state%ROWTYPE;
  work_row sw_runtime.event_work%ROWTYPE;
  prior sw_runtime.event_claim_recovery%ROWTYPE;
  existing sw_runtime.event_claim_recovery%ROWTYPE;
  final_status text;
BEGIN
  SELECT * INTO state_row FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR state_row.state<>4 OR state_row.player_present THEN
    RAISE EXCEPTION 'quarantine resolution requires frozen recovering runtime';
  END IF;
  IF p_decision IS NULL OR p_decision NOT IN ('effect_committed','effect_absent')
     OR p_owner_domain IS NULL OR p_owner_domain !~ '^[a-z][a-z0-9_]{1,47}$'
     OR p_owner_response_ref IS NULL OR length(p_owner_response_ref) NOT BETWEEN 1 AND 200
     OR p_actor_ref IS NULL OR length(p_actor_ref) NOT BETWEEN 1 AND 200
     OR p_approval_ref IS NULL OR length(p_approval_ref) NOT BETWEEN 1 AND 200
     OR p_reason_code IS NULL OR p_reason_code !~ '^[a-z][a-z0-9_]{0,63}$'
     OR p_recovery_key IS NULL OR length(p_recovery_key) NOT BETWEEN 1 AND 128 THEN
    RAISE EXCEPTION 'invalid quarantine resolution or missing provenance';
  END IF;
  SELECT * INTO existing FROM sw_runtime.event_claim_recovery WHERE recovery_key=p_recovery_key;
  IF FOUND THEN
    IF (existing.event_id,existing.prior_claim_token,existing.decision,existing.owner_domain,
        existing.owner_response_ref,existing.outcome_ref,existing.actor_ref,existing.approval_ref,
        existing.reason_code,existing.checkpoint_id)
       IS DISTINCT FROM
       (p_event_id,p_original_claim_token,p_decision,p_owner_domain,p_owner_response_ref,
        p_outcome_ref,p_actor_ref,p_approval_ref,p_reason_code,p_checkpoint_id) THEN
      RAISE EXCEPTION 'quarantine resolution key conflicts with prior decision';
    END IF;
    RETURN existing.resulting_status;
  END IF;
  SELECT * INTO prior FROM sw_runtime.event_claim_recovery
    WHERE event_id=p_event_id AND prior_claim_token=p_original_claim_token
      AND decision='indeterminate'
    ORDER BY recovery_id DESC LIMIT 1;
  IF NOT FOUND THEN RAISE EXCEPTION 'no matching indeterminate recovery record exists'; END IF;
  SELECT * INTO work_row FROM sw_runtime.event_work WHERE event_id=p_event_id FOR UPDATE;
  IF NOT FOUND OR work_row.status<>'quarantined'
     OR work_row.owner_domain<>p_owner_domain THEN
    RAISE EXCEPTION 'quarantined work or owner does not match resolution';
  END IF;
  IF p_decision='effect_committed' THEN
    IF p_outcome_ref IS NULL OR length(p_outcome_ref) NOT BETWEEN 1 AND 200 THEN
      RAISE EXCEPTION 'committed effect requires durable owner outcome reference';
    END IF;
    final_status:='completed';
  ELSE
    IF p_outcome_ref IS NOT NULL THEN
      RAISE EXCEPTION 'absent effect cannot carry an outcome reference';
    END IF;
    final_status:='failed';
  END IF;
  PERFORM set_config('sw_runtime.recovery_authorized','on',true);
  UPDATE sw_runtime.event_work SET status=final_status,claim_token=NULL,
    outcome_ref=p_outcome_ref,
    last_error_code=CASE WHEN final_status='failed' THEN 'recovery_effect_absent' ELSE NULL END,
    retry_after_tick=CASE WHEN final_status='failed' THEN state_row.world_tick ELSE retry_after_tick END
    WHERE event_id=p_event_id;
  INSERT INTO sw_runtime.event_work_attempt(
    event_id,attempt_no,attempt_status,world_tick,error_code,outcome_ref
  ) VALUES(p_event_id,work_row.attempt_count,final_status,state_row.world_tick,
    CASE WHEN final_status='failed' THEN 'recovery_effect_absent' ELSE NULL END,p_outcome_ref);
  INSERT INTO sw_runtime.event_claim_recovery(
    recovery_key,event_id,prior_claim_token,decision,owner_domain,owner_response_ref,
    outcome_ref,actor_ref,approval_ref,reason_code,checkpoint_id,world_tick,resulting_status
  ) VALUES(
    p_recovery_key,p_event_id,p_original_claim_token,p_decision,p_owner_domain,
    p_owner_response_ref,p_outcome_ref,p_actor_ref,p_approval_ref,p_reason_code,
    p_checkpoint_id,state_row.world_tick,final_status
  );
  RETURN final_status;
END
$bp39$;

CREATE FUNCTION sw_runtime.finish_event_claim_recovery() RETURNS boolean
LANGUAGE plpgsql AS $bp39$
DECLARE state_row sw_runtime.state%ROWTYPE;
BEGIN
  SELECT * INTO state_row FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR state_row.state<>4 OR state_row.player_present THEN
    RAISE EXCEPTION 'runtime is not in frozen recovery state';
  END IF;
  IF EXISTS(SELECT 1 FROM sw_runtime.event_work WHERE status IN ('claimed','quarantined')) THEN
    RAISE EXCEPTION 'unresolved or quarantined event claims block recovery completion';
  END IF;
  PERFORM set_config('sw_runtime.recovery_authorized','on',true);
  UPDATE sw_runtime.state SET state=1,player_present=false WHERE singleton=1;
  PERFORM set_config('sw_runtime.recovery_authorized','off',true);
  RETURN true;
END
$bp39$;

CREATE FUNCTION sw_runtime.count_canonical_businesses() RETURNS bigint
LANGUAGE plpgsql STABLE AS $bp39$
DECLARE r record; total bigint:=0; tables_found integer:=0; n bigint;
BEGIN
  FOR r IN SELECT table_schema,table_name FROM information_schema.tables
    WHERE table_schema NOT IN ('pg_catalog','information_schema') AND table_name='business'
  LOOP
    tables_found:=tables_found+1;
    EXECUTE format('SELECT count(*) FROM %I.%I',r.table_schema,r.table_name) INTO n;
    total:=total+n;
  END LOOP;
  IF tables_found=0 THEN RETURN NULL; END IF;
  RETURN total;
END
$bp39$;

CREATE FUNCTION sw_runtime.reject_recovery_audit_mutation() RETURNS trigger
LANGUAGE plpgsql AS $bp39$
BEGIN RAISE EXCEPTION 'event claim recovery audit is append-only'; END
$bp39$;
CREATE TRIGGER event_claim_recovery_immutable
BEFORE UPDATE OR DELETE ON sw_runtime.event_claim_recovery
FOR EACH ROW EXECUTE FUNCTION sw_runtime.reject_recovery_audit_mutation();

CREATE FUNCTION sw_runtime.capture_checkpoint_manifest(
  p_source_environment text,p_source_project text,p_source_branch text,
  p_source_database text,p_actor_ref text,p_approval_ref text
) RETURNS uuid
LANGUAGE plpgsql AS $bp39$
DECLARE
  state_row sw_runtime.state%ROWTYPE;
  schema_mark integer;
  event_total bigint;
  event_watermark bigint;
  work_counts jsonb;
  sched_counts jsonb;
  people_total integer;
  business_total bigint;
  digest_value text;
  new_id uuid:=gen_random_uuid();
BEGIN
  IF current_setting('transaction_isolation') NOT IN ('repeatable read','serializable') THEN
    RAISE EXCEPTION 'checkpoint capture requires repeatable read or serializable transaction';
  END IF;
  IF p_source_environment IS NULL OR length(p_source_environment) NOT BETWEEN 1 AND 80
     OR p_source_project IS NULL OR length(p_source_project) NOT BETWEEN 1 AND 120
     OR p_source_branch IS NULL OR length(p_source_branch) NOT BETWEEN 1 AND 120
     OR p_source_database IS NULL OR length(p_source_database) NOT BETWEEN 1 AND 120
     OR p_actor_ref IS NULL OR length(p_actor_ref) NOT BETWEEN 1 AND 200
     OR p_approval_ref IS NULL OR length(p_approval_ref) NOT BETWEEN 1 AND 200 THEN
    RAISE EXCEPTION 'checkpoint source identity, actor and approval are required';
  END IF;
  SELECT * INTO state_row FROM sw_runtime.state WHERE singleton=1;
  IF NOT FOUND THEN RAISE EXCEPTION 'runtime singleton is missing'; END IF;
  SELECT COALESCE(max(version),0) INTO schema_mark FROM sw_ops.schema_migration;
  SELECT count(*),max(event_id) INTO event_total,event_watermark FROM sw_core.simulation_event;
  SELECT COALESCE(jsonb_object_agg(status,n),'{}'::jsonb) INTO work_counts
    FROM (SELECT status,count(*) n FROM sw_runtime.event_work GROUP BY status) q;
  SELECT COALESCE(jsonb_object_agg(status,n),'{}'::jsonb) INTO sched_counts
    FROM (SELECT status,count(*) n FROM sw_runtime.schedule GROUP BY status) q;
  SELECT living_included INTO people_total FROM sw_people.population_counter WHERE singleton=1;
  business_total:=sw_runtime.count_canonical_businesses();
  digest_value:=md5(concat_ws('|',new_id::text,1,p_source_environment,p_source_project,
    p_source_branch,p_source_database,schema_mark,state_row.state,state_row.player_present,
    state_row.world_tick,state_row.last_event_id,event_total,event_watermark,
    work_counts::text,sched_counts::text,people_total,business_total,'repeatable_read',
    p_actor_ref,p_approval_ref));
  INSERT INTO sw_runtime.checkpoint_manifest(
    checkpoint_id,source_environment,source_project,source_branch,source_database,
    schema_watermark,runtime_state,player_present,world_tick,last_event_id,event_count,
    event_work_counts,schedule_counts,population_count,business_count,manifest_digest,
    actor_ref,approval_ref
  ) VALUES (
    new_id,p_source_environment,p_source_project,p_source_branch,p_source_database,
    schema_mark,state_row.state,state_row.player_present,state_row.world_tick,
    state_row.last_event_id,event_total,work_counts,sched_counts,people_total,
    business_total,digest_value,p_actor_ref,p_approval_ref
  );
  RETURN new_id;
END
$bp39$;

CREATE FUNCTION sw_runtime.validate_checkpoint_manifest(p_checkpoint_id uuid)
RETURNS jsonb
LANGUAGE plpgsql AS $bp39$
DECLARE m sw_runtime.checkpoint_manifest%ROWTYPE;
  s sw_runtime.state%ROWTYPE;
  schema_now integer;
  event_now bigint;
  event_max bigint;
  work_now jsonb;
  sched_now jsonb;
  people_now integer;
  business_total bigint;
  gates jsonb;
  ok boolean;
BEGIN
  SELECT * INTO m FROM sw_runtime.checkpoint_manifest WHERE checkpoint_id=p_checkpoint_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'checkpoint manifest does not exist'; END IF;
  SELECT * INTO s FROM sw_runtime.state WHERE singleton=1;
  SELECT COALESCE(max(version),0) INTO schema_now FROM sw_ops.schema_migration;
  SELECT count(*),max(event_id) INTO event_now,event_max FROM sw_core.simulation_event;
  SELECT COALESCE(jsonb_object_agg(status,n),'{}'::jsonb) INTO work_now
    FROM (SELECT status,count(*) n FROM sw_runtime.event_work GROUP BY status) q;
  SELECT COALESCE(jsonb_object_agg(status,n),'{}'::jsonb) INTO sched_now
    FROM (SELECT status,count(*) n FROM sw_runtime.schedule GROUP BY status) q;
  SELECT living_included INTO people_now FROM sw_people.population_counter WHERE singleton=1;
  business_total:=sw_runtime.count_canonical_businesses();
  gates:=jsonb_build_object(
    'schema_watermark',jsonb_build_object('status',CASE WHEN schema_now=m.schema_watermark THEN 'pass' ELSE 'fail' END),
    'runtime_and_tick',jsonb_build_object('status',CASE WHEN s.state=m.runtime_state AND s.player_present=m.player_present AND s.world_tick=m.world_tick THEN 'pass' ELSE 'fail' END),
    'event_watermark',jsonb_build_object('status',CASE WHEN event_now=m.event_count AND event_max IS NOT DISTINCT FROM m.last_event_id THEN 'pass' ELSE 'fail' END),
    'event_work',jsonb_build_object('status',CASE WHEN work_now=m.event_work_counts THEN 'pass' ELSE 'fail' END),
    'schedules',jsonb_build_object('status',CASE WHEN sched_now=m.schedule_counts THEN 'pass' ELSE 'fail' END),
    'population_cap',jsonb_build_object('status',CASE WHEN people_now=m.population_count AND people_now<=10000 THEN 'pass' ELSE 'fail' END),
    'business_minimum',jsonb_build_object('status',CASE WHEN business_total IS NULL THEN 'not_executed' WHEN business_total>=10000 AND business_total=m.business_count THEN 'pass' ELSE 'fail' END),
    'manifest_identity',jsonb_build_object('status',CASE WHEN m.manifest_digest=md5(concat_ws('|',m.checkpoint_id::text,m.format_version,m.source_environment,m.source_project,m.source_branch,m.source_database,m.schema_watermark,m.runtime_state,m.player_present,m.world_tick,m.last_event_id,m.event_count,m.event_work_counts::text,m.schedule_counts::text,m.population_count,m.business_count,'repeatable_read',m.actor_ref,m.approval_ref)) THEN 'pass' ELSE 'fail' END),
    'structural_integrity',jsonb_build_object('status',CASE WHEN NOT EXISTS(SELECT 1 FROM pg_constraint WHERE contype='f' AND NOT convalidated) THEN 'pass' ELSE 'fail' END),
    'append_only_history',jsonb_build_object('status',CASE WHEN EXISTS(SELECT 1 FROM pg_trigger WHERE tgname='event_work_attempt_immutable' AND NOT tgisinternal) AND EXISTS(SELECT 1 FROM pg_trigger WHERE tgname='event_claim_recovery_immutable' AND NOT tgisinternal) THEN 'pass' ELSE 'fail' END),
    'permission_hidden_truth',jsonb_build_object('status','not_executed'),
    'player_absence_freeze',jsonb_build_object('status',CASE WHEN NOT s.player_present OR s.state<>2 THEN 'pass' ELSE 'not_executed' END),
    'evidence_identity',jsonb_build_object('status',CASE WHEN m.actor_ref<>'' AND m.approval_ref<>'' AND m.source_environment<>'' THEN 'pass' ELSE 'fail' END)
  );
  SELECT bool_and(value->>'status'='pass') INTO ok FROM jsonb_each(gates);
  UPDATE sw_runtime.checkpoint_manifest SET validation_state=CASE WHEN ok THEN 'validated' ELSE 'failed' END
    WHERE checkpoint_id=p_checkpoint_id;
  RETURN jsonb_build_object('checkpoint_id',p_checkpoint_id,'valid',ok,'gates',gates);
END
$bp39$;

REVOKE ALL ON sw_runtime.checkpoint_manifest,sw_runtime.event_claim_recovery FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_runtime.count_canonical_businesses() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_runtime.capture_checkpoint_manifest(text,text,text,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_runtime.validate_checkpoint_manifest(uuid) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_runtime.begin_event_claim_recovery(text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_runtime.reconcile_event_claim(bigint,uuid,text,text,text,text,text,text,text,text,uuid) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_runtime.resolve_quarantined_event_claim(bigint,uuid,text,text,text,text,text,text,text,text,uuid) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_runtime.finish_event_claim_recovery() FROM PUBLIC;


COMMIT;
