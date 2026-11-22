# BP-05 — Police Architecture

**Project:** Saltwater  
**Blueprint:** BP-01–BP-44  
**Version:** 0.1  
**Status:** `DESIGNED_DRAFT` — user review/approval pending  
**Date:** 2026-11-22  
**Owner:** BP-05  
**Dependencies:** BP-01–BP-04, BP-06–BP-12, BP-25–BP-27, BP-30–BP-33, BP-35, BP-37–BP-44  
**Authority:** Canonical design for the Saltwater Police Department as an institution: mandate, structure, command architecture, organisational hierarchy, rank/position/grade/authority/clearance distinctions, divisions, units, reporting lines, governance interfaces and institutional operating model.

---

## 1. Purpose

BP-05 defines the complete institutional architecture of the Saltwater Police Department (SPD). It establishes why the department exists, what it is responsible for, how it is organised, how authority flows, how command and supervision work, how its components relate, and how the institution remains coherent through routine operations, emergencies, vacancies, reorganisations and leadership changes.

The department is the primary deep-simulation institution in Saltwater. It must be an operationally functioning organisation, not merely a list of ranks and units. Its structure must support individual-officer gameplay while allowing the wider department to act credibly when the player is not directly involved. The player must be able to understand the organisation through persistent textual records and commands; no graphic interface is required for essential operation.

BP-05 owns the institutional structure and authority model. It does not own:
- individual officer identity, employment/personnel history or service record (BP-06);
- career progression, promotion eligibility and retirement calculations (BP-07);
- assignment, roster, unit deployment and duty allocation (BP-08);
- equipment/resource inventory and readiness (BP-09);
- patrol, dispatch, incident response and case operations (BP-10–BP-16);
- police policy/command decisions and institutional governance procedures (BP-30);
- discipline, complaints and professional standards casework (BP-31);
- training catalogues and qualification delivery (BP-32);
- general employment/HR transactions (BP-33);
- permissions enforcement (BP-42);
- schema and persistence implementation (BP-38/BP-39).

BP-05 defines the structural framework within which those divisions operate. It must not duplicate their authoritative records.

**Traceability:** S23.R01–R04; S26.R01–R03; S24.R01–R03; S25.R01–R03; S48.R01–R03; X01–X10.

## 2. Binding institutional canon

1. Saltwater has one police service for its single sovereign city-state and one playable city.
2. The police department is the deepest and primary institutional simulation.
3. The department must be alive, internally coherent, persistent and operationally functional.
4. The planning baseline is approximately **500 individually recorded police personnel**, all included within the 10,000-person total population cap. The police count is a subset, never an additional population.
5. Every officer/personnel member has one canonical BP-03 person identity and one authoritative BP-06 personnel record. A rank, post, position, assignment or role never creates another person.
6. Rank, position, grade, authority, powers, clearance, qualification, appointment and assignment are separate concepts. They must never be treated as interchangeable.
7. Organisational need may require deployment outside an officer's preference, but deployment must respect the applicable authority, competence, qualification, safety, staffing and other recorded constraints.
8. The organisation must continue to function when posts are vacant, personnel are absent, units are unavailable or a command role is temporarily unfilled.
9. The department's structure cannot be changed through uncontrolled narrative generation. Reorganisation is a versioned, authorised change under BP-30/BP-44.
10. No police staffing or personnel seed is authorised by this specification.

## 3. Institutional mandate and service scope

### 3.1 Mandate
The SPD's fictional mandate is to maintain public safety and order within Saltwater, prevent and detect crime, respond to incidents, protect people and property, investigate offences, preserve evidence, enforce applicable fictional law and support lawful judicial processes.

The exact constitutional/legal source of powers is owned by BP-01/BP-27/BP-30. BP-05 records the institutional scope and the source authority for each function; it does not invent unlimited police powers.

