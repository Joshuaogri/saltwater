# BP-43 — Testing and Quality Assurance

**Project:** Saltwater  
**Division:** BP-43 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT — review/approval pending  
**Implementation / test execution / verification:** NOT_STARTED  
**Primary responsibility:** Test strategy, quality gates, test evidence, validation, benchmarking and release-readiness evidence.  
**Write restriction:** This specification authorises no Neon write, migration, seed/import, bulk operation, upload, credential change or production deployment.

## 1. Purpose

BP-43 defines how Saltwater's specifications, implementation, data, simulation behaviour, interfaces, persistence, security and operations are tested and how quality evidence is recorded. It establishes a consistent test lifecycle and evidence standard across all 44 divisions while leaving domain ownership with the relevant division.

BP-43 does not implement domain behaviour or declare a feature complete by assertion. It defines how requirements are verified, how defects and exceptions are handled, and what evidence is needed to distinguish a design draft, implemented capability, executed test and verified result.

## 2. Governing principles

1. Requirements first: every test traces to an authoritative requirement and an owning division.
2. Evidence first: no test pass or verification claim without execution evidence appropriate to the claim.
3. Preserve the distinction between designed, approved, implemented, tested and verified.
4. Test both permitted behaviour and prohibited behaviour; negative tests are mandatory for security and integrity boundaries.
5. Test domain owners and their cross-division contracts without transferring ownership to BP-43.
6. Reproducibility: record commit, schema, configuration, environment, fixtures, inputs and random seed where applicable.
7. No silent exceptions: known failures have owner, risk acceptance authority, rationale and review/expiry.
8. A successful static check or GitHub commit is not proof of runtime correctness or live database connectivity.
9. Test synthetic data is clearly separated from canonical simulation facts and production data.
10. No Neon write without baseline, quantified estimate and explicit user approval; measure actual growth after approved writes.
11. Text-first essential workflows and the single-city/10,000-person canon are testable invariants.
12. No in-world time advances while player is absent or simulation paused.

## 3. Scope and ownership boundary

**BP-43 owns:** test policy and taxonomy; test plans/cases/suites; fixtures and isolated test data; execution records; coverage and traceability; defect/exception evidence; quality gates; schema/migration/replay/load/storage/security/recovery testing; cross-system reconciliation; performance and narrative-quality evaluation; release-readiness evidence.

**BP-43 does not own:** domain implementation or business rules; canonical schemas (BP-38); backup execution (BP-39); simulation event execution (BP-35); time (BP-37); security policy (BP-42); formal canon/configuration approval (BP-44); domain acceptance decisions that belong to the user or owning authority. It verifies those contracts and reports evidence.

## 4. Test taxonomy and levels

Required test families include unit, component, contract, integration, schema/constraint, migration, end-to-end, replay/determinism, regression, property/invariant, boundary, negative, adversarial, concurrency/race, idempotency, load, stress, soak/continuity, storage/benchmark, security, accessibility/text workflow, narrative quality, backup/restore and operational recovery.

Test level is not inferred from test name. Each test states what it exercises, what it excludes, its dependencies and whether it uses a live external service. Live Neon connectivity is only proven by a successful current connection test; mocks and cached output are labelled as such.

## 5. Test artefacts and entities

Canonical artefacts include requirement reference, test case, test suite, test plan, fixture/dataset, environment profile, execution run, individual result, evidence attachment/reference, defect, risk exception, coverage record, benchmark, quality gate, release assessment and verification record.

Each has a stable ID, version, lifecycle, owner, timestamps, provenance and links. Test IDs are immutable and never silently reused. Superseded tests retain history and point to replacements. Results refer to the exact test definition and software/schema/configuration versions executed.

## 6. Test lifecycle and execution

Lifecycle: proposed → reviewed → approved for use → ready → executing → passed / failed / blocked / skipped / not-applicable → reviewed → superseded or retired. A run records prerequisites, environment, actor, commit, schema version, configuration, test-suite revision, fixture versions, inputs, expected and actual outcomes, timestamps, logs/evidence and cleanup status.

Randomized execution records seed and enough context to reproduce. Retries append new results and preserve original failures; they do not overwrite or conceal flakiness. A flaky test has an owner, defect record, impact and remediation plan. A skipped or blocked test is never counted as passed.

## 7. Evidence and result semantics

