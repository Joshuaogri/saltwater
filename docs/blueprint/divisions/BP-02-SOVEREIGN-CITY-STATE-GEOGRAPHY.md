# BP-02 — Sovereign City-State and Geographical Architecture

**Project:** Saltwater  
**Blueprint:** BP-01–BP-44  
**Version:** 0.1  
**Status:** `DESIGNED_DRAFT` — awaiting user review/approval  
**Date:** 2026-11-22  
**Owner:** BP-02  
**Dependencies:** BP-01, BP-03, BP-04, BP-10–BP-12, BP-17, BP-20, BP-22, BP-35, BP-37, BP-38, BP-40, BP-43, BP-44  
**Authority:** User-owned canon; no exact city map, district count, coastline, river, terrain or road inventory is assumed by this draft.

---

## 1. Purpose

BP-02 defines Saltwater's sole sovereign territory and the canonical spatial reference system used by every division. It specifies how the city-state boundary, city boundary, administrative areas, neighbourhoods, land zones, parcels, roads, junctions, paths, natural features, landmarks, addresses, access points and off-map references are represented, identified, versioned, related and queried.

BP-02 supplies authoritative spatial identity and topology. Other divisions must reference its stable spatial IDs rather than creating competing geographic hierarchies.

BP-02 does not own:
- population/person identity, residence or movement history (BP-03);
- property ownership, buildings, premises, room layouts, keys, locks, occupancy or tenancy (BP-04);
- police facilities, patrol policy or deployment (BP-05–BP-10);
- incident/case/scene identity or investigative facts (BP-12,BP-15–BP-24);
- simulation event execution or clock (BP-35,BP-37);
- database implementation/persistence (BP-38,BP-39);
- map UI or player commands (BP-40).

These systems consume BP-02's geography and may own domain-specific links to it.

**Traceability:** S01.R01,R03; S02.R01–R03; S17.R01–R03; S45.R01–R03; C01–C02.

## 2. Binding geographic canon and non-assumptions

1. Saltwater is one sovereign city-state containing one city and one sovereign jurisdiction.
2. No second city, external territory, expansion region or additional playable jurisdiction may be created.
3. All playable land, water, roads, parcels and operational locations must resolve inside the single canonical Saltwater boundary.
4. External locations are references only. They may be stored as off-map context for origin, destination, trade, travel, supply, migration or case history, but cannot become playable districts, local population areas or a second simulation map.
5. Exact city dimensions, shape, coastline, islands, waterways, terrain, districts, neighbourhoods, road names/counts, parcel counts and map origin have not been established in the adopted canon. This specification does not invent them.
6. The city may contain varied land uses and physical geography, but each feature must be user-approved or introduced through an approved versioned geography decision.
7. A map illustration is not an authoritative boundary. Canonical geometry and stable IDs govern.
8. Spatial changes must preserve prior versions and references; no silent coordinate or boundary replacement.
9. BP-02's map and location system must support all required police and city workflows even when no graphical map is available.

**Traceability:** C01–C02; S01.R01–R03; S02.R01–R03.

## 3. Geographic hierarchy

The canonical logical hierarchy is:

`Saltwater city-state → Saltwater city → administrative area → neighbourhood/locality → zone/land-use area → parcel → BP-04 property/building/premises → BP-04 internal space/access point`

Road and natural-feature networks are related spatial systems, not forced into the parcel hierarchy.

### 3.1 Required entity classes

| Entity | Meaning | Owner |
|---|---|---|
| City-state boundary | Sole sovereign territorial boundary | BP-02 |
| City boundary | Sole playable city boundary; must reconcile with sovereign boundary | BP-02 |
| Administrative area | Canonical local administrative subdivision, if adopted | BP-02 |
| Neighbourhood/locality | Recognised local area and address context | BP-02 |
| Zone/land-use area | Planning/functional spatial classification | BP-02 |
| Parcel | Canonical land parcel or spatial lot | BP-02 |
| Address | Stable location reference and structured address components | BP-02 |
| Road/path | Named or unnamed movement corridor | BP-02 |
| Junction/node | Topological connection between route segments | BP-02 |
| Road/path segment | Directed or undirected routable edge with constraints | BP-02 |
| Crossing/bridge/tunnel | Special route connector with topology and access constraints | BP-02 |
| Natural feature | Terrain, waterbody, coast, slope or other approved geographic feature | BP-02 |
| Landmark | Named reference point or area | BP-02 |
| Off-map reference | External place/context with no local playable geometry | BP-02 |
| Property/building/premises | Physical asset and occupancy structure linked to geography | BP-04 |
| Entrance/access point | Physical access location linked to a building/premises | BP-04; spatial locator BP-02 |
| Interior room/space | Building internal geometry and access | BP-04 |

