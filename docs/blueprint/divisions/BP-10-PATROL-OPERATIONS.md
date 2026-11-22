# BP-10 — Patrol Operations

**Project:** Saltwater — fictional sovereign city-state, one city, one jurisdiction  
**Blueprint division:** BP-10 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test:** NOT_STARTED | **Verification:** NOT_STARTED

## 1. Purpose

BP-10 defines how uniformed and specialist police personnel conduct patrol and field operations. It governs patrol presence, beat coverage, mobile/foot patrol, directed patrol, proactive activity, observation, public contact, traffic activity, initial response, arrival, dynamic assessment, field decisions, assistance requests, handover and return to availability.

The system must make the police service operationally alive and causally connected to the city. Patrol is grounded in geography, time, actual attendance, unit capability, resource readiness, traffic, weather, incident demand and prior events. NPC officers act according to their roles, knowledge, training, orders, current state and resources. The player controls their officer's decisions.

Patrol is not a narrative shortcut. Preserve what an officer observed, was told, inferred, decided and what objectively happened as distinct records. Do not turn suspicion into fact, a dispatch allegation into a verified offence, or a patrol contact into guilt.

## 2. Scope and boundaries

### In scope
- Patrol functions, modes, beats, sectors, coverage plans and directed areas.
- Patrol shift activation and operational handover interfaces.
- Officer/unit field status, availability and location consumption.
- Foot, vehicle, cycle and other approved patrol modes.
- Planned routes, dynamic routes, checkpoints and coverage objectives.
- Travel feasibility, response time and route constraints.
- Proactive patrol, visibility, observation and patrol-generated encounters.
- Public contacts, assistance, welfare checks and non-crime activity.
- Traffic patrol, stops, road incidents and scene-safety interfaces.
- Response to dispatched incidents and self-initiated events.
- On-scene assessment, risk, containment, assistance and escalation.
- Field actions, observations, statements, decisions and operational logs.
- Officer safety, distress/assistance requests and status monitoring.
- Pursuit/urgent-following interface without owning specialist pursuit policy.
- Task completion, referral, handover, report and return to service.
- Coverage, workload, operational reporting, NPC behaviour and player agency.

### Ownership boundaries

| Concern | Owner | BP-10 relationship |
|---|---|---|
| Police mandate, hierarchy, command authority and policy | BP-05/BP-30 | Consume authority, orders and policy |
| Personnel identity, rank, position, qualification and career | BP-06/BP-07 | Reference authoritative personnel/eligibility |
| Unit membership, duty assignment, roster, remit and deployment | BP-08 | Consume authoritative assignment and deployed unit |
| Vehicles, equipment, availability, issue, maintenance and facilities | BP-09 | Consume current capability/readiness |
| 911 intake, call recording, CAD, radio and dispatch | BP-11 | Receive tasks; return status and field updates |
| Incident master record, classification and command | BP-12 | Create/update through interface; BP-12 owns lifecycle |
| Crime definitions and offence elements | BP-13 | Record provisional classification; do not redefine taxonomy |
| Incident/crime generation | BP-14 | Supply encounters/observations; engine owns occurrence generation |
| Case ownership, objectives and investigative command | BP-15 | Refer and hand over material |
| Investigative methods and decisions | BP-16 | Preserve field actions and execute authorised tasks |
| Victim/witness records | BP-17 | Record contact and immediate needs; BP-17 owns roles |
| Suspect/offender records | BP-18 | Record observed/claimed role; guilt remains separate |
| Interviews/interrogations | BP-19 | Formal interview record belongs to BP-19 |
| Surveillance | BP-20 | Ordinary patrol observation is not covert surveillance |
| Intelligence | BP-21 | Submit observations; BP-21 owns analysis/source grading |
| Scene boundaries, entry log and scene control | BP-22 | Secure/hand over; BP-22 owns formal scene management |
| Exhibit identity and chain of custody | BP-23 | Preserve/hand over property; BP-23 owns continuity |
| Forensic methods and results | BP-24 | Do not infer forensic conclusions |
| Arrest/search/warrant authority | BP-25 | Act within authority; BP-25 owns formal action records |
| Detainee booking and custody | BP-26 | Transfer person and custody information |
| Legal procedure and prosecution | BP-27 | Preserve source records and handoffs |
| Court outcomes | BP-28 | Patrol record never establishes guilt |
| Corrections | BP-29 | No direct ownership |
| Professional standards and complaints | BP-31 | Supply auditable source material |
| Training/qualification | BP-32 | Consume current qualification/restrictions |
| General HR attendance/leave | BP-33 | Consume authoritative attendance/eligibility |
| Finance and procurement | BP-34 | No budget/purchase/payroll ownership |
| World causality and NPC processing | BP-35 | Execute through engine contracts |
| Relationships/social context | BP-36 | Consume relevant context without stereotyping |
| Authoritative clock, schedules and pause | BP-37 | Consume canonical simulation time |
| Records and persistence | BP-38/BP-39 | Store through canonical record contracts |
| Interface and optional maps | BP-40 | Supply structured data; text remains authoritative |
| Notifications and reporting | BP-41 | Publish field-status events |
| Security and permissions | BP-42 | Enforce role, knowledge and hidden-truth boundaries |
| QA and configuration | BP-43/BP-44 | Test and version patrol policy/configuration |

BP-10 owns patrol execution and field-operation records. It does not own dispatch, incident/case lifecycle, legal powers, evidence custody, staff identity, deployment, resource inventory, city geography or the authoritative clock.

## 3. Binding invariants

