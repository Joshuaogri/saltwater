# Saltwater record narrative-quality benchmark plan

Status: fixture implemented; automated structural and chronology validation passed on disposable PostgreSQL. Manual narrative review remains pending. No production records or Neon data are loaded.

## Purpose

Benchmark 0008 measures a deterministic, high-entropy text workload. It does not establish that generated records read like coherent police, forensic, custody or court documents. This test separates narrative quality from storage volume.

## Fixed scope

- Entirely fictional Saltwater simulation.
- Text only. No images, audio, CCTV/BWC media, scans, video or binary attachments.
- Use a small, manually authored, internally linked scenario to test record quality; do not inflate word counts with repeated filler.
- Keep the 10,000-resident and 10,000-business world assumptions unchanged.
- This is a quality fixture, not a new production case or a change to simulation canon.
- Do not insert the fixture into Neon. Run validation locally or on disposable PostgreSQL first.

## Record set

Create one coherent fictional incident with stable test-only IDs and a defined event chronology. Include at least:

1. Initial incident report.
2. Attending officer's contemporaneous report.
3. Two independent witness statements with distinct knowledge and wording.
4. One interview transcript with questions, answers, clarifications and explicit uncertainty.
5. Evidence register entries and written exhibit descriptions.
6. Forensic submission and examination report, with method, limitations and results.
7. Intelligence assessment that separates sourced information from inference.
8. Surveillance observation log represented only as text observations and metadata.
9. Arrest and custody records, including decision times and responsible personnel.
10. Legal submission and reasoned court outcome.

The fixture must include ordinary, serious and unresolved facts, including at least one discrepancy that remains unresolved. Do not silently reconcile conflicting accounts or turn allegations into established facts.

## Required quality assertions

- Every record has a unique stable ID, record type, author/source, created time, event time where applicable, and provenance.
- Referenced people, locations, exhibits and linked records resolve to valid fixture entities.
- Event chronology is internally possible; event time and record-creation time are distinct.
- Each record type follows its own document structure and purpose.
- Witnesses speak only to what they could reasonably perceive or know; statements are not cloned or paraphrased copies.
- Interview transcript preserves question/answer order, corrections, pauses or uncertainty where relevant; it does not invent admissions.
- Evidence descriptions identify the item, condition, packaging, recovery context and handling links without asserting forensic conclusions prematurely.
- Forensic reports distinguish submission questions, methods, observations, results, limitations and interpretation.
- Intelligence distinguishes source reporting, reliability, corroboration, assessment and unknowns.
- Surveillance logs distinguish direct observation from interpretation and record coverage gaps.
- Arrest/custody records preserve grounds as recorded, times, decision-maker and subsequent actions.
- Legal records distinguish allegation, evidence, finding, reasoning and disposition.
- Contradictions remain visible and traceable; no unsupported facts are introduced to make the story smoother.
- No repeated generic filler sentences or artificial word-count padding.
- Cross-record consistency is checked without requiring every account to agree.

## Scoring and release gate

Score each record 0–2 for: factual grounding, record-type fit, chronology, provenance, internal clarity, appropriate uncertainty and non-duplication.

- 0: absent, misleading or materially defective.
- 1: present but incomplete or weak.
- 2: clear and fit for purpose.

A record passes at 11/14 or higher, with no zero for chronology, provenance or appropriate uncertainty. The complete scenario passes only if all records pass, all links resolve, and no critical contradiction is silently erased.

Review the sample manually as well as running deterministic structural assertions. Automated checks cannot certify naturalness, fairness, evidential reasoning or legal quality.

## Storage measurement

After quality passes, use the same text records as a small representative storage fixture:

- Record original UTF-8 bytes per document and in total.
- Measure PostgreSQL heap, indexes, TOAST/auxiliary and full database before and after.
- Record row counts and text word counts.
- Measure query latency for case chronology, person history, exhibit chain and full-text retrieval.
- Record exact SQL, generator/source revision, run ID and raw byte counts.
- Distinguish the small quality fixture from the 33,500-document capacity workload. Do not extrapolate from a tiny sample without a separately justified model.

## Approval boundary

Passing this test establishes only that the sampled record workflow meets the stated quality criteria. It does not by itself approve 1 GB Neon capacity, production seeding, the full 10,000-person lifecycle, or every possible case category. Capacity approval still requires measured representative volume, performance, Neon accounting and a protected storage reserve.


## Implemented fixture 0001

