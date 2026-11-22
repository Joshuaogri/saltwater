# BP-23 — Evidence Management

**Project:** Saltwater — fictional sovereign city-state, one city, one jurisdiction  
**Blueprint division:** BP-23 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test execution:** NOT_STARTED | **Verification:** NOT_STARTED  
**Authority:** Derived from the unchanged 52-division source and fixed BP-01–BP-44 structure. No canon or division structure is changed.

## 1. Purpose

BP-23 defines the authoritative lifecycle of evidence and exhibits handled by Saltwater Police: recognition, registration, unique identity, classification, provenance, packaging, seals, handlers, custody, storage, movement, access, forensic submission/return, preservation, disclosure references, retention, disposal and audit. It supports physical, digital, documentary, biological, trace, impression, weapon, clothing, vehicle, environmental and testimonial-source material. The catalogue is extensible; category never determines evidential value.

BP-23 owns exhibit identity and evidential custody/continuity. BP-22 owns scene control, search and original recovery context. BP-24 owns forensic methods, results and expert interpretation. BP-20 owns surveillance source records; BP-19 interview originals; BP-21 intelligence. BP-23 may register a controlled evidential copy without taking ownership of the originating record. Registration, possession or a forensic result does not establish proof, guilt or admissibility.

## 2. Scope and exclusions

In scope: exhibit registration/IDs; evidence categories/descriptions; source and recovery references; condition and packaging; seals and tamper events; custody; locations; transfers and acceptance; temporary possession; digital acquisition/integrity metadata; derivatives; contamination; forensic submission/return; access; preservation holds; disclosure/export references; retention/disposal; audit, correction and reconciliation.

Out of scope: scene boundaries/search and recovery narrative (BP-22); canonical identity/property (BP-03/BP-04); surveillance originals/capture (BP-20); interview originals (BP-19); intelligence assessment (BP-21); forensic methods/results (BP-24); arrest/search/warrant authority (BP-25); person custody (BP-26); charging/disclosure workflow and court decisions (BP-27/BP-28); global clock (BP-37); schema/persistence/security policy (BP-38/BP-39/BP-42).

## 3. Concepts and evidential distinctions

An exhibit is a uniquely identified item or formally controlled evidential record. Evidence is a broader epistemic/legal concept; registration does not establish authenticity, relevance, reliability, admissibility or weight. Keep distinct: original source record/object; registered exhibit; packaging/seal state; custody history; forensic submission; examination result; interpretation; investigative inference; disclosure copy; court-used version and ruling. Never overwrite one layer with another. Allegations, intelligence, witness accounts, observations, analytical products, forensic conclusions and adjudicated findings remain distinct record types with explicit provenance.

## 4. Entity model and identifiers

Entities: Exhibit, ExhibitVersion, Classification, RecoveryReference, SourceReference, PackagingUnit, Seal, SealEvent, CustodyEvent, CustodianAssignment, StorageLocation, LocationOccupancy, Transfer, TransferAcceptance, AccessEvent, HandlingEvent, ConditionAssessment, ContaminationEvent, DigitalAcquisition, IntegrityCheck, Derivative, ForensicSubmission, SubmissionItem, ExaminationReturnReference, PreservationHold, RetentionDecision, DisposalEvent, DisclosureReference, CourtUseReference and AuditEvent.

Every exhibit receives a stable, unique, non-recycled exhibit_id. IDs do not encode mutable status, location, category, case or year. Human-readable labels are not authoritative keys. Subordinate entities have independent IDs and parent references. One exhibit may relate to multiple scenes, incidents, cases or proceedings; links are typed and attributed. Similar descriptions, source, case or location never trigger automatic merging.

## 5. Registration and intake

Registration may originate from BP-22 recovery, BP-25 seizure, BP-20 surveillance export, BP-19 interview material, BP-24 examination, voluntary submission or external transfer. Record creator/receiver, date/time and time basis, source event/system, authority/purpose, initial condition, known handlers, current physical/digital location, description, category, linked scene/case/incident/person/property, restrictions, uncertainty and provisional status.

Incomplete intake may be provisional. Unknown source, finder, time, exact location or ownership remains explicitly unknown. Do not invent missing values or reject solely for incompleteness; flag required follow-up and restrictions. Duplicate detection may alert but cannot merge. Duplicate resolution records reviewer, comparison, decision and preserved IDs.

## 6. Source and recovery provenance

Every exhibit has traceable origin or an explicit unresolved gap. Recovery provenance includes scene/search area, finder, exact/best-known location, time and time basis, method, original condition, contemporaneous observations, photographs/measurements, environmental context, packaging, attendees, emergency disturbance and limitations. Seizures reference BP-25 authority/event. Surveillance references BP-20 device/source, coverage, collection window, operator, export and clock basis. Interview material references BP-19 session/recording/statement version. Forensic-generated material references BP-24 examination.

