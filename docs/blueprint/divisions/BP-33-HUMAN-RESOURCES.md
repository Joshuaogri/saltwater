# BP-33 — Human Resources

**Division:** BP-33  
**Title:** Human Resources  
**Specification version:** 1.0  
**Status:** DESIGNED_DRAFT  
**User approval:** PENDING  
**Implementation / test execution / verification:** NOT_STARTED  
**Authority:** Adopted Saltwater BP-01–BP-44 master blueprint, original 52-division source and current 52→44 crosswalk. Fictional simulation specification; no real-world employment law is presumed and no database write is authorised.

## 1. Purpose

BP-33 defines the employment-administration and human-resources system across Saltwater's employers, businesses, public institutions and police service. It records employment relationships, recruitment administration, offers, contracts, job assignments, working patterns, attendance, leave, absence, workforce administration, employee relations referrals and separation transactions. It connects the city's living population to its workplaces without creating duplicate people or competing personnel records.

BP-33 is the authoritative owner of the general employment lifecycle and employment administration. It supports the police workforce through administrative interfaces, but police-specific personnel identity/service dossiers remain BP-06, police career rules remain BP-07, police organisational posts and authority remain BP-05, and police duty assignment/deployment remain BP-08. Finance and payroll posting remain BP-34.

The system must distinguish a person, employer, job, vacancy, application, offer, contract, employment episode, post, shift plan, actual attendance, leave request, approved leave, absence, payroll input, payroll result, discipline referral and separation. These are separate records and states. No one silently implies another.

## 2. Binding Saltwater canon

1. Saltwater is one fictional sovereign city-state, one playable city and one jurisdiction. No employer, worksite or provider creates an additional playable territory.
2. The total population has a hard cap of **10,000 living people**, including residents, police personnel, public servants, business employees, applicants who are living persons, contractors and all other represented people. Each person is counted once across all roles and jobs.
3. The initial planning baseline remains 9,000 residents plus approximately 500 police personnel and a 500-person reserve, subject to the single 10,000 hard cap. Employment does not add a second population count.
4. The city contains at least **10,000 businesses**. BP-33 must support coherent employer/workforce references without requiring every business to have a fully simulated employee roster.
5. Police is the deepest simulation. General city employment is simulated sufficiently to create credible work, schedules, income-related context, absences, movement and police-relevant records, without turning every employer into an equally deep management game.
6. Text is the permanent primary interface. No essential HR transaction depends on graphics or a map.
7. No simulation time advances while the player is absent or the game is paused. Work shifts, leave intervals, probationary administrative dates, recruitment deadlines and employment state transitions do not advance on wall-clock time.
8. Every person has one canonical BP-03 identity. A person materially connected to police activity or a case is permanently promoted to full persistent detail; they are never downgraded or erased.
9. A person may hold multiple jobs, roles or contracts, but must remain one person and cannot occupy incompatible simultaneous locations or shifts without a recorded explanation.
10. NPCs know only information they observed, received or were authorised to access. Employment records cannot expose hidden crime-generation truth.
11. The exact `bingo` command remains the only player-authorised reveal of hidden culprit/accomplice/perpetrator truth. HR records, employer references, work histories, generated reports and notifications must not leak it indirectly.
12. No Neon schema, migration, seed, import, bulk write or upload is authorised by this specification.

## 3. Scope

### 3.1 Included

- General employment policy and employer-facing HR administration.
- Employer, worksite and job references to BP-04 organisations, businesses and premises.
- Job catalogue, job descriptions, grades where applicable, vacancies and workforce plans.
- Recruitment administration: requisitions, applications, eligibility checks, selection, offers, acceptance and onboarding.
- Employment relationships, contracts, amendments, effective dates, renewals and concurrent employment.
- Employment episodes and work assignment history for non-police employers and administrative interfaces for police staff.
- Working patterns, shift plans, planned hours, actual attendance and time records.
- Leave policies, balances, applications, approval, cancellation, return and leave history.
- Absence, lateness, early departure, sickness/other absence categories as configured, notification and return-to-work administration.
- Temporary arrangements, flexible work, secondment/loan administration and workplace changes.
- Employee relations, grievances, workplace concerns, performance-management referrals and case routing.
- HR investigation administration only where explicitly configured; misconduct adjudication belongs to the relevant authority.
- Separation, resignation, termination, redundancy, retirement administration, death notification and post-employment record handling.
- Workforce headcount, vacancies, staffing levels, skills/qualification references and workforce reporting.
- Police administrative HR interfaces for recruitment, leave, attendance, employee status and workforce administration.
- Employer obligations, worker/employer relationships, employment history and work/home schedule interfaces.
- HR record access, confidentiality, retention, correction, provenance and audit.

### 3.2 Excluded

- Canonical person identity, life status and total population ledger: BP-03.
- Employer/business/organisation identity, legal form, premises and business registry: BP-04.
- Police institutional hierarchy, rank, position, grade, authority, powers, clearance and establishment: BP-05.
- Authoritative police personnel dossier, service number and police-specific service record: BP-06.
- Police career progression, promotion, acting appointment, service calculation and mandatory retirement rules: BP-07.
- Police unit assignment, duty roster, deployment, operational staffing and patrol allocation: BP-08.
- Police training delivery, assessment and qualification award: BP-32.
- Finance, accounting, payroll calculation/posting, taxation, budgets, benefits accounting and procurement: BP-34.
- Simulation causality and NPC decision execution: BP-35.
- Social relationships and household relationship authority: BP-36.
- Canonical simulation time: BP-37.
- Record schema, persistence, backup, security and configuration control: BP-38, BP-39, BP-42 and BP-44.
- Professional-standards findings and police discipline adjudication: BP-31.
- Criminal investigation and case lifecycle: BP-15/BP-16.

## 4. Ownership and system boundaries

