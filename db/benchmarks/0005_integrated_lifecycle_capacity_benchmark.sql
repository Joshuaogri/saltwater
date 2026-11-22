\set ON_ERROR_STOP on
\timing on

-- Saltwater integrated lifecycle benchmark 0005.
-- One coherent 35-year synthetic world. Shared entities are created once.
-- Stage-overlap policy: retain the larger representative history, never sum
-- duplicate entity sets from earlier stages. No production records are written.

CREATE SCHEMA sw_bench_integrated;
SET search_path TO sw_bench_integrated, public;

CREATE TABLE resident AS
SELECT g::integer AS resident_id,
       'Given' || (g % 97) AS given_name,
       'Family' || (g % 389) AS family_name,
       date '1960-01-01' + (g % 18000) AS date_of_birth,
       'Persistent synthetic resident biography covering identity, household, education, employment, relationships, service interactions and longitudinal context. ' ||
       repeat('Resident history detail; ', 5) || g AS biography,
       (g % 4)::smallint AS status_code
FROM generate_series(1,10000) g;
ALTER TABLE resident ADD PRIMARY KEY (resident_id);

CREATE TABLE business AS
SELECT g::integer AS business_id,
       'Saltwater Enterprise ' || g AS legal_name,
       (g%35)::smallint AS business_type,
       ((g-1)%6000+1)::integer AS premises_building_id,
       ((g-1)%10000+1)::integer AS owner_resident_id,
       'Synthetic business profile, ownership, trading activity, premises use, staffing and operating context. ' || repeat('Business profile detail; ',3) || g AS profile
FROM generate_series(1,10000) g;
ALTER TABLE business ADD PRIMARY KEY (business_id);
CREATE INDEX business_building_idx ON business(premises_building_id);
CREATE INDEX business_owner_idx ON business(owner_resident_id);

CREATE TABLE district AS SELECT g::smallint AS district_id, 'District '||g AS name, 'District service and geographic profile '||g AS description FROM generate_series(1,12) g;
ALTER TABLE district ADD PRIMARY KEY(district_id);
CREATE TABLE street AS SELECT g::integer AS street_id, ((g-1)%12+1)::smallint AS district_id, 'Street '||g AS name, (g%5)::smallint AS class_code FROM generate_series(1,800) g;
ALTER TABLE street ADD PRIMARY KEY(street_id);
CREATE INDEX street_district_idx ON street(district_id);
CREATE TABLE junction AS SELECT g::integer AS junction_id, ((g-1)%800+1)::integer AS street_a, ((g*17-1)%800+1)::integer AS street_b, 'Junction '||g AS name FROM generate_series(1,2500) g;
ALTER TABLE junction ADD PRIMARY KEY(junction_id);
CREATE TABLE building AS SELECT g::integer AS building_id, ((g-1)%800+1)::integer AS street_id, ((g-1)%12+1)::smallint AS district_id, 'Building '||g||', Street '||((g-1)%800+1) AS address, (g%14)::smallint AS use_code, 'Building access, occupancy, floor and use profile '||g AS description FROM generate_series(1,6000) g;
ALTER TABLE building ADD PRIMARY KEY(building_id);
CREATE INDEX building_street_idx ON building(street_id);
CREATE INDEX building_district_idx ON building(district_id);

