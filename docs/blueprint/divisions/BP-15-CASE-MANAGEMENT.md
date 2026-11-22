# BP-15 — Case Management

**Version:** 1.0 — full specification draft  
**Date:** 2026-11-22  
**Division:** BP-15 of the fixed Saltwater BP-01–BP-44 structure  
**Specification status:** `DESIGNED_DRAFT`  
**Implementation status:** `NOT_STARTED`  
**Test execution status:** `NOT_STARTED`  
**Verification status:** `NOT_STARTED`  
**Authority:** Draft derived from the approved 44-division structure and the retained 52-division source crosswalk. This document does not authorise Neon writes or database deployment.

## 1. Purpose and normative language

BP-15 defines the authoritative police case record and its lifecycle. It governs case identity, ownership, classification, status, linkage, chronology, review, referral, closure and reopening. It does not conduct investigations or own source incident, person, exhibit, intelligence, interview, forensic, prosecution or court records. “MUST”, “MUST NOT”, “SHOULD” and “MAY” are normative.

## 2. Scope and exclusions

In scope: case registration; stable identifiers; incident association; assignment and command accountability; classification snapshots; state transitions; objectives; action/decision/review records; related cases and series; duplicate review; split/merge lineage; referral; closure/reopening; audit; access; derived summaries and views. Out of scope: offence taxonomy (BP-13); occurrence truth/generation (BP-14); CAD and operational incident lifecycle (BP-12); investigative methods and task execution (BP-16); participant role semantics (BP-17/BP-18); interviews (BP-19); surveillance (BP-20); intelligence (BP-21); scenes (BP-22); exhibits (BP-23); forensics (BP-24); warrants/arrest/custody/legal process/courts (BP-25–BP-28); general identity (BP-03); map geometry (BP-02); database/persistence implementation (BP-38/BP-39).

## 3. Authority and ownership boundaries

BP-15 is sole owner of police case identity and case lifecycle. BP-12 owns operational incident identity and lifecycle. BP-13 owns offence taxonomy and classification definitions. BP-14 owns generated occurrence truth. BP-16 owns investigative actions, investigative planning and investigative decisions. BP-17 and BP-18 own victim/witness and suspect/offender role records respectively. BP-23 owns exhibit identity and continuity. BP-27/BP-28 own prosecution/legal/court records and outcomes. BP-30 owns department policy and command delegation. BP-38/BP-39 own record schema/persistence/recovery. BP-41 owns notifications/report delivery. BP-42 owns security and access enforcement. No consumer may redefine another division’s authoritative record.

## 4. Core design principles

One case identity; immutable source chronology; explicit ownership; explicit state transitions; versioned correction; typed links; separation of truth, report, allegation, intelligence, evidence, inference and adjudication; least privilege; player agency; no hidden-truth leakage; pause-safe simulation time; compact storage without semantic loss; text-first operability.

## 5. Entity catalogue

Minimum logical entities: Case; CaseClassificationVersion; CaseStatusEvent; CaseOwnershipAssignment; CaseCommandAssignment; CaseIncidentLink; CasePersonLink (role details remain with BP-17/BP-18); CaseEntityLink; CaseObjective; CaseActionReference; CaseDecision; CaseReview; CaseDeadline; CaseRelationship; CaseReferral; CaseClosure; CaseReopening; CaseMergeLineage; CaseSplitLineage; CaseAccessEvent; CaseAuditEvent; CaseSummaryVersion; CaseAttachmentReference. These are logical contracts, not a mandated physical table layout.

## 6. Canonical identifiers

Every case receives a stable non-recycled CaseID. Human-readable references are display aliases, never primary identity. IDs MUST NOT encode offence, suspect identity, guilt, location, difficulty, hidden occurrence seed, priority or chronology in a way that leaks truth. All links use canonical IDs and typed relationship records. Merge/split does not erase predecessor/successor IDs.

## 7. Case creation and registration

A case may originate from an operational incident, direct discovery, authorised proactive police activity, referral, historical review or another configured basis. Creation requires a valid source basis, creator/system actor, simulation timestamp, initial classification state, initial status, initial ownership or explicit triage custody, and provenance. A case can be registered before an incident exists only when the basis is recorded. Case creation and initial links are atomic.

## 8. Incident and source-record linkage

A case can link to zero, one or many incidents according to policy. An incident may link to multiple cases when scope, jurisdiction, investigative command or separate accountability warrants it. Link records contain type, source, creator, simulation time, rationale, effective period and status. Source incident content remains unchanged. A link never proves that linked events share an offender or cause.

## 9. Classification and offence taxonomy

Case classification references BP-13 controlled taxonomy IDs and stores a versioned snapshot of classification, confidence/qualification and rationale. Classification may be provisional, disputed, amended or undetermined. Case classification is an administrative/investigative description, not a finding of guilt or a rewrite of occurrence truth. BP-15 cannot invent or redefine offences.

## 10. Ownership, command and allocation

Day-to-day case owner, supervisory reviewer, investigative command and administrative custodian are distinct assignments. Each assignment has actor/unit, authority source, start/end simulation times, reason, acceptance and supersession. Rank alone confers no automatic case access or authority. Assignment changes preserve prior responsibility and handover. Unallocated/triage cases have explicit temporary custody.

