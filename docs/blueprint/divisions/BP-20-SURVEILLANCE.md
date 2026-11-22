# BP-20 — Surveillance

**Project:** Saltwater — fictional sovereign city-state, one city, one jurisdiction  
**Blueprint division:** BP-20 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test execution:** NOT_STARTED | **Verification:** NOT_STARTED  
**Authority:** Derived from the unchanged 52-division source and the BP-01–BP-44 target structure. This draft changes neither canon nor division structure.

## 1. Purpose

BP-20 defines the complete surveillance and observation system: physical observation, static and mobile surveillance, CCTV and other fixed sensors, automatic number plate recognition (ANPR) or equivalent systems, authorised technical monitoring, source/device registration, coverage and blind spots, operational planning, authority, deployment, collection windows, operator activity, retrieval, review, derived products and hand-off to evidence management.

It preserves what was observed, what a device actually captured, what was not captured, when and where collection occurred, the limits and uncertainty of each source, and the provenance of every derivative. It supports player-directed, operationally credible surveillance without turning surveillance into an omniscient map of the city or a hidden solution-reveal mechanism.

Surveillance is an information collection activity. It does not itself establish identity, intent, guilt, offence, truth or evidential admissibility. Absence of coverage is never proof that an event did not occur.

## 2. Scope and ownership

### 2.1 BP-20 owns

- Surveillance requests, plans, objectives, scope, operational windows and status.
- Authority and authorisation records specific to surveillance activity, under configured fictional policy.
- Surveillance operation and task records, teams, operators, observers and supervisors.
- Physical observation, mobile observation and static observation episodes.
- CCTV, ANPR/equivalent, fixed sensors, camera networks and other registered collection sources.
- Source/device identity, installation/location, ownership/operator, field of view, coverage geometry, resolution/capability and limitations.
- Blind spots, occlusion, environmental interference, unavailable periods and source status.
- Time synchronisation, clock drift, offsets, timestamp quality and uncertainty.
- Collection windows, observation logs, recording intervals, retrieval requests and retrieval events.
- Original surveillance capture references and source-level metadata.
- Surveillance review, event annotation, time/location estimates and derived surveillance products.
- Surveillance-specific access controls, source confidentiality and audit events.
- Operational hand-off of exact original or derived sources to BP-23, preserving BP-20 source ownership.
- Surveillance system failure, outage, tampering, retention/overwrite risk and continuity of source records.

### 2.2 Explicit exclusions and authoritative owners

| Concern | Owner | BP-20 interface |
|---|---|---|
| City boundary, street geometry, coordinates and spatial reference | BP-02 | Uses canonical spatial IDs and coordinates; does not invent geometry |
| People, canonical identity, person lifecycle and population cap | BP-03 | Observations may refer to known, unknown or uncertain persons; no identity creation by resemblance alone |
| Premises, ownership, tenancy, access points, keys, alarms and facility topology | BP-04 | References canonical premises, access points and time-valid access facts |
| Police authority, hierarchy, roles and command | BP-05 | Uses valid command/authority references |
| Police personnel identity, qualifications and service status | BP-06 | References operators and qualifications |
| Unit establishment and deployment capacity | BP-08 | Receives unit/tasking and capability references |
| Police equipment, vehicle, camera and technical asset inventory/maintenance | BP-09 | BP-09 owns asset lifecycle; BP-20 owns operational source registration and surveillance use |
| Patrol activity and field observation outside dedicated surveillance | BP-10 | Distinguishes routine patrol observation from planned surveillance |
| Call intake, dispatch and communications | BP-11 | May receive tasks or operational requests; does not own dispatch |
| Incident response and command at incident | BP-12 | Links operational incident; does not own incident lifecycle |
| Offence classification | BP-13 | References offence/case context only |
| Hidden occurrence truth and crime generation | BP-14 | Never supplies hidden truth to ordinary surveillance planning, operators or player-facing products |
| Case identity and lifecycle | BP-15 | References case; does not create/close/merge cases |
| Investigative strategy, leads, tasks and decisions | BP-16 | Receives authorised requests; BP-16 owns investigative purpose and decisions |
| Victim/witness roles and safeguarding | BP-17 | No participant-role ownership |
| Suspect/offender roles and status | BP-18 | Surveillance does not create suspect/offender status or prove guilt |
| Interviews and statements | BP-19 | Receives only authorised interview-source references; no ownership of statements |
| Intelligence assessment and intelligence records | BP-21 | BP-20 owns raw collection source; BP-21 owns intelligence product/assessment |
| Crime scene control/search | BP-22 | Scene access and scene observations are coordinated; BP-22 owns scene management |
| Exhibit registration, seizure, packaging, custody and evidential continuity | BP-23 | BP-20 preserves original capture source and acquisition metadata; BP-23 owns exhibit continuity after accepted transfer |
| Forensic examination and interpretation | BP-24 | Receives exact source/exhibit references; does not perform forensic interpretation |
| Arrests and warrants | BP-25 | No arrest/search authority |
| Custody | BP-26 | No custody authority |
| Legal process, disclosure and prosecution | BP-27 | Provides source records; BP-27 owns disclosure and legal process |
| Court proceedings and findings | BP-28 | Supplies traceable source references; does not determine admissibility or findings |
| Corrections | BP-29 | No authority |
| Governance, surveillance policy and oversight | BP-30 | Owns policy approval and governance |
| Professional standards and misconduct | BP-31 | Owns standards/discipline; BP-20 supplies audited records |
| Simulation causality and NPC behaviour | BP-35 | Runs plausible collection and world events under knowledge boundaries |
| Relationships and social context | BP-36 | Context only; association is not evidence of wrongdoing |
| Canonical time and scheduling/pause | BP-37 | All events use canonical clock; all progression freezes when player absent |
| Records and databases | BP-38 | Owns schema, identifiers, provenance and authoritative record interfaces |
| Persistence and recovery | BP-39 | Owns durable storage and recovery |
| Interface and maps | BP-40 | Presents authorised derived views; text remains sufficient |
| Reporting and notifications | BP-41 | Consumes authorised source references |
| Security, permissions and hidden-information boundary | BP-42 | Enforces access and secret protection |
| Testing and quality assurance | BP-43 | Executes acceptance tests and evidence |
| Configuration and change control | BP-44 | Approves policy/schema/configuration changes |

### 2.3 Non-goals

BP-20 is not a general citywide omniscience engine, automatic suspect tracker, identity-recognition certainty engine, intelligence assessment system, evidence-custody system, forensic laboratory, case-management system, automated warrant/authority generator or player guidance engine. It must not expose hidden offender truth, suggest a culprit, recommend the next investigative step or guarantee that surveillance produces useful material.

