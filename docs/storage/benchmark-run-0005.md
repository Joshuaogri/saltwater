# Integrated lifecycle capacity benchmark — run 0005

Status: prepared; execution pending. Synthetic-only, isolated schema.

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

## Added coverage

Institutional: office-holder history, public-service encounters, education, healthcare, social services, foreign relations.

Financial: bank accounts, 300,000 ledger entries, tax returns and tax payments.

Police operations: recruitment/personnel, shifts, training, discipline, CAD calls, dispatch, patrol, reports, radio, GPS points, BWC references.

Investigations/evidence/justice: cases, incidents, interviews, intelligence reports and links, surveillance, warrants, arrests, custody, evidence, chain-of-custody events, forensics, prosecution, legal proceedings, corrections.

Media: metadata and integrity hashes only. Binary payloads are separately measured as references; they are not stored in PostgreSQL by this benchmark.

## Execution

- Workflow: [integrated lifecycle capacity benchmark](../../actions/workflows/storage-benchmark-integrated.yml)
- SQL: [0005_integrated_lifecycle_capacity_benchmark.sql](../../db/benchmarks/0005_integrated_lifecycle_capacity_benchmark.sql)
- Database before/during/after, exact row counts, per-table heap/index/TOAST and aggregate relation footprint will be recorded after a successful run.
- The schema is removed after measurement.

## Capacity decision

No integrated run has yet been executed. Existing stage measurements are not added together. 1 GB is **not approved for production** pending the integrated measurement, a defined retention horizon and binary-media storage decision.