1. Saltwater is one fictional sovereign city-state, one city and one police jurisdiction. No patrol route or response creates another playable territory.
2. The hard cap is 10,000 living people total, including police. Patrol cannot create uncounted officers, callers, witnesses, bystanders or responders.
3. Police is the deepest simulation; supporting systems remain proportionate but causally credible.
4. Text is the complete primary interface. Maps/visuals are optional and derived from canonical records.
5. No simulation time advances while the player is outside the simulation. Movement, shifts, response clocks, weather, NPC activity and timers freeze.
6. The player controls their officer's consequential actions. No automatic case-solving or hidden-truth disclosure.
7. Never reveal a perpetrator, accomplice or culprit unless the player types exactly bingo. Do not provide unsolicited solution hints or tell the player what to investigate next.
8. Every material operational event has stable identity, provenance, actor/source, simulation time, location and chronology.
9. Observation, allegation, report, inference, intelligence, evidence and proven finding remain separate.
10. NPCs cannot know facts unavailable through observation, communication, authorised briefing or permitted records.
11. Officer location and availability reconcile with travel, assignment, attendance, vehicle and active tasks.
12. BP-09 is authoritative for resource readiness. A patrol plan cannot create a vehicle, equipment, communications coverage or staffing.
13. Dispatch does not erase existing commitments or make an unavailable unit available.
14. Routes and travel times are plausible under canonical roads, access, restrictions, conditions and time.
15. No officer occupies incompatible locations or duties. Planned roster, attendance, availability and current task are distinct.
16. Patrol presence may influence opportunity, reassurance, deterrence and discovery probabilistically; it guarantees none.
17. A field contact does not establish criminality. Personal characteristics cannot be automatic guilt indicators.
18. Corrections append attributable amendments; original content/history remain preserved.
19. Player and NPC officers use the same authority, capability and information rules.
20. This document authorises no Neon write, schema change, seed, import, bulk population or simulation-time advancement.

## 4. Operational concepts

### 4.1 Patrol assignment
An authoritative BP-08 deployment record consumed by BP-10. It identifies assigned officers, unit, duty period, supervisor, function, area/beat, capability and assignment state. BP-10 may hold task details but cannot independently change official posting or roster.

### 4.2 Patrol activity
A bounded action or period: beat patrol, directed patrol, foot/mobile patrol, public contact, welfare check, traffic patrol, static post, reassurance visit or response. Records purpose, actor(s), time, location, mode, tasking source and outcome.

### 4.3 Field task
A discrete operational commitment that can be assigned, accepted, underway, paused, escalated, completed, cancelled or handed over. It may originate from dispatch, supervisor, incident command, planned patrol, self-initiated encounter or authorised referral. It is not necessarily a separate incident or case.

### 4.4 Patrol presence
Actual or estimated operational presence derived from route, movement, status and location events. Planned presence is not actual presence. Confidence reflects source quality.

### 4.5 Field observation
A contemporaneous account of something perceived, with observer, sensory channel, location, time, conditions, description, confidence/limitations and source. It is not automatically a verified fact.

### 4.6 Encounter/contact
An interaction with persons, vehicles or organisations. Records why it occurred, initiator, participants, authority/purpose, timeline, information communicated, actions, outcome and referral. Contact does not imply detention or suspicion.

## 5. Entities and records

All identifiers are stable and non-semantic unless a display code is explicitly defined. Exact physical schema is deferred to implementation.

### 5.1 Beat/patrol area
Fields: beat_id, canonical geographic reference and boundary version, name/code, responsible unit/supervisor, coverage objectives, access restrictions, hazards, route dependencies, effective dates, configuration version and provenance. BP-02 owns geometry; BP-08 owns unit remit; BP-10 owns operational objectives/overlays only.

### 5.2 Patrol plan
Fields: plan_id/version, author/approver, effective duty/time window, assigned unit/officer, target beats, coverage priorities, mode, planned route/checkpoints, objectives, restrictions, risk notes, required capabilities/resources, dependencies, cancellation/review state, actual execution linkage and variance explanation. A plan is not proof of execution.

### 5.3 Patrol activity
Fields: activity_id/type/status, officer/unit, supervisor, assignment/task/incident links, start/end, event chronology, start/end location, route, mode, vehicle/resource references, objective, authority/policy version, observations, contacts, actions, outcome, interruptions, handovers and variance reasons.

### 5.4 Field task
Fields: task_id/type, origin (dispatch, supervisor, incident command, planned patrol, self-initiated or referral), priority/reason, requester/authoriser, assigned unit/officer, acceptance/status, required location/capability/resource, constraints, due/response target, linked incident/case/contact/scene, updates, completion, cancellation and handover.

### 5.5 Officer operational state
BP-10 consumes personnel, roster and deployment state and records field-operational state: available, assigned, en route, on scene, engaged, assisting, transporting, at station, authorised rest, temporarily unavailable, distress, off duty or unknown. This is not the authoritative employment/attendance record.

### 5.6 Movement event
Fields: event_id, officer/unit/vehicle, origin/destination or road-segment reference, start/end simulation time, mode, route, measured/estimated travel, source (officer, telemetry, dispatch or engine), confidence, limitations, interruption/deviation and reason.

### 5.7 Contact
Fields: contact_id/category, participants and roles, initiating source/purpose, location/time, interaction timeline, authority/policy reference, actions, attributed words/claims, observations, person/vehicle identifiers as known then, outcome, referral, linked records, source reliability and correction history.

### 5.8 Observation/field note
Fields: observation_id, observer/source, subject/event/object, time/location, observer's description, lighting/weather/distance/duration/obstruction/noise, sensory channel, recording method, certainty/limitations, contemporaneous/retrospective status, related task/incident/case, visibility class and access controls.

### 5.9 Traffic/roadside event
Fields: traffic_event_id/type, location/road segment/time, vehicle/person references, reason and initiating observation, authority/task, safety positioning, interaction, checks/results with provenance, warning/direction/enforcement/referral, hazards/obstruction/collision/assistance and closure.

### 5.10 Assistance/distress event
Fields: assistance_event_id, requesting and receiving officer/unit, location/time, urgency/reason, known risks/uncertainty, acknowledgement, response/arrival, support, stand-down/handover and communication failures.

## 6. Patrol modes

Support these configurable modes without assuming every unit has every capability:
1. General beat patrol.
2. Mobile patrol.
3. Foot patrol.
4. Cycle or other approved mode.
5. Directed patrol.
6. High-visibility patrol.
7. Reassurance/community patrol.
8. Traffic patrol.
9. Static post/guard.
10. Event patrol.
11. Specialist patrol.
12. Incident response.
13. Area search/containment support under authorised task and explicit boundaries.
14. Welfare/assistance patrol.
15. Self-initiated activity.
16. Training/familiarisation patrol, distinguished from live operational coverage.

