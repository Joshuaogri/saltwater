# BP-14 — Crime Generation

**Project:** Saltwater — fictional sovereign city-state; one city, one jurisdiction  
**Blueprint division:** BP-14 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Testing:** NOT_STARTED | **Verification:** NOT_STARTED

## 1. Purpose

BP-14 defines how the simulation generates, maintains and resolves occurrences in Saltwater's world, including criminal conduct, suspected criminal conduct, non-crime events, attempted and interrupted activity, accidents, hazards, public-safety concerns, institutional events and other police-relevant occurrences.

It is the authoritative domain for occurrence generation and causal event truth. It creates plausible events from the established world: people, relationships, households, businesses, property, employment, schedules, finances, services, infrastructure, geography, environmental conditions, public life, opportunity, motive, capability, prior events and the consequences of earlier actions. It must generate a world that feels alive without making every event a crime or making crime generation appear as an arbitrary list of calls.

BP-14 does not decide what the player should investigate. It does not reveal hidden perpetrators, accomplices, motives or solutions through player-facing records, labels, suggestions or narrative. It supplies the world and its records; the player decides what to do with the information available.

The generation system must support varied, causally grounded incidents across Saltwater, including events that are never reported to police, events discovered late, events reported inaccurately, events with no known offender, events with several possible classifications, and events that develop through multiple stages. It must preserve the distinction between the true simulated occurrence, what witnesses perceive, what is reported, what police record, what investigators infer and what a court ultimately determines.

## 2. Scope and boundaries

### 2.1 In scope
- Occurrence generation across crime and non-crime domains.
- Causal models for motives, opportunity, capability, constraints, planning and consequences.
- Actor, victim, witness, organisation, property, asset and location participation references.
- Event planning, initiation, execution, interruption, completion, continuation and aftermath.
- Temporal and spatial plausibility, movement, access, schedules and resource constraints.
- Generated event truth and its strict separation from player-visible information.
- Background-world activity relevant to police, businesses, services and community life.
- Unreported, undiscovered, delayed-discovery, anonymous and misreported events.
- Recurring, linked, serial, coordinated, copycat and independent occurrences.
- Non-criminal incidents, accidents, hazards, service disruptions and emergencies.
- Event consequences, harm, loss, damage, disruption and recovery.
- Relevance-based processing with persistent identity and causal continuity.
- NPC knowledge, perception, memory, communication and reporting behaviour.
- Occurrence provenance, event lineage, state transitions, replay and audit.
- Controlled generation parameters, content diversity, balancing and anti-repetition.
- Integration with taxonomy, incident management, case management, people, businesses, geography, relationships, time, simulation engine and AI narrative.
- Generation tests, quality measures, edge cases and traceability.

### 2.2 Explicitly out of scope
- Crime and non-crime taxonomy definitions, offence elements and formal classification decisions: BP-13.
- Operational incident intake, call-taking, CAD, dispatch and incident lifecycle: BP-11/BP-12.
- Case creation, case ownership, investigative command and case lifecycle: BP-15.
- Investigative tasks, decisions, conclusions and evidential assessment: BP-16.
- Victim/witness case roles and support records: BP-17.
- Suspect/offender case status and procedural role: BP-18.
- Interview and interrogation records: BP-19.
- Surveillance records and collection authorisations: BP-20.
- Intelligence source handling and analytical products: BP-21.
- Scene management, exhibit continuity and forensic examination: BP-22/BP-23/BP-24.
- Arrest, warrant, custody, legal process, court outcomes and corrections: BP-25 through BP-29.
- Canonical city geography: BP-02.
- Canonical person identity, population accounting and permanent promotion: BP-03.
- Businesses, organisations, property and service master records: BP-04.
- Police institutional, personnel, deployment and resource authorities: BP-05 through BP-09.
- Patrol and emergency communication operations: BP-10/BP-11.
- Shared simulation engine execution and event scheduler: BP-35.
- Social relationship master records: BP-36.
- Authoritative simulation clock and calendars: BP-37.
- Shared records, persistence, security and change-control services: BP-38/BP-39/BP-42/BP-44.
- Player interface and narrative delivery: BP-40/BP-41.

### 2.3 Authority rule
BP-14 owns the authoritative simulated occurrence, causal truth and generation lineage. Other domains own their own records and decisions. BP-14 may publish an occurrence reference or domain event but cannot rewrite a police incident, case, evidence item, intelligence assessment, court finding or canonical person record.

## 3. Foundational event concepts

The system must keep these concepts separate:

| Concept | Meaning | Authority |
|---|---|---|
| World state | Current authoritative state of people, places, organisations and assets | Owning domain |
| Causal condition | A condition that contributes to a possible event | BP-14 with source-domain facts |
| Event intention | A character's internal plan or goal, whether or not acted upon | BP-14 hidden truth |
| Attempted action | An action initiated but not necessarily completed | BP-14 |
| Occurrence | A uniquely identified event or connected event sequence | BP-14 |
| Event fact | A fact about what actually occurred in the simulated world | BP-14 |
| Perception | What a person could sense or understand at a particular time | BP-14/BP-03 |
| Memory | What a person retains, forgets or misremembers | BP-03/BP-14 |
| Report | An account communicated by a person or organisation | Originating domain/BP-12 |
| Incident | An operational matter managed by police | BP-12 |
| Classification | A taxonomy decision about reported/known conduct | BP-13 |
| Case | A police investigative record | BP-15 |
| Investigative inference | An assessment based on information gathered | BP-16 |
| Intelligence | An assessed information product | BP-21 |
| Evidence | Material handled under evidential rules | BP-22/BP-23/BP-24 |
| Legal finding | A formal adjudicated outcome | BP-28 |

An occurrence can exist without a report, incident, case, known victim, known suspect or police awareness. A report may be inaccurate or incomplete. An incident may combine several occurrences or describe only part of one occurrence. A case may investigate several occurrences. None of these records may be treated as interchangeable.

## 4. Generation architecture

### 4.1 Generation layers
BP-14 must support a layered process:

1. **World conditions:** population, geography, property, businesses, organisations, schedules, resources, relationships, economy, environment and public activity.
2. **Causal pressures:** needs, incentives, conflict, opportunity, vulnerabilities, constraints, disruption and prior consequences.
3. **Actor state:** capability, knowledge, intention, emotional state, resources, access, relationships and risk tolerance.
4. **Event proposal:** a candidate event plan with prerequisites, participants, time window, place and possible outcomes.
5. **Validation:** consistency, identity, population, geography, temporal, resource, causal and canon checks.
6. **Execution:** event steps, state changes, participant actions, interruption, completion or failure.
7. **Consequences:** harm, loss, damage, disruption, witnesses, traces, records, reactions and recovery.
8. **Discovery and awareness:** whether, when and how people or organisations notice the event.
9. **Communication and reporting:** what a person chooses or is able to communicate, to whom and when.
10. **Domain handoff:** publish valid references to BP-11/BP-12/BP-13 and other owning domains.
11. **Persistence and review:** store lineage, state, unresolved consequences and future causal dependencies.

These layers may be executed in one transaction or over multiple simulation ticks. Their conceptual boundaries remain explicit even when implementation combines them.

### 4.2 Candidate event versus committed occurrence
A proposed event is not an occurrence until it passes validation and its authoritative creation transaction commits. Rejected proposals leave no misleading public-facing occurrence, though diagnostic telemetry may record a non-sensitive rejection reason. Committed occurrences receive stable IDs and immutable creation provenance.

### 4.3 Event classes
Support at minimum:
- criminal conduct and attempted criminal conduct;
- suspected but not yet classified criminal conduct;
- interpersonal conflict and threats;
- theft, fraud, deception, exploitation and property damage;
- violence and harm;
- sexual harm and exploitation, represented sensitively and without gratuitous detail;
- organised, coordinated and repeated activity;
- cyber/digital and financial activity;
- traffic, transport and road-safety events;
- missing-person and welfare-related occurrences;
- accidents, injuries, sudden deaths and medical emergencies;
- fires, hazards, infrastructure and environmental incidents;
- business, employment, property and service disputes;
- public disorder, gatherings and event-related disruption;
- emergency-service and institutional occurrences;
- non-crime calls for assistance, false alarms and suspicious circumstances;
- events with no police relevance that nevertheless shape the living world.

This is a capability list, not a final offence catalogue. BP-13 owns the taxonomy vocabulary and BP-04/BP-30 govern supporting world institutions and services.

