# BP-39 — Persistence and Recovery

**Project:** Saltwater  
**Division:** BP-39 of the fixed 44-division master structure  
**Version:** 1.0  
**Specification status:** DESIGNED_DRAFT — review/approval pending  
**Implementation / test execution / verification:** NOT_STARTED  
**Authority:** Fixed Saltwater BP-01–BP-44 blueprint, unchanged 52-division source and current 52→44 crosswalk.  
**Database:** Neon PostgreSQL is the intended persistent database; GitHub holds source-control, specifications and migration history.  
**Write restriction:** This specification authorises no Neon write, migration, backup configuration change, export, restore, seed, import or bulk operation.

## 1. Purpose

BP-39 defines durable persistence, backup, checkpointing, restore, recovery, disaster recovery, recovery testing and integrity evidence for Saltwater. It ensures that the living simulation can survive data loss, corruption, failed changes, operator error and service interruption without losing its authoritative records, hidden state, chronology, provenance or continuity.

BP-39 owns the **operational lifecycle of recoverable copies and the process by which a known-good state is restored and validated**. BP-38 owns schemas, constraints and database integrity. BP-35 owns simulation execution. BP-37 owns canonical time. BP-43 owns test strategy/evidence governance. BP-44 owns release and change approval. Domain divisions remain responsible for validating the meaning and lifecycle correctness of their own records after recovery.

## 2. Scope and exclusions

### Included
- Backup policy, coverage, schedules, retention and recovery-point planning.
- Consistent checkpoints and manifests.
- Backup isolation, integrity, encryption and access.
- Restore selection, isolation, execution and validation.
- Point-in-time recovery where supported and verified.
- Disaster recovery scenarios, incident procedures and communications.
- Recovery testing, measured RPO/RTO and reproducible evidence.
- Event replay/reconstruction handoff and idempotency protections.
- Environment separation, provider constraints, operational monitoring and cost/capacity.
- Recovery audit, status and cross-division handoffs.

### Excluded
- Database schema and transaction ownership (BP-38).
- Domain record meaning and business lifecycle (owning domain).
- Runtime simulation/event execution (BP-35).
- Canonical time/calendar/scheduling semantics (BP-37).
- Security policy/classification ownership (BP-42).
- Independent test strategy and acceptance evidence governance (BP-43).
- Canon, release, migration and change approval authority (BP-44).
- User interface and notification/report ownership (BP-40/BP-41).

## 3. Binding Saltwater canon

1. Saltwater is one fictional sovereign city-state, one playable city, one jurisdiction. External places are off-map references only.
2. Maximum living population is 10,000, counted exactly once. Recovery must not create duplicate people or breach the cap.
3. At least 10,000 businesses must remain represented by canonical BP-04 records.
4. Police is the deepest simulation; other records remain sufficiently detailed to support it.
5. Text is the permanent primary interface; graphics are optional.
6. No simulation time or NPC/world activity advances while the player is absent or the game is paused.
7. Case-relevant people promoted to full persistent records are never downgraded.
8. Hidden offender/accomplice truth is not revealed unless the player types exactly `bingo`. Recovery tools, logs, manifests, test reports, exports and player-facing views must preserve this boundary.
9. No unsolicited investigation hints or forced player decisions.
10. Preserve every record's meaning, uncertainty, source, chronology, relationship and correction lineage. Storage efficiency cannot destroy meaning.
11. Recovery must preserve canon and player agency; restore success cannot be declared merely because the database starts.
12. No Neon mutation without the user's explicit approval after a measured baseline, incremental size estimate, projected total, assumptions and uncertainty are shown. Actual growth must be measured after an approved write.

## 4. Ownership and authority

| Concern | Owner | BP-39 responsibility |
|---|---|---|
| Canon and governing rules | BP-01 | Preserve approved canon in recovery and prevent restore from silently changing it |
| Population and person identity | BP-03 | Preserve unique population state and validate 10k cap |
| Businesses/property | BP-04 | Preserve canonical business identities and 10k minimum |
| Domain schemas/constraints/transactions | BP-38 | Restore database under BP-38 schema and integrity contracts |
| Simulation execution | BP-35 | Preserve runtime state/event sequence; do not execute simulation |
| Time/scheduling | BP-37 | Preserve canonical time and event chronology |
| Security policy | BP-42 | Enforce access, encryption and protected-data rules |
| Test strategy/evidence | BP-43 | Supply independent recovery test requirements and evidence governance |
| Configuration/change/release | BP-44 | Approve configuration, migration, restore promotion and controlled change |
| Domain facts and lifecycle | Each owning BP | Validate restored domain meaning and invariants |

