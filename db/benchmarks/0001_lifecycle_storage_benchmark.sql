\set ON_ERROR_STOP on
\timing on

-- Session-local benchmark only. Temporary relations disappear when this connection closes.
-- All values are synthetic. No production simulation records are inserted.
CREATE TEMP TABLE bench_person (
  person_id integer PRIMARY KEY,
  given_name text NOT NULL,
  family_name text NOT NULL,
  date_of_birth date NOT NULL,
  biography text NOT NULL,
  home_address text NOT NULL,
  status_code smallint NOT NULL
) ON COMMIT PRESERVE ROWS;

INSERT INTO bench_person
SELECT g,
       'Given' || (g % 97),
       'Family' || (g % 389),
       date '1960-01-01' + (g % 18000),
       'Synthetic resident biography. Employment, household, education, social ties and personal history are represented through linked records. Resident reference ' || g || '.',
       'District ' || (g % 12) || ', Street ' || (g % 740) || ', Building ' || (g % 4200),
       (g % 4)::smallint
FROM generate_series(1, 10000) AS g;

CREATE INDEX bench_person_address_idx ON bench_person(home_address);

CREATE TEMP TABLE bench_business (
  business_id integer PRIMARY KEY,
  legal_name text NOT NULL,
  business_type smallint NOT NULL,
  premises_address text NOT NULL,
  description text NOT NULL,
  owner_person_id integer NOT NULL REFERENCES bench_person(person_id),
  employee_count smallint NOT NULL
) ON COMMIT PRESERVE ROWS;

INSERT INTO bench_business
SELECT g,
       'Saltwater Enterprise ' || g,
       (g % 35)::smallint,
       'District ' || (g % 12) || ', Commercial Road ' || (g % 900) || ', Unit ' || g,
       'Synthetic business profile covering activity, trading pattern, premises, ownership and operating context. Business reference ' || g || '.',
       ((g - 1) % 10000) + 1,
       (g % 45)::smallint
FROM generate_series(1, 10000) AS g;

CREATE INDEX bench_business_address_idx ON bench_business(premises_address);
CREATE INDEX bench_business_owner_idx ON bench_business(owner_person_id);

CREATE TEMP TABLE bench_relationship (
  relationship_id integer PRIMARY KEY,
  person_a integer NOT NULL REFERENCES bench_person(person_id),
  person_b integer NOT NULL REFERENCES bench_person(person_id),
  relationship_type smallint NOT NULL,
  valid_from date NOT NULL,
  notes text NOT NULL
) ON COMMIT PRESERVE ROWS;

INSERT INTO bench_relationship
SELECT g,
       ((g - 1) % 10000) + 1,
       ((g * 37) % 10000) + 1,
       (g % 18)::smallint,
       date '2010-01-01' + (g % 5000),
       'Synthetic relationship history and context reference ' || g
FROM generate_series(1, 30000) AS g;

CREATE INDEX bench_relationship_a_idx ON bench_relationship(person_a);
CREATE INDEX bench_relationship_b_idx ON bench_relationship(person_b);

CREATE TEMP TABLE bench_employment (
  employment_id integer PRIMARY KEY,
  person_id integer NOT NULL REFERENCES bench_person(person_id),
  business_id integer NOT NULL REFERENCES bench_business(business_id),
  role_name text NOT NULL,
  started_on date NOT NULL,
  ended_on date
) ON COMMIT PRESERVE ROWS;

INSERT INTO bench_employment
SELECT g,
       ((g - 1) % 10000) + 1,
       ((g * 13 - 1) % 10000) + 1,
       'Position ' || (g % 120),
       date '2015-01-01' + (g % 3000),
       CASE WHEN g % 3 = 0 THEN date '2022-01-01' + (g % 1000) ELSE NULL END
FROM generate_series(1, 20000) AS g;

CREATE INDEX bench_employment_person_idx ON bench_employment(person_id);
CREATE INDEX bench_employment_business_idx ON bench_employment(business_id);

CREATE TEMP TABLE bench_case (
  case_id integer PRIMARY KEY,
  case_number text NOT NULL UNIQUE,
  opened_at timestamptz NOT NULL,
  offence_code smallint NOT NULL,
  summary text NOT NULL,
  status_code smallint NOT NULL
) ON COMMIT PRESERVE ROWS;

INSERT INTO bench_case
SELECT g,
       'SW-BENCH-' || lpad(g::text, 7, '0'),
       timestamptz '2020-01-01 00:00:00+00' + g * interval '3 hours',
       (g % 90)::smallint,
       'Synthetic case summary with reported circumstances, initial assessment, investigative context and linked subject references. Case ' || g || '.',
       (g % 6)::smallint
FROM generate_series(1, 2000) AS g;

CREATE INDEX bench_case_opened_idx ON bench_case(opened_at);

CREATE TEMP TABLE bench_incident (
  incident_id integer PRIMARY KEY,
  occurred_at timestamptz NOT NULL,
  location_text text NOT NULL,
  incident_type smallint NOT NULL,
  narrative text NOT NULL,
  linked_case_id integer REFERENCES bench_case(case_id)
) ON COMMIT PRESERVE ROWS;

