# Saltwater Canon Decision Record — Population Scope and Foundational Geography

**Decision ID:** SW-CANON-001  
**Date:** 2026-11-24  
**Authority:** User instruction to resolve the outstanding population-counting and geography decisions  
**Status:** ADOPTED FOR BLUEPRINT DESIGN; implementation and map construction remain separate  
**Repository:** `Joshuaogri/saltwater`  
**Branch:** `main` only

This record closes the population-scope and foundational geography questions previously left open in BP-02 and BP-03. It does not alter the fixed BP-01–BP-44 structure, authorize production Neon writes, or claim that a map/database seed has been implemented.

## 1. Population count and 10,000-person cap

### 1.1 Binding count formula

At any authoritative simulation time, count the **distinct living people** satisfying at least one of these conditions:

1. Saltwater is their current usual residence, including when they are temporarily outside the city-state; or
2. they are physically present within the Saltwater boundary, including visitors, commuters, temporary workers and temporary residents; or
3. they hold an active appointment/employment membership in the Saltwater Police Service, including when temporarily absent or living off-map.

The population count is the set union of those categories by canonical `person_id`, never the sum of category totals. A person satisfying two or three conditions counts once.

`population(t) = count(distinct person_id where living AND (usual_resident OR physically_present OR active_police_member))`

The hard ceiling is **10,000**. It applies to this union at every committed simulation state. The system must reject any admission, birth, arrival or status transition that would make the union 10,001. The remaining headroom is shared by all new countable people, not reserved for a particular category.

### 1.2 Opening population — exact target, not a range

The opening seed target is exactly:

- **9,000 civilian usual residents** (people whose primary home is in Saltwater and who are not assigned to the opening police-service cohort);
- **500 active Saltwater Police Service personnel**;
- **9,500 distinct living countable people in total**;
- **500 unused capacity**.

The 9,000 and 500 are mutually exclusive opening cohorts. A police employee who also lives in Saltwater belongs to the police cohort for this opening reconciliation and is not duplicated in the 9,000 civilian cohort. All people receive one canonical person identity. These are exact identity-level seed targets, not aggregate-only placeholders; each person must eventually be represented by an individual record before the opening world is declared provisioned.

The 500 police figure is an opening personnel headcount, not an additional population layered on top of 10,000. Police-service membership covers active sworn officers and active civilian employees directly appointed/employed by the service. Contractors and external agency staff are not police employees; they count only if they meet the usual-resident or physically-present rule.

### 1.3 Category treatment

| Person situation | Counts toward 10,000? | Rule |
|---|---:|---|
| Usual Saltwater resident, currently in or out of the city-state | Yes | Remains countable until death or permanent change of usual residence |
| Active Saltwater Police Service member, resident or nonresident, present or absent | Yes | Active service membership independently qualifies |
| Nonresident visitor physically inside Saltwater | Yes | Counted from entry until exit |
| Nonresident commuter/worker physically inside Saltwater | Yes | Counted while present; job alone does not count while off-map |
| Temporary resident/temporary accommodation occupant | Yes | Counted while physically present; no arbitrary stay-duration threshold |
| Nonresident person outside Saltwater with no active police membership | No | May retain a case-linked identity/reference, marked outside the population set |
| Person permanently moved away, no longer physically present and not active police | No | Historical identity and records remain |
| Deceased person | No | Death does not delete identity or history |
| Child/newborn | Yes if usual resident or physically present | Age does not exempt a person; birth alone does not count a nonresident who is not present |
| Person with multiple jobs, homes, roles or memberships | Once | Canonical identity deduplicates all qualifying links |

Usual residence means the person's primary home/ordinary centre of life, not citizenship, birthplace, temporary hotel occupancy or a mechanically imposed number of days. A change of usual residence requires an attributable effective-dated move event. There is no automatic 30/90-day conversion rule.

### 1.4 Lifecycle and capacity events

- Entry by a nonresident creates a count contribution at the effective boundary-entry event.
- Exit removes only the physical-presence contribution; a resident or active police member remains countable.
- A move-in creates resident status; a move-out removes it only when the person is no longer physically present and is not an active police member.
- Police appointment creates the police-membership qualification. Separation removes that qualification but does not remove a person's resident/presence qualification.
- Death removes the living contribution exactly once, preserving identity, memberships and historical links.
- Duplicate events, retries and corrections cannot add/remove capacity twice. Corrections are attributable new events.
- Concurrent admissions are serialized/atomic against the same 10,000 ceiling.
- The system must expose both the unique capped population and useful sub-counts (residents, police members, nonresident persons currently present). Sub-counts overlap where appropriate and must never be added to derive the total.

## 2. Foundational geographic canon

### 2.1 Territory and physical form

- Saltwater is one **single, contiguous island city-state** and one playable city/jurisdiction.
- There are no detached playable islands, external territories, second cities or outlying playable jurisdictions.
- The fictional landmass has a **12 km east–west by 9 km north–south bounding extent** in its local map coordinate system. This is a map extent, not a claim of surveyed accuracy.
- Saltwater is coastal and has one principal sheltered harbour on its eastern side. The harbour is part of the same island and city-state.
- A low central-western ridge provides a natural topographic divide; the built city remains connected by the approved road network.
- There is no natural river assumed in the baseline. A managed canal/freight basin may be represented in the Southworks area as a constructed water feature, not a natural river.
- No detached island, second settlement or external road corridor is to be generated.