## 11. Case state machine

Configured states: REGISTERED, TRIAGE, ALLOCATED, ACTIVE, SUSPENDED, DORMANT, COLD, REVIEW, REFERRED, CLOSED and REOPENED (REOPENED may be represented as a transition back into ACTIVE with a distinct event). State definitions and allowed transitions are policy-versioned. SUSPENDED means a deliberate pause under a recorded reason; DORMANT means no current activity but case remains open; COLD means designated long-term unresolved status; REFERRED means an external or inter-unit handoff is pending/accepted; CLOSED means an authorised closure decision, not deletion.

## 12. State transition contract

Every transition records previous state, new state, actor/process, authority, simulation time, reason, relevant decision and version. Invalid transitions fail without mutating authoritative state. Closure requires authorised decision and reason; unresolved lines and unknown offenders may remain. Reopening creates a new event and never erases prior closure. Repeated reopen/close cycles are supported.

## 13. Objectives, actions and decisions

BP-15 stores case objectives, references to actions and formal decisions. It does not prescribe investigative steps. Objectives are authored by authorised case personnel and may be changed with provenance. BP-16 owns execution and substantive investigative action records; BP-15 references them and provides case-level chronology. Proposed, authorised, commenced, completed, cancelled and failed actions remain distinct.

## 14. Reviews, deadlines and case health

Reviews record reviewer, authority, time, scope, source set, findings, directions and due dates. Deadlines use simulation time. No clock, review, escalation or automated case activity advances while the player is outside the game. Case health indicators are derived from explicit records and must not expose hidden truth or prescribe next steps.

## 15. Related cases, series and duplicate handling

Typed relationships include same-series, suspected-series, common-incident, duplicate-report, cross-reference, administrative association and referral lineage. A relationship has provenance, confidence/qualification where appropriate, effective period and review state. It is not proof of common authorship. Duplicate detection is advisory; merge/consolidation requires authorised human decision. Split and merge preserve lineage and every original ID.

## 16. People, businesses, property and other entity links

Case links reference canonical IDs for people, businesses, organisations, premises, property, vehicles and other supported entities. BP-03 owns identity and lifecycle; BP-04 owns business/property records; BP-17/BP-18 own case role semantics. A case link does not create duplicate identities or imply guilt. Materially connected persons are permanently promoted to full persistent detail through BP-03.

## 17. Incidents, evidence and specialist records

BP-15 maintains typed references to source records. BP-12 owns incidents; BP-19 interviews/statements; BP-20 surveillance; BP-21 intelligence; BP-22 scenes; BP-23 exhibits and continuity; BP-24 forensic examination; BP-25 arrest/warrants; BP-26 custody; BP-27 prosecution; BP-28 court outcomes. Case summaries must preserve the distinction between raw result, interpretation, inference and adjudication.

## 18. Referrals and interagency handoffs

A referral has sender, recipient, authority, scope, package manifest, versions, simulation time, acknowledgement and status. Statuses include prepared, sent, pending, accepted, rejected, returned, partially accepted, withdrawn and completed. Referral does not silently transfer ownership or delete local records. External bodies are represented proportionately; no external playable geography is created.

## 19. Closure, retention and reopening

Closure reasons are typed and may include resolved, referred, administratively closed, no further proportionate action, duplicate/consolidated, outside jurisdiction or other configured reason. Closure records outstanding lines and disposition. Closure is not equivalent to solved, offender identified, conviction or truth established. Retention/archival follows BP-38/BP-39 policies. Reopening requires authority and reason and preserves prior closed state.

## 20. Case chronology and provenance

Material case events are append-only. Event time (when it occurred in simulation) and record time (when entered) are separate. Corrections are new versioned events with author, reason and prior value. Each generated, imported, transcribed, manually authored or AI-assisted record identifies provenance and source version. Summaries are derived views, never authoritative replacements.

## 21. Permissions, confidentiality and conflicts

BP-42 enforces permissions for read, create, edit, assign, link, classify, restrict, refer, close, reopen, merge, split, export and override. Access may be scoped by unit, case assignment, role, clearance, purpose and sensitive flag. Conflict-of-interest restrictions are explicit. All access to restricted case material and every override are auditable. No role or seniority bypasses hidden-truth boundaries.

## 22. Hidden truth and player-agency protection

The omniscient generated occurrence truth in BP-14 is not a case-management field available to player, police users, operational NPCs, summaries, AI prompts, search indexes, exports, notifications, IDs, errors, logs or analytics. Case records contain only discovered, reported, lawfully/authorisedly accessed or otherwise in-world available information. Hidden offender/accomplice identity must not be disclosed unless the player enters exactly `bingo`. Variants such as `Bingo`, `BINGO`, `bingo ` or embedded text do not satisfy the trigger. No unsolicited solution hints or “what to investigate next” prompts are permitted.

## 23. NPC knowledge and AI-generated content

