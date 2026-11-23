# BP-12 — Incident Management

**Project:** Saltwater — fictional sovereign city-state; one city, one jurisdiction  
**Blueprint division:** BP-12 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test:** NOT_STARTED | **Verification:** NOT_STARTED

## 1. Purpose

BP-12 defines the authoritative operational lifecycle of a police incident from first recognition or report through assessment, response coordination, active management, resolution, closure, reopening and linkage to downstream records. It provides the common incident record used by emergency communications, patrol, supervisors, specialist units, partner responders and later case systems.

An incident is an operationally managed occurrence, concern, request for police attendance, developing event or linked series of events. It is not automatically a crime, offence, case, investigation, emergency call or proven fact. An incident can be non-criminal, duplicate, mistaken, preventable, unresolved, multi-agency, multi-location, recurring or later reclassified. A single incident may generate multiple crime records or cases; multiple reports may refer to one incident; one call may concern several incidents.

The system must preserve the difference between a reported event, an operational assessment, a dispatched response, observations at scene, verified facts, analytical conclusions and later legal outcomes. It must remain usable during complex, long-running and multi-unit events without collapsing chronology, command, accountability or uncertainty.

## 2. Scope and boundaries

### 2.1 In scope
- Incident identity, record creation, classification, status and lifecycle.
- Intake from BP-11, patrol/officer-generated reports, partner agencies, public-facing channels and authorised system-generated events.
- Initial assessment, priority/severity, risk, urgency and reassessment.
- Incident location, time, occurrence window, geographic spread and location uncertainty.
- Incident ownership, responsibility, lead unit, supervisor and command arrangements.
- Dispatch/response coordination interfaces with BP-11, BP-08, BP-09 and BP-10.
- Attendance, scene arrival, operational updates, actions, handovers and resource requests.
- Multi-unit, multi-agency, multi-site, linked, recurring and major incidents.
- Welfare, safeguarding, medical, fire, public safety, traffic, infrastructure and environmental impacts as police operational concerns.
- Incident logs, event chronology, decisions, rationale, communications references and attachments.
- Resolution, closure, cancellation, duplicate handling, reopening and post-incident review triggers.
- Links to crime classifications, generated occurrences, cases, victims, witnesses, suspects, evidence, custody and legal processes without taking ownership of those records.
- Incident reports, dashboards, workload queues, maps and optional visualisations.
- Audit, access control, retention interfaces, corrections and data quality.

### 2.2 Out of scope and authoritative boundaries
- BP-11 owns emergency/non-emergency call intake, call-taker records, CAD call records, radio/channel infrastructure, dispatch communications and communication-centre workflow. BP-12 receives and references those records; it does not recreate or overwrite them.
- BP-08 owns unit establishment, assignment, eligibility, deployment and authoritative unit/personnel deployment status. BP-12 requests/records operational allocation outcomes but cannot make an ineligible or unavailable unit deployable.
- BP-09 owns police assets, equipment, vehicles, facilities, inventory and serviceability. BP-12 records resource requests and incident use references, not asset ownership or maintenance.
- BP-10 owns patrol and field activity, officer field observations, attendance activity and field decision records. BP-12 consumes linked operational events and coordinates incident-level status.
- BP-13 owns crime taxonomy, offence definitions and classification rules. BP-12 may hold a provisional incident category and a referenced classification outcome; it cannot invent offence definitions.
- BP-14 owns simulated occurrence/crime generation. BP-12 can receive generated event references and operationally manage the resulting incident; it must not alter generator truth or reveal hidden offender identities.
- BP-15 owns case records, case assignment, investigative lifecycle and case closure. BP-12 may create a case referral/link but does not become the case record.
- BP-16 owns investigative activity and plans; BP-17 victims/witnesses; BP-18 suspects/offenders; BP-19 interviews/interrogations; BP-20 surveillance; BP-21 intelligence; BP-22 scenes; BP-23 evidence; BP-24 forensic examinations.
- BP-25 owns arrests/warrants; BP-26 custody; BP-27 legal processes; BP-28 courts/outcomes; BP-29 corrections.
- BP-30 owns department policy, formal command delegation and governance. BP-31 owns professional standards/complaint investigations. BP-41 owns notification/report presentation services. BP-38 owns shared record conventions and authoritative record indexing; BP-39 persistence/recovery; BP-42 permissions; BP-43 testing; BP-44 controlled change.
- BP-02 owns canonical geography and spatial identifiers. BP-03 owns the population ledger and person identity/lifecycle. BP-04 owns property, premises, businesses, organisations and infrastructure actors. BP-36 owns relationship semantics. BP-37 owns the shared simulation clock and schedules. BP-35 owns simulation execution and causal event processing.

### 2.3 Ownership principle
BP-12 is the single authoritative owner of the police operational incident record and its incident-level lifecycle. It is not the universal owner of every fact, person, call, unit, crime, case, scene or item linked to it. Every linked record retains its originating domain, identifier, permissions, provenance and lifecycle. Cross-domain links are references, not duplicate copies of authority.

## 3. Core concepts and definitions

- **Incident:** A uniquely identified operational occurrence/concern managed by the police service.
- **Report:** A source submission or account that may describe, update or relate to an incident. A report is not itself proof.
- **Call:** A BP-11 communication record. One call may be linked to zero, one or several incidents.
- **Occurrence:** A simulated event produced or maintained by BP-14 or another authorised source. It may be linked to an incident.
- **Incident category:** Operational grouping used to route and manage work; distinct from formal crime/offence classification.
- **Priority:** Operational response urgency determined from current information and policy. Priority is not a measure of guilt or evidential strength.
- **Severity:** Assessed actual or potential impact. Severity and priority may differ.
- **Risk assessment:** A time-stamped, attributed evaluation of threats, vulnerability, likelihood, impact and uncertainty.
- **Incident owner:** The role/unit accountable for maintaining the incident record and ensuring operational coordination.
- **Lead unit:** The unit currently tasked with leading the police operational response.
- **Incident commander:** The person formally exercising incident command under the applicable delegation/policy. A lead unit or senior rank alone does not automatically confer command.
- **Scene/site:** A BP-22 or BP-04/BP-02 referenced location. An incident may have multiple sites and a site may relate to multiple incidents.
- **Resolution:** The operational state reached at the time; it does not necessarily mean the underlying cause is known or the matter is legally concluded.
- **Closure:** Administrative and operational completion of the incident record under closure criteria. It is not deletion and does not prevent a justified reopening.
- **Duplicate:** A separate intake/report record determined to refer to an already-existing incident; preserve the duplicate source and its disposition.
- **Linked incident:** A distinct incident connected by an explicit relationship such as same event, related occurrence, follow-on, common hazard or operational dependency. Similarity alone is insufficient to merge.

## 4. Record identity and data model

### 4.1 Incident identifier
Each incident receives a stable, unique, non-reusable identifier at creation. The identifier must be opaque or otherwise avoid encoding sensitive personal details, offence conclusions or hidden simulation state. It must remain unchanged through reassessment, reclassification, transfer, reopening and closure. A merge never reuses or deletes an identifier; the surviving/primary relationship and historical redirects are recorded.

### 4.2 Required record fields
An incident record must support, at minimum:

