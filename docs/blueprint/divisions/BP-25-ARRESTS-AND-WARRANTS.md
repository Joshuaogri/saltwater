# BP-25 — Arrests and Warrants

**Project:** Saltwater — fictional sovereign city-state, one city, one jurisdiction  
**Blueprint division:** BP-25 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test execution:** NOT_STARTED | **Verification:** NOT_STARTED  
**Authority:** Fixed BP-01–BP-44 structure and unchanged 52-division source. No canon or division structure is changed.

## 1. Purpose

BP-25 defines the complete police operational system for arrest authority, arrest decisions and execution, warrant applications and execution, person/property search authority, seizure authority, execution records, post-action handover and interfaces with custody, evidence and legal processes. It provides a coherent, accountable operational model for the fictional Saltwater jurisdiction. It does not import real-world jurisdictional law as canon; exact fictional powers, thresholds, safeguards, approval roles and time limits remain explicit open decisions until approved.

BP-25 owns the operational decision and execution record for arrest, warrant, search and seizure actions. BP-18 owns suspect/offender role and attribution records. BP-16 owns investigative strategy and requests. BP-23 owns accepted exhibit identity, custody and continuity. BP-26 owns custody after formal handover. BP-27 owns subsequent legal process and charging/disclosure. Operational action is never conflated with a later legal decision.

## 2. Scope and exclusions

In scope: grounds and authority records; arrest consideration and decision; necessity/proportionality as configurable fictional decision factors; arrest planning; officer/task assignment; execution; use-of-force interface; person search; premises/vehicle/property search; warrant applications, issue, variation, expiry, suspension and execution; entry and safety planning; seizure decisions; property and person inventories; receipts/notifications where configured; arrest/search/seizure chronology; unsuccessful, abandoned, interrupted and disputed actions; rights/safeguards as fictional canon requires; recording, supervision, review and audit; custody handover; exhibit handover; legal interface; operational reporting.

Out of scope: suspect/offender identity and role status (BP-18); investigative hypotheses and tasks (BP-16); incident/CAD dispatch (BP-12); exhibit custody after acceptance (BP-23); custody detention, welfare, reviews and release (BP-26); charge, prosecution, disclosure and legal procedure (BP-27); court rulings (BP-28); police command/discipline (BP-30/BP-31); person identity registry (BP-03); global time (BP-37); records/persistence/security (BP-38/BP-39/BP-42).

## 3. Core distinctions

Keep separate: person of interest; suspect status; arrest grounds; arrest authority; arrest decision; arrest attempt; physical arrest/execution; search authority; warrant application; warrant issued; warrant executed; item located; item seized; exhibit accepted into BP-23 custody; person booked into BP-26 custody; charge decision; court finding. None implies another automatically.

A warrant application is not an issued warrant. An issued warrant is not proof that execution is lawful or successful. A search authority does not automatically authorise seizure of every item found. An arrest does not establish guilt, charge, conviction or admissibility. An item physically taken by an officer is not automatically an accepted exhibit. A person physically restrained is not automatically booked into custody.

## 4. Authority model and fictional legal configuration

All powers are configured as explicit, versioned fictional rules: eligible authority sources, authorised decision-makers, grounds, thresholds, scope, geographic limits, target classes, duration, conditions, approval requirements, execution roles, safeguards, reporting, review and invalidation consequences. Each rule has an ID, version, effective period, provenance, approver and supersession history.

No officer's rank, job title, clearance, unit, assignment or confidence alone grants a power. Authority is checked against the actor's appointment, role, qualification, jurisdiction, scope and the effective rule version at the action time. If the required fictional rule is unresolved or absent, the system must not invent a power; record the request as pending clarification or block execution according to the configured fail-safe.

## 5. Grounds and decision record

A grounds record identifies the person/property/action under consideration, known facts, source references, reliability/uncertainty, relevant allegations, contrary/exculpatory information, applicable authority rule/version, decision-maker, time, rationale, alternatives considered, scope, conditions and review. Separate observed facts, reported claims, intelligence, evidence, inference and unknowns.

Grounds are evaluated at the time of decision and may change as information changes. A later discovery cannot retroactively create grounds that did not exist. The record preserves the information actually available to the decision-maker, not the complete case file as reconstructed later. Do not convert a generated suspect role or hidden world truth into grounds.

## 6. Arrest consideration and decision

An arrest consideration record may end in arrest authorised, not authorised, deferred, no action, alternative action or further information required. Record the applicable rule, decision-maker, grounds, purpose, necessity/proportionality factors where configured, risks, alternatives, conditions, rationale and review. A decision not to arrest is a valid outcome and must remain visible.

An arrest decision is person- and event-specific. It does not automatically authorise a search, premises entry, seizure, detention duration or interview. Those actions require their own authority checks. The system must support multiple persons, separate decisions and changing circumstances without copying one person's grounds to another.

## 7. Arrest planning and tasking

A plan records objective, target identity resolution and uncertainty, location, time basis, authority and scope, assigned officers, supervisor, roles, equipment, transport, safety risks, vulnerable persons, third-party presence, communications, contingencies, recording requirements, medical/emergency support and custody destination/receiving capacity. Planning references BP-08 deployment, BP-09 resources, BP-12 incident, BP-15 case and BP-16 investigation records.

