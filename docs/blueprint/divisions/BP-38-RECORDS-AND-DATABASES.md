# BP-38 — Records and Databases

**Project:** Saltwater  
**Division:** BP-38 of the fixed 44-division master structure  
**Version:** 1.0  
**Specification status:** DESIGNED_DRAFT — review/approval pending  
**Implementation / test execution / verification:** NOT_STARTED  
**Authoritative source:** Fixed Saltwater BP-01–BP-44 blueprint, unchanged 52-division source and current 52→44 crosswalk.  
**Database authority:** Neon PostgreSQL is the intended persistent game database; GitHub is the source-control and schema/migration history authority; ChatGPT is the user-facing AI partner/interface.  
**Write restriction:** This document authorises no Neon connection change, schema creation, migration, seed, import, upload, bulk write or other database mutation.

## 1. Purpose

BP-38 defines Saltwater's canonical data architecture and database integrity layer: record standards, schemas, identity references, constraints, relationships, lifecycle enforcement, transaction boundaries, immutable source history, versioning, provenance, correction lineage, query contracts, indexes, storage design, migration discipline, connectivity contracts and data-level observability.

BP-38 makes the simulation's records coherent across every domain. It prevents duplicate identity, conflicting sources of truth, invalid state transitions, broken references, partial population/finance/inventory changes, lost source material, untraceable corrections and storage designs that compress away meaning.

BP-38 owns **how authoritative records are represented, constrained, related, queried and safely changed in the database**. It does not take over the business meaning or lifecycle authority of police, population, business, evidence, legal, finance or other domain records. Each domain remains the authoritative owner of its own facts and rules.

## 2. Scope and exclusions

### Included
- Canonical entity registry patterns, stable IDs and typed references.
- Relational schema conventions, keys, constraints and cardinality.
- Domain-owned record contracts and shared data dictionaries.
- Record lifecycle/state integrity and atomic transactions.
- Provenance, versions, immutable originals and additive corrections.
- Event/source record storage and derived read models.
- Query, search, pagination, export and reporting data contracts.
- Normalisation, deduplication, compression, indexes, partitioning and measured capacity.
- Schema migration/versioning and schema-drift controls.
- Neon connectivity, GitHub migration history and ChatGPT application contracts.
- Data-layer access enforcement interfaces and safe diagnostics.
- Database observability, operational maintenance and measurable storage growth.
- Schema-level test fixtures, invariants and evidence interfaces.

### Excluded
- Domain truth and domain-specific business decisions.
- Canonical person identity/population authority (BP-03).
- Canonical business/property identity and business lifecycle (BP-04).
- Police hierarchy, personnel and operational authority (BP-05–BP-12).
- Crime truth/generation, cases, investigation, roles, evidence and forensics (BP-13–BP-24).
- Arrest, custody, legal, courts and corrections authority (BP-25–BP-29).
- Institutional, professional standards, training, HR and finance rules (BP-30–BP-34).
- Runtime event execution and causal simulation (BP-35).
- Relationship meaning (BP-36), canonical time/schedule semantics (BP-37).
- Backup/restore/disaster recovery execution (BP-39).
- User interface ownership (BP-40), reporting/notification ownership (BP-41), security policy ownership (BP-42), test strategy ownership (BP-43), canon/change approval ownership (BP-44).

## 3. Binding Saltwater canon and priorities

1. Saltwater is one fictional sovereign city-state, one playable city, one jurisdiction. No external playable territory.
2. The living population hard cap is 10,000, counted exactly once across all roles. BP-03 owns the ledger; BP-38 enforces database constraints and transaction integrity supporting it.
3. The world contains at least 10,000 businesses. BP-04 owns the registry; database design must support the minimum without duplicating business identities.
4. Police is the deepest simulation; other domains are sufficiently detailed to support it.
5. Text is the permanent primary interface. Graphics and maps are optional and cannot become a prerequisite for record access or verification.
6. No simulation time or world activity advances while the player is outside the simulation. Persisted time and events obey BP-35/BP-37 pause semantics.
7. Materially case-relevant people are promoted permanently to full persistent status; they are never downgraded or erased.
8. Hidden offender/accomplice truth remains protected until the player types exactly `bingo`. Storage, search, exports, summaries, logs and views must not leak it.
9. No unsolicited investigation hints or forced player decisions.
10. Preserve meaning, narrative, relationships, provenance, uncertainty and history. Compress structure, never meaning.
11. Canon, player agency, simulation fidelity and continuity/integrity outrank storage minimisation; performance follows minimum lossless storage.
12. No Neon write without a measured baseline, an incremental size estimate and projected total with method/assumptions/uncertainty, followed by explicit user approval. Measure actual growth after an approved write.

## 4. Ownership and single-source-of-truth model

| Domain | Authoritative owner | BP-38 responsibility |
|---|---|---|
| Canon and governing rules | BP-01 | Persist versioned decisions and enforce approved schema constraints |
| Geography and spatial IDs | BP-02 | Typed references and referential integrity |
| Person identity/population | BP-03 | Support unique person registry, atomic cap enforcement and lifecycle consistency |
| Property/business/organisation | BP-04 | Support canonical registries and business minimum |
| Police architecture/personnel/career/deployment | BP-05–BP-08 | Store domain records without creating duplicate authority |
| Police resources/operations/dispatch/incidents | BP-09–BP-12 | Enforce data contracts and transactional consistency |
| Crime and case/investigation | BP-13–BP-16 | Preserve source, case and decision chronology |
| Victim/witness and suspect/offender roles | BP-17/BP-18 | Preserve separate role records linked to canonical persons |
| Interviews, surveillance, intelligence | BP-19–BP-21 | Preserve source originals, restrictions, provenance and versioned references |
| Scenes, exhibits and forensics | BP-22–BP-24 | Enforce source/evidence references and continuity contracts; BP-23 owns exhibit truth |
| Arrest, custody, legal, court, corrections | BP-25–BP-29 | Preserve separate procedural state and authoritative source orders |
| Department governance, standards, training, HR, finance | BP-30–BP-34 | Enforce attributable, auditable records and reconciliation |
| Simulation runtime | BP-35 | Persist validated events/state; do not execute simulation actions |
| Relationships/social context | BP-36 | Store canonical relationship references without defining their meaning |
| Time/scheduling | BP-37 | Store time-bearing records according to canonical clock/time semantics |
| Persistence/recovery | BP-39 | Provide durable data contract; BP-39 owns backup/restore and recovery execution |
| Interface and reports | BP-40/BP-41 | Supply safe, stable query contracts |
| Security policy | BP-42 | Enforce access policy at data boundary |
| Testing and evidence | BP-43 | Provide schema fixtures, constraints and testable invariants |
| Canon/change control | BP-44 | Enforce approved schema/version compatibility |

A domain record has one owner even when several divisions read or reference it. A shared view, index, cache, replica or report is never a second authoritative source. Cross-domain consumers reference canonical IDs and source versions.

