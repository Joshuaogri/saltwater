# BP04-02 — Deep Physical Asset and Space Profiles

**Status:** PROPOSED — awaiting explicit approval  
**Target:** GitHub `main` only; disposable PostgreSQL 16 implementation and acceptance  
**Candidate migration:** `0012_bp04_physical_asset_detail_profiles.sql`  
**Depends on:** BP04-01 identity foundation; BP-02 canonical parcel/address/road/access geography; SW-UNS-001  
**Production authority:** NONE. No Neon production connection, migration, seed, import, upload or configuration change is included.

## 1. Purpose

BP04-01 established the identity layer only. BP04-02 adds the detailed descriptive and operational-physical record layer for every:

1. Property.
2. Building or structure.
3. Premises.
4. Unit or space.
5. Access point.

The user requires extensive record depth. The implementation must not reduce these entities to a name, ID and a few generic fields. Each entity must have a meaningful, typed profile, a controlled vocabulary where appropriate, measurable physical attributes, structured feature records, provenance, lifecycle and assessment history, and explicit links to its parent and geographic context.

This package establishes the reusable data model and acceptance contract. It does **not** invent or seed Saltwater's actual city-wide inventory. Actual property/building/premises/unit/access-point population is a later, separately planned data-production step after geography coverage and the detailed model are accepted.

## 2. Universal record-depth rules

Apply these rules to all five entity types:

- **Identity is not description:** preserve BP04-01 immutable IDs and names; attach extensible profiles without rewriting identity.
- **Typed facts:** use enums/reference tables, numeric measures with explicit units, dates/ticks, booleans and structured references rather than untyped narrative blobs.
- **Unknown is not none:** represent `unknown`, `not_assessed`, `not_applicable`, `not_present` and known values distinctly. Never silently convert missing data to zero, false or none.
- **Provenance per assertion:** retain source reference, actor/source authority, recorded time, effective time, confidence/quality and reason for material facts.
- **History, not overwriting:** material profile changes, condition assessments, feature additions/removals, service states and access restrictions must be append-preserving/effective-dated.
- **Measurements:** store value, unit, measurement basis/method, precision where available, and source. Do not mix gross/net area or internal/external dimensions.
- **No fabricated precision:** estimated, observed, documented and inferred values must be distinguishable; unresolved values remain unresolved.
- **No duplicate facts:** normalise reusable classifications, materials, feature types, utility types and condition vocabularies; use references.
- **Naming:** all named entities remain under SW-UNS-001. Do not invent placeholder names for unnamed entities.
- **Temporal semantics:** use simulation ticks/effective ranges for in-world state; retain recorded timestamps for when the system learned the fact. A paused world does not advance.
- **No hidden dependencies:** profile rows must point to canonical BP04-01 identities and BP-02 spatial IDs, not copied free-text place names.
- **Compact but lossless:** use normalised tables and compact controlled codes; do not sacrifice detail, provenance or recoverability to save bytes.

## 3. Required property profile

Each property must support, where known or applicable:

### 3.1 Classification and use
- Property class/type (for example residential, mixed-use, commercial, industrial, civic, institutional, transport, utility, open-space or special-purpose).
- Primary and secondary land/building-use classifications, with effective dates.
- Development form and site pattern (standalone, attached, compound, campus, block, estate or other controlled type).
- Functional status (developed, partially developed, vacant, cleared, under construction, derelict, protected or other governed state).
- Site role and operational significance without conflating it with ownership or business identity.

### 3.2 Site and physical characteristics
- Site area and measurement basis; frontage and depth where known.
- Boundary/shape reference to BP-02 geometry; boundary certainty and source.
- Slope/terrain, surface treatment, drainage/flood exposure and ground condition where assessed.
- Open/covered areas, yards, courts, parking/loading/service areas and other site components as structured features.
- Utility/service availability at property level, distinct from a live service connection.
- Environmental/noise/industrial constraints only where supported by a defined source and classification.

