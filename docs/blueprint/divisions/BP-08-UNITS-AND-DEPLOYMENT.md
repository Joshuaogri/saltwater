# BP-08 — Units and Deployment

**Project:** Saltwater, fictional sovereign city-state; one city and one jurisdiction  
**Blueprint division:** BP-08 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test:** NOT_STARTED | **Verification:** NOT_STARTED

## 1. Purpose

Define the police organisational unit catalogue, unit lifecycle, command and supervisory assignment, establishment and staffing allocation, personnel-to-unit membership, posting, temporary attachment, specialist capability, deployment authority, operational availability, geographic responsibility, inter-unit coordination, deployment history and unit-level readiness.

BP-08 answers: **which police units exist, what they are authorised and equipped to do, who belongs to them, who commands them, and how personnel are assigned or deployed across the city**.

It must support a coherent, active police service across Saltwater's single city. It must support routine geographic patrol, response, investigation, specialist support, command, custody-related functions and administrative services without assuming every unit is simultaneously staffed or available. Unit names and final hierarchy are configurable policy, not invented canon.

## 2. Scope and authoritative boundaries

### In scope
- Unit catalogue, types, functions, mandates, geographic remit and lifecycle.
- Parent/child unit relationships and reporting structure.
- Commanding officer, deputy, supervisors and acting command assignments.
- Approved establishment: authorised posts, grades/ranks, staffing targets and capacity.
- Personnel membership, primary/secondary affiliation, posting and attachment intervals.
- Deployment eligibility, capability, availability and restriction evaluation.
- Routine, temporary, surge, event, emergency and cross-unit deployment.
- Geographic coverage, beat/sector responsibility and handover of responsibility.
- Unit readiness and capability summaries derived from personnel and resources.
- Deployment orders, acknowledgements, changes, cancellation, relief and completion.
- Unit history, audit, performance summaries and operational interfaces.

### Exclusions and owners

| Concern | Owner | BP-08 relationship |
|---|---|---|
| Overall institutional architecture and rank/position/authority catalogues | BP-05 | Uses approved structure and authority |
| Individual identity, personnel master and employment status | BP-06 | References personnel records |
| Career progression, substantive rank and acting-career history | BP-07 | Consumes career eligibility and appointment outcomes |
| Vehicles, equipment, facilities, communications devices and inventory | BP-09 | Consumes availability/capability references |
| Patrol activity, patrol task execution and field tactics | BP-10 | Receives deployment assignments and returns status |
| Call-taking, CAD queue, dispatcher workflow and radio | BP-11 | Receives resource availability and dispatch status |
| Incident command and incident lifecycle | BP-12 | Supplies incident-specific operational tasking |
| Case assignment and investigative direction | BP-15/BP-16 | Receives authorised investigative allocation |
| Specialist training and qualification awards | BP-32 | Consumes verified qualification status |
| HR transactions, leave and employment administration | BP-33 | Consumes authoritative status/availability events |
| Canonical time, calendar, recurrence and schedule execution | BP-37 | Consumes temporal services; BP-08 remains owner of police roster content and duty assignment |
| Unit/personnel persistence and records | BP-38/BP-39 | Stores canonical records and history |
| Permissions and protected assignments | BP-42 | Enforces visibility and action authority |

BP-08 owns the organisational membership, planned police duty roster and deployment assignment records. It does not own canonical clock/calendar or schedule-execution services (BP-37), personnel identity or service history (BP-06), actual attendance and leave records (BP-33), substantive career/rank progression (BP-07), resource inventory/readiness (BP-09), or the operational execution of a patrol/call/case task (BP-10/BP-11/BP-12). BP-37 supplies temporal and recurrence services; BP-08 owns the police roster's staffing and assignment content; BP-33 records actual attendance/leave, which may differ from the plan.

## 3. Governing invariants

