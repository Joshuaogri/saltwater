# BP-31 — Professional Standards

**Division:** BP-31  
**Title:** Professional Standards  
**Specification version:** 1.0  
**Status:** DESIGNED_DRAFT  
**User approval:** PENDING  
**Implementation / test execution / verification:** NOT_STARTED  
**Authority:** Adopted Saltwater BP-01–BP-44 master blueprint and binding Saltwater canon. This specification defines fictional professional-standards architecture; it does not enact real-world law or authorise database writes.

## 1. Purpose

BP-31 defines the professional-standards system for Saltwater's police service and its interfaces with public complaints, institutional oversight, internal investigations, misconduct findings, disciplinary decisions, remedies and review. It provides a fair, evidence-led, traceable process for concerns about police conduct, service standards, integrity, performance and institutional practice.

The system must support minor conduct concerns through serious and complex matters, including multiple officers, complainants, witnesses, incidents, cases and allegations. It must distinguish complaint receipt, allegation, investigation, finding, disciplinary outcome, appeal and personnel consequence. None is silently converted into another.

BP-31 is an institutional accountability system, not an omniscient narrator. It must preserve uncertainty, exculpatory information, procedural fairness, privacy, provenance and player agency. It must never reveal hidden crime-generation truth or predetermine a case outcome.

## 2. Binding Saltwater canon

1. Saltwater is one fictional sovereign city-state, one playable city and one jurisdiction.
2. Total living population has a hard cap of **10,000**, including all police personnel, public officials, complainants, investigators, witnesses and other people. Count each person once across all roles.
3. The police planning baseline is approximately 500 individually recorded personnel and remains within the 10,000 total.
4. At least **10,000 businesses** remain part of the city; BP-31 does not alter that baseline.
5. Police is the deepest simulation. Other institutions receive only the depth needed to support credible police work and accountability.
6. Text is the permanent primary interface. No essential complaint, investigation, finding, sanction or appeal workflow depends on graphics.
7. No simulation time advances while the player is absent or the game is paused. Wall-clock time never advances fictional deadlines.
8. Every person has one canonical BP-03 identity. Case-related persons promoted to full persistent simulation remain promoted permanently and are never downgraded.
9. NPCs know only what they observed, received or were authorised to access.
10. Culprit, accomplice and perpetrator hidden truth is never revealed unless the player types exactly `bingo`. No indirect disclosure through professional-standards records, AI summaries, personnel history, dialogue, notifications or analytics.
11. The player controls their officer's actions. The system must not provide unsolicited investigation hints or tell the player what to investigate next.
12. No Neon schema, migration, seed, import, bulk write or upload is authorised by this specification.

## 3. Scope

### 3.1 Included

- Public complaint intake when the complaint concerns police conduct or service, with referral interfaces for matters outside remit.
- Internal complaints, conduct concerns, integrity matters, standards breaches, misconduct allegations and professional-practice concerns.
- Screening, triage, risk flagging, assignment, investigation, review and closure.
- Investigative terms of reference, plans, actions, evidence/source references and findings.
- Procedural fairness, notices, response opportunities, representation and interpreters.
- Interim protective or operational restrictions as recommendations/references to owning divisions.
- Disciplinary decision processes and outcomes where configured.
- Appeals, reviews, reconsideration and independent review interfaces.
- Institutional remedies, recommendations, audits, inspections and accountability follow-up.
- Confidentiality, access control, provenance, retention, reporting and public outcome publication interfaces.
- Pattern analysis and organisational learning based on authorised records.

### 3.2 Excluded

- Canonical person identity and population: BP-03.
- Police organisation, rank, authority taxonomy and command structure: BP-05.
- Individual police personnel master: BP-06.
- Career, promotion, retirement and appointment execution: BP-07.
- Unit deployment and operational supervision: BP-08.
- Patrol, emergency dispatch and operational incident records: BP-10–BP-12.
- Crime taxonomy, crime generation, police case lifecycle and criminal investigation: BP-13–BP-16.
- Victim/witness identity, support and safeguarding roles: BP-17.
- Suspect/offender identity and criminal attribution: BP-18.
- Interviews/statements as authoritative records: BP-19.
- Surveillance: BP-20; intelligence: BP-21; scenes: BP-22.
- Exhibit identity and chain of custody: BP-23; forensic examination: BP-24.
- Arrests/warrants, police custody, legal proceedings, courts and corrections: BP-25–BP-29.
- Institutional governance and policy approval: BP-30.
- Training delivery/qualifications: BP-32.
- Employment/payroll/HR master processes: BP-33.
- Financial accounting and procurement transactions: BP-34.
- Simulation engine, social context, time, records, persistence, interface, notifications, security, QA and change control: BP-35–BP-44.

## 4. Ownership and cross-system boundaries

| Concern | Authoritative owner | BP-31 responsibility |
|---|---|---|
| Canonical person and population | BP-03 | Link complainants, subjects, witnesses, investigators and reviewers |
| Police mandate/authority hierarchy | BP-05 | Validate authority references; no parallel hierarchy |
| Officer personnel record | BP-06 | Link conduct matters and authorised outcomes; no duplicate personnel file |
| Career and appointment consequences | BP-07 | Supply authorised finding/outcome references; BP-07 decides and records career actions |
| Unit deployment and operational action | BP-08 | Recommend/refer restrictions; operational owner executes |
| Incidents and dispatch chronology | BP-11/BP-12 | Link source incidents; never rewrite them |
| Crime/case/investigation | BP-13–BP-16 | Coordinate parallel processes; no criminal case ownership |
| Victim/witness roles and safeguarding | BP-17 | Respect and reference source role/support records |
| Suspect/offender status | BP-18 | Never equate misconduct subject with criminal suspect/offender |
| Interview/statement records | BP-19 | Request and reference authoritative interview records |
| Surveillance/intelligence | BP-20/BP-21 | Consume authorised references with classification boundaries |
| Scene/evidence/forensics | BP-22–BP-24 | Preserve original source and custody; no shadow exhibit ledger |
| Arrest, custody, legal process and courts | BP-25–BP-28 | Respect authoritative legal orders and outcomes; no substitution |
| Corrections | BP-29 | No sentence or correctional status ownership |
| Institutional governance/policy/oversight | BP-30 | Execute professional-standards case lifecycle and report governance outcomes |
| Training/qualification | BP-32 | Refer training needs; no qualification changes |
| Employment and HR | BP-33 | Refer authorised employment actions; no payroll/HR master |
| Finance/procurement | BP-34 | No financial ledger or procurement transaction ownership |
| Time | BP-37 | All process time comes from canonical simulation time |
| Records and provenance | BP-38 | Use shared IDs, schema, provenance and retention standards |
| Persistence/recovery | BP-39 | Preserve all matter history and idempotent actions |
| Reporting/notifications | BP-41 | Supply approved status/outcome content for delivery |
| Access enforcement | BP-42 | Declare required scopes; BP-42 enforces |
| Testing/change control | BP-43/BP-44 | Supply acceptance criteria and versioned policy references |

