# BP-29 — Corrections

**Division:** BP-29  
**Title:** Corrections  
**Specification version:** 1.0  
**Status:** DESIGNED_DRAFT  
**User approval:** PENDING  
**Implementation / test execution / verification:** NOT_STARTED  
**Authority:** Saltwater fictional canon and adopted BP-01–BP-44 master blueprint. This specification defines correctional operations and post-sentence status; it does not enact fictional law or authorise database writes.

## 1. Purpose

BP-29 defines the correctional system after a person becomes subject to a valid correctional sentence or other configured correctional authority. It covers sentence intake and validation, correctional admission, custodial sentence execution, institutional placement, movements, welfare and safety interfaces, rehabilitation, community supervision, release, recall and post-release status.

BP-29 is the authoritative owner of correctional execution and supervision records. It receives legal authority from BP-28 and does not create, amend or reinterpret court sentences. BP-26 owns police custody and detention before a valid handover. BP-03 owns person identity, living status and population accounting. BP-27 owns party-side legal process and appeal applications. BP-28 owns judicial findings, sentences and orders.

The division must support custodial and non-custodial outcomes proportionately, with meaningful continuity from court to correctional execution and back to the canonical person record. It must not expand into a second deep society simulator. Correctional institutions, personnel, programmes and providers exist at the depth needed to support the police simulation and its legal consequences.

## 2. Binding Saltwater canon

1. Saltwater is one sovereign city-state, one playable city and one jurisdiction. No second city, external playable territory or world expansion is created.
2. Total living population is capped at **10,000**, including police, court, correctional, healthcare, legal and all other people. Each canonical person is counted once.
3. There are at least **10,000 businesses**. This division does not alter that baseline.
4. Police remains the deepest simulation; correctional systems are realistic and operationally coherent but proportionate.
5. Text is the permanent, complete primary interface. No essential correctional fact exists only in a graphic.
6. BP-37 is the sole simulation clock. No sentence, supervision, programme, review, release, recall, NPC or institutional activity progresses while the player is absent or the simulation is paused.
7. Every person has one canonical identity. Any person materially connected to police activity/casework and promoted to full persistent simulation remains promoted permanently; promotion never duplicates a person or exceeds the cap.
8. NPCs know only what they observed, received or were authorised to access.
9. No correctional record, dialogue, summary or notification reveals hidden culprit/accomplice/perpetrator truth unless the player types exactly `bingo`.
10. No unsolicited investigative hints or forced narrative outcomes.
11. No real-world correctional statute, sentence calculation, release rule, institution hierarchy, parole standard or rehabilitation model is silently imported. Fictional rules are explicit, versioned configuration.
12. Blueprint approval authorises no Neon schema migration, seed data, import or bulk write.

## 3. Scope

### 3.1 Included

- Correctional institution and service catalogue.
- Sentence/order intake, authenticity and completeness validation.
- Sentence commencement, calculation, execution status and reconciliation.
- Correctional admission and lawful transfer from police custody.
- Correctional population, placement, capacity and movements.
- Custodial operations, safety, incidents, welfare and institutional status.
- Temporary absence, hospital transfer, escape/unauthorised absence and return.
- Community supervision and post-sentence status.
- Rehabilitation, education, work and support programme references.
- Release eligibility, release authority validation, execution and acknowledgement.
- Recall and return to correctional custody under valid authority.
- Sentence variations, stays, appeals and recalculation interfaces.
- Correctional records, permissions, audit, reporting and persistence.
- Interfaces to person, court, police custody, healthcare, resources, finance and time.

### 3.2 Excluded

- Person identity, living status and population count: BP-03.
- Institutions, premises, service-provider identity and business identity: BP-04.
- Police mandate/personnel/operations: BP-05–BP-12.
- Crime and hidden occurrence truth: BP-13/BP-14.
- Police case/investigation and participant roles: BP-15–BP-18.
- Interview, surveillance, intelligence, scene, evidence and forensics source records: BP-19–BP-24.
- Arrest, warrant, search and seizure: BP-25.
- Police custody, booking, detention and police release: BP-26.
- Charging, prosecution/defence and appeal filing workflow: BP-27.
- Court findings, verdicts, sentences, sentence terms and judicial orders: BP-28.
- Police department governance/discipline: BP-30/BP-31.
- Global training, HR, finance, simulation engine, social context, time, records, persistence, interface, notifications, security, QA and configuration: BP-32–BP-44.

## 4. Ownership and authoritative boundaries

| Domain | Authoritative owner | BP-29 responsibility |
|---|---|---|
| Person identity/living status/population | BP-03 | Reference canonical person; never create duplicate identity |
| Correctional organisation and premises identity | BP-04 | Own correctional operational state and service relationships |
| Police custody | BP-26 | Receive valid transfer; never rewrite police custody history |
| Charging/legal party process | BP-27 | Consume legal-process references; no charging decisions |
| Court sentence/order/variation/stay | BP-28 | Validate and execute authoritative order; never change its terms |
| Correctional sentence execution/supervision/release/recall | BP-29 | Authoritative owner |
| Healthcare records and clinical judgment | Relevant source division/provider; BP-42 controls access | Record referrals/receipt and operational support only |
| Resources/facilities/equipment | BP-09/BP-04 | Request/allocate correctional operational resources by contract |
| Staff identity/employment/training | BP-06/BP-32/BP-33 | Reference qualified personnel and assigned roles |
| Finance/procurement | BP-34 | Emit costs/obligations; no competing ledger |
| Time | BP-37 | Consume canonical simulation time |
| Records/persistence/security | BP-38–BP-42 | Follow shared contracts |
| QA/configuration | BP-43/BP-44 | Supply testable rules and versioned policy |

A court sentence is an authoritative judicial instruction. A correctional execution record describes what the correctional system actually received, validated and did. A sentence start, calculated release estimate, eligibility state, release authorisation and physical release are separate facts. A court order does not prove implementation; implementation cannot amend the order.

Police custody ends only through a valid handover under BP-26. Correctional custody begins only through BP-29's accepted admission. A transfer in progress or disputed is not silently treated as completed. If a person is temporarily moved to hospital or another provider, their legal custody/supervision status is explicitly retained or changed only under the applicable authority.

