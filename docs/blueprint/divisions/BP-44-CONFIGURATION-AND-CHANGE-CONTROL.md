# BP-44 — Configuration and Change Control

**Project:** Saltwater  
**Division:** BP-44 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT — review/approval pending  
**Implementation / test execution / verification:** NOT_STARTED  
**Primary responsibility:** Canonical blueprint governance, configuration registry, decisions, versioning, change approval, impact assessment and controlled activation.  
**Write restriction:** This specification authorises no Neon write, migration, seed/import, bulk operation, upload, credential change, provider substitution or production deployment.

## 1. Purpose

BP-44 is the control plane for how Saltwater's canon, approved requirements, configuration, schemas, interfaces, operational procedures and implementation artefacts are proposed, reviewed, approved, versioned, activated, superseded and retired. It ensures that the project remains one coherent simulation rather than accumulating contradictory documents, accidental scope expansion, silent rule changes or untraceable implementation decisions.

BP-44 controls change; it does not own the domain truth being changed. Domain owners retain responsibility for their records and behaviour. BP-01 owns the governing canon; BP-38 owns database schemas and records; BP-43 owns test strategy and evidence; BP-42 owns security policy; BP-39 owns persistence/recovery. BP-44 ensures changes are properly authorised, coordinated and evidenced across those owners.

## 2. Binding canon and invariants

The following are hard constraints, not ordinary defaults: Saltwater is one sovereign city-state, one playable city and one jurisdiction; no external playable territory or expansion; exactly 44 blueprint divisions in the approved order; a hard cap of 10,000 living persons across all represented roles; at least 10,000 businesses; police is the deepest simulation; text-first is permanent and graphics are optional; simulation time freezes when the player is absent/paused; case-relevant persons are permanently promoted to full persistent simulation; hidden offender/accomplice truth is protected until the exact case-sensitive standalone `bingo` trigger.

Changing any of these constraints requires explicit user approval and a recorded canon amendment. No ordinary configuration override, environment variable, AI output, administrator action, migration or provider setting may silently weaken them. The 52-division source remains preserved as source material; the 44-division blueprint is the fixed target structure.

## 3. Scope and exclusions

**Included:** canonical blueprint version; source preservation and crosswalk governance; requirements and decision log; glossary; configuration catalogue and snapshots; schema registry coordination; change requests; approvals; impact analysis; compatibility; migration and deployment governance; release records; deprecation and retirement; audit and provenance; environment promotion; exception and emergency change process.

**Excluded:** domain record meaning and lifecycle; runtime simulation execution; canonical clock; database schema implementation; backup/restore execution; authentication/authorization policy; test execution tooling; UI presentation. BP-44 coordinates and gates these activities through BP-01, BP-35, BP-37–BP-43 and relevant domain owners.

## 4. Authority hierarchy and artefact classes

Artefacts include master blueprint, source blueprint, crosswalk, division specification, decision record, glossary, configuration schema, environment profile, configuration snapshot, schema registry entry, API/event contract, change request, impact assessment, approval, migration, release manifest, test/evidence package, exception, deprecation notice and retirement record.

Authority order: approved canon and explicit user decisions; approved master blueprint and requirements; approved division specifications; approved configuration/schema/contract versions; implemented code and migrations; runtime data and derived views. A lower-level artefact cannot override a higher-level rule. Draft source text and AI suggestions remain proposals until approved.

The authoritative location and version for each artefact are registered. Copies and generated views are references, not competing authorities. Conflicts are logged and escalated to the relevant owner; they are not resolved by silently choosing the newest file.

## 5. Canon, blueprint and requirement governance

The fixed 44-division structure is immutable without explicit user approval. Every division ID, name and position is checked against the master blueprint. No addition, removal, reorder, split, merge or rename occurs implicitly.

The original 52-division source is preserved unchanged as source material unless the user explicitly authorises a source revision. The 52→44 crosswalk maps every source requirement and test to one or more target divisions. Structural coverage is not semantic completeness: semantic audits must inspect original wording, identify omissions/conflicts/ambiguous ownership and record their disposition.

