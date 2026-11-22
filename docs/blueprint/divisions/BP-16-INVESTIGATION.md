# BP-16 — Investigation

**Project:** Saltwater  
**Blueprint structure:** Fixed BP-01–BP-44  
**Division:** BP-16  
**Specification version:** 1.0-draft  
**Design status:** DESIGNED_DRAFT  
**Implementation status:** NOT_STARTED  
**Test execution status:** NOT_STARTED  
**Verification status:** NOT_STARTED  
**Authority:** Saltwater master blueprint, 52→44 crosswalk v1.2, source JSON (unchanged)  
**Scope boundary:** Investigation work performed within a case; not case identity/lifecycle, incident dispatch, source-domain evidence production, legal process or hidden occurrence truth.

---

## 1. Purpose and intended outcome

BP-16 defines the complete investigative-work system through which authorised investigators and the player conduct, coordinate, record, review and conclude investigative activity associated with one or more cases.

It must support investigations that are complex, open-ended, uncertain, multi-person, multi-scene, multi-source, concurrent and long-running. It must allow a case to have no identified suspect, many possible lines of enquiry, conflicting accounts, incomplete records, dead ends, mistaken assumptions, exculpatory material, changing priorities and more than one investigative team. It must not force a predetermined route to a solution.

The system records what investigators decide and do, what information they had at the time, what they requested, what they received, what they concluded, what remains unresolved and who is accountable. It does not decide the truth for the player, silently complete work, manufacture investigative success or reveal hidden generated facts.

The primary outcome is a persistent, auditable, navigable record of investigative activity that preserves the distinction between:
- an occurrence and a report of an occurrence;
- an allegation and an established fact;
- a lead and evidence;
- intelligence and evidence;
- an investigative hypothesis and a conclusion;
- a source record and a summary of that record;
- a forensic result and an investigator's interpretation;
- a suspect role and guilt;
- an investigative conclusion and a court finding.

Investigation is player-directed. Available records, documents, evidence, people, requests and results may be made accessible through the interface, but the system must not tell the player what to investigate next, rank leads in a way that reveals the solution, or provide unsolicited solution hints.

## 2. Scope

### 2.1 BP-16 owns

1. Investigation records and their relationship to BP-15 cases.
2. Investigative workstreams, teams and task groups.
3. Investigative objectives and plans.
4. Lines of enquiry and leads as investigative work objects.
5. Hypotheses, alternative explanations and disconfirming propositions.
6. Investigative tasks, requests, assignments, dependencies and completion records.
7. Investigative actions and decision records.
8. Investigator ownership, collaboration, handover and review of investigative work.
9. Tracking requests to other specialist domains and linking returned records.
10. Progress, blockers, unresolved issues and investigative status summaries.
11. Investigative chronology references and links to source events.
12. Investigative quality review, supervisory review and decision audit.
13. Investigative referrals, inter-case investigative coordination and shared-work boundaries.
14. Recording why a line was opened, pursued, paused, exhausted, rejected, reopened or closed.
15. Investigator-facing presentation of the material and actions that the player is authorised to access, without revealing hidden truth.

### 2.2 Explicit exclusions and ownership boundaries

| Domain | Authoritative owner | BP-16 relationship |
|---|---|---|
| Case ID, case lifecycle, case assignment at case level, case closure/reopening, case-level chronology and related-case links | BP-15 | References the case; creates investigative work within it; requests case-level changes through BP-15 contracts. |
| Operational incident, CAD, dispatch, response chronology | BP-12 | Receives incident references and operational records; does not rewrite incident records. |
| Crime/offence taxonomy and classification | BP-13 | Consumes classifications; may record a proposed reclassification request but cannot redefine taxonomy. |
| Hidden occurrence truth, perpetrator identity, accomplices, generator-side causal facts | BP-14 | Must never query or expose protected truth in player-facing investigation paths. |
| Person identity and life record | BP-03 | References stable person IDs; never creates duplicate identities. |
| Victim/witness roles and participant-specific status | BP-17 | References role records and requests authorised participant actions. |
| Suspect/offender role and status semantics | BP-18 | References role records; never equates suspicion with guilt. |
| Interview process, recordings, notes, questions, answers and statement versions | BP-19 | Requests/coordinates interviews and links authoritative interview records. |
| Surveillance authorisation, coverage, collection, retrieval and source records | BP-20 | Requests/coordinates surveillance and links authoritative surveillance records. |
| Intelligence source grading, confidence, handling and dissemination | BP-21 | May consume or request intelligence products; does not own their lifecycle or convert intelligence into evidence. |
| Scene boundaries, scene entry, search and scene processing | BP-22 | Requests/coordinates scene work and links scene records. |
| Exhibit identity, recovery record, packaging, seals, transfers, continuity and current status | BP-23 | Requests/coordinates evidence actions and links exhibits; cannot alter continuity. |
| Forensic submissions, methods, raw results, limitations and expert interpretation | BP-24 | Requests/coordinates examinations and links authoritative reports. |
| Arrest, search, warrant authority and execution | BP-25 | May prepare an investigative request/referral; cannot authorise or execute those powers. |
| Custody lifecycle | BP-26 | Consumes custody events as authorised. |
| Prosecution, disclosure and legal workflow | BP-27 | Supplies investigative records through controlled interfaces; does not own disclosure determinations. |
| Court hearings, rulings, verdicts and outcomes | BP-28 | Consumes outcomes; does not rewrite investigative history. |
| Department command, policy and delegation | BP-30 | Receives command direction; does not create institutional authority. |
| Professional standards and misconduct case lifecycle | BP-31 | May provide referrals and preserve relevant records; does not adjudicate misconduct. |
| Simulation time and scheduling | BP-37 | Uses the canonical in-world time; cannot advance time itself. |
| Authoritative records, schema, provenance and audit standards | BP-38 | Persists domain records under BP-38 rules. |
| Persistence, backup and recovery | BP-39 | Uses persistence contracts; no independent shadow store. |
| Interface and presentation | BP-40 | Supplies text-first investigative workflows; BP-16 defines domain actions/data. |
| Notifications and reporting | BP-41 | Emits authorised progress/report events; does not redefine investigative state. |
| Access control and information boundaries | BP-42 | Enforces domain permissions and hidden-truth protection. |
| Testing and quality assurance | BP-43 | Provides requirements and acceptance evidence targets. |
| Configuration and change control | BP-44 | Governs approved changes to investigation policy/configuration. |

A handoff does not transfer ownership of the source record. A reference is not a copy unless an authorised immutable snapshot is explicitly required. A downstream summary must preserve source identity, version, timestamp, author and limitations.

## 3. Governing invariants