| Field group | Required content |
|---|---|
| Identity | Incident ID, record version, creation timestamp, creating source/actor, current status |
| Intake | Source type, source record ID, received timestamp, reporter reference if known, contactability/anonymous/withheld state |
| Description | Original reported description, current operational summary, language/communication needs where relevant |
| Classification | Initial category, current category, classification authority, confidence, effective time, change history |
| Time | Reported occurrence time/window, received time, event times, local display time and canonical stored time |
| Location | Canonical spatial reference, free-text location as received, location type, precision/confidence, multiple-site support |
| Assessment | Priority, severity, risk dimensions, rationale, assessor, assessment time, review trigger |
| Ownership | Owning function, incident owner, lead unit, supervisor, commander where appointed, effective intervals |
| Response | Linked CAD call(s), dispatch references, tasked units, attendance/arrival/departure events, response milestones |
| People | Person references and incident-specific roles, with no copied identity master data |
| Organisations | Partner agency/business/provider references and their incident roles |
| Actions | Ordered operational event log, decision records, task/request references and outcomes |
| Relationships | Duplicate, parent/child, related, follow-on, concurrent, multi-site and case/crime links |
| Resolution | Resolution code, narrative, unresolved elements, closure rationale, author and timestamps |
| Governance | Access classification, provenance, audit events, retention class reference, correction/reopen history |

Fields may be nullable where genuinely unknown. Unknown, not applicable, withheld, not yet assessed and unavailable are distinct states; empty values must not silently conflate them.

### 4.3 Append-only history
Material changes create attributable history entries. Current-state fields are projections of accepted events, not substitutes for history. Preserve original reported text and source payload references. Corrections are additive and must identify the author, time, reason, prior value and replacement value. No user, NPC or process may silently rewrite an original report, erase an earlier assessment or backdate an event.

### 4.4 Person and organisation references
Use canonical BP-03 person IDs and BP-04 organisation/business IDs. Record the person's role in this incident separately from their global identity or other roles. A caller is not automatically a victim, witness or suspect. A person present at a location is not automatically involved. A complainant is not automatically the victim. A suspect designation is owned by BP-18 and must not be inferred from incident participation.

### 4.5 Time and location
Store canonical timestamps according to BP-37. Retain source-stated local times, uncertainty, time zone/offset where applicable, and estimated time windows. Distinguish event time, report time, receipt time, record-entry time and effective time. Use BP-02 spatial IDs and preserve raw location descriptions. A location correction must not erase the original address or uncertainty.

## 5. Incident intake and creation

### 5.1 Permitted sources
An incident may originate from:
- a BP-11 call/CAD event or communication-centre referral;
- an officer's BP-10 field observation or report;
- a supervisor or authorised command instruction;
- a partner emergency service or public institution;
- a victim, witness, business, organisation or member of the public;
- an authorised referral from another police domain;
- a BP-14 generated occurrence or BP-35 system event;
- a follow-up report, discovered risk or delayed disclosure.

Every source must be identifiable as a source class even where the source person is anonymous, withheld or unknown. Automated generation must identify the originating process and event reference.

### 5.2 Creation rules
Create an incident when there is a police operational need to record, assess, coordinate, respond to or track an occurrence/concern. Do not require that a crime be suspected. Do not create a new incident merely because a second call, officer, unit or agency reports the same occurrence. Duplicate detection is a candidate-matching aid, not an automatic assertion of identity.

An intake may initially remain a pending/untriaged work item where local policy requires validation. It must not disappear from queues because information is incomplete. Urgent safety information must be escalated without waiting for complete data entry.

### 5.3 Duplicate matching and consolidation
Candidate matching may consider time window, location, event type, involved entities, call references and narrative similarity. Similarity scores only recommend review. An authorised operator or configured rule with explicit evidence may confirm a duplicate. Preserve:
- each original report/call/source record;
- the duplicate candidate and decision;
- the primary incident ID;
- rationale, decision-maker and time;
- all links and event chronology;
- any later reversal of the duplicate decision.

Do not merge incidents solely because they share an address, person, business, broad category or time period. Separate incidents at the same location may be unrelated.

### 5.4 Minimum intake data
The system should capture source, received time, reported event, known/estimated time, best available location, immediate threat/need, callback/contact state where available, and any urgent action already taken. Unknown values remain explicit. Data completeness must not block urgent response.

## 6. Assessment, categorisation and priority

### 6.1 Assessment dimensions
Assessment must support separate values for:
- operational category and subtype;
- urgency and response priority;
- actual and potential harm/severity;
- threat to life or immediate safety;
- vulnerability and safeguarding concerns;
- weapons, violence, coercion or other hazards when reported;
- number of people potentially affected;
- incident scale, spread and duration;
- environmental, infrastructure, transport or public-order disruption;
- evidential fragility or time-critical opportunity where relevant;
- uncertainty, source reliability and information gaps;
- required specialist capability and interagency support.

Do not collapse these into one opaque score. A numerical aid may support triage but must expose its inputs, version and limitations and never replace accountable assessment.

### 6.2 Priority
Priority is assigned under the approved operational policy owned by BP-30 and configured under BP-44. This specification does not invent final priority labels, response-time guarantees or numerical thresholds. The implementation must provide a configurable, versioned priority scheme with an explicit mapping to dispatch handling. It must distinguish immediate emergency, urgent, routine and deferred/non-attendance pathways if those are adopted by policy.

Priority must be reassessed when new information materially changes risk, harm, urgency, location, vulnerability, available resources or incident scope. Retain every previous priority, rationale and assessor. A reduction in priority requires a recorded rationale; it must not erase the original emergency assessment.

### 6.3 Severity and risk
Severity describes impact or potential impact; priority describes operational response urgency. A low-frequency but catastrophic risk may have high severity and require immediate action. A high-volume low-harm event may require coordinated management without being the highest individual priority. Risk assessments are time-bound snapshots and must not be treated as timeless facts.

### 6.4 Uncertainty and source quality
Store what is known, alleged, estimated, inferred, disputed, contradicted or unknown. Assess source reliability separately from content plausibility. Anonymous does not mean false; identifiable does not mean accurate. An inaccurate report may still have been made in good faith. Do not convert an uncorroborated report into a confirmed event through repeated copying.

## 7. Incident lifecycle and state machine

### 7.1 Lifecycle states
The state model must support at least these operational states, with local sub-statuses permitted through configuration:
1. **RECEIVED** — intake received and incident record created.
2. **AWAITING_TRIAGE** — awaiting assessment or validation; visible in a monitored queue.
3. **ASSESSED** — initial category, risk and priority recorded.
4. **ALLOCATED** — an owning function/lead or response task assigned.
5. **DISPATCHED** — response resource(s) tasked through BP-11/BP-08.
6. **RESPONDING** — one or more resources have acknowledged and are en route/engaged.
7. **ATTENDED** — an authorised responder has reported attendance at a relevant site.
8. **ACTIVE_MANAGEMENT** — incident is being actively managed, including multi-unit or command activity.
9. **MONITORING** — immediate response reduced but follow-up or monitoring remains necessary.
10. **RESOLVED** — operational objectives achieved or immediate incident condition ended, subject to closure review.
11. **CLOSED** — closure criteria met and record administratively closed.
12. **CANCELLED** — response/record cancelled with reason; retained for audit.
13. **DUPLICATE_LINKED** — confirmed duplicate linked to a primary incident; original record retained.
14. **REOPENED** — previously closed/resolved incident reactivated under an authorised decision.

