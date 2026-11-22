\set ON_ERROR_STOP on
\timing on

-- Saltwater calibrated text lifecycle benchmark 0008.
-- Synthetic, text-only, 10,000 residents and 10,000 businesses.
-- The 35-year date span is a sizing scenario, not a gameplay-duration rule.
\ir 0005_integrated_lifecycle_capacity_benchmark.sql

SET search_path TO sw_bench_integrated, public;

-- No binary media or media-reference schema in Saltwater.
DROP TABLE IF EXISTS media_asset_metadata CASCADE;
DROP TABLE IF EXISTS cctv_observation CASCADE;
DROP TABLE IF EXISTS body_worn_video_reference CASCADE;
DELETE FROM benchmark_exact_counts
WHERE table_name IN ('media_asset_metadata','cctv_observation','body_worn_video_reference');

-- The prose generator uses deterministic combinatorial vocabulary selection and
-- type-specific sentence framing. It is deliberately much less compressible
-- than the finite phrase bank used in 0007, while remaining reproducible.
-- High-entropy generator: deterministic combinations of broad vocabularies and
-- record-type-specific sentence frames. No small finite prose-template bank.
CREATE OR REPLACE FUNCTION make_calibrated_prose(p_words integer, p_seed bigint, p_kind text)
RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE AS $function$
WITH vocab AS (
  SELECT
    ARRAY['attending officer','case investigator','scene examiner','records clerk','custody sergeant','forensic analyst','reporting person','independent witness','prosecution advocate','court registrar','intelligence analyst','patrol supervisor','property officer','medical practitioner','dispatch operator','interviewing officer','technical specialist','reviewing inspector','community liaison officer','evidence coordinator']::text[] AS actors,
    ARRAY['recorded','observed','examined','confirmed','queried','compared','preserved','transferred','reviewed','described','identified','requested','received','reconciled','challenged','clarified','documented','assessed','disclosed','retained','located','measured','reported','explained']::text[] AS verbs,
    ARRAY['the sequence of events','the condition of the premises','the account provided at interview','the location and packaging of the exhibit','the available entry and exit information','the timing of the reported contact','the relationship between linked records','the limits of the examination','the basis for the operational decision','the identity attributed to the source','the custody and handling history','the material difference between accounts','the response to the formal request','the context of the observed activity','the chronology in the original notes','the status of the outstanding enquiry','the grounds stated in the application','the findings reached after review','the accuracy of the supplied particulars','the route by which the information arrived']::text[] AS subjects,
    ARRAY['during the initial attendance','before the record was finalised','after checking the contemporaneous entry','within the stated review period','in the presence of the authorised recipient','without altering the original account','against the independently held reference','subject to the stated examination limits','following the recorded supervisory review','at the location identified in the source','using the procedure noted in the file','with the unresolved point expressly retained','after the relevant person was contacted','under the authority recorded for the action','as part of the continuing chronology','before the material was disclosed','on the date and time shown in the register','with the source attribution preserved','after the discrepancy was put to the author','for the purpose specified in the request']::text[] AS qualifiers,
    ARRAY['The account distinguishes direct knowledge from information attributed to another source.','The original entry remains unchanged and this record is linked as a separate addition.','The time is recorded as supplied and has not been independently verified.','The available material does not resolve the difference between the two descriptions.','The author identifies the basis of the conclusion and the limits of the available information.','The record preserves the sequence in which the material was received and handled.','No inference is drawn beyond the observations and documents expressly described.','The response is recorded in the terms received, including any qualification or correction.','The reviewer considered the alternative explanation and retained the outstanding issue.','The relevant reference is linked so that the source can be retrieved without duplicating it.','The entry records what was done, who was responsible and when the action occurred.','The distinction between an allegation, an observation and an established fact is maintained.']::text[] AS caveats
),
sentences AS (
 SELECT n,
   (v.actors[1+mod(abs(hashtextextended(p_seed::text||':'||n||':a',0)),cardinality(v.actors))::int]
    ||' '||
    v.verbs[1+mod(abs(hashtextextended(p_seed::text||':'||n||':v',0)),cardinality(v.verbs))::int]
    ||' '||
    v.subjects[1+mod(abs(hashtextextended(p_seed::text||':'||n||':s',0)),cardinality(v.subjects))::int]
    ||' '||
    v.qualifiers[1+mod(abs(hashtextextended(p_seed::text||':'||n||':q',0)),cardinality(v.qualifiers))::int]
    ||'. '||
    v.caveats[1+mod(abs(hashtextextended(p_seed::text||':'||n||':c',0)),cardinality(v.caveats))::int]) AS sentence
 FROM vocab v CROSS JOIN generate_series(1,GREATEST(1,CEIL(p_words/47.0)::int)) n
),
typed AS (
 SELECT n,
 CASE p_kind
  WHEN 'witness_statement' THEN 'The witness account records that '
  WHEN 'interview_transcript' THEN 'The interview record notes that '
  WHEN 'evidence_description' THEN 'The exhibit description records that '
  WHEN 'forensic_report' THEN 'The examination report states that '
  WHEN 'intelligence_report' THEN 'The assessment records that '
  WHEN 'surveillance_observation' THEN 'The observation log records that '
  WHEN 'court_judgment' THEN 'The court gives its reasons as follows: '
  WHEN 'legal_submission' THEN 'The submission addresses the following material: '
  WHEN 'custody_record' THEN 'The custody record notes that '
  WHEN 'arrest_record' THEN 'The arrest record states that '
  ELSE 'The '||replace(p_kind,'_',' ')||' records that '
 END || sentence AS sentence
 FROM sentences
),
raw AS (SELECT string_agg(sentence,' ' ORDER BY n) AS prose FROM typed),
tokens AS (
 SELECT token,ord FROM raw
 CROSS JOIN LATERAL regexp_split_to_table(raw.prose,'\s+') WITH ORDINALITY t(token,ord)
)
SELECT string_agg(token,' ' ORDER BY ord) FROM tokens WHERE ord<=p_words;
$function$;