| Concern | Authoritative owner | BP-33 contract |
|---|---|---|
| Person identity, living/deceased/entered/exited status, population cap | BP-03 | Reference canonical person IDs; no separate person registry |
| Employer, business, institution, worksite and premises identity | BP-04 | Reference organisation and property IDs |
| Police hierarchy, posts, rank, grade, authority and clearance | BP-05 | Administer employment transactions against authorised structures; never create posts or grant authority |
| Police personnel dossier and service identity | BP-06 | Send verified employment events and references; no duplicate police dossier |
| Police career and service rules | BP-07 | Supply HR transaction facts; no promotion/retirement rule ownership |
| Police duty assignment, roster and operational deployment | BP-08 | Own police leave/actual attendance administration; reconcile with planned roster without assigning officers |
| Police resources and readiness | BP-09 | Exchange workforce/resource constraints; no asset ownership |
| Police operational shift activity | BP-10/BP-11 | Supply employment availability/attendance facts; operational assignment remains elsewhere |
| Training and qualification records | BP-32 | Reference verified learning/credential evidence; no training or qualification award |
| Police governance and delegation | BP-30 | Apply authorised HR policies and delegated approval routes |
| Police complaints and professional standards | BP-31 | Refer employee-relations or conduct matters; no misconduct finding or sanction |
| Finance, payroll and accounting | BP-34 | Supply approved hours, contract terms and employment changes as payroll inputs; BP-34 calculates/posts |
| Simulation events and NPC work behaviour | BP-35 | Define employment facts and permitted transitions; engine executes causal behaviour |
| Relationships and household links | BP-36 | Reference household/relationship context; no competing relationship graph |
| Simulation clock and calendar | BP-37 | Read-only time authority |
| Records, persistence, backup and recovery | BP-38/BP-39 | Use canonical record/event contracts |
| Security and permissions | BP-42 | Enforce purpose-based access and confidentiality |
| Tests and quality evidence | BP-43 | Supply deterministic acceptance behaviour |
| Policy and schema change control | BP-44 | Version HR policy and emit controlled changes |

### 4.1 Police boundary

BP-33 is the administrative HR owner for police leave applications, leave decisions where delegated, actual attendance and absence records, general employee-relations administration, and approved employment transactions. BP-06 remains the authoritative police personnel dossier and service-history owner. BP-07 determines police career consequences. BP-08 owns duty assignments and the planned operational roster. BP-10 owns operational patrol activity.

For example, BP-33 may record that an officer has approved leave from a specified simulation time interval and notify BP-08; BP-08 determines the resulting roster/deployment changes. BP-33 may record actual attendance against a scheduled duty; it must not rewrite the planned roster or infer that the officer was operationally deployed.

### 4.2 Payroll boundary

BP-33 owns employment terms and approved time/attendance inputs. BP-34 owns pay calculations, deductions, taxation, benefits accounting, payroll runs, ledger posting, corrections and financial reconciliation. An approved timesheet is not a payroll payment; a contract salary is not a posted expense; an HR status change must not create a ledger entry outside BP-34.

## 5. Core invariants

1. Each employment relationship references one canonical BP-03 person and one BP-04 employer/organisation, except explicitly modelled self-employment or other configured relationship types.
2. Employment does not create a second person record or alter population count by itself.
3. One person may have multiple concurrent employment relationships, but each has its own employer, contract, job, schedule, status and history.
4. Concurrent work schedules and physical locations must be compatible, or a documented exception must explain remote work, overlapping paid availability, travel, on-call status or another valid arrangement.
5. Employment status, contract status, job assignment, shift plan, attendance, leave, payroll status, police service status, rank, appointment and deployment are distinct.
6. A job offer is not employment until accepted and the effective commencement conditions are met.
7. A signed/accepted contract does not itself prove the person commenced work or attended a shift.
8. A planned shift is not actual attendance. An attendance entry does not itself prove productive work or operational deployment.
9. Approved leave changes availability only for its defined scope and interval; it does not silently terminate a contract or change rank, career or unit membership.
10. Absence is not automatically misconduct. Any investigation or disciplinary outcome belongs to an authorised process and must be separately recorded.
11. Employment separation never deletes the person, employer, contract history, attendance, payroll references or historical decisions.
12. Corrections are append-preserving, attributable and linked to superseded records.
13. Employment policies and contracts are versioned and effective-dated; a later policy does not silently rewrite historical rights or decisions.
14. No employment deadline, shift, leave interval, probation interval or NPC work action progresses while simulation time is paused or the player is absent.
15. Work schedules and NPC work behaviour progress only through BP-35 using BP-37 canonical simulation time.
16. All living employees, applicants and employer representatives count once within the 10,000-person cap.
17. Workforce planning cannot silently generate people to fill vacancies or minimum staffing levels.
18. Business and employer records remain owned by BP-04 even when a business has no individually simulated workers.
19. HR records cannot infer qualifications, skills, clearances, police authority or professional competence from a job title.
20. No police employee is deployed to an incompatible duty merely because HR marks them available; BP-08 remains deployment authority.
21. No HR action can promote, demote, appoint, dismiss from police service, retire or alter career status unless the relevant owning system records the authorised decision.
22. No allegation, complaint, absence, performance concern or investigation is represented as a final finding without an authorised decision.
23. Access to sensitive employment, health, grievance, compensation and disciplinary-reference information is restricted by purpose and role.
24. The system must distinguish missing information from a negative finding. An absent record does not mean no employment, no leave, no qualification or no complaint.
25. The system must never invent salary, hours, attendance, leave entitlement, contract terms or a reason for separation to make records appear complete.
26. The same core rules apply to player and NPC employment records; player agency is preserved for the player's officer.
27. No external jurisdiction's employment statute, collective agreement, tax regime or certification rule is presumed. Fictional policy is configurable and versioned.

## 6. Domain model and principal records

| Entity | Essential attributes and relationships |
|---|---|
| HRPolicy | policy_id, version, owner, approval, effective interval, status, scope |
| EmployerReference | employer_id, BP-04 organisation reference, employer category, status |
| WorksiteReference | worksite_id, BP-04 premises/property reference, employer relationship, access/safety references |
| JobDefinition | job_id, employer_id, title, description, job family, grade/pay-band reference, skills/qualification references, status |
| Vacancy | vacancy_id, employer_id, job_id, worksite, headcount, approval, opening/closing simulation times, status |
| WorkforcePlan | plan_id, employer_id, period, planned posts, staffing target, assumptions, approval |
| RecruitmentRequisition | requisition_id, employer, job, reason, vacancy, budget approval reference, authorised requester, status |
| Application | application_id, vacancy_id, person_id, submission, eligibility evidence, status, restricted assessment references |
| SelectionDecision | decision_id, application_id, criteria version, panel/actor, evidence, rationale, outcome, review |
| Offer | offer_id, application_id, terms reference, issue/expiry simulation time, response, status |
| EmploymentRelationship | employment_id, person_id, employer_id, job_id, episode, status, start/end effective time, source |
| Contract | contract_id, employment_id, version, terms, hours, remuneration reference, duration, conditions, acceptance |
| ContractAmendment | amendment_id, contract_id, prior version, new version, reason, approval, effective interval |
| JobAssignment | assignment_id, employment_id, job/post reference, worksite, supervisor reference, effective interval |
| WorkPattern | pattern_id, employment_id, days/times, hours, recurrence, location mode, version |
| ShiftPlan | shift_id, employment_id, planned start/end, role/location, roster reference, source version |
| AttendanceRecord | attendance_id, employment_id, shift reference, actual start/end, status, source, correction history |
| Timesheet | timesheet_id, employment_id, period, attendance references, submitted/approved state, approver |
| LeavePolicy | leave_policy_id, version, leave categories, eligibility, accrual/limits, approval route |
| LeaveBalance | balance_id, employment_id, leave category, accrued/used/adjusted amounts, effective date, source |
| LeaveRequest | request_id, employment_id, category, interval, reason/access class, submission, state |
| LeaveDecision | decision_id, request_id, approver, authority, decision, rationale, conditions |
| AbsenceEvent | absence_id, employment_id, expected shift, observed interval, category, notification, status |
| ReturnToWorkRecord | return_id, absence_id, effective return, restrictions/reference, review |
| EmployeeRelationsMatter | matter_id, employment reference, concern category, parties, restricted access, routing, state |
| HRReview | review_id, matter/decision reference, reviewer, grounds, outcome, effective time |
| Separation | separation_id, employment_id, type, notice, decision/acceptance, effective date, handover |
| EmploymentEvent | event_id, type, subject references, actor, authority, simulation timestamp, source/policy version, provenance |
| WorkforceSnapshot | employer, period, unique people, employment episodes, vacancies, hours and derived metrics, source watermark |