BP-31 owns the professional-standards matter and its procedural lifecycle. Source divisions own their source records. A reference to evidence does not transfer exhibit custody; a finding does not rewrite a personnel record; a disciplinary recommendation does not itself impose a sanction; a referral does not close a complaint.

## 5. Matter model and taxonomy

A professional-standards matter is a persistent case-like record representing one or more allegations or concerns about conduct, integrity, service quality or institutional practice. It has a stable matter ID, creation provenance, intake source, jurisdiction/remit, owner, status, participants, allegation set, linked events/cases, procedural history, findings, outcomes and access classification.

Matter types may include:
- public complaint;
- internal conduct referral;
- supervisor referral;
- integrity concern;
- use-of-force review referral;
- custody/service complaint;
- discrimination or harassment allegation (category only; do not infer protected traits);
- corruption/bribery concern;
- abuse of authority;
- neglect or dereliction;
- dishonesty or record-integrity concern;
- confidentiality/data-handling concern;
- professional-practice concern;
- institutional/systemic issue;
- protected disclosure/whistleblowing concern where configured.

Taxonomy is versioned and configurable. No real-world jurisdictional classification or legal definition is silently imported. The allegation label is not a finding. A single matter may contain multiple allegations with different subjects, evidence, findings and outcomes.

## 6. Intake and complaint receipt

Intake channels may include public complaint, online/text form, in-person report, telephone, written correspondence, internal referral, supervisory referral, another public body, court/custody referral or system-generated audit alert. Channel availability is fictional configuration.

Each intake preserves:
- intake_id and matter_id;
- received simulation time;
- receiving person/office/channel;
- complainant/reporting-person reference, if known;
- original account/source content or protected source reference;
- alleged event date/time/place, including uncertainty;
- subject identity or unknown status;
- allegation categories as initially reported;
- attachments/source references;
- urgency/safeguarding indicators;
- consent/contact preferences where supplied;
- confidentiality request;
- acknowledgement status;
- intake actor and audit provenance.

A complaint can be recorded even if incomplete, anonymous, uncertain, out of time under a configured rule, or initially outside remit. Such characteristics affect screening, not the existence of the original record. The system never invents a complainant, subject, event, date or supporting fact.

Duplicate or related intakes are linked, not erased. A later account may supplement or contradict the first; the original remains unchanged. A representative may submit a complaint only with their claimed/verified authority status recorded as applicable.

Receipt is not acknowledgement; acknowledgement is not acceptance; acceptance is not proof; referral is not resolution.

## 7. Screening, jurisdiction and triage

Screening determines whether the matter falls within remit, whether it should be accepted, referred, linked, held for information or closed under an authorised rule. Each screening decision records the decision-maker, authority, information considered, rationale, date, status and review route.

Possible screening outcomes include accepted for assessment, accepted for investigation, referred to another owner, linked to an existing matter, outside remit, insufficient information pending clarification, withdrawn, duplicate-linked, or no further action under a configured and reasoned threshold.

Screening must not treat lack of corroboration at intake as proof that a complaint is false. An unsubstantiated complaint is not automatically malicious. A complaint can proceed with unknown subject identity or incomplete chronology.

Urgency triage may flag immediate risk to a person, evidence, public safety or ongoing operation. Protective action is routed to the competent operational owner. Triage flags are not findings and do not automatically authorise suspension, arrest, search, access to private records or disciplinary sanction.

## 8. Assignment, independence and conflicts

Every matter has one accountable owner at each lifecycle stage. Assignment identifies responsible investigator, supervisor, reviewer and decision-maker as distinct roles where separation is required.

Assignment validation checks:
- competence/qualification references;
- authority and remit;
- supervisory relationships;
- prior involvement;
- personal, financial, family or institutional conflict declarations;
- subject/complainant/witness relationships;
- access classification;
- workload/capacity if configured.

An officer cannot investigate or decide their own matter. A subject's direct supervisor may be restricted from deciding or reviewing it. Senior command matters require an independent escalation route. Complaints against the professional-standards unit bypass the conflicted unit. A reviewer or panel member named in the matter is replaced through a recorded reassignment.

A conflict is not silently ignored because staffing is limited. The system records the constraint and routes to the configured independent authority or leaves the matter pending. Reassignment preserves all prior work, decisions and reasons.

## 9. Investigation lifecycle

An accepted matter may move through assessment, investigation planning, active investigation, evidence review, subject response, findings preparation, decision, outcome, review/appeal and closure. Some matter types may use a shorter authorised route. Every transition is explicit and versioned.

Investigation terms of reference define:
- matters/allegations investigated;
- subjects and relevant participants;
- scope, period and locations;
- questions to be resolved;
- exclusions and limitations;
- investigator and supervisor;
- delegated powers and restrictions;
- information access authority;
- expected deliverables and review points.

Investigation plans contain lines of enquiry, tasks, responsible actors, dependencies, status, due simulation time and completion evidence. The plan is an administrative record, not an instruction to the player. The system does not suggest which line the player should pursue or reveal hidden truth.

Investigators may gather and assess authorised records, conduct interviews through BP-19, request surveillance through BP-20, request intelligence through BP-21, inspect scenes through BP-22, reference exhibits through BP-23 and request forensic examination through BP-24. Each source division retains its authoritative record.

## 10. Evidence, information and provenance

Professional-standards investigators distinguish:
- allegation;
- report;
- intelligence;
- lead;
- witness account;
- documentary record;
- physical/digital exhibit;
- forensic result;
- inference;
- hypothesis;
- established fact for the internal process;
- finding;
- recommendation;
- disciplinary outcome;
- court adjudication.

These categories cannot be silently converted. Repetition does not establish truth. Seniority does not increase evidential weight. An allegation is not proof, an intelligence report is not automatically evidence, and a finding in one matter is not a universal fact in every other matter.

Every material source reference records source owner, source ID/version, access authority, acquisition/receipt time, provenance, integrity status, limitations, relevant allegation and reviewer. Contradictory, incomplete, exculpatory and adverse material are retained. A derivative summary cannot replace the source record.

