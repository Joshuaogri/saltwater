# BP-40 — Interface

**Project:** Saltwater  
**Division:** BP-40 of the fixed 44-division structure  
**Version:** 1.0  
**Specification:** DESIGNED_DRAFT — review/approval pending  
**Implementation / test execution / verification:** NOT_STARTED  
**Primary experience:** Laptop-style, text-first individual-officer police simulation.  
**Write restriction:** This specification authorises no Neon write, migration, seed, import, bulk operation or production configuration change.

## 1. Purpose

BP-40 defines the complete player-facing and authorised operator-facing interface: navigation, command interaction, record views, search, workflow presentation, optional maps/diagrams, feedback, error handling, notification/report presentation, observability and accessibility. The interface is the player's operational window into Saltwater's persistent police simulation. It presents, queries and submits authorised actions to owning systems; it does not own domain facts, adjudicate outcomes, invent records or silently mutate authoritative data.

## 2. Binding principles

1. Text is permanent and primary; every essential action remains usable through text.
2. Laptop-style navigation, workspaces, records, commands and status form a practical police workstation.
3. The player controls investigative decisions; no auto-solving, steering to culprits or forced actions.
4. Hidden world truth, NPC knowledge and player-visible information remain distinct. Exact bingo is the only reveal trigger.
5. BP-40 displays domain records; owning divisions control meaning, lifecycle and mutation.
6. Original records remain distinct from summaries, AI text, visuals and derived views.
7. Permissions apply before presentation, including counts, snippets, previews, maps and notifications.
8. Never claim an action, write, connection, result or health state without confirmation.
9. Preserve narrative, uncertainty, provenance, chronology, names and source wording.
10. Graphics are optional and never replace text or authoritative source records.

## 3. Scope and exclusions

**Included:** interface shell; navigation; command catalogue/parser; player and officer workflows; search/filter/pagination; record views; case/incident/patrol/dispatch/personnel/evidence/legal workspaces; optional visuals; notification/report presentation; privacy/redaction/export; accessibility; errors; operator observability.

**Excluded:** domain truth/lifecycle; crime generation and NPC decisions; schema/transactions/persistence/recovery; security policy ownership; notification/report generation; independent test governance; configuration/change approval.

## 4. User, persona and session model

The interface distinguishes player, officer persona, administrator, operator and system/service identity as configured by BP-42. The chosen officer is the gameplay persona. Rank, position, authority, grade, clearance, qualification, posting and deployment remain separate facts owned by police divisions. A session records identity, authentication, active persona, permission context, environment, expiry and revocation. Role/persona/permission changes invalidate stale authorisation and protected caches. Technical access to a workspace never implies authority to read every record or perform every action.

## 5. Information architecture

Logical workspaces include Home/shift desk; Operations; Cases; People; Evidence/Scenes; Department; Legal/Custody; Resources/Finance; Reports/Notifications; and System Status. These are logical areas, not a requirement for a separate page per area. Keep navigation compact, predictable and free of duplicated domain content. Every view identifies workspace, selected record, owning domain and available authorised actions.

## 6. Command and action contract

Every command defines stable identifier/name, purpose, owner, arguments, validation, read-only/mutating classification, permissions, preconditions, confirmation/cancellation, idempotency, output schema, source references and audit attribution. The parser distinguishes unknown command, malformed syntax, missing argument, invalid value, ambiguous target, inaccessible target, failed precondition, denied permission, no-op, pending, partial completion and confirmed success. A timeout or error is not proof of success. Read/search/inspect are non-mutating. Mutating commands call the owning domain service and cannot bypass its rules.

## 7. Search, navigation and record views

Search supports canonical IDs, names, aliases and domain terms, distinguishing exact, partial, historical and uncertain matches. Permissions apply before result counts, ranking, snippets or previews. Filters and sorting are explicit; pagination is bounded and stable. Record views show stable IDs and authorised provenance, author, recorded/effective time, status and uncertainty. Original source, derived summary, AI narrative, correction and superseded version remain distinct. Long records are complete or clearly marked partial with a continuation route.

## 8. Domain workflow ownership

