# BP-07 — Career System

**Project:** Saltwater, fictional sovereign city-state; one city and one jurisdiction  
**Blueprint division:** BP-07 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test:** NOT_STARTED | **Verification:** NOT_STARTED

## 1. Purpose and authority

Define the complete police-career lifecycle: entry, recruit status, probation, confirmation, substantive service, rank progression, promotion, lateral movement, specialist and command pathways, acting appointments, secondment, performance evidence, service calculation, retirement, separation, re-entry and post-service history.

BP-07 governs how a person's police career develops. It does not own identity/personnel master data (BP-06), institutional rank and position catalogues (BP-05), postings/deployment (BP-08), training delivery (BP-32), HR transactions (BP-33), discipline adjudication (BP-31), finance/payroll (BP-34), time (BP-37), persistence (BP-38/BP-39), or access policy (BP-42). It references authoritative records and consumes their verified outcomes; it must not create competing copies.

The player may begin as a recruit. Player and NPC careers use the same rules. Career advancement is earned, evidenced and constrained by authorised appointments and the simulation's actual elapsed time.

## 2. Scope, boundaries and governing invariants

### In scope
- Career episodes linked to a single BP-06 personnel identity.
- Entry route, application/appointment references, commencement and probation.
- Career state, substantive rank and position history, grade reference and acting/secondment history.
- Eligibility assessments, promotion cases, decisions, appeals/reviews and effective transitions.
- Lateral and specialist pathways, command appointments, acting duties and return.
- Performance evidence and its permitted use.
- Credited service, service breaks, retirement forecast and mandatory retirement.
- Resignation, dismissal, death in service, reinstatement, re-entry and retained history.
- Player career status/actions and NPC career simulation.

### Invariants
1. Each career episode references exactly one persistent personnel identity. A genuine re-entry after separation is recorded as a new episode or formally approved reactivation; it never creates a duplicate person.
2. Rank, position, grade, authority, legal powers, clearance, qualification, appointment, assignment and deployment are separate dimensions. None implies another without an explicit rule.
3. A promotion requires an authorised decision and effective date. Eligibility is not entitlement; vacancy is not promotion; selection is not effective appointment until approved.
4. Acting appointment does not silently change substantive rank. Its delegated authority, scope and expiry are explicit.
5. Career history is append-preserving. Corrections supersede or amend with provenance; they do not erase historical decisions.
6. The same rules apply to player and NPC personnel. Differences arise only from evidence, choices, eligibility, vacancies and policy.
7. No progression is inferred from narrative, wall-clock time, elapsed real-world time or an unverified generated event.
8. No simulation time advances while the player is absent. Probation, acting terms, service duration and career schedules freeze with the simulation clock.
9. Career termination never deletes the person or career history.
10. Police personnel count inside the hard 10,000 living-person population cap; career entry cannot bypass population admission or double-count a person.
11. Policy versions and effective dates are retained. A later rule change does not silently rewrite an earlier decision.
12. Career records cannot leak protected case facts or hidden offender identity. In applicable investigations, the exact user command bingo remains the only authorised reveal trigger.
13. The fixed BP-01–BP-44 structure cannot be changed without explicit user approval.

### Ownership boundaries

| Domain | Owner | BP-07 contract |
|---|---|---|
| Person/service identity | BP-06 | Foreign reference; no duplicate identity |
| Rank, position, grade, establishment, command post | BP-05 | Consume controlled catalogues |
| Posting, unit membership, deployment | BP-08 | Emit/consume career-relevant change events |
| Duty rosters and calendar | BP-10/BP-37 | Supply availability and temporal constraints |
| Training and qualification award/expiry | BP-32 | Consume verified outcomes |
| Discipline and final findings | BP-31 | Consume final authorised outcomes, never allegations as findings |
| Recruitment, leave, employment and separation administration | BP-33 | Consume authoritative HR transactions |
| Payroll, grade cost and benefits | BP-34 | Emit approved career-change events; no ledger ownership |
| Simulation clock and pause | BP-37 | Read-only time authority |
| NPC causality | BP-35 | Career triggers only while simulation time advances |
| Persistence and recovery | BP-38/BP-39 | Canonical durable events and rebuildable projections |
| Access and confidentiality | BP-42 | Enforce role/player visibility |
| Testing | BP-43 | Reproducible career and lifecycle tests |