The system may expose a simpler user-facing status while retaining the underlying detailed state and events.

### 7.2 Valid transitions
Transitions are event-driven and validated. Examples:
- RECEIVED → AWAITING_TRIAGE or ASSESSED.
- AWAITING_TRIAGE → ASSESSED, CANCELLED or DUPLICATE_LINKED.
- ASSESSED → ALLOCATED, MONITORING, RESOLVED or CANCELLED where justified.
- ALLOCATED → DISPATCHED, MONITORING or RESOLVED.
- DISPATCHED → RESPONDING, ATTENDED, ACTIVE_MANAGEMENT or CANCELLED.
- RESPONDING → ATTENDED, ACTIVE_MANAGEMENT, MONITORING or RESOLVED.
- ATTENDED ↔ ACTIVE_MANAGEMENT as activity evolves; ACTIVE_MANAGEMENT → MONITORING or RESOLVED.
- MONITORING → ACTIVE_MANAGEMENT, RESOLVED or CLOSED where closure conditions are met.
- RESOLVED → CLOSED or REOPENED.
- CLOSED → REOPENED only through an authorised reopening event.
- Any non-terminal state may be cancelled only where policy and actual operational facts support cancellation.
- DUPLICATE_LINKED may be reversed through a recorded unlink/reinstatement decision; it is not a deleted state.

A transition outside the configured graph must be rejected with a useful reason. A correction to a mistaken state is a new compensating event, not a history rewrite.

### 7.3 Terminal states and closure
CLOSED, CANCELLED and DUPLICATE_LINKED are administratively terminal for ordinary workflow but retain the ability for authorised correction/reopen/unlink operations. A record is never physically deleted as a normal lifecycle action. Closure requires:
- response and assigned tasks completed, cancelled or transferred with ownership recorded;
- immediate safety issues addressed or explicitly handed over;
- all attending units accounted for;
- required incident log and outcome fields completed or marked unknown/not applicable;
- outstanding risks and follow-up actions assigned;
- linked calls and partner handoffs reconciled;
- any mandatory supervisor review completed or explicitly pending under policy;
- closure reason and responsible actor recorded.

An unresolved crime does not prevent operational incident closure if the immediate operational incident is complete and the investigative work is properly referred. Conversely, a resolved event may remain open for necessary operational follow-up.

## 8. Ownership, supervision and command

### 8.1 Incident owner
Every active incident must have an accountable owning function or queue. A named individual owner is required where policy or risk demands it. Ownership cannot be left blank during transfer. A queue may own initial triage, but high-risk incidents require explicit human accountability.

### 8.2 Lead unit and supervisor
The lead unit is the operational unit coordinating assigned police activity. The supervising officer oversees work within their delegated authority. These are distinct from incident record ownership and formal incident command. Record effective start/end times for each assignment and handover.

### 8.3 Incident command
Command arrangements are activated according to scale, complexity, risk, duration, multi-agency needs and policy. Record commander identity, appointment authority, command level/function, start/end times, objectives, delegated responsibilities and handover. Seniority alone does not prove appointment. An acting commander must have a recorded delegation. Command decisions must be attributable and time-stamped.

### 8.4 Command levels and structure
Support configurable command structures without hard-coding unapproved titles, numeric thresholds or ranks. Permit strategic, tactical and operational coordination roles where the approved Saltwater doctrine adopts them. Each role must have defined remit, reporting line, decision limits and succession/handover. Command structures may scale up or down without losing prior command history.

### 8.5 Decision log
Material decisions record: decision ID; decision-maker; authority/delegation; time; information available at the time; options considered where material; decision; rationale; risk accepted; instructions issued; recipients; review trigger; and outcome. Later knowledge must not be retroactively attributed to an earlier decision-maker.

## 9. Response coordination and operational milestones

BP-12 coordinates the incident-level picture; dispatch and resource status remain authoritative in their owning domains.

### 9.1 Response tasks
A response task must identify the objective, priority, responsible unit/person, creation time, acceptance/acknowledgement, due/review point where applicable, status, dependencies, result and cancellation/transfer rationale. Tasks can include attendance, welfare checks, scene preservation, traffic control, evacuation support, public safety, information gathering, specialist attendance, partner liaison and follow-up.

### 9.2 Milestones
Record relevant milestones with source and confidence:
- report received;
- incident created and triaged;
- priority/risk assessed and changed;
- unit requested, selected, dispatched, acknowledged and en route;
- arrival/attendance at each site;
- command established/changed;
- specialist/partner service requested and arrived;
- hazard controlled or escalated;
- people located, assisted, evacuated or transferred;
- scene/site status changed;
- operational objectives completed;
- units released/returned to availability;
- incident resolved, reviewed and closed.

Do not infer arrival from dispatch, or attendance from GPS alone. A location telemetry signal may support but does not automatically prove an officer's physical attendance.

### 9.3 Resource requests
Requests for additional units, specialist capability, vehicles, equipment, facilities or other resources are routed to BP-11/BP-08/BP-09 as appropriate. Record requested capability, urgency, requester, reason, response, allocation outcome and any unmet requirement. BP-12 cannot silently reserve or issue an asset.

### 9.4 Arrival and non-arrival
Record actual reported arrival, source, time and site. If a unit cannot attend, is diverted, delayed, stood down or fails to acknowledge, retain that outcome and reassess risk/coverage. Do not show a task as completed merely because it was dispatched.

## 10. Multi-unit, multi-site and multi-agency incidents

### 10.1 Multiple units
One incident may have multiple assigned units with distinct roles, tasks, arrival/departure times, supervisors and outcomes. Maintain one incident-level chronology and each unit's own activity records. A unit's release does not close the incident.

### 10.2 Multiple sites
Support a primary location plus any number of linked sites within the single Saltwater city-state. Each site has a canonical BP-02 reference, site role, relevant time window, access/hazard notes and status. Do not create an external territory or off-map playable jurisdiction to accommodate an incident. Events outside Saltwater may be represented only as bounded external references/context under BP-01/BP-02 policy.

### 10.3 Partner agencies
Partner organisations are BP-04 entities. Record agency, named liaison/person reference where appropriate, requested/accepted role, information shared, command/coordination arrangement, attendance and handover. Do not assume that a partner agency has accepted a task merely because a request was sent. Police incident command does not automatically confer command over another organisation.

### 10.4 Major incidents
Support configurable major-incident designation based on policy-defined thresholds or authorised command decision. Record declaration authority, rationale, activation time, objectives, command structure, coordination cell, public information interface, resource demand, review intervals and stand-down decision. The exact thresholds, titles and doctrine remain policy/configuration decisions, not invented by this draft.

### 10.5 Incident linkage
Relationships may include same occurrence, follow-on, related event, common hazard, common location, suspected series, operational dependency, parent/child and split-from. Each relationship has direction where relevant, type, confidence, source, creator, time and rationale. A link does not prove common offender, cause or guilt.

