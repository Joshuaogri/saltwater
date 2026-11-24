-- BP04-02: detailed, typed physical asset and space profiles.
-- Disposable PostgreSQL 16 acceptance only. Never apply to Neon under this approval.
BEGIN;

CREATE TABLE sw_property.property_profile (
  property_id bigint PRIMARY KEY REFERENCES sw_property.property_asset(property_id),
  property_class text NOT NULL CHECK (property_class IN ('residential','mixed_use','commercial','industrial','civic','institutional','transport','utility','open_space','special_purpose','unknown')),
  primary_use text NOT NULL CHECK (length(btrim(primary_use)) BETWEEN 1 AND 80),
  secondary_uses text[] NOT NULL DEFAULT '{}',
  development_form text NOT NULL CHECK (development_form IN ('standalone','attached','compound','campus','block','estate','other','unknown')),
  site_state text NOT NULL CHECK (site_state IN ('developed','part_developed','vacant','cleared','construction','derelict','protected','unknown')),
  boundary_status text NOT NULL CHECK (boundary_status IN ('verified','approximate','unverified','not_assessed','not_applicable')),
  terrain_code text NOT NULL CHECK (terrain_code IN ('level','sloping','steep','varied','unknown','not_assessed')),
  drainage_state text NOT NULL CHECK (drainage_state IN ('adequate','limited','poor','flood_exposed','unknown','not_assessed')),
  perimeter_type text NOT NULL CHECK (perimeter_type IN ('none','open','fence','wall','mixed','natural','unknown','not_assessed')),
  utility_availability text NOT NULL CHECK (utility_availability IN ('full','partial','none','unknown','not_assessed')),
  source_ref text NOT NULL, actor_ref text NOT NULL, confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0), recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240)
);
CREATE TABLE sw_property.building_profile (
  building_id bigint PRIMARY KEY REFERENCES sw_property.building(building_id),
  building_use text NOT NULL, building_form text NOT NULL CHECK (building_form IN ('detached','semi_detached','terraced','tower','slab','courtyard','shed','pavilion','underground','other','unknown')),
  structure_class text NOT NULL CHECK (structure_class IN ('low_rise','mid_rise','high_rise','industrial_span','lightweight','civil_engineering','other','unknown')),
  construction_system text NOT NULL CHECK (construction_system IN ('reinforced_concrete','steel_frame','masonry','timber','composite','modular','earth','other','unknown')),
  foundation_type text NOT NULL CHECK (foundation_type IN ('shallow','raft','piles','strip','pad','mixed','unknown','not_assessed')),
  roof_form text NOT NULL, roof_covering text NOT NULL, facade_system text NOT NULL,
  storeys_above integer CHECK (storeys_above>=0), storeys_below integer CHECK (storeys_below>=0),
  height_m numeric(10,3) CHECK (height_m>=0), height_datum text,
  structural_capacity_persons integer CHECK (structural_capacity_persons>=0),
  authorised_capacity_persons integer CHECK (authorised_capacity_persons>=0),
  construction_year smallint CHECK (construction_year BETWEEN 1 AND 9999),
  completion_year smallint CHECK (completion_year BETWEEN 1 AND 9999),
  heritage_status text NOT NULL CHECK (heritage_status IN ('designated','candidate','not_designated','unknown','not_assessed')),
  source_ref text NOT NULL, actor_ref text NOT NULL, confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0), recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240)
);
CREATE TABLE sw_property.premises_profile (
  premises_id bigint PRIMARY KEY REFERENCES sw_property.premises(premises_id),
  premises_type text NOT NULL CHECK (premises_type IN ('shop','office','suite','department','warehouse','industrial_bay','civic_room','plant_space','residential_common','other','unknown')),
  primary_function text NOT NULL, floor_level text, orientation text,
  fitout_standard text NOT NULL CHECK (fitout_standard IN ('basic','standard','enhanced','specialist','shell','unknown','not_assessed')),
  occupancy_suitability text NOT NULL CHECK (occupancy_suitability IN ('suitable','restricted','unsuitable','unknown','not_assessed')),
  security_boundary text NOT NULL CHECK (security_boundary IN ('open','controlled','restricted','secure','unknown','not_assessed')),
  accessibility_state text NOT NULL CHECK (accessibility_state IN ('accessible','partially_accessible','not_accessible','unknown','not_assessed')),
  source_ref text NOT NULL, actor_ref text NOT NULL, confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0), recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240)
);
CREATE TABLE sw_property.unit_profile (
  unit_id bigint PRIMARY KEY REFERENCES sw_property.unit_space(unit_id),
  unit_class text NOT NULL CHECK (unit_class IN ('dwelling','apartment','office','shop','kiosk','stall','room','storage','workshop','parking_bay','berth','plant_space','other','unknown')),
  local_locator text, floor_level text,
  room_count smallint CHECK (room_count>=0),
  physical_capacity integer CHECK (physical_capacity>=0),
  suitability_state text NOT NULL CHECK (suitability_state IN ('suitable','restricted','unsuitable','unknown','not_assessed')),
  fitout_state text NOT NULL CHECK (fitout_state IN ('shell','basic','standard','enhanced','specialist','unknown','not_assessed')),
  accessibility_state text NOT NULL CHECK (accessibility_state IN ('accessible','partially_accessible','not_accessible','unknown','not_assessed')),
  source_ref text NOT NULL, actor_ref text NOT NULL, confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0), recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240)
);
CREATE TABLE sw_property.access_point_profile (
  access_point_id bigint PRIMARY KEY REFERENCES sw_property.access_point(access_point_id),
  access_type text NOT NULL CHECK (access_type IN ('pedestrian_entrance','pedestrian_exit','vehicle_entrance','vehicle_exit','combined_gate','loading_bay','service_entrance','emergency_exit','controlled_passage','lobby_threshold','roof_access','plant_access','other','unknown')),
  access_modes text[] NOT NULL DEFAULT '{}',
  directionality text NOT NULL CHECK (directionality IN ('inbound','outbound','bidirectional','emergency_only','restricted','unknown')),
  control_type text NOT NULL CHECK (control_type IN ('open','gate','lock','staffed','intercom','card','key','turnstile','barrier','mixed','unknown')),
  availability_state text NOT NULL CHECK (availability_state IN ('available','restricted','unavailable','emergency_only','unknown','not_assessed')),
  accessibility_state text NOT NULL CHECK (accessibility_state IN ('accessible','partially_accessible','not_accessible','unknown','not_assessed')),
  emergency_egress boolean NOT NULL,
  loading_capable boolean NOT NULL,
  source_ref text NOT NULL, actor_ref text NOT NULL, confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0), recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240)
);

