\set ON_ERROR_STOP on
BEGIN;

DO $$
DECLARE
  n bigint;
BEGIN
  SELECT count(*) INTO n FROM sw_property.property_asset;
  IF n<>420 THEN RAISE EXCEPTION 'Expected 420 property identities, got %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.building;
  IF n<>1474 THEN RAISE EXCEPTION 'Expected 1474 building identities, got %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.premises;
  IF n<>27730 THEN RAISE EXCEPTION 'Expected 27730 premises identities, got %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.unit_space;
  IF n<>180733 THEN RAISE EXCEPTION 'Expected 180733 unit identities, got %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.access_point;
  IF n<>2948 THEN RAISE EXCEPTION 'Expected 2948 access-point candidate identities, got %',n; END IF;

  SELECT count(*) INTO n FROM sw_property.access_connector_candidate;
  IF n<>2948 THEN RAISE EXCEPTION 'Expected 768 persistent access connector candidates, got %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.access_connector_candidate
   WHERE connector_type='BUILDING_TO_ROAD_RESERVE_PROXIMITY_CANDIDATE'
     AND contact_type='POINT_CONTACT_ONLY'
     AND frontage_candidate_id IS NULL
     AND road_connection_candidate_id IS NOT NULL;
  IF n<>4 THEN RAISE EXCEPTION 'Expected four point-contact-only proximity connector candidates, got %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.access_connector_candidate
   WHERE geometry_status<>'UNREVIEWED_GEOMETRIC_LINE_ONLY'
      OR review_status<>'unreviewed_candidate'
      OR constructed_state<>'unknown' OR surface_code<>'unknown'
      OR slope_state<>'not_assessed' OR barrier_state<>'not_assessed'
      OR pedestrian_suitability<>'not_assessed' OR vehicle_suitability<>'not_assessed'
      OR accessibility_state<>'not_assessed' OR legal_access_state<>'not_assessed'
      OR public_access_state<>'not_assessed' OR emergency_egress_state<>'not_assessed';
  IF n<>0 THEN RAISE EXCEPTION 'Connector candidate attributes improperly promoted: %',n; END IF;

  SELECT count(*) INTO n FROM sw_property.property_candidate_site;
  IF n<>420 THEN RAISE EXCEPTION 'Property candidate-site lineage count mismatch: %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.asset_geometry_candidate;
  IF n<>4842 THEN RAISE EXCEPTION 'Asset geometry candidate count mismatch: %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.asset_generation_batch;
  IF n<>1 THEN RAISE EXCEPTION 'Expected one immutable generation batch, got %',n; END IF;
  SELECT unresolved_source_mapping_count INTO n FROM sw_property.asset_generation_batch;
  IF n<>0 THEN RAISE EXCEPTION 'Expected zero unresolved source mappings; stable entity_code mappings are complete, got %',n; END IF;

  SELECT count(*) INTO n FROM sw_property.property_profile;
  IF n<>420 THEN RAISE EXCEPTION 'Property profile coverage mismatch: %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.building_profile;
  IF n<>1474 THEN RAISE EXCEPTION 'Building profile coverage mismatch: %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.premises_profile;
  IF n<>27730 THEN RAISE EXCEPTION 'Premises profile coverage mismatch: %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.unit_profile;
  IF n<>180733 THEN RAISE EXCEPTION 'Unit profile coverage mismatch: %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.access_point_profile;
  IF n<>2948 THEN RAISE EXCEPTION 'Access-point profile coverage mismatch: %',n; END IF;

  SELECT count(*) INTO n FROM sw_property.physical_measurement;
  IF n=0 THEN RAISE EXCEPTION 'Physical measurements were not imported'; END IF;
  SELECT count(*) INTO n FROM sw_property.building_level;
  IF n=0 THEN RAISE EXCEPTION 'Building floor/level schedules were not imported'; END IF;
  SELECT count(*) INTO n FROM sw_property.building_component;
  IF n=0 THEN RAISE EXCEPTION 'Building components were not imported'; END IF;
  SELECT count(*) INTO n FROM sw_property.premises_room;
  IF n=0 THEN RAISE EXCEPTION 'Premises room schedules were not imported'; END IF;
  SELECT count(*) INTO n FROM sw_property.utility_system;
  IF n=0 THEN RAISE EXCEPTION 'Utility system inventory was not imported'; END IF;
  SELECT count(*) INTO n FROM sw_property.physical_feature;
  IF n=0 THEN RAISE EXCEPTION 'Physical feature inventory was not imported'; END IF;
  SELECT count(*) INTO n FROM sw_property.condition_assessment;
  IF n=0 THEN RAISE EXCEPTION 'Condition assessment records were not imported'; END IF;
  SELECT count(*) INTO n FROM sw_property.asset_assertion;
  IF n=0 THEN RAISE EXCEPTION 'Knowledge-state assertions were not imported'; END IF;
  SELECT count(*) INTO n FROM sw_property.physical_defect;
  IF n<>0 THEN RAISE EXCEPTION 'No defects were evidenced; generated defect rows are prohibited (found %)',n; END IF;

  SELECT count(*) INTO n FROM sw_property.property_asset
   WHERE location_status<>'unresolved' OR parcel_spatial_id IS NOT NULL OR address_spatial_id IS NOT NULL;
  IF n<>0 THEN RAISE EXCEPTION 'Candidate properties were incorrectly assigned operational geography'; END IF;
  SELECT count(*) INTO n FROM sw_property.access_point_profile
   WHERE emergency_egress_state<>'not_assessed' OR emergency_egress IS NOT NULL
      OR loading_capability_state<>'not_assessed' OR loading_capable IS NOT NULL;
  IF n<>0 THEN RAISE EXCEPTION 'Access-point unknown/not-assessed states were not preserved'; END IF;
  SELECT count(*) INTO n FROM sw_property.building_component
   WHERE material_code<>'unknown' OR condition_code<>'not_assessed';
  IF n<>0 THEN RAISE EXCEPTION 'Unobserved construction materials or conditions were fabricated'; END IF;
  SELECT count(*) INTO n FROM sw_property.condition_assessment
   WHERE condition_code<>'not_assessed';
  IF n<>0 THEN RAISE EXCEPTION 'Unperformed physical condition assessments were fabricated'; END IF;
  SELECT count(*) INTO n FROM sw_property.asset_assertion
   WHERE knowledge_state<>'not_assessed';
  IF n<>0 THEN RAISE EXCEPTION 'Generated knowledge-state assertions are inconsistent'; END IF;

  SELECT count(*) INTO n FROM sw_property.property_building;
  IF n<>1474 THEN RAISE EXCEPTION 'Property-building relationships mismatch: %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.building_premises;
  IF n<>27730 THEN RAISE EXCEPTION 'Building-premises relationships mismatch: %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.premises_unit;
  IF n<>180733 THEN RAISE EXCEPTION 'Premises-unit relationships mismatch: %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.asset_geometry_candidate g
   WHERE g.geometry_type='Polygon' AND g.geometry_payload->>'type'='Polygon';
  IF n<>1894 THEN RAISE EXCEPTION 'Expected 1894 property/building polygon geometries, got %',n; END IF;
  SELECT count(*) INTO n FROM sw_property.asset_geometry_candidate g
   WHERE g.geometry_type='Point' AND g.geometry_payload->>'type'='Point';
  IF n<>2948 THEN RAISE EXCEPTION 'Expected 2948 access-location points, got %',n; END IF;
END
$$;

-- Append-only protection must reject both mutation and deletion.
DO $$
DECLARE rejected boolean := false;
BEGIN
  BEGIN
    UPDATE sw_property.asset_geometry_candidate
       SET reason='mutation attempt'
     WHERE geometry_candidate_id=(SELECT min(geometry_candidate_id) FROM sw_property.asset_geometry_candidate);
  EXCEPTION WHEN OTHERS THEN rejected:=true;
  END;
  IF NOT rejected THEN RAISE EXCEPTION 'Asset geometry mutation was not rejected'; END IF;
  rejected:=false;
  BEGIN
    DELETE FROM sw_property.asset_generation_batch
     WHERE batch_id=(SELECT min(batch_id) FROM sw_property.asset_generation_batch);
  EXCEPTION WHEN OTHERS THEN rejected:=true;
  END;
  IF NOT rejected THEN RAISE EXCEPTION 'Asset generation batch deletion was not rejected'; END IF;
END
$$;

ROLLBACK;
