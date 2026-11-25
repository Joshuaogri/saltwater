# BP04-03 terrain and physical-obstacle source inventory — run 0001

**Model:** SW-TERRAIN-OBSTACLE-001  
**Source:** SW-GEO-V1  
**Operational approval:** none  
**Production database writes:** none

## Source inventory

The current geography dataset contains 54 features: one city-state boundary, eight districts, 24 neighbourhoods, one harbour-water feature, one constructed-water feature, one terrain feature and 18 landmarks.

The physical-source inventory recognises elevation surfaces, contour lines, spot elevations, terrain features, retaining structures, walls, fences, gates, drainage structures, natural barriers and other physical obstacles. The present source contains:

- 1 mapped terrain feature: SW-TERR-001 — Central-Western Ridge (low_ridge).
- 0 elevation surfaces, contour lines or spot elevations.
- 0 mapped retaining structures, walls, fences, gates or drainage structures.
- 0 mapped natural barriers or other physical-obstacle records.

A zero count means no such feature is supplied in this source dataset. It does not establish that no such feature exists in the fictional world.

## Record contract

Each sourced feature is retained with source dataset/version, stable source feature ID, source geometry and attributes, source reference, actor/generator, confidence and review state. The model reserves typed fields for elevation and vertical datum; gradient; obstacle height/width/material/condition/continuity; traversal restriction; pedestrian/vehicle passability; accessibility; legal access; and emergency egress.

Where no source supplies a value, numeric values remain null and assessments remain unknown or not assessed. No zero is substituted for missing measurements. No obstacle is invented. A terrain polygon is not treated as a DEM, contour, slope, wall or impassable barrier.

## Route-corridor implications

The 47 route-centreline intersections with Central-Western Ridge remain terrain-context references only. No elevation, grade, cross-slope, retaining wall, path surface, drainage crossing, clear width, passability or route suitability is derived. Existing 768 route-corridor centreline candidates remain unreviewed candidates, not approved access routes.

## Acceptance boundary

The source inventory is non-operational, read-only and deterministic. It does not create operational terrain/obstacle identities, addresses, access points or route approvals. It performs no Neon connection, migration, import or write. The established storage estimate and explicit approval gate remains mandatory before any production database operation.
