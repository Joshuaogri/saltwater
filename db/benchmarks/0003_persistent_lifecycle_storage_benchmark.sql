\set ON_ERROR_STOP on
\timing on
-- Persistent isolated benchmark schema. Workflow drops sw_bench_run after measurements.
CREATE SCHEMA sw_bench_run;
SET search_path TO sw_bench_run, public;
\echo BENCHMARK_0003_BUILD_BEGIN
\set ON_ERROR_STOP on
\timing on

-- Persistent isolated benchmark schema; objects are dropped by the workflow after measurement.
-- All values are synthetic. No production simulation records are inserted.
CREATE TABLE pbench_person (
  person_id integer PRIMARY KEY,
  given_name text NOT NULL,
  family_name text NOT NULL,
  date_of_birth date NOT NULL,
  biography text NOT NULL,
  home_address text NOT NULL,
  status_code smallint NOT NULL
);

INSERT INTO pbench_person
SELECT g,
       'Given' || (g % 97),
       'Family' || (g % 389),
       date '1960-01-01' + (g % 18000),
       'Synthetic resident biography. Employment, household, education, social ties and personal history are represented through linked records. Resident reference ' || g || '.',
       'District ' || (g % 12) || ', Street ' || (g % 740) || ', Building ' || (g % 4200),
       (g % 4)::smallint
FROM generate_series(1, 10000) AS g;

CREATE INDEX pbench_person_address_idx ON pbench_person(home_address);

CREATE TABLE pbench_business (
  business_id integer PRIMARY KEY,
  legal_name text NOT NULL,
  business_type smallint NOT NULL,
  premises_address text NOT NULL,
  description text NOT NULL,
  owner_person_id integer NOT NULL REFERENCES pbench_person(person_id),
  employee_count smallint NOT NULL
);

INSERT INTO pbench_business
SELECT g,
       'Saltwater Enterprise ' || g,
       (g % 35)::smallint,
       'District ' || (g % 12) || ', Commercial Road ' || (g % 900) || ', Unit ' || g,
       'Synthetic business profile covering activity, trading pattern, premises, ownership and operating context. Business reference ' || g || '.',
       ((g - 1) % 10000) + 1,
       (g % 45)::smallint
FROM generate_series(1, 10000) AS g;

CREATE INDEX pbench_business_address_idx ON pbench_business(premises_address);
CREATE INDEX pbench_business_owner_idx ON pbench_business(owner_person_id);

CREATE TABLE pbench_relationship (
  relationship_id integer PRIMARY KEY,
  person_a integer NOT NULL REFERENCES pbench_person(person_id),
  person_b integer NOT NULL REFERENCES pbench_person(person_id),
  relationship_type smallint NOT NULL,
  valid_from date NOT NULL,
  notes text NOT NULL
);

INSERT INTO pbench_relationship
SELECT g,
       ((g - 1) % 10000) + 1,
       ((g * 37) % 10000) + 1,
       (g % 18)::smallint,
       date '2010-01-01' + (g % 5000),
       'Synthetic relationship history and context reference ' || g
FROM generate_series(1, 30000) AS g;

CREATE INDEX pbench_relationship_a_idx ON pbench_relationship(person_a);
CREATE INDEX pbench_relationship_b_idx ON pbench_relationship(person_b);

CREATE TABLE pbench_employment (
  employment_id integer PRIMARY KEY,
  person_id integer NOT NULL REFERENCES pbench_person(person_id),
  business_id integer NOT NULL REFERENCES pbench_business(business_id),
  role_name text NOT NULL,
  started_on date NOT NULL,
  ended_on date
);

INSERT INTO pbench_employment
SELECT g,
       ((g - 1) % 10000) + 1,
       ((g * 13 - 1) % 10000) + 1,
       'Position ' || (g % 120),
       date '2015-01-01' + (g % 3000),
       CASE WHEN g % 3 = 0 THEN date '2022-01-01' + (g % 1000) ELSE NULL END
