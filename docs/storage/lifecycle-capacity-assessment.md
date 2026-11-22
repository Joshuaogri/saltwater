# Saltwater lifecycle storage-capacity assessment

Status: 1 GB capacity NOT APPROVED pending realistic text-depth benchmark 0006. No production data has been seeded.

## 1. Verified starting point

On 2026-11-22, GitHub Actions workflow `Neon connection and storage baseline` completed successfully against the Neon database `neondb`.

- Database size: 7,790,592 bytes
- Decimal size: 7.791 MB (1 MB = 1,000,000 bytes)
- Workflow run: https://github.com/Joshuaogri/saltwater/actions/runs/45047512732
- This is a measured database baseline, not a forecast and not proof that the 1 GB allowance is sufficient.
- The baseline workflow did not apply the Saltwater foundation migration.
- No production population, business, case, evidence or other simulation seed data has been loaded.

## 2. Capacity decision gate

Do not load production-scale simulation data until a measured benchmark and lifecycle projection support a capacity decision.

The decision must be one of:
1. **1 GB sufficient** for the explicitly defined lifecycle, with a documented reserve; or
2. **1 GB insufficient**, with a quantified capacity target and an alternative architecture or plan.

A small initial database, a row-count estimate alone, or a generic PostgreSQL rule of thumb is not sufficient evidence.

## 3. Scope to include

The benchmark must represent the full 10,000-resident, one-city-state world and the deep police simulation.

### World and population
- Exactly 10,000 living residents at the hard population ceiling.
- Individual identities and persistent biographies.
- Households, families, relationships, contacts, addresses, residences and movement history.
- Employment, education, businesses, organisations and institutional affiliations.
- Deaths, departures, replacements and historical identity links.

### City and institutions
- Districts, streets, junctions, addresses, buildings and properties.
- At least 10,000 businesses, with ownership, premises, staff, opening patterns and operational history.
- Government, ministries, legislature, courts, prosecution, corrections, healthcare, education, emergency services, finance and other institutions.
- Organisational structures, personnel, facilities and inter-agency records.

### Police service
- Personnel, recruitment, training, ranks, positions, units, rosters, deployments and discipline.
- Calls, dispatch, patrol, incidents, reports and operational logs.
- Victims, witnesses, suspects, persons of interest and their persistent histories.
- Investigations, leads, interviews, intelligence, surveillance, warrants, arrests and custody.
- Evidence items, chain of custody, forensic submissions, examinations and results.
- Case files, court referrals, proceedings, outcomes and linked records.

### Longitudinal history
- Time-stamped changes and events over the defined game lifecycle.
- Relationships and employment changes, address history, business changes, institutional changes and police activity.
- Corrections, superseded records, audit/provenance and recovery information.
- Retention and archival policy, including whether old records remain online, are compressed, or are moved to another storage tier.

## 4. Benchmark method

1. Record a fresh database-size measurement before applying the foundation migration.
2. Apply the migration using a controlled, repeatable process.
3. Measure database size immediately after migration and record the net change.
4. Generate a synthetic benchmark dataset with realistic distributions and representative text lengths. Do not use real personal data.
5. Load the benchmark in measured stages: core world, residents/relationships, city/businesses, institutions, police personnel, operational activity, cases/evidence, and longitudinal history.
6. Measure database size after every stage using `pg_database_size(current_database())`; also measure table, index and TOAST contributions using PostgreSQL catalog/statistics queries.
7. Record submitted payload bytes separately from actual database growth.
8. Repeat important batches to measure duplicate handling and idempotency.
9. Test query performance and index overhead at target scale.
10. Project the defined lifecycle from measured per-record and per-event costs, including growth, indexes, TOAST, metadata, WAL implications where relevant, and a safety reserve.
11. Re-run the benchmark after schema or compression changes; compare measured results.

All measurements use decimal MB: 1 MB = 1,000,000 bytes. Preserve raw byte counts as the authoritative values.

## 5. Storage accounting

For each upload, import or bulk migration, record:
- Original input bytes and MB.
- Compressed input bytes and MB, where compression is used.
- Submitted/transfer bytes and MB.
- Database size immediately before and after.
- Net database growth in bytes and MB.
- Compression percentage, where meaningful.
- Counts of inserted, updated, skipped and deduplicated records.
- Measurement timestamp, operation identifier, migration/version and notes.