### 3.2 Cardinality and uniqueness
- Exactly one active canonical Saltwater city-state boundary.
- Exactly one active canonical playable city boundary.
- City boundary must be wholly contained by, or be the same geometry as, the city-state boundary according to the approved constitutional/geographic design. It cannot extend beyond sovereign territory.
- Administrative subdivisions must have valid parent relationships and effective dates.
- No duplicate active stable ID for the same geographic entity.
- Overlapping administrative/functional areas are permitted only where their area types and relationship rules explicitly allow overlap.
- A parcel must have one canonical parcel identity; subdivisions, amalgamations or boundary corrections create versioned successor/relationship records, not silent identity replacement.
- Every property/building/access point references canonical geography and cannot create a competing parcel or street identity.

## 4. Coordinate reference and geometry

### 4.1 Coordinate system
The initial detailed map must use a documented fictional local projected coordinate reference system suitable for a compact city. Units, axis orientation, origin, precision, extent, datum assumptions, geometry validity rules and version must be explicit.

No real-world latitude/longitude, country, projection or surveyed coordinate is assumed. If latitude/longitude-like values are used for fictional convenience, they must be clearly labelled fictional and must not imply real geography.

A coordinate reference record must define:
- stable CRS/version ID;
- units and axis order;
- origin and orientation;
- valid coordinate range/extent;
- precision and rounding rules;
- transformation rules between approved versions;
- geometry validity and topology rules;
- source and approval of the map baseline.

### 4.2 Geometry types
Support as required:
- point: junction, landmark, access locator;
- line/multiline: road, path, boundary segment, route;
- polygon/multipolygon: city, administrative area, neighbourhood, zone, parcel, natural area;
- network graph: junction/edge topology;
- structured textual geometry: fallback where map geometry is unavailable but a location must still be described.

Geometry must be valid, versioned and consistent with its entity type. No invalid ring, self-intersection, disconnected route or impossible topology may silently enter the authoritative map.

### 4.3 Precision
Precision must match the use:
- city/district orientation: coarse geometry may be sufficient;
- road routing: segment-level topology and lengths;
- parcel/address: exact canonical parcel/address link;
- access point: sufficient precision to distinguish entrances;
- scene/evidence: precise enough for reproducible scene references, with finer interior detail owned by BP-04.

Do not claim survey-grade accuracy where only fictional planning geometry exists. Store accuracy/confidence/source metadata when location precision is uncertain.

### 4.4 Boundary rules
- Boundary membership is determined by canonical geometry and explicit topological rules, not visual appearance.
- A point on a boundary must have a deterministic classification rule.
- A location outside the city-state is off-map; it cannot be silently snapped inside.
- Borderline/ambiguous locations retain uncertainty and require resolution or an explicitly approximate location status.
- No route may leave Saltwater and re-enter unless the route is explicitly marked as an off-map journey context; off-map segments are not locally routable city roads.

## 5. Stable identifiers and versioning

Every spatial entity receives a stable, opaque, non-semantic ID. Names, labels, postal forms, coordinates, parent area and geometry may change without changing identity where the underlying entity remains the same.

Minimum identifier families:
- `geo_id`: geographic entity;
- `area_id`: administrative/locality/zone;
- `parcel_id`: land parcel;
- `addr_id`: canonical address;
- `road_id`: named road/path;
- `node_id`: junction/network node;
- `seg_id`: routable segment;
- `feature_id`: natural feature/landmark;
- `offmap_id`: external reference;
- `geo_version_id`: approved geographic baseline/version.

