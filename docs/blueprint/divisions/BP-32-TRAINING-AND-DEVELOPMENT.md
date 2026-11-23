# BP-32 — Training and Development

**Division:** BP-32  
**Title:** Training and Development  
**Specification version:** 1.0  
**Status:** DESIGNED_DRAFT  
**User approval:** PENDING  
**Implementation / test execution / verification:** NOT_STARTED  
**Authority:** Adopted Saltwater BP-01–BP-44 master blueprint, original 52-division source and current 52→44 crosswalk. Fictional simulation specification; it neither imports a real-world jurisdiction nor authorises database writes.

## 1. Purpose

BP-32 defines the police training and professional-development system: learning requirements, curricula, courses, instructors, enrolment, scheduling, delivery, attendance, assessment, qualification awards, renewal, remediation and lifelong training history. It supports recruit formation, routine competence, specialist capability, supervisory and command development, and continuing professional development.

The system must distinguish exposure to instruction, attendance, completion, demonstrated competence, assessment pass, qualification award, qualification validity, appointment, authority, clearance, deployment and operational readiness. These are separate facts with separate owners. No one status silently implies another.

BP-32 supplies authoritative, versioned training and qualification evidence to the personnel, career, unit and governance systems. It does not promote officers, appoint them, grant legal powers, assign units, impose discipline or manufacture competence. The player retains control over their officer's participation and choices.

## 2. Binding Saltwater canon

1. Saltwater is one fictional sovereign city-state, one playable city and one jurisdiction. No training provider or course creates a second playable territory.
2. The hard cap is **10,000 living people total**, including police, instructors, candidates and external-provider staff represented as people. Each person is counted once across every role.
3. Police planning baseline is approximately 500 individually recorded personnel, within the total cap.
4. At least **10,000 businesses** remain in the city. Training providers may be public, police-operated, commercial or partner organisations represented through BP-04.
5. Police is the deepest simulation. Other education and training organisations are represented only to the depth needed for coherent police training and city context.
6. Text is the permanent primary interface. No essential training workflow depends on graphics.
7. No simulation time advances while the player is absent or the game is paused. Wall-clock time does not progress course sessions, probationary learning, qualification expiry or training deadlines.
8. Every person has one canonical BP-03 identity. A person materially relevant to police activity is permanently promoted to full persistent simulation; they are never downgraded.
9. NPC knowledge is limited to what they observed, received or were authorised to access.
10. Hidden culprit, accomplice and perpetrator truth is protected. No training record, scenario, instructor dialogue, assessment feedback, generated narrative or report may reveal it unless the player types exactly `bingo`. No unsolicited investigation hints are permitted.
11. Player and NPC rules are consistent. The player directs their officer's course participation and actions; no automatic player completion or forced choice.
12. This specification authorises no Neon schema, migration, seed, import, bulk write or upload.

## 3. Scope

### 3.1 Included
- Police training policy catalogue and versioned learning requirements.
- Initial recruit training, induction, probationary learning and foundational police education.
- Mandatory, role-based, refresher, specialist, supervisory, command and continuing-development programmes.
- Course catalogue, modules, learning outcomes, lesson plans, materials and controlled curriculum versions.
- Instructor, trainer, assessor, moderator and external-provider records/references.
- Prerequisites, eligibility, enrolment, waiting lists, cohort formation and scheduling.
- Course delivery, sessions, attendance, participation, interruptions and completion decisions.
- Written, oral, practical, observed, scenario-based and simulated assessments.
- Assessment criteria, marks, assessor evidence, moderation, reassessment and appeal/review.
- Qualification and certification award, issuer, scope, level, conditions, validity, renewal, suspension and revocation.
- Prior learning, equivalence, exemptions, waivers and recognition decisions.
- Individual development plans, learning needs, remedial learning and progression evidence.
- Training resource requests and use, with facilities/equipment supplied by BP-09.
- Training records, audit history, reporting, retention and interfaces to career/role eligibility.

### 3.2 Excluded
- Canonical person identity, life history and population accounting: BP-03.
- Training-provider, school, college, organisation and business identity: BP-04.
- Police hierarchy, rank, position, grade, authority, powers, clearance and post prerequisites: BP-05.
- Authoritative police personnel/service master: BP-06.
- Career lifecycle, promotion, appointment, retirement and career decisions: BP-07.
- Unit membership, posting, roster, deployment and operational tasking: BP-08.
- Police facilities, vehicles, equipment, stores and asset maintenance: BP-09.
- Professional-standards findings and disciplinary adjudication: BP-31.
- General employment, leave, payroll and HR administration: BP-33.
- Finance, purchasing and budget ledger: BP-34.
- Canonical simulation time and event execution: BP-35/BP-37.
- Canonical records infrastructure, persistence, security and configuration governance: BP-38/BP-39/BP-42/BP-44.

## 4. Ownership and system boundaries

| Concern | Authoritative owner | BP-32 responsibility |
|---|---|---|
| Person identity, living status and population cap | BP-03 | Reference person ID; never create a parallel person |
| Provider/business/institution identity | BP-04 | Reference provider and premises |
| Rank, position, grade, authority, powers, clearance and post requirements | BP-05 | Define training prerequisites as inputs to controlled role requirements; never grant authority |
| Police personnel/service record | BP-06 | Attach training events and qualification references to personnel ID |
| Career eligibility, promotion, appointment, retirement | BP-07 | Supply verified learning/qualification evidence; do not decide career outcome |
| Unit membership, roster and deployment | BP-08 | Supply competence/readiness status; do not assign or deploy |
| Training facilities and physical/digital equipment assets | BP-09 | Request, reserve and record use; no asset ownership |
| Governance policy approval and delegation | BP-30 | Apply authorised policy versions and record approvals |
| Misconduct, complaints and discipline | BP-31 | Accept authorised referrals; remedial training is not a misconduct finding or sanction |
| Employment, leave and HR administration | BP-33 | Exchange enrolment availability and approved absence references |
| Budget, procurement, payment and accounting | BP-34 | Supply course cost/resource requirements; no ledger mutation |
| Simulation causality and NPC actions | BP-35 | Emit/consume training events only through authorised simulation processing |
| Canonical clock, calendar and schedules | BP-37 | Read and schedule against simulation time |
| Record schema, audit and persistence | BP-38/BP-39 | Use canonical record contracts; preserve event history |
| Permissions and restricted information | BP-42 | Enforce role-based access and confidentiality |
| Test evidence and release quality | BP-43 | Expose deterministic acceptance behaviour |
| Policy/curriculum change control | BP-44 | Version and retire curricula without rewriting historical outcomes |

