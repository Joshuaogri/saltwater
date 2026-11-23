# BP-35 — Simulation Engine

**Project:** Saltwater  
**Blueprint division:** BP-35 of the fixed 44-division structure  
**Specification version:** 1.0  
**Specification status:** DESIGNED_DRAFT — review/approval pending  
**Implementation / test execution / verification:** NOT_STARTED  
**Authority:** Saltwater master blueprint BP-01–BP-44, original 52-division source and current 52→44 crosswalk.  
**Database authority:** This document authorises no Neon schema, migration, seed, import or other write.

## 1. Purpose

BP-35 defines the runtime simulation engine that makes Saltwater a coherent, causally connected, persistent, living city-state rather than a collection of disconnected records and scripted screens. It coordinates domain-owned state changes, scheduled work, non-player character (NPC) activity, environmental and infrastructure effects, organisations, businesses, public services, police operations, incidents, crime occurrence execution, narrative generation requests and player actions.

The engine is the authoritative coordinator for **when and in what deterministic order** simulation events are accepted, validated, executed, committed, retried, paused, resumed, replayed, observed and recovered. It does not take ownership of the business rules or canonical records belonging to other blueprint divisions. Domain divisions own their state and rules; BP-35 provides the execution contract through which those rules are invoked safely.

The engine must support a city that feels continuously alive while respecting the central Saltwater rule: **simulation time and all simulation activity stop when the player leaves the simulation or pauses it.** There is no hidden offline progression. The world resumes from its exact committed point when the player returns.

## 2. Scope and exclusions

### 2.1 BP-35 owns

- Runtime orchestration, event intake, validation, ordering, dispatch, execution coordination and commit acknowledgement.
- Event envelopes, correlation, causality metadata, idempotency, retry, dead-letter/quarantine and failure handling.
- Deterministic execution contracts and replay boundaries.
- Domain event routing and cross-domain coordination without taking domain ownership.
- Simulation lifecycle: initialisation, ready, running, paused, stopping, recovery, degraded and safe-halt states.
- Explicit player-presence/pause gate and the global no-offline-progression invariant.
- NPC activity orchestration: waking/activating only relevant simulated agents, selecting eligible actions, respecting knowledge, resources, schedules, location and authority, and committing resulting domain commands.
- Tiered simulation fidelity and relevance-based activation, including permanent promotion of materially relevant people to full persistent simulation.
- Causal propagation across people, households, businesses, organisations, services, infrastructure, transport, environment, incidents and police operations.
- Deterministic random streams, scenario seeds, generated event uniqueness and reproducibility.
- Simulation workload scheduling, priority, budgets, back-pressure and safe load shedding.
- AI/narrative generation orchestration, context assembly, output validation, provenance and strict player-agency/hidden-truth boundaries.
- Optional visual/map/timeline/chart generation requests as projections of canonical records, never as authoritative state.
- Engine health, event-queue metrics, execution traces, latency, error counters, resource use and recovery signals, with operational ownership coordinated with BP-51 source requirements and BP-38/39.
- Engine-level testability, deterministic fixtures, replay harness contracts and runtime invariants.

### 2.2 BP-35 does not own

- Canonical geography, district/address/road geometry or land-use truth (BP-02).
- Person identity, living-person ledger, life status, population cap or demographic attributes (BP-03).
- Business, organisation, property, infrastructure-operator or facility identity (BP-04).
- Police mandate, personnel, career, units, deployment, patrol, dispatch, incidents, cases, investigation, evidence, forensics, custody or legal decisions (BP-05 through BP-34 as applicable).
- Canonical relationship meaning, household membership or social-network history (BP-36).
- Authoritative simulation clock, calendar, time-zone rules, shift definitions, schedules and deadline semantics (BP-37). BP-35 consumes time and executes eligible scheduled work.
- Authoritative schemas, record constraints and transaction boundaries (BP-38), or persistence/backup/restore mechanisms (BP-39).
- Interface presentation and player command catalogue (BP-40), notification/report presentation (BP-41), security policy/permission decisions (BP-42), test governance (BP-43), or configuration/change approval (BP-44).
- Hidden case truth ownership or crime occurrence authorship (BP-14). BP-35 may coordinate generation and execution but cannot disclose hidden truth.
- Independent simulation of external cities or territories. Off-map actors may be represented as external references only.

### 2.3 Engine versus domain rule

BP-35 decides *whether and when* a command/event may execute and ensures its execution contract. The owning division decides *what the event means* and whether its domain-specific preconditions are met. BP-35 must never invent a domain outcome because an event is due, a queue is blocked, an NPC is idle or a narrative response would be convenient.

## 3. Binding Saltwater canon and global invariants

1. Saltwater is one fictional sovereign city-state, one city and one jurisdiction. No external playable city, territory or expansion is introduced by engine simulation.
2. The living population is exactly bounded by a hard cap of 10,000. Every living person is counted once by BP-03 regardless of how many roles, jobs, households, accounts or simulation agents they hold.
3. The business registry contains at least 10,000 businesses under BP-04. Engine activity must not create duplicate businesses to satisfy activity or variety.
4. Police is the deepest fully simulated institution. Other domains function coherently and sufficiently to affect policing, but the engine must not silently turn every city institution into an equally deep simulation.
5. Text is the permanent primary interface. Engine state must be inspectable and actionable through text. Maps, diagrams, charts, scene visuals and other graphics are optional projections.
6. No simulation time or simulation activity advances while the player is outside the simulation or the game is paused. This includes NPC thought/action, business opening/closing, traffic movement, weather evolution, service queues, crime occurrence, emergency calls, patrols, dispatch, investigations, interviews, surveillance, custody, court, corrections, payroll, procurement, debt accrual, notifications, deadlines and scheduled jobs.
7. Wall-clock time, browser time, server time, database time and device time cannot independently advance the fictional world. Only BP-37 canonical simulation time can do so, and only while the engine is in an authorised running state.
8. Player decisions remain authoritative. The engine does not take over the player's officer, auto-solve cases, choose investigative lines, force success/failure or reveal hidden culprit/accomplice identity.
9. The exact `bingo` trigger and all hidden-truth restrictions remain binding. The engine must not disclose hidden generator truth through logs, NPC dialogue, narrative context, tool outputs, visual metadata, event names, error messages or debug traces visible to the player.
10. All generated facts must respect canon, causality, time, geography, resources, schedules, population, business registry, knowledge and prior records.
11. Every persistent entity and event has stable identity, lifecycle, provenance and explicit relationships. No duplicate state authority.
12. Deterministic replay applies wherever declared. Non-deterministic AI output must be captured as a versioned input/result or excluded from deterministic state replay.
13. Storage efficiency may compress structure, not meaning, event lineage, provenance, auditability or required detail.
14. Engine failure must fail safely. It must not create partial domain transactions, duplicate actions, skipped evidence, population overflow or hidden time advancement.

## 4. Runtime architecture

### 4.1 Logical components

The logical engine comprises:

- **Runtime controller:** owns engine lifecycle and the running/paused gate.
- **Command gateway:** accepts player, NPC, domain and system commands with actor, authority and source context.
- **Event registry/router:** validates event type/version and routes it to the owning domain handler.
- **Eligibility scheduler:** selects scheduled work that is due according to BP-37 simulation time and current engine state.
- **Priority arbiter:** orders eligible work under deterministic priority and fairness rules.
- **Execution coordinator:** invokes domain handlers, enforces transaction/idempotency contracts and records outcomes.
- **Causality coordinator:** tracks parent/child events and cross-domain consequences.
- **NPC activity coordinator:** activates appropriate NPC agents and requests actions within their knowledge, capabilities and current situation.
- **Fidelity manager:** chooses detail level based on relevance, proximity, causal impact and resource budget without violating promotion permanence.
- **Deterministic random service:** supplies named, seeded random streams to eligible simulation systems.
- **Narrative/AI gateway:** supplies bounded context to generation services and validates output before it can be shown or used.
- **Replay and recovery interface:** exposes event sequence and state watermarks to BP-38/BP-39 and QA.
- **Observability emitter:** publishes health, queue, latency, failure, load and recovery metrics without exposing protected content.

