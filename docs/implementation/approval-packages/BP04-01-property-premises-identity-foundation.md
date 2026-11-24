# BP04-01 — Property, Building, Premises, Unit and Access-Point Identity Foundation

**Status:** APPROVED — implementation and disposable verification in progress (2026-11-24)  
**Date:** 2026-11-24  
**Repository target:** `main` only  
**Database test target:** disposable PostgreSQL 16 only  
**Production Neon authority:** NONE

## 1. Purpose

Implement the first bounded BP-04 physical built-world identity layer. It establishes canonical, durable identities and parent relationships for property assets, buildings, premises, units and physical access points. It reuses BP-02 geography identities and SW-UNS naming enforcement rather than creating competing spatial or naming systems.

This package follows the verified SW-DB-001 business identity/provisioning foundation. It does not implement the entire BP-04 division or authorise a real-world baseline seed.

## 2. Existing foundations

- `sw_geo.entity` already defines typed geography entities, including parcel kind 6 and address kind 11; `sw_geo.version` owns their names and versions.
- `sw_names.name_reservation` and `sw_names.reserve_name()` provide the global naming namespace, currently extended through BUSINESS by proposal 0010.
- `sw_business.business` and its immutable history are already provided by proposal 0010. This package must not duplicate or redesign them.
- SW-DB-001's 9,500-person/10,000-business disposable fixture and its passing evidence remain unchanged.
- The SW-GEO-V1 map is not approved for operational seeding. No new parcel/address/road records are to be fabricated here.

## 3. Bounded deliverables

### 3.1 Canonical physical entities

Add a disposable candidate proposal, `0011_bp04_property_premises_foundation.sql`, defining:

1. **Property asset** — BP-04 identity for a land-linked or explicitly unresolved property record.
2. **Building/structure** — a constructed structure associated with one or more property assets through explicit links.
3. **Premises** — a separately identifiable operational place within a building or property.
4. **Unit/space** — an occupiable subdivision of premises, such as a flat, office, shop, room or warehouse bay.
5. **Access point** — a physical entrance, exit, gate, loading bay or controlled passage associated with a building, premises or unit.

Each entity receives an immutable generated primary key, a stable unique entity code, a typed lifecycle state, provenance and creation metadata. Names and descriptive attributes are not primary keys. No identifier is reused.

### 3.2 Geography references

- Property records may reference a BP-02 parcel entity (kind 6) and/or address entity (kind 11).
- Each property must have either a valid geography link or an explicit `UNRESOLVED` link state; null references must never be interpreted as a valid location.
- Database constraints/triggers must verify the referenced geography kind.
- Building/premises/unit/access-point relationships must use BP-04 foreign keys, not copied street names or invented parcel identifiers.
- No geometry is authored by BP-04. BP-02 remains the sole spatial authority.

### 3.3 Explicit relationship model

Support:
- property-to-parcel/address references;
- property-to-building relationships;
- building-to-premises relationships;
- premises-to-unit relationships;
- access-point-to-building/premises/unit relationships;
- effective-dated association history where a physical entity changes parent or location.

Cardinality must permit multi-tenant buildings and multiple buildings on one property without conflating the identities. Relationship constraints must prevent cycles, self-parenting and invalid cross-parent links.

### 3.4 Universal naming integration

Extend SW-UNS through typed BP-04 entity kinds for named property, building, premises, unit and access-point records. All canonical names and aliases must be reserved transactionally through the existing registry. Duplicate names, including names colliding with geography, people or businesses, must fail closed. The approved exact two-root `Saltwater` exception remains geography-only and cannot be reused by BP-04.

Unnamed access points may use stable codes; generated placeholder names must not be inserted into the global name registry.

### 3.5 History and integrity

- Preserve lifecycle and parent/location changes as append-only, source-attributed events.
- Do not permit hard deletion or silent identity reassignment.
- Enforce atomic writes across entity, relationship, name reservation and history records.
- Provide deterministic reconciliation queries for missing geography links, invalid parent chains, duplicate identity codes, naming gaps and inconsistent lifecycle states.

## 4. Required tests

Use disposable PostgreSQL 16 only:

- valid property with parcel/address references and explicit unresolved property;
- rejection of wrong-kind parcel/address references;
- valid building/premises/unit/access-point parent chains;
- multi-building, multi-premises and multi-tenant relationship cases;
- rejection of orphan, cyclic, self-parent and invalid parent links;
- immutable IDs and append-only history;
- universal naming collisions across geography/person/business/BP-04 types;
- transaction rollback when name reservation or history insertion fails;
- idempotent fixture application and exact row-manifest comparison;
- storage measurements by relation, heap, index and auxiliary bytes;
- backup/restore and full existing Python/PostgreSQL regression.

Evidence must include the tested commit, workflow IDs, source byte counts, database growth, relation storage, test results and limitations.

## 5. Explicit exclusions

- No ownership interests, landlords, management appointments, leases, licences, tenancy, subletting or occupancy decisions; those belong in a later bounded BP-04 package.
- No changes to proposal 0010's business identity model.
- No business establishments, organisation registry, facilities, schedules, staff, stock, suppliers or service-provider operations.
- No parcel/address/road geometry creation, operational map import or geography canon approval.
- No property/business counts, district distributions, sector distributions or invented city-wide baseline.
- No people, population changes, police employment, police premises assignments or operational police data.
- No public interface/API, production activation or live game time advancement.
- No Neon production connection, migration, schema change, seed, import, bulk write, upload or configuration change.

## 6. Acceptance criteria

1. Every physical entity has one immutable stable identity and correct BP-04 owner.
2. Parent/child and spatial references are valid and type-checked.
3. Explicit unresolved location state is distinguishable from valid parcel/address assignment.
4. All named physical entities participate in SW-UNS; no naming bypass or exception leakage exists.
5. History is append-only and failed multi-record operations leave no partial state.
6. Disposable PostgreSQL 16 and full regression workflows pass.
7. Storage/performance results and reproducible evidence are committed to the repository.
8. No Neon production operation occurs.

## 7. Approval record

The user explicitly approved **BP04-01 — Property, Building, Premises, Unit and Access-Point Identity Foundation** for:
- implementation directly on GitHub `main`;
- disposable PostgreSQL 16 schema and acceptance testing;
- SW-UNS adapter integration;
- reproducible tests, storage/performance measurements and documentation.

This approval covers only BP04-01. It would not approve the entire BP-04 design, the open BP-04 distribution decisions, SW-GEO-V1 operational seeding, or any Neon production operation.

**Neon production write authority remains NONE.**