Evidence may include structured assertions, query results, logs, screenshots, exported artefacts, checksums, benchmark measurements, replay comparisons, restore reports or reviewer attestations. Evidence must be attributable to a run and retained under BP-38/BP-39/BP-42 policy.

Statuses: PASS only when expected criteria are met and evidence is attached/referenced; FAIL when an assertion is not met; BLOCKED when prerequisites/configuration/provider capability prevent valid execution; SKIPPED only by explicit recorded decision; NOT_APPLICABLE only with reason and authorised reviewer. A successful file creation, commit, static inspection or unexecuted test definition is not a runtime pass.

Verification requires an identified target, scope, method, evidence, reviewer/authority and result. A division may be designed but not approved; implemented but untested; tested but not verified; or verified only within an explicitly bounded scope.

## 8. Requirements, traceability and coverage

Every requirement has stable source ID, canonical wording, target division, acceptance criteria, implementation reference where applicable, test IDs and evidence. Crosswalk mappings are preserved; BP-43 tests assigned source IDs but does not rewrite source wording. Coverage reports distinguish requirement coverage, test definition coverage, execution coverage, pass rate, blocked coverage and evidence completeness.

Every division supplies its own domain acceptance criteria under the fixed specification contract. BP-43 verifies that criteria are traceable, testable and evidenced. It does not add, remove, reorder, rename, split or merge the fixed 44 divisions.

## 9. Test environments, fixtures and data

Environments are explicitly named and isolated: local/development, test/CI, staging if configured, and authoritative production. Each environment records service endpoints by safe identifier, schema/configuration versions, provider dependencies, capabilities and access boundaries. Test accounts and synthetic data cannot reach canonical records or real delivery channels by default.

Fixtures are deterministic and minimal where possible; test data is labelled synthetic. Avoid copying personal, protected, evidential or secret content into lower environments. Fixture cleanup is explicit and safe. Test runs never mutate authoritative simulation state unless the user has explicitly approved the specific operation and the required pre-write storage procedure has been completed.

## 10. Test design and quality dimensions

Tests cover correctness, completeness, consistency, integrity, security, privacy, availability, performance, scalability, resilience, recoverability, usability, accessibility, narrative quality and operational maintainability as relevant to the requirement.

Each test identifies preconditions, action, expected result, negative conditions, boundaries, state transitions, side effects, ownership interfaces and evidence. Include null/empty/malformed/oversized/duplicate/conflicting input, partial failure, retries, concurrency and long-running continuity where relevant. Tests must verify both the desired outcome and the absence of forbidden side effects.

## 11. Cross-system reconciliation

Test contracts among canonical person/population, businesses/property, police personnel/career/units, operations/dispatch, crime/cases/investigations, victim/witness/suspect roles, scenes/evidence/forensics, arrests/custody/legal/courts/corrections, HR/finance, engine/time, records/persistence, interface/reporting, security and configuration.

Reconciliation identifies orphaned IDs, contradictory lifecycle states, duplicate people, invalid authority, mismatched employment/occupancy, evidence continuity gaps, unbalanced accounting, event replay divergence, stale permissions, hidden-truth leakage and time progression while paused. Each mismatch creates a defect or a documented, approved exception; it is never silently normalised.

## 12. Scale, population and storage validation

Test the hard cap of 10,000 living persons across all represented roles, with no duplicate counting and no bypass through accounts, personnel, contractors, service roles or test fixtures. Test at least 10,000 businesses within the one-city world; test variety, identity, lifecycle and valid premises/mobile/virtual basis.

Storage tests use representative high-entropy narrative and structured records. Measure row, table, index and TOAST growth; include realistic indexes, transactions and retrieval. Compression may reduce structural overhead but must not remove meaningful narrative, source detail, provenance or case facts.

Before every proposed Neon migration, schema change, seed/import, bulk write or upload: measure current baseline; estimate incremental bytes and MB/MiB; state method, assumptions and uncertainty; calculate projected total; present the result and wait for explicit user approval. If the estimate is not credible, benchmark first. After an approved write, measure actual growth and record variance. This division does not authorise any write.

## 13. Security, privacy and adversarial testing

Test authentication and authorization at service boundaries, not just interface visibility. Cover privilege escalation, role/assignment changes, direct API access, identifier enumeration, search/count leakage, cache invalidation, exports, media, notifications, maps, AI context, secrets, audit integrity, environment isolation and revocation.

Test exact `bingo` reveal semantics and every near-match non-trigger. Verify hidden truth is absent from player-facing and unauthorised operator paths. Test prompt injection and untrusted content without allowing it to override canon, permissions or player agency.