## 3. Binding invariants

1. Every surveillance source has a defined identity, owner/operator, location or deployment context, capability, coverage and known limitations.
2. Every collection episode has a purpose, scope, responsible actor, authority status, time window and source references.
3. Physical observation and technical collection are distinct methods with distinct reliability and coverage limits.
4. A source's field of view/coverage is not assumed to include all nearby space.
5. Blind spots and non-coverage are explicit; absence of capture is not proof of absence.
6. A recording's timestamp is a source claim until reconciled against canonical time and known drift.
7. Raw capture, retrieved copy, export, clip, annotation, transcript, enhancement and analytical interpretation remain distinct.
8. Original captured material is never silently edited, overwritten or replaced by a derivative.
9. Every derivative traces to exact original source/version, operator/process, method, time and transformation history.
10. An observation is not automatically an identification; identification confidence and basis must be explicit.
11. An apparent person, vehicle, object, clothing item, route or event can be misidentified or unresolved.
12. Similarity, association, proximity, presence or repeated appearance does not establish guilt or participation in an offence.
13. Surveillance does not create or alter a BP-18 suspect/offender role.
14. Surveillance does not determine intelligence assessment; BP-21 owns intelligence products and evaluation.
15. Surveillance does not create exhibit custody; BP-23 owns exhibit lifecycle and continuity after transfer.
16. Collection authority is explicit and time/scope bounded under fictional policy; no real-world jurisdiction is silently imported.
17. Unauthorised, expired, out-of-scope or unverified collection is blocked or marked as an exception, never represented as authorised.
18. Source outages, faults, tampering, clock drift, retention overwrite and retrieval failures remain visible.
19. Operators and NPCs know only what they observed, collected or were told through a plausible information path.
20. BP-14 hidden occurrence truth is never used to aim, direct, annotate or explain ordinary surveillance.
21. Exact standalone lowercase `bingo` is the sole hidden-culprit reveal trigger; no other text or output leaks culprit/perpetrator/accomplice identities.
22. No unsolicited hints, suspect rankings, recommended surveillance targets or next investigative actions.
23. Player agency is preserved; the player decides whether, where, when and how to conduct authorised surveillance.
24. All time-dependent source, coverage, access, authority and collection facts are effective-dated and historically queryable.
25. No surveillance task, camera recording, operator activity, retrieval, processing, alert or retention timer advances while the player is outside the simulation.
26. Every living person counts once under the 10,000 total population cap; case-relevant people are permanently promoted by BP-03 without exceeding the cap.
27. Text-first operation is complete; maps, camera views and visual timelines are optional derivatives.
28. Storage optimisation cannot discard original content, source metadata, uncertainty, gaps, provenance or audit history.
29. A technical source's existence does not imply it was operational, recording, accessible or lawfully retrievable at a particular time.
30. An empty result may mean no event, no coverage, no recording, retrieval failure, poor quality or unresolved status; these meanings must not be conflated.

## 4. Core data model and stable identifiers

All IDs are stable, opaque, non-semantic and allocated under BP-38. Prefixes below are conceptual pending identifier convention approval.

| Entity | Identifier | Required meaning |
|---|---|---|
| Surveillance source | surveillance_source_id | Registered camera, sensor, platform, observer post or other source |
| Source version | source_version_id | Effective-dated configuration/capability/ownership |
| Coverage record | coverage_id | Geometry/area, direction, field of view and limitations |
| Blind-spot record | blindspot_id | Known non-coverage/occlusion |
| Surveillance request | surveillance_request_id | Request and source of tasking |
| Surveillance plan | surveillance_plan_id | Scope, purpose, locations, methods and collection window |
| Authority record | surveillance_authority_id | Fictional authority, issuer, scope, validity and conditions |
| Operation | surveillance_operation_id | Conducted surveillance activity |
| Task | surveillance_task_id | Assigned bounded action/work item |
| Operator/observer link | surveillance_operator_id | Person/unit role and active interval |
| Observation | observation_id | Attributed observation event |
| Capture | capture_id | Original captured recording/data item |
| Capture segment | capture_segment_id | Time-bounded portion of source material |
| Retrieval | retrieval_id | Request and act of obtaining stored source |
| Export/derivative | surveillance_derivative_id | Copy, clip, conversion, annotation or enhancement |
| Event annotation | surveillance_annotation_id | Descriptive marker tied to exact source position |
| Clock calibration | clock_calibration_id | Source-to-canonical offset/drift record |
| Source fault | source_fault_id | Outage, damage, tampering or recording defect |
| Review | surveillance_review_id | Technical/source-quality review |
| Handover | surveillance_handover_id | Transfer/reference to BP-23 or other authorised owner |
| Audit event | surveillance_audit_id | Sensitive access and material state change |

### 4.1 Common record fields

As applicable: stable ID; schema version; case/incident/task references; source and version; actor/person/unit; authority and scope; premises/access point/coordinates/area; method; event time; canonical time; source timestamp; record time; effective-from/to; uncertainty; status; original/derived classification; content reference; integrity/hash; retention state; access classification; provenance; correction/supersession link; idempotency key.

Do not duplicate BP-03 biographies, BP-04 property records, BP-09 asset records, BP-15 case records, BP-21 intelligence assessments or BP-23 exhibit binaries. Use canonical references and source-owned data.

## 5. Surveillance methods and source classes

### 5.1 Physical observation

Includes static observation posts, foot/mobile observation, vehicle-based observation, discreet observation, overt observation, observation of a defined place/person/object/event and coordinated observer teams. Record observer identity, position or route where safe and authorised, observation interval, visibility, distance/angle estimates, lighting/weather, obstructions, attention limits, notes and contemporaneous/later reconstruction status.

An observer cannot see all directions continuously. Record what was actually observed and the limits of recollection. A later reconstruction must be labelled as such and not backdated as a contemporaneous log.

### 5.2 Fixed technical sources

May include CCTV, door/entry cameras, traffic cameras, ANPR or equivalent, access-control event sources, alarm sensors, building/environment sensors and other configured systems. Each source is registered with source ID, device/system owner, operator, installation/premises/access-point reference, effective dates, field of view or monitored attribute, resolution/accuracy, recording mode, storage/retention behaviour, clock source, network dependencies, operating status and known limitations.

A door-access log is not a video recording. A camera is not an access-control system. A device's technical capacity is not proof it captured a particular event.

### 5.3 Mobile and carried sources

May include body-worn cameras, vehicle cameras, handheld recording devices, temporary deployed sensors or other configured equipment. BP-09 owns asset inventory and maintenance; BP-20 owns surveillance source registration/configuration and operational collection records. Record operator, device, deployment interval, activation/deactivation, field of view, handling, transfer and source clock.

