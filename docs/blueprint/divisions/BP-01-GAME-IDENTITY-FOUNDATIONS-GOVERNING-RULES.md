# BP-01 — Game Identity, Foundations and Governing Rules

**Project:** Saltwater  
**Blueprint:** Saltwater Master Blueprint BP-01–BP-44  
**Version:** 1.0  
**Status:** `DESIGNED` — reconciled against adopted Saltwater canon and approved for implementation  
**Date:** 2026-11-22  
**Authority:** User-owned canon and final design approval. The master framework and binding canon were approved 2026-11-23; BP-01 was reconciled and directed for completion on 2026-11-26. Design approval is distinct from implementation, testing and verification.  
**Parent:** `docs/blueprint/SALTWATER-MASTER-BLUEPRINT.md`  
**Traceability:** 52→44 crosswalk v1.1; source IDs retained below.

---

## 1. Purpose and authority

BP-01 is Saltwater's foundational game charter. It defines the identity, purpose, player experience, fixed world boundaries, governing principles, agency, information boundaries, simulation continuity, institutional depth, design authority, scope control and completion governance applying to all 44 divisions.

BP-01 establishes global rules. It does not take ownership of the detailed operational rules, data schemas or runtime algorithms assigned to later divisions. Domain divisions must implement BP-01's invariants in their own areas. BP-35 coordinates runtime execution but does not replace domain ownership; BP-38 owns record/schema standards; BP-43 owns test governance; BP-44 owns controlled configuration and change.

A conflict between divisions is recorded, assigned to an owner, assessed for affected requirements and resolved through an explicit, versioned decision. No system may silently reinterpret, weaken or bypass a binding rule.

**Authority hierarchy**
1. Explicit user-approved canon and recorded user decisions.
2. Approved Saltwater master blueprint and approved division specifications.
3. Approved, versioned design decisions and change records.
4. Implemented behaviour, only where consistent with approved design.
5. Draft source material, proposals, generated content and assumptions.

An implementation, source document or AI-generated statement cannot overrule user-approved canon. The former 52-division document remains source material for traceability; it is not automatically approved in its entirety by adopting the 44-division structure.

**Traceability:** P01, M01, M02, M06, M08; S01.R01–R03; S43.R01–R05; S52.R01–R04.

## 2. Game identity

Saltwater is an entirely fictional, persistent, text-first police simulation set in a fictional sovereign independent city-state named **Saltwater**. Saltwater contains one city and one sovereign jurisdiction. It is not a region of another country, a collection of cities, or a world-expansion framework.

The game models:
- One player-controlled police officer and that officer's individual experience.
- A deeply simulated police service with persistent personnel, command, units, resources, duties, operations and accountability.
- A coherent population, built environment, businesses, public institutions, services, economy, infrastructure and social world.
- Crime, incidents, investigations, evidence, forensic work, justice outcomes and their long-term consequences.
- A persistent causal world whose records, identities and history remain coherent across all 44 divisions.

All people, organisations, places, laws, offences, procedures, evidence, records and events are fictional game-world content. The user is the sole human player; every other person is an NPC. NPCs act autonomously according to their roles, knowledge, schedules, capabilities and world conditions. Real-world entities are not implicitly part of Saltwater. Real-world legal, regulatory, staffing, approval or verification requirements do not govern fictional gameplay; the adopted fictional game rules do. External production database writes and permission changes remain separate real-system actions and retain their explicit approval boundary.

**Traceability:** C01–C02; S01.R01; S43.R01.

## 3. Binding world canon

These are hard constraints, not targets that may be exceeded by convenience.

### 3.1 Sovereignty and geographic boundary
- Saltwater is one sovereign city-state, one city and one jurisdiction.
- No second playable city, external territory, expansion map or additional sovereign jurisdiction.
- External places may be named only as off-map references required for origins, trade, travel, supply, migration or case context.
- Off-map references do not create playable locations, local populations, police districts or additional world scope.
- Every in-world location resolves to Saltwater's canonical spatial system or is explicitly classified as off-map context.
- BP-02 owns the canonical geography and location hierarchy.