## 3. Core records and fields

All identifiers are stable, opaque, non-semantic and never recycled. All effective dates use BP-37's canonical simulation-time representation.

### 3.1 Career episode
Required fields:
- career_id, personnel_id, career_sequence;
- entry_route_id and optional recruitment/application reference;
- service_start_at and appointment_start_at (distinct where policy requires);
- current career/service state;
- substantive_rank_id, substantive_position_id and grade_id (references to BP-05; nullable where not yet appointed);
- probation state, start/end and review references;
- service-credit calculation reference and derived credited duration;
- projected retirement due date (derived, not independently authoritative);
- governing policy version, record version, created/recorded timestamps and source event.

One personnel identity may have only one current active career episode unless an explicitly authorised service arrangement defines otherwise. Historical episodes remain linked.

### 3.2 Career event
Every material transition is an immutable, attributable event with:
- event ID, career ID, event type, effective simulation timestamp and recorded timestamp;
- source system, actor/authority, reason code and decision reference;
- prior/resulting state references;
- policy version, evidence references and visibility classification;
- idempotency key and schema version;
- correction/supersedes reference where applicable.

Event types include application outcome, appointment, recruit commencement, probation review/extension/confirmation, posting, transfer, promotion nomination/assessment/approval/effect, acting appointment/extension/end, secondment/return, qualification dependency change, performance review, service-credit award/adjustment, suspension/reinstatement, retirement notice/effect, resignation, dismissal, death-in-service and re-entry.

### 3.3 Eligibility assessment and promotion case
An eligibility assessment stores candidate, target rank/post/pathway, criteria version, criterion-by-criterion result, evidence references, exclusions, reviewer, timestamp and reproducible decision status.

A promotion case stores authorised vacancy/post reference, target rank, eligible pool or nomination basis, published criteria, candidate evidence, assessment stages, panel/recommending decision, approval authority, effective date, notification, appeal/review and final outcome. Confidential deliberations are separately access-controlled.

### 3.4 Acting appointment, secondment and performance
A temporary appointment records substantive rank/position, temporary post, acting authority, delegated powers, scope, start/end, extensions, handover and return condition. A secondment records home/host organisation, supervision, retained/suspended police powers and access, term and return instruction.

Performance evidence references verified supervision, training, operational outcomes, commendations and final conduct outcomes. Every item records source, verification state, relevance period, permitted decision use and correction route. Allegations, untested intelligence, popularity, protected characteristics and unverified narrative are not performance facts.

## 4. Entry, recruit pathway and probation

### 4.1 Entry routes
Support configured entry routes such as recruit intake, experienced-officer entry, specialist appointment, re-entry and other explicitly approved pathways. BP-33 owns recruitment and appointment administration; BP-05 owns establishment and authorised posts.

### 4.2 Recruit start
The player may elect to start as a recruit. The system creates or references a BP-06 personnel identity and creates a linked recruit career episode. Recruit status does not grant independent police powers, operational command, unrestricted system access or a substantive constable rank unless a specific BP-05 rule expressly defines a limited authority. The recruit pathway includes required training, supervision, assessment, restrictions and progression gates.

### 4.3 Preconditions
Career commencement requires valid personnel identity, accepted recruitment/appointment outcome, authorised recruit establishment or post, population registration, effective start date, applicable policy and initial supervision/access arrangements. Missing dependencies block only the transition that needs them; no successful appointment is fabricated.

