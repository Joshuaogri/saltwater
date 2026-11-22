# Text-depth lifecycle benchmark — run 0006

Status: automated PostgreSQL 16 validation and Neon measurement pending.

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

Two linked case-history stress examples are represented as dated event narratives rather than duplicated aggregate text: one 250,000-word major case and one 500,000-word exceptional case.

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
- Database size before and after cleanup on Neon.
- Net post-cleanup change and the persistent storage-operation ledger entry.

All storage sizes use decimal MB (1 MB = 1,000,000 bytes). Transfer/upload bytes are not applicable because the synthetic records are generated inside PostgreSQL.

## Capacity gate

The 1 GB project is considered sufficient only if the measured full database remains at or below 800,000,000 bytes (800 MB), preserving at least 200 MB of nominal headroom. The disposable PostgreSQL run has a conservative 790,000,000-byte relation-footprint gate before Neon is used.

If the gate is exceeded, the workflow deliberately skips the Neon load and reports that 1 GB is not approved for this workload.

## Reproducibility

- SQL: [0006_text_depth_lifecycle_benchmark.sql](../../db/benchmarks/0006_text_depth_lifecycle_benchmark.sql)
- Workflow: [storage-benchmark-text-depth.yml](../../.github/workflows/storage-benchmark-text-depth.yml)
- Base integrated dataset: [0005_integrated_lifecycle_capacity_benchmark.sql](../../db/benchmarks/0005_integrated_lifecycle_capacity_benchmark.sql)

No production population, business, case or evidence data is inserted. The benchmark schema is dropped after measurement.