Provenance is additive and versioned. Corrections never delete the original account. Reconstructed history is labelled and identifies author, basis and uncertainty. Missing links remain gaps; assumed handoffs or inferred presence never fabricate continuity.

## 7. Classification, description and condition

Record material type/subtype, physical/digital nature, quantity/count, units, dimensions/weight only where measured, distinguishing features, observed identifiers, packaging needs, hazards, condition, damage, contamination indicators, sensitivity and handling restrictions. Separate observed description from classification, interpretation and suspected significance. Configured vocabularies are versioned; preserve free-text source description.

Condition assessments include assessor, time, method, location, packaging/seal state, context, media references and limitations. Conflicting assessments remain visible. A condition change is an event, not a silent edit. Unknown, not assessed, not applicable and negative finding are distinct.

## 8. Packaging and seals

Packaging is separate from exhibit identity so repackaging, subdivision and container replacement retain history. Each package records material/type, ID, contents, suitability, closure, packager, witness if any, time, hazard labels, environmental controls and linked version. Seals have unique IDs, type, applicator, witness, time, condition and status. Events include applied, inspected intact, damaged, broken under authority, replaced, missing, disputed and unknown.

Opening records authority, purpose, actor, time, location, attendees, pre-opening condition, seal disposition, contents condition, work, repackaging and new seal. Emergency or accidental opening remains visible. Broken seal triggers review but does not automatically invalidate the exhibit. Seal IDs are never reused and prior events never erased.

## 9. Custody and continuity

Custody is a chronological series of events, not only a mutable current-custodian field. Events include received, collected, accepted, transferred, stored, removed, accessed, examined, returned, repackaged, resealed, dispatched, delivered, quarantined, lost, damaged, recovered, disposed and corrected. Record exhibit, actor, releasing/receiving custodian, time basis, from/to location, authority, purpose, condition, package/seal state, acknowledgement, witness/transaction and source.

Dispatch does not complete a transfer; recipient acceptance is separate. Pending, rejected, partial, disputed, failed, delayed or unacknowledged transfers remain visible. Group transfers have item-level manifests and acceptance. Custody gaps identify interval, last/next confirmed event, facts, uncertainty and review; never auto-fill gaps.

## 10. Custodians and access

Custodian/handler is a scoped role for an event or period, not a permanent identity attribute. Resolve canonical persons/organisations through BP-03 and institutional records. Record identity or explicit unknown, role, authority, organisation, purpose, scope, period and restrictions. Employment or building access does not imply handling.

Record material access: inspection, package opening, digital viewing/copy/export, analysis, inventory, transfer, audit and correction. Include actor, action, purpose, authority, target/version, time, location/device, result and derivative. Restricted reads and denied access are auditable under BP-42. Access does not prove that an actor understood or altered content.

## 11. Storage and inventory

Storage locations have stable IDs, type, facility/room/container, security class, environmental capability, access policy, capacity if modelled, availability, condition and lifecycle. Occupancy is item-specific and time-valid. Location is derived from accepted events, not separately editable truth. Support stores, lockers, cold storage, hazardous areas, secure digital repositories, temporary scene custody, laboratories, court holding and external custody.

A location may become unavailable, compromised, quarantined, moved or closed; affected exhibits require reconciliation. Do not invent environmental precision. Missing/unlocated exhibits trigger an incident and preserve last confirmed location.

## 12. Transfers and external agencies

Transfers between officers, units, stores, labs, courts, external agencies or contractors record request, authority, purpose, manifest, package/seal state, dispatch, carrier, expected/actual receipt, acknowledgement, discrepancies, partial delivery, rejection, delay, damage and resolution. External entities are bounded counterparties; no external territory is simulated.

Interrupted/disputed transfers retain both parties' accounts. External identifiers remain source identifiers, not Saltwater canonical IDs. External custody gaps remain visible and are never silently repaired.

## 13. Digital and documentary material

Digital exhibits include native files, device images, forensic copies, logs, databases, communications, recordings, images, video and metadata. Record source device/system, custodian where known, acquisition authority, method/tool version, operator, interval/time basis, native format, size, digest/algorithm, write-protection where applicable, errors, source clock drift, storage and integrity checks.

Preserve original bitstream/file or authoritative source reference. Derivatives have parent, transformation, tool/version, parameters, actor/time, output digest, validation and limitations. Viewing, transcoding, redaction, enhancement, extraction or conversion never overwrites source. Hash verification supports comparison but does not prove authenticity, completeness or lawful acquisition. Scans/OCR are derivatives; preserve page/record structure and OCR limitations.

## 14. Contamination and integrity

