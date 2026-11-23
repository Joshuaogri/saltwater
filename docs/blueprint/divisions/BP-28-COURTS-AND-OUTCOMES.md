# BP-28 — Courts and Outcomes

**Division:** BP-28  
**Title:** Courts and Outcomes  
**Specification version:** 1.0  
**Status:** DESIGNED_DRAFT  
**User approval:** PENDING  
**Implementation / test execution / verification:** NOT_STARTED  
**Authority:** Saltwater fictional canon and adopted BP-01–BP-44 master blueprint. This specification defines the court simulation domain; it does not enact fictional law or authorise database writes.

## 1. Purpose

BP-28 defines the fictional court institutions and the authoritative adjudicative record for Saltwater. It governs court organisation, judicial appointments and authority, case listing, hearings, judicial procedure within the courtroom, material formally received or considered, evidential rulings, pleas, findings, verdicts, judgments, sentencing, court orders, appellate adjudication and the finality/status of judicial outcomes.

BP-28 is the authoritative source for what the court actually did and decided. BP-27 owns charging, prosecution and defence workflow, disclosure, party filings and procedural applications. BP-28 receives those submissions and records the court's own events and determinations. BP-29 owns execution of sentences and post-sentence supervision. BP-26 owns operational police custody. This separation is mandatory: a police record, legal filing, party assertion, charge, arrest or generated world fact is never itself a judicial finding.

The court simulation must support contested, complex and unresolved proceedings without guaranteeing conviction, acquittal, a particular sentence or a convenient narrative outcome. The player and authorised NPCs must be able to inspect the available record without being shown hidden generator truth.

## 2. Binding Saltwater canon

1. Saltwater is one sovereign city-state, one playable city and one jurisdiction. No second city, external playable territory or world expansion is created.
2. Total living population is capped at 10,000, including police, court personnel, legal actors, defendants, witnesses, victims and all other living persons. A person is counted once across every role and institution.
3. There are at least 10,000 businesses. Courts and supporting institutions are proportionate and do not become a second deep society simulator.
4. Police remains the deepest simulation. Court processes are detailed enough to create credible legal consequences and support police gameplay.
5. Text is the permanent, complete primary interface. No essential hearing, order, verdict, sentence or appeal information exists only in graphics.
6. BP-37 is the sole simulation clock. No hearing, listing, judgment, deadline, appeal, review, sentence commencement or court actor action progresses while the player is absent or the simulation is paused.
7. NPCs know only what they observed, received, were told or lawfully accessed under configured fictional rules.
8. Hidden occurrence truth is inaccessible to player-facing court actors and outputs. No record, judgment, testimony, dialogue, summary, notification or visual reveals a hidden culprit/accomplice/perpetrator unless the player types exactly `bingo`.
9. Do not provide unsolicited investigative hints or tell the player what to investigate next. Court decisions may state the court's actual reasoning and findings but must not expose generator-only facts.
10. Preserve player agency, uncertainty, disputed evidence, source provenance and historical records. Never force a result to move the game forward.
11. No real-world legal system, court hierarchy, evidential doctrine, standard of proof, sentencing tariff, appeal deadline or judicial power is silently imported. These are fictional, versioned configuration.
12. Blueprint approval does not authorise Neon migrations, seed data, imports or other database writes.

## 3. Scope

### 3.1 Included

- Court institutions, court identity, jurisdiction and functional structure.
- Judicial and court-officer roles, appointments, authority, conflicts and independence.
- Court registry, listing, scheduling, docket and proceeding administration.
- Court event lifecycle: hearing, adjournment, cancellation, resumption and conclusion.
- Judicial case management and procedural rulings within court authority.
- Court receipt and formal consideration of evidence/material.
- Evidential admissibility, relevance, scope, objections and exclusion decisions as configured.
- Pleas and their acceptance/recording where applicable.
- Judicial findings, verdicts, judgments and reasons.
- Acquittals, convictions, dismissals, mistrials, unresolved and mixed outcomes.
- Sentencing decisions and authoritative sentence/order records.
- Bail/remand and other judicial orders.
- Court order issue, variation, correction, service references and status.
- Appeals/reviews as adjudicative proceedings and appellate outcomes.
- Court records, transcripts/minutes, access, publication, confidentiality and audit.
- Interfaces to police, legal process, custody, healthcare and corrections.
- Court-specific NPC behaviour, knowledge boundaries and time freeze.

### 3.2 Excluded

- Sovereign constitution and city-state canon: BP-01/BP-02.
- Person identity and population count: BP-03.
- Court buildings, service providers and organisation identity: BP-04.
- Police mandate and command authority: BP-05/BP-30.
- Legal referrals, charging decisions, prosecution/defence party workflow, disclosure package creation, legal filings and appeal application filing: BP-27.
- Police case identity/lifecycle: BP-15.
- Investigation, investigative decisions and source conclusions: BP-16.
- Victim/witness and suspect/offender roles: BP-17/BP-18.
- Original interviews/statements: BP-19.
- Surveillance and intelligence source records: BP-20/BP-21.
- Scene and exhibit custody: BP-22/BP-23.
- Forensic examination and expert report source records: BP-24.
- Arrest/warrant/search/seizure execution: BP-25.
- Police custody and operational detention/release: BP-26.
- Sentence execution, prison/community supervision, rehabilitation, release and recall: BP-29.
- Department governance and discipline: BP-30/BP-31.
- Global clock, schemas, persistence, interface framework, notifications, security, QA and configuration governance: BP-37 through BP-44.

## 4. Authority and ownership boundaries

| Record or action | Authoritative owner | BP-28 responsibility |
|---|---|---|
| Person identity/population | BP-03 | Reference canonical person IDs; no duplicate persons |
| Court institution identity | BP-04 | Own court-domain role, jurisdiction and court structure; reference organisation/premises |
| Offence definition | BP-13 | Apply the configured version referenced by BP-27 charge |
| Hidden occurrence truth | BP-14 | Never access or disclose |
| Police case lifecycle | BP-15 | Link outcomes; never rewrite case history |
| Investigation | BP-16 | Receive authorised source material; do not direct investigation |
| Victim/witness/suspect roles | BP-17/BP-18 | Reference roles without overwriting them |
| Interview originals | BP-19 | Record court receipt/consideration of exact versions |
| Surveillance/intelligence originals | BP-20/BP-21 | Record court treatment under configured rules |
| Scene/exhibit records and custody | BP-22/BP-23 | Record exhibit tender/receipt/ruling; source owner remains authoritative |
| Forensic methods/results/reports | BP-24 | Record court receipt and consideration of exact report/data versions |
| Arrest/warrant/search execution | BP-25 | Reference operational records; do not rewrite them |
| Police custody | BP-26 | Issue authoritative judicial orders; BP-26 implements operational custody changes |
| Charge, prosecution/defence, disclosure and party filings | BP-27 | Receive filings and issue court determinations/orders |
| **Court events, judicial rulings, findings, verdicts, sentences and orders** | **BP-28** | **Authoritative owner** |
| Sentence execution and supervision | BP-29 | Issue sentence authority; BP-29 executes it |
| Global time | BP-37 | Consume canonical clock; no independent clock |
| Records, persistence, interface, notifications, security and QA | BP-38–BP-43 | Supply domain semantics and events |
| Fictional court configuration | BP-44 | Consume approved, versioned configuration |

A party's filing is not a court order. A prosecutor's submission is not a judicial finding. A charge is not a conviction. A conviction is not sentence execution. A sentence is not proof that corrections has received or implemented it. BP-28's authoritative record is the court's actual event/order/finding; BP-27 tracks party-side procedural consequences, BP-26 implements police custody changes and BP-29 executes sentences.

## 5. Core entities

All IDs are stable, unique and non-semantic. Exact syntax is governed by BP-38. Names are display attributes, never identity joins.

