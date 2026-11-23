# BP-30 — Department Governance

**Division:** BP-30  
**Title:** Department Governance  
**Specification version:** 1.0  
**Status:** DESIGNED_DRAFT  
**User approval:** PENDING  
**Implementation / test execution / verification:** NOT_STARTED  
**Authority:** Adopted Saltwater BP-01–BP-44 master blueprint and binding Saltwater canon. This document defines governance architecture; it does not enact fictional law or authorise database writes.

## 1. Purpose

BP-30 defines the governance of Saltwater's public institutions and, in particular, the institutional governance of the Saltwater Police Service. It establishes how mandates, offices, authority, policy, command delegation, institutional decisions, oversight and accountability are represented and controlled.

The division ensures that every material official act is attributable to a competent actor, supported by an authority source, bounded by scope and preserved as a historical record. It provides a coherent governance framework without duplicating operational, personnel, disciplinary, financial, records or legal-process systems owned elsewhere.

BP-30 is not a general-purpose government simulator. It models public institutions and police governance to the depth needed for a functioning police-centred world. Police operations remain governed and executed by their dedicated divisions; BP-30 defines the institutional authority and governance controls those operations consume.

## 2. Binding Saltwater canon

1. Saltwater is one fictional sovereign city-state, one playable city and one jurisdiction. No second city, external playable territory or world expansion is created.
2. The hard cap is **10,000 living people total**, including approximately 500 individually recorded police personnel. Police are a subset of the total, not additional population.
3. At least **10,000 businesses** remain in the city. Governance design cannot reduce or replace this baseline.
4. Police is the deepest simulation. Other public institutions are represented sufficiently to support policing and credible public administration, not as equally deep simulators.
5. Text is the permanent primary interface; no essential governance fact or action depends on graphics.
6. BP-37 is the sole simulation clock. No appointment, deadline, order, policy, complaint, audit, NPC action or institutional process progresses while the player is absent or the simulation is paused.
7. Every person has one canonical identity. Multiple offices, ranks or roles never create duplicate people.
8. Anyone materially connected to police activity/casework and promoted to full persistent simulation remains permanently promoted; never downgrade or duplicate them.
9. NPCs know only what they observed, received or were authorised to access.
10. Hidden culprit/accomplice/perpetrator truth is not revealed unless the player types exactly `bingo`. Governance systems must not become an indirect disclosure route.
11. The player controls their individual officer's actions. Governance does not railroad investigations or supply unsolicited investigative hints.
12. No Neon schema, migration, seed, import, bulk write or upload is authorised by this specification.

## 3. Scope

### 3.1 Included

- Public institutional architecture, mandates and accountability relationships.
- Executive, legislative, administrative and oversight offices at proportionate institutional depth.
- Police institutional governance, policy authority and command delegation.
- Appointment, incumbency, acting appointments, vacancy and succession interfaces.
- Orders, policies, approvals, briefings, strategic direction and governance review.
- Institutional decision provenance and authority validation.
- Public administration governance, procurement approval boundaries, permits and inspections at mandate/authority level.
- Institutional oversight, complaints governance, independent review and public accountability interfaces.
- Interagency agreements and institutional coordination mandates.
- Governance audit, reporting, access boundaries, time and persistence contracts.

### 3.2 Excluded

- Sovereign canon and global governing rules: BP-01.
- Territory, districts, addresses and spatial jurisdiction: BP-02.
- Person identity, population and person lifecycle: BP-03.
- Canonical organisation, business, property and premises records: BP-04.
- Police mandate and organisational architecture, rank/grade/position taxonomy: BP-05.
- Police personnel master records: BP-06.
- Career, promotion, retirement and tenure mechanics: BP-07.
- Unit establishment, operational deployment and staffing execution: BP-08.
- Resource inventory and facilities: BP-09.
- Patrol and field operations: BP-10.
- Emergency call-taking and dispatch: BP-11.
- Operational incident command and incident records: BP-12.
- Crime, case, investigation and participant records: BP-13–BP-18.
- Interviews, surveillance, intelligence, scenes, evidence and forensics: BP-19–BP-24.
- Arrests, warrants, police custody, prosecution and courts: BP-25–BP-28.
- Correctional execution: BP-29.
- Misconduct and complaint case lifecycle, professional standards and disciplinary findings: BP-31.
- Training and qualification delivery: BP-32.
- Employment, payroll and HR administration: BP-33.
- Financial accounting, budgets, procurement transactions and ledgers: BP-34.
- Simulation engine, relationships, time, records, persistence, interface, notifications, security, QA and change control: BP-35–BP-44.

## 4. Ownership and boundaries

| Concern | Authoritative owner | BP-30 responsibility |
|---|---|---|
| Sovereign canon, constitutional invariants | BP-01 | Apply approved rules; no unilateral canon amendment |
| Geography and jurisdiction boundary | BP-02 | Reference jurisdiction IDs and institutional scope |
| Person identity and population | BP-03 | Reference officeholders; no duplicate people |
| Public body/business/premises identity | BP-04 | Define governance mandate and accountability links |
| Police mandate and organisational architecture | BP-05 | Set governance policy/delegation within approved architecture |
| Officer personnel record | BP-06 | Reference personnel; never create a shadow personnel master |
| Career, appointments and retirement mechanics | BP-07 | Consume valid appointment/tenure outcomes; govern authority boundaries |
| Unit establishment and deployment | BP-08 | Issue approved strategic direction; no operational roster ownership |
| Operational command execution | BP-08/BP-12 | Define delegation and policy; do not rewrite operational records |
| Misconduct/complaint investigation and discipline | BP-31 | Institutional oversight and response to findings |
| Training/qualification | BP-32 | Set governance expectations; no training delivery records |
| Employment/HR | BP-33 | Set institutional accountability; no employment ledger |
| Public/police finance and procurement transactions | BP-34 | Define approval authority; no financial ledger |
| Case and investigative command | BP-15/BP-16 | Governance-level oversight only; no case lifecycle ownership |
| Legal hierarchy and proceedings | BP-27/BP-28 | Respect legal authority; no judicial or prosecution decision |
| Records and provenance | BP-38 | Supply domain accountability; follow common record contract |
| Security and access enforcement | BP-42 | Define required governance scopes; BP-42 enforces |
| Reporting/publication | BP-41 | Define approval and accountability; BP-41 delivers |
| Configuration and canon changes | BP-44 | Submit changes through formal change control |

A governance decision is not an operational event. A policy authorisation is not proof of implementation. A command order is not proof of receipt or execution. An oversight recommendation is not a binding order unless an authorised rule expressly makes it one. A complaint is not a finding. A finding is not automatically a remedy or completed institutional response.

## 5. Institutional architecture

