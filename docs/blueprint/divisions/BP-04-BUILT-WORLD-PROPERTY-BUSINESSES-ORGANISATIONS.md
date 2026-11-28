# BP-04 — Built World, Property, Businesses and Organisations

**Project:** Saltwater  
**Blueprint:** BP-01–BP-44  
**Version:** 0.1  
**Status:** `DESIGNED` — design decisions resolved; implementation and acceptance underway  
**Date:** 2026-11-22  
**Owner:** BP-04  
**Dependencies:** BP-01–BP-03, BP-06–BP-12, BP-14–BP-17, BP-20, BP-22–BP-24, BP-30–BP-42, BP-44  
**Authority:** Canonical registry for properties, buildings, premises, businesses, organisations, facilities, infrastructure operators and non-police institutional entities. BP-02 remains the authority for geography; BP-03 remains the authority for person identity.

---

## 1. Purpose and operating principle

BP-04 defines the inhabited and operated built world of Saltwater: land-linked property records, buildings, premises, units, occupancy, ownership, tenancy, business and organisation identities, institutional facilities, essential-service operators, commercial activity, physical assets, access points and their time-valid relationships.

The world must contain at least **10,000 distinct businesses**. This is a minimum registry count, not a requirement to simulate every business at police-investigation depth. Businesses and organisations must nevertheless be coherent enough to support employment, opening hours, premises, ownership, transactions, supply dependencies, public activity, police enquiries, incident generation and case continuity.

The police department receives the deepest simulation. BP-04 supplies a complete, stable, operationally useful built-world layer without turning every business, landlord, utility, school, clinic, shop or public office into a second full-depth simulation.

The central rule is **one canonical identity per real in-game entity, with separately owned facts and explicit links**:
- BP-02 owns geography, parcel identity, address topology, roads and spatial geometry.
- BP-03 owns person identity, life status and the 10,000-person population ledger.
- BP-04 owns property/building/premises/business/organisation/facility identity and the built-world relationships defined here.
- BP-33 owns employment contracts, staff attendance, leave and general HR.
- BP-34 owns finance, accounting, rent/payment transactions, procurement and financial balances.
- BP-35 owns causal event execution and world-state processing.
- BP-37 owns the canonical clock and schedule execution rules.
- BP-38/BP-39 own physical data architecture and persistence/recovery.
- BP-42 owns permissions and sensitive information boundaries.

No division may create a competing authoritative copy of an entity owned by another division.

**Traceability:** S06.R01–R03; S07.R01–R04; S08.R01–R03; S09.R01–R03; S11.R02; S13.R01; S14.R01; S15.R01–R02; S16.R01–R03; S18.R01–R03; S20.R01–R03; S21.R01–R03; S22.R01–R02.

## 2. Scope and exclusions

### 2.1 Included
- Property parcels as linked spatial references, property assets, buildings, structures and premises.
- Ownership interests, management, leases, licences, tenancy, subletting, occupancy and time-valid use rights.
- Building and premises structure to the detail required for access, incidents, investigations, safety, occupancy and asset continuity.
- Business identity, legal/trading names, sector, status, locations, ownership/control relationships and operational profile.
- Organisations and institutions: public bodies, emergency-service agencies, education/health/social-service providers, utilities, cultural/community bodies, transport operators, media, suppliers and other entities required by canon.
- Facilities, physical assets, entrances, exits, rooms/units, keys/locks and access-control references.
- Opening hours, operational schedules, capacity and service availability at proportionate depth.
- Staff and role references, linked to canonical persons and employment records.
- Goods, stock, deliveries, suppliers and essential-service dependencies at the level required to support police and city continuity.
- Business/organisation events: opening, closure, relocation, ownership change, service interruption, insolvency, damage, renovation and reopening.
- Textual lookup, reports and cross-system interfaces.

### 2.2 Excluded or separately owned
- Parcel geometry, road graph, neighbourhood and canonical address topology: BP-02.
- Person identity, population counting, biographies and person life cycle: BP-03.
- Police organisational structure, police premises as police assets, police staffing and operational resources: BP-05–BP-09. BP-04 may hold the physical property link.
- General employee contracts, payroll, attendance, leave and HR: BP-33.
- Accounting ledger, bank/payment transactions, rent postings, tax calculations, procurement accounting and financial balances: BP-34.
- Full simulation of every commercial process, customer, sale or supply-chain transaction where it has no police/world consequence.
- Full healthcare, education, social-care, utility, transport or government simulations. BP-04 represents their entities and essential operational facts; domain-specific divisions own their specialist rules.
- Event processing and time advancement: BP-35/BP-37.
- Database implementation: BP-38/BP-39.
- User interface: BP-40.
- Permission enforcement: BP-42.

## 3. Entity model and ownership

### 3.1 Required entity classes

| Entity | Meaning | Authoritative owner |
|---|---|---|
| Property asset | Land-linked property interest or managed property record | BP-04 |
| Building/structure | Constructed physical structure | BP-04 |
| Premises | Operationally distinct physical place within a building or site | BP-04 |
| Unit/space | Suite, flat, shop, office, room, warehouse bay or other occupiable subdivision | BP-04 |
| Access point | Door, gate, loading bay, entrance, exit or controlled passage | BP-04; locator references BP-02 |
| Physical asset | Installed or movable asset with operational relevance | BP-04 |
| Ownership interest | Legal/economic ownership relationship and effective interval | BP-04; financial values BP-34 |
| Management appointment | Entity responsible for property management | BP-04 |
| Lease/licence/occupancy agreement | Contractual or recorded right to occupy/use property | BP-04; financial transactions BP-34 |
| Business | Commercial undertaking with a distinct identity | BP-04 |
| Organisation | Distinct public, private, charitable, civic or institutional body | BP-04 |
| Establishment/site | Specific operating location of a business/organisation | BP-04 |
| Facility | Site or premises providing a defined service | BP-04 |
| Operator/provider | Entity responsible for operating a service or asset | BP-04 |
| Supplier/customer link | Commercial or operational relationship reference | BP-04 |
| Stock/asset state | Operational stock or asset snapshot where needed | BP-04; financial valuation BP-34 |
| Opening-hours schedule | Business/facility hours and exceptions | BP-04; clock BP-37 |
| Staff-role link | Person assigned to an entity/establishment role | BP-04 reference; employment BP-33 |
| Off-map supplier/entity | External entity reference without playable local premises | BP-04 + BP-02 off-map reference |