BP-40 provides coherent workflows while preserving ownership: BP-02 geography; BP-03 people; BP-04 property/businesses; BP-05–08 police structure/personnel/career/deployment; BP-09–12 resources/patrol/communications/incidents; BP-13–16 crime/cases/investigation; BP-17–24 participants/interviews/surveillance/intelligence/scenes/evidence/forensics; BP-25–29 arrest/custody/legal/courts/corrections; BP-30–34 governance/standards/training/HR/finance; BP-35–39 engine/relationships/time/records/persistence; BP-41 reports; BP-42 security; BP-43 quality; BP-44 change. Cross-domain links use canonical IDs and never create duplicate entities or transactions.

## 9. Casework and player agency

Casework distinguishes case lifecycle, investigation plans, leads, hypotheses, interviews, surveillance, intelligence, scenes, exhibits, forensic results, participants, legal actions and adjudicated outcomes. Each item retains source and status. The interface never identifies hidden offenders before exact bingo; never leaks truth through search, counts, summaries, maps, visual labels, errors, notifications, exports or accessibility text; never provides unsolicited investigative hints; and never converts allegation, intelligence, hypothesis or association into fact. The player chooses actions.

## 10. Optional visual presentation

Maps, scene layouts, timelines, diagrams, charts and forensic visuals are optional. They use canonical BP-02 spatial data and domain-owned scene/evidence records. Each visual identifies source IDs, version and transformation metadata. Measured facts are distinguished from illustrative geometry; observed events from inferred chronology; original media from derivatives. Text remains authoritative. Missing, incomplete or contradictory visual capability falls back to complete text. Visuals never alter source records or forensic conclusions. Markers and annotations have equivalent text descriptions and permissions.

## 11. AI narrative and NPC knowledge

Generated text must match authorised records, character voice, uncertainty and knowledge boundaries. Summaries are labelled and linked to sources. Canon-changing generated claims are persisted as attributable structured events by the owning system. NPC-facing outputs include only information plausibly observed, received or lawfully accessed. Conflicting claims remain conflicting until authoritative correction.

## 12. Permissions, privacy and exports

BP-42 owns permission policy; BP-40 enforces it before every read, preview, command, search, visualisation, notification preview, export, copy or share. Access is record- and action-specific. Exports apply the same redaction and hidden-truth restrictions as on-screen views. Export actions identify scope and destination. Credentials and tokens never appear in output or logs. Logout, session expiry, persona change or permission revocation clears or revalidates protected caches.

## 13. Notifications, errors and honest status

BP-41 owns notification/report semantics and delivery; BP-40 presents them. Previews are permission-filtered and deduplicated. Errors distinguish rejected, failed, pending, partial, uncertain and confirmed outcomes. On uncertain network/database outcomes, reconcile operation status before retry. Do not claim Neon connectivity without a successful current connection test. Health indicators include source and observation time and distinguish measurement from estimates or stale readings.

## 14. Accessibility, input and continuity

All essential workflows support keyboard navigation and assistive technology. Colour is never the only status cue. Headings, labels, focus order and control names are meaningful. Confirmation, cancellation and error feedback are accessible. Input validation does not destructively truncate or silently substitute characters. International names, diacritics, punctuation and long IDs are preserved. Drafts are distinct from committed records and preserved across safe navigation where supported.

## 15. Simulation time and pause

Navigation, reading, search, refresh, rendering, pagination, opening records and viewing maps do not advance simulation time. No off-screen time passes when the player exits. Time advances only through explicit authorised actions governed by BP-35/BP-37. No notification timer, autosave, background refresh, animation or delayed response may trigger NPC/world activity. Real-world session expiry is separate from in-game time.

## 16. Operator visibility and performance

Authorised operator views may show service health, connection status, database size/growth, latency, errors, queue depth, failed events, backup/recovery status and environment identity. Every metric has source and observation time; estimates are labelled. Development, test and authoritative production are distinguishable. BP-40 consumes supported APIs/contracts and does not bypass BP-38. Use bounded pagination and permission-aware caches; repeated rendering does not duplicate events. Concurrent edits expose version conflicts.