CREATE TABLE text_record (
  text_record_id bigserial PRIMARY KEY,
  record_type text NOT NULL,
  source_id bigint NOT NULL,
  case_id integer,
  resident_id integer,
  created_at timestamptz NOT NULL,
  word_count integer NOT NULL CHECK(word_count>0),
  body text NOT NULL,
  UNIQUE(record_type,source_id)
);

-- A 35-year synthetic scenario: 2,000 cases (~57/year). Document counts are
-- deliberately weighted by case workflow, not sprayed across every case.
-- Each generated document is a distinct authored record; no aggregate case
-- narrative is duplicated into this table.

-- Initial incident reports: one for each of 2,000 case-linked incidents.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'initial_incident_report',i.incident_id,i.case_id,i.occurred_at,
       450+(i.incident_id%451),
       make_calibrated_prose(450+(i.incident_id%451),i.incident_id,'initial_incident_report')
FROM incident i WHERE i.case_id IS NOT NULL;

-- Police reports: 3,000 full reports, distributed over cases.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'police_report',p.report_id,((p.report_id-1)%2000+1)::integer,p.submitted_at,
       CASE WHEN p.report_id%10=0 THEN 1800+(p.report_id%1201) ELSE 500+(p.report_id%701) END,
       make_calibrated_prose(CASE WHEN p.report_id%10=0 THEN 1800+(p.report_id%1201) ELSE 500+(p.report_id%701) END,p.report_id,'police_report')
FROM police_report p WHERE p.report_id%20=0;

-- Supplementary reports: 2,000, usually one per case.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'supplementary_report',g,((g-1)%2000+1)::integer,
       timestamptz '1991-01-01 00:00:00+00'+g*interval '4 days',
       250+(g%501),make_calibrated_prose(250+(g%501),g,'supplementary_report')
FROM generate_series(1,2000) g;

-- Witness statements: 4,000 records, with longer statements in a minority.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'witness_statement',g,((g-1)%2000+1)::integer,
       timestamptz '1991-01-01 00:00:00+00'+g*interval '5 days',
       CASE WHEN g%10=0 THEN 2500+(g%1501) ELSE 400+(g%801) END,
       make_calibrated_prose(CASE WHEN g%10=0 THEN 2500+(g%1501) ELSE 400+(g%801) END,g,'witness_statement')
FROM generate_series(1,4000) g;

-- Interviews: 5,000 transcripts, typically two or three per case.
INSERT INTO text_record(record_type,source_id,case_id,resident_id,created_at,word_count,body)
SELECT 'interview_transcript',v.interview_id,v.case_id,v.resident_id,v.interviewed_at,
       CASE WHEN v.interview_id%100=0 THEN 25000
            WHEN v.interview_id%10=0 THEN 6000+(v.interview_id%4001)
            ELSE 1200+(v.interview_id%1801) END,
       make_calibrated_prose(CASE WHEN v.interview_id%100=0 THEN 25000
            WHEN v.interview_id%10=0 THEN 6000+(v.interview_id%4001)
            ELSE 1200+(v.interview_id%1801) END,v.interview_id,'interview_transcript')