BP-23 remains authoritative for exhibit identity, packaging and chain of custody. BP-19 remains authoritative for interview and statement records. BP-24 remains authoritative for forensic method, result and report. BP-31 records its own assessment and finding without rewriting any source.

## 11. Subject participation and procedural fairness

The process must provide configured notice of allegations, process status, response opportunity, representation/support, interpreter assistance, relevant disclosure and decision/review route. Exact requirements remain fictional configuration rather than imported law.

A notice records recipient, content/version, delivery channel, delivery result, acknowledgement, service time and any exception. A failed delivery does not silently count as successful. The record distinguishes served, attempted, refused, unlocated, deferred and waived where configured.

The subject may respond, provide documents, identify witnesses, dispute facts, challenge source reliability, raise conflicts, request an interpreter or representative, and make submissions on outcome. Response is preserved in the subject's own words where practical and linked to BP-19 if formally recorded as an interview/statement.

If the subject declines or cannot respond, the reason and opportunity afforded are recorded. Silence is not treated as admission. Representation and interpreter records identify role and participation without assuming a person's sensitive characteristics.

Disclosure is authorised, proportionate and redacted where permitted. Confidential sources, complainant details, witness safety information, medical information and unrelated personal data are protected. The system records what was disclosed, to whom, when, under what authority and which version.

## 12. Interim measures and risk management

Interim measures are protective or operational controls pending a finding. Examples may include temporary access restrictions, separation of personnel, supervision changes, restricted duties or preservation directions, only where fictional policy and competent authority permit.

An interim measure records necessity, risk addressed, evidence basis, issuer and authority, scope, affected person, effective time, review interval, expiry/termination condition and challenge route. It is explicitly marked non-disciplinary and non-finding. It must not imply guilt.

BP-31 may recommend or refer an interim measure. The competent owner records and executes it: BP-06/BP-07/BP-08/BP-33 according to whether it affects personnel record, career, deployment or employment. BP-31 cannot directly alter duty roster, pay, rank, clearance or employment status without the owning workflow.

Safeguarding and immediate protection of complainants/witnesses are coordinated with BP-17 and relevant operational owners. No protective action may disclose a confidential source unnecessarily.

## 13. Findings and decision standards

Each allegation receives an individual finding. Permitted outcomes are configurable and may include substantiated, partly substantiated, not substantiated, inconclusive, unable to determine, withdrawn or no finding due to jurisdiction/process. The taxonomy and proof threshold must be approved through BP-30/BP-44 configuration.

A finding record contains:
- allegation and subject references;
- decision-maker and authority;
- applicable standard/version;
- issues determined;
- evidence/source set and versions;
- material supporting and contradicting the allegation;
- credibility/reliability assessments with reasons;
- facts accepted, rejected or unresolved;
- rationale and uncertainty;
- finding and effective simulation time;
- review/appeal route;
- notice and publication restrictions.

Findings must be reasoned and allegation-specific. Where evidence conflicts, the decision explains how the conflict was treated. No automatic binary guilty/not-guilty label is used. A not-substantiated finding does not mean the complainant lied. A malicious/knowingly false complaint is a separate allegation requiring its own evidence and process.

Investigators may recommend a finding but cannot present the recommendation as the final decision unless the configured workflow expressly authorises the same actor to decide. Separation requirements are explicit and validated.

## 14. Disciplinary process and outcomes

A disciplinary process begins only after an authorised decision route and is separate from the investigation finding. Configurable fictional outcomes may include no action, management advice, reflective practice, training referral, formal warning, final warning, restriction recommendation, demotion recommendation, dismissal recommendation or other approved sanction. This list is not enacted policy; exact availability and authority remain open.

Every proposed outcome records the finding relied upon, seriousness, relevant circumstances, consistency review, mitigation/aggravation, subject submissions, decision-maker, authority, rationale, effective time, review route and implementation owner.

Only the competent decision-maker may impose a sanction. BP-31 records the decision and emits an authorised outcome reference. BP-06/BP-07/BP-08/BP-32/BP-33 own resulting personnel, career, deployment, training or employment changes. A recommendation is not an implemented sanction. The record remains pending until the owning division acknowledges and reports execution or refusal.

A disciplinary hearing or panel may be required by configuration. Membership, quorum, independence, conflicts, attendance, representation, submissions, adjournments, evidence considered and decision must be recorded. A conflicted panel is invalid until resolved.

## 15. Review, appeal and reconsideration

Review mechanisms may include internal reconsideration, independent review, disciplinary appeal, procedural challenge or referral to a competent external authority. Each route has an eligibility rule, decision-maker, scope, submission window, record access rules and possible outcomes, all configured through BP-30/BP-44.

Appeal application, receipt, screening, hearing and determination are distinct events. Filing an appeal does not automatically suspend a sanction unless configured policy or an authoritative order says so. The original decision remains visible and historically intact.

Possible outcomes include affirm, vary, quash, remit for rehearing, substitute an authorised outcome, refer for further investigation or dismiss the appeal. The appeal decision records its authority, material considered, reasons, effective time and implementation instructions. BP-31 tracks the process; BP-06/BP-07/BP-08/BP-32/BP-33 implement relevant personnel outcomes.

## 16. Public complaints and institutional referrals

BP-31 receives complaints concerning police conduct and service. Complaints about other public bodies are referred to the competent body under BP-30's institutional routing framework. A complaint initially received by another agency but concerning a police officer can be transferred to BP-31 with source provenance and acknowledgement.

Public complaints may involve a named officer, unknown officer, unit, policy, service failure or systemic issue. Multiple officers or agencies may be involved. The system preserves each subject/allegation relationship and does not infer collective guilt from membership in a unit.

A complaint about senior command, the professional-standards unit, a decision-maker or an oversight reviewer must have a conflict-free escalation route. A referral does not erase the original receiving body's record or make the complaint resolved.

## 17. Systemic review, inspection and organisational learning

BP-31 may conduct or coordinate authorised thematic reviews, standards audits, inspections and systemic analysis. Each review has mandate, scope, sample frame, method, exclusions, reviewer, independence check, sources, findings, recommendations and response owner.

An inspection observation is distinct from an adverse finding. A recommendation is distinct from a binding direction. An institutional response may accept, partly accept, dispute or reject a recommendation with reasons. Implementation is evidenced by the owning institution; absence of evidence is not marked complete.

Pattern analysis may identify repeated complaint categories, recurring service failures, supervision concerns, policy gaps or training needs. It must account for reporting bias, duplicate records, sample limitations and uncertainty. Repeated allegations do not prove repeated misconduct.