### 5.4 Authorised technical monitoring

Any technical monitoring beyond ordinary fixed-source capture requires explicit fictional policy and authority configuration. Scope, target/source, method, period, responsible operator, access restrictions, minimisation/collection boundaries where configured, review and termination are recorded. Do not implement covert capabilities by implication or infer legal authorisation from rank, case assignment or technical access.

## 6. Source registry and lifecycle

Source states may include proposed, registered, installed, configured, operational, degraded, unavailable, disabled, under_maintenance, damaged, suspected_tampered, retired and archived. A source can have multiple effective-dated versions and operational intervals.

Registration records source class, manufacturer/model or logical system identifier where relevant, unique asset link, ownership/operator, physical location, coverage, capability, limitations, time source, storage/retention, network dependencies, access permissions, maintenance/fault links and current state. Installation or relocation creates a new effective-dated configuration; do not rewrite historic coverage.

A source can be operational but not recording; recording but not retrievable; retrievable but corrupted; or functioning with degraded quality. These states must be separately represented. Retired sources remain historically queryable.

## 7. Coverage, geometry and blind spots

Coverage is a time-valid spatial/functional claim. It may be represented as a polygon, line, direction, field-of-view cone, route, monitored boundary or logical detection zone. Link to canonical BP-02 geometry and BP-04 premises/access points. Record coordinate system, measurement method, source configuration/version, effective interval, estimated accuracy and author.

Coverage metadata includes direction and angle, range, resolution, frame rate or sampling interval, lighting/visibility constraints, obstructions, reflection/glare, weather exposure, occlusion, moving objects, blind zones, privacy masks/configured exclusions, recording schedule and detection limitations.

A blind spot is not necessarily permanent: construction, parked vehicles, foliage, doors, temporary barriers, source repositioning, lighting and environmental conditions can change it. Record known blind spots and their validity intervals. Do not infer complete coverage from a source's nominal specification or map icon.

For a historical query, reconstruct the source's coverage as it existed at the requested time, not today's configuration. When exact coverage cannot be established, report an uncertainty envelope or unknown state.

## 8. Requests, planning and authorisation

A request may originate from BP-16 investigation, BP-12 operational incident, authorised command, an approved policy process or another configured source. It records requester, case/incident, objective, target/location/source if known, rationale, scope, method requested, collection period, urgency, known constraints, information classification and supporting references.

A surveillance plan defines what is to be observed or collected, where, by what method/source, during which time window, by whom, under what authority, and with what limits. It records alternatives and operational risks when supplied, not generated as advice to the player.

Authorisation is a separate, versioned record. It identifies issuer and authority basis, approved method, subject/location/source, scope, start/end, conditions, restrictions, renewal, suspension and revocation. No authorisation may be expanded silently. An amendment requires a new approval event. An expired authority does not silently renew.

The precise fictional authority matrix, permitted methods, review periods and exceptional/emergency routes are open decisions for BP-30/BP-44. This specification does not impose external real-world law. Where the policy is undefined, the system must not invent authority; it records the unresolved request and blocks the restricted action.

## 9. Operation, tasking and personnel

An operation may contain multiple tasks, sources, observers and collection windows. Record operation lead, command, responsible unit, assigned personnel, qualification/briefing where configured, task ownership, location, communications plan reference, safety constraints, start/end, changes, cancellation and outcome.

Task states may include requested, awaiting_authority, authorised, assigned, ready, active, paused, interrupted, completed, failed, cancelled, suspended and reviewed. Each transition records actor, authority, reason and canonical time.

Observer teams may be split across locations and shifts. Preserve each operator's own observations and attendance interval. One operator's observation must not be attributed to another. Handover records identify outgoing/incoming operators, time, current status, equipment/source, outstanding limitations and acknowledgement.

A surveillance operation can fail or yield no useful result. The system must not force success or invent activity to complete the plan. An operation does not create a lead automatically; BP-16 owns investigative lead decisions.

## 10. Observation records and identification uncertainty

An observation record captures what an observer or source indicated, not an unqualified fact about the world. Fields may include observer/source, event interval, location/coverage area, direction, subject/object description, action/event description, distance/angle estimate, environmental conditions, visibility, duration, confidence in observation, source quality, exact versus approximate wording, contemporaneous/later status and linked capture segment.

Person/vehicle/object associations use canonical IDs only where identification is sufficiently supported and recorded. Otherwise use an unresolved observation subject with description and confidence. Similar clothing, vehicle type, gait, apparent age, height, build, voice or proximity alone must not silently resolve identity. Preserve alternative candidates and disconfirming features.

Distinguish:
- direct observation by a named human observer;
- device capture;
- operator interpretation of a device output;
- transcription or automated recognition output;
- later recollection;
- analyst annotation;
- intelligence assessment (BP-21);
- evidential interpretation (BP-23/BP-24);
- court finding (BP-28).

A record must never flatten these into one generic “fact”.

## 11. Recording, collection and retrieval

For each capture, preserve source/device ID and configuration version; original asset reference; capture start/end and segment coverage; source clock/timestamp; canonical time mapping and uncertainty; collection method; operator/requester; authority and scope; original/derivative classification; file/data format and duration/size where applicable; integrity hash; source status; recording gaps; quality limitations; retention/overwrite state; access restrictions; retrieval history and storage location reference.

Retrieval is a separate event from capture. Record who requested retrieval, who performed it, when, which source/time interval was requested, which intervals were actually returned, what was unavailable, why any gap exists, export/copy method and integrity verification.

A source may have overwritten material before a request. Record retention policy/configuration and known overwrite time. Do not recreate unavailable material. A failed retrieval is a meaningful result, not proof that no recording existed.

For human observation, the original contemporaneous note/log is the source record. A later typed summary is a derivative and must preserve author and reconstruction status.

## 12. Clock synchronisation and temporal reconstruction

All surveillance events use BP-37 canonical in-world time. Preserve the original device timestamp and the calibration relationship used to map it to canonical time. Clock calibration records source, reference clock, observed offset, drift rate if known, method, uncertainty, calibration time and validity interval.

Do not assume clocks are synchronised across devices. A device may drift, reset, use incorrect date/time, have daylight-saving/configuration issues or retain no timestamp. Record observed discrepancies and competing calibrations. Do not silently “correct” the original timestamp.

A reconstructed timeline references the exact capture/observation segments and declares method, source quality, offset assumptions, uncertainty range and author/process. An exact-looking timestamp must not conceal approximate input.

## 13. Source faults, outages, tampering and retention

