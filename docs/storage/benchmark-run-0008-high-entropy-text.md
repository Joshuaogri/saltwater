# High-entropy text lifecycle benchmark — run 0008

Status: **pending disposable PostgreSQL validation**. This benchmark is not a Neon import and does not authorize production seeding.

## Purpose

Benchmark 0008 repeats the calibrated 0007 workload with a materially higher-entropy, deterministic prose generator. The previous 0007 generator used a small finite sentence bank; that made the stored text unusually compressible. Benchmark 0008 combines larger actor, action, subject, qualifier and caveat vocabularies, with record-type-specific framing. Selection is seeded by document and sentence position so repeated runs are reproducible without repeating a small fixed paragraph template.

## Fixed workload

- Residents: 10,000.
- Businesses: 10,000.
- Cases: 2,000 in a 35-year sizing scenario (not a gameplay-duration rule).
- Text documents: 33,500, with the same calibrated record-type distribution as 0007.
- Binary media: none; Saltwater remains text-only.
- Benchmark data: disposable PostgreSQL 16 only; no Neon writes.

## Validation and measurements

The workflow asserts the expected document and integrated row counts, a minimum number of distinct openings among a 1,000-document sample, and availability of an index-assisted full-text query plan. It reports database size, relation footprint, raw UTF-8 text bytes and word count. The SQL reports record-type distributions, case-history lengths, heap, indexes, TOAST/auxiliary storage, text-table storage and query timing.

The 0007 safety gate of 790,000,000 relation bytes remains in place. A gate pass permits further review only; it is not final 1 GB approval. Final approval also requires realistic text entropy, repeatability, a 200 MB nominal reserve, query performance and a clear distinction between disposable PostgreSQL size and Neon billed storage.

## Results

Pending workflow completion. No measurements are asserted in this report yet.

- SQL: `db/benchmarks/0008_high_entropy_text_lifecycle_benchmark.sql`
- Workflow: `.github/workflows/storage-benchmark-high-entropy-text.yml`