Requirement IDs remain stable. Wording changes are versioned and justified. Retired requirements retain historical IDs, rationale and replacement links. No requirement may disappear through file rewrite, formatting, compression or crosswalk editing without explicit disposition.

## 6. Configuration catalogue and snapshots

Every configurable value has a stable namespaced key, type, owner, scope, description, default status, allowed values/range, units, nullability, validation, dependency constraints, environment applicability, sensitivity classification and provenance. Configuration is distinguished from canon, illustrative examples, runtime state and unresolved decisions.

Configuration schemas are versioned. A snapshot is an immutable, complete, validated set of effective values for a declared environment and activation boundary. It records source commit, schema version, environment, author, approval, content hash, creation and activation time. Edits create a new snapshot; they do not mutate an active snapshot in place.

Missing mandatory keys, invalid types, out-of-range values, incompatible combinations, unknown keys and unsafe overrides fail validation before activation. Secrets and credentials are not stored in ordinary configuration. Environment-specific settings may tune technical operation but cannot override canon or approved domain policy.

Development, test and authoritative runtime configurations are separate. Promotion between environments is explicit, reproducible and reviewable. Test data and credentials cannot silently point at production. Production activation cannot originate from an unreviewed or unapproved development state.

## 7. Decision log, glossary and ownership registry

Every material design or policy decision has a stable ID, question, context, alternatives, selected outcome or unresolved status, rationale, decision authority, date, affected requirements/divisions, dependencies and evidence. Open decisions have an owner and required next input. Silence is not approval.

A canonical glossary defines terms, abbreviations, status labels and distinctions. Each term has a definition, scope, owner and synonyms; ambiguous or overloaded terms are flagged. The schema registry identifies canonical entities, fields, types, constraints, relationships, versions, status, owning division, compatibility and migration notes. BP-38 owns database schema semantics; domain owners own domain meaning.

Each division has one accountable owner for its domain meaning. Cross-division data, events and contracts name the producer, consumer, authoritative owner, permitted mutations, failure behaviour and versioning rules. Shared fields do not create competing sources of truth.

## 8. Change request lifecycle

Every material change begins with a stable change-request ID and records requester, date, reason, classification, affected artefacts, exact proposed scope, alternatives, requirements, impacted divisions, dependencies, compatibility, migration, storage, security, privacy, operational and recovery impacts, tests, risks and rollback/forward-recovery approach.

Lifecycle: proposed → triaged → impact-assessed → reviewed → pending approval → approved / rejected / withdrawn / deferred → scheduled → implemented → tested → verified → released → monitored → closed; or superseded/cancelled where applicable. Each transition records actor, time, reason and evidence. No transition is inferred from a commit alone.

Change classes include editorial-only, configuration, canon, requirement/specification, schema/data, code/behaviour, security/permission, integration/provider, operational procedure and emergency. A change may have multiple classes; the highest applicable approval and impact requirements apply.

## 9. Approval and authority

Approval is explicit, attributable and bound to an exact artefact version/content hash, scope, environment and operation. It records approver, authority, date, conditions, expiry if any and evidence. A document approval does not approve implementation; implementation approval does not approve production activation; none of these grants permission to write to Neon.

Changes to canon, the fixed division structure, population cap, city boundary, business minimum, player agency, pause semantics or hidden-truth reveal rule require explicit user approval. A change to approved design requires a recorded decision. Silence, prior approval of a different version, successful tests, administrator privilege or AI recommendation cannot substitute for approval.

Where separation of duties is configured, requester, reviewer, approver and executor are distinct. Delegated approval is valid only within recorded scope and time. Rejected, withdrawn, expired and superseded approvals remain in history. A changed content hash invalidates stale approval.

## 10. Impact assessment and dependency control

