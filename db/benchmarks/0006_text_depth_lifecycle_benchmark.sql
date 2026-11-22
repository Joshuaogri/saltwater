\set ON_ERROR_STOP on
\timing on

-- Saltwater text-depth lifecycle benchmark 0006.
-- Reuses the integrated synthetic world from 0005, then removes every
-- binary-media/reference-only table and adds realistic-length textual records.
-- No production records or binary payloads are created.

\ir 0005_integrated_lifecycle_capacity_benchmark.sql

SET search_path TO sw_bench_integrated, public;

-- Saltwater is text-only: remove media, CCTV-footage and body-worn-video
-- reference tables. Written surveillance records remain as text.
DROP TABLE IF EXISTS media_asset_metadata CASCADE;
DROP TABLE IF EXISTS cctv_observation CASCADE;
DROP TABLE IF EXISTS body_worn_video_reference CASCADE;
DELETE FROM benchmark_exact_counts
WHERE table_name IN ('media_asset_metadata','cctv_observation','body_worn_video_reference');

-- Generate varied, sentence-based text with unique record/paragraph references.
-- The word count is exact; this is synthetic prose, not copied personal data.
CREATE OR REPLACE FUNCTION make_prose(p_words integer, p_seed bigint, p_kind text)
RETURNS text
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $function$
WITH bank(phrases) AS (
  VALUES (ARRAY[
    'The attending officer recorded reference %s-%s while documenting the initial circumstances and people present.',
    'The account describes the sequence of events, the location involved and the actions reported by each participant.',
    'The available information was compared with contemporaneous notes, recorded timings and the accounts obtained during enquiries.',
    'The writer distinguished direct observations from information supplied by another person and identified any remaining uncertainty.',
    'The chronology was checked against the recorded arrival time, subsequent actions and the time the matter was concluded.',
    'The description identifies the relevant property, its condition, the recovery location and the circumstances in which it was found.',
    'Each material decision is recorded with its reason, the information available at the time and the person responsible.',
    'The record notes differences between accounts without treating an unresolved discrepancy as an established fact.',
    'Relevant actions were entered in sequence so that another reviewer can reconstruct what occurred and when it occurred.',
    'The account identifies the source of each assertion and records whether supporting information was independently obtained.',
    'The officer noted environmental conditions, access arrangements, visibility and other circumstances that could affect interpretation.',
    'The record includes the enquiries completed, the responses received and any action that remained outstanding at that stage.',
    'The statement was checked with its author, and any clarification was recorded without changing the original account.',
    'The assessment considers alternative explanations and explains which points remain unverified or require further examination.',
    'The document records the handling history, identifying references, transfers and checks relevant to continuity and integrity.',
    'The supervisor reviewed the entry for completeness, internal consistency, correct attribution and compliance with recording standards.',
    'The account separates established facts, reported information, professional assessment and matters that remain disputed.',
    'The final entry records the outcome known at the time and identifies the records linked to this investigation.',
    'The interview record preserves the questions, answers, clarifications, pauses and material changes in the account.',
    'The examination report describes the method used, observations made, limitations identified and conclusions supported by the results.',
    'The investigative decision records the available grounds, the proportionality considered and the reasons for the chosen action.',
    'The case chronology links this event to earlier records while preserving the original date, author and source of information.',
    'The witness account records what the person says they perceived and distinguishes recollection from later information.',
    'The record identifies persons contacted, the purpose of contact, the response received and any agreed follow-up.',
    'The review found that the material was legible, attributable and linked to the correct incident and case references.',
    'The author records the relevant context so that the entry can be understood without relying on an undocumented conversation.',
    'The decision was made on the information then available and may be reconsidered if materially different evidence emerges.',
    'The entry preserves the original account and records subsequent corrections as separate, dated amendments with provenance.'
  ]::text[])
),
raw AS (
  SELECT string_agg(
    format(
      phrases[1 + mod(p_seed + n * 7919 + abs(hashtext(p_kind)::bigint), cardinality(phrases))::integer],
      p_seed::text, n::text
    ),
    ' ' ORDER BY n
  ) AS prose
  FROM bank
  CROSS JOIN generate_series(1, GREATEST(1, CEIL(p_words / 8.0)::integer)) AS n
),
tokens AS (
  SELECT token, ord
  FROM raw
  CROSS JOIN LATERAL regexp_split_to_table(raw.prose, '\s+') WITH ORDINALITY AS t(token, ord)
)
SELECT string_agg(token, ' ' ORDER BY ord)
FROM tokens
WHERE ord <= p_words;
$function$;