Never equate compressed transfer size with PostgreSQL storage growth. Database growth includes table data, indexes, TOAST and PostgreSQL overhead. If a value cannot be measured, mark it unavailable; do not estimate it as if measured.

## 6. Text-only records

Saltwater is entirely text-based. It stores no photographs, audio, CCTV footage, body-camera footage, video, scanned documents, binary attachments or other binary media. No external object-storage tier is part of the design or capacity calculation.

Evidence, interviews, surveillance, dispatch, forensic examinations, reports and court records are represented through written descriptions, transcripts, metadata, chronologies, reports, provenance and links to other text records. Any former media-reference benchmark tables are excluded from the text-only workload.

## 7. Efficiency principles

- Normalise stable entities and shared facts; reference them rather than duplicating them.
- Use compact surrogate identifiers where useful.
- Store repeated labels in dictionaries/reference tables.
- Use event/delta records for changing facts when this preserves complete reconstruction.
- Use JSONB for genuinely variable attributes, not as a replacement for relational design.
- Avoid excessive indexes; measure the storage and query benefit of each.
- Partition only when measured scale and query patterns justify it.
- Consider compression and archival only after testing CPU, storage, query and recovery trade-offs.
- Deduplicate identical payloads using content hashes where appropriate.
- Preserve provenance, chronology, identity resolution and full recoverability. Storage savings must not erase meaningful simulation detail.

## 8. Historical decision — superseded

The original integrated relational benchmark's conditional 1 GB approval was withdrawn after the text-only lifecycle workload was added. See Sections 17–18 and benchmark run 0006 for the current decision.

## 9. Required final report

The capacity report must state:
- Defined game lifecycle and retention assumptions.
- Benchmark dataset counts and generation rules.
- Measured baseline and post-migration size.
- Measured bytes per representative entity/event category.
- Table, index and TOAST storage breakdown.
- Measured raw text bytes, PostgreSQL heap/index/TOAST bytes and text-search index overhead; binary payload volume is zero by design.
- Projected lifecycle total, with assumptions clearly separated from measurements.
- Safety reserve and expected headroom.
- Whether 1 GB is sufficient; if not, the required alternative capacity.
- Reproducible SQL, scripts, test outputs and commit references.

## 10. Benchmark stage 2 — institutional and police lifecycle (2026-11-22)

The extended synthetic benchmark completed successfully (1,034,842 rows across 24 temporary tables):
- Workflow run: https://github.com/Joshuaogri/saltwater/actions/runs/45049121196
- Benchmark report: [benchmark-run-0002.md](benchmark-run-0002.md)
- Tested commit: `4accdd8ba88174176a2e357f4b886e4ffc381db2`
- Measured heap: 245,047,296 bytes (245.047 MB)
- Measured indexes: 61,792,256 bytes (61.792 MB)
- Total temporary relation footprint: 307,052,544 bytes (307.053 MB)
- PostgreSQL `ANALYZE`: completed successfully.

Largest categories: interviews (50.766 MB), police reports (44.573 MB), dispatch actions (41.140 MB), commercial transactions (34.447 MB), intelligence (28.705 MB), and patrol events (28.189 MB).

The 466,944-byte difference between database-size readings around the session is not the temporary dataset's storage cost. Temporary relations were removed when the connection closed; use the 307.053 MB relation measurement for this benchmark.

**Capacity status remains NOT APPROVED.** The benchmark is synthetic and temporary, and does not include complete biographies, all business/institutional history, every police workflow or binary media.

## 11. Benchmark stage 3 — combined persistent lifecycle (2026-11-22)

The combined persistent benchmark completed successfully:
- Workflow run: https://github.com/Joshuaogri/saltwater/actions/runs/45049960061
- Benchmark report: [benchmark-run-0003.md](benchmark-run-0003.md)
- Persistent benchmark tables: 32
- Exact generated-row total: 1,276,842 (stage 0001: 242,000; stage 0002: 1,034,842)
- Heap: 304,529,408 bytes (304.529 MB)
- Indexes: 76,201,984 bytes (76.202 MB)
- TOAST/auxiliary: 483,328 bytes (0.483 MB)
- **Relation footprint: 381,214,720 bytes (381.215 MB)**
- Full database while benchmark was present: 390,832,128 bytes (390.832 MB) on the exact-count rerun
- Database before benchmark: 9,347,072 bytes (9.347 MB)
- Database after cleanup: 9,617,408 bytes (9.617 MB)
- All 32 benchmark tables were dropped.