Every public institution must have a canonical BP-04 organisation reference, a defined mandate, jurisdictional scope, accountable office(s), decision authority, reporting relationships, oversight route and lifecycle. BP-30 defines institutional governance relationships; BP-04 remains authoritative for the organisation's identity, premises and operational existence.

The institutional catalogue may represent:
- sovereign/executive offices;
- legislative or representative offices;
- public administration departments;
- independent oversight bodies;
- police governance offices and command institutions;
- public service authorities;
- emergency-service agencies;
- other proportionate public institutions required by the city.

This catalogue does not imply that every institution needs a large staff, independent simulation engine or elaborate internal bureaucracy. Each institution receives only the structure necessary for its mandate and interactions.

An institution may be proposed, constituted, active, suspended, reorganised, merged or dissolved. Each transition requires an authorised act and effective simulation time. Historical decisions, incumbents, mandates and records remain queryable after reorganisation or dissolution. Dissolution does not erase outstanding obligations, cases, complaints or records; it requires an explicit successor/transfer arrangement.

## 6. Offices, incumbency and authority

An office is a stable institutional position with a defined mandate, powers, constraints, appointment route, term rules (if any), reporting line, succession rule and access profile. An officeholder is a canonical BP-03 person linked to that office for a bounded effective interval.

Fields include office_id; institution_id; title; mandate; jurisdiction; authority_set; exclusions; appointment_method; term_rule; eligibility_rule_ref; reporting_line; oversight_route; incumbent_person_id; acting_person_id; status; effective_from/to; configuration_version; audit references.

The following concepts remain distinct:
- institution;
- office;
- incumbent;
- rank;
- grade;
- position;
- appointment;
- delegation;
- authority;
- power;
- clearance;
- qualification;
- operational assignment.

Holding a title does not automatically grant every power associated with the institution. Powers are explicit, scoped and effective-dated. Eligibility, appointment and qualification mechanics remain with BP-05/BP-06/BP-07/BP-32 as appropriate.

Vacancy is a valid state. Acting appointment must identify the office covered, delegated scope, exclusions, authority, effective interval and termination condition. Acting service does not silently confer permanent appointment, promotion or rank. Succession follows a configured rule and records each step; if no valid successor exists, the office remains vacant and escalation is explicit.

## 7. Authority model and separation of functions

Every authority grant has:
- a unique authority/delegation ID;
- source institution and office;
- granting actor and legal/configuration basis;
- recipient office/person/role;
- permitted actions and scope;
- excluded actions;
- jurisdiction and affected entities;
- effective start/end;
- sub-delegation permission or prohibition;
- revocation/suspension conditions;
- review/audit references.

Delegated authority cannot exceed the grantor's authority. Delegation does not automatically remove the grantor's accountability. Sub-delegation is prohibited unless expressly enabled. Conflicting grants are flagged for resolution rather than combined into an unlimited permission set.

Separation of functions is enforced through the authority matrix. The person who proposes a decision may not necessarily approve or review it. Where a conflict exists, an independent competent office or reviewer is assigned under configuration. No officeholder may decide a complaint or review in which they have an unmanaged personal or institutional conflict.

Emergency powers are not assumed. Each emergency authority must define trigger, scope, eligible issuer, permitted actions, duration, geographic reach, review, notification and termination. It cannot suspend the fixed population cap, single-city scope, time freeze, information firewall or user-approved change control.

## 8. Police governance and command policy

BP-30 governs police institutional policy, command delegations, strategic direction, command accountability and governance review. BP-05 defines the police mandate, hierarchy and organisational architecture. BP-06 owns each officer's personnel record. BP-07 owns career and appointment mechanics. BP-08 owns unit establishment/deployment. BP-12 owns operational incident command.

Police command decisions must identify:
- issuing office/person and authority;
- recipient command/unit/person;
- decision type and purpose;
- scope, geography and affected operations;
- policy/order version;
- effective time and expiry/review trigger;
- rationale and information considered;
- restrictions and escalation route;
- acknowledgement and execution-report references.

Strategic direction, standing policy, operational order, incident command instruction, personnel appointment and disciplinary sanction are different record types. BP-30 cannot use a strategic order to alter a live incident chronology, assign a patrol unit directly, change an officer's personnel history or determine a misconduct finding.

The approximately 500 police-personnel planning baseline remains subordinate to the 10,000 living-person cap and the approved establishment. BP-30 does not create officers or posts. Vacant posts are not people. Every serving officer is one BP-03 person with one BP-06 authoritative personnel record, even when holding multiple assignments or offices.

## 9. Orders, instructions and briefings

An order record includes order_id; issuer; issuer_authority_ref; recipient/scope; order_type; text/structured direction; policy_version; issue/effective/expiry times; priority; restrictions; acknowledgement state; execution owner; completion evidence; supersession/revocation references; audit.

Lifecycle states include draft, submitted, authorised, issued, acknowledged, effective, partially executed, completed, suspended, superseded, revoked, expired and disputed. Not every order uses every state; transitions are configured by order type.

An order is valid only if its issuer has authority for the action, recipient and scope. A recipient's acknowledgement means receipt, not agreement or execution. Execution must be reported by the operational owner. A refusal, inability, conflict or delay is recorded with reason and escalation path. The original order is immutable; amendments create a new version and link to the prior one.

Briefings may communicate policy, intelligence authorised for the audience, operational plans or safety information. BP-30 records governance-level issuance and acknowledgement requirements. Operational briefing content and records remain with the operational owner where applicable.

## 10. Policy lifecycle

Policy records include policy_id; title; owner; purpose; scope; authority; approving office; version; status; effective interval; superseded version; affected roles; publication/distribution requirements; review date; exceptions; audit.

Policy lifecycle: proposed, drafted, consulted (if configured), submitted, approved, effective, under review, amended, suspended, superseded, withdrawn. Approval and effective date are distinct. Drafts must never be represented as binding policy. Historical policy remains available for determining what rule applied at a particular simulation time.

Policy must be consistent with BP-01 canon, sovereign authority, jurisdiction and higher-level rules. Conflicts are flagged; a lower-level policy cannot override a higher-level authority. Retroactive effect is prohibited unless an explicit configured rule permits it and the record identifies the legal basis and affected interval.

Policy exceptions are individually authorised, bounded and auditable. A local exception cannot silently become a general policy change. Interpretation notes and AI summaries are derivative aids, not replacements for the approved text.

## 11. Institutional decisions and approvals

A decision record contains decision_id; decision class; responsible office; proposing actor; approving actor(s); authority source; scope; affected records; material considered; rationale; alternatives; conflict declarations; decision; effective time; review route; notification; implementation owner; status; version.