A boundary conflict must be resolved by the named owner. BP-32 may publish an eligibility fact such as “qualification Q is valid through date D”; BP-05/BP-07/BP-08 decide what that fact means for authority, career or deployment under their own rules.

## 5. Core invariants

1. Every training record references one canonical person or an explicitly non-person organisational/provider reference.
2. A course, module, session, assessment, result, qualification and credential has a stable ID and immutable provenance.
3. Curriculum, policy, learning outcomes, assessment criteria and qualification rules are versioned and effective-dated.
4. Historical attendance and outcomes remain tied to the exact course and assessment versions used at the time.
5. Enrolment is not attendance; attendance is not completion; completion is not competence; a pass is not an award until an authorised award decision exists.
6. A qualification does not itself grant rank, appointment, authority, legal power, clearance, unit membership or deployment.
7. A qualification's expiry or suspension changes only BP-32's credential state. Other systems consume the event and apply their own authorised rules.
8. No skill or qualification appears without a recorded learning, prior-learning, equivalence or authorised award basis.
9. No failure is inferred from absence, an interrupted session or an incomplete record. State and reason remain explicit.
10. Assessments preserve criteria, attempts, assessor identity, evidence, result, moderation and appeal history.
11. A course may have multiple versions, providers, instructors, sessions and cohorts without duplicating the learner's identity.
12. Individual competence and unit-level capability/readiness are distinct.
13. Exemptions, waivers and prior-learning recognition are explicit, scoped, justified, approved and reviewable.
14. Instructor eligibility is checked against the course version and subject being taught or assessed.
15. Conflicts of interest are disclosed and handled under configured separation/moderation rules.
16. No training event, course clock, deadline, expiry, NPC learning or background process advances while simulation time is paused or the player is absent.
17. No training scenario can expose hidden crime-generation truth or provide unsolicited investigation direction.
18. All living instructors, candidates and provider personnel count once within the 10,000-person cap.
19. No training cohort, course, provider or resource shortage may silently create people, staff, facilities or assets.
20. Corrections are append-preserving and attributable; they do not erase prior attempts, awards or decisions.
21. The same configured training rules apply to player and NPC officers; differences must arise from recorded choices, eligibility, availability and outcomes.
22. A training requirement cannot be silently waived because a player or NPC needs a role.
23. No course or credential is assumed to exist merely because a role or scenario would benefit from it; configuration must define it.
24. No real-world law, licence, certification body, curriculum or jurisdiction is presumed. All standards are fictional, configurable and versioned.

## 6. Domain model and principal records

The following logical entities are required. Physical schema and compact storage representation belong to BP-38 and BP-39.

| Entity | Essential attributes and relationships |
|---|---|
| TrainingPolicy | policy_id, version, owner, approval, effective interval, status, scope, rule references |
| LearningRequirement | requirement_id, version, target role/post/unit/specialism, mandatory flag, prerequisites, renewal rule, effective interval |
| Course | course_id, catalogue code, title, category, provider reference, delivery mode, status |
| CourseVersion | version_id, course_id, curriculum version, learning outcomes, syllabus, assessment plan, prerequisites, duration, effective interval |
| Module | module_id, version_id, sequence, outcomes, content references, required/optional status |
| LessonPlan | lesson_id, version_id, instructor guidance, activities, scenario references, controlled materials |
| Provider | provider_id, BP-04 organisation reference, provider status, approved scope, contact and contract references |
| InstructorCredential | credential_id, person_id, subject/scope, issuer, award basis, validity, restrictions |
| InstructorAssignment | assignment_id, person_id, course/session, teaching/assessing/moderating role, authority check, dates |
| Cohort | cohort_id, course_version_id, capacity, enrolment window, state, provider and delivery mode |
| Enrolment | enrolment_id, person_id, cohort_id, eligibility snapshot/reference, request, decision, state |
| Session | session_id, cohort_id, module, start/end simulation time, venue/resource refs, instructor refs, status |
| Attendance | attendance_id, session_id, person_id, presence intervals, participation status, reason/source |
| CompletionDecision | decision_id, enrolment_id, completion criteria/version, decision, actor, rationale, evidence |
| Assessment | assessment_id, course_version_id, method, criteria/version, pass rule, assessor requirements |
| AssessmentAttempt | attempt_id, enrolment_id, assessment_id, attempt number, schedule, submission/evidence, result |
| AssessmentResult | result_id, attempt_id, marks/criteria outcomes, pass/fail/deferred/void, assessor, rationale, moderation |
| Qualification | qualification_id, catalogue code, scope, level, prerequisites, renewal and validity policy |
| CredentialAward | award_id, person_id, qualification_id, course/recognition basis, issuer, date, effective interval, status |
| RecognitionDecision | recognition_id, person_id, prior-learning evidence, equivalence mapping, scope, decision, approver |
| DevelopmentPlan | plan_id, person_id, objectives, skill gaps, agreed actions, review dates, status |
| RemediationPlan | plan_id, linked result/requirement, learning actions, support, reassessment criteria, status |
| ReviewOrAppeal | review_id, decision reference, grounds, reviewer, conflict check, outcome, effective date |
| TrainingResourceBooking | booking_id, session, BP-09 asset/facility references, period, approval, return/condition reference |
| TrainingEvent | event_id, event type, subject references, actor, simulation timestamp, policy/version, provenance |
| TrainingRecordView | derived view of a person's chronological learning/credential history; never authoritative over source events |

### 6.1 Identity and uniqueness
- Person references use BP-03 stable person IDs. Police service links use BP-06 personnel IDs and must reconcile to one person.
- A person may hold multiple concurrent roles (learner, instructor, assessor) without duplicate identity records.
- Course codes, qualification codes and provider codes are unique within their issuing namespace and version policy.
- Attempt numbers are unique within an enrolment/assessment pairing.
- Session attendance is unique per person/session, with corrections represented as amendments.
- Credential awards have unique award IDs; replacement, renewal and reinstatement create linked records, not overwrites.

