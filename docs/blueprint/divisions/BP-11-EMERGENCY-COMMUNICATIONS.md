# BP-11 — Emergency Communications

**Project:** Saltwater — fictional sovereign city-state, one city, one jurisdiction  
**Blueprint division:** BP-11 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test:** NOT_STARTED | **Verification:** NOT_STARTED

## 1. Purpose

BP-11 specifies police emergency communications: public call intake, emergency and non-emergency contact, call assessment, location resolution, call recording, communication-centre operations, computer-aided dispatch (CAD), task allocation, radio and operational messaging, unit status coordination, escalation, service continuity and communication records.

It connects the public, police field units, supervisors, incident command and supporting emergency services. Calls arrive from identifiable or anonymous sources; information may be incomplete or mistaken; call-takers clarify what they can; dispatchers allocate actual available resources; messages may be delayed or lost; field units report what they know at the time.

Preserve the distinction between what a caller reports, what a call-taker records, what a dispatcher decides, what an officer acknowledges, what is observed at scene and what later investigation establishes.

## 2. Scope and ownership

### 2.1 In scope
- Emergency, urgent, routine and non-emergency public contact channels.
- Call intake, call-taker workflow, caller interaction and call records.
- Anonymous, withheld, third-party, repeat and disconnected callers.
- Location questioning, resolution, geocoding references and confidence.
- Call categorisation, triage, priority recommendation and escalation.
- CAD event creation, updates, duplicate detection and incident linkage.
- Dispatch queue, unit selection, allocation, acknowledgement and reassignment.
- Radio channels, talkgroups, call signs, message types and transmission logs.
- Field-unit status, availability and location messages.
- Dispatcher-to-unit, unit-to-dispatch, supervisor and interagency communications.
- Emergency-service coordination and transfer of requests.
- Communication-centre staffing, roles, supervision and workload.
- Recorded calls, radio recordings, transcripts, metadata and retention interfaces.
- Communications outages, degraded modes, backup channels and recovery.
- Dispatch chronology, audit, reporting and operational performance.
- NPC call-taker/dispatcher behaviour and player-facing radio interaction.

### 2.2 Ownership boundaries

| Concern | Owner | BP-11 relationship |
|---|---|---|
| Sovereign/city geography, roads, addresses and access | BP-02 | Resolve caller/incident locations against canonical geography |
| Residents, identities, household/person records | BP-03 | Reference persons; do not create duplicate identities |
| Premises, businesses and organisations | BP-04 | Resolve reported locations and caller affiliations |
| Police mandate, command structure and authority | BP-05/BP-30 | Apply authorised communications-centre command |
| Personnel identity, career and role | BP-06/BP-07 | Authenticate staff and role eligibility |
| Unit structure, roster, assignment and deployment | BP-08 | Select only valid deployed units |
| Vehicles, radios, communication devices and readiness | BP-09 | Consume actual device/resource status |
| Patrol execution and field operations | BP-10 | Send tasks; receive status, arrival and field updates |
| Incident master, classification, command and lifecycle | BP-12 | Create/request incident; BP-12 owns incident record and command |
| Offence taxonomy and crime generation | BP-13/BP-14 | Preserve caller allegations; do not decide criminal truth |
| Case and investigative ownership | BP-15/BP-16 | Link or route authorised requests |
| Victim/witness/suspect roles | BP-17/BP-18 | Preserve reported roles as unverified until assessed |
| Formal interviews/interrogations | BP-19 | Call recording is not automatically an interview |
| Surveillance/intelligence | BP-20/BP-21 | Route authorised communications; do not expose restricted content |
| Scenes/evidence/forensics | BP-22/BP-23/BP-24 | Communicate hazards and handoffs; no evidence ownership |
| Arrest/search/warrants/custody | BP-25/BP-26 | Relay authorised instructions/status only |
| Legal processes and courts | BP-27/BP-28 | Preserve records and legal access restrictions |
| Corrections | BP-29 | No direct ownership |
| Training and qualifications | BP-32 | Consume current operator competence |
| HR attendance and schedules | BP-33 | Consume actual attendance and duty eligibility |
| Finance/procurement | BP-34 | No budget or procurement ownership |
| Simulation causality and NPC execution | BP-35 | Execute time- and event-driven communications |
| Relationships/social context | BP-36 | Use relevant context without stereotype or guilt inference |
| Authoritative time and pause | BP-37 | Timestamp and freeze all communication activity |
| Records/persistence | BP-38/BP-39 | Store canonical communications records |
| Interface and maps | BP-40 | Present call/CAD/radio views; text is authoritative |
| Notifications/reporting | BP-41 | Publish operational alerts and reports |
| Security and permissions | BP-42 | Enforce caller, staff, operational and evidential access |
| QA/configuration | BP-43/BP-44 | Test and version dispatch policy/configuration |

BP-11 owns communications-centre intake, CAD tasking and message transport records. It does not own field execution, unit establishment, incident command, crime classification, legal authority, case investigation, evidence continuity or authoritative person/location master records.

## 3. Binding Saltwater invariants

1. Saltwater is one fictional sovereign city-state, one city and one police jurisdiction. No call creates a second playable city or external territory.
2. Total living population is capped at 10,000, including police, callers, staff, responders, residents and bystanders. Count each person once.
3. At least 10,000 businesses exist in the city; business callers and premises reference BP-04 rather than duplicate records.
4. Police is the deepest simulation; other emergency services are modelled sufficiently to support credible coordination.
5. Text is the complete primary interface. Maps, audio and waveform/transcript displays are optional representations.
6. Simulation time does not advance while the player is outside the game. Calls, queues, ring timers, dispatch, radio traffic, NPC decisions and deadlines freeze.
7. A call report is an allegation/source account, not verified fact. Dispatch priority is an operational assessment, not a finding of guilt.
8. NPCs know only information received, observed, briefed or legitimately accessed at that time.
9. Preserve exact chronology and distinguish event occurrence, call arrival, answer, report, dispatch, acknowledgement, departure, arrival and later correction.
10. Never reveal perpetrator/accomplice/culprit identity unless the player types exactly bingo. No unsolicited solution hints or investigation directions.
11. Player consequential actions, including answering, dispatching, authorising exceptional actions and making operational decisions, require player input when the player is acting in that role.
12. No invented callers, staff, responders, units, devices, recordings, addresses or successful message delivery.
13. BP-08 owns unit assignment; BP-09 owns resource readiness; BP-10 owns patrol execution; BP-12 owns incident lifecycle/command.
14. All communications are attributable, access-controlled, durable and auditable.
15. Corrections append history; original call/radio content is never silently overwritten.
16. This specification authorises no Neon write, migration, seed, import, bulk data or simulation-time advancement.

## 4. Operating model and service roles

### 4.1 Communication centre
A police communications centre has configured posts, consoles, channels, supervisors, staffing levels, operating hours/coverage and fallback arrangements. Nominal establishment is not proof of staffed capacity. BP-08/BP-33 provide personnel assignment/attendance; BP-09 provides console/device/network readiness.

