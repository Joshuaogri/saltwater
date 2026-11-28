# BP04 strict acceptance audit — 2026-11-26

**Decision: NOT COMPLETE.** The former sequence-based naming defect has been remediated; AC-A04 is now PARTIAL pending complete global name reservation. This audit supersedes the premature closure wording in `BP04-completion-record-2026-11-26.md`. It evaluates the current BP-04 draft specification's 48 explicit acceptance criteria (AC-A01 through AC-G07) against evidence available on `main`. A successful workflow, source archive deployment or implemented adapter is not treated as proof of an entire criterion unless the test covers the stated requirement.

**Specification authority:** `docs/blueprint/divisions/BP-04-BUILT-WORLD-PROPERTY-BUSINESSES-ORGANISATIONS.md` (still `DESIGNED_DRAFT`; eight open design decisions remain).  
**Status register:** `docs/blueprint/DIVISION-SPECIFICATION-REGISTER.md` records BP04 as IMPLEMENTED / TESTED / BLOCKED.  
**Latest relevant CI:** Business registry build and its 9 regression tests [45840815853](https://github.com/Joshuaogri/saltwater/actions/runs/45840815853) passed; migration validation [45840815670](https://github.com/Joshuaogri/saltwater/actions/runs/45840815670) passed; PKG-001 disposable PostgreSQL [45840815690](https://github.com/Joshuaogri/saltwater/actions/runs/45840815690) passed both Python and PostgreSQL jobs. BP04 integration [45834691417](https://github.com/Joshuaogri/saltwater/actions/runs/45834691417) and earlier PKG-001 [45837315742](https://github.com/Joshuaogri/saltwater/actions/runs/45837315742) passed. These runs validate specific slices, not all 48 BP04 criteria.  
**Production archive:** [45675735246](https://github.com/Joshuaogri/saltwater/actions/runs/45675735246) passed archive-only source deployment. Production storage was measured separately.

## 2026-11-28 subletting/assignment serialization and physical-unit lock order

Migration [0020 — subletting/handover lock ordering](db/migrations/0020_bp04_subletting_handover_serialization.sql) makes subletting creation lock the physical unit before locking superior/sub-agreements, matching the exclusive handover writer's unit-before-agreement order. This prevents a subletting start from racing a physical possession change. The new two-session regression races subletting creation against contractual tenant assignment while both writers wait on the same agreement locks. Exactly one action succeeds: if subletting wins, assignment is rejected while the relationship is active; if assignment wins, the former tenant's subletting permission is expired and the stale subletting request is rejected. The existing superior physical occupancy and operator remain unchanged.

The full [95-table BP04 schema/archive workflow](https://github.com/Joshuaogri/saltwater/actions/runs/46132997130) passed on PostgreSQL 16 and 18, including concurrent handover, exact subletting replay, subletting/assignment interleaving, gameplay lookup, archive-only storage and repeat-import stability. Migration-ledger validation for the source migration set passed in [run 46132917277](https://github.com/Joshuaogri/saltwater/actions/runs/46132917277). No production Neon write occurred.

## 2026-11-28 concurrent subletting idempotency and immutable migration repair

Review of the subletting writer identified a race: two identical requests could both observe no idempotency record before either acquired the superior/sub-agreement locks. Migration 0015 has been restored byte-for-byte to its original committed content. New migration [0019 — subletting idempotency race fix](db/migrations/0019_bp04_subletting_idempotency_race_fix.sql) replaces the writer and rechecks the idempotency key after both agreement rows are locked. Exact concurrent replays now return the original relationship instead of racing on the unique key; conflicting replays remain rejected.

The real two-session test blocks both writers on the same agreement rows, releases them together, and verifies both calls return the same result with exactly one relationship row and one agreement event. The full [95-table BP04 schema/archive workflow](https://github.com/Joshuaogri/saltwater/actions/runs/46132286834) passed on PostgreSQL 16 and 18, including this new race test, existing handover race/idempotency tests, archive-only import, gameplay lookups, and repeat-import storage stability. Migration-ledger validation including migration 0019 passed in [run 46132269015](https://github.com/Joshuaogri/saltwater/actions/runs/46132269015). All tests used disposable PostgreSQL; no production Neon write occurred.

## 2026-11-28 business registry audit hardening

The audit now normalises all three lifecycle classes before comparing embedded summary counts, so a valid zero-count class is retained rather than omitted by `Counter` conversion. Tick/year/summary numeric validation now rejects Python booleans, which otherwise pass `isinstance(value, int)`. Regression coverage includes an all-active registry with zero seasonal and temporarily inactive businesses, boolean tick/count rejection, a second branch establishment, brand/alias anti-inflation, and invalid cross-business primary-establishment references.

The focused [BP04 business registry audit workflow](https://github.com/Joshuaogri/saltwater/actions/runs/46131679025) passed all 21 tests against the 10,000-business archive. The database migration validation workflow also passed on the same source commit in [run 46131679004](https://github.com/Joshuaogri/saltwater/actions/runs/46131679004). A separate full PKG-001 disposable PostgreSQL run [46130013799](https://github.com/Joshuaogri/saltwater/actions/runs/46130013799) completed successfully, including 20,000 persistent business-name reservations and NPC dispatch integration.

AC-A02, AC-A03 and AC-A05 are PASS. AC-A03 now includes record-level validation of every business address and establishment against canonical BP04 property/building/premises/unit/address IDs and BP02 district/neighbourhood IDs, with zero exceptions. AC-A04 remains PARTIAL pending full shared SW-UNS-001 namespace reconciliation. No production Neon write or seed occurred.

## 2026-11-28 agreement lifecycle, title transfer, physical handover and concurrency follow-up

Migrations 0013–0018 provide an append-only agreement-event register, controlled agreement transitions, explicit subletting relationships, contractual-tenant assignment, event-backed property title transfer and explicit physical occupancy handover. The handover writer closes the outgoing occupancy and primary unit link, creates the incoming occupancy and link, preserves legal agreements, and refuses exclusive handover while any other occupant or active subletting relationship remains.

The 95-table BP04 schema/archive workflow passed on PostgreSQL 16 and 18 in [run 46125653046](https://github.com/Joshuaogri/saltwater/actions/runs/46125653046). It includes real two-session race tests: competing handovers serialize with exactly one winner, and concurrent exact replays return the same event/occupancy/link identifiers. A failure-injection test raises after the handover has changed multiple projections but before event persistence, then verifies the entire operation rolls back without partial state. Archive-only import, gameplay lookup and repeat-import storage/idempotency checks also passed. Migration checksum/schema validation and the version-dynamic rollback test passed in [run 46125653012](https://github.com/Joshuaogri/saltwater/actions/runs/46125653012).

AC-C06 and AC-C07 remain PASS; AC-C03 and AC-C04 remain PARTIAL. Title-transfer concurrency, subletting start/end interleavings, full cross-register integration and broader multi-register rollback remain open. Validation used disposable PostgreSQL only; no production Neon migration/write was performed. BP04 remains NOT COMPLETE.


## 2026-11-28 business lookup benchmark and concurrent handover cross-version acceptance

The 95-table disposable schema/archive workflow passed on PostgreSQL 16 and 18 in [run 46130180118](https://github.com/Joshuaogri/saltwater/actions/runs/46130180118). Both versions passed the actual two-session competing physical handover race (one winner, one stale-occupancy loser), concurrent exact idempotent replay (same event/occupancy/link identifiers), and the 10,000-business/1,000-query in-memory gameplay lookup benchmark. PostgreSQL 18 measured p95 0.4410 ms and p99 0.7664 ms; PostgreSQL 16 measured p95 0.4544 ms and p99 0.8602 ms, within the p95 <=10 ms and p99 <=25 ms budgets. Indexed results matched the former linear substring semantics across 100 deterministic sample queries. The PostgreSQL 16 test initially exposed only a test-observation mismatch: a queued row-lock waiter can appear as `idle in transaction`; the test now identifies blocked sessions using lock-wait type and blocking PIDs rather than a version-sensitive activity-state label. No application acceptance was weakened.

These benchmark figures cover the in-memory archive lookup path, not database-backed query latency or write throughput. AC-G03 therefore remains PARTIAL. Assignment/title-transfer concurrency, subletting start/end interleavings, full BP03/BP34/BP35 cross-register integration and broader multi-register rollback remain open. No production Neon write occurred.


## Status meanings

- **PASS** — direct implementation and repeatable test/evidence support the full criterion.
- **PARTIAL** — meaningful implementation exists, but one or more explicit parts of the criterion lack evidence.
- **BLOCKED** — a known prerequisite prevents operational acceptance.
- **NOT VERIFIED** — available evidence does not establish the criterion; this is not a claim that no related code exists.
- **FAIL** — inspected implementation directly contradicts the criterion.

## A. Registry and business minimum

| Criterion | Status | Evidence / gap |
|---|---|---|
| AC-A01 — at least 10,000 distinct valid local businesses | PASS | The current deterministic registry audit and regression test validate 10,000 distinct local fictional business IDs, 10,000 establishments and primary occupancy links, 20,000 normalized-unique public names, required sector/activity/legal-form/size/lifecycle fields, non-numeric names, Saltwater locality, property-address lineage, and zero person records created from business records. The former sequence-suffix defect is corrected. Cross-domain shared-name reservation remains separately tracked under AC-A04; branch/brand/alias anti-inflation is covered by AC-A02. Evidence: `runtime/bp04_business_registry_audit.py`, `tests/pkg001/test_bp04_business_registry_audit.py`, focused 23-test audit workflow [46133779256](https://github.com/Joshuaogri/saltwater/actions/runs/46133779256), and the passing Python regression job. |
| AC-A02 — branches, establishments, brands and aliases not miscounted | PASS | Adversarial tests add a second establishment/branch for one business and prove the 10,000 distinct-business count remains unchanged; brand and alias records are explicitly excluded from business identity totals; a primary establishment belonging to another business is rejected. Evidence: `tests/pkg001/test_bp04_business_registry_audit.py`, focused workflow run [46131679025](https://github.com/Joshuaogri/saltwater/actions/runs/46131679025). |
| AC-A03 — every business has unique ID, plausible identity, sector, local scope, lifecycle status and provenance | PASS | The 10,000-business audit validates identity, required sector/activity/legal-form/size/lifecycle fields, Saltwater locality, generator provenance and lifecycle summary. Its spatial-lineage extension resolves all 10,000 establishments and each business registered address against canonical BP04 property, building, premises, unit and address records plus BP02 district/neighbourhood IDs. Zero exceptions; deliberately unknown addresses fail closed. Evidence: `runtime/bp04_business_registry_audit.py`, `tests/pkg001/test_bp04_business_registry_audit.py`, focused workflow run [46133779256](https://github.com/Joshuaogri/saltwater/actions/runs/46133779256) (23 tests passed). |
| AC-A04 — duplicates, placeholders and off-map entities cannot inflate local minimum | PARTIAL | The sequence-suffix defect has been corrected. The new deterministic generator creates 10,000 normalized-unique trading names from a versioned 30,448-root vocabulary, screens 11,000 candidates, holds four internal near-duplicate candidates for review, checks exact collisions against all 102 adopted SW-GEO-V1 names, rejects numeric placeholders, and places establishments only on Saltwater property-world units. However, names have not yet been persistently reserved against the complete shared SW-UNS-001 namespace or every other adopted canonical name; this remains a required acceptance step. |
| AC-A05 — total registry and active operating counts distinguished | PASS | The audit reconciles active, seasonal and temporarily inactive counts to the 10,000 distinct-business total and the embedded generator summary; zero-count lifecycle classes are handled explicitly and tested. Evidence: `runtime/bp04_business_registry_audit.py`, `tests/pkg001/test_bp04_business_registry_audit.py`, focused workflow run [46131679025](https://github.com/Joshuaogri/saltwater/actions/runs/46131679025). |
| AC-A06 — business records do not create people | PASS | BP04 source generation/import boundary does not create person records; population is separately owned. |
| AC-A07 — staffing and visitors respect the 10,000-person cap | NOT VERIFIED | Global population-cap tests pass in PKG-001, but the BP04 staff/visitor reference interaction is not demonstrated end-to-end. |

## B. Property and premises integrity

| Criterion | Status | Evidence / gap |
|---|---|---|
| AC-B01 — every property links to valid BP02 parcel/address or explicit unresolved state | BLOCKED | 420 design identities reconcile, but operational canonical parcel/address release remains unapproved. The current design-only status is explicit; operational binding is not accepted. |
| AC-B02 — building, premises, unit and access-point parent relationships valid | PASS | Source hierarchy, archive integrity and real-archive lookup tests validate core parent references; Stage E disposable ingestion and backup/restore also passed. |
| AC-B03 — multiple businesses can share a building without identity collision | NOT VERIFIED | No dedicated multi-business/shared-building adversarial acceptance result is linked. |
| AC-B04 — one business can operate multiple establishments without duplicate identity | PARTIAL | Registry hierarchy supports parent business and establishments; full multi-establishment scenario coverage is not evidenced in the consolidated report. |
| AC-B05 — access points have stable IDs, spatial locators and effective-dated status | BLOCKED | 2,948 generated access candidates are design candidates; operational spatial binding, approved entrances and effective-dated operational access state are not released. |
| AC-B06 — historical building/premises changes do not rewrite past event locations | NOT VERIFIED | No end-to-end BP04 property-change / historical incident-location immutability acceptance is linked. |

## C. Ownership, tenancy and occupancy

| Criterion | Status | Evidence / gap |
|---|---|---|
| AC-C01 — owner, manager, landlord, tenant, operator and occupant remain distinct | PARTIAL | Separate source entities and agreement roles exist; a complete adversarial role-separation acceptance matrix is not linked. |
| AC-C02 — multiple, disputed and time-bounded interests supported | NOT VERIFIED | Source registers exist, but no full lifecycle and dispute test report demonstrates all cases. |
| AC-C03 — lease/licence dates, renewals, expiry and termination preserve history | PARTIAL | Migrations 0013–0020 add append-only agreement events, controlled execution/variation/renewal/expiry/termination/surrender transitions, explicit subletting, tenant assignment, title transfer and physical occupancy handover. PostgreSQL 16/18 acceptance covers immutable histories, exact replay, renewal linkage, expiry with continuing occupancy, subletting start/end, assignment, title transfer without tenancy mutation, explicit outgoing/incoming occupancy handover, competing handover writers and failure-injected rollback. Title-transfer concurrency, subletting start/end interleavings, full cross-register integration and historic source reconciliation remain open. Historic execution dates remain unrecorded unless evidenced. |
| AC-C04 — subletting and third-party occupancy require explicit records | PARTIAL | Migration 0015 adds a secondary occupancy relationship requiring a current `subletting` right tied to the superior agreement, superior tenant, property and unit, with a matching sublease and explicit subtenant occupancy. Migration 0018 requires active subletting and other current occupants to be explicitly resolved before exclusive physical handover; migration 0020 serializes subletting creation with the physical unit lock before agreement locks. PostgreSQL 16/18 acceptance verifies missing rights and unsafe handover are rejected, no second primary business-unit link is created, subletting start/end and handover replay are idempotent, concurrent exclusive handovers serialize, and legal relationship end does not silently evict the physical occupant. Concurrent exact subletting creation and subletting-versus-tenant-assignment interleavings now pass real two-session acceptance on PostgreSQL 16/18. Consent-required/revoked rights, broader third-party occupancy types, concurrent end/start interleavings and title-transfer concurrency remain open. |
| AC-C05 — agreement existence, rent payment and physical occupancy are not conflated | NOT VERIFIED | No end-to-end test proves separation across BP04 and BP34 payment/occupancy facts. |
| AC-C06 — expired agreement with continued occupancy is representable | PASS | The disposable PostgreSQL 16/18 transition acceptance expires an agreement while its linked occupancy remains `occupied` with no end year; the agreement projection becomes `expired` and the occupancy projection is unchanged. The generated tenure regression independently protects the same no-automatic-eviction invariant. |
| AC-C07 — property transfer preserves continuing tenancy and prior ownership | PASS | Migration 0017 reuses the append-only property lifecycle event register, updates current ownership/title/interest/right-schedule projections and records a title instrument plus transaction index. PostgreSQL 16/18 acceptance verifies prior/new owner provenance and proves the existing landlord/tenant/operator agreement, physical occupant and primary business-unit link remain unchanged. No BP34 payment is created. |

## D. Organisation and facility operations

| Criterion | Status | Evidence / gap |
|---|---|---|
| AC-D01 — organisation/facility stable identity, type, status, operator and location | PARTIAL | Organisation/business source identities and establishment locations exist; full facility/operator reconciliation is not demonstrated. |
| AC-D02 — public authority is not inferred from organisation record | NOT VERIFIED | No explicit authority-separation test is linked. |
| AC-D03 — service hours, capacity, actual availability and temporary closures distinguished | PARTIAL | 70,000 daily business schedule records exist; evidence does not establish actual availability/closure state and capacity separation for every required provider class. |
| AC-D04 — essential-service operators/dependencies traceable across affected facilities | NOT VERIFIED | No end-to-end dependency disruption propagation test is linked. |
| AC-D05 — off-map organisations cannot create external playable geography/population | NOT VERIFIED | Canon prohibits external playable geography, but a dedicated data-level containment test is not linked. |
| AC-D06 — healthcare service capability/capacity/referral/treatment metadata and alert references | NOT VERIFIED | Source archive availability alone does not prove the required healthcare interface and access-controlled consumer. |
| AC-D07 — public transport routes/stops/geometry/operator/fleet/timetable/capacity/accessibility/disruption | NOT VERIFIED | No integrated BP02/BP04/BP37 transport service acceptance is linked. |

## E. Staff, stock, supply and events

| Criterion | Status | Evidence / gap |
|---|---|---|
| AC-E01 — staff links resolve to BP03 persons and BP33 employment records | NOT VERIFIED | No full BP03/BP33-linked staff reconciliation is evidenced. |
| AC-E02 — staff not duplicated across employer/establishment views | NOT VERIFIED | No cross-register staff deduplication acceptance is linked. |
| AC-E03 — planned schedules are not proof of actual presence/open status | PARTIAL | Schedules are stored separately from simulation time and actual state, but an end-to-end discrepancy test is not linked. |
| AC-E04 — stock movements reconcile where inventory tracking enabled | NOT VERIFIED | No stock ledger reconciliation result is linked. |
| AC-E05 — supplier/service disruptions have causal event references | NOT VERIFIED | No BP35-backed supplier/essential-service disruption acceptance is linked. |
| AC-E06 — material business/property changes preserve actor, reason, source and effective time | NOT VERIFIED | No complete BP04 business/property lifecycle writer and audit test suite is evidenced. |
| AC-E07 — failed multi-record transactions leave no partial authoritative state | PARTIAL | Archive importer transaction/idempotency and BP12 event-backed writer tests exist. The BP04 handover acceptance injects a failure after old occupancy/link updates and new occupancy/link inserts but before event persistence, then verifies all projections roll back with no partial state. Assignment/title-transfer and broader cross-register rollback matrices remain outstanding. |

## F. Police, evidence and information boundaries

| Criterion | Status | Evidence / gap |
|---|---|---|
| AC-F01 — authorised police enquiries retrieve property, occupancy, access, staff, business and service records | PARTIAL | Officer-only property/business/address lookup and incident-location adapters are implemented; occupancy, staff and service record coverage and production grants are incomplete. |
| AC-F02 — access logs distinguish credential/device events from verified human identity | PARTIAL | Verified session person identity and BP06 personnel-reference checks exist for command handover; full access-log event semantics are not evidenced. |
| AC-F03 — business registration/address does not prove operation or historical presence | PARTIAL | Source and design-only address states are explicitly distinguished; no complete historical business-presence inference regression suite is linked. |
| AC-F04 — source documents, claims, estimates, observations and summaries distinguishable | PARTIAL | Source provenance and uncertainty are preserved in selected registers; full BP04-wide epistemic classification acceptance is not evidenced. |
| AC-F05 — evidence custody remains BP23-owned | PASS | BP04 lookup/handoff boundaries do not own or bypass evidence custody; cross-domain tests preserve owner-service boundaries. |
| AC-F06 — restricted keys/codes/layouts/sensitive records not disclosed to unauthorised roles | PARTIAL | Default-deny authorization, audit and fail-closed tests exist; production grants remain absent and complete sensitivity-class coverage is not evidenced. |
| AC-F07 — hidden perpetrator identity never leaks before exact bingo trigger | NOT VERIFIED | No BP04-wide hidden-truth leakage acceptance artifact is linked. |

## G. Quality, scale and storage

| Criterion | Status | Evidence / gap |
|---|---|---|
| AC-G01 — duplicate detection flags candidates without unsafe auto-merges | PARTIAL | Duplicate identity safeguards exist in selected property/geography registers; full business/organisation duplicate review acceptance is not evidenced. |
| AC-G02 — registry reconciliation detects invalid relationships and business-count drift | PARTIAL | Archive import ledgers, core hierarchy validation and counts exist; complete all-register drift report is not linked. |
| AC-G03 — 10,000+ business queries meet measured performance budgets | PARTIAL | The in-memory gameplay lookup now uses a normalized bigram inverted index. The reproducible 10k-business/1k-query benchmark passed on PostgreSQL 16 and 18 in run 46130180118. PostgreSQL 18: p95 0.4410 ms, p99 0.7664 ms, max 0.8505 ms; PostgreSQL 16: p95 0.4544 ms, p99 0.8602 ms, max 1.1616 ms, against p95 <= 10 ms and p99 <= 25 ms budgets. Indexed results matched former linear substring semantics for 100 deterministic samples. Real concurrent handover and idempotent replay also passed on both versions. Database-backed query latency and write throughput remain unmeasured, so full performance acceptance remains partial. |
| AC-G04 — storage benchmark includes shared references, indexes, event history and high-entropy text | PARTIAL | Archive-only storage measured and production growth recorded; the benchmark does not demonstrate all dynamic history/index/event workloads in the criterion. |
| AC-G05 — every acceptance test links to source requirements and reproducible evidence | BLOCKED | This criterion-level matrix is now created, but the complete requirement-to-test mapping and retained evidence links for all 48 criteria are not yet complete. |
| AC-G06 — no Neon write without baseline, estimate and explicit approval | PASS | Production archive release was user-authorised; baseline and measured growth are documented. No new production write is made by this audit. |
| AC-G07 — actual post-write growth measured against estimate | PASS | Production database size and incremental growth were measured and documented after the archive release. |

## Consolidated result

| Result | Count |
|---|---:|
| PASS | 8 |
| PARTIAL | 16 |
| BLOCKED | 3 |
| NOT VERIFIED | 21 |
| FAIL | 0 |\n| **Total** | **48** |

A criterion marked NOT VERIFIED is not presumed satisfied. The division cannot be declared complete while any required criterion remains PARTIAL, BLOCKED or NOT VERIFIED.

## Immediate completion sequence

1. **Specification/design:** resolve the eight open decisions in BP04 section 23 and obtain approval of the BP04 specification. The master blueprint approval did not approve this division specification.
2. **Business registry integrity:** generate a reproducible 10,000-business audit covering unique valid identities, lifecycle counts, branch/brand/alias exclusions, duplicates, placeholders, local/off-map scope and provenance.
3. **Property and operational geography:** complete the BP02 operational release separately; then reconcile BP04 property/address/access references against approved canonical BP02 identities without guessing or promoting design candidates.
4. **Ownership/tenancy:** run explicit temporal tests for joint/disputed interests, management/landlord/operator separation, agreements, renewals, expiry, subletting, continuing occupancy and property transfer.
5. **Organisations and services:** complete organisation/facility/operator registers and the required healthcare and transport interfaces; add utilities/service dependency interfaces where the actual game consumes them.
6. **Staff, stock and events:** validate BP03/BP33 person/employment references, inventory movements where enabled, causal supply disruptions and actor/reason/time-provenanced lifecycle changes.
7. **Police/security:** complete authorized police query coverage for occupancy/access/staff/service records, BP42 policy release, restricted-data controls and hidden-truth leakage tests. No production grants are created by this audit.
8. **Scale, storage and recovery:** run a reproducible 10,000-business query benchmark, dynamic history/storage benchmark, rollback and recovery checks, and complete source-requirement-to-test traceability.
9. Re-run the consolidated matrix. Only mark PASS where a named reproducible test/artifact proves the full criterion. Record external-owner blockers separately; do not silently waive BP04-owned requirements.

## Write boundary

This is a source/documentation audit only. No production Neon writes, grants, canonical address promotions, operational access-point approvals, or property inventory expansion occurred. Work remains on GitHub `main`.


## Business-name remediation and remaining reservation gap — 2026-11-26

The former sequence-suffix defect in `runtime/business_registry_generator.py` has been corrected. A versioned SW-UNS vocabulary supplies 173 adjectives, 176 nouns, 16 business forms and 30,448 adjective/noun roots. The deterministic generator samples an 11,000-name candidate pool, screens internal near-duplicates at the shared 0.90 threshold, holds four near-duplicate candidates, and emits 10,000 normalized-unique trading names. It rejects numeric placeholders and checks exact collisions against all 102 adopted SW-GEO-V1 names. Every establishment remains linked to a Saltwater property-world unit.

The business registry and deterministic gzip were regenerated and committed to `main`. The resulting files are 8,171,566 bytes (JSON) and 638,533 bytes (gzip). Business-registry build [45840815853](https://github.com/Joshuaogri/saltwater/actions/runs/45840815853) passed all nine regression tests. Migration validation [45840815670](https://github.com/Joshuaogri/saltwater/actions/runs/45840815670) passed.

**Current acceptance:** AC-A04 is PARTIAL, not FAIL. Internal generated-batch duplicate/near-duplicate checks and exact geography collision checks pass. Names have not yet been reserved in the persistent shared `sw_names` registry, and the comparison does not yet cover every adopted canonical name across all domains. The generated data explicitly records `DRY_RUN_CANDIDATES_NOT_YET_PERSISTENTLY_RESERVED`. AC-A01 is PASS for the current 10,000 distinct local business identity dataset; complete cross-domain persistent name reservation is separately tracked under AC-A04. AC-A02 is now PASS based on the added branch/brand/alias anti-inflation regression fixtures.

**Concrete database adapter blocker:** the current SW-NAM-001 proposal 0009 reservation table stores `entity_id bigint` and its trigger only supports `GEOGRAPHY` and `PERSON`. BP04's authoritative `sw_property.business.business_id` is a text stable ID (for example, `SWBIZ-000001`). Proposal 0011 broadens the entity-type check but does not extend the trigger or bigint identity column, so it does not make BUSINESS reservation functional. A safe BP04 adapter needs a text stable-reference path, explicit business-row existence validation, transactional reservation and search support, tested against the actual disposable BP04 schema. Do not cast business IDs to integers or treat an unrelated surrogate as their stable identity.

**Next implementation task:** design and test the missing text-ID BUSINESS adapter against the actual BP04 disposable schema, build a complete dry-run inventory of all adopted global canon names, then exercise a 10,000-name bulk reservation/import against disposable PostgreSQL. Report exact collisions, near-duplicate review cases, idempotent retries and rollback outcomes. Do not write the production Neon naming registry without fresh explicit approval.


## BP04 follow-up — persistent business naming acceptance passed (2026-11-28)

This section supersedes the 2026-11-26 statement that business names had not yet been persistently reserved in disposable PostgreSQL. It does not change the production write boundary or imply that every part of AC-A04 is complete.

- **Workflow:** [PKG-001 run 46120150588](https://github.com/Joshuaogri/saltwater/actions/runs/46120150588), completed successfully on `main`.
- **Disposable PostgreSQL job:** all 19 execution steps passed, including the 20,000-name acceptance, NPC dispatch integration and final smoke check.
- **Python regression job:** all 36 steps passed.
- **Dedicated naming suite:** 10 tests passed in 1,043.796 seconds.
- **Bulk result:** 10,000 business identities; 20,000 persistent reservations (10,000 trading + 10,000 legal); stable text business IDs; global namespace collision controls; exact/near-duplicate checks; deterministic generation manifest; bounded transactions.
- **Negative paths:** exact collision, cross-business name reuse, near-duplicate review, unknown business identity and rollback were rejected as expected; their tests passed.
- **Integration:** NPC dispatch test passed; vacant establishments did not create fictional dispatch crews. Final smoke check found 1,000 people and the runtime, naming registry and population counter relations.
- **Isolation:** disposable PostgreSQL only. No production Neon write, grant, name reservation, geography promotion or seed.

**Revised criterion status:** AC-A04 remains PARTIAL because the acceptance covers the persistent business reservation adapter and 20,000 tested business public names, but the complete adopted canonical-name inventory across every domain is not yet evidenced. AC-A01 is PASS on the deterministic source-registry acceptance: 10,000 distinct local business identities, 10,000 establishments/primary links, 20,000 unique public names, valid required identity/lifecycle fields and no numeric placeholders. AC-A02 is PASS: the adversarial branch/brand/alias anti-inflation fixtures pass. AC-A05 is PASS: all lifecycle classes reconcile to the total and embedded summary, including valid zero-count classes. AC-A03 is now PASS: the 10,000-establishment property/geography lineage audit reports zero exceptions, and invalid address references fail closed. AC-G03 remains PARTIAL: the in-memory 10,000-business gameplay lookup benchmark passed its p95/p99 budgets on both PostgreSQL 16 and 18, and indexed results matched the former linear semantics. Database-backed query latency/write throughput remain unmeasured. The 1,043.796-second persistent naming-suite duration remains a separate performance observation and warrants focused optimisation; no acceptance assertions were weakened.

The next BP04 work is therefore not to rebuild the naming adapter. It is to (1) complete the global adopted-canon inventory and business registry reconciliation, then (2) address the temporal ownership/tenancy acceptance matrix. Keep operational property/address blockers separate from BP04-owned work and keep all production Neon writes out of scope.