### 4.4 Occurrence granularity
An occurrence may be a point event, a duration event, a sequence of linked actions, a repeated pattern, a continuing condition or a multi-location event. The system must distinguish a parent occurrence from constituent event steps and separately identifiable occurrences. Splitting or merging must preserve lineage and not erase history.

## 5. Causal model

### 5.1 Causal foundations
Generated occurrences must arise from plausible combinations of:
- actor needs, goals, incentives and pressures;
- capability, knowledge, skills and access;
- relationships, disputes, obligations, trust and conflict;
- opportunity, target exposure and environmental conditions;
- resources, tools, transport, communications and time;
- organisational processes, controls and vulnerabilities;
- prior events, outcomes, unresolved conflict and feedback;
- chance or environmental variation within bounded plausible limits.

No single factor should deterministically imply a crime. Poverty, occupation, relationship, location, demographic attribute or prior suspicion must never function as a shortcut that makes a person criminal by default.

### 5.2 Causal graph
Represent material causal dependencies as a directed acyclic graph for a given event transaction, with explicit temporal feedback represented through later events rather than cycles within one causal evaluation. Nodes may include state facts, decisions, actions, environmental conditions, event steps and consequences. Edges identify causal, enabling, constraining, triggering, contextual or consequential relationships.

The model must distinguish:
- necessary prerequisite;
- contributing factor;
- enabling condition;
- trigger;
- opportunity;
- correlation;
- consequence;
- coincidence;
- unknown relationship.

Correlation alone must not be upgraded to causation. Causal claims record source, confidence, model version and time basis.

### 5.3 Motive, intent and planning
A character may have an intention without acting, act impulsively, change plans, abandon a plan, act under coercion, misunderstand circumstances or have no coherent motive. Motive is not required for every event and must not be fabricated merely to make a narrative complete. Hidden intent belongs to simulated character/world truth; an NPC can communicate only what they plausibly know and choose to disclose.

### 5.4 Opportunity and capability
Event feasibility must account for actual access, skill, physical ability, available tools, money, transport, time, knowledge, security controls and competing obligations. A person cannot be in two incompatible places or perform mutually exclusive actions at the same time unless a recorded mechanism explains it. Capability does not establish participation.

### 5.5 Constraints and counterfactuals
The generator should evaluate relevant constraints: locked access, staff presence, surveillance coverage, travel time, weather, equipment condition, schedules, police presence, witnesses and other known conditions. A counterfactual may be used internally to test whether an event plan is plausible, but must not be exposed as an investigative hint or claim that a different outcome would certainly have occurred.

### 5.6 Causal provenance
Every generated event records the world-state snapshot or version references used, the rules/model version, random seed or deterministic input where applicable, proposal source, validation outcome, actor/participant references, causal parents and resulting state changes. Provenance must be sufficient to explain and replay the event internally without exposing hidden truth to the player.

## 6. Event planning, lifecycle and execution

### 6.1 Lifecycle states
A generated occurrence may use the following configurable states:
- proposed;
- validated;
- scheduled;
- initiated;
- in progress;
- interrupted;
- completed;
- failed;
- abandoned;
- continuing;
- discovered;
- reported;
- referred;
- resolved;
- superseded;
- voided by an authorised correction.

Not every occurrence passes through every state. Discovery, reporting and resolution may overlap with execution or aftermath. State transitions are validated and timestamped. A completed occurrence is not necessarily discovered, reported or resolved.

### 6.2 State-transition requirements
Each transition records occurrence ID, prior state, new state, actor/system, simulation time, event ID, reason, triggering condition, source references and resulting state version. Invalid transitions are rejected. A correction creates a compensating event or superseding version; it does not silently erase the prior state.

### 6.3 Multi-stage occurrences
Support planning, preparation, approach, execution, interruption, escape, concealment, aftermath and follow-on actions where causally appropriate. These are generic event phases, not a mandatory sequence. A single event may be immediate and unplanned; a long-running occurrence may span several simulation periods.

### 6.4 Partial completion
An occurrence may partially complete: some actions succeed, others fail; harm may occur without the intended result; property may be damaged without being taken; a person may intervene; an actor may stop voluntarily. Record each actual step and consequence separately. Do not infer a complete offence merely because a plan existed.

### 6.5 Abandonment and failure
A proposed plan may be abandoned before action, fail due to a constraint, be interrupted by another event or change for a plausible reason. The system must not turn every failed proposal into a police incident. Internal plans that never become observable world activity remain hidden and do not automatically create evidence or reports.

### 6.6 Continuing and recurring events
A continuing condition can generate periodic effects, discoveries and responses while retaining a coherent parent identity. Recurring occurrences may be separate events linked by a pattern or series relationship. Repetition must not be simulated as duplicate copies of one event.

## 7. Actor and participant model

### 7.1 Participant roles
An occurrence may reference one or more participants in contextual roles, including:
- initiator;
- actor;
- accomplice or collaborator;
- intended target;
- affected person;
- injured person;
- property owner or occupier;
- reporter;
- observer;
- witness;
- responder;
- intervener;
- discoverer;
- employer or organisational representative;
- service operator;
- unknown or unresolved participant.

These are occurrence-level participation descriptors, not authoritative police case roles. BP-17 owns victim/witness roles; BP-18 owns suspect/offender statuses; BP-03 owns person identity.

### 7.2 Person identity
Every known person reference must resolve to BP-03's canonical person ID. BP-14 must not create duplicate people or bypass the global population ledger. An unknown participant may remain an unknown participant; do not invent a named identity simply to fill a field.

### 7.3 Permanent promotion
Any person materially connected to an occurrence or related police activity, even peripherally, must be passed to BP-03 for permanent promotion to full persistent simulation under the governing rule. Promotion is idempotent and never reversed. The person's identity, population count and life history remain owned by BP-03. A promotion request must not duplicate a person or increase the living population count.

### 7.4 NPC capability and agency
NPC behaviour must reflect skills, knowledge, temperament, needs, relationships, schedule, fatigue, resources, access, experience and current context. NPCs may make mistakes, hesitate, lie, forget, misunderstand, refuse, intervene or act unexpectedly when plausible. Do not assign omniscient knowledge or perfect rationality.

### 7.5 Organisational participants
Businesses, agencies, employers, service providers and other organisations are referenced by BP-04 canonical IDs. An organisation may be an affected party, scene operator, reporter, responder, negligent actor or context provider. BP-14 does not create shadow organisation records.

## 8. Victim, target, harm and consequence model

### 8.1 Affected parties
An occurrence may affect people, businesses, public institutions, property, infrastructure, community groups or the environment. The affected party may be unknown at creation and identified later. Do not force a named victim where none is known or where the event is non-criminal.

### 8.2 Harm dimensions
Support distinct dimensions:
- physical injury, illness or death;
- psychological and emotional impact;
- sexual harm;
- financial loss and economic disruption;
- property loss or damage;
- coercion, exploitation or deprivation of autonomy;
- service interruption and infrastructure impact;
- environmental damage;
- reputational or organisational impact;
- community safety and public confidence;
- time, access and opportunity loss.

Actual harm, potential harm and perceived harm are separate values. Unknown is not zero. Do not invent numeric severity weights; BP-13/BP-30 own classification descriptors and approved scales.

### 8.3 Consequence timing
Consequences may be immediate, delayed, cumulative or discovered later. A delayed consequence must reference its causal occurrence and record when it became known. Medical deterioration, financial loss discovery, infrastructure failure and relationship fallout must not be backdated as if known earlier.

### 8.4 Consequence propagation
Material consequences may affect employment, business operations, finances, relationships, schedules, service capacity, public events and future opportunities. Propagation must use owning-domain transactions and remain proportionate. Do not create unlimited cascading events from one minor occurrence.

### 8.5 Recovery
Recovery, repair, compensation, treatment, insurance, service restoration, reconciliation or ongoing harm may be modelled as later world events. Recovery does not erase the original event or its history.

## 9. Witnesses, observation and discovery

### 9.1 Potential observers
A person can observe an event only if presence, line of sight, hearing, attention, sensory capability, environmental conditions and timing make observation plausible. Being nearby does not guarantee observation. A camera or sensor has its own coverage, field of view, operation state, time accuracy and retention characteristics.

### 9.2 Perception
Perception records distinguish what was physically available to sense from what the observer actually noticed and interpreted. Lighting, weather, distance, obstruction, stress, distraction, duration, familiarity, language and sensory limitations may affect observation.

### 9.3 Memory
Memory may be incomplete, mistaken, reconstructed, affected by later information or lost over time. Preserve original contemporaneous records separately from later recollection. Do not make all witnesses perfectly consistent or randomly unreliable without causal explanation.

