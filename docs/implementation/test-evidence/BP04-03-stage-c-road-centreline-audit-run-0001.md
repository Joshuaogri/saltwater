# BP04-03 Stage C road-centreline and fictional road-reserve resolution — run 0002

**Date:** 2026-11-24  
**Workflow:** [BP04-03 Stage B Disposable PostgreSQL](https://github.com/Joshuaogri/saltwater/actions/runs/45487528624)  
**Result:** <badge>PASS</badge>  
**Commit under test:** `62203033e7e0bcc45ddaf8a2d7a24e4d66f94dc8`  
**Production writes:** none; all database acceptance and candidate ingestion ran on disposable PostgreSQL 16

## Resolved bridge lengths

The two bridge centre-lines were measured directly from their stored polyline vertices. The canonical source lengths are now set to the geometry-derived value rounded to the dataset's metre precision:

| Segment | Bridge | Previous declared length | Geometry-derived length | Canonical length |
|---|---|---:|---:|---:|
| `SWS-0684` | Harbour Bridge | 2,000m | 2,019.803903m | 2,019.804m |
| `SWS-0685` | Customs Bridge | 2,000m | 2,019.803903m | 2,019.804m |

The audit now reports **zero length reconciliation exceptions**. The source discrepancy is fixed rather than carried as an unresolved issue.

## Adopted fictional road-reserve design standard

A canonical in-world design standard, `SW-RDS-V1`, is now part of the SW-GEO-V1 dataset. It defines total corridor width centred on the road centre-line:

| Road class | Fictional right-of-way width |
|---|---:|
| Local street | 18m |
| District connector | 24m |
| Primary arterial | 30m |
| Bridge | 24m |

These are game-world design dimensions, not claims about real-world standards or measurements. The standard is effective for the SW-GEO-V1 fictional city map.

## Generated road-reserve geometry

The deterministic corridor generator applies the class width to each source centre-line and generates a segment-level polygon using mitered offsets. All **685 of 685** road/bridge segments now have a generated corridor polygon and a defined width.

- 42 named roads; 685 segments; 367 nodes.
- One connected road-network component.
- Zero node-degree, road-membership or endpoint-geometry mismatches.
- Zero bridge length exceptions.
- Zero unresolved corridor widths.
- 685 segment corridor polygons generated.
- Design standard: `SW-RDS-V1`.
- Road register SHA-256: `c357ce13d117971cde4bb3d1d134dfb37293c63e7319715ca2dd0b57e28da727`.

Segment polygons overlap at shared junctions by design. They must be dissolved into a network-level road-reserve geometry before computing unique reserve area or using the road edges for parcel frontage. No reserve area is summed from overlapping segment polygons in this increment.

## Verification

The full dedicated workflow [45487528624](https://github.com/Joshuaogri/saltwater/actions/runs/45487528624) completed successfully. Its Python suites passed (4 + 5 + 5 + 5 tests); disposable PostgreSQL candidate ingestion and repeat-import idempotency also passed. The repeat import inserted zero candidate entities, geometry versions and parcel profiles and produced 0 bytes of database growth.

Preserved outputs:
- Road corridor register: [artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45487528624/artifacts/14962764058), **23,915 compressed bytes**, archive SHA-256 `35da68f7689bd3e45f47c7a19169bfdcff16d2f95e52ac9cbe5d329f69cc3e7d`.
- Parcel coverage audit: [artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45487528624/artifacts/14963254002), **1,713 compressed bytes**, archive SHA-256 `45630e95c4556e2637302e1534f98874c46817cd0bed7bde617247aaed77d140`.

## Remaining implementation work

The bridge-length and road-width decisions are no longer blockers. The next implementation step is to dissolve the 685 segment corridors into a non-overlapping network-level road-reserve geometry, intersect it with the 24 neighbourhood polygons, and reconcile boundary coverage/gaps/overlaps. Then regenerate parcel candidates against those actual fictional road edges instead of the provisional 15m inset. Neighbourhood boundary rules and the city boundary will be encoded in the fictional geography data and tested deterministically.

No operational addresses, property records, ownership, occupancy or city-wide built-asset inventory were created in this run. No Neon production connection, upload, migration, seed or activation occurred.


# BP04-03 Stage C dissolved road-reserve and neighbourhood topology — run 0001

**Date:** 2026-11-24  
**Workflow:** [BP04-03 Stage B Disposable PostgreSQL](https://github.com/Joshuaogri/saltwater/actions/runs/45488230508)  
**Result:** PASS  
**Commit under test:** `2aee9701e23f7e8d49c828fee9c3d00fe555d38e`  
**Geometry engine:** Shapely 2.1.2  
**Production writes:** none

## Dissolved road-reserve geometry

The 685 segment-level corridor polygons were dissolved into one connected city road-reserve geometry. The operation removes **140,804.555 m²** of duplicate overlap contributed by segment corridors meeting at junctions.

| Measure | Result |
|---|---:|
| Segment corridor polygons | 685 |
| Sum of individual segment polygon areas | 7,197,950.587 m² |
| Duplicate junction overlap removed | 140,804.555 m² |
| Dissolved city road-reserve area | 7,057,146.032 m² |
| Dissolved network components | 1 |
| Road reserve outside city boundary | 0 m² |

The dissolved geometry is wholly contained by the city boundary. Unique road-reserve area is calculated after dissolve, not by adding overlapping segment areas.

## Neighbourhood boundary reconciliation

All 24 neighbourhood polygons were validated against the sovereign city boundary:

| Measure | Result |
|---|---:|
| City boundary area | 108,000,000 m² |
| Neighbourhood union area | 108,000,000 m² |
| Neighbourhood overlap area | 0 m² |
| Neighbourhood coverage gap | 0 m² |
| Neighbourhood area outside city | 0 m² |
| Sum of neighbourhood road-reserve allocations | 7,057,146.032 m² |
| Allocation difference from dissolved road reserve | 0 m² |

The neighbourhood polygons tile the entire fictional city boundary exactly. Every square metre of dissolved road reserve is allocated once across the 24 neighbourhoods.

## Verification

[Run 45488230508](https://github.com/Joshuaogri/saltwater/actions/runs/45488230508) passed the full workflow. Five road-reserve topology tests passed; the full Python suites passed (4 + 5 + 5 + 5 + 5 tests). Disposable PostgreSQL candidate import and repeat-import idempotency also passed.

Preserved outputs:
- Dissolved road-reserve topology: [artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45488230508/artifacts/14964976654), **9,850 compressed bytes**, archive SHA-256 `6c48fa58105dcdc6aa64b97fcf94d6c538ea75ea16669c036abdb77977963379`.
- Road corridor register: [artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45488230508/artifacts/14965495973), **23,915 compressed bytes**.
- Parcel coverage area audit: [artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45488230508/artifacts/14965206332), **1,713 compressed bytes**.

## Next implementation

Regenerate parcel candidates using the dissolved SW-RDS-V1 road-reserve geometry and water geometry, replacing the provisional 15m inset. Preserve source-cell lineage, split disconnected land components deterministically, and rerun candidate validity, overlap, neighbourhood assignment, water exclusion, area reconciliation and disposable PostgreSQL idempotency. Then expand the physical asset population into detailed property, building, premises, unit and access-point dossiers.
