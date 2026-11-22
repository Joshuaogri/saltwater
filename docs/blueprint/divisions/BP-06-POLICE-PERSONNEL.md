# BP-06 — Police Personnel

**Project:** Saltwater  
**Blueprint:** Fixed BP-01–BP-44  
**Version:** 0.1  
**Status:** `DESIGNED_DRAFT` — user review/approval pending  
**Date:** 2026-11-22  
**Owner:** BP-06  
**Dependencies:** BP-01, BP-03, BP-05, BP-07–BP-09, BP-30–BP-33, BP-37–BP-39, BP-42–BP-44  
**Authority:** Canonical design for the identity and complete personnel record of every serving, former, prospective and otherwise formally associated Saltwater Police Department person. BP-06 owns the authoritative police-personnel dossier and employment/service history, not organisational structure, career rules, duty allocation, training delivery or general HR transactions.

---

## 1. Purpose

BP-06 defines the people who constitute the Saltwater Police Department as an individually simulated workforce. Every officer and employee must be a persistent person with a stable identity, a coherent service history, attributable qualifications and appointments, relationships to the institution, and a record that can be reconstructed at any relevant historical point.

The department must not be represented by anonymous headcount rows. A person may occupy a post, hold a rank, perform a duty, possess a qualification, be attached to a unit, supervise others, be absent, be suspended, leave service and later return; these are distinct facts with their own effective dates and provenance. A personnel record must not collapse them into a single mutable status or assume that rank, job title, position, grade, authority, clearance, qualification and assignment are interchangeable.

BP-06 supplies the personnel substrate required for a breathing department: colleagues, supervisors, specialists, recruits, civilian staff, managers, former employees and other authorised workforce participants must exist as identifiable people. Their actions and records must be attributable, while their simulation depth is governed by BP-03 and the rules for relevant-person promotion.

## 2. Scope and ownership boundaries

### 2.1 BP-06 owns

1. Police-personnel identity linkage and the personnel master record.
2. Employment/service relationship records with the department.
3. Personnel category and service classification.
4. Appointment, commencement, confirmation, probation, leave, suspension, separation and return-to-service history as personnel facts.
5. Service identifiers, employment particulars and historical identity corrections.
6. Personnel-file sections, record provenance, effective dates and amendment history.
7. Personnel-related relationships: supervisor links, mentor links, reporting relationships as recorded personnel facts, and declared conflicts or relevant associations.
8. Personnel record completeness, status reconciliation and authoritative personnel views.
9. The personnel-facing interface contract for other divisions.

### 2.2 BP-06 does not own

- Departmental hierarchy, establishment, rank architecture, command authority or unit definitions (BP-05).
- Career progression rules, promotion eligibility, rank progression, service-length retirement calculations or career pathways (BP-07).
- Rosters, shift assignment, post allocation, deployment, operational availability or unit attachment decisions (BP-08).
- Equipment, issued assets and resource custody (BP-09).
- Qualification standards, course design, training delivery, assessment and certification rules (BP-32); BP-06 stores verified qualification references and personnel outcomes.
- General HR policy, recruitment campaign administration, payroll, benefits, procurement or workforce-wide transactions (BP-33/BP-34); BP-06 stores the resulting personnel facts and links.
- Discipline investigations, complaint adjudication or professional standards outcomes (BP-31); BP-06 stores authorised final personnel outcomes and access-controlled references, not the investigative working file.
- Permission evaluation and enforcement (BP-42).
- Global person identity and the complete life record for all residents (BP-03). A police personnel record must link to, not duplicate, the canonical person.
- Database schema implementation, persistence mechanics, backup and recovery (BP-38/BP-39).

If an ownership conflict occurs, the originating domain owns the decision and transaction; BP-06 owns the personnel projection and historical personnel fact only where the event changes or evidences the person's service relationship.

## 3. Personnel population and categories

### 3.1 Countability

All police personnel are part of the single 10,000-person living-population ceiling. A serving officer is not an additional population unit on top of their resident/person record. Personnel records reference one canonical BP-03 person ID. The personnel headcount is a view over eligible service relationships, never an independent population.

The planning baseline remains approximately 500 police personnel within the initial 9,500-person total (9,000 other residents plus 500 police), leaving 500 total-population capacity. This is a planning assumption, not a permanent quota, minimum staffing level or permission to exceed the 10,000 living-person ceiling. Any revised allocation must reconcile against BP-03 before it is adopted.