Approval workflows may require one or more authorised actors depending on decision class. The system validates the actor's authority at the decision's effective time. Approval cannot be inferred from silence, a job title or a later action. A decision may be refused, deferred, returned for information, approved with conditions or approved.

Decision review can confirm, vary, revoke or refer a prior decision. The review creates a new event and never rewrites the original rationale or source set. Where a decision is challenged, disputed status remains explicit until a competent authority resolves it.

## 12. Public administration and service governance

BP-30 defines the mandate, accountability and oversight route for public administrative bodies. BP-04 represents the body, premises, business/provider and service identity. BP-34 owns public financial transactions and accounting. BP-38 owns public record standards.

Public policy, administrative decisions, procurement authority, permits, licensing and inspections must be attributed to competent offices. BP-30 can define who may approve or review these actions; the relevant operational owner records the application, transaction or service event. BP-30 must not create parallel application, licence, inspection or finance databases.

Social care, welfare, community support and other public services are represented proportionately. BP-04 owns provider identity and premises; BP-17 owns victim/witness support and safeguarding; BP-36 owns relationships/community context. BP-30 owns institutional mandate, public accountability and governance review, not individual clinical or service-delivery records.

Emergency-service agencies have defined mandates and coordination agreements. BP-04 owns agency identity; BP-11/BP-12 own emergency communications and incident coordination. BP-30 does not duplicate dispatch, patrol, fire/medical response or operational incident management.

## 13. Public finance and procurement authority boundary

BP-30 may define the institutional approval matrix for budgets, procurement, contracts and expenditure, but BP-34 is authoritative for financial accounting, budget ledgers, transaction posting, public finance and procurement execution.

Every approval identifies the competent office, amount/category threshold (when configured), budget reference, procurement route, conflict declarations and approval time. BP-34 validates available budget and records the financial transaction. BP-30 cannot post a payment, create a shadow ledger, alter balances or bypass financial controls.

Public assets and premises resolve to BP-04/BP-09 records. Ownership, inventory, maintenance and physical condition remain with their respective source divisions. Governance approval is not proof that an asset was purchased, received or placed into service.

## 14. Complaints, oversight and accountability

BP-30 owns institutional oversight architecture and governance response. BP-31 owns professional-standards complaint/misconduct case lifecycle and investigation/finding processes. BP-41 owns reporting/publication delivery. BP-38 owns record provenance; BP-42 enforces access.

A public complaint may be received through a configured route and assigned to the competent owner. BP-30 ensures there is a route, accountable institution, conflict check, oversight pathway and traceable response. It does not conduct the underlying misconduct investigation or decide the finding where BP-31 is the owner.

Oversight may include internal governance review, independent review, audit, inspection, public accountability hearing or other configured mechanism. Each review has scope, authority, reviewer, independence/conflict assessment, source set, findings, recommendations, publication decision and follow-up owner.

Complaint states distinguish received, acknowledged, screened, referred, accepted, under review, investigation pending, finding issued, response pending, remedy pending, resolved, closed, withdrawn and reopened. A case cannot be closed solely because it was referred or acknowledged. Unresolved status and reasons remain visible to authorised users.

A finding, recommendation, institutional response and remedy are separate. A recommendation is not automatically binding. A binding direction must identify the authority that makes it binding. The responsible institution records acceptance/dispute, implementation plan, owner, due simulation time and evidence of completion. Failure to act is retained and escalated under configured rules.

Public trust may change only through BP-35/BP-36 causal mechanisms based on recorded events and evidence. BP-30 cannot arbitrarily assign trust values or use public reporting to reveal hidden case truth.

## 15. Conflicts of interest, independence and recusal

Every material decision, complaint review, procurement approval, appointment and oversight activity must support conflict declaration and review. A conflict may arise from personal relationship, financial interest, prior involvement, supervisory responsibility, institutional liability or another configured basis.

The system records declared or identified conflict, source, affected decision, assessment, recusal/mitigation, replacement reviewer and decision authority. A recused actor cannot approve or review the same matter through another role unless an explicit, auditable exception is authorised.

Independent bodies must have an explicit mandate, appointment route, protected access boundary, reporting route and safeguards against interference. Independence does not imply unrestricted access to personal, intelligence, medical or hidden case information.

## 16. Interagency agreements and coordination

An agreement record includes agreement_id; parties; each party's authority; purpose; permitted information/services; exclusions; responsibilities; contact route; effective interval; review/termination; records and audit.

An agreement cannot grant powers that a party does not possess. Data sharing remains subject to BP-42 and source-owner permissions. Operational coordination remains with BP-11/BP-12 or the relevant service owner. A memorandum or agreement is not a blanket permission to read all records.

External entities may be referenced for necessary off-map interaction. No external playable city, population or jurisdiction is created. Agreements are limited to the fictional Saltwater jurisdiction and its explicitly permitted external interfaces.

## 17. Institutional lifecycle and reorganisation

Institutional change includes creation, mandate amendment, reorganisation, transfer of function, merger, split, suspension and dissolution. Each requires an authorised change act, effective simulation time, predecessor/successor links, affected offices, records, pending obligations, staff/asset transfer references and public notice where configured.

A reorganisation does not erase prior decisions or accountability. A successor institution inherits only the functions and records explicitly transferred. Historical actions remain attributed to the office and institution that performed them at the time.

Changes to constitutional structure, sovereignty, city boundary, population cap or fixed blueprint structure require BP-44 change control and explicit user approval. BP-30 cannot expand Saltwater or amend immutable canon through an ordinary institutional decision.

## 18. Inputs and outputs

### Inputs
- BP-01: governing canon and constitutional constraints.
- BP-02: jurisdiction and geographic scope.
- BP-03: canonical persons and population ledger.
- BP-04: institution, organisation, business and premises identities.
- BP-05: police mandate, hierarchy and authority taxonomy.
- BP-06/BP-07: officer records and appointment/career state.
- BP-08/BP-12: unit/operational command and execution status.
- BP-31: complaint/misconduct investigation and findings.
- BP-32/BP-33: qualification and employment state.
- BP-34: budgets, procurement approvals and financial transaction references.
- BP-35/BP-36: event-driven public trust and social context.
- BP-37: canonical simulation time and pause state.
- BP-38/BP-39: record identity, provenance, persistence and recovery.
- BP-41/BP-42: reporting, publication and access enforcement.
- BP-44: approved authority, policy, institutional and workflow configuration.

### Outputs
- Institutional mandates and governance relationships.
- Office and incumbency events/references.
- Authority grants, delegations, revocations and succession events.
- Approved policies and policy version notifications.
- Orders, approvals, briefings and governance decisions.
- Public administration approval/authority references.
- Oversight reviews, complaint routing and governance response.
- Conflict-of-interest and recusal records.
- Interagency agreements and institutional change events.
- Auditable notifications, reports and implementation acknowledgements.

