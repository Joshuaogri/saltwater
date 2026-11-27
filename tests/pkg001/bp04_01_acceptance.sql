-- BP04-01 disposable PostgreSQL 16 acceptance. All rows are synthetic and rolled back.
BEGIN;
-- Mirror the standard disposable BP03 acceptance harness: canonical person
-- creation is an in-game event and therefore requires a running, player-present
-- simulation. This transaction rolls the temporary runtime transition back.
UPDATE sw_runtime.state SET state=1,player_present=false
WHERE singleton=1 AND state=0 AND bootstrap_open=true AND world_tick=0;
UPDATE sw_runtime.state SET state=2,player_present=true,bootstrap_open=false
WHERE singleton=1 AND state=1 AND bootstrap_open=true AND world_tick=0;
DO $
DECLARE
  p_unresolved bigint;
  p_resolved bigint;
  b_one bigint;
  b_two bigint;
  prem_one bigint;
  prem_two bigint;
  prem_three bigint;
  unit_one bigint;
  ap_one bigint;
  ap_unnamed bigint;
  ap_unit bigint;
  parcel_id integer;
  address_id integer;
  wrong_kind integer;
  n_before integer;
  h_before integer;
  rh_before integer;
  existing_business_name text;
  existing_geography_name text;
  existing_person_name text;
  test_person_id integer;
  v_tick bigint;