### 4.2 Roles
- **Call-taker:** answers and records incoming contact, clarifies immediate safety/location details and applies approved protocol.
- **Dispatcher:** manages CAD queue, selects eligible units, sends tasks and receives acknowledgements/status.
- **Combined operator:** may perform both functions if authorised and workload permits.
- **Radio operator:** handles radio traffic where separated from CAD dispatch.
- **Communications supervisor:** manages workload, quality, escalation, staffing and authorised overrides.
- **Incident/field commander:** commands the incident under BP-12/command policy; not automatically the call-centre supervisor.
- **System administrator:** technical role with no automatic right to inspect sensitive call content.
- **Player operator:** has only the role, authority, console and information assigned in the simulation.

One person may occupy multiple roles only where staffing, qualification and policy allow. Do not silently assume unlimited parallel capacity.

### 4.3 Console/session
A console session references authenticated staff, role, workstation/device, start/end time, active channel(s), permissions, shift/attendance and interruption state. Session does not itself confer authority outside the assigned role.

## 5. Core entities and records

All IDs are stable, non-semantic and globally unique within their entity type. Physical schema is deferred to implementation.

### 5.1 Communications contact
Fields: contact_id, channel, received_time, queue_time, answer_time, caller_reference (nullable), caller display/claim, anonymity/withheld state, callback reference and confidence, language/accessibility needs, location claim, contact purpose, call-taker, console, status, linked call/event/incident, recording references, outcome, source provenance and access class.

### 5.2 Call record
Fields: call_id, contact_id(s), received/answered/ended times, call category, caller relationship to event, reported occurrence time, location as stated, location resolution, urgency, immediate hazards, persons/vehicles involved as reported, caller's words/claims, call-taker questions/answers, uncertainty, priority assessment, CAD link, transfer/referral, disposition, follow-up, recording/transcript links and amendment history.

A caller may contact the centre more than once; preserve each contact and link to a common reported event only when justified.

### 5.3 CAD event
Fields: cad_event_id, event type, created source/time, reported time, location and confidence, category, priority, status, linked calls, duplicate/related event references, assigned unit(s), dispatcher, command reference, updates, alerts, incident link, disposition, closure reason and version history.

CAD is a communications coordination record. BP-12 owns the authoritative incident master. A CAD event may precede, link to, or be closed without a formal incident record.

### 5.4 Dispatch assignment
Fields: dispatch_id, CAD event, unit/officer references, selecting dispatcher, selection rationale, task details, priority, required capability, sent/received/acknowledged times, acceptance/rejection, unit status snapshots, estimated response, reassignment, cancellation, completion and message references.

### 5.5 Radio channel/message
Fields: channel_id, type, permitted roles/units, coverage, encryption/restriction class, operational purpose and effective dates. Message fields: message_id, channel, sender, intended recipient(s), transmission/receipt times, content or coded message, priority, acknowledgement, recording reference, delivery state, retry/relay and correction link.

### 5.6 Status report
Fields: status_event_id, unit/officer, status value, effective/received times, location, source (radio/CAD/device/officer/supervisor), confidence, task link, reason and superseded event. Last-known status must not be presented as current without freshness metadata.

### 5.7 Location resolution
Fields: location_resolution_id, raw caller wording, parsed components, canonical address/place/road reference, map/geocoder version, candidate matches, selected match, confidence, unresolved elements, access point, method, operator and time. Preserve raw wording.

### 5.8 Communications recording
Fields: recording_id, source device/channel, source event, start/end, recording state, gaps, device identity, codec/reference, integrity metadata, transcript/version, access class, retention policy reference, export/access history and chain-of-custody link where applicable. A transcript is not a substitute for original recording.

### 5.9 Centre staffing/capacity snapshot
Fields: centre_id, time, staffed roles, active consoles, channel load, queued calls, active CAD events, operator workload, outage/degradation, supervisor and capacity constraints. Derived from actual staffing and equipment.

### 5.10 Handover/transfer
Fields: transfer_id, source and destination role/agency, reason, request/acceptance times, content transferred, outstanding risk/task, receiving acknowledgement, refusal/failure and responsibility state.

## 6. Incoming channels and contact handling

Support configurable channels:
1. Emergency telephone call.
2. Non-emergency telephone call.
3. In-person front-desk contact.
4. Internal police radio/telephone.
5. Alarm/automated alert from a registered system.
6. Approved text or digital contact.
7. Interagency communication.
8. Officer-initiated request.
9. Supervisor/command instruction.
10. System-generated operational alert.

Each channel has source identity, delivery characteristics, expected latency, failure modes, authentication limits and recording capability. An automated alarm is a signal, not proof of an offence. Digital messages may be delayed, duplicated or incomplete. An in-person contact has no telephone call recording unless a separate recording system is active.

### 6.1 Queue and answer
Record arrival, queue entry, answer, transfer, abandonment and end times separately. If no operator is available, the contact remains queued, is routed to a valid fallback or is abandoned according to configured policy. Never create an instant answer when no operator is staffed.

### 6.2 Call opening
The call-taker establishes the nature of the request, exact/approximate location, immediate danger, callback options, people needing assistance and safe communication constraints. Questions must not delay immediate dispatch where sufficient actionable information already exists. Record what was asked and answered; unanswered questions remain unknown.

### 6.3 Caller identity
Caller may be named, self-identified, verified by an authorised method, anonymous, withheld, third-party, mistaken or impersonating. Identity claims and verified person identity remain separate. Caller ID is not proof of identity or location. Use BP-03 stable person references only when reliable matching exists.

### 6.4 Disconnected calls
Record disconnection time, last known information, callback attempts, callback success/failure and resulting tasking. A dropped call does not automatically mean the event ended. Do not fabricate callback success.

### 6.5 Repeat and abusive contacts
Preserve every contact. Link repeat contacts with a common event only on grounded matching. Repeated contact, distress, communication difficulty or unusual behaviour is not proof of bad faith. Abusive/hoax disposition requires a reasoned, attributable assessment and does not erase the original call.

## 7. Call assessment and prioritisation

### 7.1 Information dimensions
Assess reported event type, immediacy, threat to life, injury/medical need, ongoing danger, vulnerable persons, hazards, weapons as reported, number of people, location precision, access, suspect/vehicle movement as reported, caller safety, reliability/limitations, and need for specialist or multi-agency response.

### 7.2 Priority
Use configurable operational priority levels with explicit definitions, response expectations, escalation triggers and authorised overrides. Priority is a triage decision based on available information, not a guarantee of response time or determination of offence seriousness. BP-12 may later revise incident command priority; preserve both assessments and their authors.

### 7.3 Unknown and conflicting information
Represent unknown, not asked, caller unsure, conflicting reports, unverified, stale and not applicable distinctly. Never fill gaps with plausible fiction. Conflicting calls remain separately attributed until reconciled.

### 7.4 Reassessment
Reassess when new information arrives, risk changes, location changes, a caller disconnects, a unit reports new facts, or command directs. Retain prior priority/category, new value, source, reason and effective time.