CREATE TABLE household AS SELECT g::integer AS household_id, 'Household profile '||g AS profile, (g%8)::smallint AS household_type FROM generate_series(1,5000) g;
ALTER TABLE household ADD PRIMARY KEY(household_id);
CREATE TABLE household_member AS SELECT g::integer AS membership_id, ((g-1)%5000+1)::integer AS household_id, ((g-1)%10000+1)::integer AS resident_id, (g%12)::smallint AS role_code, date '2010-01-01'+(g%5000) AS joined_on FROM generate_series(1,12000) g;
ALTER TABLE household_member ADD PRIMARY KEY(membership_id);
CREATE INDEX household_member_resident_idx ON household_member(resident_id);
CREATE TABLE relationship_history AS SELECT g::integer AS relationship_id, ((g-1)%10000+1)::integer AS resident_a, ((g*37-1)%10000+1)::integer AS resident_b, (g%18)::smallint AS relationship_type, date '1990-01-01'+(g%12000) AS valid_from, 'Relationship context and change record '||g AS note FROM generate_series(1,30000) g;
ALTER TABLE relationship_history ADD PRIMARY KEY(relationship_id);
CREATE INDEX relationship_a_idx ON relationship_history(resident_a);
CREATE INDEX relationship_b_idx ON relationship_history(resident_b);
CREATE TABLE resident_address_history AS SELECT g::integer AS address_history_id, ((g-1)%10000+1)::integer AS resident_id, ((g-1)%6000+1)::integer AS building_id, date '1990-01-01'+(g%12000) AS valid_from, 'Address change, occupancy and residence context '||g AS note FROM generate_series(1,40000) g;
ALTER TABLE resident_address_history ADD PRIMARY KEY(address_history_id);
CREATE INDEX resident_address_person_idx ON resident_address_history(resident_id);
CREATE INDEX resident_address_building_idx ON resident_address_history(building_id);
CREATE TABLE resident_life_event AS SELECT g::bigint AS event_id, ((g-1)%10000+1)::integer AS resident_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '90 minutes' AS occurred_at, (g%180)::smallint AS event_type, 'Longitudinal life event with actor, subject, location, source, context and outcome. '||repeat('Recorded life-history detail; ',3)||g AS event_detail FROM generate_series(1,200000) g;
ALTER TABLE resident_life_event ADD PRIMARY KEY(event_id);
CREATE INDEX resident_life_event_person_time_idx ON resident_life_event(resident_id,occurred_at);

CREATE TABLE property_history AS SELECT g::integer AS history_id, ((g-1)%6000+1)::integer AS building_id, date '1990-01-01'+(g%12000) AS effective_date, (g%9)::smallint AS tenure_code, 'Ownership, lease, occupancy, subletting and use change '||g AS note FROM generate_series(1,30000) g;
ALTER TABLE property_history ADD PRIMARY KEY(history_id);
CREATE INDEX property_history_building_idx ON property_history(building_id);
CREATE TABLE employment_history AS SELECT g::integer AS employment_id, ((g-1)%10000+1)::integer AS resident_id, ((g*13-1)%10000+1)::integer AS business_id, 'Position '||(g%120) AS role_name, date '1990-01-01'+(g%12000) AS started_on, CASE WHEN g%3=0 THEN date '2000-01-01'+(g%9000) ELSE NULL END AS ended_on, 'Employment appointment, posting, pay band and separation history '||g AS note FROM generate_series(1,50000) g;
ALTER TABLE employment_history ADD PRIMARY KEY(employment_id);
CREATE INDEX employment_resident_idx ON employment_history(resident_id);
CREATE INDEX employment_business_idx ON employment_history(business_id);
CREATE TABLE commercial_transaction AS SELECT g::bigint AS transaction_id, ((g-1)%10000+1)::integer AS business_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '45 minutes' AS transacted_at, (g%40)::smallint AS transaction_type, ((g%500000)+100)::bigint AS amount_minor_units, 'Commercial transaction reference and settlement context '||g AS reference FROM generate_series(1,200000) g;
ALTER TABLE commercial_transaction ADD PRIMARY KEY(transaction_id);
CREATE INDEX commercial_transaction_business_time_idx ON commercial_transaction(business_id,transacted_at);