Record suspected/confirmed contamination, cross-transfer, tampering, damage, loss, substitution, unauthorised access, seal discrepancy, exposure, data corruption, clock mismatch, incomplete acquisition and other concerns. Capture reporter/time, affected item/package/version, source, observations, suspected mechanism, interval, potentially involved persons/locations, containment, preservation, review owner and outcome.

Distinguish allegation, observed discrepancy, technical result and formal conclusion. Do not auto-label an exhibit invalid or tampered from an unverified allegation. Preserve exculpatory and adverse material equally. Disputes may remain unresolved. Reviews are attributed/versioned and cannot delete source events.

## 15. Forensic submission and return

BP-23 owns exhibit and custody; BP-24 owns forensic workflow, methods, raw results, interpretation, quality and expert conclusions. Submission references exact exhibit versions, requesting authority, question/scope, priority, discipline, hazards, contamination, package/seal state, transfer and acceptance. BP-23 records custody movement; BP-24 records examination.

Submission states include pending, accepted, rejected, deferred, partially completed, completed, cancelled and clarification requested. Examiner-created samples/derivatives use controlled registration. Return records condition, package/seal, remaining material, consumption/destruction authority, new location and custody acceptance. Results never overwrite original descriptions or raw source.

## 16. Intelligence, interviews and surveillance

BP-21 owns intelligence grading, products, confidence and dissemination. If formally tendered, BP-23 registers the exact source/version and restrictions; intelligence does not become proof. BP-19 owns interview sessions, recordings, notes and statement versions. BP-20 owns surveillance devices, collection coverage, authorisations, originals and retrieval. BP-23 owns custody of accepted evidential exports/media. Origin remains authoritative.

Copies are labelled original, forensic image, export, certified copy, working copy or derivative. Coverage and time-range limits are preserved. Registration does not imply completeness.

## 17. Case, legal and court interfaces

Exhibits link to multiple cases, incidents, persons, scenes, charges and proceedings through typed, attributed, time-valid relationships. BP-15 owns case lifecycle; BP-16 investigative actions; BP-18 suspect/offender status; BP-25 seizure authority; BP-27 charging/disclosure/prosecution; BP-28 court process/outcomes. BP-23 supplies stable references, versions, custody/integrity history and authorised copies.

Court-use references identify proceeding, issue/charge, exhibit version, disclosure state, party and ruling reference. Court outcomes cannot rewrite historical exhibit/custody records. Admission, exclusion, challenge, weight and findings are legal/court-owned. Registration never asserts admissibility.

## 18. Preservation, retention and disposal

Preservation holds record authority, scope, reason, requester/approver, start/end, affected items/versions and review/release conditions. Multiple holds may overlap. Retention policy is configured under BP-38/BP-44 and applied using BP-37; changes are versioned and never silently erase items retroactively. Disposal requires authority, review of active cases/proceedings/holds, item identity, method, actor, time, witnesses where required, final condition, certificate and resulting status. Digital deletion records scope and verification. Examination consumption records prior quantity, authority, amount consumed, remainder and result reference.

No expiry, purge or disposal progresses while paused/player absent. Active holds block routine disposal. Conflicting rules leave the item preserved pending review.

## 19. Corrections, versions and audit

Original registration and custody events are append-only. Corrections create a version/event with author, authority, time, reason, affected fields, prior value, replacement, evidence basis and review. Never silently change ID, recovery, custodian, location, time, seal, source, result or court reference. Superseded records remain available to authorised reviewers.

Audit covers creation, restricted reads, registration, packaging/seals, custody, transfer, storage, access, forensic submission/return, integrity review, preservation, disclosure export, retention, disposal, correction, merge/split and override. Each event records actor/system, authority, purpose, target/version, time, outcome and provenance.

## 20. Permissions and confidentiality

BP-42 owns global security. BP-23 defines permissions for index, sensitive descriptions, source identity, recovery location, custody, package/seal history, digital content, submissions, integrity concerns, disclosure copies, holds, disposal, export, correction and audit. Access is least-privilege and purpose-bound. Case assignment, rank or physical custody does not grant all access.

Medical, confidential-source, protected-witness, covert surveillance and privileged material retains source-owner restrictions. Search previews, counts, reports, notifications, exports and AI summaries enforce identical restrictions. Credentials never enter evidence records/logs. Denials are audited without exposing protected content.

## 21. NPC knowledge and hidden truth

NPC custodians, examiners, investigators and administrators know only material observed, received, examined or authorised. A database link is not an NPC knowledge event. BP-14 hidden truth and culprit/accomplice identities never surface through exhibit names, metadata, labels, custody events, automated descriptions, summaries, search rankings, forensic placeholders or errors. The exact reveal condition remains the player typing bingo; no role, export, test or narrative event provides an alternate route.