### 4.4 Probation
Probation has a governed start, expected end, review milestones, evidence, authorised reviewer and decision. Elapsed duration alone never confirms probation. Outcomes include confirmation, extension, remedial pathway, resignation or termination. An extension records reason, authority, duration and next review. Probation duration advances only with BP-37 simulation time.

## 5. Progression and promotion

### 5.1 Principles
Progression uses published criteria, verified competence, relevant service, conduct outcomes, performance evidence, required training/qualifications, vacancies/establishment, selection and approval. Time served alone never guarantees promotion.

BP-05 owns the rank ladder, titles, rank definitions, position and authority catalogues. BP-07 owns each employee's transition. Exact rank titles, minimum time-in-rank, service thresholds, examination formats, panel composition and promotion quotas remain open policy decisions; this draft does not invent them.

### 5.2 Eligibility checks
At the policy-defined assessment point, validate:
- source and target rank are valid and progression-compatible;
- required authorised post/vacancy exists;
- minimum service/time-in-rank is met;
- mandatory training and qualifications are current;
- required experience and competency evidence exists;
- active restrictions and final disciplinary outcomes are handled under policy;
- selection and approval authorities are valid and not conflicted;
- effective date is not earlier than approval unless a documented authorised correction permits it.

An eligibility result is a dated snapshot, not a permanent employee attribute. Reassess when a relevant qualification, restriction, policy or vacancy changes.

### 5.3 Promotion workflow
A configurable workflow comprises: authorised vacancy; published opportunity/nominations; eligibility assessment; application/nomination; evidence validation; required examination/interview/practical assessment; panel recommendation; competent-authority decision; appeal/review where provided; effective appointment; dependent-system updates; and notification. No stage is skipped unless a versioned exception policy permits it and the decision records that basis.

Possible outcomes include selected, not selected, deferred, ineligible, withdrawn, vacancy cancelled, returned for further evidence and appeal upheld/denied. Reasons are recorded at the permitted confidentiality level. Passing an assessment does not guarantee selection.

### 5.4 Lateral, specialist and command pathways
A lateral move may change unit, function, position or specialism without changing rank. Specialist entry may require prerequisites, assessment, training and a valid post. A qualification alone does not assign a specialist role or grant authority.

Command progression requires the rank, appointment, competency, leadership and post prerequisites defined by BP-05 and policy. Police Chief appointment and tenure are subject to section 9. Substantive rank remains distinct from appointment to the Chief position.

### 5.5 Player agency
The player may apply, decline, withdraw or accept a permitted opportunity. A declined promotion is recorded without automatically treating the choice as misconduct. The system must not force a player career decision where the player has a legitimate choice. Mandatory retirement and other binding rules remain binding.

## 6. Acting appointments, temporary duties and secondment

- Acting appointments require an authorised appointing authority, explicit scope, delegated authority, start and end.
- Substantive rank and position remain separately recorded.
- Acting title does not confer every power, clearance, qualification or access right associated with the post.
- Expiry, revocation, replacement and extension are explicit events. No silent extension.
- Each extension requires fresh authority and cannot bypass tenure or appointment limits.
- Temporary duty assignment is not automatically a promotion.
- Secondment preserves the home personnel identity and career record; records host, supervision, term, powers/access retained or suspended, and return conditions.
- Return restores the approved substantive status, not a guessed value.
- Concurrent assignments are allowed only where policy explicitly deems them compatible and authorised.

## 7. Performance and conduct evidence

Distinguish raw activity from verified performance; commendation from competence; allegation from substantiated finding; investigation from final adjudication; training attendance from qualification; temporary restriction from permanent disqualification; and supervisor opinion from formal decision.

Pending allegations are not findings. Any temporary promotion hold or risk restriction requires a separate authorised, proportionate, reviewable and time-bounded decision where policy provides. Final findings affect eligibility only as the governing policy permits. Reversed/expunged findings trigger reassessment of affected career decisions where required. The original event and subsequent correction remain auditable.

