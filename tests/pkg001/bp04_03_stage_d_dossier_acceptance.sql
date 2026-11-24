-- BP04-03 Stage D parcel dossier schema acceptance. Synthetic rows roll back.
BEGIN;
DO $$
DECLARE
  v_hood integer;
  v_a integer;
  v_b integer;
  v_payload_a bytea := convert_to('{"type":"Polygon","coordinates":[[[0,0],[10,0],[10,10],[0,10],[0,0]]]}','UTF8');
  v_payload_b bytea := convert_to('{"type":"Polygon","coordinates":[[[10,0],[20,0],[20,10],[10,10],[10,0]]]}','UTF8');
  v_hash_a bytea;
  v_hash_b bytea;
  v_manifest bytea := decode(repeat('11',32),'hex');
  v_mutation_rejected boolean := false;
BEGIN
  SELECT spatial_id INTO v_hood FROM sw_geo.entity WHERE entity_code='SW-D01-N1' AND kind=4;
  IF v_hood IS NULL THEN RAISE EXCEPTION 'Disposable neighbourhood fixture missing'; END IF;
  v_hash_a := sw_ops.digest(v_payload_a,'sha256');
  v_hash_b := sw_ops.digest(v_payload_b,'sha256');

  INSERT INTO sw_geo.entity(entity_code,kind) VALUES('SWP-CAND-DOSSIER-TEST-A',6) RETURNING spatial_id INTO v_a;
  INSERT INTO sw_geo.entity(entity_code,kind) VALUES('SWP-CAND-DOSSIER-TEST-B',6) RETURNING spatial_id INTO v_b;
  INSERT INTO sw_geo.version(spatial_id,version_no,effective_from_tick,parent_id,name,active,geometry_format,geometry_payload,geometry_sha256,source_ref,reason_code)
  VALUES
    (v_a,1,0,v_hood,'Asterlune',true,1,v_payload_a,v_hash_a,'bp04-03-stage-d-test','1'),
    (v_b,1,0,v_hood,'Bravendon',true,1,v_payload_b,v_hash_b,'bp04-03-stage-d-test','1');
  INSERT INTO sw_geo.parcel_profile(parcel_spatial_id,version_no,neighbourhood_spatial_id,land_use_code,development_state,area_m2,area_basis,geometry_quality,source_ref,actor_ref,confidence_code,reason)
  VALUES
    (v_a,1,v_hood,'mixed_use','unknown',100,'derived_geometry','candidate_unreviewed','bp04-03-stage-d-test','test-runner','estimated','synthetic dossier fixture'),
    (v_b,1,v_hood,'mixed_use','unknown',100,'derived_geometry','candidate_unreviewed','bp04-03-stage-d-test','test-runner','estimated','synthetic dossier fixture');

  INSERT INTO sw_geo.parcel_dossier
    (parcel_spatial_id,version_no,geometry_sha256,source_manifest_sha256,perimeter_m,compactness_index,
     centroid_x_m,centroid_y_m,label_point_x_m,label_point_y_m,bounds_min_x_m,bounds_min_y_m,
     bounds_max_x_m,bounds_max_y_m,exterior_vertex_count,interior_ring_count,road_frontage_length_m,
     frontage_segment_count,frontage_candidate_count,water_boundary_contact_length_m,adjacent_water_feature_count,
     frontage_review_status,geometry_review_status,measurement_basis,source_ref,actor_ref,confidence_code,reason)
  VALUES
    (v_a,1,v_hash_a,v_manifest,40,0.78539816,5,5,5,5,0,0,10,10,4,0,10,1,1,0,0,
     'REVIEW_REQUIRED','VALID_GENERATED_CANDIDATE','DERIVED_FROM_GENERATED_POLYGON_GEOMETRY',
     'bp04-03-stage-d-test','test-runner','estimated','synthetic dossier fixture'),
    (v_b,1,v_hash_b,v_manifest,40,0.78539816,15,5,15,5,10,0,20,10,4,0,0,0,0,0,0,
     'NO_ROAD_EDGE_CONTACT_REVIEW_REQUIRED','VALID_GENERATED_CANDIDATE','DERIVED_FROM_GENERATED_POLYGON_GEOMETRY',
     'bp04-03-stage-d-test','test-runner','estimated','synthetic dossier fixture');

  INSERT INTO sw_geo.parcel_frontage_candidate
    (parcel_spatial_id,version_no,frontage_candidate_id,road_segment_ids,road_id,road_name,road_class,contact_length_m,
     candidate_point_x_m,candidate_point_y_m,review_status,source_manifest_sha256,source_ref,actor_ref,confidence_code,reason)
  VALUES
    (v_a,1,'PFC-TEST-A-01',ARRAY['SWS-TEST-01'],'SWR-TEST-01','Aster Road','local_street',10,1,5,0,
     'UNREVIEWED_GEOMETRIC_CONTACT',v_manifest,'bp04-03-stage-d-test','test-runner','estimated','synthetic frontage');

  INSERT INTO sw_geo.parcel_access_location_candidate
    (access_candidate_id,parcel_spatial_id,version_no,frontage_candidate_id,candidate_x_m,candidate_y_m,
     candidate_type,review_status,source_manifest_sha256,source_ref,actor_ref,confidence_code,reason)
  VALUES
    ('PAC-TEST-A-01',v_a,1,'PFC-TEST-A-01',5,0,'unclassified_access_location',
     'UNREVIEWED_GEOMETRIC_CANDIDATE',v_manifest,'bp04-03-stage-d-test','test-runner','estimated','synthetic access candidate');

  INSERT INTO sw_geo.parcel_adjacency_candidate
    (left_parcel_spatial_id,left_version_no,right_parcel_spatial_id,right_version_no,
     left_neighbourhood_spatial_id,right_neighbourhood_spatial_id,relationship_code,
     shared_boundary_length_m,source_manifest_sha256,source_ref,actor_ref,confidence_code,reason)
  VALUES
    (v_a,1,v_b,1,v_hood,v_hood,'SHARED_BOUNDARY_CANDIDATE',10,v_manifest,
     'bp04-03-stage-d-test','test-runner','estimated','synthetic shared boundary');

  INSERT INTO sw_geo.parcel_water_adjacency_candidate
    (parcel_spatial_id,version_no,water_feature_id,contact_length_m,source_manifest_sha256,source_ref,actor_ref,confidence_code,reason)
  VALUES
    (v_b,1,'SW-WTR-TEST-01',5,v_manifest,'bp04-03-stage-d-test','test-runner','estimated','synthetic water adjacency');

  BEGIN
    UPDATE sw_geo.parcel_dossier SET perimeter_m=41 WHERE parcel_spatial_id=v_a AND version_no=1;
  EXCEPTION WHEN raise_exception THEN v_mutation_rejected := true;
  END;
  IF NOT v_mutation_rejected THEN RAISE EXCEPTION 'Parcel dossier mutation was accepted'; END IF;

  IF (SELECT count(*) FROM sw_geo.parcel_frontage_candidate WHERE parcel_spatial_id=v_a) <> 1
     OR (SELECT count(*) FROM sw_geo.parcel_access_location_candidate WHERE parcel_spatial_id=v_a) <> 1
     OR (SELECT count(*) FROM sw_geo.parcel_adjacency_candidate WHERE left_parcel_spatial_id=v_a) <> 1
     OR (SELECT count(*) FROM sw_geo.parcel_water_adjacency_candidate WHERE parcel_spatial_id=v_b) <> 1 THEN
    RAISE EXCEPTION 'Parcel dossier child records failed acceptance';
  END IF;
END
$$;
ROLLBACK;