No unsolicited investigative hints or next steps are generated. AI descriptions cannot invent source details, custody events, results, legal status or significance. Canon-changing generated claims must be persisted as attributed structured events.

## 22. Time, population and pause

BP-37 owns the sole simulation clock. While player is outside the simulation, no custody transfer, courier movement, storage deterioration, seal inspection, examination progress, retention timer, review, disposal, notification, NPC action or deadline advances. Resume restores exact state without off-screen catch-up. Player-authorised external actions are entered as explicit events with stated time and provenance.

All persons use BP-03 canonical identity. Every living person counts once toward the hard 10,000 cap. Materially relevant persons are promoted permanently and never downgraded. Population conflicts follow governing rules; no person is silently deleted.

## 23. Storage efficiency and persistence

Neon PostgreSQL is authoritative persistent database; GitHub holds source/specification/migration history; ChatGPT is user-facing AI partner/interface. BP-38 owns schemas, constraints, IDs, transactions and indexes; BP-39 persistence/backup/recovery. Store narrative losslessly, normalise shared facts, reference repeated entities and avoid duplicated payloads. Immutable source records/events remain separate from derived views/summaries.

Large digital objects may use controlled object references with metadata, checksums, retention and recoverability. Missing objects are flagged, never replaced. Compression cannot lose meaning, source wording, provenance, versions, custody or uncertainty. Custody transfer writes must be transactionally consistent. Never claim live database connectivity without a successful test. This design authorises no schema, seed, import or bulk write.

## 24. Interface and reports

Text-first operations support register/search/list, inspect provenance/condition/package/seal, review custody, record transfer/acceptance, locate inventory, record access, create derivatives, submit/return for examination, record integrity concerns, link cases/scenes/persons, manage holds, prepare disclosure references, record court use, retention/disposal review, correction and audit. Essential functions work without maps/images.

Optional views: custody timeline, chain diagram, package/seal history, inventory, transfer manifest, digital lineage, forensic submission status, integrity timeline and court exhibit index. Views derive from canonical records, show versions/uncertainty, are permission-filtered and traceable.

## 25. Inputs, outputs and events

Inputs: BP-03 identities; BP-04 property/access; BP-09 resources; BP-12 incident; BP-15 case; BP-16 investigation; BP-17/BP-18 participant roles; BP-19 interview sources; BP-20 surveillance; BP-21 intelligence; BP-22 scene recovery; BP-24 forensic; BP-25 seizure; BP-27 legal/disclosure; BP-28 court; BP-30 authority; BP-35 causal events; BP-37 time; BP-38 schema; BP-39 persistence; BP-40 visuals; BP-42 permissions.

Outputs: exhibit registrations/versions; provenance links; package/seal events; custody/transfer; location occupancy; access/handling; digital acquisition/integrity/derivatives; integrity concerns; forensic submissions/returns; holds; disclosure/court references; retention/disposal; audit/reports.

Events include exhibit_registered/classified/described/corrected; recovery_linked; package_created/opened/resealed; seal_applied/inspected/damaged/broken/replaced; custody_received/transferred/accepted/rejected/disputed; location_entered/moved/removed; access_granted/denied/recorded; condition_assessed/changed; contamination_suspected/assessed; digital_acquired/integrity_checked/derivative_created; forensic_submitted/accepted/deferred/rejected/returned; hold_applied/reviewed/released; disclosure_copy_created/exported; court_use_linked; retention_reviewed; disposal_authorised/completed; exhibit_lost/damaged/recovered; correction_appended. Each event carries stable ID, exhibit/version, actor, authority, purpose, event/record/effective time, state, source, idempotency and schema version.

## 26. Failure handling and edge cases

Unknown finder/source/time/location; item before scene designation; several items from one recovery; sample subdivision; duplicate candidate or mistaken merge; incomplete notes; emergency disturbance; unavailable/wrong packaging; unreadable/damaged seal; unacknowledged/partial transfer; rejection; delay; custody gap; conflicting accounts; unknown handler; temporary storage; store outage; compromised cold storage; power loss; misplaced item; location closure; external transfer dispute; unavailable digital source; interrupted acquisition; hash mismatch; clock drift; corrupted file; unsupported format; OCR error; derivative made with wrong tool version; original overwrite attempt; suspected/unconfirmed contamination; consumed sample; delayed examination; altered return package; earlier court version required; redacted disclosure copy; conflicting holds; changed retention policy; disposal under hold; pause mid-transfer; idempotent retry; backup missing object; restricted source exposed in preview. Preserve facts and uncertainty, block unsafe transitions, create explicit exception states and never fabricate continuity.

## 27. Dependencies and ownership

