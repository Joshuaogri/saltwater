# BP04-03 — Saltwater City Physical Inventory and Geography-Linked Population

**Status:** APPROVED — implementation on GitHub `main` and disposable PostgreSQL testing only  
**Target:** GitHub `main` only; disposable PostgreSQL 16 first  
**Depends on:** BP-02 canonical geography and parcel/address authority; BP-04-01 identity foundation; BP04-02 deep profiles; SW-UNS-001; SW-DB-001  
**Production authority:** NONE. This package does not authorise a Neon production connection, migration, seed, import, upload or configuration change.

## 1. Purpose

BP04-01 established immutable identities for properties, buildings, premises, units and access points. BP04-02 supplied detailed, versioned, provenance-aware physical profiles. BP04-03 is the separate city-inventory production package that will populate those structures with Saltwater's actual fictional built-world dataset and connect every applicable record to canonical geography.

The intended result is a detailed, internally consistent, city-wide physical inventory—not a list of names and IDs. It must support property/building/premises/unit/access-point dossiers, spatial search, dispatch and patrol location resolution, future business-site assignment, residence allocation and investigative location references.

The world remains one contiguous fictional island city-state, one city, eight districts and 24 neighbourhoods. BP04-03 must not create a second city, extra district or neighbourhood, external playable territory, or exceed the 10,000 living-person cap.

## 2. Verified starting point and hard dependencies

### 2.1 BP04 foundations