BEGIN
  IF current_database()<>'saltwater_test' THEN
    RAISE EXCEPTION 'BP04-01 acceptance is restricted to saltwater_test';
  END IF;
  SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
  SELECT spatial_id INTO STRICT parcel_id FROM sw_geo.entity WHERE entity_code='bp04-test-parcel-0001' AND kind=6;
  SELECT spatial_id INTO STRICT address_id FROM sw_geo.entity WHERE entity_code='bp04-test-address-0001' AND kind=11;
  SELECT spatial_id INTO STRICT wrong_kind FROM sw_geo.entity WHERE entity_code='saltwater-state';

  INSERT INTO sw_property.property_asset
    (entity_code,display_name,location_status,created_tick,source_ref,actor_ref,reason)
  VALUES('SWP-BP04-UNRES-0001','BP04 Unresolved Property','unresolved',v_tick,
    'bp04-test:unresolved-property','test-runner','explicit unresolved-location test')
  RETURNING property_id INTO p_unresolved;

  INSERT INTO sw_property.property_asset
    (entity_code,display_name,location_status,parcel_spatial_id,address_spatial_id,
     created_tick,source_ref,actor_ref,reason)
  VALUES('SWP-BP04-RES-0001','BP04 Resolved Property','resolved',parcel_id,address_id,
    v_tick,'bp04-test:resolved-property','test-runner','typed parcel and address test')
  RETURNING property_id INTO p_resolved;

  IF (SELECT count(*) FROM sw_names.name_reservation WHERE entity_type='PROPERTY'
      AND entity_id IN (p_unresolved,p_resolved) AND name_form='canonical')<>2 THEN
    RAISE EXCEPTION 'property canonical names were not registered';
  END IF;
  IF (SELECT count(*) FROM sw_property.entity_history WHERE entity_type='PROPERTY'
      AND entity_id IN (p_unresolved,p_resolved) AND event_code='created')<>2 THEN
    RAISE EXCEPTION 'property creation history missing';
  END IF;

  BEGIN
    INSERT INTO sw_property.property_asset
      (entity_code,display_name,location_status,parcel_spatial_id,created_tick,source_ref,actor_ref,reason)
    VALUES('SWP-BP04-WRONG-0001','BP04 Wrong Parcel Kind','resolved',wrong_kind,v_tick,
      'bp04-test:wrong-parcel','test-runner','must reject geography kind mismatch');
    RAISE EXCEPTION 'wrong-kind parcel reference unexpectedly accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='wrong-kind parcel reference unexpectedly accepted' THEN RAISE; END IF;
  END;

  BEGIN
    INSERT INTO sw_property.property_asset
      (entity_code,display_name,location_status,address_spatial_id,created_tick,source_ref,actor_ref,reason)
    VALUES('SWP-BP04-WRONG-0002','BP04 Wrong Address Kind','resolved',wrong_kind,v_tick,
      'bp04-test:wrong-address','test-runner','must reject address kind mismatch');
    RAISE EXCEPTION 'wrong-kind address reference unexpectedly accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='wrong-kind address reference unexpectedly accepted' THEN RAISE; END IF;
  END;

  INSERT INTO sw_property.building(entity_code,display_name,created_tick,source_ref,actor_ref,reason)
  VALUES('SWB-STR-BP04-0001','BP04 Building One',v_tick,'bp04-test:building-one','test-runner','building test')
  RETURNING building_id INTO b_one;
  INSERT INTO sw_property.building(entity_code,display_name,created_tick,source_ref,actor_ref,reason)
  VALUES('SWB-STR-BP04-0002','BP04 Building Two',v_tick,'bp04-test:building-two','test-runner','multi-building test')
  RETURNING building_id INTO b_two;

  INSERT INTO sw_property.property_building
    (property_id,building_id,valid_from_tick,source_ref,actor_ref,reason)
  VALUES(p_resolved,b_one,v_tick,'bp04-test:property-building-1','test-runner','first building'),
        (p_resolved,b_two,v_tick,'bp04-test:property-building-2','test-runner','second building');

  INSERT INTO sw_property.premises(entity_code,display_name,building_id,created_tick,source_ref,actor_ref,reason)
  VALUES('SWPR-BP04-0001','BP04 Premises One',b_one,v_tick,'bp04-test:premises-one','test-runner','building premises')
  RETURNING premises_id INTO prem_one;
  INSERT INTO sw_property.premises(entity_code,display_name,property_id,created_tick,source_ref,actor_ref,reason)
  VALUES('SWPR-BP04-0002','BP04 Premises Two',p_unresolved,v_tick,'bp04-test:premises-two','test-runner','property premises')
  RETURNING premises_id INTO prem_two;
  INSERT INTO sw_property.premises(entity_code,display_name,building_id,created_tick,source_ref,actor_ref,reason)
  VALUES('SWPR-BP04-0003','BP04 Premises Three',b_one,v_tick,'bp04-test:premises-three','test-runner','second premises in same building')
  RETURNING premises_id INTO prem_three;

  INSERT INTO sw_property.building_premises
    (building_id,premises_id,valid_from_tick,source_ref,actor_ref,reason)
  VALUES(b_one,prem_one,v_tick,'bp04-test:building-premises','test-runner','valid building premises'),
        (b_one,prem_three,v_tick,'bp04-test:building-premises-2','test-runner','second premises in same building');

  INSERT INTO sw_property.unit_space(entity_code,display_name,premises_id,created_tick,source_ref,actor_ref,reason)
  VALUES('SWU-BP04-0001','BP04 Unit One',prem_one,v_tick,'bp04-test:unit-one','test-runner','unit test')
  RETURNING unit_id INTO unit_one;
  INSERT INTO sw_property.premises_unit
    (premises_id,unit_id,valid_from_tick,source_ref,actor_ref,reason)
  VALUES(prem_one,unit_one,v_tick,'bp04-test:premises-unit','test-runner','valid premises unit');

  INSERT INTO sw_property.access_point(entity_code,display_name,building_id,created_tick,source_ref,actor_ref,reason)
  VALUES('SWA-BP04-0001','BP04 Main Entrance',b_one,v_tick,'bp04-test:access-building','test-runner','building entrance')
  RETURNING access_point_id INTO ap_one;
  INSERT INTO sw_property.access_point(entity_code,premises_id,created_tick,source_ref,actor_ref,reason)
  VALUES('SWA-BP04-0002',prem_one,v_tick,'bp04-test:access-unnamed','test-runner','unnamed premises access')
  RETURNING access_point_id INTO ap_unnamed;
  INSERT INTO sw_property.access_point(entity_code,display_name,unit_id,created_tick,source_ref,actor_ref,reason)
  VALUES('SWA-BP04-0003','BP04 Unit Exit',unit_one,v_tick,'bp04-test:access-unit','test-runner','unit exit')
  RETURNING access_point_id INTO ap_unit;

  IF (SELECT count(*) FROM sw_names.name_reservation WHERE entity_type IN
      ('BUILDING','PREMISES','UNIT','ACCESS_POINT') AND name_form='canonical')<>8 THEN
    RAISE EXCEPTION 'named physical identities did not all join SW-UNS';
  END IF;
  IF EXISTS (SELECT 1 FROM sw_names.name_reservation WHERE entity_type='ACCESS_POINT' AND entity_id=ap_unnamed) THEN
    RAISE EXCEPTION 'unnamed access point incorrectly received a placeholder name';
  END IF;
  IF (SELECT count(*) FROM sw_property.property_building WHERE property_id=p_resolved AND valid_to_tick IS NULL)<>2 THEN
    RAISE EXCEPTION 'one property must support multiple buildings';
  END IF;
  IF (SELECT count(*) FROM sw_property.building_premises WHERE building_id=b_one AND valid_to_tick IS NULL)<>2 THEN
    RAISE EXCEPTION 'one building must support multiple premises';
  END IF;

  -- A business name is globally unavailable to a property identity.
  -- The BP04-01 migration acceptance runs before the opening business fixture.
  -- Use an existing canonical global reservation so this migration test remains
  -- independent of later world seeding; the separate business collision case
  -- is exercised when the opening business registry is provisioned.
  SELECT r.display_name INTO STRICT existing_business_name
  FROM sw_names.name_reservation r
  WHERE r.name_form='canonical' AND r.entity_type IN ('GEOGRAPHY','PERSON','BUSINESS')
  ORDER BY CASE r.entity_type WHEN 'BUSINESS' THEN 0 ELSE 1 END
  LIMIT 1;
  BEGIN
    INSERT INTO sw_property.property_asset
      (entity_code,display_name,location_status,created_tick,source_ref,actor_ref,reason)
    VALUES('SWP-BP04-COLLIDE-0001',existing_business_name,'unresolved',v_tick,
      'bp04-test:business-name-collision','test-runner','cross-domain naming collision');
    RAISE EXCEPTION 'business/property global name collision unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='business/property global name collision unexpectedly succeeded' THEN RAISE; END IF;
  END;

  -- Immutable identity and append-only history.
  BEGIN
    UPDATE sw_property.property_asset SET display_name='BP04 Changed Identity' WHERE property_id=p_resolved;
    RAISE EXCEPTION 'property identity mutation unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='property identity mutation unexpectedly succeeded' THEN RAISE; END IF;
  END;
  BEGIN
    DELETE FROM sw_property.building WHERE building_id=b_two;
    RAISE EXCEPTION 'building deletion unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='building deletion unexpectedly succeeded' THEN RAISE; END IF;
  END;
  PERFORM sw_property.change_lifecycle('PROPERTY',p_unresolved,'inactive',v_tick+1,
    'bp04-test:lifecycle-change','test-runner','test attributed lifecycle transition');
  IF (SELECT count(*) FROM sw_property.entity_history WHERE entity_type='PROPERTY'
      AND entity_id=p_unresolved AND event_code='status_changed' AND new_status='inactive'
      AND effective_tick=v_tick+1 AND source_ref='bp04-test:lifecycle-change'
      AND actor_ref='test-runner' AND reason='test attributed lifecycle transition')<>1 THEN
    RAISE EXCEPTION 'lifecycle status history was not appended';
  END IF;

  -- Effective-dated association close appends, never rewrites, relationship history.
  UPDATE sw_property.property_building SET valid_to_tick=v_tick+1
    WHERE property_id=p_resolved AND building_id=b_two AND valid_to_tick IS NULL;
  IF NOT EXISTS (SELECT 1 FROM sw_property.relationship_history
    WHERE relationship_type='property_building' AND from_id=p_resolved AND to_id=b_two
      AND event_code='unlinked' AND effective_tick=v_tick+1) THEN
    RAISE EXCEPTION 'relationship end was not recorded';
  END IF;

  BEGIN
    INSERT INTO sw_property.building_premises
      (building_id,premises_id,valid_from_tick,source_ref,actor_ref,reason)
    VALUES(b_two,prem_one,v_tick,'bp04-test:wrong-parent','test-runner','must reject mismatched parent');
    RAISE EXCEPTION 'invalid building-premises parent link unexpectedly accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='invalid building-premises parent link unexpectedly accepted' THEN RAISE; END IF;
  END;

  -- Global namespace rejects existing geography and person names as well as business names.
  SELECT display_name INTO STRICT existing_geography_name
  FROM sw_names.name_reservation
  WHERE entity_type='GEOGRAPHY' AND name_form='canonical'
  ORDER BY reservation_id
  LIMIT 1;
  BEGIN
    INSERT INTO sw_property.property_asset
      (entity_code,display_name,location_status,created_tick,source_ref,actor_ref,reason)
    VALUES('SWP-BP04-GEO-COLLIDE-0001',existing_geography_name,'unresolved',v_tick,
      'bp04-test:geography-name-collision','test-runner','cross-domain geography collision');
    RAISE EXCEPTION 'geography/property global name collision unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='geography/property global name collision unexpectedly succeeded' THEN RAISE; END IF;
  END;
  -- The opening population is seeded later. Create a temporary person through
  -- the canonical BP03 service so this collision check is independent of seed order.
  test_person_id := sw_people.create_person(
    'BP04Test', 'Collision', 'bp04-test:person-name-collision',
    'test-runner', 'temporary person for global naming collision acceptance'
  );
  SELECT concat_ws(' ',given_name,middle_name,family_name) INTO STRICT existing_person_name
  FROM sw_people.person WHERE person_id=test_person_id;
  BEGIN
    INSERT INTO sw_property.property_asset
      (entity_code,display_name,location_status,created_tick,source_ref,actor_ref,reason)
    VALUES('SWP-BP04-PERSON-COLLIDE-0001',existing_person_name,'unresolved',v_tick,
      'bp04-test:person-name-collision','test-runner','cross-domain person collision');
    RAISE EXCEPTION 'person/property global name collision unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='person/property global name collision unexpectedly succeeded' THEN RAISE; END IF;
  END;
  BEGIN
    INSERT INTO sw_property.building(entity_code,display_name,created_tick,source_ref,actor_ref,reason)
    VALUES('SWB-STR-BP04-0003','BP04 Building One',v_tick,'bp04-test:bp04-name-collision',
      'test-runner','cross-BP04 entity name collision');
    RAISE EXCEPTION 'cross-BP04 global name collision unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='cross-BP04 global name collision unexpectedly succeeded' THEN RAISE; END IF;
  END;

  -- Orphan endpoints are rejected by the physical foreign-key model.
  BEGIN
    INSERT INTO sw_property.premises(entity_code,display_name,building_id,created_tick,source_ref,actor_ref,reason)
    VALUES('SWPR-BP04-ORPHAN-0001','BP04 Orphan Premises',9223372036854770000,v_tick,
      'bp04-test:orphan','test-runner','orphan parent rejection');
    RAISE EXCEPTION 'orphan premises parent unexpectedly accepted';
  EXCEPTION WHEN foreign_key_violation THEN NULL;
  END;

  -- A duplicate-name failure must roll back the newly-created physical identity.
  SELECT count(*) INTO n_before FROM sw_property.property_asset;
  BEGIN
    INSERT INTO sw_property.property_asset
      (entity_code,display_name,location_status,created_tick,source_ref,actor_ref,reason)
    VALUES('SWP-BP04-ROLLBACK-0001',existing_business_name,'unresolved',v_tick,
      'bp04-test:rollback','test-runner','atomic rollback check');
    RAISE EXCEPTION 'duplicate-name insert unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='duplicate-name insert unexpectedly succeeded' THEN RAISE; END IF;
  END;
  IF (SELECT count(*) FROM sw_property.property_asset)<>n_before THEN
    RAISE EXCEPTION 'failed name reservation left a partial property identity';
  END IF;

  IF (SELECT count(*) FROM sw_property.entity_history WHERE entity_type='BUILDING'
      AND entity_id IN (b_one,b_two) AND event_code='created')<>2
     OR (SELECT count(*) FROM sw_property.entity_history WHERE entity_type='PREMISES'
      AND entity_id IN (prem_one,prem_two,prem_three) AND event_code='created')<>3
     OR (SELECT count(*) FROM sw_property.entity_history WHERE entity_type='UNIT'
      AND entity_id=unit_one AND event_code='created')<>1
     OR (SELECT count(*) FROM sw_property.entity_history WHERE entity_type='ACCESS_POINT'
      AND entity_id IN (ap_one,ap_unnamed,ap_unit) AND event_code='created')<>3 THEN
    RAISE EXCEPTION 'physical identity creation history incomplete';
  END IF;

  RAISE NOTICE 'BP04_01_ACCEPTANCE_PASS properties=2 buildings=2 premises=3 units=1 access_points=3';
END
$$;
ROLLBACK;