INSERT INTO bench_incident
SELECT g,
       timestamptz '2021-01-01 00:00:00+00' + g * interval '90 minutes',
       'District ' || (g % 12) || ', Street ' || (g % 740),
       (g % 110)::smallint,
       'Synthetic incident narrative recording call details, attendance, observations, actions, persons present and outcome. Incident ' || g || '.',
       CASE WHEN g % 5 = 0 THEN ((g - 1) % 2000) + 1 ELSE NULL END
FROM generate_series(1, 10000) AS g;

CREATE INDEX bench_incident_time_idx ON bench_incident(occurred_at);
CREATE INDEX bench_incident_case_idx ON bench_incident(linked_case_id);

CREATE TEMP TABLE bench_evidence (
  evidence_id integer PRIMARY KEY,
  case_id integer NOT NULL REFERENCES bench_case(case_id),
  evidence_type smallint NOT NULL,
  description text NOT NULL,
  collected_at timestamptz NOT NULL,
  integrity_sha256 char(64) NOT NULL,
  custody_event_count smallint NOT NULL
) ON COMMIT PRESERVE ROWS;

INSERT INTO bench_evidence
SELECT g,
       ((g - 1) % 2000) + 1,
       (g % 40)::smallint,
       'Synthetic evidence metadata, exhibit description, recovery location, packaging and examination requirements. Exhibit ' || g || '.',
       timestamptz '2022-01-01 00:00:00+00' + g * interval '25 minutes',
       md5('saltwater-benchmark-evidence-' || g) || md5('saltwater-benchmark-integrity-' || g),
       (g % 12)::smallint
FROM generate_series(1, 10000) AS g;

CREATE INDEX bench_evidence_case_idx ON bench_evidence(case_id);
CREATE INDEX bench_evidence_collected_idx ON bench_evidence(collected_at);

CREATE TEMP TABLE bench_event (
  event_id bigint PRIMARY KEY,
  occurred_at timestamptz NOT NULL,
  event_type smallint NOT NULL,
  subject_person_id integer REFERENCES bench_person(person_id),
  location_text text NOT NULL,
  event_summary text NOT NULL,
  attributes jsonb NOT NULL
) ON COMMIT PRESERVE ROWS;

INSERT INTO bench_event
SELECT g,
       timestamptz '2018-01-01 00:00:00+00' + g * interval '12 minutes',
       (g % 180)::smallint,
       CASE WHEN g % 4 = 0 THEN ((g - 1) % 10000) + 1 ELSE NULL END,
       'District ' || (g % 12) || ', location ' || (g % 1600),
       'Synthetic longitudinal simulation event with timestamp, actor, subject, location, reason and recorded outcome. Event ' || g || '.',
       jsonb_build_object('source', 'synthetic-benchmark', 'sequence', g, 'severity', g % 5, 'resolved', (g % 2 = 0))
FROM generate_series(1, 150000) AS g;

CREATE INDEX bench_event_time_idx ON bench_event(occurred_at);
CREATE INDEX bench_event_subject_idx ON bench_event(subject_person_id);

ANALYZE bench_person;
ANALYZE bench_business;
ANALYZE bench_relationship;
ANALYZE bench_employment;
ANALYZE bench_case;
ANALYZE bench_incident;
ANALYZE bench_evidence;
ANALYZE bench_event;

\echo BENCHMARK_ROW_COUNTS
SELECT 'residents=' || count(*) FROM bench_person
UNION ALL SELECT 'businesses=' || count(*) FROM bench_business
UNION ALL SELECT 'relationships=' || count(*) FROM bench_relationship
UNION ALL SELECT 'employment_records=' || count(*) FROM bench_employment
UNION ALL SELECT 'cases=' || count(*) FROM bench_case
UNION ALL SELECT 'incidents=' || count(*) FROM bench_incident
UNION ALL SELECT 'evidence_metadata=' || count(*) FROM bench_evidence
UNION ALL SELECT 'historical_events=' || count(*) FROM bench_event;

\echo BENCHMARK_STORAGE_BY_TABLE
SELECT relname AS table_name,
       pg_relation_size(relid) AS heap_bytes,
       pg_indexes_size(relid) AS index_bytes,
       pg_total_relation_size(relid) AS total_bytes,
       round(pg_total_relation_size(relid)::numeric / 1000000, 3) AS total_mb
FROM pg_catalog.pg_statio_user_tables
WHERE schemaname LIKE 'pg_temp_%'
  AND relname LIKE 'bench_%'
ORDER BY pg_total_relation_size(relid) DESC;

\echo BENCHMARK_TOTAL
SELECT sum(pg_total_relation_size(relid)) AS total_relation_bytes,
       round(sum(pg_total_relation_size(relid))::numeric / 1000000, 3) AS total_relation_mb,
       sum(pg_relation_size(relid)) AS total_heap_bytes,
       sum(pg_indexes_size(relid)) AS total_index_bytes
FROM pg_catalog.pg_statio_user_tables
WHERE schemaname LIKE 'pg_temp_%'
  AND relname LIKE 'bench_%';

\echo BENCHMARK_COMPLETED_TEMPORARY_DATA_ONLY