1. Every unit has a stable unique ID, controlled type, mandate, lifecycle state and accountable parent or explicitly declared top-level status.
2. A unit's existence does not imply it is staffed, equipped, open, on duty or operationally available.
3. Every person assigned to a unit references one BP-06 personnel identity. No duplicate personnel are created by posting or attachment.
4. Substantive rank, position, career appointment, unit membership, supervisor relationship, operational command and temporary tasking remain separate records.
5. Unit membership does not itself confer rank, legal powers, clearance, qualification or authority.
6. No assignment may exceed approved establishment or bypass required rank, qualification, clearance, fitness, duty-status or resource constraints unless a recorded authorised exception permits it.
7. A unit cannot command itself through a circular hierarchy; parent-child relationships must be acyclic and valid.
8. A person cannot hold incompatible simultaneous primary postings. Secondary membership and temporary attachments require explicit compatibility rules and effective intervals.
9. Deployment is time-bounded or explicitly ongoing, has an authority/source, scope, destination/function and accountable supervisor, and is recorded in history.
10. An operational deployment cannot silently change the person's substantive rank, position or permanent unit.
11. Deployment orders cannot make an unavailable, suspended, deceased, separated or otherwise ineligible person operationally available.
12. A deployment must not exceed the authority of the issuing officer or the delegated powers of the deployed person.
13. Unit readiness is derived from current verified personnel/resource/qualification/availability inputs; it is never a manually asserted guarantee that a unit can perform every task.
14. Geography is limited to the single sovereign city-state of Saltwater. No unit may establish jurisdiction over another city, country or external territory.
15. No simulation time advances while the player is absent. Membership and deployment durations, rotation, temporary attachments and scheduled transitions freeze with the simulation clock.
16. Every material change is attributable, versioned and historically recoverable. Corrections supersede; they do not erase.
17. Player and NPC personnel are governed by the same unit and deployment rules.
18. The hard population cap remains 10,000 living people total, including police personnel. Unit creation does not create people; recruitment is controlled by BP-03/BP-33.
19. Hidden case facts and offender identities must not be exposed through unit rosters, deployment screens or operational summaries without legitimate access. The exact command bingo remains the only reveal trigger for culprit/accomplice/perpetrator identity.
20. The fixed 44-division blueprint structure is not changed by this specification.

## 4. Unit catalogue and organisational model

### 4.1 Unit record

Minimum fields:
- unit_id: stable opaque identifier;
- unit_code: human-readable controlled code, unique within its namespace;
- official_name and short_name;
- unit_type_id and functional_domain;
- mandate, authorised functions and prohibited functions;
- parent_unit_id, hierarchy path/projection and reporting destination;
- lifecycle_state and effective start/end;
- geographic remit references (citywide, district, sector, beat, facility or case/task scoped);
- command post/position reference from BP-05;
- authorised establishment reference and staffing capacity;
- capability profile and prerequisite qualifications;
- access classification and operational sensitivity;
- policy version, record version, provenance and audit metadata.

Names/codes may change under controlled change; unit_id does not. A disbanded unit is closed, not deleted. Re-establishing a unit may create a new unit ID or a formally versioned successor relationship; it must not silently reuse the old identity.

### 4.2 Unit types

The catalogue must support configurable unit types, not hard-code an exhaustive structure. Expected functional categories include:
- command and executive coordination;
- geographic/local policing;
- response and patrol;
- investigations and casework;
- specialist investigative or technical support;
- traffic/road policing;
- public order/event support;
- custody and prisoner-related functions;
- training and professional development;
- standards/oversight;
- intelligence and analytical support;
- communications/dispatch liaison;
- administration, logistics and staff support.

These are capability categories, not a mandate to create one unit for every label. BP-05 approves the actual structure and BP-44 governs catalogue changes.

### 4.3 Hierarchy

A unit may have one parent unit at a time unless an explicitly modelled matrix relationship is used. Matrix/reporting links must be typed (administrative, operational, specialist, oversight or support) and cannot be mistaken for command authority. The hierarchy must be acyclic. Each unit has a defined reporting destination and escalation path. A top-level unit must be explicitly identified as such.

### 4.4 Mandate and boundaries

Each unit's mandate defines:
- purpose and authorised functions;
- geographic or functional scope;
- services it provides and receives;
- command and escalation relationships;
- capabilities required to perform each function;
- functions it is prohibited from exercising;
- dependency and referral routes.

A unit label alone does not grant statutory power. Authority and legal powers are governed by BP-05 and applicable game canon.

## 5. Establishment, posts and staffing capacity

### 5.1 Establishment

The approved establishment is the authorised structure of posts by unit, role/position, rank/grade requirement and capacity. Fields include establishment_id, unit_id, post/position reference, authorised count, effective interval, approval reference, budget/grade reference where relevant, and policy version.

Establishment is not actual staffing. A unit may be:
- fully staffed;
- under-strength;
- over-strength only under authorised temporary exception;
- vacant/unfilled;
- suspended or not yet activated.