### 3.2 Functional responsibilities
The department's structure must provide accountable ownership for:
- command and strategic direction;
- local and specialist policing;
- patrol and response;
- emergency communications and dispatch;
- incident and crime recording;
- investigation and case supervision;
- specialist investigative and technical support;
- evidence, forensic and crime-scene interfaces;
- intelligence and analytical support;
- custody and arrest interfaces;
- traffic, roads and public-event policing where required;
- public protection and victim/witness support interfaces;
- professional standards and internal accountability;
- training, recruitment and development;
- personnel, welfare and workforce administration;
- finance, procurement, facilities and resources;
- information, records, technology and communications;
- audit, performance, planning and organisational resilience.

The existence of a function does not require a separate division or a fixed unit. The approved organisational design determines whether a function is a standalone command, division, branch, team, post or shared responsibility.

### 3.3 Jurisdiction
The department's operational jurisdiction is Saltwater's single city-state boundary. Off-map liaison or mutual assistance may be represented as a relationship with an external entity, but it does not create another local police district, territory or playable jurisdiction. Cross-boundary authority must be explicitly sourced and scoped.

## 4. Organisational hierarchy and component model

### 4.1 Supported hierarchy
The architecture must support a hierarchy of:
- department;
- command/portfolio;
- division/directorate;
- branch/section;
- unit/team;
- post/position;
- individual assignment.

Not every level must be used in every branch. A small specialist team may report directly to a division; a large operational division may contain several branches and units. Hierarchy depth is configurable through approved change, not hard-coded as a universal number.

### 4.2 Component identity
Every organisational component receives a stable ID:
- `department_id`;
- `command_id`;
- `division_id`;
- `branch_id`;
- `unit_id`;
- `team_id`;
- `position_id`;
- `post_id`;
- `reporting_link_id`;
- `delegation_id`;
- `structure_version_id`.

IDs are immutable and never reused. Names, reporting lines, scope and parent components may change with version history. A unit's closure does not erase its historical records or the cases/actions it owned.

### 4.3 Structure record
Each component record includes:
- stable ID and component type;
- official name, abbreviation and aliases;
- parent component;
- mission/purpose;
- functional remit;
- included and excluded responsibilities;
- geographic/operational scope;
- command owner and supervisor role;
- positions/posts authorised;
- minimum/target/maximum staffing where approved;
- authority and delegation references;
- required capabilities/qualifications;
- resource dependencies;
- service hours/on-call expectations;
- activation status and effective dates;
- predecessor/successor references;
- provenance and approving authority.

### 4.4 No false hierarchy
A person may hold a rank and occupy a position in a separate organisational branch. A unit may be operationally attached to one command while administratively supported by another. Such relationships must be explicit and typed; do not infer one from the other.

## 5. Rank, position, grade, authority and related distinctions

These concepts are independent dimensions.

| Concept | Meaning | Primary owner |
|---|---|---|
| Rank | Recognised police rank held by an officer | BP-06; progression BP-07 |
| Position | Organisational role/post occupied at a given time | BP-05 structure; appointment BP-06 |
| Grade | Pay/role classification or employment grade | BP-06/BP-33 |
| Authority | Decision/command power delegated by law, policy or appointment | BP-05 framework; BP-30 decision governance |
| Powers | Specific legal/operational powers and limits | BP-27/BP-30; referenced by BP-05 |
| Clearance | Information/system/facility access level | BP-42 |
| Qualification | Verified competence/credential for a task | BP-32 |
| Appointment | Formal placement into a post/acting role | BP-06/BP-30 |
| Assignment | Current operational tasking or deployment | BP-08 |
| Command relationship | Who directs, supervises or is accountable for whom | BP-05 |
| Seniority | Service/rank/appointment precedence under defined rules | BP-06/BP-07 |
| Acting status | Temporary assumption of a defined role with limits | BP-06/BP-30 |