### 7.5 Escalation
Escalate urgent life-safety threats, multiple casualties, major hazards, public danger, resource shortages, communications failures, high-profile/complex incidents and cross-agency needs to the designated supervisor/command path. Escalation is a notification/request, not a transfer of command unless acknowledged by the authorised recipient.

## 8. Location capture and resolution

Raw caller description must always be retained alongside any resolved location. Support canonical street address, building/premise, unit/suite, road segment, junction, landmark, public space, coordinates from a supported source, mobile caller location if available, and uncertain/approximate description.

Resolution rules:
- Use BP-02 canonical geography and BP-04 premise/business references.
- Preserve multiple plausible candidates and confidence.
- Distinguish caller's stated location, device-derived location, operator interpretation and later field correction.
- Record entrance, floor, unit, access gate and callback instructions when supplied.
- A location match is not proof the event occurred there.
- If outside city canon, treat as external context/transfer request; never expand playable geography.
- A caller may be moving; preserve time-stamped location updates.
- If a geocoder/map is unavailable, retain raw wording and manual resolution with operator/source.
- Never invent a precise address or coordinate.

Location corrections update active dispatch and BP-12 where applicable; previous dispatch destination and arrival chronology remain preserved.

## 9. CAD lifecycle

Suggested states: received, queued, being assessed, created, awaiting dispatch, dispatching, assigned, acknowledged, units responding, on scene, additional resources requested, transferred/commanded, pending disposition, closed, cancelled, duplicate-linked, unable to resource and reopened.

State transitions require actor/source, time, reason and prior state. A CAD event may have several linked calls, multiple units, related CAD events and one or more incident references. Do not collapse separate events because they share an address or caller.

Duplicate detection is advisory. A dispatcher must be able to link as duplicate/related while preserving each source call, or keep events separate where uncertainty remains. Reopening creates a new state/version and reason; never silently erase closure.

## 10. Dispatch selection and allocation

### 10.1 Eligibility
Candidate units are determined from BP-08 deployment/assignment, BP-10 operational state, BP-09 resource readiness, BP-06/BP-32 qualifications, actual location/route and current task commitments. Unit names in a directory do not prove that unit is staffed or available.

### 10.2 Selection factors
Consider incident priority, proximity/travel feasibility, capability, crew size, workload, current task, supervisor/command orders, resource readiness, geographic coverage impact, communications coverage and safety. Record selected and excluded candidates with reason at an appropriate level.

### 10.3 Allocation
Dispatcher sends task details, location and confidence, known hazards, priority, requested response, access information, reporting channel and special instructions. Unit acknowledgement, acceptance, rejection, en-route, arrival and clear messages are separate.

### 10.4 No suitable unit
Show no eligible unit and why. Dispatcher may escalate, request supervisor direction, seek another authorised service, queue with risk, reassign or advise caller of delay. Do not fabricate a unit or silently downgrade urgency.

### 10.5 Multiple units
Each unit has its own dispatch/acknowledgement/status chronology. BP-12 owns incident command and coordination. A lead unit designation is explicit and does not itself grant command powers.

### 10.6 Reassignment/cancellation
Record who authorised, reason, outgoing unit state, new recipient, acceptance and effect on response. Cancellation after a unit begins travel does not erase movement or exposure.

## 11. Radio and operational messaging

### 11.1 Radio architecture
Channels/talkgroups have configured coverage, purpose, permissions, operational priority and fallback. Actual coverage depends on BP-09 devices/network and BP-35 world conditions. Do not assume every officer hears every channel.

### 11.2 Message lifecycle
Record transmission, receipt/acknowledgement where available, relay, delay, loss, interference, repeat, correction and closure. A message sent is not necessarily received; received is not necessarily understood; acknowledgement is not proof of compliance.

### 11.3 Message classes
Support dispatch, status, arrival, assistance, urgent safety, supervisor instruction, incident update, resource request, channel change, interagency coordination, administrative and test traffic. Distinguish priority/emergency traffic from routine messages.

### 11.4 Open radio discipline
Use configurable brevity/call-sign conventions, but retain intelligible underlying meaning in the canonical record. Radio shorthand must not hide material facts or create ambiguity. Preserve original transmission and any normalised transcription separately.

### 11.5 Restricted communications
Sensitive operations may use restricted channels or approved alternate methods. Eligibility and access derive from BP-42 and command authority. Do not expose protected person, intelligence, surveillance, case or tactical details to general channels.

### 11.6 Player interaction
When the player is the radio operator or field officer, present received messages and allow explicit response. Do not auto-acknowledge, auto-dispatch or speak for the player in consequential situations. Routine configured NPC acknowledgements may be generated only for NPC-controlled units and must be logged.

## 12. Interagency and specialist coordination

Support requests to ambulance/medical response, fire/rescue, civil protection, utility response, transport operators and other relevant fictional services. BP-04/BP-35 define institutions and service capability; BP-12 owns multi-agency incident command.

Each request records requesting role, agency/service, location, need, priority, hazards, information disclosed, request time, acceptance/refusal, estimated/actual response where supplied, liaison and handover. External agency presence is within the one-city support model; no external playable territory is created.

Do not assume another service is staffed, available or has accepted. No response estimate is invented. If the receiving service is outside the simulated city-state, treat it as an external referral/communication endpoint only where canon permits; do not simulate another city.

## 13. Communications recordings and transcripts

Recordings may include telephone audio, radio audio, digital message payloads and approved console records. Each recording has source device/channel, event link, start/end, gaps, quality, failure, clock source, integrity metadata and access history.

Transcripts:
- retain source recording reference;
- identify automated, human or corrected transcription;
- preserve uncertain words, inaudible sections and speaker attribution confidence;
- never silently replace original content;
- record editor, time, reason and version;
- distinguish exact quotation from summary.

Recording activation and retention depend on configured policy and actual device operation. A failed recorder produces a gap, not a fabricated recording. A recording is not automatically admissible evidence or an interview record. BP-23 owns evidential continuity where formally submitted as an exhibit; BP-38/BP-39 own records/persistence.

## 14. Staffing, workload and centre supervision

Communications capacity depends on actual call-takers, dispatchers, supervisors, consoles, channel capacity, network/device readiness and workload. The system must model queues and competing tasks. A single operator cannot answer unlimited calls and dispatch unlimited incidents simultaneously.

Workload factors include active calls, simultaneous radio traffic, CAD updates, emergency escalations, interagency coordination, breaks, training, fatigue/fitness restrictions, technical failure and supervisor tasks.

Supervisors can rebalance workloads, open/close positions, authorise overtime/recall under configured rules, request support and escalate capacity shortage. They cannot create personnel or override attendance/qualification records. Record staffing snapshots and decision history.

## 15. Outages and degraded operations

Failure domains include telephone carrier, public contact channel, CAD application, database/persistence, radio network, repeater/site, console, power, building access, recording equipment, geocoder/map service and interagency link.

For each failure: detect/source, start time, affected services/areas, confidence, impact, fallback, notification, manual record method, recovery time, replay/reconciliation and unresolved gaps.

