-- BP12 incident master, source links, location, parties and event-driven lifecycle.
BEGIN;
CREATE SCHEMA IF NOT EXISTS sw_incident;
CREATE SEQUENCE sw_incident.incident_id_seq;

CREATE TABLE sw_incident.incident (
  incident_id integer PRIMARY KEY DEFAULT nextval('sw_incident.incident_id_seq'),
  incident_ref text NOT NULL UNIQUE,
  record_version integer NOT NULL DEFAULT 1 CHECK(record_version>0),
  status text NOT NULL CHECK(status IN
    ('RECEIVED','AWAITING_TRIAGE','ASSESSED','ALLOCATED','DISPATCHED','RESPONDING',
     'ATTENDED','ACTIVE_MANAGEMENT','MONITORING','RESOLVED','CLOSED','CANCELLED',
     'DUPLICATE_LINKED','REOPENED')),
  source_type text NOT NULL CHECK(source_type IN
    ('communications_contact','police_call','cad_event','officer_report','alarm','interagency','system','other')),
  source_record_id text NOT NULL,
  reporter_person_id integer REFERENCES sw_people.person(person_id),
  caller_identity_state text NOT NULL CHECK(caller_identity_state IN
    ('known','claimed','anonymous','withheld','unknown','not_applicable')),
  original_report_text text NOT NULL,
  operational_summary text,
  category_code text NOT NULL DEFAULT 'unclassified',
  priority smallint CHECK(priority BETWEEN 1 AND 5),
  severity_code text NOT NULL DEFAULT 'unassessed' CHECK(severity_code IN
    ('critical','high','moderate','low','unassessed')),
  priority_rationale text,
  reported_occurrence_from_tick bigint,
  reported_occurrence_to_tick bigint,
  owning_function text NOT NULL DEFAULT 'communications',
  incident_owner_personnel_id uuid REFERENCES sw_police.personnel(personnel_id),
  lead_unit_id text REFERENCES sw_police.unit_profile(unit_id),
  commander_personnel_id uuid REFERENCES sw_police.personnel(personnel_id),
  resolution_code text,
  closure_reason text,
  duplicate_of_incident_id integer REFERENCES sw_incident.incident(incident_id),
  received_tick bigint NOT NULL CHECK(received_tick>=0),
  created_tick bigint NOT NULL CHECK(created_tick>=0),
  updated_tick bigint NOT NULL CHECK(updated_tick>=0),
  closed_tick bigint,
  created_by_ref text NOT NULL,
  created_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  last_event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  idempotency_key text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CHECK(reported_occurrence_to_tick IS NULL OR reported_occurrence_from_tick IS NULL
        OR reported_occurrence_to_tick>=reported_occurrence_from_tick),
  CHECK(closed_tick IS NULL OR closed_tick>=created_tick),
  CHECK(duplicate_of_incident_id IS NULL OR duplicate_of_incident_id<>incident_id)
);
ALTER SEQUENCE sw_incident.incident_id_seq OWNED BY sw_incident.incident.incident_id;
CREATE INDEX incident_status_priority_idx ON sw_incident.incident(status,priority,created_tick);
CREATE INDEX incident_owner_idx ON sw_incident.incident(incident_owner_personnel_id,status);
CREATE INDEX incident_lead_unit_idx ON sw_incident.incident(lead_unit_id,status);