An officer's rank alone does not automatically grant every command power, specialist qualification, clearance or position. A person occupying a senior post may have delegated authority within that post without changing substantive rank. An acting appointment must state its duration, scope, delegations, limits and authorising source.

## 6. Command architecture

### 6.1 Command roles
The department must define:
- chief executive police leadership role;
- deputy/assistant leadership roles if adopted;
- command portfolio owners;
- division heads;
- branch/unit commanders;
- first-line supervisors;
- operational incident commanders;
- specialist advisers and delegated authorities.

Exact titles, numbers, rank equivalence and tenure rules are controlled canon decisions. BP-05 must not invent a command roster or alter the approved career/retirement rules.

### 6.2 Command dimensions
Each command role must specify:
- organisational scope;
- command authority;
- administrative responsibility;
- operational decision scope;
- supervision span;
- budget/resource delegation;
- policy approval/recommendation powers;
- emergency succession;
- acting appointment process;
- escalation route;
- accountability and review.

Administrative reporting and operational command may differ. A specialist officer may remain administratively within a specialist unit while temporarily operating under an incident commander. Both relationships must be recorded, with scope and time boundaries.

### 6.3 Command chain and escalation
Every active organisational component must have:
- a valid parent or explicitly approved direct-report relationship;
- an accountable command owner;
- a fallback/succession route;
- a means to escalate urgent operational or welfare concerns;
- a way to record an instruction, its authority, recipient, time and execution status.

No command chain may be circular. A person cannot simultaneously be the sole approver and sole independent reviewer of the same controlled decision where separation is required by the governing policy.

### 6.4 Acting and temporary command
Temporary command arrangements must identify:
- substantive post-holder;
- acting post-holder;
- authorising officer/body;
- start and expected end;
- scope and delegated powers;
- limitations and retained decisions;
- handover record;
- termination/extension event.

An acting role does not silently change the person's substantive rank, grade, clearance or career status.

## 7. Divisions and functional architecture

The organisational model must support, but does not force, the following functional portfolios:
1. executive command and strategic management;
2. uniformed/local policing and patrol;
3. emergency communications and dispatch;
4. investigations and specialist crime;
5. intelligence and analytical support;
6. crime scenes, evidence and forensic liaison;
7. custody and prisoner handling interfaces;
8. roads, traffic and public-event operations;
9. public protection and vulnerable-person response;
10. professional standards and complaints;
11. learning, training and development;
12. recruitment, personnel and workforce support;
13. finance, procurement and administration;
14. fleet, facilities, equipment and logistics;
15. information technology, records and communications;
16. planning, performance, inspection and organisational assurance.

These are functional domains, not a pre-approved list of 16 divisions. The final division/branch/unit structure, names and headcount must be recorded in the controlled organisational structure register. A function may be combined with another where scale justifies it, provided ownership and accountability remain unambiguous.

### 7.1 Functional coverage matrix
For every required police function, the register must state:
- accountable owner;
- operational performer;
- supervisor;
- supporting units;
- required competencies;
- resource dependencies;
- service coverage/hours;
- escalation route;
- source records;
- continuity arrangement when unavailable.

No critical function may be left ownerless. No two units may claim exclusive authority for the same decision without an explicit joint or delegated model.

## 8. Positions, posts and establishment

A position is an organisational role; a post is an authorised slot that may be filled or vacant. A position description defines duties and decision scope. A post record defines whether the slot is authorised, funded, active, vacant, frozen or abolished.

Each position/post should define:
- stable ID;
- parent unit;
- role title and purpose;
- duties and boundaries;
- supervisor/reporting line;
- rank/grade eligibility range if defined;
- mandatory qualifications and experience;
- authority and delegations;
- clearance requirements;
- staffing status;
- funding/resource reference;
- shift/on-call requirements;
- effective dates and approval.

A vacancy is an organisational state, not a person. Multiple people cannot simultaneously fill one exclusive post unless the post is explicitly job-shared or uses a defined rotation. A person may not occupy mutually exclusive full-time posts simultaneously without a valid part-time/acting arrangement.