Rules:
- IDs are unique, immutable and never reused.
- Human-readable codes are optional aliases, not primary identity.
- Name changes preserve prior names and effective dates.
- Merge/split/retirement creates explicit successor/predecessor relations.
- Geometry corrections create a new version with reason, source, approver and effective point.
- References in incidents, cases, evidence, reports and historical records continue to resolve to the location version valid at the event time.
- Deleted or retired locations remain resolvable in historical records and cannot be silently reassigned.

BP-38 defines physical schema and constraints; BP-44 governs approved geography version changes.

## 6. Administrative areas, localities and land use

BP-02 must support administrative divisions and neighbourhood/locality records without fixing their count or names before user-approved geography design.

Each area record should include:
- stable ID and optional short code;
- canonical and alternate names;
- area type and parent ID;
- boundary geometry and geometry version;
- effective start/end;
- status;
- land-use/functional tags where relevant;
- source, approval and provenance;
- textual description and navigation aliases.

Area relationships must support:
- contains/contained-by;
- adjacent-to;
- overlaps-with where permitted;
- successor/predecessor;
- administrative responsibility;
- address membership;
- route/network membership.

Land-use classification may include residential, commercial, industrial, civic, institutional, transport, port, utility, open space, mixed-use, protected/environmental and other approved categories. Categories are configurable through controlled versions; classification does not itself create a building, business or resident.

No area may be invented merely to satisfy an arbitrary count. The final city layout and number of districts/neighbourhoods are user-approved canon decisions.

## 7. Parcels, addresses and property interface

### 7.1 Parcel geography
BP-02 owns parcel identity and geographic geometry. BP-04 owns property assets, ownership, tenancy, buildings, premises, floor plans, units and occupancy.

Parcel records support:
- stable parcel ID;
- boundary geometry/version;
- address association(s);
- parent area references;
- parcel status;
- land-use references;
- subdivision/amalgamation history;
- effective dates and provenance.

### 7.2 Address model
An address is a stable spatial reference, not merely a display string. It should support:
- address ID;
- locality/neighbourhood and administrative area;
- street/road reference where applicable;
- building/plot number or approved locator;
- unit/suite identifier where BP-04 supplies it;
- postal/display form if the canon establishes one;
- entrance/access-point reference;
- validity dates;
- geocoding precision/status;
- aliases, former forms and search tokens.

BP-02 owns the canonical address locator and geographic relationship. BP-04 owns the actual premises/building/unit and physical access point. A building may have multiple entrances and an address may resolve to more than one unit only where the explicit address model permits it.

### 7.3 Location resolution
A location request may resolve to:
1. exact access point;
2. exact building/premises;
3. parcel/address;
4. road segment or junction;
5. neighbourhood/area;
6. approximate named location;
7. unknown/unresolved;
8. explicit off-map reference.

Resolution must preserve the requested precision and uncertainty. It must not invent a street number, access point, parcel or coordinates. Ambiguous results must be represented as ambiguous, not silently selected.

**Traceability:** S02.R01–R03; S06.R01–R03; S18.R01–R03.

## 8. Road, path and movement network

### 8.1 Network model
The movement network is a graph:
- nodes represent junctions, terminals, access connectors and other approved network points;
- edges represent road/path/rail/ferry or other canon-approved movement segments;
- connectors represent bridges, tunnels, crossings, ramps, gates and transitions;
- restrictions represent direction, access, mode, time, weight/height or closure constraints.

The graph must distinguish geometric intersection from actual traversable connection. Grade-separated roads, tunnels, bridges and private access must not create false junctions.

### 8.2 Segment attributes
A routable segment may contain:
- stable segment ID and road/path ID;
- start/end node IDs;
- geometry and measured length;
- directionality;
- permitted travel modes;
- road/path class;
- speed or baseline traversal model, if established;
- access restrictions and emergency exemptions;
- physical restrictions such as width/height/weight where relevant;
- surface/condition;
- effective dates;
- closure/maintenance state and source;
- provenance and confidence.

Unknown attributes remain unknown; no speed, length, restriction or access permission is invented.

### 8.3 Connectivity and topology
- Every routable edge must connect valid nodes.
- Every junction/edge must resolve to the same canonical geography version.
- Disconnected components are permitted only where physically justified and linked by a defined transfer mode or recorded isolation.
- One-way and restricted edges must be respected.
- Crossing connectors must link the correct endpoints and must not create impossible shortcuts.
- Private, controlled or restricted access cannot be used by a public route profile.
- Emergency routing may use only explicitly authorised emergency access.
- Temporary closures are effective-dated and do not erase the underlying road identity.

