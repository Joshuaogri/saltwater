# BP-26 — Custody Management

**Project:** Saltwater — fictional sovereign city-state, one city, one jurisdiction  
**Blueprint division:** BP-26 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test execution:** NOT_STARTED | **Verification:** NOT_STARTED  
**Authority:** Fixed BP-01–BP-44 structure and unchanged 52-division source. No canon or division structure is changed.

## 1. Purpose

BP-26 defines the complete, persistent and auditable custody lifecycle after a person is physically arrested or otherwise lawfully received into police custody under Saltwater's fictional rules. It covers pre-arrival coordination, handover acceptance, booking, identity verification, detention status, custody clock, welfare, risk and safeguarding, healthcare access, interviews/visits interfaces, property held in custody, reviews, transfer, release, refusal/rejection, death or emergency, record closure and continuity with courts and corrections.

BP-26 owns the authoritative police-custody record from custody handover acceptance until formal release or transfer out of police custody. BP-25 owns arrest, warrant, search and seizure operational authority and execution. BP-23 owns evidential exhibit continuity. BP-27 owns charging and prosecution processes; BP-28 owns court orders and findings; BP-29 owns sentence execution and post-sentence supervision. BP-03 owns the canonical person identity and population ledger. BP-26 must never collapse these boundaries.

## 2. Scope and exclusions

In scope: custody intake and handover acceptance; booking; identity and property reconciliation; custody record; detention status and custody clock; detention authority and limits as configured fictional rules; risk assessment and review; welfare and basic needs; medical attention and healthcare referrals; observation and safeguarding; detainee communication and visits; legal/interpreter/support access interfaces as configured; interviews and transfers to BP-19; custody searches and property handling where authorised; incidents, injuries, complaints and use-of-force interfaces; cell/holding capacity and allocation; movement and escorts; release, bail interface, transfer to another authority, court attendance, hospital transfer, death/emergency closure; audit, disclosure and historical continuity.

Out of scope: arrest grounds/execution/warrants/search authority (BP-25); exhibit identity and chain of custody (BP-23); investigative strategy (BP-16); interview content and statement versions (BP-19); charging/prosecution/disclosure decisions (BP-27); court orders/verdicts/sentencing (BP-28); prison/community sentence execution (BP-29); person identity registry (BP-03); healthcare system depth (BP-04/BP-13); global clock (BP-37); database/persistence/security foundations (BP-38/BP-39/BP-42).

## 3. Core distinctions and lifecycle boundaries

Distinguish physically arrested, offered for custody, arrived at custody facility, handover pending, accepted into custody, booked, detained, released, transferred, hospitalised under an explicit custody arrangement, escaped/missing, deceased and record administratively closed. Physical arrival does not equal acceptance; acceptance does not equal booking completion; booking does not validate the preceding arrest; detention does not imply charge; charge does not imply guilt; release does not imply acquittal.

The custody record tracks the person's actual status, responsible authority and location at every point. No interval may leave the person without an identified responsible actor/agency and known or explicitly unknown location. BP-26 may record disputed or defective authority but does not retroactively validate an arrest.

## 4. Fictional custody authority and policy configuration

Custody authority, eligible receiving officers, detention grounds, maximum periods, review intervals, authorisation roles, safeguards, rights/notice content, search powers, observation standards, medical escalation, communication/visit rules, transfer powers and release routes are configurable fictional canon. Each rule has stable ID/version, effective dates, issuing authority, scope, approval, source and supersession history.

No real-world legal regime is silently imported. Unresolved policy must remain explicitly open and configurable; the system must not invent a detention period, reviewer, legal right, search power or release condition. If a required authority or safeguard rule is missing, the system records the gap and blocks or defers the affected transition according to an explicit fail-safe.

## 5. Custody facility, capacity and resource model

Facilities, custody suites, holding areas, cells, interview rooms, medical spaces, secure property stores and access points reference canonical BP-04/BP-02 locations and BP-09 assets. Each facility records operational status, authorised capacity, usable capacity, cell/space type, accessibility, safety constraints, staffing, equipment, service outages and restrictions.

Capacity is checked atomically before acceptance and each move. Distinguish nominal capacity from currently usable capacity; unavailable cells, staffing shortage, segregation/safeguarding constraints, maintenance and emergency closures reduce effective capacity. A capacity conflict cannot be resolved by silently overfilling a cell or inventing a location. The system supports custody at a hospital or other configured location only with explicit authority, responsible custodian and handover records.

## 6. Pre-arrival coordination and custody offer

BP-25 or another authorised source offers a person for custody with arrest/action reference, person identity and confidence, authority and source version, event chronology, arresting officers, circumstances, risk and vulnerability information, injuries/medical concerns, force events, property list, exhibits already transferred, requested destination, transport and known safeguards. The offer is a handover proposal, not acceptance.

Custody staff can acknowledge, request clarification, redirect to another authorised facility, refuse with reasons, or accept. Every decision identifies receiving decision-maker, authority, time, capacity check, information considered and outstanding issues. No acceptance may be inferred from vehicle arrival, radio acknowledgement or a booking screen being opened.

## 7. Arrival and handover acceptance

Record facility arrival, time, location, escorting officers, receiving officer, person identity check, authority documents, arrest time, stated grounds, relevant conditions, risk/medical/safeguard information, force/injury details, property reconciliation, communication needs and discrepancies. Handover states include pending, accepted, accepted with recorded discrepancy, rejected, redirected, interrupted and emergency exception as configured.