## 17. Inputs, outputs and dependencies

**Inputs:** authenticated session/persona; permission context; canonical domain records; search parameters; player commands; operation status; spatial/evidence data; reports; verified health observations; approved configuration.

**Outputs:** rendered text/optional visuals; navigation state; validated player command requests; read/search requests; export requests; accessibility descriptions; honest status feedback; authorised operator views; attributable action metadata.

**Dependencies:** BP-01–BP-39 and BP-41–BP-44. BP-40 is not a substitute owner for any domain.

## 18. Acceptance tests

The following criteria define required coverage. They are design criteria only; none is claimed executed.

- UI-AT-001: Provide a laptop-style text-first interface with stable navigation, clear workspaces, selected-record context and authorised actions.
- UI-AT-002: Support individual-officer gameplay and recruit-start workflow when selected.
- UI-AT-003: Display player identity, officer persona, rank, position, authority, grade, clearance, qualifications, posting and assignment as distinct facts.
- UI-AT-004: Keep the one-city Saltwater setting explicit; do not imply additional playable cities or territories.
- UI-AT-005: Expose predictable navigation to operations, cases, people, evidence, scenes, department, legal, resources, reports and system status.
- UI-AT-006: Distinguish navigation, current workspace, selected record and contextual actions.
- UI-AT-007: Use compact metadata without replacing authoritative narrative, evidence, statements or chronology.
- UI-AT-008: Present long records completely through readable sections or pagination; never silently omit content.
- UI-AT-009: Adapt to desktop and laptop widths without losing text workflows.
- UI-AT-010: All essential controls work without graphics, hover, colour recognition or drag-and-drop.
- UI-AT-011: Optional graphics are additive and never block access to textual records.
- UI-AT-012: Keep navigation labels and command names stable and discoverable.
- UI-AT-011: Every command defines a stable identifier, purpose, owner, arguments, permissions, preconditions and output contract.
- UI-AT-012: Distinguish read-only commands from mutating commands.
- UI-AT-013: Parse unknown command, malformed syntax, missing argument, invalid value and ambiguous target as separate errors.
- UI-AT-014: Do not guess a destructive or ambiguous target.
- UI-AT-015: Search and inspect commands never mutate authoritative records.
- UI-AT-016: Mutating commands execute through the owning domain service and cannot bypass its invariants.
- UI-AT-017: Show intended target and material effect before ambiguous or consequential mutations.
- UI-AT-018: Provide explicit confirmation and cancellation where required.
- UI-AT-019: Preserve safe draft input when a user cancels or navigates away.
- UI-AT-020: Attribute every player action to active player identity and authority context.
- UI-AT-021: Distinguish rejected, failed, pending, partial, no-op and confirmed-success outcomes.
- UI-AT-022: Never claim success before the owning service confirms it.
- UI-AT-023: Reconcile uncertain write outcomes before retry to prevent duplicate actions.
- UI-AT-024: Repeated submission of an idempotent command cannot create duplicate records or events.
- UI-AT-021: Search canonical IDs, names, aliases and relevant domain terms.
- UI-AT-022: Distinguish exact match, partial match, alias, historical identity and uncertain association.
- UI-AT-023: Apply permissions before rendering search counts, titles, snippets, previews, ranking or results.
- UI-AT-024: Expose active filters, sort order and bounded pagination clearly.
- UI-AT-025: Pagination preserves stable ordering and indicates whether more results exist.
- UI-AT-026: Display stable identifiers and authorised source/provenance metadata.
- UI-AT-027: Distinguish original source, derived view, summary, generated narrative, correction and superseded version.
- UI-AT-028: Preserve author, recorded time, effective time, timezone and uncertainty where relevant.
- UI-AT-029: Long text is complete or explicitly marked partial with a continuation path.
- UI-AT-030: Derived summaries link to source records and never masquerade as original evidence.
- UI-AT-031: Do not convert allegation, intelligence, hypothesis or association into verified fact.
- UI-AT-032: Do not silently rewrite, normalise away or correct source wording.
- UI-AT-033: Cross-domain links use canonical IDs and handle merged, retired or superseded references.
- UI-AT-034: Concurrent edits expose version conflicts instead of silently overwriting newer data.
- UI-AT-031: Case views distinguish case lifecycle from investigation activity and outcomes.
- UI-AT-032: Investigation views present plans, leads, hypotheses and actions without recommending the next step.
- UI-AT-033: Participant views preserve separate victim, witness, suspect and offender roles across cases.
- UI-AT-034: Incident and dispatch views distinguish live operational state from later case records.
- UI-AT-035: Officer views distinguish rank, position, authority, grade, clearance, qualification and assignment.
- UI-AT-036: Career views show requirements and status without silently granting promotion or qualification.
- UI-AT-037: Roster views show assignment validity and effective periods without implying unauthorised powers.
- UI-AT-038: Interview views preserve original questions, answers, recording, transcript versions and adoption state.
- UI-AT-039: Surveillance and intelligence views distinguish source material, analysis, reliability, confidence and evidential status.
- UI-AT-040: Scene and evidence views preserve access, handling, measurements, custody and provenance.
- UI-AT-041: Arrest, custody, legal, court and corrections screens distinguish authoritative stages and owners.
- UI-AT-042: Personnel, complaint and professional-standards views enforce confidentiality and conflict restrictions.
- UI-AT-043: Resource and finance views distinguish estimate, commitment, invoice, payment, asset and inventory state.
- UI-AT-044: Cross-domain workflows never create duplicate people, cases, incidents, exhibits, organisations or transactions.
- UI-AT-041: Maps, layouts, timelines, charts and forensic visuals are optional views over canonical data.
- UI-AT-042: Every visual identifies the canonical source records and data version used to render it.
- UI-AT-043: Text/source records remain authoritative if a visual is unavailable, incomplete or inconsistent.
- UI-AT-044: Spatial views use BP-02 canonical spatial identifiers and never redefine locations or boundaries.
- UI-AT-045: Timelines distinguish event, effective, recorded and observed time, timezone and uncertainty.
- UI-AT-046: Scene diagrams distinguish measured geometry from illustrative geometry.
- UI-AT-047: Evidence images and derivatives link to original exhibit identity, provenance and transformation metadata.
- UI-AT-048: Visual markers, annotations and labels have equivalent textual descriptions.
- UI-AT-049: Visual rendering never alters source evidence, forensic results or court findings.
- UI-AT-050: Unavailable graphics degrade gracefully to complete textual presentation.
- UI-AT-051: Visuals apply the same permissions and hidden-truth protections as text.
- UI-AT-052: Player-requested visuals clearly distinguish source imagery from generated illustration.
- UI-AT-051: Check session, role and record-level permission before every read, search, preview, command, visualisation or export.
- UI-AT-052: Redact protected personal information before it reaches presentation or cache layers.
- UI-AT-053: Do not reveal protected record existence through counts, snippets or error messages unless authorised.
- UI-AT-054: Keep hidden offender truth out of search suggestions, summaries, map markers, notifications, exports and accessibility descriptions.
- UI-AT-055: Reveal hidden offender truth only under the exact bingo trigger defined by BP-01 and BP-42.
- UI-AT-056: NPC-facing outputs expose only information plausibly observed, received or lawfully accessed.
- UI-AT-057: Technical administrator status does not imply unrestricted domain access.
- UI-AT-058: Permission denial does not leak protected content.
- UI-AT-059: Credentials, tokens and connection strings never appear in interface output, logs or screenshots.
- UI-AT-060: Audit metadata is protected from unauthorised read or alteration.
- UI-AT-061: Exports, clipboard and share actions enforce the same permissions and redactions as the screen.
- UI-AT-062: Session, persona or permission changes invalidate protected cached content before further access.
- UI-AT-061: Present BP-41 notifications with source, event time and authorised action context.
- UI-AT-062: Notification previews are permission-filtered and do not disclose protected case truth.
- UI-AT-063: Deduplicate repeated delivery without changing the underlying source event.
- UI-AT-064: Read/unread state is interface metadata, not domain truth.
- UI-AT-065: Errors distinguish failure, partial completion, pending state, uncertain outcome and confirmed success.
- UI-AT-066: Error messages provide actionable correction information without revealing secrets or protected records.
- UI-AT-067: Transient database/network failure never produces a false success message.
- UI-AT-068: Reconcile uncertain write outcomes before permitting a retry.
- UI-AT-069: Long-running operations show truthful pending, completed, warning or failed states.
- UI-AT-070: Health indicators identify their source and observation time.
- UI-AT-071: Do not claim Neon connectivity without a successful current connection test.
- UI-AT-072: Warnings distinguish blocking constraints, advisory notices and informational status.
- UI-AT-071: Navigation, reading, search, refresh and rendering do not advance simulation time.
- UI-AT-072: No simulation time or NPC activity advances while the player is absent or the game is paused.
- UI-AT-073: Only explicit, authorised time-advancing actions can progress the simulation under BP-35/BP-37.
- UI-AT-074: Autosave, interface timers, notifications and background refresh cannot advance game time.
- UI-AT-075: Unsaved drafts are clearly distinguished from committed authoritative records.
- UI-AT-076: Preserve draft input across safe navigation or interruption where supported.
- UI-AT-077: After uncertain writes, reconcile state before retrying or presenting a committed record.
- UI-AT-078: Support keyboard navigation and assistive technologies for every essential workflow.
- UI-AT-079: Do not convey status by colour alone; provide text labels.
- UI-AT-080: Use meaningful headings, labels, focus order and control names.
- UI-AT-081: Provide accessible confirmation, cancellation and error feedback.
- UI-AT-082: Preserve international names, diacritics, punctuation and long identifiers losslessly.
- UI-AT-083: Validate input without destructive truncation or silent character substitution.
- UI-AT-084: Logout, session expiry or permission revocation clears or revalidates protected content.
- UI-AT-081: Generated prose agrees with authorised source records, character voice, uncertainty and NPC knowledge.
- UI-AT-082: Label generated summaries and retain links to their source records.
- UI-AT-083: Any AI-generated claim that changes canon is persisted as an attributable structured event by its owning system.
- UI-AT-084: AI output cannot silently overwrite source records or adjudicated outcomes.
- UI-AT-085: Do not reveal culprit, accomplice or perpetrator identities before the exact bingo trigger.
- UI-AT-086: Do not provide unsolicited solution hints or tell the player what to investigate next.
- UI-AT-087: Do not imply NPC knowledge without a plausible observation, communication or lawful access path.
- UI-AT-088: Generated visual captions obey the same permissions and hidden-truth rules as text.
- UI-AT-089: Conflicting source records remain visibly conflicting until authoritative correction.
- UI-AT-090: Uncertain, inferred and disputed information is labelled and never promoted to fact by presentation.
- UI-AT-091: Authorised operator views expose service health, errors, latency, queues, resource use and database observations.
- UI-AT-092: Metrics distinguish measured values, estimates and stale observations.
- UI-AT-093: Database size and growth views identify measurement time, scope and units.
- UI-AT-094: Failed events, stalled jobs and recovery actions are attributable and visible to authorised operators.
- UI-AT-095: Maintenance, migration and rollback status does not imply approval or completion.
- UI-AT-096: Development, test and authoritative production environments are visibly distinct.
- UI-AT-097: Test fixtures are labelled and cannot be mistaken for canonical simulation records.
- UI-AT-098: Telemetry and errors redact credentials and protected personal/case information.
- UI-AT-099: Health status is sourced from actual checks and never invented.
- UI-AT-100: Operator actions remain subject to BP-42 permissions and BP-44 change governance.
- UI-AT-091: Use supported APIs/data contracts and do not bypass BP-38 schema or transaction ownership.
- UI-AT-092: Repeated rendering of unchanged records does not duplicate stored narrative or domain events.
- UI-AT-093: Use bounded pagination rather than unbounded city-wide data retrieval.
- UI-AT-094: Retrieve long narrative and evidence metadata without loss or misleading partial display.
- UI-AT-095: Permission-aware caches are invalidated when source permissions or records change.
- UI-AT-096: Cached content cannot outlive revocation or expose data to a newly unauthorised session.
- UI-AT-097: Time-sensitive views show source observation time and do not imply freshness when stale.
- UI-AT-098: Interface integration tests cover successful, rejected, unauthorised and uncertain workflows.
- UI-AT-099: BP-40 owns presentation and workflow, not domain truth or lifecycle.
- UI-AT-100: BP-02 owns spatial identity; BP-35 simulation execution; BP-38 schemas; BP-39 recovery; BP-41 reports; BP-42 security; BP-43 tests; BP-44 change control.

