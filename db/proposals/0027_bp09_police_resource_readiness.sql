-- BP09 initial police resource catalogue, asset pool and unit readiness.
BEGIN;

CREATE TABLE sw_police.resource_model (
  resource_model_id text PRIMARY KEY,
  model_code text NOT NULL UNIQUE,
  category_code text NOT NULL CHECK(category_code IN
    ('vehicle','communications','computing','personal_safety','medical','traffic','scene_support')),
  model_name text NOT NULL,
  description text NOT NULL,
  unit_of_measure text NOT NULL,
  serialized boolean NOT NULL,
  maintenance_required boolean NOT NULL,
  restricted_use boolean NOT NULL,
  source_ref text NOT NULL
);

CREATE TABLE sw_police.resource_asset (
  asset_id text PRIMARY KEY,
  resource_model_id text NOT NULL REFERENCES sw_police.resource_model(resource_model_id),
  asset_tag text NOT NULL UNIQUE,
  lifecycle_state text NOT NULL CHECK(lifecycle_state IN
    ('available','allocated','issued','maintenance','quarantined','lost','retired','disposed')),
  serviceability_state text NOT NULL CHECK(serviceability_state IN
    ('serviceable','unserviceable','restricted','unknown')),
  condition_code text NOT NULL CHECK(condition_code IN ('new','good','fair','poor','unknown')),
  owner_component_id text NOT NULL REFERENCES sw_police.organisation_component(component_id),
  location_ref text NOT NULL,
  acquired_tick bigint NOT NULL CHECK(acquired_tick>=0),
  source_ref text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX resource_asset_model_state_idx
  ON sw_police.resource_asset(resource_model_id,lifecycle_state,serviceability_state);

CREATE TABLE sw_police.resource_asset_event (
  asset_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  asset_id text NOT NULL REFERENCES sw_police.resource_asset(asset_id),
  event_kind text NOT NULL CHECK(event_kind IN
    ('registered','lifecycle_changed','serviceability_changed','moved','inspection_recorded',
     'maintenance_started','maintenance_completed','lost','recovered','retired')),
  prior_lifecycle_state text,
  resulting_lifecycle_state text NOT NULL,
  prior_serviceability_state text,
  resulting_serviceability_state text NOT NULL,
  effective_tick bigint NOT NULL CHECK(effective_tick>=0),
  source_event_id bigint REFERENCES sw_core.simulation_event(event_id),
  actor_ref text NOT NULL,
  reason text NOT NULL,
  source_ref text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX resource_asset_event_history_idx
  ON sw_police.resource_asset_event(asset_id,asset_event_id);

CREATE TABLE sw_police.unit_resource_requirement (
  unit_id text NOT NULL REFERENCES sw_police.unit_profile(unit_id),
  resource_model_id text NOT NULL REFERENCES sw_police.resource_model(resource_model_id),
  minimum_quantity integer NOT NULL CHECK(minimum_quantity>0),
  required_for_dispatch boolean NOT NULL DEFAULT true,
  source_ref text NOT NULL,
  PRIMARY KEY(unit_id,resource_model_id)
);

CREATE TABLE sw_police.resource_allocation (
  allocation_id text PRIMARY KEY,
  asset_id text NOT NULL REFERENCES sw_police.resource_asset(asset_id),
  unit_id text NOT NULL REFERENCES sw_police.unit_profile(unit_id),
  allocation_type text NOT NULL CHECK(allocation_type IN ('unit_pool','named_custodian','temporary_task')),
  status text NOT NULL CHECK(status IN ('active','released','suspended')),
  effective_from_tick bigint NOT NULL CHECK(effective_from_tick>=0),
  effective_to_tick bigint,
  source_ref text NOT NULL,
  CHECK(effective_to_tick IS NULL OR effective_to_tick>=effective_from_tick)
);
CREATE UNIQUE INDEX resource_one_active_allocation
  ON sw_police.resource_allocation(asset_id)
  WHERE status='active' AND effective_to_tick IS NULL;
CREATE INDEX resource_allocation_unit_idx
  ON sw_police.resource_allocation(unit_id,status);

CREATE TABLE sw_police.resource_allocation_event (
  allocation_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  allocation_id text NOT NULL REFERENCES sw_police.resource_allocation(allocation_id),
  event_kind text NOT NULL CHECK(event_kind IN ('allocated','transferred','released','suspended','reinstated')),
  effective_tick bigint NOT NULL CHECK(effective_tick>=0),
  actor_ref text NOT NULL,
  reason text NOT NULL,
  source_ref text NOT NULL
);

CREATE FUNCTION sw_police.reject_resource_history_mutation() RETURNS trigger
LANGUAGE plpgsql AS $bp09$
BEGIN
  RAISE EXCEPTION '% is append-only; record a new resource event',TG_TABLE_NAME;
END
$bp09$;
CREATE TRIGGER resource_asset_event_immutable\nBEFORE UPDATE OR DELETE ON sw_police.resource_asset_event\nFOR EACH ROW EXECUTE FUNCTION sw_police.reject_resource_history_mutation();\nCREATE TRIGGER resource_allocation_event_immutable
BEFORE UPDATE OR DELETE ON sw_police.resource_allocation_event
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_resource_history_mutation();

INSERT INTO sw_police.resource_model
(resource_model_id,model_code,category_code,model_name,description,unit_of_measure,serialized,maintenance_required,restricted_use,source_ref)
VALUES
('SWPS-RM-PATROL-VEH','PATROL_VEHICLE','vehicle','Marked patrol vehicle','Standard marked frontline response vehicle.','vehicle',true,true,false,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-TRAFFIC-VEH','TRAFFIC_VEHICLE','vehicle','Traffic response vehicle','Traffic and road-policing vehicle.','vehicle',true,true,false,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-PORT-VEH','PORT_MARITIME_VEHICLE','vehicle','Port and maritime response vehicle','Vehicle configured for port and harbour access.','vehicle',true,true,false,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-PUBLICORDER-VAN','PUBLIC_ORDER_VAN','vehicle','Public-order support van','Team transport and public-order equipment vehicle.','vehicle',true,true,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-TACTICAL-VEH','TACTICAL_SUPPORT_VEHICLE','vehicle','Tactical support vehicle','Specialist support vehicle; controlled use.','vehicle',true,true,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-SAFEGUARD-VEH','SAFEGUARDING_VEHICLE','vehicle','Safeguarding response vehicle','Unmarked or low-profile safeguarding response vehicle.','vehicle',true,true,false,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-SEARCH-VEH','SEARCH_VEHICLE','vehicle','Search and missing-person vehicle','Vehicle for search coordination and missing-person response.','vehicle',true,true,false,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-CUSTODY-VEH','CUSTODY_TRANSPORT_VEHICLE','vehicle','Custody transport vehicle','Secure custody transport vehicle.','vehicle',true,true,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-RADIO','HANDHELD_RADIO','communications','Handheld operational radio','Secure portable operational radio.','device',true,true,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-MDT','MOBILE_DATA_TERMINAL','computing','Mobile data terminal','Vehicle-mounted or portable operational data terminal.','device',true,true,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-BWC','BODY_WORN_CAMERA','communications','Body-worn camera','Officer-worn recording device; content governed by records policy.','device',true,true,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-FIRSTAID','FIRST_AID_KIT','medical','Operational first-aid kit','Basic field first-aid kit.','kit',true,true,false,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-PPE','PERSONAL_PROTECTIVE_KIT','personal_safety','Personal protective equipment kit','Standard protective equipment issue kit.','kit',true,true,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-SPEED','SPEED_DETECTION_KIT','traffic','Traffic speed-detection kit','Traffic speed measurement equipment.','kit',true,true,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-RM-SCENE','SCENE_SUPPORT_KIT','scene_support','Scene support kit','Initial scene protection and documentation kit.','kit',true,true,true,'SWPS-RESOURCE-BASELINE-V1');

WITH models(resource_model_id,tag_prefix,asset_count) AS (
 VALUES
 ('SWPS-RM-PATROL-VEH','SPS-PV',24),('SWPS-RM-TRAFFIC-VEH','SPS-TV',6),
 ('SWPS-RM-PORT-VEH','SPS-MV',4),('SWPS-RM-PUBLICORDER-VAN','SPS-POV',4),
 ('SWPS-RM-TACTICAL-VEH','SPS-XV',2),('SWPS-RM-SAFEGUARD-VEH','SPS-SGV',3),
 ('SWPS-RM-SEARCH-VEH','SPS-SRV',3),('SWPS-RM-CUSTODY-VEH','SPS-CV',4),
 ('SWPS-RM-RADIO','SPS-RAD',110),('SWPS-RM-MDT','SPS-MDT',45),
 ('SWPS-RM-BWC','SPS-BWC',100),('SWPS-RM-FIRSTAID','SPS-FAK',110),
 ('SWPS-RM-PPE','SPS-PPE',100),('SWPS-RM-SPEED','SPS-SPD',6),
 ('SWPS-RM-SCENE','SPS-SCK',6)
)
INSERT INTO sw_police.resource_asset(
 asset_id,resource_model_id,asset_tag,lifecycle_state,serviceability_state,
 condition_code,owner_component_id,location_ref,acquired_tick,source_ref
)
SELECT 'SWPS-ASSET-'||m.tag_prefix||'-'||lpad(g.n::text,3,'0'),
       m.resource_model_id,m.tag_prefix||'-'||lpad(g.n::text,3,'0'),
       'available','serviceable','good','SWPS-DEP-001',
       'SWPS-CENTRAL-RESOURCE-STORE',0,'SWPS-RESOURCE-BASELINE-V1'
FROM models m CROSS JOIN LATERAL generate_series(1,m.asset_count) AS g(n);

INSERT INTO sw_police.resource_asset_event(
 asset_id,event_kind,resulting_lifecycle_state,resulting_serviceability_state,
 effective_tick,actor_ref,reason,source_ref
)
SELECT asset_id,'registered',lifecycle_state,serviceability_state,0,
       'system:resource-baseline','Initial fictional police resource asset registered.',
       'SWPS-RESOURCE-BASELINE-V1'
FROM sw_police.resource_asset;

WITH plan(resource_model_id,unit_id,first_no,quantity) AS (
 VALUES
 ('SWPS-RM-PATROL-VEH','SWPS-UNIT-PATROL',1,24),
 ('SWPS-RM-TRAFFIC-VEH','SWPS-UNIT-TRAFFIC',1,6),
 ('SWPS-RM-PORT-VEH','SWPS-UNIT-PORT',1,4),
 ('SWPS-RM-PUBLICORDER-VAN','SWPS-UNIT-PUBLICORDER',1,4),
 ('SWPS-RM-TACTICAL-VEH','SWPS-UNIT-TACTICAL',1,2),
 ('SWPS-RM-SAFEGUARD-VEH','SWPS-UNIT-SAFE',1,3),
 ('SWPS-RM-SEARCH-VEH','SWPS-UNIT-MISSING',1,3),
 ('SWPS-RM-CUSTODY-VEH','SWPS-UNIT-CUSTODY',1,4),
 ('SWPS-RM-RADIO','SWPS-UNIT-PATROL',1,48),
 ('SWPS-RM-RADIO','SWPS-UNIT-TRAFFIC',49,12),
 ('SWPS-RM-RADIO','SWPS-UNIT-PORT',61,8),
 ('SWPS-RM-RADIO','SWPS-UNIT-PUBLICORDER',69,16),
 ('SWPS-RM-RADIO','SWPS-UNIT-TACTICAL',85,8),
 ('SWPS-RM-RADIO','SWPS-UNIT-SAFE',93,6),
 ('SWPS-RM-RADIO','SWPS-UNIT-MISSING',99,6),
 ('SWPS-RM-MDT','SWPS-UNIT-PATROL',1,24),
 ('SWPS-RM-MDT','SWPS-UNIT-TRAFFIC',25,6),
 ('SWPS-RM-MDT','SWPS-UNIT-PORT',31,4),
 ('SWPS-RM-MDT','SWPS-UNIT-MISSING',35,6),
 ('SWPS-RM-BWC','SWPS-UNIT-PATROL',1,48),
 ('SWPS-RM-BWC','SWPS-UNIT-TRAFFIC',49,12),
 ('SWPS-RM-BWC','SWPS-UNIT-PORT',61,8),
 ('SWPS-RM-BWC','SWPS-UNIT-PUBLICORDER',69,16),
 ('SWPS-RM-BWC','SWPS-UNIT-TACTICAL',85,8),
 ('SWPS-RM-BWC','SWPS-UNIT-SAFE',93,6),
 ('SWPS-RM-FIRSTAID','SWPS-UNIT-PATROL',1,48),
 ('SWPS-RM-FIRSTAID','SWPS-UNIT-TRAFFIC',49,12),
 ('SWPS-RM-FIRSTAID','SWPS-UNIT-PORT',61,8),
 ('SWPS-RM-FIRSTAID','SWPS-UNIT-PUBLICORDER',69,16),
 ('SWPS-RM-FIRSTAID','SWPS-UNIT-TACTICAL',85,8),
 ('SWPS-RM-FIRSTAID','SWPS-UNIT-SAFE',93,6),
 ('SWPS-RM-FIRSTAID','SWPS-UNIT-MISSING',99,6),
 ('SWPS-RM-PPE','SWPS-UNIT-PATROL',1,48),
 ('SWPS-RM-PPE','SWPS-UNIT-TRAFFIC',49,12),
 ('SWPS-RM-PPE','SWPS-UNIT-PORT',61,8),
 ('SWPS-RM-PPE','SWPS-UNIT-PUBLICORDER',69,16),
 ('SWPS-RM-PPE','SWPS-UNIT-TACTICAL',85,8),
 ('SWPS-RM-SPEED','SWPS-UNIT-TRAFFIC',1,6),
 ('SWPS-RM-SCENE','SWPS-UNIT-SCENES',1,6)
)
INSERT INTO sw_police.resource_allocation(
 allocation_id,asset_id,unit_id,allocation_type,status,effective_from_tick,source_ref
)
SELECT 'SWPS-ALLOC-'||p.resource_model_id||'-'||p.unit_id||'-'||lpad(n.n::text,3,'0'),
       'SWPS-ASSET-'||m.tag_prefix||'-'||lpad(n.n::text,3,'0'),
       p.unit_id,'unit_pool','active',0,'SWPS-RESOURCE-BASELINE-V1'
FROM plan p
JOIN (
 VALUES
 ('SWPS-RM-PATROL-VEH','SPS-PV'),('SWPS-RM-TRAFFIC-VEH','SPS-TV'),
 ('SWPS-RM-PORT-VEH','SPS-MV'),('SWPS-RM-PUBLICORDER-VAN','SPS-POV'),
 ('SWPS-RM-TACTICAL-VEH','SPS-XV'),('SWPS-RM-SAFEGUARD-VEH','SPS-SGV'),
 ('SWPS-RM-SEARCH-VEH','SPS-SRV'),('SWPS-RM-CUSTODY-VEH','SPS-CV'),
 ('SWPS-RM-RADIO','SPS-RAD'),('SWPS-RM-MDT','SPS-MDT'),
 ('SWPS-RM-BWC','SPS-BWC'),('SWPS-RM-FIRSTAID','SPS-FAK'),
 ('SWPS-RM-PPE','SPS-PPE'),('SWPS-RM-SPEED','SPS-SPD'),('SWPS-RM-SCENE','SPS-SCK')
) AS m(resource_model_id,tag_prefix) USING(resource_model_id)
CROSS JOIN LATERAL generate_series(p.first_no,p.first_no+p.quantity-1) AS n(n);

UPDATE sw_police.resource_asset a
SET lifecycle_state='allocated',
    location_ref='SWPS-UNIT-POOL:'||r.unit_id
FROM sw_police.resource_allocation r
WHERE r.asset_id=a.asset_id AND r.status='active';

INSERT INTO sw_police.resource_allocation_event(allocation_id,event_kind,effective_tick,actor_ref,reason,source_ref)
SELECT allocation_id,'allocated',0,'system:initial-resource-baseline',
       'Initial unit pool allocation from Saltwater Police Service resource establishment.',
       'SWPS-RESOURCE-BASELINE-V1'
FROM sw_police.resource_allocation;

INSERT INTO sw_police.unit_resource_requirement(unit_id,resource_model_id,minimum_quantity,required_for_dispatch,source_ref)
VALUES
('SWPS-UNIT-PATROL','SWPS-RM-PATROL-VEH',1,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PATROL','SWPS-RM-RADIO',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PATROL','SWPS-RM-MDT',1,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PATROL','SWPS-RM-BWC',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PATROL','SWPS-RM-FIRSTAID',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PATROL','SWPS-RM-PPE',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-TRAFFIC','SWPS-RM-TRAFFIC-VEH',1,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-TRAFFIC','SWPS-RM-RADIO',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-TRAFFIC','SWPS-RM-MDT',1,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-TRAFFIC','SWPS-RM-BWC',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-TRAFFIC','SWPS-RM-FIRSTAID',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-TRAFFIC','SWPS-RM-PPE',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-TRAFFIC','SWPS-RM-SPEED',1,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PORT','SWPS-RM-PORT-VEH',1,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PORT','SWPS-RM-RADIO',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PORT','SWPS-RM-MDT',1,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PORT','SWPS-RM-BWC',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PORT','SWPS-RM-FIRSTAID',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PORT','SWPS-RM-PPE',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PUBLICORDER','SWPS-RM-PUBLICORDER-VAN',1,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PUBLICORDER','SWPS-RM-RADIO',4,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PUBLICORDER','SWPS-RM-BWC',4,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PUBLICORDER','SWPS-RM-FIRSTAID',4,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-PUBLICORDER','SWPS-RM-PPE',4,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-TACTICAL','SWPS-RM-TACTICAL-VEH',1,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-TACTICAL','SWPS-RM-RADIO',4,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-TACTICAL','SWPS-RM-BWC',4,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-TACTICAL','SWPS-RM-FIRSTAID',4,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-TACTICAL','SWPS-RM-PPE',4,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-SAFE','SWPS-RM-SAFEGUARD-VEH',1,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-SAFE','SWPS-RM-RADIO',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-SAFE','SWPS-RM-BWC',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-SAFE','SWPS-RM-FIRSTAID',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-MISSING','SWPS-RM-SEARCH-VEH',1,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-MISSING','SWPS-RM-RADIO',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-MISSING','SWPS-RM-MDT',1,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-MISSING','SWPS-RM-FIRSTAID',2,true,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-SCENES','SWPS-RM-SCENE',1,false,'SWPS-RESOURCE-BASELINE-V1'),
('SWPS-UNIT-CUSTODY','SWPS-RM-CUSTODY-VEH',1,false,'SWPS-RESOURCE-BASELINE-V1');

CREATE VIEW sw_police.unit_resource_readiness AS
SELECT req.unit_id,
       bool_and(coalesce(av.available_quantity,0)>=req.minimum_quantity) AS resources_ready,
       count(*)::integer AS requirement_count,
       count(*) FILTER(WHERE coalesce(av.available_quantity,0)>=req.minimum_quantity)::integer AS satisfied_requirements
FROM sw_police.unit_resource_requirement req
LEFT JOIN LATERAL (
  SELECT count(*)::integer AS available_quantity
  FROM sw_police.resource_allocation ra
  JOIN sw_police.resource_asset a USING(asset_id)
  WHERE ra.unit_id=req.unit_id
    AND a.resource_model_id=req.resource_model_id
    AND ra.status='active' AND ra.effective_to_tick IS NULL
    AND a.lifecycle_state='allocated'
    AND a.serviceability_state='serviceable'
) av ON true
WHERE req.required_for_dispatch
GROUP BY req.unit_id;

CREATE OR REPLACE VIEW sw_police.unit_readiness AS
SELECT u.unit_id,c.official_name,u.unit_type_code,u.functional_domain,u.dispatchable,
       u.minimum_crew_size,u.target_crew_size,u.maximum_crew_size,
       coalesce(m.active_members,0)::integer AS active_members,
       s.operational_status,
       (u.lifecycle_state='active' AND u.dispatchable
         AND s.operational_status='available'
         AND coalesce(m.active_members,0)>=u.minimum_crew_size) AS staffing_eligible,
       (u.lifecycle_state='active' AND u.dispatchable
         AND s.operational_status='available'
         AND coalesce(m.active_members,0)>=u.minimum_crew_size
         AND coalesce(r.resources_ready,false)) AS dispatch_eligible,
       CASE
         WHEN u.lifecycle_state<>'active' THEN 'unit_not_active'
         WHEN NOT u.dispatchable THEN 'not_a_dispatch_unit'
         WHEN s.operational_status<>'available' THEN 'unit_not_verified_available'
         WHEN coalesce(m.active_members,0)<u.minimum_crew_size THEN 'below_minimum_crew'
         WHEN coalesce(r.resources_ready,false)=false THEN 'resource_shortage_or_unverified'
         ELSE 'ready'
       END AS readiness_reason,
       coalesce(r.resources_ready,false) AS resources_ready
FROM sw_police.unit_profile u
JOIN sw_police.current_organisation_component c ON c.component_id=u.unit_id
JOIN sw_police.unit_current_status s USING(unit_id)
LEFT JOIN LATERAL (
  SELECT count(*) AS active_members
  FROM sw_police.unit_membership um
  JOIN sw_police.personnel_service_current p ON p.personnel_id=um.personnel_id
  WHERE um.unit_id=u.unit_id AND um.actual_end_tick IS NULL
    AND p.service_state IN ('active','probationary')
) m ON true
LEFT JOIN sw_police.unit_resource_readiness r USING(unit_id);

COMMIT;
