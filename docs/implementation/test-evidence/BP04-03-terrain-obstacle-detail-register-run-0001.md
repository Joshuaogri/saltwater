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