### 5.1 Court

Fields: court_id; canonical organisation_id; court_name; court_type; jurisdiction_id; location_ref; functions; active_status; opening/closure events; governing_configuration_version; registry_ref; access_classification; history.

A court may have configured divisions/chambers, but these are not additional jurisdictions or cities. Institutional capacity and NPC staffing remain proportionate to Saltwater's population.

### 5.2 Judicial appointment

Fields: appointment_id; person_id; court_id; judicial_role; appointment instrument/reference; appointing authority; effective_from/to; status; scope; delegation; restrictions; conflict declarations; suspension/revocation history; source references; audit events.

A title or job label does not itself prove current authority. Authority is validated at the time of each judicial act.

### 5.3 Court proceeding

Fields: court_proceeding_id; court_id; jurisdiction_id; BP-27 proceeding reference; linked police case IDs; party IDs; charge IDs/versions; proceeding type; assigned judicial actor(s); registry status; listing references; hearing IDs; evidential records; rulings; findings; verdicts; orders; sentence references; appeal links; access class; source/version manifest; state history.

A proceeding may include several defendants, counts or linked matters only where configured. Each charge, party and count retains its own outcome. Joint and severed proceedings preserve origin and cross-links without merging their histories.

### 5.4 Court listing and docket entry

Fields: listing_id; proceeding_id; court; event type; requested/assigned date; canonical scheduled time; courtroom/virtual location reference; presiding actor; required parties; notice references; status; rescheduling history; source and authority.

A listing is an administrative schedule record, not proof a hearing occurred. Requested, listed, notified, attended, commenced and concluded are separate states/events.

### 5.5 Hearing event

Fields: hearing_id; proceeding_id; listing_id; hearing_type; presiding judicial actor(s); participating parties; attendance; start/pause/resume/end simulation times; matters considered; submissions received; evidence references; objections; rulings; minutes/transcript references; adjournment/cancellation reason; outcome status; source/version manifest.

A hearing may be incomplete, interrupted, partially determined, adjourned or unresolved. The system must never fabricate an outcome because a hearing was scheduled.

### 5.6 Court material and evidential treatment

Fields: court_material_id; source_owner; source_record_id/version; submitting_party; tendered_at; received_at; purpose; material category; integrity/provenance references; objection links; treatment status; permitted purpose/scope; ruling reference; access class; retained copy/version hash.

Treatment states distinguish offered/tendered, received for filing, admitted/accepted for consideration, admitted for limited purpose, excluded, withdrawn, not ruled upon and disputed. Exact legal vocabulary is configurable. Court receipt does not transfer source ownership or rewrite custody.

### 5.7 Judicial ruling, finding and judgment

Fields: judicial_decision_id; proceeding_id; decision type; issue/charge/count/party scope; judicial actor(s); authority and configuration version; hearing reference; submissions/material considered with exact versions; disputed/undetermined matters; reasons; outcome; effective time; publication/access status; correction/review/appeal links; supersession history.

Findings must distinguish factual finding, legal conclusion, procedural ruling and evaluative observation. A judgment may contain several determinations with different scopes. No one finding silently determines a separate count, person or proceeding.

### 5.8 Verdict and disposition

Fields: disposition_id; proceeding_id; defendant_person_id; charge_id/version; count; plea reference; determination type; decision reference; decision-maker; date/time; reasons reference; finality/appeal status; correction/supersession history.

Disposition values are configured and may include guilty, not guilty, acquitted, dismissed, withdrawn by party, discontinued, mistrial, unresolved, no determination, or other fictional outcomes. These values are not interchangeable. No-charge remains a BP-27 legal-process outcome, not a court verdict.

### 5.9 Sentence and court order

Sentence fields: sentence_id; defendant; charge/count; conviction/disposition reference; sentence type; terms; duration/amount/conditions; commencement trigger; concurrency/sequence; review/appeal/stay status; reasons; exact order reference; version history.

Order fields: order_id; issuing court; judicial actor; authority; order type; parties; terms; scope; issued/effective times; conditions; duration/expiry if configured; service references; variation/revocation/correction links; status; source decision; audit history.

A court order is immutable after issue. Variation, correction, stay, discharge or revocation creates a new linked event/order. A draft order is not operative.

## 6. Court institutions and registry

BP-28 represents courts as fictional institutions with defined jurisdiction, functions, registry processes, listing capacity and recordkeeping. BP-04 remains authoritative for the organisation's identity, physical premises, utilities, staffing support and business/service relationships. BP-28 owns court-specific functions, jurisdictional assignment and adjudicative records.

The court catalogue may contain configured levels or specialist divisions, but no level, appeal route or jurisdiction is assumed until adopted in BP-44. A court cannot hear a matter outside its configured authority. Jurisdiction may be disputed; the court records the application and its own ruling rather than silently assuming competence.

Registry work includes receiving court-directed material, validating filing references from BP-27, creating docket entries, maintaining listings, recording notices and receipts, managing court record access and linking hearing/order events. Registry acceptance is administrative and does not decide the merits of a filing.

Court staff cannot exercise judicial power solely by virtue of registry access. Clerical correction of a transcription or administrative field is distinct from changing a judicial decision. Substantive correction requires the configured judicial process and a new attributable record.

## 7. Judicial actors, appointment and independence

Judges and other judicial decision-makers are canonical BP-03 persons with active BP-28 appointments. Court clerks, registry staff, assessors, jurors or other roles may exist only if configured. The system must not assume a jury or a particular adjudicative model.

Every judicial act validates:
- identity and appointment active at the event time;
- court and subject-matter jurisdiction;
- role-specific authority and any delegation;
- assignment to the proceeding;
- conflict-of-interest and recusal status;
- any required panel/quorum or review;
- access to the exact material relied upon;
- configuration version governing the act.

Police rank, prosecution authority, defence appointment, wealth, public office or database permissions do not confer judicial authority. Prosecutors and defence representatives cannot act as adjudicators in the same matter unless a future approved fictional canon explicitly defines a compatible role and safeguards; default is separation.

Recusal, reassignment, incapacity, vacancy, suspension and appointment expiry are explicit events. Prior valid decisions remain historically attributed; a later challenge or reversal is a new adjudicative event, not silent reassignment of authorship.

## 8. Court jurisdiction and allocation

Jurisdiction rules are fictional and versioned. Each proceeding records the rule and facts used to allocate it, including territorial, subject-matter, party and appeal jurisdiction where applicable. Saltwater remains the only playable jurisdiction.

An off-map source, witness or event may be referenced as external context without creating an external playable court, city or territory. Any external legal outcome is a referenced source with provenance, not a simulated external court system.

A jurisdiction challenge is a party application owned by BP-27. BP-28 records the court's ruling, reasons, scope and effective event. If jurisdiction is unresolved, the proceeding remains in a pending state and the system blocks merits determination where the configured rules require jurisdiction first.

Transfer between Saltwater courts is an explicit court/registry event with originating and receiving court references, authority, effective time and continuity manifest. Transfer does not erase earlier filings, hearings, orders or source records.

## 9. Listings, scheduling and docket management

A listing may arise from an authorised BP-27 filing, court direction, configured procedural trigger or authorised registry action. Every listing records its source and authority. The court schedule supports multiple matters, linked matters, urgent matters where configured, adjournments, cancellations and rescheduling.

The schedule must detect conflicts involving the same judicial actor, courtroom, required participant or other configured resource. A conflict is surfaced and resolved by an attributable action; the engine must not silently double-book or teleport participants.

Scheduled time is simulation time. The system must distinguish listed date/time, notice preparation, notice transmission, delivery, acknowledgement and actual attendance. A party's failure to attend is not automatically treated as an admission, waiver or guilt.