CREATE TABLE organisation AS SELECT g::integer AS organisation_id, 'Saltwater Institution '||g AS name, (g%30)::smallint AS institution_type, 'Mandate, authority, service, governance and operating remit '||g AS remit FROM generate_series(1,80) g;
ALTER TABLE organisation ADD PRIMARY KEY(organisation_id);
CREATE TABLE institutional_staff_history AS SELECT g::integer AS staff_history_id, ((g-1)%80+1)::integer AS organisation_id, ((g-1)%10000+1)::integer AS resident_id, 'Institutional post '||(g%90) AS position_title, date '1990-01-01'+(g%12000) AS appointed_on, 'Appointment, grade, posting and departure history '||g AS note FROM generate_series(1,1200) g;
ALTER TABLE institutional_staff_history ADD PRIMARY KEY(staff_history_id);
CREATE INDEX institutional_staff_org_idx ON institutional_staff_history(organisation_id);
CREATE INDEX institutional_staff_person_idx ON institutional_staff_history(resident_id);
CREATE TABLE public_office_history AS SELECT g::integer AS office_history_id, ((g-1)%80+1)::integer AS organisation_id, ((g-1)%10000+1)::integer AS resident_id, 'Public office '||(g%70) AS office_title, date '1990-01-01'+(g%12000) AS started_on, 'Appointment, term, delegation and office-holder record '||g AS note FROM generate_series(1,500) g;
ALTER TABLE public_office_history ADD PRIMARY KEY(office_history_id);
CREATE TABLE public_service_encounter AS SELECT g::integer AS encounter_id, ((g-1)%10000+1)::integer AS resident_id, ((g-1)%80+1)::integer AS organisation_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '3 hours' AS occurred_at, (g%35)::smallint AS service_type, 'Public service application, appointment, decision and outcome '||repeat('Service record detail; ',3)||g AS record FROM generate_series(1,50000) g;
ALTER TABLE public_service_encounter ADD PRIMARY KEY(encounter_id);
CREATE INDEX service_resident_time_idx ON public_service_encounter(resident_id,occurred_at);
CREATE TABLE education_enrolment AS SELECT g::integer AS enrolment_id, ((g-1)%10000+1)::integer AS resident_id, (g%120)::smallint AS institution_code, date '1991-01-01'+(g%12000) AS enrolled_on, (g%8)::smallint AS outcome_code, 'Education participation and qualification history '||g AS note FROM generate_series(1,30000) g;
ALTER TABLE education_enrolment ADD PRIMARY KEY(enrolment_id);
CREATE INDEX education_resident_idx ON education_enrolment(resident_id);
CREATE TABLE healthcare_encounter AS SELECT g::integer AS encounter_id, ((g-1)%10000+1)::integer AS resident_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '2 hours' AS occurred_at, (g%70)::smallint AS service_code, (g%8)::smallint AS outcome_code, 'Synthetic confidential clinical encounter summary, referral and care continuity metadata '||repeat('Clinical detail; ',4)||g AS record FROM generate_series(1,100000) g;
ALTER TABLE healthcare_encounter ADD PRIMARY KEY(encounter_id);
CREATE INDEX healthcare_resident_time_idx ON healthcare_encounter(resident_id,occurred_at);
CREATE TABLE social_service_case AS SELECT g::integer AS service_case_id, ((g-1)%10000+1)::integer AS resident_id, ((g-1)%80+1)::integer AS organisation_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '1 day' AS opened_at, (g%24)::smallint AS service_type, 'Social support assessment, household context, intervention and closure '||repeat('Casework detail; ',4)||g AS record FROM generate_series(1,40000) g;
ALTER TABLE social_service_case ADD PRIMARY KEY(service_case_id);
CREATE INDEX social_service_resident_idx ON social_service_case(resident_id);
CREATE TABLE foreign_relation_record AS SELECT g::integer AS record_id, (g%45)::smallint AS partner_code, timestamptz '1991-01-01 00:00:00+00'+g*interval '2 days' AS occurred_at, (g%25)::smallint AS subject_code, 'Diplomatic, consular, treaty, trade and external-affairs record '||repeat('Foreign relations detail; ',4)||g AS record FROM generate_series(1,5000) g;
ALTER TABLE foreign_relation_record ADD PRIMARY KEY(record_id);

CREATE TABLE police_personnel AS SELECT g::integer AS officer_id, 'SWP-'||lpad(g::text,5,'0') AS service_number, 'Officer '||g AS display_name, (g%18)::smallint AS rank_code, (g%26)::smallint AS unit_code, date '1990-01-01'+(g%12000) AS service_start, 'Recruitment, vetting, career, posting and personnel summary '||repeat('Career detail; ',3)||g AS career_record FROM generate_series(1,250) g;
ALTER TABLE police_personnel ADD PRIMARY KEY(officer_id);
CREATE UNIQUE INDEX police_service_number_idx ON police_personnel(service_number);
CREATE TABLE police_shift AS SELECT g::integer AS shift_id, ((g-1)%250+1)::integer AS officer_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '8 hours' AS shift_start, ((g-1)%12+1)::smallint AS district_id, (g%4)::smallint AS duty_type, 'Deployment, supervision, tasking and duty outcome '||g AS note FROM generate_series(1,100000) g;
ALTER TABLE police_shift ADD PRIMARY KEY(shift_id);
CREATE INDEX police_shift_officer_time_idx ON police_shift(officer_id,shift_start);
CREATE TABLE police_training_history AS SELECT g::integer AS training_id, ((g-1)%250+1)::integer AS officer_id, date '1991-01-01'+(g%12000) AS completed_on, (g%90)::smallint AS course_code, 'Training attendance, assessment, result and qualification '||g AS note FROM generate_series(1,10000) g;
ALTER TABLE police_training_history ADD PRIMARY KEY(training_id);
CREATE INDEX police_training_officer_idx ON police_training_history(officer_id);
CREATE TABLE police_discipline_history AS SELECT g::integer AS discipline_id, ((g-1)%250+1)::integer AS officer_id, date '1991-01-01'+(g%12000) AS recorded_on, (g%16)::smallint AS outcome_code, 'Complaint, investigation, hearing, finding and sanction history '||g AS record FROM generate_series(1,2000) g;
ALTER TABLE police_discipline_history ADD PRIMARY KEY(discipline_id);
CREATE INDEX police_discipline_officer_idx ON police_discipline_history(officer_id);

