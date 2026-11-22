\set ON_ERROR_STOP on
\timing on

-- Saltwater benchmark 0002: additional city, institutional, police and justice systems.
-- All rows are synthetic, temporary, and removed when this database session closes.

CREATE TEMP TABLE bench_district AS
SELECT g::smallint AS district_id, 'District ' || g AS district_name,
       'Synthetic district profile and service-area description ' || g AS description
FROM generate_series(1,12) g;
ALTER TABLE bench_district ADD PRIMARY KEY (district_id);

CREATE TEMP TABLE bench_street AS
SELECT g AS street_id, ((g-1)%12+1)::smallint AS district_id,
       'Street ' || g AS street_name, (g%5)::smallint AS street_class
FROM generate_series(1,800) g;
ALTER TABLE bench_street ADD PRIMARY KEY (street_id);
CREATE INDEX bench_street_district_idx ON bench_street(district_id);

CREATE TEMP TABLE bench_junction AS
SELECT g AS junction_id, ((g-1)%800+1) AS street_a,
       ((g*17-1)%800+1) AS street_b,
       'Junction ' || g || ' / ' || (g%800) AS junction_name
FROM generate_series(1,2500) g;
ALTER TABLE bench_junction ADD PRIMARY KEY (junction_id);
CREATE INDEX bench_junction_street_a_idx ON bench_junction(street_a);

CREATE TEMP TABLE bench_building AS
SELECT g AS building_id, ((g-1)%800+1) AS street_id,
       ((g-1)%12+1)::smallint AS district_id,
       'Building ' || g || ', Street ' || ((g-1)%800+1) AS postal_address,
       (g%14)::smallint AS building_type,
       'Synthetic building, access, occupancy, floor and use profile. Reference ' || g AS building_description
FROM generate_series(1,6000) g;
ALTER TABLE bench_building ADD PRIMARY KEY (building_id);
CREATE INDEX bench_building_street_idx ON bench_building(street_id);
CREATE INDEX bench_building_district_idx ON bench_building(district_id);

CREATE TEMP TABLE bench_property_history AS
SELECT g AS history_id, ((g-1)%6000+1) AS building_id,
       (date '2000-01-01' + (g%9000)) AS effective_date,
       (g%9)::smallint AS tenure_code,
       'Synthetic ownership, lease, occupancy and property-use change ' || g AS change_note
FROM generate_series(1,30000) g;
ALTER TABLE bench_property_history ADD PRIMARY KEY (history_id);
CREATE INDEX bench_property_history_building_idx ON bench_property_history(building_id);

CREATE TEMP TABLE bench_organisation AS
SELECT g AS organisation_id, 'Saltwater Institution ' || g AS organisation_name,
       (g%24)::smallint AS institution_type,
       'Synthetic remit, authority, service and organisational profile ' || g AS remit
FROM generate_series(1,80) g;
ALTER TABLE bench_organisation ADD PRIMARY KEY (organisation_id);

CREATE TEMP TABLE bench_institutional_staff AS
SELECT g AS staff_id, ((g-1)%80+1) AS organisation_id,
       ((g-1)%10000+1) AS person_id,
       'Institutional post ' || (g%90) AS position_title,
       date '2010-01-01' + (g%5000) AS appointed_on,
       'Synthetic appointment, grade and posting history ' || g AS personnel_note
FROM generate_series(1,1200) g;
ALTER TABLE bench_institutional_staff ADD PRIMARY KEY (staff_id);
CREATE INDEX bench_inst_staff_org_idx ON bench_institutional_staff(organisation_id);
CREATE INDEX bench_inst_staff_person_idx ON bench_institutional_staff(person_id);

CREATE TEMP TABLE bench_police_personnel AS
SELECT g AS officer_id, 'SWP-' || lpad(g::text,5,'0') AS service_number,
       'Officer ' || g AS display_name,
       (g%18)::smallint AS rank_code, (g%26)::smallint AS unit_code,
       date '2000-01-01' + (g%8000) AS service_start,
       'Synthetic recruitment, training, posting and career record ' || g AS career_note
FROM generate_series(1,250) g;
ALTER TABLE bench_police_personnel ADD PRIMARY KEY (officer_id);
CREATE UNIQUE INDEX bench_police_service_no_idx ON bench_police_personnel(service_number);
CREATE INDEX bench_police_unit_idx ON bench_police_personnel(unit_code);

CREATE TEMP TABLE bench_duty_shift AS
SELECT g AS shift_id, ((g-1)%250+1) AS officer_id,
       timestamptz '2020-01-01 00:00:00+00' + g*interval '8 hours' AS shift_start,
       (g%12+1)::smallint AS district_id,
       (g%4)::smallint AS duty_type,
       'Synthetic deployment, supervisor and duty outcome ' || g AS shift_note
