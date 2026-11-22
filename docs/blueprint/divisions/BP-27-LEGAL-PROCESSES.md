# BP-27 — Legal Processes

**Division:** BP-27  
**Title:** Legal Processes  
**Specification version:** 1.0  
**Status:** DESIGNED_DRAFT  
**User approval:** PENDING  
**Implementation / test execution / verification:** NOT_STARTED  
**Authority:** Saltwater fictional canon and the adopted BP-01–BP-44 master blueprint. This document defines system behaviour and ownership; it does not enact or approve fictional law.

## 1. Purpose

BP-27 governs the complete legal-process workflow between police operational activity and judicial adjudication. It represents legal review, charging referrals and decisions, prosecution and defence participation, disclosure, procedural applications, representation, filings, legal directions, appeals and procedural status. It ensures that allegations, suspicion, arrest, charge, plea, adjudicated finding, conviction and sentence remain distinct, attributable and historically accurate.

The division supplies a coherent, playable legal-process layer for the single fictional Saltwater city-state. It supports complex cases, multiple defendants, multiple charges, linked proceedings, disputed evidence, disclosure obligations, no-charge outcomes, withdrawals, acquittals, convictions, appeals and unresolved proceedings without forcing a preferred result.

BP-27 is a workflow and record owner. It does not replace the court institution or judicial authority (BP-28), police case management (BP-15), investigation (BP-16), custody operations (BP-26), or sentence execution (BP-29).

## 2. Binding canon and governing principles

1. Saltwater is one sovereign city-state and one playable city/jurisdiction. No external playable territory or second city is created by legal-process records.
2. The total living population is capped at 10,000, including police, legal actors, defendants, witnesses and all other living persons. Each person is counted once. A case-connected person is permanently promoted to a full persistent person record; promotion never creates a duplicate person or bypasses the cap.
3. There must be at least 10,000 businesses. Legal institutions and service providers are represented proportionately and do not become a second deep society simulator.
4. The police system is the deepest simulation. Legal processes are detailed enough to create meaningful consequences and credible procedural workflows.
5. Text is the complete, permanent primary interface. Every essential BP-27 action must be possible in text. Optional graphics never carry exclusive information.
6. BP-37 is the sole simulation clock. No filing, disclosure, hearing, bail, remand, review, appeal or other legal deadline progresses while the player is absent or the game is paused. No NPC legal work, court scheduling, automated filing, notification or procedural state transition occurs off-screen.
7. Hidden world truth is separate from player-visible information and NPC knowledge. No BP-27 record, participant, lawyer, prosecutor, defence actor, generated dialogue, summary, filing, disclosure package, court copy, notification or test may reveal a hidden culprit/accomplice/perpetrator unless the player types exactly `bingo`. Do not provide unsolicited solution hints or tell the player what to investigate next.
8. Player agency is preserved. The game presents available records, procedural options, authority and consequences; it does not decide the player's actions or railroad an investigation or prosecution.
9. Every material fact retains its source, time, confidence/uncertainty and status. A legal actor may rely only on information received, observed or lawfully accessed under the configured fictional rules.
10. No real-world jurisdiction, statute, burden, deadline, right, caution, charging threshold, disclosure doctrine, bail test or court hierarchy is silently imported. Such details are configurable fictional canon and remain explicitly unresolved until adopted.
11. Preserve original records. Corrections, amendments, disclosure versions and legal decisions append attributable history; they never erase the prior state.
12. Blueprint approval does not authorise Neon database writes, migrations, seed data or imports.

## 3. Scope and exclusions

### 3.1 In scope

- Legal-process reference and proceeding-party records.
- Legal review requests and outcomes, including referral for advice or review.
- Charging referral preparation, submission, clarification and receipt.
- Charge decisions: charge, no charge, defer, request further information, partial decision, alternative charge, amendment, addition, withdrawal and discontinuance where configured.
- Charge particulars, offence links, defendant links, counts, joinder/severance requests and version history.
- Prosecution case preparation and procedural status.
- Defence participation and defence case/procedural submissions.
- Disclosure workflow: schedules, material categories, relevance decisions, unused material, sensitive/restricted material, redactions, privilege claims, requests, decisions, packages, recipients, acknowledgements and version control.
- Legal representation, conflicts, change of representative, unrepresented parties and legal support access.
- Interpreter, accessibility, communication and participation arrangements as configured.
- Bail/remand legal-process applications, conditions, variations, review and court-order interfaces.
- Procedural applications, responses, notices, filings, service, acknowledgements and directions.
- Hearing preparation and case readiness as a legal-party workflow, not the adjudicative hearing itself.
- Appeals, reviews, challenges and other post-decision procedural applications.
- Legal-process status, event chronology, procedural deadlines and unresolved issues.
- Disclosure and filing access controls, audit, provenance and historical correction.
- Interfaces with BP-15 through BP-29 and supporting divisions.

### 3.2 Out of scope

- Person identity, civil identity and population count: BP-03.
- Police mandate, rank, institutional command and legal authority architecture: BP-05/BP-30.
- Police employment and professional standards: BP-06/BP-31/BP-33.
- Incident, CAD and dispatch lifecycle: BP-12.
- Offence taxonomy and offence elements: BP-13.
- Hidden occurrence truth and crime generation: BP-14.
- Police case identity, ownership, assignment, chronology and closure: BP-15.
- Investigative plans, leads, tasks, investigative inferences and investigative decisions: BP-16.
- Victim/witness roles and safeguarding records: BP-17.
- Suspect/offender role and attribution status: BP-18.
- Interview process, original questions/answers, recordings and statements: BP-19.
- Surveillance collection and source records: BP-20.
- Intelligence records, source grading and dissemination: BP-21.
- Crime-scene control and original scene records: BP-22.
- Exhibit identity, packaging, seals, custody and continuity: BP-23.
- Forensic methods, raw results, interpretation and expert reports: BP-24.
- Arrest, warrant, search and seizure operational decisions/execution: BP-25.
- Police custody, detention clock, welfare, custody reviews and operational discharge: BP-26.
- Court institution, adjudicative hearings, judicial rulings, verdicts, findings, sentencing and authoritative judicial orders: BP-28.
- Sentence execution, prison/community supervision, rehabilitation, release and recall: BP-29.
- Simulation engine, global clock, relationship model, database schemas, persistence, interface, reporting framework and security framework: BP-35 through BP-44 as allocated below.

## 4. Ownership boundaries and authoritative records

| Subject | Authoritative owner | BP-27 responsibility |
|---|---|---|
| Person identity and living-person count | BP-03 | Reference canonical person IDs; never create duplicate identities |
| Offence taxonomy/elements | BP-13 | Reference versioned offence definition and jurisdictional configuration |
| Occurrence hidden truth | BP-14 | Never access for legal decisions or expose to actors |
| Police case lifecycle | BP-15 | Link legal proceedings to case; do not change case state |
| Investigation and investigative decisions | BP-16 | Receive authorised referrals/material; do not direct investigative next steps |
| Victim/witness role | BP-17 | Reference procedural participation and protection constraints |
| Suspect/offender role | BP-18 | Reference role/status without equating it to charge or guilt |
| Interview and statement originals | BP-19 | Request/receive controlled copies; preserve source/version links |
| Surveillance originals | BP-20 | Request/receive controlled copies; preserve source/version links |
| Intelligence | BP-21 | Record restricted disclosure/review treatment; never silently convert intelligence into evidence |
| Scene records | BP-22 | Request/receive authorised scene material |
| Exhibit custody and continuity | BP-23 | Track disclosure copies and source exhibit/version; BP-23 remains authoritative for physical/digital exhibit custody |
| Forensic examination/report | BP-24 | Track legal disclosure and use of exact report/data versions |
| Arrest/warrant/search/seizure | BP-25 | Receive operational records and refer legal challenges; do not rewrite operations |
| Police custody | BP-26 | Track legal application/order interface; BP-26 implements operational custody |
| Legal workflow, charge and disclosure | **BP-27** | Authoritative owner |
| Court institution and adjudication | BP-28 | Receive filings and track court outcomes by reference; never create judicial findings |
| Sentence execution | BP-29 | Send authoritative sentence/order references; never execute sentence |
| Department governance | BP-30 | Consume configured policy/authority, not substitute for judicial independence |
| Professional standards | BP-31 | Refer relevant complaints/concerns without determining them |
| Global time and deadlines | BP-37 | Own legal-process deadline records; derive all times from BP-37 |
| Record schemas, identifiers and constraints | BP-38 | Define domain semantics; use BP-38 governed schema/ID mechanisms |
| Persistence and recovery | BP-39 | Supply events and records for durable storage; do not own backup mechanics |
| Interface | BP-40 | Provide text-first workflows and optional presentation |
| Notifications/reporting | BP-41 | Request/emit procedural notices with delivery/receipt distinctions |
| Security and permissions | BP-42 | Define BP-27 scopes; enforce central access controls |
| QA and tests | BP-43 | Supply acceptance requirements and test fixtures |
| Configuration/change control | BP-44 | Consume versioned fictional legal configuration; no unilateral canon changes |