FROM interview_record v WHERE v.interview_id%6=0;

-- Written evidence descriptions: 8,000 exhibits.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'evidence_description',e.evidence_id,e.case_id,e.collected_at,
       150+(e.evidence_id%351),
       make_calibrated_prose(150+(e.evidence_id%351),e.evidence_id,'evidence_description')
FROM evidence_item e WHERE e.evidence_id<=8000;

-- Forensic reports: 2,000 examinations.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'forensic_report',f.examination_id,f.case_id,f.examined_at,
       CASE WHEN f.examination_id%10=0 THEN 2500+(f.examination_id%1501) ELSE 600+(f.examination_id%901) END,
       make_calibrated_prose(CASE WHEN f.examination_id%10=0 THEN 2500+(f.examination_id%1501) ELSE 600+(f.examination_id%901) END,f.examination_id,'forensic_report')
FROM forensic_examination f WHERE f.examination_id%10=0;

-- Intelligence reports: 1,000 case-linked written assessments.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'intelligence_report',g,((g-1)%2000+1)::integer,
       timestamptz '1991-01-01 00:00:00+00'+g*interval '11 days',
       400+(g%1001),make_calibrated_prose(400+(g%1001),g,'intelligence_report')
FROM generate_series(1,1000) g;

-- Surveillance: 1,500 written observation logs.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'surveillance_observation',s.surveillance_id,s.case_id,s.started_at,
       150+(s.surveillance_id%551),
       make_calibrated_prose(150+(s.surveillance_id%551),s.surveillance_id,'surveillance_observation')
FROM surveillance_record s WHERE s.surveillance_id<=1500;

-- Arrest/custody records: 1,000 of each, reflecting a subset of cases.
INSERT INTO text_record(record_type,source_id,case_id,resident_id,created_at,word_count,body)
SELECT 'arrest_record',a.arrest_id,a.case_id,a.resident_id,a.arrested_at,
       350+(a.arrest_id%651),make_calibrated_prose(350+(a.arrest_id%651),a.arrest_id,'arrest_record')
FROM arrest a WHERE a.arrest_id<=1000;

INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'custody_record',c.custody_id,((c.custody_id-1)%2000+1)::integer,c.booked_at,
       350+(c.custody_id%651),make_calibrated_prose(350+(c.custody_id%651),c.custody_id,'custody_record')
FROM custody_record c WHERE c.custody_id<=1000;

-- Legal submissions: 1,500. Court judgments: 500.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'legal_submission',g,((g-1)%2000+1)::integer,
       timestamptz '1991-01-01 00:00:00+00'+g*interval '8 days',
       CASE WHEN g%10=0 THEN 5000+(g%3001) ELSE 1200+(g%1801) END,
       make_calibrated_prose(CASE WHEN g%10=0 THEN 5000+(g%3001) ELSE 1200+(g%1801) END,g,'legal_submission')
FROM generate_series(1,1500) g;

INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'court_judgment',g,((g-1)%2000+1)::integer,
       timestamptz '1991-01-01 00:00:00+00'+g*interval '15 days',
       CASE WHEN g%100=0 THEN 50000 WHEN g%10=0 THEN 12000+(g%8001) ELSE 2500+(g%3501) END,
       make_calibrated_prose(CASE WHEN g%100=0 THEN 50000 WHEN g%10=0 THEN 12000+(g%8001) ELSE 2500+(g%3501) END,g,'court_judgment')
FROM generate_series(1,500) g;

-- Personnel: compact, distinct career records for the 250 officers.
INSERT INTO text_record(record_type,source_id,created_at,word_count,body)
SELECT 'personnel_record',p.officer_id,
       timestamptz '1990-01-01 00:00:00+00'+p.officer_id*interval '30 days',
       300+(p.officer_id%1201),
       make_calibrated_prose(300+(p.officer_id%1201),p.officer_id,'personnel_record')
FROM police_personnel p;

-- Preserve the exceptional long-running history as linked dated events,
-- without imposing a global case-history ceiling or duplicating aggregates.
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'major_case_history_event',g,1,
       timestamptz '2000-01-01 00:00:00+00'+g*interval '1 day',
       1000,make_calibrated_prose(1000,g,'major_case_history_event')
