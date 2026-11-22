\set ON_ERROR_STOP on
\timing on

-- Saltwater narrative-quality fixture 0001.
-- Fictional, text-only, disposable PostgreSQL test. Never connect this file to Neon.
DROP SCHEMA IF EXISTS sw_narrative_quality CASCADE;
CREATE SCHEMA sw_narrative_quality;
SET search_path TO sw_narrative_quality, public;

CREATE TABLE fixture_entity (
  entity_id text PRIMARY KEY,
  entity_type text NOT NULL CHECK (entity_type IN ('person','place','organisation','exhibit')),
  display_label text NOT NULL,
  description text NOT NULL
);

CREATE TABLE fixture_record (
  record_id text PRIMARY KEY,
  record_type text NOT NULL,
  author_or_source text NOT NULL,
  event_at timestamptz,
  created_at timestamptz NOT NULL,
  provenance text NOT NULL,
  body text NOT NULL CHECK (length(trim(body)) >= 120)
);

CREATE TABLE record_link (
  from_record_id text NOT NULL REFERENCES fixture_record(record_id),
  to_record_id text NOT NULL REFERENCES fixture_record(record_id),
  link_type text NOT NULL,
  PRIMARY KEY (from_record_id,to_record_id,link_type),
  CHECK (from_record_id <> to_record_id)
);

CREATE TABLE record_entity_link (
  record_id text NOT NULL REFERENCES fixture_record(record_id),
  entity_id text NOT NULL REFERENCES fixture_entity(entity_id),
  relationship text NOT NULL,
  PRIMARY KEY(record_id,entity_id,relationship)
);

INSERT INTO fixture_entity VALUES
('P-OFFICER-01','person','PC Mara Venn','Attending patrol constable; authored the initial officer report.'),
('P-WITNESS-01','person','Elian Ward','Shop assistant who was at the front counter.'),
('P-WITNESS-02','person','Nadia Saye','Resident who observed the rear lane from an upstairs window.'),
('P-SUBJECT-01','person','Tomas Rell','Person arrested for investigation; allegation not treated as proof.'),
('P-EXAMINER-01','person','Dr Ivo Sen','Forensic examiner who conducted the submitted footwear comparison.'),
('L-STORE-01','place','Harbour Street Pharmacy','Fictional retail premises in Saltwater.'),
('L-REAR-01','place','Pharmacy rear service lane','Narrow service lane behind the premises.'),
('ORG-POLICE-01','organisation','Saltwater Police Service','Fictional police service.'),
('EX-01','exhibit','Exhibit SW-NQ-001','A sealed footwear impression lift recovered from the rear service threshold.'),
('EX-02','exhibit','Exhibit SW-NQ-002','A sealed fragment of clear polymer recovered beside the damaged rear latch.');