A referral, filing, legal opinion, charge or legal application is not a judicial order. Only BP-28 may create the authoritative record of a judicial ruling, verdict, finding, sentence or court-issued order. BP-27 records receipt, service, parties' responses and procedural consequences by reference to that BP-28 record.

## 5. Core legal-process entities

All identifiers are stable, unique and non-semantic. Exact ID syntax is a BP-38 implementation decision. Records use canonical IDs, never names alone, as joins.

### 5.1 Legal proceeding

Fields: proceeding_id; proceeding_type; jurisdiction_id; originating_case_ids; related_proceeding_ids; court_ref; created_at_sim; created_by; current_procedural_state; state_history; parties; charge_ids; legal_actor_assignments; next_event_ref; deadline_refs; disclosure_status; access_classification; source_refs; configuration_version; closure_status; created_event_id; updated_event_id.

A proceeding may include multiple defendants or charges only where configured rules permit. Linked proceedings do not merge histories. A single police case may generate multiple referrals or proceedings; a proceeding may reference multiple police cases without rewriting them.

### 5.2 Party and procedural role

Fields: party_link_id; proceeding_id; person_id or organisation_id; role; role_effective_from/to; representation_status; service/contact route; interpreter/accessibility needs reference; protected status reference; source; authority; status history.

Roles include defendant/respondent, prosecution, defence, complainant/applicant, interested party, witness participant, legal representative, prosecutor, defence representative, interpreter, authorised legal officer and other configured roles. One person may hold different roles in different proceedings or cases. A role in one proceeding never overwrites a different role elsewhere.

### 5.3 Legal referral

Fields: referral_id; originating_case_id; target_person_id; offence_definition_version; proposed_charge particulars; referring_actor; authority; material_index; inculpatory/exculpatory/neutral categories; unresolved issues; uncertainty; requested decision; submission version; recipient; submitted/received times; acknowledgement; clarification requests/responses; decision link; status history.

A referral is a request for legal consideration, not a charge, finding or proof. It may be incomplete, declined, returned, withdrawn, superseded or resubmitted with full version history.

### 5.4 Charge and charge version

Fields: charge_id; proceeding_id; defendant_person_id; offence_definition_id/version; count_number; particulars; alleged conduct/time/place as known; originating case/referral; decision-maker; decision authority; decision rationale; material references; status; effective time; version; amendment/supersession links; plea reference; court outcome reference.

Charge statuses include proposed, referred, under_review, clarification_required, authorised, filed, served, active, amended, added, stayed, withdrawn, discontinued, dismissed_by_court, determined and archived. Configured legal rules may add statuses through BP-44; statuses may not be conflated.

A charge is an allegation formally advanced through the configured process. It does not establish guilt, conviction, admissibility, evidential sufficiency or offender identity.

### 5.5 Disclosure item and package

Disclosure item fields: disclosure_item_id; source_record_id/version; source_owner; material_category; relevance assessment; disclosure decision; sensitivity/privilege/restriction basis; redaction version; reviewer; decision rationale; recipient eligibility; retention/preservation status; correction/supersession links.

Package fields: package_id; proceeding_id; recipient_party_id; purpose; authority; included item IDs and exact versions; excluded/withheld item references and decision basis; redaction manifest; manifest hash/reference; prepared_by; reviewed_by; prepared_at_sim; transmitted_at_sim; delivery status; acknowledgement; challenge/request references; superseding package.

A package is an immutable snapshot. Revisions create a new package and never mutate the package previously received.

### 5.6 Filing, application and procedural direction

A filing/application records: filing_id; proceeding_id; submitting party/actor; authority; filing type; requested relief/action; grounds; supporting and opposing materials; exact source versions; requested date/effect; submission version; recipient; received/accepted/rejected/returned status; response; service/notice records; linked BP-28 court event/order where applicable.

BP-27 may create party submissions and procedural requests. It may not issue judicial directions. A direction is authoritative only when linked to a BP-28 court-issued record.

### 5.7 Legal decision and advice

Fields: legal_decision_id; decision type; decision-maker; role/authority; proceeding/referral/charge; information considered with versions; excluded/unavailable material; uncertainty; rationale; alternatives; outcome; conditions; effective time; review route; signature/attestation where configured; supersession link.

A legal decision records the decision actually made and the basis available at that time. It is not a hidden generator outcome and may be wrong, incomplete, challenged or later corrected.

### 5.8 Representation, interpreter and participation arrangement

Records identify the represented party, representative, appointment/authority basis, scope, effective interval, conflict checks, withdrawal/change, communication channel, interpreter or accessibility service, language/format needs, consent/decline where relevant, provider, scheduling, actual attendance and outcome. Do not infer language, disability, capacity or vulnerability from identity or demographic attributes.

## 6. Legal actors and authority

Legal actors are canonical persons or organisations represented by BP-03/BP-04 and linked to roles, qualifications/appointments and permissions. Actor categories may include prosecutor, charging reviewer, legal adviser, defence representative, court liaison, disclosure reviewer, interpreter and configured legal officer.

Each action validates:
- actor identity and active role at the event time;
- exact authority source and version;
- jurisdiction and proceeding scope;
- delegation/appointment limits;
- conflict-of-interest restrictions;
- access to the material relied upon;
- required independent review or approval, if configured;
- absence of suspension, expiry or revocation of authority.

Rank, police seniority, case ownership or database access does not itself confer charging, prosecutorial, defence, judicial or other legal authority. BP-28 judicial actors remain institutionally separate from prosecution and defence roles. No actor may approve their own decision where configured independence rules prohibit it.

The legal actor catalogue, appointment criteria, independence rules, conflict rules and authority matrix are open fictional configuration decisions. Until defined, the system must mark an action as awaiting authority rather than inventing a power.

## 7. Legal review and charging referral

A legal review may be requested by an authorised police investigator, supervisor, prosecutor or other configured actor. The request identifies the precise question, target person, linked case(s), alleged offence(s), procedural status, requested decision and material index.

The referral material index must distinguish:
- source evidence and exact exhibit/version references;
- forensic reports and exact versions;
- interview/statement source records and versions;
- surveillance source records and versions;
- witness/victim accounts and source;
- intelligence and source restrictions;
- operational records, arrest/warrant/search records and custody status;
- inculpatory, exculpatory, neutral, contradictory and untested material;
- missing, unavailable, disputed or not-yet-received material;
- investigator opinion/inference from underlying source facts.

The system must not label material inculpatory or exculpatory without an attributed assessment and rationale. A missing record is not evidence that the event did not occur. A summary cannot replace an original.