A restored database is not automatically a valid simulation. Technical restore, schema integrity, domain integrity, access control, runtime consistency and player-facing safety are separate validation gates.

## 5. Recovery objectives and policy model

For each data class and service, policy must specify:
- Recovery Point Objective (RPO): maximum acceptable data-loss interval.
- Recovery Time Objective (RTO): maximum acceptable time to restore usable service.
- Backup frequency and retention.
- Required consistency boundary and point-in-time granularity.
- Permitted restore methods.
- Required validation and evidence.
- Responsible operator/authority and escalation route.

No RPO/RTO numeric value is invented in this draft. Values remain explicit fictional/technical configuration decisions and must be approved before implementation. Different classes may have different objectives, but critical game canon, source evidence, person identity, case records and audit history require stronger protection than rebuildable caches.

## 6. Backup coverage and classification

Classify persisted data into:
1. Canonical authoritative records.
2. Immutable source material and evidence.
3. Append-only event and audit history.
4. Current domain state and runtime checkpoint.
5. Schema/migration/configuration metadata.
6. Derived projections, search indexes and caches.
7. Operational telemetry and temporary work queues.
8. Secrets and provider-managed credentials, which are handled through the approved secret-management mechanism and are not copied into ordinary database exports.

For every class declare whether it is included in full backup, point-in-time recovery, independent export, rebuildable projection or separately managed configuration backup. Any exclusion must name an owner, reason and tested reconstruction path.

## 7. Backup schedules, retention and rotation

Backup cadence, retention, rotation and off-site/independent copy strategy are explicit per environment and data class. Do not assume provider defaults are sufficient. Verify actual Neon plan and feature availability before depending on a retention window, PITR or export mechanism.

Backup jobs must record scope, source project/branch/database, schema version, checkpoint, start/end, result, integrity evidence and tool version. Missed or failed jobs are observable and remain unresolved until a verified backup is produced. Retention pruning must never remove the only usable recovery point or violate approved RPO/RTO.

## 8. Consistent checkpoints and manifests

A checkpoint must correspond to a consistent transaction boundary. It includes the canonical schema/migration version and, where available, BP-35 event sequence and BP-37 simulation-time position. Database wall-clock creation time and in-game simulation time are separate fields.

A manifest records:
- Unique checkpoint ID.
- Project, branch, database and environment.
- Backup method, scope and consistency boundary.
- Creation time and source state/version.
- Schema and migration identifiers.
- Simulation clock and event sequence if available.
- Integrity/checksum/provider metadata.
- Backup object references and completion status.
- Actor/service identity and approval reference.
- Limitations, exclusions and validation status.

Backup operations must not advance game time, trigger NPC decisions or mutate authoritative game records.

## 9. Isolation, integrity and security

Recoverable copies are isolated from ordinary live application write credentials. Where supported, use immutable, protected or separately permissioned copies so a compromised application credential cannot erase all recovery points. Encrypt in transit and at rest using supported provider capabilities. Backup access, export and restore permissions are distinct and least-privileged.

Integrity metadata detects incomplete, altered or corrupted copies. Backup transfer must be verified before marking the object usable. Credentials and encryption secrets never enter GitHub, game records, manifests, logs or user-facing output. BP-42 owns policy; BP-39 implements it for recovery operations.

## 10. Restore selection and execution

Restore begins with an identified incident, scope, affected environment, desired checkpoint, authorised decision and target. Available checkpoints are listed with timestamps, source state, schema, integrity and scope. Selection records expected loss interval and why the checkpoint is suitable.

