-- BP12 durable append-only incident command handover register.
BEGIN;

CREATE TABLE sw_incident.command_handover (
  command_handover_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  handover_ref text NOT NULL UNIQUE,
  incident_id integer NOT NULL REFERENCES sw_incident.incident(incident_id),
  outgoing_commander_ref text NOT NULL,
  incoming_commander_ref text NOT NULL,
  prepared_by_ref text NOT NULL,
  authority_ref text NOT NULL,
  source_ref text NOT NULL,
  effective_world_tick bigint NOT NULL CHECK(effective_world_tick>=0),
  handover_document jsonb NOT NULL CHECK(jsonb_typeof(handover_document)='object'),
  source_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  idempotency_key text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK(outgoing_commander_ref<>incoming_commander_ref)
);
CREATE INDEX command_handover_incident_history_idx
  ON sw_incident.command_handover(incident_id,effective_world_tick,command_handover_id);

CREATE TRIGGER command_handover_immutable
BEFORE UPDATE OR DELETE ON sw_incident.command_handover
FOR EACH ROW EXECUTE FUNCTION sw_incident.reject_incident_history_mutation();

CREATE TRIGGER command_handover_no_truncate
BEFORE TRUNCATE ON sw_incident.command_handover
FOR EACH STATEMENT EXECUTE FUNCTION sw_incident.reject_incident_history_mutation();

INSERT INTO sw_core.event_type(event_code,description)
VALUES ('INCIDENT_COMMAND_HANDOVER_RECORDED','Append-only incident command handover recorded')
ON CONFLICT(event_code) DO NOTHING;

CREATE FUNCTION sw_incident.record_command_handover(
  p_incident_id integer,
  p_handover_ref text,
  p_outgoing_commander_ref text,
  p_incoming_commander_ref text,
  p_prepared_by_ref text,
  p_authority_ref text,
  p_source_ref text,
  p_effective_world_tick bigint,
  p_handover_document jsonb,
  p_idempotency_key text
) RETURNS bigint
LANGUAGE plpgsql AS $bp12$
DECLARE
  v_runtime sw_runtime.state%ROWTYPE;
  v_incident sw_incident.incident%ROWTYPE;
  v_prior sw_incident.command_handover%ROWTYPE;
  v_event_type_id smallint;
  v_event_id bigint;
  v_handover_id bigint;