Degraded mode may use manual logs, alternate channel, direct supervisor relay or another staffed position only when configured and actually available. Manual records receive stable IDs and are reconciled idempotently. No message is assumed delivered during an outage. On recovery, preserve original effective times and actual received/reconciled times.

## 16. Security, confidentiality and privacy boundaries

BP-42 owns permissions. Apply role- and purpose-based access to caller identity, contact details, sensitive locations, protected persons, call audio, transcripts, intelligence references, case-linked information and operational channels.

- Call-takers access only information needed for intake and immediate safety.
- Dispatchers access location, priority, hazard and task details needed for allocation.
- Field units receive only operationally necessary details.
- Supervisors access records within their remit.
- Investigators receive authorised referrals/case access, not unrestricted centre data.
- Technical administrators do not automatically gain content access.
- Exports, playback, transcript correction, disclosure, override and lookup are audited.
- Emergency override requires reason, scope, actor, time and post-event review.
- Access denial must not destroy the source record.
- Player-facing views must not reveal hidden culprit truth or NPC-only knowledge.

## 17. NPC call-taker/dispatcher behaviour and player agency

NPC operators act according to role, training, policy, workload, equipment, known information, language/accessibility ability, time and supervisor instructions. They may misunderstand, mishear, delay, make reasonable mistakes or be overloaded. Such errors are recorded and may have consequences; they are not silently corrected by omniscient simulation.

NPC dispatchers consider real unit availability and task commitments. They cannot see hidden case truth, unavailable records or future events. They may escalate uncertainty rather than invent certainty.

The player sees only information legitimately available at their console/radio/role. Consequential actions require explicit player input when the player is responsible. The simulation must not make the player answer, dispatch, acknowledge, authorise, disclose or cancel automatically. If the player is off duty or absent, time and communication activity freeze under the global pause rule.

## 18. Outputs and event contracts

### Inputs
- BP-02/BP-04: canonical locations, addresses, premises and organisations.
- BP-03: person identities and population countability.
- BP-05/BP-30: mandate, command, authority, escalation and policy.
- BP-06/BP-07/BP-08: staff roles, qualifications, attendance, unit structure and deployment.
- BP-09: consoles, telephony, radios, devices, network and resource readiness.
- BP-10: patrol status, task acceptance, movement, arrival and field updates.
- BP-12: incident priority, command, coordination and lifecycle.
- BP-13/BP-14: offence/occurrence categories where relevant.
- BP-15/BP-16: authorised case/investigation task references.
- BP-17/BP-18/BP-19: person roles and formal interview referrals.
- BP-20/BP-21: restricted surveillance/intelligence references under access controls.
- BP-22/BP-23/BP-24: scene, evidence and forensic notifications.
- BP-25/BP-26: authorised arrest/search/custody status.
- BP-32/BP-33: qualifications, attendance and staffing restrictions.
- BP-35/BP-36/BP-37: causal world events, relevant social context and canonical time/pause.
- BP-38/BP-39/BP-42: records, persistence and access control.

### Outputs
Contact/call records; location resolutions; call assessments and priority decisions; CAD events; dispatch assignments; radio messages and acknowledgements; unit-status updates; resource requests; interagency requests; escalation alerts; recordings/transcripts and access logs; outage/degraded-mode events; handovers; communications reports; incident update requests and acknowledgements.

### Event envelope
Every event carries event_id/type/schema_version, source/actor, subject/reference IDs, effective simulation time, recorded/received time, location where relevant, console/channel, provenance, access class, idempotency key and record version.

Core events: ContactReceived/Queued/Answered/Transferred/Abandoned/Ended; CallCreated/Updated/Assessed/Closed/Reopened; LocationResolved/Corrected; PriorityAssigned/Changed/Overridden; CADEventCreated/Updated/Linked/DuplicateMarked/Closed/Reopened; DispatchProposed/Sent/Acknowledged/Accepted/Rejected/Reassigned/Cancelled; UnitStatusReceived; RadioMessageSent/Received/Acknowledged/Relayed/Failed; AssistanceRequested/Accepted/Refused; InteragencyRequestSent/Acknowledged/Rejected; RecordingStarted/Stopped/Failed/Accessed/Exported; TranscriptCreated/Corrected; CentreCapacityChanged; ServiceOutageDetected/Updated/Recovered; ManualLogCreated/Reconciled; HandoverRequested/Acknowledged.

Cross-system ownership changes require explicit recipient acknowledgement. Event replay must be idempotent.

## 19. Permissions and roles

| Role | Permitted scope |
|---|---|
| Call-taker | Intake, call record and immediate safety information |
| Dispatcher | CAD, eligible unit status, dispatch and operational radio |
| Combined operator | Both scopes only while assigned/qualified |
| Communications supervisor | Centre operations, workload and authorised overrides |
| Field officer | Assigned dispatch and channel information |
| Incident commander | Incident-related operational communications |
| Investigator | Referred/case-authorised records |
| Professional standards | Purpose-limited audit and complaint records |
| Records officer | Retention/export workflow within policy |
| System administrator | Technical configuration; no automatic content access |
| Auditor | Read-only approved audit scope |
| Player | Current role and console permissions only |

Access is least-privilege. Read does not imply amend, dispatch, export or disclose. Role changes take effect at recorded time; prior access remains audited. A player cannot access another operator's private session without authority.

## 20. Exceptions and edge cases

