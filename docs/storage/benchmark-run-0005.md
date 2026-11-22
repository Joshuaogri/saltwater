# Integrated lifecycle capacity benchmark — run 0005

Status: PostgreSQL 16 validation and Neon integrated measurement successful. Synthetic-only.

## Reconciliation rules

This is one coherent benchmark, not a sum of the four prior stages. Stable entities are generated once:
- 10,000 residents; 10,000 businesses; 6,000 buildings; one 12-district/800-street/2,500-junction network.
- Shared household, resident, business, police, organisation, case and evidence IDs are reused across dependent records.
- Employment is one 50,000-row history (not 20,000 + 50,000).
- Address history is one 40,000-row history (not 30,000 + 40,000).
- Commercial transactions are one 200,000-row ledger (not 200,000 + 100,000).
- Forensic examinations are one 20,000-row history (not 20,000 + 15,000).
- Legal proceedings are one 30,000-row history (not 30,000 + 8,000).
- Household memberships are one 12,000-row relation (not 12,000 + 10,000).
- Public organisations are one 80-row set (not 80 + 60).
- All police and city records refer back to shared entity IDs.

## Coverage

Institutional: office-holder history, public-service encounters, education, healthcare, social services, foreign relations.

Financial: bank accounts, 300,000 ledger entries, tax returns and tax payments.

Police operations: recruitment/personnel, shifts, training, discipline, CAD calls, dispatch, patrol, reports, radio, GPS points, BWC references.

Investigations/evidence/justice: cases, incidents, interviews, intelligence reports and links, surveillance, warrants, arrests, custody, evidence, chain-of-custody events, forensics, prosecution, legal proceedings, corrections.

Media: metadata and integrity hashes only. Binary payloads are separately measured as references; they are not stored in PostgreSQL by this benchmark.

## Integrated dataset validation

- Validation workflow: https://github.com/Joshuaogri/saltwater/actions/runs/45052956900
- Validation commit: `960528fa97c80d31295419095d9f6a9b5e0db896`
- PostgreSQL 16, disposable GitHub Actions database; workflow succeeded.
- Exact data tables: **54**.
- Exact total: **2,516,342 rows**.
- Heap: **439,623,680 bytes (439.624 MB)**.
- Indexes: **131,866,624 bytes (131.867 MB)**.
- TOAST/auxiliary: **1,908,736 bytes (1.909 MB)**.
- **Integrated relation footprint: 573,399,040 bytes (573.399 MB)**.
- External media references: 30,000 assets; referenced payload total **1,950,015,000 bytes (1,950.015 MB)**. These payloads are excluded from PostgreSQL storage and require separate object storage.
- The test asserted the exact row total and table count, then dropped all 55 objects (54 data tables plus the audit table).

Largest tables:
- Financial ledger entries: 73.441 MB.
- Resident life events: 60.703 MB.
- Dispatch actions: 40.649 MB.
- Commercial transactions: 38.150 MB.
- Police reports: 34.120 MB.
- Patrol events: 30.728 MB.
- Healthcare encounters: 28.025 MB.
- GPS track points: 22.938 MB.
- Emergency calls: 22.913 MB.
- Interview records: 22.487 MB.
- Evidence custody events: 18.588 MB.
- Police shifts: 16.490 MB.
- Radio communications: 16.458 MB.

## Capacity arithmetic and decision

Using the measured integrated PostgreSQL relation footprint and the last measured Neon post-cleanup baseline:
- Integrated relations: 573.399 MB.
- Existing Neon baseline: 9.470 MB.
- Indicative occupied total: **582.869 MB**.
- 1 GB decimal allowance: 1,000 MB.
- 20% protected reserve: 200 MB.
- Indicative remaining headroom after reserve: **217.131 MB**.

**Decision for this defined relational benchmark: 1 GB is sufficient, conditionally.** This conclusion assumes:
1. The 35-year synthetic workload represented by this benchmark is the planning envelope, not unlimited future growth.
2. Binary photos, audio, CCTV, BWC, scans and forensic media are stored outside Neon. The benchmark references about 1.95 GB of such payloads.
3. The 200 MB reserve remains protected for PostgreSQL overhead, growth and operational headroom.
4. No major unbenchmarked data class or materially higher event rate is introduced without a new measurement.

**1 GB is not sufficient if binary media is stored in the database**, and this is not approval for unlimited lifetime growth. The integrated Neon workflow must still be run once to capture Neon-specific full-database before/during/after sizes and confirm that its measured usage fits the same reserve.

## Neon measurement workflow

- Workflow: [integrated lifecycle capacity benchmark](../../actions/workflows/storage-benchmark-integrated.yml)
- SQL: [0005_integrated_lifecycle_capacity_benchmark.sql](../../db/benchmarks/0005_integrated_lifecycle_capacity_benchmark.sql)
- The workflow measures Neon database size before, during and after the integrated dataset, captures relation size, and removes the isolated schema.
- No production population, business, case or evidence records are inserted.


## Neon measurement — successful

- GitHub Actions run: https://github.com/Joshuaogri/saltwater/actions/runs/45053385138
- Tested commit: `7621b19eb6ad540ff0407576d8c33938cfbc8909`
- Result: success; integrated schema created, measured and removed.
- Exact rows: **2,516,342** across 54 data tables.
- Table count measured in schema: 55 (54 data tables plus exact-count audit table).
- Relation footprint: **569,417,728 bytes (569.418 MB)**.
- Full Neon database before benchmark: **9,281,536 bytes (9.282 MB)**.
- Full Neon database during benchmark: **579,084,288 bytes (579.084 MB)**.
- Full Neon database after schema cleanup: **9,666,560 bytes (9.667 MB)**.
- Net database-size change after cleanup: **385,024 bytes (0.385 MB)**. This is residual database/ledger overhead, not the benchmark relation footprint.
- Database size after the persistent storage-operation ledger entry: **9,666,560 bytes (9.667 MB)**.
- The workflow inserted a successful measurement record into `sw_ops.storage_operation`; input/compressed/submitted file bytes are not applicable because SQL generated the synthetic data inside PostgreSQL.
- External media payload references: **1,950,015,000 bytes (1,950.015 MB)** across 30,000 assets; not stored in Neon.

## Superseded capacity conclusion

This report is a historical measurement of the 0005 relational benchmark. Its earlier conditional "1 GB sufficient" conclusion is **withdrawn** because 0005 did not benchmark realistic full-length reports, statements, interview transcripts, forensic documents, legal records or cumulative long-running case histories.

The media-reference table and its 1,950.015 MB notional payload are not part of Saltwater's design. Saltwater is text-only: no photographs, audio, CCTV footage, body-camera footage, video, scans, binary attachments or external media storage are required. The 0006 text-depth benchmark removes the 0005 media, CCTV-observation-reference and body-worn-video-reference tables before its storage measurement.

**Current decision: 1 GB is NOT YET APPROVED.** See [benchmark run 0006 — text-depth lifecycle](benchmark-run-0006-text-depth.md). Production seeding remains blocked until the realistic text workload is measured and the 200 MB reserve gate is passed.