A plan is not an execution event. Assignments must respect actual duty status, competence, equipment, geography and time. A plan may be changed, paused, cancelled or abandoned with attributed rationale. No automatic arrest occurs because a plan exists or a target is present.

## 8. Arrest execution lifecycle

Execution records distinguish initiated, attempted, contact made, arrest declared/confirmed under configured rule, not completed, target absent, mistaken identity, interrupted, abandoned, failed, disputed and completed. Record exact event sequence, location, actors, authority/rule version, words/actions where relevant, observations, force/constraint events, injuries or medical concerns, property search, items handled, witnesses, recordings, deviations and outcome.

An arrest event must reference the person identity with confidence and preserve uncertainty. Mistaken identity must be explicitly supported, corrected and linked; it must not rewrite the original event. An arrest cannot be represented as completed merely because an officer selected an arrest option in the interface.

## 9. Person identity and mistaken identity

Resolve the target to BP-03 canonical identity using source, identifiers, confidence, conflicting identifiers and verification status. Distinguish same-name candidates, aliases, false identity, unknown person and mistaken identity. A warrant or arrest decision against one person cannot be applied to another merely because of name similarity or a generated suspect association.

If identity is uncertain, record the uncertainty and permitted action under the configured fictional rule. Corrections append a new event, preserve the original belief and record who corrected it, when, why and what downstream records require review.

## 10. Warrants: application and preparation

A warrant application identifies applicant, authority, proposed issuer, target person or premises/property, exact scope, purpose, grounds, source material, uncertainty, requested powers, proposed execution period, conditions, risks, limitations, disclosure/notification handling as configured and linked case/incident. Applications are versioned; amendments do not overwrite submitted versions.

The application must identify each requested action separately where powers differ, such as entry, search, person search, seizure, digital access or other configured scope. The system does not infer broader powers from a general request. Supporting material and sensitive-source restrictions retain provenance and access control.

## 11. Warrant decision and lifecycle

Warrant states include draft, submitted, awaiting clarification, granted/issued, refused, partially granted, varied, suspended, expired, revoked, executed, partially executed, not executed, returned and archived. Every decision records issuer, authority, effective time, expiry/conditions, scope, reasons and exact approved version. A refused or partially granted application remains preserved.

A warrant is valid only within its configured time, place, target, purpose, method, conditions and powers. Expiry, revocation or suspension blocks future execution unless an explicit configured rule states otherwise. Do not extend a warrant by silently editing its expiry. Variations create new versions and execution references the version actually relied upon.

## 12. Warrant execution

Before execution, verify the authoritative warrant version, issuer, scope, target/premises, effective period, conditions, executing personnel, required approvals and any suspension/revocation event. Record verification time and source. Execution records arrival, access/entry method where authorised, persons present, notices/actions where required by fictional configuration, search areas, items handled, interruptions, scope limits, outcomes and departure/closure.

Execution may be full, partial, unsuccessful, abandoned or interrupted. Record each authorised scope component as executed, not executed, refused, inaccessible, unsafe, unavailable or outside scope. A failed attempt remains part of the warrant history. Execution does not cure a defect in the warrant or expand its scope.

## 13. Search authority and search planning

A search record identifies subject, location/property, purpose, grounds, authority type and rule version, scope, authorised searcher(s), supervisor, limits, conditions, time, risk assessment, third-party presence, sensitive areas/material, recording and completion status. Search authority may arise from a configured warrant, consent, arrest-related power, emergency power or other fictional source; these categories are placeholders until the authority matrix is approved.

Each search action must reference the exact authority and remain within scope. Consent, where configured, records who gave it, capacity/authority, scope, conditions, time, withdrawal and effect. Consent is not presumed from silence, presence, ownership or a relationship. Search authority is not inferred from mere access to premises.

## 14. Premises, vehicle and person searches

Support separate search targets and procedures for premises, rooms/areas, vehicles, persons, containers, devices and other property as the fictional authority matrix permits. Each target has canonical identity/location, owner/occupier/keeper where known, access conditions, search scope, start/end, searchers, observations, items located, damage, restrictions and outcome.

Search coverage is recorded sufficiently to establish what was and was not searched. A room, vehicle or person not searched is not silently treated as clear. Search records distinguish an item seen, handled, tested, photographed, moved, seized, left in place or refused. Search of one person or property does not automatically authorise another.

## 15. Entry, safety and use-of-force interface

Entry and safety plans identify hazards, people at risk, children/dependants, animals, weapons or other threats as reported/observed, utilities, environmental conditions, emergency support, communication, exit routes and contingencies. Record source and confidence for each risk; an intelligence flag is not an established fact.

Use-of-force events are separately recorded with actor, time, context, authority, type/level under the fictional force model, duration, observations, injuries, medical assistance, witnesses, recordings, supervisor notification and review. BP-25 records the operational interface and links to BP-30/BP-31 oversight; it does not invent detailed force policy. No force is assumed or normalised merely because an arrest occurred.

## 16. Search results and seizure decisions