Impact analysis identifies affected divisions, requirements, entities, schemas, APIs, events, jobs, interfaces, reports, permissions, NPC behaviours, cases, evidence, finance, people, businesses, persistence, backups, player workflows and external integrations as relevant. It identifies downstream consumers and required owner reviews.

Changes to population/geography require BP-02/BP-03/BP-04 review; police authority/career/personnel changes require relevant BP-05–BP-08/BP-30–BP-33 review; crime/case/evidence/legal changes require BP-13–BP-29 review; simulation/time changes require BP-35/BP-37; records/storage/recovery require BP-38/BP-39; interface/reporting require BP-40/BP-41; security changes require BP-42; test and release evidence require BP-43.

Unresolved critical conflicts, missing owner review, unquantified storage risk or absent recovery path block activation. An impact assessment cannot silently transfer domain ownership to BP-44.

## 11. Schema, API, event and migration governance

BP-38 owns canonical database schemas, constraints, IDs, indexes, transactions and migration implementation. BP-44 governs approval and coordination of changes to them. Schema and event versions are explicit; compatibility and consumer impacts are documented. IDs are never silently reused.

Breaking changes require a versioned migration plan, preconditions, postconditions, representative test, backup/recovery review and rollback or forward-recovery procedure. Migrations are ordered, versioned, repeatable or safely guarded against duplicate application. Partial failure must leave authoritative state consistent or invoke a verified recovery plan. Data corrections preserve original value, actor, reason, authority, timestamp and lineage.

Migration approval is specific to the exact operation and target. No migration, schema change, seed/import, bulk write, upload or credential change is authorised by a blueprint or this specification.

## 12. Mandatory Neon storage and write governance

Before every proposed Neon write or database-changing operation, measure the current live baseline. Estimate incremental storage in bytes and MB/MiB; disclose method, assumptions and uncertainty; calculate projected post-write total; and present the estimate before requesting explicit user approval. If the estimate is not credible, benchmark a representative sample first and do not deploy until a defensible estimate exists.

After each specifically approved operation, measure actual database growth and compare it with the estimate; record actual delta and explain material variance. Approval for one operation does not authorise a later operation, a larger scope or a changed estimate. A material difference from the approved operation requires renewed approval before proceeding.

Measure row, table, index and TOAST growth where applicable. Use representative high-entropy narrative data. Compact structure, normalise shared facts and deduplicate repeated payloads, but never remove meaningful narrative, case facts, provenance or other information. Never infer live Neon connectivity or storage from old measurements, GitHub state, mock results or cached output.

## 13. GitHub, Neon, ChatGPT and integration governance

Saltwater's selected architecture is GitHub for source control/specifications/migration history, Neon PostgreSQL for persistent data and ChatGPT as user-facing AI partner/interface. Substitutions that alter this approved architecture require explicit architecture review and user approval.

Every integration declares owner, purpose, environment, permitted data/actions, credential source, scopes, failure behaviour, revocation and audit. Secrets are controlled by BP-42 and never committed. Integration failures cannot silently cause duplicate writes, lost events or unauthorized external side effects. No configuration can authorize real-world communications or side effects beyond explicit user intent and approved capability.

## 14. Repository, version and release governance

Every approved release identifies immutable Git commit, branch/tag, blueprint version, configuration snapshot, schema/migration version, test-suite revision, evidence package, approvals and known exceptions. Repository changes link to change requests and preserve history. Protected canonical artefacts cannot be overwritten without traceable version history and required approval.

AI-generated or externally proposed changes are untrusted proposals. AI cannot approve its own output, grant itself authority, alter the approval workflow or bypass canon. Every AI-assisted change records the human decision authority and exact diff scope. Prompt injection and source text cannot modify this control policy.

Register entries must match real file paths, IDs, titles and separate design/implementation/test/verification states. Register history is chronological, unique and evidence-backed. Cross-reference links are checked for existence.

## 15. Deprecation, retirement and rollback

Deprecation identifies reason, replacement, affected consumers, compatibility period, migration and sunset criteria. Retirement occurs only after dependencies are resolved or explicitly excepted. Retired artefacts remain auditable and recoverable under retention policy; IDs are not reused.

