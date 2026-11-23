# BP-37 — Time and Scheduling

**Project:** Saltwater  
**Division:** BP-37 of the fixed 44-division master structure  
**Version:** 1.0  
**Specification status:** DESIGNED_DRAFT — review/approval pending  
**Implementation / test execution / verification:** NOT_STARTED  
**Authority:** Saltwater master blueprint, original 52-division source and authoritative 52→44 crosswalk.  
**Database status:** This specification authorises no Neon schema, migration, seed, import or other database write.

## 1. Purpose

BP-37 defines the single authoritative in-world clock, calendar, temporal model, schedule catalogue, recurrence rules, due-event eligibility and temporal query semantics. It provides one consistent basis for dates, times, intervals, deadlines, shifts, opening hours, appointments, hearings, custody reviews, travel plans, maintenance, deliveries, public events and historical chronology.

Time is part of the fictional simulation, not a reflection of the user's device clock. When the player leaves, closes the game or otherwise pauses the simulation, all simulation time and all time-dependent world activity freeze. On return, the world resumes from the exact committed point. There is no offline catch-up.

BP-37 owns canonical time and scheduling services. It does not own the meaning, authority or business logic of the actions scheduled. Domain owners define and validate their own actions; BP-35 coordinates runtime execution.

## 2. Scope and exclusions

Included:
- Canonical simulation clock and monotonic advancement.
- Fictional calendar, timezone and civil-time rules.
- Timestamp, interval, precision and uncertainty semantics.
- Pause/resume temporal invariants and committed time watermarks.
- One-off, recurring and exception schedules.
- Due queues, ordering, priorities, dependencies, expiry and retry metadata.
- Scheduling interfaces for people, businesses, police, courts, custody, services and infrastructure.
- Temporal history, effective time, recorded time and correction lineage.
- Replay, recovery, audit, access controls and operational observability.

Excluded:
- Domain-specific authority or policy for employment, police rosters, opening hours, court listings, custody, sentence calculation, healthcare or dispatch.
- Event-processing engine ownership and general NPC decision-making.
- Person, business, asset, case or location identity.
- Real-world wall-clock timers that progress the fictional world while paused.
- Unbounded continuous simulation of every person or business.

## 3. Binding Saltwater canon

1. One sovereign city-state, one playable city and one bounded jurisdiction.
2. Living population hard cap: 10,000 total, counted once across all roles. BP-03 owns the canonical ledger.
3. At least 10,000 businesses; BP-04 owns business identity and status.
4. Police is the deepest simulation; other domains are proportionate.
5. Text-first interface is complete without optional graphics.
6. No world-time advancement while the player is outside the simulation.
7. No offline catch-up, hidden deadlines, NPC actions, queue execution, sentence progression or environmental progression.
8. A materially case-relevant person is permanently promoted to full persistent detail; never downgrade or erase them.
9. Hidden offender/accomplice truth remains protected until the player types exactly bingo. No time or schedule feature may expose it or suggest investigative next steps.
10. Compress storage representation, never meaning, provenance, chronology or audit.
11. Neon writes require separate explicit user approval after storage baseline, incremental estimate and projected total are reported.

## 4. Ownership and authority