Outputs are attributable and versioned. BP-30 emits instructions/references to owning divisions; it does not directly mutate their authoritative records.

## 19. Core entities and record fields

### 19.1 Institution governance profile
institution_id; mandate_version; jurisdiction; constitutional_basis; governing_offices; accountability_routes; oversight_body_refs; status; effective interval; source organisation; audit.

### 19.2 Office and incumbency
office_id; institution_id; mandate; authority_set; exclusions; incumbent_person_id; appointment_ref; acting_status; effective interval; vacancy/succession state; audit.

### 19.3 Authority grant/delegation
grant_id; grantor; recipient; authority source; permitted scope; exclusions; sub-delegation; effective interval; revocation; review; audit.

### 19.4 Policy
policy_id; version; owner; approval authority; status; scope; text/structured rules; effective interval; supersession; distribution; exception; audit.

### 19.5 Order/instruction
order_id; issuer; authority; recipient; type; scope; issue/effective/expiry; rationale; acknowledgement; execution owner; status; supersession; audit.

### 19.6 Governance decision
decision_id; proposer; approver; authority; material considered; rationale; conflict status; decision; effective time; review; implementation owner; audit.

### 19.7 Oversight review
review_id; mandate; reviewer; independence check; scope; sources; findings; recommendations; publication state; response owner; follow-up; audit.

### 19.8 Institutional complaint route
route_id; subject institution; intake channel; screening authority; owner division; conflict rules; referral path; status vocabulary; notification; audit. Complaint case details remain with BP-31 or the relevant owner.

### 19.9 Interagency agreement
agreement_id; parties; authority of each party; scope; responsibilities; data-sharing terms; effective interval; review; termination; audit.

## 20. State transitions and event contracts

Every material governance event records event_id, entity_id, event type, actor/person/office, authority reference, prior/new state, canonical simulation time, source version, reason, affected scope, correlation/idempotency key, result and audit reference.

Events include institution_proposed/constituted/reorganised/suspended/dissolved; office_created/appointed/vacated/acting_assigned/acting_ended; authority_granted/delegated/revoked; policy_drafted/submitted/approved/effective/amended/suspended/withdrawn; order_drafted/approved/issued/acknowledged/executed/superseded/revoked; decision_proposed/approved/refused/reviewed; conflict_declared/assessed/recusal_recorded; complaint_received/acknowledged/referred; oversight_started/finding_recorded/recommendation_issued/response_recorded/remedy_completed; agreement_signed/varied/terminated.

Events are append-only and idempotent. Duplicate replay cannot create duplicate appointments, approvals, orders, complaints or institutional transitions. Partial failure preserves completed steps and explicit incomplete status. A downstream acknowledgement is required before the system reports that a recipient accepted or executed an instruction.

## 21. Time and pause invariants

All effective dates, terms, appointments, orders, policy periods, reviews, deadlines and institutional events use BP-37 canonical simulation time.

When paused or absent:
- no appointment, succession, order, policy or governance decision progresses;
- no NPC official issues, receives or executes an order;
- no complaint, audit, review or remedy deadline advances;
- no public institution changes status or mandate;
- no interagency agreement takes effect or expires;
- no trust effect or institutional consequence is generated;
- no wall-clock time is applied on resume.

A date becoming due requires actual in-game time progression and a recorded event. Scheduled items remain pending while the clock is frozen.

## 22. NPC knowledge, AI and player agency

Officials and oversight actors know only facts observed, received or lawfully accessible within their roles. A senior title does not grant omniscient knowledge. Restricted police intelligence, source identities, medical information, protected complainant details and hidden crime-generation truth remain subject to their owners' access rules.

AI may assist with navigation, summaries, consistency checks and drafting proposals. It cannot independently appoint/remove an official, issue a binding order, approve expenditure, determine misconduct, impose discipline, change policy, grant access or amend canon. Any AI-produced proposal is clearly labelled and requires the authorised in-world actor and workflow.

The player sees only information their character can access. Governance UI must not reveal culprit/accomplice identity or generate investigative prompts. Exact `bingo` gating applies across records, summaries, notifications, metadata and search.

## 23. Permissions, audit and information boundaries

BP-42 owns enforcement. BP-30 defines access needs for institutional mandates, protected deliberations, appointments, policy drafts, orders, complaints routing, oversight records, conflict declarations, public reports and interagency agreements.

Access is checked against actor, office, role, institution, assignment, purpose, jurisdiction, record class and effective time. Public availability is an explicit publication state, not the default for internal records. Independent oversight access is bounded by mandate. Access to a summary does not grant access to source records.

Every read, export, disclosure, change, approval and denied access is audited. Public reports use approved/redacted derivatives and cannot disclose restricted personal information, confidential sources or hidden case truth. Credentials and secrets never appear in source, narrative records or logs.

## 24. Records, persistence and reporting

BP-38 owns identifiers, schema and provenance; BP-39 owns persistence, backups and recovery; BP-41 owns reporting/notification delivery. BP-30 records source references and domain accountability without inventing competing record standards.

Historical policy, officeholder, authority, order and decision versions must be queryable as of any simulation time. Corrections append a new event and preserve the original. Recovery must not replay an already completed appointment, order or approval.

Reports distinguish draft from approved policy, authority from title, order issuance from execution, complaint receipt from finding, recommendation from binding direction and institutional response from completed remedy. Every report states its as-of simulation time, scope, source versions, access class and uncertainty.

## 25. Cross-system effects

- **BP-01/BP-02/BP-44:** all governance operates within immutable Saltwater canon and approved change control.
- **BP-03/BP-04:** people and institutions use canonical identities; no duplicate registries.
- **BP-05/BP-06/BP-07:** police structure, personnel and career authorities remain separate; BP-30 does not redefine ranks or service rules.
- **BP-08/BP-12:** operational orders/delegations are consumed by units and incident command; operational records remain authoritative there.
- **BP-31:** misconduct and complaint investigations/findings are owned by professional standards; BP-30 provides institutional oversight and response.
- **BP-32/BP-33:** qualification and employment data remain with training/HR owners.
- **BP-34:** public/police budgets, procurement transactions and accounts remain authoritative there.
- **BP-38/BP-39/BP-42:** records, persistence and security are shared infrastructure owners.
- **BP-41:** public reporting and notification delivery use reporting interfaces.
- **BP-35/BP-36:** public trust and social consequences arise from event-driven causal models, not arbitrary governance scripts.

## 26. Exceptions and edge cases