### 3.2 Population
- Maximum: **10,000 living people in total**, including police and every other countable person.
- Opening baseline: **9,000 residents + 500 police = 9,500 living people**.
- Remaining capacity at opening: **500**. This is headroom, not an additional population.
- Police are included in the total and must never be added a second time.
- Every person is counted once by stable person identity, regardless of multiple roles, jobs, household memberships or population categories.
- Population accounting must define treatment of residents, temporary residents, visitors, commuters, officials and other persons. No represented living person may be silently excluded from the authoritative count.
- Births and arrivals consume capacity; deaths and qualifying permanent exits release capacity. Capacity-changing transactions must be atomic and auditable.
- An operation that would create 10,001 living people must be rejected without partial side effects.
- Approximate police strength is 500; each police employee has an individual persistent record and is part of the same population ledger.
- BP-03 owns population identity/counting/capacity; BP-06 owns police-personnel records; BP-38 owns integrity constraints; BP-43 verifies boundaries.

### 3.3 Businesses
- Saltwater must contain at least **10,000 distinct businesses**.
- A business must be a coherent identifiable entity, not a duplicate placeholder created only to reach a count.
- Each active business must have a stable ID, status, sector, ownership/operator basis and a valid premises, mobile or virtual operating basis.
- Business records must support the functions relevant to policing and city coherence: people, employment, premises, hours, access, services, assets, transactions, records and lifecycle.
- The 10,000-business minimum is a separate entity-count requirement; it does not create additional people or alter the population cap.
- BP-04 owns business identity and operations; BP-38 owns shared identity/data standards.

### 3.4 Simulation depth
Police is the deepest and primary simulation. Other institutions and city systems must function sufficiently to create, support, constrain and respond to policing and to produce credible persistent consequences. They must not be decorative placeholders where their operation affects play. They are not automatically required to have police-equivalent depth.

**Traceability:** C03–C07; P02–P03,P05–P06; S03.R01–R05; S07.R01–R04.

## 4. Primary experience and connected simulation layers

Saltwater is one shared simulation with connected layers, not separate games:

1. **Personal:** player identity, employment, rank, appointment, position, qualifications, authority, clearance, duties, resources, relationships, career and history.
2. **Operational:** calls, dispatch, patrol, deployment, incidents, scenes, public contacts, decisions, reports, investigations and outcomes.
3. **Institutional:** police command, supervision, units, staffing, training, resources, finance, administration, governance, standards and accountability.
4. **City/world:** people, households, businesses, properties, organisations, public services, infrastructure, economy, routines, events, transport, environment and relationships.

Events may affect several layers. A field action may change an incident, create evidence, affect a person's life, require supervision, alter public confidence and affect the player's career. Such effects must arise from explicit rules and persisted events, not narrative assertion alone.

Each division owns its domain facts. Cross-division effects use stable references and defined events/contracts. BP-35 coordinates; it does not become the owner of every domain's substantive rules.

**Traceability:** P02,P05–P07; S42.R01–R03.

## 5. Player role, perspective and agency

### 5.1 One individual officer
- The player controls one individual police officer at a time.
- A recruit-start option must be available where selected by the player.
- The player character has one persistent identity and a current, historically traceable employment and assignment state.
- The player does not directly control the whole department, other officers or the city.
- Other officers and NPCs act according to their own roles, knowledge, schedules, capabilities, instructions and world conditions.

### 5.2 Agency contract
The player chooses what the character attempts within the character's knowledge, capability, current status, authority, qualifications, permissions, location and available resources. The simulation resolves the result from established world state and rules.

The system must never silently:
- choose a material player decision;
- convert a question into an action;
- convert an intention into an attempt;
- convert an attempt into successful completion;
- claim an action succeeded before resolution;
- invent a record, authority, permission, resource or result;
- bypass a required decision or review;
- auto-solve an investigation or select the player's investigative direction.

Actions may succeed, fail, be delayed, be blocked, be interrupted, produce partial results or create unintended consequences. Results must be causally supported and reported accurately.

### 5.3 Distinct action states
Every action-capable workflow must distinguish at least:
- information request/question;
- proposal or intention;
- command issued;
- validation result;
- accepted/queued action;
- action started;
- action interrupted/failed/blocked;
- completed action;
- resulting record/event;
- later correction, review or reversal.