### 9.4 Discovery
An occurrence may be discovered by a participant, neighbour, employee, family member, passer-by, automated system, service provider, patrol officer or later investigation. Discovery time is distinct from event time. Record discovery method, discoverer, observed condition and uncertainty.

### 9.5 Non-discovery
An occurrence may remain undiscovered for a long period or forever. Absence of discovery does not mean absence of occurrence. A hidden event must not generate a police call, witness statement, CCTV retrieval or other player-visible record without a plausible discovery or disclosure path.

## 10. Reporting and information propagation

### 10.1 Reporting choice
A person may report, delay, disclose partially, report anonymously, report to a non-police organisation, tell another person, publish publicly, remain silent or be unable to report. Decisions depend on knowledge, fear, trust, access, incentives, relationships, capacity and perceived risk.

### 10.2 Report content
A report is generated from the reporting person's knowledge and memory, not from omniscient occurrence truth. It may include uncertainty, omissions, errors, hearsay, speculation or deliberate deception. Every claim has a source and information status where the receiving system supports it.

### 10.3 Propagation delay
Information travels through plausible channels and time. A witness may tell a manager, who contacts police later; an organisation may discover a loss during reconciliation; a digital alert may arrive automatically. Do not make every relevant actor immediately aware.

### 10.4 Multiple reports
One occurrence may generate several reports; several occurrences may be described in one report; duplicate reports may arise from the same source. Link source and occurrence relationships without treating duplicate accounts as independent corroboration.

### 10.5 False and mistaken reports
Reports may be mistaken, incomplete, exaggerated, maliciously false or honestly uncertain. The system must distinguish falsity of content from knowledge or intent to deceive. It must not assume a false report is malicious or that an inaccurate reporter is an offender.

### 10.6 Police awareness
An occurrence becomes police-known only through a valid route: call, direct observation, referral, proactive discovery, partner notification, existing case, intelligence or another configured mechanism. No hidden event may silently appear in an officer's knowledge.

## 11. Non-crime and background world generation

### 11.1 Balanced living world
The generator must create ordinary life as well as crime: work, commuting, shopping, appointments, social visits, family responsibilities, leisure, public events, maintenance, service delivery, disputes, accidents and routine changes. A city where every person is constantly involved in crime is not credible.

### 11.2 Non-crime police-relevant occurrences
Support welfare checks, missing-person reports, sudden death attendance, accidents, lost property, hazards, noise concerns, civil disputes, false alarms, service requests, public assistance and suspicious circumstances without an established offence. BP-13 supplies taxonomy concepts; BP-12 owns operational incident records.

### 11.3 Non-police occurrences
Generate relevant business, government, healthcare, education, social care, utility, transport, environmental, food, cultural and community events at proportionate depth. These events can create future police-relevant consequences, but must not be over-simulated into a separate full institutional simulator.

### 11.4 Routine baseline
Maintain schedules and normal operating patterns for people, businesses and services. Deviations from routine can arise naturally and must not automatically be treated as suspicious. Ordinary activity provides context for interpreting unusual events.

### 11.5 Crime frequency and distribution
Crime frequency and type are controlled by world conditions, event models and approved tuning parameters. Avoid arbitrary crime quotas, uniform distribution, repeated identical templates and deterministic targeting of specific demographics or neighbourhoods. No unsupported real-world statistical rate is assumed; initial Saltwater baselines remain configurable decisions.

## 12. Variety, plausibility and anti-repetition

### 12.1 Diversity dimensions
Vary event type, scale, duration, location, participants, relationships, motive, opportunity, method, time, discovery delay, reporting route, consequences, uncertainty and resolution. Variation must remain causally justified rather than decorative randomisation.

### 12.2 Template use
Templates may provide reusable structures, but each committed occurrence must have unique identity, valid participant references, distinct causal lineage, specific time/place constraints and appropriate consequences. Templates are scaffolds, not repeated narrative scripts.

### 12.3 Repetition control
Track recent and historical patterns to prevent implausible repetition. Reuse is allowed when causally plausible, such as a genuine series, recurring dispute, repeated hazard or copycat event. A similarity score alone does not prove common authorship.

### 12.4 Novel events
Support new combinations and emergent events without requiring every occurrence to match a fixed template. Novelty must pass canon, causality, resource, identity and taxonomy validation. Unknown event types may be held for controlled taxonomy review rather than mislabelled.

### 12.5 Narrative variation
Narrative text may vary in wording, but the underlying structured event facts remain authoritative. Narrative must not invent additional participants, times, evidence, injuries, actions or admissions beyond the committed record.

## 13. Event links, patterns and series

### 13.1 Relationship types
Support explicit links including:
- causal parent/child;
- prerequisite/enabling event;
- consequence of;
- continuation of;
- interrupted by;
- repeated pattern;
- suspected series;
- confirmed series under authorised assessment;
- copycat resemblance;
- independent but coincident;
- duplicate/overlapping record;
- split from/merged into;
- discovered through;
- reported by;
- related location or participant.

Each link records type, direction, source, creator/system, time, rationale, confidence and version.

### 13.2 Series truth versus assessment
BP-14 may know whether generated events share a hidden causal actor or plan. Operational users do not automatically know this. BP-16 owns investigative conclusions and BP-21 owns intelligence assessment. A suspected link is not a confirmed common offender.

### 13.3 Multiple actors and coordinated events
Support coordinated actions, accomplices, independent participants, conflicting goals, role changes and unknown participants. Hidden role truth must remain in restricted occurrence data. Public-facing records show only discovered or lawfully/appropriately communicated information.

### 13.4 Split and merge
Splitting or merging occurrence records requires explicit lineage, rationale, effective time and references to the original IDs. Existing reports, incidents, cases and evidence links remain attributable to their original sources and are reconciled through explicit relationships.

## 14. Geography, movement and access

### 14.1 Canonical spatial references
Every physical event location, route, premises, entrance, room, road segment and relevant zone must resolve through BP-02. Businesses and properties resolve through BP-04. BP-14 must not invent addresses or duplicate spatial entities.

### 14.2 One-city constraint
Saltwater is one sovereign city-state, one city and one jurisdiction. No generation may create another playable city, external district, border expansion or second police jurisdiction. Off-map dependencies may be represented abstractly where canon permits, without adding playable geography.

### 14.3 Movement feasibility
Movement must account for origin, destination, route, travel mode, speed, traffic, access restrictions, transport availability and time. A person cannot teleport or traverse impossible routes. The system must support uncertainty in estimated travel times and distinguish estimated from observed movement.

### 14.4 Access and occupancy
Event plans must respect ownership, tenancy, occupancy, keys, locks, alarms, permissions, opening hours, staff presence and access-control records. An unauthorised entry may occur through a plausible mechanism; the mechanism must be recorded in hidden truth and not invented retrospectively to fit a theory.

### 14.5 Digital and remote activity
Digital occurrences may involve Saltwater people, organisations, devices or services without a physical Saltwater scene. Record the relevant logical systems and affected canonical entities. Do not invent off-map physical details or infer a real-world origin without a supported in-world source.

## 15. Time, schedules and event ordering

### 15.1 Shared clock
BP-37 owns the authoritative simulation clock. BP-35 owns event scheduling and execution. BP-14 consumes canonical time and must not maintain an independent clock.

### 15.2 Time freeze
No simulation time advances while the player is outside the simulation or the game is paused under the governing rule. Occurrence plans, NPC actions, event queues, discovery, reporting, consequences, schedules and background activity all freeze. On resume, continue from the exact saved state; do not catch up wall-clock time.

### 15.3 Temporal validity
Every event records event time, recorded time and, where relevant, discovery/report time. Distinguish exact, estimated, bounded and unknown time. Use consistent timezone and ordering rules. Do not silently replace an estimated time with a precise timestamp.

### 15.4 Concurrent events
Support simultaneous and overlapping occurrences with deterministic ordering for conflicting state mutations. If two events compete for one resource, location, person or asset, apply explicit priority and transaction rules; do not permit impossible double allocation.

### 15.5 Schedule interactions
Events may arise from or disrupt shifts, opening hours, appointments, public events, transport timetables and service schedules. A schedule is a constraint or context, not proof that a person attended. Attendance and actual movement are separate records.

## 16. Economy, organisations and service dependencies

### 16.1 Economic causality
Events may arise from or affect income, debts, contracts, stock, supply chains, payroll, deliveries, insurance, business continuity and public finance. Use BP-04 and other domain records as authoritative sources. Do not fabricate unbalanced transactions or duplicate assets.

