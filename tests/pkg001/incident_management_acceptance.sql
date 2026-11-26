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
  v_assessment_event_id bigint;
  v_location_id bigint;
  v_second_location_id bigint;
  v_operational_event_id bigint;
  v_operational_replay_id bigint;
  v_status text;
  v_error text;
  v_handover_id bigint;
  v_handover_replay_id bigint;
  v_handover_document jsonb;
  v_bootstrap_open boolean;
BEGIN
  -- Activate the disposable runtime so positive incident and handover paths run.
  SELECT state,player_present,bootstrap_open INTO v_state,v_present,v_bootstrap_open
  FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF v_state=0 THEN
    UPDATE sw_runtime.state SET state=1 WHERE singleton=1;
    v_state:=1;
  END IF;
  IF v_state=1 THEN
    IF v_bootstrap_open THEN
      UPDATE sw_runtime.state SET bootstrap_open=false WHERE singleton=1;
    END IF;
    UPDATE sw_runtime.state SET state=2,player_present=true WHERE singleton=1;
    v_state:=2; v_present:=true;
  ELSIF NOT (v_state=2 AND v_present) THEN
    RAISE EXCEPTION 'BP12 acceptance fixture cannot activate runtime from state %, player_present %',v_state,v_present;
  END IF;
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
      'test:bp12','BP12-ACCEPTANCE-CREATE-001',NULL,'unknown','unclassified',3::smallint,
      'moderate','Fictional test location','SWPS-TEST-LOCATION','raw','unknown',NULL
    );
    SELECT status INTO v_status FROM sw_incident.incident WHERE incident_id=v_incident_id;
    IF v_status<>'RECEIVED'
       OR (SELECT count(*) FROM sw_incident.incident_assessment WHERE incident_id=v_incident_id)<>1
       OR (SELECT count(*) FROM sw_incident.incident_event WHERE incident_id=v_incident_id)<>1
       OR (SELECT count(*) FROM sw_incident.incident_source_link WHERE incident_id=v_incident_id)<>1
       OR (SELECT count(*) FROM sw_incident.incident_location WHERE incident_id=v_incident_id)<>1 THEN
      RAISE EXCEPTION 'BP12 incident creation did not create complete source/event/location lineage';
    END IF;
    v_location_id:=sw_incident.add_incident_location(
      v_incident_id,'secondary','property','SWADDR-TEST-002',NULL,
      'Fictional secondary test address','unverified',
      'test:bp12','test-authority','caller-stated:BP12-ACCEPTANCE-LOCATION-001',
      'bp04-address:SWADDR-TEST-002','BP12-ACCEPTANCE-LOCATION-001'
    );
    IF (SELECT count(*) FROM sw_incident.incident_location WHERE incident_id=v_incident_id)<>2
       OR NOT EXISTS(
         SELECT 1 FROM sw_incident.incident_location
         WHERE incident_location_id=v_location_id
           AND location_ref='SWADDR-TEST-002'
           AND confidence='unverified'
           AND source_ref='caller-stated:BP12-ACCEPTANCE-LOCATION-001'
           AND (SELECT attributes->>'address_source_ref' FROM sw_core.simulation_event
                WHERE event_id=sw_incident.incident_location.source_event_id)
                ='bp04-address:SWADDR-TEST-002'
       )
       OR NOT EXISTS(
         SELECT 1 FROM sw_core.simulation_event se
         JOIN sw_core.event_type et USING(event_type_id)
         WHERE se.event_id=(SELECT source_event_id FROM sw_incident.incident_location
                            WHERE incident_location_id=v_location_id)
           AND et.event_code='INCIDENT_LOCATION_ADDED'
           AND se.subject_kind='incident' AND se.subject_id=v_incident_id
       ) THEN
      RAISE EXCEPTION 'BP12 incident location event/provenance recording failed';
    END IF;
    IF (SELECT count(*) FROM sw_incident.incident_location_history(v_incident_id))<>2
       OR NOT EXISTS(
         SELECT 1 FROM sw_incident.incident_location_history(v_incident_id)
         WHERE incident_location_id=v_location_id
           AND event_attributes->>'address_source_ref'='bp04-address:SWADDR-TEST-002'
           AND event_source_ref='caller-stated:BP12-ACCEPTANCE-LOCATION-001'
       ) THEN
      RAISE EXCEPTION 'BP12 incident location history reader lost provenance or chronology';
    END IF;
    v_second_location_id:=sw_incident.add_incident_location(
      v_incident_id,'secondary','property','SWADDR-TEST-002',NULL,
      'Fictional secondary test address','unverified',
      'test:bp12','test-authority','caller-stated:BP12-ACCEPTANCE-LOCATION-001',
      'bp04-address:SWADDR-TEST-002','BP12-ACCEPTANCE-LOCATION-001'
    );
    IF v_second_location_id<>v_location_id
       OR (SELECT count(*) FROM sw_incident.incident_location WHERE incident_id=v_incident_id)<>2 THEN
      RAISE EXCEPTION 'BP12 incident location idempotency failed';
    END IF;
    BEGIN
      PERFORM sw_incident.add_incident_location(
        v_incident_id,'primary','canonical_spatial',NULL,NULL,
        'Missing canonical spatial identity','unknown',
        'test:bp12','test-authority','test-source','bp04-address:invalid','BP12-ACCEPTANCE-INVALID-SPATIAL'
      );
      RAISE EXCEPTION 'canonical spatial location without spatial ID was accepted';
    EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS v_error = MESSAGE_TEXT;
      IF v_error<>'canonical spatial location requires a spatial entity ID' THEN RAISE; END IF;
    END;
    v_operational_event_id:=sw_incident.record_operational_timeline_event(
      v_incident_id,'DISPATCH_ACKNOWLEDGED','dispatcher:4','dispatch-authority:9',
      'dispatch-ack:ACK-TEST-1','CAD-TEST-88',NULL,NULL,NULL,
      'Fictional unit acknowledged dispatch','BP12-ACCEPTANCE-DISPATCH-ACK-001'
    );
    v_operational_replay_id:=sw_incident.record_operational_timeline_event(
      v_incident_id,'DISPATCH_ACKNOWLEDGED','dispatcher:4','dispatch-authority:9',
      'dispatch-ack:ACK-TEST-1','CAD-TEST-88',NULL,NULL,NULL,
      'Fictional unit acknowledged dispatch','BP12-ACCEPTANCE-DISPATCH-ACK-001'
    );
    IF v_operational_replay_id<>v_operational_event_id
       OR (SELECT count(*) FROM sw_incident.operational_timeline(v_incident_id)
           WHERE event_code='DISPATCH_ACKNOWLEDGED')<>1
       OR NOT EXISTS(
         SELECT 1 FROM sw_incident.operational_timeline(v_incident_id)
         WHERE event_id=v_operational_event_id
           AND attributes->>'dispatch_ref'='CAD-TEST-88'
           AND attributes->>'actor_ref'='dispatcher:4'
       ) THEN
      RAISE EXCEPTION 'dispatch acknowledgement timeline/idempotency failed';
    END IF;
    v_operational_event_id:=sw_incident.record_operational_timeline_event(
      v_incident_id,'UNIT_ARRIVED','officer:12','patrol-order:5',
      'bp10-arrival:PATROL-ACT-19',NULL,'UNIT-7','DEP-4','PATROL-ACT-19',
      'Fictional unit arrived at incident','BP12-ACCEPTANCE-UNIT-ARRIVAL-001'
    );
    IF (SELECT count(*) FROM sw_incident.operational_timeline(v_incident_id)
        WHERE event_code='UNIT_ARRIVED')<>1
       OR NOT EXISTS(
         SELECT 1 FROM sw_incident.operational_timeline(v_incident_id)
         WHERE event_id=v_operational_event_id
           AND attributes->>'unit_ref'='UNIT-7'
           AND attributes->>'assignment_ref'='DEP-4'
           AND attributes->>'field_activity_ref'='PATROL-ACT-19'
       ) THEN
      RAISE EXCEPTION 'field unit arrival timeline provenance failed';
    END IF;
    BEGIN
      PERFORM sw_incident.record_operational_timeline_event(
        v_incident_id,'UNIT_ARRIVED','officer:12','patrol-order:5',
        'bp10-arrival:PATROL-ACT-20',NULL,'UNIT-7','DEP-4',NULL,
        'Missing BP10 field activity reference','BP12-ACCEPTANCE-INVALID-ARRIVAL'
      );
      RAISE EXCEPTION 'unit arrival without field activity reference was accepted';
    EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS v_error = MESSAGE_TEXT;
      IF v_error<>'unit arrival requires unit, deployment and field activity references' THEN RAISE; END IF;
    END;
    v_second_id:=sw_incident.create_incident(
      'system','BP12-ACCEPTANCE-001','Fictional test incident; no real occurrence.',
      'test:bp12','BP12-ACCEPTANCE-CREATE-001',NULL,'unknown','unclassified',3::smallint,
      'moderate','Fictional test location','SWPS-TEST-LOCATION','raw','unknown',NULL
    );
    IF v_second_id<>v_incident_id THEN RAISE EXCEPTION 'incident create idempotency failed'; END IF;
    v_assessment_event_id:=sw_incident.record_incident_assessment(
      v_incident_id,'public_safety',2::smallint,'high','high',
      'Test reassessment preserves source and prior assessment.',
      'test:bp12','test-authority','BP12-ACCEPTANCE-ASSESS-001',NULL
    );
    IF (SELECT count(*) FROM sw_incident.incident_assessment WHERE incident_id=v_incident_id)<>2
       OR (SELECT priority FROM sw_incident.incident WHERE incident_id=v_incident_id)<>2
       OR (SELECT severity_code FROM sw_incident.incident WHERE incident_id=v_incident_id)<>'high'
       OR (SELECT category_code FROM sw_incident.incident WHERE incident_id=v_incident_id)<>'public_safety' THEN
      RAISE EXCEPTION 'BP12 assessment history and current projection do not reconcile';
    END IF;
    IF sw_incident.record_incident_assessment(
      v_incident_id,'public_safety',2::smallint,'high','high',
      'Test reassessment preserves source and prior assessment.',
      'test:bp12','test-authority','BP12-ACCEPTANCE-ASSESS-001',NULL
    )<>v_assessment_event_id THEN RAISE EXCEPTION 'incident assessment idempotency failed'; END IF;
    v_event_id:=sw_incident.transition_incident(
      v_incident_id,'AWAITING_TRIAGE','test:bp12','test-authority','Initial triage queue test',
      'BP12-ACCEPTANCE-TRANSITION-001'
    );
    IF (SELECT status FROM sw_incident.incident WHERE incident_id=v_incident_id)<>'AWAITING_TRIAGE'
       OR (SELECT count(*) FROM sw_incident.incident_event WHERE incident_id=v_incident_id)<>3 THEN
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
    v_handover_document:=jsonb_build_object(
      'handover_ref','BP12-HANDOVER-TEST-001',
      'incident_id',v_incident_id,
      'incident_status','AWAITING_TRIAGE',
      'outgoing_commander_ref','commander:outgoing',
      'incoming_commander_ref','commander:incoming',
      'prepared_by_ref','supervisor:prepared',
      'authority_ref','command-authority:test',
      'source_ref','command-room:handover-test',
      'effective_world_tick',(SELECT world_tick FROM sw_runtime.state WHERE singleton=1),
      'assignment_reconciliation',jsonb_build_object('incident_id',v_incident_id,'handover_ready',true,'as_of_world_tick',
        (SELECT world_tick FROM sw_runtime.state WHERE singleton=1),'unresolved_active_assignments',jsonb_build_array()),
      'commander_decisions',jsonb_build_array(),
      'outstanding_actions',jsonb_build_array(),
      'responsibility_transfers',jsonb_build_array(jsonb_build_object(
        'record_ref','transfer:test:1','responsibility_ref','incident-command',
        'from_ref','commander:outgoing','to_ref','commander:incoming',
        'actor_ref','commander:outgoing','source_ref','command-room:transfer','world_tick',
        (SELECT world_tick FROM sw_runtime.state WHERE singleton=1))),
      'acknowledgements',jsonb_build_array(jsonb_build_object(
        'record_ref','ack:test:1','handover_ref','BP12-HANDOVER-TEST-001',
        'recipient_ref','commander:incoming','acknowledgement','ACCEPTED',
        'actor_ref','commander:incoming','source_ref','command-room:ack',
        'world_tick',(SELECT world_tick FROM sw_runtime.state WHERE singleton=1),'notes','Accepted')),
      'handover_ready',true,'record_status','PROJECTED_NOT_PERSISTED','read_only',true
    );
    v_handover_id:=sw_incident.record_command_handover(
      v_incident_id,'BP12-HANDOVER-TEST-001','commander:outgoing','commander:incoming',
      'supervisor:prepared','command-authority:test','command-room:handover-test',
      (SELECT world_tick FROM sw_runtime.state WHERE singleton=1),v_handover_document,
      'BP12-HANDOVER-IDEMPOTENCY-001'
    );
    v_handover_replay_id:=sw_incident.record_command_handover(
      v_incident_id,'BP12-HANDOVER-TEST-001','commander:outgoing','commander:incoming',
      'supervisor:prepared','command-authority:test','command-room:handover-test',
      (SELECT world_tick FROM sw_runtime.state WHERE singleton=1),v_handover_document,
      'BP12-HANDOVER-IDEMPOTENCY-001'
    );
    IF v_handover_replay_id<>v_handover_id
       OR (SELECT count(*) FROM sw_incident.command_handover WHERE incident_id=v_incident_id)<>1
       OR NOT EXISTS (
         SELECT 1 FROM sw_incident.command_handover_history(v_incident_id)
         WHERE command_handover_id=v_handover_id
           AND handover_document->>'record_status'='PERSISTED'
           AND handover_document->>'incoming_commander_ref'='commander:incoming'
           AND source_event_id IS NOT NULL AND occurred_at IS NOT NULL
           AND event_world_tick >= effective_world_tick
       ) THEN
      RAISE EXCEPTION 'BP12 command handover persistence, history or idempotency failed';
    END IF;
    BEGIN
      PERFORM sw_incident.record_command_handover(
        v_incident_id,'BP12-HANDOVER-TEST-001','commander:outgoing','commander:incoming',
        'supervisor:prepared','command-authority:test','command-room:handover-test',
        (SELECT world_tick FROM sw_runtime.state WHERE singleton=1),
        jsonb_set(v_handover_document,'{acknowledgements,0,notes}','"Changed replay payload"'::jsonb,true),
        'BP12-HANDOVER-IDEMPOTENCY-001'
      );
      RAISE EXCEPTION 'conflicting command handover idempotency replay was accepted';
    EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS v_error = MESSAGE_TEXT;
      IF v_error<>'command handover idempotency key conflicts with prior record' THEN RAISE; END IF;
    END;
    BEGIN
      UPDATE sw_incident.command_handover SET source_ref='tampered' WHERE command_handover_id=v_handover_id;
      RAISE EXCEPTION 'BP12 command handover update was accepted';
    EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS v_error = MESSAGE_TEXT;
      IF v_error NOT LIKE '%append-only%' THEN RAISE; END IF;
    END;
    BEGIN
      DELETE FROM sw_incident.command_handover WHERE command_handover_id=v_handover_id;
      RAISE EXCEPTION 'BP12 command handover delete was accepted';
    EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS v_error = MESSAGE_TEXT;
      IF v_error NOT LIKE '%append-only%' THEN RAISE; END IF;
    END;
    BEGIN
      TRUNCATE TABLE sw_incident.command_handover;
      RAISE EXCEPTION 'BP12 command handover truncate was accepted';
    EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS v_error = MESSAGE_TEXT;
      IF v_error NOT LIKE '%append-only%' THEN RAISE; END IF;
    END;
    BEGIN
      PERFORM sw_incident.record_command_handover(
        v_incident_id,'BP12-HANDOVER-INVALID-002','commander:outgoing','commander:incoming',
        'supervisor:prepared','command-authority:test','command-room:handover-test',
        (SELECT world_tick FROM sw_runtime.state WHERE singleton=1),
        jsonb_set(v_handover_document,'{handover_ready}','false'::jsonb,true),
        'BP12-HANDOVER-INVALID-IDEMPOTENCY'
      );
      RAISE EXCEPTION 'unready command handover was accepted';
    EXCEPTION WHEN OTHERS THEN
      GET STACKED DIAGNOSTICS v_error = MESSAGE_TEXT;
      IF v_error<>'command handover is not accepted and ready for transfer' THEN RAISE; END IF;
    END;
  ELSE
    BEGIN
      PERFORM sw_incident.create_incident(
        'system','BP12-ACCEPTANCE-001','Fictional test incident; no real occurrence.',
        'test:bp12','BP12-ACCEPTANCE-CREATE-001',NULL,'unknown','unclassified',3::smallint,
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
DO $bp12$
BEGIN
  IF (SELECT count(*) FROM sw_incident.incident)<>0 THEN RAISE EXCEPTION 'BP12 acceptance transaction leaked a test incident'; END IF;
END
$bp12$;
SELECT 'BP12 incident schema and runtime-boundary acceptance passed' AS result;