## 19. Source traceability

The following requirements/tests are mapped to BP-40 by the authoritative 52→44 crosswalk. Wording is taken from the unchanged source JSON.

| Source ID | Source division | Original requirement/test wording |
|---|---|---|
| S02.R01 | Geography, land and spatial reference | Maintain canonical districts, neighbourhoods, zones, parcels, addresses, coordinates, boundaries, terrain, coastlines and land use. |
| S02.R02 | Geography, land and spatial reference | All places, routes, incidents and properties resolve to consistent spatial IDs. |
| S02.R03 | Geography, land and spatial reference | Support textual descriptions and optional map rendering. |
| S02.T01 | Geography, land and spatial reference | No duplicate or contradictory canonical locations. |
| S02.T02 | Geography, land and spatial reference | Every operational location is addressable and spatially related. |
| S43.R01 | AI generation, narrative and player agency | Generate detailed, varied, naturalistic text consistent with records, knowledge boundaries, character voice and uncertainty. |
| S43.R02 | AI generation, narrative and player agency | Separate hidden world truth from player-visible information and from NPC knowledge. |
| S43.R03 | AI generation, narrative and player agency | Never disclose culprit/accomplice/perpetrator identities or hidden solution unless the player types exactly 'bingo'. |
| S43.R04 | AI generation, narrative and player agency | Never provide unsolicited solution hints or tell the player what to investigate next; present available records and let the player decide. |
| S43.R05 | AI generation, narrative and player agency | All generated claims that alter canon must be persisted as structured events or records. |
| S43.T01 | AI generation, narrative and player agency | No hidden truth leaks before the exact reveal trigger. |
| S43.T02 | AI generation, narrative and player agency | NPC knowledge never exceeds their plausible information. |
| S44.R01 | Text interface, commands and player workflow | Provide a laptop-style, text-first interface with clear navigation, commands, records, status and contextual actions. |
| S44.R02 | Text interface, commands and player workflow | Support individual-officer gameplay, including recruit start where selected. |
| S44.R03 | Text interface, commands and player workflow | Keep prose and source records readable while using compact presentation for navigation and metadata. |
| S44.R04 | Text interface, commands and player workflow | No essential action depends on graphics. |
| S44.T01 | Text interface, commands and player workflow | All essential workflows are operable through text commands and views. |
| S45.R01 | Maps, diagrams and visual evidence | Provide optional maps, layouts, timelines, charts and forensic scene visuals when useful or requested. |
| S45.R02 | Maps, diagrams and visual evidence | Visuals must derive from canonical spatial/evidence data and never silently contradict text records. |
| S45.R03 | Maps, diagrams and visual evidence | Keep text as authoritative source. |
| S45.T01 | Maps, diagrams and visual evidence | Every visual can be traced to the underlying canonical records. |
| S46.R01 | Database, schemas and persistence | Use Neon PostgreSQL as the persistent database and GitHub as source control, specification and migration history; ChatGPT is the user-facing AI partner/interface. |
| S46.R02 | Database, schemas and persistence | Define canonical schemas, constraints, relationships, IDs, migrations, indexes and transaction boundaries. |
| S46.R03 | Database, schemas and persistence | Store detailed narrative losslessly; normalise shared facts, reference repeated entities and avoid duplicate payloads. |
| S46.R04 | Database, schemas and persistence | Separate immutable source records/events from derived views and summaries. |
| S46.R05 | Database, schemas and persistence | Never claim live database connectivity without a successful connection test. |
| S46.T01 | Database, schemas and persistence | Schema constraints enforce identity, referential integrity, population cap and valid lifecycle states. |
| S48.R01 | Security, permissions and information boundaries | Define user, player, officer, administrator and system roles; least privilege; secret handling; access checks and audit logs. |
| S48.R02 | Security, permissions and information boundaries | Protect hidden case truth and restricted personal information from player-facing leakage. |
| S48.R03 | Security, permissions and information boundaries | Keep credentials out of source control, narrative records and logs. |
| S48.T01 | Security, permissions and information boundaries | Unauthorised reads/writes are rejected and audited. |
| S51.R01 | Operations, observability and maintenance | Track service health, errors, latency, job queues, resource use, database size, failed events and recovery actions. |
| S51.R02 | Operations, observability and maintenance | Provide safe maintenance, migration, rollback and incident procedures. |
| S51.R03 | Operations, observability and maintenance | Separate development/test data from authoritative simulation data. |
| S51.T01 | Operations, observability and maintenance | Operational failures are detectable, attributable and recoverable. |