### 6.2 Evidence and provenance
Each material decision records actor, authority, simulation time, policy/curriculum/criteria version, input evidence references, rationale, result, review state and supersession link. Source documents and submissions remain distinct from derived summaries.

## 7. Training catalogue and curriculum lifecycle

Course categories may include recruit/basic police training, induction, operational skills, patrol, emergency response, communications, first aid/medical response, safeguarding, interviewing, evidence handling, crime-scene awareness, forensic awareness, digital skills, intelligence, surveillance, custody, legal procedure, driving/vehicle operation, weapons/force where configured, ethics, professional standards, leadership, supervision, command, specialist practice, instructor development and continuing professional development.

A category is a classification, not proof that a particular course exists. Every usable course must have a controlled catalogue entry and at least one approved version.

Course lifecycle: proposed → designed → reviewed → approved → published → open for enrolment → active delivery → completed/withdrawn → archived. A version may be suspended or superseded. Historical cohorts retain their original version.

Curriculum changes require a new version and BP-44 change record. Material changes to outcomes, prerequisites, assessment criteria, pass rules, duration or credential validity cannot be retroactively applied to learners already assessed unless a separately authorised corrective process explicitly requires it.

Learning outcomes must be observable and assessable. Syllabus content, instructional material, scenarios and assessment criteria must be aligned. A course may be classroom, practical, field-supervised, remote, blended or simulation-based, as explicitly configured.

## 8. Requirements, prerequisites and eligibility

A requirement can attach to a role, post, specialist function, grade, unit capability or individual development plan. BP-05 owns the role/post and authority catalogue; BP-32 stores the training requirement and supplies the evidence of fulfilment.

Eligibility may depend on prior courses, valid credentials, experience, service status, medical/fitness evidence where configured, security clearance references, instructor approval, equipment availability or prerequisite assessment. BP-32 must not invent missing evidence or infer a clearance from a course.

Eligibility is evaluated against a versioned rule set at enrolment and rechecked before delivery or award where the policy requires. The system records the exact result and input references. A later change does not silently rewrite the earlier eligibility decision.

Equivalent prior learning and external qualifications require mapped outcomes, source/issuer verification appropriate to the fictional policy, scope equivalence, validity comparison and an authorised recognition decision. Partial equivalence may satisfy only named modules or outcomes.

Exemptions and waivers must specify the exact requirement waived, person, scope, effective interval, reason, approving authority and review/expiry condition. A waiver never creates a credential or competence that was not awarded.

## 9. Enrolment, cohorts and scheduling

Enrolment states: requested, eligibility-pending, eligible, waitlisted, approved, enrolled, declined, withdrawn, cancelled, deferred, suspended, completed or closed. Transitions require defined actor/authority, reason and event.

Cohort capacity is an explicit configured limit based on instructor, venue, equipment, safety and delivery constraints. Capacity cannot be exceeded by concurrent enrolment transactions. Waitlist ordering and priority are policy-driven and auditable; no hidden favouritism.

Scheduling uses BP-37 canonical simulation time and references the provider calendar, candidate availability, instructor availability, roster/leave constraints, venue and equipment availability. BP-32 proposes and manages training schedules; BP-33/BP-08 remain authoritative for employment/leave and deployment/roster conflicts.

The system must support overlapping courses, multi-session programmes, repeat sessions, cancelled sessions, rescheduling, partial attendance, interruptions and transfer between cohorts. A transfer preserves completed module/assessment evidence only where course-version equivalence is explicitly approved.

No course duration, attendance, deadline or expiry advances during pause/player absence. On resume, the simulation continues from the exact frozen state; it does not catch up wall-clock time.

## 10. Delivery, attendance and completion

Session states: planned, confirmed, ready, in-progress, paused, interrupted, completed, cancelled or void. Every transition records simulation time, actor/system authority, reason and relevant resource/instructor references.

Attendance records presence intervals and distinguish present, late, partial, absent, excused, withdrawn, removed, remote participation and unverified. Attendance corrections retain the original assertion and correction provenance.

Participation may be recorded separately from attendance, but subjective instructor impressions must be attributed and must not be converted automatically into an assessment result.

Completion rules are course-version specific. They may require minimum attendance, module completion, practical participation, assessment outcomes or portfolio evidence. A learner who attends every session may still fail an assessment; a learner who misses a session may be eligible for an approved make-up. Neither outcome is inferred without the configured rule and decision.

Completion decision states include pending, completed, not-completed, deferred, withdrawn and void. Completion is an administrative course outcome, not a qualification award.

## 11. Assessment and reassessment

Assessment methods include written, oral, practical, observed performance, scenario exercise, simulated operation, portfolio, project and structured demonstration. Multiple methods may be combined.

Each assessment version defines outcomes, criteria, marking rubric, pass threshold or competency rule, required evidence, permitted aids, assessor qualification, moderation requirement, reasonable adjustments, attempt limits, reassessment rules and result categories.

Attempt states include scheduled, in-progress, submitted, awaiting-marking, marked, moderated, appealed, void and closed. Result categories include pass, fail, conditional, deferred, absent, incomplete and invalid. The policy must state which categories count toward attempts and progression.

Assessment records preserve the candidate's submitted work or performance evidence, criteria-level outcomes, assessor notes, result rationale and any moderation. A result cannot be silently edited; correction or appeal creates a linked decision with provenance.

Reassessment must follow the course-version rule. It may require targeted remediation, a waiting period, a different assessor, a new scenario or a capped number of attempts. Failure does not automatically terminate employment, demote rank, remove authority or trigger discipline. Any downstream consequence belongs to its owning division and requires an explicit rule.

Appeals/reviews support grounds, submission, evidence, independent reviewer where configured, conflict checks, decision and outcome. A successful appeal may void, amend or require a new assessment; original records remain visible in history.

## 12. Qualification and credential lifecycle

Qualification states: proposed, approved, awarded, active, nearing-expiry, expired, suspended, revoked, superseded or surrendered. A credential records issuer, award basis, scope, level, effective date, validity interval, conditions, renewal requirements and linked evidence.

Award requires a defined authority and evidence basis. Passing an assessment is necessary only where the applicable qualification rule says so; it is not by itself an award. Awarding authority must be separate from ordinary course administration where policy requires.