- BP04-01 identity foundation is implemented and passed full disposable PostgreSQL 16 acceptance.
- BP04-02 detailed profiles are implemented and passed full Python and disposable PostgreSQL 16 acceptance in [run 45478587738](https://github.com/Joshuaogri/saltwater/actions/runs/45478587738).
- BP04-02 provides versioned profiles for property, building, premises, unit and access point, plus structured measurement, floor, component, room, service, feature, condition, defect and assertion records.
- SW-UNS-001 is the sole naming authority. No BP04-specific naming registry or bypass is permitted.
- SW-DB-001 provides the disposable opening population/business fixture and shared 10,000-person cap proof. It does not supply physical asset geography.

### 2.2 BP-02 geography is not yet ready for operational inventory import

The committed [SW-GEO-V1 map register](../../maps/README.md) and [geography dataset](../../../data/geography/saltwater-geography-v1.json) are planning-grade fictional geometry. They contain the adopted 8 districts, 24 neighbourhoods, 42 named roads, 367 junction nodes, 685 connected road/bridge segments and 5 route definitions.

The map register explicitly records that:
- parcel fabric and canonical numbered addresses do not yet exist;
- building footprints and entrances do not yet exist;
- the 100 source-to-spatial-ID mappings remain unresolved;
- the map baseline is `DESIGN_BASELINE_NOT_YET_USER_APPROVED_FOR_OPERATIONAL_SEED`;
- graph structure checks are not full geometry QA or operational routing acceptance.

**Precondition:** BP04-03 may develop and test a disposable parcel/address/asset candidate, but it must not silently treat SW-GEO-V1 as an approved operational spatial authority. Before a production-grade inventory is designated canonical, the geography mapping gaps, parcel/address layer, geometry QA and map approval must be resolved through BP-02's own authority and version controls. A BP04 package cannot approve BP-02 on the user's behalf.

## 3. Delivery boundaries

This package is divided into controlled stages. Each stage must produce a reproducible manifest, validation output and storage measurement.

### Stage A — geography readiness and reconciliation

1. Reconcile the full source geography inventory against stable BP-02 IDs.
2. Resolve the 100 outstanding source-to-spatial-ID mappings; record every source row, destination ID, mapping status, rationale and reviewer/source provenance.
3. Validate the eight district and 24 neighbourhood polygons, boundaries, containment, adjacency, overlaps/gaps and point-in-polygon assignment rules.
4. Validate the 42 named roads, 367 junctions, 685 segments and five routes against the actual committed dataset; verify endpoint integrity, parent-road membership, connectedness and access semantics.
5. Confirm the authoritative geography version and its approval status. Preserve SW-GEO-V1 unchanged; any correction is a new version with explicit predecessor/successor history.
6. Do not fabricate a parcel, street number, road entrance or coordinate to make a failed mapping pass.

**Gate A:** no city-wide physical inventory seed is eligible until the geography source map, mapping register, parcel/address model and approval state are explicit and internally consistent.

### Stage B — parcel fabric and canonical address layer

BP-02 owns parcel and address identities. BP04-03 consumes those IDs and must not create competing parcel/address registries.

Create a coherent fictional parcel fabric for the whole city-state:
- parcels cover buildable, developed, vacant, open-space, transport, port, utility, civic and other land-use areas as applicable;
- parcel polygons are valid, non-overlapping except for explicitly governed special cases, contained by the city boundary and assigned to exactly one neighbourhood under the adopted deterministic boundary rule;
- parcel splits, amalgamations, boundary corrections and retirement preserve predecessor/successor history;
- each parcel has land-use, development/status, area basis, geometry version, provenance and confidence;
- every address is a structured, stable BP-02 address ID linked to its parcel, locality and road/locator where applicable;
- street numbers and local locators are deterministic and unique within their defined address scope;
- addresses retain aliases and effective history; no duplicate active canonical address;
- multi-frontage parcels, corner parcels, compounds, campuses and parcels without a conventional street frontage are explicitly modelled rather than forced into a false single-frontage assumption.

The parcel model must distinguish parcel identity from BP04 property identity. Define and test the relationship cardinality for properties spanning multiple parcels and parcels containing multiple separately managed property assets. Do not assume one-to-one identity without a documented rule.

### Stage C — property and built-asset population

Populate the BP04-01 identity types:
1. Property/site.
2. Building/structure.
3. Premises.
4. Unit/space.
5. Access point.

Use the full BP04-02 profile model for every created record. The population must be coherent from land parcel to site, building, premises, unit and access point. Every parent/child relationship must be valid and every applicable record must resolve to canonical parcel/address/road/junction/neighbourhood IDs.

Include both developed and non-building land. A park, harbour facility, road-support site, utility compound or vacant parcel must not be represented as a fictitious conventional building merely to achieve coverage. Use governed property/feature classifications and explicit not-present/not-applicable states.

The inventory must cover all 24 neighbourhoods. The generation plan must show, per neighbourhood, parcel count, property count, building count, premises count, unit count, access-point count, land-use distribution, and unresolved/unknown totals. Any area with no built assets must have an explicit, supported land-use explanation rather than disappearing from the report.

Do not hard-code arbitrary city-wide building/unit totals before parcel and land-use capacity modelling. Establish counts from the approved parcel fabric and a deterministic, documented generation manifest. All generated counts must reconcile exactly to parent/child relationships.

### Stage D — detailed physical dossiers

Every property, building, premises, unit and access point receives a substantive profile using BP04-02's typed fields and child relations.

Mandatory detail by applicable type includes:
- **Property:** land-use and site class, site form, parcel relationships, area and measurement basis, frontage/depth where supported, boundary reference, terrain/surface/drainage state, yard/court/parking/loading/open-space features, utility availability, perimeter/security form, site condition, hazards and lifecycle.
- **Building:** use/form/construction class, structural system/materials, foundation/frame/floors/walls/roof/envelope where modelled, floor schedule, footprint/gross/net area basis, height/storeys where supported, circulation, utilities, fire/life-safety provisions, accessibility, security systems as physical attributes, shared spaces, element-level condition, defects and maintenance history.
- **Premises:** functional type, floor/location, frontage/orientation, gross/net/usable area basis, room/zone composition, fit-out/finish, fixtures/equipment categories, service points, security boundary, fire/escape/accessibility relationships, physical suitability and maintenance history.
- **Unit:** controlled unit class and local locator, floor/position, area basis, room/compartment composition where relevant, fit-out, fixtures, equipment, utility/service points, accessibility, entry/security, fire/escape, physical capacity/suitability and condition history.
- **Access point:** access type, exact parent and geographic locator, approach/orientation, measured opening dimensions only where justified, allowed physical modes, directionality, physical controls, accessibility/threshold/ramp, applicable vehicle restrictions, loading/turning attributes, emergency-egress role, availability state, obstruction/condition and verification provenance.

Use structured child records, not a single unstructured notes field or oversized JSON blob. Measurements must identify units, basis, method, precision, source and confidence. Distinguish documented, observed, generated-design-estimate, inferred, unknown and not-assessed facts. Generated fictional estimates must never be presented as surveyed or verified measurements. Unknown, not assessed, not applicable, not present and measured zero remain distinct.

### Stage E — cross-domain reconciliation and operational location readiness

- Reconcile every parcel/property/building/premises/unit/access-point ID and parent link.
- Ensure every named entity is reserved through SW-UNS-001 before commit; preserve all existing canon names and reject exact/normalised/near-duplicate collisions according to the naming standard.
- Validate address resolution from full address to parcel, property, building, premises, unit and entrance where such detail exists.
- Validate reverse lookup from access point to road/junction/route and neighbourhood where supported.
- Validate that an entrance is physically connected to a plausible approach; do not connect an entrance to a road solely because it is nearby in a drawing.
- Test multiple entrances, multiple road frontages, shared entrances, restricted/service/emergency entrances, internal access and properties with no conventional entrance.
- Preserve unresolved and approximate locations as explicit statuses; never silently snap or invent.
- Produce per-district and per-neighbourhood coverage, land-use and data-quality reports.
- Confirm this physical inventory does not itself allocate residents, households, tenants, businesses, employees or police facilities. Those are separate domain decisions and packages.

## 4. Naming and identity rules

- All permanent identities are immutable, opaque and never reused.
- Every canonical named entity is reserved in SW-UNS-001; local unit/plot numbers are locators, not competing canonical names.
- Preserve adopted district, neighbourhood, road and landmark names exactly as currently approved.
- Do not use generic repetitive names such as "Building 1" as canonical entity names. Use unique generated names only where an entity is actually named; otherwise leave the canonical name absent and retain its stable ID and local locator.
- Name generation must be deterministic for a given manifest, reject collisions globally and record generator/version/source.
- Corrections create alias/history events; they do not overwrite identity or erase former names.

## 5. Population realism and distribution rules

The inventory should reflect the functional roles already defined for the eight districts and 24 neighbourhoods: civic/government, harbour/customs/maritime, education/institutional, commercial/market/exchange/entertainment, industrial/freight, historic waterfront, open-space/reservoir and mixed residential areas.

The distribution model must:
- be neighbourhood-first and parcel-capacity constrained;
- use compatible land-use/building/premises/unit combinations;
- account for mixed-use and multi-building compounds;
- distinguish residential suitability from actual residence/occupancy;
- distinguish business-capable premises from actual business assignment;
- avoid placing heavy industrial uses in incompatible residential/civic parcels;
- include civic, public, transport, port, utility and open-space assets as physical sites where canon requires them;
- record the reason and source/rule for each generated classification;
- expose counts and ratios rather than conceal imbalances.

No business operators, business premises assignments, staffing, resident household allocation, ownership, tenancy, leases or police-facility appointments are created by this package. The 10,000-business opening fixture remains a separate SW-DB-001 test cohort, not evidence of 10,000 geographically assigned operating businesses.

## 6. Data provenance and synthetic-world truth

This is a fictional world, so deterministic generated data is allowed. Its epistemic status must remain honest:
- `fictional_canon`: a user-approved world fact;
- `generated_design_value`: a deterministic fictional construction choice;
- `derived_geometry_value`: reproducibly calculated from approved fictional geometry;
- `unknown`: not known or not supplied;
- `not_assessed`: no assessment performed;
- `not_applicable`: field does not apply;
- `not_present`: feature was assessed and does not exist.

Every generated batch must record generator version, source commit, seed/manifest checksum, geography version, naming-generator version, generation time, deterministic parameters and row counts/checksums by entity type. Re-running the same manifest must be idempotent and yield the same canonical row manifest and content checksums. A changed manifest must create an explicit new batch/revision and must not silently overwrite prior facts.

## 7. Storage, performance and reproducibility requirements

Before any Neon operation, follow the repository's mandatory storage/write gate. BP04-03 implementation begins on disposable PostgreSQL only.

Measure separately:
1. schema-only migration growth;
2. parcel/address fixture growth;
3. property identity/profile growth;
4. building identity/profile growth;
5. premises identity/profile growth;
6. unit identity/profile growth;
7. access-point identity/profile growth;
8. shared naming/provenance/history growth;
9. total fixture growth and bytes per entity/child record class.

Also measure:
- deterministic generation time and rows/second;
- index sizes and relation sizes by domain;
- representative exact-address, parcel, property, building, premises/unit-tree and access-point-to-road queries;
- per-neighbourhood aggregation and reconciliation latency;
- same-manifest idempotency delta;
- backup/restore content checksums;
- rollback cleanliness and absence of orphan rows.

Do not hide shared registry/index overhead inside per-entity byte figures; report both direct and allocated/shared costs with a documented method. Do not invent performance numbers.

## 8. Required acceptance tests

1. All eight districts and 24 neighbourhoods reconcile to the approved geography version.
2. All 100 outstanding source-to-spatial-ID mappings are either resolved with provenance or remain explicit blockers; none are silently dropped.
3. Parcel polygons pass validity, containment, overlap/gap and deterministic neighbourhood-assignment checks.
4. Parcel split/merge/successor history is queryable and identity is never reused.
5. Address uniqueness, alias history and parcel/road/locality relationships pass.
6. Property-to-parcel cardinality rules pass for one-to-many and many-to-one cases where allowed.
7. All five BP04 identity types are populated with complete required profiles and valid parent/geography references.
8. Every neighbourhood has a reconciled physical coverage report, including legitimate no-building/open-space cases.
9. Land-use and asset combinations pass compatibility checks.
10. Every material profile assertion carries provenance, confidence/quality and effective/recorded chronology.
11. Generated estimates are labelled as generated; no survey-grade or verified claim is fabricated.
12. SW-UNS-001 rejects duplicate and near-duplicate names and concurrent reservation collisions.
13. Address-to-entrance and entrance-to-road relationships pass topology and access-mode tests.
14. Restricted, emergency, service, shared and multiple entrances are represented without false public access.
15. Unknown/not-assessed/not-applicable/not-present/zero states remain distinct.
16. Repeat generation with the same manifest is idempotent and checksum-identical.
17. A changed manifest preserves prior version/history and produces a traceable revision.
18. Full disposable backup/restore preserves row counts and content checksums.
19. All test fixtures roll back or remain confined to disposable databases.
20. No Neon production connection or write occurs.
21. Storage and query measurements are recorded by entity class and shared-cost category.
22. README, implementation sequence and evidence are updated on `main`.

## 9. Explicit exclusions

BP04-03 does not implement:
- property ownership, title, landlords, managers or beneficial ownership;
- tenancy, leases, licences, rents, household/resident allocation or occupancy;
- business legal entities, operators, business-site assignments, trading schedules, employees, stock, suppliers or revenue;
- police stations, police facility assignment, patrol deployment or staff allocation;
- simulation runtime/time advancement, dispatch policy or incident/case content;
- changes to the eight-district/24-neighbourhood canon;
- unapproved changes to SW-GEO-V1 or BP-02 operational geography;
- Neon production migrations, seed/import, bulk upload or activation.

These remain separate BP-02/BP-03/BP-04 and operational packages.

## 10. Delivery and approval record

Recommended sequence after approval:

1. Implement Stage A geography reconciliation and publish the exact blocker/coverage register.
2. Complete and validate the parcel/address candidate layer on disposable PostgreSQL.
3. Obtain the required BP-02 geography/version approval before designating spatial records canonical.
4. Generate the full deterministic physical inventory and BP04-02 profiles in disposable PostgreSQL.
5. Run all acceptance, storage, performance, idempotency and restore checks.
6. Publish evidence and update README/implementation sequence.
7. Only then prepare a separately measured production migration/seed proposal. No Neon production write is included here.

**Approval recorded 2026-11-24:** the user approved BP04-03 for GitHub `main` implementation and disposable PostgreSQL testing, including staged geography reconciliation and parcel/address candidate work. This approval does not authorise Neon production access or writes, operational geography approval, or production inventory seeding.

**Implementation log:** Stage A read-only geography readiness audit, tests and dedicated CI workflow committed to `main`. First validation run: [45480250963](https://github.com/Joshuaogri/saltwater/actions/runs/45480250963). Stage A structural readiness audit is verified: [run 45480493889](https://github.com/Joshuaogri/saltwater/actions/runs/45480493889), 28/28 checks passed. The [source-to-spatial reconciliation register](../../../data/geography/bp04-03-stage-a-source-spatial-reconciliation-v1.json) contains all 100 source identities; 0 are resolved and 100 remain explicitly blocked. See [Stage A run evidence](../test-evidence/BP04-03-stage-a-run-0001.md). Stage A mapping resolution remains incomplete. Stage B schema foundation is implemented in [proposal 0013](../../../db/proposals/0013_bp02_parcel_address_candidate.sql): BP-02-owned parcel/address profiles, version-linked geometry payload/checksum, structured locators and frontage types, parcel lineage, address aliases, kind guards and append-only controls. The dedicated disposable PostgreSQL 16 workflow [run 45481959712](https://github.com/Joshuaogri/saltwater/actions/runs/45481959712) passed Python contract tests and SQL acceptance, including duplicate locator, invalid road-kind, geometry checksum and append-only rejection. Schema growth was 294,912 bytes; proposal source was 10,668 bytes. See [Stage B schema run evidence](../test-evidence/BP04-03-stage-b-schema-run-0001.md). This verifies only the schema foundation: no city-wide parcel polygons, canonical address candidate population or operational spatial IDs have been generated. Next: deterministic parcel geometry and address candidate generation with topology/frontage validation. The 100 Stage A source mappings remain unresolved.

**Stage B candidate generation log (2026-11-24):** Deterministic candidate generator, five Python tests and dedicated GitHub Actions workflow committed on `main`. Run [45482818681](https://github.com/Joshuaogri/saltwater/actions/runs/45482818681) passed: 396 500m block-scale candidate polygons across all 24 neighbourhoods; 36 cells with mapped-water bounding-box conflicts excluded; 392 matching road-edge geometries; 4 frontage-unresolved candidates. Candidate artifact (compressed ZIP) size: 11,656 bytes. Manifest SHA-256: `6afc12c8e27717523bb581057da8c936481b1950faa5703f52bb5e7560e8cba4`. Evidence: [BP04-03 Stage B parcel candidate run 0001](../test-evidence/BP04-03-stage-b-parcel-candidates-run-0001.md). This is a planning-grade block framework, not final cadastral parcel geometry. No spatial IDs, addresses, DB writes, or Neon operations were performed; all 100 source mappings remain unresolved. Exact water clipping, road-reserve modelling, topology/coverage validation and disposable PostgreSQL ingestion/acceptance remain next.


**Stage B exact geometry and topology refinement (2026-11-24):** Generator v2 now computes polygon-to-cell intersection area against current single-ring water polygons using Sutherland–Hodgman clipping. Unsupported polygon holes and geometry types fail closed. The subsequent topology refinement verifies all 396 candidate interiors remain inside their source neighbourhoods, with zero pairwise candidate-interior overlaps; the 432-cell source grid reconciles to 396 candidates plus 36 water-excluded cells. Eight tests passed in [run 45483804394](https://github.com/Joshuaogri/saltwater/actions/runs/45483804394). Latest manifest SHA-256: `83ec53dc09f51483110e1e564b82919d2da63a0f5c5adcd92b42e04bf508f85f`; artifact size 12,033 bytes compressed: [candidate artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45483804394/artifacts/14962257890). This is generated-grid topology only, not cadastral topology. The 15m inset is provisional; residual area is not classified. Next: disposable PostgreSQL candidate ingestion with BP-02 identity/name registry integration, geometry checksums, storage and repeatability tests. No operational IDs or addresses were created; all 100 source mappings remain unresolved.


**Stage B disposable ingestion completed (2026-11-24):** Workflow [45484639045](https://github.com/Joshuaogri/saltwater/actions/runs/45484639045) passed on PostgreSQL 16. Imported 396 candidate identities, 396 versioned geometry payloads with SHA-256 checksums and 396 parcel profiles. No addresses were created. First import added 1,187,840 database bytes (739.125 ms); proposal 0013 schema-only growth was 294,912 bytes (10,668-byte SQL source). Repeat import inserted zero rows and measured 0-byte database growth. Evidence: [BP04-03 Stage B disposable ingestion run 0001](../test-evidence/BP04-03-stage-b-disposable-ingestion-run-0001.md). These are disposable candidates only. No operational geography approval, canonical address allocation, or Neon operation occurred.
