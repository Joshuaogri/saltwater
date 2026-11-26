# BP-02 address placement review register

**Date:** 2026-11-26  
**Status:** STRUCTURAL ACCEPTANCE PASSED — full audit run 45831361588; operational geography release remains blocked  
**Scope:** Read-only GitHub source and disposable CI validation. No Neon writes.

## Purpose

The BP04-to-BP02 reconciliation now produces a deterministic 420-record review queue from the stable SWP/SWA design identity register and the building-access road reconciliation. It consolidates the original address road, parcel frontage candidate roads, building-access candidate roads, stable design IDs and review priority without changing source facts.

## Review classification

- **P1 — ROAD_REFERENCE_CONFLICT:** source address road differs from the parcel's geometric frontage-road candidate set.
- **P1 — NO_PARCEL_FRONTAGE_EVIDENCE:** the parcel has no geometric frontage-road candidate.
- **P2 — NO_BUILDING_ON_PROPERTY_SITE:** the property site has no candidate building; this is not automatically an address defect.
- **P2 — BUILDING_ACCESS_ROAD_REVIEW:** building-access road evidence exists but does not resolve to the source road.
- **P3 — SOURCE_CONTEXT_COHERENT_CANDIDATE:** source road agrees with available parcel-frontage and building-access candidate evidence.

The register preserves the source road even where a single alternative road is proposed. It never substitutes the alternative, creates a postal number, infers a constructed entrance, or upgrades geometric contact to legal or operational access.

## Fail-closed invariants

- Exactly one review record per source address.
- Every source address resolves to one stable design parcel identity.
- Every review record has a corresponding building-access reconciliation record.
- Duplicate/missing parcel, address or access evidence causes an error.
- Every record remains non-operational and unapproved.
- The output explicitly reports zero operational approvals and no database write.

## Current interpretation

The current source reconciliation baseline has 420 addresses:
- 415 source-road/frontage candidate matches.
- 3 source-road/frontage conflicts, each with a single alternative candidate retained for review.
- 2 addresses with no parcel frontage candidate.
- Building-access evidence covers 1,474 building candidates and 2,948 building-boundary access candidates. It resolves a source-road match for 384/420 property sites with building candidates; 36 sites have no generated building candidates and are classified separately.
- The three frontage-road conflicts occur on sites with no generated building candidates. Their single alternative frontage candidates are preserved for review: `SWR-H17` for two addresses and `SWR-H01` for one.
- The two parcels without boundary-frontage candidates do have building-access road-reserve proximity candidates matching their source roads: `SWR-B2` and `SWR-B1`. Both are `POINT_CONTACT_ONLY`, so they do not establish a driveway, traversable route or legal/operational access.
- The review queue contains 5 P1 records (3 road-reference conflicts and 2 no-frontage cases), 33 P2 records (no-building observations not already classified P1), and 382 P3 source-context-coherent candidates. The 36 no-building sites include the three P1 road conflicts.

The 415 direct parcel-frontage road matches remain coherent. Building presence and access evidence are tracked independently; the two no-frontage cases have separate proximity-only building access candidates.

## Verification