## 11. Safety, safeguarding and specialist coordination

Incident assessment and management must support:
- immediate threats to life and serious injury;
- vulnerable people, children and adults needing support;
- missing or at-risk persons;
- domestic, sexual, hate-related or exploitation concerns as incident indicators without prematurely assigning legal classifications;
- medical emergencies and health-provider coordination;
- fire, hazardous environment and structural danger;
- traffic collision, road obstruction and transport disruption;
- utility, communications and essential-service outage;
- public disorder, crowd safety and major public events;
- environmental hazards, severe weather and natural events;
- animal-related hazards where relevant;
- welfare checks, death-related attendance and sudden/unexplained death referrals;
- specialist safeguarding, negotiator, forensic, technical or other capability requests.

Sensitive details must be access-controlled and shared only on a need-to-know basis. The incident record should hold the minimum operational summary needed by broad responders and point to restricted domain records for protected details. BP-17, BP-22, BP-23, BP-24 and BP-26 retain their specialised records.

## 12. Incident reports, event log and evidential integrity

### 12.1 Event log
The incident event log is chronological and append-only. Entries may include intake, updates, assessment, risk review, decision, command change, dispatch reference, arrival, task, communication reference, partner handoff, resource request, scene/site update, resolution, closure, reopening and correction.

Each event must carry event ID, incident ID, event type, effective timestamp, recorded timestamp, actor/source, source record reference, content, confidence/provenance, access classification and correlation/causation reference where available.

### 12.2 Narrative integrity
Keep source statements, officer observations, third-party accounts, system-generated facts, analytical summaries and command decisions distinguishable. A summary may condense but must not replace or misrepresent source material. Preserve original text and attachments under their owning record system.

### 12.3 Corrections and disputed entries
A person with authority may challenge an entry. Record the challenge, claimant, disputed item, grounds, reviewer, outcome and any annotation/correction. Do not silently remove disputed information. Corrected summaries must continue to expose the fact that an earlier version existed.

### 12.4 Evidence boundary
An incident log is not an evidence exhibit register. Potential evidential material must be referred to BP-22/BP-23 and preserve original source, collection, custody and integrity under those divisions. The incident can link to an exhibit or scene record but cannot certify its forensic integrity.

## 13. Crime, case and legal-domain referrals

### 13.1 Crime classification
An incident may be assessed as no crime apparent, possible crime, confirmed crime classification, non-criminal, public safety, administrative or undetermined. These are operational descriptions only. BP-13 owns formal taxonomy and classification. Record who made a provisional assessment and what information supported it.

### 13.2 Multiple crime records
One incident may contain multiple alleged offences or crime occurrences. One alleged offence may relate to multiple incident reports. Maintain explicit many-to-many links and distinguish alleged event counts from confirmed crime records. Never force one incident to equal one crime.

### 13.3 Case referral
Refer to BP-15 when investigative work meets configured criteria or an authorised decision requires case creation. Referral carries the incident reference, source chronology, relevant people/locations, risk, outstanding tasks and linked domain references. BP-15 decides case acceptance/creation and owns investigative lifecycle. Record referral, acceptance, rejection, return for information and case link. An incident may be closed while a linked case remains open.

### 13.4 Arrest/custody/legal links
Reference BP-25 arrest/warrant records, BP-26 custody records and BP-27 legal-process records. A police incident record must not substitute for arrest grounds, custody log, warrant authority, charge decision or court outcome. Link only the actual record and effective relationship.

## 14. Notifications, escalation and handover

### 14.1 Escalation triggers
Configurable triggers may include rising severity/priority, threat to life, multiple casualties, vulnerable persons, weapon/hazard report, spread to additional sites, resource shortfall, prolonged duration, major service outage, public-order impact, command request or partner-agency escalation. A trigger creates an alert/task for an authorised recipient; it does not silently change command or declare a major incident.

### 14.2 Handover
A handover records outgoing and incoming owners/commanders, effective time, current status, known facts and uncertainties, risks, objectives, units/sites, outstanding tasks, decisions, partner arrangements and acceptance. Responsibility remains with the outgoing owner until the receiving owner accepts or an authorised command process assigns it. A failed handover is visible and escalated.

### 14.3 Notifications
BP-41 delivers notifications. BP-12 supplies event, recipient role, urgency, access classification and correlation ID. Notification delivery does not itself prove that the recipient read or acted on it. Delivery failures remain visible to the owning queue.

## 15. NPC and simulation behaviour

### 15.1 Actors
Call-takers, dispatchers, officers, supervisors, commanders, partner responders, reporters and other relevant persons act according to their individual records, role, training, authority, knowledge, workload, current location, availability, relationships and access permissions. BP-12 must not simulate an actor acting on information they have not received or observed.

### 15.2 Operational realism
NPC behaviour may include delayed updates, incomplete records, disagreement, missed communications, competing priorities, workload pressure, mistaken categorisation, late escalation, resource shortages, conflicting accounts and handover gaps. Such behaviour must be causally plausible and leave records of consequential actions. Do not manufacture arbitrary failures solely to frustrate the player.

### 15.3 Player agency
The player controls their own officer's choices. The system presents the information available to that officer at the time. It must not reveal hidden offender identities, accomplices, generator truth or investigative solutions unless the player enters exactly `bingo`. Incident management screens and NPC updates must not leak concealed case truth through labels, hints, metadata, notifications or summaries.

### 15.4 Relevant-person promotion
Any person who becomes materially connected to an incident or related police activity is promoted under BP-03 to the required persistent individual simulation level and is never downgraded later. This applies to minor but material connections as well as central participants. Promotion must be idempotent and must not create duplicate person identities or exceed the global population cap.

## 16. Time, queues and causal execution

- BP-37 owns simulation time; BP-35 executes scheduled and event-driven work.
- All incident timestamps and deadlines use the shared time contract. No division may maintain a conflicting independent clock.
- When the player exits or the simulation is paused, simulation time does not advance. Incident queues, timers, dispatch escalation deadlines, NPC activity, response travel, notification schedules and automated transitions freeze with it.
- On resume, continue from the exact persisted state; do not simulate absence-time events or catch up elapsed wall-clock time.
- Within active play, events occur in causal order. Concurrent events require deterministic ordering/tie-breaking and preserve their original event times.
- A timer expiring may trigger a review/alert, not automatically prove an operational fact or change a legal classification.
- Repeated events must be idempotent by stable event/correlation key. Retry must not duplicate an incident, dispatch task, notification or handover.

## 17. Interfaces and event contracts

### 17.1 Inputs
BP-12 accepts validated references/events from:
- BP-11: call/CAD creation, call updates, dispatch outcomes, radio/communication references;
- BP-10: field observations, attendance, patrol activity, officer reports;
- BP-08: unit assignment/deployment eligibility and status;
- BP-09: resource availability and request outcomes;
- BP-14/BP-35: generated occurrences and simulation events;
- BP-04: organisation, premises, infrastructure and partner references;
- BP-02: spatial identities and topology;
- BP-03: person references and lifecycle/promotion events;
- BP-30: policy, command delegation and authorised decisions;
- BP-15 through BP-29: referrals and linked domain record events;
- BP-37: time and scheduling events.