### 3.2 Personnel categories

The model must support, at minimum:

- sworn police officers;
- recruits and probationary officers;
- senior officers and supervisors;
- commissioned/command officers;
- specialist officers;
- police civilian employees and professional staff;
- administrative and records staff;
- technical, analytical and forensic employees where employed by the department;
- temporary, fixed-term, seconded or contract personnel where the canon permits;
- volunteers, auxiliary or reserve personnel only if separately authorised by the governing canon;
- former personnel, retirees, deceased personnel and persons whose appointment was rescinded;
- applicants and candidates who have not yet entered service.

Categories describe the service relationship, not a rank or authority. A civilian employee can hold a management position without being a sworn officer. A sworn officer can be assigned to a civilian-facing function without losing sworn status. No category automatically grants operational powers.

### 3.3 Category constraints

Each category must have explicit permitted appointment types, service states, authority implications and eligibility constraints. The system must not infer legal or operational powers from a category label alone. Unsupported category values must be rejected or held as an unresolved proposal, never silently normalised to sworn officer.

## 4. Canonical identity and identifiers

Each personnel file must reference exactly one canonical person record from BP-03. The link is mandatory before an individual becomes a serving employee. Applicants may have a provisional candidate record linked to a person record; duplicate person creation is prohibited merely because a person applies, changes name, transfers unit or receives a new service number.

Required identifiers:

| Identifier | Purpose | Rule |
|---|---|---|
| `person_id` | Canonical individual identity | Stable BP-03 identifier; never recycled |
| `personnel_id` | Department personnel dossier | Stable, unique, never recycled |
| `service_number` | Human-facing service identifier | Unique within department; historical values retained |
| `application_id` | Recruitment/candidacy linkage | BP-33-originated or recruitment workflow ID |
| `appointment_id` | One appointment or service engagement | Unique per appointment; repeat engagements remain distinct |
| `employment_event_id` | One personnel lifecycle event | Immutable event identity |
| `qualification_ref` | Qualification/certification reference | Owned by BP-32; verified snapshot/validity recorded |
| `position_id`, `rank_id`, `unit_id` | Organisational references | Owned by BP-05/BP-07/BP-08; no duplicate master definitions |

Identifiers must be opaque or otherwise non-semantic. Names, dates of birth, rank, unit, ethnicity, address or other changeable attributes must never be encoded as identity keys. A former service number remains reserved and must not be assigned to another person.

## 5. Personnel master record

The master record is a current-state projection assembled from authoritative events and domain references. It must include, where applicable:

### 5.1 Identity linkage
- personnel ID;
- canonical person ID;
- current and former service numbers;
- verified name reference and approved display name;
- identity-link status;
- identity discrepancy flag and resolution reference.

Names and biographical facts are sourced from BP-03. BP-06 may hold service-specific display preferences or historically used names where necessary for accurate records, but it must not create a competing civil identity.

### 5.2 Service particulars
- personnel category;
- sworn/civilian classification;
- appointment type;
- service start and end dates;
- current service state;
- probation status and dates, if applicable;
- employing department/entity;
- primary personnel contact channel reference;
- current organisational references as projections, not authoritative ownership;
- service location or station reference where relevant;
- employment status effective date;
- reason code and source event for current status.

### 5.3 Professional record references
- rank history reference (BP-07);
- post/position history reference (BP-05/BP-07);
- unit attachment history reference (BP-08);
- qualification and certification references (BP-32);
- training record references (BP-32);
- commendation and recognition references;
- authorised discipline outcome references (BP-31);
- absence/leave and availability references (BP-33/BP-37/BP-08);
- issued-asset references (BP-09);
- payroll/benefit references where applicable (BP-33/BP-34).

### 5.4 Record administration
- created timestamp and creating actor/system;
- source/provenance reference;
- last validated timestamp;
- record completeness state;
- restricted-record markers;
- correction and supersession links;
- audit history reference.

No sensitive field is included merely because it could be collected. Each field must have a defined purpose, authoritative owner, permitted readers, retention rule and lifecycle.

## 6. Service relationship and lifecycle

A person's relationship with the department is represented as one or more service engagements. Multiple engagements are allowed over a lifetime, but overlapping active engagements require explicit compatibility and cannot be created accidentally.

### 6.1 Applicant lifecycle

