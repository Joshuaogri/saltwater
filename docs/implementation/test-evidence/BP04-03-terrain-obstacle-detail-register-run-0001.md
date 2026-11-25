# BP04-03 terrain and physical-obstacle detailed register — run 0001

**Register:** SW-TERRAIN-OBSTACLE-DETAIL-001  
**Source:** SW-GEO-V1  
**Operational approval:** none  
**Database writes:** none

## Detailed terrain record

The sole supplied terrain record is Central-Western Ridge (SW-TERR-001, low_ridge). The register preserves its original polygon and adds reproducible planar geometry descriptors: area, perimeter, bounding box, centroid, exterior/interior ring counts, ring closure, individual boundary-edge IDs, endpoint coordinates, planar edge lengths and coordinate bearings.

It overlays the terrain geometry with the 8 district geometries and 24 neighbourhood geometries, retaining positive-area intersections and calculating each intersection's area and share of the terrain polygon. It also intersects the 768 route-corridor centreline candidates and retains candidate IDs and geometric intersection lengths. These are geometry-derived relationships, not physical access or terrain traversal assessments.

## Obstacle classes and source coverage

The register maintains distinct source classes for retaining structures, walls, fences, gates, drainage structures, natural barriers and other physical obstacles. The current source supplies no records in these classes. Each class is marked NO_SOURCE_RECORDS_SUPPLIED with absence_claim false; no fictional obstacle is fabricated to fill the gap.

## Explicitly unassessed

Elevation, vertical datum, slope/gradient, slope direction, ground surface, material, condition, physical barrier continuity, passability, accessibility, legal access and emergency egress remain unassessed. Bearings describe polygon boundary direction in the local coordinate plane; they are not slope directions. Planar area/perimeter are not ground-survey measurements.

## Acceptance boundary

The detail register is a read-only derived candidate artifact. No operational terrain or obstacle assets, addresses, access points or approved paths are created. No Neon connection, migration, import or write is performed.

## Executed result — 2026-11-25

- Terrain records: 1; obstacle source records: 0.
- Terrain planar area: 5,100,000.000 m²; planar perimeter: derived from the nine source boundary edges.
- Boundary edge records: 9, all positive length; one closed exterior ring.
- Positive-area neighbourhood overlays: 5; overlay areas reconcile to the terrain polygon area.
- Route-corridor centreline candidates supplied: 768; terrain geometry intersections: 47, each retained with route-candidate and source-connector lineage.
- Elevation/gradient/traversability/obstacle-condition assessments: 0.
- Operational obstacle records: 0; operational seed eligibility: false.
- Regression tests: 5 passed. All 7 register checks passed.
- GitHub Actions: [detail-register workflow run 45566205681](https://github.com/Joshuaogri/saltwater/actions/runs/45566205681).
- Read-only artifact: [bp04-03-terrain-obstacle-detail-register](https://github.com/Joshuaogri/saltwater/actions/runs/45566205681/artifacts/15000356249), uploaded size 3,319 bytes; ZIP SHA-256 f8d2a4622f025d44c87963521f554a92d07e1d0e7351f5c4ee89edc36086195a.
- Database migration validation: [run 45566205655 passed](https://github.com/Joshuaogri/saltwater/actions/runs/45566205655). The separate PKG-001 disposable PostgreSQL validation was still running at evidence capture.