### 16.2 Business diversity
Saltwater maintains at least 10,000 businesses under BP-04. Occurrences must reuse canonical business IDs and create plausible variety across sectors, scale, ownership, premises and operating patterns. Business count must not increase because an event creates a duplicate reference.

### 16.3 Service dependencies
Utilities, transport, communications, healthcare, education, social care, emergency services and other institutions can create or experience disruptions. Model only dependencies established by the world configuration. A service outage affects connected systems/areas, not arbitrary unrelated locations.

### 16.4 Institutional events
Public institutions and organisations may make decisions, fail, investigate, report, provide assistance or generate records. Actions require plausible authority, actor and chronology. BP-14 models the occurrence and consequences; BP-30 and other owning domains retain governance and institutional records.

## 17. NPC knowledge, beliefs and behaviour

### 17.1 Knowledge boundaries
Every NPC's knowledge must be limited by observation, communication, records they can access, role, training and time. No NPC may know hidden occurrence truth merely because the simulation engine knows it.

### 17.2 Belief states
An NPC may hold a belief, suspicion, misconception, uncertainty or false memory. Belief is not fact. Store source and acquisition time where materially relevant. A character's confidence may be mistaken.

### 17.3 Communication
NPCs communicate only through plausible channels and at plausible times. Messages, calls, conversations and reports must reference participants, channel, time, content source and access boundaries. A person cannot disclose a fact they have not learned.

### 17.4 Decision behaviour
NPC decisions reflect goals, knowledge, personality, relationships, resources, fatigue, incentives, pressure and risk. Do not make every NPC optimally rational or randomly irrational. Consequential choices should have traceable causal context.

### 17.5 Deception and concealment
Some actors may lie, conceal, destroy, alter or withhold information as part of generated truth. This must be causally plausible and remain hidden unless discovered. Do not turn concealment into automatic evidence of guilt; preserve alternative explanations.

### 17.6 No player guidance leakage
NPC actions, dialogue, generated messages and occurrence summaries must not tell the player what to investigate next, identify the hidden culprit, or imply a solution. Present records and observable behaviour; player agency controls investigative choices.

## 18. Hidden truth and information security

### 18.1 Separate truth layers
Maintain separate, access-controlled representations for:
- authoritative world/occurrence truth;
- participant knowledge and belief;
- witness perception and memory;
- reported information;
- police operational knowledge;
- investigative assessments;
- intelligence assessments;
- evidence and forensic results;
- legal allegations and adjudicated findings;
- player-visible presentation.

These layers may reference one another but must never collapse into a single omniscient narrative object.

### 18.2 Exact reveal gate
The identity of a hidden culprit, perpetrator or accomplice must never be revealed unless the player types exactly `bingo`, in accordance with BP-01. Case truth must not leak through partial matches, case-insensitive variants, punctuation changes, whitespace, autocomplete, metadata, IDs, error messages, analytics, NPC dialogue or generated hints.

### 18.3 No indirect reveal
Before the exact trigger, do not reveal hidden identity indirectly through unique descriptors, narrative emphasis, unusual category labels, generated names, causal explanations, event ordering, model confidence, search suggestions or a combination of otherwise innocuous fields.

### 18.4 Role-scoped access
The omniscient simulation engine may access hidden truth for causal consistency. Operational NPCs, police records, AI narrative, player interface and analytics receive only authorised views. Service identities are least-privileged and all access is auditable.

### 18.5 Testing the boundary
Every release must test direct and indirect leakage paths, including search, exports, notifications, logs, exception text, model prompts, cached summaries and replay tools. A failed concealment test blocks release.

## 19. Generation controls and balancing

### 19.1 Configuration
Generation parameters must be stored in versioned configuration, not scattered code constants. Parameters may include event-family weights, temporal windows, diversity constraints, population relevance thresholds, resource limits, discovery delays, reporting probabilities and processing budgets.

### 19.2 No arbitrary quotas
Do not force a fixed number of crimes, calls, victims or arrests per day or shift unless an explicitly approved scenario requires it. Generation should respond to world conditions and configured baselines.

### 19.3 Fairness and non-determinism
Do not use protected or sensitive personal traits as simplistic predictors of criminality. Avoid deterministic neighbourhood stigma, demographic shortcuts and repeated targeting. Any use of traits in a causal model requires a defensible in-world mechanism, explicit approval and testing for unintended bias.

### 19.4 Difficulty and player progression
Generation may adapt to game scenario, player career stage or approved difficulty settings, but must not manipulate event truth to punish or reward the player, force a particular investigation, guarantee a culprit or produce impossible cases. Player progression does not make the world omnisciently responsive to the player's desires.

### 19.5 Scenario mode
Explicit scenario content may seed a known occurrence or event chain. Scenario seeding must use the same identity, causality, chronology, population, geography and concealment rules as procedural generation. It must be labelled internally as scenario-originated and remain hidden from the player unless the scenario design exposes it.

## 20. Persistence, identity and data model

### 20.1 Core entities
The design must support at least:
- Occurrence;
- OccurrenceVersion;
- EventProposal;
- EventExecution;
- EventStep;
- CausalLink;
- ParticipantLink;
- OccurrenceLocationLink;
- OccurrenceAssetLink;
- OccurrenceConsequence;
- HarmAssessment;
- PerceptionRecord;
- DiscoveryRecord;
- ReportTrigger;
- OccurrenceRelationship;
- SeriesLink;
- WorldStateReference;
- GenerationRuleVersion;
- GenerationRun;
- GenerationDecision;
- Randomness/ReplaySeedReference;
- HiddenTruthRecord;
- KnowledgeExposureRecord;
- EventOutboxRecord;
- ReconciliationRecord.

### 20.2 Stable IDs
Every committed occurrence, event step and causal relationship receives a stable, unique, non-reusable ID. IDs do not encode culprit identity, offence category in a way that leaks hidden truth, location-sensitive data or secrets. Split/merge and correction preserve all predecessor IDs.

### 20.3 Minimum occurrence fields
Each occurrence supports:
- occurrence ID and schema version;
- occurrence type and BP-13 taxonomy reference where applicable;
- lifecycle state;
- start/end time or bounded time interval;
- recorded/created time;
- canonical location references or explicit non-physical/digital context;
- participant references and contextual roles;
- affected entities and assets;
- parent/child and causal links;
- event steps and actual outcomes;
- consequences and harm references;
- discovery and reporting state;
- generation rule/model version;
- world-state input references;
- provenance, confidence and uncertainty;
- hidden-truth access classification;
- correction/supersession links;
- audit and retention metadata.

### 20.4 Immutable history
Committed event facts are not silently overwritten. Corrections use append-only events or versioned supersession with reason and actor. Derived summaries may be rebuilt, but source facts and lineage remain recoverable.

### 20.5 Lossless narrative
Narrative records that carry meaningful facts must be preserved losslessly or represented as structured claims with source references. Compression may reduce structural overhead but must not remove meaning, uncertainty, provenance, chronology or distinctive details.

## 21. Event execution, transactions and idempotency

### 21.1 Atomicity
A committed occurrence creation must atomically establish its stable identity, initial state, provenance and required outbox event. Multi-domain consequences use reliable transaction/outbox patterns and explicit pending states. No partial commit may leave an event appearing completed while its mandatory world-state effects are missing.

### 21.2 Idempotency
Every generation request and downstream event has an idempotency key. Retries must not create duplicate occurrences, duplicate participants, duplicate harm or duplicate reports. A repeated request with conflicting payload is rejected or quarantined.

### 21.3 Ordering and concurrency
Concurrent generation processes must not allocate the same unique ID or mutate a person, property, resource or location into impossible simultaneous states. Use transaction isolation, conflict detection and deterministic resolution rules.

### 21.4 Failure handling
If a dependency is unavailable, preserve the event proposal or committed occurrence with explicit pending consequences. Do not claim a notification, report, dispatch or external state change succeeded until the owning domain acknowledges it.

### 21.5 Replay
Where deterministic replay is required, preserve inputs, configuration/model versions, seeds, ordering and external domain responses. Replay must reproduce the authoritative state without re-sending real side effects or duplicating records.

## 22. Processing tiers, scale and relevance

### 22.1 Relevance-based processing
The world may use different processing frequency/detail for distant or inactive entities, but relevance optimisation must never delete identities, established facts, event lineage or obligations. Low-frequency processing may defer non-critical activity; it may not rewrite history.

### 22.2 Promotion triggers
Material connection to police activity or an occurrence triggers permanent full-detail promotion through BP-03. Examples include a participant, affected person, observer, reporter, discoverer, relevant employee, linked owner, responder or person whose actions materially shape a case. The threshold must be applied consistently and conservatively.

