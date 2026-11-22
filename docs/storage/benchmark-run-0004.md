# Saltwater benchmark run 0004 — longitudinal world and police records

Status: prepared; awaiting manual GitHub Actions execution. No measurements are claimed yet.

## Scope

Workflow: [Run stage 4 benchmark](https://github.com/Joshuaogri/saltwater/actions/workflows/storage-benchmark-stage-4.yml)

SQL: [0004 longitudinal world and police benchmark](../../db/benchmarks/0004_longitudinal_world_and_police_benchmark.sql)

The benchmark creates 15 persistent synthetic tables in the isolated schema `sw_bench_run_0004`, then measures exact row counts, heap, indexes, TOAST/auxiliary storage, total relation footprint and full database size. The workflow drops the isolated schema after measurement, including on failure where cleanup is possible.

## Planned generated dataset

| Category | Rows |
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
| **Expected total** | **600,560** |

Dates span up to 35 years from the synthetic start date. These are benchmark distributions, not approved gameplay activity assumptions or an official simulation duration.

## Measurement fields to capture

- Exact per-table counts and exact combined total.
- Database size before and while the schema is present.
- Per-table heap, index and total relation bytes.
- Aggregate heap, index, TOAST/auxiliary and relation total.
- Database size after cleanup and cleanup confirmation.
- Workflow run ID, tested commit and execution conclusion.

## Important limitations

This stage adds depth for household membership, addresses, resident life events, business staffing and transactions, public organisations and services, education, police professional history, radio, forensics and legal proceedings. It is still a sample and does not yet include full binary media payloads, complete detailed financial ledgers, every health/social-service subtype, or a complete 35-year event-rate model.

**Capacity decision remains NOT APPROVED.** Await measured workflow output before recording any storage result or combining this stage with other benchmark measurements.