Public trust and institutional reputation change only through BP-35/BP-36 event-driven causal rules. BP-31 supplies verified events and outcomes; it does not manually invent trust scores.

## 18. Interfaces to personnel, career, training and command

Professional-standards information is not a second personnel master. BP-06 stores authoritative personnel identity/history and receives only authorised references or outcome summaries appropriate to its schema. Confidential source material and raw complaint data are not copied wholesale into a general personnel file.

BP-07 decides career consequences under its own rules. BP-32 records training/refresher completion and qualification consequences. BP-08 executes unit/deployment restrictions. BP-33 handles employment/payroll action. BP-30 approves governance policy and institutional oversight.

A pending allegation must not automatically block promotion, change rank, revoke qualification, alter pay, change posting or trigger dismissal unless an explicit authorised rule and competent decision exists. A finding is not itself a career event. An appeal may affect implementation only according to configured rule/order.

## 19. Interfaces to criminal investigation and courts

The same conduct may also constitute a criminal allegation. Internal and criminal processes may run in parallel, but remain separate and may have different evidence access, standards, decision-makers and outcomes.

BP-15/BP-16 own criminal case and investigation lifecycle. BP-18 owns suspect/offender attribution. BP-25 owns arrest/warrant action. BP-26 owns police custody. BP-27 owns prosecution/legal process. BP-28 owns court adjudication. BP-29 owns correctional sentence execution.

BP-31 may refer information to a criminal investigation authority where authorised. It cannot make an arrest, charge, conviction or sentence. A criminal investigation does not automatically suspend the internal matter; any pause/sequencing rule must be explicit and time-bound. A court outcome may trigger a review of an internal matter but does not silently rewrite it.

## 20. NPC behaviour, player agency and hidden truth

NPC investigators, supervisors, complainants, witnesses and decision-makers act only on facts they have observed, received or are authorised to access. They do not receive hidden generator state or omniscient case solutions.

The player may initiate, direct, pause, resume, review and complete their officer's permitted actions. The system does not tell the player what to investigate next, reveal a culprit, manufacture evidence or force a successful/unsuccessful outcome.

The exact `bingo` gate protects all hidden offender and accomplice identities. It applies to search results, personnel records, professional-standards summaries, dialogue, notifications, reports, analytics and metadata. No role or clearance bypasses the player-facing reveal rule.

## 21. Time, deadlines and pause

BP-37 is the sole canonical clock. All receipt times, notice periods, investigation targets, review dates, hearings, appeal windows, interim measure reviews and retention events use simulation time.

While paused or absent:
- no complaint is automatically received or screened;
- no NPC investigator performs background enquiries;
- no interview, review, hearing or panel meeting progresses;
- no deadline, notice period, sanction or appeal period advances;
- no interim measure expires or is renewed;
- no matter is automatically closed;
- no trust/reputation consequence is generated;
- no wall-clock elapsed time is applied on resume.

A scheduled action becomes eligible only after the game clock advances and the event is explicitly executed. Due dates are reminders/eligibility conditions, not silent state transitions.

## 22. Core entities and fields

### 22.1 Professional-standards matter
matter_id; matter_type; intake_refs; status; remit; owner; priority; confidentiality_class; created_at_sim; last_event_at_sim; closure_state; linked_matter_refs; source_versions; audit.

### 22.2 Complaint/intake
intake_id; matter_id; channel; received_at_sim; receiving_actor; complainant_ref; representative_ref; original_account_ref; event_time/place; subject_refs/unknown; allegation_refs; urgency; contact_preference; confidentiality; acknowledgement; provenance.

### 22.3 Allegation
allegation_id; matter_id; category/version; subject_ref; alleged_conduct; event_ref; status; scope; evidence_refs; response_refs; finding_ref; audit.

### 22.4 Participant and role
participant_link_id; matter_id; person_id; role; effective_interval; contact/access classification; participation state; source; safeguarding reference; audit. Role links do not alter the person's canonical identity or other case roles.

### 22.5 Assignment and conflict
assignment_id; matter_id; actor/person/office; function; authority; competence_ref; conflict_declarations; assessment; start/end; reassignment_reason; audit.

### 22.6 Investigation plan/action
plan_id/action_id; matter_id; allegation_refs; author; owner; authority; task; purpose; source/access requests; status; dependencies; result; canonical time; provenance.

### 22.7 Source reference
source_link_id; source_division; source_record_id/version; source_type; authority; access basis; acquisition time; integrity/provenance; limitations; allegations linked; reviewer.

### 22.8 Notice and disclosure
notice_id/disclosure_id; matter; recipient; content/version; authority; delivery channel; sent/delivered/acknowledged times; redactions; source set; outcome; audit.

### 22.9 Finding and disciplinary outcome
finding_id; allegation; decision-maker; authority; standard/version; source set; accepted/rejected facts; rationale; outcome; uncertainty; effective time; review route.
disciplinary_id; finding_ref; decision-maker; authority; proposed/imposed outcome; factors; rationale; implementation owner; status; appeal refs.

### 22.10 Review, remedy and publication
review_id; scope; reviewer; independence; source set; decision; remedy_id; owner; due time; completion evidence; publication_id; approved content/version; redactions; delivery status.

## 23. State transitions and event contracts

Matter lifecycle may include received, acknowledged, screening, pending-information, referred, accepted, assigned, investigation-planned, investigating, subject-response, evidence-review, findings-pending, finding-issued, disciplinary-pending, outcome-issued, appeal-pending, review-pending, remedy-pending, resolved, closed, reopened and archived.

Allegation lifecycle is separately tracked: reported, screened, accepted, investigated, response-pending, decision-pending, substantiated, partly-substantiated, not-substantiated, inconclusive, withdrawn, no-finding or superseded under authorised correction/review.

Every event records event_id, matter_id, allegation/participant references, event type, actor, authority, prior/new state, canonical simulation time, source/configuration version, reason, affected scope, correlation/idempotency key and audit reference.

Events include complaint_received/acknowledged/screened/referred; matter_assigned/reassigned; conflict_declared/assessed; terms_of_reference_approved; investigation_action_opened/completed; source_linked/restricted/disclosed; notice_issued/delivered; response_received; interim_measure_referred/implemented/reviewed/ended; finding_proposed/issued/reviewed; disciplinary_hearing_opened/outcome_imposed; appeal_received/determined; recommendation_issued/response_recorded/remedy_completed; matter_reopened/closed.

Transitions are validated against authority, status and prerequisites. Events are append-only and idempotent. Duplicate replay cannot create duplicate findings, sanctions, hearings or closure. A failed downstream action leaves explicit pending/incomplete state.

