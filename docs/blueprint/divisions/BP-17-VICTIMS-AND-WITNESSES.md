# BP-17 — Victims and Witnesses

**Project:** Saltwater  
**Division:** BP-17 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT  
**Implementation:** NOT_STARTED  
**Test execution:** NOT_STARTED  
**Verification:** NOT_STARTED  
**Authority:** Derived from the unchanged 52-division source blueprint and 52→44 crosswalk. This draft does not approve canon or structural changes.

## 1. Purpose

Define the complete, persistent and auditable victim- and witness-participant domain for Saltwater police activity and cases. Represent each person's case-specific role, contact and availability, impact, needs, vulnerability, risk, safeguarding, support, procedural participation, referrals and changing status without changing authoritative person identity or assuming guilt, credibility, cooperation or evidential value.

A person may hold several roles in one or several cases at different times. Each role is independent and historised. A person may be a victim in one case and a witness, reporter, employee, family member, officer or suspect in another. Role overlap is not contradiction and establishes no wrongdoing.

## 2. Scope and ownership

### 2.1 BP-17 owns

- Victim and witness case-participant records and role-specific lifecycle.
- Participant role episodes, effective dates, source basis and status.
- Alleged victim, affected person, witness, potential witness, reporting person, caller linkage, indirect impact, expert-witness participation, representative, advocate and support-person roles.
- Contact channels, verification, safe-contact restrictions, communication preferences and availability declarations.
- Participant-reported needs, accessibility requirements, vulnerability assessments, safeguarding concerns and participant-related risk assessments.
- Victim/witness support needs, referrals, provider responses, consent/authority references and support episode status.
- Participant update preferences, liaison, notification history and participant-supplied impact information.
- Corrections or challenges to participant records, with source ownership and resolution preserved.
- Versioned links to interviews, statements, calls, incidents, medical records, scenes, exhibits, intelligence, investigations and legal processes.
- Confidentiality, role separation and participant-specific access metadata.

### 2.2 Explicit exclusions

| Concern | Owner | BP-17 relationship |
|---|---|---|
| Person identity, matching, life status, population ledger, 10,000 cap, permanent full-detail promotion | BP-03 | References person ID; never creates shadow identities or alters population count |
| Household, family, friendship, conflict and social-network semantics | BP-36 | References relationship IDs and case relevance only |
| Case identity, lifecycle, assignment, closure/reopening and related-case links | BP-15 | References case IDs; cannot open, close, merge or split cases |
| Investigative plans, leads, hypotheses, tasks and decisions | BP-16 | Supplies authorised participant information; does not direct investigation |
| Suspect/offender roles and statuses | BP-18 | Separate roles may coexist; BP-17 cannot assign guilt or overwrite them |
| Interview planning, procedural status, questions, answers, recordings and statements | BP-19 | Provides participant association and needs; BP-19 owns source records |
| Surveillance | BP-20 | References only authorised participant-related sources |
| Intelligence lifecycle, grading and confidence | BP-21 | Does not convert a witness account into intelligence |
| Scene control/search | BP-22 | References participant/scene links only |
| Exhibit identity, custody and continuity | BP-23 | Read-only source references; no evidential custody authority |
| Forensic methods, results and interpretation | BP-24 | References exact source versions |
| Arrest, warrants and searches | BP-25 | No arrest/search authority |
| Custody | BP-26 | May receive authorised interface events only |
| Legal process, disclosure, prosecution and summons | BP-27 | Supplies exact source versions and liaison history |
| Court proceedings and findings | BP-28 | References outcomes; never rewrites original accounts |
| Corrections | BP-29 | No ownership |
| Providers, facilities and service directory | BP-04 | Owns provider records and capacity |
| Public-service governance and safeguarding authority | BP-30 | Owns authority and policy; BP-17 tracks participant-facing referral |
| Police personnel/employment | BP-06/BP-33 | Officer identity remains in BP-03 with separate employment role |
| Global canon and player agency | BP-01 | Binding invariants |
| Simulation event execution/NPC behaviour | BP-35 | Executes permitted events; cannot grant omniscience |
| Canonical time/calendar | BP-37 | All time-bearing facts use its clock |
| Schemas, provenance, record versions | BP-38 | BP-17 domain records comply with global record rules |
| Persistence and recovery | BP-39 | Preserves IDs, history and audit |
| Text interface | BP-40 | Complete text operation; visuals optional |
| Notifications/report delivery | BP-41 | Delivery infrastructure; BP-17 owns participant preferences |
| Security and permissions | BP-42 | Authoritative access matrix and hidden-information controls |
| QA and evidence | BP-43 | Executes tests and stores reproducible evidence |
| Change control | BP-44 | Controls amendments and status changes |

## 3. Governing invariants