1. No operator staffed: queue, route to configured fallback or record abandonment; no invented answer.
2. Operator answers two calls simultaneously: enforce console/workload capacity.
3. Caller disconnects before location: preserve partial call and uncertainty.
4. Caller disconnects after dispatch: preserve dispatch; callback attempts separately.
5. Caller refuses identity: retain anonymous/withheld state.
6. Caller ID conflicts with caller statement: preserve both sources.
7. Caller uses a third party's phone: do not infer caller identity from subscriber.
8. Caller cannot speak: use supported silent/emergency protocol only if configured; preserve ambiguity.
9. Language barrier: record language and actual interpreter availability; no invented translation.
10. Accessibility need: apply available support; record delay/limitation.
11. Caller is distressed/confused: preserve words and call-taker interpretation separately.
12. Caller gives changing location: time-stamp each update and notify dispatched units.
13. Caller gives vague landmark: retain raw wording; no fabricated street number.
14. Multiple plausible addresses: show candidates/confidence; dispatcher may request clarification.
15. Map/geocoder unavailable: manual/raw location retained.
16. Address is outside Saltwater: external context/referral only; no new playable geography.
17. Caller reports event in a private building: access point and unit details remain distinct.
18. Caller reports moving vehicle: retain direction/time/source and uncertainty.
19. Device-derived location conflicts with caller: preserve both; no silent preference.
20. Duplicate call from same caller: preserve both contacts and link cautiously.
21. Several callers report same event: separate accounts linked to one CAD event where justified.
22. Similar calls at same address but unrelated: keep separate events.
23. False/hoax allegation later identified: retain original and later assessment.
24. Malicious caller impersonates official: verify through authorised channel; do not accept claimed authority.
25. Caller makes allegation against police employee: preserve source and restricted route to BP-31.
26. Call category uncertain: provisional classification and review.
27. Priority disputed by supervisor: preserve both decisions and authority.
28. New life threat during routine call: reassess and escalate immediately.
29. Caller reports weapon but cannot describe: mark reported/unknown, not confirmed.
30. Caller reports injury without medical detail: do not invent diagnosis.
31. Caller cannot safely continue: preserve communication constraint and approved procedure.
32. Call-taker misses question: mark unknown; no inferred answer.
33. Call audio unintelligible: preserve audio/gap and uncertain transcript.
34. Recording device failed: record failure; never fabricate recording.
35. Recording starts late: preserve missing opening interval.
36. Recording stops early: preserve gap and stop reason.
37. Transcript disagrees with audio: audio remains source; correction versioned.
38. Speaker attribution uncertain: retain uncertainty.
39. Caller asks for confidentiality: explain only configured policy; restrict access appropriately.
40. Sensitive location reported: apply restricted dissemination.
41. Caller identity matched to wrong resident: correct by append-only process; preserve original match.
42. Person not in database: do not exceed 10,000 cap; creation controlled by BP-03.
43. Caller is already counted resident: reuse stable person ID.
44. Business caller: reference BP-04 business and named caller separately.
45. Alarm activation with no caller: alarm source is not proof of crime.
46. Automated alert duplicates: idempotency and source reference prevent duplicate dispatch.
47. Alarm has stale contact/location: show staleness; verify before reliance where possible.
48. CAD application unavailable: manual fallback only if staffed and configured.
49. Database unavailable: durable local/manual queue with reconciliation; no false persistence claim.
50. Radio repeater failure: affected coverage shown; no universal radio reach.
51. Telephone carrier outage: show failed/alternate channel and public impact.
52. Power failure: actual backup power capability required.
53. Console failure: operator moves only to an available console.
54. Radio interference: message delivery/understanding uncertain; repeat/relay.
55. Message sent but not acknowledged: do not mark accepted.
56. Acknowledgement received late: preserve sent/received times.
57. Radio transmission overlaps: preserve collision/inaudibility.
58. Incorrect call sign: clarify; do not route to guessed unit.
59. Unit responds on wrong channel: record failed contact and channel correction.
60. Dispatcher sends to unavailable unit: reject or flag and reassign; no phantom deployment.
61. Unit status stale: treat availability as uncertain, not current.
62. Unit declines task: preserve reason and request supervisor decision.
63. Two dispatchers allocate same unit: concurrency control prevents double commitment.
64. Unit becomes unavailable after allocation: update and reassess.
65. No unit available: escalate/queue/seek authorised service; no invented responder.
66. Nearest unit lacks capability: choose eligible alternative or request specialist.
67. Candidate unit has conflicting task: expose commitment and obtain authorised reprioritisation.
68. Dispatch location changes: send correction and preserve old destination.
69. Dispatcher cancels after departure: movement remains in BP-10.
70. Multiple units assigned: individual chronology and command linkage.
71. Lead unit not acknowledged: do not assume command accepted.
72. Supervisor overrides priority: authority/reason/time and review recorded.
73. Operator makes mistaken entry: append correction and preserve source.
74. Call is reopened: prior closure and reason retained.
75. CAD duplicate merge is reversed: original calls/events remain resolvable.
76. Incident record not yet created: CAD remains valid pending BP-12 linkage.
77. CAD closed but incident active: separate lifecycle states remain.
78. Incident commander changes: BP-12 authority update controls command.
79. Interagency service unavailable: preserve refusal/unavailability and escalation.
80. External agency requests sensitive details: disclose only authorised minimum.
81. Ambulance/fire request accepted but ETA unknown: do not invent ETA.
82. Radio channel restricted: deny unauthorised access and audit.
83. Operator accesses unrelated call: deny or audit according to permission.
84. Emergency override used: scope, reason, actor and review retained.
85. Player lacks dispatcher role: cannot dispatch from a field console.
86. Player is dispatcher: consequential dispatch requires explicit choice.
87. Player exits simulation: all queues, timers and messages freeze.
88. Player resumes: no hidden call arrivals or elapsed response time.
89. NPC operator acts on hidden truth: flag knowledge-provenance violation.
90. NPC dispatcher invents unit availability: reject and log simulation defect.
91. Caller reports a known suspect: report remains allegation, not guilt.
92. Call relates to ongoing case: link only through authorised reference; do not reveal case secrets.
93. Call contains evidence claim: record source; BP-23 owns exhibit continuity.
94. Caller requests immediate arrest: request does not grant arrest authority.
95. Call requests search of premises: no search authority created by call.
96. Caller reports officer distress: dispatch assistance using actual available units.
97. Distress button activation without location: last confirmed location marked stale/uncertain.
98. Multiple simultaneous emergencies exceed capacity: queue and prioritise transparently; escalate.
99. Call volume spikes: capacity and wait time reflect actual staffed positions.
100. Operator fatigue/absence: BP-33 eligibility and BP-08 assignment apply.
101. Unqualified staff at console: block restricted functions.
102. Shift handover mid-call: named operator transfer and acknowledgement.
103. Dispatcher leaves with active tasks: explicit handover; no orphaned CAD events.
104. Handover recipient unavailable: current operator/supervisor retains responsibility.
105. Manual log reconciled after outage: original event time and reconciliation time separate.
106. Replayed message duplicates prior event: idempotent handling.
107. Events arrive out of order: preserve source/received chronology and deterministic state.
108. Clock correction: BP-37 canonical time rules; never rewrite source timestamps.
109. Communications centre relocates: authorised configuration and effective time required.
110. Emergency channel overloaded: priority traffic and degraded mode visible.
111. Radio battery fails: BP-09 device readiness updated; no assumed transmission.
112. Caller is a minor or vulnerable person: apply configured safeguarding referral; do not infer details.
113. Caller gives sensitive unrelated information: minimise onward disclosure, preserve necessary source.
114. Media/public official calls: same triage; no automatic priority or privileged access.
115. Business alarm from closed premises: business hours/status are context, not proof of entry/offence.
116. Caller alleges crime that is not an offence: preserve allegation; BP-13 classification controls.
117. Non-crime welfare request: create appropriate CAD task without forcing crime classification.
118. Location is a shared address with multiple units: unit/access point remains unresolved until confirmed.
119. Caller gives wrong address then corrects: preserve both and update field unit immediately.
120. Dispatcher hears ambiguous instruction: clarify; do not infer authorisation.
121. Operator accidentally broadcasts protected data: record incident and access/security referral.
122. Transcript export requested: permission, purpose and export history required.
123. Recording submitted as evidence: BP-23 chain-of-custody handoff acknowledged.
124. Retention deadline reached while legal hold exists: BP-38 policy/hold controls disposition.
125. A call record is corrected after case linkage: notify authorised linked owners without overwriting.
126. Unit sends field update with unverified claim: label as report/source, not fact.
127. Two agencies use different incident references: preserve both cross-references.
128. Interagency transfer not acknowledged: origin retains responsibility/status.
129. Public call channel sends duplicate packets: deduplicate transport without losing distinct user messages.
130. New staff member joins mid-shift: role, training, session and access effective time recorded.
131. Console session expires during active emergency: controlled continuity and reauthentication.
132. Network returns with stale unit positions: mark stale until refreshed.
133. Public channel unavailable but radio active: do not assume public can reach centre.
134. Caller calls back after closure with new information: new contact, linked event and reassessment.
135. Call reports multiple locations: create distinct location claims and dispatch tasks as needed.
136. CAD event has no resolvable location: retain open/limited state and escalation.
137. Operator selects wrong unit: correction/reassignment chronology retained.
138. Dispatch task has no acceptance: show unacknowledged; escalate per policy.
139. Message delivered to wrong recipient: record, restrict further disclosure and correct.
140. A unit transmits but dispatcher does not hear: transmission and receipt remain distinct.
141. Radio message is relayed by another unit: relay chain retained.
142. Automatic location update is inaccurate: preserve source and confidence; do not treat as ground truth.
143. Centre capacity display is stale: show timestamp and unknown state.
144. A call is answered but not recorded: recording gap explicit; call record still exists.
145. System-generated alert has no responsible owner: route to configured queue, not a fabricated operator.
146. Request conflicts with command order: follow configured authority precedence and audit.
147. Incident priority changes after field arrival: notify units and preserve prior tasking.
148. Call category changed after assessment: retain old/new category and reason.
149. Caller retracts allegation: preserve original report and retraction separately.
150. Player asks for restricted transcript: deny and explain permission boundary.
151. Player attempts to dispatch outside city canon: reject playable destination; external referral only.
152. Population cap would be exceeded by new caller: use anonymous/unknown source unless verified creation is permitted within cap.
153. Police personnel counted twice as residents: reconcile one person identity/count.
154. Service outage occurs while player is absent: time remains frozen; no hidden outage progression.
155. Communications recording has no integrity metadata: flag evidential limitation; do not claim verified integrity.
156. A call-taker summarises instead of verbatim quote: label as summary and preserve distinction.
157. A caller's statement is translated: preserve original where available, translation source and uncertainty.
158. Emergency call is transferred between operators: preserve full transfer chronology and responsibility.
159. Call queue priority changes while waiting: retain original and revised order/reason.
160. A unit reports arrival at a different access point: preserve reported location and reconcile with BP-10.
161. Radio status conflicts with CAD telemetry: preserve both and flag conflict.
162. A communications record is deleted by unauthorised actor: reject and audit; recovery via BP-39.
163. A system update changes priority rules: BP-44 version/effective time and audit required.
164. A test call enters live queue: identify test source and prevent accidental operational dispatch.
165. An operator mistakes test traffic for emergency: record decision and correction without erasing event.
166. A call is made from a business alarm panel: distinguish panel identity, premises and human caller.
167. Call-taker is interrupted by radio emergency: record pause, reassignment and call continuity.
168. Multiple operators edit same CAD event: version/concurrency control and conflict resolution.
169. A field unit requests dispatch correction: preserve request, authorisation and update delivery.
170. A caller asks for unit identity/location: disclose only permitted public information.
171. A call contains threat against a public institution: preserve exact source and escalate under policy without presuming credibility.
172. A request concerns a utility hazard: route to appropriate service and BP-12 coordination.
173. A communication is delayed by queue overload: actual delay visible and reviewable.
174. An operator is temporarily unfit: supervisor reassigns console duties; no silent capacity assumption.
175. A person is materially connected to a case: BP-03 permanent promotion applies; reuse persistent identity.
176. A call is associated with a person later found deceased: preserve call chronology; BP-03 lifecycle handles person status.
177. A CAD event references a business that changes name: stable BP-04 entity reference remains.
178. A road/place name changes: canonical BP-02 ID and version resolve historical wording.
179. A caller's callback number is reassigned: do not assume present subscriber is historical caller.
180. A message is received after task closure: preserve late receipt and reopen/review only by authorised decision.
181. A task is cancelled but safety update arrives: route update and reassess; do not discard.
182. An officer sends a personal message over operational channel: retain according to configured policy; do not treat as dispatch task automatically.
183. A radio channel is accidentally left open: record exposure and security incident.
184. A supervisor requests call recording playback: purpose/permission and audit required.
185. A recording is corrupt: preserve source metadata and corruption status.
186. A transcript has machine-generated speaker labels: mark confidence and avoid asserting identity.
187. A caller's account is internally inconsistent: record inconsistency without automatic falsehood finding.
188. A call concerns an event outside police remit: route/referral and caller advice, not forced police incident.
189. An operator requests a resource not authorised for dispatch: reject/escalate.
190. An emergency call is answered by a fallback centre: record actual centre, operator and transfer chain.
191. A system restarts during an active call: recover durable state and expose any unrecoverable gap.
192. A dispatch message has partial payload: flag missing fields and seek clarification.
193. A caller requests an ambulance but police are first available: dispatch according to authorised protocol; no service substitution without authority.
194. A unit cannot acknowledge because device failed: show communication uncertainty, not refusal.
195. An incident has no assigned commander: BP-12 escalation; BP-11 does not self-appoint command.
196. A new caller would exceed 10,000 people: do not create person record; retain unlinked call source.
197. An NPC operator has a relationship to caller: conflict/recusal rules apply where configured; audit.
198. A call contains information from a restricted source: retain source restrictions in all onward referrals.
199. A dispatcher uses stale beat coverage data: flag version/staleness and request current BP-08/BP-10 state.
200. A CAD event has unresolved duplicate candidates at closure: preserve links as uncertain, do not merge silently.
201. A public contact is interrupted by player exit: freeze call and all timers exactly.
202. A communication is received during paused game: impossible; no event may progress while paused.
203. A field report contradicts caller account: preserve both accounts and source chronology.
204. A call is linked to an active case with hidden solution: no player-facing disclosure absent exact bingo.
205. A service is marked recovered before actual confirmation: reject or mark provisional with source.
206. A communications centre exceeds configured console count: block fictitious concurrent session.
207. A unit is in a different location than last report: use newest reliable status and show timestamp/confidence.
208. A caller requests police attendance for a civil disagreement: record request and triage; do not invent offence.
209. A supervisor instructs call closure without disposition: require reason or retain unresolved state.
210. A communications report aggregates sensitive contacts: apply aggregation and minimum disclosure controls.