CREATE TABLE text_record (
  text_record_id bigserial PRIMARY KEY,
  record_type text NOT NULL,
  source_id bigint NOT NULL,
  case_id integer,
  resident_id integer,
  created_at timestamptz NOT NULL,
  word_count integer NOT NULL CHECK (word_count > 0),
  body text NOT NULL,
  UNIQUE (record_type, source_id)
);

-- Initial incident reports: routine and complex lengths.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'initial_incident_report', incident_id, COALESCE(case_id, ((incident_id-1)%2000+1)::integer),
       occurred_at, words, make_prose(words,incident_id,'initial_incident_report')
FROM (
  SELECT incident_id, case_id, occurred_at,
         CASE WHEN incident_id%10=0 THEN 1500+(incident_id%1501)
              ELSE 300+(incident_id%501) END AS words
  FROM incident
) q;

-- Full officer reports, plus separate supplementary reports.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'police_report', report_id, ((report_id-1)%2000+1)::integer,
       submitted_at, words, make_prose(words,report_id,'police_report')
FROM (
  SELECT report_id,submitted_at,
         CASE WHEN report_id%10=0 THEN 1500+(report_id%1501)
              ELSE 300+(report_id%501) END AS words
  FROM police_report
) q;

INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'supplementary_report', g, ((g-1)%2000+1)::integer,
       timestamptz '1991-01-01 00:00:00+00'+g*interval '7 hours', words,
       make_prose(words,g,'supplementary_report')
FROM (
  SELECT g,
         CASE WHEN g%10=0 THEN 1000+(g%1501)
              ELSE 200+(g%401) END AS words
  FROM generate_series(1,20000) g
) q;

-- Witness statements: predominantly routine, with a complex minority.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'witness_statement', g, ((g-1)%2000+1)::integer,
       timestamptz '1991-01-01 00:00:00+00'+g*interval '9 hours', words,
       make_prose(words,g,'witness_statement')
FROM (
  SELECT g,
         CASE WHEN g%20 IN (0,1,2) THEN 2000+(g%3001)
              ELSE 300+(g%701) END AS words
  FROM generate_series(1,20000) g
) q;

-- Interview transcripts: routine, complex and exceptional-length interviews.
INSERT INTO text_record(record_type,source_id,case_id,resident_id,created_at,word_count,body)
SELECT 'interview_transcript', interview_id, case_id, resident_id,
       interviewed_at, words, make_prose(words,interview_id,'interview_transcript')
FROM (
  SELECT interview_id,case_id,resident_id,interviewed_at,
         CASE WHEN interview_id%100=0 THEN 25000
              WHEN interview_id%100 BETWEEN 86 AND 99 THEN 5000+(interview_id%7001)
              ELSE 1000+(interview_id%2001) END AS words
  FROM interview_record
) q;

-- Evidence descriptions: written descriptions only; no image/audio/video payload.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'evidence_description', evidence_id, case_id, collected_at, words,
       make_prose(words,evidence_id,'evidence_description')
FROM (
  SELECT evidence_id,case_id,collected_at,
         CASE WHEN evidence_id%10=0 THEN 500+(evidence_id%1001)
              ELSE 100+(evidence_id%301) END AS words
  FROM evidence_item
) q;

-- Forensic examination reports.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'forensic_report', examination_id, case_id, examined_at, words,
       make_prose(words,examination_id,'forensic_report')
