-- BP03 distinct population-union and canonical-person service acceptance.
-- Disposable PostgreSQL only. All test records are rolled back.
\set ON_ERROR_STOP on
BEGIN;
DO $bp03$
DECLARE v_person_id integer; v_replayed_id integer; v_count integer; v_history_count integer;
BEGIN
 UPDATE sw_runtime.state SET state=1,player_present=false
 WHERE singleton=1 AND state=0 AND bootstrap_open=true AND world_tick=0;
 v_person_id:=sw_people.create_person('Zelvian','Meren','BP03-UNION-TEST:person:1',
  'bp03-ci','distinct population union acceptance','Qorveth');
 v_replayed_id:=sw_people.create_person('Zelvian','Meren','BP03-UNION-TEST:person:1',
  'bp03-ci','idempotent create replay','Qorveth');
 IF v_person_id<>v_replayed_id THEN RAISE EXCEPTION 'person creation replay changed identity'; END IF;
 IF (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>0 THEN
  RAISE EXCEPTION 'unqualified living identity must not count';
 END IF;
 v_count:=sw_people.set_population_qualifications(v_person_id,true,false,false,
  'BP03-UNION-TEST:resident','bp03-ci','usual residence');
 IF v_count<>1 THEN RAISE EXCEPTION 'resident count mismatch: %',v_count; END IF;
 v_count:=sw_people.set_population_qualifications(v_person_id,true,true,false,
  'BP03-UNION-TEST:presence','bp03-ci','presence overlaps residence');
 IF v_count<>1 THEN RAISE EXCEPTION 'resident plus presence must count once: %',v_count; END IF;
 v_count:=sw_people.set_population_qualifications(v_person_id,true,true,true,
  'BP03-UNION-TEST:police','bp03-ci','police membership overlaps both');
 IF v_count<>1 THEN RAISE EXCEPTION 'three-way overlap must count once: %',v_count; END IF;
 v_count:=sw_people.set_population_qualifications(v_person_id,false,true,true,
  'BP03-UNION-TEST:move-out','bp03-ci','remove residence only');
 IF v_count<>1 THEN RAISE EXCEPTION 'other qualifications must preserve count: %',v_count; END IF;
 v_count:=sw_people.set_population_qualifications(v_person_id,false,false,true,
  'BP03-UNION-TEST:exit','bp03-ci','physical exit');
 IF v_count<>1 THEN RAISE EXCEPTION 'active police member must remain counted: %',v_count; END IF;
 v_count:=sw_people.set_population_qualifications(v_person_id,false,false,false,
  'BP03-UNION-TEST:separation','bp03-ci','remove final qualification');
 IF v_count<>0 THEN RAISE EXCEPTION 'final qualification removal mismatch: %',v_count; END IF;
 v_count:=sw_people.set_population_qualifications(v_person_id,false,true,false,
  'BP03-UNION-TEST:arrival','bp03-ci','nonresident arrival');
 IF v_count<>1 THEN RAISE EXCEPTION 'nonresident arrival mismatch: %',v_count; END IF;
 v_count:=sw_people.record_person_death(v_person_id,'BP03-UNION-TEST:death',
  'bp03-ci','death preserves identity and removes living count');
 IF v_count<>0 THEN RAISE EXCEPTION 'death count mismatch: %',v_count; END IF;
 IF NOT EXISTS(SELECT 1 FROM sw_people.person p JOIN sw_people.population_state s USING(person_id)
  WHERE p.person_id=v_person_id AND s.life_status=2 AND NOT s.usual_resident
   AND NOT s.physically_present AND NOT s.active_police_service) THEN
  RAISE EXCEPTION 'death must preserve identity and clear qualifications';
 END IF;
 BEGIN
  PERFORM sw_people.set_population_qualifications(v_person_id,true,false,false,
   'BP03-UNION-TEST:resurrection','bp03-ci','deceased cannot be requalified');
  RAISE EXCEPTION 'deceased person was incorrectly requalified';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM='deceased person was incorrectly requalified' THEN RAISE; END IF;
 END;
 SELECT count(*) INTO v_history_count FROM sw_people.population_qualification_history WHERE person_id=v_person_id;
 IF v_history_count<>8 THEN RAISE EXCEPTION 'expected eight qualification history transitions, got %',v_history_count; END IF;
 IF (SELECT total_living_countable FROM sw_people.population_summary)<>0
  OR (SELECT active_police_service_members FROM sw_people.population_summary)<>0 THEN
  RAISE EXCEPTION 'population summary did not reconcile after death';
 END IF;
 RAISE NOTICE 'BP03_POPULATION_UNION_PASS person_id=% qualification_transitions=% final_population=0',
  v_person_id,v_history_count;
END $bp03$;
ROLLBACK;