## 14. Simulation, causality and narrative quality

Test deterministic replay where specified, event ordering, idempotency, concurrency, impossible state prevention, relevance-based processing, continuity and population promotion. Verify pause/exit freezes in-world events, deadlines, queues, NPC actions and simulation clocks. Real authentication/session protections may continue without advancing the game.

Narrative quality tests evaluate continuity, character voice, uncertainty, source distinction, non-repetition, plausible NPC knowledge, lack of unsolicited hints and no hidden truth leakage. AI-generated assertions that alter canon must be backed by structured, attributable domain events.

## 15. Performance, resilience and operational testing

Benchmarks state hardware/runtime, provider, dataset size, concurrency, warm/cold conditions, repetitions and measurement method. Test expected load, stress thresholds, graceful degradation, queue growth, failed events, latency, memory/resource use and database growth. Long-running tests detect drift, orphan records, leaks and unbounded logs.

Test maintenance, backup/restore, rollback or forward recovery, service outage, provider timeout and partial failure in isolated environments before authoritative use. Never claim provider capabilities or live health from assumptions or stale observations.

## 16. Defects, exceptions and release gates

Defects record severity, affected requirement/division, reproduction steps, environment, evidence, owner, impact, mitigation and retest. Critical defects block the affected release unless an explicitly authorised risk exception exists. Exceptions record authority, rationale, affected scope, compensating controls, expiry/review date and closure evidence.

Release gates assess specification completeness, design approval, implementation readiness, test execution, blocking defects, evidence completeness, security, storage impact, migration/recovery readiness and operational readiness separately. Passing one gate never implies another has passed. BP-44 owns change approval; user approval remains mandatory for canon changes and Neon writes.

## 17. Reporting and observability

Reports distinguish test definitions from executed runs; pass/fail/blocked/skipped/not-applicable; requirement and division coverage; open defects; exceptions; flaky tests; performance/storage metrics; security findings; recovery results; and release recommendation. Every report is scoped to exact commit, schema, configuration and test-suite revision.

Operational metrics and logs are not substitutes for test evidence. Monitoring identifies failures and supports triage; BP-41 owns notification/report delivery semantics and BP-38/BP-39 own durable records.

## 18. Inputs, outputs and dependencies

**Inputs:** authoritative requirements and crosswalk; division specifications; implementation commits; schema/configuration versions; test plans/cases; fixtures; environment profiles; execution telemetry; defects; benchmarks; security and recovery policies.

**Outputs:** test plans/suites; execution records; evidence references; coverage maps; defects and exceptions; benchmark reports; reconciliation results; quality-gate assessments; release-readiness recommendations.

**Dependencies:** BP-01–BP-42 and BP-44. BP-43 consumes their contracts and verifies them; it does not become the owner of their domain data or behaviour.

## 19. Acceptance tests

The following are required acceptance criteria for BP-43 itself. They are design criteria, not executed results.