CREATE TABLE sw_incident.incident_event (
  incident_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  incident_id integer NOT NULL REFERENCES sw_incident.incident(incident_id),
  source_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  event_kind text NOT NULL CHECK(event_kind IN
    ('created','state_changed','assessment_recorded','category_changed','priority_changed',
     'owner_assigned','lead_unit_assigned','commander_appointed','location_added',
     'party_linked','source_linked','decision_recorded','response_milestone',
     'resolved','closed','cancelled','duplicate_linked','reopened','corrected')),
  prior_status text,
  resulting_status text,
  prior_priority smallint,
  resulting_priority smallint,
  effective_tick bigint NOT NULL CHECK(effective_tick>=0),
  actor_ref text NOT NULL,
  authority_ref text,
  source_ref text NOT NULL,
  reason text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX incident_event_history_idx ON sw_incident.incident_event(incident_id,incident_event_id);

CREATE TABLE sw_incident.incident_assessment (
  assessment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  incident_id integer NOT NULL REFERENCES sw_incident.incident(incident_id),
  assessment_kind text NOT NULL CHECK(assessment_kind IN
    ('source_inherited','initial','reassessment','supervisor_review')),
  category_code text NOT NULL,
  priority smallint CHECK(priority BETWEEN 1 AND 5),
  severity_code text NOT NULL CHECK(severity_code IN
    ('critical','high','moderate','low','unassessed')),
  confidence text NOT NULL CHECK(confidence IN ('high','medium','low','unverified','unknown')),
  rationale text NOT NULL,
  assessed_by_personnel_id uuid REFERENCES sw_police.personnel(personnel_id),
  actor_ref text NOT NULL,
  authority_ref text,
  effective_tick bigint NOT NULL CHECK(effective_tick>=0),
  source_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  source_ref text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX incident_assessment_history_idx
  ON sw_incident.incident_assessment(incident_id,assessment_id);

CREATE TABLE sw_incident.incident_source_link (
  incident_source_link_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  incident_id integer NOT NULL REFERENCES sw_incident.incident(incident_id),
  source_type text NOT NULL CHECK(source_type IN
    ('communications_contact','police_call','cad_event','officer_report','alarm',
     'interagency','system','other')),
  source_record_id text NOT NULL,
  link_type text NOT NULL CHECK(link_type IN ('origin','supporting','related','duplicate','follow_on')),
  linked_tick bigint NOT NULL CHECK(linked_tick>=0),
  source_event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  source_ref text NOT NULL,
  UNIQUE(incident_id,source_type,source_record_id,link_type)
);
CREATE INDEX incident_source_lookup_idx ON sw_incident.incident_source_link(source_type,source_record_id);

CREATE TABLE sw_incident.incident_location (
  incident_location_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  incident_id integer NOT NULL REFERENCES sw_incident.incident(incident_id),
  location_role text NOT NULL CHECK(location_role IN
    ('primary','secondary','staging','origin','last_known','search_area','other')),
  location_type text NOT NULL CHECK(location_type IN
    ('canonical_spatial','property','premises','road','landmark','public_space','raw','external')),
  spatial_id integer REFERENCES sw_geo.entity(spatial_id),
  location_ref text,
  raw_description text NOT NULL,
  confidence text NOT NULL CHECK(confidence IN ('high','medium','low','unverified','unknown')),
  effective_tick bigint NOT NULL CHECK(effective_tick>=0),
  source_event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  source_ref text NOT NULL,
  CHECK(location_ref IS NOT NULL OR spatial_id IS NOT NULL OR length(raw_description)>0)
);
CREATE INDEX incident_location_idx ON sw_incident.incident_location(incident_id,effective_tick);

CREATE TABLE sw_incident.incident_party (
  incident_party_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  incident_id integer NOT NULL REFERENCES sw_incident.incident(incident_id),
  person_id integer REFERENCES sw_people.person(person_id),
  organisation_ref text,
  role_code text NOT NULL CHECK(role_code IN
    ('caller','reporter','complainant','victim','witness','affected_person',
     'responder','property_contact','other')),
  identity_state text NOT NULL CHECK(identity_state IN
    ('verified','claimed','unverified','anonymous','withheld','unknown','not_applicable')),
  effective_tick bigint NOT NULL CHECK(effective_tick>=0),
  source_event_id bigint NOT NULL REFERENCES sw_core.simulation_event(event_id),
  source_ref text NOT NULL,
  CHECK((person_id IS NOT NULL)::integer + (organisation_ref IS NOT NULL)::integer = 1)
);
CREATE INDEX incident_party_person_idx ON sw_incident.incident_party(person_id,incident_id);

CREATE TABLE sw_incident.incident_decision (
  incident_decision_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  incident_id integer NOT NULL REFERENCES sw_incident.incident(incident_id),
  decision_type text NOT NULL,
  decision_maker_personnel_id uuid REFERENCES sw_police.personnel(personnel_id),
  authority_ref text NOT NULL,
  decision_tick bigint NOT NULL CHECK(decision_tick>=0),
  information_available text NOT NULL,
  options_considered text,
  decision_text text NOT NULL,
  rationale text NOT NULL,
  risk_accepted text,
  review_trigger text,
  source_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  source_ref text NOT NULL
);

CREATE FUNCTION sw_incident.reject_incident_history_mutation() RETURNS trigger
LANGUAGE plpgsql AS $bp12$
BEGIN
  RAISE EXCEPTION '% is append-only; record a new incident event',TG_TABLE_NAME;
END
$bp12$;
CREATE TRIGGER incident_event_immutable BEFORE UPDATE OR DELETE ON sw_incident.incident_event
FOR EACH ROW EXECUTE FUNCTION sw_incident.reject_incident_history_mutation();
CREATE TRIGGER incident_assessment_immutable BEFORE UPDATE OR DELETE ON sw_incident.incident_assessment
FOR EACH ROW EXECUTE FUNCTION sw_incident.reject_incident_history_mutation();
CREATE TRIGGER incident_source_link_immutable BEFORE UPDATE OR DELETE ON sw_incident.incident_source_link
FOR EACH ROW EXECUTE FUNCTION sw_incident.reject_incident_history_mutation();
CREATE TRIGGER incident_location_immutable BEFORE UPDATE OR DELETE ON sw_incident.incident_location
FOR EACH ROW EXECUTE FUNCTION sw_incident.reject_incident_history_mutation();
CREATE TRIGGER incident_party_immutable BEFORE UPDATE OR DELETE ON sw_incident.incident_party
FOR EACH ROW EXECUTE FUNCTION sw_incident.reject_incident_history_mutation();
CREATE TRIGGER incident_decision_immutable BEFORE UPDATE OR DELETE ON sw_incident.incident_decision
FOR EACH ROW EXECUTE FUNCTION sw_incident.reject_incident_history_mutation();

INSERT INTO sw_core.event_type(event_code,description) VALUES
 ('INCIDENT_CREATED','Police operational incident created'),
 ('INCIDENT_STATE_CHANGED','Police operational incident state changed'),
 ('INCIDENT_ASSESSMENT_RECORDED','Incident assessment recorded'),
 ('INCIDENT_LOCATION_ADDED','Incident location or site linked'),
 ('INCIDENT_PARTY_LINKED','Person or organisation linked to an incident'),
 ('INCIDENT_DECISION_RECORDED','Material incident decision recorded'),
 ('INCIDENT_SOURCE_LINKED','Call, CAD or other source linked to incident'),
 ('INCIDENT_DUPLICATE_LINKED','Incident linked as a confirmed duplicate'),
 ('INCIDENT_REOPENED','Resolved or closed incident reopened')
ON CONFLICT(event_code) DO NOTHING;

CREATE FUNCTION sw_incident.guard_incident_update() RETURNS trigger
LANGUAGE plpgsql AS $bp12$
DECLARE v_event sw_core.simulation_event%ROWTYPE;
        v_code text;
        v_status_changed boolean;
        v_assessment_changed boolean;
BEGIN
  IF NEW.incident_id<>OLD.incident_id
     OR NEW.incident_ref<>OLD.incident_ref
     OR NEW.created_event_id<>OLD.created_event_id
     OR NEW.created_tick<>OLD.created_tick
     OR NEW.source_type<>OLD.source_type
     OR NEW.source_record_id<>OLD.source_record_id
     OR NEW.original_report_text<>OLD.original_report_text
     OR NEW.idempotency_key<>OLD.idempotency_key THEN
    RAISE EXCEPTION 'incident source and identity fields are immutable';
  END IF;
  v_status_changed:=NEW.status IS DISTINCT FROM OLD.status;
  v_assessment_changed:=ROW(NEW.category_code,NEW.priority,NEW.severity_code,NEW.priority_rationale)
    IS DISTINCT FROM ROW(OLD.category_code,OLD.priority,OLD.severity_code,OLD.priority_rationale);
  IF v_status_changed=v_assessment_changed
     OR NEW.record_version<>OLD.record_version+1
     OR NEW.last_event_id IS NOT DISTINCT FROM OLD.last_event_id THEN
    RAISE EXCEPTION 'incident changes require one validated state or assessment event';
  END IF;
  SELECT * INTO v_event FROM sw_core.simulation_event WHERE event_id=NEW.last_event_id;
  SELECT event_code INTO v_code FROM sw_core.event_type WHERE event_type_id=v_event.event_type_id;
  IF v_event.subject_kind<>'incident' OR v_event.subject_id<>OLD.incident_id
     OR v_event.world_tick<>NEW.updated_tick THEN
    RAISE EXCEPTION 'incident projection update does not match its committed event';
  END IF;
  IF v_status_changed AND v_code<>'INCIDENT_STATE_CHANGED' THEN
    RAISE EXCEPTION 'incident status change requires INCIDENT_STATE_CHANGED event';
  END IF;
  IF v_assessment_changed AND (v_code<>'INCIDENT_ASSESSMENT_RECORDED' OR NOT EXISTS(
      SELECT 1 FROM sw_incident.incident_assessment a
      WHERE a.incident_id=OLD.incident_id AND a.source_event_id=NEW.last_event_id
  )) THEN
    RAISE EXCEPTION 'incident assessment projection requires its assessment event record';
  END IF;
  RETURN NEW;
END
$bp12$;
CREATE TRIGGER incident_projection_guard BEFORE UPDATE ON sw_incident.incident
FOR EACH ROW EXECUTE FUNCTION sw_incident.guard_incident_update();

CREATE FUNCTION sw_incident.create_incident(
  p_source_type text,
  p_source_record_id text,
  p_original_report_text text,
  p_actor_ref text,
  p_idempotency_key text,
  p_reporter_person_id integer DEFAULT NULL,
  p_caller_identity_state text DEFAULT 'unknown',
  p_category_code text DEFAULT 'unclassified',
  p_priority smallint DEFAULT NULL,
  p_severity_code text DEFAULT 'unassessed',
  p_location_raw text DEFAULT NULL,
  p_location_ref text DEFAULT NULL,
  p_location_type text DEFAULT 'raw',
  p_location_confidence text DEFAULT 'unknown',
  p_received_tick bigint DEFAULT NULL
) RETURNS integer
LANGUAGE plpgsql AS $bp12$
DECLARE
  v_runtime sw_runtime.state%ROWTYPE;
  v_prior sw_incident.incident%ROWTYPE;
  v_incident_id integer;
  v_event_id bigint;
  v_event_type_id smallint;
  v_received_tick bigint;
  v_source_type text;
BEGIN
  IF p_source_type IS NULL OR p_source_type NOT IN ('communications_contact','police_call','cad_event','officer_report','alarm','interagency','system','other')
     OR p_source_record_id IS NULL OR length(trim(p_source_record_id))=0
     OR p_original_report_text IS NULL OR length(trim(p_original_report_text))=0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref))=0
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_caller_identity_state IS NULL OR p_caller_identity_state NOT IN ('known','claimed','anonymous','withheld','unknown','not_applicable')
     OR p_category_code IS NULL OR p_category_code=''
     OR p_priority IS NOT NULL AND p_priority NOT BETWEEN 1 AND 5
     OR p_severity_code IS NULL OR p_severity_code NOT IN ('critical','high','moderate','low','unassessed')
     OR (p_location_raw IS NOT NULL AND (p_location_type IS NULL OR p_location_type NOT IN
       ('canonical_spatial','property','premises','road','landmark','public_space','raw','external')))
     OR (p_location_raw IS NOT NULL AND (p_location_confidence IS NULL OR p_location_confidence NOT IN
       ('high','medium','low','unverified','unknown'))) THEN
    RAISE EXCEPTION 'invalid incident intake data';
  END IF;

  SELECT * INTO v_prior FROM sw_incident.incident WHERE idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.source_type<>p_source_type OR v_prior.source_record_id<>p_source_record_id
       OR v_prior.original_report_text<>p_original_report_text
       OR v_prior.category_code<>p_category_code
       OR v_prior.priority IS DISTINCT FROM p_priority
       OR v_prior.severity_code<>p_severity_code THEN
      RAISE EXCEPTION 'incident idempotency key conflicts with prior intake definition';
    END IF;
    RETURN v_prior.incident_id;
  END IF;
  SELECT i.incident_id INTO v_incident_id
  FROM sw_incident.incident_source_link l
  JOIN sw_incident.incident i USING(incident_id)
  WHERE l.source_type=p_source_type AND l.source_record_id=p_source_record_id
    AND l.link_type='origin'
  ORDER BY l.incident_source_link_id LIMIT 1;
  IF FOUND THEN RETURN v_incident_id; END IF;

  SELECT * INTO v_runtime FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR v_runtime.state<>2 OR NOT v_runtime.player_present THEN
    RAISE EXCEPTION 'incident intake requires running player-present simulation';
  END IF;
  v_received_tick:=coalesce(p_received_tick,v_runtime.world_tick);
  IF v_received_tick<0 OR v_received_tick>v_runtime.world_tick THEN
    RAISE EXCEPTION 'incident received tick must not be in the future';
  END IF;

  SELECT event_type_id INTO v_event_type_id FROM sw_core.event_type WHERE event_code='INCIDENT_CREATED';
  v_incident_id:=nextval('sw_incident.incident_id_seq');
  INSERT INTO sw_core.simulation_event(
    event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key
  ) VALUES (
    v_event_type_id,now(),v_runtime.world_tick,'incident',v_incident_id,
    p_source_type||':'||p_source_record_id,
    jsonb_build_object('source_type',p_source_type,'source_record_id',p_source_record_id,
      'category_code',p_category_code,'priority',p_priority,'severity_code',p_severity_code),
    p_idempotency_key
  ) RETURNING event_id INTO v_event_id;

  INSERT INTO sw_incident.incident(
    incident_id,incident_ref,status,source_type,source_record_id,reporter_person_id,
    caller_identity_state,original_report_text,category_code,priority,severity_code,
    received_tick,created_tick,updated_tick,owning_function,created_by_ref,
    created_event_id,last_event_id,idempotency_key
  ) VALUES (
    v_incident_id,'SWI-'||lpad(v_incident_id::text,7,'0'),'RECEIVED',
    p_source_type,p_source_record_id,p_reporter_person_id,p_caller_identity_state,
    p_original_report_text,p_category_code,p_priority,p_severity_code,
    v_received_tick,v_runtime.world_tick,v_runtime.world_tick,'communications',
    p_actor_ref,v_event_id,v_event_id,p_idempotency_key
  );

  INSERT INTO sw_incident.incident_event(
    incident_id,source_event_id,event_kind,resulting_status,resulting_priority,
    effective_tick,actor_ref,source_ref,reason
  ) VALUES (
    v_incident_id,v_event_id,'created','RECEIVED',p_priority,
    v_runtime.world_tick,p_actor_ref,p_source_type||':'||p_source_record_id,
    'Initial incident created from operational source'
  );

  IF p_priority IS NOT NULL OR p_category_code<>'unclassified' OR p_severity_code<>'unassessed' THEN
    INSERT INTO sw_incident.incident_assessment(
      incident_id,assessment_kind,category_code,priority,severity_code,confidence,
      rationale,actor_ref,effective_tick,source_event_id,source_ref
    ) VALUES (
      v_incident_id,'source_inherited',p_category_code,p_priority,p_severity_code,
      'unknown','Initial assessment inherited from the originating operational source.',
      p_actor_ref,v_runtime.world_tick,v_event_id,'incident-source-assessment:'||v_incident_id::text
    );
  END IF;

  INSERT INTO sw_incident.incident_source_link(
    incident_id,source_type,source_record_id,link_type,linked_tick,source_event_id,source_ref
  ) VALUES (
    v_incident_id,p_source_type,p_source_record_id,'origin',v_runtime.world_tick,
    v_event_id,p_source_type||':'||p_source_record_id
  );

  IF p_location_raw IS NOT NULL AND length(trim(p_location_raw))>0 THEN
    INSERT INTO sw_incident.incident_location(
      incident_id,location_role,location_type,location_ref,raw_description,confidence,
      effective_tick,source_event_id,source_ref
    ) VALUES (
      v_incident_id,'primary',p_location_type,p_location_ref,p_location_raw,
      p_location_confidence,v_runtime.world_tick,v_event_id,
      'incident-intake-location:'||v_incident_id::text
    );
  END IF;

  UPDATE sw_runtime.state SET last_event_id=v_event_id,updated_at=now() WHERE singleton=1;
  RETURN v_incident_id;