### 6.1 Identity and uniqueness

- Person IDs resolve through BP-03. Police personnel IDs resolve through BP-06 and must map to the same canonical person.
- Employer and worksite references resolve through BP-04. BP-33 must not create a second business or premises record.
- An employment episode has a stable ID. Rehire after separation creates a new episode or an explicitly approved reactivation linked to prior history.
- A person can have several jobs with the same or different employers; each employment relationship is separately identified.
- A contract amendment creates a new version; it does not overwrite accepted historical terms.
- Attendance is uniquely keyed to an employment/shift occurrence, with corrections represented as linked events.
- A person employed by two organisations remains one population member.

### 6.2 Employment relationship model

Employment is represented as an episode with a lifecycle and effective dates. It may be permanent/ongoing, fixed-term, temporary, casual, part-time, full-time, apprenticeship, probationary, secondment, contractor or another configured relationship type. Labels do not determine legal rights unless a configured fictional policy defines them.

The system must support one employer with multiple job assignments and one person with multiple employers. It must also support unpaid/voluntary public service or self-employment as distinct relationship types where configured; they must not be misrepresented as payroll employment.

## 7. Employer and job architecture

Employers may be private businesses, public bodies, police institutions, non-profit organisations, sole traders or other BP-04 organisations. BP-04 owns their identity, legal form, business status, ownership and premises. BP-33 records the employment relationship to that employer.

Job definitions describe work performed, required skills, qualifications, working pattern, supervisor relationship, location, grade/pay-band references and approved headcount. They do not grant professional licences, police powers, security clearances or institutional appointments.

A vacancy must reference an approved job and employer. Vacancy count is not workforce headcount and does not create a person. A workforce plan is a planning record, not authority to hire or spend. Where budget approval is required, BP-34 supplies the authoritative financial decision.

The system supports employer closures, mergers, name changes, ownership changes and worksite changes through BP-04 references and effective-dated employment decisions. An employer's closure does not automatically decide each worker's separation terms; each affected relationship receives an explicit transition.

## 8. Recruitment and onboarding

Recruitment lifecycle: workforce need identified → requisition drafted → approved → vacancy published/open → applications received → eligibility review → selection → offer issued → accepted/declined/expired → pre-commencement conditions → employment commenced or cancelled.

Each stage records actor, authority, criteria version, simulation time, source evidence, decision and reason. The system supports internal and external applicants, multiple vacancies, repeat applications, candidate withdrawal, incomplete applications, conflicts, selection panels, reserve lists and appeals/reviews where configured.

Recruitment decisions must use recorded criteria. A candidate's existing employment, skills, qualifications and availability may be referenced but cannot be assumed. Sensitive personal information is collected only where necessary and permissioned. A selection decision is not a criminal finding or proof of suitability outside its stated scope.

An offer records the role, employer, proposed start, worksite, hours, remuneration reference, term, conditions, response deadline and approving authority. Acceptance does not commence employment before the effective start and any required conditions are satisfied.

Onboarding may create links to BP-06 for police personnel, BP-32 for training enrolment, BP-09 for issued assets, BP-42 for access permissions and BP-34 for payroll setup. Each owner performs its own transaction. HR does not silently create a completed training record, issued asset, access clearance or payroll payment.

Police recruitment is coordinated with BP-06/BP-07 and the police authority structure in BP-05. BP-33 may administer applications, offers and employment paperwork, but police service identity, entry eligibility, rank/appointment and career status are owned by the police-specific divisions.

## 9. Contracts and employment lifecycle

Employment relationship states include proposed, offer-pending, accepted-not-started, active, suspended, on-leave, notice-period, ended, deceased-linked, disputed and closed. A contract may be draft, issued, accepted, active, amended, expired, terminated or superseded. The relationship and contract states are related but not identical.

Contract terms may include job, hours, work location, remuneration reference, duration, probation conditions, notice, leave policy, benefits references, confidentiality and other fictional terms. Terms are stored as a versioned agreement and are effective-dated. The system must retain the version accepted by the parties.

Changes to hours, job, supervisor, worksite, remuneration reference or duration require an authorised amendment and effective date. Retroactive amendments require explicit authority, rationale and an audit trail. A disputed or unsigned amendment must not be treated as accepted.

Suspension of an employment relationship is distinct from leave, arrest, police suspension, access restriction, disciplinary finding or termination. The relevant owning process records its own authority and consequence. A police officer's service status is reflected in BP-06 and career implications in BP-07; BP-33 cannot create conflicting police status.

## 10. Working patterns, shifts and attendance

Work patterns define expected hours and availability. They may be fixed, rotating, irregular, seasonal, on-call, flexible, remote, hybrid or event-based. Every schedule is interpreted using BP-37 simulation time and effective-dated recurrence rules.

Planned shifts and actual attendance are distinct. A shift plan identifies expected start/end, job, worksite, role and source roster. Attendance records actual arrival/departure or other verified participation, source and exceptions. For police, BP-08 remains the owner of the duty assignment/roster; BP-33 records employment attendance and leave facts and sends reconciled events to BP-08.

Attendance categories may include present, late, early departure, absent, excused, approved remote work, on-call, called out, interrupted, unverified or corrected. A time record must identify whether it is self-reported, supervisor-confirmed, system-observed or otherwise sourced. Unverified data must not be treated as verified.