BEGIN
  IF p_incident_id IS NULL OR p_incident_id<1
     OR p_handover_ref IS NULL OR p_handover_ref !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_outgoing_commander_ref IS NULL OR length(trim(p_outgoing_commander_ref))=0
     OR p_incoming_commander_ref IS NULL OR length(trim(p_incoming_commander_ref))=0
     OR p_outgoing_commander_ref=p_incoming_commander_ref
     OR p_prepared_by_ref IS NULL OR length(trim(p_prepared_by_ref))=0
     OR p_authority_ref IS NULL OR length(trim(p_authority_ref))=0
     OR p_source_ref IS NULL OR length(trim(p_source_ref))=0
     OR p_effective_world_tick IS NULL OR p_effective_world_tick<0
     OR p_handover_document IS NULL OR jsonb_typeof(p_handover_document)<>'object'
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$' THEN
    RAISE EXCEPTION 'invalid command handover identity or provenance';
  END IF;

  IF p_handover_document->>'handover_ref' IS DISTINCT FROM p_handover_ref
     OR (p_handover_document->>'incident_id')::integer IS DISTINCT FROM p_incident_id
     OR p_handover_document->>'outgoing_commander_ref' IS DISTINCT FROM p_outgoing_commander_ref
     OR p_handover_document->>'incoming_commander_ref' IS DISTINCT FROM p_incoming_commander_ref
     OR p_handover_document->>'prepared_by_ref' IS DISTINCT FROM p_prepared_by_ref
     OR p_handover_document->>'authority_ref' IS DISTINCT FROM p_authority_ref
     OR p_handover_document->>'source_ref' IS DISTINCT FROM p_source_ref
     OR (p_handover_document->>'effective_world_tick')::bigint IS DISTINCT FROM p_effective_world_tick
     OR p_handover_document->>'record_status' IS DISTINCT FROM 'PROJECTED_NOT_PERSISTED'
     OR p_handover_document->'read_only' IS DISTINCT FROM 'true'::jsonb
     OR jsonb_typeof(p_handover_document->'assignment_reconciliation') IS DISTINCT FROM 'object'
     OR (p_handover_document->'assignment_reconciliation'->>'incident_id')::integer IS DISTINCT FROM p_incident_id
     OR coalesce((p_handover_document->'assignment_reconciliation'->>'handover_ready')::boolean,false) IS NOT TRUE
     OR jsonb_typeof(p_handover_document->'commander_decisions') IS DISTINCT FROM 'array'
     OR jsonb_typeof(p_handover_document->'outstanding_actions') IS DISTINCT FROM 'array'
     OR jsonb_typeof(p_handover_document->'responsibility_transfers') IS DISTINCT FROM 'array'
     OR jsonb_typeof(p_handover_document->'acknowledgements') IS DISTINCT FROM 'array' THEN
    RAISE EXCEPTION 'command handover document identity or register shape does not reconcile';
  END IF;
  IF coalesce((p_handover_document->>'handover_ready')::boolean,false) IS NOT TRUE
     OR NOT EXISTS (
       SELECT 1 FROM jsonb_array_elements(p_handover_document->'responsibility_transfers') t
       WHERE t->>'from_ref'=p_outgoing_commander_ref AND t->>'to_ref'=p_incoming_commander_ref
     )
     OR NOT EXISTS (
       SELECT 1 FROM jsonb_array_elements(p_handover_document->'acknowledgements') a
       WHERE a->>'recipient_ref'=p_incoming_commander_ref AND a->>'acknowledgement'='ACCEPTED'
         AND a->>'handover_ref'=p_handover_ref
     )
     OR EXISTS (
       SELECT 1 FROM jsonb_array_elements(p_handover_document->'acknowledgements') a
       WHERE a->>'acknowledgement'='DECLINED'
     ) THEN
    RAISE EXCEPTION 'command handover is not accepted and ready for transfer';
  END IF;

  -- Serialize concurrent retries for the same key before checking either ledger.
  PERFORM pg_advisory_xact_lock(hashtextextended(p_idempotency_key,0));
  SELECT * INTO v_prior FROM sw_incident.command_handover
  WHERE idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.incident_id<>p_incident_id OR v_prior.handover_ref<>p_handover_ref
       OR v_prior.handover_document<>p_handover_document
       OR v_prior.source_ref<>p_source_ref THEN
      RAISE EXCEPTION 'command handover idempotency key conflicts with prior record';
    END IF;
    RETURN v_prior.command_handover_id;
  END IF;

  SELECT * INTO v_runtime FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR v_runtime.state<>2 OR NOT v_runtime.player_present THEN
    RAISE EXCEPTION 'command handover recording requires running player-present simulation';
  END IF;
  IF p_effective_world_tick>v_runtime.world_tick THEN
    RAISE EXCEPTION 'command handover effective tick cannot be in the future';
  END IF;

  SELECT * INTO v_incident FROM sw_incident.incident
  WHERE incident_id=p_incident_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'command handover incident does not exist'; END IF;
  IF v_incident.status IN ('CLOSED','CANCELLED','DUPLICATE_LINKED') THEN
    RAISE EXCEPTION 'command handover cannot be recorded for a terminal incident';
  END IF;

  SELECT event_type_id INTO v_event_type_id FROM sw_core.event_type
  WHERE event_code='INCIDENT_COMMAND_HANDOVER_RECORDED';
  INSERT INTO sw_core.simulation_event(
    event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key
  ) VALUES (
    v_event_type_id,now(),v_runtime.world_tick,'incident',p_incident_id,p_source_ref,
    jsonb_build_object('handover_ref',p_handover_ref,
      'outgoing_commander_ref',p_outgoing_commander_ref,
      'incoming_commander_ref',p_incoming_commander_ref,
      'prepared_by_ref',p_prepared_by_ref,'authority_ref',p_authority_ref,
      'effective_world_tick',p_effective_world_tick,'idempotency_key',p_idempotency_key),
    p_idempotency_key
  ) RETURNING event_id INTO v_event_id;

  INSERT INTO sw_incident.command_handover(
    handover_ref,incident_id,outgoing_commander_ref,incoming_commander_ref,
    prepared_by_ref,authority_ref,source_ref,effective_world_tick,
    handover_document,source_event_id,idempotency_key
  ) VALUES (
    p_handover_ref,p_incident_id,p_outgoing_commander_ref,p_incoming_commander_ref,
    p_prepared_by_ref,p_authority_ref,p_source_ref,p_effective_world_tick,
    jsonb_set(p_handover_document,'{record_status}','"PERSISTED"'::jsonb,true),
    v_event_id,p_idempotency_key
  ) RETURNING command_handover_id INTO v_handover_id;
  RETURN v_handover_id;
END
$bp12$;

CREATE FUNCTION sw_incident.command_handover_history(p_incident_id integer)
RETURNS TABLE(
  command_handover_id bigint,
  handover_ref text,
  incident_id integer,
  outgoing_commander_ref text,
  incoming_commander_ref text,
  prepared_by_ref text,
  authority_ref text,
  source_ref text,
  effective_world_tick bigint,
  handover_document jsonb,
  source_event_id bigint,
  occurred_at timestamptz,
  event_world_tick bigint
)
LANGUAGE sql STABLE AS $bp12$
  SELECT h.command_handover_id,h.handover_ref,h.incident_id,
    h.outgoing_commander_ref,h.incoming_commander_ref,h.prepared_by_ref,
    h.authority_ref,h.source_ref,h.effective_world_tick,h.handover_document,
    h.source_event_id,e.occurred_at,e.world_tick
  FROM sw_incident.command_handover h
  JOIN sw_core.simulation_event e ON e.event_id=h.source_event_id
  WHERE h.incident_id=p_incident_id
  ORDER BY h.effective_world_tick,h.command_handover_id
$bp12$;

COMMIT;
