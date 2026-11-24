-- BP04-02 deep profile acceptance. All synthetic records are rolled back.
BEGIN;
DO $$
DECLARE
 p bigint; b bigint; pr bigint; u bigint; a bigint; lvl bigint;
 n integer;
BEGIN
 INSERT INTO sw_property.property_asset(entity_code,display_name,location_status,created_tick,source_ref,actor_ref,reason)
 VALUES('SWP-BP04-02-TEST-0001','BP04 Profile Test Property','unresolved',0,'bp04-02-test:property','test-runner','synthetic acceptance only') RETURNING property_id INTO p;
 INSERT INTO sw_property.building(entity_code,display_name,created_tick,source_ref,actor_ref,reason)
 VALUES('SWB-STR-BP04-02-0001','BP04 Profile Test Building',0,'bp04-02-test:building','test-runner','synthetic acceptance only') RETURNING building_id INTO b;
 INSERT INTO sw_property.premises(entity_code,display_name,building_id,created_tick,source_ref,actor_ref,reason)
 VALUES('SWPR-BP04-02-TEST-0001','BP04 Profile Test Premises',b,0,'bp04-02-test:premises','test-runner','synthetic acceptance only') RETURNING premises_id INTO pr;
 INSERT INTO sw_property.unit_space(entity_code,display_name,premises_id,created_tick,source_ref,actor_ref,reason)
 VALUES('SWU-BP04-02-TEST-0001','BP04 Profile Test Unit',pr,0,'bp04-02-test:unit','test-runner','synthetic acceptance only') RETURNING unit_id INTO u;
 INSERT INTO sw_property.access_point(entity_code,display_name,building_id,created_tick,source_ref,actor_ref,reason)
 VALUES('SWA-BP04-02-TEST-0001','BP04 Profile Test Access',b,0,'bp04-02-test:access','test-runner','synthetic acceptance only') RETURNING access_point_id INTO a;

 INSERT INTO sw_property.property_profile
 (property_id,property_class,primary_use,secondary_uses,development_form,site_state,boundary_status,terrain_code,drainage_state,perimeter_type,utility_availability,source_ref,actor_ref,confidence_code,effective_from_tick,recorded_at,reason) VALUES
 (p,'mixed_use','residential and retail',ARRAY['retail','residential'],'compound','developed','verified','level','adequate','fence','partial','bp04-02-test:profile','test-runner','documented',0,transaction_timestamp(),'typed profile acceptance');
 INSERT INTO sw_property.building_profile
 (building_id,building_use,building_form,structure_class,construction_system,foundation_type,roof_form,roof_covering,facade_system,storeys_above,storeys_below,height_m,height_datum,structural_capacity_persons,authorised_capacity_persons,construction_year,completion_year,heritage_status,source_ref,actor_ref,confidence_code,effective_from_tick,reason)
 VALUES(b,'mixed-use','tower','high_rise','reinforced_concrete','piles','flat','membrane','curtain_wall',8,1,31.500,'ground datum',300,250,2012,2014,'not_designated','bp04-02-test:profile','test-runner','documented',0,'typed profile acceptance');
 INSERT INTO sw_property.premises_profile
 (premises_id,premises_type,primary_function,floor_level,orientation,fitout_standard,occupancy_suitability,security_boundary,accessibility_state,source_ref,actor_ref,confidence_code,effective_from_tick,recorded_at,reason) VALUES
 (pr,'shop','retail unit','Ground','east','enhanced','suitable','controlled','accessible','bp04-02-test:profile','test-runner','observed',0,transaction_timestamp(),'typed profile acceptance');
 INSERT INTO sw_property.unit_profile
 (unit_id,unit_class,local_locator,floor_level,room_count,physical_capacity,suitability_state,fitout_state,accessibility_state,source_ref,actor_ref,confidence_code,effective_from_tick,recorded_at,reason) VALUES
 (u,'shop','G-01','Ground',2,12,'suitable','standard','accessible','bp04-02-test:profile','test-runner','observed',0,transaction_timestamp(),'typed profile acceptance');
 INSERT INTO sw_property.access_point_profile
 (access_point_id,access_type,access_modes,directionality,control_type,availability_state,accessibility_state,emergency_egress,loading_capable,source_ref,actor_ref,confidence_code,effective_from_tick,recorded_at,reason) VALUES
 (a,'pedestrian_entrance',ARRAY['pedestrian','cycle'],'bidirectional','card','available','accessible',false,false,'bp04-02-test:profile','test-runner','verified',0,transaction_timestamp(),'typed profile acceptance');

 INSERT INTO sw_property.physical_measurement(entity_type,entity_id,measure_code,numeric_value,unit_code,measurement_basis,precision_code,method_code,effective_from_tick,source_ref,actor_ref,confidence_code,reason)
 VALUES ('PROPERTY',p,'site_area',1200,'m2','gross','rounded','survey',0,'bp04-02-test:measurement','test-runner','verified','measured site area'),
 ('BUILDING',b,'gross_floor_area',4200,'m2','gross','approximate','plan',0,'bp04-02-test:measurement','test-runner','documented','gross floor area'),
 ('PREMISES',pr,'usable_area',180,'m2','usable','rounded','survey',0,'bp04-02-test:measurement','test-runner','verified','usable area'),
 ('UNIT',u,'opening_width',1.2,'m','clear_opening','exact','instrument',0,'bp04-02-test:measurement','test-runner','observed','unit door clear width'),
 ('ACCESS_POINT',a,'opening_height',2.1,'m','clear_opening','exact','instrument',0,'bp04-02-test:measurement','test-runner','observed','access clear height');
 INSERT INTO sw_property.building_level(building_id,level_code,level_name,level_order,level_type,source_ref,actor_ref,effective_from_tick,reason)
 VALUES(b,'L00','Ground',0,'ground','bp04-02-test:level','test-runner',0,'floor schedule') RETURNING level_id INTO lvl;
 INSERT INTO sw_property.building_component(building_id,level_id,component_type,material_code,condition_code,source_ref,actor_ref,effective_from_tick,reason)
 VALUES(b,lvl,'frame','reinforced_concrete','good','bp04-02-test:component','test-runner',0,'component survey');
 INSERT INTO sw_property.premises_room(premises_id,room_code,room_type,floor_level,area_m2,accessibility_state,source_ref,actor_ref,effective_from_tick,reason)
 VALUES(pr,'R-01','sales floor','Ground',120,'accessible','bp04-02-test:room','test-runner',0,'room survey');
 INSERT INTO sw_property.utility_system(entity_type,entity_id,utility_type,availability_state,capacity_value,capacity_unit,source_ref,actor_ref,effective_from_tick,confidence_code,reason)
 VALUES('BUILDING',b,'electricity','connected',250,'kVA','bp04-02-test:utility','test-runner',0,'documented','utility schedule');
 INSERT INTO sw_property.physical_feature(entity_type,entity_id,feature_type,feature_label,feature_state,source_ref,actor_ref,effective_from_tick,confidence_code,reason)
 VALUES('PROPERTY',p,'parking','Rear parking court','present','bp04-02-test:feature','test-runner',0,'observed','site inspection');
 INSERT INTO sw_property.condition_assessment(entity_type,entity_id,element_code,condition_code,assessed_tick,assessor_ref,source_ref,confidence_code,findings,recommended_action)
 VALUES('BUILDING',b,'roof','fair',0,'assessor-01','bp04-02-test:condition','observed','Localised membrane wear','Schedule roof repair');
 INSERT INTO sw_property.physical_defect(entity_type,entity_id,defect_code,severity,defect_state,discovered_tick,source_ref,actor_ref,confidence_code,description,action_required)
 VALUES('ACCESS_POINT',a,'GATE-HINGE-WEAR','moderate','open',0,'bp04-02-test:defect','test-runner','observed','Hinge wear at access gate','Inspect and repair');
 INSERT INTO sw_property.asset_assertion(entity_type,entity_id,attribute_code,value_text,knowledge_state,effective_from_tick,source_ref,actor_ref,confidence_code,reason)
 VALUES('UNIT',u,'meter_serial',NULL,'not_assessed',0,'bp04-02-test:assertion','test-runner','unknown','meter not yet inspected'),
 ('UNIT',u,'ceiling_finish','plaster','known',0,'bp04-02-test:assertion','test-runner','observed','visible finish recorded');

 IF (SELECT count(*) FROM sw_property.physical_measurement WHERE entity_id IN (p,b,pr,u,a))<>5 THEN RAISE EXCEPTION 'measurement detail missing'; END IF;
 IF (SELECT count(*) FROM sw_property.building_component WHERE building_id=b)<>1
 OR (SELECT count(*) FROM sw_property.premises_room WHERE premises_id=pr)<>1
 OR (SELECT count(*) FROM sw_property.condition_assessment WHERE entity_id=b)<>1
 OR (SELECT count(*) FROM sw_property.physical_defect WHERE entity_id=a)<>1 THEN
 RAISE EXCEPTION 'structured component, room, condition or defect detail missing'; END IF;

 BEGIN
  UPDATE sw_property.unit_profile SET room_count=3 WHERE unit_id=u;
  RAISE EXCEPTION 'append-only profile update unexpectedly succeeded';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM='append-only profile update unexpectedly succeeded' THEN RAISE; END IF;
 END;
 BEGIN
  INSERT INTO sw_property.physical_measurement(entity_type,entity_id,measure_code,numeric_value,unit_code,measurement_basis,precision_code,method_code,effective_from_tick,source_ref,actor_ref,confidence_code,reason)
  VALUES('PROPERTY',9223372036854770000,'site_area',0,'m2','gross','exact','survey',0,'bp04-02-test:bad-ref','test-runner','verified','must reject orphan');
  RAISE EXCEPTION 'orphan profile detail unexpectedly succeeded';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM='orphan profile detail unexpectedly succeeded' THEN RAISE; END IF;
 END;
 BEGIN
  INSERT INTO sw_property.asset_assertion(entity_type,entity_id,attribute_code,value_text,knowledge_state,effective_from_tick,source_ref,actor_ref,confidence_code,reason)
  VALUES('UNIT',u,'unknown_meter','', 'not_assessed',0,'bp04-02-test:bad-state','test-runner','unknown','must reject unknown with value');
  RAISE EXCEPTION 'knowledge-state contradiction unexpectedly succeeded';
 EXCEPTION WHEN check_violation THEN NULL;
 END;
 RAISE NOTICE 'BP04_02_ACCEPTANCE_PASS property=1 building=1 premises=1 unit=1 access_point=1 measurements=5 levels=1 components=1 rooms=1 utility=1 feature=1 condition=1 defect=1 assertions=2';
END $$;
ROLLBACK;
