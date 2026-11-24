# BP04-03 Stage B disposable parcel ingestion — run 0001

**Date:** 2026-11-24  
**Workflow:** [BP04-03 Stage B Disposable PostgreSQL](https://github.com/Joshuaogri/saltwater/actions/runs/45484639045)  
**Result:** PASS  
**Commit under test:** `e17f04535e9c0df668cadbb47cc0a82f79b8ee3f`  
**Database:** GitHub Actions disposable PostgreSQL 16 service, database `saltwater_test`  
**Production writes:** none

## Acceptance

- Existing proposals 0001–0012 applied to a fresh disposable PostgreSQL 16 database.
- 100-entry SW-GEO-V1 geography identity map materialised as test fixtures.
- BP04-01 test geography references loaded.
- Proposal 0013 parcel/address schema applied.
- BP04-03 schema acceptance passed, including geometry checksum, duplicate active locator, wrong-kind road reference, append-only and parcel lineage checks.
- Candidate manifest generated with SHA-256 `83ec53dc09f51483110e1e564b82919d2da63a0f5c5adcd92b42e04bf508f85f`.
- Importer validated the manifest checksum, candidate count, closed polygon rings, absence of allocated spatial IDs and absence of canonical addresses.
- 396 parcel candidate identities, 396 versioned geometry payloads and 396 parcel profiles imported.
- All candidate parent neighbourhood references resolved to kind-4 geography identities.
- Geometry payload SHA-256 values were calculated and stored; proposal 0013's parcel-profile trigger independently recomputed and verified them.
- 0 address identities and 0 address profiles created.
- First import: 396 entities, 396 geometry versions and 396 profiles inserted.
- Second import: 0 entities, 0 geometry versions and 0 profiles inserted; all 396 profiles remained present.
- Repeat import reported zero database-size growth and passed the explicit idempotency assertions.

## Storage and execution measurements

| Measurement | Result |
|---|---:|
| Proposal 0013 source SQL | 10,668 bytes |
| Proposal 0013 schema-only database growth | 294,912 bytes |
| Database before first import | 12,917,783 bytes |
| Database after first import | 14,105,623 bytes |
| First import net database growth | 1,187,840 bytes |
| First import elapsed time | 739.125 ms |
| Candidate entities inserted | 396 |
| Geometry versions inserted | 396 |
| Parcel profiles inserted | 396 |
| Parcel profile relation total | 229,376 bytes |
| Geography version relation total | 229,376 bytes |
| Repeat import net database growth | 0 bytes |
| Repeat import elapsed time | 211.230 ms |

The database-size figures are for this disposable CI database only; they are not Neon storage measurements. Relation totals are whole-relation measurements and should not be added to database growth as if they were separate bytes.

## Scope and limits

- These 396 rows are explicitly candidate parcel identities/profiles in disposable PostgreSQL, not operational cadastral parcels.
- The 100 source-to-spatial-ID mappings remain unresolved; the identity-map rows are test fixtures and do not resolve those source mappings.
- The candidate 15m road-reserve inset remains provisional.
- No canonical addresses, property assets, buildings, premises, units, access points, owners, occupants, businesses or operational assignments were created.
- No BP-02 operational geography approval was inferred.
- No Neon connection, migration, upload, write or production activation occurred.
- The import is repeatable for the same manifest; conflicting existing geometry versions fail closed rather than being overwritten.

## Next

Continue refining candidate parcel geometry against explicit road-reserve and neighbourhood boundary geometry, and validate complete spatial coverage, inter-neighbourhood boundaries, gaps and overlaps before any operational geography approval or production seeding.