Referral states: draft, submitted, received, awaiting_review, clarification_requested, clarification_received, decision_pending, accepted_for_charge, no_charge, deferred, returned_incomplete, withdrawn, superseded, closed. Each transition records actor, authority, canonical time, reason and exact version.

A legal reviewer may decide to authorise a charge, decline, defer, seek clarification or further material, approve only some proposed charges, select a configured alternative, or return the referral. No automatic charging occurs because an arrest was made, custody exists, an investigation is marked complete, or a hidden perpetrator is known to the engine.

## 8. Charge decision and lifecycle

A charge decision must identify the decision-maker and authority, defendant, offence definition/version, particulars, counts, supporting and contrary material, uncertainties, rationale, decision time, effective time, decision outcome and any conditions or review route.

The decision must be limited to information actually available and authorised at the time. It must preserve exculpatory and contradictory material, unresolved identity, disputed attribution, missing evidence and uncertainty. It must not treat intelligence, suspicion, arrest, an interview admission, forensic association or generated role as automatic proof.

Support multiple defendants, co-defendants, multiple counts, alternative charges, separate proceedings, linked cases, joint/severed proceedings where configured, partial decisions, amendments and withdrawn charges. Charge amendment creates a new version and preserves the original wording, decision and service history. A charge cannot be silently replaced by editing its particulars.

No-charge, deferred, withdrawn and discontinued outcomes remain explicit and searchable. A no-charge decision does not erase a police case, imply innocence, prove an allegation false or prohibit a later referral if new authorised material arises under configured rules. A charge does not create a conviction. A conviction exists only through the authoritative BP-28 adjudicative record.

Charge lifecycle transitions must be valid under the configured fictional rule set. If the rules are incomplete or contradictory, block the transition and record the unresolved configuration issue rather than guessing.

## 9. Prosecution workflow

BP-27 represents prosecution as a party/process role, not as an automatic consequence of police referral. It supports case review, charge selection, proceeding preparation, material requests, witness coordination references, disclosure preparation, filing, responses, case position, legal submissions, case readiness, discontinuance/withdrawal applications and appeal participation.

Prosecution actors can only access information within their configured authority and disclosure rules. Their decisions and submissions are attributable, versioned and challengeable. Prosecution statements, summaries and positions remain party assertions unless and until a BP-28 court record determines an issue.

Prosecution workflow states may include referred, accepted_for_review, preparation, disclosure_in_progress, filed, awaiting_response, ready_for_hearing, hearing_in_progress (court-owned event reference only), adjourned (BP-28 event reference), concluded, appeal_pending and closed. BP-27 does not simulate or adjudicate the hearing itself.

A prosecution may proceed on some charges and not others. Multiple defendants may have different procedural status, representation and disclosure. One defendant's plea or outcome does not automatically determine another's.

## 10. Defence workflow and procedural equality

BP-27 represents defence as an independent party role with its own authorised representatives, filings, applications, requests, responses, disclosed material access and procedural history. Defence records are not police-owned notes and are not automatically visible to investigators or prosecution.

Support represented and unrepresented defendants; changes or withdrawal of representation; conflicts; separate representation for co-defendants; confidential communications; legal assistance requests; defence disclosure where configured; challenges to charge particulars, evidence handling, disclosure decisions, jurisdiction, identity, procedure, bail/remand and other legal issues.

The system must not presume that a defendant has a lawyer, has waived representation, accepts a charge, understands a document or has received a notice. Each fact requires a source and event. Defence positions are party assertions, not adjudicated facts.

Confidential or privileged material is protected according to fictional configuration and BP-42. A defence request does not automatically grant access to restricted sources or protected identities. Refusal or restriction records the decision-maker, authority, reason, scope, review route and any permitted substitute/summary.

## 11. Disclosure governance

Disclosure is a controlled, versioned workflow that makes authorised material available to a specified recipient for a specified purpose. It is not a general export of the police database.

### 11.1 Material universe

Disclosure may include source material, exhibits, exhibit records, forensic reports, underlying data references, statements, recordings, transcripts, surveillance records, operational records, custody records, expert material, schedules, correspondence and other configured material. The source owner remains authoritative.

Every disclosure item records source owner, exact source record/version, material category, date acquired/created where known, provenance, completeness, restrictions, relevance assessment, decision, reviewer and rationale. Unavailable material, missing pages, failed recordings, incomplete exports and unknown versions remain explicitly marked.

### 11.2 Categories and decisions

The configurable category vocabulary must support at least:
- relied upon / proposed for reliance;
- potentially relevant;
- unused;
- exculpatory or potentially exculpatory;
- contradictory or impeaching;
- sensitive/restricted;
- privileged or confidential;
- irrelevant with recorded basis;
- unavailable, lost, destroyed under authorised process, or not held;
- duplicate or derivative, with canonical source link.

Categories are not mutually exclusive where the fictional rules permit multiple labels. The system must not silently suppress potentially exculpatory or contradictory material. Any decision to withhold, redact, defer or restrict is separately reasoned and reviewable.

### 11.3 Redaction and protected information

Redactions create immutable derivatives linked to an unchanged source version. Store redaction reason/category, author, reviewer, authority, scope, date and recipient-specific version. The original is never overwritten. Redaction must not fabricate context or alter meaning. A redacted copy is not represented as an unredacted original.

Protected witnesses, informants, minors where configured, medical data, personal contact details, confidential legal communications, intelligence sources, operational methods and security-sensitive information receive role- and purpose-specific restrictions. The exact protected categories and review mechanisms are open fictional policy choices.

### 11.4 Packages, service and challenge

A disclosure package is a fixed manifest of exact item versions and recipient-specific derivatives. Record preparer, independent reviewer where required, authority, purpose, time, delivery method, transmission result, recipient, receipt/acknowledgement and any failed or partial delivery. Sending is not proof of receipt; receipt is not proof of understanding.

A recipient may request clarification, missing material, an alternate format, review of a redaction/withholding decision or correction of an index. Each request and response is separately recorded. Superseding a package does not erase earlier delivery or create a false history that the earlier version was never received.

Disclosure deadlines and review intervals derive from BP-37 and configured fictional rules. They freeze while paused or absent. No package is generated or transmitted off-screen.

## 12. Procedural applications, filings and service

Support party applications and procedural filings including configured applications concerning charge particulars, joinder/severance, evidence handling, disclosure, representation, interpreter/accessibility, bail/remand, adjournment, anonymity/protection, jurisdiction, review, appeal and other fictional procedural matters.

Each filing records submitting party, authorised actor, requested action, grounds, supporting and opposing material, exact versions, recipient, submission time, acknowledgement, response deadline, response and status. A filing may be draft, submitted, received, rejected as invalid, returned for correction, accepted for processing, opposed, withdrawn, determined by court or superseded.

Service records identify document version, sender, recipient, authority, method, attempt, delivery status, receipt evidence and failure reason. Do not infer service from generation, dispatch or an unverified notification. Where delivery is partial or disputed, preserve both claims and source records.

Court acceptance, listing, direction and determination are BP-28 records. BP-27 links to the authoritative BP-28 event/order and records party-side actions or procedural consequences only.

## 13. Bail and remand legal process

BP-27 owns the legal application and party workflow for bail/remand and variations/reviews, subject to the fictional authority matrix. BP-28 owns the authoritative judicial decision/order. BP-26 owns implementation of police custody status, physical detention, operational release or transfer.

Records may include applicant, respondent, requested status, grounds, representations, material versions, proposed conditions, risks and uncertainty, decision reference, effective time, review date and variation history. Conditions are represented exactly as ordered/configured; no condition is invented or silently altered.