These are logical responsibilities, not a mandate to deploy separate microservices. A compact modular runtime may implement them within one process or a small number of components, provided ownership, isolation, transaction and failure contracts remain explicit.

### 4.2 Domain ownership

Every event type has exactly one primary domain owner. Multiple divisions may subscribe to an event, but only the owner may authoritatively change its domain record. A consumer may create its own linked record through its own command contract.

Examples:
- BP-14 owns crime occurrence generation and hidden occurrence truth; BP-35 coordinates due execution and resulting event delivery.
- BP-12 owns operational incident records; BP-35 routes accepted incident events and causal notifications.
- BP-37 owns time and schedules; BP-35 runs eligible schedule entries only while active.
- BP-03 owns person identity and population; BP-35 coordinates person activity without creating duplicate identities.
- BP-04 owns business/property identities; BP-35 coordinates opening, service, supply and disruption events through BP-04-owned rules.
- BP-36 owns relationships; BP-35 coordinates relationship-triggered activity without rewriting relationship truth.
- BP-38 owns record/schema integrity; BP-39 owns durable persistence and recovery.
- BP-42 owns permissions; BP-35 checks supplied authorisation decisions before dispatching protected commands.

## 5. Core event model

### 5.1 Event envelope

Every accepted event uses a versioned envelope containing, at minimum:

- `event_id`: globally unique stable ID.
- `event_type` and `schema_version`.
- `occurred_at_sim`: canonical simulation timestamp, if applicable.
- `received_at_sim`: simulation timestamp at acceptance; absent for paused external arrivals held outside simulation execution.
- `actor_ref`: canonical person, organisation, system or player reference.
- `actor_type` and acting role/capability reference.
- `source_division` and `source_record_ref`.
- `correlation_id` and optional `causation_id`.
- `idempotency_key` where an operation can be retried.
- `priority_class`, eligibility and expiry policy.
- `payload_ref` or validated compact payload.
- `visibility_class` and permission requirements.
- `random_stream_ref` where stochastic behaviour is permitted.
- `processing_state`, attempt count and outcome reference.
- `created_by`, configuration/policy version and provenance metadata.

The envelope contains references and routing metadata, not duplicated domain truth. Sensitive payloads remain in their authoritative domain records.

### 5.2 Event versus command versus observation

- A **command** requests an action and may be accepted, rejected or held after validation.
- An **event** records that an attributable state transition or occurrence has happened.
- An **observation** records information perceived or received by an actor; it does not automatically establish objective truth.
- A **scheduled item** represents work eligible at a future BP-37 simulation time; it is not itself proof that the resulting action occurred.
- A **projection** is a derived view or narrative rendering and cannot independently mutate authoritative state.

The engine must not convert an unverified observation into a fact or a rejected command into an event.

### 5.3 Event lifecycle

Standard lifecycle:

`Created → SchemaValidated → Authorised → Eligible → Queued → Claimed → Executing → Committed → Delivered/Completed`

Alternative states include `Rejected`, `Held`, `Deferred`, `Cancelled`, `Expired`, `FailedRetryable`, `Quarantined`, `DeadLettered` and `Superseded`.

State transitions are explicit and attributable. A committed event cannot be silently returned to draft or deleted. A correction is a new linked event. Terminal failure must retain enough diagnostic evidence for safe review/recovery.

### 5.4 Event immutability and delivery

Accepted event identity and original payload are immutable. Delivery attempts and processing outcomes are append-only records. The engine may use at-least-once delivery internally only when consumers implement idempotency; user-visible and domain-level effects must be effectively once. A successful commit and its delivery acknowledgement must be recoverable without repeating the domain mutation.

## 6. Deterministic ordering, causality and concurrency

### 6.1 Ordering

Eligible work is ordered by a deterministic tuple, using configured priority class, due simulation timestamp, causal dependency, domain-defined ordering key and stable event ID as tie-breakers. The exact priority catalogue is configuration-controlled. Priority must not cause starvation: lower classes receive bounded service under load.

No ordering rule may use random iteration order, database row order without explicit ordering, machine-local time or nondeterministic thread completion as an authoritative tie-breaker.

### 6.2 Causal dependencies

An event may declare prerequisite event IDs or required source-state versions. It cannot execute until prerequisites are committed or explicitly resolved by the owning domain. Parent/child causation is recorded. Cross-domain consequences are emitted as new events rather than hidden synchronous side effects.

A causal chain must support:
- tracing from initiating player action or world event to every downstream consequence;
- detection of cycles and runaway feedback;
- bounded fan-out and depth;
- deterministic ordering among siblings;
- explicit cancellation/compensation rules;
- recovery after partial delivery.

### 6.3 Concurrency

Concurrent execution is permitted only where domain contracts establish independence. Shared resources, population capacity, inventory, account balances, unit availability, facility capacity, actor location, custody status and other contested state require atomic validation/commit at the owning domain.

The engine cannot reserve or consume a domain resource based on a stale projection. A command rejected due to changed state must be returned as rejected/conflicted with a source reference, not silently retried as a different action.

### 6.4 Atomicity boundary

A single domain state transition must commit atomically under BP-38. Multi-domain workflows use explicit event choreography, acknowledgements and compensating actions; they must not pretend that independent domain records share one unbounded transaction. Every partial workflow state is visible and recoverable.

## 7. Simulation lifecycle and pause gate

### 7.1 Lifecycle states

- **Uninitialised:** no runtime state has been loaded.
- **Initialising:** canon, configuration, domain registries and persistence watermarks are being checked.
- **Ready:** coherent state is loaded; no simulation time is advancing.
- **Running:** player has entered/resumed the simulation and the runtime gate permits scheduled simulation work.
- **Paused:** simulation state is frozen at a committed timestamp.
- **Stopping:** runtime is closing active execution at a safe commit boundary.
- **Recovering:** reconciling event log, domain commits, scheduler and persistence.
- **Degraded:** non-critical subsystem unavailable; only explicitly safe operations may continue.
- **SafeHalt:** critical integrity or canon invariant failed; simulation execution is blocked pending recovery.

Only the runtime controller may change lifecycle state through an authorised transition. UI display does not itself change the authoritative state.

### 7.2 Pause semantics

On pause or player exit:
1. Stop admitting new simulation-time advancement.
2. Stop claiming new scheduled/NPC/world events.
3. Allow an already executing atomic domain transaction to reach a safe commit or rollback boundary; do not expose half-committed state.
4. Freeze BP-37 clock at the last committed simulation instant.
5. Persist execution watermark and pause reason.
6. Keep read-only inspection available subject to permissions.
7. Queue external notifications/requests without processing their simulation effects.
8. Do not run background simulation, AI NPC decisions, event generation or catch-up.

No elapsed real-world time is converted into fictional time after pause.

### 7.3 Resume semantics

On resume:
1. Validate player session and runtime state.
2. Verify persistence watermark and domain consistency.
3. Reconcile only work committed before pause.
4. Obtain the next simulation time/action from BP-37.
5. Reopen event claiming under deterministic order.
6. Process eligible events at the normal configured rate; do not fast-forward to wall-clock time.
7. Surface queued external inputs as pending items; they become simulation events only under explicit rules and after the game resumes.

Repeated pause/resume cycles without an intervening simulation step must not change any domain state or timestamp.

### 7.4 External arrivals during pause

External connector callbacks, database notifications, system messages or user-facing notifications may arrive while paused. They must be stored as non-simulation ingress metadata or held by the host; they cannot mutate Saltwater world state, trigger NPC reactions, create cases, change a clock or generate fictional events until resumed and validated. Arrival time in the real world is not fictional occurrence time.

## 8. Canonical time and scheduling interface