- QA-AT-001: Every division specification has explicit, traceable acceptance criteria before implementation is declared complete.
- QA-AT-002: Every acceptance criterion has a stable unique identifier and an unambiguous pass/fail or justified not-applicable outcome.
- QA-AT-003: Every test maps to one or more governing requirements and identifies its owning division.
- QA-AT-004: Every implementation item maps to an approved requirement and evidence.
- QA-AT-005: Design approval, implementation, test execution and verification are separately recorded statuses.
- QA-AT-006: An unapproved design cannot be treated as approved merely because tests pass.
- QA-AT-007: A passing test cannot be claimed when it was not executed against the stated target.
- QA-AT-008: Every test result records test ID, version, environment, inputs, expected result, actual result, status and evidence reference.
- QA-AT-009: Test evidence identifies the actor or automation identity and execution time.
- QA-AT-010: Test runs are reproducible from versioned test definitions, fixtures and configuration.
- QA-AT-011: Test suites distinguish unit, component, integration, contract, schema, migration, end-to-end, replay, load, security and recovery testing.
- QA-AT-012: Each test declares prerequisites, setup, cleanup and isolation requirements.
- QA-AT-013: Test fixtures are deterministic where determinism is required and explicitly seeded where randomness is tested.
- QA-AT-014: Randomized tests record seed and reproducible execution context.
- QA-AT-015: Flaky tests are identified, tracked and not silently counted as passing.
- QA-AT-016: Retries preserve original failure evidence and do not conceal intermittent defects.
- QA-AT-017: Test failures are classified by severity, affected domain, reproducibility and release impact.
- QA-AT-018: Known failures have owner, rationale, risk acceptance authority and expiry/review date.
- QA-AT-019: Critical failures block the affected release or deployment unless an explicit documented exception is approved.
- QA-AT-020: Test coverage measures meaningful requirement and risk coverage, not only line or branch counts.
- QA-AT-021: Every division has positive, negative, boundary and lifecycle tests appropriate to its scope.
- QA-AT-022: Cross-division contracts are tested at both producer and consumer boundaries.
- QA-AT-023: Shared identifiers, foreign keys, relationship cardinality and referential integrity are tested.
- QA-AT-024: Canonical person identity is unique across roles and person promotion does not create duplicate people.
- QA-AT-025: The 10,000 living-person hard cap is tested at boundary, concurrency and import paths.
- QA-AT-026: Population replacement after death or permanent exit is tested without exceeding the hard cap.
- QA-AT-027: At least 10,000 businesses are supported without violating the single-city world constraint.
- QA-AT-028: No test fixture introduces an additional playable city or external territory.
- QA-AT-029: All represented locations resolve within Saltwater or are explicitly marked off-map.
- QA-AT-030: Business identities, sector, location, status, employment and premises occupancy reconcile.
- QA-AT-031: Business variety and traceable ownership are tested against mass-generation duplication.
- QA-AT-032: Police rank, position, grade, authority, powers, clearance, qualification and assignment remain distinct in data and behaviour.
- QA-AT-033: Police staffing and all other people count once against the global population cap.
- QA-AT-034: Personnel, career, unit, roster, dispatch and deployment interfaces reconcile.
- QA-AT-035: Recruit, probation, promotion, lateral move, acting appointment, transfer, retirement and separation lifecycle tests exist.
- QA-AT-036: Mandatory retirement is based on 35 years of police service, not age.
- QA-AT-037: Police Chief exception requires formal appointment before 35 years of service, five-year terms, one renewal and no third term.
- QA-AT-038: Case lifecycle, assignment, closure, reopening, merge/split and related-case links preserve history.
- QA-AT-039: Investigation leads, allegations, intelligence, evidence, facts, findings and outcomes remain distinct.
- QA-AT-040: Case-related people are promoted to persistent full simulation without duplicate identity or population-cap violation.
- QA-AT-041: Victim, witness, suspect and offender roles can coexist without overwriting one another.
- QA-AT-042: NPC knowledge tests prove no actor knows facts they have not observed, received or lawfully accessed.
- QA-AT-043: Hidden culprit/accomplice truth never leaks before exact bingo trigger.
- QA-AT-044: Near-match strings and paraphrases do not activate the bingo reveal gate.
- QA-AT-045: No unsolicited investigation hints or forced player choices appear in generated outputs.
- QA-AT-046: Crime generation preserves causal consistency and does not predetermine player investigative success.
- QA-AT-047: Crime taxonomy, classification and historical reclassification preserve source provenance.
- QA-AT-048: Evidence registration, exhibit identity, continuity, handler transfers and seals reconcile.
- QA-AT-049: Physical and digital evidence derivatives retain source links and integrity metadata.
- QA-AT-050: Crime-scene access, search zones, measurements, observations and interpretations remain distinguishable.
- QA-AT-051: Forensic requests, methods, raw results, interpretation and reports remain linked and attributable.
- QA-AT-052: Interview recordings, transcripts, statements, corrections and participant chronology reconcile.
- QA-AT-053: Surveillance records preserve source device, coverage, blind spots, time basis and authorisation.
- QA-AT-054: Intelligence preserves source grading, confidence, dissemination restrictions and separation from evidence.
- QA-AT-055: Arrest, warrant, custody, charge, court finding, sentence and correctional status do not auto-convert into one another.
- QA-AT-056: Custody clocks and sentence calculations follow configured rules and authoritative orders.
- QA-AT-057: Legal disclosure, redaction, court orders, appeal and correctional execution preserve authority boundaries.
- QA-AT-058: Police governance, professional standards, complaints, discipline and appeals retain fair process and audit evidence.
- QA-AT-059: Training prerequisites block deployments or roles where configured and training history is retained.
- QA-AT-060: HR employment, attendance, leave, timesheets and payroll inputs reconcile with finance ownership.
- QA-AT-061: Financial postings balance under the selected accounting model and corrections use traceable entries.
- QA-AT-062: Procurement, receipt, invoice, liability, payment and asset acquisition lifecycles reconcile.
- QA-AT-063: Simulation event replay produces the same authoritative state where deterministic replay is specified.
- QA-AT-064: Event processing rejects impossible simultaneous states and unexplained mutations.
- QA-AT-065: Relevance-based processing does not lose persistent state or required continuity.
- QA-AT-066: Player exit or pause freezes all in-world activity, deadlines, queues, NPC actions and simulation clocks.
- QA-AT-067: Real security session expiry and credential revocation do not advance simulation time.
- QA-AT-068: Text interface supports every essential workflow without requiring graphics.
- QA-AT-069: Optional maps and visuals never become the sole carrier of essential evidence or controls.
- QA-AT-070: Commands and views provide useful safe errors without disclosing restricted records.
- QA-AT-071: Accessibility and readable text presentation are tested across essential workflows.
- QA-AT-072: Notifications are delivered only to authorised recipients and preserve source permissions.
- QA-AT-073: Reports, dashboards, exports and public outputs respect redaction and information classification.
- QA-AT-074: Search, counts, facets, autocomplete, pagination and map results do not leak inaccessible records.
- QA-AT-075: AI receives only authorised context and cannot override security policy or reveal hidden truth.
- QA-AT-076: Every protected read/write is denied when the principal lacks permission and the denial is audited.
- QA-AT-077: Secrets are absent from source control, narrative records, ordinary logs, reports and outputs.
- QA-AT-078: Development, test and authoritative production environments are separated.
- QA-AT-079: Test identities cannot mutate authoritative player data by default.
- QA-AT-080: No test suite sends real external notifications or uses production credentials unintentionally.
- QA-AT-081: Neon connectivity is reported only after a successful live connection test.
- QA-AT-082: Schema constraints enforce identity, referential integrity, population cap and lifecycle states.
- QA-AT-083: Migrations are tested against a representative baseline and supported upgrade path.
- QA-AT-084: Migration rollback or forward-recovery behaviour is tested before deployment.
- QA-AT-085: Partial writes and transaction failures leave no inconsistent authoritative state.
- QA-AT-086: Immutable source records/events remain distinct from derived views and summaries.
- QA-AT-087: Long narrative content is preserved losslessly through storage, retrieval, export and recovery.
- QA-AT-088: Storage benchmarks use representative high-entropy long text rather than only compressible fixtures.
- QA-AT-089: Row, table, index and TOAST growth are measured and attributable.
- QA-AT-090: Before every proposed Neon write, baseline measurement is captured from the current database.
- QA-AT-091: Every proposed Neon write has an incremental estimate in bytes and MB/MiB, method, assumptions and uncertainty range.
- QA-AT-092: Projected post-write database size is calculated and disclosed before requesting approval.
- QA-AT-093: No Neon write, migration, seed/import, bulk write or upload occurs without explicit user approval after the estimate.
- QA-AT-094: If an estimate is not credible, representative benchmarking occurs before deployment is proposed.
- QA-AT-095: After an approved write, actual database growth is measured and compared with the estimate.
- QA-AT-096: Post-deployment measurement records actual delta and explains material variance.
- QA-AT-097: Database connectivity, storage measurements and write approvals are not inferred from stale logs or old results.
- QA-AT-098: Backup cadence, retention and recovery objectives are tested against configured policy.
- QA-AT-099: Restore tests reproduce a verified checkpoint with integrity, permissions and audit continuity.
- QA-AT-100: Backups are separate from live mutable state and protected by appropriate access controls.
- QA-AT-101: Recovery procedures preserve canon, authoritative records, provenance and hidden-truth protections.
- QA-AT-102: Service health, errors, latency, queue depth, resource use, database size and failed events are observable.
- QA-AT-103: Operational alerts are attributable and distinguish warning, failure and confirmed incident.
- QA-AT-104: Maintenance and rollback procedures are tested in isolated environments before authoritative use.
- QA-AT-105: Configuration drift is detected and reported.
- QA-AT-106: Security tests cover authentication, authorization, privilege escalation, secret leakage and access revocation.
- QA-AT-107: Security tests cover direct API, UI, search, export, media, notification, map and AI paths.
- QA-AT-108: Audit logs are tamper-evident and cannot be silently altered by ordinary administrators.
- QA-AT-109: Policy changes are tested before activation and rollback preserves audit history.
- QA-AT-110: Race-condition tests cover concurrent updates, duplicate submissions and competing state transitions.
- QA-AT-111: Idempotency tests prove retries do not duplicate people, incidents, payments, exhibits or events.
- QA-AT-112: Concurrency tests cover population cap, unique IDs, dispatch assignment and resource allocation.
- QA-AT-113: Load tests cover peak expected police activity and city baseline without violating correctness.
- QA-AT-114: Stress tests establish failure thresholds and graceful degradation behaviour.
- QA-AT-115: Long-running continuity tests detect state drift, orphan records and unbounded growth.
- QA-AT-116: Performance tests use declared hardware, dataset size, concurrency and measurement method.
- QA-AT-117: Test results record resource consumption and storage impact where relevant.
- QA-AT-118: Boundary tests cover empty, null, malformed, oversized, duplicate and conflicting input.
- QA-AT-119: Adversarial tests cover prompt injection, malformed commands, identifier enumeration and data exfiltration.
- QA-AT-120: Negative tests prove forbidden actions fail safely rather than partially succeeding.
- QA-AT-121: Error handling preserves useful operator diagnostics without exposing secrets or protected facts.
- QA-AT-122: Cross-system reconciliation detects mismatched people, employment, premises, evidence, finance and case states.
- QA-AT-123: Every failed reconciliation produces an attributable defect or explicitly accepted exception.
- QA-AT-124: Regression suites run against affected domains and declared dependency contracts after changes.
- QA-AT-125: Test impact analysis identifies downstream domains affected by schema, policy or event changes.
- QA-AT-126: Change control requires linked requirements, approvals, migration impact and test evidence.
- QA-AT-127: Blueprint or division structure changes are rejected unless explicitly approved by the user.
- QA-AT-128: Retired tests retain history and replacement links; identifiers are never silently reused.
- QA-AT-129: Test data and generated fixtures are clearly marked and cannot be mistaken for canonical simulation facts.
- QA-AT-130: Quality gates distinguish specification completeness, implementation readiness, test pass and operational verification.
- QA-AT-131: Acceptance criteria that depend on unresolved fictional configuration are marked blocked/configurable, not silently passed.
- QA-AT-132: Every division's evidence package can be independently reviewed from repository references.
- QA-AT-133: All test reports identify exact commit, schema version, configuration and test-suite revision.
- QA-AT-134: Every implementation item traces to an approved requirement and recorded evidence.
- QA-AT-135: Operational failures are detectable, attributable, recoverable and included in regression tests.
- QA-AT-136: AI-generated narrative quality is assessed for continuity, character voice, knowledge boundaries, uncertainty and non-repetition.
- QA-AT-137: Generated content cannot silently mutate authoritative facts without a structured, auditable domain event.
- QA-AT-138: Every material quality exception has a documented risk owner, approval and review/expiry date.
- QA-AT-139: Final release gate checks all blocking failures, unresolved critical defects and evidence completeness.
- QA-AT-140: Test execution status cannot be changed to passed without attached or referenced execution evidence.
- QA-AT-141: Verification status cannot be set complete solely from a successful commit or static file creation.
- QA-AT-142: Acceptance test coverage includes the exact source traceability IDs assigned to BP-43.
- QA-AT-143: Source requirement wording is preserved in traceability and not weakened by test summaries.

