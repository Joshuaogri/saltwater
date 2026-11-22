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