Every NPC access is constrained by role, assignment, observed events, communications and permitted records. Case assignment does not grant omniscience. AI summaries and narrative must be grounded in source records, preserve uncertainty and distinguish allegation from fact. AI-generated content that alters canon becomes a structured attributable event. Generation seeds and hidden truth stay outside player-facing data.

## 24. Time, pause and deterministic processing

All timestamps use canonical Saltwater simulation time. When simulation is paused or exited, case deadlines, scheduled reviews, automatic reassignment, NPC activity, notification delivery and processing freeze. Resume continues from persisted state with no wall-clock catch-up. Deterministic replay is supported where specified by BP-35/BP-39; it must not expose hidden seed/truth.

## 25. Population, jurisdiction and world constraints

All persons use BP-03 identity and population accounting. Total living population never exceeds 10,000; police personnel are included. No case workflow may create an extra uncounted person. Relevant-person promotion is permanent. The world remains one Saltwater city and one sovereign jurisdiction; off-map references are contextual dependencies only. At least 10,000 businesses remain represented under BP-04; case records link to business IDs rather than cloning business records.

## 26. Storage and performance contract

Store canonical case facts once; use compact typed references for repeated entities; avoid duplicated narratives and denormalised truth-bearing fields. Compression may reduce representation but never meaning, provenance, history, uncertainty, rights, exceptions or testability. Derived lists, timelines and summaries may be rebuilt from authoritative records. Pagination and retrieval must not alter chronology or access rules. Physical schema decisions belong to BP-38/BP-39.

## 27. Interface and player workflow

Essential workflows must be operable through the text-first laptop interface: list/search accessible cases; open a case; inspect chronology; view linked incidents/entities; create or edit authorised case metadata; assign/transfer; record decisions/reviews; manage typed relationships; refer; close/reopen; and inspect history. Search results and counts must not reveal inaccessible records or hidden truth. Optional maps, diagrams and timelines are derived from canonical records.

## 28. Notifications and reporting

BP-41 owns notification delivery and report presentation. BP-15 emits authorised case events and data contracts; it does not bypass notification permissions. Notifications freeze while the game is paused. Reports identify as-of simulation time, source records, version and uncertainty. Restricted fields and hidden truth are filtered before rendering, not merely hidden in the interface.

## 29. Failure handling and transaction boundaries

Case creation, state transition, ownership transfer, referral, merge and split are transactional multi-record operations. On failure, no partial authoritative mutation remains. Use optimistic version checks or equivalent concurrency control. Stale writes are rejected or reconciled without silent last-write-wins loss. Retry operations are idempotent. Orphan links and duplicate transition events are prohibited.

## 30. Inputs, outputs and event contracts

Inputs: authorised case request; incident/discovery/referral references; canonical identity and entity IDs; BP-13 taxonomy IDs; ownership/command decisions; source-record references; BP-42 access decision; simulation timestamp. Outputs: case ID; case state/ownership events; typed relationship/link events; review/referral/closure/reopening events; authorised case-list/detail projections; notifications requested through BP-41; audit and persistence events for BP-38/BP-39. Every output carries provenance, version and access classification.

## 31. Dependencies and interface ownership

Required dependencies: BP-01 canon; BP-02 geography; BP-03 population/person identity; BP-04 businesses/property; BP-05/BP-06/BP-08 police authority/personnel/deployment; BP-11 communications; BP-12 incidents; BP-13 taxonomy; BP-14 occurrence surfacing; BP-16 investigations; BP-17/BP-18 participants; BP-19 interviews; BP-20 surveillance; BP-21 intelligence; BP-22 scenes; BP-23 evidence; BP-24 forensics; BP-27/BP-28 legal outcomes; BP-30 governance; BP-35 engine; BP-37 time; BP-38 records; BP-39 persistence; BP-40 interface; BP-41 reporting; BP-42 security; BP-43 QA; BP-44 change control. BP-15 owns only case identity/lifecycle and case-level relationships.

## 32. Acceptance tests

The following acceptance tests are required. They are design criteria, not evidence of execution.

## 33. Edge cases and failure scenarios

The following scenarios must be explicitly covered in implementation and regression testing.

### Source traceability

| Source requirement/test | BP-15 obligation |
|---|---|
| S04.R03 | Case-linked people use the permanent person-promotion rule; identity remains BP-03-owned. |
| S07.R03 | Business, premises, access, records and witness links are referenced by canonical IDs. |
| S29.R01 | Case records accept broad crime/non-crime incident taxonomy references while incident lifecycle remains BP-12-owned. |
| S29.R03 | Case management supports downstream legal/court links without taking over their ownership. |
| S30.R01 | Stable case IDs, ownership, classification, status, objectives, actions, decisions, reviews, deadlines, linked incidents and closure reasons. |
| S30.R02 | Concurrent investigations, cold cases, linked series, referrals and reopened cases. |
| S30.R03 | Full case chronology and decision provenance. |
| S30.T01 | Every case state change has actor, time, reason and evidence/source reference. |
| S31.R01 | Typed person-role links preserve contact, vulnerability, risk, statements, availability and procedural status through BP-17/BP-18. |
| S31.R02 | Role and classification semantics remain distinct from guilt and adjudicated outcomes. |
| S31.R03 | Relevant persons use BP-03 permanent promotion and stable identity. |
| S31.T01 | No person is guilty solely because of generated role or suspicion. |
| S38.R01 | Case links to charging, disclosure, prosecution, defence, hearings, evidence, rulings, verdicts, sentencing and appeals. |
| S38.R03 | Outcomes feed back as linked records without rewriting investigative history. |
| S38.T01 | Outcomes link to correct charges, defendants and evidence versions. |
| S45.R01–R03 | Optional case maps/diagrams/timelines are traceable derived views; text remains authoritative. |
| S46.R03–R04 | Canonical case records, immutable source events and derived views remain separate; persistence/recovery are BP-39-owned. |
| S48.R02 / S48.T01 | Hidden truth and restricted personal information are protected; unauthorised reads/writes are rejected and audited. |
| S43.R01, R04, R05; S43.T01–T02 | Naturalistic grounded text, no unsolicited investigative hints, structured canon changes and strict hidden-truth/knowledge boundaries. |