CREATE TABLE police_case AS SELECT g::integer AS case_id, 'SW-CASE-'||lpad(g::text,7,'0') AS case_number, timestamptz '1991-01-01 00:00:00+00'+g*interval '5 days' AS opened_at, (g%120)::smallint AS offence_code, (g%8)::smallint AS status_code, 'Case summary, circumstances, scope, linked subjects and investigative context '||repeat('Case narrative; ',5)||g AS summary FROM generate_series(1,2000) g;
ALTER TABLE police_case ADD PRIMARY KEY(case_id);
CREATE UNIQUE INDEX police_case_number_idx ON police_case(case_number);
CREATE TABLE incident AS SELECT g::integer AS incident_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '90 minutes' AS occurred_at, ((g-1)%6000+1)::integer AS building_id, (g%110)::smallint AS incident_type, CASE WHEN g%5=0 THEN ((g-1)%2000+1)::integer ELSE NULL END AS case_id, 'Incident call narrative, attendance, observations, people present and outcome '||repeat('Incident detail; ',3)||g AS narrative FROM generate_series(1,10000) g;
ALTER TABLE incident ADD PRIMARY KEY(incident_id);
CREATE INDEX incident_time_idx ON incident(occurred_at);
CREATE INDEX incident_case_idx ON incident(case_id);
CREATE TABLE emergency_call AS SELECT g::integer AS call_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '7 minutes' AS received_at, (g%110)::smallint AS call_type, ((g-1)%6000+1)::integer AS building_id, (g%5)::smallint AS priority, 'Caller account, call-taking details, risk assessment and contact metadata '||repeat('Call detail; ',3)||g AS narrative FROM generate_series(1,100000) g;
ALTER TABLE emergency_call ADD PRIMARY KEY(call_id);
CREATE INDEX emergency_call_time_idx ON emergency_call(received_at);
CREATE TABLE dispatch_action AS SELECT g::integer AS action_id, ((g-1)%100000+1)::integer AS call_id, ((g-1)%250+1)::integer AS officer_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '4 minutes' AS action_at, (g%16)::smallint AS action_code, 'CAD assignment, status, radio reference and dispatch note '||g AS note FROM generate_series(1,200000) g;
ALTER TABLE dispatch_action ADD PRIMARY KEY(action_id);
CREATE INDEX dispatch_call_idx ON dispatch_action(call_id);
CREATE INDEX dispatch_officer_time_idx ON dispatch_action(officer_id,action_at);
CREATE TABLE patrol_event AS SELECT g::integer AS patrol_event_id, ((g-1)%250+1)::integer AS officer_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '5 minutes' AS occurred_at, ((g-1)%6000+1)::integer AS building_id, (g%30)::smallint AS activity_code, 'Patrol observation, route, contact, intervention and outcome '||repeat('Patrol detail; ',2)||g AS narrative FROM generate_series(1,150000) g;
ALTER TABLE patrol_event ADD PRIMARY KEY(patrol_event_id);
CREATE INDEX patrol_officer_time_idx ON patrol_event(officer_id,occurred_at);
CREATE TABLE police_report AS SELECT g::integer AS report_id, ((g-1)%100000+1)::integer AS call_id, ((g-1)%250+1)::integer AS officer_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '2 hours' AS submitted_at, 'Full synthetic report: circumstances, actions, statements, observations, exhibits, supervisory review and outcome. '||repeat('Detailed report narrative; ',12)||g AS report_body FROM generate_series(1,60000) g;
ALTER TABLE police_report ADD PRIMARY KEY(report_id);
CREATE INDEX police_report_call_idx ON police_report(call_id);
CREATE INDEX police_report_officer_idx ON police_report(officer_id);
CREATE TABLE interview_record AS SELECT g::integer AS interview_id, ((g-1)%2000+1)::integer AS case_id, ((g-1)%10000+1)::integer AS resident_id, ((g-1)%250+1)::integer AS officer_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '3 hours' AS interviewed_at, (g%8)::smallint AS interview_type, 'Interview transcript with questions, answers, clarifications, chronology and evidential context. '||repeat('Question and answer detail; ',18)||g AS transcript FROM generate_series(1,30000) g;
ALTER TABLE interview_record ADD PRIMARY KEY(interview_id);
CREATE INDEX interview_case_idx ON interview_record(case_id);
CREATE INDEX interview_resident_idx ON interview_record(resident_id);
CREATE TABLE intelligence_report AS SELECT g::integer AS intelligence_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '5 hours' AS created_at, (g%6)::smallint AS source_grade, (g%5)::smallint AS confidence_code, ((g-1)%10000+1)::integer AS resident_id, 'Source evaluation, corroboration, reliability, caveats and analytical assessment. '||repeat('Intelligence narrative; ',12)||g AS narrative FROM generate_series(1,20000) g;
ALTER TABLE intelligence_report ADD PRIMARY KEY(intelligence_id);
CREATE INDEX intelligence_resident_idx ON intelligence_report(resident_id);
CREATE TABLE intelligence_link AS SELECT g::integer AS link_id, ((g-1)%20000+1)::integer AS intelligence_id, ((g-1)%10000+1)::integer AS resident_id, (g%20)::smallint AS link_type, (g%5)::smallint AS confidence_code, 'Analytical relationship, corroboration and provenance '||g AS note FROM generate_series(1,40000) g;
ALTER TABLE intelligence_link ADD PRIMARY KEY(link_id);
CREATE INDEX intelligence_link_person_idx ON intelligence_link(resident_id);
CREATE TABLE surveillance_record AS SELECT g::integer AS surveillance_id, ((g-1)%2000+1)::integer AS case_id, ((g-1)%6000+1)::integer AS building_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '2 hours' AS started_at, (g%6)::smallint AS method_code, 'Authority, deployment, observation, continuity and result record '||repeat('Surveillance detail; ',3)||g AS summary FROM generate_series(1,10000) g;
ALTER TABLE surveillance_record ADD PRIMARY KEY(surveillance_id);
CREATE INDEX surveillance_case_idx ON surveillance_record(case_id);
CREATE TABLE warrant AS SELECT g::integer AS warrant_id, ((g-1)%2000+1)::integer AS case_id, ((g-1)%10000+1)::integer AS subject_resident_id, date '1991-01-01'+(g%12000) AS issued_on, (g%12)::smallint AS warrant_type, 'Application grounds, scope, authority, execution and return '||repeat('Warrant detail; ',3)||g AS record FROM generate_series(1,8000) g;
ALTER TABLE warrant ADD PRIMARY KEY(warrant_id);
CREATE INDEX warrant_case_idx ON warrant(case_id);
CREATE TABLE arrest AS SELECT g::integer AS arrest_id, ((g-1)%2000+1)::integer AS case_id, ((g-1)%10000+1)::integer AS resident_id, ((g-1)%250+1)::integer AS officer_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '6 hours' AS arrested_at, 'Grounds, caution, search, property and arrest circumstances '||repeat('Arrest detail; ',3)||g AS record FROM generate_series(1,12000) g;
ALTER TABLE arrest ADD PRIMARY KEY(arrest_id);
CREATE INDEX arrest_case_idx ON arrest(case_id);
CREATE TABLE custody_record AS SELECT g::integer AS custody_id, ((g-1)%12000+1)::integer AS arrest_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '6 hours' AS booked_at, (g%14)::smallint AS disposal_code, 'Custody risk, rights, welfare, property, reviews and detention outcome '||repeat('Custody detail; ',3)||g AS note FROM generate_series(1,12000) g;
ALTER TABLE custody_record ADD PRIMARY KEY(custody_id);
CREATE TABLE evidence_item AS SELECT g::integer AS evidence_id, ((g-1)%2000+1)::integer AS case_id, (g%40)::smallint AS evidence_type, timestamptz '1991-01-01 00:00:00+00'+g*interval '25 minutes' AS collected_at, md5('saltwater-evidence-'||g)||md5('saltwater-integrity-'||g) AS sha256, 'Exhibit description, recovery location, packaging, continuity and examination requirements '||repeat('Evidence detail; ',3)||g AS description FROM generate_series(1,10000) g;
ALTER TABLE evidence_item ADD PRIMARY KEY(evidence_id);
CREATE INDEX evidence_case_idx ON evidence_item(case_id);
CREATE TABLE evidence_custody_event AS SELECT g::integer AS custody_event_id, ((g-1)%10000+1)::integer AS evidence_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '2 hours' AS occurred_at, (g%18)::smallint AS action_code, ((g-1)%250+1)::integer AS officer_id, 'Transfer, seal check, storage, access, submission and audit event '||g AS note FROM generate_series(1,100000) g;
ALTER TABLE evidence_custody_event ADD PRIMARY KEY(custody_event_id);
CREATE INDEX evidence_custody_item_time_idx ON evidence_custody_event(evidence_id,occurred_at);
CREATE TABLE forensic_examination AS SELECT g::integer AS examination_id, ((g-1)%10000+1)::integer AS evidence_id, ((g-1)%2000+1)::integer AS case_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '4 hours' AS examined_at, (g%35)::smallint AS discipline_code, 'Submission, method, observations, limitations, quality review and conclusion. '||repeat('Forensic result detail; ',8)||g AS result FROM generate_series(1,20000) g;
ALTER TABLE forensic_examination ADD PRIMARY KEY(examination_id);
CREATE INDEX forensic_evidence_idx ON forensic_examination(evidence_id);
CREATE INDEX forensic_case_idx ON forensic_examination(case_id);
CREATE TABLE legal_proceeding AS SELECT g::integer AS proceeding_id, ((g-1)%2000+1)::integer AS case_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '1 day' AS proceeding_at, (g%20)::smallint AS proceeding_type, 'Filing, hearing, ruling, evidence, appeal and disposition summary '||repeat('Legal detail; ',5)||g AS record FROM generate_series(1,30000) g;
ALTER TABLE legal_proceeding ADD PRIMARY KEY(proceeding_id);
CREATE INDEX legal_proceeding_case_idx ON legal_proceeding(case_id);
CREATE TABLE prosecution_file AS SELECT g::integer AS prosecution_id, ((g-1)%2000+1)::integer AS case_id, ((g-1)%10000+1)::integer AS defendant_resident_id, date '1991-01-01'+(g%12000) AS referred_on, (g%12)::smallint AS outcome_code, 'Charging decision, disclosure, prosecution review and case outcome '||repeat('Prosecution detail; ',4)||g AS record FROM generate_series(1,10000) g;
ALTER TABLE prosecution_file ADD PRIMARY KEY(prosecution_id);
CREATE TABLE correction_record AS SELECT g::integer AS correction_id, ((g-1)%10000+1)::integer AS resident_id, ((g-1)%10000+1)::integer AS prosecution_id, date '1991-01-01'+(g%12000) AS commenced_on, (g%18)::smallint AS status_code, 'Sentence, custody, rehabilitation, supervision and release history '||repeat('Corrections detail; ',4)||g AS record FROM generate_series(1,12000) g;
ALTER TABLE correction_record ADD PRIMARY KEY(correction_id);

