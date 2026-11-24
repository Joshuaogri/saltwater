# SW-UNS-001 — Saltwater Universal Naming Standard

**Class:** CORE FOUNDATIONAL STANDARD — MANDATORY  
**Status:** ADOPTED BY USER — 2026-11-24  
**Applies to:** All 44 blueprint divisions and every named entity in Saltwater  
**Authority:** BP-01 global charter; domain ownership remains with the relevant BP division  
**Scope:** Design and governance standard only. This document does not implement a database registry or authorise Neon changes.

---

## 1. Purpose

Saltwater must have one coherent naming system. Names must be distinctive, natural, stable, searchable, historically traceable and resistant to duplication, ambiguity, accidental reuse and deliberate bypass.

This is a core world foundation, not an optional feature. Every division must use the same universal naming authority. A division may define vocabulary and domain-specific naming rules, but it may not create a competing registry, weaken uniqueness, recycle a retired name or bypass the shared controls.

**Controlling rule:** Every named entity has one permanent entity ID and one unique canonical name, subject to the single, explicit sovereign/city shared-name exception in §3.2. Names are labels; permanent IDs are identity. Neither may substitute for the other.

## 2. Coverage

The standard applies to all named and name-bearing entities, including but not limited to:

### 2.1 People and identity
- Every civilian, resident, visitor, police employee, recruit, official, business owner, employee, victim, witness, suspect, offender, applicant, contractor and other person.
- Legal/full names, preferred display names, documented former names, aliases, nicknames and pseudonyms.
- Households and other named person groupings where represented as entities.

### 2.2 Geography and movement
- City-state, city, districts, neighbourhoods, localities, zones, roads, streets, avenues, crescents, closes, lanes, alleys, paths, cycleways, junctions, roundabouts, bridges, tunnels, crossings, routes, stations, stops, terminals, harbours, quays, docks, basins, parks, gardens, squares, landmarks, terrain and natural/constructed features.
- Parcels, canonical addresses, named estates and other geographic locators.

### 2.3 Built environment and economy
- Properties, houses, apartment blocks, estates, towers, buildings, facilities, premises, units, rooms, entrances, gates, access points and named infrastructure.
- Businesses, trading names, companies, employers, operators, suppliers, institutions, public bodies, charities, clubs, schools, hospitals, courts, banks, hotels, restaurants and other organisations.

### 2.4 Police and operational world
- Police services, commands, departments, divisions, units, teams, stations, posts, beats, patrol areas, call signs, radio channels and named operations.
- Vehicles, vessels, equipment, devices, resources, storage locations and named assets.
- Incidents, cases, investigations, evidence collections, exhibits, reports, records, projects, procedures, policies, forms, schedules, events and other named operational objects.

The list is deliberately inclusive. A division cannot claim an entity is outside the standard merely because its entity type is not listed.

## 3. Universal identity and uniqueness rules

1. Every entity receives a stable, opaque, permanent entity ID before or atomically with creation.
2. Every named entity has one canonical name. Unnamed entities may use a controlled type label in internal interfaces, but must not be given a fabricated public name.
3. Canonical names are unique across the **shared Saltwater canonical-name namespace**, not merely within one table, district, division or entity type. An identical canonical name cannot be assigned to two different entities, even if they are different types, except for the single, tightly scoped sovereign/city exception defined in §3.2.
4. A name remains reserved to its entity throughout its lifecycle and after retirement, closure, demolition, death, dissolution, departure or deletion from active use. It is never recycled for a different entity.
5. A genuine rename creates a new name record linked to the same entity ID. It does not erase, overwrite or transfer the former name.
6. Names never act as primary keys, foreign keys or substitutes for entity IDs.
7. Every reference to a named entity resolves through its stable ID. Name search is a discovery mechanism and must not silently select among ambiguous matches.
8. Name uniqueness is enforced at the authoritative shared registry, not by a client-side check or a division-specific list.
9. Creation and name reservation are atomic. Concurrent requests for the same name cannot both succeed.
10. The same rules apply to player-created, NPC-created, generated, imported, migrated, corrected and manually entered entities.

### 3.1 What “unique” means for people

- Each person's complete canonical full name must be unique in the shared namespace.
- Preferred display names and registered aliases must also be unambiguous and must pass registry collision checks.
- First-name components and surname components may naturally recur; uniqueness applies to the complete registered name, not to common linguistic components in isolation.
- If two people would otherwise receive the same full name, generate a genuinely distinct, plausible full name (for example, a different middle name or surname). Do not append arbitrary numbers as a routine workaround.
- Identity is never inferred from a name alone. Two records must not be merged merely because their names match.
- A legal name change preserves the former name and its effective dates. The former name cannot be reassigned to another person.