Renewal may require refresher learning, repeat assessment, practice evidence or review. Renewal creates a new credential interval linked to the prior award. Expiry is computed only from canonical simulation time and configured effective-date rules.

Suspension or revocation requires an authorised, attributable decision and stated scope. A correction to an erroneous award is distinguished from misconduct. A credential may be restricted for one function while remaining valid for another if its scope permits.

A credential is not a rank, appointment, statutory power, legal authority, security clearance, employment contract or deployment order. It is evidence of a defined training/qualification status only.

## 13. Instructor, assessor and provider controls

Instructor and assessor records identify person, subject scope, credential/experience basis, validity, permitted activity, restrictions and review history. Assignment checks that the person is qualified for the course version, available, not conflicted and authorised to perform the assigned teaching or assessment role.

Teaching, assessing and moderating may be combined only where policy permits. A conflict of interest, personal relationship, prior involvement, complaint or other configured disqualifier must trigger recusal, independent review or moderation.

External providers are BP-04 organisations. Provider approval is scoped by course/subject, delivery method, location and validity. Provider approval does not replace individual instructor credentials or BP-32's assessment of the delivered course evidence.

Instructor performance and course quality feedback may inform development and quality review, but an adverse allegation is not a finding. Misconduct is referred to BP-31; employment action belongs to BP-33; appointment and authority remain with BP-05/BP-07.

## 14. Individual development and competence

A development plan links a person to objectives, observed skill gaps, target role or capability, agreed activities, support, owner, milestones and review dates. Plans may be initiated by the individual, supervisor or authorised training manager under configured rules.

Competence is represented by scoped evidence: skill/outcome, level, evidence source, assessor, assessment date, validity or review date, conditions and confidence/limitations. An unassessed skill claim remains a claim, not verified competence.

Development records can include coaching, mentoring, supervised practice, self-study, secondment learning, workshops and formal courses. Informal activity must not be presented as a formal qualification unless the relevant recognition process awards it.

The system supports individual variation in learning pace and outcome. NPC officers do not acquire skills merely because their role would benefit from them. Any learning or skill development is an explicit, causal event with recorded source and result.

## 15. Remediation, failure and welfare

Remediation may include repeat instruction, coaching, supervised practice, adjusted learning materials, additional assessment or a revised plan. It must be proportionate to the identified gap and linked to the original evidence.

A failure or learning difficulty is not automatically misconduct, incompetence in every domain, or a career-ending event. Any temporary restriction on duties or role eligibility is decided by BP-05/BP-07/BP-08 under explicit policy, not imposed by BP-32.

Reasonable adjustments and accommodations are recorded with restricted access and only the minimum necessary detail. Sensitive health information remains with its authoritative owner; BP-32 stores an eligibility/adjustment reference and operational instructions, not an unnecessary medical dossier.

Where a learner is distressed, injured or unable to continue, session safety and welfare handling are recorded and referred to the appropriate owner. No training scenario may use graphic or coercive content as a shortcut to assessment.

## 16. Training scenarios and hidden information

Scenarios may test decision-making, communication, safety, evidence handling, procedure, teamwork and specialist skills. They may use fictional cases and synthetic data or carefully controlled references to existing game records.

Scenario design must specify learning objectives, fictional status, permitted information, expected observable behaviours, scoring criteria and debrief boundaries. A scenario is not a live case and must not mutate an actual case, evidence record or NPC status unless an explicitly authorised simulation event does so.

Where a scenario references a live or historical case, only authorised, redacted information may be used. No assessment, feedback, instructor, NPC or generated summary may disclose the true perpetrator, accomplice or hidden causal solution. The exact `bingo` trigger remains exclusive to the player-facing reveal mechanism; training content must not become an indirect reveal channel.

The player must not receive hints about what to investigate in a live case under the guise of training. Training may teach general methods and competencies without steering a current investigation.

## 17. Resource and capacity management

Training venues, vehicles, equipment, consumables and specialist facilities are BP-09 assets or BP-04 premises. BP-32 creates bookings and use records referencing those assets; it does not create or own them.

Resource reservations must be time-bounded, conflict-checked and released or reconciled after cancellation/completion. Damaged, missing or consumed assets are reported to BP-09 through a traceable event.

Course capacity considers instructor-to-learner ratios, equipment availability, room/venue capacity and configured safety limits. The system must not solve a shortage by silently increasing capacity or generating staff/assets.

Training demand and instructor staffing must remain compatible with the police personnel baseline and the total population cap. A provider employee who is already a person in BP-03 is not counted again when acting as an instructor.

## 18. Interfaces and event contracts

### 18.1 Inputs
- Person/personnel references and service status from BP-03/BP-06.
- Role, post, unit capability and qualification prerequisites from BP-05/BP-08.
- Career requirements and eligibility requests from BP-07.
- Facility, vehicle, equipment and resource availability from BP-09.
- Approved policies/delegations from BP-30 and referrals from BP-31.
- Employment availability/leave constraints from BP-33.
- Provider, premises and organisation references from BP-04.
- Simulation time, pause state and event sequencing from BP-35/BP-37.
- Authorised user actions and permissions from BP-40/BP-42.

### 18.2 Outputs
- Enrolment, attendance, completion and assessment events.
- Verified competence and qualification award/validity events.
- Renewal, expiry, suspension, revocation and correction events.
- Training requirement status and evidence references for BP-05/BP-07/BP-08.
- Course and resource demand references for BP-09/BP-34.
- Development-plan and learning-history views for authorised supervisors and personnel.
- Quality, capacity and training-gap reports for authorised governance roles.

### 18.3 Event envelope
Every authoritative event carries event_id, event_type, subject reference, actor/system identity, authority reference, simulation timestamp, source record/version, policy/curriculum version, correlation reference, prior-state reference, new-state reference and provenance. Idempotency keys prevent duplicate enrolment, attendance, award or expiry events. Replayed events must not create duplicate credentials or alter an already-final decision without a new authorised event.

## 19. State transitions and lifecycle summary