Fault records include source/device, fault type, discovery time, estimated onset/clearance, reporter, symptoms, affected coverage/recording intervals, repair/maintenance reference, tampering indicators, confidence and unresolved questions. Fault categories include power loss, network loss, storage failure, lens obstruction, camera movement, clock fault, corrupted media, deliberate damage, configuration change, access failure and unknown cause.

Do not assume deliberate tampering from an outage alone. Distinguish observed damage, technical fault, suspected interference and confirmed tampering under the authorised review process. Preserve maintenance and configuration history.

Retention/overwrite policies are source-specific and configured by BP-30/BP-44. Record policy version, expected retention, actual overwrite/deletion event if configured, legal/preservation hold reference and responsible system. No destructive deletion or retention period is invented by this draft. A preservation request does not itself prove the source is preserved; acknowledgement and verification are separate.

## 14. Review, annotation and derived products

Review may assess source identity, coverage, quality, completeness, timestamp, clock offset, gaps, authenticity indicators, retrieval accuracy, operator notes and limitations. It does not determine guilt or make a legal admissibility finding.

Annotations are separate from original capture. Each annotation records author/process, creation time, source and segment, exact time/location marker, description, category, confidence, method and correction history. Avoid subjective or conclusory labels such as “culprit”, “criminal” or “suspicious person” unless explicitly quoted as an attributed opinion and permitted by policy.

Derived products may include clips, still frames, redacted copies, contact sheets, timelines, route reconstructions, coverage diagrams, comparison images, event indexes and descriptive summaries. Every product references exact source versions and transformation steps. Enhancement does not create details absent from the source. AI-generated descriptions or image enhancement are labelled derived and must not be presented as original capture.

A comparison may identify similarities/differences but cannot assert identity without an authorised, evidentially supported process. Any uncertainty or limitation remains visible.

## 15. Interfaces with investigation, intelligence, evidence and scenes

### 15.1 BP-16 investigation

BP-16 owns investigative plans, leads, tasks and decisions. It may request surveillance or receive a source/product reference. BP-20 records execution and results; it does not decide what the investigator should do next. A completed operation does not automatically create or close a lead.

### 15.2 BP-21 intelligence

BP-20 owns raw observation/capture and its source metadata. BP-21 owns intelligence assessment, grading, evaluation, dissemination and intelligence holdings. A surveillance annotation is not an intelligence assessment. Transfer uses exact source/version, access restrictions, confidence and provenance.

### 15.3 BP-23 evidence management

BP-20 owns surveillance source records and original capture metadata. BP-23 owns exhibit registration, seizure/receipt, packaging, custody, handling, continuity, storage and evidential status after formal transfer. Handover identifies the exact original/derivative, source, operator, method, date/time, integrity reference, restrictions, recipient and acknowledgement. BP-20 must not claim BP-23 custody before accepted receipt.

### 15.4 BP-22 crime scenes and BP-24 forensics

Scene access/geometry and scene control are BP-22-owned. BP-20 can reference scene cameras or observation coverage. BP-24 owns forensic methods and interpretations, including any technical enhancement requiring forensic authority. BP-20 preserves the source and derivative provenance.

### 15.5 BP-27/BP-28 legal process and courts

BP-20 supplies records and provenance. BP-27 owns disclosure decisions and legal process; BP-28 owns court proceedings and findings. No BP-20 label establishes admissibility, proof or conviction.

## 16. NPC and simulation behaviour

NPC observers and operators act only within assigned role, capability, knowledge, schedule and authority. Their observations are limited by position, visibility, attention, equipment, time and conditions. They may miss events, misperceive details, make recording errors or provide uncertain recollections. Do not grant perfect surveillance coverage or perfect recall.

The simulation may generate plausible technical source events, outages, movements and environmental effects when the world state supports them. Generated events must be causally consistent with source capability, installation, power/network, retention, location, coverage, time and operating state. If the source was offline, it cannot produce a normal capture for that interval.

NPCs cannot use hidden BP-14 truth to select targets, interpret footage, write annotations or inform the player. The player's private investigative reasoning is not automatically known to NPCs. A source may be discovered, requested, retrieved or unavailable according to in-world conditions and player action; no invisible system may force the intended clue to appear.

## 17. Player agency and hidden-information protection

The player chooses whether to request, authorise (if empowered), plan, deploy, review and retrieve surveillance. The interface must not recommend a target, suggest a camera to inspect, rank people/vehicles, disclose the next investigative action or imply a particular source will solve the case.

The exact reveal trigger is a standalone player input of lowercase `bingo`, with no punctuation, surrounding whitespace or additional words. Before that trigger:
- no culprit/perpetrator/accomplice identity is disclosed directly or indirectly;
- hidden BP-14 truth is excluded from source selection, operator knowledge, recording metadata, annotation, source labels, timeline order, report text, alerts, exports and generated imagery;
- no surveillance output is marked incriminating or exculpatory based on hidden truth;
- no absence, gap or anomaly is used as a covert culprit signal;
- no NPC receives hidden truth through prompts or system context;
- no suspect ranking or next-step recommendation is produced.

BP-42 owns security enforcement; BP-35 enforces generation boundaries; BP-43 tests direct and indirect leakage. A permitted reveal does not waive other access controls or convert allegations into adjudicated findings.

## 18. Permissions and audit

BP-42 owns global access policy. Suggested granular capabilities:
- surveillance.read.registry
- surveillance.read.coverage
- surveillance.read.requests
- surveillance.read.plans
- surveillance.read.authority
- surveillance.read.operations
- surveillance.read.observations
- surveillance.read.capture_metadata
- surveillance.read.original_capture
- surveillance.read.restricted
- surveillance.create.request
- surveillance.plan
- surveillance.authorise
- surveillance.assign
- surveillance.operate
- surveillance.annotate
- surveillance.retrieve
- surveillance.review
- surveillance.derive
- surveillance.handover
- surveillance.export
- surveillance.manage_source
- surveillance.manage_fault
- surveillance.audit.read

Read does not imply playback, copy, export, authorise, retrieve or alter. Access is checked for indexes, counts, search results, previews, thumbnails, summaries, notifications, reports, media playback, downloads, backups and AI context. Source owner access does not automatically grant police access; police access does not automatically grant access to all surveillance sources.

Audit source registration/configuration, coverage changes, authority decisions, operation/task changes, capture access/playback, retrieval, copy/export, annotation, derivation, redaction, handover, access denial, emergency access and retention events. Emergency access, if configured, must be reasoned, scoped, logged and reviewed.

## 19. Time, scheduling and pause

BP-37 is the only canonical simulation clock. Distinguish event time, source clock time, operator log time, retrieval time, processing time, record time and effective time. Preserve uncertainty and clock offsets.