A bail application is not bail granted. A remand request is not a remand order. A legal decision to release is not an operational discharge until BP-26 executes and records the authorised action. BP-26 must not release a detainee solely because BP-27 has an incomplete, draft or unverified record. BP-27 must not alter BP-26 custody state directly.

Bail/remand time limits, eligibility, decision tests, conditions, review intervals and authority remain open fictional policy decisions. No real-world standard is assumed. All relevant clocks freeze when the simulation is paused.

## 14. Hearings and court interface

BP-27 prepares party positions, filings, disclosure, witness/expert coordination references and readiness information. It may record that a party attended, submitted material or received a direction only with a source event. It does not create hearing transcripts, judicial deliberations, rulings, verdicts or sentences.

BP-28 owns court listings, hearing events, judicial participants, evidence formally received, procedural rulings, findings, verdicts, sentence and court-issued orders. BP-27 links each relevant charge, party, filing, disclosure package and procedural status to the exact BP-28 record.

Adjournments, cancellations, non-attendance, partial hearings, mistrials or other outcomes are represented from BP-28 records. BP-27 may record the resulting party tasks and deadlines only after receiving an authoritative event. It must not invent a court date or infer a ruling from a narrative summary.

## 15. Appeals, reviews and challenges

BP-27 owns the procedural application and party-side tracking of appeals, reviews, challenges and requests to reconsider or vary legal decisions. BP-28 owns the adjudicative outcome and authoritative judicial order. BP-29 applies any sentence execution change arising from an authoritative order.

An appeal record identifies appellant, challenged decision/order, grounds, requested remedy, filing authority, filing version, time, applicable deadline, supporting material, respondent, response, status and linked court outcome. It supports accepted, rejected as out of time/invalid, pending, withdrawn, dismissed, allowed in whole/part, remitted, varied or other configured statuses, but only BP-28 may authoritatively determine the judicial outcome.

Filing an appeal does not automatically stay, vacate or alter a conviction, sentence, bail condition or order. Any stay or variation must be an authoritative BP-28 order. BP-29 must not change sentence execution without that authoritative source. Prior outcomes remain historically visible.

## 16. Procedural deadlines and canonical time

Every legal deadline, filing window, response period, disclosure date, review date, bail/remand review and hearing-related task is a BP-27 domain record based on BP-37 canonical simulation time and versioned fictional rules.

Store triggering event, rule/configuration version, calculation inputs, due time, responsible party/actor, notification policy, pause behaviour, extension/variation authority, status and completion evidence. Derived due times are reproducible and never replace source events.

The system must distinguish:
- due date calculated;
- notice prepared;
- notice sent;
- delivery attempted;
- delivered;
- receipt acknowledged;
- filing submitted;
- filing accepted;
- task completed.

No deadline expires while the player is absent or paused. No NPC files, responds, serves, reviews or makes a decision off-screen. Resume does not apply elapsed wall-clock time or execute a backlog of simulated actions. Time advances only through explicit in-game progression.

If a configured deadline rule is missing, contradictory or cannot be calculated, mark it unresolved and block automated expiry consequences. Never invent a deadline.

## 17. Legal knowledge, confidentiality and information barriers

An actor's knowledge is limited to information they personally observed, received, were told, or lawfully accessed under configured authority. Assignment to a proceeding does not grant access to every linked case, source, person, intelligence record, police database or hidden world record.

Separate prosecution, defence, court, police investigation, witness, victim and protected-source information according to configured fictional rules. Defence confidential communications must not be exposed to prosecution or police merely because they are stored in the same database. Prosecutorial work product and judicial material are separately restricted. Court access is governed by BP-28 and applicable configured orders.

Every read/export/disclosure of restricted material is authorised, purpose-bound and auditable. AI-generated summaries must use only the authorised input set, retain citations/source IDs and uncertainty, and cannot reveal excluded material through paraphrase, metadata, error messages or inferred hints.

## 18. Person and role continuity

All persons connected to a legal process resolve to one BP-03 person ID. If an unknown person is later identified, retain the prior unknown identity reference and append a reviewed link/correction; do not overwrite the history or merge distinct people on name similarity alone.

A person may simultaneously be a defendant in one proceeding, witness in another, victim in another, employee, family member or legal actor where the records support each role. Roles are scoped to their proceeding/case and effective interval. No legal role implies guilt or changes civil identity.

Anyone materially connected to a case or legal process is permanently promoted to full persistent simulation. Promotion is idempotent, does not duplicate identity, does not downgrade and must obey the 10,000 living-person cap. If the cap prevents a new living-person entry, the system blocks creation and records the capacity conflict; it must not silently exceed the cap or remove a living person.

## 19. Inputs and outputs

### Inputs

- BP-03: canonical person identities and population status.
- BP-04: legal institutions, providers, premises and organisation identity.
- BP-05/BP-30: institutional mandates, authority architecture and approved delegations.
- BP-13: offence definitions, elements and versioned classification.
- BP-15: case identity, lifecycle and links.
- BP-16: authorised investigation referral, investigative status and decision references.
- BP-17/BP-18: participant roles, identity/attribution status and relevant restrictions.
- BP-19: interview/statement source records and exact versions.
- BP-20/BP-21: surveillance/intelligence records and restrictions.
- BP-22/BP-23: scene/exhibit records, provenance and custody references.
- BP-24: forensic reports, data references, limitations and versions.
- BP-25: arrest, warrant, search, seizure and operational review records.
- BP-26: custody status, clock, welfare/transfer/release implementation references.
- BP-28: court listings, hearing events, judicial decisions, orders, verdicts and sentence records.
- BP-29: sentence execution status and implementation references.
- BP-37: canonical simulation time and pause state.
- BP-38/BP-39: schema, identifiers, provenance, persistence and recovery.
- BP-41/BP-42: notifications, reporting, security and permissions.
- BP-44: approved fictional legal configuration and change history.

### Outputs

- Legal review requests and attributed decisions.
- Charging referrals, clarification requests, charging decisions and versioned charge records.
- Proceeding and party-role links.
- Prosecution/defence procedural workflow records.
- Disclosure item assessments, redactions, packages, delivery and acknowledgement records.
- Legal applications, filings, service and responses.
- Bail/remand applications and court-order interface events.
- Appeal/review/challenge procedural records.
- Legal deadlines, tasks, notifications and exception records.
- Court-facing material manifests and source-version references.
- Audit events, legal-process reports and status summaries.
- Authorised handover events to BP-28 and BP-29.

BP-27 emits domain events; downstream divisions validate and apply their own authoritative state changes. No event directly mutates another division's owned record without that owner's contract.

## 20. State transitions and event contract

All state transitions are explicit, validated and append-only. A transition records event_id, entity_id, prior_state, new_state, actor/person or system identity, actor role, authority and rule version, canonical simulation time, source records and versions, rationale, result, correlation/idempotency key, schema version and related entity IDs.

Core event types include:
- legal_review_requested / received / clarified / decided;
- referral_created / submitted / received / clarification_requested / clarification_received / returned / withdrawn / superseded;
- charge_decided / authorised / declined / deferred / filed / served / amended / added / stayed / withdrawn / discontinued;
- proceeding_opened / party_linked / party_role_changed / proceeding_linked / proceeding_closed;
- representation_requested / appointed / changed / withdrawn / conflict_flagged;
- interpreter_requested / arranged / attended / unavailable;
- disclosure_item_registered / assessed / restricted / redacted / reviewed;
- disclosure_package_prepared / approved / transmitted / delivery_failed / received / acknowledged / challenged / superseded;
- filing_prepared / submitted / received / returned / accepted_for_processing / opposed / withdrawn;
- service_attempted / delivered / failed / disputed / acknowledged;
- bail_application_submitted / varied / withdrawn / court_order_received;
- appeal_submitted / received / challenged / withdrawn / court_outcome_received;
- deadline_created / varied / suspended / completed / unresolved;
- court_event_linked / court_order_received / court_finding_received;
- correction_proposed / approved / appended / superseded;
- access_granted / denied / disclosed / exported / revoked.