A request is not proof of execution. A completed action must have a result and attributable record.

### 5.4 Player information
The interface exposes only information the character is entitled and reasonably able to access through available channels. It must distinguish:
- known by the player character;
- available to request or discover;
- restricted or inaccessible;
- suspected, inferred or uncertain;
- held by an NPC;
- present in hidden world state but not known to the character.

**Traceability:** P08; S43.R01–R04; S44.R02.

## 6. Knowledge, uncertainty and hidden truth

The simulation maintains a strict separation between:
1. authoritative hidden world truth;
2. facts known to individual NPCs;
3. facts available to the player character;
4. records and evidence collected;
5. allegations, reports and claims;
6. intelligence and analytical assessments;
7. hypotheses, inferences and opinions;
8. findings established through the fictional justice process.

These categories must not be collapsed. A suspect designation is not guilt; an allegation is not proof; intelligence is not automatically evidence; a plausible inference is not an established fact; a court outcome does not rewrite what investigators originally knew.

### 6.1 Absolute reveal gate
The identity of a hidden culprit, perpetrator or accomplice must never be disclosed to the player before the player types the exact command:

`bingo`

The trigger is exact and deliberate. Near-matches, quoted text, accidental substrings, inferred intent or AI interpretation do not qualify. The reveal gate applies across every interface, report, notification, narrative, tool result and generated response.

Before the exact trigger:
- Do not name, identify or indirectly expose the hidden perpetrator/accomplice.
- Do not leak identity through uniquely identifying descriptions, metadata, ordering, labels, summaries or cross-references.
- Do not provide unsolicited solution hints or tell the player what to investigate next.
- Present available records, observations, statements, evidence and actions without steering the player to the answer.
- Do not conceal information the character has legitimately obtained; instead preserve the distinction between disclosed evidence and the still-hidden authoritative truth.

After the exact trigger, reveal only the permitted hidden solution information for the relevant case, with appropriate explanation of the underlying fictional truth. The trigger does not authorise rewriting records or changing the case's historical state.

### 6.2 NPC knowledge
NPC knowledge must be bounded by their identity, role, perception, access, experience, communications and chronology. An NPC cannot know facts merely because they exist in the simulation. Generated dialogue must not leak hidden system truth.

**Traceability:** P08; S34.R03; S43.R02–R04; S48.R02; X05.

## 7. Core gameplay cycle

The detailed commands and workflow are owned by BP-40 and relevant domain divisions. The foundational cycle is:

1. **Establish state:** current in-game date/time, duty status, rank/position/assignment, location, availability, resources, active work and known information.
2. **Receive/select work:** show calls, duties, instructions, tasks, incidents and opportunities actually available to the character.
3. **Understand:** present accessible information with source, time, status and uncertainty where relevant.
4. **Choose:** player selects a question, decision, command or attempted action.
5. **Validate:** check identity, role, authority, competence, clearance, resources, location, timing, dependencies and current state.
6. **Resolve:** determine success, failure, delay, partial result or other outcome from the world state and domain rules.
7. **Persist:** record material actions, outcomes, state changes, provenance, timestamps and resulting tasks.
8. **Present:** show the changed state and allow the player to choose the next action.

This is a conceptual contract, not a requirement for eight screens or a rigid interaction sequence. Simple information queries need not be treated as operational actions.

**Traceability:** S43.R01,R04; S44.R01–R04.

## 8. Time and simulation continuity

- One authoritative in-world clock/calendar governs all time-dependent systems.
- BP-37 owns clock, calendar, time zones, scheduling and time-advance semantics.
- BP-35 owns event execution and pause/resume coordination.
- All domains use canonical timestamps and must not create competing clocks.
- Time may advance only through explicit player action or defined, permitted in-game simulation processing.
- **No simulation time advances while the player is outside the simulation, has exited, or is absent.**
- No offline catch-up, hidden background progression, NPC routine advancement, deadline expiry, incident generation or world-state mutation may occur during absence.
- On return, resume from the last authoritative in-game time/state; do not simulate elapsed real-world time.
- A deliberate time-advance action must disclose the intended effect and obey the relevant validation and player-control rules.
- Historical timestamps remain unchanged when a record is corrected or supplemented. Corrections are additive, attributed and traceable.
- Queued events must not execute during the paused/absent state.
- All scheduling, travel, opening hours, appointments, rosters, evidence timelines, custody clocks and deadlines use the same time basis.

