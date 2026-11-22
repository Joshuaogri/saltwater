\set ON_ERROR_STOP on
\timing on
-- Stage 4 expands longitudinal life, household, address, business, public-service,
-- police-professional, radio, forensic and justice records.
-- Synthetic only; workflow removes sw_bench_run_0004 after measurements.
CREATE SCHEMA sw_bench_run_0004;
SET search_path TO sw_bench_run_0004, public;

CREATE TABLE s4_household (
  household_id integer PRIMARY KEY,
  household_type smallint NOT NULL,
  formed_on date NOT NULL,
  household_profile text NOT NULL
);
INSERT INTO s4_household
SELECT g,(g%12)::smallint,date '1991-01-01'+(g%12000),
       'Synthetic household composition, dependants, shared responsibilities and change history. Household '||g
FROM generate_series(1,5000) g;

CREATE TABLE s4_household_member (
  membership_id integer PRIMARY KEY,
  household_id integer NOT NULL REFERENCES s4_household,
  person_id integer NOT NULL,
  role_code smallint NOT NULL,
  valid_from date NOT NULL,
  valid_to date,
  change_reason text NOT NULL
);
INSERT INTO s4_household_member
SELECT g,((g-1)%5000)+1,((g-1)%10000)+1,(g%14)::smallint,
       date '1991-01-01'+(g%12000),
       CASE WHEN g%4=0 THEN date '2005-01-01'+(g%7000) END,
       'Synthetic household entry, departure, relationship and dependency change '||g
FROM generate_series(1,10000) g;
CREATE INDEX s4_household_member_person_idx ON s4_household_member(person_id);

CREATE TABLE s4_address_history (
  address_history_id bigint PRIMARY KEY,
  person_id integer NOT NULL,
  address_id integer NOT NULL,
  valid_from date NOT NULL,
  valid_to date,
  residence_type smallint NOT NULL,
  recorded_reason text NOT NULL
);
INSERT INTO s4_address_history
SELECT g,((g-1)%10000)+1,((g*31-1)%6000)+1,
       date '1991-01-01'+(g%12500),
       CASE WHEN g%3=0 THEN date '2008-01-01'+(g%6500) END,
       (g%8)::smallint,
       'Synthetic address move, occupancy, temporary residence and verification history '||g
FROM generate_series(1,40000) g;
CREATE INDEX s4_address_person_date_idx ON s4_address_history(person_id,valid_from);

CREATE TABLE s4_resident_life_event (
  life_event_id bigint PRIMARY KEY,
  person_id integer NOT NULL,
  occurred_at timestamptz NOT NULL,
  event_code smallint NOT NULL,
  location_id integer,
  event_detail text NOT NULL,
  attributes jsonb NOT NULL
);
INSERT INTO s4_resident_life_event
SELECT g,((g-1)%10000)+1,
       timestamptz '1991-01-01 00:00:00+00'+(g%12784)*interval '1 day',
       (g%42)::smallint,(g%6000)+1,
       'Synthetic longitudinal life event including education, employment, family, travel, health-service and civic milestones. Record '||g||'.',
       jsonb_build_object('source','stage4-synthetic','sequence',g,'scenario_year',1+(g%35),'verified',g%7<>0)
FROM generate_series(1,200000) g;
CREATE INDEX s4_life_event_person_time_idx ON s4_resident_life_event(person_id,occurred_at);
CREATE INDEX s4_life_event_time_idx ON s4_resident_life_event(occurred_at);

CREATE TABLE s4_business_staffing_history (
  staffing_history_id bigint PRIMARY KEY,
  business_id integer NOT NULL,
  person_id integer NOT NULL,
  job_code smallint NOT NULL,
  started_on date NOT NULL,
  ended_on date,
  employment_terms text NOT NULL
);
INSERT INTO s4_business_staffing_history
SELECT g,((g-1)%10000)+1,((g*17-1)%10000)+1,(g%160)::smallint,
       date '1991-01-01'+(g%12500),
       CASE WHEN g%3=0 THEN date '2005-01-01'+(g%8000) END,
       'Synthetic appointment, role, working pattern, contract and separation details '||g
