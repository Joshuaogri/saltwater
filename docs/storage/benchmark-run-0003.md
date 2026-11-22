# Saltwater persistent lifecycle benchmark — run 0003

Date: 2026-11-22  
Status: successful; synthetic data only; isolated schema removed after measurement.

## Execution

- GitHub Actions run: https://github.com/Joshuaogri/saltwater/actions/runs/45050714671
- Workflow: Saltwater persistent isolated lifecycle benchmark, run 3
- Run conclusion: success
- Tested commit: `71beee01cb4794b56f8b15d50940f157b5ebeba4`
- Neon database: `neondb`
- Isolated schema: `sw_bench_run`
- Tables created: 32
- All benchmark tables were persistent PostgreSQL tables during measurement, then removed by dropping the isolated schema.
- No production residents, businesses, cases, evidence or other simulation records were seeded.

## Dataset and exact row-count reconciliation

The benchmark combines the generated rows from stages 0001 and 0002:

- Stage 0001: 242,000 rows across eight tables.
- Stage 0002: 1,034,842 rows across 24 tables.
- **Exact total: 1,276,842 rows across 32 tables.**

Run 3 added a direct `COUNT(*)` for every table. The exact aggregate returned **1,276,842** and therefore confirms the generated-row total with no missing or additional rows.

The earlier `pg_stat_user_tables.n_live_tup` estimate reported 1,318,842, which is 42,000 higher. This is a PostgreSQL statistics estimate, not an exact count. The exact per-table counts resolve the discrepancy: use 1,276,842 as the authoritative benchmark row count and retain the statistics estimate only as a diagnostic.

## Measured storage

All MB values are decimal (1 MB = 1,000,000 bytes).

| Measurement | Bytes | Decimal MB |
|---|---:|---:|
| Database before benchmark | 9,347,072 | 9.347 |
| Benchmark schema relation total (heap + indexes + TOAST/auxiliary) | 381,214,720 | 381.215 |
| Database while benchmark tables existed | 390,832,128 | 390.832 |
| Database after schema cleanup | 9,617,408 | 9.617 |
| Net database-size difference after cleanup vs before | 270,336 | 0.270 |

### Relation breakdown

| Component | Bytes | Decimal MB |
|---|---:|---:|
| Heap | 304,529,408 | 304.529 |
| Indexes | 76,201,984 | 76.202 |
| TOAST and auxiliary | 483,328 | 0.483 |
| **Total relation footprint** | **381,214,720** | **381.215** |

The full database measured 390.832 MB while the benchmark was present. The benchmark schema accounted for 381.215 MB; the difference includes the foundation schema and database-level overhead.

After cleanup, the database was 0.270 MB larger than before the benchmark. This residual is not the benchmark dataset footprint and must not replace the measured 381.215 MB relation total.

## Interpretation and limitations

This confirms the storage footprint of this specific synthetic 1,276,842-row, 32-table dataset. It does not prove that 1 GB is sufficient for Saltwater's complete lifetime. The dataset remains a bounded sample:
- Resident and business records do not yet represent every required attribute and complete lifecycle history.
- Police and institutional activity distributions are synthetic sizing assumptions, not final forecasts.
- Event and case histories do not yet represent a defined full game duration or all activity.
- Several government, service, financial, social and police workflows remain absent or simplified.
- Binary evidence/media (photographs, audio, video, scans, CCTV/BWC footage and forensic images) is not included in the relational measurements.
- Backup, branch, archival and external object-storage costs have not been measured.
- A substantial free-space reserve remains mandatory.

## Cleanup

The workflow successfully dropped `sw_bench_run` and all 32 benchmark tables. The final database-size measurement was 9,617,408 bytes. The benchmark schema is not intended to persist.

## Decision

**1 GB capacity remains NOT APPROVED.**

No production simulation data should be seeded until missing lifecycle categories, binary-media strategy, defined 10-/20-/35-year scenarios, realistic activity distributions, growth projection and safety reserve have been measured.
