# BP04 full acceptance audit — 2026-11-25

**Result: NOT PASSED — BP04 is partially implemented and must not be marked COMPLETED.**

**Audit source:** `main` at commit `881b9531aa609811bef5eb7fd306a4bc6be11145`  
**Production release:** [GitHub Actions run 45675735246](https://github.com/Joshuaogri/saltwater/actions/runs/45675735246) — completed successfully  
**Latest disposable archive-only validation:** [run 45672436619](https://github.com/Joshuaogri/saltwater/actions/runs/45672436619) — completed successfully  
**Neon target:** project `misty-breeze-20463094`, production branch `br-still-cloud-bdvaw8u4`, database `neondb`.

This audit distinguishes successful delivery of the compressed BP04 source package from completion of every BP04 division acceptance criterion. The production deployment is successful; the complete division acceptance is not.

## 1. Verified production deployment

A read-only query against Neon on 2026-11-25 verified:

| Measure | Verified value |
|---|---:|
| BP04 production migrations | 0003–0012 (10 versions) |
| BP04 base tables | 92 |
| Archived source datasets | 14 |
| Source collections | 105 |
| Source records represented | 1,950,923 |
| Compressed source bytes | 29,434,820 (29.43 MB) |
| Uncompressed source bytes | 558,602,287 (558.60 MB) |
| Dataset ledger rows | 14 |
| Collection ledger rows | 105 |
| Dataset/collection mappings in archive-only state | 14 / 105 |
| Permanently materialised typed source rows | 0 |
| Current `pg_database_size` | 41,525,248 bytes (41.53 MB) |
| Pre-BP04 baseline | 9,306,112 bytes (9.31 MB) |
| Measured production growth | 32,219,136 bytes (32.22 MB) |

The production workflow passed both jobs and every deployment step: target/commit/package-digest verification, ordered migrations, archive-only import, production acceptance, repeat-import idempotency/storage stability and final measurements. The 14 original compressed archives are retained once. The zero typed-row count is intentional under the selected archive-only storage design.

The archive-only disposable workflow also passed on PostgreSQL 16 and 18. Its acceptance verifies 14 datasets, 105 collections, source counts, archive byte accounting, archive-only mapping states, zero typed rows and repeat-import stability.

## 2. Source-world coverage verified in GitHub

The committed property-world source and its generator tests cover a canonical fictional estate baseline of:

- 420 property sites and 420 generated address records;
- 1,474 buildings;
- 27,730 premises;
- 180,733 units;
- 110,920 named rooms;
- 2,984 access points and 2,984 access routes.

The source ledgers also account for:

- 10,000 business identities;
- 10,000 establishments;
- 10,000 business-to-unit links;
- 10,000 weekly business profiles;
- 70,000 daily operating schedules;
- 811 organisation records in the tenure source;
- ownership, management, occupancy, agreements, utilities, maintenance, security, valuation, lawful-use, lifecycle, title, rights, insurance and facilities-operation collections.

The property-world generator regression verifies unique IDs within entity types, property/building/premises/unit parent relationships, address references, ownership references, access-point/route matching, campus buildings and no person creation. These are meaningful source-generation checks, but they do not prove that every BP04 cross-register acceptance criterion is operationally available through the game.

## 3. Acceptance matrix

| Acceptance group | Result | Audit finding |
|---|---|---|
| A — business registry | PARTIAL | The 10,000-business, 10,000-establishment and operating-schedule source collections exist. The deployed archive acceptance verifies source counts, not the complete AC-A01–A07 identity-quality, duplicate, branch-count and population-interface invariants. |
| B — property and premises | PARTIAL / BLOCKED | The generator tests verify the source hierarchy and generated address/access relationships. BP04 addresses are not yet demonstrated as fully bound to BP-02's authoritative parcel/address identity and operational spatial references. The production source is archived, not query-indexed into the property tables. |
| C — ownership, tenancy and occupancy | PARTIAL | The source archives include ownership, management, 12,500 agreements and 10,000 occupancies. Production archive acceptance does not execute the full temporal, party-role, dispute, subletting and continuity checks in AC-C01–C07. |
| D — organisations and facilities | PARTIAL | Organisation and facility-related source collections exist. Full service-level acceptance for healthcare capability and public transport operator/route/timetable integration (AC-D06/D07) is not evidenced as a tested, playable interface. |
| E — staff, stock, supply and events | PARTIAL | Business profiles and schedules are present. The complete person/employment interfaces, stock reconciliation, causal disruption events and transactional rollback requirements in AC-E01–E07 are not verified end to end. |
| F — police, evidence and information boundaries | PARTIAL / BLOCKED | A separate officer-only BP04 adapter now checks the required principal kind, live grants and durable audit. It is default-deny until approved policy grants are provisioned, and it is not yet called by dispatch/incident/investigation services. BP-42/BP-23 remain required cross-division interfaces. |
| G — quality, scale and storage | PARTIAL | Archive integrity, source counts, storage measurement and repeat-import stability pass. The 10,000-business query-performance budget, complete duplicate/reconciliation suite, representative lookup benchmarks and full criterion-to-test traceability are not yet demonstrated. |

## 4. Concrete blockers to full acceptance

1. **Canonical BP-02 parcel/address identities:** the read-only reconciliation in [run 45680995361](https://github.com/Joshuaogri/saltwater/actions/runs/45680995361) matched all 420 property-to-generated-candidate-parcel links, 420 property-to-address links, and 420 each of district, neighbourhood and road references to BP-02 `entity_code` values. It also confirmed that the current BP-02 identity map contains zero parcel and zero address identities. The 420 parcels remain unapproved candidates and the 420 BP04 addresses remain source-world labels. BP-02 must supply canonical parcel/address identities before BP04 can bind or promote them.
2. **Gameplay lookup integration:** the bounded property/address/building/premises/unit/access-point/business/establishment API is implemented in `runtime/bp04_lookup.py`. The player interface now supports `find` and `inspect`; PKG-005 lazily loads the lookup only after the command gateway authorizes the action; PKG-006/007 host and ChatGPT contracts accept bounded lookup commands. See [lookup design](../BP04-gameplay-lookup.md) and [integration record](../BP04-player-police-geography-integration.md).
3. **Police access integration:** `runtime/bp04_police_access.py` provides an officer-only adapter and a PostgreSQL composition factory using live grants and durable append-only audit. It denies non-officers and denies all ungranted requests. Approved `player.command.find/inspect` and `bp04.lookup.*` grants have not been provisioned in production; no Neon policy rows were changed. Dispatch, incident and investigation services still need to call this adapter.
4. **Cross-register acceptance:** test uniqueness, parent/child references, temporal relationships, business-versus-establishment identity, 10,000-business quality, organisation/facility links and all 105 collection counts from the pinned source release.
5. **Operational interfaces and regression:** verify the applicable healthcare, transport, utility, business-schedule, lifecycle and disruption interfaces; add representative lookup-performance, failure/rollback and recovery tests.

### BP-02 identity-layer update — 2026-11-25

The source-only `runtime/bp02_parcel_address_identity.py` now assigns stable portable design IDs to every BP04 parcel candidate and primary address:

| Measure | Result |
|---|---:|
| Stable parcel design identities | 420 |
| Stable address design identities | 420 |
| Property-to-parcel design identity links | 420/420 |
| Property-to-primary-address links | 420/420 |
| Address-to-parcel design identity links | 420/420 |
| Operationally approved parcel identities | 0 |
| Operationally approved canonical address identities | 0 |
| Neon writes / seed rows | 0 |

Parcel IDs are deterministic SHA-256-derived `SWP-` identifiers; address IDs are deterministic SHA-256-derived `SWA-` identifiers. The register preserves candidate geometry and source address attributes, records lineage, rejects broken/duplicate links and does not invent missing numbers, entrances or frontage. It does not promote candidate polygons or addresses into an operational cadastral/address authority.

The updated BP04-to-BP02 reconciliation therefore distinguishes design identity coverage (420/420) from operational canonical release (still blocked). The source geography is still marked not approved for operational seed. This is a genuine source identity layer, not a Neon upload.

The real-source frontage reconciliation further checked address road references against the road owning each parcel candidate's shared-boundary frontage segments. It found 415 direct matches, three source-road conflicts and two parcels without a frontage-road candidate. The three conflicts and two no-frontage cases are enumerated in the integration record. A single geometric frontage road exists for 88/420 parcels and multiple frontage roads for 330/420. In all 330 multi-road cases, the source road is itself a member of the frontage candidate set and disambiguates the candidate without arbitrary selection. Of the 88 single-road cases, 85 source roads match and three have a single alternative road proposed for review. Two addresses have no frontage candidate. Candidate road references are therefore resolved for 418/420 addresses, but none is promoted to an operational address road without review. The expanded integration passed 108 tests on `main` in [run 45686302214](https://github.com/Joshuaogri/saltwater/actions/runs/45686302214).

## 5. Final decision

**BP04 production archive release: COMPLETED and VERIFIED.**  
**Player command lookup integration: IMPLEMENTED AND TESTED.**  
**Officer lookup adapter: IMPLEMENTED; production access remains default-deny pending policy grants and police-service integration.**  
**BP04-to-BP02 design identity binding: 420/420 parcels and 420/420 addresses; operational canonical geography release: BLOCKED.**  
**BP04 full division acceptance: NOT COMPLETED.**

Do not mark the entire BP04 division `COMPLETED` yet. The next geography prerequisite is operational release of the BP-02 parcel/address design identity layer: review candidate geometries, prove frontage/address placement, confirm address scope/aliases and version lineage, then approve the geography version. Separately, provision approved access grants, wire the officer adapter into police operational services, and complete remaining cross-register acceptance. These tasks remain on GitHub `main`; no further Neon write is required for the source reconciliation or player lookup implementation.

No Neon writes were made during this audit.