### 8.4 Routing
Routing must support shortest-distance and fastest-estimated routes where sufficient data exists. It must:
- use graph topology, edge lengths, permitted modes and directionality;
- apply access restrictions and closures;
- distinguish public, pedestrian, cycling, service, freight and emergency route profiles where adopted;
- return ordered route legs and total distance;
- return a duration/ETA only where a defensible traversal model exists;
- state when a route is unavailable or only approximate;
- preserve route snapshots used in dispatch/case timelines where another division requires them;
- never invent route metrics for disconnected or unknown paths.

Dynamic traffic, congestion, driving behaviour, incident closures and calibrated travel-time models are optional later refinements, not assumed live capabilities.

BP-02 owns base topology and route calculation contracts. BP-10/BP-11/BP-12 own operational use and dispatch decisions. BP-35 coordinates time-dependent route changes.

**Traceability:** S09.R01–R03; S17.R01–R03; S22.R01–R03.

## 9. Natural geography, environment and landmarks

BP-02 provides canonical geometry and identity for approved:
- terrain and elevation features;
- water bodies, waterways, coastlines and shorelines if present in the approved map;
- islands, slopes, cliffs, wetlands and other landforms if present;
- bridges, crossings and geographic barriers;
- public/open spaces and other spatial landmarks;
- named landmarks and orientation references.

BP-02 does not decide the city's actual natural geography. BP-19 owns weather/environmental conditions and hazard events; BP-02 supplies the spatial base on which those conditions are located.

Landmark records include stable ID, name, type, geometry, area/parcel relation, effective dates, aliases, description and provenance. A landmark is not automatically a building or business. If it is a physical premises, BP-04 supplies the linked property/building identity.

## 10. Off-map references and boundary enforcement

Off-map records exist only to represent context. They may identify a fictional external place, organisation, route origin/destination or source location without constructing a second playable map.

An off-map reference must include:
- stable off-map ID;
- display name and optional type;
- relation to Saltwater (origin, destination, supplier, jurisdiction, etc.);
- source/provenance and confidence;
- whether it is a broad reference or exact external location;
- explicit `playable=false` and `local_spatial_geometry=false` semantics;
- links to relevant Saltwater events/entities.

No off-map record may:
- receive local district/neighbourhood/parcel membership;
- create local residents or police staff;
- create a routable local road network;
- be used to bypass the 10,000-person limit;
- become a second city or jurisdiction through generated narrative.

A travel event to/from off-map context is represented as an event and reference, not as an extension of the playable map.

**Traceability:** S01.R03; S09.R03; C01–C02.

## 11. Spatial search and textual location descriptions

All core spatial functions must work without a graphical map:
- find by canonical ID, current/former name, address, alias or linked entity;
- describe a location relative to a recognised area, road, junction or landmark;
- list neighbouring/adjacent areas;
- identify valid access points;
- resolve a route and explain its ordered legs;
- query what lies within an area or radius where geometry supports it;
- distinguish exact, approximate, ambiguous and unknown locations;
- identify off-map context clearly.

Text descriptions must be generated from canonical records and not contradict coordinates, boundaries, road topology or access restrictions. BP-40 owns the presentation and commands.

## 12. Time, history and changing geography

Geographic entities may change through approved construction, road works, boundary adjustments, parcel subdivision, renaming, closure, access modification or map correction.

Each change must record:
- entity and version affected;
- previous and new values/geometry;
- effective in-game time;
- record creation time;
- reason and source;
- actor/authority and approval;
- affected dependent records;
- migration/alias/successor links;
- tests and evidence.

Historical events must resolve against the geographic version valid at the event time. A road closure does not erase the road. A renamed street retains historical names. A parcel split does not rewrite prior incident locations.

BP-37 supplies canonical in-game time. BP-38 supplies effective-dating and record constraints. BP-39 preserves and restores history.

## 13. Data ownership and interface contracts