FROM generate_series(1, 20000) AS g;

CREATE INDEX pbench_employment_person_idx ON pbench_employment(person_id);
CREATE INDEX pbench_employment_business_idx ON pbench_employment(business_id);

CREATE TABLE pbench_case (
  case_id integer PRIMARY KEY,
  case_number text NOT NULL UNIQUE,
  opened_at timestamptz NOT NULL,
  offence_code smallint NOT NULL,
  summary text NOT NULL,
  status_code smallint NOT NULL
);

INSERT INTO pbench_case
SELECT g,
       'SW-BENCH-' || lpad(g::text, 7, '0'),
       timestamptz '2020-01-01 00:00:00+00' + g * interval '3 hours',
       (g % 90)::smallint,
       'Synthetic case summary with reported circumstances, initial assessment, investigative context and linked subject references. Case ' || g || '.',
       (g % 6)::smallint
FROM generate_series(1, 2000) AS g;

CREATE INDEX pbench_case_opened_idx ON pbench_case(opened_at);

CREATE TABLE pbench_incident (
  incident_id integer PRIMARY KEY,
  occurred_at timestamptz NOT NULL,
  location_text text NOT NULL,
  incident_type smallint NOT NULL,
  narrative text NOT NULL,
  linked_case_id integer REFERENCES pbench_case(case_id)
);

INSERT INTO pbench_incident
SELECT g,
       timestamptz '2021-01-01 00:00:00+00' + g * interval '90 minutes',
       'District ' || (g % 12) || ', Street ' || (g % 740),
       (g % 110)::smallint,
       'Synthetic incident narrative recording call details, attendance, observations, actions, persons present and outcome. Incident ' || g || '.',
       CASE WHEN g % 5 = 0 THEN ((g - 1) % 2000) + 1 ELSE NULL END
FROM generate_series(1, 10000) AS g;

CREATE INDEX pbench_incident_time_idx ON pbench_incident(occurred_at);
CREATE INDEX pbench_incident_case_idx ON pbench_incident(linked_case_id);

CREATE TABLE pbench_evidence (
  evidence_id integer PRIMARY KEY,
  case_id integer NOT NULL REFERENCES pbench_case(case_id),
  evidence_type smallint NOT NULL,
  description text NOT NULL,
  collected_at timestamptz NOT NULL,
  integrity_sha256 char(64) NOT NULL,
  custody_event_count smallint NOT NULL
);

INSERT INTO pbench_evidence
SELECT g,
       ((g - 1) % 2000) + 1,
       (g % 40)::smallint,
       'Synthetic evidence metadata, exhibit description, recovery location, packaging and examination requirements. Exhibit ' || g || '.',
       timestamptz '2022-01-01 00:00:00+00' + g * interval '25 minutes',
       md5('saltwater-benchmark-evidence-' || g) || md5('saltwater-benchmark-integrity-' || g),
       (g % 12)::smallint
FROM generate_series(1, 10000) AS g;

CREATE INDEX pbench_evidence_case_idx ON pbench_evidence(case_id);
CREATE INDEX pbench_evidence_collected_idx ON pbench_evidence(collected_at);

CREATE TABLE pbench_event (
  event_id bigint PRIMARY KEY,
  occurred_at timestamptz NOT NULL,
  event_type smallint NOT NULL,
  subject_person_id integer REFERENCES pbench_person(person_id),
  location_text text NOT NULL,
  event_summary text NOT NULL,
  attributes jsonb NOT NULL
);

INSERT INTO pbench_event
SELECT g,
       timestamptz '2018-01-01 00:00:00+00' + g * interval '12 minutes',
       (g % 180)::smallint,
       CASE WHEN g % 4 = 0 THEN ((g - 1) % 10000) + 1 ELSE NULL END,
       'District ' || (g % 12) || ', location ' || (g % 1600),
       'Synthetic longitudinal simulation event with timestamp, actor, subject, location, reason and recorded outcome. Event ' || g || '.',
       jsonb_build_object('source', 'synthetic-benchmark', 'sequence', g, 'severity', g % 5, 'resolved', (g % 2 = 0))