The direct count audit is authoritative; the `pg_stat_user_tables.n_live_tup` estimate differed by 42,000. The 0.270 MB post-cleanup residual is not the benchmark dataset footprint.

This stage remains incomplete: biographies and histories are simplified; many government, service and police workflows are sampled or missing; simulation duration is not fixed; binary media is not included.

**Capacity status remains NOT APPROVED.**

## 12. Benchmark stage 3 exact-count rerun — verified (2026-11-22)

- Workflow run: https://github.com/Joshuaogri/saltwater/actions/runs/45050714671
- Tested commit: `71beee01cb4794b56f8b15d50940f157b5ebeba4`
- Exact count across all 32 tables: **1,276,842 rows**.
- Database before: 9,347,072 bytes (9.347 MB).
- Relation footprint: 381,214,720 bytes (381.215 MB): heap 304.529 MB, indexes 76.202 MB, TOAST/auxiliary 0.483 MB.
- Full database during benchmark: 390,832,128 bytes (390.832 MB).
- Database after cleanup: 9,617,408 bytes (9.617 MB); residual vs pre-run: 270,336 bytes (0.270 MB).
- Report: [benchmark-run-0003.md](benchmark-run-0003.md).

This confirms exact row counts but not complete lifecycle coverage. **1 GB remains NOT APPROVED.**

## 13. Benchmark stage 4 — longitudinal world and police records (verified 2026-11-22)

Stage 4 completed successfully against Neon:
- Workflow run: https://github.com/Joshuaogri/saltwater/actions/runs/45052214555
- Tested commit: `7413ce7fa0e75f672c99a9d1266f2ff6131bc6ed`
- Report: [benchmark-run-0004.md](benchmark-run-0004.md)
- 15 benchmark tables plus one exact-count audit table were created and subsequently removed.
- Exact audited total: **600,560 rows** across the 15 benchmark tables.
- Relation heap: 133,021,696 bytes (133.022 MB).
- Relation indexes: 33,185,792 bytes (33.186 MB).
- TOAST/auxiliary: 507,904 bytes (0.508 MB).
- **Stage 4 relation footprint: 166,715,392 bytes (166.715 MB).**
- Full database before benchmark: 9,355,264 bytes (9.355 MB).
- Full database while benchmark present: 176,185,344 bytes (176.185 MB).
- Full database after cleanup: 9,469,952 bytes (9.470 MB).
- Cleanup log confirms all 16 objects were dropped.

The 114,688-byte difference between database size after cleanup and before the run is not the benchmark dataset footprint. Use the measured 166.715 MB relation total.

Stage 4 adds household profiles/memberships, resident address and life-event history, business staffing and transactions, public organisations/office history, public-service encounters, education, police training/discipline, radio communications, forensic examinations and legal proceedings. Its synthetic dates span up to 35 years, but this is not an approved simulation duration or event-rate assumption.

**Do not simply add stage 4's 166.715 MB to stage 3's 381.215 MB:** the benchmark scopes overlap in several categories, and the datasets are synthetic. Reconcile overlap and complete missing categories before calculating a combined lifecycle projection.

## 14. Historical remaining work — superseded after text-only correction

- Select and test external object storage for the measured 1,950.015 MB of binary media references.
- Treat the 35-year integrated workload as the current planning scenario; explicitly approve a different lifetime/retention horizon before changing the forecast.
- Keep the 200 MB Neon reserve protected and monitor actual database growth.
- Test backup/recovery, archival, media integrity, retention and representative query performance.
- Re-run the integrated benchmark if event rates, text lengths, indexes, evidence volume or retention scope materially increase.

The relational capacity decision is recorded in Section 16. Production media ingestion remains blocked until the separate media tier is operational and verified.


## 15. Historical integrated lifecycle benchmark and conditional 1 GB decision (2026-11-22) — superseded

The four earlier stages have now been reconciled into one coherent synthetic dataset. The benchmark does not sum duplicate stage footprints or repeat stable entities. It uses one 10,000-resident population, one 10,000-business population, shared geographic/institutional/police/case/evidence identifiers, and one consolidated history per overlapping category.