## 21. Acceptance tests and evidence

All tests use fictional fixtures and controlled simulation time. Each test records fixture IDs, policy/configuration version, source events, expected and actual states, actor, effective/recorded times, provenance and reproducible evidence.

| ID | Scenario | Required result |
|---|---|---|
| COM-001 | Emergency call arrives | Stable contact and call with source/time |
| COM-002 | No operator available | Queue/fallback/abandonment; no fabricated answer |
| COM-003 | Call answered | Answer time/operator/console recorded |
| COM-004 | Caller disconnects | End/disconnect and callback history preserved |
| COM-005 | Anonymous caller | No invented identity |
| COM-006 | Caller ID conflicts | Both claims preserved |
| COM-007 | Third-party caller | Caller and subject distinct |
| COM-008 | Language barrier | Actual capability/interpreter availability recorded |
| COM-009 | Silent call | Configured procedure only; uncertainty retained |
| COM-010 | Multiple calls same event | Separate sources linked without duplication |
| COM-011 | Similar calls unrelated | Separate CAD events |
| COM-012 | Caller retracts allegation | Original/retraction retained |
| COM-013 | Location exact | Canonical reference and raw wording stored |
| COM-014 | Location ambiguous | Candidates/confidence retained |
| COM-015 | Device location conflict | Both sources preserved |
| COM-016 | Moving caller | Time-stamped location updates |
| COM-017 | Outside-city location | No playable geography expansion |
| COM-018 | Geocoder unavailable | Manual/raw location workflow |
| COM-019 | Priority assigned | Criteria, actor, time and version |
| COM-020 | New threat reported | Priority reassessed and history preserved |
| COM-021 | Supervisor override | Authority/reason/audit |
| COM-022 | Caller reports weapon | Unverified report label |
| COM-023 | Caller reports injury | No invented diagnosis |
| COM-024 | Non-crime request | Appropriate non-crime task |
| COM-025 | CAD event created | Stable ID and call linkage |
| COM-026 | CAD duplicate candidate | Advisory link; no destructive merge |
| COM-027 | CAD reopened | Prior closure retained |
| COM-028 | Incident not yet created | CAD remains valid pending BP-12 |
| COM-029 | CAD closure vs incident | Independent lifecycles |
| COM-030 | Unit selection | Actual BP-08/BP-09/BP-10 eligibility |
| COM-031 | Nearest unit unavailable | No dispatch to phantom unit |
| COM-032 | Nearest unit lacks capability | Eligible alternative/escalation |
| COM-033 | Unit already committed | Conflict exposed |
| COM-034 | No unit available | Delay/escalation, no fabrication |
| COM-035 | Dispatch sent | Sent distinct from acknowledgement |
| COM-036 | Unit acknowledges | Receipt/acceptance chronology |
| COM-037 | Unit rejects | Reason and reassignment |
| COM-038 | Unit status stale | Unknown/stale, not available |
| COM-039 | Two dispatchers allocate same unit | Concurrency prevents double assignment |
| COM-040 | Multiple units dispatched | Separate assignment/status timelines |
| COM-041 | Reassignment after departure | Movement and old/new task history |
| COM-042 | Cancellation after departure | Movement remains |
| COM-043 | Dispatch location corrected | Old/new destinations and delivery |
| COM-044 | Radio message sent but not received | Delivery remains unconfirmed |
| COM-045 | Late acknowledgement | Sent/received times preserved |
| COM-046 | Radio interference | Uncertain delivery/understanding |
| COM-047 | Radio relay | Relay chain retained |
| COM-048 | Restricted channel | Access control enforced |
| COM-049 | Wrong call sign | Clarification, no guessed routing |
| COM-050 | Channel coverage failure | No assumed universal reach |
| COM-051 | Player is field officer | Explicit radio response required |
| COM-052 | Player is dispatcher | Explicit dispatch decision required |
| COM-053 | Player lacks dispatcher role | Dispatch action denied |
| COM-054 | NPC dispatches | Only known/eligible units |
| COM-055 | NPC uses hidden truth | Knowledge-provenance violation |
| COM-056 | Emergency service request | Request/acceptance/refusal distinct |
| COM-057 | Agency unavailable | No invented response |
| COM-058 | Interagency transfer | Recipient acknowledgement |
| COM-059 | Sensitive detail requested | Minimum authorised disclosure |
| COM-060 | Call recording active | Device/source/start/end linked |
| COM-061 | Recording failure | Gap recorded; no fabricated audio |
| COM-062 | Recording starts late | Missing interval retained |
| COM-063 | Transcript corrected | Version and editor; original retained |
| COM-064 | Speaker uncertain | Attribution confidence shown |
| COM-065 | Recording exported | Permission/purpose/access audit |
| COM-066 | Recording submitted as evidence | BP-23 handover acknowledgement |
| COM-067 | Retention/legal hold | BP-38 policy governs disposition |
| COM-068 | Call volume exceeds staffing | Queue/workload reflects capacity |
| COM-069 | Operator absent | BP-33/BP-08 availability enforced |
| COM-070 | Unqualified operator | Restricted function blocked |
| COM-071 | Operator handover mid-call | Transfer and acknowledgement |
| COM-072 | Dispatcher leaves with active tasks | Explicit handover |
| COM-073 | Centre outage | Affected service and fallback recorded |
| COM-074 | CAD outage | Manual/degraded process only if available |
| COM-075 | Radio outage | Alternate channel only if available |
| COM-076 | Power failure | Backup capability checked |
| COM-077 | Recovery and replay | Idempotent reconciliation |
| COM-078 | Duplicate message replay | No duplicate action |
| COM-079 | Out-of-order events | Source/receipt chronology preserved |
| COM-080 | Clock correction | BP-37 authority; originals retained |
| COM-081 | Concurrent CAD edits | Version/conflict handling |
| COM-082 | Unauthorised lookup | Deny and audit |
| COM-083 | Emergency override | Scope/reason/review |
| COM-084 | Hidden culprit exists internally | No disclosure absent exact bingo |
| COM-085 | Player exits simulation | All call/dispatch/radio time freezes |
| COM-086 | Player resumes | No hidden elapsed time or arrivals |
| COM-087 | Population cap reached | No new person creation beyond 10,000 |
| COM-088 | Police person counted twice | Population reconciliation |
| COM-089 | Business caller | BP-04 stable reference |
| COM-090 | Materially connected person | BP-03 permanent promotion/reference |
| COM-091 | Call linked to case | Authorised reference; no secret disclosure |
| COM-092 | Caller alleges suspect | Allegation remains distinct from guilt |
| COM-093 | Caller requests arrest/search | No authority created by request |
| COM-094 | Call reports possible evidence | Source preserved; BP-23 owns exhibit |
| COM-095 | Officer distress call | Real available assistance only |
| COM-096 | Distress location uncertain | Last-known/confidence visible |
| COM-097 | Multiple simultaneous emergencies | Capacity/prioritisation/escalation |
| COM-098 | Caller callback after closure | New contact and reassessment |
| COM-099 | Field update contradicts caller | Both sources retained |
| COM-100 | Late message after closure | Late receipt and authorised review |
| COM-101 | Message delivered to wrong recipient | Disclosure incident and correction |
| COM-102 | Test call enters queue | Identified and prevented from accidental live dispatch |
| COM-103 | Test traffic mistaken as emergency | Correction without erasure |
| COM-104 | Sensitive unrelated information | Restricted/minimised onward disclosure |
| COM-105 | Call record corrected after case link | Linked owners notified; original retained |
| COM-106 | Service recovery is provisional | Not marked fully recovered without confirmation |
| COM-107 | Console count exceeded | Concurrent session blocked |
| COM-108 | Stale beat coverage | Current BP-08/BP-10 data required or flagged |
| COM-109 | Unresolved duplicate at closure | Uncertain relation retained |
| COM-110 | Paused game receives call | No event progresses during pause |
| COM-111 | Operator has caller conflict | Configured recusal/oversight applied |
| COM-112 | Sensitive source restriction | Propagates to all referrals |
| COM-113 | Call contains translated statement | Original/translation/source uncertainty preserved |
| COM-114 | Public channel unavailable | No assumption caller can reach centre |
| COM-115 | Emergency transfer to fallback centre | Full transfer and responsibility chronology |
| COM-116 | System restarts during active call | Durable recovery and explicit gaps |
| COM-117 | Partial dispatch payload | Missing fields flagged; clarification |
| COM-118 | Call outside police remit | Appropriate referral, no forced crime record |
| COM-119 | CAD closure lacks disposition | Closure blocked or authorised exception |
| COM-120 | Aggregate reporting | Definitions, context and privacy controls |