1. A victim or witness role is a case-specific relationship, not a person's identity.
2. A person may hold multiple simultaneous or successive roles. Each role has a distinct ID, case link, effective period, source and status.
3. A victim, witness, caller, reporter or affected-person label does not prove an offence occurred, an account is accurate, a person is credible, or another person is guilty.
4. Allegation, account, observation, intelligence, evidence, expert opinion, inference, charge and judicial finding remain distinct.
5. An alleged victim may be recorded while the allegation remains unverified, disputed or withdrawn.
6. A witness role requires a recorded basis; it is not assigned merely because someone assumes a person knows something.
7. Refusal, silence, inability to contact, memory limitation, distress, disability, delay, inconsistency or withdrawal is not automatically deception, guilt or lack of credibility.
8. Confidentiality and safety restrictions apply to every read, search, aggregate, report, export, notification, generated dialogue and visualisation.
9. Shared case membership does not permit one participant to see another's protected details.
10. Case closure does not erase person identity, participant history, support history, statements or source links.
11. Any person materially connected to police activity or a case is promoted by BP-03 to persistent full-detail status for the remainder of the simulation. Promotion is permanent; no downgrade, deletion or shadow identity.
12. The total living population never exceeds 10,000. A participant link does not create another counted person.
13. Culprit, accomplice and perpetrator identities remain hidden unless the player types exactly bingo. The gate applies to direct and indirect output.
14. Never provide unsolicited solution hints or tell the player what to investigate next. Present available records and leave decisions to the player.
15. No simulation time, contact attempt, referral, review, notification, availability change, NPC action or deadline progresses while the player is outside the simulation.
16. Preserve original participant statements and source records. Summaries never replace originals.
17. Material changes are attributed, canonical-time-stamped, reasoned, versioned and historically queryable.
18. Compress representation, never meaning, uncertainty, chronology, provenance or relationships.

## 4. Core entities and identifiers

All IDs are stable, opaque and non-semantic. Exact prefixes/display formats are BP-38/BP-44 decisions.

| Entity | Required ID | Purpose |
|---|---|---|
| Person reference | person_id | BP-03 identity; no local person duplicate |
| Participant link | participant_id | One person's role in one case context |
| Role episode | role_episode_id | Dated role/status period |
| Contact point reference | contact_point_id | Restricted channel reference |
| Contact preference | contact_preference_id | Consent, safe method, timing and limits |
| Availability record | availability_id | Time-bounded declaration/contactability |
| Needs assessment | needs_assessment_id | Versioned needs/accessibility assessment |
| Risk assessment | participant_risk_id | Risk scope, basis and mitigation |
| Safeguarding concern | safeguarding_id | Concern/referral/action history |
| Support referral | support_referral_id | Referral lifecycle |
| Support episode | support_episode_id | Provider response and outcome |
| Liaison event | liaison_event_id | Attributed contact/update |
| Participant correction | correction_id | Challenge and resolution |
| Consent/authority | consent_authority_id | Scope-limited consent/legal authority reference |
| Participant-source link | participant_source_link_id | Versioned source link |

### 4.1 Common record fields

As applicable, every persistent entity includes: stable ID; schema version; person/case/role references; source type and exact source version; actor/system; created and changed canonical times; effective-from/effective-to; recorded-at; status and reason; sensitivity/classification; authority/consent basis and scope; provenance; confidence/uncertainty; reported/observed/assessed/imported/derived distinction; supersession/correction links; access policy reference; correlation and idempotency identifiers.

### 4.2 Identity and matching

- BP-03 alone owns person identity and matching.
- An unidentified participant may use an unresolved BP-03 reference under BP-03 rules; no parallel permanent identity is created.
- Possible matches remain possible until BP-03-authorised reconciliation.
- Mistaken matching is corrected through a versioned event preserving the original association.
- Similar names, addresses, telephone numbers, family links or appearance are not sufficient to merge identities.
- A participant link may precede identity resolution but must retain its source basis and unresolved status.

## 5. Participant role catalogue and lifecycle

### 5.1 Minimum role catalogue

- **Alleged victim:** person reported as directly subjected to or targeted by an alleged event; not a finding.
- **Confirmed affected person:** impact is supported by an authorised record; does not prove offence elements or guilt.
- **Witness:** person believed to have relevant first-hand or attributable information, with basis recorded.
- **Potential witness:** possible relevance recorded without conclusion that useful knowledge exists.
- **Reporting person:** communicates an event whether or not personally affected.
- **Caller:** person contacting emergency/non-emergency communications; call record remains BP-11-owned.
- **Indirectly affected person:** person whose welfare, property, household or livelihood is affected without a direct-victim label.
- **Expert witness participant:** participates in an expert capacity; expertise/report/opinion remain in source domains and BP-27.
- **Family/representative contact:** person recorded or authorised to contact another participant; not automatically a witness.
- **Support person/advocate:** provides support; presence does not automatically make them a witness.
- **Anonymous/confidential participant:** restricted identity handling; not an assumption of reliability or intelligence status.

The catalogue is extensible only through BP-44. Suspect/offender categories remain BP-18-owned.

### 5.2 Role episodes and statuses

Each role is a separate episode with start/end, source, status and reason. One person may hold multiple roles in one case and across cases. Role changes create a new episode or versioned transition; prior history is not rewritten. Roles may be provisional, disputed, mistaken, withdrawn, ended, superseded or reinstated.

The minimum lifecycle supports proposed → recorded → active → under_review → ended, with disputed, withdrawn, mistaken, superseded and reopened states. Transitions require an authorised actor, reason, source and canonical time. Withdrawal applies only to the stated scope; it does not erase a prior event or source. Mistaken links remain as historical errors with correction. Reopening preserves prior disposition. Role status is never an evidential or case outcome.

## 6. Contact points, safe contact and preferences

A person may have multiple independently classified contact points: telephone, email, in-person location, authorised representative, service-provider contact or another configured channel.