### 5.2 Capacity controls

Assignment checks the active establishment at the effective time. Over-strength assignment is rejected unless a competent authority records the exception, scope, reason, duration and funding/HR implications where required. Temporary surge capacity must be separately represented and expire or be reviewed; it must not permanently inflate establishment through repeated informal extensions.

The overall police headcount is constrained by the 10,000 total living-person cap and the approved population model. BP-08 cannot create a personnel identity or bypass BP-03 population admission.

### 5.3 Posts versus people

A post is an authorised organisational slot; a person is an individual employee. One post may have successive incumbents over time but not multiple simultaneous substantive incumbents unless explicitly designed as a shared/rotational post. A person may have a substantive post and a separately authorised temporary acting role. Vacant posts remain recorded.

## 6. Command, supervision and responsibility

### 6.1 Command assignments

A command assignment identifies the unit, command role/post, incumbent personnel ID, authority basis, start/end, substantive or acting status, delegated scope and approval reference. The unit's command post may be vacant. Command assignment does not automatically grant authority beyond BP-05.

### 6.2 Acting command and absence

Where a commander is absent, unavailable, conflicted or removed, the unit follows an approved succession/delegation order. Acting command must identify:
- appointing authority;
- acting incumbent;
- effective interval;
- command scope and limitations;
- handover/acknowledgement;
- expiry and reversion/successor.

No acting command is inferred merely because a person is the most senior present. If the chain is vacant or conflicted, use the authorised alternate in BP-05; do not permit self-appointment.

### 6.3 Supervisory links

A supervisory assignment is explicit and effective-dated. A supervisor may supervise personnel without being their substantive line manager only where a typed operational/specialist supervision relationship permits it. Supervisory responsibility, career reporting line and incident command are distinct. Multiple supervisors must have clearly scoped domains and no contradictory authority.

### 6.4 Span and continuity

BP-05 may define expected span-of-control limits. BP-08 validates configured limits and flags exceptions; it must not invent numerical thresholds. Vacancies, leave and absences trigger succession/coverage processes, not deletion of the unit or automatic authority transfer.

## 7. Personnel membership and posting

### 7.1 Membership record

Minimum fields:
- membership_id, personnel_id, unit_id;
- membership_type (primary, secondary, attachment, temporary task group, liaison);
- position/post reference where applicable;
- supervisor reference;
- start_at, planned_end_at, actual_end_at;
- assignment authority and source transaction;
- posting reason and geographic/function scope;
- eligibility validation snapshot;
- status, policy version, audit metadata.

A person has one primary operational posting at a time by default. Additional memberships require explicit permission and compatible workload/authority rules. A temporary task group membership must not overwrite the substantive primary posting.

### 7.2 Posting workflow

1. Identify operational/organisational requirement and authorised vacancy or temporary need.
2. Select candidate using verified personnel status, career eligibility, qualifications, clearance, restrictions and availability.
3. Validate establishment and post compatibility.
4. Obtain competent approval.
5. Set effective date and duration/conditions.
6. Create membership and command/supervisory links as needed.
7. Notify affected employee and units.
8. Transfer responsibilities, equipment and active work through owning systems.
9. Close prior membership at the correct effective time.
10. Record acknowledgement, handover and audit.

A failed validation leaves existing membership unchanged. No employee may be silently moved by a narrative event.

### 7.3 Transfers and attachments

Permanent transfer closes prior primary membership and starts the new one with no gap/overlap unless explicitly authorised. Temporary attachment retains the home unit and specifies host unit, purpose, authority, duration, supervision, equipment responsibility and return condition. Secondment to an external organisation is a BP-07/BP-33 employment arrangement; BP-08 records only the unit interface and must not create an external jurisdiction.

### 7.4 Restrictions and eligibility

Before membership/deployment, validate:
- active police employment/service status;
- duty and leave status;
- suspension/restriction;
- required rank/position eligibility;
- mandatory qualifications and currency;
- clearance/access;
- fitness or operational restrictions where represented;
- conflict of interest and incompatibility;
- workload and shift availability;
- establishment capacity.

A restriction may prohibit a function but permit another. Store the actual scope; do not reduce all restrictions to a generic unavailable flag. The system must not disclose confidential underlying reasons to unauthorised users.

## 8. Deployment model

### 8.1 Deployment record

