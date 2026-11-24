# BP04-03 — Stage B Parcel Candidate Generation Run 0001

**Date:** 2026-11-24  
**Branch:** `main`  
**Initial generator commit:** `498b56413267a7107ec1045bd57958866c312804`  
**Exact-clipping refinement commit:** `fe43f94f01a8ba981e11c4448c36a669cbc2360a`  
**Topology-validation refinement commit:** `c6d4c72d70e377a9a939cb891c9bb34c28b38d05`  
**Workflow:** [BP04-03 Stage B Parcel Candidate Generation — run 45482818681](https://github.com/Joshuaogri/saltwater/actions/runs/45482818681)  
**Initial result:** PASS  
**Refined exact-clipping result:** PASS ([run 45483557867](https://github.com/Joshuaogri/saltwater/actions/runs/45483557867))  
**Topology-validation result:** PASS ([run 45483804394](https://github.com/Joshuaogri/saltwater/actions/runs/45483804394))

## Scope

Generated a deterministic, planning-grade parcel/block candidate layer from the committed SW-GEO-V1 neighbourhood rectangles and road-segment geometry. The generator is pure Python and does not connect to PostgreSQL, Neon or any production service.

## Implementation

- Generator: [runtime/parcel_candidate_generator.py](../../../runtime/parcel_candidate_generator.py)
- Tests: [tests/pkg001/test_parcel_candidate_generator.py](../../../tests/pkg001/test_parcel_candidate_generator.py)
- Workflow: [bp04-03-parcel-candidates.yml](../../../.github/workflows/bp04-03-parcel-candidates.yml)
- Exact clipping implementation: Stage B generator version 2, using Sutherland–Hodgman clipping of each supported single-ring water Polygon against each 500m cell.
- Output artifact: [bp04-03-stage-b-parcel-candidates.json](https://github.com/Joshuaogri/saltwater/actions/runs/45482818681/artifacts/14961918786)

The generator partitions each of the 24 neighbourhood rectangles into 500m planning cells, applies a 15m inset as an explicitly unapproved candidate road-reserve allowance, and checks road frontage against actual committed road-segment geometry. Cells with positive-area intersection against the actual mapped harbour/canal water polygon rings are excluded and recorded with the exact measured intersection area rather than filled with invented land parcels. Boundary-only contact has zero intersection area and is not treated as a water overlap.

## Results

- Initial Python tests: 5 passed.
- Exact-clipping Python tests: 7 passed, including exact clipped-area calculations, zero-area boundary touch and fail-closed rejection of water polygons with interior holes.
- Topology-refined Python tests: 8 passed, including neighbourhood containment, zero candidate-interior overlaps and source grid-cell count reconciliation (432).
- Candidate parcel/block polygons: 396.
- Neighbourhoods represented: 24 of 24.
- Water-conflict cells excluded and recorded: 36.
- Candidate polygons with at least one matching road-edge segment: 392.
- Candidate polygons with no supported road-edge match: 4.
- Spatial IDs assigned: 0.
- Canonical addresses created: 0.
- Source-to-spatial-ID mappings resolved: 0; all 100 remain unresolved.
- Operational approval: false.
- Initial candidate manifest SHA-256: `6afc12c8e27717523bb581057da8c936481b1950faa5703f52bb5e7560e8cba4`.
- Exact-clipping manifest SHA-256: `4da7999ef7b5f98b3b1214096f11fbce633317ae38585ca231f6f8131c3c39bf`.
- Topology-refined manifest SHA-256: `83ec53dc09f51483110e1e564b82919d2da63a0f5c5adcd92b42e04bf508f85f`.
- Latest artifact: [run 45483804394 artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45483804394/artifacts/14962257890), 12,033 bytes compressed.
- Uploaded artifact size: 11,656 bytes (compressed artifact ZIP).

## Important limitations

These are **500m block-scale planning candidates**, not final cadastral parcels. The output is a reproducible spatial candidate framework, not a surveyed or approved parcel fabric. The 15m inset is a generator assumption, not an approved road right-of-way. The refined generator calculates exact polygon-to-cell intersection area for the current SW-GEO-V1 water features, which are single-ring Polygon geometries. It fails closed for water polygon holes and unsupported geometry types. This is exact for the current supported input geometry, not a general GIS overlay engine. Road-edge matches prove geometric coincidence only, not legal frontage, actual access, safe approach or operational routing. Candidate land-use labels are generated design classifications derived from adopted neighbourhood roles; development state remains unknown.

No canonical street numbers, address IDs, parcel spatial IDs or operational source mappings are created. No BP-02 geography approval is inferred. No database was connected or written. No Neon production access or write occurred.

## Topology checks

The generator now independently checks every candidate interior against its source neighbourhood envelope and performs pairwise candidate-interior overlap checks within each neighbourhood. The 432 source 500m grid cells reconcile with 396 candidate parcels plus 36 water-intersecting excluded cells. All candidate interiors are contained within their source neighbourhoods; zero candidate-interior overlaps and zero out-of-neighbourhood candidates were found. This is an internal geometry/topology check on generated rectangles, not a full cadastral topology validation: the unallocated area includes provisional 15m grid insets and excluded cells and is not classified as road, public space or developable land.

## Remaining limits and next

The 15m inset is still a provisional grid assumption, not an approved road-reserve polygon. The candidate output is not a final parcel fabric and does not prove legal access, road connectivity, land ownership, development state or surveyed boundaries. The current exact water overlay supports simple single-ring Polygon inputs; holes and MultiPolygon geometry fail closed. Neighbourhood coverage, candidate overlap/gap topology and land-use capacity still require explicit validation. Next, implement a disposable PostgreSQL ingestion adapter that maps candidate IDs to test-only BP-02 identities, preserves all provenance and geometry checksums, measures storage, and rolls back or recreates the disposable database for repeatability. No operational identity or canonical address is to be allocated. Address candidates remain blocked until road/source identity mapping and BP-02 authority are resolved.