| Division | Authoritative responsibility | BP-37 contract |
|---|---|---|
| BP-01 | Canon, player agency and global rules | Enforce no-offline-progression invariants |
| BP-03 | Person identity, lifecycle and population | Reference canonical person IDs; never duplicate identities |
| BP-04 | Businesses, organisations, property and opening-hour policy | Provide schedules and canonical business references |
| BP-07 | Career and service-credit policy | Consume canonical time |
| BP-08 | Police rosters, shifts, deployment and availability | Own police duty schedules and assignment |
| BP-11/BP-12 | Emergency communications and incidents | Own dispatch and incident chronology |
| BP-14 | Hidden occurrence truth and generation | Never disclose hidden truth through time data |
| BP-26 | Custody authority and custody clock policy | Own custody-specific rules |
| BP-27/BP-28 | Legal process and court adjudication | Own legal deadlines, listings and hearings |
| BP-29 | Sentence and correctional execution | Own sentence calculation and execution |
| BP-33 | Employment, contracts, attendance and leave | Own employment schedules and attendance policy |
| BP-35 | Simulation runtime and event execution | Coordinate pause/resume and invoke owner handlers |
| BP-36 | Relationships and social context | Supply social schedules and relationship history |
| BP-37 | Canonical clock, calendar and scheduling | Own shared temporal services and schedule semantics |
| BP-38/BP-39 | Records and persistence | Validate contracts; persist and recover time state |
| BP-42/BP-43/BP-44 | Security, QA and configuration | Enforce access, tests and controlled configuration |

A schedule is not authority to perform an action. BP-37 may make an occurrence eligible, but only the owning domain may validate and commit the action.

## 5. Temporal model

The canonical clock has one authoritative simulation instant and a monotonically increasing committed advancement sequence. Its snapshot includes canonical instant, configured fictional timezone and offset, local civil date/time, calendar identity/version, runtime pause state, committed advancement watermark, precision and ordering metadata.

The system distinguishes:
- **Occurred time:** when the event happened in-world.
- **Effective time:** when a fact or state is considered effective.
- **Observed time:** when an actor or system observed it.
- **Recorded time:** when the simulation recorded it.
- **Committed time:** when the durable transaction committed.
- **Source time:** time supplied by an external or documentary source.

These values are not interchangeable. A record entered later does not mean the underlying event happened later. A source timestamp is not trusted without provenance and timezone/precision context.

## 6. Calendar and timezone

The fictional calendar and timezone are versioned configuration. The implementation must define date arithmetic, month lengths, leap rules, weekdays, seasons if used, civil-time transitions if configured, and local-time ambiguity handling. No host device timezone or wall clock may silently define the game calendar.

Historical timestamps retain the calendar/timezone interpretation under which they were recorded. A configuration change affects future interpretation only unless a separately authorised correction is recorded. Date-only, approximate and uncertain times remain so; the system must not invent seconds or exact instants.

## 7. Clock lifecycle and advancement

Clock states are coordinated with BP-35 runtime states: paused, active, advancing, recovering and safe-halted. Only an explicit authorised active-time advancement can move the clock. Every advancement is validated, bounded, sequenced, attributable and committed atomically with its watermark.

Time cannot move backwards through ordinary play. Corrections are separate records preserving the prior value, reason, authority and lineage. Concurrent advancement attempts must serialize or reject; they must never double-advance. Failed advancement leaves the last committed state intact.

## 8. Pause and resume

Pause freezes the canonical clock and all simulation-owned activity. This includes NPC plans, travel, conversations, shifts, dispatch, investigations, business operations, deliveries, appointments, hearings, custody reviews, legal deadlines, sentence progression, weather, daylight, tides, maintenance and social events.

Real-world elapsed time while paused is irrelevant. On resume, the simulation continues from the last committed watermark. It does not calculate elapsed offline time, replay missed wall-clock intervals, trigger overdue activity or manufacture NPC actions. Events become eligible only as the resumed simulation clock advances to their due times.

External messages arriving while paused follow an explicit ingress policy. They may be retained as external inputs for later authorised processing, but cannot silently mutate world state or advance time.

## 9. Schedule catalogue and record contract

A schedule record minimally identifies:
- Stable schedule ID and owner domain.
- Schedule type and lifecycle status.
- Canonical subject/resource references.
- Start, end, due or recurrence definition.
- Timezone/calendar version and precision.
- Recurrence and exception rules where applicable.
- Dependencies and priority class.
- Creation/modification actor, reason and authority.
- Version, provenance and audit lineage.
- Execution policy, expiry policy and idempotency key.

