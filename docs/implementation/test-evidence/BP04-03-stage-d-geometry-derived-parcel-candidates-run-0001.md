# BP04-03 Stage D geometry-derived parcel candidates — run 0001

**Date:** 2026-11-24  
**Disposable workflow:** [BP04-03 Stage B Disposable PostgreSQL — run 45490203072](https://github.com/Joshuaogri/saltwater/actions/runs/45490203072)  
**Candidate generator workflow:** [run 45490210942](https://github.com/Joshuaogri/saltwater/actions/runs/45490210942)  
**Result:** PASS  
**Geometry engine:** Shapely 2.1.2  
**Database:** Disposable PostgreSQL 16 database `saltwater_test` only  
**Production / Neon writes:** none

## Replacement of provisional parcel geometry

This run supersedes the earlier 396-cell parcel candidate layer that inset each 500m cell by a provisional 15m allowance and excluded every cell touched by water.

The new deterministic generator:
1. Intersects each 500m source lineage cell with its source neighbourhood polygon.
2. Dissolves the 685 fictional road/bridge corridor polygons using SW-RDS-V1 and subtracts the resulting road-reserve geometry.
3. Subtracts only the actual mapped water polygon geometry; it does not exclude an entire cell merely because water intersects it.
4. Splits resulting land geometry into valid polygon components, retaining interior rings where present.
5. Gives each component a deterministic candidate ID and a pronounceable fictional display name accepted by the universal naming registry.
6. Records source neighbourhood, district, source-cell index, component index, geometry, measured area, land-use category, road-edge-contact segment references, confidence, provenance and non-operational status.

The old 15m inset is no longer used.

## Verified candidate geography

| Measure | Result |
|---|---:|
| Neighbourhoods | 24 |
| Source 500m lineage cells | 432 |
| Candidate parcel components | 420 |
| Candidate components with road-reserve edge contact | 418 |
| Components without identified road-edge contact | 2 |
| Cells intersected by mapped water | 36 |
| Dissolved fictional road-reserve area | 7,057,146.032 m² |
| Water area outside road reserve | 5,605,030.589 m² |
| Candidate land area | 95,337,823.379 m² |
| Total source neighbourhood area | 108,000,000.000 m² |
| Area reconciliation difference | 0.000 m² |

The area identity is exact to the audit precision:

`108,000,000.000 = 7,057,146.032 + 5,605,030.589 + 95,337,823.379` m².

All 24 neighbourhoods independently reconcile with zero area delta. Candidate interiors are valid, non-overlapping polygon components. Road frontage is only a geometric road-reserve edge-contact candidate; it does not claim a legal frontage, entrance, access route or canonical address.

## Naming and disposable database acceptance

The first import attempt exposed that the generic label `Candidate Parcel <id>` violated SW-UNS-001's near-duplicate review rule. That label was replaced with deterministic, pronounceable, unique fictional parcel names. The importer uses those names through the existing geography-name trigger; no naming checks were disabled or bypassed.

[Run 45490203072](https://github.com/Joshuaogri/saltwater/actions/runs/45490203072) passed:
- 420 candidate geography identities inserted in disposable PostgreSQL.
- 420 checksummed geometry versions inserted.
- 420 detailed parcel candidate profiles inserted.
- First import database growth: **1,081,344 bytes**.
- First import elapsed time: **625.396 ms**.
- Canonical address identities created: **0**.
- Repeat import: 420 profiles remained present; zero identities, versions or profiles inserted; **0 bytes** database growth; 175.672 ms.
- Repeat-import idempotency assertion passed.

The candidate manifest SHA-256 is `d2b1db72d45dabbc5d54eb864fe6c6e4e9b428c5b8e771316b49efb7343fe305`.

## Preserved artifacts

- Geometry-derived parcel candidate manifest: **28,513 compressed bytes** ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45490203072/artifacts/14965647916)).
- Dissolved road-reserve topology: **9,850 compressed bytes** ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45490203072/artifacts/14965578349)).
- Parcel area coverage audit: **1,586 compressed bytes** ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45490203072/artifacts/14965003943)).
- Road corridor register: **23,915 compressed bytes** ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45490203072/artifacts/14965428482)).

The separate candidate-generation regression workflow [45490210942](https://github.com/Joshuaogri/saltwater/actions/runs/45490210942) also passed, including deterministic IDs and names, valid polygon rings, cell lineage, road-edge-contact logic, exact area reconciliation and zero operational IDs/addresses.

## State and next implementation

This is a fictional game-world planning layer, not a real cadastral survey. Candidate parcel identities and profiles exist only in the disposable test database. They are not production spatial IDs, approved cadastral parcels or operational addresses. The 100 unresolved source-to-spatial mappings remain unresolved; no addresses are allocated.

Next: build the parcel-level dossier and boundary/frontage review layer, including parcel dimensions, perimeter, shape, area, adjoining roads, access candidates, water adjacency, neighbouring parcel relationships, land-use and development state, constraints and source lineage. Then use those parcels as the parent geography for detailed property, building, premises, unit and access-point inventory. Do not seed shallow property records.