### 3.2 Entity separation
A property owner, landlord, property manager, tenant, business operator, employer, brand, franchise, parent company and premises occupant are not automatically the same entity. Each receives its own identity where it is a distinct in-game entity.

A company may operate several establishments; an establishment may occupy several premises; several businesses may occupy one building; one business may occupy multiple units; one property owner may own many properties; a property may have multiple ownership interests. These relationships must be explicit and time-valid.

A brand or trading name is not automatically a separate legal entity. Store it as an alias/brand relationship unless the canon defines a distinct legal operator.

### 3.3 Stable identifiers
Use immutable, opaque identifiers:
- `property_id`
- `building_id`
- `premises_id`
- `unit_id`
- `access_point_id`
- `asset_id`
- `business_id`
- `organisation_id`
- `establishment_id`
- `facility_id`
- `agreement_id`
- `ownership_interest_id`
- `occupancy_id`
- `operator_link_id`
- `supplier_link_id`
- `schedule_id`
- `business_event_id`

IDs are unique, immutable and never reused. Names, addresses, trading styles, ownership, operators, status and premises may change without silently changing identity. A genuine entity merger, split, conversion or succession creates explicit predecessor/successor relationships. Historical records remain resolvable.

## 4. Binding built-world canon

1. Saltwater remains one sovereign city-state and one playable city only.
2. At least **10,000 distinct businesses** must exist in the Saltwater registry.
3. The business minimum does not create additional people. Staff, owners, customers and visitors are persons governed by BP-03 and all countability rules.
4. The total living population, including all police personnel, remains capped at 10,000. Businesses and organisations are not population units.
5. No second playable city, external territory or off-map expansion may be created through a business branch, supplier, parent company, franchise, address or generated narrative.
6. An external company/supplier may be represented as an off-map reference, but it cannot create external playable premises, residents or local roads.
7. The exact distribution of businesses by sector, size, ownership, district and operating status is not fixed by this document and must be generated or approved without violating other canon.
8. Business registry size and business simulation depth are separate. Every business has a stable identity and minimum coherent profile; only relevant businesses receive expanded persistent detail as required.
9. No business, property, facility or organisation may be created as a duplicate to evade identity, population, storage or jurisdiction constraints.
10. No Neon seed/import/bulk write is authorised by this specification.

## 5. Minimum business registry and business profile tiers

### 5.1 Count invariant
At all approved baseline states:

[
B(t) = |{business_id : entity_type=BUSINESS land registry_scope=LOCAL}|
]

Required invariant:

[
B(t) geq 10{,}000
]

The count is distinct local business identities, not branches, trading names, premises, brands, departments or aliases. A business with five branches counts once. Five independent businesses sharing one address count five only if they are genuinely distinct operators.

The registry must report:
- total distinct businesses;
- active, temporarily inactive, dormant, closed and historical businesses;
- businesses with one or multiple establishments;
- businesses with known/unknown premises;
- sector and size distributions;
- duplicate/identity-review exceptions;
- local vs off-map entity references.

The minimum applies to registered local businesses in the approved world baseline. Closed historical businesses remain in history but do not count as active operating businesses; whether they count toward the minimum registry total must be reported separately. The baseline must contain at least 10,000 distinct local business records, not 10,000 active premises.

### 5.2 Profile tiers
Profile tiers control processing and record detail, not entity existence or truth.

- **Tier 0 — registry profile:** stable ID, name/trading names, sector, legal/operating status, local/off-map scope, establishment references and basic provenance.
- **Tier 1 — operational profile:** ownership/operator links, premises, opening hours, staff-role references, basic capacity/service description and contact channels where relevant.
- **Tier 2 — relevant profile:** detailed occupancy, access, assets, schedules, suppliers, stock/service dependencies, incidents and case-linked history.
- **Tier 3 — persistent case/operational profile:** expanded event chronology, source documents, staff and access history, premises detail, relevant transactions, relationships and continuing activity.

A business or organisation materially connected to police activity, an incident, an investigation or another essential operational dependency may be promoted to detailed persistent status. Promotion must not discard established facts and must not fabricate missing history. BP-35 controls processing; BP-38/BP-39 preserve records.

The 10,000 minimum does not require 10,000 Tier-3 simulations. It does require every Tier-0 record to be a distinct, valid, non-placeholder business identity.

### 5.3 Sector coverage
The registry must support configurable sectors and sub-sectors, including as applicable:
- retail and wholesale;
- food, hospitality and accommodation;
- manufacturing, repair and industrial operations;
- warehousing, freight and logistics;
- construction and property services;
- finance, insurance and professional services;
- technology, communications and media;
- healthcare and social services;
- education and research;
- utilities, energy and water;
- transport and mobility;
- public administration and civic services;
- security and facilities services;
- agriculture, food production and distribution;
- arts, culture, sport and recreation;
- personal, domestic and community services;
- charities, associations and non-profit operations.

Sector lists are versioned and extensible by approved configuration. A sector is a classification, not a business identity.

## 6. Property, buildings and premises

### 6.1 Property record
A property record may include:
- property ID;
- linked BP-02 parcel ID and address ID;
- property type/use classification;
- current and historical owner-interest references;
- management entity;
- property status;
- linked buildings, premises and access points;
- land/building relationship;
- effective dates;
- source/provenance;
- risk/sensitivity tags;
- description and aliases.

BP-04 does not invent parcel geometry or address topology. A property without a resolved parcel/address must retain an explicit unresolved/approximate spatial state.

### 6.2 Building and structure
A building record may include:
- building ID and property ID;
- name/number/alias;
- building type and use;
- footprint/geometry reference from BP-02 where appropriate;
- floors/levels;
- construction/renovation/demolition history;
- structural status and condition;
- access-point list;
- premises/units list;
- utilities and installed-system references;
- safety/access restrictions;
- owner/operator/manager references;
- effective dates and provenance.

A building may contain multiple separately operated premises. A single site may contain several buildings. Do not assume one building equals one business.

### 6.3 Premises and units
Premises represent operationally meaningful places: shop, office, clinic, school, warehouse, residence, public counter, workshop, station, storage unit or other space.

A unit/space record may include:
- unit ID, parent building and premises;
- floor/level and internal locator;
- intended and actual use;
- occupiable capacity where known;
- access points;
- occupancy/tenancy links;
- operating entity;
- condition and access restrictions;
- time-valid status;
- source and provenance.