Restore targets are isolated from the live authoritative environment until validation passes. Source and destination project/branch/database must be confirmed to prevent accidental overwrite. Restore methods may include full restore, provider-supported PITR, isolated branch clone or selective reconstruction. Selective restore is prohibited if it breaks cross-domain transactions, source provenance or domain invariants.

Each execution records operator, authority, incident, checkpoint, target, steps, tools, timestamps, errors, outcome and evidence. A failed restore must leave the live authoritative source in a known state and must not be marked successful.

## 11. Mandatory post-restore validation

Validation is layered and all required layers must pass:
1. **Technical:** database starts, expected schema and migrations exist, constraints are active.
2. **Structural:** primary/foreign keys, uniqueness, typed references and transaction invariants reconcile.
3. **Canon:** city identity, one-city boundary, 10k living-person cap, 10k business minimum and fixed division structure remain intact.
4. **Domain:** owning divisions validate their state, lifecycle and cross-record meaning.
5. **Historical:** source originals, immutable evidence, event order, provenance and correction lineage survive.
6. **Temporal:** simulation time and event sequence are consistent; no offline progression has occurred.
7. **Security:** access roles, protected data, hidden-truth firewall, exports and derived views remain restricted.
8. **Runtime:** outbox, queues, idempotency keys and pending work cannot create duplicate actions.
9. **Interface:** player-facing text and reports show only authorised, validated records.
10. **Evidence:** checksums, test results, operator, source checkpoint and exact software/schema versions are recorded.

Any required failure blocks promotion to authoritative service. A database accepting connections is not sufficient evidence.

## 12. Disaster recovery scenarios

At minimum, plan and test:
- Accidental deletion or overwrite.
- Corrupted rows, indexes, schema or database.
- Failed or partially applied migration.
- Provider outage or region/service interruption.
- Compromised credentials or unauthorised destructive access.
- Application defect writing invalid state.
- Lost or corrupted backup object.
- Inconsistent event/outbox or duplicated side effects.
- Operator error selecting wrong project, branch or checkpoint.
- Environment contamination between development, test and production.

Each scenario defines detection, containment, authority, recovery method, validation, communications and closure criteria. Preserve affected sources for diagnosis when safe. Do not overwrite the only good recovery copy. State confirmed facts separately from estimates and unknowns.

## 13. Event replay and reconstruction

BP-35 owns execution semantics. BP-39 preserves checkpoints and recovery inputs and coordinates a controlled handoff for replay. Replay must use immutable events, stable IDs, deterministic sequence metadata and domain-approved idempotency. It cannot infer lost source truth from summaries or create duplicate people, cases, exhibits, postings or external side effects.

Replay preserves occurred/effective/observed/recorded/committed times and BP-37 canonical simulation time. It cannot progress the game while paused or absent. Hidden offender truth remains inaccessible through player-facing outputs unless the exact `bingo` gate is satisfied.

## 14. Preservation of source and domain meaning

Recovery preserves original evidence, interview recordings/statements, surveillance source material, intelligence source boundaries, forensic results, case chronology, legal orders, financial postings, personnel histories and all other domain-owned records in their native semantic distinction.

Summaries, redactions, transcriptions, visualisations and derived products remain linked to originals and transformation metadata. A source is not reconstructed from a derivative when the source is missing. Missing source material is recorded as loss, not concealed by regenerated text.

## 15. Environment separation

Development, test and production environments use separate identities, credentials and data boundaries. Test fixtures are labelled and cannot be mistaken for authoritative records. Production data is not copied into test environments without approved minimisation and access controls. Restoring to a non-production target cannot write back to production.

Promotion of a recovered target to authoritative use requires BP-44 change/release authority after technical, domain, security and player-facing validation.

## 16. Recovery testing and evidence

A backup is not proven usable until a restore has been performed and validated. Recovery tests use isolated targets and identify exact source checkpoint, target, schema, migration set, software version, operator and test evidence.

Tests include representative canonical people, businesses, cases, evidence, long narrative, source media metadata, event histories, financial/resource invariants, permissions, hidden-truth protection and time-freeze semantics. Measure actual recovery time and data-loss interval against approved objectives. Failed tests create remediation and cannot be reported as passed.

Re-test after material changes to schema, provider, retention, backup method, access control or recovery scripts. BP-43 owns test strategy and acceptance evidence; BP-39 owns the operational recovery procedure and execution record.