## 5. Canonical record architecture

Every persisted record type must declare:
- Stable record ID and ID namespace.
- Owning domain and schema version.
- Entity type and canonical identity reference(s).
- Required fields, optional fields, types, units, nullability and cardinality.
- Lifecycle state and permitted transitions.
- Source/provenance and confidence/uncertainty where applicable.
- Occurred/effective/observed/recorded/committed timestamps as applicable.
- Actor, authority, reason and correlation/causation references for material changes.
- Sensitivity classification and access policy reference.
- Retention, correction, supersession and deletion constraints.
- Cross-domain dependencies and read/write ownership.

Records are classified as canonical entity records, domain-owned state records, immutable source records, append-only event/audit records, derived projections, caches, search indexes, export packages or operational telemetry. Their class determines mutation and retention rules.

## 6. Stable identity and reference integrity

IDs are stable, unique, opaque where appropriate and independent of mutable attributes such as name, address, rank, job, business ownership or case status. Human-readable numbers may be aliases, not primary identity.

References are typed. A person reference cannot resolve to a business; an exhibit reference cannot resolve to a generic attachment; a case reference cannot resolve to an incident without an explicit relation. Missing, retired, merged, split and inaccessible references have distinct handling.

Merges preserve source IDs and redirect history. Splits create new identities with explicit provenance and do not rewrite earlier records. Retired entities remain resolvable for historical records. Reuse of a retired identifier is prohibited.

## 7. Schema catalogue and domain contracts

Every schema object has a documented owner, purpose, source requirements, field dictionary, lifecycle, constraints, indexes, retention, sensitivity, consumers and migration history. Domain divisions publish contracts for commands, events, queries and state transitions.

Shared schema conventions include stable primary keys, typed foreign keys, explicit uniqueness, controlled enums, check constraints, temporal columns, provenance references and version metadata. Avoid generic untyped JSON blobs as a substitute for domain schemas. JSON/JSONB is suitable for bounded, versioned, genuinely variable payloads with validated structure; it must not weaken core relational invariants.

Domain owners define required fields and semantic constraints. BP-38 defines and enforces cross-domain structural integrity. Conflicting ownership or duplicate authority is a design blocker.

## 8. Lifecycle and state constraints

Every persisted record family has a state model. Allowed transitions, required actor/authority, required fields and side effects are declared by the domain owner. Database constraints enforce structural state validity; domain services enforce complex transition rules and authorisation.

Invalid transitions are rejected at the authoritative write boundary. A user interface hiding a button is not an integrity control. Terminal states remain historically queryable. Reopening, reinstatement, closure reversal and correction require explicit, attributed transitions. State updates use optimistic concurrency or equivalent version checks to prevent lost updates.

## 9. Provenance, versions and corrections

Original records and source content are preserved. A summary, transcript extract, analytical product, redacted copy, image derivative or report is a separate object linked to its source and transformation. It never replaces the source.

Material changes record actor, authority, reason, timestamp, changed fields, prior version and resulting version. Corrections append a superseding value or correction event; they do not silently overwrite the historical value. Effective time is distinct from record-created time.

Source types remain distinct: observed fact, reported claim, allegation, estimate, inference, intelligence, opinion, source statement, forensic interpretation and adjudicated finding. Conflicting sources may coexist. No generic database rule ranks one source as truth without domain authority and evidence.

## 10. Time and event history

All time-bearing records use BP-37's canonical simulation-time contract. Persisted records distinguish occurred, effective, observed, recorded, committed and external source time where applicable. Timezone, precision, uncertainty and source clock drift are retained.

Append-only events identify event type, schema version, actor/system, entity references, simulation sequence, causal parent, correlation ID, source, authority and payload. Events are not interchangeable with current state. Current state may be a projection derived from authoritative events and domain commands.

Replay is deterministic only where the owning domain and BP-35 specify deterministic semantics. Replay must not duplicate external side effects. Event order cannot be inferred from database insertion order alone.

## 11. Transactions and atomic reconciliation

A transaction boundary is declared for each operation that changes multiple related records. Population entries/deaths/exits, financial postings, inventory movement, staffing/deployment and resource-capacity changes must reconcile atomically where their owning contracts require it.

The transaction validates uniqueness, foreign keys, lifecycle, capacity and domain preconditions before commit. A failed operation leaves no partial mutation. Concurrency controls prevent two individually valid transactions from jointly violating a cap, balance, exclusive assignment or other invariant.

Use serializable transactions, explicit locks, exclusion constraints, optimistic versions or other justified controls according to the invariant. Retries are bounded and safe only for idempotent commands. External notifications and asynchronous work use a transactional outbox or equivalent mechanism so committed state cannot be separated from its required handoff.

## 12. Immutable sources, evidence and case records

BP-38 enforces storage patterns that preserve source originals and provenance, while domain owners control source meaning:
- BP-22 owns crime-scene control and original scene observations.
- BP-23 owns exhibit identity, evidential custody and continuity.
- BP-24 owns forensic examination methods, results and interpretation.
- BP-19 owns interview process and original interview records.
- BP-20 owns surveillance source/collection records.
- BP-21 owns intelligence lifecycle and analytical products.
- BP-15 owns case identity/lifecycle; BP-16 owns investigative actions and decisions.
- BP-17/BP-18 own procedural participant roles, not canonical person identity.

A source object and a registered evidential copy are distinguishable and linked. Redaction, conversion, transcription, enhancement, OCR, summarisation and visualisation create derivatives with source reference, tool/method version, actor, time and integrity metadata. No derivative silently replaces the source.

## 13. Query, search and read-model contracts

Every query contract declares its owner, purpose, fields, filtering, sorting, pagination, freshness, sensitivity and maximum result size. Stable pagination uses a deterministic cursor/keyset or equivalent strategy; offset-only pagination must not silently skip or duplicate records under concurrent changes.

Search indexes and materialised views are derived. They can be rebuilt from source records and versioned transformations. Search snippets, counts, facets and error messages must apply access controls before returning information. A hidden or protected record must not be inferable through aggregate counts, autocomplete, timing, ranking or result omissions.

Narrative search must not truncate or mutate authoritative long-form text. Summaries link to full source records and identify themselves as derived. Missing, ambiguous and inaccessible references have distinct responses that do not reveal protected existence.

## 14. Storage efficiency and capacity

Normalise shared facts and use stable references; avoid repeating person/business names, biographies, addresses, role histories or source payloads in every linked record. Preserve atomic records where normalisation would make reconstruction unsafe or costly.

Measure row, table, index, TOAST, WAL and backup growth as relevant. Benchmark representative high-entropy narratives, long interviews, reports, image metadata and evidence manifests; do not assume compression ratios. Use indexes only where query value justifies write and storage overhead. Avoid unbounded snapshots, duplicated logs and premature aggregation.