Schedule types include appointments, attendance, employment shifts, police duties, business opening hours, court hearings, custody reviews, legal deadlines, sentence milestones, maintenance, deliveries, healthcare, public events, travel plans, recurring routines and social gatherings. This catalogue does not transfer domain ownership to BP-37.

## 10. Recurrence, exceptions and versions

One-off schedules and recurrence definitions are distinct. Recurrence rules generate bounded occurrences within an active horizon; they must not materialise unlimited future rows. Calendar arithmetic is deterministic and handles month ends, leap days and configured civil-time transitions.

Exceptions may skip, move or replace an occurrence only within defined scope. Schedule edits create new versions and preserve the prior definition. Completed historical occurrences are never rewritten by a future schedule edit. Cancellation, suspension, rescheduling and reinstatement are explicit auditable transitions.

## 11. Due queue and event ordering

An occurrence becomes eligible only when canonical simulation time reaches its due instant and all prerequisites are satisfied. Ordering uses due instant, owner-defined priority class, causal dependency and stable sequence/tie-break rules. Priority cannot bypass causal prerequisites or domain authority.

The queue is a derived operational projection, not the authoritative schedule record. It can be rebuilt from versioned schedule definitions and committed event history. Queue rebuilding must not reorder dependent work or duplicate already committed actions.

## 12. Execution contract

BP-37 supplies an eligible occurrence to BP-35. BP-35 invokes the owning domain's validated handler. The owner rechecks current state, authority, resource availability, permissions and prerequisites before committing. An idempotency key prevents duplicate action if a worker retries.

Execution results distinguish committed, rejected, deferred, expired and failed. Each result retains schedule ID, occurrence ID, owner, attempt, source event, reason and retry policy. The scheduler cannot compensate for a domain action by directly mutating domain state. Compensation belongs to the owner.

## 13. Deadlines and overdue work

A deadline is a domain-owned obligation with a BP-37 due-time reference. It does not elapse while paused. Extensions, suspensions, completion, cancellation, expiry and breach are explicit owner-authorised transitions. BP-37 provides temporal comparison and ordering but does not decide legal consequences, custody authority, employment discipline or case outcomes.

No missed or overdue event is silently executed as though it occurred during a paused interval. Overdue status derives only from active simulation time and the owning domain's policy.

## 14. Person, business and resource availability

Schedules reference canonical entities. They do not duplicate identities or prove attendance. Person availability is computed from authoritative domain records, including employment, leave, custody, training, deployment, health or other applicable state. Conflicting claims are surfaced to the relevant owner.

BP-37 does not own police rosters, employment shifts, business opening-hour policy, property occupancy, custody status, court listing or resource inventory. It must not infer that a person is physically present merely because an appointment exists. Actual attendance, travel and access require their own authoritative events.

## 15. Historical chronology and uncertainty

Temporal records preserve occurrence, observation, recording, effective and commit times where relevant. External device clocks may drift; their source time, measured offset and uncertainty are retained. Unknown timezone, date-only evidence and approximate time ranges remain unresolved or approximate.

Intervals use consistent boundary semantics. Open-ended intervals remain open. Invalid ranges are rejected or retained as explicitly flagged source errors. Historical reconstruction uses schedule versions and event records valid at the requested time.

## 16. NPC and world activity

NPCs may have schedules and routines, but BP-37 does not grant omniscient knowledge or decide their choices. NPCs know only what they observed, were told or lawfully accessed. Scheduled attendance is not proof of actual attendance. Social, employment and family schedules may inform availability but cannot deterministically dictate crime, guilt or testimony.

All NPC and ambient activity freezes with the simulation. Relevance-based activation and scheduled wake-ups avoid polling all 10,000 people continuously. Case-relevant facts and persons are never aggregated away.

## 17. Privacy and permissions

Sensitive schedules may reveal a person's location, health, relationships, safeguarding status, witness protection, informant handling or police deployment. Reads, exports and changes follow BP-42. Unauthorised users and NPCs must not infer protected locations or routines from schedule projections.

