# BP04-03 — Stage B Parcel Candidate Generation Run 0001

**Date:** 2026-11-24  
**Branch:** `main`  
**Commit under test:** `498b56413267a7107ec1045bd57958866c312804`  
**Workflow:** [BP04-03 Stage B Parcel Candidate Generation — run 45482818681](https://github.com/Joshuaogri/saltwater/actions/runs/45482818681)  
**Result:** PASS

## Scope

Generated a deterministic, planning-grade parcel/block candidate layer from the committed SW-GEO-V1 neighbourhood rectangles and road-segment geometry. The generator is pure Python and does not connect to PostgreSQL, Neon or any production service.

## Implementation

- Generator: [runtime/parcel_candidate_generator.py](../../../runtime/parcel_candidate_generator.py)
- Tests: [tests/pkg001/test_parcel_candidate_generator.py](../../../tests/pkg001/test_parcel_candidate_generator.py)
- Workflow: [bp04-03-parcel-candidates.yml](../../../.github/workflows/bp04-03-parcel-candidates.yml)
- Output artifact: [bp04-03-stage-b-parcel-candidates.json](https://github.com/Joshuaogri/saltwater/actions/runs/45482818681/artifacts/14961918786)

The generator partitions each of the 24 neighbourhood rectangles into 500m planning cells, applies a 15m inset as an explicitly unapproved candidate road-reserve allowance, and checks road frontage against actual committed road-segment geometry. Cells intersecting mapped harbour/canal water feature bounding boxes are excluded and recorded as unresolved rather than filled with invented land parcels.

## Results

- Python tests: 5 passed.
- Candidate parcel/block polygons: 396.
- Neighbourhoods represented: 24 of 24.
- Water-conflict cells excluded and recorded: 36.
- Candidate polygons with at least one matching road-edge segment: 392.
- Candidate polygons with no supported road-edge match: 4.
- Spatial IDs assigned: 0.
- Canonical addresses created: 0.
- Source-to-spatial-ID mappings resolved: 0; all 100 remain unresolved.
- Operational approval: false.
- Candidate manifest SHA-256: `6afc12c8e27717523bb581057da8c936481b1950faa5703f52bb5e7560e8cba4`.
- Uploaded artifact size: 11,656 bytes (compressed artifact ZIP).

## Important limitations

These are **500m block-scale planning candidates**, not final cadastral parcels. The output is a reproducible spatial candidate framework, not a surveyed or approved parcel fabric. The 15m inset is a generator assumption, not an approved road right-of-way. Water conflict detection uses feature bounding boxes for conservative exclusion; it does not calculate exact polygon intersections. Road-edge matches prove geometric coincidence only, not legal frontage, actual access, safe approach or operational routing. Candidate land-use labels are generated design classifications derived from adopted neighbourhood roles; development state remains unknown.

No canonical street numbers, address IDs, parcel spatial IDs or operational source mappings are created. No BP-02 geography approval is inferred. No database was connected or written. No Neon production access or write occurred.

## Next

Refine the candidate layer into a true parcel fabric using exact water polygon clipping and explicit road-reserve geometry; validate complete coverage, topology, gaps, overlaps, frontage, and per-neighbourhood land-use capacity. Only after those checks should candidate records be loaded into a disposable PostgreSQL database for acceptance and storage measurement. Address candidates remain blocked until road/source identity mapping and BP-02 authority are resolved.