BP-22 supplies scene/recovery context; BP-23 registers exhibit and owns custody after accepted transfer. BP-20/BP-19/BP-21 remain authoritative for source records; BP-23 links/registers a specific evidential copy. BP-24 owns examination methods/results; BP-25 seizure authority; BP-27 disclosure/prosecution; BP-28 court rulings; BP-37 time; BP-38/BP-39 data/persistence; BP-42 security. Dependency failure leaves a pending/unresolved reference and prohibits false success. No division silently mutates another's authoritative record.

## 24. Acceptance tests

These are design criteria, not executed results. BP-43 owns test execution and reproducible evidence.

- **EVID-AT-001** — Every exhibit has a stable, unique, non-recycled ID.
- **EVID-AT-002** — Registration preserves source event and originating system reference.
- **EVID-AT-003** — Provisional registration supports explicit unknown fields.
- **EVID-AT-004** — Missing provenance is flagged, never fabricated.
- **EVID-AT-005** — Duplicate detection never merges automatically.
- **EVID-AT-006** — Duplicate resolution preserves IDs and reviewer rationale.
- **EVID-AT-007** — One exhibit links to multiple cases without duplication.
- **EVID-AT-008** — One recovery can produce multiple independently identified exhibits.
- **EVID-AT-009** — One exhibit can link to multiple scenes through typed relationships.
- **EVID-AT-010** — Registration does not assert authenticity, admissibility, relevance or guilt.
- **EVID-AT-011** — Observed description is distinct from interpretation.
- **EVID-AT-012** — Unknown, not assessed, not applicable and negative finding are distinct.
- **EVID-AT-013** — Condition assessments are attributed and time-stamped.
- **EVID-AT-014** — Conflicting condition assessments remain visible.
- **EVID-AT-015** — Condition change creates an event, not a silent edit.
- **EVID-AT-016** — Every exhibit has traceable origin or explicit unresolved gap.
- **EVID-AT-017** — Scene exhibits reference BP-22 recovery context.
- **EVID-AT-018** — Seized exhibits reference BP-25 authority and event.
- **EVID-AT-019** — Surveillance exhibits reference BP-20 source, coverage, operator and time basis.
- **EVID-AT-020** — Interview exhibits reference BP-19 exact session/source version.
- **EVID-AT-021** — Forensic-generated material references BP-24 creation event.
- **EVID-AT-022** — Reconstructed provenance is labelled with author, basis and uncertainty.
- **EVID-AT-023** — Original recovery wording survives correction.
- **EVID-AT-024** — Packaging units have independent stable IDs.
- **EVID-AT-025** — Repackaging preserves previous container history.
- **EVID-AT-026** — Seal IDs are unique and never reused.
- **EVID-AT-027** — Seal application records actor, time, condition and witness where applicable.
- **EVID-AT-028** — Opening records authority, purpose, pre-opening state and attendees.
- **EVID-AT-029** — Seal damage is an event, never silently repaired.
- **EVID-AT-030** — Repackaging creates new packaging/seal history.
- **EVID-AT-031** — Emergency or accidental opening remains visible.
- **EVID-AT-032** — Seal damage does not automatically invalidate an exhibit.
- **EVID-AT-033** — Custody is an event sequence, not only a mutable field.
- **EVID-AT-034** — Every custody event identifies actor, time, purpose and authority.
- **EVID-AT-035** — Transfers identify outgoing and receiving custodians separately.
- **EVID-AT-036** — Dispatch alone does not complete transfer.
- **EVID-AT-037** — Recipient acceptance is a separate event.
- **EVID-AT-038** — Rejected transfers preserve dispatch and rejection records.
- **EVID-AT-039** — Partial manifests record item-level outcomes.
- **EVID-AT-040** — Custody gaps are explicit and never auto-filled.
- **EVID-AT-041** — Unknown handler remains unknown without supporting evidence.
- **EVID-AT-042** — Custody corrections preserve original event and basis.
- **EVID-AT-043** — Current custodian is derived from accepted events.
- **EVID-AT-044** — Current location is derived from accepted location/custody events.
- **EVID-AT-045** — Storage locations have stable IDs and access restrictions.
- **EVID-AT-046** — Storage occupancy is item-specific and time-valid.
- **EVID-AT-047** — Moving an exhibit creates a location/custody event.
- **EVID-AT-048** — Storage closure/compromise triggers reconciliation.
- **EVID-AT-049** — Misplaced exhibits preserve last confirmed location.
- **EVID-AT-050** — Environmental storage values identify measured or sourced estimates.
- **EVID-AT-051** — External agencies are bounded counterparties, not new territories.
- **EVID-AT-052** — External IDs remain source identifiers.
- **EVID-AT-053** — External transfer disputes preserve both accounts.
- **EVID-AT-054** — Digital acquisition records source, method/tool version and operator.
- **EVID-AT-055** — Digital acquisition records time basis and clock uncertainty.
- **EVID-AT-056** — Digital originals are preserved or referenced under controlled retention.
- **EVID-AT-057** — Integrity checks record algorithm and digest.
- **EVID-AT-058** — Hash match is not proof of authenticity or lawful acquisition.
- **EVID-AT-059** — Derivatives record parent, transformation and output integrity.
- **EVID-AT-060** — Viewing/redaction/enhancement never overwrites original.
- **EVID-AT-061** — OCR/transcription is labelled derivative with limitations.
- **EVID-AT-062** — Interrupted acquisition is recorded incomplete.
- **EVID-AT-063** — Integrity mismatch creates explicit exception/review.
- **EVID-AT-064** — Contamination concerns identify affected items, source and uncertainty.
- **EVID-AT-065** — Unverified tampering allegation is not an established finding.
- **EVID-AT-066** — Integrity review is attributed and versioned.
- **EVID-AT-067** — Exculpatory and adverse material are retained equally.
- **EVID-AT-068** — BP-23 does not decide admissibility.
- **EVID-AT-069** — Forensic submission references exact exhibit versions.
- **EVID-AT-070** — BP-24 owns methods, raw results and expert interpretation.
- **EVID-AT-071** — Submission acceptance/rejection is recorded by recipient.
- **EVID-AT-072** — Examination return records condition, package, seal and location.
- **EVID-AT-073** — Consumed material records authority, amount and remainder.
- **EVID-AT-074** — Results do not overwrite original exhibit descriptions.
- **EVID-AT-075** — Intelligence remains distinct from exhibit and proof.
- **EVID-AT-076** — Intelligence tender references exact source version.
- **EVID-AT-077** — BP-19 remains authoritative for interview originals/statements.
- **EVID-AT-078** — BP-20 remains authoritative for surveillance originals/capture.
- **EVID-AT-079** — Registered copies link to originating authoritative record.
- **EVID-AT-080** — Surveillance coverage limitations remain attached to export.
- **EVID-AT-081** — Exhibits link to multiple cases/proceedings through typed relationships.
- **EVID-AT-082** — BP-15 owns case lifecycle; BP-23 does not change case state.
- **EVID-AT-083** — BP-27 owns disclosure/prosecution workflow.
- **EVID-AT-084** — BP-28 owns court rulings/outcomes.
- **EVID-AT-085** — Court-use references identify exact exhibit version.
- **EVID-AT-086** — Court outcomes do not rewrite custody history.
- **EVID-AT-087** — Registration does not imply admissibility or weight.
- **EVID-AT-088** — Preservation holds record authority, scope, actor and review.
- **EVID-AT-089** — Overlapping preservation holds are supported.
- **EVID-AT-090** — Active hold blocks routine disposal.
- **EVID-AT-091** — Retention policy changes are versioned.
- **EVID-AT-092** — Retention/disposal do not progress while paused.
- **EVID-AT-093** — Disposal records authority, method, actor, time and status.
- **EVID-AT-094** — Digital destruction records scope and verification.
- **EVID-AT-095** — Examination consumption is distinct from disposal.
- **EVID-AT-096** — Conflicting retention rules preserve item pending review.
- **EVID-AT-097** — Original registration/custody events are append-only.
- **EVID-AT-098** — Corrections record prior value, replacement, author, reason and basis.
- **EVID-AT-099** — Superseded versions remain available to authorised reviewers.
- **EVID-AT-100** — Restricted reads and denied access are audited.
- **EVID-AT-101** — Search results/previews enforce exhibit permissions.
- **EVID-AT-102** — Exports preserve redaction and derivative lineage.
- **EVID-AT-103** — Least privilege applies independently of rank or physical custody.
- **EVID-AT-104** — Source-owner restrictions remain on evidential copies.
- **EVID-AT-105** — NPC knowledge follows plausible observation, receipt and authority.
- **EVID-AT-106** — Database links alone do not create NPC knowledge.
- **EVID-AT-107** — Hidden culprit/accomplice identity cannot leak through metadata.
- **EVID-AT-108** — Only exact player input bingo triggers hidden-truth reveal.
- **EVID-AT-109** — No unsolicited investigative hints or next-step recommendations.
- **EVID-AT-110** — AI cannot invent custody, source, forensic or legal events.
- **EVID-AT-111** — Canon-changing generated claims persist as attributed events.
- **EVID-AT-112** — Each living person counts once toward 10,000 cap.
- **EVID-AT-113** — Materially relevant persons are permanently promoted.
- **EVID-AT-114** — BP-37 owns simulation time and one canonical clock.
- **EVID-AT-115** — No transfer/examination/timer/disposal advances while absent.
- **EVID-AT-116** — Resume restores exact state without off-screen catch-up.
- **EVID-AT-117** — Digital objects retain metadata, integrity and recovery references.
- **EVID-AT-118** — Compression does not remove meaning or provenance.
- **EVID-AT-119** — Immutable source events are separate from derived views.
- **EVID-AT-120** — Custody transfer is transactionally consistent.
- **EVID-AT-121** — No live Neon connectivity claim without successful test.
- **EVID-AT-122** — No schema/seed/import/bulk write is authorised by this draft.
- **EVID-AT-123** — Text-only registration/search/custody review is fully operable.
- **EVID-AT-124** — Optional diagrams derive from canonical records.
- **EVID-AT-125** — Every visual traces to source exhibit/version records.
- **EVID-AT-126** — BP-43 test status is not inferred from specification creation.

