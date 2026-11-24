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
