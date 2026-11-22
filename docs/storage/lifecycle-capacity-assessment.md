# Saltwater lifecycle storage-capacity assessment

Status: baseline measured; lifetime capacity not approved.

## 1. Verified starting point

On 2026-11-22, GitHub Actions workflow `Neon connection and storage baseline` completed successfully against the Neon database `neondb`.

- Database size: 7,790,592 bytes
- Decimal size: 7.791 MB (1 MB = 1,000,000 bytes)
- Workflow run: https://github.com/Joshuaogri/saltwater/actions/runs/45047512732
- This is a measured database baseline, not a forecast and not proof that the 1 GB allowance is sufficient.
- The baseline workflow did not apply the Saltwater foundation migration.
- No population, business, case, evidence, or other simulation seed data has been loaded.

## 2. Capacity decision gate

Do not load production-scale simulation data until a measured benchmark and lifecycle projection support a capacity decision.

The decision must be one of:
1. **1 GB sufficient** for the explicitly defined lifecycle, with a documented reserve; or
2. **1 GB insufficient**, with a quantified capacity target and an alternative architecture or plan.

A small initial database, a row-count estimate alone, or a generic PostgreSQL rule of thumb is not sufficient evidence.

## 3. Scope to include

The benchmark must represent the full 10,000-resident, one-city-state world and the deep police simulation.

### World and population
- Exactly 10,000 living residents at the hard population ceiling.
- Individual identities and persistent biographies.
- Households, families, relationships, contacts, addresses, residences and movement history.
- Employment, education, businesses, organisations and institutional affiliations.
- Deaths, departures, replacements and historical identity links.

### City and institutions
- Districts, streets, junctions, addresses, buildings and properties.
- At least 10,000 businesses, with ownership, premises, staff, opening patterns and operational history.
- Government, ministries, legislature, courts, prosecution, corrections, healthcare, education, emergency services, finance and other institutions.
- Organisational structures, personnel, facilities and inter-agency records.

### Police service
- Personnel, recruitment, training, ranks, positions, units, rosters, deployments and discipline.
- Calls, dispatch, patrol, incidents, reports and operational logs.
- Victims, witnesses, suspects, persons of interest and their persistent histories.
- Investigations, leads, interviews, intelligence, surveillance, warrants, arrests and custody.
- Evidence items, chain of custody, forensic submissions, examinations and results.
- Case files, court referrals, proceedings, outcomes and linked records.

### Longitudinal history
- Time-stamped changes and events over the defined game lifecycle.
- Relationships and employment changes, address history, business changes, institutional changes and police activity.
- Corrections, superseded records, audit/provenance and recovery information.
- Retention and archival policy, including whether old records remain online, are compressed, or are moved to another storage tier.

## 4. Benchmark method

1. Record a fresh database-size measurement before applying the foundation migration.
2. Apply the migration using a controlled, repeatable process.
3. Measure database size immediately after migration and record the net change.
4. Generate a synthetic benchmark dataset with realistic distributions and representative text lengths. Do not use real personal data.
5. Load the benchmark in measured stages: core world, residents/relationships, city/businesses, institutions, police personnel, operational activity, cases/evidence, and longitudinal history.
6. Measure database size after every stage using `pg_database_size(current_database())`; also measure table, index and TOAST contributions using PostgreSQL catalog/statistics queries.
7. Record submitted payload bytes separately from actual database growth.
8. Repeat important batches to measure duplicate handling and idempotency.
9. Test query performance and index overhead at target scale.
10. Project the defined lifecycle from measured per-record and per-event costs, including growth, indexes, TOAST, metadata, WAL implications where relevant, and a safety reserve.
11. Re-run the benchmark after schema or compression changes; compare measured results.

All measurements use decimal MB: 1 MB = 1,000,000 bytes. Preserve raw byte counts as the authoritative values.

## 5. Storage accounting

For each upload, import or bulk migration, record:

- Original input bytes and MB.
- Compressed input bytes and MB, where compression is used.
- Submitted/transfer bytes and MB.
- Database size immediately before and after.
- Net database growth in bytes and MB.
- Compression percentage, where meaningful.
- Counts of inserted, updated, skipped and deduplicated records.
- Measurement timestamp, operation identifier, migration/version and notes.

Never equate compressed transfer size with PostgreSQL storage growth. Database growth includes table data, indexes, TOAST and PostgreSQL overhead. If a value cannot be measured, mark it unavailable; do not estimate it as if measured.

## 6. Binary evidence and attachments

The benchmark must distinguish structured evidence metadata from binary payloads such as photographs, audio, video, scanned documents and other large files.

Do not assume Neon database storage is the right place for every binary payload. Evaluate database storage versus a separate object-storage tier, including lifecycle cost, retrieval, durability, access patterns, references, integrity hashes and backup/recovery. No external object-storage service is considered configured until it is actually provisioned and tested.

## 7. Efficiency principles

- Normalise stable entities and shared facts; reference them rather than duplicating them.
- Use compact surrogate identifiers where useful.
- Store repeated labels in dictionaries/reference tables.
- Use event/delta records for changing facts when this preserves complete reconstruction.
- Use JSONB for genuinely variable attributes, not as a replacement for relational design.
- Avoid excessive indexes; measure the storage and query benefit of each.
- Partition only when measured scale and query patterns justify it.
- Consider compression and archival only after testing CPU, storage, query and recovery trade-offs.
- Deduplicate identical payloads using content hashes where appropriate.
- Preserve provenance, chronology, identity resolution and full recoverability. Storage savings must not erase meaningful simulation detail.

## 8. Current decision

**Not approved:** 1 GB lifetime capacity.

**Allowed:** schema design, migration validation, read-only measurement, synthetic benchmark design and controlled benchmark loads after the measurement procedure is ready.

**Blocked:** production population/business/case/evidence seeding and any large irreversible import until the benchmark and capacity decision are complete.

## 9. Required final report

The capacity report must state:
- Defined game lifecycle and retention assumptions.
- Benchmark dataset counts and generation rules.
- Measured baseline and post-migration size.
- Measured bytes per representative entity/event category.
- Table, index and TOAST storage breakdown.
- Measured binary payload volumes and proposed storage tier.
- Projected lifecycle total, with assumptions clearly separated from measurements.
- Safety reserve and expected headroom.
- Whether 1 GB is sufficient; if not, the required alternative capacity.
- Reproducible SQL, scripts, test outputs and commit references.