**Traceability:** P06,P09; C08; S41.R01–R03; S42.R04; X03,X07.

## 9. Persistent world, identity and records

Persistence covers the player, police service, population, businesses, organisations, locations, incidents, cases, evidence, finances, resources, relationships, schedules, decisions and relevant historical state.

Global rules:
- Every persistent entity has a stable unique identity.
- A name, address, role, job, status or relationship change does not silently create a new identity.
- Every consequential state change has provenance: actor/system, event, time, reason/source and affected record.
- Current state must be reconstructible from valid state transitions or authoritative snapshots plus event history.
- Original records remain distinguishable from amendments, corrections, supplements, derived summaries and interpretations.
- No derived summary may silently replace or destroy a source record.
- Referential integrity and domain ownership must prevent duplicate or contradictory authorities.
- Time-dependent facts must be effective-dated and historically queryable.
- A person materially connected to police activity or a case is promoted to persistent full-detail status and is never downgraded or erased thereafter.
- Processing tiers may reduce computation, not erase identities, established facts, history or continuity.
- Domain divisions own their records; BP-38 owns common data standards; BP-39 owns persistence and recovery.

Storage efficiency is subordinate to meaning and fidelity. Normalisation, compact keys, enums, references, deduplication and lossless compression are permitted; omission of meaningful narrative, facts, relationships, provenance, chronology, exceptions or evidence is not. No Neon write may occur without the required measured baseline, credible estimate, method/assumptions/uncertainty, explicit user approval and post-write measurement.

**Traceability:** P04–P06,P10; C03–C07; S04.R01–R03; S46.R01–R05; S47.R01–R05; S49.R01–R03.

## 10. NPCs and world activity

Saltwater must feel like a coherent living city, not a static set of records created only when the player asks a question. People, organisations, businesses and services have identities, schedules, activities, relationships and changing circumstances according to their owning divisions.

The simulation may use relevance-based processing and different computational detail levels. This is an implementation strategy, not permission to:
- create duplicate identities;
- contradict established facts;
- silently change history;
- downgrade promoted people;
- let background processes advance while the player is absent;
- grant NPCs knowledge they could not have obtained;
- generate events without causal, spatial, temporal and resource validity.

City systems must be sufficiently functional to support police work: employment, commerce, premises, occupancy, transport, utilities, health, education, welfare, government, emergency response, public finance, culture, media and other source domains. Their detail remains proportionate to their gameplay and police-support function.

**Traceability:** P02,P03,P05,P07; S04.R02–R03; S07.R01–R04; S42.R01–R03.

## 11. Consequences, fairness and causality

All generated facts and outcomes must respect:
- approved canon and current configuration;
- prior authoritative records and historical chronology;
- location, geography, travel feasibility and physical access;
- time, schedules, opening hours and availability;
- identity, relationships, employment and knowledge;
- authority, competence, permission and institutional procedure;
- staffing, equipment, stock, money and capacity;
- event causes, dependencies and effects.

The simulation must not guarantee success merely because the player requests it, nor arbitrarily deny success to force a preferred story. Uncertainty may arise from incomplete information, unreliable sources, human behaviour, physical constraints, resource limits, time and chance only where the relevant domain defines it.

No impossible simultaneous states, unexplained mutation, unbounded causal loop or untraceable consequential outcome is permitted. Contradictions must be surfaced as errors/conflicts and resolved through explicit correction, not silently overwritten.

**Traceability:** P06–P08; S42.R01–R03; S43.R01–R05.

## 12. Authority, roles and institutional boundaries

The following are distinct and must not be conflated:
- rank;
- grade;
- appointment;
- position;
- command authority;
- legal/in-world power;
- qualification and competence;
- clearance and information access;
- unit membership;
- assignment and deployment;
- current duty status.

