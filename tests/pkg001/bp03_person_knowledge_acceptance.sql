\set ON_ERROR_STOP on
BEGIN;
UPDATE sw_runtime.state SET state=1,player_present=false
WHERE singleton=1 AND state=0 AND bootstrap_open=true AND world_tick=0;
UPDATE sw_runtime.state SET state=2,player_present=true,bootstrap_open=false
WHERE singleton=1 AND state=1 AND bootstrap_open=true AND world_tick=0;
DO $$
DECLARE v_person integer; v_source_person integer; v_source_event bigint;
 v_knowledge bigint; v_retry bigint;
BEGIN
 v_person:=sw_people.create_person('Taylor','Knowledge','BP03-KNOWLEDGE-ACCEPTANCE:RECIPIENT',
  'test:bp03','Disposable BP03 knowledge recipient');
 v_source_person:=sw_people.create_person('Riley','Source','BP03-KNOWLEDGE-ACCEPTANCE:SOURCE',
  'test:bp03','Disposable BP03 knowledge source');
 SELECT last_event_id INTO STRICT v_source_event FROM sw_people.person WHERE person_id=v_source_person;
 v_knowledge:=sw_people.record_person_knowledge(v_person,'received',
  'SW-INFO:FIXTURE:STATEMENT-01',v_source_event,v_source_person,0,0.850,
  'BP03-KNOWLEDGE:RECEIVED-01','test:bp03',
  'Recipient was told the referenced fact by the source person');
 v_retry:=sw_people.record_person_knowledge(v_person,'received',
  'SW-INFO:FIXTURE:STATEMENT-01',v_source_event,v_source_person,0,0.850,
  'BP03-KNOWLEDGE:RECEIVED-01','test:bp03','Idempotent replay');
 IF v_knowledge<>v_retry THEN RAISE EXCEPTION 'knowledge replay created a duplicate'; END IF;
 IF NOT EXISTS(SELECT 1 FROM sw_people.person_knowledge_item
  WHERE knowledge_id=v_knowledge AND person_id=v_person AND source_event_id=v_source_event
   AND source_person_id=v_source_person AND acquired_tick=0 AND confidence=0.850) THEN
  RAISE EXCEPTION 'knowledge source, recipient, time or confidence was not preserved';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM sw_people.person_knowledge_summary
  WHERE person_id=v_person AND knowledge_item_count=1 AND latest_acquisition_tick=0) THEN
  RAISE EXCEPTION 'knowledge summary did not reconcile';
 END IF;
 BEGIN
  UPDATE sw_people.person_knowledge_item SET confidence=0.1 WHERE knowledge_id=v_knowledge;
  RAISE EXCEPTION 'knowledge mutation unexpectedly accepted';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM='knowledge mutation unexpectedly accepted' THEN RAISE; END IF;
 END;
 IF (SELECT count(*) FROM sw_people.person_knowledge_item WHERE person_id=v_person)<>1 THEN
  RAISE EXCEPTION 'knowledge item count does not reconcile';
 END IF;
END $$;
ROLLBACK;