END
$bp12$;

CREATE FUNCTION sw_incident.record_incident_assessment(
  p_incident_id integer,
  p_category_code text,
  p_priority smallint,
  p_severity_code text,
  p_confidence text,
  p_rationale text,
  p_actor_ref text,
  p_authority_ref text,
  p_idempotency_key text,
  p_assessed_by_personnel_id uuid DEFAULT NULL
) RETURNS bigint
LANGUAGE plpgsql AS $bp12$
DECLARE
  v_runtime sw_runtime.state%ROWTYPE;
  v_incident sw_incident.incident%ROWTYPE;
  v_event_id bigint;
  v_event_type_id smallint;
BEGIN
  IF p_category_code IS NULL OR length(trim(p_category_code))=0
     OR p_priority IS NOT NULL AND p_priority NOT BETWEEN 1 AND 5
     OR p_severity_code NOT IN ('critical','high','moderate','low','unassessed')
     OR p_confidence NOT IN ('high','medium','low','unverified','unknown')
     OR p_rationale IS NULL OR length(trim(p_rationale))=0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref))=0
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$' THEN
    RAISE EXCEPTION 'invalid incident assessment';
  END IF;
  SELECT event_id INTO v_event_id FROM sw_core.simulation_event WHERE idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF NOT EXISTS(SELECT 1 FROM sw_core.simulation_event se
      JOIN sw_core.event_type et USING(event_type_id)
      WHERE se.event_id=v_event_id AND et.event_code='INCIDENT_ASSESSMENT_RECORDED'
        AND se.subject_kind='incident' AND se.subject_id=p_incident_id) THEN
      RAISE EXCEPTION 'incident assessment idempotency key conflicts with another event';
    END IF;
    RETURN v_event_id;
  END IF;
  SELECT * INTO v_runtime FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR v_runtime.state<>2 OR NOT v_runtime.player_present THEN
    RAISE EXCEPTION 'incident assessment requires running player-present simulation';
  END IF;
  SELECT * INTO v_incident FROM sw_incident.incident WHERE incident_id=p_incident_id FOR UPDATE;
  IF NOT FOUND OR v_incident.status IN ('CLOSED','CANCELLED','DUPLICATE_LINKED') THEN
    RAISE EXCEPTION 'incident is not open for assessment';
  END IF;
  SELECT event_type_id INTO v_event_type_id FROM sw_core.event_type
  WHERE event_code='INCIDENT_ASSESSMENT_RECORDED';
  INSERT INTO sw_core.simulation_event(
    event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key
  ) VALUES (
    v_event_type_id,now(),v_runtime.world_tick,'incident',p_incident_id,
    'incident:'||p_incident_id::text,
    jsonb_build_object('category_code',p_category_code,'priority',p_priority,
      'severity_code',p_severity_code,'confidence',p_confidence,'rationale',p_rationale),
    p_idempotency_key
  ) RETURNING event_id INTO v_event_id;
  INSERT INTO sw_incident.incident_assessment(
    incident_id,assessment_kind,category_code,priority,severity_code,confidence,
    rationale,assessed_by_personnel_id,actor_ref,authority_ref,effective_tick,
    source_event_id,source_ref
  ) VALUES (
    p_incident_id,'reassessment',p_category_code,p_priority,p_severity_code,p_confidence,
    p_rationale,p_assessed_by_personnel_id,p_actor_ref,p_authority_ref,
    v_runtime.world_tick,v_event_id,'incident-assessment:'||p_incident_id::text
  );
  UPDATE sw_incident.incident
  SET category_code=p_category_code,priority=p_priority,severity_code=p_severity_code,
      priority_rationale=p_rationale,record_version=record_version+1,
      updated_tick=v_runtime.world_tick,last_event_id=v_event_id,updated_at=now()
  WHERE incident_id=p_incident_id;
  INSERT INTO sw_incident.incident_event(
    incident_id,source_event_id,event_kind,prior_status,resulting_status,
    prior_priority,resulting_priority,effective_tick,actor_ref,authority_ref,source_ref,reason
  ) VALUES (
    p_incident_id,v_event_id,'assessment_recorded',v_incident.status,v_incident.status,
    v_incident.priority,p_priority,v_runtime.world_tick,p_actor_ref,p_authority_ref,
    'incident-assessment:'||p_incident_id::text,p_rationale
  );
  UPDATE sw_runtime.state SET last_event_id=v_event_id,updated_at=now() WHERE singleton=1;
  RETURN v_event_id;