FROM generate_series(1,100000) g;
ALTER TABLE bench_duty_shift ADD PRIMARY KEY (shift_id);
CREATE INDEX bench_shift_officer_time_idx ON bench_duty_shift(officer_id,shift_start);
CREATE INDEX bench_shift_district_idx ON bench_duty_shift(district_id);

CREATE TEMP TABLE bench_call AS
SELECT g AS call_id, timestamptz '2020-01-01 00:00:00+00' + g*interval '7 minutes' AS received_at,
       (g%110)::smallint AS call_type,
       ((g-1)%6000+1) AS building_id,
       (g%5)::smallint AS priority,
       'Synthetic caller account, call-taking details and risk assessment narrative ' || g AS call_narrative
FROM generate_series(1,100000) g;
ALTER TABLE bench_call ADD PRIMARY KEY (call_id);
CREATE INDEX bench_call_received_idx ON bench_call(received_at);
CREATE INDEX bench_call_building_idx ON bench_call(building_id);

CREATE TEMP TABLE bench_dispatch_action AS
SELECT g AS action_id, ((g-1)%100000+1) AS call_id,
       ((g-1)%250+1) AS officer_id,
       timestamptz '2020-01-01 00:00:00+00' + g*interval '4 minutes' AS action_at,
       (g%16)::smallint AS action_code,
       'Synthetic CAD status, radio traffic reference and dispatch note ' || g AS action_note
FROM generate_series(1,200000) g;
ALTER TABLE bench_dispatch_action ADD PRIMARY KEY (action_id);
CREATE INDEX bench_dispatch_call_idx ON bench_dispatch_action(call_id);
CREATE INDEX bench_dispatch_officer_time_idx ON bench_dispatch_action(officer_id,action_at);

CREATE TEMP TABLE bench_patrol_event AS
SELECT g AS patrol_event_id, ((g-1)%250+1) AS officer_id,
       timestamptz '2020-01-01 00:00:00+00' + g*interval '5 minutes' AS occurred_at,
       ((g-1)%6000+1) AS building_id,
       (g%30)::smallint AS activity_code,
       'Synthetic patrol observation, route, contact or intervention ' || g AS narrative
FROM generate_series(1,150000) g;
ALTER TABLE bench_patrol_event ADD PRIMARY KEY (patrol_event_id);
CREATE INDEX bench_patrol_officer_time_idx ON bench_patrol_event(officer_id,occurred_at);
CREATE INDEX bench_patrol_building_idx ON bench_patrol_event(building_id);

CREATE TEMP TABLE bench_police_report AS
SELECT g AS report_id, ((g-1)%100000+1) AS call_id,
       ((g-1)%250+1) AS reporting_officer,
       timestamptz '2020-01-01 00:00:00+00' + g*interval '2 hours' AS submitted_at,
       'Synthetic report with circumstances, actions, statements, observations and outcome. Report ' || g ||
       '. ' || repeat('Detailed narrative content for measured report text length. ', 8) AS report_body
FROM generate_series(1,60000) g;
ALTER TABLE bench_police_report ADD PRIMARY KEY (report_id);
CREATE INDEX bench_report_call_idx ON bench_police_report(call_id);
CREATE INDEX bench_report_officer_idx ON bench_police_report(reporting_officer);

CREATE TEMP TABLE bench_interview AS
SELECT g AS interview_id, ((g-1)%2000+1) AS case_id,
       ((g-1)%10000+1) AS person_id,
       ((g-1)%250+1) AS interviewing_officer,
       timestamptz '2021-01-01 00:00:00+00' + g*interval '3 hours' AS interview_at,
       (g%8)::smallint AS interview_type,
       'Synthetic interview record. ' || repeat('Question, answer, clarification, account detail and evidential context. ', 18) AS transcript_text
FROM generate_series(1,30000) g;
ALTER TABLE bench_interview ADD PRIMARY KEY (interview_id);
CREATE INDEX bench_interview_case_idx ON bench_interview(case_id);
CREATE INDEX bench_interview_person_idx ON bench_interview(person_id);

CREATE TEMP TABLE bench_intelligence (
  intelligence_id integer PRIMARY KEY,
  created_at timestamptz NOT NULL,
  source_grade smallint NOT NULL,
  confidence_code smallint NOT NULL,
  narrative text NOT NULL,
  linked_person_id integer NOT NULL
) ON COMMIT PRESERVE ROWS;
INSERT INTO bench_intelligence
SELECT g, timestamptz '2020-01-01 00:00:00+00'+g*interval '5 hours',
       (g%6)::smallint,(g%5)::smallint,
       'Synthetic intelligence report. ' || repeat('Source evaluation, corroboration, reliability, handling caveat and analytical assessment. ', 12),
       ((g-1)%10000+1)
