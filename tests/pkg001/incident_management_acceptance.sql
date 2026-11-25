\set ON_ERROR_STOP on
BEGIN;
DO $bp12$
DECLARE
  v_count integer;
  v_state smallint;
  v_present boolean;
  v_incident_id integer;
  v_second_id integer;
  v_event_id bigint;
  v_status text;
  v_error text;
BEGIN
  IF to_regclass('sw_incident.incident') IS NULL
     OR to_regclass('sw_incident.incident_event') IS NULL
     OR to_regclass('sw_incident.incident_source_link') IS NULL
     OR to_regclass('sw_incident.incident_location') IS NULL
     OR to_regclass('sw_incident.incident_party') IS NULL
     OR to_regclass('sw_incident.incident_decision') IS NULL
     OR to_regclass('sw_incident.incident_current') IS NULL THEN
    RAISE EXCEPTION 'BP12 incident schema is incomplete';
  END IF;
  SELECT count(*) INTO v_count FROM sw_core.event_type
  WHERE event_code IN ('INCIDENT_CREATED','INCIDENT_STATE_CHANGED','INCIDENT_ASSESSMENT_RECORDED',
    'INCIDENT_LOCATION_ADDED','INCIDENT_PARTY_LINKED','INCIDENT_DECISION_RECORDED',
    'INCIDENT_SOURCE_LINKED','INCIDENT_DUPLICATE_LINKED','INCIDENT_REOPENED');
  IF v_count<>9 THEN RAISE EXCEPTION 'BP12 incident event vocabulary incomplete'; END IF;
  IF (SELECT count(*) FROM sw_incident.incident)<>0
     OR (SELECT count(*) FROM sw_incident.incident_event)<>0
     OR (SELECT count(*) FROM sw_incident.incident_source_link)<>0 THEN
    RAISE EXCEPTION 'BP12 schema migration must not invent incident records';
  END IF;
  SELECT state,player_present INTO v_state,v_present FROM sw_runtime.state WHERE singleton=1;
  IF v_state=2 AND v_present THEN
    v_incident_id:=sw_incident.create_incident(
      'system','BP12-ACCEPTANCE-001','Fictional test incident; no real occurrence.',
      'test:bp12','BP12-ACCEPTANCE-CREATE-001',NULL,'unknown','unclassified',3,
      'moderate','Fictional test location','SWPS-TEST-LOCATION','raw','unknown',NULL
    );
    SELECT status INTO v_status FROM sw_incident.incident WHERE incident_id=v_incident_id;
    IF v_status<>'RECEIVED'
       OR (SELECT count(*) FROM sw_incident.incident_event WHERE incident_id=v_incident_id)<>1
       OR (SELECT count(*) FROM sw_incident.incident_source_link WHERE incident_id=v_incident_id)<>1
       OR (SELECT count(*) FROM sw_incident.incident_location WHERE incident_id=v_incident_id)<>1 THEN
      RAISE EXCEPTION 'BP12 incident creation did not create complete source/event/location lineage';
    END IF;
    v_second_id:=sw_incident.create_incident(
      'system','BP12-ACCEPTANCE-001','Fictional test incident; no real occurrence.',
      'test:bp12','BP12-ACCEPTANCE-CREATE-001',NULL,'unknown','unclassified',3,
      'moderate','Fictional test location','SWPS-TEST-LOCATION','raw','unknown',NULL
    );
    IF v_second_id<>v_incident_id THEN RAISE EXCEPTION 'incident create idempotency failed'; END IF;
    v_event_id:=sw_incident.transition_incident(
      v_incident_id,'AWAITING_TRIAGE','test:bp12','test-authority','Initial triage queue test',
      'BP12-ACCEPTANCE-TRANSITION-001'
    );
    IF (SELECT status FROM sw_incident.incident WHERE incident_id=v_incident_id)<>'AWAITING_TRIAGE'
       OR (SELECT count(*) FROM sw_incident.incident_event WHERE incident_id=v_incident_id)<>2 THEN
      RAISE EXCEPTION 'BP12 state transition/event projection failed';
    END IF;
    IF sw_incident.transition_incident(
      v_incident_id,'AWAITING_TRIAGE','test:bp12','test-authority','Initial triage queue test',
      'BP12-ACCEPTANCE-TRANSITION-001'
    )<>v_event_id THEN RAISE EXCEPTION 'incident transition idempotency failed'; END IF;
    BEGIN
      PERFORM sw_incident.transition_incident(
        v_incident_id,'RECEIVED','test:bp12','test-authority','Invalid backwards transition',
        'BP12-ACCEPTANCE-INVALID-001'
      );
      RAISE EXCEPTION 'invalid backwards incident transition was accepted';
    EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS v_error = MESSAGE_TEXT;
      IF v_error NOT LIKE 'invalid incident state transition:%' THEN RAISE; END IF;
    END;
  ELSE
    BEGIN
      PERFORM sw_incident.create_incident(
        'system','BP12-ACCEPTANCE-001','Fictional test incident; no real occurrence.',
        'test:bp12','BP12-ACCEPTANCE-CREATE-001',NULL,'unknown','unclassified',3,
        'moderate','Fictional test location','SWPS-TEST-LOCATION','raw','unknown',NULL
      );
      RAISE EXCEPTION 'incident intake was accepted while runtime was not active';
    EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS v_error = MESSAGE_TEXT;
      IF v_error<>'incident intake requires running player-present simulation' THEN RAISE; END IF;
    END;
  END IF;
END
$bp12$;
ROLLBACK;
DO $bp12$\nBEGIN\n  IF (SELECT count(*) FROM sw_incident.incident)<>0 THEN RAISE EXCEPTION 'BP12 acceptance transaction leaked a test incident'; END IF;\nEND\n$bp12$;\nSELECT 'BP12 incident schema and runtime-boundary acceptance passed' AS result;