END
$bp12$;
CREATE FUNCTION sw_incident.transition_incident(
  p_incident_id integer,
  p_new_status text,
  p_actor_ref text,
  p_authority_ref text,
  p_reason text,
  p_idempotency_key text,
  p_duplicate_of_incident_id integer DEFAULT NULL,
  p_resolution_code text DEFAULT NULL
) RETURNS bigint
LANGUAGE plpgsql AS $bp12$
DECLARE
  v_runtime sw_runtime.state%ROWTYPE;
  v_incident sw_incident.incident%ROWTYPE;
  v_event_id bigint;
  v_event_type_id smallint;
  v_allowed boolean:=false;
BEGIN
  IF p_new_status NOT IN ('RECEIVED','AWAITING_TRIAGE','ASSESSED','ALLOCATED','DISPATCHED','RESPONDING',
      'ATTENDED','ACTIVE_MANAGEMENT','MONITORING','RESOLVED','CLOSED','CANCELLED','DUPLICATE_LINKED','REOPENED')
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref))=0
     OR p_reason IS NULL OR length(trim(p_reason))=0
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_new_status='DUPLICATE_LINKED' AND p_duplicate_of_incident_id IS NULL
     OR p_new_status IN ('CLOSED','CANCELLED') AND length(trim(p_reason))=0 THEN
    RAISE EXCEPTION 'invalid incident transition request';
  END IF;
  SELECT se.event_id INTO v_event_id
  FROM sw_core.simulation_event se
  JOIN sw_core.event_type et USING(event_type_id)
  WHERE se.idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF NOT EXISTS(SELECT 1 FROM sw_core.simulation_event
      WHERE event_id=v_event_id AND subject_kind='incident'
        AND subject_id=p_incident_id AND event_type_id IN
          (SELECT event_type_id FROM sw_core.event_type WHERE event_code='INCIDENT_STATE_CHANGED')) THEN
      RAISE EXCEPTION 'incident transition idempotency key conflicts with another event';
    END IF;
    RETURN v_event_id;
  END IF;

  SELECT * INTO v_runtime FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR v_runtime.state<>2 OR NOT v_runtime.player_present THEN
    RAISE EXCEPTION 'incident transition requires running player-present simulation';
  END IF;
  SELECT * INTO v_incident FROM sw_incident.incident WHERE incident_id=p_incident_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'incident not found'; END IF;

  v_allowed:=CASE v_incident.status
    WHEN 'RECEIVED' THEN p_new_status IN ('AWAITING_TRIAGE','ASSESSED','CANCELLED','DUPLICATE_LINKED')
    WHEN 'AWAITING_TRIAGE' THEN p_new_status IN ('ASSESSED','CANCELLED','DUPLICATE_LINKED')
    WHEN 'ASSESSED' THEN p_new_status IN ('ALLOCATED','MONITORING','RESOLVED','CANCELLED')
    WHEN 'ALLOCATED' THEN p_new_status IN ('DISPATCHED','MONITORING','RESOLVED','CANCELLED')
    WHEN 'DISPATCHED' THEN p_new_status IN ('RESPONDING','ATTENDED','ACTIVE_MANAGEMENT','CANCELLED')
    WHEN 'RESPONDING' THEN p_new_status IN ('ATTENDED','ACTIVE_MANAGEMENT','MONITORING','RESOLVED')
    WHEN 'ATTENDED' THEN p_new_status IN ('ACTIVE_MANAGEMENT','MONITORING','RESOLVED')
    WHEN 'ACTIVE_MANAGEMENT' THEN p_new_status IN ('ATTENDED','MONITORING','RESOLVED')
    WHEN 'MONITORING' THEN p_new_status IN ('ACTIVE_MANAGEMENT','RESOLVED','CLOSED')
    WHEN 'RESOLVED' THEN p_new_status IN ('CLOSED','REOPENED')
    WHEN 'CLOSED' THEN p_new_status='REOPENED'
    WHEN 'REOPENED' THEN p_new_status IN ('AWAITING_TRIAGE','ASSESSED','ALLOCATED','ACTIVE_MANAGEMENT')
    ELSE false
  END;
  IF NOT v_allowed THEN
    RAISE EXCEPTION 'invalid incident state transition: % -> %',v_incident.status,p_new_status;
  END IF;
  IF p_duplicate_of_incident_id IS NOT NULL AND p_new_status<>'DUPLICATE_LINKED' THEN
    RAISE EXCEPTION 'duplicate target is only valid for DUPLICATE_LINKED transition';
  END IF;
  IF p_duplicate_of_incident_id IS NOT NULL AND
     (p_duplicate_of_incident_id=p_incident_id OR NOT EXISTS(
       SELECT 1 FROM sw_incident.incident WHERE incident_id=p_duplicate_of_incident_id)) THEN
    RAISE EXCEPTION 'duplicate target incident is invalid';
  END IF;

  SELECT event_type_id INTO v_event_type_id FROM sw_core.event_type WHERE event_code='INCIDENT_STATE_CHANGED';
  INSERT INTO sw_core.simulation_event(
    event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key
  ) VALUES (
    v_event_type_id,now(),v_runtime.world_tick,'incident',p_incident_id,
    'incident:'||p_incident_id::text,
    jsonb_build_object('prior_status',v_incident.status,'new_status',p_new_status,
      'reason',p_reason,'authority_ref',p_authority_ref),
    p_idempotency_key
  ) RETURNING event_id INTO v_event_id;

  UPDATE sw_incident.incident
  SET status=p_new_status,record_version=record_version+1,updated_tick=v_runtime.world_tick,
      last_event_id=v_event_id,updated_at=now(),
      duplicate_of_incident_id=coalesce(p_duplicate_of_incident_id,duplicate_of_incident_id),
      resolution_code=coalesce(p_resolution_code,resolution_code),
      closed_tick=CASE WHEN p_new_status IN ('CLOSED','CANCELLED') THEN v_runtime.world_tick
                       WHEN p_new_status='REOPENED' THEN NULL ELSE closed_tick END,
      closure_reason=CASE WHEN p_new_status IN ('CLOSED','CANCELLED') THEN p_reason
                          WHEN p_new_status='REOPENED' THEN NULL ELSE closure_reason END
  WHERE incident_id=p_incident_id;

  IF p_new_status='DUPLICATE_LINKED' THEN
    INSERT INTO sw_incident.incident_source_link(
      incident_id,source_type,source_record_id,link_type,linked_tick,source_event_id,source_ref
    ) VALUES (
      p_incident_id,'system','incident:'||p_duplicate_of_incident_id::text,'duplicate',
      v_runtime.world_tick,v_event_id,'incident-duplicate:'||p_incident_id::text
    );
  END IF;

  INSERT INTO sw_incident.incident_event(
    incident_id,source_event_id,event_kind,prior_status,resulting_status,
    prior_priority,resulting_priority,effective_tick,actor_ref,authority_ref,source_ref,reason
  ) VALUES (
    p_incident_id,v_event_id,'state_changed',v_incident.status,p_new_status,
    v_incident.priority,v_incident.priority,v_runtime.world_tick,p_actor_ref,
    p_authority_ref,'incident:'||p_incident_id::text,p_reason
  );

  UPDATE sw_runtime.state SET last_event_id=v_event_id,updated_at=now() WHERE singleton=1;
  RETURN v_event_id;
