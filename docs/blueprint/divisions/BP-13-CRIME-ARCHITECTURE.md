# BP-13 — Crime Architecture

**Project:** Saltwater — fictional sovereign city-state; one city, one jurisdiction  
**Blueprint division:** BP-13 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test:** NOT_STARTED | **Verification:** NOT_STARTED

## 1. Purpose

BP-13 defines Saltwater's authoritative crime and non-crime incident classification architecture: the taxonomy, category hierarchy, offence concepts, offence elements, classification states, severity dimensions, location and context attributes, classification decisions, reporting routes, and controlled relationships between reported conduct and formal crime records.

It establishes a consistent vocabulary for the police simulation while preserving uncertainty and procedural distinctions. A reported occurrence is not automatically a crime; a crime allegation is not proof; a classification is not a finding of guilt; intelligence is not evidence merely because it is stored; a suspect designation is not a conviction; and a court outcome does not rewrite what was known at an earlier point in time.

BP-13 owns the crime taxonomy and classification rules. BP-12 owns operational incident records and their lifecycle. BP-14 owns generation of simulated occurrences and their causal truth. BP-15 owns case records and investigative lifecycle. BP-17 owns victim/witness case roles. BP-18 owns suspect/offender status. BP-21 owns intelligence records. BP-27 and BP-28 own legal process and court outcomes. This division defines the interfaces without absorbing those domains.

The taxonomy must be broad enough to support varied crime and non-crime activity across Saltwater's people, businesses, organisations, property and infrastructure. It must be extensible through controlled configuration without silently changing historical classifications or altering the fixed 44-division blueprint.

## 2. Scope and boundaries

### 2.1 In scope
- Canonical crime and non-crime classification taxonomy.
- Hierarchical category, subcategory, offence-concept and descriptor model.
- Offence elements and structured element assessments.
- Distinction between conduct, occurrence, report, allegation, incident, offence concept, intelligence, evidence, finding and legal outcome.
- Classification status, confidence, uncertainty, source basis and decision history.
- Crime and non-crime classification workflows and reporting routes.
- Multiple classifications and multiple offences arising from one occurrence.
- One classification or alleged offence linked to multiple reports/incidents/cases where justified.
- Location, context, victim, suspect, witness, method, harm and impact descriptors as references or structured attributes.
- Severity and harm dimensions, kept distinct from incident priority and legal seriousness.
- Classification review, correction, declassification, reclassification, duplicate and series relationships.
- Taxonomy versioning, effective dates, deprecation, migration and historical reproducibility.
- Search, reporting, aggregation, taxonomy governance and acceptance testing.
- Interfaces to occurrence generation, incident management, case management, investigation, intelligence, people, evidence and legal domains.

### 2.2 Explicitly out of scope
- Generation of hidden occurrence truth, offender identity, accomplices, motive or event outcomes: BP-14.
- Police incident intake, CAD, dispatch and incident operational status: BP-11/BP-12.
- Case creation, ownership, investigative lifecycle and case closure: BP-15.
- Investigative tasks and investigative conclusions: BP-16.
- Victim and witness case roles, support and safeguarding case records: BP-17.
- Suspect, person-of-interest and offender status: BP-18.
- Interview/interrogation records: BP-19.
- Surveillance records: BP-20.
- Intelligence collection, source handling, assessment and intelligence products: BP-21.
- Scene control and scene records: BP-22.
- Exhibit records, continuity and chain of custody: BP-23.
- Forensic examination and results: BP-24.
- Arrests, warrants, custody, legal proceedings, court decisions and corrections: BP-25 through BP-29.
- Global person identity, population and permanent promotion: BP-03.
- Canonical geography, road network and spatial identifiers: BP-02.
- Property, business, organisation and infrastructure master records: BP-04.
- Formal department policy approval and governance: BP-30.
- Simulation event generation and execution: BP-35.
- Shared clock and scheduling: BP-37.
- Shared records, persistence, permissions and change control: BP-38, BP-39, BP-42 and BP-44.

### 2.3 Authority rule
BP-13 is authoritative for the meaning, identity, structure, version and classification rules of taxonomy entries and classification decisions. It is not authoritative for whether an event actually happened, who committed it, whether a person is guilty, what evidence proves, or what a court decided. Those facts remain with their originating domains and must be referenced with provenance.

## 3. Foundational terminology and distinctions

The system must preserve these separate concepts:

| Concept | Meaning | Authority |
|---|---|---|
| Conduct/event | Something that may have happened in the simulated world | BP-14 or source domain |
| Occurrence | A generated or reported event instance with causal and temporal identity | BP-14 |
| Report | An account submitted by a person, organisation or system | Source domain / BP-12 |
| Incident | An operational occurrence/concern managed by police | BP-12 |
| Allegation | An assertion that conduct occurred or a person did something | Originating report / linked record |
| Crime category | A broad taxonomy grouping | BP-13 |
| Offence concept | A defined classification concept with versioned elements | BP-13 |
| Classification | An attributed decision applying a taxonomy concept to available information | BP-13 |
| Intelligence | Information assessed for intelligence purposes | BP-21 |
| Evidence | Material handled under evidential rules | BP-22/BP-23/BP-24 |
| Investigative assessment | An assessment reached during investigation | BP-16 |
| Suspect status | A case role/status assigned under defined criteria | BP-18 |
| Charge/legal allegation | A formal legal-process action | BP-27 |
| Adjudicated finding | A court determination | BP-28 |
| Sentence/correctional outcome | Post-conviction disposition | BP-29 |

No user interface, NPC dialogue, generated report or API may use these terms interchangeably. A classification may be provisional, disputed, revised or withdrawn. A court acquittal does not prove that the original report was knowingly false; a conviction does not retroactively make earlier uncertain information certain.

## 4. Taxonomy architecture

### 4.1 Taxonomy layers
The taxonomy should support the following conceptual layers. The exact initial catalogue is a controlled content decision and must be populated through versioned data, not hard-coded into application logic.

1. **Domain family:** broad grouping such as violence, property, deception, sexual harm, exploitation, public order, cyber/digital conduct, drugs/controlled substances, weapons-related conduct, environmental harm, traffic/transport, public safety, organised activity, financial/economic conduct, offences against institutions, and non-crime operational categories.
2. **Category:** a meaningful grouping within a domain family.
3. **Subcategory:** a more specific class used for routing, analysis and reporting.
4. **Offence concept:** a defined offence or alleged-offence concept with a stable taxonomy ID and version.
5. **Variant/qualifier:** contextual modifier such as attempt, conspiracy, aggravated circumstance, protected target, location context or method, where approved.
6. **Descriptor:** non-dispositive tags for method, setting, instrument, relationship context, harm, vulnerability, digital component or modus-operandi feature.
7. **Reporting route:** the operational and specialist routing guidance associated with a classification, without directly dispatching resources or assigning a case.