Detailed room layouts are created only where they materially support police operations, emergency response, access reconstruction or a case. BP-04 may store a simplified floor/space graph; BP-22 owns scene-specific control/search records, BP-20 surveillance coverage, BP-23 exhibit locations.

### 6.4 Physical access points
Access points include entrances, exits, doors, gates, loading bays, windows where relevant, service passages, vehicle barriers and controlled internal connectors.

Each access point must have:
- stable ID;
- parent premises/building;
- BP-02 spatial locator;
- access type and direction;
- active/closed/blocked state;
- permitted user/role categories;
- lock/key/control references;
- operating schedule where applicable;
- physical condition;
- time-valid history and provenance.

An access point is not proof that a person used it. Actual entry/exit is a separate observed, recorded or inferred event owned by the relevant operational/case division. Access permissions, key allocation and lock state must be distinguishable from actual access.

## 7. Ownership, management, tenancy and occupancy

### 7.1 Ownership interests
Property ownership is represented as one or more effective-dated interests. Support full ownership, joint ownership, beneficial/economic interests, secured interests and other canon-defined forms where required. Each interest identifies the holder, asset, interest type, share if known, start/end and source.

Ownership is not equivalent to possession, management, tenancy or authority to enter. Unknown ownership remains unknown. A disputed interest is stored as a disputed claim with provenance, not silently resolved.

### 7.2 Management
A property manager or facilities operator may be separate from the owner and tenant. Store appointment scope, authority, service period, duties and termination. Management authority does not automatically grant unrestricted access or ownership.

### 7.3 Lease, licence and occupancy agreements
An agreement record supports:
- agreement ID and type;
- parties and their roles;
- property/premises/unit references;
- execution date;
- commencement and expiry;
- renewal options and actual renewals;
- rent/fee terms as a reference to BP-34 financial records;
- permitted use;
- access rights and restrictions;
- subletting/assignment/third-party licence terms;
- maintenance and repair responsibility;
- termination, surrender, breach or dispute;
- source document/version and provenance.

An agreement's existence does not prove compliance, payment, actual occupancy or physical access. These are separate facts.

### 7.4 Occupancy
Occupancy records identify who or what occupies a premises/unit, in what capacity, over which effective interval, and under what source/right:
- tenant;
- licensee;
- owner-occupier;
- employee/resident occupant;
- contractor/service provider;
- temporary user;
- unauthorised/unknown occupant;
- vacant;
- disputed/uncertain.

A business occupancy links the business ID and establishment ID to the premises. Individual occupants/staff link through person IDs and employment/role records. Multiple concurrent occupancies are permitted only where premises use and rights allow them.

### 7.5 Subletting and third-party use
Subletting, assignment, concession, desk/room sharing, storage licence, contractor access and informal third-party use must be represented as distinct relationships. A primary tenant does not automatically authorise every third party. Record:
- granting party;
- receiving party;
- underlying agreement;
- premises/space;
- permitted purpose;
- access scope;
- effective interval;
- consent/approval status;
- source and uncertainty.

### 7.6 Financial interface
BP-04 owns agreement and occupancy facts; BP-34 owns invoices, receipts, arrears, deposits, rent payment postings, refunds and accounting balances. A payment record must reference the relevant agreement/period but does not itself prove physical occupancy. A lease does not prove payment. Financial status and occupancy status must never be conflated.

## 8. Business identity, ownership and operation

### 8.1 Business profile
A business record should include:
- business ID;
- legal name where applicable;
- trading name(s), former names and aliases;
- entity type and sector/sub-sector;
- local registry status;
- incorporation/registration reference if the fictional canon uses one;
- owner/control relationships;
- parent/subsidiary/franchise links;
- principal establishment;
- additional establishments;
- premises and property links;
- operator/manager;
- services/products and operating profile;
- staff/employment references;
- opening-hours schedule;
- contact channels;
- supplier/customer/dependency references;
- incident/case links;
- provenance and effective dates.

A business must not be considered a person. Its owners and employees are separate canonical people in BP-03.

### 8.2 Business vs establishment vs brand
- **Business:** distinct undertaking/operator identity.
- **Establishment:** one operational site/branch/location of a business.
- **Brand/trading style:** name/identity used for market presentation.
- **Parent company:** separate controlling entity where it exists.
- **Franchisee:** independent operator linked to a brand/franchisor where applicable.
- **Department:** internal organisational subdivision, not automatically a separate business.
- **Premises:** physical place, not an operator.

A business operating at three locations has one business ID and three establishment IDs. A building hosting ten unrelated operators has one building ID and ten relevant business/establishment links.

### 8.3 Ownership and control
Represent direct/indirect ownership, controlling interests, directors/managers and authorised representatives as effective-dated links. Do not infer ownership from a person's job title, presence, signature, phone contact or key possession.

Ownership/control claims may be confirmed, reported, disputed, estimated or unknown. Preserve source and confidence. A case may investigate a relationship without converting it into fact.

### 8.4 Business lifecycle
Support:
- proposed/registered;
- active;
- temporarily suspended;
- dormant;
- insolvent/under administration where canon uses the status;
- relocating;
- closed;
- dissolved/ceased;
- historical/succeeded/merged.

Status transitions require actor/source, reason, effective date and event record. A closed business is not deleted. Reopening may reactivate the same identity if the same undertaking continues; a genuinely new operator receives a new identity with predecessor/successor links.

## 9. Organisations and institutions

### 9.1 General organisation registry
Organisations include government bodies, public agencies, emergency services, healthcare providers, educational institutions, social-care providers, utilities, transport operators, charities, community associations, religious/cultural bodies, media organisations, private companies and other entities required for the city to function.

An organisation profile includes:
- organisation ID;
- official/common names and aliases;
- type, purpose and sector;
- status and effective dates;
- parent/affiliate relationships;
- governing/controlling body;
- leadership/representative role references;
- establishments/facilities;
- operating hours and service availability;
- public-facing functions;
- contact channels;
- staff/person links;
- asset/property references;
- external dependencies;
- source/provenance.

### 9.2 Institutional authority
BP-04 represents institutional entities and their physical/operational profile. BP-30 owns public institutional architecture, government authority and decisions. BP-31 owns professional standards/oversight where assigned. BP-05 owns police structure. BP-11/BP-12 own interagency dispatch and incident coordination.