### 3.2 Sole shared-name exception — Saltwater sovereign territory and playable city

The user has expressly approved one exception: the sovereign territory and the playable city may both retain the exact canonical display name **Saltwater**, while remaining two distinct geographic entities with two distinct permanent spatial IDs.

This exception is deliberately narrow and is not a general relaxation of global uniqueness:

1. It applies only to the one canonical sovereign-root entity (existing kind 1 / entity code `saltwater-state`) and the one canonical playable-city entity (existing kind 2 / entity code `saltwater-city`).
2. Both entities retain their existing stable IDs, ownership, parent relationship and separate records. They must not be merged or treated as one entity.
3. The exact normalized canonical name `saltwater` is permitted for this pair only. No third entity, alias, business, person, road, district, neighbourhood, property, operational object or historical name may claim it.
4. The registry must represent this as an explicit, code-level exception for this exact pair of entity types/IDs, not as a general duplicate-name allowance or a client-side bypass.
5. Both names remain searchable by stable ID and entity type. A name-only search for `Saltwater` must return both records as an explicit ambiguity/disambiguation result; it must never silently choose one.
6. Case, punctuation, spacing, Unicode and other normalized variants do not create additional exceptions. The exception covers the one exact canonical normalized key only.
7. The exception must be auditable and covered by positive tests for the permitted pair and negative tests proving a third entity and all other cross-type duplicates are rejected.
8. The exception does not extend to aliases, former names, retired names or any other name form.

This is the only shared canonical-name exception unless the user expressly approves another one and the standard is versioned accordingly.

### 3.3 Addresses and structured locators

An address is both a structured locator and a display form. Its uniqueness is enforced by a canonical address key built from the authoritative components (geography ID, road ID, building/plot number and unit where applicable), not by punctuation in a display string alone. Two distinct premises may share a building address only where the explicit multi-unit address model permits it; each unit/access point must remain individually resolvable. BP-02 owns geographic/address identity; BP-04 owns property, building, premises and unit identity.

## 4. Name forms and registry model

The central registry must distinguish the following concepts:

| Field/concept | Rule |
|---|---|
| Entity ID | Permanent opaque identity; never reused |
| Name ID | Permanent identity for one name assignment/version |
| Entity type | Controlled type from the owning division |
| Canonical name | One official current name; globally unique |
| Normalized key | Deterministic comparison key used for uniqueness |
| Name form | Canonical, preferred, alias, former, legal, trading, call sign or other controlled form |
| Status | Reserved, active, superseded, retired or rejected |
| Effective from/to | In-world validity interval; no silent time edits |
| Provenance | Creator/source, reason, authority and event/reference |
| Prior/successor link | Explicit name history; never destructive replacement |
| Locale/script | Language/script metadata where relevant |
| Pronunciation | Optional human-readable pronunciation aid |
| Search tokens | Derived, non-authoritative search aids |

The registry must maintain a unique reservation for each canonical normalized name key, with only the exact two-entity Saltwater sovereign/city exception in §3.2. Registered aliases and alternate names must also be collision-checked and resolvable without ambiguity; the exception does not apply to aliases. Historical forms remain searchable as historical references but cannot be claimed by another entity.

A name record must never be detached from its history or reassigned to a new entity.

## 5. Normalization and collision prevention

The registry must calculate comparison keys deterministically. At minimum:

1. Unicode-normalize text using one documented canonical normalization form.
2. Apply locale-independent case folding.
3. Trim leading/trailing whitespace and collapse repeated internal whitespace.
4. Standardize typographic apostrophes, quotation marks, hyphens and dash variants for comparison.
5. Normalize equivalent punctuation and spacing without changing the authoritative display spelling.
6. Normalize approved diacritic/transliteration search variants for collision review; do not erase culturally meaningful spelling from the display name.
7. Standardize common road suffix and abbreviation variants for road-name comparison (for example, “Road” and “Rd”) while retaining the full official form.
8. Reject empty, whitespace-only, control-character, malformed or prohibited names.
9. Keep the original approved display form and the normalized comparison form separately.

The comparison key is not the display name. Normalization must not silently rewrite the user's or canon's approved spelling.

### 5.1 Collision classes