## 25. Source traceability

The original source JSON and 52→44 crosswalk remain unchanged. Source IDs use source division number and original array order.

| Source ID | Original requirement/test | BP-23 coverage |
|---|---|---|
| S13.R02 | Model injuries, deaths, medical evidence and care access consistently without a deep healthcare simulator. | Sections 3, 6, 17, 18; restricted sourced medical material, not a parallel simulator. |
| S13.R03 | Protect sensitive information through role-based access. | Section 19; source restrictions and least-privilege permissions. |
| S18.R02 | Track keys, locks, alarms, maintenance, ownership and authorised access. | Sections 9–11; evidence storage/access consumes authoritative property records. |
| S18.R03 | Ensure scene geometry and access timelines are consistent. | Sections 6, 9, 10; recovery and custody reference scene/access provenance. |
| S30.R03 | Preserve case chronology and decision provenance. | Sections 15, 16, 20; immutable exhibit history and attributed links. |
| S32.R01 | Scene boundaries, entry logs, security, search, recovery, exhibits, packaging, seals, handlers and transfers. | Sections 5–11; BP-22 owns scene control; BP-23 exhibit/packaging/custody. |
| S32.R02 | Preserve original observations separately from interpretation. | Sections 3, 6, 7, 13; source observations remain linked and unaltered. |
| S32.R03 | Support physical, digital, documentary, biological, trace and testimonial evidence. | Sections 4, 5, 12, 14; extensible categories and source ownership. |
| S33.R01 | Forensic disciplines, submissions, prioritisation, methods, results, limitations, contamination, quality and interpretation. | Section 13; BP-23 custody interface, BP-24 owns methods/results. |
| S33.R02 | Distinguish raw result, interpretation and investigative inference. | Sections 3, 13, 15; separate source/exhibit/result/interpretation/inference. |
| S33.R03 | Support specialist resources and realistic turnaround. | Sections 13, 21; submission states and pause-aware timing interface. |
| S34.R02 | Preserve source interview content and distinguish summaries from originals. | Sections 3, 14; BP-19 owns original, registered copies/derivatives are explicit. |
| S35.R02 | Separate intelligence from evidence and established fact. | Sections 3, 14; explicit status separation and source version. |
| S36.R02 | Track surveillance requests, authorisations, windows, operators, exports and evidential continuity. | Section 14; BP-20 owns capture; BP-23 accepted-copy custody. |
| S36.R03 | Absence of coverage is not proof of absence. | Section 14; limitations retained with exports. |
| S37.R02 | Maintain custody clock and property continuity. | Sections 8–11, 15, 21; chronological, pause-aware custody. |
| S38.R01 | Charging, disclosure, prosecution, hearings, evidence, rulings, verdicts, sentencing, appeals and outcomes. | Section 15; BP-23 supplies versioned exhibits; BP-27/BP-28 own legal process. |
| S38.R03 | Feed outcomes back without rewriting investigative history. | Sections 15–16; additive court references. |
| S43.R02 | Separate hidden world truth, player-visible information and NPC knowledge. | Section 18; knowledge boundary. |
| S43.R03 | Reveal hidden culprit/accomplice identity only after exact bingo input. | Section 18; exact reveal gate across metadata and outputs. |
| S45.R01 | Optional maps, layouts, timelines, charts and forensic visuals. | Section 22; optional custody/lineage views; text remains sufficient. |
| S45.R02 | Visuals derive from canonical evidence data and do not contradict text. | Sections 22–23; versioned references and traceability. |
| S46.R02 | Canonical schemas, constraints, relationships, IDs, migrations, indexes and transactions. | Sections 4, 23; IDs and transactional custody; BP-38 owns schema governance. |
| S46.R03 | Lossless narrative, normalised shared facts, references and no duplicate payloads. | Section 23; lossless records and canonical references. |
| S46.R04 | Separate immutable source records/events from derived views/summaries. | Sections 3, 16, 23; append-only originals. |
| S48.R02 | Protect hidden truth and restricted personal information from player-facing leakage. | Sections 17–19; least privilege and reveal firewall. |
| S32.T01 | Every exhibit has unique ID, recovery details, continuity and current location/status. | EVID-AT-001, 016–023, 032–049, 104–108. |
| S33.T01 | Every conclusion identifies method, source, limitations and examiner. | EVID-AT-067–074; BP-24 owns conclusion and source references. |
| S35.T01 | Every intelligence item has source, confidence and handling status. | EVID-AT-075–077; BP-21 owns grading; evidential copy references version. |
| S36.T01 | Every surveillance item has source device, coverage limits and time basis. | EVID-AT-018–020, 076–078. |
| S45.T01 | Every visual traces to underlying canonical records. | EVID-AT-109–110. |
| S46.T01 | Schema constraints enforce identity, referential integrity, population cap and lifecycle states. | EVID-AT-001, 002, 098, 103, 108; BP-38/BP-43 validation. |
| S48.T01 | Unauthorised reads/writes are rejected and audited. | EVID-AT-091–096. |