## 24. Permissions, confidentiality and audit

BP-42 enforces access. BP-31 defines domain access classes for public intake, complainant identity, subject identity, investigator working records, confidential sources, witness material, medical/safeguarding references, interim measures, findings, disciplinary records, appeals and publication drafts.

Access is based on actor, role, assignment, matter, purpose, jurisdiction, record class and effective time. Being a police officer, supervisor or senior commander does not grant blanket access. Subjects receive only the authorised disclosure package, not unrestricted access to all internal or third-party records.

Every read, search, export, disclosure, amendment, decision, denial and permission change is audited. Protected complainant/witness identities and source details are minimised. Public publication requires a separate approval and redaction workflow. An exported index does not confer access to linked source records.

## 25. Records, persistence and reporting

BP-38 owns identifiers, schemas, provenance and correction conventions. BP-39 owns durable persistence, backup and recovery. BP-41 owns notification and reporting delivery. BP-31 preserves matter-level lifecycle and references source records by stable ID/version.

Original complaint accounts, notices, findings and decisions are immutable. Corrections append a reasoned event identifying actor, authority, prior value, corrected value and source. Historical views reproduce the policy, evidence set and matter state applicable at a selected simulation time.

Reports distinguish allegation from finding, finding from sanction, recommendation from implemented remedy, and criminal outcome from internal outcome. Every report identifies as-of simulation time, scope, source versions, author, approval status, access class and limitations.

Retention, legal hold, archive and disposal follow BP-38/BP-39 rules. BP-31 cannot silently delete, overwrite or shorten retention of a matter.

## 26. Inputs and outputs

### Inputs
- BP-03 canonical person and population records.
- BP-05 police authority and command hierarchy.
- BP-06 personnel records and status references.
- BP-07 career/appointment state.
- BP-08 deployment and operational restrictions.
- BP-11/BP-12 emergency/incident records.
- BP-13–BP-18 crime, case, investigation and participant references.
- BP-19–BP-24 interview, surveillance, intelligence, scene, evidence and forensic source records.
- BP-25–BP-29 arrest, custody, legal, court and correctional orders/outcomes.
- BP-30 approved policies, institutional mandates and oversight authority.
- BP-32/BP-33 training and employment outcome interfaces.
- BP-35/BP-36 event-driven social/public trust mechanisms.
- BP-37 canonical simulation time and pause state.
- BP-38/BP-39 records and persistence services.
- BP-41/BP-42 reporting and security services.
- BP-44 approved taxonomy, standards, procedures and configuration versions.

### Outputs
- Complaint/intake and professional-standards matter records.
- Screening, referral, assignment and conflict decisions.
- Investigation terms, actions and source-reference index.
- Notices, response and disclosure records.
- Allegation-specific findings and reasons.
- Disciplinary recommendations/decisions and implementation references.
- Appeal/review outcomes.
- Interim measure referrals and acknowledgement state.
- Institutional recommendations, remedies and follow-up.
- Approved reporting/publication packages and audit events.

Outputs are attributable references/events. BP-31 does not directly rewrite another division's authoritative records.

## 27. Exceptions and edge cases

1. Anonymous, incomplete or contradictory complaint.
2. Unknown subject, multiple subjects or mistaken identity.
3. Multiple allegations with mixed findings.
4. Duplicate or related complaints received through different channels.
5. Complaint outside remit or involving another public body.
6. Complaint against senior command or professional-standards personnel.
7. Investigator, supervisor, reviewer or panel conflict.
8. Complainant withdraws or becomes unavailable.
9. Subject resigns, retires, transfers, dies or leaves service during proceedings.
10. Subject cannot be located or is unavailable to respond.
11. Evidence is missing, contaminated, altered, disputed or inaccessible.
12. Confidential source or protected witness requires identity separation.
13. Parallel criminal investigation, arrest, prosecution or court proceeding.
14. Court order restricts disclosure or process.
15. Internal and criminal outcomes differ.
16. Allegation is partly substantiated or inconclusive.
17. Finding is challenged or corrected.
18. Appeal is late, incomplete, withdrawn or outside remit.
19. Appeal decision conflicts with a prior sanction implementation.
20. Interim measure becomes unnecessary, expires or is challenged.
21. Recommended training or deployment restriction is not implemented.
22. Disciplinary decision-maker lacks authority or panel quorum.
23. Complaint alleges systemic failure rather than individual misconduct.
24. Repeated complaints may reflect reporting patterns or duplicate records.
25. Malicious complaint is alleged but not established.
26. Public reporting risks identifying a protected person.
27. Subject seeks source material beyond authorised disclosure.
28. Personnel system rejects an outcome reference.
29. Matter is partially persisted or event replay occurs.
30. Population cap or person identity conflict arises.
31. Simulation pause occurs during a deadline or hearing.
32. AI summary omits contradictory or exculpatory material.
33. NPC actor appears to know information never received.
34. Hidden offender truth appears in a report or linked metadata.
35. Retention/legal hold conflicts with archive or disposal request.
36. An independent oversight route is unavailable or itself conflicted.

The system preserves the original facts, attempted action, actor, authority, canonical time, source version, conflict and resolution. It does not invent a result to force closure.

## 28. Configuration and unresolved fictional policy

The following require explicit fictional configuration through BP-30/BP-44; do not silently import real-world law or assume a jurisdictional model:

1. Professional-standards office structure, staffing and reporting independence.
2. Complaint channels, eligibility, limitation periods and screening thresholds.
3. Anonymous complaint and protected-disclosure handling.
4. Allegation taxonomy and definitions.
5. Investigation powers, competence and delegation.
6. Evidence/finding standards and burden/threshold.
7. Notice, disclosure and subject-response requirements.
8. Representation, support-person and interpreter rules.
9. Interim restrictions, authority, duration and review intervals.
10. Finding taxonomy and decision-maker separation.
11. Disciplinary sanction catalogue, thresholds and competent authorities.
12. Hearing/panel composition, quorum and procedure.
13. Appeal eligibility, submission windows, reviewer and outcomes.
14. Independent review and external referral institutions.
15. Confidentiality, publication and redaction standards.
16. Whistleblowing/protected disclosure protections.
17. Complaint retention, legal hold and archival rules.
18. Workload, caseload, staffing and NPC autonomy.
19. Systemic audit/inspection frequency and sampling methodology.
20. Public trust indicators and causal effects, implemented by BP-35/BP-36.

If a required rule is unresolved, the affected action remains pending or blocked with a clear reason. No default sanction, proof standard, appointment power, legal right or procedural deadline is invented.

