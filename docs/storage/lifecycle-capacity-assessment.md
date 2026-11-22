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


## 10. Benchmark stage 2 — institutional and police lifecycle (2026-11-22)

The extended synthetic benchmark completed successfully (1,034,842 rows across 24 temporary tables):

- Workflow run: https://github.com/Joshuaogri/saltwater/actions/runs/45049121196
- Benchmark report: [benchmark-run-0002.md](benchmark-run-0002.md)
- Tested commit: `4accdd8ba88174176a2e357f4b886e4ffc381db2`
- Temporary tables: 24
- Synthetic rows: 1,034,842
- Measured heap: 245,047,296 bytes (245.047 MB)
- Measured indexes: 61,792,256 bytes (61.792 MB)
- Total temporary relation footprint: 307,052,544 bytes (307.053 MB)
- PostgreSQL `ANALYZE`: completed successfully.

The largest measured categories were interviews (50.766 MB), police reports (44.573 MB), dispatch actions (41.140 MB), commercial transactions (34.447 MB), intelligence (28.705 MB), and patrol events (28.189 MB).

Database size readings around the session were 8,347,648 bytes before and 8,814,592 bytes after. The 466,944-byte difference is not the temporary dataset's storage cost. Temporary relations were removed when the connection closed; use the 307.053 MB relation measurement for this benchmark.

This stage improves coverage but does not yet represent final production schemas, complete resident biographies, all business and institutional history, every police workflow, or binary media. The benchmark remains synthetic and temporary. No production population, business, case or evidence data was loaded.

**Capacity status remains NOT APPROVED.** Next: measure persistent relation growth in an isolated benchmark schema or Neon branch, including heap, indexes and TOAST, and add missing lifecycle categories and media-volume assumptions before projecting the 1 GB limit.


## 11. Benchmark stage 3 — combined persistent lifecycle (2026-11-22)

The combined persistent benchmark completed successfully against Neon:

- Workflow run: https://github.com/Joshuaogri/saltwater/actions/runs/45049960061
- Benchmark report: [benchmark-run-0003.md](benchmark-run-0003.md)
- Tested workflow commit: `d14a03e354f5fe1d56821484a2d3fb796f78e863`
- Persistent benchmark tables: 32
- Exact generated-row total from stage counts: 1,276,842 (stage 0001: 242,000; stage 0002: 1,034,842)
- Relation heap: 304,529,408 bytes (304.529 MB)
- Relation indexes: 76,201,984 bytes (76.202 MB)
- TOAST/auxiliary: 483,328 bytes (0.483 MB)
- **Persistent benchmark relation footprint: 381,214,720 bytes (381.215 MB)**
- Full database size while benchmark was present: 390,815,744 bytes (390.816 MB)
- Database before benchmark: 8,953,856 bytes (8.954 MB)
- Database after cleanup: 9,461,760 bytes (9.462 MB)
- The isolated `sw_bench_run` schema and all 32 tables were successfully dropped.

The supplementary `pg_stat_user_tables.n_live_tup` estimate reported 1,318,842, which is 42,000 above the exact generated-row total. It is explicitly treated as an estimate, not an exact count. The stage-specific count queries and generate-series inputs support the 1,276,842 generated-row figure.

The 507,904-byte (0.508 MB) difference between database size after cleanup and before the benchmark is not the benchmark dataset footprint. Use the measured 381.215 MB relation footprint and 390.816 MB full database size during the persistent test.

This benchmark combines the earlier synthetic resident/business/case/event dataset with the extended city, institutional, police and justice dataset. It remains incomplete as a full lifecycle model: biographies and histories are simplified; many government, service and police workflows are missing or sampled; the intended simulation duration is not fixed; binary media is not included; and backup/archival/object-storage costs are not yet measured.

**Capacity status remains NOT APPROVED.** The persistent benchmark is a useful measured sizing point, not a lifetime capacity proof. Continue with complete category coverage, realistic record distributions, 10-/20-/35-year scenario modelling, media-storage strategy and a documented safety reserve before production seeding.
