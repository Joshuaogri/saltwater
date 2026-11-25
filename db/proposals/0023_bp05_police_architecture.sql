-- BP05 police architecture and initial organisational establishment.
-- Disposable PostgreSQL implementation proposal; source records are fictional Saltwater canon.
BEGIN;

CREATE TABLE sw_police.structure_version (
  structure_version_id text PRIMARY KEY,
  version_no integer NOT NULL UNIQUE CHECK (version_no > 0),
  effective_tick bigint NOT NULL CHECK (effective_tick >= 0),
  change_reason text NOT NULL,
  source_ref text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE sw_police.organisation_component (
  component_id text PRIMARY KEY,
  component_code text NOT NULL UNIQUE,
  component_type text NOT NULL CHECK (component_type IN
    ('department','command','division','branch','unit','team')),
  created_tick bigint NOT NULL DEFAULT 0 CHECK (created_tick >= 0),
  source_ref text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE sw_police.organisation_component_version (
  component_id text NOT NULL REFERENCES sw_police.organisation_component(component_id),
  version_no integer NOT NULL CHECK (version_no > 0),
  structure_version_id text NOT NULL REFERENCES sw_police.structure_version(structure_version_id),
  parent_component_id text REFERENCES sw_police.organisation_component(component_id),
  official_name text NOT NULL,
  abbreviation text NOT NULL,
  mission text NOT NULL,
  functional_remit text NOT NULL,
  geographic_scope text NOT NULL DEFAULT 'SALTWATER_CITY_STATE',
  activation_status text NOT NULL CHECK (activation_status IN ('active','suspended','closed')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick >= 0),
  source_ref text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(component_id,version_no),
  CHECK(parent_component_id IS NULL OR parent_component_id<>component_id)
);
CREATE INDEX organisation_component_parent_idx
  ON sw_police.organisation_component_version(parent_component_id,component_id,version_no DESC);

CREATE VIEW sw_police.current_organisation_component AS
SELECT DISTINCT ON (c.component_id)
  c.component_id,c.component_code,c.component_type,v.version_no,
  v.parent_component_id,v.official_name,v.abbreviation,v.mission,
  v.functional_remit,v.geographic_scope,v.activation_status,
  v.effective_from_tick,v.source_ref
FROM sw_police.organisation_component c
JOIN sw_police.organisation_component_version v USING(component_id)
ORDER BY c.component_id,v.version_no DESC;

CREATE TABLE sw_police.rank_definition (
  rank_code text PRIMARY KEY,
  rank_title text NOT NULL UNIQUE,
  rank_order smallint NOT NULL UNIQUE CHECK(rank_order BETWEEN 1 AND 9),
  rank_group text NOT NULL CHECK(rank_group IN ('constable','supervisory','management','executive')),
  description text NOT NULL,
  source_ref text NOT NULL
);

CREATE TABLE sw_police.position_definition (
  position_id text PRIMARY KEY,
  position_code text NOT NULL UNIQUE,
  component_id text NOT NULL REFERENCES sw_police.organisation_component(component_id),
  position_title text NOT NULL,
  position_type text NOT NULL CHECK(position_type IN ('sworn','civilian','mixed')),
  purpose text NOT NULL,
  command_scope text NOT NULL,
  minimum_rank_order smallint,
  maximum_rank_order smallint,
  source_ref text NOT NULL,
  CHECK ((position_type='civilian' AND minimum_rank_order IS NULL AND maximum_rank_order IS NULL)
      OR (position_type IN ('sworn','mixed') AND minimum_rank_order BETWEEN 1 AND 9
          AND maximum_rank_order BETWEEN minimum_rank_order AND 9))
);

CREATE TABLE sw_police.authorised_post (
  post_id text PRIMARY KEY,
  post_code text NOT NULL UNIQUE,
  position_id text NOT NULL REFERENCES sw_police.position_definition(position_id),
  slot_no smallint NOT NULL CHECK(slot_no > 0),
  post_status text NOT NULL DEFAULT 'vacant' CHECK(post_status IN ('vacant','filled','frozen','abolished')),
  authorised_tick bigint NOT NULL DEFAULT 0 CHECK(authorised_tick >= 0),
  source_ref text NOT NULL,
  UNIQUE(position_id,slot_no)
);
CREATE INDEX authorised_post_position_status_idx
  ON sw_police.authorised_post(position_id,post_status);

CREATE TABLE sw_police.authorised_post_event (
  post_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  post_id text NOT NULL REFERENCES sw_police.authorised_post(post_id),
  event_code text NOT NULL CHECK(event_code IN ('authorised','filled','vacated','frozen','unfrozen','abolished')),
  prior_status text,
  new_status text NOT NULL CHECK(new_status IN ('vacant','filled','frozen','abolished')),
  effective_tick bigint NOT NULL CHECK(effective_tick >= 0),
  source_ref text NOT NULL,
  actor_ref text NOT NULL,
  reason text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX authorised_post_event_history_idx
  ON sw_police.authorised_post_event(post_id,post_event_id);

CREATE TABLE sw_police.reporting_relationship (
  relationship_id text PRIMARY KEY,
  from_component_id text NOT NULL REFERENCES sw_police.organisation_component(component_id),
  to_component_id text NOT NULL REFERENCES sw_police.organisation_component(component_id),
  relationship_type text NOT NULL CHECK(relationship_type IN
    ('administrative','command','operational','functional_support')),
  effective_from_tick bigint NOT NULL CHECK(effective_from_tick >= 0),
  source_ref text NOT NULL,
  supersedes_relationship_id text REFERENCES sw_police.reporting_relationship(relationship_id),
  CHECK(from_component_id<>to_component_id)
);
CREATE INDEX reporting_relationship_from_idx
  ON sw_police.reporting_relationship(from_component_id,effective_from_tick DESC);

CREATE TABLE sw_police.command_delegation (
  delegation_id text PRIMARY KEY,
  delegator_personnel_id uuid NOT NULL REFERENCES sw_police.personnel(personnel_id),
  delegate_personnel_id uuid NOT NULL REFERENCES sw_police.personnel(personnel_id),
  authority_code text NOT NULL,
  scope_ref text NOT NULL,
  effective_from_tick bigint NOT NULL CHECK(effective_from_tick >= 0),
  effective_to_tick bigint,
  source_ref text NOT NULL,
  CHECK(delegator_personnel_id<>delegate_personnel_id),
  CHECK(effective_to_tick IS NULL OR effective_to_tick>=effective_from_tick)
);

CREATE FUNCTION sw_police.reject_structure_history_mutation() RETURNS trigger
LANGUAGE plpgsql AS $bp05$
BEGIN
  RAISE EXCEPTION '% is append-only; create a new version/event',TG_TABLE_NAME;
END
$bp05$;
CREATE TRIGGER structure_version_immutable BEFORE UPDATE OR DELETE ON sw_police.structure_version
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_structure_history_mutation();
CREATE TRIGGER component_identity_immutable BEFORE UPDATE OR DELETE ON sw_police.organisation_component
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_structure_history_mutation();
CREATE TRIGGER component_version_immutable BEFORE UPDATE OR DELETE ON sw_police.organisation_component_version
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_structure_history_mutation();
CREATE TRIGGER rank_definition_immutable BEFORE UPDATE OR DELETE ON sw_police.rank_definition
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_structure_history_mutation();
CREATE TRIGGER post_event_immutable BEFORE UPDATE OR DELETE ON sw_police.authorised_post_event
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_structure_history_mutation();
CREATE TRIGGER reporting_relationship_immutable BEFORE UPDATE OR DELETE ON sw_police.reporting_relationship
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_structure_history_mutation();
CREATE TRIGGER command_delegation_immutable BEFORE UPDATE OR DELETE ON sw_police.command_delegation
FOR EACH ROW EXECUTE FUNCTION sw_police.reject_structure_history_mutation();

INSERT INTO sw_police.structure_version
(structure_version_id,version_no,effective_tick,change_reason,source_ref)
VALUES ('SWPS-ORG-V1',1,0,'Initial Saltwater Police Service organisational architecture','saltwater-fictional-canon');

INSERT INTO sw_police.organisation_component(component_id,component_code,component_type,source_ref)
VALUES
('SWPS-DEP-001','SALTWATER_POLICE_SERVICE','department','saltwater-fictional-canon'),
('SWPS-CMD-EXEC','EXECUTIVE_COMMAND','command','saltwater-fictional-canon'),
('SWPS-CMD-OPS','OPERATIONS_COMMAND','command','saltwater-fictional-canon'),
('SWPS-CMD-INV','INVESTIGATIONS_COMMAND','command','saltwater-fictional-canon'),
('SWPS-CMD-CORP','CORPORATE_SERVICES_COMMAND','command','saltwater-fictional-canon'),
('SWPS-DIV-EXEC','EXECUTIVE_OFFICE','division','saltwater-fictional-canon'),
('SWPS-DIV-UNIFORM','UNIFORMED_OPERATIONS','division','saltwater-fictional-canon'),
('SWPS-DIV-COMMS','EMERGENCY_COMMUNICATIONS','division','saltwater-fictional-canon'),
('SWPS-DIV-INV','CRIMINAL_INVESTIGATIONS','division','saltwater-fictional-canon'),
('SWPS-DIV-INTEL','INTELLIGENCE_ANALYSIS','division','saltwater-fictional-canon'),
('SWPS-DIV-SPEC','SPECIALIST_OPERATIONS','division','saltwater-fictional-canon'),
('SWPS-DIV-PROTECT','PUBLIC_PROTECTION','division','saltwater-fictional-canon'),
('SWPS-DIV-PS','PROFESSIONAL_STANDARDS','division','saltwater-fictional-canon'),
('SWPS-DIV-PEOPLE','PEOPLE_TRAINING','division','saltwater-fictional-canon'),
('SWPS-DIV-RES','RESOURCES_TECHNOLOGY','division','saltwater-fictional-canon'),
('SWPS-DIV-LEGAL','LEGAL_CUSTODY_LIAISON','division','saltwater-fictional-canon'),
('SWPS-DIV-RECORDS','RECORDS_PERFORMANCE','division','saltwater-fictional-canon'),
('SWPS-UNIT-PATROL','GENERAL_PATROL','unit','saltwater-fictional-canon'),
('SWPS-UNIT-TRAFFIC','TRAFFIC_ROAD_POLICING','unit','saltwater-fictional-canon'),
('SWPS-UNIT-PORT','PORT_MARITIME_POLICING','unit','saltwater-fictional-canon'),
('SWPS-UNIT-PUBLICORDER','PUBLIC_ORDER_EVENTS','unit','saltwater-fictional-canon'),
('SWPS-UNIT-CALLTAKE','CALL_TAKING','unit','saltwater-fictional-canon'),
('SWPS-UNIT-DISPATCH','CAD_DISPATCH','unit','saltwater-fictional-canon'),
('SWPS-UNIT-RADIO','RADIO_OPERATIONS','unit','saltwater-fictional-canon'),
('SWPS-UNIT-GENINV','GENERAL_INVESTIGATIONS','unit','saltwater-fictional-canon'),
('SWPS-UNIT-MAJOR','MAJOR_CRIME','unit','saltwater-fictional-canon'),
('SWPS-UNIT-FINCRIME','FINANCIAL_ECONOMIC_CRIME','unit','saltwater-fictional-canon'),
('SWPS-UNIT-CYBER','CYBERCRIME','unit','saltwater-fictional-canon'),
('SWPS-UNIT-MARITIME','MARITIME_CARGO_CRIME','unit','saltwater-fictional-canon'),
('SWPS-UNIT-CRIMEAN','CRIME_ANALYSIS','unit','saltwater-fictional-canon'),
('SWPS-UNIT-INTELDEV','INTELLIGENCE_DEVELOPMENT','unit','saltwater-fictional-canon'),
('SWPS-UNIT-THREAT','THREAT_ASSESSMENT','unit','saltwater-fictional-canon'),
('SWPS-UNIT-TACTICAL','TACTICAL_RESPONSE','unit','saltwater-fictional-canon'),
('SWPS-UNIT-SCENES','SCENES_FORENSIC_LIAISON','unit','saltwater-fictional-canon'),
('SWPS-UNIT-SAFE','SAFEGUARDING','unit','saltwater-fictional-canon'),
('SWPS-UNIT-MISSING','MISSING_PERSONS','unit','saltwater-fictional-canon'),
('SWPS-UNIT-COMPLAINTS','COMPLAINTS','unit','saltwater-fictional-canon'),
('SWPS-UNIT-INTERNAL','INTERNAL_INVESTIGATIONS','unit','saltwater-fictional-canon'),
('SWPS-UNIT-INTEGRITY','INTEGRITY_ANTI_CORRUPTION','unit','saltwater-fictional-canon'),
('SWPS-UNIT-RECRUIT','RECRUITMENT_PERSONNEL','unit','saltwater-fictional-canon'),
('SWPS-UNIT-ACADEMY','ACADEMY_DEVELOPMENT','unit','saltwater-fictional-canon'),
('SWPS-UNIT-FLEET','FLEET_EQUIPMENT','unit','saltwater-fictional-canon'),
('SWPS-UNIT-IT','IT_COMMUNICATIONS','unit','saltwater-fictional-canon'),
('SWPS-UNIT-LOGISTICS','LOGISTICS','unit','saltwater-fictional-canon'),
('SWPS-UNIT-CUSTODY','CUSTODY_MANAGEMENT','unit','saltwater-fictional-canon'),
('SWPS-UNIT-LEGAL','LEGAL_PROCESS_COURT_LIAISON','unit','saltwater-fictional-canon'),
('SWPS-UNIT-RECORDS','RECORDS_MANAGEMENT','unit','saltwater-fictional-canon'),
('SWPS-UNIT-PERF','PERFORMANCE_ASSURANCE','unit','saltwater-fictional-canon');

WITH components(component_id,parent_component_id,official_name,abbreviation,mission,functional_remit) AS (
 VALUES
 ('SWPS-DEP-001',NULL::text,'Saltwater Police Service','SPS','Provide a unified police service for the sovereign city-state.','Single-city jurisdiction; public safety, crime prevention, response, investigation and lawful enforcement.'),
 ('SWPS-CMD-EXEC','SWPS-DEP-001','Executive Command','EC','Set service direction and maintain command continuity.','Executive leadership, strategic priorities, governance and accountability.'),
 ('SWPS-CMD-OPS','SWPS-DEP-001','Operations Command','OC','Deliver visible policing and coordinated operational response.','Uniformed operations, emergency communications, specialist field response and public protection.'),
 ('SWPS-CMD-INV','SWPS-DEP-001','Investigations and Intelligence Command','IIC','Lead investigative and intelligence functions.','Criminal investigation, intelligence, analytical support and specialist crime.'),
 ('SWPS-CMD-CORP','SWPS-DEP-001','Corporate Services Command','CSC','Maintain institutional capability, standards and support.','People, training, resources, professional standards, legal liaison and records.'),
 ('SWPS-DIV-EXEC','SWPS-CMD-EXEC','Executive Office','EXO','Support the Chief of Police and executive leadership.','Executive coordination, strategic planning and command support.'),
 ('SWPS-DIV-UNIFORM','SWPS-CMD-OPS','Uniformed Operations Division','UOD','Provide frontline uniformed policing across Saltwater.','General patrol, traffic, port/maritime and public-order/event policing.'),
 ('SWPS-DIV-COMMS','SWPS-CMD-OPS','Emergency Communications Division','ECD','Receive public contacts and coordinate police communications.','Call-taking, CAD dispatch and radio operations.'),
 ('SWPS-DIV-INV','SWPS-CMD-INV','Criminal Investigations Division','CID','Investigate reported and generated criminal occurrences.','General, major, financial/economic, cyber and maritime/cargo crime.'),
 ('SWPS-DIV-INTEL','SWPS-CMD-INV','Intelligence and Analysis Division','IAD','Develop lawful intelligence and analytical support.','Crime analysis, intelligence development and threat assessment.'),
 ('SWPS-DIV-SPEC','SWPS-CMD-OPS','Specialist Operations Division','SOD','Provide specialist operational support.','Tactical response and scenes/forensic liaison.'),
 ('SWPS-DIV-PROTECT','SWPS-CMD-OPS','Public Protection Division','PPD','Coordinate safeguarding and missing-person response.','Vulnerable persons, safeguarding and missing persons.'),
 ('SWPS-DIV-PS','SWPS-CMD-CORP','Professional Standards Division','PSD','Maintain integrity, complaints and internal accountability.','Complaints, internal investigations and anti-corruption.'),
 ('SWPS-DIV-PEOPLE','SWPS-CMD-CORP','People and Training Division','PTD','Maintain recruitment, personnel administration and development.','Recruitment, personnel support and academy/training.'),
 ('SWPS-DIV-RES','SWPS-CMD-CORP','Resources and Technology Division','RTD','Maintain operational resources and technical capability.','Fleet, equipment, IT, communications and logistics.'),
 ('SWPS-DIV-LEGAL','SWPS-CMD-CORP','Legal and Custody Liaison Division','LCD','Coordinate custody and legal-process interfaces.','Custody management and court/legal process liaison.'),
 ('SWPS-DIV-RECORDS','SWPS-CMD-CORP','Records and Performance Division','RPD','Maintain records quality and organisational assurance.','Records management, performance and assurance.'),
 ('SWPS-UNIT-PATROL','SWPS-DIV-UNIFORM','General Patrol Unit','GPU','Provide routine and directed patrol coverage.','Beat patrol, public contact and initial response.'),
 ('SWPS-UNIT-TRAFFIC','SWPS-DIV-UNIFORM','Traffic and Road Policing Unit','TRP','Manage road safety and traffic-related policing.','Traffic patrol, collisions and road disruption.'),
 ('SWPS-UNIT-PORT','SWPS-DIV-UNIFORM','Port and Maritime Policing Unit','PMP','Police the port, harbour and maritime interfaces.','Port security, vessel-related incidents and cargo interface.'),
 ('SWPS-UNIT-PUBLICORDER','SWPS-DIV-UNIFORM','Public Order and Events Unit','POE','Support lawful public-order and event operations.','Public events, crowd safety and public-order support.'),
 ('SWPS-UNIT-CALLTAKE','SWPS-DIV-COMMS','Call Taking Unit','CTU','Receive and assess public communications.','Emergency and non-emergency call intake and contact records.'),
 ('SWPS-UNIT-DISPATCH','SWPS-DIV-COMMS','CAD and Dispatch Unit','CDU','Coordinate dispatch and unit communications.','CAD event management, dispatch selection and status coordination.'),
 ('SWPS-UNIT-RADIO','SWPS-DIV-COMMS','Radio Operations Unit','ROU','Maintain operational radio coordination.','Radio messages, channel discipline and communications handover.'),
 ('SWPS-UNIT-GENINV','SWPS-DIV-INV','General Investigations Unit','GIU','Investigate general criminal matters.','General investigation and case referrals.'),
 ('SWPS-UNIT-MAJOR','SWPS-DIV-INV','Major Crime Unit','MCU','Investigate serious and complex crime.','Major crime investigations and specialist coordination.'),
 ('SWPS-UNIT-FINCRIME','SWPS-DIV-INV','Financial and Economic Crime Unit','FECU','Investigate financial and economic offences.','Fraud, corruption, financial and corporate crime.'),
 ('SWPS-UNIT-CYBER','SWPS-DIV-INV','Cybercrime Unit','CCU','Investigate cyber-enabled and digital crime.','Cybercrime and digital investigative coordination.'),
 ('SWPS-UNIT-MARITIME','SWPS-DIV-INV','Maritime and Cargo Crime Unit','MCCU','Investigate port, shipping and cargo crime.','Cargo theft, shipping fraud and maritime crime.'),
 ('SWPS-UNIT-CRIMEAN','SWPS-DIV-INTEL','Crime Analysis Unit','CAU','Provide analytical support from authorised records.','Demand analysis, pattern analysis and performance intelligence.'),
 ('SWPS-UNIT-INTELDEV','SWPS-DIV-INTEL','Intelligence Development Unit','IDU','Develop and assess intelligence reports.','Source grading, intelligence development and dissemination.'),
 ('SWPS-UNIT-THREAT','SWPS-DIV-INTEL','Threat Assessment Unit','TAU','Assess operational threats and emerging risks.','Threat assessment and strategic risk support.'),
 ('SWPS-UNIT-TACTICAL','SWPS-DIV-SPEC','Tactical Response Unit','TRU','Provide specialist response support.','Tactical response under authorised command and qualification.'),
 ('SWPS-UNIT-SCENES','SWPS-DIV-SPEC','Scenes and Forensic Liaison Unit','SFLU','Coordinate specialist scene and forensic interfaces.','Scene support and forensic referral; no ownership of evidence custody.'),
 ('SWPS-UNIT-SAFE','SWPS-DIV-PROTECT','Safeguarding Unit','SGU','Coordinate safeguarding and vulnerable-person referrals.','Safeguarding and public protection.'),
 ('SWPS-UNIT-MISSING','SWPS-DIV-PROTECT','Missing Persons Unit','MPU','Coordinate missing-person response.','Missing-person reports, search coordination and welfare links.'),
 ('SWPS-UNIT-COMPLAINTS','SWPS-DIV-PS','Complaints Unit','CPU','Receive and triage complaints.','Complaints intake and assessment.'),
 ('SWPS-UNIT-INTERNAL','SWPS-DIV-PS','Internal Investigations Unit','IIU','Investigate internal misconduct allegations.','Internal investigations and referral.'),
 ('SWPS-UNIT-INTEGRITY','SWPS-DIV-PS','Integrity and Anti-Corruption Unit','IACU','Protect institutional integrity.','Anti-corruption and integrity intelligence.'),
 ('SWPS-UNIT-RECRUIT','SWPS-DIV-PEOPLE','Recruitment and Personnel Unit','RPU','Administer recruitment and personnel services.','Recruitment, personnel administration and service records.'),
 ('SWPS-UNIT-ACADEMY','SWPS-DIV-PEOPLE','Academy and Development Unit','ADU','Deliver police learning and development.','Recruit training, qualifications and professional development.'),
 ('SWPS-UNIT-FLEET','SWPS-DIV-RES','Fleet and Equipment Unit','FEU','Manage fleet and operational equipment.','Fleet readiness, equipment custody and serviceability.'),
 ('SWPS-UNIT-IT','SWPS-DIV-RES','Information Technology and Communications Unit','ITCU','Maintain digital and communications capability.','IT, CAD infrastructure, radio and secure communications support.'),
 ('SWPS-UNIT-LOGISTICS','SWPS-DIV-RES','Logistics Unit','LU','Coordinate logistics and supply.','Stores, supply, facilities and operational logistics.'),
 ('SWPS-UNIT-CUSTODY','SWPS-DIV-LEGAL','Custody Management Unit','CMU','Coordinate detainee custody services.','Custody interfaces and detainee management.'),
 ('SWPS-UNIT-LEGAL','SWPS-DIV-LEGAL','Legal Process and Court Liaison Unit','LPCLU','Coordinate legal process and court interfaces.','Legal process, prosecution liaison and court administration.'),
 ('SWPS-UNIT-RECORDS','SWPS-DIV-RECORDS','Records Management Unit','RMU','Maintain authoritative police records.','Records governance, access and retention interfaces.'),
 ('SWPS-UNIT-PERF','SWPS-DIV-RECORDS','Performance and Assurance Unit','PAU','Monitor performance and institutional assurance.','Performance reporting, inspection and quality assurance.')
)
INSERT INTO sw_police.organisation_component_version
(component_id,version_no,structure_version_id,parent_component_id,official_name,abbreviation,mission,functional_remit,geographic_scope,activation_status,effective_from_tick,source_ref)
SELECT component_id,1,'SWPS-ORG-V1',parent_component_id,official_name,abbreviation,mission,functional_remit,
       'SALTWATER_CITY_STATE','active',0,'saltwater-fictional-canon'
FROM components;

INSERT INTO sw_police.reporting_relationship
(relationship_id,from_component_id,to_component_id,relationship_type,effective_from_tick,source_ref)
SELECT 'SWPS-REL-'||component_id,component_id,parent_component_id,
       CASE WHEN child.component_type='command' THEN 'command' ELSE 'administrative' END,
       0,'saltwater-fictional-canon'
FROM sw_police.organisation_component_version v
JOIN sw_police.organisation_component child USING(component_id)
WHERE parent_component_id IS NOT NULL;

INSERT INTO sw_police.rank_definition(rank_code,rank_title,rank_order,rank_group,description,source_ref) VALUES
('CONSTABLE','Constable',1,'constable','Entry substantive sworn rank; does not by itself confer every specialist authority.','SWPS-ORG-V1'),
('SERGEANT','Sergeant',2,'supervisory','First-line supervisory rank; command scope remains position/delegation dependent.','SWPS-ORG-V1'),
('INSPECTOR','Inspector',3,'management','Operational management rank; command scope remains position/delegation dependent.','SWPS-ORG-V1'),
('CHIEF_INSPECTOR','Chief Inspector',4,'management','Senior divisional or branch management rank.','SWPS-ORG-V1'),
('SUPERINTENDENT','Superintendent',5,'management','Senior command rank.','SWPS-ORG-V1'),
('CHIEF_SUPERINTENDENT','Chief Superintendent',6,'management','Senior command portfolio rank.','SWPS-ORG-V1'),
('ASSISTANT_CHIEF','Assistant Chief',7,'executive','Executive rank; authority remains delegated and scoped.','SWPS-ORG-V1'),
('DEPUTY_CHIEF','Deputy Chief',8,'executive','Deputy service executive.','SWPS-ORG-V1'),
('CHIEF_OF_POLICE','Chief of Police',9,'executive','Head of Saltwater Police Service.','SWPS-ORG-V1');

WITH positions(position_id,position_code,component_id,position_title,position_type,purpose,command_scope,min_rank,max_rank,post_count) AS (
 VALUES
 ('SWPS-POS-CHIEF','CHIEF_OF_POLICE','SWPS-DIV-EXEC','Chief of Police','sworn','Lead the Saltwater Police Service.','Service-wide executive command',9,9,1),
 ('SWPS-POS-DEPUTY','DEPUTY_CHIEF','SWPS-DIV-EXEC','Deputy Chief','sworn','Support service-wide executive leadership.','Service-wide delegated command',8,8,1),
 ('SWPS-POS-ASSTCHIEF','ASSISTANT_CHIEF','SWPS-DIV-EXEC','Assistant Chief','sworn','Lead an executive portfolio.','Portfolio command',7,7,2),
 ('SWPS-POS-COMMANDER','COMMANDER','SWPS-CMD-OPS','Command Portfolio Commander','sworn','Lead an operational command portfolio.','Command portfolio',6,8,4),
 ('SWPS-POS-DIVDIRECTOR','DIVISION_DIRECTOR','SWPS-DIV-UNIFORM','Division Director','sworn','Lead a functional division.','Division command',5,8,12),
 ('SWPS-POS-BRANCHHEAD','BRANCH_HEAD','SWPS-DIV-INV','Branch Head','sworn','Lead a branch or specialist function.','Branch command',4,7,20),
 ('SWPS-POS-UNITSUP','UNIT_SUPERVISOR','SWPS-UNIT-PATROL','Unit Supervisor','sworn','Supervise a unit or operational team.','Unit supervision',2,6,45),
 ('SWPS-POS-PATROL','PATROL_OFFICER','SWPS-UNIT-PATROL','Patrol Officer','sworn','Conduct uniformed patrol and first response.','Field operations',1,4,150),
 ('SWPS-POS-TRAFFIC','TRAFFIC_OFFICER','SWPS-UNIT-TRAFFIC','Traffic Officer','sworn','Conduct traffic and road policing.','Traffic operations',1,4,20),
 ('SWPS-POS-PORT','PORT_OFFICER','SWPS-UNIT-PORT','Port and Maritime Officer','sworn','Police port and maritime environments.','Port and maritime operations',1,4,15),
 ('SWPS-POS-PUBLICORDER','PUBLIC_ORDER_OFFICER','SWPS-UNIT-PUBLICORDER','Public Order Officer','sworn','Support public order and event operations.','Public order operations',1,4,15),
 ('SWPS-POS-CALLHANDLER','CALL_HANDLER','SWPS-UNIT-CALLTAKE','Emergency Call Handler','civilian','Receive and assess public contacts.','Communications intake',NULL,NULL,20),
 ('SWPS-POS-DISPATCHER','DISPATCHER','SWPS-UNIT-DISPATCH','Dispatcher','civilian','Coordinate CAD allocation and dispatch.','Dispatch operations',NULL,NULL,20),
 ('SWPS-POS-INVESTIGATOR','INVESTIGATOR','SWPS-UNIT-GENINV','Investigator','sworn','Conduct authorised criminal investigations.','Investigations',1,5,48),
 ('SWPS-POS-SENIORINV','SENIOR_INVESTIGATOR','SWPS-UNIT-MAJOR','Senior Investigator','sworn','Lead complex investigations and teams.','Major investigations',3,6,20),
 ('SWPS-POS-ANALYST','INTELLIGENCE_ANALYST','SWPS-UNIT-CRIMEAN','Intelligence Analyst','civilian','Analyse authorised operational information.','Analysis and intelligence',NULL,NULL,25),
 ('SWPS-POS-SPECIALIST','SPECIALIST_OFFICER','SWPS-UNIT-TACTICAL','Specialist Officer','sworn','Perform qualified specialist operational duties.','Specialist operations',2,6,15),
 ('SWPS-POS-SAFEGUARD','SAFEGUARDING_OFFICER','SWPS-UNIT-SAFE','Safeguarding Officer','mixed','Coordinate safeguarding response and referrals.','Public protection',1,4,20),
 ('SWPS-POS-STANDARDS','PROFESSIONAL_STANDARDS_OFFICER','SWPS-UNIT-INTERNAL','Professional Standards Officer','sworn','Conduct authorised internal standards work.','Professional standards',2,6,10),
 ('SWPS-POS-RECRUIT','RECRUITMENT_OFFICER','SWPS-UNIT-RECRUIT','Recruitment Officer','civilian','Administer recruitment and personnel processes.','People services',NULL,NULL,5),
 ('SWPS-POS-TRAINING','TRAINING_OFFICER','SWPS-UNIT-ACADEMY','Training Officer','mixed','Deliver and assess police training.','Training and development',1,5,10),
 ('SWPS-POS-RESOURCE','RESOURCE_OFFICER','SWPS-UNIT-FLEET','Resource Officer','civilian','Manage fleet and equipment readiness.','Resource services',NULL,NULL,7),
 ('SWPS-POS-CUSTODY','CUSTODY_OFFICER','SWPS-UNIT-CUSTODY','Custody Officer','mixed','Coordinate custody operations under authority.','Custody services',1,4,10),
 ('SWPS-POS-RECORDS','RECORDS_OFFICER','SWPS-UNIT-RECORDS','Records Officer','civilian','Maintain police records and access controls.','Records management',NULL,NULL,5)
)
INSERT INTO sw_police.position_definition
(position_id,position_code,component_id,position_title,position_type,purpose,command_scope,minimum_rank_order,maximum_rank_order,source_ref)
SELECT position_id,position_code,component_id,position_title,position_type,purpose,command_scope,min_rank,max_rank,'SWPS-ORG-V1'
FROM positions;

WITH positions(position_id,post_count) AS (
 VALUES
 ('SWPS-POS-CHIEF',1),('SWPS-POS-DEPUTY',1),('SWPS-POS-ASSTCHIEF',2),('SWPS-POS-COMMANDER',4),
 ('SWPS-POS-DIVDIRECTOR',12),('SWPS-POS-BRANCHHEAD',20),('SWPS-POS-UNITSUP',45),
 ('SWPS-POS-PATROL',150),('SWPS-POS-TRAFFIC',20),('SWPS-POS-PORT',15),('SWPS-POS-PUBLICORDER',15),
 ('SWPS-POS-CALLHANDLER',20),('SWPS-POS-DISPATCHER',20),('SWPS-POS-INVESTIGATOR',48),
 ('SWPS-POS-SENIORINV',20),('SWPS-POS-ANALYST',25),('SWPS-POS-SPECIALIST',15),
 ('SWPS-POS-SAFEGUARD',20),('SWPS-POS-STANDARDS',10),('SWPS-POS-RECRUIT',5),
 ('SWPS-POS-TRAINING',10),('SWPS-POS-RESOURCE',7),('SWPS-POS-CUSTODY',10),('SWPS-POS-RECORDS',5)
)
INSERT INTO sw_police.authorised_post(post_id,post_code,position_id,slot_no,post_status,authorised_tick,source_ref)
SELECT 'SWPS-POST-'||p.position_id||'-'||lpad(g.slot_no::text,3,'0'),
       'POST-'||p.position_id||'-'||lpad(g.slot_no::text,3,'0'),
       p.position_id,g.slot_no,'vacant',0,'SWPS-ORG-V1'
FROM positions p CROSS JOIN LATERAL generate_series(1,p.post_count) AS g(slot_no);

INSERT INTO sw_police.authorised_post_event(post_id,event_code,prior_status,new_status,effective_tick,source_ref,actor_ref,reason)
SELECT post_id,'authorised',NULL,'vacant',0,'SWPS-ORG-V1','system:structure-seed','Initial authorised establishment slot'
FROM sw_police.authorised_post;

COMMIT;