FROM generate_series(1, 150000) AS g;

CREATE INDEX pbench_event_time_idx ON pbench_event(occurred_at);
CREATE INDEX pbench_event_subject_idx ON pbench_event(subject_person_id);

ANALYZE pbench_person;
ANALYZE pbench_business;
ANALYZE pbench_relationship;
ANALYZE pbench_employment;
ANALYZE pbench_case;
ANALYZE pbench_incident;
ANALYZE pbench_evidence;
ANALYZE pbench_event;

\echo BENCHMARK_ROW_COUNTS
SELECT 'residents=' || count(*) FROM pbench_person
UNION ALL SELECT 'businesses=' || count(*) FROM pbench_business
UNION ALL SELECT 'relationships=' || count(*) FROM pbench_relationship
UNION ALL SELECT 'employment_records=' || count(*) FROM pbench_employment
UNION ALL SELECT 'cases=' || count(*) FROM pbench_case
UNION ALL SELECT 'incidents=' || count(*) FROM pbench_incident
UNION ALL SELECT 'evidence_metadata=' || count(*) FROM pbench_evidence
UNION ALL SELECT 'historical_events=' || count(*) FROM pbench_event;

\echo BENCHMARK_STORAGE_BY_TABLE
SELECT relname AS table_name,
       pg_relation_size(relid) AS heap_bytes,
       pg_indexes_size(relid) AS index_bytes,
       pg_total_relation_size(relid) AS total_bytes,
       round(pg_total_relation_size(relid)::numeric / 1000000, 3) AS total_mb
FROM pg_catalog.pg_statio_user_tables
WHERE schemaname = 'sw_bench_run'
  AND relname LIKE 'pbench_%'
ORDER BY pg_total_relation_size(relid) DESC;

\echo BENCHMARK_TOTAL
SELECT sum(pg_total_relation_size(relid)) AS total_relation_bytes,
       round(sum(pg_total_relation_size(relid))::numeric / 1000000, 3) AS total_relation_mb,
       sum(pg_relation_size(relid)) AS total_heap_bytes,
       sum(pg_indexes_size(relid)) AS total_index_bytes
FROM pg_catalog.pg_statio_user_tables
WHERE schemaname = 'sw_bench_run'
  AND relname LIKE 'pbench_%';

\echo BENCHMARK_0003_PERSISTENT_DATA_MEASURED

\set ON_ERROR_STOP on
\timing on

-- Saltwater benchmark 0002: additional city, institutional, police and justice systems.
-- All rows are synthetic and isolated in the disposable sw_bench_run schema.

CREATE TABLE pbench_district AS
SELECT g::smallint AS district_id, 'District ' || g AS district_name,
       'Synthetic district profile and service-area description ' || g AS description
FROM generate_series(1,12) g;
ALTER TABLE pbench_district ADD PRIMARY KEY (district_id);

CREATE TABLE pbench_street AS
SELECT g AS street_id, ((g-1)%12+1)::smallint AS district_id,
       'Street ' || g AS street_name, (g%5)::smallint AS street_class
FROM generate_series(1,800) g;
ALTER TABLE pbench_street ADD PRIMARY KEY (street_id);
CREATE INDEX pbench_street_district_idx ON pbench_street(district_id);

CREATE TABLE pbench_junction AS
SELECT g AS junction_id, ((g-1)%800+1) AS street_a,
       ((g*17-1)%800+1) AS street_b,
       'Junction ' || g || ' / ' || (g%800) AS junction_name
FROM generate_series(1,2500) g;
ALTER TABLE pbench_junction ADD PRIMARY KEY (junction_id);
CREATE INDEX pbench_junction_street_a_idx ON pbench_junction(street_a);