Events are idempotent. Retrying a submission cannot create duplicate charges, proceedings, packages, filings, service events or appeal records. Partial failures retain the successfully completed sub-events and an explicit incomplete state; replay resumes safely without duplicating them.

## 21. Permissions and security

BP-42 owns global security and permission enforcement. BP-27 defines domain scopes including:
- legal referral and charging material;
- charging decision and reviewer-only rationale;
- prosecution case material;
- defence submissions and confidential communications;
- disclosure schedules, source material and redaction decisions;
- protected witness/informant identities;
- medical, safeguarding and vulnerability references;
- intelligence source identities and restricted material;
- legal advice and privileged/confidential records;
- bail/remand applications and conditions;
- appeal/review materials;
- court copies and judicially restricted material;
- audit, export and correction privileges.

Permissions are evaluated per actor, role, proceeding, party, purpose, record category, source restriction and event time. Least privilege applies. Rank, employment, database access, police case assignment, prosecution role or defence role alone does not grant universal access. Access may be revoked; prior lawful access remains in audit history.

No hidden-truth field or generator-only source may be included in any BP-27 permission scope. There is no general administrator bypass for player-facing output that defeats the exact `bingo` rule.

## 22. Exceptions and edge cases

The system must explicitly handle, without silent repair:
1. Referral submitted to wrong legal recipient.
2. Referral lacks authority or has conflicting authority.
3. Incomplete, unreadable or corrupt referral material.
4. Missing original, unavailable source or unknown version.
5. Conflicting or mistaken person identity.
6. Multiple same-name defendants.
7. Multiple charges or counts with different decisions.
8. Alternative or amended charge after filing.
9. Charge particulars do not match offence-definition version.
10. Proposed charge lacks required configured elements.
11. Exculpatory material omitted from referral or index.
12. Intelligence presented as evidence without an authorised conversion/source.
13. Contradictory witness or forensic material.
14. Evidence source later corrected or withdrawn.
15. Arrest without charge; charge without arrest; charge while person is not in police custody.
16. No-charge, deferred, returned, withdrawn or discontinued referral.
17. Charge filed but service failed or disputed.
18. Defendant cannot be located or identity remains uncertain.
19. Multiple defendants with incompatible interests or separate representation.
20. Defence representative conflict or withdrawal.
21. Defendant unrepresented or refuses/declines offered support.
22. Interpreter unavailable, unsuitable or communication unsuccessful.
23. Accessibility or participation arrangement unavailable.
24. Protected witness or sensitive source material requires restriction.
25. Privilege/confidentiality claim disputed.
26. Disclosure item missing, withheld, redacted, delayed or incorrectly categorised.
27. Redaction derivative accidentally omits too much or changes meaning.
28. Disclosure package partially transmitted, corrupted, duplicated or delivered to wrong recipient.
29. Recipient disputes receipt or package completeness.
30. New material arises after prior disclosure.
31. Earlier disclosure package later found inaccurate or incomplete.
32. Filing submitted to wrong forum or returned as invalid.
33. Service attempt fails or recipient disputes service.
34. Filing deadline cannot be calculated from approved rules.
35. Deadline extension requested, refused or varied.
36. Player pauses or exits before any procedural action completes.
37. Court hearing is adjourned, cancelled, partially completed or rescheduled.
38. Court order is delayed, disputed, varied or corrected.
39. Bail/remand application differs from court's actual order.
40. BP-26 operational custody state has not yet implemented a court-directed change.
41. Appeal is late, incomplete, withdrawn or filed by an unauthorised actor.
42. Appeal filed but no stay order exists.
43. Court outcome applies to only some defendants or charges.
44. Acquittal/dismissal/no-charge must not erase police investigative history.
45. Conviction or sentence record conflicts with charge version.
46. Sentence execution record has not received authoritative BP-28 order.
47. Legal actor's appointment expires or is revoked during a proceeding.
48. Conflict of interest discovered after prior action.
49. Material was accessed by an unauthorised actor.
50. Record correction affects a prior disclosure or filing.
51. Duplicate submission/retry or interrupted persistence operation.
52. NPC or AI attempts to use hidden generator truth.
53. A legal actor claims knowledge without a valid source.
54. Population cap would be exceeded by person creation/promotion.
55. Configuration is missing, contradictory or changed mid-proceeding.
56. External/off-map source is referenced without creating external playable geography.
57. A legal process depends on an unimplemented division or unsupported event.
58. Court outcome is unknown, pending or not received.
59. Record is disputed but not yet adjudicated.
60. Summary conflicts with the underlying source record.

For every exception, preserve the attempted action, actor, authority, source, time, known state, failure reason, affected records and next authorised resolution path. Do not fabricate a successful outcome, silently discard material or infer a legal conclusion.

## 23. Cross-system effects and handover contracts

### BP-15/BP-16
A legal referral may be linked to a police case and investigation. BP-27 cannot close, reassign or rewrite the police case or investigation. A legal request for additional information is a request, not an instruction that tells the player what to investigate next.

### BP-18
Charge status is separate from suspect/offender status. BP-18 retains role and attribution history. BP-27 may send a charge event reference but cannot promote a person to offender or alter attribution.

### BP-19/BP-20/BP-21
BP-27 requests controlled versions and restrictions. Original interview, surveillance and intelligence records remain with their source owners. Disclosure does not convert intelligence into evidence or make an actor omniscient.

### BP-23/BP-24
BP-23 retains exhibit custody and source integrity; BP-24 retains forensic method/results/report ownership. BP-27 records exact versions disclosed, relied upon or challenged. A legal challenge does not rewrite an exhibit or forensic result.

### BP-25/BP-26
Arrest/search/seizure remains BP-25. Police detention, custody clock and operational discharge remain BP-26. BP-27 legal decisions and BP-28 court orders are sent as authenticated references; BP-26 validates and implements its own operational transition.

### BP-28
BP-27 submits party filings and receives court events/orders/findings. BP-28 is the sole authoritative owner of adjudicative events and judicial outcomes. A missing court response remains pending, not presumed.

### BP-29
BP-27 transmits exact authoritative BP-28 sentence/order references. BP-29 determines and records execution, supervision and release/recall implementation. A charge or conviction alone does not start a sentence.

### BP-37/BP-38/BP-39/BP-42
All time uses BP-37. All identifiers, schemas and constraints use BP-38. Durable state and recovery use BP-39. Access enforcement uses BP-42. Domain events must be replay-safe and preserve provenance.

## 24. Text-first interface requirements

The interface must support plain-text commands or equivalent accessible controls to:
- list legal referrals, proceedings, parties, charges, filings, disclosure packages and deadlines within the player's authority;
- inspect one record with status, source, version, authority, chronology and access restrictions;
- create, amend, submit, withdraw or review an authorised referral;
- inspect and decide a charging referral where the player has the required role;
- inspect charge particulars and immutable versions;
- prepare, review and transmit authorised disclosure packages;
- inspect source versions and redaction manifests;
- record receipt, challenge, correction request or missing-material response;
- prepare and submit party filings/applications;
- record service attempts and acknowledgements;
- inspect bail/remand applications and linked court orders;
- inspect appeal status and linked adjudicative outcome;
- inspect procedural deadlines and explain their rule/source;
- view a chronology without replacing source records;
- inspect permissions and explain why an action is unavailable;
- export authorised reports with provenance and version manifests.

A command must not expose a record merely because the user knows its ID. Unauthorised results must not reveal restricted content through error messages, counts, autocomplete, search snippets or metadata.

## 25. Reporting and summaries

BP-27 may produce referral summaries, charge status reports, disclosure indexes, package manifests, filing registers, procedural chronologies, deadline lists, party/representation lists, appeal status and court-order receipt reports.

