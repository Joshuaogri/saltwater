# Text-depth lifecycle benchmark — run 0006

Status: PostgreSQL 16 validation successful on two independent runs. The 1 GB safety gate was exceeded, so Neon measurement was correctly skipped. No benchmark data was loaded into Neon.

## Purpose

Benchmark the full 10,000-resident integrated synthetic world with realistic-length written records. This benchmark supersedes the earlier conditional 1 GB conclusion, which did not include realistic full-length documents.

## Text-only scope

Saltwater stores no photographs, audio, CCTV footage, body-camera footage, video, scanned documents, binary attachments or other binary media. No external media/object-storage tier is required by this design.

The benchmark reuses the integrated 0005 synthetic world, then removes its media-asset, CCTV-footage-reference and body-worn-video-reference tables before measuring. Written incident, police, witness, interview, evidence, forensic, intelligence, surveillance, arrest, custody, legal, court and personnel records remain text.

## Document-length workload

The SQL assigns varied routine, complex and exceptional lengths within the proposed ranges:

| Record type | Routine range | Complex range | Exceptional test |
|---|---:|---:|---:|
| Initial incident reports | 300–800 | 1,500–3,000 | — |
| Police reports | 300–800 | 1,500–3,000 | — |
| Supplementary reports | 200–600 | 1,000–2,500 | — |
| Witness statements | 300–1,000 | 2,000–5,000 | — |
| Interview transcripts | 1,000–3,000 | 5,000–12,000 | 25,000 |
| Evidence descriptions | 100–400 | 500–1,500 | — |
| Forensic reports | 500–1,500 | 2,000–5,000 | — |
| Intelligence reports | 300–1,000 | 2,000–5,000 | — |
| Surveillance observations | 100–500 | 1,000–3,000 | — |
| Arrest and custody records | 300–800 | 1,000–2,000 | — |
| Legal submissions | 1,000–3,000 | 5,000–15,000 | — |
| Court judgments | 1,000–5,000 | 10,000–25,000 | 50,000 |
| Police personnel records | 200–800 | 1,000–3,000 | — |

Two linked case-history stress examples are represented as dated event narratives rather than duplicated aggregate text: one 250,000-word major case and one 500,000-word exceptional case. Because other linked reports and records also attach to those cases, the measured maximum cumulative case history is larger than either standalone stress example.

The lengths are benchmark assumptions, not a gameplay limit or a promise that every record has the same length. Case history is derived by summing linked dated records, not by storing a second copy of the complete narrative.

## Storage and performance measurements

The benchmark reports:
- Exact document counts and exact word counts by record type.
- Minimum, average, 95th-percentile and maximum document word counts.
- Raw UTF-8 text bytes before PostgreSQL storage compression.
- Heap, index and TOAST/auxiliary relation bytes.
- Full database size during the complete benchmark.
- Case-history word-count distribution.
- Full-text search query plan and execution time.
- Full database size in disposable PostgreSQL 16.
- Neon before/during/after measurements only if the disposable safety gate passes. In this run the gate failed, so Neon was not touched.

All storage sizes use decimal MB (1 MB = 1,000,000 bytes). Transfer/upload bytes are not applicable because the synthetic records are generated inside PostgreSQL.

## Capacity gate

The 1 GB project is considered sufficient only if the measured full database remains at or below 800,000,000 bytes (800 MB), preserving at least 200 MB of nominal headroom. The disposable PostgreSQL run has a conservative 790,000,000-byte relation-footprint gate before Neon is used.

If the gate is exceeded, the workflow deliberately skips the Neon load and reports that 1 GB is not approved for this workload.

## Reproducibility

- SQL: [0006_text_depth_lifecycle_benchmark.sql](../../db/benchmarks/0006_text_depth_lifecycle_benchmark.sql)
- Workflow: [storage-benchmark-text-depth.yml](../../.github/workflows/storage-benchmark-text-depth.yml)
- Base integrated dataset: [0005_integrated_lifecycle_capacity_benchmark.sql](../../db/benchmarks/0005_integrated_lifecycle_capacity_benchmark.sql)

No production population, business, case or evidence data is inserted. The benchmark schema is dropped after measurement.


## Measured results — 2026-11-22

Two independent GitHub Actions runs completed successfully:
- Run 1: https://github.com/Joshuaogri/saltwater/actions/runs/45055330210
- Run 2: https://github.com/Joshuaogri/saltwater/actions/runs/45055343838
- PostgreSQL version: 16.16.
- Both runs passed exact row-count, table-count and text-volume checks.
- Both runs deliberately skipped the Neon measurement because the disposable relation footprint exceeded the 790 MB safety gate.

### Workload measured

- Residents: 10,000.
- Businesses: 10,000.
- Text documents: **237,000**.
- Total generated text: **283,702,825 words**.
- Raw UTF-8 text: **2,081,698,917 bytes (2,081.699 MB)**.
- Total integrated rows including text-depth records: **2,653,342**.
- Cases with linked text: **2,000**.
- Case history words: minimum 64,716; median 111,245.5; 95th percentile 309,125.05; maximum 752,119.
- Largest case's raw text: 5,521,186 bytes.

### PostgreSQL storage results

| Measurement | Run 1 | Run 2 |
|---|---:|---:|
| Full disposable database | 1,149.173 MB | 1,149.353 MB |
| Relation footprint | 1,140.179 MB | 1,140.318 MB |
| Heap | 762.233 MB | — |
| Indexes | 207.716 MB | — |
| TOAST/auxiliary | 170.230 MB | — |

The Run 1 relation breakdown sums to 1,140.179 MB. The text-record table alone occupied 588.087 MB (heap 339.091 MB, indexes 80.650 MB, TOAST/auxiliary 168.346 MB). PostgreSQL compressed the 2,081.699 MB raw text to a smaller on-disk text-record footprint; the measured relation footprint also includes all non-text world, institutional, police and operational tables.

Run 2 differed slightly because of PostgreSQL physical layout; row counts, document counts, word counts and raw text bytes were identical.

### Search performance

The sample full-text query returned 50 rows in **42.881 ms** on the disposable PostgreSQL instance. The observed plan used a sequential scan for this limited query, so this result is a baseline rather than proof that the GIN index is always selected or that search performance is fully tuned.

### Capacity decision

<badge color="danger">1 GB not sufficient for this benchmark workload</badge>

The complete disposable database occupied approximately **1,149 MB**, already exceeding the nominal 1,000 MB allowance. Its relation footprint was approximately **1,140 MB**, exceeding the 790 MB pre-Neon safety gate. The required 200 MB reserve is therefore not available.

**Neon was not loaded or measured in this run.** This was intentional: the workflow prevented a benchmark that already exceeded the safe capacity gate from consuming the live project's storage. No production data was inserted.

This result establishes that the *current 0006 workload* does not fit in 1 GB. It does **not** prove that 10,000 residents by themselves require more than 1 GB, nor does it establish a smaller safe population. The text workload is driven primarily by document counts, text lengths, case-history accumulation, indexes and retention assumptions, not simply resident count. A smaller resident population is not yet justified.

### Next capacity step

Build a second, calibrated workload profile that retains the 10,000 residents and 10,000 businesses but uses a defensible distribution of cases and documents across a clearly stated lifecycle. Avoid assigning the same large set of documents to every case by modulo alone. Separate routine, serious and exceptional cases using realistic prevalence, retain the stated maximum document lengths, and calculate linked case histories from those distributions. Then repeat the disposable gate and measure Neon only if the 200 MB reserve can be protected.

No production population, business, case or evidence data has been inserted. The disposable benchmark schema was dropped after measurement.