Rollback restores a known valid code/configuration state but does not silently erase valid newer domain records. Data rollback requires an explicit recovery plan and BP-39 review. Derived views and caches are rebuilt or invalidated after relevant changes. Configuration activation is atomic or has a documented partial-failure strategy. Concurrent edits use conflict detection; stale approvals cannot authorize changed content.

## 16. Emergency change and change freeze

Emergency changes are limited to the minimum necessary scope, with recorded reason, authority, affected systems, expiry, compensating controls and retrospective review. Emergency status does not bypass user approval for canon changes or Neon writes. Temporary exceptions expire and cannot be reused after expiry.

A change freeze may be invoked for security incident, data-integrity risk, recovery, provider instability or unresolved critical defect. Its scope, authority, start, review interval, release conditions and expiry are explicit. Emergency access and security policy remain under BP-42.

## 17. Inputs, outputs and dependencies

**Inputs:** approved canon and requirements; source blueprint; crosswalk; division specifications; open decisions; glossary; schema registry; configuration; code/repository versions; migration proposals; impact assessments; tests/evidence; security/recovery/operational policies; user approvals.

**Outputs:** canonical version manifest; decision log; glossary; configuration schema/snapshots; change requests; impact assessments; approval records; migration/release manifests; deprecation/retirement records; change audit and status reports.

**Dependencies:** BP-01–BP-43. BP-44 coordinates controlled change across the project but does not replace domain owners or user approval.

## 18. Acceptance tests

The following criteria define required BP-44 coverage. They are design criteria only and have not been executed.