Compression, deduplication and compaction are lossless with respect to meaning, chronology, provenance, source content, uncertainty, relationships, corrections and replay requirements. Case-relevant people and evidence are never dropped or downgraded to save storage. Support the fixed population/business constraints.

**Implementation standard:** [Compact-storage design standard](../../storage/COMPACT-STORAGE-DESIGN.md). This applies across all divisions; BP-38 owns data architecture and byte measurement.

## 15. Security and information boundaries

BP-42 owns security policy and classifications; BP-38 enforces the data boundary. Apply least privilege to player, officer, administrator, service, migration and operational identities. Separate read, write, export, schema-change and secret-management capabilities.

Sensitive medical, safeguarding, witness, informant, personnel, intelligence, case and hidden-truth data require explicit access paths. Direct database/API access, joins, search, caches, exports, logs and derived views must not bypass the same policy. Row-level security or an equivalent server-side mechanism is required where appropriate and must be tested against direct and indirect access.

Credentials and connection strings are secrets, never source code, GitHub files, narrative records, migration literals, error messages or logs. Logs redact restricted data but retain safe diagnostic identifiers. Administrative override is attributable and auditable.

## 16. Neon, GitHub and ChatGPT integration

Neon PostgreSQL is the intended authoritative persistent database. GitHub stores source code, schema definitions, migrations, specifications, decision records and test evidence. ChatGPT is the user-facing AI partner/interface and must communicate through documented, permission-checked application contracts.

A successful connection claim requires an actual authenticated test against the expected Neon project, branch, database and schema. Merely having a project ID, connection string, integration or saved configuration is not proof of connectivity. Connection diagnostics must never reveal credentials.

Connection pooling, timeouts, transaction lifetimes and retry policies are bounded. Application startup validates schema compatibility before writes. Safe health checks use bounded read-only queries unless a separately approved test explicitly requires a write. Development, test and production environments and credentials are isolated.

## 17. Migrations and schema evolution

Every migration has a stable ID, purpose, author, source requirement, dependencies, preconditions, postconditions, risk, estimated storage effect, verification and rollback/forward-repair plan. Migrations are versioned in GitHub and applied in deterministic order.

Use additive expand/contract evolution where possible. Active application versions must remain compatible during staged changes. Destructive or lossy transformations require separate explicit approval and a proven recovery path. Schema drift is detected and reported. A failed migration is not marked applied; concurrent migration attempts are serialised or rejected.

Migration files contain no credentials or environment secrets. Canon, population rules, division structure and approved blueprint meaning cannot be changed as incidental schema maintenance.

## 18. Storage approval and measurement gate

Before every Neon schema change, migration, seed/import, bulk write, upload or other mutation:
1. Measure the current database baseline at the relevant project/branch.
2. Record measurement time, method, scope and query/source.
3. Estimate incremental growth in bytes and MiB, separating table, index, TOAST and other material components where possible.
4. State assumptions, representative workload, uncertainty range and projected total.
5. Show the estimate and wait for the user's explicit approval.
6. Do not write if the estimate is not credible; benchmark first.
7. After approved deployment, measure actual growth, compare with estimate and record variance.

No approval is implied by a blueprint, schema draft, GitHub commit or prior unrelated database action. No Neon write has been performed for this BP-38 document.

## 19. Observability and safe maintenance

Expose database availability, connection state, schema version, migration status, storage size, table/index/TOAST growth, connection usage, query latency, deadlocks, constraint failures, queue/outbox lag, failed events and maintenance status. Distinguish healthy, degraded, unavailable, stale and recovering states.

Maintenance procedures include safe query review, vacuum/analyze, index maintenance, retention, partition management and schema drift review. Maintenance cannot remove required history, weaken constraints or mutate game canon. Operator-facing diagnostics and reports remain text-first. Observability itself does not advance simulation time.

## 20. Failure handling and consistency repair

Constraint violations, stale versions, missing references, duplicate IDs, transaction failures, connection loss, migration conflicts, schema drift, corrupted projections and access-denied events produce classified diagnostics. Do not retry non-idempotent operations blindly. Do not silently skip or repair authoritative data.

Repair is an explicit, attributed operation with a source, reason, before/after values, validation and review. Derived projections may be rebuilt from source. Authoritative originals are not regenerated from lossy summaries. BP-39 owns backup/restore and recovery execution; BP-38 validates restored schema, constraints, references and domain invariants before records are declared usable.

## 21. Dependencies and interfaces

- BP-03 supplies canonical person identity and population events.
- BP-04 supplies canonical business/property/organisation identity.
- Every domain supplies its record contracts, state transitions, authority and source data.
- BP-35 supplies event execution/causation contracts.
- BP-36 supplies relationship records and links.
- BP-37 supplies canonical time semantics.
- BP-39 supplies backup, restore and recovery procedures.
- BP-40/BP-41 consume authorised query/report contracts.
- BP-42 supplies access policies and classifications.
- BP-43 owns test strategy, benchmarks and evidence.
- BP-44 governs approved canon/schema version changes.

## 22. Acceptance tests

The following 160 criteria define required BP-38 acceptance coverage. They are design criteria only; none is claimed executed.