## 5. Core entities and records

All IDs are stable, unique, non-semantic and governed by BP-38. Names are display attributes, never identity joins.

### 5.1 Correctional institution

Fields: institution_id; canonical organisation_id; institution_name; institution_type; premises_ref; jurisdiction_id; operational_status; capabilities; configured capacity; active population; staffing/capability state; access class; opening/closure events; configuration version; audit history.

Institution types may include custodial facility, remand/holding facility if configured, community supervision office, programme provider or other approved service. The catalogue is fictional and configurable. A facility's label does not grant legal authority to detain.

### 5.2 Sentence execution record

Fields: execution_id; canonical person_id; court_sentence_id; court_order_id/version; issuing court; linked BP-27 proceeding; charge/count references; received time; validation status; legal effective date; commencement trigger; commencement event/time; sentence type; exact terms snapshot; calculation method/version; estimated and confirmed dates; stays/variations; completion status; downstream references; audit history.

The terms snapshot is a read-only reference/copy for execution convenience. BP-28 remains authoritative. Every recalculation records the exact order version and configured rule version.

### 5.3 Correctional admission

Fields: admission_id; person_id; execution_id or other authority_ref; sending agency; sending custody record; receiving institution; receiving officer; identity checks; property/health/safety handover references; arrival time; acceptance time; discrepancies; status; source manifest; audit history.

Arrival, identity confirmation, authority validation, physical acceptance and completed admission are separate events. A failed or disputed admission remains explicitly pending and preserves the person's actual location/agency responsibility.

### 5.4 Placement and movement

Fields: placement_id; person_id; institution_id; location/cell/area reference; placement purpose; start/end times; authority; risk/safeguarding basis; review trigger; responsible actor; movement events; history.

Movement fields include movement_id; person_id; origin; destination; purpose; escort/responsible actor; authority; departure/arrival times; status; handover and acknowledgement; incident references.

### 5.5 Community supervision record

Fields: supervision_id; person_id; originating sentence/order; responsible unit/provider; supervising officer; start trigger/time; terms snapshot; conditions; reporting requirements; contact plan; status; variation/stay; breach allegations; review events; termination basis/time; history.

Conditions reproduce the authoritative order. Local operational plans may organise contacts but cannot create new legal conditions.

### 5.6 Rehabilitation and programme participation

Fields: programme_id; provider_ref; programme type; eligibility/configuration; capacity; session schedule; participant_id; referral source; consent/authority basis; enrolment; attendance; completion; outcome; assessment source; restrictions; version history.

Programme records distinguish referral, offer, acceptance, attendance, participation, completion and outcome. A programme provider's source record remains with its owning institution; BP-29 holds only the necessary participation and handover facts.

### 5.7 Release and recall

Release fields: release_id; person_id; execution_id; authoritative order/authority; release eligibility snapshot; validation; responsible institution/actor; effective time; actual departure; destination/receiving person or service; conditions; property/identity handover; notifications; acknowledgement; exceptions; history.

Recall fields: recall_id; person_id; authority/order; originating supervision/execution; reason/category as supplied by authority; validation; location; execution event; receiving institution; effective time; linked prior release; history.

Recall application, warrant/order, operational location, physical return and readmission are separate events.

## 6. Correctional institutional architecture

Correctional institutions are functional organisations and facilities within Saltwater, not additional cities or jurisdictions. BP-04 owns canonical organisation and premises records; BP-29 owns correctional operational functions, admissions, placements, sentence execution and supervision.

The institutional catalogue may include custodial establishments, community supervision functions and approved programme services. It must not assume a national prison network, foreign jurisdiction or large external estate. External transfer or post-release residence may be represented as an off-map reference only; it does not create playable external geography or NPC populations.

Each institution has configured capabilities, operational state, capacity, staffing, access controls and service relationships. A facility may be open, restricted, temporarily unavailable, under maintenance, emergency-closed or decommissioned. Closure must not erase residents, sentences, movements, incidents or records. Affected persons require an explicit transfer/continuity event.

Capacity is configured and measured using the approved definition (e.g. usable places, staffed places or specialist places). The system must not silently overfill a facility. Exceptional placement, if permitted, requires explicit authority, rationale, duration and review. The exact capacity baseline remains open configuration.

## 7. Sentence intake and validation

BP-29 receives a sentence or other correctional authority only from an authenticated BP-28 order/event reference. Intake records the sender, source, exact order version, time received, integrity/provenance and acknowledgement. The record is not accepted merely because a player or NPC states that a sentence exists.

Validation checks:
- canonical identity and person match;
- issuing court and judicial authority reference;
- authoritative order status and version;
- defendant and charge/count scope;
- sentence type, terms, duration/amount and conditions;
- effective date and commencement trigger;
- concurrent/consecutive relationships;
- appeal, stay, variation or supersession status;
- required accompanying documents and handover details;
- duplicate or conflicting execution records.

Outcomes are accepted, accepted with explicitly identified non-blocking discrepancy, pending information, rejected as invalid, superseded or disputed. No missing value is invented. A correction from BP-28 creates a new validation/reconciliation event linked to the earlier snapshot.

A sentence may be received before the person arrives. This creates an execution record in awaiting-admission status, not a correctional custody record. Non-custodial sentences may proceed to a supervision or programme workflow without institutional admission.

## 8. Sentence commencement and calculation

The commencement trigger is exactly the trigger defined by the authoritative order and configured fictional rule. It may refer to a specified event/date, completion of another term, admission, release from another order or another explicitly configured condition. BP-29 does not choose a more convenient start date.

Store separately:
- court-ordered sentence date/trigger;
- order receipt and validation time;
- actual correctional admission time;
- legal commencement time;
- estimated completion/release date;
- confirmed completion or release event/time.

Calculations are deterministic, reproducible and versioned. Each calculation records input order versions, credited time where authorised, concurrency/sequence, rule version, result and any uncertainty. If the order is ambiguous, the system records a blocked calculation and requests authoritative clarification through the proper legal interface. It must not silently calculate from an assumption.