BP-37 owns time zones, calendar, date arithmetic, clock progression, schedule definitions, deadlines and authoritative due-time calculation. BP-35 consumes a canonical time snapshot and executes only events declared due by BP-37.

The engine must:
- require a canonical timestamp for every time-sensitive event;
- preserve both effective/occurrence time and processing/commit sequence where they differ;
- order equal-time events deterministically;
- reject timestamps outside valid simulation state unless an explicit historical import/replay operation is authorised;
- prevent machine time from advancing the world;
- avoid running scheduled jobs while paused;
- process missed/delayed jobs only according to BP-37 catch-up policy, which must never imply offscreen world activity;
- distinguish an event due at a simulation time from an event actually executed;
- preserve local time-zone and daylight/calendar semantics supplied by BP-37;
- use explicit time budgets and event-step boundaries to prevent a single resume from creating an uncontrolled time jump.

Schedules include but are not limited to NPC routines, business hours, public service appointments, police shifts, transport timetables, deliveries, maintenance, weather/environment updates, recurring social events, crime occurrence windows, court/custody processes, finance cycles and notifications. The owning domain creates and interprets the schedule; BP-35 coordinates execution.

## 9. NPC and world-activity orchestration

### 9.1 Agent identity and activation

Every simulated person references one BP-03 canonical person ID. An NPC agent is a runtime capability/profile associated with that person, not a second person record. Activation does not create identity. A person may be activated for a single event, a short activity window or ongoing relevant simulation.

The engine selects agents for processing based on relevance, current activity, schedule, location, relationships, operational duties, incoming event, player proximity and causal impact. Selection must not be random in a way that creates unexplained priority or causes important events to disappear.

### 9.2 Knowledge boundary

An NPC may act only on information that the person has observed, been told, lawfully accessed or reasonably inferred under their own knowledge record. BP-35 must provide bounded context and must not supply global database truth, hidden generator records, unseen case evidence or another NPC's private knowledge without an authorised information transfer.

Knowledge includes source, acquisition time, confidence/uncertainty, access basis, retention/forgetting rules where configured and current availability. A generated narrative may not assert that an NPC knows a fact unless a valid knowledge source exists.

### 9.3 Decision and action contract

An NPC decision request contains:
- canonical person reference and active role;
- current location and time snapshot;
- known facts and permitted context;
- capabilities, skills, authority and current commitments;
- needs/goals/preferences supplied by BP-03/BP-36 or relevant domain;
- available resources and constraints;
- candidate action schema supplied by the owning domain;
- deterministic random-stream reference if stochastic choice is allowed;
- output schema and validation rules.

The AI may propose an action or dialogue, but the owning domain validates authority, feasibility, knowledge and state before committing. A narrative answer alone never performs an action. Unsupported action proposals are rejected with no domain side effect.

### 9.4 Relevant-person promotion

When a person becomes materially relevant to a case, incident, police activity, player action or consequential world event, BP-35 signals BP-03 to promote that canonical person to the required full persistent simulation level. Promotion is permanent for the remainder of the game. A person is never downgraded or deleted merely because immediate relevance ends.

Promotion must be atomic with population-ledger checks and must not exceed the 10,000 living-person cap. If the cap is full, the engine must not create a new person; BP-03's authorised lifecycle/capacity process must resolve eligibility. Existing person identity and history remain stable across promotions.

### 9.5 Workload and fidelity

The engine may use tiers such as:
- **Registry tier:** canonical identity/business/service record with minimal runtime activity.
- **Ambient tier:** periodic aggregate activity and schedule state.
- **Active tier:** event-level behaviour for current causal relevance.
- **Full persistent tier:** complete individual history, schedule, relationships, knowledge, needs, actions and domain references for permanently promoted persons.

Tier changes may increase fidelity. They must not erase existing detail, reverse promotion or falsely imply that unobserved activity was individually simulated. Historical aggregate periods remain labelled as aggregate. Material events are recorded at the fidelity needed for audit and case use.

## 10. City systems, environment and causal propagation

BP-35 coordinates interactions among domain-owned systems without taking over their state. Causal propagation must be geographically bounded, time-valid and resource-aware.

### 10.1 Geography and access

All location references resolve through BP-02 canonical districts, zones, parcels, coordinates, roads and boundaries. BP-04 owns premises/building topology and access points. Movement, entry, service and incident events must reference valid locations or explicit external references. The engine cannot create duplicate or contradictory addresses, buildings, parcels, road links or access points.

### 10.2 People, businesses and organisations

Activity must respect person schedules, employment, roles, skills, availability, relationships and known information. Business activity must respect BP-04 status, premises/mobile/virtual basis, opening hours, services, staffing and relevant resource constraints. Organisations and public services must respect authority, operating hours, capacity, staffing and dependencies.

The minimum 10,000-business registry is not a requirement to run 10,000 full agent loops each simulation tick. The engine uses tiered, event-driven activation while ensuring business activity that materially affects the player or police is individually traceable.

### 10.3 Utilities and infrastructure

Water, electricity, sanitation, waste, telecoms, internet and other critical infrastructure are represented by BP-04 or designated domain owners. BP-35 propagates outages only to connected areas, facilities and dependent services. An outage has source, affected network/asset references, start/end simulation times, severity, operator response, restoration event and consequences.

No unrelated area is affected by a local failure unless a recorded dependency supports propagation. Restoration is an explicit event; a system does not silently return to service because a timer expired.

### 10.4 Transport, trade and supply

Movement and delivery use canonical roads/routes, transport modes, timetables, travel constraints, inventory and capacity. Sender, carrier and receiver records must reconcile under BP-04/BP-09 and related owners. Off-map gateways or counterparties are external references only. They do not instantiate another city or playable geography.

Supply disruption propagates through recorded dependency chains: source/stock, carrier, route, receiver, service and resulting availability. Essential food and service states must reconcile across stock and delivery records. The engine cannot conjure replacement stock or instant delivery to resolve a shortage.

### 10.5 Weather and hazards

Weather, daylight, tide/water conditions where relevant, pollution and hazards are generated or sourced under configured rules and BP-37 time. Each fact has location coverage, valid time range, source/model version, confidence and effect scope. Hazards may affect roads, facilities, utilities, businesses, public events, health services, police response and evidence conditions only where a valid causal link exists.

### 10.6 Public services and emergency coordination

Healthcare, social care, education, culture, media, recreation, food services, emergency response and civil protection remain proportionate domain representations. BP-35 coordinates capacity, appointment, event, outage, alert and response effects. BP-11/BP-12 own police emergency intake/dispatch/incident workflows; other agency records remain with their owners. Resource availability and response chronology must reconcile across agencies.

### 10.7 Crime and police activity

BP-14 owns hidden occurrence truth, crime generation rules and the occurrence catalogue. BP-35 may schedule and execute eligible occurrence events, but it cannot reveal hidden offenders or bypass BP-14's safeguards. BP-12 owns incident records, BP-15 cases, BP-16 investigation, and all other police divisions own their respective records. The engine routes events and consequences; it never auto-solves investigations or suggests the next line of enquiry.

## 11. Crime generation and player agency firewall

The engine must support varied, plausible crime and non-crime events while preserving the separation between:
- hidden world truth;
- event-generation plan;
- event execution;
- observable consequences;
- witness/NPC knowledge;
- reports and allegations;
- police incident and case records;
- evidence and intelligence;
- investigative hypotheses and conclusions;
- legal findings.

Only authorised internal components may access hidden occurrence truth. The narrative/AI gateway receives only the minimum context needed for the requested output. A player-facing request may include observations, reports, evidence or uncertainty but must not include the hidden solution.

