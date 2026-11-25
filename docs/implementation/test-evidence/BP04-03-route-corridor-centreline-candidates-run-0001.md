# BP04-03 route-corridor centreline candidates — run 0001

**Implementation commit:** `bd4a76609249a81de588822bb528a9f86bd9bebd`  
**Workflow:** [45520905232 — successful](https://github.com/Joshuaogri/saltwater/actions/runs/45520905232)  
**Generated manifest artifact:** `bp04-03-route-corridor-candidates` (45,079 bytes; 14-day GitHub Actions artifact)  
**Manifest SHA-256:** `abc492d6d1cd2f277f355ddfc8ec8a79f30d4721f34db72726d70381f6dc3471`

## Candidate inventory

| Measure | Result |
|---|---:|
| Source connector candidates | 768 |
| Route-corridor centreline candidates | 768 |
| Frontage centreline candidates | 764 |
| Point-contact/proximity centreline candidates | 4 |
| Unresolved connector candidates | 0 |
| Mapped building intersections | 0 |
| Mapped water intersections | 0 |
| Origin-building interior crossings | 0 |
| Linked road-reserve overlaps | 0 |
| Terrain-feature intersections | 47 |
| Regression tests | 6 passed |
| Independent checks | 7/7 passed |

The analysis carries forward stable connector, access-point, building, property, parcel, road, road-segment, frontage/proximity and source-manifest lineage. It checks each two-point centreline against its parent property, originating building footprint, all other generated building footprints, mapped harbour/canal water and the linked road-reserve segment geometry.

The minimum measured distance from any centreline to another generated building footprint is **31.894 m**; the maximum is **480.755 m**. This is a geometric separation measurement to other generated footprints, not available route width, a safety clearance, or a claim of traversability.

Forty-seven centrelines intersect the mapped Central-Western Ridge terrain feature. This is recorded as terrain context only. It is not treated as impassable, and no gradient or elevation is inferred.

## Explicit unknowns

All 768 records have:
- `available_width_m = null`;
- `corridor_width_m = null`;
- width assessment `NOT_ASSESSED_NO_WIDTH_OR_CLEARANCE_SOURCE`;
- surface `unknown`;
- gradient `not_assessed_no_elevation_source`;
- barriers, pedestrian/vehicle suitability, accessibility, legal/public access and emergency-egress `not_assessed`;
- route suitability `unknown`.

A route corridor polygon was deliberately not manufactured because no supported path-width or clear-width source exists. The output is a two-dimensional centreline candidate register, not an approved route network.

The four point-contact-only road-reserve cases remain separate from the 764 frontage candidates.

## Operational and persistence boundary

- Operational access points: **0**.
- Canonical addresses: **0**.
- Operational seed eligibility: **false**.
- Production database writes: **none**.
- Neon production size: unchanged at **9,306,112 bytes** on the last read-only measurement.
- Route-corridor candidate manifest: CI artifact only; no production migration or Neon import.

**Next:** enrich the terrain/elevation and physical-obstacle source model before assessing grade, path width, surface, barriers or actual route suitability. Keep every missing value explicit rather than estimating it from a two-dimensional line.