A sentence may be varied, stayed, quashed or replaced only through an authoritative BP-28 event. The new calculation references both old and new terms. Historical values remain queryable. Filing an appeal alone does not suspend execution; an explicit stay or variation is required.

## 9. Admission and transfer from police custody

A transfer from police custody is coordinated with BP-26. Required records include sending custody identity/status, valid court or other authority, receiving institution, person identity verification, responsible sending/receiving actors, physical arrival, property handover, medical/welfare information permitted for transfer, risks/alerts and discrepancies.

The handover lifecycle includes initiated, dispatched, arrived, identity checked, authority checked, accepted, rejected, disputed or interrupted. Sending custody remains responsible until the agreed/authorised handover point is recorded under BP-26/BP-29 contract. No division silently changes the other's status.

If the receiving institution cannot accept the person, the refusal reason, actual location, responsible authority and next authorised handling state are recorded. A full facility or missing document does not permit an invented legal basis for detention or release.

## 10. Custodial execution and placement

For persons serving custodial sentences, BP-29 tracks institutional custody, placement, movements, access to services, operational restrictions and sentence execution. Placement decisions must respect configured capacity, legal order, safety, separation, accessibility and available capability. The system records reasons and responsible authority without exposing protected information to unauthorised users.

A placement is time-bounded and historically queryable. Transfers between cells, units or facilities are explicit movements with origin/destination, authorisation, actor, reason, departure/arrival times and handover. Temporary movement to healthcare or another provider does not automatically terminate correctional custody.

Institutional staff actions and NPC routines occur only when simulation time advances. The game does not simulate every institutional detail or every resident continuously; it preserves enough operational state, records and relevant-person depth for credible consequences and player interaction.

## 11. Welfare, safety and incidents

BP-29 records correctional operational incidents such as injury, illness referral, self-harm report, violence, threat, fire, property damage, disturbance, unauthorised absence, death or other configured event. It separates the initial report, observed facts, immediate response, referrals, investigation and findings.

Clinical assessment and diagnosis remain with the appropriate healthcare source. BP-29 records referral, attendance, operational instructions received and custody implications within authorised access. It cannot invent diagnosis, prescribe treatment or overwrite clinical records.

Risk assessments identify assessor, method/version, evidence considered, confidence/limitations, effective interval, review trigger and access class. A risk score is advisory unless an explicit fictional rule gives it a defined operational effect. It does not itself authorise segregation, punishment, release or recall.

Disciplinary proceedings are distinct from criminal proceedings and sentence execution. Allegation, notice, response, hearing, finding, sanction and appeal/review are separate events. A disciplinary sanction cannot extend or alter a court sentence unless an authoritative court order permits the effect.

## 12. Temporary absence, hospital transfer and unauthorised absence

A person may be temporarily outside a facility while remaining subject to correctional custody or supervision. Each movement records legal status, escort, authority, destination, departure/return, receiving provider and acknowledgement. Hospital admission does not transfer correctional authority unless the applicable order and configured rules say so.

Escape or unauthorised absence is an incident with observed facts, last confirmed location, discovery time, responsible actor, response and notification references. It does not automatically extend the sentence, create a new charge, establish guilt or change legal status. Any new warrant, sentence adjustment or recall requires its own legal authority.

Return or recovery requires identity confirmation, authority checks, receiving institution and a new admission/return event. A person may be missing, located, in transit or returned; the state must not collapse these statuses.

## 13. Community supervision

Community supervision applies only where an authoritative BP-28 order or configured lawful authority requires it. BP-29 records the exact person, order, terms, start trigger, responsible supervision function, assigned officer/provider, conditions, reporting/contact plan, review dates and end trigger.

A supervision condition is not created by a caseworker preference or AI-generated plan. Operational contact schedules may organise delivery but cannot expand legal restrictions. Every contact records date/time, participants, method, purpose, outcome, source and any follow-up. Missed appointment, inability to contact, refusal, non-compliance allegation, verified event and adjudicated breach remain separate.

Supervision may be active, pending commencement, paused by authoritative order, varied, suspended, completed, terminated or under recall process. A variation or termination requires authority and a new version. No condition expires while the simulation is paused.

## 14. Rehabilitation, education, work and support

Rehabilitation supports sentence execution and post-sentence outcomes without becoming a parallel healthcare, education, employment or social-care simulator. Programmes may include configured education, skills, work, behaviour support, substance-use support, family contact or other fictional categories. These are catalogue labels only until BP-44 configuration.

For every programme, distinguish referral, eligibility, offer, consent/authority, enrolment, attendance, participation, completion and recorded outcome. Non-attendance is not automatically a breach. A programme unavailable because of capacity or staffing does not silently extend a sentence or alter release date.

Clinical services remain with healthcare source owners. Employment, education and business records remain with their respective divisions/providers. BP-29 stores only the referral/participation/necessary result and source link. Sensitive details are minimised and access-controlled.

## 15. Release eligibility, authority and execution

Release is a controlled multi-stage process:
1. calculate potential eligibility from exact sentence order and approved rules;
2. record the result as estimated/eligible/not eligible/uncertain;
3. receive any required authoritative release order or confirm the exact automatic authority specified in the sentence;
4. validate identity, order, conditions, effective date, stays, other active lawful holds and required handovers;
5. prepare the release;
6. record actual physical departure and effective release;
7. record property, documents, conditions, destination/referrals and acknowledgement;
8. update correctional execution and post-release status through an attributable event.

Eligibility is not authority. Authority is not physical release. An estimated release date is not a promise or order. If there are multiple sentences or independent holds, each must be reconciled under configured rules. A correctional officer cannot override a court order or invent a detention basis.

A delay or blocked release is recorded with the exact conflict, source, responsible authority and current physical/legal status. No person is shown as released until the actual release event is confirmed.

## 16. Recall and return to custody

Recall may apply only under an authoritative order or explicitly configured legal mechanism. An allegation, missed appointment, intelligence report or unverified breach is not itself recall authority.

The recall workflow distinguishes application/request, decision/order, notification, location, operational execution, transport, arrival, identity confirmation and admission. Each stage has its own source, actor, time and status. A recall may be refused, withdrawn, pending, stayed, varied, executed or unsuccessful.