Controls:
1. Exact `bingo` is the sole user trigger for the permitted hidden-truth reveal defined by global canon. Near matches, synonyms, case variations or NPC utterances do not count unless global rules explicitly say so.
2. No event ID, payload field, database query, debug log, model context, exception trace, image label, map annotation, notification or generated dialogue may leak hidden identities before the trigger.
3. No unsolicited hint, suspect ranking, recommended investigative action, leading question or solution nudge may be generated.
4. The player controls investigative actions. The engine may report observable state and requested results, not choose the next step.
5. NPC investigators are not omniscient and do not receive BP-14 truth unless a valid observation or authorised disclosure provides it.
6. Generation must not guarantee a solvable case by inserting clues that are not causally supported. Conversely, it must not secretly make a case impossible after the player has taken valid actions.
7. Crime occurrence uniqueness, chronology, actors, locations, resources and consequences are validated before execution.
8. A generated event cannot silently overwrite a pre-existing fact or create a contradiction; it must be rejected, reconciled by the domain owner or recorded as an explicit uncertainty/conflict.

## 12. AI and narrative orchestration

AI generation is a service used by the engine, not an authority over the world. Its outputs may include natural-language dialogue, descriptions, summaries, reports, NPC action proposals and optional visual-generation requests.

### 12.1 Context assembly

Context is assembled from authorised, versioned source records. It must include only the facts necessary for the task, with source IDs, time validity, confidence and visibility constraints. It must distinguish fact, observation, allegation, inference, hypothesis, estimate, memory, rumour and unknown information.

Context must not contain hidden truth for player-facing or unauthorised NPC-facing generation. A domain-specific prompt cannot override global agency, pause, population, canon or confidentiality rules.

### 12.2 Output validation

Generated output is checked for:
- schema and required fields;
- source-grounded factual assertions;
- time, location, identity and chronology consistency;
- actor knowledge and authority;
- canon and population constraints;
- hidden-truth leakage;
- unsupported legal, medical, financial or operational conclusions;
- prohibited investigative hints or forced player actions;
- duplicate or contradictory event proposals;
- text safety and presentation requirements.

Invalid output is rejected, regenerated within a bounded retry policy or replaced with a neutral failure message. It is never committed as domain truth merely because a model produced it.

### 12.3 Provenance and versioning

Store generation request ID, model/provider identifier where available, model/configuration version, prompt-template version, context-source references, output hash or retained output, validation result, actor/recipient, simulation timestamp and resulting domain command/event references. Sensitive prompts and outputs follow BP-42 permissions and BP-39 retention.

### 12.4 Deterministic replay boundary

A recorded AI output used as an input to authoritative state is replayed as the recorded versioned input, not regenerated from a later model. If the output is merely presentation and has no authoritative effect, it may be regenerated for display only where the interface permits, and it must not change simulation state.

## 13. Randomness and reproducibility

Stochastic events use deterministic named random streams seeded by game identity, scenario seed, domain/event scope and stable event ID. One subsystem's random draw must not shift another subsystem's sequence. A random decision records stream ID, seed/version reference, draw index or reproducible equivalent, and consuming event.

Randomness may influence only configured variables and bounded choices. It cannot override hard canon, population cap, authority, player choice, evidence integrity, case truth firewall or resource feasibility.

For replay, the engine must preserve:
- initial scenario seed and engine/configuration versions;
- ordered input event IDs and payload versions;
- random stream state or reproducible draw references;
- domain handler versions;
- canonical time snapshots;
- accepted commands and outcomes;
- external/AI outputs that influenced authoritative state;
- persistence watermark and transaction commit sequence.

Replay comparison is performed against authoritative domain state and event outputs, not unstable presentation ordering or wall-clock metrics.

## 14. Workload, fidelity and resource governance

The runtime must operate efficiently on a modest development environment and a compact Neon database. Avoid continuous per-person polling or a high-frequency full-city tick where event-driven scheduling is sufficient.

- Use event-driven execution and coarse-to-fine activation.
- Batch safe independent work while preserving deterministic ordering and domain atomicity.
- Apply bounded queue sizes, worker budgets, execution timeouts and back-pressure.
- Prioritise player-facing and safety-critical operational events without starving routine simulation.
- Use deterministic degradation: defer low-impact ambient updates before dropping critical events.
- Never discard committed events or case-relevant activity to meet a performance target.
- Never reduce a promoted person's fidelity or delete their history to save resources.
- Cache projections only with source watermark and invalidation rules.
- Use compact references, stable codes and versioned schemas; avoid duplicate copies of domain records.
- Keep event payloads small and reference authoritative records.
- Record storage growth, event volume, queue age, latency, CPU/memory and failure rates.
- If resource pressure threatens correctness, enter degraded mode or safe halt rather than silently lowering integrity.

A low-detail business may be represented through aggregate state, but any material transaction, event, police relevance, player interaction or case connection must be promoted to traceable event-level detail without changing business identity or fabricating historical precision.

## 15. Failure handling and recovery

### 15.1 Failure classes

- Validation failure: schema, authority, canon or precondition failure; reject with reason.
- Transient infrastructure failure: retry only under bounded policy and idempotency.
- Domain conflict: return conflict to owner/caller; do not force overwrite.
- Dependency unavailable: hold event until dependency is restored or expiry policy applies.
- Handler failure: rollback incomplete transaction; preserve diagnostic trace.
- Poison event: quarantine after configured attempts; do not block unrelated independent work.
- Integrity failure: safe halt affected scope or whole runtime, depending on blast radius.
- Persistence failure: do not acknowledge commit until durable write is confirmed.
- AI provider failure: no world-state change; use bounded retry or safe neutral fallback.
- Replay mismatch: stop verification, preserve both expected and actual evidence, require investigation.

### 15.2 Retry rules

Retries use the same event ID/idempotency key and preserve original payload/version. Backoff is measured in runtime processing attempts or active simulation time as configured; it must not cause fictional time progression while paused. A retry cannot mutate its payload to make a rejected command succeed. Changed intent requires a new command/event.

### 15.3 Quarantine and dead-letter

Quarantined events retain source, payload hash/reference, validation/handler error, attempt history, timestamps, dependency state and resolution authority. Only authorised recovery actions may requeue, supersede or reject them. A dead-letter queue is not a deletion bin. Case-relevant or financial/evidence-related failures remain visible to authorised users and are not silently discarded.

### 15.4 Recovery

On restart/restore, the engine:
1. Loads the last durable engine and domain watermarks from BP-39.
2. Validates schema/configuration compatibility through BP-38/BP-44.
3. Reconciles event claims, commits, acknowledgements and domain transaction outcomes.
4. Reconstructs eligible queues from authoritative scheduled records and BP-37 time.
5. Identifies incomplete, duplicate, missing or out-of-order deliveries.
6. Replays only safe uncommitted work using original event IDs and idempotency keys.
7. Verifies population, identity, business registry, resource, money, location and domain invariants.
8. Remains paused/ready until an authorised player session resumes simulation.

Recovery must not advance time, regenerate new NPC decisions, create duplicate crime occurrences or re-run a committed payment/action.

## 16. Security, permissions and information boundaries

BP-42 owns permission policy. BP-35 must attach actor identity, role, session, capability, purpose, source and visibility class to every command and event. It must not infer authority from a display name, rank string or prompt.

- Validate permission before protected event dispatch and again at commit where authority may have changed.
- Separate player commands, NPC proposals, domain events, system maintenance and administrator recovery actions.
- Prevent privilege escalation through event payloads or generated text.
- Restrict hidden truth, sensitive person data, medical records, intelligence, evidence, payroll, financial and surveillance material.
- Redact protected fields before context assembly, logs, notifications, narrative and visual projections.
- Keep secrets and credentials out of prompts, logs, event payloads and GitHub.
- Record denied commands and access attempts without exposing protected content.
- Do not let an AI agent grant itself authority or create permissions.
- Administrative recovery is attributable and cannot bypass immutable records or global canon.

## 17. Observability and operational interfaces

The engine emits structured operational signals for:
- lifecycle state and pause reason;
- current simulation timestamp and committed watermark;
- queue depth, oldest eligible item and per-priority backlog;
- event throughput, handler latency and commit latency;
- retry, rejection, quarantine, dead-letter and replay mismatch counts;
- active NPC agents by fidelity tier;
- scheduled work due versus executed;
- event causality depth/fan-out;
- AI request volume, latency, validation failure and token/resource usage where available;
- persistence latency and failed commits;
- memory/CPU/storage estimates and database size measurements;
- population-cap and invariant checks;
- domain dependency health and degraded/safe-halt state.