## 20. Source traceability

The following source requirements/tests are assigned to BP-43 by the authoritative 52→44 crosswalk. Wording is copied from the unchanged source JSON.

| Source ID | Source division | Original requirement/test wording |
|---|---|---|
| S07.R01 | Businesses and commercial economy | Maintain a dedicated business registry with stable IDs, sector, premises, ownership, operators, employees, opening hours, finances, assets, services and lifecycle. |
| S07.R02 | Businesses and commercial economy | Represent supply, demand, customers, contracts, inventory, deliveries, debts, closures and commercial relationships at a functional level. |
| S07.R03 | Businesses and commercial economy | Ensure businesses create realistic employment, premises access, records, witnesses, transactions and police-relevant activity. |
| S07.R04 | Businesses and commercial economy | Avoid mass-generated indistinguishable businesses; maintain coherent variety and traceable ownership. |
| S07.T01 | Businesses and commercial economy | Every active business has a valid status, sector and location or explicit mobile/virtual basis. |
| S07.T02 | Businesses and commercial economy | Business employment and premises occupancy reconcile. |
| S10.R01 | Public finance, taxation and economic accounts | Define currency, public revenue, taxation, fees, expenditure, budgets, debt, grants and financial periods. |
| S10.R02 | Public finance, taxation and economic accounts | Represent business and household finances at a level needed for city function and police cases. |
| S10.R03 | Public finance, taxation and economic accounts | Maintain arithmetic and audit trails; avoid fabricated unbalanced totals. |
| S10.T01 | Public finance, taxation and economic accounts | Every posted transaction balances under its accounting model. |
| S42.R01 | Simulation engine, causality and world activity | Coordinate people, organisations, services, incidents, schedules, resources, weather and time through deterministic, auditable event processing where feasible. |
| S42.R02 | Simulation engine, causality and world activity | Use relevance-based processing without breaking persistence or continuity. |
| S42.R03 | Simulation engine, causality and world activity | Prevent impossible simultaneous states, causal loops and unexplained state mutation. |
| S42.R04 | Simulation engine, causality and world activity | Background activity must not advance while the player is out. |
| S42.T01 | Simulation engine, causality and world activity | Replay of a recorded event sequence yields the same authoritative state where deterministic replay is specified. |
| S44.R01 | Text interface, commands and player workflow | Provide a laptop-style, text-first interface with clear navigation, commands, records, status and contextual actions. |
| S44.R02 | Text interface, commands and player workflow | Support individual-officer gameplay, including recruit start where selected. |
| S44.R03 | Text interface, commands and player workflow | Keep prose and source records readable while using compact presentation for navigation and metadata. |
| S44.R04 | Text interface, commands and player workflow | No essential action depends on graphics. |
| S44.T01 | Text interface, commands and player workflow | All essential workflows are operable through text commands and views. |
| S46.R01 | Database, schemas and persistence | Use Neon PostgreSQL as the persistent database and GitHub as source control, specification and migration history; ChatGPT is the user-facing AI partner/interface. |
| S46.R02 | Database, schemas and persistence | Define canonical schemas, constraints, relationships, IDs, migrations, indexes and transaction boundaries. |
| S46.R03 | Database, schemas and persistence | Store detailed narrative losslessly; normalise shared facts, reference repeated entities and avoid duplicate payloads. |
| S46.R04 | Database, schemas and persistence | Separate immutable source records/events from derived views and summaries. |
| S46.R05 | Database, schemas and persistence | Never claim live database connectivity without a successful connection test. |
| S46.T01 | Database, schemas and persistence | Schema constraints enforce identity, referential integrity, population cap and valid lifecycle states. |
| S47.R01 | Storage efficiency and capacity governance | Use compact keys, enums, references, normalisation, deduplication and lossless compression where justified; compress structure, never meaningful narrative. |
| S47.R02 | Storage efficiency and capacity governance | Avoid redundant fields, duplicate text, unnecessary indexes, repeated snapshots and unbounded logs. |
| S47.R03 | Storage efficiency and capacity governance | Measure row, table, index and TOAST growth; benchmark representative high-entropy long text. |
| S47.R04 | Storage efficiency and capacity governance | Before every Neon migration, schema change, seed/import, bulk write or upload, show current measured baseline, incremental estimate in bytes and MB/MiB, method, assumptions, uncertainty range and projected total; wait for explicit user approval. |
| S47.R05 | Storage efficiency and capacity governance | After approved deployment, measure actual growth and compare with estimate. If estimate is not credible, benchmark first; do not deploy. |
| S47.T01 | Storage efficiency and capacity governance | No Neon write occurs without explicit approval after a documented estimate. |
| S47.T02 | Storage efficiency and capacity governance | Post-deployment measured delta is recorded. |
| S48.R01 | Security, permissions and information boundaries | Define user, player, officer, administrator and system roles; least privilege; secret handling; access checks and audit logs. |
| S48.R02 | Security, permissions and information boundaries | Protect hidden case truth and restricted personal information from player-facing leakage. |
| S48.R03 | Security, permissions and information boundaries | Keep credentials out of source control, narrative records and logs. |
| S48.T01 | Security, permissions and information boundaries | Unauthorised reads/writes are rejected and audited. |
| S49.R01 | Backups, recovery and data integrity | Define backup cadence, retention, restore testing, point-in-time recovery where available, export format and disaster recovery procedure. |
| S49.R02 | Backups, recovery and data integrity | Protect canon and authoritative records against corruption, accidental overwrite and partial writes. |
| S49.R03 | Backups, recovery and data integrity | Keep recoverable backups separate from live mutable state. |
| S49.T01 | Backups, recovery and data integrity | A tested restore reproduces a verified checkpoint. |
| S50.R01 | Testing, validation and simulation quality | Maintain unit, integration, schema, migration, end-to-end, replay, load, population, storage and narrative-quality tests. |
| S50.R02 | Testing, validation and simulation quality | Test edge cases, adversarial inputs, boundary conditions, race conditions, long-running continuity and cross-system reconciliation. |
| S50.R03 | Testing, validation and simulation quality | Use evidence-based completion criteria and regression gates. |
| S50.T01 | Testing, validation and simulation quality | Every division has traceable acceptance tests and recorded results. |
| S51.R01 | Operations, observability and maintenance | Track service health, errors, latency, job queues, resource use, database size, failed events and recovery actions. |
| S51.R02 | Operations, observability and maintenance | Provide safe maintenance, migration, rollback and incident procedures. |
| S51.R03 | Operations, observability and maintenance | Separate development/test data from authoritative simulation data. |
| S51.T01 | Operations, observability and maintenance | Operational failures are detectable, attributable and recoverable. |
| S52.R01 | Canon, versioning and change control | Maintain a single canonical blueprint version, decision log, glossary, schema registry and traceability matrix. |
| S52.R02 | Canon, versioning and change control | No unapproved changes to canon, division structure, requirements or approved design. |
| S52.R03 | Canon, versioning and change control | Record every amendment with reason, approval, affected requirements, migration impact and tests. |
| S52.R04 | Canon, versioning and change control | Keep proposed, approved, implemented, verified and retired states distinct. |
| S52.T01 | Canon, versioning and change control | Every implementation item maps to an approved requirement and evidence. |