Recall links to the original release/supervision and exact legal authority. It does not silently restart an expired sentence or change terms. The effect on remaining sentence, credit, supervision and release calculation is derived only from BP-28 order and approved rules.

## 17. Post-release status and continuity

Post-release status records the person's relationship to the completed or active sentence after physical release. It may include completed, active community supervision, conditional release, discharged, recalled, deceased, transferred to external authority or other configured state. The catalogue is fictional and versioned.

The person remains the same canonical BP-03 identity. Release does not create a new NPC or erase past correctional records. Case, conviction, sentence, supervision and release histories remain separately queryable and access-controlled. A person who is permanently promoted to full simulation remains so after release or sentence completion.

An external address, service or authority may be referenced without creating an external playable city or simulating external institutions in depth. The system must not create off-map living-person counts that undermine the single-city population canon.

## 18. Court variation, appeal and legal reconciliation

BP-28 is authoritative for sentence, stay, variation, quashing, appellate outcome and other judicial orders. BP-29 receives the new order, validates the affected person and sentence, records receipt/acknowledgement and computes a new execution state. The prior state remains in history.

BP-27 owns appeal applications and party-side procedure. An appeal filing does not itself change correctional status. If a stay is issued, BP-29 applies only the effect stated in the authoritative order. If an order is unclear or conflicts with another active order, mark the execution record disputed/pending and request clarification through the legal interface; do not choose an interpretation.

Acquittal, dismissal, conviction, sentence, sentence completion, release and post-release status are distinct. BP-29 cannot decide guilt, vary conviction, amend the charge or make a judicial finding. It can report operational execution facts and discrepancies to authorised recipients.

## 19. Person identity, population and role continuity

All persons use BP-03 canonical person IDs. Correctional role, prisoner/detainee status, supervision status, employee role, victim/witness role and suspect/offender role are separate time-bounded relationships. A person may have several roles across cases and time; one role never overwrites another.

Correctional admission, release, death, transfer and temporary absence do not create duplicate person records. Population count is determined by BP-03 canonical living status and geography rules, not by the number of institutional or case records. A person is counted once.

Any person promoted to full persistent simulation because of police/case relevance remains permanently promoted. This applies through arrest, remand, sentence, imprisonment, release and post-release status. Promotion cannot exceed the hard 10,000 living-person cap. If a genuinely new person would exceed the cap, BP-03's approved replacement/lifecycle rules must resolve it; BP-29 cannot bypass the limit.

## 20. Time, scheduling and pause invariants

BP-37 is the sole simulation clock. All sentence, admission, placement, movement, programme, contact, review, release and recall events use canonical simulation time. Every effective-dated status is historically queryable.

When the player exits or the game is paused:
- no sentence time accrues;
- no custodial or community supervision activity occurs;
- no programme session runs or attendance changes;
- no review or deadline expires;
- no release or recall eligibility changes through elapsed time;
- no NPC contact, movement, incident or institutional routine progresses;
- no facility capacity or staffing changes;
- no court order is received or implemented in the background.

Resume continues from the exact frozen state. No real-world elapsed time is applied and no catch-up events are generated. The game advances these processes only as part of explicit in-game time progression.

## 21. NPC knowledge, autonomy and player agency

Correctional NPCs know only their own observations, received records, assigned duties and authorised information. A supervising officer does not know private police investigation facts unless lawfully provided. A correctional employee cannot access BP-14 hidden occurrence truth.

NPC autonomy is bounded by role, authority, assigned workload, capability, available information and simulation time. NPCs may perform routine actions only while the game clock advances and only when configured behaviour permits. They cannot autonomously create a sentence, vary a court order, impose release, recall a person or determine a criminal breach without authority.

The player can inspect records and make decisions permitted by their in-world role. The interface must not provide omniscient clues or recommend an investigation path. The exact `bingo` reveal firewall applies to dialogue, reports, records, notifications, search snippets, AI summaries and metadata.

## 22. Inputs and outputs

### Inputs

- BP-03: canonical identity, living status, population and permanent person-promotion state.
- BP-04: correctional organisations, facilities, premises and service-provider identities.
- BP-06/BP-32/BP-33: staff identities, qualifications, training and employment/assignment.
- BP-09: facilities, equipment and resource availability.
- BP-17/BP-18: participant roles and restrictions where relevant.
- BP-25/BP-26: arrest, police custody and transfer/handover records.
- BP-27: legal process and appeal application references.
- BP-28: authoritative sentence, order, stay, variation, release and recall authority.
- BP-34: financial obligations/cost interfaces.
- BP-37: canonical time and pause state.
- BP-38/BP-39: identifiers, schemas, persistence and recovery.
- BP-41/BP-42: notifications, reporting and permissions.
- BP-44: approved fictional correctional rules and catalogues.

### Outputs

- Sentence receipt, validation, execution and calculation records.
- Correctional admission, placement, movement and handover events.
- Institutional capacity, status and operational incident records.
- Community supervision, programme referral and participation records.
- Eligibility estimates, release validation and actual release events.
- Recall validation, execution and return/admission events.
- Order discrepancy, implementation acknowledgement and reconciliation notices.
- Person/case/court references, reports, audit and state-change events.

Every output is attributable, versioned and linked to source authority. Downstream owners validate their own transitions; BP-29 does not directly mutate another division's records.

## 23. State transitions and event contracts

Every material event records event_id, entity_id, prior/new state, actor, role/authority, canonical simulation time, source record/version, institution/location, reason, configuration version, result, idempotency key and correlation references.

Core events include sentence_received/validated/rejected/disputed; execution_created/commenced/stayed/varied/completed; admission_initiated/arrived/accepted/rejected; placement_assigned/changed; movement_started/completed/interrupted; incident_reported/reviewed/closed; referral_created/accepted/declined; programme_started/attended/completed; supervision_started/contact_recorded/varied/paused/terminated; release_eligibility_calculated/validated; release_authorised/prepared/completed/blocked; recall_requested/ordered/located/executed/returned; order_acknowledged/reconciled; record_corrected/accessed/exported.