Acceptance transfers custody responsibility to the receiving authority at a specific canonical time. If rejected, responsibility remains explicitly with the prior custodian until a valid alternative handover occurs. A discrepancy must be recorded and referred; staff cannot silently correct the source record. Acceptance does not determine legality, admissibility or guilt.

## 8. Booking and custody record creation

A booking creates one authoritative custody episode ID linked to the canonical BP-03 person, originating arrest/authority event, incident and case where available. Record booking officer, receiving officer, facility, cell/holding location, accepted time, booking completion time, legal/fictional basis, stated reason, identity confidence, known aliases, photographs/identifiers where configured, language/accessibility needs, risk, welfare, property and associated documents.

Booking is a structured event sequence, not a single status flag. Required fields are defined by versioned fictional policy. Unknown, unavailable, disputed and not-applicable values remain distinct. Duplicate booking attempts must be idempotent or explicitly linked as correction/rebooking; they must not create a second person or concurrent custody episode without a documented transfer/re-arrest basis.

## 9. Identity, verification and correction

Custody identity checks use BP-03 canonical identity and source evidence. Record identifiers checked, source, person response, confidence, discrepancies, aliases, mistaken identity concerns and verification actor/time. Similar names, aliases, false documents, unknown identity, minors or vulnerable persons (where configured) require explicit uncertainty and policy-driven handling.

Identity correction appends a linked correction with actor, authority, reason, source and downstream review requirements. It preserves the identity believed at booking and any actions taken on that belief. A mistaken identity does not disappear from the historical record. A correction must propagate references without merging distinct people or changing the identity of unrelated records.

## 10. Detention authority and custody status

Each custody episode records the precise authority basis, decision-maker, start time, permitted scope, conditions, review points, configured maximum/expiry, restrictions and source version. Status transitions include received, booking in progress, detained, under review, authorised extension/continuation where configured, transferred, released, escaped/missing, deceased and closed. Additional local statuses must be versioned and cannot contradict the core lifecycle.

The custody clock begins at the canonical event defined by fictional policy; the system must not assume that arrival, arrest or booking completion is the start without an approved rule. Every clock calculation is derived from BP-37 canonical simulation time and recorded authority. A missing or invalid detention basis triggers an explicit exception and review; the system must not fabricate authority.

## 11. Custody clock, reviews and deadlines

Maintain elapsed custody time, review due times, maximum authorised period and any extension/continuation under configured fictional rules. Store the underlying start event, time basis, rule version, calculations and decisions; derived clock displays are not authoritative independent values. Each review records reviewer, independence/authority, time, information available, detainee condition, grounds, representations, decision, rationale, next review and conditions.

Clock transitions are event-based and historically queryable. Pausing the game pauses the simulation clock and all custody elapsed time, review deadlines, detention limits, scheduled checks and notifications. On resume, there is no wall-clock catch-up. No detainee is released, unlawfully detained by elapsed simulated time, transferred, moved or reviewed off-screen. Time progression occurs only through explicit player-controlled simulation advancement.

## 12. Risk, vulnerability and safeguarding

Record risk assessment as a time-specific assessment, not an immutable person trait. Domains may include self-harm, violence, victimisation, vulnerability, intoxication, withdrawal, disability, age-related needs, communication, mental distress, medical risk, escape risk and risks posed by others, according to approved fictional policy. Each entry records source, confidence, observations, reported information, assessor, time, rationale, protective actions and review trigger.

Separate known fact, self-report, third-party report, intelligence, professional opinion and uncertainty. Risk flags are not proof of conduct or guilt. Safeguarding measures include separation, accessible accommodation, additional observation, support person, healthcare referral and escalation only where configured. Avoid discriminatory inference from identity or protected characteristics. Risk can increase, decrease, be disputed or be reassessed; prior assessments remain preserved.

## 13. Welfare and humane custody conditions

Track welfare checks and provision of basic needs at policy-defined intervals: water, food, rest, sanitation, temperature, clothing, hygiene, accessibility, medication access through authorised healthcare pathways, communication, religious/cultural accommodation only where relevant and user-established canon permits, and protection from harm. Each check records time, staff member, observation, detainee request/response, action, refusal, inability, reason and follow-up.

A scheduled check is not marked complete without a recorded observation or an explicit failed/unavailable outcome. Missed or late checks generate an incident/escalation record. Welfare data is time-dependent and must not be represented as continuous observation when only periodic checks occurred. Cell condition and facility outages can affect welfare and must be linked to BP-04/BP-09 service records.

## 14. Healthcare, injury and emergency response

Custody staff record reported symptoms, visible injuries, distress, medication information voluntarily or lawfully provided, medical requests, observations and emergency events without making unsupported diagnoses. Referral to a clinic/hospital/practitioner uses BP-04 healthcare providers and BP-13 medical service interfaces at proportionate depth. Record request, triage/response, provider, appointment/attendance, treatment event reference, transfer, escort, return and outstanding instructions.

Medical opinion belongs to qualified fictional healthcare actors, not police custody staff. Medical records are sensitive and role-restricted under BP-42. Emergency escalation, ambulance response and hospital transfer are separate events with time, authority, receiving provider, escort/custody responsibility and location. Refusal or inability to access care is documented and escalated. Injury records link to BP-25 force/arrest events or other incidents without assuming cause.

## 15. Observation, supervision and custody staffing

Define observation levels and required frequency through versioned fictional policy. Record assigned staff, responsible supervisor, location, actual observation times, method, findings, welfare concerns, missed checks, escalation and handover between shifts. Staffing/competence and duty status are checked against BP-06/BP-08/BP-33; resource/equipment availability against BP-09.