- DB-AT-001: Every canonical entity type has one declared identity owner and stable ID namespace.
- DB-AT-002: Person IDs resolve to BP-03 records; BP-38 never creates duplicate person identities.
- DB-AT-003: Business and organisation IDs resolve to BP-04 records and the 10,000-business minimum is not weakened.
- DB-AT-004: Property, premises, roads and spatial references resolve to BP-02/BP-04 canonical records.
- DB-AT-005: Police personnel, cases, incidents, suspects, exhibits and court records resolve to their owning domains.
- DB-AT-006: Cross-domain links use typed foreign references and reject mismatched entity types.
- DB-AT-007: ID allocation is collision-safe under concurrent transactions.
- DB-AT-008: Retired, deceased, closed or merged identities retain resolvable historical references.
- DB-AT-009: Merge and split operations preserve redirects, lineage and source IDs without deleting history.
- DB-AT-010: Registry lookup cannot silently create a new entity when a referenced ID is missing.
- DB-AT-011: Every persisted entity has a documented schema owner and version.
- DB-AT-012: Domain owners control meaning and validation of their records; BP-38 controls shared data contracts and integrity.
- DB-AT-013: BP-38 does not duplicate domain business rules or become a second source of truth.
- DB-AT-014: Schema fields have explicit type, nullability, cardinality, units and allowed values.
- DB-AT-015: Unknown enum values are rejected or preserved in an explicitly versioned extension field.
- DB-AT-016: Required versus optional fields are defined for every lifecycle state.
- DB-AT-017: Schema changes identify all consuming divisions and compatibility effects.
- DB-AT-018: Domain-specific extensions cannot override canonical shared fields.
- DB-AT-019: Cross-domain views cannot write back into source records without an authorised owner command.
- DB-AT-020: Conflicting ownership declarations block design approval until resolved.
- DB-AT-021: Canonical person records and population membership reconcile one-to-one under BP-03 authority.
- DB-AT-022: Living-person count cannot exceed 10,000 under concurrent arrivals, births or status changes.
- DB-AT-023: Police employees and officials are counted once, not added as separate population totals.
- DB-AT-024: One person holding several roles does not create duplicate population rows.
- DB-AT-025: Atomic population transactions either commit all required linked changes or none.
- DB-AT-026: Failed population transactions leave both registry and count unchanged.
- DB-AT-027: Business registry constraints support at least 10,000 businesses without duplicating organisations as people.
- DB-AT-028: Entity lifecycle states cannot contradict the authoritative population or business ledger.
- DB-AT-029: Reconciliation identifies orphaned, duplicated and inconsistent references.
- DB-AT-030: Repair procedures preserve original values and record the reason, actor and evidence.
- DB-AT-031: Every record type has explicit lifecycle states and permitted transitions.
- DB-AT-032: Illegal state transitions are rejected at the data boundary, not merely hidden by the interface.
- DB-AT-033: Terminal states remain historically queryable and cannot be silently reopened.
- DB-AT-034: Reopening or reinstatement is a new attributed transition with authority and reason.
- DB-AT-035: Required state-dependent fields are enforced before commit.
- DB-AT-036: Related records transition atomically where the domain contract requires it.
- DB-AT-037: Concurrent updates cannot silently overwrite a newer version.
- DB-AT-038: Optimistic concurrency detects stale writes and returns a conflict.
- DB-AT-039: Idempotent commands do not create duplicate records or duplicate side effects.
- DB-AT-040: Record deletion is prohibited where retention, evidence, legal or audit rules require preservation.
- DB-AT-041: Every material record has source/provenance appropriate to its domain and sensitivity.
- DB-AT-042: Original source content is retained separately from summaries, extracts and derived interpretations.
- DB-AT-043: Corrections are additive, attributed and historically traceable.
- DB-AT-044: A correction never silently overwrites the prior value or original record.
- DB-AT-045: Record versions identify author, actor, time, reason, authority and changed fields.
- DB-AT-046: Effective time and recorded time remain distinct and queryable.
- DB-AT-047: Imported or external source timestamps preserve source timezone and uncertainty.
- DB-AT-048: Fact, allegation, estimate, inference, intelligence, opinion and adjudicated finding remain distinguishable.
- DB-AT-049: Conflicting source claims can coexist without automatic truth selection.
- DB-AT-050: Derived summaries retain references to all source records and transformation version.
- DB-AT-051: Multi-record domain changes use explicit transaction boundaries.
- DB-AT-052: Population, finance, inventory, staffing and capacity changes reconcile atomically where required.
- DB-AT-053: Foreign-key and uniqueness constraints remain valid at commit.
- DB-AT-054: Deferred constraints are checked before transaction completion.
- DB-AT-055: Concurrent transactions cannot violate unique identity or resource/capacity invariants.
- DB-AT-056: Transaction isolation is selected and documented for each invariant-sensitive operation.
- DB-AT-057: Deadlocks and serialization conflicts are retried only under bounded idempotent policy.
- DB-AT-058: Partial failure rolls back all changes in the declared transaction boundary.
- DB-AT-059: External side effects are emitted through a transactional outbox or equivalent reliable handoff.
- DB-AT-060: Committed events and source records cannot disagree about the same authoritative transition.
- DB-AT-061: Original evidence, statements, calls, intelligence sources and source documents remain immutable once registered under their domain policy.
- DB-AT-062: Append-only history records who did what, when, why and under which authority.
- DB-AT-063: Event ordering uses BP-37 canonical simulation time plus stable sequence metadata.
- DB-AT-064: Event records distinguish occurred, effective, observed, recorded and committed times.
- DB-AT-065: Event replay cannot create duplicate side effects.
- DB-AT-066: Corrections append superseding records while retaining original source data.
- DB-AT-067: Event payloads carry schema version and stable entity references.
- DB-AT-068: Event history records causation and correlation identifiers where relevant.
- DB-AT-069: Derived projections can be rebuilt without changing immutable source history.
- DB-AT-070: Audit history remains available after domain closure, transfer or entity retirement.
- DB-AT-071: Evidence identity and custody remain owned by BP-23; database constraints enforce its declared continuity contract.
- DB-AT-072: Crime-scene observations remain separate from interpretation and forensic conclusions.
- DB-AT-073: Interview originals, recordings, transcripts and adopted statements remain distinct source objects.
- DB-AT-074: Surveillance originals, collection metadata, derivatives and evidential copies remain separately traceable.
- DB-AT-075: Intelligence source material, analytical products and evidence are not collapsed into one record type.
- DB-AT-076: Case identity and lifecycle remain BP-15-owned; linked records never create a second case authority.
- DB-AT-077: Suspect, victim and witness roles remain separate from canonical person identity and adjudicated guilt.
- DB-AT-078: Disclosure packages reference exact source versions and redaction derivatives.
- DB-AT-079: Protected and sensitive data are restricted by BP-42 and are not exposed through generic search or logs.
- DB-AT-080: Hidden offender truth is never stored in player-visible derived views or ordinary query projections.
- DB-AT-081: Every read model identifies its authoritative source and freshness semantics.
- DB-AT-082: Search results preserve entity identity, source reference, status and provenance.
- DB-AT-083: Pagination is stable under concurrent inserts and updates.
- DB-AT-084: Filters and sorting use declared fields and deterministic ordering.
- DB-AT-085: Search indexes do not become independent authorities.
- DB-AT-086: Full-text search can retrieve long narrative content without truncating the authoritative source.
- DB-AT-087: Summaries and snippets are explicitly derived and link to the complete source.
- DB-AT-088: Access filtering occurs before results, counts, facets and snippets are returned.
- DB-AT-089: Query APIs enforce bounded result size and resource limits.
- DB-AT-090: Missing, ambiguous and inaccessible references produce distinct safe responses.
- DB-AT-091: Normalisation removes duplicated shared facts without splitting a logically atomic record.
- DB-AT-092: Repeated entities use stable references instead of repeated identity payloads.
- DB-AT-093: Long narrative source text is stored losslessly and remains readable/exportable.
- DB-AT-094: Compression is benchmarked on representative high-entropy narrative and evidence payloads.
- DB-AT-095: TOAST and large-object growth are measured rather than assumed.
- DB-AT-096: Indexes are justified by query patterns and their write/storage cost is measured.
- DB-AT-097: Redundant snapshots and unbounded duplicated logs are avoided.
- DB-AT-098: Partitioning or archival never removes required cross-case or historical continuity.
- DB-AT-099: Storage compaction preserves all meaning, provenance, relationships and correction lineage.
- DB-AT-100: At least 10,000 businesses and up to 10,000 living people are supported without premature destructive aggregation.
- DB-AT-101: All data access is authorised by BP-42 policy at the service/data boundary.
- DB-AT-102: Least-privilege roles separate player, officer, administrator, service and migration identities.
- DB-AT-103: Sensitive personal, medical, safeguarding, informant and witness data have explicit classification.
- DB-AT-104: Row-level security or equivalent enforcement is tested for direct and indirect query paths.
- DB-AT-105: Unauthorised users cannot infer protected records through counts, errors, search snippets or timing.
- DB-AT-106: Credentials, connection strings and secret values never enter source control or simulation records.
- DB-AT-107: Logs redact secrets and restricted personal data while retaining operational diagnostics.
- DB-AT-108: Exports apply the same permission and redaction policy as interactive reads.
- DB-AT-109: Administrative access and exceptional overrides are attributable and audited.
- DB-AT-110: Schema owners cannot grant themselves broader access merely by changing domain metadata.
- DB-AT-111: Every migration has a stable ID, purpose, author, source requirement and dependency declaration.
- DB-AT-112: Migrations are versioned in GitHub and applied in a deterministic order.
- DB-AT-113: Migration preconditions and postconditions are explicit and testable.
- DB-AT-114: Destructive or lossy transformations are prohibited unless separately authorised and proven reversible or recoverable.
- DB-AT-115: Additive expand/contract changes preserve compatibility with active application versions.
- DB-AT-116: Migration failure leaves a known, recoverable state and is not falsely marked applied.
- DB-AT-117: Concurrent migration attempts are serialised or rejected.
- DB-AT-118: Schema drift is detected against the versioned desired schema.
- DB-AT-119: Rollback or forward-repair procedures are documented for each migration class.
- DB-AT-120: Migration metadata cannot contain credentials, live secrets or private connection details.
- DB-AT-121: Neon PostgreSQL is the authoritative persistent database for the game.
- DB-AT-122: GitHub is the source-control and migration/specification history authority.
- DB-AT-123: ChatGPT is the user-facing AI partner/interface and must use declared application contracts.
- DB-AT-124: Connectivity is not claimed until a successful authenticated connection test returns evidence.
- DB-AT-125: Connection tests verify expected project, branch, database and schema identity without exposing credentials.
- DB-AT-126: Connection pool limits and transaction lifetime are bounded.
- DB-AT-127: Transient connection loss is distinguished from authentication, permission and schema errors.
- DB-AT-128: Application startup validates compatible schema version before accepting writes.
- DB-AT-129: Read/write health checks use safe bounded queries and do not mutate canonical game state.
- DB-AT-130: Development, test and production credentials/data are isolated.
- DB-AT-131: Monitoring exposes database health, size, table/index/TOAST growth, connections and query latency.
- DB-AT-132: Failed transactions, constraint violations and deadlocks are attributable and diagnosable.
- DB-AT-133: Slow query monitoring records safe query identifiers and avoids leaking sensitive values.
- DB-AT-134: Queue and outbox lag are visible to operators.
- DB-AT-135: Database maintenance operations are bounded, documented and recoverable.
- DB-AT-136: Vacuum, analyze, index maintenance and retention actions cannot violate canonical record history.
- DB-AT-137: Development/test data cannot be mistaken for authoritative simulation records.
- DB-AT-138: Health reporting distinguishes unavailable, degraded, stale and healthy states.
- DB-AT-139: Operator-facing status is available through text-first interface and reports.
- DB-AT-140: Observability records do not themselves mutate game canon or advance simulation time.
- DB-AT-141: Every schema object maps to an approved blueprint requirement or explicit approved technical decision.
- DB-AT-142: Every implementation change links its GitHub commit, migration and tests.
- DB-AT-143: Design, implementation, test execution and verification statuses remain separate.
- DB-AT-144: Documentation alone never marks a schema or division implemented or verified.
- DB-AT-145: Canon and division structure cannot be changed by an ordinary schema migration.
- DB-AT-146: Before every Neon write, current database size is measured and timestamped.
- DB-AT-147: Before every Neon write, incremental bytes/MiB and projected total are estimated with method, assumptions and uncertainty.
- DB-AT-148: No Neon write occurs without the user's explicit approval after the estimate is shown.
- DB-AT-149: After an approved write, actual database growth is measured and compared with estimate.
- DB-AT-150: Unapproved or failed writes are detected, reported and reconciled without claiming success.
- DB-AT-151: BP-38 owns schema integrity and record consistency; BP-39 owns backup, restore and recovery execution.
- DB-AT-152: Recovery restores preserve BP-38 constraints and validate them before the system is declared usable.
- DB-AT-153: BP-35 owns event execution; BP-38 stores validated source and committed state without taking runtime authority.
- DB-AT-154: BP-37 owns canonical clock semantics; BP-38 persists time-bearing records using its contract.
- DB-AT-155: BP-44 owns canonical version/change approval; BP-38 enforces deployed schema version compatibility.
- DB-AT-156: BP-43 owns test strategy and evidence; BP-38 supplies schema-level fixtures and invariant tests.
- DB-AT-157: BP-40 displays authorised records but cannot bypass server-side access checks.
- DB-AT-158: Domain divisions retain authoritative business rules and state transitions.
- DB-AT-159: Cross-domain transactions declare their owning coordinator and failure semantics.
- DB-AT-160: All global canon, player-agency, pause and hidden-truth constraints survive storage, export, query and restore.