A person's possession of one does not automatically confer another. Authority is validated for the specific action, jurisdiction, time, role and conditions.

Police is the principal deeply simulated institution. Other public bodies, private organisations, businesses, service providers and community structures must have enough defined identity, function, personnel, locations, schedules, authority and records to support credible interaction and consequences.

No division may claim ownership of another division's substantive domain. BP-35 coordinates events but does not define every domain's rules. BP-38 defines shared record/data standards but does not become the owner of police, business, legal or other substantive facts.

**Traceability:** S01.R02; S11.R01–R03; S23.R01–R04; S26.R01–R03; P05–P07.

## 13. Text-first interface and presentation

Text is the permanent, complete primary interface. The laptop-style interface must support the entire essential gameplay loop: status, navigation, commands, records, reports, dialogue, chronology, evidence, casework, personnel, dispatch, decisions and system feedback.

Maps, diagrams, charts, timelines and forensic scene visuals may supplement play when useful or requested. They are never prerequisites for understanding or completing essential gameplay. Visuals must derive from canonical data and must not contradict authoritative text/records.

Presentation may be concise for navigation and metadata, but underlying records and narrative must retain full required detail. Do not compress away content to make a display shorter; provide pagination, filtering, references or expandable detail instead.

BP-40 owns interface and command workflows. BP-02 and relevant domain divisions own source data for visuals. BP-38 preserves the authoritative records.

**Traceability:** C08; S44.R01–R04; S45.R01–R03; X08.

## 14. Technical platform boundary

The adopted architecture is:
- **Neon PostgreSQL:** persistent authoritative database.
- **GitHub:** source control, versioned specifications, migrations, tests and evidence.
- **ChatGPT:** user-facing AI partner/interface.

This statement fixes the intended project architecture; it does not assert that every integration or feature is implemented or currently connected. Connectivity must be demonstrated by successful tests before it is claimed.

BP-38 owns schemas, constraints, transactions and data ownership. BP-39 owns persistence/recovery. BP-40 owns the player-facing interface. BP-43 owns verification. BP-44 owns version/configuration/change control.

No Neon migration, schema change, seed, import, bulk write or upload is authorised by this specification. Every proposed write remains subject to measured storage governance and explicit user approval.

**Traceability:** S46.R01–R05; S47.R01–R05; S49.R01–R03; S51.R01–R03.

## 15. Scope boundaries and exclusions

The following are prohibited or out of scope unless the user explicitly changes canon:
- a second playable city or external territory;
- expansion beyond the single Saltwater city-state;
- a population above 10,000 living people;
- counting police outside the population cap;
- a second, hidden or parallel population registry;
- fewer than 10,000 active/valid business entities at the required baseline;
- indistinguishable filler businesses used only to satisfy the count;
- equal-depth simulation of every non-police institution;
- graphics as a prerequisite for gameplay;
- offline time advancement or hidden catch-up;
- unapproved Neon writes;
- invented implementation, test or verification status;
- unapproved structural changes to BP-01–BP-44.

A proposal that affects a boundary must identify its purpose, affected divisions, entities, state changes, dependencies, resource/storage impact, tests and required approval before adoption.

**Traceability:** C01–C09; M07; S01.R03; S47.R04–R05; S52.R01–R04.

## 16. Foundational records and lifecycle contracts

BP-01 does not define physical database schemas. It requires the following logical governance records to exist under BP-38/BP-44 ownership:

| Record | Required content | Owner |
|---|---|---|
| Canon rule | Stable rule ID, statement, scope, effective version, status, authority, source and affected divisions | BP-44 |
| Design decision | ID, issue, options, decision, rationale, approver, date/version, affected requirements/divisions | BP-44 |
| Requirement trace | Source ID, target BP ID, requirement text/reference, owner, design artefact, test, evidence and status | BP-38/BP-43/BP-44 |
| Scope proposal | Purpose, in/out scope, impacts, dependencies, risks, storage estimate, tests and decision | BP-44 |
| Conflict record | Conflicting rules/records, impact, interim handling, owner, resolution and evidence | BP-01/BP-44 |
| Approval record | Exact artefact/version, approving authority, approval scope, date and conditions | BP-44 |
| Completion record | State, implementation reference, test result, dependency status and evidence link | BP-43/BP-44 |