### Cross-cutting and governance traceability

| X07 | No hidden simulation time while player is out; pause/resume and deliberate time advancement are explicit. | BP-01,BP-35,BP-37,BP-38,BP-39,BP-40,BP-43 |
| X08 | Text-first operation; optional maps/graphics cannot be required and cannot contradict authoritative text/records. | BP-01,BP-02,BP-20,BP-22,BP-23,BP-24,BP-38,BP-40,BP-43 |
| C08 | `/canon/interface`: permanent text-first; detailed narrative/records/dialogue/evidence/chronology; visuals optional | BP-01,BP-40,BP-43 |
| P08 | `/principles/7`: player actions authoritative; no auto-solving or hidden-truth disclosure | BP-01,BP-16,BP-35,BP-40,BP-42 |
| M07 | `/out_of_scope/0..5`: second playable city; equal-depth non-police simulation; graphics prerequisite; unbounded population; unapproved Neon writes; invented completion status | BP-01,BP-02,BP-03,BP-04,BP-38,BP-40,BP-43,BP-44 |
| A09 | Visuals/timelines omitted case, incident, engine and reporting interfaces. | Expanded S45.R01. | BP-40 presents views; domain data remains authoritative. |
| A10 | Database architecture requirement omitted ChatGPT interface and connectivity/quality verification. | Expanded S46.R01. | BP-38 owns data; BP-39 persistence; BP-40 interface; BP-43 tests; BP-44 source/version governance. |
| A11 | Security roles and secret protection omitted player-facing enforcement and test coverage. | Expanded S48.R01–R03. | BP-42 owns policy; domain owners enforce; BP-40 applies presentation boundary; BP-43 verifies. |
| A12 | Operations/observability lacked operator-facing visibility. | Added BP-40 to S51.R01. | BP-41 reports/alerts; BP-40 displays; BP-43 tests. |