## 23. Source traceability

The following source requirements and tests are mapped to BP-38 by the authoritative crosswalk. The source wording is reproduced for traceability; the JSON source remains authoritative.

| Source ID | Source division | Original requirement/test wording |
|---|---|---|
| S03.R01 | Population accounting and demographic model | Enforce the 9,500 opening total: 9,000 residents plus 500 police; 500 reserve; 10,000 hard cap. |
| S03.R02 | Population accounting and demographic model | Maintain one authoritative person registry and exact living/deceased/entered/exited status. |
| S03.R03 | Population accounting and demographic model | Track age, household, residence, occupation, eligibility, movement, births, deaths and permanent departures according to canon. |
| S03.R04 | Population accounting and demographic model | Use atomic capacity checks for arrivals and births; reject any event that would exceed cap. |
| S03.R05 | Population accounting and demographic model | Prevent double-counting police or people with multiple roles. |
| S03.T01 | Population accounting and demographic model | Population ledger reconciles to person records. |
| S03.T02 | Population accounting and demographic model | No valid operation can produce 10,001 living persons. |
| S03.T03 | Population accounting and demographic model | Police count is a subset of total population, not an extra uncounted population. |
| S04.R01 | Person identity and life records | Give each person a stable identity, attributes, history, needs, schedule, skills, employment, finances, relationships and relevant records. |
| S04.R02 | Person identity and life records | Use tiered processing without deleting or downgrading persistent identities or established facts. |
| S04.R03 | Person identity and life records | Promote any person materially connected to police activity or a case to persistent full-detail status for the remainder of the simulation. |
| S04.T01 | Person identity and life records | Identity remains stable across jobs, addresses and relationships. |
| S04.T02 | Person identity and life records | Promoted people are never downgraded or erased. |
| S05.R01 | Households, relationships and social networks | Represent households, families, partners, dependants, friendships, conflicts, professional links and social networks. |
| S05.R02 | Households, relationships and social networks | Track relationship history, shared addresses, contact patterns and plausible changes. |
| S05.R03 | Households, relationships and social networks | Generate consistent witness, victim, suspect and community connections without deterministic shortcuts. |
| S05.T01 | Households, relationships and social networks | Relationship links are reciprocal where applicable and historically traceable. |
| S06.R01 | Housing, property and tenancy | Represent residential and commercial parcels, owners, landlords, tenants, leases, occupancy, vacancies, access rights, maintenance and disputes. |
| S06.R02 | Housing, property and tenancy | Track lease terms, renewals, payments, subletting, licences, keys and occupancy history where relevant. |
| S06.R03 | Housing, property and tenancy | Ensure occupancy and access facts are time-valid. |
| S06.T01 | Housing, property and tenancy | No simultaneous incompatible occupancy or ownership state without an explicit explanation. |
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
| S11.R01 | Government and public administration | Define executive, legislative, administrative and oversight functions, offices, incumbents, mandates, decision processes and records. |
| S11.R02 | Government and public administration | Represent public policy, procurement, permits, licensing, inspections and public complaints. |
| S11.R03 | Government and public administration | Ensure government actions have accountable actors, authority and dates. |
| S11.T01 | Government and public administration | Every official action has an authorised actor and traceable record. |
| S12.R01 | Civil registry and public records | Maintain civil status, identity, address, property, business, permits and other canonically required registers. |
| S12.R02 | Civil registry and public records | Track corrections, versions, issuing authority, access and provenance. |
| S12.R03 | Civil registry and public records | Support lawful in-world retrieval and controlled disclosure. |
| S12.T01 | Civil registry and public records | Record changes preserve prior values and reason for change. |
| S13.R01 | Healthcare and public health | Represent hospitals, clinics, practitioners, emergency care, capacity, appointments, treatment events and public-health alerts. |
| S13.R02 | Healthcare and public health | Model injuries, deaths, medical evidence and care access consistently without turning healthcare into a separate deep simulation. |
| S13.R03 | Healthcare and public health | Protect sensitive information through role-based access in-world. |
| S13.T01 | Healthcare and public health | Medical timelines and capacity are internally consistent. |
| S14.R01 | Education, training and research | Represent schools, colleges, training providers, enrolment, attendance, staff, qualifications, schedules and facilities. |
| S14.R02 | Education, training and research | Support police recruitment/training and city workforce development. |
| S14.R03 | Education, training and research | Generate credible education and qualification histories. |
| S14.T01 | Education, training and research | Qualifications have issuing bodies, dates and valid prerequisites where applicable. |
| S15.R01 | Social care, welfare and community support | Represent social services, housing support, safeguarding, disability support, youth and elder services, charities and community organisations. |
| S15.R02 | Social care, welfare and community support | Track referrals, eligibility, capacity, case status and outcomes proportionately. |
| S15.R03 | Social care, welfare and community support | Allow these services to affect vulnerability, risk, support and police interactions. |
| S15.T01 | Social care, welfare and community support | Referrals have an origin, receiving service, status and outcome or pending state. |
| S19.R01 | Environment, weather and natural hazards | Model local weather, daylight, tides or water conditions where geographically relevant, seasons, pollution and hazards. |
| S19.R02 | Environment, weather and natural hazards | Apply environmental conditions to visibility, travel, infrastructure, health and evidence persistence where justified. |
| S19.R03 | Environment, weather and natural hazards | Keep environmental chronology consistent. |
| S19.T01 | Environment, weather and natural hazards | Environmental facts are location- and time-valid. |
| S25.R01 | Police duty rosters, staffing and deployment | Generate and maintain shifts, duty rosters, leave, absences, minimum staffing, specialist availability, patrol areas and command coverage. |
| S25.R02 | Police duty rosters, staffing and deployment | Account for workload, geography, skills, fatigue and emergency demand. |
| S25.R03 | Police duty rosters, staffing and deployment | Record roster changes and actual attendance separately. |
| S25.T01 | Police duty rosters, staffing and deployment | No officer is simultaneously assigned to incompatible duties. |
| S26.R01 | Police command, policy and internal governance | Represent orders, policies, briefings, operational plans, supervision, approvals, audits, complaints, misconduct and review. |
| S26.R02 | Police command, policy and internal governance | Record who authorised, issued, received and executed every material instruction. |
| S26.R03 | Police command, policy and internal governance | Support fair internal process and traceable decisions. |
| S26.T01 | Police command, policy and internal governance | Material command decisions have authority, rationale and audit trail. |
| S27.R01 | 911, call-taking, CAD and dispatch | Represent emergency/non-emergency intake, caller identity or anonymity, call recording, triage, incident creation, unit recommendation, dispatch, radio, status and closure. |
| S27.R02 | 911, call-taking, CAD and dispatch | Preserve original call content and event chronology; distinguish caller claims from verified facts. |
| S27.R03 | 911, call-taking, CAD and dispatch | Support concurrent calls, priority changes, escalation and interagency dispatch. |
| S27.T01 | 911, call-taking, CAD and dispatch | Every dispatched unit and status transition is chronologically auditable. |
| S30.R01 | Case management and investigative command | Create stable case IDs, ownership, classification, status, objectives, actions, decisions, reviews, deadlines, linked incidents and closure reasons. |
| S30.R02 | Case management and investigative command | Support concurrent investigations, cold cases, linked series, referrals and reopened cases. |
| S30.R03 | Case management and investigative command | Preserve full case chronology and decision provenance. |
| S30.T01 | Case management and investigative command | Every case state change has actor, time, reason and evidence. |
| S32.R01 | Scene management and evidence collection | Represent scene boundaries, entry logs, scene security, search areas, recovery methods, exhibits, packaging, seals, handlers and transfers. |
| S32.R02 | Scene management and evidence collection | Preserve original observations separately from interpretation. |
| S32.R03 | Scene management and evidence collection | Support physical, digital, documentary, biological, trace and testimonial evidence. |
| S32.T01 | Scene management and evidence collection | Every exhibit has unique ID, recovery details, continuity and current location/status. |
| S34.R01 | Interviews, interrogations and statements | Represent interview planning, cautions/procedural status as fictional canon requires, participants, recordings, notes, questions, answers, breaks, disclosure and statement versions. |
| S34.R02 | Interviews, interrogations and statements | Preserve verbatim or detailed source content where available; distinguish summaries from originals. |
| S34.R03 | Interviews, interrogations and statements | Do not generate leading prompts or reveal hidden case solutions to the player. |
| S34.T01 | Interviews, interrogations and statements | Interview chronology, participants and recording references reconcile. |
| S35.R01 | Intelligence, analysis and information handling | Represent source grading, reliability, confidence, dissemination, restrictions, analytical products, links and review dates. |
| S35.R02 | Intelligence, analysis and information handling | Separate intelligence from evidence and established fact. |
| S35.R03 | Intelligence, analysis and information handling | Preserve source provenance and uncertainty. |
| S35.T01 | Intelligence, analysis and information handling | Every intelligence item has source, confidence and handling status. |
| S36.R01 | Surveillance, observation and technical monitoring | Represent physical observation, CCTV, ANPR or equivalent systems, authorised technical monitoring, coverage, blind spots, time drift, retention and retrieval. |
| S36.R02 | Surveillance, observation and technical monitoring | Track requests, authorisations, collection windows, operators, exports and evidential continuity. |
| S36.R03 | Surveillance, observation and technical monitoring | Never treat absence of coverage as proof of absence. |
| S36.T01 | Surveillance, observation and technical monitoring | Every surveillance item has source device, coverage limits and time basis. |
| S37.R01 | Arrest, search, warrants and custody | Represent grounds, authority, applications, approvals, execution, person/property searches, seizure, transport, booking, detention, welfare, reviews and release. |
| S37.R02 | Arrest, search, warrants and custody | Maintain custody clock and property continuity. |
| S37.R03 | Arrest, search, warrants and custody | Separate operational action from later legal decision. |
| S37.T01 | Arrest, search, warrants and custody | Custody and warrant events satisfy configured fictional rules and chronological constraints. |
| S38.R01 | Prosecution, courts and legal outcomes | Represent charging decisions, disclosure, prosecution, defence, hearings, evidence, rulings, verdicts, sentencing, appeals and case outcomes. |
| S38.R02 | Prosecution, courts and legal outcomes | Track procedural state and legal actors; preserve acquittals, dismissals and unresolved outcomes. |
| S38.R03 | Prosecution, courts and legal outcomes | Feed outcomes back into records without rewriting investigative history. |
| S38.T01 | Prosecution, courts and legal outcomes | Court outcomes link to the correct charges, defendants and evidence versions. |
| S39.R01 | Corrections, rehabilitation and post-sentence status | Represent sentence execution, prison or community supervision, rehabilitation, release, recall and post-release status proportionately. |
| S39.R02 | Corrections, rehabilitation and post-sentence status | Maintain continuity between custody, court and person records. |
| S39.T01 | Corrections, rehabilitation and post-sentence status | Sentence and release dates reconcile with court orders. |
| S40.R01 | Complaints, oversight and public accountability | Represent public complaints, independent review, internal investigations, inspections, findings, remedies and published outcomes. |
| S40.R02 | Complaints, oversight and public accountability | Preserve due process, conflicts of interest and auditability. |
| S40.R03 | Complaints, oversight and public accountability | Allow institutional failure and public trust to evolve from events. |
| S40.T01 | Complaints, oversight and public accountability | Every complaint has a route, owner, status and outcome or pending reason. |
| S41.R01 | Time, calendar, schedules and simulation clock | Maintain one authoritative in-world clock, calendar, time zones, shifts, opening hours, deadlines and event ordering. |
| S41.R02 | Time, calendar, schedules and simulation clock | No time advances while player is outside the simulation; resume without hidden elapsed simulation time. |
| S41.R03 | Time, calendar, schedules and simulation clock | Support paused, active, queued and historical events. |
| S41.T01 | Time, calendar, schedules and simulation clock | All event timestamps use one canonical time basis and stable ordering. |
| S42.R01 | Simulation engine, causality and world activity | Coordinate people, organisations, services, incidents, schedules, resources, weather and time through deterministic, auditable event processing where feasible. |
| S42.R02 | Simulation engine, causality and world activity | Use relevance-based processing without breaking persistence or continuity. |
| S42.R03 | Simulation engine, causality and world activity | Prevent impossible simultaneous states, causal loops and unexplained state mutation. |
| S42.R04 | Simulation engine, causality and world activity | Background activity must not advance while the player is out. |
| S42.T01 | Simulation engine, causality and world activity | Replay of a recorded event sequence yields the same authoritative state where deterministic replay is specified. |
| S43.R01 | AI generation, narrative and player agency | Generate detailed, varied, naturalistic text consistent with records, knowledge boundaries, character voice and uncertainty. |
| S43.R02 | AI generation, narrative and player agency | Separate hidden world truth from player-visible information and from NPC knowledge. |
| S43.R03 | AI generation, narrative and player agency | Never disclose culprit/accomplice/perpetrator identities or hidden solution unless the player types exactly 'bingo'. |
| S43.R04 | AI generation, narrative and player agency | Never provide unsolicited solution hints or tell the player what to investigate next; present available records and let the player decide. |
| S43.R05 | AI generation, narrative and player agency | All generated claims that alter canon must be persisted as structured events or records. |
| S43.T01 | AI generation, narrative and player agency | No hidden truth leaks before the exact reveal trigger. |
| S43.T02 | AI generation, narrative and player agency | NPC knowledge never exceeds their plausible information. |
| S44.R01 | Text interface, commands and player workflow | Provide a laptop-style, text-first interface with clear navigation, commands, records, status and contextual actions. |
| S44.R02 | Text interface, commands and player workflow | Support individual-officer gameplay, including recruit start where selected. |
| S44.R03 | Text interface, commands and player workflow | Keep prose and source records readable while using compact presentation for navigation and metadata. |
| S44.R04 | Text interface, commands and player workflow | No essential action depends on graphics. |
| S44.T01 | Text interface, commands and player workflow | All essential workflows are operable through text commands and views. |
| S45.R01 | Maps, diagrams and visual evidence | Provide optional maps, layouts, timelines, charts and forensic scene visuals when useful or requested. |
| S45.R02 | Maps, diagrams and visual evidence | Visuals must derive from canonical spatial/evidence data and never silently contradict text records. |
| S45.R03 | Maps, diagrams and visual evidence | Keep text as authoritative source. |
| S45.T01 | Maps, diagrams and visual evidence | Every visual can be traced to the underlying canonical records. |
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