## 8. Service calculation and retirement

### 8.1 Ordinary mandatory retirement
Mandatory retirement is after **35 years of police service**, not age 35. Calculate from the authoritative service commencement date plus/minus explicitly approved service-credit and excluded-interval events. The treatment of unpaid leave, suspension, prior service, career breaks, re-entry, part-time service and secondment is an open policy decision; the engine must not invent treatment.

The system produces a reproducible forecast and configurable advance notice. A notice is not itself a status change. At the mandatory retirement effective instant, the employee retires unless the specific Chief exception applies. The event retains calculation inputs and policy version.

### 8.2 Police Chief exception — binding rule
A person who formally becomes Police Chief **before completing 35 years of police service** may continue under this exception:
- each Chief term is five years;
- one renewal is permitted;
- maximum total Chief tenure is ten years;
- a renewal is explicit and is never automatic;
- no third term is permitted;
- the exception does not convert the service rule into an age rule;
- eligibility requires a formal Chief appointment effective before the 35-year service threshold.

The career record retains formal appointment date, term start/end, renewal decision and service calculation. An acting Chief appointment does not qualify under this draft; acting status alone is not formal appointment.

At the end of the permitted tenure, if 35 years of service have been reached, mandatory retirement applies. If not, the person leaves the Chief appointment and continues only under the applicable substantive rank/position and service rules. The exception never authorises a third term or more than ten years. Succession and post-Chief placement are governed by BP-05.

A person who reaches 35 years before formal appointment as Chief does not qualify. A pending appointment or promotion does not suspend the ordinary retirement rule.

### 8.3 Calculation integrity
Expose a reproducible calculation: service commencement, approved credits, excluded intervals, adjustments, governing policy version and result. No manual override without authorised adjustment event, reason and provenance. The same events and policy version must produce the same result.

## 9. Separation, re-entry and post-service

Retirement, resignation, dismissal, death in service and other configured separation require an authoritative BP-06/BP-33 outcome and effective date. Separation closes active appointment and future duty eligibility; triggers access revocation and return of resources through owning systems; emits finance/records workflows; and preserves person, career, historical assignments and relevant records.

Re-entry requires a defined route and approval. Prior service is not automatically credited; a service-credit decision is explicit. Dismissal cannot be silently bypassed. An erroneous separation is corrected through an attributable reinstatement/correction event, not deletion of history. Civilian post-service work does not reactivate police powers or count as police service without a new formal appointment.

## 10. State model and transition protocol

Suggested state dimensions include career episode (pending start/active/closed), service standing (recruit/probationary/confirmed/separated/retired/deceased), duty status (available/leave/suspended/restricted), appointment status (substantive/acting/seconded) and review status. These are orthogonal dimensions where necessary; do not force incompatible combinations into one simplistic status field. Controlled vocabularies must reconcile with BP-06 and BP-33.

Every transition:
1. validates identity, current record version and source state;
2. validates permitted transition and effective time;
3. validates authority, reason, evidence and dependency references;
4. checks appointment compatibility, establishment and population constraints;
5. writes an immutable event with idempotency key;
6. updates/derives the current projection transactionally;
7. emits versioned events to dependent systems;
8. records notification and audit outcomes.

Failure leaves no partial transition. Replayed or duplicate delivery cannot duplicate a promotion, service credit or separation. Out-of-order events are held/reconciled against authoritative source versions; the system never guesses.

## 11. Inputs, outputs and event contracts

### Inputs
BP-06 personnel identity/status; BP-05 rank/position/grade/command/establishment catalogues; BP-08 posting outcomes; BP-31 final conduct outcomes/restrictions; BP-32 training and qualification awards/expiry/revocation; BP-33 recruitment, appointment, leave and separation; BP-34 authorised grade/finance consequences; BP-35 NPC triggers; BP-37 clock/calendar/pause; BP-42 permissions and visibility.