## 21. Open configuration and implementation decisions

1. Test runner, CI provider and execution orchestration.
2. Test ID namespace and machine-readable test/result schema.
3. Evidence storage, retention and access policy.
4. Environment topology and synthetic fixture strategy.
5. Coverage reporting and quality-gate thresholds.
6. Defect severity taxonomy and release-blocking thresholds.
7. Performance/load targets and representative hardware/data sizes.
8. Benchmark methodology for high-entropy narrative and Neon storage.
9. Safe migration/rollback test strategy and isolated database environments.
10. Security/adversarial test harness and red-team scope.
11. Backup/restore test cadence and recovery acceptance thresholds.
12. Narrative-quality rubric and human review workflow.
13. CI concurrency, retry policy, flaky-test quarantine and failure notification.
14. Artifact retention, reproducibility and test data disposal.
15. Approval roles for exceptions and quality-gate waivers.

## SW-NAM-001 — naming test slice

Added deterministic Python tests for the transactional PostgreSQL adapter contract, NFKC/case-folding, punctuation and road suffix variants, display-spelling preservation, collision classes, near-duplicate review, retired-name protection, rename history, generator reproducibility, immutable generator-manifest persistence/linkage, exactly one active canonical name per entity under concurrent different-name reservations, direct-insert bypass prevention and the exact two-root `Saltwater` exception. Disposable SQL acceptance covers the root pair, third-entity/alias rejection, geography rename history, person full-name enforcement and rename identity continuity. PostgreSQL concurrency tests race same-name and distinct-name reservations, test idempotency and transaction rollback. Backup/restore assertions now include reservation and name-event counts. The SW-NAM-001 27-group bounded acceptance suite passed in run `45409845359`, including concurrency, rollback, 10,000-person capacity, access controls and backup/restore. Final manifest-version verification also passed in run `45410340222`; a storage-only rerun is capturing heap/index/TOAST detail. All fixtures use disposable PostgreSQL and do not write Neon.

## 22. Completion status

- Specification: DESIGNED_DRAFT; review/approval pending.
- Implementation: Bounded SW-NAM-001 naming acceptance suite and CI integration implemented; the wider BP-43 programme remains incomplete.
- Test execution: SW-NAM-001 bounded tests passed in run `45409845359`; remaining BP-43 acceptance criteria are not executed evidence.
- Verification: Bounded SW-NAM-001 verification passed; BP-43 overall remains incomplete.
- Neon writes, migrations, seed/import, bulk operations, uploads or production deployments: none performed or authorised.
- Next division: BP-44 — Configuration and Change Control.