1. **Player agency:** the player chooses investigative actions. No mandatory sequence, automatic case-solving or forced lead progression.
2. **No unsolicited guidance:** do not suggest what to investigate next, identify a likely culprit, highlight a hidden decisive clue, or provide solution-shaped nudges.
3. **Exact reveal gate:** no perpetrator, culprit or accomplice identity, including indirect confirmation, is revealed unless the player enters exactly `bingo`. Case output, reports, notifications, summaries, NPC dialogue, error messages, debug output and visualisations are all subject to this gate.
4. **No hidden-truth contamination:** investigative records and NPC knowledge may contain only information plausibly observed, received, derived or authorised. BP-14 generator truth is not a permissible investigative input.
5. **No guilt by role:** lead, witness, victim, person of interest, suspect, arrest, charge or generated role is not proof of guilt.
6. **No evidence inflation:** leads, intelligence, hypotheses, allegations and unverified reports do not become evidence or facts by changing status or being copied.
7. **Source integrity:** BP-16 references authoritative source records; it never silently edits, overwrites or upgrades them.
8. **Historical integrity:** investigative actions, decisions and state transitions are append-only or versioned. Corrections supersede; they do not erase history.
9. **Attribution:** every material action, decision, assignment, status transition and review has an actor/system identity, canonical time, authority basis and reason.
10. **Population integrity:** any materially case-connected person is promoted to persistent full-detail status through BP-03 and is never downgraded; the 10,000 living-person cap remains absolute.
11. **Time freeze:** no investigative task, NPC activity, deadline, automated analysis, background process or scheduled action advances while the player is outside the simulation. No hidden elapsed time on resume.
12. **Single-city canon:** investigation geography is limited to Saltwater. External places may appear only as off-map references or contextual records and do not create playable territory.
13. **Text completeness:** every essential investigative action and result is available in text. Maps, diagrams, timelines and forensic visuals are optional and derived from canonical records.
14. **No assumed success:** task completion records the outcome actually returned, including failure, inconclusive result, refusal, no record, unavailable source or partial completion.
15. **Uncertainty is explicit:** unknown, disputed, estimated, inferred, unverified, contradictory and time-uncertain information remain labelled as such.
16. **No silent authority:** task assignment or a supervisory title does not automatically confer legal powers, clearance or access outside the relevant BP-05/BP-30/BP-42 rules.
17. **No forced closure:** investigative work may remain open, dormant, blocked, exhausted or unresolved even if the case lifecycle changes under BP-15.
18. **No structural drift:** this specification does not add, remove, reorder, split, merge or rename any BP division.

## 4. Core entities and records

All identifiers are stable, opaque, non-semantic IDs generated under BP-38 conventions. Human-readable references are display labels, not primary keys. The exact physical schema is owned by BP-38 and is not prescribed here.

### 4.1 Investigation

One case may have one or more investigation records where approved case-management policy requires distinct investigative mandates or workstreams. An investigation belongs to exactly one BP-15 case. It may reference several incidents and related cases but cannot change their ownership.

Required attributes:
- investigation_id;
- case_id;
- title/short description;
- purpose and authorised scope;
- investigation type/category where configured;
- status and status history;
- accountable lead investigator;
- supervisory owner where applicable;
- opening actor, canonical time and reason;
- current team/workstream references;
- priority and priority rationale;
- current review state and next review condition (not a running timer);
- restrictions/classification/access policy reference;
- linked incident, person, business, property, location and source-record references;
- unresolved issues and closure/transfer rationale;
- provenance and version metadata.

Investigation status is distinct from case status. A case may be open while a workstream is dormant; a case may be closed while records remain retained and read-only; reopening a case is BP-15 authority and may trigger a new or resumed investigation by explicit action.

### 4.2 Workstream

A workstream is a bounded body of investigative work under an investigation, such as a defined subject area, event sequence, location, evidence family, participant group or analytical question. The label must not reveal hidden truth.

Required attributes:
- workstream_id and investigation_id;
- neutral title and scope statement;
- accountable owner and participating members;
- status and status history;
- linked objectives, leads, tasks, requests and decisions;
- dependencies and blockers;
- access restrictions;
- opening/closing rationale and provenance.

Workstreams may overlap. Overlap must be explicit and must not create duplicate source records or competing ownership.

### 4.3 Investigative objective

An objective states a question or outcome the authorised investigator chooses to address. It is not a hint generated by the system.

Attributes: objective_id, investigation_id, workstream_id (optional), statement, rationale, author, created_at, status, success/closure criteria, linked tasks/leads/decisions, review history and provenance.

Objectives may be broad, narrow, provisional, revised, suspended, completed, abandoned or unresolved. A completed objective does not prove a hypothesis.

### 4.4 Lead / line of enquiry

A lead is a recorded avenue of enquiry arising from an identified source, observation, report, information item or investigator decision. A lead is a work object, not proof.

Attributes:
- lead_id;
- investigation_id and optional workstream_id;
- neutral title and factual description;
- source reference(s) and exact source version(s);
- originator and recorded time;
- basis for relevance;
- known uncertainty, contradiction or limitation;
- owner;
- priority selected by authorised human actor, with reason;
- status and full status history;
- linked objectives, tasks, requests, hypotheses and decisions;
- disposition and rationale;
- access classification and provenance.

Permitted dispositions include: unassessed, accepted for enquiry, assigned, active, awaiting response, blocked, deferred, exhausted, unsupported, contradicted, duplicate, out of scope, completed, reopened and retained for record. Configuration may define finer labels but cannot collapse these materially different outcomes.

The system must not rank or sort leads by hidden generator significance. Default ordering must be neutral and transparent (for example, creation time or explicit user-selected sort).

### 4.5 Hypothesis and alternative explanation

A hypothesis is a provisional explanatory proposition created or adopted by an investigator. It must be attributable and must never be presented as hidden world truth.

Attributes: hypothesis_id, investigation_id, proposition, author, creation time, rationale, supporting references, contrary references, assumptions, confidence expression (optional and explicitly subjective), status, review history, supersession link and provenance.

Hypotheses may coexist and conflict. A hypothesis cannot be marked as fact merely because it has more linked records, a high subjective confidence or an AI-generated score. Alternative explanations and exculpatory possibilities must be recordable without penalty. The interface must not invent a probability of guilt.

### 4.6 Investigative task

A task is a discrete, authorised item of work with a defined actor/owner and expected output. It may be assigned to a human investigator or an NPC investigator if that NPC has authority, access, competence, time and resources.

Attributes:
- task_id, investigation_id, optional workstream_id;
- neutral title and instructions authored by an authorised actor;
- purpose and expected output;
- creator, assignee, supervisor and assignment time;
- priority and rationale;
- status and transition history;
- prerequisites/dependencies;
- relevant records, leads, objectives and request IDs;
- due condition or deadline, if configured;
- start, pause, resume and completion events;
- result summary and authoritative output references;
- failure/blocked reason;
- review/acceptance decision;
- provenance and access policy.

Tasks do not run while the simulation is paused. A due date is an in-world condition, not a real-world timer. A task may be marked complete only when its actual outcome is recorded; an unanswered request is not a completed result.

### 4.7 Investigative action

An action is a material investigative step or event, including a search of an authorised record, contact attempt, request, review, visit, comparison, analysis or other permitted action. BP-16 records the action and its outcome; specialist source domains own their source activity where applicable.

Required fields: action_id, investigation_id, actor, action type, time, authority/access basis, purpose, inputs/source versions, method or procedure reference, action narrative, output references, result, limitations, failure/exception, related task/lead/objective, and provenance.

### 4.8 Investigative decision

A decision is a deliberate choice affecting investigative direction, resource allocation, access request, prioritisation, task assignment, line disposition, pause/resumption or recommendation/referral.

Required fields:
- decision_id and investigation_id;
- decision-maker and role/authority at decision time;
- canonical decision time;
- question decided;
- information considered, with immutable source references and versions;
- rationale;
- alternatives considered, where recorded;
- known uncertainty and contrary material;
- decision/outcome;
- conditions, review trigger or expiry condition;
- affected tasks, leads, objectives, workstreams and people;
- review/appeal/supersession references;
- provenance.