The taxonomy must not force every event into a formal offence concept. Non-crime categories and undetermined states are first-class supported outcomes.

### 4.2 Stable identifiers
Every taxonomy entry receives a stable, unique, non-reusable identifier independent of its display name, position or parent. A rename or move does not change its identity. A materially different legal or semantic meaning requires a new version or new identifier according to the change rules. IDs must not encode hidden offender truth, sensitive personal data or assumptions about guilt.

### 4.3 Taxonomy entry fields
Each entry must support:
- stable taxonomy ID;
- entry type and layer;
- parent/child references;
- canonical name and approved aliases;
- concise definition and inclusion criteria;
- exclusion criteria and boundary examples;
- offence-concept elements, where applicable;
- jurisdiction applicability and territorial scope;
- effective-from and effective-to times;
- status: draft, active, deprecated, superseded or withdrawn;
- severity/harm descriptors, if defined;
- reporting-route and specialist capability references;
- version and predecessor/successor links;
- author, approver, source basis and change rationale;
- locale/language display strings;
- tags and search synonyms;
- compatibility/migration notes;
- review date and owner.

### 4.4 Hierarchy integrity
A taxonomy entry may have one canonical parent unless an explicit multi-parent classification model is approved. Acyclic hierarchy is mandatory. Parent retirement must not silently retire active children. Every active offence concept must be reachable from an active category. Aliases must resolve to one or more explicitly disambiguated entries and must never create duplicate identities.

### 4.5 Broad coverage
The taxonomy must support serious, minor, emerging, organised, opportunistic, digital, financial, interpersonal, property, environmental, public-safety and non-criminal occurrences. It must support attempted, completed, interrupted, continuing, repeated and uncertain conduct where the concept permits. It must not be limited to a small fixed list of common offences or force novel conduct into an inaccurate category.

### 4.6 Non-crime categories
Non-crime categories include, as policy/configuration requires, welfare and safeguarding concerns, missing-person reports, sudden death attendance, accidents, public safety hazards, service disruption, civil disputes, lost/found property, suspicious circumstances without a substantiated offence, false alarms, requests for assistance and other police-managed events. These are operational taxonomy concepts, not necessarily incidents of criminal conduct. They remain available to BP-12 without manufacturing an offence classification.

## 5. Offence concepts and elements

### 5.1 Offence concept
An offence concept represents a defined classification construct. It may describe a statutory offence in the fictional jurisdiction, a common-law concept if the game's approved legal model uses one, or a generic offence class for a non-legal simulation layer. The initial Saltwater legal catalogue must be approved through BP-30/BP-44 policy and configuration. This draft does not invent a real-world legal code or import another jurisdiction's law by assumption.

### 5.2 Elements model
Where an offence concept has elements, each element must be individually represented with:
- element ID and version;
- plain-language definition;
- element type (conduct, circumstance, result, mental state, status, relationship or other approved type);
- required/optional/alternative designation;
- logical grouping (all, any, one-of, conditional);
- relevant time and territorial scope;
- source basis and interpretation notes;
- evidence/information types that may be relevant, without implying proof;
- exclusion/defence/exception references where modelled;
- uncertainty and assessment status.

The model must support compound elements, alternative pathways, conditional elements and aggravating/mitigating qualifiers. It must not assume that every offence can be represented as a flat checklist.

### 5.3 Element assessment states
An element assessment may be:
- not considered;
- information not available;
- alleged;
- supported by reported information;
- supported by an identified source;
- disputed;
- contradicted;
- assessed as not present;
- requires further assessment;
- determined by an authorised legal/court process, if a linked legal finding explicitly supports it.

These are information states, not a guilt score. The system must preserve assessor, source references, time, rationale, confidence and version. Do not convert a repeated allegation into corroboration merely because it appears in multiple derivative records.

### 5.4 Attempt, preparation and completion
Support attempt, incomplete, interrupted, completed, continuing, repeated and unknown status only where the relevant offence concept and approved policy permit. Do not infer attempt from failure to complete an outcome. Do not infer completion from harm alone. Preserve factual conduct descriptors separately from legal characterisation.

### 5.5 Multiple and alternative offences
A single occurrence may be associated with multiple possible offence concepts, including alternatives that cannot all ultimately apply. The system must preserve each considered classification and its status. It must not force a single label where facts are incomplete or several legal interpretations remain possible. Duplicate classifications should be linked and resolved through an auditable decision, not deleted.

## 6. Classification workflow and decision record

### 6.1 Classification stages
A classification workflow may include:
1. Unclassified/awaiting assessment.
2. Initial broad operational category.
3. Provisional offence concept(s) considered.
4. Element-by-element assessment as information becomes available.
5. Supervisor or specialist review where policy requires.
6. Confirmed operational classification for current reporting purposes.
7. Reclassification, withdrawal, supersession or closure with retained history.
8. Legal-process/court outcome linked from BP-27/BP-28 without rewriting prior assessments.

Not every record must pass through every stage. A non-crime event may remain non-crime. A low-information report may remain unclassified while BP-12 still responds.

### 6.2 Required decision fields
Every classification decision must record:
- classification decision ID;
- target incident, occurrence, case or other permitted source reference;
- taxonomy entry ID and exact version;
- classification status;
- decision-maker or service identity;
- decision authority/role;
- decision time and effective time;
- information cut-off or snapshot reference;
- source records and relevant element assessments;
- rationale and uncertainty;
- confidence descriptor, where used;
- review trigger and due point, if configured;
- prior decision and supersession link;
- dispute/challenge state;
- approval/review record where required.

### 6.3 Initial classification
Initial classification is provisional unless an approved policy explicitly defines a particular low-risk administrative category as final for its limited purpose. The user-facing display must clearly label provisional/uncertain classifications. A classification is not a finding that an offence occurred or that any named person committed it.

### 6.4 Reclassification
Reclassification creates a new decision referencing the prior decision, reason, new taxonomy version and information available at the time. It must not erase prior classifications. If a category is split or merged, preserve a traceable mapping from old to new concepts and flag cases where a one-to-one migration is impossible.

### 6.5 Withdrawal and no-crime outcome
A classification may be withdrawn or a report may be assessed as no crime apparent, non-criminal, unfounded under an explicitly defined evidential/administrative meaning, mistaken, duplicate or undetermined. These outcomes are not interchangeable. A no-crime outcome must record why and what scope was assessed. It does not automatically mean that the reporter lied or that no harmful event occurred.