FROM (
  SELECT examination_id,case_id,examined_at,
         CASE WHEN examination_id%20=0 THEN 2000+(examination_id%3001)
              ELSE 500+(examination_id%1001) END AS words
  FROM forensic_examination
) q;

-- Intelligence reports.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'intelligence_report', intelligence_id, ((intelligence_id-1)%2000+1)::integer,
       created_at, words, make_prose(words,intelligence_id,'intelligence_report')
FROM (
  SELECT intelligence_id,created_at,
         CASE WHEN intelligence_id%10=0 THEN 2000+(intelligence_id%3001)
              ELSE 300+(intelligence_id%701) END AS words
  FROM intelligence_report
) q;

-- Written surveillance observations and logs only.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'surveillance_observation', surveillance_id, case_id, started_at, words,
       make_prose(words,surveillance_id,'surveillance_observation')
FROM (
  SELECT surveillance_id,case_id,started_at,
         CASE WHEN surveillance_id%10=0 THEN 1000+(surveillance_id%2001)
              ELSE 100+(surveillance_id%401) END AS words
  FROM surveillance_record
) q;

-- Arrest and custody written records.
INSERT INTO text_record(record_type,source_id,case_id,resident_id,created_at,word_count,body)
SELECT 'arrest_record', arrest_id, case_id, resident_id, arrested_at, words,
       make_prose(words,arrest_id,'arrest_record')
FROM (
  SELECT arrest_id,case_id,resident_id,arrested_at,
         CASE WHEN arrest_id%10=0 THEN 1000+(arrest_id%1001)
              ELSE 300+(arrest_id%501) END AS words
  FROM arrest
) q;

INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'custody_record', custody_id, ((custody_id-1)%2000+1)::integer,
       booked_at, words, make_prose(words,custody_id,'custody_record')
FROM (
  SELECT custody_id,booked_at,
         CASE WHEN custody_id%10=0 THEN 1000+(custody_id%1001)
              ELSE 300+(custody_id%501) END AS words
  FROM custody_record
) q;

-- Legal submissions and court judgments.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'legal_submission', g, ((g-1)%2000+1)::integer,
       timestamptz '1991-01-01 00:00:00+00'+g*interval '3 days', words,
       make_prose(words,g,'legal_submission')
FROM (
  SELECT g,
         CASE WHEN g%5=0 THEN 5000+(g%10001)
              ELSE 1000+(g%2001) END AS words
  FROM generate_series(1,10000) g
) q;

INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'court_judgment', g, ((g-1)%2000+1)::integer,
       timestamptz '1991-01-01 00:00:00+00'+g*interval '5 days', words,
       make_prose(words,g,'court_judgment')
FROM (
  SELECT g,
         CASE WHEN g%100=0 THEN 50000
              WHEN g%10=0 THEN 10000+(g%15001)
              ELSE 1000+(g%4001) END AS words
  FROM generate_series(1,2000) g
) q;

-- Personnel career records.
INSERT INTO text_record(record_type,source_id,created_at,word_count,body)
SELECT 'personnel_record', officer_id, timestamptz '1990-01-01 00:00:00+00'+officer_id*interval '30 days',
       words, make_prose(words,officer_id,'personnel_record')
FROM (
  SELECT officer_id,
         CASE WHEN officer_id%20=0 THEN 1000+(officer_id%2001)
              ELSE 200+(officer_id%601) END AS words
  FROM police_personnel
) q;

-- Two linked, dated case-history stress examples: one major (250k words)
-- and one exceptional (500k words), stored as event narratives, not a
-- duplicated aggregate narrative.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'case_history_event_major', g, 1,
       timestamptz '2000-01-01 00:00:00+00'+g*interval '1 day',
       1000, make_prose(1000,g,'case_history_event_major')
FROM generate_series(1,250) g;

INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'case_history_event_exceptional', g, 2,
       timestamptz '1995-01-01 00:00:00+00'+g*interval '1 day',
       1000, make_prose(1000,g,'case_history_event_exceptional')