### 16.1 Canon and design lifecycle
A canon/design change follows:

`PROPOSED → IMPACT_ASSESSED → AWAITING_USER_DECISION → APPROVED or REJECTED → VERSIONED`

An approved amendment is effective only at its recorded version/effective point. Rejected proposals do not alter canon. An urgent inconsistency may be marked `BLOCKED`; it must not be resolved by silent reinterpretation.

### 16.2 Division completion states
Use exactly these distinct states:
- `NOT_STARTED`
- `DESIGNED`
- `IMPLEMENTED`
- `TESTED`
- `VERIFIED`
- `BLOCKED`
- `RETIRED`

State semantics:
- `DESIGNED`: complete specification reviewed against source requirements; user approval recorded where required.
- `IMPLEMENTED`: corresponding code/schema/configuration exists and is linked.
- `TESTED`: required tests executed and results recorded; failed tests remain visible.
- `VERIFIED`: implementation and tests pass, dependencies reconcile, and reproducible evidence is linked.
- `BLOCKED`: a documented unresolved dependency, conflict or failure prevents progression.
- `RETIRED`: formally retired by approved change; historical records and traceability remain.

No status may be inferred from the existence of a document or commit alone. A division cannot be marked VERIFIED on design prose.

**Traceability:** M03–M08; P01,P10; S50.R01–R03; S52.R01–R04.

## 17. Dependencies and ownership map

| Concern | Primary owner | BP-01 relationship |
|---|---|---|
| Sovereignty/geography | BP-02 | Enforces single-city boundary |
| Population/identity | BP-03 | Enforces 10k total and continuity principles |
| Built world/businesses | BP-04 | Enforces 10k+ coherent business requirement |
| Police structure/personnel/career | BP-05–BP-08 | Enforces one-officer perspective and distinct authority concepts |
| Police resources/operations/dispatch/incidents | BP-09–BP-12 | Enforces agency, causality and operational continuity |
| Crime/cases/investigation | BP-13–BP-16 | Enforces uncertainty, agency and no auto-solving |
| Victims/suspects/interviews/surveillance/intelligence | BP-17–BP-21 | Enforces role, knowledge and hidden-truth boundaries |
| Scenes/evidence/forensics | BP-22–BP-24 | Enforces provenance and source preservation |
| Arrest/custody/legal/courts/corrections | BP-25–BP-29 | Enforces authority and historical integrity |
| Department governance/standards/training/HR/finance | BP-30–BP-34 | Enforces institutional coherence and accountability |
| Runtime causality | BP-35 | Coordinates; does not own domain truth |
| Relationships/social context | BP-36 | Enforces stable identity and historical relationships |
| Time/scheduling | BP-37 | Owns authoritative clock semantics |
| Records/database | BP-38 | Owns schemas, IDs, integrity and data standards |
| Persistence/recovery | BP-39 | Owns durable state and restoration |
| Interface | BP-40 | Enforces complete text-first gameplay and knowledge boundary |
| Notifications/reporting | BP-41 | Enforces truthful, permission-aware delivery |
| Security/permissions | BP-42 | Enforces role and hidden-information controls |
| Testing/QA | BP-43 | Verifies requirements and invariants |
| Configuration/change control | BP-44 | Records approved canon, versions and traceability |

No domain owner may redefine a shared identity, clock, population count, jurisdiction or hidden-information rule independently.

## 18. Acceptance criteria and test suite

BP-01 is design-complete only when all applicable criteria below are specified and linked to the target divisions. It is implementation-verified only when the corresponding tests execute against the implemented system and evidence is retained.

### A. Identity, world and scope
- **A01:** Game is identified as fictional sovereign Saltwater city-state; one city and one jurisdiction only.
- **A02:** No external location can become playable without explicit canon amendment.
- **A03:** 10,000 living-person cap includes police; opening ledger is 9,000 + 500 = 9,500 with 500 headroom.
- **A04:** A 10,001st person creation/arrival is rejected atomically; no partial record, duplicate or side effect remains.
- **A05:** Police are counted once in total population and have individual persistent personnel records.
- **A06:** At least 10,000 distinct coherent businesses are required; duplicate/filler entities fail acceptance.
- **A07:** Business count is not conflated with population count.
- **A08:** Non-police institutions are operationally credible and proportionate, not decorative or equal-depth by default.