A patrol label describes function, not legal authority. It never grants search, detention, entry, surveillance or enforcement powers.

## 7. Beats, coverage and planning

### 7.1 Beat model
A beat references canonical BP-02 geography and may represent a neighbourhood, sector, corridor, transport node, waterfront/industrial area or other grounded city area. Beats may overlap for specialist/time-limited purposes only with explicit ownership and boundary version.

Attributes: canonical area/geometry version, operational name/code, coverage unit/supervisor, demand context (not deterministic crime prediction), access/route constraints, priority periods, objectives, checkpoints, configured target presence, active state and effective dates.

### 7.2 Coverage planning
Consider actual staffed units and attendance; qualifications/team composition/supervision; resource readiness; geography/travel; historical demand without treating it as certainty; current incidents; public events, closures, hazards and weather; workload/fatigue; minimum service obligations; and command priorities. Show assumptions, constraints, uncovered areas and competing commitments. A nominal unit assignment does not prove beat coverage.

### 7.3 Planned versus actual route
A planned route may contain ordered road segments, checkpoints, zones and dwell targets. Actual route derives from movement events and may differ. Record deviations, interruptions, emergency tasking, road closures, access barriers and reasons where known. Route variance alone does not imply misconduct.

### 7.4 Checkpoints
A checkpoint is a location/time objective, not a teleport. Record planned window, arrival/absence, confirmation method, dwell, officer and exception. Missed checkpoints create reviewable exceptions only under policy; they do not prove neglect.

### 7.5 Presence effects
Visibility may probabilistically influence perception, reporting, deterrence opportunity or offender behaviour. Effects are bounded, causal and non-deterministic. Presence does not guarantee prevention, detection, reassurance or witness reporting. No recorded crime does not prove effectiveness.

## 8. Shift activation, briefing and handover

BP-08 owns assignment; BP-33 attendance; BP-37 time. BP-10 starts activity only after eligibility and attendance conditions are met.

Start-of-duty: confirm attendance/assignment, supervisor/command channel, vehicle/equipment readiness from BP-09, current commitments, area priorities, safety notices, briefing source and constraints. Acknowledgement does not imply comprehension beyond what is recorded.

Handover captures active tasks, locations, known risks, persons needing assistance, equipment/property custody, scene status, traffic hazards, outstanding calls, resource state and instructions. Identify outgoing/incoming personnel and time. Incoming personnel acknowledge receipt or record refusal/exception. Handover does not erase earlier accountability.

End of duty: active tasks are completed, handed over, returned or escalated under policy. Equipment return uses BP-09. BP-08/BP-33 own deployment/attendance closure. Do not force implausible task completion solely to end a shift.

## 9. Task intake, acceptance and prioritisation

Task origins include CAD/dispatch, incident command, supervisor direction, planned objective, self-initiated encounter, specialist request, authorised interagency request and case/investigation field task.

Acceptance records receiving unit/officer, time, task version, current state, estimated availability and limitation. Acknowledgement is not acceptance. Unaccepted, rejected, queued and reassigned tasks remain visible.

BP-11/BP-12 own authoritative priority/command decisions. BP-10 exposes actual commitments, travel and capability. Conflicts require an authorised choice: continue, reassign, defer, request assistance, split, cancel or hand over. A new task does not automatically cancel an existing one. Record displaced tasks and consequences.

Self-initiated tasks require an observable trigger, purpose, urgency, duration, authority, resource implications and required notification. Player chooses optional actions; NPCs act under policy and their knowledge.

## 10. Travel, response and arrival

Travel time derives from BP-02 geography, BP-17 road/transport state, BP-35 environmental/world effects and BP-37 time. Factors include road network, direction/turn restrictions, closures, congestion, collisions, hazards, mode/vehicle, access barriers, weather, visibility, response mode and starting-location confidence.

Travel estimates must be plausible and reproducible under identical authoritative state/configuration where deterministic calculation is required. Do not invent precise coordinates or second-level certainty from vague reports.

Support ordinary, priority and emergency response only under configured fictional policy. Response mode changes route/arrival estimates and risk; it does not bypass collisions, closures or resource limits. Special driving permissions, equipment and qualifications come from BP-05/BP-06/BP-08/BP-09/BP-32.

En route begins when an accepted task's movement actually commences. Record dispatch, acceptance, departure and arrival separately. Delays, diversions, stops and communication loss update status/ETA. Never backdate arrival.

Arrival records location/time, source/confidence and whether the officer is at reported address, access point or perimeter. Being at a street address is not proof of reaching the precise incident location.

## 11. Dynamic assessment and decision-making

Assess immediate threat to life/safety; ongoing violence/escalation; medical need/vulnerability; reported/observed weapons or hazards; number/location of persons; environmental/access hazards; scene integrity; need for police/ambulance/fire/specialist support; authority/policy limits; options; uncertainty and conflicting accounts.

Separate:
- directly observed fact;
- attributed statement/allegation;
- information received via radio/CAD;
- inference/risk assessment;
- unknown/not checked;
- decision and rationale.

Risk ratings are aids, not truth. Do not fabricate certainty or force an action. Player choices and NPC decisions retain their knowledge basis and consequences. Later information cannot be retroactively inserted into earlier knowledge.

## 12. Field workflows

Field actions are generic records with action type, actor, authority, time, location, purpose, participants, inputs, result, limits and linked record. Specific powers/process ownership remain elsewhere.

### 12.1 Initial attendance
Confirm task/location, assess safety and urgent needs, request support, identify persons as known, preserve observations, determine scene-control/referral need, update dispatch/command and record actions/decisions/status.

### 12.2 Public assistance and welfare
Record request/reason, identity/anonymous status as known, immediate need, communication, assistance, consent/refusal where relevant, referral, safeguarding concern and outcome. Do not invent diagnosis or sensitive detail. BP-17 owns victim/witness records where applicable.

### 12.3 Public order and conflict
Record observed behaviour, participants, location/time, communication/de-escalation, directions, support, actions, injuries/damage and referral. Distinguish peaceful assembly, disagreement, nuisance, disorder and violence. BP-12/BP-13/BP-25 own incident/offence/action classification.