While the player is outside the simulation:
- no surveillance operation starts, continues, moves or ends;
- no NPC observer conducts an observation;
- no camera/sensor records new world events;
- no storage retention/overwrite timer advances;
- no scheduled collection/retrieval/review occurs;
- no alert, automated analysis or notification progresses;
- no clock calibration or maintenance task executes.

On return, resume from the exact persisted state. No real-world catch-up or invented off-screen surveillance is allowed. Static source configuration remains stored but its simulated capture progression freezes.

## 20. Population, identity and privacy boundaries

All people remain BP-03 canonical persons. An unidentified observation subject is not automatically promoted as a new identified person. Where an observation is materially connected to a case or police activity, BP-03 applies permanent promotion rules to the relevant person record once identified or otherwise resolved under its policy. No person is downgraded after promotion. The 10,000 living-person cap includes police and all other counted persons; surveillance cannot bypass it by creating shadow identities.

Do not copy sensitive personal records into surveillance annotations without authorised need. A source's view of a home, workplace, vehicle or person does not grant unrestricted access to unrelated personal information. BP-42 controls restricted information and purpose-bound access.

## 21. Persistence, provenance and storage efficiency

BP-38 owns schema and record authority; BP-39 owns persistence and recovery. BP-20 owns surveillance semantics, source registry, operation records and original capture metadata.

Preserve:
- original source identity and exact configuration/version;
- original capture or human observation record;
- source timestamps and canonical mapping/uncertainty;
- coverage and blind spots at the relevant time;
- authority, purpose, scope and operator;
- capture gaps, faults and unavailable intervals;
- retrieval, playback, copy, export and access history;
- all derivative versions and transformation steps;
- annotations, corrections and reviews;
- exact handover to BP-23/BP-21 and recipient acknowledgement;
- provenance and audit trail.

Use deduplicated binary storage and references where appropriate, not duplicated copies of identical source assets. Deduplication must preserve per-case access restrictions, custody/retention holds, provenance and version references. Lossless compression is acceptable; semantic loss is not. Do not store repeated rendered map images when canonical geometry plus a reproducible view suffices. A compact record must retain every field necessary to reconstruct meaning.

Persistence operations are atomic across operation, source, capture, metadata and audit. Idempotent retry must not create duplicate captures, retrievals or handovers. Restore verifies hashes and links; missing assets are flagged, never silently replaced by an unrelated file or placeholder labelled original.

## 22. Interface, reports and visualisations

Text-first operation is complete. Required capabilities:
- list/search authorised surveillance sources and their effective-dated configurations;
- inspect coverage, blind spots, operational intervals and limitations;
- create/request and inspect a surveillance plan;
- record/inspect authority and conditions;
- assign and manage operations/tasks;
- record physical observations and operator logs;
- inspect source/capture metadata, recording intervals and gaps;
- request/review retrieval and failures;
- inspect exact original and derivative references with permissions;
- create attributable annotations and reviews;
- hand over exact source/version to BP-23 or BP-21;
- inspect source faults, retention/overwrite status and audit history.

Reports may include source register, historical coverage report, authority/operation log, observer chronology, capture inventory, retrieval result, fault/outage report, clock calibration report, source-quality review, derivative provenance and handover receipt. Every report declares scope, as-of time, source versions and limitations.

Optional maps, camera-layout diagrams, route/timeline views and still-frame displays are derived from canonical records. They must not invent coverage, imply certainty, expose hidden truth or contradict text. No visual is required to operate or review surveillance.

## 23. Inputs, outputs and event contracts

**Inputs:** BP-02 spatial geometry; BP-03 person identity; BP-04 premises/access facts; BP-05/BP-06 authority/personnel; BP-08 deployment; BP-09 asset status; BP-10 patrol observations; BP-11/BP-12 operational tasking; BP-15 case references; BP-16 investigative requests; BP-17/BP-18 participant roles; BP-21 intelligence interface; BP-22 scene records; BP-23 exhibit handover; BP-27 disclosure constraints; BP-30 policy; BP-35 world/NPC state; BP-37 canonical time; BP-38/BP-39 records/persistence; BP-42 permissions.

**Outputs:** source registry/configuration versions; coverage and blind-spot records; surveillance plans/authorities; operations/tasks; observer assignments and logs; raw capture references; retrieval events; annotations/reviews/derivatives; source fault/clock records; handover references; audit events.

Minimum event types: source_registered/configured/relocated/disabled/re-enabled/retired; coverage_created/amended/expired; blindspot_recorded/changed; request_created/approved/declined; authority_issued/amended/suspended/revoked/expired; plan_created/approved; operation_started/paused/resumed/interrupted/completed/failed/cancelled; task_assigned/reassigned/completed; operator_arrived/departed/handed_over; observation_recorded/corrected; capture_started/ended/gap_detected/faulted; retrieval_requested/completed/failed; derivative_created/reviewed/corrected; annotation_created/corrected; clock_calibrated/discrepancy_detected; source_fault_reported/resolved; retention_hold_requested/confirmed; handover_offered/accepted/rejected; access_granted/denied/emergency_used; restore_verified/reconciliation_failed.

Every event carries event ID, actor, authority, source/configuration version, operation/task/case reference, event and record time, effective interval, provenance, previous/resulting state, schema version and idempotency key.

## 24. Failure handling and edge cases

