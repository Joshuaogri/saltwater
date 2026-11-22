# Saltwater record narrative-quality benchmark plan

Status: fixture implemented; automated structural validation passed once on disposable PostgreSQL. A follow-up run is validating chronology refinements. Manual narrative review remains pending. No production records or Neon data are loaded.

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
