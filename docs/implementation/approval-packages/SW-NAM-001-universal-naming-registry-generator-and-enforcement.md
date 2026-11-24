# SW-NAM-001 — Universal Naming Registry, Generator and Enforcement

**Project:** Saltwater  
**Package:** SW-NAM-001  
**Classification:** CORE FOUNDATIONAL IMPLEMENTATION  
**Status:** PROPOSED — awaiting explicit user approval  
**Prepared:** 2026-11-24  
**Target:** GitHub `main`; disposable PostgreSQL 16 for schema and integration validation  
**Authority:** Adopted policy [SW-UNS-001](../../blueprint/decisions/SW-UNS-001-universal-naming-standard.md)  
**Production Neon write authority:** NONE

---

## 1. Purpose

Implement the already-adopted SW-UNS-001 policy as a real, shared, enforceable naming capability. This package is not a new policy decision and does not reopen the user's adoption of the standard.

The outcome is one central naming registry and service used by every Saltwater domain. It must prevent duplicate or ambiguous names, reserve historical names permanently, generate realistic candidates, preserve existing canon and provide reproducible automated evidence.

The implementation is cross-cutting and mandatory across all 44 blueprint divisions. It does not create a new blueprint division, replace domain-owned entity registries or transfer domain truth to BP-38.

## 2. Existing architecture and constraints inspected

The current repository already contains:
- `sw_geo.entity` and versioned `sw_geo.version.name` in proposal 0002;
- `sw_people.person` with given, middle and family name fields and append-only `sw_people.profile_history`;
- domain-specific identity ownership in BP-02, BP-03 and BP-04;
- PostgreSQL proposal sequence through `0008_bp39_checkpoint_recovery.sql`;
- Python runtime modules under `runtime/` and unittest suites under `tests/pkg001/`;
- a disposable PostgreSQL 16 GitHub Actions workflow.

The registry must integrate with these records rather than invent parallel person, geography or business identities. BP-02 continues to own spatial IDs and geography; BP-03 owns person IDs and person identity; BP-04 owns property/business/organisation IDs and their facts; BP-38 owns shared registry persistence and database integrity; BP-43 owns tests and evidence; BP-44 governs vocabulary/configuration changes.

**Migration numbering:** This package reserves proposal `0009_universal_name_registry.sql`. The proposed SW-DB-001 world-provisioning package must therefore use the next available number (`0010`, subject to a fresh sequence audit) rather than assuming 0009.

## 3. Deliverables

### 3.1 Shared persistent naming registry

Prepare `db/proposals/0009_universal_name_registry.sql` for disposable PostgreSQL only.

The schema candidate must provide:
- permanent name-record identity;
- owning entity type and stable domain entity ID reference;
- canonical, preferred, legal, trading, alias, former and other controlled name forms;
- exact approved display spelling plus deterministic normalized comparison key;
- global canonical-name namespace and collision-safe alias reservation;
- reservation/active/superseded/retired/rejected lifecycle;
- effective-time interval, source, actor/process, reason and provenance;
- immutable append-only rename/history events;
- generator/configuration version and source-manifest provenance where generated;
- unique constraints and transactional reservation protection.

The registry stores naming authority and name history, not a duplicate copy of domain facts. It must not create a second person table, geography authority, business register or substitute primary key.

**Typed identity references:** name rows identify their owner using the domain's existing stable ID plus a controlled entity type. The implementation must validate that the referenced domain entity exists using explicit, whitelisted domain adapters/constraints; it must never build executable SQL from an untrusted entity-type string. If the existing schema cannot safely validate a domain reference, the package must document the precise gap and block that entity type rather than accept an orphan.

### 3.2 Deterministic normalization and collision service

Implement `runtime/naming.py` as a provider-neutral naming service with:
- Unicode NFKC comparison normalization while preserving original display spelling;
- locale-independent case folding;
- leading/trailing trim and internal whitespace collapse;
- standardized comparison treatment for typographic apostrophes, quotes, hyphens/dashes and punctuation;
- configurable abbreviation/suffix rules for road and address forms;
- confusable/near-duplicate candidate scoring, with a review threshold rather than unsafe automatic equivalence;
- explicit canonical-name, alias and operational-namespace collision classes;
- deterministic results independent of row ordering or process locale.

Exact normalized collisions and punctuation/case/spacing variants are rejected. Near-duplicates, likely homophones and transliteration/confusable cases are held for review. Search must return a unique stable entity reference or an explicit ambiguity result; it must never guess.

Normalization is versioned. A future normalization change must be able to detect newly introduced collisions before activation; it must not silently rewrite existing canon.

