# BP04-03 independent parcel-dossier geometry QA — run 0001

**Date:** 2026-11-24  
**Workflow:** [BP04-03 Parcel Dossier Geometry QA — successful run 45511739957](https://github.com/Joshuaogri/saltwater/actions/runs/45511739957)  
**Verified source commit:** `59aae8abd261d4bdc97f57b6d9862eb0feab3d30`  
**Source geography:** `SW-GEO-V1`  
**Geometry engine:** Shapely 2.1.2

## Result

The new independent parcel-dossier audit passed **10/10 checks**. All **8 regression tests passed** in 18.931 seconds. The workflow then emitted the full read-only geometry report successfully.

## Verified inventory and relationships

| Measure | Result |
|---|---:|
| Geometry-derived parcel candidates | 420 |
| Parcel dossiers | 420 |
| Candidate parcel land area | 95,337,823.379 m² |
| Parcel interior overlap area | 0.000 m² |
| Parcel-to-road frontage candidates | 1,374 |
| Unreviewed parcel access-location candidates | 1,374 |
| Parcel adjacency relationships | 100 |
| Water adjacency relationships | 32 |
| Invalid parcel polygons | 0 |
| Parcels outside assigned neighbourhood/city | 0 |
| Parcels intruding into road reserve or mapped water | 0 |
| Incorrect/incomplete frontage relationships | 0 |
| Incorrect access-candidate points/statuses | 0 |
| Incorrect water-adjacency relationships | 0 |
| Missing, duplicate or incorrect parcel adjacency rows | 0 |

## What the independent audit verifies

1. Candidate and dossier identity sets match exactly, with 420 unique parcel candidates.
2. Every candidate is a valid, positive-area polygon contained by its assigned neighbourhood and the city boundary.
3. Parcel interiors exclude the dissolved road reserve and mapped water geometry.
4. Candidate parcel interiors have no overlap.
5. Frontage candidates are complete against the source road-segment reserve geometry: named road, contributing segment IDs, measured contact length and candidate point all reconcile.
6. Every parcel access-location candidate references a frontage candidate, coincides with its candidate point, and remains explicitly unreviewed and unclassified.
7. Water adjacency IDs and measured contact lengths match the source water polygons.
8. The parcel adjacency register is complete, uniquely ordered and has correct shared-boundary/corner-touch classification and measured lengths.
9. Manifest summary counts reconcile with the actual records.
10. The candidate-only authority boundary remains explicit.

## Regression coverage

The tests deliberately corrupt road references, frontage coordinates, access candidate coordinates, water adjacency, parcel adjacency and parcel geometry. The audit rejects each corrupted state. It also confirms no canonical address or operational access-point identity is created.

## Authority and persistence

This proves internal consistency of the generated fictional planning candidates only. It does not prove surveyed cadastral boundaries, legal road frontage, a usable driveway, an actual building entrance, an address, ownership or operational access.

- Canonical addresses created: **0**.
- Operational access points created: **0**.
- Operational seed eligible: **false**.
- Database writes performed: **false**.
- Neon production migration/import/seed: **none**.

The next work can reconcile the 1,374 parcel frontage/access candidates with the 768 building-boundary access-location candidates generated in Stage E. Such matching must remain a geometric candidate analysis; it must not assert actual entrances, driveways or usable access without supporting source evidence.