END
$bp12$;


CREATE FUNCTION sw_incident.add_incident_location(
  p_incident_id integer,
  p_location_role text,
  p_location_type text,
  p_location_ref text,
  p_spatial_id integer,
  p_raw_description text,
  p_confidence text,
  p_actor_ref text,
  p_authority_ref text,
  p_source_ref text,
  p_address_source_ref text,
  p_idempotency_key text
) RETURNS bigint
LANGUAGE plpgsql AS $bp12$
DECLARE
  v_runtime sw_runtime.state%ROWTYPE;
  v_incident sw_incident.incident%ROWTYPE;
  v_event_id bigint;
  v_location_id bigint;
  v_event_type_id smallint;
BEGIN
  IF p_incident_id IS NULL OR p_incident_id<1
     OR p_location_role NOT IN ('primary','secondary','staging','origin','last_known','search_area','other')
     OR p_location_type NOT IN ('canonical_spatial','property','premises','road','landmark','public_space','raw','external')
     OR (p_location_ref IS NULL AND p_spatial_id IS NULL
         AND (p_raw_description IS NULL OR length(trim(p_raw_description))=0))
     OR p_raw_description IS NULL OR length(trim(p_raw_description))=0
     OR p_confidence NOT IN ('high','medium','low','unverified','unknown')
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref))=0
     OR p_authority_ref IS NULL OR length(trim(p_authority_ref))=0
     OR p_source_ref IS NULL OR length(trim(p_source_ref))=0
     OR p_address_source_ref IS NULL OR length(trim(p_address_source_ref))=0
     OR p_idempotency_key IS NULL
     OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$' THEN
    RAISE EXCEPTION 'invalid incident location request';
  END IF;
  IF p_location_type='canonical_spatial' AND p_spatial_id IS NULL THEN
    RAISE EXCEPTION 'canonical spatial location requires a spatial entity ID';
  END IF;
  IF p_location_type<>'canonical_spatial' AND p_spatial_id IS NOT NULL THEN
    RAISE EXCEPTION 'spatial entity ID is only valid for canonical spatial locations';
  END IF;

  SELECT se.event_id INTO v_event_id
  FROM sw_core.simulation_event se
  JOIN sw_core.event_type et USING(event_type_id)
  WHERE se.idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF NOT EXISTS (
      SELECT 1 FROM sw_core.simulation_event se
      JOIN sw_core.event_type et USING(event_type_id)
      WHERE se.event_id=v_event_id AND et.event_code='INCIDENT_LOCATION_ADDED'
        AND se.subject_kind='incident' AND se.subject_id=p_incident_id
    ) THEN
      RAISE EXCEPTION 'incident location idempotency key conflicts with another event';
    END IF;
    SELECT incident_location_id INTO v_location_id
    FROM sw_incident.incident_location
    WHERE source_event_id=v_event_id;
    IF NOT FOUND THEN
      RAISE EXCEPTION 'incident location event exists without its location record';
    END IF;
    RETURN v_location_id;
  END IF;

  SELECT * INTO v_runtime FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR v_runtime.state<>2 OR NOT v_runtime.player_present THEN
    RAISE EXCEPTION 'incident location recording requires running player-present simulation';
  END IF;
  SELECT * INTO v_incident FROM sw_incident.incident
  WHERE incident_id=p_incident_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'incident not found'; END IF;
  IF v_incident.status IN ('CLOSED','CANCELLED','DUPLICATE_LINKED') THEN
    RAISE EXCEPTION 'incident is not open for location updates';
  END IF;

  SELECT event_type_id INTO v_event_type_id FROM sw_core.event_type
  WHERE event_code='INCIDENT_LOCATION_ADDED';
  INSERT INTO sw_core.simulation_event(
    event_type_id,occurred_at,world_tick,subject_kind,subject_id,
    source_ref,attributes,idempotency_key
  ) VALUES (
    v_event_type_id,now(),v_runtime.world_tick,'incident',p_incident_id,
    p_source_ref,
    jsonb_build_object(
      'location_role',p_location_role,'location_type',p_location_type,
      'location_ref',p_location_ref,'spatial_id',p_spatial_id,
      'confidence',p_confidence,'authority_ref',p_authority_ref,
      'source_ref',p_source_ref,'address_source_ref',p_address_source_ref
    ),
    p_idempotency_key
  ) RETURNING event_id INTO v_event_id;

  INSERT INTO sw_incident.incident_location(
    incident_id,location_role,location_type,spatial_id,location_ref,
    raw_description,confidence,effective_tick,source_event_id,source_ref
  ) VALUES (
    p_incident_id,p_location_role,p_location_type,p_spatial_id,p_location_ref,
    p_raw_description,p_confidence,v_runtime.world_tick,v_event_id,p_source_ref
  ) RETURNING incident_location_id INTO v_location_id;

  UPDATE sw_runtime.state SET last_event_id=v_event_id,updated_at=now()
  WHERE singleton=1;
  RETURN v_location_id;