Validation:
- PostgreSQL 16 GitHub Actions run: https://github.com/Joshuaogri/saltwater/actions/runs/45052956900
- Commit: `960528fa97c80d31295419095d9f6a9b5e0db896`
- 54 data tables; exact total **2,516,342 rows**.
- Heap: 439,623,680 bytes (439.624 MB).
- Indexes: 131,866,624 bytes (131.867 MB).
- TOAST/auxiliary: 1,908,736 bytes (1.909 MB).
- Integrated relation footprint: **573,399,040 bytes (573.399 MB)**.
- Referenced media: 30,000 assets representing 1,950,015,000 bytes (1,950.015 MB) of payload. This is excluded from PostgreSQL and must be stored separately.
- All 54 data tables plus the exact-count audit table were removed after validation.

The consolidated schema includes institutional/office and public-service records; healthcare, social services, education and foreign relations; bank accounts, financial ledger and tax records; police personnel, shifts, training, discipline, CAD, dispatch, patrol, reports, radio and GPS; cases, incidents, interviews, intelligence and links, surveillance, warrants, arrests, custody, evidence, custody events, forensic examinations, prosecution, legal proceedings, corrections and media references.

Planning arithmetic (decimal MB):
- Integrated relation footprint: 573.399 MB.
- Last measured Neon post-cleanup baseline: 9.470 MB.
- Indicative occupied total: 582.869 MB.
- 1 GB allowance: 1,000 MB.
- Protected 20% reserve: 200 MB.
- Indicative headroom beyond reserve: 217.131 MB.

**Conditional capacity decision: 1 GB is sufficient for the defined integrated relational benchmark only if binary media is kept outside Neon and the 200 MB reserve is protected.** It is not sufficient if the 1.95 GB of referenced binary media is stored inside Neon, and it is not an unlimited-growth guarantee.

The Neon-specific integrated workflow is prepared at https://github.com/Joshuaogri/saltwater/actions/workflows/storage-benchmark-integrated.yml. It must be run once to capture Neon database size before/during/after and confirm the actual Neon footprint. Until that run confirms the reserve, production seeding remains blocked. The 35-year benchmark is a planning scenario, not a newly approved canon game-duration rule.

Report: [benchmark-run-0005.md](benchmark-run-0005.md).


## 16. Historical Neon integrated benchmark — measured decision (2026-11-22) — superseded

The integrated 0005 benchmark was successfully executed against the actual Neon database:
- Run: https://github.com/Joshuaogri/saltwater/actions/runs/45053385138
- Commit: `7621b19eb6ad540ff0407576d8c33938cfbc8909`
- Exact total: **2,516,342 rows** across 54 data tables.
- Relation footprint: **569,417,728 bytes (569.418 MB)**.
- Full database before: **9,281,536 bytes (9.282 MB)**.
- Full database during: **579,084,288 bytes (579.084 MB)**.
- Full database after cleanup: **9,666,560 bytes (9.667 MB)**.
- Net post-cleanup difference: **385,024 bytes (0.385 MB)**; not the benchmark dataset footprint.
- Database after storage-ledger insert: **9,666,560 bytes (9.667 MB)**.
- Measurement was recorded in `sw_ops.storage_operation`; SQL-generated synthetic data has no original/compressed/submitted file payload.
- 30,000 external media references represent **1,950,015,000 bytes (1,950.015 MB)** of media payload, excluded from Neon.

### Final 1 GB decision

**YES — 1 GB is sufficient for the defined 35-year integrated relational workload, provided binary media is stored outside Neon and a 200 MB reserve is protected.**

Actual Neon budget:
- Database occupied during the integrated test: 579.084 MB.
- Capacity: 1,000 MB.
- Remaining capacity: 420.916 MB.
- Protected reserve: 200 MB.
- Further headroom after reserve: **220.916 MB**.

**NO** if full binary media is to be stored inside Neon: the benchmark references 1,950.015 MB of binary payload alone. This is also not an unlimited-growth guarantee; any material increase in event rates, text sizes, indexes or retention scope requires another measurement.

The 35-year dates are a benchmark planning scenario, not a change to the game's canon or a mandatory retirement/lifespan rule. Keep production seeding blocked until the separate media-storage tier is chosen and tested, and preserve the 200 MB Neon reserve.


## 17. Text-only capacity decision reset and benchmark 0006

The earlier conditional 1 GB approval in Sections 15–16 is **withdrawn**. It measured the 0005 integrated relational workload but did not include realistic full-length written reports, witness statements, interviews, evidence descriptions, forensic reports, legal submissions, judgments or cumulative long-running case histories.