The authorised establishment, filled posts and actual personnel count must reconcile but remain distinct measures.

## 9. Reporting lines, supervision and accountability

### 9.1 Relationship types
Support typed links:
- direct line management;
- operational command;
- professional supervision;
- administrative support;
- functional coordination;
- temporary attachment;
- incident command;
- acting/succession;
- independent oversight.

Each link has start/end time, source, scope and status. A single officer may have multiple relationship types, but the system must prevent ambiguity about who can issue which instruction.

### 9.2 Span of control
The structure should support realistic supervisory capacity without hard-coding a universal span. Each unit defines expected supervisory coverage, shift distribution, specialist complexity and contingency arrangements. Overloaded or unstaffed supervision is a visible organisational risk, not silently ignored.

### 9.3 Accountability
Every material function, post, decision class and record type must have an accountable owner. Responsibility may be delegated, but delegation does not erase the original accountable authority unless formally transferred.

## 10. Organisational lifecycle and change

### 10.1 Component lifecycle
Components support:
- proposed;
- approved;
- active;
- temporarily suspended;
- under reorganisation;
- merged;
- split;
- renamed;
- closed/retired;
- historical.

Only approved components may receive live assignments or command authority. A proposed unit cannot dispatch officers or own cases as an active unit unless explicitly authorised as a temporary task group.

### 10.2 Reorganisation
A reorganisation must include:
- reason and desired outcome;
- affected components and posts;
- old/new structure diagrams or textual hierarchy;
- authority and approval;
- effective in-game date/time;
- staff and command transfer plan;
- open case/incident ownership transfer;
- records and access permissions impact;
- resources, facilities and budget impact;
- temporary coverage and service continuity;
- training/qualification impacts;
- tests and post-change review.

The change must preserve historical reporting lines and command authority at the time of past decisions. It must not rewrite who supervised an officer or owned a case at an earlier date.

### 10.3 Closure and merger
Closing a unit does not close its cases automatically. Cases, incidents, personnel, resources, assets, records and responsibilities must be transferred to valid successors or explicitly retained under a historical custodian. No reference may point to a deleted component.

## 11. Department-wide staffing architecture

BP-05 defines authorised establishment and structural staffing requirements; BP-06 owns individual police personnel records; BP-07 career; BP-08 assignment/rosters; BP-09 resources; BP-33 employment/attendance.

The approximate 500-person police baseline must be represented as distinct individual personnel records, not anonymous headcount alone. All are part of the 10,000 population cap. This specification does not seed or allocate those people.

Staffing measures must distinguish:
- authorised posts;
- funded posts;
- filled posts;
- active personnel;
- temporarily absent personnel;
- restricted/unavailable personnel;
- deployable personnel;
- personnel on duty;
- personnel assigned to a unit;
- personnel assigned to an incident;
- vacancies and frozen posts.

A department may have 500 personnel but fewer than 500 deployable officers at a given time. Staffing plans must account for leave, training, sickness, restrictions, command duties, specialist availability, shift coverage and minimum service obligations.

### 11.1 Structural staffing rules
- Every active post has a defined role and valid reporting line.
- Every filled post links to one canonical person/personnel record.
- A personnel record may have only one substantive primary post at a time unless an approved shared/dual-post arrangement exists.
- Temporary acting/attachment assignments are separately recorded.
- No post may be filled by a person who lacks a mandatory qualification or authority unless an explicitly valid supervised exception is recorded.
- Vacancy does not automatically create a replacement person.
- Staffing totals are projections from personnel/post relationships, not independent duplicate headcounts.

## 12. Operational command vs organisational command

Operational command is incident/task-specific and may temporarily supersede ordinary line direction for the scope of the operation. It does not automatically alter the permanent organisational chart.