END
$bp12$;

CREATE FUNCTION sw_incident.incident_location_history(p_incident_id integer)
RETURNS TABLE (
  incident_location_id bigint,
  incident_id integer,
  location_role text,
  location_type text,
  spatial_id integer,
  location_ref text,
  raw_description text,
  confidence text,
  effective_tick bigint,
  source_event_id bigint,
  source_ref text,
  event_occurred_at timestamptz,
  event_source_ref text,
  event_attributes jsonb
)
LANGUAGE sql STABLE AS $bp12$
  SELECT l.incident_location_id,l.incident_id,l.location_role,l.location_type,
         l.spatial_id,l.location_ref,l.raw_description,l.confidence,
         l.effective_tick,l.source_event_id,l.source_ref,
         se.occurred_at,se.source_ref,se.attributes
  FROM sw_incident.incident_location l
  JOIN sw_core.simulation_event se ON se.event_id=l.source_event_id
  WHERE l.incident_id=p_incident_id
  ORDER BY l.effective_tick,l.incident_location_id
$bp12$;

INSERT INTO sw_core.event_type(event_code,description) VALUES
 ('DISPATCH_ACKNOWLEDGED','Dispatch assignment acknowledged by a responding unit'),
 ('UNIT_ARRIVED','Assigned field unit reported arrival at an incident')