## 17. Monitoring and operational maintenance

Monitor backup job success, age of newest verified checkpoint, backup size/growth, retention coverage, integrity failures, restore-test age, RPO/RTO compliance, restore duration, provider availability, recovery incidents and unresolved remediation.

Operational status distinguishes healthy, degraded, failed, stale and recovering. Maintenance scripts are versioned, bounded, auditable and secret-free. Logs retain diagnostic value while redacting credentials and protected personal data. Monitoring and backup jobs do not advance simulation time.

## 18. Storage, provider and cost constraints

Measure backup size and growth. Benchmark long high-entropy narrative and evidence metadata; do not assume compression. Avoid unnecessary full duplicate copies when supported incremental/PITR options satisfy approved objectives, but never trade away independent recoverability.

Provider plan, retention, PITR, export and restore capabilities must be checked against current actual service configuration before use. Cost and storage impacts of new retention/backup settings are estimated before material commitments. Preserve at least one verified recovery path at all times. Cleanup is blocked if it would remove the last suitable checkpoint.

## 19. Permissions and audit

Backup creation, listing, download/export, restore, promotion and deletion have separate permissions. Every action records actor/service identity, time, purpose, authority, target, source and result. Emergency overrides are time-bounded, logged and reviewed. Backup logs do not expose hidden truth, sensitive case details or secrets.

## 20. Interfaces and dependencies

- **BP-38:** schema, constraints, transaction integrity, canonical record contracts.
- **BP-35:** runtime events, causation, replay semantics and checkpoint handoff.
- **BP-37:** canonical time, calendar and event chronology.
- **BP-42:** security classifications, permissions, secrets and protected information.
- **BP-43:** test strategy, recovery acceptance and reproducible evidence.
- **BP-44:** approved changes, configuration, migration/release control and restore promotion.
- **BP-03/BP-04:** population and business registry validation.
- **All domain owners:** validate restored domain facts, lifecycle and cross-domain invariants.
- **BP-40/BP-41:** authorised text-first recovery status and reporting.

## 21. Acceptance tests

These 120 criteria define required BP-39 acceptance coverage. They are design criteria only; none is claimed executed.