An operational command record must identify:
- operation/incident ID;
- incident commander and command level;
- command start/end;
- geographic/functional scope;
- delegated authority;
- participating units;
- reporting/communications structure;
- safety and escalation arrangements;
- handover and termination.

An officer can therefore have:
- substantive line manager;
- unit commander;
- shift supervisor;
- incident commander;
- specialist technical supervisor.

The system must resolve which authority applies to a particular action and time. Conflicts must be surfaced and resolved by the relevant policy/command process, not by guessing based solely on rank.

## 13. Interagency and external relationships

The department may maintain structured liaison with:
- emergency-service agencies;
- government and public bodies;
- courts/prosecution/corrections;
- healthcare and welfare providers;
- transport and utility operators;
- educational institutions;
- businesses and property operators;
- community organisations;
- external police or specialist agencies for off-map assistance.

Each relationship defines purpose, contact/liaison role, information-sharing scope, authority, service interface, time validity and provenance. An external agency is an off-map entity reference unless explicitly represented as an in-city organisation under BP-04. No external liaison creates another playable jurisdiction.

BP-11/BP-12 own dispatch and incident handoffs; BP-27/BP-28 own legal process/court interfaces; BP-30 owns institutional agreements and authority.

## 14. Governance and policy interface

BP-05 defines the structural places where governance decisions are made. BP-30 owns policy lifecycle, command orders, approval, delegation and institutional governance. BP-31 owns standards, complaints and discipline. BP-32 owns training and qualifications. BP-33 owns employment processes.

The organisational architecture must provide:
- policy owner and approving authority;
- command authority register;
- delegation register;
- meeting/briefing and decision forums where used;
- audit/inspection access;
- complaints and escalation route;
- succession and continuity plan;
- controlled organisational chart versions.

A policy cannot be treated as valid solely because it appears in an officer's narrative. It must have a source, owner, approval state, effective time and version.

## 15. Security, clearance and information architecture

BP-05 specifies structural security roles and sensitivity needs; BP-42 owns actual permission enforcement.

The architecture must distinguish:
- public organisational information;
- internal operational information;
- confidential personnel/HR information;
- restricted intelligence/investigation information;
- sensitive operational plans and tactics;
- protected witness/victim information;
- executive/command material;
- system administration and security credentials.

A rank or position does not automatically grant unrestricted access. Clearance, task purpose, case assignment, role and explicit permissions must be evaluated by BP-42. The department's chart must not expose hidden case truth or confidential information through titles, unit names, staffing summaries or reporting metadata.

## 16. Department activity and institutional continuity

The department must function across:
- ordinary shifts;
- peak demand;
- simultaneous incidents;
- major emergencies;
- command vacancies;
- staff absence;
- specialist unavailability;
- unit suspension;
- resource shortage;
- system outage;
- investigation/case surges;
- reorganisation;
- leadership succession.

Continuity rules:
- command succession is explicit;
- urgent functions have fallback ownership;
- critical records remain accessible to authorised successors;
- open cases and incidents retain accountable owners;
- resource limitations are visible;
- staff cannot be double-booked;
- absence does not silently transfer authority;
- a closed unit's responsibilities are transferred or suspended explicitly;
- no operational command or event proceeds while the simulation clock is paused.

BP-35/BP-37 govern simulation activity and time. BP-05 supplies valid organisational state and authority relationships.

## 17. Data and event contracts

BP-05 defines logical records; BP-38 determines physical schemas and constraints.