### Outputs
Current career projection and event history; rank/position/acting/secondment history for authorised consumers; eligibility snapshots and promotion decisions; probation/retirement forecasts; effective career-change events; player-facing status and available actions; audit evidence and deterministic service calculations.

Every event is uniquely identified, schema-versioned, attributable, timestamped in simulation time and idempotent. Consumers tolerate delayed/replayed delivery. Payloads contain only the minimum necessary data; protected panel deliberations and personnel evidence stay with their authoritative owner.

## 12. Permissions and information boundaries

BP-42 governs access. The player may see their own career status, completed decisions and available actions subject to simulation rules. Supervisors see information required for supervision; panels see authorised candidate materials; HR/command receive defined views. Confidential deliberations, restricted personnel details, protected third-party information and security-sensitive appointments are not exposed by default.

NPC career decisions may be simulated without disclosing private motives. Players receive observable outcomes and authorised reasons, not hidden internal reasoning. Read access does not imply authority to change records.

## 13. Exceptions and edge cases

1. Employee reaches 35 service years while promotion is pending: retirement calculation remains effective; pending promotion does not suspend it.
2. Formal Chief appointment occurs immediately before threshold: eligibility depends on verified effective timestamp and service calculation.
3. Acting Chief reaches threshold: no exception under acting status alone.
4. Chief seeks a third term: reject.
5. Chief first term is informally extended: invalid; one formal renewal only, ten-year ceiling.
6. Chief leaves early: record end/succession; no silent carry-over of remaining term.
7. Candidate passes assessment but vacancy is withdrawn: no promotion.
8. Eligible candidate is not selected: retain reasoned outcome; eligibility is not entitlement.
9. Approval arrives after proposed effective date: no backdating absent authorised correction.
10. Rank changes without position: validate BP-05 compatibility; preserve independent histories.
11. Position changes without rank: transfer/appointment, not promotion.
12. Acting appointment expires during player absence: simulation time has not advanced; no offline expiry.
13. Qualification expires during promotion: reassess at policy checkpoint.
14. Qualification later revoked: reassess affected eligibility/appointment under policy; preserve original decision.
15. Allegation pending: not a proven finding.
16. Finding overturned: reassess affected decisions; retain audit history.
17. Suspension then reinstatement: retain interval and explicit service-credit treatment.
18. Resignation followed by re-entry: approved new episode; no silent service credit.
19. Death while on leave/secondment: close career on authoritative event; retain last valid state.
20. Duplicate promotion/service-credit event: apply once.
21. HR and career events arrive out of order: reconcile source version; no guessed state.
22. Personnel duplicate identities are merged: remap references through canonical identity process with audit.
23. Concurrent assignments: permit only when explicitly compatible.
24. NPC progression trigger occurs while game paused: no progression/time advancement.
25. Policy changes during an open promotion: apply explicit transition rule; retain both policy versions.
26. Population already at 10,000: no new living person may be admitted through recruitment; resolve through BP-03/BP-33 vacancy/admission rules.
27. Rank/position catalogue retired: preserve historical references; future use requires active or grandfathered rule.
28. Candidate appeals: preserve original decision and pause only affected transition where policy says.
29. Service start corrected: recalculate projections, preserve original and correction provenance, notify affected authorities.
30. Retirement projection conflicts with event history: rebuild from authoritative events and policy.
31. Specialist qualification without specialist post: no specialist appointment by qualification alone.
32. Acting authority conflicts with clearance: no automatic clearance elevation; apply stricter boundary.
33. Player declines promotion: record choice, no automatic misconduct.
34. Player exits recruit path: record actual permitted choice and consequences; do not fabricate completion.
35. Approval authority vacant/conflicted: use authorised alternate from BP-05; no self-approval.
36. Transition attempted while clock paused: administrative correction may be recorded only as a non-time-advancing action if permitted.
37. Retired person takes civilian contract: no police powers/service absent formal reappointment.
38. Occupied position abolished: preserve incumbent/history; route transition through BP-05/BP-08/BP-33.