**Traceability count:** 35 distinct source requirement/test IDs. Mapping is not evidence of implementation or test execution.

## 20. Open design/configuration decisions

1. Final command grammar, names, aliases and help format.
2. Workspace layout and default home view.
3. Session authentication, persona switching and timeout under BP-42.
4. Search ranking, pagination defaults and maximum result sizes.
5. Draft/autosave semantics and reconciliation after uncertain writes.
6. Export formats, redaction templates and approved destinations.
7. Accessibility target and formal test matrix.
8. Supported optional visual formats and rendering capability.
9. Operator metrics, thresholds, refresh cadence and health-check sources.
10. Error taxonomy and user-facing wording.
11. AI summary labelling and source-link presentation.
12. Localisation policy, if any.
13. Offline/read-only behaviour during provider outage.
14. UI state clearing on logout, persona or permission change.
15. Exact BP-41 notification/report integration contracts.
16. Visual identity and design tokens.

## 21. Completion status

- Specification: DESIGNED_DRAFT; review/approval pending.
- Implementation: NOT_STARTED.
- Test execution: NOT_STARTED; listed criteria are not executed evidence.
- Verification: NOT_STARTED.
- Neon connectivity: no new connection test performed; no claim of live connectivity.
- Neon writes/configuration changes: none performed or authorised.
- Next division: BP-41 — Notifications and Reporting.