- Raw values are held only in the authorised protected store; ordinary views mask/minimise them.
- Each point records source, verification, effective dates, permitted purposes, restrictions and review date.
- A number/address may be shared, reassigned, stale, unsafe or controlled by another person.
- Invalid/unreachable contact does not invalidate the participant.
- Do not copy protected values into general case notes when a restricted reference suffices.
- Record preferred and alternative channels; permitted hours/days; voicemail/text/email permission; shared-device/account risks; permitted intermediaries and exact scope; interpretation/accessibility requirements; no-contact or limited-contact requests; source, consent/authority, effective period and review trigger.
- Preference is not itself a legal prohibition or disclosure authority. BP-27/BP-42 govern legal restrictions and access.
- Emergency exceptions, if configured, are narrow, authorised, reasoned and audited.

Every material attempt records participant/role, actor, purpose, authority, channel, contact-point reference, start/end time, outcome, actual answering party where known, summary/source recording, new safety concern and any follow-up explicitly selected by an authorised actor. Outcomes include attempted, connected, refused, interrupted, unsafe, unsuccessful and deferred. A device owner is not assumed to be the person answering. No contact occurs during pause.

## 7. Availability and participation

Availability is a time-bounded statement, not a promise or proof of cooperation. Record declared windows, constraints, source, location restrictions, time basis, cancellations, missed appointments and rescheduling. Distinguish participant declaration, third-party report, observed contactability and system inference. Conflicting accounts remain separate. Non-attendance, silence, refusal or inability to attend does not imply guilt or deception.

Support work, caring duties, health, transport, safety, accessibility, education, employment and participant-stated obligations may be represented without inferring sensitive traits. Appointment scheduling belongs to BP-19/BP-27/provider workflow; BP-17 owns participant constraints and references the appointment. Appointments do not progress during pause.

## 8. Vulnerability, needs and accessibility

Assessments are contextual, time-bounded, purpose-specific and versioned, not permanent labels. Record source and basis: self-disclosure, observation, professional assessment, third-party report or derived indicator. Distinguish the participant's own description from professional assessment and unverified third-party claim. Do not infer vulnerability solely from age, disability, injury, diagnosis, relationship, occupation, income, housing or case role.

Support at least:
- Communication, language and interpretation.
- Mobility, sensory, cognitive and other accessibility arrangements.
- Age/developmentally appropriate communication.
- Advocate, support person or trusted intermediary.
- Safe transport and waiting arrangements.
- Distress-sensitive contact, breaks and paced communication.
- Medical/welfare assistance request.
- Cultural support requested by participant.
- Protection from intimidation, coercion, retaliation or disclosure.
- Scheduling, caring, employment and practical participation constraints.
- Other participant-defined needs.

Unknown needs, not-yet-assessed needs, no identified needs and declined assessment are distinct. Clinical diagnosis/treatment remain with healthcare providers; BP-17 stores minimum necessary functional needs and restricted references. Reviews may be triggered by participant request, new information, material change, incident, referral response, contact event, configured in-world interval or authorised decision. No review occurs while paused. Earlier assessments remain queryable.

## 9. Risk and safeguarding

Risk domains may include risk to participant, risk posed by participant (without assuming guilt), intimidation, coercion, retaliation, harassment, unwanted disclosure, immediate welfare/medical concern, unsafe contact/address/device, child/dependent safeguarding, self-neglect or accidental disclosure through police/service/court workflows.

Every assessment records scope, source, assessor, canonical time, confidence/uncertainty, factors, protective factors, mitigation, review trigger and access classification. Any future score must not replace the narrative basis or be treated as objective truth.

Safeguarding lifecycle: identified → recorded → triaged → referred/retained_for_action → action_pending → reviewed → resolved/closed. BP-30 owns public authority and safeguarding policy; BP-04 owns providers. BP-17 tracks participant-facing referral and status only.

- Urgent danger may trigger an authorised urgent notification under configured policy; it does not grant unrestricted access.
- Record decision-maker, information considered, urgency, scope and receiving service.
- Referral outcomes include accepted, declined, redirected, pending, partially fulfilled, returned for information or closed without service.
- Referral is not proof that the concern is true; inability to accept is not proof it is false.
- Repeated referrals link to earlier referrals; they are not false independent corroboration.
- Refusal of support is recorded respectfully and does not erase concern or create adverse inference.
- Conflicts between participant preference and authorised safeguarding decision preserve both, with rationale and restricted access.

## 10. Support services and referrals

BP-04 owns provider/service/facility directory; BP-30 owns public-service authority/governance. BP-17 references provider ID, service type, eligibility, time-valid capacity, referral method, minimum required information, secure channel, operating status, authorised contact and BP-02 location ID. Off-map services may be contextual references only; they do not create playable territory.

A referral records: referral ID; participant/case and originating concern/needs; referring actor/authority/time; receiving provider; purpose and requested assistance; minimum information disclosed; consent/authority and scope; urgency/safety handling; acknowledgement, decision, appointment, response and outcome; delivery evidence/failure; source version and follow-up owner where assigned.

Minimum referral states: draft, authorised, sent, acknowledged, accepted, declined, redirected, awaiting_information, pending_capacity, partially_fulfilled, fulfilled, withdrawn, closed_no_service and failed_delivery. Sent requires delivery attempt/result; acknowledgement is not acceptance; acceptance is not completion; fulfilment requires provider response or valid evidence; partial fulfilment remains distinct; reopening preserves previous history. Service outcomes do not determine credibility.

Service simulation is proportionate: capacity, eligibility, referral state, response delay and outcome are represented sufficiently for coherent play, without turning healthcare/social care/charities into a second deep simulation.

## 11. Participant updates and liaison

Record participant's preferred level/method of updates where permitted. Distinguish requested, approved, prepared, sent, delivered, acknowledged, declined and withheld. BP-41 owns delivery infrastructure; BP-17 owns preferences and liaison history.