| Consumer | BP-02 provides | Consumer owns |
|---|---|---|
| BP-03 Population | Address, locality, spatial membership, movement network | Person, residence history, population status and movement events |
| BP-04 Built world | Parcel, address, area, road and access locator | Property, building, premises, unit, entrance asset, occupancy and tenancy |
| BP-09 Resources | Facility/asset spatial reference | Police resource inventory, readiness and maintenance |
| BP-10 Patrol | Beats/areas, road network, route topology | Patrol policy, assignments, field activity and coverage |
| BP-11 Communications | Location resolution, route topology | Calls, CAD, radio, dispatch and communication events |
| BP-12 Incidents | Canonical location resolution | Incident identity, response and incident chronology |
| BP-17/18 Case persons | Location references | Person identity and case roles |
| BP-20 Surveillance | Device/site location and coverage geometry reference | Surveillance source, collection, retention and retrieval |
| BP-22 Crime scenes | Scene coordinates/access locator | Scene control, boundaries, search and release |
| BP-23 Evidence | Recovery-location reference | Exhibit identity, custody and evidential continuity |
| BP-35 Simulation | Spatial IDs, topology, route queries and geography versions | Runtime orchestration and event processing |
| BP-37 Time | Effective-date interface | Canonical clock and schedules |
| BP-40 Interface | Names, aliases, descriptions, map-ready geometry | Commands, textual/visual presentation |
| BP-43 Testing | Geography fixtures and invariants | Test execution and evidence |

No consumer may copy a geographic entity as a new canonical entity. Local caches or denormalised read models must retain the authoritative ID and version.

## 14. Failure, ambiguity and exception handling

The system must explicitly handle:
- unknown address or location;
- ambiguous names/aliases;
- duplicate candidate matches;
- missing geometry;
- invalid or self-intersecting geometry;
- location outside Saltwater;
- conflicting area membership;
- stale geography version;
- retired or merged parcel;
- disconnected route graph;
- blocked or restricted road;
- inaccessible entrance;
- route mode not supported;
- missing speed/length/travel-time inputs;
- temporary closure with conflicting effective dates;
- map data unavailable while text location remains known;
- spatial source with low confidence;
- attempted off-map expansion.

Failures must not produce fabricated coordinates, route distances, travel times, access permissions or local addresses. Preserve the original query and return a truthful status with the highest valid precision.

## 15. Security and permissions

- Read access to general public geography may be broad within the game world.
- Restricted facilities, sensitive infrastructure, private premises, protected locations and operationally sensitive map layers require BP-42 permissions.
- A public map view must not reveal restricted access points, hidden facilities or confidential surveillance locations.
- Police-only route access must be distinguished from public route access.
- Spatial permissions do not alter the underlying location identity.
- Every restricted access, disclosure, correction or export must be attributable and auditable.
- BP-42 owns the permission model; BP-02 supplies sensitivity classifications and location-level restrictions.

## 16. Acceptance criteria and test suite

### A. Canon and boundary
- **AC-A01:** Exactly one Saltwater city-state and one playable city boundary exist.
- **AC-A02:** The playable city is contained within the sovereign boundary.
- **AC-A03:** No second playable city, external territory or expansion map can be created through ordinary configuration or generated content.
- **AC-A04:** Every local operational location resolves inside Saltwater or is explicitly off-map.
- **AC-A05:** Off-map references cannot acquire local playable geometry, residents, districts or routable local streets.

### B. Identity and hierarchy
- **AC-B01:** All spatial entities have stable unique IDs.
- **AC-B02:** Duplicate active canonical IDs and contradictory same-entity records are rejected.
- **AC-B03:** Area parent/child relationships are valid and versioned.
- **AC-B04:** Parcel split/merge/retirement preserves predecessor/successor history.
- **AC-B05:** Every BP-04 property/building/access point links to valid geographic references.

### C. Geometry and location resolution
- **AC-C01:** Coordinate reference metadata defines units, axes, origin, precision and version.
- **AC-C02:** Invalid geometry is rejected with no partial authoritative update.
- **AC-C03:** Boundary points resolve through deterministic rules.
- **AC-C04:** Unknown/ambiguous locations are not silently geocoded to fabricated points.
- **AC-C05:** Historical events continue resolving to the geographic version valid at their time.
- **AC-C06:** Exact, approximate, ambiguous, unknown and off-map precision states are distinguishable.