## 32. Acceptance tests

- [ ] **CM-001** — Create a stable, unique case ID on the first authorised case-creation transaction; never recycle it.
- [ ] **CM-002** — Reject duplicate case IDs and preserve uniqueness under concurrent case creation.
- [ ] **CM-003** — Require a valid case-creation basis and record the originating actor or automated process.
- [ ] **CM-004** — Permit case creation from one or more eligible incidents without changing source incident identity.
- [ ] **CM-005** — Permit a case to exist before an incident is formally linked when an authorised policy permits it.
- [ ] **CM-006** — Keep an incident and a case as distinct records with distinct lifecycles.
- [ ] **CM-007** — Support multiple cases arising from one incident when separate investigative ownership or scope is justified.
- [ ] **CM-008** — Support multiple incidents linked to one case without collapsing their individual chronology.
- [ ] **CM-009** — Validate every linked incident reference against the authoritative incident registry.
- [ ] **CM-010** — Preserve source incident descriptions and original caller claims unchanged when linked.
- [ ] **CM-011** — Maintain one authoritative case record and prevent competing duplicate master records.
- [ ] **CM-012** — Record case title, reference, classification, status, owner, command responsibility and creation basis.
- [ ] **CM-013** — Record the creating officer, creating unit or authorised system process.
- [ ] **CM-014** — Record creation time from simulation time, not wall-clock time.
- [ ] **CM-015** — Record the current case owner and every ownership transfer.
- [ ] **CM-016** — Require an authorised accepting owner when a case is transferred.
- [ ] **CM-017** — Record case supervisor and command authority independently from day-to-day case ownership.
- [ ] **CM-018** — Prevent a rank title alone from granting case access or command authority.
- [ ] **CM-019** — Enforce permissions separately for view, create, edit, assign, link, classify, restrict, close and reopen.
- [ ] **CM-020** — Record the reason and authority for every material permission override.
- [ ] **CM-021** — Support case categories and classifications sourced from BP-13 without redefining offence taxonomy.
- [ ] **CM-022** — Allow classification to be provisional, disputed, amended or undetermined without rewriting source facts.
- [ ] **CM-023** — Record the author, time, reason and prior value for every classification change.
- [ ] **CM-024** — Do not infer offender identity, guilt or evidential strength from a case classification.
- [ ] **CM-025** — Maintain case status as a controlled state machine with valid transitions.
- [ ] **CM-026** — Reject invalid state transitions and preserve the attempted action in an appropriate audit record.
- [ ] **CM-027** — Support new, triage, allocated, active, suspended, dormant, cold, review, referred, closed and reopened states where configured.
- [ ] **CM-028** — Distinguish suspended from dormant and cold; each state has explicit entry criteria and resumption rules.
- [ ] **CM-029** — Do not treat a closed case as deleted or erase its chronology.
- [ ] **CM-030** — Require an authorised closure decision and a recorded closure reason.
- [ ] **CM-031** — Allow closure with unresolved lines, unknown offender or unavailable evidence when the recorded rationale permits it.
- [ ] **CM-032** — Record outstanding actions and disposition at closure.
- [ ] **CM-033** — Reopening creates a new state transition and preserves the previous closure event and rationale.
- [ ] **CM-034** — Support repeated reopen/close cycles without overwriting earlier decisions.
- [ ] **CM-035** — Support cold-case status and review scheduling without automatic wall-clock progression.
- [ ] **CM-036** — Support referral to another unit, agency or fictional authority while preserving case identity and ownership history.
- [ ] **CM-037** — Record referral package contents, sender, recipient, authority, time and acknowledgement.
- [ ] **CM-038** — Support accepted, rejected, returned, pending and partially accepted referrals.
- [ ] **CM-039** — Preserve originating police case record when an external referral or prosecution process is created.
- [ ] **CM-040** — Support concurrent investigations with separate teams, permissions and workstreams under one case.
- [ ] **CM-041** — Support parallel workstreams without duplicate ownership of the authoritative case.
- [ ] **CM-042** — Record case objectives as authored operational goals, not system-generated investigative hints.
- [ ] **CM-043** — Record actions and decisions as attributable chronology entries, not mutable narrative summaries.
- [ ] **CM-044** — Allow action records to reference incidents, people, locations, exhibits, statements, intelligence and external records.
- [ ] **CM-045** — Validate every referenced entity and preserve the source record's own ownership.
- [ ] **CM-046** — Record action start, completion, cancellation, outcome and responsible actor where applicable.
- [ ] **CM-047** — Distinguish a proposed action from an authorised, commenced or completed action.
- [ ] **CM-048** — Record decisions with decision-maker, authority, time, rationale, information considered and resulting state.
- [ ] **CM-049** — Preserve dissent, supervisory review and superseded decisions without deleting history.
- [ ] **CM-050** — Support case reviews, review findings, directions and due dates as explicit records.
- [ ] **CM-051** — Do not generate a direction telling the player what to investigate next.
- [ ] **CM-052** — Record deadlines using simulation time and pause them whenever the simulation is paused or exited.
- [ ] **CM-053** — Do not allow wall-clock time to advance case deadlines while the player is outside the game.
- [ ] **CM-054** — Support linked series and related-case associations with typed relationship semantics.
- [ ] **CM-055** — Distinguish same-series, suspected-series, duplicate-report, common-incident, cross-reference and administrative-link relationships.
- [ ] **CM-056** — Record who created each case relationship, when and why.
- [ ] **CM-057** — Allow a relationship to be disputed, downgraded or severed without deleting its history.
- [ ] **CM-058** — Prevent a related-case link from automatically proving common authorship or offender identity.
- [ ] **CM-059** — Support duplicate-case detection as a review aid without automatic destructive merging.
- [ ] **CM-060** — Require authorised review before consolidating duplicate records.
- [ ] **CM-061** — Preserve all source identifiers, chronology and audit history during an approved merge or consolidation.
- [ ] **CM-062** — Support split of a case into distinct cases where scope or governance requires it, preserving cross-reference history.
- [ ] **CM-063** — Record the authority, rationale and mapping of records during a split.
- [ ] **CM-064** — Support case priority and risk assessment as configurable operational values, distinct from offence severity.
- [ ] **CM-065** — Record priority changes and their rationale, including resource or safeguarding reasons.
- [ ] **CM-066** — Do not use priority to alter hidden occurrence truth or select a culprit.
- [ ] **CM-067** — Support safeguarding flags and restricted handling without exposing sensitive details to unauthorised users.
- [ ] **CM-068** — Support victim and witness links through BP-17 and suspect/offender links through BP-18.
- [ ] **CM-069** — Do not duplicate authoritative person identity or life records inside the case record.
- [ ] **CM-070** — Promote materially connected persons through BP-03 and preserve permanent full-detail status.
- [ ] **CM-071** — Preserve role uncertainty; victim, witness, suspect, person of interest and offender are not interchangeable.
- [ ] **CM-072** — Do not treat suspicion, allegation, intelligence or case association as proof of guilt.
- [ ] **CM-073** — Support unknown, unidentified, deceased and multiple affected-person situations without fabricated identities.
- [ ] **CM-074** — Support victimless, organisation-level and property-only cases where appropriate.
- [ ] **CM-075** — Support business, premises, property, vehicle and organisation links by canonical identifiers.
- [ ] **CM-076** — Preserve time-valid relationships between people, businesses, properties and cases.
- [ ] **CM-077** — Support case-linked maps, diagrams, timelines and reports as optional views derived from canonical records.
- [ ] **CM-078** — Ensure optional visuals do not become an independent source of case truth.
- [ ] **CM-079** — Support case-linked evidence references without taking over exhibit custody or continuity.
- [ ] **CM-080** — Preserve BP-23 as owner of exhibit identity, continuity, location and status.
- [ ] **CM-081** — Support forensic report references while BP-24 remains owner of methods, raw results and interpretation.
- [ ] **CM-082** — Support interview and statement references while BP-19 remains owner of interview records.
- [ ] **CM-083** — Support intelligence references while BP-21 remains owner of intelligence lifecycle and confidence.
- [ ] **CM-084** — Support surveillance references while BP-20 remains owner of surveillance sources and collection.
- [ ] **CM-085** — Support legal/prosecution/court references while BP-27 and BP-28 own their respective processes.
- [ ] **CM-086** — Preserve the distinction between case allegation, investigative hypothesis, evidence, expert interpretation and adjudicated outcome.
- [ ] **CM-087** — Record court and prosecution outcomes as linked downstream records without rewriting investigative history.
- [ ] **CM-088** — Support case management for investigations that remain unresolved indefinitely.
- [ ] **CM-089** — Support cases with no suspect, no victim contact, no physical evidence or no immediate investigative action.
- [ ] **CM-090** — Support cases with many incidents, people, exhibits, agencies and concurrent workstreams.
- [ ] **CM-091** — Keep case chronology append-only for material events and corrections.
- [ ] **CM-092** — Correct erroneous data through versioned correction events rather than silent overwrite.
- [ ] **CM-093** — Record provenance for imported, transcribed, AI-generated and manually entered case content.
- [ ] **CM-094** — Require generated claims that alter canon to become structured, attributable records.
- [ ] **CM-095** — Keep AI-generated summaries subordinate to source records and identify their source set and generation version.
- [ ] **CM-096** — Prevent summaries from introducing facts absent from their source records.
- [ ] **CM-097** — Prevent hidden generator truth from appearing in case fields, IDs, tags, logs, metadata, exports or summaries.
- [ ] **CM-098** — Enforce the exact player reveal gate: hidden offender/accomplice identities are not disclosed unless the player enters exactly `bingo`.
- [ ] **CM-099** — Do not disclose hidden truth through error messages, search ordering, suggested links, completion status or record counts.
- [ ] **CM-100** — Do not provide unsolicited solution hints or tell the player what to investigate next.
- [ ] **CM-101** — Present available records and let the player determine investigative actions.
- [ ] **CM-102** — Ensure operational NPC knowledge is limited to information received, observed or legitimately accessed.
- [ ] **CM-103** — Ensure case ownership or supervisory access does not grant omniscient knowledge of hidden occurrence truth.
- [ ] **CM-104** — Freeze all case timers, review schedules, deadlines, automation and NPC case activity when the simulation is paused or exited.
- [ ] **CM-105** — Resume from the exact persisted simulation state without catch-up case events.
- [ ] **CM-106** — Ensure case creation, linking and state changes are transactionally consistent under failure.
- [ ] **CM-107** — Prevent partial case creation from leaving orphan links or inconsistent counters.
- [ ] **CM-108** — Enforce referential integrity for every person, incident, exhibit, unit, user and location reference.
- [ ] **CM-109** — Enforce the single-city Saltwater jurisdiction and reject external playable locations.
- [ ] **CM-110** — Ensure case-linked person creation respects the 10,000 living-person hard cap.
- [ ] **CM-111** — Count police personnel within the same population cap, never as an additional population.
- [ ] **CM-112** — Support at least 10,000 businesses as a world baseline without cloning business records into cases.
- [ ] **CM-113** — Keep case processing proportional and avoid requiring a full simulation of unrelated institutions.
- [ ] **CM-114** — Support compact textual case lists and detailed individual case records in the laptop-style interface.
- [ ] **CM-115** — Keep all essential case workflows operable through text-first commands and views.
- [ ] **CM-116** — Provide optional map/timeline/diagram views only when requested or materially useful.
- [ ] **CM-117** — Ensure every case acceptance test can be traced to a source requirement or governing invariant.
- [ ] **CM-118** — Record test execution evidence separately from specification status.
- [ ] **CM-119** — Do not mark implementation, testing or verification complete merely because this specification is committed.