CREATE TABLE pbench_building AS
SELECT g AS building_id, ((g-1)%800+1) AS street_id,
       ((g-1)%12+1)::smallint AS district_id,
       'Building ' || g || ', Street ' || ((g-1)%800+1) AS postal_address,
       (g%14)::smallint AS building_type,
       'Synthetic building, access, occupancy, floor and use profile. Reference ' || g AS building_description
FROM generate_series(1,6000) g;
ALTER TABLE pbench_building ADD PRIMARY KEY (building_id);
CREATE INDEX pbench_building_street_idx ON pbench_building(street_id);
CREATE INDEX pbench_building_district_idx ON pbench_building(district_id);

CREATE TABLE pbench_property_history AS
SELECT g AS history_id, ((g-1)%6000+1) AS building_id,
       (date '2000-01-01' + (g%9000)) AS effective_date,
       (g%9)::smallint AS tenure_code,
       'Synthetic ownership, lease, occupancy and property-use change ' || g AS change_note
FROM generate_series(1,30000) g;
ALTER TABLE pbench_property_history ADD PRIMARY KEY (history_id);
CREATE INDEX pbench_property_history_building_idx ON pbench_property_history(building_id);

CREATE TABLE pbench_organisation AS
SELECT g AS organisation_id, 'Saltwater Institution ' || g AS organisation_name,
       (g%24)::smallint AS institution_type,
       'Synthetic remit, authority, service and organisational profile ' || g AS remit
FROM generate_series(1,80) g;
ALTER TABLE pbench_organisation ADD PRIMARY KEY (organisation_id);

CREATE TABLE pbench_institutional_staff AS
SELECT g AS staff_id, ((g-1)%80+1) AS organisation_id,
       ((g-1)%10000+1) AS person_id,
       'Institutional post ' || (g%90) AS position_title,
       date '2010-01-01' + (g%5000) AS appointed_on,
       'Synthetic appointment, grade and posting history ' || g AS personnel_note
FROM generate_series(1,1200) g;
ALTER TABLE pbench_institutional_staff ADD PRIMARY KEY (staff_id);
CREATE INDEX pbench_inst_staff_org_idx ON pbench_institutional_staff(organisation_id);
CREATE INDEX pbench_inst_staff_person_idx ON pbench_institutional_staff(person_id);

CREATE TABLE pbench_police_personnel AS
SELECT g AS officer_id, 'SWP-' || lpad(g::text,5,'0') AS service_number,
       'Officer ' || g AS display_name,
       (g%18)::smallint AS rank_code, (g%26)::smallint AS unit_code,
       date '2000-01-01' + (g%8000) AS service_start,
       'Synthetic recruitment, training, posting and career record ' || g AS career_note
FROM generate_series(1,250) g;
ALTER TABLE pbench_police_personnel ADD PRIMARY KEY (officer_id);
CREATE UNIQUE INDEX pbench_police_service_no_idx ON pbench_police_personnel(service_number);
CREATE INDEX pbench_police_unit_idx ON pbench_police_personnel(unit_code);

CREATE TABLE pbench_duty_shift AS
SELECT g AS shift_id, ((g-1)%250+1) AS officer_id,
       timestamptz '2020-01-01 00:00:00+00' + g*interval '8 hours' AS shift_start,
       (g%12+1)::smallint AS district_id,
       (g%4)::smallint AS duty_type,
       'Synthetic deployment, supervisor and duty outcome ' || g AS shift_note
FROM generate_series(1,100000) g;
ALTER TABLE pbench_duty_shift ADD PRIMARY KEY (shift_id);
CREATE INDEX pbench_shift_officer_time_idx ON pbench_duty_shift(officer_id,shift_start);
CREATE INDEX pbench_shift_district_idx ON pbench_duty_shift(district_id);

CREATE TABLE pbench_call AS
SELECT g AS call_id, timestamptz '2020-01-01 00:00:00+00' + g*interval '7 minutes' AS received_at,
       (g%110)::smallint AS call_type,
       ((g-1)%6000+1) AS building_id,
       (g%5)::smallint AS priority,
       'Synthetic caller account, call-taking details and risk assessment narrative ' || g AS call_narrative
