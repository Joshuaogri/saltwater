# BP04-03 Stage C road centreline and corridor audit — run 0001

**Date:** 2026-11-24  
**Workflow:** [BP04-03 Stage B Disposable PostgreSQL, road audit extension](https://github.com/Joshuaogri/saltwater/actions/runs/45485282025)  
**Result:** PASS  
**Commit under test:** `2efc918fc245a524ce19a89b4fd4cdb0006af082`  
**Database:** no additional database writes; the workflow's disposable PostgreSQL checks remain unchanged  
**Production writes:** none

## Network inventory and topology

- 42 named roads.
- 685 road/bridge segments.
- 367 junction nodes.
- Segment classes reconcile to 482 local streets, 117 primary arterials, 84 district connectors and 2 bridges.
- The node graph has one connected component.
- All 367 declared node degrees match calculated endpoint degrees.
- Every segment is assigned to exactly one matching named road.
- Every segment's stored polyline begins and ends at the declared endpoint-node coordinates.
- No duplicate road or segment identifiers.
- Five Python road-corridor audit tests passed. Existing Stage B contract, importer and SQL acceptance tests also passed in the same workflow.

## Source-data exceptions

Two bridge segment lengths do not reconcile:

| Segment | Declared length | Measured stored polyline | Difference |
|---|---:|---:|---:|
| `SWS-0684` Harbour Bridge | 2,000m | 2,019.804m | +19.804m |
| `SWS-0685` Customs Bridge | 2,000m | 2,019.804m | +19.804m |

The source declarations and geometry are preserved. No source data was silently rewritten.

## Road corridor register

The deterministic generator emits one record per road and one per segment, retaining source identifiers, names, classes, direction, permitted modes, access, surface, endpoint references, centreline geometry, declared length and measured polyline length.

- All 685 road widths remain null/unresolved.
- All reserve polygons remain null.
- Reserve area assigned: 0 m².
- Road-reserve polygon generation: BLOCKED.
- The source has no surveyed road-edge geometry or right-of-way width; no width, offset, area deduction or frontage right is inferred.
- Candidate register SHA-256: `36fef2acb94d9248d7810d983117e73ee1c5dc8cf8570996a42cfcdd384f805e`.

The output is a width-agnostic source register, not a cadastral road-reserve layer and not operational geography.

## Scope

No parcel candidate geometry was altered. No operational addresses, property records, ownership, occupancy, businesses, road widths, reserve polygons or land-use deductions were created. No BP-02 operational geography approval was inferred. No Neon connection, write, upload or production activation occurred.

## Next

Reconcile the two bridge length exceptions against the intended route geometry, then obtain/define source-supported road-edge and right-of-way geometry before deriving reserve polygons. Continue parcel coverage/gap/overlap analysis only against those explicit source boundaries; keep unknown road-reserve land unclassified.