A deployment is an operational assignment of a person, team or unit to a defined task, area, event, incident, case support function or temporary operational objective. Minimum fields:
- deployment_id and deployment type;
- subject type and subject ID (person/team/unit);
- originating unit and current accountable unit;
- task/incident/case/event reference where permitted;
- geographic scope or location reference within Saltwater;
- objective, authorised functions and restrictions;
- issuing authority and order/reference;
- start_at, planned_end_at, actual_end_at;
- operational supervisor/commander;
- personnel/resource composition references;
- acknowledgement/status and status history;
- priority, confidentiality and policy version.

### 8.2 Deployment types

Support routine beat/sector assignment, shift deployment, call/incident response, case support, planned operation, event/public-order support, specialist assistance, temporary reinforcement, mutual support between Saltwater units, protective/escort function where authorised, training exercise and emergency redeployment. Types are configurable and cannot extend Saltwater jurisdiction beyond the city-state.

### 8.3 Deployment lifecycle

Suggested states: proposed, awaiting approval, authorised, issued, acknowledged, mobilising, active, paused/held, reassigned, stood down, completed, cancelled, expired, rejected. The implementation must define legal transitions and distinguish order status from execution status.

A deployment order:
1. validates issuer authority and tasking scope;
2. validates unit/person availability, competence, clearance and resource needs;
3. checks conflicts with existing deployments and duty roster;
4. confirms operational supervisor and communications route;
5. records approval and issue;
6. obtains acknowledgement or records a controlled no-acknowledgement exception;
7. updates resource availability for BP-10/BP-11;
8. tracks changes, relief, handover and completion;
9. releases personnel/resources only when owning operational workflow confirms release.

### 8.4 Tasking and operational command

The originating authority, task commander, home-unit supervisor and incident commander may be different people. Each role is separately recorded with scope and precedence. An incident commander under BP-12 controls incident objectives within authorised remit; BP-08 records resulting deployment and accountability. A case investigator under BP-15/BP-16 may request support but cannot independently command a unit outside delegated authority.

### 8.5 Priority and conflicts

When demands exceed available capacity, prioritisation follows the relevant command/incident policy (BP-05/BP-12) and dispatch/operations workflow (BP-10/BP-11). BP-08 supplies truthful capacity and constraints; it does not fabricate resources or silently cancel lower-priority assignments. Conflict resolution records decision-maker, reason, affected tasks, risks, time and notifications.

## 9. Geographic responsibility and coverage

All unit geography is contained within Saltwater. A unit may have citywide remit, district/sector/beat responsibility, facility responsibility, specialist functional remit or task-specific location. Geographic objects are referenced from BP-02 and may not be duplicated as free-text geography.

Coverage records define area, effective interval, responsible unit, backup/support unit, boundary reference and service scope. Adjacent coverage areas may share boundary support but must have one clearly identified primary responsibility for each governed function/time interval, unless a documented joint arrangement applies.

Temporary boundary changes for an event, incident or emergency require authority, duration, map/spatial version, affected coverage, communications and restoration trigger. No unit may be assumed responsible for a location outside the city-state. If a task refers to an external place, it is recorded as external context/liaison only and does not create Saltwater police jurisdiction there.

## 10. Unit capability and readiness

Capability profiles define functions the unit is configured to perform and the minimum prerequisites: personnel roles/qualifications, command coverage, equipment/facility/vehicle references, communications, specialist support and authorisation. BP-08 computes readiness from current authoritative inputs and displays:
- authorised capability;
- staffed capability;
- currently available capability;
- degraded/limited capability;
- unavailable capability;
- reason category and data freshness.

Readiness is time-sensitive and must identify the calculation timestamp and source versions. A unit can be authorised for a function but not currently able to perform it. Missing data must be labelled unknown, not treated as ready. A readiness percentage, if later configured, must disclose denominator and weighting; no arbitrary percentage is introduced here.

## 11. Inputs, outputs and system contracts

### Inputs
- BP-05: unit hierarchy policy, command posts, authority, rank/position, establishment rules.
- BP-06: personnel identity and service state.
- BP-07: career rank, appointment and eligibility outcomes.
- BP-09: resource, equipment, vehicle, facility and communications availability.
- BP-10: patrol and field deployment execution/availability.
- BP-11: dispatch resource status and communications events.
- BP-12: incident command, objectives, priority and stand-down.
- BP-15/BP-16: authorised case/task support requests and assignment outcomes.
- BP-31: authorised restrictions that affect duties, subject to confidentiality.
- BP-32: qualifications and capability credentials.
- BP-33: leave, HR and employment status.
- BP-37: canonical clock, calendar, recurrence, temporal queries and schedule execution; BP-08 owns police planned-roster content and duty assignment, while BP-33 owns actual attendance/leave.
- BP-42: access and information classification.