1. Institution has no valid mandate or constitutional basis.
2. Institution identity exists but its premises/provider record is missing.
3. Office is vacant, incumbent deceased, departed or unavailable.
4. Appointment is disputed, expired, revoked or not yet effective.
5. Acting appointment exceeds scope or term.
6. Two offices or duties are incompatible.
7. Succession rule is absent or produces no eligible successor.
8. Delegator lacks authority or attempts excessive sub-delegation.
9. Delegation has conflicting scope or overlapping effective dates.
10. Order is issued by an unauthorised actor.
11. Order has conflicting recipients, scope or effective time.
12. Order is received but not acknowledged or executed.
13. Policy conflicts with higher authority or fixed canon.
14. Draft policy is mistakenly treated as effective.
15. Policy change attempts retroactive alteration.
16. Emergency power lacks a trigger, expiry or review.
17. Emergency declaration attempts to exceed jurisdiction or population cap.
18. Decision approver has a conflict of interest.
19. Procurement approval lacks budget authority or transaction reference.
20. Public complaint is misrouted or has no owner.
21. Complaint subject controls its own review.
22. Complaint is referred but falsely marked resolved.
23. Oversight reviewer lacks independence or access authority.
24. Finding is confused with recommendation or remedy.
25. Institution fails to implement a recommendation.
26. Public report contains restricted or unverified material.
27. Trust indicator changes without a causal source event.
28. Police command instruction conflicts with operational command or policy.
29. Strategic direction attempts to rewrite a live incident record.
30. Command order changes an officer's personnel or career record without owner authority.
31. Police headcount or officeholder record duplicates a person.
32. Population cap would be exceeded by an appointment or new official.
33. Institutional reorganisation leaves pending cases, assets or obligations unassigned.
34. Interagency agreement grants powers or access beyond a party's authority.
35. External reference is mistakenly treated as a new playable jurisdiction.
36. NPC official acts on hidden or unauthorised information.
37. AI-generated proposal is mistaken for binding decision.
38. Clock advances while paused or absent.
39. Duplicate event replay or partial persistence failure.
40. Governance record conflicts with BP-38/BP-39/BP-42 authoritative infrastructure.

Every exception preserves the attempted action, actor, authority, time, affected record, source version, conflict and resolution. The system must not silently invent an authority or choose a convenient institutional outcome.

## 27. Configuration and unresolved fictional policy

BP-44 governs the versioned fictional configuration. The following remain open and must not be guessed:

1. Exact executive, legislative, administrative and oversight institutional catalogue.
2. Constitutional offices, appointment methods, term lengths and succession.
3. Police governance board/commission model, if any.
4. Police chief and command appointment/tenure interface with BP-07.
5. Strategic order categories, approval matrix and emergency powers.
6. Policy categories, approval routes, consultation and review intervals.
7. Command delegation levels, sub-delegation and revocation.
8. Public complaint channels and independent oversight structure.
9. Conflict-of-interest declarations, recusal and reviewer independence standards.
10. Public accountability hearing and publication rules.
11. Government procurement approval thresholds (financial execution remains BP-34).
12. Permit, licensing and inspection authority catalogue.
13. Public-service governance and institutional performance measures.
14. Interagency agreement catalogue and data-sharing limits.
15. Public trust measures and causal weights (implementation belongs BP-35/BP-36).
16. Institutional reorganisation and dissolution rules.
17. Emergency governance continuity and succession.
18. Public record publication and confidentiality categories.
19. NPC official autonomy and governance workload.
20. Retention and review policy in coordination with BP-38/BP-39.

Where authority is unresolved, action remains pending/blocked and is referred to the configured competent decision route. No real-world constitution, police commission, ministerial system or public-law doctrine is silently imported.

## 28. Acceptance tests

These are criteria for BP-43. They are not evidence that implementation or testing has occurred.