FROM generate_series(1,100000) g;
ALTER TABLE pbench_call ADD PRIMARY KEY (call_id);
CREATE INDEX pbench_call_received_idx ON pbench_call(received_at);
CREATE INDEX pbench_call_building_idx ON pbench_call(building_id);

CREATE TABLE pbench_dispatch_action AS
SELECT g AS action_id, ((g-1)%100000+1) AS call_id,
       ((g-1)%250+1) AS officer_id,
       timestamptz '2020-01-01 00:00:00+00' + g*interval '4 minutes' AS action_at,
       (g%16)::smallint AS action_code,
       'Synthetic CAD status, radio traffic reference and dispatch note ' || g AS action_note
FROM generate_series(1,200000) g;
ALTER TABLE pbench_dispatch_action ADD PRIMARY KEY (action_id);
CREATE INDEX pbench_dispatch_call_idx ON pbench_dispatch_action(call_id);
CREATE INDEX pbench_dispatch_officer_time_idx ON pbench_dispatch_action(officer_id,action_at);

CREATE TABLE pbench_patrol_event AS
SELECT g AS patrol_event_id, ((g-1)%250+1) AS officer_id,
       timestamptz '2020-01-01 00:00:00+00' + g*interval '5 minutes' AS occurred_at,
       ((g-1)%6000+1) AS building_id,
       (g%30)::smallint AS activity_code,
       'Synthetic patrol observation, route, contact or intervention ' || g AS narrative
FROM generate_series(1,150000) g;
ALTER TABLE pbench_patrol_event ADD PRIMARY KEY (patrol_event_id);
CREATE INDEX pbench_patrol_officer_time_idx ON pbench_patrol_event(officer_id,occurred_at);
CREATE INDEX pbench_patrol_building_idx ON pbench_patrol_event(building_id);

CREATE TABLE pbench_police_report AS
SELECT g AS report_id, ((g-1)%100000+1) AS call_id,
       ((g-1)%250+1) AS reporting_officer,
       timestamptz '2020-01-01 00:00:00+00' + g*interval '2 hours' AS submitted_at,
       'Synthetic report with circumstances, actions, statements, observations and outcome. Report ' || g ||
       '. ' || repeat('Detailed narrative content for measured report text length. ', 8) AS report_body
FROM generate_series(1,60000) g;
ALTER TABLE pbench_police_report ADD PRIMARY KEY (report_id);
CREATE INDEX pbench_report_call_idx ON pbench_police_report(call_id);
CREATE INDEX pbench_report_officer_idx ON pbench_police_report(reporting_officer);

CREATE TABLE pbench_interview AS
SELECT g AS interview_id, ((g-1)%2000+1) AS case_id,
       ((g-1)%10000+1) AS person_id,
       ((g-1)%250+1) AS interviewing_officer,
       timestamptz '2021-01-01 00:00:00+00' + g*interval '3 hours' AS interview_at,
       (g%8)::smallint AS interview_type,
       'Synthetic interview record. ' || repeat('Question, answer, clarification, account detail and evidential context. ', 18) AS transcript_text
FROM generate_series(1,30000) g;
ALTER TABLE pbench_interview ADD PRIMARY KEY (interview_id);
CREATE INDEX pbench_interview_case_idx ON pbench_interview(case_id);
CREATE INDEX pbench_interview_person_idx ON pbench_interview(person_id);

CREATE TABLE pbench_intelligence (
  intelligence_id integer PRIMARY KEY,
  created_at timestamptz NOT NULL,
  source_grade smallint NOT NULL,
  confidence_code smallint NOT NULL,
  narrative text NOT NULL,
  linked_person_id integer NOT NULL
);
INSERT INTO pbench_intelligence
SELECT g, timestamptz '2020-01-01 00:00:00+00'+g*interval '5 hours',
       (g%6)::smallint,(g%5)::smallint,
       'Synthetic intelligence report. ' || repeat('Source evaluation, corroboration, reliability, handling caveat and analytical assessment. ', 12),
       ((g-1)%10000+1)