### 22.3 No downgrade
Once promoted, a person remains full persistent simulation for the remainder of the game. Relevance may change processing priority but never reverses promotion or deletes established records.

### 22.4 Population cap
The global hard cap is 10,000 living people total. Police personnel and all other people are included once in the same count. BP-14 cannot create a person outside BP-03's atomic capacity check. If the cap is reached, the relevant admission/replacement rules are handled by BP-03; BP-14 must not bypass them by using placeholders or duplicate identities.

### 22.5 Business count
Saltwater must maintain at least 10,000 businesses under BP-04. Event generation references existing canonical businesses or submits a controlled creation request to BP-04; it does not create duplicates to satisfy an occurrence.

### 22.6 Bounded workload
Generation budgets, queue limits and processing intervals are configuration decisions. Overload must defer or prioritise work transparently, not silently drop committed events or advance simulation time while paused.

## 23. Interfaces and ownership contracts

### 23.1 Inputs
BP-14 consumes:
- BP-01: canon, player-agency and concealment invariants;
- BP-02: canonical spatial world, boundaries, routes and premises references;
- BP-03: people, life state, schedules, attributes and population admission/promotion responses;
- BP-04: property, businesses, organisations, employment, services and assets;
- BP-05 through BP-10: police organisation, personnel, resources, patrol presence and operational context where authorised;
- BP-11/BP-12: police awareness and operational feedback, not occurrence truth;
- BP-13: taxonomy entries, descriptors and classification constraints;
- BP-15/BP-16: case/investigative discoveries as feedback into world consequences only through permitted references;
- BP-17/BP-18: role/status references where permitted, without taking ownership;
- BP-19/BP-21/BP-22/BP-23/BP-24: discovered information and evidence references, not authority to rewrite occurrence truth;
- BP-30/BP-36: institutional configuration and social relationship context;
- BP-35/BP-37: event execution, scheduling and canonical time;
- BP-38/BP-39/BP-42/BP-44: records, persistence, permissions and approved configuration.

All inputs must be schema-validated, source-attributed and versioned. A downstream police record cannot be used as the sole source to retroactively alter hidden truth.

### 23.2 Outputs
BP-14 publishes:
- occurrence created/updated/superseded events;
- event-step and state-transition records;
- causal lineage and participant/location links;
- consequence and world-state change requests;
- discovery and reporting triggers;
- taxonomy references for BP-13 classification;
- valid police-awareness/referral triggers for BP-11/BP-12;
- person-promotion requests for BP-03;
- organisation/property/service effect requests for BP-04 and owning domains;
- replay/provenance references;
- non-sensitive quality and operational telemetry.

### 23.3 Event envelope
Every cross-domain event includes event ID, schema version, event type, source domain and record ID, target/reference IDs, canonical simulation time, recorded time, correlation ID, idempotency key, actor/service identity, provenance, access classification and causality references.

### 23.4 Ownership
BP-14 owns occurrence truth and generation lineage. BP-03 owns people; BP-02 geography; BP-04 businesses/property/organisations; BP-13 taxonomy; BP-12 incidents; BP-15 cases; BP-16 investigative actions; BP-35 engine; BP-37 time. Reconciliation must respect these boundaries.

## 24. Reporting, analytics and quality monitoring

Provide internal and authorised reporting for:
- occurrences by type, state, time, location and causal family;
- criminal versus non-criminal occurrence counts, separately from BP-13 classifications;
- reported, unreported, discovered and undiscovered events;
- discovery and reporting delays;
- participant and affected-entity counts;
- consequences and recovery;
- event generation rate and proposal rejection reasons;
- repeated templates and diversity;
- causal integrity and invalid state transitions;
- processing queue health and deferred work;
- event-to-incident/case referral reconciliation;
- hidden-truth access and leakage test results.

Every report must define its unit of count, filters, time basis, taxonomy/model version and deduplication rules. Player-facing reports must not disclose hidden truths or reveal investigation directions. Analytics are derived views, not authoritative event records.

## 25. Error handling and degraded operation

Handle missing person/property/location references, capacity rejection, invalid schedules, impossible travel, conflicting event proposals, unavailable dependencies, queue overload, duplicate requests, stale configuration, time anomalies, failed consequence delivery, broken causal links, corrupt replay inputs and access denial.

- Reject impossible proposals with an attributable reason.
- Preserve committed occurrence state if a downstream service is temporarily unavailable.
- Mark incomplete consequences as pending; never claim they succeeded.
- Do not fabricate replacement people, businesses, addresses, evidence or reports.
- Do not expose hidden truth in diagnostic errors.
- Retry idempotently and reconcile acknowledgements.
- Do not advance the simulation clock to clear a backlog while the player is absent.
- Quarantine irreconcilable events for controlled review.
- A failed event transaction must not leave a partial occurrence.
- A restore must recover committed events and their causal lineage.

## 26. Acceptance criteria

1. Occurrences arise from plausible world conditions and causal relationships.
2. Crime and non-crime activity are both generated.
3. Event proposals are distinct from committed occurrences.
4. Every committed occurrence has a stable unique ID and immutable provenance.
5. Occurrence truth, perception, memory, report, incident, classification, case, intelligence, evidence and court finding remain distinct.
6. Actor participation and consequences reflect plausible capability, access, time, resources and constraints.
7. One event can have multiple participants, stages, sites and consequences.
8. Attempted, interrupted, abandoned, failed, completed and continuing events are supported.
9. Events may remain undiscovered, unreported or unknown to police.
10. Reporting content reflects the reporter's knowledge and memory, not omniscient truth.
11. Discovery time and report time remain distinct from event time.
12. Witness observation and memory reflect plausible conditions.
13. Consequences propagate through owning domains without duplicate or unbounded cascades.
14. NPC knowledge never exceeds plausible information and access.
15. Hidden occurrence truth is inaccessible to operational actors and player-facing systems unless discovered through valid routes.
16. Exact `bingo` reveal gate is preserved; no direct or indirect leak before it.
17. No unsolicited investigative hints or directions are generated.
18. Person identities reuse BP-03; materially relevant people are permanently promoted.
19. The 10,000 living-person hard cap is enforced atomically and globally.
20. At least 10,000 businesses remain canonical BP-04 entities, without duplicate event-created businesses.
21. All physical locations and routes resolve through BP-02.
22. No external playable city or jurisdiction is created.
23. BP-13 owns taxonomy and formal classification; BP-14 does not redefine it.
24. BP-12 owns police incident records; BP-14 does not fabricate dispatch or incident closure.
25. BP-35/BP-37 own engine execution and time; player absence freezes all simulation activity.
26. Causal links, event steps and consequences are traceable and replayable as configured.
27. Generation is varied and avoids arbitrary quotas, deterministic targeting and repeated templates.
28. Failed downstream delivery remains pending and recoverable.
29. Cross-domain events are schema-valid, versioned, attributable and idempotent.
30. Every mapped source requirement, test and cross-cutting invariant is traceable.
31. Implementation, testing and verification remain separate statuses.
32. No Neon write is authorised by this specification.

## 27. Acceptance test catalogue