Every summary identifies its as-of simulation time, scope, author/system, filters, source record IDs and versions, omitted/restricted sections, uncertainty and generation version. It is a derivative and never replaces the authoritative source records. A summary must not state guilt or hidden truth, infer service/receipt, convert an allegation into a fact, or omit a known exculpatory/contradictory source in a misleading manner.

## 26. Audit, correction and retention

Every create/read/export/disclose/decision/transition that the configured audit policy classifies as material is logged with actor, role, authority, purpose, canonical time, record, exact version, source, action and result. Failed and denied access attempts are recorded without exposing protected contents.

Corrections append a linked record containing original value/reference, corrected value/reference, reason, source, actor, authority, review, effective time and affected downstream records. Historical filings, disclosure packages, charge versions, service attempts and decisions remain queryable as they existed at the time.

Retention, sealing, archiving and deletion rules are configurable fictional policy. A preservation hold blocks destructive disposal under configured authority. No source owner may delete or rewrite material merely because BP-27 has closed a proceeding. Any lawful deletion/retention action is recorded and must preserve required audit/provenance metadata.

## 27. Configuration and unresolved fictional policy

BP-44 governs versioned configuration. The following must remain open until explicitly decided; this specification does not invent values:

1. Legal hierarchy, court levels, jurisdiction and appeal routes.
2. Prosecutorial institution, defence services and legal actor categories.
3. Charging authority, eligibility, delegation and review/approval matrix.
4. Charging threshold/decision criteria and required offence-element assessment.
5. Legal referral form, required fields, recipients and review workflow.
6. Charge terminology, count conventions, joinder/severance and amendment rules.
7. Prosecution/defence procedural rights, duties and filing categories.
8. Disclosure doctrine, material categories, timing, review and remedies.
9. Privilege, confidentiality, sensitive material and protected-identity rules.
10. Redaction standards and independent review.
11. Representation, appointment, conflicts and unrepresented-party support.
12. Interpreter and accessibility provision.
13. Bail/remand eligibility, criteria, decision-maker and condition catalogue.
14. Custody review, bail/remand clocks and BP-26 interface rules.
15. Filing deadlines, service methods, proof and extension authority.
16. Hearing readiness and party attendance rules.
17. Appeal grounds, time limits, permissions and stay rules.
18. Record sealing, retention, disclosure and preservation policy.
19. Legal actor qualifications, appointment, independence and conflicts.
20. Court order service and operational implementation protocols.
21. Legal process priority and workload/queue rules.
22. Fictional law versioning, transitional rules and pending-proceeding treatment.

When a rule is unresolved, present the gap and block any consequential automatic action. Never import real-world legal doctrine by implication.

## 28. Acceptance tests

These are required BP-43 acceptance tests. They are specification criteria, not evidence that implementation has been tested. IDs are unique and sequential.