| Record | Principal transitions |
|---|---|
| Course version | draft → reviewed → approved → published → active → superseded/withdrawn/archived |
| Cohort | planned → open → filling → confirmed → active → completed/cancelled |
| Enrolment | requested → eligibility-pending → eligible → waitlisted/approved → enrolled → completed/withdrawn/deferred/cancelled |
| Session | planned → confirmed → ready → in-progress ↔ paused/interrupted → completed/cancelled/void |
| Assessment attempt | scheduled → in-progress → submitted → marking → moderated → closed; appeal/void via linked decision |
| Result | pending → pass/fail/conditional/deferred/absent/incomplete/invalid → reviewed/corrected |
| Credential | proposed → approved → awarded/active → nearing-expiry → renewed/expired/suspended/revoked/superseded |
| Development plan | proposed → agreed → active → review-due → completed/revised/paused/closed |
| Remediation | identified → planned → active → reassessment-due → resolved/continued/closed |
| Provider approval | proposed → assessed → approved → active → suspended/expired/withdrawn |

Invalid transitions are rejected with a reason and audit event. A correction never deletes the earlier state transition.

## 20. Permissions and information handling

Access is role- and purpose-based. Learners may view their own enrolments, attendance, results, credentials and permitted feedback. Instructors see assigned cohorts and the minimum learner information needed to deliver/assess. Assessors see evidence for assigned assessments. Training administrators manage catalogues and enrolment within delegated scope. Commanders see role-readiness summaries only where authorised. Auditors/reviewers receive controlled read access.

Restricted health/adjustment, personnel, security and case-linked information must not be copied into general training views. Sensitive scenario source material is compartmentalised. Every access to restricted records is attributable and auditable.

No person may approve their own qualification award, appeal or waiver where separation is required by policy. Privileged overrides require reason, authority and audit. Deletion is not an ordinary correction mechanism.

## 21. NPC behaviour and player agency

NPC training participation, scheduling, attendance, assessment and development occur only through BP-35 while simulation time advances. NPC capability changes only after a valid learning or recognition event and recorded outcome.

NPCs may request training, be nominated, be waitlisted, decline where policy permits, fail, pass, seek review or complete remediation according to their individual circumstances and knowledge. They must not know hidden scenario answers or live case truth beyond authorised information.

The player's officer receives the same catalogue, requirements, schedule constraints, evidence standards and appeal rights as NPC officers. The player chooses whether to enrol, attend, participate, submit work, request support, appeal or pursue optional development. Mandatory training may affect eligibility only through explicit rules in owning systems; the interface must explain the recorded requirement and status without silently changing the player's career or deployment.

No player training activity is auto-completed, auto-failed or auto-selected. No simulation time advances while the player is away.

## 22. Failure handling and exceptional conditions

The system must explicitly handle:
- course cancellation, provider withdrawal or instructor unavailability;
- venue/equipment failure, resource conflict and safety interruption;
- late arrival, partial attendance, absence and disputed attendance;
- illness, injury, welfare concern and authorised adjustment;
- incomplete, lost, corrupted or duplicated assessment submission;
- assessor conflict, unavailable assessor and moderation disagreement;
- failed, conditional, deferred, void or appealed assessment;
- reassessment limit reached, remediation unavailable or course superseded;
- incorrect award, wrong person, identity merge or person-status change;
- duplicate enrolment, concurrent capacity race and repeated event delivery;
- expired, suspended, revoked or disputed external credential;
- provider closure, changed ownership or loss of approval;
- policy/curriculum change during an active cohort;
- pause/resume, interrupted simulation and restoration from backup;
- access denial, attempted privilege escalation and restricted-data leakage;
- population-cap pressure affecting instructor/candidate availability.

Each exception records detection, affected records, actor/system, decision authority, containment, recovery action and final state. Unresolved ambiguity is flagged; the system must not invent a pass, qualification, attendance or waiver.

## 23. Reporting and derived views

Reports may include course demand, enrolment and waiting lists, completion rates, assessment outcomes, qualification validity, renewal demand, instructor capacity, resource utilisation, role requirement coverage, individual development history and organisation-level capability gaps.

Reports are derived, versioned by generation time and source watermark, and must be reproducible. They cannot overwrite source events or become an alternative personnel/qualification authority.

Aggregates must distinguish unique people from enrolment counts, attempts, credentials and course seats. Multiple courses or roles do not multiply the population count.

## 24. Retention, correction and audit

Training history is append-preserving and queryable over time. Retention and archival periods are fictional configurable policy. A record may be corrected, restricted, superseded or lawfully retired under authorised policy, but material history and provenance remain available to authorised audit.

Corrections identify the original record, corrected fields, reason, requester, approver, simulation time and downstream notifications. If a correction affects a qualification or role requirement, BP-32 emits a correction event; BP-05/BP-07/BP-08 determine downstream action.

Audit covers catalogue changes, policy approvals, instructor assignments, enrolment decisions, attendance amendments, assessment marks, moderation, awards, renewals, waivers, appeals, access and exports.

## 25. Dependencies and ordering

BP-32 depends on BP-01 for canon and agency; BP-03 for person identity/population; BP-04 for providers; BP-05 for role/authority catalogues; BP-06 for personnel references; BP-07 for career requirements; BP-08 for deployment constraints; BP-09 for resources; BP-30 for governance; BP-31 for standards referrals; BP-33 for HR availability; BP-35/BP-37 for event/time behaviour; BP-38/BP-39 for records and persistence; BP-42 for permissions; BP-43 for test evidence; BP-44 for change control.

A missing upstream reference blocks the affected transaction only. It must not create a duplicate record or silently substitute a guessed value.

## 26. Storage and performance requirements

Store shared course, curriculum, policy, assessment and qualification definitions once; reference versions from enrolments and outcomes. Store attendance and assessment events as compact structured records with references to large source materials rather than copying full content into every view.

Avoid repeated snapshots of static curriculum text, duplicated person data, unbounded generated narratives and redundant derived metrics. Preserve original learner submissions, instructor notes and meaningful narrative losslessly where required. Compression may reduce representation size but never remove meaning, uncertainty, provenance or auditability.

High-volume attendance, event and assessment histories must be queryable by person, course, cohort, qualification and effective date. Indexing and retention choices belong to BP-38/BP-39 and must be measured before database deployment.

## 27. Acceptance tests

The following are required acceptance tests, not evidence that implementation or execution has occurred. Each test must produce reproducible evidence and reference the applicable source requirements.