### B. Player agency and action semantics
- **B01:** Only one player character is active at a time.
- **B02:** Recruit start is available where selected.
- **B03:** Question, intention, command, attempt, accepted action and completed action are distinguishable.
- **B04:** A question does not mutate world state.
- **B05:** An unauthorised or impossible action is rejected with a truthful reason and no forbidden side effect.
- **B06:** A failed or partial action is not reported as successful.
- **B07:** The simulation does not choose material player decisions or auto-solve investigations.
- **B08:** Outcomes follow the authoritative state, constraints and domain rules.

### C. Knowledge and hidden truth
- **AC-C01:** Character-visible information is permission- and knowledge-bounded.
- **AC-C02:** NPCs cannot know facts outside their plausible information history.
- **AC-C03:** Hidden culprit/accomplice identity remains undisclosed before exact `bingo`.
- **AC-C04:** Near-match, quoted, accidental or substring uses do not trigger reveal.
- **AC-C05:** Reports, summaries, metadata, notifications, search results and generated text cannot leak hidden identity indirectly.
- **AC-C06:** No unsolicited investigative solution hints or next-step instructions are supplied.
- **AC-C07:** Legitimately obtained evidence remains available without disclosing hidden truth beyond its actual content.

### D. Time and continuity
- **AC-D01:** One canonical in-game clock is used across all divisions.
- **AC-D02:** Closing/exiting/absence causes zero simulation-time advancement and zero background world-state progression.
- **AC-D03:** Reopening resumes at the last saved in-game time/state, without offline catch-up.
- **AC-D04:** Queued events remain paused while absent.
- **AC-D05:** Time advancement requires an explicit permitted in-game action.
- **AC-D06:** Corrections do not rewrite original timestamps or erase history.

### E. Persistence and causality
- **AC-E01:** Stable IDs persist across name, job, address, role and relationship changes.
- **AC-E02:** Promoted persons never downgrade or lose established facts.
- **AC-E03:** Every consequential state change has source, actor/system, time and reason.
- **AC-E04:** Original records and later amendments remain distinguishable.
- **AC-E05:** No contradictory duplicate authoritative records can be created.
- **AC-E06:** Cross-domain resource, money, time, capacity and location changes reconcile.
- **AC-E07:** Replaying a deterministic event sequence produces the same authoritative state where deterministic replay is specified.
- **AC-E08:** A contradiction or invalid transition is surfaced and blocked/recorded, not silently overwritten.

### F. Interface, architecture and governance
- **AC-F01:** Essential gameplay is possible through text alone.
- **AC-F02:** Optional visuals trace to authoritative records and cannot override them.
- **AC-F03:** Neon/GitHub/ChatGPT roles are documented without claiming untested live connectivity.
- **AC-F04:** No Neon write is executed without measured baseline, credible estimate and explicit user approval.
- **AC-F05:** Post-write actual storage delta is measured and compared to estimate.
- **AC-F06:** Every requirement maps to design, implementation, test and evidence references.
- **AC-F07:** DESIGN, IMPLEMENTED, TESTED and VERIFIED remain distinct.
- **AC-F08:** No division is VERIFIED without passing tests, reconciled dependencies and reproducible evidence.
- **AC-F09:** Canon/structure amendments are user-approved and versioned.
- **AC-F10:** BP-01–BP-44 structure is not altered by implementation convenience.

### G. Test classes required
Positive, negative, boundary, adversarial, permission, concurrency/race, replay, recovery, integration, population-scale, business-scale, storage-growth, narrative leakage and regression tests. Each test must specify preconditions, action/input, expected state/result, prohibited side effects, evidence and traceable requirement IDs.

## 19. Source traceability register

This division owns the global charter interpretation for the following source requirements. Operational details remain with domain owners.