## 33. Edge cases and failure scenarios

- [ ] **EC-001** — Case creation races produce one canonical ID and no duplicate master record.
- [ ] **EC-002** — Two incidents reported separately are later linked without losing either caller narrative.
- [ ] **EC-003** — One incident legitimately generates separate cases with different scope and ownership.
- [ ] **EC-004** — A single case spans several incident records across time and locations.
- [ ] **EC-005** — A case is opened before a suspect is identified and remains valid indefinitely.
- [ ] **EC-006** — A case is created from a delayed report long after the underlying occurrence.
- [ ] **EC-007** — A report is later found to be mistaken; case records preserve the report and correction.
- [ ] **EC-008** — A case classification changes after forensic results without rewriting original allegation.
- [ ] **EC-009** — A supervisor changes ownership while the original owner has an unsaved or pending action.
- [ ] **EC-010** — An owner becomes unavailable; reassignment preserves accountability and history.
- [ ] **EC-011** — Two units claim ownership; command authority resolves the conflict through a recorded decision.
- [ ] **EC-012** — A case is referred but the recipient does not acknowledge receipt.
- [ ] **EC-013** — A referral is rejected and returned with partial records.
- [ ] **EC-014** — A referred case retains a local record and subsequent updates are synchronised without overwriting provenance.
- [ ] **EC-015** — A case is closed with unknown offender and later receives a credible new lead.
- [ ] **EC-016** — A cold case is reviewed while simulation time is frozen.
- [ ] **EC-017** — A deadline expires only after simulation time advances in-game.
- [ ] **EC-018** — A case is reopened more than once after separate new developments.
- [ ] **EC-019** — Two cases appear duplicated but concern separate occurrences with similar descriptions.
- [ ] **EC-020** — Two duplicate records are merged after review; source IDs remain resolvable.
- [ ] **EC-021** — A large case is split into separate cases while retaining shared-series links.
- [ ] **EC-022** — A suspected series link is later disproved.
- [ ] **EC-023** — A series link spans different offence classifications but shares a validated common occurrence context.
- [ ] **EC-024** — A person is first a witness and later becomes a suspect; historical role records remain.
- [ ] **EC-025** — A person is named in error and later exonerated; prior association remains auditable.
- [ ] **EC-026** — A victim is unidentified and no synthetic person record is invented.
- [ ] **EC-027** — A deceased person is linked without increasing the living population count.
- [ ] **EC-028** — A business is the victim and no individual victim is required.
- [ ] **EC-029** — A person materially connected to the case is permanently promoted to full detail.
- [ ] **EC-030** — Population cap is reached when an additional materially relevant person is discovered; no 10,001st living person is created.
- [ ] **EC-031** — An officer is both case owner and witness; permissions and conflict review remain explicit.
- [ ] **EC-032** — A case supervisor lacks a specialist clearance required to view a restricted attachment.
- [ ] **EC-033** — An authorised override is used and fully audited.
- [ ] **EC-034** — A user attempts to infer hidden truth by sorting case IDs or examining metadata.
- [ ] **EC-035** — An AI summary tries to include a hidden perpetrator identity.
- [ ] **EC-036** — A generated notification leaks an undiscovered accomplice.
- [ ] **EC-037** — A search result exposes a hidden-truth relationship through ranking or snippets.
- [ ] **EC-038** — A case export includes restricted data or hidden truth and must be filtered.
- [ ] **EC-039** — A player types `Bingo`, `bingo ` or `BINGO`; none satisfies the exact trigger.
- [ ] **EC-040** — The player enters exactly `bingo`; reveal policy is applied only to the permitted reveal channel.
- [ ] **EC-041** — A simulation restart restores case state without advancing deadlines.
- [ ] **EC-042** — A database failure occurs between case creation and incident linking; transaction rolls back cleanly.
- [ ] **EC-043** — A stale client submits a state transition based on an old version.
- [ ] **EC-044** — Two authorised actors update different fields concurrently; no unrelated change is lost.
- [ ] **EC-045** — A correction is entered after court outcome; historical outcome remains intact.
- [ ] **EC-046** — A court acquittal does not erase the case, evidence or original suspicion history.
- [ ] **EC-047** — A prosecution referral is withdrawn and the investigation record remains.
- [ ] **EC-048** — A case includes physical, digital, documentary and testimonial exhibits with BP-23 ownership.
- [ ] **EC-049** — A visual diagram is regenerated after a canonical location correction and remains traceable.
- [ ] **EC-050** — A map renderer is unavailable; textual case records remain fully usable.
- [ ] **EC-051** — A case references an external off-map supply chain only as contextual dependency, not playable geography.
- [ ] **EC-052** — An unrelated organisation or person is not promoted merely because a broad event exists nearby.
- [ ] **EC-053** — A case action is proposed but never authorised; it is not represented as completed.
- [ ] **EC-054** — A case contains contradictory witness accounts; the system preserves both without choosing truth.
- [ ] **EC-055** — A summary omits uncertainty or overstates an allegation; source records remain authoritative.
- [ ] **EC-056** — A case is administratively closed while an external legal process remains pending.
- [ ] **EC-057** — A case remains active while an associated court process has concluded.
- [ ] **EC-058** — A case has no linked incident because the initial basis is a direct discovery or authorised proactive activity.
- [ ] **EC-059** — A case has multiple responsible agencies but only one authoritative police case identity.
- [ ] **EC-060** — A user with read access attempts a prohibited edit or closure.
- [ ] **EC-061** — A person changes name, address or employment; case links remain stable by person ID.
- [ ] **EC-062** — A business changes operator or closes; historical case references remain valid.
- [ ] **EC-063** — A property changes tenancy; historical occupancy at event time remains retrievable.
- [ ] **EC-064** — A case has events from different simulation dates; chronology uses canonical simulation time.
- [ ] **EC-065** — A case action is entered out of chronological order; event time and recording time remain distinct.
- [ ] **EC-066** — A retrospective correction is made by an authorised reviewer with reason and provenance.
- [ ] **EC-067** — A case contains hundreds of linked records; pagination and retrieval do not alter identity or chronology.
- [ ] **EC-068** — A case is reopened after an approved merge; lineage remains intact.
- [ ] **EC-069** — A case merge is attempted across incompatible jurisdiction or security boundaries; it is rejected or explicitly referred.
- [ ] **EC-070** — A malicious or malformed case title attempts to inject commands or alter hidden fields.
- [ ] **EC-071** — A user attempts to create a case referencing an unknown person or incident ID.
- [ ] **EC-072** — A user attempts to link a person to a role implying guilt without authorised role basis.
- [ ] **EC-073** — An incident's classification is revised after case creation; case history records both versions.
- [ ] **EC-074** — A case is linked to a generated occurrence before police discovery; no player-visible case appears prematurely.
- [ ] **EC-075** — A discovered event becomes an operational incident and later a case through distinct recorded transitions.
- [ ] **EC-076** — NPC action is paused mid-case; no action or deadline progresses outside active simulation.
- [ ] **EC-077** — An automated review is due while the game is closed; it remains pending until simulation resumes.
- [ ] **EC-078** — An AI process lacks permission to access restricted records; no inference from hidden fields is allowed.
- [ ] **EC-079** — A system diagnostic includes identifiers but not hidden offender identity or restricted personal data.
- [ ] **EC-080** — A case record is restored from backup; all cross-references and audit chains reconcile.
- [ ] **EC-081** — A backup restore replays immutable events without duplicating case state transitions.
- [ ] **EC-082** — A test fixture is deterministic but its seed and hidden truth are not exposed in player-facing output.
- [ ] **EC-083** — A case is associated with a non-crime incident and is not incorrectly forced into an offence category.
- [ ] **EC-084** — A case is linked to a false report; the original report and its outcome remain distinguishable.
- [ ] **EC-085** — A multi-victim event creates appropriate person-role links without assuming identical needs or accounts.
- [ ] **EC-086** — A case with no immediate action remains visible according to its status and access rules.
- [ ] **EC-087** — A case is archived or retained under policy without deleting the authoritative record.
- [ ] **EC-088** — A case has no meaningful investigative owner during a controlled triage interval; temporary custody is explicit.
- [ ] **EC-089** — A case ownership transfer fails due to permission; prior owner remains authoritative.
- [ ] **EC-090** — A case is restricted after sensitive information emerges; access changes are versioned and audited.
- [ ] **EC-091** — A case is de-restricted after review; prior restricted period and access history remain.
- [ ] **EC-092** — A system attempts to change case status based solely on an AI confidence score; transition is rejected.
- [ ] **EC-093** — A case action references a superseded exhibit version; source version remains identifiable.
- [ ] **EC-094** — A cross-case relationship is visible only to users authorised for both records or approved disclosure.
- [ ] **EC-095** — A case notification is queued during pause; it is not delivered until simulation resumes.
- [ ] **EC-096** — A case list count excludes inaccessible restricted records without revealing their existence improperly.
- [ ] **EC-097** — A text command is ambiguous; system requests clarification rather than choosing a destructive action.
- [ ] **EC-098** — A user requests a case summary; it cites canonical records and preserves uncertainty.
- [ ] **EC-099** — A case is created by an automated process; initiating rule, source event and software version are recorded.
- [ ] **EC-100** — A generated case has an impossible chronology; validation rejects it before commit.
- [ ] **EC-101** — A case is linked to a person outside Saltwater; external person is contextual only unless canon explicitly permits a non-resident reference.
- [ ] **EC-102** — A case is linked to a person whose status is deceased; historical role and event-time status remain valid.
- [ ] **EC-103** — A case action occurs during an active major incident; command handoff is recorded.
- [ ] **EC-104** — A case receives an oversight complaint; complaint process remains owned by its designated division.
- [ ] **EC-105** — A case has an attached report version replaced by correction; both versions remain retrievable.
- [ ] **EC-106** — A case is transferred between shifts; handover includes outstanding actions and accepted responsibility.
- [ ] **EC-107** — A player leaves during a case state change; transaction either commits fully or not at all.
- [ ] **EC-108** — A hidden perpetrator's identity is accidentally included in a diagnostic; the output path is blocked and incident audited.
- [ ] **EC-109** — A case's linked series is large; traversal is bounded and does not imply common guilt.
- [ ] **EC-110** — A case's legal status changes; investigative status and chronology remain separately represented.
- [ ] **EC-111** — A case is closed after referral; the reason distinguishes referral from solved or adjudicated outcome.
- [ ] **EC-112** — A case is reopened due to new evidence; the new evidence retains its own source and custody history.
- [ ] **EC-113** — A case is found to be outside jurisdiction; it is referred or recorded as out-of-scope without expanding Saltwater.
- [ ] **EC-114** — A case record references a map location deleted from current active map; historical spatial identity remains resolvable.