Events are append-only and idempotent. Replaying an event cannot create duplicate admissions, sentence commencements, releases, recalls or movements. Partial failures preserve completed steps and an explicit incomplete status. An unacknowledged downstream message remains pending; it is never presumed successful.

## 24. Permissions and security

BP-42 owns global enforcement. BP-29 defines scopes for sentence records, custody status, institutional placement, movements, risk assessments, incidents, health/welfare referrals, programme participation, supervision, release, recall, protected persons, external handovers, financial obligations and audit.

Access is checked by actor, role, institution, assignment, purpose, person, case/order, record class and event time. Correctional staff do not receive unrestricted police intelligence, medical records, court deliberations or protected source identities. Healthcare access is limited to authorised clinical roles. A person may have rights to access certain records under configured fictional rules, but that does not expose protected third-party information.

Every read, change, export, disclosure, correction and denied access is audited. Search results, counts, summaries and metadata must not leak restricted information or hidden truth.

## 25. Records, persistence and reporting

BP-38 defines schemas and identifiers; BP-39 defines persistence, backups, recovery and integrity. BP-29 must preserve authoritative source links, execution snapshots, event history, corrections, calculations and handover acknowledgements. A restart must not duplicate a release, admission or sentence event.

Reports distinguish:
- court-ordered sentence terms;
- correctional receipt and validation;
- actual commencement and execution status;
- estimated vs confirmed completion/release;
- release eligibility vs release authority vs physical departure;
- recall application/order/execution;
- active supervision vs completed supervision;
- programme referral vs attendance vs outcome.

Every report includes as-of simulation time, source versions, scope, filters, uncertainty, access class and author/system. A report is a derivative, never an authoritative court order or healthcare record.

## 26. Cross-system effects and handover

### BP-03 — Person and population
Canonical person IDs and living status are authoritative. Admission, release and transfer update BP-29 role/status records; BP-03 controls identity and population accounting. Permanent promotion remains in force after sentence completion.

### BP-04 — Institutions and premises
Correctional organisation and premises identities are sourced from BP-04. BP-29 maintains operational correctional functions, capacity and admissions, not duplicate property or organisation masters.

### BP-09/BP-33/BP-34 — Resources, staff and finance
Correctional facilities and equipment use BP-09 resource contracts. Staff identity, training and employment use BP-06/BP-32/BP-33. Costs, fines, restitution and procurement/financial transactions link to BP-34; no competing ledger is created.

### BP-25/BP-26 — Arrest and police custody
BP-25 owns arrest; BP-26 owns police custody. A valid transfer and accepted handover are required before BP-29 correctional custody begins. All prior police custody records remain unchanged.

### BP-27/BP-28 — Legal process and court
BP-27 owns applications and party-side process. BP-28 owns sentence and order authority. BP-29 acknowledges and implements exact authoritative orders, reports discrepancies and returns implementation status. It never creates or changes a sentence.

### Healthcare and support
Healthcare providers and clinical records remain with their source owners. BP-29 records authorised referrals, attendance/receipt and operational implications. Sensitive material is controlled under BP-42.

### BP-37–BP-44 — Shared infrastructure
Use BP-37 clock; BP-38 IDs/schemas; BP-39 persistence; BP-40 interface; BP-41 notifications/reporting; BP-42 security; BP-43 QA; BP-44 configuration. No local substitute or competing authority is permitted.

## 27. Exceptions and edge cases

The implementation must explicitly handle:
1. Court order missing, unauthenticated, corrupt, superseded or unissued.
2. Sentence identifies wrong person, charge or count.
3. Sentence terms or commencement trigger ambiguous.
4. Multiple concurrent/consecutive sentences conflict or are incomplete.
5. Appeal filed without a stay.
6. Stay/variation/quashing received after execution has commenced.
7. Conflicting court orders or unclear effective dates.
8. Sentence received before physical admission.
9. Person arrives without valid authority.
10. Identity mismatch or disputed identity.
11. Sending police custody record and receiving institution disagree.
12. Facility full, closed, unavailable or lacks required capability.
13. Transfer interrupted, delayed, rejected or disputed.
14. Person physically present but admission not accepted.
15. Placement requires separation/protection or specialist capability.
16. Temporary hospital transfer with custody status unresolved.
17. Injury, illness, serious incident or death in custody.
18. Escape/unauthorised absence and later recovery.
19. Supervision order lacks clear terms or start trigger.
20. Missed appointment with uncertain cause.
21. Alleged breach not yet verified or adjudicated.
22. Programme unavailable, declined, interrupted or completed without outcome.
23. Clinical referral with missing, restricted or conflicting information.
24. Release estimate conflicts with court order or sentence calculation.
25. Release eligibility exists but authority is missing.
26. Release order exists but is not served/received or is stayed.
27. Multiple sentences or active holds affect release.
28. Release is authorised but physical departure is delayed.
29. Person departs but receiving service acknowledgement is absent.
30. Recall allegation exists but no recall order.
31. Recall order cannot be executed or person cannot be located.
32. Return identity or receiving facility is disputed.
33. Post-release supervision status conflicts with court order.
34. Correctional status conflicts with BP-03 living status.
35. Person appears under duplicate identity records.
36. Population cap would be exceeded by person creation.
37. NPC attempts unauthorised sentence, release, recall or condition change.
38. Sensitive healthcare or protected-person data accessed improperly.
39. Financial obligation is duplicated across BP-29 and BP-34.
40. Capacity/staffing/inventory changes fail atomic reconciliation.
41. Clock advances while paused or absent.
42. Duplicate event replay or partial persistence failure.
43. Court order implementation acknowledgement is lost.
44. Correction requested after release or sentence completion.
45. Facility closure occurs with residents or pending movements.
46. External transfer could be misread as external playable geography.
47. AI summary conflicts with the authoritative order.
48. Configuration is missing or changes during active sentence execution.

Every exception preserves the attempted action, actor, authority, time, source versions, affected records, actual person location/status, failure reason and authorised resolution path. Never invent legal authority, sentence terms, release date or breach finding.

## 28. Configuration and unresolved fictional policy

BP-44 governs correctional configuration. The following remain open and must not be guessed:

1. Correctional institution catalogue, names, types, capacity and geographic placement.
2. Custodial and community-supervision organisational hierarchy.
3. Sentence intake validation and discrepancy acceptance rules.
4. Sentence commencement, calculation, concurrency and credit rules.
5. Custodial facility admission, placement and transfer standards.
6. Capacity definition, overflow and emergency placement authority.
7. Staffing, role, qualification and supervision requirements.
8. Welfare, safety, observation and incident-review standards.
9. Healthcare referral, escort and hospital-transfer procedures.
10. Temporary absence and unauthorised absence handling.
11. Community supervision catalogue, conditions and contact intervals.
12. Breach allegation, verification and legal referral process.
13. Rehabilitation programme types, eligibility and provider capacity.
14. Work, education, family contact and support arrangements.
15. Release eligibility, authorisation and operational checklist.
16. Recall authority, procedure, execution and sentence-credit effect.
17. Post-release status catalogue and duration.
18. Record retention, disclosure and access rules.
19. Correctional discipline and review/appeal process.
20. Financial obligations and restitution execution interfaces.
21. External agency handover and off-map reference conventions.
22. NPC autonomy, staffing and routine activity policy.
23. Facility closure, emergency continuity and transfer policy.
24. Transition rules when configuration changes during active sentences.

Where a required rule is unresolved, mark the action pending/blocked and preserve the uncertainty. Do not import real-world law or invent an operational outcome.

## 29. Acceptance tests

These are criteria for BP-43. They are not evidence that implementation or testing has occurred.