An organisation record does not create constitutional authority, legal powers or command authority. Those must be explicitly defined by the owning governance division.

### 9.3 Service-provider representation
Healthcare, education, welfare, emergency, utility and transport organisations must have enough detail to support:
- what service they provide;
- where and when it is available;
- who operates it;
- broad capacity/availability;
- how police or public-service systems contact/refer to them;
- what happens when the service is disrupted;
- which records and assets are relevant to an incident or case.

For schools, colleges and non-police training providers, BP-04 also maintains proportionate provider-level education facts: programmes/courses offered, term or operating periods, enrolment capacity/availability, session and attendance-reporting arrangements, staff-role references, qualification-issuing body/profile where applicable, facilities and service schedules. It does not maintain a duplicate individual learner file or a full education simulator. Individual enrolment, attendance/participation and education history belong to BP-03; staff employment belongs to BP-33; schedules use BP-37; police training and police-training credentials belong to BP-32.

For non-police emergency-service and civil-protection agencies, BP-04 maintains proportionate operational profiles for service units and response assets: stable unit/vehicle/equipment references, home base and service area, capability, staffing-role and assigned-person references, readiness/availability state, capacity limits, and effective-time status. BP-33 remains authoritative for each employee's employment, qualification, shift and attendance; BP-04 must not duplicate those person or employment records. BP-11 owns emergency call intake, resource requests, dispatch communications, acknowledgements and unit-status exchange; BP-12 owns multi-agency incident coordination, command milestones and incident chronology; BP-35 coordinates time-valid state changes and causal effects. BP-09 remains the police resource inventory owner and must not become the asset register for other agencies. This is sufficient operational representation for credible mutual aid and civil protection, not a second deep emergency-services simulator.

Healthcare providers also require proportionate service-operation records: practitioner/service roles, emergency-care capability, capacity and availability, appointment slots and booking/referral status, treatment-encounter event metadata, public-health alert references and disruption/restoration. BP-04 records the provider/service event and care-access interface, not a detailed clinical chart. Person-specific injury/death/care facts are linked to BP-03 and relevant case/custody records (BP-17/BP-26); forensic medical examination remains BP-24; evidence continuity remains BP-23; BP-42 governs sensitive access; BP-35 coordinates time-valid capacity, alerts and disruption effects.

Transport operators require proportionate service records: operator and service identity, route/service ID, ordered stop/station/terminal references, fleet and vehicle availability profile, service capacity, accessibility characteristics, service restrictions, disruption/closure state and timetable references. BP-02 owns stop/terminal/parking spatial identity and route geometry; BP-04 owns operator/service/fleet profiles; BP-37 owns timetable definitions and scheduled runs; BP-09 owns police fleet only. Actual vehicle movement, dispatch and patrol decisions remain with the relevant operational owner.

Specialist service records remain in their owning domains. BP-04 stores stable entity and facility references, not duplicate clinical, individual education, employment, custody or dispatch records.

## 10. Facilities, infrastructure and physical assets

### 10.1 Facility model
A facility is a physical site or premises used to deliver a service or perform an operational function. Examples include stations, clinics, schools, shelters, depots, utility sites, transport terminals, warehouses, public offices and emergency-service bases.

Facility records include owner, operator, service type, premises, access points, opening/service hours, capacity where known, availability state, dependencies, contacts and incident history.

### 10.2 Infrastructure operators and assets
Represent utility, energy, water, communications, waste, transport and other essential-service operators and their relevant local assets. The record may include asset ID/type, location, owner, operator, service area, capacity band, operational state, maintenance state, dependencies and outage history.

BP-04 owns the entity/asset register and physical/operational relationships. BP-09 owns police equipment/resource readiness. BP-35 owns causal outage/disruption/restoration events. BP-41 owns notifications/reporting. Domain-specific technical detail is limited to what is needed for coherent consequences.

### 10.3 Asset lifecycle
Assets support acquisition/installation, commissioning, active operation, inspection, maintenance, failure, repair, replacement, decommissioning and disposal. Preserve asset identity and service history. A replaced asset is not silently the same physical asset unless it is a repair/upgrade of the same identity under explicit rules.

### 10.4 Access systems
Keys, key cards, codes, locks, alarms, access-control devices and access logs must be represented with:
- device/control ID;
- controlled access point(s);
- issuer/administrator;
- authorised person/entity/role;
- allocation/return/disable events;
- validity period;
- lost/stolen/compromised state;
- audit log reference;
- source and confidence.

Secret codes and credentials must not be stored in plain narrative or exposed to unauthorised player roles. BP-42 governs secrets. Access logs are records of a device/system event, not automatically proof of the identity of the person physically using the credential.

## 11. Opening hours, schedules and capacity

A business, establishment, organisation or facility may have:
- regular opening/service hours;
- shift/service windows;
- appointment-only operation;
- seasonal hours;
- public holidays/closure days;
- temporary closures;
- emergency exceptions;
- after-hours access;
- delivery and loading windows.

BP-04 owns the schedule definition and its link to the entity. BP-37 owns canonical time, calendar interpretation and schedule execution. BP-35 applies resulting events.

Capacity may describe customers, visitors, beds, classrooms, staff, storage, throughput, vehicles or service units. Each capacity must identify its unit, scope, time period, source and confidence. Capacity is not automatically actual occupancy or availability.

A planned opening schedule is not proof the business was open. Actual operating state, staff attendance, customer presence, access events and service delivery remain separate event/fact types.

## 12. Employment and people interfaces

BP-04 records which business/organisation has a staff role or employer relationship reference; BP-33 owns the employment contract and HR lifecycle; BP-03 owns the person's identity; BP-06 owns police personnel records.

A staff-role link may include:
- person ID;
- employer business/organisation ID;
- establishment ID;
- role/title;
- reporting manager reference;
- start/end;
- status;
- source and confidence.

Do not duplicate employee biographies, payroll, leave or attendance in BP-04. Do not create fictional staff solely to make every business appear busy. Staffing must respect the 10,000-person cap, approved population composition, schedules and employment capacity.

A business can exist with no currently recorded employees, unknown staffing, an owner-operated model or automated/outsourced operation. Missing staff records must not be filled with invented people.

## 13. Commercial activity, stock, supply and dependencies

### 13.1 Proportionate operating model
Each business may have a simplified operating profile describing services/products, operating hours, approximate scale, essential inputs, storage, delivery, suppliers and dependencies. Detailed transactions are created only where they materially affect simulation, police activity, finance or a case.