| Record family | Required meaning | Owner |
|---|---|---|
| Department profile | Mandate, jurisdiction, status, version | BP-05 |
| Structure version | Complete effective-dated hierarchy | BP-05 |
| Organisational component | Unit/division/branch identity and remit | BP-05 |
| Position/post | Duties, authority, requirements and vacancy state | BP-05 |
| Reporting relationship | Typed, scoped, time-valid command/supervision link | BP-05 |
| Authority framework | Structural authority classes and delegation references | BP-05/BP-30 |
| Command succession | Primary/fallback/acting command and effective interval | BP-05/BP-30 |
| Establishment plan | Authorised/funded post totals and staffing assumptions | BP-05/BP-34 |
| Personnel occupancy link | Person/personnel ID filling a post | BP-06 |
| Career/rank history | Rank and career transitions | BP-06/BP-07 |
| Duty/assignment link | Current operational deployment | BP-08 |
| Operational command record | Incident-specific command and handover | BP-08/BP-12 |
| Governance decision | Policy/order/delegation approval | BP-30 |
| Structural change event | Reorganisation, transfer, closure or creation | BP-05/BP-30/BP-44 |
| Structure audit | Reconciliation of posts, personnel and reporting lines | BP-05/BP-38 |

Every material structure/authority change records unique event ID, component IDs, prior/new state, effective in-game time, recorded time, actor, authority, reason, source, approvals, impact links and test evidence.

## 18. Failure modes and edge cases

The architecture must handle:
- vacant chief or senior command role;
- simultaneous absence of multiple commanders;
- acting appointment with limited authority;
- acting appointment expiry during an active operation;
- conflicting administrative and operational reporting lines;
- circular reporting relationship;
- officer assigned to a unit that has closed;
- post filled by an ineligible or unqualified person;
- one officer occupying incompatible exclusive posts;
- unit with no supervisor or insufficient coverage;
- unit with more cases/tasks than its staffing can support;
- command role held by a person whose rank differs from normal expectation;
- temporary task group without permanent chart status;
- interagency command handoff;
- emergency command succession;
- structure change while incidents/cases remain open;
- reorganisation with staff, resources and records in transit;
- duplicate component names or IDs;
- retired unit referenced by a historical record;
- unauthorised command/position change;
- authority claim unsupported by policy/appointment;
- rank incorrectly used as a proxy for clearance or power;
- staffing total inconsistent with BP-06/BP-08/BP-33;
- command decisions made while simulation time is paused.

The system must preserve the last valid structure, reject invalid authority transitions and record a resolvable exception. It must not invent a commander or transfer responsibility silently.

## 19. Acceptance criteria and test suite

### A. Institutional mandate and hierarchy
- **AC-A01:** Exactly one Saltwater Police Department institutional identity exists.
- **AC-A02:** Its jurisdiction resolves only to the approved Saltwater city-state.
- **AC-A03:** Every active component has a valid identity, parent/reporting structure and accountable owner.
- **AC-A04:** Hierarchy supports department, command, division, branch, unit, team and post without forcing unused levels.
- **AC-A05:** No circular command/reporting relationships are accepted.
- **AC-A06:** Every critical function has an accountable owner and continuity route.

### B. Authority distinctions
- **AC-B01:** Rank, position, grade, authority, powers, clearance, qualification, appointment and assignment are separately represented.
- **AC-B02:** Rank alone cannot grant a position, qualification, clearance or unrecorded delegation.
- **AC-B03:** Acting appointments include scope, start/end, authoriser and limitations.
- **AC-B04:** Administrative and operational command relationships can coexist without ambiguity.
- **AC-B05:** Every command decision resolves the authority applicable at its effective time.

### C. Posts and staffing
- **AC-C01:** Every authorised post has duties, eligibility, reporting line and status.
- **AC-C02:** Vacant, frozen, funded, filled and abolished posts are distinct.
- **AC-C03:** Every filled post links to one canonical BP-03 person and BP-06 personnel record.
- **AC-C04:** Approximately 500 individually recorded police personnel reconcile as a subset of the 10,000 population cap.
- **AC-C05:** Staffing summaries reconcile to BP-06, BP-08 and BP-33 without duplicate counts.
- **AC-C06:** Ineligible/underqualified appointments are rejected or recorded only under a valid exception.
- **AC-C07:** Exclusive posts cannot be double-filled.