## 14. Cross-system effects

- BP-03 counts all police employees inside the 10,000 living-person cap.
- BP-05 supplies rank/position/authority definitions and Chief appointment structure.
- BP-06 supplies personnel identity and master employment record.
- BP-08 executes posting/deployment consequences; BP-07 does not dispatch.
- BP-10/BP-37 use career availability and temporal constraints for rosters.
- BP-31 supplies final conduct outcomes, not unproven allegations.
- BP-32 supplies verified training/qualification outcomes.
- BP-33 owns recruitment, leave, appointment and separation administration.
- BP-34 receives approved grade/appointment changes; BP-07 does not post money.
- BP-35 simulates NPC career actions only while time advances.
- BP-38/BP-39 persist and reconstruct events/projections.
- BP-42 filters confidential records.
- BP-43 tests calculations, state transitions and replay deterministically.

## 15. Acceptance tests and evidence

Each test must retain fixture IDs, policy version, input events, expected and actual result, and pass/fail evidence. Use fictional records only.

| ID | Scenario | Acceptance result |
|---|---|---|
| CAREER-001 | Start recruit from valid BP-06 identity | One linked recruit episode; no duplicate person |
| CAREER-002 | Start without personnel identity | Reject; no partial record |
| CAREER-003 | Appointment without authorised establishment | Block |
| CAREER-004 | Recruit access/powers | Recruit restrictions enforced |
| CAREER-005 | Probation while simulation paused | No elapsed duration added |
| CAREER-006 | Complete probation with required reviews | Valid confirmation event |
| CAREER-007 | Probation duration passes without assessment | No automatic confirmation |
| CAREER-008 | Promotion requires vacancy but none exists | Reject |
| CAREER-009 | Eligibility without selection | No promotion |
| CAREER-010 | Approved promotion has future effective date | Rank changes only at effective time |
| CAREER-011 | Lateral transfer | Position/assignment changes; rank does not |
| CAREER-012 | Acting appointment begins | Acting scope recorded; substantive rank unchanged |
| CAREER-013 | Acting appointment expires | Acting authority ends; approved substantive state restored |
| CAREER-014 | Acting extension lacks approval | Reject |
| CAREER-015 | Mandatory qualification missing/expired | Ineligible or held per policy |
| CAREER-016 | Pending allegation | Not treated as finding |
| CAREER-017 | Final finding affects eligibility | Only policy-defined effect applied |
| CAREER-018 | Finding overturned | Reassessment; history retained |
| CAREER-019 | Service reaches 35 years | Retirement based on service, not age |
| CAREER-020 | Age 35, service below 35 years | No age-only retirement |
| CAREER-021 | Formal Chief appointment before 35 service years | Exception eligibility recorded |
| CAREER-022 | Acting Chief only | No exception eligibility |
| CAREER-023 | Chief completes five-year term and valid renewal | One renewal; maximum ten years |
| CAREER-024 | Chief attempts third term | Reject |
| CAREER-025 | Chief tenure ends before 35 service years | Leaves Chief post; ordinary service continues; no third term |
| CAREER-026 | Chief tenure ends after 35 service years | Mandatory retirement applies |
| CAREER-027 | Approved service calculation correction | Recalculate with provenance |
| CAREER-028 | Duplicate service-credit event | Apply once |
| CAREER-029 | Resignation | Close active appointment; retain history |
| CAREER-030 | Re-entry after separation | Approved episode; no automatic prior-service credit |
| CAREER-031 | Death in service | Close career; retain person and history |
| CAREER-032 | Player declines promotion | Choice recorded; no fabricated promotion |
| CAREER-033 | NPC career trigger while game paused | No progression |
| CAREER-034 | Policy changes during open promotion | Explicit version transition; prior basis retained |
| CAREER-035 | Recruitment would exceed 10,000 living people | Block pending valid population resolution |
| CAREER-036 | Rank differs from position | Independent values/history preserved |
| CAREER-037 | Acting title conflicts with clearance | No clearance escalation |
| CAREER-038 | Rebuild projection from events | Deterministic same result |
| CAREER-039 | Unauthorised panel-record access | Denied and audited |
| CAREER-040 | Out-of-order career event | No corrupt transition; reconciliation required |
| CAREER-041 | Specialist move without promotion | Assignment changes; rank unchanged |
| CAREER-042 | Occupied position abolished | Preserve history; controlled transition |
| CAREER-043 | Break and re-entry | Service follows explicit approved credit policy |
| CAREER-044 | Player views own career | Only authorised personal data exposed |