A candidate may progress through states such as:
`PROSPECT` → `APPLIED` → `UNDER_REVIEW` → `ASSESSMENT` → `OFFERED` → `ACCEPTED` → `APPOINTED`.

Alternative terminal or paused states include `WITHDRAWN`, `REJECTED`, `INELIGIBLE`, `OFFER_DECLINED`, `ON_HOLD` and `EXPIRED`.

These are workflow states, not employment states. An applicant does not count as serving police personnel merely by applying or receiving an offer. Recruitment workflow ownership resides with BP-33; BP-06 receives the accepted appointment facts and creates/activates the personnel service engagement.

### 6.2 Service lifecycle

An appointment may use the following state model, with only valid transitions permitted:

- `PENDING_START`: appointment agreed, service not yet commenced;
- `PROBATIONARY`: service commenced subject to probation where applicable;
- `ACTIVE`: confirmed or otherwise active service;
- `LEAVE`: employment continues while the person is on an authorised leave state;
- `SUSPENDED`: service relationship continues but defined duties/permissions may be restricted by authorised action;
- `SECONDMENT_OUT`: service relationship retained while temporarily serving elsewhere;
- `SECONDMENT_IN`: person serves with Saltwater SPD under a recorded secondment;
- `NOTICE`: separation is pending, but service continues until its effective date;
- `SEPARATED`: appointment ended;
- `RETIRED`: service ended by retirement;
- `DECEASED`: person deceased; service ends according to effective event and relevant rules;
- `RESCINDED`: appointment invalidated or rescinded with a recorded reason and authority.

The exact state vocabulary may be refined during implementation, but the distinctions above must remain. In particular, leave, suspension, secondment and notice are not equivalent to separation. A person can have more than one historical appointment; only one may be the primary active appointment unless an explicitly modelled arrangement permits otherwise.

### 6.3 Transition controls

Every transition records:
- prior state and new state;
- effective date/time and recorded date/time;
- authorised actor and authority reference;
- reason code and explanatory note;
- originating decision/workflow reference;
- impacted rank, position, unit, access, roster, resource, payroll and notification references;
- whether the event is prospective, immediate, backdated or corrective;
- audit and supersession links.

A transition must be atomic across dependent projections or leave a visible pending reconciliation state. No partial transition may silently present a person as both active and separated.

### 6.4 Backdated and corrected events

Backdating is permitted only as an explicit correction or authorised effective-date decision. The system preserves both the effective time and the time the record was entered. It must not rewrite history as if the correction had always been known. Downstream views must be recalculated or flagged for reconciliation, and prior snapshots remain reconstructable.

## 7. Employment events and immutable history

Personnel facts are event-based. Events include appointment, commencement, confirmation, probation extension, category change, service-number issue, name-display correction, promotion outcome reference, transfer, secondment, leave, suspension, reinstatement, notice, resignation, dismissal, retirement, death, rescission, rehire and record correction.

Each event must carry:
1. immutable event ID;
2. personnel and appointment IDs;
3. event type and schema version;
4. effective-from and, where relevant, effective-to;
5. recorded-at timestamp;
6. actor/system and authority;
7. source transaction/document reference;
8. structured reason code;
9. previous/new values or state references;
10. validation result;
11. audit/provenance chain;
12. supersession/correction reference where applicable.

Events are append-only in the logical model. A mistaken event is corrected by a compensating or superseding event; it is not silently deleted or overwritten. The current personnel profile is a projection, not the only retained truth.

## 8. Rank, position, grade, authority and assignment separation

BP-06 must preserve the distinctions established by BP-05 and BP-07:

- **Rank:** the person's recognised police rank at a point in time.
- **Position/post:** an authorised organisational job or establishment post.
- **Grade:** a pay or employment grading classification, if used.
- **Authority:** specific decision-making or operational authority granted by a defined source.
- **Clearance:** permission to access a class of protected information or facility, enforced by BP-42.
- **Qualification:** a verified competence or certification with scope, issuer, validity and status.
- **Assignment:** the person's current or historical allocation to a unit, team, duty or task, owned by BP-08.
- **Appointment:** the legal/organisational act establishing a service relationship or placing a person into a post, as applicable.

No one field implies another. A rank does not automatically prove current qualification, active duty, supervisory appointment, clearance or authority to perform a particular specialist task. A position title does not confer rank. A qualification does not itself confer permission. A unit attachment does not alter the underlying employment category.