- REC-AT-001: An approved backup policy defines covered databases, branches, schemas, records, files, metadata and configuration required to reconstruct the authoritative game.
- REC-AT-002: Backup scope includes canonical records, immutable source records, append-only histories, event records, domain state and required schema/migration metadata.
- REC-AT-003: Derived caches and rebuildable projections are classified separately from authoritative source data.
- REC-AT-004: Every excluded data class has an explicit rationale, owner and documented reconstruction path.
- REC-AT-005: Backup policy covers the single Saltwater city-state and does not create external playable geography.
- REC-AT-006: Backup scope preserves the complete 10,000-person population ledger and supports at least 10,000 businesses.
- REC-AT-007: Backup scope preserves the permanent promotion of materially case-relevant people and never downgrades them.
- REC-AT-008: Backup scope preserves evidence, case chronology, source originals, provenance and correction lineage.
- REC-AT-009: Backup scope preserves hidden offender truth securely without exposing it to player-facing recovery reports.
- REC-AT-010: Policy changes are versioned, approved and attributable.
- REC-AT-011: Backup schedules are defined for each data class and deployment environment.
- REC-AT-012: Backup cadence is configurable and documented rather than silently assumed.
- REC-AT-013: Retention periods and rotation rules are explicit, versioned and tested.
- REC-AT-014: Recovery point objectives are explicitly selected for each data class and approved before implementation.
- REC-AT-015: Recovery time objectives are explicitly selected for each service/data class and approved before implementation.
- REC-AT-016: Point-in-time recovery capability is used only when supported by the selected Neon plan/configuration and verified in practice.
- REC-AT-017: Backup frequency and retention are sufficient for the approved recovery-point objective.
- REC-AT-018: Scheduled backup jobs record start, completion, scope, result and integrity metadata.
- REC-AT-019: Missed or failed backup jobs trigger attributable alerts and remain unresolved until verified.
- REC-AT-020: Backup schedule changes do not silently shorten retention or create a recovery gap.
- REC-AT-021: Backups are logically and access-control separated from the live mutable database.
- REC-AT-022: Where feasible, recovery copies are protected against deletion or modification by the same credentials that operate the live database.
- REC-AT-023: Backup objects are encrypted in transit and at rest using supported provider mechanisms.
- REC-AT-024: Backup access follows least privilege and is independently auditable.
- REC-AT-025: Backup credentials and encryption secrets are not committed to GitHub or stored in simulation records.
- REC-AT-026: Backup manifests include source project, branch, database, schema version and checkpoint identity.
- REC-AT-027: Backup manifests include creation time, source consistency boundary and tool/method version.
- REC-AT-028: Checksums or provider integrity metadata detect incomplete or corrupted backup objects.
- REC-AT-029: Backup transfer completion is verified before a backup is marked usable.
- REC-AT-030: An isolated backup copy cannot be overwritten by an ordinary application transaction.
- REC-AT-031: Backups represent a transactionally consistent database point or an explicitly documented consistent snapshot boundary.
- REC-AT-032: Checkpoint creation captures the exact source commit/schema migration state corresponding to the data.
- REC-AT-033: Checkpoint metadata records simulation clock position and canonical event sequence where available.
- REC-AT-034: Checkpoint metadata distinguishes database wall-clock creation time from in-game simulation time.
- REC-AT-035: Cross-domain transactions are not split across inconsistent backup snapshots.
- REC-AT-036: Outbox/event records and associated domain state are captured consistently.
- REC-AT-037: Immutable evidence and source records are included without transformation.
- REC-AT-038: Checkpoint identifiers are stable and uniquely resolvable.
- REC-AT-039: Backup jobs do not advance Saltwater simulation time or trigger NPC activity.
- REC-AT-040: Backup creation is safe while simulation is paused and does not alter game canon.
- REC-AT-041: Restore procedures identify the incident, affected environment, desired checkpoint and authorised decision-maker.
- REC-AT-042: Available checkpoints can be listed with timestamps, schema versions, integrity status and scope.
- REC-AT-043: Restore selection records why a checkpoint is suitable and what data may be lost after it.
- REC-AT-044: Recovery selection distinguishes full restore, point-in-time restore, branch clone and selective reconstruction.
- REC-AT-045: Selective restore is prohibited where it would break cross-domain invariants or source provenance.
- REC-AT-046: Recovery target is isolated from live production until validation succeeds.
- REC-AT-047: Restore destination and source project/branch/database are confirmed before mutation.
- REC-AT-048: Restore procedures prevent accidental overwriting of the only good live copy.
- REC-AT-049: Restore actions require explicit operator authority and a documented change record.
- REC-AT-050: Recovery cannot silently change canon, population cap, city boundaries or division structure.
- REC-AT-051: Restore recreates the chosen checkpoint using a documented reproducible procedure.
- REC-AT-052: Restore execution records each step, tool version, start/end time and outcome.
- REC-AT-053: Restore failure leaves the live authoritative database in a known state.
- REC-AT-054: Restore verification checks schema version and migration history.
- REC-AT-055: Restore verification checks primary keys, unique constraints and foreign-key integrity.
- REC-AT-056: Restore verification checks population count and the 10,000-person hard cap.
- REC-AT-057: Restore verification checks the 10,000-business minimum and canonical business identities.
- REC-AT-058: Restore verification checks case, incident, person, exhibit and source-record references.
- REC-AT-059: Restore verification checks append-only histories, source originals and correction lineage.
- REC-AT-060: Restore verification checks event sequence and time metadata for consistency.
- REC-AT-061: Restore verification checks domain lifecycle invariants supplied by BP-03 and all owning divisions.
- REC-AT-062: Restore verification checks hidden-truth access boundaries and player-facing views.
- REC-AT-063: Restore verification checks security roles, permissions and row-level access controls.
- REC-AT-064: Restore verification checks outbox/queue consistency and prevents duplicate side effects.
- REC-AT-065: Restore verification checks data checksums or equivalent integrity evidence.
- REC-AT-066: Restore validation failures block promotion of the restored target to authoritative service.
- REC-AT-061: A recovery test is performed against an isolated target, not by experimenting on the only live copy.
- REC-AT-062: Each restore test identifies the source checkpoint and exact target environment.
- REC-AT-063: Restore tests exercise a complete checkpoint rather than only verifying that a backup file exists.
- REC-AT-064: Recovery tests include schema/migration compatibility checks.
- REC-AT-065: Recovery tests include representative person, business, case, evidence and long narrative records.
- REC-AT-066: Recovery tests include high-entropy long text and source payloads to detect truncation or encoding loss.
- REC-AT-067: Recovery tests include concurrent transaction boundary and event/outbox consistency checks.
- REC-AT-068: Recovery tests verify provenance, source lineage, corrections and historical versions after restore.
- REC-AT-069: Recovery tests verify permissions, protected records and hidden-truth isolation after restore.
- REC-AT-070: Recovery tests measure actual recovery time and compare it with the approved objective.
- REC-AT-071: Recovery tests measure actual data-loss interval and compare it with the approved objective.
- REC-AT-072: Recovery test results include reproducible logs, checksums, timestamps and operator identity.
- REC-AT-073: Failed recovery tests create remediation actions and cannot be reported as successful.
- REC-AT-074: Restore tests are repeated after material schema, provider, retention or backup-process changes.
- REC-AT-075: Successful restore evidence is linked to the exact checkpoint, migration set and test run.
- REC-AT-071: Disaster scenarios include accidental deletion, corruption, failed migration, credential compromise, provider outage and operator error.
- REC-AT-072: Each scenario defines detection, containment, decision authority, recovery path and validation criteria.
- REC-AT-073: Provider outage handling distinguishes service unavailability from data corruption or credential failure.
- REC-AT-074: Credential compromise triggers controlled credential rotation and review of backup access.
- REC-AT-075: Corruption response preserves the affected source for diagnosis where safe and avoids overwriting recovery copies.
- REC-AT-076: Failed migration recovery uses the migration-specific forward-repair or rollback plan.
- REC-AT-077: Recovery from accidental deletion uses the nearest verified suitable checkpoint and documents lost transactions.
- REC-AT-078: Disaster recovery roles and escalation paths are documented and tested.
- REC-AT-079: Communication during recovery distinguishes confirmed facts, estimates and unresolved uncertainty.
- REC-AT-080: Recovery is not declared complete until data integrity and application-level validation pass.
- REC-AT-081: Event replay is performed only under BP-35 and domain-owned replay contracts.
- REC-AT-082: Replay uses immutable source events and deterministic sequence metadata.
- REC-AT-083: Replay never creates duplicate cases, people, exhibits, financial postings or external side effects.
- REC-AT-084: Non-idempotent events are guarded by stable event IDs and deduplication records.
- REC-AT-085: Replayed projections are compared with checkpointed projections where comparison is meaningful.
- REC-AT-086: Replay does not infer missing source truth from summaries or narrative guesses.
- REC-AT-087: Replay preserves occurred, effective, observed, recorded and committed timestamps.
- REC-AT-088: Replay cannot advance simulation time while the player is absent or simulation is paused.
- REC-AT-089: Replay respects the exact bingo hidden-truth access gate.
- REC-AT-090: Replay results record source range, software version, transformations and validation outcome.
- REC-AT-091: Recovery preserves original source payloads without lossy conversion.
- REC-AT-092: Recovery preserves evidence identity and chain-of-custody history under BP-23.
- REC-AT-093: Recovery preserves original interviews, recordings, transcripts and adopted statements as distinct records.
- REC-AT-094: Recovery preserves surveillance originals, collection metadata and derivative links.
- REC-AT-095: Recovery preserves intelligence source separation and access restrictions.
- REC-AT-096: Recovery preserves case and investigative chronology without converting allegation to fact.
- REC-AT-097: Recovery preserves effective dates, record dates and source timezone/uncertainty.
- REC-AT-098: Recovery preserves superseded values and additive correction history.
- REC-AT-099: Recovery preserves retired/merged identity redirects and historical references.
- REC-AT-100: Any detected data loss is explicitly scoped, recorded and never hidden by a regenerated summary.
- REC-AT-101: Development, test and production data are isolated by environment and credentials.
- REC-AT-102: Test fixtures cannot be mistaken for authoritative Saltwater records.
- REC-AT-103: Production records are not copied to development/test without approved minimisation and access controls.
- REC-AT-104: Restores into development/test environments cannot write back to production.
- REC-AT-105: Environment identifiers are included in backup manifests and recovery logs.
- REC-AT-106: Promotion of a restored target requires explicit release/change authority under BP-44.
- REC-AT-107: Operational scripts are versioned and reviewed in GitHub.
- REC-AT-108: Recovery scripts do not embed secrets or rely on undocumented local state.
- REC-AT-109: Database and backup monitoring report healthy, degraded, failed and recovering states distinctly.
- REC-AT-110: Recovery operations remain text-first and do not require optional graphical interfaces.
- REC-AT-111: Backup storage and retention costs are estimated before enabling material new backup scope.
- REC-AT-112: Backup size and growth are measured from representative data rather than guessed.
- REC-AT-113: Backup compression is evaluated without altering source meaning or provenance.
- REC-AT-114: Duplicate full backups are avoided where safe incremental/PITR capabilities meet approved objectives.
- REC-AT-115: Provider-specific limits, retention and restore capabilities are verified rather than assumed.
- REC-AT-116: Neon plan changes or feature availability are not presumed; current capability is checked before reliance.
- REC-AT-117: Backup export format is documented and can be interpreted independently of transient application state.
- REC-AT-118: Storage cleanup never deletes the only verified recovery point.
- REC-AT-119: Retention pruning verifies that remaining restore points still meet approved recovery objectives.
- REC-AT-120: Recovery cost and capacity changes are recorded for user review before material commitments.
- REC-AT-121: Every backup and restore action has an actor/service identity, timestamp, purpose and result.
- REC-AT-122: Backup read/export privileges are separate from live database write privileges.
- REC-AT-123: Restore privilege is restricted to designated roles and separately audited.
- REC-AT-124: Emergency override is attributable, time-bounded and reviewed after use.
- REC-AT-125: Backup and restore logs redact secrets and protected personal content.
- REC-AT-126: Recovery evidence is retained for the configured audit period.
- REC-AT-127: Design, implementation, testing and verification statuses are reported separately.
- REC-AT-128: A documented backup policy is not evidence that a backup job is deployed or working.
- REC-AT-129: A backup file existing is not evidence of a successful restore.
- REC-AT-130: A successful test restore is not evidence of production recovery objectives unless measured under representative conditions.
- REC-AT-131: BP-38 owns schemas, constraints and database transaction integrity; BP-39 owns backup, restore and recovery execution.
- REC-AT-132: BP-35 owns runtime event execution; BP-39 preserves checkpoints and recovery evidence without executing simulation events.
- REC-AT-133: BP-37 owns canonical time semantics; BP-39 preserves simulation-time and sequence metadata faithfully.
- REC-AT-134: BP-43 owns recovery test strategy and independent test evidence; BP-39 provides procedures and execution records.
- REC-AT-135: BP-44 governs approved configuration, migrations, deployment and recovery promotion decisions.
- REC-AT-136: BP-42 owns security policy; BP-39 applies approved access restrictions to backup and restore operations.
- REC-AT-137: Domain owners validate restored business meaning and lifecycle invariants for their records.
- REC-AT-138: BP-40/BP-41 display recovery status only through authorised and appropriately redacted interfaces.
- REC-AT-139: Recovery handoff contracts identify source, target, checkpoint, schema, authority, validation and outcome.
- REC-AT-140: Recovery cannot relax population, business, player-agency, pause or hidden-truth canon.