### D. Roads and routing
- **AC-D01:** Every routable segment connects valid nodes.
- **AC-D02:** Grade-separated crossings do not create false at-grade connections.
- **AC-D03:** One-way, mode, access and closure restrictions are respected.
- **AC-D04:** Public routes cannot use restricted/private segments without explicit permission.
- **AC-D05:** Emergency route profiles use only configured emergency access.
- **AC-D06:** Route legs, total distance and duration reconcile where metrics are available.
- **AC-D07:** No ETA or route is invented where required inputs/topology are missing.
- **AC-D08:** A temporary closure affects only its valid segment/time window and does not erase road identity.
- **AC-D09:** Disconnected graph components are reported as unreachable unless a valid transfer connector exists.

### E. Integration, time and history
- **AC-E01:** Incidents, cases, evidence, dispatch, people and properties share canonical spatial IDs.
- **AC-E02:** Consumers cannot create duplicate authoritative location records.
- **AC-E03:** Geography changes have actor, reason, effective time, version and impact links.
- **AC-E04:** Historical route/location snapshots remain available where operational records depend on them.
- **AC-E05:** Paused/absent simulation time does not activate temporary geography changes or closures.

### F. Interface, security and quality
- **AC-F01:** All essential location lookup and route explanation works through text.
- **AC-F02:** Optional maps are generated from canonical geometry and are non-authoritative views.
- **AC-F03:** Restricted location layers are not exposed to unauthorised roles.
- **AC-F04:** Search handles aliases, former names and duplicate candidates without arbitrary selection.
- **AC-F05:** Geography tests do not create or advance population, police, case or simulation records.
- **AC-F06:** All tests are traceable to source IDs and retain reproducible evidence.

Required test classes: geometry validity, boundary, graph topology, routing, access control, temporal versioning, alias resolution, off-map containment, concurrency, migration/rollback, high-volume spatial lookup and regression.

## 17. Source traceability

| Source IDs | BP-02 obligation |
|---|---|
| C01–C02 | Single city-state and off-map-only external references |
| S01.R01–R03; S01.T01 | Jurisdiction and no expansion |
| S02.R01–R03; S02.T01–T02 | Canonical geography, spatial IDs and textual/map support |
| S06.R01,R03; S06.T01 | Parcel/address/access geography and effective location |
| S09.R01–R03; S09.T01 | Trade/logistics spatial network and off-map dependency |
| S17.R01–R03; S17.T01 | Roads, routes, movement and emergency access |
| S18.R01–R03; S18.T01 | Building/entrance spatial reference |
| S19.R01–R03; S19.T01 | Natural geography and spatially valid environment |
| S45.R01–R03; S45.T01 | Map/visual source geometry and traceability |
| X01–X04, X08 | Identity, source of truth, effective time, reconciliation and text-first map views |

The complete source-to-target mapping is maintained in `SALTWATER-52-TO-44-CROSSWALK.md`.

## 18. Open canon decisions

The following are required before BP-02 can be considered fully design-complete:
1. Exact city-state/city boundary geometry and whether it is contiguous or includes separated land areas.
2. Coordinate origin, axes, extent, units and precision.
3. City districts, neighbourhoods/localities and their names/counts.
4. Natural geography: coastline, waterways, terrain, elevation and other defining features, if any.
5. Road/path network, transport modes, junctions, crossings and access restrictions.
6. Addressing convention, street naming and parcel identifier convention.
7. Land-use categories and planning/administrative area model.
8. Initial landmark and major facility register.
9. Whether any off-map travel is represented as abstract reference only or with limited route context.

No values are silently invented here. The data structures, invariants, ownership boundaries, interfaces, failure handling and test contracts are specified; final map facts require explicit canon decisions.

## 19. Completion statement

**Design status:** `DESIGNED_DRAFT`; complete architecture and domain contract drafted, with material city-map canon decisions outstanding.  
**Implementation status:** `NOT_STARTED` unless separately evidenced.  
**Test status:** `NOT_STARTED`.  
**Verification status:** `NOT_STARTED`.

No Neon schema, migration, seed, import, upload or database write is performed or authorised by this document.
