# Saltwater benchmark run 0004 — longitudinal world and police records

Status: **completed successfully** (2026-11-22).

- Workflow run: https://github.com/Joshuaogri/saltwater/actions/runs/45052214555
- Tested commit: `7413ce7fa0e75f672c99a9d1266f2ff6131bc6ed`
- Workflow conclusion: success.
- Isolated schema: `sw_bench_run_0004`; all 16 objects (15 benchmark tables plus exact-count audit table) were dropped after measurement.

## Exact generated dataset

| Table | Exact rows |
|---|---:|
| Household profiles | 5,000 |
| Household memberships | 10,000 |
| Resident address history | 40,000 |
| Resident longitudinal life events | 200,000 |
| Business staffing history | 50,000 |
| Commercial transactions | 100,000 |
| Public organisations | 60 |
| Public office history | 500 |
| Public-service encounters | 50,000 |
| Education enrolments | 30,000 |
| Police training history | 10,000 |
| Police discipline history | 2,000 |
| Police radio communications | 80,000 |
| Forensic examinations | 15,000 |
| Legal proceedings | 8,000 |
| **Exact total** | **600,560** |

Dates span up to 35 years from the synthetic start date. These are benchmark distributions, not approved gameplay activity assumptions or an official simulation duration.

## Measured PostgreSQL storage

All sizes use decimal MB (1 MB = 1,000,000 bytes); raw bytes are authoritative.

| Measurement | Bytes | Decimal MB |
|---|---:|---:|
| Heap | 133,021,696 | 133.022 |
| Indexes | 33,185,792 | 33.186 |
| TOAST/auxiliary | 507,904 | 0.508 |
| **Total relation footprint** | **166,715,392** | **166.715** |
| Full database before benchmark | 9,355,264 | 9.355 |
| Full database while benchmark present | 176,185,344 | 176.185 |
| Full database after cleanup | 9,469,952 | 9.470 |

The relation footprint is the measured cost of this benchmark schema. The database-size delta before/after cleanup (114,688 bytes) is not the benchmark dataset footprint and must not be substituted for it.

Largest measured table: resident longitudinal life events, 75.571 MB total (63.005 MB heap; 12.526 MB indexes). Commercial transactions used 24.486 MB; radio communications 18.842 MB.

## Method and cleanup

The workflow connected to Neon, confirmed foundation migration 0001, created and populated the isolated benchmark schema, ran exact `COUNT(*)` audits for all 15 tables, measured per-table and aggregate storage, measured full database size, and dropped the schema. The exact-count audit used psql `\\gexec`; no PL/pgSQL dollar-quoted block was needed. Logs confirm the exact total of 600,560 and successful removal of all 16 objects.

## Limitations

This stage adds household membership, address and life-event history, business staffing and transactions, public organisations/services, education, police professional history, radio, forensics and legal proceedings. It remains a representative sample, not a complete 35-year lifecycle. It does not include full binary media payloads, complete detailed financial ledgers, every healthcare/social-service subtype, full CAD/BWC/GPS/interview/surveillance media, or complete event-rate assumptions.

**Capacity decision remains NOT APPROVED.** This measured 166.715 MB stage must not simply be added to stage 3 as though all records are disjoint; overlap and coverage must be reconciled before a combined lifecycle projection. No production population, business, case or evidence data was loaded.