The dedicated BP04 player/police/geography workflow passed in [run 45688271976](https://github.com/Joshuaogri/saltwater/actions/runs/45688271976): 120 tests passed, and the complete 420-address reconciliation plus review-register generation succeeded. The review register is an audit aid only. It does not constitute BP-02 operational geography approval, canonical address promotion, Neon permission provisioning or BP04 full acceptance.
## Geometry-based disposition of the five P1 exceptions

The five exceptions were cross-checked against the actual SW-GEO-V1 road IDs, road classes, parcel frontage candidates and building-access candidate types:

| Source address | Source road | Geometry candidate | Disposition |
|---|---|---|---|
| `SWADDR-BPCSWD03N301701` | Dock Street (`SWR-V16`) | North Coast Road (`SWR-H17`) | Unique parcel-frontage road association identified; source value retained as provenance |
| `SWADDR-BPCSWD03N301801` | Ropewalk Road (`SWR-V17`) | North Coast Road (`SWR-H17`) | Unique parcel-frontage road association identified; source value retained as provenance |
| `SWADDR-BPCSWD05N100201` | West Coast Road (`SWR-V01`) | South Coast Road (`SWR-H01`) | Unique parcel-frontage road association identified; source value retained as provenance |
| `SWADDR-BPCSWD04N100402` | Customs Bridge (`SWR-B2`) | Two feasible property-contained connector candidates to bridge reserve | Bridge endpoints connect to public streets; entrance engineering and operational verification remain outstanding |
| `SWADDR-BPCSWD08N101802` | Harbour Bridge (`SWR-B1`) | Two feasible property-contained connector candidates to bridge reserve | Bridge endpoints connect to public streets; entrance engineering and operational verification remain outstanding |

The first three are resolved to a unique geometric frontage candidate, not to a final address. The last two cannot be promoted as bridge-frontage addresses. All five original road references are retained. No canonical address or operational access point is approved.

## Consolidated BP-02 audit

`runtime/bp02_full_acceptance_audit.py` consolidates the existing independent geometry audits for city/neighbourhood/road topology, parcel polygons/frontages/adjacency, property/building/access-point hierarchy, connector topology and route-corridor candidates, then adds the BP04 address/property reconciliation and exception dispositions. CI runs the audit and publishes a JSON evidence artifact. Structural pass and operational release are separate outcomes. The operational gate remains blocked while SW-GEO-V1 is unapproved, canonical addresses are unmaterialised and no operational access points are approved.

See `runtime/bp02_address_frontage_exception_resolution.py`, `runtime/bp02_full_acceptance_audit.py`, and `.github/workflows/bp02-full-acceptance-audit.yml`.

## Follow-up connector and road-network evidence review — 2026-11-26

The full BP02 acceptance audit previously used only parcel-frontage candidates and the `POINT_CONTACT_ONLY` bridge classification when disposing the five exceptions. That omitted the separately generated direct access-connector audit and the bridge endpoint topology. The resolver now consumes both evidence layers:

- The three source-road conflicts each have exactly one parcel-frontage road candidate. The derived road association is therefore resolved to North Coast Road (`SWR-H17`) for two records and South Coast Road (`SWR-H01`) for one. Original source-road values remain immutable provenance; canonical address promotion is still separate.
- Customs Bridge (`SWR-B2`) and Harbour Bridge (`SWR-B1`) each have two direct connector candidates from building-boundary access points. All four are classified `DIRECT_GEOMETRY_FEASIBLE_UNREVIEWED`, remain within their property, and do not cross mapped buildings or water.
- Both bridge segments connect at both endpoints to public motor-vehicle/emergency street segments. The connector candidates therefore reach a connected public road network at design-geometry level.
- The two bridge access associations can be dispositioned as geometric access-connection candidates, rather than left as unexplained point contacts. They are not confirmed entrances: width, gradient, surface, drainage, clearance, access controls and operational approval remain outstanding.

The updated resolver and regression tests are committed on `main`. The complete full-parcel/address/access acceptance workflow passed in [run 45831361588](https://github.com/Joshuaogri/saltwater/actions/runs/45831361588) on 2026-11-26. The published artifact `bp02-full-parcel-address-access-acceptance` reports `STRUCTURAL_PASS_OPERATIONAL_RELEASE_BLOCKED`: all 12 structural checks passed; all six geometry/access layers reported zero failed checks; all five exception dispositions are resolved; and there are zero unresolved address-road/access exceptions. The report confirms 420/420 property-address links, 2,948 connector candidates, 1,474 building candidates, 2,926 direct-geometry-feasible unreviewed connectors and 22 blocked direct lines. No canonical addresses, operational access points, database writes or Neon writes were created. No source geography, BP04 source address or operational status was promoted by this review.


## Verified BP-02 structural acceptance — 2026-11-26

The successful run's acceptance artifact confirms the structural result and preserves the operational boundary:

- Overall status: `STRUCTURAL_PASS_OPERATIONAL_RELEASE_BLOCKED`.
- Structural status: `PASS`; all 12 structural assertions are true.
- All five former P1 address/access exceptions have evidence-based geometric dispositions; `unresolved_address_road_access_exceptions = 0`.
- The three source-road conflicts resolve to unique parcel frontage associations (`SWR-H17` twice and `SWR-H01` once), while both bridge records resolve to connected-public-road geometric access candidates (two property-contained connector candidates per bridge).
- The six layer audits (parcel geometry, geography geometry, building access candidates, direct access connectors, connector topology and route-corridor candidates) all report zero failed checks.
- The 22 direct connector lines that are not clear remain explicitly blocked; they are not silently treated as passable. The 2,926 feasible direct lines remain unreviewed geometric candidates.
- Operational release remains blocked because SW-GEO-V1 has not been approved as operational geography, canonical parcels/addresses are not materialised, no operational access points are approved, and bridge entrance engineering/operational validation is outstanding.

The run published the JSON evidence artifact `bp02-full-parcel-address-access-acceptance` (45,291-byte ZIP; artifact SHA-256 `d8a19a4098891a06dadcbc857b5c22037545371c28bb6251ed8e84b2626d6aaa`). This is CI evidence only. No production database or Neon writes were performed.

## Review of the 36 sites without generated building candidates — 2026-11-26

The 36-site observation has been reviewed against the Stage E generator contract and the available generated inventory evidence. It is **not possible to classify these sites as vacant, undeveloped, open space, reserved, under construction or otherwise unoccupied from the present records**.

The generator records each site's `site_state` as `unknown`, its boundary as `unverified`, and its geometry as a non-operational parcel candidate. A site receives no building candidate when the deterministic footprint search returns no feasible footprint, or when the generated land-use class is `open_space`. The current generated summary reports the total of 36 but does not preserve a per-site reason code that distinguishes those two paths. Nor does it establish real site condition, construction, occupancy, ownership, access or intended use.

Accordingly:

- The 36 records remain **NO_BUILDING_CANDIDATE — CAUSE UNCLASSIFIED**.
- No site is relabelled vacant or undeveloped.
- No building, premises, unit, room, business, occupancy or physical asset is created to fill the gap.
- No source land-use, site-state or address value is changed.
- The three road-conflict addresses already included in the five resolved geometric exception dispositions remain separate address-provenance matters; the 36-site count is not an additional address-road exception count.
- A future classification requires a source-backed site-use/state field or an explicitly authored fictional world-state decision, not inference from the absence of a generated footprint.

This closes the current evidence review without expanding the frozen BP04 inventory. It does not change the BP02 structural pass or the operational geography release blocker. No database or Neon write, canonical promotion, operational access approval or permission grant was performed.
## Bridge connector engineering-data completeness review — 2026-11-26

## Explicit property identity lineage correction — 2026-11-26

The five-exception reconciliation previously derived a candidate property ID by removing the `SWADDR-` prefix from a source address ID and adding `SWP-`. This relied on two independent identifiers sharing a suffix, rather than using the authoritative BP04 address-to-property relationship. That implicit naming convention has been removed.

The BP04-to-BP02 reconciliation now carries the exact `property_id` from the validated address identity row into each frontage-exception evidence record. Bridge connector candidates are matched against that explicit property reference. A missing property reference fails closed and cannot resolve a bridge connector. The regression test deliberately uses a property ID unrelated to the source address ID suffix and confirms the explicit relationship is used.

The 36 no-building-site records continue to be linked through the source property and candidate parcel relationships; their absence of buildings is not treated as an address or identity failure. This correction does not change any property, parcel, address or connector identity and does not approve operational access. Full BP02 acceptance workflow is running for the updated source and test code; results will be recorded after completion. No Neon write or promotion was performed.


The four geometric connector candidates associated with Customs Bridge (`SWR-B2`) and Harbour Bridge (`SWR-B1`) were checked against the Stage E connector generator, direct-connector audit, route-corridor candidate audit and terrain/obstacle source model.

| Engineering item | Evidence available | Assessment |
|---|---|---|
| Connector geometry | Two-dimensional centreline coordinates and parent-property containment checks | Candidate geometry only; not a surveyed or constructed path |
| Connector width / clear width | Route-corridor output has `available_width_m=null` and `corridor_width_m=null`; width assessment state is `NOT_ASSESSED_NO_WIDTH_OR_CLEARANCE_SOURCE` | Not assessed |
| Gradient / slope | Connector `slope_state=not_assessed`; route-corridor gradient state is `not_assessed_no_elevation_source`; terrain source model has no elevation surfaces, contours or spot elevations | Not assessed |
| Surface / construction | Connector `surface_code=unknown`; corridor `surface_state=unknown`; no construction or material inspection | Unknown |
| Drainage | No verified connector drainage dimensions, structures, condition or flow data; source terrain inventory does not establish drainage at these connectors | Not assessed |
| Vertical / overhead clearance | No verified vertical profile, overhead obstruction or clearance measurements | Not assessed |
| Building / mapped-water clearance | Independent geometry audit checks mapped building and water intersections; route-corridor layer can calculate planar minimum clearances to mapped features | Two-dimensional geometric evidence only; not physical or vehicle clearance |
| Access controls | Access-point `control_type=unknown`; directionality and access modes are unknown/empty | Not assessed |
| Legal/public access and emergency egress | No rights, gates, operating controls, emergency egress or traversability evidence | Not established |
| Entrance verification | No surveyed entrance, door/gate interface, construction record or field verification | Not verified |

The generator explicitly states that each connector line is derived from generated building-boundary and parcel road-connection candidates; construction, legal access, surface, gradient and route usability are not assessed. The route-corridor audit deliberately produces a centreline rather than a corridor polygon because no supported width source exists. Successful geometric checks must not be interpreted as engineering acceptance.

**Disposition:** all four connectors remain `UNREVIEWED_GEOMETRIC_LINE_ONLY`. The two bridge cases retain their previously established design-geometry connection to a public road network, but neither is engineering-ready nor operationally approved. No numerical width, gradient, surface, drainage, clearance or control values are invented.

**Minimum evidence needed to advance:** a site-specific surveyed entrance and connector alignment; measured clear width and vertical clearance; level/elevation survey for longitudinal and crossfall gradients; documented surface and construction condition; drainage inspection; mapped and inspected physical obstacles; access-control/gate details; and a competent review of vehicle/emergency suitability and legal/public access. Evidence must be attached to each of the four candidate connector identities, not inferred from the bridge road segment generally.

This review closes the current source-schema completeness check. It does not close the engineering work, approve an entrance, promote a canonical address or operational access point, or change BP02's `STRUCTURAL_PASS_OPERATIONAL_RELEASE_BLOCKED` status. No source data, property inventory or Neon data was changed.