If listing rules, court capacity or an essential resource is unavailable, mark the matter unscheduled or blocked with a reason. Do not invent a court date, court, judge or hearing result. No background scheduling occurs while the player is absent.

## 10. Hearing lifecycle and courtroom events

A hearing has an explicit lifecycle: proposed/requested, listed, notified, ready, commenced, paused, resumed, adjourned, cancelled, concluded or unresolved, subject to configured transitions. A hearing may cover one or more procedural issues, charges or parties; the record identifies exactly what was considered.

Record the presiding actor(s), parties and representatives present, absences, interpreter/accessibility arrangements, submissions received, evidence/material considered, objections, rulings, directions, reasons and outcome. Record the source for any oral statement or event; do not fabricate transcripts.

A hearing may be interrupted by emergency, participant unavailability, technical failure, loss of evidence, judicial recusal or other event. Partial work remains recorded. Resumption creates a linked continuation or resumed segment; it does not duplicate prior testimony or evidence receipt.

Adjournment and cancellation reasons are attributable. An adjournment does not decide the underlying issue. A hearing may conclude with no ruling, reserved decision, partial ruling or unresolved question. The absence of a ruling remains explicit.

## 11. Court participation and attendance

Participants resolve to canonical BP-03 persons and BP-27 party-role links. Attendance is recorded per event: present, absent, excused, remote, late, departed, excluded by order or unknown. Do not infer attendance from a listing, notice or a person's presence elsewhere.

Record representative attendance separately from party attendance. Interpreter attendance and successful interpretation are separate facts. Accessibility and participation arrangements are recorded without inferring sensitive attributes. A participant may dispute the record; preserve both the original attendance entry and the challenge/correction outcome.

Victim, witness, defendant and suspect roles remain owned by BP-17/BP-18. Court participation does not overwrite those roles. Protected persons receive the configured restrictions. A witness's appearance does not prove the truth of their account.

## 12. Pleas and admissions

BP-27 owns filing/party-side workflow and records the party's submission; BP-28 owns the authoritative courtroom record of a plea and any judicial acceptance, rejection or other determination.

A plea event identifies the defendant, exact charge/count version, wording/category, time, presence/representation status, interpreter or accessibility support, source, judicial actor and acceptance status. A plea may be entered, not entered, reserved, disputed, changed or withdrawn only under configured fictional rules.

The system must distinguish a statement of admission, an interview account, a party submission, a formal plea and a judicially accepted plea. None may be silently substituted for another. A guilty plea does not automatically create a conviction until the configured court process records the authoritative determination. A plea on one count does not decide another count or co-defendant's charge.

No plea is presumed from silence, absence, refusal to answer or player inaction. Deemed/default pleas are permitted only if explicitly configured and supported by a recorded judicial act.

## 13. Court receipt and treatment of evidence

BP-28 records material formally tendered, received, admitted, considered, limited or excluded in a proceeding. BP-23 owns exhibit identity and chain of custody; BP-24 owns forensic examination and reports; BP-19/BP-20/BP-21 own their source records. Court treatment never alters the source record.

For each item, record source owner, exact record/version, tendering party, time and purpose, integrity/provenance references, objection, response, ruling, permitted use and access restriction. Distinguish:
- source exists;
- party has disclosed it;
- party tenders it;
- registry receives it;
- court admits or accepts it for consideration;
- court limits its purpose;
- court excludes it;
- court has not ruled on it.

A document filed with the registry is not necessarily evidence considered on the merits. An exhibit's physical presence is not proof of authenticity or admissibility. The court may record a dispute without deciding it. Exclusion from a proceeding does not delete the source or prevent its use in a separate proceeding under that proceeding's rules.

## 14. Evidential objections and rulings

Objections and evidential applications are initiated through BP-27 party workflow. BP-28 records the hearing/event, parties' positions as received, material version, judicial ruling, scope and reasons.

Configured rulings may address admissibility, relevance, authenticity, reliability, privilege, unfairness, limited purpose, redaction, expert evidence, witness handling, chain of custody, late material or other fictional categories. The catalogue and decision standards remain open configuration, not imported law.

A ruling must identify whether it applies to one item, a derivative, a purpose, a count, a party or the whole proceeding. A ruling may be reserved, varied or superseded through an authorised later judicial event. The original remains in history.

A party objection is not itself an exclusion. A party's assertion that evidence is unreliable is not a judicial finding. An evidential ruling does not necessarily determine ultimate weight or guilt.

## 15. Judicial findings, verdicts and judgments

A finding is an authoritative judicial determination of a defined issue. A verdict/disposition determines a charge/count or other matter under configured procedure. A judgment may consolidate reasons and determinations but must preserve their separate scopes.

Every decision records the court, judicial actor(s), appointment/authority, proceeding, parties, charge/count versions, issues, hearing, submissions and exact material considered, disputed or unresolved points, reasons, outcome, effective time and any review/appeal route.

Findings distinguish:
- allegation or party assertion;
- fact admitted by a party;
- fact the court finds established;
- fact the court finds not established;
- issue not determined;
- legal/procedural conclusion;
- evidential ruling;
- final disposition.

A court may reach different outcomes on different counts and defendants. A mixed outcome is valid. A conviction is recorded only for the correct defendant and charge/count following an authorised court determination. An acquittal, dismissal, withdrawal, discontinuance, mistrial and unresolved status remain distinct.

The court's reasoning must reflect material actually before it. It must not draw on hidden generator truth, unrecorded NPC knowledge, unseen evidence or information unavailable to the parties/court under configured rules.

## 16. Judgment, reasons and publication

A judgment/reasons record links to the exact decision and material versions. It may be reserved and delivered later in simulation time, but no delivery occurs off-screen. Oral pronouncement, written reasons, formal order and publication are distinct records/events where configured.

Reasons must identify the issues determined, relevant submissions, material considered, findings, applicable fictional rules/configuration and rationale. The system must preserve uncertainty, rejected arguments, limitations and unresolved matters. It must not generate plausible-sounding reasons unsupported by the record.

Publication/access categories may include public, party-only, restricted, sealed, anonymised or unpublished, as configured. Publication does not automatically expose protected identities, confidential records or judicial deliberations. Redacted/anonymised publications are immutable derivatives with provenance and review history.

A correction to typographical or administrative content is distinct from changing the substance of a judgment. Substantive change requires an authorised judicial review, appeal or correction process and a new linked decision.

## 17. Dispositions and finality

A proceeding's overall status is derived from its individual parties, charges, counts and unresolved issues. Do not use a single case-level outcome to overwrite different defendant/count outcomes.

Support configured dispositions including conviction, acquittal/not guilty, dismissal, withdrawal, discontinuance, mistrial, no determination, unresolved and partial/mixed outcome. Exact categories and legal effect are versioned fictional configuration.

Finality is not inferred from silence or elapsed wall-clock time. Record the relevant decision, order, appeal rights/status and configured finality trigger. A final outcome may later be reopened, set aside, varied or remitted only through an authorised event. Preserve the earlier finality interval and the new status.

A court outcome must never erase the police case, investigation, original evidence, victim/witness history or source records. An acquittal is not proof that the report was fabricated; a conviction is not permission to rewrite prior uncertain evidence as if certainty existed at collection time.

## 18. Sentencing

BP-28 owns sentencing decisions and the authoritative sentence order. BP-27 owns prosecution/defence submissions and procedural applications. BP-29 owns sentence execution and supervision.

A sentence may be created only after the configured prerequisite disposition. Record the exact defendant, charge/count, conviction/finding reference, judicial actor, authority, sentencing hearing, submissions, material considered, reasons, sentence type, terms, conditions, duration/amount, commencement trigger, concurrency/sequence, effective date and appeal/stay status.