### 6.6 Review and challenge
Authorised users may request review or challenge a classification. The challenge must be linked to the exact decision, identify grounds and preserve the original. Reviewers must have appropriate authority and must record whether the decision is upheld, amended, withdrawn or referred. A challenge does not automatically suspend urgent safety action.

## 7. Severity, harm and impact model

### 7.1 Separate dimensions
Do not collapse crime seriousness, actual harm, potential harm, incident priority, public risk, evidential strength and legal outcome into one score. They are different questions owned by different decision contexts.

The taxonomy may define descriptors or structured scales for:
- physical injury and threat to life;
- psychological/emotional harm;
- sexual harm;
- financial/economic loss;
- property damage or loss;
- coercion, exploitation and loss of autonomy;
- disruption to essential services or business operations;
- environmental damage;
- community/public impact;
- duration, recurrence and scale;
- vulnerability and safeguarding context;
- potential future harm.

### 7.2 Severity rules
Severity scales, labels, weighting and thresholds are configuration/policy decisions. This draft does not set arbitrary numeric weights or response thresholds. Every score or band must identify its model/version, inputs, assessor, time and limitations. Unknown harm is not zero harm. Lack of a reported injury does not prove absence of harm.

### 7.3 Link to incident priority
BP-12 owns operational priority and response urgency. BP-13 supplies taxonomy descriptors and any approved classification-related severity metadata. A severe offence concept does not automatically dictate dispatch priority; a lower-level offence concept can involve an immediate threat. BP-12 must remain able to override an automated suggestion with a reasoned operational assessment.

## 8. Context, method and descriptive attributes

### 8.1 Structured descriptors
Support descriptive attributes such as:
- alleged method and modus operandi;
- attempt/completion status;
- location type and setting;
- time pattern and duration;
- instrument or mechanism;
- digital/online/offline component;
- relationship context;
- target/property/business/infrastructure class;
- harm/impact dimensions;
- group/series indicators;
- concealment, access or opportunity descriptors;
- reported motive, explicitly marked as reported or assessed rather than fact;
- vulnerability or safeguarding context;
- cross-domain hazards and dependencies.

Descriptors are not necessarily taxonomy categories and must not be promoted into offence labels without an authorised mapping.

### 8.2 Controlled vocabularies
Use versioned controlled vocabularies for common descriptors while allowing attributed free-text detail. A new descriptor value must not be silently invented by an NPC or imported source. Unknown/unmapped values remain preserved and flagged for taxonomy review.

### 8.3 Method versus identity
Method, instrument, location, relationship or signature similarity must never be treated as proof of offender identity. A modus-operandi association is an analytical lead, not a confirmed common perpetrator. BP-21 owns intelligence assessment and BP-16 owns investigative assessment.

## 9. Victims, witnesses, suspects and other people

BP-13 may describe which roles or person dimensions are relevant to a classification, but it does not assign authoritative person roles.

- BP-03 owns canonical person identity, population status and permanent promotion of materially relevant people.
- BP-17 owns victim and witness case roles, safeguarding/support details and role history.
- BP-18 owns suspect, person-of-interest and offender statuses.
- BP-19 owns interview and interrogation records.
- BP-21 owns intelligence-source and subject assessment records.

A person may occupy several roles in different contexts or at different times. A caller is not automatically a victim; a victim is not automatically a witness; a witness is not automatically a suspect; a suspect is not an offender finding; and an offender label must not be treated as conviction unless supported by BP-28. A person mentioned in a taxonomy descriptor is only a reference to the canonical identity, never a duplicate person record.

Any person who becomes materially connected to the occurrence, incident, crime or related police activity is permanently promoted under BP-03's full-simulation rule. This applies to minor but material connections. BP-13 must invoke/reference that promotion process idempotently and must not create identities outside the global 10,000 living-person cap.

## 10. Location, jurisdiction and territorial scope

### 10.1 Canonical geography
Use BP-02 spatial identifiers for locations, boundaries, premises, roads and zones. Retain the source location description and uncertainty. BP-13 must not create duplicate addresses, streets, buildings or external playable territory.

### 10.2 Jurisdiction
Saltwater is one sovereign city-state, one city and one police jurisdiction. Classification applicability is determined against the approved Saltwater jurisdiction model. External conduct may be represented as context or a referenced external event only where approved; it does not create another playable city or jurisdiction.

### 10.3 Location attributes
A classification may carry location type, public/private access, premises type, transport context, digital/remote context, multiple sites or unknown location. A location descriptor does not determine guilt or prove presence. Digital conduct may have affected persons or systems in Saltwater without inventing an off-map physical scene.

### 10.4 Territorial uncertainty
If the location or jurisdiction is uncertain, preserve that uncertainty and refer to BP-02/BP-30 policy. Do not force a classification into Saltwater solely because the reporting person is located there.

## 11. Reporting routes and operational use

### 11.1 Route metadata
Taxonomy entries may reference:
- initial intake/triage route;
- specialist capability or unit type;
- safeguarding referral;
- intelligence assessment route;
- scene/evidence preservation consideration;
- case referral consideration;
- partner-service coordination;
- required supervisor review;
- mandatory notification or audit trigger.

These are advisory/configured workflow references. BP-13 does not dispatch a unit, open a case, assign a suspect, collect evidence or notify an external body itself.

### 11.2 Route conditions
A route may depend on the current classification, risk, location, vulnerability, time, resource availability or policy. Route rules must expose version, trigger, recipient domain and expected acknowledgement. If a receiving domain rejects a referral, BP-13 preserves the rejection and does not claim that the action occurred.

### 11.3 No automatic guilt inference
A routing rule based on a category or descriptor must not imply that a person is guilty, that an allegation is substantiated, or that an offence element is proved. It may indicate a precautionary capability or safeguarding need only.

## 12. Relationship to occurrence generation and hidden truth

### 12.1 BP-14 boundary
BP-14 generates simulated occurrences, including causal event facts and concealed ground truth. BP-13 provides the taxonomy against which reports or occurrences may be classified. A generated occurrence may have an underlying truth that the player, an officer NPC or a classifier has not discovered. BP-13 must not expose generator-only truth through classification labels, IDs, metadata, analytics, error messages, suggestions or hidden fields.

### 12.2 Information available at classification time
Every decision is based only on information available to its decision-maker at the time. A generated event's hidden truth may be used by the simulation engine to ensure causal consistency, but it must not be included in officer-facing classification inputs unless discovered through a permitted in-game process.

### 12.3 Variation and plausibility
Taxonomy breadth must allow BP-14 to generate varied crime and non-crime occurrences grounded in people, relationships, businesses, property, organisations, schedules and city context. BP-13 does not choose the culprit, motive, event chronology or occurrence outcome. It supplies stable semantic categories and valid classification constraints.