### Outputs
- authoritative unit and hierarchy catalogue;
- current/historical unit membership and command assignments;
- authorised establishment and vacancy/strength summaries;
- deployment orders and assignment status;
- person/team/unit availability and capability projections;
- coverage and responsibility projections;
- events to patrol, dispatch, incident, case, resource, HR and reporting systems;
- audit trail and operationally filtered unit views.

### Event contract
Every event has unique ID, source, schema version, effective simulation time, recorded time, actor/authority, subject, prior/resulting version, idempotency key and visibility. Consumers tolerate retries and out-of-order delivery. A projection is rebuildable from authoritative records/events. Cross-system updates must be transactional where within one database boundary or use an outbox/inbox/idempotent event pattern across boundaries.

## 12. Permissions and confidentiality

BP-42 governs all access. Commanders see their unit's authorised operational information; supervisors see assigned personnel and duty information; dispatch sees availability and deployment facts needed for dispatch; case teams see only approved support assignment details; HR sees membership and posting facts needed for administration. Sensitive specialist capability, protected assignments, undercover identities, confidential case associations and personnel restrictions are not exposed by default.

A user may not infer a protected assignment from a generic unit roster. Administrative read access does not grant deployment authority. Only authorised command roles may create, amend, approve or cancel the relevant orders. Every denied or exceptional access/action is auditable.

## 13. Exceptions and edge cases

1. Unit exists but has no staff: retain unit; readiness is unstaffed/unavailable.
2. Unit has staff but no commander: flag command vacancy and apply approved succession; do not infer authority from seniority.
3. Parent unit is closed: child units require explicit transfer, closure or new parent; no orphaned silent hierarchy.
4. Attempt to create a hierarchy cycle: reject.
5. Person assigned to two primary units concurrently: reject unless explicit shared-post policy exists.
6. Temporary attachment expires: return/extension must be authorised; do not silently continue.
7. Person becomes suspended while deployed: notify responsible command and operations; apply authorised stand-down/replacement.
8. Person goes on leave during deployment: reconcile through roster/operational workflow; no assignment silently remains executable.
9. Required qualification expires: capability and eligibility are recalculated; remove only the affected capability.
10. Equipment unavailable: unit readiness degrades; do not represent unavailable capability as ready.
11. Unit is over establishment: reject absent documented temporary exception.
12. Emergency surge staffing: record source, scope, authoriser, expiry and review; do not convert into permanent establishment.
13. Unit renamed: preserve unit ID and historical name intervals.
14. Unit split or merger: create successor relationships and transfer memberships/tasks with effective dates; retain predecessor history.
15. Unit disbanded with active deployments: explicitly reassign, complete or cancel every active deployment.
16. Acting commander departs unexpectedly: use authorised succession chain and record handover.
17. Commander is conflicted: route to authorised alternate; no self-approval.
18. Cross-unit tasking is disputed: escalate under command hierarchy; preserve both request and decision.
19. Dispatch requests unavailable unit: return actual status and constraints, not a false acceptance.
20. Incident commander changes: update operational command assignment without rewriting home-unit membership.
21. Case support request is withdrawn: close or reassign support task; preserve investigative case ownership.
22. Geography boundary changes: apply versioned boundary and effective interval; do not rewrite past coverage.
23. Two units claim same primary coverage: reject or require explicit joint responsibility with lead unit.
24. Location lies outside Saltwater: no local jurisdiction/deployment authority is created.
25. Player is assigned elsewhere by organisational need: apply valid order; preference is not guaranteed.
26. Player is unavailable/offline: no simulated time or automatic career/deployment progression occurs while paused.
27. Duplicate deployment order arrives: idempotency prevents duplicate assignment.
28. Out-of-order membership events arrive: reconcile source version; do not guess current unit.
29. Unit readiness inputs are stale/missing: show unknown/degraded with freshness; never assume ready.
30. Deployment order exceeds issuer's authority: reject and audit.
31. Deployment asks person to exercise unqualified function: block or require authorised support/supervision.
32. Temporary task group ends: close group and memberships; preserve individual primary postings.
33. Unit has no approved establishment: it cannot receive substantive staffing until authorised.
34. Employee separates or dies: close membership/deployment through authoritative personnel event; retain history.
35. A confidential specialist assignment is queried by unauthorised player: deny without revealing existence where policy requires.
36. Population cap reached: unit structure changes cannot create extra people; any recruitment remains subject to population controls.
37. Unit is temporarily suspended: block new tasking and resolve active tasks under command decision.
38. Emergency redeployment conflicts with existing critical task: require explicit priority decision and record displaced risk.
39. A post changes but unit membership does not: preserve separate post and membership histories.
40. A person holds an acting role in one unit and substantive role in another: validate compatibility and authority; do not merge the records.