ON CONFLICT(event_code) DO NOTHING;

CREATE FUNCTION sw_incident.record_operational_timeline_event(
  p_incident_id integer,
  p_event_code text,
  p_actor_ref text,
  p_authority_ref text,
  p_source_ref text,
  p_dispatch_ref text,
  p_unit_ref text,
  p_assignment_ref text,
  p_field_activity_ref text,
  p_description text,
  p_idempotency_key text
) RETURNS bigint
LANGUAGE plpgsql AS $bp12$
DECLARE
  v_runtime sw_runtime.state%ROWTYPE;
  v_incident sw_incident.incident%ROWTYPE;
  v_event_id bigint;
  v_event_type_id smallint;
BEGIN
  IF p_incident_id IS NULL OR p_incident_id<1
     OR p_event_code NOT IN ('DISPATCH_ACKNOWLEDGED','UNIT_ARRIVED')
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref))=0
     OR p_authority_ref IS NULL OR length(trim(p_authority_ref))=0
     OR p_source_ref IS NULL OR length(trim(p_source_ref))=0
     OR p_description IS NULL OR length(trim(p_description))=0
     OR p_idempotency_key IS NULL
     OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}
SELECT i.*,
       (SELECT count(*) FROM sw_incident.incident_location l WHERE l.incident_id=i.incident_id)::integer AS location_count,
       (SELECT count(*) FROM sw_incident.incident_source_link s WHERE s.incident_id=i.incident_id)::integer AS source_count