### 12.4 No solution hints
Player-facing taxonomy, classification history, reports and NPC statements must not disclose a hidden offender or accomplice identity unless the player enters exactly `bingo`. They must not indirectly reveal it through unusually specific taxonomy choices, unique labels, generated IDs, category metadata or explanatory hints.

## 13. Crime series, links and aggregation

### 13.1 Classification relationships
Support explicit relationships such as:
- same taxonomy concept;
- alternative possible classification;
- included/lesser/greater offence concept where approved;
- multiple offences in one occurrence;
- related occurrence;
- suspected series;
- confirmed series under authorised assessment;
- reclassified from/to;
- supersedes/superseded by;
- duplicate classification;
- linked legal charge or court outcome.

Every relationship records type, direction where applicable, creator, time, rationale, confidence and source. Similarity alone does not prove a series or common offender.

### 13.2 Series authority
BP-13 may define a taxonomy-level series classification or relationship vocabulary. BP-21 owns intelligence products and BP-16 owns investigative conclusions about links. A suspected series is not a confirmed common perpetrator. Court findings are linked from BP-28 and remain separately attributable.

### 13.3 Aggregation rules
Reports must state whether they count reports, incidents, occurrences, alleged offences, provisional classifications, confirmed classifications, charges or adjudicated findings. Do not combine these into a single crime count. Deduplication rules must be explicit, reproducible and versioned.

## 14. Taxonomy governance, versioning and change control

### 14.1 Controlled lifecycle
Taxonomy entries move through configured states such as draft, review, approved, active, deprecated, superseded and withdrawn. Only authorised governance roles may approve changes under BP-30/BP-44. A content author cannot self-approve a change unless policy explicitly permits it and the audit records the exception.

### 14.2 Version rules
A taxonomy version is immutable after publication. A correction that changes meaning creates a new version or successor entry; it does not overwrite the historical version. Every classification stores the exact taxonomy version used. Historical queries must reproduce the classification as understood at decision time.

### 14.3 Effective dating
Support effective-from and effective-to timestamps. A classification decision must use the taxonomy version applicable under the approved temporal rule. The system must not automatically reclassify historical records merely because a new taxonomy version becomes active.

### 14.4 Deprecation and migration
Deprecating an entry prevents new use where policy says so but does not delete prior decisions. Migrations require a mapping table, rationale, approval, dry-run report, conflict list and rollback/reversal path. One old concept may map to several new concepts or vice versa; ambiguous mappings require human review and cannot be silently guessed.

### 14.5 Change impact
Before publication, identify affected incidents, cases, reports, analytics, generation constraints, routes, training materials and interfaces. Existing records retain their original classification snapshot. Any migration is separately versioned and auditable.

## 15. NPC and AI classification behaviour

### 15.1 Role and competence
NPC classifiers act according to their role, training, authority, workload, knowledge, access and available information. They may use only taxonomy versions and policy available to them at the time. A junior or untrained NPC cannot make a restricted formal classification solely because a model suggests it.

### 15.2 Uncertainty and mistakes
NPCs may make plausible mistakes, disagree, delay, use broad categories or request review. Consequential decisions are recorded with rationale and source basis. Do not manufacture random misclassification without a plausible cause such as incomplete information, ambiguity, workload or training gap.

### 15.3 AI assistance
AI may suggest candidate categories, identify missing elements, detect inconsistent labels or propose review. Suggestions must be clearly marked as machine-generated, include model/rule version and supporting inputs, and never become authoritative without the required human or policy-controlled acceptance. AI must not invent facts, sources, evidence or legal elements.

### 15.4 Knowledge boundaries
An NPC or AI process must not use concealed BP-14 ground truth unless its explicit simulation role is the omniscient engine and the output remains inaccessible to player-facing or operational decision systems. Prevent hidden fields from leaking through logs, explanations, exports, search, notifications and error payloads.

## 16. Interfaces and ownership contracts

### 16.1 Inputs
BP-13 accepts validated references and events from:
- BP-12: incident creation/update, operational descriptions and classification requests;
- BP-14: occurrence references and permitted classification metadata, excluding hidden truth from operational views;
- BP-15: case-linked classification review requests and case references;
- BP-16: investigative assessment references, findings and source links;
- BP-17/BP-18: role references and status changes only as needed for classification context;
- BP-21: intelligence references or assessed descriptors with source/provenance labels;
- BP-27/BP-28: formal charge and adjudicated outcome references;
- BP-02/BP-03/BP-04: canonical location, person, business and organisation references;
- BP-30/BP-44: approved taxonomy policy and configuration changes;
- BP-35/BP-37: simulation event and shared time references.

Inputs are schema-validated, versioned, source-attributed and idempotent. No inbound domain may overwrite taxonomy definitions or classification decisions without the BP-13 workflow.

### 16.2 Outputs
BP-13 publishes:
- taxonomy entry/version and lifecycle events;
- classification created, reviewed, changed, withdrawn and superseded events;
- element assessment and rationale references;
- classification-to-incident/occurrence/case links;
- reporting-route recommendations;
- taxonomy deprecation and migration notices;
- review-required and unresolved-classification flags;
- analytics projections with explicit counting basis.

### 16.3 Event envelope
Every cross-domain event includes event ID, schema version, event type, source domain and record ID, target/reference IDs, taxonomy ID/version where relevant, canonical event time, recorded time, correlation ID, idempotency key, actor/service identity, access classification and provenance. Consumers must tolerate duplicate, delayed and reordered delivery. Rejected events must return actionable errors without partial mutation.

### 16.4 Ownership and reconciliation
BP-13 owns taxonomy and classification records. Source domains retain their source records. A mismatch is resolved by reconciliation or a new classification decision, not by editing the source domain's data. Reconciliation reports missing, stale, invalid or conflicting references and preserves the original source values.

## 17. Data model and record contracts

### 17.1 Core entities
The design must support at least:
- TaxonomyCatalogue;
- TaxonomyVersion;
- TaxonomyEntry;
- TaxonomyRelationship;
- OffenceConcept;
- OffenceElement;
- ElementAssessment;
- ClassificationDecision;
- ClassificationTargetLink;
- ClassificationDescriptor;
- ClassificationRelationship;
- ReportingRouteRule;
- TaxonomyChangeProposal;
- TaxonomyApproval;
- TaxonomyMigration;
- ClassificationReview;
- TaxonomyAuditEvent.