- GOV-AT-001 — Every public institution has a stable institutional ID and canonical BP-04 organisation reference.
- GOV-AT-002 — Every governing office has a defined mandate, jurisdiction and accountable incumbent or vacancy state.
- GOV-AT-003 — Every officeholder resolves to one canonical BP-03 person identity.
- GOV-AT-004 — An office title alone does not grant powers outside its recorded mandate.
- GOV-AT-005 — Constitutional and sovereign authority derives from approved BP-01 canon and versioned BP-44 configuration.
- GOV-AT-006 — No institution exercises undefined or unassigned authority.
- GOV-AT-007 — Every public body has an explicit parent, independence status or constitutional basis.
- GOV-AT-008 — Public executive, legislative, administrative and oversight functions are represented distinctly.
- GOV-AT-009 — Separation of functions is enforced by authority rules, not merely labels.
- GOV-AT-010 — An office may be vacant without deleting the office or its institutional history.
- GOV-AT-011 — Acting appointments have explicit scope, start, end, authority and limits.
- GOV-AT-012 — Succession follows configured authority and records the triggering event.
- GOV-AT-013 — An incumbent cannot hold incompatible offices unless an explicit exception authorises it.
- GOV-AT-014 — Appointment, confirmation, suspension, resignation and removal are distinct events.
- GOV-AT-015 — Every appointment records appointing authority, effective date and term where applicable.
- GOV-AT-016 — Every material institutional decision has an accountable decision-maker.
- GOV-AT-017 — Every material decision records authority, rationale, evidence/material considered and outcome.
- GOV-AT-018 — Every decision records its effective simulation time and configuration version.
- GOV-AT-019 — Every order has an issuer, recipient/scope, authority, issue time and status.
- GOV-AT-020 — An order outside the issuer's authority is rejected or held pending review.
- GOV-AT-021 — Orders distinguish draft, approved, issued, acknowledged, effective, superseded, revoked and completed.
- GOV-AT-022 — Receipt of an order does not prove execution.
- GOV-AT-023 — Execution reports do not rewrite the original order.
- GOV-AT-024 — Orders can be amended only through a new attributable version.
- GOV-AT-025 — Conflicting orders are detected and escalated without silent precedence assumptions.
- GOV-AT-026 — Emergency powers are explicitly configured, bounded, time-limited and reviewable.
- GOV-AT-027 — Emergency declaration does not suspend the 10,000-person cap or one-city canon.
- GOV-AT-028 — Emergency action records triggering facts, authority, scope, duration and review.
- GOV-AT-029 — Emergency powers expire or are renewed only through explicit configured authority.
- GOV-AT-030 — Public policy has stable identity, owner, approval authority, effective date and version.
- GOV-AT-031 — Policy drafts are distinct from approved and effective policy.
- GOV-AT-032 — Policy changes preserve prior versions and effective intervals.
- GOV-AT-033 — Policy cannot retroactively change historical authority unless explicit legal/configuration rule allows it.
- GOV-AT-034 — Policy dissemination records target roles, channels, delivery and acknowledgement where required.
- GOV-AT-035 — Policy exceptions record applicant, authority, scope, rationale and duration.
- GOV-AT-036 — Policy interpretation does not silently amend policy text.
- GOV-AT-037 — Operational procedures remain owned by relevant divisions while BP-30 owns governance approval/delegation where assigned.
- GOV-AT-038 — Police mandate is consistent with sovereign canon and fixed jurisdiction.
- GOV-AT-039 — Police command hierarchy references BP-05 authoritative organisational structure.
- GOV-AT-040 — Rank, grade, position, appointment, authority, powers, clearance and qualification remain separate concepts.
- GOV-AT-041 — BP-30 does not create a duplicate officer personnel master.
- GOV-AT-042 — Every officer resolves to one BP-06 personnel record.
- GOV-AT-043 — Police command delegations identify delegator, delegate, scope, exclusions and validity interval.
- GOV-AT-044 — Delegated authority cannot exceed the delegator's own authority.
- GOV-AT-045 — Delegation does not transfer accountability unless explicit configuration says so.
- GOV-AT-046 — Revocation of delegation is effective-dated and historically preserved.
- GOV-AT-047 — Acting command arrangements are explicit and do not silently promote rank.
- GOV-AT-048 — Command succession is deterministic under approved policy and records each step.
- GOV-AT-049 — Command vacancies and unavailable commanders have defined escalation routes.
- GOV-AT-050 — Police policy approval is distinct from operational command execution.
- GOV-AT-051 — BP-08 owns unit establishment and deployment implementation.
- GOV-AT-052 — BP-12 owns incident command execution and operational incident records.
- GOV-AT-053 — BP-30 may issue strategic direction but cannot overwrite operational incident chronology.
- GOV-AT-054 — Operational commanders retain only authority delegated by BP-05/BP-30 and applicable policy.
- GOV-AT-055 — Every operational plan approved under governance has scope, owner, version and review trigger.
- GOV-AT-056 — Briefings record author, recipients, content/version and acknowledgement where required.
- GOV-AT-057 — Material instructions record who authorised, issued, received and executed them.
- GOV-AT-058 — Command decisions preserve rationale and contemporaneous information.
- GOV-AT-059 — Command decisions can be reviewed without altering their original event record.
- GOV-AT-060 — Police staffing baseline is approximately 500 individually recorded personnel, subject to approved establishment and cap.
- GOV-AT-061 — Police personnel are included within the total 10,000 living-person cap, never added outside it.
- GOV-AT-062 — Police population totals reconcile with BP-03 person records.
- GOV-AT-063 — Vacant posts are not counted as people.
- GOV-AT-064 — Recruitment and appointment do not exceed available population capacity.
- GOV-AT-065 — Command structures cannot imply more officers than canonical personnel records.
- GOV-AT-066 — Public procurement governance defines authority and approval boundaries but BP-34 owns financial accounting and transactions.
- GOV-AT-067 — Budget authority and posted financial transactions remain owned by BP-34.
- GOV-AT-068 — BP-30 cannot create a parallel public finance ledger.
- GOV-AT-069 — Public expenditure approvals reference authorised budgets and BP-34 transaction records.
- GOV-AT-070 — Public asset ownership and premises identity remain with BP-04 and resource owners.
- GOV-AT-071 — Government permits and licensing decisions have an identified competent authority.
- GOV-AT-072 — Permit application, review, decision, issuance, variation, suspension and revocation are separate states.
- GOV-AT-073 — Inspection authority and scope are explicit and auditable.
- GOV-AT-074 — Inspection observations are distinct from findings and enforcement decisions.
- GOV-AT-075 — Public complaint receipt is distinct from complaint investigation and outcome.
- GOV-AT-076 — BP-31 owns complaint/misconduct case lifecycle and investigative findings where specified.
- GOV-AT-077 — BP-30 owns institutional oversight, governance response and accountability follow-through.
- GOV-AT-078 — BP-41 owns reporting and publication delivery interfaces.
- GOV-AT-079 — BP-38 owns authoritative record/version/provenance standards.
- GOV-AT-080 — BP-42 enforces access control and protected-information boundaries.
- GOV-AT-081 — Every public complaint has a route, owner, status and outcome or pending reason.
- GOV-AT-082 — Complaints can be referred to an independent or external review body where configured.
- GOV-AT-083 — Conflicts of interest are identified and managed before assignment or decision.
- GOV-AT-084 — A complaint about an officeholder is not decided solely by that same officeholder.
- GOV-AT-085 — Complainant identity and protected information are access restricted.
- GOV-AT-086 — Complaint receipt acknowledgement is distinct from substantive resolution.
- GOV-AT-087 — Investigation findings are attributed to BP-31 or other competent owner.
- GOV-AT-088 — Governance response to findings records accepted, disputed or partially accepted status.
- GOV-AT-089 — Remedies have an owner, action, due simulation time and completion evidence.
- GOV-AT-090 — Public trust effects arise from recorded events and configured causal rules, not arbitrary narrative.
- GOV-AT-091 — Public trust indicators do not reveal hidden case truth or restricted complaint details.
- GOV-AT-092 — Published outcomes are approved, appropriately redacted and traceable to source records.
- GOV-AT-093 — An unresolved complaint remains visibly unresolved rather than receiving fabricated closure.
- GOV-AT-094 — Independent oversight cannot access records beyond its configured authority.
- GOV-AT-095 — Oversight review records scope, reviewer, independence/conflict check, source set and conclusions.
- GOV-AT-096 — Inspection and audit findings distinguish observation, inference, substantiated finding and recommendation.
- GOV-AT-097 — Recommendations are distinct from binding orders.
- GOV-AT-098 — Implementation of a recommendation is tracked by the responsible institution.
- GOV-AT-099 — Failure to implement a recommendation is recorded and escalated under configured rules.
- GOV-AT-100 — Public administration actions have accountable actors, authority and dates.
- GOV-AT-101 — Administrative records identify the responsible office and decision chain.
- GOV-AT-102 — Public service governance defines mandate and accountability without deeply simulating every provider.
- GOV-AT-103 — BP-04 owns provider identities and premises for social care and welfare services.
- GOV-AT-104 — BP-17 owns victim/witness support interactions and safeguarding records.
- GOV-AT-105 — BP-36 owns social relationships and community context.
- GOV-AT-106 — BP-30 governs public-service mandate, oversight and institutional accountability only.
- GOV-AT-107 — Service referral does not prove service delivery or outcome.
- GOV-AT-108 — Service performance reporting uses source records and preserves uncertainty.
- GOV-AT-109 — Public service failure or disruption is recorded with responsible owner and review route.
- GOV-AT-110 — Emergency service agency mandates and institutional identities are explicit.
- GOV-AT-111 — BP-04 represents emergency-service agencies; BP-11/BP-12 own dispatch and incident coordination.
- GOV-AT-112 — BP-30 does not duplicate emergency dispatch, operational response or incident command systems.
- GOV-AT-113 — Interagency agreements define purpose, authority, scope, contact and review.
- GOV-AT-114 — Interagency coordination records do not grant unrestricted cross-agency data access.
- GOV-AT-115 — Public institutions operate within Saltwater's one-city sovereign jurisdiction.
- GOV-AT-116 — An off-map reference does not create an additional playable city or jurisdiction.
- GOV-AT-117 — Public offices, institutions and agencies do not cause population to exceed 10,000.
- GOV-AT-118 — Every living officeholder or employee is counted once by BP-03 regardless of offices held.
- GOV-AT-119 — At least 10,000 businesses remain part of the fixed canon and are not altered by governance design.
- GOV-AT-120 — Governance does not expand into a full national or global government simulator.
- GOV-AT-121 — All time-dependent appointments, orders, policies and terms use BP-37 canonical simulation time.
- GOV-AT-122 — No appointment, order, policy deadline or oversight process progresses while paused or absent.
- GOV-AT-123 — No NPC official performs background governance activity while simulation time is frozen.
- GOV-AT-124 — On resume, no wall-clock elapsed time is applied to institutional decisions or deadlines.
- GOV-AT-125 — NPC officials know only observed, received or authorised information.
- GOV-AT-126 — Officials cannot access BP-14 hidden crime-generation truth through governance systems.
- GOV-AT-127 — No governance record, dialogue or report reveals hidden culprit/accomplice identity before exact bingo.
- GOV-AT-128 — No unsolicited investigative hints or next-step directions are generated.
- GOV-AT-129 — Governance action cannot be used to force a case outcome or predetermine guilt.
- GOV-AT-130 — AI-generated policy summaries cannot replace authoritative policy versions.
- GOV-AT-131 — AI cannot issue binding orders, appoint officials, remove officers or approve expenditure without explicit authorised workflow.
- GOV-AT-132 — AI cannot invent constitutional powers or legal authorities.
- GOV-AT-133 — AI recommendations are labelled as recommendations and identify source records.
- GOV-AT-134 — Text-only interface supports all essential governance workflows.
- GOV-AT-135 — Optional maps/graphics never contain exclusive authority or decision facts.
- GOV-AT-136 — Every read/export of restricted governance material is permission checked and audited.
- GOV-AT-137 — Every material change records actor, authority, purpose, canonical time and source version.
- GOV-AT-138 — Corrections preserve original values and append reasoned, attributable events.
- GOV-AT-139 — Duplicate event replay does not create duplicate appointments, orders, approvals or complaint outcomes.
- GOV-AT-140 — Partial persistence failure preserves completed steps and explicit incomplete status.
- GOV-AT-141 — BP-39 recovery preserves institutional and command histories without duplicate actions.
- GOV-AT-142 — Governance records use BP-38 identifiers and schemas; no conflicting local identity system.
- GOV-AT-143 — Financial, population, staffing, resource and capacity changes reconcile atomically under X04.
- GOV-AT-144 — Every officer has one authoritative personnel record and valid command/position relationships.
- GOV-AT-145 — Every official action has an authorised actor and traceable record.
- GOV-AT-146 — Material command decisions have authority, rationale and audit trail.
- GOV-AT-147 — Every complaint has a route, owner, status and outcome or pending reason.
- GOV-AT-148 — All BP-30 mapped source requirements and tests are traceable to this specification.
- GOV-AT-149 — No BP-30 rule silently takes ownership from BP-31, BP-34, BP-38 or BP-42.
- GOV-AT-150 — No Neon schema, seed, import or bulk write is authorised by this specification.