A rota or assignment is not evidence that an observation occurred. Staff absence, simultaneous duties, equipment outage and facility blind spots are represented. The system must not generate false checks or imply continuous observation from periodic records. High-risk events may trigger review or additional safeguards, but no risk score alone determines guilt or release.

## 16. Detainee communication, visits and support

Track requests and outcomes for communication, notification, visits, support persons, legal representative access, interpreter and other assistance as fictional policy requires. Each request records requester, intended recipient, authority, time, scope, scheduling, privacy/security conditions, approval/refusal, reason, attempt, completion, content metadata and any resulting action. Do not fabricate message content or assume a notification was received because it was sent.

Communication records are not interview statements. BP-19 owns formal investigative interviews, questions, answers and statement versions. BP-27 owns prosecution/legal disclosure. BP-26 records access logistics, custody safety, requests and completion. Restricted or privileged communications must not be exposed to investigators unless an explicit fictional authority permits access.

## 17. Interviews and investigative access

An interview request references BP-19 interview record, case, requesting officer, authority, time, location, safeguards, legal/support access and custody availability. BP-26 checks custody status, welfare, suitability, room/resource and configured safeguards; BP-19 owns interview planning, conduct, recording, transcript and statements.

Custody staff do not decide interview content, infer guilt from silence/refusal or create statements. Interview breaks, medical interruption, return to cell and changes in welfare are reflected in custody chronology. An interview request does not extend detention authority. Any detention clock/review interaction follows explicit fictional rules and remains independently recorded.

## 18. Searches, property and personal effects in custody

Any custody search is separately authorised under a configured fictional rule, recorded with purpose, scope, actor, time, method, safeguards and outcome. BP-26 does not inherit BP-25 search authority merely because a person is in custody. Distinguish search for safety, identity, property inventory, evidential purposes and other configured purposes; each has its own authority and handling rules.

Personal property received with a detainee is recorded by item, quantity, condition, owner/possessor, seal/package, officer, time, storage location, receipt and return/transfer/disposal outcome. Property held for safekeeping is distinct from seized property and evidential exhibits. BP-23 retains ownership of exhibits and evidential continuity; BP-26 references but does not reclassify, open, test or dispose of an exhibit. Property discrepancies, damage or unauthorised access trigger review.

## 19. Cell allocation, movement and separation

Every cell/holding allocation records facility, cell, start/end, occupants, authorised capacity, compatibility/safeguarding rationale, responsible staff and actual moves. Movement records origin, destination, time, escort, reason, authority, status, property and welfare handover. Separation and shared accommodation decisions follow configured fictional policy and documented risk/needs; do not infer compatibility from demographic similarity or case association.

Capacity is checked atomically. No overlapping incompatible occupancy or impossible simultaneous location. A cell closure, emergency evacuation or facility outage creates explicit relocation events. A detainee cannot be in two places at once except where a clearly recorded transfer interval models uncertainty; no silent teleportation.

## 20. Visits, transfers and external attendance

A transfer or escorted attendance identifies purpose, authority, origin/destination, receiving authority, escort, transport, departure/arrival, custody responsibility, property, medical/safeguard information, status and acceptance. Destinations may include court, hospital, another police facility or another configured authority within the fictional world. Off-map services may be represented as external dependencies but never create additional playable cities or territory.

A departure is not a completed transfer until receiving acceptance is recorded or the configured custody responsibility remains explicitly assigned. Court attendance links to BP-28 schedule/order; hospital care links to healthcare records; transfer to prison/sentence execution belongs to BP-29 after the relevant court authority. Every movement is effective-dated and location-consistent.

## 21. Release, bail interface and discharge

Release outcomes include unconditional release, release subject to configured conditions, bail-related interface, transfer to another authority, court-directed release, release after detention authority ends, mistaken identity release, medical transfer with custody arrangement, and other explicitly configured routes. BP-26 records operational release/discharge from police custody; BP-27 owns charge/prosecution and bail legal process; BP-28 owns court orders.

A release decision references authority, decision-maker, effective time, conditions supplied by authorised source, property return, medication/medical needs, safeguarding, destination/transport, notifications, person acknowledgement or inability, and final custody status. Do not invent bail conditions or infer release from a case closure. A release does not erase the custody record or determine guilt/innocence.

## 22. Transfer to prison or corrections

When a court sentence or other authorised direction requires transfer to a correctional setting, BP-26 records the handover from police custody and acceptance by the receiving correctional authority. BP-28 is the source of court sentence/order; BP-29 owns sentence execution, prison/community supervision, rehabilitation, release and recall. BP-26 must not start, modify or close a sentence.

Record order/version, person identity, property, health/safeguard information, escort, departure/arrival, receiving officer, acceptance and discrepancy. If the transfer is rejected or delayed, retain an explicit custody status and responsible authority; do not assume prison acceptance.

## 23. Escape, missing person, death and serious incident

Support escape/attempted escape, missing person, injury, self-harm concern, violence, assault, fire, infrastructure failure, medical emergency, death in custody, property loss, complaint and other serious events. Record discovery time, last confirmed observation/location, reporting actor, persons involved, response, emergency services, scene/evidence preservation interfaces, notifications, command, investigation referral and status. Unknown facts remain unknown.

Death in custody triggers preservation of the custody timeline, medical and observation records, access logs, CCTV, communications, property and associated evidence. BP-12 manages incident response; BP-23 manages exhibits; BP-24 forensic examination; BP-30/BP-31 oversight and standards; BP-40 external review as configured. No record is altered to imply a cause before it is established by authorised process.

## 24. Complaints, representations and review

