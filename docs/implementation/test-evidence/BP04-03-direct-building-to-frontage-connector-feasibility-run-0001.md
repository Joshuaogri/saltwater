# BP04-03 direct building-to-frontage connector feasibility — run 0001

**Implementation commit:** `72b5cd12e05b4a77c6e1216348df9c4020ddd0f7`  
**Workflow:** [BP04-03 Direct Building-to-Frontage Connector Feasibility — successful run 45514361814](https://github.com/Joshuaogri/saltwater/actions/runs/45514361814)  
**Audit:** `runtime/building_access_connector_audit.py`  
**Regression suite:** `tests/pkg001/test_building_access_connector_audit.py`

## Defect found and correction

The first connector feasibility audit (run 45514079279) found that the existing second boundary-location candidate could generate a direct line crossing its own building interior. It reported 160 blocked candidates, 604 geometrically feasible candidates and four with no frontage candidate.

The Stage E generator was corrected:
- A01 continues to use the nearest building-boundary/frontage pair.
- A02 now searches 128 deterministic samples around the building boundary.
- A02 candidates must be separated from A01 by at least the greater of 5 metres or 10% of the building perimeter.
- A candidate line must be covered by the parent property and must not pass through the origin building interior.
- If no sampled line qualifies, the location remains a candidate and the audit will classify the connector as blocked; no route is invented.

## Successful result

The corrected workflow passed all **6 regression tests** and all **7 audit checks**.

| Measure | Result |
|---|---:|
| Building-boundary access-location candidates | 768 |
| Direct connector candidates tested | 764 |
| Geometrically feasible, unreviewed connector candidates | 764 |
| Blocked connector candidates | 0 |
| Candidates with no parcel frontage | 4 |
| Parent-property containment failures | 0 |
| Origin-building interior crossings among feasible connectors | 0 |
| Other-building interior crossings among feasible connectors | 0 |
| Mapped-water crossings among feasible connectors | 0 |
| Median straight-line connector length | 214.853 m |
| Maximum straight-line connector length | 332.870 m |

The four candidates without parcel frontage remain explicitly unresolved and are not included in the 764 direct connector candidates.

## Meaning and limitations

“Geometrically feasible” means only that the straight line between the generated building-boundary point and its same-parcel frontage candidate is contained by the generated parent-property polygon and avoids mapped building interiors and mapped water.

It does **not** establish a constructed driveway, entrance, gate, public/legal access, path surface, slope, gradient, barrier-free route, vehicle suitability, lighting, security, availability or emergency egress. These remain unknown/not assessed.

The connector audit is read-only. It reports candidate geometry but does not write connector records to Neon or promote them to operational access.

- Operational access points created: **0**.
- Canonical addresses created: **0**.
- Operational seed eligible: **false**.
- Database write performed: **false**.
- Neon production changes: **none**.

**Next:** add these connector geometries as provenance-bearing, non-operational candidate records in the generated Stage E manifest, with deterministic IDs and typed review/condition/measurement states; then test the manifest/importer and measure disposable storage before any production consideration.