## 14. Cross-system effects

- BP-05 defines institutional hierarchy, unit authority, command posts and establishment policy.
- BP-06 provides person and employment identity; BP-07 provides career/appointment eligibility.
- BP-09 supplies resources and equipment status used in readiness.
- BP-10 executes patrol and field tasking; BP-11 uses availability for dispatch.
- BP-12 supplies incident command and emergency priorities.
- BP-15/BP-16 request and receive case support without taking unit command.
- BP-31/BP-32 supply authorised restrictions and qualifications.
- BP-33 supplies leave and HR status.
- BP-37 supplies roster/time and enforces pause.
- BP-38/BP-39 persist unit/membership/deployment histories.
- BP-40/BP-41 display and notify through authorised interfaces.
- BP-42 enforces information/action permissions.
- BP-43 validates hierarchy, staffing, deployment and readiness.

## 15. Acceptance tests and evidence

Each test stores fixture IDs, policy version, source events, expected/actual result, timestamps and reproducible pass/fail evidence. Use fictional data only.

| ID | Scenario | Required result |
|---|---|---|
| UNIT-001 | Create valid unit with mandate and parent | Stable ID and valid hierarchy |
| UNIT-002 | Create unit without mandate/type | Reject or remain draft; not operational |
| UNIT-003 | Parent-child cycle | Reject |
| UNIT-004 | Unit has no staff | Retain unit; report unstaffed |
| UNIT-005 | Unit has no commander | Flag vacancy; use authorised succession only |
| UNIT-006 | Create approved establishment | Posts/capacity distinct from actual staff |
| UNIT-007 | Assign beyond establishment | Reject absent authorised temporary exception |
| UNIT-008 | Assign person without valid BP-06 identity | Reject |
| UNIT-009 | Assign suspended employee | Reject operational membership/deployment as policy requires |
| UNIT-010 | Assign person to two primary units | Reject absent explicit shared-post rule |
| UNIT-011 | Add temporary attachment | Preserve home primary membership and record host/scope |
| UNIT-012 | Attachment expires | Close/return or require authorised extension |
| UNIT-013 | Transfer primary unit | Close prior interval and create new interval correctly |
| UNIT-014 | Unit rename | Same unit ID; historical names preserved |
| UNIT-015 | Unit merger/split | Successor links and prior history retained |
| UNIT-016 | Acting commander appointed | Authority and interval explicitly recorded |
| UNIT-017 | Commander absent with no approved successor | Do not infer command |
| UNIT-018 | Conflicted approval authority | Route to authorised alternate |
| UNIT-019 | Deployment order lacks issuer authority | Reject and audit |
| UNIT-020 | Deploy person without required qualification | Block or require authorised supervision |
| UNIT-021 | Deploy unavailable person | Reject; availability remains truthful |
| UNIT-022 | Duplicate deployment order | Apply once |
| UNIT-023 | Out-of-order deployment events | Reconcile without corrupting state |
| UNIT-024 | Deployment is stood down | Close assignment and release only on confirmed workflow |
| UNIT-025 | Incident commander changes | Update incident command; retain home unit |
| UNIT-026 | Case support is requested | Record support task without transferring case ownership |
| UNIT-027 | Two units claim exclusive coverage | Reject or require explicit joint lead |
| UNIT-028 | Coverage boundary changes | Versioned effective interval; history unchanged |
| UNIT-029 | External location task | No Saltwater jurisdiction created |
| UNIT-030 | Unit resource becomes unavailable | Readiness degrades; no false capability |
| UNIT-031 | Readiness data missing/stale | Mark unknown/stale, not ready |
| UNIT-032 | Emergency surge deployment | Authority, duration, review and displaced risk recorded |
| UNIT-033 | Unit suspended | Block new tasking and resolve active work |
| UNIT-034 | Employee separates | Close membership/deployment; retain history |
| UNIT-035 | Population cap reached | No additional living personnel admitted |
| UNIT-036 | Player preference conflicts with organisational order | Apply valid authorised order and record it |
| UNIT-037 | Simulation paused | No time-based deployment/membership transition |
| UNIT-038 | Unauthorised roster query | Deny protected information and audit |
| UNIT-039 | Unit dissolved with active deployments | Every deployment explicitly resolved |
| UNIT-040 | Rebuild membership/readiness projections | Deterministic result from canonical records/events |