A decision record does not imply that its decision was correct. Later review may criticise or supersede it without erasing it.

### 4.9 Request and response

A request is a formal handoff from investigation to a source-owning division or external in-world body. It identifies the requested action/data, authority, scope, time range, target, purpose, priority, requester, recipient, restrictions and expected response.

A response is a linked record from the recipient owner. It may be fulfilled, partially fulfilled, declined, unavailable, no-hit, inconclusive, delayed, withdrawn, invalid or returned for clarification. The original request remains immutable; amendments create a new version or linked replacement. The response source remains owned by the recipient division.

### 4.10 Review record

A review records independent or supervisory examination of investigative work. It identifies reviewer, authority, time, scope, materials examined, findings, recommendations (if requested/authorised), decisions, actions and unresolved disagreements. A review cannot silently change a source record or make a hidden truth disclosure.

## 5. Identity, relationships and cardinality

1. Each investigation belongs to one and only one case.
2. Each case may have zero, one or multiple investigations subject to BP-15 policy.
3. An investigation may have multiple workstreams, objectives, leads, hypotheses, tasks, actions, decisions, requests, reviews and linked source records.
4. A lead may be linked to multiple tasks and hypotheses; a task may address multiple leads when its purpose and ownership are explicit.
5. One source record may support, contradict or contextualise several leads. Linkage does not duplicate the source.
6. One person may have multiple case roles across cases and time. BP-03 identity is canonical; BP-17/BP-18 own role semantics.
7. One task has one accountable assignee at a time. Collaborators may be many. Reassignment is historised.
8. One decision has one accountable decision-maker; consultation and concurrence are separately recorded.
9. A request has one responsible receiving owner at a time, even if multiple teams contribute.
10. A cross-case shared task must identify a lead investigation and all participating case references; BP-15 retains case ownership and BP-16 records allocation/permission boundaries.
11. Deletion is not a normal lifecycle operation. Retention, restriction, correction and archival follow BP-38/BP-42/BP-44.

## 6. Lifecycle and state transitions

### 6.1 Investigation lifecycle

Suggested controlled states:
- proposed;
- authorised;
- active;
- paused;
- dormant;
- transferred;
- concluded;
- administratively closed;
- restricted/read-only;
- reopened (new state event, not history erasure).

Transitions require an authorised actor and reason. Creation does not itself authorise intrusive actions. A case closure under BP-15 may cause an investigation review event but must not silently rewrite investigation status. An investigation may be administratively concluded with unresolved matters if the record explicitly states why.

### 6.2 Workstream lifecycle

proposed → active → paused / blocked / dormant → active → concluded / cancelled / transferred. Reopening creates a new state event and records the reason. A workstream may remain open after another workstream concludes.

### 6.3 Lead lifecycle

unassessed → accepted / duplicate / out-of-scope / deferred; accepted → assigned → active → awaiting response / blocked / deferred / exhausted / unsupported / contradicted / completed; any disposition may be reopened by authorised decision with reason. "Exhausted" means recorded reasonable avenues under the defined scope were attempted or unavailable; it does not mean the underlying proposition is false.

### 6.4 Task lifecycle

draft → authorised → assigned → queued → active → paused / blocked / awaiting response → completed / failed / cancelled / withdrawn. A completed task may be reopened only through a new linked event and reason. Failed and cancelled tasks remain visible. No task advances when simulation time is frozen.

### 6.5 Hypothesis lifecycle

proposed → under consideration → retained / weakened / strengthened / disputed / rejected / unresolved / superseded. These are investigator assessments, not objective truth states. A hypothesis may be reopened or superseded. "Rejected" records an investigative judgement and basis; it is not a universal proof of impossibility.

### 6.6 Decision lifecycle

draft (if supported) → made → reviewed / superseded / revoked where authority permits. The original decision and its effects remain historically visible. Revocation does not retroactively erase actions lawfully taken under it; corrective action is separately recorded.

### 6.7 Request lifecycle

draft → submitted → accepted / returned / declined → in progress → fulfilled / partially fulfilled / no-hit / unavailable / inconclusive / failed / withdrawn / cancelled. A response may be corrected by its owner through a versioned correction. BP-16 never edits the recipient's authoritative result.

## 7. Investigative work planning and coordination

### 7.1 Plans

An investigative plan is a human-authored or expressly approved structured view of objectives, workstreams, tasks, dependencies, resource requests, known constraints and review points. It may be incomplete and revised. It is not a deterministic route to solve the case.

The plan must distinguish:
- established administrative facts;
- reported claims;
- leads awaiting assessment;
- hypotheses;
- authorised tasks;
- requests awaiting response;
- blockers;
- completed actions and actual results;
- unresolved questions.

The system may provide blank templates and neutral organisational views. It must not populate a plan with generated suspect theories, decisive clues, ranked likely culprits or unsolicited "next steps".

### 7.2 Teams and assignments

A team may contain authorised personnel from one or more units. Membership and authority are validated against BP-05/BP-06/BP-08/BP-30/BP-42. The accountable investigation lead is not automatically the case owner, legal decision-maker or holder of every required authority.

Assignment rules:
- one accountable owner per task;
- optional collaborators and reviewers;
- effective-dated membership;
- explicit handover acceptance or recorded forced transfer;
- no assignment to a person who is unavailable, deceased, separated or lacks required capability/access;
- NPC assignment requires plausible workload, location, schedule, skill and knowledge;
- conflicts of interest and restricted roles are surfaced to authorised supervisors;
- reassignment preserves prior ownership and work history.

### 7.3 Dependencies and concurrency

Tasks may depend on other tasks or external responses. Dependencies must be acyclic unless a deliberately modelled iterative cycle is approved and bounded. A blocked task identifies the blocking dependency; it does not invent a resolution. Independent tasks may proceed concurrently where staff/resources permit. Shared resources must reconcile with BP-08/BP-09.

A task's dependency completion is not evidence that the task itself succeeded. A task can be complete with an inconclusive outcome.

### 7.4 Priorities

Priority is a configurable administrative classification assigned by an authorised actor with rationale. Priority may consider urgency, safeguarding, risk of loss, operational impact, legal deadline and resource constraints. It must not be calculated from hidden culprit relevance. Equal-priority ordering is stable and neutral.

## 8. Leads, hypotheses and information discipline

1. Lead creation requires a source or a clearly labelled investigator-generated question/observation. The origin is explicit.
2. Every lead preserves the exact source reference and version available at creation.
3. The lead description distinguishes direct observation, reported account, inference and assumption.
4. A lead can be pursued even when weak, and can be retained without being pursued.
5. A lead may be contradicted by later material without being deleted.
6. A lead may be duplicated; duplicate resolution links records and preserves both histories.
7. A lead may concern an unknown person, unidentified object, vehicle, location, event, business, document, digital account or other entity.
8. A lead may be exculpatory or point away from a suspect.
9. A hypothesis records both supporting and contrary information. The interface must not hide contrary records by default.
10. The system must not assign a guilt probability, suspect ranking or hidden relevance score.
11. A lead's closure disposition is not an offence classification, forensic conclusion, legal finding or case closure.
12. Intelligence items remain governed by BP-21. Their confidence and source grading are displayed as supplied by BP-21, not silently recomputed.
13. Evidence exhibits remain governed by BP-23. A lead link does not create a new exhibit.
14. Forensic findings remain governed by BP-24. An investigative interpretation is explicitly labelled as such.
15. Interview records remain governed by BP-19. A summary cannot be presented as a verbatim statement.
16. Surveillance records remain governed by BP-20. Missing coverage cannot be represented as proof that an event did not occur.
17. Unverified or anonymous claims remain labelled and traceable to their origin/handling record.
18. Corrections and changed interpretations append new versions; the original statement remains recoverable according to access policy.