### 13.2 Stock and inventory
Where operationally necessary, stock records may include item/category, quantity or range, unit, location, owner, status, batch/serial where relevant, last verified time and source. Stock must reconcile across receipts, deliveries, use, sale, transfer, loss, seizure and disposal where those events are tracked.

BP-34 owns financial valuation and accounting entries. BP-23 owns seized-exhibit identity and evidential custody. BP-04 owns the business's operational stock reference and location, not evidence custody.

### 13.3 Supply chains and off-map dependencies
Supplier/customer relationships may link local businesses and off-map references. Store relationship type, goods/service category, direction, dependency level, effective dates, status, lead-time/route reference if known and provenance.

Off-map suppliers do not create additional playable territory or external NPC populations. Import/export events are represented as boundary-crossing transactions or abstract logistics events. Local storage, delivery, shortage and disruption consequences are simulated only to the degree needed by police/world continuity.

### 13.4 Essential-service dependencies
Record dependencies such as power, water, communications, transport, fuel, food, waste and emergency support. A dependency link should specify:
- dependent entity/facility;
- provider/operator;
- service type;
- criticality;
- alternative/redundancy if known;
- service area/location;
- effective period;
- disruption consequence class;
- provenance.

An outage is not generated merely because a dependency exists. BP-35 must process a causal disruption event with scope, duration, affected assets/services and recovery.

## 14. Business and built-world events

Every material state change is an event with stable event ID, entity ID, type, effective in-game time, recorded time, actor/system, reason, source, prior state, new state, related entity IDs and transaction outcome.

Event types include:
- entity creation/registration;
- name or classification change;
- ownership/control change;
- management appointment/change;
- lease/licence commencement, renewal, variation, termination or dispute;
- occupancy start/end/change;
- business opening, suspension, relocation, closure or reopening;
- premises acquisition/release;
- construction, renovation, damage, inspection or demolition;
- access-control/key issue, return, disable or compromise;
- asset commissioning, failure, maintenance, repair or replacement;
- service opening/closure/outage/restoration;
- education programme/course offering or withdrawal, term/session schedule change, enrolment-capacity change and education-service availability change;
- healthcare appointment booked/rescheduled/cancelled/attended/no-show; treatment encounter started/completed/referred (metadata only); public-health alert issued/updated/withdrawn;
- transport service/route created/changed/withdrawn; stop sequence or accessibility profile changed; timetable version activated; service run delayed/cancelled/restored; fleet vehicle serviceability/availability changed;
- stock receipt, movement, use, loss or reconciliation;
- supplier relationship start/end;
- incident, complaint, inspection or case linkage.

Events must be causally valid and time-ordered. An event cannot be effective before the entity or agreement exists unless it explicitly records a retrospective fact with provenance. Corrections append a new attributed record and preserve the original.

## 15. Police and case relevance

BP-04 must support police enquiries without deciding the investigation.

Relevant records may include:
- business registry extracts;
- property ownership and control;
- lease, licence and occupancy documents;
- premises/room and access-point details;
- key allocation and access-control logs;
- staff-role and shift references;
- opening hours and actual closure events;
- supplier/customer links;
- deliveries, stock and asset registers;
- CCTV/device location and operator references;
- service outages and maintenance history;
- complaints, inspections and incident history;
- business and premises relationships.

Each record must preserve whether it is original, copy, extracted data, reported claim, estimate or analyst-created summary. BP-23 owns exhibit registration and chain of custody; BP-20 owns surveillance collection; BP-22 owns scene access and search; BP-16 owns investigative decisions.

A property owner is not presumed to know all tenant activity. A manager is not presumed to be present. A keyholder is not presumed to have used a key. A business being registered at an address does not prove it operated there at a particular time. A lease does not prove actual occupancy. A CCTV system does not prove coverage or recording at the relevant time.

## 16. Data quality, reconciliation and anti-duplication

### 16.1 Required integrity checks
- Every property links to a valid parcel/address or explicit unresolved spatial status.
- Every building links to a property/site or explicit exception.
- Every premises/unit has a valid parent building/site.
- Every access point has a valid physical parent and spatial locator.
- Every local business has a stable ID and local registry scope.
- Every establishment links to one business or an explicit independent operator.
- Every occupancy links to a premises and an occupant entity/person.
- Every agreement links to parties, premises/assets and effective dates.
- Every ownership interest links to a holder and asset.
- Every staff link resolves to a canonical person and employer.
- Every organisation/facility has a valid type and status.
- Every local/off-map entity is correctly scoped.
- Every business count is based on distinct business identities.
- Business/organisation identities do not create duplicate person identities or population count contributions.

### 16.2 Duplicate detection
Potential duplicates are identified using names, addresses, registration references, owners, contacts, trading styles and historical links. Similarity is a review signal, not proof of identity.

Do not auto-merge entities solely because they share:
- an address;
- a phone number;
- a director/owner;
- a brand;
- a trading name;
- a premises;
- a supplier;
- a registered agent.

A merge requires a supported identity decision, provenance, affected-reference inventory and reversible migration plan. If two businesses are genuinely independent, retain separate IDs even when their records resemble each other.

### 16.3 Registry integrity
The 10,000-business minimum must not be met with:
- numbered placeholder names;
- duplicate aliases counted as businesses;
- multiple branch records counted as independent businesses;
- inactive dummy records created solely to inflate the total;
- businesses with no plausible identity or operating classification;
- external/off-map entities mislabelled as local.

A minimum valid profile requires distinct business identity, plausible name, sector, local scope, lifecycle status, provenance/generation source and at least a defined operating model or explicit unknown state. Detailed operational facts may remain unknown until generated or relevant.

## 17. Interfaces and ownership contracts