Metrics must not expose hidden offender identity or sensitive payloads. Logs use event IDs and redacted references. Operational records are themselves attributable and retained under BP-38/BP-39.

Engine service health and database size are measured; the engine does not perform unapproved schema changes or data imports. Any future Neon write requires a measured baseline, incremental size estimate, explicit user approval and post-write measurement.

## 18. Inputs, outputs and event contracts

### Inputs

- Player commands and session/presence state from BP-40/host runtime.
- Canonical time snapshots, schedule definitions and due events from BP-37.
- Canonical identities, population-cap decisions and person lifecycle from BP-03.
- Geography and road/location references from BP-02.
- Business, premises, infrastructure, organisation and service records from BP-04.
- Police and other domain events/commands from their authoritative divisions.
- Relationships and social context from BP-36.
- Configuration and policy versions approved through BP-44.
- Schemas, transaction outcomes and record references from BP-38.
- Persistence watermarks, recovery status and backup/restore signals from BP-39.
- Permission decisions and visibility classifications from BP-42.
- AI/narrative service responses, treated as untrusted proposals until validated.

### Outputs

- Routed domain commands/events and delivery acknowledgements.
- Runtime lifecycle transitions, pause/resume records and simulation-step watermarks.
- NPC activity requests and validated action proposals.
- Scheduled-event execution outcomes.
- Causal consequence events and cross-domain correlation links.
- Validated narrative outputs and optional visual-projection requests.
- Queue, retry, quarantine, failure, replay and recovery records.
- Operational metrics, health alerts and QA evidence references.

### Event contract

Every handler declares event types, schema versions, owning domain, input preconditions, permission requirements, idempotency strategy, transaction boundary, output events, retry policy, failure policy, time semantics, visibility and replay classification. Undeclared event types are rejected. Handler version changes are controlled by BP-44 and migration compatibility is tested by BP-43.

## 19. Acceptance tests

These are design acceptance criteria, not evidence of executed tests. All fixtures are fictional and deterministic. Tests must not write to production Neon.

