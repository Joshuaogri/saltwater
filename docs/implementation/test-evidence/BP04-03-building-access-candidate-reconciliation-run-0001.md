# BP04-03 building-access candidate reconciliation — run 0001

**Date:** 2026-11-24  
**Workflow:** [BP04-03 Building Access Candidate Reconciliation — successful run 45512496892](https://github.com/Joshuaogri/saltwater/actions/runs/45512496892)  
**Verified implementation commit:** `78cc8a767e3ca73813131dd23a26ceb9deea7e11`  
**Geometry engine:** Shapely 2.1.2

## Result

All **7 regression tests passed** and all **8 independent audit checks passed**. The audit found a real data-quality defect in the previous generator: both building-boundary candidates inherited one road-frontage candidate selected using the building centroid. That did not guarantee the selected frontage was nearest to each individual access-location candidate.

The generator was corrected:
- Candidate A01 now selects the frontage with the shortest possible straight-line gap to the building boundary, then places the candidate at the nearest point on that boundary.
- Candidate A02 is placed at its deterministic boundary fraction and independently linked to its nearest parcel frontage candidate.
- Both candidates record the nearest-frontage candidate ID, straight-line gap in metres, matching basis and explicit unreviewed status.
- If a parcel has no frontage candidate, the building access candidate remains explicitly unlinked.

## Reconciled counts and measurements

| Measure | Result |
|---|---:|
| Property-site candidates | 420 |
| Building candidates | 384 |
| Building-boundary access-location candidates | 768 |
| A01 candidates with frontage link | 382 |
| A02 candidates with frontage link | 382 |
| Access candidates without parcel frontage | 4 |
| Incorrect/mismatched nearest-frontage links | 0 |
| Median straight-line gap to nearest frontage candidate | 220.500 m |
| Maximum straight-line gap to nearest frontage candidate | 351.102 m |

The four unlinked candidates belong to building candidates whose parent parcels have no identified road-edge frontage. They remain unlinked; no frontage, driveway or entrance was fabricated.

## Candidate facts and authority

The audit also verified:
- all 384 building footprints remain inside their parent property/parcel geometry;
- all 768 candidate points lie on their respective building boundaries and inside their parent property sites;
- each non-null frontage link resolves to a frontage candidate belonging to the same parcel;
- each linked candidate uses the nearest geometric frontage under deterministic distance/ID tie-breaking;
- the recorded straight-line gap matches the geometry;
- access type/modes, availability, accessibility, emergency egress and loading capability remain unknown or not assessed.

Straight-line proximity is not a route, driveway, entrance, public access right or emergency egress finding. Every building-boundary point remains `UNREVIEWED_BUILDING_BOUNDARY_CANDIDATE`.

- Canonical addresses created: **0**.
- Operational access points created: **0**.
- Operational seed eligible: **false**.
- Database writes performed by this audit: **false**.
- Neon production changes: **none**.

The updated generator was also exercised by the existing Stage E candidate-generation and disposable PostgreSQL workflows. The full Stage E disposable acceptance run is separately tracked in [run 45512496924](https://github.com/Joshuaogri/saltwater/actions/runs/45512496924).