For each located item, record finder, exact location/context, time, observation, description, relation to search scope, reason for handling and decision: leave in place, photograph/document, further authority requested, seize, secure temporarily under a configured rule, or no action. Record the decision-maker, authority and rationale. Discovery alone does not make an item seizable.

Seizure authority is item-specific and tied to the applicable fictional rule, warrant scope or other authorised basis. If authority is uncertain or absent, record the item and seek clarification rather than inventing power. Items outside scope are not silently seized under a broad case association.

## 17. Seizure and property inventory

A seizure record identifies item/property, person with possession or control, owner/claimant where known, location, description, quantity, condition, serial/unique identifiers, photographs/notes, authority, reason, officer, time, witnesses, packaging state and disposition. Distinguish seized property, voluntarily provided material, found property, safeguarding hold, temporary securing and property later accepted as an exhibit.

Provide a complete inventory of items taken and items not taken where relevant. Receipts/notifications, copies, translations, acknowledgements and refusal to sign are configurable fictional procedures; record what occurred, not what should have occurred. A missing item or quantity discrepancy triggers an incident record and review.

## 18. Handover to BP-23 evidence custody

Physical collection at a scene or during a search is not BP-23 custody acceptance. BP-25 records the collecting officer, time, source location, authority, circumstances, item description, temporary possession and transfer offer. BP-23 accepts or rejects the exhibit transfer and becomes authoritative for exhibit identity, packaging, seals, storage, handlers and continuity after acceptance.

The handover contains the exact item, packaging/seal condition, source context, collection details, risk/hazard, authority and chain-of-possession events. Rejected or pending transfers remain under an explicitly assigned temporary custodian; no custody gap is concealed. BP-25 never fabricates a BP-23 exhibit ID or changes BP-23 custody state.

## 19. Person handover to BP-26 custody

Physical arrest and formal custody booking are separate events. BP-25 records arrest execution, identity, authority, time, location, officers, circumstances, property carried, injuries/medical concerns, force events, safeguards and transport. BP-26 accepts or rejects the person handover and owns booking, detention, welfare, reviews, custody clock and release.

The handover records departure, transport, arrival, receiving officer, identity verification, property reconciliation, medical information transfer, time and acceptance outcome. If custody refuses or cannot accept, the person remains in an explicit operational status with responsible authority and next action under configured rules; no fictional detention state is silently assumed. BP-25 does not run custody clocks or decide release.

## 20. Unsuccessful, interrupted and exceptional actions

Support target absent, address incorrect, identity mismatch, warrant expired/revoked, authority unclear, premises inaccessible, consent withdrawn, safety risk, third-party emergency, item outside scope, equipment failure, communications failure, officer unavailable, custody full/unavailable, medical emergency, partial execution, force incident, damaged property, lost item, contamination concern, complaint, refusal, obstruction, unexpected discovery and action abandoned.

Each exception records event time, actor, authority, facts known then, action taken, rationale, consequence, notifications, review and linked incident/case. Exceptions do not silently convert to success. A partially executed action preserves completed and uncompleted components.

## 21. Safeguards, notices and procedural status

BP-25 records applicable fictional safeguards and notices as configured: information provided, timing, recipient, language/interpreter needs, comprehension or response, accessibility needs, support person, legal assistance interface, medical referral and any reason a step was delayed, omitted or unavailable. Exact rights, wording, timing, exceptions and authority are open canon decisions, not assumed real-world legal advice.

A safeguard record distinguishes required, provided, declined, unavailable, delayed, not applicable and disputed. The system does not auto-mark a safeguard complete. Corrections preserve the original record and explain who amended it.

## 22. Supervision, review and accountability

Review triggers may include high-risk action, force, injury, disputed identity, warrant variation, scope deviation, seizure dispute, failed handover, complaint, missing property, authority concern or other configured condition. Review identifies reviewer, independence, authority, materials examined, findings, actions, limitations and unresolved issues. Review can find no issue, procedural issue, policy breach, unresolved concern or refer to BP-30/BP-31/BP-40.

A review does not rewrite original events. Operational supervisors may approve actions only within explicit authority. Rank does not cure a missing legal power. Decisions, overrides, refusals and notifications remain attributable and auditable.

## 23. Case, incident and suspect interfaces

Every action links to relevant BP-12 incident and BP-15 case where available, while allowing a lawful/fictional action before a case exists with a later linked record. BP-16 may request or plan action but does not execute it automatically. BP-18 receives suspect procedural-status references; an arrest does not automatically change suspect/offender classification or create a proven-offender status.

Multiple cases, persons and incidents can be linked without merging their histories. A case link does not create authority. A suspect status does not create grounds. A warrant may relate to multiple authorised targets only where its exact scope says so.

## 24. Disclosure, legal challenge and court interface

BP-25 preserves original applications, warrants, grounds, execution records, search logs, seizure inventories, receipts, handover records, recordings, notices, deviations and review history for authorised BP-27/BP-28 workflows. Record the exact versions disclosed, recipient, authority, time, redactions and restrictions.

Challenges to grounds, identity, warrant validity, execution, search scope, seizure, force, notices or property handling are recorded with challenger, issue, supporting material, response and outcome status. BP-25 supplies factual operational records but does not decide admissibility, charge, prosecution, legal remedy, guilt or court findings. BP-27/BP-28 own those determinations.