FROM generate_series(1,50000) g;
CREATE INDEX s4_staff_business_idx ON s4_business_staffing_history(business_id);
CREATE INDEX s4_staff_person_idx ON s4_business_staffing_history(person_id);

CREATE TABLE s4_commercial_transaction (
  transaction_id bigint PRIMARY KEY,
  business_id integer NOT NULL,
  occurred_at timestamptz NOT NULL,
  transaction_type smallint NOT NULL,
  amount_minor bigint NOT NULL,
  counterparty_person_id integer,
  transaction_reference text NOT NULL,
  transaction_context text NOT NULL
);
INSERT INTO s4_commercial_transaction
SELECT g,((g-1)%10000)+1,
       timestamptz '1991-01-01 00:00:00+00'+(g%12784)*interval '1 day',
       (g%24)::smallint,((g*7919)%25000000)+100,
       CASE WHEN g%2=0 THEN ((g*13-1)%10000)+1 END,
       'S4-TXN-'||lpad(g::text,9,'0'),
       'Synthetic commercial activity, payment context, invoice reference and reconciliation note '||g
FROM generate_series(1,100000) g;
CREATE INDEX s4_transaction_business_time_idx ON s4_commercial_transaction(business_id,occurred_at);

CREATE TABLE s4_public_organisation (
  organisation_id integer PRIMARY KEY,
  parent_organisation_id integer,
  organisation_type smallint NOT NULL,
  established_on date NOT NULL,
  remit text NOT NULL,
  organisational_history text NOT NULL
);
INSERT INTO s4_public_organisation
SELECT g,CASE WHEN g>1 THEN (g/2)::integer END,(g%30)::smallint,
       date '1991-01-01'+(g%9000),
       'Synthetic public mandate, service remit and statutory function '||g,
       'Synthetic formation, restructuring, transfer and closure history '||g
FROM generate_series(1,60) g;

CREATE TABLE s4_public_office_history (
  office_history_id integer PRIMARY KEY,
  organisation_id integer NOT NULL REFERENCES s4_public_organisation,
  person_id integer NOT NULL,
  office_code smallint NOT NULL,
  appointed_on date NOT NULL,
  ended_on date,
  appointment_record text NOT NULL
);
INSERT INTO s4_public_office_history
SELECT g,((g-1)%60)+1,((g*19-1)%10000)+1,(g%90)::smallint,
       date '1991-01-01'+(g%12000),
       CASE WHEN g%4=0 THEN date '2008-01-01'+(g%6000) END,
       'Synthetic appointment, authority, delegation, performance and departure record '||g
FROM generate_series(1,500) g;
CREATE INDEX s4_office_org_idx ON s4_public_office_history(organisation_id);
CREATE INDEX s4_office_person_idx ON s4_public_office_history(person_id);

CREATE TABLE s4_public_service_encounter (
  encounter_id bigint PRIMARY KEY,
  person_id integer NOT NULL,
  organisation_id integer NOT NULL REFERENCES s4_public_organisation,
  service_code smallint NOT NULL,
  occurred_at timestamptz NOT NULL,
  outcome_code smallint NOT NULL,
  encounter_summary text NOT NULL
);
INSERT INTO s4_public_service_encounter
SELECT g,((g-1)%10000)+1,((g-1)%60)+1,(g%80)::smallint,
       timestamptz '1991-01-01 00:00:00+00'+(g%12784)*interval '1 day',
       (g%18)::smallint,
       'Synthetic confidential public-service encounter, referral, assessment, action and outcome record '||g
FROM generate_series(1,50000) g;
CREATE INDEX s4_service_person_time_idx ON s4_public_service_encounter(person_id,occurred_at);
CREATE INDEX s4_service_org_idx ON s4_public_service_encounter(organisation_id);