The system must detect incompatible simultaneous shifts, locations and travel times. Valid exceptions may include remote work, overlapping standby windows, flexible hours or a documented handover. A conflict is flagged for resolution rather than silently choosing one record.

Timesheets aggregate attendance/time records for a period. Submission, approval and correction are separate states. BP-33 supplies approved time inputs; BP-34 calculates payroll and posts financial results. A timesheet must not be equated with a pay run or ledger transaction.

## 11. Leave and absence administration

Leave categories are fictional configurable policy, potentially including annual, personal, family, parental, study, compassionate, unpaid, medical/sickness-related, public-service, special, training and other authorised leave. The system must not assume statutory entitlements, accrual rates, carry-over, evidence requirements or maximum duration.

Leave request states include drafted, submitted, pending, approved, partially-approved, declined, withdrawn, cancelled, deferred, in-progress, completed and disputed. Every decision records policy version, authority, reason, interval, conditions and effective time.

Leave balances are calculated from versioned policy and approved events. Manual adjustments require authority and provenance. The system must distinguish accrued, available, reserved, used, expired, carried forward and adjusted amounts. If a policy or balance is unresolved, the system flags it; it does not invent entitlement.

Absence records distinguish planned leave, notified absence, unnotified absence, lateness, early departure, sickness/health-related absence, workplace injury, emergency absence and unknown reason. An unknown reason remains unknown. An absence is not automatically misconduct or proof of dishonesty.

Return-to-work records may capture effective return, restrictions or adjustments by reference, follow-up and supervisor confirmation. Sensitive medical detail remains with its authoritative source; ordinary HR and line-management views receive only the minimum necessary operational information.

For police personnel, BP-33 communicates approved leave/absence to BP-08 so that duty coverage can be reconsidered. It does not itself select replacements, amend operational deployments or assume an officer attended a duty because the roster listed them.

## 12. Police staffing and roster interfaces

BP-33 supplies employment status, availability, leave, absence, actual attendance and workforce administration facts to BP-06/BP-08/BP-10/BP-11 as appropriate. BP-08 owns police duty assignment and planned roster; BP-09 owns resource readiness; BP-10 owns patrol deployment and field operations; BP-11 owns communications/dispatch.

Minimum staffing, specialist availability, patrol area coverage, command coverage, workload, geography, skills, fatigue and emergency demand are considered by the owning operational systems. BP-33 may report employment availability and approved leave but cannot determine operational sufficiency or allocate officers.

Roster changes and actual attendance must be recorded separately. A roster amendment must retain prior plan, actor, reason and effective time. Actual attendance may differ from planned assignment and must not overwrite it. A late, absent or diverted officer remains linked to the original planned shift and the actual event.

A police employee can be employed and active while unavailable for a particular duty. Conversely, a person can be scheduled but not actually attend. Employment availability is not operational readiness, legal authority or permission to perform a specialist function.

## 13. Employee relations, grievances and performance referrals

BP-33 supports intake, classification, routing and administrative tracking of workplace concerns, grievances, interpersonal disputes, performance support requests, accommodation requests and employment-policy disputes. Each matter has a defined scope, parties, confidentiality class, assigned handler, response steps, decision authority and review route.

A grievance or complaint is an allegation or request, not a finding. BP-33 must preserve the complainant's account, the response, supporting material references, uncertainty and any interim administrative steps. A manager's note is not automatically a verified fact.

Police conduct, integrity and misconduct matters are referred to BP-31. BP-31 owns the professional-standards process and findings. BP-33 may implement an authorised HR transaction after receiving a final decision, but cannot create a misconduct finding or disciplinary sanction.

Career performance and promotion decisions belong to BP-07. Training and qualification evidence belongs to BP-32. Operational supervision and duty decisions belong to BP-08/BP-10. BP-33 may store a reference to an authoritative outcome and perform a permitted administrative action, not duplicate the adjudication.

Conflict-of-interest, retaliation, confidentiality breach, protected disclosure and appeal routes must be configurable. A matter involving a supervisor or HR handler must be routed to an independent authorised person where policy requires.

## 14. Separation, exit and re-employment

Separation types may include resignation, end of fixed term, contract expiry, redundancy, employer closure, dismissal following an authorised process, retirement under the applicable career/HR owner, death, mutual agreement, transfer, abandonment after an authorised process or other configured reason.

Separation is a controlled process with proposal/request, notice, review, decision/acceptance, effective date, handover, access/asset notifications and closure. The system must distinguish notice served, resignation accepted, termination decided, effective last day and final administrative closure.

For police, BP-06 owns the authoritative service record and BP-07 owns career/separation rules, including police-specific retirement. BP-33 records the HR transaction and references the authorised decision. It must not apply a general retirement age or override the user's police service-retirement rules.

Separation does not delete a person, employment episode, contract, attendance, approved leave, payroll references, workplace grievance or historical role. BP-09 handles asset return; BP-42 handles access changes; BP-34 handles final payroll/financial reconciliation; BP-06/BP-07 handle police personnel/career consequences.

Re-employment creates a new employment episode or approved reactivation with explicit links to prior service. Prior performance, discipline, skills and qualifications are not automatically treated as current; validity and permitted use are checked with the relevant owner.

## 15. Workforce planning and reporting

Workforce plans may record approved staffing targets, job families, skills demand, vacancies, budget assumptions, workload and expected schedule coverage. They are planning instruments, not proof of funded posts, hires or available workers.

Reports may include headcount, unique persons employed, employment episodes, vacancies, contract types, hours, leave, absence, attendance, turnover, recruitment pipeline, job movement and workforce capacity. Reports must state their time period, employer scope, policy version and source watermark.

A single person with two jobs counts as one unique person and two employment relationships. A police employee who also holds another permitted role remains one person. Vacancy counts, applications, shifts and contracts must never be added to the living population.

Aggregates must distinguish planned from actual staffing, active from suspended employment, approved leave from absence, and reported from verified attendance. Missing records must be shown as unknown/not supplied, not silently treated as zero.

## 16. Time, schedules and NPC employment behaviour

BP-37 is the sole simulation clock. Employment start/end, shift recurrence, leave, absence, contract expiry, recruitment deadlines and HR review dates use canonical simulation time and effective-dated rules.

BP-35 controls NPC decisions and work/home movement. An NPC may travel to work, perform a job, be absent, request leave, change jobs or separate only through a causal event and known information. A schedule is not proof that an NPC completed the activity.