### 12.4 Traffic and roadside
Record reason, observed vehicle identification, safe location, traffic conditions, interaction and result. A stop does not imply an offence. Checks/enforcement use authoritative systems and configured authority. Collision, injury or obstruction is handed to BP-12 and relevant emergency partners.

### 12.5 Suspicious circumstances
Record specific observable circumstances prompting attention. Avoid unsupported labels or claims such as known criminal. Preserve the person's account and officer observation separately. Protected or irrelevant characteristics cannot alone generate a contact.

### 12.6 Search for person or vehicle
BP-10 may represent an assigned search task, perimeter observation or area coverage. Grounds, authority, scope, warrant and execution belong to BP-25. A patrol plan/task label creates no search authority. Record areas covered, officers, time, limits, negative results and items/persons located; do not imply completeness if partial.

### 12.7 Scene security and preservation
Immediate protective steps within authority, support request, prevent avoidable disturbance and communicate access. Formal boundary, entry log and scene management pass to BP-22. Exhibit recovery/packaging/continuity pass to BP-23. Mentioning an object does not create an exhibit.

### 12.8 Arrest and detention handoff
BP-25 owns formal action/authority; BP-26 booking/custody. BP-10 preserves patrol timeline, observations, statements, actions, force/injury events and transfer. Task remains open until person and responsibilities are handed over.

### 12.9 Pursuit and urgent following
Record participation, observations, route, status, communications, risk updates, decision references and handover. Dedicated pursuit policy/authorisation/command belongs to BP-05/BP-30/BP-12. Following is not automatically pursuit; proximity/movement alone is insufficient.

### 12.10 Field referral
Refer to BP-12, BP-15/BP-16, BP-17, BP-21 or another owner with source records, urgency, outstanding actions, limitations and recipient. Referral is not accepted/ownership-transferred until acknowledged.

## 13. Officer safety and resilience

Operational status may be updated by officer, radio/CAD, authorised supervisor, approved telemetry or engine event. Record source/time/confidence. Missing or stale status is unknown, not available or safe.

Assistance requests record urgency, location, reason, risks, acknowledgement, response and arrival. Missing acknowledgement triggers configured escalation. Do not create a responder if none exists.

Injury/distress records source, time, response, medical referral and duty impact. Detailed medical records remain in appropriate restricted domains; patrol receives operational restrictions/handoff only.

Communications failure records last confirmed communication, fallback method, attempts and uncertainty. Do not simulate successful delivery. If task requires a partner/supervisor/specialist, check actual available personnel and capability. A lone officer is not silently treated as a team. Exceptions require authority and audit.

## 14. Contacts, observations and information quality

Attribute who said, saw, heard, reported or inferred each material detail. Preserve contemporaneous wording. Summaries cannot convert uncertainty into certainty. Corrections retain original and reason.

Person identity may be unknown, self-reported, document-supported, system-matched or independently confirmed. BP-03 owns identity; BP-18 suspect/offender role; BP-17 victim/witness role. Initial patrol identification is not automatically authoritative.

Vehicle registration/description as observed and check result are separate. Plates may be misread, duplicated or associated with another vehicle. Do not silently resolve uncertainty.

Negative observations are bounded by observer, place, time, duration, visibility and method. A short/obstructed observation cannot establish universal absence.

If body-worn or other recording is assigned and operational under BP-09/policy, record device ID, activation/deactivation, gaps, malfunction, upload/reference and access restrictions. BP-23 owns evidential continuity; BP-38 records. Recording does not prove completeness.

## 15. Task completion and closure

Statuses: completed with outcome; completed/no further action; partially completed; handed over; cancelled by authorised actor; superseded/reassigned; unable due to resource/access/safety/other constraint; suspended pending defined trigger.

Closure requires final status/time, participants, location/movement endpoint, actions/decisions, contact/observation/incident links, outstanding risks/actions, property/equipment custody, handover recipient, incomplete/cancelled reason and report/supervisor-review references.

Completing a patrol task does not close linked incident, case, investigation, custody or court process.

## 16. Performance, coverage and accountability

Reports may include planned versus actual patrol time/area, route/checkpoints, response/arrival intervals with clock definitions, workload/interruptions, resource/staffing constraints, contacts/assistance/referrals, incidents, public feedback, safety events and report completion.

Raw contact/stop counts, arrests or enforcement totals are not quality measures. Absence of reported crime is not proof of deterrence. Route compliance alone does not establish effectiveness. Response metrics disclose start/end definitions, hold states and data quality. Comparisons account for geography, task complexity, staffing and constraints. Supervisory metrics cannot infer misconduct from a single indicator; BP-31 owns formal conduct processes.

## 17. NPC behaviour and player agency

NPC actions depend on assignment, authority, training, policy, attendance, workload, resources, known tasking, briefings, observations, permitted records, geography, weather, risk and competing obligations. NPCs cannot access hidden case truth or records unavailable to them. Their actions may be imperfect, delayed or mistaken.

NPCs may conduct routine patrol, respond, seek help, make contacts, record observations and refer within authority. Consequential actions retain rationale and knowledge basis. They cannot silently solve a case, reveal a culprit or decide for the player.

The player interface presents current task, location, state, known information, resources, orders and options. Consequential actions require explicit player input. If an action is outside authority/capability/context, explain the constraint without silently substituting another action.

Do not append unsolicited advice such as investigate a named person next. Present only information and operational options legitimately available to the officer. The player determines investigative direction.

## 18. Inputs, outputs and event contracts

### Inputs
- BP-02: canonical location, roads, access points, geometry and boundaries.
- BP-05/BP-30: authority, command orders, policy and delegation.
- BP-06/BP-07/BP-08: identity, qualifications, duty, assignment, attendance and unit capability.
- BP-09: vehicle/equipment/facility readiness, custody and availability.
- BP-11: call, dispatch, radio, task and status messages.
- BP-12: incident details, priority, command and coordination.
- BP-13/BP-14: offence/incident classification and generated occurrences.
- BP-15/BP-16: case references, authorised field tasking and investigative handoffs.
- BP-17/BP-18/BP-19: person roles and formal interview/statement handoffs.
- BP-20/BP-21: surveillance/intelligence task references and restrictions.
- BP-22/BP-23/BP-24: scene, exhibit and forensic interfaces.
- BP-25/BP-26: arrest/search authority and custody transfer.
- BP-32/BP-33: qualification and attendance/leave restrictions.
- BP-35/BP-36: causal world activity and relevant social context.
- BP-37: canonical time and pause.
- BP-38/BP-39/BP-42: records, persistence and access contracts.