### 3.3 Property-level service and condition
- Overall site condition, inspection/assessment state, date and assessor.
- Site security/perimeter characteristics and boundary-access arrangement.
- Shared facilities and external infrastructure.
- Development/works state and dated changes.
- Property-level hazard/constraint register with severity, confidence, mitigation/status and source.

## 4. Required building/structure profile

Each building/structure must support:

### 4.1 Form and construction
- Building use/function, building form and structure class.
- Construction system and primary/secondary structural materials.
- Foundation, frame, floor, wall, roof and external-envelope characteristics where known.
- Roof form/covering, façade/cladding and glazing characteristics.
- Construction/start/completion/major-refurbishment years or dates with source and precision.
- Heritage/protection/designation status only through a controlled, source-backed reference.

### 4.2 Dimensions and capacity
- Footprint area, gross floor area, net usable floor area and measurement basis separately.
- Storey count above/below ground; floor-level schedule with explicit level identifiers.
- Building height and height datum where known.
- Structural/design occupancy capacity and current authorised use capacity as distinct measures.
- Basement, mezzanine, roof, plant and service levels.
- Vertical circulation: stairs, lifts, ramps and service lifts, each typed and described.

### 4.3 Building systems and safety
- Electrical, water, wastewater, gas/fuel, communications, HVAC and backup-power systems as typed system records.
- Fire detection, alarm, suppression, compartmentation, escape and emergency lighting provisions.
- Security systems, controlled zones, CCTV presence as a system attribute (not surveillance content), alarms and access-control types.
- Accessibility provisions, barriers and accessible circulation.
- Building condition by element (structure, roof, façade, internal fabric, services and safety systems), not just one overall rating.
- Inspection/maintenance/defect records with severity, location, action, responsible source and status.

### 4.4 Building operation and shared facilities
- Operating/closure/construction/maintenance state.
- Shared lobbies, corridors, stairwells, toilets, plant rooms, refuse rooms, loading areas, parking and common facilities.
- Environmental performance/energy attributes only where measurable and sourced.
- Fire/service access and emergency assembly features.

## 5. Required premises profile

Each premises record must support:
- Premises function/use and occupancy suitability classification, without recording actual occupants or tenancy rights in this package.
- Suite/shop/office/department/industrial bay/civic room/warehouse/plant space or other controlled premises type.
- Floor/level, internal location reference, frontage/orientation and circulation relationship.
- Gross/net/usable area with measurement basis.
- Internal layout/room or zone composition as structured child records where justified.
- Fit-out/finish standard, internal condition, fixtures and installed equipment categories.
- Dedicated/shared services, utility availability and service points.
- Security boundary, controlled access, fire compartment/escape relationship and accessibility.
- Opening/operating capability as a physical capability only; business schedules and actual opening hours are out of scope.
- Inspection, defect, repair and refurbishment history.

## 6. Required unit/space profile

Each unit must support:
- Unit class (dwelling, apartment, office, shop, kiosk, stall, room, storage, workshop, parking bay, berth, plant space or governed extension).
- Unit number/code/label as a local locator, separate from SW-UNS canonical entity name.
- Floor/level and position within premises.
- Internal, gross and usable area where relevant, with explicit basis.
- Room/compartment count and typed layout attributes where relevant.
- Fit-out, fixtures, installed equipment categories and condition.
- Utility/service points and meter references where present.
- Accessibility, entry arrangement, security boundary and fire/escape relationship.
- Physical capacity/suitability limits as distinct from actual occupancy.
- Inspection/maintenance/defect history and lifecycle state.

## 7. Required access-point profile