FROM sw_incident.incident i;

COMMIT;
 THEN
    RAISE EXCEPTION 'invalid incident operational timeline event';
  END IF;
  IF p_event_code='DISPATCH_ACKNOWLEDGED'
     AND (p_dispatch_ref IS NULL OR length(trim(p_dispatch_ref))=0) THEN
    RAISE EXCEPTION 'dispatch acknowledgement requires a dispatch reference';
  END IF;
  IF p_event_code='UNIT_ARRIVED'
     AND (p_unit_ref IS NULL OR length(trim(p_unit_ref))=0
          OR p_assignment_ref IS NULL OR length(trim(p_assignment_ref))=0
          OR p_field_activity_ref IS NULL OR length(trim(p_field_activity_ref))=0) THEN
    RAISE EXCEPTION 'unit arrival requires unit, deployment and field activity references';
  END IF;

  SELECT se.event_id INTO v_event_id
  FROM sw_core.simulation_event se
  WHERE se.idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF NOT EXISTS (
      SELECT 1 FROM sw_core.simulation_event se
      JOIN sw_core.event_type et USING(event_type_id)
      WHERE se.event_id=v_event_id AND et.event_code=p_event_code
        AND se.subject_kind='incident' AND se.subject_id=p_incident_id
        AND se.attributes->>'source_ref'=p_source_ref
    ) THEN
      RAISE EXCEPTION 'operational timeline idempotency key conflicts with another event';
    END IF;
    RETURN v_event_id;
  END IF;

  SELECT * INTO v_runtime FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR v_runtime.state<>2 OR NOT v_runtime.player_present THEN
    RAISE EXCEPTION 'operational event recording requires running player-present simulation';
  END IF;
  SELECT * INTO v_incident FROM sw_incident.incident
  WHERE incident_id=p_incident_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'incident not found'; END IF;
  IF v_incident.status IN ('CLOSED','CANCELLED','DUPLICATE_LINKED') THEN
    RAISE EXCEPTION 'incident is not open for operational updates';
  END IF;

  SELECT event_type_id INTO v_event_type_id FROM sw_core.event_type
  WHERE event_code=p_event_code;
  INSERT INTO sw_core.simulation_event(
    event_type_id,occurred_at,world_tick,subject_kind,subject_id,
    source_ref,attributes,idempotency_key
  ) VALUES (
    v_event_type_id,now(),v_runtime.world_tick,'incident',p_incident_id,
    p_source_ref,
    jsonb_strip_nulls(jsonb_build_object(
      'actor_ref',p_actor_ref,'authority_ref',p_authority_ref,
      'source_ref',p_source_ref,'dispatch_ref',p_dispatch_ref,
      'unit_ref',p_unit_ref,'assignment_ref',p_assignment_ref,
      'field_activity_ref',p_field_activity_ref,'description',p_description
    )),
    p_idempotency_key
  ) RETURNING event_id INTO v_event_id;

  UPDATE sw_runtime.state SET last_event_id=v_event_id,updated_at=now()
  WHERE singleton=1;
  RETURN v_event_id;
END
$bp12$;

CREATE FUNCTION sw_incident.operational_timeline(p_incident_id integer)
RETURNS TABLE (
  event_id bigint,
  incident_id integer,
  event_code text,
  occurred_at timestamptz,
  world_tick bigint,
  source_ref text,
  attributes jsonb
)
LANGUAGE sql STABLE AS $bp12$
  SELECT se.event_id,se.subject_id,et.event_code,se.occurred_at,se.world_tick,
         se.source_ref,se.attributes
  FROM sw_core.simulation_event se
  JOIN sw_core.event_type et USING(event_type_id)
  WHERE se.subject_kind='incident' AND se.subject_id=p_incident_id
    AND et.event_code IN ('DISPATCH_ACKNOWLEDGED','UNIT_ARRIVED')
  ORDER BY se.world_tick,se.event_id
$bp12$;

CREATE VIEW sw_incident.incident_current AS
SELECT i.*,
       (SELECT count(*) FROM sw_incident.incident_location l WHERE l.incident_id=i.incident_id)::integer AS location_count,
       (SELECT count(*) FROM sw_incident.incident_source_link s WHERE s.incident_id=i.incident_id)::integer AS source_count
FROM sw_incident.incident i;

COMMIT;
