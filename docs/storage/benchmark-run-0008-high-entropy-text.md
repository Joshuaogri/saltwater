# High-entropy text lifecycle benchmark — run 0008

Status: **first disposable run passed; clean text-only repeat is running**. This benchmark is not a Neon import and does not authorize production seeding.

## Purpose

Benchmark 0008 repeats the calibrated 0007 workload with a deterministic, higher-entropy prose generator. It combines broad actor, action, subject, qualifier and caveat vocabularies with record-type-specific framing. Selection is seeded by document and sentence position so runs are reproducible without relying on a small fixed paragraph bank.

## Fixed workload

- Residents: 10,000.
- Businesses: 10,000.
- Cases: 2,000 in a 35-year sizing scenario (not a gameplay-duration rule).
- Text documents: 33,500.
- Integrated rows: 2,449,842.
- Binary media, CCTV footage and body-camera reference tables: excluded.
- Benchmark data: disposable PostgreSQL 16 only; no Neon writes.

## First-run measured results

Successful GitHub Actions run: https://github.com/Joshuaogri/saltwater/actions/runs/45058337044

| Measure | Result |
|---|---:|
| Full disposable database | 651.722 MB |
| Total relation footprint | 642.720 MB |
| Heap | 457.146 MB |
| Indexes | 138.838 MB |
| TOAST and auxiliary | 46.735 MB |
| Raw UTF-8 text | 244.366 MB |
| Text documents | 33,500 |
| Words | 49,897,629 |
| Integrated rows | 2,449,842 |
| Tables | 53 |

The 1,000-document sample had 1,000 distinct openings (100%). The forced GIN-index query plan used `text_record_search_gin_idx`; its measured execution time was 2.484 ms for the limited query. This is a forced index-path check, not proof that the planner will choose the index for every query or dataset.

The relation footprint was 147.280 MB below the 790 MB gate. The full disposable database was 348.278 MB below a nominal 1,000 MB. These are disposable PostgreSQL measurements, not Neon billed-storage measurements.

## Text-only correction and repeatability

The first run's shared 0005 setup emitted an obsolete media-reference diagnostic before 0008 removed those tables. That diagnostic is excluded from all capacity calculations and this report. The shared setup has now been corrected to omit media, CCTV and body-worn-video reference tables entirely. The 0008 workflow now reruns when that shared SQL changes.

A clean repeat is required to validate the same workload without even transient media-reference schema or diagnostic output. No production-capacity approval is made until the clean repeat and an additional repeat agree, the narrative realism is reviewed, and a reserve/performance assessment is completed.

## Capacity decision

**1 GB production capacity: NOT APPROVED YET.** The first run passes the 790 MB relation-footprint benchmark gate, but this is not final approval. No benchmark data has been inserted into Neon. Production seeding remains blocked.

## Files

- SQL: `db/benchmarks/0008_high_entropy_text_lifecycle_benchmark.sql`
- Shared text-only setup: `db/benchmarks/0005_integrated_lifecycle_capacity_benchmark.sql`
- Workflow: `.github/workflows/storage-benchmark-high-entropy-text.yml`


## Clean-repeat attempt: failed before measurement

The first clean text-only repeat (run 45058809884) failed during workload setup, before the measurement step. Log inspection identified a stray standalone `WHERE true;` in the shared 0005 SQL, left by the media-reference cleanup. This was a SQL syntax error, not a capacity-gate failure; no valid clean-repeat measurements were produced. The stray clause was removed in commit `fc23353ac6995aa42b05504f18ab3aa7be63066f`, which triggered a new disposable run: https://github.com/Joshuaogri/saltwater/actions/runs/45059118741. Await its completion before claiming a clean repeat. The original first-run measurements remain valid only for that original run and do not establish the corrected text-only baseline.


## Corrected clean-repeat result (run 45059118741)

The corrected text-only repeat completed successfully on commit `fc23353ac6995aa42b05504f18ab3aa7be63066f`. The SQL setup correction is confirmed. Disposable PostgreSQL measurements:

- Full database: 651,779,095 bytes = **651.779 MB**.
- Relation footprint: 642,727,936 bytes = **642.728 MB**.
- Heap: 457,146,368 bytes = 457.146 MB.
- Indexes: 138,838,016 bytes = 138.838 MB.
- TOAST/auxiliary: 46,743,552 bytes = 46.744 MB.
- Raw UTF-8 text: 244,366,230 bytes = 244.366 MB.
- Text documents: 33,500; words: 49,897,629; integrated rows: 2,449,842; tables: 53.
- Text table storage including indexes: 90,636,288 bytes = 90.636 MB.
- A 1,000-document entropy sample had 1,000 distinct openings (100%).
- Full-text query execution: 2.019 ms in the recorded plan; the plan's forced-index test is not proof the planner always chooses the GIN index.
- Largest case: 517,809 words; median case: 12,373 words; p95: approximately 152,711 words.

Compared with the first 0008 run (651.722 MB full database; 642.720 MB relation footprint), the corrected clean repeat differs by only 0.057 MB full-database and 0.008 MB relation footprint. This is a strong reproducibility result for this generated workload. Both runs are disposable PostgreSQL measurements, not Neon billed-storage measurements. The workload generator is deterministic, so repeated storage similarity establishes repeatability, not independent narrative diversity. Production capacity remains unapproved pending a further independent/repeated run, content-realism review and a defensible Neon reserve assessment.