### 3.3 Reservation and lifecycle service

The service must expose typed operations for:
- propose and validate a name;
- reserve a canonical name;
- commit the reservation with entity creation;
- add a preferred name or alias;
- rename an entity;
- retire a name while retaining its permanent reservation;
- search current and historical names;
- inspect collision/review results.

Reservation plus entity creation must be atomic. Concurrent attempts for the same normalized key must yield exactly one successful reservation. Idempotent retries must return the original outcome without creating a second name or entity. A failed entity creation must not leave an orphan reservation.

No division, import script, bulk generator or NPC/player path may bypass the service. Database uniqueness constraints remain the final authority; application-side pre-checks alone are insufficient.

### 3.4 Domain adapters and mandatory coverage

The first integration slice must cover the existing name-bearing records:
- BP-02 geography: every versioned spatial entity name, including Saltwater roots, districts, neighbourhoods, roads, bridges, landmarks and later spatial types;
- BP-03 people: complete canonical full name composed from the existing name fields; preferred names and aliases as distinct registered forms;
- BP-04 built world: business, organisation, property/building/premises and trading names through the BP-04 adapter when its authoritative entity schema is available;
- shared operational names: unit/vehicle/facility/asset and other adopted named entities through typed adapters.

Existing direct-write paths must be identified. Database triggers or restricted write functions must prevent a record from being created or renamed without the corresponding registry reservation. A table without a safely integrated adapter is explicitly marked NOT CONNECTED and cannot be represented as compliant.

This package does not invent the unresolved BP-04 business/property schema or fabricate business data. It defines and tests the adapter contract, and integrates actual BP-04 tables only where present and authoritative.

### 3.5 Name-generation engine

Implement `runtime/name_generation.py` with domain-specific candidate builders:
- people: varied, plausible complete names using curated/configured given, middle and family-name vocabularies; no repeated mechanical patterns or numeric suffix workarounds;
- roads and public places: varied, coherent roots and forms such as Road, Street, Avenue, Crescent, Close, Lane, Drive, Walk, Mews and Square;
- buildings/properties: distinctive names appropriate to building use and local character;
- businesses/organisations: distinctive names related to activity, location, heritage or brand identity;
- police/operational labels: pronounceable and radio-distinguishable names/call signs, with time-window uniqueness for operational call-sign namespaces.

Generator requirements:
- accept explicit domain vocabulary/configuration rather than hard-code one narrow cultural profile;
- use a recorded generator version and deterministic seed for reproducible batches;
- produce candidates only; every candidate must pass the live registry reservation path;
- regenerate on hard collision using a deterministic, bounded retry strategy;
- send near-duplicate candidates to review;
- never use arbitrary numeric suffixes as the default collision workaround;
- record generator version, configuration version, seed/manifest reference and outcome without duplicating large vocabulary data on every entity;
- never create real-world personal data; all game population output is fictional.

The engine must support both a one-off entity and a large deterministic batch without weakening uniqueness.

### 3.6 Canon registration and migration of existing names

Before any new population, geography or business name generation, import existing adopted names into the registry using their stable existing IDs.

At minimum, preserve and register:
- the Saltwater sovereign/city roots;
- all eight adopted districts;
- all 24 adopted neighbourhoods;
- all 42 named SW-GEO-V1 roads, including named bridges;
- existing SW-GEO-V1 landmarks, routes and named spatial features;
- existing player/workspace/command names and any other already-adopted canonical entity names discovered by a controlled repository inventory.

The import must be deterministic, repeatable and report every accepted name, pre-existing collision, skipped record and unresolved owner reference. It must not silently rename or overwrite canon. A collision discovered among existing canon becomes a recorded conflict requiring explicit resolution; it is not “fixed” by choosing one name to discard.

The initial inventory must distinguish true entity names from descriptive labels, schema identifiers, example names and UI copy. Do not indiscriminately reserve every word appearing in documentation.

### 3.7 Automated tests and CI

Add focused tests under `tests/pkg001/` and a dedicated disposable PostgreSQL validation workflow or a carefully scoped extension to the existing disposable workflow.