Cross-cutting X01–X10 apply where relevant: one-city canon and bounded population; canonical identity; causal/time-valid records; provenance; fact/allegation/inference/evidence/finding separation; immutable originals and additive corrections; player agency and exact reveal firewall; time freeze; storage/persistence integrity; text-first operation with optional traceable visuals.

## 26. Open decisions and risk register

### Open decisions
1. Exhibit ID format and human-readable label convention.
2. Evidence category/subcategory taxonomy and extensibility.
3. Mandatory intake fields by exhibit type and provisional registration.
4. Packaging material catalogue and seal format.
5. Custody acceptance/witness requirements by transfer type.
6. Storage classification, environmental thresholds and inventory cadence.
7. Digital acquisition metadata, hashing algorithms and object-storage boundary.
8. Forensic submission priority/turnaround with BP-24.
9. Integrity review authority and escalation.
10. Preservation hold authority and retention schedule.
11. Disposal/consumption authorisation matrix.
12. Disclosure copy formats, redaction and export controls.
13. Court exhibit versioning and challenge/ruling reference format.
14. Sensitive exhibit classifications and permissions.
15. External agency custody reconciliation.

### Risk register

| Risk | Mitigation |
|---|---|
| Registration mistaken for proof | Explicit epistemic/legal separation |
| Custody gaps hidden by assumed transfers | Append-only events and explicit gaps |
| Scene/exhibit ownership duplicated | BP-22 recovery context; BP-23 accepted custody |
| Seal damage erased | Versioned seal events and integrity review |
| Derivative replaces original | Immutable source and derivative lineage |
| Intelligence treated as proof | Exact source version and status distinction |
| Sensitive material leaks in previews | Permission-filtered derived outputs |
| Disposal under active hold | Hold-aware transition guards |
| Paused simulation advances timers | BP-37 freeze tests |
| Compression loses chain detail | Lossless source narrative/event history |
| Court outcome rewrites history | Versioned court-use references |
| Hidden truth leaks through metadata | Exact reveal firewall across outputs |

