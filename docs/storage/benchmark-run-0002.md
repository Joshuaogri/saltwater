# Storage Benchmark Run 0002 — Institutional and Police Lifecycle

- Run: [GitHub Actions #45049121196](https://github.com/Joshuaogri/saltwater/actions/runs/45049121196)
- Workflow: Saltwater extended institutional and police benchmark
- Result: success
- Commit tested: `4accdd8ba88174176a2e357f4b886e4ffc381db2`
- Date: 2026-11-22
- Database: Neon `neondb`
- Method: temporary PostgreSQL tables measured with `pg_total_relation_size`; all tables were dropped automatically when the benchmark connection closed.

## Dataset

24 temporary tables; 1,034,842 rows:

| Category | Rows |
|---|---:|
| Districts | 12 |
| Streets | 800 |
| Junctions | 2,500 |
| Buildings | 6,000 |
| Property history | 30,000 |
| Organisations | 80 |
| Institutional staff | 1,200 |
| Police personnel | 250 |
| Duty shifts | 100,000 |
| Calls | 100,000 |
| Dispatch actions | 200,000 |
| Patrol events | 150,000 |
| Police reports | 60,000 |
| Interviews | 30,000 |
| Intelligence reports | 20,000 |
| Surveillance sessions | 10,000 |
| Warrants | 8,000 |
| Arrests | 12,000 |
| Custody records | 12,000 |
| Forensic examinations | 20,000 |
| Court proceedings | 30,000 |
| Commercial transactions | 200,000 |
| Address history | 30,000 |
| Household memberships | 12,000 |
| **Total** | **1,034,842** |

## Measured storage

Decimal MB (1 MB = 1,000,000 bytes).

| Table | Heap MB | Index MB | Total MB |
|---|---:|---:|---:|
| Interview | 49.283 | 1.475 | 50.766 |
| Police report | 41.419 | 3.146 | 44.573 |
| Dispatch action | 26.214 | 14.918 | 41.140 |
| Commercial transaction | 23.593 | 10.846 | 34.447 |
| Intelligence | 27.312 | 1.360 | 28.705 |
| Patrol event | 18.874 | 9.306 | 28.189 |
| Call | 14.156 | 5.358 | 19.522 |
| Duty shift | 11.010 | 6.160 | 17.179 |
| Forensic examination | 13.107 | 1.098 | 14.213 |
| Court proceeding | 4.194 | 1.655 | 5.857 |
| Property history | 3.670 | 1.057 | 4.735 |
| Address history | 3.146 | 1.565 | 4.719 |
| Arrest | 2.097 | 0.721 | 2.826 |
| Surveillance | 1.573 | 0.614 | 2.195 |
| Custody | 1.573 | 0.573 | 2.154 |
| Household membership | 1.049 | 0.729 | 1.778 |
| Warrant | 1.049 | 0.508 | 1.565 |
| Building | 1.049 | 0.303 | 1.360 |
| Institutional staff | 0.262 | 0.131 | 0.401 |
| Junction | 0.262 | 0.131 | 0.401 |
| Street | 0.066 | 0.057 | 0.131 |
| Police personnel | 0.066 | 0.049 | 0.123 |
| Organisation | 0.016 | 0.016 | 0.041 |
| District | 0.008 | 0.016 | 0.033 |
| **Total** | **245.047** | **61.792** | **307.053** |

PostgreSQL `ANALYZE` completed successfully.

## Database size readings

- Before benchmark: 8,347,648 bytes = 8.348 MB.
- After benchmark session: 8,814,592 bytes = 8.815 MB.
- Observed difference: 466,944 bytes = 0.467 MB.

**Important:** these database-size readings do not represent the 307.053 MB temporary dataset. Temporary relations are not included in the ordinary persistent database-size figure in the same way as permanent relations. The 307.053 MB relation footprint is the valid benchmark measurement. The 0.467 MB difference must not be reported as the dataset's storage cost.

## Interpretation and limitations

This benchmark provides a measured footprint for a broad synthetic set of institutional, geographic, commercial and police records, including substantial text fields and indexes. It identifies interviews, police reports, dispatch actions, transactions, intelligence and patrol events as the largest tested relations.

It does not establish full lifecycle capacity. The schemas and distributions are simplified benchmark structures, not final production schemas. It does not adequately represent all institutional records, complete resident biographies, all business staffing histories, full family/relationship histories, radio and body-camera media, call recordings, forensic photographs, evidence files, detailed chain-of-custody histories, full prosecution/corrections records, or long-term retention. Binary media are not included.

The tables were temporary, so this run did not add 307.053 MB of persistent data to Neon. It did not seed production simulation data.

## Capacity decision

**NOT APPROVED.** The 1 GB lifecycle capacity gate remains open. The next stage must use a controlled persistent benchmark in an isolated schema or branch, measure actual persistent heap/index/TOAST/database growth, and test missing record classes and lifecycle scenarios. Keep production population, businesses, cases and evidence unseeded until the full capacity assessment passes.