### 17.2 Classification record
Minimum fields:
- classification ID and version;
- target type and target ID;
- taxonomy entry ID and version;
- decision state and effective period;
- classification source and decision-maker;
- authority/role;
- created/recorded/effective timestamps;
- source snapshot/reference set;
- element assessments;
- descriptors and qualifiers;
- uncertainty/confidence;
- rationale;
- review/challenge state;
- predecessor/successor references;
- audit and access classification.

### 17.3 Reference integrity
All person, organisation, property, location, incident, occurrence, case, evidence, intelligence, charge and court references must resolve to valid owning-domain IDs or be explicitly marked unresolved/pending. BP-13 must not create shadow copies of those entities. Invalid references are rejected or quarantined with a visible reason.

### 17.4 Append-only history
Published taxonomy versions and classification decisions are immutable. Corrections are new events or versions. Preserve the source statement, original classification, decision-maker and the information available at the time. No physical deletion is a normal classification lifecycle action.

## 18. Permissions and sensitive information

BP-42 owns permission enforcement. Support separate permissions for taxonomy view, propose, edit draft, approve, publish, deprecate, migrate, classify, review, withdraw, export and audit.

- Access to a classification does not grant access to all linked source records.
- Sensitive victim, witness, suspect, health, intelligence and safeguarding details remain in their owning restricted domains.
- A general incident view receives only the minimum permitted classification summary.
- Taxonomy administrators cannot inspect hidden occurrence truth merely because they administer taxonomy.
- AI services have scoped service identities and may not bypass role-based or attribute-based restrictions.
- Bulk export, search and analytics must enforce the same access constraints as individual record access.
- Break-glass access, if configured, records reason, scope, duration and post-event review.

## 19. Reporting, search and analytics

Provide:
- taxonomy catalogue browsing by hierarchy, aliases, effective date and status;
- classification search by ID, taxonomy entry/version, status, target reference and time;
- provisional/unreviewed/disputed classifications;
- element assessments with unresolved or contradicted items;
- reclassification and withdrawal history;
- crime/non-crime classification trends;
- occurrence/report/incident/offence/case/charge/court-outcome counts separately;
- taxonomy usage and deprecated-entry usage;
- classification quality and review workload;
- routing recommendations and referral outcomes;
- series/relationship views with confidence and authority.

Every report must identify taxonomy version, time basis, filters, deduplication logic and counting unit. Analytics cannot expose hidden generator truth or restricted person details. A chart or map is a derived presentation; the text records remain complete and authoritative.

## 20. Error handling and degraded operation

Handle missing taxonomy versions, invalid entries, ambiguous aliases, unknown descriptor values, conflicting classification decisions, unavailable source domains, stale references, duplicate events, access denial, clock anomalies, failed migrations and partial storage outages.

- If classification cannot be completed, retain the request in an explicit pending/unclassified state.
- Do not block urgent BP-12 response merely because BP-13 is unavailable.
- Do not substitute a guessed taxonomy entry when a reference is invalid or ambiguous.
- Preserve unknown or unmapped source descriptors for later review.
- A failed publication or migration must not partially activate a taxonomy version.
- A failed classification update must leave the prior decision intact.
- Retries are idempotent and must not create duplicate classifications.
- Stale or unavailable source information is visibly marked.
- All errors identify the responsible domain, failed reference and safe recovery path without exposing protected data.

## 21. Time, persistence and scale

- BP-37 is the sole shared simulation clock; BP-35 owns event execution.
- All taxonomy effective dates and classification timestamps use the shared time contract.
- When the player exits or pauses the simulation, simulation time freezes. Scheduled classification reviews, expiry, NPC work, migration jobs, route triggers and analytics refreshes do not advance.
- On resume, continue from the exact persisted state; do not catch up wall-clock time or create absence-time classifications.
- Taxonomy publication and classification changes are atomic with their audit events.
- Stable IDs, immutable versions and compact references support long-lived records without deleting semantic information.
- Taxonomy size is driven by the approved catalogue; no arbitrary small maximum may prevent broad coverage.
- Saltwater remains one city and one jurisdiction; the population hard cap is 10,000 living people, counted once globally. BP-13 must not create person identities.
- At least 10,000 businesses remain represented under BP-04; taxonomy links reuse their canonical IDs.
- Deep police simulation is preserved while other institutions and service domains are represented proportionately.

## 22. Acceptance criteria

1. Taxonomy entries have stable, unique, non-reusable IDs and immutable published versions.
2. Hierarchy is valid, acyclic and supports controlled aliases and descriptors.
3. Crime and non-crime categories are both first-class.
4. Offence concepts support structured, versioned elements and logical relationships.
5. Classification decisions identify target, taxonomy version, authority, source basis, time and rationale.
6. Report, occurrence, incident, allegation, offence, intelligence, evidence, suspect status, charge and court finding remain distinct.
7. Initial classification can remain provisional or undetermined.
8. Multiple possible classifications and multiple offences per occurrence are supported.
9. Reclassification and withdrawal preserve all prior decisions.
10. Severity, harm, incident priority, evidential strength and legal outcome remain separate.
11. Reporting routes are advisory/configurable and do not impersonate dispatch or case creation.
12. BP-14 hidden truth cannot leak through operational classifications or metadata.
13. Person roles remain owned by BP-17/BP-18 and canonical identities by BP-03.
14. Location and jurisdiction use BP-02; no external playable territory is created.
15. Taxonomy changes are approved, versioned, effective-dated and auditable.
16. Historical classification can be reconstructed using the original taxonomy version.
17. AI suggestions are non-authoritative until accepted under policy.
18. NPC classification behaviour respects knowledge, authority, training and permissions.
19. Analytics distinguish the unit being counted and disclose deduplication rules.
20. Cross-domain events are validated, versioned, traceable and idempotent.
21. Sensitive linked information remains protected under BP-42.
22. Player absence freezes simulation-time-dependent work.
23. The global population and business constraints are not bypassed.
24. All mapped source requirements, tests and cross-cutting rules are traceable.
25. Implementation, testing and verification remain separate statuses.

## 23. Acceptance test catalogue