## 29. Source traceability

Original source remains `docs/governance/SALTWATER_MASTER_BLUEPRINT.json`, SHA `a882c4fc17f5654268a9b6d5823f5b9a4f3f1ade`. The IDs below are the exact requirements and tests mapped to BP-30 in the 52→44 crosswalk.

| Source ID | Source requirement/test | BP-30 coverage |
|---|---|---|
| S01.R01 | Define Saltwater sovereign status, territory boundary, jurisdiction, institutions, powers, succession and constitutional rules. | Sections 2, 5–7, 17, 25–27; BP-01 owns canon, BP-02 geography, BP-30 institutional authority and succession. |
| S01.R02 | Define legal hierarchy, authority sources, emergency powers, separation of functions and jurisdictional limits. | Sections 7–8, 10, 17, 25–27; authority/delegation, emergency powers, separation and bounded jurisdiction; BP-27 owns legal process. |
| S01.T02 | No institution exercises undefined authority. | Sections 5–7, 10, 26 and tests GOV-AT-001–027; authority validation is mandatory. |
| S11.R01 | Define executive, legislative, administrative and oversight functions, offices, incumbents, mandates, decision processes and records. | Sections 5–7, 11, 17–20; institutional, office, authority and decision models. |
| S11.R02 | Represent public policy, procurement, permits, licensing, inspections and public complaints. | Sections 10, 12–14; governance approval/mandate boundaries, with financial and complaint case ownership retained by BP-34/BP-31. |
| S11.R03 | Ensure government actions have accountable actors, authority and dates. | Sections 7, 9, 11, 20–24; all material actions are attributable and effective-dated. |
| S11.T01 | Every official action has an authorised actor and traceable record. | Sections 7, 9, 11, 20, 23–24 and tests GOV-AT-016–025, GOV-AT-124–140. |
| S15.R01 | Represent social care, welfare and community support governance. | Sections 12, 18, 25; BP-04 owns providers, BP-17 support interactions, BP-30 public-service governance. |
| S15.R02 | Maintain accountable public-service support and records. | Sections 12, 14, 18, 23–25; BP-30 oversight and accountability, BP-38 record provenance. |
| S15.T01 | Public-service records have accountable ownership and traceable routes. | Sections 12, 14, 20, 23–24 and tests GOV-AT-091–105. |
| S23.R01 | Define police mandate, command hierarchy, rank/grade/position/authority/powers/clearance, divisions, units and reporting lines as distinct concepts. | Sections 4, 7–9, 18, 25; BP-05 owns structural taxonomy, BP-30 policy and delegation. |
| S23.R03 | Define appointment, promotion, transfer, acting roles, succession, discipline, grievance, standards and retirement rules. | Sections 6–8, 14, 17, 25; BP-07/BP-31/BP-32/BP-33 own execution of their respective processes. |
| S26.R01 | Represent orders, policies, briefings, operational plans, supervision, approvals, audits, complaints, misconduct and review. | Sections 8–15, 20, 25; BP-30 governance ownership, operational and misconduct records remain with their owners. |
| S26.R02 | Record who authorised, issued, received and executed every material instruction. | Sections 7, 9, 11, 20, 23–24; explicit authority, acknowledgement and execution contracts. |
| S26.R03 | Support fair internal process and traceable decisions. | Sections 11, 14–15, 20, 23–24; due process, conflicts, recusal and immutable provenance. |
| S26.T01 | Material command decisions have authority, rationale and audit trail. | Sections 8–11, 20, 23–24 and tests GOV-AT-016–027, GOV-AT-048–060, GOV-AT-124–140. |
| S40.R01 | Represent public complaints, independent review, internal investigations, inspections, findings, remedies and published outcomes. | Sections 14–15, 20, 23–25; BP-31 owns complaint/misconduct case lifecycle, BP-30 institutional oversight, BP-41 publication. |
| S40.R02 | Preserve due process, conflicts of interest and auditability. | Sections 14–15, 20, 23–24; conflict checks, recusal, independence and audit. |
| S40.R03 | Allow institutional failure and public trust to evolve from events. | Sections 14, 22, 25; BP-35/BP-36 own causal trust consequences; governance records failures and responses. |
| S40.T01 | Every complaint has a route, owner, status and outcome or pending reason. | Sections 14, 20, 23–24 and tests GOV-AT-076–090. |
| C07 | Approximately 500 individually persistent police personnel within the population cap. | Sections 2, 8, 18, 25 and tests GOV-AT-057–062, GOV-AT-112–115; police headcount remains within BP-03's 10,000 total. |
| S10.R01 | Define currency, public revenue, taxation, fees, expenditure, budgets, debt, grants and financial periods. | Section 13; BP-30 defines approval authority only; BP-34 owns the financial model, accounts and transactions. |
| S12.R01 | Maintain civil status, identity, address, property, business, permits and other canonically required registers. | Sections 12, 18, 23–25; BP-03/BP-04/BP-38 own registers and source records; BP-30 defines institutional authority for public administration. |
| S21.R01 | Represent media outlets, public communications, events, venues, sports, cultural organisations and community gatherings. | Sections 12, 14, 16 and 25; BP-04 owns organisations/venues, BP-36 civic context; BP-30 governs public institutional mandates and accountability. |
| S21.R03 | Keep civic organisations and public-facing institutions distinct and appropriately scoped. | Sections 5, 12, 16–17 and 25; canonical organisations remain BP-04 records with explicit institutional mandate and governance links. |
| S22.R01 | Define emergency services and civil protection agencies, response and mutual aid within canon. | Sections 5, 12, 16 and 25; BP-04 owns agency identity, BP-11/BP-12 own dispatch/incident coordination, BP-30 defines public mandate and interagency governance. |
| S23.R04 | Keep the police service alive, internally coherent and operationally functional. | Sections 8–9, 18, 20, 22 and 25; BP-30 governs policy/delegation while BP-05–BP-12 own structure, personnel and operational execution. |
| S28.R01 | Simulate patrol presence, beat coverage, response, scene arrival, public contact and field decisions. | Sections 8–9 and 25; BP-30 defines strategic authority and policy; BP-08/BP-10/BP-12 own field execution and records. |
| S30.R01 | Create stable case IDs, ownership, classification, status, objectives, actions, decisions, reviews, deadlines and closure reasons. | Sections 8, 14, 18 and 25; BP-15/BP-16 own case and investigative command lifecycle; BP-30 has governance-level oversight only. |
| S48.R01 | Define user/player/officer/administrator/system roles, least privilege, secret handling, access checks and audit logs. | Sections 4, 14–16, 22–24 and 25; BP-42 owns enforcement; BP-30 defines domain governance scopes and independence requirements. |