Required tests:
1. Exact duplicate canonical name rejected.
2. Cross-entity-type duplicate canonical name rejected.
3. Case, whitespace, punctuation, dash and configured abbreviation variants rejected.
4. Unicode normalization is deterministic and display spelling remains unchanged.
5. Near-duplicate/confusable candidates are held for review.
6. Historical and retired canonical names cannot be recycled.
7. Alias collision with canonical or alias names is rejected.
8. Two people cannot have the same complete canonical name.
9. Person ID remains unchanged across rename and alias changes.
10. Concurrent same-name reservation yields one winner only.
11. Concurrent different-name reservations both succeed.
12. Idempotent retry creates no duplicate reservation or entity.
13. Failed entity creation rolls back the reservation.
14. Direct domain insert/update cannot bypass the registry.
15. Existing canon import is repeatable and preserves stable IDs and display names.
16. Unresolved entity type or orphan entity reference is rejected.
17. Generator output is deterministic for the same version/configuration/seed.
18. Generator handles a large candidate batch without duplicates or numeric-suffix dependence.
19. Search resolves by stable ID and reports ambiguity instead of guessing.
20. Rename, retirement, correction and history remain append-only and attributable.
21. Registry backup/restore preserves current and historical reservations.
22. Tests do not advance the fictional clock, mutate production data or reveal hidden simulation truth.

CI must apply the foundation plus proposals 0002–0009 to a fresh disposable PostgreSQL 16 service, run the registry SQL acceptance suite and Python tests, and report storage measurements. No workflow may connect to Neon or require Neon secrets.

### 3.8 Storage and performance report

Measure raw bytes before and after:
- disposable database baseline;
- registry schema and indexes;
- canon-name import;
- representative synthetic person/geography/business names;
- rename and alias history;
- repeated idempotent import.

Report database, table, index and TOAST bytes; bytes per current name and per history event; import throughput; exact lookup and normalized lookup latency; collision-check cost; concurrent reservation outcome; and uncertainty. Distinguish submitted fixture size from actual PostgreSQL growth. Avoid redundant indexes and repeated vocabulary copies.

This package does not approve any production capacity assumption. No Neon write is part of this work.

## 4. Acceptance gates

The package is complete only when all of the following are evidenced:
- the SQL registry schema applies cleanly to disposable PostgreSQL 16 after proposals 0002–0008;
- existing geography and person name writes are enforced through the registry;
- domain ownership and stable IDs are preserved;
- all 22 required test groups pass with attached execution evidence;
- deterministic canon import registers all in-scope current names and reports every conflict;
- generator produces varied, reproducible candidates and cannot bypass reservations;
- concurrent uniqueness is enforced by PostgreSQL, not only Python;
- storage/performance report records raw before/after measurements;
- full existing Python and disposable PostgreSQL regression suites pass;
- backup/restore preserves registry and name history;
- no simulation time advances and no hidden truth is exposed;
- code, SQL, tests, evidence and documentation are committed on `main`.

A green CI run proves only the tested disposable scope. It does not prove all 44 domain adapters are implemented if a domain schema is not yet available. Each unconnected entity type must remain explicitly listed as NOT CONNECTED.

## 5. Explicit exclusions and safety boundaries

- No Neon production migration, schema change, seed, import, bulk write, upload, credential change or production connection test.
- No production person, road, building, business or organisation name import.
- No automatic rewrite of adopted canon names.
- No invention of BP-04 unresolved business distribution or property/address canon.
- No creation of a parallel person, geography or business identity authority.
- No weakening of the global canonical-name namespace to make generation easier.
- No alteration of the fixed BP-01–BP-44 structure.
- No change to hidden-truth rules, player agency, simulation-time pause rules or the 10,000-person cap.
- No public frontend/API deployment or ChatGPT transport integration.
- No claim that every division is integrated until each applicable domain adapter and bypass test is evidenced.

## 6. Approval requested

Approve **SW-NAM-001 — Universal Naming Registry, Generator and Enforcement** for:
- implementation directly on GitHub `main`;
- creation of disposable-only SQL proposal `0009_universal_name_registry.sql`;
- Python normalization, reservation and deterministic generation services;
- existing canon-name inventory/import tooling (dry-run and disposable fixture only);
- BP-02/BP-03 integration and BP-04 adapter contract without inventing missing domain schema;
- automated Python/SQL/concurrency/bypass/restore tests;
- dedicated disposable PostgreSQL CI and measured storage/performance evidence;
- documentation updates to BP-02, BP-03, BP-04, BP-38, BP-43, BP-44, implementation sequence and README.

**Approval does not authorize any Neon production write.** A future exact Neon operation requires its own measured baseline, projected storage, exact operation description and separate explicit user approval.

## 7. Status

**Policy:** ADOPTED — SW-UNS-001.  
**Implementation package:** PROPOSED — awaiting explicit user approval.  
**GitHub branch:** `main` only.  
**Disposable PostgreSQL implementation/tests:** NOT_STARTED.  
**Neon production changes:** none authorised or performed.