Record complaints, requests, representations, alleged mistreatment, property disputes, access refusals, welfare concerns and challenges to custody authority. Preserve exact source content where available and distinguish verbatim record from summary. Identify recipient, time, route, urgency, confidentiality, referral, response and outcome/pending reason.

BP-26 owns custody-side intake and factual records; BP-31 owns professional standards/complaints investigation; BP-30 owns command governance; BP-27/BP-28 own legal processes and judicial decisions. The subject of a complaint must not control its review. Findings and remedies do not rewrite original custody events.

## 25. Shift handover and continuity

A custody shift handover lists every detainee, location, legal/fictional authority, custody clock, next review, risk and welfare needs, medical requests, property status, interviews/visits scheduled, transfers pending, incidents, safeguards and unresolved actions. Outgoing and incoming staff, supervisor, canonical time, acknowledgement and discrepancies are recorded.

Handover does not reset custody time, risk, observation intervals or review deadlines. Missing information is explicitly marked and escalated. A staff member cannot be recorded as having received responsibility without a defined acceptance event. Staffing and assignment changes preserve historical responsibility.

## 26. Records, disclosure and privacy

Maintain authoritative custody episode, booking, handover, authority, clock, review, risk, welfare, medical referral, observation, communication, visit, interview access, search, property, cell allocation, movement, incident, complaint, release and transfer records. Each has stable ID, source, actor, time, authority, version and links. BP-38 owns schema/IDs; BP-39 persistence/recovery; BP-42 access control and security.

Sensitive medical, safeguarding, legal communication, identity and intelligence details require least-privilege access. Disclosure/export records exact versions, recipient, purpose, authority, redactions and time. Custody summaries are derived views and never replace source records. Corrections append linked records and preserve prior values.

## 27. NPC knowledge and hidden-truth firewall

Custody officers, healthcare actors, escorts and detainees know only what they observed, were told or lawfully accessed. Being detained does not make a person know the case truth. A custody record, risk flag, interview request, charge or transfer must not expose hidden offender/accomplice identity.

No booking screen, custody log, NPC dialogue, medical referral, notification, AI summary, error, report or test may reveal hidden culprit identity. Only the player typing exactly bingo permits the reveal. Do not provide unsolicited investigative hints or tell the player what to investigate next. Custody procedures must remain neutral as to guilt.

## 28. Player agency and operational simulation

The player controls their officer's decisions and actions. BP-26 presents records, custody status, requests, facility capacity, safeguards and outcomes; it does not force the player into a particular arrest, charge, interview, release or investigative path. NPC custody actions require role, authority, knowledge, capacity and an explicit in-world trigger.

Autonomous NPCs may perform only configured custody tasks while simulation time is actively advanced. No off-screen progression, silent detention expiry, automatic release or hidden punitive outcome occurs while paused. Failure, delay, disagreement and uncertainty are valid simulated outcomes.

## 29. Time, pause and event ordering

BP-37 owns the sole clock. All custody events, detention durations, review deadlines, observation intervals, visits, meals, medical appointments, shift handovers, movements and release conditions use canonical simulation time. No simulation time advances while the player is outside the game; all dependent events freeze. Resume never applies wall-clock catch-up. Events are ordered deterministically where feasible, with stable tie-breakers and explicit causal references.

## 30. Population and canonical identity

Every detainee is one BP-03 person and counted once in the 10,000 living-person cap. Custody status, location, transfer, release or death does not create another person. Anyone materially connected to a police activity or case is promoted to full persistent simulation and never downgraded. Promotion cannot bypass the population cap. Multiple custody episodes over time remain linked to one person, with no overlapping episode unless a defined transfer or correction explains it.

## 31. Inputs, outputs and event contracts

Inputs: BP-03 person; BP-04 facility/healthcare/service context; BP-05 authority; BP-06 personnel; BP-08 deployment; BP-09 assets; BP-12 incidents; BP-15 cases; BP-17 victim/witness context where relevant; BP-18 suspect status; BP-19 interview request; BP-23 evidence references; BP-25 arrest and handover offer; BP-27 legal-process directions; BP-28 court orders; BP-29 corrections acceptance; BP-30 command; BP-31 standards; BP-33 workforce; BP-35 engine; BP-37 time; BP-38 records; BP-39 persistence; BP-42 permissions.

Outputs: custody offer decisions; handover acceptance/rejection; booking and custody episode; detention authority and clock; reviews; risk/welfare/observation events; healthcare referrals and transfers; communication/visit access records; interview availability/access; personal property inventory; cell allocations and movements; incident/complaint records; release/transfer handovers; disclosure-ready custody records; audit events.

Events include custody_offered/acknowledged/accepted/rejected/redirected; arrived/booked/identity_verified; detention_started/authority_reviewed/continued/ended; custody_review_due/completed; risk_assessed/updated; welfare_check_completed/missed; medical_request/referred/attended/transferred; communication_requested/sent/received; visit_requested/approved/refused/completed; interview_access_requested/approved/declined/started/ended; property_received/stored/transferred/returned/disputed; cell_allocated/moved; custody_shift_handover; transfer_departed/arrived/accepted/rejected; release_authorised/completed; escape/missing/serious_incident/death_reported; complaint_received/referred/resolved. Each event has stable ID, actor, authority, canonical time, source, prior/new state, outcome, idempotency key and schema version.

## 32. Failure modes and edge cases

