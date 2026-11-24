# SW-GEO-V1 geometric QA — run 0001

Date: 2026-11-24  
Workflow: [BP04-03 Geography Readiness Audit — successful run 45510749489](https://github.com/Joshuaogri/saltwater/actions/runs/45510749489)  
Verified commit: `2a107d902a4009afe2c47c633c2210297a29db41`

## Automated verification

The main-branch GitHub Actions workflow completed successfully.

- Existing BP04-03 structural readiness tests: **4 passed**.
- New geometric/routing QA regression tests: **9 passed**.
- Stable source-identity reconciliation tests: **5 passed**.
- Total: **18 Python tests passed**.
- Existing structural geography audit: **28/28 checks passed**.
- Stable source-to-entity_code mappings: **100 resolved, 0 unresolved**.
- New geometric/routing audit: **10/10 checks passed; zero failed checks**.

## Geometric/routing measurements

| Check | Result |
|---|---:|
| Polygon features checked | 36 |
| Point features checked | 18 |
| Invalid polygon rings / self-intersections | 0 |
| Point features outside city boundary | 0 |
| Neighbourhoods contained by assigned district | 24/24 |
| Neighbourhood interior overlap pairs | 0 |
| City boundary area | 108,000,000 m² |
| Sum of neighbourhood areas | 108,000,000 m² |
| Area difference | 0 m² |
| Road nodes | 367 |
| Road segments | 685 |
| Segment geometry/node/length exceptions | 0 |
| Road segments outside city boundary | 0 |
| Node-degree mismatches | 0 |
| Connected network components | 1 (all 367 nodes) |
| Route segment-sequence failures | 0 |

The audit checks polygon ring closure, non-zero area and self-intersection; point-in-city containment; neighbourhood containment within assigned district geometry; pairwise neighbourhood interior overlap; neighbourhood/city area balance; road segment endpoint geometry and measured polyline length; road-segment containment; graph degrees and connectivity; and ordered route-to-segment continuity.

## Scope and authority boundary

This is reproducible structural geometric QA for the fictional planning dataset SW-GEO-V1. It does not establish surveyed accuracy, cadastral parcel validity, legal frontage, confirmed entrances, address validity, calibrated travel times or operational dispatch acceptance. It does not approve BP-02 geography or authorize production activation.

- `operational_seed_eligible`: false.
- `geometry_import_performed`: false.
- `database_write_performed`: false.
- No Neon production migration, seed, import or write occurred.

Next dependency: continue BP-02 operational geography acceptance and cadastral/access review, keeping planning candidates separate from approved operational records.