Screen each update for safety, case sensitivity, legal restriction, operational risk and information about another person. Do not promise outcomes/timelines or disclose another person's identity, address, statement or protected status. A withheld update records authorised reason and review condition without exposing protected information. Delivery failure is not receipt. A request for updates is not consent to disclose the whole case. Notifications freeze during pause.

## 12. Impact, corrections and participant challenges

Impact may include physical, emotional, practical, property, financial, household, work, education, community or other consequences as described by participant or authorised source. Keep reported impact distinct from verified loss, medical diagnosis, insurance value, forensic finding or judicial determination. Preserve original wording/recording; summaries are labelled and linked. Do not infer monetary value or severity.

Corrections may challenge identity, role, contact, chronology, attributed words, needs, risk or support status. Record the correction request immediately; the authoritative source owner decides whether its source changes. Rejected/partly accepted corrections retain the request and reasoned response. One participant cannot edit another person's source record merely because they share a case.

## 13. Specialist interfaces

- **BP-11/BP-12:** caller, call and incident references remain authoritative there. Caller account is not automatically a witness statement.
- **BP-15/BP-16:** case belongs to BP-15; investigative work belongs to BP-16. BP-17 supplies authorised participant information and never creates/ranks leads or recommends next steps.
- **BP-18:** suspect/offender role remains separate; either role does not cancel the other.
- **BP-19:** owns interview planning, procedural status, recordings, notes, questions, answers and statement versions. BP-17 supplies participant reference, accessibility and safe-contact requirements. A request does not fabricate an interview.
- **BP-23/BP-24:** BP-17 references exact exhibit/forensic versions; cannot change custody, raw result or interpretation.
- **BP-27/BP-28:** own disclosure, prosecution, summons, proceedings and findings. BP-17 supplies exact source versions and liaison references.
- **BP-04/BP-30:** own service/provider and public authority; BP-17 tracks referral and participant-facing state.

## 14. Knowledge, uncertainty and NPC behaviour

NPCs know only what they observed, were told, received through authorised handoff or derived through a permitted process. A witness does not automatically know another witness's account, suspect status, case file or police hypothesis. A victim does not automatically know offender identity or motive. A service provider knows only authorised referral information and its own service records. Family/representatives do not automatically know private details or gain update authority.

Memory, confidence, perception and recall may be incomplete. Contradictions remain separate source records. Generated dialogue reflects plausible character voice and known information without hidden-truth leakage, insinuation or leading prompts. No NPC gives unsolicited advice on whom to contact/interview/investigate. Neutral participant listings are permitted only when requested and never ranked by hidden culprit relevance.

## 15. Information classification and access

BP-42 owns access control. BP-17 supplies classifications and enforces checks on read, write, search, aggregation, export, notification and visualisation.

Minimum classes: general participant index; restricted identity/contact; safe address/contact; vulnerability/accessibility; safeguarding/risk; medical liaison; confidential/anonymous identity; interview/statement references; referral/provider communications; participant impact/financial/property; legal restriction/disclosure hold.

Rules:
1. Least privilege; case assignment alone does not grant all sensitive fields.
2. Reviewer, supervisor, service liaison or administrator receives only explicit access.
3. Access denial cannot confirm existence or role to unauthorised users.
4. Search snippets, counts, autocomplete, errors and exports cannot leak protected values/existence.
5. Shared devices/accounts are treated as possible disclosure risks.
6. Sensitive data is excluded from ordinary logs, analytics, debug output, source control and generated prompts unless specifically authorised and minimised.
7. Emergency access, if configured, is scoped, reasoned, time-limited, logged and reviewed.
8. Denial does not disclose protected reason.
9. The bingo gate does not replace ordinary permissions.
10. No participant-facing surface reveals hidden offender identity before exact bingo.

## 16. Time and pause semantics

Every time-bearing fact uses BP-37 canonical in-world time and preserves source/time basis. Keep event time, report time, entry time, effective time and correction time distinct where needed. Preserve local-time context and uncertainty. Availability, contact limits, appointments, service hours, review intervals and notification schedules are effective-dated.

No clock tick, deadline, contact attempt, notification, referral transmission, provider response, NPC decision or review occurs while the player is outside the simulation. Resume from exact persisted state; no real-world catch-up or silent queue processing. Events scheduled during pause remain pending until resumed and processed under deterministic ordering. Time-zone/calendar changes never rewrite historical timestamps.

## 17. Population, persistence and lifecycle

BP-03 owns the sole population ledger and person lifecycle. Every materially relevant victim/witness is permanently promoted through BP-03. Promotion is idempotent; repeated case links do not create duplicate people or population entries. A participant link does not increment population. Any new person admission is subject to atomic BP-03 cap enforcement and the 10,000 living-person maximum. Deceased and permanently departed participants retain historical records. A participant may be inactive in one case and active in another. Case closure, role termination or support completion never downgrades identity. Material events and dependent references commit atomically or fail without partial state.

## 18. Records, audit and correction

All BP-17 records are versioned/source-linked under BP-38. Preserve original text/media/provider responses; derived summaries are separate. Corrections are append-only events with before/after references, author, time, reason, authority and review outcome. Audit includes restricted reads, exports, emergency access, disclosure decisions and safe-contact changes. Audit is itself protected from ordinary alteration. Idempotency prevents duplicate referrals, contacts, notifications and transitions. Concurrent edits preserve both versions for reconciliation. Restore preserves IDs, episodes, source versions, restrictions, audit and referral state. Storage optimisation cannot remove meaning.