Support configured sentence forms such as custodial, community-based, financial, restriction/prohibition, treatment-related or other fictional order. Do not assume a particular catalogue or duration. Concurrent and consecutive terms are distinct; aggregate calculations must be reproducible from source orders and approved rules.

If a term, commencement date or calculation depends on missing or ambiguous information, mark it unresolved. Never invent a duration, fine, release date or legal consequence. A sentence order is authority for BP-29; it is not proof that a person has been admitted, supervised, released or recalled.

## 19. Bail, remand and interim judicial orders

BP-27 owns the application and party workflow; BP-28 owns the judicial decision/order; BP-26 implements police custody status. Court orders may grant, refuse, vary or revoke bail/remand status or impose configured conditions.

Every order identifies defendant, application, hearing/decision, judicial actor, exact conditions, commencement/effective time, review/expiry if configured, service requirements and variation history. A court decision must be communicated to BP-26 through an authenticated order reference. BP-26 validates and performs its own custody transition.

A draft, unsigned, unissued or disputed order cannot trigger release. An application is not an order. A party's report of an order is not the authoritative record. If the order has not been received or verified, preserve the uncertainty and do not assume the operational change occurred.

Other interim orders may address participation, protection, evidence preservation, access, anonymity, treatment or procedure where configured. BP-28 records the authoritative order; source owners implement their own operational changes and report back.

## 20. Court-issued orders and order lifecycle

An order records issuing authority, scope, parties, terms, effective event/time, service requirements, duration/expiry where configured, variation/revocation process and source decision. Orders may be operative, stayed, varied, suspended, discharged, expired, revoked, corrected or superseded under configured transitions.

Issuance, sealing/signing where configured, service, receipt, acknowledgement and implementation are separate events. An order may be issued but not yet served; service may fail or be disputed. The system must not infer receipt from creation or transmission.

A variation creates a new order/version linked to the original. A stay changes legal effect only as specified by the authoritative order. A correction preserves the prior version and states whether it is clerical or substantive. A judicial order cannot directly mutate BP-26 or BP-29 state; the receiving owner validates and implements it.

## 21. Appeals and appellate adjudication

BP-27 owns appeal notice/application filing, party submissions, deadlines and procedural tracking. BP-28 owns appellate court institution, listing, hearing, review, decision, judgment and appellate order. The appealed decision remains immutable and linked.

An appeal proceeding records appellant, respondent, challenged decision/order/version, grounds, requested remedy, applicable fictional rule, filing references, court jurisdiction, panel/actor, hearing events, materials considered, reasons, disposition and authoritative order.

Configured outcomes may include allowed in whole/part, dismissed, refused, remitted, varied, set aside, retrial directed or other fictional results. The catalogue and effect remain open until configured. Filing an appeal does not automatically stay conviction, sentence, custody or order. Only an explicit authoritative stay/variation order changes legal effect.

Remittal creates a linked proceeding or resumed process while preserving the appellate history and prior trial record. BP-29 receives sentence changes only from an authoritative appellate order. BP-26 receives custody-related changes only from an authoritative order. Appeal outcomes do not rewrite police investigative history.

## 22. Court records, transcript and minutes

Court records may include docket entries, hearing minutes, transcript/audio/video references, exhibits/material manifest, rulings, reasons, judgments, orders, sentence records and publication derivatives. Each record has a stable ID, author/source, event time, version, completeness status, access classification and provenance.

A transcript is a record of what was captured or transcribed, not an infallible account. Corrections and disputes are appended with the original retained. A summary/minute is a derivative and cannot replace the underlying recording or formal order.

The system must distinguish recording planned, recording started, recording interrupted, recording completed, transcript drafted, transcript reviewed, transcript certified where configured and transcript corrected. No recording is invented where none occurred. Technical failure is preserved.

## 23. Victims, witnesses, experts and protected participants

BP-17 owns victim/witness identity and roles; BP-18 owns suspect/offender status; BP-24 owns expert competence and forensic reports. BP-28 records court participation, evidence and protective orders without taking over those source domains.

A witness's testimony is attributed to the witness and proceeding. Prior statements link to BP-19 exact versions. A witness may be mistaken, inconsistent, hostile, unavailable, recanting or credible; such characterisations require a sourced judicial assessment and must not be generated from hidden truth.

Experts are identified with qualifications and source report references. Their opinion is distinguished from raw result, party submission and court finding. The court may accept, reject or limit expert opinion through an attributed ruling/finding.

Protection, anonymity, remote participation, exclusion of public or other special measures exist only under configured authority. Protected identity is hidden from unauthorised parties and outputs, including metadata and search results.

## 24. Healthcare and specialist court interfaces

Courts may receive authorised clinical or specialist material and issue configured directions involving assessment, treatment or attendance. BP-04 owns provider/institution identity; BP-09/BP-12/BP-17/BP-24/BP-26 own their respective operational and source records; BP-42 controls sensitive access.

A court finding about a legal issue is not a medical diagnosis. Clinical assessment, forensic opinion and judicial determination remain distinct. A court cannot invent clinical facts or alter a medical record. Any treatment or assessment direction is linked to an authoritative order and implemented by the relevant provider/owning division.

Healthcare remains proportionate and supportive; BP-28 does not create a separate full healthcare simulation. Sensitive medical material is purpose-restricted, minimised and auditable. Missing clinical evidence remains missing, not inferred.

## 25. Time, scheduling and pause invariants

BP-37 is the sole clock. All listing, hearing, decision, order, service-reference, sentence and appeal dates use canonical simulation time and preserve effective intervals. The court may store wall-clock metadata for technical provenance only if permitted by BP-37/BP-39; it must never drive game progression.

When paused or the player exits:
- no hearing begins, resumes or concludes;
- no judge deliberates or delivers a reserved judgment;
- no registry clerk lists, serves or processes a matter;
- no deadline expires;
- no order is issued, served, varied or revoked;
- no sentence commences or progresses;
- no appeal is heard or decided;
- no NPC attendance or court communication changes.

On resume, the simulation continues from the exact frozen state. No catch-up, elapsed-time penalty, automatic outcome or queued NPC action is applied. All scheduled events require explicit in-game time progression.

## 26. Knowledge boundaries and hidden truth

A judicial actor may know only what is presented, observed, received or lawfully accessed in the proceeding. Court appointment does not grant omniscience. A judge cannot inspect BP-14 generator truth, private NPC memory, undisclosed evidence, protected sources or other proceeding records without configured authority.

Court findings are based on the actual record available to the court and the fictional rules in force. The simulation engine must not use its hidden knowledge to make a judge reach a correct or incorrect verdict. The possibility of error, uncertainty, conflicting evidence and unresolved outcomes is essential.

The exact `bingo` safeguard applies to every court record, judicial reason, verdict, order, NPC dialogue, transcript, report, search result, metadata field and AI-generated summary. No hidden perpetrator or accomplice identity may be disclosed before that exact player input. The rule is not bypassed by describing circumstantial facts in a revealing combination or by an AI-generated conclusion.

## 27. Inputs and outputs

### Inputs

- BP-03: canonical person identities and living-person lifecycle.
- BP-04: court organisations, premises, healthcare providers and institutions.
- BP-13: offence definition and version referenced by the charge.
- BP-15: police case references and historical case links.
- BP-17/BP-18: victim/witness/suspect/offender roles and restrictions.
- BP-19: interview and statement originals/versions.
- BP-20/BP-21: surveillance and intelligence source records/restrictions.
- BP-22/BP-23: scene/exhibit records and continuity.
- BP-24: forensic results, expert reports and limitations.
- BP-25/BP-26: operational arrest/warrant/custody records.
- BP-27: charges, parties, prosecution/defence filings, disclosure manifests, applications, service and appeal filings.
- BP-29: sentence execution acknowledgement, status and implementation.
- BP-37: canonical simulation time and pause state.
- BP-38/BP-39: schemas, IDs, provenance and persistence.
- BP-41/BP-42: notifications/reporting and access controls.
- BP-44: approved fictional court/legal configuration.