## 9. Investigative actions and specialist requests

BP-16 may create and track requests; the receiving owner determines whether and how to fulfil them. Requests must be specific enough to be actionable but cannot bypass the recipient's authority or permissions.

Supported request classes include, without limiting future configuration:
- BP-17 participant contact, safeguarding or witness availability;
- BP-18 role/status clarification or controlled suspect-related records;
- BP-19 interview, re-interview, statement or recording retrieval;
- BP-20 surveillance review, footage retrieval or observation request;
- BP-21 intelligence assessment, source validation or dissemination;
- BP-22 scene access, scene record or further scene examination;
- BP-23 exhibit retrieval, transfer, continuity confirmation or submission;
- BP-24 forensic submission, comparison, specialist review or interpretation;
- BP-25 warrant/arrest/search application or operational referral;
- BP-27 disclosure/prosecution liaison;
- BP-30 command direction or resource authorisation;
- BP-31 professional standards referral;
- BP-38 records retrieval, correction or provenance query.

A request must capture:
- request ID and investigation/case linkage;
- requesting actor and authority;
- recipient division/person/team;
- target person/entity/record;
- purpose and scope;
- requested date/time range and canonical time basis;
- location or geographic scope where applicable;
- urgency/priority and rationale;
- legal/policy authorisation reference where required by fictional canon;
- privacy/classification restrictions;
- expected output type;
- submission and receipt timestamps;
- response status, source ID and version;
- partial fulfilment, refusal, no-hit, technical failure or limitations;
- requester acknowledgement/review.

A request cannot be treated as an instruction to alter source records. A refusal is a valid recorded outcome, not a system error to be hidden.

## 10. Investigative decisions, reviews and accountability

Material decisions must record the decision-maker, role and authority effective at the time; the information actually considered; source versions; rationale; uncertainty; alternatives where recorded; outcome; affected work; review trigger; and later supersession.

Decision categories may include:
- opening or narrowing an investigation;
- creating, merging or separating workstreams;
- accepting, deferring or closing a lead;
- selecting or changing a hypothesis;
- prioritising or allocating tasks;
- requesting specialist resources;
- pausing, resuming or concluding work;
- escalating or referring a matter;
- recommending (not authorising) an arrest, warrant, search or prosecution step;
- correcting or qualifying an investigative summary.

Review must be possible without overwriting the original decision. Review outcomes may be accepted, accepted with action, challenged, returned for more information, escalated or recorded as unresolved disagreement. A reviewer cannot silently change a source-domain result.

Supervisory review is driven by configured policy, risk or an explicit command. The system must not create artificial deadlines that advance during pause. Review triggers may be event-based (new evidence received, serious incident, case referral) or time-based using the canonical simulation clock.

## 11. NPC investigators and knowledge boundaries

NPC investigators may perform work only when:
- the simulation is active;
- their in-world schedule permits;
- they are alive and available;
- they possess the required competence, authority, access and resources;
- the work is assigned or otherwise permitted by an explicit simulation rule;
- they know the relevant information through plausible observation, receipt, authorised access or documented communication.

NPCs must not:
- read BP-14 hidden truth;
- infer facts from protected generator metadata;
- access records outside their clearance;
- know an interview or surveillance result before receipt;
- complete work while the player is absent;
- advance a task simply because real-world time passes;
- generate an authoritative result without recording the action, method, time and source;
- reveal hidden culprit/accomplice identities to the player through dialogue or indirect implication.

NPC-generated work must be auditable and may be mistaken, incomplete, biased or inconclusive in plausible ways. NPC knowledge is not shared automatically across a team; handoffs and briefings create recorded knowledge-transfer events.

## 12. Time, deadlines and paused simulation

BP-37 owns the canonical clock. BP-16 stores event times against that clock and uses it for scheduling, due conditions and chronology.

When the player exits or the simulation is paused:
- no task starts, progresses, completes or expires;
- no NPC conducts an interview, review, analysis, surveillance check or field action;
- no request is fulfilled by an in-world actor;
- no deadline elapses;
- no queue is processed;
- no notification is generated from newly elapsed simulation time;
- no resource availability changes due to time passage;
- no hidden catch-up occurs on resume.

On resume, processing continues from the exact saved simulation state. Events that were already queued remain queued. Their ordering is deterministic where BP-35 specifies deterministic replay. The real-world gap is not converted into in-world time.

## 13. Information security and player-facing disclosure

Access is determined by BP-42 and relevant domain policies. BP-16 must enforce permissions at retrieval, query, report, export, notification, search, summarisation and visualisation layers—not merely hide a field in the interface.

Protected information includes:
- hidden generator truth and culprit/accomplice identities;
- restricted personal records;
- confidential sources and intelligence handling details;
- protected interview/surveillance methods;
- sealed or restricted evidence and legal material;
- credentials and system secrets.

The exact `bingo` trigger is case-insensitive? **No.** The trigger is the exact lowercase text `bingo`, with no added punctuation, whitespace or surrounding words. Any different input does not unlock protected truth. The trigger's precise matching and scope must be implemented in BP-01/BP-42 and applied consistently here. This division must not create its own alternative reveal mechanism.

The player-facing system must not leak through:
- lead ordering, labels, colours, badges or counts;
- task names, assignment patterns or NPC dialogue;
- error messages, unavailable-record messages or timing;
- summaries, dashboards, notifications or exports;
- optional maps, timelines or visual scene reconstructions;
- differences in response latency or empty-result behaviour;
- AI-generated phrasing that indirectly confirms a protected identity.

A normal user query for a person's name or record must return only authorised known information. The system must not confirm that a protected person is the perpetrator by refusing, redacting or selectively omitting their record. Access-denied responses should be generic enough not to signal hidden truth.

## 14. Records, provenance, audit and retention

Every material BP-16 record must include:
- stable record ID and record type;
- investigation and case references;
- actor/system identity and actor role at event time;
- canonical event time and record creation time;
- source references and exact versions;
- authoring method (human, NPC, system import or derived);
- authority/access basis where relevant;
- content version and supersession relationship;
- status history and reason;
- integrity metadata required by BP-38;
- access classification and retention policy reference.

Original source material remains owned by its source domain. A derived investigative note records the source and transformation. A summary must not be substituted for the original. Corrections must preserve who changed what, when, why and under whose authority.

Audit logs must record successful and denied access to restricted investigation material where required by BP-42. Audit logging itself must not reveal protected facts to unauthorised readers.

Retention, archival, legal hold, deletion and recovery are governed by BP-38/BP-39/BP-44. BP-16 must not invent an independent retention schedule. A case closure does not authorise destruction of investigation history.

## 15. Text interface and optional visuals