## 19. Text interface and optional visuals

Text is the complete primary interface. Authorised workflows must list participant links; open a participant record while distinguishing identity from role; view role history, source, restrictions, availability and support state; create/update/correct roles with provenance; record contact and liaison; track referrals; view permitted updates; inspect audit within permission. Command syntax belongs to BP-40.

Optional visuals: participant-role timeline, referral flow, contact/availability calendar or relationship view. All derive from canonical records, obey access, carry as-of time/source references and never infer guilt, credibility, relationship or hidden truth. Visuals are never required.

## 20. Inputs, outputs and event contracts

**Inputs:** BP-03 person/lifecycle; BP-04 providers; BP-11/BP-12 caller/incident; BP-15 case; BP-16 investigative context; BP-18 separate suspect role; BP-19 interview/statement; BP-23/BP-24 evidence/forensic source; BP-27/BP-28 legal restrictions/outcomes; BP-30 authority; BP-37 time; BP-42 permission.

**Outputs:** versioned participant roles; contact/preferences/availability/liaison; needs/risk/safeguarding; referral/support status; impact/correction; authorised BP-41 notification/report inputs; provenance-backed events and source links for BP-38/BP-39.

Each event includes stable ID, actor/source, canonical event time, recorded time, correlation/idempotency key, entity references, schema version, authority/consent basis, prior-state reference and resulting-state reference. Events include role proposed/activated/ended/reopened; contact preference changed; safe-contact restriction added/removed; availability declared/changed; assessment recorded/reviewed; safeguarding opened/referred/resolved; referral sent/acknowledged/accepted/declined/fulfilled; liaison sent/withheld; correction submitted/resolved; source link added/restricted/withdrawn.

## 21. Failure handling and edge cases

- Unknown identity: unresolved BP-03 reference; no local permanent identity.
- Duplicate candidate: possible match pending BP-03.
- Mistaken match: preserve original, append correction, authorised re-link only.
- Anonymous/confidential participant: preserve known facts and restrict identity; no unauthorised discovery.
- Shared device/contact: safe-contact assessment; no involvement disclosure.
- Unsafe address: restricted and excluded from ordinary views.
- Refusal/no response: record scope and attempt; no motive inference.
- Conflicting accounts: preserve all versions and sources.
- Late report/inconsistent dates: separate event/report time and retain uncertainty.
- Multiple/cross-case roles: separate episodes and permissions.
- Disputed/withdrawn role: preserve history and exact scope.
- Death/permanent exit: preserve history and disable only invalid future contact.
- Referral failure/provider full: retain delivery/provider reason; no false acceptance.
- Partial service: retain partial fulfilment and unresolved need.
- Safeguarding emergency: configured authority and minimum disclosure only.
- Legal/preference conflict: preserve both; route authority decision to BP-27/BP-30.
- Access denied: no existence/role leakage.
- Pause: all scheduled activity frozen.
- Population cap: role link proceeds without duplicate person; new admission follows BP-03.
- Persistence failure: atomic rollback or safe idempotent retry.
- Narrative inconsistency: source wins; correct derived output with audit.

## 22. Dependencies and failure contracts

| Dependency | Contract | Failure behaviour |
|---|---|---|
| BP-03 | Stable identity, lifecycle, population and promotion | Hold unresolved; no duplicate |
| BP-04 | Provider registry, eligibility, capacity, response | Referral pending/failed with reason |
| BP-11/BP-12 | Caller/call/incident sources | Preserve source; mark link unavailable |
| BP-15 | Case ID/status/access | No orphan participant link |
| BP-16 | Investigative context/request | No automatic lead/task |
| BP-18 | Separate suspect/offender role | Never infer/overwrite |
| BP-19 | Interview/statement source versions | Pending request; no fabricated record |
| BP-23/BP-24 | Evidence/forensic versions | No unsupported evidential claim |
| BP-27/BP-28 | Legal/disclosure restrictions | Restrict pending authoritative response |
| BP-30 | Safeguarding/public-service authority | Unresolved and visible to authorised role |
| BP-35/BP-37 | Causal events, canonical time and pause | Freeze all scheduled work |
| BP-38/BP-39 | Schema, provenance, atomic persistence/recovery | No partial commit |
| BP-40/BP-41 | Text workflow, notification/report delivery | Suppress unsafe output; preserve status |
| BP-42 | Access/confidentiality/hidden truth | Deny safely and audit |
| BP-43/BP-44 | Test evidence and controlled change | No completion promotion without evidence/approval |

## 23. Logical permissions

BP-42 owns the role-to-capability matrix. BP-17 capabilities include:
- participant.read.index
- participant.read.identity_restricted
- participant.read.contact
- participant.read.safe_contact
- participant.read.needs
- participant.read.risk
- participant.read.safeguarding
- participant.read.referral
- participant.read.source_links
- participant.create.role
- participant.update.role
- participant.record.contact_attempt
- participant.update.preference
- participant.record.assessment
- participant.create.referral
- participant.authorise.referral
- participant.record.liaison
- participant.submit.correction
- participant.resolve.correction
- participant.export
- participant.emergency_access
- participant.audit.read

Read does not imply write, export or disclosure authority. Emergency access is scoped, reasoned and audited. Self-approval of access elevation is prohibited unless BP-42 explicitly authorises a narrow exception.

## 24. Acceptance tests

These are specified, not executed. BP-43 must link reproducible evidence before any test is passed.