Inputs must be schema-validated, source-attributed, versioned and idempotently processed.

### 17.2 Outputs
BP-12 publishes:
- incident-created/updated/status-transition events;
- triage, priority and risk review requests/results;
- incident-level task and resource requests;
- command/ownership/handover events;
- partner-agency coordination references;
- escalation and notification requests to BP-41;
- crime/case referral requests and accepted links;
- incident closure/reopen/duplicate-link events;
- reporting projections and audit references.

### 17.3 Event envelope
Every cross-domain event should include event ID, schema/version, event type, source domain and record ID, target/reference IDs, canonical event time, recorded time, correlation ID, idempotency key, actor/process, access classification and payload. Consumers must tolerate delayed, duplicated, reordered and rejected events. A rejected event must produce a visible, actionable error and not partially mutate the incident.

### 17.4 Transaction and consistency rules
Incident creation plus source linkage must be atomic or recoverably idempotent. State transition and audit event must commit together. Ownership transfer must never leave an unowned active incident. Cross-domain workflows use explicit pending/accepted/rejected states rather than pretending a remote action succeeded. Reconciliation detects missing links and stale projections without rewriting source records.

## 18. Permissions and access control

Permissions are enforced by BP-42. Support role-based and attribute-based restrictions for create, view, edit, assess, prioritise, assign, command, link, merge, close, reopen, export and audit. Access may depend on unit, role, incident assignment, sensitivity, geography, task and purpose.

- Emergency access may be available under a controlled break-glass process with reason, scope, duration, audit and post-event review.
- Restricted safeguarding, health, intelligence, witness-protection and other sensitive information must not be exposed to all incident viewers.
- A user may be permitted to add an observation but not alter the original caller account.
- A dispatcher may update dispatch-related status but not make a formal crime classification outside their authority.
- A commander may set operational objectives within delegation but may not rewrite source records or override another domain's record authority.
- Closure/reopening/duplicate confirmation and command appointment require configured permissions.
- Export and bulk search are separately controlled and audited.
- NPC access follows equivalent role/assignment/need-to-know rules; AI/system processes have explicit service identities and scoped permissions.

## 19. Reporting, search and operational views

Provide operationally useful views for:
- untriaged and awaiting-action incidents;
- active incidents by priority, severity, age, location and owning queue;
- incidents without accountable owner or current risk assessment;
- dispatched/attended incidents and units not yet accounted for;
- resource requests outstanding or unmet;
- major/multi-site/multi-agency incidents;
- incidents with overdue review or unresolved safety issues;
- handovers pending acceptance;
- closed, cancelled, duplicate and reopened incidents;
- case/crime referral outcomes;
- workload, response milestones and outcome trends.

Search must support incident ID, source/call ID, time range, category, status, location, linked record ID and authorised person/organisation references. Results must respect permissions and avoid exposing hidden truth. Aggregates must state their filters, time basis and exclusions. Optional maps and timelines are presentations of canonical records; text records remain complete and primary.

## 20. Error handling and degraded operation

Handle unavailable BP-11/BP-08/BP-09 services, communication loss, partial partner response, conflicting updates, stale unit status, duplicate delivery, clock/ordering anomalies, location ambiguity, invalid references, access denial and storage/retry failures.

- Preserve received messages in a durable pending queue where persistence is available.
- Mark data as pending/unconfirmed when authoritative confirmation has not arrived.
- Do not invent a successful dispatch, attendance, partner acceptance or resource allocation.
- Provide controlled manual recording with later reconciliation and attribution.
- Keep emergency response possible when optional fields or non-critical integrations fail.
- Prevent a partial failure from creating two authoritative incidents or losing the original source report.
- Display stale-data age and source; do not silently present stale state as current.
- Escalate unresolved failures to the owning queue and record their operational impact.

## 21. Retention, audit and recovery

BP-38 owns shared record conventions and BP-39 persistence/recovery. BP-12 records must be durably persisted with stable identity, ordered event history, source references, versioning, access logs and relationship integrity. Retention periods and lawful disposition rules are configurable policy decisions; this draft does not invent numeric retention periods.

Backups and recovery must restore incidents, event logs, source references, relationships and audit records consistently. Recovery must not replay non-idempotent dispatch or notification side effects. Any reconstructed projection must be reproducible from retained source events or explicitly marked as a recovery correction. No record is physically removed merely because an incident is closed, cancelled or duplicated.

## 22. Population, geography and scale constraints

- Saltwater remains one sovereign city-state, one city and one jurisdiction. BP-12 cannot create another city or playable territory.
- The global living-person cap is exactly 10,000. All people referenced by incidents are part of BP-03's one population ledger and counted once across all roles and domains.
- The 10,000-person cap is hard; incident creation, caller intake, NPC generation and relevant-person promotion must not bypass it. If a new person cannot be admitted under the cap, the system must follow BP-03's approved admission/replacement rules rather than silently exceed the limit.
- Maintain at least 10,000 businesses under BP-04; incident references do not create duplicate business records.
- Support high incident volume, large linked events, many reports and long-lived records through compact references and indexed projections, without deleting semantic detail.
- Police receives deep simulation; healthcare, fire, utilities, transport, civil services and other partners are represented proportionately, with sufficient operational detail to support realistic incidents and handoffs.

## 23. Acceptance criteria

The division is acceptable for implementation only when all criteria below are testable and evidenced:
1. Every incident has a stable, unique, non-reusable ID and append-only event history.
2. A call, report, occurrence, incident, crime record and case remain distinct record types with explicit links.
3. Multiple calls/reports can link to one incident without losing source identity.
4. One incident can link to multiple crime records and cases where appropriate.
5. Duplicate matching never silently merges records; decisions are attributable and reversible.
6. Initial and subsequent assessments preserve source, uncertainty, rationale and effective time.
7. Priority, severity and risk remain separate and reassessable.
8. State transitions follow the validated lifecycle and invalid transitions are rejected.
9. Active incidents always have an accountable owner/queue.
10. Command appointment, delegation and handover are explicit and time-bounded.
11. Dispatch, unit deployment, resource issue and partner acceptance are confirmed by their owning domains.
12. Attendance is not inferred solely from dispatch or telemetry.
13. Multi-unit, multi-site and multi-agency activity is supported without loss of chronology.
14. Safety and safeguarding information is appropriately restricted.
15. Incident logs preserve originals and distinguish allegations, observations, inferences and findings.
16. Evidence, case, crime, custody and legal records remain owned by their respective divisions.
17. Reopening, closure, cancellation and duplicate linking preserve history.
18. Notifications and escalation are idempotent and delivery/read states are distinct.
19. NPCs act only on information available to them and cannot leak concealed simulation truth.
20. Relevant-person promotion is permanent, idempotent and subject to the global cap.
21. Time freezes completely while the player is absent.
22. Cross-domain events are versioned, validated, traceable and recoverably processed.
23. Access controls and audit apply to sensitive reads, changes and exports.
24. Reports and visualisations are derived from canonical records and do not become competing sources of truth.
25. Backup/restore preserves identity, links, chronology and audit without repeating side effects.
26. The specification maps all assigned source requirements/tests and cross-cutting rules without changing the 44-division structure.