### Outputs
Patrol plans/activity/coverage; field task lifecycle; movement and operational status; arrival, contact, observation and field-note records; traffic/roadside events; assistance/distress; incident updates and field reports; scene/evidence/person/intelligence/case referrals; resource constraints; supervisory notifications and operational reports.

### Event envelope
Every event has event_id/type, schema_version, subject_id, source/actor, effective simulation time, recorded time, location, task/assignment reference, authority/policy version, provenance, visibility class, idempotency key and prior/resulting record version. Cross-division events use stable references and explicit acknowledgement where ownership changes.

Core event types: PatrolPlanCreated/Approved/Amended/Cancelled; PatrolActivityStarted/Updated/Interrupted/Completed; FieldTaskCreated/Assigned/Accepted/Rejected/Started/Paused/Resumed/Completed/Cancelled/HandedOver; OfficerStatusChanged; UnitStatusChanged; MovementStarted/Updated/Interrupted/Completed; CheckpointReached/Missed; FieldObservationRecorded/Amended; ContactStarted/Updated/Ended; TrafficEventStarted/Updated/Ended; AssistanceRequested/Acknowledged/Dispatched/Arrived/Closed; FieldAssessmentRecorded; IncidentUpdateRequested/Accepted/Rejected; SceneHandoverRequested/Acknowledged; CustodyHandoverRequested/Acknowledged; PatrolReportSubmitted/Reviewed.

## 19. Permissions and information boundaries

BP-42 owns access control. Roles include patrol officer, acting supervisor, shift supervisor, unit commander, dispatcher, incident commander, investigator, professional-standards reviewer, administrator and auditor.

- Officers view tasks/records necessary for current duty.
- Supervisors view operational status and records within command remit.
- Dispatch receives location/status/task information needed for coordination.
- Investigators receive referred field material under case access, not unrestricted patrol data.
- Professional standards access is purpose-limited and audited.
- Victim, witness, medical, intelligence and protected-location details retain domain permissions.
- Hidden culprit/accomplice truth is never exposed in player-facing views unless exact bingo condition is met.
- Player cannot inspect NPC private knowledge, sealed briefings or restricted records merely by being in the same unit.
- Read access does not grant amendment, deletion, cancellation or reassignment.
- Restricted access, overrides, reassignment, amendment and exceptional actions are audited.

## 20. Exceptions and edge cases

