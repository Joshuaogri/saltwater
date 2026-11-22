# Saltwater persistent lifecycle benchmark — run 0003

Date: 2026-11-22  
Status: successful; synthetic data only; isolated schema removed after measurement.

## Execution

- GitHub Actions run: https://github.com/Joshuaogri/saltwater/actions/runs/45049960061
- Workflow: Saltwater persistent isolated lifecycle benchmark
- Run conclusion: success
- Tested commit: `d14a03e354f5fe1d56821484a2d3fb796f78e863`
- Neon database: `neondb`
- Isolated schema: `sw_bench_run`
- Tables created: 32
- All benchmark tables were persistent PostgreSQL tables during measurement, then removed by dropping the isolated schema.
- No production residents, businesses, cases, evidence or other simulation records were seeded.

## Dataset

The benchmark combined the generated rows from benchmark stages 0001 and 0002:

- Stage 0001: 242,000 rows across eight tables.
- Stage 0002: 1,034,842 rows across 24 tables.
- **Expected generated total: 1,276,842 rows across 32 tables.**

The workflow's supplementary `pg_stat_user_tables.n_live_tup` estimate reported 1,318,842 live rows, 42,000 above the exact generated-row total. This statistic is an estimate, not an exact count; the exact generated totals above are derived from the benchmark's explicit per-table `generate_series` row counts and the stage count queries. The discrepancy is recorded rather than silently treating the estimate as exact.

## Measured storage

All MB values are decimal (1 MB = 1,000,000 bytes).

| Measurement | Bytes | Decimal MB |
|---|---:|---:|
| Database before benchmark | 8,953,856 | 8.954 |
| Benchmark schema relation total (heap + indexes + TOAST/auxiliary) | 381,214,720 | 381.215 |
| Database while benchmark tables existed | 390,815,744 | 390.816 |
| Database after schema cleanup | 9,461,760 | 9.462 |
| Net database-size difference after cleanup vs before | 507,904 | 0.508 |

### Relation breakdown

| Component | Bytes | Decimal MB |
|---|---:|---:|
| Heap | 304,529,408 | 304.529 |
| Indexes | 76,201,984 | 76.202 |
| TOAST and auxiliary | 483,328 | 0.483 |
| **Total relation footprint** | **381,214,720** | **381.215** |

The database size while the benchmark was present was 390.816 MB, which is the full-database measurement. The benchmark schema itself accounted for 381.215 MB. The remaining difference includes the foundation schema and database-level overhead.

The post-cleanup database was 0.508 MB larger than its pre-benchmark measurement. This residual is not the benchmark dataset footprint and must not be used as a substitute for the measured 381.215 MB relation total. PostgreSQL/Neon allocation and internal overhead may not return exactly to the earlier size immediately after dropping tables.

## Interpretation

This is the first successful persistent combined benchmark and is substantially more useful than the earlier temporary-table-only measurements. It confirms that this particular synthetic representation of 10,000 residents, 10,000 businesses, relationships, employment, cases, incidents, evidence metadata, 150,000 historical events and the additional city/institutional/police/justice sample occupies approximately 381.215 MB in PostgreSQL relations, with the entire database at 390.816 MB during the test.

It does **not** prove that 1 GB is sufficient for the complete Saltwater lifecycle. It is a bounded benchmark, not the complete world or all lifetime activity. In particular:

- The 10,000-resident and 10,000-business samples do not yet represent every required attribute and complete lifecycle history.
- The police and institutional samples are synthetic sizing assumptions, not a final staffing or activity forecast.
- The event and case histories do not yet represent the full intended duration and frequency of play.
- Several institutional and police workflows remain absent or simplified.
- Large binary evidence and media (photographs, audio, video, scans, CCTV/BWC footage and forensic images) are not represented by these relational measurements.
- Backup, branch, archival and external object-storage requirements have not been measured.
- A substantial free-space reserve is still required.

## Cleanup

The workflow successfully dropped `sw_bench_run` and all 32 benchmark tables. The final database-size measurement was 9,461,760 bytes. The benchmark schema is not intended to persist.

## Decision

**1 GB capacity remains NOT APPROVED.**

No production simulation data should be seeded until the remaining lifecycle categories, binary-media strategy, defined simulation-duration scenarios, growth projection and safety reserve have been measured. The next stage should improve realism and completeness of the benchmark and model 10-, 20- and 35-year activity scenarios without silently assuming which one is the official game lifetime.