INSERT INTO fixture_record VALUES
('R-001','initial_incident_report','Emergency call intake; source CALL-2026-1014-2041','2026-10-14 20:38+00','2026-10-14 20:41+00','Call record CALL-2026-1014-2041; caller identity withheld in this test fixture.',
'At 20:38 on 14 October 2026, an emergency caller reported that the rear service door of Harbour Street Pharmacy appeared damaged and that a person had left through the rear lane. The caller did not claim to have seen entry into the premises. The caller described a sharp impact shortly before noticing the door damage. No injury was reported during the call. The information was treated as an unverified report pending police attendance.'),
('R-002','attending_officer_report','PC Mara Venn; service record SWP-00417','2026-10-14 20:52+00','2026-10-14 22:06+00','Officer notebook entry ON-417-14OCT; attendance log CAD-88421.',
'I arrived at Harbour Street Pharmacy at 20:52 and met the duty manager, who confirmed that the rear service door had not been secured as expected. I observed damage around the external latch and a clear polymer fragment on the ground immediately outside the threshold. I did not move the fragment. The rear lane was wet from recent rain. I established a short scene boundary and requested an evidence officer. The premises were checked with the manager; no person was found inside. I did not identify who caused the damage.'),
('R-003','witness_statement','Elian Ward; signed statement WS-01','2026-10-14 20:42+00','2026-10-14 22:18+00','Statement WS-01, taken by PC Venn; witness confirms own account.',
'I was working at the front counter when I heard a hard noise from the back of the shop at about 20:35. I looked toward the stockroom corridor but could not see the rear door from where I stood. A few moments later I saw someone cross the end of the corridor toward the staff exit. I only saw the person briefly and could not identify their face. I remember a red or rust-coloured upper garment, although the lighting was poor. I did not see anyone carrying property. I cannot say whether the person entered from outside or had already been in the building.'),
('R-004','witness_statement','Nadia Saye; signed statement WS-02','2026-10-14 20:44+00','2026-10-14 22:31+00','Statement WS-02, taken independently by PC Venn; witness confirms own account.',
'I was at the upstairs window overlooking the rear service lane. At approximately 20:44 I noticed a person moving away from the pharmacy rear door toward the junction. The person appeared to wear a dark blue jacket. I could not see the face because the person was looking down and the lane lighting is uneven. I did not see the person enter the pharmacy. I heard a metallic clatter but cannot place it precisely in time. I had no view of the shop interior and cannot say what, if anything, was taken.'),
('R-005','interview_transcript','Interviewing officer PC L. Oran; interviewee Tomas Rell','2026-10-15 10:14+00','2026-10-15 12:02+00','Audio-free written interview transcript INT-2026-771; checked and signed by interviewee with one correction noted.',
'Officer: Were you at Harbour Street Pharmacy on the evening of 14 October? Rell: I walked along Harbour Street after work, but I did not go into the pharmacy. Officer: Did you use the rear lane? Rell: No. Officer: A witness describes a person in a red or rust-coloured top near the staff corridor. Rell: That was not me; I had a navy coat. Officer: Did you hear a noise? Rell: I heard something like a bin lid when I was near the junction, but I cannot give you a time. Officer: Can you identify the person in either witness account? Rell: No. The interviewee corrected the recorded finish time from 10:08 to 10:14 after reviewing the transcript. No admission was made.'),
('R-006','evidence_register','Evidence officer PC D. Hale; register ER-2026-551','2026-10-14 21:16+00','2026-10-14 21:22+00','Evidence register ER-2026-551; recovery entries cross-referenced to officer report R-002.',
'Two items were separately packaged at the rear service threshold. SW-NQ-001 is a footwear impression lift taken from a damp surface approximately 0.6 metres outside the door. SW-NQ-002 is a clear polymer fragment recovered beside the damaged latch. The recovery positions were measured from the fixed door frame and entered in the scene notes. Neither item was attributed to a person at the scene. This fixture does not reproduce the package identifiers, individual seal numbers, receiving property officer's identity, transfer time or storage location. The register ER-2026-551 is cited as the source record, but those continuity particulars have not been independently verified in this sample; no uninterrupted chain of custody is asserted here.'),
('R-007','exhibit_description','Evidence officer PC D. Hale; exhibit description ED-001','2026-10-14 21:04+00','2026-10-14 21:25+00','Scene note SN-551-01 and evidence register ER-2026-551; linked exhibit EX-01.',
'Exhibit SW-NQ-001 consists of one gel lift showing a partial footwear impression. The impression was recovered from the damp concrete immediately outside the rear service threshold. The heel and part of the forefoot are visible; the central tread area is incomplete. The surface was exposed to rain and pedestrian traffic before police arrival. The lift was placed in a rigid protective sleeve, sealed, labelled and transferred to secure property storage. The impression does not, by itself, identify a wearer.'),
('R-008','exhibit_description','Evidence officer PC D. Hale; exhibit description ED-002','2026-10-14 21:07+00','2026-10-14 21:27+00','Scene note SN-551-02 and evidence register ER-2026-551; linked exhibit EX-02.',
'Exhibit SW-NQ-002 is a single clear polymer fragment, irregular in outline and approximately 18 millimetres at its widest point. It was located beside the external latch plate. The fragment was photographed in the scene notes before recovery; no image is stored in this text-only fixture. It was lifted with clean forceps, placed in a rigid container and sealed. Its material composition and whether it originated from the door assembly were not determined at the scene.'),
('R-009','forensic_submission','Case investigator PC L. Oran; submission FS-2026-118','2026-10-15 09:30+00','2026-10-15 09:42+00','Forensic submission FS-2026-118; exhibit seals verified on receipt.',
'The laboratory is asked to assess whether the partial footwear impression in SW-NQ-001 contains sufficient class characteristics for comparison with the reference footwear supplied under separate authority. The laboratory is also asked to describe the polymer fragment SW-NQ-002 and assess whether its composition is consistent with the submitted latch material. No request is made to identify a person. The submission records the scene conditions, recovery locations, packaging and seal identifiers.'),
('R-010','forensic_report','Dr Ivo Sen; laboratory report LAB-2026-883','2026-10-18 15:00+00','2026-10-18 16:12+00','Laboratory report LAB-2026-883; examination worksheet EXAM-883; seals intact on receipt.',
'The footwear lift contains a partial pattern with limited class features. The available area is insufficient for a reliable individual comparison, and the damp recovery surface may have affected detail. The polymer fragment was examined visually and by a non-destructive material screening method. Its characteristics are consistent with several common clear polymers; the results do not uniquely associate it with the pharmacy door. No individual identification or source attribution can be made from either exhibit. The limitations are material and should accompany any summary of these findings.'),
('R-011','intelligence_assessment','Intelligence analyst IA-22; assessment IA-2026-091','2026-10-15 08:00+00','2026-10-15 08:38+00','Source report SR-2026-441, graded low reliability; assessment version 1.',
'An uncorroborated source report states that a person matching Tomas Rell''s general build was seen near Harbour Street during the evening. The source could not provide a precise time and did not describe clothing. The report has not been independently corroborated and the source reliability is assessed as low. The information is recorded for context only; it does not establish that Rell was at the pharmacy or involved in the reported damage. No operational conclusion should rely on this source alone.'),
('R-012','surveillance_observation_log','Text observation officer SO-08; log SUR-2026-14','2026-10-14 20:30+00','2026-10-15 08:20+00','Written observation log SUR-2026-14; coverage plan CP-14; no video or image retained.',
'The written observation log records that the public street-facing entrance was visible from the authorised observation point between 20:30 and 20:55. The rear service lane was not continuously visible; a delivery vehicle obstructed the view from 20:40 to 20:45. At 20:46 an unidentified person was noted moving toward the junction, but the observer could not establish the person''s direction of travel before entering the visible area. No reliable facial description was obtained. The log distinguishes direct observation from the observer''s unverified interpretation.'),
('R-013','arrest_record','PC L. Oran; arrest record AR-2026-204','2026-10-16 09:22+00','2026-10-16 09:30+00','Arrest record AR-2026-204; decision review DR-204.',
'Tomas Rell was arrested at 09:22 on 16 October 2026 on suspicion of criminal damage and attempted burglary. The arrest record identifies the information said to be available at the time, including the differing witness descriptions and the uncorroborated, low-reliability intelligence report. The fixture does not reproduce the arresting officer's specific factual grounds or the case-specific reasons why arrest rather than voluntary attendance was considered necessary; the decision review DR-204 is cited but its reasoning is not included. Those grounds therefore cannot be evaluated from this sample. The footwear and polymer examination did not identify Rell and are not presented as grounds linking him to the incident.'),
('R-014','custody_record','Custody sergeant M. Pell; custody record CR-2026-204','2026-10-16 09:41+00','2026-11-03 09:10+00','Custody record CR-2026-204; booking entry at 09:49, detention review at 13:41, release and pre-charge bail entry at 17:10 on 16 October, and bail-cancellation update BC-204-03NOV entered at 09:05 on 3 November; consolidated at 09:10.',
'Rell arrived at the custody suite at 09:41 on 16 October. The custody sergeant recorded the arresting officer, stated grounds, booking time, property declaration, welfare questions and access to legal advice. Rell requested legal advice and the interview was not resumed until the recorded consultation had taken place. A review at 13:41 confirmed the continuing detention decision and recorded the reasons supplied. At 17:10 Rell was released on pre-charge police bail, with a return date of 10 November and a condition not to contact either named witness directly or indirectly. Following the prosecution review of 2 November, the investigating officer cancelled the bail and its conditions at 09:05 on 3 November; the cancellation was notified to Rell and entered in the custody record.'),
('R-015','legal_submission','Prosecution review lawyer A. Neri; review PS-2026-330','2026-11-02 14:00+00','2026-11-02 15:20+00','Prosecution review PS-2026-330; disclosed material schedule DS-330.',
'The review considers the two witness accounts, interview transcript, scene records, exhibit continuity and laboratory report. The clothing descriptions differ: one witness recalled red or rust, while the other recalled dark blue. Neither witness identifies Rell. The laboratory findings do not identify a wearer or establish the source of the polymer fragment. The intelligence report is low reliability and uncorroborated. The review records the allegation and evidential weaknesses separately and concludes that the current material does not provide a realistic basis for prosecution.'),
('R-016','court_outcome','Court registrar; disposition record COURT-2026-881','2026-11-10 10:00+00','2026-11-10 10:26+00','Court file COURT-2026-881; defence application APP-204-20OCT filed 20 October seeking variation of the pre-charge bail no-contact condition; custody/bail cancellation notice BC-204-03NOV; prosecution review PS-2026-330; hearing register and signed withdrawal notice.',
'The matter was listed on 10 November to hear Tomas Rell''s application, filed on 20 October, to vary the pre-charge bail condition prohibiting direct or indirect contact with the two named witnesses. The prosecution review dated 2 November concluded that the available evidence did not provide a realistic basis for prosecution. The investigating officer cancelled the pre-charge bail and all associated conditions on 3 November, and the cancellation was notified to Rell. At the hearing, Rell''s representative confirmed that the application was withdrawn because the condition was no longer in force. The court registrar recorded the withdrawal and closed the application without determining its merits. No prosecution had been commenced, no finding was made that Rell committed either alleged offence, and the police incident remains unresolved.');

INSERT INTO record_link VALUES
('R-001','R-002','attendance_follow_up'),
('R-002','R-003','witness_account'),
('R-002','R-004','witness_account'),
('R-003','R-004','accounts_to_compare'),
('R-002','R-006','scene_evidence_register'),
('R-006','R-007','exhibit_description'),
('R-006','R-008','exhibit_description'),
('R-007','R-009','forensic_submission'),
('R-008','R-009','forensic_submission'),
('R-009','R-010','forensic_result'),
('R-003','R-015','prosecution_review'),
('R-004','R-015','prosecution_review'),
('R-005','R-015','prosecution_review'),
('R-010','R-015','prosecution_review'),
('R-011','R-013','arrest_information_recorded'),
('R-012','R-015','coverage_limit_considered'),
('R-013','R-014','custody_booking'),
('R-014','R-015','case_disposal_context'),
('R-015','R-016','court_disposition');

INSERT INTO record_entity_link VALUES
('R-002','P-OFFICER-01','author'),
('R-002','L-STORE-01','attendance_location'),
('R-002','L-REAR-01','scene_area'),
('R-003','P-WITNESS-01','witness'),
('R-003','L-STORE-01','location'),
('R-004','P-WITNESS-02','witness'),
('R-004','L-REAR-01','observation_location'),
('R-005','P-SUBJECT-01','interviewee'),
('R-005','ORG-POLICE-01','interviewing_service'),
('R-006','EX-01','registered_exhibit'),
('R-006','EX-02','registered_exhibit'),
('R-007','EX-01','described_exhibit'),
('R-008','EX-02','described_exhibit'),
('R-009','EX-01','submitted_exhibit'),
('R-009','EX-02','submitted_exhibit'),
('R-010','P-EXAMINER-01','examiner'),
('R-010','EX-01','examined_exhibit'),
('R-010','EX-02','examined_exhibit'),
('R-011','P-SUBJECT-01','person_referenced'),
('R-012','L-REAR-01','observation_area'),
('R-013','P-SUBJECT-01','arrested_person'),
('R-014','P-SUBJECT-01','detained_person'),
('R-015','P-SUBJECT-01','person_reviewed'),
('R-016','P-SUBJECT-01','person_named');

-- Structural assertions: these are machine-checkable; narrative judgement remains manual.
DO $$
DECLARE
  n_records integer;
  n_links integer;
  bad_links integer;
  missing_provenance integer;
  bad_timestamps integer;
  distinct_witness_bodies integer;
BEGIN
  SELECT count(*) INTO n_records FROM fixture_record;
  IF n_records <> 16 THEN RAISE EXCEPTION 'Expected 16 records, found %',n_records; END IF;

  SELECT count(*) INTO n_links FROM record_link;
  IF n_links < 15 THEN RAISE EXCEPTION 'Expected at least 15 record links, found %',n_links; END IF;

  SELECT count(*) INTO bad_links
  FROM record_link l
  LEFT JOIN fixture_record a ON a.record_id=l.from_record_id
  LEFT JOIN fixture_record b ON b.record_id=l.to_record_id
  WHERE a.record_id IS NULL OR b.record_id IS NULL;
  IF bad_links <> 0 THEN RAISE EXCEPTION 'Unresolved record links: %',bad_links; END IF;

  SELECT count(*) INTO missing_provenance
  FROM fixture_record
  WHERE trim(author_or_source)='' OR trim(provenance)='' OR trim(body)='';
  IF missing_provenance <> 0 THEN RAISE EXCEPTION 'Records missing author/source, provenance or body: %',missing_provenance; END IF;

  SELECT count(*) INTO bad_timestamps
  FROM fixture_record
  WHERE event_at IS NOT NULL AND created_at < event_at;
  IF bad_timestamps <> 0 THEN RAISE EXCEPTION 'Record created before its stated event time: %',bad_timestamps; END IF;

  SELECT count(DISTINCT body) INTO distinct_witness_bodies
  FROM fixture_record WHERE record_type='witness_statement';
  IF distinct_witness_bodies <> 2 THEN RAISE EXCEPTION 'Witness statements are not distinct'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM fixture_record
    WHERE record_id='R-003' AND body ILIKE '%red or rust-coloured%'
  ) OR NOT EXISTS (
    SELECT 1 FROM fixture_record
    WHERE record_id='R-004' AND body ILIKE '%dark blue jacket%'
  ) THEN RAISE EXCEPTION 'Required unresolved clothing discrepancy is missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM fixture_record
    WHERE record_id='R-010' AND body ILIKE '%insufficient for a reliable individual comparison%'
  ) THEN RAISE EXCEPTION 'Forensic limitation is missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM fixture_record
    WHERE record_id='R-011' AND body ILIKE '%low%'
      AND body ILIKE '%independently corroborated%'
  ) THEN RAISE EXCEPTION 'Intelligence reliability/corroboration caveat is missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM fixture_record
    WHERE record_id='R-012' AND body ILIKE '%not continuously visible%'
  ) THEN RAISE EXCEPTION 'Surveillance coverage gap is missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM fixture_record
    WHERE record_id='R-016' AND body ILIKE '%police incident remains unresolved%'
  ) THEN RAISE EXCEPTION 'Unresolved outcome is missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM fixture_record
    WHERE record_id='R-006' AND body ILIKE '%individual seal numbers%'
      AND body ILIKE '%no uninterrupted chain of custody is asserted%'
  ) THEN RAISE EXCEPTION 'Evidence continuity omissions are not explicitly disclosed'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM fixture_record
    WHERE record_id='R-013' AND body ILIKE '%specific factual grounds%'
      AND body ILIKE '%cannot be evaluated from this sample%'
  ) THEN RAISE EXCEPTION 'Arrest necessity evidence gap is not explicitly disclosed'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM fixture_record intelligence
    JOIN fixture_record arrest ON arrest.record_id='R-013'
    WHERE intelligence.record_id='R-011'
      AND intelligence.created_at < arrest.event_at
  ) THEN RAISE EXCEPTION 'Intelligence assessment post-dates arrest decision'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM fixture_record arrest
    JOIN fixture_record custody ON custody.record_id='R-014'
    WHERE arrest.record_id='R-013'
      AND arrest.created_at < custody.event_at
  ) THEN RAISE EXCEPTION 'Arrest record was not created before custody booking'; END IF;