## 22. Reporting and performance

Reports may include contact volume by channel/time/category, queue and answer intervals, abandonment, location resolution quality, call-to-dispatch intervals, dispatch acknowledgement, unit availability, resource shortfall, repeat contacts, transfer success, radio delivery/coverage, recording gaps, outage duration, staffing and workload, escalation, handover and audit exceptions.

Metrics must define clock endpoints, inclusion/exclusion, priority, time window and missing data. A short answer time is not proof of good triage; dispatch speed is not proof of correct allocation; call volume is not crime prevalence; repeat calls are not proof of caller dishonesty. Never rank operators solely by volume, closure rate or response time without workload and case-mix context. Performance review does not itself establish misconduct; BP-31 owns formal processes.

## 23. Non-functional requirements

- **Temporal integrity:** canonical simulation time; distinct effective, received, answered, dispatched, acknowledged and reconciled times.
- **Spatial integrity:** canonical city locations; preserve raw descriptions and uncertainty.
- **Availability truth:** only actually staffed operators, consoles, units and channels can act.
- **Message integrity:** sent, delivered, received, acknowledged and understood are distinct.
- **Epistemic integrity:** caller report, operator summary, dispatch assessment, field observation and verified fact remain distinct.
- **Player agency:** consequential player decisions require explicit input.
- **NPC realism:** workload, qualification, knowledge and equipment bound behaviour.
- **Population integrity:** maximum 10,000 living people, counted once.
- **Auditability:** immutable source, versioned corrections, access and override history.
- **Replay safety:** idempotent delivery and recovery.
- **Security:** least privilege, purpose limitation and restricted channel/content handling.
- **Resilience:** durable fallback, visible outage and reconciliation.
- **Storage efficiency:** shared stable references; do not duplicate people, businesses, premises, units, incidents, cases, evidence or resource masters.
- **Text-first completeness:** every operational action possible and understandable without audio/map UI.
- **Explainability:** display why a call is queued, a location uncertain, a unit ineligible or a message unacknowledged.