| Test ID | Scenario | Expected result |
|---|---|---|
| CG-001 | Generate a valid candidate event | Proposal created with causal inputs and version |
| CG-002 | Candidate violates canon | Rejected before occurrence commit |
| CG-003 | Candidate references unknown person | Rejected or held; no person invented |
| CG-004 | Candidate references duplicate person identity | Canonical BP-03 identity reused |
| CG-005 | Candidate references unknown location | Rejected or unresolved; no address fabricated |
| CG-006 | Candidate references valid business | Canonical BP-04 business reused |
| CG-007 | Candidate passes validation | Stable occurrence ID and provenance committed atomically |
| CG-008 | Event transaction fails before commit | No partial occurrence visible |
| CG-009 | Same generation request retried | Idempotent; no duplicate occurrence |
| CG-010 | Same idempotency key has conflicting payload | Rejected/quarantined |
| CG-011 | Event proposal is abandoned before action | No completed occurrence or police report generated |
| CG-012 | Event begins but is interrupted | Actual steps and interruption recorded |
| CG-013 | Event partly succeeds | Successful and failed steps separately represented |
| CG-014 | Event completes | Completion state and consequences recorded |
| CG-015 | Event continues across simulation periods | One coherent continuing occurrence |
| CG-016 | Repeated events occur independently | Separate IDs with explicit pattern links if justified |
| CG-017 | One occurrence has multiple stages | Ordered event steps preserve chronology |
| CG-018 | One occurrence has multiple physical locations | Every location resolves to BP-02 |
| CG-019 | One occurrence has several participants | Participant links and contextual roles preserved |
| CG-020 | Unknown participant is involved | Unknown reference retained; no fabricated identity |
| CG-021 | Person is materially connected peripherally | BP-03 permanent promotion requested |
| CG-022 | Promotion request delivered twice | Idempotent; one person and one population count |
| CG-023 | Person is already promoted | No downgrade or duplicate profile |
| CG-024 | Population already at 10,000 living people | BP-03 capacity rules apply; no cap bypass |
| CG-025 | Police officer participates in occurrence | Counted once within total population |
| CG-026 | Event references one of 10,000+ businesses | Existing business ID reused |
| CG-027 | Event attempts to create duplicate business | BP-04 rejects duplicate or handles approved merge |
| CG-028 | Actor lacks required access | Event plan rejected or alternative mechanism causally recorded |
| CG-029 | Actor lacks capability | Impossible action rejected or failure represented plausibly |
| CG-030 | Actor has competing appointment | Schedule conflict resolved; no impossible simultaneous state |
| CG-031 | Travel time is too short | Candidate rejected or timeline corrected before commit |
| CG-032 | Locked premises entered | Valid access mechanism exists in hidden event truth |
| CG-033 | Premises occupancy conflicts | Conflict detected and reconciled |
| CG-034 | Surveillance device is offline | No recording falsely generated for unavailable interval |
| CG-035 | Camera has blind spot | Event not automatically visible in that coverage |
| CG-036 | Witness is nearby but distracted | Observation not guaranteed |
| CG-037 | Witness has obstructed view | Perception reflects obstruction |
| CG-038 | Poor lighting/weather affects perception | Observation quality reflects actual conditions |
| CG-039 | Witness misremembers time | Memory remains distinct from event timestamp |
| CG-040 | Witness receives later information | Later recollection/source influence is recorded |
| CG-041 | No observer is present | No invented witness statement |
| CG-042 | Event remains undiscovered | No discovery or report generated |
| CG-043 | Event is discovered days later | Discovery time differs from occurrence time |
| CG-044 | Discovery occurs through automated alert | Device/system and coverage provenance recorded |
| CG-045 | Reporter only knows part of event | Report contains only plausible known information |
| CG-046 | Reporter makes honest mistake | Inaccuracy does not automatically imply deception |
| CG-047 | Reporter knowingly lies | Hidden intent and reported claim remain separate |
| CG-048 | Anonymous report is submitted | Reporter identity remains unknown where genuinely unavailable |
| CG-049 | Several people report same occurrence | Multiple report links; no false independent corroboration |
| CG-050 | One report describes multiple occurrences | Separate occurrence links supported |
| CG-051 | One occurrence is never reported to police | No automatic police awareness |
| CG-052 | Non-police organisation receives report first | Plausible delay and referral path recorded |
| CG-053 | Police directly observe occurrence | Awareness arises through valid BP-10/BP-12 path |
| CG-054 | Event is criminal but not yet classified | Occurrence exists; BP-13 classification remains separate |
| CG-055 | Event is non-criminal | Valid occurrence without forced offence classification |
| CG-056 | Welfare concern generated | Non-crime event and possible support referral |
| CG-057 | Accident causes injury | Harm and event facts recorded without assuming crime |
| CG-058 | False alarm occurs | Non-crime occurrence; no fabricated underlying offence |
| CG-059 | Suspicious circumstance has no established offence | Uncertainty preserved |
| CG-060 | Business suffers stock loss | BP-04 stock and financial effects reconcile |
| CG-061 | Utility outage causes downstream disruption | Only connected assets/areas affected |
| CG-062 | Transport disruption affects travel | Movement and arrival estimates adjust consistently |
| CG-063 | Environmental hazard occurs | Location/time-valid impact and response references |
| CG-064 | Public event creates crowd and traffic effects | Attendance and spatial constraints remain plausible |
| CG-065 | Healthcare response follows injury | Referral and care records remain owned by healthcare domain |
| CG-066 | Occurrence creates financial loss | No unbalanced transaction or duplicate asset |
| CG-067 | Delayed harm becomes apparent | Discovery time and causal occurrence linked |
| CG-068 | Recovery follows damage | Recovery event does not erase original occurrence |
| CG-069 | Consequence propagation creates loop | Causal loop blocked or represented as later event chain |
| CG-070 | Minor event would trigger excessive cascade | Bounded propagation prevents unbounded event explosion |
| CG-071 | Similar method appears in two events | Similarity does not prove common actor |
| CG-072 | True common actor links two generated events | Hidden series truth retained; operational assessment remains separate |
| CG-073 | Copycat event occurs | Similarity link distinct from shared authorship |
| CG-074 | Coordinated event involves accomplices | Hidden participant roles recorded with access restrictions |
| CG-075 | One actor changes plan mid-event | New event step and causal decision recorded |
| CG-076 | Actor abandons plan | Abandonment is not falsely represented as completed offence |
| CG-077 | Actor is coerced | Coercion represented as causal context, not erased |
| CG-078 | Event occurs without clear motive | Motive remains unknown |
| CG-079 | NPC has not learned hidden fact | NPC cannot use or communicate it |
| CG-080 | NPC receives valid information later | Knowledge update time and source recorded |
| CG-081 | NPC lies about known event | Belief/knowledge and communicated claim remain distinct |
| CG-082 | NPC misinterprets an observation | Interpretation differs from raw perception |
| CG-083 | AI generates narrative from occurrence | No facts beyond committed structured record |
| CG-084 | AI suggests investigative action | Unsolicited investigation hint is suppressed |
| CG-085 | Player views event summary | Hidden perpetrator/accomplice identity remains concealed |
| CG-086 | Player enters near-match to bingo | Reveal gate remains closed |
| CG-087 | Player enters exact bingo | Only governing reveal mechanism is invoked |
| CG-088 | Hidden identity appears in generated ID | Validation rejects/leak test fails |
| CG-089 | Hidden truth appears in error/log/export | Access filter blocks disclosure |
| CG-090 | Operational officer queries generator-only field | Access denied and audited |
| CG-091 | Player exits while event is scheduled | No simulation-time progression |
| CG-092 | Player is absent while NPC action is queued | Queue and world state remain frozen |
| CG-093 | Player resumes simulation | Exact saved state resumes; no catch-up |
| CG-094 | Two events compete for one asset | Explicit concurrency rule prevents double allocation |
| CG-095 | Two events attempt conflicting occupancy changes | Transaction conflict handled consistently |
| CG-096 | Event arrives out of order | Canonical event time and lineage preserved |
| CG-097 | Downstream incident service unavailable | Referral remains pending; occurrence persists |
| CG-098 | Downstream delivery retried | No duplicate incident/report |
| CG-099 | Replay a deterministic event sequence | Authoritative state reproduces under defined conditions |
| CG-100 | Replay attempts external side effect | Side effect is suppressed or safely simulated |
| CG-101 | Configuration changes between proposal and execution | Version rule determines valid behaviour |
| CG-102 | Taxonomy entry is retired | BP-13 governs classification; occurrence history remains |
| CG-103 | Event uses external context | No additional playable city or jurisdiction created |
| CG-104 | Digital occurrence affects Saltwater organisation | Logical target recorded without fabricated physical scene |
| CG-105 | Person dies in an occurrence | BP-03 life-state transaction and population ledger reconcile |
| CG-106 | Person permanently exits city | BP-03 lifecycle rules apply; no direct population mutation |
| CG-107 | Occurrence references several organisations | Canonical IDs reused; ownership preserved |
| CG-108 | Generation uses demographic attribute | No prohibited deterministic criminality shortcut |
| CG-109 | Generation weights change | Versioned configuration and impact evidence recorded |
| CG-110 | High event load exceeds budget | Work deferred transparently; committed events not dropped |
| CG-111 | Repetition detector sees recurring legitimate dispute | Recurrence allowed with causal links |
| CG-112 | Repetition detector sees duplicate template output | Duplicate proposal blocked or flagged |
| CG-113 | New event combination is not in template library | Novel candidate validated under generic constraints |
| CG-114 | Scenario seed creates an event | Same canon, identity, time and concealment rules apply |
| CG-115 | Event has no known affected person | No fabricated victim identity |
| CG-116 | Event affects business and person | Separate affected-entity references preserved |
| CG-117 | Reported time is an interval | Interval and uncertainty preserved |
| CG-118 | Clock changes or pause occurs | BP-37 time contract remains authoritative |
| CG-119 | Occurrence correction is needed | Superseding record preserves old version and rationale |
| CG-120 | Source world-state reference is stale | Proposal revalidated or rejected |
| CG-121 | A participant reference is invalidated by correction | Historical reference retained and current status reconciled |
| CG-122 | Event has several independent causes | Causal graph supports multiple parent nodes |
| CG-123 | Correlation is mistaken for causation | Relationship remains non-causal until supported |
| CG-124 | Causal graph would contain a cycle | Invalid same-transaction cycle rejected |
| CG-125 | Delayed consequence creates later event | Explicit parent-child causal relationship stored |
| CG-126 | Event is split into two occurrences | Both new records link to original lineage |
| CG-127 | Two occurrence records are merged | Original IDs retained and merge audited |
| CG-128 | A false report is withdrawn | Report lifecycle belongs to source domain; occurrence truth unchanged |
| CG-129 | A court outcome contradicts earlier belief | BP-28 outcome linked; occurrence history not rewritten |
| CG-130 | Intelligence links two occurrences | BP-21 assessment remains separate from hidden truth |
| CG-131 | Evidence later supports event reconstruction | BP-23/BP-24 own evidence and forensic records |
| CG-132 | A person is peripheral but material to case | Permanent BP-03 promotion occurs |
| CG-133 | Person is already counted as police and resident | Population ledger counts one living person |
| CG-134 | City has exactly 10,000 living people | Generation cannot exceed cap |
| CG-135 | Business registry exceeds 10,000 records | Occurrences reuse existing canonical businesses |
| CG-136 | Database restoration occurs | Occurrence, lineage, event steps and provenance reconcile |
| CG-137 | Audit write fails | Event transaction does not partially commit |
| CG-138 | Permissions change after occurrence creation | Historical access is governed by current policy; audit remains |
| CG-139 | Hidden truth is queried through analytics | Restricted fields excluded |
| CG-140 | Full source conformance audit runs | S29.R02, S29.T01, S05.R03, S15.R03, S21.R02, S28.R03, S40.R03, S42.R01–R04, S43.R01–R05, P07, X09 and A06 traceability is evidenced |