Identity mismatch; no valid detention authority; arrest authority disputed; custody facility full; no safe/accessible cell; staffing shortage; receiving officer unavailable; incomplete handover; contradictory property inventory; injury not disclosed; medical emergency; interpreter unavailable; risk changes; missed welfare check; observation equipment outage; cell unsafe; incompatible co-location; transfer vehicle failure; receiving authority refuses; hospital cannot accept; detainee refuses property receipt; property lost/damaged; exhibit confused with personal property; duplicate booking; overlapping custody episode; clock start ambiguous; review deadline during pause; attempted wall-clock expiry; release condition unavailable; mistaken identity; death/escape; complaint against reviewer; restricted medical record accessed; corrupted/replayed event. Each remains explicit, attributable and historically preserved; never fabricate completion, acceptance, authority, care or release.

## 33. Dependencies and ownership boundaries

BP-03 identity/population; BP-04 city facilities and healthcare provider registry; BP-05 mandate; BP-06 personnel; BP-08 deployment; BP-09 resources; BP-12 incidents; BP-15 case lifecycle; BP-16 investigation; BP-17 victim/witness; BP-18 suspect/offender roles; BP-19 interviews; BP-23 evidence custody; BP-25 arrest/warrant/search/seizure; BP-27 legal process; BP-28 court orders; BP-29 corrections; BP-30 governance; BP-31 professional standards; BP-33 workforce; BP-35 engine; BP-37 time; BP-38 records; BP-39 persistence; BP-42 security. BP-26 owns police-custody lifecycle and handovers only; it must not overwrite another division's authoritative facts.

## 34. Acceptance tests

These are specification acceptance criteria, not executed results. BP-43 owns test execution and reproducible evidence.

