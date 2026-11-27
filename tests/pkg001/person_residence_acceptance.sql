\set ON_ERROR_STOP on
BEGIN;
DO $bp03$
DECLARE v_person integer; v_residence bigint; v_replayed bigint; v_count integer;
BEGIN
 INSERT INTO sw_geo.bp02_parcel(source_id,operational_status,record)
 VALUES('BP03-RES-TEST:PARCEL','ACTIVE_IN_GAME','{"test_fixture":true}');
 INSERT INTO sw_geo.bp02_address(source_id,parcel_source_id,operational_status,record)
 VALUES
 ('BP03-RES-TEST:ADDRESS-1','BP03-RES-TEST:PARCEL','ACTIVE_IN_GAME','{"test_fixture":true,"label":"Fixture address one"}'),
 ('BP03-RES-TEST:ADDRESS-2','BP03-RES-TEST:PARCEL','ACTIVE_IN_GAME','{"test_fixture":true,"label":"Fixture address two"}');
 v_person:=sw_people.create_person('Tavren','Solmere','BP03-RES-TEST:PERSON',
  'bp03-residence-ci','BP02 address-linked residence acceptance','Elyndra');
 v_residence:=sw_people.set_person_residence(v_person,'BP03-RES-TEST:ADDRESS-1','permanent',
  'BP03-RES-TEST:ASSIGN-1','bp03-residence-ci','initial address assignment');
 v_replayed:=sw_people.set_person_residence(v_person,'BP03-RES-TEST:ADDRESS-1','permanent',
  'BP03-RES-TEST:ASSIGN-1','bp03-residence-ci','idempotent assignment replay');
 IF v_residence<>v_replayed THEN RAISE EXCEPTION 'residence replay changed residence identity'; END IF;
 IF (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>1
  OR NOT (SELECT usual_resident FROM sw_people.population_state WHERE person_id=v_person) THEN
  RAISE EXCEPTION 'residence assignment did not create one usual-resident count';
 END IF;
 v_residence:=sw_people.set_person_residence(v_person,'BP03-RES-TEST:ADDRESS-2','temporary',
  'BP03-RES-TEST:ASSIGN-2','bp03-residence-ci','move to second address');
 IF (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>1 THEN
  RAISE EXCEPTION 'moving residence must not double-count or remove person';
 END IF;
 IF (SELECT count(*) FROM sw_people.person_residence WHERE person_id=v_person AND residence_status='ended')<>1
  OR NOT EXISTS(SELECT 1 FROM sw_people.person_residence WHERE person_id=v_person
   AND address_source_id='BP03-RES-TEST:ADDRESS-2' AND residence_status='current') THEN
  RAISE EXCEPTION 'residence move did not close prior and open current address';
 END IF;
 PERFORM sw_people.set_population_qualifications(v_person,true,true,false,
  'BP03-RES-TEST:PHYSICAL-PRESENCE','bp03-residence-ci','person is physically present');
 v_count:=sw_people.end_person_residence(v_person,'BP03-RES-TEST:END',
  'bp03-residence-ci','end current residence while person remains present');
 IF v_count<>1 OR (SELECT usual_resident FROM sw_people.population_state WHERE person_id=v_person)
  OR NOT (SELECT physically_present FROM sw_people.population_state WHERE person_id=v_person) THEN
  RAISE EXCEPTION 'ending residence incorrectly removed a physically present person';
 END IF;
 v_count:=sw_people.set_population_qualifications(v_person,false,false,false,
  'BP03-RES-TEST:DEPART','bp03-residence-ci','person leaves Saltwater');
 IF v_count<>0 THEN RAISE EXCEPTION 'final departure did not remove countable person'; END IF;
 IF (SELECT count(*) FROM sw_people.person_residence_history WHERE person_id=v_person)<>3 THEN
  RAISE EXCEPTION 'expected assignment, move and end residence history';
 END IF;
 IF (SELECT total_living_countable FROM sw_people.population_summary)<>0 THEN
  RAISE EXCEPTION 'population summary failed residence reconciliation';
 END IF;
 RAISE NOTICE 'BP03_BP02_RESIDENCE_LINK_PASS person_id=% residence_id=% history_events=3',
  v_person,v_residence;
END
$bp03$;
ROLLBACK;