| Source IDs | BP-01 obligation |
|---|---|
| C01–C09 | Binding canon, population/business limits, police depth, interface and priority |
| P01–P10 | Global governing principles |
| M01–M09 | Authority, source status, dependency, completion, change and traceability governance |
| S01.R01–R03; S01.T01–T02 | Sovereignty, jurisdiction, authority and no expansion |
| S23.R01–R04; S23.T01 | Police structure and authority distinctions |
| S34.R03; S34.T01 | No leading prompts or hidden solution disclosure |
| S43.R01–R05; S43.T01–T02 | AI generation, player agency, knowledge and reveal boundary |
| S44.R01–R04; S44.T01 | Text-first player workflow |
| S46.R01; S46.T01 | Platform architecture and no false connectivity claims |
| S47.R04–R05; S47.T01–T02 | Storage approval and measured growth |
| S48.R02; S48.T01 | Hidden truth and restricted-information boundary |
| S49.R02; S49.T01 | Protection of canon and authoritative records |
| S50.R03; S50.T01 | Evidence-based completion |
| S52.R01–R04; S52.T01 | Canon, versioning, change and traceability |

The complete 52-division mapping remains in `SALTWATER-52-TO-44-CROSSWALK.md`. This register is not a substitute for that crosswalk.

## 20. Open decisions and non-assumptions

The following are implementation details owned by the named divisions, not unresolved BP-01 canon decisions:
- exact city geometry, districts, roads, parcels and address register (BP-02);
- population membership definitions for transient persons and the exact atomic admission/exit event model (BP-03);
- business sector distribution, operating premises and generation method for the 10,000+ registry (BP-04);
- police organisation, ranks, positions, staffing structure and career rules (BP-05–BP-08);
- detailed crime taxonomy, legal framework and procedural rules of the fictional jurisdiction (BP-13,BP-25–BP-29);
- exact simulation clock commands and permitted time-advance increments (BP-37);
- database schema, event storage, backup policy and storage benchmark design (BP-38,BP-39);
- exact command grammar and screen/navigation model (BP-40);
- detailed permission matrix and secret-handling implementation (BP-42).

These are not omissions from the global charter; they are explicit domain-owned details. No unapproved assumptions may be presented as settled canon.

## 21. Core universal naming authority — SW-UNS-001

Saltwater has one mandatory Universal Naming Standard: [SW-UNS-001](../decisions/SW-UNS-001-universal-naming-standard.md). It is a core foundation applying to every named entity and all 44 blueprint divisions. It is not optional, a later enhancement or a domain-local preference.

Binding BP-01 rules:
- Every named entity has a permanent stable entity ID and a unique canonical name.
- Canonical names are unique in the shared Saltwater namespace across entity types, not merely within a division, table, district or category.
- A central authoritative registry controls normalization, exact/near-duplicate detection, reservations, aliases, historical names and concurrency-safe creation.
- Names are never identity keys. Entity IDs remain immutable when names change.
- Retired, former, deceased, closed, demolished or superseded names remain historically reserved and cannot be recycled for another entity.
- All generated, imported, NPC-created, player-created and manually entered names use the same reservation path. No division or script may bypass it.
- Domain divisions own their vocabularies and entity lifecycles but must comply with the central standard. BP-38 owns registry persistence/constraints; BP-43 owns acceptance tests; BP-44 governs controlled vocabulary/configuration changes.
- Existing canon names are preserved and registered before new names are generated. Existing conflicts are recorded for explicit resolution, never silently overwritten.

This requirement does not alter the fixed BP-01–BP-44 structure. Adoption of the policy does not claim the registry or tests are implemented and does not authorise Neon production writes.

## 22. Completion statement

**Design status:** `DESIGNED_DRAFT`; this is a complete first-pass BP-01 specification for user review, subject to the open decisions and cross-division contracts above.  
**Implementation status:** `NOT_STARTED` unless independently established by linked code/schema evidence.  
**Test status:** `NOT_STARTED` unless test results are independently recorded.  
**Verification status:** `NOT_STARTED`.

No Neon schema, migration, seed, import, upload or database write is performed or authorised by this document. The user has separately reserved explicit approval for production Neon writes and permission changes.