- SQL fixture: `db/benchmarks/0009_narrative_quality_fixture.sql`.
- Disposable CI workflow: `.github/workflows/narrative-quality-fixture.yml`.
- Fictional scenario: reported damage at Harbour Street Pharmacy, Saltwater, on 14 October 2026.
- 16 linked records spanning call intake, attending officer, two independent witness statements, interview transcript, evidence register, two exhibit descriptions, forensic submission/report, intelligence assessment, text-only surveillance log, arrest, custody, prosecution review and court disposition.
- 10 test entities and explicit record-to-record/entity links.
- The two witness accounts retain a material clothing-description discrepancy; the forensic findings remain limited; the intelligence source remains low-reliability and uncorroborated; surveillance coverage gaps remain explicit; the final disposition does not identify a perpetrator.
- Automated checks validate record count, link integrity, provenance presence, event/creation chronology, distinct witness text, and preservation of selected uncertainty/limitation statements.
- The workflow runs only on disposable PostgreSQL 16. It has no Neon credentials or Neon connection path.
- A manual review row is created for every record with status `pending`. SQL does not assign review scores or claim human review has passed.

### Validation boundary

A green CI run will mean the fixture loads and its structural assertions pass. It will not mean the 16 records have passed the 0–2 human quality rubric. The next quality step is to review every record against the rubric, record scores and reviewer notes, and fail the fixture if any record scores below 11/14 or receives zero for chronology, provenance or uncertainty. Only after that review should this same fixture be used for a measured small-scale storage/query test. No Neon writes are permitted.


### First automated validation result

- Successful run: https://github.com/Joshuaogri/saltwater/actions/runs/45062664898
- Commit tested: `de036d620f010fa6f4abb1962cd29513784c67fa`.
- 16 records, 19 record links, 10 entities.
- All 16 manual-review rows remained `pending`.
- No media/image/audio/video/CCTV/body-worn-video tables were present.
- Raw UTF-8 narrative text: **8,525 bytes** (approximately 1,351 whitespace-delimited words).
- Diagnostic relation footprint: **196,608 bytes**; heap 49,152 bytes; indexes 81,920 bytes; TOAST/auxiliary 65,536 bytes.
- Disposable database size after fixture creation: **8,109,079 bytes**.

These storage figures are diagnostic measurements from the first structurally passing version, not a final before/after storage experiment and not capacity evidence. A subsequent editorial chronology review found that the intelligence assessment was dated after the arrest despite being cited in the arrest decision. The fixture was corrected so the assessment precedes the arrest, the arrest record is created before custody booking, and explicit assertions guard both orderings. The corrected run must pass before the fixture is considered structurally stable.


### Corrected chronology validation

- Successful corrected run: https://github.com/Joshuaogri/saltwater/actions/runs/45062795840
- Tested commit: `a7bcdd11096092dbf56ff360b5d57ebc1ad03f5a`.
- The intelligence assessment is now recorded before the arrest decision that references it.
- The arrest record is recorded before custody booking.
- Explicit SQL assertions enforce both chronology relationships.
- The workflow completed successfully, including the 16-record, 19-link, 10-entity, 16-pending-review and zero-media-table checks.

The earlier successful run 45062664898 is superseded for chronology purposes. The fixture's automated structure is now stable, but its narrative quality is not yet approved: the 16 human-review scores remain pending. The next task is to complete a record-by-record editorial review against the seven-part 0–2 rubric, preserve any unresolved weaknesses as review notes, and only then decide whether to accept the fixture for the small-scale storage/query experiment.


### AI-assisted editorial review — 22 November 2026

- Review: `docs/storage/narrative-quality-editorial-review-0001.md`.
- The 16 records were scored individually against the seven-part rubric. Fourteen meet the numeric threshold; R-016 fails at 10/14 because the court application and procedural disposition are not sufficiently identified.
- R-014's record-creation timestamp was corrected in `db/benchmarks/0009_narrative_quality_fixture.sql`: the consolidated custody record is now created at 17:18, after the 17:10 release entry. The booking, review and disposal chronology is retained.
- R-003, R-005, R-006–R-010, R-012 and R-013 have specific improvement notes in the review document. R-006 and R-013 are borderline passes.
- This is an AI-assisted editorial assessment, not independent human sign-off. The 16 SQL `manual_review` rows remain pending; do not change them to passed on the strength of this assessment.
- Overall fixture release status remains **NOT APPROVED** until R-016 is repaired and the complete record set receives human sign-off. No Neon writes or production seeding.


### Revised court/custody narrative — 22 November 2026

- R-014 now records release on pre-charge police bail on 16 October, a return date of 10 November, a no-contact condition concerning the two named witnesses, and cancellation of bail and its conditions on 3 November after the prosecution review. The consolidated custody/bail record is timestamped after the cancellation entry.
- R-016 now identifies the 20 October defence application to vary the no-contact condition. It records that the condition had already been cancelled on 3 November, so the application was withdrawn as moot at the 10 November hearing. The court closes the application without deciding its merits or making any finding about the alleged offences.
- Updated editorial assessment: `docs/storage/narrative-quality-editorial-review-0001.md`. All 16 records now meet the numeric threshold in the revised AI-assisted assessment; R-006 and R-013 remain borderline and specific quality improvements are outstanding.
- The fixture is conditionally ready for independent human sign-off, **not approved**. Database manual-review rows remain pending. No Neon writes or production seeding.