## 25. Permissions and protected information

BP-42 owns global access policy. BP-25 defines scoped permissions for arrest grounds, warrant applications and supporting sources, protected identities, informants, medical details, search plans, operational locations, tactical information, recordings, property inventories and court copies. Least privilege applies. Rank, case assignment or operational interest alone does not authorise every read/export.

Access, denied access, amendment, disclosure, print/export and sensitive search are audited. Redacted views preserve links to authoritative originals and record the reason, actor and authority. Player-facing views cannot expose protected source identities or hidden generator truth.

## 26. NPC knowledge and hidden-truth protection

An officer or NPC knows only what they observed, were told, received or lawfully accessed. An arrest plan, warrant, case association or hidden world record does not make every officer omniscient. Actors may misunderstand, misidentify, omit or misreport facts; the record preserves source and uncertainty.

No arrest, warrant, search, seizure, inventory, receipt, report, NPC dialogue, notification, AI summary, error message or test fixture may leak hidden offender/accomplice identity. The only reveal condition remains the player typing exactly bingo. Do not provide unsolicited solution hints or tell the player what to investigate next.

## 27. Player agency and decision integrity

The player controls their own officer's decisions and actions within the game interface. The system presents available records, authority, options and outcomes without choosing an arrest, search, seizure, warrant application or target on the player's behalf. NPC actions are simulated only when supported by their own role, knowledge, authority, capability and an explicit in-world event.

No auto-arrest, auto-search, auto-seizure or automatic warrant execution occurs because a case needs progression. Outcomes may be unsuccessful, delayed, challenged, incomplete or refused. The game must not railroad a player into an arrest or use a hidden culprit flag as operational grounds.

## 28. Time, scheduling and pause

BP-37 is the sole simulation clock. Arrest plans, warrant validity, expiry, execution windows, search durations, officer travel, custody handover, notifications, review deadlines and scheduled actions are time-dependent and use one canonical time basis. No clock advances when the player exits or pauses. No warrant expires, detention period elapses, officer travels, search continues, custody handover occurs or deadline passes off-screen.

On resume, no catch-up execution or expiry occurs. Time advances only through explicit player-controlled in-game progression, with all consequential transitions recorded. Warrant validity is evaluated against the canonical simulation time, not wall-clock time.

## 29. Population and person continuity

Every person is one canonical BP-03 person, counted once in Saltwater's 10,000 living-person hard cap. Arrest, detention, custody, release, death, departure or a role change does not create a duplicate person. Anyone materially connected to a police action or case is promoted to full persistent person simulation and never downgraded. Promotion cannot bypass the cap or create a second identity.

A person can hold multiple case roles over time or across cases. Arrest in one case does not erase victim/witness status in another. Status corrections preserve prior states and reasons.

## 30. Records, identifiers and event integrity

Use stable IDs for arrest considerations, arrest events, warrant applications, warrant versions, search authorities, search actions, execution records, seizure events, inventory lines, handovers, reviews and challenges. BP-38 owns schemas, constraints and identifiers; BP-39 owns persistence/recovery. Each material event records actor, authority, canonical time, source, reason, exact rule/version, prior/new state, outcome and related record IDs.

Events are append-only for material history. Corrections add a linked correction/supersession record; they do not erase the original. Idempotency prevents duplicate execution or handover from retries. Partial failure and replay must not duplicate arrests, warrants, seizures or person/property records.

## 31. Inputs, outputs and event contracts

Inputs: BP-03 person identity; BP-05 police authority; BP-06 personnel; BP-08 deployment; BP-09 resources; BP-12 incidents/dispatch; BP-15 cases; BP-16 investigative requests; BP-18 suspect roles; BP-22 scene context; BP-23 exhibit custody; BP-26 custody capacity/acceptance; BP-27 legal requests; BP-28 court directions; BP-30 command; BP-31 standards; BP-37 time; BP-38 records; BP-39 persistence; BP-42 permissions.

Outputs: grounds and arrest consideration records; arrest decisions and execution events; warrant applications, issued versions and execution records; search authority and search logs; seizure decisions and property inventories; force/safeguard/review events; custody and evidence handover offers; incident/case links; disclosure-ready operational records; audit events.

Events include arrest_considered/authorised/declined/deferred; arrest_planned/assigned/attempted/executed/abandoned/disputed; warrant_drafted/submitted/clarified/issued/refused/varied/suspended/revoked/expired/executed/partially_executed/returned; search_authorised/started/paused/completed/abandoned; item_located/recorded/seizure_authorised/seized/not_seized; force_event_recorded; safeguard_recorded; property_handover_offered/accepted/rejected; custody_handover_offered/accepted/rejected; review_opened/completed; challenge_received/responded. Every event includes stable ID, actor, authority, purpose, canonical time, source, exact scope/rule version, outcome, idempotency key and schema version.

## 32. Failure modes and edge cases