- AT-001: Runtime initialises only after canon, configuration, domain registry and persistence watermarks validate.
- AT-002: An invalid or missing configuration prevents transition to Running.
- AT-003: Runtime lifecycle follows only declared valid state transitions.
- AT-004: UI display cannot independently change authoritative runtime state.
- AT-005: Exactly one controller owns the authoritative running/paused gate.
- AT-006: A player exit moves the engine to Paused at a committed boundary.
- AT-007: No scheduled event is claimed after pause is committed.
- AT-008: An in-flight atomic transaction commits or rolls back safely before pause completion.
- AT-009: Pausing does not advance BP-37 canonical time.
- AT-010: Repeated pause/resume without a simulation step produces no world-state change.
- AT-011: Real-world elapsed time while paused produces no fictional time advancement.
- AT-012: Device clock changes cannot alter simulation time.
- AT-013: Resume validates persistence and domain watermarks before event execution.
- AT-014: Resume does not fast-forward to current wall-clock time.
- AT-015: External ingress received while paused cannot mutate world state.
- AT-016: A queued external request is validated only after authorised resume.
- AT-017: Every accepted event has a stable unique event ID.
- AT-018: An event without a registered type/version is rejected.
- AT-019: An event with an incompatible schema version is rejected or explicitly migrated.
- AT-020: Event envelope records source division, actor, provenance and correlation.
- AT-021: Command, event, observation, schedule and projection are distinct types.
- AT-022: A rejected command does not emit a success event.
- AT-023: An observation does not automatically become objective fact.
- AT-024: A scheduled item does not prove the scheduled action occurred.
- AT-025: Event payload is immutable after acceptance.
- AT-026: Processing attempts are appended without mutating original payload.
- AT-027: Repeated delivery of an idempotent event creates one domain effect.
- AT-028: Commit acknowledgement is recoverable without repeating domain mutation.
- AT-029: A handler declares its owning domain and undeclared ownership is rejected.
- AT-030: A consumer cannot directly mutate another domain's authoritative record.
- AT-031: Domain event routing preserves source record references.
- AT-032: Event priority and ordering are deterministic for equal input state.
- AT-033: Stable event ID is the final deterministic tie-breaker where configured.
- AT-034: Scheduler ordering never relies on database row order without explicit ordering.
- AT-035: Lower-priority eligible work receives bounded service under sustained high priority load.
- AT-036: Causal prerequisites prevent child execution before parent commit.
- AT-037: Causation and correlation links trace a full cross-domain event chain.
- AT-038: A causal cycle is detected and quarantined or safely blocked.
- AT-039: Event fan-out and causal depth remain within configured limits.
- AT-040: Concurrent events cannot consume the same exclusive resource twice.
- AT-041: Population-cap validation is atomic through BP-03.
- AT-042: Engine cannot create a duplicate person identity.
- AT-043: Engine cannot exceed the 10,000 living-person cap.
- AT-044: Every simulated person agent references one canonical BP-03 person ID.
- AT-045: Agent activation does not create a second person record.
- AT-046: Relevant-person promotion invokes BP-03 and is permanent.
- AT-047: A promoted person is never downgraded after immediate relevance ends.
- AT-048: Promotion preserves identity and existing life history.
- AT-049: Promotion at full population capacity does not create a new person.
- AT-050: The engine references at least 10,000 BP-04 businesses without duplication.
- AT-051: Business activation respects active/inactive lifecycle and valid location basis.
- AT-052: Engine does not create duplicate business identities for event variety.
- AT-053: A low-fidelity business event is labelled at its true abstraction level.
- AT-054: Material business activity can be promoted to detailed traceable events.
- AT-055: Promotion does not fabricate historical event-level precision.
- AT-056: NPC action context contains only facts in that NPC's authorised knowledge set.
- AT-057: NPC cannot access hidden crime occurrence truth without an authorised disclosure.
- AT-058: NPC cannot use another person's private knowledge without a valid transfer.
- AT-059: NPC action proposal identifies the person, role, location, time and source context.
- AT-060: An NPC proposal is not committed until its owning domain validates it.
- AT-061: An NPC cannot act without required skill, authority or resource.
- AT-062: An NPC cannot perform incompatible simultaneous shifts without an explicit explanation.
- AT-063: NPC location changes respect canonical geography and travel feasibility.
- AT-064: NPC schedules remain frozen while the simulation is paused.
- AT-065: NPC needs or goals cannot override player agency or domain constraints.
- AT-066: NPC knowledge confidence and source provenance remain distinct from truth.
- AT-067: AI-generated dialogue does not itself mutate domain state.
- AT-068: AI-generated action proposal is rejected when output schema is invalid.
- AT-069: AI context is assembled from authorised versioned records.
- AT-070: Player-facing AI context excludes hidden truth.
- AT-071: Unauthorised NPC context excludes protected case information.
- AT-072: Generated factual assertions are checked against source records.
- AT-073: Generated chronology and location are validated before display/commit.
- AT-074: Unsupported legal, medical, financial or operational conclusion is rejected or qualified.
- AT-075: A generated investigative hint or suspect ranking is blocked.
- AT-076: Exact `bingo` rule remains case-sensitive and exact as defined by global canon.
- AT-077: Near-match trigger text does not reveal hidden truth.
- AT-078: Hidden identities do not appear in event names, errors, debug output or metadata.
- AT-079: Visual/map/timeline projections cannot expose hidden truth unavailable in text.
- AT-080: NPC investigator does not receive generator truth absent a valid knowledge source.
- AT-081: Engine never chooses the player's next investigative action.
- AT-082: Engine does not auto-solve or force success/failure in an investigation.
- AT-083: Crime occurrence execution is authorised by BP-14 and does not redefine its truth.
- AT-084: Generated occurrence is unique under its configured identity rule.
- AT-085: Generated occurrence uses valid person, business, location and chronology references.
- AT-086: Generated incident is not silently converted into a police case.
- AT-087: Operational incident lifecycle remains owned by BP-12.
- AT-088: Crime taxonomy remains owned by BP-13.
- AT-089: Case identity/lifecycle remains owned by BP-15.
- AT-090: Investigation actions and decisions remain owned by BP-16.
- AT-091: Evidence, forensics and custody state remain owned by their respective divisions.
- AT-092: One local utility outage affects only connected assets/areas.
- AT-093: Utility restoration is an explicit recorded event.
- AT-094: A local outage cannot affect an unconnected facility without a dependency record.
- AT-095: Environmental event carries valid location and time scope.
- AT-096: Weather/hazard effect cannot propagate outside its configured geographic scope.
- AT-097: Hazard effects on roads/facilities/services are causally linked.
- AT-098: A weather update does not rewrite historical observations.
- AT-099: Transport movement uses canonical roads/routes and valid constraints.
- AT-100: Travel time and route feasibility reconcile with distance, mode and conditions.
- AT-101: A delivery links sender, carrier and receiver events.
- AT-102: Delivery and inventory changes reconcile across owning domains.
- AT-103: Off-map trade reference does not create another playable city.
- AT-104: Essential supply shortage does not create unsupported replacement stock.
- AT-105: Business opening/closing respects BP-04 status and BP-37 time.
- AT-106: Public event has valid time, location, organiser and plausible attendance source.
- AT-107: Public-service capacity cannot be exceeded without an explicit configured exception.
- AT-108: Healthcare appointments/treatment chronology and capacity remain consistent.
- AT-109: Emergency response resource and chronology reconcile across agencies.
- AT-110: Police dispatch event is routed through BP-11 and incident state through BP-12.
- AT-111: Every dispatched unit/status transition remains chronologically auditable.
- AT-112: Patrol action respects time, distance, staffing and equipment availability.
- AT-113: Police command authority is checked against BP-05/BP-30 source records.
- AT-114: Ranks, grades, positions, authority, powers and clearance are not conflated by engine.
- AT-115: Roster/leave/attendance source remains with BP-08/BP-33.
- AT-116: Canonical geography is referenced from BP-02 and never duplicated.
- AT-117: Premises/access topology is sourced from BP-04.
- AT-118: Contradictory location identity prevents event commit.
- AT-119: Every access event resolves to a valid access point or explained mechanism.
- AT-120: Household and relationship effects reference BP-36 authoritative records.
- AT-121: Engine cannot silently rewrite relationship or household membership.
- AT-122: Person employment and financial state are updated only by owning domains.
- AT-123: Engine respects configured business/service staffing and capacity constraints.
- AT-124: Deterministic random streams are isolated by subsystem/event scope.
- AT-125: One subsystem's random draws do not shift another subsystem's stream.
- AT-126: Random output cannot override canon, authority, population or player agency.
- AT-127: Initial scenario seed and engine/configuration versions are retained.
- AT-128: Replaying identical deterministic inputs yields identical authoritative state.
- AT-129: Recorded AI output affecting state is replayed as the same versioned input.
- AT-130: Replay does not call a newer model to regenerate an authoritative prior action.
- AT-131: Replay mismatch is detected and produces retained diagnostic evidence.
- AT-132: Presentation-only output does not alter authoritative state during replay.
- AT-133: Atomic domain transition either fully commits or fully rolls back.
- AT-134: Multi-domain workflow exposes intermediate state and explicit acknowledgements.
- AT-135: A failed consumer delivery does not undo an already committed unrelated domain transaction.
- AT-136: Retry uses original event ID and idempotency key.
- AT-137: Retry cannot mutate rejected command payload.
- AT-138: Changed intent requires a new command/event ID.
- AT-139: Poison event is quarantined without blocking unrelated work.
- AT-140: Quarantined event retains source, error, attempt history and resolution authority.
- AT-141: Dead-letter record is not silently deleted.
- AT-142: Persistence failure prevents commit acknowledgement.
- AT-143: Restart loads last durable engine/domain watermarks.
- AT-144: Recovery reconciles claims, commits and delivery acknowledgements.
- AT-145: Recovery does not repeat a committed payment, arrest, dispatch or other domain action.
- AT-146: Recovery does not create a duplicate crime occurrence.
- AT-147: Recovery does not advance simulation time.
- AT-148: Recovery restores queues from authoritative schedule records and BP-37 time.
- AT-149: Integrity failure enters appropriate degraded or safe-halt state.
- AT-150: Runtime remains paused/ready after recovery until authorised resume.
- AT-151: Permission is checked before protected command dispatch.
- AT-152: Permission is rechecked at commit when authority may have changed.
- AT-153: Event payload cannot grant its actor additional permission.
- AT-154: AI agent cannot create or grant its own authority.
- AT-155: Protected medical, intelligence, evidence, payroll and financial data are redacted before context assembly.
- AT-156: Access denial is logged without exposing protected payload.
- AT-157: Administrative recovery action records actor, authority, reason and outcome.
- AT-158: Engine metrics do not disclose hidden offender/accomplice identity.
- AT-159: Operational logs use event references and redact sensitive payloads.
- AT-160: Queue depth, oldest eligible event and priority backlog are observable.
- AT-161: Event latency, throughput, retries and failures are measurable.
- AT-162: NPC activation counts and fidelity tiers are measurable without duplicating persons.
- AT-163: Database size and storage growth are observable without unapproved writes.
- AT-164: Resource pressure triggers deterministic deferral/degradation before integrity loss.
- AT-165: Critical player-facing and safety events are not silently dropped under load.
- AT-166: Low-impact ambient work can be deferred without changing committed facts.
- AT-167: Back-pressure prevents unbounded event queue growth.
- AT-168: Queue fairness prevents permanent starvation of lower-priority work.
- AT-169: Worker timeout cannot leave a domain transaction half committed.
- AT-170: Runtime load shedding never reduces a promoted person's fidelity or deletes history.
- AT-171: Text interface can inspect runtime lifecycle and relevant event status.
- AT-172: Optional map/timeline/chart projection is derived from canonical source records.
- AT-173: A visual projection cannot become an independent authoritative record.
- AT-174: Visual generation request preserves source references and provenance.
- AT-175: Narrative and event output remain coherent with prior committed records.
- AT-176: Every generated fact has source or explicit generated-event provenance.
- AT-177: A contradictory generated event is rejected or recorded as explicit uncertainty.
- AT-178: Engine does not silently overwrite an existing fact to preserve narrative flow.
- AT-179: All schedules and deadlines freeze while paused.
- AT-180: No NPC, business, service, crime, patrol, case, finance or public event progresses while player is absent.
- AT-181: Wall-clock passage while paused causes zero event execution.
- AT-182: A resume processes only due work at canonical simulation time.
- AT-183: Equal-time events execute in stable deterministic order.
- AT-184: Every event handler declares time semantics and pause behaviour.
- AT-185: Handler version changes are controlled by BP-44.
- AT-186: Schema/handler compatibility is validated through BP-38 and BP-43.
- AT-187: Unit, integration, end-to-end, replay, load, population and narrative tests are supported.
- AT-188: Test fixtures do not write to production Neon.
- AT-189: Engine invariants are checked at defined lifecycle and recovery boundaries.
- AT-190: A failed invariant blocks affected execution and emits attributable diagnostics.
- AT-191: Operations failures are detectable, attributable and recoverable.
- AT-192: Runtime service health, queue health and persistence health are independently observable.
- AT-193: Configuration changes require approved BP-44 change records.
- AT-194: Engine supports one bounded city and does not create external playable geography.
- AT-195: Business registry remains at least 10,000 without forcing 10,000 full agent loops per tick.
- AT-196: Living population never exceeds 10,000 across all roles and agents.
- AT-197: Engine activity respects the one-city sovereign jurisdiction.
- AT-198: Police remains the deepest simulation; other domains remain proportionate and coherent.
- AT-199: Text-first gameplay remains complete without optional visual rendering.
- AT-200: Storage compaction preserves event meaning, provenance, audit and causal lineage.
- AT-201: Event sequence, journal/domain commit and persistence watermarks reconcile after backup restore.
- AT-202: Engine can resume from the exact committed pause point without offline catch-up.
- AT-203: A schedule item whose due time has not arrived cannot execute early.
- AT-204: An expired event follows explicit owner-defined expiry policy and is not silently discarded.
- AT-205: A domain handler's unavailable dependency holds or rejects work according to declared policy.
- AT-206: A stale projection cannot authorise a resource-consuming action.
- AT-207: Conflicting concurrent movement/resource claims are resolved by the owning domain atomically.
- AT-208: Causal consequence events retain initiating event and source record lineage.
- AT-209: A model/provider outage produces no unvalidated world-state change.
- AT-210: A narrative retry is bounded and cannot create duplicate authoritative action.
- AT-211: A player command is not silently replaced by an NPC/system action.
- AT-212: A player decision is not overwritten by a generated preference or recommendation.
- AT-213: Engine diagnostics distinguish rejected, deferred, failed and committed work.
- AT-214: A paused runtime may serve authorised read-only inspection without world mutation.
- AT-215: Engine startup rejects population/business/geography invariants that do not match canonical records.
- AT-216: Event schema version and handler version are recorded for every committed event.
- AT-217: Replay uses stable ordering and original external inputs, not current external responses.
- AT-218: No generated output may claim an unobserved person was present at a location.
- AT-219: Business and public-service activity respects declared operating status and capacity.
- AT-220: Cross-domain event processing cannot duplicate a person's canonical identity or domain role.
- AT-221: Engine can identify and report orphan events with missing source/domain owner.
- AT-222: Orphan events are quarantined and cannot mutate domain state.
- AT-223: A committed event is never silently deleted during compaction or archival.
- AT-224: Event retention/archival preserves replay sufficiency and required case provenance.
- AT-225: A safe halt preserves last known-good state and blocks further mutation.
- AT-226: Degraded mode exposes unavailable capabilities and prevents unsafe dependent work.
- AT-227: Recovery action is itself an immutable attributable event.
- AT-228: Simulation startup and resume do not create NPC actions merely to fill an empty queue.
- AT-229: A deterministic test run with identical seed/configuration/input yields identical event outcomes.
- AT-230: Engine never performs a Neon schema/data write outside an explicitly approved implementation operation.