1. **TRN-AT-001** — A course cannot be published without an identified owner, approved version and learning outcomes.
2. **TRN-AT-002** — A course version has a stable unique identifier.
3. **TRN-AT-003** — A curriculum amendment creates a new version and preserves the prior version.
4. **TRN-AT-004** — Historical enrolments remain linked to the version originally selected.
5. **TRN-AT-005** — A course category alone cannot create a usable course.
6. **TRN-AT-006** — Every qualification catalogue entry defines scope and an award authority.
7. **TRN-AT-007** — Every mandatory learning requirement identifies its target role or function.
8. **TRN-AT-008** — A requirement version has an effective interval and approval reference.
9. **TRN-AT-009** — A changed prerequisite does not rewrite an earlier eligibility decision.
10. **TRN-AT-010** — A missing prerequisite blocks enrolment where the rule requires it.
11. **TRN-AT-011** — An authorised exemption identifies the exact waived requirement and scope.
12. **TRN-AT-012** — An exemption does not create a qualification award.
13. **TRN-AT-013** — Prior learning is recognised only through a recorded equivalence decision.
14. **TRN-AT-014** — Partial equivalence satisfies only the mapped outcomes.
15. **TRN-AT-015** — An external credential records issuer, scope, validity and verification basis.
16. **TRN-AT-016** — A provider reference resolves to BP-04 without creating a duplicate organisation.
17. **TRN-AT-017** — A person reference resolves to one canonical BP-03 identity.
18. **TRN-AT-018** — Multiple learner/instructor roles do not duplicate the person.
19. **TRN-AT-019** — Enrolment cannot exceed cohort capacity under concurrent requests.
20. **TRN-AT-020** — A waitlist decision follows the configured ordering rule and is auditable.
21. **TRN-AT-021** — An ineligible applicant cannot be enrolled through an ordinary path.
22. **TRN-AT-022** — A privileged override records authority and rationale.
23. **TRN-AT-023** — Duplicate enrolment requests are idempotent.
24. **TRN-AT-024** — Withdrawal preserves the enrolment and its prior events.
25. **TRN-AT-025** — A cohort cannot start without required instructor and resource confirmations.
26. **TRN-AT-026** — A session references a valid course version and module.
27. **TRN-AT-027** — A session cannot be scheduled in the past relative to simulation time without an explicit historical-import authority.
28. **TRN-AT-028** — Conflicting instructor assignments are detected.
29. **TRN-AT-029** — Conflicting venue or equipment reservations are detected.
30. **TRN-AT-030** — Cancelling a session releases its reservations through traceable events.
31. **TRN-AT-031** — Attendance is unique per person and session.
32. **TRN-AT-032** — Attendance records distinguish full, partial, late, absent and excused states.
33. **TRN-AT-033** — An attendance correction preserves the original assertion.
34. **TRN-AT-034** — An unverified attendance claim cannot satisfy a mandatory attendance threshold.
35. **TRN-AT-035** — Attendance alone cannot create an assessment pass.
36. **TRN-AT-036** — Attendance alone cannot create a qualification.
37. **TRN-AT-037** — Course completion is decided against the exact version's criteria.
38. **TRN-AT-038** — A missing module blocks completion only where configured as mandatory.
39. **TRN-AT-039** — A make-up session records equivalence to the missed learning outcome.
40. **TRN-AT-040** — A learner transfer preserves completed modules only where equivalence is approved.
41. **TRN-AT-041** — An assessment defines criteria and result rules before an attempt begins.
42. **TRN-AT-042** — An assessment identifies the required assessor qualification.
43. **TRN-AT-043** — An attempt has a unique sequence number within its enrolment/assessment.
44. **TRN-AT-044** — A submitted assessment preserves its original evidence.
45. **TRN-AT-045** — An assessment result records criteria-level outcomes.
46. **TRN-AT-046** — A result records assessor identity and decision rationale.
47. **TRN-AT-047** — A failed result cannot be changed to pass by editing the original record.
48. **TRN-AT-048** — A corrected result links to the superseded result and approval.
49. **TRN-AT-049** — A moderated assessment preserves assessor and moderator decisions.
50. **TRN-AT-050** — A required moderation cannot be bypassed by ordinary course administration.
51. **TRN-AT-051** — An assessor with a disqualifying conflict is prevented from marking.
52. **TRN-AT-052** — A reasonable adjustment does not silently alter the learning outcome being assessed.
53. **TRN-AT-053** — An absent candidate receives the configured absent/deferred outcome, not an invented fail.
54. **TRN-AT-054** — An incomplete submission is not treated as a pass.
55. **TRN-AT-055** — A void attempt remains visible with its reason.
56. **TRN-AT-056** — Reassessment obeys the configured attempt limit.
57. **TRN-AT-057** — A required remediation plan links to the originating learning gap.
58. **TRN-AT-058** — Remediation completion does not itself create a pass unless the rule explicitly defines it as assessment evidence.
59. **TRN-AT-059** — An appeal records grounds, reviewer, conflict check and outcome.
60. **TRN-AT-060** — An appeal reviewer cannot be the original decision-maker where separation is required.
61. **TRN-AT-061** — A successful appeal creates a linked correction or reassessment instruction.
62. **TRN-AT-062** — An unsuccessful appeal preserves the original result and reasons.
63. **TRN-AT-063** — Completion and qualification award are stored as separate outcomes.
64. **TRN-AT-064** — Passing a course does not award a credential without an authorised award decision.
65. **TRN-AT-065** — An award records issuer, date, scope, basis and validity interval.
66. **TRN-AT-066** — A credential cannot be awarded to an unresolved or mismatched person identity.
67. **TRN-AT-067** — A credential renewal links to the previous credential.
68. **TRN-AT-068** — Renewal creates a new validity interval without erasing prior validity.
69. **TRN-AT-069** — Expiry is calculated from simulation time, not wall-clock time.
70. **TRN-AT-070** — A suspended credential records authority, scope, reason and effective time.
71. **TRN-AT-071** — A revoked credential retains its award and revocation history.
72. **TRN-AT-072** — A credential correction is distinguishable from disciplinary action.
73. **TRN-AT-073** — A credential does not grant rank or appointment.
74. **TRN-AT-074** — A credential does not grant legal powers or security clearance.
75. **TRN-AT-075** — Qualification expiry does not directly change deployment or career status.
76. **TRN-AT-076** — BP-05/BP-07/BP-08 receive a scoped qualification status event for their own decisions.
77. **TRN-AT-077** — An instructor assignment verifies subject and course-version scope.
78. **TRN-AT-078** — An instructor credential outside its validity interval blocks assignment where required.
79. **TRN-AT-079** — Instructor and assessor roles are separately recorded.
80. **TRN-AT-080** — A provider approval is scoped to its authorised subjects and delivery modes.
81. **TRN-AT-081** — Provider approval does not replace instructor qualification.
82. **TRN-AT-082** — An instructor conflict triggers recusal or the configured independent control.
83. **TRN-AT-083** — A trainer's adverse conduct allegation is not treated as a finding.
84. **TRN-AT-084** — A professional-standards referral links to BP-31 without duplicating its case.
85. **TRN-AT-085** — Employment and leave facts are referenced from BP-33 rather than re-authored.
86. **TRN-AT-086** — Training records link to the authoritative BP-06 personnel reference.
87. **TRN-AT-087** — Career eligibility consumes verified training evidence without BP-32 deciding promotion.
88. **TRN-AT-088** — Unit readiness consumes qualification status without BP-32 assigning personnel.
89. **TRN-AT-089** — Individual competence is not equated with unit capability.
90. **TRN-AT-090** — A development plan identifies objectives, actions, owner and review point.
91. **TRN-AT-091** — Informal learning is not represented as a formal qualification without recognition.
92. **TRN-AT-092** — NPC skill changes require a recorded learning or recognition event.
93. **TRN-AT-093** — NPCs cannot acquire skills solely because their assigned role requires them.
94. **TRN-AT-094** — The player officer is not automatically enrolled in a course.
95. **TRN-AT-095** — The player officer is not automatically marked present, complete or passed.
96. **TRN-AT-096** — Mandatory training affects eligibility only through an explicit owning-system rule.
97. **TRN-AT-097** — Player and NPC eligibility rules are consistent.
98. **TRN-AT-098** — A course scenario is labelled and segregated from live case records.
99. **TRN-AT-099** — A scenario cannot mutate a live case without an authorised event.
100. **TRN-AT-100** — Training feedback cannot reveal hidden culprit or accomplice truth.
101. **TRN-AT-101** — No training output reveals hidden truth before the exact `bingo` command.
102. **TRN-AT-102** — Training content provides no unsolicited live-investigation direction.
103. **TRN-AT-103** — Scenario materials expose only information authorised for that learner.
104. **TRN-AT-104** — Sensitive case-linked material is redacted or access-restricted.
105. **TRN-AT-105** — Simulation pause freezes course sessions and attendance progression.
106. **TRN-AT-106** — Simulation pause freezes qualification expiry and renewal clocks.
107. **TRN-AT-107** — Resume does not apply hidden wall-clock catch-up.
108. **TRN-AT-108** — NPC course participation does not progress while the player is absent.
109. **TRN-AT-109** — Every time-dependent training event uses BP-37 canonical time.
110. **TRN-AT-110** — Duplicate event delivery does not duplicate an award or attendance event.
111. **TRN-AT-111** — Replaying an event sequence preserves deterministic authoritative outcomes where specified.
112. **TRN-AT-112** — A training cohort cannot create unregistered people to fill seats.
113. **TRN-AT-113** — Instructors and learners count once toward the population cap.
114. **TRN-AT-114** — Population admission pressure cannot be bypassed by training enrolment.
115. **TRN-AT-115** — Resource bookings reference BP-09 assets or BP-04 premises.
116. **TRN-AT-116** — A damaged training asset is referred to BP-09 and remains traceable.
117. **TRN-AT-117** — Course costs do not create or post a BP-34 ledger transaction without that owner's process.
118. **TRN-AT-118** — A restricted health/adjustment detail is not exposed to an ordinary instructor.
119. **TRN-AT-119** — Learners can view their own permitted learning and credential records.
120. **TRN-AT-120** — Privileged access and exports are attributable and audited.
121. **TRN-AT-121** — A user without catalogue authority cannot publish a course version.
122. **TRN-AT-122** — A user cannot approve their own waiver or appeal where separation applies.
123. **TRN-AT-123** — A course withdrawal preserves prior learner outcomes.
124. **TRN-AT-124** — Provider closure does not delete issued credentials or history.
125. **TRN-AT-125** — A policy change during an active cohort follows the stated transition rule.
126. **TRN-AT-126** — A superseded curriculum remains available for historical audit.
127. **TRN-AT-127** — A disputed external qualification remains marked disputed pending resolution.
128. **TRN-AT-128** — An incorrect-person award is corrected without deleting the original award event.
129. **TRN-AT-129** — A failed database/event transaction cannot leave an enrolment half-created.
130. **TRN-AT-130** — Concurrent award requests cannot issue duplicate credentials.
131. **TRN-AT-131** — A missing upstream personnel reference blocks only the affected transaction.
132. **TRN-AT-132** — An unresolved authority conflict is flagged rather than guessed.
133. **TRN-AT-133** — Training reports distinguish unique people, enrolments, attempts and course seats.
134. **TRN-AT-134** — Aggregate training reports are reproducible from a stated source watermark.
135. **TRN-AT-135** — Derived reports cannot overwrite authoritative learning events.
136. **TRN-AT-136** — Historical attendance and assessment records remain queryable under retention policy.
137. **TRN-AT-137** — A correction records actor, authority, reason, time and supersession link.
138. **TRN-AT-138** — Curriculum and qualification policy changes are linked to BP-44 change control.
139. **TRN-AT-139** — Every material decision records its policy and criteria version.
140. **TRN-AT-140** — Every course, enrolment, result and credential has provenance.
141. **TRN-AT-141** — The same person is not counted twice when learner and instructor roles overlap.
142. **TRN-AT-142** — A course cannot silently exceed configured instructor-to-learner ratios.
143. **TRN-AT-143** — A course interruption preserves completed work and identifies unfinished requirements.
144. **TRN-AT-144** — A learner returning after interruption resumes only under the applicable versioned rule.
145. **TRN-AT-145** — A waiver expires or is reviewed at its configured time only while simulation time advances.
146. **TRN-AT-146** — A credential nearing-expiry notice is generated only from canonical simulation time and authorised recipient rules.
147. **TRN-AT-147** — A course quality review distinguishes learner feedback from verified findings.
148. **TRN-AT-148** — A training gap report distinguishes missing evidence from proven lack of competence.
149. **TRN-AT-149** — No generated narrative invents a completed course, pass, credential or skill.
150. **TRN-AT-150** — All essential enrolment, attendance, assessment, award and review actions are available through the text-first interface.
151. **TRN-AT-151** — Optional charts or diagrams reconcile to the underlying text records.
152. **TRN-AT-152** — A backup restore preserves curriculum versions, attendance, assessments and credential history.
153. **TRN-AT-153** — A restored event log does not replay awards twice.
154. **TRN-AT-154** — Storage compaction preserves meaningful narrative and all provenance references.
155. **TRN-AT-155** — No Neon write is made by specification or test preparation without explicit user approval.
156. **TRN-AT-156** — A test result is not marked passed until reproducible execution evidence is recorded.
157. **TRN-AT-157** — The fixed 44-division structure is unchanged by BP-32.
158. **TRN-AT-158** — No training policy silently imports a real-world legal or certification regime.
159. **TRN-AT-159** — Qualification scope and validity are independently represented.
160. **TRN-AT-160** — A requirement linked to a post does not itself grant appointment or authority.