1. Officer rostered but absent: BP-33/BP-08 control availability; no patrol start.
2. Officer attends but assignment is stale: require authoritative confirmation.
3. Unit below minimum crew: mark constrained; no invented staff.
4. Officer lacks qualification: block restricted task/action.
5. Qualification expired/suspended: ineligible until updated.
6. Vehicle allocated but unserviceable: not dispatchable.
7. Equipment missing/not issued: record limitation; do not assume possession.
8. Communications device fails: degraded/unknown state and fallback.
9. Duplicate dispatch task: idempotency prevents duplicate execution.
10. Priority changes en route: preserve old/new priority, source and time.
11. Unit already committed: expose conflict; authorised decision required.
12. Dispatch location incomplete: clarify or preserve uncertainty; no invented address.
13. Address known but entrance unknown: record discrepancy and locate access within authority.
14. Road closed: recalculate route and preserve delay/source.
15. Travel estimate stale: mark stale and recompute.
16. Reported location conflicts with telemetry: preserve both sources.
17. Location update missing: show last known and age.
18. Route deviates: record known cause; no misconduct inference.
19. Checkpoint missed: configured review, not automatic neglect finding.
20. Plan approved but never started: planned-not-executed.
21. Plan partially executed: actual coverage and outstanding objectives retained.
22. Patrol interrupted by emergency: preserve interruption and original objective.
23. Weather changes: apply canonical event at correct location/time.
24. Poor visibility: qualify observations and estimates.
25. Crowd exceeds plan: report constraints and request support.
26. Person refuses voluntary contact: record refusal; proceed only under separate authority.
27. Anonymous caller/person: preserve anonymous status.
28. Conflicting identity claims: preserve claim and verification state.
29. Misidentification: retain original and correction.
30. Conflicting officer observations: retain both with conditions/time.
31. Auditory-only observation: distinguish from visual confirmation.
32. Partial negative observation: record coverage/limits.
33. Contact becomes formal interview: BP-19 owns process.
34. Contact reveals victim/witness role: refer BP-17; account not automatically verified.
35. Contact raises suspect status: BP-18 owns role; suspicion is not guilt.
36. Possible evidence observed: request BP-22/BP-23; no automatic exhibit.
37. Scene already contaminated: record condition and notify BP-22.
38. Scene handover unacknowledged: responsibility remains visible/open.
39. Arrest authority unclear: do not mark arrest complete; seek clarification.
40. Arrest occurs: BP-25 formal record and BP-26 custody acknowledgement.
41. Detainee transfer delayed: retain responsibility and task.
42. No assisting unit free: record unavailability and escalate.
43. Assistance not acknowledged: show unconfirmed and escalate.
44. Distress location stale: use last confirmed location and show uncertainty.
45. Two incompatible tasks: reject or record authorised reprioritisation.
46. Task outside authority: record refusal/escalation and order source.
47. Conflicting supervisor order: enforce configured precedence and audit.
48. Fatigue/unfitness: apply configured restriction; do not ignore HR/roster state.
49. Vehicle collision: create incident and require inspection.
50. Officer injured: welfare/medical and staffing effects; hand over task.
51. Camera not assigned/fails: record gap; no implied recording.
52. Recording interrupted: preserve gap/device state.
53. Late report: actual submission time; no backdating.
54. Report amended: original and amendment retained.
55. Network outage: durable delivery and replay without duplicate actions.
56. Duplicate event: apply once.
57. Out-of-order events: canonical ordering and received provenance retained.
58. Player exits: freeze patrol movement, timers, NPC actions and time.
59. Player resumes: continue from frozen state; no hidden elapsed time.
60. NPC receives information later: knowledge begins at receipt/observation time.
61. NPC internal hidden truth: never expose to player/officer.
62. Player requests unavailable action: explain constraint; no silent substitute.
63. Unauthorised lookup: deny and audit.
64. Duty ends with active task: hand over, extend under authority or retain active duty.
65. Equipment unreturned: BP-09 custody discrepancy.
66. Task references invalid location: resolve canonical ID or reject.
67. Map versions conflict: BP-02 canonical version prevails.
68. Public event cancelled/relocated: authorised update; preserve prior assignment.
69. Interagency request lacks authority/acceptance: queue or reject.
70. Off-map supplier reference: external context only; no patrol expansion.
71. New person would exceed 10,000 cap: BP-03 blocks creation.
72. Police staffing counted separately: prevent population double count.
73. Patrol consumes stock: BP-09 movement; no negative stock.
74. Task requests absent resource: unavailable and escalated.
75. Handover recipient rejects: current authorised holder retains responsibility.
76. Unauthorised status override: reject and audit.
77. Location confidence low: approximate/unknown, no false precision.
78. Sensitive unrelated information: restrict/minimise dissemination while preserving source.
79. Report alleges officer misconduct: preserve source and refer BP-31; no adjudication.
80. Later review finds decision mistaken: preserve contemporaneous basis and append review.
81. Activity crosses beat boundary: record actual route without duplicate activity.
82. Task cancelled after travel: record cancellation; movement remains.
83. Fuel/charge insufficient: BP-09 readiness update.
84. Specialist capability absent: request specialist; no task-label capability grant.
85. Contact creates non-crime incident: BP-12/BP-13 distinguish it.
86. Call later false/unfounded: preserve call and later outcome.
87. Observation outside assigned beat: record location/reason; no teleport barrier.
88. Urgent task interrupts patrol: preserve lost coverage and rationale.
89. Briefing contains error: preserve source and correction; knowledge changes on receipt.
90. Restricted facility: verify access; no bypass of BP-04/BP-42.
91. Immediate hazard: protective action within authority and auditable referral.
92. Duty restriction changes mid-shift: re-evaluate active task and eligibility.
93. Route crosses private/inaccessible land: reject/recalculate.
94. Task closed with unresolved safety issue: block or require authorised exception.
95. Unsupported conclusion in report: retain as opinion, not fact.
96. Multi-unit task: explicit assignments and shared command.
97. Temporary beat detachment: record authority/time/coverage impact.
98. Approved plan changes: new version and authoriser/reason.
99. Actual presence unknown: do not mark area covered.
100. Person already registered: reuse stable person ID.
101. Materially relevant person: BP-03 permanent promotion; BP-10 references persistent identity.
102. Unverified allegation about business: attribute source; do not alter BP-04 facts.
103. Unsafe stop location: record repositioning and original location.
104. Contact interrupted by urgent task: preserve partial contact and handover.
105. Ambiguous radio message: record uncertainty and clarify.
106. Delayed supervisor instruction: preserve sent/received times.
107. Utility/weather hazard: consume BP-35 state at correct place/time.
108. Player action blocked by equipment/authority/time: explain reason.
109. Metric used to rank officers without context: disclose limitations/prevent unsupported conclusion.
110. Resource changes during task: update feasibility without rewriting task start.
111. Incident location changes after dispatch: preserve old/new and recalculate.
112. Training overlaps patrol: distinguish exercise from operational coverage.
113. Task lacks end condition: retain open and request direction; no auto-close.
114. Unresolved person/property handoff: task/handoff remains open.
115. Case team requests attendance: verify authority, scope and information boundary.
116. Map contradicts text: canonical event/text prevails; log rendering defect.
117. Clock correction: BP-37 owns; preserve original ordering/audit.
118. Incorrect visibility label: audited correction and access history.
119. Historical task references disposed asset: reference remains resolvable.
120. Vehicle/person/location status is stale: mark unknown/stale, not available/current.
121. Task requests multiple resources with one unavailable: partial fulfilment and unmet need visible.
122. Patrol vehicle is shared between shifts: custody and handover explicit.
123. Officer is suspended while on scene: safe relief/transfer and access restrictions.
124. Task is reassigned mid-action: preserve outgoing work and recipient acknowledgement.
125. Officer is sent to a location outside city canon: reject as playable destination.
126. A simulated caller is also an existing resident: reuse person identity and count once.
127. Patrol contact is later linked to a case: preserve source contact and create reference, not duplicate record.
128. NPC reports a fact they could not know: reject or flag knowledge-provenance violation.
129. A patrol route estimate crosses a blocked bridge/road: route engine recalculates or reports no feasible route.
130. A field action has no authority reference where one is required: block completion or mark exception pending review.

## 21. Cross-system effects

- BP-02 owns canonical spatial IDs, roads, access and geometry; BP-10 never authors a competing map.
- BP-05/BP-30 own orders, authority, policy, escalation and command precedence.
- BP-06/BP-07/BP-08/BP-32/BP-33 own identity, career, assignment, qualification and attendance separately.
- BP-09 owns vehicle/equipment/facility availability; BP-10 requests/consumes and reports usage.
- BP-11 owns intake/CAD/radio/dispatch; BP-10 returns acceptance, movement, arrival, updates and clear status.
- BP-12 owns incident priority, command and multi-agency coordination; patrol sends observations/actions and receives instructions.
- BP-13/BP-14 own taxonomy and occurrence generation; patrol discovers/reports, not offence elements.
- BP-15/BP-16 own case/investigation objectives; patrol preserves material and executes authorised tasks.
- BP-17/BP-18/BP-19 own person roles and formal interviews; patrol contact is a source record.
- BP-20/BP-21 own surveillance/intelligence rules; ordinary observation does not bypass them.
- BP-22/BP-23/BP-24 own scene, exhibit and forensic continuity.
- BP-25/BP-26 own arrest/search authority and custody.
- BP-31 consumes immutable source records for complaints/conduct.
- BP-35/BP-36/BP-37 own causality, social context and time; pause freezes all time-dependent activity.
- BP-38/BP-39 own records and persistence.
- BP-40/BP-41 present authorised views/notifications.
- BP-42 enforces security/hidden-truth boundaries; BP-43 tests; BP-44 controls configuration changes.

