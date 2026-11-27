\set ON_ERROR_STOP on
BEGIN;
UPDATE sw_runtime.state SET state=1,player_present=false
WHERE singleton=1 AND state=0 AND bootstrap_open=true AND world_tick=0;
UPDATE sw_runtime.state SET state=2,player_present=true,bootstrap_open=false
WHERE singleton=1 AND state=1 AND bootstrap_open=true AND world_tick=0;
DO $$
DECLARE v_person integer; v_tier smallint; v_promoted boolean;
BEGIN
 v_person:=sw_people.create_person('Avery','Example','BP03-TIER-ACCEPTANCE:PERSON',
  'test:bp03','Disposable BP03 tier and promotion acceptance');
 IF NOT EXISTS(SELECT 1 FROM sw_people.person_simulation_summary
   WHERE person_id=v_person AND detail_tier=0 AND NOT permanently_promoted)
  OR NOT EXISTS(SELECT 1 FROM sw_people.person_simulation_state
   WHERE person_id=v_person AND detail_tier=0)
  OR NOT EXISTS(SELECT 1 FROM sw_people.person_simulation_history
   WHERE person_id=v_person AND prior_tier IS NULL AND new_tier=0 AND trigger_kind='person_created') THEN
  RAISE EXCEPTION 'new person must persist registry tier 0 and its creation history';
 END IF;
 v_tier:=sw_people.set_person_detail_tier(v_person,1::smallint,'routine_profile',
  'fixture:routine-1','Routine simulation enabled','test:bp03','BP03-TIER:ROUTINE');
 IF v_tier<>1 THEN RAISE EXCEPTION 'tier 1 transition failed'; END IF;
 v_promoted:=sw_people.promote_person_persistently(v_person,'witness',
  'fixture:incident-1','Person is a material witness','test:bp03','BP03-PROMOTION:WITNESS');
 IF NOT v_promoted THEN RAISE EXCEPTION 'first permanent promotion was not recorded'; END IF;
 IF NOT EXISTS(SELECT 1 FROM sw_people.person_simulation_summary
   WHERE person_id=v_person AND detail_tier=3 AND permanently_promoted
    AND trigger_kind='witness' AND trigger_ref='fixture:incident-1') THEN
  RAISE EXCEPTION 'promotion must permanently set tier 3 and retain its trigger';
 END IF;
 IF sw_people.promote_person_persistently(v_person,'witness','fixture:incident-1',
   'Idempotent retry','test:bp03','BP03-PROMOTION:WITNESS-RETRY') THEN
  RAISE EXCEPTION 'duplicate promotion must be idempotent';
 END IF;
 BEGIN
  PERFORM sw_people.set_person_detail_tier(v_person,2::smallint,'case_closed','fixture:incident-1',
   'Attempted downgrade','test:bp03','BP03-TIER:DOWNGRADE');
  RAISE EXCEPTION 'tier 3 downgrade unexpectedly succeeded';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM='tier 3 downgrade unexpectedly succeeded' THEN RAISE; END IF;
 END;
 IF (SELECT count(*) FROM sw_people.person_simulation_history WHERE person_id=v_person)<>3 THEN
  RAISE EXCEPTION 'expected initial tier 0, 0->1 and 1->3 append-only history';
 END IF;
 IF (SELECT count(*) FROM sw_people.person_relevance_promotion WHERE person_id=v_person)<>1 THEN
  RAISE EXCEPTION 'expected exactly one permanent promotion record';
 END IF;
END $$;
ROLLBACK;