### Outputs

- Court listings, dockets and hearing events.
- Judicial rulings on procedure, jurisdiction and evidence.
- Authoritative findings, verdicts, judgments and dispositions.
- Bail/remand and other court orders.
- Sentence orders and exact sentence terms.
- Appellate hearings, decisions and orders.
- Court material receipt/admission/consideration manifest.
- Party/court notices and authoritative event references.
- Outcome references for BP-15/BP-27/BP-29 and custody implementation references for BP-26.
- Audit, transcript/minute, reporting and publication records.

Every output is a versioned domain event or record. Downstream divisions validate and apply their own state transitions; BP-28 does not directly mutate another division's owned records.

## 28. State transitions and event contracts

Every material transition records event_id, entity_id, prior/new state, actor, role, appointment and authority, court/proceeding, canonical simulation time, source records and versions, reason, configuration version, result, idempotency key and correlation references.

Core events include court_created/activated/closed; appointment_made/suspended/revoked/expired; proceeding_received/allocated/transferred; listing_created/changed/cancelled; hearing_started/paused/resumed/adjourned/concluded; attendance_recorded/corrected; material_tendered/received/admitted/limited/excluded/withdrawn; objection_recorded/decided; plea_entered/accepted/rejected/changed; ruling_reserved/delivered; finding_recorded; verdict_recorded; judgment_delivered/published; order_drafted/issued/served/received/varied/stayed/discharged/revoked/corrected; sentence_imposed/varied; appeal_heard/decided/remitted; transcript_created/corrected; access_granted/denied/revoked; correction_proposed/approved/appended.

Events are append-only and idempotent. Replay cannot create duplicate hearings, orders, findings, verdicts or sentence records. Partial failures preserve completed sub-events and an explicit incomplete state. A missing downstream acknowledgement remains pending, not presumed successful.

## 29. Permissions and security

BP-42 owns global enforcement. BP-28 defines domain scopes for:
- court registry and docket administration;
- judicial appointments and restricted personnel records;
- proceeding and party records;
- hearing attendance and recordings;
- judicial deliberations and draft reasons;
- evidence/material manifests and protected sources;
- rulings, findings, verdicts, judgments and sentence records;
- sealed/restricted/anonymised proceedings;
- protected witness, victim and informant identities;
- medical and specialist material;
- appeal records and appellate deliberations;
- publication, export, transcript and audit.

Access is checked by actor, role, court, proceeding, party, purpose, record class, source restrictions and event time. Party access does not grant access to judicial deliberations. Judicial access does not grant unrestricted access to protected source identities. Registry permissions do not confer judicial power. Police or prosecution status does not grant access to defence-confidential material.

Every read, export, publication, disclosure, correction and denied access is audited. Search results, counts, snippets, autocomplete, error messages and metadata must not leak restricted content or hidden truth.

## 30. Exceptions and edge cases

The implementation must explicitly handle:
1. Court lacks configured jurisdiction.
2. Jurisdiction is disputed or unresolved.
3. Judicial appointment missing, expired, suspended or revoked.
4. Judicial conflict or recusal arises before or during a hearing.
5. Judicial actor becomes unavailable or incapacitated.
6. Court has no configured listing capacity or registry.
7. Scheduling conflict involving judge, room, party or required resource.
8. Listing notice not delivered or receipt disputed.
9. Party absent, late, excused or attendance unknown.
10. Interpreter or accessibility support unavailable or unsuitable.
11. Hearing interrupted, partially completed or technically compromised.
12. Adjournment/cancellation entered without sufficient authority.
13. Filing reference is invalid, duplicate or linked to wrong proceeding.
14. Charge version changed after listing.
15. One party/charge/count is severed or joined.
16. Plea is absent, disputed, changed, withdrawn or incorrectly recorded.
17. A party claims admission but no formal plea event exists.
18. Evidence tendered but not received by registry.
19. Material received but not admitted for consideration.
20. Objection remains unresolved or ruling is reserved.
21. Evidence admitted for limited purpose only.
22. Evidence excluded, withdrawn or later corrected.
23. Exhibit identity/custody disputed.
24. Forensic report or underlying data is challenged.
25. Intelligence or protected source material is improperly tendered.
26. Disclosure package is incomplete or superseded.
27. Court record conflicts with original source version.
28. Transcript missing, incomplete, inaccurate or disputed.
29. Oral ruling differs from later written order.
30. Order drafted but not issued.
31. Order issued but not served or received.
32. Order served to wrong person or service disputed.
33. Order is varied, stayed, discharged, revoked or corrected.
34. Bail/remand order received but BP-26 has not implemented it.
35. Sentence order received but BP-29 has not acknowledged it.
36. Sentencing prerequisite or conviction status is unresolved.
37. Sentence term or aggregate calculation cannot be reproduced.
38. Appeal is filed but no stay exists.
39. Appellate outcome applies to only some charges or parties.
40. Matter remitted to a lower court or further hearing.
41. Finality is disputed or appeal remains pending.
42. Court outcome conflicts with BP-27 charge/proceeding version.
43. Court outcome appears to identify wrong person.
44. One defendant's result is incorrectly applied to another.
45. One count's result is incorrectly applied to another count.
46. Acquittal/dismissal is misrepresented as proof of fabrication.
47. A court actor claims knowledge without a source.
48. AI attempts to create a verdict or reveal hidden truth.
49. Protected identity leaks through transcript, publication or metadata.
50. Healthcare or privileged material is accessed without authority.
51. Population cap would be exceeded by person creation.
52. Time advances while paused or absent.
53. Configuration is missing, contradictory or changes mid-proceeding.
54. External source is referenced without creating external playable geography.
55. Duplicate event replay or partial persistence failure occurs.
56. A downstream division rejects an order or event.
57. Summary conflicts with authoritative order or finding.
58. Correction requested after finality or publication.
59. A proceeding has mixed outcomes and unresolved counts.
60. Court closes or changes structure while matters remain pending.

Every exception preserves attempted action, actor, authority, canonical time, source versions, affected records, known state, failure reason and authorised resolution path. No silent repair or invented result.

## 31. Cross-system effects and handover

### BP-27 — Legal Processes
BP-27 sends charges, party roles, filings, disclosure manifests, applications and appeal notices. BP-28 returns court event references, rulings, authoritative orders, findings, verdicts, judgments, sentences and appeal outcomes. BP-27 retains party-side workflow and procedural tracking; it must not rewrite judicial records.

### BP-15/BP-16 — Police case and investigation
Court outcomes are linked to police case/investigation records as downstream references. BP-15/BP-16 retain their original lifecycle and decision history. An acquittal, dismissal or conviction does not retroactively rewrite investigative facts or conclusions.

### BP-17/BP-18 — Participants
Court findings and verdicts are separate from victim/witness and suspect/offender roles. BP-18 updates status only through its own validated contract; BP-28 does not silently overwrite person-role history.

### BP-19–BP-24 — Source material
Court material references exact original source IDs and versions. BP-23 remains authoritative for exhibits and custody; BP-24 for forensic work; BP-19/BP-20/BP-21 for their respective records. Judicial treatment is a separate proceeding-specific event.

### BP-26 — Custody
BP-28 issues an authoritative order. BP-26 validates, receives and implements operational custody changes. BP-28 does not directly release, transfer or detain a person.

### BP-29 — Corrections
BP-28 issues the authoritative sentence and any variation/stay/release order. BP-29 validates and executes sentence, supervision, rehabilitation, release or recall. Court sentence and correctional status remain separate.