## 20. Cross-system interfaces and dependencies

| Division | Authoritative responsibility | BP-35 contract |
|---|---|---|
| BP-01 | Canon, player agency, global rules | Enforce invariants as non-overridable runtime constraints |
| BP-02 | City geography and canonical spatial IDs | Resolve all location references; never duplicate geometry |
| BP-03 | Person identity, population and lifecycle | Activate agents and request permanent promotion; never create duplicate persons |
| BP-04 | Businesses, organisations, property and infrastructure operators | Coordinate business/service/infrastructure events through owner handlers |
| BP-05–BP-08 | Police architecture, personnel, career, deployment | Respect authority, eligibility, roster and assignment |
| BP-09 | Police physical resources | Consume current availability/capacity; never mutate asset master |
| BP-10–BP-12 | Patrol, emergency communications and incidents | Route commands/events and respect operational chronology |
| BP-13–BP-14 | Crime taxonomy and occurrence generation | Schedule/execute authorised occurrence events; hidden truth remains protected |
| BP-15–BP-29 | Case, investigative, evidence, forensic, arrest, custody, legal and corrections domains | Route only owner-approved commands and preserve player agency |
| BP-30–BP-34 | Governance, standards, training, HR, finance/procurement | Respect authority, qualifications, approved employment and financial events |
| BP-36 | Relationships/social context | Consume relationship state and submit owner-validated changes |
| BP-37 | Canonical time/calendar/schedules | Read authoritative time and due events; never run its own clock |
| BP-38 | Schemas, constraints and records | Use validated event/record contracts and atomic domain transactions |
| BP-39 | Persistence, backup and recovery | Persist watermarks and reconcile durable execution state |
| BP-40 | Player interface | Accept explicit player commands and expose readable runtime status |
| BP-41 | Notifications/reporting | Emit source-linked outputs; respect pause and visibility |
| BP-42 | Security/permissions | Enforce actor authority, data visibility and audit |
| BP-43 | QA/testing | Provide deterministic fixtures, replay and operational evidence |
| BP-44 | Configuration/change control | Use approved versioned rules and handler configurations |

## 21. Storage and performance design

The engine is designed for event-driven operation, not continuous brute-force simulation of every entity. The target city has at least 10,000 businesses and at most 10,000 living people, including the police service and all other represented roles.

- Keep event envelopes compact and reference authoritative domain records.
- Store immutable event facts once; derive projections, queues and dashboards from source events and state watermarks.
- Avoid duplicate copies of names, addresses, biographies, financial values, inventory or case evidence.
- Use stable IDs, compact enums, indexed due-time/priority/owner/status fields and bounded payload sizes.
- Batch independent work only when ordering and atomicity remain deterministic.
- Use per-agent activation and scheduled wake-up rather than polling all persons continuously.
- Use aggregate/ambient business activity where appropriate; promote material events to event-level records.
- Never aggregate away a case-relevant person, action, location, evidence connection or transaction.
- Preserve all promoted-person detail permanently.
- Archive/compact only under BP-38/BP-39 retention and provenance rules.
- Track event volume, payload size, queue age, retries, replay data, active agents and database growth.
- Benchmark peak incident loads, shift changes, major city disruptions, weather/hazard cascades, mass public events, payroll/procurement cycles and recovery.
- Measure Neon baseline and relevant storage before any future write. Estimate incremental bytes/MiB and projected total with assumptions and uncertainty. Obtain explicit user approval before write. Measure actual growth afterward and compare with estimate.
- No seed generation, schema migration, event import, bulk person creation or bulk business generation is authorised by this specification.

## 22. Open fictional and technical configuration decisions

1. Runtime deployment shape: one modular process or a small number of isolated services.
2. Simulation step granularity and permitted active-time execution rate.
3. Event priority classes, fairness bounds and per-class queue limits.
4. Event retention, archival and replay horizon.
5. Deterministic random algorithm and seed lifecycle.
6. NPC activity decision cadence, action catalogue and fidelity promotion thresholds.
7. Exact relevance definition for permanent person promotion, while preserving the global rule.
8. Ambient business simulation frequency and aggregate precision tiers.
9. Weather/environment source or fictional deterministic model and update cadence.
10. Utility and infrastructure dependency graph baseline.
11. Transport/travel calculation model and route update cadence.
12. Cross-domain workflow timeout, compensation and expiry policies.
13. AI provider/model selection, budgets, fallback and context-retention rules.
14. AI output validation strictness and retry limits.
15. Narrative voice/personality configuration and NPC memory/forgetting rules.
16. Safe-halt blast radius and recovery authority matrix.
17. Operational metric retention and alert thresholds.
18. Runtime resource budgets for modest local hardware and Neon limits.
19. Event payload size limits and maximum causal fan-out/depth.
20. Replay compatibility policy across engine/handler/configuration versions.
21. External ingress policy for messages arriving during pause.
22. Simulation startup initial state validation and corruption response.
23. Optional visual generation formats and provenance requirements.
24. Load-shedding thresholds and which ambient activities may be deferred.
25. Exact acceptance-test execution harness and evidence format under BP-43.

## 23. Source traceability

The following source IDs are mapped to BP-35 in the authoritative crosswalk. Original wording is preserved in `docs/governance/SALTWATER_MASTER_BLUEPRINT.json`; IDs use 1-based source-array positions. A mapping is not evidence that a requirement has been implemented or verified.