| Division | BP-04 provides | Other division owns |
|---|---|---|
| BP-02 | Property/building/premises/access IDs and spatial references | Parcels, addresses, road topology, geometry |
| BP-03 | Employer, household-site and premises links; education-provider/programme/facility references | Person identity, life status, population count and individual enrolment/attendance/education history |
| BP-05–BP-09 | Police facility/property references | Police structure, personnel, assignment, equipment readiness |
| BP-10–BP-12 | Business/site/facility location, access and opening context | Patrol, calls, dispatch and incident records |
| BP-13–BP-16 | Business/organisation entities and operational records | Crime taxonomy, occurrence, case and investigative decisions |
| BP-17–BP-19 | Provider/site/staff role references | Victim/witness/suspect roles and interviews |
| BP-20 | Building/access/device-site and operator references | Surveillance source, collection, coverage, retrieval |
| BP-22–BP-24 | Premises, access, layout and asset references | Scene control, exhibit custody and forensic examination |
| BP-30–BP-32 | Public bodies, facilities, provider identities | Institutional authority, standards and training |
| BP-33 | Employer, establishment and staff-role references | Employment contract, payroll, attendance, leave and HR |
| BP-34 | Property/business/agreement and transaction subject references | Accounting, rent payment, tax, procurement and balances |
| BP-35 | Entity profiles, schedules, dependencies and valid state transitions | Event orchestration, causality and processing |
| BP-36 | Organisation membership/venue links | Social relationships and household semantics |
| BP-37 | Opening-hours and operating-schedule definitions | Canonical clock, calendars and execution |
| BP-38–BP-39 | Domain entities, logical record requirements and history | Physical schema, persistence and recovery |
| BP-40–BP-41 | Searchable entity data and reportable state | Interface and notification/report presentation |
| BP-42 | Sensitivity labels and restricted entity attributes | Permission enforcement and access decisions |
| BP-43–BP-44 | Domain invariants, acceptance criteria and change impacts | Test strategy/evidence and controlled change |

All inter-division references must use stable IDs. Consumers may cache/denormalise data only while retaining the authoritative source ID, version and provenance.

## 18. Failure modes and edge cases

The system must explicitly handle:
- business with no known physical premises;
- one business with multiple establishments;
- multiple businesses sharing one building/address;
- one establishment occupying multiple units/buildings;
- property owner distinct from landlord, manager, tenant and operator;
- joint or disputed ownership;
- expired lease with continued physical occupancy;
- agreement executed but not commenced;
- agreement commenced but payment unknown;
- subtenant or third-party user without confirmed consent;
- vacant premises with residual keys/access;
- premises physically occupied but registry says vacant;
- business registered but not operating;
- business operating under a former/trading name;
- business closure while lease/property remains active;
- property sold while tenancy continues;
- building renovation or partial closure;
- access point damaged, blocked or compromised;
- key issued but not returned;
- key/access credential shared, copied, lost or stolen;
- access log with clock drift or uncertain actor;
- staff roster conflicting with observed presence;
- supplier failure or off-map disruption;
- utility outage affecting multiple premises;
- stock discrepancy, theft, damage or unverified quantity;
- duplicate or successor business identity;
- entity merger/split;
- missing source document or conflicting claims;
- historical location/address change;
- business count falling below 10,000;
- attempted local entity creation outside Saltwater;
- population-cap pressure from proposed staffing/visitors;
- database failure during multi-record business/property transaction.

Failures must retain the last valid state, record the exception and prevent partial or contradictory updates. Unknown remains unknown; no fabricated owner, tenant, occupant, employee, opening time, keyholder, stock quantity or payment status.

## 19. Security and information boundaries

BP-04 classifies information; BP-42 enforces permissions.

Sensitivity categories include:
- public registry information;
- ordinary commercial/operational information;
- private ownership/tenancy and contract information;
- restricted access-control/key/lock information;
- sensitive infrastructure and facility details;
- confidential staff and personal links;
- police-sensitive or case-linked material;
- credentials/secrets.

Rules:
- Public business identity does not make all records public.
- Property ownership does not automatically grant access to tenant records.
- A business employee does not automatically access ownership, payroll, security or customer records.
- Access to key codes, alarm credentials, restricted facility layouts and sensitive infrastructure is role- and purpose-controlled.
- Player-visible records must respect the character's authority and information actually obtained.
- Hidden case truth must never be exposed through an entity profile, business owner field, generated narrative or cross-reference before the exact `bingo` trigger defined by BP-01.
- Every sensitive read, export, disclosure or modification is attributable and auditable.

## 20. Storage and performance requirements

The business/property world must be storage-efficient without losing semantic content.

- Use compact stable IDs, enumerated types, shared dictionaries and references for repeated facts.
- Store business identity once; branch/establishment records reference it.
- Store address/geometry once in BP-02; property/building records reference it.
- Store person identity once in BP-03; staff and ownership links reference person IDs.
- Store employment once in BP-33; do not duplicate contracts/payroll/attendance.
- Store financial transactions once in BP-34; agreement records reference them.
- Store source documents and evidence once under the relevant record/evidence system; derived summaries reference originals.
- Avoid repeating full company descriptions, addresses, owner biographies, schedules and supplier profiles in every linked record.
- Use effective-dated changes and event references rather than duplicating entire entity snapshots for every small change.
- Index only measured access patterns; account for index and TOAST growth.
- Preserve original high-entropy narrative/source content losslessly where required.
- Measure baseline and estimate all database growth before any Neon write under the mandatory BP-38/BP-43/BP-44 approval process.

A compact record is acceptable only if all required meaning, history, provenance, uncertainty and relationships remain recoverable.

## 21. Acceptance criteria and test suite

### A. Registry and business minimum
- **AC-A01:** The approved local business registry contains at least 10,000 distinct valid business identities.
- **AC-A02:** Branches, establishments, brands, aliases and premises are not incorrectly counted as separate businesses.
- **AC-A03:** Every business has a unique stable ID, plausible identity, sector, local scope, lifecycle status and provenance.
- **AC-A04:** Duplicate/placeholder/off-map entities cannot inflate the local minimum.
- **AC-A05:** Business count reports distinguish total registry identities from active operating businesses.
- **AC-A06:** Business records do not create people or increase population count.
- **AC-A07:** Business staffing and visitors remain subject to BP-03's 10,000-person cap.

### B. Property and premises integrity
- **AC-B01:** Every property links to a valid BP-02 parcel/address or explicit unresolved state.
- **AC-B02:** Building, premises, unit and access-point parent relationships are valid.
- **AC-B03:** Multiple businesses can share a building without identity collision.
- **AC-B04:** One business can operate multiple establishments without duplicate business identity.
- **AC-B05:** Physical access points have stable IDs, spatial locators and effective-dated status.
- **AC-B06:** Historical building/premises changes do not rewrite past event locations.