- CFG-AT-001: Exactly 44 blueprint divisions exist and their approved IDs, names and order match the master blueprint.
- CFG-AT-002: No division can be added, removed, reordered, split, merged or renamed without explicit user approval.
- CFG-AT-003: Every canonical requirement has a stable ID, authoritative wording, status and provenance.
- CFG-AT-004: The 52-division source remains preserved as source material and is not silently overwritten by the 44-division target.
- CFG-AT-005: Every source requirement and source test is mapped to one or more valid target divisions.
- CFG-AT-006: Crosswalk changes preserve all source IDs and make additions, removals, retargeting and rationale explicit.
- CFG-AT-007: Structural coverage reports do not claim semantic completeness without a requirement-by-requirement review.
- CFG-AT-008: Every semantic audit finding records source ID, issue, affected target, decision, rationale and evidence.
- CFG-AT-009: Ambiguous ownership is resolved by explicit owner and interface contract without dropping requirements.
- CFG-AT-010: Conflicting requirements are surfaced for decision and never silently reconciled.
- CFG-AT-011: Global canon constraints are available to every affected division and test.
- CFG-AT-012: Saltwater remains one sovereign city-state and one playable city/jurisdiction.
- CFG-AT-013: No change introduces a second city, external playable territory or territorial expansion.
- CFG-AT-014: The living-person cap remains exactly 10,000 across every represented role and data source.
- CFG-AT-015: Any population addition at cap requires a qualifying death or permanent exit under canon.
- CFG-AT-016: At least 10,000 businesses remain supported without creating additional people beyond the population cap.
- CFG-AT-017: Police simulation remains the deepest simulation; non-police institutions remain support-level unless approved.
- CFG-AT-018: Text remains the permanent primary interface and graphics remain optional.
- CFG-AT-019: Simulation time does not advance while the player is absent or the game is paused.
- CFG-AT-020: Relevant case-connected people are permanently promoted to full persistent simulation without duplicate identity.
- CFG-AT-021: Hidden offender/accomplice truth remains protected until the exact standalone case-sensitive `bingo` trigger.
- CFG-AT-022: No change may introduce unsolicited investigative hints or force player decisions.
- CFG-AT-023: Canonical values, policies and configurable values are distinguished from defaults and illustrative examples.
- CFG-AT-024: Unresolved configuration decisions remain explicitly open and cannot be treated as approved defaults.
- CFG-AT-025: Every configurable value has a stable key, type, scope, owner, default status, validation rule and provenance.
- CFG-AT-026: Configuration keys are namespaced and collision-free.
- CFG-AT-027: Configuration values have explicit allowed ranges, enumerations, units, nullability and cross-field constraints.
- CFG-AT-028: Invalid configuration is rejected before activation with actionable, non-sensitive diagnostics.
- CFG-AT-029: Configuration validation detects missing mandatory keys and incompatible combinations.
- CFG-AT-030: Configuration schema versions are explicit and migration paths are documented.
- CFG-AT-031: Configuration has separate development, test and authoritative runtime profiles.
- CFG-AT-032: Environment-specific overrides cannot silently change canonical rules.
- CFG-AT-033: Secrets and credentials are excluded from ordinary configuration files.
- CFG-AT-034: Configuration values that affect hidden truth or player-facing information pass through BP-42 controls.
- CFG-AT-035: Configuration changes are versioned and reproducible from repository history.
- CFG-AT-036: Each configuration snapshot identifies its source commit, schema version, environment and activation state.
- CFG-AT-037: Active configuration snapshots are immutable; edits create a new version.
- CFG-AT-038: Configuration rollback restores a prior valid snapshot without rewriting historical audit evidence.
- CFG-AT-039: Canonical blueprint versions have one designated authoritative location and immutable version identifier.
- CFG-AT-040: Blueprint metadata records version, status, owner, created time, approval time and supersession relation.
- CFG-AT-041: Proposed, reviewed, approved, implemented, verified, deprecated and retired states remain distinct.
- CFG-AT-042: Approval is attributable to the authorised decision-maker and cannot be inferred from silence.
- CFG-AT-043: Approval records identify exact artefact version and content hash.
- CFG-AT-044: Approval of a document does not imply implementation or deployment approval.
- CFG-AT-045: Implementation approval does not imply permission to write to Neon or change production.
- CFG-AT-046: Changes to canon, population cap, city boundary, business minimum, player agency or reveal rule require explicit user approval.
- CFG-AT-047: Changes to the 44-division structure require explicit user approval.
- CFG-AT-048: Changes to approved blueprint requirements require a recorded decision and impact assessment.
- CFG-AT-049: Editorial corrections that do not alter meaning are identified separately from semantic changes.
- CFG-AT-050: Typos and formatting changes preserve IDs, meaning, links and provenance.
- CFG-AT-051: Every proposed change has a stable change-request ID.
- CFG-AT-052: Change requests record requester, date, rationale, affected artefacts, affected requirements and proposed scope.
- CFG-AT-053: Change requests identify whether they are editorial, configuration, schema, data, code, canon, security or operational changes.
- CFG-AT-054: Change requests identify backward compatibility, migration, storage, security, privacy and recovery impacts as applicable.
- CFG-AT-055: Change requests identify affected divisions, interfaces, events, schemas, APIs, tests and user workflows.
- CFG-AT-056: Change requests include alternatives considered and reason for selection where material.
- CFG-AT-057: Change requests identify risks, failure modes, rollback or forward-recovery plan and verification criteria.
- CFG-AT-058: Changes with unresolved critical impact are blocked rather than silently approved.
- CFG-AT-059: Emergency changes have narrowly defined scope, rationale, expiry and retrospective review.
- CFG-AT-060: Emergency status cannot bypass user approval for canon changes or Neon writes.
- CFG-AT-061: Approval workflows enforce separation of requester, reviewer and approver where configured.
- CFG-AT-062: Self-approval is prohibited where independent approval is required.
- CFG-AT-063: Delegated approval is valid only within explicit scope and time.
- CFG-AT-064: Approval withdrawal or supersession is recorded and does not erase prior history.
- CFG-AT-065: Rejected and withdrawn changes remain discoverable with reasons and status.
- CFG-AT-066: Every material decision is recorded in a durable decision log.
- CFG-AT-067: Decision records include ID, question, options, selected outcome, rationale, authority, date and affected requirements.
- CFG-AT-068: Open decisions have an owner, required input, dependency and status.
- CFG-AT-069: Decision closure updates affected specifications, register, tests and traceability.
- CFG-AT-070: Decision records do not overwrite the source material or conceal superseded decisions.
- CFG-AT-071: A canonical glossary defines terms, abbreviations, status labels and ownership terminology.
- CFG-AT-072: Glossary terms have definitions, scope, synonyms and explicit distinctions.
- CFG-AT-073: Conflicting or overloaded terms are flagged and resolved through controlled decisions.
- CFG-AT-074: A schema registry identifies canonical entities, fields, types, constraints, relationships and owning divisions.
- CFG-AT-075: Each schema entry records version, status, compatibility, migration and provenance.
- CFG-AT-076: Only the owning division can propose domain meaning changes; BP-38 governs canonical data structure.
- CFG-AT-077: Cross-division fields and events have one authoritative owner and documented consumer contracts.
- CFG-AT-078: Schema IDs, event IDs, configuration keys and requirement IDs are not silently reused.
- CFG-AT-079: Deprecated fields and events have replacement references and retirement conditions.
- CFG-AT-080: API and event contract changes identify producers, consumers and compatibility impacts.
- CFG-AT-081: Breaking schema changes require migration, backup/recovery, test and rollback or forward-recovery plans.
- CFG-AT-082: Migration scripts are versioned, ordered, repeatable or safely guarded against duplicate application.
- CFG-AT-083: Migration preconditions and postconditions are explicit and testable.
- CFG-AT-084: Migration execution records exact commit, schema version, actor, time, environment and outcome.
- CFG-AT-085: Migration failure leaves authoritative state consistent or invokes a verified recovery plan.
- CFG-AT-086: No migration is executed against Neon without current baseline measurement and explicit approval.
- CFG-AT-087: Schema and data migration proposals quantify expected incremental storage in bytes and MB/MiB.
- CFG-AT-088: Storage estimates disclose method, assumptions, uncertainty and projected post-write total.
- CFG-AT-089: If estimates are not credible, representative benchmark is required before deployment.
- CFG-AT-090: After approved writes, actual database growth is measured and compared with estimate.
- CFG-AT-091: Database connection status is never inferred from repository state or stale measurements.
- CFG-AT-092: GitHub is the source-control/specification/migration-history platform as canonically selected.
- CFG-AT-093: Neon PostgreSQL is the persistent database as canonically selected.
- CFG-AT-094: ChatGPT remains the user-facing AI partner/interface as canonically selected.
- CFG-AT-095: Provider substitutions require explicit architecture/canon review and user approval where they change approved design.
- CFG-AT-096: External integrations have declared owner, purpose, scope, credential source, environment and revocation procedure.
- CFG-AT-097: Integration failure behaviour and data consistency boundaries are documented.
- CFG-AT-098: Configuration cannot silently authorize external side effects or real-world communications.
- CFG-AT-099: Development/test data is isolated from authoritative simulation data.
- CFG-AT-100: Test configuration cannot silently point to production credentials or databases.
- CFG-AT-101: Production configuration cannot be activated from an unreviewed development branch.
- CFG-AT-102: Branch, commit and release references are immutable and resolvable for every approved release.
- CFG-AT-103: Repository changes are reviewed and traceable to approved change requests.
- CFG-AT-104: Protected canonical artefacts cannot be overwritten without version history and approval.
- CFG-AT-105: Repository history and release tags preserve prior approved artefacts.
- CFG-AT-106: Generated or AI-proposed changes are treated as proposals until reviewed and approved.
- CFG-AT-107: AI cannot approve its own changes, change canon, grant itself authority or bypass workflow.
- CFG-AT-108: Prompt injection and untrusted source text cannot modify change-control policy.
- CFG-AT-109: Every AI-assisted change records human decision authority and exact diff scope.
- CFG-AT-110: Documentation links and cross-references resolve to existing artefacts.
- CFG-AT-111: Register entries match actual file paths, IDs, titles and current design/implementation/test/verification states.
- CFG-AT-112: Register history is chronological, unique and does not duplicate or contradict prior decisions.
- CFG-AT-113: Division specification status changes only when evidence for that status exists.
- CFG-AT-114: Every division retains purpose, scope, entities, lifecycle, rules, inputs/outputs, dependencies, permissions, edge cases, effects and acceptance tests.
- CFG-AT-115: Specification edits preserve all previously approved requirements unless explicitly amended.
- CFG-AT-116: Test IDs remain unique, sequential where required and linked to the exact specification version.
- CFG-AT-117: Test additions, removals and replacements retain historical results and rationale.
- CFG-AT-118: BP-43 acceptance evidence is required before implementation or release can be marked tested/verified.
- CFG-AT-119: Security-sensitive configuration changes receive BP-42 policy review and tests.
- CFG-AT-120: Persistence and recovery changes receive BP-38/BP-39 impact review and restore validation.
- CFG-AT-121: Simulation engine/time changes receive BP-35/BP-37 replay and pause/freeze impact tests.
- CFG-AT-122: Interface/report changes receive BP-40/BP-41 permissions and information-leak tests.
- CFG-AT-123: Police authority/career/discipline changes receive the relevant BP-05–BP-08/BP-30–BP-33 review.
- CFG-AT-124: Crime/case/evidence/legal lifecycle changes receive affected BP-13–BP-29 owner review.
- CFG-AT-125: Population and geography changes receive BP-02/BP-03/BP-04 invariant review.
- CFG-AT-126: Every change has an impact analysis identifying downstream dependencies and affected interfaces.
- CFG-AT-127: Change impact analysis includes people, businesses, cases, evidence, events, reports, permissions, persistence and player workflows where relevant.
- CFG-AT-128: Every changed invariant has positive, negative and boundary tests.
- CFG-AT-129: Every migration has isolated test execution before authoritative deployment.
- CFG-AT-130: Rollback or forward recovery is rehearsed where failure could affect authoritative data.
- CFG-AT-131: Data correction preserves original value, reason, actor, authority, timestamp and lineage.
- CFG-AT-132: Historical facts are never silently rewritten to match current configuration.
- CFG-AT-133: Derived views and caches are rebuilt or invalidated after relevant approved changes.
- CFG-AT-134: Configuration activation is atomic or has a safe, documented partial-failure strategy.
- CFG-AT-135: Configuration activation records exact snapshot and activation boundary.
- CFG-AT-136: Concurrent changes cannot overwrite one another without conflict detection.
- CFG-AT-137: Stale approvals cannot authorize a changed artefact hash.
- CFG-AT-138: Expired approvals and temporary exceptions cannot be reused.
- CFG-AT-139: User approval is specific to the exact operation, scope, artefact and measured write estimate.
- CFG-AT-140: No Neon write, migration, seed/import, bulk write, upload or credential change occurs without explicit user approval.
- CFG-AT-141: Approval for one write does not imply approval for later writes or larger scope.
- CFG-AT-142: Any material difference from the approved write estimate requires renewed approval before proceeding.
- CFG-AT-143: Post-write measurements and variance are recorded after each approved database operation.
- CFG-AT-144: Operational procedures identify responsible owner, prerequisites, execution steps, validation and recovery.
- CFG-AT-145: Maintenance windows and service interruptions are declared before operational changes where relevant.
- CFG-AT-146: Operational changes preserve pause semantics and do not advance in-world time while player absent.
- CFG-AT-147: Monitoring and audit retain enough provenance to reconstruct configuration and change history.
- CFG-AT-148: Change-related incidents are linked to change request, release, migration and affected records.
- CFG-AT-149: Security incidents or data integrity failures can trigger change freeze and controlled recovery.
- CFG-AT-150: Change freeze scope and release authority are explicit and time-bounded.
- CFG-AT-151: Retirement of a configuration or schema element checks for dependent records and consumers.
- CFG-AT-152: Retired artefacts remain auditable and recoverable under retention policy.
- CFG-AT-153: Canonical blueprint and schema registry have validated backups and recovery evidence.
- CFG-AT-154: Restoring prior configuration does not silently roll back valid newer domain records.
- CFG-AT-155: Quality gates block activation when mandatory tests, approvals or impact reviews are missing.
- CFG-AT-156: Release readiness is distinct from design approval, implementation completion and operational verification.
- CFG-AT-157: Every implementation item traces to an approved requirement and test evidence.
- CFG-AT-158: Every completed change can be independently reconstructed from repository history, decision log and evidence.
- CFG-AT-159: Change-control reports distinguish proposed, approved, rejected, implemented, verified and retired changes.
- CFG-AT-160: Every unresolved open decision is visible in the register and cannot be mistaken for settled policy.
- CFG-AT-161: All source traceability IDs assigned to BP-44 are present and their original wording remains unchanged.