- **CUSTODY-AT-001** — Every custody episode has a stable unique ID.
- **CUSTODY-AT-002** — Every booking event has a stable unique ID.
- **CUSTODY-AT-003** — Every custody handover offer has a stable unique ID.
- **CUSTODY-AT-004** — Every handover acceptance/rejection has a stable unique ID.
- **CUSTODY-AT-005** — Every detention authority has a stable ID and version.
- **CUSTODY-AT-006** — Every custody review has a stable unique ID.
- **CUSTODY-AT-007** — Every cell allocation and movement has a stable event ID.
- **CUSTODY-AT-008** — Every release/transfer has a stable unique ID.
- **CUSTODY-AT-009** — A physical arrest is distinct from custody acceptance.
- **CUSTODY-AT-010** — Arrival at a facility does not automatically constitute custody acceptance.
- **CUSTODY-AT-011** — Radio acknowledgement does not constitute custody acceptance.
- **CUSTODY-AT-012** — Opening a booking screen does not constitute custody acceptance.
- **CUSTODY-AT-013** — Custody acceptance records the exact transfer of responsibility.
- **CUSTODY-AT-014** — A rejected handover preserves prior custodian responsibility.
- **CUSTODY-AT-015** — A redirected handover records destination and reason.
- **CUSTODY-AT-016** — A handover may be accepted with a documented discrepancy.
- **CUSTODY-AT-017** — Acceptance does not validate arrest legality.
- **CUSTODY-AT-018** — Acceptance does not establish guilt or charge.
- **CUSTODY-AT-019** — A custody episode links to one canonical BP-03 person.
- **CUSTODY-AT-020** — Booking records originating arrest/action reference.
- **CUSTODY-AT-021** — Booking records receiving officer and booking officer.
- **CUSTODY-AT-022** — Booking records facility and actual location.
- **CUSTODY-AT-023** — Booking records canonical arrival and acceptance times.
- **CUSTODY-AT-024** — Unknown booking fields remain explicitly unknown.
- **CUSTODY-AT-025** — Unavailable information is not fabricated.
- **CUSTODY-AT-026** — A duplicate booking request does not create a duplicate person.
- **CUSTODY-AT-027** — Rebooking requires explicit correction or new lawful episode basis.
- **CUSTODY-AT-028** — Multiple custody episodes remain linked to one person.
- **CUSTODY-AT-029** — Identity verification records source and identifiers checked.
- **CUSTODY-AT-030** — Identity confidence and discrepancies are preserved.
- **CUSTODY-AT-031** — Similar names do not merge distinct people.
- **CUSTODY-AT-032** — Aliases remain linked without overwriting canonical identity.
- **CUSTODY-AT-033** — Mistaken identity can be represented and corrected.
- **CUSTODY-AT-034** — Identity correction preserves the original belief and actions.
- **CUSTODY-AT-035** — Correction records actor, authority, reason and time.
- **CUSTODY-AT-036** — Identity correction triggers review of dependent records.
- **CUSTODY-AT-037** — Custody authority identifies exact fictional rule and version.
- **CUSTODY-AT-038** — Custody authority records authorised decision-maker.
- **CUSTODY-AT-039** — Custody authority records effective start time.
- **CUSTODY-AT-040** — Custody authority records scope and conditions.
- **CUSTODY-AT-041** — No real-world detention period is silently imported.
- **CUSTODY-AT-042** — An unresolved detention rule is not invented.
- **CUSTODY-AT-043** — Missing authority triggers explicit exception handling.
- **CUSTODY-AT-044** — Detention status distinguishes received, booking, detained, review, transfer and release.
- **CUSTODY-AT-045** — Detention status distinguishes escaped/missing and deceased outcomes.
- **CUSTODY-AT-046** — Detention does not imply charge.
- **CUSTODY-AT-047** — Charge does not imply guilt.
- **CUSTODY-AT-048** — Booking does not validate the arrest.
- **CUSTODY-AT-049** — Custody clock start follows configured fictional rule.
- **CUSTODY-AT-050** — Custody clock references canonical BP-37 time.
- **CUSTODY-AT-051** — Custody clock stores source event and rule version.
- **CUSTODY-AT-052** — Elapsed custody time is derived from authoritative events.
- **CUSTODY-AT-053** — Review due times derive from configured rules.
- **CUSTODY-AT-054** — Review records reviewer identity and authority.
- **CUSTODY-AT-055** — Review records information available at decision time.
- **CUSTODY-AT-056** — Review records detainee condition and representations.
- **CUSTODY-AT-057** — Review records decision, rationale and next review.
- **CUSTODY-AT-058** — A review does not silently extend detention without authority.
- **CUSTODY-AT-059** — A review does not overwrite prior reviews.
- **CUSTODY-AT-060** — A custody clock cannot advance on wall-clock time while paused.
- **CUSTODY-AT-061** — No detention limit expires while the player is absent.
- **CUSTODY-AT-062** — No review deadline passes while the player is absent.
- **CUSTODY-AT-063** — No release occurs automatically while paused.
- **CUSTODY-AT-064** — Resume does not apply elapsed wall-clock time.
- **CUSTODY-AT-065** — All custody events are historically queryable.
- **CUSTODY-AT-066** — Risk assessments are time-specific records.
- **CUSTODY-AT-067** — Risk records source, confidence and assessor.
- **CUSTODY-AT-068** — Self-report is distinct from observed fact.
- **CUSTODY-AT-069** — Third-party report is distinct from professional opinion.
- **CUSTODY-AT-070** — Risk flags do not establish guilt.
- **CUSTODY-AT-071** — Risk may be disputed or reassessed without erasing prior versions.
- **CUSTODY-AT-072** — Risk assessment records protective actions and review trigger.
- **CUSTODY-AT-073** — Safeguarding measures require configured authority and rationale.
- **CUSTODY-AT-074** — Vulnerability is not inferred solely from identity or protected traits.
- **CUSTODY-AT-075** — Welfare checks record actual observation time.
- **CUSTODY-AT-076** — A scheduled check is not marked complete without evidence.
- **CUSTODY-AT-077** — Missed checks have explicit missed/unavailable status.
- **CUSTODY-AT-078** — Late checks preserve actual time and reason.
- **CUSTODY-AT-079** — Welfare records water/food/rest/sanitation provision where configured.
- **CUSTODY-AT-080** — Welfare records detainee requests and responses.
- **CUSTODY-AT-081** — Welfare records refusal without treating it as misconduct automatically.
- **CUSTODY-AT-082** — Periodic checks are not misrepresented as continuous observation.
- **CUSTODY-AT-083** — Cell condition and service outages can affect welfare records.
- **CUSTODY-AT-084** — Medical requests are recorded with time and source.
- **CUSTODY-AT-085** — Police staff do not create unsupported medical diagnoses.
- **CUSTODY-AT-086** — Medical opinion is attributed to an authorised healthcare actor.
- **CUSTODY-AT-087** — Healthcare referrals link to a canonical provider.
- **CUSTODY-AT-088** — Medical attendance/treatment is recorded as a separate event.
- **CUSTODY-AT-089** — Medical information is protected by role-based access.
- **CUSTODY-AT-090** — Emergency medical transfer records escort and custody responsibility.
- **CUSTODY-AT-091** — Refusal or inability to access care is documented and escalated.
- **CUSTODY-AT-092** — Injury records do not assume cause.
- **CUSTODY-AT-093** — Force/arrest injury links to BP-25 without rewriting BP-25 events.
- **CUSTODY-AT-094** — Observation levels follow versioned fictional policy.
- **CUSTODY-AT-095** — Observation assignments identify responsible staff.
- **CUSTODY-AT-096** — A roster assignment is not evidence an observation occurred.
- **CUSTODY-AT-097** — Observation records actual time, method and finding.
- **CUSTODY-AT-098** — Staff absence and incompatible duties are represented.
- **CUSTODY-AT-099** — Equipment outage does not generate false observation.
- **CUSTODY-AT-100** — Shift handover preserves observation and review obligations.
- **CUSTODY-AT-101** — Communication requests record requester and intended recipient.
- **CUSTODY-AT-102** — Sending a notification does not prove receipt.
- **CUSTODY-AT-103** — Communication content is not fabricated.
- **CUSTODY-AT-104** — Visit requests record approval/refusal and reason.
- **CUSTODY-AT-105** — Privileged/restricted communication is not exposed without authority.
- **CUSTODY-AT-106** — Interpreter/support requests and outcomes are recorded.
- **CUSTODY-AT-107** — Custody access logistics are separate from interview content.
- **CUSTODY-AT-108** — BP-19 owns interview questions, answers and statements.
- **CUSTODY-AT-109** — An interview request does not extend detention authority.
- **CUSTODY-AT-110** — Interview interruption is reflected in custody chronology.
- **CUSTODY-AT-111** — Custody search requires its own configured authority.
- **CUSTODY-AT-112** — BP-25 arrest/search authority is not automatically inherited.
- **CUSTODY-AT-113** — Search purpose and scope are explicitly recorded.
- **CUSTODY-AT-114** — Personal property is distinct from seized property.
- **CUSTODY-AT-115** — Safekeeping property is distinct from evidential exhibit.
- **CUSTODY-AT-116** — BP-23 remains authoritative for exhibits and continuity.
- **CUSTODY-AT-117** — Custody staff cannot silently reclassify exhibits as personal property.
- **CUSTODY-AT-118** — Property inventory records item, quantity and condition where known.
- **CUSTODY-AT-119** — Unknown property quantity remains explicitly unknown.
- **CUSTODY-AT-120** — Property storage location and custodian are recorded.
- **CUSTODY-AT-121** — Property return records recipient and outcome.
- **CUSTODY-AT-122** — Property discrepancy or damage triggers review.
- **CUSTODY-AT-123** — Cell capacity is checked atomically before allocation.
- **CUSTODY-AT-124** — Unavailable cells reduce usable capacity.
- **CUSTODY-AT-125** — Nominal capacity is distinct from operational capacity.
- **CUSTODY-AT-126** — No cell is silently overfilled.
- **CUSTODY-AT-127** — Cell allocation records start/end and occupants.
- **CUSTODY-AT-128** — Incompatible co-location is blocked or explicitly authorised under policy.
- **CUSTODY-AT-129** — Movement records origin, destination, time and escort.
- **CUSTODY-AT-130** — A detainee cannot occupy two cells simultaneously without explicit transition state.
- **CUSTODY-AT-131** — Facility outage creates explicit relocation events.
- **CUSTODY-AT-132** — Transfer records purpose, authority and destination.
- **CUSTODY-AT-133** — Departure alone does not prove receiving acceptance.
- **CUSTODY-AT-134** — Receiving authority acceptance is explicitly recorded.
- **CUSTODY-AT-135** — Rejected transfer retains assigned custody responsibility.
- **CUSTODY-AT-136** — Hospital transfer records provider and custody arrangement.
- **CUSTODY-AT-137** — Court attendance links to BP-28 order/schedule where applicable.
- **CUSTODY-AT-138** — Prison transfer requires the relevant court/corrections interface.
- **CUSTODY-AT-139** — BP-29 owns sentence execution and post-sentence supervision.
- **CUSTODY-AT-140** — BP-26 does not start or alter a sentence.
- **CUSTODY-AT-141** — Release records authority and decision-maker.
- **CUSTODY-AT-142** — Release records effective time and conditions from authorised source.
- **CUSTODY-AT-143** — BP-27 owns prosecution/bail legal process.
- **CUSTODY-AT-144** — BP-28 owns court-directed release orders.
- **CUSTODY-AT-145** — BP-26 records operational discharge from police custody.
- **CUSTODY-AT-146** — Case closure does not automatically release a detainee.
- **CUSTODY-AT-147** — Release does not imply acquittal or innocence.
- **CUSTODY-AT-148** — Release does not erase custody history.
- **CUSTODY-AT-149** — Property return is reconciled before/at discharge as configured.
- **CUSTODY-AT-150** — Medical/safeguarding needs at release are recorded.
- **CUSTODY-AT-151** — Release notification records actual attempt and receipt where known.
- **CUSTODY-AT-152** — Escape/missing event records last confirmed location and time.
- **CUSTODY-AT-153** — Serious incident response links to BP-12.
- **CUSTODY-AT-154** — Death in custody preserves full chronology and source records.
- **CUSTODY-AT-155** — Death cause is not invented or prematurely asserted.
- **CUSTODY-AT-156** — Exhibits from serious incidents use BP-23 custody.
- **CUSTODY-AT-157** — Complaints preserve original source content where available.
- **CUSTODY-AT-158** — The subject of a complaint cannot control its review.
- **CUSTODY-AT-159** — BP-31 owns professional standards investigation.
- **CUSTODY-AT-160** — Shift handover lists every detainee and current location.
- **CUSTODY-AT-161** — Shift handover includes authority, clock and next review.
- **CUSTODY-AT-162** — Shift handover includes risk, welfare and medical needs.
- **CUSTODY-AT-163** — Shift handover includes property and pending transfers.
- **CUSTODY-AT-164** — Handover requires outgoing/incoming staff acknowledgement.
- **CUSTODY-AT-165** — Handover does not reset custody clock or review intervals.
- **CUSTODY-AT-166** — Missing information is marked and escalated.
- **CUSTODY-AT-167** — Custody summaries do not replace source records.
- **CUSTODY-AT-168** — Corrections append linked events and preserve prior values.
- **CUSTODY-AT-169** — Sensitive medical and safeguarding records enforce least privilege.
- **CUSTODY-AT-170** — Disclosure records exact version, recipient, purpose and authority.
- **CUSTODY-AT-171** — NPCs know only what they observed, received or accessed.
- **CUSTODY-AT-172** — Detention does not reveal hidden case truth.
- **CUSTODY-AT-173** — Custody dialogue/logs cannot leak hidden culprit identity.
- **CUSTODY-AT-174** — Only exact player input bingo permits hidden-truth reveal.
- **CUSTODY-AT-175** — No unsolicited investigative hints or next-step instructions are generated.
- **CUSTODY-AT-176** — Custody actions do not force player decisions.
- **CUSTODY-AT-177** — NPC custody actions require role, authority, knowledge and capability.
- **CUSTODY-AT-178** — No autonomous custody event progresses while the game is paused.
- **CUSTODY-AT-179** — BP-37 remains the sole simulation clock.
- **CUSTODY-AT-180** — All custody timestamps use canonical simulation time.
- **CUSTODY-AT-181** — Every event has actor, authority, source and reason.
- **CUSTODY-AT-182** — Every status transition preserves prior and new state.
- **CUSTODY-AT-183** — Idempotent retries do not duplicate booking or handover.
- **CUSTODY-AT-184** — Replay does not duplicate custody episode or release.
- **CUSTODY-AT-185** — Every detainee resolves to one BP-03 identity.
- **CUSTODY-AT-186** — Detainees are counted once within the 10,000 living-person cap.
- **CUSTODY-AT-187** — Case-connected people are permanently promoted to full simulation.
- **CUSTODY-AT-188** — Promotion never downgrades or bypasses the population cap.
- **CUSTODY-AT-189** — Custody facility and healthcare references resolve to canonical entities.
- **CUSTODY-AT-190** — All essential custody workflows are operable in text-only interface.
- **CUSTODY-AT-191** — Optional visuals derive from canonical custody/location records.
- **CUSTODY-AT-192** — No Neon write is authorised by this specification.
- **CUSTODY-AT-193** — All source-mapped requirements and tests are traceable to this division.