## 34. Open decisions (must not be silently guessed)

- Exact case-reference display format and any human-readable check digit.
- Full case-state transition matrix and which transitions require supervisory approval.
- Case priority bands, review intervals and escalation thresholds.
- Case retention, archival, destruction and legal-hold periods under the fictional canon.
- Exact role/clearance matrix and conflict-of-interest rules.
- Which source event types may create cases automatically versus require officer registration.
- Duplicate-detection thresholds and authorised merge/split roles.
- Referral acceptance timeouts and interagency acknowledgement policy.
- Whether a case may have co-owners, and exact limits for concurrent accountable owners.
- Case-list visibility/counting rules for restricted records.
- Exact report templates, required metadata and redaction profiles.
- Which case status labels are exposed in the player interface versus internal workflow.
- The exact scope of the `bingo` reveal channel and its interaction with saved-game/session state.
- Case-level risk/priority scoring model and whether any score is manual, rule-based or advisory.

These decisions require later canon/policy resolution. Until then, implementations must use explicit configuration and fail safely rather than inventing defaults.

## 35. Completion and evidence gates

1. Every source mapping above is incorporated into BP-15 and reconciled against the original JSON wording.
2. BP-15 ownership boundaries are reconciled with BP-12, BP-13, BP-16–BP-28, BP-30, BP-38–BP-42.
3. All acceptance tests are implemented as executable or reproducible checks and have recorded results.
4. Edge cases are represented in regression tests, including concurrency, pause/resume, population cap, restricted records and hidden-truth adversarial leakage.
5. Case identity, lifecycle, links, chronology, permissions, provenance and recovery are verified against authoritative records.
6. No Neon writes occur until the user explicitly authorises a measured deployment plan; blueprint commits alone do not authorise data changes.

**Current status:** `DESIGNED_DRAFT`. This document is a specification draft only. It is not implementation, test execution, user approval or verification.