-- Typed, provenance-bearing measurements. A missing measurement is not zero.
CREATE TABLE sw_property.physical_measurement (
  measurement_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_type text NOT NULL CHECK (entity_type IN ('PROPERTY','BUILDING','PREMISES','UNIT','ACCESS_POINT')),
  entity_id bigint NOT NULL CHECK (entity_id>0),
  measure_code text NOT NULL CHECK (measure_code IN ('site_area','frontage','site_depth','footprint_area','gross_floor_area','net_floor_area','usable_area','height','opening_width','opening_height','vehicle_width_limit','vehicle_height_limit','vehicle_weight_limit','slope')),
  numeric_value numeric(16,4) NOT NULL CHECK (numeric_value>=0),
  unit_code text NOT NULL CHECK (unit_code IN ('m','m2','m3','kg','tonne','degree','person')),
  measurement_basis text NOT NULL CHECK (measurement_basis IN ('gross','net','usable','clear_opening','external','internal','design','observed','estimated','not_applicable')),
  precision_code text NOT NULL CHECK (precision_code IN ('exact','rounded','approximate','estimated')),
  method_code text NOT NULL CHECK (method_code IN ('survey','plan','instrument','inspection','document','estimate','inference')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  source_ref text NOT NULL, actor_ref text NOT NULL, confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  reason text NOT NULL, recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX physical_measurement_entity_idx ON sw_property.physical_measurement(entity_type,entity_id,measure_code,measurement_id DESC);

CREATE TABLE sw_property.building_level (
  level_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  building_id bigint NOT NULL REFERENCES sw_property.building(building_id),
  level_code text NOT NULL, level_name text NOT NULL,
  level_order smallint NOT NULL,
  level_type text NOT NULL CHECK (level_type IN ('basement','ground','upper','mezzanine','roof','plant','service','other')),
  source_ref text NOT NULL, actor_ref text NOT NULL, effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  reason text NOT NULL, recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE(building_id,level_code)
);
CREATE TABLE sw_property.building_component (
  component_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  building_id bigint NOT NULL REFERENCES sw_property.building(building_id),
  level_id bigint REFERENCES sw_property.building_level(level_id),
  component_type text NOT NULL CHECK (component_type IN ('foundation','frame','floor','wall','roof','facade','glazing','stair','lift','ramp','fire_door','fire_alarm','suppression','hvac','electrical','water','wastewater','communications','backup_power','security','other')),
  material_code text NOT NULL, condition_code text NOT NULL CHECK (condition_code IN ('excellent','good','fair','poor','critical','unknown','not_assessed','not_applicable')),
  source_ref text NOT NULL, actor_ref text NOT NULL, effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  reason text NOT NULL, recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE TABLE sw_property.premises_room (
  room_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  premises_id bigint NOT NULL REFERENCES sw_property.premises(premises_id),
  room_code text NOT NULL, room_type text NOT NULL,
  floor_level text, area_m2 numeric(12,3) CHECK (area_m2>=0),
  accessibility_state text NOT NULL CHECK (accessibility_state IN ('accessible','partially_accessible','not_accessible','unknown','not_assessed')),
  source_ref text NOT NULL, actor_ref text NOT NULL, effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  reason text NOT NULL, recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE(premises_id,room_code)
);
CREATE TABLE sw_property.utility_system (
  utility_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_type text NOT NULL CHECK (entity_type IN ('PROPERTY','BUILDING','PREMISES','UNIT')),
  entity_id bigint NOT NULL CHECK (entity_id>0),
  utility_type text NOT NULL CHECK (utility_type IN ('electricity','water','wastewater','gas','fuel','telecommunications','internet','hvac','backup_power','district_heat','other')),
  availability_state text NOT NULL CHECK (availability_state IN ('connected','available_nearby','intermittent','disconnected','not_present','unknown','not_assessed')),
  capacity_value numeric(14,3) CHECK (capacity_value>=0),
  capacity_unit text,
  service_point_ref text,
  source_ref text NOT NULL, actor_ref text NOT NULL, effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  reason text NOT NULL, recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX utility_system_entity_idx ON sw_property.utility_system(entity_type,entity_id,utility_type);

CREATE TABLE sw_property.physical_feature (
  feature_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_type text NOT NULL CHECK (entity_type IN ('PROPERTY','BUILDING','PREMISES','UNIT','ACCESS_POINT')),
  entity_id bigint NOT NULL CHECK (entity_id>0),
  feature_type text NOT NULL CHECK (feature_type IN ('yard','court','parking','loading_area','refuse_area','plant_room','lobby','corridor','stairwell','lift','toilet','assembly_point','security_perimeter','ramp','dock','turning_area','queue_area','fire_escape','meter_point','other')),
  feature_label text, feature_state text NOT NULL CHECK (feature_state IN ('present','absent','unknown','not_assessed')),
  source_ref text NOT NULL, actor_ref text NOT NULL, effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  reason text NOT NULL, recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX physical_feature_entity_idx ON sw_property.physical_feature(entity_type,entity_id,feature_type);

CREATE TABLE sw_property.condition_assessment (
  assessment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_type text NOT NULL CHECK (entity_type IN ('PROPERTY','BUILDING','PREMISES','UNIT','ACCESS_POINT')),
  entity_id bigint NOT NULL CHECK (entity_id>0),
  element_code text NOT NULL CHECK (element_code IN ('overall','site','structure','foundation','frame','roof','facade','internal_fabric','electrical','water','wastewater','hvac','fire_safety','security','accessibility','surface','gate','door','other')),
  condition_code text NOT NULL CHECK (condition_code IN ('excellent','good','fair','poor','critical','unknown','not_assessed','not_applicable')),
  assessed_tick bigint NOT NULL CHECK (assessed_tick>=0),
  assessor_ref text NOT NULL, source_ref text NOT NULL,
  confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  findings text NOT NULL, recommended_action text,
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX condition_assessment_entity_idx ON sw_property.condition_assessment(entity_type,entity_id,assessed_tick DESC);

CREATE TABLE sw_property.physical_defect (
  defect_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_type text NOT NULL CHECK (entity_type IN ('PROPERTY','BUILDING','PREMISES','UNIT','ACCESS_POINT')),
  entity_id bigint NOT NULL CHECK (entity_id>0),
  defect_code text NOT NULL, severity text NOT NULL CHECK (severity IN ('low','moderate','high','critical','unknown')),
  defect_state text NOT NULL CHECK (defect_state IN ('open','contained','repair_planned','repaired','closed','unverified')),
  discovered_tick bigint NOT NULL CHECK (discovered_tick>=0),
  source_ref text NOT NULL, actor_ref text NOT NULL, confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  description text NOT NULL, action_required text,
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX physical_defect_entity_idx ON sw_property.physical_defect(entity_type,entity_id,discovered_tick DESC);

CREATE TABLE sw_property.asset_assertion (
  assertion_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entity_type text NOT NULL CHECK (entity_type IN ('PROPERTY','BUILDING','PREMISES','UNIT','ACCESS_POINT')),
  entity_id bigint NOT NULL CHECK (entity_id>0),
  attribute_code text NOT NULL, value_text text,
  knowledge_state text NOT NULL CHECK (knowledge_state IN ('known','unknown','not_assessed','not_applicable','not_present')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  source_ref text NOT NULL, actor_ref text NOT NULL,
  confidence_code text NOT NULL CHECK (confidence_code IN ('verified','documented','observed','estimated','inferred','unknown')),
  reason text NOT NULL, recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK ((knowledge_state='known' AND value_text IS NOT NULL) OR (knowledge_state<>'known' AND value_text IS NULL))
);
CREATE INDEX asset_assertion_entity_idx ON sw_property.asset_assertion(entity_type,entity_id,attribute_code,assertion_id DESC);

-- Polymorphic references are checked against the correct canonical BP04-01 table.
CREATE FUNCTION sw_property.guard_profile_entity_ref()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE ok boolean;
BEGIN
  CASE NEW.entity_type
    WHEN 'PROPERTY' THEN SELECT EXISTS(SELECT 1 FROM sw_property.property_asset WHERE property_id=NEW.entity_id) INTO ok;
    WHEN 'BUILDING' THEN SELECT EXISTS(SELECT 1 FROM sw_property.building WHERE building_id=NEW.entity_id) INTO ok;
    WHEN 'PREMISES' THEN SELECT EXISTS(SELECT 1 FROM sw_property.premises WHERE premises_id=NEW.entity_id) INTO ok;
    WHEN 'UNIT' THEN SELECT EXISTS(SELECT 1 FROM sw_property.unit_space WHERE unit_id=NEW.entity_id) INTO ok;
    WHEN 'ACCESS_POINT' THEN SELECT EXISTS(SELECT 1 FROM sw_property.access_point WHERE access_point_id=NEW.entity_id) INTO ok;
    ELSE ok:=false;
  END CASE;
  IF NOT ok THEN RAISE EXCEPTION 'BP04 profile detail references a missing or mismatched physical identity'; END IF;
  RETURN NEW;
END
$$;
DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['physical_measurement','physical_feature','condition_assessment','physical_defect','asset_assertion'] LOOP
    EXECUTE format('CREATE TRIGGER %I_entity_guard BEFORE INSERT OR UPDATE ON sw_property.%I FOR EACH ROW EXECUTE FUNCTION sw_property.guard_profile_entity_ref()',t||'_entity_guard',t);
  END LOOP;
  FOREACH t IN ARRAY ARRAY['utility_system'] LOOP
    EXECUTE format('CREATE TRIGGER %I_entity_guard BEFORE INSERT OR UPDATE ON sw_property.%I FOR EACH ROW EXECUTE FUNCTION sw_property.guard_profile_entity_ref()',t||'_entity_guard',t);
  END LOOP;
END
$$;

-- Profile and child facts are append-only. Corrections are new sourced assertions/assessments.
CREATE FUNCTION sw_property.reject_profile_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'BP04 detailed profiles and assessments are append-only; record a new sourced version';
END
$$;
DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['property_profile','building_profile','premises_profile','unit_profile','access_point_profile','physical_measurement','building_level','building_component','premises_room','utility_system','physical_feature','condition_assessment','physical_defect','asset_assertion'] LOOP
    EXECUTE format('CREATE TRIGGER %I_append_only BEFORE UPDATE OR DELETE ON sw_property.%I FOR EACH ROW EXECUTE FUNCTION sw_property.reject_profile_mutation()',t||'_append_only',t);
  END LOOP;
END
$$;

GRANT SELECT ON ALL TABLES IN SCHEMA sw_property TO sw_game_readonly;
REVOKE ALL ON ALL TABLES IN SCHEMA sw_property FROM PUBLIC,sw_game_command,sw_game_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA sw_property TO sw_game_readonly;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA sw_property FROM PUBLIC,sw_game_command,sw_game_readonly;
INSERT INTO sw_ops.storage_operation(operation_kind,description,status,measurement_notes)
VALUES('migration','0012 BP04-02 deep physical asset and space profiles','succeeded',
 'Disposable PostgreSQL 16 only. Typed profiles, measurements, levels, components, rooms, utilities, features, condition, defects and sourced assertions; no city inventory and no Neon production write.');
COMMIT;