### Identity, roles and lifecycle
- **VIC-AT-001** — Victim role references an existing BP-03 person and creates no second person.
- **VIC-AT-002** — Witness role references an existing BP-03 person and retains provenance.
- **VIC-AT-003** — A person may hold victim and witness roles simultaneously with separate bases.
- **VIC-AT-004** — Different roles in different cases remain independent.
- **VIC-AT-005** — Victim in one case and suspect in another does not cause role overwrite.
- **VIC-AT-006** — Each role episode has a stable unique ID.
- **VIC-AT-007** — Ending a role preserves all prior history.
- **VIC-AT-008** — Reopening records actor, reason, time and prior end state.
- **VIC-AT-009** — Disputed role retains dispute source and authorised visibility.
- **VIC-AT-010** — Withdrawal does not delete original report/source.
- **VIC-AT-011** — Mistaken link is corrected without destructive deletion.
- **VIC-AT-012** — Unidentified participant does not become a duplicate BP-03 identity.
- **VIC-AT-013** — Possible identity match awaits BP-03-authorised reconciliation.
- **VIC-AT-014** — Similar names/contact details do not auto-merge people.
- **VIC-AT-015** — Successive role episodes preserve effective periods.
- **VIC-AT-016** — Role overlap/status transitions retain source basis and exact time.
- **VIC-AT-017** — Material relevance triggers permanent BP-03 full-detail promotion.
- **VIC-AT-018** — Promoted person is never downgraded after role/case closure.
- **VIC-AT-019** — Repeated case links do not duplicate population entry.
- **VIC-AT-020** — Death/permanent departure preserves historic role/source records.

### Information and evidential distinction
- **VIC-AT-021** — Alleged-victim label does not establish an offence.
- **VIC-AT-022** — Witness label does not establish credibility or accuracy.
- **VIC-AT-023** — Reporting person is not automatically a direct victim.
- **VIC-AT-024** — Caller record remains BP-11-owned and is not silently converted to statement.
- **VIC-AT-025** — Account remains distinct from intelligence, evidence, inference and finding.
- **VIC-AT-026** — Inconsistency is not automatically labelled deception.
- **VIC-AT-027** — Refusal/non-response is not automatically guilt or obstruction.
- **VIC-AT-028** — Support referral does not prove the underlying concern.
- **VIC-AT-029** — Provider outcome does not determine credibility.
- **VIC-AT-030** — Charge/court finding does not rewrite original account.
- **VIC-AT-031** — Summary is distinguished from original/verbatim source.
- **VIC-AT-032** — Conflicting accounts remain separately accessible with provenance.
- **VIC-AT-033** — Late report preserves event and report times separately.
- **VIC-AT-034** — Approximate/conflicting recollections retain uncertainty.
- **VIC-AT-035** — Correction request remains even if source owner declines it.

### Contact and availability
- **VIC-AT-036** — Multiple contact points coexist with independent verification/restrictions.
- **VIC-AT-037** — Shared phone is not assumed exclusive to participant.
- **VIC-AT-038** — Safe-contact restriction prevents prohibited channel use.
- **VIC-AT-039** — Shared device triggers disclosure-risk handling.
- **VIC-AT-040** — Masked contact values appear without full permission.
- **VIC-AT-041** — Unsafe address is hidden from ordinary views.
- **VIC-AT-042** — Preference records scope, source, period and review condition.
- **VIC-AT-043** — Contact may be restricted to a named intermediary.
- **VIC-AT-044** — Intermediary cannot exceed authority scope.
- **VIC-AT-045** — Contact attempt records actor, purpose, channel, time and outcome.
- **VIC-AT-046** — Device respondent is not assumed to be participant.
- **VIC-AT-047** — Failed contact does not mark participant uncooperative.
- **VIC-AT-048** — Preference withdrawal preserves prior contact history.
- **VIC-AT-049** — Availability retains source and time basis.
- **VIC-AT-050** — Conflicting availability reports remain separate.
- **VIC-AT-051** — Missed appointment does not create negative credibility assessment.
- **VIC-AT-052** — Practical constraints recorded without motive inference.
- **VIC-AT-053** — Contact/appointment cannot complete during pause.
- **VIC-AT-054** — Rescheduling preserves original appointment and reason.
- **VIC-AT-055** — Failed notification is not successful delivery/receipt.

### Needs, risk and safeguarding
- **VIC-AT-056** — Needs assessment records source, assessor, scope, time and uncertainty.
- **VIC-AT-057** — Unknown/not-assessed/no-needs/declined are distinct.
- **VIC-AT-058** — Declined assessment creates no adverse inference.
- **VIC-AT-059** — Needs assessment is versioned and time-bounded.
- **VIC-AT-060** — New assessment does not overwrite prior assessment.
- **VIC-AT-061** — Age/disability/diagnosis alone does not assign vulnerability.
- **VIC-AT-062** — Accessibility needs do not expose unnecessary clinical data.
- **VIC-AT-063** — Risk record includes factors, protections, mitigation and review.
- **VIC-AT-064** — Risk to participant is distinct from risk posed by participant.
- **VIC-AT-065** — Unverified third-party concern remains a report, not finding.
- **VIC-AT-066** — Safeguarding referral records authority, recipient and minimum disclosure.
- **VIC-AT-067** — Acknowledgement is not acceptance.
- **VIC-AT-068** — Acceptance is not service completion.
- **VIC-AT-069** — Declined/unavailable service retains reason and history.
- **VIC-AT-070** — Partial fulfilment remains distinct from full fulfilment.
- **VIC-AT-071** — Repeat referrals link to prior referral and do not falsely corroborate.
- **VIC-AT-072** — Refusal of support does not erase concern or force closure.
- **VIC-AT-073** — Urgent disclosure uses configured authority and minimum data.
- **VIC-AT-074** — Preference/legal-authority conflict preserves both and decision-maker.
- **VIC-AT-075** — Provider capacity is time-valid; stale responses are not current.