## 29. Acceptance tests

These are BP-43 acceptance criteria, not evidence of implementation or test execution.

- PS-AT-001 — Every professional-standards matter has a stable unique identifier and canonical source-record references.
- PS-AT-002 — Every complaint records intake channel, received simulation time, receiving actor and original wording/source.
- PS-AT-003 — Complaint receipt is distinct from acknowledgement, screening, acceptance, investigation and outcome.
- PS-AT-004 — Anonymous complaints are accepted or declined only under configured rules and retain the information actually supplied.
- PS-AT-005 — An incomplete complaint remains recordable and is not silently discarded.
- PS-AT-006 — Duplicate or overlapping complaints are linked without deleting either original intake.
- PS-AT-007 — Each matter is classified by allegation type without treating the allegation as proven.
- PS-AT-008 — Allegation categories are configurable and versioned; no real-world legal taxonomy is silently imposed.
- PS-AT-009 — Every allegation identifies the subject role/person only where known and preserves unknown identity.
- PS-AT-010 — A person may be complainant, subject, witness or reporting person in different matters without role collision.
- PS-AT-011 — Complainant identity and protected contact details have separate access controls.
- PS-AT-012 — Complaint intake can be made by a representative where configured and records the representative's authority.
- PS-AT-013 — Every complaint receives a screening outcome or explicit pending reason.
- PS-AT-014 — Screening outcomes distinguish accept, refer, duplicate-link, outside remit, insufficient information, withdraw and no further action.
- PS-AT-015 — Screening rationale, decision-maker and authority are recorded.
- PS-AT-016 — An outside-remit complaint is referred only to a known competent owner and transfer acknowledgement is tracked.
- PS-AT-017 — Referral does not mark the underlying concern as resolved.
- PS-AT-018 — Urgent risk or safeguarding concerns are flagged and routed without predetermining misconduct.
- PS-AT-019 — Immediate protective action is separate from a disciplinary finding.
- PS-AT-020 — Retaliation or intimidation concerns can be recorded and linked to protection measures.
- PS-AT-021 — Every matter has an accountable owner and current responsible investigator or reviewer.
- PS-AT-022 — Assignment records competence, authority, conflicts and effective time.
- PS-AT-023 — Investigators cannot investigate matters where an unmanaged conflict exists.
- PS-AT-024 — Subject officers cannot investigate or determine their own matter.
- PS-AT-025 — Supervisors cannot suppress or close complaints outside their authority.
- PS-AT-026 — Reassignment preserves prior ownership, actions and rationale.
- PS-AT-027 — Case status changes follow defined transition rules and are audited.
- PS-AT-028 — Open matters remain visibly open with a reason for inactivity or delay.
- PS-AT-029 — Closure requires an authorised outcome and recorded rationale.
- PS-AT-030 — Reopening creates a new attributable event and preserves prior closure history.
- PS-AT-031 — Professional standards records are distinct from general personnel records.
- PS-AT-032 — BP-06 remains the authoritative police personnel record; BP-31 links to it rather than duplicating it.
- PS-AT-033 — Career or promotion consequences are not automatically applied from an allegation.
- PS-AT-034 — BP-07 owns career actions and consumes only authorised BP-31 findings/outcomes.
- PS-AT-035 — Employment and payroll consequences remain owned by BP-33.
- PS-AT-036 — Training interventions and qualification status remain owned by BP-32.
- PS-AT-037 — Departmental governance and policy approval remain owned by BP-30.
- PS-AT-038 — Police operational command and incident chronology remain owned by BP-08/BP-12.
- PS-AT-039 — Criminal investigation and criminal case lifecycle remain owned by BP-15/BP-16.
- PS-AT-040 — Criminal suspect/offender attribution remains owned by BP-18 and does not follow automatically from a misconduct allegation.
- PS-AT-041 — Arrest, custody, prosecution and court outcomes remain owned by BP-25–BP-28.
- PS-AT-042 — An internal professional-standards investigation does not substitute for a criminal investigation.
- PS-AT-043 — Parallel internal and criminal processes can coexist with explicit coordination and access restrictions.
- PS-AT-044 — An internal finding does not establish criminal guilt.
- PS-AT-045 — A criminal acquittal or conviction does not silently rewrite every internal finding; configured review is required.
- PS-AT-046 — Every investigation has defined terms of reference, scope, allegations and exclusions.
- PS-AT-047 — Investigation plans and actions have an author, authority, owner, status and simulation timestamp.
- PS-AT-048 — Investigators record evidence considered, sources, provenance and limitations.
- PS-AT-049 — Evidence is referenced through BP-23; BP-31 does not create a competing exhibit custody ledger.
- PS-AT-050 — Interview and statement records are owned by BP-19 and linked by stable references.
- PS-AT-051 — Surveillance records are owned by BP-20 and linked by stable references.
- PS-AT-052 — Intelligence records are owned by BP-21 and remain distinct from evidence and findings.
- PS-AT-053 — Forensic records are owned by BP-24 and remain unaltered by professional-standards interpretation.
- PS-AT-054 — Each material investigative action records purpose, actor, authority and result.
- PS-AT-055 — Investigative hypotheses remain distinguishable from established facts and findings.
- PS-AT-056 — Exculpatory and contradictory information is preserved and considered.
- PS-AT-057 — Unverified information is not upgraded to fact by repetition or seniority.
- PS-AT-058 — Investigator conclusions identify supporting and contrary material.
- PS-AT-059 — Investigators cannot access BP-14 hidden crime-generation truth.
- PS-AT-060 — NPC investigators know only information observed, received or authorised for them.
- PS-AT-061 — Investigative assignments do not generate unsolicited player investigation hints.
- PS-AT-062 — An investigation can conclude inconclusive, unsubstantiated, substantiated, partly substantiated or other configured outcome without forced binary guilt.
- PS-AT-063 — Each allegation receives its own finding; a matter with multiple allegations can have mixed outcomes.
- PS-AT-064 — Finding standards and proof thresholds are explicit configurable fictional policy, not silently imported.
- PS-AT-065 — Decision-makers are distinct from investigators where configured separation requires it.
- PS-AT-066 — Every finding identifies decision-maker, authority, standard applied, material considered and rationale.
- PS-AT-067 — Subject receives the applicable procedural notice and opportunity to respond under configured rules.
- PS-AT-068 — Response opportunity and any waiver, refusal or inability to respond are recorded.
- PS-AT-069 — Representation, support person and interpreter participation are configurable and recorded.
- PS-AT-070 — Vulnerable participants receive configured safeguards without assuming sensitive traits.
- PS-AT-071 — Disclosure to subject is controlled, reasoned and redacted where authorised.
- PS-AT-072 — Sensitive sources, confidential informants and protected complainants are not exposed by default.
- PS-AT-073 — Procedural notices record content/version, recipient, delivery method and acknowledgement.
- PS-AT-074 — Failure to deliver a required notice blocks or flags progression according to configured rule.
- PS-AT-075 — Interim restrictions are distinct from findings and disciplinary sanctions.
- PS-AT-076 — Interim measures have authority, necessity/rationale, scope, review time and expiry.
- PS-AT-077 — Interim measures are proportionate and do not imply guilt.
- PS-AT-078 — Suspension, restricted duty or access limitation is recorded as an employment/operational action by its owning division.
- PS-AT-079 — BP-31 sends an authorised recommendation or finding reference; BP-06/BP-07/BP-33 record the resulting personnel/career/employment action.
- PS-AT-080 — Disciplinary outcomes are distinct from investigative findings.
- PS-AT-081 — Available disciplinary outcomes are explicitly configured and versioned.
- PS-AT-082 — Only a competent authorised decision-maker may impose a sanction.
- PS-AT-083 — Sanction decision records seriousness, relevant circumstances, consistency review and rationale.
- PS-AT-084 — Sanction must not exceed the decision-maker's authority or configured maximum.
- PS-AT-085 — Mitigating and aggravating factors are recorded without invented facts.
- PS-AT-086 — Similar cases may inform consistency review but do not predetermine outcome.
- PS-AT-087 — Warnings, management advice, training referral and formal sanctions remain distinct outcome types.
- PS-AT-088 — Management action is not labelled as a misconduct finding unless an authorised finding exists.
- PS-AT-089 — Disciplinary hearing, panel or decision meeting is represented where configured.
- PS-AT-090 — Panel membership, quorum, independence and conflict checks are validated before decision.
- PS-AT-091 — Subject attendance, representation, response and adjournment are recorded.
- PS-AT-092 — Decision notice identifies findings, outcome, reasons, effective time and review/appeal route.
- PS-AT-093 — Appeal or review is a distinct process with independent reviewer where required.
- PS-AT-094 — Appeal submission does not automatically suspend a sanction unless configured or ordered.
- PS-AT-095 — Appeal outcome may affirm, vary, quash, remit or otherwise resolve the decision under configured rules.
- PS-AT-096 — Original finding and sanction remain historically preserved after appeal.
- PS-AT-097 — Correction of a mistaken record is additive, reasoned and attributable.
- PS-AT-098 — Public complaints involving non-police public bodies are routed to the competent owner rather than absorbed into police misconduct.
- PS-AT-099 — Complaints concerning a police officer are routed to BP-31 even when initially received by another public body.
- PS-AT-100 — Complaints concerning senior command have an independent escalation route.
- PS-AT-101 — Complaints against the professional-standards unit itself bypass the conflicted unit.
- PS-AT-102 — Complaints about a reviewer or panel member trigger conflict reassignment.
- PS-AT-103 — Whistleblowing and protected disclosures have distinct confidentiality and handling controls where configured.
- PS-AT-104 — Misconduct matters can be linked to incidents, cases, policies, training, supervision or prior findings without assuming causation.
- PS-AT-105 — Pattern analysis uses only authorised and appropriately qualified source data.
- PS-AT-106 — Repeated allegations are not treated as proof solely because they are repeated.
- PS-AT-107 — False or malicious complaint findings require evidence and separate decision; unsubstantiated does not mean malicious.
- PS-AT-108 — Complainants are not penalised merely because an allegation is not substantiated.
- PS-AT-109 — Victim and witness safeguarding remains with BP-17 and applicable source owners.
- PS-AT-110 — Professional-standards matter records do not overwrite victim/witness roles or case participation.
- PS-AT-111 — Public complaint progress updates disclose only authorised status information.
- PS-AT-112 — Publication of findings/outcomes requires approval, redaction and source traceability.
- PS-AT-113 — Public reporting does not reveal confidential personnel, complainant, witness or case information.
- PS-AT-114 — Public trust effects arise from recorded outcomes through BP-35/BP-36 causal rules, not arbitrary manual values.
- PS-AT-115 — Every remedy or organisational recommendation has an owner, due simulation time and completion evidence.
- PS-AT-116 — Failure to implement a remedy remains open and escalates under configured rules.
- PS-AT-117 — Audit/inspection findings distinguish observation, inference, substantiated finding and recommendation.
- PS-AT-118 — Inspection authority and scope are explicit and cannot be expanded by investigator convenience.
- PS-AT-119 — Professional-standards audits preserve sampling method, source population, exclusions and limitations.
- PS-AT-120 — Quality review checks completeness, authority, fairness, evidence provenance and decision rationale.
- PS-AT-121 — Quality reviewer cannot silently alter investigator findings.
- PS-AT-122 — Conflicting findings or evidence are flagged for reasoned resolution.
- PS-AT-123 — Case file export includes an index, source references, versions, access class and as-of simulation time.
- PS-AT-124 — Export does not grant recipient access to linked source records.
- PS-AT-125 — Every read, search, export, disclosure, amendment and denied access is permission checked and audited.
- PS-AT-126 — Sensitive personnel, medical, family, financial and protected-source details are minimised and access restricted.
- PS-AT-127 — Record retention, legal hold, archive and disposal follow BP-38/BP-39 rules; BP-31 cannot silently delete records.
- PS-AT-128 — Every correction preserves original value, reason, actor, authority and timestamp.
- PS-AT-129 — Every material event is idempotent; duplicate replay cannot duplicate an interview, finding, sanction or complaint closure.
- PS-AT-130 — Partial failure preserves completed work and explicit incomplete status.
- PS-AT-131 — Recovery preserves matter identity, evidence links, access logs and procedural history.
- PS-AT-132 — All effective dates, notices, review periods and deadlines use BP-37 simulation time.
- PS-AT-133 — No complaint, investigation, hearing, sanction, appeal or review progresses while the game is paused or player absent.
- PS-AT-134 — No NPC investigator or decision-maker performs background work while simulation time is frozen.
- PS-AT-135 — On resume, no wall-clock elapsed time is applied to deadlines or process stages.
- PS-AT-136 — All living complainants, officers, witnesses, investigators and panel members count once in the 10,000-person population.
- PS-AT-137 — Case-related persons promoted to persistent full-detail status are never downgraded.
- PS-AT-138 — Professional standards cannot create duplicate person identities or personnel records.
- PS-AT-139 — Police headcount remains within the 10,000 total population cap; the approximate 500 baseline remains a subset.
- PS-AT-140 — Professional-standards staffing and caseload do not imply unrecorded NPC employees.
- PS-AT-141 — Every official action has an authorised actor, authority reference, canonical time and traceable record.
- PS-AT-142 — Every officer links to one authoritative BP-06 personnel record and valid BP-05/BP-08 relationships.
- PS-AT-143 — Every complaint has a route, owner, status and outcome or explicit pending reason.
- PS-AT-144 — Every material command/disciplinary decision has authority, rationale and audit trail.
- PS-AT-145 — All mapped BP-31 source requirements and tests are traceable to this specification.
- PS-AT-146 — No BP-31 rule silently takes ownership from BP-06, BP-07, BP-15, BP-16, BP-19, BP-23, BP-30, BP-32, BP-33, BP-38 or BP-42.
- PS-AT-147 — No Neon schema, migration, seed, import or bulk write is authorised by this specification.

