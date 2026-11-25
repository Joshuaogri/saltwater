-- BP08 operational unit catalogue, membership, readiness and deployment.
BEGIN;

CREATE TABLE sw_police.unit_profile (
  unit_id text PRIMARY KEY REFERENCES sw_police.organisation_component(component_id),
  unit_type_code text NOT NULL,
  functional_domain text NOT NULL CHECK(functional_domain IN
    ('frontline','communications','investigation','intelligence','specialist',
     'public_protection','governance','support')),
  mandate text NOT NULL,
  prohibited_functions text NOT NULL,
  dispatchable boolean NOT NULL DEFAULT false,
  minimum_crew_size smallint NOT NULL CHECK(minimum_crew_size>0),
  target_crew_size smallint NOT NULL CHECK(target_crew_size>=minimum_crew_size),
  maximum_crew_size smallint NOT NULL CHECK(maximum_crew_size>=target_crew_size),
  capability_codes text[] NOT NULL,
  geographic_scope text NOT NULL DEFAULT 'SALTWATER_CITY_STATE',
  lifecycle_state text NOT NULL CHECK(lifecycle_state IN ('active','suspended','closed')),
  source_ref text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO sw_police.unit_profile
(unit_id,unit_type_code,functional_domain,mandate,prohibited_functions,dispatchable,
 minimum_crew_size,target_crew_size,maximum_crew_size,capability_codes,geographic_scope,lifecycle_state,source_ref)
VALUES
('SWPS-UNIT-PATROL','general_patrol','frontline','Routine and directed patrol, public contact and first response.','No independent investigative command or specialist authority by unit label.',true,2,6,12,ARRAY['patrol','first_response','public_contact'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-TRAFFIC','traffic_road_policing','frontline','Traffic enforcement, road safety and collision response.','No authority beyond verified officer powers and qualifications.',true,2,4,8,ARRAY['traffic','road_safety','collision_response'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-PORT','port_maritime_policing','frontline','Port, harbour and maritime interface policing.','No external jurisdiction beyond Saltwater city-state waters and canon.',true,2,4,8,ARRAY['port','maritime','cargo_interface'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-PUBLICORDER','public_order_events','frontline','Public-order and event support.','No tactical deployment without required authority and qualifications.',true,4,8,16,ARRAY['public_order','event_support','crowd_safety'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-CALLTAKE','call_taking','communications','Receive, queue and assess public contacts.','Cannot dispatch units or determine incident command.',false,1,6,12,ARRAY['call_taking','contact_assessment','location_capture'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-DISPATCH','cad_dispatch','communications','Coordinate CAD events and dispatch tasks.','Cannot invent unit availability or exercise incident command.',false,1,6,12,ARRAY['cad','dispatch','resource_coordination'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-RADIO','radio_operations','communications','Coordinate operational radio traffic.','Transmission does not prove receipt, understanding or compliance.',false,1,4,8,ARRAY['radio_control','message_routing','channel_discipline'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-GENINV','general_investigations','investigation','Investigate general criminal matters.','No automatic arrest, search or disclosure authority.',false,2,12,30,ARRAY['general_investigation','casework'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-MAJOR','major_crime','investigation','Investigate serious and complex crime.','No access to restricted intelligence without authorisation.',false,3,8,16,ARRAY['major_crime','complex_investigation'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-FINCRIME','financial_economic_crime','investigation','Investigate fraud, corruption and economic crime.','No financial account access without purpose and authority.',false,2,6,12,ARRAY['fraud','financial_investigation','economic_crime'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-CYBER','cybercrime','investigation','Investigate cyber-enabled and digital crime.','No unauthorised system access or surveillance.',false,2,6,12,ARRAY['cybercrime','digital_investigation'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-MARITIME','maritime_cargo_crime','investigation','Investigate maritime, shipping and cargo crime.','No authority over external ports or foreign territory.',false,2,6,12,ARRAY['maritime_crime','cargo_theft','shipping_fraud'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-CRIMEAN','crime_analysis','intelligence','Provide analytical support from authorised records.','No independent operational command or unverified identity claims.',false,1,6,10,ARRAY['crime_analysis','demand_analysis','pattern_analysis'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-INTELDEV','intelligence_development','intelligence','Develop and assess intelligence reports.','No unrestricted dissemination of protected intelligence.',false,1,6,10,ARRAY['intelligence_development','source_assessment'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-THREAT','threat_assessment','intelligence','Assess operational threats and emerging risks.','Assessment is not proof of offence or guilt.',false,1,4,8,ARRAY['threat_assessment','risk_analysis'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-TACTICAL','tactical_response','specialist','Provide qualified specialist response support.','No deployment without verified specialist qualification and authority.',true,4,8,16,ARRAY['tactical_response','specialist_support'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-SCENES','scenes_forensic_liaison','specialist','Coordinate crime-scene and forensic support referrals.','Does not own evidence continuity or forensic conclusions.',false,2,6,10,ARRAY['scene_support','forensic_liaison'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-SAFE','safeguarding','public_protection','Coordinate safeguarding and vulnerable-person response.','No unverified diagnosis or disclosure beyond role.',true,2,6,12,ARRAY['safeguarding','vulnerable_persons'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-MISSING','missing_persons','public_protection','Coordinate missing-person response and search liaison.','No assumption that a missing person is a crime victim or suspect.',true,2,6,12,ARRAY['missing_persons','search_coordination'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-COMPLAINTS','complaints','governance','Receive and triage complaints.','Cannot determine findings outside authorised process.',false,1,3,6,ARRAY['complaints_intake','triage'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-INTERNAL','internal_investigations','governance','Investigate internal misconduct allegations.','No access to unrelated personnel material.',false,2,4,8,ARRAY['internal_investigation','professional_standards'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-INTEGRITY','integrity_anti_corruption','governance','Protect institutional integrity and investigate corruption.','No unapproved covert activity or unrestricted intelligence access.',false,2,4,8,ARRAY['integrity','anti_corruption'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-RECRUIT','recruitment_personnel','support','Administer recruitment and personnel services.','Cannot create duplicate person identities or bypass population admission.',false,1,3,6,ARRAY['recruitment','personnel_administration'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-ACADEMY','academy_development','support','Deliver police learning and development.','Training attendance alone does not prove qualification.',false,2,6,12,ARRAY['academy','training','assessment'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-FLEET','fleet_equipment','support','Manage fleet and operational equipment readiness.','Does not independently authorise deployment of personnel.',false,1,3,6,ARRAY['fleet','equipment_readiness'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-IT','it_communications','support','Maintain digital and communications capability.','No access to protected content absent a support purpose and permission.',false,1,3,6,ARRAY['it_support','communications_systems'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-LOGISTICS','logistics','support','Coordinate stores, supply and logistics.','No independent operational tasking authority.',false,1,3,6,ARRAY['logistics','stores','supply'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-CUSTODY','custody_management','support','Coordinate custody operations and detainee handling.','No detention or release decision without competent authority.',false,2,6,12,ARRAY['custody','detainee_welfare'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-LEGAL','legal_process_court_liaison','support','Coordinate legal process and court liaison.','No legal outcome or charging decision is inferred.',false,1,3,6,ARRAY['legal_process','court_liaison'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-RECORDS','records_management','support','Maintain authoritative police records and access workflows.','No unauthorised alteration, disclosure or deletion.',false,1,3,6,ARRAY['records_management','information_governance'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1'),
('SWPS-UNIT-PERF','performance_assurance','governance','Monitor performance and organisational assurance.','No access to case/personnel detail beyond authorised assurance purpose.',false,1,3,6,ARRAY['performance','assurance','inspection'],'SALTWATER_CITY_STATE','active','SWPS-ORG-V1');

CREATE TABLE sw_police.unit_membership (
  membership_id uuid PRIMARY KEY,
  personnel_id uuid NOT NULL REFERENCES sw_police.personnel(personnel_id),
  unit_id text NOT NULL REFERENCES sw_police.unit_profile(unit_id),
  post_id text NOT NULL REFERENCES sw_police.authorised_post(post_id),
  position_appointment_id uuid NOT NULL UNIQUE REFERENCES sw_police.career_post_appointment(position_appointment_id),
  membership_type text NOT NULL CHECK(membership_type IN ('primary','secondary','attachment','temporary_task_group','liaison')),
  supervisor_personnel_id uuid REFERENCES sw_police.personnel(personnel_id),
  effective_from_tick bigint NOT NULL CHECK(effective_from_tick>=0),
  planned_end_tick bigint,
  actual_end_tick bigint,
  source_ref text NOT NULL,
  CHECK(planned_end_tick IS NULL OR planned_end_tick>=effective_from_tick),
  CHECK(actual_end_tick IS NULL OR actual_end_tick>=effective_from_tick)
);
CREATE UNIQUE INDEX unit_one_active_primary_membership_per_person
  ON sw_police.unit_membership(personnel_id)
  WHERE membership_type='primary' AND actual_end_tick IS NULL;
CREATE UNIQUE INDEX unit_one_active_member_per_post
  ON sw_police.unit_membership(post_id)
  WHERE actual_end_tick IS NULL;
CREATE INDEX unit_membership_unit_idx
  ON sw_police.unit_membership(unit_id,effective_from_tick DESC);

CREATE FUNCTION sw_police.create_unit_membership_from_post()
RETURNS trigger LANGUAGE plpgsql AS $bp08$
DECLARE v_unit_id text;
BEGIN
  SELECT c.component_id INTO v_unit_id
  FROM sw_police.authorised_post p
  JOIN sw_police.organisation_component c ON c.component_id=p.component_id
  WHERE p.post_id=NEW.post_id AND c.component_type='unit';
  IF v_unit_id IS NOT NULL THEN
    INSERT INTO sw_police.unit_membership(
      membership_id,personnel_id,unit_id,post_id,position_appointment_id,
      membership_type,effective_from_tick,source_ref
    ) VALUES (
      gen_random_uuid(),NEW.personnel_id,v_unit_id,NEW.post_id,
      NEW.position_appointment_id,CASE WHEN NEW.appointment_type='substantive' THEN 'primary' ELSE 'attachment' END,NEW.effective_from_tick,
      'BP08:career-post:'||NEW.position_appointment_id::text
    );
  END IF;
  RETURN NEW;
END
$bp08$;
CREATE TRIGGER unit_membership_from_career_post
AFTER INSERT ON sw_police.career_post_appointment
FOR EACH ROW EXECUTE FUNCTION sw_police.create_unit_membership_from_post();

CREATE TABLE sw_police.unit_status_event (
  unit_status_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  unit_id text NOT NULL REFERENCES sw_police.unit_profile(unit_id),
  status text NOT NULL CHECK(status IN
    ('available','committed','deployed','unavailable','out_of_service','training','administrative')),
  effective_tick bigint NOT NULL CHECK(effective_tick>=0),
  source_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  actor_ref text NOT NULL,
  reason text NOT NULL,
  location_ref text,
  source_ref text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX unit_status_history_idx
  ON sw_police.unit_status_event(unit_id,effective_tick DESC,unit_status_event_id DESC);

CREATE TABLE sw_police.unit_deployment (
  deployment_id uuid PRIMARY KEY,
  unit_id text NOT NULL REFERENCES sw_police.unit_profile(unit_id),
  deployment_type text NOT NULL CHECK(deployment_type IN
    ('beat','shift','call_response','incident','case_support','planned_operation',
     'public_event','specialist_assistance','reinforcement','training_exercise','emergency_redeployment')),
  task_ref text,
  location_ref text,
  geographic_scope text NOT NULL DEFAULT 'SALTWATER_CITY_STATE',
  objective text NOT NULL,
  issuing_personnel_id uuid REFERENCES sw_police.personnel(personnel_id),
  authority_ref text NOT NULL,
  start_tick bigint NOT NULL CHECK(start_tick>=0),
  planned_end_tick bigint,
  actual_end_tick bigint,
  status text NOT NULL CHECK(status IN
    ('proposed','awaiting_approval','authorised','issued','acknowledged','mobilising',
     'active','paused','reassigned','stood_down','completed','cancelled','expired','rejected')),
  priority smallint NOT NULL CHECK(priority BETWEEN 1 AND 5),
  source_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  idempotency_key text NOT NULL UNIQUE,
  source_ref text NOT NULL,
  CHECK(planned_end_tick IS NULL OR planned_end_tick>=start_tick),
  CHECK(actual_end_tick IS NULL OR actual_end_tick>=start_tick),
  CHECK(geographic_scope='SALTWATER_CITY_STATE')
);
CREATE INDEX unit_deployment_active_idx
  ON sw_police.unit_deployment(unit_id,start_tick DESC)
  WHERE status IN ('authorised','issued','acknowledged','mobilising','active','paused');

CREATE TABLE sw_police.unit_deployment_member (
  deployment_id uuid NOT NULL REFERENCES sw_police.unit_deployment(deployment_id),
  membership_id uuid NOT NULL REFERENCES sw_police.unit_membership(membership_id),
  assigned_tick bigint NOT NULL CHECK(assigned_tick>=0),
  released_tick bigint,
  role_code text NOT NULL,
  source_ref text NOT NULL,
  PRIMARY KEY(deployment_id,membership_id),
  CHECK(released_tick IS NULL OR released_tick>=assigned_tick)
);

CREATE TABLE sw_police.unit_deployment_event (
  deployment_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  deployment_id uuid NOT NULL REFERENCES sw_police.unit_deployment(deployment_id),
  source_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
  event_kind text NOT NULL CHECK(event_kind IN
    ('proposed','authorised','issued','acknowledged','mobilising','started','paused',
     'reassigned','stood_down','completed','cancelled','expired','rejected')),
  prior_status text,
  resulting_status text NOT NULL,
  effective_tick bigint NOT NULL CHECK(effective_tick>=0),
  actor_ref text NOT NULL,
  authority_ref text,
  reason text NOT NULL,
  source_ref text NOT NULL
);

CREATE FUNCTION sw_police.reject_unit_history_mutation() RETURNS trigger
LANGUAGE plpgsql AS $bp08$
BEGIN
  RAISE EXCEPTION '% is append-only; record a new unit status/deployment event',TG_TABLE_NAME;
END
$bp08$;
CREATE TRIGGER unit_status_event_immutable
BEFORE UPDATE OR DELETE ON sw_police.unit_status_event
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_unit_history_mutation();
CREATE TRIGGER unit_deployment_event_immutable
BEFORE UPDATE OR DELETE ON sw_police.unit_deployment_event
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_unit_history_mutation();

CREATE VIEW sw_police.unit_establishment AS
SELECT u.unit_id,c.official_name,count(p.post_id)::integer AS authorised_posts,
       count(p.post_id) FILTER(WHERE p.post_status='vacant')::integer AS vacant_posts,
       count(p.post_id) FILTER(WHERE p.post_status='filled')::integer AS filled_posts
FROM sw_police.unit_profile u
JOIN sw_police.current_organisation_component c ON c.component_id=u.unit_id
LEFT JOIN sw_police.authorised_post p ON p.component_id=u.unit_id
GROUP BY u.unit_id,c.official_name;

CREATE VIEW sw_police.unit_current_status AS
SELECT u.unit_id,
       coalesce(s.status,'unavailable') AS operational_status,
       s.effective_tick AS status_effective_tick,
       s.source_ref AS status_source_ref
FROM sw_police.unit_profile u
LEFT JOIN LATERAL (
  SELECT status,effective_tick,source_ref
  FROM sw_police.unit_status_event e
  WHERE e.unit_id=u.unit_id
  ORDER BY effective_tick DESC,unit_status_event_id DESC LIMIT 1
) s ON true;

CREATE VIEW sw_police.unit_readiness AS
SELECT u.unit_id,c.official_name,u.unit_type_code,u.functional_domain,u.dispatchable,
       u.minimum_crew_size,u.target_crew_size,u.maximum_crew_size,
       coalesce(m.active_members,0)::integer AS active_members,
       s.operational_status,
       (u.lifecycle_state='active' AND u.dispatchable
         AND s.operational_status='available'
         AND coalesce(m.active_members,0)>=u.minimum_crew_size) AS staffing_eligible,
       false AS dispatch_eligible,
       CASE
         WHEN u.lifecycle_state<>'active' THEN 'unit_not_active'
         WHEN NOT u.dispatchable THEN 'not_a_dispatch_unit'
         WHEN s.operational_status<>'available' THEN 'unit_not_verified_available'
         WHEN coalesce(m.active_members,0)<u.minimum_crew_size THEN 'below_minimum_crew'
         ELSE 'resource_readiness_not_integrated'
       END AS readiness_reason
FROM sw_police.unit_profile u
JOIN sw_police.current_organisation_component c ON c.component_id=u.unit_id
JOIN sw_police.unit_current_status s USING(unit_id)
LEFT JOIN LATERAL (
  SELECT count(*) AS active_members
  FROM sw_police.unit_membership um
  JOIN sw_police.personnel_service_current p ON p.personnel_id=um.personnel_id
  WHERE um.unit_id=u.unit_id AND um.actual_end_tick IS NULL
    AND p.service_state IN ('active','probationary')
) m ON true;

INSERT INTO sw_core.event_type(event_code,description) VALUES
 ('UNIT_STATUS_CHANGED','Police unit operational status changed'),
 ('UNIT_DEPLOYMENT_PROPOSED','Police unit deployment proposed'),
 ('UNIT_DEPLOYMENT_AUTHORISED','Police unit deployment authorised'),
 ('UNIT_DEPLOYMENT_ISSUED','Police unit deployment order issued'),
 ('UNIT_DEPLOYMENT_ACKNOWLEDGED','Police unit deployment acknowledged'),
 ('UNIT_DEPLOYMENT_STARTED','Police unit deployment started'),
 ('UNIT_DEPLOYMENT_CHANGED','Police unit deployment changed'),
 ('UNIT_DEPLOYMENT_COMPLETED','Police unit deployment completed'),
 ('UNIT_DEPLOYMENT_CANCELLED','Police unit deployment cancelled')
ON CONFLICT (event_code) DO NOTHING;

COMMIT;