### Cross-cutting and governing traceability

| X01 | Stable identity and provenance across every domain; domain owners create records while shared registries enforce canonical identity. | BP-01,BP-03,BP-04,BP-05,BP-06,BP-12,BP-15,BP-23,BP-35,BP-38,BP-39,BP-44 |
| X02 | Single source of truth; no contradictory duplicate authority, including spatial, person, business, time, case, evidence and finance records. | BP-01,BP-02,BP-03,BP-04,BP-05,BP-12,BP-15,BP-23,BP-34,BP-35,BP-37,BP-38,BP-44 |
| X03 | All time-dependent facts are effective-dated and historically queryable; all domain divisions must comply with the shared clock contract. | BP-01,BP-02,BP-03,BP-04,BP-05,BP-08,BP-10,BP-11,BP-12,BP-15,BP-16,BP-19,BP-20,BP-22,BP-23,BP-25,BP-26,BP-27,BP-28,BP-29,BP-33,BP-35,BP-37,BP-38,BP-39,BP-43 |
| X04 | All financial, population, inventory, staffing, resource and capacity changes reconcile atomically. | BP-03,BP-04,BP-06,BP-08,BP-09,BP-11,BP-12,BP-26,BP-29,BP-33,BP-34,BP-35,BP-38,BP-43 |
| X05 | Distinguish fact, allegation, estimate, inference, intelligence, opinion, source statement, analytical conclusion and adjudicated finding. | BP-01,BP-12,BP-13,BP-15,BP-16,BP-17,BP-18,BP-19,BP-20,BP-21,BP-22,BP-23,BP-24,BP-27,BP-28,BP-31,BP-38,BP-42 |
| X06 | Preserve originals; derived summaries never replace source records; corrections are additive, attributed and historically traceable. | BP-01,BP-12,BP-15,BP-16,BP-19,BP-20,BP-21,BP-22,BP-23,BP-24,BP-27,BP-28,BP-31,BP-38,BP-39,BP-43 |
| X07 | No hidden simulation time while player is out; pause/resume and deliberate time advancement are explicit. | BP-01,BP-35,BP-37,BP-38,BP-39,BP-40,BP-43 |
| X08 | Text-first operation; optional maps/graphics cannot be required and cannot contradict authoritative text/records. | BP-01,BP-02,BP-20,BP-22,BP-23,BP-24,BP-38,BP-40,BP-43 |
| X10 | No design/implementation/test/verification status is asserted without the corresponding approval, artefact, passing test and reproducible evidence. | BP-01,BP-38,BP-39,BP-43,BP-44 |
| C05 | `/canon/population/hard_cap`: 10,000 living people maximum | BP-01,BP-03,BP-38,BP-43 |
| C06 | `/canon/population/counting` and `/canon/population/rule`: count every qualifying living person once; atomic entries/exits/deaths; never exceed cap | BP-01,BP-03,BP-35,BP-38,BP-43 |
| C09 | `/canon/priority`: canon/player agency → fidelity → continuity/integrity → minimum lossless storage → performance | BP-01,BP-38,BP-43,BP-44 |
| P04 | `/principles/3`: preserve detail; compress structure, never meaning | BP-01,BP-38,BP-43 |
| P05 | `/principles/4`: stable unique IDs, lifecycle, provenance and explicit relationships | BP-01,BP-03,BP-04,BP-38 |
| P06 | `/principles/5`: reconcile time, population, money, stock, capacity, authority and location | BP-01,BP-02,BP-03,BP-04,BP-05,BP-34,BP-35,BP-37,BP-38,BP-43 |
| P10 | `/principles/9`: no completion without implementation and test evidence | BP-01,BP-38,BP-43,BP-44 |
| M04 | `/completion_states`: NOT_STARTED, DESIGNED, IMPLEMENTED, TESTED, VERIFIED, BLOCKED, RETIRED | BP-01,BP-38,BP-43,BP-44 |
| M05 | `/completion_rule`: VERIFIED requires implementation, passing acceptance tests, reconciled dependencies and linked GitHub evidence; documentation alone is insufficient | BP-01,BP-38,BP-43,BP-44 |
| M07 | `/out_of_scope/0..5`: second playable city; equal-depth non-police simulation; graphics prerequisite; unbounded population; unapproved Neon writes; invented completion status | BP-01,BP-02,BP-03,BP-04,BP-38,BP-40,BP-43,BP-44 |
| M08 | `/traceability`: every requirement stable ID; implementation, test, schema object and evidence link to it | BP-01,BP-38,BP-43,BP-44 |
| A10 | Database architecture requirement omitted ChatGPT interface and connectivity/quality verification. | Expanded S46.R01. | BP-38 owns data; BP-39 persistence; BP-40 interface; BP-43 tests; BP-44 source/version governance. |

