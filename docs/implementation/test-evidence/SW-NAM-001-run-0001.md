# SW-NAM-001 — Disposable PostgreSQL Run 0001

**Result:** PASS  
**Workflow:** [PKG-001 disposable PostgreSQL validation](https://github.com/Joshuaogri/saltwater/actions/runs/45409845359)  
**Tested commit:** `9739b91d19259b578bf112c3e82fd917daf49633`  
**Database:** Disposable PostgreSQL 16 only  
**Production Neon:** Not connected or modified

## Verified scope

- Foundation and proposals 0002–0009 applied successfully.
- SQL naming acceptance: global uniqueness, exact Saltwater root pair, explicit ambiguous search, Unicode case-fold collision, alias collision, historical-name protection, rename/reactivation and direct-insert bypass prevention.
- Python normalizer, in-memory registry, deterministic generators, canon inventory, PostgreSQL adapter and existing runtime regression suites passed.
- PostgreSQL same-name concurrency, different-name concurrency, same-entity different-canonical-name concurrency, idempotency and transaction rollback passed.
- Person and geography identity adapters preserved stable IDs and append-only name history.
- Generator manifest persistence, idempotent registration and reservation linkage passed.
- 9,999-person fixture, concurrent 10,000-person cap boundary, database role/access checks, checkpoint consistency and full disposable backup/restore passed.
- Restore assertions verified name reservations, name-event history, the Saltwater exception, geographic rename identity and generator-manifest linkage.
- Fictional world tick remained controlled by the existing runtime gates.

## Storage measurements

| Measurement | Result |
|---|---:|
| Disposable DB baseline before proposal 0009 | 10,066,967 bytes |
| After proposal 0009 schema | 10,484,759 bytes |
| Schema growth | 417,792 bytes |
| Full disposable database after 10,000 people | 32,070,679 bytes |
| Reserved names | 10,011 |
| Name-reservation table + indexes | 8,536,064 bytes |
| Average total bytes per reservation | 852.67 bytes |
| Name-event table + indexes | 3,694,592 bytes |
| Generator-batch table + indexes | 49,152 bytes |

The per-reservation figure includes the table and its indexes; it is not a raw row-width measurement. A later workflow revision additionally reports heap, index and TOAST/auxiliary bytes separately.

## Explicitly unresolved / not claimed complete

- The SW-GEO-V1 dry-run inventory found two duplicate canonical names: district/neighbourhood `Westgate` and neighbourhood/landmark `Government Square`.
- 100 SW-GEO-V1 source IDs have not been materialised as database spatial IDs.
- SW-GEO-V1 remains marked as not approved for operational seeding. No canon import was performed.
- BP-04 business/property/organisation and other operational adapters remain NOT CONNECTED because their authoritative entity schemas are not yet available.
- This run does not authorize a Neon production migration, seed, import or write.

## Follow-up verification

A follow-up workflow [45410340222](https://github.com/Joshuaogri/saltwater/actions/runs/45410340222) rechecks the final generator-manifest normalizer-version metadata and the separate heap/index/TOAST storage report. Its final result must be recorded separately.

## Follow-up verification — final manifest version

**Result:** PASS  
**Workflow:** [PKG-001 disposable PostgreSQL validation](https://github.com/Joshuaogri/saltwater/actions/runs/45410340222)  
**Tested commit:** `a2e04e601b85c98a84946a6aae5f85bc1c594563`

This rerun passed the final Python generator-manifest normalizer-version metadata, SQL migration, all naming and runtime tests, same-entity concurrent canonical-name reservations, the 10,000-person population/cap fixture, access controls, checkpoint consistency and backup/restore.

Updated 10,011-name registry measurements:
- `sw_names.name_reservation`: 8,568,832 bytes total, including indexes (855.94 bytes per reservation).
- `sw_names.name_event`: 3,694,592 bytes total.
- `sw_names.generation_batch`: 49,152 bytes total.
- Schema growth remains 417,792 bytes.

A subsequent workflow revision now prints separate heap, index and TOAST/auxiliary bytes. That storage-only detail is awaiting its own run; it does not affect the passing functional/restore result above.


## Final storage-detail verification — run 45411243093

**Result:** PASS  
**Workflow:** [PKG-001 disposable PostgreSQL validation](https://github.com/Joshuaogri/saltwater/actions/runs/45411243093)  
**Tested workflow commit:** `9a5e1a09a082e67810fb01177408ca6447a21fef`  
**Database:** Disposable PostgreSQL 16 only

After the 10,011-name fixture and associated naming history/manifests were populated, PostgreSQL reported:

| Registry relation | Heap bytes | Index bytes | TOAST/auxiliary bytes | Total bytes |
|---|---:|---:|---:|---:|
| `name_reservation` | 2,007,040 | 6,488,064 | 40,960 | 8,536,064 |
| `name_event` | 2,531,328 | 1,122,304 | 40,960 | 3,694,592 |
| `generation_batch` | 8,192 | 32,768 | 8,192 | 49,152 |
| **Total** | **4,546,560** | **7,643,136** | **90,112** | **12,279,808** |

The reservation relation measured **8,536,064 bytes / 852.67 bytes per reserved name** across 10,011 names. The naming schema itself increased the empty disposable database from 10,066,967 to 10,484,759 bytes, a **417,792-byte** delta. The populated relation breakdown is separate and includes indexes and TOAST/auxiliary allocation as shown. These are not Neon production measurements.

The same run passed all workflow jobs, including the full 10,000-person fixture, population-cap concurrency boundary, naming acceptance, access controls and disposable backup/restore.

## Approved geography naming corrections — 2026-11-24

The user approved and the repository source now records:
- `SW-D01-N1`: **Westgate Gardens** (district `SW-D01` remains **Westgate**).
- `SW-D03-N2`: **Civic Terrace** (landmark `SW-POI-002` remains **Government Square**).

The source IDs and geometry are unchanged. The 100 unresolved source-to-spatial-ID mappings remain; SW-GEO-V1 is not approved for operational seeding and no canon import or Neon write occurred.


## Full regression, geography identity and storage verification — run 45441551968

**Result:** PASS — both workflow jobs and every step completed successfully  
**Workflow:** [Full Saltwater Python and disposable PostgreSQL regression](https://github.com/Joshuaogri/saltwater/actions/runs/45441551968)  
**Tested commit:** `64ccb19ca8fad1f0caef62a138a6d8cfa4447aa4`  
**Database:** Disposable PostgreSQL 16 only  
**Production Neon:** Not connected or modified

### Full regression coverage

The Python job passed the runtime kernel, player command interface, BP40-01 workspace, recruit-entry adapter, SW-NAM-001 naming/generator/canon inventory/PostgreSQL adapter, accepted-player activation, durable player composition, authenticated command runtime, trusted host adapter, ChatGPT tool handler, BP37-01 scheduler, BP35-01 event engine, BP39-01 recovery, actor authorization and hidden-truth gate suites.

The disposable PostgreSQL job passed foundation and PKG-001 acceptance; all 100 geography identity-map rows and parent links; all 100 naming-trigger reservations; recruit-entry acceptance; representative 1,000-person storage; naming concurrency, idempotency and rollback; persistent session verifier/audit sink; BP37 schedule, BP35 event dispatch and BP39 checkpoint/claim recovery; durable runtime adapter and authenticated command E2E; the 9,999-person fill and concurrent final-slot boundary; the full 10,000-person fixture; database access boundary; consistent checkpoint-manifest capture; and full backup/restore.

### Geography identity acceptance

- All 100 non-root SW-GEO-V1 source IDs materialised in disposable PostgreSQL.
- All parent references resolved and validated.
- All 100 geography name reservations created through the naming trigger.
- PostgreSQL-generated `spatial_id` values were captured through `INSERT ... RETURNING`.
- The fixture's hard guard restricted execution to database `saltwater_test` on PostgreSQL 16; no Neon or production connection was involved.
- This validates the disposable identity mapping only. It does not approve operational canon seeding or remove the separate map approval gate.

### Measured storage

| Measurement | Result |
|---|---:|
| Empty disposable database before SW-NAM-001 schema | 10,066,967 bytes |
| After naming schema | 10,484,759 bytes |
| Naming schema incremental growth | 417,792 bytes |
| Full disposable database before 10,000-person fixture | 11,172,887 bytes |
| After 10,000-person fixture | 13,507,607 bytes |
| 10,000-person fixture growth | 2,334,720 bytes (2.226562 MiB) |
| Average fixture growth per person | 2,334.72 bytes |
| Full database after population and naming fixture | 32,250,903 bytes |
| Reserved names after full fixture | 10,111 |
| Name-reservation total relation | 8,642,560 bytes (854.77 bytes per reservation) |
| Name-event total relation | 3,727,360 bytes |
| Generator-batch total relation | 49,152 bytes |

At the full fixture stage, the naming relations separately measured:

| Relation | Heap bytes | Index bytes | TOAST/auxiliary bytes | Total bytes |
|---|---:|---:|---:|---:|
| `name_reservation` | 2,023,424 | 6,578,176 | 40,960 | 8,642,560 |
| `name_event` | 2,555,904 | 1,130,496 | 40,960 | 3,727,360 |
| `generation_batch` | 8,192 | 32,768 | 8,192 | 49,152 |

These are disposable PostgreSQL measurements, not Neon production growth or a 1 GB capacity approval. The per-person value is the incremental database growth divided by 1,000 fixture persons, not a raw row width or a forecast of full narrative records.

### Backup/restore and checkpoint limitations

Backup/restore passed. The restored fixture exactly matched the source manifest:

`people=10000; states=10000; population=10000; events=20022; max_event=20058; tick=2; living_included=10000; names=10111; name_events=20225; generator_batches=1`.

The restore assertion reported `RESTORE_PASS`. The checkpoint validator deliberately returned `valid=false` because three gates were `not_executed`: `business_minimum`, `player_absence_freeze` and `permission_hidden_truth`. All executed structural, schema, event, schedule, population-cap, identity and append-only-history gates passed. The CI step asserted this exact expected partial-validation state. This is not a claim of a fully valid production-world checkpoint or of business-minimum completion.

### Outstanding integration boundaries

- BP-04 business/property/organisation and other operational named-entity adapters remain disconnected until their authoritative schemas exist.
- The 100-entry identity map remains a disposable mapping candidate; no production spatial IDs or operational canon seed were written.
- SW-GEO-V1 remains subject to its separate operational map approval gate.
- No Neon production migration, seed, import or write occurred in this run.