FROM generate_series(1,250) g;
INSERT INTO text_record(record_type,source_id,case_id,created_at,word_count,body)
SELECT 'exceptional_case_history_event',g,2,
       timestamptz '1995-01-01 00:00:00+00'+g*interval '1 day',
       1000,make_calibrated_prose(1000,g,'exceptional_case_history_event')
FROM generate_series(1,500) g;

CREATE INDEX text_record_case_time_idx ON text_record(case_id,created_at);
CREATE INDEX text_record_resident_idx ON text_record(resident_id) WHERE resident_id IS NOT NULL;
CREATE INDEX text_record_search_gin_idx ON text_record USING gin(to_tsvector('english',body));

CREATE VIEW case_history_word_totals AS
SELECT case_id,count(*)::bigint AS linked_document_count,
       sum(word_count)::bigint AS cumulative_words,
       sum(octet_length(body))::bigint AS raw_text_bytes
FROM text_record WHERE case_id IS NOT NULL GROUP BY case_id;

INSERT INTO benchmark_exact_counts(table_name,exact_rows)
VALUES ('text_record',(SELECT count(*) FROM text_record));

ANALYZE;

\echo CALIBRATED_TEXT_RECORD_DISTRIBUTION
SELECT record_type,count(*) documents,min(word_count) min_words,
       round(avg(word_count)::numeric,1) average_words,
       percentile_cont(0.95) WITHIN GROUP(ORDER BY word_count) p95_words,
       max(word_count) max_words,sum(word_count)::bigint total_words,
       sum(octet_length(body))::bigint raw_text_bytes
FROM text_record GROUP BY record_type ORDER BY record_type;

\echo CALIBRATED_TEXT_TOTALS
SELECT count(*) text_documents,sum(word_count)::bigint total_words,
       sum(octet_length(body))::bigint raw_text_bytes,
       round(sum(octet_length(body))::numeric/1000000,3) raw_text_mb
FROM text_record;

\echo CALIBRATED_CASE_HISTORY_DISTRIBUTION
SELECT count(*) cases_with_text,min(cumulative_words) minimum_case_words,
       percentile_cont(0.50) WITHIN GROUP(ORDER BY cumulative_words) median_case_words,
       percentile_cont(0.95) WITHIN GROUP(ORDER BY cumulative_words) p95_case_words,
       max(cumulative_words) maximum_case_words,max(raw_text_bytes) largest_case_raw_text_bytes
FROM case_history_word_totals;

\echo CALIBRATED_STORAGE_TOTAL
SELECT sum(pg_relation_size(c.oid)) heap_bytes,
       sum(pg_indexes_size(c.oid)) index_bytes,
       sum(pg_total_relation_size(c.oid)-pg_relation_size(c.oid)-pg_indexes_size(c.oid)) toast_aux_bytes,
       sum(pg_total_relation_size(c.oid)) relation_total_bytes,
       round(sum(pg_total_relation_size(c.oid))::numeric/1000000,3) relation_total_mb
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='sw_bench_integrated' AND c.relkind='r';

\echo CALIBRATED_TEXT_TABLE_STORAGE
SELECT pg_relation_size('sw_bench_integrated.text_record') heap_bytes,
       pg_indexes_size('sw_bench_integrated.text_record') index_bytes,
       pg_total_relation_size('sw_bench_integrated.text_record') total_bytes,
       round(pg_total_relation_size('sw_bench_integrated.text_record')::numeric/1000000,3) total_mb;

\echo HIGH_ENTROPY_TEXT_SEARCH_PLAN
SET enable_seqscan=off;
EXPLAIN(ANALYZE,BUFFERS)
SELECT text_record_id FROM text_record
WHERE to_tsvector('english',body) @@ plainto_tsquery('english','forensic exhibit transfer')
LIMIT 50;
RESET enable_seqscan;

\echo TEXT_ENTROPY_SAMPLE
SELECT count(*) sampled_documents,count(DISTINCT left(body,240)) distinct_openings,
       round(count(DISTINCT left(body,240))::numeric/count(*)*100,2) distinct_opening_pct
FROM (SELECT body FROM text_record ORDER BY text_record_id LIMIT 1000) sample;

\echo CALIBRATED_EXACT_ROW_TOTAL
SELECT sum(exact_rows)::bigint exact_total_rows FROM benchmark_exact_counts;