### Specialist and legal interfaces
- **VIC-AT-076** — Participant link cannot create/close a BP-15 case.
- **VIC-AT-077** — BP-17 cannot create/rank investigative leads.
- **VIC-AT-078** — Interview request creates BP-19 request, not interview/statement.
- **VIC-AT-079** — BP-19 owns recording, notes, questions, answers and statement versions.
- **VIC-AT-080** — Participant source link identifies exact BP-19 version.
- **VIC-AT-081** — BP-17 cannot alter BP-23 exhibit custody/continuity.
- **VIC-AT-082** — BP-17 cannot alter BP-24 raw results/interpretation.
- **VIC-AT-083** — Medical liaison does not expose full clinical record without permission.
- **VIC-AT-084** — BP-27 disclosure restriction applies to views and exports.
- **VIC-AT-085** — BP-28 outcome does not rewrite participant/statement history.
- **VIC-AT-086** — Provider receives only authorised referral information.
- **VIC-AT-087** — Off-map provider does not create playable territory.
- **VIC-AT-088** — Multiple scene links do not transfer scene control to BP-17.
- **VIC-AT-089** — Expert-witness role does not transfer expert/report ownership.
- **VIC-AT-090** — Family representative has no update access without authority.

### Player agency and hidden truth
- **VIC-AT-091** — NPC knowledge derives only from observation, receipt or authorised handoff.
- **VIC-AT-092** — Witness cannot see another witness's protected account by shared case membership.
- **VIC-AT-093** — Victim is not automatically given suspect identity or police hypothesis.
- **VIC-AT-094** — NPC dialogue does not reveal culprit through insinuation.
- **VIC-AT-095** — No unsolicited prompt tells player whom to contact/interview/investigate.
- **VIC-AT-096** — Participant lists are not ranked by hidden culprit relevance.
- **VIC-AT-097** — No offender identity before exact lowercase bingo.
- **VIC-AT-098** — Case/uppercase/punctuation/extra-word variants do not trigger reveal.
- **VIC-AT-099** — Reports, notifications, exports and visuals enforce reveal gate.
- **VIC-AT-100** — Access denial does not confirm/deny protected role.
- **VIC-AT-101** — Untrusted source text cannot override canon or reveal rules.
- **VIC-AT-102** — Generated summaries distinguish reports, facts, assessments and unknowns.
- **VIC-AT-103** — Query sequences cannot reconstruct protected hidden truth.
- **VIC-AT-104** — Service NPC cannot disclose beyond authorised service knowledge.

### Time, population, security and persistence
- **VIC-AT-105** — No contact/referral/notification/review/NPC action progresses outside simulation.
- **VIC-AT-106** — Resume uses exact persisted state without real-world catch-up.
- **VIC-AT-107** — Newly relevant participant is permanently promoted through BP-03.
- **VIC-AT-108** — Participant is never downgraded after case/role closure.
- **VIC-AT-109** — Admission rejected if it exceeds 10,000 living persons.
- **VIC-AT-110** — Police and multi-role people count once.
- **VIC-AT-111** — Participant role link does not increment population.
- **VIC-AT-112** — Restricted contact/safeguarding data denied without permission.
- **VIC-AT-113** — Search/autocomplete/count/export/notification enforce same restrictions.
- **VIC-AT-114** — Emergency access is reasoned, scoped, time-limited and audited.
- **VIC-AT-115** — Restricted reads/exports are audited.
- **VIC-AT-116** — Concurrent conflicting edits preserve both versions.
- **VIC-AT-117** — Failed transaction leaves no incomplete participant/case/person link.
- **VIC-AT-118** — Retry does not duplicate referral or contact event.
- **VIC-AT-119** — Restore preserves IDs, episodes, source versions, preferences and audit.
- **VIC-AT-120** — Storage compaction preserves meaning, uncertainty, chronology and provenance.
- **VIC-AT-121** — Large lists paginate without silently omitting authorised records.
- **VIC-AT-122** — Source correction creates traceable update without rewriting prior decisions.
- **VIC-AT-123** — Report identifies author, as-of time, scope, source versions and limitations.
- **VIC-AT-124** — Optional visual traces to canonical records and respects permissions.
- **VIC-AT-125** — No test is marked passed without reproducible BP-43 evidence.

## 25. Traceability to the original 52-division source

The source JSON remains unchanged. IDs use 1-based requirement/test array positions and the crosswalk's JSON-pointer convention.