## 27. Design completion checklist

- [ ] Exhibit identity, registration, versioning and classification specified.
- [ ] Recovery/source provenance and uncertainty specified.
- [ ] Packaging, seals and opening/resealing specified.
- [ ] Custody, handlers, transfers and acceptance specified.
- [ ] Storage inventory, movement and exceptions specified.
- [ ] Digital acquisition, integrity, derivatives and documentary handling specified.
- [ ] Contamination, integrity disputes and corrections specified.
- [ ] Forensic submission/return boundary with BP-24 specified.
- [ ] Interview, surveillance and intelligence source ownership preserved.
- [ ] Case, disclosure and court version interfaces specified.
- [ ] Holds, retention, consumption and disposal specified.
- [ ] Permissions, audit, NPC knowledge and reveal firewall specified.
- [ ] Time freeze, population cap and permanent promotion specified.
- [ ] Neon/GitHub/ChatGPT architecture and no-write governance preserved.
- [ ] Text-first interface complete; optional visuals traceable.
- [ ] All 110 acceptance tests await BP-43 execution.
- [ ] Open decisions remain explicit; no policy invented.
- [ ] No Neon schema, seed, import or bulk write has been made or authorised.

## 28. Status and next dependencies

This is a complete division design draft, not approved policy or implementation evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-24 — Forensics**. BP-24 owns forensic disciplines, examination methods, raw results, interpretation, limitations and expert conclusions. BP-23 continues to own exhibit identity, packaging, custody, storage and continuity.