All core actions must be available through a laptop-style text interface:
- open an investigation;
- inspect status, objectives, workstreams and assigned personnel;
- create or revise a player-authored objective, lead, hypothesis or task;
- record an action or decision;
- submit and track an authorised request;
- inspect linked source records and versions;
- review blockers and task outcomes;
- compare supporting and contrary material;
- inspect chronology and provenance;
- transfer, pause, resume or conclude work when authorised;
- inspect review history and unresolved issues.

The interface should show neutral factual information, not prescriptive next steps. It may offer commands or blank action templates, but not recommendations that reveal a solution.

Optional maps, scene diagrams, timelines, relationship views and charts must be generated from canonical BP-02/BP-12/BP-15/BP-20/BP-22/BP-23/BP-24/BP-37 records. Each visual must identify its source data and time basis. Text remains authoritative. No visual may add inferred facts without an explicit label and provenance.

## 16. Reporting and outputs

BP-16 may produce:
- investigation status report;
- workstream register;
- task register and dependency view;
- lead register with neutral ordering;
- hypothesis register showing both supporting and contrary material;
- action and decision chronology;
- outstanding request register;
- review and handover report;
- source-reference index;
- unresolved issue register;
- investigative summary for authorised internal use;
- controlled case handoff package for BP-15/BP-27.

Reports must distinguish confirmed source records from investigator statements and analytical assessments. Every summary has an as-of canonical time, author, scope, source list, limitations and access classification. A report must not imply completeness if material is outstanding or unavailable.

## 17. Error, exception and recovery handling

The system must handle, without data loss or false success:
- duplicate or conflicting person identities;
- source record corrected after a lead was created;
- source record withdrawn, restricted or superseded;
- contradictory statements or records;
- missing, corrupt or unavailable attachments;
- inaccessible source due to clearance;
- request refused or partially fulfilled;
- no-hit result;
- unavailable specialist or resource;
- assignee absent, deceased, transferred or no longer authorised;
- task dependency cycle;
- concurrent edits to the same investigative record;
- duplicate task execution or retry;
- interrupted transaction or persistence failure;
- case closed while investigative work is active;
- case reopened after investigation conclusion;
- shared work across related cases;
- incorrect lead association;
- mistaken hypothesis;
- unlawful or unauthorised action recorded as an allegation;
- clock rollback/recovery or duplicate event delivery;
- player attempts to elicit protected truth through indirect prompts;
- NPC knowledge contamination;
- population cap reached when a newly relevant person is encountered.

A failed write must not partially commit related records. Retried operations must be idempotent where appropriate. A conflict must preserve both proposed changes for authorised resolution. The system must never resolve ambiguity by silently merging people or records.

If a relevant person cannot be added because the 10,000-person living cap is reached, BP-03 must block the addition and require a canon-compliant population event (death or permanent exit) before entry. BP-16 must not bypass the cap by creating a temporary duplicate, anonymous person record or uncounted shadow identity. The event that establishes relevance must remain recorded.

## 18. Dependencies and event contracts

### 18.1 Inbound dependencies

- BP-01: canon, player agency, reveal trigger and no-hint rules.
- BP-02: canonical locations, spatial IDs and jurisdiction.
- BP-03: person identity, population ledger and permanent relevance promotion.
- BP-04: business, property, occupancy and organisational records.
- BP-05/BP-06/BP-08: police authority, personnel, role, assignment, capability and availability.
- BP-09: police resource availability.
- BP-11/BP-12: emergency communications and incident records.
- BP-13/BP-14: crime classification and occurrence/report separation, with strict hidden-truth firewall.
- BP-15: case identity, case status, ownership, related-case references and chronology.
- BP-17/BP-18: participant roles.
- BP-19/BP-20/BP-21: interview, surveillance and intelligence source records.
- BP-22/BP-23/BP-24: scene, evidence and forensic records.
- BP-25/BP-26/BP-27/BP-28: arrest, custody, legal process and outcomes.
- BP-30/BP-31: command and professional standards.
- BP-35/BP-37: event processing and canonical time.
- BP-38/BP-39: record, audit, persistence and recovery.
- BP-42: access and information boundaries.

### 18.2 Outbound events and requests

BP-16 may emit versioned events such as:
- investigation_opened / investigation_status_changed;
- workstream_created / workstream_status_changed;
- objective_created / objective_revised / objective_closed;
- lead_created / lead_assigned / lead_disposition_changed;
- hypothesis_recorded / hypothesis_revised / hypothesis_superseded;
- task_created / task_assigned / task_started / task_paused / task_completed / task_failed;
- investigative_action_recorded;
- investigative_decision_recorded / decision_reviewed;
- specialist_request_submitted / request_response_linked;
- investigation_review_requested / review_completed;
- investigative_handover_created / accepted;
- investigative_summary_published.

Events carry stable IDs, schema/version, actor, canonical time, correlation/causation references, source versions, access classification and idempotency key where required. Events do not authorise recipients to mutate unrelated source records.

### 18.3 Cross-division contracts

- BP-15 receives case-level linkage and status-impact requests; BP-16 does not directly close/reopen cases.
- BP-17/BP-18 receive role-specific requests; BP-16 cannot create their authoritative participant statuses.
- BP-19/BP-20/BP-21/BP-22/BP-23/BP-24 return source-owned records with limitations and provenance.
- BP-25/BP-27 receive referrals or requests only; their authority decisions remain independent.
- BP-30 may issue command direction; BP-16 records its receipt and implementation.
- BP-38/BP-39 guarantee durable storage and recovery; BP-16 supplies complete records and relationships.
- BP-42 checks every protected read/write and prevents hidden-truth leakage.
- BP-43 validates acceptance criteria and regression behaviour.

## 19. Permissions and authority matrix

| Operation | Minimum authority concept | Notes |
|---|---|---|
| View investigation | Case/investigation access | Further restrictions may apply to linked sources. |
| Create objective/lead/hypothesis | Assigned investigator or authorised supervisor | Author and rationale required. |
| Create/assign task | Investigation lead or delegated supervisor | Assignment cannot exceed recipient's authority. |
| Record action | Actor who performed it or authorised recorder | Distinguish firsthand record from later transcription. |
| Make material decision | Decision authority configured by BP-30/policy | Role at decision time is preserved. |
| Submit specialist request | Authorised investigator and required approval | Recipient retains fulfilment authority. |
| Access restricted source | BP-42 clearance and source-domain permission | Case membership alone is insufficient. |
| Review investigation | Designated supervisor/reviewer | Conflict-of-interest check applies. |
| Transfer ownership | Current owner or authorised supervisor | Handover and reason recorded. |
| Conclude investigation | Designated authority | BP-15 case lifecycle remains separate. |
| Export/share report | Explicit disclosure permission | Redaction and source restrictions enforced. |
| Reveal hidden truth | Exact global `bingo` trigger only | No division-specific override. |

No rank, title, case membership or task assignment alone grants unrestricted access. Authority is effective-dated and checked at action time. Historical records preserve the authority basis that existed when the action occurred.

## 20. Performance, scale and storage principles