## 30. Source traceability

Original source: `docs/governance/SALTWATER_MASTER_BLUEPRINT.json`, SHA `a882c4fc17f5654268a9b6d5823f5b9a4f3f1ade`. Crosswalk: `docs/blueprint/SALTWATER-52-TO-44-CROSSWALK.md`. The mapped IDs below are preserved exactly.

| Source ID | Source requirement/test | BP-31 coverage |
|---|---|---|
| S11.R02 | Represent public policy, procurement, permits, licensing, inspections and public complaints. | Sections 6–8, 16–17; BP-31 owns police complaint intake/lifecycle; BP-30 routes other public-body complaints; BP-34 owns finance. |
| S23.R01 | Define police mandate, command hierarchy, rank/grade/position/authority/powers/clearance, divisions, units and reporting lines as distinct concepts. | Sections 4, 8, 18; BP-05/BP-06/BP-30 own hierarchy and authority; BP-31 validates and links standards matters. |
| S23.R03 | Define appointment, promotion, transfer, acting roles, succession, discipline, grievance, standards and retirement rules. | Sections 8, 14–18; BP-31 owns disciplinary matter process; BP-07/BP-32/BP-33 own career, training and employment execution. |
| S26.R01 | Represent orders, policies, briefings, operational plans, supervision, approvals, audits, complaints, misconduct and review. | Sections 7–18, 23–26; BP-30 policy/command governance, BP-31 complaint/misconduct lifecycle, operational owners retain execution. |
| S26.R03 | Support fair internal process and traceable decisions. | Sections 8–15, 23–25; conflicts, notice, response, evidence, reasoned findings, review and audit. |
| S40.R01 | Represent public complaints, independent review, internal investigations, inspections, findings, remedies and published outcomes. | Sections 6–17, 23–26; full complaint and professional-standards lifecycle, oversight and publication interfaces. |
| S40.R02 | Preserve due process, conflicts of interest and auditability. | Sections 8, 11, 13–15, 24–25; independent assignment, procedural fairness and immutable audit. |
| S40.R03 | Allow institutional failure and public trust to evolve from events. | Sections 17, 25–26; BP-31 records findings/remedies; BP-35/BP-36 generate causal trust effects. |
| S40.T01 | Every complaint has a route, owner, status and outcome or pending reason. | Sections 6–9, 16, 23, 27 and tests PS-AT-001–030, PS-AT-116–125. |