When the player exits or pauses, all employment time-dependent activity freezes. No shift starts or ends, salary period elapses, leave accrues, deadline expires, attendance changes, NPC changes employer or HR case advances. On resume, no wall-clock catch-up is applied.

Schedules must interface with BP-36 household relationships and BP-02/BP-04 locations without owning those records. Travel feasibility and incompatible location detection must be reproducible. Work movement may create relevant observed facts only when a simulated observer/system could legitimately observe them.

## 17. Information security, privacy and access

Access is role- and purpose-based. Employees may view their own permitted contracts, schedules, attendance, leave and decisions. Supervisors see only workers within their delegated scope. HR officers see assigned records. Employer representatives see their own organisation's permitted employment records. Auditors receive controlled read access.

Restricted categories may include health-related absence references, compensation, grievance, protected disclosure, performance, disciplinary references, identity verification, recruitment assessments and police-sensitive personnel information. Sensitive information is segregated and disclosed only to authorised roles for a defined purpose.

Police personnel records must not be exposed to ordinary business employers. A person's employment at a business must not expose police identity, service history, operational assignment or security-sensitive status unless an explicit authorised rule permits it.

All privileged access, bulk export, correction, override and disclosure actions are attributable and audited. Data minimisation applies to views and reports; it does not justify deleting required source facts or provenance.

## 18. Interfaces and event contracts

### 18.1 Inputs
- Canonical person IDs, life status and population admission from BP-03.
- Employer, organisation, business and premises references from BP-04.
- Police structure, authorised posts and authority from BP-05.
- Police personnel identity/service references from BP-06.
- Police career/retirement decisions from BP-07.
- Police duty roster and assignment from BP-08.
- Resource availability and asset issue/return from BP-09.
- Operational duty/dispatch context from BP-10/BP-11.
- Governance delegations from BP-30 and professional-standards outcomes/referrals from BP-31.
- Training/qualification evidence from BP-32.
- Financial approvals and payroll outputs from BP-34.
- NPC event execution from BP-35; household/work movement references from BP-36.
- Canonical time and pause state from BP-37.
- Record, persistence, permission and configuration contracts from BP-38/BP-39/BP-42/BP-44.

### 18.2 Outputs
- Recruitment, offer, contract, job assignment and employment lifecycle events.
- Effective-dated employment status, work pattern, shift plan and availability references.
- Approved leave, absence, attendance, return-to-work and timesheet input events.
- Police HR transaction and actual attendance references for BP-06/BP-08.
- Verified employment and work schedule references for BP-03/BP-04/BP-35/BP-36.
- Approved payroll input references for BP-34, never direct ledger postings.
- Training enrolment/availability referrals for BP-32.
- Asset/access onboarding and separation notifications for BP-09/BP-42.
- Workforce, vacancy, attendance, leave and employment reports for authorised users.

### 18.3 Event envelope

Every authoritative event includes event_id, event_type, person/employment/employer reference, actor or system identity, authority reference, simulation timestamp, policy/contract version, source record, correlation/idempotency key, prior-state reference, resulting-state reference and provenance. Repeated delivery must not create duplicate employment episodes, attendance entries, leave balances, payroll inputs or separation actions.

## 19. State transitions

| Record | Principal transitions |
|---|---|
| Requisition | draft → submitted → approved/declined → open → filled/cancelled/closed |
| Application | received → eligibility-review → shortlisted/rejected/withdrawn → selected/reserve/closed |
| Offer | drafted → approved → issued → accepted/declined/expired/withdrawn |
| Employment relationship | proposed → accepted-not-started → active → suspended/on-leave/notice → ended/closed |
| Contract | draft → issued → accepted → active → amended/expired/terminated/superseded |
| Job assignment | proposed → approved → active → changed/ended |
| Work pattern | draft → approved → active → amended/retired |
| Shift plan | planned → confirmed → amended/cancelled → elapsed (simulation only) |
| Attendance | unrecorded → reported → verified/disputed/corrected |
| Timesheet | draft → submitted → reviewed → approved/rejected/corrected |
| Leave request | draft → submitted → pending → approved/part-approved/declined/withdrawn/cancelled → completed |
| Absence | detected/notified → classified → reviewed → resolved/referred |
| Employee-relations matter | received → screened → assigned → response/review → resolved/referred/closed |
| Separation | proposed/requested → notice/review → authorised → effective → handover/closed |

A state transition must identify the actor, authority, policy version, simulation time and reason. Invalid transitions are rejected with a traceable error. A correction creates a linked event; it never erases the original.

## 20. Exceptions and edge cases

The system must handle:
- duplicate person or employer references and unresolved identity matching;
- multiple jobs, concurrent contracts and incompatible shifts;
- worksite closure, employer merger, employer insolvency or ownership change;
- vacancy withdrawal, failed recruitment, reserve candidate and offer expiry;
- incomplete application, disputed selection and recruitment appeal;
- unsigned, disputed, amended or retroactive contract terms;
- probation, fixed-term expiry, contract renewal and transfer;
- secondment, loan, temporary assignment and return to substantive employer;
- remote work, on-call, flexible hours, travel and overnight shifts;
- late arrival, early departure, partial shift, interrupted shift and disputed attendance;
- planned leave, emergency leave, overlapping requests and insufficient balance;
- unknown absence reason, sickness-related absence, workplace injury and return restrictions;
- leave during notice, suspension or another employment status;
- police leave affecting roster coverage and actual attendance differing from roster;
- police officer holding a second job where permitted, including conflict or schedule incompatibility;
- death, permanent departure or population status change during active employment;
- employee grievance involving supervisor/HR handler and protected disclosures;
- separation with outstanding assets, leave, payroll or access;
- rehire after separation, reinstatement and corrected historical records;
- policy changes during active contracts or leave periods;
- simulation pause/resume and backup restoration;
- duplicate event delivery, concurrent approvals and partial transaction failure;
- access denial, inappropriate disclosure and unauthorised bulk export;
- population-cap pressure when recruitment would add a new living person.

For every exception, preserve the original state, record the issue, identify the decision owner and block only the affected transaction where possible. Never invent a replacement person, employment fact, entitlement, payment or decision.

## 21. Storage, performance and audit

Store employer, job, policy and contract definitions once and reference their immutable versions from employment episodes. Reuse canonical person, business, premises and police personnel IDs. Store attendance and leave as compact events with references to source evidence; do not duplicate static employer or person data into every shift.

Preserve meaningful narrative, disputed accounts, corrections, decision rationale and provenance losslessly. Derived workforce snapshots must carry source watermarks and be reproducible. Compaction may reduce representation size but must not remove meaning, uncertainty, history or auditability.