## 22. Source traceability

The following source requirements and tests are mapped to BP-39 by the current authoritative crosswalk. Source wording is reproduced; the original JSON remains authoritative.

| Source ID | Source division | Original requirement/test wording |
|---|---|---|
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
| S49.R01 | Backups, recovery and data integrity | Define backup cadence, retention, restore testing, point-in-time recovery where available, export format and disaster recovery procedure. |
| S49.R02 | Backups, recovery and data integrity | Protect canon and authoritative records against corruption, accidental overwrite and partial writes. |
| S49.R03 | Backups, recovery and data integrity | Keep recoverable backups separate from live mutable state. |
| S49.T01 | Backups, recovery and data integrity | A tested restore reproduces a verified checkpoint. |
| S51.R01 | Operations, observability and maintenance | Track service health, errors, latency, job queues, resource use, database size, failed events and recovery actions. |
| S51.R02 | Operations, observability and maintenance | Provide safe maintenance, migration, rollback and incident procedures. |
| S51.R03 | Operations, observability and maintenance | Separate development/test data from authoritative simulation data. |
| S51.T01 | Operations, observability and maintenance | Operational failures are detectable, attributable and recoverable. |

### Cross-cutting and governance traceability

| X01 | Stable identity and provenance across every domain; domain owners create records while shared registries enforce canonical identity. | BP-01,BP-03,BP-04,BP-05,BP-06,BP-12,BP-15,BP-23,BP-35,BP-38,BP-39,BP-44 |
| X03 | All time-dependent facts are effective-dated and historically queryable; all domain divisions must comply with the shared clock contract. | BP-01,BP-02,BP-03,BP-04,BP-05,BP-08,BP-10,BP-11,BP-12,BP-15,BP-16,BP-19,BP-20,BP-22,BP-23,BP-25,BP-26,BP-27,BP-28,BP-29,BP-33,BP-35,BP-37,BP-38,BP-39,BP-43 |
| X06 | Preserve originals; derived summaries never replace source records; corrections are additive, attributed and historically traceable. | BP-01,BP-12,BP-15,BP-16,BP-19,BP-20,BP-21,BP-22,BP-23,BP-24,BP-27,BP-28,BP-31,BP-38,BP-39,BP-43 |
| X07 | No hidden simulation time while player is out; pause/resume and deliberate time advancement are explicit. | BP-01,BP-35,BP-37,BP-38,BP-39,BP-40,BP-43 |
| X10 | No design/implementation/test/verification status is asserted without the corresponding approval, artefact, passing test and reproducible evidence. | BP-01,BP-38,BP-39,BP-43,BP-44 |
| A10 | Database architecture requirement omitted ChatGPT interface and connectivity/quality verification. | Expanded S46.R01. | BP-38 owns data; BP-39 persistence; BP-40 interface; BP-43 tests; BP-44 source/version governance. |