- CORR-AT-001 — Every correctional institution has a stable unique institutional ID and canonical BP-04 organisation reference.
- CORR-AT-002 — Every correctional facility resolves to a Saltwater location and premises record.
- CORR-AT-003 — Correctional institutions remain within the single Saltwater city-state and jurisdiction.
- CORR-AT-004 — Correctional custody is distinct from police custody under BP-26.
- CORR-AT-005 — A person cannot be simultaneously counted as two living persons because of multiple correctional roles.
- CORR-AT-006 — Every correctional person record resolves to one canonical BP-03 identity.
- CORR-AT-007 — Every sentence execution record references an authoritative BP-28 sentence/order version.
- CORR-AT-008 — A charge, arrest, allegation or police referral cannot independently create a correctional sentence.
- CORR-AT-009 — A draft, unissued, stayed or invalid sentence order cannot commence execution.
- CORR-AT-010 — Sentence receipt and sentence acceptance are separately recorded.
- CORR-AT-011 — An invalid or incomplete sentence package is quarantined as pending validation.
- CORR-AT-012 — Sentence validation checks person, charge, court, order authority, effective date and terms.
- CORR-AT-013 — Sentence validation preserves unresolved discrepancies rather than inventing values.
- CORR-AT-014 — Every correctional admission records legal authority, receiving actor, institution and simulation time.
- CORR-AT-015 — Physical arrival does not alone prove lawful admission.
- CORR-AT-016 — Correctional admission is distinct from police custody booking.
- CORR-AT-017 — Transfer from BP-26 requires an authenticated order and handover record.
- CORR-AT-018 — Transfer receipt does not erase the prior police custody history.
- CORR-AT-019 — Correctional custody status is authoritative only within BP-29.
- CORR-AT-020 — Every movement between correctional locations records origin, destination, authority and time.
- CORR-AT-021 — Facility assignment respects configured capacity and eligibility constraints.
- CORR-AT-022 — Over-capacity admission is blocked or explicitly exceptional under approved configuration.
- CORR-AT-023 — Cell/placement assignment records effective interval and responsible actor.
- CORR-AT-024 — Separation or protection placement is recorded with authority and review requirements.
- CORR-AT-025 — Placement changes preserve previous location and reason.
- CORR-AT-026 — Facility status changes do not alter court sentence terms.
- CORR-AT-027 — Correctional institution closure preserves all resident and record histories.
- CORR-AT-028 — Facility staffing and capability constraints are visible to authorised operational users.
- CORR-AT-029 — Correctional operations remain proportionate and do not become a second deep society simulator.
- CORR-AT-030 — Sentence commencement follows the exact court-ordered trigger.
- CORR-AT-031 — Sentence commencement date is never inferred from arrest or police custody arrival.
- CORR-AT-032 — Concurrent sentences remain distinct and are calculated under configured rules.
- CORR-AT-033 — Consecutive sentences remain distinct and are calculated under configured rules.
- CORR-AT-034 — Aggregate sentence calculations are reproducible from authoritative order versions.
- CORR-AT-035 — Uncertain sentence arithmetic remains unresolved rather than guessed.
- CORR-AT-036 — Remand credit or time-served credit is applied only when the authoritative order and configured rules permit it.
- CORR-AT-037 — Sentence variation creates a new linked execution calculation without overwriting history.
- CORR-AT-038 — Appeal filing alone does not automatically suspend sentence execution.
- CORR-AT-039 — Only an authoritative stay, variation or appellate order changes legal execution status.
- CORR-AT-040 — Sentence completion is derived from authoritative terms and configured calculation rules.
- CORR-AT-041 — Release eligibility is not the same as an authorised release event.
- CORR-AT-042 — An estimated release date is labelled as an estimate and never represented as an order.
- CORR-AT-043 — Release occurs only on validated legal authority and configured operational checks.
- CORR-AT-044 — Release record identifies person, authority, order, institution, actor and actual simulation time.
- CORR-AT-045 — Physical departure is distinct from release authorisation.
- CORR-AT-046 — Release notification and recipient acknowledgement are separately recorded.
- CORR-AT-047 — Release cannot be backdated to conceal an operational delay.
- CORR-AT-048 — Release does not erase prior custody, sentence or institutional records.
- CORR-AT-049 — Where release is blocked, the reason and responsible authority are recorded.
- CORR-AT-050 — Recall requires an authoritative legal basis and configured process.
- CORR-AT-051 — Recall application or allegation is not itself a recall order.
- CORR-AT-052 — Recall execution records authority, location, time and receiving institution.
- CORR-AT-053 — Recall does not silently reinstate an expired or varied sentence.
- CORR-AT-054 — Post-release status is distinct from correctional custody status.
- CORR-AT-055 — Community supervision begins only under an authoritative order and configured trigger.
- CORR-AT-056 — Supervision terms reproduce the exact order and identify effective intervals.
- CORR-AT-057 — Supervision conditions are not invented by NPCs or the engine.
- CORR-AT-058 — Supervision appointments, contacts and compliance events occur only during active simulation time.
- CORR-AT-059 — Missed contact is recorded as an event, not automatically as breach or guilt.
- CORR-AT-060 — Alleged breach is distinct from verified breach and adjudicated finding.
- CORR-AT-061 — Risk assessments preserve method, assessor, date, source and uncertainty.
- CORR-AT-062 — Risk score does not automatically determine release, recall or placement.
- CORR-AT-063 — Supervision variation requires authorised order or configured authority.
- CORR-AT-064 — Supervision termination records the legal basis and effective date.
- CORR-AT-065 — Rehabilitation plan is distinct from sentence and supervision order.
- CORR-AT-066 — Participation in rehabilitation is not automatically compulsory unless ordered/configured.
- CORR-AT-067 — Programme attendance and completion are recorded separately.
- CORR-AT-068 — Programme referral does not prove attendance or success.
- CORR-AT-069 — Rehabilitation outcomes do not rewrite conviction or court findings.
- CORR-AT-070 — Education, work, health and support referrals reference source providers without duplicating their records.
- CORR-AT-071 — Clinical diagnosis remains owned by the relevant healthcare source, not BP-29.
- CORR-AT-072 — Sensitive health and vulnerability data are access restricted.
- CORR-AT-073 — Support needs are recorded without inferring protected or sensitive traits.
- CORR-AT-074 — Refusal or non-participation is not automatically a disciplinary breach.
- CORR-AT-075 — Programme availability and waiting lists respect configured provider capacity.
- CORR-AT-076 — Unavailable programmes do not silently extend a sentence.
- CORR-AT-077 — Correctional discipline is distinct from criminal conviction and court sentence.
- CORR-AT-078 — Disciplinary allegation, hearing, finding and sanction remain separate events.
- CORR-AT-079 — Disciplinary sanction cannot exceed configured authority or alter court sentence.
- CORR-AT-080 — Serious incidents preserve immediate safety actions and later review as separate records.
- CORR-AT-081 — Deaths in custody are recorded with correct person lifecycle and source authority.
- CORR-AT-082 — Deaths do not count as living population after canonical death effective time.
- CORR-AT-083 — Temporary absence, hospital transfer and escorted movement preserve legal custody status.
- CORR-AT-084 — Escape or unauthorised absence is a recorded incident, not automatic sentence extension.
- CORR-AT-085 — Return after absence requires identity and authority checks.
- CORR-AT-086 — External transfer is represented as an off-map reference, not a new playable jurisdiction.
- CORR-AT-087 — External agency handover records source, authority, time and acknowledgement.
- CORR-AT-088 — Every person-related action is linked to canonical identity, never name-only matching.
- CORR-AT-089 — Case-connected people promoted to full persistent records are never downgraded.
- CORR-AT-090 — Population promotion does not create a duplicate person or exceed the 10,000 cap.
- CORR-AT-091 — All correctional events use BP-37 canonical simulation time.
- CORR-AT-092 — No sentence, supervision, rehabilitation, release, recall or facility action progresses while paused or absent.
- CORR-AT-093 — No correctional NPC performs background work while simulation time is frozen.
- CORR-AT-094 — On resume, no elapsed wall-clock time is applied to sentence or supervision progression.
- CORR-AT-095 — Deadlines and reviews do not expire while the player is absent.
- CORR-AT-096 — Every scheduled review requires in-game time progression and an attributable event.
- CORR-AT-097 — NPC correctional knowledge is limited to observed, received or authorised information.
- CORR-AT-098 — Correctional staff cannot access BP-14 hidden occurrence truth.
- CORR-AT-099 — No correctional record, dialogue or report reveals hidden culprit/accomplice identity before exact bingo.
- CORR-AT-100 — No unsolicited investigative hints or next-step prompts are generated.
- CORR-AT-101 — Sentence and custody status are not used to infer guilt beyond the court record.
- CORR-AT-102 — Acquittal, dismissal and unresolved court outcomes remain distinct from conviction and sentence.
- CORR-AT-103 — A sentence cannot be attached to the wrong defendant or charge.
- CORR-AT-104 — Co-defendants retain independent sentence and correctional records.
- CORR-AT-105 — Multiple sentences for one person preserve separate order links and calculations.
- CORR-AT-106 — Correctional record conflicts with BP-28 order are flagged and not silently resolved.
- CORR-AT-107 — Corrections division acknowledges court order receipt and validation state.
- CORR-AT-108 — BP-28 remains authoritative for sentence terms and judicial variation.
- CORR-AT-109 — BP-26 remains authoritative for police custody until valid transfer is completed.
- CORR-AT-110 — BP-03 remains authoritative for identity, living status and population count.
- CORR-AT-111 — BP-29 does not alter police investigation or source evidence records.
- CORR-AT-112 — BP-29 does not make charging, verdict or judicial findings.
- CORR-AT-113 — BP-27 owns party-side legal workflow and appeal applications.
- CORR-AT-114 — BP-28 owns judicial appeal outcomes and authoritative orders.
- CORR-AT-115 — BP-38 identifiers and schemas are followed without local conflicting identity systems.
- CORR-AT-116 — BP-39 persistence preserves correctional event history across restart and recovery.
- CORR-AT-117 — Duplicate event replay does not create duplicate admissions, movements, sentences or releases.
- CORR-AT-118 — Partial persistence failure records completed steps and explicit incomplete handover state.
- CORR-AT-119 — Every state change records actor, role, authority, canonical time, source and reason.
- CORR-AT-120 — Every correction preserves original value and appends a reasoned correction event.
- CORR-AT-121 — Every read/export of restricted correctional records is permission checked and audited.
- CORR-AT-122 — Role-based access separates custody operations, case management, healthcare and protected records.
- CORR-AT-123 — Player access is governed by assigned role and in-world authority, not omniscient convenience.
- CORR-AT-124 — Text-only interface supports all essential correctional workflows.
- CORR-AT-125 — Optional graphics never contain exclusive sentence, custody or release facts.
- CORR-AT-126 — Reports distinguish court order, execution status, estimate and actual event.
- CORR-AT-127 — Reports show as-of simulation time, source versions and unresolved discrepancies.
- CORR-AT-128 — AI-generated summaries cite source records and preserve uncertainty.
- CORR-AT-129 — AI cannot invent sentence terms, release dates, breach findings or recall authority.
- CORR-AT-130 — AI cannot autonomously impose a sentence, release a person or recall a person.
- CORR-AT-131 — AI cannot override a court order or owning division's state.
- CORR-AT-132 — All S38 and S39 mapped requirements/tests are traceable to this specification and owner boundaries.
- CORR-AT-133 — Sentence and release dates reconcile with authoritative court orders and configured calculation rules.
- CORR-AT-134 — Financial penalties, restitution or compensation execution link to BP-34 without duplicate financial ledgers.
- CORR-AT-135 — Work assignments and institutional resources reconcile with BP-09, BP-33 and BP-34 ownership.
- CORR-AT-136 — Facility capacity, staffing and inventory changes reconcile atomically under X04.
- CORR-AT-137 — Correctional institution and service-provider records remain subordinate to the fixed Saltwater canon.
- CORR-AT-138 — At least 10,000-business canon is not changed by correctional design.
- CORR-AT-139 — No additional city or external playable territory is created.
- CORR-AT-140 — No Neon schema, seed, import or bulk write is authorised by this specification.

