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

## BP-02 address placement review register — 2026-11-25

Added `runtime/bp02_address_review_register.py` and its dedicated regression suite. The BP04-to-BP02 reconciliation now emits one deterministic review row per source address, joining SWA/SWP design identities, unchanged source road references, parcel-frontage candidate roads and building-access candidate roads. The completed review queue contains 5 P1 records (3 frontage-road conflicts and 2 missing-frontage cases), 33 P2 records (no-building observations not already classified P1) and 382 P3 source-context-coherent candidates. There are 36 sites without generated building candidates in total, including the three P1 conflicts.

The two addresses without parcel-boundary frontage have matching building-access road-reserve proximity candidates (`SWR-B2` and `SWR-B1`), both `POINT_CONTACT_ONLY`; this is not proof of constructed or legal access. The three road conflicts are on sites with no generated buildings; their alternative frontage candidates remain `SWR-H17` (two) and `SWR-H01` (one). Of the 384 property sites with building candidates, all 384 source roads match their building-access candidate sets; 1,474 building candidates and 2,948 boundary access candidates are included, with zero unresolved building-to-road candidate links.

No source address or road is rewritten, no operational address/access point is approved, and no Neon write occurs. The complete dedicated BP04 integration and source reconciliation passed 120 tests in [run 45688271976](https://github.com/Joshuaogri/saltwater/actions/runs/45688271976). See [BP-02 address placement review register](../BP02-address-placement-review-register.md).

## BP-02 frontage exception resolution and consolidated acceptance audit — 2026-11-25

Added a geometry-based disposition for all five P1 exceptions. Three have unique parcel-frontage candidates (two `SWR-H17` North Coast Road, one `SWR-H01` South Coast Road), but the affected property sites have no candidate buildings, so the source address road is preserved and no address correction is promoted. Two have only point-contact proximity to bridge reserves (`SWR-B2` Customs Bridge and `SWR-B1` Harbour Bridge); bridge point contact is explicitly not treated as street frontage. Implementation: `runtime/bp02_address_frontage_exception_resolution.py`.

Added `runtime/bp02_full_acceptance_audit.py` to combine the SW-GEO-V1 geometry audit, 420 parcel-dossier geometry audit, building-boundary access-point audit, connector topology, direct connector feasibility, route-corridor candidate checks, and all 420 BP04 property/address reconciliation records. It reports structural integrity separately from operational release. The dedicated CI audit was started in [run 45689194753](https://github.com/Joshuaogri/saltwater/actions/runs/45689194753); its complete result is pending at the time of this audit entry.

All five exception records remain non-operational. No canonical address correction, operational access-point approval, Neon write or property archive upload occurred. BP-02 and BP04 are not declared complete.

## BP-02 consolidated audit result and connector remediation — 2026-11-25

The first complete consolidated audit completed in [run 45690177004](https://github.com/Joshuaogri/saltwater/actions/runs/45690177004) and failed structural acceptance on one genuine geometry check: 26 of 2,948 route-centreline candidates intersected other generated building footprints. All 11 address-review and five-exception unit tests passed. The building-boundary access candidate layer passed after its count assertions were reconciled to the expanded estate inventory (1,474 buildings and 2,948 access candidates). Other route checks passed: valid geometry, parent-property containment, no origin-building interior crossing, no mapped-water intersection and no road-reserve overlap.

The 26 intersections were not waived. `runtime/physical_asset_inventory_generator.py` now performs a final geometry reconciliation after every building footprint has been generated. For each connector, it retains the existing boundary access-point location, evaluates the parcel's frontage candidates, and selects the shortest deterministic line that remains within the parent property and avoids all other building footprints. If none qualifies, the original candidate is retained for the independent audit to flag; no unsupported route is invented.

The route-corridor regression now expects the full 2,948 connector set (2,944 frontage candidates and four point-contact/proximity candidates). The full BP-02 workflow also runs the building-access and route-corridor regression suites. The new consolidated run is [45691636832](https://github.com/Joshuaogri/saltwater/actions/runs/45691636832); its result must be checked before structural acceptance is claimed.

This remediation changes generated design candidates only. It does not create operational routes, addresses or access points. The five P1 address/frontage exceptions remain dispositioned but unresolved for operational purposes; no canonical address or operational access-point approval has been made. No Neon writes or property archive uploads occurred.


## BP04 closure reassessment — 2026-11-26

**Current decision: NOT COMPLETED.** The production archive release remains verified as recorded above. The latest work advances player command integration and the authenticated handover boundary, but it does not remove the separately owned operational release blockers.

### New verified implementation

- Real archive-backed player command tests now exercise find for property, address and business and inspect for all eight supported entity types. They also check missing/malformed records and prove lookup does not advance the world tick. The PostgreSQL 16/18 workflow has passed the player command, ChatGPT contract, officer authorization and BP04/BP02 lookup/reconciliation contract steps; the full workflow is still running its 420-address BP02 reconciliation at the time of this reassessment: [run 45825332438](https://github.com/Joshuaogri/saltwater/actions/runs/45825332438).
- AuthorizationDecision.active_person_id is now propagated from the verified session. The BP12 handover path requires a trusted personnel-reference verifier to match prepared_by_ref to that verified person before it reads the owner snapshots or calls the writer. Missing active-person identity, absent verifier or mismatched reference is denied. Regression cases cover a matching reference, mismatched caller-supplied reference and missing active person. The targeted officer-authorization workflow step passed.
- The migration-validation workflow passed on the latest tested code commit: [run 45825332455](https://github.com/Joshuaogri/saltwater/actions/runs/45825332455).
- The Python-kernel job in the full PKG-001 regression workflow passed. Its disposable PostgreSQL job was still exercising the 9,999-person population fill at the time of this reassessment: [run 45825332524](https://github.com/Joshuaogri/saltwater/actions/runs/45825332524).

### Updated criterion-to-evidence matrix

| Criterion | Status | Evidence / remaining condition |
|---|---|---|
| Compressed source deployment, digest, counts, archive-only storage and idempotent repeat import | PASS | Production archive deployment and prior PostgreSQL 16/18 archive acceptance recorded above |
| Frozen property-world source inventory and generated hierarchy | PASS for source generation | Existing generator and source-ledger tests; no further inventory expansion is authorised or needed for closure |
| Player find/inspect against actual imported archives | PASS for targeted test steps; full run pending | Run 45825332438 has passed command and lookup steps; complete 420-address reconciliation still running |
| Officer authorization, default-deny and durable audit boundary | PASS for tested adapter contract | Targeted officer authorization step passed; production grants remain unprovisioned |
| Verified officer identity in command handover | PASS for fail-closed contract tests; production integration BLOCKED | Session person identity is propagated and mismatch/missing-identity tests are present. Actual personnel-reference resolver is still an injected dependency and is not wired to the production personnel service |
| BP02 canonical parcel/address operational release | BLOCKED | 420/420 design identities are not operationally approved; five priority frontage exceptions remain unresolved for operational use |
| Production officer grants / BP42 policy | BLOCKED | No approved grants provisioned; default-deny remains correct |
| Full dispatch/CAD and investigation service consumers | NOT IMPLEMENTED / owner dependency | BP04 adapters and handoff contracts exist; they do not constitute complete BP11 or BP16 applications |
| Business schedule, healthcare, transport and utility operational interfaces | NOT VERIFIED / owner dependencies | Source archives exist; no claim of complete service-level consumer integration |
| Cross-register, representative performance, failure/rollback/recovery consolidated acceptance | NOT PASSED | Earlier archive/source tests pass, but the full BP04 criterion-to-test suite has not been executed and accepted as one release gate |

### Closure boundary

The following are completed deliverables: production compressed archive deployment; frozen source-world inventory; bounded archive-backed lookup implementation; player find/inspect integration tests; and a fail-closed officer-attribution contract for BP12 handover.

The following are not silently waived: BP02 operational geography approval; five frontage/access exceptions; production BP42 officer grants; wiring the trusted personnel-reference resolver to the authoritative BP06 personnel service; BP11/BP16 operational consumers; applicable business/healthcare/transport/utility consumers; and consolidated cross-register/performance/recovery acceptance.

No production Neon writes, permission grants, operational geography promotions or data promotions were made by this work. Do not mark BP04 COMPLETED until required BP04-owned criteria pass and external dependencies are either completed or explicitly accepted by the user.


### Final CI results for the 2026-11-26 closure reassessment

The three workflows referenced above have now completed successfully against code commit 57fef4ab24b3e9f6767b204fa15eec60fdb8153a:

- [BP04 player and police lookup integration with BP02 geography — run 45825332438](https://github.com/Joshuaogri/saltwater/actions/runs/45825332438): passed, 12/12 steps. This includes the complete 420-address BP02 reconciliation, not merely the earlier player and authorization steps.
- [PKG-001 disposable PostgreSQL validation — run 45825332524](https://github.com/Joshuaogri/saltwater/actions/runs/45825332524): both jobs passed; 31 disposable-PostgreSQL steps and 25 Python-kernel steps.
- [Database migration validation — run 45825332455](https://github.com/Joshuaogri/saltwater/actions/runs/45825332455): passed, 21/21 steps.

This closes the outstanding CI execution for the current player integration, identity-boundary tests, BP02 structural reconciliation and regression baseline. It does not approve the five BP02 frontage exceptions, provision production BP42 grants, wire a production personnel-reference resolver, implement missing BP11/BP16 or other owner-service consumers, or substitute for the consolidated BP04 cross-register/performance/recovery acceptance. Therefore the BP04 division decision remains NOT COMPLETED.