- Unknown source owner: preserve source claim and unresolved ownership; do not invent an operator.
- Device relocated: create a new effective-dated configuration; retain historic location and coverage.
- Camera exists but is offline: no normal capture is generated.
- Camera online but not recording: distinguish status from capture availability.
- Capture exists but cannot be retrieved: preserve capture claim and retrieval failure.
- Retention overwrite: record actual/estimated overwrite; never reconstruct deleted content.
- Clock drift: preserve raw timestamp and competing calibration estimates.
- Device clock reset: create a new calibration interval.
- Incorrect device date: mark source timestamp unreliable.
- Coverage partially obstructed: preserve affected area and time interval.
- Temporary blind spot: create effective-dated blind-spot record.
- Weather reduces visibility: represent source-specific impact, not citywide assumed failure.
- Operator distracted or unable to observe: record known limitation; do not infer continuous attention.
- Multiple observers disagree: preserve separate accounts and provenance.
- Person identification uncertain: retain unresolved identity and alternative candidates.
- Vehicle plate unreadable: do not guess missing characters.
- ANPR match false positive: preserve system output and later correction separately.
- Similar clothing/appearance: no automatic identity resolution.
- Footage shows a person near an event: proximity alone does not establish participation.
- No capture during interval: report possible reasons; do not assert event absence.
- Recording contains gap: expose exact known gap and uncertainty.
- Device tampering suspected: preserve indicators and uncertainty; no automatic attribution.
- Equipment asset marked maintenance: prevent contradictory operational status unless explicit exception.
- Authority expires during task: apply configured stop/hold; do not silently extend.
- Scope changes: require new authorised version and preserve old scope.
- Operator reassigned mid-operation: retain each person's interval and handover.
- Multiple devices capture same event: preserve separate sources; do not deduplicate away provenance.
- Derivative clip edited: preserve original and transformation history.
- Enhancement creates apparent detail: label derived; no claim of original detail.
- Map coverage is approximate: display uncertainty rather than exact polygon.
- Case closes: retain records under policy and preserve links.
- Person dies: historical record remains; no future activity generated for them.
- Pause occurs mid-operation: freeze all operation and source progression exactly.
- Hidden truth enters model context: suppress and audit without disclosing it.
- Duplicate capture event retry: idempotent result.
- Partial transaction failure: rollback or mark explicit incomplete state.
- Restored binary hash mismatch: quarantine/flag; never assert integrity.
- BP-23 rejects handover: BP-20 retains source ownership and rejection event.
- BP-21 receives raw source: do not relabel source as intelligence assessment.
- Unauthorised search snippet: redact at query/result layer, not only detail view.

## 25. Dependencies and failure contracts

| Dependency | Contract | Failure behaviour |
|---|---|---|
| BP-02/BP-04 | Canonical geometry, premises and access topology | Preserve unresolved location; no invented coverage |
| BP-03 | Canonical people and permanent promotion | Unresolved subject remains unresolved |
| BP-05/BP-06/BP-30 | Authority, personnel and policy | Block unsupported restricted activity |
| BP-08/BP-09 | Deployment and equipment capability/state | No impossible assignment or capture |
| BP-10/BP-11/BP-12 | Patrol/communications/incident interfaces | Preserve distinct operational ownership |
| BP-15/BP-16 | Case and investigative request | No orphan case or automatic lead |
| BP-17/BP-18 | Participant roles | Reference roles; do not infer guilt |
| BP-21 | Intelligence assessment | Hand off raw source; BP-21 assesses |
| BP-22 | Scene control and spatial facts | Respect scene authority and chronology |
| BP-23 | Exhibit continuity | Handover only on explicit accepted receipt |
| BP-24 | Forensic interpretation | Preserve source; no self-issued forensic conclusion |
| BP-27/BP-28 | Disclosure and judicial process | Supply traceable source; do not decide legal status |
| BP-35 | Causal simulation/NPC knowledge | No omniscient or hidden-truth generation |
| BP-37 | Canonical time and freeze | Stop all progression while absent |
| BP-38/BP-39 | Records, provenance, persistence | Atomic writes, idempotency, recoverable links |
| BP-40/BP-41 | Interface and reporting | Same permissions and hidden-truth rules on all outputs |
| BP-42 | Security and information boundaries | Deny safely and audit |
| BP-43/BP-44 | Test evidence and approved change | No status upgrade without evidence/change record |

## 26. Acceptance tests

These are specified acceptance criteria, not executed test results. BP-43 must execute them with reproducible evidence.

### Source registry, capability and coverage
- **SUR-AT-001** — Every registered source has a stable opaque ID.
- **SUR-AT-002** — Every source has a source class and owner/operator reference.
- **SUR-AT-003** — Source configuration is versioned and effective-dated.
- **SUR-AT-004** — Source location resolves to canonical spatial/premises reference or explicit unresolved state.
- **SUR-AT-005** — Source asset reference resolves to BP-09 where applicable.
- **SUR-AT-006** — Source capability is distinct from operational status.
- **SUR-AT-007** — Operational status is distinct from recording status.
- **SUR-AT-008** — Recording status is distinct from retrieval availability.
- **SUR-AT-009** — Source relocation preserves historical location and coverage.
- **SUR-AT-010** — Retired sources remain historically queryable.
- **SUR-AT-011** — Every coverage record identifies source configuration/version.
- **SUR-AT-012** — Coverage geometry uses canonical coordinate reference.
- **SUR-AT-013** — Field of view/detection zone includes measurement uncertainty.
- **SUR-AT-014** — Known blind spots are explicitly represented.
- **SUR-AT-015** — Temporary occlusion has a validity interval.
- **SUR-AT-016** — Current coverage is not substituted for historic coverage.
- **SUR-AT-017** — Nominal camera specification does not imply actual coverage.
- **SUR-AT-018** — Coverage gaps are not treated as proof of event absence.
- **SUR-AT-019** — Environmental visibility limits are source/time-specific.
- **SUR-AT-020** — Unknown coverage remains unknown, not guessed.

### Requests, authority and operations
- **SUR-AT-021** — Every request identifies requester, purpose and scope.
- **SUR-AT-022** — Request source and case/incident references are preserved.
- **SUR-AT-023** — Request is distinct from authorisation.
- **SUR-AT-024** — Authorisation records issuer and authority basis.
- **SUR-AT-025** — Authorisation scope, method and time window are explicit.
- **SUR-AT-026** — Expired authority cannot silently renew.
- **SUR-AT-027** — Scope expansion requires a new authorised event.
- **SUR-AT-028** — Undefined fictional authority does not default to permitted.
- **SUR-AT-029** — Unsupported real-world legal rules are not invented.
- **SUR-AT-030** — Every operation has responsible command/lead reference.
- **SUR-AT-031** — Every task has an assigned person/unit or explicit unassigned state.
- **SUR-AT-032** — Operator qualification is checked where policy requires.
- **SUR-AT-033** — Operator arrival/departure intervals are retained.
- **SUR-AT-034** — Handover identifies outgoing and incoming operator.
- **SUR-AT-035** — Multiple operators retain separate observation attribution.
- **SUR-AT-036** — Invalid operation lifecycle transition is rejected.
- **SUR-AT-037** — Failed/unproductive operation is valid terminal outcome.
- **SUR-AT-038** — Surveillance does not automatically create an investigative lead.
- **SUR-AT-039** — Surveillance does not automatically alter suspect/offender status.
- **SUR-AT-040** — Player retains choice whether to initiate authorised surveillance.