Wrong or uncertain identity; duplicate identity; no grounds; conflicting grounds; stale intelligence; exculpatory information omitted; unauthorised actor; rank/power confusion; warrant refused/partial/expired/revoked/suspended; warrant version mismatch; target outside scope; address ambiguity; third-party property; consent ambiguity/withdrawal; entry blocked; unsafe premises; vulnerable person present; item outside scope; digital device inaccessible; seizure quantity mismatch; property damage; force incident; injury/medical emergency; language/accessibility need; custody unavailable; evidence handover rejected; custody handover rejected; officer assignment conflict; duplicate event submission; network interruption; time paused; wall-clock expiry attempt; post-event identity correction; report challenged; source protection restriction; hidden-truth leakage attempt. Preserve original state, uncertainty and event history; block invalid transition; never fabricate authority or success.

## 33. Dependencies and ownership boundaries

BP-03 owns person identity/population; BP-05 owns institutional mandate and authority architecture; BP-06 owns personnel; BP-08 deployment; BP-09 assets; BP-12 incident/CAD; BP-15 case lifecycle; BP-16 investigation; BP-18 suspect/offender roles; BP-22 scenes; BP-23 exhibit custody; BP-26 custody; BP-27 legal processes; BP-28 courts; BP-30 command; BP-31 professional standards; BP-37 time; BP-38 records; BP-39 persistence; BP-42 security. BP-25 owns arrest, warrant, search and seizure operational decisions and execution. It references and hands off; it never silently mutates another division's authoritative records.

## 26. Acceptance tests

These are specification acceptance criteria, not executed results. BP-43 owns test execution and reproducible evidence.

