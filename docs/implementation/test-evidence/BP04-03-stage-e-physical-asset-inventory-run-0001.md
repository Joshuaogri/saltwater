# BP04-03 Stage E physical-asset inventory — run 0001

Date: 2026-11-24  
Workflow: [BP04-03 Stage E Disposable PostgreSQL — successful run 45504985010](https://github.com/Joshuaogri/saltwater/actions/runs/45504985010)  
Verified commit: `1eadb489a957b7c0ca5787f215380707a97e62d5`  
Candidate manifest SHA-256: `9b9bf26f756a74a8607d36a48c504879d12fd8ef9c188e34bda846bc71b11b9a`  
Parcel dossier manifest SHA-256: `173006d39e9172741a4900559751907856524532edba5a98403293c07a4d0a67`  
Physical-asset manifest SHA-256: `b6178ffad486295fcf7adb106ca76870ed9a7b455dcb3d8136b63b2d0f71aa45`

## Verification result

The full disposable PostgreSQL 16 workflow passed. It applied proposals 0011–0015, loaded the approved test-only geography fixtures, imported parcel candidates and parcel dossiers, generated the physical-asset hierarchy, imported identities/profiles/typed details/geometries, verified same-manifest idempotency, ran database acceptance, measured lookups, and completed a PostgreSQL 16-matched backup/restore.

All 15 Stage E Python regression tests passed (9 generator tests and 6 importer validation tests).

## Physical-asset hierarchy

| Identity class | Count |
|---|---:|
| Property-site candidates | 420 |
| Building candidates | 384 |
| Premises | 1,327 |
| Units | 15,199 |
| Access-location candidates | 768 |
| Properties without a building candidate | 36 |

The 420 property sites are tied to 420 geometry-derived parcel candidates. They are large candidate sites, not final cadastral lots or operationally approved property boundaries. Every building footprint passed validity and parent-property containment tests. Premises are floor-level spaces within buildings; units are subordinate to premises. Each generated building has two unreviewed boundary access-location candidates.

## Detailed BP04-02 profiles and child records

| Record family | Imported |
|---|---:|
| Typed profiles across all five identity classes | 18,098 |
| Physical measurements | 34,624 |
| Building level schedules | 1,327 |
| Building components | 4,608 |
| Premises room allocations | 3,981 |
| Utility-system records | 37,979 |
| Physical-feature records | 21,417 |
| Condition assessments | 22,533 |
| Knowledge-state assertions | 55,446 |
| Physical defect records | 0 |
| Candidate geometry records | 1,572 |
| Property-to-parcel candidate lineage links | 420 |
| Parent relationship records | 16,910 |

The profile and detail records explicitly preserve unknown or not-assessed states. Generated component material is `unknown`; condition assessments are `not_assessed`; utility availability and physical-feature presence are `not_assessed`; access-point emergency egress and loading capability use nullable booleans plus explicit epistemic state. No physical defects were invented.

## Storage and repeat-import measurements

- Proposal 0015 source SQL: **9,238 bytes**.
- Proposal 0015 schema-only disposable database growth: **303,104 bytes**.
- First Stage E inventory import database growth: **130,441,216 bytes**.
- First import elapsed time: **172,618.046 ms**.
- Same-manifest repeat import: **0 bytes** database growth; zero identities, relationships, profiles, detail rows, geometry rows or candidate-site links inserted; **6.970 ms**.
- Full compressed Stage E manifest artifact: **1,523,057 bytes**.
- [Preserved full physical-asset manifest](https://github.com/Joshuaogri/saltwater/actions/runs/45504985010/artifacts/14971474446).

Largest Stage E relation footprints in the disposable database:
- `asset_assertion`: 22,429,696 bytes.
- `physical_measurement`: 14,516,224 bytes.
- `utility_system`: 14,245,888 bytes.
- `condition_assessment`: 10,043,392 bytes.
- `physical_feature`: 7,512,064 bytes.

Representative indexed lookups completed in 0.043 ms for parcel-to-property lineage, 0.061 ms for building-to-premises, and 0.114 ms for premises-to-units.

## Backup and restore

The PostgreSQL 16-matched `pg_dump`/`pg_restore` round trip passed. The restored database preserved:
- 420 property identities.
- 15,199 unit identities.
- 1,572 asset geometry candidates.
- The exact asset-generation manifest checksum.

## Scope and authority boundaries

This is a successful disposable PostgreSQL import and regression proof, not a Neon production deployment or operational city activation.

- Zero canonical addresses were created.
- Zero operational spatial IDs were assigned.
- Zero operational access points/entrances were asserted; all 768 are unreviewed geometry candidates.
- Zero ownership, tenancy, occupancy, resident, business-operator or police-facility assignments were created.
- All all 100 source records now map to stable entity_code values; database spatial_id is generated per database and looked up by entity_code.
- Building footprints, room layouts, unit areas and floor heights are generated design allocations, not survey measurements.
- Construction materials, utility connections, physical condition, defects, capacity and actual access remain unknown/not assessed unless later supported by evidence.
- No Neon production connection, migration, seed, upload or activation occurred.

## Next

Proceed to operational reconciliation only after the BP-02 geography approval/version gate. All 100 source records already resolve to stable entity_code values; production spatial_id surrogates remain database-specific and unassigned until activation. Downstream business-site, resident, household, tenancy, ownership, occupancy and police-facility assignments remain separate controlled work.


## Geography source-identity reconciliation correction (2026-11-24)

The earlier statement that 100 source-to-spatial mappings remained unresolved is superseded. All **100 source records now map one-to-one to stable `sw_geo.entity.entity_code` values**: 8 districts, 24 neighbourhoods, 18 landmarks, 5 routes, 3 geography zones and 42 roads. The exact source record, entity type/kind, canonical name and parent are checked against SW-GEO-V1 by `runtime/geography_identity_reconciliation.py`; the readiness workflow runs regression tests for full coverage, duplicate IDs, incorrect parents and missing records. The reconciliation register now reports 100 resolved and 0 unresolved source-identity mappings.

PostgreSQL `spatial_id` is a GENERATED ALWAYS AS IDENTITY surrogate, so its integer is database-specific and must be looked up using the stable `entity_code` in each database. The portable source manifest intentionally does not freeze a disposable integer as a production ID. This correction resolves source-to-identity mapping; it does **not** approve SW-GEO-V1 for operational seeding, create parcel/address/entrance geometry, or authorize Neon writes. Those separate geography quality and activation gates remain.