### BP-03/BP-04/BP-37–BP-44
All people resolve to canonical identities; institutions resolve to BP-04; all times use BP-37; records use BP-38; persistence uses BP-39; interface is BP-40; notices/reporting BP-41; security BP-42; tests BP-43; configuration BP-44.

## 32. Text-first interface and reporting

Essential text commands or equivalent controls must allow authorised users to:
- list courts, proceedings, dockets, listings and hearing events;
- inspect jurisdiction, appointment, party and charge references;
- view hearing attendance, minutes and material manifests;
- inspect evidence treatment, objections and rulings;
- inspect pleas, findings, verdicts and judgments;
- inspect exact sentence terms and authoritative orders;
- view order issue/service/receipt/implementation status separately;
- inspect appeal proceedings and appellate outcomes;
- view unresolved matters, reserved decisions and pending acknowledgements;
- inspect source provenance, versions, restrictions and audit;
- generate authorised court register, hearing, outcome and sentence reports.

Reports identify as-of simulation time, scope, source IDs/versions, filters, access restrictions, author/system and uncertainty. A report is a derivative and never replaces an authoritative judicial order, transcript or judgment. No summary may convert an allegation into a finding or disclose hidden generator truth.

## 33. Audit, correction, retention and publication

Every material judicial act, record creation, access, export, order, ruling, finding, verdict, sentence, publication and correction is attributable to an actor, appointment, authority, purpose, time, source and version.

Corrections append a linked record containing original, corrected value, reason, source, author, authority, review and effective time. Prior orders and judgments remain available according to access rules. A substantive change requires a new authorised judicial event, not editing the old record.

Retention, sealing, archiving, destruction and publication are governed by versioned fictional configuration and BP-39/BP-42. Preservation holds prevent configured disposal. Public publication is a controlled derivative; confidential and protected information remains restricted.

## 34. Configuration and unresolved fictional policy

BP-44 governs all court configuration. The following remain open and must not be guessed:

1. Court hierarchy, court names, divisions and jurisdiction boundaries.
2. Judicial appointment process, terms, qualifications and removal.
3. Judicial powers, delegations, recusal and conflict standards.
4. Court registry structure, staffing, capacity and operating schedule.
5. Case allocation, listing priority and scheduling rules.
6. Hearing types, courtroom procedure and participation requirements.
7. Whether juries, panels, assessors or single-judge determinations exist.
8. Plea categories, acceptance rules and consequences.
9. Evidential doctrine, admissibility, relevance and burden/standard of proof.
10. Objection types, procedure and available remedies.
11. Verdict/disposition taxonomy and finality triggers.
12. Judgment form, reasons, publication and correction procedure.
13. Sentencing catalogue, terms, calculation and concurrency rules.
14. Bail/remand judicial criteria, condition catalogue and review.
15. Court order types, service and effective-date rules.
16. Appeal courts, grounds, filing periods, review powers and stays.
17. Remittal, retrial and reopening rules.
18. Court record, transcript, recording, retention and sealing standards.
19. Protected witness, anonymity and closed hearing rules.
20. Healthcare/fitness assessment and treatment order interfaces.
21. Court actor NPC autonomy and workload policy.
22. Court continuity during institutional closure or vacancy.
23. Transition rules when configuration changes during an open case.
24. Publication and public access rules.

When a required rule is unresolved, mark the action blocked/pending and preserve the issue. Do not import real-world law or invent a court outcome.

## 35. Acceptance tests

These criteria are for BP-43. They are not evidence that implementation or testing has occurred.

