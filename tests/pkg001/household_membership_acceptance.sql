-- BP03 household disposable acceptance: exercised by PKG-001.
\set ON_ERROR_STOP on
BEGIN;
UPDATE sw_runtime.state SET state=1,player_present=false
 WHERE singleton=1 AND state=0 AND bootstrap_open=true AND world_tick=0;
UPDATE sw_runtime.state SET bootstrap_open=false,state=2,player_present=true
 WHERE singleton=1 AND state=1 AND bootstrap_open=true AND world_tick=0;
DO $bp03$
DECLARE v_household integer; v_p1 integer; v_p2 integer; v_count integer; v_member bigint;
BEGIN
 INSERT INTO sw_geo.bp02_parcel(source_id,operational_status,record)
 VALUES('BP03-HH-TEST:PARCEL','ACTIVE_IN_GAME','{"test_fixture":true}');
 INSERT INTO sw_geo.bp02_address(source_id,parcel_source_id,operational_status,record)
 VALUES('BP03-HH-TEST:ADDRESS','BP03-HH-TEST:PARCEL','ACTIVE_IN_GAME','{"test_fixture":true}');
 INSERT INTO sw_property.property_site(
  property_id,display_name,address_id,use_class,lifecycle_status,source_dataset,source_record
 ) VALUES('BP03-HH-TEST:PROPERTY','Fixture dwelling',NULL,'residential','active',
  'BP03-HH-TEST','{"source_candidate_parcel_id":"BP03-HH-TEST:PARCEL"}');
 INSERT INTO sw_property.street_address(
  address_id,property_id,display_name,source_dataset,source_record
 ) VALUES('BP03-HH-TEST:BP04-ADDRESS','BP03-HH-TEST:PROPERTY','Fixture dwelling address',
  'BP03-HH-TEST','{"test_fixture":true,"source_ref":"SW-GEO-V1:BP03-HH-TEST:PARCEL"}');
 UPDATE sw_property.property_site SET address_id='BP03-HH-TEST:BP04-ADDRESS'
 WHERE property_id='BP03-HH-TEST:PROPERTY';
 INSERT INTO sw_property.building(
  building_id,property_id,display_name,building_use,lifecycle_status,source_dataset,source_record
 ) VALUES('BP03-HH-TEST:BUILDING','BP03-HH-TEST:PROPERTY','Fixture residential building',
  'residential','active','BP03-HH-TEST','{"test_fixture":true}');
 INSERT INTO sw_property.premises(
  premises_id,property_id,building_id,display_name,premises_use,lifecycle_status,source_dataset,source_record
 ) VALUES('BP03-HH-TEST:PREMISES','BP03-HH-TEST:PROPERTY','BP03-HH-TEST:BUILDING',
  'Fixture dwelling premises','residential','active','BP03-HH-TEST','{"test_fixture":true}');
 INSERT INTO sw_property.unit_space(
  unit_id,property_id,building_id,premises_id,display_name,unit_class,use_class,lifecycle_status,source_dataset,source_record
 ) VALUES('BP03-HH-TEST:UNIT','BP03-HH-TEST:PROPERTY','BP03-HH-TEST:BUILDING',
  'BP03-HH-TEST:PREMISES','Fixture dwelling unit','dwelling','residential','active',
  'BP03-HH-TEST','{"test_fixture":true}');
 IF NOT sw_geo.link_bp04_bp02_address(
  'BP03-HH-TEST:BP04-ADDRESS','BP03-HH-TEST:ADDRESS',
  'BP03-HH-TEST:CROSSWALK','BP03-HH-TEST:EXACT-PARCEL-IDENTITY') THEN
  RAISE EXCEPTION 'exact parcel address crosswalk was not recorded';
 END IF;
 v_household:=sw_people.create_household(
  'BP03-HH-TEST:HOUSEHOLD','BP03-HH-TEST:UNIT','BP03-HH-TEST:BP04-ADDRESS',
  'BP03-HH-TEST:ADDRESS','BP03-HH-TEST:HOUSEHOLD-CREATE',
  'bp03-household-ci','two-person fixture household');
 v_p1:=sw_people.create_person('Maren','Dovell','BP03-HH-TEST:PERSON-1',
  'bp03-household-ci','household membership acceptance','Elyra');
 v_p2:=sw_people.create_person('Tavian','Merrow','BP03-HH-TEST:PERSON-2',
  'bp03-household-ci','household membership acceptance','Corin');
 PERFORM sw_people.set_person_residence(v_p1,'BP03-HH-TEST:ADDRESS','permanent',
  'BP03-HH-TEST:RESIDENCE-1','bp03-household-ci','household address');
 PERFORM sw_people.set_person_residence(v_p2,'BP03-HH-TEST:ADDRESS','permanent',
  'BP03-HH-TEST:RESIDENCE-2','bp03-household-ci','household address');
 v_member:=sw_people.add_household_member(v_household,v_p1,'household_contact',
  'BP03-HH-TEST:MEMBER-1','bp03-household-ci','fixture household contact');
 PERFORM sw_people.add_household_member(v_household,v_p2,'member',
  'BP03-HH-TEST:MEMBER-2','bp03-household-ci','fixture household member');
 IF (SELECT current_member_count FROM sw_people.household_summary WHERE household_id=v_household)<>2
  OR (SELECT contact_count FROM sw_people.household_summary WHERE household_id=v_household)<>1 THEN
  RAISE EXCEPTION 'household membership summary did not reconcile';
 END IF;
 SELECT living_included INTO v_count FROM sw_people.population_counter WHERE singleton=1;
 IF v_count<>2 THEN RAISE EXCEPTION 'two household members must contribute two distinct population identities'; END IF;
 PERFORM sw_people.end_household_membership(v_p2,'BP03-HH-TEST:MEMBER-END',
  'bp03-household-ci','fixture household departure');
 IF (SELECT current_member_count FROM sw_people.household_summary WHERE household_id=v_household)<>1
  OR (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>2 THEN
  RAISE EXCEPTION 'ending household membership must not silently remove resident population status';
 END IF;
 IF (SELECT count(*) FROM sw_people.household_history WHERE household_id=v_household)<>4 THEN
  RAISE EXCEPTION 'household history must contain creation, two joins and one departure';
 END IF;
 RAISE NOTICE 'BP03_HOUSEHOLD_MEMBERSHIP_PASS household_id=% members=2 population=2 history=4',v_household;
END
$bp03$;
ROLLBACK;

-- CI fixture is transactional and leaves no persistent household records.