### 2.2 Coordinate reference

- CRS identifier: `SW-LOCAL-01`.
- Units: metres.
- Origin: south-west corner of the 12 km × 9 km map extent.
- X increases east; Y increases north.
- Valid extent: `0 ≤ X ≤ 12000`, `0 ≤ Y ≤ 9000`.
- Coordinate precision: whole metres for the initial city map; finer precision may be stored only where a later approved use requires it.
- Coordinates are wholly fictional local-grid coordinates. They are not latitude/longitude and imply no real-world location or survey.
- Geometry source, version, confidence and effective dates remain mandatory. The island outline and all subdivision polygons must be validated for closure, containment and topology before use.

### 2.3 Administrative structure

The city has **eight administrative districts**, each with three named neighbourhoods/localities, for **24 neighbourhoods** total. The districts and neighbourhoods are:

| District | Neighbourhoods |
|---|---|
| Civic Core | Assembly Quarter; Government Square; Museum Gardens |
| Old Quays | Old Harbour; Ropewalk; Dockside |
| Central Market | Grand Market; Exchange Ward; Theatre Quarter |
| Northbank | Northbank West; Northbank East; University Quarter |
| East Harbour | Port Quarter; Customs Ward; Marina Point |
| Westgate | Westgate; Foundry Quarter; Garden Ward |
| Southworks | Industrial Park; Rail Yards; Canal End |
| Greenfields | Parkside; Reservoir Ward; South Gardens |

These are canonical names and counts. Districts partition the single city-state without gaps or overlaps; neighbourhoods partition their parent district. Functional/land-use overlays may cross administrative boundaries but do not create additional districts or neighbourhoods.

### 2.4 Functional geography and movement

- Civic Core is the seat of city-state government and central civic institutions.
- Old Quays and East Harbour form the historic and active maritime/port frontage; the principal harbour, ferry/port interchange and customs functions are located in this eastern coastal sector.
- Central Market is the principal high-street, exchange, retail and entertainment centre.
- Northbank contains major education and mixed residential/institutional uses.
- Westgate contains western access, mixed commercial, residential and light-industrial uses.
- Southworks contains heavier industry, freight/rail yards and the constructed canal/freight basin.
- Greenfields contains the principal public open-space, reservoir and lower-density residential/garden areas.
- The road graph uses a connected primary orbital distributor, radial district connectors and a finer local-street grid. Every routable segment must connect valid nodes; barriers, bridges, grade separation, one-way restrictions and private/emergency access are explicit. Exact road names and segment inventory are to be authored as a versioned map dataset, not fabricated as a decorative illustration.
- The island's external passenger/freight connection is maritime. Off-map destinations remain abstract external references; no off-map routable road network is part of Saltwater.
- The initial address convention is: district → neighbourhood → named road → building number → optional unit/suite. Building numbers increase along each road from its designated origin; odd/even side assignment is consistent per road. Stable address and parcel IDs remain opaque and immutable.
- Land-use overlays use residential, commercial, mixed-use, civic/government, institutional/education, industrial/freight, transport/maritime, utility, open-space/recreation and environmental/reservoir classes. A land-use label does not itself create a property, business or person.

### 2.5 Spatial construction constraints

The decisions above settle the geography baseline, but they do not pretend that the detailed map is already built. The next map-data work must create and validate the island boundary, eight district polygons, 24 neighbourhood polygons, harbour/coastline, terrain features, parcels, named roads, nodes, segments, access points and landmark/facility register as one coherent versioned dataset. It must be connected and routable for dispatch/patrol use, not a decorative disconnected street sketch.

No real-world coordinates, real-world country, actual external jurisdiction, or unsourced real map is to be imported. No exact street, parcel, property or address may be invented outside the controlled map dataset.

## 3. Remaining work versus closed decisions

Closed by this record:
- who counts toward the 10,000 cap;
- how residents, police, visitors, commuters, temporary presence, absences, departures and deaths affect the count;
- exact opening cohort arithmetic and headroom;
- one-island physical form, map extent and coordinate convention;
- district and neighbourhood counts/names;
- functional geography, access model and address convention.

Still implementation/design work, not unresolved canon:
- generate the individual opening person identities and reconcile them;
- build/validate the actual versioned polygon and road graph dataset;
- author exact street/parcel/address/facility records;
- define measured processing-tier budgets and runtime promotion implementation under BP-35/BP-43;
- define schema/event/recovery mechanics under BP-38/BP-39;
- decide BP-04 business category/site distribution and validate 10,000+ distinct businesses.

## 4. Authority and restrictions

This record resolves design canon only. It does **not**:
- approve a Neon production migration, seed, import, upload, credential change or any other production write;
- claim that synthetic test fixtures are canonical persons or businesses;
- mark BP-02/BP-03 fully implemented, tested or released;
- change the fixed BP-01–BP-44 structure;
- approve any business-distribution assumptions owned by BP-04.

All development remains directly on GitHub `main`. Neon production remains unchanged absent a separate exact-operation approval.