**Traceability count:** 161 distinct source requirement/test IDs mapped to BP-38, extracted from all crosswalk rows that name BP-38. Cross-cutting, canon, principles and governance mappings are listed separately above. This is incorporation planning; it is not evidence that implementation or tests have been completed.

## 24. Open design/configuration decisions

1. Final canonical ID formats/namespaces and whether IDs are UUID, ULID or another opaque stable scheme.
2. Exact domain schema catalogue, ownership registry and schema naming convention.
3. PostgreSQL version-specific feature selection and compatibility policy.
4. Transaction isolation/locking policy by invariant class.
5. Outbox/event envelope format, partitioning and retention.
6. Immutable event payload policy and permitted correction patterns by domain.
7. Data classification taxonomy and exact BP-42 policy matrix.
8. Row-level security versus service-layer enforcement boundaries and defence-in-depth requirements.
9. Narrative compression/TOAST benchmark corpus and acceptable measured trade-offs.
10. Index policy, partitioning thresholds and archival strategy.
11. Migration runner, advisory locking and release sequencing.
12. Environment topology, connection pooling and safe health-check design.
13. Backup/restore verification handoff and integrity evidence format with BP-39.
14. Schema drift and migration rollback/forward-repair thresholds.
15. Data retention and deletion policy by record category, subject to source-domain and canon constraints.
16. Read-model freshness and pagination contracts for each interface.
17. Exact database size measurement query set and reporting format.
18. Test harness, fixtures and evidence links required by BP-43.