High-volume queries must support person history, employer workforce, contract status, shift/attendance, leave intervals, police attendance and historical as-of dates. Indexing, retention and physical schema are owned by BP-38/BP-39. Database baseline, projected incremental bytes and actual growth must be measured before/after any future Neon write, with explicit user approval required before the write.

Audit covers recruitment criteria and decisions, contract acceptance/amendment, schedule changes, attendance, leave balance/decision, absence classification, employee-relations access, separation, payroll input release, bulk exports and privileged overrides.

## 22. Dependencies and ordering

BP-33 depends on BP-01 for canon and player agency; BP-03 for identity/population; BP-04 for employers and premises; BP-05/BP-06/BP-07/BP-08 for police structures/personnel/career/deployment boundaries; BP-09 for resources; BP-30/BP-31 for governance and standards interfaces; BP-32 for training; BP-34 for finance/payroll; BP-35/BP-36/BP-37 for causal, social and time behaviour; BP-38/BP-39 for records and persistence; BP-42 for security; BP-43 for tests; BP-44 for change control.

A missing upstream reference blocks only the dependent transaction. BP-33 must not create a shadow person, employer, post, police career, roster, qualification, payroll ledger or clock to make the transaction succeed.

## 23. Open fictional configuration decisions

The following remain open and must not be guessed:
1. Employer/job taxonomy and standard job catalogue.
2. Employment relationship and contract categories available in Saltwater.
3. Recruitment stages, eligibility criteria, panel rules and appeal routes.
4. Contract terms, probation, notice, renewal and termination policy.
5. Working hours, shift-pattern library, overtime and on-call rules.
6. Leave categories, accrual, balance, carry-over, approval authority and evidence rules.
7. Absence categories, notification standards and return-to-work process.
8. Attendance verification sources and timesheet approval matrix.
9. General employer grievance and employee-relations procedure.
10. Police HR transaction delegation and exact BP-06/BP-07/BP-08 hand-off rules.
11. Secondment, multiple employment and conflict-of-interest policy.
12. Sensitive record categories, access matrix and retention periods.
13. Workforce planning and minimum staffing/reporting standards.
14. Payroll input frequency, cut-off and BP-34 reconciliation interface.
15. Fictional employment dispute review and external referral model.
16. NPC employment schedule generation, work/home movement and job-change parameters.
17. Business-level workforce detail thresholds and when employees are promoted to full simulation.
18. Exact text commands and interface navigation for HR workflows.

These are configuration decisions, not reasons to invent real-world law. They may be resolved during later design review without changing the fixed 44-division structure.

## 24. Acceptance tests

These are required acceptance tests, not evidence that implementation or execution has occurred.