Cross-cutting controls:
- X03: all governance effective dates and deadlines use BP-37 canonical time and freeze while paused/absent.
- X04: population, staffing, finance, resources and capacity reconcile atomically.
- X05: allegation, inference, intelligence, recommendation, official finding and adjudicated outcome remain distinct.
- X06: original records and decisions are preserved; corrections are additive and attributable.
- Global canon: one Saltwater city/jurisdiction; 10,000 living-person cap; at least 10,000 businesses; police-depth priority; permanent person promotion; text-first completeness; exact `bingo` firewall; no offline progression; no Neon writes without explicit approval.

All 30 mapped source requirement/test/canon IDs are explicitly traced. The original source JSON and crosswalk are not modified by this specification.

## 30. Risk register

| Risk | Control |
|---|---|
| Institution acts outside mandate | Explicit authority matrix and validation |
| Title confused with authority | Office mandate and effective delegation |
| Acting role treated as permanent appointment | Separate acting status and appointment record |
| Strategic order confused with operational execution | Separate BP-30 order and operational owner acknowledgement |
| Policy draft treated as binding | Explicit approval/effective lifecycle |
| Governance duplicates police personnel records | BP-06 authoritative personnel master |
| Complaint subject controls investigation | BP-31 ownership and conflict/recusal rules |
| Recommendation treated as binding order | Explicit distinction and authority validation |
| Financial approvals bypass budget | BP-34 validation and transaction ownership |
| Emergency power becomes unlimited | Trigger, scope, duration and review |
| Institutional reorganisation erases history | Predecessor/successor references and append-only history |
| Public reporting leaks restricted information | BP-41 publication workflow and BP-42 access controls |
| Trust changes arbitrarily | BP-35/BP-36 event-driven causality |
| NPCs progress while player absent | BP-37 pause invariant |
| Hidden case truth leaks through governance | BP-14 firewall and exact bingo gate |

## 31. Design completion checklist

- [ ] Public institutional architecture and mandates defined.
- [ ] Office, incumbency, appointment and succession interfaces defined.
- [ ] Authority, delegation, separation and emergency powers defined.
- [ ] Police governance and command policy boundaries defined.
- [ ] Order, policy, briefing and decision lifecycles defined.
- [ ] Public administration and procurement authority boundaries defined.
- [ ] Complaint routing, oversight, independence and remedies defined.
- [ ] Conflict-of-interest and recusal controls defined.
- [ ] Interagency agreement and institutional reorganisation defined.
- [ ] BP-31/BP-34/BP-38/BP-42 ownership boundaries preserved.
- [ ] Time freeze, NPC knowledge and player agency defined.
- [ ] 10,000 population cap, 500 police baseline and 10,000-business canon preserved.
- [ ] All 150 acceptance tests await BP-43 execution.
- [ ] All 21 mapped source IDs traced.
- [ ] Fictional policy decisions remain explicit.
- [ ] No Neon schema, seed, import or bulk write made or authorised.

## 32. Status and next dependencies

This is a design draft, not approved fictional law, implemented functionality or executed test evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-31 — Professional Standards**. BP-30 owns institutional governance and oversight architecture; BP-31 owns professional standards, complaint/misconduct case lifecycle, investigation, findings and disciplinary process.