Administrative override requires defined authority, reason and audit event. A schedule's existence does not imply that every user may view its details. Reports expose only the minimum permitted temporal detail.

## 18. Inputs and outputs

**Inputs:** authorised schedule create/update/cancel commands; owner-domain references; canonical time advancement; calendar/timezone configuration; dependency events; pause/resume state; external timestamps with provenance; recovery watermarks.

**Outputs:** canonical time snapshot; validated schedule record/version; occurrence projections; due/blocked/expired queue entries; temporal comparisons; execution eligibility events; audit and diagnostics; read-only calendar/timeline projections.

All outputs include stable references and preserve owner attribution. BP-37 emits no domain outcome by itself.

## 19. State transitions

Schedule lifecycle: DRAFT → VALIDATED → ACTIVE → OCCURRENCE_DUE → EXECUTION_PENDING → COMMITTED, REJECTED, DEFERRED, FAILED or EXPIRED. Cancellation, suspension and supersession are explicit transitions. Recurring definitions remain distinct from occurrence lifecycle.

Clock lifecycle is coordinated with BP-35: PAUSED ↔ ACTIVE, with guarded ADVANCING, RECOVERING and SAFE_HALTED operational states. A failed transition cannot leave a partially advanced clock.

## 20. Invariants

- Exactly one authoritative in-world clock and calendar configuration.
- No simulation time or scheduled world activity progresses while paused/outside the game.
- No offline catch-up and no wall-clock-derived advancement.
- Monotonic committed time and stable event ordering.
- Due events never execute early.
- A schedule does not confer domain authority.
- Owner validation occurs immediately before action commit.
- Idempotent execution prevents duplicate side effects.
- Historical versions, source time, uncertainty and correction lineage are preserved.
- No schedule implies attendance, presence, consent or knowledge.
- No hidden truth or investigative hints are disclosed.
- Population and business invariants remain owned by BP-03/BP-04.
- No Neon write is authorised.

## 21. Storage and performance

Use compact schedule definitions and bounded occurrence projections. Store immutable changes and source events once; derive queue/calendar views. Use stable IDs, compact enumerations, indexed owner/status/due-time/priority fields and bounded payloads. Avoid duplicating names, addresses, biographies or domain facts.

Do not poll every person or business every tick. Use bounded recurrence horizons, relevant-entity activation, aggregate ambient schedules and explicit promotion of case-relevant events. Compaction must preserve meaning, versions, provenance, audit and replay sufficiency.

Before any future Neon write, measure the current database baseline; estimate incremental bytes/MiB and projected total with assumptions and uncertainty; obtain explicit user approval; then measure actual growth and compare. This document authorises no migration, seed, import or bulk write.

## 22. Failure handling and recovery

Invalid time configuration, missing owner, invalid reference, impossible interval, stale version, unavailable dependency, queue corruption, duplicate occurrence, transaction interruption or failed persistence must produce explicit diagnostics. Unsafe work is held, rejected or quarantined under declared policy; it is never silently discarded or force-executed.

Recovery restores the exact committed clock watermark, schedule versions, occurrence state and queue eligibility. Partial advancement is atomic: fully committed or rolled back. Safe halt preserves last known-good state. Recovery actions are attributable and replay-safe.

## 23. Observability

Expose current simulation instant, timezone/calendar version, pause state, committed watermark, queue depth, oldest due item, blocked/expired counts, retry counts, handler latency, failed execution, clock drift on external sources, recovery state and storage growth. Distinguish late, blocked, deferred, rejected, failed and committed work. Metrics and alerts do not themselves advance time.

## 24. Dependencies and interfaces

BP-35 coordinates execution and pause/resume. BP-38 validates schema and transactions. BP-39 persists clock/schedule/watermark state. BP-42 protects access. BP-43 tests deterministic chronology and failure cases. BP-44 governs calendar, timezone, recurrence, priority and precision configuration.