1. **HR-AT-001** — Every employment relationship references one canonical BP-03 person.
2. **HR-AT-002** — An employment relationship references an authoritative BP-04 employer.
3. **HR-AT-003** — A person with multiple jobs is counted once in population.
4. **HR-AT-004** — Employment creation cannot bypass the 10,000-person admission cap.
5. **HR-AT-005** — A vacancy does not create a person or employment relationship.
6. **HR-AT-006** — A business with no individually simulated employees remains a valid BP-04 employer.
7. **HR-AT-007** — A job definition has a stable ID and versioned terms.
8. **HR-AT-008** — A vacancy references an approved job and employer.
9. **HR-AT-009** — Workforce planning is not treated as hiring authority.
10. **HR-AT-010** — A recruitment requisition records requester and approval authority.
11. **HR-AT-011** — An application references a person and vacancy without duplicating identity.
12. **HR-AT-012** — An incomplete application remains incomplete rather than being silently accepted.
13. **HR-AT-013** — Selection uses a recorded criteria version.
14. **HR-AT-014** — A selection decision records panel/actor, evidence and rationale.
15. **HR-AT-015** — A conflict of interest triggers the configured recusal/control.
16. **HR-AT-016** — A reserve-list candidate is not represented as hired.
17. **HR-AT-017** — An offer records terms, response and effective start conditions.
18. **HR-AT-018** — Offer acceptance does not commence employment before its effective start.
19. **HR-AT-019** — An expired or declined offer cannot create an active employment episode.
20. **HR-AT-020** — Onboarding sends separate transactions to personnel, training, resources and access owners.
21. **HR-AT-021** — A police recruitment transaction creates no duplicate police/person identity.
22. **HR-AT-022** — BP-33 cannot grant police rank, post, authority, power or clearance.
23. **HR-AT-023** — An employment episode has a stable unique identifier.
24. **HR-AT-024** — Rehire creates a linked new episode or approved reactivation.
25. **HR-AT-025** — A contract preserves the exact accepted version.
26. **HR-AT-026** — A contract amendment creates a new version and retains the old terms.
27. **HR-AT-027** — A disputed amendment is not treated as accepted.
28. **HR-AT-028** — Employment status and contract status are separately represented.
29. **HR-AT-029** — A contract does not prove commencement or attendance.
30. **HR-AT-030** — A job change records effective time, approval and prior assignment.
31. **HR-AT-031** — A worksite change references BP-04 premises.
32. **HR-AT-032** — Employer closure does not silently terminate every employment relationship.
33. **HR-AT-033** — A person can hold two concurrent employment relationships without duplicate identity.
34. **HR-AT-034** — Incompatible concurrent shifts are detected.
35. **HR-AT-035** — A valid remote/flexible-work exception records its basis.
36. **HR-AT-036** — Work patterns use BP-37 canonical simulation time.
37. **HR-AT-037** — A planned shift is distinguishable from actual attendance.
38. **HR-AT-038** — A shift plan does not prove that work occurred.
39. **HR-AT-039** — Attendance records identify their source and verification status.
40. **HR-AT-040** — An unverified attendance claim is not reported as verified.
41. **HR-AT-041** — Late arrival and early departure preserve actual times.
42. **HR-AT-042** — Partial attendance is not rounded into a full shift without a rule.
43. **HR-AT-043** — An attendance correction retains the original assertion.
44. **HR-AT-044** — A timesheet aggregates source attendance records without replacing them.
45. **HR-AT-045** — Timesheet approval is separate from payroll calculation.
46. **HR-AT-046** — BP-33 does not post a payroll ledger transaction.
47. **HR-AT-047** — A leave request references an employment relationship and policy version.
48. **HR-AT-048** — Leave approval records actor, authority, reason and interval.
49. **HR-AT-049** — Overlapping leave requests are detected.
50. **HR-AT-050** — A leave balance is derived from approved policy/events and is auditable.
51. **HR-AT-051** — An unresolved leave entitlement is flagged rather than invented.
52. **HR-AT-052** — A declined leave request does not reduce an approved balance.
53. **HR-AT-053** — Leave cancellation preserves the original decision and cancellation reason.
54. **HR-AT-054** — Approved leave affects availability only within its effective interval.
55. **HR-AT-055** — Leave does not itself terminate or suspend a contract.
56. **HR-AT-056** — Absence with unknown reason remains unknown.
57. **HR-AT-057** — Absence is not automatically recorded as misconduct.
58. **HR-AT-058** — A return-to-work record references the originating absence.
59. **HR-AT-059** — Sensitive medical detail is not copied into ordinary supervisor views.
60. **HR-AT-060** — An HR policy amendment does not silently rewrite historic leave decisions.
61. **HR-AT-061** — Police leave is communicated to BP-08 without BP-33 assigning a replacement.
62. **HR-AT-062** — BP-33 actual police attendance does not overwrite the BP-08 planned roster.
63. **HR-AT-063** — A police officer can be employed but unavailable for a particular duty.
64. **HR-AT-064** — An officer listed on a roster but absent is represented by separate planned and actual records.
65. **HR-AT-065** — BP-33 does not determine patrol coverage or operational minimum staffing.
66. **HR-AT-066** — BP-33 does not grant specialist readiness from a job title.
67. **HR-AT-067** — Police service status is reconciled with BP-06.
68. **HR-AT-068** — Police career consequences are decided by BP-07, not inferred by BP-33.
69. **HR-AT-069** — A police duty assignment remains owned by BP-08.
70. **HR-AT-070** — A grievance is stored as a concern/allegation, not a finding.
71. **HR-AT-071** — A grievance involving its handler is routed under conflict rules.
72. **HR-AT-072** — A police misconduct referral links to BP-31 without duplicating its investigation.
73. **HR-AT-073** — BP-33 cannot create a professional-standards finding.
74. **HR-AT-074** — A final BP-31 outcome is referenced with its source and authority.
75. **HR-AT-075** — Performance-management notes are not automatically treated as verified misconduct.
76. **HR-AT-076** — A training qualification reference resolves to BP-32.
77. **HR-AT-077** — An HR job record cannot create a qualification or competence claim.
78. **HR-AT-078** — Separation records preserve employment history.
79. **HR-AT-079** — Notice served is distinct from separation effective date.
80. **HR-AT-080** — Resignation request and resignation acceptance are distinct.
81. **HR-AT-081** — Termination requires an authorised decision reference.
82. **HR-AT-082** — Police retirement follows BP-07 rules and cannot be replaced by a general HR age rule.
83. **HR-AT-083** — Death changes employment status without deleting the person or employment history.
84. **HR-AT-084** — Separation notifies resource, access and finance owners through separate events.
85. **HR-AT-085** — Re-employment links to prior episodes without silently reviving old contract terms.
86. **HR-AT-086** — Outstanding assets are referred to BP-09 rather than marked returned by HR.
87. **HR-AT-087** — Access removal is referred to BP-42 and remains auditable.
88. **HR-AT-088** — Final payroll reconciliation remains owned by BP-34.
89. **HR-AT-089** — Workforce reports distinguish unique persons from employment episodes.
90. **HR-AT-090** — Workforce reports distinguish vacancies from filled jobs.
91. **HR-AT-091** — Reports distinguish planned staffing from actual attendance.
92. **HR-AT-092** — Reports distinguish approved leave from absence.
93. **HR-AT-093** — Reports identify source watermark and reporting period.
94. **HR-AT-094** — Derived workforce reports cannot overwrite source employment events.
95. **HR-AT-095** — A person with several employers remains one population member.
96. **HR-AT-096** — A worker's household link resolves through BP-36, not a duplicate HR relationship graph.
97. **HR-AT-097** — Worksite and home locations resolve through canonical spatial/property references.
98. **HR-AT-098** — NPC job changes require a causal BP-35 event.
99. **HR-AT-099** — An NPC does not attend work solely because a schedule exists.
100. **HR-AT-100** — Work/home movement follows canonical simulation time and spatial constraints.
101. **HR-AT-101** — Pausing the game freezes shifts, attendance and leave progression.
102. **HR-AT-102** — Absence and employment deadlines do not advance on wall-clock time.
103. **HR-AT-103** — NPC employment changes do not progress while the player is absent.
104. **HR-AT-104** — Resume does not apply wall-clock catch-up to employment events.
105. **HR-AT-105** — All living employees and applicants count once within the 10,000-person cap.
106. **HR-AT-106** — Workforce growth cannot silently generate people to fill vacancies.
107. **HR-AT-107** — A person materially relevant to police activity is permanently promoted under BP-03 rules.
108. **HR-AT-108** — A person is not downgraded or erased after employment ends.
109. **HR-AT-109** — Employment records do not disclose hidden offender truth.
110. **HR-AT-110** — No HR report, notification or narrative bypasses the exact `bingo` reveal gate.
111. **HR-AT-111** — Employment records expose only information observed, received or authorised for the viewer.
112. **HR-AT-112** — A business employer cannot view a person's police service or operational assignment without authority.
113. **HR-AT-113** — A worker can view their own permitted employment records.
114. **HR-AT-114** — Supervisors cannot view records outside their delegated workforce scope.
115. **HR-AT-115** — Privileged access, correction and export actions are attributable.
116. **HR-AT-116** — A restricted grievance or health reference is not exposed in a general workforce report.
117. **HR-AT-117** — A missing attendance record is reported as unknown, not as absence or presence.
118. **HR-AT-118** — A missing qualification record is not treated as proof of unqualified status without an explicit completeness rule.
119. **HR-AT-119** — A missing contract field is flagged rather than supplied from a guess.
120. **HR-AT-120** — Concurrent approvals cannot create duplicate employment episodes.
121. **HR-AT-121** — Duplicate event delivery does not duplicate attendance, leave or separation records.
122. **HR-AT-122** — A failed transaction cannot leave a partially active employment relationship.
123. **HR-AT-123** — A policy change during an active contract follows a stated transition rule.
124. **HR-AT-124** — A retroactive contract amendment records authority and rationale.
125. **HR-AT-125** — A separation correction preserves the original decision and effective date.
126. **HR-AT-126** — A restored event history does not duplicate employment or attendance events.
127. **HR-AT-127** — Storage compaction preserves contract meaning, disputes and provenance.
128. **HR-AT-128** — HR retention and archival follow versioned policy without erasing required history.
129. **HR-AT-129** — No HR action changes public finance balances outside BP-34.
130. **HR-AT-130** — Public-sector employment references the approved employer and governance authority.
131. **HR-AT-131** — A public employment transaction does not invent a budget or appropriation.
132. **HR-AT-132** — A workforce report reconciles headcount, employment episodes and payroll-input populations without double-counting.
133. **HR-AT-133** — Simultaneous shifts at incompatible locations are blocked or explicitly explained.
134. **HR-AT-134** — A person with multiple job titles retains distinct job assignments and one identity.
135. **HR-AT-135** — An employee transfer between employers closes or amends the correct relationship and preserves both histories.
136. **HR-AT-136** — A business name change does not create a new employer identity unless BP-04 authorises a new entity.
137. **HR-AT-137** — An employer merger preserves employment references and requires explicit transition decisions.
138. **HR-AT-138** — A person permanently exiting Saltwater cannot remain in an active work schedule without a valid status correction.
139. **HR-AT-139** — A police employee's civilian second job is checked against configured conflict and schedule rules.
140. **HR-AT-140** — A training absence and an operational duty absence remain distinct, linked records.
141. **HR-AT-141** — All employment and attendance intervals are effective-dated and historically queryable.
142. **HR-AT-142** — Financial, population and staffing changes reconcile atomically across their owning systems.
143. **HR-AT-143** — Every material HR decision records actor, authority, policy version, simulation time and evidence references.
144. **HR-AT-144** — No real-world employment law or jurisdiction is silently imported.
145. **HR-AT-145** — The fixed 44-division structure is unchanged by BP-33.
146. **HR-AT-146** — Test status is not marked passed without reproducible execution evidence.
147. **HR-AT-147** — No Neon write is made by specification or test preparation without explicit user approval.
148. **HR-AT-148** — A source correction updates derived views without deleting the original HR event.
149. **HR-AT-149** — A worker's actual work location cannot conflict with the person's recorded location without a valid movement or remote-work explanation.
150. **HR-AT-150** — The text-first interface supports essential recruitment, contract, attendance, leave and separation workflows.