FROM generate_series(1,20000) g;
CREATE INDEX pbench_intel_person_idx ON pbench_intelligence(linked_person_id);
CREATE INDEX pbench_intel_time_idx ON pbench_intelligence(created_at);

CREATE TABLE pbench_surveillance AS
SELECT g AS surveillance_id, ((g-1)%2000+1) AS case_id,
       ((g-1)%6000+1) AS building_id,
       timestamptz '2022-01-01 00:00:00+00'+g*interval '2 hours' AS started_at,
       (g%6)::smallint AS method_code,
       'Synthetic authority, deployment, observation and result record ' || g AS observation_summary
FROM generate_series(1,10000) g;
ALTER TABLE pbench_surveillance ADD PRIMARY KEY (surveillance_id);
CREATE INDEX pbench_surveillance_case_idx ON pbench_surveillance(case_id);
CREATE INDEX pbench_surveillance_building_idx ON pbench_surveillance(building_id);

CREATE TABLE pbench_warrant AS
SELECT g AS warrant_id, ((g-1)%2000+1) AS case_id,
       ((g-1)%10000+1) AS subject_person_id,
       date '2020-01-01'+(g%2000) AS issued_on,
       (g%12)::smallint AS warrant_type,
       'Synthetic application grounds, scope, execution and return record ' || g AS warrant_detail
FROM generate_series(1,8000) g;
ALTER TABLE pbench_warrant ADD PRIMARY KEY (warrant_id);
CREATE INDEX pbench_warrant_case_idx ON pbench_warrant(case_id);
CREATE INDEX pbench_warrant_subject_idx ON pbench_warrant(subject_person_id);

CREATE TABLE pbench_arrest AS
SELECT g AS arrest_id, ((g-1)%2000+1) AS case_id,
       ((g-1)%10000+1) AS person_id,
       ((g-1)%250+1) AS arresting_officer,
       timestamptz '2020-01-01 00:00:00+00'+g*interval '6 hours' AS arrested_at,
       'Synthetic grounds, caution, search, property and arrest circumstances ' || g AS arrest_record
FROM generate_series(1,12000) g;
ALTER TABLE pbench_arrest ADD PRIMARY KEY (arrest_id);
CREATE INDEX pbench_arrest_case_idx ON pbench_arrest(case_id);
CREATE INDEX pbench_arrest_person_idx ON pbench_arrest(person_id);

CREATE TABLE pbench_custody AS
SELECT g AS custody_id, ((g-1)%12000+1) AS arrest_id,
       timestamptz '2020-01-01 00:00:00+00'+g*interval '6 hours' AS booked_at,
       (g%14)::smallint AS disposal_code,
       'Synthetic custody risk, rights, welfare, property and detention review ' || g AS custody_note
FROM generate_series(1,12000) g;
ALTER TABLE pbench_custody ADD PRIMARY KEY (custody_id);
CREATE INDEX pbench_custody_arrest_idx ON pbench_custody(arrest_id);

CREATE TABLE pbench_forensic_exam AS
SELECT g AS examination_id, ((g-1)%10000+1) AS evidence_id,
       ((g-1)%2000+1) AS case_id,
       timestamptz '2021-01-01 00:00:00+00'+g*interval '4 hours' AS examined_at,
       (g%35)::smallint AS discipline_code,
       'Synthetic forensic submission, method, observations, limitations and conclusion. ' ||
       repeat('Recorded analytical detail and quality assurance statement. ', 8) AS examination_result
FROM generate_series(1,20000) g;
ALTER TABLE pbench_forensic_exam ADD PRIMARY KEY (examination_id);
CREATE INDEX pbench_forensic_evidence_idx ON pbench_forensic_exam(evidence_id);
CREATE INDEX pbench_forensic_case_idx ON pbench_forensic_exam(case_id);