## 28. Edge cases and failure scenarios

1. A proposed event has no plausible causal trigger.
2. An event is plausible but conflicts with a participant's schedule.
3. An actor has a motive but no capability or opportunity.
4. An actor has opportunity but no intention to act.
5. A plan is prepared but abandoned before any observable action.
6. An attempt begins but fails before the intended outcome.
7. An occurrence is interrupted by a witness, alarm, outage or unrelated event.
8. An occurrence partly succeeds and partly fails.
9. An occurrence continues over several simulation periods.
10. One continuous condition causes several separately identifiable consequences.
11. A single occurrence has multiple victims or affected organisations.
12. A single occurrence has no identifiable victim at creation.
13. An affected person is identified only after later discovery.
14. An occurrence has no known perpetrator.
15. An occurrence has multiple actors with different levels of participation.
16. A participant's role changes during the event.
17. An accomplice is hidden from other participants.
18. A participant is coerced or deceived by another actor.
19. A person is falsely implicated by another participant.
20. A person is present but does not observe the event.
21. A person observes only a fragment.
22. A witness has a sensory or language limitation.
23. Weather, lighting, noise or obstruction changes perception.
24. A witness's memory changes after discussion with another person.
25. Several reports derive from one original source.
26. A reporter deliberately lies for reasons unrelated to the underlying occurrence.
27. A reporter honestly misidentifies a person or time.
28. A reporter delays because of fear, loyalty, shame or uncertainty.
29. A person reports to an employer or service provider rather than police.
30. An occurrence is discovered by routine audit rather than a witness.
31. An occurrence remains undiscovered indefinitely.
32. An occurrence is discovered long after its physical traces have changed.
33. A camera is installed but not recording.
34. A camera records but its clock is inaccurate.
35. A sensor detects an event but its interpretation is wrong.
36. A person is nearby but behind an inaccessible boundary.
37. An access mechanism is plausible but not known to police.
38. A key or credential is shared, borrowed, copied or revoked.
39. Occupancy records are incomplete or stale.
40. A business is temporarily closed but an authorised person is present.
41. A person is scheduled to work but is absent.
42. A vehicle route is blocked or unavailable.
43. Travel time changes due to traffic or weather.
44. A person attempts two incompatible actions at once.
45. Two events compete for the same person, room, vehicle or equipment.
46. A service outage affects only part of the city.
47. A utility dependency is incorrectly assumed for an unconnected building.
48. A business disruption causes delayed financial or employment consequences.
49. A healthcare outcome is delayed or uncertain.
50. A death or serious injury changes population and relationship records.
51. A person permanently leaves or enters the city during a pending event.
52. The population cap is reached before a new relevant person is discovered.
53. A peripheral person becomes materially connected to a case.
54. The same person appears in multiple role contexts.
55. A business is both target and reporter in separate linked events.
56. A non-crime hazard is incorrectly generated as criminal conduct.
57. A crime occurrence is generated but no valid BP-13 category exists.
58. A new taxonomy version becomes active while an occurrence is in progress.
59. A digital occurrence affects a local account but has no known physical origin.
60. An external event is referenced without expanding Saltwater's playable geography.
61. A series is suspected but events are actually independent.
62. Events share an actor but differ in method and target.
63. A copycat imitates a method without common authorship.
64. Several actors coordinate but do not share all information.
65. A generated event accidentally repeats a prior narrative template.
66. A generation model produces an implausible crime cluster.
67. A generation model systematically targets one neighbourhood or group.
68. A low-probability event is generated too frequently by repeated retries.
69. A high-probability event is suppressed by a duplicate detector.
70. A candidate proposal becomes invalid before execution.
71. A world-state update occurs between validation and commit.
72. A dependency service is unavailable during event execution.
73. A consequence is delivered twice after retry.
74. A consequence is delivered out of order.
75. A generation process crashes after creating an event ID but before commit.
76. A transaction commits but the acknowledgement is lost.
77. A replay uses a different model/configuration version.
78. A replay re-sends a notification or creates duplicate police incident.
79. A causal link points to a missing or superseded event.
80. A correction is attempted after a downstream case has closed.
81. An event is split after reports and exhibits have been linked.
82. Two event records are merged despite having different causal truth.
83. A derived summary contains more certainty than the source records.
84. An AI narrative invents a witness, injury, time or admission.
85. An NPC uses hidden generator knowledge in dialogue.
86. Hidden identity leaks through a generated identifier or filename.
87. Hidden identity leaks through search ranking or autocomplete.
88. Hidden truth appears in error messages, logs or telemetry.
89. An authorised engine query is mistakenly exposed to player role.
90. A player types a near-match rather than exact `bingo`.
91. A player exits while events are queued.
92. A paused simulation receives a wall-clock callback.
93. A background process attempts to catch up elapsed real time.
94. A generation backlog grows beyond configured capacity.
95. A deferred event is lost during restart.
96. A backup omits hidden-truth records or causal lineage.
97. A restore creates duplicate occurrences.
98. A person promotion is committed but the occurrence transaction fails.
99. A population count is incremented twice by concurrent events.
100. A business reference is duplicated to bypass registry constraints.
101. A person is counted once as resident and again as police.
102. An occurrence creates an organisation that should already exist.
103. An environmental condition is applied outside its valid location/time.
104. A schedule is treated as proof of attendance.
105. A location estimate is displayed as a precise observation.
106. A crime count includes reports and incidents as if each were separate offences.
107. A court outcome is used to rewrite occurrence truth retroactively.
108. An intelligence assessment is treated as generator truth.
109. A false report is treated as proof that no occurrence happened.
110. An unreported occurrence is treated as nonexistent.
111. A completed occurrence is incorrectly assumed to be discovered.
112. A discovered occurrence is incorrectly assumed to be reported to police.
113. A route recommendation is treated as a dispatch acknowledgement.
114. A non-police event is overdeveloped beyond supporting-world scope.
115. A routine activity is incorrectly flagged as suspicious solely due to location.
116. A demographic trait is used as a deterministic crime predictor.
117. A character's past suspicion is treated as proof of a new occurrence.
118. A player career level changes event truth to force a challenge.
119. A scenario seed bypasses normal validation.
120. A hidden truth is accidentally copied into a player-visible snapshot.

## 29. Dependencies and ownership matrix