- COURT-AT-001 — Every court has a stable unique institutional ID.
- COURT-AT-002 — Every judicial actor resolves to a canonical person and appointment record.
- COURT-AT-003 — Every proceeding resolves to the single Saltwater jurisdiction or a marked off-map reference.
- COURT-AT-004 — A court cannot claim jurisdiction without a configured jurisdiction rule.
- COURT-AT-005 — Court institutional identity is distinct from police and prosecution institutions.
- COURT-AT-006 — Judicial roles are separate from prosecution, defence and police roles.
- COURT-AT-007 — Judicial appointment and authority are validated at the event time.
- COURT-AT-008 — Expired, suspended or revoked judicial appointment cannot authorise a new judicial act.
- COURT-AT-009 — Judicial independence restrictions are enforced by configured authority rules.
- COURT-AT-010 — A judicial actor cannot determine a matter where a configured conflict exists.
- COURT-AT-011 — Judicial assignment and recusal history are preserved.
- COURT-AT-012 — A court listing is distinct from a hearing event.
- COURT-AT-013 — A hearing event is distinct from a party filing.
- COURT-AT-014 — A hearing event records its actual start, pause, resumption and conclusion.
- COURT-AT-015 — An adjournment is an explicit judicial/court event, not an inferred delay.
- COURT-AT-016 — A cancelled hearing remains in historical records.
- COURT-AT-017 — A hearing may be partially completed without forcing a conclusion.
- COURT-AT-018 — Non-attendance is recorded per party and does not imply admission or guilt.
- COURT-AT-019 — An unresolved hearing remains unresolved.
- COURT-AT-020 — All hearing times use BP-37 canonical simulation time.
- COURT-AT-021 — No hearing, judicial review or court action progresses while paused or absent.
- COURT-AT-022 — No NPC judge, clerk or court actor performs work off-screen.
- COURT-AT-023 — Resume does not apply elapsed wall-clock time to court proceedings.
- COURT-AT-024 — Court listings use configured scheduling rules and never invent dates.
- COURT-AT-025 — Missing court scheduling configuration blocks automatic listing.
- COURT-AT-026 — Parties and representatives are linked by canonical BP-03 IDs and BP-27 role records.
- COURT-AT-027 — A party's role in one case does not overwrite roles in another.
- COURT-AT-028 — Multiple defendants may have separate hearings and outcomes.
- COURT-AT-029 — Multiple charges against one defendant may have separate determinations.
- COURT-AT-030 — Joint proceedings preserve party-specific and charge-specific outcomes.
- COURT-AT-031 — Severed proceedings retain links to their origin and history.
- COURT-AT-032 — Linked proceedings do not merge evidence or adjudicative histories.
- COURT-AT-033 — A proceeding may remain open with unresolved counts or parties.
- COURT-AT-034 — Case and investigation lifecycle remain owned by BP-15 and BP-16.
- COURT-AT-035 — BP-28 cannot close or rewrite a police investigation.
- COURT-AT-036 — Charge identity and version are sourced from BP-27.
- COURT-AT-037 — A charge amendment creates a distinct version and court record reference.
- COURT-AT-038 — A charge is not treated as a finding or conviction.
- COURT-AT-039 — An arrest does not imply a court finding.
- COURT-AT-040 — A plea is distinct from a verdict or finding.
- COURT-AT-041 — A guilty plea is recorded only when made and accepted under configured rules.
- COURT-AT-042 — A not-guilty plea does not establish factual innocence.
- COURT-AT-043 — A plea may be absent, reserved, changed or disputed.
- COURT-AT-044 — A plea for one count does not determine another count.
- COURT-AT-045 — A plea by one defendant does not determine a co-defendant's plea.
- COURT-AT-046 — Default or deemed plea is not invented when no event exists.
- COURT-AT-047 — Every plea event identifies the person, charge, time and source.
- COURT-AT-048 — Every judicial finding identifies the exact issue and parties determined.
- COURT-AT-049 — Findings distinguish fact found, legal conclusion and procedural ruling.
- COURT-AT-050 — Findings record the evidence/material considered and exact versions.
- COURT-AT-051 — Findings record reasons and the judicial actor responsible.
- COURT-AT-052 — Findings preserve disputed facts and contrary evidence.
- COURT-AT-053 — An evidential association is not automatically a judicial finding.
- COURT-AT-054 — Intelligence is not silently treated as admitted evidence.
- COURT-AT-055 — An allegation is not silently converted into an established fact.
- COURT-AT-056 — An investigative hypothesis is not presented as a court finding.
- COURT-AT-057 — An expert opinion retains its limitations and source report.
- COURT-AT-058 — An exhibit is linked to its BP-23 identity and custody history.
- COURT-AT-059 — A forensic report is linked to its BP-24 version.
- COURT-AT-060 — Interview and statement material is linked to BP-19 source versions.
- COURT-AT-061 — Surveillance material is linked to BP-20 source versions.
- COURT-AT-062 — Disclosure package and service history is linked to BP-27.
- COURT-AT-063 — Evidence admission/receipt status is distinct from source existence.
- COURT-AT-064 — Evidence tendered by a party is not automatically admitted or accepted.
- COURT-AT-065 — An objection is recorded separately from the court's ruling on it.
- COURT-AT-066 — An exhibit may be admitted for a limited purpose where configured.
- COURT-AT-067 — An exhibit may be excluded without deleting the source record.
- COURT-AT-068 — An evidential ruling identifies scope, rationale and effective time.
- COURT-AT-069 — An evidential ruling may be challenged through configured procedure.
- COURT-AT-070 — New evidence received after a ruling does not rewrite the earlier ruling.
- COURT-AT-071 — Evidence versions available to the court are preserved as a snapshot.
- COURT-AT-072 — Missing or corrupt evidence is represented explicitly.
- COURT-AT-073 — Chain-of-custody challenge links to BP-23 records without rewriting them.
- COURT-AT-074 — Forensic challenge links to BP-24 records without rewriting them.
- COURT-AT-075 — Disclosure dispute links to BP-27 decisions and package versions.
- COURT-AT-076 — Protected or sensitive material is access-controlled.
- COURT-AT-077 — Closed judicial material remains restricted according to configured rules.
- COURT-AT-078 — Public/private hearing status is explicit and versioned.
- COURT-AT-079 — Anonymity or protective direction is a judicial order, not a UI-only setting.
- COURT-AT-080 — Protected identity is not exposed through search, summaries or metadata.
- COURT-AT-081 — Judicial deliberation records are segregated from party-accessible records.
- COURT-AT-082 — Judicial reasons may be published only under configured authority.
- COURT-AT-083 — An oral ruling and written order are separately represented when applicable.
- COURT-AT-084 — A written order links to the ruling it formalises.
- COURT-AT-085 — A corrected order preserves the original and correction history.
- COURT-AT-086 — Every order has a stable ID, issuing court, actor and authority.
- COURT-AT-087 — Every order records exact parties, scope, terms and effective time.
- COURT-AT-088 — An order cannot exceed the issuing court's configured authority.
- COURT-AT-089 — An order is not effective before its configured effective event/time.
- COURT-AT-090 — Service of an order is distinct from issuance.
- COURT-AT-091 — Receipt of an order is distinct from service.
- COURT-AT-092 — BP-27 records party-side receipt and procedural response.
- COURT-AT-093 — BP-26 validates and implements custody-related operational changes.
- COURT-AT-094 — BP-29 validates and implements sentence execution.
- COURT-AT-095 — BP-28 does not directly operate police custody or prison supervision.
- COURT-AT-096 — A bail/remand decision is recorded as an authoritative court order.
- COURT-AT-097 — A bail/remand order records conditions exactly as ordered.
- COURT-AT-098 — Variation or revocation creates a new order and preserves prior terms.
- COURT-AT-099 — A draft or unissued order cannot trigger release or sentence execution.
- COURT-AT-100 — An order does not silently mutate BP-26 custody status.
- COURT-AT-101 — A court direction concerning treatment references a BP-04/BP-24/BP-26 provider or source as applicable.
- COURT-AT-102 — Healthcare records remain owned by their source division and protected by BP-42.
- COURT-AT-103 — A court cannot fabricate a medical diagnosis or clinical finding.
- COURT-AT-104 — Judicial findings on fitness/capacity are distinct from clinical assessments.
- COURT-AT-105 — Sentencing occurs only after an authoritative finding/plea outcome under configured rules.
- COURT-AT-106 — A sentence identifies the correct defendant and determined charge/count.
- COURT-AT-107 — Sentencing reasons and factors are recorded with provenance.
- COURT-AT-108 — Sentencing orders identify type, duration/terms and effective trigger where configured.
- COURT-AT-109 — Concurrent and consecutive terms are represented distinctly where configured.
- COURT-AT-110 — Aggregate sentence calculations are reproducible from source orders.
- COURT-AT-111 — Uncertain or missing sentence parameters block invented calculations.
- COURT-AT-112 — Fines, compensation, restrictions and other orders use configured fictional categories.
- COURT-AT-113 — Sentence order amendment or correction preserves prior versions.
- COURT-AT-114 — A sentence does not execute itself in BP-28.
- COURT-AT-115 — BP-29 receives the authoritative sentence/order reference.
- COURT-AT-116 — Sentence and release dates reconcile with authoritative court orders.
- COURT-AT-117 — A conviction is distinct from sentence execution.
- COURT-AT-118 — Acquittal is distinct from dismissal, withdrawal and no-charge.
- COURT-AT-119 — Dismissal is recorded with its exact procedural or substantive basis.
- COURT-AT-120 — An acquittal does not erase police investigation or source evidence.
- COURT-AT-121 — A conviction applies only to the named person and charge version.
- COURT-AT-122 — One defendant's conviction does not determine another defendant's outcome.
- COURT-AT-123 — One count's outcome does not determine other counts.
- COURT-AT-124 — Partial verdicts and unresolved counts are supported.
- COURT-AT-125 — Mistrial or equivalent configured outcome does not imply acquittal.
- COURT-AT-126 — Deadlocked or undecided outcome remains explicitly unresolved where configured.
- COURT-AT-127 — Proceedings can conclude with mixed outcomes.
- COURT-AT-128 — Every outcome records its source hearing, decision-maker and effective time.
- COURT-AT-129 — Outcome correction or setting-aside preserves the original history.
- COURT-AT-130 — Appeal application and filing workflow remain BP-27-owned.
- COURT-AT-131 — Appeal adjudication and appellate orders are BP-28-owned.
- COURT-AT-132 — Appeal filing does not automatically stay a conviction or sentence.
- COURT-AT-133 — Only an authoritative appellate order changes the prior legal effect.
- COURT-AT-134 — An appellate outcome links to exact challenged decision/order versions.
- COURT-AT-135 — Appeal may be allowed in whole, in part, dismissed or remitted as configured.
- COURT-AT-136 — Remittal creates a linked further proceeding without erasing prior records.
- COURT-AT-137 — An appeal outcome does not rewrite police investigative source records.
- COURT-AT-138 — Review or retrial eligibility comes from configured fictional rules.
- COURT-AT-139 — Finality status is explicit and does not erase appeal history.
- COURT-AT-140 — Sentence variation is transmitted to BP-29 only by authoritative order.
- COURT-AT-141 — Custody changes are transmitted to BP-26 only by authoritative order.
- COURT-AT-142 — All judicial outcomes preserve links to correct charges, defendants and evidence versions.
- COURT-AT-143 — Every adjudicative decision records reasons, authority and material considered.
- COURT-AT-144 — Judicial conclusions do not reveal hidden generator truth.
- COURT-AT-145 — Judicial actors cannot access hidden culprit/accomplice identity from BP-14.
- COURT-AT-146 — No court record, judgment, dialogue or summary reveals hidden truth before exact bingo.
- COURT-AT-147 — No unsolicited investigative hints or next-step prompts are generated.
- COURT-AT-148 — NPC court knowledge is limited to observed, received or authorised information.
- COURT-AT-149 — AI-generated judicial summaries cite source records and preserve uncertainty.
- COURT-AT-150 — AI cannot invent testimony, evidence, rulings, pleas or reasons.
- COURT-AT-151 — AI cannot generate a verdict merely to advance gameplay.
- COURT-AT-152 — An AI summary cannot replace a judicial order or reasoned finding.
- COURT-AT-153 — All essential court workflows are available through text-only interface.
- COURT-AT-154 — Optional maps or graphics never contain exclusive judicial facts.
- COURT-AT-155 — Every material event is append-only and attributable.
- COURT-AT-156 — Every read/export/access to restricted court material is permission checked.
- COURT-AT-157 — Party access does not imply access to judicial deliberations.
- COURT-AT-158 — Judicial access does not imply unrestricted access to protected source identities.
- COURT-AT-159 — Audit records include actor, authority, purpose, time, record version and result.
- COURT-AT-160 — Corrections preserve original values and source records.
- COURT-AT-161 — Duplicate event replay does not create duplicate hearings, orders or outcomes.
- COURT-AT-162 — Partial persistence failure preserves completed sub-events and explicit incomplete status.
- COURT-AT-163 — All source-mapped BP-28 requirements and tests are traceable.
- COURT-AT-164 — Population identity references never create duplicate living persons.
- COURT-AT-165 — Case-connected persons remain permanently promoted to full persistent simulation.
- COURT-AT-166 — Living population never exceeds 10,000.
- COURT-AT-167 — Legal and court institutions remain proportionate and do not create a second deep society simulator.
- COURT-AT-168 — At least 10,000-business canon is not altered by court-system design.
- COURT-AT-169 — No external playable jurisdiction or additional city is created.
- COURT-AT-170 — No Neon schema, seed, import or bulk write is authorised by this specification.

