# Calibrated text lifecycle benchmark — run 0007

Status: disposable PostgreSQL 16 validation succeeded on run 45057029582. The capacity-gate follow-on jobs were skipped because output interpolation in the workflow was escaped; this was corrected in commit 1d00c5c566fd4fa9696d72ca775a4a1f9440986a. Neon was not touched.

## Purpose and fixed world

Retain the approved 10,000-resident and 10,000-business targets. This benchmark recalibrates the text workload after 0006 showed that 237,000 documents distributed broadly across 2,000 cases produced an implausibly dense case-history distribution.

The underlying integrated world remains the 0005 synthetic dataset. The 35-year date span is only a capacity-sizing scenario, not an approved game-duration or retention limit.

## Calibrated case/document assumptions

The synthetic case cohort contains 2,000 cases across the scenario, approximately 57 cases per year. Text records are assigned by workflow-specific counts rather than spreading every record type over every case.

| Text record type | Documents |
|---|---:|
| Initial incident reports | 2,000 |
| Police reports | 3,000 |
| Supplementary reports | 2,000 |
| Witness statements | 4,000 |
| Interview transcripts | 5,000 |
| Evidence descriptions | 8,000 |
| Forensic reports | 2,000 |
| Intelligence reports | 1,000 |
| Written surveillance observations | 1,500 |
| Arrest records | 1,000 |
| Custody records | 1,000 |
| Legal submissions | 1,500 |
| Court judgments | 500 |
| Police personnel records | 250 |
| Major/exceptional case-history events | 750 |
| **Total** | **33,500** |

These are explicit benchmark assumptions, not final simulation event-rate canon. The 0005 world already contains operational rows and short descriptive fields; 0007 adds distinct full-length written records and avoids a second aggregate copy of each case history.

## Length and exceptional-history treatment

- Routine reports and statements are mostly several hundred to roughly 1,500 words.
- Complex witness, interview, forensic and legal records have a minority of longer documents.
- Interview and court records include a small exceptional-length tail.
- Two case-history stress examples retain 250,000 and 500,000 cumulative words as linked dated 1,000-word events. These are examples, not global maximums.
- Every text record is independently attributed and linked to its source/case where applicable.

## Text generation and storage measurement

The deterministic prose generator uses varied sentence templates and unique record/segment identifiers. It is intentionally less repetitive than the 0006 phrase bank, but remains synthetic and should not be treated as a perfect model of natural-language entropy.

The workflow measures:
- exact text document count, word count and raw UTF-8 bytes;
- complete disposable database size;
- total relation footprint;
- text-record heap, index and TOAST contribution;
- full-text search plan and execution time;
- exact base-world plus text-record row count.

All sizes use decimal MB. No file is uploaded and no binary media is stored. Submitted/transfer payload is therefore not applicable.

## Safety gate

The disposable workflow reports whether the relation footprint is at or below 790,000,000 bytes. A pass only permits a separately reviewed Neon measurement; it does not automatically insert data into Neon. A failure leaves Neon untouched. The desired full-database budget remains at or below 800,000,000 bytes, preserving at least 200 MB of nominal headroom in a 1 GB project.

## Decision

No capacity approval is made until the workflow completes and measured results are reviewed. The 10,000-resident and 10,000-business design targets remain unchanged.


## First successful measured run (2026-11-22)

GitHub Actions run: https://github.com/Joshuaogri/saltwater/actions/runs/45057029582

- Database size: 656,833,559 bytes = 656.834 MB.
- Relation footprint: 647,839,744 bytes = 647.840 MB.
- Heap: 463,036,416 bytes = 463.036 MB.
- Indexes: 145,195,008 bytes = 145.195 MB.
- TOAST/auxiliary: 39,616,512 bytes = 39.617 MB.
- Text-record table total: 95.756 MB (heap 39.895 MB; indexes 18.129 MB; remainder TOAST/auxiliary).
- Text documents: 33,500.
- Text words: 49,897,629.
- Raw UTF-8 text: 341,425,062 bytes = 341.425 MB.
- Integrated row count: 2,449,842.
- Base-world resident/business counts remain 10,000 each.
- Largest linked case history: 517,809 words; median: 12,373; p95: approximately 152,711.
- Full-text sample query: 50 rows in approximately 43.9 ms, but planner selected sequential scan; index/search tuning remains open.

The relation footprint is 142.160 MB below the 790 MB safety threshold. The full database is 143.166 MB below the 800 MB working target. These results are for a disposable benchmark database, not Neon. The workflow's capacity-gate jobs did not run due to an escaped output-expression defect; the defect has been fixed and must be confirmed in the next run.

No submitted Neon payload, Neon storage increase, before/after Neon database size, or Neon compression measurement exists for this benchmark because no Neon import was performed. Mark those measurements not applicable/not measured, not zero.


## Corrected gate run and live Neon baseline (2026-11-22)

Corrected workflow run: https://github.com/Joshuaogri/saltwater/actions/runs/45057328325

- Validation job: **success**.
- Capacity gate: **passed** (relation footprint at or below 790,000,000 bytes).
- Capacity-exceeded job: skipped as expected.
- Measured disposable database: 656,890,903 bytes = **656.891 MB**.
- Measured relation footprint: 647,839,744 bytes = **647.840 MB**.
- Integrated rows: **2,449,842**.
- Text documents: **33,500**.
- Text words: **49,897,629**.
- Raw UTF-8 text: 341,425,062 bytes = **341.425 MB**.
- Tables asserted: **53**.
- The disposable benchmark schema was dropped after measurement. No benchmark data was inserted into Neon.

The corrected run's relation footprint is 142.160 MB below the 790 MB gate. Its full database size is 143.109 MB below the 800 MB working target. This is a **benchmark gate pass**, not final approval of the 1 GB production plan: the generated narrative still relies on a finite sentence bank with deterministic record/segment labels and may compress more effectively than genuinely varied authored text.

Read-only Neon baseline workflow: https://github.com/Joshuaogri/saltwater/actions/runs/45057566657

- Workflow: **success**.
- Measurement transaction: BEGIN READ ONLY followed by ROLLBACK.
- Database: neondb.
- Database size: 9,306,112 bytes = **9.306 MB**.
- User relation footprint measured by the workflow: 188,416 bytes = **0.188 MB**.
- Five user tables were reported; largest measured user relation was 49,152 bytes.
- No rows were inserted, updated or deleted.
- No production benchmark payload was submitted; Neon storage increase is **not applicable/not measured**.
- Compressed transfer payload is **not applicable/not measured**.
- No before/after Neon size delta or Neon compression ratio is claimed.

## Decision after corrected gate

The 10,000-resident and 10,000-business targets remain unchanged. The calibrated workload passes the disposable relation-footprint gate and the live Neon baseline is small, but the 1 GB capacity decision remains **provisional / not approved** until a second benchmark uses substantially higher text entropy and measures realistic PostgreSQL heap, indexes, TOAST and full-text search behaviour. Production seeding remains blocked pending that test and a reviewed reserve calculation.