- **ARREST-AT-001** — Every arrest consideration has a stable unique ID.
- **ARREST-AT-002** — Every arrest execution has a stable unique ID.
- **ARREST-AT-003** — Every warrant application has a stable unique ID.
- **ARREST-AT-004** — Every warrant issue/variation has an immutable version ID.
- **ARREST-AT-005** — Every search action has a stable unique ID.
- **ARREST-AT-006** — Every seizure event and inventory line has stable unique IDs.
- **ARREST-AT-007** — An arrest decision identifies the person and identity confidence.
- **ARREST-AT-008** — A grounds record identifies the information available at decision time.
- **ARREST-AT-009** — Reported claims remain distinct from observed facts.
- **ARREST-AT-010** — Intelligence remains distinct from evidence and established fact.
- **ARREST-AT-011** — Exculpatory or contrary information can be recorded alongside supporting information.
- **ARREST-AT-012** — A later discovery cannot retroactively create earlier grounds.
- **ARREST-AT-013** — A generated suspect role alone cannot create arrest grounds.
- **ARREST-AT-014** — Hidden generator truth cannot be used as an officer's grounds.
- **ARREST-AT-015** — Authority is checked against actor role and effective rule version.
- **ARREST-AT-016** — Rank alone does not grant arrest, search, entry or seizure power.
- **ARREST-AT-017** — Unit assignment alone does not grant authority.
- **ARREST-AT-018** — An actor outside jurisdiction cannot exercise undefined powers.
- **ARREST-AT-019** — An unresolved authority rule does not get silently invented.
- **ARREST-AT-020** — A missing authority basis blocks or defers action according to fail-safe configuration.
- **ARREST-AT-021** — Arrest consideration supports authorised, declined, deferred and no-action outcomes.
- **ARREST-AT-022** — A decision not to arrest remains preserved.
- **ARREST-AT-023** — Arrest authority does not automatically authorise search.
- **ARREST-AT-024** — Arrest authority does not automatically authorise premises entry.
- **ARREST-AT-025** — Arrest authority does not automatically authorise seizure.
- **ARREST-AT-026** — Each person has an individual arrest decision record.
- **ARREST-AT-027** — One person's grounds are not copied to another person.
- **ARREST-AT-028** — Arrest alternatives and rationale are recorded where configured.
- **ARREST-AT-029** — An arrest plan is distinct from an arrest execution.
- **ARREST-AT-030** — An arrest plan identifies target, location, time basis and authority.
- **ARREST-AT-031** — A plan identifies assigned officers and their valid duty status.
- **ARREST-AT-032** — A plan checks relevant competence and equipment.
- **ARREST-AT-033** — A plan identifies supervisory responsibility.
- **ARREST-AT-034** — A plan records relevant safety and third-party risks.
- **ARREST-AT-035** — A plan may be amended with version history.
- **ARREST-AT-036** — A plan may be cancelled without creating an arrest event.
- **ARREST-AT-037** — No arrest occurs solely because a plan exists.
- **ARREST-AT-038** — Arrest execution records actual event chronology.
- **ARREST-AT-039** — Arrest execution supports unsuccessful and interrupted outcomes.
- **ARREST-AT-040** — Target absent is not recorded as successful arrest.
- **ARREST-AT-041** — Mistaken identity is explicitly representable.
- **ARREST-AT-042** — Identity confidence and conflicting identifiers are preserved.
- **ARREST-AT-043** — An arrest event does not automatically establish guilt.
- **ARREST-AT-044** — An arrest event does not automatically establish offender status.
- **ARREST-AT-045** — An arrest event does not automatically create a charge.
- **ARREST-AT-046** — An arrest event does not automatically book the person into custody.
- **ARREST-AT-047** — An arrest event records actual actors and location.
- **ARREST-AT-048** — An arrest event records the authority version relied upon.
- **ARREST-AT-049** — An arrest event records deviations and reasons.
- **ARREST-AT-050** — A correction to identity preserves the original mistaken belief.
- **ARREST-AT-051** — A warrant application identifies applicant and authority.
- **ARREST-AT-052** — A warrant application identifies exact target and location/property.
- **ARREST-AT-053** — A warrant application records purpose and grounds.
- **ARREST-AT-054** — A warrant application records source material and uncertainty.
- **ARREST-AT-055** — Each requested power has an explicit scope.
- **ARREST-AT-056** — A broad application does not silently imply unrequested powers.
- **ARREST-AT-057** — Submitted application versions remain immutable.
- **ARREST-AT-058** — A warrant application can be clarified without losing the original.
- **ARREST-AT-059** — A warrant may be refused or partially granted.
- **ARREST-AT-060** — A refusal preserves issuer, reason and submitted version.
- **ARREST-AT-061** — A granted warrant identifies issuer and authority.
- **ARREST-AT-062** — A warrant identifies effective time and expiry/conditions.
- **ARREST-AT-063** — A warrant identifies exact location, target, purpose and scope.
- **ARREST-AT-064** — A warrant variation creates a new version.
- **ARREST-AT-065** — A warrant suspension blocks execution as configured.
- **ARREST-AT-066** — A revoked warrant cannot be silently used.
- **ARREST-AT-067** — An expired warrant cannot be silently used.
- **ARREST-AT-068** — A warrant cannot be extended by editing the original expiry.
- **ARREST-AT-069** — Execution references the exact warrant version relied upon.
- **ARREST-AT-070** — Execution checks scope, target, time and conditions.
- **ARREST-AT-071** — Warrant verification records who checked and when.
- **ARREST-AT-072** — Warrant execution supports full and partial outcomes.
- **ARREST-AT-073** — Warrant execution supports unsuccessful and abandoned outcomes.
- **ARREST-AT-074** — Each scope component has its own execution status.
- **ARREST-AT-075** — A warrant does not expand beyond its approved scope.
- **ARREST-AT-076** — A warrant does not prove guilt or evidential relevance.
- **ARREST-AT-077** — A search record identifies target and location/property.
- **ARREST-AT-078** — A search record identifies authority type and rule version.
- **ARREST-AT-079** — A search record identifies scope, limits and conditions.
- **ARREST-AT-080** — A search record identifies authorised searchers.
- **ARREST-AT-081** — Search authority is not inferred from mere access or ownership.
- **ARREST-AT-082** — Consent is not inferred from silence or presence.
- **ARREST-AT-083** — Consent records the person, authority, scope and conditions where configured.
- **ARREST-AT-084** — Consent withdrawal and its effect are recordable.
- **ARREST-AT-085** — Search of one person does not authorise search of another.
- **ARREST-AT-086** — Search of one property does not authorise search of another.
- **ARREST-AT-087** — Premises searches identify areas searched and not searched.
- **ARREST-AT-088** — Vehicle searches identify the specific vehicle and scope.
- **ARREST-AT-089** — Person searches identify the specific person and scope.
- **ARREST-AT-090** — Search records distinguish seen, handled, photographed, moved and seized items.
- **ARREST-AT-091** — An unsearched area is not silently marked clear.
- **ARREST-AT-092** — Entry method is checked against the authority scope.
- **ARREST-AT-093** — Safety planning records source and confidence of hazards.
- **ARREST-AT-094** — Third-party presence is recordable.
- **ARREST-AT-095** — Vulnerable persons and emergency needs are recordable.
- **ARREST-AT-096** — Force events are separately attributable and reviewable.
- **ARREST-AT-097** — An arrest does not imply force was used.
- **ARREST-AT-098** — Injury and medical assistance events are recordable.
- **ARREST-AT-099** — A force event does not rewrite arrest grounds or authority.
- **ARREST-AT-100** — A located item is not automatically seizable.
- **ARREST-AT-101** — Each seizure decision identifies item and legal/fictional authority.
- **ARREST-AT-102** — Seizure authority is item-specific.
- **ARREST-AT-103** — Items outside warrant/search scope are not silently seized.
- **ARREST-AT-104** — A decision to leave an item in place is recordable.
- **ARREST-AT-105** — A request for further authority is recordable.
- **ARREST-AT-106** — Seizure records item condition and quantity where known.
- **ARREST-AT-107** — Unknown quantity remains explicitly unknown.
- **ARREST-AT-108** — Property owner/possessor/claimant are separate roles.
- **ARREST-AT-109** — Seized property is distinct from voluntarily provided material.
- **ARREST-AT-110** — Temporary securing is distinct from formal seizure.
- **ARREST-AT-111** — Found property is distinct from evidential exhibit.
- **ARREST-AT-112** — Property inventory supports refusal to acknowledge receipt.
- **ARREST-AT-113** — Property discrepancies trigger an attributable review.
- **ARREST-AT-114** — Physical possession by officer is not BP-23 custody acceptance.
- **ARREST-AT-115** — BP-25 records temporary custodian before BP-23 acceptance.
- **ARREST-AT-116** — BP-23 may accept or reject an exhibit transfer.
- **ARREST-AT-117** — A rejected exhibit handover retains an explicit custodian.
- **ARREST-AT-118** — BP-25 cannot fabricate BP-23 exhibit IDs or custody events.
- **ARREST-AT-119** — Evidence handover records package/seal condition.
- **ARREST-AT-120** — Evidence handover records recovery/collection context.
- **ARREST-AT-121** — Arrest is distinct from formal BP-26 custody booking.
- **ARREST-AT-122** — BP-26 owns custody booking and detention lifecycle.
- **ARREST-AT-123** — A custody handover records receiving officer and acceptance outcome.
- **ARREST-AT-124** — A rejected custody handover leaves explicit responsibility/status.
- **ARREST-AT-125** — BP-25 does not run custody clocks or decide release.
- **ARREST-AT-126** — Custody property reconciliation is recorded at handover.
- **ARREST-AT-127** — Medical/safeguard information is transferred only with authorised scope.
- **ARREST-AT-128** — Failed or interrupted actions remain in history.
- **ARREST-AT-129** — A warrant defect is not cured by successful physical execution.
- **ARREST-AT-130** — A search scope deviation is recorded, not concealed.
- **ARREST-AT-131** — An action can be abandoned for safety with rationale.
- **ARREST-AT-132** — A target address mismatch is explicitly recorded.
- **ARREST-AT-133** — A custody capacity failure does not create a false booking.
- **ARREST-AT-134** — An unavailable officer cannot be recorded as executing an action.
- **ARREST-AT-135** — A duplicate command/event does not create duplicate arrest or seizure.
- **ARREST-AT-136** — Partial failure preserves completed and uncompleted components.
- **ARREST-AT-137** — Safeguard records distinguish required, provided, declined, delayed and unavailable.
- **ARREST-AT-138** — The system does not auto-mark notices or safeguards complete.
- **ARREST-AT-139** — Fictional rights/notice wording remains configurable pending canon.
- **ARREST-AT-140** — Review identifies reviewer, scope and outcome.
- **ARREST-AT-141** — Review does not overwrite original events.
- **ARREST-AT-142** — Rank does not cure missing authority.
- **ARREST-AT-143** — Command approval is limited to explicit authority.
- **ARREST-AT-144** — Complaints and challenges retain challenger and grounds.
- **ARREST-AT-145** — Case/incident links do not create authority.
- **ARREST-AT-146** — A person may retain victim/witness status in another case.
- **ARREST-AT-147** — Arrest does not automatically change BP-18 suspect/offender status.
- **ARREST-AT-148** — Multiple cases retain separate action histories.
- **ARREST-AT-149** — Disclosure records identify exact versions supplied.
- **ARREST-AT-150** — Redacted copies link to authoritative originals.
- **ARREST-AT-151** — BP-25 does not decide admissibility or evidential weight.
- **ARREST-AT-152** — BP-25 does not decide charge or prosecution.
- **ARREST-AT-153** — Court findings remain BP-28-owned.
- **ARREST-AT-154** — Sensitive grounds and sources enforce BP-42 permissions.
- **ARREST-AT-155** — Rank/case assignment alone does not grant unrestricted access.
- **ARREST-AT-156** — Denied reads and sensitive exports are audited.
- **ARREST-AT-157** — Protected source identity is not exposed in player views.
- **ARREST-AT-158** — NPC knowledge reflects actual observation, receipt and access.
- **ARREST-AT-159** — An arrest plan does not make all assigned officers omniscient.
- **ARREST-AT-160** — No warrant, report or notification leaks hidden culprit identity.
- **ARREST-AT-161** — Only exact player input bingo permits hidden-truth reveal.
- **ARREST-AT-162** — No unsolicited investigation hint is generated.
- **ARREST-AT-163** — The player is not forced into an arrest or search.
- **ARREST-AT-164** — The system does not auto-arrest to advance a case.
- **ARREST-AT-165** — The system does not auto-seize an item because it is relevant.
- **ARREST-AT-166** — NPC actions require their own authority and capability.
- **ARREST-AT-167** — BP-37 is the sole simulation clock.
- **ARREST-AT-168** — No warrant expires while the player is outside the simulation.
- **ARREST-AT-169** — No officer travels or executes actions off-screen.
- **ARREST-AT-170** — No search or handover progresses while paused.
- **ARREST-AT-171** — Resume does not apply wall-clock catch-up.
- **ARREST-AT-172** — All timestamps use canonical simulation time.
- **ARREST-AT-173** — All event transitions have actor, authority, time and reason.
- **ARREST-AT-174** — Corrections append and preserve original events.
- **ARREST-AT-175** — Retries do not duplicate material events.
- **ARREST-AT-176** — Replay preserves one arrest, warrant and seizure outcome.
- **ARREST-AT-177** — Every action links to exact rule/version and scope.
- **ARREST-AT-178** — Every person resolves to one canonical BP-03 identity.
- **ARREST-AT-179** — Arrest does not create duplicate person records.
- **ARREST-AT-180** — Police personnel are counted within the 10,000 living-person cap.
- **ARREST-AT-181** — Case-connected persons are permanently promoted to full simulation.
- **ARREST-AT-182** — Promotion never downgrades and never bypasses population cap.
- **ARREST-AT-183** — Text-only interface supports every essential BP-25 workflow.
- **ARREST-AT-184** — Optional visual plans/maps derive from canonical records.
- **ARREST-AT-185** — Visuals do not replace authoritative text or action logs.
- **ARREST-AT-186** — No Neon write is authorised by this specification.
- **ARREST-AT-187** — Every material action is traceable to source requirement and test evidence.