CREATE TABLE s4_education_enrolment (
  enrolment_id bigint PRIMARY KEY,
  person_id integer NOT NULL,
  institution_id integer NOT NULL,
  programme_code smallint NOT NULL,
  started_on date NOT NULL,
  completed_on date,
  achievement_record text NOT NULL
);
INSERT INTO s4_education_enrolment
SELECT g,((g-1)%10000)+1,((g-1)%250)+1,(g%120)::smallint,
       date '1991-01-01'+(g%12000),
       CASE WHEN g%5<>0 THEN date '1994-01-01'+(g%12000) END,
       'Synthetic enrolment, attendance, progression, qualification and outcome history '||g
FROM generate_series(1,30000) g;
CREATE INDEX s4_education_person_idx ON s4_education_enrolment(person_id);

CREATE TABLE s4_police_training_history (
  training_id bigint PRIMARY KEY,
  officer_id integer NOT NULL,
  course_code smallint NOT NULL,
  started_at timestamptz NOT NULL,
  completed_at timestamptz,
  result_code smallint NOT NULL,
  training_record text NOT NULL
);
INSERT INTO s4_police_training_history
SELECT g,((g-1)%250)+1,(g%140)::smallint,
       timestamptz '1991-01-01 00:00:00+00'+(g%12784)*interval '1 day',
       CASE WHEN g%8<>0 THEN timestamptz '1991-01-02 00:00:00+00'+(g%12784)*interval '1 day' END,
       (g%9)::smallint,
       'Synthetic police recruitment, probation, mandatory training, specialist accreditation and refresher record '||g
FROM generate_series(1,10000) g;
CREATE INDEX s4_training_officer_time_idx ON s4_police_training_history(officer_id,started_at);

CREATE TABLE s4_police_discipline_history (
  discipline_id integer PRIMARY KEY,
  officer_id integer NOT NULL,
  initiated_at timestamptz NOT NULL,
  allegation_code smallint NOT NULL,
  process_stage smallint NOT NULL,
  outcome_code smallint,
  decision_record text NOT NULL
);
INSERT INTO s4_police_discipline_history
SELECT g,((g-1)%250)+1,
       timestamptz '1991-01-01 00:00:00+00'+(g%12784)*interval '1 day',
       (g%35)::smallint,(g%12)::smallint,
       CASE WHEN g%5<>0 THEN (g%9)::smallint END,
       'Synthetic complaint, investigation, hearing, findings, sanction or exoneration record '||g
FROM generate_series(1,2000) g;
CREATE INDEX s4_discipline_officer_time_idx ON s4_police_discipline_history(officer_id,initiated_at);

CREATE TABLE s4_radio_communication (
  communication_id bigint PRIMARY KEY,
  occurred_at timestamptz NOT NULL,
  channel_code smallint NOT NULL,
  sender_officer_id integer,
  recipient_unit_code smallint,
  related_call_id bigint,
  transmission_text text NOT NULL
);
INSERT INTO s4_radio_communication
SELECT g,timestamptz '1991-01-01 00:00:00+00'+(g%12784)*interval '1 day',
       (g%24)::smallint,CASE WHEN g%3<>0 THEN ((g-1)%250)+1 END,
       (g%26)::smallint,CASE WHEN g%2=0 THEN ((g-1)%100000)+1 END,
       'Synthetic radio transmission recording dispatch, acknowledgement, status update, request, warning and closure traffic '||g
FROM generate_series(1,80000) g;
CREATE INDEX s4_radio_time_idx ON s4_radio_communication(occurred_at);
CREATE INDEX s4_radio_call_idx ON s4_radio_communication(related_call_id);

