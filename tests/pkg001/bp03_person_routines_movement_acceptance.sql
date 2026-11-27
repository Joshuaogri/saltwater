\set ON_ERROR_STOP on
BEGIN;
UPDATE sw_runtime.state SET state=1,player_present=false
WHERE singleton=1 AND state=0 AND bootstrap_open=true AND world_tick=0;
UPDATE sw_runtime.state SET state=2,player_present=true,bootstrap_open=false
WHERE singleton=1 AND state=1 AND bootstrap_open=true AND world_tick=0;
DO $$
DECLARE v_person integer; v_routine bigint; v_retry bigint; v_successor bigint; v_move bigint;
BEGIN
 v_person:=sw_people.create_person('Morgan','Routine','BP03-ROUTINE-ACCEPTANCE:PERSON',
  'test:bp03','Disposable BP03 routine and movement acceptance');
 v_routine:=sw_people.record_person_routine(v_person,'workday','SW-LOC:WORKPLACE-01',
  '{"days":["mon","tue","wed","thu","fri"],"start":"09:00","end":"17:00","timezone":"simulation"}'::jsonb,
  0,NULL,NULL,'BP03-ROUTINE:WORKDAY','test:bp03','Fixture schedule only; not proof of attendance');
 v_retry:=sw_people.record_person_routine(v_person,'workday','SW-LOC:WORKPLACE-01',
  '{"days":["mon","tue","wed","thu","fri"],"start":"09:00","end":"17:00","timezone":"simulation"}'::jsonb,
  0,NULL,NULL,'BP03-ROUTINE:WORKDAY','test:bp03','Idempotent replay');
 IF v_routine<>v_retry THEN RAISE EXCEPTION 'routine replay created a duplicate'; END IF;
 IF NOT EXISTS(SELECT 1 FROM sw_people.person_routine_current
   WHERE routine_id=v_routine AND person_id=v_person) THEN
  RAISE EXCEPTION 'current routine view did not return the routine';
 END IF;
 v_successor:=sw_people.record_person_routine(v_person,'home_evening','SW-LOC:HOME-01',
  '{"days":["mon","tue","wed","thu","fri"],"start":"18:00","end":"22:00","timezone":"simulation"}'::jsonb,
  0,NULL,v_routine,'BP03-ROUTINE:HOME-EVENING','test:bp03','Routine successor fixture');
 IF EXISTS(SELECT 1 FROM sw_people.person_routine_current WHERE routine_id=v_routine)
  OR NOT EXISTS(SELECT 1 FROM sw_people.person_routine_current WHERE routine_id=v_successor) THEN
  RAISE EXCEPTION 'routine successor did not replace the prior current routine';
 END IF;
 v_move:=sw_people.record_person_movement(v_person,'SW-LOC:HOME-01','SW-LOC:WORKPLACE-01',
  'estimated','walking',0.750,0,'BP03-MOVEMENT:COMMUTE','test:bp03',
  'Fixture movement estimate; not verified presence');
 IF NOT EXISTS(SELECT 1 FROM sw_people.person_movement_summary
   WHERE person_id=v_person AND movement_event_count=1 AND latest_movement_tick=0) THEN
  RAISE EXCEPTION 'movement summary did not reconcile';
 END IF;
 IF (SELECT movement_kind FROM sw_people.person_movement_event WHERE movement_id=v_move)<>'estimated' THEN
  RAISE EXCEPTION 'movement certainty was not preserved';
 END IF;
 BEGIN
  PERFORM sw_people.record_person_movement(v_person,'SW-LOC:WORKPLACE-01','SW-LOC:HOME-01',
   'observed','walking',1.0,1,'BP03-MOVEMENT:FUTURE','test:bp03','Future movement should fail');
  RAISE EXCEPTION 'future movement unexpectedly accepted';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM='future movement unexpectedly accepted' THEN RAISE; END IF;
 END;
 BEGIN
  UPDATE sw_people.person_routine SET reason='tampered' WHERE routine_id=v_routine;
  RAISE EXCEPTION 'routine mutation unexpectedly accepted';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM='routine mutation unexpectedly accepted' THEN RAISE; END IF;
 END;
 IF (SELECT count(*) FROM sw_people.person_routine WHERE person_id=v_person)<>2
  OR (SELECT count(*) FROM sw_people.person_movement_event WHERE person_id=v_person)<>1 THEN
  RAISE EXCEPTION 'routine or movement counts do not reconcile';
 END IF;
END $$;
ROLLBACK;