- **Exact normalized collision:** hard reject.
- **Case, spacing, punctuation or abbreviation collision:** hard reject.
- **Equivalent Unicode or diacritic collision:** hard reject or block pending authoritative review where the equivalence is uncertain.
- **Near-duplicate or confusable spelling:** hold for review; do not auto-accept.
- **Similar pronunciation/transliteration:** hold for review where likely to confuse speech, dispatch, search or records.
- **Same name in a different entity type:** hard reject under the shared canonical namespace, except the exact sovereign-territory/playable-city pair defined in §3.2.
- **Same historical name proposed for another entity:** hard reject.
- **Alias colliding with another active canonical name or alias:** reject or require a different unambiguous form.
- **Legitimate component reuse:** allowed only where the component is not itself registered as a complete entity name or conflicting standalone alias.

Near-duplicate detection is a safeguard, not a claim that all linguistically similar names are identical. The system must preserve human review and provenance for exceptions.

## 6. Reservations, creation and concurrency

A proposed name follows this controlled lifecycle:

PROPOSED → NORMALIZED → COLLISION_CHECKED → RESERVED → ENTITY_CREATED → ACTIVE

A proposal may instead be rejected, held for review or released before entity creation under a recorded reason. Once bound to a created entity, the name reservation is permanent.

Required controls:
- Reservation and entity creation occur in one transaction or equivalent atomic operation.
- Unique constraints protect normalized canonical keys at the authoritative persistence layer.
- Concurrent requests serialize or fail safely; a check-then-insert race is not acceptable.
- Failed creation rolls back both entity and reservation unless an explicit audit policy records a short-lived reservation.
- Idempotency keys prevent retries from creating duplicate entities or consuming multiple names.
- Imports and bulk generation use the same reservation path as interactive creation.
- No division may bypass registry checks with direct inserts, alternate APIs, scripts or manual seed files.
- Name reservations are auditable and attributable to an actor/process, source, time and reason.

## 7. Naming quality and generation strategy

Uniqueness is necessary but not sufficient. Saltwater names must sound like a coherent, lived-in fictional city rather than a mechanically generated catalogue.

### 7.1 Roads, streets and public places
Use varied, locally coherent naming vocabularies and forms, such as:
- Traditional and heritage: Ashbourne Road, Foundry Street, Old Mill Lane.
- Landscape and vegetation: Willowbank Crescent, Ridgeway Drive, Hawthorn Close.
- Residential: Bellview Crescent, Rosewood Walk, Garden Mews.
- Commercial and civic: Exchange Avenue, Market Square, Assembly Way.
- Maritime and coastal: Breakwater Road, Seafarers Way, Harbour View.
- Industrial and transport: Forge Road, Rail Yard Way, Dockworkers Avenue.

These are examples only, not permission to add them to canon automatically. Names must be checked against existing canon and the shared registry. Avoid repetitive suffix-swapping, tiny spelling changes, excessive reuse of one root word and names that misrepresent the location.

### 7.2 People
Use curated, varied name-component pools and culturally/plausibly coherent combinations appropriate to Saltwater's fictional population. Vary first, middle and family names; avoid a small repeated pool, predictable cycling and visibly synthetic sequences. Generate a complete candidate, check it against active and historical records, then reserve it. If a collision occurs, regenerate the full name using a different plausible combination. Do not expose internal generator patterns as public names.

### 7.3 Buildings, businesses and organisations
Names should reflect purpose, location, history, ownership or brand identity without copying an existing name. Avoid placeholder names such as “Shop 001” or “Building 245” as public-facing names. Numbered plot/address identifiers are permitted as structured locators, not substitutes for distinct entity names.

### 7.4 Police and operational labels
Use distinct, pronounceable names and call signs suitable for radio and written records. Active call signs, radio channels, unit labels and operational identifiers must be unique within their operational namespace and time window; where the label is also a canonical entity name, it must additionally pass the global namespace check. Avoid phonetic confusion and ambiguous near-homophones.

### 7.5 Generation determinism and quality
Bulk generation must be reproducible from a recorded generator version/configuration and seed where appropriate, but must not depend on unstable ordering or hidden mutable pools. A deterministic generator must still check the live registry at reservation time. Store the generator/version/provenance needed to explain a generated name; do not store repeated copies of large source vocabularies on every entity.

## 8. Renames, aliases and historical names

- A rename is an append-only event with old name ID, new name ID, entity ID, reason, actor/authority, effective time and provenance.
- The entity ID does not change when its name changes.
- Former names remain reserved to the same entity permanently.
- Aliases and nicknames are separate name forms, never silent replacements for the canonical name.
- An alias may be added, corrected or retired only through a recorded action.
- An alias must not cause ambiguous resolution. If an entity's preferred name is ambiguous, it must receive a distinct registered preferred display form.
- Mergers, splits, subdivisions, amalgamations, renumbering and successor entities preserve predecessor/successor links; names are not silently transferred.
- Deceased people, closed businesses, demolished buildings and retired roads retain historical identity and name history.
- Corrections must not erase the original value or the reason for correction.