### Physical observation and source capture
- **SUR-AT-041** — Human observation identifies observer and observation interval.
- **SUR-AT-042** — Contemporaneous log is distinguished from later reconstruction.
- **SUR-AT-043** — Observation records visibility and relevant limitations.
- **SUR-AT-044** — Human observer is not treated as continuously omniscient.
- **SUR-AT-045** — Device capture references exact source and configuration.
- **SUR-AT-046** — Capture interval and source timestamp are retained.
- **SUR-AT-047** — Capture gaps are explicit.
- **SUR-AT-048** — Offline source cannot generate normal capture.
- **SUR-AT-049** — Online-but-not-recording state creates no recording.
- **SUR-AT-050** — Device capability alone does not prove a capture exists.
- **SUR-AT-051** — Multiple device sources remain independently identifiable.
- **SUR-AT-052** — Source ownership and operation role are not conflated.
- **SUR-AT-053** — Retrieval request is distinct from original capture.
- **SUR-AT-054** — Retrieval result records actual returned intervals.
- **SUR-AT-055** — Retrieval failure is retained as an event.
- **SUR-AT-056** — Overwritten/unavailable content is never reconstructed.
- **SUR-AT-057** — Source retention policy version is recorded.
- **SUR-AT-058** — Preservation request is distinct from confirmed preservation.
- **SUR-AT-059** — Original capture is never edited in place.
- **SUR-AT-060** — Every derivative links to exact original source/version.

### Time, identity and uncertainty
- **SUR-AT-061** — Raw source timestamp is preserved unchanged.
- **SUR-AT-062** — Canonical time mapping references calibration record.
- **SUR-AT-063** — Clock offset and uncertainty are represented.
- **SUR-AT-064** — Clock reset creates a new calibration interval.
- **SUR-AT-065** — Competing clock calibrations remain traceable.
- **SUR-AT-066** — Timeline reconstruction states method and assumptions.
- **SUR-AT-067** — Approximate source time is not rendered as exact.
- **SUR-AT-068** — Source identity confidence is explicit.
- **SUR-AT-069** — Unidentified subject remains unresolved.
- **SUR-AT-070** — Similar appearance alone cannot resolve identity.
- **SUR-AT-071** — Vehicle/plate uncertainty is preserved.
- **SUR-AT-072** — Alternative identity candidates and disconfirming details remain.
- **SUR-AT-073** — Observation is distinct from interpretation.
- **SUR-AT-074** — Operator interpretation is attributed to operator.
- **SUR-AT-075** — Automated recognition output is labelled derived.
- **SUR-AT-076** — Proximity does not establish participation in an offence.
- **SUR-AT-077** — Absence of coverage is not evidence of absence.
- **SUR-AT-078** — No source label asserts guilt or culpability.
- **SUR-AT-079** — No hidden truth informs observation confidence.
- **SUR-AT-080** — Every observation retains source and provenance.

### Faults, review and derivatives
- **SUR-AT-081** — Source fault identifies affected device and interval.
- **SUR-AT-082** — Fault discovery time differs from estimated onset.
- **SUR-AT-083** — Suspected tampering is distinct from confirmed tampering.
- **SUR-AT-084** — Maintenance history is time-valid and retained.
- **SUR-AT-085** — Fault does not imply deliberate interference.
- **SUR-AT-086** — Retention/overwrite event is auditable.
- **SUR-AT-087** — Source review references exact source version.
- **SUR-AT-088** — Review records limitations and unresolved defects.
- **SUR-AT-089** — Review does not determine guilt or legal admissibility.
- **SUR-AT-090** — Annotation is distinct from original media.
- **SUR-AT-091** — Annotation author, time and source position are retained.
- **SUR-AT-092** — Annotation correction preserves prior version.
- **SUR-AT-093** — Derived clip retains original source reference.
- **SUR-AT-094** — Redaction/conversion records transformation provenance.
- **SUR-AT-095** — Enhancement cannot claim details absent from source.
- **SUR-AT-096** — AI-generated descriptions are labelled derived.
- **SUR-AT-097** — Derived timeline links to exact source segments.
- **SUR-AT-098** — Visual coverage diagram traces to canonical geometry.
- **SUR-AT-099** — Uncertain coverage is visibly represented as uncertain.
- **SUR-AT-100** — Derivative does not replace original capture.

### Interfaces and player agency
- **SUR-AT-101** — BP-16 request and BP-20 operation ownership are separate.
- **SUR-AT-102** — BP-21 owns intelligence assessment, not raw source capture.
- **SUR-AT-103** — BP-23 owns exhibit custody after accepted handover.
- **SUR-AT-104** — Rejected handover leaves source ownership with BP-20.
- **SUR-AT-105** — Handover identifies exact source/derivative version.
- **SUR-AT-106** — BP-22 owns scene management and access control.
- **SUR-AT-107** — BP-24 owns forensic interpretation/enhancement authority.
- **SUR-AT-108** — BP-27 owns disclosure decision.
- **SUR-AT-109** — Surveillance product does not determine court finding.
- **SUR-AT-110** — Interface lists only authorised sources and records.
- **SUR-AT-111** — Interface does not recommend surveillance targets.
- **SUR-AT-112** — Interface does not recommend next investigative action.
- **SUR-AT-113** — No suspect or culprit ranking is emitted.
- **SUR-AT-114** — No unsolicited solution hint is emitted.
- **SUR-AT-115** — Empty search result does not assert no source existed.
- **SUR-AT-116** — Text interface supports all essential operations.
- **SUR-AT-117** — Optional visual does not contradict canonical text.
- **SUR-AT-118** — Every report states scope, time and limitations.
- **SUR-AT-119** — Hidden truth is excluded from source selection and annotation.
- **SUR-AT-120** — Exact standalone lowercase bingo is the only reveal trigger.

### Security, pause, persistence and population
- **SUR-AT-121** — Access control applies to indexes, previews, metadata and original media.
- **SUR-AT-122** — Playback, copy, retrieval and export require distinct permissions.
- **SUR-AT-123** — Sensitive reads and all exports are audited.
- **SUR-AT-124** — Emergency access is scoped, reasoned and audited if configured.
- **SUR-AT-125** — Search snippets and notifications enforce same restrictions as detail view.
- **SUR-AT-126** — No operation progresses while player is outside simulation.
- **SUR-AT-127** — No device capture or retention timer progresses while paused.
- **SUR-AT-128** — Resume restores exact operation and source state without catch-up.
- **SUR-AT-129** — Each living person is counted once within the 10,000 cap.
- **SUR-AT-130** — Permanent person promotion is never reversed.
- **SUR-AT-131** — Unknown observations do not create duplicate identities.
- **SUR-AT-132** — Atomic persistence prevents orphan capture/metadata records.
- **SUR-AT-133** — Idempotent retries do not duplicate capture or handover.
- **SUR-AT-134** — Restore verifies source hashes and reference links.
- **SUR-AT-135** — Missing media is flagged, not replaced by false original.
- **SUR-AT-136** — Storage compaction preserves source meaning and provenance.
- **SUR-AT-137** — Deduplication preserves case access and custody references.
- **SUR-AT-138** — Every material change records actor, authority, time and version.
- **SUR-AT-139** — All access-denial and hidden-truth leakage tests are auditable.
- **SUR-AT-140** — No test is passed without reproducible BP-43 evidence.