END $$;

-- Human review is deliberately pending; SQL cannot certify prose quality.
CREATE TABLE manual_review (
  record_id text PRIMARY KEY REFERENCES fixture_record(record_id),
  factual_grounding smallint CHECK (factual_grounding BETWEEN 0 AND 2),
  record_type_fit smallint CHECK (record_type_fit BETWEEN 0 AND 2),
  chronology smallint CHECK (chronology BETWEEN 0 AND 2),
  provenance smallint CHECK (provenance BETWEEN 0 AND 2),
  clarity smallint CHECK (clarity BETWEEN 0 AND 2),
  uncertainty smallint CHECK (uncertainty BETWEEN 0 AND 2),
  non_duplication smallint CHECK (non_duplication BETWEEN 0 AND 2),
  reviewer_notes text,
  review_status text NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending','pass','fail'))
);
INSERT INTO manual_review(record_id)
SELECT record_id FROM fixture_record ORDER BY record_id;

\echo NARRATIVE_QUALITY_RECORD_SUMMARY
SELECT record_type,count(*) AS records,
       sum(octet_length(body)) AS raw_utf8_bytes,
       sum(array_length(regexp_split_to_array(trim(body),'\s+'),1)) AS approximate_words
FROM fixture_record GROUP BY record_type ORDER BY record_type;

\echo NARRATIVE_QUALITY_LINKS
SELECT link_type,count(*) AS links FROM record_link GROUP BY link_type ORDER BY link_type;

\echo NARRATIVE_QUALITY_MANUAL_REVIEW_STATUS
SELECT review_status,count(*) AS records FROM manual_review GROUP BY review_status;

\echo NARRATIVE_QUALITY_SAMPLE
SELECT record_id,record_type,author_or_source,event_at,created_at,provenance,body
FROM fixture_record ORDER BY record_id;

\echo NARRATIVE_QUALITY_STORAGE
SELECT pg_database_size(current_database()) AS database_bytes,
       sum(pg_total_relation_size(c.oid)) AS relation_bytes,
       sum(pg_relation_size(c.oid)) AS heap_bytes,
       sum(pg_indexes_size(c.oid)) AS index_bytes,
       sum(pg_total_relation_size(c.oid)-pg_relation_size(c.oid)-pg_indexes_size(c.oid)) AS toast_aux_bytes
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='sw_narrative_quality' AND c.relkind='r';