FROM generate_series(1,20000) g;
CREATE INDEX bench_intel_person_idx ON bench_intelligence(linked_person_id);
CREATE INDEX bench_intel_time_idx ON bench_intelligence(created_at);

CREATE TEMP TABLE bench_surveillance AS
SELECT g AS surveillance_id, ((g-1)%2000+1) AS case_id,
       ((g-1)%6000+1) AS building_id,
       timestamptz '2022-01-01 00:00:00+00'+g*interval '2 hours' AS started_at,
       (g%6)::smallint AS method_code,
       'Synthetic authority, deployment, observation and result record ' || g AS observation_summary
FROM generate_series(1,10000) g;
ALTER TABLE bench_surveillance ADD PRIMARY KEY (surveillance_id);
CREATE INDEX bench_surveillance_case_idx ON bench_surveillance(case_id);
CREATE INDEX bench_surveillance_building_idx ON bench_surveillance(building_id);

CREATE TEMP TABLE bench_warrant AS
SELECT g AS warrant_id, ((g-1)%2000+1) AS case_id,
       ((g-1)%10000+1) AS subject_person_id,
       date '2020-01-01'+(g%2000) AS issued_on,
       (g%12)::smallint AS warrant_type,
       'Synthetic application grounds, scope, execution and return record ' || g AS warrant_detail
FROM generate_series(1,8000) g;
ALTER TABLE bench_warrant ADD PRIMARY KEY (warrant_id);
CREATE INDEX bench_warrant_case_idx ON bench_warrant(case_id);
CREATE INDEX bench_warrant_subject_idx ON bench_warrant(subject_person_id);

CREATE TEMP TABLE bench_arrest AS
SELECT g AS arrest_id, ((g-1)%2000+1) AS case_id,
       ((g-1)%10000+1) AS person_id,
       ((g-1)%250+1) AS arresting_officer,
       timestamptz '2020-01-01 00:00:00+00'+g*interval '6 hours' AS arrested_at,
       'Synthetic grounds, caution, search, property and arrest circumstances ' || g AS arrest_record
FROM generate_series(1,12000) g;
ALTER TABLE bench_arrest ADD PRIMARY KEY (arrest_id);
CREATE INDEX bench_arrest_case_idx ON bench_arrest(case_id);
CREATE INDEX bench_arrest_person_idx ON bench_arrest(person_id);

CREATE TEMP TABLE bench_custody AS
SELECT g AS custody_id, ((g-1)%12000+1) AS arrest_id,
       timestamptz '2020-01-01 00:00:00+00'+g*interval '6 hours' AS booked_at,
       (g%14)::smallint AS disposal_code,
       'Synthetic custody risk, rights, welfare, property and detention review ' || g AS custody_note
FROM generate_series(1,12000) g;
ALTER TABLE bench_custody ADD PRIMARY KEY (custody_id);
CREATE INDEX bench_custody_arrest_idx ON bench_custody(arrest_id);

CREATE TEMP TABLE bench_forensic_exam AS
SELECT g AS examination_id, ((g-1)%10000+1) AS evidence_id,
       ((g-1)%2000+1) AS case_id,
       timestamptz '2021-01-01 00:00:00+00'+g*interval '4 hours' AS examined_at,
       (g%35)::smallint AS discipline_code,
       'Synthetic forensic submission, method, observations, limitations and conclusion. ' ||
       repeat('Recorded analytical detail and quality assurance statement. ', 8) AS examination_result
FROM generate_series(1,20000) g;
ALTER TABLE bench_forensic_exam ADD PRIMARY KEY (examination_id);
CREATE INDEX bench_forensic_evidence_idx ON bench_forensic_exam(evidence_id);
CREATE INDEX bench_forensic_case_idx ON bench_forensic_exam(case_id);

CREATE TEMP TABLE bench_court_proceeding AS
SELECT g AS proceeding_id, ((g-1)%2000+1) AS case_id,
       timestamptz '2022-01-01 00:00:00+00'+g*interval '1 day' AS proceeding_at,
       (g%20)::smallint AS proceeding_type,
       'Synthetic filing, hearing, ruling, evidence and disposition summary ' || g AS proceeding_record
FROM generate_series(1,30000) g;
ALTER TABLE bench_court_proceeding ADD PRIMARY KEY (proceeding_id);
CREATE INDEX bench_court_case_idx ON bench_court_proceeding(case_id);
CREATE INDEX bench_court_date_idx ON bench_court_proceeding(proceeding_at);

CREATE TEMP TABLE bench_transaction AS
SELECT g AS transaction_id, ((g-1)%10000+1) AS business_id,
       timestamptz '2020-01-01 00:00:00+00'+g*interval '30 minutes' AS transacted_at,
       (g%40)::smallint AS transaction_type,
       ((g%500000)+100)::bigint AS amount_minor_units,
       'Synthetic commercial transaction reference ' || g AS transaction_reference