### D. Command, continuity and change
- **AC-D01:** Command succession resolves when a post-holder is absent or vacant.
- **AC-D02:** Temporary acting command expires or is renewed through an authorised event.
- **AC-D03:** Operational command is scoped to its incident/task and does not silently alter the permanent chart.
- **AC-D04:** Unit closure/reorganisation transfers or explicitly suspends open responsibilities.
- **AC-D05:** Historical command relationships remain queryable at the time of past decisions.
- **AC-D06:** Reorganisation records authority, reason, impact, effective time and evidence.
- **AC-D07:** No command/structure event executes while simulation time is paused.

### E. Governance and interagency
- **AC-E01:** Structural authority and policy approval are linked to BP-30 governance records.
- **AC-E02:** Professional standards and complaint ownership resolve to BP-31.
- **AC-E03:** Training/qualification requirements resolve to BP-32.
- **AC-E04:** Employment and attendance resolve to BP-33.
- **AC-E05:** Interagency relationships have defined purpose, authority, scope and time validity.
- **AC-E06:** External liaison cannot create a second playable jurisdiction.

### F. Security and quality
- **AC-F01:** Rank and position do not bypass BP-42 permission checks.
- **AC-F02:** Restricted personnel, intelligence and operational information are not exposed through organisational views.
- **AC-F03:** Every material structural change is attributable and auditable.
- **AC-F04:** Component identity, reporting lines and post occupancy reconcile across version changes.
- **AC-F05:** Historical references to retired components remain valid.
- **AC-F06:** All tests have source requirement links and reproducible evidence.

Required test classes: hierarchy integrity, circularity, authority resolution, acting-role expiry, vacancy/succession, staffing reconciliation, reorganisation migration, historical query, interagency boundary, permission enforcement, concurrent command changes, paused-clock protection, scale and regression.

## 20. Source traceability

| Source IDs | BP-05 obligation |
|---|---|
| S23.R01–R04; S23.T01 | Mandate, ranks/positions/authority distinctions, hierarchy, appointment and organisational functionality |
| S24.R01–R03; S24.T01 | Personnel/career and competence interfaces |
| S25.R01–R03; S25.T01 | Roster, staffing, deployment and attendance interfaces |
| S26.R01–R03; S26.T01 | Command, policy, orders, supervision and accountable decisions |
| S48.R01–R03; S48.T01 | Role structure, least privilege, information boundaries and audit |
| X01–X10 | Stable identity, source of truth, time, reconciliation, epistemic distinction, originals, pause, text-first, police-depth and evidence-based completion |

The complete source wording and exact source pointers remain in the preserved 52-division JSON and crosswalk.

## 21. Open decisions

1. Exact SPD command titles and approved rank-to-post eligibility rules.
2. Final number and names of divisions, branches and units.
3. Exact allocation of the approximately 500 police personnel across functions and shifts.
4. Chief appointment/tenure and succession detail, to be reconciled with BP-07 and BP-30.
5. Formal authority/powers matrix, sourced to BP-27/BP-30.
6. Which functions are 24-hour, on-call, shift-based or office-hours.
7. Exact staffing minimums, supervisory spans and establishment/funding model.
8. Final organisational chart baseline and effective date.

No structure, rank or personnel allocation is silently invented by this draft. These decisions do not weaken the requirement for a fully functional, accountable department.

## 22. Completion statement

**Design status:** `DESIGNED_DRAFT`; complete institutional architecture, authority distinctions, hierarchy, lifecycle, interfaces, continuity, exceptions and acceptance suite drafted. Exact command titles, unit structure and staffing allocations remain open.  
**Implementation status:** `NOT_STARTED` unless separately evidenced.  
**Test status:** `NOT_STARTED`.  
**Verification status:** `NOT_STARTED`.

No Neon schema, migration, seed, import, upload or database write is performed or authorised by this document.