**Traceability count:** 21 distinct source requirement/test IDs mapped to BP-39. Cross-cutting rules are listed separately. This establishes mapping and incorporation targets, not implementation or test completion.

## 23. Open design/configuration decisions

1. Approved RPO/RTO values by data class and environment.
2. Actual Neon plan/branch topology and verified PITR/backup/export capabilities.
3. Backup cadence, retention, rotation and independent-copy policy.
4. Exact checkpoint consistency mechanism and BP-35 event-sequence handoff.
5. Backup manifest schema, checksum and integrity-verification method.
6. Backup encryption and secret-management mechanism.
7. Separate backup/export/restore/promotion roles and BP-42 permission matrix.
8. Full restore versus PITR/branch-clone runbooks for each failure class.
9. Restore isolation and final promotion criteria.
10. Domain-level post-restore validation owners and exact invariants.
11. Recovery-test frequency, corpus and evidence format with BP-43.
12. Provider outage and credential compromise procedures.
13. Recovery log retention and protected-data redaction.
14. Backup storage sizing, cost and growth alert thresholds.
15. Environment topology and production-data minimisation.
16. Retention pruning safeguards and minimum protected checkpoint count.
17. Recovery communication and escalation roles.
18. Approved numeric thresholds for stale backups and recovery degradation.

No decision here authorises a provider change, database write, backup export or restore.

## 24. Completion status

- Specification: DESIGNED_DRAFT; review/approval pending.
- Implementation: NOT_STARTED.
- Test execution: NOT_STARTED; acceptance criteria are not executed evidence.
- Verification: NOT_STARTED.
- Live backup configuration: not newly inspected or changed.
- Live restore capability: not newly tested; no capability claim is made.
- Neon writes/restores: none performed or authorised.
- Next division: BP-40 — Interface.