## 16. Non-functional and operational requirements

- **Integrity:** enforce unique IDs, valid references, acyclic hierarchy, effective intervals and compatible membership.
- **Temporal correctness:** all durations use BP-37 simulation time; paused simulation has no elapsed deployment time.
- **Auditability:** all creation, approval, reassignment, exception, cancellation and closure actions are attributable.
- **Idempotency:** duplicate commands/events cannot create duplicate memberships or deployments.
- **Availability truthfulness:** unknown/stale inputs never imply available or ready.
- **Privacy:** protected units, rosters, restrictions and assignments are access-filtered.
- **Resilience:** rebuild projections from canonical unit, membership, command and deployment history.
- **Efficiency:** avoid duplicating personnel, rank, qualification, resource and geographic data; use references and compact event records without loss of meaning.
- **NPC consistency:** NPC assignment and deployment follow the same authority, capacity and eligibility rules as player personnel.
- **Operational clarity:** distinguish home unit, tasking unit, incident command, supervisor and dispatch status in every relevant view.

## 17. Source traceability

Primary sources: S23 police service governance and structure; S24 police personnel/career (membership interface); S25 police duty rosters, staffing and deployment; S26 police command, policy and internal governance; S16 utilities/communications (resource interface); S17 roads/transport and S18 facilities (geographic/resource interfaces); S22 emergency services/civil protection (coordination interface); S27 call-taking/CAD/dispatch; S28 patrol/response/field operations; S30 case management/investigative command; S35 intelligence and information handling (restricted support interface); S41 time/scheduling; S42 simulation causality; S43 AI/player agency; S45 maps/diagrams; S46 persistence; S48 permissions; S49 recovery; S50 testing; S51 operations/observability; S52 canon/change control. Requirement/test IDs and exact source pointers remain in SALTWATER-52-TO-44-CROSSWALK.md and must be semantically reconciled before approval.

## 18. Open decisions

1. Exact police unit hierarchy, names, codes and functional catalogue (BP-05/user canon).
2. Authorised establishment and staffing allocation by unit and shift.
3. Which units have geographic beats versus citywide or functional remit.
4. Command post titles, deputy structure, acting succession and span-of-control limits.
5. Rules for primary/secondary membership and matrix reporting.
6. Which rank, qualifications, clearance and experience prerequisites apply to each unit/function.
7. Temporary attachment and surge maximum durations and renewal controls.
8. Deployment priority hierarchy and conflict arbitration policy (BP-05/BP-12).
9. Unit readiness formula, data freshness thresholds and any display score.
10. Whether any specialist or confidential units require hidden existence as well as hidden membership.
11. Cross-unit joint responsibility and lead-unit rules.
12. External liaison/secondment boundaries; no external policing jurisdiction is implied.
13. Which establishment changes require budget approval and which are command-authorised (BP-34).
14. Final status vocabularies and event schema shared with BP-10/BP-11/BP-12/BP-37.

These are explicit policy decisions, not permission to invent permanent organisational canon. The architecture, boundaries and invariants above remain binding in the draft.

## 19. Completion criteria

BP-08 may move to DESIGNED only after every mapped source requirement and test is semantically reconciled; open canonical decisions are resolved or explicitly accepted as configurable policy; interfaces with BP-05/BP-06/BP-07/BP-09/BP-10/BP-11/BP-12/BP-15/BP-16/BP-31/BP-32/BP-33/BP-37/BP-38/BP-39/BP-42 are reconciled; and the user reviews and approves the full specification.

Implementation, testing and verification remain separate states. This document authorises no Neon schema change, migration, seed, import or database write.
