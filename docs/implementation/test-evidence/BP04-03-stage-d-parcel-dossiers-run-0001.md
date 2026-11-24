# BP04-03 Stage D detailed parcel dossiers — run 0001

**Date:** 2026-11-24  
**Workflow:** [BP04-03 Stage B Disposable PostgreSQL — run 45494991970](https://github.com/Joshuaogri/saltwater/actions/runs/45494991970)  
**Result:** PASS  
**Database:** Disposable PostgreSQL 16 only  
**Production / Neon writes:** none

## Parcel dossier coverage

The 420 geometry-derived parcel candidates now have detailed, geometry-linked dossier records. The dossier generator measures each polygon and derives its spatial relationships without inventing survey, ownership, occupancy, address or access facts.

Every parcel dossier records:
- area and perimeter;
- compactness index;
- centroid and interior representative label point;
- bounding box;
- exterior vertex and interior-ring counts;
- total contact length along the dissolved road-reserve boundary;
- frontage candidate count and source segment lineage;
- water-boundary contact length and water feature relationships;
- measurement basis, source reference, actor, confidence and reason;
- explicit geometry and frontage review states.

## Spatial relationship results

| Measure | Result |
|---|---:|
| Parcel dossiers | 420 |
| Valid generated polygon geometries | 420 |
| Parcels requiring frontage review | 418 |
| Parcels without road-edge contact | 2 |
| Parcel-to-road frontage candidates | 1,374 |
| Source road segments represented in frontage candidates | 1,374 |
| Unreviewed access-location candidates | 1,374 |
| Shared parcel-boundary relationships | 100 |
| Corner-touch relationships | 0 |
| Water-adjacent parcels | 32 |
| Parcel-to-water adjacency relationships | 32 |
| Operational access-point identities | 0 |
| Canonical addresses | 0 |

Each frontage candidate is a parcel-to-named-road relationship and retains its contributing source road segment IDs and measured contact length. Its candidate point is the midpoint of the longest continuous contact component. An access-location candidate is only an unreviewed geometric point on that frontage; it is not an entrance, driveway, usable access route or operational access-point record.

Adjacency records use canonically ordered parcel pairs and measured shared boundary length. Water adjacency records identify the mapped water feature and measured boundary contact. Neither relationship asserts ownership, title, legal boundary agreement or occupancy.

## Database schema and disposable import

Proposal `0014_bp04_parcel_dossier_detail.sql` adds five append-only typed tables:
1. `sw_geo.parcel_dossier`
2. `sw_geo.parcel_frontage_candidate`
3. `sw_geo.parcel_access_location_candidate`
4. `sw_geo.parcel_adjacency_candidate`
5. `sw_geo.parcel_water_adjacency_candidate`

The schema enforces composite parcel/version references, geometry checksums, dossier manifest checksums, frontage-to-road segment lineage, access-candidate-to-frontage references, canonically ordered adjacency pairs, water contact provenance and append-only mutation guards.

- Proposal source size: **10,311 bytes**.
- Schema-only disposable database growth: **368,640 bytes**.
- Synthetic SQL acceptance passed and rolled back all test rows.
- First dossier import: 420 dossiers, 1,374 frontage records, 1,374 access-location candidates, 100 adjacency records and 32 water-adjacency records.
- First dossier import database growth: **1,859,584 bytes** (1,353.791 ms).
- Repeat dossier import: zero inserts across all five tables and **0 bytes** database growth (1,326.012 ms).
- Canonical addresses created: **0**.
- Dossier manifest SHA-256: `173006d39e9172741a4900559751907856524532edba5a98403293c07a4d0a67`.

The preceding parcel candidate import inserted 420 identities, 420 geometry versions and 420 parcel profiles; first-import growth was 1,040,384 bytes and repeat-import growth was 0 bytes.

## Verification and artifacts

The full workflow passed all eight Python test suites (41 tests total), the BP04-03 Stage B and Stage D disposable SQL acceptance scripts, candidate import, dossier import and both repeat-import idempotency checks.

Preserved artifacts:
- Detailed parcel dossiers: **68,438 compressed bytes** ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45494991970/artifacts/14968720668)).
- Geometry-derived parcel candidates: **28,508 compressed bytes** ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45494991970/artifacts/14966689354)).
- Dissolved road-reserve topology: **9,850 compressed bytes** ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45494991970/artifacts/14966794706)).
- Parcel area coverage: **1,585 compressed bytes** ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45494991970/artifacts/14968377307)).
- Road corridor register: **23,915 compressed bytes** ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45494991970/artifacts/14967403802)).

## State and next implementation

All dossier and relationship rows were imported only into the disposable test database. No Neon production connection, migration, seed, upload or activation occurred. No canonical addresses, operational access points, property, building, premises, unit, ownership, tenancy or occupancy records were created.

Next: build the complete detailed property, building, premises, unit and access-point inventory on top of these parcel parents. Each asset must receive its full BP04-01 identity and BP04-02 effective-dated physical dossier, including dimensions, construction/materials, levels, rooms, utilities, facilities, condition, defects, access and provenance. Do not create shallow ID-only records.