CREATE TABLE s4_forensic_examination (
  examination_id bigint PRIMARY KEY,
  evidence_id integer NOT NULL,
  case_id integer NOT NULL,
  discipline_code smallint NOT NULL,
  submitted_at timestamptz NOT NULL,
  completed_at timestamptz,
  result_summary text NOT NULL,
  interpretation_and_limits text NOT NULL
);
INSERT INTO s4_forensic_examination
SELECT g,((g-1)%10000)+1,((g-1)%2000)+1,(g%32)::smallint,
       timestamptz '1991-01-01 00:00:00+00'+(g%12784)*interval '1 day',
       CASE WHEN g%7<>0 THEN timestamptz '1991-01-03 00:00:00+00'+(g%12784)*interval '1 day' END,
       'Synthetic forensic examination result, observations, methods and findings '||g,
       'Synthetic limitations, uncertainty, quality controls, alternative explanations and review notes '||g
FROM generate_series(1,15000) g;
CREATE INDEX s4_forensic_case_idx ON s4_forensic_examination(case_id);
CREATE INDEX s4_forensic_evidence_idx ON s4_forensic_examination(evidence_id);

CREATE TABLE s4_legal_proceeding (
  proceeding_id bigint PRIMARY KEY,
  case_id integer NOT NULL,
  person_id integer NOT NULL,
  proceeding_type smallint NOT NULL,
  commenced_at timestamptz NOT NULL,
  concluded_at timestamptz,
  stage_code smallint NOT NULL,
  filing_summary text NOT NULL,
  outcome_and_reasons text NOT NULL
);
INSERT INTO s4_legal_proceeding
SELECT g,((g-1)%2000)+1,((g*11-1)%10000)+1,(g%22)::smallint,
       timestamptz '1991-01-01 00:00:00+00'+(g%12784)*interval '1 day',
       CASE WHEN g%6<>0 THEN timestamptz '1991-01-05 00:00:00+00'+(g%12784)*interval '1 day' END,
       (g%14)::smallint,
       'Synthetic filing, disclosure, hearing, application and procedural history '||g,
       'Synthetic judicial finding, sentence, dismissal, acquittal, appeal or other disposition and reasons '||g
FROM generate_series(1,8000) g;
CREATE INDEX s4_legal_case_idx ON s4_legal_proceeding(case_id);
CREATE INDEX s4_legal_person_idx ON s4_legal_proceeding(person_id);

ANALYZE;

\echo BENCHMARK_0004_EXACT_COUNTS
CREATE TEMP TABLE s4_exact_row_counts(table_name text PRIMARY KEY, exact_rows bigint NOT NULL);
DO $$
DECLARE r record;
BEGIN
  FOR r IN
    SELECT c.relname
    FROM pg_class c
    JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='sw_bench_run_0004' AND c.relkind='r'
    ORDER BY c.relname
  LOOP
    EXECUTE format('INSERT INTO s4_exact_row_counts SELECT %L, count(*) FROM %I.%I',
                   r.relname, 'sw_bench_run_0004', r.relname);
  END LOOP;
END $$;
SELECT table_name, exact_rows FROM s4_exact_row_counts ORDER BY table_name;

\echo BENCHMARK_0004_EXACT_TOTAL
SELECT sum(exact_rows) AS exact_total_rows FROM s4_exact_row_counts;

\echo BENCHMARK_0004_STORAGE_BY_TABLE
SELECT c.relname AS table_name, pg_relation_size(c.oid) AS heap_bytes,
       pg_indexes_size(c.oid) AS index_bytes, pg_total_relation_size(c.oid) AS total_bytes,
       round(pg_total_relation_size(c.oid)::numeric/1000000,3) AS total_mb
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='sw_bench_run_0004' AND c.relkind='r'
ORDER BY pg_total_relation_size(c.oid) DESC;

\echo BENCHMARK_0004_TOTAL
SELECT sum(pg_relation_size(c.oid)) AS heap_bytes,
       sum(pg_indexes_size(c.oid)) AS index_bytes,
       sum(pg_total_relation_size(c.oid)-pg_relation_size(c.oid)-pg_indexes_size(c.oid)) AS toast_aux_bytes,
       sum(pg_total_relation_size(c.oid)) AS relation_total_bytes,
       round(sum(pg_total_relation_size(c.oid))::numeric/1000000,3) AS relation_total_mb
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='sw_bench_run_0004' AND c.relkind='r';