### C. Ownership, tenancy and occupancy
- **AC-C01:** Owner, manager, landlord, tenant, operator and occupant roles remain distinct.
- **AC-C02:** Ownership and occupancy support multiple, disputed and time-bounded interests.
- **AC-C03:** Lease/licence dates, renewals, expiry and termination preserve history.
- **AC-C04:** Subletting and third-party occupancy require explicit relationship records.
- **AC-C05:** Agreement existence, rent payment and physical occupancy are not conflated.
- **AC-C06:** Expired agreement with continued occupancy is representable without silently renewing it.
- **AC-C07:** Property transfer does not erase a continuing tenancy or prior ownership.

### D. Organisation and facility operations
- **AC-D01:** Each organisation/facility has a stable identity, type, status, operator and location reference.
- **AC-D02:** Public authority is not inferred from an organisation record.
- **AC-D03:** Service hours, capacity, actual availability and temporary closures are distinguishable.
- **AC-D04:** Essential-service operators and dependencies can be traced across affected facilities.
- **AC-D05:** Off-map organisations cannot create external playable geography or population.
- **AC-D06:** Healthcare providers expose service capability, capacity, appointment/referral availability, treatment-event metadata and public-health alert references without creating duplicate clinical charts or bypassing BP-42 access controls.
- **AC-D07:** Each public transport service route references valid BP-02 stops and route geometry, a BP-04 operator/fleet profile and a BP-37 timetable; service capacity/accessibility and disruption state are time-valid.

### E. Staff, stock, supply and events
- **AC-E01:** Staff links resolve to canonical BP-03 person IDs and BP-33 employment records.
- **AC-E02:** Business staff are not duplicated across employer/establishment views.
- **AC-E03:** Schedules and planned opening hours are not treated as proof of actual presence/open status.
- **AC-E04:** Stock movements reconcile where inventory tracking is enabled.
- **AC-E05:** Supplier and service dependency disruptions have causal event references.
- **AC-E06:** Material business/property state changes preserve actor, reason, source and effective time.
- **AC-E07:** Failed multi-record transactions leave no partial authoritative state.

### F. Police, evidence and information boundaries
- **AC-F01:** Police enquiries can retrieve relevant property, occupancy, access, staff, business and service records through authorised workflows.
- **AC-F02:** Access logs distinguish credential/device events from verified human identity.
- **AC-F03:** Business registration/address does not prove operation or presence at a historical time.
- **AC-F04:** Source documents, claims, estimates, observations and summaries remain distinguishable.
- **AC-F05:** Evidence custody remains owned by BP-23; BP-04 cannot bypass it.
- **AC-F06:** Restricted keys, codes, facility layouts and sensitive business records are not disclosed to unauthorised roles.
- **AC-F07:** No business/entity view leaks hidden perpetrator identity before exact `bingo`.

### G. Quality, scale and storage
- **AC-G01:** Duplicate detection flags candidates without unsafe automatic merges.
- **AC-G02:** Registry reconciliation detects missing/invalid entity relationships and business-count drift.
- **AC-G03:** 10,000+ business registry queries remain usable within measured performance budgets.
- **AC-G04:** Storage benchmark includes shared references, indexes, event history and representative high-entropy source text.
- **AC-G05:** Every acceptance test links to source requirement IDs and retains reproducible evidence.
- **AC-G06:** No Neon write occurs without baseline, byte/MiB estimate, assumptions, uncertainty, projected total and explicit user approval.
- **AC-G07:** Actual post-write growth is measured and compared with the approved estimate.

Required test classes: identity/duplicate detection, minimum registry, entity relationship integrity, temporal ownership/tenancy, multi-tenant buildings, occupancy conflict, access-control history, schedule/time validity, population-cap interaction, off-map containment, supply disruption, transaction atomicity, permissions, police evidence interfaces, 10k-scale query performance, storage benchmarks, backup/restore and regression.

## 22. Source traceability

| Source IDs | BP-04 obligation |
|---|---|
| S06.R01–R03; S06.T01 | Property, tenancy, occupancy, access and temporal consistency |
| S07.R01–R04; S07.T01–T02 | Business registry, commercial operations, police-relevant links, persistent records |
| S08.R01–R03; S08.T01 | Employer identity and employment interface |
| S09.R01–R03; S09.T01 | Trade, suppliers, logistics, local/off-map dependencies |
| S11.R02; S11.T01 | Public institutions, organisations and operational premises |
| S13.R01; S13.T01 | Healthcare/provider/facility representation |
| S14.R01; S14.T01 | Education and training provider representation |
| S15.R01–R02; S15.T01 | Social-care and community provider representation |
| S16.R01–R03; S16.T01 | Utilities, communications, infrastructure operators and disruption links |
| S17.R01 | Transport operators, service routes, fleet profiles, stops, timetable references, parking and accessibility interfaces; BP-02 owns spatial geometry and BP-37 timetable execution |
| S18.R01–R03; S18.T01 | Buildings, facilities, physical assets, access and maintenance |
| S20.R01–R03; S20.T01 | Food, essential services, stock, distribution and supply |
| S21.R01–R03; S21.T01 | Culture, media, recreation, events and civic organisations |
| S22.R01–R02; S22.T01 | Emergency-service agency, facility, staffing and interagency interfaces |
| X01–X06, X09 | Stable identity, single source of truth, time, reconciliation, epistemic distinctions, source preservation and police-depth scope |

Full source wording and exact source JSON pointers remain in `SALTWATER-52-TO-44-CROSSWALK.md` and the preserved 52-division source JSON.

## 23. Resolved design decisions

The master blueprint and current implementation establish the following choices. These are working design decisions, not separate player-approval gates:

1. **Business minimum:** at least 10,000 total distinct local business identities; active, seasonal and temporarily inactive counts are reported separately.
2. **Sector and size distribution:** use the deterministic fictional business registry distribution and its recorded sector, activity, legal-form and size classifications. No additional quotas are required.
3. **Registration model:** stable Saltwater business IDs and fictional legal/registration attributes are authoritative. No real-world registration numbers, jurisdiction or external legal system is implied.
4. **Property and addressing:** BP-02 owns canonical parcel/address identities and spatial topology; BP-04 properties, buildings, premises and units link to those identities. Generated fictional records retain explicit source and confidence metadata.
5. **Non-police detail:** model only the facility, provider, capacity, schedule, operator and service details needed for city and police gameplay.
6. **Inventory:** track stock where the business or facility type enables inventory; do not create stock ledgers for every entity by default.
7. **Service operations:** service capability, scheduled hours, capacity, actual availability and temporary disruption are separate facts. Actual NPC activity is not inferred from a timetable.
8. **Generation and storage:** deterministic source generators, compressed archives, typed operational references and reproducible storage/performance measurements are used. Disposable validation is routine; production Neon writes retain the explicit release controls required by BP-38/BP-43/BP-44.

