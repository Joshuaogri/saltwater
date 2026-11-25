# BP04-03 terrain and physical-obstacle survey coverage grid — run 0001

**Grid:** SW-TERRAIN-SURVEY-GRID-001  
**Source:** SW-GEO-V1  
**Cell size:** 500 m × 500 m  
**Operational approval:** none  
**Database writes:** none

## Purpose

A deterministic citywide coverage index divides the 12,000 m × 9,000 m planning extent into 432 survey cells. Each cell retains geometry, district and neighbourhood intersections, generated property/building candidate references, road-segment intersections, route-corridor midpoint assignments, terrain/water intersections and explicit evidence-coverage states.

Cells are survey planning units only. They are not parcels, physical objects, survey results or operational geography.

## Evidence boundary

The grid reports source counts and assessment gaps. It does not infer elevation, terrain condition, slope, obstacles, drainage, surface, access rights, route traversability, accessibility or emergency egress. A zero source count means the current source supplied no such record; it is not an absence assertion. Survey priorities remain unranked.

## Acceptance boundary

Every property/building candidate must be assigned to one cell, grid area must reconcile to city area, and all assessments remain unassessed. No production database operations occur.