| Source ID | Source division | Requirement/test intent incorporated |
|---|---|---|
| S02.R01 | Geography, land and spatial reference | Consume canonical districts, zones, parcels, addresses, coordinates, boundaries, terrain, coastlines and land use; do not duplicate geography |
| S02.T01 | Geography, land and spatial reference | Prevent duplicate or contradictory canonical locations |
| S03.R01 | Population accounting and demographic model | Respect opening population accounting, reserve headroom and 10,000 hard cap as superseded by current Saltwater canon |
| S03.T01 | Population accounting and demographic model | Reconcile population ledger and person records |
| S04.R01 | Person identity and life records | Coordinate stable person identity, attributes, history, needs, schedule, skills, employment, finances, relationships and records |
| S04.T01 | Person identity and life records | Preserve identity across jobs, addresses and relationships |
| S05.R01 | Households, relationships and social networks | Coordinate household, family, partner, dependant, friendship, conflict and professional relationship activity |
| S06.R01 | Housing, property and tenancy | Coordinate parcels, ownership, leases, occupancy, vacancies, access, maintenance and disputes through BP-04 |
| S06.T01 | Housing, property and tenancy | Prevent unexplained incompatible occupancy/ownership states |
| S07.R01 | Businesses and commercial economy | Coordinate business registry, sector, premises, ownership, operators, employees, hours, finances, assets, services and lifecycle |
| S07.T01 | Businesses and commercial economy | Require valid active business status, sector and location/mobile/virtual basis |
| S08.R01 | Employment, labour and professional life | Coordinate jobs, contracts, shifts, attendance, payroll, leave, skills, qualifications, discipline and separation through owners |
| S08.T01 | Employment, labour and professional life | Prevent unexplained shift/location conflicts |
| S09.R01 | Markets, trade, supply chains and logistics | Coordinate essential goods, wholesalers, retailers, imports/exports, gateways, warehouses, transport and distribution |
| S09.T01 | Markets, trade, supply chains and logistics | Reconcile inventory/delivery across sender, carrier and receiver |
| S13.R01 | Healthcare and public health | Coordinate providers, emergency care, capacity, appointments, treatment and public-health alerts at proportionate depth |
| S13.T01 | Healthcare and public health | Preserve consistent medical timelines and capacity |
| S15.R01 | Social care, welfare and community support | Coordinate social services, housing support, safeguarding, disability, youth/elder services and community organisations |
| S16.R01 | Utilities, energy and communications infrastructure | Coordinate utility assets/operators, capacity, outages and restoration |
| S16.T01 | Utilities, energy and communications infrastructure | Limit outage effects to connected assets/areas and require recorded restoration |
| S17.R01 | Roads, transport and mobility | Consume canonical roads, paths, junctions, restrictions, public transport, fleet, routes, timetables, stops, parking and accessibility |
| S17.T01 | Roads, transport and mobility | Enforce spatially consistent travel time and route feasibility |
| S18.R01 | Buildings, facilities and physical assets | Coordinate premises, facilities, floor plans, access points, rooms, access controls and asset condition |
| S18.T01 | Buildings, facilities and physical assets | Resolve every access event to a real access point, actor or explained mechanism |
| S19.R01 | Environment, weather and natural hazards | Coordinate local weather, daylight, tides/water, seasons, pollution and hazards where geographically relevant |
| S19.T01 | Environment, weather and natural hazards | Require location- and time-valid environmental facts |
| S20.R01 | Food systems and essential services | Coordinate food production/procurement, storage, distribution, retail, waste and emergency supply |
| S20.T01 | Food systems and essential services | Reconcile essential supply states across stock and delivery |
| S21.R01 | Culture, media, recreation and civic life | Coordinate media, public communications, events, venues, sports, cultural bodies and gatherings |
| S21.T01 | Culture, media, recreation and civic life | Require public events to have time, place, organiser and plausible attendance |
| S22.R01 | Emergency services and civil protection | Coordinate locally relevant fire/rescue, ambulance, coast/emergency response, disaster coordination and mutual aid |
| S22.T01 | Emergency services and civil protection | Reconcile resource availability and response chronology across agencies |
| S23.R01 | Police service governance and structure | Respect distinct mandate, command, rank, grade, position, authority, powers, clearance, divisions, units and reporting lines |
| S25.R01 | Police duty rosters, staffing and deployment | Coordinate shifts, rosters, leave, absences, minimum staffing, specialist availability, patrol areas and command coverage |
| S27.R01 | 911, call-taking, CAD and dispatch | Route emergency/non-emergency intake, caller identity/anonymity, recording, triage, incident creation, dispatch, radio, status and closure |
| S27.T01 | 911, call-taking, CAD and dispatch | Preserve chronological audit of every dispatched unit/status transition |
| S28.R01 | Patrol, response and field operations | Coordinate patrol presence, beat coverage, response, arrival, risk, public contact, traffic and field decisions |
| S28.T01 | Patrol, response and field operations | Enforce time, distance, staffing and equipment constraints |
| S29.R01 | Incidents, crime taxonomy and occurrence generation | Coordinate broad crime/non-crime incident taxonomy and reporting routes without taking domain ownership |
| S29.T01 | Incidents, crime taxonomy and occurrence generation | Require unique plausible generated incidents linked to valid entities and chronology |
| S31.R01 | Victims, witnesses, suspects and persons of interest | Coordinate role-specific case links, contact, vulnerability, risk, statements, availability and procedural status without assuming guilt |
| S33.R01 | Forensics and specialist examination | Coordinate forensic submissions, prioritisation, methods, results, limitations, contamination, quality and interpretation |
| S36.R01 | Surveillance, observation and technical monitoring | Coordinate authorised observation, CCTV/ANPR, coverage, blind spots, time drift, retention and retrieval |
| S40.R01 | Complaints, oversight and public accountability | Coordinate public complaints, independent review, internal investigations, inspections, findings, remedies and outcomes |
| S41.R01 | Time, calendar, schedules and simulation clock | Consume one authoritative in-world clock, calendar, time zones, shifts, opening hours, deadlines and ordering |
| S41.T01 | Time, calendar, schedules and simulation clock | Use one canonical time basis and stable timestamp ordering |
| S42.R01 | Simulation engine, causality and world activity | Coordinate people, organisations, services, incidents, schedules, resources, weather and time through auditable deterministic event processing where feasible |
| S42.T01 | Simulation engine, causality and world activity | Replay recorded event sequences to the same authoritative state where specified |
| S43.R01 | AI generation, narrative and player agency | Generate detailed, varied, naturalistic text consistent with records, knowledge, voice and uncertainty |
| S43.T01 | AI generation, narrative and player agency | Prevent hidden truth leakage before exact reveal trigger |
| S45.R01 | Maps, diagrams and visual evidence | Support optional maps, layouts, timelines, charts and forensic visuals from canonical records |
| S46.R01 | Database, schemas and persistence | Use Neon PostgreSQL for persistence, GitHub for source/spec/migration history and ChatGPT as user-facing AI partner/interface |
| S50.R01 | Testing, validation and simulation quality | Support unit, integration, schema, migration, end-to-end, replay, load, population, storage and narrative-quality tests |
| S51.R01 | Operations, observability and maintenance | Track service health, errors, latency, queues, resource use, database size, failed events and recovery |
| S51.T01 | Operations, observability and maintenance | Make operational failures detectable, attributable and recoverable |

**Traceability note:** The original source's opening population detail (9,500 = 9,000 residents + 500 police) is superseded by the current binding Saltwater canon. The 10,000 hard cap remains binding; the old opening composition is not reintroduced by this mapping.

## 24. Completion status

- Specification: **DESIGNED_DRAFT**; user review/approval pending.
- Implementation: **NOT_STARTED**.
- Test execution: **NOT_STARTED**. The 230 acceptance tests above are criteria, not execution evidence.
- Verification: **NOT_STARTED**.
- Neon: **No database write performed or authorised**.
- Next division in fixed numeric order: **BP-36 — Relationships and Social Context**.