## 24. Acceptance test catalogue

Each test must be automated where feasible; tests requiring simulated human judgement must retain input scenario, expected policy outcome, evaluator and evidence. Tests are not passed merely because the code path executes.

| Test ID | Scenario | Expected result |
|---|---|---|
| IM-001 | Create an incident from a valid BP-11 call | One stable incident; source call preserved and linked |
| IM-002 | Retry the same intake event | Idempotent; no duplicate incident |
| IM-003 | Create incident from an officer observation without a call | Valid incident with officer source provenance |
| IM-004 | Create incident from a partner referral | Partner source and acceptance state preserved |
| IM-005 | Create incident from BP-14 occurrence | Occurrence reference linked; generator record unchanged |
| IM-006 | Intake lacks exact location | Record accepted with explicit uncertainty and triage task |
| IM-007 | Intake lacks reporter identity | Anonymous/unknown state represented without fabricated person |
| IM-008 | Two callers report same event | Candidate duplicate surfaced; sources remain distinct |
| IM-009 | Two unrelated events share address and time | No automatic merge |
| IM-010 | Confirm duplicate after review | Duplicate source retained and linked to primary |
| IM-011 | Reverse an incorrect duplicate decision | Both incidents restored with complete history |
| IM-012 | One call contains two unrelated occurrences | Multiple incident links permitted |
| IM-013 | Several calls refer to one incident | Many-to-one linkage preserved |
| IM-014 | One incident relates to two alleged crimes | Separate BP-13 records linked without conflation |
| IM-015 | Incident generates two cases | Both BP-15 case links retained |
| IM-016 | Reported time differs from received time | Separate timestamps retained |
| IM-017 | Approximate time window supplied | Uncertainty/window preserved |
| IM-018 | Location later corrected | Original description and correction history retained |
| IM-019 | Priority raised after new threat information | New assessment and rationale appended |
| IM-020 | Priority lowered after review | Earlier priority retained; reason and author required |
| IM-021 | Severity high but immediate urgency low | Separate values remain representable |
| IM-022 | Source credibility uncertain | Uncertainty recorded; report not silently rejected |
| IM-023 | Invalid state transition attempted | Rejected with no partial state mutation |
| IM-024 | Valid transition to dispatched | Transition occurs only with dispatch reference/outcome |
| IM-025 | Unit dispatched but has not acknowledged | Status does not falsely show responding |
| IM-026 | Unit acknowledges and reports en route | Responding milestone records source/time |
| IM-027 | GPS enters scene geofence without officer report | Telemetry alone does not assert attendance |
| IM-028 | Officer reports attendance | Attendance event records officer, site and time |
| IM-029 | One of three units is released | Incident remains active while other work remains |
| IM-030 | Active incident has no named owner | Queue owner remains accountable; high-risk policy escalates |
| IM-031 | Ownership transfer not accepted | Outgoing ownership remains or authorised assignment is explicit |
| IM-032 | Handover accepted | Both parties, content and effective time recorded |
| IM-033 | Commander appointed by authorised delegation | Appointment and remit recorded |
| IM-034 | Senior officer attempts command without delegation | Command authority not inferred from rank |
| IM-035 | Command changes during incident | Prior command interval preserved |
| IM-036 | Multi-site event spans several city locations | Sites linked using canonical BP-02 IDs |
| IM-037 | Attempt to create external playable site | Rejected under single-city canon |
| IM-038 | Partner agency request sent but not accepted | Pending state shown; no false acceptance |
| IM-039 | Partner accepts defined task | Acceptance and scope recorded |
| IM-040 | Partner agency exercises its own command | Police command record does not overwrite partner authority |
| IM-041 | Major incident declared | Authorised declaration, rationale and command record created |
| IM-042 | Major incident stood down | Stand-down decision recorded; incident remains open if needed |
| IM-043 | Resource request submitted | BP-09/BP-08 owns allocation outcome |
| IM-044 | Asset is unavailable | BP-12 does not mark asset allocated or serviceable |
| IM-045 | Safeguarding detail is restricted | Unauthorised viewer sees only permitted summary |
| IM-046 | User adds observation to caller account | Original caller account remains unchanged |
| IM-047 | Incident report contains allegation and officer observation | Provenance/type distinctions remain explicit |
| IM-048 | Incident log entry is corrected | Original entry retained with correction link |
| IM-049 | Potential exhibit identified | BP-23 referral/link created; incident log not treated as exhibit register |
| IM-050 | Case referral is rejected by BP-15 | Incident remains; rejection reason and follow-up recorded |
| IM-051 | Case accepted while incident resolved | Independent lifecycles maintained |
| IM-052 | Incident closed with outstanding task | Closure blocked or task explicitly transferred/cancelled |
| IM-053 | Closed incident receives new material information | Authorised reopening creates new event and active state |
| IM-054 | Incident cancelled after false alarm | Cancellation reason and source retained |
| IM-055 | Incident closed while crime remains unresolved | Closure permitted if operational criteria met; case remains open |
| IM-056 | Escalation threshold met | Alert/request generated to BP-41, not silent command transfer |
| IM-057 | Notification delivery fails | Failure visible; incident state not falsely updated |
| IM-058 | Notification retried | Idempotent delivery handling; no duplicate task |
| IM-059 | NPC dispatcher receives incomplete information | NPC action reflects only available information |
| IM-060 | Player views incident before investigative disclosure | Hidden offender identity and generator truth remain concealed |
| IM-061 | Relevant minor participant is connected | BP-03 promotion event created permanently |
| IM-062 | Person already promoted is connected to another incident | No duplicate identity or second population count |
| IM-063 | Population is at hard cap | No incident workflow creates an extra living person outside BP-03 rules |
| IM-064 | Player exits while an escalation timer is pending | Simulation time and timer freeze |
| IM-065 | Player resumes | Exact prior timer/state resumes; no absence-time events occur |
| IM-066 | Cross-domain event is delivered twice | Idempotent processing |
| IM-067 | Cross-domain event arrives out of order | Reconciliation preserves effective chronology and flags conflict |
| IM-068 | Referenced person/business/location ID is invalid | Event rejected or quarantined; no fabricated entity |
| IM-069 | Database write fails mid-transition | No partial state/audit inconsistency; recoverable retry |
| IM-070 | Backup restored | Incident IDs, history, links and access audit reconcile |
| IM-071 | Restore replays notification event | No duplicate external side effect |
| IM-072 | User without export permission attempts bulk export | Denied and audited |
| IM-073 | Search includes restricted incident | Results filtered by BP-42 permissions |
| IM-074 | Map view is unavailable | Text incident record remains complete and usable |
| IM-075 | Aggregate report spans a selected period | Filters, time basis and exclusions are explicit |
| IM-076 | More than one unit/site/agency reports simultaneous updates | Deterministic event ordering; all source times retained |
| IM-077 | Stale unit status is received | Staleness shown; availability not assumed current |
| IM-078 | Call intake integration is offline | Manual/pending intake preserves source and later reconciles |
| IM-079 | High-volume intake occurs | Queues remain ordered, searchable and durable without ID collision |
| IM-080 | Closed/cancelled/duplicate incident queried | Record remains retrievable subject to permissions |
| IM-081 | Person's role changes from reporter to witness | Separate role history; identity unchanged |
| IM-082 | Reporter is mistakenly labelled suspect | BP-18 ownership enforced; incident participation alone cannot assign suspect status |
| IM-083 | Same business appears in multiple incidents | One canonical BP-04 business ID referenced |
| IM-084 | Utility outage affects several incidents | Shared outage reference; each incident retains its own operational record |
| IM-085 | Incident review deadline expires during active play | Review alert generated according to policy |
| IM-086 | Review deadline would expire while player absent | No simulation-time advance or alert execution |
| IM-087 | Source narrative is summarised | Original retained and summary provenance linked |
| IM-088 | Contradictory witness reports arrive | Both preserved; contradiction is not silently resolved |
| IM-089 | Incident category changes after assessment | Versioned category change; formal crime taxonomy remains BP-13-owned |
| IM-090 | Two incident records are split after mistaken consolidation | New/retained IDs and complete relationship history preserved |
| IM-091 | One incident is related to another by suspected series | Link confidence and rationale recorded; no guilt inference |
| IM-092 | Break-glass access used | Reason, scope, duration and review audit captured |
| IM-093 | AI/system process updates incident | Service identity, scope, input provenance and output audit captured |
| IM-094 | Retention policy changes | BP-44-controlled change; existing record history remains governed |
| IM-095 | Incident is queried at an earlier historical time | Effective-dated state reconstructs correctly |
| IM-096 | Current summary differs from earlier version | Both versions/history are retrievable |
| IM-097 | Cross-domain owner rejects a malformed update | No false success; actionable error and source reference retained |
| IM-098 | Emergency response cannot wait for complete metadata | Response task can proceed with explicit missing fields |
| IM-099 | Incident is resolved but safeguarding follow-up remains | Monitoring/follow-up remains assigned; closure criteria enforced |
| IM-100 | Full lifecycle replay from event history | Deterministic current projection with no lost or duplicated events |