1. Investigation records must scale to many concurrent cases, workstreams, leads, tasks and linked source records without changing semantics.
2. Use stable references rather than duplicating large source documents, media, evidence or personal records.
3. Store concise structured metadata and full authored narrative where required; compression must never remove uncertainty, source identity, chronology, limitations, contrary material or provenance.
4. Use pagination and filtered retrieval for large registers; default views must not hide relevant exculpatory or contradictory material.
5. Avoid unbounded fan-out when a case is linked to many records. Use indexed references and explicit query scopes.
6. Preserve auditability under retries, concurrency and recovery.
7. Do not create speculative schema migrations or Neon writes from this specification.
8. Any future Neon change requires a fresh measured database baseline, incremental storage estimate in bytes/MiB, projected total and assumptions, explicit user approval before writing, then post-write measurement. No approval is implied by blueprint progress.
9. Benchmarks and storage tests are owned/evidenced under BP-43/BP-38/BP-39.
10. Do not trade away meaning or detail to meet storage targets.

## 21. Acceptance criteria and test suite

The following are required acceptance tests. They are design criteria only; none is claimed executed. Test IDs are stable within BP-16 and must later link to executable tests and evidence under BP-43.

### Identity, case linkage and lifecycle

- **INV-AT-001** — Creating an investigation requires a valid BP-15 case reference; an unknown case is rejected.
- **INV-AT-002** — An investigation cannot belong to two cases simultaneously.
- **INV-AT-003** — One case can contain multiple authorised investigations without duplicating the case record.
- **INV-AT-004** — Investigation status changes preserve actor, canonical time, reason and prior state.
- **INV-AT-005** — Closing a BP-15 case does not silently delete or rewrite investigation records.
- **INV-AT-006** — Reopening a case does not silently reactivate every concluded workstream.
- **INV-AT-007** — A concluded investigation can retain unresolved issues and linked source records.
- **INV-AT-008** — A transferred investigation preserves prior ownership and handover history.
- **INV-AT-009** — Case-level chronology remains owned by BP-15; investigation events are linked without replacing it.
- **INV-AT-010** — A request to change case status is routed to BP-15 and cannot directly mutate BP-15 state.

### Leads and information classification

- **INV-AT-011** — Every lead has a stable ID, origin, source reference or explicitly labelled investigator-created basis.
- **INV-AT-012** — A lead can be recorded as unverified without being promoted to evidence.
- **INV-AT-013** — A lead can be contradicted while its original content and history remain available.
- **INV-AT-014** — Duplicate leads can be linked without deleting either history.
- **INV-AT-015** — A lead about an unknown person or unidentified object does not require inventing an identity.
- **INV-AT-016** — A lead may be exculpatory and remains visible in normal authorised views.
- **INV-AT-017** — Lead ordering does not expose generator-side relevance or culprit probability.
- **INV-AT-018** — "Exhausted" is not interpreted as false or disproven.
- **INV-AT-019** — Changing a lead status cannot convert it into an exhibit or intelligence item.
- **INV-AT-020** — A lead references the exact source version available at creation.
- **INV-AT-021** — Later source correction creates a traceable changed-source relationship without rewriting the lead's original basis.
- **INV-AT-022** — Anonymous information remains labelled with source/handling limitations.
- **INV-AT-023** — A source record can support one lead and contradict another without duplication.
- **INV-AT-024** — A summary cannot be presented as an original interview, recording or document.

### Hypotheses and decisions

- **INV-AT-025** — Multiple competing hypotheses can coexist.
- **INV-AT-026** — A hypothesis records supporting and contrary references separately.
- **INV-AT-027** — An investigator's confidence does not become a system-calculated probability of guilt.
- **INV-AT-028** — Rejection of a hypothesis preserves its rationale and evidence references.
- **INV-AT-029** — A superseded hypothesis remains historically retrievable to authorised users.
- **INV-AT-030** — A material decision identifies decision-maker, authority, time, information considered and rationale.
- **INV-AT-031** — A decision's source references resolve to immutable versions.
- **INV-AT-032** — A review can criticise a prior decision without erasing it.
- **INV-AT-033** — A decision made by an unauthorised actor is rejected or explicitly recorded as an unauthorised event without granting it effect.
- **INV-AT-034** — Alternative explanations and exculpatory material are not hidden by default.
- **INV-AT-035** — A conclusion is labelled as investigative assessment, not adjudicated fact.

### Tasks, teams and concurrency

- **INV-AT-036** — Every task has one accountable assignee at a time.
- **INV-AT-037** — Reassignment preserves prior assignee, time, reason and work history.
- **INV-AT-038** — A task cannot be assigned to a deceased, separated or unavailable NPC.
- **INV-AT-039** — An NPC task assignment checks competence, authority, access, schedule and resources.
- **INV-AT-040** — A task with an unmet dependency cannot be marked as started unless an authorised override is recorded.
- **INV-AT-041** — Cyclic task dependencies are rejected unless an explicitly bounded iterative workflow is configured.
- **INV-AT-042** — Independent tasks may proceed concurrently without overwriting one another.
- **INV-AT-043** — Duplicate task submission with the same idempotency key does not create duplicate work.
- **INV-AT-044** — Conflicting concurrent edits preserve both versions for authorised reconciliation.
- **INV-AT-045** — A task marked complete records its actual output or explicit no-output outcome.
- **INV-AT-046** — An unanswered request cannot be represented as a completed result.
- **INV-AT-047** — A failed task remains visible and can be retried through a linked new attempt.
- **INV-AT-048** — Team membership changes are effective-dated and historised.
- **INV-AT-049** — Shared work across cases records all case links and permission boundaries.
- **INV-AT-050** — Task priority changes require an authorised actor and rationale.

### Specialist-domain interfaces

- **INV-AT-051** — An interview request creates a BP-19 request and does not fabricate an interview record.
- **INV-AT-052** — Interview source content is retrieved from BP-19 with original/version distinction intact.
- **INV-AT-053** — A surveillance request is subject to BP-20 authority and coverage limits.
- **INV-AT-054** — Absence of surveillance coverage is never reported as proof of absence.
- **INV-AT-055** — An intelligence product retains BP-21 source grading, confidence and handling restrictions.
- **INV-AT-056** — Intelligence cannot be relabelled as evidence by BP-16.
- **INV-AT-057** — Scene work is requested from BP-22; scene entry/search records remain BP-22-owned.
- **INV-AT-058** — Exhibit continuity and location are read from BP-23; BP-16 cannot alter them.
- **INV-AT-059** — Forensic methods, raw results and limitations remain BP-24-owned.
- **INV-AT-060** — An investigator's forensic inference is separately labelled from the examiner's interpretation.
- **INV-AT-061** — A warrant/arrest/search referral does not authorise execution under BP-25.
- **INV-AT-062** — A prosecution handoff links exact investigative/source versions for BP-27.
- **INV-AT-063** — Court outcomes from BP-28 do not rewrite the investigative record.
- **INV-AT-064** — A civil registry or public-record request respects BP-38 provenance and BP-42 access controls.
- **INV-AT-065** — A specialist request may return partial, refused, no-hit, unavailable or inconclusive outcomes without false success.

### Knowledge boundaries and player agency