BP-06 records the personnel-side references and effective periods. It must reject contradictory combinations where the owning division declares them invalid, while retaining historical combinations that were valid at the time.

## 9. Personnel relationships and supervision records

The dossier may reference:
- line manager and designated supervisor;
- subordinate/supervisee relationships;
- mentor and trainee;
- coach or assessor;
- professional reporting contact;
- emergency contact (restricted);
- declared personal/professional conflict or relevant association;
- former colleague or prior supervisory relationship.

Relationships must be typed, directional where appropriate, effective-dated and sourced. A reporting relationship is not automatically the same as operational command at an incident. Operational command is owned by BP-10/BP-12; organisational reporting structure is owned by BP-05; personnel history stores the relevant link and effective interval.

The system must allow a supervisor relationship to change without rewriting historical supervision. It must support temporary acting supervision and distinguish it from permanent appointment. Personal relationships must not be inferred from shared surnames, addresses, workplaces or social proximity.

## 10. Qualifications, training and professional capability references

BP-06 stores verified references to qualifications and training outcomes owned by BP-32. A reference must identify:
- qualification/certificate ID;
- issuing body;
- qualification name and version;
- scope and restrictions;
- issue date, expiry date or review date;
- verification state and verifier;
- suspension, revocation or supersession status;
- source evidence reference.

Capability is time-dependent. Expired, suspended, revoked, unverified or out-of-scope qualifications cannot be displayed as currently valid. Historical validity must remain queryable. A person may have a qualification record without being authorised or assigned to exercise it. BP-08 and BP-42 must consume the appropriate current capability and permission state rather than infer from a personnel summary.

## 11. Absence, availability and fitness-related record boundaries

BP-06 may display a minimal personnel status such as on leave, absent, suspended or unavailable where that status is necessary to understand service continuity. The authoritative scheduling and availability record belongs to BP-08/BP-33/BP-37 according to the event type.

Sensitive medical or fitness information is not a general personnel-profile field. Where the game requires a fitness-for-duty determination, BP-06 stores only the authorised outcome, scope, effective period, restrictions and reference to the restricted source record. It must not expose diagnoses or unnecessary intimate details to ordinary supervisors, colleagues or operational users. Fitness status does not automatically establish guilt, misconduct or permanent incapacity.

## 12. Commendations, conduct outcomes and restricted personnel material

Commendations, awards and formal recognition may be linked to a personnel record with issuer, date, reason, decision reference and status. Allegations, complaints and investigations remain in BP-31 and must not be presented as established findings. Only authorised final outcomes may be reflected in the ordinary personnel summary, with exact outcome classification and access restrictions.

A pending allegation must never be silently converted into a disciplinary finding. An overturned, expunged or corrected outcome must retain the historical audit trail while the current display follows the applicable authorised visibility rule. Personnel records must distinguish:
- allegation;
- investigation opened;
- interim measure;
- finding;
- sanction or management action;
- appeal;
- overturned or varied outcome;
- closed with no finding;
- withdrawn or unsubstantiated matter.

The detailed case file remains owned by BP-31. BP-06 receives a minimum necessary personnel outcome projection and reference.

## 13. Personnel file structure and documents

A personnel file is a logical collection of references, not an uncontrolled document dump. Sections may include:
- identity and appointment;
- service history;
- rank and position history;
- assignments and secondments;
- qualifications and training;
- commendations;
- authorised conduct outcomes;
- leave and availability summaries;
- issued property references;
- acknowledgements and signed personnel notices;
- separation and retirement records;
- restricted annexes.

Each document/reference must carry type, owner, source, creation date, effective date, status, version, access classification, retention rule, integrity metadata and relationship to the relevant event. The personnel file must not duplicate full evidence, medical files, investigation files, payroll ledgers or training course records when those are owned elsewhere.

Missing, disputed, illegible, unverified or superseded material must be explicitly labelled. A missing document is not proof that an event did not occur. A document's existence is not proof of its truth; provenance and verification status must be visible to authorised readers.

## 14. Personnel count and establishment reconciliation

BP-06 provides reliable personnel counts by service state, category, sworn/civilian status and effective date. It must distinguish:
- living people who are current employees;
- people on leave or suspended but still employed;
- seconded-in and seconded-out personnel;
- applicants and candidates;
- former employees;
- deceased former or serving personnel;
- vacant posts, which are not people.