CREATE TABLE radio_communication AS SELECT g::integer AS radio_id, ((g-1)%250+1)::integer AS officer_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '5 minutes' AS occurred_at, (g%40)::smallint AS channel_code, 'Radio transmission content and dispatch context '||repeat('Radio detail; ',3)||g AS transcript FROM generate_series(1,80000) g;
ALTER TABLE radio_communication ADD PRIMARY KEY(radio_id);
CREATE INDEX radio_officer_time_idx ON radio_communication(officer_id,occurred_at);
CREATE TABLE gps_track_point AS SELECT g::bigint AS point_id, ((g-1)%250+1)::integer AS officer_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '2 minutes' AS recorded_at, ((g-1)%6000+1)::integer AS building_id, (g%360)::smallint AS heading, (g%80)::smallint AS speed_code FROM generate_series(1,200000) g;
ALTER TABLE gps_track_point ADD PRIMARY KEY(point_id);
CREATE INDEX gps_officer_time_idx ON gps_track_point(officer_id,recorded_at);
CREATE TABLE bank_account AS SELECT g::integer AS account_id, ((g-1)%10000+1)::integer AS resident_id, ((g-1)%10000+1)::integer AS business_id, (g%12)::smallint AS account_type, date '1991-01-01'+(g%12000) AS opened_on, (g%4)::smallint AS status_code FROM generate_series(1,15000) g;
ALTER TABLE bank_account ADD PRIMARY KEY(account_id);
CREATE INDEX bank_account_resident_idx ON bank_account(resident_id);
CREATE INDEX bank_account_business_idx ON bank_account(business_id);
CREATE TABLE financial_ledger_entry AS SELECT g::bigint AS entry_id, ((g-1)%15000+1)::integer AS account_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '30 minutes' AS posted_at, (g%30)::smallint AS entry_type, ((g%100000000)+1)::bigint AS amount_minor_units, md5('saltwater-ledger-'||g) AS transaction_hash, 'Double-entry ledger reference, counterparty, reconciliation and audit note '||g AS note FROM generate_series(1,300000) g;
ALTER TABLE financial_ledger_entry ADD PRIMARY KEY(entry_id);
CREATE INDEX ledger_account_time_idx ON financial_ledger_entry(account_id,posted_at);
CREATE TABLE tax_return AS SELECT g::integer AS return_id, ((g-1)%10000+1)::integer AS taxpayer_resident_id, ((g-1)%10000+1)::integer AS taxpayer_business_id, (1991+(g%35))::smallint AS tax_year, (g%16)::smallint AS tax_type, ((g%50000000)+1000)::bigint AS assessed_minor_units, 'Tax filing, assessment, amendment and review metadata '||g AS record FROM generate_series(1,10000) g;
ALTER TABLE tax_return ADD PRIMARY KEY(return_id);
CREATE TABLE tax_payment AS SELECT g::integer AS payment_id, ((g-1)%10000+1)::integer AS return_id, timestamptz '1991-01-01 00:00:00+00'+g*interval '1 day' AS paid_at, ((g%5000000)+100)::bigint AS amount_minor_units, (g%8)::smallint AS payment_method FROM generate_series(1,40000) g;
ALTER TABLE tax_payment ADD PRIMARY KEY(payment_id);
CREATE INDEX tax_payment_return_idx ON tax_payment(return_id);