## 25. Edge cases and failure scenarios

1. Multiple callers independently report the same event with materially different descriptions.
2. A caller reports several events in one conversation, only some of which are connected.
3. A caller disconnects before providing a usable location.
4. A third party reports an incident but cannot identify the affected person.
5. Anonymous and withheld callers provide urgent information.
6. A caller deliberately or mistakenly supplies a false identity.
7. The report is malicious, mistaken, exaggerated, outdated or made in good faith but inaccurate.
8. A report is received long after the alleged occurrence.
9. Event time crosses midnight or spans several days.
10. Different sources use inconsistent clocks or local-time assumptions.
11. The reported location is ambiguous, misspelled, obsolete or not a canonical address.
12. One incident moves across multiple locations over time.
13. A single site contains multiple unrelated incidents.
14. A location is inaccessible, privately controlled, hazardous or incorrectly geocoded.
15. The incident is first reported as non-criminal and later appears potentially criminal.
16. A crime report is reclassified as non-criminal without erasing the original allegation.
17. Several crime categories may apply but BP-13 has not completed classification.
18. A generated occurrence contains concealed truth not available to the player or NPC responders.
19. A generated occurrence is cancelled or corrected by BP-14 after an incident has been opened.
20. Two incidents are mistakenly merged and later need to be separated.
21. Two incidents are mistakenly kept separate and later confirmed as one operational event.
22. Similar incidents are linked as a possible series but the connection is uncertain.
23. A person is reporter, victim, witness and employee in different contexts; roles must remain contextual.
24. A person is named in a report but identity matching is uncertain.
25. A person is already deceased or has permanently exited the population when a delayed report arrives.
26. A relevant person is discovered after the initial incident closure.
27. A relevant person promotion would collide with the population hard cap.
28. An officer is assigned but absent, suspended, off duty or otherwise not actually available.
29. Unit status changes between selection and dispatch.
30. A dispatched unit fails to acknowledge, loses communications or is diverted.
31. A unit reports attendance from an adjacent location rather than the actual incident site.
32. GPS, radio and officer narrative provide conflicting attendance times.
33. Multiple units arrive in an order different from dispatch order.
34. A specialist unit arrives but lacks the expected capability or equipment.
35. A resource is requested but not owned, serviceable or available.
36. A resource is used by another incident before the allocation response returns.
37. A partner agency declines, delays or only partially accepts a request.
38. A partner agency and police disagree about command, access or task responsibility.
39. A partner agency provides information that is later withdrawn or corrected.
40. A major incident declaration is delayed, disputed or made retrospectively.
41. A command appointment is invalid, expires or is not accepted at handover.
42. An incident commander becomes unavailable without a successor.
43. A commander gives an instruction beyond their authority.
44. A high-risk incident has no available supervisor or commander.
45. The incident owner changes while several tasks are outstanding.
46. Handover is interrupted by a new emergency or communication failure.
47. The outgoing owner leaves before the incoming owner accepts; accountability must remain explicit.
48. An incident is resolved but follow-up safeguarding, welfare or property protection remains.
49. An incident is closed while an investigation, forensic examination or court process continues.
50. A case referral is rejected, withdrawn, split or later reopened.
51. An arrest occurs during an incident but the arrest/custody record is delayed.
52. A person dies or is seriously injured after the incident was initially assessed as low severity.
53. An incident affects essential services, transport or several businesses simultaneously.
54. Weather or infrastructure changes make the original response route/site unsafe.
55. The same hazard creates several separate operational incidents.
56. An incident spans a boundary within the one city; no new jurisdiction is created.
57. A request originates outside Saltwater but concerns an event or person within Saltwater.
58. An external event is relevant as context but must not create an off-map playable location.
59. A mass event creates many reports, sites, people and tasks without exceeding the global population cap.
60. The system receives duplicate, delayed, reordered or malformed domain events.
61. A remote domain is unavailable during incident creation or state transition.
62. Storage is unavailable after an officer has captured urgent information.
63. A notification is queued but the recipient's assignment changes before delivery.
64. A user has incident access but not access to linked restricted health, intelligence or witness data.
65. A break-glass access session remains open after the emergency purpose ends.
66. An NPC receives a summary that omits a material uncertainty or contradiction.
67. A report summary accidentally implies guilt or certainty not present in the source.
68. A player attempts to infer concealed truth from an incident label, alert or map annotation.
69. A time-based escalation is due while simulation time is frozen.
70. A clock correction changes display time but must not reorder immutable source chronology.
71. A closed incident is subject to an audit, complaint or records challenge.
72. A backup is restored to a point before a dispatch acknowledgement; reconciliation must not repeat dispatch side effects.
73. An incident ID or linked source ID is referenced by a stale external message.
74. A user attempts to delete an incident rather than cancel, close or correct it.
75. A bulk report includes duplicate, cancelled or reopened incidents and must explain its counting rules.
76. A text-only interface must support every critical action when maps, images or charts are unavailable.
77. A large incident event log must remain navigable without truncating source records.
78. A person has a minor but material connection and must be permanently promoted, even if later ruled irrelevant.
79. A reporter's account is corrected but the correction does not erase the original.
80. The incident has no confirmed resolution; closure must not invent one.

## 26. Dependencies and ownership matrix