All domain divisions consume time services through documented contracts. Domain owners publish schedule definitions and action handlers; BP-37 does not duplicate their business rules.

## 25. Acceptance tests

These 130 criteria are required design acceptance criteria. None is claimed executed.

- AT-001: One authoritative in-world clock exists.
- AT-002: The clock uses one canonical instant and stable advancement sequence.
- AT-003: Timezone and calendar configuration are explicit and versioned.
- AT-004: Local civil time and canonical instant remain distinguishable.
- AT-005: Leap days and month/year boundaries are calculated deterministically.
- AT-006: Ambiguous or nonexistent local times follow an explicit policy.
- AT-007: Historical timestamps retain the calendar version under which they were recorded.
- AT-008: Device timezone never silently configures the fictional calendar.
- AT-009: Changing calendar configuration does not rewrite historical timestamps.
- AT-010: Clock state reconciles with the committed runtime watermark.
- AT-011: Leaving the simulation freezes all world time.
- AT-012: Real-world elapsed time never becomes fictional elapsed time.
- AT-013: No offline catch-up occurs after reopening.
- AT-014: Resume begins at the exact committed pause point.
- AT-015: Paused inspection is read-only with respect to world state.
- AT-016: Pause and resume transitions are attributable and ordered.
- AT-017: Repeated pause commands do not create duplicate transitions.
- AT-018: Repeated resume commands do not create duplicate active intervals.
- AT-019: Invalid or negative time increments are rejected.
- AT-020: A failed advancement leaves the last committed clock state intact.
- AT-021: Ordinary play cannot move the clock backwards.
- AT-022: Historical corrections are separate audited records.
- AT-023: Concurrent advancement requests serialize or reject without double advancement.
- AT-024: Every committed advancement has a unique sequence.
- AT-025: A zero-duration advance does not trigger future events.
- AT-026: Advancement is bounded by configured limits.
- AT-027: Clock and event transaction boundaries are atomic.
- AT-028: Interrupted advancement is fully committed or rolled back.
- AT-029: Recovery restores the exact committed watermark.
- AT-030: Clock drift is recorded rather than silently corrected.
- AT-031: Every schedule has a stable identifier.
- AT-032: Every schedule has one authoritative owner domain.
- AT-033: Schedules reference canonical entities rather than duplicating identity.
- AT-034: Schedule type is explicit and validated.
- AT-035: One-off schedules differ from recurrence definitions.
- AT-036: Schedule versions preserve prior definitions.
- AT-037: Creation records actor, authority, reason and provenance.
- AT-038: Modification records actor, authority, reason and prior version.
- AT-039: Cancellation preserves history and does not erase occurrences.
- AT-040: A schedule never grants authority to perform its action.
- AT-041: Recurrence generation is bounded to a configured horizon.
- AT-042: Month-end recurrence follows explicit calendar rules.
- AT-043: Leap-year recurrence is deterministic.
- AT-044: Civil-time transitions follow configured rules.
- AT-045: Exceptions affect only their declared scope.
- AT-046: Skipped occurrences remain auditable.
- AT-047: Rescheduled occurrences preserve original timing and change lineage.
- AT-048: Completed occurrences are not rewritten by future edits.
- AT-049: Recurrence expansion cannot create unbounded future rows.
- AT-050: Every occurrence references the schedule version that generated it.
- AT-051: An event cannot execute before its due time.
- AT-052: Due-time evaluation uses simulation time only.
- AT-053: Equal-time events have deterministic tie-breaking.
- AT-054: Priority cannot bypass causal prerequisites.
- AT-055: Dependencies between scheduled events are explicit.
- AT-056: Unavailable dependencies hold or reject work under declared policy.
- AT-057: Expired events follow owner-defined expiry policy.
- AT-058: Overdue status derives from active simulation time only.
- AT-059: Queue rebuild preserves deterministic ordering.
- AT-060: Queue rebuild does not duplicate committed actions.
- AT-061: BP-37 makes occurrences eligible but does not execute domain actions itself.
- AT-062: BP-35 coordinates runtime execution.
- AT-063: The owning domain validates current state before commit.
- AT-064: Idempotency keys prevent duplicate execution.
- AT-065: Retries are bounded and attributable.
- AT-066: Retry cannot bypass a domain validation failure.
- AT-067: Execution result distinguishes committed, rejected, deferred, failed and expired.
- AT-068: Compensation belongs to the owning domain.
- AT-069: A stale projection cannot authorise a resource-consuming action.
- AT-070: Failure records retain owner, schedule, occurrence and reason.
- AT-071: Deadlines do not elapse while paused.
- AT-072: Extensions and suspensions are explicit authorised transitions.
- AT-073: Completion records actual completion time and source action.
- AT-074: Cancellation preserves reason and authority.
- AT-075: A late-recorded fact is not assumed to have occurred late.
- AT-076: Occurred, effective, observed, recorded and committed times remain distinct.
- AT-077: Backdated facts require provenance and correction lineage.
- AT-078: Date-only facts are not converted into invented exact times.
- AT-079: Approximate times preserve uncertainty.
- AT-080: Unknown timezones remain unresolved rather than guessed.
- AT-081: A scheduled appointment does not prove attendance.
- AT-082: Attendance requires an authoritative attendance event.
- AT-083: A schedule does not prove a person was physically present.
- AT-084: Conflicting schedule claims are surfaced to the relevant owner.
- AT-085: Person availability derives from authoritative domain records.
- AT-086: BP-33 owns employment shifts and attendance policy.
- AT-087: BP-08 owns police rosters and deployment.
- AT-088: BP-26 owns custody clock policy.
- AT-089: BP-27 and BP-28 own legal deadlines and court listings.
- AT-090: BP-37 never duplicates canonical person identity.
- AT-091: BP-04 owns business opening-hour policy.
- AT-092: BP-37 provides temporal services to business schedules.
- AT-093: A scheduled delivery does not prove receipt of goods.
- AT-094: Resource availability is validated by its owning domain.
- AT-095: Travel feasibility is validated against canonical spatial/transport data.
- AT-096: Weather and environmental cycles freeze while paused.
- AT-097: Healthcare and public-service schedules freeze while paused.
- AT-098: Sentence progression freezes while paused.
- AT-099: NPC routines and social gatherings freeze while paused.
- AT-100: Domain owners retain authority over scheduled action meaning.
- AT-101: NPCs know only facts they observed, received or lawfully accessed.
- AT-102: A schedule cannot grant omniscient knowledge.
- AT-103: Scheduled attendance cannot be treated as proof of guilt.
- AT-104: Time data cannot reveal hidden offender truth.
- AT-105: The exact bingo reveal gate remains unchanged.
- AT-106: No schedule feature gives unsolicited investigative hints.
- AT-107: Generated NPC actions cannot silently replace player commands.
- AT-108: An empty queue does not cause invented NPC activity on resume.
- AT-109: Case-relevant persons remain permanently promoted.
- AT-110: Temporal compaction cannot remove case-relevant facts.
- AT-111: Sensitive schedules follow BP-42 access controls.
- AT-112: Protected persons' locations are not exposed to unauthorised actors.
- AT-113: Informant, witness, victim and medical schedules receive restricted handling.
- AT-114: Police personnel schedules have role-authorised visibility.
- AT-115: Reads and changes are attributable where required.
- AT-116: Exports preserve source references and uncertainty.
- AT-117: Historical schedule versions remain queryable.
- AT-118: Correction lineage cannot be silently deleted.
- AT-119: Schemas and constraints are validated through BP-38.
- AT-120: Durable clock and schedule state are managed through BP-39.
- AT-121: Queue processing avoids polling all 10,000 people continuously.
- AT-122: Person schedules use relevance-based activation and bounded wake-ups.
- AT-123: Business schedules use proportionate aggregate processing where safe.
- AT-124: Case-relevant events are never aggregated away.
- AT-125: Recurring schedule storage remains bounded.
- AT-126: Indexes support due-time, owner, status and priority lookup.
- AT-127: Monitoring exposes clock watermark and queue depth.
- AT-128: Diagnostics distinguish blocked, deferred, rejected and failed work.
- AT-129: Safe halt preserves last known-good clock and queue state.
- AT-130: No BP-37 specification action authorises a Neon write.