## 19. Source traceability

The following source requirements/tests are mapped to BP-44 by the authoritative 52→44 crosswalk. Original wording is copied from the unchanged source JSON.

| Source ID | Source division | Original requirement/test wording |
|---|---|---|
| S01.R01 | Sovereignty, jurisdiction and constitutional order | Define Saltwater's sovereign status, territory boundary, jurisdiction, institutions, powers, succession and constitutional rules. |
| S01.R02 | Sovereignty, jurisdiction and constitutional order | Define legal hierarchy, authority sources, emergency powers, separation of functions and jurisdictional limits. |
| S01.R03 | Sovereignty, jurisdiction and constitutional order | Prevent external-city or territorial expansion. |
| S01.T01 | Sovereignty, jurisdiction and constitutional order | Every location resolves inside the single Saltwater jurisdiction or is explicitly marked off-map. |
| S01.T02 | Sovereignty, jurisdiction and constitutional order | No institution exercises undefined authority. |
| S12.R01 | Civil registry and public records | Maintain civil status, identity, address, property, business, permits and other canonically required registers. |
| S12.R02 | Civil registry and public records | Track corrections, versions, issuing authority, access and provenance. |
| S12.R03 | Civil registry and public records | Support lawful in-world retrieval and controlled disclosure. |
| S12.T01 | Civil registry and public records | Record changes preserve prior values and reason for change. |
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