- LEGAL-AT-001 — Every proceeding has a stable unique ID.
- LEGAL-AT-002 — Every proceeding resolves to the single Saltwater jurisdiction or an explicitly marked off-map reference.
- LEGAL-AT-003 — Every party resolves to one canonical BP-03 identity or organisation.
- LEGAL-AT-004 — Multiple roles for one person are scoped and do not overwrite each other.
- LEGAL-AT-005 — A legal referral is distinct from a charge.
- LEGAL-AT-006 — A charge is distinct from arrest, suspicion and offender status.
- LEGAL-AT-007 — A charge does not imply guilt or conviction.
- LEGAL-AT-008 — A conviction exists only from an authoritative BP-28 outcome.
- LEGAL-AT-009 — A sentence exists only from an authoritative BP-28 order.
- LEGAL-AT-010 — BP-27 cannot create a judicial finding or order.
- LEGAL-AT-011 — Every legal actor action validates role and authority at event time.
- LEGAL-AT-012 — Rank or police seniority does not grant legal authority.
- LEGAL-AT-013 — Expired or revoked appointment cannot authorise a new action.
- LEGAL-AT-014 — Conflicts of interest are represented and enforced under configuration.
- LEGAL-AT-015 — Missing authority blocks a consequential transition.
- LEGAL-AT-016 — Legal hierarchy is versioned fictional configuration.
- LEGAL-AT-017 — No real-world statute or threshold is silently imported.
- LEGAL-AT-018 — A referral records the originating case and target person.
- LEGAL-AT-019 — A referral records offence definition and version.
- LEGAL-AT-020 — A referral records the decision requested.
- LEGAL-AT-021 — A referral indexes source material by exact ID/version.
- LEGAL-AT-022 — Inculpatory, exculpatory, neutral and contradictory material can be distinguished.
- LEGAL-AT-023 — Material classification is attributed and reasoned.
- LEGAL-AT-024 — Missing material remains explicitly missing or unavailable.
- LEGAL-AT-025 — A referral may be returned for clarification without losing its original.
- LEGAL-AT-026 — A referral may be deferred or declined.
- LEGAL-AT-027 — A referral may concern multiple charges with separate decisions.
- LEGAL-AT-028 — Referral submission is idempotent.
- LEGAL-AT-029 — A charge decision identifies decision-maker and authority.
- LEGAL-AT-030 — A charge decision records material considered and exact versions.
- LEGAL-AT-031 — A charge decision preserves uncertainty and contrary material.
- LEGAL-AT-032 — A charge decision records rationale and alternatives.
- LEGAL-AT-033 — A charge may be authorised, declined or deferred.
- LEGAL-AT-034 — Partial charge decisions are supported.
- LEGAL-AT-035 — Alternative charges are separately identified.
- LEGAL-AT-036 — Charge particulars are versioned and immutable after issue.
- LEGAL-AT-037 — Charge amendment preserves the previous version.
- LEGAL-AT-038 — Charge withdrawal/discontinuance preserves prior history.
- LEGAL-AT-039 — No-charge does not close the police case automatically.
- LEGAL-AT-040 — No-charge does not imply allegation false or person innocent.
- LEGAL-AT-041 — An arrest does not automatically create a charge.
- LEGAL-AT-042 — Custody does not automatically create a charge.
- LEGAL-AT-043 — Hidden generator truth cannot be used as charging grounds.
- LEGAL-AT-044 — Offence definition mismatch blocks or flags the charge.
- LEGAL-AT-045 — Multiple defendants have independent charge states.
- LEGAL-AT-046 — Multiple counts retain separate particulars and outcomes.
- LEGAL-AT-047 — Linked proceedings do not merge their histories.
- LEGAL-AT-048 — Charge status never overwrites BP-18 suspect/offender status.
- LEGAL-AT-049 — Prosecution is an explicit party/process role.
- LEGAL-AT-050 — Prosecution decisions are attributable and versioned.
- LEGAL-AT-051 — Prosecution summaries link to underlying source versions.
- LEGAL-AT-052 — Prosecution workflow supports incomplete and disputed material.
- LEGAL-AT-053 — Prosecution may proceed on some charges but not others.
- LEGAL-AT-054 — Prosecution workflow does not simulate a judicial hearing.
- LEGAL-AT-055 — Prosecution statements remain party assertions until adjudicated.
- LEGAL-AT-056 — Defence is an independent party/process role.
- LEGAL-AT-057 — Defence submissions are not police-owned notes.
- LEGAL-AT-058 — Defence records are not automatically visible to prosecution.
- LEGAL-AT-059 — Represented and unrepresented parties are supported.
- LEGAL-AT-060 — Representation appointment and withdrawal are versioned.
- LEGAL-AT-061 — Co-defendant conflicts can be represented.
- LEGAL-AT-062 — Confidential defence communications are restricted.
- LEGAL-AT-063 — A defendant is not presumed to understand or receive a notice.
- LEGAL-AT-064 — Defence positions remain party assertions.
- LEGAL-AT-065 — Interpreter need is not inferred from identity or ethnicity.
- LEGAL-AT-066 — Interpreter request, assignment and attendance are distinct events.
- LEGAL-AT-067 — Interpreter unavailability is explicitly recorded.
- LEGAL-AT-068 — Accessibility arrangements can be requested and tracked.
- LEGAL-AT-069 — Refusal or inability to participate is recorded with source.
- LEGAL-AT-070 — Legal actor knowledge is limited to received/observed/authorised information.
- LEGAL-AT-071 — Disclosure items link to an authoritative source owner.
- LEGAL-AT-072 — Disclosure references an exact source record version.
- LEGAL-AT-073 — Disclosure material category is explicit.
- LEGAL-AT-074 — Unused material can be indexed.
- LEGAL-AT-075 — Potentially exculpatory material is not silently suppressed.
- LEGAL-AT-076 — Contradictory material is preserved and indexed.
- LEGAL-AT-077 — Sensitive material has a separate restriction decision.
- LEGAL-AT-078 — Privilege/confidentiality claims are recorded, not assumed.
- LEGAL-AT-079 — Withholding decisions identify authority and rationale.
- LEGAL-AT-080 — Disclosure decisions are reviewable under configuration.
- LEGAL-AT-081 — Redactions create derivatives and preserve the original.
- LEGAL-AT-082 — Redaction records author, reviewer, scope and reason.
- LEGAL-AT-083 — Redacted copies are not represented as originals.
- LEGAL-AT-084 — Redaction does not fabricate or distort source meaning.
- LEGAL-AT-085 — Protected identities are restricted by recipient and purpose.
- LEGAL-AT-086 — Intelligence restrictions remain linked to BP-21 source rules.
- LEGAL-AT-087 — A disclosure package has an immutable manifest.
- LEGAL-AT-088 — A package identifies recipient, purpose and authority.
- LEGAL-AT-089 — A package records exact item and derivative versions.
- LEGAL-AT-090 — A package records preparer and required reviewer.
- LEGAL-AT-091 — Package transmission is distinct from delivery.
- LEGAL-AT-092 — Delivery is distinct from acknowledgement.
- LEGAL-AT-093 — Partial transmission is represented accurately.
- LEGAL-AT-094 — Wrong-recipient transmission triggers an explicit incident/exception.
- LEGAL-AT-095 — A superseding package does not erase the earlier package.
- LEGAL-AT-096 — A recipient can request missing or corrected material.
- LEGAL-AT-097 — Disclosure challenge and response are separately recorded.
- LEGAL-AT-098 — New material after disclosure can trigger a new package version.
- LEGAL-AT-099 — Disclosure deadlines use BP-37 canonical time.
- LEGAL-AT-100 — No disclosure action progresses while paused or absent.
- LEGAL-AT-101 — Filing records identify submitting party and authorised actor.
- LEGAL-AT-102 — Filing records requested action and grounds.
- LEGAL-AT-103 — Filing records exact supporting material versions.
- LEGAL-AT-104 — Filing status distinguishes draft, submitted and received.
- LEGAL-AT-105 — Returned or rejected filings preserve the submitted version.
- LEGAL-AT-106 — Filing amendments create a new version.
- LEGAL-AT-107 — Service records identify document version and recipient.
- LEGAL-AT-108 — Service attempt is distinct from successful delivery.
- LEGAL-AT-109 — Delivery is distinct from receipt acknowledgement.
- LEGAL-AT-110 — Disputed service is preserved as disputed.
- LEGAL-AT-111 — BP-27 cannot create a judicial direction.
- LEGAL-AT-112 — Court listing and hearing events reference BP-28.
- LEGAL-AT-113 — Court order receipt links to the authoritative BP-28 order.
- LEGAL-AT-114 — A missing court order is not inferred from narrative.
- LEGAL-AT-115 — Adjournment/cancellation is sourced from BP-28.
- LEGAL-AT-116 — BP-27 records party tasks arising from court events.
- LEGAL-AT-117 — A bail application is not a bail order.
- LEGAL-AT-118 — A remand request is not a remand order.
- LEGAL-AT-119 — Bail/remand authority is versioned fictional configuration.
- LEGAL-AT-120 — Bail/remand conditions match the exact authoritative order.
- LEGAL-AT-121 — BP-26 alone implements operational custody transition.
- LEGAL-AT-122 — BP-27 cannot directly discharge a detainee.
- LEGAL-AT-123 — A draft or unverified order cannot trigger release.
- LEGAL-AT-124 — Appeal filing does not automatically stay an order.
- LEGAL-AT-125 — A stay/variation requires an authoritative BP-28 order.
- LEGAL-AT-126 — Appeal records identify challenged order and grounds.
- LEGAL-AT-127 — Appeal filing deadline uses configured rule and BP-37.
- LEGAL-AT-128 — Appeal procedural status is distinct from judicial outcome.
- LEGAL-AT-129 — Only BP-28 records authoritative appeal determination.
- LEGAL-AT-130 — BP-29 receives sentence changes only from authoritative order.
- LEGAL-AT-131 — Acquittal/dismissal does not erase police investigative history.
- LEGAL-AT-132 — Conviction applies only to the correct defendant and charge version.
- LEGAL-AT-133 — One defendant's outcome does not determine co-defendant outcomes.
- LEGAL-AT-134 — No charge, acquittal, conviction and sentence remain distinct.
- LEGAL-AT-135 — Every deadline records trigger and rule version.
- LEGAL-AT-136 — Unresolved deadline rules do not produce invented due dates.
- LEGAL-AT-137 — Deadline extensions require configured authority and history.
- LEGAL-AT-138 — No deadline expires while the player is absent.
- LEGAL-AT-139 — Resume does not apply wall-clock elapsed time.
- LEGAL-AT-140 — No NPC files, serves or decides legal matters off-screen.
- LEGAL-AT-141 — All time-dependent records use BP-37.
- LEGAL-AT-142 — All material state changes are append-only and attributable.
- LEGAL-AT-143 — Corrections preserve original value and source.
- LEGAL-AT-144 — Disclosure, filing and decision histories remain queryable.
- LEGAL-AT-145 — Every access/export/disclosure is permission checked.
- LEGAL-AT-146 — Least privilege applies independently of rank.
- LEGAL-AT-147 — Defence confidential records are not exposed to police by default.
- LEGAL-AT-148 — Restricted source metadata does not leak through search/error output.
- LEGAL-AT-149 — NPC knowledge never exceeds observed/received/authorised information.
- LEGAL-AT-150 — Hidden culprit/accomplice identity never appears before exact bingo.
- LEGAL-AT-151 — No unsolicited investigative hints or next-step prompts are generated.
- LEGAL-AT-152 — AI summaries retain source links and uncertainty.
- LEGAL-AT-153 — AI summaries cannot convert allegation into fact or finding.
- LEGAL-AT-154 — A person in multiple proceedings resolves to one BP-03 identity.
- LEGAL-AT-155 — Role changes do not overwrite other proceeding roles.
- LEGAL-AT-156 — Case-connected legal participants are permanently promoted.
- LEGAL-AT-157 — Promotion is idempotent and never downgrades.
- LEGAL-AT-158 — Population count never exceeds 10,000 living people.
- LEGAL-AT-159 — Population-cap conflict blocks creation rather than exceeding cap.
- LEGAL-AT-160 — Legal institution/provider references resolve to BP-04 entities.
- LEGAL-AT-161 — All essential legal workflows are available in text-only interface.
- LEGAL-AT-162 — Optional visuals derive from canonical records and add no exclusive facts.
- LEGAL-AT-163 — Event retries do not duplicate referrals, charges or filings.
- LEGAL-AT-164 — Replay does not duplicate disclosure transmission or receipt.
- LEGAL-AT-165 — Partial failure preserves completed events and explicit incomplete status.
- LEGAL-AT-166 — Every material event records actor, authority, time and source.
- LEGAL-AT-167 — Every decision records rationale and exact material considered.
- LEGAL-AT-168 — A proceeding may remain unresolved without forced closure.
- LEGAL-AT-169 — No legal outcome is generated solely to advance gameplay.
- LEGAL-AT-170 — No legal actor receives hidden generator truth.
- LEGAL-AT-171 — All source-mapped requirements and tests are traceable to BP-27.
- LEGAL-AT-172 — No Neon write is authorised by this specification.