| Test ID | Scenario | Expected result |
|---|---|---|
| CA-001 | Load an approved taxonomy catalogue | Stable IDs, versions and hierarchy resolve |
| CA-002 | Create taxonomy entry with duplicate ID | Rejected; existing entry unchanged |
| CA-003 | Create a hierarchy cycle | Rejected |
| CA-004 | Rename an active entry | ID retained; new version and history created |
| CA-005 | Move an entry to another parent | Relationship change versioned and audited |
| CA-006 | Resolve approved alias | Correct canonical entry returned |
| CA-007 | Alias matches two entries ambiguously | Disambiguation required; no silent selection |
| CA-008 | Publish a taxonomy version | Atomic activation with approval/audit |
| CA-009 | Publish without required approval | Rejected |
| CA-010 | Deprecate an entry with historical uses | Historical classifications remain resolvable |
| CA-011 | Query historical classification | Original taxonomy version and display reconstructed |
| CA-012 | Load a non-crime category | Available without creating an offence |
| CA-013 | Classify a welfare concern | Non-crime operational classification preserved |
| CA-014 | Classify suspicious circumstances with insufficient facts | Undetermined/provisional state retained |
| CA-015 | Create offence concept with required elements | Element schema and logical rules validate |
| CA-016 | Create offence concept with alternative elements | Alternative logic preserved |
| CA-017 | Create conditional element | Condition and dependency are evaluated correctly |
| CA-018 | Omit an element assessment | Remains not considered/unknown, not treated as absent |
| CA-019 | Mark an element disputed | Dispute and sources remain visible |
| CA-020 | Receive contradictory sources for one element | Both preserved; no automatic resolution |
| CA-021 | Classify an occurrence provisionally | Provisional status and rationale recorded |
| CA-022 | Reclassify after new information | New decision linked to prior decision |
| CA-023 | Withdraw a classification | Withdrawal reason recorded; prior decision retained |
| CA-024 | Assess no crime apparent | Does not imply reporter lied or no harm occurred |
| CA-025 | One occurrence may involve two offence concepts | Both classifications supported |
| CA-026 | Two alternative concepts cannot both apply | Alternative relationship represented without forced selection |
| CA-027 | One occurrence has several alleged offences | Distinct offence links maintained |
| CA-028 | One offence is reported through multiple incidents | Many-to-many links retained |
| CA-029 | One incident is linked to multiple occurrences | BP-12 incident and BP-14 occurrence identities remain distinct |
| CA-030 | A report is copied into three systems | Derivative copies do not count as independent corroboration |
| CA-031 | High harm but uncertain offence classification | Harm recorded without false legal certainty |
| CA-032 | Low harm but immediate operational threat | BP-12 priority remains independently assessable |
| CA-033 | Change severity descriptor model | New model version; historical values preserved |
| CA-034 | Unknown harm is submitted | Unknown does not become zero |
| CA-035 | Attempted conduct is reported | Attempt status only applied where concept permits |
| CA-036 | Event is interrupted before completion | Conduct status and legal classification remain distinct |
| CA-037 | A descriptor suggests a method | No offender identity inference |
| CA-038 | Similar modus operandi appears in separate events | Series link remains a hypothesis until authorised assessment |
| CA-039 | Classify digital conduct affecting Saltwater | Digital context represented without inventing external playable city |
| CA-040 | Location lies outside Saltwater | External context handled under policy; no new jurisdiction created |
| CA-041 | Location is uncertain | Uncertainty retained; no fabricated canonical address |
| CA-042 | Link a business to a classification | Canonical BP-04 ID reused |
| CA-043 | Link a person as victim | BP-17 remains authoritative for role |
| CA-044 | Link a person as suspect | BP-18 remains authoritative for status |
| CA-045 | Caller is not confirmed victim | Caller role does not auto-create victim role |
| CA-046 | Suspect is later acquitted | Historical suspect status and court outcome remain distinct |
| CA-047 | Court conviction arrives | BP-28 finding linked; earlier classification snapshot unchanged |
| CA-048 | Legal charge differs from operational classification | Both records remain separately attributable |
| CA-049 | Intelligence descriptor supports a lead | BP-21 retains intelligence authority and source handling |
| CA-050 | Evidence is linked to classification | BP-23 exhibit record remains authoritative |
| CA-051 | Classification suggests specialist route | Advisory route created; no dispatch claimed |
| CA-052 | Receiving unit rejects route referral | Rejection recorded; no false acceptance |
| CA-053 | Route rule changes | New version; historical route decisions retained |
| CA-054 | BP-14 supplies occurrence metadata | Only permitted operational fields reach classifier |
| CA-055 | BP-14 hidden offender field is present in payload | Field blocked from player/officer-facing classification |
| CA-056 | Player views provisional classification | No hidden offender or accomplice revealed |
| CA-057 | Player types text other than exact bingo | Concealed truth remains concealed |
| CA-058 | Player types exactly bingo | Reveal gate is invoked only through the governing game rule |
| CA-059 | NPC classifier has not received a source update | NPC cannot rely on that information |
| CA-060 | Junior NPC attempts restricted classification | Authority check rejects or routes for review |
| CA-061 | AI suggests a category | Suggestion marked non-authoritative with model/input provenance |
| CA-062 | AI suggestion is rejected | No authoritative classification mutation |
| CA-063 | AI invents an element/source | Validation rejects unsupported content |
| CA-064 | Taxonomy changes while player is absent | Simulation-time-dependent publication/review jobs remain frozen |
| CA-065 | Player exits with review due | No review timer advancement |
| CA-066 | Player resumes after pause | Prior state resumes without catch-up events |
| CA-067 | Duplicate classification event delivered | Idempotent processing |
| CA-068 | Classification event arrives out of order | Effective chronology and source timestamps preserved |
| CA-069 | Invalid incident/case reference received | Rejected or quarantined; no shadow record created |
| CA-070 | BP-13 service unavailable during urgent response | BP-12 response proceeds with pending classification |
| CA-071 | Taxonomy version missing | Classification held pending; no guessed substitute |
| CA-072 | Descriptor is unknown to current vocabulary | Raw value preserved and flagged for review |
| CA-073 | Taxonomy migration maps one entry to two | Ambiguity surfaced for review |
| CA-074 | Migration fails mid-run | No partial publication; prior version remains active |
| CA-075 | Migration is rolled back | Reversal is auditable; historical decisions intact |
| CA-076 | Access to linked restricted victim data denied | Classification summary reveals only permitted fields |
| CA-077 | Taxonomy administrator queries hidden occurrence truth | Access denied and audited |
| CA-078 | Bulk export includes restricted classifications | Restricted rows/fields excluded or export denied per policy |
| CA-079 | Classification correction is requested | Challenge linked to exact decision |
| CA-080 | Reviewer upholds classification | Review outcome and rationale appended |
| CA-081 | Reviewer amends classification | New decision supersedes prior without deletion |
| CA-082 | Reviewer lacks authority | Review action rejected |
| CA-083 | Search uses deprecated alias | Historical lookup resolves; new classification warns or blocks per policy |
| CA-084 | Analytics counts reports and offences | Separate counts and definitions displayed |
| CA-085 | Multiple incidents describe one occurrence | Deduplication method explicit; no hidden count collapse |
| CA-086 | Taxonomy entry is renamed | Old aliases remain searchable under configured rules |
| CA-087 | Entry is superseded | Predecessor/successor and effective dates preserved |
| CA-088 | Taxonomy contains inactive child of active parent | Lifecycle state displayed accurately |
| CA-089 | Parent is deprecated while child remains active | No silent child deprecation |
| CA-090 | A new category is proposed | Proposal, rationale and impact assessment required |
| CA-091 | A person is materially connected but only peripherally | BP-03 permanent promotion event invoked |
| CA-092 | Person already promoted is referenced again | Same identity reused; no double population count |
| CA-093 | Population is at 10,000 living people | BP-03 admission/replacement rules enforced; no cap bypass |
| CA-094 | At least 10,000 businesses are linked across records | Canonical business identities reused without duplication |
| CA-095 | External event is linked for context | No external playable geography is created |
| CA-096 | Taxonomy definition includes inclusion/exclusion examples | Boundary guidance is stored and searchable |
| CA-097 | Classification is reconstructed from history | Deterministic prior state and source snapshot recovered |
| CA-098 | Audit record write fails | Classification transaction does not partially commit |
| CA-099 | Backup restored | Taxonomy versions, decisions, links and audit reconcile |
| CA-100 | Full mapped-source conformance review | S29.R01–R03, S29.T01, S31.R02 and X05 requirements remain covered |