Each access point must support:
- Access-point type: pedestrian entrance/exit, vehicle entrance/exit, combined gate, loading bay, service entrance, emergency exit, controlled passage, lobby threshold, roof/plant access or other governed type.
- Parent entity and exact physical location reference; where appropriate link to BP-02 road, junction, route or transport-node IDs.
- Approach side/orientation and position/geometry reference; no free-text invented coordinates.
- Clear opening width/height and dimensional units where measured.
- Access mode: pedestrian, cycle, motorcycle, light vehicle, heavy vehicle, service, emergency or restricted combination.
- Directionality and permitted movement.
- Physical control: open, gated, locked, staffed, intercom, card/key, turnstile, barrier or other typed mechanism.
- Accessibility and step/ramp/threshold characteristics.
- Vehicle height/weight/width restrictions where applicable.
- Loading/unloading capability, dock/turning/queuing attributes where applicable.
- Emergency egress role, fire-door/escape relationship and obstruction state.
- Operating availability/restriction windows as physical access controls; business opening hours remain out of scope.
- Security/condition/inspection state, last known verification and provenance.
- Explicit distinction between access point existence, current availability and permission to use it.

## 8. Shared structured child records

The implementation should use reusable, typed child relations where they add real value, including:

- Physical measurements and measurement history.
- Building floors/levels and level references.
- Building components/material assemblies.
- Premises rooms/zones where needed.
- Utility/service systems and service-point references.
- Physical features and facilities.
- Condition assessments and element-level ratings.
- Defects, hazards and remedial actions.
- Access restrictions, physical controls and accessibility features.
- Inspection/maintenance events.
- Evidence/source assertions and confidence.
- Effective-dated entity-to-entity and entity-to-geography relationships.

Do not create one giant JSON column or repeat the same detail in each parent record. Use typed relations with concise enumerated codes and source-linked history.

## 9. Explicit exclusions

BP04-02 does not implement:
- Ownership, title, landlords, property managers, leases, licences, rent, tenancy, subletting or agreements.
- Actual occupancy, residents, household allocation, business operators, staff or employment.
- Business establishment/site assignment, trading schedules, stock, suppliers or revenue.
- Police facilities, police station assignments or operational deployments.
- New geometry, map construction, road-network edits or geography canon approval.
- City-wide property counts, neighbourhood distribution or fabricated real inventory.
- Neon production changes or bulk seed/import.

Those matters require their own BP04/BP-02/BP-03 bounded packages and approvals.

## 10. Candidate implementation and acceptance

Candidate migration: `0012_bp04_physical_asset_detail_profiles.sql`. It must be schema-only and tested on disposable PostgreSQL 16.

Acceptance must demonstrate:
1. Every one of the five BP04-01 identity types can have a complete typed profile.
2. Distinct entity-specific fields and child records are available; no generic profile that loses domain detail.
3. Unknown, not assessed, not applicable, not present and measured zero remain distinguishable.
4. Area, length, height, capacity, floor level and utility/service values enforce units and measurement basis.
5. Every material fact/assessment/feature change carries provenance and effective/recorded chronology.
6. Historical assertions remain queryable after corrections and status changes.
7. Referential integrity prevents orphan profiles, levels, components, rooms, services and access relationships.
8. SW-UNS-001 remains the only naming registry; global collisions are rejected.
9. Repeated application/fixture loads are idempotent where specified.
10. Backup/restore preserves profile and history content checksums.
11. Representative queries support property dossier, building dossier, premises/unit tree, access-point register, condition/defect summary and spatially linked asset search.
12. Storage measurements report migration-only growth and synthetic profile fixture growth separately, with bytes per each of the five entity types and child-record class.
13. No synthetic fixture row survives rollback and no production database is contacted.

## 11. Delivery sequence

- First complete BP04-01 acceptance and publish its evidence.
- Then, after explicit BP04-02 approval, implement proposal 0012 on GitHub `main`, run disposable PostgreSQL 16 acceptance and regression, record exact storage/performance figures, and update README/implementation sequence.
- Only after the model is verified should a separate package design the real Saltwater property inventory and its geography-linked population workflow.

**Decision requested:** approve BP04-02 for GitHub `main` implementation and disposable PostgreSQL 16 testing only. Neon production remains untouched.