Cross-cutting controls:
- X03: BP-37 canonical time; no process or deadline advances while paused/absent.
- X04: atomic population/staffing/capacity reconciliation; all persons count once.
- X05: allegations, intelligence, evidence, inference, findings and adjudicated outcomes remain distinct.
- X06: original records are preserved; corrections are additive and attributable.
- Global canon: one city/jurisdiction; 10,000 living-person cap; >=10,000 businesses; police-depth priority; permanent person promotion; text-first completeness; exact `bingo` reveal gate; no offline progression; no Neon writes without explicit approval.

All 9 BP-31-mapped source IDs are explicitly traced. Source JSON and crosswalk remain unchanged.

## 31. Risk register

| Risk | Control |
|---|---|
| Complaint treated as proven | Separate allegation, investigation and finding states |
| Unsubstantiated complaint treated as malicious | Separate proof requirement for malicious allegation |
| Subject presumed guilty by interim restriction | Explicit non-disciplinary/non-finding status and review |
| Investigator conflict | Mandatory declaration, validation and reassignment |
| Senior command suppresses complaint | Independent escalation route |
| Internal finding confused with criminal guilt | Strict BP-15–BP-28 boundary |
| Evidence copied and custody diverges | BP-23 authoritative exhibit custody |
| Personnel file leaks confidential material | BP-06 minimal outcome references and BP-42 access |
| Career sanction applied automatically | BP-07 independent authorised workflow |
| Finding without fair response | Notice/response prerequisites and exception record |
| Appeal overwrites original decision | Append-only review history |
| Public report identifies protected person | Approval, redaction and publication access controls |
| NPC obtains hidden truth | Knowledge boundaries and exact bingo firewall |
| Background process advances while paused | BP-37 hard pause invariant |
| Duplicate replay duplicates sanction | Idempotency and recovery tests |

## 32. Design completion checklist

- [ ] Complaint intake, screening, assignment and referral defined.
- [ ] Matter/allegation lifecycle and multiple-subject handling defined.
- [ ] Independence, conflict and senior-command escalation defined.
- [ ] Investigation plan, source links and provenance defined.
- [ ] Procedural notice, response, representation and disclosure defined.
- [ ] Interim measures separated from findings/sanctions.
- [ ] Allegation-specific findings and standards configuration defined.
- [ ] Disciplinary process, decision authority and implementation interfaces defined.
- [ ] Appeal, review and reconsideration defined.
- [ ] Public complaint, systemic review, remedies and publication defined.
- [ ] Boundaries with personnel, career, criminal case, evidence, governance and HR owners preserved.
- [ ] Permissions, audit, retention, time freeze and hidden-truth protection defined.
- [ ] 10,000 population cap, 500 police planning baseline and >=10,000 businesses preserved.
- [ ] All 147 acceptance tests await BP-43 execution.
- [ ] All 10 mapped source IDs traced.
- [ ] Fictional policy decisions remain explicit.
- [ ] No Neon schema, seed, import or bulk write made or authorised.

## 33. Status and next dependencies

This document is a design draft only. It is not approved fictional law, implemented functionality or executed test evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-32 — Training and Development**. BP-31 owns professional-standards complaints, investigations, findings and disciplinary process; BP-32 owns training programmes, attendance, assessment, qualifications and development records.