## 25. Source traceability

The original 52-division JSON remains the source of truth for original requirement wording. The crosswalk assigns requirements and tests to BP-33 as follows; all mapped meaning is retained in this specification. IDs below are included only where the authoritative crosswalk maps them to BP-33.

| Source ID | Original requirement/test | BP-33 incorporation |
|---|---|---|
| S03.R05 | Prevent double-counting police or people with multiple roles | Sections 2, 5–6, 15, 24; HR-AT-003–004, 095, 105 |
| S04.R01 | Stable identity, attributes, history, needs, schedule, skills, employment, finances, relationships and relevant records | Sections 5–6, 10, 15–18; HR-AT-001–004, 033–036, 095–100 |
| S08.R01 | Track jobs, employers, contracts, shifts, attendance, payroll, leave, skills, qualifications, discipline and separation | Sections 6–15, 18–21; HR-AT-007–094 |
| S08.R02 | Generate plausible work schedules and movement between work and home | Sections 10, 16, 18, 24; HR-AT-034–044, 098–104, 133, 149 |
| S08.R03 | Link employment to businesses, public institutions and police staffing | Sections 4, 7, 8, 12, 18; HR-AT-002, 020–022, 061–069, 130–132 |
| S08.T01 | Simultaneous shifts and locations do not conflict without recorded explanation | Sections 5, 10, 16, 20; HR-AT-034–036, 097–100, 133, 149 |
| S10.R01 | Define currency, public revenue, taxation, fees, expenditure, budgets, debt, grants and financial periods | Sections 4.2, 7, 8, 10, 15, 18; finance/payroll ownership boundary and HR-AT-045–046, 129–132 |
| S23.R01 | Police mandate/structure/rank/position/authority/powers/clearance/divisions/units/reporting | Sections 4, 8, 12, 18; HR administration respects BP-05 structure and authority and BP-06/BP-08 interfaces |
| S23.R03 | Appointment, promotion, transfer, acting roles, succession, discipline, grievance, standards and retirement | Sections 4, 8, 13–14, 18; HR transaction interfaces to BP-06/BP-07/BP-30/BP-31 |
| S24.R01 | Officer identity/history/recruitment/vetting/training/qualifications/skills/performance/welfare/leave/shifts/pay/discipline/career | Sections 4, 6, 8, 11–15, 18; police HR administration and owner boundaries |
| S24.R02 | Recruit entry and career progression through vacancies, standards and required training | Sections 8–9, 12–14, 18; police recruitment administration with BP-06/BP-07/BP-32 |
| S25.R01 | Generate and maintain shifts, duty rosters, leave, absences, minimum staffing, specialist availability, patrol areas and command coverage | Sections 10–12, 18; BP-08/BP-09 operational ownership and HR-AT-061–069 |
| S25.R03 | Record roster changes and actual attendance separately | Sections 10, 12, 18–19; HR-AT-037–045, 061–064 |

Crosswalk-wide rules also apply:
- **X03:** All time-dependent facts are effective-dated and historically queryable; HR uses BP-37 and never wall-clock progression.
- **X04:** Financial, population, inventory, staffing, resource and capacity changes reconcile atomically across owning systems.
- **A02:** Person life records and property/tenancy links preserve BP-03/BP-04/BP-33/BP-34 ownership.
- **A04:** Police structure/career interfaces preserve BP-05/BP-06/BP-07/BP-31/BP-32/BP-33 boundaries.
- **A05:** Roster staffing uses BP-08 for assignments, BP-09 for resource readiness and BP-33 for attendance.

## 26. Design completion checklist

- [x] Purpose, scope and exclusions defined.
- [x] Saltwater canon and population constraints preserved.
- [x] Employment, employer and police HR ownership boundaries defined.
- [x] Recruitment, contracts, work patterns and employment lifecycle defined.
- [x] Attendance, leave, absence and separation processes defined.
- [x] Police roster and career interfaces defined without ownership overlap.
- [x] Payroll/finance boundary defined.
- [x] NPC behaviour, time freeze and player agency preserved.
- [x] Permissions, provenance, retention and storage constraints defined.
- [x] Acceptance tests drafted with unique sequential identifiers.
- [x] Source requirement/test traceability included.
- [ ] User review and approval.
- [ ] Implementation.
- [ ] Acceptance test execution and evidence.
- [ ] Cross-system verification.

## 27. Status and next work

**Specification:** DESIGNED_DRAFT  
**User approval:** PENDING  
**Implementation:** NOT_STARTED  
**Test execution:** NOT_STARTED  
**Verification:** NOT_STARTED

Next division: **BP-34 — Finance and Procurement**, preserving the fixed BP-01–BP-44 structure and the same full specification and traceability contract.

No Neon writes have been made or authorised by this specification.