## 22. Acceptance tests and evidence

All tests use fictional fixtures and controlled simulation time. Evidence includes fixture IDs, policy/config version, source events, expected/actual state, actor, effective time, provenance and reproducible result.

| ID | Scenario | Required result |
|---|---|---|
| PAT-001 | Start with valid attendance/assignment/capability | Correct activity, officer, unit, time and location |
| PAT-002 | Rostered officer absent | No patrol start |
| PAT-003 | Stale assignment | Block pending authoritative resolution |
| PAT-004 | Approved plan never executed | Planned/actual distinct |
| PAT-005 | Amend patrol plan | Version, authority and history preserved |
| PAT-006 | Route uses canonical roads | Segments resolve to BP-02 |
| PAT-007 | Closed/inaccessible route | Reject/recalculate; no teleport |
| PAT-008 | Travel with congestion/weather | Plausible constraints applied |
| PAT-009 | Planned versus actual route | Deviation/source retained |
| PAT-010 | Checkpoint reached | Time/location/method recorded |
| PAT-011 | Checkpoint missed | Exception, not automatic misconduct |
| PAT-012 | No confirmed patrol presence | Area not marked covered |
| PAT-013 | Directed patrol | Purpose, authority, area and time |
| PAT-014 | Patrol visibility effect | Bounded probability, no guarantee |
| PAT-015 | Receive dispatch task | Acceptance and chronology recorded |
| PAT-016 | Duplicate dispatch | Idempotent; no duplicate execution |
| PAT-017 | Unit already committed | Conflict and authorised resolution |
| PAT-018 | Priority changes en route | Old/new source/time preserved |
| PAT-019 | Unit departs | Departure distinct from dispatch/acceptance |
| PAT-020 | At address, not access point | Arrival discrepancy retained |
| PAT-021 | Cancel after movement | Cancellation and movement preserved |
| PAT-022 | Self-initiate task | Trigger, purpose, authority, notification |
| PAT-023 | Self-initiate outside authority | Block/escalate |
| PAT-024 | Public assistance contact | Request, action, refusal/consent and outcome |
| PAT-025 | Anonymous person | No invented identity |
| PAT-026 | Voluntary contact refusal | No implied detention |
| PAT-027 | Suspicious circumstance | Observable basis, no guilt inference |
| PAT-028 | Conflicting observations | Both accounts retained |
| PAT-029 | Limited negative observation | Limits preserved |
| PAT-030 | Unverified identity | Claim/check remain distinct |
| PAT-031 | Uncertain registration | Observation and check separate |
| PAT-032 | Unsafe traffic stop | Reposition and chronology retained |
| PAT-033 | Roadside collision | BP-12 handoff and traffic status |
| PAT-034 | Specialist task | Capability checked; no fabrication |
| PAT-035 | Request assistance | Request/acknowledgement/dispatch/arrival distinct |
| PAT-036 | No assistance available | Constraint; no invented responder |
| PAT-037 | Assistance not acknowledged | Unconfirmed and escalation |
| PAT-038 | Stale officer status | Unknown/last confirmed, not available |
| PAT-039 | Officer distress | Assistance workflow and audit |
| PAT-040 | Communications outage | No false delivery; fallback recorded |
| PAT-041 | Missing qualification | Restricted task blocked |
| PAT-042 | Qualification suspended mid-task | Eligibility rechecked and handover |
| PAT-043 | Vehicle unserviceable | BP-09 readiness consumed |
| PAT-044 | Patrol consumes stock | BP-09 movement; no negative stock |
| PAT-045 | Missing equipment | Request unavailable |
| PAT-046 | Initial scene protection | BP-22 handoff; no duplicate scene |
| PAT-047 | Possible evidence | Observation; exhibit only via BP-23 |
| PAT-048 | Scene handover unacknowledged | Responsibility open/visible |
| PAT-049 | Arrest | BP-25 formal record; patrol timeline |
| PAT-050 | Custody transfer | BP-26 acknowledgement required |
| PAT-051 | Formal interview starts | BP-19 owns interview; contact retained |
| PAT-052 | Intelligence report | BP-21 source attribution; no conflation |
| PAT-053 | Surveillance task | BP-20 authorisation/ownership |
| PAT-054 | Case referral | Recipient acknowledgement and source refs |
| PAT-055 | Partial completion | Outstanding actions retained |
| PAT-056 | End shift with active task | Handover/extension/escalation |
| PAT-057 | Equipment not returned | BP-09 discrepancy |
| PAT-058 | Handover to incoming unit | Parties/time/content/acknowledgement |
| PAT-059 | Briefing received after event | Knowledge begins on receipt |
| PAT-060 | NPC chooses field action | Available knowledge/authority/resources only |
| PAT-061 | Player consequential choice | No execution without input |
| PAT-062 | Player asks unavailable action | Explain constraint; no substitute |
| PAT-063 | Unauthorised lookup | Deny and audit |
| PAT-064 | Hidden culprit exists internally | No player disclosure absent exact bingo |
| PAT-065 | Materially connected person | BP-03 permanent promotion/reference |
| PAT-066 | Population cap reached | New person blocked |
| PAT-067 | Player exits | All patrol time/activity freezes |
| PAT-068 | Player resumes | No hidden elapsed time |
| PAT-069 | Duplicate event replay | Idempotent |
| PAT-070 | Out-of-order events | Deterministic reconciliation/provenance |
| PAT-071 | Engine replay | Same authoritative state when deterministic |
| PAT-072 | Report amended | Original and amendment retained |
| PAT-073 | Late report | Actual time; no backdating |
| PAT-074 | Conduct complaint | BP-31 source; no BP-10 adjudication |
| PAT-075 | Performance metric | Definition/context/limitations |
| PAT-076 | Map contradicts text | Canonical record prevails |
| PAT-077 | Low location confidence | Approximate/unknown, no false precision |
| PAT-078 | Multi-unit task | Assignments/command/chronology explicit |
| PAT-079 | Beat detachment | Authority/time/coverage impact |
| PAT-080 | Utility/weather disruption | BP-35 correct place/time |
| PAT-081 | Unauthorised interagency request | Queue/reject |
| PAT-082 | New person breaches cap | BP-03 blocks |
| PAT-083 | Police headcount duplicated | Population reconciliation |
| PAT-084 | Invalid location | Resolve canonical ID or reject |
| PAT-085 | Duty restriction mid-shift | Re-evaluate task/eligibility |
| PAT-086 | Unverified claim in assessment | Attributed and unverified |
| PAT-087 | Later review finds error | Original basis preserved |
| PAT-088 | Handover rejected | Current owner retains responsibility |
| PAT-089 | Historical disposed vehicle | Reference remains resolvable |
| PAT-090 | Full task lifecycle | Auditable and reproducible |