Counts must be derived from person-linked appointments and effective-dated status. No vacancy, post, rank slot, roster slot or organisation record counts as a person. A seconded-out employee remains one living person in the total population and must not be counted twice. A seconded-in person must be reconciled with the canonical population and the one-city/one-jurisdiction rule; the system must not invent off-city living persons to fill staffing needs.

When headcount approaches the 10,000-person ceiling, BP-03 is authoritative for admission/exit accounting. BP-06 must not independently create or admit a person to bypass the cap. Workforce planning must operate within the shared population budget.

## 15. Separation, retirement, death and re-engagement

Separation events must include effective date, initiating party, reason classification, decision authority, notice/appeal references where relevant, final service state and downstream consequences. A resignation, dismissal, retirement, death, rescinded appointment and contract expiry are distinct event types.

Retirement eligibility and mandatory retirement calculations are owned by BP-07. BP-06 records the effective retirement decision and service end. The Saltwater career rule, where applicable, is service-based rather than age-based: mandatory retirement after 35 years of police service, with the specific Police Chief tenure exception defined by BP-07. BP-06 must not independently calculate or modify that rule.

Death is linked to the canonical BP-03 life event. The personnel record must close or transition the service relationship consistently without erasing service history. Re-engagement creates a new appointment or engagement linked to the same person and retained personnel dossier; it must not reset the person's identity, erase prior service or reuse identifiers.

## 16. Permissions and information boundaries

BP-06 defines record sensitivity labels and intended access classes; BP-42 enforces access. At minimum, distinguish:
- basic directory information;
- ordinary service particulars;
- supervisor/management-only information;
- restricted personnel material;
- highly restricted medical/fitness or protected personal information;
- audit and integrity records.

Access is purpose-limited and role/context dependent. A supervisor's legitimate access to availability does not grant access to a subordinate's full restricted file. A colleague's need to know a service number or current unit does not grant access to private contact details, medical information, complaint files or personal relationships.

Every read of restricted material, export, correction, disclosure or permission change must be auditable. Emergency access, if supported, must be explicit, justified, time-limited where possible and reviewed. Personnel must not be able to alter their own authoritative appointment, qualification, discipline or access records without independent authorised approval.

## 17. Interfaces and data contracts

| Consumer/producer | Contract |
|---|---|
| BP-03 Population | Canonical person identity, life status and population countability; BP-06 references person, never creates a duplicate |
| BP-05 Police Architecture | Rank/post/structure references and authorised organisational relationships |
| BP-07 Career | Career events and service history inputs; BP-07 owns progression and retirement rules |
| BP-08 Units and Deployment | Current personnel eligibility, service state, qualifications references and unit attachment projection |
| BP-09 Police Resources | Personnel-to-issued-asset custody links |
| BP-30 Department Governance | Approved establishment/appointment/management decisions |
| BP-31 Professional Standards | Authorised final personnel outcome references; no duplication of investigative file |
| BP-32 Training and Development | Verified qualification and training outcomes |
| BP-33 Human Resources | Recruitment, contracts, leave, payroll/benefits and general HR transaction events |
| BP-37 Time and Scheduling | Effective dates, service periods and schedule references |
| BP-38 Records and Databases | Logical records, identifiers, constraints and provenance contracts |
| BP-39 Persistence and Recovery | Durable event history, snapshots, reconciliation and recovery |
| BP-42 Security and Permissions | Classification, access purpose, audit requirements and sensitive-field boundaries |
| BP-43 Testing and Quality Assurance | Test fixtures, invariant checks, evidence and regression scenarios |
| BP-44 Configuration and Change Control | Versioned vocabularies, approved policy changes and migration compatibility |

### 17.1 Interface invariants

1. Every personnel dossier references one canonical person.
2. No person is counted twice because of multiple appointments or secondment.
3. A personnel record cannot override BP-03 life status.
4. BP-06 cannot invent rank, position, qualification, unit or clearance master data.
5. All state-changing inputs carry an originating authority and event reference.
6. Consumer projections must identify their source and effective timestamp.
7. Unavailable upstream data is shown as unknown/stale, not fabricated or silently treated as valid.
8. Cross-domain updates are idempotent by source event ID.
9. A failed downstream projection must be retryable without duplicate personnel events.
10. Historical views must reproduce the state as of a requested effective time.

## 18. Operational queries and commands