## 28. Source traceability

The original 52-division JSON remains authoritative for source wording. The crosswalk maps every requirement/test to one or more target divisions. BP-32 must preserve the full meaning of each mapped item.

| Source ID | Source requirement/test | BP-32 incorporation |
|---|---|---|
| S14.R01 | Education providers, enrolment, attendance, staff, qualifications, schedules and facilities | Sections 6–10, 13, 17–18, 27 |
| S14.R02 | Police recruitment/training and workforce development | Sections 7–15, 21, 25, 27 |
| S14.R03 | Credible education and qualification histories | Sections 6, 12, 14, 24, 26–27 |
| S14.T01 | Qualifications have issuing bodies, dates and valid prerequisites | Sections 8, 12–13; TRN-AT-006–015, 65–81 |
| S23.R01 | Police mandate/structure/rank/position/authority/powers/clearance/divisions/units/reporting | Sections 4, 8, 18, 25; explicit non-ownership and training prerequisite contract |
| S23.R03 | Appointment, promotion, transfer, acting roles, succession, discipline, grievance, standards and retirement | Sections 4, 8, 15, 18, 25; career/standards/HR ownership interfaces |
| S24.R01 | Officer identity/history/recruitment/vetting/training/qualifications/skills/performance/welfare/leave/shifts/pay/discipline/career | Sections 4, 6, 8, 14–15, 18, 21, 24–26 |
| S24.R02 | Recruit entry and career progression through vacancies, standards and required training | Sections 7–8, 14–15, 18, 21, 25 |
| S24.R03 | Deployment reflects organisational need while respecting authority, competence and constraints | Sections 4, 8, 14, 18, 21, 25 |
| S24.T01 | No officer performs a role beyond recorded competence/authority without valid exception | Sections 4–5, 8, 12, 18, 21; TRN-AT-073–088, 160 |