| Source ID | Original source area | BP-17 incorporation |
|---|---|---|
| S03.R01–R05 / S03.T01–T03 | Population accounting | BP-03 owns cap and unique-person ledger; role links never double-count. |
| S04.R01–R03 / S04.T01–T02 | Person identity/life records | BP-03 owns identity and permanent full-detail promotion. |
| S05.R01–R03 / S05.T01 | Households/relationships | BP-36 owns relationship semantics; BP-17 references relevant links. |
| S13.R01–R03 / S13.T01 | Healthcare/public health | Provider, emergency care, medical liaison, capacity and sensitive access interfaces. |
| S15.R01–R03 / S15.T01 | Social care/welfare | Safeguarding, housing, disability, youth/elder/community support and referral lifecycle. |
| S27.R01–R02 | Call-taking/CAD | Caller-to-participant linkage; BP-11/BP-12 retain original source authority. |
| S29.R01–R03 | Incidents and occurrences | Participant links distinct from incident, classification and hidden occurrence truth. |
| S31.R01–R03 / S31.T01 | Victims/witnesses/suspects | Role-specific links, contact, vulnerability, risk, statements, availability and procedural status; allegation/suspicion/evidence/charge/finding distinct; no guilt from role. |
| S34.R01–R03 / S34.T01 | Interviews/statements | BP-19 owns process and original content; participant association and no-leading-prompt rules retained. |
| S43.R01–R05 / S43.T01–T02 | AI/player agency | Plausible NPC knowledge, hidden-truth firewall, exact bingo trigger, no unsolicited hints, structured events. |
| S45.R01–R03 / S45.T01 | Visuals | Optional participant timelines/referral views trace to canonical data; text authoritative. |
| S48.R01–R03 / S48.T01 | Security | Least privilege, restricted participant data, hidden truth, access audit and no credentials in records/logs. |
| S50.R01–R03 / S50.T01 | Testing/quality | 125 acceptance criteria; evidence-based test gate. |
| S52.R01–R04 / S52.T01 | Canon/change control | BP-44 owns amendments; approval/implementation/test/verification remain distinct. |

BP-17 applies all X01–X10 cross-cutting rules: stable identity/provenance; single source of truth; effective-dated facts; reconciliation; fact/allegation/estimate/inference/intelligence/opinion distinctions; source preservation; no hidden time; text-first operation; proportionate non-police depth; evidence-based completion.

## 26. Open decisions

These remain open; this draft does not invent approval:
1. Final participant-role catalogue and display labels.
2. Role/status transition approval matrix.
3. Whether victim liaison is a distinct position or existing unit responsibility.
4. Risk vocabulary and whether scoring is permitted; narrative basis remains mandatory.
5. Safeguarding urgency levels and notification authority.
6. Provider catalogue, eligibility, capacity and referral response windows.
7. Consent/authority categories and expiry/review rules with BP-27/BP-30/BP-42.
8. Participant update frequency/templates with BP-27/BP-41.
9. Anonymous/confidential identity architecture and access matrix with BP-38/BP-42.
10. Retention/legal-hold policy with BP-38/BP-44.
11. Whether availability calendars live in BP-17 or BP-37; BP-17 owns participant-declared constraints.
12. Exact command syntax/layout with BP-40.
13. NPC autonomy and permitted participant-contact actions with BP-35/BP-42.
14. Emergency access roles/review with BP-42.
15. Identifier prefixes/display formats with BP-38.

### Risks and mitigations

| Risk | Mitigation |
|---|---|
| Role mistaken for guilt/credibility | Explicit distinctions, source basis and negative tests |
| Duplicate identity across cases | BP-03 sole identity owner and idempotent links |
| Contact/safe address leak | Field-level restrictions across every output |
| Victim/witness and suspect roles collapse | Independent BP-17/BP-18 domains |
| Summary replaces original account | Immutable source links and versioned summaries |
| Referral treated as proof | Referral lifecycle separate from evidential assessment |
| Vulnerability becomes permanent label | Contextual, time-bounded sourced assessment |
| NPC omniscience | Knowledge provenance and authorised handoffs |
| System directs investigation | No automatic lead creation/ranking or unsolicited hints |
| Hidden truth leaks through metadata | Exact bingo gate and BP-42 output checks |
| Paused game processes actions | BP-35/BP-37 freeze invariant |
| Population cap bypass | BP-03 single ledger; role links do not create people |
| Compression removes meaning | Lossless semantic preservation |

## 27. Design completion checklist

Before DESIGNED status:
- [ ] Every applicable source requirement/test incorporated or assigned to owner.
- [ ] BP-03 remains sole identity/population owner.
- [ ] Role episodes support simultaneous, successive and cross-case roles.
- [ ] Victim/witness labels do not imply guilt, credibility, offence proof or evidential weight.
- [ ] Allegation, statement, intelligence, evidence, inference, charge and finding remain distinct.
- [ ] Contact, safe-contact, availability and update preferences have provenance/scope.
- [ ] Needs, risk and safeguarding are sourced, contextual and time-bounded.
- [ ] Referral states distinguish delivery, acknowledgement, acceptance, partial and full fulfilment.
- [ ] BP-04/BP-30 service ownership is explicit and proportionate.
- [ ] BP-15/BP-16/BP-18/BP-19/BP-23/BP-24/BP-27/BP-28 interfaces are explicit.
- [ ] Confidentiality and hidden-truth restrictions cover all access/output paths.
- [ ] Exact bingo gate and no unsolicited hints preserved.
- [ ] Pause/resume covers all scheduled participant/service actions.
- [ ] Population cap and permanent promotion enforced by BP-03.
- [ ] Changes are attributable, versioned and auditable.
- [ ] All 125 tests are traceable and later receive BP-43 evidence.
- [ ] Open decisions resolved or explicitly retained for approved configuration.
- [ ] No Neon write, migration, seed or import has been performed or authorised.

## 28. Status and next dependencies

This is a full division design draft, not user-approved design or implementation evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-18 — Suspects and Offenders**. It must own suspect/offender role and status semantics without collapsing allegation, suspicion, charge, finding or conviction, and must preserve BP-17's independent victim/witness records.