FROM generate_series(1,200000) g;
ALTER TABLE bench_transaction ADD PRIMARY KEY (transaction_id);
CREATE INDEX bench_transaction_business_time_idx ON bench_transaction(business_id,transacted_at);

CREATE TEMP TABLE bench_address_history AS
SELECT g AS address_history_id, ((g-1)%10000+1) AS person_id,
       ((g-1)%6000+1) AS building_id,
       date '2000-01-01'+(g%9000) AS valid_from,
       'Synthetic residence and address change history ' || g AS history_note
FROM generate_series(1,30000) g;
ALTER TABLE bench_address_history ADD PRIMARY KEY (address_history_id);
CREATE INDEX bench_address_person_idx ON bench_address_history(person_id);
CREATE INDEX bench_address_building_idx ON bench_address_history(building_id);

CREATE TEMP TABLE bench_household_membership AS
SELECT g AS membership_id, ((g-1)%2500+1) AS household_id,
       ((g-1)%10000+1) AS person_id,
       (g%12)::smallint AS household_role,
       date '2010-01-01'+(g%5000) AS joined_on
FROM generate_series(1,12000) g;
ALTER TABLE bench_household_membership ADD PRIMARY KEY (membership_id);
CREATE INDEX bench_household_id_idx ON bench_household_membership(household_id);
CREATE INDEX bench_household_person_idx ON bench_household_membership(person_id);

ANALYZE;
\echo BENCHMARK_0002_ROW_COUNTS
SELECT 'districts='||count(*) FROM bench_district
UNION ALL SELECT 'streets='||count(*) FROM bench_street
UNION ALL SELECT 'junctions='||count(*) FROM bench_junction
UNION ALL SELECT 'buildings='||count(*) FROM bench_building
UNION ALL SELECT 'property_history='||count(*) FROM bench_property_history
UNION ALL SELECT 'organisations='||count(*) FROM bench_organisation
UNION ALL SELECT 'institutional_staff='||count(*) FROM bench_institutional_staff
UNION ALL SELECT 'police_personnel='||count(*) FROM bench_police_personnel
UNION ALL SELECT 'duty_shifts='||count(*) FROM bench_duty_shift
UNION ALL SELECT 'calls='||count(*) FROM bench_call
UNION ALL SELECT 'dispatch_actions='||count(*) FROM bench_dispatch_action
UNION ALL SELECT 'patrol_events='||count(*) FROM bench_patrol_event
UNION ALL SELECT 'police_reports='||count(*) FROM bench_police_report
UNION ALL SELECT 'interviews='||count(*) FROM bench_interview
UNION ALL SELECT 'intelligence_reports='||count(*) FROM bench_intelligence
UNION ALL SELECT 'surveillance_sessions='||count(*) FROM bench_surveillance
UNION ALL SELECT 'warrants='||count(*) FROM bench_warrant
UNION ALL SELECT 'arrests='||count(*) FROM bench_arrest
UNION ALL SELECT 'custody_records='||count(*) FROM bench_custody
UNION ALL SELECT 'forensic_examinations='||count(*) FROM bench_forensic_exam
UNION ALL SELECT 'court_proceedings='||count(*) FROM bench_court_proceeding
UNION ALL SELECT 'commercial_transactions='||count(*) FROM bench_transaction
UNION ALL SELECT 'address_history='||count(*) FROM bench_address_history
UNION ALL SELECT 'household_memberships='||count(*) FROM bench_household_membership;

\echo BENCHMARK_0002_STORAGE_BY_TABLE
SELECT relname,
       pg_relation_size(relid) AS heap_bytes,
       pg_indexes_size(relid) AS index_bytes,
       pg_total_relation_size(relid) AS total_bytes,
       round(pg_total_relation_size(relid)::numeric/1000000,3) AS total_mb
FROM pg_catalog.pg_statio_user_tables
WHERE schemaname LIKE 'pg_temp_%' AND relname LIKE 'bench_%'
ORDER BY pg_total_relation_size(relid) DESC;

\echo BENCHMARK_0002_TOTAL
SELECT count(*) AS table_count,
       sum(pg_relation_size(relid)) AS heap_bytes,
       sum(pg_indexes_size(relid)) AS index_bytes,
       sum(pg_total_relation_size(relid)) AS total_relation_bytes,
       round(sum(pg_total_relation_size(relid))::numeric/1000000,3) AS total_relation_mb
FROM pg_catalog.pg_statio_user_tables
WHERE schemaname LIKE 'pg_temp_%' AND relname LIKE 'bench_%';
\echo BENCHMARK_0002_TEMPORARY_DATA_ONLY