## 30. Source traceability

Original source remains `docs/governance/SALTWATER_MASTER_BLUEPRINT.json`, SHA `a882c4fc17f5654268a9b6d5823f5b9a4f3f1ade`. The following IDs are the exact source requirements/tests mapped to BP-29 in the 52→44 crosswalk.

| Source ID | Source requirement/test | BP-29 coverage |
|---|---|---|
| S38.R02 | Track procedural state and legal actors; preserve acquittals, dismissals and unresolved outcomes. | Sections 4, 7, 18, 22, 26 and 27; execution consumes only authoritative sentence/order events and preserves unresolved/conflicting legal status. |
| S39.R01 | Represent sentence execution, prison/community supervision, rehabilitation, release, recall and post-release status proportionately. | Sections 5–18, 22–29; correctional execution and supervision are authoritative BP-29 responsibilities, proportionate to police-first simulation scope. |
| S39.R02 | Maintain continuity between custody, court and person records. | Sections 4, 7–10, 17–20, 22, 26 and 27; BP-03 identity, BP-26 police custody and BP-28 court order continuity. |
| S39.T01 | Sentence and release dates reconcile with court orders. | Sections 7–8, 15–18, 22–23 and 29; exact order versions and reproducible configured calculations govern dates. |

Cross-cutting rules:
- X03: all sentence, custody, supervision, programme, release and recall events use BP-37 canonical time and freeze while paused/absent.
- X04: financial, population, inventory, staffing, resource and capacity changes reconcile atomically.
- X05: allegations, estimates, inferences, intelligence, opinions and adjudicated findings remain distinct.
- X06: original court/person/healthcare/custody records are preserved; corrections are additive and attributable.
- Global canon: one Saltwater city/jurisdiction; 10,000 living-person cap; at least 10,000 businesses; police-depth priority; permanent case-person promotion; text-first completeness; exact `bingo` reveal firewall; no offline progression; no Neon writes without explicit approval.

All four mapped BP-29 source IDs are explicitly traced. The source JSON and crosswalk are not modified by this specification.

## 31. Risk register

| Risk | Control |
|---|---|
| Sentence terms altered by correctional staff | BP-28 order remains authoritative; execution snapshot is read-only |
| Police custody confused with correctional custody | Explicit BP-26 handover and BP-29 admission |
| Release estimate treated as release authority | Separate eligibility, authority and physical departure |
| Appeal assumed to stay sentence | Only authoritative stay/variation changes execution |
| Recall triggered by allegation alone | Require configured legal authority and distinct execution |
| Sentence arithmetic guessed | Versioned deterministic calculation; unresolved state on ambiguity |
| Duplicate person created at admission | Canonical BP-03 identity and population accounting |
| NPCs progress while player absent | BP-37 freeze invariant |
| Clinical diagnosis fabricated | Healthcare source ownership and restricted references |
| Correctional simulation becomes society simulator | Proportionate institutions and operational scope |
| Hidden offender truth leaks into correctional records | Strict BP-14 knowledge firewall |
| Costs duplicated in correctional ledger | BP-34 remains financial authority |

## 32. Design completion checklist

- [ ] Correctional institutional architecture and authority defined.
- [ ] Sentence intake, validation and reconciliation defined.
- [ ] Sentence commencement and calculation defined.
- [ ] Police-to-correctional custody handover defined.
- [ ] Admission, placement and movement lifecycle defined.
- [ ] Custodial welfare, safety and incident records defined.
- [ ] Temporary absence, hospital transfer and unauthorised absence defined.
- [ ] Community supervision lifecycle defined.
- [ ] Rehabilitation and support programme boundaries defined.
- [ ] Release eligibility, authority and execution separated.
- [ ] Recall and return-to-custody lifecycle defined.
- [ ] Post-release status and person continuity defined.
- [ ] Appeal/stay/variation interfaces defined.
- [ ] Time freeze, NPC knowledge and player agency defined.
- [ ] Population cap and permanent person promotion preserved.
- [ ] Permissions, provenance, persistence and reporting defined.
- [ ] All 140 acceptance tests await BP-43 execution.
- [ ] All four mapped source requirement/test IDs traced.
- [ ] Fictional policy decisions remain explicit.
- [ ] No Neon schema, seed, import or bulk write made or authorised.

## 33. Status and next dependencies

This is a design draft, not approved fictional law, implemented functionality or executed test evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-30 — Department Governance**. BP-30 governs police departmental command, policy, oversight and institutional governance. BP-29 remains the owner of correctional sentence execution and post-sentence status; it does not govern the police department.