Saltwater is entirely text-based. It stores no photographs, audio, CCTV footage, body-camera footage, video, scanned documents, binary attachments or other binary media. No external media/object-storage tier is part of the design or capacity calculation. The 0006 benchmark removes the 0005 media-asset, CCTV-observation-reference and body-worn-video-reference tables before measuring.

## 18. Benchmark 0006 — measured text-depth result (2026-11-22)

Two independent PostgreSQL 16.16 disposable benchmark runs completed successfully:
- Run 1: https://github.com/Joshuaogri/saltwater/actions/runs/45055330210
- Run 2: https://github.com/Joshuaogri/saltwater/actions/runs/45055343838
- Full report: [benchmark-run-0006-text-depth.md](benchmark-run-0006-text-depth.md)
- SQL: [0006_text_depth_lifecycle_benchmark.sql](../../db/benchmarks/0006_text_depth_lifecycle_benchmark.sql)
- Workflow: [storage-benchmark-text-depth.yml](../../.github/workflows/storage-benchmark-text-depth.yml)

### Exact workload

- Residents: 10,000.
- Businesses: 10,000.
- Text documents: **237,000**.
- Generated text: **283,702,825 words**.
- Raw UTF-8 text: **2,081,698,917 bytes (2,081.699 MB)**.
- Integrated total: **2,653,342 rows**.
- Cases with linked text: 2,000.
- Case-history words: minimum 64,716; median 111,245.5; p95 309,125.05; maximum 752,119.

### Measured disposable PostgreSQL storage

| Measurement | Run 1 | Run 2 |
|---|---:|---:|
| Full database | 1,149.173 MB | 1,149.353 MB |
| Relation footprint | 1,140.179 MB | 1,140.318 MB |
| Heap | 762.233 MB | not separately recorded |
| Indexes | 207.716 MB | not separately recorded |
| TOAST/auxiliary | 170.230 MB | not separately recorded |

The text_record table alone occupied **588.087 MB** in Run 1. It held 237,000 written documents and 283.7 million words. Its storage comprised 339.091 MB heap, 80.650 MB indexes and 168.346 MB TOAST/auxiliary. The full relation footprint also includes the 10,000-resident world, 10,000 businesses, institutions, finance, police operations and other lifecycle records.

The sample full-text query returned 50 rows in 42.881 ms on the disposable PostgreSQL instance. The observed plan used a sequential scan; search-index selection and performance require further tuning.

### Capacity decision

**The defined 0006 benchmark workload does not fit within a 1 GB project.** The full disposable database occupied approximately 1,149 MB before any Neon measurement, and the relation footprint exceeded the 790 MB pre-Neon safety gate. The workflow therefore skipped the Neon load. This protected the live Neon project; no benchmark data was inserted into it and no Neon storage was consumed by this test.

The 200 MB reserve was not met. The earlier 1 GB approval is no longer valid for this workload.

**Important interpretation:** this result does not prove that 10,000 residents alone require more than 1 GB, and it does not establish that reducing the resident population would solve the problem. The result is driven by the chosen volume of long-form text records and case histories as well as the underlying world data. The benchmark assigned 237,000 text documents across 2,000 cases, resulting in a median linked case history of 111,245.5 words and a maximum of 752,119 words. Those prevalence and distribution assumptions must be calibrated before making a population decision.

### Next step

Retain the 10,000-resident and 10,000-business design targets. Build a calibrated lifecycle workload that:
- Defines realistic annual case volumes and the prevalence of minor, ordinary, serious, major and exceptional cases.
- Assigns interviews, reports, witness statements, evidence and court documents according to case type rather than distributing high volumes uniformly by modulo.
- Preserves the proposed maximum document lengths and full case-history reconstruction.
- Avoids storing duplicate narrative content while retaining separate authored reports and transcripts where they represent distinct records.
- Measures raw text, PostgreSQL compression, heap, indexes, TOAST, search performance and full database size.
- Runs on disposable PostgreSQL first; Neon is tested only if the disposable result leaves at least 200 MB of nominal capacity in reserve.

**Current decision: 1 GB is NOT APPROVED for the 0006 workload. The 10,000-resident target remains unchanged pending a calibrated second benchmark. Production seeding remains blocked.**