## 29. Source traceability

Original source: `docs/governance/SALTWATER_MASTER_BLUEPRINT.json`. The source JSON remains unchanged. Source IDs refer to original source-array positions (1-based). Crosswalk IDs are preserved exactly.

| Source ID | Original requirement/test | BP-27 coverage |
|---|---|---|
| S01.R02 | Define legal hierarchy, authority sources, emergency powers, separation of functions and jurisdictional limits. | Sections 2, 4, 6 and 27; fictional legal hierarchy and actor authority are versioned configuration; BP-27 owns legal-process workflow, not sovereign canon or judicial institution. |
| S12.R03 | Support lawful in-world retrieval and controlled disclosure. | Sections 11, 17, 21, 24 and 26; controlled recipient/purpose/version disclosure and access audit. |
| S29.R03 | Support occurrence, reporting, case and legal status distinctions across crime processes. | Sections 4, 7–8 and 23; offence and hidden occurrence owners remain BP-13/BP-14; legal charge and procedural state are separate. |
| S30.R02 | Link case management and investigative command with legal processes and court outcomes. | Sections 4, 7, 19 and 23; BP-15/BP-16 remain authoritative for case/investigation; BP-27 links referrals and legal outcomes. |
| S31.R02 | Keep allegation, suspicion, evidential support, charge and finding distinct. | Sections 2, 4, 8, 18 and 28; separate role, evidence, charge and adjudication state. |
| S34.R01 | Represent interview planning, cautions/procedural status, participants, recordings, notes, questions, answers, breaks, disclosure and statement versions. | Sections 4, 11, 17 and 23; BP-19 owns original interview/statement records; BP-27 receives controlled versions for legal workflow/disclosure. |
| S35.R02 | Preserve distinction between intelligence and evidence and support authorised information handling. | Sections 4, 11, 17 and 23; BP-21 owns intelligence; disclosure does not silently convert it into evidence. |
| S37.R01 | Represent grounds, authority, applications, approvals, execution, searches, seizure, transport, booking, detention, welfare, reviews and release. | Sections 4, 13 and 23; BP-25/BP-26 own operational events; BP-27 owns subsequent legal applications/process only. |
| S37.R03 | Separate operational action from later legal decision. | Sections 2, 4, 8, 13 and 23; arrest/search/custody events remain separate from charge, bail/remand and court decision. |
| S37.T01 | Custody and warrant events satisfy configured fictional rules and chronological constraints. | Sections 13, 16, 20 and 28; BP-25/BP-26 operations and BP-27 legal process use configured authority and BP-37 time. |
| S38.R01 | Represent charging decisions, disclosure, prosecution, defence, hearings, evidence, rulings, verdicts, sentencing, appeals and case outcomes. | Sections 7–16 and 23; BP-27 owns charging, disclosure, prosecution/defence and appeal workflow; BP-28 owns hearings, evidence adjudication, rulings, verdicts and sentencing. |
| S38.R02 | Track procedural state and legal actors; preserve acquittals, dismissals and unresolved outcomes. | Sections 5–10, 15–18, 20–22 and 28; actor authority, independent party roles, procedural states, acquittal/dismissal and unresolved proceedings retained. |
| S38.R03 | Feed outcomes back into records without rewriting investigative history. | Sections 4, 8, 14–15, 23 and 26; authoritative BP-28 outcomes link to BP-15/BP-16 without mutating original investigation history. |
| S38.T01 | Court outcomes link to the correct charges, defendants and evidence versions. | Sections 5, 8, 11, 14–15 and 28; immutable charge IDs, party IDs, exact disclosure/source versions and BP-28 order references. |

Cross-cutting rules:
- X03: all legal deadlines and time-dependent facts use BP-37 canonical time and freeze when paused/absent.
- X05: fact, allegation, estimate, inference, intelligence, opinion, source statement and adjudicated finding remain distinct.
- X06: originals are preserved; summaries do not replace sources; corrections are additive and attributable.
- Global canon: one-city Saltwater; 10,000 living-person cap; minimum 10,000 businesses; police-depth priority; permanent person promotion; text-first completeness; exact `bingo` reveal firewall; no offline progression; no Neon writes without explicit approval.

Source-mapped tests S37.T01 and S38.T01 are included in BP-27's acceptance criteria. BP-27 does not claim ownership of the operational warrant/custody tests or adjudicative court tests; those remain shared integration tests with BP-25/BP-26/BP-28/BP-38.

## 30. Risk register

| Risk | Mitigation |
|---|---|
| Charge confused with guilt | Separate immutable charge and BP-28 finding records |
| Arrest treated as automatic charge | Independent referral and charging decision |
| Legal authority invented | Versioned fictional authority matrix; block unresolved actions |
| Prosecution/defence access conflated | Separate party roles, scopes and audit |
| Exculpatory material omitted | Required indexed material categories and review |
| Disclosure copy replaces source | Immutable derivative and exact source version |
| Sending confused with receipt | Separate transmission, delivery and acknowledgement |
| Court event fabricated by legal workflow | BP-28 authoritative event reference only |
| Bail order confused with operational release | BP-28 order + BP-26 implementation |
| Appeal assumed to stay order | Explicit BP-28 stay/variation order |
| Acquittal erases investigation | Preserve BP-15/BP-16 history |
| Hidden truth leaks through legal actors | Knowledge firewall and exact bingo condition |
| Deadline advances offline | BP-37 pause invariant |
| Person duplicated across proceedings | Canonical BP-03 identity and idempotent promotion |
| Legal process becomes a second society simulator | Proportionate institutions; police remains deepest system |

## 31. Design completion checklist

- [ ] Scope and ownership boundaries defined.
- [ ] Legal-process entities and stable-reference requirements defined.
- [ ] Legal actor roles and authority checks defined.
- [ ] Legal review and charging referral workflow defined.
- [ ] Charge decision, versioning and lifecycle defined.
- [ ] Prosecution workflow defined.
- [ ] Independent defence workflow defined.
- [ ] Disclosure items, categories, restrictions and review defined.
- [ ] Redaction, packages, delivery and acknowledgement defined.
- [ ] Filings, service and procedural applications defined.
- [ ] Bail/remand interface with BP-26/BP-28 defined.
- [ ] Court interface and authoritative order boundaries defined.
- [ ] Appeal/review workflow defined.
- [ ] Canonical deadlines and pause behaviour defined.
- [ ] Knowledge boundaries, confidentiality and security defined.
- [ ] Population cap and permanent person promotion defined.
- [ ] Text-first interface and reporting requirements defined.
- [ ] Append-only audit, correction and retention requirements defined.
- [ ] All 172 acceptance tests await BP-43 execution.
- [ ] All 14 mapped source requirement/test IDs traced.
- [ ] Open fictional policy decisions remain explicit.
- [ ] No Neon schema, seed, import or bulk write made or authorised.

## 32. Status and next dependencies

This is a complete division design draft, not approved fictional law, implementation evidence or executed test evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-28 — Courts and Outcomes**. BP-28 owns court institution, listings, hearings, judicial actors, evidence formally received, rulings, verdicts, findings, sentencing and authoritative court orders. BP-27 remains the owner of charging, disclosure, prosecution/defence and procedural filing workflow. BP-29 owns sentence execution.