## 35. Source traceability

The original 52-division source JSON remains unchanged. Source IDs refer to original source-array positions (1-based).

| Source ID | Original requirement/test | BP-26 coverage |
|---|---|---|
| S13.R01 | Represent hospitals, clinics, practitioners, emergency care, capacity, appointments, treatment events and public-health alerts. | Sections 5, 13 and 28; police custody uses proportionate provider, capacity, referral, appointment/treatment and emergency-care interfaces, not a separate deep healthcare simulation. |
| S37.R01 | Represent grounds, authority, applications, approvals, execution, person/property searches, seizure, transport, booking, detention, welfare, reviews and release. | Sections 3–23 and 29; BP-25 owns grounds, warrants, searches and seizure; BP-26 owns booking, detention, welfare, custody review and release. |
| S37.R02 | Maintain custody clock and property continuity. | Sections 10–11, 17, 25 and 29; BP-26 owns custody clock and personal property while in custody; BP-23 retains exhibit continuity. |
| S37.R03 | Separate operational action from later legal decision. | Sections 3, 4, 21–23 and 29; operational booking/detention/release events remain distinct from BP-27/BP-28 legal decisions. |
| S37.T01 | Custody and warrant events satisfy configured fictional rules and chronological constraints. | CUSTODY-AT-037–063 and CUSTODY-AT-178–180; configured authority, custody clock, review deadlines, pause behaviour and canonical chronology. |
| S39.R02 | Maintain continuity between custody, court and person records. | Sections 3, 21–23, 25 and 28; BP-03 identity, BP-28 court orders and BP-29 corrections are linked without ownership overlap. |

