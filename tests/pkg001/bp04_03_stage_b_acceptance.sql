-- BP04-03 Stage B schema acceptance. Synthetic rows are rolled back.
BEGIN;
DO $$
DECLARE
 v_neighbourhood integer;
 v_road integer;
 v_parcel integer;
 v_address integer;
 v_other_address integer;
 v_successor_parcel integer;
 v_append_only_rejected boolean := false;
 v_payload bytea := convert_to('{"type":"Polygon","coordinates":[[[0,0],[10,0],[10,10],[0,10],[0,0]]]}','UTF8');
 v_hash bytea;
 v_duplicate_rejected boolean := false;
 v_bad_road_rejected boolean := false;
BEGIN
 SELECT spatial_id INTO v_neighbourhood FROM sw_geo.entity WHERE entity_code='SW-D01-N1' AND kind=4;
 SELECT spatial_id INTO v_road FROM sw_geo.entity WHERE entity_code='SWR-V01' AND kind=7;
 IF v_neighbourhood IS NULL OR v_road IS NULL THEN
   RAISE EXCEPTION 'SW-GEO-V1 disposable identity fixture must be loaded first';
 END IF;
 v_hash := sw_ops.digest(v_payload,'sha256');

 INSERT INTO sw_geo.entity(entity_code,kind) VALUES('SWP-CAND-BP04-03-0001',6) RETURNING spatial_id INTO v_parcel;
 INSERT INTO sw_geo.version(spatial_id,version_no,effective_from_tick,parent_id,name,active,geometry_format,geometry_payload,geometry_sha256,source_ref,reason_code)
 VALUES(v_parcel,1,0,v_neighbourhood,'Candidate parcel 0001',true,1,v_payload,v_hash,'bp04-03-stage-b-test',1);
 INSERT INTO sw_geo.parcel_profile(parcel_spatial_id,version_no,neighbourhood_spatial_id,land_use_code,development_state,area_m2,area_basis,geometry_quality,source_ref,actor_ref,confidence_code,reason)
 VALUES(v_parcel,1,v_neighbourhood,'mixed_use','developed',100,'derived_geometry','candidate_unreviewed','bp04-03-stage-b-test','test-runner','estimated','synthetic disposable acceptance');

 INSERT INTO sw_geo.entity(entity_code,kind) VALUES('SWA-CAND-BP04-03-0001',11) RETURNING spatial_id INTO v_address;
 INSERT INTO sw_geo.version(spatial_id,version_no,effective_from_tick,parent_id,name,active,source_ref,reason_code)
 VALUES(v_address,1,0,v_parcel,'Address locator candidate',true,'bp04-03-stage-b-test',1);
 INSERT INTO sw_geo.address_profile(address_spatial_id,version_no,parcel_spatial_id,neighbourhood_spatial_id,road_spatial_id,locator_kind,locator_value,frontage_type,source_ref,actor_ref,confidence_code,reason)
 VALUES(v_address,1,v_parcel,v_neighbourhood,v_road,'street_number','101','direct_public_frontage','bp04-03-stage-b-test','test-runner','estimated','synthetic disposable acceptance');

 INSERT INTO sw_geo.entity(entity_code,kind) VALUES('SWA-CAND-BP04-03-0002',11) RETURNING spatial_id INTO v_other_address;
 INSERT INTO sw_geo.version(spatial_id,version_no,effective_from_tick,parent_id,name,active,source_ref,reason_code)
 VALUES(v_other_address,1,0,v_parcel,'Duplicate address locator candidate',true,'bp04-03-stage-b-test',1);
 BEGIN
   INSERT INTO sw_geo.address_profile(address_spatial_id,version_no,parcel_spatial_id,neighbourhood_spatial_id,road_spatial_id,locator_kind,locator_value,frontage_type,source_ref,actor_ref,confidence_code,reason)
   VALUES(v_other_address,1,v_parcel,v_neighbourhood,v_road,'street_number','101','direct_public_frontage','bp04-03-stage-b-test','test-runner','estimated','duplicate must fail');
 EXCEPTION WHEN unique_violation THEN v_duplicate_rejected := true;
 END;
 IF NOT v_duplicate_rejected THEN RAISE EXCEPTION 'duplicate active road locator was accepted'; END IF;

 BEGIN
   INSERT INTO sw_geo.address_profile(address_spatial_id,version_no,parcel_spatial_id,neighbourhood_spatial_id,road_spatial_id,locator_kind,locator_value,frontage_type,source_ref,actor_ref,confidence_code,reason)
   VALUES(v_other_address,1,v_parcel,v_neighbourhood,v_parcel,'street_number','102','direct_public_frontage','bp04-03-stage-b-test','test-runner','estimated','wrong-kind road must fail');
 EXCEPTION WHEN raise_exception THEN v_bad_road_rejected := true;
 END;
 IF NOT v_bad_road_rejected THEN RAISE EXCEPTION 'non-road spatial reference was accepted'; END IF;

 INSERT INTO sw_geo.entity(entity_code,kind) VALUES('SWP-CAND-BP04-03-0002',6) RETURNING spatial_id INTO v_successor_parcel;
 INSERT INTO sw_geo.version(spatial_id,version_no,effective_from_tick,parent_id,name,active,geometry_format,geometry_payload,geometry_sha256,source_ref,reason_code)
 VALUES(v_successor_parcel,1,0,v_neighbourhood,'Candidate parcel 0002',true,1,v_payload,v_hash,'bp04-03-stage-b-test',1);
 INSERT INTO sw_geo.parcel_profile(parcel_spatial_id,version_no,neighbourhood_spatial_id,land_use_code,development_state,area_m2,area_basis,geometry_quality,source_ref,actor_ref,confidence_code,reason)
 VALUES(v_successor_parcel,1,v_neighbourhood,'mixed_use','developed',100,'derived_geometry','candidate_unreviewed','bp04-03-stage-b-test','test-runner','estimated','synthetic disposable acceptance');
 INSERT INTO sw_geo.parcel_lineage(predecessor_parcel_spatial_id,successor_parcel_spatial_id,relationship_code,effective_from_tick,source_ref,actor_ref,reason)
 VALUES(v_parcel,v_successor_parcel,'split_into',0,'bp04-03-stage-b-test','test-runner','synthetic lineage row');
 BEGIN
   UPDATE sw_geo.parcel_profile SET area_m2=101 WHERE parcel_spatial_id=v_parcel AND version_no=1;
 EXCEPTION WHEN raise_exception THEN v_append_only_rejected := true;
 END;
 IF NOT v_append_only_rejected THEN RAISE EXCEPTION 'parcel profile mutation was accepted'; END IF;
END
$$;
ROLLBACK;