The text interface must support authorised queries, including:
- view a personnel directory with privacy-filtered fields;
- open a personnel dossier;
- retrieve service history as of a date;
- list active, probationary, suspended, on-leave, seconded or former personnel;
- search by personnel ID or service number;
- list vacancies only when joined to BP-05 establishment data (vacancies are not personnel);
- list expiring or invalid qualifications from BP-32 references;
- reconcile personnel count against population count;
- inspect authorised event history and correction chain;
- identify incomplete, disputed or stale personnel records;
- compare current and historical supervisory links.

Commands must not disclose restricted data merely because a user knows an ID. Search results must apply the same field-level and record-level permissions as dossier views. Bulk exports require explicit permission, purpose and audit.

## 19. Failure modes and edge cases

The design must handle, without silent corruption:

1. A recruit has a candidate record but no accepted appointment.
2. An appointment is accepted but the person has not commenced service.
3. Two records appear to represent the same person.
4. A person changes legal or preferred name.
5. A service number is mistyped, duplicated or replaced.
6. A person has multiple historical appointments.
7. Two appointments overlap unexpectedly.
8. A civilian employee is incorrectly assigned sworn powers.
9. A rank is current but the required qualification has expired.
10. A person is on leave while a roster still shows them assigned.
11. A suspended person remains on an active duty roster.
12. A person is seconded out but counted twice or removed from population.
13. A seconded-in person lacks a canonical person record.
14. A supervisor leaves but historical subordinate relationships are lost.
15. A temporary acting supervisor is mistaken for a permanent appointment.
16. A complaint is pending but displayed as a finding.
17. A disciplinary outcome is overturned but remains displayed as current.
18. A death event conflicts with an active service state.
19. A retirement event is entered before its approved effective date.
20. A backdated correction changes a historical roster or authority projection.
21. A source system sends the same event more than once.
22. An upstream system is unavailable or returns stale data.
23. A restricted file is requested by an unauthorised user.
24. A personnel record is exported without required redactions.
25. A person reaches the population ceiling during recruitment.
26. A vacancy is incorrectly counted as a person.
27. A former employee is rehired and a new identity is created.
28. An appointment is rescinded after downstream permissions were granted.
29. A qualification issuer revokes a certificate.
30. A record is incomplete, disputed, forged or has uncertain provenance.
31. The personnel system is restored from backup with downstream systems at different event positions.
32. A person is deceased while records remain necessary for historical investigations, court proceedings or audit.

For each case, preserve source facts, flag conflicts, prevent unsafe state transitions, and create a resolvable reconciliation task. Never resolve identity or status ambiguity by choosing the most convenient value.

## 20. Acceptance criteria and tests

The following tests are mandatory before BP-06 can be marked tested. Test execution and evidence are not implied by this specification.

| Test ID | Scenario | Expected result |
|---|---|---|
| PERS-001 | Create a serving officer dossier | One personnel ID links to exactly one BP-03 person |
| PERS-002 | Create applicant without appointment | Candidate exists; serving headcount unchanged |
| PERS-003 | Commence accepted appointment | Service state and effective date recorded once |
| PERS-004 | Duplicate source event replay | Idempotent; no duplicate appointment or event |
| PERS-005 | Change person's name | Same person/personnel identity; historical display retained where required |
| PERS-006 | Replace service number | Old number reserved; new number unique and audited |
| PERS-007 | Record rank and position separately | No automatic rank/position equivalence |
| PERS-008 | Expire specialist qualification | Capability view marks invalid; historical validity remains queryable |
| PERS-009 | Place employee on leave | Employment continues; availability projection changes |
| PERS-010 | Suspend officer | State and restrictions recorded; no automatic separation |
| PERS-011 | Record secondment out | One person counted once; service history retained |
| PERS-012 | Record secondment in | Existing canonical person required; no invented population record |
| PERS-013 | Change supervisor | New relationship effective-dated; prior relationship preserved |
| PERS-014 | Record temporary acting supervisor | Acting interval distinguished from permanent appointment |
| PERS-015 | Record pending complaint | No finding appears in ordinary personnel summary |
| PERS-016 | Record final authorised conduct outcome | Correct minimal outcome reference appears under access control |
| PERS-017 | Overturn prior conduct outcome | Current view corrected; full audit trail retained |
| PERS-018 | Record death | BP-03 life event and personnel service state reconcile |
| PERS-019 | Rehire former employee | Same person and dossier; distinct appointment history |
| PERS-020 | Backdate a correction | Effective and recorded times both retained; projections reconciled |
| PERS-021 | Count personnel | Count derives from person-linked service engagements, not posts or roster slots |
| PERS-022 | Reach 10,000 population ceiling | New admission blocked/held by BP-03; no cap bypass |
| PERS-023 | Request restricted personnel file | Access denied unless BP-42 authorises; attempt audited |
| PERS-024 | Export directory | Only permitted fields exported; purpose and actor logged |
| PERS-025 | Restore personnel history | Events and projections recover without duplicate or lost history |
| PERS-026 | Query historical service state | State is reproducible at requested effective timestamp |
| PERS-027 | Conflicting upstream status | Conflict surfaced; no silent overwrite |
| PERS-028 | Vacancy count | Vacancy is never counted as a living person |
| PERS-029 | Appointment rescinded | Downstream eligibility/access projections invalidated or reconciled |
| PERS-030 | Verify personnel completeness | Missing provenance, dates or required references are explicitly reported |