## 20. Open configuration and implementation decisions

1. Canonical blueprint versioning and approval metadata format.
2. Machine-readable requirement, decision, glossary and crosswalk schemas.
3. Configuration key namespace, schema format and validation engine.
4. Environment profile and promotion workflow.
5. Change request taxonomy, templates and lifecycle automation.
6. Approval roles, separation-of-duties matrix and user approval capture.
7. Schema registry and event/API compatibility policy.
8. Migration tooling, transaction strategy and recovery method.
9. GitHub branch protection, review requirements and release/tag policy.
10. Neon baseline and storage measurement queries and benchmark dataset.
11. Evidence retention and immutable audit implementation.
12. Decision-log and glossary ownership and review cadence.
13. Emergency change and change-freeze authority and expiry.
14. Release manifest and operational handover format.
15. Deprecation periods and compatibility support windows.
16. Automated link/register/crosswalk validation and CI quality gates.
17. Configuration activation atomicity and rollback mechanism.

## 21. Completion status

- Specification: DESIGNED_DRAFT; review/approval pending.
- Implementation: NOT_STARTED.
- Test execution: NOT_STARTED; acceptance criteria are not executed evidence.
- Verification: NOT_STARTED.
- No Neon writes, migrations, seed/import, bulk operations, uploads, credential changes or production deployments have been performed or authorised by this work.
- BP-44 is the final division in the fixed 44-division blueprint. The next work is whole-blueprint semantic audit, gap resolution, cross-division consistency review and then explicit implementation planning; no new division is implied.