Crosswalk context also includes semantic-audit amendment A04, which expressly identifies BP-32 as owner of training and its interface with police structure, standards and HR. BP-32 does not absorb the responsibilities of BP-05, BP-06, BP-07, BP-08, BP-30, BP-31 or BP-33.

## 29. Open fictional configuration decisions

The following are intentionally unresolved and must not be guessed or treated as approved:
1. Full police course and qualification catalogue, codes and taxonomy.
2. Recruit curriculum, duration, modules, graduation and probation integration.
3. Mandatory training matrix by rank, post, unit, specialist role and authority.
4. Competency levels, assessment rubrics, pass thresholds and moderation rules.
5. Instructor, assessor and provider approval standards.
6. Course capacity, instructor-to-learner ratios and cohort priority rules.
7. Qualification validity periods, renewal intervals and expiry warnings.
8. Reassessment limits, remediation design, appeals and review authority.
9. Prior-learning equivalence, external qualification recognition and waiver authority.
10. Which courses are delivered internally versus by external providers.
11. Training facility, equipment and vehicle catalogue and capacity.
12. Training costs, budget ownership and procurement workflow.
13. Whether and how training status may temporarily restrict particular duties, with owning-system decisions retained.
14. Sensitive learning, welfare and adjustment record access/retention policy.
15. NPC training autonomy, frequency, prioritisation and resource-allocation parameters.
16. Instructor workload, protected training time and roster conflict resolution.
17. Fictional scenario catalogue, assessment security and debrief rules.
18. Qualification suspension/revocation grounds and independent review arrangements.
19. Training record retention and archival schedule.
20. Exact text commands and interface navigation for training workflows.

These decisions may be resolved during later design/configuration review. They do not block the creation of this architecture draft.

## 30. Design completion checklist

- [x] Purpose, scope and exclusions defined.
- [x] Saltwater canon and global invariants preserved.
- [x] Ownership boundaries and cross-system contracts defined.
- [x] Logical entities and identity rules defined.
- [x] Course, curriculum and policy lifecycle defined.
- [x] Prerequisites, enrolment, delivery and attendance defined.
- [x] Assessment, reassessment, qualification and credential lifecycle defined.
- [x] Instructor, provider, development and remediation controls defined.
- [x] Time freeze, NPC knowledge and player agency preserved.
- [x] Population, storage, provenance, permissions and persistence constraints defined.
- [x] Acceptance tests drafted with unique sequential identifiers.
- [x] Source requirement/test traceability included.
- [ ] User review and approval.
- [ ] Implementation.
- [ ] Acceptance test execution and evidence.
- [ ] Cross-system verification.

## 31. Status and next work

**Specification:** DESIGNED_DRAFT  
**User approval:** PENDING  
**Implementation:** NOT_STARTED  
**Test execution:** NOT_STARTED  
**Verification:** NOT_STARTED

Next division: **BP-33 — Human Resources**, preserving the fixed BP-01–BP-44 structure and the same full specification and traceability contract.

No Neon writes have been made or authorised by this specification.