Cross-cutting X03 applies: every time-dependent fact is effective-dated and historically queryable; BP-37 is the sole clock and pause freezes all time-dependent activity. X04 requires capacity and resource changes to reconcile atomically. X05 preserves fact/allegation/intelligence/evidence/opinion/conclusion distinctions. Global constraints include one-city Saltwater, 10,000 living-person cap, permanent promotion of case-connected people, player agency and exact bingo reveal firewall.

## 36. Open decisions and risk register

### Open fictional decisions
1. Exact custody authority sources, eligible receiving officers and acceptance criteria.
2. Detention clock start event, maximum periods, review intervals and extension authority.
3. Custody facility baseline, capacity, cell types, staffing and specialist capability.
4. Identity verification standards and handling of unknown/mistaken identity.
5. Risk assessment domains, observation levels and safeguarding triggers.
6. Welfare check schedule, minimum services and missed-check escalation.
7. Healthcare referral, emergency response and hospital custody arrangements.
8. Communication, visit, legal-support, interpreter and notification rules.
9. Custody search powers and procedures.
10. Personal property inventory, storage, return and disposal rules.
11. Cell allocation, separation and compatibility policy.
12. Transfer, court attendance and corrections handover rules.
13. Release routes, conditions, authority and notification standards.
14. Escape, serious incident, death-in-custody and external review procedures.
15. Retention, disclosure and access policy for sensitive custody records.

### Risk register

| Risk | Mitigation |
|---|---|
| Arrival confused with acceptance | Explicit handover acceptance event |
| Arrest confused with lawful detention | Separate authority and review records |
| Clock advances off-screen | BP-37 hard pause invariant |
| Missed welfare checks hidden | Actual check evidence and explicit missed state |
| Medical details exposed | BP-42 least-privilege controls |
| Custody property confused with exhibits | BP-23/BP-26 ownership separation |
| Cell overcapacity | Atomic capacity constraints |
| Transfer loses responsibility | Acceptance-based handover |
| Release treated as acquittal | Separate custody and court status |
| Hidden truth leaks through custody | Exact bingo firewall and NPC knowledge boundaries |

## 37. Design completion checklist

- [ ] Custody offer, acceptance/rejection and booking specified.
- [ ] Identity verification and correction specified.
- [ ] Fictional detention authority and clock specified.
- [ ] Reviews and deadlines specified.
- [ ] Risk, vulnerability, safeguarding and welfare specified.
- [ ] Healthcare and emergency interfaces specified.
- [ ] Observation and custody staffing specified.
- [ ] Communication, visits and interview access specified.
- [ ] Custody search and personal property specified.
- [ ] Cell capacity, allocation and movement specified.
- [ ] Transfers, release and corrections handover specified.
- [ ] Escape, death and serious incidents specified.
- [ ] Complaints and shift handover specified.
- [ ] Disclosure, permissions, NPC knowledge and bingo firewall specified.
- [ ] Pause, population cap and permanent person promotion specified.
- [ ] Text-first workflow and optional visual support specified.
- [ ] All 193 acceptance tests await BP-43 execution.
- [ ] Open decisions remain explicit; no real-world law silently imported.
- [ ] No Neon schema, seed, import or bulk write has been made or authorised.

## 38. Status and next dependencies

This is a complete division design draft, not approved policy or implementation evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-27 — Legal Processes**. BP-27 owns charging decisions, disclosure, prosecution, defence and procedural workflow. BP-26 continues to own police-custody lifecycle, clock, welfare and custody handover; BP-28 owns court proceedings and outcomes; BP-29 owns sentence execution.