## 27. Source traceability

Original source JSON remains unchanged. IDs follow the 1-based source array positions and exact JSON pointer convention in the 52→44 crosswalk.

| Source ID | Original source requirement/test | BP-20 implementation |
|---|---|---|
| S06.R03 | Ensure occupancy and access facts are time-valid. | Sections 2, 7, 8, 12; use BP-04 time-valid access facts to interpret premises/source access. |
| S17.R03 | Support dispatch, pursuit, traffic enforcement, emergency access and case timelines. | Sections 2, 8, 9, 12, 15; surveillance routes/observations can support these operations without owning dispatch or pursuit. |
| S18.R02 | Track keys, locks, alarms, maintenance, ownership and authorised access. | Sections 2, 6–8, 13; source and premises interfaces consume BP-04/BP-09 records. |
| S18.R03 | Ensure scene geometry and access timelines are internally consistent. | Sections 7, 12, 15; time-valid coverage and access interfaces. |
| S19.R02 | Apply environmental conditions to visibility, travel, infrastructure, health and evidence persistence where justified. | Sections 5, 7, 10, 12–13, 16; source-specific visibility/recording effects and chronology. |
| S32.R03 | Support physical, digital, documentary, biological, trace and testimonial evidence. | Sections 11, 15, 23; surveillance sources support physical/digital/documentary material; BP-23 owns exhibit handling and other evidence categories. |
| S36.R01 | Represent physical observation, CCTV, ANPR or equivalent systems, authorised technical monitoring, coverage, blind spots, time drift, retention and retrieval. | Sections 5–7, 11–13; complete source/method/coverage model. |
| S36.R02 | Track requests, authorisations, collection windows, operators, exports and evidential continuity. | Sections 8–9, 11, 14–15, 18, 23; request-to-authority-to-operation-to-retrieval-to-handover lifecycle. |
| S36.R03 | Never treat absence of coverage as proof of absence. | Sections 3, 7, 10, 17, 24; explicit no-coverage invariant and tests. |
| S36.T01 | Every surveillance item has source device, coverage limits and time basis. | SUR-AT-001–020, 045–067 and 080. |
| S45.R01 | Provide optional maps, layouts, timelines, charts and forensic scene visuals when useful or requested. | Sections 7, 14, 22; optional source-derived coverage/timeline visuals. |
| S45.R02 | Visuals must derive from canonical spatial/evidence data and never silently contradict text records. | Sections 7, 14, 22; source links and uncertainty are mandatory. |
| S48.R02 | Protect hidden case truth and restricted personal information from player-facing leakage. | Sections 17–20; permissions, knowledge boundary and exact reveal gate. |

Cross-cutting rules X03, X05, X06 and X08 apply in full: time-valid facts; distinct fact/allegation/estimate/inference/intelligence/opinion/source statement/conclusion/finding; immutable originals and additive corrections; text-first sufficiency with optional visual consistency. The crosswalk remains authoritative for all other mapped source and cross-cutting references.

## 28. Open decisions and risk register

### Open decisions

1. Fictional surveillance authority matrix, issuer roles and approval levels.
2. Permitted surveillance methods and any methods requiring additional approval.
3. Emergency/urgent authority route and review.
4. Source classes and minimum registration metadata.
5. Camera/ANPR capability and uncertainty vocabularies.
6. Coverage geometry precision and coordinate conventions with BP-02.
7. Retention and overwrite policy by source class.
8. Preservation-hold rules and who may impose/release holds.
9. Technical monitoring safeguards, scope and duration.
10. Observer qualification, team composition and handover requirements.
11. Source quality grading vocabulary and review authority.
12. Identity-resolution process and confidence vocabulary with BP-03/BP-21/BP-24.
13. Media formats, binary storage and deduplication implementation with BP-38/BP-39.
14. Access-control matrix and emergency access with BP-42.
15. Exact command/interface syntax and optional map/camera display with BP-40.

### Risk register

| Risk | Mitigation |
|---|---|
| Assumed camera coverage | Effective-dated geometry and blind spots |
| Device time mistaken for canonical time | Raw timestamp plus calibration/uncertainty |
| Empty footage treated as proof | Distinct no-coverage, no-recording, gap and retrieval-failure states |
| Identity inferred from resemblance | Explicit confidence, alternatives and unresolved state |
| Derivative replaces original | Immutable original and transformation provenance |
| Unauthorised monitoring | Explicit authority/scope/version checks |
| Hidden culprit leaks through annotations | Generation firewall and adversarial output tests |
| Surveillance mistaken for intelligence | BP-20 raw source/BP-21 assessment boundary |
| Capture mistaken for exhibit custody | Explicit BP-23 accepted handover |
| Pause permits off-screen collection | BP-37 freeze enforced across all sources |
| Storage compaction removes context | Lossless metadata/provenance preservation |

## 29. Design completion checklist

- [ ] All BP-20 destination requirements and tests from the 52-division crosswalk are incorporated.
- [ ] Original 52-division source remains unchanged.
- [ ] Source registry and effective-dated configuration are specified.
- [ ] Physical and technical methods are distinct.
- [ ] Coverage, blind spots and limits are explicit.
- [ ] Requests, plans and authority are separate.
- [ ] Operations, operators, tasks and handovers are attributable.
- [ ] Original capture, retrieval, export and derivative are distinct.
- [ ] Clock drift, uncertainty, gaps and retention are represented.
- [ ] Identification remains uncertain where source does not support resolution.
- [ ] BP-16, BP-21, BP-22, BP-23, BP-24 and BP-27 boundaries are explicit.
- [ ] No hidden truth leakage, suspect ranking or unsolicited hints.
- [ ] No simulation progress while player is absent.
- [ ] Population cap and permanent promotion are enforced by BP-03.
- [ ] Text-first operation is complete; visuals are optional and traceable.
- [ ] Permissions, provenance, audit, recovery and storage efficiency are specified.
- [ ] All 140 acceptance tests await BP-43 execution.
- [ ] Open fictional policy decisions remain explicit.
- [ ] No Neon write, migration, seed, import or bulk write has been made or authorised.

## 30. Status and next dependencies

This is a complete division design draft, not approved policy or implementation evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-21 — Intelligence**. BP-21 owns intelligence collection holdings, evaluation, analysis, dissemination and intelligence lifecycle; BP-20 remains owner of surveillance source/capture and raw observation provenance.
