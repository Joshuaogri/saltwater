# BP04 strict acceptance audit — 2026-11-26

**Decision: NOT COMPLETE.** A confirmed business-name quality defect also fails AC-A04. This audit supersedes the premature closure wording in `BP04-completion-record-2026-11-26.md`. It evaluates the current BP-04 draft specification's 48 explicit acceptance criteria (AC-A01 through AC-G07) against evidence available on `main`. A successful workflow, source archive deployment or implemented adapter is not treated as proof of an entire criterion unless the test covers the stated requirement.

**Specification authority:** `docs/blueprint/divisions/BP-04-BUILT-WORLD-PROPERTY-BUSINESSES-ORGANISATIONS.md` (still `DESIGNED_DRAFT`; eight open design decisions remain).  
**Status register:** `docs/blueprint/DIVISION-SPECIFICATION-REGISTER.md` records BP04 as IMPLEMENTED / TESTED / BLOCKED.  
**Latest relevant CI:** BP04 integration [45834691417](https://github.com/Joshuaogri/saltwater/actions/runs/45834691417) passed; PKG-001 disposable PostgreSQL [45837315742](https://github.com/Joshuaogri/saltwater/actions/runs/45837315742) passed; migration validation [45837315871](https://github.com/Joshuaogri/saltwater/actions/runs/45837315871) passed. These runs validate specific slices, not all 48 BP04 criteria.  
**Production archive:** [45675735246](https://github.com/Joshuaogri/saltwater/actions/runs/45675735246) passed archive-only source deployment. Production storage was measured separately.

## Status meanings

- **PASS** — direct implementation and repeatable test/evidence support the full criterion.
- **PARTIAL** — meaningful implementation exists, but one or more explicit parts of the criterion lack evidence.
- **BLOCKED** — a known prerequisite prevents operational acceptance.
- **NOT VERIFIED** — available evidence does not establish the criterion; this is not a claim that no related code exists.
- **FAIL** — inspected implementation directly contradicts the criterion.

## A. Registry and business minimum

| Criterion | Status | Evidence / gap |
|---|---|---|
| AC-A01 — at least 10,000 distinct valid local businesses | PARTIAL | The raw source contains 10,000 business and establishment records, but the sequence-suffixed names fail the valid-identity quality requirement; the raw count is not accepted as 10,000 valid businesses until AC-A04 is remediated. |
| AC-A02 — branches, establishments, brands and aliases not miscounted | PARTIAL | Business/establishment hierarchy and parent references are validated; a full adversarial branch/brand/alias anti-inflation acceptance report is not present. |
| AC-A03 — every business has unique ID, plausible identity, sector, local scope, lifecycle status and provenance | PARTIAL | Stable identities, sector and source provenance exist; a full record-by-record plausibility/local-scope/lifecycle audit with exception report is not linked. |
| AC-A04 — duplicates, placeholders and off-map entities cannot inflate local minimum | FAIL | `runtime/business_registry_generator.py` appends the sequential index (`{sequence:05d}`) to every trading name and registered name. These sequence-generated labels are not independently plausible business identities; they are being used to make the 10,000 names unique. The generator also does not reserve candidates through the mandatory shared SW-UNS-001 registry. The current 10,000 count therefore cannot be accepted as 10,000 valid distinct identities. |
| AC-A05 — total registry and active operating counts distinguished | NOT VERIFIED | The required reconciled count report separating all lifecycle classes is not evidenced. |
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
| AC-C03 — lease/licence dates, renewals, expiry and termination preserve history | PARTIAL | Agreement and lifecycle registers exist; 1,232 agreements were inventoried, but no execution dates were recorded and lifecycle event history is incomplete. |
| AC-C04 — subletting and third-party occupancy require explicit records | NOT VERIFIED | No dedicated positive/negative subletting and third-party occupancy acceptance is linked. |
| AC-C05 — agreement existence, rent payment and physical occupancy are not conflated | NOT VERIFIED | No end-to-end test proves separation across BP04 and BP34 payment/occupancy facts. |
| AC-C06 — expired agreement with continued occupancy is representable | NOT VERIFIED | No specific temporal conflict test/evidence is linked. |
| AC-C07 — property transfer preserves continuing tenancy and prior ownership | NOT VERIFIED | No transfer-with-continuing-tenancy history test is linked. |

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
| AC-E07 — failed multi-record transactions leave no partial authoritative state | PARTIAL | Archive importer transaction/idempotency and BP12 event-backed writer tests exist; BP04 ownership/tenancy/business multi-record transaction rollback is not demonstrated. |

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
| AC-G03 — 10,000+ business queries meet measured performance budgets | NOT VERIFIED | Bounded lookup exists, but no reproducible 10,000-business latency/throughput budget report is linked. |
| AC-G04 — storage benchmark includes shared references, indexes, event history and high-entropy text | PARTIAL | Archive-only storage measured and production growth recorded; the benchmark does not demonstrate all dynamic history/index/event workloads in the criterion. |
| AC-G05 — every acceptance test links to source requirements and reproducible evidence | BLOCKED | This criterion-level matrix is now created, but the complete requirement-to-test mapping and retained evidence links for all 48 criteria are not yet complete. |
| AC-G06 — no Neon write without baseline, estimate and explicit approval | PASS | Production archive release was user-authorised; baseline and measured growth are documented. No new production write is made by this audit. |
| AC-G07 — actual post-write growth measured against estimate | PASS | Production database size and incremental growth were measured and documented after the archive release. |

## Consolidated result

| Result | Count |
|---|---:|
| PASS | 5 |
| PARTIAL | 18 |
| BLOCKED | 3 |
| NOT VERIFIED | 21 |
| FAIL | 1 |\n| **Total** | **48** |

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


## Confirmed business-name quality defect — 2026-11-26

The registry generator currently builds each trading name as `<prefix> <root> <five-digit sequence>` and uses that as the basis for the registered name. The numeric sequence is an identity-disambiguation device, not a natural business naming method. This directly conflicts with BP04 AC-A04's prohibition on numbered placeholder names and SW-UNS-001's requirement that names be proposed and reserved through the shared canonical namespace.

**Consequence:** the 10,000-record source count is real, but it is not yet accepted as 10,000 valid distinct business identities. AC-A01's raw count passes; AC-A04 fails and AC-A03 remains partial. Do not claim the minimum valid-business invariant is satisfied until all names are regenerated as plausible names, the existing adopted global names are checked, candidate uniqueness/near-duplicate rules are applied, and the names are reserved under the shared naming authority. The business and establishment stable IDs remain unchanged by any future rename.

**Next implementation task:** replace the sequence-suffixed naming in `runtime/business_registry_generator.py` with a deterministic, sufficiently large candidate vocabulary using the shared SW-UNS generator and authoritative reservation workflow; create regression tests proving no sequence-number placeholders, no within-registry normalized duplicates, no known adopted-name collisions, and deterministic regeneration. Do not apply naming-registry writes to production Neon as part of this task.