## 26. Source traceability

The authoritative crosswalk maps the following requirements and tests to BP-37. Original wording remains in docs/governance/SALTWATER_MASTER_BLUEPRINT.json.

| Source ID | Source division | Incorporated intent |
|---|---|---|
| S03.R03 | Population accounting and demographic model | Temporal support for age, household, residence, occupation, eligibility, movement and life events; BP-03 retains population ownership and cap enforcement. |
| S04.R01 | Person identity and life records | Person schedules, needs, skills, employment, finances and relationship timelines reference canonical person records without duplication. |
| S05.R02 | Households, relationships and social networks | Relationship history, shared-address periods, contact patterns and plausible changes retain effective and recorded time. |
| S41.R01 | Time, calendar, schedules and simulation clock | One authoritative clock/calendar/timezone basis for shifts, opening hours, deadlines and event ordering. |
| S41.R02 | Time, calendar, schedules and simulation clock | No time advances outside the simulation; resume exactly without hidden elapsed time. |
| S41.R03 | Time, calendar, schedules and simulation clock | Support paused, active, queued and historical event states. |
| S42.R01 | Simulation engine, causality and world activity | Coordinate people, organisations, services, incidents, schedules, resources, weather and time through auditable deterministic event processing where feasible; BP-35 owns execution. |
| S42.R03 | Simulation engine, causality and world activity | Prevent impossible simultaneous states, causal loops and unexplained state mutation through owner validation and temporal invariants. |
| S42.R04 | Simulation engine, causality and world activity | Background activity does not advance while player is out. |
| S41.T01 | Time, calendar, schedules and simulation clock | All event timestamps use one canonical time basis and stable ordering. |
| S42.T01 | Simulation engine, causality and world activity | Replay of recorded event sequence yields the same authoritative state where deterministic replay is specified. |

