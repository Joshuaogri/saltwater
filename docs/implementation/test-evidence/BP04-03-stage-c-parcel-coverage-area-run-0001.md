# BP04-03 Stage C parcel coverage area reconciliation — run 0001

**Date:** 2026-11-24  
**Workflow:** [BP04-03 Stage B Disposable PostgreSQL](https://github.com/Joshuaogri/saltwater/actions/runs/45486168411)  
**Result:** PASS  
**Commit under test:** `535f307ada92b71252325e3efe2fd2ae3090fd75`  
**Database:** no production database; area analysis is deterministic Python over SW-GEO-V1 and the generated candidate manifest  
**Production writes:** none

## Area balance

The source contains 24 rectangular neighbourhood polygons covering 108,000,000 m². Their envelopes reconcile exactly to 432 source grid cells of 250,000 m² each.

| Area class | Area |
|---|---:|
| Full neighbourhood/source grid envelope | 108,000,000 m² |
| Candidate-eligible cell envelopes (396 cells) | 99,000,000 m² |
| Candidate parcel interiors (396 polygons) | 87,476,400 m² |
| Exact water polygon intersections in 36 excluded cells | 5,740,000 m² |
| Full envelopes of 36 water-hit cells | 9,000,000 m² |
| Provisional 15m inset residual inside candidate-eligible cells | 11,523,600 m² |
| Non-water remainder inside the 36 excluded cell envelopes | 3,260,000 m² |
| Total unallocated area (excluding exact water intersection and candidate parcels) | 14,783,600 m² |
| Area balance delta | 0 m² |

The accounting identity is:

`108,000,000 = 87,476,400 + 5,740,000 + 14,783,600`

The 14,783,600 m² unallocated total is fully decomposed into the 11,523,600 m² provisional inset residual and 3,260,000 m² non-water remainder within cells excluded because they intersect water.

## Interpretation and limits

- Exact water area is computed from the current SW-GEO-V1 single-ring axis-aligned rectangular water polygons. Water polygon overlap is checked and rejected to prevent double counting.
- A cell is excluded in full if any water polygon intersects it; the non-water remainder inside such a cell is not assumed developable.
- The 15m inset is a generator assumption only. Its 11,523,600 m² residual is not a measured road reserve, footway, verge, public space or other land category.
- The 3,260,000 m² non-water remainder in water-hit cell envelopes is unresolved.
- The 87,476,400 m² candidate area is not a final cadastral parcel area or approved developable land.
- No property/building/premises/unit/access-point count or capacity is inferred from area.
- All 24 neighbourhoods receive an individual coverage record in the generated artifact.
- Operational approval remains false. No canonical addresses, operational spatial IDs or property inventory were created.

## Preserved artifacts

- Parcel coverage audit: [run 45486168411 artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45486168411/artifacts/14964432302), compressed size **1,713 bytes**, archive SHA-256 `8469dd6a09553c928b773c31724d98eec079828142449b47b18805b51741d07e`.
- Road corridor register: [run 45486168411 artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45486168411/artifacts/14964487149), compressed size **15,676 bytes**, archive SHA-256 `c27afcb551eaf91c69fe63bdb5f654ad92bb0f82c3e6cd6b03b1afee87868d32`.

## Next

Reconcile the two bridge length source exceptions and establish road-edge/right-of-way geometry before classifying any inset residual. Then proceed to parcel gap/overlap and neighbourhood-boundary topology against explicit, versioned boundary geometry.