## 24. Edge cases and failure scenarios

1. A report describes conduct that could fit several categories.
2. A report contains multiple distinct alleged offences.
3. A single event contains a completed offence and a separate attempted offence.
4. An offence concept has alternative or conditional elements.
5. A key element is unknown, disputed or contradicted.
6. A source repeats another person's account without independent knowledge.
7. Several reports share one source or copied text and must not be treated as corroboration.
8. A report is anonymous but contains actionable information.
9. A reporter is mistaken but acting in good faith.
10. A report is maliciously fabricated; falsity and knowledge of falsity remain separate questions.
11. The alleged conduct is harmful but not criminal under the current taxonomy.
12. The conduct is criminal but no current category fits accurately.
13. The offence concept changes meaning following an approved taxonomy update.
14. A category is split into several more specific categories.
15. Several categories are consolidated into a broader category.
16. An alias becomes ambiguous after taxonomy expansion.
17. A taxonomy parent is retired while child concepts remain in use.
18. A category is valid for historical dates but not current conduct.
19. A classification was made under a superseded taxonomy version.
20. A legal charge differs from the operational classification.
21. A court acquittal follows a reasonable earlier classification.
22. A conviction concerns only some of several alleged offences.
23. A charge is withdrawn or amended after referral.
24. A classification is disputed by a victim, reporter, suspect or officer.
25. A classification is corrected after incident closure.
26. An occurrence is reclassified after forensic results arrive.
27. A classification is based on intelligence that cannot be broadly disclosed.
28. A descriptor reveals protected victim information if shown without filtering.
29. A suspected series is later separated into unrelated occurrences.
30. Separate events are later linked as a series.
31. Similar methods are used by different offenders.
32. One offender uses several methods across occurrences.
33. A business is the scene, victim, reporter and/or affected organisation in distinct roles.
34. One person is both a victim and alleged perpetrator in separate events.
35. A person changes role as facts develop; prior roles remain historically attributable.
36. A suspect is later eliminated; the historical suspicion is not erased.
37. A suspect is later convicted; the conviction does not rewrite the earlier knowledge state.
38. A generated occurrence contains hidden facts unavailable to operational actors.
39. A taxonomy recommendation accidentally encodes hidden generator truth.
40. An NPC receives a classification update before receiving its source evidence.
41. An AI model proposes a category from a misleading narrative.
42. An AI explanation invents an element not present in the taxonomy.
43. A taxonomy administrator attempts to inspect a restricted case.
44. A route rule points to a unit that no longer exists.
45. A route rule is valid but the required unit is unavailable.
46. A non-crime event is mistakenly assigned a formal offence concept.
47. A crime classification is withdrawn but the incident remains operationally active.
48. One incident is linked to multiple cases and different classification outcomes.
49. A case is split or merged without changing source incident identity.
50. A digital event affects Saltwater residents but has no physical Saltwater scene.
51. An external location is mentioned in a report and must not expand playable geography.
52. A location is incorrectly geocoded to Saltwater.
53. An incident has multiple sites with different jurisdictional uncertainty.
54. An occurrence has no identifiable victim at initial classification.
55. A victim is identified only after classification.
56. A victim declines engagement; classification remains independent of support choices.
57. A witness is also a suspect in another linked occurrence.
58. An offender is unknown; no placeholder person is fabricated.
59. A descriptor value is missing from the controlled vocabulary.
60. A taxonomy migration has no unambiguous successor.
61. A migration is interrupted by storage failure.
62. A taxonomy approval is revoked after publication.
63. A historical record is queried after a category rename.
64. A report aggregates provisional and confirmed classifications.
65. A report counts charges as if they were occurrences.
66. A user exports classification data without access to linked case material.
67. A taxonomy service is offline during emergency incident intake.
68. A classification event is delivered repeatedly or out of order.
69. A source record is deleted/withdrawn in its own domain while the classification reference must remain auditable.
70. The player exits while a scheduled review is due.
71. A system attempts to use wall-clock time to advance taxonomy effective dates during pause.
72. A relevant person is only marginally connected but must be permanently promoted.
73. The population cap is reached when a new relevant person is discovered.
74. More than 10,000 businesses are linked through classification descriptors without creating duplicate entities.
75. A taxonomy category is used in a generated occurrence before its effective date.
76. A generated occurrence references a retired taxonomy ID.
77. A non-crime classification is treated as a crime count by an analytics report.
78. A classification summary turns an allegation into an apparent fact.
79. A legal finding is imported without the originating court record reference.
80. A player-facing message leaks offender identity through an unusual category label or metadata.

## 25. Dependencies and ownership matrix