| Domain | BP-12 dependency / contract | Authority retained by domain |
|---|---|---|
| BP-01 | Canon and governing constraints | Game identity, single-city and player-agency rules |
| BP-02 | Canonical location and geography references | Spatial IDs, geometry, topology |
| BP-03 | Person identity, population cap and promotion | Person master, life state, global population ledger |
| BP-04 | Property, business, infrastructure and partner references | Premises, organisation and business registry |
| BP-05 | Police institutional authority | Department structure and formal authority architecture |
| BP-06/BP-07 | Personnel identity, status, career eligibility | Personnel and career records |
| BP-08 | Unit eligibility, assignment and deployment | Unit establishment, deployment and personnel assignment |
| BP-09 | Resource request and availability | Asset inventory, serviceability and allocation |
| BP-10 | Field observation, attendance and patrol activity | Field activity and officer observation records |
| BP-11 | Call/CAD/dispatch/communications references | Call intake, CAD, dispatch and communication records |
| BP-13/BP-14 | Crime classification and generated occurrences | Crime taxonomy/classification; occurrence generation |
| BP-15/BP-16 | Case referral and investigation links | Case and investigative lifecycle |
| BP-17–BP-24 | People, interviews, surveillance, intelligence, scenes, evidence, forensics | Each specialist domain's records and decisions |
| BP-25–BP-29 | Arrest, custody, legal, court and corrections links | Each legal/custodial domain |
| BP-30/BP-31 | Policy, command delegation and standards referrals | Governance, formal policy and professional standards |
| BP-35/BP-37 | Causal execution, shared clock and pause/freeze | Simulation engine and time |
| BP-38/BP-39 | Record conventions, persistence and recovery | Shared record governance and persistence |
| BP-40/BP-41 | Text/map interface and notifications/reporting | Presentation and delivery |
| BP-42–BP-44 | Permissions, test governance and change control | Security, QA and controlled configuration |

## 27. Open decisions for later policy/configuration approval

These are deliberately not silently fixed by this draft:
1. Final incident category and subtype catalogue and its relationship to BP-13 offence taxonomy.
2. Exact priority labels, thresholds, review intervals and response-time targets.
3. Severity/risk scoring model, if any, and the balance between structured assessment and narrative judgement.
4. Exact criteria for major-incident designation and command structure activation.
5. Formal command doctrine, role titles, levels and delegation instruments.
6. Which incident categories require mandatory supervisor review or named ownership.
7. Closure review rules by category and risk.
8. Retention periods and any legally required disposition schedule.
9. Exact incident ID display format, while preserving opaque stable identity.
10. Which partner agencies and external contact interfaces are represented in the initial playable release.
11. Whether some low-risk reports remain BP-11-only until triage or always receive BP-12 incident records.
12. Exact workload queue and escalation service levels.
13. Which analytics and performance measures are enabled and their counting definitions.
14. Data minimisation rules for sensitive incident summaries and external partner views.
15. Whether command structures adopt strategic/tactical/operational labels or a different approved vocabulary.

An open decision does not permit implementation to invent a permanent rule. Use versioned configuration and record the selected policy when approved.

## 28. Traceability to source blueprint

The specification must preserve all mapped requirements and tests from the original 52-division source. Relevant destinations include:
- **S02** Geography, land and spatial reference: canonical geography remains BP-02-owned; BP-12 only references it.
- **S07** Businesses and commercial economy: incident links reference BP-04 businesses and organisations without duplicating their records.
- **S13** Healthcare and public health: provider/medical response interfaces and protected information are supported; healthcare is not expanded into an equal-depth simulation.
- **S16** Utilities, energy and communications infrastructure: outages and service disruption can affect incident risk, response and coordination.
- **S17** Roads, transport and mobility: response routing, access and movement consume canonical roads and transport conditions.
- **S19** Environment, weather and natural hazards: hazards affect location, safety, resources and operational decisions.
- **S20** Food systems and essential services: disruptions can create police incidents and resource dependencies.
- **S22** Emergency services and civil protection: multi-agency coordination, dispatch handoffs and incident command interfaces are explicit.
  - Exact obligations: S22.R01–R03 and S22.T01. BP-12 owns incident-level multi-agency command, operational milestones, resource/agency status links and handoff chronology; BP-11 owns communications/dispatch exchange; BP-04/BP-33 own partner-agency capability and staffing source records; BP-35 owns event execution.
- **S26** Police command, policy and internal governance: operational command and policy authority are distinguished.
- **S27** 911, call-taking, CAD and dispatch: BP-11 owns communications; BP-12 owns the incident record.
- **S28** Patrol, response and field operations: BP-10 owns field activity; BP-12 coordinates incident-level status.
- **S29** Incidents, crime taxonomy and occurrence generation: BP-12 owns incident lifecycle; BP-13 taxonomy; BP-14 generation.
- **S37** Arrest, search, warrants and custody: arrest/custody references do not displace BP-25/BP-26 authority.
- **S45** Maps, diagrams and visual evidence: maps/timelines are optional views of authoritative incident data, not alternate records.
- **X01–X06 and X09** stable identity/provenance, single source of truth, shared time, atomic reconciliation, fact/allegation distinctions, preservation of originals and police-depth/proportionate-support principles.

The crosswalk remains the authoritative exhaustive index of all 168 source requirements and 60 source tests. BP-12 implementation must verify each source ID mapped to BP-12 against the original JSON pointer and incorporate its full meaning. This draft's test catalogue supplements, and does not replace, the source tests.

## 29. Implementation sequencing and exit conditions

Before implementation:
- Resolve or explicitly defer the open policy decisions with versioned configuration.
- Validate all BP-12 source requirement/test mappings against the original source JSON and crosswalk.
- Define event schemas and contract tests with BP-08, BP-09, BP-10, BP-11, BP-13, BP-14, BP-15, BP-17, BP-22, BP-23, BP-30, BP-35, BP-37, BP-38, BP-39, BP-41 and BP-42.
- Confirm stable identifier strategy, append-only event model, idempotency and projection rebuild approach.
- Confirm population-cap and pause/freeze enforcement are inherited from BP-03/BP-35/BP-37 rather than duplicated.
- Define access matrix and restricted-field projection with BP-42.
- Define recovery and reconciliation evidence with BP-39.
- Establish acceptance fixtures for ordinary, high-risk, multi-site, multi-agency, duplicate, long-running and reopened incidents.

Implementation is not complete until all mandatory tests pass, event contracts reconcile, permissions are tested, replay/recovery is demonstrated, no forbidden time advance occurs, and traceability evidence is attached. Testing and verification statuses remain separate from design status.

## 30. Design status and change control

**Current status:** DESIGNED_DRAFT. This is a comprehensive design specification draft, not an approved design and not an implementation.

- Implementation: NOT_STARTED.
- Test execution: NOT_STARTED.
- Verification: NOT_STARTED.
- User approval: PENDING.
- Neon writes: NONE; this document authorises no database changes, migrations, imports, seeds or writes.

Any future change must preserve the fixed BP-01–BP-44 structure, maintain source traceability, record rationale and update the specification register. No requirement, test, edge case or canon constraint may be removed merely to reduce storage or implementation effort. Compress representation, never meaning.