NPCs make ordinary ownership, management, tenancy, consent, service and business decisions autonomously. The simulation records the actor, source, authority where applicable, effective time and recorded time. No human-player approval is required for ordinary fictional NPC decisions or routine in-game state transitions.

## 24. Completion statement

**Design status:** `DESIGNED`; the domain model and eight design choices above are resolved against the approved master blueprint and current fictional game canon.  
**Implementation status:** `IN_PROGRESS`; source data, runtime interfaces and database migrations are being completed.  
**Test status:** `PARTIALLY_ACCEPTED`; 18 of 48 criteria currently pass, with reproducible disposable PostgreSQL, Python and BP02 operational-geography evidence.  
**Verification status:** `IN_PROGRESS`; BP04 remains incomplete until all 48 acceptance criteria pass.

No separate human approval is required for NPC decisions, ordinary fictional records or routine in-game operations. Production Neon writes remain separately controlled and require the explicit release instruction required by the project.


## 2026-11-28 approved NPC integration implementation decisions

The playable simulation has one human player; all other people, businesses, organisations, landlords, tenants, operators, occupiers, employees, service providers and counterparties are fictional NPCs. NPC decisions are represented as in-world authority/consent records with actor, source and effective/recorded time. They do not require a human-player approval gate. This rule applies to the following accepted implementation scope:

1. Subletting starts, ends and exact replays serialize on the physical unit; two-session PostgreSQL 16/18 acceptance covers the interleavings.
2. Third-party occupancy supports business, organisation and BP03-person identities, explicit use types and append-only lifecycle events. Owner/landlord, tenant, operator and occupant are separate role references.
3. BP03 owns canonical person identity and population counting; BP33 owns NPC employment records; BP04 stores validated staff-role links to those records. One person may hold multiple jobs without duplicate population counting.
4. BP34 owns rent schedules, charges, payment transactions, allocations and derived balances. BP04 stores only external finance references; rent arrears or settlement never directly changes agreement or physical occupancy status.
5. BP04 facility/service profiles link organisation operators, healthcare capability/referral metadata, BP02 route/stop references, BP37 timetable references, fleet/accessibility metadata, utility dependencies and append-only disruption events. Clinical records remain outside BP04.

Implementation migrations 0025–0032 and the complete [110-table disposable PostgreSQL 16/18 acceptance workflow 46142915466](https://github.com/Joshuaogri/saltwater/actions/runs/46142915466) passed on both versions, including archive import, gameplay lookup, player find/inspect, performance benchmark and repeat-import stability. These five requested workstreams are approved and cleared. This addendum does not declare the entire BP04 division complete; the remaining 48-criterion audit is authoritative for outstanding work.


## 2026-11-28 BP02 operational geography and BP04 spatial binding acceptance

BP02 full parcel/address/access acceptance [run 46144797735](https://github.com/Joshuaogri/saltwater/actions/runs/46144797735) passed on 2026-11-28. It released 420/420 canonical parcels and addresses, 2,948 operational access points, and 2,984 BP04 access locators with effective dates; all structural checks passed, all five frontage exceptions received geometry dispositions, and zero address-road-access exceptions remain unresolved. The run performed no database or Neon write.

AC-B01 (property-to-parcel/address identity) and AC-B05 (stable, spatially located, effective-dated access points) are now PASS. The remaining BP04 acceptance criteria continue under the strict audit; this does not declare BP04 complete.


## 2026-11-28 NPC tenant/operator role matrix extension

The property-tenure generator creates deterministic independent tenant/operator business pairs across every generated unit class, while retaining self-operated premises. Operator references resolve to canonical business identities. Both direct-owner and third-party property management appointments remain represented. The regenerated canonical tenure archive and all 14 focused regression tests passed in [workflow 46145870349](https://github.com/Joshuaogri/saltwater/actions/runs/46145870349). This extends AC-C01 evidence but does not close the criterion: independent landlord/title-holder and occupant/tenant combinations, plus broader database-level cross-register role coverage, remain outstanding. No production Neon write occurred.


## 2026-11-28 management-role coverage audit

The property-tenure runtime audit now reports direct-owner versus third-party management appointment coverage for every generated unit class. Regression coverage confirms the class inventory is complete and each property's current management appointment is counted exactly once. The 15-test property ownership/occupancy build passed in [workflow 46146300199](https://github.com/Joshuaogri/saltwater/actions/runs/46146300199). This is additional AC-C01 verification; independent landlord/title-holder and occupant/tenant arrangements plus database-level role combinations remain outstanding.


## 2026-11-28 explicit non-owner landlord / head-lessee authority

Migrations 0033–0034 add a property- or unit-scoped letting-authority register with separate grantor and grantee organisations, head-lease/leasehold/concession/contractual letting-right types, effective years, instrument provenance and append-only authority events. An occupancy agreement may identify a non-owner landlord only when the registered proprietor granted a matching authority for that property/unit and commencement period and the grant event is recorded. Revoked and superseded authorities cannot support a new agreement. Direct title-holder landlords remain valid without a separate authority. Disposable PostgreSQL migration, ledger and functional acceptance passed in [workflow 46147360337](https://github.com/Joshuaogri/saltwater/actions/runs/46147360337). The canonical 420-property/10,000-business generated landlord matrix has not yet been expanded; AC-C01 remains PARTIAL.


## 2026-11-28 generated independent landlord and head-lessee roles

The canonical tenure generator now creates 8 independent head-lessee organisations distinct from property owners and managing agents. Each is linked to a property-scoped letting authority granted by the registered title holder and an immutable grant event with a deterministic UUID. 1,821 current occupancy agreements identify an authorised head-lessee as landlord; owner-landlord agreements remain unchanged elsewhere. The 19-test generator suite passed [46148027844](https://github.com/Joshuaogri/saltwater/actions/runs/46148027844), and disposable PostgreSQL 16/18 schema and authority acceptance passed [46148246368](https://github.com/Joshuaogri/saltwater/actions/runs/46148246368). AC-C01 remains PARTIAL until the wider canonical occupant/tenant role matrix and typed-import acceptance are complete.