## 27. Source traceability

The original 52-division source JSON remains unchanged. IDs below refer to original source-array positions (1-based). BP-25 receives only its explicit mapped source requirements/tests; cross-cutting rules apply in addition.

| Source ID | Original requirement/test | BP-25 coverage |
|---|---|---|
| S37.R01 | Represent grounds, authority, applications, approvals, execution, person/property searches, seizure, transport, booking, detention, welfare, reviews and release. | Sections 4–22 and 26; BP-25 owns grounds, authority, applications, execution, search and seizure. BP-26 owns custody, welfare, reviews and release. |
| S37.R02 | Maintain custody clock and property continuity. | Sections 16–17, 23 and 25; BP-25 handover references BP-26 custody clock and BP-23 property continuity; it does not take ownership of either. |
| S37.R03 | Separate operational action from later legal decision. | Sections 3, 21–22 and 30; operational arrest/search/seizure records remain separate from BP-27/BP-28 legal outcomes. |
| S37.T01 | Custody and warrant events satisfy configured fictional rules and chronological constraints. | ARREST-AT-060–076, 153–157; warrant version/scope/time checks, custody handover, configured authority and canonical clock. |

Cross-cutting X03 applies: every time-dependent fact is effective-dated and historically queryable; BP-37 remains the sole clock and pause freezes all time-dependent action. X05 preserves fact/allegation/estimate/inference/intelligence/opinion/conclusion/finding distinctions. X08 requires text-first gameplay and optional visuals derived from canonical records. Global constraints include one-city Saltwater, 10,000 living-person cap, permanent promotion of case-connected people, player agency and exact bingo reveal firewall.