| Domain | BP-13 contract | Authority retained |
|---|---|---|
| BP-01 | Canon, player agency and concealment rules | Governing game rules |
| BP-02 | Spatial and jurisdiction references | Canonical geography |
| BP-03 | Person identity and permanent promotion | Population ledger and person lifecycle |
| BP-04 | Business, property and organisation references | Entity master records |
| BP-11 | Dispatch/intake route references | Call, CAD and dispatch |
| BP-12 | Incident classification and operational summaries | Incident record/lifecycle |
| BP-14 | Generated occurrence references | Occurrence creation and hidden truth |
| BP-15 | Case links and classification review | Case lifecycle |
| BP-16 | Investigative assessments | Investigative activity and conclusions |
| BP-17 | Victim/witness role references | Victim/witness case records |
| BP-18 | Suspect/offender role references | Suspect/offender status |
| BP-19 | Interview record references | Interview/interrogation records |
| BP-20 | Surveillance references | Surveillance records |
| BP-21 | Intelligence references and assessed descriptors | Intelligence source handling/products |
| BP-22/BP-23/BP-24 | Scene, exhibit and forensic references | Scene/evidence/forensic authority |
| BP-27/BP-28/BP-29 | Charge, court and correctional outcome links | Legal and adjudicated records |
| BP-30/BP-44 | Policy and taxonomy change approval | Governance and configuration |
| BP-35/BP-37 | Simulation events and shared time | Engine and clock |
| BP-38/BP-39 | Shared records, persistence and recovery | Records and persistence |
| BP-40/BP-41 | Presentation and notifications | Interface/reporting delivery |
| BP-42/BP-43 | Permissions and test evidence | Security and QA |

## 26. Open decisions for policy and configuration

1. Exact initial Saltwater offence catalogue and the fictional legal framework it represents.
2. Whether the catalogue uses statute-like references, generic offence concepts or both.
3. Final crime-domain family and category list, including emerging/digital categories.
4. Exact offence element schemas and any permitted alternative/conditional logic.
5. Severity and harm descriptors, scales and any weighting model.
6. Which classifications require mandatory supervisor or specialist approval.
7. Which categories trigger mandatory referral routes or safeguarding notifications.
8. Formal meaning and use of labels such as unfounded, no-crime, withdrawn, mistaken and unsubstantiated.
9. Rules for attempt, conspiracy, continuing conduct, aggravating factors and lesser/alternative offences.
10. Taxonomy publication authority, review board and approval workflow.
11. Taxonomy effective-date rules for conduct spanning a change date.
12. Retention and migration policy for historical classifications.
13. Exact controlled descriptor vocabularies and permitted free-text fields.
14. Which analytics are enabled and their official counting definitions.
15. AI classification model use, if any, and the mandatory human review threshold.
16. External event/jurisdiction reference policy.
17. Which reporting-route metadata is advisory versus mandatory under policy.
18. Language/localisation requirements for taxonomy names and definitions.

These decisions remain open until approved. Implementation must not silently invent permanent legal definitions, thresholds, labels or governance powers.

## 27. Traceability to source blueprint

The authoritative source is `docs/governance/SALTWATER_MASTER_BLUEPRINT.json` (52-division source, SHA previously recorded as `a882c4fc17f5654268a9b6d5823f5b9a4f3f1ade`). The 52-to-44 crosswalk remains the exhaustive mapping authority.

### 27.1 Direct source requirements — S29
- **S29.R01:** Maintain broad crime and non-crime incident taxonomy with elements, severity, location, victims, suspects, witnesses, methods and reporting routes. BP-13 owns taxonomy, offence elements, classification, severity descriptors, contextual descriptors and reporting-route metadata. BP-02 owns canonical geography; BP-11/BP-12 own intake/dispatch/incident; BP-17/BP-18 own victim/witness and suspect/offender roles; BP-14 owns generated occurrence truth; BP-15 owns case lifecycle.
- **S29.R02:** Generate varied, causally grounded incidents across the city and its organisations. BP-14 owns generation; BP-13 supplies valid taxonomy categories and constraints; BP-02/BP-03/BP-04/BP-35/BP-36/BP-37 supply geography, people, organisations, causal simulation, relationships and time.
- **S29.R03:** Distinguish occurrence, report, allegation, intelligence, offence and proven finding. BP-13 defines taxonomy/classification distinctions; BP-12 owns incident/report lifecycle; BP-15/BP-16 own case/investigation; BP-18 owns suspect/offender status; BP-21 owns intelligence; BP-27/BP-28 own legal processes and adjudicated findings.

### 27.2 Direct source test — S29.T01
Generated incidents must be unique, plausible and linked to valid entities and chronology. BP-14 is responsible for generation and causal truth; BP-13 must validate taxonomy references and classification semantics; BP-12/BP-35 validate incident linkage and chronological event execution. This specification's CA-001 through CA-100 supplement rather than replace S29.T01.

### 27.3 Additional mapped source
- **S31.R02:** Person-role distinctions and case context. BP-13 must preserve classification context without taking ownership of victim/witness or suspect/offender roles.
- **S31.T01:** Role/identity distinction is shared with BP-03, BP-15, BP-17 and BP-18; BP-13 must not infer roles from a crime category.
- **X05:** Distinguish fact, allegation, estimate, inference, intelligence, opinion, source statement, analytical conclusion and adjudicated finding.
- **A06:** Crime taxonomy/generation ownership must remain explicit across BP-13 and BP-14, with geography, dispatch and victim/suspect responsibilities assigned to their correct divisions.

## 28. Implementation sequencing and exit conditions

Before implementation:
- Complete the semantic crosswalk audit for every requirement/test mapped to BP-13, using original JSON pointers and source text.
- Approve the initial fictional Saltwater legal framework and taxonomy catalogue through BP-30/BP-44.
- Define immutable taxonomy versioning and effective-date behaviour.
- Define offence element schemas and classification decision records.
- Agree event contracts with BP-02, BP-03, BP-04, BP-11, BP-12, BP-14, BP-15, BP-16, BP-17, BP-18, BP-21, BP-27, BP-28, BP-35, BP-37, BP-38, BP-39 and BP-42.
- Define non-crime and undetermined states without forcing offence classifications.
- Establish data fixtures for ambiguous, multiple, alternative, historical, disputed, reclassified and non-criminal scenarios.
- Test that hidden occurrence truth is inaccessible to operational users and player-facing interfaces.
- Confirm all population, geography, time-freeze and business constraints are inherited from their authoritative divisions.
- Define migration dry-run, impact analysis, approval and rollback evidence.

Implementation is complete only when all required tests pass, source traceability is evidenced, event contracts reconcile, historical reconstruction is reproducible, permissions are tested and hidden truth remains concealed. Design, implementation, testing and verification are independent statuses.

## 29. Design status and change control

**Current status:** DESIGNED_DRAFT. This is a comprehensive specification draft, not an approved design and not an implementation.

- Implementation: NOT_STARTED.
- Test execution: NOT_STARTED.
- Verification: NOT_STARTED.
- User approval: PENDING.
- Neon writes: NONE. This document authorises no schema changes, migrations, imports, seeds or database writes.

All changes must preserve the fixed BP-01–BP-44 structure, traceability and source meaning. No requirement, test, edge case, provenance link or canon constraint may be removed to reduce storage or implementation effort. Compress representation, never meaning.