CREATE TABLE benchmark_exact_counts(table_name text PRIMARY KEY, exact_rows bigint NOT NULL);
SELECT format('INSERT INTO sw_bench_integrated.benchmark_exact_counts SELECT %L,count(*) FROM sw_bench_integrated.%I',c.relname,c.relname)
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='sw_bench_integrated' AND c.relkind='r' AND c.relname<>'benchmark_exact_counts'
ORDER BY c.relname
\gexec

ANALYZE;
\echo INTEGRATED_EXACT_ROW_COUNTS
SELECT table_name, exact_rows FROM benchmark_exact_counts ORDER BY table_name;
\echo INTEGRATED_EXACT_TOTAL
SELECT sum(exact_rows)::bigint AS exact_total_rows FROM benchmark_exact_counts;
\echo INTEGRATED_TABLE_STORAGE
SELECT c.relname AS table_name,
       pg_relation_size(c.oid) AS heap_bytes,
       pg_indexes_size(c.oid) AS index_bytes,
       pg_total_relation_size(c.oid)-pg_relation_size(c.oid)-pg_indexes_size(c.oid) AS toast_aux_bytes,
       pg_total_relation_size(c.oid) AS total_bytes,
       round(pg_total_relation_size(c.oid)::numeric/1000000,3) AS total_mb
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='sw_bench_integrated' AND c.relkind='r'
ORDER BY pg_total_relation_size(c.oid) DESC;
\echo INTEGRATED_STORAGE_TOTAL
SELECT sum(pg_relation_size(c.oid)) AS heap_bytes,
       sum(pg_indexes_size(c.oid)) AS index_bytes,
       sum(pg_total_relation_size(c.oid)-pg_relation_size(c.oid)-pg_indexes_size(c.oid)) AS toast_aux_bytes,
       sum(pg_total_relation_size(c.oid)) AS relation_total_bytes,
       round(sum(pg_total_relation_size(c.oid))::numeric/1000000,3) AS relation_total_mb
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='sw_bench_integrated' AND c.relkind='r';