## 36. Source traceability

Original source remains `docs/governance/SALTWATER_MASTER_BLUEPRINT.json` and is unchanged. The BP-28 mappings below are the exact source IDs mapped to BP-28 in the 52→44 crosswalk.

| Source ID | Source requirement/test | BP-28 coverage |
|---|---|---|
| S13.R02 | Healthcare and public-health support records and interfaces. | Sections 4, 24, 27, 29 and 31; court orders may reference configured clinical material or directions, while providers/source records remain with BP-04 and relevant operational divisions. |
| S29.R03 | Preserve distinct incident, crime, case and legal outcomes. | Sections 2, 4, 15, 17, 27 and 31; court disposition is separate from occurrence, allegation, police case and investigation. |
| S30.R02 | Link case management and investigative command with legal processes and court outcomes. | Sections 4, 27 and 31; court outcomes reference BP-15/BP-16 without rewriting them. |
| S31.R02 | Distinguish allegation, suspicion, evidential support, charge and finding. | Sections 2, 4, 12–17, 26 and 35; plea, evidence, charge, finding and verdict are distinct. |
| S38.R01 | Represent charging, disclosure, prosecution, defence, hearings, evidence, rulings, verdicts, sentencing, appeals and case outcomes. | Sections 4, 12–21 and 27–31; BP-27 owns charging/disclosure/party workflow; BP-28 owns hearings/adjudication/sentencing/appellate outcomes. |
| S38.R02 | Track procedural state and legal actors; preserve acquittals, dismissals and unresolved outcomes. | Sections 5–10, 15–17, 28–30 and 35; judicial appointment/authority, hearing lifecycle, disposition taxonomy and unresolved states. |
| S38.R03 | Feed outcomes back into records without rewriting investigative history. | Sections 4, 17, 27 and 31; outcomes link to case/investigation and corrections by immutable references. |
| S38.T01 | Court outcomes link to correct charges, defendants and evidence versions. | Sections 5, 13–17, 27–28 and 35; canonical IDs, charge versions, material manifests and party/count-specific outcome links. |
| S39.R01 | Represent sentence execution, prison/community supervision, rehabilitation, release, recall and post-release status proportionately. | Sections 4, 18, 20, 27 and 31; BP-28 owns sentence authority; BP-29 owns execution and supervision. |
| S39.R02 | Maintain continuity between custody, court and person records. | Sections 4, 19, 20, 27 and 31; BP-26/BP-29 implement court orders and BP-03 remains identity owner. |
| S39.T01 | Sentence and release dates reconcile with court orders. | Sections 18–20, 27–28 and 35; BP-29 reconciliation uses exact authoritative order and effective date. |

Cross-cutting rules:
- X03: all court dates, hearings, orders, sentence and appeal events use BP-37 canonical time; all progression freezes while paused/absent.
- X05: allegations, estimates, inferences, intelligence, opinions, source statements and adjudicated findings remain distinct.
- X06: originals are preserved; judgments and summaries do not replace source records; corrections are additive and attributable.
- Global canon: one Saltwater city/jurisdiction; 10,000 living-person cap; at least 10,000 businesses; police-depth priority; permanent case-person promotion; text-first completeness; exact `bingo` reveal firewall; no offline progression; no Neon writes without explicit approval.

All 11 mapped source requirement/test IDs are explicitly traced. Source JSON and crosswalk are not modified by this specification.

## 37. Risk register

| Risk | Control |
|---|---|
| Party submission confused with judicial decision | Separate BP-27 and BP-28 authoritative records |
| Charge confused with conviction | Charge version links to distinct court disposition |
| Court finding fabricated from hidden truth | Strict knowledge firewall and record-only adjudication |
| Judicial authority assumed from title | Appointment and jurisdiction validation |
| Hearing scheduled but treated as completed | Separate listing and hearing lifecycle |
| Evidence receipt confused with admission | Explicit treatment states and ruling reference |
| Evidence source overwritten by court copy | Immutable source links and court manifest |
| Acquittal erases police history | Downstream reference only; no case rewrite |
| Sentence confused with execution | BP-28 order vs BP-29 implementation |
| Court order confused with custody release | BP-26 validates and executes operational change |
| Appeal assumed to stay sentence | Explicit authoritative stay/variation order |
| NPC court work advances offline | BP-37 pause invariant |
| Restricted identity leaks in public judgment | Access classes, redacted derivatives and audit |
| Court simulation expands into society simulation | Proportionate institutions and staffing |

## 38. Design completion checklist

- [ ] Court institution and jurisdiction model defined.
- [ ] Judicial appointments, authority and independence controls defined.
- [ ] Court proceeding, listing and hearing lifecycle defined.
- [ ] Participation and attendance records defined.
- [ ] Plea and admission distinctions defined.
- [ ] Court material receipt and evidential treatment defined.
- [ ] Objections and judicial rulings defined.
- [ ] Findings, verdicts, judgments and dispositions defined.
- [ ] Sentencing and order lifecycle defined.
- [ ] Bail/remand and custody handover defined.
- [ ] Appeal adjudication and appellate outcomes defined.
- [ ] Court record, transcript and publication controls defined.
- [ ] Healthcare/specialist interface and privacy boundaries defined.
- [ ] Pause/time-freeze and NPC knowledge rules defined.
- [ ] Population cap and permanent person promotion preserved.
- [ ] Text-first workflows and reporting defined.
- [ ] Audit, correction, retention and security boundaries defined.
- [ ] All 170 acceptance tests await BP-43 execution.
- [ ] All 11 mapped source requirement/test IDs traced.
- [ ] Open fictional policy decisions remain explicit.
- [ ] No Neon schema, seed, import or bulk write made or authorised.

## 39. Status and next dependencies

This is a design draft, not approved fictional law, implemented functionality or executed test evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-29 — Corrections**. BP-28 is the authoritative source of sentence and judicial order records. BP-29 owns sentence commencement, custody within correctional institutions, community supervision, rehabilitation, release, recall and post-sentence status. BP-26 remains owner of police custody; BP-03 remains owner of person identity/lifecycle.