## 24. Source traceability

Primary source mappings to the original 52-division source:
- S02: geography, address, road and location resolution.
- S03/S04: population and individual identity references.
- S08/S09: organisations and business premises/caller context.
- S23: police governance and communications-centre authority.
- S25: personnel, rosters, roles and deployed units.
- S26: operational command and supervision.
- S27: emergency call-taking, CAD, dispatch and radio.
- S28: field operations, status, response and task handoff.
- S29/S30: incident/crime classification and case linkage.
- S37: arrest/search/custody communication interfaces.
- S38: courts/legal process records where disclosure/notice is relevant.
- S41: authoritative time, schedule and pause.
- S42: simulation engine, NPC behaviour and causal event handling.
- S48: security, permissions and sensitive information.
- S49/S50: persistence, recovery, backup and integrity.
- S51: observability, outage and operational monitoring.
- S52: canon/configuration/version control.

The original source JSON remains authoritative for source wording. The 52-to-44 crosswalk maps all source requirements/tests, but structural mapping alone does not establish semantic completeness. Every applicable requirement must be checked against this division and its named owner/interface.

## 25. Open decisions

1. Communications-centre name, location and console layout.
2. Exact centre staffing establishment, posts and shift pattern.
3. Whether call-taking and dispatch are separate posts or combined at different workload levels.
4. Call priority levels, definitions, review thresholds and escalation matrix.
5. Emergency/non-emergency contact channel catalogue and operating coverage.
6. Public caller callback and anonymous-call protocols.
7. Supported language/accessibility service availability.
8. Call-taking question sets and when immediate dispatch may precede completion.
9. Location resolution sources, confidence thresholds and fallback method.
10. CAD categories, statuses, duplicate-link rules and closure criteria.
11. Unit selection weighting and dispatcher discretion boundaries.
12. Dispatch acknowledgement and escalation intervals.
13. Radio channel/talkgroup catalogue, coverage and access.
14. Call-sign and message conventions.
15. Radio recording and transcript policy.
16. Telephone/digital recording activation, retention and export rules.
17. Emergency override and audit-review procedure.
18. Interagency request catalogue, contacts and acceptance workflows.
19. Manual/degraded mode and fallback centre arrangements.
20. Staffing/workload thresholds and fatigue management.
21. Supervisor authority over queue/priority/reassignment.
22. Public notification and caller update standards.
23. Communications reporting intervals and metric definitions.
24. Data retention and access boundaries across call/CAD/radio recordings.
25. NPC operator error and quality-review parameters.
26. Console/device/network capacity and outage recovery targets.
27. Which communication events create a BP-12 incident automatically versus by operator/dispatcher action.
28. How text/digital messages are rate-limited and protected from spam without discarding emergency information.
29. How historical call references are presented to field officers.
30. Exact schema/event delivery contract with BP-10, BP-12 and BP-38/BP-39.

Do not invent permanent staffing numbers, response-time guarantees, recording retention periods, priority thresholds, channel coverage, or unit quantities while unresolved. Represent them as versioned configuration with an explicit owner.

## 26. Completion criteria

BP-11 may move from DESIGNED_DRAFT only after:
- every mapped source requirement/test is semantically checked against the unchanged 52-division source;
- all interfaces with BP-02/BP-03/BP-04/BP-05/BP-08/BP-09/BP-10/BP-12/BP-32/BP-33/BP-37/BP-38/BP-39/BP-42 are reconciled;
- call, CAD, dispatch, radio, recording, outage and handover lifecycles have unambiguous states and owners;
- location, priority, message delivery, identity, population and time invariants are validated;
- permission and hidden-truth boundaries are tested;
- all acceptance tests have explicit fixtures, actions, expected outcomes and evidence;
- open decisions are resolved or explicitly accepted as configurable with an owner;
- the user approves the specification.

Implementation, testing and verification remain independent register states. This document authorises no Neon schema change, migration, seed, import, bulk record creation or database write.