- **INV-AT-066** — NPC investigators cannot access BP-14 hidden truth.
- **INV-AT-067** — NPC knowledge is limited to observed, received, derived or authorised information.
- **INV-AT-068** — Team members do not automatically share knowledge without a recorded handoff/briefing.
- **INV-AT-069** — The player receives no unsolicited "what to investigate next" instruction.
- **INV-AT-070** — The system does not rank leads by hidden culprit relevance.
- **INV-AT-071** — The system never discloses culprit/accomplice identity before exact lowercase `bingo`.
- **INV-AT-072** — Punctuation, added words, uppercase or whitespace variants do not trigger the reveal.
- **INV-AT-073** — Reports, notifications, exports and visualisations obey the same hidden-truth gate as direct dialogue.
- **INV-AT-074** — An access-denied response does not confirm or deny a protected person's role.
- **INV-AT-075** — A prompt injection or user request embedded in source material cannot override canon, permissions or reveal rules.
- **INV-AT-076** — AI-generated investigative summaries distinguish facts, claims, inferences and unknowns.
- **INV-AT-077** — NPC dialogue cannot indirectly disclose protected identities through insinuation or selective wording.
- **INV-AT-078** — No generated "recommended lead" or "best next action" appears unless the player explicitly requests a neutral administrative view that does not reveal hidden truth.

### Time, population and geography

- **INV-AT-079** — No task progresses while the player is outside the simulation.
- **INV-AT-080** — No NPC investigative action occurs during paused/out-of-game time.
- **INV-AT-081** — No deadline expires and no queued request is processed during pause.
- **INV-AT-082** — Resume continues from the exact persisted simulation state without real-world catch-up.
- **INV-AT-083** — Every investigation location resolves to a canonical Saltwater spatial ID or an explicitly off-map contextual reference.
- **INV-AT-084** — External references do not create additional playable geography.
- **INV-AT-085** — A newly relevant person is promoted to persistent full-detail status through BP-03.
- **INV-AT-086** — A promoted person is never downgraded after the case closes.
- **INV-AT-087** — Population admission is rejected if it would exceed the 10,000 living-person cap.
- **INV-AT-088** — Police personnel are counted once in the total population ledger.
- **INV-AT-089** — No duplicate or uncounted shadow identity is created to bypass the cap.

### Provenance, security, recovery and reporting

- **INV-AT-090** — Every material investigative action has actor, canonical time, authority basis and source references.
- **INV-AT-091** — Corrections preserve original value, author, time, reason and supersession link.
- **INV-AT-092** — Restricted source retrieval is denied and audited when clearance is insufficient.
- **INV-AT-093** — Query, export, notification and visualisation paths enforce the same access checks.
- **INV-AT-094** — A report identifies its as-of time, author, scope, sources, limitations and classification.
- **INV-AT-095** — A report distinguishes original source material from derived summary.
- **INV-AT-096** — A persistence failure cannot partially commit a task and its dependent records.
- **INV-AT-097** — Retry/replay does not duplicate an investigative action or request.
- **INV-AT-098** — Restore/recovery preserves identifiers, source links, chronology and audit history.
- **INV-AT-099** — A case handoff preserves open tasks, unresolved leads, restrictions and source versions.
- **INV-AT-100** — A large investigation register can be paginated without silently omitting authorised records.
- **INV-AT-101** — Search results do not reveal inaccessible record existence or hidden truth.
- **INV-AT-102** — An investigation summary is not labelled complete while required source responses remain outstanding.
- **INV-AT-103** — A task deadline uses canonical in-world time and does not advance outside the simulation.
- **INV-AT-104** — Optional visual outputs can be traced to canonical source records and do not contradict text.
- **INV-AT-105** — Storage compaction preserves all narrative meaning, uncertainty, provenance and relationships.

### Integration, scale and regression

- **INV-AT-106** — A single case with multiple investigations and hundreds of leads retains unique IDs and correct ownership.
- **INV-AT-107** — Multiple cases may reference the same source record without duplicating its authoritative content.
- **INV-AT-108** — A multi-scene investigation preserves separate scene ownership, timelines and source links.
- **INV-AT-109** — Contradictory time sources remain separately represented with their time basis and uncertainty.
- **INV-AT-110** — A source correction propagates a visible update notification without silently changing prior decisions.
- **INV-AT-111** — A withdrawn or restricted source is handled according to policy while its historical reference remains auditable.
- **INV-AT-112** — A task dependency failure does not falsely mark dependent tasks successful.
- **INV-AT-113** — A handover interrupted by persistence failure can be safely retried without duplicate ownership.
- **INV-AT-114** — A reviewer cannot access restricted material solely by being assigned as a reviewer.
- **INV-AT-115** — A player cannot obtain protected truth through a sequence of otherwise individually permitted queries.
- **INV-AT-116** — A system-generated event records causation/correlation and can be replayed deterministically where required.
- **INV-AT-117** — A population-cap rejection leaves the original investigation and source records intact.
- **INV-AT-118** — A reopened lead preserves its prior disposition and records the reopening decision.
- **INV-AT-119** — A completed investigation can be audited from source, through actions and decisions, to its summary without missing provenance.
- **INV-AT-120** — No acceptance test is marked passed until reproducible evidence is linked under BP-43.

## 22. Traceability to original source requirements and tests

The original source JSON remains unchanged. The IDs below refer to its 1-based arrays and exact JSON pointers. The 52→44 crosswalk remains the mapping authority; this division records the relevant allocation and how it is implemented here.

| Source ID | Original source area | BP-16 incorporation |
|---|---|---|
| S04.R03 | Person identity and life records | Permanent full-detail promotion for materially relevant persons; BP-03 owns identity and cap. |
| S04.T02 | Person identity tests | Promoted people never downgraded/erased; INV-AT-085/086. |
| S07.R03 | Business and commercial economy | Business records, premises, employees, transactions and police-relevant activity may create investigative leads; BP-04 owns them. |
| S12.R03 | Civil registry/public records | Controlled retrieval and disclosure requests; BP-38/BP-42 remain authoritative. |
| S17.R03 | Roads, transport and mobility | Travel, movement and case timeline source references; BP-02/BP-04 own geography and transport. |
| S29.R03 | Incidents, crime taxonomy and occurrence generation | Investigation links distinguish incident, offence classification, intelligence and outcome. |
| S30.R01 | Case management and investigative command | Case linkage, ownership boundaries, objectives, actions, decisions, reviews and deadlines. |
| S30.R02 | Concurrent investigations, cold cases, linked series, referrals and reopened cases | Multiple investigations/workstreams, dormant work, referrals and cross-case coordination. |
| S30.R03 | Full case chronology and decision provenance | Immutable source references, attributed actions/decisions and audit chronology. |
| S30.T01 | Case state change accountability | Every state change has actor, time, reason and source/evidence reference. |
| S31.R01 | Role-specific person links, contact, vulnerability, risk and status | BP-17/BP-18 request and reference contracts; identity remains BP-03. |
| S31.R02 | Distinguish allegation, suspicion, evidential support, charge and finding | Explicit information categories and no guilt-by-role rule. |
| S31.R03 | Permanent person promotion | Population and persistence invariants. |
| S31.T01 | No guilt from generated role/suspicion | INV-AT-016, 071 and role separation. |
| S33.R02 | Forensic analysis, intelligence and evidential interpretation interfaces | Specialist requests and strict separation of raw result, interpretation and inference. |
| S33.T01 | Forensic conclusion source/method/limitations/examiner | BP-24-owned report references and INV-AT-059/060. |
| S34.R03 | No leading prompts or hidden solution disclosure | Player-agency and reveal invariants. |
| S34.T01 | Interview chronology and source reconciliation | BP-19 source records and INV-AT-051/052. |
| S35.R01 | Source grading, reliability, confidence, dissemination and restrictions | BP-21 ownership and read-only intelligence linkage. |
| S35.R02 | Intelligence/evidence/fact distinction | No conversion or evidential inflation. |
| S35.R03 | Source provenance and uncertainty | Exact source versions and confidence/handling references. |
| S35.T01 | Intelligence source/confidence/handling | BP-21-owned attributes retained. |
| S36.R02 | Surveillance requests, authorisations, collection and continuity | BP-20 request/response contract; BP-23 evidential continuity. |
| S36.R03 | Surveillance and intelligence/evidence interfaces | Cross-domain source references; no absence-of-coverage inference. |
| S36.T01 | Device, coverage limits and time basis | INV-AT-053/054. |
| S43.R01 | Naturalistic generation, knowledge and uncertainty | NPC knowledge limits and evidence-based narrative. |
| S43.R02 | Hidden truth separated from player and NPC knowledge | Strict BP-14 firewall. |
| S43.R03 | Exact `bingo` reveal trigger | INV-AT-071–078. |
| S43.R04 | No unsolicited solution hints or next-investigation instructions | INV-AT-069/078 and text interface rules. |
| S43.R05 | Canon-changing claims persisted as structured events | BP-38/BP-35 event and persistence contracts. |
| S43.T01 | No hidden truth leakage; NPC knowledge plausible | INV-AT-066–077. |
| S43.T02 | Population and knowledge-boundary behaviour | INV-AT-085–089. |
| S45.R01 | Optional maps, layouts, timelines and diagrams | Investigation timelines and optional views derived from source data. |
| S45.R02 | Visuals traceable to canonical records | INV-AT-104. |
| S45.R03 | Text remains authoritative | Text-first interface invariant. |
| S48.R02 | Protect hidden case truth and restricted personal information | Access control across all BP-16 output channels. |
| S48.T01 | Unauthorised reads/writes rejected and audited | INV-AT-092/093. |
| S50.R01–R03 | Test strategy, edge/race/scale/replay/continuity and evidence-based completion | 120 acceptance criteria and BP-43 execution/evidence requirement. |
| S51.R01–R03 | Observability, maintenance, rollback and environment separation | BP-41/BP-43/BP-44 interfaces; no direct operational write authority. |
| S52.R01–R04 | Canon/version/change control and approval states | BP-01/BP-44 governance; draft status remains distinct from approval. |