FROM generate_series(1,500) g;

CREATE INDEX text_record_case_time_idx ON text_record(case_id,created_at);
CREATE INDEX text_record_resident_idx ON text_record(resident_id) WHERE resident_id IS NOT NULL;
CREATE INDEX text_record_search_gin_idx ON text_record USING gin (to_tsvector('english',body));

CREATE VIEW case_history_word_totals AS
SELECT case_id, count(*)::bigint AS linked_document_count,
       sum(word_count)::bigint AS cumulative_words,
       sum(octet_length(body))::bigint AS raw_text_bytes
FROM text_record
WHERE case_id IS NOT NULL
GROUP BY case_id;

INSERT INTO benchmark_exact_counts(table_name,exact_rows)
VALUES ('text_record',(SELECT count(*) FROM text_record));

ANALYZE;

\echo TEXT_DEPTH_RECORD_DISTRIBUTION
SELECT record_type,count(*) AS documents,
       min(word_count) AS min_words,
       round(avg(word_count)::numeric,1) AS average_words,
       percentile_cont(0.95) WITHIN GROUP (ORDER BY word_count) AS p95_words,
       max(word_count) AS max_words,
       sum(word_count)::bigint AS total_words,
       sum(octet_length(body))::bigint AS raw_text_bytes
FROM text_record
GROUP BY record_type
ORDER BY record_type;

\echo TEXT_DEPTH_TOTALS
SELECT count(*) AS text_documents,
       sum(word_count)::bigint AS total_words,
       sum(octet_length(body))::bigint AS raw_text_bytes,
       round(sum(octet_length(body))::numeric/1000000,3) AS raw_text_mb
FROM text_record;

\echo CASE_HISTORY_DISTRIBUTION
SELECT count(*) AS cases_with_text,
       min(cumulative_words) AS minimum_case_words,
       percentile_cont(0.50) WITHIN GROUP (ORDER BY cumulative_words) AS median_case_words,
       percentile_cont(0.95) WITHIN GROUP (ORDER BY cumulative_words) AS p95_case_words,
       max(cumulative_words) AS maximum_case_words,
       max(raw_text_bytes) AS largest_case_raw_text_bytes
FROM case_history_word_totals;

\echo TEXT_DEPTH_EXACT_ROW_TOTAL
SELECT sum(exact_rows)::bigint AS exact_total_rows FROM benchmark_exact_counts;

\echo TEXT_DEPTH_STORAGE_BY_TABLE
SELECT c.relname AS table_name,
       pg_relation_size(c.oid) AS heap_bytes,
       pg_indexes_size(c.oid) AS index_bytes,
       pg_total_relation_size(c.oid)-pg_relation_size(c.oid)-pg_indexes_size(c.oid) AS toast_aux_bytes,
       pg_total_relation_size(c.oid) AS total_bytes,
       round(pg_total_relation_size(c.oid)::numeric/1000000,3) AS total_mb
FROM pg_class c
JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='sw_bench_integrated' AND c.relkind='r'
ORDER BY pg_total_relation_size(c.oid) DESC;

\echo TEXT_DEPTH_STORAGE_TOTAL
SELECT sum(pg_relation_size(c.oid)) AS heap_bytes,
       sum(pg_indexes_size(c.oid)) AS index_bytes,
       sum(pg_total_relation_size(c.oid)-pg_relation_size(c.oid)-pg_indexes_size(c.oid)) AS toast_aux_bytes,
       sum(pg_total_relation_size(c.oid)) AS relation_total_bytes,
       round(sum(pg_total_relation_size(c.oid))::numeric/1000000,3) AS relation_total_mb
FROM pg_class c
JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='sw_bench_integrated' AND c.relkind='r';

\echo TEXT_SEARCH_QUERY_PLAN
EXPLAIN (ANALYZE,BUFFERS)
SELECT text_record_id
FROM text_record
WHERE to_tsvector('english',body) @@ plainto_tsquery('english','officer recorded witness account')
LIMIT 50;