## 16. Non-functional and operational requirements

- Determinism: identical event history and policy version produce identical projections/calculations.
- Auditability: every material decision has authority, effective time, evidence and policy version.
- Idempotency: retries/replays cannot duplicate transitions.
- Temporal integrity: all durations use simulation time; no wall-clock advancement.
- Historical integrity: corrections supersede, never erase.
- Privacy: confidential panel, disciplinary and restricted personnel information is permission-filtered.
- Storage efficiency: store canonical facts once; reference personnel, rank, position, qualification, roster and HR records. Projections are rebuildable. Compress representation, never semantic meaning.
- NPC consistency: same rules and event contracts as player.
- Explainability: provide permitted decision reasons without disclosing protected deliberations or hidden facts.
- Recovery: rebuild current projections from durable career events and authoritative references.

## 17. Source traceability

Primary source divisions: S24 police personnel and career simulation; S23 police governance/structure (BP-05-owned rank framework); S25 staffing/deployment (BP-08/BP-10 interface); S26 command/internal governance; S08 employment/professional life (BP-33 HR ownership); S41 time/calendar (BP-37); S42 causality (BP-35); S43 AI/narrative/player agency; S46 database/persistence (BP-38/BP-39); S48 permissions (BP-42); S50 testing (BP-43); S52 canon/versioning (BP-44). Detailed requirement and test IDs remain in SALTWATER-52-TO-44-CROSSWALK.md and must be semantically reconciled before approval.

## 18. Open decisions

1. Exact rank ladder, titles and grade structure (BP-05/user canon).
2. Minimum service and time-in-rank per promotion.
3. Recruit training duration, probation duration, review intervals and assessment standards (BP-32/BP-33).
4. Promotion examinations, panel composition, scoring, tie-break and appeal windows.
5. Whether every promotion requires a vacant post.
6. Exact entry routes and experienced-officer/re-entry rules.
7. Service-credit treatment for prior service, breaks, suspension, unpaid leave, part-time service and secondment.
8. Retirement notice lead times and benefits administration (BP-34).
9. Whether early departure changes a Chief term's cumulative tenure; the five-year term, one renewal and ten-year maximum are fixed.
10. Chief appointment authority, succession and post-Chief placement (BP-05).
11. Appeal effects and whether specific transitions are paused.
12. Permitted performance evidence and weighting; prohibited inputs remain excluded.
13. Acting appointment maximum duration and concurrent-role compatibility.
14. Final state dimensions/vocabularies reconciled with BP-06/BP-33.
15. Medical separation, reinstatement and death-in-service subtypes.

These decisions do not erase the specified invariants. Resolve them before implementing affected policy paths; do not silently invent values.

## 19. Completion criteria

BP-07 may become DESIGNED only after semantic reconciliation of every mapped source requirement/test, resolution or explicit acceptance of canonical open decisions, contract reconciliation with BP-05/BP-06/BP-08/BP-31/BP-32/BP-33/BP-34/BP-35/BP-37/BP-38/BP-39/BP-42, and user review/approval.

Implementation, testing and verification remain separate states. This document authorises no database schema change, migration, seed, import or Neon write.