CREATE TABLE pbench_court_proceeding AS
SELECT g AS proceeding_id, ((g-1)%2000+1) AS case_id,
       timestamptz '2022-01-01 00:00:00+00'+g*interval '1 day' AS proceeding_at,
       (g%20)::smallint AS proceeding_type,
       'Synthetic filing, hearing, ruling, evidence and disposition summary ' || g AS proceeding_record
FROM generate_series(1,30000) g;
ALTER TABLE pbench_court_proceeding ADD PRIMARY KEY (proceeding_id);
CREATE INDEX pbench_court_case_idx ON pbench_court_proceeding(case_id);
CREATE INDEX pbench_court_date_idx ON pbench_court_proceeding(proceeding_at);

CREATE TABLE pbench_transaction AS
SELECT g AS transaction_id, ((g-1)%10000+1) AS business_id,
       timestamptz '2020-01-01 00:00:00+00'+g*interval '30 minutes' AS transacted_at,
       (g%40)::smallint AS transaction_type,
       ((g%500000)+100)::bigint AS amount_minor_units,
       'Synthetic commercial transaction reference ' || g AS transaction_reference
FROM generate_series(1,200000) g;
ALTER TABLE pbench_transaction ADD PRIMARY KEY (transaction_id);
CREATE INDEX pbench_transaction_business_time_idx ON pbench_transaction(business_id,transacted_at);

CREATE TABLE pbench_address_history AS
SELECT g AS address_history_id, ((g-1)%10000+1) AS person_id,
       ((g-1)%6000+1) AS building_id,
       date '2000-01-01'+(g%9000) AS valid_from,
       'Synthetic residence and address change history ' || g AS history_note
FROM generate_series(1,30000) g;
ALTER TABLE pbench_address_history ADD PRIMARY KEY (address_history_id);
CREATE INDEX pbench_address_person_idx ON pbench_address_history(person_id);
CREATE INDEX pbench_address_building_idx ON pbench_address_history(building_id);

CREATE TABLE pbench_household_membership AS
SELECT g AS membership_id, ((g-1)%2500+1) AS household_id,
       ((g-1)%10000+1) AS person_id,
       (g%12)::smallint AS household_role,
       date '2010-01-01'+(g%5000) AS joined_on
FROM generate_series(1,12000) g;
ALTER TABLE pbench_household_membership ADD PRIMARY KEY (membership_id);
CREATE INDEX pbench_household_id_idx ON pbench_household_membership(household_id);
CREATE INDEX pbench_household_person_idx ON pbench_household_membership(person_id);

ANALYZE;
\echo BENCHMARK_0002_ROW_COUNTS
SELECT 'districts='||count(*) FROM pbench_district
UNION ALL SELECT 'streets='||count(*) FROM pbench_street
UNION ALL SELECT 'junctions='||count(*) FROM pbench_junction
UNION ALL SELECT 'buildings='||count(*) FROM pbench_building
UNION ALL SELECT 'property_history='||count(*) FROM pbench_property_history
UNION ALL SELECT 'organisations='||count(*) FROM pbench_organisation
UNION ALL SELECT 'institutional_staff='||count(*) FROM pbench_institutional_staff
UNION ALL SELECT 'police_personnel='||count(*) FROM pbench_police_personnel
UNION ALL SELECT 'duty_shifts='||count(*) FROM pbench_duty_shift
UNION ALL SELECT 'calls='||count(*) FROM pbench_call
UNION ALL SELECT 'dispatch_actions='||count(*) FROM pbench_dispatch_action
UNION ALL SELECT 'patrol_events='||count(*) FROM pbench_patrol_event
UNION ALL SELECT 'police_reports='||count(*) FROM pbench_police_report
UNION ALL SELECT 'interviews='||count(*) FROM pbench_interview
UNION ALL SELECT 'intelligence_reports='||count(*) FROM pbench_intelligence
UNION ALL SELECT 'surveillance_sessions='||count(*) FROM pbench_surveillance
UNION ALL SELECT 'warrants='||count(*) FROM pbench_warrant
UNION ALL SELECT 'arrests='||count(*) FROM pbench_arrest
UNION ALL SELECT 'custody_records='||count(*) FROM pbench_custody
UNION ALL SELECT 'forensic_examinations='||count(*) FROM pbench_forensic_exam
UNION ALL SELECT 'court_proceedings='||count(*) FROM pbench_court_proceeding
UNION ALL SELECT 'commercial_transactions='||count(*) FROM pbench_transaction
UNION ALL SELECT 'address_history='||count(*) FROM pbench_address_history
UNION ALL SELECT 'household_memberships='||count(*) FROM pbench_household_membership;