### 20.1 Evidence required

For every executed test, retain:
- test ID and version;
- fixture/person IDs (synthetic);
- preconditions and input events;
- expected and actual result;
- pass/fail and failure classification;
- relevant event/projection snapshots;
- audit/provenance evidence;
- test runner/version and execution timestamp;
- defect reference and retest result, if applicable.

No real personal data is required for tests; synthetic Saltwater people are sufficient.

## 21. Source traceability

BP-06 must preserve the full intent of the 52-division source blueprint, including personnel identity, service history, workforce classification, employment and professional-life references, police personnel, staffing/deployment interfaces, governance, training, complaints, time, population accounting, security and persistence.

Primary source areas:
- S04 — person identity and life records (identity remains BP-03-owned; BP-06 links it);
- S08 — employment, labour and professional life;
- S23 — police service governance and structure (BP-05 ownership; personnel interface);
- S24 — police personnel and career simulation;
- S25 — police duty rosters, staffing and deployment (BP-08 ownership; personnel interface);
- S26 — police command, policy and internal governance (BP-05/BP-30 ownership);
- S32 — victims, witnesses, suspects and persons of interest (person identity remains BP-03; case role is case-domain owned);
- S40 — complaints, oversight and public accountability (BP-31 ownership; authorised outcome interface);
- S41 — time, calendar, schedules and simulation clock (BP-37);
- S46 — database, schemas and persistence (BP-38/BP-39);
- S48 — security, permissions and information boundaries (BP-42);
- S49 — backups, recovery and data integrity (BP-39);
- S50 — testing, validation and simulation quality (BP-43);
- S52 — canon, versioning and change control (BP-44).

Cross-cutting requirements X01–X10 apply, particularly population cap, stable identity, no time advancement while absent, hidden information, provenance, player agency, efficient storage and no unapproved database writes. The 52→44 crosswalk remains the detailed source-to-target mapping authority; this specification does not replace or narrow it.

## 22. Open decisions retained for user authority

These are deliberately not guessed:
1. Exact sworn/civilian category taxonomy and whether auxiliary/reserve personnel exist.
2. Exact service-number format and whether visible numbering encodes any station or cohort (default design: non-semantic).
3. Whether applicant records are retained indefinitely or subject to a defined lifecycle/retention policy.
4. Exact probation rules by appointment category.
5. Which personnel documents and conduct outcomes are visible to which ranks/roles.
6. Exact emergency-access model for restricted personnel records.
7. Whether Saltwater has formal secondments, temporary contracts or volunteer personnel.
8. Exact field-level retention periods and archival treatment.
9. Which personnel profile fields appear in the default directory.
10. Final headcount allocation within the 10,000-person total; the 500 police figure remains a planning baseline, not a fixed quota.

These decisions do not prevent the core data model, identity linkage, lifecycle, provenance, separation of ownership and test design from being specified.

## 23. Design completion and status

- Specification: `DESIGNED_DRAFT`.
- User approval: pending.
- Implementation: `NOT_STARTED`.
- Tests: `NOT_STARTED`.
- Verification: `NOT_STARTED`.
- Neon schema, migration, seed or data write: none authorised or performed by this document.

BP-06 is not complete merely because this file exists. It becomes `DESIGNED` only after the user approves the specification and its open decisions are resolved or explicitly accepted as deferred. Implementation, testing and verification require separate artefacts and evidence.