## 28. Open decisions and risk register

### Open fictional decisions
1. Complete authority/powers matrix and source hierarchy.
2. Arrest grounds threshold and decision-maker roles.
3. Necessity/proportionality factors and permitted alternatives.
4. Warrant categories, issuer roles, application evidence and approval process.
5. Warrant duration, expiry, variation, suspension and revocation rules.
6. Search authority categories and scope for persons, premises, vehicles, containers and devices.
7. Consent validity, scope, withdrawal and recording rules.
8. Entry methods, notices and safeguards.
9. Seizure categories, exceptions, receipts and property return.
10. Force model, reporting thresholds, supervision and review.
11. Vulnerability, medical assistance and support safeguards.
12. Failed/rejected custody handover fallback.
13. Failed/rejected evidence handover fallback.
14. Recording and retention rules for arrest/search activity.
15. Operational review and escalation matrix.

### Risk register

| Risk | Mitigation |
|---|---|
| Rank confused with legal power | Effective-dated authority matrix and actor checks |
| Arrest treated as guilt | Explicit status separation and BP-18/BP-28 boundaries |
| Warrant application treated as issued | Immutable lifecycle and exact-version verification |
| Search exceeds scope | Target/action-level authority checks |
| Seizure without authority | Item-specific decision and provenance |
| Exhibit custody gap | Explicit temporary custodian and BP-23 acceptance |
| Arrest mistaken for booking | Explicit BP-26 handover and acceptance |
| Hidden truth leaks through action | NPC knowledge firewall and exact bingo tests |
| Time passes while absent | BP-37 hard pause invariant |
| Duplicate events on retry | Idempotency and append-only event history |
| Population double-counting | One BP-03 person identity and 10k cap |

## 29. Design completion checklist

- [ ] Fictional authority model and unresolved powers explicitly represented.
- [ ] Grounds, decisions and alternatives specified.
- [ ] Arrest planning and execution lifecycle specified.
- [ ] Identity resolution and mistaken identity specified.
- [ ] Warrant application, issue, variation and execution specified.
- [ ] Search authority, scope and target-specific search records specified.
- [ ] Entry, safety and force interfaces specified.
- [ ] Item-specific seizure decisions and property inventory specified.
- [ ] BP-23 evidence handover and temporary custody specified.
- [ ] BP-26 person/custody handover specified.
- [ ] Safeguards, supervision, challenge and review specified.
- [ ] BP-27/BP-28 legal boundaries specified.
- [ ] NPC knowledge, player agency and bingo firewall specified.
- [ ] Time freeze, population cap and permanent person promotion specified.
- [ ] Text-first workflow and optional visual support specified.
- [ ] All 160 acceptance tests await BP-43 execution.
- [ ] Open decisions remain explicit; no real-world law silently imported.
- [ ] No Neon schema, seed, import or bulk write has been made or authorised.

## 30. Status and next dependencies

This is a complete division design draft, not approved policy or implementation evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-26 — Custody Management**. BP-26 owns booking, detention, custody clock, welfare, property reconciliation while in custody, reviews, visits, transfer and release. BP-25 remains the owner of arrest, warrant, search and seizure operational authority and execution.