## 9. Existing canon and initial registry import

Before new generation, the registry must reserve all existing adopted names and identifiers. At minimum this includes:
- Saltwater, the single city-state and city identity;
- all eight adopted district names;
- all 24 adopted neighbourhood names;
- all 42 named roads in SW-GEO-V1, including named bridges;
- existing landmark, feature, route, institution, workspace, command and other canonical names already committed to the repository;
- every subsequently adopted person, property, business and operational name.

Existing names are grandfathered as canon, not silently renamed to satisfy a newly built registry. If an existing conflict is discovered, record it as a controlled conflict for explicit resolution; do not silently overwrite either entity. The SW-GEO-V1 source dataset remains versioned and must be imported into the registry by stable IDs, not copied into a competing geography authority.

## 10. Domain ownership across the 44 divisions

The shared standard is mandatory across all divisions. Detailed vocabulary and entity lifecycle remain with domain owners:

- **BP-01:** global naming policy, authority, conflict hierarchy and mandatory compliance.
- **BP-02:** geography, roads, areas, landmarks, parcels, addresses and spatial labels.
- **BP-03:** person identity and person-name lifecycle; person ID remains distinct from name.
- **BP-04:** properties, buildings, premises, businesses, organisations and trading names.
- **BP-05–BP-09, BP-30–BP-34:** police organisations, units, personnel-facing labels, facilities, assets, HR and financial entities.
- **BP-10–BP-12, BP-15–BP-29:** operational, incident, case, investigative, legal, custody, evidence and forensic entities.
- **BP-35–BP-37:** runtime generation, event ordering, effective time and schedule-aware reservation behaviour.
- **BP-38:** authoritative registry schema, constraints, indexes, provenance and data ownership.
- **BP-39:** persistence, backup, restore and name-history continuity.
- **BP-40–BP-42:** user-facing lookup, safe display, access control and protected name forms.
- **BP-43:** duplicate, near-duplicate, concurrency, history, import and regression tests.
- **BP-44:** controlled naming vocabulary/configuration changes and version governance.

BP-13, BP-14 and every other division not individually named above remain bound by the universal rule. The list assigns primary responsibilities; it does not create exemptions.

## 11. Required acceptance tests

The implementation must eventually prove, with reproducible automated evidence:

1. Exact duplicate canonical name is rejected.
2. Case-only, whitespace-only and punctuation-only variants are rejected.
3. Unicode-equivalent and configured abbreviation variants are detected.
4. Near-duplicate/confusable candidates are held for review.
5. Cross-entity-type duplicate names are rejected.
6. Active and historical canonical names cannot be recycled.
7. Alias collisions and ambiguous search results are prevented.
8. Two people cannot receive the same complete canonical name.
9. Person identity remains stable across rename, alias and lifecycle changes.
10. Two simultaneous reservations for one normalized key cannot both succeed.
11. Retry/idempotency cannot create duplicate entities or reservations.
12. Failed entity creation leaves no orphan reservation or partial entity.
13. Bulk imports and generated populations use the same checks.
14. Existing adopted geography names and stable IDs import without alteration.
15. Renames preserve former names, actor, reason and effective time.
16. Merges, splits and retirement preserve history and references.
17. Every one of the 44 divisions is checked for compliance and cannot bypass the shared service.
18. Search resolves a unique entity or explicitly reports ambiguity; it never guesses.
19. The registry can be backed up and restored without losing uniqueness or historical reservations.
20. Tests do not advance the simulation clock or mutate production records.

A passing test suite is required before claiming the registry is implemented. This specification alone does not prove implementation.

## 12. Change control and non-assumptions

- This standard is core and mandatory. It may not be weakened by a domain-specific specification.
- New naming categories and vocabulary may be added through controlled BP-44 configuration without changing the fixed BP-01–BP-44 division structure.
- Any proposed exception to global uniqueness requires explicit user approval and a versioned decision. Convenience, generator collision or legacy implementation is not an exception.
- Existing canon names are preserved unless explicitly amended by the user.
- Do not invent a real-world postal authority, language law or naming regulator; Saltwater is fictional.
- Do not make a database migration, production seed, import, bulk write or Neon upload under this design approval. Production changes remain subject to the separate storage measurement and explicit approval gate.

## 13. Completion state

**Policy:** ADOPTED — core foundational requirement.  
**Specification:** recorded in this document.  
**Registry implementation:** NOT_STARTED / NOT VERIFIED by this document.  
**Automated acceptance tests:** NOT_STARTED / NOT VERIFIED by this document.  
**Neon production changes:** none authorised or performed.