These decisions do not alter the fixed 44 divisions, approve a Neon write or permit a relaxation of the user's storage-measurement approval gate.

## SW-NAM-001 — shared naming persistence slice

Disposable proposal `db/proposals/0009_universal_name_registry.sql` adds immutable `sw_names.generation_batch` manifest records, `sw_names.name_reservation`, append-only `sw_names.name_event`, normalized registry/search view and transactional reservation/lifecycle functions. Generated reservations can reference the deterministic generator/configuration version, seed and SHA-256 manifest. It uses stable BP-02 `spatial_id` and BP-03 `person_id` references, database uniqueness constraints, an indexed `pg_trgm` near-duplicate review gate, append-only name history, domain triggers and controlled function grants. The command role receives no direct registry-table DML; read-only lookup is exposed through the registry view/search function. Only `GEOGRAPHY` and `PERSON` adapters are connected. BP-04 and operational entity types remain NOT CONNECTED until authoritative schemas exist. This is a disposable schema proposal only; no Neon migration, schema write or production seed has occurred. CI and restore evidence are pending.

## 25. Completion status

- Specification: DESIGNED_DRAFT; review/approval pending.
- Implementation: NOT_STARTED.
- Test execution: NOT_STARTED. The 160 acceptance criteria are not execution evidence.
- Verification: NOT_STARTED.
- Neon connectivity: not newly tested by this specification task; no connectivity claim is made.
- Neon writes: none performed or authorised.
- Next division in fixed numeric order: BP-39 — Persistence and Recovery.