### Cross-cutting rules

BP-16 applies all X01–X10 cross-cutting rules from the source crosswalk. In particular: stable IDs and provenance; ownership and explicit interfaces; canonical time and paused-state semantics; access controls and hidden truth; atomicity and idempotency; source/derived record distinction; reproducible testing; population and storage reconciliation; versioned change control; and no status inflation. The crosswalk's exact X-rule wording remains authoritative.

## 23. Open decisions and controlled assumptions

These are explicit decisions for user review or later policy configuration. They are not silently settled by this draft.

1. Investigation reference display format (opaque ID remains authoritative).
2. Whether one case normally has one primary investigation or may routinely have multiple independently authorised investigations.
3. Initial investigation-type catalogue and whether types affect workflow.
4. Investigation status catalogue and which transitions require supervisory approval.
5. Workstream templates, if any, and which are neutral rather than prescriptive.
6. Lead priority vocabulary and permitted priority-setting roles.
7. Whether subjective hypothesis confidence uses labels, free text or no scale; no numeric guilt probability is permitted.
8. Task due-condition vocabulary and which tasks may have deadlines.
9. NPC investigator autonomy: exact task classes permitted without direct player assignment.
10. Review triggers and frequency while simulation time is active.
11. Cross-case shared-work approval matrix.
12. Record retention and legal-hold policy, owned by BP-38/BP-44.
13. Default access matrix by rank, role, unit, assignment and case sensitivity, owned by BP-42.
14. Whether investigation plans have a versioned formal approval state or remain working documents.
15. Report templates and disclosure workflow with BP-27.
16. Whether AI-assisted neutral indexing/search may be enabled; any such feature must not recommend next steps or expose hidden truth.
17. Exact canonical matching implementation for the global `bingo` trigger is owned by BP-01/BP-42; this draft states exact lowercase matching as a conservative implementation assumption.
18. Task workload and resource allocation thresholds, owned jointly by BP-08/BP-09/BP-30 policy.
19. Conflict-of-interest and investigator separation rules, owned by BP-30/BP-31.
20. The degree of deterministic replay required for NPC investigative actions, owned by BP-35/BP-43.

### Risks and mitigations

| Risk | Mitigation |
|---|---|
| BP-16 duplicates BP-15 case lifecycle | Enforce one case owner; investigation status remains separate. |
| Leads are mistaken for evidence | Explicit type distinctions, source ownership and acceptance tests. |
| Hidden truth leaks through metadata | Apply BP-42 checks to all outputs and neutralise side channels. |
| Investigative hints reduce player agency | No automatic recommendations, suspect rankings or hidden relevance ordering. |
| NPC omniscience | Record knowledge provenance and handoffs; deny BP-14 truth access. |
| Large case records become unwieldy | Indexed stable references, pagination and neutral filters without semantic loss. |
| Conflicting source records are silently reconciled | Preserve source versions and competing accounts; explicit review only. |
| Task completion falsely implies success | Store actual result categories and output references. |
| Paused game advances in background | Freeze event engine, queues, deadlines and NPC work under BP-35/BP-37. |
| Population cap bypassed by case records | BP-03 single ledger and atomic admission check. |
| Case closure destroys unresolved work | Retain investigation history and require explicit disposition. |
| Storage optimisation removes meaning | Preserve full semantic content; compress only representation. |

## 24. Design completion checklist

A reviewer must verify all items before changing specification status from DESIGNED_DRAFT to DESIGNED:

- [ ] Every applicable source requirement and test is incorporated or explicitly assigned to its authoritative owner.
- [ ] All entities, fields, identifiers, relationships and cardinalities are specified sufficiently for BP-38 schema design.
- [ ] Every lifecycle and state transition has an actor, trigger, authority and historical record.
- [ ] Every cross-division interface has request/response ownership and failure semantics.
- [ ] BP-15/BP-16 case-versus-investigation ownership is unambiguous.
- [ ] Lead, intelligence, evidence, hypothesis, fact, conclusion and adjudicated outcome remain distinct.
- [ ] Player agency, no unsolicited hints and exact reveal gate are preserved across every output path.
- [ ] NPC knowledge is plausible and provenance-backed.
- [ ] Time freeze and resume semantics are explicit.
- [ ] Population cap and permanent person promotion are enforced by BP-03.
- [ ] Security, confidentiality and access controls are defined with BP-42.
- [ ] Storage, persistence, recovery and audit responsibilities are allocated.
- [ ] Acceptance tests cover positive, negative, boundary, adversarial, concurrency, replay, scale and integration cases.
- [ ] Every test is traceable to source requirements and later implementation evidence.
- [ ] All open decisions are either resolved by user approval or explicitly retained as approved configurable decisions.
- [ ] No Neon write, migration, seed or import has been performed or authorised.

## 25. Status and next dependencies

This document is a full design draft, not an approved specification and not implementation evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Primary next division in fixed order: **BP-17 — Victims and Witnesses**. BP-17 must define participant role, victim/witness status, contact, vulnerability, safeguarding, risk, availability and support records while preserving BP-03 identity, BP-15 case ownership and BP-16 investigative-work boundaries.
