\set ON_ERROR_STOP on
BEGIN;
UPDATE sw_runtime.state SET state=1,player_present=false
WHERE singleton=1 AND state=0 AND bootstrap_open=true AND world_tick=0;
UPDATE sw_runtime.state SET state=2,player_present=true,bootstrap_open=false
WHERE singleton=1 AND state=1 AND bootstrap_open=true AND world_tick=0;
DO $$
DECLARE v_person integer; v_source integer; v_source_event bigint; v_claim1 bigint; v_claim2 bigint; v_retry bigint;
BEGIN
 v_person:=sw_people.create_person('Jordan','Claims','BP03-CLAIM-ACCEPTANCE:PERSON',
  'test:bp03','Disposable BP03 attribute claim target');
 v_source:=sw_people.create_person('Casey','Source','BP03-CLAIM-ACCEPTANCE:SOURCE',
  'test:bp03','Disposable BP03 attribute source');
 SELECT last_event_id INTO STRICT v_source_event FROM sw_people.person WHERE person_id=v_source;
 v_claim1:=sw_people.record_person_attribute_claim(v_person,'age_range',
  '{"minimum":28,"maximum":34}'::jsonb,'estimated',0.650,0,v_source_event,NULL,
  'BP03-CLAIM:AGE-ESTIMATE','test:bp03','An estimated age range from a fictional source');
 v_retry:=sw_people.record_person_attribute_claim(v_person,'age_range',
  '{"minimum":28,"maximum":34}'::jsonb,'estimated',0.650,0,v_source_event,NULL,
  'BP03-CLAIM:AGE-ESTIMATE','test:bp03','Idempotent replay');
 IF v_claim1<>v_retry THEN RAISE EXCEPTION 'attribute claim replay created a duplicate'; END IF;
 v_claim2:=sw_people.record_person_attribute_claim(v_person,'age_range',
  '{"minimum":31,"maximum":37}'::jsonb,'disputed',0.400,0,v_source_event,NULL,
  'BP03-CLAIM:AGE-DISPUTED','test:bp03','A conflicting sourced claim');
 IF v_claim1=v_claim2 THEN RAISE EXCEPTION 'conflicting claims collapsed to one identity'; END IF;
 IF (SELECT count(*) FROM sw_people.person_attribute_claim
  WHERE person_id=v_person AND attribute_code='age_range')<>2 THEN
  RAISE EXCEPTION 'conflicting age claims were not preserved independently';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM sw_people.person_attribute_claim_summary
  WHERE person_id=v_person AND attribute_code='age_range'
   AND claim_count=2 AND disputed_claim_count=1) THEN
  RAISE EXCEPTION 'attribute claim summary did not reconcile';
 END IF;
 BEGIN
  UPDATE sw_people.person_attribute_claim SET confidence=0.99 WHERE claim_id=v_claim1;
  RAISE EXCEPTION 'attribute claim mutation unexpectedly accepted';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM='attribute claim mutation unexpectedly accepted' THEN RAISE; END IF;
 END;
END $$;
ROLLBACK;