| Domain | BP-14 interface | Authority retained |
|---|---|---|
| BP-01 | Canon, player agency, concealment and game rules | Governing invariants |
| BP-02 | Location, routes, premises and spatial constraints | Canonical geography |
| BP-03 | Person IDs, life status, schedules and promotion | Person identity and population |
| BP-04 | Businesses, property, organisations, assets and services | World entity registry |
| BP-05–BP-09 | Police presence, personnel, resources and organisational context | Police architecture/resources |
| BP-10 | Patrol presence and direct observation | Field operations |
| BP-11 | Call and communication pathways | Intake and dispatch |
| BP-12 | Police incident records and operational awareness | Incident lifecycle |
| BP-13 | Taxonomy and classification constraints | Crime classification |
| BP-15 | Case references and case outcomes | Case lifecycle |
| BP-16 | Investigative discoveries and assessments | Investigation |
| BP-17/BP-18 | Victim/witness and suspect/offender roles | Case-role/status records |
| BP-19/BP-20/BP-21 | Interview, surveillance and intelligence references | Their originating records |
| BP-22/BP-23/BP-24 | Scene, evidence and forensic references | Evidence authority |
| BP-25–BP-29 | Arrest, custody, legal and court outcomes | Justice process |
| BP-30 | Institutional rules and public-service configuration | Governance |
| BP-35 | Event scheduling, execution and causal processing | Simulation engine |
| BP-36 | Relationships and social context | Relationship master records |
| BP-37 | Canonical simulation clock | Time authority |
| BP-38/BP-39 | Records, persistence and recovery | Data/persistence authority |
| BP-40/BP-41 | Player-facing presentation and notifications | Interface/delivery |
| BP-42 | Role and attribute-based access | Security |
| BP-43 | Test strategy and evidence | Quality assurance |
| BP-44 | Approved configuration and change history | Change control |

## 30. Open decisions for policy and configuration

1. Initial occurrence-family catalogue and generation scope by domain.
2. Opening-world event baselines and ordinary-life activity distribution.
3. Crime/non-crime generation rates and tuning methodology.
4. Event-family weighting, diversity targets and repetition windows.
5. Causal model implementation and explainability requirements.
6. Permitted AI/model use in event proposal and narrative generation.
7. NPC behavioural dimensions, memory decay and communication rules.
8. Discovery and reporting delay distributions.
9. Consequence propagation limits and priority rules.
10. Event granularity thresholds for splitting/merging.
11. Exact occurrence lifecycle states and terminal-state semantics.
12. Scenario generation and curated scenario seeding rules.
13. Random seed, deterministic replay and reproducibility policy.
14. Processing tiers, relevance thresholds and resource budgets.
15. Event proposal rejection and quarantine workflow.
16. Permitted use of sensitive attributes in generation, if any.
17. Initial service dependency map and emergency event catalogue.
18. Environmental and weather model fidelity.
19. Digital occurrence scope and external-context representation.
20. Data retention, audit and hidden-truth access policy.
21. Event correction and historical reconstruction rules.
22. Which metrics are player-visible versus internal-only.

These decisions remain open. This specification does not silently choose real-world crime rates, legal thresholds, demographic correlations, model weights or operational policies.

## 31. Traceability to source blueprint

The authoritative source is `docs/governance/SALTWATER_MASTER_BLUEPRINT.json`; the 52-to-44 crosswalk is the requirement mapping authority.

### 31.1 Direct source requirements — S29
- **S29.R02:** Generate varied, causally grounded incidents across the city and its organisations. BP-14 owns event proposal, causal truth, execution, consequences, discovery and generation provenance. BP-02/BP-03/BP-04/BP-35/BP-36/BP-37 provide geography, people, organisations, execution, relationships and time. BP-13 provides taxonomy constraints; BP-12 receives valid police-awareness/referral events.
- **S29.T01:** Generated incidents must be unique, plausible and linked to valid entities and chronology. BP-14 owns uniqueness, causal plausibility, event lineage and entity references; BP-12/BP-13/BP-35 validate incident linkage, taxonomy semantics and event execution.

### 31.2 Additional mapped source requirements
- **S05.R03:** Generate consistent witness, victim, suspect and community connections without deterministic shortcuts. BP-14 models occurrence-level participation and plausible causal context; BP-03 owns identity; BP-17/BP-18 own case roles; BP-21 owns intelligence.
- **S15.R03:** Social care and community services affect vulnerability, risk, support and police interactions. BP-14 may generate service interactions and consequences; BP-04 owns service providers; BP-17 owns support case interfaces; BP-30 owns institutional governance.
- **S21.R02:** Events, attendance and public narratives can affect incidents and investigations. BP-14 generates causal event activity; BP-04 owns venues/organisations; BP-17/BP-21 own case support/intelligence; BP-35/BP-36/BP-37/BP-41 own execution, social context, time and notifications.
- **S28.R03:** Patrol and field activity creates unexpected operational events. BP-14 generates occurrences from world conditions; BP-10/BP-12 own field activity and incidents; BP-35 owns execution.
- **S40.R03:** Institutional failures and public trust evolve from events. BP-14 generates causal occurrences and social consequences; BP-30/BP-31 own oversight and complaint processes; BP-35/BP-36/BP-41 own simulation, social effects and notifications.
- **S42.R01–R04:** Coordinate world activity, preserve relevance-based processing, prevent impossible states and freeze background activity while the player is absent. BP-14 owns occurrence-domain causality; BP-35 owns event execution; BP-03/BP-04/BP-37/BP-38/BP-43 support identity, world records, time, persistence and quality.
- **S43.R01–R05:** Generate naturalistic text within knowledge boundaries; separate hidden truth; preserve exact `bingo` reveal rule and no unsolicited hints; persist canon-changing generated claims. BP-01 owns player agency/concealment; BP-14 owns occurrence truth; BP-16/BP-19/BP-21 own investigation/interview/intelligence records; BP-35/BP-38/BP-40/BP-42 own execution, persistence, interface and access.
- **P07:** Generated facts obey canon, causality, schedules, geography, resources and prior records. BP-14 enforces occurrence constraints; BP-01/BP-02/BP-35/BP-37/BP-43 provide canon, geography, execution, time and tests.
- **X09:** Police receives deepest simulation; supporting city systems remain operationally coherent, proportionate and causally connected. BP-14 generates police-relevant and background events without expanding non-police systems beyond their support role.
- **A06:** Crime taxonomy/generation ownership must remain explicit across BP-13/BP-14, with geography, dispatch and victim/suspect responsibilities assigned correctly. BP-13 owns taxonomy; BP-14 occurrence generation; BP-02 geography; BP-11 reporting/dispatch; BP-17/BP-18 case roles.

## 32. Implementation sequencing and exit conditions

Before implementation:
- Complete semantic crosswalk review for every requirement and test mapped to BP-14; structural mapping alone is not semantic completion.
- Confirm BP-13 taxonomy interface and initial approved taxonomy catalogue.
- Confirm BP-02 spatial references, BP-03 population/promotion contracts and BP-04 world entity references.
- Define event identity, lifecycle, causal graph and append-only correction model.
- Define the boundary between hidden occurrence truth, NPC knowledge, police awareness and player-visible information.
- Define BP-35/BP-37 scheduling, deterministic ordering, pause/freeze and replay contracts.
- Define occurrence-to-report/incident referral events with BP-11/BP-12.
- Define consequence handoffs and idempotency across all owning domains.
- Establish test fixtures for unreported, misreported, non-crime, delayed-discovery, multi-actor, multi-stage and linked occurrences.
- Test 10,000-person capacity, 10,000+ business references, one-city geography and permanent promotion.
- Establish anti-leak tests for exact `bingo` reveal gate, metadata, search, logs, exports and AI narrative.
- Establish representative load, replay, recovery and high-entropy narrative storage benchmarks.
- Record approved generation parameters and model/configuration versions before implementation.

Implementation is complete only when event truth is causally coherent, interfaces reconcile, time-freeze is enforced, population/geography constraints hold, hidden truth remains protected, replay and recovery evidence pass, and all mapped acceptance tests have recorded results. Design, implementation, testing and verification remain independent statuses.

## 33. Design status and change control

**Current status:** DESIGNED_DRAFT. This is a comprehensive specification draft, not an approved design and not an implementation.

- Implementation: NOT_STARTED.
- Test execution: NOT_STARTED.
- Verification: NOT_STARTED.
- User approval: PENDING.
- Neon writes: NONE. This document authorises no schema changes, migrations, seeds, imports, bulk writes or uploads.

Changes must preserve the fixed BP-01–BP-44 structure, source requirements, test traceability and Saltwater canon. Do not remove event meaning, causal detail, uncertainty, provenance, identity, history or edge cases to reduce storage. Compress representation, never meaning.