## 23. Non-functional requirements

- Temporal integrity: one authoritative clock; distinct dispatch, acceptance, departure, arrival, action and report times.
- Spatial integrity: canonical geography and route constraints; no teleportation or external playable territory.
- Operational truthfulness: planned, assigned, dispatched, accepted, underway, arrived and completed are distinct.
- Epistemic integrity: source, observation, allegation, inference, intelligence, evidence and finding remain separate.
- Player agency: consequential player actions require explicit choice.
- NPC realism: knowledge, authority, capability, workload and resources bound behaviour.
- Population integrity: all persons counted once under BP-03; hard cap 10,000 including police.
- Resource integrity: BP-09 controls actual vehicles, equipment, stock and facilities.
- Auditability: decisions, status changes, overrides, handovers and amendments have actor/time/reason.
- Replay safety: duplicate events do not duplicate tasks, movement, reports or stock consumption.
- Performance: relevance-based processing cannot erase records, break causality or downgrade permanently promoted persons.
- Storage efficiency: shared catalogues and stable references; do not duplicate personnel, person, property, road, vehicle, finance, evidence or case masters.
- Security: purpose-limited access; protected person/case data not exposed in general patrol views.
- Resilience: delayed messages/service failures are durable, visible and recoverable.
- Explainability: show why a task cannot start, route is delayed or unit unavailable.

## 24. Source traceability

Primary source mappings:
- S02 geography/spatial reference: canonical operational locations, roads, boundaries and optional maps.
- S17 roads/transport/mobility: route feasibility, movement and response constraints.
- S19 environment/weather/hazards: time/location-valid effects on visibility, travel and safety.
- S22 emergency services/civil protection: multi-agency handoffs and chronology.
- S23 police governance/structure: mandate, command and authority.
- S25 rosters/staffing/deployment: actual attendance, staffing and task compatibility.
- S27 911/CAD/dispatch: task intake and auditable status transitions.
- S28 patrol/response/field operations: patrol presence, proactive activity, response, contact, traffic and field decisions.
- S29 incident/crime taxonomy/generation: occurrence/report/allegation/offence distinctions.
- S30 case management/investigative command: task and case handoffs.
- S32 scene/evidence collection: scene preservation and evidence referrals.
- S35 intelligence/analysis: source and confidence separation.
- S37 arrest/search/warrants/custody: formal authority and custody interfaces.
- S41 time/calendar/schedules: canonical time and pause.
- S42 simulation engine/causality: coherent world activity.
- S45 maps/diagrams/visual evidence: optional visuals derived from canonical data.
- S48 security/permissions: least privilege, secrets and hidden-truth boundary.
- S51 operations/observability: health, errors and recovery.

The unchanged source JSON remains authoritative for original wording. The 52-to-44 crosswalk maps every source requirement/test. A mapping is not complete design: BP-10 must incorporate applicable requirements or explicitly identify the authoritative owner/interface.

## 25. Open decisions

1. Exact beat/sector count, names, boundaries and unit responsibility.
2. Patrol staffing and minimum crew composition by task/time.
3. Patrol mode availability by unit and qualification.
4. Coverage objectives, priority windows and minimum service standards.
5. Route/checkpoint design and deviation thresholds.
6. Response modes, activation authority and risk controls.
7. Patrol visibility/encounter influence parameters.
8. Public-contact categories, recording thresholds and report requirements.
9. Traffic-stop and roadside workflow detail within fictional policy.
10. Officer status/check-in intervals and stale-location thresholds.
11. Assistance/distress priority, acknowledgement and escalation timers.
12. Fatigue/workload thresholds and BP-33 interaction.
13. Handover requirements and task ownership at shift end.
14. Supervisor review thresholds for route variance, missed checkpoints and delayed reports.
15. Body-worn recording rules and exceptions.
16. Interagency request/acceptance and shared command procedures.
17. Specialist patrol categories and capability catalogue.
18. Performance measures, denominators and reporting intervals.
19. Deterministic route/travel simulation versus bounded estimation.
20. Retention/access for routine contact and patrol location telemetry.
21. Urgent response/pursuit thresholds; BP-10 does not invent them.
22. Task priority conflict arbitration and override authority.
23. Text-first presentation of planned coverage versus actual presence.
24. NPC initiative and supervisor notification rules.
25. Which routine field reports require review before closure.

Do not invent permanent beat counts, staffing quotas, route geometry, fleet quantities, response-time guarantees or legal thresholds while unresolved. Use canonical references and configurable policy with explicit owners.

## 26. Completion criteria

BP-10 moves to DESIGNED only after all mapped source requirements/tests are checked against the unchanged source JSON and incorporated or explicitly assigned; interfaces with BP-08/BP-09/BP-11/BP-12/BP-15/BP-16/BP-22/BP-23/BP-25/BP-26 are reconciled; authority/time/spatial/population/hidden-truth/player-agency invariants are validated; open decisions are resolved or accepted as configurable with owners; tests have unambiguous setup/action/expected result/evidence; and the user approves.

Implementation, testing and verification remain separate. This specification authorises no Neon schema change, migration, seed, import, bulk records or database write.