\echo BENCHMARK_0002_STORAGE_BY_TABLE
SELECT relname,
       pg_relation_size(relid) AS heap_bytes,
       pg_indexes_size(relid) AS index_bytes,
       pg_total_relation_size(relid) AS total_bytes,
       round(pg_total_relation_size(relid)::numeric/1000000,3) AS total_mb
FROM pg_catalog.pg_statio_user_tables
WHERE schemaname = 'sw_bench_run' AND relname LIKE 'pbench_%'
ORDER BY pg_total_relation_size(relid) DESC;

\echo BENCHMARK_0002_TOTAL
SELECT count(*) AS table_count,
       sum(pg_relation_size(relid)) AS heap_bytes,
       sum(pg_indexes_size(relid)) AS index_bytes,
       sum(pg_total_relation_size(relid)) AS total_relation_bytes,
       round(sum(pg_total_relation_size(relid))::numeric/1000000,3) AS total_relation_mb
FROM pg_catalog.pg_statio_user_tables
WHERE schemaname = 'sw_bench_run' AND relname LIKE 'pbench_%';
\echo BENCHMARK_0002_PERSISTENT_TABLES_INCLUDED

\echo BENCHMARK_0003_ROW_COUNTS_AND_TABLES
SELECT schemaname, count(*) AS table_count,
       sum(n_live_tup)::bigint AS estimated_live_rows
FROM pg_stat_user_tables
WHERE schemaname = 'sw_bench_run'
GROUP BY schemaname;
\echo BENCHMARK_0003_STORAGE_BY_TABLE
SELECT relname AS table_name,
       pg_relation_size(relid) AS heap_bytes,
       pg_indexes_size(relid) AS index_bytes,
       (pg_total_relation_size(relid)-pg_relation_size(relid)-pg_indexes_size(relid)) AS toast_and_aux_bytes,
       pg_total_relation_size(relid) AS total_bytes,
       round(pg_total_relation_size(relid)::numeric/1000000,3) AS total_mb
FROM pg_catalog.pg_statio_user_tables
WHERE schemaname = 'sw_bench_run'
ORDER BY pg_total_relation_size(relid) DESC;
\echo BENCHMARK_0003_TOTAL
SELECT count(*) AS table_count,
       sum(pg_relation_size(relid)) AS heap_bytes,
       sum(pg_indexes_size(relid)) AS index_bytes,
       sum(pg_total_relation_size(relid)-pg_relation_size(relid)-pg_indexes_size(relid)) AS toast_and_aux_bytes,
       sum(pg_total_relation_size(relid)) AS total_relation_bytes,
       round(sum(pg_total_relation_size(relid))::numeric/1000000,3) AS total_relation_mb
FROM pg_catalog.pg_statio_user_tables
WHERE schemaname = 'sw_bench_run';
\echo BENCHMARK_0003_DATABASE_SIZE_WHILE_PERSISTENT
SELECT pg_database_size(current_database()) AS database_bytes,
       round(pg_database_size(current_database())::numeric/1000000,3) AS database_mb;