**Traceability audit:** 11 mapped IDs checked against the current crosswalk; no extra IDs claimed.

## 27. Open configuration decisions

1. Fictional calendar epoch, month lengths, leap-year rule and weekday naming.
2. Canonical timezone identity and offset; whether civil-time seasonal transitions exist.
3. Timestamp precision and canonical ordering sequence.
4. Maximum active-time advancement per player command and simulation-step granularity.
5. Whether active simulation time advances continuously while the player is actively playing or only through explicit commands.
6. Schedule type catalogue and required fields by type.
7. Recurrence syntax, bounded expansion horizon and exception semantics.
8. Event priority classes, fairness and starvation bounds.
9. Expiry, retry, deferral and dependency-timeout policies.
10. External timestamp ingestion, clock-drift tolerance and uncertainty representation.
11. Historical correction authority and permissible correction scope.
12. Queue partitioning, idempotency-key format and replay compatibility.
13. Sensitive schedule access matrix and audit retention.
14. Operational thresholds for queue depth, lateness, retry and recovery.
15. Exact BP-43 evidence format and test harness.

These are fictional/technical configuration decisions, not permission to introduce real-world legal assumptions or advance time while paused.

## 28. Completion status

- Specification: DESIGNED_DRAFT; review/approval pending.
- Implementation: NOT_STARTED.
- Test execution: NOT_STARTED. The 130 criteria are not execution evidence.
- Verification: NOT_STARTED.
- Neon: No database write performed or authorised.
- Next division in fixed numeric order: BP-38 — Records and Databases.
